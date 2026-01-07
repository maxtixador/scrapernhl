"""NHL team and player statistics scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize


def getTeamStatsData(
    team: str = "MTL",
    season: Union[str, int] = "20252026",
    session: Union[str, int] = 2,
    goalies: bool = False,
) -> List[Dict]:
    """
    Scrapes NHL team statistics for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")
    - session (str or int): Session ID (default is 2) - 1 for pre-season, 2 for regular season, 3 for playoffs
    - goalies (bool): Whether to fetch goalie stats (default is False for skaters)

    Returns:
    - List[Dict]: Raw team statistics records with metadata
    """
    season = str(season)
    url = f"https://api-web.nhle.com/v1/club-stats/{team}/{season}/{session}"

    key = "goalies" if goalies else "skaters"

    try:
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and key in response:
            data = response[key]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching team stats data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Team Stats API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeTeamStats(
    team: str = "MTL",
    season: Union[str, int] = "20252026",
    session: Union[str, int] = 2,
    goalies: bool = False,
    output_format: str = "pandas",
) -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL team statistics for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")
    - session (str or int): Session ID (default is 2) - 1 for pre-season, 2 for regular season, 3 for playoffs
    - goalies (bool): Whether to fetch goalie stats (default is False for skaters)
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Team statistics data with metadata in the specified format.
    """
    raw_data = getTeamStatsData(team, season, session, goalies)
    return json_normalize(raw_data, output_format)
