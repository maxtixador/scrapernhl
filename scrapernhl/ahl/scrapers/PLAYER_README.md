# AHL Player Scrapers

This module provides comprehensive player data scrapers for the American Hockey League (AHL).

## Overview

The player scraper module allows you to fetch:
- **Player biographical information** (name, position, birth info, physical stats)
- **Season statistics** (current season performance)
- **Career statistics** (stats across all seasons/leagues)
- **Game-by-game logs** (individual game performance)
- **Shot location data** (coordinate data for shot analysis)
- **Draft information** (NHL draft details)

## API Endpoint

The player scrapers use the HockeyTech API endpoint:
```
https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player
```

## Installation

```python
from scrapernhl.ahl.scrapers import (
    get_player_profile,
    get_player_bio,
    get_player_stats,
    scrape_player_profile,
    scrape_player_stats,
    scrape_player_career_stats,
    scrape_player_game_log,
    scrape_player_shot_locations,
    scrape_multiple_players
)
```

## Quick Start

### Get Player Profile (Raw Data)

```python
from scrapernhl.ahl.scrapers import get_player_profile

# Get complete player profile
profile = get_player_profile(player_id=10036)

# Access different sections
bio = profile['info']
career_stats = profile['careerStats']
game_log = profile['gameByGame']
```

### Get Player Stats as DataFrame

```python
from scrapernhl.ahl.scrapers import scrape_player_stats

# Get current season stats
stats_df = scrape_player_stats(player_id=10036)
print(stats_df[['gamesPlayed', 'goals', 'assists', 'points']])
```

### Get Career Statistics

```python
from scrapernhl.ahl.scrapers import scrape_player_career_stats

# Get career stats by season
career_df = scrape_player_career_stats(player_id=10036)
print(career_df[['season', 'league', 'team', 'gamesPlayed', 'points']])
```

### Get Game-by-Game Log

```python
from scrapernhl.ahl.scrapers import scrape_player_game_log

# Get game log for current season
game_log_df = scrape_player_game_log(player_id=10036)
print(f"Games played: {len(game_log_df)}")
```

### Get Shot Locations

```python
from scrapernhl.ahl.scrapers import scrape_player_shot_locations

# Get shot coordinate data
shots_df = scrape_player_shot_locations(player_id=10036)

# Visualize shot locations
import matplotlib.pyplot as plt
plt.scatter(shots_df['x'], shots_df['y'], alpha=0.5)
plt.title('Shot Locations')
plt.show()
```

### Scrape Multiple Players

```python
from scrapernhl.ahl.scrapers import scrape_multiple_players

# Get data for multiple players
player_ids = [10036, 10037, 10038]
players_df = scrape_multiple_players(player_ids, include_stats=True)

print(f"Scraped {len(players_df)} players")
```

## Available Functions

### Raw Data Fetchers (Return Dict/List)

- `get_player_profile(player_id, season_id, stats_type, config)` - Complete player profile
- `get_player_bio(player_id, season_id, config)` - Biographical info only
- `get_player_stats(player_id, season_id, config)` - Season/career stats
- `get_player_game_log(player_id, season_id, config)` - Game-by-game data
- `get_player_shot_locations(player_id, season_id, config)` - Shot coordinates
- `get_player_draft_info(player_id, season_id, config)` - NHL draft data

### DataFrame Scrapers (Return pandas DataFrame)

- `scrape_player_profile(player_id, season_id, config)` - Bio as DataFrame
- `scrape_player_stats(player_id, season_id, config)` - Season stats as DataFrame
- `scrape_player_career_stats(player_id, season_id, config)` - Career stats as DataFrame
- `scrape_player_game_log(player_id, season_id, config)` - Game log as DataFrame
- `scrape_player_shot_locations(player_id, season_id, config)` - Shots as DataFrame
- `scrape_multiple_players(player_ids, season_id, config, include_stats)` - Multiple players

## Parameters

### Common Parameters

- `player_id` (int): AHL player ID
- `season_id` (int/str, optional): Season ID (defaults to current season)
- `stats_type` (str): Type of stats ('standard', 'bio')
- `config` (AHLConfig, optional): Custom API configuration

### scrape_multiple_players Additional Parameters

- `player_ids` (list[int]): List of player IDs to scrape
- `include_stats` (bool): Include current season stats (default: True)

## Examples

### Example 1: Player Performance Analysis

```python
from scrapernhl.ahl.scrapers import scrape_player_game_log
import pandas as pd

# Get game log
game_log = scrape_player_game_log(10036)

# Calculate cumulative points
game_log['cumulative_points'] = game_log['points'].cumsum()

# Get recent form (last 5 games)
recent_form = game_log.tail(5)
print(f"Points in last 5 games: {recent_form['points'].sum()}")
```

### Example 2: Shot Analysis

```python
from scrapernhl.ahl.scrapers import scrape_player_shot_locations

# Get shots
shots = scrape_player_shot_locations(10036)

# Separate goals from other shots
if 'outcome' in shots.columns:
    goals = shots[shots['outcome'] == 'goal']
    shooting_pct = len(goals) / len(shots) * 100
    print(f"Shooting %: {shooting_pct:.1f}%")
```

### Example 3: Career Progression

```python
from scrapernhl.ahl.scrapers import scrape_player_career_stats

# Get career stats
career = scrape_player_career_stats(10036)

# Filter to AHL seasons only
ahl_seasons = career[career['league'] == 'AHL']

# Calculate points per game by season
ahl_seasons['ppg'] = ahl_seasons['points'] / ahl_seasons['gamesPlayed']
print(ahl_seasons[['season', 'team', 'gamesPlayed', 'points', 'ppg']])
```

### Example 4: Team Comparison

```python
from scrapernhl.ahl.scrapers import scrape_multiple_players
from scrapernhl.ahl.api import get_roster

# Get roster
roster = get_roster(team_id=2)
player_ids = [p['id'] for p in roster.get('players', [])]

# Scrape all players
team_stats = scrape_multiple_players(player_ids, include_stats=True)

# Sort by points
top_scorers = team_stats.nlargest(10, 'points')
print(top_scorers[['name', 'position', 'gamesPlayed', 'goals', 'assists', 'points']])
```

## Data Structure

### Player Profile Response

```json
{
  "info": {
    "name": "Player Name",
    "firstName": "First",
    "lastName": "Last",
    "position": "D",
    "jerseyNumber": "5",
    "birthDate": "2001-10-07",
    "birthplace": "City, Country",
    "height": "6'2\"",
    "weight": 192,
    "shoots": "R",
    "currentTeam": "Team Name"
  },
  "draft": {
    "draftYear": 2023,
    "round": 1,
    "overall": 5,
    "team": "NHL Team"
  },
  "seasonStats": {
    "gamesPlayed": 45,
    "goals": 5,
    "assists": 15,
    "points": 20,
    "plusMinus": 8,
    "pim": 24
  },
  "careerStats": [...],
  "gameByGame": [...],
  "shotLocations": [...]
}
```

## Notes

- All functions support custom AHL API configuration via the `config` parameter
- Season IDs default to the current AHL season if not specified
- DataFrame scrapers automatically flatten nested JSON structures
- Multiple player scraping includes error handling for individual failures
- Shot location data includes coordinate data for spatial analysis

## See Also

- [AHL API Examples Notebook](../../../notebooks/ahl_player_examples.ipynb) - Full examples with visualizations
- [AHL API Module](../api.py) - Core API functions
- [AHL Scrapers](README.md) - Overview of all AHL scrapers

## Support

For issues or questions:
1. Check the example notebook for usage patterns
2. Review the function docstrings for parameter details
3. Ensure you have the correct player IDs (from roster or search endpoints)
