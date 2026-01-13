# API Reference

ScraperNHL API documentation covering 6 hockey leagues.

## Table of Contents

### Leagues We Scrape
- [NHL - National Hockey League](#nhl---national-hockey-league) - Full scraping with play-by-play, advanced analytics
- [PWHL - Professional Women's Hockey League](#pwhl---professional-womens-hockey-league) - Complete API access
- [AHL - American Hockey League](#ahl---american-hockey-league) - Complete API access
- [OHL - Ontario Hockey League](#ohl---ontario-hockey-league) - Complete API access
- [WHL - Western Hockey League](#whl---western-hockey-league) - Complete API access
- [QMJHL - Quebec Maritimes Junior Hockey League](#qmjhl---quebec-maritimes-junior-hockey-league) - Complete API access

### Other
- [Core Utilities](#core-utilities) - HTTP, caching, utils
- [Configuration](#configuration) - Constants and settings

---

# NHL - National Hockey League

Full NHL scraping with play-by-play data, advanced analytics, and Expected Goals (xG) model.

### Quick Start

#### Modular Imports (Recommended)
```python
from scrapernhl.scrapers.teams import scrapeTeams
from scrapernhl.scrapers.schedule import scrapeSchedule

teams = scrapeTeams()
schedule = scrapeSchedule("MTL", "20252026")
```

#### Legacy Imports (Still Supported)
```python
from scrapernhl import scrapeTeams, scrapeSchedule

teams = scrapeTeams()
schedule = scrapeSchedule("MTL", "20252026")
```

### Command-Line Interface

All scraping functions are available via CLI for quick data exports across all 6 supported leagues:

```bash
# View available commands
python scrapernhl/cli.py --help

# NHL commands
python scrapernhl/cli.py teams --output teams.csv
python scrapernhl/cli.py schedule MTL 20252026 --format json
python scrapernhl/cli.py standings --format parquet

# Multi-league commands (PWHL, AHL, OHL, WHL, QMJHL)
python scrapernhl/cli.py pwhl teams
python scrapernhl/cli.py ahl standings --season 2024
python scrapernhl/cli.py ohl stats --player-type goalie
python scrapernhl/cli.py whl game 12345
python scrapernhl/cli.py qmjhl roster --team-id 7
```

See the [CLI Examples](examples/cli.md) page for comprehensive CLI usage including all leagues.

---
### IMPORTANT NOTE ABOUT GAME STRENGTHS
In order to differenciate **empty-net** situtations to **non-empty net** situations, there the scraper incorporates a unique format. It uses the star symbol to indentify the team with an empty net.

If you ever see ```5v6*```, it means that the player or team is facing a team that has 6 skaters and the net empty. 
If you see ```5*v4```, it means that the player or team has 5 skaters and the net empty while facing a team with 4 skaters with a goalie. 

---

## Scrapers Module (`scrapernhl.scrapers`)

### Teams (`scrapernhl.scrapers.teams`)

#### `getTeamsData(source: str = "default") -> List[Dict]`

Scrapes raw NHL team data from various public endpoints.

**Parameters:**
- `source` (str): Data source to use. Options: `"default"`, `"calendar"`, `"records"`

**Returns:**
- `List[Dict]`: Raw team data with metadata

**Example:**
```python
from scrapernhl.scrapers.teams import getTeamsData

raw_teams = getTeamsData(source="default")
```

#### `scrapeTeams(source: str = "default", output_format: str = "pandas") -> DataFrame`

Scrapes NHL team data and returns as DataFrame.

**Parameters:**
- `source` (str): Data source. Options: `"default"`, `"calendar"`, `"records"`
- `output_format` (str): Output format. Options: `"pandas"`, `"polars"`

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Team data with metadata

**Example:**
```python
from scrapernhl.scrapers.teams import scrapeTeams

# Get as pandas DataFrame
teams = scrapeTeams()

# Get as polars DataFrame
teams_pl = scrapeTeams(output_format="polars")
```

---

### Schedule (`scrapernhl.scrapers.schedule`)

#### `getScheduleData(team: str = "MTL", season: Union[str, int] = "20252026") -> List[Dict]`

Scrapes raw NHL schedule data for a team and season.

**Parameters:**
- `team` (str): Team abbreviation (e.g., "MTL", "TOR", "BOS")
- `season` (str | int): Season ID (e.g., "20252026" or 20252026)

**Returns:**
- `List[Dict]`: Raw schedule records

**Example:**
```python
from scrapernhl.scrapers.schedule import getScheduleData

raw_schedule = getScheduleData("MTL", "20252026")
```

#### `scrapeSchedule(team: str = "MTL", season: Union[str, int] = "20252026", output_format: str = "pandas") -> DataFrame`

Scrapes NHL schedule data for a team and season.

**Parameters:**
- `team` (str): Team abbreviation
- `season` (str | int): Season ID
- `output_format` (str): Output format. Options: `"pandas"`, `"polars"`

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Schedule data

**Example:**
```python
from scrapernhl.scrapers.schedule import scrapeSchedule

# Montreal Canadiens 2025-26 season
schedule = scrapeSchedule("MTL", "20252026")
```

---

### Standings (`scrapernhl.scrapers.standings`)

#### `getStandingsData(date: str = None) -> List[Dict]`

Scrapes raw NHL standings data for a specific date.

**Parameters:**
- `date` (str, optional): Date in 'YYYY-MM-DD' format. Defaults to previous year's January 1st

**Returns:**
- `List[Dict]`: Raw standings records

**Example:**
```python
from scrapernhl.scrapers.standings import getStandingsData

raw_standings = getStandingsData("2025-01-01")
```

#### `scrapeStandings(date: str = None, output_format: str = "pandas") -> DataFrame`

Scrapes NHL standings data for a specific date.

**Parameters:**
- `date` (str, optional): Date in 'YYYY-MM-DD' format
- `output_format` (str): Output format. Options: `"pandas"`, `"polars"`

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Standings data

**Example:**
```python
from scrapernhl.scrapers.standings import scrapeStandings

standings = scrapeStandings("2025-01-01")
```

---

### Roster (`scrapernhl.scrapers.roster`)

#### `getRosterData(team: str = "MTL", season: Union[str, int] = "20242025") -> List[Dict]`

Scrapes raw NHL roster data for a team and season.

**Parameters:**
- `team` (str): Team abbreviation
- `season` (str | int): Season ID

**Returns:**
- `List[Dict]`: Raw roster records (forwards, defensemen, goalies)

**Example:**
```python
from scrapernhl.scrapers.roster import getRosterData

raw_roster = getRosterData("MTL", "20242025")
```

#### `scrapeRoster(team: str = "MTL", season: Union[str, int] = "20242025", output_format: str = "pandas") -> DataFrame`

Scrapes NHL roster data for a team and season.

**Parameters:**
- `team` (str): Team abbreviation
- `season` (str | int): Season ID
- `output_format` (str): Output format

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Roster data

**Example:**
```python
from scrapernhl.scrapers.roster import scrapeRoster

roster = scrapeRoster("MTL", "20252026")
```

---

### Stats (`scrapernhl.scrapers.stats`)

#### `getTeamStatsData(team: str = "MTL", season: Union[str, int] = "20252026", session: Union[str, int] = 2, goalies: bool = False) -> List[Dict]`

Scrapes raw NHL team statistics.

**Parameters:**
- `team` (str): Team abbreviation
- `season` (str | int): Season ID
- `session` (str | int): Session type - 1: pre-season, 2: regular season, 3: playoffs
- `goalies` (bool): If True, fetch goalie stats; if False, fetch skater stats

**Returns:**
- `List[Dict]`: Raw statistics records

**Example:**
```python
from scrapernhl.scrapers.stats import getTeamStatsData

# Get skater stats
skater_stats = getTeamStatsData("MTL", "20252026", session=2, goalies=False)

# Get goalie stats
goalie_stats = getTeamStatsData("MTL", "20252026", session=2, goalies=True)
```

#### `scrapeTeamStats(team: str = "MTL", season: Union[str, int] = "20252026", session: Union[str, int] = 2, goalies: bool = False, output_format: str = "pandas") -> DataFrame`

Scrapes NHL team statistics.

**Parameters:**
- `team` (str): Team abbreviation
- `season` (str | int): Season ID
- `session` (str | int): Session type
- `goalies` (bool): Fetch goalie stats vs skater stats
- `output_format` (str): Output format

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Team statistics

**Example:**
```python
from scrapernhl.scrapers.stats import scrapeTeamStats

stats = scrapeTeamStats("MTL", "20252026", session=2)
```

---

### Draft (`scrapernhl.scrapers.draft`)

#### `getDraftDataData(year: Union[str, int] = "2024", round: Union[str, int] = "all") -> List[Dict]`

Scrapes raw NHL draft data.

**Parameters:**
- `year` (str | int): Draft year (e.g., "2024")
- `round` (str | int): Round number or "all" for all rounds

**Returns:**
- `List[Dict]`: Raw draft records

#### `scrapeDraftData(year: Union[str, int] = "2024", round: Union[str, int] = "all", output_format: str = "pandas") -> DataFrame`

Scrapes NHL draft data.

**Parameters:**
- `year` (str | int): Draft year
- `round` (str | int): Round number or "all"
- `output_format` (str): Output format

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Draft data

**Example:**
```python
from scrapernhl.scrapers.draft import scrapeDraftData

# All rounds
draft = scrapeDraftData("2024", "all")

# First round only
first_round = scrapeDraftData("2024", 1)
```

#### `getRecordsDraftData(year: Union[str, int] = "2025") -> List[Dict]`

Scrapes draft records from NHL Records API.

#### `scrapeDraftRecords(year: Union[str, int] = "2025", output_format: str = "pandas") -> DataFrame`

Scrapes draft records from NHL Records API.

#### `getRecordsTeamDraftHistoryData(franchise: Union[str, int] = 1) -> List[Dict]`

Scrapes team draft history for a franchise.

**Parameters:**
- `franchise` (str | int): Franchise ID

#### `scrapeTeamDraftHistory(franchise: Union[str, int] = 1, output_format: str = "pandas") -> DataFrame`

Scrapes team draft history.

**Example:**
```python
from scrapernhl.scrapers.draft import scrapeTeamDraftHistory

# Montreal Canadiens (franchise ID 1)
mtl_draft_history = scrapeTeamDraftHistory(1)
```

---

### Games (`scrapernhl.scrapers.games`)

#### `getGameData(game: Union[str, int], addGoalReplayData: bool = False) -> Dict`

Scrapes NHL play-by-play data for a game.

**Parameters:**
- `game` (str | int): Game ID (e.g., 2024020001)
- `addGoalReplayData` (bool): If True, fetch goal replay data

**Returns:**
- `Dict`: Complete game data with enriched plays

**Example:**
```python
from scrapernhl.scrapers.games import getGameData

game_data = getGameData(2024020001, addGoalReplayData=True)
```

#### `scrapePlays(game: Union[str, int], addGoalReplayData: bool = False, output_format: str = "pandas") -> DataFrame`

Scrapes play-by-play data for a game.

**Parameters:**
- `game` (str | int): Game ID
- `addGoalReplayData` (bool): Include goal replay data
- `output_format` (str): Output format

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Play-by-play data

**Example:**
```python
from scrapernhl.scrapers.games import scrapePlays

pbp = scrapePlays(2024020001)
```

#### `getGoalReplayData(json_url: str) -> List[Dict]`

Fetches goal replay data from a JSON URL.

**Parameters:**
- `json_url` (str): URL to goal replay JSON

**Returns:**
- `List[Dict]`: Goal replay data

#### `convert_json_to_goal_url(json_url: str) -> str`

Converts a JSON URL to NHL goal replay URL.

**Parameters:**
- `json_url` (str): JSON URL

**Returns:**
- `str`: Goal replay URL

---

## Core Utilities (`scrapernhl.core`)

### HTTP (`scrapernhl.core.http`)

#### `fetch_json(url: str, timeout: int = 10) -> dict`

Fetches JSON data from a URL with retry logic.

**Parameters:**
- `url` (str): URL to fetch
- `timeout` (int): Request timeout in seconds

**Returns:**
- `dict`: Parsed JSON response

**Raises:**
- `requests.exceptions.RequestException`: If request fails

**Example:**
```python
from scrapernhl.core.http import fetch_json

data = fetch_json("https://api-web.nhle.com/v1/...")
```

#### `fetch_html(url: str, timeout: int = 10) -> Optional[str]`

Fetches HTML content from a URL.

**Parameters:**
- `url` (str): URL to fetch
- `timeout` (int): Request timeout in seconds

**Returns:**
- `str` or `None`: HTML content, or None if request fails

#### `fetch_html_async(url: str, timeout: int = 10) -> Optional[str]`

Async wrapper around fetch_html.

#### `fetch_json_async(url: str, timeout: int = 10) -> dict`

Async wrapper around fetch_json.

---

### Utils (`scrapernhl.core.utils`)

#### `time_str_to_seconds(time_str: Optional[str]) -> Optional[int]`

Converts time string in 'MM:SS' format to total seconds.

**Parameters:**
- `time_str` (str): Time string (e.g., "05:30")

**Returns:**
- `int` or `None`: Total seconds

**Example:**
```python
from scrapernhl.core.utils import time_str_to_seconds

seconds = time_str_to_seconds("05:30")  # Returns 330
```

#### `json_normalize(data: List[Dict], output_format: str = "pandas") -> DataFrame`

Normalizes nested JSON data to flat table.

**Parameters:**
- `data` (List[Dict]): List of dictionaries
- `output_format` (str): "pandas" or "polars"

**Returns:**
- `pd.DataFrame` or `pl.DataFrame`: Normalized data

---

## Configuration (`scrapernhl.config`)

### Constants

```python
from scrapernhl.config import (
    DEFAULT_TEAM,      # "MTL"
    DEFAULT_SEASON,    # "20252026"
    DEFAULT_DATE,      # "2025-11-11"
    DEFAULT_HEADERS,   # HTTP headers dict
    DEFAULT_TIMEOUT,   # 10 seconds
)
```

### API Endpoints

```python
from scrapernhl.config import (
    NHL_API_BASE_URL,
    NHL_API_BASE_URL_V1,
    STANDINGS_ENDPOINT,
    TEAM_SCHEDULE_ENDPOINT,
    FRANCHISES_ENDPOINT,
)
```

---

## Legacy Functions

Advanced functions (PBP parsing, feature engineering, analytics) are available via lazy loading from `scraper_legacy.py`. These load only when accessed:

```python
from scrapernhl import (
    scrape_game,
    engineer_xg_features,
    build_on_ice_wide,
    toi_by_strength,
    combo_on_ice_stats,
)
```

**Note:** These functions require additional dependencies (xgboost, etc.) and are being modularized in Phase 2.

---

## Complete Example

```python
from scrapernhl.scrapers.teams import scrapeTeams
from scrapernhl.scrapers.schedule import scrapeSchedule
from scrapernhl.scrapers.standings import scrapeStandings
from scrapernhl.scrapers.games import scrapePlays

# Get all teams
teams = scrapeTeams()
print(f"Found {len(teams)} teams")

# Get Montreal Canadiens schedule
mtl_schedule = scrapeSchedule("MTL", "20252026")
print(f"MTL has {len(mtl_schedule)} games")

# Get current standings
standings = scrapeStandings("2025-01-01")
print(f"Standings for {len(standings)} teams")

# Get play-by-play for a specific game
pbp = scrapePlays(2024020001)
print(f"Game has {len(pbp)} events")
```

---

## Performance Tips

1. **Use modular imports** for faster loading:
   ```python
   from scrapernhl.scrapers.teams import scrapeTeams  # Fast
   from scrapernhl import scrapeTeams  # Also fast, but loads more
   ```

2. **Choose output format** based on your needs:
   ```python
   teams_pd = scrapeTeams(output_format="pandas")   # pandas
   teams_pl = scrapeTeams(output_format="polars")   # polars (faster)
   ```

3. **Cache results** when scraping multiple times:
   ```python
   @lru_cache(maxsize=100)
   def get_cached_teams():
       return scrapeTeams()
   ```

---


---

# PWHL - Professional Women's Hockey League

Complete API access for the Professional Women's Hockey League using the HockeyTech/LeagueStat platform.

## PWHL Overview

- **API Key**: `446521baf8c38984`
- **Teams**: 9 teams (Boston Fleet, Minnesota Frost, Montréal Victoire, New York Sirens, Ottawa Charge, Toronto Sceptres)
- **Base URL**: `https://lscluster.hockeytech.com/feed/index.php`
- **Rate Limit**: ~2 requests/second

## PWHL Quick Start

```python
from scrapernhl.pwhl import api

# Get all PWHL teams
teams = api.get_teams()

# Get top scorers
stats = api.get_skater_stats(limit=20)

# Get standings
standings = api.get_standings()

# Get games
games = api.get_scorebar()
```

## PWHL Available Functions

All 15 functions available. See [Quick Reference](api-quick-reference.md) for detailed parameters.

### Core Data
- `get_teams()` - All teams
- `get_scorebar()` - Live games & schedule  
- `get_standings()` - Standings

### Player Statistics
- `get_skater_stats()` - Skater stats with filtering
- `get_goalie_stats()` - Goalie stats with filtering
- `get_player_profile()` - Player details
- `get_all_players()` - All players

### Games & Schedule
- `get_schedule()` - Full schedule
- `get_team_schedule()` - Team schedule
- `get_game_preview()` - Game preview
- `get_game_summary()` - Game summary
- `get_play_by_play()` - Play-by-play
- `get_game_full_data()` - All game data

### Team Functions
- `get_roster()` - Team roster
- `get_bootstrap()` - Configuration

## PWHL Examples

```python
from scrapernhl.pwhl import api

# Team dashboard
def team_dashboard(team_id):
    return {
        'roster': api.get_roster(team_id=team_id),
        'schedule': api.get_team_schedule(team_id=team_id),
        'skaters': api.get_skater_stats(team=str(team_id), limit=50),
        'goalies': api.get_goalie_stats(team=str(team_id), limit=10)
    }

# Get leaders
leaders = api.get_skater_stats(limit=10)
```

---

# AHL - American Hockey League

Complete API access for the American Hockey League.

## AHL Overview

- **API Key**: `ccb91f29d6744675`
- **Site ID**: `3`
- **Teams**: 24+ teams
- **Base URL**: `https://lscluster.hockeytech.com/feed/index.php`

## AHL Quick Start

```python
from scrapernhl.ahl import api

# Get teams
teams = api.get_teams()

# Get leaders
stats = api.get_skater_stats(limit=50)

# Get standings
standings = api.get_standings(group_by='division')
```

## AHL Available Functions

All 15 functions work identically to PWHL (see PWHL section above).

## AHL Examples

```python
from scrapernhl.ahl import api

# Find rookies
rookies = api.get_skater_stats(rookies=1, limit=20)

# Team comparison
team1 = api.get_skater_stats(team='5', limit=100)
team2 = api.get_skater_stats(team='8', limit=100)
```

---

# OHL - Ontario Hockey League

Complete API access for the Ontario Hockey League.

## OHL Overview

- **API Key**: `f1aa699db3d81487`
- **Teams**: 20+ teams
- **Base URL**: `https://lscluster.hockeytech.com/feed/index.php`

## OHL Quick Start

```python
from scrapernhl.ohl import api

# Get teams
teams = api.get_teams()

# Get leaders
leaders = api.get_skater_stats(limit=10)

# Get schedule
schedule = api.get_team_schedule(team_id=5)
```

## OHL Available Functions

All 15 functions work identically to PWHL (see PWHL section above).

## OHL Examples

```python
from scrapernhl.ohl import api

# Game analysis
game = api.get_game_full_data(game_id=12345)
pbp = game.get('play_by_play', {})
print(f"Events: {len(pbp.get('plays', []))}")
```

---

# WHL - Western Hockey League

Complete API access for the Western Hockey League.

## WHL Overview

- **API Key**: `f1aa699db3d81487` (shared with OHL)
- **Teams**: 22+ teams
- **Base URL**: `https://lscluster.hockeytech.com/feed/index.php`

## WHL Quick Start

```python
from scrapernhl.whl import api

# Get teams
teams = api.get_teams()

# Get goalies
goalies = api.get_goalie_stats(qualified='qualified', limit=20)

# Get standings
standings = api.get_standings(context='overall')
```

## WHL Available Functions

All 15 functions work identically to PWHL (see PWHL section above).

## WHL Examples

```python
from scrapernhl.whl import api

# Top goalies by save percentage
goalies = api.get_goalie_stats(qualified='qualified', limit=50)
goalie_list = goalies.get('players', [])
sorted_goalies = sorted(goalie_list, key=lambda g: g.get('save_pct', 0), reverse=True)[:10]
```

---

# QMJHL - Quebec Maritimes Junior Hockey League

Complete API access for the Quebec Maritimes Junior Hockey League.

## QMJHL Overview

- **API Key**: `f322673b6bcae299`
- **Teams**: 18+ teams
- **Base URL**: `https://lscluster.hockeytech.com/feed/index.php`

## QMJHL Quick Start

```python
from scrapernhl.qmjhl import api

# Get teams
teams = api.get_teams()

# Get stats with pagination
page1 = api.get_skater_stats(first=0, limit=50)
page2 = api.get_skater_stats(first=50, limit=50)

# Get roster
roster = api.get_roster(team_id=3)
```

## QMJHL Available Functions

All 15 functions work identically to PWHL (see PWHL section above).

## QMJHL Examples

```python
from scrapernhl.qmjhl import api

# Scoring leaders
stats = api.get_skater_stats(limit=10)
for i, player in enumerate(stats.get('players', []), 1):
    print(f"{i}. {player['name']}: {player.get('points', 0)}P")

# Paginate all players
all_players = []
page = 0
while True:
    stats = api.get_skater_stats(first=page * 100, limit=100)
    players = stats.get('players', [])
    if not players:
        break
    all_players.extend(players)
    page += 1
```

---

# Multi-League Comparison

## Cross-League Analysis

Compare data across all 5 leagues using the same API:

```python
from scrapernhl.pwhl import api as pwhl
from scrapernhl.ahl import api as ahl
from scrapernhl.ohl import api as ohl
from scrapernhl.whl import api as whl
from scrapernhl.qmjhl import api as qmjql

leagues = [
    ('PWHL', pwhl),
    ('AHL', ahl),
    ('OHL', ohl),
    ('WHL', whl),
    ('QMJHL', qmjql)
]

# Compare team counts
for name, module in leagues:
    teams = module.get_teams()
    print(f"{name}: {len(teams.get('teams', []))} teams")

# Compare top scorers
for name, module in leagues:
    stats = module.get_skater_stats(limit=1)
    players = stats.get('players', [])
    if players:
        print(f"{name}: {players[0]['name']} - {players[0].get('points', 0)}P")
```

## Common Parameters

All 5 leagues support identical parameters:

**Player Stats:**
```python
api.get_skater_stats(
    limit=50,           # Max results
    first=0,            # Starting offset
    team='5',           # Filter by team
    rookies=1,          # Rookies only
    qualified='qualified'  # Qualified only
)
```

**Schedule:**
```python
api.get_schedule(
    team_id=-1,         # -1 for all teams
    month=-1,           # -1 for all months
    location='home'     # 'home', 'away', or None
)
```

**Standings:**
```python
api.get_standings(
    group_by='division',  # 'division', 'conference', 'league'
    context='overall'     # 'overall', 'home', 'away'
)
```

## Multi-League Resources

- **[Quick Reference](api-quick-reference.md)** - Fast function lookup
- **[Complete Examples](multi-league-api-examples.md)** - Comprehensive guide
- **[Interactive Notebook](../notebooks/multi_league_api_examples.ipynb)** - Jupyter examples
- **[Test Suite](../test_multi_league_api.py)** - Reference implementations

---

For more information:
- [Getting Started](getting-started.md)
- [NHL Examples](examples/scraping.md)
- [Multi-League Examples](multi-league-api-examples.md)
