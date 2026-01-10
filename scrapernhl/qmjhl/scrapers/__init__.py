"""
QMJHL Scrapers Package

This package contains scrapers for various QMJHL data sources:
- schedule: Season schedules and game listings
- teams: Team information
- games: Play-by-play game data (Playwright-based)
- official_report: Official game reports (static HTML)
- gamecentre: Game centre API data (rosters, stats, goals with +/-)
"""

from .schedule import getSchedule, getSeasons
from .teams import getTeams
from .games import scrape_game
from .official_report import scrape_official_report
from .gamecentre import (
    scrape_gamecentre,
    get_rosters,
    get_player_ids,
    get_goals_with_onice,
)

__all__ = [
    # Schedule
    'getSchedule',
    'getSeasons',
    # Teams
    'getTeams',
    # Games
    'scrape_game',
    # Official reports
    'scrape_official_report',
    # Game centre
    'scrape_gamecentre',
    'get_rosters',
    'get_player_ids',
    'get_goals_with_onice',
]
