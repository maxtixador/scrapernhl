"""NHL schedule data scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize
from scrapernhl.core.progress import console
from scrapernhl.core.cache import cached
from scrapernhl.exceptions import APIError, InvalidTeamError, InvalidSeasonError


@cached(ttl=3600, cache_key_func=lambda team="MTL", season="20252026": f"schedule_{team}_{season}")
def getScheduleData(team: str = "MTL", season: Union[str, int] = "20252026") -> List[Dict]:
    """
    Scrapes raw NHL schedule data for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")

    Returns:
    - List[Dict]: Raw schedule records with metadata
    """
    console.print_info(f"Fetching schedule for {team} ({season})...")
    season = str(season)
    
    # Validate season format (should be 8 digits like 20242025)
    if not season.isdigit() or len(season) != 8:
        raise InvalidSeasonError(f"Invalid season format '{season}'. Expected 8-digit format like '20242025'.")
    
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/{season}"

    try:
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "games" in response:
            data = response["games"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except APIError as e:
        # 404 typically means invalid team code
        if "404" in str(e):
            raise InvalidTeamError(f"Invalid team code '{team}'. Team not found in NHL API.")
        raise
    except Exception as e:
        raise RuntimeError(f"Error fetching schedule data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Schedule API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeSchedule(team: str = "MTL", season: Union[str, int] = "20252026", output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL schedule data for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Schedule data with metadata in the specified format.
    """
    raw_data = getScheduleData(team, season)
    return json_normalize(raw_data, output_format)
