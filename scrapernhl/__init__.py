"""NHL data scraping package"""

__version__ = "0.1.4"

# Import main scraper functions for easy access (from NHL module)
from .nhl.scraper import *

# Create properly-named alias for main game scraping function
from .nhl.scraper import scrape_game
scrapeGame = scrape_game  # Follows naming convention: scrapeTeams, scrapeSchedule, etc.

# Import exceptions for user convenience
from .exceptions import (
    ScraperNHLError,
    APIError,
    InvalidGameError,
    InvalidTeamError,
    InvalidSeasonError,
    DataValidationError,
    CacheError,
    ParsingError,
    RateLimitError,
)

# Import core utilities
from .core.schema import standardize_columns, validate_data_quality
from .core.logging_config import setup_logging
from .core.progress import console, create_progress_bar, create_table
from .core.cache import Cache, get_cache, cached
from .core.batch import BatchScraper, BatchResult, scrape_season_games, scrape_date_range

# Import player scrapers (from NHL module)
from .nhl.scrapers.players import (
    scrapePlayerProfile,
    scrapePlayerSeasonStats,
    scrapePlayerGameLog,
    scrapeMultiplePlayerStats,
    scrapeTeamRoster,
    scrapeTeamPlayerStats,
)

# Import analytics (from NHL module)
from .nhl.analytics import (
    calculate_shot_distance,
    calculate_shot_angle,
    identify_scoring_chances,
    prepare_pbp_with_xg,
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

# Import xG functions from scraper_legacy
from .nhl.scraper_legacy import (
    engineer_xg_features,
    predict_xg_for_pbp,
)

# Import visualization (generic, not league-specific)
from .visualization import (
    display_team_stats,
    display_advanced_stats,
    display_player_summary,
    display_scoring_chances,
    display_shooting_patterns,
    display_score_effects,
    display_game_summary,
    display_top_players,
    print_analytics_summary,
)

__all__ = [
    'scraper',
    # Main game scraping function
    'scrapeGame',
    'scrape_game',  # Backward compatibility
    # Exceptions
    'ScraperNHLError',
    'APIError',
    'InvalidGameError',
    'InvalidTeamError',
    'InvalidSeasonError',
    'DataValidationError',
    'CacheError',
    'ParsingError',
    'RateLimitError',
    # Utilities
    'standardize_columns',
    'validate_data_quality',
    'setup_logging',
    # Progress & Output
    'console',
    'create_progress_bar',
    'create_table',
    # Caching
    'Cache',
    'get_cache',
    'cached',
    # Batch Processing
    'BatchScraper',
    'BatchResult',
    'scrape_season_games',
    'scrape_date_range',
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
    'prepare_pbp_with_xg',
    'engineer_xg_features',
    'predict_xg_for_pbp',
    'calculate_corsi',
    'calculate_fenwick',
    'calculate_player_toi',
    'calculate_zone_start_percentage',
    'calculate_team_stats_summary',
    'calculate_player_stats_summary',
    'calculate_score_effects',
    'analyze_shooting_patterns',
    'create_analytics_report',
    # Visualization
    'display_team_stats',
    'display_advanced_stats',
    'display_player_summary',
    'display_scoring_chances',
    'display_shooting_patterns',
    'display_score_effects',
    'display_game_summary',
    'display_top_players',
    'print_analytics_summary',
]
