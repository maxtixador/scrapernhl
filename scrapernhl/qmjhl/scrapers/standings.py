"""QMJHL standings data scrapers following NHL pattern."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import APIError
from ..api import fetch_api, QMJHLConfig


@cached(ttl=3600, cache_key_func=lambda season=None, context='overall', special='false', group_by='division', **kwargs: f"qmjhl_standings_{season}_{context}_{group_by}")
def getStandingsData(
    season: Union[int, str] = None,
    context: str = 'overall',
    special: str = 'false',
    group_by: str = 'division'
) -> List[Dict]:
    """
    Scrapes raw QMJHL standings data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)
    - context (str): 'overall', 'home', 'away', etc.
    - special (str): 'true' or 'false'
    - group_by (str): 'division', 'conference', etc.

    Returns:
    - List[Dict]: Raw standings records with metadata
    """
    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON
    
    console.print_info(f"Fetching QMJHL standings (season={season}, context={context})...")
    
    try:
        response = fetch_api(
            feed='statviewfeed',
            view='teams',
            groupTeamsBy=group_by,
            context=context,
            special=special,
            season=season
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
        raise RuntimeError(f"Error fetching standings data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Standings API"}
        for record in teams
        if isinstance(record, dict)
    ]


def scrapeStandings(
    season: Union[int, str] = None,
    context: str = 'overall',
    special: str = 'false',
    group_by: str = 'division',
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL standings data.

    Parameters:
    - season (int or str): Season ID (e.g., 211)
    - context (str): 'overall', 'home', 'away', etc.
    - special (str): 'true' or 'false'
    - group_by (str): 'division', 'conference', etc.
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Standings data with metadata
    """
    raw_data = getStandingsData(season, context, special, group_by)
    return json_normalize(raw_data, output_format)


__all__ = [
    'getStandingsData',
    'scrapeStandings'
]
