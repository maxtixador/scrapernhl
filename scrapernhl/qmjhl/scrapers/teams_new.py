"""QMJHL teams data scrapers following NHL pattern."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import APIError
from ..api import fetch_api, QMJHLConfig


@cached(ttl=86400, cache_key_func=lambda season=None, **kwargs: f"qmjhl_teams_{season}")
def getTeamsData(season: Union[int, str] = None) -> List[Dict]:
    """
    Scrapes raw QMJHL teams data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)

    Returns:
    - List[Dict]: Raw team records with metadata
    """
    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON
    
    console.print_info(f"Fetching QMJHL teams (season={season})...")
    
    try:
        response = fetch_api(
            feed='statviewfeed',
            view='teamsForSeason',
            season=season
        )

        # Handle different response structures
        teams = []
        if isinstance(response, list):
            teams = response
        elif isinstance(response, dict):
            if 'teams' in response:
                teams = response['teams']
            elif 'sections' in response:
                for section in response['sections']:
                    if 'data' in section:
                        teams.extend(section['data'])
            else:
                teams = [response]
        else:
            teams = []

    except Exception as e:
        raise RuntimeError(f"Error fetching teams data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Teams API"}
        for record in teams
        if isinstance(record, dict)
    ]


def scrapeTeams(
    season: Union[int, str] = None,
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL teams data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Teams data with metadata
    """
    raw_data = getTeamsData(season)
    return json_normalize(raw_data, output_format)


__all__ = [
    'getTeamsData',
    'scrapeTeams'
]
