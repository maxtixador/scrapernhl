"""
Helper functions to extract data from bootstrap objects.

Bootstrap data is cached metadata that includes leagues, seasons, teams, etc.
These helpers make it easy to extract specific data from any league's bootstrap.
"""

import pandas as pd
from typing import Union, List, Dict, Any


def get_leagues(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract leagues information from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with leagues data
    """
    if 'leagues' in bootstrap:
        data = bootstrap['leagues']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_seasons(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract seasons information from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with seasons data
    """
    if 'seasons' in bootstrap:
        data = bootstrap['seasons']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_regular_seasons(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract regular seasons from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with regular seasons data
    """
    if 'regularSeasons' in bootstrap:
        data = bootstrap['regularSeasons']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_playoff_seasons(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract playoff seasons from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with playoff seasons data
    """
    if 'playoffSeasons' in bootstrap:
        data = bootstrap['playoffSeasons']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_teams(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract teams from bootstrap (includes 'All Teams').

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with teams data (including 'All Teams' entry)
    """
    if 'teams' in bootstrap:
        data = bootstrap['teams']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_teams_no_all(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract teams from bootstrap (excludes 'All Teams').

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with teams data (no 'All Teams' entry)
    """
    if 'teamsNoAll' in bootstrap:
        data = bootstrap['teamsNoAll']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_divisions(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract divisions from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with divisions data
    """
    if 'divisions' in bootstrap:
        data = bootstrap['divisions']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    # Try divisionsAll as fallback
    elif 'divisionsAll' in bootstrap:
        data = bootstrap['divisionsAll']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_conferences(bootstrap: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract conferences from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        DataFrame with conferences data
    """
    if 'conferences' in bootstrap:
        data = bootstrap['conferences']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    # Try conferencesAll as fallback
    elif 'conferencesAll' in bootstrap:
        data = bootstrap['conferencesAll']
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
    return pd.DataFrame()


def get_current_season_id(bootstrap: Dict[str, Any]) -> Union[int, None]:
    """
    Get the current season ID from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        Current season ID or None
    """
    return bootstrap.get('current_season_id')


def get_current_league_id(bootstrap: Dict[str, Any]) -> Union[int, None]:
    """
    Get the current league ID from bootstrap.

    Args:
        bootstrap: Bootstrap dict from get_bootstrap()

    Returns:
        Current league ID or None
    """
    return bootstrap.get('current_league_id')


# Convenience exports
__all__ = [
    'get_leagues',
    'get_seasons',
    'get_regular_seasons',
    'get_playoff_seasons',
    'get_teams',
    'get_teams_no_all',
    'get_divisions',
    'get_conferences',
    'get_current_season_id',
    'get_current_league_id',
]
