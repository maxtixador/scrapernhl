# AHL Player API Information

## Endpoint

```
https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player
```

## Required Parameters

- `player_id`: Player identifier (integer)
- `season_id`: Season identifier (integer, e.g., 90 for current season)
- `site_id`: Site identifier (3 for AHL)
- `key`: API key (ccb91f29d6744675)
- `client_code`: Client code (ahl)
- `league_id`: League ID (4 for AHL)
- `lang`: Language (en)
- `statsType`: Type of stats (standard, bio)

## Example Request

```
https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player&player_id=10036&season_id=90&site_id=3&key=ccb91f29d6744675&client_code=ahl&league_id=&lang=en&statsType=standard&callback=angular.callbacks._2
```

## Response Structure

### Top-Level Keys

The API returns a JSONP response that contains the following main sections:

```json
{
  "SiteKit": {
    "info": {},           // Biographical information
    "seasonStats": {},    // Current season statistics
    "careerStats": [],    // Career statistics by season
    "gameByGame": [],     // Game-by-game breakdown
    "shotLocations": [],  // Shot coordinate data
    "draft": {},          // NHL draft information
    "media": {},          // Player photos/images
    "seasons": []         // Available seasons
  }
}
```

### 1. Biographical Information (`info`)

Player biographical data including:

```json
{
  "id": 10036,
  "name": "David Reinbacher",
  "firstName": "David",
  "lastName": "Reinbacher",
  "jerseyNumber": "5",
  "position": "D",
  "positionLong": "Defense",
  "birthDate": "2001-10-07",
  "birthplace": "Vienna, AUT",
  "height": "6'2\"",
  "heightInches": 74,
  "weight": 192,
  "shoots": "R",
  "currentTeam": "Laval Rocket",
  "currentTeamId": 1063,
  "rookie": true,
  "socialMedia": {
    "twitter": "",
    "instagram": "",
    "facebook": ""
  }
}
```

### 2. Season Statistics (`seasonStats`)

Current season performance:

```json
{
  "season": "2024-25",
  "teamName": "Laval Rocket",
  "gamesPlayed": 28,
  "goals": 3,
  "assists": 9,
  "points": 12,
  "plusMinus": 5,
  "penaltyMinutes": 14,
  "shots": 45,
  "shootingPercentage": 6.7,
  "powerPlayGoals": 1,
  "powerPlayAssists": 3,
  "shorthandedGoals": 0,
  "shorthandedAssists": 0,
  "gameWinningGoals": 0,
  "overtimeGoals": 0,
  "blockedShots": 32,
  "hits": 45,
  "faceoffWins": 0,
  "faceoffLosses": 0,
  "faceoffPercentage": 0.0,
  "timeOnIce": "18:45",
  "timeOnIcePerGame": "18:45"
}
```

### 3. Career Statistics (`careerStats`)

Array of season-by-season statistics across all leagues:

```json
[
  {
    "season": "2024-25",
    "league": "AHL",
    "team": "Laval Rocket",
    "gamesPlayed": 28,
    "goals": 3,
    "assists": 9,
    "points": 12,
    "plusMinus": 5,
    "penaltyMinutes": 14
  },
  {
    "season": "2023-24",
    "league": "NHL",
    "team": "Montreal Canadiens",
    "gamesPlayed": 11,
    "goals": 0,
    "assists": 1,
    "points": 1,
    "plusMinus": -6,
    "penaltyMinutes": 2
  }
]
```

### 4. Game-by-Game Log (`gameByGame`)

Individual game performance data:

```json
[
  {
    "gameId": 1028297,
    "gameDate": "2024-10-12",
    "opponent": "Belleville Senators",
    "homeAway": "H",
    "opponentId": 1064,
    "result": "W",
    "score": "4-1",
    "goals": 0,
    "assists": 1,
    "points": 1,
    "plusMinus": 2,
    "penaltyMinutes": 0,
    "shots": 2,
    "timeOnIce": "19:23",
    "powerPlayGoals": 0,
    "powerPlayAssists": 0,
    "shorthandedGoals": 0,
    "shorthandedAssists": 0
  }
]
```

### 5. Shot Locations (`shotLocations`)

Shot coordinate data for spatial analysis:

```json
[
  {
    "gameId": 1028297,
    "period": 2,
    "time": "12:34",
    "x": 65,
    "y": 25,
    "outcome": "shot",
    "type": "wrist",
    "strength": "ev",
    "quality": "high"
  },
  {
    "gameId": 1028297,
    "period": 3,
    "time": "05:12",
    "x": 70,
    "y": -15,
    "outcome": "goal",
    "type": "slap",
    "strength": "pp",
    "quality": "high"
  }
]
```

### 6. Draft Information (`draft`)

NHL draft details:

```json
{
  "draftYear": 2023,
  "round": 1,
  "overall": 5,
  "team": "Montréal Canadiens",
  "teamId": 8,
  "teamLogo": "https://..."
}
```

### 7. Media Assets (`media`)

Player photos and images:

```json
{
  "headshot": "https://assets.leaguestat.com/ahl/240x240/10036.jpg",
  "action": "https://assets.leaguestat.com/ahl/640x480/10036.jpg",
  "profile": "https://assets.leaguestat.com/ahl/1280x720/10036.jpg"
}
```

## Data Types by Position

### Skaters (Forwards/Defensemen)

All skaters receive:
- Biographical info
- Standard statistics (goals, assists, points, +/-, PIM)
- Advanced stats (shots, shooting %, TOI, hits, blocks)
- Special teams stats (PP, SH)
- Game-by-game logs
- Shot locations

### Goalies

Goalies receive different statistics:
- Biographical info
- Goalie-specific stats (wins, saves, GAA, SV%)
- Game-by-game logs
- Shot locations against

## statsType Parameter

The `statsType` parameter controls the level of detail:

- `standard`: Full profile with all stats and game logs
- `bio`: Biographical information only (faster, lighter)

## Rate Limiting

The AHL API has rate limiting:
- 2 calls per second
- Automatic retry on rate limit errors
- Built-in rate limiting in the scraper functions

## Notes

1. **Player IDs**: Can be found from roster endpoints or team pages
2. **Season IDs**: Current season is 90, previous seasons have lower IDs
3. **Response Format**: JSONP wrapped (automatically cleaned by scrapers)
4. **Missing Data**: Some fields may be null/empty for certain players
5. **Rookie Status**: Determined by games played in previous seasons
6. **Shot Coordinates**: X/Y coordinates are relative to rink dimensions
7. **Time Format**: Time on ice is formatted as "MM:SS"

## Finding Player IDs

### Method 1: From Roster

```python
from scrapernhl.ahl.api import get_roster

roster = get_roster(team_id=2)
for player in roster.get('players', []):
    print(f"{player['name']}: {player['id']}")
```

### Method 2: From Player Stats

```python
from scrapernhl.ahl.api import get_skater_stats

stats = get_skater_stats(limit=100)
for player in stats.get('players', []):
    print(f"{player['name']}: {player['id']}")
```

### Method 3: From Schedule/Game Data

Game rosters include player IDs for all players who participated.

## Related Endpoints

- `/roster` - Team rosters with player IDs
- `/players` - League-wide player statistics
- `/goalies` - Goalie-specific statistics
- `/gameSummary` - Game data including player participation

## Examples

See the example notebook for complete usage examples:
[ahl_player_examples.ipynb](../../../notebooks/ahl_player_examples.ipynb)
