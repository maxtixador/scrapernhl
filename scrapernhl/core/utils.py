"""utils.py : Utility functions for NHL data scraping."""

from typing import Dict, List, Optional, Sequence

import pandas as pd
import polars as pl
import numpy as np
from scrapernhl.config import DEFAULT_HEADERS, DEFAULT_TIMEOUT, _DOT_XY, _DOT_LABELS

def time_str_to_seconds(time_str: Optional[str]) -> Optional[int]:
    """Convert a time string in 'MM:SS' format to total seconds."""
    if not time_str or not isinstance(time_str, str):
        return None
    try:
        m, s = time_str.split(":")
        return int(m) * 60 + int(s)
    except Exception:
        return None
    
def _group_merge_index(df: pd.DataFrame, keys: Sequence[str], out_col: str = "merge_idx") -> pd.Series:
    """Helper to create a merge index for deduplication."""
    k = df[keys].astype(str).agg("|".join, axis=1)
    return k.groupby(k).cumcount().rename(out_col)

def _dedup_cols(cols: pd.Index) -> pd.Index:
    """Helper to deduplicate column names by appending suffixes."""
    seen: Dict[str, int] = {}
    out: list[str] = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            out.append(c)
        else:
            seen[c] += 1
            out.append(f"{c}_{seen[c]}")
    return pd.Index(out)


def json_normalize(data: List[Dict], output_format: str = "pandas") -> pd.DataFrame | pl.DataFrame:
    """
    Normalize nested JSON data to a flat table.

    Parameters:
    - data (List[Dict]): List of dictionaries to normalize.
    - output_format (str): One of ["pandas", "polars"]

    Returns:
    - pd.DataFrame or pl.DataFrame: Normalized data in the specified format.
    """
    if output_format == "pandas":
        return pd.json_normalize(data)
    elif output_format == "polars":
        return pl.DataFrame(data)
    else:
        raise ValueError(f"Invalid output_format: {output_format}. Use 'pandas' or 'polars'.")


def _classify_faceoff_dot_vec(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Vectorized nearest-dot classifier using Euclidean distance.
    
    Parameters
    ----------
    x : np.ndarray
        X coordinates of faceoff locations
    y : np.ndarray
        Y coordinates of faceoff locations
    
    Returns
    -------
    np.ndarray
        Array of dot labels (dtype object) with np.nan where x or y is nan
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    # Initialize output with NaN
    out = np.full(x.shape, np.nan, dtype=object)
    
    # Find valid coordinates
    valid = np.isfinite(x) & np.isfinite(y)
    
    if not np.any(valid):
        return out
    
    # Vectorized distance calculation: (n, 1) - (1, k) -> (n, k)
    xv = x[valid][:, None]  # Shape: (n, 1)
    yv = y[valid][:, None]  # Shape: (n, 1)
    cx = _DOT_XY[:, 0][None, :]  # Shape: (1, k)
    cy = _DOT_XY[:, 1][None, :]  # Shape: (1, k)
    
    # Squared Euclidean distance (no need for sqrt since we only need argmin)
    d2 = (xv - cx) ** 2 + (yv - cy) ** 2  # Shape: (n, k)
    
    # Find nearest dot for each point
    idx = np.argmin(d2, axis=1)
    out[valid] = _DOT_LABELS[idx]
    
    return out


def add_on_event_shift_start_qualifiers(
    on_events: pd.DataFrame,
    pbp: pd.DataFrame,
    *,
    game_col: str = "game_id",
    period_col: str = "period",
    team_col: str = "team_id",
    start_time_col: str = "shift_start_seconds",
    pbp_time_col: str = "timeInPeriodSec",
    pbp_type_col: str = "Event",
    pbp_x_col: str = "xCoord",
    pbp_y_col: str = "yCoord",
    attack_sign_col: str = "attack_sign",
    faceoff_type_value: str = "FAC",
    oz_threshold: float = 25.0,
) -> pd.DataFrame:
    """
    Add zone start qualifiers to ON events using vectorized operations.
    
    Parameters
    ----------
    on_events : pd.DataFrame
        DataFrame of ON events (shift starts) with columns:
        - game_col: Game identifier
        - period_col: Period number
        - start_time_col: Shift start time in seconds
        - attack_sign_col: +1 if team attacks to +x, -1 if attacks to -x
    
    pbp : pd.DataFrame
        Play-by-play DataFrame with columns:
        - game_col: Game identifier
        - period_col: Period number
        - pbp_time_col: Event time in seconds
        - pbp_type_col: Event type (must contain faceoff_type_value)
        - pbp_x_col: X coordinate
        - pbp_y_col: Y coordinate
    
    game_col : str, default "game_id"
        Column name for game identifier
    
    period_col : str, default "period"
        Column name for period number
    
    team_col : str, default "team_id"
        Column name for team identifier (kept for compatibility)
    
    start_time_col : str, default "shift_start_seconds"
        Column name for shift start time in on_events
    
    pbp_time_col : str, default "timeInPeriodSec"
        Column name for event time in pbp
    
    pbp_type_col : str, default "Event"
        Column name for event type in pbp
    
    pbp_x_col : str, default "xCoord"
        Column name for X coordinate in pbp
    
    pbp_y_col : str, default "yCoord"
        Column name for Y coordinate in pbp
    
    attack_sign_col : str, default "attack_sign"
        Column name for attack direction (+1 or -1)
    
    faceoff_type_value : str, default "FAC"
        Value in pbp_type_col that indicates a faceoff
    
    oz_threshold : float, default 25.0
        X coordinate threshold for offensive zone (in attacking direction)
    
    Returns
    -------
    pd.DataFrame
        Original on_events with added columns:
        - shift_start_type: 'ZS' (zone start) or 'OTF' (on the fly)
        - start_dot: Faceoff dot label for ZS shifts (OZ_L, NZ_C, etc.)
        - start_zone: Zone classification for ZS shifts (OZS, NZS, DZS)
    
    Notes
    -----
    - If timestamps don't align exactly, consider rounding both time columns
      to the same precision before calling this function
    - The function uses vectorized NumPy operations for performance
    - Attack direction is used to convert absolute coordinates to attacking-frame
    
    Examples
    --------
    >>> result = add_on_event_shift_start_qualifiers(
    ...     on_events=shifts_df,
    ...     pbp=play_by_play_df,
    ...     pbp_x_col="xCoord",
    ...     pbp_y_col="yCoord"
    ... )
    """
    # Extract faceoffs only with necessary columns
    faceoff_cols = [game_col, period_col, pbp_time_col, pbp_x_col, pbp_y_col]
    f = pbp.loc[
        pbp[pbp_type_col].eq(faceoff_type_value),
        faceoff_cols
    ].copy()
    
    # Check if on_events already has coordinate columns
    # If so, we need to handle suffix collision
    has_coords = pbp_x_col in on_events.columns or pbp_y_col in on_events.columns
    suffix_left = "_orig" if has_coords else ""
    suffix_right = "_faceoff" if has_coords else ""
    
    # Merge ON events with faceoffs at exact shift-start time
    out = on_events.merge(
        f,
        how="left",
        left_on=[game_col, period_col, start_time_col],
        right_on=[game_col, period_col, pbp_time_col],
        suffixes=(suffix_left, suffix_right),
    )
    
    # Get the correct column names after merge
    x_col = f"{pbp_x_col}{suffix_right}" if has_coords else pbp_x_col
    y_col = f"{pbp_y_col}{suffix_right}" if has_coords else pbp_y_col
    
    # Extract coordinates as numpy arrays
    x = out[x_col].to_numpy(dtype=float, copy=False)
    y = out[y_col].to_numpy(dtype=float, copy=False)
    
    # Identify zone starts (shifts that matched a faceoff)
    is_zs = np.isfinite(x) & np.isfinite(y)
    
    # Classify shift start type
    out["shift_start_type"] = np.where(is_zs, "ZS", "OTF")
    
    # Classify faceoff dot (vectorized)
    start_dot = _classify_faceoff_dot_vec(x, y)
    out["start_dot"] = np.where(is_zs, start_dot, np.nan)
    
    # Zone start classification using attack direction
    # Convert to attacking-frame coordinates: positive x = offensive zone
    atk = out[attack_sign_col].to_numpy(copy=False)
    atk = np.asarray(atk, dtype=float)  # Handle int/object columns safely
    x_att = x * atk  # If atk is nan, x_att becomes nan
    
    # Define zones based on attacking-frame x coordinate
    oz = x_att >= oz_threshold
    dz = x_att <= -oz_threshold
    
    # Build zone labels
    start_zone = np.full(x.shape, np.nan, dtype=object)
    start_zone[is_zs & oz] = "OZS"
    start_zone[is_zs & dz] = "DZS"
    start_zone[is_zs & ~(oz | dz) & np.isfinite(x_att)] = "NZS"
    
    out["start_zone"] = start_zone
    
    # Clean up the merge columns
    cols_to_drop = []
    if pbp_time_col in out.columns and pbp_time_col != start_time_col:
        cols_to_drop.append(pbp_time_col)
    if has_coords:
        # Also drop the faceoff coordinate columns since we've extracted the info
        cols_to_drop.extend([x_col, y_col])
    
    if cols_to_drop:
        out.drop(columns=cols_to_drop, inplace=True, errors="ignore")
    
    return out


def add_on_event_shift_start_qualifiers_simplified(
    on_events: pd.DataFrame,
    pbp: pd.DataFrame,
    *,
    game_col: str = "game_id",
    period_col: str = "period",
    start_time_col: str = "shift_start_seconds",
    pbp_time_col: str = "timeInPeriodSec",
    pbp_type_col: str = "Event",
    pbp_x_col: str = "xCoord",
    pbp_y_col: str = "yCoord",
    attack_sign_col: str = "attack_sign",
    faceoff_type_value: str = "FAC",
    oz_threshold: float = 25.0,
) -> pd.DataFrame:
    """
    Simplified version optimized for data with 100% faceoff coordinate coverage.
    
    This version skips some validity checks since we know all faceoffs have coordinates.
    Use this if you've verified your data has complete coordinate coverage.
    
    Parameters and returns are the same as add_on_event_shift_start_qualifiers().
    """
    # Extract faceoffs only
    f = pbp[pbp[pbp_type_col] == faceoff_type_value].copy()
    
    # Keep only necessary columns for merge
    merge_cols = [game_col, period_col, pbp_time_col, pbp_x_col, pbp_y_col]
    f = f[merge_cols]
    
    # Merge ON events with faceoffs
    out = on_events.merge(
        f,
        how='left',
        left_on=[game_col, period_col, start_time_col],
        right_on=[game_col, period_col, pbp_time_col],
        suffixes=('', '_faceoff')
    )
    
    # Check for zone start (shift matched a faceoff)
    is_zs = out[pbp_x_col].notna()
    
    # Shift start type
    out['shift_start_type'] = np.where(is_zs, 'ZS', 'OTF')
    
    # Faceoff dot classification (only for zone starts)
    x = out[pbp_x_col].fillna(0).to_numpy(dtype=float)
    y = out[pbp_y_col].fillna(0).to_numpy(dtype=float)
    
    start_dot = _classify_faceoff_dot_vec(x, y)
    out['start_dot'] = np.where(is_zs, start_dot, np.nan)
    
    # Zone classification using attack direction
    atk = out[attack_sign_col].to_numpy(dtype=float)
    x_att = x * atk
    
    oz = x_att >= oz_threshold
    dz = x_att <= -oz_threshold
    
    # Use np.select for cleaner zone assignment
    conditions = [
        is_zs & oz,
        is_zs & dz,
        is_zs & ~(oz | dz)
    ]
    choices = ['OZS', 'DZS', 'NZS']
    out['start_zone'] = np.select(conditions, choices, default=None)
    
    # Clean up merge column
    if pbp_time_col in out.columns and pbp_time_col != start_time_col:
        out.drop(columns=[pbp_time_col], inplace=True, errors='ignore')
    
    return out


# Convenience function for batch processing
def process_multiple_games(
    on_events: pd.DataFrame,
    pbp: pd.DataFrame,
    game_ids: Optional[list] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Process multiple games efficiently.
    
    Parameters
    ----------
    on_events : pd.DataFrame
        ON events for multiple games
    pbp : pd.DataFrame
        Play-by-play for multiple games
    game_ids : list, optional
        Specific game IDs to process. If None, processes all games.
    **kwargs
        Additional arguments passed to add_on_event_shift_start_qualifiers
    
    Returns
    -------
    pd.DataFrame
        ON events with shift start qualifiers for all games
    """
    game_col = kwargs.get('game_col', 'game_id')
    
    if game_ids is None:
        game_ids = on_events[game_col].unique()
    
    results = []
    
    for gid in game_ids:
        game_on = on_events[on_events[game_col] == gid]
        game_pbp = pbp[pbp[game_col] == gid]
        
        result = add_on_event_shift_start_qualifiers(
            game_on,
            game_pbp,
            **kwargs
        )
        results.append(result)
    
    return pd.concat(results, ignore_index=True)