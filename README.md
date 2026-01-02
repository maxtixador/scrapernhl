# ScraperNHL

Python package for scraping and analyzing NHL data with built-in Expected Goals (xG) modeling.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://maxtixador.github.io/scrapernhl/)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

### Data Scraping
- **Teams**: NHL team data, rosters, metadata
- **Schedule**: Team schedules with game states and scores
- **Standings**: League standings
- **Player Stats**: Skater and goalie statistics
- **Play-by-Play**: Game events with coordinates
- **Draft Data**: Historical draft picks
- **Expected Goals (xG)**: Built-in xG model

### Access Methods
- **Python API**: pandas/polars support
- **Command-Line Interface**: Quick exports
- **Jupyter Notebooks**: Interactive examples

### Design
- **Modular**: Fast imports (~100ms)
- **Flexible Output**: CSV, JSON, Parquet, Excel
- **Backward Compatible**: Works with existing code
- **Documented**: Guides and API reference

## Installation

### From PyPI (Stable)

```bash
pip install scrapernhl
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

```bash
git clone https://github.com/maxtixador/scrapernhl.git
cd scrapernhl
pip install -e .
```

## Quick Start

### Python API

```python
from scrapernhl import scrapeTeams, scrapeSchedule, scrapeStandings

# Get all NHL teams
teams = scrapeTeams()

# Get team schedule
schedule = scrapeSchedule("MTL", "20252026")

# Get current standings
from datetime import datetime
standings = scrapeStandings(datetime.now().strftime("%Y-%m-%d"))
```

### Command-Line Interface

```bash
# Scrape teams
scrapernhl teams --output teams.csv

# Scrape schedule
scrapernhl schedule MTL 20252026 --format json

# Scrape play-by-play with xG
scrapernhl game 2024020001 --with-xg --output game.csv

# Get help
scrapernhl --help
```

## Documentation

Full documentation: [maxtixador.github.io/scrapernhl](https://maxtixador.github.io/scrapernhl/)

- [Getting Started Guide](https://maxtixador.github.io/scrapernhl/getting-started/)
- [API Reference](https://maxtixador.github.io/scrapernhl/api/)
- [CLI Usage Examples](https://maxtixador.github.io/scrapernhl/examples/cli/)
- [Advanced Analytics](https://maxtixador.github.io/scrapernhl/examples/advanced/)
- [Data Export Options](https://maxtixador.github.io/scrapernhl/examples/export/)

## Examples

Check out the notebooks:
- [notebooks/01_basic_scraping.ipynb](notebooks/01_basic_scraping.ipynb)
- [notebooks/02_advanced_analytics.ipynb](notebooks/02_advanced_analytics.ipynb)
- [notebooks/03_data_export.ipynb](notebooks/03_data_export.ipynb)

## What's New in v0.1.4

- Modular architecture
- CLI for all scraping functions
- Documentation website
- Faster imports
- Unit tests
- Standardized code

See [full release notes](https://maxtixador.github.io/scrapernhl/announcements/version-014/)

## Contributing

Contributions welcome - bug reports, features, docs, or code.

## License

MIT License - see LICENSE file for details

## Author

**Max Tixador** | Hockey Analytics Enthusiast

- Twitter: [@woumaxx](https://x.com/woumaxx)
- Bluesky: [@HabsBrain.com](https://bsky.app/profile/habsbrain.com)
- Email: [maxtixador@gmail.com](mailto:maxtixador@gmail.com)

## Acknowledgments

Built for the hockey analytics community.

---

**Last Updated:** January 2026 | **Version:** 0.1.4
