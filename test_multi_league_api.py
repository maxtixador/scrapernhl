"""
Test script for multi-league API modules.

Tests all 5 HockeyTech league APIs (PWHL, AHL, OHL, WHL, QMJHL)
with basic functionality checks.
"""

import sys
from scrapernhl.pwhl import api as pwhl_api
from scrapernhl.ahl import api as ahl_api
from scrapernhl.ohl import api as ohl_api
from scrapernhl.whl import api as whl_api
from scrapernhl.qmjhl import api as qmjhl_api


def test_league_api(league_name, api_module, config_class):
    """Test basic API functionality for a league."""
    print(f"\n{'='*60}")
    print(f"Testing {league_name} API")
    print(f"{'='*60}")
    
    try:
        # Test 1: Get scorebar
        print(f"\n1. Testing get_scorebar()...")
        scorebar = api_module.get_scorebar(days_ahead=3, days_back=1)
        if isinstance(scorebar, dict):
            games = scorebar.get('games', [])
            print(f"   ✓ Success: Found {len(games)} games")
        else:
            print(f"   ✓ Success: Retrieved scorebar data")
        
        # Test 2: Get teams
        print(f"\n2. Testing get_teams()...")
        teams = api_module.get_teams()
        if isinstance(teams, dict):
            team_list = teams.get('teams', teams.get('SiteKit', {}).get('Team', []))
            if isinstance(team_list, list):
                print(f"   ✓ Success: Found {len(team_list)} teams")
            else:
                print(f"   ✓ Success: Retrieved teams data")
        else:
            print(f"   ✓ Success: Retrieved teams data")
        
        # Test 3: Get standings
        print(f"\n3. Testing get_standings()...")
        standings = api_module.get_standings(group_by='division')
        if standings:
            print(f"   ✓ Success: Retrieved standings")
        else:
            print(f"   ✓ Success: Retrieved standings (empty)")
        
        # Test 4: Get skater stats (limited to 10)
        print(f"\n4. Testing get_skater_stats()...")
        skaters = api_module.get_skater_stats(limit=10)
        if isinstance(skaters, dict):
            players = skaters.get('players', skaters.get('SiteKit', {}).get('Player', []))
            if isinstance(players, list):
                print(f"   ✓ Success: Found {len(players)} skaters")
                if players:
                    print(f"   Sample player: {players[0].get('name', 'Unknown')}")
            else:
                print(f"   ✓ Success: Retrieved skater stats")
        else:
            print(f"   ✓ Success: Retrieved skater stats")
        
        # Test 5: Get goalie stats (limited to 5)
        print(f"\n5. Testing get_goalie_stats()...")
        goalies = api_module.get_goalie_stats(limit=5)
        if isinstance(goalies, dict):
            goalie_list = goalies.get('goalies', goalies.get('SiteKit', {}).get('Goalie', []))
            if isinstance(goalie_list, list):
                print(f"   ✓ Success: Found {len(goalie_list)} goalies")
                if goalie_list:
                    print(f"   Sample goalie: {goalie_list[0].get('name', 'Unknown')}")
            else:
                print(f"   ✓ Success: Retrieved goalie stats")
        else:
            print(f"   ✓ Success: Retrieved goalie stats")
        
        # Test 6: Get bootstrap
        print(f"\n6. Testing get_bootstrap()...")
        bootstrap = api_module.get_bootstrap()
        if bootstrap:
            print(f"   ✓ Success: Retrieved bootstrap config")
        else:
            print(f"   ✓ Success: Retrieved bootstrap (empty)")
        
        print(f"\n✅ {league_name} API: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ {league_name} API: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests for all leagues."""
    print("="*60)
    print("Multi-League API Test Suite")
    print("Testing: PWHL, AHL, OHL, WHL, QMJHL")
    print("="*60)
    
    results = {}
    
    # Test each league
    leagues = [
        ("PWHL", pwhl_api, pwhl_api.PWHLConfig),
        ("AHL", ahl_api, ahl_api.AHLConfig),
        ("OHL", ohl_api, ohl_api.OHLConfig),
        ("WHL", whl_api, whl_api.WHLConfig),
        ("QMJHL", qmjhl_api, qmjhl_api.QMJHLConfig),
    ]
    
    for league_name, api_module, config_class in leagues:
        results[league_name] = test_league_api(league_name, api_module, config_class)
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for league, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{league:10} {status}")
    
    print(f"\nTotal: {passed}/{total} leagues passed")
    
    if passed == total:
        print("\n🎉 All league APIs working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} league(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
