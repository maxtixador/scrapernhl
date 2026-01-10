"""
AHL API Module

Comprehensive API for the American Hockey League (AHL) using the HockeyTech platform.
Provides access to games, schedules, teams, rosters, player stats, and more.

The AHL uses the same LeagueStat platform as PWHL, so the API structure is identical.
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

class AHLConfig:
    """Configuration for AHL API access."""
    
    # API credentials
    API_KEY = "ccb91f29d6744675"
    CLIENT_CODE = "ahl"
    LEAGUE_ID = "4"
    SITE_ID = "3"
    
    # Defaults
    DEFAULT_SEASON = "90"  # Current AHL season
    
    # Rate limiting
    RATE_LIMIT_CALLS = 2  # calls per period
    RATE_LIMIT_PERIOD = 1.0  # period in seconds
    
    # API base URL
    BASE_URL = "https://lscluster.hockeytech.com/feed/index.php"
    
    def __init__(
        self,
        api_key: str = None,
        client_code: str = None,
        league_id: str = None,
        default_season: str = None
    ):
        """
        Initialize AHL config with custom values.
        
        Args:
            api_key: Override default API key
            client_code: Override default client code
            league_id: Override default league ID
            default_season: Override default season
        """
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
            
            # Remove timestamps outside the window
            self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]
            
            # Wait if we've hit the limit
            if len(self.timestamps) >= self.calls:
                sleep_time = self.period - (now - self.timestamps[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            
            # Record this call
            self.timestamps.append(time.time())
            
            return func(*args, **kwargs)
        return wrapper


# ============================================================================
# API UTILITIES
# ============================================================================

def clean_jsonp(text: str) -> str:
    """
    Remove JSONP wrapper from response.
    
    HockeyTech API returns responses wrapped in:
    - angular.callbacks._X(...)
    - or just (...)
    This function strips those wrappers to get clean JSON.
    
    Args:
        text: Raw response text
    
    Returns:
        Clean JSON string
    """
    text = text.strip()
    
    # Check for angular.callbacks wrapper
    if text.startswith('angular.callbacks.'):
        # Find the opening parenthesis
        start = text.find('(')
        if start != -1:
            # Remove wrapper and trailing semicolon/parenthesis
            text = text[start + 1:]
            if text.endswith(');'):
                text = text[:-2]
            elif text.endswith(')'):
                text = text[:-1]
    # Check for plain parentheses wrapper (AHL format)
    elif text.startswith('(') and text.endswith(')'):
        text = text[1:-1]
    
    return text


@RateLimiter(calls=AHLConfig.RATE_LIMIT_CALLS, period=AHLConfig.RATE_LIMIT_PERIOD)
def fetch_api(
    feed: str,
    view: str,
    config: AHLConfig = None,
    **params
) -> Dict[str, Any]:
    """
    Generic API fetch function with rate limiting.
    
    Args:
        feed: Feed type ('statviewfeed', 'modulekit', etc.)
        view: View type ('gameCenterPlayByPlay', 'scorebar', etc.)
        config: AHLConfig instance (uses defaults if None)
        **params: Additional query parameters
    
    Returns:
        Parsed JSON response
    
    Raises:
        requests.RequestException: On HTTP errors
        json.JSONDecodeError: On JSON parsing errors
    """
    if config is None:
        config = AHLConfig()
    
    # Build query parameters
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
        
        # Clean JSONP wrapper
        clean_text = clean_jsonp(response.text)
        
        # Parse JSON
        data = json.loads(clean_text)
        
        # Handle nested SiteKit structure
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get live games and upcoming schedule (scorebar).
    
    Args:
        days_ahead: Number of days ahead to fetch (default: 6)
        days_back: Number of days back to fetch (default: 0)
        limit: Maximum number of games (default: 1000)
        fmt: Response format ('json' or 'jsonp')
        division_id: Division ID filter (-1 for all)
        season_id: Explicit season id (defaults to current season)
        config: AHLConfig instance
    
    Returns:
        Scorebar data with games
    
    Example:
        >>> scorebar = get_scorebar(days_ahead=7, days_back=2)
        >>> print(f"Found {len(scorebar['games'])} games")
    """
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
        season = config.DEFAULT_SEASON if config else AHLConfig.DEFAULT_SEASON
    
    params = {
        'date_from': date_from,
        'date_to': date_to,
        'season_id': season,
        'limit': limit,
        'fmt': fmt,
        'site_id': AHLConfig.SITE_ID,
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get full season schedule.
    
    Args:
        team_id: Team ID (use -1 for all teams)
        season: Season ID (uses default if None)
        month: Month filter (-1 for all months, 1-12 for specific month)
        location: Game location filter ('homeaway', 'home', 'away')
        config: AHLConfig instance
    
    Returns:
        Schedule data
    
    Example:
        >>> schedule = get_schedule()  # All teams
        >>> schedule = get_schedule(team_id=2, location='home')  # Home games only
    """
    if season is None:
        season = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='schedule',
        team=team_id,
        season=season,
        month=month,
        location=location,
        site_id=AHLConfig.SITE_ID,
        conference_id=-1,
        division_id=-1,
        config=config
    )


def get_game_preview(game_id: int, config: AHLConfig = None) -> Dict[str, Any]:
    """
    Get game preview/summary information.
    
    Args:
        game_id: Game ID
        config: AHLConfig instance
    
    Returns:
        Game preview data
    
    Example:
        >>> preview = get_game_preview(12345)
        >>> print(preview['home_team'], 'vs', preview['away_team'])
    """
    return fetch_api(
        feed='statviewfeed',
        view='gameCenterPreview',
        game_id=game_id,
        config=config
    )


def get_game_summary(game_id: int, config: AHLConfig = None) -> Dict[str, Any]:
    """
    Get detailed game summary with stats.
    
    Args:
        game_id: Game ID
        config: AHLConfig instance
    
    Returns:
        Game summary with team stats, scoring, penalties, etc.
    
    Example:
        >>> summary = get_game_summary(12345)
        >>> print(summary['final_score'])
    """
    return fetch_api(
        feed='statviewfeed',
        view='gameSummary',
        game_id=game_id,
        config=config
    )


def get_play_by_play(game_id: int, config: AHLConfig = None) -> List[Dict[str, Any]]:
    """
    Get play-by-play events for a game.
    
    Args:
        game_id: Game ID
        config: AHLConfig instance
    
    Returns:
        List of play-by-play events
    
    Example:
        >>> pbp = get_play_by_play(12345)
        >>> print(f"Found {len(pbp)} events")
    """
    data = fetch_api(
        feed='statviewfeed',
        view='gameCenterPlayByPlay',
        game_id=game_id,
        config=config
    )
    
    # Extract events array if wrapped
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'events' in data:
        return data['events']
    return data


# ============================================================================
# TEAMS
# ============================================================================

def get_teams(season: Union[int, str] = None, config: AHLConfig = None) -> Dict[str, Any]:
    """
    Get all teams for a season.
    
    Args:
        season: Season ID (uses default if None)
        config: AHLConfig instance
    
    Returns:
        Teams data
    """
    if season is None:
        season = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get team standings with grouping options.
    
    Args:
        season: Season ID (uses default if None)
        context: Stats context ('overall', 'home', 'away')
        special: Include special team stats ('true' or 'false')
        group_by: How to group teams ('division', 'conference', 'league')
        config: AHLConfig instance
    
    Returns:
        Standings data
    
    Example:
        >>> standings = get_standings()  # Overall standings by division
        >>> standings = get_standings(context='home', group_by='league')
    """
    if season is None:
        season = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
    return fetch_api(
        feed='statviewfeed',
        view='teams',
        groupTeamsBy=group_by,
        context=context,
        special=special,
        season=season,
        site_id=AHLConfig.SITE_ID,
        config=config
    )


def get_roster(
    team_id: int,
    season_id: Union[int, str] = None,
    roster_status: str = 'undefined',
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get team roster with status filtering.
    
    Args:
        team_id: Team ID
        season_id: Season ID (uses default if None)
        roster_status: Roster status filter ('undefined' for all, 'active', 'inactive', etc.)
        config: AHLConfig instance
    
    Returns:
        Roster data with players
    
    Example:
        >>> roster = get_roster(team_id=2)
        >>> roster = get_roster(team_id=2, roster_status='active')
        >>> print(f"Found {len(roster['players'])} players")
    """
    if season_id is None:
        season_id = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get skater statistics with filtering and pagination.
    
    Args:
        season: Season ID (uses default if None)
        team: Team ID filter ('-1' for all teams)
        rookies: Rookies only (0=all, 1=rookies only)
        stats_type: Stats type ('standard', 'bio', etc.)
        first: Starting index for pagination (0-based)
        limit: Number of results per page
        site_id: Site ID (uses default if None)
        division: Division ID filter ('-1' for all)
        conference: Conference ID filter ('-1' for all)
        config: AHLConfig instance
    
    Returns:
        Player stats data with pagination info
    
    Example:
        >>> stats = get_skater_stats(limit=50)  # First 50 players
        >>> stats = get_skater_stats(team='5', rookies=1)  # Team 5 rookies
        >>> stats = get_skater_stats(first=50, limit=50)  # Next 50 players
    """
    if season is None:
        season = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    if site_id is None:
        site_id = int(AHLConfig.SITE_ID)
    
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get goalie statistics with filtering and pagination.
    
    Args:
        season: Season ID (uses default if None)
        team: Team ID filter ('-1' for all teams)
        rookies: Rookies only (0=all, 1=rookies only)
        stats_type: Stats type ('standard', 'bio', etc.)
        first: Starting index for pagination (0-based)
        limit: Number of results per page
        qualified: Qualification filter ('all', 'qualified', 'unqualified')
        site_id: Site ID (uses default if None)
        division: Division ID filter ('-1' for all)
        conference: Conference ID filter ('-1' for all)
        config: AHLConfig instance
    
    Returns:
        Goalie stats data with pagination info
    
    Example:
        >>> stats = get_goalie_stats(qualified='qualified')
        >>> stats = get_goalie_stats(team='5', limit=10)
    """
    if season is None:
        season = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    if site_id is None:
        site_id = int(AHLConfig.SITE_ID)
    
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get detailed player profile and career stats.
    
    Args:
        player_id: Player ID
        season_id: Season ID (uses default if None)
        config: AHLConfig instance
    
    Returns:
        Player profile with bio and career stats
    
    Example:
        >>> profile = get_player_profile(12345)
        >>> print(profile['name'], profile['position'])
    """
    if season_id is None:
        season_id = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON
    
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get bootstrap/configuration data for initializing the API.
    
    Args:
        game_id: Optional game ID for game-specific bootstrap
        season: Season ('latest' or specific season ID)
        page_name: Page name context ('scorebar', 'gamecenter', 'schedule', etc.)
        league_code: League code filter
        conference: Conference filter
        division: Division filter
        config: AHLConfig instance
    
    Returns:
        Bootstrap configuration data including teams, divisions, seasons, etc.
    
    Example:
        >>> bootstrap = get_bootstrap()  # Get default config
        >>> bootstrap = get_bootstrap(game_id=12345, page_name='gamecenter')
    """
    params = {
        'feed': 'statviewfeed',
        'view': 'bootstrap',
        'season': season,
        'pageName': page_name,
        'site_id': AHLConfig.SITE_ID,
        'config': config
    }
    
    # Add optional filters
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
    config: AHLConfig = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all players (skaters and goalies) for a season.
    
    Args:
        season: Season ID (uses default if None)
        config: AHLConfig instance
    
    Returns:
        Dict with 'skaters' and 'goalies' lists
    
    Example:
        >>> all_players = get_all_players()
        >>> print(f"Skaters: {len(all_players['skaters'])}")
        >>> print(f"Goalies: {len(all_players['goalies'])}")
    """
    skaters = get_skater_stats(season=season, limit=10000, config=config)
    goalies = get_goalie_stats(season=season, limit=1000, config=config)
    
    return {
        'skaters': skaters.get('players', []) if isinstance(skaters, dict) else skaters,
        'goalies': goalies.get('goalies', []) if isinstance(goalies, dict) else goalies
    }


def get_team_schedule(
    team_id: int,
    season: Union[int, str] = None,
    config: AHLConfig = None
) -> List[Dict[str, Any]]:
    """
    Get schedule for a specific team.
    
    Args:
        team_id: Team ID
        season: Season ID (uses default if None)
        config: AHLConfig instance
    
    Returns:
        List of games for the team
    
    Example:
        >>> schedule = get_team_schedule(team_id=2)
        >>> print(f"Team has {len(schedule)} games")
    """
    data = get_schedule(team_id=team_id, season=season, config=config)
    
    if isinstance(data, dict) and 'games' in data:
        return data['games']
    return data


def get_game_full_data(game_id: int, config: AHLConfig = None) -> Dict[str, Any]:
    """
    Get complete game data: preview, summary, and play-by-play.
    
    Args:
        game_id: Game ID
        config: AHLConfig instance
    
    Returns:
        Dict with 'preview', 'summary', and 'play_by_play' keys
    
    Example:
        >>> game = get_game_full_data(12345)
        >>> print(game['summary']['final_score'])
        >>> print(f"PBP events: {len(game['play_by_play'])}")
    """
    return {
        'preview': get_game_preview(game_id, config=config),
        'summary': get_game_summary(game_id, config=config),
        'play_by_play': get_play_by_play(game_id, config=config)
    }
