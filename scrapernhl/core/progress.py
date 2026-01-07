"""Progress tracking and styled output using Rich library.

This module provides utilities for displaying progress bars, styled console output,
and formatted tables using the Rich library. It integrates with the logging system
to provide consistent, visually appealing output for scraping operations.

Examples:
    Basic progress bar usage:
    
    >>> from scrapernhl.core.progress import create_progress_bar
    >>> with create_progress_bar() as progress:
    ...     task = progress.add_task("Scraping games...", total=100)
    ...     for i in range(100):
    ...         # Do work
    ...         progress.update(task, advance=1)
    
    Using the console wrapper:
    
    >>> from scrapernhl.core.progress import console
    >>> console.print("[bold green]Success![/bold green]")
    >>> console.print_error("An error occurred")
    >>> console.print_warning("Warning message")
    
    Creating formatted tables:
    
    >>> from scrapernhl.core.progress import create_table
    >>> table = create_table("Team Statistics", ["Team", "Wins", "Losses"])
    >>> table.add_row("Maple Leafs", "45", "20")
    >>> console.print(table)

Author: ScraperNHL Team
Version: 0.1.4
"""

from contextlib import contextmanager
from typing import Optional, Any, Dict, List, Union
import sys

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeRemainingColumn,
        TimeElapsedColumn,
        MofNCompleteColumn,
    )
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich import box
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Define dummy classes when Rich is not available
    Progress = None  # type: ignore

from scrapernhl.core.logging_config import get_logger

LOG = get_logger(__name__)


class ConsoleWrapper:
    """Wrapper for Rich Console with fallback to standard print.
    
    Provides a consistent interface for styled output that gracefully degrades
    when Rich is not available. All output methods work whether Rich is installed
    or not, ensuring the library functions in all environments.
    
    Attributes:
        console: Rich Console instance if available, None otherwise
        use_rich: Boolean indicating whether Rich is available
    
    Examples:
        >>> console = ConsoleWrapper()
        >>> console.print("[bold]Hello[/bold]")  # Styled if Rich available
        >>> console.print_success("Operation completed")
        >>> console.print_error("Something went wrong")
    """
    
    def __init__(self, force_terminal: Optional[bool] = None):
        """Initialize console wrapper.
        
        Args:
            force_terminal: Force terminal mode. If None, auto-detect.
        """
        self.use_rich = RICH_AVAILABLE
        if self.use_rich:
            self.console = Console(force_terminal=force_terminal)
        else:
            self.console = None
            LOG.debug("Rich not available, using fallback print")
    
    def print(self, *args, **kwargs) -> None:
        """Print with Rich styling if available, fallback to standard print.
        
        Args:
            *args: Positional arguments to print
            **kwargs: Keyword arguments (style, highlight, etc.)
        """
        if self.use_rich:
            self.console.print(*args, **kwargs)
        else:
            # Strip Rich markup for plain output
            text = " ".join(str(arg) for arg in args)
            # Simple markup removal (basic)
            import re
            text = re.sub(r'\[.*?\]', '', text)
            print(text, **{k: v for k, v in kwargs.items() if k in ['file', 'end', 'flush']})
    
    def print_success(self, message: str) -> None:
        """Print success message in green.
        
        Args:
            message: Success message to display
        """
        if self.use_rich:
            self.console.print(f"✓ {message}", style="bold green")
        else:
            print(f"✓ {message}")
    
    def print_error(self, message: str) -> None:
        """Print error message in red.
        
        Args:
            message: Error message to display
        """
        if self.use_rich:
            self.console.print(f"✗ {message}", style="bold red")
        else:
            print(f"✗ {message}", file=sys.stderr)
    
    def print_warning(self, message: str) -> None:
        """Print warning message in yellow.
        
        Args:
            message: Warning message to display
        """
        if self.use_rich:
            self.console.print(f"⚠ {message}", style="bold yellow")
        else:
            print(f"⚠ {message}")
    
    def print_info(self, message: str) -> None:
        """Print info message in blue.
        
        Args:
            message: Info message to display
        """
        if self.use_rich:
            self.console.print(f"ℹ {message}", style="bold blue")
        else:
            print(f"ℹ {message}")
    
    def rule(self, title: str = "", **kwargs) -> None:
        """Print a horizontal rule with optional title.
        
        Args:
            title: Optional title for the rule
            **kwargs: Additional arguments for Rich rule
        """
        if self.use_rich:
            self.console.rule(title, **kwargs)
        else:
            print(f"\n{'=' * 80}")
            if title:
                print(f" {title} ".center(80, '='))
            print(f"{'=' * 80}\n")
    
    def status(self, message: str):
        """Create a status context manager (spinner).
        
        Args:
            message: Status message to display
            
        Returns:
            Context manager for status display
        """
        if self.use_rich:
            return self.console.status(message)
        else:
            # Simple fallback
            @contextmanager
            def _fallback_status():
                print(f"{message}...")
                yield
                print(f"{message}... done")
            return _fallback_status()


# Global console instance
console = ConsoleWrapper()


def create_progress_bar(
    transient: bool = False,
    show_percentage: bool = True,
    show_time: bool = True,
) -> Union['Progress', '_DummyProgress']:
    """Create a Rich progress bar with standard configuration.
    
    Args:
        transient: If True, remove progress bar after completion
        show_percentage: Show percentage complete
        show_time: Show time remaining and elapsed
    
    Returns:
        Configured Progress instance or _DummyProgress if Rich not available
        
    Examples:
        >>> with create_progress_bar() as progress:
        ...     task = progress.add_task("Processing", total=100)
        ...     for i in range(100):
        ...         progress.update(task, advance=1)
    """
    if not RICH_AVAILABLE:
        LOG.warning("Rich not available, progress bars disabled")
        return _DummyProgress()
    
    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
    ]
    
    if show_percentage:
        columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))
    
    if show_time:
        columns.extend([
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        ])
    
    return Progress(*columns, transient=transient)


def create_table(
    data: Any = None,
    title: str = "",
    columns: List[str] = None,
    show_header: bool = True,
    show_lines: bool = False,
    box_style: Any = None,
) -> Any:
    """Create a formatted table from data or column headers.
    
    Args:
        data: Optional pandas DataFrame to populate the table
        title: Table title
        columns: List of column headers (required if data is None)
        show_header: Show column headers
        show_lines: Show lines between rows
        box_style: Box style (default: ROUNDED)
    
    Returns:
        Rich Table instance or None if Rich not available
        
    Examples:
        >>> # From DataFrame
        >>> import pandas as pd
        >>> df = pd.DataFrame({"Name": ["Alice", "Bob"], "Score": [95, 87]})
        >>> table = create_table(df, title="Results")
        >>> console.print(table)
        
        >>> # Manual construction
        >>> table = create_table(title="Results", columns=["Name", "Score"])
        >>> table.add_row("Alice", "95")
        >>> table.add_row("Bob", "87")
        >>> console.print(table)
    """
    if not RICH_AVAILABLE:
        LOG.warning("Rich not available, tables not supported")
        return None
    
    if box_style is None:
        box_style = box.ROUNDED
    
    # If data is a DataFrame, extract columns and populate automatically
    if data is not None:
        try:
            # Check if it's a pandas DataFrame
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                columns = list(data.columns)
                
                table = Table(
                    title=title,
                    show_header=show_header,
                    show_lines=show_lines,
                    box=box_style,
                )
                
                for col in columns:
                    table.add_column(str(col), style="cyan", no_wrap=False)
                
                # Add rows from DataFrame
                for _, row in data.iterrows():
                    table.add_row(*[str(val) for val in row])
                
                return table
        except ImportError:
            LOG.warning("pandas not available, cannot create table from DataFrame")
            return None
    
    # Manual table construction
    if columns is None:
        raise ValueError("Either 'data' or 'columns' must be provided")
    
    table = Table(
        title=title,
        show_header=show_header,
        show_lines=show_lines,
        box=box_style,
    )
    
    for col in columns:
        table.add_column(col, style="cyan", no_wrap=False)
    
    return table


def create_panel(
    content: str,
    title: str = "",
    border_style: str = "blue",
) -> Any:
    """Create a styled panel.
    
    Args:
        content: Panel content
        title: Panel title
        border_style: Border color/style
    
    Returns:
        Rich Panel instance or None if Rich not available
        
    Examples:
        >>> panel = create_panel("Important info", title="Notice")
        >>> console.print(panel)
    """
    if not RICH_AVAILABLE:
        LOG.warning("Rich not available, panels not supported")
        return None
    
    return Panel(content, title=title, border_style=border_style)


def create_tree(label: str) -> Any:
    """Create a tree structure for hierarchical data.
    
    Args:
        label: Root node label
    
    Returns:
        Rich Tree instance or None if Rich not available
        
    Examples:
        >>> tree = create_tree("Teams")
        >>> atlantic = tree.add("Atlantic Division")
        >>> atlantic.add("Toronto Maple Leafs")
        >>> atlantic.add("Boston Bruins")
        >>> console.print(tree)
    """
    if not RICH_AVAILABLE:
        LOG.warning("Rich not available, trees not supported")
        return None
    
    return Tree(label)


class _DummyProgress:
    """Dummy progress bar for when Rich is not available.
    
    Provides the same interface as Rich Progress but does nothing,
    allowing code to work without modification when Rich is not installed.
    """
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def add_task(self, description: str, total: Optional[float] = None, **kwargs) -> int:
        """Add a dummy task."""
        return 0
    
    def update(self, task_id: int, **kwargs) -> None:
        """Update dummy task (no-op)."""
        pass
    
    def start(self) -> None:
        """Start dummy progress (no-op)."""
        pass
    
    def stop(self) -> None:
        """Stop dummy progress (no-op)."""
        pass


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
        
    Examples:
        >>> format_duration(65)
        '1m 5s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


def print_summary(
    title: str,
    data: Dict[str, Any],
    style: str = "blue",
) -> None:
    """Print a formatted summary of key-value pairs.
    
    Args:
        title: Summary title
        data: Dictionary of key-value pairs to display
        style: Border style color
        
    Examples:
        >>> print_summary("Scraping Results", {
        ...     "Games scraped": 82,
        ...     "Duration": "2m 34s",
        ...     "Success rate": "100%"
        ... })
    """
    if not RICH_AVAILABLE:
        print(f"\n{title}")
        print("=" * len(title))
        for key, value in data.items():
            print(f"{key}: {value}")
        print()
        return
    
    lines = [f"[bold]{key}:[/bold] {value}" for key, value in data.items()]
    content = "\n".join(lines)
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)
