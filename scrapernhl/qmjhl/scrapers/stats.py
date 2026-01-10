"""QMJHL player and team stats scrapers following NHL pattern."""

from datetime import datetime
from typing import Dict, List, Union, Optional

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import APIError
from ..api import fetch_api, QMJHLConfig


# Player Stats
@cached(ttl=3600, cache_key_func=lambda season=None, player_type='skater', sort='points', qualified='qualified', limit=50, first=0, **kwargs: f"qmjhl_player_stats_{season}_{player_type}_{sort}_{limit}_{first}")
def getPlayerStatsData(
    season: Union[int, str] = None,
    player_type: str = 'skater',
    sort: str = 'points',
    qualified: str = 'qualified',
    limit: int = 50,
    first: int = 0
) -> List[Dict]:
    """
    Scrapes raw QMJHL player stats data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)
    - player_type (str): 'skater' or 'goalie'
    - sort (str): Sort field (e.g., 'points', 'goals', 'saves')
    - qualified (str): 'qualified', 'all', etc.
    - limit (int): Number of records to return
    - first (int): Starting index for pagination

    Returns:
    - List[Dict]: Raw player stats records with metadata
    """
    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON
    
    stats_type = 'skaters' if player_type == 'skater' else 'goalies'
    console.print_info(f"Fetching QMJHL {stats_type} stats (season={season})...")
    
    try:
        if player_type == 'skater':
            response = fetch_api(
                feed='statviewfeed',
                view='players',
                season=season,
                sort=sort,
                statsType='standard',
                first=first,
                limit=limit,
                qualified=qualified,
                site_id=QMJHLConfig.SITE_ID
            )
        else:  # goalie
            response = fetch_api(
                feed='statviewfeed',
                view='goalies',
                season=season,
                sort=sort,
                statsType='standard',
                first=first,
                limit=limit,
                qualified=qualified,
                site_id=QMJHLConfig.SITE_ID
            )

        # Handle different response structures
        players = []
        if isinstance(response, list) and len(response) > 0:
            # Response is a list with one object containing sections
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            # Extract 'row' from each data item
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])
        elif isinstance(response, dict):
            if 'players' in response:
                players = response['players']
            elif 'goalies' in response:
                players = response['goalies']
            elif 'sections' in response:
                for section in response['sections']:
                    if 'data' in section:
                        for data_item in section['data']:
                            if isinstance(data_item, dict) and 'row' in data_item:
                                players.append(data_item['row'])
            else:
                players = [response]
        else:
            players = []

    except Exception as e:
        raise RuntimeError(f"Error fetching player stats data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Player Stats API"}
        for record in players
        if isinstance(record, dict)
    ]


def scrapePlayerStats(
    season: Union[int, str] = None,
    player_type: str = 'skater',
    sort: str = 'points',
    qualified: str = 'qualified',
    limit: int = 50,
    first: int = 0,
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL player stats data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)
    - player_type (str): 'skater' or 'goalie'
    - sort (str): Sort field (e.g., 'points', 'goals', 'saves')
    - qualified (str): 'qualified', 'all', etc.
    - limit (int): Number of records to return
    - first (int): Starting index for pagination
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Player stats data with metadata
    """
    raw_data = getPlayerStatsData(season, player_type, sort, qualified, limit, first)
    return json_normalize(raw_data, output_format)


# Team Stats
@cached(ttl=3600, cache_key_func=lambda season=None, **kwargs: f"qmjhl_team_stats_{season}")
def getTeamStatsData(season: Union[int, str] = None) -> List[Dict]:
    """
    Scrapes raw QMJHL team stats data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)

    Returns:
    - List[Dict]: Raw team stats records with metadata
    """
    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON
    
    console.print_info(f"Fetching QMJHL team stats (season={season})...")
    
    try:
        response = fetch_api(
            feed='statviewfeed',
            view='teams',
            season=season,
            statsType='standard',
            context='overall'
        )

        # Handle different response structures
        teams = []
        if isinstance(response, list) and len(response) > 0:
            # Response is a list with one object containing sections
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            # Extract 'row' from each data item
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    teams.append(data_item['row'])
        elif isinstance(response, dict):
            if 'teams' in response:
                teams = response['teams']
            elif 'sections' in response:
                for section in response['sections']:
                    if 'data' in section:
                        for data_item in section['data']:
                            if isinstance(data_item, dict) and 'row' in data_item:
                                teams.append(data_item['row'])
            else:
                teams = [response]
        else:
            teams = []

    except Exception as e:
        raise RuntimeError(f"Error fetching team stats data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Team Stats API"}
        for record in teams
        if isinstance(record, dict)
    ]


def scrapeTeamStats(
    season: Union[int, str] = None,
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL team stats data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Team stats data with metadata
    """
    raw_data = getTeamStatsData(season)
    return json_normalize(raw_data, output_format)


__all__ = [
    'getPlayerStatsData',
    'scrapePlayerStats',
    'getTeamStatsData',
    'scrapeTeamStats'
]
