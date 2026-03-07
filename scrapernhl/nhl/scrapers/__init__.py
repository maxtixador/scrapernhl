"""NHL data scrapers organized by data type."""

from .draft import (
    getDraftData,
    getRecordsDraftData,
    getRecordsTeamDraftHistoryData,
    scrapeDraftData,
    scrapeDraftRecords,
    scrapeTeamDraftHistory,
)
from .games import getGameData, getGoalReplayData, scrapePlays
from .players import (
    scrapeMultiplePlayerStats,
    scrapePlayerGameLog,
    scrapePlayerProfile,
    scrapePlayerSeasonStats,
    scrapeTeamPlayerStats,
    scrapeTeamRoster,
)
from .roster import getRosterData, scrapeRoster
from .schedule import getScheduleData, scrapeSchedule
from .standings import getStandingsData, scrapeStandings
from .stats import getTeamStatsData, scrapeTeamStats
from .teams import getTeamsData, scrapeTeams

__all__ = [
    # Teams
    "getTeamsData", "scrapeTeams",
    # Schedule
    "getScheduleData", "scrapeSchedule",
    # Standings
    "getStandingsData", "scrapeStandings",
    # Roster
    "getRosterData", "scrapeRoster",
    # Stats
    "getTeamStatsData", "scrapeTeamStats",
    # Draft
    "getDraftData", "scrapeDraftData",
    "getRecordsDraftData", "scrapeDraftRecords",
    "getRecordsTeamDraftHistoryData", "scrapeTeamDraftHistory",
    # Games & Plays
    "getGameData", "scrapePlays", "getGoalReplayData",
    # Players
    "scrapePlayerProfile",
    "scrapePlayerSeasonStats",
    "scrapePlayerGameLog",
    "scrapeMultiplePlayerStats",
    "scrapeTeamRoster",
    "scrapeTeamPlayerStats",
]
