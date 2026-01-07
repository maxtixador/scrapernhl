# ScraperNHL Coding Standards

This document defines coding standards and best practices for the ScraperNHL project. Following these guidelines ensures consistency, maintainability, and quality across the codebase.

## Table of Contents

1. [Python Version & Compatibility](#python-version--compatibility)
2. [Code Style](#code-style)
3. [Naming Conventions](#naming-conventions)
4. [Type Hints](#type-hints)
5. [Documentation](#documentation)
6. [Error Handling](#error-handling)
7. [Testing](#testing)
8. [Git Workflow](#git-workflow)
9. [Column Naming Standards](#column-naming-standards)

---

## Python Version & Compatibility

- **Minimum version**: Python 3.9
- **Target versions**: 3.9, 3.10, 3.11, 3.12, 3.13
- Avoid Python 3.12+ only features (e.g., new type syntax) for broader compatibility
- Use `from __future__ import annotations` for forward compatibility

```python
from __future__ import annotations
from typing import Optional, Union
```

---

## Code Style

### General Style: PEP 8

Follow [PEP 8](https://pep8.org/) - the official Python style guide.

**Key Points:**
- **Line length**: 100 characters (slightly more than PEP 8's 79 for readability)
- **Indentation**: 4 spaces (no tabs)
- **Blank lines**: 
  - 2 blank lines between top-level functions/classes
  - 1 blank line between methods in a class
- **Imports**: Group in order (stdlib, third-party, local), alphabetically

### Formatting Tools

We use **Ruff** for linting and formatting (modern, fast alternative to Black + Flake8 + isort):

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "N",  # pep8-naming
    "UP", # pyupgrade
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Run formatting:**
```bash
ruff format .
ruff check --fix .
```

---

## Naming Conventions

### Variables and Functions

```python
# snake_case for internal variables and functions
game_id = 2024020001
player_stats = _process_player_data()

# UPPER_CASE for constants
DEFAULT_TIMEOUT = 10
API_BASE_URL = "https://api-web.nhle.com/v1"

# _leading_underscore for private/internal
def _internal_helper():
    pass
```

### Classes

```python
# PascalCase for classes
class GameScraper:
    pass

class ColumnSchema:
    pass
```

### Functions: Public API Style

For **public API functions** (those users directly call), use camelCase to match existing package style:

```python
# Public API - use existing camelCase style
def scrapeTeams(source: str = "calendar") -> pd.DataFrame:
    """User-facing scraper function."""
    pass

def scrapeSchedule(team: str, season: str) -> pd.DataFrame:
    """User-facing scraper function."""
    pass
```

For **internal/helper functions**, use snake_case:

```python
# Internal functions - use snake_case
def _parse_roster_data(raw_data: dict) -> list:
    """Internal helper function."""
    pass

def build_shifts_events(shifts: pd.DataFrame) -> pd.DataFrame:
    """Internal processing function."""
    pass
```

---

## Type Hints

Use type hints for all function signatures:

```python
from typing import Optional, Union, Dict, List
import pandas as pd

def scrapeTeams(
    source: str = "calendar",
    output_format: str = "pandas"
) -> pd.DataFrame:
    """
    Scrape NHL teams data.
    
    Args:
        source: Data source ("calendar" or "standings")
        output_format: Output format ("pandas" or "polars")
    
    Returns:
        DataFrame containing teams data
    """
    pass
```

**Type Hint Best Practices:**
- Use `Optional[T]` for values that can be None
- Use `Union[T1, T2]` or `T1 | T2` for multiple possible types
- Use `List[T]`, `Dict[K, V]`, `Set[T]` for collections
- Use `pd.DataFrame` for DataFrames
- Import from `typing` module for Python 3.9 compatibility

---

## Documentation

### Docstrings: Google Style

Use Google-style docstrings for consistency:

```python
def scrape_game(
    game_id: int,
    include_shifts: bool = False,
    include_xg: bool = False
) -> pd.DataFrame:
    """
    Scrape complete game data including play-by-play and optional components.
    
    This function fetches comprehensive game data from the NHL API and HTML reports,
    combining them into a unified play-by-play DataFrame.
    
    Args:
        game_id: NHL game ID (e.g., 2024020001 for regular season game 1)
        include_shifts: If True, include shift start/end events
        include_xg: If True, calculate Expected Goals for shot attempts
    
    Returns:
        DataFrame containing play-by-play data with the following columns:
            - gameId: Game identifier
            - Event: Event type (GOAL, SHOT, FAC, etc.)
            - Per: Period number (1-5, 5 is shootout)
            - timeInPeriodSec: Seconds elapsed in period
            - x, y: Event coordinates
    
    Raises:
        InvalidGameError: If game_id is invalid
        APIError: If API request fails
    
    Example:
        >>> # Basic game data
        >>> df = scrape_game(2024020001)
        >>> print(f"Scraped {len(df)} events")
        
        >>> # With shifts and xG
        >>> df = scrape_game(2024020001, include_shifts=True, include_xg=True)
    
    Note:
        - Shift data requires additional HTML scraping (~2-3 seconds)
        - xG calculation requires XGBoost model (~1 second for 300 shots)
    """
    pass
```

---

## Error Handling

### Exception Hierarchy

Use custom exceptions from `scrapernhl.exceptions`:

```python
from scrapernhl.exceptions import APIError, InvalidGameError

def scrape_game(game_id: int) -> pd.DataFrame:
    """Scrape game with proper error handling."""
    
    # Validate input
    if not isinstance(game_id, int) or game_id < 2000000000:
        raise InvalidGameError(f"Invalid game ID: {game_id}")
    
    try:
        data = fetch_json(f"https://api.../game/{game_id}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise InvalidGameError(f"Game {game_id} not found") from e
        else:
            raise APIError(f"API request failed: {e}") from e
```

---

## Testing

### Test Naming

```python
import pytest
from scrapernhl import scrapeTeams
from scrapernhl.exceptions import InvalidGameError

class TestTeamsScraper:
    """Test suite for teams scraper."""
    
    def test_scrape_teams_returns_dataframe(self):
        """Test that scrapeTeams returns a pandas DataFrame."""
        result = scrapeTeams()
        assert isinstance(result, pd.DataFrame)
    
    def test_scrape_teams_has_required_columns(self):
        """Test that scraped teams have all required columns."""
        df = scrapeTeams()
        required = {"id", "name", "triCode", "franchiseId"}
        assert required.issubset(df.columns)
```

---

## Git Workflow

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format
<type>(<scope>): <subject>

<body>
```

**Examples:**

```bash
feat(scrapers): add player stats scraper

Add scrapePlayerStats() function to fetch individual player statistics.

---

fix(schema): correct column renaming for nested fields

Updated rename_map to flatten nested JSON fields properly.

---

docs(examples): add batch scraping example
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance (dependencies, config)

---

## Column Naming Standards

### Standard Column Names

To ensure consistency across all scrapers, use these standardized column names:

#### Game Identifiers
```python
"gameId"           # NHL game ID (int)
"season"           # Season (e.g., "20252026")
"gameType"         # Game type (2=regular, 3=playoff)
"gameDate"         # Date string (YYYY-MM-DD)
```

#### Team Identifiers
```python
"teamId"           # Team ID (int)
"teamName"         # Full team name
"teamAbbrev"       # 3-letter abbreviation (e.g., "MTL")
"triCode"          # Same as teamAbbrev (for compatibility)
```

#### Time Fields
```python
"Per"              # Period number (1-5, where 5 is shootout)
"period"           # Same as Per
"timeInPeriodSec"  # Seconds elapsed in period (int)
"elapsedTime"      # Total elapsed seconds from game start (int)
```

#### Event Fields
```python
"Event"            # Event type (GOAL, SHOT, FAC, etc.) - uppercase
"eventType"        # Same as Event
"eventId"          # Unique event identifier (int)
```

#### Coordinates
```python
"x"                # X coordinate (float, -100 to 100)
"y"                # Y coordinate (float, -42.5 to 42.5)
"xCoord"           # Same as x (from API)
"yCoord"           # Same as y (from API)
```

### Using Column Schemas

Always use the standardization function for scraped data:

```python
from scrapernhl.core.schema import standardize_columns

def scrapeTeams(output_format: str = "pandas") -> pd.DataFrame:
    """Scrape teams with standardized columns."""
    # Fetch raw data
    raw_data = fetch_json(TEAMS_URL)
    df = pd.json_normalize(raw_data)
    
    # Standardize columns
    df = standardize_columns(df, "teams", strict=False)
    
    return df
```

---

## Summary Checklist

Before submitting code, ensure:

- [ ] Follows PEP 8 style
- [ ] Has type hints for function signatures
- [ ] Has Google-style docstrings with examples
- [ ] Uses standardized column names
- [ ] Uses custom exceptions from `scrapernhl.exceptions`
- [ ] Uses logging from `scrapernhl.core.logging_config`
- [ ] Includes tests for new functionality
- [ ] Tests pass locally (`pytest`)
- [ ] Commit messages follow conventional commits format

---

**Questions or suggestions?** Open an issue or discussion on GitHub!
