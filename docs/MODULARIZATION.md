# ScraperNHL - Modularization Guide

## ✅ Status: Phase 1 Complete (v0.1.4)

The scraper codebase has been successfully modularized while maintaining **100% backward compatibility**. The original monolithic `scraper.py` (~5000 lines) has been split into focused, single-responsibility modules.

**All tests passing** ✅ | **Original code backed up** ✅ | **Zero breaking changes** ✅ | **CLI added** ✅

## Current Structure

```
scrapernhl/
├── __init__.py                 # Public API exports
├── __main__.py                 # CLI entry point
├── cli.py                      # Command-line interface (click-based)
├── config.py                   # Constants, headers, API endpoints
├── scraper.py                  # Backward-compatible re-exports with lazy loading
├── scraper_legacy.py           # BACKUP: Original monolithic file (for safety)
│
├── core/                       # Core utilities ✅ COMPLETED
│   ├── __init__.py
│   ├── http.py                 # fetch_json, fetch_html, async variants
│   └── utils.py                # time_str_to_seconds, json_normalize, etc.
│
├── scrapers/                   # Data fetching modules ✅ COMPLETED
│   ├── __init__.py
│   ├── teams.py                # getTeamsData, scrapeTeams
│   ├── schedule.py             # getScheduleData, scrapeSchedule
│   ├── standings.py            # getStandingsData, scrapeStandings
│   ├── roster.py               # getRosterData, scrapeRoster
│   ├── stats.py                # getTeamStatsData, scrapeTeamStats
│   ├── draft.py                # Draft-related scrapers (all variants)
│   └── games.py                # getGameData, scrapePlays, goal replays
│
└── models/                     # ML models ✅ PRESENT
    ├── xgboost_xG_model1.json  # XGBoost Expected Goals model
    └── xgboost_xG_features1.pkl # Feature definitions for xG model
```

## Future Modules (Phase 2 - Not Yet Created)

```
scrapernhl/
├── pbp/                        # Play-by-play processing (PLANNED)
│   ├── __init__.py
│   ├── parsers.py              # parse_html_pbp, parse_html_shifts
│   ├── coordinates.py          # _add_normalized_coordinates
│   └── events.py               # Event-related processing
│
├── features/                   # Feature engineering (PLANNED)
│   ├── __init__.py
│   ├── xg.py                   # engineer_xg_features, predict_xg_for_pbp
│   ├── on_ice.py               # build_on_ice_long, build_on_ice_wide
│   ├── strengths.py            # build_strength_segments, etc.
│   └── shifts.py               # build_shifts_events, etc.
│
└── analysis/                   # Analytics functions (PLANNED)
    ├── __init__.py
    ├── toi.py                  # toi_by_strength, shared_toi_*
    ├── combos.py               # combos_teammates_by_strength, etc.
    ├── stats.py                # on_ice_stats_by_player_strength, etc.
    └── aggregates.py           # team_strength_aggregates, etc.
```

## Usage

### New Modular Style (Recommended)

Import directly from submodules for faster loading:

```python
from scrapernhl.scrapers.teams import scrapeTeams
from scrapernhl.scrapers.schedule import scrapeSchedule
from scrapernhl.scrapers.standings import scrapeStandings

# Fast imports, no heavy dependencies
teams = scrapeTeams()
schedule = scrapeSchedule("MTL", "20252026")
standings = scrapeStandings("2025-01-01")
```

### Legacy Style (Still Works)

The old API is fully backward compatible:

```python
from scrapernhl import scrapeTeams, scrapeSchedule, scrapeStandings

# Everything works as before
teams = scrapeTeams()
schedule = scrapeSchedule("MTL", "20252026")
```

### CLI Usage

The package includes a comprehensive command-line interface:

```bash
# View available commands
scrapernhl --help
# or
python -m scrapernhl --help

# Scrape teams
scrapernhl teams --output teams.csv

# Scrape schedule
scrapernhl schedule MTL 20252026 --format json

# Scrape standings
scrapernhl standings --output standings.parquet --format parquet

# Scrape game with xG
scrapernhl game 2024020001 --with-xg

# See all CLI examples in the documentation
```

### Testing

Quick tests from command line:

```bash
# Test import
python -c "from scrapernhl.scrapers.teams import scrapeTeams; print('✓ Works')"

# Test scraping
python -c "from scrapernhl import scrapeTeams; print(f'{len(scrapeTeams())} teams')"

# Run test suite (if available)
pytest tests/

# Run interactive demo (if available)
python demo_modular.py
```

## Benefits

1. **Faster imports**: Basic scrapers load in ~100ms (vs 2-3s previously)
2. **Better organization**: Each module has a single responsibility
3. **Easier testing**: Can test individual modules in isolation
4. **Improved docs**: Smaller files are easier to document and understand
5. **Safer refactoring**: Original code backed up in `scraper_legacy.py`
6. **Clearer dependencies**: Know exactly what each module requires
7. **CLI integration**: Command-line interface for quick data exports
8. **Lazy loading**: Heavy dependencies (xgboost) only load when needed

## Available Modules

### Scrapers (`scrapernhl.scrapers`)
| Module | Functions | Description |
|--------|-----------|-------------|
| `teams` | `scrapeTeams()` | NHL team data |
| `schedule` | `scrapeSchedule(team, season)` | Team schedule |
| `standings` | `scrapeStandings(date)` | League standings |
| `roster` | `scrapeRoster(team, season)` | Team rosters |
| `stats` | `scrapeTeamStats(team, season)` | Player statistics |
| `draft` | `scrapeDraftData(year)` | Draft picks |
| `games` | `scrapePlays(game_id)` | Play-by-play data |

### Core Utilities (`scrapernhl.core`)
| Module | Functions | Description |
|--------|-----------|-------------|
| `http` | `fetch_json()`, `fetch_html()` | HTTP fetching with retry |
| `utils` | `json_normalize()`, `time_str_to_seconds()` | Helper functions |

## Migration Status

### ✅ Completed (Phase 1)
- Core utilities (`scrapernhl.core.http`, `scrapernhl.core.utils`)
- Configuration module (`scrapernhl.config`)
- All basic scrapers (`scrapernhl.scrapers.*`)
  - teams, schedule, standings, roster, stats, draft, games
- Command-line interface (`scrapernhl.cli`)
- Backward compatibility layer (`scrapernhl.scraper`)
- Lazy loading for legacy/advanced functions
- XGBoost models for Expected Goals
- Package distribution (PyPI)
- Comprehensive documentation website

### 🔄 To Be Created (Phase 2)
- PBP parsing module (`scrapernhl.pbp`)
- Feature engineering modules (`scrapernhl.features`)
- Analysis modules (`scrapernhl.analysis`)
- Pipeline orchestration
- Additional unit tests for edge cases
- Performance benchmarking

## Testing

```bash
# Run test suite with pytest
pytest tests/ -v

# Run specific test file
pytest tests/test_modular.py -v

# Quick inline tests
python -c "from scrapernhl import scrapeTeams; print(f'{len(scrapeTeams())} teams')"

# Test modular imports
python -c "from scrapernhl.scrapers.teams import scrapeTeams; print('✓ Modular imports work')"

# Test CLI
scrapernhl --help
scrapernhl teams --output test_teams.csv
```

## Safety

- **Original code preserved**: `scraper_legacy.py` contains the full original implementation
- **Lazy loading**: Heavy dependencies only load when advanced features are used
- **100% backward compatible**: Existing code continues to work without changes

## Next Steps (Phase 2)

1. **Modularize PBP parsing** → Create `scrapernhl/pbp/` module
   - `parsers.py` - HTML parsing functions
   - `coordinates.py` - Coordinate normalization
   - `events.py` - Event processing

2. **Extract feature engineering** → Create `scrapernhl/features/` module
   - `xg.py` - Expected goals features and predictions
   - `on_ice.py` - On-ice player tracking
   - `strengths.py` - Strength state analysis
   - `shifts.py` - Shift processing

3. **Organize analysis functions** → Create `scrapernhl/analysis/` module
   - `toi.py` - Time on ice calculations
   - `combos.py` - Line combination analysis
   - `stats.py` - Player and team statistics
   - `aggregates.py` - Team-level aggregations

4. **Testing & Quality**
   - Add comprehensive unit tests for each module
   - Add integration tests for full workflows
   - Performance benchmarking and optimization
   - Code coverage reporting

5. **Documentation**
   - Update API reference with all new modules
   - Add more usage examples
   - Create migration guide for legacy code

---

**Related Files:**
- Main guide: `MODULARIZATION.md` (this file)
- Test suite: `tests/test_modular.py`
- CLI implementation: `scrapernhl/cli.py`
- Package config: `pyproject.toml`
- Documentation: `docs/` directory
