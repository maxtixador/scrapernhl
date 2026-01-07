"""NHL-specific scraping functionality"""

# Import main scraper functions
from .scraper import *

# Import NHL-specific scrapers
from .scrapers.players import (
    scrapePlayerProfile,
    scrapePlayerSeasonStats,
    scrapePlayerGameLog,
    scrapeMultiplePlayerStats,
    scrapeTeamRoster,
    scrapeTeamPlayerStats,
)

# Import NHL analytics
from .analytics import (
    calculate_shot_distance,
    calculate_shot_angle,
    identify_scoring_chances,
    calculate_corsi,
    calculate_fenwick,
    calculate_player_toi,
    calculate_zone_start_percentage,
    calculate_team_stats_summary,
    calculate_player_stats_summary,
    calculate_score_effects,
    analyze_shooting_patterns,
    create_analytics_report,
)

__all__ = [
    # Player Scrapers
    'scrapePlayerProfile',
    'scrapePlayerSeasonStats',
    'scrapePlayerGameLog',
    'scrapeMultiplePlayerStats',
    'scrapeTeamRoster',
    'scrapeTeamPlayerStats',
    # Analytics
    'calculate_shot_distance',
    'calculate_shot_angle',
    'identify_scoring_chances',
    'calculate_corsi',
    'calculate_fenwick',
    'calculate_player_toi',
    'calculate_zone_start_percentage',
    'calculate_team_stats_summary',
    'calculate_player_stats_summary',
    'calculate_score_effects',
    'analyze_shooting_patterns',
    'create_analytics_report',
]
