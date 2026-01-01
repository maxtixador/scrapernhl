# Welcome to ScraperNHL's documentation!

ScraperNHL is a Python package designed for scraping and analyzing NHL data. This documentation will guide you through the installation, usage, and features of the package.

# ScraperNHL

A comprehensive Python package for scraping and analyzing NHL data with built-in Expected Goals (xG) modeling and advanced analytics.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://maxtixador.github.io/scrapernhl/)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

### Comprehensive Data Scraping
- **Teams**: NHL team data, rosters, and metadata
- **Schedule**: Team schedules with game states and scores
- **Standings**: League standings with points and rankings
- **Player Stats**: Skater and goalie statistics
- **Play-by-Play**: Detailed game events with coordinates
- **Draft Data**: Historical draft picks and prospects
- **Expected Goals (xG)**: Built-in xG model for shot quality analysis

### Multiple Access Methods
- **Python API**: Full-featured library with pandas/polars support
- **Command-Line Interface**: Quick data exports without writing code
- **Jupyter Notebooks**: Interactive examples and tutorials

### Performance & Design
- **Modular Architecture**: Fast imports (~100ms vs 2-3s)
- **Flexible Output**: CSV, JSON, Parquet, Excel formats
- **Backward Compatible**: Existing code works without changes
- **Well Documented**: Comprehensive guides and API reference

## Installation

```bash
pip install scrapernhl
```

Or install from source:
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

📚 **Full documentation available at: [maxtixador.github.io/scrapernhl](https://maxtixador.github.io/scrapernhl/)**

- [Getting Started Guide](https://maxtixador.github.io/scrapernhl/getting-started/)
- [API Reference](https://maxtixador.github.io/scrapernhl/api/)
- [CLI Usage Examples](https://maxtixador.github.io/scrapernhl/examples/cli/)
- [Advanced Analytics](https://maxtixador.github.io/scrapernhl/examples/advanced/)
- [Data Export Options](https://maxtixador.github.io/scrapernhl/examples/export/)

## Examples

Check out the example notebooks for detailed tutorials:
- [notebooks/01_basic_scraping.ipynb](notebooks/01_basic_scraping.ipynb) - Basic data scraping
- [notebooks/02_advanced_analytics.ipynb](notebooks/02_advanced_analytics.ipynb) - xG analysis, TOI, player combinations
- [notebooks/03_data_export.ipynb](notebooks/03_data_export.ipynb) - Export formats and workflows

## What's New in v0.1.4

- **Modular Architecture**: Codebase restructured into focused modules
- **CLI Integration**: Command-line interface for all scraping functions
- **Documentation Website**: Comprehensive guides and examples
- **Performance**: Faster imports and optimized data fetching
- **Testing**: Unit tests for reliability
- **Standardized Code**: Consistent style across notebooks and examples

See [full release notes](https://maxtixador.github.io/scrapernhl/announcements/version-014/)

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, documentation improvements, or code contributions - your help makes this project better.

## License

MIT License - see LICENSE file for details

## Author

**Max Tixador** | Hockey Analytics Enthusiast

- Twitter: [@woumaxx](https://x.com/woumaxx)
- Bluesky: [@HabsBrain.com](https://bsky.app/profile/habsbrain.com)
- Email: [maxtixador@gmail.com](mailto:maxtixador@gmail.com)

## Acknowledgments

Built for the hockey analytics community. Special thanks to all contributors and users who provide feedback and suggestions!

---

**Last Updated:** January 2026 | **Version:** 0.1.4
