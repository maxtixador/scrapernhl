#!/usr/bin/env python3
"""
Test to verify the fix for mirrored game states bug.
Tests that the 2nd team alphabetically gets correct (not mirrored) strength labels.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapernhl.scraper_legacy import on_ice_stats_by_player_strength, team_strength_aggregates


def create_test_pbp():
    """
    Create a simple test pbp DataFrame with known strength situations.
    Teams: OTT (alphabetically first) and WPG (alphabetically second)
    Scenario: OTT has 5 skaters, WPG has 4 skaters for 120 seconds
    """
    rows = []
    
    # Start at time 0
    # OTT puts 5 skaters on ice
    for i in range(1, 6):
        rows.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'eventTeam': 'OTT',
            'player1Id': 1000 + i,
            'player1Name': f'OTT Player {i}',
            'isGoalie': 0
        })
    
    # WPG puts 4 skaters on ice (one short - penalty kill)
    for i in range(1, 5):
        rows.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'eventTeam': 'WPG',
            'player1Id': 2000 + i,
            'player1Name': f'WPG Player {i}',
            'isGoalie': 0
        })
    
    # Add goalies
    rows.append({
        'Event': 'ON',
        'elapsedTime': 0,
        'eventTeam': 'OTT',
        'player1Id': 1090,
        'player1Name': 'OTT Goalie',
        'isGoalie': 1
    })
    rows.append({
        'Event': 'ON',
        'elapsedTime': 0,
        'eventTeam': 'WPG',
        'player1Id': 2090,
        'player1Name': 'WPG Goalie',
        'isGoalie': 1
    })
    
    # Add a shot event at time 60 (from OTT)
    rows.append({
        'Event': 'SHOT',
        'elapsedTime': 60,
        'eventTeam': 'OTT',
        'xG': 0.1
    })
    
    # End game at time 120
    rows.append({
        'Event': 'GEND',
        'elapsedTime': 120,
        'eventTeam': 'OTT'
    })
    
    df = pd.DataFrame(rows)
    return df


def test_player_strength_labels():
    """Test that on_ice_stats_by_player_strength assigns correct strength labels."""
    print("\nTesting on_ice_stats_by_player_strength...")
    
    pbp = create_test_pbp()
    result = on_ice_stats_by_player_strength(pbp, include_goalies=False)
    
    # Check OTT players (alphabetically first team)
    ott_players = result[result['eventTeam'] == 'OTT']
    ott_strengths = ott_players['strength'].unique()
    print(f"  OTT strength labels: {sorted(ott_strengths)}")
    
    # Check WPG players (alphabetically second team)
    wpg_players = result[result['eventTeam'] == 'WPG']
    wpg_strengths = wpg_players['strength'].unique()
    print(f"  WPG strength labels: {sorted(wpg_strengths)}")
    
    # OTT should have 5v4 (5 skaters vs 4 opponents)
    assert '5v4' in ott_strengths, f"OTT should have 5v4 strength, got {ott_strengths}"
    
    # WPG should have 4v5 (4 skaters vs 5 opponents) - NOT 5v4!
    assert '4v5' in wpg_strengths, f"WPG should have 4v5 strength, got {wpg_strengths}"
    
    # Make sure they DON'T have the mirrored incorrect labels
    assert '4v5' not in ott_strengths, f"OTT should NOT have 4v5 strength"
    assert '5v4' not in wpg_strengths, f"WPG should NOT have 5v4 strength (this was the bug!)"
    
    # Check TOI is correct
    ott_toi = ott_players[ott_players['strength'] == '5v4']['seconds'].iloc[0]
    wpg_toi = wpg_players[wpg_players['strength'] == '4v5']['seconds'].iloc[0]
    
    print(f"  OTT 5v4 TOI: {ott_toi} seconds")
    print(f"  WPG 4v5 TOI: {wpg_toi} seconds")
    
    # Both teams should have 120 seconds TOI
    assert ott_toi == 120, f"OTT should have 120s TOI, got {ott_toi}"
    assert wpg_toi == 120, f"WPG should have 120s TOI, got {wpg_toi}"
    
    print("  ✓ Player strength labels are correct!")


def test_team_strength_labels():
    """Test that team_strength_aggregates assigns correct strength labels."""
    print("\nTesting team_strength_aggregates...")
    
    pbp = create_test_pbp()
    result = team_strength_aggregates(pbp, include_goalies=False)
    
    # Check OTT team stats
    ott_stats = result[result['team'] == 'OTT']
    ott_strengths = ott_stats['strength'].unique()
    print(f"  OTT strength labels: {sorted(ott_strengths)}")
    
    # Check WPG team stats
    wpg_stats = result[result['team'] == 'WPG']
    wpg_strengths = wpg_stats['strength'].unique()
    print(f"  WPG strength labels: {sorted(wpg_strengths)}")
    
    # OTT should have 5v4
    assert '5v4' in ott_strengths, f"OTT should have 5v4 strength, got {ott_strengths}"
    
    # WPG should have 4v5 - NOT 5v4!
    assert '4v5' in wpg_strengths, f"WPG should have 4v5 strength, got {wpg_strengths}"
    
    # Make sure they DON'T have the mirrored incorrect labels
    assert '4v5' not in ott_strengths, f"OTT should NOT have 4v5 strength"
    assert '5v4' not in wpg_strengths, f"WPG should NOT have 5v4 strength (this was the bug!)"
    
    # Check TOI is correct
    ott_toi = ott_stats[ott_stats['strength'] == '5v4']['seconds'].iloc[0]
    wpg_toi = wpg_stats[wpg_stats['strength'] == '4v5']['seconds'].iloc[0]
    
    print(f"  OTT 5v4 TOI: {ott_toi} seconds")
    print(f"  WPG 4v5 TOI: {wpg_toi} seconds")
    
    # Both teams should have 120 seconds TOI
    assert abs(ott_toi - 120) < 0.01, f"OTT should have 120s TOI, got {ott_toi}"
    assert abs(wpg_toi - 120) < 0.01, f"WPG should have 120s TOI, got {wpg_toi}"
    
    # Check shot stats are correct
    ott_5v4 = ott_stats[ott_stats['strength'] == '5v4'].iloc[0]
    wpg_4v5 = wpg_stats[wpg_stats['strength'] == '4v5'].iloc[0]
    
    print(f"  OTT 5v4 SF: {ott_5v4['SF']}, SA: {ott_5v4['SA']}")
    print(f"  WPG 4v5 SF: {wpg_4v5['SF']}, SA: {wpg_4v5['SA']}")
    
    # OTT took the shot, so OTT should have 1 SF, WPG should have 1 SA
    assert ott_5v4['SF'] == 1, f"OTT should have 1 SF, got {ott_5v4['SF']}"
    assert ott_5v4['SA'] == 0, f"OTT should have 0 SA, got {ott_5v4['SA']}"
    assert wpg_4v5['SF'] == 0, f"WPG should have 0 SF, got {wpg_4v5['SF']}"
    assert wpg_4v5['SA'] == 1, f"WPG should have 1 SA, got {wpg_4v5['SA']}"
    
    print("  ✓ Team strength labels are correct!")


def test_alphabetical_ordering():
    """
    Test with teams in reverse alphabetical order to ensure the fix works
    regardless of which team is t1 and which is t2.
    """
    print("\nTesting with WSH vs WPG (different alphabetical order)...")
    
    rows = []
    
    # WSH (alphabetically second) puts 5 skaters on
    for i in range(1, 6):
        rows.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'eventTeam': 'WSH',
            'player1Id': 3000 + i,
            'player1Name': f'WSH Player {i}',
            'isGoalie': 0
        })
    
    # WPG (alphabetically first) puts 4 skaters on
    for i in range(1, 5):
        rows.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'eventTeam': 'WPG',
            'player1Id': 2000 + i,
            'player1Name': f'WPG Player {i}',
            'isGoalie': 0
        })
    
    # Goalies
    rows.append({
        'Event': 'ON',
        'elapsedTime': 0,
        'eventTeam': 'WSH',
        'player1Id': 3090,
        'player1Name': 'WSH Goalie',
        'isGoalie': 1
    })
    rows.append({
        'Event': 'ON',
        'elapsedTime': 0,
        'eventTeam': 'WPG',
        'player1Id': 2090,
        'player1Name': 'WPG Goalie',
        'isGoalie': 1
    })
    
    rows.append({
        'Event': 'GEND',
        'elapsedTime': 100,
        'eventTeam': 'WPG'
    })
    
    pbp = pd.DataFrame(rows)
    result = team_strength_aggregates(pbp, include_goalies=False)
    
    # WPG (alphabetically first) should have 4v5
    wpg_strengths = result[result['team'] == 'WPG']['strength'].unique()
    assert '4v5' in wpg_strengths, f"WPG should have 4v5, got {wpg_strengths}"
    
    # WSH (alphabetically second) should have 5v4
    wsh_strengths = result[result['team'] == 'WSH']['strength'].unique()
    assert '5v4' in wsh_strengths, f"WSH should have 5v4, got {wsh_strengths}"
    
    print(f"  WPG strength labels: {sorted(wpg_strengths)}")
    print(f"  WSH strength labels: {sorted(wsh_strengths)}")
    print("  ✓ Alphabetical ordering test passed!")


def test_toi_by_player_and_strength():
    """Test that toi_by_player_and_strength assigns correct strength labels."""
    print("\nTesting toi_by_player_and_strength...")
    
    from scrapernhl.scraper_legacy import toi_by_player_and_strength
    
    rows = []
    
    # Time 0: OTT puts 5 skaters on, WPG puts 4 skaters on
    for i in range(1, 6):
        rows.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'Per': 1,
            'eventTeam': 'OTT',
            'player1Id': 1000 + i,
            'player1Name': f'OTT Player {i}',
            'isGoalie': 0
        })
    
    for i in range(1, 5):
        rows.append({
            'Event': 'ON',
            'elapsedTime': 0,
            'Per': 1,
            'eventTeam': 'WPG',
            'player1Id': 2000 + i,
            'player1Name': f'WPG Player {i}',
            'isGoalie': 0
        })
    
    # Add goalies
    rows.append({
        'Event': 'ON',
        'elapsedTime': 0,
        'Per': 1,
        'eventTeam': 'OTT',
        'player1Id': 1090,
        'player1Name': 'OTT Goalie',
        'isGoalie': 1
    })
    rows.append({
        'Event': 'ON',
        'elapsedTime': 0,
        'Per': 1,
        'eventTeam': 'WPG',
        'player1Id': 2090,
        'player1Name': 'WPG Goalie',
        'isGoalie': 1
    })
    
    # Time 120: WPG player comes off (to create a final segment)
    rows.append({
        'Event': 'OFF',
        'elapsedTime': 120,
        'Per': 1,
        'eventTeam': 'WPG',
        'player1Id': 2001,
        'player1Name': 'WPG Player 1',
        'isGoalie': 0
    })
    
    change_events = pd.DataFrame(rows)
    
    result = toi_by_player_and_strength(change_events)
    
    # Check OTT players
    ott_players = result[result['eventTeam'] == 'OTT']
    ott_strengths = ott_players['strength'].unique()
    print(f"  OTT strength labels: {sorted(ott_strengths)}")
    
    # Check WPG players
    wpg_players = result[result['eventTeam'] == 'WPG']
    wpg_strengths = wpg_players['strength'].unique()
    print(f"  WPG strength labels: {sorted(wpg_strengths)}")
    
    # OTT should have 5v4
    assert '5v4' in ott_strengths, f"OTT should have 5v4 strength, got {ott_strengths}"
    
    # WPG should have 4v5 - NOT 5v4!
    assert '4v5' in wpg_strengths, f"WPG should have 4v5 strength, got {wpg_strengths}"
    
    # Make sure they DON'T have the mirrored incorrect labels
    assert '4v5' not in ott_strengths, f"OTT should NOT have 4v5 strength"
    assert '5v4' not in wpg_strengths, f"WPG should NOT have 5v4 strength (this was the bug!)"
    
    print("  ✓ toi_by_player_and_strength labels are correct!")


def test_combo_on_ice_stats():
    """Test that combo_on_ice_stats assigns correct strength labels for focus_team."""
    print("\nTesting combo_on_ice_stats...")
    
    from scrapernhl.scraper_legacy import combo_on_ice_stats
    
    pbp = create_test_pbp()
    
    # Test with OTT as focus_team (alphabetically first)
    result_ott = combo_on_ice_stats(pbp, focus_team='OTT', n_team=2, min_TOI=0)
    ott_strengths = result_ott['strength'].unique()
    print(f"  OTT (focus_team, alphabetically 1st) strength labels: {sorted(ott_strengths)}")
    assert '5v4' in ott_strengths, f"OTT should have 5v4 strength, got {ott_strengths}"
    assert '4v5' not in ott_strengths, f"OTT should NOT have 4v5 strength"
    
    # Test with WPG as focus_team (alphabetically second) - THIS IS THE CRITICAL TEST
    result_wpg = combo_on_ice_stats(pbp, focus_team='WPG', n_team=2, min_TOI=0)
    wpg_strengths = result_wpg['strength'].unique()
    print(f"  WPG (focus_team, alphabetically 2nd) strength labels: {sorted(wpg_strengths)}")
    assert '4v5' in wpg_strengths, f"WPG should have 4v5 strength, got {wpg_strengths}"
    assert '5v4' not in wpg_strengths, f"WPG should NOT have 5v4 strength (this was the bug!)"
    
    print("  ✓ combo_on_ice_stats labels are correct!")


if __name__ == "__main__":
    try:
        test_player_strength_labels()
        test_team_strength_labels()
        test_alphabetical_ordering()
        test_toi_by_player_and_strength()
        test_combo_on_ice_stats()
        
        print("\n" + "="*50)
        print("✅ ALL STRENGTH LABEL TESTS PASSED")
        print("="*50)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
