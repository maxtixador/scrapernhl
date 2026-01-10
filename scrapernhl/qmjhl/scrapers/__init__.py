"""
QMJHL Scrapers Package

This package contains scrapers for various QMJHL data sources:
- schedule_new: Season schedules (2 API patterns: statviewfeed and scorebar)
- teams_new: Team information
- standings: League standings (division/conference)
- stats: Player and team statistics
- roster: Team rosters
- games: Play-by-play game data (Playwright-based)
- official_report: Official game reports (static HTML)
- gamecentre: Game centre API data (rosters, stats, goals with +/-)
- player: Player profiles, statistics, and career data
"""

from .schedule import getSchedule, getSeasons
from .schedule_new import (
    getScheduleData,
    getScorebarData,
    scrapeSchedule,
    scrapeScorebar,
)
from .teams import getTeams
from .teams_new import (
    getTeamsData,
    scrapeTeams,
)
from .standings import (
    getStandingsData,
    scrapeStandings,
)
from .stats import (
    getPlayerStatsData,
    scrapePlayerStats,
    getTeamStatsData,
    scrapeTeamStats,
)
from .roster import (
    getRosterData,
    scrapeRoster,
)
from .games import scrape_game
from .official_report import scrape_official_report
from .gamecentre import (
    scrape_gamecentre,
    get_rosters,
    get_player_ids,
    get_goals_with_onice,
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
    # Old schedule (backwards compatibility)
    'getSchedule',
    'getSeasons',
    # New schedule APIs
    'getScheduleData',
    'getScorebarData',
    'scrapeSchedule',
    'scrapeScorebar',
    # Old teams (backwards compatibility)
    'getTeams',
    # New teams
    'getTeamsData',
    'scrapeTeams',
    # Standings
    'getStandingsData',
    'scrapeStandings',
    # Stats
    'getPlayerStatsData',
    'scrapePlayerStats',
    'getTeamStatsData',
    'scrapeTeamStats',
    # Roster
    'getRosterData',
    'scrapeRoster',
    # Games
    'scrape_game',
    # Official reports
    'scrape_official_report',
    # Game centre
    'scrape_gamecentre',
    'get_rosters',
    'get_player_ids',
    'get_goals_with_onice',
    # Player data
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
