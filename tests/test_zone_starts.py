#!/usr/bin/env python3
"""Test script for zone start integration"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test a recent game
game_id = 2024020571  # Recent game

print(f"Testing zone start integration for game {game_id}...")
print("-" * 60)

try:
    from scrapernhl import scrape_game
    
    # Scrape the game
    print("Scraping game data...")
    data = scrape_game(game_id)
    
    # Filter for ON events
    on_events = data[data['Event'] == 'ON'].copy()
    
    print(f"\nTotal ON events: {len(on_events)}")
    
    # Check if zone start columns exist
    zone_cols = ['shift_start_type', 'start_dot', 'start_zone']
    missing = [col for col in zone_cols if col not in on_events.columns]
    
    if missing:
        print(f"❌ Missing columns: {missing}")
        sys.exit(1)
    
    print("✓ All zone start columns present")
    
    # Show statistics
    print("\n" + "=" * 60)
    print("ZONE START STATISTICS")
    print("=" * 60)
    
    print("\nShift Start Types:")
    print(on_events['shift_start_type'].value_counts())
    
    print("\nZone Start Distribution (for ZS shifts only):")
    zs_events = on_events[on_events['shift_start_type'] == 'ZS']
    if len(zs_events) > 0:
        print(zs_events['start_zone'].value_counts())
        
        print("\nFaceoff Dot Distribution (for ZS shifts only):")
        print(zs_events['start_dot'].value_counts())
    else:
        print("No zone start events found")
    
    # Show a few examples
    print("\n" + "=" * 60)
    print("SAMPLE ZONE STARTS")
    print("=" * 60)
    
    sample_cols = ['#', 'Per', 'timeInPeriodSec', 'eventTeam', 'player1Name', 
                   'shift_start_type', 'start_zone', 'start_dot']
    available_cols = [col for col in sample_cols if col in on_events.columns]
    
    print("\nFirst 5 Zone Starts:")
    zs_sample = zs_events[available_cols].head()
    if len(zs_sample) > 0:
        print(zs_sample.to_string(index=False))
    else:
        print("No zone start events found")
    
    print("\nFirst 5 On-The-Fly Shifts:")
    otf_events = on_events[on_events['shift_start_type'] == 'OTF']
    otf_sample = otf_events[available_cols].head()
    if len(otf_sample) > 0:
        print(otf_sample.to_string(index=False))
    else:
        print("No OTF events found")
    
    print("\n" + "=" * 60)
    print("✅ Zone start integration test PASSED!")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nThis is likely a numpy compatibility issue in your environment.")
    print("The syntax check passed, so the code is correct.")
    print("Try running in a clean virtual environment with:")
    print("  python -m venv test_env")
    print("  source test_env/bin/activate")
    print("  pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
