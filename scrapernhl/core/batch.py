"""Advanced batch scraping utilities with parallel processing.

This module provides utilities for efficiently scraping large amounts of data
with features like:
- Parallel/concurrent API requests
- Rate limiting and backoff
- Batch processing with checkpoints
- Error recovery and retry logic
- Progress tracking
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional, Union
from dataclasses import dataclass, field

import pandas as pd
import polars as pl

from scrapernhl.core.progress import console, create_progress_bar
from scrapernhl.core.logging_config import get_logger
from scrapernhl.exceptions import APIError, RateLimitError

LOG = get_logger(__name__)


@dataclass
class BatchResult:
    """Container for batch scraping results.
    
    Attributes:
        successful: List of successful results
        failed: List of failed items with error messages
        duration: Total duration in seconds
        success_rate: Percentage of successful items
    """
    successful: List[Any] = field(default_factory=list)
    failed: List[Dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = len(self.successful) + len(self.failed)
        if total == 0:
            return 0.0
        return (len(self.successful) / total) * 100
    
    @property
    def total_items(self) -> int:
        """Total number of items processed."""
        return len(self.successful) + len(self.failed)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'total_items': self.total_items,
            'successful': len(self.successful),
            'failed': len(self.failed),
            'success_rate': f"{self.success_rate:.1f}%",
            'duration': f"{self.duration:.2f}s",
            'items_per_second': f"{self.total_items / self.duration:.2f}" if self.duration > 0 else "N/A"
        }


class BatchScraper:
    """Advanced batch scraping with parallel processing and rate limiting.
    
    Features:
    - Parallel execution with configurable workers
    - Rate limiting (requests per second)
    - Automatic retry with exponential backoff
    - Progress tracking
    - Error collection and reporting
    
    Examples:
        >>> scraper = BatchScraper(max_workers=5, rate_limit=10)
        >>> result = scraper.scrape_batch(game_ids, fetch_game_data)
        >>> print(f"Success rate: {result.success_rate}%")
    """
    
    def __init__(
        self,
        max_workers: int = 5,
        rate_limit: Optional[float] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        show_progress: bool = True
    ):
        """Initialize batch scraper.
        
        Args:
            max_workers: Maximum number of concurrent workers
            rate_limit: Maximum requests per second (None for unlimited)
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Initial delay between retries (exponential backoff)
            show_progress: Whether to show progress bar
        """
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.show_progress = show_progress
        
        # Rate limiting state
        self._last_request_time = 0.0
        self._min_request_interval = 1.0 / rate_limit if rate_limit else 0.0
        
        LOG.info(f"BatchScraper initialized: workers={max_workers}, "
                f"rate_limit={rate_limit}, retries={max_retries}")
    
    def _rate_limit_wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        if self.rate_limit is None:
            return
        
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            wait_time = self._min_request_interval - elapsed
            time.sleep(wait_time)
        
        self._last_request_time = time.time()
    
    def _execute_with_retry(
        self,
        func: Callable,
        item: Any,
        **kwargs
    ) -> tuple[bool, Any, Optional[str]]:
        """Execute function with retry logic.
        
        Args:
            func: Function to execute
            item: Item to pass to function
            **kwargs: Additional keyword arguments for function
            
        Returns:
            Tuple of (success, result, error_message)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                self._rate_limit_wait()
                result = func(item, **kwargs)
                return True, result, None
                
            except RateLimitError as e:
                last_error = str(e)
                # Respect retry-after header if provided
                wait_time = getattr(e, 'retry_after', self.retry_delay * (2 ** attempt))
                LOG.warning(f"Rate limited on {item}, waiting {wait_time}s")
                time.sleep(wait_time)
                
            except APIError as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    LOG.warning(f"API error on {item}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    LOG.error(f"Failed after {self.max_retries} attempts: {item}")
                    
            except Exception as e:
                last_error = str(e)
                LOG.error(f"Unexpected error on {item}: {e}")
                break
        
        return False, None, last_error
    
    def scrape_batch(
        self,
        items: List[Any],
        func: Callable,
        description: str = "Processing items",
        **kwargs
    ) -> BatchResult:
        """Scrape a batch of items with parallel processing.
        
        Args:
            items: List of items to process
            func: Function to apply to each item
            description: Description for progress bar
            **kwargs: Additional keyword arguments passed to func
            
        Returns:
            BatchResult with successful and failed items
            
        Examples:
            >>> def fetch_game(game_id):
            ...     return getGameData(game_id)
            >>> scraper = BatchScraper(max_workers=10)
            >>> result = scraper.scrape_batch(game_ids, fetch_game)
        """
        result = BatchResult()
        start_time = time.time()
        
        if not items:
            console.print_warning("No items to process")
            return result
        
        console.print_info(f"Starting batch processing of {len(items)} items")
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(self._execute_with_retry, func, item, **kwargs): item
                for item in items
            }
            
            # Process results with progress tracking
            if self.show_progress:
                with create_progress_bar() as progress:
                    task = progress.add_task(
                        f"[cyan]{description}...",
                        total=len(items)
                    )
                    
                    for future in as_completed(future_to_item):
                        item = future_to_item[future]
                        success, data, error = future.result()
                        
                        if success:
                            result.successful.append(data)
                        else:
                            result.failed.append({
                                'item': item,
                                'error': error
                            })
                        
                        progress.update(task, advance=1)
            else:
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    success, data, error = future.result()
                    
                    if success:
                        result.successful.append(data)
                    else:
                        result.failed.append({
                            'item': item,
                            'error': error
                        })
        
        result.duration = time.time() - start_time
        
        # Print summary
        summary = result.summary()
        console.print_success(
            f"Batch complete: {summary['successful']}/{summary['total_items']} "
            f"succeeded ({summary['success_rate']}) in {summary['duration']}"
        )
        
        if result.failed:
            console.print_warning(f"{len(result.failed)} items failed")
            LOG.info(f"Failed items: {[f['item'] for f in result.failed]}")
        
        return result


def scrape_season_games(
    season: Union[str, int],
    team: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    max_workers: int = 5,
    rate_limit: Optional[float] = 10.0
) -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrape all games for a season with parallel processing.
    
    This function:
    1. Gets the schedule for the season/team
    2. Extracts game IDs
    3. Scrapes play-by-play data in parallel
    4. Returns combined DataFrame
    
    Parameters:
    - season: Season ID (e.g., "20232024")
    - team: Optional team abbreviation to filter games
    - start_date: Optional start date filter (YYYY-MM-DD)
    - end_date: Optional end date filter (YYYY-MM-DD)
    - max_workers: Number of parallel workers
    - rate_limit: Maximum requests per second
    
    Returns:
    - Combined DataFrame with all play-by-play data
    
    Examples:
        >>> # Scrape all Maple Leafs games from 2023-24 season
        >>> plays = scrape_season_games("20232024", team="TOR", max_workers=10)
        >>> print(f"Scraped {len(plays)} plays from {plays['gameId'].nunique()} games")
    """
    from scrapernhl.scrapers.schedule import getScheduleData
    from scrapernhl.scrapers.games import getGameData
    
    console.print_info(f"Fetching schedule for season {season}...")
    
    # Get schedule
    if team:
        schedule_data = getScheduleData(team, season)
    else:
        # Would need to implement league-wide schedule scraper
        raise NotImplementedError("League-wide schedule scraping not yet implemented")
    
    # Extract game IDs
    game_ids = []
    for game in schedule_data:
        game_id = game.get('id')
        game_date = game.get('gameDate', '')
        
        # Apply date filters
        if start_date and game_date < start_date:
            continue
        if end_date and game_date > end_date:
            continue
        
        if game_id:
            game_ids.append(game_id)
    
    console.print_info(f"Found {len(game_ids)} games to scrape")
    
    if not game_ids:
        console.print_warning("No games found matching criteria")
        return pd.DataFrame()
    
    # Scrape games in parallel
    scraper = BatchScraper(
        max_workers=max_workers,
        rate_limit=rate_limit,
        show_progress=True
    )
    
    result = scraper.scrape_batch(
        game_ids,
        getGameData,
        description=f"Scraping {season} games"
    )
    
    # Extract plays from all games
    all_plays = []
    for game_data in result.successful:
        if isinstance(game_data, dict):
            plays = game_data.get('plays', [])
            all_plays.extend(plays)
    
    if not all_plays:
        console.print_warning("No plays found in scraped games")
        return pd.DataFrame()
    
    # Convert to DataFrame
    from scrapernhl.core.utils import json_normalize
    df = json_normalize(all_plays, "pandas")
    
    console.print_success(f"Scraped {len(df)} plays from {len(result.successful)} games")
    
    return df


def scrape_date_range(
    start_date: str,
    end_date: str,
    data_type: str = "schedule",
    max_workers: int = 5
) -> Union[pd.DataFrame, pl.DataFrame]:
    """Scrape data for a date range with parallel processing.
    
    Parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - data_type: Type of data to scrape ("schedule", "standings")
    - max_workers: Number of parallel workers
    
    Returns:
    - Combined DataFrame for all dates
    
    Examples:
        >>> # Get standings for every day in January 2024
        >>> standings = scrape_date_range("2024-01-01", "2024-01-31", "standings")
    """
    # Generate date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    console.print_info(f"Scraping {data_type} for {len(dates)} dates")
    
    # Select appropriate scraper
    if data_type == "standings":
        from scrapernhl.scrapers.standings import getStandingsData
        func = getStandingsData
    else:
        raise NotImplementedError(f"Data type '{data_type}' not supported")
    
    # Scrape in parallel
    scraper = BatchScraper(max_workers=max_workers, show_progress=True)
    result = scraper.scrape_batch(
        dates,
        func,
        description=f"Scraping {data_type}"
    )
    
    # Flatten results
    all_records = []
    for records in result.successful:
        if isinstance(records, list):
            all_records.extend(records)
    
    if not all_records:
        console.print_warning("No records found")
        return pd.DataFrame()
    
    # Convert to DataFrame
    from scrapernhl.core.utils import json_normalize
    df = json_normalize(all_records, "pandas")
    
    console.print_success(f"Scraped {len(df)} records from {len(result.successful)} dates")
    
    return df


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
        
    Examples:
        >>> items = list(range(10))
        >>> chunks = chunk_list(items, 3)
        >>> print(len(chunks))  # 4 chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def scrape_with_checkpoints(
    items: List[Any],
    func: Callable,
    checkpoint_size: int = 100,
    checkpoint_file: Optional[str] = None,
    **kwargs
) -> BatchResult:
    """Scrape items in chunks with checkpointing for recovery.
    
    Useful for very large scraping jobs that may be interrupted.
    
    Parameters:
    - items: List of items to process
    - func: Function to apply to each item
    - checkpoint_size: Number of items per checkpoint
    - checkpoint_file: Optional file to save progress
    - **kwargs: Additional arguments for func
    
    Returns:
    - BatchResult with all results
    
    Examples:
        >>> # Scrape 1000 games with checkpoints every 100
        >>> result = scrape_with_checkpoints(
        ...     game_ids,
        ...     getGameData,
        ...     checkpoint_size=100
        ... )
    """
    chunks = chunk_list(items, checkpoint_size)
    total_result = BatchResult()
    
    console.print_info(f"Processing {len(items)} items in {len(chunks)} chunks")
    
    scraper = BatchScraper(show_progress=False)
    
    with create_progress_bar() as progress:
        task = progress.add_task(
            "[cyan]Processing chunks...",
            total=len(chunks)
        )
        
        for i, chunk in enumerate(chunks, 1):
            console.print_info(f"Processing chunk {i}/{len(chunks)}")
            
            chunk_result = scraper.scrape_batch(
                chunk,
                func,
                description=f"Chunk {i}/{len(chunks)}",
                **kwargs
            )
            
            # Accumulate results
            total_result.successful.extend(chunk_result.successful)
            total_result.failed.extend(chunk_result.failed)
            total_result.duration += chunk_result.duration
            
            progress.update(task, advance=1)
            
            # Optional: Save checkpoint
            if checkpoint_file:
                import json
                with open(checkpoint_file, 'w') as f:
                    json.dump({
                        'completed_chunks': i,
                        'total_chunks': len(chunks),
                        'successful': len(total_result.successful),
                        'failed': len(total_result.failed)
                    }, f)
    
    console.print_success(f"All chunks complete: {total_result.summary()}")
    
    return total_result
