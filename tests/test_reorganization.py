"""Test script to verify package reorganization worked correctly."""

import sys
from rich.console import Console

console = Console()

def test_basic_imports():
    """Test basic package imports work."""
    console.print("\n[bold blue]Testing Basic Imports...[/bold blue]")
    
    try:
        import scrapernhl
        console.print("✓ Package import successful")
        
        # Test version
        assert hasattr(scrapernhl, '__version__')
        console.print(f"✓ Version: {scrapernhl.__version__}")
        
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Basic import failed: {e}[/bold red]")
        return False


def test_exception_imports():
    """Test exception imports."""
    console.print("\n[bold blue]Testing Exception Imports...[/bold blue]")
    
    try:
        from scrapernhl import (
            ScraperNHLError,
            APIError,
            InvalidGameError,
            InvalidTeamError,
            InvalidSeasonError,
            DataValidationError,
            CacheError,
            ParsingError,
            RateLimitError,
        )
        console.print("✓ All exception classes imported")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Exception imports failed: {e}[/bold red]")
        return False


def test_core_utilities():
    """Test core utility imports."""
    console.print("\n[bold blue]Testing Core Utilities...[/bold blue]")
    
    try:
        from scrapernhl import (
            standardize_columns,
            validate_data_quality,
            setup_logging,
            console as prog_console,
            create_progress_bar,
            create_table,
            Cache,
            get_cache,
            cached,
            BatchScraper,
            BatchResult,
            scrape_season_games,
            scrape_date_range,
        )
        console.print("✓ Core utilities imported")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Core utility imports failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def test_scraper_imports():
    """Test scraper imports (backward compatibility)."""
    console.print("\n[bold blue]Testing Scraper Imports (Backward Compatibility)...[/bold blue]")
    
    try:
        from scrapernhl import (
            scrapeTeams,
            scrapeSchedule,
            scrapeStandings,
            scrapeRoster,
        )
        console.print("✓ Main scrapers imported (backward compatible)")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Scraper imports failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def test_player_scrapers():
    """Test player scraper imports."""
    console.print("\n[bold blue]Testing Player Scraper Imports...[/bold blue]")
    
    try:
        from scrapernhl import (
            scrapePlayerProfile,
            scrapePlayerSeasonStats,
            scrapePlayerGameLog,
            scrapeMultiplePlayerStats,
            scrapeTeamRoster,
            scrapeTeamPlayerStats,
        )
        console.print("✓ Player scrapers imported")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Player scraper imports failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_imports():
    """Test analytics imports."""
    console.print("\n[bold blue]Testing Analytics Imports...[/bold blue]")
    
    try:
        from scrapernhl import (
            calculate_shot_distance,
            calculate_shot_angle,
            identify_scoring_chances,
            calculate_corsi,
            calculate_fenwick,
            calculate_player_toi,
            calculate_zone_start_percentage,
            calculate_team_stats_summary,
            calculate_player_stats_summary,
            calculate_score_effects,
            analyze_shooting_patterns,
            create_analytics_report,
        )
        console.print("✓ Analytics functions imported")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Analytics imports failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def test_visualization_imports():
    """Test visualization imports."""
    console.print("\n[bold blue]Testing Visualization Imports...[/bold blue]")
    
    try:
        from scrapernhl import (
            display_team_stats,
            display_advanced_stats,
            display_player_summary,
            display_scoring_chances,
            display_shooting_patterns,
            display_score_effects,
            display_game_summary,
            display_top_players,
            print_analytics_summary,
        )
        console.print("✓ Visualization functions imported")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Visualization imports failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def test_direct_nhl_imports():
    """Test direct imports from nhl module."""
    console.print("\n[bold blue]Testing Direct NHL Module Imports...[/bold blue]")
    
    try:
        from scrapernhl.nhl.scrapers.teams import scrapeTeams
        from scrapernhl.nhl.scrapers.schedule import scrapeSchedule
        from scrapernhl.nhl.scrapers.players import scrapePlayerProfile
        from scrapernhl.nhl.analytics import calculate_corsi
        console.print("✓ Direct NHL module imports work")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Direct NHL imports failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def test_live_scraping():
    """Test actual scraping functionality."""
    console.print("\n[bold blue]Testing Live Scraping...[/bold blue]")
    
    try:
        from scrapernhl import scrapeTeams
        
        console.print("Fetching NHL teams...")
        teams = scrapeTeams()
        
        if len(teams) > 0:
            console.print(f"✓ Successfully scraped {len(teams)} teams")
            # Get team names from any available column
            if 'fullName' in teams.columns:
                sample = teams['fullName'].head(3).tolist()
            elif 'name' in teams.columns:
                sample = teams['name'].head(3).tolist()
            else:
                sample = [str(i) for i in range(min(3, len(teams)))]
            console.print(f"  Sample teams: {', '.join(sample)}")
            return True
        else:
            console.print("[bold red]✗ No teams returned[/bold red]")
            return False
            
    except Exception as e:
        console.print(f"[bold red]✗ Live scraping failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    console.print("[bold green]╔══════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║   ScraperNHL Reorganization Test Suite          ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════╝[/bold green]")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Exception Imports", test_exception_imports),
        ("Core Utilities", test_core_utilities),
        ("Scraper Imports", test_scraper_imports),
        ("Player Scrapers", test_player_scrapers),
        ("Analytics Imports", test_analytics_imports),
        ("Visualization Imports", test_visualization_imports),
        ("Direct NHL Imports", test_direct_nhl_imports),
        ("Live Scraping", test_live_scraping),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[bold red]✗ Test '{test_name}' crashed: {e}[/bold red]")
            results.append((test_name, False))
    
    # Summary
    console.print("\n[bold blue]════════════════════════════════════════════════════[/bold blue]")
    console.print("[bold blue]                    TEST SUMMARY                    [/bold blue]")
    console.print("[bold blue]════════════════════════════════════════════════════[/bold blue]")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[bold green]✓ PASS[/bold green]" if result else "[bold red]✗ FAIL[/bold red]"
        console.print(f"{status}  {test_name}")
    
    console.print("\n[bold blue]════════════════════════════════════════════════════[/bold blue]")
    
    if passed == total:
        console.print(f"[bold green]ALL TESTS PASSED! ({passed}/{total})[/bold green]")
        return 0
    else:
        console.print(f"[bold red]SOME TESTS FAILED ({passed}/{total})[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
