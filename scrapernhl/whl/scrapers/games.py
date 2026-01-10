"""
WHL Game Scraper Module

Wrapper around the core HockeyTech scraper for WHL-specific games.
Uses the same cleaning logic as QMJHL since they share the same data structure.
"""

from typing import Dict, Any
import pandas as pd

from ...core.hockeytech import get_api_events as _get_api_events
from ...core.hockeytech import scrape_game as _scrape_game
from ...qmjhl.scrapers.games import clean_pbp


def getAPIEvents(game_id: int, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch raw event data for a WHL game.
    
    Args:
        game_id: The unique identifier for the WHL game
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        Dictionary containing play-by-play event data
        
    Example:
        >>> events = getAPIEvents(1022565)
    """
    return _get_api_events(game_id, league="whl", timeout=timeout)


def scrape_game(game_id: int, timeout: int = 30, nhlify: bool = True) -> pd.DataFrame:
    """
    Fetch and clean play-by-play data for a WHL game.
    
    Args:
        game_id: The unique identifier for the WHL game
        timeout: Maximum time to wait for page load in seconds (default: 30)
        nhlify: If True, merge shot+goal rows into single rows (NHL-style).
                If False, keep separate rows for shots and goals (WHL-style).
    
    Returns:
        Cleaned DataFrame with play-by-play event data ready for analysis
        
    Example:
        >>> df = scrape_game(1022565)
        >>> print(df['event'].value_counts())
    """
    return _scrape_game(
        game_id,
        league="whl",
        nhlify=nhlify,
        clean_fn=clean_pbp,
        timeout=timeout
    )


__all__ = ['getAPIEvents', 'scrape_game']
