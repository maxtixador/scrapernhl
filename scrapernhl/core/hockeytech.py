"""
Generic HockeyTech/LeagueStat API Scraper

This module provides a unified interface for scraping play-by-play data from leagues
that use the HockeyTech/LeagueStat platform:
- QMJHL (Quebec Major Junior Hockey League)
- OHL (Ontario Hockey League)
- WHL (Western Hockey League)
- AHL (American Hockey League)
- PWHL (Professional Women's Hockey League)

All these leagues use the same API structure with different client codes and keys.
"""

from __future__ import annotations

import re
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass

import requests
import pandas as pd


@dataclass
class LeagueConfig:
    """Configuration for a HockeyTech league."""
    client_code: str
    api_key: str
    base_url: str = "https://lscluster.hockeytech.com/feed/"
    feed_type: str = "gc"  # 'gc' or 'statviewfeed'
    
    def get_api_url(self, game_id: int, lang: str = "en") -> str:
        """Generate the API URL for a game."""
        if self.feed_type == "gc":
            # QMJHL, OHL, WHL pattern
            return (
                f"{self.base_url}?feed=gc&key={self.api_key}&client_code={self.client_code}"
                f"&game_id={game_id}&lang_code={lang}&fmt=json&tab=pxpverbose"
            )
        elif self.feed_type == "statviewfeed":
            # AHL, PWHL pattern
            return (
                f"{self.base_url}index.php?feed=statviewfeed&view=gameCenterPlayByPlay"
                f"&game_id={game_id}&key={self.api_key}&client_code={self.client_code}"
                f"&lang={lang}&league_id="
            )
        else:
            raise ValueError(f"Unknown feed_type: {self.feed_type}")


# League configurations
LEAGUE_CONFIGS = {
    "qmjhl": LeagueConfig(
        client_code="lhjmq",
        api_key="f322673b6bcae299",
        base_url="https://cluster.leaguestat.com/feed/index.php",
        feed_type="gc"
    ),
    "ohl": LeagueConfig(
        client_code="ohl",
        api_key="f1aa699db3d81487",
        feed_type="gc"
    ),
    "whl": LeagueConfig(
        client_code="whl",
        api_key="f1aa699db3d81487",
        feed_type="gc"
    ),
    "ahl": LeagueConfig(
        client_code="ahl",
        api_key="ccb91f29d6744675",
        feed_type="statviewfeed"
    ),
    "pwhl": LeagueConfig(
        client_code="pwhl",
        api_key="446521baf8c38984",
        feed_type="statviewfeed"
    ),
}


def get_api_events(
    game_id: int,
    league: str = "qmjhl",
    timeout: int = 10,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Fetch raw event data from HockeyTech API for any supported league.
    
    Args:
        game_id: The unique identifier for the game
        league: League code ('qmjhl', 'ohl', 'whl', 'ahl', 'pwhl')
        timeout: Request timeout in seconds (default: 10)
        lang: Language code ('en' or 'fr')
    
    Returns:
        Dictionary containing play-by-play event data
        
    Raises:
        ValueError: If league is not supported
        requests.RequestException: If the API request fails
        KeyError: If the response format is unexpected
        
    Example:
        >>> events = get_api_events(31171, league='qmjhl')
        >>> events = get_api_events(28528, league='ohl')
        >>> events = get_api_events(1028297, league='ahl')
    """
    league = league.lower()
    
    if league not in LEAGUE_CONFIGS:
        raise ValueError(
            f"Unsupported league: {league}. "
            f"Supported leagues: {', '.join(LEAGUE_CONFIGS.keys())}"
        )
    
    config = LEAGUE_CONFIGS[league]
    url = config.get_api_url(game_id, lang)
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Handle JSONP responses (some endpoints return JSONP)
        content = response.text
        
        # Remove JSONP callback wrapper if present
        if content.startswith(('jsonp_', 'angular.callbacks')):
            # Extract JSON from JSONP: callback_name({...})
            match = re.search(r'\((.*)\);?\s*$', content, re.DOTALL)
            if match:
                content = match.group(1)
        elif content.startswith('([') or content.startswith('({'):
            # Some APIs return bare JSONP without callback name: ([...]) or ({...})
            content = content[1:-1]  # Remove wrapping parentheses
        
        data = json.loads(content)
        
        # Extract the actual event data based on feed type
        if config.feed_type == "gc":
            # QMJHL, OHL, WHL format
            return data["GC"]["Pxpverbose"]
        elif config.feed_type == "statviewfeed":
            # AHL, PWHL format - data is already an array of events
            return data

        
    except requests.RequestException as e:
        raise requests.RequestException(
            f"Failed to fetch {league.upper()} game {game_id}: {e}"
        )
    except (KeyError, json.JSONDecodeError) as e:
        raise KeyError(
            f"Unexpected API response format for {league.upper()} game {game_id}: {e}"
        )


def scrape_game(
    game_id: int,
    league: str = "qmjhl",
    nhlify: bool = True,
    clean_fn: Optional[callable] = None,
    timeout: int = 30,
    lang: str = "en"
) -> pd.DataFrame:
    """
    Fetch and clean play-by-play data for any HockeyTech league.
    
    Args:
        game_id: The unique identifier for the game
        league: League code ('qmjhl', 'ohl', 'whl', 'ahl', 'pwhl')
        nhlify: If True, merge shot+goal rows into single rows (NHL-style)
        clean_fn: Optional custom cleaning function. If None, uses default cleaning.
        timeout: Maximum time to wait for page load in seconds
        lang: Language code ('en' or 'fr')
    
    Returns:
        Cleaned DataFrame with play-by-play event data ready for analysis
        
    Example:
        >>> # QMJHL game
        >>> df = scrape_game(31171, league='qmjhl')
        >>> 
        >>> # OHL game
        >>> df = scrape_game(28528, league='ohl')
        >>> 
        >>> # AHL game with custom cleaning
        >>> from scrapernhl.ahl.scrapers.games import clean_pbp as ahl_clean
        >>> df = scrape_game(1028297, league='ahl', clean_fn=ahl_clean)
    """
    # Fetch raw data
    data = get_api_events(game_id, league, timeout, lang)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["game_id"] = int(game_id)
    df["league"] = league.upper()
    
    # Apply cleaning function
    if clean_fn is not None:
        df = clean_fn(df, nhlify=nhlify)
    else:
        # Use default cleaning (import here to avoid circular imports)
        from ..qmjhl.scrapers.games import clean_pbp
        df = clean_pbp(df, nhlify=nhlify)
    
    return df


def get_league_config(league: str) -> LeagueConfig:
    """
    Get the configuration for a specific league.
    
    Args:
        league: League code ('qmjhl', 'ohl', 'whl', 'ahl', 'pwhl')
    
    Returns:
        LeagueConfig object
        
    Raises:
        ValueError: If league is not supported
    """
    league = league.lower()
    if league not in LEAGUE_CONFIGS:
        raise ValueError(
            f"Unsupported league: {league}. "
            f"Supported leagues: {', '.join(LEAGUE_CONFIGS.keys())}"
        )
    return LEAGUE_CONFIGS[league]


__all__ = [
    'LeagueConfig',
    'LEAGUE_CONFIGS',
    'get_api_events',
    'scrape_game',
    'get_league_config',
]
