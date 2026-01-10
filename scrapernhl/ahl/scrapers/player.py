"""
AHL Player Scraper Module

This module provides functions to scrape comprehensive player data from the AHL API.

The player endpoint returns:
- Basic biographical data (name, birthdate, birthplace, height, weight)
- Position and jersey number
- Draft information
- Career statistics by season
- Current season statistics
- Game-by-game breakdowns
- Shot location data
- Media assets (photos)
"""

from typing import Dict, Any, Union, Optional, List
import pandas as pd

from ..api import fetch_api, AHLConfig


# ============================================================================
# RAW DATA FETCHERS
# ============================================================================

def get_player_profile(
    player_id: int,
    season_id: Union[int, str] = None,
    stats_type: str = 'standard',
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get comprehensive player profile including bio, stats, and career data.

    This function fetches detailed player information from the AHL API,
    including biographical data, current season stats, career statistics,
    and game-by-game breakdowns.

    Args:
        player_id: Player ID (e.g., 10036)
        season_id: Season ID (uses current season if None)
        stats_type: Type of stats to include ('standard', 'bio', etc.)
        config: AHLConfig instance

    Returns:
        Dict containing:
            - info: Player biographical information
            - careerStats: Career statistics by season
            - currentSeasonStats: Current season statistics
            - gameByGame: Game-by-game breakdown
            - shotLocations: Shot location data
            - draftInfo: NHL draft information
            - media: Player photos and images

    Example:
        >>> profile = get_player_profile(10036)
        >>> print(f"{profile['info']['name']} - {profile['info']['position']}")
        >>> print(f"Current team: {profile['info']['currentTeam']}")
    """
    if season_id is None:
        season_id = AHLConfig.DEFAULT_SEASON if config is None else config.DEFAULT_SEASON

    params = {
        'player_id': player_id,
        'season_id': season_id,
        'site_id': AHLConfig.SITE_ID,
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
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get player biographical information only (no stats).

    This is a lightweight version that extracts just the biographical
    data from the player profile endpoint.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        Dict with biographical information:
            - name: Player full name
            - firstName: First name
            - lastName: Last name
            - position: Playing position
            - jerseyNumber: Jersey number
            - birthDate: Date of birth
            - birthplace: City, country of birth
            - height: Height (formatted string)
            - weight: Weight in pounds
            - shoots: Shooting hand (L/R)
            - currentTeam: Current team name

    Example:
        >>> bio = get_player_bio(10036)
        >>> print(f"{bio['name']}: {bio['position']}, #{bio['jerseyNumber']}")
    """
    profile = get_player_profile(player_id, season_id, 'bio', config)

    # Extract biographical fields from the response
    if isinstance(profile, dict):
        # Try different possible structures
        if 'info' in profile:
            return profile['info']
        elif 'player' in profile:
            return profile['player']

    return profile


def get_player_stats(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get player season and career statistics.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        Dict containing:
            - seasonStats: Current season statistics
            - careerStats: Career statistics by season/league

    Example:
        >>> stats = get_player_stats(10036)
        >>> print(f"GP: {stats['seasonStats']['gamesPlayed']}")
        >>> print(f"Goals: {stats['seasonStats']['goals']}")
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
    config: AHLConfig = None
) -> List[Dict[str, Any]]:
    """
    Get player game-by-game statistics for a season.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        List of game log entries with stats for each game

    Example:
        >>> game_log = get_player_game_log(10036)
        >>> print(f"Games played: {len(game_log)}")
    """
    profile = get_player_profile(player_id, season_id, 'standard', config)

    if isinstance(profile, dict) and 'gameByGame' in profile:
        return profile['gameByGame']

    return []


def get_player_shot_locations(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> List[Dict[str, Any]]:
    """
    Get player shot location data.

    This provides coordinate data for all shots taken by the player,
    useful for analyzing shooting patterns and tendencies.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        List of shot location entries with coordinates and outcomes

    Example:
        >>> shots = get_player_shot_locations(10036)
        >>> print(f"Total shots tracked: {len(shots)}")
    """
    profile = get_player_profile(player_id, season_id, 'standard', config)

    if isinstance(profile, dict) and 'shotLocations' in profile:
        return profile['shotLocations']

    return []


def get_player_draft_info(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> Dict[str, Any]:
    """
    Get player NHL draft information.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        Dict with draft information:
            - draftYear: Year drafted
            - round: Draft round
            - overall: Overall pick number
            - team: NHL team that drafted the player

    Example:
        >>> draft = get_player_draft_info(10036)
        >>> print(f"Drafted by {draft['team']} in {draft['draftYear']}")
        >>> print(f"Round {draft['round']}, Pick #{draft['overall']}")
    """
    profile = get_player_profile(player_id, season_id, 'standard', config)

    if isinstance(profile, dict) and 'draft' in profile:
        return profile['draft']

    return {}


# ============================================================================
# DATAFRAME SCRAPERS
# ============================================================================

def scrape_player_profile(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player profile and return as a pandas DataFrame.

    This function fetches the complete player profile and flattens
    the biographical information into a single-row DataFrame for
    easy analysis and storage.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        Single-row DataFrame with player biographical data

    Example:
        >>> df = scrape_player_profile(10036)
        >>> print(df[['name', 'position', 'currentTeam']])
    """
    bio = get_player_bio(player_id, season_id, config)

    # Convert to DataFrame
    if isinstance(bio, dict):
        df = pd.DataFrame([bio])
    else:
        df = pd.DataFrame()

    return df


def scrape_player_stats(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player season statistics as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        DataFrame with season statistics

    Example:
        >>> df = scrape_player_stats(10036)
        >>> print(df[['gamesPlayed', 'goals', 'assists', 'points']])
    """
    stats = get_player_stats(player_id, season_id, config)

    if isinstance(stats, dict) and 'seasonStats' in stats:
        return pd.DataFrame([stats['seasonStats']])

    return pd.DataFrame()


def scrape_player_career_stats(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player career statistics by season as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        DataFrame with career statistics, one row per season

    Example:
        >>> df = scrape_player_career_stats(10036)
        >>> print(df[['season', 'league', 'team', 'gamesPlayed', 'points']])
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
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player game-by-game log as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        DataFrame with game-by-game statistics

    Example:
        >>> df = scrape_player_game_log(10036)
        >>> print(df[['gameDate', 'opponent', 'goals', 'assists', 'points']])
    """
    game_log = get_player_game_log(player_id, season_id, config)

    if isinstance(game_log, list) and game_log:
        return pd.DataFrame(game_log)

    return pd.DataFrame()


def scrape_player_shot_locations(
    player_id: int,
    season_id: Union[int, str] = None,
    config: AHLConfig = None
) -> pd.DataFrame:
    """
    Scrape player shot location data as a DataFrame.

    Args:
        player_id: Player ID
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance

    Returns:
        DataFrame with shot coordinates and outcomes

    Example:
        >>> df = scrape_player_shot_locations(10036)
        >>> print(df[['x', 'y', 'outcome', 'gameId']])
    """
    shots = get_player_shot_locations(player_id, season_id, config)

    if isinstance(shots, list) and shots:
        return pd.DataFrame(shots)

    return pd.DataFrame()


def scrape_multiple_players(
    player_ids: List[int],
    season_id: Union[int, str] = None,
    config: AHLConfig = None,
    include_stats: bool = True
) -> pd.DataFrame:
    """
    Scrape biographical data for multiple players.

    Args:
        player_ids: List of player IDs
        season_id: Season ID (uses current season if None)
        config: AHLConfig instance
        include_stats: If True, include current season stats

    Returns:
        DataFrame with all players' biographical data and optional stats

    Example:
        >>> player_ids = [10036, 10037, 10038]
        >>> df = scrape_multiple_players(player_ids)
        >>> print(f"Scraped {len(df)} player profiles")
    """
    profiles = []

    for player_id in player_ids:
        try:
            if include_stats:
                profile = get_player_profile(player_id, season_id, 'standard', config)
            else:
                profile = get_player_bio(player_id, season_id, config)

            if isinstance(profile, dict):
                # Flatten the profile structure
                flat_profile = {}

                # Add bio info
                if 'info' in profile:
                    flat_profile.update(profile['info'])
                elif isinstance(profile, dict) and 'name' in profile:
                    flat_profile.update(profile)

                # Add season stats if requested
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
    'get_player_draft_info',
    'scrape_player_profile',
    'scrape_player_stats',
    'scrape_player_career_stats',
    'scrape_player_game_log',
    'scrape_player_shot_locations',
    'scrape_multiple_players'
]
