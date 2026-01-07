"""NHL data scrapers organized by data type."""

from .teams import getTeamsData, scrapeTeams
from .schedule import getScheduleData, scrapeSchedule
from .standings import getStandingsData, scrapeStandings
from .roster import getRosterData, scrapeRoster
from .stats import getTeamStatsData, scrapeTeamStats
from .draft import (
    getDraftDataData, scrapeDraftData,
    getRecordsDraftData, scrapeDraftRecords,
    getRecordsTeamDraftHistoryData, scrapeTeamDraftHistory
)
from .games import getGameData, scrapePlays, getGoalReplayData
from .players import (
    scrapePlayerProfile,
    scrapePlayerSeasonStats,
    scrapePlayerGameLog,
    scrapeMultiplePlayerStats,
    scrapeTeamRoster,
    scrapeTeamPlayerStats,
)

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
    "getDraftDataData", "scrapeDraftData",
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
