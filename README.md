# ScraperNHL

Python package for scraping and analyzing NHL data with built-in Expected Goals (xG) modeling and multi-league support architecture.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://maxtixador.github.io/scrapernhl/)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

### Data Scraping
- **🏒 Game Data (`scrapeGame`)**: Complete play-by-play, rosters, metadata - THE MAIN FUNCTION
- **Teams**: NHL team data, rosters, metadata
- **Schedule**: Team schedules with game states and scores
- **Standings**: League standings
- **Player Stats**: Skater and goalie statistics, game logs
- **Play-by-Play**: Game events with coordinates
- **Draft Data**: Historical draft picks
- **Expected Goals (xG)**: Built-in xG model
- **Advanced Analytics**: Corsi, Fenwick, scoring chances, TOI, zone starts

### Multi-League Ready
- **NHL**: Full support (teams, games, players, analytics)
- **Future Leagues**: Architecture supports OHL, WHL, QMJHL, PWHL
- **Shared Infrastructure**: Caching, progress tracking, batch processing

### Access Methods
- **Python API**: pandas/polars support
- **Command-Line Interface**: Quick exports
- **Jupyter Notebooks**: Interactive examples

### Design
- **Modular**: Fast imports (~100ms)
- **Professional**: Error handling, logging, caching, progress bars
- **Flexible Output**: CSV, JSON, Parquet, Excel
- **Backward Compatible**: All existing code continues to work
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
from scrapernhl import scrapeGame, scrapeTeams, scrapeSchedule

# Scrape complete game data (play-by-play + rosters) - THE MAIN FUNCTION
game_data = scrapeGame(2024020001, include_tuple=True)
print(f"Game: {game_data.awayTeam} @ {game_data.homeTeam}")
print(f"Events: {len(game_data.data)}")

# Get all NHL teams
teams = scrapeTeams()

# Get team schedule
schedule = scrapeSchedule("MTL", "20252026")

# Get current standings
from scrapernhl import scrapeStandings
from datetime import datetime
standings = scrapeStandings(datetime.now().strftime("%Y-%m-%d"))

# Player stats
from scrapernhl import scrapePlayerSeasonStats
player_stats = scrapePlayerSeasonStats(8478402, "20242025")  # Connor McDavid

# Advanced analytics
from scrapernhl import calculate_corsi, identify_scoring_chances, create_analytics_report
pbp = game_data.data
corsi = calculate_corsi(pbp)
chances = identify_scoring_chances(pbp)
report = create_analytics_report(pbp, game_data.rosters)
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

### Major Features
- **Multi-League Architecture**: Reorganized for NHL, OHL, WHL, QMJHL, PWHL support
- **Advanced Analytics**: 12 analytics functions (Corsi, Fenwick, scoring chances, TOI, zone starts)
- **Visualization**: 9 Rich-formatted display functions for beautiful console output
- **Player Stats**: Complete player data scrapers with batch processing
- **Batch Processing**: Parallel scraping with rate limiting and error recovery
- **Professional Infrastructure**: Caching, logging, progress bars, error handling

### Improvements
- Modular architecture with league-specific subdirectories
- CLI for all scraping functions
- Documentation website with examples
- Faster imports (<100ms)
- Comprehensive test suite
- Full backward compatibility

See:
- [Multi-League Reorganization Guide](MULTI_LEAGUE_REORG.md)
- [Project Structure

```
scrapernhl/
├── core/                    # Shared utilities (all leagues)
│   ├── http.py             # HTTP client
│   ├── cache.py            # File caching
│   ├── progress.py         # Progress bars
│   ├── batch.py            # Parallel processing
│   └── ...
├── nhl/                     # NHL-specific code
│   ├── scrapers/           # NHL data scrapers
│   ├── analytics.py        # NHL analytics
│   └── models/             # xG models
├── exceptions.py            # Error handling
├── visualization.py         # Display utilities
└── ...
```

For adding new leagues, see [MULTI_LEAGUE_REORG.md](MULTI_LEAGUE_REORG.md)

## Contributing

Contributions welcome - bug reports, features, docs, or code.

For AI assistants: See `.ai/GUIDELINES.md` for development standards
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
