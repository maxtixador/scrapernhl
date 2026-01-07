"""Demo script showcasing Phase 3 features: Player Stats and Batch Processing.

This script demonstrates the new player statistics scrapers and advanced
batch processing capabilities added in Phase 3.

Usage:
    python examples/phase3_demo.py
"""

from scrapernhl import (
    console,
    create_table,
    scrapePlayerProfile,
    scrapePlayerSeasonStats,
    scrapePlayerGameLog,
    scrapeMultiplePlayerStats,
    scrapeTeamRoster,
    scrapeTeamPlayerStats,
    BatchScraper,
    scrape_season_games,
)


def demo_player_profile():
    """Demonstrate player profile scraping."""
    console.rule("[bold blue]Player Profile Demo")
    
    # Auston Matthews
    player_id = 8478402
    
    console.print_info(f"Fetching profile for player {player_id}...")
    profile = scrapePlayerProfile(player_id)
    
    # Display key info
    if not profile.empty:
        row = profile.iloc[0]
        console.print_success("Profile retrieved!")
        console.print(f"  Name: {row.get('firstName', '')} {row.get('lastName', '')}")
        console.print(f"  Position: {row.get('position', 'N/A')}")
        console.print(f"  Team: {row.get('currentTeamAbbrev', 'N/A')}")
        console.print(f"  Birth Date: {row.get('birthDate', 'N/A')}")


def demo_player_season_stats():
    """Demonstrate season statistics scraping."""
    console.rule("[bold blue]Player Season Stats Demo")
    
    # McDavid, Matthews, Draisaitl
    player_ids = [8478402, 8479318, 8480012]
    player_names = ["Matthews", "McDavid", "Draisaitl"]
    
    console.print_info("Fetching season stats for top players...")
    
    stats = scrapeMultiplePlayerStats(player_ids, "20232024", show_progress=True)
    
    if not stats.empty:
        console.print_success(f"Retrieved stats for {len(stats)} players")
        
        # Create a formatted table
        table = create_table(
            "Top Players - 2023-24 Season",
            ["Player ID", "Records"]
        )
        
        for i, (pid, name) in enumerate(zip(player_ids, player_names)):
            count = len(stats[stats['playerId'] == str(pid)])
            table.add_row(f"{name} ({pid})", str(count))
        
        console.print(table)


def demo_game_log():
    """Demonstrate game log scraping."""
    console.rule("[bold blue]Player Game Log Demo")
    
    # Auston Matthews
    player_id = 8478402
    
    console.print_info(f"Fetching game log for player {player_id}...")
    gamelog = scrapePlayerGameLog(player_id, "20232024")
    
    if not gamelog.empty:
        console.print_success(f"Retrieved {len(gamelog)} games")
        
        # Show first 5 games
        console.print("\nFirst 5 games:")
        for i, row in gamelog.head(5).iterrows():
            game_date = row.get('gameDate', 'N/A')
            opponent = row.get('opponentAbbrev', 'N/A')
            goals = row.get('goals', 0)
            assists = row.get('assists', 0)
            console.print(f"  {game_date} vs {opponent}: {goals}G, {assists}A")


def demo_team_roster():
    """Demonstrate team roster scraping."""
    console.rule("[bold blue]Team Roster Demo")
    
    team = "TOR"
    season = "20232024"
    
    console.print_info(f"Fetching roster for {team}...")
    roster = scrapeTeamRoster(team, season)
    
    if not roster.empty:
        console.print_success(f"Found {len(roster)} players on roster")
        
        # Count by position
        if 'positionGroup' in roster.columns:
            position_counts = roster['positionGroup'].value_counts()
            console.print("\nRoster breakdown:")
            for pos, count in position_counts.items():
                console.print(f"  {pos.capitalize()}: {count}")


def demo_team_player_stats():
    """Demonstrate team player stats scraping."""
    console.rule("[bold blue]Team Player Stats Demo")
    
    team = "TOR"
    season = "20232024"
    
    console.print_info(f"Fetching all player stats for {team}...")
    
    # This will scrape stats for every player on the roster
    stats = scrapeTeamPlayerStats(team, season, show_progress=True)
    
    if not stats.empty:
        console.print_success(f"Retrieved stats for {len(stats)} players")


def demo_batch_scraper():
    """Demonstrate advanced batch scraping."""
    console.rule("[bold blue]Batch Scraper Demo")
    
    from scrapernhl.nhl.scrapers.games import getGameData
    
    # Some game IDs from 2023-24 season
    game_ids = [2023020001, 2023020002, 2023020003, 2023020004, 2023020005]
    
    console.print_info(f"Using BatchScraper to fetch {len(game_ids)} games...")
    
    # Create batch scraper with rate limiting
    scraper = BatchScraper(
        max_workers=3,
        rate_limit=5.0,  # 5 requests per second
        max_retries=2,
        show_progress=True
    )
    
    result = scraper.scrape_batch(
        game_ids,
        getGameData,
        description="Fetching games"
    )
    
    # Show summary
    console.print("\n[bold]Batch Results:[/bold]")
    summary = result.summary()
    for key, value in summary.items():
        console.print(f"  {key}: {value}")
    
    if result.failed:
        console.print_warning(f"\nFailed items: {[f['item'] for f in result.failed]}")


def demo_season_scraper():
    """Demonstrate season-wide scraping (optional, requires many API calls)."""
    console.rule("[bold blue]Season Scraper Demo")
    
    console.print_warning("This demo scrapes multiple games and may take a while.")
    
    if input("Continue? [y/N]: ").lower() != 'y':
        console.print_info("Skipping season scraper demo")
        return
    
    team = "TOR"
    season = "20232024"
    
    console.print_info(f"Scraping first 10 games for {team} in {season}...")
    
    # Get schedule first to limit games
    from scrapernhl.nhl.scrapers.schedule import getScheduleData
    schedule = getScheduleData(team, season)
    game_ids = [g['id'] for g in schedule[:10] if 'id' in g]
    
    console.print_info(f"Found {len(game_ids)} games")
    
    # Use batch scraper
    from scrapernhl.nhl.scrapers.games import getGameData
    scraper = BatchScraper(max_workers=5, rate_limit=10.0)
    result = scraper.scrape_batch(
        game_ids,
        getGameData,
        description=f"Scraping {team} games"
    )
    
    # Count total plays
    total_plays = sum(len(g.get('plays', [])) for g in result.successful if isinstance(g, dict))
    console.print_success(f"Scraped {total_plays} total plays from {len(result.successful)} games")


def main():
    """Run all demos."""
    console.print("\n[bold green]Phase 3 Features Demo[/bold green]\n")
    
    # Run demos
    demo_player_profile()
    print()
    
    demo_player_season_stats()
    print()
    
    demo_game_log()
    print()
    
    demo_team_roster()
    print()
    
    # Optional: team stats (scrapes many players)
    if input("\nRun team player stats demo? (scrapes all players on roster) [y/N]: ").lower() == 'y':
        demo_team_player_stats()
        print()
    
    demo_batch_scraper()
    print()
    
    # Optional: season scraper (many API calls)
    demo_season_scraper()
    
    console.rule("[bold green]Demo Complete!")


if __name__ == "__main__":
    main()
