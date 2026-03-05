"""
Comprehensive tests for scrapernhl.HockeyScraper and the scrape() functional API.

Tests all core methods across all six supported leagues with different parameters.
Requires a network connection — these are integration tests against live APIs.
"""

import pytest
import pandas as pd

from scrapernhl import HockeyScraper, scrape
from scrapernhl.config import LEAGUES

# ---------------------------------------------------------------------------
# Known-good game IDs (completed regular-season games)
# ---------------------------------------------------------------------------
GAME_IDS = {
    "nhl":   2023020001,  # 2023-24 regular season
    "ahl":   1027781,     # 2025-26 season
    "qmjhl": 31909,       # 2025-26 season
    "ohl":   28150,       # 2024-25 season
    "whl":   1022126,     # 2024-25 season
    "pwhl":  210,         # 2023-24 season
}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def assert_df(df, min_rows: int = 1, required_cols: list[str] | None = None):
    """Assert that df is a non-empty DataFrame and optionally contains required columns."""
    assert isinstance(df, pd.DataFrame), f"Expected DataFrame, got {type(df)}"
    assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"
    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        assert not missing, f"Missing columns: {missing}"


# ===========================================================================
# 1. Instantiation & bootstrap
# ===========================================================================

class TestInstantiation:
    """Test HockeyScraper instantiation for every league."""

    @pytest.mark.parametrize("league", list(LEAGUES))
    def test_creates_scraper(self, league):
        s = HockeyScraper(league)
        assert s.league == league
        assert s.config is not None

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_bootstrap_data_fetched(self, league):
        """Non-NHL leagues should auto-fetch bootstrap on init."""
        s = HockeyScraper(league)
        assert s.bootstrap_data is not None
        assert isinstance(s.bootstrap_data, dict)

    def test_nhl_no_bootstrap_data(self):
        """NHL scraper should not auto-fetch bootstrap."""
        s = HockeyScraper("nhl")
        assert s.bootstrap_data is None

    def test_case_insensitive_league(self):
        """League name should be lowercased internally."""
        s = HockeyScraper("NHL")
        assert s.league == "nhl"

    def test_invalid_league_raises(self):
        with pytest.raises(KeyError):
            HockeyScraper("mlb")


# ===========================================================================
# 2. Bootstrap / metadata accessors
# ===========================================================================

class TestBootstrapAccessors:
    """Test bootstrap property accessors for non-NHL leagues."""

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_teams_property(self, league):
        s = HockeyScraper(league)
        teams = s.teams
        assert isinstance(teams, list)
        assert len(teams) > 0
        first = teams[0]
        assert "id" in first or "team_id" in first

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_current_season_id(self, league):
        s = HockeyScraper(league)
        sid = s.current_season_id
        assert sid is not None
        assert str(sid) == str(s.config.default_season)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_teams_include_all(self, league):
        s = HockeyScraper(league)
        all_teams = s.get_teams(include_all=True)
        no_all_teams = s.get_teams(include_all=False)
        # include_all=True should return >= include_all=False
        assert len(all_teams) >= len(no_all_teams)

    @pytest.mark.parametrize("league", ["ahl", "ohl", "whl"])
    def test_get_team_by_id(self, league):
        s = HockeyScraper(league)
        teams = s.get_teams()
        if teams:
            team = teams[0]
            found = s.get_team_by_id(team["id"])
            assert found is not None
            assert str(found["id"]) == str(team["id"])

    @pytest.mark.parametrize("league", ["ahl", "ohl", "whl"])
    def test_get_team_by_code(self, league):
        s = HockeyScraper(league)
        teams = s.get_teams()
        if teams and "team_code" in teams[0]:
            code = teams[0]["team_code"]
            found = s.get_team_by_code(code)
            assert found is not None

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_seasons_all(self, league):
        s = HockeyScraper(league)
        seasons = s.get_seasons("all")
        assert isinstance(seasons, list)
        assert len(seasons) > 0

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_seasons_regular(self, league):
        s = HockeyScraper(league)
        seasons = s.get_seasons("regular")
        assert isinstance(seasons, list)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_seasons_playoff(self, league):
        s = HockeyScraper(league)
        seasons = s.get_seasons("playoff")
        assert isinstance(seasons, list)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_conferences(self, league):
        s = HockeyScraper(league)
        confs = s.get_conferences()
        assert isinstance(confs, list)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_divisions(self, league):
        s = HockeyScraper(league)
        divs = s.get_divisions()
        assert isinstance(divs, list)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_positions(self, league):
        s = HockeyScraper(league)
        positions = s.get_positions()
        assert isinstance(positions, list)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_league_metadata(self, league):
        s = HockeyScraper(league)
        meta = s.get_league_metadata()
        assert isinstance(meta, dict)
        assert "name" in meta or "code" in meta

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_is_playoffs_active(self, league):
        s = HockeyScraper(league)
        result = s.is_playoffs_active()
        assert isinstance(result, bool)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_is_bilingual(self, league):
        s = HockeyScraper(league)
        result = s.is_bilingual()
        assert isinstance(result, bool)

    def test_get_current_season(self):
        s = HockeyScraper("ahl")
        season = s.get_current_season()
        # May be None if not in seasons list, but should not raise
        assert season is None or isinstance(season, dict)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_get_goalie_filters(self, league):
        s = HockeyScraper(league)
        filters = s.get_goalie_filters()
        assert isinstance(filters, list)

    def test_nhl_bootstrap_raises(self):
        s = HockeyScraper("nhl")
        with pytest.raises(NotImplementedError):
            s.bootstrap()


# ===========================================================================
# 3. play_by_play() — all leagues
# ===========================================================================

class TestPlayByPlay:
    """Test play_by_play() across all supported leagues."""

    def test_nhl_pbp(self):
        s = HockeyScraper("nhl")
        df = s.play_by_play(GAME_IDS["nhl"])
        assert_df(df, min_rows=10, required_cols=["typeDescKey", "periodDescriptor"])

    def test_ahl_pbp(self):
        s = HockeyScraper("ahl")
        df = s.play_by_play(GAME_IDS["ahl"])
        assert_df(df, min_rows=10)

    def test_qmjhl_pbp(self):
        s = HockeyScraper("qmjhl")
        df = s.play_by_play(GAME_IDS["qmjhl"])
        assert_df(df, min_rows=10)

    def test_ohl_pbp(self):
        s = HockeyScraper("ohl")
        df = s.play_by_play(GAME_IDS["ohl"])
        assert_df(df, min_rows=10)

    def test_whl_pbp(self):
        s = HockeyScraper("whl")
        df = s.play_by_play(GAME_IDS["whl"])
        assert_df(df, min_rows=10)

    def test_pwhl_pbp(self):
        s = HockeyScraper("pwhl")
        df = s.play_by_play(GAME_IDS["pwhl"])
        assert_df(df, min_rows=5)

    def test_pbp_nhlify_false(self):
        """With nhlify=False, OHL/WHL/QMJHL keep raw shot+goal rows."""
        s = HockeyScraper("ohl")
        df_raw = s.play_by_play(GAME_IDS["ohl"], nhlify=False)
        df_nhl = s.play_by_play(GAME_IDS["ohl"], nhlify=True)
        # nhlify merges shot+goal, so raw should have >= rows
        assert len(df_raw) >= len(df_nhl)

    def test_scrape_pbp_alias(self):
        """scrape_pbp() should be identical to play_by_play()."""
        s = HockeyScraper("ahl")
        df1 = s.play_by_play(GAME_IDS["ahl"])
        df2 = s.scrape_pbp(GAME_IDS["ahl"])
        assert df1.shape == df2.shape

    def test_scrape_game_pbp_alias(self):
        """scrape_game_pbp() should be identical to play_by_play()."""
        s = HockeyScraper("ahl")
        df1 = s.play_by_play(GAME_IDS["ahl"])
        df2 = s.scrape_game_pbp(GAME_IDS["ahl"])
        assert df1.shape == df2.shape

    def test_invalid_game_id_raises(self):
        s = HockeyScraper("nhl")
        with pytest.raises(Exception):
            s.play_by_play(0)


# ===========================================================================
# 4. player_stats() — all leagues, skaters + goalies
# ===========================================================================

class TestPlayerStats:
    """Test player_stats() across all leagues."""

    @pytest.mark.parametrize("league,season,team", [
        ("nhl", 20232024, "MTL"),  # NHL requires a team tricode
        ("ahl", 90, "all"),
        ("qmjhl", 208, "all"),
        ("ohl", 83, "all"),
        ("whl", 289, "all"),
        ("pwhl", 8, "all"),
    ])
    def test_skater_stats(self, league, season, team):
        s = HockeyScraper(league)
        df = s.player_stats(season=season, team=team, position="skaters")
        assert_df(df, min_rows=10)

    @pytest.mark.parametrize("league,season,team", [
        ("nhl", 20232024, "MTL"),  # NHL requires a team tricode
        ("ahl", 90, "all"),
        ("qmjhl", 208, "all"),
        ("ohl", 83, "all"),
        ("whl", 289, "all"),
        ("pwhl", 8, "all"),
    ])
    def test_goalie_stats(self, league, season, team):
        s = HockeyScraper(league)
        df = s.player_stats(season=season, team=team, position="goalies")
        assert_df(df, min_rows=1)

    def test_default_season(self):
        """When no season given, should use default_season from config."""
        s = HockeyScraper("ahl")
        df = s.player_stats()
        assert_df(df, min_rows=10)

    def test_scrape_skaters_alias(self):
        s = HockeyScraper("ahl")
        df1 = s.player_stats(position="skaters")
        df2 = s.scrape_skaters()
        assert df1.shape == df2.shape

    def test_scrape_goalies_alias(self):
        s = HockeyScraper("ahl")
        df1 = s.player_stats(position="goalies")
        df2 = s.scrape_goalies()
        assert df1.shape == df2.shape

    def test_ahl_skaters_has_league_col(self):
        s = HockeyScraper("ahl")
        df = s.player_stats(position="skaters")
        assert "league" in df.columns
        assert (df["league"] == "ahl").all()

    def test_ohl_goalies(self):
        s = HockeyScraper("ohl")
        df = s.scrape_goalies()
        assert_df(df, min_rows=1)


# ===========================================================================
# 5. schedule() — all leagues
# ===========================================================================

class TestSchedule:
    """Test schedule() across all leagues."""

    @pytest.mark.parametrize("league,season,team", [
        ("nhl", 20232024, "MTL"),  # NHL requires a team tricode
        ("ahl", 90, "all"),
        ("qmjhl", 211, "all"),
        ("ohl", 83, "all"),
        ("whl", 289, "all"),
        ("pwhl", 8, "all"),
    ])
    def test_full_schedule(self, league, season, team):
        s = HockeyScraper(league)
        df = s.schedule(team=team, season=season)
        assert_df(df, min_rows=10)

    def test_nhl_team_schedule(self):
        s = HockeyScraper("nhl")
        df = s.schedule(team="MTL", season=20232024)
        assert_df(df, min_rows=10)

    def test_scrape_schedule_alias(self):
        s = HockeyScraper("ahl")
        df1 = s.schedule()
        df2 = s.scrape_schedule()
        assert df1.shape == df2.shape

    def test_schedule_has_date_col(self):
        s = HockeyScraper("ahl")
        df = s.schedule()
        # Should have some date-related column
        date_cols = [c for c in df.columns if "date" in c.lower()]
        assert len(date_cols) > 0

    def test_default_season_schedule(self):
        s = HockeyScraper("whl")
        df = s.schedule()
        assert_df(df, min_rows=10)

    def test_ahl_schedule_league_col(self):
        s = HockeyScraper("ahl")
        df = s.schedule()
        assert "league" in df.columns


# ===========================================================================
# 6. roster() — all leagues
# ===========================================================================

class TestRoster:
    """Test roster() across all leagues."""

    def test_nhl_roster(self):
        s = HockeyScraper("nhl")
        df = s.roster(team="MTL", season=20232024)
        assert_df(df, min_rows=15)

    def test_ahl_roster(self):
        s = HockeyScraper("ahl")
        # Team ID 390 = San Diego Gulls (from AHL bootstrap)
        df = s.roster(team="390", season=90)
        assert_df(df, min_rows=5)

    def test_ohl_roster(self):
        s = HockeyScraper("ohl")
        teams = s.get_teams()
        if teams:
            team_id = teams[0]["id"]
            df = s.roster(team=str(team_id))
            assert_df(df, min_rows=5)

    def test_whl_roster(self):
        s = HockeyScraper("whl")
        teams = s.get_teams()
        if teams:
            team_id = teams[0]["id"]
            df = s.roster(team=str(team_id))
            assert_df(df, min_rows=5)

    def test_qmjhl_roster(self):
        s = HockeyScraper("qmjhl")
        teams = s.get_teams()
        if teams:
            team_id = teams[0]["id"]
            df = s.roster(team=str(team_id))
            assert_df(df, min_rows=5)

    def test_pwhl_roster(self):
        s = HockeyScraper("pwhl")
        teams = s.get_teams()
        if teams:
            team_id = teams[0]["id"]
            df = s.roster(team=str(team_id))
            assert_df(df, min_rows=5)

    def test_scrape_roster_alias(self):
        s = HockeyScraper("nhl")
        df1 = s.roster(team="TOR", season=20232024)
        df2 = s.scrape_roster(team="TOR", season=20232024)
        assert df1.shape == df2.shape

    def test_roster_has_league_col_non_nhl(self):
        s = HockeyScraper("ahl")
        teams = s.get_teams()
        if teams:
            df = s.roster(team=str(teams[0]["id"]))
            assert "league" in df.columns


# ===========================================================================
# 7. standings() — all leagues
# ===========================================================================

class TestStandings:
    """Test standings() across all leagues."""

    @pytest.mark.parametrize("league,season", [
        ("nhl", 20232024),
        ("ahl", 90),
        ("qmjhl", 211),
        ("ohl", 83),
        ("whl", 289),
        ("pwhl", 8),
    ])
    def test_standings(self, league, season):
        s = HockeyScraper(league)
        df = s.standings(season=season)
        assert_df(df, min_rows=5)

    def test_default_standings(self):
        s = HockeyScraper("nhl")
        df = s.standings()
        assert_df(df, min_rows=5)

    def test_scrape_standings_alias(self):
        s = HockeyScraper("nhl")
        df1 = s.standings()
        df2 = s.scrape_standings()
        assert df1.shape == df2.shape

    def test_standings_has_league_col_non_nhl(self):
        s = HockeyScraper("ahl")
        df = s.standings()
        assert "league" in df.columns


# ===========================================================================
# 8. teams_by_season() — all leagues
# ===========================================================================

class TestTeamsBySeason:
    """Test teams_by_season() across all leagues."""

    @pytest.mark.parametrize("league,season", [
        ("nhl", 20232024),
        ("ahl", 90),
        ("qmjhl", 211),
        ("ohl", 83),
        ("whl", 289),
        ("pwhl", 8),
    ])
    def test_teams_by_season(self, league, season):
        s = HockeyScraper(league)
        df = s.teams_by_season(season=season)
        assert_df(df, min_rows=1)
        assert "league" in df.columns
        assert "season" in df.columns

    def test_nhl_teams_by_season_default(self):
        s = HockeyScraper("nhl")
        df = s.teams_by_season()
        assert_df(df, min_rows=5)


# ===========================================================================
# 9. scrape_teams() — NHL only
# ===========================================================================

class TestScrapeTeams:
    """Test scrape_teams() for NHL (only supported league)."""

    def test_scrape_teams_calendar(self):
        s = HockeyScraper("nhl")
        df = s.scrape_teams(source="calendar")
        assert_df(df, min_rows=5)

    def test_scrape_teams_franchise(self):
        s = HockeyScraper("nhl")
        df = s.scrape_teams(source="franchise")
        assert_df(df, min_rows=5)

    def test_scrape_teams_records(self):
        s = HockeyScraper("nhl")
        df = s.scrape_teams(source="records")
        assert_df(df, min_rows=5)

    def test_scrape_teams_invalid_source(self):
        s = HockeyScraper("nhl")
        with pytest.raises(ValueError):
            s.scrape_teams(source="invalid")

    def test_scrape_teams_non_nhl_raises(self):
        s = HockeyScraper("ahl")
        with pytest.raises(NotImplementedError):
            s.scrape_teams(source="calendar")

    def test_scrape_teams_has_league_col(self):
        s = HockeyScraper("nhl")
        df = s.scrape_teams(source="calendar")
        assert "league" in df.columns
        assert (df["league"] == "nhl").all()


# ===========================================================================
# 10. seasons() — all leagues
# ===========================================================================

class TestSeasons:
    """Test seasons() across all leagues."""

    @pytest.mark.parametrize("league", list(LEAGUES))
    def test_seasons_all(self, league):
        s = HockeyScraper(league)
        df = s.seasons("all")
        assert_df(df, min_rows=1)
        assert "league" in df.columns

    def test_seasons_regular_non_nhl(self):
        s = HockeyScraper("ahl")
        df = s.seasons("regular")
        assert isinstance(df, pd.DataFrame)

    def test_seasons_playoff_non_nhl(self):
        s = HockeyScraper("ahl")
        df = s.seasons("playoff")
        assert isinstance(df, pd.DataFrame)


# ===========================================================================
# 11. scrape_multiple_games() — batch operations
# ===========================================================================

class TestBatchOperations:
    """Test scrape_multiple_games() batch method."""

    def test_multiple_games_ahl(self):
        s = HockeyScraper("ahl")
        game_ids = [1027781, 1027779]
        df = s.scrape_multiple_games(game_ids)
        assert_df(df, min_rows=10)

    def test_multiple_games_nhl(self):
        s = HockeyScraper("nhl")
        game_ids = [2023020001, 2023020002]
        df = s.scrape_multiple_games(game_ids)
        assert_df(df, min_rows=10)

    def test_multiple_games_partial_failure(self):
        """If one game fails, the rest should still be returned."""
        s = HockeyScraper("ahl")
        game_ids = [1027781, 9999999]  # second one is invalid
        df = s.scrape_multiple_games(game_ids)
        # Should still have data from the valid game
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_multiple_games_all_fail(self):
        """If all games fail, should return an empty DataFrame."""
        s = HockeyScraper("ahl")
        df = s.scrape_multiple_games([9999999, 8888888])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


# ===========================================================================
# 12. NHL-only methods
# ===========================================================================

class TestNHLOnly:
    """Test NHL-specific methods and that non-NHL raises NotImplementedError."""

    def test_nhl_only_methods_raise_for_ahl(self):
        s = HockeyScraper("ahl")
        nhl_methods = [
            lambda: s.scrape_plays(1027781),
            lambda: s.standings_by_date("2024-01-01"),
            lambda: s.team_stats("TOR"),
            lambda: s.draft(2024),
            lambda: s.draft_records(2024),
            lambda: s.team_draft_history(1),
            lambda: s.html_pbp(2023020001),
            lambda: s.shifts(2023020001),
            lambda: s.scrape_game(2023020001),
        ]
        for fn in nhl_methods:
            with pytest.raises(NotImplementedError):
                fn()

    def test_scrape_plays(self):
        s = HockeyScraper("nhl")
        df = s.scrape_plays(GAME_IDS["nhl"])
        assert_df(df, min_rows=10)

    def test_standings_by_date_default(self):
        s = HockeyScraper("nhl")
        df = s.standings_by_date()
        assert_df(df, min_rows=5)

    def test_standings_by_date_specific(self):
        s = HockeyScraper("nhl")
        df = s.standings_by_date("2024-01-15")
        assert_df(df, min_rows=5)

    def test_team_stats_skaters(self):
        s = HockeyScraper("nhl")
        df = s.team_stats(team="MTL", season=20232024, session=2, goalies=False)
        assert_df(df, min_rows=5)

    def test_team_stats_goalies(self):
        s = HockeyScraper("nhl")
        df = s.team_stats(team="MTL", season=20232024, session=2, goalies=True)
        assert_df(df, min_rows=1)

    def test_draft(self):
        s = HockeyScraper("nhl")
        df = s.draft(year=2024, round="all")
        assert_df(df, min_rows=50)

    def test_draft_specific_round(self):
        s = HockeyScraper("nhl")
        df = s.draft(year=2023, round=1)
        assert_df(df, min_rows=1)

    def test_draft_records(self):
        s = HockeyScraper("nhl")
        df = s.draft_records(year=2024)
        assert_df(df, min_rows=1)

    def test_team_draft_history(self):
        s = HockeyScraper("nhl")
        df = s.team_draft_history(franchise=1)
        assert_df(df, min_rows=1)

    def test_html_pbp(self):
        s = HockeyScraper("nhl")
        df = s.html_pbp(GAME_IDS["nhl"])
        assert_df(df, min_rows=10)

    def test_html_pbp_return_raw(self):
        s = HockeyScraper("nhl")
        result = s.html_pbp(GAME_IDS["nhl"], return_raw=True)
        assert isinstance(result, tuple)
        df, raw = result
        assert_df(df, min_rows=10)
        assert isinstance(raw, dict)

    def test_shifts(self):
        s = HockeyScraper("nhl")
        df = s.shifts(GAME_IDS["nhl"])
        assert_df(df, min_rows=10)

    def test_scrape_game(self):
        s = HockeyScraper("nhl")
        df = s.scrape_game(GAME_IDS["nhl"])
        assert_df(df, min_rows=10)

    def test_scrape_game_include_tuple(self):
        s = HockeyScraper("nhl")
        result = s.scrape_game(GAME_IDS["nhl"], include_tuple=True)
        assert isinstance(result, tuple)
        # GameResult namedtuple: (pbp, shifts, html_pbp, home_team, away_team)
        assert len(result) == 5
        assert_df(result[0], min_rows=10)  # pbp DataFrame

    def test_get_game_data(self):
        s = HockeyScraper("nhl")
        data = s.get_game_data(GAME_IDS["nhl"])
        assert isinstance(data, dict)


# ===========================================================================
# 13. NHL Analytics pipeline
# ===========================================================================

class TestNHLAnalytics:
    """Test the NHL analytics chain: scrape_game → on-ice stats."""

    @pytest.fixture(scope="class")
    def game_data(self):
        """Shared fixture: scrape one game and build all derived data."""
        s = HockeyScraper("nhl")
        game_id = GAME_IDS["nhl"]
        pbp = s.scrape_game(game_id)
        shifts = s.shifts(game_id)
        return {"scraper": s, "pbp": pbp, "shifts": shifts, "game_id": game_id}

    def test_build_shifts_events(self, game_data):
        s = game_data["scraper"]
        shifts = game_data["shifts"]
        df = s.build_shifts_events(shifts)
        assert_df(df, min_rows=10)

    def test_build_on_ice_long(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.build_on_ice_long(pbp)
        assert_df(df, min_rows=10)

    def test_build_on_ice_wide(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.build_on_ice_wide(pbp)
        assert_df(df, min_rows=10)

    def test_build_on_ice_wide_no_goalie(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.build_on_ice_wide(pbp, include_goalie=False)
        assert_df(df, min_rows=10)

    def test_seconds_matrix(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        shifts = game_data["shifts"]
        matrix = s.seconds_matrix(pbp, shifts)
        assert_df(matrix, min_rows=1)

    def test_strengths_by_second(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        shifts = game_data["shifts"]
        matrix = s.seconds_matrix(pbp, shifts)
        df = s.strengths_by_second(matrix)
        assert_df(df, min_rows=1)

    def test_toi_by_strength_all(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        shifts = game_data["shifts"]
        matrix = s.seconds_matrix(pbp, shifts)
        strengths = s.strengths_by_second(matrix)
        df = s.toi_by_strength_all(matrix, strengths)
        assert_df(df, min_rows=1)

    def test_toi_by_strength_in_seconds(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        shifts = game_data["shifts"]
        matrix = s.seconds_matrix(pbp, shifts)
        strengths = s.strengths_by_second(matrix)
        df = s.toi_by_strength_all(matrix, strengths, in_seconds=True)
        assert_df(df, min_rows=1)

    def test_shared_toi_teammates(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        shifts = game_data["shifts"]
        matrix = s.seconds_matrix(pbp, shifts)
        strengths = s.strengths_by_second(matrix)
        df = s.shared_toi_teammates(matrix, strengths)
        assert isinstance(df, pd.DataFrame)

    def test_shared_toi_opponents(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        shifts = game_data["shifts"]
        matrix = s.seconds_matrix(pbp, shifts)
        strengths = s.strengths_by_second(matrix)
        df = s.shared_toi_opponents(matrix, strengths)
        assert isinstance(df, pd.DataFrame)

    def test_on_ice_stats(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.on_ice_stats(pbp)
        assert_df(df, min_rows=1)

    def test_on_ice_stats_with_goalies(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.on_ice_stats(pbp, include_goalies=True)
        assert_df(df, min_rows=1)

    def test_on_ice_stats_with_rates(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.on_ice_stats(pbp, rates=True)
        # Per-60 rate columns should be present
        rate_cols = [c for c in df.columns if "60" in c or "per" in c.lower()]
        assert len(rate_cols) > 0

    def test_combo_on_ice_stats(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        # Use the home team from the pbp
        if "homeTeam" in pbp.columns:
            focus = pbp["homeTeam"].iloc[0]
        else:
            focus = "MTL"
        df = s.combo_on_ice_stats(pbp, focus_team=focus, n_team=2)
        assert isinstance(df, pd.DataFrame)

    def test_team_strength_aggregates(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.team_strength_aggregates(pbp)
        assert_df(df, min_rows=1)

    def test_team_strength_aggregates_with_rates(self, game_data):
        s = game_data["scraper"]
        pbp = game_data["pbp"]
        df = s.team_strength_aggregates(pbp, rates=True)
        assert_df(df, min_rows=1)

    def test_analytics_raises_for_non_nhl(self):
        s = HockeyScraper("ahl")
        dummy = pd.DataFrame()
        analytics_methods = [
            lambda: s.build_shifts_events(dummy),
            lambda: s.build_on_ice_long(dummy),
            lambda: s.build_on_ice_wide(dummy),
            lambda: s.seconds_matrix(dummy, dummy),
            lambda: s.strengths_by_second(dummy),
            lambda: s.toi_by_strength_all(dummy, dummy),
            lambda: s.shared_toi_teammates(dummy, dummy),
            lambda: s.shared_toi_opponents(dummy, dummy),
            lambda: s.on_ice_stats(dummy),
            lambda: s.combo_on_ice_stats(dummy, "TOR"),
            lambda: s.team_strength_aggregates(dummy),
        ]
        for fn in analytics_methods:
            with pytest.raises(NotImplementedError):
                fn()


# ===========================================================================
# 14. Functional API — scrape()
# ===========================================================================

class TestFunctionalAPI:
    """Test the top-level scrape() functional API."""

    def test_scrape_pbp_ahl(self):
        df = scrape("ahl", "pbp", game_id=GAME_IDS["ahl"])
        assert_df(df, min_rows=10)

    def test_scrape_pbp_nhl(self):
        df = scrape("nhl", "pbp", game_id=GAME_IDS["nhl"])
        assert_df(df, min_rows=10)

    def test_scrape_pbp_qmjhl(self):
        df = scrape("qmjhl", "pbp", game_id=GAME_IDS["qmjhl"])
        assert_df(df, min_rows=10)

    def test_scrape_pbp_ohl(self):
        df = scrape("ohl", "pbp", game_id=GAME_IDS["ohl"])
        assert_df(df, min_rows=10)

    def test_scrape_pbp_whl(self):
        df = scrape("whl", "pbp", game_id=GAME_IDS["whl"])
        assert_df(df, min_rows=10)

    def test_scrape_pbp_pwhl(self):
        df = scrape("pwhl", "pbp", game_id=GAME_IDS["pwhl"])
        assert_df(df, min_rows=5)

    def test_scrape_stats_ahl(self):
        df = scrape("ahl", "stats", season=90, position="skaters")
        assert_df(df, min_rows=10)

    def test_scrape_stats_nhl(self):
        df = scrape("nhl", "stats", team="MTL", season=20232024, position="skaters")
        assert_df(df, min_rows=10)

    def test_scrape_schedule(self):
        df = scrape("nhl", "schedule", team="TOR", season=20232024)
        assert_df(df, min_rows=10)

    def test_scrape_roster(self):
        df = scrape("nhl", "roster", team="MTL", season=20232024)
        assert_df(df, min_rows=5)

    def test_scrape_standings(self):
        df = scrape("nhl", "standings", season=20232024)
        assert_df(df, min_rows=5)

    def test_scrape_teams_nhl(self):
        df = scrape("nhl", "teams")
        assert_df(df, min_rows=5)

    def test_scrape_teams_non_nhl(self):
        df = scrape("ahl", "teams", season=90)
        assert_df(df, min_rows=5)

    def test_scrape_teams_by_season(self):
        df = scrape("nhl", "teams_by_season", season=20232024)
        assert_df(df, min_rows=5)

    def test_scrape_scrape_teams_nhl(self):
        df = scrape("nhl", "scrape_teams", source="calendar")
        assert_df(df, min_rows=5)

    def test_scrape_seasons_nhl(self):
        df = scrape("nhl", "seasons")
        assert_df(df, min_rows=5)

    def test_scrape_seasons_ahl(self):
        df = scrape("ahl", "seasons")
        assert_df(df, min_rows=5)

    def test_invalid_data_type_raises(self):
        with pytest.raises(ValueError):
            scrape("nhl", "invalid_type")

    def test_case_insensitive_league(self):
        df = scrape("NHL", "standings")
        assert_df(df, min_rows=5)


# ===========================================================================
# 15. bootstrap() explicit call — non-NHL only
# ===========================================================================

class TestBootstrapExplicit:
    """Test the bootstrap() method called explicitly."""

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_bootstrap_scorebar(self, league):
        s = HockeyScraper(league)
        data = s.bootstrap(page_name="scorebar")
        assert isinstance(data, dict)

    @pytest.mark.parametrize("league", ["ahl", "qmjhl", "ohl", "whl", "pwhl"])
    def test_bootstrap_with_season(self, league):
        s = HockeyScraper(league)
        season = str(s.config.default_season)
        data = s.bootstrap(season=season)
        assert isinstance(data, dict)
