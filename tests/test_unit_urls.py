"""Unit tests for scrapernhl.urls URL builders — no I/O, no network."""
import pytest

from scrapernhl.config import LEAGUES
from scrapernhl.urls import (
    build_nhl_club_stats_url,
    build_nhl_pbp_url,
    build_nhl_roster_url,
    build_nhl_schedule_url,
    build_nhl_standings_url,
    build_pbp_url,
    build_roster_url,
    build_schedule_url,
    build_stats_url,
)

_NHL_BASE = "https://api-web.nhle.com"


# ---------------------------------------------------------------------------
# Standalone NHL URL helpers (no config needed)
# ---------------------------------------------------------------------------

class TestBuildNhlPbpUrl:
    def test_integer_game_id(self):
        url = build_nhl_pbp_url(2023020001)
        assert url == f"{_NHL_BASE}/v1/gamecenter/2023020001/play-by-play"

    def test_string_game_id(self):
        url = build_nhl_pbp_url("2023020001")
        assert url == f"{_NHL_BASE}/v1/gamecenter/2023020001/play-by-play"

    def test_url_contains_base(self):
        url = build_nhl_pbp_url(1)
        assert url.startswith(_NHL_BASE)


class TestBuildNhlScheduleUrl:
    def test_returns_correct_url(self):
        url = build_nhl_schedule_url("MTL", 20232024)
        assert url == f"{_NHL_BASE}/v1/club-schedule-season/MTL/20232024"

    def test_accepts_string_season(self):
        url = build_nhl_schedule_url("TOR", "20242025")
        assert "/v1/club-schedule-season/TOR/20242025" in url

    def test_team_code_in_path(self):
        url = build_nhl_schedule_url("BOS", 20232024)
        assert "/BOS/" in url


class TestBuildNhlStandingsUrl:
    def test_returns_correct_url(self):
        url = build_nhl_standings_url("2024-01-15")
        assert url == f"{_NHL_BASE}/v1/standings/2024-01-15"

    def test_date_in_path(self):
        url = build_nhl_standings_url("2023-11-01")
        assert "2023-11-01" in url


class TestBuildNhlRosterUrl:
    def test_returns_correct_url(self):
        url = build_nhl_roster_url("TOR", 20232024)
        assert url == f"{_NHL_BASE}/v1/roster/TOR/20232024"

    def test_accepts_string_season(self):
        url = build_nhl_roster_url("MTL", "20242025")
        assert "/v1/roster/MTL/20242025" in url


class TestBuildNhlClubStatsUrl:
    def test_default_session_is_2(self):
        url = build_nhl_club_stats_url("MTL", 20232024)
        assert url == f"{_NHL_BASE}/v1/club-stats/MTL/20232024/2"

    def test_custom_session(self):
        url = build_nhl_club_stats_url("MTL", 20232024, session=1)
        assert url == f"{_NHL_BASE}/v1/club-stats/MTL/20232024/1"

    def test_accepts_string_season(self):
        url = build_nhl_club_stats_url("TOR", "20242025", session=2)
        assert "/v1/club-stats/TOR/20242025/2" in url


# ---------------------------------------------------------------------------
# Multi-league URL builders (take league + config)
# ---------------------------------------------------------------------------

class TestBuildPbpUrl:
    def test_nhl_routes_to_api_web(self):
        config = LEAGUES["nhl"]
        url = build_pbp_url("nhl", config, 2023020001)
        assert "/v1/gamecenter/2023020001/play-by-play" in url
        assert "api-web.nhle.com" in url

    def test_ahl_hockeytech_a_style(self):
        config = LEAGUES["ahl"]
        url = build_pbp_url("ahl", config, 12345)
        assert "gameCenterPlayByPlay" in url or "view=gameCenterPlayByPlay" in url
        assert f"game_id=12345" in url
        assert "key=" in url
        assert "client_code=" in url
        assert "league_id=" in url

    def test_ohl_hockeytech_b_style(self):
        config = LEAGUES["ohl"]
        url = build_pbp_url("ohl", config, 99999)
        assert "tab=pxpverbose" in url or "pxpverbose" in url
        assert "game_id=99999" in url

    def test_non_nhl_url_contains_base_url(self):
        config = LEAGUES["ahl"]
        url = build_pbp_url("ahl", config, 1)
        assert url.startswith(config.base_url)


class TestBuildScheduleUrl:
    def test_nhl_routes_to_club_schedule(self):
        config = LEAGUES["nhl"]
        url = build_schedule_url("nhl", config, "MTL", 20232024)
        assert "/v1/club-schedule-season/MTL/20232024" in url

    def test_ahl_includes_required_params(self):
        config = LEAGUES["ahl"]
        url = build_schedule_url("ahl", config, "all", 90)
        assert "view=schedule" in url
        assert "season=90" in url
        assert "key=" in url
        assert "client_code=" in url

    def test_qmjhl_includes_league_id(self):
        config = LEAGUES["qmjhl"]
        url = build_schedule_url("qmjhl", config, "all", 70)
        assert "league_id=" in url


class TestBuildRosterUrl:
    def test_nhl_routes_to_roster_endpoint(self):
        config = LEAGUES["nhl"]
        url = build_roster_url("nhl", config, "MTL", 20232024)
        assert "/v1/roster/MTL/20232024" in url

    def test_ahl_uses_team_id_param(self):
        config = LEAGUES["ahl"]
        url = build_roster_url("ahl", config, "456", 90)
        assert "view=roster" in url
        assert "team_id=456" in url

    def test_whl_includes_league_id(self):
        config = LEAGUES["whl"]
        url = build_roster_url("whl", config, "123", 95)
        assert "league_id=" in url


class TestBuildStatsUrl:
    def test_nhl_routes_to_club_stats(self):
        config = LEAGUES["nhl"]
        url = build_stats_url("nhl", config, 20232024, "MTL", "skaters")
        assert "/v1/club-stats/MTL/20232024/2" in url

    def test_ahl_sets_default_limit(self):
        config = LEAGUES["ahl"]
        url = build_stats_url("ahl", config, 90, "all", "skaters")
        assert "limit=2000" in url

    def test_ahl_goalies_adds_position_param(self):
        config = LEAGUES["ahl"]
        url = build_stats_url("ahl", config, 90, "all", "goalies")
        assert "position=goalies" in url

    def test_ahl_includes_season(self):
        config = LEAGUES["ahl"]
        url = build_stats_url("ahl", config, 90, "all", "skaters")
        assert "season=90" in url
