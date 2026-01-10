# Multi-League Scraper API Quick Reference

This document provides a quick reference for all scraper functions across the 5 supported leagues.

## Supported Leagues

1. **QMJHL** - Quebec Major Junior Hockey League
2. **OHL** - Ontario Hockey League  
3. **WHL** - Western Hockey League
4. **PWHL** - Professional Women's Hockey League
5. **AHL** - American Hockey League

## Common Parameters

All scrapers support these common parameters:

- `season` (int/str): Season ID (league-specific)
- `team_id` (int): Team ID (-1 for all teams)
- `output_format` (str): "pandas" or "polars" (default: "pandas")

## Schedule Scrapers

Get game schedules with scores, dates, and status.

```python
from scrapernhl.{league}.scrapers import scrapeSchedule

df = scrapeSchedule(
    season=None,        # Season ID (uses default if None)
    team_id=-1,        # Team ID (-1 for all teams)
    month=-1,          # Month filter (-1 for all months)
    location='homeaway', # 'homeaway', 'home', or 'away'
    output_format='pandas'
)
```

**Returns:** DataFrame with game_id, date, teams, scores, status, venue

## Teams Scrapers

Get team information for a season.

```python
from scrapernhl.{league}.scrapers import scrapeTeams

df = scrapeTeams(
    season=None,
    output_format='pandas'
)
```

**Returns:** DataFrame with team id, name, division, conference, logo

## Standings Scrapers

Get league standings with wins, losses, points.

```python
from scrapernhl.{league}.scrapers import scrapeStandings

df = scrapeStandings(
    season=None,
    context='overall',      # 'overall', 'home', 'away'
    special='false',
    group_by='division',   # 'division', 'conference'
    output_format='pandas'
)
```

**Returns:** DataFrame with team_code, wins, losses, OT losses, points, rankings

## Player Stats Scrapers

Get player statistics (skaters or goalies).

```python
from scrapernhl.{league}.scrapers import scrapePlayerStats

df = scrapePlayerStats(
    season=None,
    player_type='skater',    # 'skater' or 'goalie'
    sort='points',           # Sort field
    qualified='qualified',   # 'qualified' or 'all'
    limit=50,                # Number of records
    first=0,                 # Starting index (pagination)
    output_format='pandas'
)
```

**Returns:** DataFrame with player_id, name, team, games_played, goals, assists, points, etc.

## Roster Scrapers

Get team roster with player details.

```python
from scrapernhl.{league}.scrapers import scrapeRoster

df = scrapeRoster(
    team_id,                # Required: Team ID
    season=None,
    output_format='pandas'
)
```

**Returns:** DataFrame with player_id, name, position, jersey_number, birthdate, birthplace

## Example Usage

### QMJHL (Season 211 = 2024-25)

```python
from scrapernhl.qmjhl.scrapers import (
    scrapeSchedule, scrapeTeams, scrapeStandings,
    scrapePlayerStats, scrapeRoster
)

# Get full schedule
schedule = scrapeSchedule(season=211)

# Get standings by division
standings = scrapeStandings(season=211, group_by='division')

# Get top 20 scorers
top_scorers = scrapePlayerStats(season=211, sort='points', limit=20)

# Get roster for team 52 (Quebec Remparts)
roster = scrapeRoster(team_id=52, season=211)
```

### OHL (Season 68 = 2024-25)

```python
from scrapernhl.ohl.scrapers import (
    scrapeSchedule, scrapeStandings, scrapePlayerStats, scrapeRoster
)

schedule = scrapeSchedule(season=68)
standings = scrapeStandings(season=68)
top_scorers = scrapePlayerStats(season=68, limit=20)
roster = scrapeRoster(team_id=1, season=68)
```

### PWHL (Season 2 = 2024-25)

```python
from scrapernhl.pwhl.scrapers import (
    scrapeSchedule, scrapeStandings, scrapePlayerStats, scrapeRoster
)

schedule = scrapeSchedule(season=2)
standings = scrapeStandings(season=2)
top_scorers = scrapePlayerStats(season=2, limit=20)
roster = scrapeRoster(team_id=1, season=2)
```

### AHL (Season 71 = 2024-25)

```python
from scrapernhl.ahl.scrapers import (
    scrapeSchedule, scrapeStandings, scrapePlayerStats, scrapeRoster
)

schedule = scrapeSchedule(season=71)
standings = scrapeStandings(season=71)
top_scorers = scrapePlayerStats(season=71, limit=20)
roster = scrapeRoster(team_id=1, season=71)
```

### WHL (Season 70 = 2024-25)

```python
from scrapernhl.whl.scrapers import (
    scrapeSchedule, scrapeStandings, scrapePlayerStats, scrapeRoster
)

schedule = scrapeSchedule(season=70)
standings = scrapeStandings(season=70)
top_scorers = scrapePlayerStats(season=70, limit=20)
roster = scrapeRoster(team_id=1, season=70)
```

## Data Functions

For direct access to raw data (List[Dict]) before DataFrame conversion:

```python
from scrapernhl.{league}.scrapers import (
    getScheduleData,
    getTeamsData,
    getStandingsData,
    getPlayerStatsData,
    getRosterData
)

# Returns List[Dict] instead of DataFrame
raw_data = getScheduleData(season=211)
```

## Caching

All scrapers include built-in caching with TTL (Time-To-Live):

- **Schedule**: 1 hour (3600s)
- **Teams**: 24 hours (86400s)
- **Standings**: 1 hour (3600s)
- **Player Stats**: 1 hour (3600s)
- **Roster**: 1 hour (3600s)

Cache is stored in `~/.scrapernhl/cache/`

To clear cache:
```bash
rm -rf ~/.scrapernhl/cache
```

## Error Handling

All scrapers include error handling for:
- Invalid team IDs → `InvalidTeamError`
- API errors → `APIError`
- Network issues → `RuntimeError`

```python
from scrapernhl.exceptions import InvalidTeamError, APIError

try:
    roster = scrapeRoster(team_id=9999, season=211)
except InvalidTeamError as e:
    print(f"Invalid team: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Output Formats

### Pandas (default)

```python
df = scrapeSchedule(season=211, output_format='pandas')
# Returns pandas.DataFrame
```

### Polars

```python
df = scrapeSchedule(season=211, output_format='polars')
# Returns polars.DataFrame
```

## Best Practices

1. **Use specific season IDs** instead of defaults for consistent results
2. **Limit queries** when testing (use `limit` parameter for stats)
3. **Cache is your friend** - repeated calls use cached data
4. **Check for empty data** - some endpoints may return no data for certain seasons
5. **Export results** - save DataFrames to CSV/Excel for analysis

## Season IDs Reference

| League | 2024-25 Season ID |
|--------|-------------------|
| QMJHL  | 211              |
| OHL    | 68               |
| WHL    | 70               |
| PWHL   | 2                |
| AHL    | 71               |

## Support

- Documentation: See `notebooks/multi_league_scrapers_demo.ipynb`
- Framework: See `MULTI_LEAGUE_API_FRAMEWORK.md`
- Issues: Check existing scrapers and error messages
