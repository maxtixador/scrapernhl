"""Visualization helpers for NHL analytics.

This module provides utilities for creating visualizations and formatted
reports of NHL data using Rich tables and console output.
"""

from typing import Union, List, Dict, Optional
import pandas as pd
import polars as pl

from scrapernhl.core.progress import console, create_table
from scrapernhl.core.logging_config import get_logger

LOG = get_logger(__name__)


def display_team_stats(
    stats: Dict,
    title: Optional[str] = None
) -> None:
    """Display team statistics in a formatted table.
    
    Args:
        stats: Dictionary with team statistics
        title: Optional title for the table
    """
    if title is None:
        title = f"Team Statistics - {stats.get('team', 'Unknown')}"
    
    table = create_table(title=title, columns=["Metric", "Value"])
    
    # Basic stats
    if 'team_stats' in stats:
        team_stats = stats['team_stats']
        for key, value in team_stats.items():
            if not isinstance(value, dict):
                formatted_value = f"{value:.1f}" if isinstance(value, float) else str(value)
                table.add_row(key.replace('_', ' ').title(), formatted_value)
    else:
        for key, value in stats.items():
            if not isinstance(value, dict):
                formatted_value = f"{value:.1f}" if isinstance(value, float) else str(value)
                table.add_row(key.replace('_', ' ').title(), formatted_value)
    
    console.print(table)


def display_advanced_stats(
    corsi: Dict,
    fenwick: Dict,
    title: str = "Advanced Statistics"
) -> None:
    """Display advanced statistics (Corsi/Fenwick) in formatted table.
    
    Args:
        corsi: Corsi statistics dictionary
        fenwick: Fenwick statistics dictionary
        title: Table title
    """
    table = create_table(title=title, columns=["Metric", "For", "Against", "Differential", "%"])
    
    # Corsi row
    table.add_row(
        "Corsi",
        str(corsi.get('corsi_for', 0)),
        str(corsi.get('corsi_against', 0)),
        str(corsi.get('corsi_differential', 0)),
        f"{corsi.get('corsi_percentage', 0):.1f}%"
    )
    
    # Fenwick row
    table.add_row(
        "Fenwick",
        str(fenwick.get('fenwick_for', 0)),
        str(fenwick.get('fenwick_against', 0)),
        str(fenwick.get('fenwick_differential', 0)),
        f"{fenwick.get('fenwick_percentage', 0):.1f}%"
    )
    
    console.print(table)


def display_player_summary(
    stats: Dict,
    player_name: Optional[str] = None
) -> None:
    """Display player statistics summary.
    
    Args:
        stats: Dictionary with player statistics
        player_name: Optional player name for title
    """
    title = f"Player Summary - {player_name}" if player_name else "Player Summary"
    
    table = create_table(title=title, columns=["Category", "Value"])
    
    # Offensive stats
    if 'goals' in stats or 'shots' in stats:
        table.add_row("Goals", str(stats.get('goals', 0)))
        table.add_row("Shots", str(stats.get('shots', 0)))
        table.add_row("Hits", str(stats.get('hits', 0)))
        table.add_row("Takeaways", str(stats.get('takeaways', 0)))
        table.add_row("Giveaways", str(stats.get('giveaways', 0)))
    
    # TOI stats
    if 'total_toi_minutes' in stats:
        table.add_row("Total TOI", f"{stats['total_toi_minutes']:.1f} min")
        table.add_row("Shifts", str(stats.get('num_shifts', 0)))
        table.add_row("Avg Shift", f"{stats.get('avg_shift_length', 0):.1f}s")
    
    # Zone start stats
    if 'offensive_zone_starts' in stats:
        table.add_row("Offensive Zone Starts", str(stats['offensive_zone_starts']))
        table.add_row("Defensive Zone Starts", str(stats['defensive_zone_starts']))
        table.add_row("OZS%", f"{stats.get('offensive_zone_start_pct', 0):.1f}%")
    
    console.print(table)


def display_scoring_chances(
    df: Union[pd.DataFrame, pl.DataFrame],
    team: Optional[str] = None
) -> None:
    """Display scoring chance breakdown.
    
    Args:
        df: DataFrame with scoring_chance column
        team: Optional team to filter by
    """
    is_polars = isinstance(df, pl.DataFrame)
    
    if is_polars:
        df_pd = df.to_pandas()
    else:
        df_pd = df
    
    if team:
        df_pd = df_pd[df_pd.get('eventOwnerTeam', df_pd.get('team')) == team]
    
    if 'scoring_chance' not in df_pd.columns:
        console.print_warning("No scoring_chance column found")
        return
    
    chance_counts = df_pd['scoring_chance'].value_counts()
    total = len(df_pd)
    
    title = f"Scoring Chances - {team}" if team else "Scoring Chances"
    table = create_table(title=title, columns=["Category", "Count", "Percentage"])
    
    for chance_type in ['high', 'medium', 'low']:
        count = chance_counts.get(chance_type, 0)
        pct = (count / total * 100) if total > 0 else 0
        table.add_row(
            chance_type.capitalize(),
            str(count),
            f"{pct:.1f}%"
        )
    
    console.print(table)


def display_shooting_patterns(
    shooting_df: pd.DataFrame,
    title: str = "Shooting Patterns by Distance"
) -> None:
    """Display shooting patterns analysis.
    
    Args:
        shooting_df: DataFrame from analyze_shooting_patterns()
        title: Table title
    """
    table = create_table(title=title, columns=["Distance", "Shots", "Goals", "Shooting %"])
    
    for _, row in shooting_df.iterrows():
        table.add_row(
            row['distance_range'],
            str(row['total_shots']),
            str(row['goals']),
            f"{row['shooting_percentage']:.1f}%"
        )
    
    console.print(table)


def display_score_effects(
    score_effects: Dict,
    title: str = "Performance by Score Differential"
) -> None:
    """Display score effects analysis.
    
    Args:
        score_effects: Dictionary from calculate_score_effects()
        title: Table title
    """
    table = create_table(title=title, columns=["Situation", "Events", "CF", "CA", "CF%"])
    
    situations = ['trailing', 'down_one', 'tied', 'up_one', 'leading']
    situation_labels = ['Trailing by 2+', 'Down by 1', 'Tied', 'Up by 1', 'Leading by 2+']
    
    for situation, label in zip(situations, situation_labels):
        if situation in score_effects:
            data = score_effects[situation]
            table.add_row(
                label,
                str(data.get('events', 0)),
                str(data.get('corsi_for', 0)),
                str(data.get('corsi_against', 0)),
                f"{data.get('corsi_percentage', 0):.1f}%"
            )
    
    console.print(table)


def display_game_summary(
    game_data: Dict,
    show_scoring: bool = True,
    show_stats: bool = True
) -> None:
    """Display comprehensive game summary.
    
    Args:
        game_data: Game data dictionary
        show_scoring: Show scoring summary
        show_stats: Show team statistics
    """
    # Game header
    home_team = game_data.get('homeTeam', {}).get('abbrev', 'HOME')
    away_team = game_data.get('awayTeam', {}).get('abbrev', 'AWAY')
    
    console.rule(f"[bold cyan]{away_team} @ {home_team}")
    
    # Score
    if show_scoring and 'homeTeam' in game_data and 'awayTeam' in game_data:
        away_score = game_data['awayTeam'].get('score', 0)
        home_score = game_data['homeTeam'].get('score', 0)
        
        console.print(f"\n[bold]Final Score:[/bold] {away_team} {away_score} - {home_team} {home_score}\n")
    
    # Team stats
    if show_stats and 'homeTeam' in game_data and 'awayTeam' in game_data:
        home_stats = game_data['homeTeam']
        away_stats = game_data['awayTeam']
        
        table = create_table(title="Team Statistics", columns=["Stat", away_team, home_team])
        
        stats_to_show = [
            ('sog', 'Shots on Goal'),
            ('faceoffWinningPctg', 'Faceoff %'),
            ('powerPlayGoals', 'PP Goals'),
            ('pim', 'Penalty Minutes'),
            ('hits', 'Hits'),
            ('blocks', 'Blocks')
        ]
        
        for key, label in stats_to_show:
            away_val = away_stats.get(key, 'N/A')
            home_val = home_stats.get(key, 'N/A')
            
            if isinstance(away_val, float):
                away_val = f"{away_val:.1f}"
            if isinstance(home_val, float):
                home_val = f"{home_val:.1f}"
            
            table.add_row(label, str(away_val), str(home_val))
        
        console.print(table)


def display_top_players(
    players_df: Union[pd.DataFrame, pl.DataFrame],
    stat: str = 'goals',
    n: int = 10,
    title: Optional[str] = None
) -> None:
    """Display top N players by a statistic.
    
    Args:
        players_df: DataFrame with player statistics
        stat: Statistic to sort by
        n: Number of players to show
        title: Optional title
    """
    is_polars = isinstance(players_df, pl.DataFrame)
    
    if is_polars:
        df_pd = players_df.to_pandas()
    else:
        df_pd = players_df
    
    if stat not in df_pd.columns:
        console.print_error(f"Column '{stat}' not found")
        return
    
    if title is None:
        title = f"Top {n} Players - {stat.replace('_', ' ').title()}"
    
    top_players = df_pd.nlargest(n, stat)
    
    # Determine columns to show
    display_cols = ['player', 'firstName', 'lastName', 'playerId']
    name_col = next((col for col in display_cols if col in top_players.columns), None)
    
    table = create_table(title=title, columns=["Rank", "Player", stat.replace('_', ' ').title()])
    
    for i, (_, row) in enumerate(top_players.iterrows(), 1):
        player_name = row.get(name_col, f"Player {row.get('playerId', 'Unknown')}")
        value = row[stat]
        
        formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
        table.add_row(str(i), str(player_name), formatted_value)
    
    console.print(table)


def print_analytics_summary(report: Dict) -> None:
    """Print comprehensive analytics report to console.
    
    Args:
        report: Analytics report dictionary from create_analytics_report()
    """
    console.rule(f"[bold green]Analytics Report - {report.get('team', 'Unknown')}")
    
    console.print(f"\n[dim]Generated: {report.get('generated_at', 'N/A')}[/dim]\n")
    
    # Team stats
    if 'team_stats' in report:
        display_team_stats(report, title="Team Statistics")
        console.print()
    
    # Advanced stats
    if 'team_stats' in report:
        team_stats = report['team_stats']
        if 'corsi' in team_stats and 'fenwick' in team_stats:
            display_advanced_stats(team_stats['corsi'], team_stats['fenwick'])
            console.print()
    
    # Score effects
    if 'score_effects' in report:
        display_score_effects(report['score_effects'])
        console.print()
    
    # Shooting patterns
    if 'shooting_patterns' in report:
        shooting_df = pd.DataFrame(report['shooting_patterns'])
        display_shooting_patterns(shooting_df)
    
    console.rule("[bold green]End of Report")
