"""
AHL Game Scraper Module

Wrapper around the core HockeyTech scraper for AHL-specific games.
Uses the same cleaning logic as QMJHL since they share the same data structure.

Note: AHL uses a different API endpoint format (statviewfeed) but returns
similar data structure. May require minor adjustments to clean_pbp if needed.
"""

from typing import Dict, Any
import pandas as pd

from ...core.hockeytech import get_api_events as _get_api_events
from ...core.hockeytech import scrape_game as _scrape_game
from ...core.ahl_pwhl_clean import clean_ahl_pwhl


def getAPIEvents(game_id: int, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch raw event data for an AHL game.
    
    Args:
        game_id: The unique identifier for the AHL game
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        Dictionary containing play-by-play event data
        
    Example:
        >>> events = getAPIEvents(1028297)
    """
    return _get_api_events(game_id, league="ahl", timeout=timeout)


def scrape_game(game_id: int, timeout: int = 30, nhlify: bool = True) -> pd.DataFrame:
    """
    Fetch and clean play-by-play data for an AHL game.
    
    Args:
        game_id: The unique identifier for the AHL game
        timeout: Maximum time to wait for page load in seconds (default: 30)
        nhlify: If True, merge shot+goal rows into single rows (NHL-style).
                If False, keep separate rows for shots and goals (AHL-style).
    
    Returns:
        Cleaned DataFrame with play-by-play event data ready for analysis
        
    Example:
        >>> df = scrape_game(1028297)
        >>> print(df['event'].value_counts())
    """
    return _scrape_game(
        game_id,
        league="ahl",
        nhlify=nhlify,
        clean_fn=clean_ahl_pwhl,
        timeout=timeout
    )


__all__ = ['getAPIEvents', 'scrape_game']
