# ScraperNHL Documentation

NHL data scraping package with Expected Goals (xG) model, advanced analytics, and multi-league support architecture.

## Overview

ScraperNHL is a Python package designed for scraping and analyzing NHL data. This documentation will guide you through the installation, usage, and features of the package.

**Python Version:** 3.9+ (tested on 3.9-3.13)  
**Current Version:** 0.1.4

## Installation

**Stable (PyPI):**
```bash
pip install scrapernhl
```

**Latest (GitHub):**
```bash
pip install git+https://github.com/maxtixador/scrapernhl.git
```

See [Getting Started](getting-started.md) for more installation options.

## Quick Example

```python
from scrapernhl import scrapeGame

# The main function - get complete game data in one call
game_data = scrapeGame(2024020001, include_tuple=True)
print(f"Game: {game_data.awayTeam} @ {game_data.homeTeam}")

# Access play-by-play and rosters
pbp = game_data.data
rosters = game_data.rosters
```

## Features

### Data Collection
- Fast NHL data scraping using `selectolax`
- Teams, schedules, standings, rosters, stats
- Play-by-play data with coordinates
- Player profiles, season stats, game logs
- Draft data and historical records

### Multi-League Support
- **5 Leagues**: PWHL, AHL, OHL, WHL, QMJHL
- Unified API across all leagues
- 15+ functions per league (75 total endpoints)
- See [Multi-League API Examples](multi-league-api-examples.md) and [Quick Reference](api-quick-reference.md)

### Analytics
- Pre-trained XGBoost Expected Goals (xG) model
- Corsi and Fenwick calculations
- Scoring chance classification (high/medium/low danger)
- Time on ice (TOI) metrics
- Zone start percentages
- Score effects analysis
- Shooting pattern analysis

### Infrastructure
- Professional error handling and logging
- File-based caching with TTL
- Progress bars for long operations
- Batch processing with parallel execution
- Rate limiting and automatic retries
- Rich-formatted console output

### Multi-League Ready
- Organized for NHL, OHL, WHL, QMJHL, PWHL support
- Shared core utilities across leagues
- League-specific scrapers and analytics
- Backward compatible API

## Quick Links

### Getting Started
- [Getting Started](getting-started.md) - Installation and setup
- [API Reference](api.md) - Complete NHL API documentation

### Multi-League APIs (NEW!)
- [🚀 Quick Reference](api-quick-reference.md) - Fast lookup for all 15 functions
- [📚 Complete Examples](multi-league-api-examples.md) - Comprehensive guide with patterns
- [📓 Interactive Notebook](../notebooks/multi_league_api_examples.ipynb) - Jupyter examples
- [🧪 Test Suite](../test_multi_league_api.py) - Reference implementations

### Examples
- [CLI Examples](examples/cli.md) - Command-line usage
- [Python Examples](examples/scraping.md) - Python API usage
- [Advanced Analytics](examples/advanced.md) - Analytics features

### About
- [About the Project](about.md)
- [GitHub Repository](https://github.com/maxtixador/scrapernhl)
- [PyPI Package](https://pypi.org/project/scrapernhl/)
- [Announcements](announcements/version-014.md) - Latest news and updates


