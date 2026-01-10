"""PWHL teams, standings, stats, and roster scrapers."""

from datetime import datetime
from typing import Dict, List, Union
import pandas as pd
import polars as pl
from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import InvalidTeamError
from ..api import fetch_api, PWHLConfig

# Teams
@cached(ttl=86400, cache_key_func=lambda season=None, **kwargs: f"pwhl_teams_{season}")
def getTeamsData(season: Union[int, str] = None) -> List[Dict]:
    """Scrapes raw PWHL teams data."""
    if season is None:
        season = PWHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching PWHL teams (season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='teamsForSeason', season=season)
        teams = response if isinstance(response, list) else []
    except Exception as e:
        raise RuntimeError(f"Error fetching teams data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "PWHL Teams API"} for record in teams if isinstance(record, dict)]

def scrapeTeams(season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes PWHL teams data."""
    raw_data = getTeamsData(season)
    return json_normalize(raw_data, output_format)

# Standings
@cached(ttl=3600, cache_key_func=lambda season=None, context='overall', special='false', group_by='division', **kwargs: f"pwhl_standings_{season}_{context}_{group_by}")
def getStandingsData(season: Union[int, str] = None, context: str = 'overall', special: str = 'false', group_by: str = 'division') -> List[Dict]:
    """Scrapes raw PWHL standings data."""
    if season is None:
        season = PWHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching PWHL standings (season={season}, context={context})...")
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
    return [{**record, "scrapedOn": now, "source": "PWHL Standings API"} for record in teams if isinstance(record, dict)]

def scrapeStandings(season: Union[int, str] = None, context: str = 'overall', special: str = 'false', group_by: str = 'division', output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes PWHL standings data."""
    raw_data = getStandingsData(season, context, special, group_by)
    return json_normalize(raw_data, output_format)

# Player Stats
@cached(ttl=3600, cache_key_func=lambda season=None, player_type='skater', sort='points', qualified='qualified', limit=50, first=0, **kwargs: f"pwhl_player_stats_{season}_{player_type}_{sort}_{limit}_{first}")
def getPlayerStatsData(season: Union[int, str] = None, player_type: str = 'skater', sort: str = 'points', qualified: str = 'qualified', limit: int = 50, first: int = 0) -> List[Dict]:
    """Scrapes raw PWHL player stats data."""
    if season is None:
        season = PWHLConfig.DEFAULT_SEASON
    stats_type = 'skaters' if player_type == 'skater' else 'goalies'
    console.print_info(f"Fetching PWHL {stats_type} stats (season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='players', season=season, sort=sort, statsType='standard', first=first, limit=limit, qualified=qualified, site_id=PWHLConfig.SITE_ID)
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
    return [{**record, "scrapedOn": now, "source": "PWHL Player Stats API"} for record in players if isinstance(record, dict)]

def scrapePlayerStats(season: Union[int, str] = None, player_type: str = 'skater', sort: str = 'points', qualified: str = 'qualified', limit: int = 50, first: int = 0, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes PWHL player stats data."""
    raw_data = getPlayerStatsData(season, player_type, sort, qualified, limit, first)
    return json_normalize(raw_data, output_format)

# Roster
@cached(ttl=3600, cache_key_func=lambda team_id, season=None, **kwargs: f"pwhl_roster_{team_id}_{season}")
def getRosterData(team_id: int, season: Union[int, str] = None) -> List[Dict]:
    """Scrapes raw PWHL roster data."""
    if team_id is None or not isinstance(team_id, int):
        raise InvalidTeamError(f"Invalid team_id: {team_id}")
    if season is None:
        season = PWHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching PWHL roster (team={team_id}, season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='roster', team=team_id, season=season)
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
    return [{**record, "scrapedOn": now, "source": "PWHL Roster API", "team_id": team_id} for record in players if isinstance(record, dict)]

def scrapeRoster(team_id: int, season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes PWHL roster data."""
    raw_data = getRosterData(team_id, season)
    return json_normalize(raw_data, output_format)

__all__ = ['getTeamsData', 'scrapeTeams', 'getStandingsData', 'scrapeStandings', 'getPlayerStatsData', 'scrapePlayerStats', 'getRosterData', 'scrapeRoster']
