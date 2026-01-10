"""QMJHL schedule data scrapers following NHL pattern."""

from datetime import datetime
from typing import Dict, List, Union, Optional

import pandas as pd
import polars as pl

from ...core.http import fetch_json
from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import APIError, InvalidTeamError, InvalidSeasonError
from ..api import fetch_api, QMJHLConfig


@cached(ttl=3600, cache_key_func=lambda team_id=-1, season=None, month=-1, location='homeaway', **kwargs: f"qmjhl_schedule_{team_id}_{season}_{month}_{location}")
def getScheduleData(
    team_id: int = -1,
    season: Union[int, str] = None,
    month: int = -1,
    location: str = 'homeaway'
) -> List[Dict]:
    """
    Scrapes raw QMJHL schedule data.

    This uses the statviewfeed/schedule endpoint which returns structured
    schedule data with sections. Best for full league schedules.

    Parameters:
    - team_id (int): Team ID (-1 for all teams)
    - season (int or str): Season ID (e.g., 211)
    - month (int): Month filter (-1 for all months)
    - location (str): 'homeaway', 'home', or 'away'

    Returns:
    - List[Dict]: Raw schedule records with metadata
    """
    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON
    
    console.print_info(f"Fetching QMJHL schedule (team={team_id}, season={season})...")
    
    try:
        response = fetch_api(
            feed='statviewfeed',
            view='schedule',
            team=team_id,
            season=season,
            month=month,
            location=location,
            site_id=QMJHLConfig.SITE_ID,
            conference_id=-1,
            division_id=-1
        )

        # Extract games from sections structure
        games = []
        if isinstance(response, list) and len(response) > 0:
            # Response is a list with one object containing sections
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            # Extract 'row' from each data item
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    games.append(data_item['row'])
        elif isinstance(response, dict) and 'sections' in response:
            for section in response['sections']:
                if 'data' in section:
                    for data_item in section['data']:
                        if isinstance(data_item, dict) and 'row' in data_item:
                            games.append(data_item['row'])
        else:
            games = []

    except APIError as e:
        if "404" in str(e):
            raise InvalidTeamError(f"Invalid team ID '{team_id}'. Team not found in QMJHL API.")
        raise
    except Exception as e:
        raise RuntimeError(f"Error fetching schedule data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Schedule API"}
        for record in games
        if isinstance(record, dict)
    ]


@cached(ttl=3600, cache_key_func=lambda team_id=-1, season=None, days_ahead=365, days_back=365, **kwargs: f"qmjhl_scorebar_{team_id}_{season}_{days_ahead}_{days_back}")
def getScorebarData(
    team_id: int = -1,
    season: Union[int, str] = None,
    days_ahead: int = 365,
    days_back: int = 365
) -> List[Dict]:
    """
    Scrapes QMJHL schedule using the scorebar endpoint.

    This is Pattern 1 from the API investigation. Returns game scores
    and schedule info, optimized for team-specific schedules.

    Parameters:
    - team_id (int): Team ID (-1 for all teams)
    - season (int or str): Season ID (e.g., 211)
    - days_ahead (int): Number of days ahead to fetch
    - days_back (int): Number of days back to fetch

    Returns:
    - List[Dict]: Raw scorebar records with metadata
    """
    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON
    
    console.print_info(f"Fetching QMJHL scorebar (team={team_id}, season={season})...")
    
    url = f"https://lscluster.hockeytech.com/feed/?feed=modulekit&key={QMJHLConfig.API_KEY}&view=scorebar&client_code={QMJHLConfig.CLIENT_CODE}&numberofdaysahead={days_ahead}&numberofdaysback={days_back}&season_id={season}&team_id={team_id}&lang_code=en&fmt=json"
    
    try:
        response = fetch_json(url)

        # Extract from SiteKit.Scorebar structure
        games = []
        if isinstance(response, dict) and 'SiteKit' in response:
            sitekit = response['SiteKit']
            if 'Scorebar' in sitekit:
                games = sitekit['Scorebar']
        elif isinstance(response, list):
            games = response
        else:
            games = [response] if response else []

    except Exception as e:
        raise RuntimeError(f"Error fetching scorebar data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Scorebar API"}
        for record in games
        if isinstance(record, dict)
    ]


def scrapeSchedule(
    team_id: int = -1,
    season: Union[int, str] = None,
    month: int = -1,
    location: str = 'homeaway',
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL schedule data.

    Uses the statviewfeed/schedule endpoint for structured data.

    Parameters:
    - team_id (int): Team ID (-1 for all teams)
    - season (int or str): Season ID (e.g., 211)
    - month (int): Month filter (-1 for all months)
    - location (str): 'homeaway', 'home', or 'away'
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Schedule data with metadata
    """
    raw_data = getScheduleData(team_id, season, month, location)
    return json_normalize(raw_data, output_format)


def scrapeScorebar(
    team_id: int = -1,
    season: Union[int, str] = None,
    days_ahead: int = 365,
    days_back: int = 365,
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL schedule using the scorebar endpoint.

    Parameters:
    - team_id (int): Team ID (-1 for all teams)
    - season (int or str): Season ID (e.g., 211)
    - days_ahead (int): Number of days ahead to fetch
    - days_back (int): Number of days back to fetch
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Scorebar data with metadata
    """
    raw_data = getScorebarData(team_id, season, days_ahead, days_back)
    return json_normalize(raw_data, output_format)


__all__ = [
    'getScheduleData',
    'getScorebarData',
    'scrapeSchedule',
    'scrapeScorebar'
]
