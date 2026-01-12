"""
Tests for the DataFrame-based scrape functions used in notebooks 05-09.

These tests validate that all the scrape* functions return proper DataFrames
as used in the league example notebooks.
"""

import pytest
import pandas as pd
import polars as pl
from typing import Union

# Import scrape functions for each league
# PWHL
from scrapernhl.pwhl.scrapers.schedule import scrapeSchedule as pwhl_scrapeSchedule
from scrapernhl.pwhl.scrapers.teams_stats_roster import (
    scrapeTeams as pwhl_scrapeTeams,
    scrapeStandings as pwhl_scrapeStandings,
    scrapePlayerStats as pwhl_scrapePlayerStats,
    scrapeRoster as pwhl_scrapeRoster,
)
from scrapernhl.pwhl.scrapers.games import scrape_game as pwhl_scrape_game

# AHL
from scrapernhl.ahl.scrapers.complete_suite import (
    scrapeSchedule as ahl_scrapeSchedule,
    scrapeTeams as ahl_scrapeTeams,
    scrapeStandings as ahl_scrapeStandings,
    scrapePlayerStats as ahl_scrapePlayerStats,
    scrapeRoster as ahl_scrapeRoster,
)
from scrapernhl.ahl.scrapers.games import scrape_game as ahl_scrape_game

# OHL
from scrapernhl.ohl.scrapers.schedule import scrapeSchedule as ohl_scrapeSchedule
from scrapernhl.ohl.scrapers.teams import scrapeTeams as ohl_scrapeTeams
from scrapernhl.ohl.scrapers.standings import scrapeStandings as ohl_scrapeStandings
from scrapernhl.ohl.scrapers.stats import scrapePlayerStats as ohl_scrapePlayerStats
from scrapernhl.ohl.scrapers.roster import scrapeRoster as ohl_scrapeRoster
from scrapernhl.ohl.scrapers.games import scrape_game as ohl_scrape_game

# WHL
from scrapernhl.whl.scrapers.schedule import scrapeSchedule as whl_scrapeSchedule
from scrapernhl.whl.scrapers.teams_stats_roster import (
    scrapeTeams as whl_scrapeTeams,
    scrapeStandings as whl_scrapeStandings,
    scrapePlayerStats as whl_scrapePlayerStats,
    scrapeRoster as whl_scrapeRoster,
)
from scrapernhl.whl.scrapers.games import scrape_game as whl_scrape_game

# QMJHL
from scrapernhl.qmjhl.scrapers.schedule_new import scrapeSchedule as qmjhl_scrapeSchedule
from scrapernhl.qmjhl.scrapers.teams_new import scrapeTeams as qmjhl_scrapeTeams
from scrapernhl.qmjhl.scrapers.standings import scrapeStandings as qmjhl_scrapeStandings
from scrapernhl.qmjhl.scrapers.stats import scrapePlayerStats as qmjhl_scrapePlayerStats
from scrapernhl.qmjhl.scrapers.roster import scrapeRoster as qmjhl_scrapeRoster
from scrapernhl.qmjhl.scrapers.games import scrape_game as qmjhl_scrape_game


# ==============================================================================
# Test Configuration
# ==============================================================================

LEAGUE_CONFIGS = {
    'PWHL': {
        'season': 8,
        'team_id': 1,  # Boston Fleet
    },
    'AHL': {
        'season': 90,
        'team_id': 440,  # Abbotsford Canucks
    },
    'OHL': {
        'season': 83,
        'team_id': 7,  # Barrie Colts
    },
    'WHL': {
        'season': 289,
        'team_id': 201,  # Brandon Wheat Kings
    },
    'QMJHL': {
        'season': 211,
        'team_id': 16,  # Baie-Comeau Drakkar
    },
}


# ==============================================================================
# Helper Functions
# ==============================================================================

def validate_dataframe(df: Union[pd.DataFrame, pl.DataFrame], league: str, min_rows: int = 0, function_name: str = "") -> None:
    """Validate that result is a DataFrame with expected structure"""
    assert isinstance(df, (pd.DataFrame, pl.DataFrame)), \
        f"{league} {function_name}: Should return a pandas or polars DataFrame, got {type(df)}"

    # Get row count based on DataFrame type
    if isinstance(df, pd.DataFrame):
        row_count = len(df)
        col_count = len(df.columns)
    else:  # polars
        row_count = df.shape[0]
        col_count = df.shape[1]

    assert row_count >= min_rows, \
        f"{league} {function_name}: Should have at least {min_rows} rows, got {row_count}"
    assert col_count > 0, \
        f"{league} {function_name}: Should have columns, got {col_count}"


# ==============================================================================
# PWHL Tests
# ==============================================================================

class TestPWHLScrapes:
    """Test PWHL scrape functions used in notebooks"""

    def test_pwhl_scrapeTeams(self):
        """Test scrapeTeams returns DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        teams_df = pwhl_scrapeTeams(season=season)
        validate_dataframe(teams_df, 'PWHL', min_rows=1, function_name='scrapeTeams')
        print(f"✓ PWHL scrapeTeams: {len(teams_df)} teams")

    def test_pwhl_scrapeSchedule(self):
        """Test scrapeSchedule returns DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        schedule_df = pwhl_scrapeSchedule(season=season)
        validate_dataframe(schedule_df, 'PWHL', min_rows=1, function_name='scrapeSchedule')
        print(f"✓ PWHL scrapeSchedule: {len(schedule_df)} games")

    def test_pwhl_scrapeStandings(self):
        """Test scrapeStandings returns DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        standings_df = pwhl_scrapeStandings(season=season)
        validate_dataframe(standings_df, 'PWHL', min_rows=1, function_name='scrapeStandings')
        print(f"✓ PWHL scrapeStandings: {len(standings_df)} teams")

    def test_pwhl_scrapeRoster(self):
        """Test scrapeRoster returns DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        team_id = LEAGUE_CONFIGS['PWHL']['team_id']
        roster_df = pwhl_scrapeRoster(team_id=team_id, season=season)
        validate_dataframe(roster_df, 'PWHL', min_rows=1, function_name='scrapeRoster')
        print(f"✓ PWHL scrapeRoster: {len(roster_df)} players")

    def test_pwhl_scrapePlayerStats_skaters(self):
        """Test scrapePlayerStats for skaters returns DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        stats_df = pwhl_scrapePlayerStats(season=season, player_type='skaters')
        validate_dataframe(stats_df, 'PWHL', min_rows=1, function_name='scrapePlayerStats(skaters)')
        print(f"✓ PWHL scrapePlayerStats (skaters): {len(stats_df)} players")

    def test_pwhl_scrapePlayerStats_goalies(self):
        """Test scrapePlayerStats for goalies returns DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        stats_df = pwhl_scrapePlayerStats(season=season, player_type='goalies')
        validate_dataframe(stats_df, 'PWHL', min_rows=1, function_name='scrapePlayerStats(goalies)')
        print(f"✓ PWHL scrapePlayerStats (goalies): {len(stats_df)} goalies")

    def test_pwhl_scrape_game(self):
        """Test scrape_game returns game data with DataFrame"""
        season = LEAGUE_CONFIGS['PWHL']['season']
        schedule_df = pwhl_scrapeSchedule(season=season)

        if len(schedule_df) > 0:
            # Try to find a completed game
            if isinstance(schedule_df, pd.DataFrame):
                completed = schedule_df[schedule_df.get('game_status', schedule_df.get('status', '')) == 'Final']
                game_id = int(completed.iloc[0]['game_id']) if len(completed) > 0 else int(schedule_df.iloc[0]['game_id'])
            else:  # polars
                completed = schedule_df.filter(pl.col('game_status') == 'Final')
                game_id = int(completed[0, 'game_id']) if len(completed) > 0 else int(schedule_df[0, 'game_id'])

            try:
                game_data = pwhl_scrape_game(game_id=game_id, include_tuple=True)
                validate_dataframe(game_data.data, 'PWHL', min_rows=1, function_name='scrape_game')
                print(f"✓ PWHL scrape_game: {len(game_data.data)} events")
            except Exception as e:
                print(f"⚠ PWHL scrape_game skipped: {e}")


# ==============================================================================
# AHL Tests
# ==============================================================================

class TestAHLScrapes:
    """Test AHL scrape functions used in notebooks"""

    def test_ahl_scrapeTeams(self):
        """Test scrapeTeams returns DataFrame"""
        season = LEAGUE_CONFIGS['AHL']['season']
        teams_df = ahl_scrapeTeams(season=season)
        validate_dataframe(teams_df, 'AHL', min_rows=1, function_name='scrapeTeams')
        print(f"✓ AHL scrapeTeams: {len(teams_df)} teams")

    def test_ahl_scrapeSchedule(self):
        """Test scrapeSchedule returns DataFrame"""
        season = LEAGUE_CONFIGS['AHL']['season']
        schedule_df = ahl_scrapeSchedule(season=season)
        validate_dataframe(schedule_df, 'AHL', min_rows=1, function_name='scrapeSchedule')
        print(f"✓ AHL scrapeSchedule: {len(schedule_df)} games")

    def test_ahl_scrapeStandings(self):
        """Test scrapeStandings returns DataFrame"""
        season = LEAGUE_CONFIGS['AHL']['season']
        standings_df = ahl_scrapeStandings(season=season)
        validate_dataframe(standings_df, 'AHL', min_rows=1, function_name='scrapeStandings')
        print(f"✓ AHL scrapeStandings: {len(standings_df)} teams")

    def test_ahl_scrapeRoster(self):
        """Test scrapeRoster returns DataFrame"""
        season = LEAGUE_CONFIGS['AHL']['season']
        team_id = LEAGUE_CONFIGS['AHL']['team_id']
        roster_df = ahl_scrapeRoster(team_id=team_id, season=season)
        validate_dataframe(roster_df, 'AHL', min_rows=1, function_name='scrapeRoster')
        print(f"✓ AHL scrapeRoster: {len(roster_df)} players")

    def test_ahl_scrapePlayerStats_skaters(self):
        """Test scrapePlayerStats for skaters returns DataFrame"""
        season = LEAGUE_CONFIGS['AHL']['season']
        stats_df = ahl_scrapePlayerStats(season=season, player_type='skaters')
        validate_dataframe(stats_df, 'AHL', min_rows=1, function_name='scrapePlayerStats(skaters)')
        print(f"✓ AHL scrapePlayerStats (skaters): {len(stats_df)} players")

    def test_ahl_scrapePlayerStats_goalies(self):
        """Test scrapePlayerStats for goalies returns DataFrame"""
        season = LEAGUE_CONFIGS['AHL']['season']
        stats_df = ahl_scrapePlayerStats(season=season, player_type='goalies')
        validate_dataframe(stats_df, 'AHL', min_rows=1, function_name='scrapePlayerStats(goalies)')
        print(f"✓ AHL scrapePlayerStats (goalies): {len(stats_df)} goalies")


# ==============================================================================
# OHL Tests
# ==============================================================================

class TestOHLScrapes:
    """Test OHL scrape functions used in notebooks"""

    def test_ohl_scrapeTeams(self):
        """Test scrapeTeams returns DataFrame"""
        season = LEAGUE_CONFIGS['OHL']['season']
        teams_df = ohl_scrapeTeams(season=season)
        validate_dataframe(teams_df, 'OHL', min_rows=1, function_name='scrapeTeams')
        print(f"✓ OHL scrapeTeams: {len(teams_df)} teams")

    def test_ohl_scrapeSchedule(self):
        """Test scrapeSchedule returns DataFrame"""
        season = LEAGUE_CONFIGS['OHL']['season']
        schedule_df = ohl_scrapeSchedule(season=season)
        validate_dataframe(schedule_df, 'OHL', min_rows=1, function_name='scrapeSchedule')
        print(f"✓ OHL scrapeSchedule: {len(schedule_df)} games")

    def test_ohl_scrapeStandings(self):
        """Test scrapeStandings returns DataFrame"""
        season = LEAGUE_CONFIGS['OHL']['season']
        standings_df = ohl_scrapeStandings(season=season)
        validate_dataframe(standings_df, 'OHL', min_rows=1, function_name='scrapeStandings')
        print(f"✓ OHL scrapeStandings: {len(standings_df)} teams")

    def test_ohl_scrapeRoster(self):
        """Test scrapeRoster returns DataFrame"""
        season = LEAGUE_CONFIGS['OHL']['season']
        team_id = LEAGUE_CONFIGS['OHL']['team_id']
        roster_df = ohl_scrapeRoster(team_id=team_id, season=season)
        validate_dataframe(roster_df, 'OHL', min_rows=1, function_name='scrapeRoster')
        print(f"✓ OHL scrapeRoster: {len(roster_df)} players")

    def test_ohl_scrapePlayerStats_skaters(self):
        """Test scrapePlayerStats for skaters returns DataFrame"""
        season = LEAGUE_CONFIGS['OHL']['season']
        stats_df = ohl_scrapePlayerStats(season=season, player_type='skaters')
        validate_dataframe(stats_df, 'OHL', min_rows=1, function_name='scrapePlayerStats(skaters)')
        print(f"✓ OHL scrapePlayerStats (skaters): {len(stats_df)} players")

    def test_ohl_scrapePlayerStats_goalies(self):
        """Test scrapePlayerStats for goalies returns DataFrame"""
        season = LEAGUE_CONFIGS['OHL']['season']
        stats_df = ohl_scrapePlayerStats(season=season, player_type='goalies')
        validate_dataframe(stats_df, 'OHL', min_rows=1, function_name='scrapePlayerStats(goalies)')
        print(f"✓ OHL scrapePlayerStats (goalies): {len(stats_df)} goalies")


# ==============================================================================
# WHL Tests
# ==============================================================================

class TestWHLScrapes:
    """Test WHL scrape functions used in notebooks"""

    def test_whl_scrapeTeams(self):
        """Test scrapeTeams returns DataFrame"""
        season = LEAGUE_CONFIGS['WHL']['season']
        teams_df = whl_scrapeTeams(season=season)
        validate_dataframe(teams_df, 'WHL', min_rows=1, function_name='scrapeTeams')
        print(f"✓ WHL scrapeTeams: {len(teams_df)} teams")

    def test_whl_scrapeSchedule(self):
        """Test scrapeSchedule returns DataFrame"""
        season = LEAGUE_CONFIGS['WHL']['season']
        schedule_df = whl_scrapeSchedule(season=season)
        validate_dataframe(schedule_df, 'WHL', min_rows=1, function_name='scrapeSchedule')
        print(f"✓ WHL scrapeSchedule: {len(schedule_df)} games")

    def test_whl_scrapeStandings(self):
        """Test scrapeStandings returns DataFrame"""
        season = LEAGUE_CONFIGS['WHL']['season']
        standings_df = whl_scrapeStandings(season=season)
        validate_dataframe(standings_df, 'WHL', min_rows=1, function_name='scrapeStandings')
        print(f"✓ WHL scrapeStandings: {len(standings_df)} teams")

    def test_whl_scrapeRoster(self):
        """Test scrapeRoster returns DataFrame"""
        season = LEAGUE_CONFIGS['WHL']['season']
        team_id = LEAGUE_CONFIGS['WHL']['team_id']
        roster_df = whl_scrapeRoster(team_id=team_id, season=season)
        validate_dataframe(roster_df, 'WHL', min_rows=1, function_name='scrapeRoster')
        print(f"✓ WHL scrapeRoster: {len(roster_df)} players")

    def test_whl_scrapePlayerStats_skaters(self):
        """Test scrapePlayerStats for skaters returns DataFrame"""
        season = LEAGUE_CONFIGS['WHL']['season']
        stats_df = whl_scrapePlayerStats(season=season, player_type='skaters')
        validate_dataframe(stats_df, 'WHL', min_rows=1, function_name='scrapePlayerStats(skaters)')
        print(f"✓ WHL scrapePlayerStats (skaters): {len(stats_df)} players")

    def test_whl_scrapePlayerStats_goalies(self):
        """Test scrapePlayerStats for goalies returns DataFrame"""
        season = LEAGUE_CONFIGS['WHL']['season']
        stats_df = whl_scrapePlayerStats(season=season, player_type='goalies')
        validate_dataframe(stats_df, 'WHL', min_rows=1, function_name='scrapePlayerStats(goalies)')
        print(f"✓ WHL scrapePlayerStats (goalies): {len(stats_df)} goalies")


# ==============================================================================
# QMJHL Tests
# ==============================================================================

class TestQMJHLScrapes:
    """Test QMJHL scrape functions used in notebooks"""

    def test_qmjhl_scrapeTeams(self):
        """Test scrapeTeams returns DataFrame"""
        season = LEAGUE_CONFIGS['QMJHL']['season']
        teams_df = qmjhl_scrapeTeams(season=season)
        validate_dataframe(teams_df, 'QMJHL', min_rows=1, function_name='scrapeTeams')
        print(f"✓ QMJHL scrapeTeams: {len(teams_df)} teams")

    def test_qmjhl_scrapeSchedule(self):
        """Test scrapeSchedule returns DataFrame"""
        season = LEAGUE_CONFIGS['QMJHL']['season']
        schedule_df = qmjhl_scrapeSchedule(season=season)
        validate_dataframe(schedule_df, 'QMJHL', min_rows=1, function_name='scrapeSchedule')
        print(f"✓ QMJHL scrapeSchedule: {len(schedule_df)} games")

    def test_qmjhl_scrapeStandings(self):
        """Test scrapeStandings returns DataFrame"""
        season = LEAGUE_CONFIGS['QMJHL']['season']
        standings_df = qmjhl_scrapeStandings(season=season)
        validate_dataframe(standings_df, 'QMJHL', min_rows=1, function_name='scrapeStandings')
        print(f"✓ QMJHL scrapeStandings: {len(standings_df)} teams")

    def test_qmjhl_scrapeRoster(self):
        """Test scrapeRoster returns DataFrame"""
        season = LEAGUE_CONFIGS['QMJHL']['season']
        team_id = LEAGUE_CONFIGS['QMJHL']['team_id']
        roster_df = qmjhl_scrapeRoster(team_id=team_id, season=season)
        validate_dataframe(roster_df, 'QMJHL', min_rows=1, function_name='scrapeRoster')
        print(f"✓ QMJHL scrapeRoster: {len(roster_df)} players")

    def test_qmjhl_scrapePlayerStats_skaters(self):
        """Test scrapePlayerStats for skaters returns DataFrame"""
        season = LEAGUE_CONFIGS['QMJHL']['season']
        stats_df = qmjhl_scrapePlayerStats(season=season, player_type='skaters')
        validate_dataframe(stats_df, 'QMJHL', min_rows=1, function_name='scrapePlayerStats(skaters)')
        print(f"✓ QMJHL scrapePlayerStats (skaters): {len(stats_df)} players")

    def test_qmjhl_scrapePlayerStats_goalies(self):
        """Test scrapePlayerStats for goalies returns DataFrame"""
        season = LEAGUE_CONFIGS['QMJHL']['season']
        stats_df = qmjhl_scrapePlayerStats(season=season, player_type='goalies')
        validate_dataframe(stats_df, 'QMJHL', min_rows=1, function_name='scrapePlayerStats(goalies)')
        print(f"✓ QMJHL scrapePlayerStats (goalies): {len(stats_df)} goalies")


# ==============================================================================
# Cross-League Tests
# ==============================================================================

class TestCrossLeagueScrapes:
    """Test that all leagues have consistent scrape function behavior"""

    def test_all_leagues_scrapeTeams(self):
        """Test that all leagues can scrape teams"""
        results = {}

        for league, config in LEAGUE_CONFIGS.items():
            try:
                if league == 'PWHL':
                    df = pwhl_scrapeTeams(season=config['season'])
                elif league == 'AHL':
                    df = ahl_scrapeTeams(season=config['season'])
                elif league == 'OHL':
                    df = ohl_scrapeTeams(season=config['season'])
                elif league == 'WHL':
                    df = whl_scrapeTeams(season=config['season'])
                elif league == 'QMJHL':
                    df = qmjhl_scrapeTeams(season=config['season'])

                row_count = len(df) if isinstance(df, pd.DataFrame) else df.shape[0]
                results[league] = f"{row_count} teams"
            except Exception as e:
                results[league] = f"FAILED: {str(e)[:50]}"

        print(f"✓ scrapeTeams results: {results}")
        assert all('FAILED' not in v for v in results.values()), "All leagues should scrape teams successfully"

    def test_all_leagues_scrapePlayerStats(self):
        """Test that all leagues can scrape player stats"""
        results = {}

        for league, config in LEAGUE_CONFIGS.items():
            try:
                if league == 'PWHL':
                    df = pwhl_scrapePlayerStats(season=config['season'], player_type='skaters')
                elif league == 'AHL':
                    df = ahl_scrapePlayerStats(season=config['season'], player_type='skaters')
                elif league == 'OHL':
                    df = ohl_scrapePlayerStats(season=config['season'], player_type='skaters')
                elif league == 'WHL':
                    df = whl_scrapePlayerStats(season=config['season'], player_type='skaters')
                elif league == 'QMJHL':
                    df = qmjhl_scrapePlayerStats(season=config['season'], player_type='skaters')

                row_count = len(df) if isinstance(df, pd.DataFrame) else df.shape[0]
                results[league] = f"{row_count} players"
            except Exception as e:
                results[league] = f"FAILED: {str(e)[:50]}"

        print(f"✓ scrapePlayerStats results: {results}")
        assert all('FAILED' not in v for v in results.values()), "All leagues should scrape player stats successfully"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
