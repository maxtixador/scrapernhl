# ScraperNHL Documentation

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://maxtixador.github.io/scrapernhl/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Hockey (*not only NHL anymore 😀*) data scraping package with advanced analytics and multi-league support.

## Overview

ScraperNHL is a Python package designed for scraping and analyzing hockey data. This documentation will guide you through the installation, usage, and features of the package.

**Python Version:** 3.10+ (tested on 3.10–3.13)  
**Current Version:** 0.3.1

> **New in 0.3.0:** Complete rewrite — all six leagues now share a single `HockeyScraper` client with a consistent API. League-specific modules are removed. Install footprint reduced from ~650 MB to ~50 MB. See the [migration guide](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md#migration-guide) for details.
>
> **New in 0.3.1:** Bug-fix release — corrects `gameStrength` perspective for away-team shift events, fixes swapped `home_strength`/`away_strength` columns, fixes `parse_schedule` `IndexError` on empty API responses, and resolves a zone-start pandas length-mismatch crash.

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
from scrapernhl import HockeyScraper

# Works for any of the six leagues
nhl = HockeyScraper('nhl')
ahl = HockeyScraper('ahl')

# Play-by-play
pbp = nhl.play_by_play(2023020001)

# Full game pipeline (HTML + JSON merged, with on-ice player lists)
full_pbp = nhl.scrape_game(2023020001)

# Non-NHL: standings, stats, schedule
standings = ahl.standings()
stats     = ahl.player_stats(season=90, position='skaters')
schedule  = ahl.schedule(season=90)
```

Or with the functional one-liner API:

```python
from scrapernhl import scrape

pbp      = scrape('ahl', 'pbp', game_id=1027781)
standings = scrape('nhl', 'standings', season=20232024)
```

## Features

### Data Collection
- Fast NHL data scraping using `selectolax`
- Teams, schedules, standings, rosters, stats
- Play-by-play data with coordinates
- Player profiles, season stats, game logs
- Draft data and historical records

### Multi-League Support
- **6 Leagues**: NHL, PWHL, AHL, OHL, WHL, QMJHL — single `HockeyScraper` client for all
- Complete scraper coverage: Schedule, Teams, Standings, Player Stats, Rosters, Play-by-Play
- Bootstrap accessors for non-NHL leagues (teams, seasons, conferences, divisions)
- Built-in caching and error handling

### Analytics

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
- Single `HockeyScraper` client for all six leagues
- Bootstrap accessors: `teams`, `get_seasons()`, `get_conferences()`, `get_divisions()`
- `url_for()` and `fetch_raw()` available on every scraper
- Consistent method signatures across all leagues

## Quick Links

### Getting Started
- [Getting Started](getting-started.md) - Installation and setup
- [API Reference](api.md) - Complete API documentation for all leagues

### Examples
- [CLI Examples](examples/cli.md) - Command-line usage
- [Python Examples](examples/scraping.md) - Python API usage
- [Advanced Analytics](examples/advanced.md) - Analytics features

### About
- [About the Project](about.md)
- [GitHub Repository](https://github.com/maxtixador/scrapernhl)
- [PyPI Package](https://pypi.org/project/scrapernhl/)
- [Changelog](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md)
- [Announcements](announcements/version-030.md) - Latest news and updates


