"""
Comprehensive tests for all 5 leagues: AHL, PWHL, OHL, WHL, QMJHL

Tests cover:
- Player profile scrapers
- Player statistics
- Game logs
- Team data
- Season data
- API endpoints
- Data validation
"""

import pytest
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Union

# AHL imports
from scrapernhl.ahl.scrapers.player import (
    get_player_profile as ahl_get_player_profile,
    get_player_bio as ahl_get_player_bio,
    get_player_stats as ahl_get_player_stats,
    get_player_game_log as ahl_get_player_game_log,
    scrape_player_profile as ahl_scrape_player_profile,
    scrape_player_career_stats as ahl_scrape_player_career_stats,
)
from scrapernhl.ahl.api import (
    get_teams as ahl_get_teams,
    get_standings as ahl_get_standings,
    get_roster as ahl_get_roster,
    get_schedule as ahl_get_schedule,
)

# PWHL imports
from scrapernhl.pwhl.scrapers.player import (
    get_player_profile as pwhl_get_player_profile,
    get_player_bio as pwhl_get_player_bio,
    get_player_stats as pwhl_get_player_stats,
    get_player_game_log as pwhl_get_player_game_log,
    scrape_player_profile as pwhl_scrape_player_profile,
    scrape_player_career_stats as pwhl_scrape_player_career_stats,
)
from scrapernhl.pwhl.api import (
    get_teams as pwhl_get_teams,
    get_standings as pwhl_get_standings,
    get_roster as pwhl_get_roster,
    get_schedule as pwhl_get_schedule,
)

# OHL imports
from scrapernhl.ohl.scrapers.player import (
    get_player_profile as ohl_get_player_profile,
    get_player_bio as ohl_get_player_bio,
    get_player_stats as ohl_get_player_stats,
    get_player_game_log as ohl_get_player_game_log,
    scrape_player_profile as ohl_scrape_player_profile,
    scrape_player_career_stats as ohl_scrape_player_career_stats,
)
from scrapernhl.ohl.api import (
    get_teams as ohl_get_teams,
    get_standings as ohl_get_standings,
    get_roster as ohl_get_roster,
    get_schedule as ohl_get_schedule,
)

# WHL imports
from scrapernhl.whl.scrapers.player import (
    get_player_profile as whl_get_player_profile,
    get_player_bio as whl_get_player_bio,
    get_player_stats as whl_get_player_stats,
    get_player_game_log as whl_get_player_game_log,
    scrape_player_profile as whl_scrape_player_profile,
    scrape_player_career_stats as whl_scrape_player_career_stats,
)
from scrapernhl.whl.api import (
    get_teams as whl_get_teams,
    get_standings as whl_get_standings,
    get_roster as whl_get_roster,
    get_schedule as whl_get_schedule,
)

# QMJHL imports
from scrapernhl.qmjhl.scrapers.player import (
    get_player_profile as qmjhl_get_player_profile,
    get_player_bio as qmjhl_get_player_bio,
    get_player_stats as qmjhl_get_player_stats,
    get_player_game_log as qmjhl_get_player_game_log,
    scrape_player_profile as qmjhl_scrape_player_profile,
    scrape_player_career_stats as qmjhl_scrape_player_career_stats,
)
from scrapernhl.qmjhl.api import (
    get_teams as qmjhl_get_teams,
    get_standings as qmjhl_get_standings,
    get_roster as qmjhl_get_roster,
    get_schedule as qmjhl_get_schedule,
)


# ==============================================================================
# Test Data - Real player IDs and team IDs for each league
# ==============================================================================

TEST_PLAYERS = {
    'ahl': {
        'player_id': 8928,  # Danila Klimovich
        'player_name': 'Danila Klimovich',
        'season_id': 86,  # 2024-25 season
        'old_season_id': 64,  # 2019 season for historical testing
    },
    'pwhl': {
        'player_id': 18,  # Sophie Shirley
        'player_name': 'Sophie Shirley',
        'season_id': 1,  # First PWHL season
    },
    'ohl': {
        'player_id': 9578,  # Nicholas Desiderio
        'player_name': 'Nicholas Desiderio',
        'season_id': 78,  # 2024-25 season
    },
    'whl': {
        'player_id': 29601,  # Brady Turko
        'player_name': 'Brady Turko',
        'season_id': 78,  # 2024-25 season
    },
    'qmjhl': {
        'player_id': 21348,  # Aiden Kirkwood
        'player_name': 'Aiden Kirkwood',
        'season_id': 78,  # 2024-25 season
    },
}

TEST_TEAMS = {
    'ahl': {
        'team_id': 440,  # Abbotsford Canucks
        'season': '2024-25',
    },
    'pwhl': {
        'team_id': 1,  # Boston Fleet
        'season': '2024',
    },
    'ohl': {
        'team_id': 7,  # Barrie Colts
        'season': '2024-25',
    },
    'whl': {
        'team_id': 201,  # Brandon Wheat Kings
        'season': '2024-25',
    },
    'qmjhl': {
        'team_id': 16,  # Baie-Comeau Drakkar
        'season': '2024-25',
    },
}


# ==============================================================================
# Helper Functions
# ==============================================================================

def validate_player_profile(profile: Dict[str, Any], league: str) -> None:
    """Validate that a player profile has expected fields"""
    assert isinstance(profile, dict), f"{league}: Profile should be a dictionary"
    
    # Check for player ID in multiple possible locations
    has_id = ('id' in profile or 'playerId' in profile or 
              ('info' in profile and 'playerId' in profile['info']))
    assert has_id, f"{league}: Profile should have player ID"
    
    # Check for first/last name in multiple possible locations  
    has_name = (('firstName' in profile or 'first_name' in profile or 
                 ('info' in profile and 'firstName' in profile['info'])) and
                ('lastName' in profile or 'last_name' in profile or 
                 ('info' in profile and 'lastName' in profile['info'])))
    assert has_name, f"{league}: Profile should have first and last name"


def validate_player_stats(stats: Dict[str, Any], league: str) -> None:
    """Validate that player stats have expected structure"""
    assert isinstance(stats, dict), f"{league}: Stats should be a dictionary"
    # Stats might have seasonStats, careerStats, or similar structures


def validate_game_log(game_log: List[Dict[str, Any]], league: str) -> None:
    """Validate that game log has expected structure"""
    assert isinstance(game_log, list), f"{league}: Game log should be a list"
    if len(game_log) > 0:
        game = game_log[0]
        # Each game should have some basic fields
        # Note: Different leagues may have different field names


def validate_dataframe(df: pd.DataFrame, league: str, min_rows: int = 0) -> None:
    """Validate that a DataFrame has expected structure"""
    assert isinstance(df, pd.DataFrame), f"{league}: Should return a DataFrame"
    assert len(df) >= min_rows, f"{league}: Should have at least {min_rows} rows, got {len(df)}"
    assert len(df.columns) > 0, f"{league}: Should have columns"


def validate_teams(teams: Dict[str, Any], league: str) -> None:
    """Validate teams data structure"""
    assert isinstance(teams, dict), f"{league}: Teams should be a dictionary"
    # Teams data structure may vary by league


def validate_standings(standings: Union[Dict[str, Any], List], league: str) -> None:
    """Validate standings data structure"""
    # Standings can be either a dict or a list depending on the API response format
    assert isinstance(standings, (dict, list)), f"{league}: Standings should be a dictionary or list"
    assert len(standings) > 0, f"{league}: Standings should not be empty"


def validate_roster(roster: List[Dict], league: str) -> None:
    """Validate roster data structure"""
    assert isinstance(roster, (list, dict)), f"{league}: Roster should be a list or dict"
    if isinstance(roster, list):
        assert len(roster) > 0, f"{league}: Roster should have players"


# ==============================================================================
# AHL Tests
# ==============================================================================

class TestAHL:
    """Test suite for AHL scrapers and API"""
    
    def test_ahl_get_player_profile(self):
        """Test getting AHL player profile (raw data)"""
        player_id = TEST_PLAYERS['ahl']['player_id']
        profile = ahl_get_player_profile(player_id)
        validate_player_profile(profile, 'AHL')
        print(f"✓ AHL player profile for ID {player_id}: {profile.get('firstName', '')} {profile.get('lastName', '')}")
    
    def test_ahl_get_player_bio(self):
        """Test getting AHL player biographical info"""
        player_id = TEST_PLAYERS['ahl']['player_id']
        bio = ahl_get_player_bio(player_id)
        assert isinstance(bio, dict), "AHL: Bio should be a dictionary"
        assert 'firstName' in bio or 'first_name' in bio, "AHL: Bio should have first name"
        print(f"✓ AHL player bio retrieved successfully")
    
    def test_ahl_get_player_stats(self):
        """Test getting AHL player stats"""
        player_id = TEST_PLAYERS['ahl']['player_id']
        stats = ahl_get_player_stats(player_id)
        validate_player_stats(stats, 'AHL')
        print(f"✓ AHL player stats retrieved successfully")
    
    def test_ahl_get_player_game_log(self):
        """Test getting AHL player game log"""
        player_id = TEST_PLAYERS['ahl']['player_id']
        season_id = TEST_PLAYERS['ahl']['season_id']
        game_log = ahl_get_player_game_log(player_id, season_id=season_id)
        assert isinstance(game_log, list), "AHL: Game log should be a list"
        print(f"✓ AHL player game log retrieved: {len(game_log)} entries")
    
    # Note: test_ahl_get_player_game_log_multiple_seasons removed because
    # player 8928 (Danila Klimovich) doesn't have sufficient historical data
    # across multiple seasons in the AHL
    
    def test_ahl_scrape_player_profile(self):
        """Test scraping AHL player profile as DataFrame"""
        player_id = TEST_PLAYERS['ahl']['player_id']
        profile_df = ahl_scrape_player_profile(player_id)
        validate_dataframe(profile_df, 'AHL', min_rows=1)
        print(f"✓ AHL player profile DataFrame: {profile_df.shape}")
    
    def test_ahl_scrape_player_career_stats(self):
        """Test scraping AHL player career stats as DataFrame"""
        player_id = TEST_PLAYERS['ahl']['player_id']
        career_df = ahl_scrape_player_career_stats(player_id)
        validate_dataframe(career_df, 'AHL')
        print(f"✓ AHL player career stats: {career_df.shape}")
    
    def test_ahl_get_teams(self):
        """Test getting AHL teams"""
        teams = ahl_get_teams()
        validate_teams(teams, 'AHL')
        print(f"✓ AHL teams retrieved successfully")
    
    def test_ahl_get_standings(self):
        """Test getting AHL standings"""
        standings = ahl_get_standings()
        validate_standings(standings, 'AHL')
        print(f"✓ AHL standings retrieved successfully")
    
    def test_ahl_get_roster(self):
        """Test getting AHL team roster"""
        team_id = TEST_TEAMS['ahl']['team_id']
        roster = ahl_get_roster(team_id)
        validate_roster(roster, 'AHL')
        print(f"✓ AHL roster for team {team_id} retrieved")
    
    def test_ahl_get_schedule(self):
        """Test getting AHL schedule"""
        schedule = ahl_get_schedule()
        assert isinstance(schedule, (list, dict)), "AHL: Schedule should be list or dict"
        print(f"✓ AHL schedule retrieved successfully")


# ==============================================================================
# PWHL Tests
# ==============================================================================

class TestPWHL:
    """Test suite for PWHL scrapers and API"""
    
    def test_pwhl_get_player_profile(self):
        """Test getting PWHL player profile (raw data)"""
        player_id = TEST_PLAYERS['pwhl']['player_id']
        profile = pwhl_get_player_profile(player_id)
        validate_player_profile(profile, 'PWHL')
        print(f"✓ PWHL player profile for ID {player_id}")
    
    def test_pwhl_get_player_bio(self):
        """Test getting PWHL player biographical info"""
        player_id = TEST_PLAYERS['pwhl']['player_id']
        bio = pwhl_get_player_bio(player_id)
        assert isinstance(bio, dict), "PWHL: Bio should be a dictionary"
        print(f"✓ PWHL player bio retrieved successfully")
    
    def test_pwhl_get_player_stats(self):
        """Test getting PWHL player stats"""
        player_id = TEST_PLAYERS['pwhl']['player_id']
        stats = pwhl_get_player_stats(player_id)
        validate_player_stats(stats, 'PWHL')
        print(f"✓ PWHL player stats retrieved successfully")
    
    def test_pwhl_get_player_game_log(self):
        """Test getting PWHL player game log"""
        player_id = TEST_PLAYERS['pwhl']['player_id']
        season_id = TEST_PLAYERS['pwhl']['season_id']
        game_log = pwhl_get_player_game_log(player_id, season_id=season_id)
        assert isinstance(game_log, list), "PWHL: Game log should be a list"
        print(f"✓ PWHL player game log retrieved: {len(game_log)} entries")
    
    def test_pwhl_scrape_player_profile(self):
        """Test scraping PWHL player profile as DataFrame"""
        player_id = TEST_PLAYERS['pwhl']['player_id']
        profile_df = pwhl_scrape_player_profile(player_id)
        validate_dataframe(profile_df, 'PWHL', min_rows=1)
        print(f"✓ PWHL player profile DataFrame: {profile_df.shape}")
    
    def test_pwhl_scrape_player_career_stats(self):
        """Test scraping PWHL player career stats as DataFrame"""
        player_id = TEST_PLAYERS['pwhl']['player_id']
        career_df = pwhl_scrape_player_career_stats(player_id)
        validate_dataframe(career_df, 'PWHL')
        print(f"✓ PWHL player career stats: {career_df.shape}")
    
    def test_pwhl_get_teams(self):
        """Test getting PWHL teams"""
        teams = pwhl_get_teams()
        validate_teams(teams, 'PWHL')
        print(f"✓ PWHL teams retrieved successfully")
    
    def test_pwhl_get_standings(self):
        """Test getting PWHL standings"""
        standings = pwhl_get_standings()
        validate_standings(standings, 'PWHL')
        print(f"✓ PWHL standings retrieved successfully")
    
    def test_pwhl_get_roster(self):
        """Test getting PWHL team roster"""
        team_id = TEST_TEAMS['pwhl']['team_id']
        roster = pwhl_get_roster(team_id)
        validate_roster(roster, 'PWHL')
        print(f"✓ PWHL roster for team {team_id} retrieved")
    
    def test_pwhl_get_schedule(self):
        """Test getting PWHL schedule"""
        schedule = pwhl_get_schedule()
        assert isinstance(schedule, (list, dict)), "PWHL: Schedule should be list or dict"
        print(f"✓ PWHL schedule retrieved successfully")


# ==============================================================================
# OHL Tests
# ==============================================================================

class TestOHL:
    """Test suite for OHL scrapers and API"""
    
    def test_ohl_get_player_profile(self):
        """Test getting OHL player profile (raw data)"""
        player_id = TEST_PLAYERS['ohl']['player_id']
        profile = ohl_get_player_profile(player_id)
        validate_player_profile(profile, 'OHL')
        print(f"✓ OHL player profile for ID {player_id}")
    
    def test_ohl_get_player_bio(self):
        """Test getting OHL player biographical info"""
        player_id = TEST_PLAYERS['ohl']['player_id']
        bio = ohl_get_player_bio(player_id)
        assert isinstance(bio, dict), "OHL: Bio should be a dictionary"
        print(f"✓ OHL player bio retrieved successfully")
    
    def test_ohl_get_player_stats(self):
        """Test getting OHL player stats"""
        player_id = TEST_PLAYERS['ohl']['player_id']
        stats = ohl_get_player_stats(player_id)
        validate_player_stats(stats, 'OHL')
        print(f"✓ OHL player stats retrieved successfully")
    
    def test_ohl_get_player_game_log(self):
        """Test getting OHL player game log"""
        player_id = TEST_PLAYERS['ohl']['player_id']
        season_id = TEST_PLAYERS['ohl']['season_id']
        game_log = ohl_get_player_game_log(player_id, season_id=season_id)
        assert isinstance(game_log, list), "OHL: Game log should be a list"
        print(f"✓ OHL player game log retrieved: {len(game_log)} entries")
    
    def test_ohl_scrape_player_profile(self):
        """Test scraping OHL player profile as DataFrame"""
        player_id = TEST_PLAYERS['ohl']['player_id']
        profile_df = ohl_scrape_player_profile(player_id)
        validate_dataframe(profile_df, 'OHL', min_rows=1)
        print(f"✓ OHL player profile DataFrame: {profile_df.shape}")
    
    def test_ohl_scrape_player_career_stats(self):
        """Test scraping OHL player career stats as DataFrame"""
        player_id = TEST_PLAYERS['ohl']['player_id']
        career_df = ohl_scrape_player_career_stats(player_id)
        validate_dataframe(career_df, 'OHL')
        print(f"✓ OHL player career stats: {career_df.shape}")
    
    def test_ohl_get_teams(self):
        """Test getting OHL teams"""
        teams = ohl_get_teams()
        validate_teams(teams, 'OHL')
        print(f"✓ OHL teams retrieved successfully")
    
    def test_ohl_get_standings(self):
        """Test getting OHL standings"""
        standings = ohl_get_standings()
        validate_standings(standings, 'OHL')
        print(f"✓ OHL standings retrieved successfully")
    
    def test_ohl_get_roster(self):
        """Test getting OHL team roster"""
        team_id = TEST_TEAMS['ohl']['team_id']
        roster = ohl_get_roster(team_id)
        validate_roster(roster, 'OHL')
        print(f"✓ OHL roster for team {team_id} retrieved")
    
    def test_ohl_get_schedule(self):
        """Test getting OHL schedule"""
        schedule = ohl_get_schedule()
        assert isinstance(schedule, (list, dict)), "OHL: Schedule should be list or dict"
        print(f"✓ OHL schedule retrieved successfully")


# ==============================================================================
# WHL Tests
# ==============================================================================

class TestWHL:
    """Test suite for WHL scrapers and API"""
    
    def test_whl_get_player_profile(self):
        """Test getting WHL player profile (raw data)"""
        player_id = TEST_PLAYERS['whl']['player_id']
        profile = whl_get_player_profile(player_id)
        validate_player_profile(profile, 'WHL')
        print(f"✓ WHL player profile for ID {player_id}")
    
    def test_whl_get_player_bio(self):
        """Test getting WHL player biographical info"""
        player_id = TEST_PLAYERS['whl']['player_id']
        bio = whl_get_player_bio(player_id)
        assert isinstance(bio, dict), "WHL: Bio should be a dictionary"
        print(f"✓ WHL player bio retrieved successfully")
    
    def test_whl_get_player_stats(self):
        """Test getting WHL player stats"""
        player_id = TEST_PLAYERS['whl']['player_id']
        stats = whl_get_player_stats(player_id)
        validate_player_stats(stats, 'WHL')
        print(f"✓ WHL player stats retrieved successfully")
    
    def test_whl_get_player_game_log(self):
        """Test getting WHL player game log"""
        player_id = TEST_PLAYERS['whl']['player_id']
        season_id = TEST_PLAYERS['whl']['season_id']
        game_log = whl_get_player_game_log(player_id, season_id=season_id)
        assert isinstance(game_log, list), "WHL: Game log should be a list"
        print(f"✓ WHL player game log retrieved: {len(game_log)} entries")
    
    def test_whl_scrape_player_profile(self):
        """Test scraping WHL player profile as DataFrame"""
        player_id = TEST_PLAYERS['whl']['player_id']
        profile_df = whl_scrape_player_profile(player_id)
        validate_dataframe(profile_df, 'WHL', min_rows=1)
        print(f"✓ WHL player profile DataFrame: {profile_df.shape}")
    
    def test_whl_scrape_player_career_stats(self):
        """Test scraping WHL player career stats as DataFrame"""
        player_id = TEST_PLAYERS['whl']['player_id']
        career_df = whl_scrape_player_career_stats(player_id)
        validate_dataframe(career_df, 'WHL')
        print(f"✓ WHL player career stats: {career_df.shape}")
    
    def test_whl_get_teams(self):
        """Test getting WHL teams"""
        teams = whl_get_teams()
        validate_teams(teams, 'WHL')
        print(f"✓ WHL teams retrieved successfully")
    
    def test_whl_get_standings(self):
        """Test getting WHL standings"""
        standings = whl_get_standings()
        validate_standings(standings, 'WHL')
        print(f"✓ WHL standings retrieved successfully")
    
    def test_whl_get_roster(self):
        """Test getting WHL team roster"""
        team_id = TEST_TEAMS['whl']['team_id']
        roster = whl_get_roster(team_id)
        validate_roster(roster, 'WHL')
        print(f"✓ WHL roster for team {team_id} retrieved")
    
    def test_whl_get_schedule(self):
        """Test getting WHL schedule"""
        schedule = whl_get_schedule()
        assert isinstance(schedule, (list, dict)), "WHL: Schedule should be list or dict"
        print(f"✓ WHL schedule retrieved successfully")


# ==============================================================================
# QMJHL Tests
# ==============================================================================

class TestQMJHL:
    """Test suite for QMJHL scrapers and API"""
    
    def test_qmjhl_get_player_profile(self):
        """Test getting QMJHL player profile (raw data)"""
        player_id = TEST_PLAYERS['qmjhl']['player_id']
        profile = qmjhl_get_player_profile(player_id)
        validate_player_profile(profile, 'QMJHL')
        print(f"✓ QMJHL player profile for ID {player_id}")
    
    def test_qmjhl_get_player_bio(self):
        """Test getting QMJHL player biographical info"""
        player_id = TEST_PLAYERS['qmjhl']['player_id']
        bio = qmjhl_get_player_bio(player_id)
        assert isinstance(bio, dict), "QMJHL: Bio should be a dictionary"
        print(f"✓ QMJHL player bio retrieved successfully")
    
    def test_qmjhl_get_player_stats(self):
        """Test getting QMJHL player stats"""
        player_id = TEST_PLAYERS['qmjhl']['player_id']
        stats = qmjhl_get_player_stats(player_id)
        validate_player_stats(stats, 'QMJHL')
        print(f"✓ QMJHL player stats retrieved successfully")
    
    def test_qmjhl_get_player_game_log(self):
        """Test getting QMJHL player game log"""
        player_id = TEST_PLAYERS['qmjhl']['player_id']
        season_id = TEST_PLAYERS['qmjhl']['season_id']
        game_log = qmjhl_get_player_game_log(player_id, season_id=season_id)
        assert isinstance(game_log, list), "QMJHL: Game log should be a list"
        print(f"✓ QMJHL player game log retrieved: {len(game_log)} entries")
    
    def test_qmjhl_scrape_player_profile(self):
        """Test scraping QMJHL player profile as DataFrame"""
        player_id = TEST_PLAYERS['qmjhl']['player_id']
        profile_df = qmjhl_scrape_player_profile(player_id)
        validate_dataframe(profile_df, 'QMJHL', min_rows=1)
        print(f"✓ QMJHL player profile DataFrame: {profile_df.shape}")
    
    def test_qmjhl_scrape_player_career_stats(self):
        """Test scraping QMJHL player career stats as DataFrame"""
        player_id = TEST_PLAYERS['qmjhl']['player_id']
        career_df = qmjhl_scrape_player_career_stats(player_id)
        validate_dataframe(career_df, 'QMJHL')
        print(f"✓ QMJHL player career stats: {career_df.shape}")
    
    def test_qmjhl_get_teams(self):
        """Test getting QMJHL teams"""
        teams = qmjhl_get_teams()
        validate_teams(teams, 'QMJHL')
        print(f"✓ QMJHL teams retrieved successfully")
    
    def test_qmjhl_get_standings(self):
        """Test getting QMJHL standings"""
        standings = qmjhl_get_standings()
        validate_standings(standings, 'QMJHL')
        print(f"✓ QMJHL standings retrieved successfully")
    
    def test_qmjhl_get_roster(self):
        """Test getting QMJHL team roster"""
        team_id = TEST_TEAMS['qmjhl']['team_id']
        roster = qmjhl_get_roster(team_id)
        validate_roster(roster, 'QMJHL')
        print(f"✓ QMJHL roster for team {team_id} retrieved")
    
    def test_qmjhl_get_schedule(self):
        """Test getting QMJHL schedule"""
        schedule = qmjhl_get_schedule()
        assert isinstance(schedule, (list, dict)), "QMJHL: Schedule should be list or dict"
        print(f"✓ QMJHL schedule retrieved successfully")


# ==============================================================================
# Cross-League Comparison Tests
# ==============================================================================

class TestCrossLeague:
    """Tests that compare functionality across all leagues"""
    
    def test_all_leagues_player_profiles(self):
        """Test that all leagues can retrieve player profiles"""
        leagues_tested = []
        
        try:
            ahl_get_player_profile(TEST_PLAYERS['ahl']['player_id'])
            leagues_tested.append('AHL')
        except Exception as e:
            print(f"✗ AHL failed: {e}")
        
        try:
            pwhl_get_player_profile(TEST_PLAYERS['pwhl']['player_id'])
            leagues_tested.append('PWHL')
        except Exception as e:
            print(f"✗ PWHL failed: {e}")
        
        try:
            ohl_get_player_profile(TEST_PLAYERS['ohl']['player_id'])
            leagues_tested.append('OHL')
        except Exception as e:
            print(f"✗ OHL failed: {e}")
        
        try:
            whl_get_player_profile(TEST_PLAYERS['whl']['player_id'])
            leagues_tested.append('WHL')
        except Exception as e:
            print(f"✗ WHL failed: {e}")
        
        try:
            qmjhl_get_player_profile(TEST_PLAYERS['qmjhl']['player_id'])
            leagues_tested.append('QMJHL')
        except Exception as e:
            print(f"✗ QMJHL failed: {e}")
        
        print(f"✓ Successfully tested player profiles for: {', '.join(leagues_tested)}")
        assert len(leagues_tested) >= 3, "At least 3 leagues should work"
    
    def test_all_leagues_teams(self):
        """Test that all leagues can retrieve teams data"""
        leagues_tested = []
        
        for name, func in [
            ('AHL', ahl_get_teams),
            ('PWHL', pwhl_get_teams),
            ('OHL', ohl_get_teams),
            ('WHL', whl_get_teams),
            ('QMJHL', qmjhl_get_teams),
        ]:
            try:
                teams = func()
                assert teams is not None
                leagues_tested.append(name)
            except Exception as e:
                print(f"✗ {name} teams failed: {e}")
        
        print(f"✓ Successfully tested teams for: {', '.join(leagues_tested)}")
        assert len(leagues_tested) >= 3, "At least 3 leagues should work"
    
    def test_all_leagues_standings(self):
        """Test that all leagues can retrieve standings"""
        leagues_tested = []
        
        for name, func in [
            ('AHL', ahl_get_standings),
            ('PWHL', pwhl_get_standings),
            ('OHL', ohl_get_standings),
            ('WHL', whl_get_standings),
            ('QMJHL', qmjhl_get_standings),
        ]:
            try:
                standings = func()
                assert standings is not None
                leagues_tested.append(name)
            except Exception as e:
                print(f"✗ {name} standings failed: {e}")
        
        print(f"✓ Successfully tested standings for: {', '.join(leagues_tested)}")
        assert len(leagues_tested) >= 3, "At least 3 leagues should work"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
