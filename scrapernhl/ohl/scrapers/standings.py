"""OHL standings data scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ..api import fetch_api, OHLConfig


@cached(ttl=3600, cache_key_func=lambda season=None, context='overall', special='false', group_by='division', **kwargs: f"ohl_standings_{season}_{context}_{group_by}")
def getStandingsData(season: Union[int, str] = None, context: str = 'overall', special: str = 'false', group_by: str = 'division') -> List[Dict]:
    """Scrapes raw OHL standings data."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON

    console.print_info(f"Fetching OHL standings (season={season}, context={context})...")

    try:
        response = fetch_api(feed='statviewfeed', view='teams', groupTeamsBy=group_by, context=context, special=special, season=season)

        teams = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    teams.append(data_item['row'])
        elif isinstance(response, dict) and 'sections' in response:
            for section in response['sections']:
                if 'data' in section:
                    for data_item in section['data']:
                        if isinstance(data_item, dict) and 'row' in data_item:
                            teams.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching standings data: {e}")

    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "OHL Standings API"} for record in teams if isinstance(record, dict)]


def scrapeStandings(season: Union[int, str] = None, context: str = 'overall', special: str = 'false', group_by: str = 'division', output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes OHL standings data."""
    raw_data = getStandingsData(season, context, special, group_by)
    return json_normalize(raw_data, output_format)


__all__ = ['getStandingsData', 'scrapeStandings']
