"""http.py : HTTP utilities for fetching NHL data with retry logic and session management."""

import asyncio
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scrapernhl.core.logging_config import get_logger, log_api_request
from scrapernhl.exceptions import APIError, RateLimitError

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}
DEFAULT_TIMEOUT = 10  # seconds

# Setup logging
LOG = get_logger(__name__)



# Retry configuration
_RETRY_CONFIG = Retry(
    total=5,
    backoff_factor=0.3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)


def _get_session() -> requests.Session:
    """Create and configure a requests session with retry logic."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=_RETRY_CONFIG, pool_connections=50, pool_maxsize=50)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# Global session for sync usage
SESSION = _get_session()


def fetch_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Fetch JSON data from a URL with retry logic.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON response

    Raises:
        APIError: If request fails
        RateLimitError: If rate limit is exceeded
    """
    try:
        log_api_request(url, "GET")
        resp = SESSION.get(url, headers=DEFAULT_HEADERS, timeout=timeout)

        # Check for rate limiting
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            log_api_request(url, "GET", resp.status_code)
            raise RateLimitError(
                f"Rate limit exceeded for {url}",
                retry_after=retry_seconds
            )

        resp.raise_for_status()
        log_api_request(url, "GET", resp.status_code)
        return resp.json()

    except RateLimitError:
        raise  # Re-raise rate limit errors

    except requests.exceptions.HTTPError as e:
        LOG.error(f"HTTP error fetching {url}: {e}")
        raise APIError(
            f"HTTP error: {e}",
            status_code=e.response.status_code if e.response else None
        ) from e

    except requests.exceptions.RequestException as e:
        LOG.error(f"Request failed for {url}: {e}")
        raise APIError(f"Request failed: {e}") from e

    except Exception as e:
        LOG.error(f"Unexpected error fetching {url}: {e}")
        raise APIError(f"Unexpected error: {e}") from e


def fetch_raw(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Fetch the raw HTTP response body from a URL with the same retry logic as fetch_json.

    Returns a bronze-layer record containing the unmodified wire payload and
    request metadata, suitable for storage in a source-of-truth (bronze) database
    before any parsing or transformation is applied.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        dict with keys:
            url (str): The source URL
            raw_text (str): Unmodified HTTP response body (JSON, JSONP, or HTML)
            scraped_at (str): ISO-8601 UTC timestamp
            content_type (str): Content-Type response header
            status_code (int): HTTP status code

    Raises:
        APIError: If the request fails
        RateLimitError: If rate limit is exceeded
    """
    try:
        log_api_request(url, "GET")
        resp = SESSION.get(url, headers=DEFAULT_HEADERS, timeout=timeout)

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            log_api_request(url, "GET", resp.status_code)
            raise RateLimitError(
                f"Rate limit exceeded for {url}",
                retry_after=retry_seconds,
            )

        resp.raise_for_status()
        log_api_request(url, "GET", resp.status_code)

        return {
            "url": url,
            "raw_text": resp.text,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "content_type": resp.headers.get("Content-Type", ""),
            "status_code": resp.status_code,
        }

    except RateLimitError:
        raise

    except requests.exceptions.HTTPError as e:
        LOG.error(f"HTTP error fetching {url}: {e}")
        raise APIError(
            f"HTTP error: {e}",
            status_code=e.response.status_code if e.response else None,
        ) from e

    except requests.exceptions.RequestException as e:
        LOG.error(f"Request failed for {url}: {e}")
        raise APIError(f"Request failed: {e}") from e

    except Exception as e:
        LOG.error(f"Unexpected error fetching {url}: {e}")
        raise APIError(f"Unexpected error: {e}") from e


def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Fetch HTML content from a URL with retry logic.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        APIError: If the request fails
    """
    try:
        resp = SESSION.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.HTTPError as e:
        LOG.error(f"HTTP error fetching HTML from {url}: {e}")
        raise APIError(
            f"HTTP error: {e}",
            status_code=e.response.status_code if e.response else None,
        ) from e
    except requests.exceptions.RequestException as e:
        LOG.error(f"Failed to fetch HTML from {url}: {e}")
        raise APIError(f"Request failed: {e}") from e
    except Exception as e:
        LOG.error(f"Unexpected error fetching HTML from {url}: {e}")
        raise APIError(f"Unexpected error: {e}") from e


async def fetch_html_async(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Async wrapper around fetch_html using a background thread.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        APIError: If the request fails
    """
    return await asyncio.to_thread(fetch_html, url, timeout)


async def fetch_json_async(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Async wrapper around fetch_json using a background thread.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON response

    Raises:
        requests.exceptions.RequestException: If request fails
    """
    return await asyncio.to_thread(fetch_json, url, timeout)
