"""
QMJHL Player Scraper Module

This module provides functions to scrape comprehensive player data from the QMJHL API.

The player endpoint returns:
- Basic biographical data (name, birthdate, birthplace, height, weight)
- Position and jersey number
- Career statistics by season
- Current season statistics
- Game-by-game breakdowns
"""

from typing import Dict, Any, Union, Optional, List
import pandas as pd

from ..api import fetch_api, QMJHLConfig


# ============================================================================
# RAW DATA FETCHERS
# ============================================================================

def get_player_profile(
    player_id: int,
    season_id: Union[int, str] = None,
    stats_type: str = 'standard',
    config: QMJHLConfig = None
) -> Dict[str, Any]:
    """
    Get comprehensive player profile including bio, stats, and career data.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        stats_type: Type of stats to include ('standard', 'bio', etc.)
        config: QMJHLConfig instance

    Returns:
        Dict containing player profile data
    """
    if season_id is None:
        season_id = QMJHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON

    params = {
        'player_id': player_id,
        'season_id': season_id,
        'site_id': QMJHLConfig.SITE_ID,
        'lang': 'en',
        'statsType': stats_type,
    }

    data = fetch_api(
        feed='statviewfeed',
        view='player',
        config=config,
        **params
    )

    return data


def get_player_bio(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> Dict[str, Any]:
    """
    Get player biographical information only (no stats).

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        Dict with biographical information
    """
    profile = get_player_profile(player_id, season_id, 'bio', config)

    if isinstance(profile, dict):
        if 'info' in profile:
            return profile['info']
        elif 'player' in profile:
            return profile['player']

    return profile


def get_player_stats(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> Dict[str, Any]:
    """
    Get player season and career statistics.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        Dict containing seasonStats and careerStats
    """
    profile = get_player_profile(player_id, season_id, 'standard', config)

    stats_data = {}
    if isinstance(profile, dict):
        if 'seasonStats' in profile:
            stats_data['seasonStats'] = profile['seasonStats']
        if 'careerStats' in profile:
            stats_data['careerStats'] = profile['careerStats']

    return stats_data


def get_player_game_log(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> List[Dict[str, Any]]:
    """
    Get player game-by-game statistics for a season.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        List of game log entries
    """
    profile = get_player_profile(player_id, season_id, 'standard', config)

    if isinstance(profile, dict) and 'gameByGame' in profile:
        return profile['gameByGame']

    return []


def get_player_shot_locations(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> List[Dict[str, Any]]:
    """
    Get player shot location data.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        List of shot location entries
    """
    profile = get_player_profile(player_id, season_id, 'standard', config)

    if isinstance(profile, dict) and 'shotLocations' in profile:
        return profile['shotLocations']

    return []


# ============================================================================
# DATAFRAME SCRAPERS
# ============================================================================

def scrape_player_profile(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player profile and return as a pandas DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        Single-row DataFrame with player biographical data
    """
    bio = get_player_bio(player_id, season_id, config)

    if isinstance(bio, dict):
        df = pd.DataFrame([bio])
    else:
        df = pd.DataFrame()

    return df


def scrape_player_stats(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player season statistics as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        DataFrame with season statistics
    """
    stats = get_player_stats(player_id, season_id, config)

    if isinstance(stats, dict) and 'seasonStats' in stats:
        return pd.DataFrame([stats['seasonStats']])

    return pd.DataFrame()


def scrape_player_career_stats(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player career statistics by season as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        DataFrame with career statistics, one row per season
    """
    stats = get_player_stats(player_id, season_id, config)

    if isinstance(stats, dict) and 'careerStats' in stats:
        career_data = stats['careerStats']
        if isinstance(career_data, list):
            return pd.DataFrame(career_data)

    return pd.DataFrame()


def scrape_player_game_log(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player game-by-game log as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        DataFrame with game-by-game statistics
    """
    game_log = get_player_game_log(player_id, season_id, config)

    if isinstance(game_log, list) and game_log:
        return pd.DataFrame(game_log)

    return pd.DataFrame()


def scrape_player_shot_locations(
    player_id: int,
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player shot location data as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance

    Returns:
        DataFrame with shot coordinates and outcomes
    """
    shots = get_player_shot_locations(player_id, season_id, config)

    if isinstance(shots, list) and shots:
        return pd.DataFrame(shots)

    return pd.DataFrame()


def scrape_multiple_players(
    player_ids: List[int],
    season_id: Union[int, str] = None,
    config: QMJHLConfig = None,
    include_stats: bool = True
) -> pd.DataFrame:
    """
    Scrape biographical data for multiple players.

    Args:
        player_ids: List of player IDs
        season_id: Season ID (uses current season if None)
        config: QMJHLConfig instance
        include_stats: If True, include current season stats

    Returns:
        DataFrame with all players' biographical data and optional stats
    """
    profiles = []

    for player_id in player_ids:
        try:
            if include_stats:
                profile = get_player_profile(player_id, season_id, 'standard', config)
            else:
                profile = get_player_bio(player_id, season_id, config)

            if isinstance(profile, dict):
                flat_profile = {}

                if 'info' in profile:
                    flat_profile.update(profile['info'])
                elif isinstance(profile, dict) and 'name' in profile:
                    flat_profile.update(profile)

                if include_stats and 'seasonStats' in profile:
                    flat_profile.update(profile['seasonStats'])

                flat_profile['player_id'] = player_id
                profiles.append(flat_profile)

        except Exception as e:
            print(f"Error scraping player {player_id}: {e}")
            continue

    if profiles:
        return pd.DataFrame(profiles)

    return pd.DataFrame()


__all__ = [
    'get_player_profile',
    'get_player_bio',
    'get_player_stats',
    'get_player_game_log',
    'get_player_shot_locations',
    'scrape_player_profile',
    'scrape_player_stats',
    'scrape_player_career_stats',
    'scrape_player_game_log',
    'scrape_player_shot_locations',
    'scrape_multiple_players'
]
