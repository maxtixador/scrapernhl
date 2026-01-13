# ScraperNHL Documentation

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://maxtixador.github.io/scrapernhl/)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Hockey (*not only NHL anymore 😀*) data scraping package with Expected Goals (xG) model, advanced analytics, and multi-league support architecture.

## Overview

ScraperNHL is a Python package designed for scraping and analyzing hockey data. This documentation will guide you through the installation, usage, and features of the package.

**Python Version:** 3.9+ (tested on 3.9-3.13)  
**Current Version:** 0.1.5

> **New in 0.1.5:** Multi-league support for **PWHL, AHL, OHL, WHL, QMJHL**! ScraperNHL now supports 6 total hockey leagues with complete scraper coverage.

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
- Complete scraper coverage: Schedule, Teams, Standings, Player Stats, Rosters
- Unified interface across all leagues
- Built-in caching and error handling
- See [Multi-League Scraper Reference](multi-league-scraper-reference.md)

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

### Multi-League Scrapers
- [Scraper Reference](multi-league-scraper-reference.md) - Complete API for all 5 leagues
- [Demo Notebook](../notebooks/multi_league_demo.ipynb) - Interactive examples
- [Player Demo](../notebooks/player_demo.ipynb) - Cross-league player data

### Examples
- [CLI Examples](examples/cli.md) - Multi-league command-line usage
- [Python Examples](examples/scraping.md) - Python API usage
- [Advanced Analytics](examples/advanced.md) - Analytics features
- [Multi-League API Examples](multi-league-api-examples.md) - Cross-league examples

### About
- [About the Project](about.md)
- [GitHub Repository](https://github.com/maxtixador/scrapernhl)
- [PyPI Package](https://pypi.org/project/scrapernhl/)
- [Announcements](announcements/version-015.md) - Latest news and updates


