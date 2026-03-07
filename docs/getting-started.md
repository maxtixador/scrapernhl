# Getting Started

Install the package and start scraping hockey data in minutes.

## Installation

### From PyPI (Stable)

```bash
pip install scrapernhl
```

Or with uv:

```bash
uv add scrapernhl
```

### From GitHub (Latest)

```bash
pip install git+https://github.com/maxtixador/scrapernhl.git
```

### From Source

```bash
git clone https://github.com/maxtixador/scrapernhl.git
cd scrapernhl
pip install -e .
```

---

## Supported Leagues

| Key | League | API Style |
| --- | --- | --- |
| `nhl` | National Hockey League | Native NHL REST API |
| `ahl` | American Hockey League | HockeyTech |
| `pwhl` | Professional Women's Hockey League | HockeyTech |
| `ohl` | Ontario Hockey League | HockeyTech |
| `whl` | Western Hockey League | HockeyTech |
| `qmjhl` | Quebec Maritimes Junior Hockey League | HockeyTech |

---

## Two APIs: OOP and Functional

### OOP API — `HockeyScraper`

The main interface. Create one scraper per league:

```python
from scrapernhl import HockeyScraper

# Works for any league
scraper = HockeyScraper('ahl')

standings = scraper.standings()
pbp       = scraper.play_by_play(1027781)
stats     = scraper.player_stats(position='skaters')
schedule  = scraper.schedule()
roster    = scraper.roster(team='390')
```

### Functional API — `scrape()`

One-liner for quick lookups:

```python
from scrapernhl import scrape

pbp      = scrape('ahl', 'pbp', game_id=1027781)
stats    = scrape('ahl', 'stats', season=90, position='skaters')
schedule = scrape('nhl', 'schedule', team='MTL', season=20232024)
```

---

## Quick Examples by League

### NHL

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')

# Current standings (all 32 teams)
standings = nhl.standings()

# MTL schedule for 2023-24 season
schedule = nhl.schedule(team='MTL', season=20232024)

# MTL roster
roster = nhl.roster(team='MTL', season=20232024)

# MTL skater stats
stats = nhl.player_stats(team='MTL', season=20232024, position='skaters')

# Play-by-play (basic — JSON API only)
pbp = nhl.play_by_play(2023020001)

# Full game pipeline (HTML + JSON merged, includes on-ice players)
full_pbp = nhl.scrape_game(2023020001)

# Draft picks
draft = nhl.draft(year=2024, round='all')
```

### AHL

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Current standings
standings = ahl.standings()                   # default_season=90

# Skater stats for all teams
skaters = ahl.player_stats(season=90, position='skaters')  # 1089 players

# Goalie stats
goalies = ahl.player_stats(season=90, position='goalies')

# Schedule for all teams
schedule = ahl.schedule(season=90)

# Roster (team ID from bootstrap)
teams = ahl.teams          # list of dicts with 'id', 'name', ...
roster = ahl.roster(team=str(teams[0]['id']))

# Play-by-play
pbp = ahl.play_by_play(1027781)    # 61 events
```

### PWHL / OHL / WHL / QMJHL

All non-NHL leagues share the same method signatures:

```python
from scrapernhl import HockeyScraper

league = HockeyScraper('qmjhl')   # or 'pwhl', 'ohl', 'whl'

# Bootstrap data is auto-fetched on init
teams        = league.teams
season_id    = league.current_season_id
current_seas = league.get_current_season()

# Core data
standings = league.standings()
schedule  = league.schedule()
stats     = league.player_stats(position='skaters')
pbp       = league.play_by_play(31909)

# Roster (requires a numeric team ID)
teams     = league.get_teams()
roster    = league.roster(team=str(teams[0]['id']))
```

---

## NHL Analytics Pipeline

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')
game_id = 2023020001

# 1. Full game data (HTML + JSON merged, with on-ice player lists)
pbp    = nhl.scrape_game(game_id)
shifts = nhl.shifts(game_id)

# 2. Per-player on-ice stats (Corsi, Fenwick, TOI)
player_stats = nhl.on_ice_stats(pbp, rates=True)

# 3. Per-team strength-state aggregates
team_stats = nhl.team_strength_aggregates(pbp, rates=True)

# 5. Player-combination stats (e.g. 2-player combos for MTL)
combos = nhl.combo_on_ice_stats(pbp, focus_team='MTL', n_team=2)

# 6. Time-on-ice analysis
matrix    = nhl.seconds_matrix(pbp, shifts)
strengths = nhl.strengths_by_second(matrix)
toi       = nhl.toi_by_strength_all(matrix, strengths)
pairs     = nhl.shared_toi_teammates(matrix, strengths)
```

---

## Command-Line Interface

```bash
# All leagues are available as subcommands
python -m scrapernhl --help

# NHL commands (top-level)
python -m scrapernhl teams
python -m scrapernhl schedule MTL 20252026
python -m scrapernhl standings
python -m scrapernhl roster MTL 20252026
python -m scrapernhl stats MTL 20252026
python -m scrapernhl game 2024020001
python -m scrapernhl draft 2024

# Non-NHL leagues (subcommands: ahl, pwhl, ohl, whl, qmjhl)
python -m scrapernhl ahl standings
python -m scrapernhl ahl game 1027781
python -m scrapernhl ahl stats --season 90
python -m scrapernhl ahl roster --help
python -m scrapernhl pwhl standings

# Save output
python -m scrapernhl ahl standings -o standings.csv
python -m scrapernhl standings -f json -o standings.json
python -m scrapernhl ahl stats --season 90 -f parquet -o stats.parquet
```

---

## Accessing Bootstrap Metadata (non-NHL)

Non-NHL leagues pre-fetch configuration data on init. Use it to discover valid team and season IDs:

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Teams
for team in ahl.teams:
    print(team['id'], team['name'])

# Current season
print(ahl.current_season_id)     # e.g. '90'
season = ahl.get_current_season()

# All seasons
seasons = ahl.get_seasons('all')      # list of dicts
seasons = ahl.get_seasons('regular')  # regular season only
seasons = ahl.get_seasons('playoff')  # playoff only

# Divisions / conferences
divisions = ahl.get_divisions()
conferences = ahl.get_conferences()
```

---

## Raw Access

Inspect the URL or raw JSON before parsing:

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Get the URL that would be called
url = ahl.url_for('pbp', game_id=1027781)
print(url)

# Get raw JSON without any transformation
raw = ahl.fetch_raw('standings', season=90)
```

---

## Requirements

- Python >= 3.10
- Network access to public NHL / HockeyTech APIs
- See `pyproject.toml` for full dependency list
