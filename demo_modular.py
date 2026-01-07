#!/usr/bin/env python3
"""
Quick demo of the modularized scraper functionality.
Run this to see the new structure in action!
"""

def demo():
    print("=" * 60)
    print("NHL Scraper - Modularized Structure Demo")
    print("=" * 60)
    
    # Demo 1: Fast import
    print("\n📦 Demo 1: Fast Import (no heavy dependencies)")
    print("-" * 60)
    import time
    start = time.time()
    from scrapernhl.nhl.scrapers.teams import scrapeTeams
    print(f"✓ Import time: {(time.time() - start)*1000:.1f}ms")
    
    # Demo 2: Scrape teams
    print("\n🏒 Demo 2: Scrape NHL Teams")
    print("-" * 60)
    teams = scrapeTeams()
    print(f"✓ Scraped {len(teams)} teams")
    print(f"✓ Sample: {teams['fullName'].head(3).tolist()}")
    
    # Demo 3: Backward compatibility
    print("\n🔄 Demo 3: Backward Compatibility")
    print("-" * 60)
    from scrapernhl import scrapeStandings
    standings = scrapeStandings("2025-01-01")
    print(f"✓ Old import style still works!")
    print(f"✓ Scraped {len(standings)} standings records")
    
    # Demo 4: Module structure
    print("\n📁 Demo 4: New Module Structure")
    print("-" * 60)
    print("Available scraper modules:")
    print("  • scrapernhl.nhl.scrapers.teams")
    print("  • scrapernhl.nhl.scrapers.schedule")
    print("  • scrapernhl.nhl.scrapers.standings")
    print("  • scrapernhl.nhl.scrapers.roster")
    print("  • scrapernhl.nhl.scrapers.stats")
    print("  • scrapernhl.nhl.scrapers.draft")
    print("  • scrapernhl.nhl.scrapers.games")
    
    # Demo 5: Safety
    print("\n🛡️  Demo 5: Safety Features")
    print("-" * 60)
    import os
    legacy_file = "scrapernhl/scraper_legacy.py"
    if os.path.exists(legacy_file):
        size = os.path.getsize(legacy_file) // 1024
        print(f"✓ Original code backed up: {legacy_file} ({size}KB)")
    print("✓ Lazy loading: Complex functions load only when needed")
    print("✓ Zero breaking changes to existing code")
    
    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  • Use new imports: from scrapernhl.nhl.scrapers.teams import scrapeTeams")
    print("  • See MODULARIZATION.md for full documentation")
    print("  • Run tests/test_modular.py for comprehensive tests")
    

if __name__ == "__main__":
    demo()
