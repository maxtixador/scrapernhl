# Multi-League API Quick Reference

Fast reference for all 15 API functions across 5 leagues (PWHL, AHL, OHL, WHL, QMJHL).

## Quick Import

```python
# Pick your league
from scrapernhl.pwhl import api   # or ahl, ohl, whl, qmjhl
```

All functions work identically across all leagues!

---

## Core Functions

### 1. `get_teams(season_id=None)`
Returns all teams in the league.

```python
teams = api.get_teams()
teams = api.get_teams(season_id='2024-25')
```

### 2. `get_scorebar(days_ahead=7, days_back=3)`
Get recent/live/upcoming games.

```python
games = api.get_scorebar()
games = api.get_scorebar(days_ahead=14, days_back=7)
```

### 3. `get_standings(group_by='division', context='overall')`
League standings by division/conference/league.

```python
standings = api.get_standings()
standings = api.get_standings(group_by='conference', context='home')
```

**Parameters:**
- `group_by`: `'division'`, `'conference'`, `'league'`
- `context`: `'overall'`, `'home'`, `'away'`

---

## Player Stats

### 4. `get_skater_stats(...)`
Skater statistics with filtering and pagination.

```python
# Basic
stats = api.get_skater_stats(limit=50)

# By team
stats = api.get_skater_stats(team='5', limit=100)

# Rookies only
stats = api.get_skater_stats(rookies=1, limit=50)

# Pagination
stats = api.get_skater_stats(first=100, limit=50)  # Get players 100-150
```

**Key Parameters:**
- `limit`: Number of players (default 20, max ~1000)
- `first`: Starting offset for pagination
- `team`: Filter by team ID (string)
- `rookies`: `1` for rookies only
- `stats_type`: `'standard'`, `'advanced'`, etc.
- `division`, `conference`: Filter by division/conference ID
- `qualified`: `'qualified'` for qualified players only

### 5. `get_goalie_stats(...)`
Goalie statistics (same parameters as skater stats).

```python
goalies = api.get_goalie_stats(limit=20)
goalies = api.get_goalie_stats(team='5', qualified='qualified')
```

### 6. `get_player_profile(player_id, season_id=None)`
Detailed player information.

```python
profile = api.get_player_profile(player_id=12345)
```

### 7. `get_all_players(limit=1000)`
Convenience function to get both skaters and goalies.

```python
all_players = api.get_all_players()
# Returns: {'skaters': [...], 'goalies': [...]}
```

---

## Game Functions

### 8. `get_schedule(team_id=-1, month=-1, location=None)`
Full season schedule.

```python
# All games
schedule = api.get_schedule()

# Team schedule
schedule = api.get_schedule(team_id=2)

# Specific month (1=January, 12=December)
schedule = api.get_schedule(month=1)

# Home games only
schedule = api.get_schedule(team_id=2, location='home')
```

### 9. `get_team_schedule(team_id)`
Convenience function for team-specific schedule.

```python
schedule = api.get_team_schedule(team_id=2)
```

### 10. `get_game_preview(game_id)`
Game preview with lineups and pregame info.

```python
preview = api.get_game_preview(game_id=12345)
```

### 11. `get_game_summary(game_id)`
Game summary with box score and stats.

```python
summary = api.get_game_summary(game_id=12345)
```

### 12. `get_play_by_play(game_id)`
Detailed play-by-play data.

```python
pbp = api.get_play_by_play(game_id=12345)
```

### 13. `get_game_full_data(game_id)`
All game data in one call (preview + summary + play-by-play).

```python
game_data = api.get_game_full_data(game_id=12345)
# Returns: {'preview': {...}, 'summary': {...}, 'play_by_play': {...}}
```

---

## Team Functions

### 14. `get_roster(team_id, roster_status='undefined')`
Team roster with player details.

```python
# All players
roster = api.get_roster(team_id=2)

# Active players only
roster = api.get_roster(team_id=2, roster_status='active')
```

---

## Configuration

### 15. `get_bootstrap(game_id=None, page_name='scorebar')`
League configuration and metadata.

```python
# General config
config = api.get_bootstrap()

# Game-specific config
config = api.get_bootstrap(game_id=12345, page_name='gamecenter')
```

---

## Common Patterns

### Pattern 1: Team Dashboard

```python
def team_dashboard(team_id):
    roster = api.get_roster(team_id=team_id)
    schedule = api.get_team_schedule(team_id=team_id)
    skaters = api.get_skater_stats(team=str(team_id), limit=100)
    goalies = api.get_goalie_stats(team=str(team_id), limit=10)
    return {
        'roster': roster,
        'schedule': schedule,
        'skaters': skaters,
        'goalies': goalies
    }
```

### Pattern 2: League Leaders

```python
def get_top_scorers(limit=10):
    stats = api.get_skater_stats(limit=limit)
    players = stats.get('players', [])
    return sorted(players, key=lambda p: p.get('points', 0), reverse=True)[:limit]
```

### Pattern 3: Paginate All Players

```python
def get_all_skaters():
    all_players = []
    page = 0
    page_size = 100
    
    while True:
        stats = api.get_skater_stats(first=page * page_size, limit=page_size)
        players = stats.get('players', [])
        if not players:
            break
        all_players.extend(players)
        page += 1
    
    return all_players
```

### Pattern 4: Cross-League Comparison

```python
from scrapernhl.pwhl import api as pwhl
from scrapernhl.ahl import api as ahl
from scrapernhl.ohl import api as ohl
from scrapernhl.whl import api as whl
from scrapernhl.qmjhl import api as qmjhl

leagues = [
    ('PWHL', pwhl),
    ('AHL', ahl),
    ('OHL', ohl),
    ('WHL', whl),
    ('QMJHL', qmjhl)
]

for name, api_module in leagues:
    teams = api_module.get_teams()
    print(f"{name}: {len(teams.get('teams', []))} teams")
```

---

## Parameter Quick Reference

### Common to Most Functions
- `season_id`: Season identifier (e.g., `'2024-25'`), usually optional
- `limit`: Maximum results to return
- `first`: Starting offset for pagination

### Player Stats Specific
- `team`: Team ID as string (e.g., `'5'`)
- `rookies`: `1` for rookies only
- `stats_type`: Type of stats (e.g., `'standard'`, `'advanced'`)
- `qualified`: `'qualified'` for qualified players
- `division`, `conference`: Filter by division/conference

### Schedule Specific
- `team_id`: Team ID as integer, `-1` for all teams
- `month`: Month number (1-12), `-1` for all months
- `location`: `'home'` or `'away'`

### Standings Specific
- `group_by`: `'division'`, `'conference'`, `'league'`
- `context`: `'overall'`, `'home'`, `'away'`

### Roster Specific
- `roster_status`: `'undefined'` (all) or `'active'` (active only)

---

## Response Formats

Most functions return dictionaries with league data. Common structures:

```python
# Teams
{
    'teams': [
        {'id': 1, 'name': 'Team Name', ...},
        ...
    ]
}

# Players (skaters/goalies)
{
    'players': [
        {'id': 123, 'name': 'Player Name', 'goals': 10, ...},
        ...
    ]
}

# Standings
{
    'divisions': [
        {
            'name': 'Division Name',
            'teams': [
                {'name': 'Team', 'wins': 20, 'losses': 5, ...},
                ...
            ]
        }
    ]
}

# Games (scorebar/schedule)
{
    'games': [
        {'id': 12345, 'home_team': '...', 'away_team': '...', ...},
        ...
    ]
}
```

---

## Tips

1. **Rate Limiting**: API automatically limits to ~2 requests/second
2. **Pagination**: Use `first` and `limit` for large datasets
3. **Team IDs**: Often need to be strings, not integers
4. **Error Handling**: Always check response structure (formats can vary)
5. **Caching**: Consider caching team/config data (changes infrequently)
6. **Season IDs**: Usually optional, defaults to current season

---

## Full Documentation

- Complete guide: [Multi-League API Examples](multi-league-api-examples.md)
- Framework details: [MULTI_LEAGUE_API_FRAMEWORK.md](../MULTI_LEAGUE_API_FRAMEWORK.md)
- Interactive examples: [multi_league_api_examples.ipynb](../notebooks/multi_league_api_examples.ipynb)
- Test suite: [test_multi_league_api.py](../test_multi_league_api.py)

---

## Getting Started

1. Import the league you want:
   ```python
   from scrapernhl.pwhl import api
   ```

2. Make your first call:
   ```python
   teams = api.get_teams()
   print(f"Found {len(teams.get('teams', []))} teams")
   ```

3. Explore more functions:
   ```python
   stats = api.get_skater_stats(limit=20)
   standings = api.get_standings()
   games = api.get_scorebar()
   ```

That's it! Same API for all 5 leagues.
