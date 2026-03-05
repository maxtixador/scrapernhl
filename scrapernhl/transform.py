"""All data transformations in one place."""

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .config import LEAGUES, LeagueType, get_ot_period_length

# ============================================================================
# Play-by-Play Transformations
# ============================================================================

def transform_pbp(
    events: list,
    league: LeagueType,
    nhlify: bool = True,
    game_id: int | str | None = None,
    season_id: int | None = None,
    is_playoff: bool = False,
) -> pd.DataFrame:
    """Transform play-by-play to standard format.

    Parameters
    ----------
    events:
        Raw event list from parse_pbp().
    league:
        League code ('nhl', 'ahl', 'pwhl', 'ohl', 'whl', 'qmjhl').
    nhlify:
        Merge shot+goal duplicate rows emitted by HockeyTech feeds.
    game_id:
        Optional game identifier; added as a column when provided.
    season_id:
        League-specific season ID (e.g. 90 for AHL 2024-25).  Used to look
        up the correct OT period length when the league's OT format has
        changed over time (see LeagueConfig.ot_period_length_history).
    is_playoff:
        Set True for playoff games.  All leagues use 20-minute (1200 s)
        sudden-death OT in the playoffs regardless of the regular-season OT
        length configured in LeagueConfig.ot_period_length.
    """
    if not events:
        return pd.DataFrame()

    df = pd.DataFrame(events)
    config = LEAGUES[league]

    # Apply transformations in sequence
    df = _normalize_periods(df, league)
    df = _normalize_times(df, league, config, season_id=season_id, is_playoff=is_playoff)
    df = _normalize_events(df, league)
    df = _normalize_players(df, league)
    df = _normalize_coordinates(df, config)
    df = _normalize_strength(df, league)
    df = _calculate_scores(df)
    df = _add_metadata(df, league, game_id=game_id)

    # Merge shot+goal duplicate rows for all HockeyTech leagues.
    # AHL/PWHL emit a separate 'goal' event even though the shot event already
    # has isGoal=True; OHL/WHL/QMJHL do the same.  nhlify=False lets callers
    # skip this step and keep both rows.
    if nhlify and league != 'nhl':
        df = nhlify_goals(df)

    return df


def _normalize_periods(df: pd.DataFrame, league: str) -> pd.DataFrame:
    """Normalize period numbers."""
    if 'period' not in df.columns:
        return df

    # ---- hockeytech_b (OHL / WHL / QMJHL) ----
    # Most events only carry `period_id` (always numeric); goal events also
    # carry a text `period` field ("1st","2nd","3rd","OT","1st OT"…).
    # Prioritise period_id (reliable), fall back to mapped text period.
    if league in ['qmjhl', 'ohl', 'whl']:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}
        ot_map = {f"{i}{suffix.get(i, 'th')} OT": i + 3 for i in range(1, 10)}
        text_map = {"1st": 1, "2nd": 2, "3rd": 3, "OT": 4}
        period_map = {**text_map, **ot_map}
        df['period'] = df['period'].replace(period_map)

        # Fill NaN period from period_id (present in most event types)
        if 'period_id' in df.columns:
            df['period'] = df['period'].fillna(
                pd.to_numeric(df['period_id'], errors='coerce')
            )

    # ---- hockeytech_a (AHL / PWHL) ----
    # After parsers.py unpack, period is a plain string like "1"/"OT1".
    # Guard against old dict form just in case.
    if league in ['ahl', 'pwhl']:
        df['period'] = df['period'].apply(
            lambda x: x.get('id', 1) if isinstance(x, dict) else x
        )
        # PWHL / AHL send OT periods as "OT1", "OT2", …
        ot_map = {f"OT{i}": i + 3 for i in range(1, 10)}
        df['period'] = df['period'].replace(ot_map)

    # Convert to numeric
    df['period'] = pd.to_numeric(df['period'], errors='coerce')

    # Fill remaining NaN periods by forward/back-fill within non-shootout rows
    m_so = df['event'].eq('shootout') if 'event' in df.columns else pd.Series(False, index=df.index)
    df.loc[~m_so, 'period'] = df.loc[~m_so, 'period'].ffill().bfill()

    return df


def _normalize_times(
    df: pd.DataFrame,
    league: str,
    config,
    season_id: int | None = None,
    is_playoff: bool = False,
) -> pd.DataFrame:
    """Normalize time fields."""
    # All HockeyTech leagues (AHL/PWHL after parser unpack, OHL/WHL/QMJHL)
    # expose their per-period elapsed time under a top-level 'time' column.
    # NHL uses 'timeInPeriod'.
    time_col_map = {
        'nhl': 'timeInPeriod',
        'ahl': 'time',
        'pwhl': 'time',
        'ohl': 'time',
        'whl': 'time',
        'qmjhl': 'time',
    }

    source_col = time_col_map.get(league, 'time')

    if source_col in df.columns:
        df['elapsedTime'] = df[source_col]

    # NOTE (WHL older seasons): some penalty events in pre-~season-283 WHL games
    # omit the 'time' field entirely at the API level.  There is no way to recover
    # the elapsed time for those rows; they will have NaN time_seconds / game_seconds.
    # This is an upstream data gap, not a parser bug.

    # Convert to seconds; handles both "MM:SS" and "HH:MM:SS" formats
    if 'elapsedTime' in df.columns:
        df['time_seconds'] = df['elapsedTime'].apply(_time_to_seconds)
        # Only calculate game_seconds if period is available.
        # Regulation periods are 1200 s; OT uses the league-configured length
        # (regular-season OT is shorter for most non-NHL leagues).
        # Playoff OT reverts to full 20-min periods — callers must account for
        # that separately when the game type is known.
        if 'period' in df.columns:
            ot_len = get_ot_period_length(config, season_id, is_playoff)
            period = pd.to_numeric(df['period'], errors='coerce')
            reg = period <= 3
            df['game_seconds'] = np.where(
                reg,
                df['time_seconds'] + (period - 1) * 1200,
                df['time_seconds'] + 3 * 1200 + (period - 4) * ot_len,
            )

    return df


def _normalize_events(df: pd.DataFrame, league: str) -> pd.DataFrame:
    """Normalize event types to lowercase strings."""
    event_map = {
        'nhl': 'typeDescKey',
        'ahl': 'event',
        'pwhl': 'event',
        'ohl': 'event',
        'whl': 'event',
        'qmjhl': 'event',
    }

    source_col = event_map.get(league, 'event')
    if source_col in df.columns and source_col != 'event':
        df['event'] = df[source_col]

    # Canonicalize to lowercase stripped strings; preserves None/NaN.
    if 'event' in df.columns:
        df['event'] = df['event'].apply(
            lambda x: x.strip().lower() if isinstance(x, str) else x
        )

    return df


def _normalize_players(df: pd.DataFrame, league: str) -> pd.DataFrame:
    """Normalize player fields."""
    config = LEAGUES[league]

    if config.pbp_style == 'hockeytech_a':
        # AHL/PWHL: flatten nested player objects
        df = _flatten_player_objects(df)

    # Expand on-ice arrays (plus/minus)
    if 'plus' in df.columns:
        df = _expand_on_ice(df, 'plus')
    if 'minus' in df.columns:
        df = _expand_on_ice(df, 'minus')

    return df


def _normalize_coordinates(df: pd.DataFrame, config) -> pd.DataFrame:
    """Normalize coordinates to feet, centered at ice center (0, 0).

    Both canvas types are mapped to the same coordinate system:
      x: -100 (left boards) to +100 (right boards) feet from center ice
      y: -42.5 (one board) to +42.5 (other board) feet from center ice

    Shot distance and angle are then computed from the goal at (±89, 0) —
    i.e., the standard NHL goal-line position 11 ft from the end boards.
    abs(x) is used so both offensive zones map to the same end, which lets
    distance/angle be compared across teams without knowing shooting direction.
    """
    if 'x_location' not in df.columns or 'y_location' not in df.columns:
        return df

    canvas_x, canvas_y = config.canvas_size
    x_loc = pd.to_numeric(df['x_location'], errors='coerce')
    y_loc = pd.to_numeric(df['y_location'], errors='coerce')

    if canvas_x == 850:  # AHL/PWHL: origin is top-left corner of canvas
        # Scale to feet, then shift so center ice = (0, 0)
        df['x'] = (x_loc / canvas_x * 200 - 100).round(2)
        df['y'] = (y_loc / canvas_y * 85 - 42.5).round(2)
    else:  # OHL/WHL/QMJHL: canvas center is already ice center for x
        # x scale: 600 px = 200 ft  →  1 px = 1/3 ft (correct)
        df['x'] = ((x_loc - canvas_x / 2) / 3).round(2)
        # y scale: 300 px = 85 ft  →  1 px = 85/300 ft (was /3 = 100 ft, wrong)
        df['y'] = ((y_loc - canvas_y / 2) * (85 / canvas_y)).round(2)

    # Shot metrics: distance and angle from the goal at (±89, 0).
    # GOAL_X = 89 ft from center ice (goal line is 11 ft from end boards).
    # Using abs(x) maps both ends to the positive-x goal so that
    # distance/angle are zone-agnostic and comparable across the full game.
    GOAL_X = 89.0
    x_from_goal = df['x'].abs() - GOAL_X  # negative = shot in front of net
    y_from_goal = df['y']
    df['shot_distance_ft'] = np.sqrt(
        x_from_goal ** 2 + y_from_goal ** 2
    ).round(2)
    # Angle: 0° = straight on, 90° = directly to the side at the post line
    df['shot_angle_deg'] = np.degrees(
        np.arctan2(y_from_goal.abs(), x_from_goal.abs())
    ).round(2)

    return df


def _normalize_strength(df: pd.DataFrame, league: str) -> pd.DataFrame:
    """Normalize strength descriptions."""

    if league == 'nhl':
        pass
    else:
        # goal_type handling
        if "goal_type_name" in df.columns:
            df["goal_type_name"] = df["goal_type_name"].replace({"": "EV", "EN": "EN.EV"})
        if "goal_type" in df.columns:
            df["goal_type"] = df["goal_type"].replace({"": "EV", "EN": "EN.EV"})
    return df


def _calculate_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate cumulative scores."""
    if 'event' not in df.columns:
        return df

    m_goal = df['event'].eq('goal')
    # 'home' is a string ('1'/'0') in HockeyTech feeds; cast to numeric so
    # .eq(1) / .eq(0) work correctly regardless of the source type.
    home = pd.to_numeric(df.get('home', pd.Series(dtype=float)), errors='coerce').fillna(-1)
    df['_home_goal'] = (m_goal & home.eq(1)).astype(int)
    df['_away_goal'] = (m_goal & home.eq(0)).astype(int)

    df['score_home'] = df['_home_goal'].cumsum()
    df['score_away'] = df['_away_goal'].cumsum()

    df = df.drop(columns=['_home_goal', '_away_goal'])

    return df


def _add_metadata(
    df: pd.DataFrame,
    league: str,
    game_id: int | str | None = None,
) -> pd.DataFrame:
    """Add metadata columns."""
    df['league'] = league.upper()
    if game_id is not None:
        df['game_id'] = game_id
    df['scraped_at'] = datetime.now(timezone.utc).isoformat()
    return df


def nhlify_goals(df: pd.DataFrame) -> pd.DataFrame:  # ✅ Correct function name
    """Merge shot+goal rows into single goal rows."""
    if df.empty or "event" not in df.columns:
        return df

    # Check if we have time_seconds column
    if "time_seconds" not in df.columns:
        return df

    # Sort by time — use the best available ordering columns.
    # Preserve the original API row order as a tiebreaker so that events with
    # identical timestamps (common in old-format games) are not scrambled.
    sort_cols = [c for c in ["period", "game_seconds", "time_seconds"] if c in df.columns]
    if not sort_cols:
        return df
    df = df.reset_index(drop=True)
    df["_orig_idx"] = df.index
    df = df.sort_values(sort_cols + ["_orig_idx"], kind="stable").reset_index(drop=True)
    df = df.drop(columns=["_orig_idx"])

    # Add next event indicators
    df["_next_event"] = df["event"].shift(-1)
    df["_next_time"] = df["time_seconds"].shift(-1)

    # Find shots followed by goals at same time
    mask = (
        df["event"].isin(["shot", "penaltyshot"]) &
        (df["_next_event"] == "goal") &
        (df["time_seconds"] == df["_next_time"])
    )

    if mask.any():
        shot_indices = df[mask].index
        goal_indices = shot_indices + 1

        # Copy shot data to goal rows.
        # Include both snake_case (OHL/WHL/QMJHL) and camelCase (AHL/PWHL) variants
        # so the merge works regardless of which naming convention the league uses.
        shot_cols = [
            "x_location", "y_location", "x_feet", "y_feet",
            "shot_type", "shotType",
            "shot_quality_description", "shotQuality",
            "shot_distance_ft", "shot_angle_deg",
        ]

        for shot_idx, goal_idx in zip(shot_indices, goal_indices):
            if goal_idx >= len(df):
                continue
            # Guard: after sorting, the next row should be the goal, but
            # confirm before clobbering data (e.g. two events at identical
            # time_seconds could shift the assumed adjacency).
            if df.at[goal_idx, 'event'] != 'goal':
                continue
            for col in shot_cols:
                if col in df.columns:
                    if pd.isna(df.at[goal_idx, col]) and pd.notna(df.at[shot_idx, col]):
                        df.at[goal_idx, col] = df.at[shot_idx, col]

        # Remove redundant shot rows
        df = df.drop(index=shot_indices).reset_index(drop=True)

    # Cleanup
    df = df.drop(columns=["_next_event", "_next_time"], errors="ignore")

    # Validate: if any shot+goal pairs still coexist at the same (period,
    # time_seconds), the merge failed — the data format is incompatible.
    shot_mask = df["event"].isin(["shot", "penaltyshot"])
    goal_mask = df["event"] == "goal"
    if shot_mask.any() and goal_mask.any() and "time_seconds" in df.columns:
        key_cols = [c for c in ["period", "time_seconds"] if c in df.columns]
        shot_keys = set(df.loc[shot_mask, key_cols].dropna().itertuples(index=False, name=None))
        goal_keys = set(df.loc[goal_mask, key_cols].dropna().itertuples(index=False, name=None))
        unmerged = shot_keys & goal_keys
        if unmerged:
            raise ValueError(
                f"nhlify_goals failed: {len(unmerged)} goal(s) could not be merged with "
                f"their preceding shot (shot+goal pairs still present at the same time). "
                f"The data format for this game may be incompatible with automatic merging. "
                f"Re-scrape with nhlify=False to get the raw event rows."
            )

    return df


# ============================================================================
# Goal Replay Tracking Transformations
# ============================================================================

def tracking_dict_to_df(
    frames: list,
    svg_width: int = 2400,
    svg_height: int = 1020,
    rink_length: int = 200,
    rink_width: int = 85,
    extra: bool = True,
) -> pd.DataFrame:
    """Convert NHL goal-replay sprite frames into a tidy DataFrame.

    Each row represents one entity (player or puck) at one timestamp.

    Parameters
    ----------
    frames:
        Raw frame list returned by ``HockeyScraper.goal_replay()``.  Each
        frame is a dict with keys ``timeStamp`` (int) and ``onIce`` (dict
        mapping sprite IDs to entity dicts with ``x``, ``y``, ``playerId``,
        ``teamId``, etc.).
    svg_width:
        Width of the SVG canvas in pixels (default 2400).
    svg_height:
        Height of the SVG canvas in pixels (default 1020).
    rink_length:
        Rink length in feet (default 200).
    rink_width:
        Rink width in feet (default 85).
    extra:
        When ``True`` (default), add frame-to-frame movement columns
        ``frame``, ``dx``, ``dy``, ``dt``, and ``speed`` (feet per frame).

    Returns
    -------
    pd.DataFrame
        Columns: ``entity_id``, ``id``, ``playerId``, ``teamId``, ``x``,
        ``y``, ``rink_x``, ``rink_y``, ``timeStamp``, ``is_puck``.
        When ``extra=True``: also ``frame``, ``dx``, ``dy``, ``dt``,
        ``speed``.

    Notes
    -----
    Approach inspired by code shared by @the_bucketless.
    """
    df = pd.concat(
        [
            pd.DataFrame(frame["onIce"]).T.assign(timeStamp=frame["timeStamp"])
            for frame in frames
        ]
    )

    df = df.reset_index().rename(columns={"index": "entity_id"})

    df["playerId"] = pd.to_numeric(df["playerId"], errors="coerce")
    df["teamId"] = pd.to_numeric(df["teamId"], errors="coerce")

    # Convert SVG canvas coordinates → rink coordinates (feet, origin = center)
    df["rink_x"] = df["x"] * rink_length / svg_width - rink_length / 2
    df["rink_y"] = rink_width / 2 - df["y"] * rink_width / svg_height

    df["is_puck"] = df["playerId"].isna()

    df = df.sort_values(["entity_id", "timeStamp"]).reset_index(drop=True)

    if extra:
        df["frame"] = df["timeStamp"] - df["timeStamp"].min()
        df["dx"] = df.groupby("entity_id")["rink_x"].diff()
        df["dy"] = df.groupby("entity_id")["rink_y"].diff()
        df["dt"] = df.groupby("entity_id")["frame"].diff()
        df["speed"] = ((df["dx"] ** 2 + df["dy"] ** 2) ** 0.5) / df["dt"]

    return df


# ============================================================================
# Player Stats Transformations
# ============================================================================

def transform_stats(players: list, league: LeagueType, position: str) -> pd.DataFrame:
    """Transform player stats to standard format."""
    if not players:
        return pd.DataFrame()

    df = pd.DataFrame(players)

    # Standardize column names
    df = _standardize_stat_columns(df, league, position)

    # Add metadata
    df['league'] = league.upper()
    df['position_group'] = position

    return df


def _standardize_stat_columns(df: pd.DataFrame, league: str, position: str) -> pd.DataFrame:
    """Standardize stat column names."""
    # Common renames
    rename_map = {
        'player_id': 'playerId',
        'first_name': 'firstName',
        'last_name': 'lastName',
        'jersey_number': 'jerseyNumber',
        'gp': 'gamesPlayed',
        'plus_minus': 'plusMinus',
        'pim': 'penaltyMinutes',
        'ppg': 'powerPlayGoals',
        'shg': 'shorthandedGoals',
        'gwg': 'gameWinningGoals',
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    return df


# ============================================================================
# Helper Functions
# ============================================================================


def _time_to_seconds(time_str: str | None) -> int | None:
    """Convert MM:SS or HH:MM:SS to seconds.

    HockeyTech feeds mix both formats in the same game; e.g. faceoff events
    use '19:08' while some goal events use '00:19:08'.
    """
    if not time_str or not isinstance(time_str, str):
        return None
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return None
    except Exception:
        return None


def _flatten_player_objects(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten nested player objects (AHL/PWHL).

    scoredBy is an alternate field name for the goal scorer used by some
    seasons/leagues; both map to scorer* output columns so downstream code
    only needs to reference one name.  scorer* values from the explicit
    'scorer' field take precedence; scoredBy fills any remaining NaNs.
    """
    # source field → output prefix ('scoredBy' aliases to 'scorer')
    field_map = {
        'shooter': 'shooter',
        'goalie': 'goalie',
        'scorer': 'scorer',
        'scoredBy': 'scorer',
    }

    attrs = [('id', 'Id'), ('firstName', 'FirstName'),
             ('lastName', 'LastName'), ('jerseyNumber', 'JerseyNumber')]

    for field, prefix in field_map.items():
        if field not in df.columns:
            continue
        for attr, suffix in attrs:
            col = f'{prefix}{suffix}'
            vals = df[field].apply(
                lambda x, a=attr: x.get(a) if isinstance(x, dict) else None
            )
            if col not in df.columns:
                df[col] = vals
            else:
                df[col] = df[col].fillna(vals)

    return df


def _expand_on_ice(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Expand on-ice player arrays to columns."""
    if col not in df.columns:
        return df

    # Get max players
    max_players = df[col].apply(lambda x: len(x) if isinstance(x, list) else 0).max()

    for i in range(int(max_players)):
        df[f'{col}Player{i+1}Id'] = df[col].apply(
            lambda x, _i=i: (
                # AHL/PWHL use 'id'; OHL/WHL/QMJHL use 'player_id'
                (x[_i].get('player_id') or x[_i].get('id'))
                if isinstance(x, list) and _i < len(x)
                and isinstance(x[_i], dict)
                else None
            )
        )

    return df
