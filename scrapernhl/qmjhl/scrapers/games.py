"""
QMJHL Game Scraper Module

This module provides functions to scrape game data from the QMJHL (LHJMQ) website.
Supports both synchronous and asynchronous operations.

Features:
- API-based event data retrieval
- Play-by-play scraping using Playwright (dynamic HTML)
- Player ID extraction from links
- Goal scoring details with on-ice players
- Both sync and async interfaces

Usage:
    # Sync API calls
    events = getAPIEvents(41450)
    
    # Async Playwright scraping
    events = await scrape_game_async(41450)
    
    # Sync wrapper for Playwright scraping
    events = scrape_game(41450)
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
import pandas as pd
import numpy as np

import requests

# try:
#     from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
#     PLAYWRIGHT_AVAILABLE = True
# except ImportError:
#     PLAYWRIGHT_AVAILABLE = False
#     Page = Any  # Type hint fallback


# -----------------------------
# API Functions
# -----------------------------

def getAPIEvents(game_id: int, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch raw event data for a given game ID from the QMJHL API.
    
    Args:
        game_id: The unique identifier for the game
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        Dictionary containing play-by-play event data
        
    Raises:
        requests.RequestException: If the API request fails
        KeyError: If the response format is unexpected
        
    Example:
        >>> events = getAPIEvents(41450)
        >>> print(events.keys())
    """
    url = (
        f"https://cluster.leaguestat.com/feed/index.php"
        f"?feed=gc&key=f322673b6bcae299&client_code=lhjmq"
        f"&game_id={game_id}&lang_code=en&fmt=json&tab=pxpverbose"
    )

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["GC"]["Pxpverbose"]
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch game {game_id}: {e}")
    except KeyError as e:
        raise KeyError(f"Unexpected API response format for game {game_id}: {e}")




def scrape_game(game_id: int, timeout: int = 30, nhlify: bool = True) -> pd.DataFrame:
    """
    Fetch and clean play-by-play data for a QMJHL game.
    
    Args:
        game_id: The unique identifier for the game
        timeout: Maximum time to wait for page load in seconds (default: 30)
        nhlify: If True, merge shot+goal rows into single rows (NHL-style).
                If False, keep separate rows for shots and goals (QMJHL-style).
    
    Returns:
        Cleaned DataFrame with play-by-play event data ready for analysis
        
    Raises:
        RuntimeError: If Playwright is not installed
        Exception: Propagates exceptions from the async function
        
    Example:
        >>> df = scrape_game(31171)
        >>> print(df['event'].value_counts())
        >>> 
        >>> # Keep QMJHL-style separate shot/goal rows
        >>> df_qmjhl = scrape_game(31171, nhlify=False)
    """
    
    data = getAPIEvents(game_id)
    
    df = pd.DataFrame(data)
    df["game_id"] = int(game_id)
    df = df.pipe(clean_pbp, nhlify=nhlify)
    
    return df
    
 
 
 

def _expand_on_ice_wide(df: pd.DataFrame, col: str, prefix: str, drop_source: bool = False) -> pd.DataFrame:
    """
    Expand a column that contains list[dict] into wide columns:
    prefixPlayer1Id, prefixPlayer1JerseyNumber, ... prefixPlayerNLastName

    drop_source: if True, removes the original `col` from the output.
    """
    if col not in df.columns:
        return df

    out = df.copy()
    out["_row_id"] = out.index

    # explode list -> long
    long = out[["_row_id", col]].explode(col, ignore_index=False)
    long = long[long[col].notna()]
    if long.empty:
        out = out.drop(columns=["_row_id"])
        return out.drop(columns=[col]) if drop_source else out

    # dict -> columns
    norm = pd.json_normalize(long[col])
    norm["_row_id"] = long["_row_id"].values
    norm["_p"] = norm.groupby("_row_id").cumcount().add(1)

    keymap = {
        "player_id": "Id",
        "jersey_number": "JerseyNumber",
        "team_id": "TeamId",
        "team_code": "Team",
        "first_name": "FirstName",
        "last_name": "LastName",
    }
    keep = [k for k in keymap if k in norm.columns]
    if not keep:
        out = out.drop(columns=["_row_id"])
        return out.drop(columns=[col]) if drop_source else out

    # pivot safely
    wide = (
        norm.pivot_table(index="_row_id", columns="_p", values=keep, aggfunc="first")
    )
    wide.columns = [f"{prefix}Player{p}{keymap[field]}" for field, p in wide.columns]
    wide = wide.reset_index()

    # merge back
    out = out.merge(wide, on="_row_id", how="left").drop(columns=["_row_id"])
    if drop_source:
        out = out.drop(columns=[col])
    return out


def clean_pbp(pbp: pd.DataFrame, nhlify: bool = True) -> pd.DataFrame:
    """
    Clean and standardize QMJHL play-by-play data.
    
    Args:
        pbp: Raw play-by-play DataFrame from getAPIEvents
        nhlify: If True, merge shot+goal rows into single goal rows (NHL-style).
                If False, keep separate rows for shots and goals (QMJHL-style).
    
    Returns:
        Cleaned DataFrame ready for analysis with standardized columns
    """
    df = pbp.copy()
    
    df["orderIdx"] = np.arange(len(df))
    
    # ensure target cols exist
    new_cols = [
        "event_detail",
        "player1Id", "player1JerseyNumber", "player1FirstName", "player1LastName", "player1Team", "player1TeamId",
        "player2Id", "player2JerseyNumber", "player2FirstName", "player2LastName", "player2Team", "player2TeamId",
        "player3Id", "player3JerseyNumber", "player3FirstName", "player3LastName", "player3Team", "player3TeamId",
        "eventTeam", "eventTeamId",
        "goalieId", "goalieJerseyNumber", "goalieFirstName", "goalieLastName", "goalieTeam", "goalieTeamId",
    ]
    for c in new_cols:
        if c not in df.columns:
            df[c] = pd.NA

    def assign(mask, mapping):
        if not mask.any():
            return
        for dst, src in mapping.items():
            if src in df.columns:
                df.loc[mask, dst] = df.loc[mask, src]

    # goalie_change
    m_gc = df["event"].eq("goalie_change")
    m_in  = m_gc & df.get("goalie_in_id", pd.Series(pd.NA, index=df.index)).notna()
    m_out = m_gc & df.get("goalie_out_id", pd.Series(pd.NA, index=df.index)).notna()

    df.loc[m_in, "event_detail"] = "in"
    df.loc[m_out, "event_detail"] = "out"

    assign(m_in, {
        "eventTeam": "team_code",
        "eventTeamId": "team_id",
        "player1Id": "goalie_in_info.player_id",
        "player1JerseyNumber": "goalie_in_info.jersey_number",
        "player1FirstName": "goalie_in_info.first_name",
        "player1LastName": "goalie_in_info.last_name",
        "player1Team": "goalie_in_info.team_code",
        "player1TeamId": "goalie_in_info.team_id",
    })
    assign(m_out, {
        "eventTeam": "team_code",
        "eventTeamId": "team_id",
        "player1Id": "goalie_out_info.player_id",
        "player1JerseyNumber": "goalie_out_info.jersey_number",
        "player1FirstName": "goalie_out_info.first_name",
        "player1LastName": "goalie_out_info.last_name",
        "player1Team": "goalie_out_info.team_code",
        "player1TeamId": "goalie_out_info.team_id",
    })

    # faceoff
    m_fo = df["event"].eq("faceoff")
    home_win = pd.to_numeric(df.get("home_win", pd.Series(pd.NA, index=df.index)), errors="coerce")
    m_hw = m_fo & home_win.eq(1)
    m_hl = m_fo & home_win.eq(0)

    assign(m_hw, {
        "eventTeam": "player_home.team_code",
        "eventTeamId": "player_home.team_id",
        "player1Id": "player_home.player_id",
        "player1JerseyNumber": "player_home.jersey_number",
        "player1FirstName": "player_home.first_name",
        "player1LastName": "player_home.last_name",
        "player1Team": "player_home.team_code",
        "player1TeamId": "player_home.team_id",
        "player2Id": "player_visitor.player_id",
        "player2JerseyNumber": "player_visitor.jersey_number",
        "player2FirstName": "player_visitor.first_name",
        "player2LastName": "player_visitor.last_name",
        "player2Team": "player_visitor.team_code",
        "player2TeamId": "player_visitor.team_id",
    })
    assign(m_hl, {
        "eventTeam": "player_visitor.team_code",
        "eventTeamId": "player_visitor.team_id",
        "player1Id": "player_visitor.player_id",
        "player1JerseyNumber": "player_visitor.jersey_number",
        "player1FirstName": "player_visitor.first_name",
        "player1LastName": "player_visitor.last_name",
        "player1Team": "player_visitor.team_code",
        "player1TeamId": "player_visitor.team_id",
        "player2Id": "player_home.player_id",
        "player2JerseyNumber": "player_home.jersey_number",
        "player2FirstName": "player_home.first_name",
        "player2LastName": "player_home.last_name",
        "player2Team": "player_home.team_code",
        "player2TeamId": "player_home.team_id",
    })

    # hit
    m_hit = df["event"].eq("hit")
    assign(m_hit, {
        "eventTeam": "hitter.team_code",
        "eventTeamId": "hitter.team_id",
        "player1Id": "hitter.player_id",
        "player1JerseyNumber": "hitter.jersey_number",
        "player1FirstName": "hitter.first_name",
        "player1LastName": "hitter.last_name",
        "player1Team": "hitter.team_code",
        "player1TeamId": "hitter.team_id",
    })

    # shot + penaltyshot
    m_shot = df["event"].isin(["shot", "penaltyshot"])
    assign(m_shot, {
        "eventTeam": "player.team_code",
        "eventTeamId": "player.team_id",
        "player1Id": "player.player_id",
        "player1JerseyNumber": "player.jersey_number",
        "player1FirstName": "player.first_name",
        "player1LastName": "player.last_name",
        "player1Team": "player.team_code",
        "player1TeamId": "player.team_id",
        "goalieId": "goalie.player_id",
        "goalieJerseyNumber": "goalie.jersey_number",
        "goalieFirstName": "goalie.first_name",
        "goalieLastName": "goalie.last_name",
        "goalieTeam": "goalie.team_code",
        "goalieTeamId": "goalie.team_id",
    })

    # penalty
    m_pen = df["event"].eq("penalty")
    assign(m_pen, {
        "eventTeam": "player_penalized_info.team_code",
        "eventTeamId": "player_penalized_info.team_id",
        "player1Id": "player_penalized_info.player_id",
        "player1JerseyNumber": "player_penalized_info.jersey_number",
        "player1FirstName": "player_penalized_info.first_name",
        "player1LastName": "player_penalized_info.last_name",
        "player1Team": "player_penalized_info.team_code",
        "player1TeamId": "player_penalized_info.team_id",
        "player2Id": "player_served_info.player_id",
        "player2JerseyNumber": "player_served_info.jersey_number",
        "player2FirstName": "player_served_info.first_name",
        "player2LastName": "player_served_info.last_name",
        "player2Team": "player_served_info.team_code",
        "player2TeamId": "player_served_info.team_id",
    })
    
    df.loc[m_pen, "period"] = pd.to_numeric(df.loc[m_pen, "period"].str.extract(r"(\d+)")[0], errors="coerce")

    # goal
    m_goal = df["event"].eq("goal")
    assign(m_goal, {
        "eventTeam": "goal_scorer.team_code",
        "eventTeamId": "goal_scorer.team_id",
        "player1Id": "goal_scorer.player_id",
        "player1JerseyNumber": "goal_scorer.jersey_number",
        "player1FirstName": "goal_scorer.first_name",
        "player1LastName": "goal_scorer.last_name",
        "player1Team": "goal_scorer.team_code",
        "player1TeamId": "goal_scorer.team_id",
        "player2Id": "assist1_player.player_id",
        "player2JerseyNumber": "assist1_player.jersey_number",
        "player2FirstName": "assist1_player.first_name",
        "player2Team": "assist1_player.team_code",
        "player2TeamId": "assist1_player.team_id",
        "player2LastName": "assist1_player.last_name",
        "player3Id": "assist2_player.player_id",
        "player3JerseyNumber": "assist2_player.jersey_number",
        "player3FirstName": "assist2_player.first_name",
        "player3LastName": "assist2_player.last_name",
        "player3Team": "assist2_player.team_code",
        "player3TeamId": "assist2_player.team_id",
    })
    
    if "plus" not in df.columns:
        df["plus"] = pd.NA
        df["minus"] = pd.NA
        df["n_plus"] = pd.NA
        df["n_minus"] = pd.NA
        df["homeSkaters"] = pd.NA
        df["awaySkaters"] = pd.NA
        
    else:
        df["n_plus"] = df["plus"].apply(lambda x: len(x) if isinstance(x, list) else np.nan)
        df["n_minus"] = df["minus"].apply(lambda x: len(x) if isinstance(x, list) else np.nan)
        
        df["homeSkaters"] = np.where(
            df["home"].eq(1) & df["n_plus"].notna() & df["n_minus"].notna(),
            df["n_plus"],
            df["n_minus"]
        )
        df["awaySkaters"] = np.where(
            df["home"].eq(0) & df["n_plus"].notna() & df["n_minus"].notna(),
            df["n_plus"],
            df["n_minus"]
        )

        # expand plus/minus
        df = _expand_on_ice_wide(df, col="plus", prefix="plus", drop_source=False)
        df = _expand_on_ice_wide(df, col="minus", prefix="minus", drop_source=False)

    # shootout
    m_so = df["event"].eq("shootout")
    assign(m_so, {
        "eventTeam": "shooter.team_code",
        "eventTeamId": "shooter.team_id",
        "player1Id": "shooter.player_id",
        "player1JerseyNumber": "shooter.jersey_number",
        "player1FirstName": "shooter.first_name",
        "player1LastName": "shooter.last_name",
        "goalieId": "goalie.player_id",
        "goalieJerseyNumber": "goalie.jersey_number",
        "goalieFirstName": "goalie.first_name",
        "goalieLastName": "goalie.last_name",
        "goalieTeam": "goalie.team_code",
        "goalieTeamId": "goalie.team_id",
    })

    # drop source columns if present
    columns_to_delete = (
        df.filter(like='first_name').columns.tolist()
        + df.filter(like='last_name').columns.tolist()
        + df.filter(like='team_code').columns.tolist()
        + df.filter(like='team_id').columns.tolist()
        + df.filter(like='player_id').columns.tolist()
        + df.filter(like='jersey_number').columns.tolist()
        + ["home_win", "player_home", "player_visitor",
           "goalie_in_id", "goalie_out_id",
           "goalie_in_info", "goalie_out_info",
           "hitter", "player", "goalie",
           "player_penalized_info", "player_served_info",
           "goal_scorer", "assist1_player", "assist2_player",
           "shooter"]
    )

    # optional: remove duplicates while preserving order
    columns_to_delete = list(dict.fromkeys(columns_to_delete))
    
    df = df.drop(columns=[c for c in columns_to_delete if c in df.columns])
    
    has_playoff_OT = df["period"].unique().tolist()
    has_playoff_OT = any(isinstance(p, str) and "OT" in p for p in has_playoff_OT)
    # convert period like "1st OT" to 4
    df["period"] = df["period"].replace({"1st OT": 4, "2nd OT": 5, "3rd OT": 6, "4th OT": 7, "5th OT": 8,
                                         "6th OT": 9, "7th OT": 10, "8th OT": 11, "9th OT": 12})
    
    # period - handle period_id column check
    if "period_id" in df.columns:
        df["period"] = np.where(
            df["period"].isnull(),
            df["period_id"],
            df["period"])
        df = df.drop(["period_id"], axis=1)
    
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    
    # ffill non shootout periods
    m_so_event = df["event"].eq("shootout")
    
    if has_playoff_OT:
        # for playoff OT, fill forward and backward to handle gaps
        df.loc[~m_so_event, "period"] = df.loc[~m_so_event].groupby("game_id")["period"].ffill().bfill()
    else:
        # for regular season, fill forward and backward, then fillna with 5 for shootout
        df.loc[~m_so_event, "period"] = df.loc[~m_so_event].groupby("game_id")["period"].ffill().bfill().fillna(5)
    
    # Check if 's' column exists before using it
    if "s" in df.columns:
        df.loc[df["period"].notnull(), "elapsedTime"] = df["s"] + (df["period"] - 1).clip(upper=4) * 20 * 60
    
    # ensure correct ordering within each game
    df = df.sort_values(["game_id", "elapsedTime", "orderIdx"], kind="mergesort")

    # goal masks
    m_goal = df["event"].eq("goal")

    # increment columns
    df["home"] = pd.to_numeric(df["home"], errors="coerce")
    df["_home_goal"] = (m_goal & df["home"].eq(1)).astype(int)
    df["_away_goal"] = (m_goal & df["home"].eq(0)).astype(int)

    # cumulative scores per game
    df["score_home"] = df.groupby("game_id")["_home_goal"].cumsum()
    df["score_away"] = df.groupby("game_id")["_away_goal"].cumsum()

    # cleanup
    df = df.drop(columns=["_home_goal", "_away_goal"])
    
    # x, y coordinates
    if "x_location" in df.columns and "y_location" in df.columns:
        df["x_norm"] = df["x_location"]
        df["y_norm"] = df["y_location"]

        # home team shoots left → flip x
        m_home = df["home"].eq(1)
        df.loc[m_home, "x_norm"] = 600 - df.loc[m_home, "x_location"]
        
        # y stays the same
        df["x"] = (df["x_norm"] - 300) / 3.0
        df["y"] = (df["y_norm"] - 150) / 3.0
        
        dx = 600 - df["x_norm"]
        dy = 150 - df["y_norm"]

        df["shot_distance_ft"] = (dx**2 + dy**2) ** 0.5 / 3.0
        df["shot_angle_deg"] = abs(np.degrees(np.arctan2(dy, dx)))
    
    # goal_type handling
    if "goal_type_name" in df.columns:
        df["goal_type_name"] = df["goal_type_name"].replace({"": "EV", "EN": "EN.EV"})
    if "goal_type" in df.columns:
        df["goal_type"] = df["goal_type"].replace({"": "EV", "EN": "EN.EV"})
    
    # ensure correct order
    df = df.sort_values(["game_id", "elapsedTime", "orderIdx"], kind="mergesort")

    # ========================================================================================
    # NHLIFY: Merge shot+goal rows (QMJHL has separate rows, NHL has one row per shot event)
    # ========================================================================================
    if nhlify:
        # Create shifted columns to check next event
        df["_next_event"] = df.groupby("game_id")["event"].shift(-1)
        df["_next_time"] = df.groupby("game_id")["elapsedTime"].shift(-1)
        
        # For shots that are followed by goals at the same time, copy shot data to the goal row
        m_shot_before_goal = (
            df["event"].isin(["shot", "penaltyshot"]) &
            (df["_next_event"] == "goal") &
            (df["elapsedTime"] == df["_next_time"])
        )
        
        # Copy ALL data from shot row to goal row where goal has NA but shot doesn't
        if m_shot_before_goal.any():
            shot_indices = df[m_shot_before_goal].index
            goal_indices = shot_indices + 1
            
            # Ensure goal_indices are valid
            valid_mask = goal_indices < len(df)
            shot_indices = shot_indices[valid_mask]
            goal_indices = goal_indices[valid_mask]
            
            # Get columns to potentially copy (exclude meta columns)
            cols_to_skip = ["game_id", "event", "orderIdx", "_next_event", "_next_time"]
            cols_to_check = [c for c in df.columns if c not in cols_to_skip]
            
            # For each pair, copy shot data where goal has NA
            for shot_idx, goal_idx in zip(shot_indices, goal_indices):
                for col in cols_to_check:
                    goal_val = df.at[goal_idx, col]
                    shot_val = df.at[shot_idx, col]
                    
                    # Handle different types of values
                    try:
                        # Check if goal value is NA/None/empty
                        goal_is_na = (
                            goal_val is None or
                            goal_val is pd.NA or
                            (isinstance(goal_val, float) and pd.isna(goal_val)) or
                            (isinstance(goal_val, str) and goal_val == '')
                        )
                        
                        # Check if shot value is not NA/None/empty
                        shot_has_value = (
                            shot_val is not None and
                            shot_val is not pd.NA and
                            not (isinstance(shot_val, float) and pd.isna(shot_val)) and
                            not (isinstance(shot_val, str) and shot_val == '')
                        )
                        
                        # Copy if goal is NA and shot has value
                        if goal_is_na and shot_has_value:
                            df.at[goal_idx, col] = shot_val
                    except (ValueError, TypeError):
                        # Skip columns that can't be compared (like lists/arrays)
                        continue
        
        # Now remove the redundant shot rows
        df = df[~m_shot_before_goal].copy()
        
        # Clean up temporary columns
        df = df.drop(columns=["_next_event", "_next_time"], errors="ignore")
        
        # Reset order index after removal
        df = df.reset_index(drop=True)
        df["orderIdx"] = np.arange(len(df))

    # format cols
    id_cols = [c for c in df.columns if str(c).endswith("Id")]

    if id_cols:
        df[id_cols] = df[id_cols].apply(lambda s: pd.to_numeric(s, errors="coerce"))    
   
    df["scrapeOn"] = pd.Timestamp.now(tz="UTC")
    
    # Drop orderIdx (was only used for sorting)
    df = df.drop(columns=["orderIdx"], errors="ignore")
    
    return df
   

# Maintain backward compatibility
__all__ = [
    'getAPIEvents',
    'scrape_game',
    'scrape_game_async',
]



