"""
NHL Scraper - Modularized Entry Point

This file re-exports all public functions from the modularized codebase
to maintain backward compatibility with existing code.

For new code, prefer importing directly from submodules:
    from scrapernhl.nhl.scrapers.teams import scrapeTeams
    from scrapernhl.nhl.analytics import calculate_corsi
"""

# Re-export scraper functions for backward compatibility
from scrapernhl.nhl.scrapers.teams import getTeamsData, scrapeTeams
from scrapernhl.nhl.scrapers.schedule import getScheduleData, scrapeSchedule
from scrapernhl.nhl.scrapers.standings import getStandingsData, scrapeStandings
from scrapernhl.nhl.scrapers.roster import getRosterData, scrapeRoster
from scrapernhl.nhl.scrapers.stats import getTeamStatsData, scrapeTeamStats
from scrapernhl.nhl.scrapers.draft import (
    getDraftDataData,
    scrapeDraftData,
    getRecordsDraftData,
    scrapeDraftRecords,
    getRecordsTeamDraftHistoryData,
    scrapeTeamDraftHistory,
)
from scrapernhl.nhl.scrapers.games import (
    getGameData,
    scrapePlays,
    getGoalReplayData,
    convert_json_to_goal_url,
)

# Re-export HTTP and utility functions
from scrapernhl.core.http import fetch_json, fetch_html, fetch_html_async, fetch_json_async
from scrapernhl.core.utils import time_str_to_seconds, json_normalize, _dedup_cols, _group_merge_index


# Re-export from config
from scrapernhl.config import (
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
    DEFAULT_TEAM,
    DEFAULT_SEASON,
    DEFAULT_DATE,
)

# Legacy functions - imported lazily to avoid heavy dependencies
# These will be gradually migrated to proper modules
def __getattr__(name):
    """Lazy import of legacy functions to avoid loading heavy dependencies."""
    legacy_functions = {
        'scrapeHtmlPbp', 'scrapeHtmlPbp_async', 'scrapeHTMLShifts', 'scrapeHTMLShifts_async',
        'scrape_html_pbp', 'scrape_shifts', 'scrape_shifts_async', 'scrape_game', 'scrape_game_async',
        'parse_html_pbp', 'parse_html_shifts', 'parse_html_rosters',
        'build_shifts_events', 'add_strengths_to_shifts_events', 'build_strength_segments_from_shifts',
        'strengths_by_second_from_segments', 'build_on_ice_long', 'build_on_ice_wide',
        'seconds_matrix', 'strengths_by_second', 'toi_by_strength_all',
        'shared_toi_teammates_by_strength', 'shared_toi_opponents_by_strength',
        'combos_teammates_by_strength', 'combos_opponents_by_strength', 'combo_toi_by_strength',
        'combo_shot_metrics_by_strength', 'engineer_xg_features', 'build_shots_design_matrix',
        'predict_xg_for_pbp', 'pipeline', 'toi_by_strength', 'toi_by_player_and_strength',
        'on_ice_stats_by_player_strength', 'combo_on_ice_stats', 'combo_on_ice_stats_both_teams',
        'team_strength_aggregates', '_add_normalized_coordinates',
        'EVENT_MAPPING', 'MODEL_PATH', 'FEAT_PATH', 'BASE_NUM', 'BASE_BOOL', 'CAT_COLS', 'EVENTS_FOR_XG',
    }
    
    if name in legacy_functions:
        from scrapernhl.nhl import scraper_legacy
        return getattr(scraper_legacy, name)
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Teams
    "getTeamsData",
    "scrapeTeams",
    # Schedule
    "getScheduleData",
    "scrapeSchedule",
    # Standings
    "getStandingsData",
    "scrapeStandings",
    # Roster
    "getRosterData",
    "scrapeRoster",
    # Stats
    "getTeamStatsData",
    "scrapeTeamStats",
    # Draft
    "getDraftDataData",
    "scrapeDraftData",
    "getRecordsDraftData",
    "scrapeDraftRecords",
    "getRecordsTeamDraftHistoryData",
    "scrapeTeamDraftHistory",
    # Games
    "getGameData",
    "scrapePlays",
    "getGoalReplayData",
    "convert_json_to_goal_url",
    # HTTP & Utils
    "fetch_json",
    "fetch_html",
    "fetch_html_async",
    "fetch_json_async",
    "time_str_to_seconds",
    "json_normalize",
    "_dedup_cols",
    "_group_merge_index",
    # Config
    "DEFAULT_HEADERS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_TEAM",
    "DEFAULT_SEASON",
    "DEFAULT_DATE",
    # Legacy/Advanced functions (lazy-loaded)
    "scrapeHtmlPbp",
    "scrapeHtmlPbp_async",
    "scrapeHTMLShifts",
    "scrapeHTMLShifts_async",
    "scrape_html_pbp",
    "scrape_shifts",
    "scrape_shifts_async",
    "scrape_game",
    "scrape_game_async",
    "parse_html_pbp",
    "parse_html_shifts",
    "parse_html_rosters",
    "build_shifts_events",
    "add_strengths_to_shifts_events",
    "build_strength_segments_from_shifts",
    "strengths_by_second_from_segments",
    "build_on_ice_long",
    "build_on_ice_wide",
    "seconds_matrix",
    "strengths_by_second",
    "toi_by_strength_all",
    "shared_toi_teammates_by_strength",
    "shared_toi_opponents_by_strength",
    "combos_teammates_by_strength",
    "combos_opponents_by_strength",
    "combo_toi_by_strength",
    "combo_shot_metrics_by_strength",
    "engineer_xg_features",
    "build_shots_design_matrix",
    "predict_xg_for_pbp",
    "pipeline",
    "toi_by_strength",
    "toi_by_player_and_strength",
    "on_ice_stats_by_player_strength",
    "combo_on_ice_stats",
    "combo_on_ice_stats_both_teams",
    "team_strength_aggregates",
    "_add_normalized_coordinates",
    "EVENT_MAPPING",
    "MODEL_PATH",
    "FEAT_PATH",
    "BASE_NUM",
    "BASE_BOOL",
    "CAT_COLS",
    "EVENTS_FOR_XG",
]
