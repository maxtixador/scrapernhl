"""
AHL/PWHL Data Cleaning Module

These leagues use a different (cleaner) nested data structure than QMJHL/OHL/WHL.
This module normalizes the AHL/PWHL structure to match the QMJHL flat format,
then applies a simplified cleaning pipeline.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any


def normalize_player_object(player_obj: Dict, prefix: str = "player") -> Dict:
    """
    Normalize AHL/PWHL player object to QMJHL format.
    
    AHL/PWHL: {"id": 123, "firstName": "John", "lastName": "Doe", "jerseyNumber": 9}
    QMJHL: {player}Id, {player}FirstName, {player}LastName, {player}JerseyNumber
    """
    if not isinstance(player_obj, dict):
        return {}
    
    return {
        f"{prefix}Id": player_obj.get("id"),
        f"{prefix}FirstName": player_obj.get("firstName"),
        f"{prefix}LastName": player_obj.get("lastName"),
        f"{prefix}JerseyNumber": player_obj.get("jerseyNumber"),
        f"{prefix}Position": player_obj.get("position"),
    }


def flatten_ahl_pwhl_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a single AHL/PWHL event to QMJHL-compatible format.
    """
    flat = {"event": event.get("event")}
    details = event.get("details", {})
    
    # Extract period
    period_obj = details.get("period", {})
    if isinstance(period_obj, dict):
        flat["period"] = str(period_obj.get("id", "1"))
    
    # Extract time as elapsedTime
    flat["elapsedTime"] = details.get("time")
    
    # Extract team IDs
    flat["team_id"] = details.get("shooterTeamId") or details.get("team_id")
    
    # Extract location
    flat["x_location"] = details.get("xLocation")
    flat["y_location"] = details.get("yLocation")
    
    # Extract shot info
    flat["shot_type"] = details.get("shotType")
    flat["shot_quality_description"] = details.get("shotQuality")
    flat["is_goal"] = details.get("isGoal")
    
    # Handle player objects
    if "shooter" in details and isinstance(details["shooter"], dict):
        flat["shooter_info"] = details["shooter"]
        # Also flatten for compatibility
        flat.update(normalize_player_object(details["shooter"], "player1"))
    
    if "goalie" in details and isinstance(details["goalie"], dict):
        flat["goalie_info"] = details["goalie"]
        flat.update(normalize_player_object(details["goalie"], "goalie"))
    
    if "goalieComingIn" in details and isinstance(details["goalieComingIn"], dict):
        flat.update(normalize_player_object(details["goalieComingIn"], "player1"))
    
    if "goalieGoingOut" in details and isinstance(details["goalieGoingOut"], dict):
        flat.update(normalize_player_object(details["goalieGoingOut"], "player2"))
    
    # Copy any other simple fields
    for key, value in details.items():
        if key not in ["period", "time", "shooter", "goalie", "goalieComingIn", "goalieGoingOut"] and not isinstance(value, (dict, list)):
            flat[key] = value
    
    return flat


def clean_ahl_pwhl(df: pd.DataFrame, nhlify: bool = True) -> pd.DataFrame:
    """
    Clean AHL/PWHL play-by-play data with simplified pipeline.
    
    Args:
        df: Raw DataFrame from AHL/PWHL statviewfeed API
        nhlify: If True, merge shot+goal rows (NHL-style)
    
    Returns:
        Cleaned DataFrame ready for analysis
    """
    # Preserve game_id and league
    game_id = df["game_id"].iloc[0] if "game_id" in df.columns and len(df) > 0 else None
    league = df["league"].iloc[0] if "league" in df.columns and len(df) > 0 else None
    
    # Flatten nested structure
    if len(df) > 0 and "details" in df.columns:
        records = []
        for _, row in df.iterrows():
            event_dict = row.to_dict()
            flat = flatten_ahl_pwhl_event(event_dict)
            records.append(flat)
        df = pd.DataFrame(records)
    
    # Restore metadata
    if game_id is not None:
        df["game_id"] = game_id
    if league is not None:
        df["league"] = league
    
    # Add orderIdx for consistent ordering
    df["orderIdx"] = np.arange(len(df))
    
    # Normalize coordinates (AHL/PWHL uses pixel coordinates)
    if "x_location" in df.columns and "y_location" in df.columns:
        # Convert pixel coords to feet (approximate)
        # HockeyTech uses ~850x400 pixel canvas for 200x85 ft rink
        df["x"] = (df["x_location"] / 850 * 200).round(2)
        df["y"] = (df["y_location"] / 400 * 85).round(2)
        
        # Calculate normalized coordinates (-100 to 100 for x, -42.5 to 42.5 for y)
        df["x_norm"] = df["x"] - 100
        df["y_norm"] = df["y"] - 42.5
        
        # Calculate shot distance and angle
        df["shot_distance_ft"] = np.sqrt(df["x_norm"]**2 + df["y_norm"]**2).round(2)
        df["shot_angle_deg"] = np.degrees(np.arctan2(df["y_norm"].abs(), df["x_norm"].abs())).round(2)
    
    # Handle shot quality
    if "shot_quality_description" in df.columns:
        quality_map = {
            "Quality on net": 3,
            "Standard": 2,
            "Not on net": 1,
        }
        df["quality"] = df["shot_quality_description"].map(quality_map)
    
    # Convert period to numeric where needed
    if "period" in df.columns:
        df["period"] = pd.to_numeric(df["period"], errors="coerce").fillna(1).astype(int)
    
    # Apply nhlify if requested
    if nhlify:
        df = _nhlify_ahl_pwhl(df)
    
    return df


def _nhlify_ahl_pwhl(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge shot+goal rows for AHL/PWHL data (NHL-style).
    
    In AHL/PWHL, goals are marked with isGoal=true on shot events,
    which is different from QMJHL where they're separate events.
    
    We'll look for shot events where isGoal=true and treat those as goals.
    """
    # Check if goals are already separate events
    has_goal_events = "goal" in df["event"].values
    
    if not has_goal_events and "is_goal" in df.columns:
        # Convert shot events with isGoal=true to goal events
        df.loc[df["is_goal"] == True, "event"] = "goal"
    
    # If there are both shot and goal events at same time, merge them (QMJHL-style)
    if has_goal_events:
        # Create shifted columns to find shot before goal
        df = df.sort_values(["period", "elapsedTime", "orderIdx"]).reset_index(drop=True)
        df["_next_event"] = df["event"].shift(-1)
        df["_next_time"] = df["elapsedTime"].shift(-1)
        
        # Find shots followed by goals at same time
        m_shot = df["event"].eq("shot")
        m_goal_after = df["_next_event"].eq("goal")
        m_same_time = df["elapsedTime"].eq(df["_next_time"])
        m_shot_before_goal = m_shot & m_goal_after & m_same_time
        
        if m_shot_before_goal.any():
            shot_indices = df[m_shot_before_goal].index.tolist()
            goal_indices = [idx + 1 for idx in shot_indices if idx + 1 < len(df)]
            
            # Transfer shot data to goal rows
            shot_cols = ["x", "y", "x_norm", "y_norm", "shot_distance_ft", "shot_angle_deg",
                        "shot_type", "shot_quality_description", "quality", "x_location", "y_location"]
            
            for shot_idx, goal_idx in zip(shot_indices, goal_indices):
                for col in shot_cols:
                    if col in df.columns:
                        if pd.isna(df.at[goal_idx, col]) and pd.notna(df.at[shot_idx, col]):
                            df.at[goal_idx, col] = df.at[shot_idx, col]
            
            # Remove redundant shot rows
            df = df.drop(index=shot_indices).reset_index(drop=True)
        
        # Drop helper columns
        df = df.drop(columns=["_next_event", "_next_time"], errors="ignore")
    
    return df


__all__ = ['clean_ahl_pwhl', 'flatten_ahl_pwhl_event', 'normalize_player_object']
