"""Demo script showcasing Phase 4 features: Analytics and Visualization.

This script demonstrates the new analytics functions and visualization
utilities added in Phase 4.

Usage:
    python examples/phase4_demo.py
"""

from scrapernhl import (
    console,
    create_table,
    # Analytics
    identify_scoring_chances,
    calculate_corsi,
    calculate_fenwick,
    calculate_team_stats_summary,
    analyze_shooting_patterns,
    create_analytics_report,
    # Visualization
    display_team_stats,
    display_advanced_stats,
    display_scoring_chances,
    display_shooting_patterns,
    display_score_effects,
    print_analytics_summary,
)
from scrapernhl.nhl.scrapers.games import scrapePlays


def demo_scoring_chances():
    """Demonstrate scoring chance classification."""
    console.rule("[bold blue]Scoring Chance Classification Demo")
    
    # Get some play data
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    # Filter to shots
    shots = plays[plays['typeDescKey'].isin(['shot-on-goal', 'goal', 'missed-shot'])]
    
    if len(shots) == 0:
        console.print_warning("No shots found in game")
        return
    
    console.print_success(f"Found {len(shots)} shots")
    
    # Classify scoring chances
    console.print_info("Classifying scoring chances...")
    shots_with_chances = identify_scoring_chances(shots)
    
    # Display breakdown
    display_scoring_chances(shots_with_chances)


def demo_advanced_stats():
    """Demonstrate Corsi and Fenwick calculations."""
    console.rule("[bold blue]Advanced Statistics Demo")
    
    # Get game data
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    # Get teams
    if 'eventOwnerTeam' in plays.columns:
        teams = plays['eventOwnerTeam'].unique()
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            
            console.print_info(f"Analyzing {team1} vs {team2}")
            
            # Calculate Corsi and Fenwick
            team1_corsi = calculate_corsi(plays, team1)
            team1_fenwick = calculate_fenwick(plays, team1)
            
            team2_corsi = calculate_corsi(plays, team2)
            team2_fenwick = calculate_fenwick(plays, team2)
            
            # Display
            console.print(f"\n[bold]{team1} Advanced Stats:[/bold]")
            display_advanced_stats(team1_corsi, team1_fenwick, title=f"{team1} Stats")
            
            console.print(f"\n[bold]{team2} Advanced Stats:[/bold]")
            display_advanced_stats(team2_corsi, team2_fenwick, title=f"{team2} Stats")


def demo_shooting_patterns():
    """Demonstrate shooting pattern analysis."""
    console.rule("[bold blue]Shooting Patterns Demo")
    
    # Get game data
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    # Analyze shooting patterns
    console.print_info("Analyzing shooting patterns...")
    shooting_df = analyze_shooting_patterns(plays)
    
    # Display
    display_shooting_patterns(shooting_df)


def demo_team_stats_summary():
    """Demonstrate comprehensive team statistics."""
    console.rule("[bold blue]Team Statistics Summary Demo")
    
    # Get game data
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    if 'eventOwnerTeam' in plays.columns:
        teams = plays['eventOwnerTeam'].unique()
        if len(teams) >= 1:
            team = teams[0]
            
            console.print_info(f"Calculating stats for {team}...")
            stats = calculate_team_stats_summary(plays, team, include_advanced=True)
            
            # Display
            display_team_stats({'team': team, 'team_stats': stats})
            
            # Show advanced stats separately
            if 'corsi' in stats and 'fenwick' in stats:
                console.print()
                display_advanced_stats(stats['corsi'], stats['fenwick'])


def demo_analytics_report():
    """Demonstrate comprehensive analytics report."""
    console.rule("[bold blue]Analytics Report Demo")
    
    # Get game data
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    if 'eventOwnerTeam' in plays.columns:
        teams = plays['eventOwnerTeam'].unique()
        if len(teams) >= 1:
            team = teams[0]
            
            # Create report
            console.print_info(f"Generating analytics report for {team}...")
            report = create_analytics_report(plays, None, team)
            
            # Display full report
            print_analytics_summary(report)


def demo_score_effects():
    """Demonstrate score effects analysis."""
    console.rule("[bold blue]Score Effects Demo")
    
    # Get game data
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    # Need scoreDiff column
    if 'scoreDiff' not in plays.columns:
        console.print_warning("scoreDiff column not found, skipping demo")
        return
    
    if 'eventOwnerTeam' in plays.columns:
        teams = plays['eventOwnerTeam'].unique()
        if len(teams) >= 1:
            team = teams[0]
            
            # Calculate score effects
            from scrapernhl.analytics import calculate_score_effects
            console.print_info(f"Analyzing score effects for {team}...")
            score_effects = calculate_score_effects(plays, team)
            
            # Display
            display_score_effects(score_effects)


def demo_custom_analysis():
    """Demonstrate custom analysis workflow."""
    console.rule("[bold blue]Custom Analysis Workflow Demo")
    
    console.print_info("Fetching game data...")
    plays = scrapePlays(2023020001)
    
    # Filter to goals only
    goals = plays[plays['typeDescKey'] == 'goal']
    
    console.print_success(f"Found {len(goals)} goals")
    
    if len(goals) > 0:
        # Classify goals by scoring chance
        goals_with_chances = identify_scoring_chances(goals)
        
        # Count by type
        if 'scoring_chance' in goals_with_chances.columns:
            chance_counts = goals_with_chances['scoring_chance'].value_counts()
            
            table = create_table("Goals by Scoring Chance", ["Type", "Count", "Percentage"])
            
            total = len(goals_with_chances)
            for chance_type in ['high', 'medium', 'low']:
                count = chance_counts.get(chance_type, 0)
                pct = (count / total * 100) if total > 0 else 0
                table.add_row(
                    chance_type.capitalize(),
                    str(count),
                    f"{pct:.1f}%"
                )
            
            console.print(table)


def main():
    """Run all demos."""
    console.print("\n[bold green]Phase 4 Features Demo: Analytics & Visualization[/bold green]\n")
    
    # Run demos
    demo_scoring_chances()
    print()
    
    demo_advanced_stats()
    print()
    
    demo_shooting_patterns()
    print()
    
    demo_team_stats_summary()
    print()
    
    # Optional: score effects (requires scoreDiff column)
    if input("\nRun score effects demo? [y/N]: ").lower() == 'y':
        demo_score_effects()
        print()
    
    demo_custom_analysis()
    print()
    
    # Optional: full analytics report
    if input("\nRun full analytics report demo? [y/N]: ").lower() == 'y':
        demo_analytics_report()
    
    console.rule("[bold green]Demo Complete!")
    
    # Summary
    console.print("\n[bold]What's included in Phase 4:[/bold]")
    console.print("  • Scoring chance classification (high/medium/low danger)")
    console.print("  • Advanced stats (Corsi, Fenwick)")
    console.print("  • Shooting pattern analysis by distance")
    console.print("  • Team statistics summaries")
    console.print("  • Score effects analysis")
    console.print("  • Player TOI and zone start calculations")
    console.print("  • Rich-formatted visualizations")
    console.print("  • Comprehensive analytics reports")


if __name__ == "__main__":
    main()
