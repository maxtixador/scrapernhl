"""
PWHL Scraper Functions

Wrapper functions that convert PWHL API responses to pandas DataFrames.
These follow the same pattern as the main NHL scrapers for consistency.
"""

from typing import Union, Optional
import pandas as pd
from scrapernhl.pwhl.api import (
    get_teams, get_schedule, get_scorebar, get_standings,
    get_roster, get_skater_stats, get_goalie_stats,
    get_play_by_play, get_game_summary, PWHLConfig
)


def scrapeTeams(season: Union[int, str] = None, config: PWHLConfig = None) -> pd.DataFrame:
    """
    Scrape PWHL teams data as a DataFrame.
    
    Args:
        season: Season ID (uses default if None)
        config: PWHLConfig instance
        
    Returns:
        DataFrame with team information
    """
    data = get_teams(season=season, config=config)
    teams = data.get('teams', [])
    return pd.DataFrame(teams)


def scrapeSchedule(
    team_id: int = -1,
    season: Union[int, str] = None,
    month: int = -1,
    location: str = 'homeaway',
    config: PWHLConfig = None
) -> pd.DataFrame:
    """
    Scrape PWHL schedule as a DataFrame.
    
    Args:
        team_id: Team ID (use -1 for all teams)
        season: Season ID (uses default if None)
        month: Month filter (-1 for all months)
        location: Game location filter ('homeaway', 'home', 'away')
        config: PWHLConfig instance
        
    Returns:
        DataFrame with schedule data
    """
    data = get_schedule(team_id=team_id, season=season, month=month, location=location, config=config)
    games = data.get('SiteKit', {}).get('Gamesbydate', [])
    return pd.DataFrame(games)


def scrapeScorebar(
    days_ahead: int = 6,
    days_back: int = 0,
    season_id: Optional[int] = None,
    config: PWHLConfig = None
) -> pd.DataFrame:
    """
    Scrape PWHL live games and recent results as a DataFrame.
    
    Args:
        days_ahead: Number of days ahead to fetch
        days_back: Number of days back to fetch
        season_id: Season ID (uses default if None)
        config: PWHLConfig instance
        
    Returns:
        DataFrame with scorebar games
    """
    data = get_scorebar(days_ahead=days_ahead, days_back=days_back, season_id=season_id, config=config)
    games = data.get('SiteKit', {}).get('Scorebar', [])
    return pd.DataFrame(games)


def scrapeStandings(
    season: Union[int, str] = None,
    context: str = 'overall',
    group_by: str = 'division',
    config: PWHLConfig = None
) -> pd.DataFrame:
    """
    Scrape PWHL standings as a DataFrame.
    
    Args:
        season: Season ID (uses default if None)
        context: Stats context ('overall', 'home', 'away')
        group_by: How to group teams ('division', 'conference', 'league')
        config: PWHLConfig instance
        
    Returns:
        DataFrame with standings
    """
    data = get_standings(season=season, context=context, group_by=group_by, config=config)
    standings = data.get('SiteKit', {}).get('Standings', [])
    return pd.DataFrame(standings)


def scrapeRoster(
    team_id: int,
    season_id: Union[int, str] = None,
    roster_status: str = 'undefined',
    config: PWHLConfig = None
) -> pd.DataFrame:
    """
    Scrape PWHL team roster as a DataFrame.
    
    Args:
        team_id: Team ID
        season_id: Season ID (uses default if None)
        roster_status: Roster status filter
        config: PWHLConfig instance
        
    Returns:
        DataFrame with roster data
    """
    data = get_roster(team_id=team_id, season_id=season_id, roster_status=roster_status, config=config)
    roster = data.get('roster', [])
    return pd.DataFrame(roster)


def scrapeSkaterStats(
    season: Union[int, str] = None,
    sort: str = 'points',
    team: str = 'all',
    limit: int = 500,
    config: PWHLConfig = None
) -> pd.DataFrame:
    """
    Scrape PWHL skater statistics as a DataFrame.
    
    Args:
        season: Season ID (uses default if None)
        sort: Sort field ('points', 'goals', 'assists', etc.)
        team: Team filter ('all' or team ID)
        limit: Number of results to return
        config: PWHLConfig instance
        
    Returns:
        DataFrame with skater stats
    """
    data = get_skater_stats(season=season, sort=sort, team=team, limit=limit, config=config)
    skaters = data.get('SiteKit', {}).get('PlayerStats', [])
    return pd.DataFrame(skaters)


def scrapeGoalieStats(
    season: Union[int, str] = None,
    sort: str = 'gaa',
    team: str = 'all',
    limit: int = 200,
    config: PWHLConfig = None
) -> pd.DataFrame:
    """
    Scrape PWHL goalie statistics as a DataFrame.
    
    Args:
        season: Season ID (uses default if None)
        sort: Sort field ('gaa', 'savePct', 'wins', etc.)
        team: Team filter ('all' or team ID)
        limit: Number of results to return
        config: PWHLConfig instance
        
    Returns:
        DataFrame with goalie stats
    """
    data = get_goalie_stats(season=season, sort=sort, team=team, limit=limit, config=config)
    goalies = data.get('SiteKit', {}).get('GoalieStats', [])
    return pd.DataFrame(goalies)


def scrapePlayByPlay(game_id: int, config: PWHLConfig = None) -> pd.DataFrame:
    """
    Scrape PWHL play-by-play events as a DataFrame.
    
    Args:
        game_id: Game ID
        config: PWHLConfig instance
        
    Returns:
        DataFrame with play-by-play events
    """
    pbp_data = get_play_by_play(game_id=game_id, config=config)
    return pd.DataFrame(pbp_data)


def scrapeGameSummary(game_id: int, config: PWHLConfig = None) -> dict:
    """
    Scrape PWHL game summary.
    
    Args:
        game_id: Game ID
        config: PWHLConfig instance
        
    Returns:
        Dictionary with game summary data (contains multiple DataFrames)
    """
    return get_game_summary(game_id=game_id, config=config)
