"""PWHL scrapers module"""
from .games import scrape_game, getAPIEvents
from .schedule import getScheduleData, scrapeSchedule
from .teams_stats_roster import (
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
    scrape_player_profile,
    scrape_player_stats,
    scrape_player_career_stats,
    scrape_player_game_log,
    scrape_player_shot_locations,
    scrape_multiple_players,
)

__all__ = [
    'scrape_game',
    'getAPIEvents',
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
    'scrape_multiple_players',
]
