# Getting Started

Install the package and start scraping NHL data in minutes.

## Installation

### From PyPI (Stable)

Install the latest stable version:

```bash
pip install scrapernhl
```

> **Note:** Version 0.1.5 (latest) includes critical bug fixes for multi-league scrapers. See the [CHANGELOG](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md) for details.

Or with uv:

```bash
uv add scrapernhl
```

### From GitHub (Latest)

Install the development version with the latest features and fixes:

```bash
pip install git+https://github.com/maxtixador/scrapernhl.git
```

Or with uv:

```bash
uv pip install git+https://github.com/maxtixador/scrapernhl.git
```

### From Source

For development or local modifications:

```bash
git clone https://github.com/maxtixador/scrapernhl.git
cd scrapernhl
pip install -e .
```


## Quick Start

### Command-Line Interface

The fastest way to get started is using the CLI:

```bash
# Get help
python scrapernhl/cli.py --help

# Scrape all NHL teams
python scrapernhl/cli.py teams

# Get a team's schedule
python scrapernhl/cli.py schedule MTL 20252026

# Get current standings
python scrapernhl/cli.py standings
```

See [CLI Examples](examples/cli.md) for more examples.

### Python API

The main function you'll use most is `scrapeGame()`:

```python
from scrapernhl import scrapeGame

# Scrape complete game data (play-by-play + rosters + metadata)
# This is THE MAIN FUNCTION - it gets everything you need in one call
game_data = scrapeGame(2024020001, include_tuple=True)

print(f"Game: {game_data.awayTeam} @ {game_data.homeTeam}")
print(f"Events: {len(game_data.data)}")

# Access the data
pbp = game_data.data  # Play-by-play DataFrame
rosters = game_data.rosters  # Player rosters
```

Other useful scraping functions:

```python
from scrapernhl import scrapeTeams, scrapeSchedule, scrapeStandings

# Scrape teams
teams = scrapeTeams()

# Scrape schedule  
schedule = scrapeSchedule('MTL', '20252026')

# Scrape standings
standings = scrapeStandings('2026-01-01')

# Player stats
from scrapernhl import scrapePlayerSeasonStats
stats = scrapePlayerSeasonStats(8478402, "20242025")  # Connor McDavid

# Advanced analytics
from scrapernhl import calculate_corsi, identify_scoring_chances, create_analytics_report

corsi = calculate_corsi(pbp)
chances = identify_scoring_chances(pbp)
report = create_analytics_report(pbp, rosters)
```

**Note**: The function is named `scrapeGame` (camelCase) to match naming conventions (`scrapeTeams`, `scrapeSchedule`, etc.). The old `scrape_game` (snake_case) still works for backward compatibility.

See [API Reference](api.md) for all available functions.

## Project Structure

ScraperNHL v0.1.5 supports 6 hockey leagues with a modular structure:

```
scrapernhl/
├── core/          # Shared utilities (all leagues)
├── nhl/           # NHL scrapers and analytics
├── pwhl/          # PWHL support
├── ahl/           # AHL support
├── ohl/           # OHL support
├── whl/           # WHL support
├── qmjhl/         # QMJHL support
└── cli.py         # Multi-league CLI
```

### Multi-League Support (New in v0.1.5)

Each league has its own module with consistent API:

```python
# PWHL
from scrapernhl.pwhl.scrapers import scrapeTeams, scrapeSchedule, scrapeStandings

# AHL
from scrapernhl.ahl.scrapers import scrapeTeams, scrapeRoster

# OHL
from scrapernhl.ohl.scrapers import scrapeTeams, scrapePlayerStats

# WHL
from scrapernhl.whl.scrapers import scrapeTeams, scrape_game

# QMJHL
from scrapernhl.qmjql.scrapers import scrapeTeams, scrapeStandings
```

### Backward Compatibility

For backward compatibility, all NHL functions are re-exported at the package level:

```python
# These are equivalent:
from scrapernhl import scrapeTeams
from scrapernhl.nhl.scrapers.teams import scrapeTeams
```

See the [Multi-League API Examples](multi-league-api-examples.md) and [Multi-League Scraper Reference](multi-league-scraper-reference.md) for comprehensive documentation.

## Requirements

- Python >= 3.9 (tested on 3.9-3.13)
- See full dependencies in `pyproject.toml`