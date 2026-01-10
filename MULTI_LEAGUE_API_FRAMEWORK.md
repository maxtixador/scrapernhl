# Multi-League API Framework

## Overview

Comprehensive API modules created for all 5 HockeyTech/LeagueStat leagues:
- **PWHL** (Professional Women's Hockey League)
- **AHL** (American Hockey League)
- **OHL** (Ontario Hockey League)
- **WHL** (Western Hockey League)
- **QMJHL** (Quebec Maritimes Junior Hockey League)

## Module Locations

```
scrapernhl/
├── pwhl/
│   └── api.py          ✅ Complete with all discovered parameters
├── ahl/
│   └── api.py          ✅ Complete (needs AHL API key)
├── ohl/
│   └── api.py          ✅ Complete
├── whl/
│   └── api.py          ✅ Complete
└── qmjhl/
    └── api.py          ✅ Complete
```

## League Configurations

| League | API Key | Client Code | League ID | Site ID |
|--------|---------|-------------|-----------|---------|
| PWHL   | 446521baf8c38984 | pwhl | 1 | 0 |
| AHL    | ccb91f29d6744675 | ahl | 4 | 3 |
| OHL    | f1aa699db3d81487 | ohl | 2 | 0 |
| WHL    | f1aa699db3d81487 | whl | 7 | 0 |
| QMJHL  | f322673b6bcae299 | lhjmq | 6 | 0 |

**Note:** All API keys are confirmed working as of January 2026.

## API Features

### 1. Games & Schedule
- `get_scorebar()` - Live games and upcoming schedule with date range filters
- `get_schedule()` - Full season schedule with month/location filters
- `get_game_preview()` - Game preview/matchup information
- `get_game_summary()` - Detailed game summary with stats
- `get_play_by_play()` - Play-by-play events for analysis

### 2. Teams
- `get_teams()` - All teams for a season
- `get_standings()` - Standings with grouping by division/conference/league
- `get_roster()` - Team roster with status filtering

### 3. Player Statistics
- `get_skater_stats()` - Skater stats with pagination and filtering
  - Supports: team filter, rookies only, pagination (first/limit), division/conference filters
- `get_goalie_stats()` - Goalie stats with qualification filters
  - Supports: qualified/unqualified filter, same filtering as skaters
- `get_player_profile()` - Detailed player profile and career stats

### 4. Configuration
- `get_bootstrap()` - Bootstrap/config data for API initialization
  - Supports: game-specific bootstrap, page context, league/conference/division filters

### 5. Convenience Functions
- `get_all_players()` - Fetch all skaters and goalies in one call
- `get_team_schedule()` - Get schedule for a specific team
- `get_game_full_data()` - Get complete game data (preview + summary + PBP)

## Enhanced Parameters (Discovered from PWHL URLs)

### Scorebar
- `numberofdaysahead` (default: 6)
- `numberofdaysback` (default: 0)
- `limit` (default: 1000)
- `fmt` (default: 'json')
- `division_id` (default: -1)

### Schedule
- `month` (default: -1, supports 1-12)
- `location` (default: 'homeaway', supports 'home', 'away')

### Standings
- `context` (default: 'overall', supports 'home', 'away')
- `special` (default: 'false')
- `groupTeamsBy` (default: 'division')

### Roster
- `rosterstatus` (default: 'undefined', supports 'active', 'inactive')

### Player Stats
- `team` (default: '-1' for all)
- `rookies` (default: 0, set to 1 for rookies only)
- `statsType` (default: 'standard', supports 'bio')
- `first` (pagination start index, default: 0)
- `limit` (pagination size, default: 100)
- `site_id`, `division`, `conference` filters

### Goalie Stats (additional)
- `qualified` (default: 'all', supports 'qualified', 'unqualified')

### Bootstrap (additional)
- `game_id` (optional game-specific context)
- `pageName` (default: 'scorebar')
- `league_code`, `conference`, `division` filters

## Technical Features

### Rate Limiting
- **2 requests per second** enforced via decorator pattern
- Sliding window implementation
- Automatic sleep when limit reached

### JSONP Handling
- Automatic removal of `angular.callbacks._X()` wrapper
- Handles both JSONP and clean JSON responses

### Error Handling
- HTTP error logging with detailed messages
- JSON parsing error recovery
- Response truncation for debugging (first 200 chars)

### Response Normalization
- Extracts nested `SiteKit` wrapper if present
- Handles list vs dict response variations
- Consistent return types across all functions

## Usage Examples

### PWHL Example
```python
from scrapernhl.pwhl import api

# Get current games
scorebar = api.get_scorebar(days_ahead=7, days_back=2)
print(f"Found {len(scorebar['games'])} games")

# Get skater stats with pagination
stats = api.get_skater_stats(team='5', limit=50, rookies=1)
print(f"Team 5 has {len(stats['players'])} rookie skaters")

# Get standings by division
standings = api.get_standings(context='overall', group_by='division')
```

### OHL Example
```python
from scrapernhl.ohl import api

# Get team schedule
schedule = api.get_team_schedule(team_id=2)
print(f"Team has {len(schedule)} games")

# Get complete game data
game = api.get_game_full_data(game_id=12345)
print(f"Final score: {game['summary']['final_score']}")
print(f"PBP events: {len(game['play_by_play'])}")
```

### WHL Example with Custom Config
```python
from scrapernhl.whl import api

# Custom configuration
config = api.WHLConfig(default_season='80')

# Get all players
players = api.get_all_players(season='80', config=config)
print(f"Skaters: {len(players['skaters'])}")
print(f"Goalies: {len(players['goalies'])}")
```

### QMJHL Goalie Stats
```python
from scrapernhl.qmjql import api

# Get qualified goalies only
goalies = api.get_goalie_stats(qualified='qualified', limit=20)
for g in goalies['goalies'][:5]:
    print(f"{g['name']}: {g['save_pct']}")
```

### AHL with Pagination
```python
from scrapernhl.ahl import api

# Paginate through all players (100 per page)
all_skaters = []
page = 0
while True:
    stats = api.get_skater_stats(first=page*100, limit=100)
    players = stats.get('players', [])
    if not players:
        break
    all_skaters.extend(players)
    page += 1

print(f"Total skaters: {len(all_skaters)}")
```

## API Structure Consistency

All 5 leagues share **identical API structure** with only configuration differences:

```python
# Same functions across all leagues:
- get_scorebar()
- get_schedule()
- get_game_preview()
- get_game_summary()
- get_play_by_play()
- get_teams()
- get_standings()
- get_roster()
- get_skater_stats()
- get_goalie_stats()
- get_player_profile()
- get_bootstrap()
- get_all_players()
- get_team_schedule()
- get_game_full_data()
```

This allows for **drop-in replacement** between leagues - just change the import!

## Next Steps

1. ✅ **AHL API Key**: Successfully configured with key `ccb91f29d6744675`

2. ✅ **All Keys Verified**: All 5 league API keys tested and confirmed working

3. ✅ **Testing Complete**: Comprehensive test suite passes for all leagues

4. **Explore the Notebook**: Check out `notebooks/multi_league_api_examples.ipynb` for 15+ code examples

5. **Build Applications**: Use the APIs to create hockey analytics applications

## Testing

All APIs have been tested and verified working:

```bash
python test_multi_league_api.py
```

Results:
```
PWHL       ✅ PASS
AHL        ✅ PASS  
OHL        ✅ PASS
WHL        ✅ PASS
QMJHL      ✅ PASS

Total: 5/5 leagues passed
🎉 All league APIs working correctly!
```

## Benefits

✅ **Comprehensive**: All 15+ endpoints covered for each league  
✅ **Consistent**: Identical API across all 5 leagues  
✅ **Paginated**: Support for large datasets with first/limit parameters  
✅ **Filtered**: Team, division, conference, rookies, qualified filters  
✅ **Rate-Limited**: Automatic 2 req/sec enforcement  
✅ **Error-Handled**: Robust error logging and recovery  
✅ **Type-Hinted**: Full type annotations for IDE support  
✅ **Documented**: Comprehensive docstrings with examples  
✅ **Tested**: Full test suite with 100% pass rate

## Quick Reference

### Common Patterns

#### Get Current Games
```python
from scrapernhl.pwhl import api
games = api.get_scorebar(days_ahead=7, days_back=3)
```

#### Get Team Stats with Pagination
```python
stats = api.get_skater_stats(team='5', first=0, limit=50)
```

#### Get Qualified Goalies
```python
goalies = api.get_goalie_stats(qualified='qualified', limit=20)
```

#### Get Standings by Division
```python
standings = api.get_standings(group_by='division', context='overall')
```

#### Get Team Schedule
```python
schedule = api.get_schedule(team_id=2, month=1, location='home')
```

### Available Endpoints

| Category | Function | Description |
|----------|----------|-------------|
| **Games** | `get_scorebar()` | Live games + upcoming schedule |
| | `get_schedule()` | Full season schedule |
| | `get_game_preview()` | Game matchup info |
| | `get_game_summary()` | Game stats & summary |
| | `get_play_by_play()` | Event-level PBP data |
| **Teams** | `get_teams()` | All teams in league |
| | `get_standings()` | League standings |
| | `get_roster()` | Team roster |
| **Players** | `get_skater_stats()` | Skater statistics |
| | `get_goalie_stats()` | Goalie statistics |
| | `get_player_profile()` | Player details |
| **Config** | `get_bootstrap()` | League configuration |
| **Helpers** | `get_all_players()` | All skaters + goalies |
| | `get_team_schedule()` | Team-specific schedule |
| | `get_game_full_data()` | Complete game data |

### Rate Limiting

All API calls are automatically rate-limited to **2 requests per second** using a sliding window algorithm. No manual delays needed!

### Error Handling

All functions include comprehensive error handling:
- HTTP errors are logged and raised
- JSON parsing errors show response preview
- Invalid responses return structured data

### Response Formats

Most endpoints return dictionaries with nested data:
```python
{
    'teams': [...],  # List of teams
    'SiteKit': {...}  # Sometimes wrapped in SiteKit
}
```

The API automatically unwraps common structures like:
- `angular.callbacks._X(...)` - PWHL format
- `(...)` - AHL format
- `SiteKit` wrapper - Various leagues

