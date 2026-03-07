"""Unit tests for scrapernhl.exceptions — no I/O, no network."""
import pytest

from scrapernhl.exceptions import (
    APIError,
    CacheError,
    DataValidationError,
    InvalidGameError,
    InvalidSeasonError,
    InvalidTeamError,
    ParsingError,
    RateLimitError,
    ScraperNHLError,
)


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:
    def test_api_error_is_scraper_error(self):
        assert issubclass(APIError, ScraperNHLError)

    def test_rate_limit_is_api_error(self):
        assert issubclass(RateLimitError, APIError)

    def test_rate_limit_is_scraper_error(self):
        assert issubclass(RateLimitError, ScraperNHLError)

    def test_parsing_error_is_scraper_error(self):
        assert issubclass(ParsingError, ScraperNHLError)

    def test_invalid_game_error_is_scraper_error(self):
        assert issubclass(InvalidGameError, ScraperNHLError)

    def test_invalid_team_error_is_scraper_error(self):
        assert issubclass(InvalidTeamError, ScraperNHLError)

    def test_invalid_season_error_is_scraper_error(self):
        assert issubclass(InvalidSeasonError, ScraperNHLError)

    def test_data_validation_error_is_scraper_error(self):
        assert issubclass(DataValidationError, ScraperNHLError)

    def test_cache_error_is_scraper_error(self):
        assert issubclass(CacheError, ScraperNHLError)


# ---------------------------------------------------------------------------
# APIError
# ---------------------------------------------------------------------------

class TestAPIError:
    def test_stores_message(self):
        err = APIError("something went wrong")
        assert str(err) == "something went wrong"

    def test_stores_status_code(self):
        err = APIError("HTTP error", status_code=404)
        assert err.status_code == 404

    def test_stores_response_text(self):
        err = APIError("error", response_text="Not Found")
        assert err.response_text == "Not Found"

    def test_defaults_are_none(self):
        err = APIError("error")
        assert err.status_code is None
        assert err.response_text is None

    def test_is_exception(self):
        err = APIError("error")
        assert isinstance(err, Exception)


# ---------------------------------------------------------------------------
# RateLimitError
# ---------------------------------------------------------------------------

class TestRateLimitError:
    def test_stores_retry_after(self):
        err = RateLimitError("rate limited", retry_after=30)
        assert err.retry_after == 30

    def test_default_retry_after_is_none(self):
        err = RateLimitError("rate limited")
        assert err.retry_after is None

    def test_sets_status_code_429(self):
        err = RateLimitError("rate limited")
        assert err.status_code == 429

    def test_is_api_error(self):
        err = RateLimitError("rate limited", retry_after=60)
        assert isinstance(err, APIError)

    def test_is_scraper_error(self):
        err = RateLimitError("rate limited")
        assert isinstance(err, ScraperNHLError)


# ---------------------------------------------------------------------------
# DataValidationError
# ---------------------------------------------------------------------------

class TestDataValidationError:
    def test_stores_missing_columns(self):
        err = DataValidationError("validation failed", missing_columns=["goals", "assists"])
        assert "goals" in err.missing_columns
        assert "assists" in err.missing_columns

    def test_stores_invalid_dtypes(self):
        err = DataValidationError("validation failed", invalid_dtypes={"points": "str"})
        assert err.invalid_dtypes["points"] == "str"

    def test_stores_validation_errors(self):
        err = DataValidationError(
            "validation failed",
            validation_errors=["points must be non-negative"],
        )
        assert len(err.validation_errors) == 1

    def test_defaults_are_empty_collections(self):
        err = DataValidationError("validation failed")
        assert err.missing_columns == []
        assert err.invalid_dtypes == {}
        assert err.validation_errors == []


# ---------------------------------------------------------------------------
# Catch-all: except ScraperNHLError catches all custom exceptions
# ---------------------------------------------------------------------------

class TestCatchAll:
    @pytest.mark.parametrize("exc", [
        APIError("api"),
        RateLimitError("rl"),
        ParsingError("parse"),
        InvalidGameError("game"),
        InvalidTeamError("team"),
        InvalidSeasonError("season"),
        CacheError("cache"),
        DataValidationError("data"),
    ])
    def test_all_caught_by_scraper_error(self, exc):
        with pytest.raises(ScraperNHLError):
            raise exc

    def test_catching_base_does_not_swallow_rate_limit(self):
        err = RateLimitError("rl", retry_after=5)
        try:
            raise err
        except ScraperNHLError as e:
            assert isinstance(e, RateLimitError)
            assert e.retry_after == 5
