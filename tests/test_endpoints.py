"""
Integration tests for raw API endpoints.

Tests make direct HTTP requests — NOT through HockeyScraper — verifying:
  - Each endpoint returns HTTP 200
  - The response body is valid JSON (JSONP-cleaned for HockeyTech)
  - The top-level structure has expected keys
  - Data lists are non-empty for known-complete games / seasons

Run with: pytest tests/test_endpoints.py -v
Requires a network connection. All APIs are public read-only endpoints.
"""

import json
import pytest
import requests

from scrapernhl.config import LEAGUES
from scrapernhl.utils import clean_jsonp
from scrapernhl.urls import (
    build_bootstrap_url,
    build_pbp_url,
    build_stats_url,
    build_schedule_url,
    build_roster_url,
    build_standings_url,
    build_nhl_seasons_url,
    build_nhl_schedule_calendar_url,
    build_nhl_franchise_url,
    build_nhl_records_franchise_url,
    build_nhl_draft_picks_url,
    build_nhl_records_draft_url,
    build_nhl_records_team_draft_history_url,
    build_nhl_html_pbp_url,
    build_nhl_html_shifts_home_url,
    build_nhl_html_shifts_visitor_url,
)

# ---------------------------------------------------------------------------
# Known-good completed game IDs and season IDs
# ---------------------------------------------------------------------------
NHL_GAME_ID  = 2023020001   # 2023-24 regular season
AHL_GAME_ID  = 1027781      # 2025-26 season
PWHL_GAME_ID = 210          # 2023-24 season
OHL_GAME_ID  = 28150        # 2024-25 season
WHL_GAME_ID  = 1022126      # 2024-25 season
QMJHL_GAME_ID = 31909       # 2025-26 season

SEASONS = {
    "ahl":   90,
    "pwhl":  8,
    "ohl":   83,
    "whl":   289,
    "qmjhl": 211,
}

TIMEOUT = 30  # seconds per request


# ---------------------------------------------------------------------------
# Session fixture — one requests.Session shared for the entire test run
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def http():
    session = requests.Session()
    session.headers.update({"User-Agent": "scrapernhl-endpoint-tests/1.0"})
    yield session
    session.close()


# ---------------------------------------------------------------------------
# Helper: fetch a HockeyTech URL (JSONP → JSON)
# ---------------------------------------------------------------------------

def ht_get(session: requests.Session, url: str) -> dict | list:
    """GET a HockeyTech endpoint and return parsed JSON (strips JSONP wrapper)."""
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return json.loads(clean_jsonp(resp.text))


# ---------------------------------------------------------------------------
# Shared fixture: first real team ID per non-NHL league (from bootstrap)
# Used by roster tests so they don't need hard-coded team IDs.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def team_ids(http):
    """
    Return {league: team_id_str} by fetching each league's bootstrap once.
    Falls back to None if the bootstrap doesn't yield a usable team.
    """
    ids: dict[str, str | None] = {}
    for league in ["ahl", "pwhl", "ohl", "whl", "qmjhl"]:
        cfg = LEAGUES[league]
        url = build_bootstrap_url(cfg, game_id=None, season="latest", page_name="scorebar")
        try:
            data = ht_get(http, url)
            # Bootstrap structure varies: try common locations
            teams = (
                data.get("teams")
                or data.get("SiteKit", {}).get("teams")
                or []
            )
            # Filter out the "All Teams" sentinel (id -1, 0, or "all")
            real = [
                t for t in teams
                if str(t.get("id", t.get("team_id", -1))) not in ("-1", "0", "all")
            ]
            if real:
                raw_id = real[0].get("id", real[0].get("team_id"))
                ids[league] = str(raw_id)
            else:
                ids[league] = None
        except Exception:
            ids[league] = None
    return ids


# ===========================================================================
# NHL — Play-by-Play (api-web.nhle.com)
# ===========================================================================

class TestNHLPlayByPlay:

    def _url(self):
        return f"https://api-web.nhle.com/v1/gamecenter/{NHL_GAME_ID}/play-by-play"

    def test_status_200(self, http):
        assert http.get(self._url(), timeout=TIMEOUT).status_code == 200

    def test_has_plays_key(self, http):
        data = http.get(self._url(), timeout=TIMEOUT).json()
        assert "plays" in data, "'plays' key missing from NHL PBP response"

    def test_plays_list_non_empty(self, http):
        plays = http.get(self._url(), timeout=TIMEOUT).json()["plays"]
        assert isinstance(plays, list) and len(plays) > 0

    def test_has_home_and_away_team(self, http):
        data = http.get(self._url(), timeout=TIMEOUT).json()
        assert "homeTeam" in data and "awayTeam" in data

    def test_plays_have_type_and_period(self, http):
        plays = http.get(self._url(), timeout=TIMEOUT).json()["plays"]
        sample = plays[:20]
        assert all("typeDescKey" in p for p in sample), "Some plays missing 'typeDescKey'"
        assert all("periodDescriptor" in p for p in sample), "Some plays missing 'periodDescriptor'"

    def test_period_values_are_valid(self, http):
        plays = http.get(self._url(), timeout=TIMEOUT).json()["plays"]
        periods = {p["periodDescriptor"]["number"] for p in plays if "periodDescriptor" in p}
        # Regular game: periods 1, 2, 3 (possibly OT)
        assert periods >= {1, 2, 3}, f"Expected periods 1-3, got {periods}"


# ===========================================================================
# NHL — Schedule (api-web.nhle.com)
# ===========================================================================

class TestNHLSchedule:

    def test_status_200(self, http):
        url = "https://api-web.nhle.com/v1/club-schedule-season/MTL/20232024"
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_games_key_present(self, http):
        data = http.get("https://api-web.nhle.com/v1/club-schedule-season/MTL/20232024", timeout=TIMEOUT).json()
        assert "games" in data

    def test_full_season_has_82_games(self, http):
        # NHL regular season = 82 games
        games = http.get("https://api-web.nhle.com/v1/club-schedule-season/MTL/20232024", timeout=TIMEOUT).json()["games"]
        assert len(games) >= 82

    def test_games_have_date_field(self, http):
        games = http.get("https://api-web.nhle.com/v1/club-schedule-season/TOR/20232024", timeout=TIMEOUT).json()["games"]
        game = games[0]
        assert "gameDate" in game or "startTimeUTC" in game

    def test_games_have_home_and_away_team(self, http):
        games = http.get("https://api-web.nhle.com/v1/club-schedule-season/TOR/20232024", timeout=TIMEOUT).json()["games"]
        game = games[0]
        assert "homeTeam" in game and "awayTeam" in game


# ===========================================================================
# NHL — Standings (api-web.nhle.com)
# ===========================================================================

class TestNHLStandings:

    _URL = "https://api-web.nhle.com/v1/standings/2024-01-15"

    def test_status_200(self, http):
        assert http.get(self._URL, timeout=TIMEOUT).status_code == 200

    def test_standings_key_present(self, http):
        data = http.get(self._URL, timeout=TIMEOUT).json()
        assert "standings" in data

    def test_all_32_teams_present(self, http):
        standings = http.get(self._URL, timeout=TIMEOUT).json()["standings"]
        assert len(standings) == 32, f"Expected 32 teams, got {len(standings)}"

    def test_teams_have_points(self, http):
        team = http.get(self._URL, timeout=TIMEOUT).json()["standings"][0]
        assert "points" in team, "Team entry missing 'points'"

    def test_teams_have_wins_losses(self, http):
        team = http.get(self._URL, timeout=TIMEOUT).json()["standings"][0]
        assert "wins" in team and "losses" in team

    def test_team_name_is_string(self, http):
        team = http.get(self._URL, timeout=TIMEOUT).json()["standings"][0]
        name = team.get("teamName", team.get("teamAbbrev", {}))
        # teamName is a localized dict like {"default": "Canadiens"}
        assert name, "Team name is empty"


# ===========================================================================
# NHL — Roster (api-web.nhle.com)
# ===========================================================================

class TestNHLRoster:

    _URL = "https://api-web.nhle.com/v1/roster/MTL/20232024"

    def test_status_200(self, http):
        assert http.get(self._URL, timeout=TIMEOUT).status_code == 200

    def test_has_forwards_defensemen_goalies(self, http):
        data = http.get(self._URL, timeout=TIMEOUT).json()
        assert "forwards" in data and "defensemen" in data and "goalies" in data

    def test_roster_at_least_20_players(self, http):
        data = http.get(self._URL, timeout=TIMEOUT).json()
        total = len(data["forwards"]) + len(data["defensemen"]) + len(data["goalies"])
        assert total >= 20

    def test_players_have_name(self, http):
        player = http.get(self._URL, timeout=TIMEOUT).json()["forwards"][0]
        assert "firstName" in player or "lastName" in player

    def test_players_have_jersey_number(self, http):
        player = http.get(self._URL, timeout=TIMEOUT).json()["forwards"][0]
        assert "sweaterNumber" in player or "jerseyNumber" in player


# ===========================================================================
# NHL — Club Stats (api-web.nhle.com)
# ===========================================================================

class TestNHLClubStats:

    _URL = "https://api-web.nhle.com/v1/club-stats/MTL/20232024/2"

    def test_status_200(self, http):
        assert http.get(self._URL, timeout=TIMEOUT).status_code == 200

    def test_has_skaters_and_goalies(self, http):
        data = http.get(self._URL, timeout=TIMEOUT).json()
        assert "skaters" in data and "goalies" in data

    def test_skaters_non_empty(self, http):
        skaters = http.get(self._URL, timeout=TIMEOUT).json()["skaters"]
        assert len(skaters) > 0

    def test_goalies_non_empty(self, http):
        goalies = http.get(self._URL, timeout=TIMEOUT).json()["goalies"]
        assert len(goalies) > 0

    def test_skater_has_goals_assists_points(self, http):
        skater = http.get(self._URL, timeout=TIMEOUT).json()["skaters"][0]
        assert "goals" in skater and "assists" in skater and "points" in skater

    def test_goalie_has_save_pct(self, http):
        goalie = http.get(self._URL, timeout=TIMEOUT).json()["goalies"][0]
        assert "savePctg" in goalie or "savePercentage" in goalie or "svp" in str(goalie).lower()

    def test_playoffs_session_3_works(self, http):
        # Verify session=3 (playoffs) endpoint is also valid
        url = "https://api-web.nhle.com/v1/club-stats/MTL/20232024/3"
        resp = http.get(url, timeout=TIMEOUT)
        assert resp.status_code == 200
        data = resp.json()
        assert "skaters" in data or "goalies" in data


# ===========================================================================
# NHL — Seasons REST API (api.nhle.com)
# ===========================================================================

class TestNHLSeasons:

    _URL = "https://api.nhle.com/stats/rest/en/season"

    def test_status_200(self, http):
        assert http.get(self._URL, timeout=TIMEOUT).status_code == 200

    def test_data_list_non_empty(self, http):
        data = http.get(self._URL, timeout=TIMEOUT).json()
        assert "data" in data and len(data["data"]) > 0

    def test_seasons_have_id(self, http):
        season = http.get(self._URL, timeout=TIMEOUT).json()["data"][0]
        assert "id" in season

    def test_season_id_format(self, http):
        # NHL season IDs are 8-digit YYYYYYYY e.g. 20232024
        seasons = http.get(self._URL, timeout=TIMEOUT).json()["data"]
        recent = [s for s in seasons if s.get("id", 0) >= 20200000]
        assert len(recent) > 0, "No post-2020 seasons found"

    def test_total_matches_data_length(self, http):
        resp = http.get(self._URL, timeout=TIMEOUT).json()
        if "total" in resp:
            assert resp["total"] == len(resp["data"])


# ===========================================================================
# NHL — Schedule Calendar (active teams)
# ===========================================================================

class TestNHLScheduleCalendar:

    _URL = "https://api-web.nhle.com/v1/schedule-calendar/now"

    def test_status_200(self, http):
        assert http.get(self._URL, timeout=TIMEOUT).status_code == 200

    def test_response_is_dict(self, http):
        assert isinstance(http.get(self._URL, timeout=TIMEOUT).json(), dict)

    def test_contains_team_or_game_data(self, http):
        data = http.get(self._URL, timeout=TIMEOUT).json()
        # The calendar endpoint nests data — at least one of these keys should be present
        known_keys = {"teams", "games", "gameWeek", "today", "currentSeason"}
        assert known_keys & set(data.keys()), f"Unexpected calendar keys: {list(data.keys())}"


# ===========================================================================
# NHL — Franchise list (api.nhle.com/stats/rest)
# ===========================================================================

class TestNHLFranchise:

    def test_status_200(self, http):
        assert http.get(build_nhl_franchise_url(), timeout=TIMEOUT).status_code == 200

    def test_data_non_empty(self, http):
        data = http.get(build_nhl_franchise_url(), timeout=TIMEOUT).json()
        assert "data" in data and len(data["data"]) > 0

    def test_franchises_have_full_name(self, http):
        franchise = http.get(build_nhl_franchise_url(), timeout=TIMEOUT).json()["data"][0]
        assert "fullName" in franchise

    def test_franchises_have_first_last_season(self, http):
        franchise = http.get(build_nhl_franchise_url(), timeout=TIMEOUT).json()["data"][0]
        assert "firstSeason" in franchise or "lastSeason" in franchise


# ===========================================================================
# NHL — Records franchise (records.nhl.com)
# ===========================================================================

class TestNHLRecordsFranchise:

    def test_status_200(self, http):
        assert http.get(build_nhl_records_franchise_url(), timeout=TIMEOUT).status_code == 200

    def test_data_non_empty(self, http):
        data = http.get(build_nhl_records_franchise_url(), timeout=TIMEOUT).json()
        assert "data" in data and len(data["data"]) > 0

    def test_franchise_has_teams_array(self, http):
        franchise = http.get(build_nhl_records_franchise_url(), timeout=TIMEOUT).json()["data"][0]
        assert "teams" in franchise

    def test_team_has_tricode(self, http):
        franchise = http.get(build_nhl_records_franchise_url(), timeout=TIMEOUT).json()["data"][0]
        team = franchise["teams"][0]
        assert "triCode" in team or "abbrev" in team


# ===========================================================================
# NHL — Draft picks (api-web.nhle.com)
# ===========================================================================

class TestNHLDraftPicks:

    def test_all_rounds_status_200(self, http):
        url = build_nhl_draft_picks_url(2024, "all")
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_round_1_status_200(self, http):
        url = build_nhl_draft_picks_url(2023, 1)
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_all_rounds_non_empty(self, http):
        data = http.get(build_nhl_draft_picks_url(2024, "all"), timeout=TIMEOUT).json()
        picks = data.get("picks", data.get("data", data))
        assert len(picks) > 0

    def test_round_1_has_at_least_32_picks(self, http):
        data = http.get(build_nhl_draft_picks_url(2023, 1), timeout=TIMEOUT).json()
        picks = data.get("picks", data.get("data", []))
        assert len(picks) >= 32

    def test_picks_have_player_info(self, http):
        data = http.get(build_nhl_draft_picks_url(2024, 1), timeout=TIMEOUT).json()
        picks = data.get("picks", data.get("data", []))
        if picks:
            pick = picks[0]
            text = str(pick).lower()
            assert "name" in text or "player" in text or "first" in text


# ===========================================================================
# NHL — Draft records (records.nhl.com)
# ===========================================================================

class TestNHLDraftRecords:

    def test_status_200(self, http):
        assert http.get(build_nhl_records_draft_url(2024), timeout=TIMEOUT).status_code == 200

    def test_data_non_empty(self, http):
        data = http.get(build_nhl_records_draft_url(2024), timeout=TIMEOUT).json()
        assert "data" in data and len(data["data"]) > 0

    def test_picks_have_player(self, http):
        picks = http.get(build_nhl_records_draft_url(2023), timeout=TIMEOUT).json()["data"]
        pick = picks[0]
        assert "player" in pick or "draftProspect" in pick

    def test_total_picks_matches_count(self, http):
        resp = http.get(build_nhl_records_draft_url(2024), timeout=TIMEOUT).json()
        if "total" in resp:
            assert resp["total"] == len(resp["data"])


# ===========================================================================
# NHL — Team draft history (records.nhl.com)
# ===========================================================================

class TestNHLTeamDraftHistory:

    def test_status_200(self, http):
        # Franchise 1 = Montréal Canadiens
        assert http.get(build_nhl_records_team_draft_history_url(1), timeout=TIMEOUT).status_code == 200

    def test_data_non_empty(self, http):
        data = http.get(build_nhl_records_team_draft_history_url(1), timeout=TIMEOUT).json()
        assert "data" in data and len(data["data"]) > 0

    def test_all_picks_belong_to_franchise(self, http):
        picks = http.get(build_nhl_records_team_draft_history_url(1), timeout=TIMEOUT).json()["data"]
        # Every pick should have a franchiseTeam reference
        assert all("franchiseTeam" in p for p in picks[:10])


# ===========================================================================
# NHL — HTML Reports (www.nhl.com/scores/htmlreports)
# ===========================================================================

class TestNHLHTMLReports:

    def test_pbp_status_200(self, http):
        url = build_nhl_html_pbp_url(str(NHL_GAME_ID))
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_pbp_is_html(self, http):
        resp = http.get(build_nhl_html_pbp_url(str(NHL_GAME_ID)), timeout=TIMEOUT)
        ct = resp.headers.get("Content-Type", "")
        assert "html" in ct.lower() or resp.text.lstrip().startswith("<")

    def test_pbp_contains_play_data(self, http):
        html = http.get(build_nhl_html_pbp_url(str(NHL_GAME_ID)), timeout=TIMEOUT).text
        assert "Play-by-Play" in html or "PLAY BY PLAY" in html.upper()

    def test_shifts_home_status_200(self, http):
        url = build_nhl_html_shifts_home_url(str(NHL_GAME_ID))
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_shifts_home_contains_shift_data(self, http):
        html = http.get(build_nhl_html_shifts_home_url(str(NHL_GAME_ID)), timeout=TIMEOUT).text
        assert "Shift" in html or "shift" in html.lower()

    def test_shifts_visitor_status_200(self, http):
        url = build_nhl_html_shifts_visitor_url(str(NHL_GAME_ID))
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_shifts_visitor_contains_shift_data(self, http):
        html = http.get(build_nhl_html_shifts_visitor_url(str(NHL_GAME_ID)), timeout=TIMEOUT).text
        assert "Shift" in html or "shift" in html.lower()


# ===========================================================================
# HockeyTech — Bootstrap (all non-NHL leagues)
# ===========================================================================

@pytest.mark.parametrize("league", ["ahl", "pwhl", "ohl", "whl", "qmjhl"])
class TestHockeyTechBootstrap:

    def test_status_200(self, http, league):
        cfg = LEAGUES[league]
        url = build_bootstrap_url(cfg, game_id=None, season="latest", page_name="scorebar")
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league):
        cfg = LEAGUES[league]
        url = build_bootstrap_url(cfg, game_id=None, season="latest", page_name="scorebar")
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_contains_team_list(self, http, league):
        cfg = LEAGUES[league]
        url = build_bootstrap_url(cfg, game_id=None, season="latest", page_name="scorebar")
        data = ht_get(http, url)
        teams = (
            data.get("teams")
            or data.get("SiteKit", {}).get("teams")
            or []
        )
        assert len(teams) > 0, f"No teams in {league} bootstrap"

    def test_contains_season_info(self, http, league):
        cfg = LEAGUES[league]
        url = build_bootstrap_url(cfg, game_id=None, season="latest", page_name="scorebar")
        data = ht_get(http, url)
        text = str(data)
        assert "season" in text.lower(), f"No season data in {league} bootstrap"

    def test_specific_season_works(self, http, league):
        cfg = LEAGUES[league]
        season = SEASONS[league]
        url = build_bootstrap_url(cfg, game_id=None, season=str(season), page_name="scorebar")
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))


# ===========================================================================
# HockeyTech — Play-by-Play style A: AHL, PWHL
# (feed=statviewfeed&view=gameCenterPlayByPlay)
# ===========================================================================

@pytest.mark.parametrize("league,game_id", [
    ("ahl",  AHL_GAME_ID),
    ("pwhl", PWHL_GAME_ID),
])
class TestPBPStyleA:

    def test_status_200(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_returns_list_of_plays(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        data = ht_get(http, url)
        # hockeytech_a: response is a list of play dicts
        assert isinstance(data, list), f"{league} PBP should be a list"
        assert len(data) > 0, f"{league} PBP list is empty"

    def test_plays_have_event_type(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        plays = ht_get(http, url)
        sample = plays[:10]
        # Each play should have some event identifier
        assert all(
            "event" in str(p).lower() or "type" in str(p).lower()
            for p in sample
        ), f"Some {league} plays missing event/type field"


# ===========================================================================
# HockeyTech — Play-by-Play style B: OHL, WHL, QMJHL
# (feed=gc&tab=pxpverbose)
# ===========================================================================

@pytest.mark.parametrize("league,game_id", [
    ("ohl",   OHL_GAME_ID),
    ("whl",   WHL_GAME_ID),
    ("qmjhl", QMJHL_GAME_ID),
])
class TestPBPStyleB:

    def test_status_200(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_gc_pxpverbose_structure(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        data = ht_get(http, url)
        assert isinstance(data, dict), f"{league} PBP root should be a dict"
        assert "GC" in data, f"Missing 'GC' key in {league} PBP"
        assert "Pxpverbose" in data["GC"], f"Missing 'GC.Pxpverbose' in {league} PBP"

    def test_plays_non_empty(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        plays = ht_get(http, url)["GC"]["Pxpverbose"]
        assert isinstance(plays, list) and len(plays) > 0

    def test_plays_have_period(self, http, league, game_id):
        cfg = LEAGUES[league]
        url = build_pbp_url(league, cfg, game_id)
        plays = ht_get(http, url)["GC"]["Pxpverbose"]
        sample = plays[:10]
        assert all("period" in str(p).lower() for p in sample), \
            f"Some {league} plays missing period info"


# ===========================================================================
# HockeyTech — Schedule (all non-NHL leagues)
# ===========================================================================

@pytest.mark.parametrize("league,season", list(SEASONS.items()))
class TestHockeyTechSchedule:

    def test_status_200(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_schedule_url(league, cfg, team="-1", season=season)
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_schedule_url(league, cfg, team="-1", season=season)
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_games_non_empty(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_schedule_url(league, cfg, team="-1", season=season)
        data = ht_get(http, url)
        games = _extract_sections_data(data)
        assert len(games) > 0, f"No games found in {league} schedule (season {season})"

    def test_games_have_date(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_schedule_url(league, cfg, team="-1", season=season)
        data = ht_get(http, url)
        games = _extract_sections_data(data)
        if games:
            row = games[0].get("row", games[0])
            assert "date" in str(row).lower() or "time" in str(row).lower(), \
                f"No date/time in {league} schedule game"

    def test_games_have_home_and_away(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_schedule_url(league, cfg, team="-1", season=season)
        data = ht_get(http, url)
        games = _extract_sections_data(data)
        if games:
            row_str = str(games[0]).lower()
            assert "home" in row_str or "visitor" in row_str or "away" in row_str, \
                f"No home/away info in {league} schedule game"


def _extract_sections_data(data) -> list:
    """Extract the flat list of game rows from HockeyTech schedule/standings response."""
    if isinstance(data, list) and data and "sections" in data[0]:
        rows = []
        for section in data[0].get("sections", []):
            rows.extend(section.get("data", []))
        return rows
    return []


# ===========================================================================
# HockeyTech — Standings (all non-NHL leagues)
# ===========================================================================

@pytest.mark.parametrize("league,season", list(SEASONS.items()))
class TestHockeyTechStandings:

    def test_status_200(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season)
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season)
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_teams_non_empty(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season)
        data = ht_get(http, url)
        teams = _extract_standings_rows(data)
        assert len(teams) > 0, f"No teams in {league} standings (season {season})"

    def test_teams_have_wins(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season)
        data = ht_get(http, url)
        teams = _extract_standings_rows(data)
        if teams:
            assert "wins" in str(teams[0]).lower() or "win" in str(teams[0]).lower(), \
                f"No wins in {league} standings row"

    def test_teams_have_points(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season)
        data = ht_get(http, url)
        teams = _extract_standings_rows(data)
        if teams:
            assert "points" in str(teams[0]).lower() or "pts" in str(teams[0]).lower(), \
                f"No points in {league} standings row"

    def test_groupby_conference_works(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season, groupTeamsBy="conference")
        resp = http.get(url, timeout=TIMEOUT)
        assert resp.status_code == 200

    def test_context_home_works(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_standings_url(league, cfg, season=season, context="home")
        resp = http.get(url, timeout=TIMEOUT)
        assert resp.status_code == 200


def _extract_standings_rows(data) -> list:
    """Extract team rows from HockeyTech standings response."""
    if isinstance(data, list) and data and "sections" in data[0]:
        rows = []
        for section in data[0].get("sections", []):
            for item in section.get("data", []):
                if "row" in item:
                    rows.append(item["row"])
        return rows
    return []


# ===========================================================================
# HockeyTech — Roster (all non-NHL leagues)
# Requires a real team_id from bootstrap (via team_ids fixture)
# ===========================================================================

@pytest.mark.parametrize("league", ["ahl", "pwhl", "ohl", "whl", "qmjhl"])
class TestHockeyTechRoster:

    def test_status_200(self, http, team_ids, league):
        tid = team_ids.get(league)
        if not tid:
            pytest.skip(f"Could not get team_id for {league}")
        cfg = LEAGUES[league]
        url = build_roster_url(league, cfg, team=tid, season=SEASONS[league])
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, team_ids, league):
        tid = team_ids.get(league)
        if not tid:
            pytest.skip(f"Could not get team_id for {league}")
        cfg = LEAGUES[league]
        url = build_roster_url(league, cfg, team=tid, season=SEASONS[league])
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_roster_non_empty(self, http, team_ids, league):
        tid = team_ids.get(league)
        if not tid:
            pytest.skip(f"Could not get team_id for {league}")
        cfg = LEAGUES[league]
        url = build_roster_url(league, cfg, team=tid, season=SEASONS[league])
        data = ht_get(http, url)
        players = _extract_roster_players(data)
        assert len(players) > 0, f"No players in {league} roster"

    def test_players_have_name(self, http, team_ids, league):
        tid = team_ids.get(league)
        if not tid:
            pytest.skip(f"Could not get team_id for {league}")
        cfg = LEAGUES[league]
        url = build_roster_url(league, cfg, team=tid, season=SEASONS[league])
        data = ht_get(http, url)
        players = _extract_roster_players(data)
        if players:
            assert "name" in str(players[0]).lower() or "first" in str(players[0]).lower(), \
                f"No name field in {league} roster player"

    def test_players_have_position(self, http, team_ids, league):
        tid = team_ids.get(league)
        if not tid:
            pytest.skip(f"Could not get team_id for {league}")
        cfg = LEAGUES[league]
        url = build_roster_url(league, cfg, team=tid, season=SEASONS[league])
        data = ht_get(http, url)
        players = _extract_roster_players(data)
        if players:
            assert "position" in str(players[0]).lower(), \
                f"No position field in {league} roster player"


def _extract_roster_players(data) -> list:
    """Extract player list from HockeyTech roster response."""
    if not isinstance(data, dict):
        return data if isinstance(data, list) else []

    roster = data.get("roster", [])
    if isinstance(roster, list) and roster and "sections" in roster[0]:
        players = []
        for section in roster[0].get("sections", []):
            title = section.get("title", "").lower()
            if title in ("forwards", "defencemen", "defenders", "goalies"):
                for item in section.get("data", []):
                    if "row" in item:
                        players.append(item["row"])
        return players

    # Fallback: SiteKit.Roster
    return data.get("SiteKit", {}).get("Roster", [])


# ===========================================================================
# HockeyTech — Player Stats: Skaters (all non-NHL leagues)
# ===========================================================================

@pytest.mark.parametrize("league,season", list(SEASONS.items()))
class TestHockeyTechSkaterStats:

    def test_status_200(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="skaters")
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="skaters")
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_skaters_non_empty(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="skaters")
        data = ht_get(http, url)
        players = _extract_player_stats(data)
        assert len(players) > 0, f"No skaters in {league} player stats"

    def test_skaters_have_goals(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="skaters")
        data = ht_get(http, url)
        players = _extract_player_stats(data)
        if players:
            assert "goals" in str(players[0]).lower() or "g" in players[0], \
                f"No goals in {league} skater stats"

    def test_skaters_have_points(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="skaters")
        data = ht_get(http, url)
        players = _extract_player_stats(data)
        if players:
            text = str(players[0]).lower()
            assert "points" in text or "pts" in text, f"No points in {league} skater stats"


# ===========================================================================
# HockeyTech — Player Stats: Goalies (all non-NHL leagues)
# ===========================================================================

@pytest.mark.parametrize("league,season", list(SEASONS.items()))
class TestHockeyTechGoalieStats:

    def test_status_200(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="goalies")
        assert http.get(url, timeout=TIMEOUT).status_code == 200

    def test_parseable_as_json(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="goalies")
        data = ht_get(http, url)
        assert isinstance(data, (dict, list))

    def test_goalies_non_empty(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="goalies")
        data = ht_get(http, url)
        players = _extract_player_stats(data)
        assert len(players) > 0, f"No goalies in {league} player stats"

    def test_goalies_have_gaa_or_save_pct(self, http, league, season):
        cfg = LEAGUES[league]
        url = build_stats_url(league, cfg, season=season, team="all", position="goalies")
        data = ht_get(http, url)
        players = _extract_player_stats(data)
        if players:
            text = str(players[0]).lower()
            assert any(kw in text for kw in ["gaa", "save", "goals_against", "savepct", "sv"]), \
                f"No GAA/save% in {league} goalie stats"


def _extract_player_stats(data) -> list:
    """Extract player rows from HockeyTech stats response."""
    if isinstance(data, dict):
        players = data.get("SiteKit", {}).get("Players")
        if players:
            return players

    if isinstance(data, list) and data and "sections" in data[0]:
        players = []
        for section in data[0].get("sections", []):
            for item in section.get("data", []):
                if "row" in item:
                    players.append(item["row"])
        return players

    return data if isinstance(data, list) else []
