"""Unit tests for scrapernhl.core.http — all network calls mocked."""
import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from scrapernhl.core.http import fetch_html, fetch_json
from scrapernhl.exceptions import APIError, RateLimitError


def _make_response(
    status_code: int,
    body: str | dict = "",
    headers: dict | None = None,
) -> MagicMock:
    """Build a fake requests.Response that mimics the real object closely enough."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.headers = headers or {}

    if isinstance(body, dict):
        resp.text = json.dumps(body)
        resp.json.return_value = body
    else:
        resp.text = body
        try:
            resp.json.return_value = json.loads(body) if body else {}
        except (ValueError, TypeError):
            resp.json.return_value = {}

    if status_code >= 400:
        http_error = requests.exceptions.HTTPError(
            f"{status_code} Error", response=resp
        )
        resp.raise_for_status.side_effect = http_error
    else:
        resp.raise_for_status.return_value = None

    return resp


# ---------------------------------------------------------------------------
# fetch_json
# ---------------------------------------------------------------------------

class TestFetchJson:
    def test_returns_parsed_dict_on_200(self):
        payload = {"plays": [{"event": "goal"}], "homeTeam": {}}
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(200, payload)):
            result = fetch_json("https://example.com/api/pbp")
        assert result == payload

    def test_returns_empty_dict_on_200_empty_body(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(200, {})):
            result = fetch_json("https://example.com/api")
        assert result == {}

    def test_raises_api_error_on_404(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(404)):
            with pytest.raises(APIError):
                fetch_json("https://example.com/api/notfound")

    def test_raises_api_error_on_500(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(500, "Server Error")):
            with pytest.raises(APIError):
                fetch_json("https://example.com/api")

    def test_raises_api_error_on_403(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(403, "Forbidden")):
            with pytest.raises(APIError):
                fetch_json("https://example.com/api")

    def test_raises_rate_limit_error_on_429(self):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = 429
        resp.headers = {"Retry-After": "30"}
        resp.raise_for_status.return_value = None  # 429 is checked manually before raise_for_status
        with patch("scrapernhl.core.http.SESSION.get", return_value=resp):
            with pytest.raises(RateLimitError) as exc_info:
                fetch_json("https://example.com/api")
        assert exc_info.value.retry_after == 30

    def test_rate_limit_error_without_retry_after_header(self):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = 429
        resp.headers = {}
        resp.raise_for_status.return_value = None
        with patch("scrapernhl.core.http.SESSION.get", return_value=resp):
            with pytest.raises(RateLimitError) as exc_info:
                fetch_json("https://example.com/api")
        assert exc_info.value.retry_after is None

    def test_rate_limit_error_is_api_error(self):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = 429
        resp.headers = {}
        resp.raise_for_status.return_value = None
        with patch("scrapernhl.core.http.SESSION.get", return_value=resp):
            with pytest.raises(APIError):
                fetch_json("https://example.com/api")

    def test_raises_api_error_on_connection_error(self):
        with patch(
            "scrapernhl.core.http.SESSION.get",
            side_effect=requests.exceptions.ConnectionError("connection refused"),
        ):
            with pytest.raises(APIError):
                fetch_json("https://example.com/api")

    def test_raises_api_error_on_timeout(self):
        with patch(
            "scrapernhl.core.http.SESSION.get",
            side_effect=requests.exceptions.Timeout("timed out"),
        ):
            with pytest.raises(APIError):
                fetch_json("https://example.com/api")

    def test_api_error_is_scraper_error(self):
        """APIError must always be catchable via ScraperNHLError."""
        from scrapernhl.exceptions import ScraperNHLError

        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(500)):
            with pytest.raises(ScraperNHLError):
                fetch_json("https://example.com/api")


# ---------------------------------------------------------------------------
# fetch_html
# ---------------------------------------------------------------------------

class TestFetchHtml:
    def test_returns_html_string_on_200(self):
        html = "<html><body><p>Hello</p></body></html>"
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(200, html)):
            result = fetch_html("https://example.com/page")
        assert result == html

    def test_returns_string_not_none(self):
        html = "<!DOCTYPE html><html></html>"
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(200, html)):
            result = fetch_html("https://example.com/page")
        assert result is not None
        assert isinstance(result, str)

    def test_raises_api_error_on_403(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(403)):
            with pytest.raises(APIError):
                fetch_html("https://example.com/page")

    def test_raises_api_error_on_500(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(500)):
            with pytest.raises(APIError):
                fetch_html("https://example.com/page")

    def test_raises_on_http_error_not_returns_none(self):
        """Regression: fetch_html must raise APIError, never return None."""
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(404)):
            with pytest.raises(APIError):
                fetch_html("https://example.com/missing")

    def test_raises_api_error_on_timeout(self):
        with patch(
            "scrapernhl.core.http.SESSION.get",
            side_effect=requests.exceptions.Timeout("request timeout"),
        ):
            with pytest.raises(APIError):
                fetch_html("https://example.com/page")

    def test_raises_api_error_on_connection_error(self):
        with patch(
            "scrapernhl.core.http.SESSION.get",
            side_effect=requests.exceptions.ConnectionError("refused"),
        ):
            with pytest.raises(APIError):
                fetch_html("https://example.com/page")

    def test_api_error_preserves_status_code_on_http_error(self):
        with patch("scrapernhl.core.http.SESSION.get", return_value=_make_response(503)):
            try:
                fetch_html("https://example.com/page")
            except APIError as e:
                assert e.status_code == 503
