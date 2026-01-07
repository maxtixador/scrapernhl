"""
exceptions.py : Custom exceptions for the scrapernhl package.

This module defines a hierarchy of exceptions specific to NHL data scraping operations.
All custom exceptions inherit from ScraperNHLError for easy catching.

Example:
    >>> from scrapernhl.exceptions import InvalidGameError
    >>> try:
    ...     data = scrape_game(123)  # Invalid ID
    ... except InvalidGameError as e:
    ...     print(f"Error: {e}")
"""

from typing import Optional


class ScraperNHLError(Exception):
    """
    Base exception for all scrapernhl package errors.
    
    All custom exceptions in this package inherit from this class,
    allowing users to catch all package-specific errors with a single except clause.
    
    Example:
        >>> try:
        ...     # Any scrapernhl operation
        ...     data = scrape_game(game_id)
        ... except ScraperNHLError as e:
        ...     print(f"ScraperNHL error: {e}")
    """
    pass


class APIError(ScraperNHLError):
    """
    NHL API returned an error or unexpected response.
    
    Raised when:
    - API request fails (timeout, connection error)
    - API returns non-200 status code
    - API response format is unexpected
    
    Attributes:
        status_code: HTTP status code if available
        response_text: Raw response text if available
    
    Example:
        >>> try:
        ...     data = fetch_json(url)
        ... except APIError as e:
        ...     if e.status_code == 503:
        ...         print("NHL API is down, retry later")
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class InvalidGameError(ScraperNHLError):
    """
    Invalid game ID or game not found.
    
    Raised when:
    - Game ID format is invalid (e.g., too short, wrong format)
    - Game ID is valid but game doesn't exist (404)
    - Game data is incomplete or corrupted
    
    Example:
        >>> try:
        ...     data = scrape_game(123)  # Too short
        ... except InvalidGameError as e:
        ...     print(f"Invalid game: {e}")
    """
    pass


class InvalidTeamError(ScraperNHLError):
    """
    Invalid team abbreviation or team not found.
    
    Raised when:
    - Team abbreviation is not recognized
    - Team ID is invalid
    
    Example:
        >>> try:
        ...     schedule = scrapeSchedule("XXX", "20252026")
        ... except InvalidTeamError as e:
        ...     print(f"Invalid team: {e}")
    """
    pass


class InvalidSeasonError(ScraperNHLError):
    """
    Invalid season format or season not available.
    
    Raised when:
    - Season format is incorrect (should be "YYYYYYYY")
    - Season is too old or not yet available
    
    Example:
        >>> try:
        ...     schedule = scrapeSchedule("MTL", "2025")  # Wrong format
        ... except InvalidSeasonError as e:
        ...     print(f"Invalid season: {e}")
    """
    pass


class DataValidationError(ScraperNHLError):
    """
    Data failed validation checks.
    
    Raised when:
    - Required columns are missing
    - Data types are incorrect
    - Data values are outside expected ranges
    - Data quality metrics below threshold
    
    Attributes:
        missing_columns: List of missing required columns
        invalid_dtypes: Dict of columns with wrong data types
        validation_errors: List of specific validation errors
    
    Example:
        >>> try:
        ...     df = standardize_columns(df, "teams", strict=True)
        ... except DataValidationError as e:
        ...     print(f"Missing columns: {e.missing_columns}")
    """
    
    def __init__(
        self,
        message: str,
        missing_columns: Optional[list] = None,
        invalid_dtypes: Optional[dict] = None,
        validation_errors: Optional[list] = None
    ):
        super().__init__(message)
        self.missing_columns = missing_columns or []
        self.invalid_dtypes = invalid_dtypes or {}
        self.validation_errors = validation_errors or []


class CacheError(ScraperNHLError):
    """
    Error reading from or writing to cache.
    
    Raised when:
    - Cache directory is not accessible
    - Cached data is corrupted
    - Cache write fails due to permissions or disk space
    
    Example:
        >>> try:
        ...     data = load_from_cache(key)
        ... except CacheError as e:
        ...     print(f"Cache error: {e}, fetching fresh data")
    """
    pass


class ParsingError(ScraperNHLError):
    """
    Error parsing HTML or JSON data.
    
    Raised when:
    - HTML structure has changed
    - JSON format is unexpected
    - Required fields are missing in response
    
    Example:
        >>> try:
        ...     df = parse_html_roster(html)
        ... except ParsingError as e:
        ...     print(f"HTML parsing failed: {e}")
    """
    pass


class RateLimitError(APIError):
    """
    Rate limit exceeded for NHL API.
    
    Raised when API returns 429 Too Many Requests.
    Users should implement backoff and retry logic.
    
    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API)
    
    Example:
        >>> import time
        >>> try:
        ...     data = fetch_json(url)
        ... except RateLimitError as e:
        ...     if e.retry_after:
        ...         time.sleep(e.retry_after)
        ...         data = fetch_json(url)  # Retry
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
