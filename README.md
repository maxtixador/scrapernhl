# ScraperNHL

**Scrape and analyze hockey data from 6 leagues with one unified API.**

[![PyPI version](https://img.shields.io/pypi/v/scrapernhl)](https://pypi.org/project/scrapernhl/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://maxtixador.github.io/scrapernhl/)

ScraperNHL provides play-by-play events, player stats, schedules, rosters, and standings for the NHL, AHL, PWHL, OHL, WHL, and QMJHL — all returned as pandas DataFrames, all from the same interface.

NHL support goes further with an advanced analytics pipeline: time-on-ice matrices, shift-level analysis, on-ice shot/Corsi/Fenwick stats, and per-60 rates.

---

## Supported Leagues

| League | Key | Season format | Current season |
|--------|-----|---------------|----------------|
| National Hockey League | `nhl` | `YYYYYYYY` | `20252026` |
| American Hockey League | `ahl` | integer | `90` |
| Professional Women's Hockey League | `pwhl` | integer | `8` |
| Ontario Hockey League | `ohl` | integer | `83` |
| Western Hockey League | `whl` | integer | `289` |
| Quebec Major Junior Hockey League | `qmjhl` | integer | `211` |

---

## Installation

```bash
pip install scrapernhl
```

From source (latest dev):

```bash
git clone https://github.com/maxtixador/scrapernhl.git
cd scrapernhl
pip install -e .
```

**Requirements:** Python 3.10+, pandas, numpy, requests, beautifulsoup4, selectolax

---

## Two Ways to Use It

### 1. Functional API — one-liners for everything

```python
from scrapernhl import scrape

# Play-by-play — works for all 6 leagues
pbp = scrape('nhl',   'pbp', game_id=2023020001)
pbp = scrape('ahl',   'pbp', game_id=1027781)
pbp = scrape('qmjhl', 'pbp', game_id=31909)
pbp = scrape('ohl',   'pbp', game_id=28150)
pbp = scrape('whl',   'pbp', game_id=1022126)
pbp = scrape('pwhl',  'pbp', game_id=210)

# Player stats
skaters = scrape('ahl',   'stats', season=90, position='skaters')
goalies = scrape('ohl',   'stats', season=83, position='goalies')
skaters = scrape('nhl',   'stats', team='MTL', season=20232024, position='skaters')  # NHL needs a team

# Schedule, roster, standings
schedule  = scrape('whl',  'schedule',  season=289)
schedule  = scrape('nhl',  'schedule',  team='MTL', season=20232024)  # NHL needs a team
roster    = scrape('nhl',  'roster',    team='MTL', season=20232024)
standings = scrape('qmjhl','standings', season=211)
standings = scrape('nhl',  'standings', season=20232024)

# Teams and seasons
teams   = scrape('nhl', 'teams')              # active NHL teams
teams   = scrape('ahl', 'teams', season=90)   # AHL teams for a season
seasons = scrape('ahl', 'seasons')
```

### 2. Object-Oriented API — more control

```python
from scrapernhl import HockeyScraper

s = HockeyScraper('ahl')

pbp      = s.play_by_play(game_id=1027781)
skaters  = s.player_stats(season=90, position='skaters')
goalies  = s.player_stats(season=90, position='goalies')
schedule = s.schedule(season=90)               # team='all' by default for non-NHL
roster   = s.roster(team='390', season=90)     # team ID from bootstrap data
standing = s.standings(season=90)
teams    = s.teams_by_season(season=90)
seasons  = s.seasons('all')                    # 'all', 'regular', or 'playoff'

# Convenience aliases — same result, different names
s.scrape_pbp(game_id=1027781)
s.scrape_skaters()
s.scrape_goalies()
s.scrape_schedule()
s.scrape_roster(team='390')
s.scrape_standings()

# Scrape multiple games and get one concatenated DataFrame
df = s.scrape_multiple_games([1027781, 1027779])
```

---

## League Metadata (non-NHL)

Bootstrap data is fetched automatically when you create a non-NHL scraper. Use it to look up valid team IDs and season IDs before making other calls.

```python
s = HockeyScraper('ahl')

s.teams                          # list of team dicts
s.current_season_id              # '90'
s.get_teams(include_all=False)   # excludes the "All Teams" placeholder
s.get_team_by_id('390')          # dict with id, name, team_code, logo, ...
s.get_team_by_code('ABB')
s.get_seasons('regular')         # list of season dicts; also 'playoff', 'all'
s.get_current_season()           # dict for the current season
s.get_conferences()
s.get_divisions()
s.get_positions()
s.get_league_metadata()          # league name, short_name, code, logo
s.is_playoffs_active()           # True during playoff season
s.is_bilingual()                 # True for QMJHL (has French translations)

# Raw bootstrap dict
data = s.bootstrap(season='90', page_name='scorebar')
```

---

## NHL-Specific Methods

The following are only available on `HockeyScraper('nhl')` and raise `NotImplementedError` for other leagues.

### Play-by-Play Sources

```python
nhl = HockeyScraper('nhl')

# Three different PBP sources for the same game
json_pbp = nhl.scrape_plays(2023020001)    # JSON API — fastest
html_pbp = nhl.html_pbp(2023020001)        # HTML report — includes faceoff zone, shot type
full_pbp = nhl.scrape_game(2023020001)     # Merged pipeline (HTML + JSON) — most complete

# Raw dict from the JSON API
data = nhl.get_game_data(2023020001)

# With include_tuple=True, scrape_game returns a GameResult namedtuple
# (pbp_df, shifts_df, html_pbp_df, home_team, away_team)
result = nhl.scrape_game(2023020001, include_tuple=True)
pbp, shifts, html, home, away = result
```

### Shifts, Stats, Standings

```python
shifts = nhl.shifts(2023020001)

nhl.team_stats(team='MTL', season=20232024, session=2, goalies=False)
# session: 1=preseason, 2=regular season, 3=playoffs

nhl.standings_by_date('2024-01-15')
nhl.standings_by_date()           # defaults to Jan 1 of the previous year
```

### Teams and Draft

```python
# Three team data sources
nhl.scrape_teams(source='calendar')    # active teams from the schedule calendar
nhl.scrape_teams(source='franchise')   # franchise list with first/last season
nhl.scrape_teams(source='records')     # records API — includes logos, conference, division

# Draft
nhl.draft(year=2024, round='all')      # all rounds
nhl.draft(year=2023, round=1)          # single round
nhl.draft_records(year=2024)           # records API — more player detail
nhl.team_draft_history(franchise=1)    # all picks for one franchise (1 = NJD)
```

---

## NHL Analytics Pipeline

`scrape_game` is the starting point. It merges HTML and JSON PBP into one enriched DataFrame with on-ice player lists, strength state, zone starts, and shot coordinates.

```python
nhl = HockeyScraper('nhl')

# Step 1: Get game data
pbp    = nhl.scrape_game(2023020001)
shifts = nhl.shifts(2023020001)

# Step 2: Player-by-second matrix and strength states
matrix    = nhl.seconds_matrix(pbp, shifts)
strengths = nhl.strengths_by_second(matrix)

# Step 4: Time-on-ice by strength
toi = nhl.toi_by_strength_all(matrix, strengths)
toi = nhl.toi_by_strength_all(matrix, strengths, in_seconds=True)

# Step 5: Pairwise shared TOI
teammates = nhl.shared_toi_teammates(matrix, strengths)
opponents = nhl.shared_toi_opponents(matrix, strengths)

# Step 5: On-ice shot/goal stats
player_stats = nhl.on_ice_stats(pbp)
player_stats = nhl.on_ice_stats(pbp, include_goalies=True, rates=True)  # per-60 rates

# Combination stats (e.g. all 2-player pairs for MTL)
combos = nhl.combo_on_ice_stats(pbp, focus_team='MTL', n_team=2, m_opp=0)

# Team-level aggregates by strength state
team_agg = nhl.team_strength_aggregates(pbp, rates=True)

# On-ice player columns: choose long (tidy) or wide (numbered) format
long_df = nhl.build_on_ice_long(pbp)
wide_df = nhl.build_on_ice_wide(pbp, max_skaters=6, include_goalie=True)

# Shift events table (ON/OFF events from the shifts DataFrame)
shift_events = nhl.build_shifts_events(shifts)
```

---

## Command-Line Interface

```bash
# Play-by-play
scrapernhl ahl   game 1027781              --output game.csv
scrapernhl game  2023020001               --output nhl_game.json

# Player stats (non-NHL)
scrapernhl ahl   stats --season 90 --player-type skater  --output stats.csv
scrapernhl ohl   stats --season 83 --player-type goalie  --output goalies.json

# NHL player stats (top-level command, requires team + season)
scrapernhl stats MTL 20252026            --output mtl_skaters.csv
scrapernhl stats MTL 20252026 --goalies  --output mtl_goalies.csv

# Schedule
scrapernhl whl   schedule --season 289   --output schedule.csv
scrapernhl schedule MTL 20252026         --output nhl_schedule.csv

# Standings
scrapernhl standings                     --output standings.csv
scrapernhl qmjhl standings --season 211  --output standings.json

scrapernhl --help
scrapernhl ahl --help
```

---

## Important Behavior Notes

**NHL `player_stats` and `schedule` require a team tricode.**
The NHL API serves data per-team, not league-wide. Pass `team='MTL'`, `team='TOR'`, etc.
Non-NHL leagues default to `team='all'` for league-wide data.

**Bootstrap data is fetched on init for non-NHL leagues.**
The first call to `HockeyScraper('ahl')` makes one network request to get teams, seasons, and configuration. Subsequent calls use the cached data.

**Caching is automatic and disk-based.**

| Data type | Cache TTL |
|-----------|-----------|
| Play-by-play | None (always fresh) |
| Schedule | 1 hour |
| Player stats | 1 hour |
| Standings | 30 minutes |
| Roster | 24 hours |

---

## Running Tests

```bash
# Integration tests — require a network connection
pytest tests/test_client.py -v

# Run only a specific class
pytest tests/test_client.py::TestNHLAnalytics -v
pytest tests/test_client.py::TestPlayByPlay -v
```

717 tests cover all 6 leagues across: instantiation, bootstrap accessors, play-by-play, player stats (skaters + goalies), schedules, rosters, standings, teams, seasons, batch scraping, all NHL-specific methods, the full analytics pipeline, and the `scrape()` functional API.

---

## Project Structure

```text
scrapernhl/
├── __init__.py         # Public API: HockeyScraper, scrape()
├── client.py           # Unified HockeyScraper class (~900 lines)
├── config.py           # League configs, API keys, cache TTLs
├── urls.py             # URL builders for every league/endpoint
├── parsers.py          # Extract records from raw API responses
├── transform.py        # Normalize coordinates, events, times
├── enrichment.py       # Add team names, season metadata (non-NHL)
├── utils.py            # Rate limiter, disk cache, HTTP session
├── cli.py              # Click-based CLI
└── nhl/
    ├── scraper_legacy.py   # Full NHL pipeline: HTML PBP, shifts, TOI
    ├── analytics.py        # Advanced analytics (Corsi, scoring chances, zone starts)
    └── scrapers/           # Modular per-endpoint scrapers
```

---

## Contributing

Bug reports and pull requests are welcome at <https://github.com/maxtixador/scrapernhl>.

## License

MIT

## Author

**Max Tixador**
[@woumaxx](https://x.com/woumaxx) · [@HabsBrain.com](https://bsky.app/profile/habsbrain.com) · [maxtixador@gmail.com](mailto:maxtixador@gmail.com)
