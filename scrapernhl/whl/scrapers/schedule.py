"""WHL schedule scrapers."""

from datetime import datetime
from typing import Dict, List, Union
import pandas as pd
import polars as pl
from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ...exceptions import InvalidTeamError, APIError
from ..api import fetch_api, WHLConfig

@cached(ttl=3600, cache_key_func=lambda team_id=-1, season=None, month=-1, location='homeaway', **kwargs: f"whl_schedule_{team_id}_{season}_{month}_{location}")
def getScheduleData(team_id: int = -1, season: Union[int, str] = None, month: int = -1, location: str = 'homeaway') -> List[Dict]:
    """Scrapes raw WHL schedule data."""
    if season is None:
        season = WHLConfig.DEFAULT_SEASON
    console.print_info(f"Fetching WHL schedule (team={team_id}, season={season})...")
    try:
        response = fetch_api(feed='statviewfeed', view='schedule', team=team_id, season=season, month=month, location=location, site_id=WHLConfig.SITE_ID, conference_id=-1, division_id=-1)
        games = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    games.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching schedule data: {e}")
    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "WHL Schedule API"} for record in games if isinstance(record, dict)]

def scrapeSchedule(team_id: int = -1, season: Union[int, str] = None, month: int = -1, location: str = 'homeaway', output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes WHL schedule data."""
    raw_data = getScheduleData(team_id, season, month, location)
    return json_normalize(raw_data, output_format)

__all__ = ['getScheduleData', 'scrapeSchedule']
