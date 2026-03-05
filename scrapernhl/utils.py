# scrapernhl/utils.py
"""Rate limiting, caching, and HTTP utilities."""

import hashlib
import json
import re
import time
from pathlib import Path
from threading import Lock

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, calls: int = 2, period: float = 1.0):
        self.calls = calls
        self.period = period
        self.timestamps: list[float] = []
        self.lock = Lock()

    def wait(self):
        """Wait if rate limit would be exceeded."""
        with self.lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if now - t < self.period]

            if len(self.timestamps) >= self.calls:
                sleep_time = self.period - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
                    self.timestamps = [t for t in self.timestamps if now - t < self.period]

            self.timestamps.append(now)


# ============================================================================
# Caching (Disk-based)
# ============================================================================

class Cache:
    """Simple disk-based cache with TTL."""

    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path.home() / '.scrapernhl' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        # Hash key to create valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> dict | None:
        """Get cached value if not expired."""
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None

        try:
            with cache_file.open('r') as f:
                entry = json.load(f)

            if time.time() - entry['timestamp'] > entry['ttl']:
                cache_file.unlink()
                return None

            return entry['data']
        except Exception:
            return None

    def set(self, key: str, value: dict, ttl: int):
        """Cache value with TTL."""
        if ttl == 0:  # Don't cache if TTL is 0
            return

        cache_file = self._get_cache_file(key)
        entry = {
            'data': value,
            'timestamp': time.time(),
            'ttl': ttl,
        }

        try:
            with cache_file.open('w') as f:
                json.dump(entry, f)
        except Exception:
            pass  # Silently fail on cache write errors

    def clear(self):
        """Clear all cached files."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception:
                pass


# ============================================================================
# HTTP
# ============================================================================

def get_session() -> requests.Session:
    """Get configured session with retry logic."""
    if not hasattr(get_session, '_session'):
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        get_session._session = session
    return get_session._session


def clean_jsonp(text: str) -> str:
    """Remove JSONP wrappers from HockeyTech responses."""
    text = text.strip()
    text = re.sub(r'^angular\.callbacks\._\d+\(', '', text)
    text = re.sub(r'^[a-zA-Z_][a-zA-Z0-9_]*\(', '', text)
    if text.startswith('('):
        text = text[1:]
    text = re.sub(r'\);?\s*$', '', text)
    return text.strip()


def extract_nested(data: dict | list, keys: list[str]) -> list:
    """Extract data from nested structure."""
    if isinstance(data, list):
        return data

    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, [])
        else:
            return []

    return result if isinstance(result, list) else []


# ============================================================================
# Validation
# ============================================================================

def validate_game_id(game_id: int | str) -> int:
    """
    Validate game ID format.
    """
    if isinstance(game_id, str) and game_id.isdigit():
        game_id = int(game_id)
    if not isinstance(game_id, int) or game_id <= 0:
        raise ValueError(f"Invalid game_id: {game_id}")
    return game_id


def validate_season(season: int | str, league: str) -> int:
    """
    Validate season format.
    """
    if isinstance(season, str) and season.isdigit():
        season = int(season)
    if league == 'nhl':
        if not (20000000 <= season <= 30000000):
            raise ValueError(f"Invalid NHL season: {season}")
    else:
        if not (1 <= season <= 1000):
            raise ValueError(f"Invalid {league.upper()} season: {season}")
    return season

# Add more validation functions as needed

