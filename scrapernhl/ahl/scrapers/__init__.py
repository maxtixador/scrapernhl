"""AHL scrapers module"""
from .games import scrape_game, getAPIEvents
from .complete_suite import (
    getScheduleData, scrapeSchedule,
    getTeamsData, scrapeTeams,
    getStandingsData, scrapeStandings,
    getPlayerStatsData, scrapePlayerStats,
    getRosterData, scrapeRoster
)
from .player import (
    get_player_profile,
    get_player_bio,
    get_player_stats,
    get_player_game_log,
    get_player_shot_locations,
    get_player_draft_info,
    scrape_player_profile,
    scrape_player_stats,
    scrape_player_career_stats,
    scrape_player_game_log,
    scrape_player_shot_locations,
    scrape_multiple_players
)

__all__ = [
    # Game scrapers
    'scrape_game',
    'getAPIEvents',
    # Schedule, teams, standings, stats, roster
    'getScheduleData',
    'scrapeSchedule',
    'getTeamsData',
    'scrapeTeams',
    'getStandingsData',
    'scrapeStandings',
    'getPlayerStatsData',
    'scrapePlayerStats',
    'getRosterData',
    'scrapeRoster',
    # Player data fetchers
    'get_player_profile',
    'get_player_bio',
    'get_player_stats',
    'get_player_game_log',
    'get_player_shot_locations',
    'get_player_draft_info',
    # Player DataFrame scrapers
    'scrape_player_profile',
    'scrape_player_stats',
    'scrape_player_career_stats',
    'scrape_player_game_log',
    'scrape_player_shot_locations',
    'scrape_multiple_players'
]
