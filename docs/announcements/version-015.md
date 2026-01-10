---
title: "Version 0.1.4 Released"
date: 2026-02-01
tags: ["announcement", "release"]
categories: ["announcements"]
draft: false
---

# ANNOUNCEMENT: Version 0.1.5 Released
*Date: February 1st, 2026*

Hello, fellow hockey analytics enthusiasts!
I am thrilled to announce the release of version 0.1.5 of the scraper package!

If in the latest update (v0.1.4), we focused on usability (modularization, documentation, CLI), this time the emphasis has been on both **enhancing the core functionality** and **expanding multi-league support** to 5 professional hockey leagues!

## 🎉 Major New Features

### Multi-League API Support (NEW!)
The biggest addition to v0.1.5 is comprehensive API support for **5 hockey leagues**:
- **PWHL** (Professional Women's Hockey League)
- **AHL** (American Hockey League)
- **OHL** (Ontario Hockey League)
- **WHL** (Western Hockey League)
- **QMJHL** (Quebec Maritimes Junior Hockey League)

**Key Features:**
- **75 Total Endpoints**: 15 functions × 5 leagues
- **Unified API**: Same function names across all leagues
- **Complete Coverage**: Teams, players, stats, games, schedules, standings, rosters
- **Full Documentation**: Quick reference, comprehensive examples, interactive notebooks
- **100% Test Coverage**: All leagues verified and working

**Example Usage:**
```python
# Works identically for all 5 leagues!
from scrapernhl.pwhl import api as pwhl
from scrapernhl.ahl import api as ahl
from scrapernhl.ohl import api as ohl

# Get teams
teams = pwhl.get_teams()
stats = ahl.get_skater_stats(limit=50)
standings = ohl.get_standings()
```

**Available Functions (All Leagues):**
1. `get_teams()` - All teams
2. `get_scorebar()` - Live games & schedule
3. `get_standings()` - League standings
4. `get_skater_stats()` - Skater statistics
5. `get_goalie_stats()` - Goalie statistics
6. `get_player_profile()` - Player details
7. `get_all_players()` - All players (skaters + goalies)
8. `get_schedule()` - Full season schedule
9. `get_team_schedule()` - Team-specific schedule
10. `get_game_preview()` - Game preview data
11. `get_game_summary()` - Game summary/box score
12. `get_play_by_play()` - Play-by-play data
13. `get_game_full_data()` - Complete game data
14. `get_roster()` - Team roster
15. `get_bootstrap()` - League configuration

**Documentation:**
- [Quick Reference](../api-quick-reference.md) - Fast function lookup
- [Complete Examples](../multi-league-api-examples.md) - Comprehensive guide
- [Interactive Notebook](../../notebooks/multi_league_api_examples.ipynb) - Jupyter examples
- [Test Suite](../../test_multi_league_api.py) - Reference implementations

## 🐛 Critical Bug Fixes

### NHL Aggregation Functions - Major Fix
Fixed a **critical bug** in NHL aggregation functions that was causing incorrect calculations in:
- `toi_by_strength()` - Time on ice aggregations
- `combo_on_ice_stats()` - Combined on-ice statistics
- Zone-based aggregations
- Score-state calculations

**Impact:** This bug could have affected advanced analytics calculations. All aggregation functions now produce accurate results and have been validated with test cases.

## 🔧 Core Improvements

Summary of other improvements in this release:
1. **Migrate legacy code** → Better maintenance and organization
2. **Add player stats scraper** → Complete feature set for NHL
3. **Improve caching** → Better performance and reliability
4. **Add batch scraping** → User convenience for bulk operations
5. **Add validation** → Data reliability and error detection
6. **Standardize errors** → Better debugging and error messages
7. **Rich integration** → Enhanced developer experience with formatted output
8. **Enhance logging** → Easier issue tracking and debugging
9. **Visualization functions** → Quick insights from data
10. **Aggregation functions** → Simplified analysis (now with bug fixes!)

## 📊 League Data Coverage

With v0.1.5, you now have access to:
- **NHL**: Full play-by-play, advanced analytics, xG models
- **PWHL**: Complete API (9 teams)
- **AHL**: Complete API (24+ teams)
- **OHL**: Complete API (20+ teams)
- **WHL**: Complete API (22+ teams)
- **QMJHL**: Complete API (18+ teams)

## 🚀 Getting Started with Multi-League APIs

```python
# Install/upgrade
pip install --upgrade scrapernhl

# Basic usage - works for all leagues!
from scrapernhl.pwhl import api

# Get teams
teams = api.get_teams()

# Get player stats with pagination
stats = api.get_skater_stats(limit=100, first=0)

# Get live games
games = api.get_scorebar(days_ahead=7)

# Get standings
standings = api.get_standings(group_by='division')
```

## 📚 Resources

- **Quick Start**: [Multi-League API Quick Reference](../api-quick-reference.md)
- **Full Guide**: [Multi-League API Examples](../multi-league-api-examples.md)
- **Interactive**: [Jupyter Notebook](../../notebooks/multi_league_api_examples.ipynb)
- **Tests**: [test_multi_league_api.py](../../test_multi_league_api.py)

## 🙏 Thank You

Thank you to everyone who uses ScraperNHL! This release represents a significant expansion of the package's capabilities. We now support 6 hockey leagues (NHL + 5 HockeyTech leagues) with a unified, consistent API.

As always, feedback and contributions are welcome. If you encounter any issues or have suggestions, please open an issue on GitHub.

Happy scraping! 🏒

---

**Full Changelog**: [v0.1.4...v0.1.5](https://github.com/maxtixador/scrapernhl/compare/v0.1.4...v0.1.5)
