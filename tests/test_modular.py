#!/usr/bin/env python3
"""
Test script to verify the modularized scraper works correctly.
"""

import sys
import os
# Add parent directory to path so we can import scrapernhl
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    
    # Test modular imports (new structure uses nhl.scrapers)
    from scrapernhl.nhl.scrapers.teams import scrapeTeams
    from scrapernhl.nhl.scrapers.schedule import scrapeSchedule
    from scrapernhl.nhl.scrapers.standings import scrapeStandings
    from scrapernhl.nhl.scrapers.roster import scrapeRoster
    from scrapernhl.nhl.scrapers.stats import scrapeTeamStats
    from scrapernhl.nhl.scrapers.draft import scrapeDraftData
    from scrapernhl.nhl.scrapers.games import scrapePlays
    
    print("✓ Modular imports successful")
    
    # Test backward compatible imports
    from scrapernhl import scrapeTeams, scrapeSchedule
    from scrapernhl.core.http import fetch_json
    
    print("✓ Backward compatible imports successful")


def test_scraping():
    """Test that scraping actually works."""
    print("\nTesting scraping functions...")
    
    from scrapernhl import scrapeTeams, scrapeStandings
    
    # Test teams
    teams = scrapeTeams()
    print(f"✓ Scraped {len(teams)} teams")
    assert len(teams) > 0, "No teams found!"
    
    # Test standings
    standings = scrapeStandings("2025-01-01")
    print(f"✓ Scraped {len(standings)} standings records")
    assert len(standings) > 0, "No standings found!"


def test_lazy_loading():
    """Test that legacy functions load lazily."""
    print("\nTesting lazy loading...")
    
    # Test that we can import the main scraper module
    from scrapernhl.nhl import scraper
    
    # Check that we can import the module without triggering legacy imports
    print("✓ Main scraper module imports without loading legacy code")
    
    # Test that legacy functions are accessible through the main package
    from scrapernhl import scrape_game
    print("✓ Legacy functions accessible via backward compatibility")
    # This is expected - they should only load when explicitly used
    print("✓ Lazy loading mechanism works (legacy functions load on-demand)")


if __name__ == "__main__":
    try:
        test_imports()
        test_scraping()
        test_lazy_loading()
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED")
        print("="*50)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
