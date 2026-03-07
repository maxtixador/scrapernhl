"""Unit tests for scrapernhl.transform — pure functions, no I/O."""
import pandas as pd
import pytest

from scrapernhl.transform import (
    _add_metadata,
    _calculate_scores,
    _normalize_events,
    _normalize_periods,
    _normalize_strength,
    nhlify_goals,
    transform_pbp,
)


# ---------------------------------------------------------------------------
# transform_pbp — top-level entrypoint
# ---------------------------------------------------------------------------

class TestTransformPBPEmpty:
    def test_empty_events_returns_empty_dataframe(self):
        result = transform_pbp([], "nhl")
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_empty_events_ahl(self):
        result = transform_pbp([], "ahl")
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_empty_events_ohl(self):
        result = transform_pbp([], "ohl")
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestTransformPBPNHL:
    def test_returns_dataframe(self):
        events = [{"typeDescKey": "shot-on-goal", "timeInPeriod": "05:20"}]
        result = transform_pbp(events, "nhl")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_adds_league_column_uppercase(self):
        events = [{"typeDescKey": "faceoff", "timeInPeriod": "00:00"}]
        result = transform_pbp(events, "nhl")
        assert "league" in result.columns
        assert result["league"].iloc[0] == "NHL"

    def test_adds_game_id_when_provided(self):
        events = [{"typeDescKey": "shot-on-goal", "timeInPeriod": "05:00"}]
        result = transform_pbp(events, "nhl", game_id=2023020001)
        assert "game_id" in result.columns
        assert result["game_id"].iloc[0] == 2023020001

    def test_no_game_id_column_when_not_provided(self):
        events = [{"typeDescKey": "shot-on-goal", "timeInPeriod": "05:00"}]
        result = transform_pbp(events, "nhl")
        assert "game_id" not in result.columns

    def test_adds_scraped_at_column(self):
        events = [{"typeDescKey": "faceoff", "timeInPeriod": "00:00"}]
        result = transform_pbp(events, "nhl")
        assert "scraped_at" in result.columns
        assert result["scraped_at"].iloc[0] != ""

    def test_normalizes_event_to_lowercase(self):
        events = [{"typeDescKey": "Shot-On-Goal", "timeInPeriod": "05:00"}]
        result = transform_pbp(events, "nhl")
        assert result["event"].iloc[0] == "shot-on-goal"

    def test_computes_time_seconds(self):
        events = [{"typeDescKey": "faceoff", "timeInPeriod": "01:30"}]
        result = transform_pbp(events, "nhl")
        assert "time_seconds" in result.columns
        assert result["time_seconds"].iloc[0] == 90

    def test_multiple_events_preserved(self):
        events = [
            {"typeDescKey": "faceoff", "timeInPeriod": "00:00"},
            {"typeDescKey": "shot-on-goal", "timeInPeriod": "05:20"},
            {"typeDescKey": "goal", "timeInPeriod": "10:00"},
        ]
        result = transform_pbp(events, "nhl")
        assert len(result) == 3


# ---------------------------------------------------------------------------
# _normalize_periods
# ---------------------------------------------------------------------------

class TestNormalizePeriods:
    def test_nhl_numeric_periods_unchanged(self):
        df = pd.DataFrame({"period": [1, 2, 3, 4]})
        result = _normalize_periods(df, "nhl")
        assert list(result["period"].astype(int)) == [1, 2, 3, 4]

    def test_ohl_text_periods_1st_2nd_3rd_ot(self):
        df = pd.DataFrame({"period": ["1st", "2nd", "3rd", "OT"]})
        result = _normalize_periods(df, "ohl")
        assert list(result["period"].astype(int)) == [1, 2, 3, 4]

    def test_whl_text_periods_same_as_ohl(self):
        df = pd.DataFrame({"period": ["1st", "2nd", "3rd", "OT"]})
        result = _normalize_periods(df, "whl")
        assert list(result["period"].astype(int)) == [1, 2, 3, 4]

    def test_qmjhl_ot_mapped_to_4(self):
        df = pd.DataFrame({"period": ["OT"]})
        result = _normalize_periods(df, "qmjhl")
        assert result["period"].iloc[0] == 4

    def test_qmjhl_2nd_ot_mapped_to_5(self):
        df = pd.DataFrame({"period": ["2nd OT"]})
        result = _normalize_periods(df, "qmjhl")
        assert result["period"].iloc[0] == 5

    def test_qmjhl_3rd_ot_mapped_to_6(self):
        df = pd.DataFrame({"period": ["3rd OT"]})
        result = _normalize_periods(df, "qmjhl")
        assert result["period"].iloc[0] == 6

    def test_ahl_ot1_mapped_to_4(self):
        df = pd.DataFrame({"period": ["OT1"]})
        result = _normalize_periods(df, "ahl")
        assert result["period"].iloc[0] == 4

    def test_ahl_ot2_mapped_to_5(self):
        df = pd.DataFrame({"period": ["OT2"]})
        result = _normalize_periods(df, "ahl")
        assert result["period"].iloc[0] == 5

    def test_pwhl_ot1_mapped_to_4(self):
        df = pd.DataFrame({"period": ["OT1"]})
        result = _normalize_periods(df, "pwhl")
        assert result["period"].iloc[0] == 4

    def test_pwhl_ot2_mapped_to_5(self):
        df = pd.DataFrame({"period": ["OT2"]})
        result = _normalize_periods(df, "pwhl")
        assert result["period"].iloc[0] == 5

    def test_missing_period_column_returns_df_unchanged(self):
        df = pd.DataFrame({"event": ["shot"]})
        result = _normalize_periods(df, "nhl")
        assert "period" not in result.columns
        assert "event" in result.columns

    def test_ahl_numeric_string_periods(self):
        df = pd.DataFrame({"period": ["1", "2", "3"]})
        result = _normalize_periods(df, "ahl")
        assert list(result["period"].astype(int)) == [1, 2, 3]


# ---------------------------------------------------------------------------
# _normalize_events
# ---------------------------------------------------------------------------

class TestNormalizeEvents:
    def test_nhl_typeDescKey_becomes_event(self):
        df = pd.DataFrame({"typeDescKey": ["Shot-On-Goal", "GOAL"]})
        result = _normalize_events(df, "nhl")
        assert "event" in result.columns
        assert list(result["event"]) == ["shot-on-goal", "goal"]

    def test_ahl_event_normalized_to_lowercase(self):
        df = pd.DataFrame({"event": ["Shot", "GOAL", "Penalty"]})
        result = _normalize_events(df, "ahl")
        assert list(result["event"]) == ["shot", "goal", "penalty"]

    def test_ohl_event_normalized_to_lowercase(self):
        df = pd.DataFrame({"event": ["FACEOFF", "Blocked-Shot"]})
        result = _normalize_events(df, "ohl")
        assert list(result["event"]) == ["faceoff", "blocked-shot"]

    def test_event_strips_whitespace(self):
        df = pd.DataFrame({"event": ["  goal  ", " shot "]})
        result = _normalize_events(df, "ahl")
        assert list(result["event"]) == ["goal", "shot"]

    def test_missing_source_column_does_not_add_event(self):
        df = pd.DataFrame({"unrelated_col": ["foo"]})
        result = _normalize_events(df, "ohl")
        assert "event" not in result.columns


# ---------------------------------------------------------------------------
# _normalize_strength
# ---------------------------------------------------------------------------

class TestNormalizeStrength:
    def test_nhl_data_unchanged(self):
        df = pd.DataFrame({"strength": ["even", "powerPlay"]})
        result = _normalize_strength(df, "nhl")
        assert list(result["strength"]) == ["even", "powerPlay"]

    def test_hockeytech_empty_goal_type_name_becomes_ev(self):
        df = pd.DataFrame({"goal_type_name": ["", "PP", ""]})
        result = _normalize_strength(df, "ahl")
        assert list(result["goal_type_name"]) == ["EV", "PP", "EV"]

    def test_hockeytech_en_becomes_en_ev(self):
        df = pd.DataFrame({"goal_type_name": ["EN"]})
        result = _normalize_strength(df, "ahl")
        assert result["goal_type_name"].iloc[0] == "EN.EV"

    def test_hockeytech_goal_type_column(self):
        df = pd.DataFrame({"goal_type": ["", "SH"]})
        result = _normalize_strength(df, "ohl")
        assert result["goal_type"].iloc[0] == "EV"
        assert result["goal_type"].iloc[1] == "SH"

    def test_no_goal_type_columns_unchanged(self):
        df = pd.DataFrame({"event": ["goal"]})
        result = _normalize_strength(df, "ahl")
        assert "goal_type_name" not in result.columns
        assert "goal_type" not in result.columns


# ---------------------------------------------------------------------------
# _calculate_scores
# ---------------------------------------------------------------------------

class TestCalculateScores:
    def test_cumulative_home_and_away_goals(self):
        df = pd.DataFrame({
            "event": ["shot", "goal", "shot", "goal", "goal"],
            "home": [1, 1, 0, 0, 1],
        })
        result = _calculate_scores(df)
        assert "score_home" in result.columns
        assert "score_away" in result.columns
        assert result["score_home"].iloc[-1] == 2
        assert result["score_away"].iloc[-1] == 1

    def test_no_event_column_returns_unchanged(self):
        df = pd.DataFrame({"period": [1, 2]})
        result = _calculate_scores(df)
        assert "score_home" not in result.columns

    def test_all_home_goals(self):
        df = pd.DataFrame({
            "event": ["goal", "goal", "goal"],
            "home": ["1", "1", "1"],  # HockeyTech sends string "1"/"0"
        })
        result = _calculate_scores(df)
        assert list(result["score_home"]) == [1, 2, 3]
        assert list(result["score_away"]) == [0, 0, 0]

    def test_all_away_goals(self):
        df = pd.DataFrame({
            "event": ["goal", "goal"],
            "home": ["0", "0"],
        })
        result = _calculate_scores(df)
        assert list(result["score_home"]) == [0, 0]
        assert list(result["score_away"]) == [1, 2]

    def test_no_goals_scores_remain_zero(self):
        df = pd.DataFrame({
            "event": ["faceoff", "shot", "blocked-shot"],
            "home": [1, 0, 1],
        })
        result = _calculate_scores(df)
        assert result["score_home"].max() == 0
        assert result["score_away"].max() == 0

    def test_internal_columns_removed(self):
        df = pd.DataFrame({"event": ["goal"], "home": [1]})
        result = _calculate_scores(df)
        assert "_home_goal" not in result.columns
        assert "_away_goal" not in result.columns

    def test_missing_home_column_still_returns_score_columns(self):
        # Events without 'home' key: scores should all be zero (no team tracking)
        df = pd.DataFrame({"event": ["shot", "goal", "shot"]})
        result = _calculate_scores(df)
        assert "score_home" in result.columns
        assert "score_away" in result.columns


# ---------------------------------------------------------------------------
# _add_metadata
# ---------------------------------------------------------------------------

class TestAddMetadata:
    def test_adds_league_column_uppercase(self):
        df = pd.DataFrame({"event": ["shot"]})
        result = _add_metadata(df, "nhl")
        assert result["league"].iloc[0] == "NHL"

    def test_ahl_league_uppercase(self):
        df = pd.DataFrame({"event": ["shot"]})
        result = _add_metadata(df, "ahl")
        assert result["league"].iloc[0] == "AHL"

    def test_adds_game_id_when_provided(self):
        df = pd.DataFrame({"event": ["shot"]})
        result = _add_metadata(df, "ahl", game_id=99999)
        assert result["game_id"].iloc[0] == 99999

    def test_no_game_id_column_when_not_provided(self):
        df = pd.DataFrame({"event": ["shot"]})
        result = _add_metadata(df, "nhl")
        assert "game_id" not in result.columns

    def test_adds_scraped_at_iso_timestamp(self):
        df = pd.DataFrame({"event": ["shot"]})
        result = _add_metadata(df, "nhl")
        assert "scraped_at" in result.columns
        ts = result["scraped_at"].iloc[0]
        assert "T" in ts  # ISO-8601 format


# ---------------------------------------------------------------------------
# nhlify_goals
# ---------------------------------------------------------------------------

class TestNhlifyGoals:
    def test_merges_shot_and_goal_at_same_time(self):
        df = pd.DataFrame({
            "event": ["shot", "goal"],
            "period": [1, 1],
            "time_seconds": [300.0, 300.0],
            "game_seconds": [300.0, 300.0],
            "x_location": [150.0, None],
            "y_location": [200.0, None],
            "home": ["1", "1"],
        })
        result = nhlify_goals(df)
        assert len(result) == 1
        assert result["event"].iloc[0] == "goal"
        assert result["x_location"].iloc[0] == 150.0

    def test_shot_coordinates_copied_to_goal(self):
        df = pd.DataFrame({
            "event": ["shot", "goal"],
            "period": [1, 1],
            "time_seconds": [600.0, 600.0],
            "game_seconds": [600.0, 600.0],
            "x_location": [80.0, None],
            "y_location": [10.0, None],
            "home": ["0", "0"],
        })
        result = nhlify_goals(df)
        assert len(result) == 1
        assert result["x_location"].iloc[0] == 80.0
        assert result["y_location"].iloc[0] == 10.0

    def test_does_not_merge_different_team_events(self):
        df = pd.DataFrame({
            "event": ["shot", "goal"],
            "period": [2, 2],
            "time_seconds": [700.0, 700.0],
            "game_seconds": [1900.0, 1900.0],
            "x_location": [100.0, None],
            "y_location": [50.0, None],
            "home": ["1", "0"],  # different teams
        })
        result = nhlify_goals(df)
        # Both rows kept since teams differ
        assert len(result) == 2

    def test_does_not_merge_events_at_different_times(self):
        df = pd.DataFrame({
            "event": ["shot", "goal"],
            "period": [1, 1],
            "time_seconds": [300.0, 310.0],  # different times
            "game_seconds": [300.0, 310.0],
            "home": ["1", "1"],
        })
        result = nhlify_goals(df)
        assert len(result) == 2

    def test_empty_dataframe_returned_unchanged(self):
        df = pd.DataFrame()
        result = nhlify_goals(df)
        assert result.empty

    def test_no_matching_shots_unchanged(self):
        df = pd.DataFrame({
            "event": ["faceoff", "penalty", "goal"],
            "period": [1, 1, 2],
            "time_seconds": [0.0, 400.0, 900.0],
            "game_seconds": [0.0, 400.0, 2100.0],
            "home": ["1", "0", "1"],
        })
        result = nhlify_goals(df)
        assert len(result) == 3

    def test_penalty_shot_also_merged(self):
        df = pd.DataFrame({
            "event": ["penaltyshot", "goal"],
            "period": [3, 3],
            "time_seconds": [900.0, 900.0],
            "game_seconds": [2700.0 + 900.0, 2700.0 + 900.0],
            "x_location": [88.0, None],
            "y_location": [0.0, None],
            "home": ["1", "1"],
        })
        result = nhlify_goals(df)
        assert len(result) == 1
        assert result["event"].iloc[0] == "goal"
        assert result["x_location"].iloc[0] == 88.0
