"""AHL complete scraper suite."""

from datetime import datetime
from typing import Dict, List, Union
import pandas as pd
import polars as pl
from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import InvalidTeamError
from ..api import fetch_api, get_scorebar, AHLConfig

# Schedule
@cached(ttl=3600, cache_key_func=lambda team_id=-1, season=None, month=-1, location='homeaway', **kwargs: f"ahl_schedule_{team_id}_{season}_{month}_{location}")
def getScheduleData(team_id: int = -1, season: Union[int, str] = None, month: int = -1, location: str = 'homeaway') -> List[Dict]:
    """Scrapes raw AHL schedule data."""
    if season is None:
        season = AHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching AHL schedule (team={team_id}, season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='schedule', team=team_id, season=season, month=month, location=location, site_id=AHLConfig.SITE_ID, conference_id=-1, division_id=-1)
        games = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    games.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching schedule data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "AHL Schedule API"} for record in games if isinstance(record, dict)]

def scrapeSchedule(team_id: int = -1, season: Union[int, str] = None, month: int = -1, location: str = 'homeaway', output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes AHL schedule data."""
    raw_data = getScheduleData(team_id, season, month, location)
    return json_normalize(raw_data, output_format)

@cached(ttl=3600, cache_key_func=lambda team_id=None, season=None, **kwargs: f"ahl_schedule_legacy_{team_id}_{season}")
def getScheduleLegacyData(team_id: Union[int, str] = None, season: Union[int, str] = None) -> List[Dict]:
    """
    Scrapes raw AHL schedule data using the scorebar endpoint (legacy method).

    This endpoint provides more detailed schedule information including scores,
    game status, venue information, and timestamps in a flattened format.

    Parameters:
    -----------
    team_id : int or str, optional
        The team ID to filter schedule for. If None, returns all games.
    season : int or str, optional
        The season ID to fetch the schedule for. If None, uses default season.

    Returns:
    --------
    List[Dict]: List of game records with metadata
    """
    if season is None:
        season = AHLConfig.DEFAULT_SEASON

    console.print_info(f"Fetching AHL schedule via scorebar (team={team_id}, season={season})...")

    try:
        # Fetch data using scorebar endpoint with extended date range
        response = get_scorebar(
            days_ahead=365,
            days_back=365,
            season_id=int(season) if season else None,
            limit=2000
        )

        # Extract scorebar data
        games = []
        if isinstance(response, dict) and 'Scorebar' in response:
            games = response['Scorebar']
        elif isinstance(response, list):
            games = response

        # Filter by team_id if provided
        if team_id is not None:
            team_id_str = str(team_id)
            games = [
                g for g in games
                if isinstance(g, dict) and (
                    str(g.get('HomeID')) == team_id_str or
                    str(g.get('VisitorID')) == team_id_str
                )
            ]

        # Filter by season
        if season is not None:
            season_filters = [season, int(season) if str(season).isdigit() else season, str(season)]
            games = [
                g for g in games
                if isinstance(g, dict) and g.get('SeasonID') in season_filters
            ]

    except Exception as e:
        raise RuntimeError(f"Error fetching legacy schedule data: {e}")

    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "AHL Scorebar API"} for record in games if isinstance(record, dict)]

def scrapeScheduleLegacy(team_id: Union[int, str] = None, season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes AHL schedule data using the scorebar endpoint (legacy method).

    This method uses the scorebar API which provides more detailed information
    than the standard schedule endpoint, including real-time scores, game status,
    and venue details.

    Parameters:
    -----------
    team_id : int or str, optional
        The team ID to filter schedule for. If None, returns all games.
    season : int or str, optional
        The season ID to fetch the schedule for. If None, uses default season.
    output_format : str, default "pandas"
        Output format: "pandas" or "polars"

    Returns:
    --------
    pd.DataFrame or pl.DataFrame: Schedule data with metadata

    Example:
    --------
    >>> # Get all games for season
    >>> df = scrapeScheduleLegacy(season=77)
    >>>
    >>> # Get schedule for specific team
    >>> df = scrapeScheduleLegacy(team_id=20, season=77)
    """
    raw_data = getScheduleLegacyData(team_id, season)
    return json_normalize(raw_data, output_format)

# Teams
@cached(ttl=86400, cache_key_func=lambda season=None, **kwargs: f"ahl_teams_{season}")
def getTeamsData(season: Union[int, str] = None) -> List[Dict]:
    """Scrapes raw AHL teams data."""
    if season is None:
        season = AHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching AHL teams (season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='teamsForSeason', season=season)
        # Handle both dict (with 'teams' key) and list responses
        if isinstance(response, dict) and 'teams' in response:
            teams = response['teams']
        elif isinstance(response, list):
            teams = response
        else:
            teams = []
    except Exception as e:
        raise RuntimeError(f"Error fetching teams data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "AHL Teams API"} for record in teams if isinstance(record, dict)]

def scrapeTeams(season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes AHL teams data."""
    raw_data = getTeamsData(season)
    return json_normalize(raw_data, output_format)

# Standings
@cached(ttl=3600, cache_key_func=lambda season=None, context='overall', special='false', group_by='division', **kwargs: f"ahl_standings_{season}_{context}_{group_by}")
def getStandingsData(season: Union[int, str] = None, context: str = 'overall', special: str = 'false', group_by: str = 'division') -> List[Dict]:
    """Scrapes raw AHL standings data."""
    if season is None:
        season = AHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching AHL standings (season={season}, context={context})...")
    try:
        response = fetch_api(feed='statviewfeed', view='teams', groupTeamsBy=group_by, context=context, special=special, season=season)
        teams = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    teams.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching standings data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "AHL Standings API"} for record in teams if isinstance(record, dict)]

def scrapeStandings(season: Union[int, str] = None, context: str = 'overall', special: str = 'false', group_by: str = 'division', output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes AHL standings data."""
    raw_data = getStandingsData(season, context, special, group_by)
    return json_normalize(raw_data, output_format)

# Player Stats
@cached(ttl=3600, cache_key_func=lambda season=None, player_type='skater', sort='points', qualified='qualified', limit=50, first=0, **kwargs: f"ahl_player_stats_{season}_{player_type}_{sort}_{limit}_{first}")
def getPlayerStatsData(season: Union[int, str] = None, player_type: str = 'skater', sort: str = 'points', qualified: str = 'qualified', limit: int = 50, first: int = 0) -> List[Dict]:
    """Scrapes raw AHL player stats data."""
    if season is None:
        season = AHLConfig.DEFAULT_SEASON
    stats_type = 'skaters' if player_type == 'skater' else 'goalies'
    console.print_info(f"Fetching AHL {stats_type} stats (season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='players', season=season, sort=sort, statsType='standard', first=first, limit=limit, qualified=qualified, site_id=AHLConfig.SITE_ID)
        players = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching player stats data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "AHL Player Stats API"} for record in players if isinstance(record, dict)]

def scrapePlayerStats(season: Union[int, str] = None, player_type: str = 'skater', sort: str = 'points', qualified: str = 'qualified', limit: int = 50, first: int = 0, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes AHL player stats data."""
    raw_data = getPlayerStatsData(season, player_type, sort, qualified, limit, first)
    return json_normalize(raw_data, output_format)

# Roster
@cached(ttl=3600, cache_key_func=lambda team_id, season=None, **kwargs: f"ahl_roster_{team_id}_{season}")
def getRosterData(team_id: int, season: Union[int, str] = None) -> List[Dict]:
    """Scrapes raw AHL roster data."""
    if team_id is None or not isinstance(team_id, int):
        raise InvalidTeamError(f"Invalid team_id: {team_id}")
    if season is None:
        season = AHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching AHL roster (team={team_id}, season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='roster', team_id=team_id, season_id=season)
        players = []
        if isinstance(response, dict) and 'roster' in response and isinstance(response['roster'], list):
            for roster_item in response['roster']:
                if isinstance(roster_item, dict) and 'sections' in roster_item:
                    for section in roster_item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching roster data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "AHL Roster API", "team_id": team_id} for record in players if isinstance(record, dict)]

def scrapeRoster(team_id: int, season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes AHL roster data."""
    raw_data = getRosterData(team_id, season)
    return json_normalize(raw_data, output_format)

__all__ = ['getScheduleData', 'scrapeSchedule', 'getTeamsData', 'scrapeTeams', 'getStandingsData', 'scrapeStandings', 'getPlayerStatsData', 'scrapePlayerStats', 'getRosterData', 'scrapeRoster']
