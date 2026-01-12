"""QMJHL roster scrapers following NHL pattern."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import InvalidTeamError
from ..api import fetch_api, QMJHLConfig


@cached(ttl=3600, cache_key_func=lambda team_id, season=None, **kwargs: f"qmjhl_roster_{team_id}_{season}")
def getRosterData(team_id: int, season: Union[int, str] = None) -> List[Dict]:
    """
    Scrapes raw QMJHL roster data for a specific team.

    Parameters:
    - team_id (int): Team ID
    - season (int or str): Season ID (e.g., 211)

    Returns:
    - List[Dict]: Raw roster records with metadata
    """
    if team_id is None or not isinstance(team_id, int):
        raise InvalidTeamError(f"Invalid team_id: {team_id}")

    if season is None:
        season = QMJHLConfig.DEFAULT_SEASON

    console.print_info(f"Fetching QMJHL roster (team={team_id}, season={season})...")

    try:
        response = fetch_api(
            feed='statviewfeed',
            view='roster',
            team_id=team_id,
            season_id=season
        )

        # Handle different response structures
        players = []
        if isinstance(response, dict):
            if 'roster' in response and isinstance(response['roster'], list):
                # roster is a list with sections inside
                for roster_item in response['roster']:
                    if isinstance(roster_item, dict) and 'sections' in roster_item:
                        for section in roster_item['sections']:
                            if 'data' in section:
                                # Extract 'row' from each data item
                                for data_item in section['data']:
                                    if isinstance(data_item, dict) and 'row' in data_item:
                                        players.append(data_item['row'])
            elif 'players' in response:
                players = response['players']
            elif 'sections' in response:
                for section in response['sections']:
                    if 'data' in section:
                        for data_item in section['data']:
                            if isinstance(data_item, dict) and 'row' in data_item:
                                players.append(data_item['row'])
            else:
                players = [response]
        elif isinstance(response, list):
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])
        else:
            players = []

    except Exception as e:
        raise RuntimeError(f"Error fetching roster data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "QMJHL Roster API", "team_id": team_id}
        for record in players
        if isinstance(record, dict)
    ]


def scrapeRoster(
    team_id: int,
    season: Union[int, str] = None,
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrapes QMJHL roster data for a specific team.

    Parameters:
    - team_id (int): Team ID
    - season (int or str): Season ID (e.g., 211)
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Roster data with metadata
    """
    raw_data = getRosterData(team_id, season)
    return json_normalize(raw_data, output_format)


__all__ = [
    'getRosterData',
    'scrapeRoster'
]
