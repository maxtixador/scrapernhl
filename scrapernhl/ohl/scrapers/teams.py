"""OHL teams data scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ..api import fetch_api, OHLConfig


@cached(ttl=86400, cache_key_func=lambda season=None, **kwargs: f"ohl_teams_{season}")
def getTeamsData(season: Union[int, str] = None) -> List[Dict]:
    """Scrapes raw OHL teams data."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON
    
    console.print_info(f"Fetching OHL teams (season={season})...")
    
    try:
        response = fetch_api(feed='statviewfeed', view='teamsForSeason', season=season)
        teams = response if isinstance(response, list) else []
    except Exception as e:
        raise RuntimeError(f"Error fetching teams data: {e}")

    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "OHL Teams API"} for record in teams if isinstance(record, dict)]


def scrapeTeams(season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes OHL teams data."""
    raw_data = getTeamsData(season)
    return json_normalize(raw_data, output_format)


__all__ = ['getTeamsData', 'scrapeTeams']
