"""
Test file to verify WHL and QMJHL goalie stats are working correctly.

This tests the fix for the API limitation where goalie stats need to use
the position='goalies' parameter instead of a separate view.
"""

import sys
import pytest

# Import pandas and polars only when needed to avoid dependency issues
pandas_available = True
polars_available = True

try:
    import pandas as pd
except ImportError:
    pandas_available = False

try:
    import polars as pl
except ImportError:
    polars_available = False


class TestWHLGoalieStats:
    """Test WHL goalie stats functionality."""

    def test_whl_api_goalie_stats_direct(self):
        """Test WHL API get_goalie_stats function directly."""
        from scrapernhl.whl.api import get_goalie_stats, WHLConfig

        result = get_goalie_stats(season=WHLConfig.DEFAULT_SEASON, limit=10)

        # Should return data structure with sections
        assert result is not None
        assert isinstance(result, (dict, list))

        # Extract players from response
        players = []
        if isinstance(result, list) and len(result) > 0:
            for item in result:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])

        # Should have returned some goalie data
        assert len(players) > 0, "No goalie stats returned from API"

        # Check for goalie-specific stats (not skater stats)
        first_player = players[0]
        goalie_stat_fields = ['gaa', 'savePct', 'saves', 'shotsAgainst', 'wins', 'losses']
        has_goalie_stats = any(field in first_player for field in goalie_stat_fields)

        assert has_goalie_stats, f"Response doesn't contain goalie stats. Fields: {list(first_player.keys())}"

    def test_whl_scraper_goalie_stats(self):
        """Test WHL scraper function for goalie stats."""
        from scrapernhl.whl.scrapers.teams_stats_roster import scrapePlayerStats
        from scrapernhl.whl.api import WHLConfig

        # Test with pandas output
        df = scrapePlayerStats(
            season=WHLConfig.DEFAULT_SEASON,
            player_type='goalie',
            limit=10,
            output_format='pandas'
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "No goalie stats returned from scraper"

        # Check for goalie-specific columns
        goalie_stat_cols = ['gaa', 'savePct', 'saves', 'shotsAgainst', 'wins', 'losses']
        has_goalie_stats = any(col in df.columns for col in goalie_stat_cols)

        assert has_goalie_stats, f"DataFrame doesn't contain goalie stats. Columns: {list(df.columns)}"

    def test_whl_scraper_skater_vs_goalie(self):
        """Test that WHL scraper returns different stats for skaters vs goalies."""
        from scrapernhl.whl.scrapers.teams_stats_roster import scrapePlayerStats
        from scrapernhl.whl.api import WHLConfig

        # Get skater stats
        skater_df = scrapePlayerStats(
            season=WHLConfig.DEFAULT_SEASON,
            player_type='skater',
            limit=5,
            output_format='pandas'
        )

        # Get goalie stats
        goalie_df = scrapePlayerStats(
            season=WHLConfig.DEFAULT_SEASON,
            player_type='goalie',
            limit=5,
            output_format='pandas'
        )

        # Skater stats should have goals, assists, points
        skater_stat_cols = ['goals', 'assists', 'points']
        has_skater_stats = any(col in skater_df.columns for col in skater_stat_cols)
        assert has_skater_stats, "Skater DataFrame missing skater-specific stats"

        # Goalie stats should have GAA, save%, wins
        goalie_stat_cols = ['gaa', 'savePct', 'wins']
        has_goalie_stats = any(col in goalie_df.columns for col in goalie_stat_cols)
        assert has_goalie_stats, "Goalie DataFrame missing goalie-specific stats"


class TestQMJHLGoalieStats:
    """Test QMJHL goalie stats functionality."""

    def test_qmjhl_api_goalie_stats_direct(self):
        """Test QMJHL API get_goalie_stats function directly."""
        from scrapernhl.qmjhl.api import get_goalie_stats, QMJHLConfig

        result = get_goalie_stats(season=QMJHLConfig.DEFAULT_SEASON, limit=10)

        # Should return data structure with sections
        assert result is not None
        assert isinstance(result, (dict, list))

        # Extract players from response
        players = []
        if isinstance(result, list) and len(result) > 0:
            for item in result:
                if isinstance(item, dict) and 'sections' in item:
                    for section in item['sections']:
                        if 'data' in section:
                            for data_item in section['data']:
                                if isinstance(data_item, dict) and 'row' in data_item:
                                    players.append(data_item['row'])

        # Should have returned some goalie data
        assert len(players) > 0, "No goalie stats returned from API"

        # Check for goalie-specific stats
        first_player = players[0]
        goalie_stat_fields = ['gaa', 'savePct', 'saves', 'shotsAgainst', 'wins', 'losses']
        has_goalie_stats = any(field in first_player for field in goalie_stat_fields)

        assert has_goalie_stats, f"Response doesn't contain goalie stats. Fields: {list(first_player.keys())}"

    def test_qmjhl_scraper_goalie_stats(self):
        """Test QMJHL scraper function for goalie stats."""
        from scrapernhl.qmjhl.scrapers.stats import scrapePlayerStats
        from scrapernhl.qmjhl.api import QMJHLConfig

        # Test with pandas output
        df = scrapePlayerStats(
            season=QMJHLConfig.DEFAULT_SEASON,
            player_type='goalie',
            limit=10,
            output_format='pandas'
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "No goalie stats returned from scraper"

        # Check for goalie-specific columns
        goalie_stat_cols = ['gaa', 'savePct', 'saves', 'shotsAgainst', 'wins', 'losses']
        has_goalie_stats = any(col in df.columns for col in goalie_stat_cols)

        assert has_goalie_stats, f"DataFrame doesn't contain goalie stats. Columns: {list(df.columns)}"

    def test_qmjhl_scraper_skater_vs_goalie(self):
        """Test that QMJHL scraper returns different stats for skaters vs goalies."""
        from scrapernhl.qmjhl.scrapers.stats import scrapePlayerStats
        from scrapernhl.qmjhl.api import QMJHLConfig

        # Get skater stats
        skater_df = scrapePlayerStats(
            season=QMJHLConfig.DEFAULT_SEASON,
            player_type='skater',
            limit=5,
            output_format='pandas'
        )

        # Get goalie stats
        goalie_df = scrapePlayerStats(
            season=QMJHLConfig.DEFAULT_SEASON,
            player_type='goalie',
            limit=5,
            output_format='pandas'
        )

        # Skater stats should have goals, assists, points
        skater_stat_cols = ['goals', 'assists', 'points']
        has_skater_stats = any(col in skater_df.columns for col in skater_stat_cols)
        assert has_skater_stats, "Skater DataFrame missing skater-specific stats"

        # Goalie stats should have GAA, save%, wins
        goalie_stat_cols = ['gaa', 'savePct', 'wins']
        has_goalie_stats = any(col in goalie_df.columns for col in goalie_stat_cols)
        assert has_goalie_stats, "Goalie DataFrame missing goalie-specific stats"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
