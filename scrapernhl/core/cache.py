"""File-based caching system with TTL support.

This module provides a simple file-based caching system for API responses and
computed data. Caches are stored as JSON files with timestamps, allowing for
time-to-live (TTL) based expiration. The system is designed to reduce API calls
and improve performance for frequently accessed data.

Features:
    - File-based storage (JSON format)
    - TTL (time-to-live) support
    - Automatic cache invalidation
    - Type-safe get/set operations
    - Cache statistics and management

Examples:
    Basic cache usage:
    
    >>> from scrapernhl.core.cache import Cache
    >>> cache = Cache()
    >>> cache.set("teams", teams_data, ttl=3600)  # Cache for 1 hour
    >>> teams = cache.get("teams")
    
    Using the cached decorator:
    
    >>> from scrapernhl.core.cache import cached
    >>> @cached(ttl=3600, cache_key_func=lambda season: f"schedule_{season}")
    ... def getSchedule(season: int):
    ...     # Expensive API call
    ...     return fetch_schedule(season)
    
    Cache management:
    
    >>> cache.clear()  # Clear all cache
    >>> cache.invalidate("teams")  # Remove specific key
    >>> cache.cleanup()  # Remove expired entries
    >>> stats = cache.stats()  # Get cache statistics

Author: ScraperNHL Team
Version: 0.1.4
"""

import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Optional, Callable, Dict, List
from datetime import datetime, timedelta

from scrapernhl.core.logging_config import get_logger
from scrapernhl.exceptions import CacheError

LOG = get_logger(__name__)

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".scrapernhl" / "cache"


class CacheEntry:
    """Represents a single cache entry with metadata.
    
    Attributes:
        key: Cache key
        data: Cached data
        timestamp: Unix timestamp when cached
        ttl: Time to live in seconds
    """
    
    def __init__(self, key: str, data: Any, timestamp: float, ttl: Optional[int] = None):
        """Initialize cache entry.
        
        Args:
            key: Cache key
            data: Data to cache
            timestamp: Unix timestamp
            ttl: Time to live in seconds (None for no expiration)
        """
        self.key = key
        self.data = data
        self.timestamp = timestamp
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.ttl is None:
            return False
        return (time.time() - self.timestamp) > self.ttl
    
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds.
        
        Returns:
            Age in seconds
        """
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "key": self.key,
            "data": self.data,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create CacheEntry from dictionary.
        
        Args:
            data: Dictionary with cache entry data
            
        Returns:
            CacheEntry instance
        """
        return cls(
            key=data["key"],
            data=data["data"],
            timestamp=data["timestamp"],
            ttl=data.get("ttl"),
        )


class Cache:
    """File-based cache manager with TTL support.
    
    Provides a simple interface for caching data to disk with automatic
    expiration based on time-to-live (TTL) settings. Cache entries are
    stored as individual JSON files in the cache directory.
    
    Attributes:
        cache_dir: Path to cache directory
        enabled: Whether caching is enabled
    
    Examples:
        >>> cache = Cache()
        >>> cache.set("my_key", {"data": "value"}, ttl=3600)
        >>> data = cache.get("my_key")
        >>> cache.invalidate("my_key")
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, enabled: bool = True):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files (default: ~/.scrapernhl/cache)
            enabled: Enable/disable caching
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.enabled = enabled
        
        if self.enabled:
            self._ensure_cache_dir()
            LOG.debug(f"Cache initialized at {self.cache_dir}")
    
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            LOG.error(f"Failed to create cache directory: {e}")
            self.enabled = False
            raise CacheError(f"Failed to create cache directory: {e}")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cache file
        """
        # Sanitize key for filename
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found or expired
            
        Returns:
            Cached value or default
        """
        if not self.enabled:
            return default
        
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            LOG.debug(f"Cache miss: {key}")
            return default
        
        try:
            with open(cache_path, "r") as f:
                entry_dict = json.load(f)
                entry = CacheEntry.from_dict(entry_dict)
            
            if entry.is_expired():
                LOG.debug(f"Cache expired: {key}")
                self.invalidate(key)
                return default
            
            LOG.debug(f"Cache hit: {key} (age: {entry.age_seconds():.1f}s)")
            return entry.data
            
        except (json.JSONDecodeError, KeyError, OSError) as e:
            LOG.warning(f"Failed to read cache for {key}: {e}")
            self.invalidate(key)
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
        """
        if not self.enabled:
            return
        
        cache_path = self._get_cache_path(key)
        entry = CacheEntry(key=key, data=value, timestamp=time.time(), ttl=ttl)
        
        try:
            with open(cache_path, "w") as f:
                json.dump(entry.to_dict(), f, indent=2, default=str)
            
            ttl_msg = f"ttl={ttl}s" if ttl else "no expiration"
            LOG.debug(f"Cached: {key} ({ttl_msg})")
            
        except (OSError, TypeError) as e:
            LOG.error(f"Failed to write cache for {key}: {e}")
            raise CacheError(f"Failed to write cache: {e}")
    
    def invalidate(self, key: str) -> bool:
        """Remove key from cache.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if removed, False if not found
        """
        if not self.enabled:
            return False
        
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            try:
                cache_path.unlink()
                LOG.debug(f"Invalidated cache: {key}")
                return True
            except OSError as e:
                LOG.error(f"Failed to invalidate cache for {key}: {e}")
                return False
        
        return False
    
    def clear(self) -> int:
        """Clear all cache entries.
        
        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0
        
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            LOG.info(f"Cleared {count} cache entries")
        except OSError as e:
            LOG.error(f"Failed to clear cache: {e}")
        
        return count
    
    def cleanup(self) -> int:
        """Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0
        
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        entry_dict = json.load(f)
                        entry = CacheEntry.from_dict(entry_dict)
                    
                    if entry.is_expired():
                        cache_file.unlink()
                        count += 1
                        LOG.debug(f"Cleaned up expired cache: {entry.key}")
                        
                except (json.JSONDecodeError, KeyError, OSError):
                    # Remove corrupted cache files
                    cache_file.unlink()
                    count += 1
            
            if count > 0:
                LOG.info(f"Cleaned up {count} expired/corrupted cache entries")
                
        except OSError as e:
            LOG.error(f"Failed to cleanup cache: {e}")
        
        return count
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled:
            return {"enabled": False}
        
        total = 0
        expired = 0
        total_size = 0
        oldest_age = 0.0
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                total += 1
                total_size += cache_file.stat().st_size
                
                try:
                    with open(cache_file, "r") as f:
                        entry_dict = json.load(f)
                        entry = CacheEntry.from_dict(entry_dict)
                    
                    if entry.is_expired():
                        expired += 1
                    
                    age = entry.age_seconds()
                    if age > oldest_age:
                        oldest_age = age
                        
                except (json.JSONDecodeError, KeyError, OSError):
                    expired += 1
                    
        except OSError as e:
            LOG.error(f"Failed to get cache stats: {e}")
        
        return {
            "enabled": True,
            "directory": str(self.cache_dir),
            "total_entries": total,
            "expired_entries": expired,
            "valid_entries": total - expired,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_age_seconds": oldest_age,
        }
    
    def list_keys(self) -> List[str]:
        """List all cache keys.
        
        Returns:
            List of cache keys
        """
        if not self.enabled:
            return []
        
        keys = []
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        entry_dict = json.load(f)
                        keys.append(entry_dict["key"])
                except (json.JSONDecodeError, KeyError, OSError):
                    pass
        except OSError as e:
            LOG.error(f"Failed to list cache keys: {e}")
        
        return sorted(keys)


# Global cache instance
_global_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get global cache instance.
    
    Returns:
        Global Cache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = Cache()
    return _global_cache


def cached(
    ttl: Optional[int] = None,
    cache_key_func: Optional[Callable[..., str]] = None,
    cache_instance: Optional[Cache] = None,
):
    """Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        cache_key_func: Function to generate cache key from args
        cache_instance: Cache instance to use (default: global cache)
        
    Returns:
        Decorator function
        
    Examples:
        >>> @cached(ttl=3600)
        ... def expensive_function(arg1, arg2):
        ...     return compute_result(arg1, arg2)
        
        >>> @cached(ttl=1800, cache_key_func=lambda season: f"schedule_{season}")
        ... def getSchedule(season: int):
        ...     return fetch_schedule_from_api(season)
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or get_cache()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Default: use function name and str representation of args
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{func.__name__}_{args_str}_{kwargs_str}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                LOG.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return result
            
            # Call function and cache result
            LOG.debug(f"Cache miss for {func.__name__}: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Add cache management methods to wrapper
        wrapper.cache = cache
        wrapper.invalidate_cache = lambda *args, **kwargs: cache.invalidate(
            cache_key_func(*args, **kwargs) if cache_key_func else f"{func.__name__}"
        )
        
        return wrapper
    
    return decorator
