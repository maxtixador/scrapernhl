"""NHL draft data scrapers."""

import logging
from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize

LOG = logging.getLogger(__name__)


def getDraftDataData(year: Union[str, int] = "2024", round: Union[str, int] = "all") -> List[Dict]:
    """
    Scrapes NHL draft data for a given season.

    Parameters:
    - year (str or int): Season ID (e.g., "2024")
    - round (str or int): Round number (default is "all" for all rounds)

    Returns:
    - List[Dict]: Raw draft records with metadata
    """
    year = str(year)
    url = f"https://api-web.nhle.com/v1/draft/picks/{year}/{round}"

    try:
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "picks" in response:
            data = response["picks"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching draft data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "year": year, "scrapedOn": now, "source": "NHL Draft API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeDraftData(year: Union[str, int] = "2024", round: Union[str, int] = "all", output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL draft data for a given season.

    Parameters:
    - year (str or int): Season ID (e.g., "2024")
    - round (str or int): Round number (default is "all" for all rounds)
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Draft data with metadata in the specified format.
    """
    raw_data = getDraftDataData(year, round)
    return json_normalize(raw_data, output_format)


def getRecordsDraftData(year: Union[str, int] = "2025") -> List[Dict]:
    """
    Scrapes NHL draft records for a given season from NHL Records API.

    Parameters:
    - year (str or int): Season ID (e.g., "2024")

    Returns:
    - List[Dict]: Raw draft records with metadata
    """
    year = str(year)
    url = f"https://records.nhl.com/site/api/draft?include=draftProspect.id&include=player.birthStateProvince&include=player.birthCountry&include=player.position&include=player.onRoster&include=player.yearsPro&include=player.firstName&include=player.lastName&include=player.id&include=team.id&include=team.placeName&include=team.commonName&include=team.fullName&include=team.triCode&include=team.logos&include=franchiseTeam.franchise.mostRecentTeamId&include=franchiseTeam.franchise.teamCommonName&include=franchiseTeam.franchise.teamPlaceName&cayenneExp=%20draftYear%20=%20{year}&start=0&limit=500"

    try:
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "data" in response:
            data = response["data"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching draft records: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "year": year, "scrapedOn": now, "source": "NHL Draft Records API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeDraftRecords(year: Union[str, int] = "2025", output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL draft records for a given season from NHL Records API.

    Parameters:
    - year (str or int): Season ID (e.g., "2024")
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Draft records data with metadata in the specified format.
    """
    raw_data = getRecordsDraftData(year)
    return json_normalize(raw_data, output_format)


def getRecordsTeamDraftHistoryData(franchise: Union[str, int] = 1) -> List[Dict]:
    """
    Scrapes NHL team draft history for a given franchise.

    Parameters:
    - franchise (str or int): Franchise ID

    Returns:
    - List[Dict]: Raw draft history records with metadata
    """
    franchise = str(franchise)
    url = f"https://records.nhl.com/site/api/draft?include=draftProspect.id&include=franchiseTeam&include=player.birthStateProvince&include=player.birthCountry&include=player.position&include=player.onRoster&include=player.yearsPro&include=player.firstName&include=player.lastName&include=player.id&include=team.id&include=team.placeName&include=team.commonName&include=team.fullName&include=team.triCode&include=team.logos&cayenneExp=franchiseTeam.franchiseId=%22{franchise}%22"
    LOG.info(f"Fetching team draft history for franchise: {franchise} from {url}")

    try:
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "data" in response:
            data = response["data"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching team draft history: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Team Draft History API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeTeamDraftHistory(franchise: Union[str, int] = 1, output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Scrapes NHL team draft history for a given franchise from NHL Records API.

    Parameters:
    - franchise (str or int): Franchise ID
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Team draft history data with metadata in the specified format.
    """
    raw_data = getRecordsTeamDraftHistoryData(franchise)
    return json_normalize(raw_data, output_format)
