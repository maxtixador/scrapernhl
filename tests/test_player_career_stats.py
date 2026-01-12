"""
Test suite for scrape_player_career_stats across all leagues

This verifies that the career stats function properly parses the nested
API response structure and returns a flattened DataFrame instead of
just returning the raw 'sections' data.
"""
import pytest
import pandas as pd


class TestPlayerCareerStats:
    """Test scrape_player_career_stats for all leagues"""

    def test_ahl_career_stats(self):
        """Test AHL career stats returns proper DataFrame"""
        from scrapernhl.ahl.scrapers.player import scrape_player_career_stats

        # Use Sam Poulin (8890) from notebook
        result = scrape_player_career_stats(8890)

        # Should return a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should have multiple rows (one per season)
        assert len(result) > 1

        # Should NOT have 'sections' column (means it wasn't parsed)
        assert 'sections' not in result.columns

        # Should have proper stat columns
        assert 'row.season_name' in result.columns
        assert 'row.goals' in result.columns
        assert 'row.assists' in result.columns
        assert 'row.games_played' in result.columns

    def test_ohl_career_stats(self):
        """Test OHL career stats returns proper DataFrame"""
        from scrapernhl.ohl.scrapers.player import scrape_player_career_stats

        # Use Nathan Aspinall (8705) from notebook
        result = scrape_player_career_stats(8705)

        # Should return a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should have multiple rows (one per season)
        assert len(result) > 1

        # Should NOT have 'sections' column
        assert 'sections' not in result.columns

        # Should have proper stat columns
        assert 'row.season_name' in result.columns
        assert 'row.goals' in result.columns
        assert 'row.assists' in result.columns

    def test_whl_career_stats(self):
        """Test WHL career stats returns proper DataFrame"""
        from scrapernhl.whl.scrapers.player import scrape_player_career_stats

        # Use Cameron Schmidt (29235) from notebook
        result = scrape_player_career_stats(29235)

        # Should return a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should have multiple rows (one per season)
        assert len(result) > 1

        # Should NOT have 'sections' column
        assert 'sections' not in result.columns

        # Should have proper stat columns
        assert 'row.season_name' in result.columns
        assert 'row.goals' in result.columns
        assert 'row.assists' in result.columns

    def test_qmjhl_career_stats(self):
        """Test QMJHL career stats returns proper DataFrame"""
        from scrapernhl.qmjhl.scrapers.player import scrape_player_career_stats

        # Use Philippe Veilleux (20174) from notebook
        result = scrape_player_career_stats(20174)

        # Should return a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should have multiple rows (one per season)
        assert len(result) > 1

        # Should NOT have 'sections' column
        assert 'sections' not in result.columns

        # Should have proper stat columns
        assert 'row.season_name' in result.columns
        assert 'row.goals' in result.columns
        assert 'row.assists' in result.columns

    def test_career_stats_filters_totals(self):
        """Test that career stats filters out 'Total' rows"""
        from scrapernhl.ohl.scrapers.player import scrape_player_career_stats

        result = scrape_player_career_stats(8705)

        # Should not have any rows with season_name == "Total"
        if 'row.season_name' in result.columns:
            assert 'Total' not in result['row.season_name'].values
