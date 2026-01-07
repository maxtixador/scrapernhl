"""NHL standings data scrapers."""

from datetime import datetime
from typing import Dict, List

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize
from scrapernhl.core.progress import console
from scrapernhl.core.cache import cached


@cached(ttl=1800, cache_key_func=lambda date=None: f"standings_{date or 'default'}")
def getStandingsData(date: str = None) -> List[Dict]:
    """
    Scrapes NHL standings data for a given date.

    Parameters:
    - date (str, optional): Date in 'YYYY-MM-DD' format. Defaults to None (previous years' new year).

    Returns:
    - List[Dict]: Raw standings records with metadata
    """
    # If no date is provided, use the previous year's new year's date
    if date is None:
        date = f"{datetime.now().year - 1}-01-01"
    
    console.print_info(f"Fetching standings for {date}...")
    url = f"https://api-web.nhle.com/v1/standings/{date}"

    try:
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "standings" in response:
            data = response["standings"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching standings data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Standings API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeStandings(date: str = None, output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL standings data for a given date.

    Parameters:
    - date (str, optional): Date in 'YYYY-MM-DD' format. Defaults to None (previous years' new year).
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Standings data with metadata in the specified format.
    """
    raw_data = getStandingsData(date)
    return json_normalize(raw_data, output_format)
