"""Comprehensive test script for all league scrapers"""

import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_league_scrapers(league_name, scrapers):
    """Test all scrapers for a league."""
    print(f"\n{'=' * 80}")
    print(f"Testing {league_name} Scrapers")
    print('=' * 80)
    
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    for test_name, scraper_func in scrapers.items():
        print(f"\n{test_name}...")
        try:
            df = scraper_func()
            if df is not None and len(df) > 0:
                print(f"   ✓ Success: Retrieved {len(df)} records")
                print(f"   Columns: {list(df.columns)[:5]}...")
                results['success'] += 1
            else:
                print(f"   ⚠ Warning: No data returned")
                results['success'] += 1
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results['failed'] += 1
            results['errors'].append(f"{test_name}: {e}")
    
    return results

def main():
    """Run all tests."""
    print("=" * 80)
    print("Multi-League Scraper Test Suite")
    print("=" * 80)
    
    all_results = {}
    
    # Test QMJHL
    from scrapernhl.qmjhl.scrapers import (
        scrapeSchedule as qmjhl_schedule,
        scrapeTeams as qmjhl_teams,
        scrapeStandings as qmjhl_standings,
        scrapePlayerStats as qmjhl_player_stats,
        scrapeRoster as qmjhl_roster,
    )
    
    qmjhl_tests = {
        '1. Schedule': lambda: qmjhl_schedule(season=211, team_id=-1),
        '2. Teams': lambda: qmjhl_teams(season=211),
        '3. Standings': lambda: qmjhl_standings(season=211),
        '4. Player Stats': lambda: qmjhl_player_stats(season=211, limit=10),
        '5. Roster': lambda: qmjhl_roster(team_id=52, season=211),
    }
    
    all_results['QMJHL'] = test_league_scrapers('QMJHL', qmjhl_tests)
    
    # Test OHL
    from scrapernhl.ohl.scrapers import (
        scrapeSchedule as ohl_schedule,
        scrapeTeams as ohl_teams,
        scrapeStandings as ohl_standings,
        scrapePlayerStats as ohl_player_stats,
        scrapeRoster as ohl_roster,
    )
    
    ohl_tests = {
        '1. Schedule': lambda: ohl_schedule(season=68, team_id=-1),
        '2. Teams': lambda: ohl_teams(season=68),
        '3. Standings': lambda: ohl_standings(season=68),
        '4. Player Stats': lambda: ohl_player_stats(season=68, limit=10),
        '5. Roster': lambda: ohl_roster(team_id=1, season=68),
    }
    
    all_results['OHL'] = test_league_scrapers('OHL', ohl_tests)
    
    # Test WHL
    from scrapernhl.whl.scrapers import (
        scrapeSchedule as whl_schedule,
        scrapeTeams as whl_teams,
        scrapeStandings as whl_standings,
        scrapePlayerStats as whl_player_stats,
        scrapeRoster as whl_roster,
    )
    
    whl_tests = {
        '1. Schedule': lambda: whl_schedule(season=70, team_id=-1),
        '2. Teams': lambda: whl_teams(season=70),
        '3. Standings': lambda: whl_standings(season=70),
        '4. Player Stats': lambda: whl_player_stats(season=70, limit=10),
        '5. Roster': lambda: whl_roster(team_id=1, season=70),
    }
    
    all_results['WHL'] = test_league_scrapers('WHL', whl_tests)
    
    # Test PWHL
    from scrapernhl.pwhl.scrapers import (
        scrapeSchedule as pwhl_schedule,
        scrapeTeams as pwhl_teams,
        scrapeStandings as pwhl_standings,
        scrapePlayerStats as pwhl_player_stats,
        scrapeRoster as pwhl_roster,
    )
    
    pwhl_tests = {
        '1. Schedule': lambda: pwhl_schedule(season=2, team_id=-1),
        '2. Teams': lambda: pwhl_teams(season=2),
        '3. Standings': lambda: pwhl_standings(season=2),
        '4. Player Stats': lambda: pwhl_player_stats(season=2, limit=10),
        '5. Roster': lambda: pwhl_roster(team_id=1, season=2),
    }
    
    all_results['PWHL'] = test_league_scrapers('PWHL', pwhl_tests)
    
    # Test AHL
    from scrapernhl.ahl.scrapers import (
        scrapeSchedule as ahl_schedule,
        scrapeTeams as ahl_teams,
        scrapeStandings as ahl_standings,
        scrapePlayerStats as ahl_player_stats,
        scrapeRoster as ahl_roster,
    )
    
    ahl_tests = {
        '1. Schedule': lambda: ahl_schedule(season=71, team_id=-1),
        '2. Teams': lambda: ahl_teams(season=71),
        '3. Standings': lambda: ahl_standings(season=71),
        '4. Player Stats': lambda: ahl_player_stats(season=71, limit=10),
        '5. Roster': lambda: ahl_roster(team_id=1, season=71),
    }
    
    all_results['AHL'] = test_league_scrapers('AHL', ahl_tests)
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    total_success = 0
    total_failed = 0
    
    for league, results in all_results.items():
        total_success += results['success']
        total_failed += results['failed']
        status = "✓" if results['failed'] == 0 else "⚠"
        print(f"{status} {league}: {results['success']} passed, {results['failed']} failed")
        if results['errors']:
            for error in results['errors']:
                print(f"    - {error}")
    
    print("\n" + "=" * 80)
    print(f"Overall: {total_success} tests passed, {total_failed} tests failed")
    print("=" * 80)

if __name__ == "__main__":
    main()
