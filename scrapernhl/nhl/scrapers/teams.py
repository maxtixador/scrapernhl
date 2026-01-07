"""NHL team data scrapers."""

from datetime import datetime
from typing import Dict, List

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize
from scrapernhl.core.progress import console
from scrapernhl.core.cache import cached


@cached(ttl=86400, cache_key_func=lambda source="calendar": f"teams_{source}")
def getTeamsData(source: str = "calendar") -> List[Dict]:
    """
    Scrapes NHL team data from various public endpoints and enriches it with metadata to dict format.

    Parameters:
    - source (str): One of ["calendar", "franchise", "records"]

    Returns:
    - List[Dict]: Raw enriched team data with metadata.
    """
    console.print_info(f"Fetching teams data from {source}...")
    source_dict = {

        "calendar": "https://api-web.nhle.com/v1/schedule-calendar/now",
        "franchise": "https://api.nhle.com/stats/rest/en/franchise?sort=fullName&include=lastSeason.id&include=firstSeason.id",
        "records": (
            "https://records.nhl.com/site/api/franchise?"
            "include=teams.id&include=teams.active&include=teams.triCode&"
            "include=teams.placeName&include=teams.commonName&include=teams.fullName&"
            "include=teams.logos&include=teams.conference.name&include=teams.division.name&"
            "include=teams.franchiseTeam.firstSeason.id&include=teams.franchiseTeam.lastSeason.id"
        ),
    }

    if source not in source_dict:
        print(f"[Warning] Invalid source '{source}', falling back to 'default'.")
        source = "default"

    try:
        url = source_dict[source]
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "data" in response:
            data = response["data"]
        elif isinstance(response, dict) and "teams" in response:
            data = response["teams"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching data from {source}: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": source}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeTeams(source: str = "calendar", output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL team data from various public endpoints and enriches it with metadata.

    Parameters:
    - source (str): One of ["calendar", "franchise", "records"]
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Enriched team data with metadata in the specified format.
    """
    from scrapernhl.core.schema import standardize_columns
    
    raw_data = getTeamsData(source)
    df = json_normalize(raw_data, output_format)
    
    # Standardize column names if pandas format
    if output_format == "pandas" and isinstance(df, pd.DataFrame):
        df = standardize_columns(df, "teams", strict=False, warn_missing=False)
    
    return df

