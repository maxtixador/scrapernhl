---
title: "Version 0.3.x Released — Unified Client, Leaner Install & Strength-Label Fix"
date: 2026-03-07
tags: ["announcement", "release", "breaking-change"]
categories: ["announcements"]
---

# ANNOUNCEMENT: Version 0.3.0 / 0.3.1 / 0.3.2 Released
*0.3.0: March 5th, 2026 — 0.3.1: March 6th, 2026 — 0.3.2: March 7th, 2026*

Hello, fellow hockey analytics enthusiasts!

Version 0.3.0 is a full rewrite of the internals. All six leagues — NHL, AHL, PWHL, OHL, WHL, and
QMJHL — now share a **single `HockeyScraper` client** with one consistent API surface. No more
importing from `scrapernhl.ahl.scrapers` or remembering which league uses which function name. Just:

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
standings = ahl.standings()
```

This is a **breaking change** if you were importing from league-specific modules. See the migration
guide at the bottom.

Big thanks to everyone who filed issues and sent PRs since 0.1.5! Also to Claude Sonnet for
co-authoring several of the refactor commits (still not sponsored by Anthropic, unfortunately 😄). *The package was not vibecoded. Support from Claude was used during the process, but 99% of the work was done by me (Max)*. 

Make sure you follow the project on GitHub and check out the
[full changelog](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md) for details.

---

## 0.3.1 Patch — March 6, 2026

A same-day bug-fix release on top of 0.3.0. No new features or breaking changes — just four
corrections to the PBP pipeline:

| Fix | Details |
|-----|---------|
| `gameStrength` perspective | ON/OFF shift events reported strength from the **home team's** perspective even for away players. An away player killing a penalty now correctly shows `"4v5"` instead of `"5v4"`. |
| `home_strength` / `away_strength` swapped | Both columns contained the away team's and home team's values respectively (swapped) for events owned by the away team. They now always reflect the actual home and away team regardless of event ownership. |
| `parse_schedule` `IndexError` | Crashed with `IndexError` when the NHL API returned an empty sections list (e.g. a team with no scheduled games in the requested season). |
| Zone-start pandas crash | `scrape_game` raised a length-mismatch error when two faceoff events shared the exact same elapsed second in the same period. Faceoffs are now deduplicated before the zone-start merge. |

Upgrade:

```bash
pip install --upgrade scrapernhl
```
You can also follow me on Bluesky [@HabsBrain.com](https://bsky.app/profile/habsbrain.com) or
Twitter/X [@maxtixador](https://x.com/maxtixador) for updates.

---

## 0.3.2 Patch — March 7, 2026

A follow-up bug-fix release. No new features or breaking changes.

### Fix: Strength State Mirroring for the Alphabetically Second Team (PR #10)

All per-player and per-combination analytics functions (`on_ice_stats_by_player_strength()`, `toi_by_player_and_strength()`, `combo_on_ice_stats()`, `combo_on_ice_stats_both_teams()`, `team_strength_aggregates()`) now use the **focus team's perspective** for strength labels. Previously, the alphabetically second team always received mirrored labels — e.g. its power-play bucket was labelled `"4v5"` instead of `"5v4"`.

### Other fixes in 0.3.2

| Fix | Details |
|-----|--------|
| `urllib3` minimum | Bumped from `2.0.0` to `2.0.7` to prevent silent truncation of chunked HTTP responses (incomplete PBP data with no error). |
| `pandas` minimum | Updated to `>=2.2.3` for NumPy 2.x compatibility. |

Upgrade:

```bash
pip install --upgrade scrapernhl
```

---

## Major New Features

### Single Unified Client

One class, all six leagues, identical method signatures:

```python
from scrapernhl import HockeyScraper

nhl   = HockeyScraper('nhl')
ahl   = HockeyScraper('ahl')
pwhl  = HockeyScraper('pwhl')
ohl   = HockeyScraper('ohl')
whl   = HockeyScraper('whl')
qmjhl = HockeyScraper('qmjhl')
```

Every scraper exposes the same core methods:

| Method | Description |
|---|---|
| `play_by_play(game_id)` | Play-by-play events |
| `scrape_multiple_games(game_ids)` | PBP for multiple games, concatenated |
| `player_stats(season, position)` | Skater or goalie stats |
| `schedule(team, season)` | Full schedule |
| `roster(team, season)` | Team roster |
| `standings(season)` | League standings |
| `teams_by_season(season)` | Teams active in a season |
| `seasons(season_type)` | All/regular/playoff seasons |
| `url_for(data_type, **kwargs)` | Inspect the URL without fetching |
| `fetch_raw(data_type, **kwargs)` | Raw JSON (post-`json.loads()`), no parsing |
| `raw_source(endpoint, **kwargs)` | True wire payload for bronze-layer storage |

### Bootstrap Accessors (non-NHL leagues)

All non-NHL scrapers (`ahl`, `pwhl`, `ohl`, `whl`, `qmjhl`) pre-fetch bootstrap/config data on
init, so you can immediately discover valid team and season IDs:

```python
ahl = HockeyScraper('ahl')

# Properties
print(ahl.current_season_id)    # '90'
print(ahl.current_league_id)    # '6'
print(ahl.teams)                # list of dicts

# Methods
teams       = ahl.get_teams()
team        = ahl.get_team_by_id('390')
team        = ahl.get_team_by_code('MIL')
seasons     = ahl.get_seasons('all')      # 'regular' or 'playoff' also valid
season      = ahl.get_current_season()
confs       = ahl.get_conferences()
divs        = ahl.get_divisions()
```

### Play-by-Play Improvements

**`nhlify` parameter** — non-NHL PBP rows are now optionally normalized to the same column schema
as NHL PBP, making it easy to run the same downstream analysis across leagues:

```python
ahl = HockeyScraper('ahl')

pbp_clean = ahl.play_by_play(1027781)              # nhlify=True (default)
pbp_raw   = ahl.play_by_play(1027781, nhlify=False) # raw HockeyTech row layout
```

**`scrape_multiple_games()`** — scrape a list of game IDs and get one concatenated DataFrame back.
Failed games are logged and skipped rather than crashing the whole batch:

```python
pbp = ahl.scrape_multiple_games([1027779, 1027781, 1027785])
print(pbp['game_id'].value_counts())
```

### Player Profile & Bootstrap (non-NHL)

**`player_profile(player_id, season)`** returns a structured dict with `info`, `careerStats`,
`seasonStats`, `gameByGame`, and `shotLocations`:

```python
profile = ahl.player_profile(player_id, season=90)
print(profile['info'])
career = profile['careerStats']   # list of per-season dicts
```

**`bootstrap(game_id, season, page_name)`** explicitly fetches raw bootstrap/config data. Normally
you won't need this — data is auto-fetched on init — but it's useful for historical seasons or
game-specific context:

```python
bs      = ahl.bootstrap()                              # current season
game_bs = ahl.bootstrap(game_id=1027781, page_name='gamecenter')
hist_bs = ahl.bootstrap(season='88')
```

### NHL Analytics Pipeline

All NHL analytics methods are accessible directly on `HockeyScraper('nhl')`:

```python
nhl = HockeyScraper('nhl')

# Full game — HTML + JSON merged, includes on-ice player lists
pbp    = nhl.scrape_game(2023020001)
shifts = nhl.shifts(2023020001)

# Per-player on-ice stats (Corsi, Fenwick, TOI)
player_stats = nhl.on_ice_stats(pbp, rates=True)

# Per-team strength-state aggregates
team_stats = nhl.team_strength_aggregates(pbp)

# Goal replay sprite frames → tidy DataFrame
from scrapernhl import tracking_dict_to_df

replay     = nhl.goal_replay('https://wsr.nhle.com/sprites/20232024/2023020001/ev154.json')
tracking   = tracking_dict_to_df(replay)
```

`tracking_dict_to_df` is now exported at the top level so you don't need to import it from a
sub-module.

### Unified CLI

The CLI now follows a single `scrapernhl <league> <data_type> [options]` pattern for all leagues:

```bash
# Play-by-play
scrapernhl ahl pbp --game-id 1027781
scrapernhl nhl pbp --game-id 2023020001

# Standings
scrapernhl ahl standings --season 90
scrapernhl nhl standings --season 20232024

# Stats
scrapernhl ahl stats --season 90 --position skaters
scrapernhl ahl stats --season 90 --position goalies

# Schedule & roster
scrapernhl nhl schedule --team MTL --season 20232024
scrapernhl ohl roster --team 7

# Save output to disk
scrapernhl ahl standings -o standings.csv
scrapernhl ahl stats --season 90 -f parquet -o stats.parquet
```

### New Notebooks

The old league-specific notebooks (01–10) have been replaced with four focused notebooks in
`notebooks/`:

| Notebook | Contents |
|---|---|
| `01_getting_started.ipynb` | Installation, first scrape, all leagues |
| `02_nhl_data.ipynb` | Full NHL pipeline — PBP, shifts, analytics |
| `03_other_leagues.ipynb` | AHL / PWHL / OHL / WHL / QMJHL walkthrough |
| `04_advanced_features.ipynb` | On-ice stats, strength aggregates, goal replay |

`docs/api_notebook.ipynb` is a new comprehensive, runnable reference covering every public method
across all six leagues with live output.

### Functional `scrape()` One-Liner

A top-level convenience function for quick lookups without instantiating a scraper manually:

```python
from scrapernhl import scrape

pbp      = scrape('ahl', 'pbp',  game_id=1027781)
stats    = scrape('ahl', 'stats', season=90, position='skaters')
schedule = scrape('nhl', 'schedule', team='MTL', season=20232024)
```

### Bronze / Silver / Gold Pipeline Support

A new `raw_source()` method returns the **unmodified HTTP response body** (raw JSONP, JSON, or
HTML) before any parsing or transformation, along with a metadata envelope ready to be written
directly to a cloud database:

```python
scraper = HockeyScraper('ahl')
record  = scraper.raw_source('pbp', game_id=1027781)

# record = {
#   'url':          'https://lscluster.hockeytech.com/feed/...',
#   'raw_text':     'angular.callbacks._0({"SiteKit": ...})',  # raw JSONP, untouched
#   'scraped_at':   '2026-03-05T14:22:01.123456+00:00',
#   'content_type': 'application/json',
#   'status_code':  200,
#   'league':       'ahl',
#   'endpoint':     'pbp',
# }
```

All 19 endpoints are supported across all leagues — `pbp`, `stats`, `schedule`, `roster`,
`standings`, `bootstrap`, `teams`, `teams_by_season`, `seasons`, `player_profile`,
`player_game_log`, `html_pbp`, `shifts` (home + away), `standings_by_date`, `team_stats`,
`draft`, `draft_records`, `team_draft_history`.

The NHL HTML shift reports (`shifts`) return a dict with `home` and `away` sub-records, each
containing the raw HTML for their respective report.

A standalone `fetch_raw(url)` utility is also exported from `scrapernhl.core` for cases where
you're constructing URLs yourself.

`url_for()` and `fetch_raw()` now cover the same full endpoint list.

### Lineage Columns on All DataFrames

All silver-layer DataFrames now carry `scraped_at` (ISO-8601 UTC) and `league` columns
automatically — no extra code needed:

```python
df = HockeyScraper('nhl').standings(season=20252026)
print(df['scraped_at'].iloc[0])  # '2026-03-05T19:46:03.412001+00:00'
print(df['league'].iloc[0])      # 'nhl'
```

This applies to `player_stats()`, `schedule()`, `roster()`, `standings()`, `teams_by_season()`,
`seasons()`, and `scrape_teams()`. PBP already had these columns via the transform pipeline.

### Much Lighter Install

Heavy optional dependencies are now opt-in extras.
`pip install scrapernhl` installs **~50 MB** instead of the previous ~650 MB:

```bash
pip install scrapernhl              # core scraping only (~50 MB)
pip install scrapernhl[analytics]   # + xgboost, seaborn
pip install scrapernhl[notebooks]   # + jupyterlab, playwright
pip install scrapernhl[all]         # everything
```

### GitHub Actions CI

Every push and PR now runs `ruff` lint + `pytest` automatically across Python 3.10, 3.11, and
3.12. Integration tests are skipped in CI to avoid hitting live APIs on every commit.

### Test Suite

501 pytest tests across three files, all passing:

- `tests/test_client.py` — core `HockeyScraper` methods for all leagues
- `tests/test_endpoints.py` — URL construction and raw fetch for every data type
- `tests/test_all_non_nhl_leagues.py` — integration coverage for AHL, PWHL, OHL, WHL, QMJHL

---

## Critical Bug Fixes

### Lint & Import Cleanup

- Removed leftover `_config.py` module; all internal imports updated to `scrapernhl.core.http`
- Fixed a lambda loop-variable capture bug (`B023`) in `scraper_legacy.py` that could silently
  return the wrong value in certain batched call patterns
- Fixed `F821` undefined name: added missing `matrix_df` computation and `build_nhl_schedule_url`
  import to `scraper_legacy.py`
- Removed unused imports across `client.py` and `core/progress.py`
- Added `ruff` per-file ignore rules for legacy `camelCase` names in `scraper_legacy.py` and
  matrix/linear-algebra variable names (`M`, `S`, `X`, `TOI`) in `analytics.py` — these are
  domain conventions, not bugs

### Stale Test Files Removed

Five old test files that imported deleted league modules were removed rather than left as silent
failures: `test_reorganization.py`, `test_multi_league.py`, `test_pwhl_scraper.py`,
`test_ohl_scraper.py`, and two others importing the removed `scrapernhl.ahl` / `scrapernhl.whl`
module paths.

### Bootstrap Integration Test Fixed

`test_bootstrap_data_fetched` was marked `@pytest.mark.integration` and its assertion updated to
use the new lazy `_bootstrap` property correctly.

---

## Breaking Changes & Migration

All league-specific module imports have been removed. Update your code as follows:

```python
# 0.1.x (old) — no longer works
from scrapernhl.ahl.scrapers import scrapeSkaterStats, scrapeStandings
from scrapernhl.pwhl.scrapers import scrapeSchedule, scrapeTeams
from scrapernhl.nhl.scraper import scrapeGame

stats     = scrapeSkaterStats(season=90)
standings = scrapeStandings()
schedule  = scrapeSchedule(season=2024)
game      = scrapeGame(2023020001, include_tuple=True)

# 0.3.0 (new)
from scrapernhl import HockeyScraper

ahl  = HockeyScraper('ahl')
pwhl = HockeyScraper('pwhl')
nhl  = HockeyScraper('nhl')

stats     = ahl.player_stats(season=90, position='skaters')
standings = ahl.standings()
schedule  = pwhl.schedule()
game      = nhl.scrape_game(2023020001)
```

**Also removed:**
- `engineer_xg_features()` and `predict_xg()` — use `on_ice_stats()` and
  `team_strength_aggregates()` directly on the PBP DataFrame
- `visualization.py` module and all chart helpers

*Why I removed the xG model and viz helpers:*
The xG model was a fun experiment but it added a lot of complexity and dependencies for a
relatively niche use case. It also wasn't performing well enough to justify the maintenance burden. I also felt terrible for giving you a half-baked model that I knew had issues with data leakage and overfitting. I'd rather focus on providing clean, reliable data and let users build their own models on top of it. I can always eventually add a well-designed, properly validated xG model back in the future if there's demand for it. I am also thinking about writing a tutorial to build an xG models (from the most simple to relatively complex models), how to evaluate them, and how to use them in real analysis. But for now I think it's best to remove it and avoid the risk of people using it without understanding its limitations.

The visualization helpers were similarly narrow in scope and not core to the scraping mission. I
want to focus on making the core client and data retrieval as robust and user-friendly as possible,and I think these features distracted from that goal. If there's strong demand for them in the future,I can always add them back as separate optional modules or example notebooks.

---

## Updated Documentation

- **`docs/api_notebook.ipynb`** — new runnable reference notebook covering every public method
  across all six leagues with live output
- **`endpoints.md`** — new wire-format API reference documenting every URL, parameter, and
  response shape for all six leagues
- **`docs/index.md`** and **`docs/getting-started.md`** updated with 0.3.0 API examples,
  minimum Python version (3.10+), and correct install instructions
- Old references to `multi-league-scraper-reference.md` and the old league demo notebooks
  removed from nav

---

## Getting Started

Install or upgrade to 0.3.0:

```bash
pip install --upgrade scrapernhl
```

Or from GitHub for the absolute latest:

```bash
pip install git+https://github.com/maxtixador/scrapernhl.git
```

### Quick Example

```python
from scrapernhl import HockeyScraper

# Non-NHL — bootstrap data auto-fetched on init
ahl = HockeyScraper('ahl')
print(ahl.current_season_id)                    # '90'
standings = ahl.standings()
pbp       = ahl.play_by_play(1027781)
stats     = ahl.player_stats(season=90, position='skaters')

# NHL analytics pipeline
nhl          = HockeyScraper('nhl')
pbp_nhl      = nhl.scrape_game(2023020001)      # HTML + JSON merged
player_stats = nhl.on_ice_stats(pbp_nhl, rates=True)
team_stats   = nhl.team_strength_aggregates(pbp_nhl)
```

---

## What's Next?

Upcoming work will focus on:

- Adding more leagues (e.g. NCAA, European leagues) and more endpoints (e.g. injuries, transactions)
- Adding more features and transformation functions -- to support more advanced analytics use cases out of the box
- Rate-limit handling improvements and smarter retry logic
- Expanded NHL draft scraping (pick details, etc.)
- Cross-league player matching utilities (e.g. map a QMJHL prospect to their NHL draft slot)
- Performance improvements for large multi-game batch scrapes
- Continued documentation and notebook improvements

---

## Resources

- **Documentation**: [maxtixador.github.io/scrapernhl](https://maxtixador.github.io/scrapernhl/)
- **API Reference**: [api.md](../api.md)
- **Endpoints Reference**: [endpoints.md](https://github.com/maxtixador/scrapernhl/blob/master/endpoints.md)
- **Examples**: [Jupyter Notebooks](https://github.com/maxtixador/scrapernhl/tree/master/notebooks/)
- **Changelog**: [CHANGELOG.md](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md)

---

## Thank You

Thank you to everyone who uses ScraperNHL! Version 0.3.0 delivers what 0.1.x was building toward —
a single, clean, fully-tested API for all six leagues. Whether you're tracking NHL prospects through
the CHL, following women's hockey in the PWHL, or running advanced analytics on NHL play-by-play
data, it all works the same way now.

If you run into any issues or have suggestions, please open an issue on
[GitHub](https://github.com/maxtixador/scrapernhl/issues).

Now that the scraper is leaner and more robust, I will focus on using it for my own analysis and building out more advanced features. You can read my analysis on my blog [HabsBrain.com](https://habsbrain.com) and follow me on Bluesky [@HabsBrain.com](https://bsky.app/profile/habsbrain.com) or Twitter/X [@maxtixador](https://x.com/maxtixador) for updates. If you need hockey analysis consulting or custom data solutions, or just want to chat hockey analytics, feel free to reach out!

Happy scraping!

---

**Full Changelog**: [v0.1.5...v0.3.2](https://github.com/maxtixador/scrapernhl/compare/v0.1.5...v0.3.2)