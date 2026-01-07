"""NHL roster data scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize


def getRosterData(team: str = "MTL", season: Union[str, int] = "20242025") -> List[Dict]:
    """
    Scrapes NHL roster data for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")

    Returns:
    - List[Dict]: Raw roster records with metadata
    """
    season = str(season)
    url = f"https://api-web.nhle.com/v1/roster/{team}/{season}"

    try:
        response = fetch_json(url)

        # Normalize nested keys - roster has forwards, defensemen, goalies
        data = []
        if isinstance(response, dict):
            for position in ["forwards", "defensemen", "goalies"]:
                if position in response:
                    data.extend(response[position])
        elif isinstance(response, list):
            data = response

    except Exception as e:
        raise RuntimeError(f"Error fetching roster data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Roster API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeRoster(team: str = "MTL", season: Union[str, int] = "20242025", output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL roster data for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Roster data with metadata in the specified format.
    """
    raw_data = getRosterData(team, season)
    return json_normalize(raw_data, output_format)
