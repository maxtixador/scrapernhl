"""OHL teams data scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ..api import get_bootstrap, OHLConfig


@cached(ttl=86400, cache_key_func=lambda season=None, **kwargs: f"ohl_teams_{season if season is not None else OHLConfig.DEFAULT_SEASON}")
def getTeamsData(season: Union[int, str] = None) -> List[Dict]:
    """Scrapes raw OHL teams data from bootstrap."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON

    console.print_info(f"Fetching OHL teams (season={season})...")

    try:
        # Use bootstrap data which contains correct teams list
        bootstrap = get_bootstrap()
        # Use teamsNoAll to exclude 'All Teams' entry, fall back to teams
        if isinstance(bootstrap, dict):
            if 'teamsNoAll' in bootstrap and len(bootstrap['teamsNoAll']) > 0:
                teams = bootstrap['teamsNoAll']
            elif 'teams' in bootstrap:
                # Filter out 'All Teams' entry (id=-1)
                teams = [t for t in bootstrap['teams'] if t.get('id') != -1 and t.get('id') != '-1']
            else:
                teams = []
        else:
            teams = []
    except Exception as e:
        raise RuntimeError(f"Error fetching teams data: {e}")

    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "OHL Teams API"} for record in teams if isinstance(record, dict)]


def scrapeTeams(season: Union[int, str] = None, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes OHL teams data."""
    raw_data = getTeamsData(season)
    return json_normalize(raw_data, output_format)


__all__ = ['getTeamsData', 'scrapeTeams']
