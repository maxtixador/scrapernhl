"""
OHL API Module

Comprehensive API for the Ontario Hockey League (OHL) using the HockeyTech platform.
Provides access to games, schedules, teams, rosters, player stats, and more.

The OHL uses the same LeagueStat platform structure as other HockeyTech leagues.
"""

import time
import json
import logging
from typing import Dict, Any, List, Union, Optional
from functools import wraps
import requests

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

class OHLConfig:
    """Configuration for OHL API access."""
    
    # API credentials
    API_KEY = "f1aa699db3d81487"
    CLIENT_CODE = "ohl"
    LEAGUE_ID = "1"  # use current league id from bootstrap
    SITE_ID = "1"    # site_id used by current OHL feed
    
    # Defaults
    DEFAULT_SEASON = "83"  # Update to current OHL season
    
    # Rate limiting
    RATE_LIMIT_CALLS = 2
    RATE_LIMIT_PERIOD = 1.0
    
    # API base URL
    BASE_URL = "https://lscluster.hockeytech.com/feed/index.php"
    
    def __init__(
        self,
        api_key: str = None,
        client_code: str = None,
        league_id: str = None,
        default_season: str = None
    ):
        self.API_KEY = api_key or self.API_KEY
        self.CLIENT_CODE = client_code or self.CLIENT_CODE
        self.LEAGUE_ID = league_id or self.LEAGUE_ID
        self.DEFAULT_SEASON = default_season or self.DEFAULT_SEASON


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Simple rate limiter using sliding window."""
    
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps: List[float] = []
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]
            
            if len(self.timestamps) >= self.calls:
                sleep_time = self.period - (now - self.timestamps[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            
            self.timestamps.append(time.time())
            return func(*args, **kwargs)
        return wrapper


# ============================================================================
# API UTILITIES
# ============================================================================

def clean_jsonp(text: str) -> str:
    """Remove JSONP wrapper from response."""
    text = text.strip()
    
    if text.startswith('angular.callbacks.'):
        start = text.find('(')
        if start != -1:
            text = text[start + 1:]
            if text.endswith(');'):
                text = text[:-2]
            elif text.endswith(')'):
                text = text[:-1]
    # Handle plain parentheses wrapper
    elif text.startswith('(') and text.endswith(')'):
        text = text[1:-1]
    
    return text


@RateLimiter(calls=OHLConfig.RATE_LIMIT_CALLS, period=OHLConfig.RATE_LIMIT_PERIOD)
def fetch_api(
    feed: str,
    view: str,
    config: OHLConfig = None,
    **params
) -> Dict[str, Any]:
    """Generic API fetch function with rate limiting."""
    if config is None:
        config = OHLConfig()
    
    query_params = {
        'feed': feed,
        'view': view,
        'key': config.API_KEY,
        'client_code': config.CLIENT_CODE,
        'league_id': config.LEAGUE_ID,
        **params
    }
    
    logger.debug(f"Fetching {view} with params: {query_params}")
    
    try:
        response = requests.get(config.BASE_URL, params=query_params, timeout=30)
        response.raise_for_status()
        
        clean_text = clean_jsonp(response.text)
        data = json.loads(clean_text)
        
        if isinstance(data, dict) and 'SiteKit' in data:
            return data['SiteKit']
        
        return data
        
    except requests.RequestException as e:
        logger.error(f"HTTP error fetching {view}: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {view}: {e}")
        logger.debug(f"Response text: {response.text[:200]}")
        raise


# ============================================================================
# GAMES & SCHEDULE
# ============================================================================

def get_scorebar(
    days_ahead: int = 6,
    days_back: int = 0,
    limit: int = 1000,
    fmt: str = 'json',
    division_id: int = -1,
    season_id: Optional[int] = None,
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get live games and upcoming schedule (scorebar)."""
    from datetime import datetime, timedelta
    
    # Calculate date range (API requires explicit dates, not relative days)
    today = datetime.now()
    date_from = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
    date_to = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

    season = season_id
    if season is None:
        try:
            bootstrap = get_bootstrap(config=config)
            if isinstance(bootstrap, dict):
                seasons = bootstrap.get('SiteKit', {}).get('Seasons') or bootstrap.get('seasons', [])
                if isinstance(seasons, list):
                    current = next((s for s in seasons if s.get('is_current')), None)
                    if current and current.get('id'):
                        season = current['id']
        except Exception:
            season = None

    if season is None:
        season = config.DEFAULT_SEASON if config else OHLConfig.DEFAULT_SEASON
    
    params = {
        'date_from': date_from,
        'date_to': date_to,
        'season_id': season,
        'limit': limit,
        'fmt': fmt,
        'site_id': OHLConfig.SITE_ID,
    }
    if division_id != -1:
        params['division_id'] = division_id

    return fetch_api(
        feed='modulekit',
        view='scorebar',
        config=config,
        **params
    )


def get_schedule(
    team_id: int = -1,
    season: Union[int, str] = None,
    month: int = -1,
    location: str = 'homeaway',
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get full season schedule."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='schedule',
        team=team_id,
        season=season,
        month=month,
        location=location,
        site_id=OHLConfig.SITE_ID,
        conference_id=-1,
        division_id=-1,
        config=config
    )


def get_game_preview(game_id: int, config: OHLConfig = None) -> Dict[str, Any]:
    """Get game preview/summary information."""
    return fetch_api(
        feed='statviewfeed',
        view='gameCenterPreview',
        game_id=game_id,
        config=config
    )


def get_game_summary(game_id: int, config: OHLConfig = None) -> Dict[str, Any]:
    """Get detailed game summary with stats."""
    return fetch_api(
        feed='statviewfeed',
        view='gameSummary',
        game_id=game_id,
        config=config
    )


def get_play_by_play(game_id: int, config: OHLConfig = None) -> List[Dict[str, Any]]:
    """Get play-by-play events for a game."""
    data = fetch_api(
        feed='statviewfeed',
        view='gameCenterPlayByPlay',
        game_id=game_id,
        config=config
    )
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'events' in data:
        return data['events']
    return data


# ============================================================================
# TEAMS
# ============================================================================

def get_teams(season: Union[int, str] = None, config: OHLConfig = None) -> Dict[str, Any]:
    """Get all teams for a season."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='teamsForSeason',
        season=season,
        config=config
    )


def get_standings(
    season: Union[int, str] = None,
    context: str = 'overall',
    special: str = 'false',
    group_by: str = 'division',
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get team standings with grouping options."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='teams',
        groupTeamsBy=group_by,
        context=context,
        special=special,
        season=season,
        site_id=OHLConfig.SITE_ID,
        config=config
    )


def get_roster(
    team_id: int,
    season_id: Union[int, str] = None,
    roster_status: str = 'undefined',
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get team roster with status filtering."""
    if season_id is None:
        season_id = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='roster',
        team_id=team_id,
        season_id=season_id,
        rosterstatus=roster_status,
        config=config
    )


# ============================================================================
# PLAYER STATS
# ============================================================================

def get_skater_stats(
    season: Union[int, str] = None,
    team: str = '-1',
    rookies: int = 0,
    stats_type: str = 'standard',
    first: int = 0,
    limit: int = 100,
    site_id: int = None,
    division: str = '-1',
    conference: str = '-1',
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get skater statistics with filtering and pagination."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    if site_id is None:
        site_id = int(OHLConfig.SITE_ID)
    
    return fetch_api(
        feed='statviewfeed',
        view='players',
        season=season,
        team=team,
        rookies=rookies,
        statsType=stats_type,
        first=first,
        limit=limit,
        site_id=site_id,
        division=division,
        conference=conference,
        config=config
    )


def get_goalie_stats(
    season: Union[int, str] = None,
    team: str = '-1',
    rookies: int = 0,
    stats_type: str = 'standard',
    first: int = 0,
    limit: int = 100,
    qualified: str = 'all',
    site_id: int = None,
    division: str = '-1',
    conference: str = '-1',
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get goalie statistics with filtering and pagination."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    if site_id is None:
        site_id = int(OHLConfig.SITE_ID)
    
    return fetch_api(
        feed='statviewfeed',
        view='goalies',
        season=season,
        team=team,
        rookies=rookies,
        statsType=stats_type,
        first=first,
        limit=limit,
        qualified=qualified,
        site_id=site_id,
        division=division,
        conference=conference,
        config=config
    )


def get_player_profile(
    player_id: int,
    season_id: Union[int, str] = None,
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get detailed player profile and career stats."""
    if season_id is None:
        season_id = OHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='player',
        player_id=player_id,
        season_id=season_id,
        config=config
    )


# ============================================================================
# BOOTSTRAP / CONFIG
# ============================================================================

def get_bootstrap(
    game_id: int = None,
    season: str = 'latest',
    page_name: str = 'scorebar',
    league_code: str = None,
    conference: str = None,
    division: str = None,
    config: OHLConfig = None
) -> Dict[str, Any]:
    """Get bootstrap/configuration data for initializing the API."""
    params = {
        'feed': 'statviewfeed',
        'view': 'bootstrap',
        'season': season,
        'pageName': page_name,
        'site_id': OHLConfig.SITE_ID,
        'config': config
    }
    
    if game_id is not None:
        params['game_id'] = game_id
    if league_code is not None:
        params['league_code'] = league_code
    if conference is not None:
        params['conference'] = conference
    if division is not None:
        params['division'] = division
    
    return fetch_api(**params)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_all_players(
    season: Union[int, str] = None,
    config: OHLConfig = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Get all players (skaters and goalies) for a season."""
    skaters = get_skater_stats(season=season, limit=10000, config=config)
    goalies = get_goalie_stats(season=season, limit=1000, config=config)
    
    return {
        'skaters': skaters.get('players', []) if isinstance(skaters, dict) else skaters,
        'goalies': goalies.get('goalies', []) if isinstance(goalies, dict) else goalies
    }


def get_team_schedule(
    team_id: int,
    season: Union[int, str] = None,
    config: OHLConfig = None
) -> List[Dict[str, Any]]:
    """Get schedule for a specific team."""
    data = get_schedule(team_id=team_id, season=season, config=config)
    
    if isinstance(data, dict) and 'games' in data:
        return data['games']
    return data


def get_game_full_data(game_id: int, config: OHLConfig = None) -> Dict[str, Any]:
    """Get complete game data: preview, summary, and play-by-play."""
    return {
        'preview': get_game_preview(game_id, config=config),
        'summary': get_game_summary(game_id, config=config),
        'play_by_play': get_play_by_play(game_id, config=config)
    }
