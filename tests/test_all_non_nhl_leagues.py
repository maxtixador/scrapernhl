"""
Tests for all non-NHL league scrapers (AHL, PWHL, OHL, WHL, QMJHL)
via the unified HockeyScraper API.
"""

import pytest
import pandas as pd

from scrapernhl import HockeyScraper


def assert_df(df, min_rows: int = 1):
    assert isinstance(df, pd.DataFrame), f"Expected DataFrame, got {type(df)}"
    assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"


NON_NHL_LEAGUES = ["ahl", "pwhl", "ohl", "whl", "qmjhl"]


class TestNonNHLTeams:
    @pytest.mark.parametrize("league", NON_NHL_LEAGUES)
    def test_teams(self, league):
        s = HockeyScraper(league)
        teams = s.get_teams()
        assert isinstance(teams, list)
        assert len(teams) > 0
        print(f"✓ {league.upper()} Teams: {len(teams)} teams found")


class TestNonNHLStandings:
    @pytest.mark.parametrize("league", NON_NHL_LEAGUES)
    def test_standings(self, league):
        s = HockeyScraper(league)
        df = s.standings()
        assert_df(df)
        print(f"✓ {league.upper()} Standings: {len(df)} rows")


class TestNonNHLSchedule:
    @pytest.mark.parametrize("league", NON_NHL_LEAGUES)
    def test_schedule(self, league):
        s = HockeyScraper(league)
        df = s.schedule()
        assert_df(df)
        print(f"✓ {league.upper()} Schedule: {len(df)} rows")


class TestNonNHLSkaterStats:
    @pytest.mark.parametrize("league", NON_NHL_LEAGUES)
    def test_skater_stats(self, league):
        s = HockeyScraper(league)
        df = s.player_stats(position="skaters")
        assert_df(df, min_rows=10)
        print(f"✓ {league.upper()} Skater Stats: {len(df)} rows")


class TestNonNHLGoalieStats:
    @pytest.mark.parametrize("league", NON_NHL_LEAGUES)
    def test_goalie_stats(self, league):
        s = HockeyScraper(league)
        df = s.player_stats(position="goalies")
        assert_df(df)
        print(f"✓ {league.upper()} Goalie Stats: {len(df)} rows")


class TestNonNHLScorebar:
    @pytest.mark.parametrize("league", NON_NHL_LEAGUES)
    def test_scorebar(self, league):
        s = HockeyScraper(league)
        data = s.bootstrap(page_name="scorebar")
        assert isinstance(data, dict)
        print(f"✓ {league.upper()} Scorebar: retrieved successfully")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("NON-NHL LEAGUE API TESTS")
    print("="*60 + "\n")

    import sys

    test_classes = [
        (TestNonNHLTeams, "Teams"),
        (TestNonNHLStandings, "Standings"),
        (TestNonNHLSchedule, "Schedule"),
        (TestNonNHLSkaterStats, "Skater Stats"),
        (TestNonNHLGoalieStats, "Goalie Stats"),
        (TestNonNHLScorebar, "Scorebar"),
    ]

    total_passed = 0
    total_failed = 0

    for test_class, category in test_classes:
        print(f"\n{category}")
        print("-" * 40)
        instance = test_class()
        for league in NON_NHL_LEAGUES:
            method_name = [m for m in dir(instance) if m.startswith("test_")][0]
            method = getattr(instance, method_name)
            try:
                method(league)
                total_passed += 1
            except Exception as e:
                print(f"✗ {league.upper()} {category}: {e}")
                total_failed += 1

    print(f"\n{'='*60}")
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print('='*60 + "\n")
    sys.exit(0 if total_failed == 0 else 1)
