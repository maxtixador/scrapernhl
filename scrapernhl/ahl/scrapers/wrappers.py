"""
AHL Additional Wrapper Functions

Additional wrapper functions for AHL data that provide convenience aliases
and additional functionality beyond the base scrapers.
"""

from typing import Union, Optional
import pandas as pd
from scrapernhl.ahl.api import (
    get_scorebar, get_play_by_play, get_game_summary, AHLConfig, fetch_api
)
from datetime import datetime


def scrapeScorebar(
    days_ahead: int = 6,
    days_back: int = 0,
    season_id: Optional[int] = None,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape AHL live games and recent results as a DataFrame.
    
    Args:
        days_ahead: Number of days ahead to fetch
        days_back: Number of days back to fetch
        season_id: Season ID (uses default if None)
        config: AHLConfig instance
        
    Returns:
        DataFrame with scorebar games
    """
    data = get_scorebar(days_ahead=days_ahead, days_back=days_back, season_id=season_id, config=config)
    # AHL scorebar returns data directly in 'Scorebar' key (no SiteKit wrapper)
    games = data.get('Scorebar', []) if isinstance(data, dict) else []
    return pd.DataFrame(games)


def scrapeSkaterStats(
    season: Union[int, str] = None,
    sort: str = 'points',
    team: str = 'all',
    limit: int = 500,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape AHL skater statistics as a DataFrame.
    
    This is a convenience wrapper around the base scrapePlayerStats function.
    
    Args:
        season: Season ID (uses default if None)
        sort: Sort field ('points', 'goals', 'assists', etc.)
        team: Team filter ('all' or team ID)
        limit: Number of results to return
        config: AHLConfig instance
        
    Returns:
        DataFrame with skater stats
    """
    # Import here to avoid circular imports
    from .complete_suite import scrapePlayerStats
    return scrapePlayerStats(season=season, player_type='skater', sort=sort, limit=limit)


def scrapeGoalieStats(
    season: Union[int, str] = None,
    sort: str = 'gaa',
    team: str = 'all',
    limit: int = 200,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape AHL goalie statistics as a DataFrame.
    
    This is a convenience wrapper around the base scrapePlayerStats function.
    
    Args:
        season: Season ID (uses default if None)
        sort: Sort field ('gaa', 'savePct', 'wins', etc.)
        team: Team filter ('all' or team ID)
        limit: Number of results to return
        config: AHLConfig instance
        
    Returns:
        DataFrame with goalie stats
    """
    # Import here to avoid circular imports
    from .complete_suite import scrapePlayerStats
    return scrapePlayerStats(season=season, player_type='goalie', sort=sort, limit=limit)


def scrapePlayByPlay(game_id: int, config: AHLConfig = None) -> pd.DataFrame:
    """
    Scrape AHL play-by-play events as a DataFrame.
    
    Args:
        game_id: Game ID
        config: AHLConfig instance
        
    Returns:
        DataFrame with play-by-play events
    """
    pbp_data = get_play_by_play(game_id=game_id, config=config)
    return pd.DataFrame(pbp_data)


def scrapeGameSummary(game_id: int, config: AHLConfig = None) -> dict:
    """
    Scrape AHL game summary.
    
    Args:
        game_id: Game ID
        config: AHLConfig instance
        
    Returns:
        Dictionary with game summary data (contains multiple DataFrames)
    """
    return get_game_summary(game_id=game_id, config=config)
