"""
QMJHL Game Centre Data Scraper

This module scrapes comprehensive game data from the QMJHL game centre API,
including rosters, player stats, goals with on-ice players, and more.

The data is fetched from: https://chl.ca/lhjmq/en/gamecentre/{game_id}/
API endpoint: https://lscluster.hockeytech.com/feed/?feed=gc&key=f1aa699db3d81487&game_id={game_id}&client_code=lhjmq&tab=gamesummary&lang_code=en&fmt=json

Author: Max Tixador
Date: 2026-01-07
"""

import requests
from typing import Dict, List, Any


# API configuration
API_BASE_URL = "https://lscluster.hockeytech.com/feed/"
API_KEY = "f1aa699db3d81487"
CLIENT_CODE = "lhjmq"
DEFAULT_LANG = "en"


def scrape_gamecentre(game_id: int, lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Scrape comprehensive game data from the QMJHL game centre API.

    This function fetches the complete game summary including:
    - Game information (date, venue, status, officials)
    - Home and visiting team info
    - Full rosters with player IDs and stats
    - Goals with scorer, assists, and on-ice players (+/-)
    - Goaltender stats
    - Penalties
    - Team stats by period

    Args:
        game_id: The unique game identifier
        lang: Language code ('en' or 'fr'), defaults to 'en'

    Returns:
        Dictionary containing all game centre data with keys:
        - game_info: Basic game information
        - home_team: Home team info and roster
        - visiting_team: Visiting team info and roster
        - goals: List of goals with on-ice players
        - penalties: List of all penalties
        - stats: Game statistics

    Example:
        >>> data = scrape_gamecentre(game_id=32236)
        >>> print(f"Game: {data['visiting_team']['info']['name']} @ {data['home_team']['info']['name']}")
        >>> print(f"Home roster: {len(data['home_team']['roster']['players'])} skaters")
        >>> print(f"Goals: {len(data['goals'])}")
    """
    # Fetch the game summary data
    url = f"{API_BASE_URL}?feed=gc&key={API_KEY}&game_id={game_id}&client_code={CLIENT_CODE}&tab=gamesummary&lang_code={lang}&fmt=json"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()

    if 'GC' not in data or 'Gamesummary' not in data['GC']:
        raise ValueError(f"Invalid API response for game_id {game_id}")

    gamesummary = data['GC']['Gamesummary']

    # Extract and structure the data
    return {
        'game_info': _extract_game_info(gamesummary),
        'home_team': _extract_team_data(gamesummary, 'home'),
        'visiting_team': _extract_team_data(gamesummary, 'visitor'),
        'goals': _extract_goals(gamesummary),
        'penalties': _extract_penalties(gamesummary),
        'stats': _extract_stats(gamesummary),
    }


def get_rosters(game_id: int, lang: str = DEFAULT_LANG) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get just the rosters for a game (faster than full game centre scrape).

    Returns rosters with player IDs, names, positions, and jersey numbers.
    Useful when you only need roster information without full game stats.

    Args:
        game_id: The unique game identifier
        lang: Language code ('en' or 'fr'), defaults to 'en'

    Returns:
        Dictionary with keys 'home' and 'visiting', each containing:
        - team_info: Basic team information
        - players: List of skaters with IDs and positions
        - goalies: List of goaltenders with IDs

    Example:
        >>> rosters = get_rosters(game_id=32236)
        >>> for player in rosters['home']['players']:
        ...     print(f"#{player['jersey_number']} {player['first_name']} {player['last_name']} ({player['player_id']})")
    """
    url = f"{API_BASE_URL}?feed=gc&key={API_KEY}&game_id={game_id}&client_code={CLIENT_CODE}&tab=gamesummary&lang_code={lang}&fmt=json"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    gamesummary = data['GC']['Gamesummary']

    return {
        'home': _extract_roster(gamesummary, 'home'),
        'visiting': _extract_roster(gamesummary, 'visitor'),
    }


def _extract_game_info(gamesummary: Dict[str, Any]) -> Dict[str, Any]:
    """Extract basic game information."""
    return {
        'game_id': gamesummary.get('game_ident'),
        'date': gamesummary.get('game_date'),
        'date_iso': gamesummary.get('game_date_iso_8601'),
        'status': gamesummary.get('status_value'),
        'venue': gamesummary.get('venue'),
        'game_length': gamesummary.get('game_length'),
        'officials': {
            'referee1': gamesummary.get('referee1'),
            'referee2': gamesummary.get('referee2'),
            'linesman1': gamesummary.get('linesman1'),
            'linesman2': gamesummary.get('linesman2'),
        },
        'periods': gamesummary.get('periods', []),
    }


def _extract_team_data(gamesummary: Dict[str, Any], team_type: str) -> Dict[str, Any]:
    """
    Extract complete team data including info, roster, and stats.

    Args:
        gamesummary: The game summary data
        team_type: 'home' or 'visitor'
    """
    team_key = team_type
    lineup_key = f'{team_type}_team_lineup'

    team_info = gamesummary.get(team_key, {})
    lineup = gamesummary.get(lineup_key, {})

    return {
        'info': {
            'team_id': team_info.get('team_id'),
            'name': team_info.get('name'),
            'city': team_info.get('city'),
            'nickname': team_info.get('nickname'),
            'code': team_info.get('code'),
            'division': gamesummary.get(f'{team_type}_division'),
            'division_id': gamesummary.get(f'{team_type}_division_id'),
        },
        'roster': {
            'players': lineup.get('players', []),
            'goalies': lineup.get('goalies', []),
        },
    }


def _extract_roster(gamesummary: Dict[str, Any], team_type: str) -> Dict[str, Any]:
    """
    Extract roster with minimal data (for get_rosters function).

    Returns player IDs, names, positions, and jersey numbers only.
    """
    team_key = team_type
    lineup_key = f'{team_type}_team_lineup'

    team_info = gamesummary.get(team_key, {})
    lineup = gamesummary.get(lineup_key, {})

    # Extract only essential player data
    players = []
    for player in lineup.get('players', []):
        players.append({
            'person_id': player.get('person_id'),
            'player_id': player.get('player_id'),
            'first_name': player.get('first_name'),
            'last_name': player.get('last_name'),
            'jersey_number': player.get('jersey_number'),
            'position': player.get('position_str'),
            'status': player.get('status', ''),  # C, A, or empty
            'rookie': player.get('rookie') == '1',
        })

    goalies = []
    for goalie in lineup.get('goalies', []):
        goalies.append({
            'person_id': goalie.get('person_id'),
            'player_id': goalie.get('player_id'),
            'first_name': goalie.get('first_name'),
            'last_name': goalie.get('last_name'),
            'jersey_number': goalie.get('jersey_number'),
            'position': 'G',
            'rookie': goalie.get('rookie') == '1',
        })

    return {
        'team_info': {
            'team_id': team_info.get('team_id'),
            'name': team_info.get('name'),
            'city': team_info.get('city'),
            'code': team_info.get('code'),
        },
        'players': players,
        'goalies': goalies,
    }


def _extract_goals(gamesummary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all goals with scorer, assists, and on-ice players (+/-).

    Each goal includes:
    - Period, time, location
    - Scorer and assists (with player_id)
    - On-ice players for both teams (plus/minus)
    - Goal type (PP, SH, EN, etc.)
    """
    goals = gamesummary.get('goals', [])

    formatted_goals = []
    for goal in goals:
        formatted_goals.append({
            'period': goal.get('period_id'),
            'time': goal.get('time'),
            'team_id': goal.get('team_id'),
            'home_goal': goal.get('home') == '1',
            'location': {
                'x': goal.get('x_location'),
                'y': goal.get('y_location'),
            },
            'goal_type': {
                'power_play': goal.get('power_play') == '1',
                'short_handed': goal.get('short_handed') == '1',
                'empty_net': goal.get('empty_net') == '1',
                'penalty_shot': goal.get('penalty_shot') == '1',
                'game_winning': goal.get('game_winning') == '1',
            },
            'scorer': goal.get('goal_scorer', {}),
            'assist1': goal.get('assist1_player', {}),
            'assist2': goal.get('assist2_player', {}),
            'on_ice_plus': goal.get('plus', []),  # Scoring team
            'on_ice_minus': goal.get('minus', []),  # Defending team
        })

    return formatted_goals


def _extract_penalties(gamesummary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all penalties with player info and penalty details."""
    penalties = gamesummary.get('penalties', [])

    formatted_penalties = []
    for penalty in penalties:
        formatted_penalties.append({
            'period': penalty.get('period_id'),
            'time': penalty.get('time'),
            'team_id': penalty.get('team_id'),
            'home_team': penalty.get('home') == '1',
            'player': {
                'player_id': penalty.get('player_id'),
                'first_name': penalty.get('first_name'),
                'last_name': penalty.get('last_name'),
                'jersey_number': penalty.get('jersey_number'),
            },
            'penalty': {
                'minutes': penalty.get('minutes'),
                'lang_penalty_description': penalty.get('lang_penalty_description'),
                'penalty_class': penalty.get('penalty_class'),
            },
        })

    return formatted_penalties


def _extract_stats(gamesummary: Dict[str, Any]) -> Dict[str, Any]:
    """Extract team statistics and game totals."""
    return {
        'shots_by_period': gamesummary.get('shotsByPeriod', []),
        'goals_by_period': gamesummary.get('goalsByPeriod', []),
        'power_play': {
            'goals': gamesummary.get('powerPlayGoals', []),
            'count': gamesummary.get('powerPlayCount', []),
        },
        'totals': {
            'goals': gamesummary.get('totalGoals', []),
            'shots': gamesummary.get('totalShots', []),
            'shots_on': gamesummary.get('totalShotsOn', []),
            'faceoffs': gamesummary.get('totalFaceoffs', []),
            'hits': gamesummary.get('totalHits', []),
        },
        'penalty_minutes': {
            'total': gamesummary.get('pimTotal', []),
            'bench': gamesummary.get('pimBench', []),
        },
    }


# Convenience functions for common use cases

def get_player_ids(game_id: int, team: str = 'both', lang: str = DEFAULT_LANG) -> List[str]:
    """
    Get list of player IDs for a specific team or both teams.

    Args:
        game_id: The unique game identifier
        team: 'home', 'visiting', or 'both' (default)
        lang: Language code

    Returns:
        List of player_id strings

    Example:
        >>> player_ids = get_player_ids(game_id=32236, team='home')
        >>> print(f"Found {len(player_ids)} players")
    """
    rosters = get_rosters(game_id, lang)

    player_ids = []

    if team in ('home', 'both'):
        for player in rosters['home']['players']:
            player_ids.append(player['player_id'])
        for goalie in rosters['home']['goalies']:
            player_ids.append(goalie['player_id'])

    if team in ('visiting', 'both'):
        for player in rosters['visiting']['players']:
            player_ids.append(player['player_id'])
        for goalie in rosters['visiting']['goalies']:
            player_ids.append(goalie['player_id'])

    return player_ids


def get_goals_with_onice(game_id: int, lang: str = DEFAULT_LANG) -> List[Dict[str, Any]]:
    """
    Get goals with on-ice player information.

    This is a convenience function that returns just the goals data
    without fetching the full game centre information.

    Args:
        game_id: The unique game identifier
        lang: Language code

    Returns:
        List of goals with on-ice players (+/-)

    Example:
        >>> goals = get_goals_with_onice(game_id=32236)
        >>> for goal in goals:
        ...     scorer = goal['scorer']
        ...     print(f"Goal by #{scorer['jersey_number']} {scorer['last_name']}")
        ...     print(f"  On ice (+): {len(goal['on_ice_plus'])} players")
        ...     print(f"  On ice (-): {len(goal['on_ice_minus'])} players")
    """
    data = scrape_gamecentre(game_id, lang)
    return data['goals']
