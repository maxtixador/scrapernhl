"""OHL schedule scrapers with two API patterns following QMJHL model."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import InvalidTeamError, APIError
from ..api import fetch_api, get_scorebar, OHLConfig


@cached(ttl=3600, cache_key_func=lambda team_id=-1, season=None, month=-1, location='homeaway', **kwargs: f"ohl_schedule_{team_id}_{season}_{month}_{location}")
def getScheduleData(
    team_id: int = -1,
    season: Union[int, str] = None,
    month: int = -1,
    location: str = 'homeaway'
) -> List[Dict]:
    """
    Scrapes raw OHL schedule data using statviewfeed endpoint.

    Parameters:
    - team_id (int): Team ID (-1 for all teams)
    - season (int or str): Season ID
    - month (int): Month filter (-1 for all months)
    - location (str): 'homeaway', 'home', or 'away'

    Returns:
    - List[Dict]: Raw schedule records with metadata
    """
    if season is None:
        season = OHLConfig.DEFAULT_SEASON

    console.print_info(f"Fetching OHL schedule (team={team_id}, season={season})...")

    try:
        response = fetch_api(
            feed='statviewfeed',
            view='schedule',
            team=team_id,
            season=season,
            month=month,
            location=location,
            site_id=OHLConfig.SITE_ID,
            conference_id=-1,
            division_id=-1
        )

        # Extract games from sections structure
        games = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
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
            raise InvalidTeamError(f"Invalid team ID '{team_id}'. Team not found in OHL API.")
        raise
    except Exception as e:
        raise RuntimeError(f"Error fetching schedule data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "OHL Schedule API"}
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
    Scrapes OHL schedule data.

    Parameters:
    - team_id (int): Team ID (-1 for all teams)
    - season (int or str): Season ID
    - month (int): Month filter (-1 for all months)
    - location (str): 'homeaway', 'home', or 'away'
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Schedule data with metadata
    """
    raw_data = getScheduleData(team_id, season, month, location)
    return json_normalize(raw_data, output_format)


@cached(ttl=3600, cache_key_func=lambda team_id=None, season=None, **kwargs: f"ohl_schedule_legacy_{team_id}_{season}")
def getScheduleLegacyData(team_id: Union[int, str] = None, season: Union[int, str] = None) -> List[Dict]:
    """
    Scrapes raw OHL schedule data using the scorebar endpoint (legacy method).

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
        season = OHLConfig.DEFAULT_SEASON

    console.print_info(f"Fetching OHL schedule via scorebar (team={team_id}, season={season})...")

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
    return [{**record, "scrapedOn": now, "source": "OHL Scorebar API"} for record in games if isinstance(record, dict)]


def scrapeScheduleLegacy(team_id: Union[int, str] = None, season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes OHL schedule data using the scorebar endpoint (legacy method).

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
    >>> df = scrapeScheduleLegacy(season=74)
    >>>
    >>> # Get schedule for specific team
    >>> df = scrapeScheduleLegacy(team_id=4, season=74)
    """
    raw_data = getScheduleLegacyData(team_id, season)
    return json_normalize(raw_data, output_format)


__all__ = [
    'getScheduleData',
    'scrapeSchedule',
    'getScheduleLegacyData',
    'scrapeScheduleLegacy'
]
