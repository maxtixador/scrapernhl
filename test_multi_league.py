"""
Test script for multi-league HockeyTech scraper

This script tests the unified scraper across all supported leagues:
- QMJHL (Quebec Major Junior Hockey League)
- OHL (Ontario Hockey League)
- WHL (Western Hockey League)
- AHL (American Hockey League)
- PWHL (Professional Women's Hockey League)
"""

import sys
from scrapernhl.core.hockeytech import get_api_events, scrape_game

# Test cases with game IDs from your examples
TEST_GAMES = {
    "qmjhl": 31171,    # Existing QMJHL game we've been testing
    "ohl": 28528,      # From your OHL example URL
    "whl": 1022565,    # From your WHL example URL
    "ahl": 1028297,    # From your AHL example URL
    "pwhl": 210,       # From your PWHL example URL
}


def test_raw_api_access():
    """Test that we can fetch raw data from each league's API."""
    print("=" * 80)
    print("TEST 1: Raw API Access")
    print("=" * 80)
    
    for league, game_id in TEST_GAMES.items():
        try:
            print(f"\n{league.upper()}: Fetching game {game_id}...")
            data = get_api_events(game_id, league=league, timeout=15)
            
            if isinstance(data, list):
                print(f"  ✓ Success! Retrieved {len(data)} events")
                if len(data) > 0:
                    print(f"  ✓ First event: {data[0].get('event', 'N/A')}")
            elif isinstance(data, dict):
                print(f"  ✓ Success! Retrieved dict with keys: {list(data.keys())}")
            else:
                print(f"  ⚠ Warning: Unexpected data type: {type(data)}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_league_specific_wrappers():
    """Test league-specific scraper modules."""
    print("\n" + "=" * 80)
    print("TEST 2: League-Specific Wrappers")
    print("=" * 80)
    
    league_imports = {
        "qmjhl": "scrapernhl.qmjhl.scrapers.games",
        "ohl": "scrapernhl.ohl.scrapers.games",
        "whl": "scrapernhl.whl.scrapers.games",
        "ahl": "scrapernhl.ahl.scrapers.games",
        "pwhl": "scrapernhl.pwhl.scrapers.games",
    }
    
    for league, module_path in league_imports.items():
        game_id = TEST_GAMES[league]
        
        try:
            print(f"\n{league.upper()}: Testing scrape_game({game_id})...")
            
            # Dynamic import
            module = __import__(module_path, fromlist=['scrape_game'])
            df = module.scrape_game(game_id, timeout=15, nhlify=True)
            
            print(f"  ✓ Success! Retrieved {len(df)} rows")
            print(f"  ✓ Columns: {len(df.columns)}")
            print(f"  ✓ Events: {df['event'].nunique()} unique types")
            
            # Show event breakdown
            event_counts = df['event'].value_counts().head(5)
            print(f"  ✓ Top events:")
            for event, count in event_counts.items():
                print(f"      - {event}: {count}")
            
            # Check for goals and shots
            goals = len(df[df['event'] == 'goal'])
            shots = len(df[df['event'] == 'shot'])
            print(f"  ✓ Goals: {goals}, Shots: {shots}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()


def test_nhlify_functionality():
    """Test that nhlify works across leagues (shot+goal merging)."""
    print("\n" + "=" * 80)
    print("TEST 3: Nhlify Functionality (Shot+Goal Merging)")
    print("=" * 80)
    
    # Test with a couple leagues
    test_leagues = ["qmjhl", "ohl"]
    
    for league in test_leagues:
        game_id = TEST_GAMES[league]
        
        try:
            print(f"\n{league.upper()} game {game_id}:")
            
            # Get data with and without nhlify
            df_nhl = scrape_game(game_id, league=league, nhlify=True, timeout=15)
            df_raw = scrape_game(game_id, league=league, nhlify=False, timeout=15)
            
            goals_nhl = len(df_nhl[df_nhl['event'] == 'goal'])
            goals_raw = len(df_raw[df_raw['event'] == 'goal'])
            shots_nhl = len(df_nhl[df_nhl['event'] == 'shot'])
            shots_raw = len(df_raw[df_raw['event'] == 'shot'])
            
            print(f"  Raw format:  {len(df_raw)} rows, {goals_raw} goals, {shots_raw} shots")
            print(f"  NHL format:  {len(df_nhl)} rows, {goals_nhl} goals, {shots_nhl} shots")
            print(f"  Difference:  {len(df_raw) - len(df_nhl)} rows merged")
            
            # Check if goals have shot data in nhlified version
            if goals_nhl > 0:
                goals_df = df_nhl[df_nhl['event'] == 'goal']
                has_coords = goals_df['x'].notna().sum()
                has_shot_type = goals_df['shot_type'].notna().sum()
                
                print(f"  ✓ Goals with coordinates: {has_coords}/{goals_nhl} ({has_coords/goals_nhl*100:.1f}%)")
                print(f"  ✓ Goals with shot_type: {has_shot_type}/{goals_nhl} ({has_shot_type/goals_nhl*100:.1f}%)")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MULTI-LEAGUE HOCKEYTECH SCRAPER TEST")
    print("=" * 80)
    print("\nTesting unified scraper across 5 leagues:")
    print("  - QMJHL (Quebec Major Junior Hockey League)")
    print("  - OHL (Ontario Hockey League)")
    print("  - WHL (Western Hockey League)")
    print("  - AHL (American Hockey League)")
    print("  - PWHL (Professional Women's Hockey League)")
    print()
    
    try:
        test_raw_api_access()
        test_league_specific_wrappers()
        test_nhlify_functionality()
        
        print("\n" + "=" * 80)
        print("TESTING COMPLETE!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
