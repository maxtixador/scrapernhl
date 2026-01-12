"""
WHL Additional Wrapper Functions

Additional wrapper functions for WHL data that provide convenience aliases
and additional functionality beyond the base scrapers.
"""

from typing import Union, Optional
import pandas as pd
from scrapernhl.whl.api import (
    get_scorebar, get_play_by_play, get_game_summary, WHLConfig, fetch_api
)
from datetime import datetime


def scrapeScorebar(
    days_ahead: int = 6,
    days_back: int = 0,
    season_id: Optional[int] = None,
    config: WHLConfig = None
) -> pd.DataFrame:
    """
    Scrape WHL live games and recent results as a DataFrame.

    Args:
        days_ahead: Number of days ahead to fetch
        days_back: Number of days back to fetch
        season_id: Season ID (uses default if None)
        config: WHLConfig instance

    Returns:
        DataFrame with scorebar games
    """
    data = get_scorebar(days_ahead=days_ahead, days_back=days_back, season_id=season_id, config=config)
    # WHL scorebar returns data directly in 'Scorebar' key (no SiteKit wrapper)
    games = data.get('Scorebar', []) if isinstance(data, dict) else []
    return pd.DataFrame(games)


def scrapePlayerStats(
    season: Union[int, str] = None,
    player_type: str = 'skater',
    sort: str = 'points',
    limit: int = 50,
    config: WHLConfig = None
) -> pd.DataFrame:
    """
    Scrape WHL player statistics as a DataFrame.

    This is a unified wrapper that handles both skaters and goalies.

    Args:
        season: Season ID (uses default if None)
        player_type: Type of player ('skater' or 'goalie')
        sort: Sort field (e.g., 'points', 'goals', 'wins', 'gaa')
        limit: Number of results to return
        config: WHLConfig instance

    Returns:
        DataFrame with player stats
    """
    # Import here to avoid circular imports
    from .teams_stats_roster import scrapePlayerStats as basePlayerStats
    return basePlayerStats(season=season, player_type=player_type, sort=sort, limit=limit)


def scrapeSkaterStats(
    season: Union[int, str] = None,
    sort: str = 'points',
    team: str = 'all',
    limit: int = 500,
    config: WHLConfig = None
) -> pd.DataFrame:
    """
    Scrape WHL skater statistics as a DataFrame.
    
    This is a convenience wrapper around the base scrapePlayerStats function.
    
    Args:
        season: Season ID (uses default if None)
        sort: Sort field ('points', 'goals', 'assists', etc.)
        team: Team filter ('all' or team ID)
        limit: Number of results to return
        config: WHLConfig instance
        
    Returns:
        DataFrame with skater stats
    """
    # Import here to avoid circular imports
    from .teams_stats_roster import scrapePlayerStats
    return scrapePlayerStats(season=season, player_type='skater', sort=sort, limit=limit)


def scrapeGoalieStats(
    season: Union[int, str] = None,
    sort: str = 'gaa',
    team: str = 'all',
    limit: int = 200,
    config: WHLConfig = None
) -> pd.DataFrame:
    """
    Scrape WHL goalie statistics as a DataFrame.
    
    This is a convenience wrapper around the base scrapePlayerStats function.
    
    Args:
        season: Season ID (uses default if None)
        sort: Sort field ('gaa', 'savePct', 'wins', etc.)
        team: Team filter ('all' or team ID)
        limit: Number of results to return
        config: WHLConfig instance
        
    Returns:
        DataFrame with goalie stats
    """
    # Import here to avoid circular imports
    from .teams_stats_roster import scrapePlayerStats
    return scrapePlayerStats(season=season, player_type='goalie', sort=sort, limit=limit)


def scrapePlayByPlay(game_id: int, config: WHLConfig = None) -> pd.DataFrame:
    """
    Scrape WHL play-by-play events as a DataFrame.
    
    Args:
        game_id: Game ID
        config: WHLConfig instance
        
    Returns:
        DataFrame with play-by-play events
    """
    pbp_data = get_play_by_play(game_id=game_id, config=config)
    return pd.DataFrame(pbp_data)


def scrapeGameSummary(game_id: int, config: WHLConfig = None) -> dict:
    """
    Scrape WHL game summary.
    
    Args:
        game_id: Game ID
        config: WHLConfig instance
        
    Returns:
        Dictionary with game summary data (contains multiple DataFrames)
    """
    return get_game_summary(game_id=game_id, config=config)
