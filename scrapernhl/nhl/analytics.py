"""Advanced analytics and statistical functions for NHL data.

This module provides high-level analytics functions for:
- Shot quality metrics
- Player impact analysis
- Team performance analytics
- Zone start analysis
- Expected goals (xG) calculations
- Scoring chance identification
- Plus/minus calculations

All functions work with pandas or polars DataFrames.
"""

from typing import Union, Optional, List, Dict, Tuple
import numpy as np
import pandas as pd
import polars as pl

from scrapernhl.core.logging_config import get_logger
from scrapernhl.core.progress import console, create_progress_bar
from scrapernhl.exceptions import DataValidationError

LOG = get_logger(__name__)


def _normalize_event_type(event: str) -> str:
    """Normalize event type to standard format.
    
    Converts various event type formats to standard lowercase hyphenated format.
    Handles both API format (SHOT, GOAL, etc.) and typeDescKey format.
    
    Args:
        event: Event type string
        
    Returns:
        Normalized event type
    """
    if pd.isna(event):
        return event
    
    event_lower = str(event).lower().strip()
    
    # Mapping from various formats to standard format
    event_map = {
        # scrape_game uppercase format (EVENT_MAPPING values)
        'shot': 'shot-on-goal',
        'miss': 'missed-shot',
        'block': 'blocked-shot',
        'goal': 'goal',
        'hit': 'hit',
        'give': 'giveaway',
        'take': 'takeaway',
        'penl': 'penalty',
        'fac': 'faceoff',
        # API lowercase format
        'shot-on-goal': 'shot-on-goal',
        'missed-shot': 'missed-shot',
        'blocked-shot': 'blocked-shot',
        'blocked_shot': 'blocked-shot',
        'giveaway': 'giveaway',
        'give away': 'giveaway',
        'takeaway': 'takeaway',
        'take away': 'takeaway',
        'penalty': 'penalty',
        'penaltytaken': 'penalty',
        'faceoff': 'faceoff',
        'face off': 'faceoff',
        'faceoff win': 'faceoff',
    }
    
    return event_map.get(event_lower, event_lower)


def calculate_shot_distance(x: float, y: float, goal_x: float = 89.0) -> float:
    """Calculate shot distance from goal.
    
    Args:
        x: X coordinate of shot
        y: Y coordinate of shot  
        goal_x: X coordinate of goal (default 89.0 for right side)
    
    Returns:
        Distance in feet
    """
    return np.sqrt((x - goal_x)**2 + y**2)


def calculate_shot_angle(x: float, y: float, goal_x: float = 89.0) -> float:
    """Calculate shot angle to goal.
    
    Args:
        x: X coordinate of shot
        y: Y coordinate of shot
        goal_x: X coordinate of goal
    
    Returns:
        Angle in degrees (-90 to 90)
    """
    dx = goal_x - x
    angle = np.degrees(np.arctan2(y, dx))
    return angle


def identify_scoring_chances(
    df: Union[pd.DataFrame, pl.DataFrame],
    distance_col: str = "distanceFromGoal",
    angle_col: str = "angle_signed",
    high_danger_distance: float = 25.0,
    medium_danger_distance: float = 50.0,
    angle_threshold: float = 45.0
) -> Union[pd.DataFrame, pl.DataFrame]:
    """Classify shots into scoring chance categories.
    
    Categories:
    - High Danger: Close (< 25ft) and good angle (< 45°)
    - Medium Danger: Medium distance (< 50ft) or good angle
    - Low Danger: Far distance or poor angle
    
    Args:
        df: DataFrame with shot data
        distance_col: Column name for distance
        angle_col: Column name for angle
        high_danger_distance: Distance threshold for high danger (feet)
        medium_danger_distance: Distance threshold for medium danger (feet)
        angle_threshold: Angle threshold (degrees)
    
    Returns:
        DataFrame with added 'scoring_chance' column
    """
    is_polars = isinstance(df, pl.DataFrame)
    
    if is_polars:
        # Convert to pandas for processing
        df_pd = df.to_pandas()
    else:
        df_pd = df.copy()
    
    # Validate required columns
    if distance_col not in df_pd.columns or angle_col not in df_pd.columns:
        raise DataValidationError(
            f"Required columns missing",
            missing_columns=[col for col in [distance_col, angle_col] if col not in df_pd.columns]
        )
    
    # Determine event type column
    event_col = 'Event' if 'Event' in df_pd.columns else 'typeDescKey'
    
    # Only classify shots/goals/misses
    if event_col == 'Event':
        shot_mask = df_pd['Event'].isin(['SHOT', 'GOAL', 'MISS'])
    else:
        shot_mask = df_pd['typeDescKey'].isin(['shot-on-goal', 'goal', 'missed-shot'])
    
    # Calculate scoring chance only for shots
    def classify_shot(row):
        distance = abs(row[distance_col])
        angle = abs(row[angle_col])
        
        if distance < high_danger_distance and angle < angle_threshold:
            return "high"
        elif distance < medium_danger_distance or angle < angle_threshold:
            return "medium"
        else:
            return "low"
    
    # Initialize with NaN for all events
    df_pd['scoring_chance'] = pd.NA
    # Only classify shot events
    df_pd.loc[shot_mask, 'scoring_chance'] = df_pd[shot_mask].apply(classify_shot, axis=1)
    
    if is_polars:
        return pl.from_pandas(df_pd)
    return df_pd


def prepare_pbp_with_xg(
    df: pd.DataFrame,
    goal_x: float = 89.0,
    goal_y: float = 0.0,
    rebound_window_s: int = 3
) -> pd.DataFrame:
    """Convenience function to engineer xG features and predict xG in one call.
    
    This combines engineer_xg_features() and predict_xg_for_pbp() into a single
    function for easier use.
    
    Args:
        df: Play-by-play DataFrame
        goal_x: X coordinate of goal (default 89.0)
        goal_y: Y coordinate of goal (default 0.0)
        rebound_window_s: Time window in seconds to identify rebounds (default 3)
    
    Returns:
        DataFrame with xG features and predictions added
    
    Example:
        >>> from scrapernhl import scrape_game, prepare_pbp_with_xg
        >>> game_tuple = scrape_game(game_id=2024020001, include_tuple=True)
        >>> pbp_with_xg = prepare_pbp_with_xg(game_tuple.data)
    """
    from scrapernhl.nhl.scraper_legacy import engineer_xg_features, predict_xg_for_pbp
    
    # Engineer features
    df_with_features = engineer_xg_features(
        df,
        goal_x=goal_x,
        goal_y=goal_y,
        rebound_window_s=rebound_window_s
    )
    
    # Predict xG
    df_with_xg = predict_xg_for_pbp(df_with_features)
    
    return df_with_xg


def calculate_corsi(
    df: Union[pd.DataFrame, pl.DataFrame],
    team: str,
    event_col: str = "Event",
    team_col: str = "eventTeam"
) -> Dict[str, int]:
    """Calculate Corsi (shot attempts) for a team.
    
    Corsi = Shots + Missed Shots + Blocked Shots
    
    Args:
        df: DataFrame with event data
        team: Team abbreviation
        event_col: Column with event types (default "Event" from scrape_game)
        team_col: Column with team that generated event (default "eventTeam" from scrape_game)
    
    Returns:
        Dictionary with corsi_for, corsi_against, corsi_differential
    """
    is_polars = isinstance(df, pl.DataFrame)
    
    if is_polars:
        df_pd = df.to_pandas()
    else:
        df_pd = df
    
    # Check which column names exist
    if event_col not in df_pd.columns:
        # Try alternative column name
        event_col = 'typeDescKey' if 'typeDescKey' in df_pd.columns else event_col
    if team_col not in df_pd.columns:
        # Try alternative column name
        team_col = 'eventOwnerTeam' if 'eventOwnerTeam' in df_pd.columns else team_col
    
    # Normalize event types
    df_pd = df_pd.copy()
    df_pd['_normalized_event'] = df_pd[event_col].apply(_normalize_event_type)
    
    # Shot attempt events
    shot_events = ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal']
    
    shot_attempts = df_pd[df_pd['_normalized_event'].isin(shot_events)]
    
    corsi_for = len(shot_attempts[shot_attempts[team_col] == team])
    corsi_against = len(shot_attempts[shot_attempts[team_col] != team])
    
    return {
        'corsi_for': corsi_for,
        'corsi_against': corsi_against,
        'corsi_differential': corsi_for - corsi_against,
        'corsi_percentage': (corsi_for / (corsi_for + corsi_against) * 100) if (corsi_for + corsi_against) > 0 else 0.0
    }


def calculate_fenwick(
    df: Union[pd.DataFrame, pl.DataFrame],
    team: str,
    event_col: str = "Event",
    team_col: str = "eventTeam"
) -> Dict[str, int]:
    """Calculate Fenwick (unblocked shot attempts) for a team.
    
    Fenwick = Shots + Missed Shots (excludes blocked shots)
    
    Args:
        df: DataFrame with event data
        team: Team abbreviation
        event_col: Column with event types (default "Event" from scrape_game)
        team_col: Column with team that generated event (default "eventTeam" from scrape_game)
    
    Returns:
        Dictionary with fenwick_for, fenwick_against, fenwick_differential
    """
    is_polars = isinstance(df, pl.DataFrame)
    
    if is_polars:
        df_pd = df.to_pandas()
    else:
        df_pd = df
    
    # Check which column names exist
    if event_col not in df_pd.columns:
        # Try alternative column name
        event_col = 'typeDescKey' if 'typeDescKey' in df_pd.columns else event_col
    if team_col not in df_pd.columns:
        # Try alternative column name
        team_col = 'eventOwnerTeam' if 'eventOwnerTeam' in df_pd.columns else team_col
    
    # Normalize event types
    df_pd = df_pd.copy()
    df_pd['_normalized_event'] = df_pd[event_col].apply(_normalize_event_type)
    
    # Unblocked shot attempt events
    shot_events = ['shot-on-goal', 'missed-shot', 'goal']
    
    shot_attempts = df_pd[df_pd['_normalized_event'].isin(shot_events)]
    
    fenwick_for = len(shot_attempts[shot_attempts[team_col] == team])
    fenwick_against = len(shot_attempts[shot_attempts[team_col] != team])
    
    return {
        'fenwick_for': fenwick_for,
        'fenwick_against': fenwick_against,
        'fenwick_differential': fenwick_for - fenwick_against,
        'fenwick_percentage': (fenwick_for / (fenwick_for + fenwick_against) * 100) if (fenwick_for + fenwick_against) > 0 else 0.0
    }


def calculate_player_toi(
    shifts_df: Union[pd.DataFrame, pl.DataFrame],
    player_id: Union[str, int],
    player_id_col: str = "playerId"
) -> Dict[str, float]:
    """Calculate time on ice statistics for a player.
    
    Args:
        shifts_df: DataFrame with shift data
        player_id: Player ID to calculate TOI for
        player_id_col: Column name for player ID
    
    Returns:
        Dictionary with total_toi, avg_shift_length, num_shifts
    """
    is_polars = isinstance(shifts_df, pl.DataFrame)
    
    if is_polars:
        df_pd = shifts_df.to_pandas()
    else:
        df_pd = shifts_df
    
    player_shifts = df_pd[df_pd[player_id_col] == str(player_id)]
    
    if 'duration' in player_shifts.columns:
        total_toi = player_shifts['duration'].sum()
        avg_shift = player_shifts['duration'].mean()
    elif 'shiftDuration' in player_shifts.columns:
        total_toi = player_shifts['shiftDuration'].sum()
        avg_shift = player_shifts['shiftDuration'].mean()
    else:
        total_toi = 0.0
        avg_shift = 0.0
    
    return {
        'total_toi': total_toi,
        'avg_shift_length': avg_shift,
        'num_shifts': len(player_shifts),
        'total_toi_minutes': total_toi / 60.0
    }


def calculate_zone_start_percentage(
    shifts_df: Union[pd.DataFrame, pl.DataFrame],
    player_id: Union[str, int],
    zone_col: str = "zoneStartType"
) -> Dict[str, float]:
    """Calculate zone start percentages for a player.
    
    Args:
        shifts_df: DataFrame with shift data including zone starts
        player_id: Player ID
        zone_col: Column with zone start type
    
    Returns:
        Dictionary with offensive, defensive, neutral, on_the_fly percentages
    """
    is_polars = isinstance(shifts_df, pl.DataFrame)
    
    if is_polars:
        df_pd = shifts_df.to_pandas()
    else:
        df_pd = shifts_df
    
    player_shifts = df_pd[df_pd['playerId'] == str(player_id)]
    
    if zone_col not in player_shifts.columns:
        LOG.warning(f"Zone start column '{zone_col}' not found")
        return {
            'offensive_zone_starts': 0,
            'defensive_zone_starts': 0,
            'neutral_zone_starts': 0,
            'on_the_fly': 0,
            'total_zone_starts': 0,
            'offensive_zone_start_pct': 0.0
        }
    
    # Count by zone
    zone_counts = player_shifts[zone_col].value_counts()
    
    offensive = zone_counts.get('O', 0)
    defensive = zone_counts.get('D', 0)
    neutral = zone_counts.get('N', 0)
    on_the_fly = zone_counts.get('OTF', 0)
    
    total_zone_starts = offensive + defensive + neutral
    offensive_pct = (offensive / total_zone_starts * 100) if total_zone_starts > 0 else 0.0
    
    return {
        'offensive_zone_starts': offensive,
        'defensive_zone_starts': defensive,
        'neutral_zone_starts': neutral,
        'on_the_fly': on_the_fly,
        'total_zone_starts': total_zone_starts,
        'offensive_zone_start_pct': offensive_pct
    }


def calculate_team_stats_summary(
    plays_df: Union[pd.DataFrame, pl.DataFrame],
    team: str,
    include_advanced: bool = True
) -> Dict[str, any]:
    """Calculate comprehensive team statistics summary.
    
    Args:
        plays_df: DataFrame with play-by-play data
        team: Team abbreviation
        include_advanced: Include advanced stats (Corsi, Fenwick)
    
    Returns:
        Dictionary with team statistics
    """
    is_polars = isinstance(plays_df, pl.DataFrame)
    
    if is_polars:
        df_pd = plays_df.to_pandas()
    else:
        df_pd = plays_df
    
    stats = {}
    
    # Determine which column names to use
    event_col = 'Event' if 'Event' in df_pd.columns else 'typeDescKey'
    team_col = 'eventTeam' if 'eventTeam' in df_pd.columns else 'eventOwnerTeam'
    
    # Normalize event types
    df_pd = df_pd.copy()
    df_pd['_normalized_event'] = df_pd[event_col].apply(_normalize_event_type)
    
    # Basic stats
    team_events = df_pd[df_pd[team_col] == team]
    
    stats['goals'] = len(team_events[team_events['_normalized_event'] == 'goal'])
    stats['shots'] = len(team_events[team_events['_normalized_event'] == 'shot-on-goal'])
    stats['shot_percentage'] = (stats['goals'] / stats['shots'] * 100) if stats['shots'] > 0 else 0.0
    
    stats['hits'] = len(team_events[team_events['_normalized_event'] == 'hit'])
    stats['giveaways'] = len(team_events[team_events['_normalized_event'] == 'giveaway'])
    stats['takeaways'] = len(team_events[team_events['_normalized_event'] == 'takeaway'])
    stats['penalties'] = len(team_events[team_events['_normalized_event'] == 'penalty'])
    
    # Faceoffs (need to check both teams)
    faceoffs = df_pd[df_pd['_normalized_event'] == 'faceoff']
    team_faceoffs = faceoffs[faceoffs[team_col] == team]
    stats['faceoff_wins'] = len(team_faceoffs)
    stats['faceoff_total'] = len(faceoffs)
    stats['faceoff_percentage'] = (stats['faceoff_wins'] / stats['faceoff_total'] * 100) if stats['faceoff_total'] > 0 else 0.0
    
    # Advanced stats
    if include_advanced:
        stats['corsi'] = calculate_corsi(df_pd, team, event_col=event_col, team_col=team_col)
        stats['fenwick'] = calculate_fenwick(df_pd, team, event_col=event_col, team_col=team_col)
    
    return stats


def calculate_player_stats_summary(
    plays_df: Union[pd.DataFrame, pl.DataFrame],
    shifts_df: Optional[Union[pd.DataFrame, pl.DataFrame]],
    player_id: Union[str, int]
) -> Dict[str, any]:
    """Calculate comprehensive player statistics summary.
    
    Args:
        plays_df: DataFrame with play-by-play data
        shifts_df: Optional DataFrame with shift data
        player_id: Player ID
    
    Returns:
        Dictionary with player statistics
    """
    is_polars = isinstance(plays_df, pl.DataFrame)
    
    if is_polars:
        df_pd = plays_df.to_pandas()
    else:
        df_pd = plays_df
    
    stats = {'player_id': str(player_id)}
    
    # Basic event stats
    if 'details.eventOwnerPlayerId' in df_pd.columns:
        player_events = df_pd[df_pd['details.eventOwnerPlayerId'] == str(player_id)]
        
        if 'typeDescKey' in player_events.columns:
            stats['goals'] = len(player_events[player_events['typeDescKey'] == 'goal'])
            stats['shots'] = len(player_events[player_events['typeDescKey'] == 'shot-on-goal'])
            stats['hits'] = len(player_events[player_events['typeDescKey'] == 'hit'])
            stats['takeaways'] = len(player_events[player_events['typeDescKey'] == 'takeaway'])
            stats['giveaways'] = len(player_events[player_events['typeDescKey'] == 'giveaway'])
    
    # Shift stats
    if shifts_df is not None:
        toi_stats = calculate_player_toi(shifts_df, player_id)
        stats.update(toi_stats)
        
        zone_stats = calculate_zone_start_percentage(shifts_df, player_id)
        stats.update(zone_stats)
    
    return stats


def calculate_score_effects(
    df: Union[pd.DataFrame, pl.DataFrame],
    team: str,
    score_diff_col: str = "scoreDiff"
) -> Dict[str, Dict]:
    """Analyze team performance by score differential.
    
    Args:
        df: DataFrame with event data
        team: Team abbreviation
        score_diff_col: Column with score differential
    
    Returns:
        Dictionary with stats broken down by score situation
    """
    is_polars = isinstance(df, pl.DataFrame)
    
    if is_polars:
        df_pd = df.to_pandas()
    else:
        df_pd = df
    
    results = {}
    
    # Define score situations
    situations = {
        'trailing': df_pd[score_diff_col] < -1,
        'down_one': df_pd[score_diff_col] == -1,
        'tied': df_pd[score_diff_col] == 0,
        'up_one': df_pd[score_diff_col] == 1,
        'leading': df_pd[score_diff_col] > 1
    }
    
    for situation_name, mask in situations.items():
        situation_df = df_pd[mask]
        if len(situation_df) > 0:
            results[situation_name] = calculate_corsi(situation_df, team)
            results[situation_name]['events'] = len(situation_df)
        else:
            results[situation_name] = {'events': 0}
    
    return results


def analyze_shooting_patterns(
    df: Union[pd.DataFrame, pl.DataFrame],
    distance_bins: List[Tuple[float, float]] = [(0, 20), (20, 40), (40, 60), (60, 100)],
    x_col: str = "details.xCoord",
    y_col: str = "details.yCoord"
) -> pd.DataFrame:
    """Analyze shooting patterns by distance and location.
    
    Args:
        df: DataFrame with shot data
        distance_bins: List of (min, max) distance bins
        x_col: Column with X coordinate
        y_col: Column with Y coordinate
    
    Returns:
        DataFrame with shooting statistics by distance bin
    """
    is_polars = isinstance(df, pl.DataFrame)
    
    if is_polars:
        df_pd = df.to_pandas()
    else:
        df_pd = df.copy()
    
    # Filter to shots only - handle both event type formats
    event_type_col = 'Event' if 'Event' in df_pd.columns else 'typeDescKey'
    
    if event_type_col == 'Event':
        # scrape_game format: uppercase SHOT, GOAL, MISS
        shots = df_pd[df_pd['Event'].isin(['SHOT', 'GOAL', 'MISS'])].copy()
    else:
        # Legacy format: lowercase hyphenated
        shots = df_pd[df_pd['typeDescKey'].isin(['shot-on-goal', 'goal', 'missed-shot'])].copy()
    
    # Calculate distance if not present
    if 'distanceFromGoal' not in shots.columns and x_col in shots.columns and y_col in shots.columns:
        shots['distanceFromGoal'] = shots.apply(
            lambda row: calculate_shot_distance(row[x_col], row[y_col]),
            axis=1
        )
    
    # Bin by distance
    results = []
    for min_dist, max_dist in distance_bins:
        bin_shots = shots[(shots['distanceFromGoal'] >= min_dist) & (shots['distanceFromGoal'] < max_dist)]
        
        total_shots = len(bin_shots)
        # Check for goal in the correct column
        if event_type_col == 'Event':
            goals = len(bin_shots[bin_shots['Event'] == 'GOAL'])
        else:
            goals = len(bin_shots[bin_shots['typeDescKey'] == 'goal'])
        
        results.append({
            'distance_range': f"{min_dist}-{max_dist}ft",
            'total_shots': total_shots,
            'goals': goals,
            'shooting_percentage': (goals / total_shots * 100) if total_shots > 0 else 0.0
        })
    
    return pd.DataFrame(results)


def create_analytics_report(
    plays_df: Union[pd.DataFrame, pl.DataFrame],
    shifts_df: Optional[Union[pd.DataFrame, pl.DataFrame]],
    team: str,
    output_format: str = "dict"
) -> Union[Dict, pd.DataFrame]:
    """Create comprehensive analytics report for a team.
    
    Args:
        plays_df: DataFrame with play-by-play data
        shifts_df: Optional DataFrame with shift data
        team: Team abbreviation
        output_format: "dict" or "dataframe"
    
    Returns:
        Comprehensive analytics report
    """
    console.print_info(f"Generating analytics report for {team}...")
    
    report = {
        'team': team,
        'generated_at': pd.Timestamp.now().isoformat()
    }
    
    # Team stats
    report['team_stats'] = calculate_team_stats_summary(plays_df, team, include_advanced=True)
    
    # Score effects
    if 'scoreDiff' in plays_df.columns:
        report['score_effects'] = calculate_score_effects(plays_df, team)
    
    # Shooting patterns - filter to team's events only
    # Determine event team column
    event_team_col = 'eventTeam' if 'eventTeam' in plays_df.columns else 'eventOwnerTeam'
    team_plays = plays_df[plays_df[event_team_col] == team]
    report['shooting_patterns'] = analyze_shooting_patterns(team_plays).to_dict('records')
    
    console.print_success("Analytics report generated")
    
    if output_format == "dataframe":
        return pd.DataFrame([report])
    
    return report
