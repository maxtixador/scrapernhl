# Multi-League API Examples

This guide provides comprehensive examples for using the API modules across all 5 HockeyTech leagues (PWHL, AHL, OHL, WHL, QMJHL).

## Quick Start

All leagues use the **exact same API structure**. Just change the import!

```python
# Choose your league
from scrapernhl.pwhl import api   # PWHL
from scrapernhl.ahl import api    # AHL  
from scrapernhl.ohl import api    # OHL
from scrapernhl.whl import api    # WHL
from scrapernhl.qmjhl import api  # QMJHL

# Same functions for all leagues!
teams = api.get_teams()
games = api.get_scorebar()
stats = api.get_skater_stats()
```

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Player Statistics](#player-statistics)
3. [Team Data](#team-data)
4. [Game Information](#game-information)
5. [Advanced Filtering](#advanced-filtering)
6. [Pagination](#pagination)
7. [Cross-League Analysis](#cross-league-analysis)

---

## Basic Queries

### Get All Teams

```python
from scrapernhl.pwhl import api

# Get all teams for current season
teams = api.get_teams()

# Access team data
team_list = teams.get('teams', [])
for team in team_list:
    print(f"{team['id']}: {team['name']}")
```

### Get Current Games

```python
# Get games from past 3 days and next 7 days
scorebar = api.get_scorebar(days_ahead=7, days_back=3)

games = scorebar.get('games', [])
print(f"Found {len(games)} games")
```

### Get League Standings

```python
# Get standings grouped by division
standings = api.get_standings(
    group_by='division',
    context='overall'
)
```

---

## Player Statistics

### Get Skater Stats

```python
# Basic usage - get first 20 players
stats = api.get_skater_stats(limit=20)

# With team filter
team_stats = api.get_skater_stats(
    team='5',
    limit=50
)

# Rookies only
rookies = api.get_skater_stats(
    rookies=1,
    limit=20
)
```

### Get Goalie Stats

```python
# Get all goalies
goalies = api.get_goalie_stats(limit=50)

# Qualified goalies only
qualified = api.get_goalie_stats(
    qualified='qualified',
    limit=20
)

# By team
team_goalies = api.get_goalie_stats(
    team='5',
    limit=10
)
```

### Get Player Profile

```python
# Get detailed player information
profile = api.get_player_profile(
    player_id=12345,
    season_id='2024-25'
)
```

---

## Team Data

### Get Team Roster

```python
# Get current roster
roster = api.get_roster(
    team_id=2,
    roster_status='undefined'
)

# Active players only
active_roster = api.get_roster(
    team_id=2,
    roster_status='active'
)
```

### Get Team Schedule

```python
# Convenience function for team-specific schedule
schedule = api.get_team_schedule(team_id=2)

# Or use full schedule API
full_schedule = api.get_schedule(
    team_id=2,
    month=-1,          # All months
    location='home'    # Home games only
)
```

---

## Game Information

### Get Game Details

```python
# Get game preview
preview = api.get_game_preview(game_id=12345)

# Get game summary with stats
summary = api.get_game_summary(game_id=12345)

# Get play-by-play
pbp = api.get_play_by_play(game_id=12345)

# Get everything at once
game_data = api.get_game_full_data(game_id=12345)
# Returns: {'preview': ..., 'summary': ..., 'play_by_play': ...}
```

### Get Full Season Schedule

```python
# All games
schedule = api.get_schedule(team_id=-1)

# Specific month (January = 1)
jan_games = api.get_schedule(
    team_id=-1,
    month=1
)

# Home games only
home_games = api.get_schedule(
    team_id=2,
    location='home'
)

# Away games only
away_games = api.get_schedule(
    team_id=2,
    location='away'
)
```

---

## Advanced Filtering

### Combine Multiple Filters

```python
# Team rookies with specific stats type
team_rookies = api.get_skater_stats(
    team='5',
    rookies=1,
    stats_type='standard',
    limit=50
)

# Qualified goalies from specific division
div_goalies = api.get_goalie_stats(
    qualified='qualified',
    division='2',
    limit=20
)
```

### Filter by Context

```python
# Home game standings
home_standings = api.get_standings(
    context='home',
    group_by='division'
)

# Away game standings
away_standings = api.get_standings(
    context='away',
    group_by='division'
)

# Overall standings
overall_standings = api.get_standings(
    context='overall',
    group_by='league'
)
```

---

## Pagination

### Fetch All Players

```python
# Paginate through all players
all_players = []
page = 0
page_size = 100

while True:
    stats = api.get_skater_stats(
        first=page * page_size,
        limit=page_size
    )
    
    players = stats.get('players', [])
    if not players:
        break
    
    all_players.extend(players)
    page += 1
    
    # Optional: add delay to respect rate limits
    # time.sleep(0.5)

print(f"Total players: {len(all_players)}")
```

### Paginate with Filtering

```python
# Get all rookies across multiple pages
all_rookies = []
page = 0

while True:
    rookies = api.get_skater_stats(
        rookies=1,
        first=page * 50,
        limit=50
    )
    
    players = rookies.get('players', [])
    if not players:
        break
    
    all_rookies.extend(players)
    page += 1

print(f"Total rookies: {len(all_rookies)}")
```

---

## Cross-League Analysis

### Compare Across All Leagues

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
    ('QMJHL', qmjql)
]

# Compare team counts
for league_name, api_module in leagues:
    teams = api_module.get_teams()
    team_list = teams.get('teams', [])
    print(f"{league_name}: {len(team_list)} teams")
```

### Multi-League Player Search

```python
def search_player_across_leagues(player_name):
    \"\"\"Search for a player in all leagues.\"\"\"
    results = {}
    
    for league_name, api_module in leagues:
        try:
            # Get all players (using pagination if needed)
            stats = api_module.get_skater_stats(limit=1000)
            players = stats.get('players', [])
            
            # Search for player
            matches = [
                p for p in players 
                if player_name.lower() in p.get('name', '').lower()
            ]
            
            if matches:
                results[league_name] = matches
        
        except Exception as e:
            print(f"Error searching {league_name}: {e}")
    
    return results

# Example usage
results = search_player_across_leagues("Smith")
for league, players in results.items():
    print(f"\\n{league}:")
    for player in players:
        print(f"  - {player['name']}")
```

---

## Convenience Functions

### Get All Players (Skaters + Goalies)

```python
# One call to get both skaters and goalies
all_players = api.get_all_players()

print(f"Skaters: {len(all_players['skaters'])}")
print(f"Goalies: {len(all_players['goalies'])}")
```

### Bootstrap Configuration

```python
# Get league configuration
bootstrap = api.get_bootstrap(page_name='scorebar')

# Game-specific bootstrap
game_config = api.get_bootstrap(
    game_id=12345,
    page_name='gamecenter'
)
```

---

## Custom Configuration

### Use Custom Settings

```python
from scrapernhl.pwhl import api

# Create custom config
config = api.PWHLConfig(
    default_season='2024-25',
    api_key='your_key_if_needed'
)

# Use custom config
teams = api.get_teams(config=config)
stats = api.get_skater_stats(config=config)
```

---

## Error Handling

### Handle API Errors

```python
try:
    stats = api.get_skater_stats(limit=50)
    players = stats.get('players', [])
    
    if not players:
        print("No players found")
    else:
        print(f"Found {len(players)} players")
        
except Exception as e:
    print(f"Error fetching stats: {e}")
```

### Validate Response

```python
def safe_get_teams(api_module):
    \"\"\"Safely get teams with validation.\"\"\"
    try:
        teams = api_module.get_teams()
        
        if not isinstance(teams, dict):
            print("Warning: Unexpected response format")
            return []
        
        team_list = teams.get('teams', [])
        
        if not isinstance(team_list, list):
            print("Warning: Teams is not a list")
            return []
        
        return team_list
    
    except Exception as e:
        print(f"Error: {e}")
        return []

# Usage
teams = safe_get_teams(api)
```

---

## Data Export

### Export to CSV

```python
import pandas as pd

# Get player stats
stats = api.get_skater_stats(limit=100)
players = stats.get('players', [])

# Convert to DataFrame
df = pd.DataFrame(players)

# Export
df.to_csv('player_stats.csv', index=False)
print(f"Exported {len(df)} players to CSV")
```

### Export to JSON

```python
import json

# Get multiple data types
data = {
    'teams': api.get_teams(),
    'standings': api.get_standings(),
    'scorebar': api.get_scorebar()
}

# Export
with open('league_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Data exported to JSON")
```

---

## Best Practices

### 1. Respect Rate Limits

```python
import time

# The API automatically rate limits to 2 req/sec
# But for bulk operations, add delays:

game_ids = [12345, 12346, 12347]
games = []

for game_id in game_ids:
    game = api.get_game_summary(game_id)
    games.append(game)
    time.sleep(0.5)  # Extra safety margin
```

### 2. Cache Results

```python
import pickle
from pathlib import Path

def get_teams_cached(api_module, cache_file='teams_cache.pkl'):
    \"\"\"Get teams with caching.\"\"\"
    cache_path = Path(cache_file)
    
    # Check cache
    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    
    # Fetch and cache
    teams = api_module.get_teams()
    with open(cache_path, 'wb') as f:
        pickle.dump(teams, f)
    
    return teams

# Usage
teams = get_teams_cached(api)
```

### 3. Use Type Checking

```python
from typing import Dict, List, Any

def get_team_names(api_module) -> List[str]:
    \"\"\"Get list of team names.\"\"\"
    teams_data = api_module.get_teams()
    
    if not isinstance(teams_data, dict):
        return []
    
    teams = teams_data.get('teams', [])
    return [team.get('name', 'Unknown') for team in teams]
```

---

## Common Patterns

### Pattern 1: Team Statistics Dashboard

```python
def team_dashboard(api_module, team_id: int):
    \"\"\"Create a simple team dashboard.\"\"\"
    # Get team roster
    roster = api_module.get_roster(team_id=team_id)
    
    # Get team stats
    skaters = api_module.get_skater_stats(team=str(team_id), limit=100)
    goalies = api_module.get_goalie_stats(team=str(team_id), limit=10)
    
    # Get schedule
    schedule = api_module.get_team_schedule(team_id=team_id)
    
    return {
        'roster': roster,
        'skaters': skaters,
        'goalies': goalies,
        'schedule': schedule
    }

# Usage
dashboard = team_dashboard(api, team_id=2)
```

### Pattern 2: League Leaders

```python
def get_scoring_leaders(api_module, limit=10):
    \"\"\"Get top scorers in the league.\"\"\"
    stats = api_module.get_skater_stats(limit=limit)
    players = stats.get('players', [])
    
    # Sort by points (if not already sorted)
    sorted_players = sorted(
        players,
        key=lambda p: p.get('points', 0),
        reverse=True
    )
    
    return sorted_players[:limit]

# Usage
leaders = get_scoring_leaders(api, limit=10)
for i, player in enumerate(leaders, 1):
    name = player.get('name', 'Unknown')
    points = player.get('points', 0)
    print(f"{i}. {name}: {points} points")
```

### Pattern 3: Multi-League Comparison

```python
def compare_league_leaders():
    \"\"\"Compare top scorers across all leagues.\"\"\"
    results = {}
    
    for league_name, api_module in leagues:
        try:
            leaders = get_scoring_leaders(api_module, limit=5)
            results[league_name] = leaders
        except Exception as e:
            print(f"Error getting {league_name} leaders: {e}")
    
    return results

# Usage
comparison = compare_league_leaders()
for league, players in comparison.items():
    print(f"\\n{league} Top 5:")
    for player in players:
        print(f"  {player['name']}: {player.get('points', 0)}P")
```

---

## Next Steps

- Explore the [API Reference](../MULTI_LEAGUE_API_FRAMEWORK.md) for complete endpoint documentation
- Check out the [Jupyter Notebook](../notebooks/multi_league_api_examples.ipynb) for interactive examples
- Review [test_multi_league_api.py](../test_multi_league_api.py) for more usage patterns
- Build your own analytics dashboards and applications!

## Support

For issues or questions:
- Check the main [README](../README.md)
- Review [MULTI_LEAGUE_API_FRAMEWORK.md](../MULTI_LEAGUE_API_FRAMEWORK.md)
- Open an issue on GitHub
