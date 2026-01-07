#!/usr/bin/env python3
"""
Test to verify that strength labels are correctly mirrored for the second team alphabetically.
This test validates the fix for the bug where the 2nd team (by alphabetical order) was getting
the mirror of the desired game state in their stats.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapernhl import on_ice_stats_by_player_strength, team_strength_aggregates


def create_test_pbp_data():
    """
    Create test play-by-play data simulating a game between OTT and WPG.
    OTT is alphabetically first, WPG is second.
    
    Scenario:
    - At time 0: Both teams have 5 skaters and 1 goalie on ice (5v5)
    - At time 100: OTT player goes to penalty box (4v5 from OTT's perspective, 5v4 from WPG's)
    - At time 220: OTT player returns from penalty box (back to 5v5)
    - At time 300: Game ends
    """
    
    events = []
    
    # Initial ON events at time 0 - OTT players
    for i in range(1, 6):  # 5 skaters
        events.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'eventTeam': 'OTT',
            'player1Id': i,
            'player1Name': f'OTT_Player_{i}',
            'isGoalie': 0
        })
    events.append({  # 1 goalie
        'Event': 'ON',
        'elapsedTime': 0,
        'eventTeam': 'OTT',
        'player1Id': 100,
        'player1Name': 'OTT_Goalie',
        'isGoalie': 1
    })
    
    # Initial ON events at time 0 - WPG players
    for i in range(11, 16):  # 5 skaters
        events.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'eventTeam': 'WPG',
            'player1Id': i,
            'player1Name': f'WPG_Player_{i}',
            'isGoalie': 0
        })
    events.append({  # 1 goalie
        'Event': 'ON',
        'elapsedTime': 0,
        'eventTeam': 'WPG',
        'player1Id': 200,
        'player1Name': 'WPG_Goalie',
        'isGoalie': 1
    })
    
    # At time 100: OTT takes a penalty
    events.append({
        'Event': 'PENL',
        'elapsedTime': 100,
        'eventTeam': 'OTT',
        'player1Id': None,
        'player1Name': None,
        'isGoalie': None
    })
    
    # OTT player goes OFF at time 100
    events.append({
        'Event': 'OFF',
        'elapsedTime': 100,
        'eventTeam': 'OTT',
        'player1Id': 5,
        'player1Name': 'OTT_Player_5',
        'isGoalie': 0
    })
    
    # At time 120: Shot by WPG during power play
    events.append({
        'Event': 'SHOT',
        'elapsedTime': 120,
        'eventTeam': 'WPG',
        'xG': 0.2
    })
    
    # At time 220: OTT player returns from penalty box
    events.append({
        'Event': 'ON',
        'elapsedTime': 220,
        'eventTeam': 'OTT',
        'player1Id': 5,
        'player1Name': 'OTT_Player_5',
        'isGoalie': 0
    })
    
    # Game ends at time 300
    
    return pd.DataFrame(events)


def test_team_strength_aggregates():
    """Test that team_strength_aggregates produces correct mirrored strengths."""
    print("\n" + "="*60)
    print("Testing team_strength_aggregates...")
    print("="*60)
    
    pbp = create_test_pbp_data()
    result = team_strength_aggregates(pbp)
    
    print("\nTeam Strength Aggregates Result:")
    print(result[['team', 'opp', 'strength', 'seconds', 'SF', 'SA']].to_string())
    
    # Extract relevant rows
    ott_5v5 = result[(result['team'] == 'OTT') & (result['strength'] == '5v5')]
    ott_4v5 = result[(result['team'] == 'OTT') & (result['strength'] == '4v5')]
    wpg_5v5 = result[(result['team'] == 'WPG') & (result['strength'] == '5v5')]
    wpg_5v4 = result[(result['team'] == 'WPG') & (result['strength'] == '5v4')]
    
    # Validate
    errors = []
    
    # OTT should have 100 seconds at 5v5 (0 to 100)
    if not ott_5v5.empty:
        ott_5v5_seconds = ott_5v5.iloc[0]['seconds']
        if abs(ott_5v5_seconds - 100) > 0.1:
            errors.append(f"OTT 5v5: Expected ~100 seconds, got {ott_5v5_seconds}")
    else:
        errors.append("OTT 5v5 row is missing")
    
    # OTT should have 120 seconds at 4v5 (100 to 220) - penalty kill
    if not ott_4v5.empty:
        ott_4v5_seconds = ott_4v5.iloc[0]['seconds']
        if abs(ott_4v5_seconds - 120) > 0.1:
            errors.append(f"OTT 4v5: Expected ~120 seconds, got {ott_4v5_seconds}")
        # OTT should have 1 shot against during penalty kill
        ott_4v5_sa = ott_4v5.iloc[0]['SA']
        if ott_4v5_sa != 1:
            errors.append(f"OTT 4v5 SA: Expected 1 shot against, got {ott_4v5_sa}")
    else:
        errors.append("OTT 4v5 row is missing")
    
    # WPG should have 100 seconds at 5v5 (0 to 100)
    if not wpg_5v5.empty:
        wpg_5v5_seconds = wpg_5v5.iloc[0]['seconds']
        if abs(wpg_5v5_seconds - 100) > 0.1:
            errors.append(f"WPG 5v5: Expected ~100 seconds, got {wpg_5v5_seconds}")
    else:
        errors.append("WPG 5v5 row is missing")
    
    # WPG should have 120 seconds at 5v4 (100 to 220) - power play
    if not wpg_5v4.empty:
        wpg_5v4_seconds = wpg_5v4.iloc[0]['seconds']
        if abs(wpg_5v4_seconds - 120) > 0.1:
            errors.append(f"WPG 5v4: Expected ~120 seconds, got {wpg_5v4_seconds}")
        # WPG should have 1 shot for during power play
        wpg_5v4_sf = wpg_5v4.iloc[0]['SF']
        if wpg_5v4_sf != 1:
            errors.append(f"WPG 5v4 SF: Expected 1 shot for, got {wpg_5v4_sf}")
    else:
        errors.append("WPG 5v4 row is missing")
    
    # Check that OTT doesn't have 5v4 time (the bug would give them this)
    ott_5v4 = result[(result['team'] == 'OTT') & (result['strength'] == '5v4')]
    if not ott_5v4.empty:
        errors.append(f"FAILED: OTT should NOT have 5v4 time, but has {ott_5v4.iloc[0]['seconds']} seconds")
    
    # Check that WPG doesn't have 4v5 time (they should have 5v4, not 4v5)
    wpg_4v5 = result[(result['team'] == 'WPG') & (result['strength'] == '4v5')]
    if not wpg_4v5.empty:
        errors.append(f"FAILED: WPG should NOT have 4v5 time, but has {wpg_4v5.iloc[0]['seconds']} seconds")
    
    if errors:
        print("\n❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n✅ All team strength aggregate checks passed!")
        return True


def test_on_ice_stats_by_player_strength():
    """Test that on_ice_stats_by_player_strength produces correct mirrored strengths."""
    print("\n" + "="*60)
    print("Testing on_ice_stats_by_player_strength...")
    print("="*60)
    
    pbp = create_test_pbp_data()
    result = on_ice_stats_by_player_strength(pbp)
    
    print("\nPlayer Stats Sample (OTT and WPG players):")
    # Show sample of OTT and WPG players
    sample = result[result['player1Name'].isin(['OTT_Player_1', 'OTT_Player_5', 'WPG_Player_11'])]
    print(sample[['player1Name', 'eventTeam', 'strength', 'seconds', 'SF', 'SA']].to_string())
    
    errors = []
    
    # Check OTT players
    ott_players = result[result['eventTeam'] == 'OTT']
    
    # OTT_Player_5 went to penalty box, so should have less time than others
    player_5 = result[result['player1Name'] == 'OTT_Player_5']
    
    # OTT players 1-4 should have time in 5v5 and 4v5
    for pid in range(1, 5):
        player_rows = result[result['player1Id'] == pid]
        player_4v5 = player_rows[player_rows['strength'] == '4v5']
        player_5v4 = player_rows[player_rows['strength'] == '5v4']
        
        if not player_4v5.empty:
            seconds_4v5 = player_4v5.iloc[0]['seconds']
            if abs(seconds_4v5 - 120) > 0.1:
                errors.append(f"OTT_Player_{pid} 4v5: Expected ~120 seconds, got {seconds_4v5}")
        else:
            errors.append(f"OTT_Player_{pid} missing 4v5 row")
        
        # These players should NOT have 5v4 time (the bug would give them this)
        if not player_5v4.empty:
            errors.append(f"FAILED: OTT_Player_{pid} should NOT have 5v4 time, but has {player_5v4.iloc[0]['seconds']} seconds")
    
    # Check WPG players
    wpg_players = result[result['eventTeam'] == 'WPG']
    
    # All WPG players should have time in 5v5 and 5v4 (power play)
    for pid in range(11, 16):
        player_rows = result[result['player1Id'] == pid]
        player_5v4 = player_rows[player_rows['strength'] == '5v4']
        player_4v5 = player_rows[player_rows['strength'] == '4v5']
        
        if not player_5v4.empty:
            seconds_5v4 = player_5v4.iloc[0]['seconds']
            if abs(seconds_5v4 - 120) > 0.1:
                errors.append(f"WPG_Player_{pid} 5v4: Expected ~120 seconds, got {seconds_5v4}")
            # Should have 1 shot for during power play
            sf = player_5v4.iloc[0]['SF']
            if sf != 1:
                errors.append(f"WPG_Player_{pid} 5v4 SF: Expected 1, got {sf}")
        else:
            errors.append(f"WPG_Player_{pid} missing 5v4 row")
        
        # WPG players should NOT have 4v5 time (the bug would give them this)
        if not player_4v5.empty:
            errors.append(f"FAILED: WPG_Player_{pid} should NOT have 4v5 time, but has {player_4v5.iloc[0]['seconds']} seconds")
    
    if errors:
        print("\n❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n✅ All player strength checks passed!")
        return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESTING FIX FOR MIRRORED GAME STATES BUG")
    print("="*60)
    print("\nThis test validates that the 2nd team alphabetically")
    print("gets the correct (mirrored) game state in their stats.")
    print("="*60)
    
    test1_passed = test_team_strength_aggregates()
    test2_passed = test_on_ice_stats_by_player_strength()
    
    print("\n" + "="*60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("="*60)
        return 1


if __name__ == "__main__":
    exit(main())
