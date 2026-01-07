"""http.py : HTTP utilities for fetching NHL data with retry logic and session management."""

import asyncio
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scrapernhl.config import DEFAULT_HEADERS, DEFAULT_TIMEOUT
from scrapernhl.core.logging_config import get_logger, log_api_request
from scrapernhl.exceptions import APIError, RateLimitError

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


def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Fetch HTML content from a URL with retry logic.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content as string, or None if request fails
    """
    try:
        resp = SESSION.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        LOG.warning(f"Failed to fetch HTML from {url}: {e}")
        return None
    except Exception as e:
        LOG.error(f"Unexpected error fetching {url}: {e}")
        return None


async def fetch_html_async(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Async wrapper around fetch_html using a background thread.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content as string, or None if request fails
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