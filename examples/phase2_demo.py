"""Demo script showcasing Phase 2 features: Rich integration and Caching.

This script demonstrates the new progress bars, styled console output,
and caching capabilities added in Phase 2.

Usage:
    python examples/phase2_demo.py
"""

from scrapernhl import (
    console,
    create_progress_bar,
    create_table,
    get_cache,
    cached,
)
from scrapernhl.nhl.scrapers.schedule import scrapeSchedule
from scrapernhl.nhl.scrapers.standings import scrapeStandings
from scrapernhl.nhl.scrapers.teams import scrapeTeams
from scrapernhl.nhl.scrapers.games import scrapeMultipleGames


def demo_styled_output():
    """Demonstrate styled console output."""
    console.rule("[bold blue]Styled Console Output Demo")
    
    console.print_success("This is a success message")
    console.print_error("This is an error message")
    console.print_warning("This is a warning message")
    console.print_info("This is an info message")
    
    console.print("\n[bold]Rich markup:[/bold] [cyan]colored text[/cyan], "
                 "[yellow]more colors[/yellow], [green]and more![/green]")


def demo_caching():
    """Demonstrate caching functionality."""
    console.rule("[bold blue]Caching Demo")
    
    # Get cache instance
    cache = get_cache()
    
    # Show cache stats
    console.print_info("Initial cache statistics:")
    stats = cache.stats()
    for key, value in stats.items():
        console.print(f"  {key}: {value}")
    
    # Scrape with caching (first call - cache miss)
    console.print("\n[yellow]First call - fetching from API...[/yellow]")
    schedule = scrapeSchedule("TOR", "20232024")
    console.print_success(f"Fetched {len(schedule)} games")
    
    # Second call - cache hit
    console.print("\n[yellow]Second call - should use cache...[/yellow]")
    schedule = scrapeSchedule("TOR", "20232024")
    console.print_success(f"Retrieved {len(schedule)} games from cache")
    
    # Show updated cache stats
    console.print_info("\nUpdated cache statistics:")
    stats = cache.stats()
    for key, value in stats.items():
        console.print(f"  {key}: {value}")
    
    # List cached keys
    console.print_info("\nCached keys:")
    for key in cache.list_keys():
        console.print(f"  - {key}")


def demo_progress_bars():
    """Demonstrate progress bar functionality."""
    console.rule("[bold blue]Progress Bar Demo")
    
    # Example: scraping multiple games
    console.print_info("Scraping multiple games with progress tracking...")
    
    # Use some real game IDs from 2023-24 season
    game_ids = [
        2023020001,  # Opening night games
        2023020002,
        2023020003,
    ]
    
    # This will show a progress bar
    plays_df = scrapeMultipleGames(game_ids, show_progress=True)
    
    console.print_success(f"Scraped {len(plays_df)} total plays")


def demo_tables():
    """Demonstrate table formatting."""
    console.rule("[bold blue]Table Formatting Demo")
    
    # Scrape standings
    standings = scrapeStandings("2024-01-01")
    
    # Create a formatted table (top 5 teams)
    table = create_table(
        "NHL Standings (Top 5)",
        ["Team", "Wins", "Losses", "Points"]
    )
    
    for _, row in standings.head(5).iterrows():
        team_name = row.get('teamName.default', 'Unknown')
        wins = row.get('wins', 0)
        losses = row.get('losses', 0)
        points = row.get('points', 0)
        table.add_row(str(team_name), str(wins), str(losses), str(points))
    
    console.print(table)


def demo_custom_cached_function():
    """Demonstrate custom function caching."""
    console.rule("[bold blue]Custom Function Caching Demo")
    
    @cached(ttl=60, cache_key_func=lambda x: f"square_{x}")
    def expensive_calculation(x):
        """Simulate an expensive calculation."""
        console.print_info(f"Computing square of {x}...")
        return x * x
    
    console.print("\n[yellow]First call (cache miss):[/yellow]")
    result1 = expensive_calculation(42)
    console.print_success(f"Result: {result1}")
    
    console.print("\n[yellow]Second call (cache hit):[/yellow]")
    result2 = expensive_calculation(42)
    console.print_success(f"Result: {result2}")


def main():
    """Run all demos."""
    console.print("\n[bold green]Phase 2 Features Demo[/bold green]\n")
    
    # Run demos
    demo_styled_output()
    print()
    
    demo_caching()
    print()
    
    demo_tables()
    print()
    
    demo_custom_cached_function()
    print()
    
    # Progress bars demo (optional - requires API calls)
    if input("\nRun progress bar demo? (requires API calls) [y/N]: ").lower() == 'y':
        demo_progress_bars()
    
    console.rule("[bold green]Demo Complete!")


if __name__ == "__main__":
    main()
