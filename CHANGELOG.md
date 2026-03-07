# Changelog

All notable changes to ScraperNHL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2026-03-07

### Fixed

- Strength labels for the alphabetically second team in analytics functions — `on_ice_stats_by_player_strength()`, `toi_by_player_and_strength()`, `combo_on_ice_stats()`, `combo_on_ice_stats_both_teams()`, and `team_strength_aggregates()` now correctly use the focus team's perspective for strength labels. Previously the second alphabetical team always received the mirror of the home team's label (e.g. `"5v4"` instead of `"4v5"` for a penalized away team killing off a penalty)
- `urllib3` minimum version bumped to `2.0.7` (was `2.0.0`) to fix chunked HTTP response truncation causing silently incomplete PBP data
- `pandas` dependency updated to `>=2.2.3` for NumPy 2.x compatibility
- README: corrected PWHL's full name from "Provincial" to "Professional" (Professional Women's Hockey League)

## [0.3.1] - 2026-03-06

### Fixed

- `gameStrength` on ON/OFF shift events was always from the home team's perspective; now uses the changing player's team perspective (`"4v5"` for an away player killed off, not `"5v4"`)
- `home_strength` and `away_strength` PBP columns were swapped for away-team events (contained the away team's value and home team's value respectively); now always reflect the actual home and away team regardless of which team owns the event
- `parse_schedule` raised `IndexError` when the API returned a response with empty sections (e.g. a team with no scheduled games in the requested season)
- Zone start qualifier assignment in `scrape_game` could crash with a pandas length-mismatch error when two faceoff events shared the exact same elapsed second in the same period; faceoffs are now deduplicated before the merge

## [0.3.0] - 2026-03-05

This is a major rewrite. The package is now a single unified client for all six leagues with a clean, consistent API.

### Added
- **Unified `HockeyScraper` client** — one class for all six leagues (`nhl`, `ahl`, `pwhl`, `ohl`, `whl`, `qmjhl`) via `from scrapernhl import HockeyScraper`
- **`scrape()` functional API** — top-level one-liner: `scrape('ahl', 'pbp', game_id=1027781)`
- **Parse → transform → enrich pipeline** — `parsers.py`, `transform.py`, `urls.py`, `utils.py`, `enrichment.py` as the internal supporting layer
- **`url_for(data_type, **kwargs)`** — inspect the URL for any endpoint without making a network request
- **`fetch_raw(data_type, **kwargs)`** — return the unprocessed API response, bypassing all parsing
- **`endpoints.md`** — wire-format API reference documenting every URL, parameter, and response shape for all six leagues
- **GitHub Actions CI** — ruff lint + pytest on Python 3.10, 3.11, and 3.12 on every push and PR; integration tests skipped in CI
- **New unified notebooks** — `01_getting_started.ipynb`, `02_nhl_data.ipynb`, `03_other_leagues.ipynb`, `04_advanced_features.ipynb`
- **`api_notebook.ipynb`** — comprehensive, runnable API reference notebook covering every public method
- **Comprehensive pytest suites** — `test_client.py`, `test_endpoints.py`, `test_all_non_nhl_leagues.py` (501 tests)
- **`tracking_dict_to_df(frames)`** exported at top level — converts goal-replay sprite frames to a tidy DataFrame with rink coordinates

### Changed
- **Minimum Python version raised to 3.10** (was 3.9)
- **Optional dependencies restructured** — `xgboost`, `seaborn`, `jupyterlab`, and `playwright` moved out of the default install into `[analytics]` and `[notebooks]` extras; `pip install scrapernhl` now installs ~50 MB instead of ~650 MB
- **CLI unified** — single `scrapernhl <league> <data_type> [options]` interface replaces the old league-specific subcommand structure
- **Bootstrap data lazy-loaded** — non-NHL scrapers fetch bootstrap on first access rather than eagerly on init, improving cold-start time

### Removed
- All league-specific top-level modules (`scrapernhl.ahl`, `scrapernhl.pwhl`, `scrapernhl.ohl`, `scrapernhl.whl`, `scrapernhl.qmjhl`) — use `HockeyScraper('<league>')` instead
- `engineer_xg_features()` and `predict_xg()` — use `on_ice_stats()` and `team_strength_aggregates()` directly on the PBP DataFrame
- Visualization module (`visualization.py`)
- Old league-specific notebooks (01–10 in `archive/`)

### Migration Guide
```python
# 0.1.x (old)
from scrapernhl.ahl.scrapers import scrapeSkaterStats, scrapeStandings
from scrapernhl.nhl.scraper import scrapeGame

stats     = scrapeSkaterStats(season=90)
standings = scrapeStandings()
game      = scrapeGame(2023020001, include_tuple=True)

# 0.3.0 (new)
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
nhl = HockeyScraper('nhl')

stats     = ahl.player_stats(season=90, position='skaters')
standings = ahl.standings()
game      = nhl.scrape_game(2023020001)
```

## [0.1.5] - 2026-01-11

### Fixed
- Fixed WHL and OHL teams scrapers to use bootstrap data instead of broken `teamsForSeason` API endpoint
- Fixed OHL career stats function to handle empty DataFrames correctly
- Fixed PWHL scrape_game test to use correct column name ('game_id' instead of 'id')
- Fixed test_reorganization.py pytest warnings by removing return statements from test functions
- Fixed WHL, OHL, QMJHL goalie stats to correctly use `position='goalies'` parameter
- Fixed QMJHL goalie stats to use `view='players'` instead of non-existent `view='goalies'`
- Fixed AHL and PWHL teams API response handling for both dict and list responses

### Added
- Comprehensive test suite for multi-league scrapers (AHL, PWHL, OHL, WHL, QMJHL)
- Notebook scrape function tests to ensure DataFrame output
- Career stats tests across all HockeyTech leagues
- Goalie stats validation tests

### Changed
- Career stats functions in OHL, WHL, QMJHL now properly parse nested JSON structure
- Updated notebooks 05-09 to use DataFrame-based scraper functions

### Documentation
- Added CAREER_STATS_FIX.md documenting career stats improvements
- Added GOALIE_STATS_FIX.md documenting goalie stats fixes
- Added NOTEBOOK_ERRORS_LOG.md tracking notebook validation issues
- Added TEST_RESULTS.md documenting test suite results

## [0.1.4] - 2024

### Added
- Multi-league support: PWHL, AHL, OHL, WHL, QMJHL
- Comprehensive scraper modules for 5 HockeyTech leagues
- Complete coverage: Schedule, teams, standings, player stats, rosters
- Unified interface across all leagues
- DataFrame output with pandas/polars support
- Play-by-Play scrapers with enhanced cleaning
- Built-in TTL-based caching for all scrapers
- Rate limiting (2 req/sec enforcement)

### Changed
- Modular architecture with fast imports (~100ms)
- Professional error handling, logging, and progress bars
- Flexible output formats: CSV, JSON, Parquet, Excel

### Documentation
- Multi-league API framework documentation
- Jupyter notebooks for each league (05-09)

## [0.1.3] - 2024

### Added
- Expected Goals (xG) modeling functionality
- Advanced analytics: Corsi, Fenwick, scoring chances
- TOI and zone start calculations

### Fixed
- Various bug fixes and performance improvements

## [0.1.2] - 2024

### Added
- Command-line interface improvements
- Enhanced player statistics scraping
- Game log functionality

### Fixed
- API endpoint updates
- Data parsing improvements

## [0.1.1] - 2024

### Added
- Initial draft data scraping
- Player profile functions
- Team roster scraping

### Fixed
- Schedule parsing issues
- Team data validation

## [0.1.0] - 2024

### Added
- Initial release
- Core NHL data scraping functionality
- Game data with play-by-play
- Team and schedule scrapers
- Standings functionality
- Basic player stats
- Python API and CLI interface

[Unreleased]: https://github.com/maxtixador/scrapernhl/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/maxtixador/scrapernhl/compare/v0.1.5...v0.3.0
[0.1.5]: https://github.com/maxtixador/scrapernhl/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/maxtixador/scrapernhl/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/maxtixador/scrapernhl/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/maxtixador/scrapernhl/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/maxtixador/scrapernhl/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/maxtixador/scrapernhl/releases/tag/v0.1.0
