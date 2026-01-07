"""
logging_config.py : Centralized logging configuration for scrapernhl.

This module provides consistent logging configuration across the package,
with structured formatting and proper log levels for different components.

Example:
    >>> from scrapernhl.core.logging_config import get_logger
    >>> 
    >>> LOG = get_logger(__name__)
    >>> LOG.info("Scraping game %d", game_id)
    >>> LOG.warning("Missing coordinate data for event %d", event_id)
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# Default log format with timestamp, level, module, and message
DEFAULT_FORMAT = "[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s"
SIMPLE_FORMAT = "%(levelname)-8s %(message)s"
DETAILED_FORMAT = "[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s"

# Default date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels for terminal output.
    
    Uses ANSI color codes for different log levels:
    - DEBUG: Cyan
    - INFO: Green
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Bold Red
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[1;31m", # Bold Red
        "RESET": "\033[0m",       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Reset levelname to original (for subsequent handlers)
        record.levelname = levelname
        
        return formatted


def setup_logging(
    level: str = "INFO",
    format_style: str = "default",
    log_file: Optional[Path] = None,
    colored: bool = True
) -> None:
    """
    Configure logging for the entire scrapernhl package.
    
    This function should be called once at package initialization or
    at the start of a script to configure logging behavior.
    
    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        format_style: Format style ("default", "simple", "detailed")
        log_file: Optional path to write logs to file
        colored: Whether to use colored output for console (default True)
    
    Example:
        >>> # Basic setup with INFO level
        >>> setup_logging(level="INFO")
        >>> 
        >>> # Debug mode with detailed format
        >>> setup_logging(level="DEBUG", format_style="detailed")
        >>> 
        >>> # Log to file
        >>> setup_logging(log_file=Path("scraper.log"))
    """
    # Get root logger for scrapernhl
    logger = logging.getLogger("scrapernhl")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Choose format
    if format_style == "simple":
        log_format = SIMPLE_FORMAT
    elif format_style == "detailed":
        log_format = DETAILED_FORMAT
    else:
        log_format = DEFAULT_FORMAT
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if colored and sys.stdout.isatty():
        # Use colored formatter for terminal
        console_formatter = ColoredFormatter(log_format, datefmt=DATE_FORMAT)
    else:
        # Use plain formatter for non-terminal or when colors disabled
        console_formatter = logging.Formatter(log_format, datefmt=DATE_FORMAT)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        
        # File logs don't need colors
        file_formatter = logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    This is the recommended way to get loggers in scrapernhl modules.
    All loggers are children of the 'scrapernhl' logger.
    
    Args:
        name: Module name (typically __name__)
    
    Returns:
        Logger instance configured with package settings
    
    Example:
        >>> # In scrapernhl/scrapers/teams.py
        >>> LOG = get_logger(__name__)
        >>> 
        >>> def scrapeTeams():
        ...     LOG.info("Fetching teams data")
        ...     # ...
        ...     LOG.debug("Received %d teams", len(teams))
    """
    # Ensure the name is under scrapernhl namespace
    if not name.startswith("scrapernhl"):
        name = f"scrapernhl.{name}"
    
    return logging.getLogger(name)


def log_function_call(func_name: str, **kwargs) -> None:
    """
    Log a function call with parameters (for debugging).
    
    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    
    Example:
        >>> LOG = get_logger(__name__)
        >>> 
        >>> def scrape_game(game_id, include_shifts=False):
        ...     LOG.debug("Function call: %s", 
        ...               {"game_id": game_id, "include_shifts": include_shifts})
    """
    logger = get_logger("scrapernhl.calls")
    
    # Format parameters
    params = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    logger.debug(f"{func_name}({params})")


def log_api_request(url: str, method: str = "GET", status_code: Optional[int] = None) -> None:
    """
    Log an API request (useful for debugging rate limits and failures).
    
    Args:
        url: The API URL being called
        method: HTTP method (GET, POST, etc.)
        status_code: Response status code (if available)
    
    Example:
        >>> LOG = get_logger(__name__)
        >>> 
        >>> def fetch_json(url):
        ...     log_api_request(url, "GET")
        ...     response = requests.get(url)
        ...     log_api_request(url, "GET", response.status_code)
    """
    logger = get_logger("scrapernhl.api")
    
    if status_code:
        if status_code >= 400:
            logger.warning(f"{method} {url} - Status: {status_code}")
        else:
            logger.debug(f"{method} {url} - Status: {status_code}")
    else:
        logger.debug(f"{method} {url}")


def log_scraping_progress(
    operation: str,
    current: int,
    total: int,
    item_name: str = "items"
) -> None:
    """
    Log scraping progress (alternative to progress bars for non-interactive mode).
    
    Args:
        operation: Description of operation (e.g., "Scraping games")
        current: Current item number
        total: Total number of items
        item_name: Name of items being processed
    
    Example:
        >>> LOG = get_logger(__name__)
        >>> 
        >>> for i, game_id in enumerate(game_ids, 1):
        ...     log_scraping_progress("Scraping games", i, len(game_ids), "games")
        ...     data = scrape_game(game_id)
    """
    logger = get_logger("scrapernhl.progress")
    
    percentage = (current / total) * 100 if total > 0 else 0
    logger.info(f"{operation}: {current}/{total} {item_name} ({percentage:.1f}%)")


# Initialize default logging on module import
# Users can override with setup_logging()
setup_logging(level="WARNING", format_style="default", colored=True)
