"""Unit tests for scrapernhl.parsers — pure functions, no I/O."""
import pytest

from scrapernhl.parsers import (
    _unpack_hockeytech_a_event,
    parse_pbp,
    parse_player_page,
    parse_roster,
    parse_schedule,
    parse_standings,
    parse_stats,
)


# ---------------------------------------------------------------------------
# parse_pbp
# ---------------------------------------------------------------------------

class TestParsePbpNHL:
    def test_returns_plays_list(self):
        data = {
            "plays": [
                {"typeDescKey": "shot-on-goal", "timeInPeriod": "05:20"},
                {"typeDescKey": "goal", "timeInPeriod": "10:00"},
            ],
            "homeTeam": {"id": 8},
            "awayTeam": {"id": 9},
        }
        result = parse_pbp("nhl", "nhl", data)
        assert len(result) == 2
        assert result[0]["typeDescKey"] == "shot-on-goal"

    def test_empty_plays_list(self):
        data = {"plays": [], "homeTeam": {}, "awayTeam": {}}
        result = parse_pbp("nhl", "nhl", data)
        assert result == []

    def test_missing_plays_key_returns_empty(self):
        result = parse_pbp("nhl", "nhl", {})
        assert result == []

    def test_plays_content_preserved(self):
        data = {"plays": [{"eventId": 42, "typeDescKey": "faceoff"}]}
        result = parse_pbp("nhl", "nhl", data)
        assert result[0]["eventId"] == 42


class TestParsePbpHockeytechA:
    def test_returns_unpacked_events(self):
        raw = [
            {
                "event": "shot",
                "details": {
                    "period": {"id": "1"},
                    "time": "05:30",
                    "xLocation": 150.0,
                    "yLocation": 200.0,
                },
            }
        ]
        result = parse_pbp("ahl", "hockeytech_a", raw)
        assert len(result) == 1
        assert result[0]["event"] == "shot"
        assert result[0]["time"] == "05:30"
        assert result[0]["x_location"] == 150.0

    def test_empty_list_returns_empty(self):
        result = parse_pbp("ahl", "hockeytech_a", [])
        assert result == []

    def test_non_list_input_returns_empty(self):
        result = parse_pbp("ahl", "hockeytech_a", {"events": []})
        assert result == []


class TestParsePbpHockeytechB:
    def test_extracts_nested_events(self):
        data = {
            "GC": {
                "Pxpverbose": [
                    {"event": "shot", "period": "1"},
                    {"event": "goal", "period": "1"},
                ]
            }
        }
        result = parse_pbp("ohl", "hockeytech_b", data)
        assert len(result) == 2
        assert result[1]["event"] == "goal"

    def test_missing_nested_key_returns_empty(self):
        result = parse_pbp("ohl", "hockeytech_b", {"GC": {}})
        assert result == []

    def test_missing_gc_key_returns_empty(self):
        result = parse_pbp("ohl", "hockeytech_b", {})
        assert result == []


# ---------------------------------------------------------------------------
# _unpack_hockeytech_a_event
# ---------------------------------------------------------------------------

class TestUnpackHockeytechAEvent:
    def test_basic_fields_extracted(self):
        ev = {
            "event": "shot",
            "details": {
                "period": {"id": "2", "shortName": "2", "longName": "2nd"},
                "time": "10:25",
                "xLocation": 100.0,
                "yLocation": 150.0,
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["event"] == "shot"
        assert result["period"] == "2"
        assert result["time"] == "10:25"
        assert result["x_location"] == 100.0
        assert result["y_location"] == 150.0

    def test_powerplay_goal_type(self):
        ev = {
            "event": "goal",
            "details": {
                "period": {"id": "1"},
                "time": "08:00",
                "isGoal": True,
                "properties": {
                    "isPowerPlay": True,
                    "isShortHanded": False,
                    "isEmptyNet": False,
                },
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["goal_type"] == "PP"
        assert result["isGoal"] is True

    def test_shorthanded_goal_type(self):
        ev = {
            "event": "goal",
            "details": {
                "period": {"id": "3"},
                "time": "15:00",
                "isGoal": True,
                "properties": {
                    "isPowerPlay": False,
                    "isShortHanded": True,
                    "isEmptyNet": False,
                },
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["goal_type"] == "SH"

    def test_even_strength_goal_type(self):
        ev = {
            "event": "goal",
            "details": {
                "period": {"id": "2"},
                "time": "05:00",
                "properties": {
                    "isPowerPlay": False,
                    "isShortHanded": False,
                    "isEmptyNet": False,
                },
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["goal_type"] == "EV"

    def test_empty_net_even_strength(self):
        ev = {
            "event": "goal",
            "details": {
                "period": {"id": "3"},
                "time": "19:45",
                "isGoal": True,
                "properties": {
                    "isPowerPlay": False,
                    "isShortHanded": False,
                    "isEmptyNet": True,
                },
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["goal_type"] == "EV.EN"

    def test_empty_net_powerplay(self):
        ev = {
            "event": "goal",
            "details": {
                "period": {"id": "3"},
                "time": "19:45",
                "properties": {
                    "isPowerPlay": True,
                    "isShortHanded": False,
                    "isEmptyNet": True,
                },
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["goal_type"] == "PP.EN"

    def test_missing_details_uses_defaults(self):
        ev = {"event": "faceoff"}
        result = _unpack_hockeytech_a_event(ev)
        assert result["event"] == "faceoff"
        assert result["period"] is None
        assert result["time"] is None
        assert result["x_location"] is None

    def test_player_fields_extracted(self):
        ev = {
            "event": "shot",
            "details": {
                "period": {"id": "1"},
                "time": "05:00",
                "shooter": {"id": "99", "firstName": "Test", "lastName": "Player"},
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert result["shooter"]["id"] == "99"

    def test_on_ice_arrays_extracted(self):
        ev = {
            "event": "goal",
            "details": {
                "period": {"id": "1"},
                "time": "05:00",
                "plusPlayers": [{"id": "1"}, {"id": "2"}],
                "minusPlayers": [{"id": "3"}],
                "properties": {},
            },
        }
        result = _unpack_hockeytech_a_event(ev)
        assert len(result["plus"]) == 2
        assert len(result["minus"]) == 1


# ---------------------------------------------------------------------------
# parse_stats
# ---------------------------------------------------------------------------

class TestParseStats:
    def test_nhl_skaters(self):
        data = {"skaters": [{"playerId": 1, "points": 50}], "goalies": []}
        result = parse_stats("nhl", data, "skaters")
        assert len(result) == 1
        assert result[0]["playerId"] == 1

    def test_nhl_goalies(self):
        data = {"skaters": [], "goalies": [{"playerId": 2, "wins": 20}]}
        result = parse_stats("nhl", data, "goalies")
        assert len(result) == 1
        assert result[0]["wins"] == 20

    def test_nhl_missing_key_returns_empty(self):
        result = parse_stats("nhl", {}, "skaters")
        assert result == []

    def test_hockeytech_sitekit_path(self):
        data = {
            "SiteKit": {
                "Players": [
                    {"player_id": "99", "name": "Test Player", "goals": "10"},
                ]
            }
        }
        result = parse_stats("ahl", data, "skaters")
        assert len(result) == 1
        assert result[0]["player_id"] == "99"

    def test_hockeytech_sections_path(self):
        data = [
            {
                "sections": [
                    {
                        "data": [
                            {"row": {"player_id": "10", "goals": "5"}},
                            {"row": {"player_id": "11", "goals": "3"}},
                        ]
                    }
                ]
            }
        ]
        result = parse_stats("ahl", data, "skaters")
        assert len(result) == 2

    def test_list_input_returned_directly(self):
        data = [{"player_id": "5"}, {"player_id": "6"}]
        result = parse_stats("ahl", data, "skaters")
        assert len(result) == 2


# ---------------------------------------------------------------------------
# parse_schedule
# ---------------------------------------------------------------------------

class TestParseSchedule:
    def test_nhl_returns_games(self):
        data = {
            "games": [
                {"id": 2023020001, "homeTeam": {"abbrev": "MTL"}},
                {"id": 2023020002, "homeTeam": {"abbrev": "TOR"}},
            ]
        }
        result = parse_schedule("nhl", data)
        assert len(result) == 2

    def test_nhl_empty_games(self):
        result = parse_schedule("nhl", {"games": []})
        assert result == []

    def test_nhl_missing_games_key(self):
        result = parse_schedule("nhl", {})
        assert result == []

    def test_hockeytech_sections_path(self):
        data = [
            {
                "sections": [
                    {"data": [{"id": 101}, {"id": 102}]},
                    {"data": [{"id": 103}]},
                ]
            }
        ]
        result = parse_schedule("ahl", data)
        assert len(result) == 3

    def test_hockeytech_empty_sections(self):
        data = [{"sections": []}]
        result = parse_schedule("ahl", data)
        assert result == []

    def test_hockeytech_non_list_returns_empty(self):
        result = parse_schedule("ahl", {})
        assert result == []


# ---------------------------------------------------------------------------
# parse_roster
# ---------------------------------------------------------------------------

class TestParseRoster:
    def test_nhl_combines_all_positions(self):
        data = {
            "forwards": [{"playerId": 1}, {"playerId": 2}],
            "defensemen": [{"playerId": 3}],
            "goalies": [{"playerId": 4}],
        }
        result = parse_roster("nhl", data)
        assert len(result) == 4
        ids = [p["playerId"] for p in result]
        assert set(ids) == {1, 2, 3, 4}

    def test_nhl_preserves_order(self):
        data = {
            "forwards": [{"playerId": 1}],
            "defensemen": [{"playerId": 2}],
            "goalies": [{"playerId": 3}],
        }
        result = parse_roster("nhl", data)
        assert result[0]["playerId"] == 1
        assert result[1]["playerId"] == 2
        assert result[2]["playerId"] == 3

    def test_nhl_empty_positions(self):
        data = {"forwards": [], "defensemen": [], "goalies": []}
        result = parse_roster("nhl", data)
        assert result == []

    def test_nhl_missing_keys(self):
        result = parse_roster("nhl", {})
        assert result == []

    def test_hockeytech_sitekit_path(self):
        data = {
            "SiteKit": {
                "Roster": [{"player_id": "10"}, {"player_id": "20"}]
            }
        }
        result = parse_roster("ahl", data)
        assert len(result) == 2

    def test_hockeytech_sections_path(self):
        data = {
            "roster": [
                {
                    "sections": [
                        {
                            "title": "Forwards",
                            "data": [{"row": {"player_id": "1"}}, {"row": {"player_id": "2"}}],
                        },
                        {
                            "title": "Defencemen",
                            "data": [{"row": {"player_id": "3"}}],
                        },
                        {
                            "title": "Goalies",
                            "data": [{"row": {"player_id": "4"}}],
                        },
                    ]
                }
            ]
        }
        result = parse_roster("ahl", data)
        assert len(result) == 4


# ---------------------------------------------------------------------------
# parse_standings
# ---------------------------------------------------------------------------

class TestParseStandings:
    def test_nhl_returns_standings_list(self):
        data = {
            "standings": [
                {"teamName": {"default": "Montréal Canadiens"}, "points": 80},
                {"teamName": {"default": "Toronto Maple Leafs"}, "points": 90},
            ]
        }
        result = parse_standings("nhl", data)
        assert len(result) == 2
        assert result[0]["points"] == 80

    def test_nhl_missing_key_returns_empty(self):
        result = parse_standings("nhl", {})
        assert result == []

    def test_hockeytech_sitekit_path(self):
        data = {
            "SiteKit": {
                "Standings": [
                    {"team_code": "BUF", "points": "70"},
                    {"team_code": "ROC", "points": "65"},
                ]
            }
        }
        result = parse_standings("ahl", data)
        assert len(result) == 2

    def test_hockeytech_sections_path(self):
        data = [
            {
                "sections": [
                    {
                        "data": [
                            {"row": {"team_code": "LAV", "points": "80"}},
                        ]
                    },
                    {
                        "data": [
                            {"row": {"team_code": "SYR", "points": "75"}},
                        ]
                    },
                ]
            }
        ]
        result = parse_standings("ahl", data)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# parse_player_page
# ---------------------------------------------------------------------------

class TestParsePlayerPage:
    def test_returns_sitekit_subtree(self):
        data = {
            "SiteKit": {
                "info": {"player_id": "99", "name": "Test Player"},
                "careerStats": [],
                "seasonStats": [],
            }
        }
        result = parse_player_page(data)
        assert "info" in result
        assert result["info"]["player_id"] == "99"
        assert "careerStats" in result

    def test_non_dict_returns_empty(self):
        result = parse_player_page([])
        assert result == {}

    def test_none_returns_empty(self):
        result = parse_player_page(None)
        assert result == {}

    def test_missing_sitekit_returns_original_dict(self):
        data = {"info": {"player_id": "1"}}
        result = parse_player_page(data)
        assert result == data
