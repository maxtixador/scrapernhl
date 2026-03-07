"""Unit tests for scrapernhl.client.HockeyScraper — all HTTP mocked."""
import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from scrapernhl.client import HockeyScraper
from scrapernhl.exceptions import ScraperNHLError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok_response(body: dict) -> MagicMock:
    """Return a mock requests.Response with status 200 and JSON body."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = body
    resp.text = json.dumps(body)
    resp.raise_for_status.return_value = None
    return resp


def _make_scraper(league: str = "nhl", bootstrap: dict | None = None) -> HockeyScraper:
    """Create a HockeyScraper with a mocked session and optional injected bootstrap."""
    scraper = HockeyScraper(league)
    scraper.session = MagicMock()
    # Disable disk cache for unit tests
    scraper.cache = MagicMock()
    scraper.cache.get.return_value = None
    if bootstrap is not None:
        scraper.bootstrap_data = bootstrap
    return scraper


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestHockeyScraperInit:
    def test_nhl_no_rate_limiter(self):
        scraper = HockeyScraper("nhl")
        assert scraper.limiter is None

    def test_league_normalized_to_lowercase(self):
        scraper = HockeyScraper("NHL")
        assert scraper.league == "nhl"

    def test_nhl_bootstrap_not_auto_fetched(self):
        """NHL league must never auto-fetch bootstrap on instantiation."""
        scraper = HockeyScraper("nhl")
        assert scraper._bootstrap_data is None

    def test_ahl_has_rate_limiter(self):
        scraper = HockeyScraper("ahl")
        assert scraper.limiter is not None

    def test_ohl_has_rate_limiter(self):
        scraper = HockeyScraper("ohl")
        assert scraper.limiter is not None

    def test_unknown_league_raises_key_error(self):
        with pytest.raises(KeyError):
            HockeyScraper("invalid_league")

    def test_league_stored(self):
        scraper = HockeyScraper("pwhl")
        assert scraper.league == "pwhl"

    def test_nhl_bootstrap_property_returns_empty_dict(self):
        """_bootstrap for NHL returns {} since NHL never fetches bootstrap data."""
        scraper = HockeyScraper("nhl")
        assert scraper._bootstrap == {}


# ---------------------------------------------------------------------------
# Bootstrap property and injection
# ---------------------------------------------------------------------------

class TestBootstrapProperty:
    def test_injected_bootstrap_accessible_via_property(self):
        scraper = HockeyScraper("ahl")
        scraper.bootstrap_data = {"ahl": {"current_season_id": "90"}}
        assert scraper.bootstrap_data["ahl"]["current_season_id"] == "90"

    def test_bootstrap_setter(self):
        scraper = HockeyScraper("ahl")
        scraper.bootstrap_data = {"ahl": {"teams": []}}
        assert scraper._bootstrap_data == {"ahl": {"teams": []}}

    def test_bootstrap_underscore_extracts_league_subtree(self):
        scraper = HockeyScraper("ahl")
        scraper.bootstrap_data = {
            "ahl": {"current_season_id": "90", "teamsNoAll": []},
        }
        assert scraper._bootstrap["current_season_id"] == "90"


# ---------------------------------------------------------------------------
# Bootstrap accessor methods
# ---------------------------------------------------------------------------

class TestBootstrapAccessors:
    def test_get_teams_returns_teams_no_all(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {
                "teamsNoAll": [{"id": "1", "name": "Laval Rocket", "team_code": "LAV"}],
                "teams": [{"id": "0", "name": "All Teams"}, {"id": "1", "name": "Laval Rocket"}],
            }
        })
        teams = scraper.get_teams()
        assert len(teams) == 1
        assert teams[0]["name"] == "Laval Rocket"

    def test_get_teams_include_all(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {
                "teamsNoAll": [{"id": "1", "name": "Laval"}],
                "teams": [{"id": "0", "name": "All"}, {"id": "1", "name": "Laval"}],
            }
        })
        teams = scraper.get_teams(include_all=True)
        assert len(teams) == 2

    def test_get_team_by_code_found(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {
                "teams": [{"id": "5", "name": "Team", "team_code": "TM"}],
                "teamsNoAll": [{"id": "5", "name": "Team", "team_code": "TM"}],
            }
        })
        team = scraper.get_team_by_code("TM")
        assert team is not None
        assert team["id"] == "5"

    def test_get_team_by_code_case_insensitive(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {
                "teams": [{"id": "5", "name": "Team", "team_code": "LAV"}],
                "teamsNoAll": [{"id": "5", "name": "Team", "team_code": "LAV"}],
            }
        })
        team = scraper.get_team_by_code("lav")
        assert team is not None
        assert team["id"] == "5"

    def test_get_team_by_code_not_found(self):
        scraper = _make_scraper("ahl", bootstrap={"ahl": {"teamsNoAll": []}})
        result = scraper.get_team_by_code("ZZZZ")
        assert result is None

    def test_get_seasons_regular(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {
                "regularSeasons": [{"id": "90", "name": "2024-25"}],
                "playoffSeasons": [{"id": "91", "name": "2024-25 Playoffs"}],
            }
        })
        seasons = scraper.get_seasons("regular")
        assert len(seasons) == 1
        assert seasons[0]["id"] == "90"

    def test_get_seasons_playoff(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {
                "regularSeasons": [{"id": "90"}],
                "playoffSeasons": [{"id": "91"}],
            }
        })
        seasons = scraper.get_seasons("playoff")
        assert len(seasons) == 1
        assert seasons[0]["id"] == "91"

    def test_get_current_season_id(self):
        scraper = _make_scraper("ahl", bootstrap={
            "ahl": {"current_season_id": "90"}
        })
        assert scraper.get_current_season_id() == "90"

    def test_empty_bootstrap_returns_empty_teams(self):
        scraper = _make_scraper("ahl", bootstrap={"ahl": {}})
        assert scraper.get_teams() == []


# ---------------------------------------------------------------------------
# NHL play_by_play
# ---------------------------------------------------------------------------

class TestNHLPlayByPlay:
    def test_returns_dataframe(self):
        data = {
            "plays": [
                {"typeDescKey": "faceoff", "timeInPeriod": "00:00"},
                {"typeDescKey": "shot-on-goal", "timeInPeriod": "05:20"},
            ],
            "homeTeam": {"id": 8},
            "awayTeam": {"id": 9},
        }
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.play_by_play(2023020001)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_raw_true_returns_dict(self):
        data = {"plays": [{"typeDescKey": "goal"}], "homeTeam": {}, "awayTeam": {}}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.play_by_play(2023020001, raw=True)
        assert isinstance(result, dict)
        assert "plays" in result

    def test_dataframe_has_league_column(self):
        data = {"plays": [{"typeDescKey": "faceoff", "timeInPeriod": "00:00"}]}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.play_by_play(2023020001)
        assert "league" in result.columns
        assert result["league"].iloc[0] == "NHL"

    def test_invalid_game_id_raises_value_error(self):
        scraper = _make_scraper("nhl")
        with pytest.raises(ValueError):
            scraper.play_by_play("not_a_game_id")

    def test_negative_game_id_raises_value_error(self):
        scraper = _make_scraper("nhl")
        with pytest.raises(ValueError):
            scraper.play_by_play(-1)

    def test_empty_plays_returns_empty_dataframe(self):
        data = {"plays": [], "homeTeam": {}, "awayTeam": {}}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.play_by_play(2023020001)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_string_numeric_game_id_accepted(self):
        data = {"plays": [], "homeTeam": {}, "awayTeam": {}}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        # "2023020001" should be coerced to int
        result = scraper.play_by_play("2023020001")
        assert isinstance(result, pd.DataFrame)


# ---------------------------------------------------------------------------
# NHL schedule
# ---------------------------------------------------------------------------

class TestNHLSchedule:
    def test_returns_dataframe(self):
        data = {
            "games": [
                {"id": 2023020001, "homeTeam": {"abbrev": "MTL"}, "awayTeam": {"abbrev": "TOR"}},
                {"id": 2023020002, "homeTeam": {"abbrev": "BOS"}, "awayTeam": {"abbrev": "FLA"}},
            ]
        }
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.schedule("MTL", season=20232024)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_raw_true_returns_dict(self):
        data = {"games": [{"id": 2023020001}]}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.schedule("MTL", raw=True)
        assert isinstance(result, dict)
        assert "games" in result

    def test_empty_games_returns_empty_dataframe(self):
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response({"games": []})
        result = scraper.schedule("MTL")
        assert isinstance(result, pd.DataFrame)


# ---------------------------------------------------------------------------
# NHL roster
# ---------------------------------------------------------------------------

class TestNHLRoster:
    def test_returns_dataframe_with_all_positions(self):
        data = {
            "forwards": [
                {"playerId": 1, "firstName": {"default": "Alice"}, "lastName": {"default": "A"}},
                {"playerId": 2, "firstName": {"default": "Bob"}, "lastName": {"default": "B"}},
            ],
            "defensemen": [
                {"playerId": 3, "firstName": {"default": "Charlie"}, "lastName": {"default": "C"}},
            ],
            "goalies": [
                {"playerId": 4, "firstName": {"default": "Dave"}, "lastName": {"default": "D"}},
            ],
        }
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.roster("MTL")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4

    def test_raw_true_returns_dict(self):
        data = {"forwards": [], "defensemen": [], "goalies": []}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.roster("MTL", raw=True)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# NHL standings
# ---------------------------------------------------------------------------

class TestNHLStandings:
    def test_returns_dataframe(self):
        data = {
            "standings": [
                {"teamName": {"default": "Montréal Canadiens"}, "points": 80},
                {"teamName": {"default": "Toronto Maple Leafs"}, "points": 90},
            ]
        }
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.standings()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_raw_true_returns_dict(self):
        data = {"standings": [{"points": 100}]}
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.standings(raw=True)
        assert isinstance(result, dict)
        assert "standings" in result


# ---------------------------------------------------------------------------
# scrape_multiple_games
# ---------------------------------------------------------------------------

class TestScrapeMultipleGames:
    def test_returns_concatenated_dataframe(self):
        data = {
            "plays": [{"typeDescKey": "faceoff", "timeInPeriod": "00:00"}],
            "homeTeam": {},
            "awayTeam": {},
        }
        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = _ok_response(data)
        result = scraper.scrape_multiple_games([2023020001, 2023020002])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # one event per game

    def test_empty_list_returns_empty_dataframe(self):
        scraper = _make_scraper("nhl")
        result = scraper.scrape_multiple_games([])
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_failed_game_logs_warning_not_raises(self):
        """A fetching failure is logged at WARNING level and does not abort the batch."""
        from unittest.mock import patch

        success_data = {
            "plays": [{"typeDescKey": "shot-on-goal", "timeInPeriod": "05:00"}],
            "homeTeam": {},
            "awayTeam": {},
        }
        error_resp = MagicMock(spec=requests.Response)
        error_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )

        scraper = _make_scraper("nhl")
        scraper.session.get.side_effect = [
            _ok_response(success_data),
            error_resp,
        ]

        with patch("scrapernhl.client.LOG.warning") as mock_warn:
            results = scraper.scrape_multiple_games([2023020001, 2023020002])

        # First game succeeded
        assert len(results) == 1
        # LOG.warning was called (not print, not raise)
        assert mock_warn.called
        # The failed game ID appears in the warning arguments
        warn_args = str(mock_warn.call_args)
        assert "2023020002" in warn_args

    def test_all_games_fail_returns_empty_dataframe(self):
        error_resp = MagicMock(spec=requests.Response)
        error_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500")

        scraper = _make_scraper("nhl")
        scraper.session.get.return_value = error_resp

        result = scraper.scrape_multiple_games([2023020001, 2023020002])
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_partial_failure_preserves_successful_games(self):
        """Games after a failed one are still processed."""
        data = {
            "plays": [{"typeDescKey": "faceoff", "timeInPeriod": "00:00"}],
            "homeTeam": {},
            "awayTeam": {},
        }
        error_resp = MagicMock(spec=requests.Response)
        error_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500")

        scraper = _make_scraper("nhl")
        scraper.session.get.side_effect = [
            _ok_response(data),   # game 1: success
            error_resp,            # game 2: failure
            _ok_response(data),   # game 3: success
        ]
        result = scraper.scrape_multiple_games([2023020001, 2023020002, 2023020003])
        assert len(result) == 2  # two successful games


# ---------------------------------------------------------------------------
# _stamp (lineage columns)
# ---------------------------------------------------------------------------

class TestStamp:
    def test_stamp_adds_scraped_at_and_league(self):
        scraper = _make_scraper("nhl")
        df = pd.DataFrame({"points": [50, 60]})
        result = scraper._stamp(df)
        assert "scraped_at" in result.columns
        assert "league" in result.columns
        assert result["league"].iloc[0] == "nhl"

    def test_stamp_does_not_overwrite_existing_columns(self):
        scraper = _make_scraper("nhl")
        df = pd.DataFrame({"scraped_at": ["2024-01-01"], "league": ["ahl"]})
        result = scraper._stamp(df)
        # Pre-existing values are kept
        assert result["scraped_at"].iloc[0] == "2024-01-01"
        assert result["league"].iloc[0] == "ahl"
