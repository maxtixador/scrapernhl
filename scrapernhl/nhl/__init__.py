"""NHL-specific scraping functionality"""

# Import main scraper functions
# Import NHL analytics
from .analytics import (
    analyze_shooting_patterns,
    calculate_corsi,
    calculate_fenwick,
    calculate_player_stats_summary,
    calculate_player_toi,
    calculate_score_effects,
    calculate_shot_angle,
    calculate_shot_distance,
    calculate_team_stats_summary,
    calculate_zone_start_percentage,
    create_analytics_report,
    identify_scoring_chances,
)
from .scraper import *

# Import NHL-specific scrapers
from .scrapers.players import (
    scrapeMultiplePlayerStats,
    scrapePlayerGameLog,
    scrapePlayerProfile,
    scrapePlayerSeasonStats,
    scrapeTeamPlayerStats,
    scrapeTeamRoster,
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
