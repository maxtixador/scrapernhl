"""Test script for QMJHL scrapers"""

import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from scrapernhl.qmjhl.scrapers import (
    scrapeSchedule,
    scrapeScorebar,
    scrapeTeams,
    scrapeStandings,
    scrapePlayerStats,
    scrapeTeamStats,
    scrapeRoster,
)

def test_qmjhl_scrapers():
    """Test all QMJHL scrapers to ensure they work."""
    print("=" * 80)
    print("Testing QMJHL Scrapers")
    print("=" * 80)
    
    # Test schedule (statviewfeed pattern)
    print("\n1. Testing scrapeSchedule (statviewfeed)...")
    try:
        schedule_df = scrapeSchedule(season=211, team_id=-1, month=-1)
        print(f"   ✓ Success: Retrieved {len(schedule_df)} schedule records")
        print(f"   Columns: {list(schedule_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test scorebar (modulekit pattern)
    print("\n2. Testing scrapeScorebar (modulekit)...")
    try:
        scorebar_df = scrapeScorebar(season=211, days_ahead=30, days_back=30)
        print(f"   ✓ Success: Retrieved {len(scorebar_df)} scorebar records")
        print(f"   Columns: {list(scorebar_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test teams
    print("\n3. Testing scrapeTeams...")
    try:
        teams_df = scrapeTeams(season=211)
        print(f"   ✓ Success: Retrieved {len(teams_df)} teams")
        if len(teams_df) > 0:
            print(f"   Sample teams: {teams_df.iloc[0].get('name', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test standings
    print("\n4. Testing scrapeStandings...")
    try:
        standings_df = scrapeStandings(season=211, group_by='division')
        print(f"   ✓ Success: Retrieved {len(standings_df)} standings records")
        print(f"   Columns: {list(standings_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test player stats (skaters)
    print("\n5. Testing scrapePlayerStats (skaters)...")
    try:
        skater_stats_df = scrapePlayerStats(season=211, player_type='skater', limit=10)
        print(f"   ✓ Success: Retrieved {len(skater_stats_df)} skater records")
        print(f"   Columns: {list(skater_stats_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test player stats (goalies)
    print("\n6. Testing scrapePlayerStats (goalies)...")
    try:
        goalie_stats_df = scrapePlayerStats(season=211, player_type='goalie', limit=10)
        print(f"   ✓ Success: Retrieved {len(goalie_stats_df)} goalie records")
        print(f"   Columns: {list(goalie_stats_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test team stats
    print("\n7. Testing scrapeTeamStats...")
    try:
        team_stats_df = scrapeTeamStats(season=211)
        print(f"   ✓ Success: Retrieved {len(team_stats_df)} team stats records")
        print(f"   Columns: {list(team_stats_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test roster (using first team from teams if available)
    print("\n8. Testing scrapeRoster...")
    try:
        # Try with a known team ID (e.g., 52 for Quebec Remparts)
        roster_df = scrapeRoster(team_id=52, season=211)
        print(f"   ✓ Success: Retrieved {len(roster_df)} roster records")
        print(f"   Columns: {list(roster_df.columns)[:5]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_qmjhl_scrapers()
