---
title: "Version 0.1.5 Released - Multi-League Support!"
date: 2026-01-11
tags: ["announcement", "release", "multi-league"]
categories: ["announcements"]
draft: false
---

# ANNOUNCEMENT: Version 0.1.5 Released
*Date: January 11th, 2026*

Hello, fellow hockey analytics enthusiasts!

Version 0.1.5 is now available with **major new features**: comprehensive support for **5 professional hockey leagues**! Previously, ScraperNHL only supported NHL data. Now you can scrape data from:

- **PWHL** (Professional Women's Hockey League) - Shoutout to women's hockey! *where I got my first pro hockey experience 😉*
- **AHL** (American Hockey League)
- **OHL** (Ontario Hockey League)
- **WHL** (Western Hockey League)
- **QMJHL** (Quebec Maritimes Junior Hockey League)

This release includes complete scraper coverage, robust test suites, and bug fixes to ensure reliable data collection across all leagues.

Thanks to Louis Boulet for telling me about the massive bug in strength label calculations that prompted this fix! Also thanks to Claude Code (I am not sponsored by Anthropic yet unfornunately) for the multiplle rounds of review and and debugging help. 

Of course, there are still more improvements to be made. Make sure you follow the project on GitHub and check out the [full changelog](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md) for details. You can also follow me on Twitter [@maxtixador](https://twitter.com/maxtixador) or on Bluesky [@HabsBrain.com](https://bsky.app/profile/habsbrain.com) for updates.


## Major New Features

### Multi-League Scraper Support

ScraperNHL now supports **5 additional hockey leagues** beyond NHL:

```python
# Each league has complete scraper coverage
from scrapernhl.pwhl.scrapers import scrapeSchedule, scrapeTeams, scrapeStandings
from scrapernhl.ahl.scrapers import scrapeSkaterStats, scrapeGoalieStats
from scrapernhl.ohl.scrapers import scrapeGame, scrapeRoster

# Unified API across all leagues
pwhl_schedule = scrapeSchedule(season=2024)
ahl_teams = scrapeTeams()
ohl_games = scrapeGame(game_id=12345, nhlify=True)
```

**Available Functions (All 5 Leagues):**
- `scrapeSchedule()` - Game schedules with scores and status
- `scrapeTeams()` - Team information and rosters
- `scrapeStandings()` - League standings
- `scrapeSkaterStats()` - Player statistics (skaters)
- `scrapeGoalieStats()` - Goalie statistics
- `scrapeGame()` - Play-by-play data with optional "nhlify" cleaning
- `scrapeRoster()` - Team rosters
- Plus career stats, player profiles, and more!

**Features:**
- **Unified Interface**: Same function signatures across all leagues
- **DataFrame Output**: Returns pandas/polars DataFrames
- **Built-in Caching**: TTL-based caching for performance
- **Rate Limiting**: Automatic 2 req/sec enforcement
- **Progress Bars**: Visual feedback for long operations
- **Error Handling**: Robust error recovery

### Complete Documentation

- [Multi-League Scraper Reference](../multi-league-scraper-reference.md) - Complete API documentation
- [Jupyter Notebooks](../../notebooks/) - Interactive examples for each league (notebooks 05-09)
- [API Quick Reference](../api-quick-reference.md) - Fast function lookup

## Critical Bug Fixes

### Strength Label Perspective

Fixed an issue where strength states were computed from a single (alphabetical) team’s perspective and incorrectly applied to both teams, causing PK situations to be mislabeled as PP for the opponent.

- `strength_label()` helpers now accept a team parameter to ensure correct perspective
- All affected call sites now pass team context when computing TOI and attributing stats

**Result:** Strength labels are now correct and team-relative (e.g., OTT 5v4, WPG 4v5).

## New Test Coverage

Version 0.1.5 includes a comprehensive test suite to ensure data quality across all leagues:

### Multi-League Scraper Tests
- Complete test coverage for AHL, PWHL, OHL, WHL, and QMJHL scrapers
- Tests for schedule, teams, standings, player stats, and rosters
- Ensures all scrapers return valid DataFrames with expected columns

### Career Stats Tests
- Validates career statistics parsing across all HockeyTech leagues
- Ensures proper handling of nested JSON structures
- Tests for both skaters and goalies

### Goalie Stats Validation
- Comprehensive goalie statistics tests for all leagues
- Validates correct API parameter usage
- Ensures accurate stat retrieval

### Notebook Function Tests
- Tests all scrape functions used in notebooks 05-09
- Ensures DataFrame output is correctly formatted
- Validates data consistency across examples

## Updated Documentation

- **Notebooks 05-09** updated to use improved DataFrame-based scraper functions
- All examples now work correctly with the bug fixes
- Improved inline documentation for multi-league functions

## Backward Compatibility

All existing code continues to work without changes. This release only fixes bugs and improves data quality—**no breaking changes** to the API.

## Getting Started

Install or update to version 0.1.5:

```bash
pip install --upgrade scrapernhl
```

Or install from GitHub for the latest:

```bash
pip install git+https://github.com/maxtixador/scrapernhl.git
```

### Multi-League Scraping Example

```python
# NHL (existing functionality)
from scrapernhl import scrapeGame
nhl_game = scrapeGame(2024020001)

# NEW: PWHL support
from scrapernhl.pwhl.scrapers import scrapeSchedule, scrapeSkaterStats
pwhl_schedule = scrapeSchedule(season=2024)
pwhl_stats = scrapeSkaterStats(season=2024, team_id=-1)

# NEW: AHL support  
from scrapernhl.ahl.scrapers import scrapeTeams, scrapeGoalieStats
ahl_teams = scrapeTeams()
ahl_goalies = scrapeGoalieStats(season=2024)

# NEW: OHL, WHL, QMJHL support
from scrapernhl.ohl.scrapers import scrapeGame
from scrapernhl.whl.scrapers import scrapeStandings
from scrapernhl.qmjhl.scrapers import scrapeRoster

ohl_game = scrapeGame(12345, nhlify=True)
whl_standings = scrapeStandings()
qmjhl_roster = scrapeRoster(season=2024, team_id=5)
```

### Multi-League API

All leagues also support a unified API interface:

```python
from scrapernhl.pwhl import api as pwhl
from scrapernhl.ahl import api as ahl

# Get teams
teams = pwhl.get_teams()

# Get player stats
stats = ahl.get_skater_stats(limit=50)

# Get standings
standings = pwhl.get_standings(group_by='division')
```

## What's Next?

With multi-league support established in v0.1.5, version 0.1.6 will focus on:
- Enhanced analytics functions for multi-league data
- Cross-league comparison tools
- Performance improvements for large datasets
- Additional interactive notebooks and examples
- More comprehensive documentation

## Resources

- **Documentation**: [maxtixador.github.io/scrapernhl](https://maxtixador.github.io/scrapernhl/)
- **API Reference**: [Multi-League API](../api-quick-reference.md)
- **Examples**: [Jupyter Notebooks](../../notebooks/)
- **Changelog**: [CHANGELOG.md](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md)

## Thank You

Thank you to everyone who uses ScraperNHL! This release represents a **major expansion** of the package's capabilities—from a single-league NHL scraper to a comprehensive multi-league platform covering 6 hockey leagues.

With this release, you can now:
- Analyze women's professional hockey (PWHL)
- Track prospects across CHL leagues (OHL, WHL, QMJHL)
- Follow AHL development players
- Compare data across multiple leagues

If you encounter any issues or have suggestions, please open an issue on [GitHub](https://github.com/maxtixador/scrapernhl/issues).

Happy scraping!

---

**Full Changelog**: [v0.1.4...v0.1.5](https://github.com/maxtixador/scrapernhl/compare/v0.1.4...v0.1.5)
