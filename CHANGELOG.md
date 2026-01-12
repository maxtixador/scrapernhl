# Changelog

All notable changes to ScraperNHL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/maxtixador/scrapernhl/compare/v0.1.5...HEAD
[Unreleased]: https://github.com/maxtixador/scrapernhl/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/maxtixador/scrapernhl/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/maxtixador/scrapernhl/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/maxtixador/scrapernhl/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/maxtixador/scrapernhl/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/maxtixador/scrapernhl/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/maxtixador/scrapernhl/releases/tag/v0.1.0
