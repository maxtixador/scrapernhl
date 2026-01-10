"""OHL player and team stats scrapers."""

from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import polars as pl

from ...core.utils import json_normalize
from ...core.progress import console
from ...core.cache import cached
from ..api import fetch_api, OHLConfig


@cached(ttl=3600, cache_key_func=lambda season=None, player_type='skater', sort='points', qualified='qualified', limit=50, first=0, **kwargs: f"ohl_player_stats_{season}_{player_type}_{sort}_{limit}_{first}")
def getPlayerStatsData(season: Union[int, str] = None, player_type: str = 'skater', sort: str = 'points', qualified: str = 'qualified', limit: int = 50, first: int = 0) -> List[Dict]:
    """Scrapes raw OHL player stats data."""
    if season is None:
        season = OHLConfig.DEFAULT_SEASON
    
    stats_type = 'skaters' if player_type == 'skater' else 'goalies'
    console.print_info(f"Fetching OHL {stats_type} stats (season={season})...")
    
    try:
        response = fetch_api(feed='statviewfeed', view='players', season=season, sort=sort, statsType='standard', first=first, limit=limit, qualified=qualified, site_id=OHLConfig.SITE_ID)
        
        players = []
        if isinstance(response, list) and len(response) > 0:
            for item in response:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])
    except Exception as e:
        raise RuntimeError(f"Error fetching player stats data: {e}")

    now = datetime.utcnow().isoformat()
    return [{**record, "scrapedOn": now, "source": "OHL Player Stats API"} for record in players if isinstance(record, dict)]


def scrapePlayerStats(season: Union[int, str] = None, player_type: str = 'skater', sort: str = 'points', qualified: str = 'qualified', limit: int = 50, first: int = 0, output_format: str = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrapes OHL player stats data."""
    raw_data = getPlayerStatsData(season, player_type, sort, qualified, limit, first)
    return json_normalize(raw_data, output_format)


__all__ = ['getPlayerStatsData', 'scrapePlayerStats']
