# API Reference

Comprehensive reference for all `scrapernhl` functions, parameters, and return values.

## Table of Contents

- [HockeyScraper](#hockeyscraper)
  - [Constructor](#constructor)
  - [play\_by\_play()](#play_by_play)
  - [player\_stats()](#player_stats)
  - [schedule()](#schedule)
  - [roster()](#roster)
  - [standings()](#standings)
  - [teams\_by\_season()](#teams_by_season)
  - [seasons()](#seasons)
  - [player\_profile()](#player_profile)
  - [bootstrap()](#bootstrap)
  - [scrape\_multiple\_games()](#scrape_multiple_games)
  - [url\_for()](#url_for)
  - [fetch\_raw()](#fetch_raw)
  - [Convenience Aliases](#convenience-aliases)
- [Bootstrap Properties and Accessors](#bootstrap-properties-and-accessors)
- [NHL-Only Methods](#nhl-only-methods)
  - [scrape\_game()](#scrape_game)
  - [scrape\_plays()](#scrape_plays)
  - [html\_pbp()](#html_pbp)
  - [shifts()](#shifts)
  - [get\_game\_data()](#get_game_data)
  - [scrape\_teams()](#scrape_teams)
  - [team\_stats()](#team_stats)
  - [standings\_by\_date()](#standings_by_date)
  - [draft()](#draft)
  - [draft\_records()](#draft_records)
  - [team\_draft\_history()](#team_draft_history)
  - [goal\_replay()](#goal_replay)
- [NHL Analytics Pipeline](#nhl-analytics-pipeline)
  - [build\_shifts\_events()](#build_shifts_events)
  - [build\_on\_ice\_long()](#build_on_ice_long)
  - [build\_on\_ice\_wide()](#build_on_ice_wide)
  - [seconds\_matrix()](#seconds_matrix)
  - [strengths\_by\_second()](#strengths_by_second)
  - [toi\_by\_strength\_all()](#toi_by_strength_all)
  - [shared\_toi\_teammates()](#shared_toi_teammates)
  - [shared\_toi\_opponents()](#shared_toi_opponents)
  - [on\_ice\_stats()](#on_ice_stats)
  - [combo\_on\_ice\_stats()](#combo_on_ice_stats)
  - [team\_strength\_aggregates()](#team_strength_aggregates)
- [Functional API — scrape()](#functional-api--scrape)
- [CLI Reference](#cli-reference)
- [Legacy NHL Scraper — scraper\_legacy.py](#legacy-nhl-scraper-scraper_legacypy)
  - [Importing legacy functions](#importing-legacy-functions)
  - [Core PBP functions](#core-pbp-functions)
  - [Shift & strength pipeline](#shift--strength-pipeline)
  - [On-ice stats & TOI](#on-ice-stats--toi)
  - [Combination stats](#combination-stats)
  - [Team aggregates & expected goals](#team-aggregates--expected-goals)
- [Strength Notation](#strength-notation)

---

## HockeyScraper

The unified entry point for all six leagues. Import from the top-level package:

```python
from scrapernhl import HockeyScraper
```

---

### Constructor

```python
HockeyScraper(league: str)
```

Creates a scraper for the specified league. For non-NHL leagues, bootstrap/configuration data is fetched lazily on first access and cached in `bootstrap_data`.

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `league` | `str` | Yes | League code. One of: `'nhl'`, `'ahl'`, `'pwhl'`, `'ohl'`, `'whl'`, `'qmjhl'`. Case-insensitive. |

**Public attributes after init:**

| Attribute | Type | Description |
| --- | --- | --- |
| `league` | `str` | Normalised (lowercased) league code |
| `config` | `LeagueConfig` | League settings: `api_key`, `league_id`, `site_id`, `base_url`, `pbp_style`, `canvas_size`, rate limits |
| `bootstrap_data` | `dict \| None` | Pre-fetched league metadata (non-NHL only). Contains teams, seasons, divisions, conferences. `None` for NHL |

**Raises:** `KeyError` if the league is not supported.

**Example:**

```python
from scrapernhl import HockeyScraper

nhl  = HockeyScraper('nhl')
ahl  = HockeyScraper('ahl')
pwhl = HockeyScraper('PWHL')  # case-insensitive
```

---

### play_by_play()

```python
play_by_play(
    game_id: int,
    nhlify: bool = True,
    raw: bool = False,
    season_id: int | None = None,
    is_playoff: bool = False,
) -> pd.DataFrame | dict
```

Fetches and parses play-by-play events for a single game. Works across all six leagues. For NHL, the output comes from the JSON API; for non-NHL leagues, events are sourced from the HockeyTech feed and normalized into a shared schema.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int` | — | League-specific game ID (e.g. `2023020001` for NHL, `1027781` for AHL) |
| `nhlify` | `bool` | `True` | For HockeyTech leagues (AHL/PWHL/OHL/WHL/QMJHL): merge separate shot and goal rows that occur at the same timestamp into a single goal row, matching NHL PBP structure. Set `False` to keep raw rows |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` instead of a `DataFrame` |
| `season_id` | `int \| None` | `None` | League-specific season ID (e.g. `90` for AHL 2024-25). Used to resolve the correct overtime period length for leagues that have changed OT formats over time. Defaults to the league's `default_season` |
| `is_playoff` | `bool` | `False` | Set `True` for playoff games so overtime `game_seconds` are computed with 20-minute periods instead of the regular-season OT length |

**Returns:** `pd.DataFrame` with one row per event, or `dict` if `raw=True`.

**Key output columns (all leagues):**

| Column | Description |
| --- | --- |
| `event` | Event type string (e.g. `'shot'`, `'goal'`, `'penalty'`, `'faceoff'`) |
| `period` | Period number (4+ = overtime) |
| `time` | Clock time in the period (`MM:SS`) |
| `elapsedTime` | Elapsed time since period start (`MM:SS`) |
| `time_seconds` | Period clock as seconds from period start |
| `game_seconds` | Total elapsed game seconds |
| `x`, `y` | Ice coordinates in feet, centered at the neutral zone dot |
| `shot_distance_ft` | Distance from net in feet (shot/goal events) |
| `shot_angle_deg` | Shot angle in degrees from goal line (shot/goal events) |
| `score_home`, `score_away` | Cumulative score at the time of the event |
| `game_id` | Game ID |
| `league` | League code |
| `scraped_at` | UTC timestamp when data was fetched |

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
pbp = ahl.play_by_play(1027781)

print(pbp.shape)               # (61, 67)
print(pbp['event'].value_counts())
# shot           22
# faceoff        14
# penalty         7
# goalie_change   4
# ...

# First few events
print(pbp[['event', 'period', 'time', 'x', 'y']].head())
#            event  period  time       x       y
# 0  goalie_change       1  0:00     NaN     NaN
# 1  goalie_change       1  0:00     NaN     NaN
# 2        penalty       1  1:38     NaN     NaN
# 3           shot       1  1:46  -53.65   -3.19
# 4           shot       1  2:03    9.88  -29.32
```

**Aliases:** `scrape_pbp()`, `scrape_game_pbp()`

---

### player_stats()

```python
player_stats(
    season: int | None = None,
    team: str = 'all',
    position: Literal['skaters', 'goalies'] = 'skaters',
    raw: bool = False,
    **filters,
) -> pd.DataFrame | dict
```

Fetches player statistics for a season. Supports skaters and goalies for all six leagues.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `season` | `int \| None` | `None` | League-specific season ID (e.g. `20232024` for NHL, `90` for AHL). Defaults to `config.default_season` |
| `team` | `str` | `'all'` | Filter by team. Use `'all'` for every team, or a team abbreviation / numeric ID (e.g. `'MTL'` for NHL, `'5'` for AHL) |
| `position` | `str` | `'skaters'` | `'skaters'` for forward/defence stats, `'goalies'` for goaltender stats |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` |
| `**filters` | | | Additional query parameters forwarded to the API (league-dependent) |

**Returns:** `pd.DataFrame` or `dict` if `raw=True`.

**Key output columns (non-NHL skaters):**

| Column | Description |
| --- | --- |
| `player_id` | HockeyTech player ID |
| `name` | Full player name |
| `position` | Position code |
| `teamCode` | Team abbreviation |
| `GP` | Games played |
| `G` | Goals |
| `A` | Assists |
| `PTS` | Points |
| `PTS/GP` | Points per game |
| `+/-` | Plus/minus |
| `PIM` | Penalty minutes |
| `PPG`, `SHG` | Power-play / shorthanded goals |
| `season`, `league` | Season ID and league code |
| `seasonName` | Human-readable season name (e.g. `'2024-25'`) |

**Notes:**

- For NHL, `team` must be a valid tricode (e.g. `'MTL'`) — the NHL stats endpoint is per-team only. To get league-wide skater stats, iterate over all teams.
- Non-NHL results are league-wide when `team='all'`.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# All AHL skaters
skaters = ahl.player_stats(season=90, position='skaters')
print(skaters.shape)   # (1089, 32)
print(skaters[['name', 'GP', 'G', 'A', 'PTS']].head(3))
#                 name  GP   G   A  PTS
# 0    Laurent Dauphin  49  15  41   56
# 1    Jakob Pelletier  45  20  33   53
# 2  Alex Barré-Boulet  49  17  35   52

# AHL goalies
goalies = ahl.player_stats(season=90, position='goalies')

# NHL — per-team only
nhl = HockeyScraper('nhl')
mtl_skaters = nhl.player_stats(team='MTL', season=20232024, position='skaters')
```

**Aliases:** `scrape_skaters()` (calls with `position='skaters'`), `scrape_goalies()` (calls with `position='goalies'`)

---

### schedule()

```python
schedule(
    team: str = 'all',
    season: int | None = None,
    raw: bool = False,
    **filters,
) -> pd.DataFrame | dict
```

Fetches the game schedule. Returns every game in the season for the given team, or all teams when `team='all'`.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `team` | `str` | `'all'` | Team filter. Use `'all'` for the full league schedule, or a team abbreviation / numeric ID |
| `season` | `int \| None` | `None` | Season ID. Defaults to `config.default_season` |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` |
| `**filters` | | | Additional query parameters forwarded to the API |

**Returns:** `pd.DataFrame` or `dict` if `raw=True`.

**Key output columns (non-NHL):**

| Column | Description |
| --- | --- |
| `gameId` | Game ID |
| `date` | Game date string |
| `homeCity`, `awayCity` | City names for home and away teams |
| `homeScore`, `awayScore` | Final scores (blank if not yet played) |
| `gameStatus` | Game status (e.g. `'Final'`, `'Scheduled'`) |
| `venue` | Arena name |
| `homeTeamName`, `awayTeamName` | Full team names (added by enrichment) |
| `season`, `league` | Season ID and league code |

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Full AHL schedule
schedule = ahl.schedule(season=90)
print(len(schedule))    # ~1400 games

# Specific team
# First, find team ID from bootstrap
teams = ahl.get_teams()
print([(t['id'], t['name']) for t in teams[:3]])

# NHL schedule
nhl = HockeyScraper('nhl')
mtl = nhl.schedule(team='MTL', season=20232024)
print(mtl.shape)        # (82, ...)
```

**Alias:** `scrape_schedule()`

---

### roster()

```python
roster(
    team: str,
    season: int | None = None,
    raw: bool = False,
) -> pd.DataFrame | dict
```

Fetches the player roster for a specific team.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `team` | `str` | — | **Required.** Team identifier. For NHL: tricode (e.g. `'MTL'`). For non-NHL: numeric team ID string (e.g. `'390'`). Non-numeric codes are automatically resolved to numeric IDs via bootstrap data |
| `season` | `int \| None` | `None` | Season ID. Defaults to `config.default_season` |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` |

**Returns:** `pd.DataFrame` or `dict` if `raw=True`.

**Key output columns (non-NHL):**

| Column | Description |
| --- | --- |
| `player_id` | HockeyTech player ID |
| `name` | Full player name |
| `firstName`, `lastName` | Split name components |
| `position` | Position code |
| `tp_jersey_number` | Jersey number |
| `birthdate` | Date of birth |
| `h`, `w` | Height (cm) and weight (lbs) |
| `height_cm` | Parsed height in centimeters |
| `birthCity`, `birthCountry` | Birthplace |
| `shoots` / `catches` | Shooting/catching hand (skater/goalie) |
| `teamId`, `teamName`, `teamCode` | Team metadata |
| `season`, `league` | Season and league context |

**Notes:**

- For non-NHL leagues, `team` must be a numeric ID string. Retrieve valid IDs from `scraper.get_teams()`.
- Team code abbreviations (e.g. `'Rou'` for Rouyn-Noranda in QMJHL) are automatically resolved to numeric IDs when passed to this method.

**Example:**

```python
from scrapernhl import HockeyScraper

# OHL roster
ohl = HockeyScraper('ohl')
teams = ohl.get_teams()
print(teams[0])  # {'id': '7', 'name': 'Barrie Colts', ...}

roster = ohl.roster(team='7')
print(roster[['name', 'position', 'tp_jersey_number']].head(5))
#               name position tp_jersey_number
# 0  Nicholas Desiderio       LW               11
# 1     William Schneid       RW               29
# ...

# NHL roster
nhl = HockeyScraper('nhl')
mtl_roster = nhl.roster(team='MTL', season=20232024)
```

**Alias:** `scrape_roster()`

---

### standings()

```python
standings(
    season: int | None = None,
    raw: bool = False,
    **filters,
) -> pd.DataFrame | dict
```

Fetches current or historical league standings.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `season` | `int \| None` | `None` | Season ID. Defaults to `config.default_season` |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` |
| `**filters` | | | Additional query parameters (e.g. `context='home'` for home standings on HockeyTech leagues) |

**Returns:** `pd.DataFrame` or `dict` if `raw=True`.

**Key output columns (non-NHL):**

| Column | Description |
| --- | --- |
| `teamName` | Full team name |
| `teamId` | Numeric team ID |
| `team_code` | Team abbreviation |
| `wins` | Wins |
| `losses` | Losses |
| `ot_losses` | Overtime losses |
| `points` | Points |
| `games_played` | Games played |
| `goals_for`, `goals_against` | Goals for / against |
| `percentage` | Points percentage |
| `regulation_wins` | Regulation wins (ROW/ROW equivalent) |
| `streak` | Current streak |
| `past_10` | Last 10 games record |
| `rank` | Division rank |
| `overall_rank` | League-wide rank |
| `season`, `league`, `seasonName` | Season and league metadata |

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
standings = ahl.standings()
print(standings.shape)   # (32, 28)
print(standings[['teamName', 'wins', 'losses', 'points']].head(3))
#                           teamName  wins  losses  points
# 0               Providence Bruins    38      10      77
# 1  Wilkes-Barre/Scranton Penguins    35      13      75
# 2              Charlotte Checkers    29      17      61

# Filter by context (HockeyTech leagues)
home_standings = ahl.standings(context='home')
away_standings = ahl.standings(context='away')
```

**Alias:** `scrape_standings()`

---

### teams_by_season()

```python
teams_by_season(season: int | None = None, raw: bool = False) -> pd.DataFrame | dict | list
```

Returns a DataFrame of teams that participated in a specific season. For NHL, pulls from the standings endpoint. For non-NHL, reads from bootstrap data.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `season` | `int \| None` | `None` | Season ID. Defaults to `config.default_season` |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response (NHL: `dict`, non-NHL: `list`) |

**Returns:** `pd.DataFrame` with columns `season` and `league` always present, or raw `dict`/`list` if `raw=True`.

**Example:**

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')
teams = nhl.teams_by_season(season=20232024)
print(teams.shape)   # (32, ...)

ahl = HockeyScraper('ahl')
teams = ahl.teams_by_season(season=90)
print(teams[['name', 'id', 'season']].head(3))
```

---

### seasons()

```python
seasons(season_type: Literal['all', 'regular', 'playoff'] = 'all', raw: bool = False) -> pd.DataFrame | dict | list
```

Returns available seasons for the league. For NHL, fetches from the NHL seasons endpoint. For non-NHL, reads from bootstrap data (and discovers hidden playoff/preseason IDs for QMJHL and WHL by probing ID gaps).

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `season_type` | `str` | `'all'` | Which seasons to return: `'all'`, `'regular'`, or `'playoff'` |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` or `list` |

**Returns:** `pd.DataFrame` with `league` column always present, or raw `dict`/`list` if `raw=True`.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
all_seasons = ahl.seasons('all')
regular     = ahl.seasons('regular')
playoffs    = ahl.seasons('playoff')

print(all_seasons[['id', 'name']].tail(5))
```

---

### player_profile()

```python
player_profile(
    player_id: int,
    season: int | None = None,
    stats_type: str = 'standard',
    raw: bool = False,
) -> dict
```

Fetches a player's full profile page from the HockeyTech API. **Non-NHL leagues only.** For NHL player data, use `url_for('player_profile', player_id=...)` or `fetch_raw('player_profile', player_id=...)`.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `player_id` | `int` | — | HockeyTech player ID (obtain from `player_stats()` `player_id` column) |
| `season` | `int \| None` | `None` | Season ID. Defaults to `config.default_season` |
| `stats_type` | `str` | `'standard'` | `'standard'` for full stats profile, `'bio'` for biographical data only |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` |

**Returns:** `dict` with keys:

| Key | Description |
| --- | --- |
| `info` | Bio data (name, position, birthdate, height, weight, etc.) |
| `careerStats` | Career stats aggregated by season |
| `seasonStats` | Stats for the requested season only |
| `gameByGame` | Game-by-game log for the season |
| `shotLocations` | Shot location data (if available for the league) |

**Raises:** `NotImplementedError` if called on an NHL scraper.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Get player ID first
stats = ahl.player_stats(season=90)
player_id = int(stats.iloc[0]['player_id'])

# Fetch full profile
profile = ahl.player_profile(player_id, season=90)
print(profile['info'])          # bio dict
print(profile['careerStats'])   # list of season dicts
```

---

### bootstrap()

```python
bootstrap(
    game_id: int | None = None,
    season: str = 'latest',
    page_name: str = 'scorebar',
    **filters,
) -> dict
```

Explicitly fetches raw bootstrap/configuration data from the HockeyTech API. **Non-NHL only.** Useful when you need game-specific configuration data or want to inspect the full raw metadata structure.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int \| None` | `None` | Optional game ID for game-specific configuration context |
| `season` | `str` | `'latest'` | Season to fetch metadata for. `'latest'` returns current season data |
| `page_name` | `str` | `'scorebar'` | Page context for the bootstrap request. Common values: `'scorebar'`, `'gamecenter'`, `'roster'` |
| `**filters` | | | Additional query parameters forwarded to the API |

**Returns:** `dict` — the full raw bootstrap payload, which includes the league's configuration subtree.

**Raises:** `NotImplementedError` if called on an NHL scraper.

**Notes:**
Bootstrap data is **automatically fetched on init** for non-NHL leagues and stored in `scraper.bootstrap_data`. Only call this method explicitly when you need a different season or page context.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Same data as auto-fetched on init
bootstrap = ahl.bootstrap()

# Game-specific context
bootstrap = ahl.bootstrap(game_id=1027781, page_name='gamecenter')

# Historical season
bootstrap = ahl.bootstrap(season='88')

print(bootstrap['current_season_id'])  # '90'
print(len(bootstrap['teamsNoAll']))    # 32
```

---

### scrape_multiple_games()

```python
scrape_multiple_games(game_ids: list[int], **kwargs) -> pd.DataFrame
```

Scrapes PBP data for multiple games and concatenates the results into a single DataFrame. Failed individual games are logged to stdout and skipped.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_ids` | `list[int]` | — | List of game IDs to scrape |
| `**kwargs` | | | Additional keyword arguments forwarded to `play_by_play()` (e.g. `nhlify`, `season_id`, `is_playoff`) |

**Returns:** `pd.DataFrame` — concatenated PBP rows from all successful games. Empty `DataFrame` if all games fail.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
pbp = ahl.scrape_multiple_games([1027779, 1027781, 1027785])
print(pbp['game_id'].value_counts())

nhl = HockeyScraper('nhl')
pbp = nhl.scrape_multiple_games([2023020001, 2023020002])
```

---

### url_for()

```python
url_for(data_type: str, **kwargs) -> str
```

Returns the URL that would be fetched for a given data type and parameters, without making any HTTP request. Use this for debugging, inspecting raw endpoints, or building `curl` commands.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `data_type` | `str` | Endpoint type. One of: `'pbp'`, `'stats'`, `'schedule'`, `'roster'`, `'standings'`, `'bootstrap'`, `'scorebar'`, `'player_profile'`, `'player_game_log'` (NHL only) |
| `**kwargs` | | Same keyword arguments as the corresponding scraper method |

**Returns:** `str` — the fully-constructed URL.

**Example:**

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')
print(nhl.url_for('pbp', game_id=2023020001))
# https://api-web.nhle.com/v1/gamecenter/2023020001/play-by-play

ahl = HockeyScraper('ahl')
print(ahl.url_for('standings', season=90))
print(ahl.url_for('player_profile', player_id=12345, season=90))
```

---

### fetch_raw()

```python
fetch_raw(data_type: str, **kwargs) -> dict
```

Fetches the unprocessed API response for a given data type, bypassing all parsing and transformation. Caching and rate limiting still apply.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `data_type` | `str` | Endpoint type. Same options as `url_for()` |
| `**kwargs` | | Same keyword arguments as the corresponding scraper method |

**Returns:** `dict` — raw JSON as returned by the API.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')
raw = ahl.fetch_raw('standings', season=90)
print(raw.keys())

raw_pbp = ahl.fetch_raw('pbp', game_id=1027781)
```

---

### Convenience Aliases

The following methods are direct aliases for the primary methods above:

| Alias | Equivalent call |
| --- | --- |
| `scrape_pbp(game_id, **kwargs)` | `play_by_play(game_id, **kwargs)` |
| `scrape_game_pbp(game_id, **kwargs)` | `play_by_play(game_id, **kwargs)` |
| `scrape_schedule(team, season, **kwargs)` | `schedule(team, season, **kwargs)` |
| `scrape_roster(team, season)` | `roster(team, season)` |
| `scrape_standings(season, **kwargs)` | `standings(season, **kwargs)` |
| `scrape_skaters(season, team, **kwargs)` | `player_stats(season, team, position='skaters', **kwargs)` |
| `scrape_goalies(season, team, **kwargs)` | `player_stats(season, team, position='goalies', **kwargs)` |

---

## Bootstrap Properties and Accessors

Available on all non-NHL `HockeyScraper` instances. NHL calls raise `NotImplementedError`.

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `teams` | `list[dict]` | All teams, excluding the "All Teams" aggregate entry |
| `current_season_id` | `str \| None` | Current season ID as a string |
| `current_league_id` | `str \| None` | Current league ID as a string |

### Accessor Methods

```python
get_current_season_id() -> str | None
```

Returns the current season ID string.

```python
get_current_league_id() -> str | None
```

Returns the current league ID string.

```python
get_teams(include_all: bool = False) -> list[dict]
```

Returns the teams list. When `include_all=True`, includes the synthetic "All Teams" entry used in API filter parameters.

```python
get_team_by_id(team_id: str | int) -> dict | None
```

Looks up a team by its numeric ID. Returns `None` if not found.

```python
get_team_by_code(team_code: str) -> dict | None
```

Looks up a team by abbreviation code (case-insensitive). Returns `None` if not found.

```python
get_seasons(season_type: Literal['all', 'regular', 'playoff'] = 'all') -> list[dict]
```

Returns the list of seasons for the given type. For QMJHL and WHL, playoff and preseason IDs are discovered by probing ID gaps between regular seasons.

```python
get_current_season() -> dict | None
```

Returns the current season metadata dict, or `None` if not found in the seasons list.

```python
get_conferences(include_all: bool = True) -> list[dict]
```

Returns conferences. When `include_all=True`, includes the "All Conferences" aggregate entry.

```python
get_divisions(include_all: bool = True) -> list[dict]
```

Returns divisions. When `include_all=True`, includes the "All Divisions" aggregate entry.

```python
get_positions(normalize: bool = True) -> list[dict]
```

Returns position list. When `normalize=True`, normalises PWHL "Defenders" → "Defencemen".

```python
get_goalie_filters() -> list[dict]
```

Returns the goalie qualification filter options (e.g. `'qualified'`, `'all'`).

```python
get_first_season_year() -> str | None
```

Returns the league's inaugural season year as a string.

```python
is_bilingual() -> bool
```

Returns `True` if the league supports French (`'fr'` is in `svfLanguages`). Currently `True` for QMJHL.

```python
get_league_metadata() -> dict
```

Returns the league's metadata dict containing `id`, `name`, `short_name`, `code`, `logo_image`.

```python
get_config_flag(key: str, default=False) -> Any
```

Reads a boolean or string flag from the league's `svfConfig` block.

```python
get_player_no_pic_override() -> str | None
```

Returns the URL for the default player image when no headshot is available.

```python
is_playoffs_active() -> bool
```

Returns `True` if the current season has active playoff data in bootstrap.

```python
get_show_expanded_goalies() -> bool
```

Returns `True` if the league config enables the expanded goalie stats option.

**Example:**

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Quick lookups
print(ahl.current_season_id)       # '90'
print(ahl.is_bilingual())          # False

# Teams
for team in ahl.teams:
    print(team['id'], team['name'])

# Find a specific team
team = ahl.get_team_by_id('390')
print(team)   # {'id': '390', 'name': 'San Diego Gulls', ...}

# Seasons
regular_seasons = ahl.get_seasons('regular')
current = ahl.get_current_season()
print(current['name'])             # '2024-25'
```

---

## NHL-Only Methods

These methods raise `NotImplementedError` when called on a non-NHL scraper.

---

### scrape_game()

```python
scrape_game(
    game_id: int | str,
    add_goal_replay: bool = False,
    include_tuple: bool = False,
) -> pd.DataFrame
```

Full NHL game pipeline. Combines data from three sources:

1. **HTML play-by-play report** — event descriptions, on-ice player names
2. **HTML shift reports** (home + visitor) — player shift times, on-ice player IDs
3. **JSON API** — event coordinates, shot types, player IDs

The three sources are merged on game time to produce a single enriched DataFrame with on-ice players, strength states, and zone start qualifiers.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int \| str` | — | NHL game ID (e.g. `2023020001`) |
| `add_goal_replay` | `bool` | `False` | If `True`, fetch goal replay video URLs from PPT. Adds extra network requests |
| `include_tuple` | `bool` | `False` | If `True`, return a named tuple `(pbp, shifts, html_pbp, home_team, away_team)` instead of just the PBP DataFrame |

**Returns:** `pd.DataFrame` (or 5-tuple if `include_tuple=True`).

**Key output columns:**

| Column | Description |
| --- | --- |
| `Event` | HTML event type string |
| `Description` | Full HTML event description |
| `Per` | Period |
| `Time:Elapsed Game` | Elapsed game time |
| `strength`, `gameStrength` | Strength state (e.g. `'5v5'`, `'5v4'`) |
| `detailedGameStrength` | Detailed strength with empty-net notation (e.g. `'5v6*'`) |
| `home_on_ice`, `away_on_ice` | Lists of on-ice player names |
| `home_on_id`, `away_on_id` | Lists of on-ice player IDs |
| `n_home_skaters`, `n_away_skaters` | Skater counts |
| `pulled_home`, `pulled_away` | Boolean — goalie pulled |
| `xCoord`, `yCoord` | API shot coordinates |
| `homeTeam`, `awayTeam` | Team tricodes |
| `gameId`, `gameDate` | Game metadata |
| `start_zone` | Zone where the event started (from shift data) |

**Example:**

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')

# Full enriched PBP
pbp = nhl.scrape_game(2023020001)
print(pbp.shape)          # (1817, ~100 columns)
print(pbp.columns.tolist())

# Include metadata tuple
result = nhl.scrape_game(2023020001, include_tuple=True)
pbp, shifts, html_pbp, home_team, away_team = result
print(f"{away_team} @ {home_team}")
```

---

### scrape_plays()

```python
scrape_plays(
    game_id: int | str,
    add_goal_replay: bool = False,
) -> pd.DataFrame
```

Fetches NHL play-by-play from the **JSON API only** (no HTML report). Lighter-weight than `scrape_game()` but lacks on-ice player lists and strength states.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int \| str` | — | NHL game ID |
| `add_goal_replay` | `bool` | `False` | If `True`, enrich goal rows with replay video URLs |

**Returns:** `pd.DataFrame`.

**Example:**

```python
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_plays(2023020001)
print(pbp.shape)   # (328, ~20 columns)
```

---

### html_pbp()

```python
html_pbp(
    game_id: int | str,
    raw: bool = False,
    return_raw: bool = False,
) -> pd.DataFrame | dict | tuple
```

Scrapes and parses the NHL HTML play-by-play report from `nhl.com`. Returns the event table with on-ice player names from the official game report.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int \| str` | — | NHL game ID |
| `raw` | `bool` | `False` | If `True`, return the unprocessed bronze-layer `dict` (`{'data': html_str, 'urls', 'game_id', 'scraped_on', 'source'}`) |
| `return_raw` | `bool` | `False` | If `True`, return `(DataFrame, raw_dict)` tuple where `raw_dict` contains the raw parsed HTML structure |

**Returns:** `pd.DataFrame`, or raw `dict` if `raw=True`, or `(pd.DataFrame, dict)` tuple if `return_raw=True`.

**Example:**

```python
nhl = HockeyScraper('nhl')
df = nhl.html_pbp(2023020001)

# With raw HTML parse tree
df, raw = nhl.html_pbp(2023020001, return_raw=True)
```

---

### shifts()

```python
shifts(game_id: int | str, raw: bool = False) -> pd.DataFrame | dict
```

Scrapes NHL HTML shift reports for both the home and visitor team from `nhl.com`. Returns all individual player shifts with start/end times.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int \| str` | — | NHL game ID |
| `raw` | `bool` | `False` | If `True`, return the unprocessed bronze-layer `dict` (`{'home': html_str, 'away': html_str, 'urls', 'game_id', 'scraped_on', 'source'}`) |

**Returns:** `pd.DataFrame` with one row per player shift, or raw `dict` if `raw=True`.

**Key output columns:**

| Column | Description |
| --- | --- |
| `player_id` | NHL player ID |
| `player_name` | Player full name |
| `team` | Team tricode |
| `period` | Period number |
| `shift_start`, `shift_end` | Shift start/end time (`MM:SS`) |
| `shift_start_sec`, `shift_end_sec` | Shift times in seconds |
| `duration` | Shift duration (`MM:SS`) |

**Example:**

```python
nhl = HockeyScraper('nhl')
shifts = nhl.shifts(2023020001)
print(shifts.shape)    # (~500 shifts per game)
print(shifts[['player_name', 'team', 'period', 'shift_start', 'shift_end']].head())
```

---

### get_game_data()

```python
get_game_data(
    game_id: int | str,
    add_goal_replay: bool = False,
) -> dict
```

Returns the raw NHL JSON API response for a game, with plays already extracted into a list. Useful for inspection or custom parsing.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `game_id` | `int \| str` | — | NHL game ID |
| `add_goal_replay` | `bool` | `False` | If `True`, enrich goal plays with replay URLs |

**Returns:** `dict` — full API response with `plays` list.

---

### scrape_teams()

```python
scrape_teams(source: str = 'calendar', raw: bool = False) -> pd.DataFrame | dict
```

Returns NHL team data from one of three public NHL endpoints. **NHL only.**

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `source` | `str` | `'calendar'` | Data source. One of: `'calendar'` (active teams from the schedule), `'franchise'` (franchise list with first/last season from stats REST API), `'records'` (full details with logos from records API) |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `dict` |

**Returns:** `pd.DataFrame` with `league` and `source` columns always present, or raw `dict` if `raw=True`.

**Raises:** `ValueError` for invalid `source`. `NotImplementedError` for non-NHL leagues.

**Example:**

```python
nhl = HockeyScraper('nhl')

# Active teams (default)
teams = nhl.scrape_teams()

# Full franchise history
franchises = nhl.scrape_teams(source='franchise')

# Records endpoint (includes logos)
records = nhl.scrape_teams(source='records')
```

---

### team_stats()

```python
team_stats(
    team: str,
    season: int | str | None = None,
    session: int | str = 2,
    goalies: bool = False,
    raw: bool = False,
) -> pd.DataFrame | list
```

Returns per-player statistics for one NHL team from the NHL stats REST API.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `team` | `str` | — | Team tricode (e.g. `'MTL'`) |
| `season` | `int \| str \| None` | `None` | Season ID (e.g. `20232024`). Defaults to current season |
| `session` | `int \| str` | `2` | Session type: `1` = pre-season, `2` = regular season, `3` = playoffs |
| `goalies` | `bool` | `False` | If `True`, return goalie stats; otherwise skater stats |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `list` |

**Returns:** `pd.DataFrame`, or raw `list` if `raw=True`.

**Example:**

```python
nhl = HockeyScraper('nhl')

# MTL skaters — regular season
skaters = nhl.team_stats(team='MTL', season=20232024, session=2)

# MTL goalies — playoffs
goalies = nhl.team_stats(team='MTL', season=20232024, session=3, goalies=True)
```

---

### standings_by_date()

```python
standings_by_date(date: str | None = None, raw: bool = False) -> pd.DataFrame | list
```

Returns NHL standings for a specific calendar date.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `date` | `str \| None` | `None` | Date in `'YYYY-MM-DD'` format. Defaults to January 1st of the previous year |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `list` |

**Returns:** `pd.DataFrame`, or raw `list` if `raw=True`.

**Example:**

```python
nhl = HockeyScraper('nhl')
standings = nhl.standings_by_date('2024-01-15')
```

---

### draft()

```python
draft(
    year: int | str = 2024,
    round: int | str = 'all',
    raw: bool = False,
) -> pd.DataFrame | list
```

Returns NHL draft picks from the draft picks API.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `year` | `int \| str` | `2024` | Draft year |
| `round` | `int \| str` | `'all'` | Round number (1–7), or `'all'` for every round |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `list` |

**Returns:** `pd.DataFrame` with one row per draft pick, or raw `list` if `raw=True`.

**Example:**

```python
nhl = HockeyScraper('nhl')

# All picks
draft = nhl.draft(year=2024, round='all')

# First round only
first_round = nhl.draft(year=2023, round=1)
```

---

### draft_records()

```python
draft_records(year: int | str = 2025, raw: bool = False) -> pd.DataFrame | list
```

Returns draft records from the NHL Records API. Includes more detailed player and team information than `draft()`.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `year` | `int \| str` | `2025` | Draft year |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `list` |

**Returns:** `pd.DataFrame`, or raw `list` if `raw=True`.

---

### team_draft_history()

```python
team_draft_history(franchise: int | str = 1, raw: bool = False) -> pd.DataFrame | list
```

Returns the complete draft history for a specific franchise.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `franchise` | `int \| str` | `1` | NHL franchise ID (e.g. `1` for New Jersey Devils, `20` for Montreal Canadiens) |
| `raw` | `bool` | `False` | If `True`, return the unprocessed API response `list` |

**Returns:** `pd.DataFrame` with every draft pick ever made by the franchise, or raw `list` if `raw=True`.

**Example:**

```python
nhl = HockeyScraper('nhl')
mtl_history = nhl.team_draft_history(franchise=20)
```

---

### goal_replay()

```python
goal_replay(json_url: str) -> list[dict]
```

Fetches goal replay video data from a PPT replay URL. The URL comes from the `pptReplayUrl` column in PBP DataFrames returned by `scrape_plays()` or `scrape_game()`.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `json_url` | `str` | The `pptReplayUrl` value from a goal play row |

**Returns:** `list[dict]` — goal replay data objects.

---

## NHL Analytics Pipeline

All analytics methods are **NHL-only** and raise `NotImplementedError` for other leagues. The recommended pipeline is:

```text
scrape_game() → on_ice_stats() / combo_on_ice_stats() / team_strength_aggregates()
```

For TOI analysis:

```text
scrape_game() + shifts() → seconds_matrix() → strengths_by_second()
                         → toi_by_strength_all() / shared_toi_teammates() / shared_toi_opponents()
```

---

### build_shifts_events()

```python
build_shifts_events(shifts: pd.DataFrame) -> pd.DataFrame
```

Converts shift data from `shifts()` into a tidy ON/OFF event table. Each shift becomes two rows: one `SHIFT_START` and one `SHIFT_END`. Used internally by the analytics pipeline.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `shifts` | `pd.DataFrame` | Shift DataFrame from `shifts()` |

**Returns:** `pd.DataFrame` with one row per shift boundary event.

---

### build_on_ice_long()

```python
build_on_ice_long(df: pd.DataFrame) -> pd.DataFrame
```

Converts the list-based `home_on_ice` / `away_on_ice` columns in a PBP DataFrame into a tidy long-format table where each row represents one player at one event.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `df` | `pd.DataFrame` | PBP DataFrame from `scrape_game()` |

**Returns:** `pd.DataFrame` — long-format on-ice table (no numbered wide columns).

**Example:**

```python
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2023020001)
long = nhl.build_on_ice_long(pbp)
print(long.columns.tolist())
```

---

### build_on_ice_wide()

```python
build_on_ice_wide(
    df: pd.DataFrame,
    max_skaters: int = 6,
    include_goalie: bool = True,
    drop_list_cols: bool = False,
) -> pd.DataFrame
```

Expands the list-based on-ice columns into named wide columns (`home_skater_1` … `home_skater_N`, `home_goalie`, and equivalent for away).

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `df` | `pd.DataFrame` | — | PBP DataFrame from `scrape_game()` |
| `max_skaters` | `int` | `6` | Maximum number of skater columns per team |
| `include_goalie` | `bool` | `True` | Whether to add goalie columns |
| `drop_list_cols` | `bool` | `False` | If `True`, drop the original list columns after expansion |

**Returns:** `pd.DataFrame` — input with additional `home_skater_1..N`, `away_skater_1..N`, and goalie columns.

---

### seconds_matrix()

```python
seconds_matrix(df: pd.DataFrame, shifts: pd.DataFrame) -> pd.DataFrame
```

Creates a boolean matrix where rows are players and columns are game seconds. A `True` value indicates that player was on the ice during that second. Used as the base for all TOI computations.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `df` | `pd.DataFrame` | PBP DataFrame from `scrape_game()` |
| `shifts` | `pd.DataFrame` | Shifts DataFrame from `shifts()` |

**Returns:** `pd.DataFrame` — matrix indexed by player with game-second columns.

---

### strengths_by_second()

```python
strengths_by_second(matrix_df: pd.DataFrame) -> pd.DataFrame
```

Derives the strength state (skater count for each team) for every second of the game from the on-ice matrix.

**Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| `matrix_df` | `pd.DataFrame` | Output from `seconds_matrix()` |

**Returns:** `pd.DataFrame` — per-second table with home/away skater counts and strength label.

---

### toi_by_strength_all()

```python
toi_by_strength_all(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    in_seconds: bool = False,
) -> pd.DataFrame
```

Computes total time-on-ice for every player broken down by strength state.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix_df` | `pd.DataFrame` | — | Output from `seconds_matrix()` |
| `strengths_df` | `pd.DataFrame` | — | Output from `strengths_by_second()` |
| `in_seconds` | `bool` | `False` | If `True`, return TOI in seconds; default is minutes |

**Returns:** `pd.DataFrame` — per-player, per-strength-state TOI.

**Example:**

```python
nhl = HockeyScraper('nhl')
pbp    = nhl.scrape_game(2023020001)
shifts = nhl.shifts(2023020001)
matrix    = nhl.seconds_matrix(pbp, shifts)
strengths = nhl.strengths_by_second(matrix)
toi = nhl.toi_by_strength_all(matrix, strengths)
print(toi.head())
```

---

### shared_toi_teammates()

```python
shared_toi_teammates(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    in_seconds: bool = False,
) -> pd.DataFrame
```

Computes pairwise shared time-on-ice between teammates by strength state.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix_df` | `pd.DataFrame` | — | Output from `seconds_matrix()` |
| `strengths_df` | `pd.DataFrame` | — | Output from `strengths_by_second()` |
| `in_seconds` | `bool` | `False` | Return TOI in seconds instead of minutes |

**Returns:** `pd.DataFrame` — every (player_a, player_b) teammate pair with shared TOI per strength.

---

### shared_toi_opponents()

```python
shared_toi_opponents(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    in_seconds: bool = False,
) -> pd.DataFrame
```

Computes pairwise shared time-on-ice between players on **opposing** teams by strength state.

**Parameters:** Same as `shared_toi_teammates()`.

**Returns:** `pd.DataFrame` — every (home_player, away_player) opponent pair with shared TOI per strength.

---

### on_ice_stats()

```python
on_ice_stats(
    pbp: pd.DataFrame,
    include_goalies: bool = False,
    rates: bool = False,
) -> pd.DataFrame
```

Computes per-player, per-strength on-ice stats from a PBP DataFrame. Includes Corsi (CF/CA), Fenwick (FF/FA), shots (SF/SA), goals (GF/GA), and penalties (PF/PA).

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pbp` | `pd.DataFrame` | — | PBP DataFrame from `scrape_game()` |
| `include_goalies` | `bool` | `False` | Whether to include goalies in the output |
| `rates` | `bool` | `False` | Whether to add per-60-minute rate columns (e.g. `CF60`, `CA60`) |

**Returns:** `pd.DataFrame` — per-player, per-strength aggregated stats.

**Example:**

```python
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2023020001)
stats = nhl.on_ice_stats(pbp, rates=True)
print(stats.columns.tolist())
print(stats.sort_values('CF', ascending=False).head(5))
```

---

### combo_on_ice_stats()

```python
combo_on_ice_stats(
    pbp: pd.DataFrame,
    focus_team: str,
    n_team: int = 2,
    m_opp: int = 0,
    min_toi: int = 15,
    include_goalies: bool = False,
    rates: bool = False,
) -> pd.DataFrame
```

Computes on-ice stats for all n-player combinations on a focus team, optionally crossed against m-player combinations on the opposing team.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pbp` | `pd.DataFrame` | — | PBP DataFrame from `scrape_game()` |
| `focus_team` | `str` | — | Team tricode for the team whose player combinations to compute |
| `n_team` | `int` | `2` | Size of player combinations on the focus team |
| `m_opp` | `int` | `0` | Size of opponent player combinations to cross against. `0` means opponent combinations are not computed |
| `min_toi` | `int` | `15` | Minimum shared TOI in seconds to include a combination in the output |
| `include_goalies` | `bool` | `False` | Whether to include goalies in combinations |
| `rates` | `bool` | `False` | Whether to add per-60 rate columns |

**Returns:** `pd.DataFrame` — on-ice stats for each qualifying player combination.

**Example:**

```python
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2023020001)
# home team combos
home_team = pbp['homeTeam'].iloc[0]
combos = nhl.combo_on_ice_stats(pbp, focus_team=home_team, n_team=2)
print(combos.head())
```

---

### team_strength_aggregates()

```python
team_strength_aggregates(
    pbp: pd.DataFrame,
    rates: bool = False,
) -> pd.DataFrame
```

Aggregates on-ice shot and goal stats by team and strength state. Provides a team-level view of shot share.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pbp` | `pd.DataFrame` | — | PBP DataFrame from `scrape_game()` |
| `rates` | `bool` | `False` | Whether to add per-60 rate columns |

**Returns:** `pd.DataFrame` — per-team, per-strength aggregated stats.

**Example:**

```python
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2023020001)
agg = nhl.team_strength_aggregates(pbp, rates=True)
print(agg)
```

---

## Functional API — scrape()

```python
scrape(league: str, data_type: str = 'pbp', **kwargs) -> pd.DataFrame | dict
```

A thin wrapper around `HockeyScraper` for quick one-liner usage. Creates a scraper instance internally and delegates to the appropriate method.

**Parameters:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `league` | `str` | — | League code. Same options as `HockeyScraper(league)` |
| `data_type` | `str` | `'pbp'` | Data type to fetch. See table below |
| `**kwargs` | | | Forwarded to the underlying method |

**Supported `data_type` values:**

| `data_type` | Delegates to | Key kwargs |
| --- | --- | --- |
| `'pbp'` | `play_by_play()` | `game_id` |
| `'stats'` | `player_stats()` | `season`, `team`, `position` |
| `'schedule'` | `schedule()` | `team`, `season` |
| `'roster'` | `roster()` | `team`, `season` |
| `'standings'` | `standings()` | `season` |
| `'teams'` | `scrape_teams()` for NHL, `teams_by_season()` for others | `season` |
| `'teams_by_season'` | `teams_by_season()` | `season` |
| `'scrape_teams'` | `scrape_teams()` (NHL only) | `source` |
| `'seasons'` | `seasons()` | `season_type` |

**Raises:** `ValueError` for unrecognised `data_type`.

**Example:**

```python
from scrapernhl import scrape

# PBP
pbp = scrape('ahl', 'pbp', game_id=1027781)

# Stats
skaters = scrape('ahl', 'stats', season=90, position='skaters')
nhl_mtl = scrape('nhl', 'stats', team='MTL', season=20232024, position='skaters')

# Schedule
schedule = scrape('nhl', 'schedule', team='TOR', season=20232024)

# Standings
standings = scrape('nhl', 'standings', season=20232024)
standings = scrape('ahl', 'standings')

# Roster
roster = scrape('nhl', 'roster', team='MTL', season=20232024)

# Teams
nhl_teams  = scrape('nhl', 'teams')
nhl_teams  = scrape('nhl', 'scrape_teams', source='records')
ahl_teams  = scrape('ahl', 'teams', season=90)

# Seasons
seasons = scrape('nhl', 'seasons')
seasons = scrape('ahl', 'seasons', season_type='regular')
```

---

## CLI Reference

The CLI is available as a Python module:

```bash
python -m scrapernhl [COMMAND] [OPTIONS]
```

### NHL Commands (top-level)

```bash
# Teams
python -m scrapernhl teams [-o OUTPUT] [-f FORMAT]

# Schedule (requires TEAM and SEASON)
python -m scrapernhl schedule TEAM SEASON [-o OUTPUT] [-f FORMAT]

# Standings (optional DATE in YYYY-MM-DD format)
python -m scrapernhl standings [DATE] [-o OUTPUT] [-f FORMAT]

# Roster (requires TEAM and SEASON)
python -m scrapernhl roster TEAM SEASON [-o OUTPUT] [-f FORMAT]

# Player stats (requires TEAM and SEASON)
python -m scrapernhl stats TEAM SEASON [--goalies] [--session INT] [-o OUTPUT] [-f FORMAT]

# Play-by-play (requires GAME_ID)
python -m scrapernhl game GAME_ID [-o OUTPUT] [-f FORMAT]

# Draft (requires YEAR, optional ROUND)
python -m scrapernhl draft YEAR [ROUND] [-o OUTPUT] [-f FORMAT]
```

### Non-NHL League Commands

Non-NHL leagues are accessed as subcommands: `ahl`, `pwhl`, `ohl`, `whl`, `qmjhl`.

```bash
python -m scrapernhl ahl [COMMAND] [OPTIONS]
```

Available subcommands per league:

| Subcommand | Description | Key Options |
| --- | --- | --- |
| `teams` | List teams | `[-o] [-f]` |
| `schedule` | Season schedule | `[--season INT] [-o] [-f]` |
| `standings` | League standings | `[--season INT] [-o] [-f]` |
| `roster` | Team roster | `--team-id INT [--season INT] [-o] [-f]` |
| `stats` | Player stats | `[--season INT] [--player-type skater\|goalie] [--limit INT] [-o] [-f]` |
| `game` | Play-by-play | `GAME_ID [-o] [-f]` |
| `bootstrap` | Raw config data | `[--season TEXT] [--page-name TEXT] [--game-id INT] [-o]` |

### Output Formats

All commands support `-f / --format` with these options:

| Format | Description |
| --- | --- |
| `csv` | Comma-separated values (default for most commands) |
| `json` | JSON array |
| `parquet` | Apache Parquet (columnar, efficient for large data) |
| `excel` | Excel `.xlsx` |

### Examples

```bash
# NHL examples
python -m scrapernhl standings -o nhl_standings.csv
python -m scrapernhl schedule MTL 20252026 -f json -o mtl_schedule.json
python -m scrapernhl game 2024020001 -o game_pbp.parquet -f parquet
python -m scrapernhl draft 2024 -o draft_2024.csv

# AHL examples
python -m scrapernhl ahl standings
python -m scrapernhl ahl standings -o ahl_standings.csv
python -m scrapernhl ahl stats --season 90 -f parquet -o ahl_skaters.parquet
python -m scrapernhl ahl stats --player-type goalie --season 90
python -m scrapernhl ahl game 1027781 -o pbp.csv
python -m scrapernhl ahl bootstrap --season 90

# PWHL / OHL / WHL / QMJHL
python -m scrapernhl pwhl standings
python -m scrapernhl ohl stats --player-type skater
python -m scrapernhl whl game 1022126
python -m scrapernhl qmjhl standings -f json
```

---

## Legacy NHL Scraper — scraper_legacy.py

`scraper_legacy.py` is the original NHL analytics engine. It remains fully functional in 0.3.x and contains all heavy per-player and per-combination stat functions that have not yet been ported to the new module structure.

All functions are accessible via **lazy import** through `scrapernhl.nhl.scraper` (no heavy dependencies are loaded until you actually call a legacy function) or by importing `scrapernhl.nhl.scraper_legacy` directly.

!!! note
    These functions are NHL-only. They operate on DataFrames produced by `scrape_game()`. For non-NHL leagues use `HockeyScraper('<league>').play_by_play()`.

---

### Importing legacy functions

```python
# Option A — via the nhl scraper module (lazy, preferred)
from scrapernhl.nhl.scraper import (
    scrape_game,
    on_ice_stats_by_player_strength,
    toi_by_player_and_strength,
    combo_on_ice_stats,
    combo_on_ice_stats_both_teams,
    team_strength_aggregates,
)

# Option B — direct import (loads xgboost / polars / numpy immediately)
from scrapernhl.nhl.scraper_legacy import scrape_game

# Option C — via HockeyScraper convenience wrappers (recommended for new code)
from scrapernhl import HockeyScraper
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2024020001)
```

---

### Core PBP functions

| Function | Signature | Description |
|---|---|---|
| `scrape_game()` | `scrape_game(game_id, *, shifts=True, html_pbp=True, output_format='pandas') -> pd.DataFrame` | Full enriched PBP with shifts, strengths, and on-ice players. The main entry point for all analytics. |
| `scrape_game_async()` | `scrape_game_async(game_id, ...) -> pd.DataFrame` | Async version of `scrape_game()`. |
| `scrapePlays()` | `scrapePlays(game, output_format='pandas') -> pd.DataFrame` | JSON PBP only (no HTML enrichment). Faster but less complete. |
| `getGameData()` | `getGameData(game, addGoalReplayData=False) -> dict` | Raw game JSON from the NHL API. |
| `scrape_html_pbp()` | `scrape_html_pbp(game_id, return_raw=False) -> pd.DataFrame` | Parse HTML play-by-play sheet. Used internally by `scrape_game()`. |
| `scrape_shifts()` | `scrape_shifts(game_id) -> pd.DataFrame` | Parse HTML shift chart into a tidy shift DataFrame. |
| `getGoalReplayData()` | `getGoalReplayData(json_url) -> dict` | Fetch goal-replay sprite frame data. |

---

### Shift & strength pipeline

These functions form the low-level strength/TOI backbone used by the higher-level stat functions.

| Function | Description |
|---|---|
| `build_shifts_events(shifts)` | Convert shift DataFrame into ON/OFF boundary events table. |
| `add_strengths_to_shifts_events(shifts_events, strengths_df)` | Annotate each ON/OFF event with the strength state at that second. |
| `build_strength_segments_from_shifts(shifts)` | Build contiguous strength segments from the shift chart. |
| `strengths_by_second_from_segments(segments)` | Turn segments into a per-second strength lookup Series. |
| `seconds_matrix(df, shifts)` | Build a player × second presence matrix (input to TOI math). |
| `strengths_by_second(matrix_df)` | Map each column (second) of the presence matrix to a strength label. |
| `toi_by_strength_all(matrix_df, strengths_df)` | Total TOI for every player × strength combination. |

---

### On-ice stats & TOI

| Function | Signature | Description |
|---|---|---|
| `toi_by_strength(pbp_change_events)` | `toi_by_strength(df) -> pd.DataFrame` | Per-team TOI broken out by `EV / PP / PK / other`. |
| `toi_by_player_and_strength(pbp_change_events)` | `toi_by_player_and_strength(df) -> pd.DataFrame` | Per-player TOI split by strength state from the **player's team perspective** (fixed in 0.3.2 for the alphabetically second team). |
| `on_ice_stats_by_player_strength(pbp, team)` | `on_ice_stats_by_player_strength(pbp, team) -> pd.DataFrame` | Corsi / Fenwick / goals for every player × strength, from `team`'s perspective. |
| `build_on_ice_long(df)` | `build_on_ice_long(df) -> pd.DataFrame` | Expand the compact on-ice player columns to long format (one row per player per event). |
| `build_on_ice_wide(df, ...)` | `build_on_ice_wide(df, ...) -> pd.DataFrame` | Pivot long on-ice data back to wide format for downstream modeling. |
| `shared_toi_teammates_by_strength(...)` | — | Pairwise shared TOI for all teammate pairs at each strength. |
| `shared_toi_opponents_by_strength(...)` | — | Pairwise shared TOI for all opponent pairs at each strength. |

---

### Combination stats

| Function | Description |
|---|---|
| `combo_on_ice_stats(pbp, focus_team)` | Corsi / Fenwick / goals for every N-player combination from `focus_team`'s perspective. Strength labels use `focus_team`'s perspective (fixed in 0.3.2). |
| `combo_on_ice_stats_both_teams(pbp)` | Runs `combo_on_ice_stats()` for home and away and concatenates results. Both teams now get correct perspective labels (fixed in 0.3.2). |
| `combos_teammates_by_strength(...)` | Pairwise teammate combination TOI by strength. |
| `combos_opponents_by_strength(...)` | Pairwise opponent combination TOI by strength. |
| `combo_toi_by_strength(...)` | Aggregate TOI for multi-player combinations at each strength. |
| `combo_shot_metrics_by_strength(...)` | Corsi / Fenwick / xG for multi-player combinations. |

---

### Team aggregates & expected goals

| Function | Description |
|---|---|
| `team_strength_aggregates(pbp)` | Per-team Corsi, Fenwick, goals, TOI, and xG split by strength state. Returns one row per team per strength. Strength labels from each team's perspective (fixed in 0.3.2). |
| `build_shots_design_matrix(pbp_df)` | Build the feature matrix used by the xG model. |
| `predict_xg_for_pbp(pbp_df)` | Add an `xG` column using the bundled XGBoost model. Requires `pip install scrapernhl[analytics]`. |
| `engineer_xg_features(pbp_df)` | *(deprecated)* Feature engineering step — use `build_shots_design_matrix()` + `predict_xg_for_pbp()` instead. |
| `pipeline(game_id)` | Convenience wrapper: scrape → parse → compute on-ice stats in one call. |

---

## Strength Notation

To distinguish empty-net situations from non-empty-net situations in on-ice stats, the scraper uses a `*` suffix to mark the team with the empty net.

| Notation | Meaning |
| --- | --- |
| `5v5` | Five skaters vs. five skaters, both goalies in net |
| `5v4` | Five skaters (power play) vs. four skaters (penalty kill), both goalies in net |
| `5v6*` | Five skaters vs. six skaters with the net empty (opposing goalie pulled) |
| `5*v4` | Five skaters with their net empty vs. four skaters with a goalie in net |
| `4v4` | Four-on-four (double minor / concurrent penalties) |

The `*` always marks the team whose goalie is not in the net. This notation appears in the `detailedGameStrength` column of `scrape_game()` output and in the `on_ice_stats()` / `combo_on_ice_stats()` strength columns.
