"""NHL player statistics and information scrapers.

This module provides comprehensive player data scraping including:
- Player profiles and biographical information
- Season statistics (regular season and playoffs)
- Career statistics
- Game logs
- Advanced metrics

All functions support caching to minimize API calls and improve performance.
"""

from datetime import datetime
from typing import Dict, List, Union, Optional, Literal

import pandas as pd
import polars as pl

from scrapernhl.core.http import fetch_json
from scrapernhl.core.utils import json_normalize
from scrapernhl.core.progress import console
from scrapernhl.core.cache import cached
from scrapernhl.exceptions import InvalidGameError, APIError


@cached(ttl=86400, cache_key_func=lambda player_id: f"player_profile_{player_id}")
def getPlayerProfile(player_id: Union[str, int]) -> Dict:
    """
    Get detailed player profile information.
    
    Parameters:
    - player_id: NHL player ID (e.g., 8478402 for Auston Matthews)
    
    Returns:
    - Dict: Player profile including biographical data, current team, etc.
    
    Raises:
    - APIError: If API request fails
    
    Examples:
        >>> profile = getPlayerProfile(8478402)
        >>> print(f"{profile['firstName']} {profile['lastName']}")
        Auston Matthews
    """
    player_id = str(player_id)
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    
    console.print_info(f"Fetching profile for player {player_id}...")
    
    try:
        response = fetch_json(url)
        
        if not isinstance(response, dict):
            raise APIError(f"Invalid response format for player {player_id}")
        
        # Enrich with metadata
        now = datetime.utcnow().isoformat()
        response['scrapedOn'] = now
        response['source'] = 'NHL Player API'
        response['playerId'] = player_id
        
        return response
        
    except Exception as e:
        raise APIError(f"Error fetching player profile for {player_id}: {e}")


@cached(ttl=3600, cache_key_func=lambda player_id, season: f"player_stats_{player_id}_{season}")
def getPlayerSeasonStats(
    player_id: Union[str, int],
    season: Union[str, int] = "20232024"
) -> Dict:
    """
    Get player statistics for a specific season.
    
    Parameters:
    - player_id: NHL player ID
    - season: Season ID (e.g., "20232024")
    
    Returns:
    - Dict: Season statistics including regular season and playoffs
    
    Examples:
        >>> stats = getPlayerSeasonStats(8478402, "20232024")
        >>> print(f"Goals: {stats['regularSeason']['goals']}")
    """
    player_id = str(player_id)
    season = str(season)
    
    # Use landing page which includes season stats
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    
    console.print_info(f"Fetching season stats for player {player_id} ({season})...")
    
    try:
        response = fetch_json(url)
        
        if not isinstance(response, dict):
            raise APIError(f"Invalid response format for player {player_id}")
        
        # Extract season-specific stats
        season_stats = {
            'playerId': player_id,
            'season': season,
            'featuredStats': response.get('featuredStats', {}),
            'careerTotals': response.get('careerTotals', {}),
            'scrapedOn': datetime.utcnow().isoformat(),
            'source': 'NHL Player API'
        }
        
        return season_stats
        
    except Exception as e:
        raise APIError(f"Error fetching season stats for player {player_id}: {e}")


@cached(ttl=7200, cache_key_func=lambda player_id, season, game_type: f"player_gamelog_{player_id}_{season}_{game_type}")
def getPlayerGameLog(
    player_id: Union[str, int],
    season: Union[str, int] = "20232024",
    game_type: Literal["2", "3"] = "2"
) -> List[Dict]:
    """
    Get player game-by-game statistics for a season.
    
    Parameters:
    - player_id: NHL player ID
    - season: Season ID (e.g., "20232024")
    - game_type: Game type ("2" for regular season, "3" for playoffs)
    
    Returns:
    - List[Dict]: List of game log entries
    
    Examples:
        >>> gamelog = getPlayerGameLog(8478402, "20232024")
        >>> print(f"Games played: {len(gamelog)}")
    """
    player_id = str(player_id)
    season = str(season)
    
    url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/{season}/{game_type}"
    
    console.print_info(f"Fetching game log for player {player_id} ({season})...")
    
    try:
        response = fetch_json(url)
        
        # Response can be a dict with 'gameLog' key or a list
        if isinstance(response, dict):
            games = response.get('gameLog', [])
        elif isinstance(response, list):
            games = response
        else:
            games = []
        
        # Enrich with metadata
        now = datetime.utcnow().isoformat()
        enriched_games = []
        for game in games:
            if isinstance(game, dict):
                enriched_game = {
                    **game,
                    'playerId': player_id,
                    'season': season,
                    'gameType': game_type,
                    'scrapedOn': now,
                    'source': 'NHL Player Game Log API'
                }
                enriched_games.append(enriched_game)
        
        return enriched_games
        
    except Exception as e:
        raise APIError(f"Error fetching game log for player {player_id}: {e}")


def scrapePlayerProfile(
    player_id: Union[str, int],
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape player profile and return as DataFrame.
    
    Parameters:
    - player_id: NHL player ID
    - output_format: One of ["pandas", "polars"]
    
    Returns:
    - DataFrame with player profile information
    """
    raw_data = getPlayerProfile(player_id)
    return json_normalize([raw_data], output_format)


def scrapePlayerSeasonStats(
    player_id: Union[str, int],
    season: Union[str, int] = "20232024",
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape player season statistics and return as DataFrame.
    
    Parameters:
    - player_id: NHL player ID
    - season: Season ID (e.g., "20232024")
    - output_format: One of ["pandas", "polars"]
    
    Returns:
    - DataFrame with season statistics
    """
    raw_data = getPlayerSeasonStats(player_id, season)
    return json_normalize([raw_data], output_format)


def scrapePlayerGameLog(
    player_id: Union[str, int],
    season: Union[str, int] = "20232024",
    game_type: Literal["2", "3"] = "2",
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape player game log and return as DataFrame.
    
    Parameters:
    - player_id: NHL player ID
    - season: Season ID (e.g., "20232024")
    - game_type: Game type ("2" for regular season, "3" for playoffs)
    - output_format: One of ["pandas", "polars"]
    
    Returns:
    - DataFrame with game-by-game statistics
    """
    raw_data = getPlayerGameLog(player_id, season, game_type)
    return json_normalize(raw_data, output_format)


def scrapeMultiplePlayerStats(
    player_ids: List[Union[str, int]],
    season: Union[str, int] = "20232024",
    output_format: str = "pandas",
    show_progress: bool = True
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape statistics for multiple players with progress tracking.
    
    Parameters:
    - player_ids: List of NHL player IDs
    - season: Season ID (e.g., "20232024")
    - output_format: One of ["pandas", "polars"]
    - show_progress: Whether to show progress bar
    
    Returns:
    - Combined DataFrame with stats for all players
    
    Examples:
        >>> player_ids = [8478402, 8479318, 8480012]  # Matthews, McDavid, Draisaitl
        >>> stats = scrapeMultiplePlayerStats(player_ids, "20232024")
        >>> print(f"Scraped stats for {len(stats)} players")
    """
    from scrapernhl.core.progress import create_progress_bar
    
    all_stats = []
    failed_players = []
    
    if show_progress:
        with create_progress_bar() as progress:
            task = progress.add_task(
                "[cyan]Scraping player stats...",
                total=len(player_ids)
            )
            
            for player_id in player_ids:
                try:
                    stats_df = scrapePlayerSeasonStats(player_id, season, output_format)
                    all_stats.append(stats_df)
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print_error(f"Failed to scrape player {player_id}: {e}")
                    failed_players.append(player_id)
                    progress.update(task, advance=1)
    else:
        for player_id in player_ids:
            try:
                stats_df = scrapePlayerSeasonStats(player_id, season, output_format)
                all_stats.append(stats_df)
            except Exception as e:
                console.print_error(f"Failed to scrape player {player_id}: {e}")
                failed_players.append(player_id)
    
    # Combine all dataframes
    if not all_stats:
        console.print_warning("No player stats successfully scraped")
        if output_format == "polars":
            return pl.DataFrame()
        return pd.DataFrame()
    
    if output_format == "polars":
        combined = pl.concat(all_stats, how="vertical")
    else:
        combined = pd.concat(all_stats, ignore_index=True)
    
    success_count = len(all_stats)
    total_count = len(player_ids)
    
    if failed_players:
        console.print_warning(f"Failed to scrape {len(failed_players)} players: {failed_players}")
    
    console.print_success(f"Successfully scraped stats for {success_count}/{total_count} players")
    
    return combined


@cached(ttl=3600, cache_key_func=lambda team_abbr, season: f"team_roster_{team_abbr}_{season}")
def getTeamRoster(
    team_abbr: str,
    season: Union[str, int] = "20232024"
) -> List[Dict]:
    """
    Get full roster for a team in a given season.
    
    Parameters:
    - team_abbr: Team abbreviation (e.g., "TOR")
    - season: Season ID (e.g., "20232024")
    
    Returns:
    - List[Dict]: List of player dictionaries with IDs and basic info
    
    Examples:
        >>> roster = getTeamRoster("TOR", "20232024")
        >>> player_ids = [p['id'] for p in roster]
    """
    team_abbr = team_abbr.upper()
    season = str(season)
    
    url = f"https://api-web.nhle.com/v1/roster/{team_abbr}/{season}"
    
    console.print_info(f"Fetching roster for {team_abbr} ({season})...")
    
    try:
        response = fetch_json(url)
        
        if not isinstance(response, dict):
            raise APIError(f"Invalid response format for team {team_abbr}")
        
        # Extract all players from forwards, defensemen, and goalies
        all_players = []
        now = datetime.utcnow().isoformat()
        
        for position_group in ['forwards', 'defensemen', 'goalies']:
            players = response.get(position_group, [])
            for player in players:
                if isinstance(player, dict):
                    enriched_player = {
                        **player,
                        'teamAbbr': team_abbr,
                        'season': season,
                        'positionGroup': position_group,
                        'scrapedOn': now,
                        'source': 'NHL Roster API'
                    }
                    all_players.append(enriched_player)
        
        return all_players
        
    except Exception as e:
        raise APIError(f"Error fetching roster for team {team_abbr}: {e}")


def scrapeTeamRoster(
    team_abbr: str,
    season: Union[str, int] = "20232024",
    output_format: str = "pandas"
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape team roster and return as DataFrame.
    
    Parameters:
    - team_abbr: Team abbreviation (e.g., "TOR")
    - season: Season ID (e.g., "20232024")
    - output_format: One of ["pandas", "polars"]
    
    Returns:
    - DataFrame with roster information
    
    Examples:
        >>> roster = scrapeTeamRoster("TOR", "20232024")
        >>> print(f"Roster size: {len(roster)}")
    """
    raw_data = getTeamRoster(team_abbr, season)
    return json_normalize(raw_data, output_format)


def scrapeTeamPlayerStats(
    team_abbr: str,
    season: Union[str, int] = "20232024",
    output_format: str = "pandas",
    show_progress: bool = True
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape statistics for all players on a team.
    
    This is a convenience function that:
    1. Gets the team roster
    2. Scrapes stats for each player
    3. Returns combined DataFrame
    
    Parameters:
    - team_abbr: Team abbreviation (e.g., "TOR")
    - season: Season ID (e.g., "20232024")
    - output_format: One of ["pandas", "polars"]
    - show_progress: Whether to show progress bar
    
    Returns:
    - Combined DataFrame with stats for all players on the team
    
    Examples:
        >>> stats = scrapeTeamPlayerStats("TOR", "20232024")
        >>> print(f"Total players: {len(stats)}")
    """
    # Get roster first
    roster = getTeamRoster(team_abbr, season)
    
    # Extract player IDs
    player_ids = [p.get('id') for p in roster if p.get('id')]
    
    if not player_ids:
        console.print_warning(f"No players found for {team_abbr}")
        if output_format == "polars":
            return pl.DataFrame()
        return pd.DataFrame()
    
    console.print_info(f"Found {len(player_ids)} players for {team_abbr}")
    
    # Scrape stats for all players
    return scrapeMultiplePlayerStats(player_ids, season, output_format, show_progress)
