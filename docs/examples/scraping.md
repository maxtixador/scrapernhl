# Basic Scraping Examples

Examples showing how to scrape NHL data.

## Setup

```python
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
```

## 1. Scraping NHL Teams

Retrieve information about all NHL teams including their names, IDs, and locations.

```python
# Import using backward-compatible package-level import
from scrapernhl import scrapeTeams

# Or import directly from NHL module
# from scrapernhl.nhl.scrapers.teams import scrapeTeams

# Get all NHL teams (cached automatically)
teams = scrapeTeams()
print(f"Found {len(teams)} teams")

# Display selected columns
teams[['name.default', 'abbrev','id', 'placeName.default', 'commonName.default']].head(10)
```

## 2. Scraping Team Schedule

Get the complete schedule for a specific team and season, including game dates, opponents, scores, and game states.

```python
from scrapernhl import scrapeSchedule

# Get Montreal Canadiens schedule for current season (with caching)
schedule = scrapeSchedule("MTL", "20252026")
print(f"MTL has {len(schedule)} games this season")

# Show first 5 games with key information
schedule[['gameDate', 'gameType', 'homeTeam.abbrev', 'homeTeam.score',
          'awayTeam.abbrev', 'awayTeam.score', 'gameOutcome.lastPeriodType', 'gameState']].head()
```

## 3. Current Standings

Fetch the league standings for a specific date, including wins, losses, points, and point percentage.

```python
from scrapernhl import scrapeStandings, console
from datetime import datetime

# Get current standings (with progress indication)
today = datetime.now().strftime("%Y-%m-%d")
console.print_info(f"Fetching standings for {today}...")
standings = scrapeStandings(today)

console.print_success(f"Retrieved standings for {len(standings)} teams")
standings[['teamName.default', 'teamAbbrev.default', 'gamesPlayed', 'wins', 'losses', 'otLosses', 'points', 'pointPctg', 'date']].sort_values(by='pointPctg', ascending=False).head(10)
```

## 4. Team Roster

Get the complete roster for a team, including player names, positions, physical attributes, and biographical information.

```python import scrapeRoster, create_table

# Get Montreal Canadiens roster
roster = scrapeRoster("MTL", "20252026")

# Separate by position
forwards = roster[roster['positionCode'].isin(['C', 'L', 'R'])]
defensemen = roster[roster['positionCode'] == 'D']
goalies = roster[roster['positionCode'] == 'G']

print(f"Forwards: {len(forwards)}, Defense: {len(defensemen)}, Goalies: {len(goalies)}")

# Display forwards with formatted table
print("\nForwards:")
forwards[['id', 'firstName.default', 'lastName.default', 'positionCode', 'shootsCatches', 
          'sweaterNumber', 'heightInInches', 'weightInPounds', 'birthDate', 'birthCountry']]
          'sweaterNumber', 'heightInInches', 'weightInPounds', 'birthDate', 'birthCountry']].assign(team="MTL").head(10)
```

## 5. Player Statistics

Scrape player statistics for both skaters and goalies, including goals, assists, points, wins, and save percentage.

```python
from scrapernhl.scrapers.stats import scrapeTeamStats

# Get skater stats
skaters = scrapeTeamStats("MTL", "20252026", session=2, goalies=False)
print("Top 10 scorers:")
skaters.nlargest(10, 'points')[['playerId', 'firstName.default', 'lastName.default', 'positionCode', 
                                'gamesPlayed', 'goals', 'assists', 'points']].assign(pointsPerGame=lambda df: df['points'].div(df['gamesPlayed']))

# Get goalie stats
goalies = scrapeTeamStats("MTL", "20252026", session=2, goalies=True)
print("\nGoalie statistics:")
goalies[['playerId', 'firstName.default', 'lastName.default', 'gamesPlayed', 'wins', 'losses',
         'overtimeLosses', 'goalsAgainstAverage', 'savePercentage']]
```

## 6. Play-by-Play Data

Retrieve detailed play-by-play data for a specific game, including all events like shots, goals, hits, and faceoffs.

```python
from scrapernhl.scrapers.games import scrapePlays

# Get a recent game ID from schedule
completed_games = schedule[schedule['gameState'] == 'OFF']
if len(completed_games) > 0:
    game_id = completed_games.iloc[0]['id']
    print(f"Scraping game {game_id}...")
    
    pbp = scrapePlays(game_id)
    print(f"Game has {len(pbp)} events")
    
    # Show event types
    print("\nEvent counts:")
    pbp['typeDescKey'].value_counts()
    
    # Show first few events
    print("\nFirst 10 events:")
    pbp[['periodDescriptor.number', 'timeInPeriod', 'typeDescKey', 'details.eventOwnerTeamId', 'gameId']].head(10)
else:
    print("No completed games found in schedule")
```

## 7. Draft Data

Access historical NHL draft data including player information, draft position, and team selections.

```python
from scrapernhl.scrapers.draft import scrapeDraftData

# Get 2025 first round picks
draft_2025_r1 = scrapeDraftData("2025", 1)
print(f"2025 Draft - Round 1: {len(draft_2025_r1)} picks")
draft_2025_r1[['round', 'pickInRound', 'overallPick', 'teamAbbrev', 'firstName.default', 'lastName.default',
               'positionCode', 'countryCode', 'height', 'weight', 'year']].head(10)
```

## 8. Using Polars (Alternative to Pandas)

Polars is a faster alternative to Pandas for large datasets. The scraper supports both output formats.

```python
# Get data as Polars DataFrame (faster for large datasets)
teams_pl = scrapeTeams(output_format="polars")
print(f"Type: {type(teams_pl)}")
print(f"Shape: {teams_pl.shape}")

# Polars syntax
teams_pl.select(['name', 'abbrev','id', 'placeName', 'commonName']).head(5)
```

## 9. Backward Compatibility Test

The package maintains backward compatibility with older import styles for ease of migration.

```python
# The old import style still works
from scrapernhl import scrapeTeams, scrapeSchedule

teams_old_style = scrapeTeams()
print(f"Old import style works: {len(teams_old_style)} teams scraped")
```

## See Also

- [Advanced Examples](advanced.md) - Feature engineering, analytics
- [Data Export](export.md) - Saving data to files
- [API Reference](../api.md) - Complete API documentation

```python
from scrapernhl.scrapers.teams import scrapeTeams

# Get all NHL teams
teams = scrapeTeams()
print(f"Found {len(teams)} teams")

# Display selected columns
teams[['name.default', 'abbrev','id', 'placeName.default', 'commonName.default']].head(10)
```

### Scraping Schedule

```python
from scrapernhl.scrapers.schedule import scrapeSchedule

# Get Montreal Canadiens schedule for current season
schedule = scrapeSchedule("MTL", "20252026")
print(f"MTL has {len(schedule)} games this season")

# Show first 5 games with key information
schedule[['gameDate', 'gameType', 'homeTeam.abbrev', 'homeTeam.score',
          'awayTeam.abbrev', 'awayTeam.score', 'gameOutcome.lastPeriodType', 'gameState']].head()
```

### Scraping Standings

```python
from scrapernhl.scrapers.standings import scrapeStandings
from datetime import datetime

# Get current standings
today = datetime.now().strftime("%Y-%m-%d")
standings = scrapeStandings(today)

print(f"Standings as of {today}:")
standings[['teamName.default', 'teamAbbrev.default', 'gamesPlayed', 'wins', 'losses', 'otLosses', 'points', 'pointPctg', 'date']].sort_values(by='pointPctg', ascending=False).head(10)
```

## Getting Play-by-Play Data

```python
from scrapernhl.scrapers.games import scrapePlays

# Get play-by-play for a specific game
game_id = 2024020001
pbp = scrapePlays(game_id)

print(f"Game {game_id} has {len(pbp)} events")

# Show event types
print("\nEvent counts:")
pbp['typeDescKey'].value_counts()

# Show first few events
print("\nFirst 10 events:")
pbp[['periodDescriptor.number', 'timeInPeriod', 'typeDescKey', 'details.eventOwnerTeamId', 'gameId']].head(10)
```

### With Goal Replay Data

```python
from scrapernhl.scrapers.games import scrapePlays

# Include goal replay data
pbp = scrapePlays(2024020001, addGoalReplayData=True)

# Filter for goals only
goals = pbp[pbp['eventType'] == 'goal']
print(f"Goals scored: {len(goals)}")
```

## Scraping Multiple Games

```python
from scrapernhl.scrapers.games import scrapePlays
import pandas as pd

# Scrape multiple games
game_ids = [2024020001, 2024020002, 2024020003]
all_plays = []

for game_id in game_ids:
    print(f"Scraping game {game_id}...")
    pbp = scrapePlays(game_id)
    all_plays.append(pbp)

# Combine all games
combined_pbp = pd.concat(all_plays, ignore_index=True)
print(f"Total events across {len(game_ids)} games: {len(combined_pbp)}")
```

## Getting Roster Information

```python
from scrapernhl.scrapers.roster import scrapeRoster

# Get Montreal Canadiens roster
roster = scrapeRoster("MTL", "20252026")

# Separate by position
forwards = roster[roster['positionCode'].isin(['C', 'L', 'R'])]  # Forwards: Centers, Left Wings, Right Wings
defensemen = roster[roster['positionCode'] == 'D']
goalies = roster[roster['positionCode'] == 'G']

print(f"Forwards: {len(forwards)}, Defense: {len(defensemen)}, Goalies: {len(goalies)}")

print("\nForwards:")
forwards[['id', 'firstName.default', 'lastName.default', 'positionCode', 'shootsCatches', 
          'sweaterNumber', 'heightInInches', 'weightInPounds', 'birthDate', 'birthCountry']].assign(team="MTL").head(10)
```

## Getting Player Statistics

```python
from scrapernhl.scrapers.stats import scrapeTeamStats

# Get skater stats
skaters = scrapeTeamStats("MTL", "20252026", session=2, goalies=False)
print("Top 10 scorers:")
skaters.nlargest(10, 'points')[['playerId', 'firstName.default', 'lastName.default', 'positionCode', 
                                'gamesPlayed', 'goals', 'assists', 'points']].assign(pointsPerGame=lambda df: df['points'].div(df['gamesPlayed']))

# Get goalie stats
goalies = scrapeTeamStats("MTL", "20252026", session=2, goalies=True)
print("\nGoalie statistics:")
goalies[['playerId', 'firstName.default', 'lastName.default', 'gamesPlayed', 'wins', 'losses',
         'overtimeLosses', 'goalsAgainstAverage', 'savePercentage']]
```

## Getting Draft Data

```python
from scrapernhl.scrapers.draft import scrapeDraftData

# Get 2025 first round picks
draft_2025_r1 = scrapeDraftData("2025", 1)
print(f"2025 Draft - Round 1: {len(draft_2025_r1)} picks")
draft_2025_r1[['round', 'pickInRound', 'overallPick', 'teamAbbrev', 'firstName.default', 'lastName.default',
               'positionCode', 'countryCode', 'height', 'weight', 'year']].head(10)
```

## Using Polars Instead of Pandas

```python
# Get data as Polars DataFrame (faster for large datasets)
teams_pl = scrapeTeams(output_format="polars")
print(f"Type: {type(teams_pl)}")
print(f"Shape: {teams_pl.shape}")

# Polars syntax
teams_pl.select(['name', 'abbrev','id', 'placeName', 'commonName']).head(5)
```

## Backward Compatible Style

If you have existing code, the old import style still works:

```python
# The old import style still works
from scrapernhl import scrapeTeams, scrapeSchedule

teams_old_style = scrapeTeams()
print(f"Old import style works: {len(teams_old_style)} teams scraped")
```

## Error Handling

```python
from scrapernhl.nhl.scrapers.games import scrapePlays
from scrapernhl.exceptions import InvalidGameError

try:
    pbp = scrapePlays(9999999999)  # Invalid game ID
except InvalidGameError as e:
    print(f"Error scraping game: {e}")
```

## 10. Player Stats (Phase 3)

New player scraping functions with progress bars and caching.

### Player Profile

```python
from scrapernhl import scrapePlayerProfile, console

# Get player profile (Auston Matthews)
player_id = 8478402
console.print_info(f"Fetching profile for player {player_id}...")
profile = scrapePlayerProfile(player_id)

if not profile.empty:
    console.print_success("Profile retrieved!")
    print(f"\nName: {profile['firstName.default'].iloc[0]} {profile['lastName.default'].iloc[0]}")
    print(f"Position: {profile['position'].iloc[0]}")
    print(f"Team: {profile['fullTeamName.default'].iloc[0]}")
    print(f"Birth Date: {profile['birthDate'].iloc[0]}")
```

### Player Season Stats

```python
from scrapernhl import scrapePlayerSeasonStats

# Get season stats
stats = scrapePlayerSeasonStats(8478402, "20232024")

if not stats.empty:
    print(f"\n2023-24 Season:")
    print(f"  GP: {stats['gamesPlayed'].iloc[0]}")
    print(f"  G: {stats['goals'].iloc[0]}")
    print(f"  A: {stats['assists'].iloc[0]}")
    print(f"  PTS: {stats['points'].iloc[0]}")
```

### Player Game Log

```python
from scrapernhl import scrapePlayerGameLog

# Get game-by-game log
gamelog = scrapePlayerGameLog(8478402, "20232024")

print(f"\nGame Log: {len(gamelog)} games")
print(f"Total Goals: {gamelog['goals'].sum()}")
print(f"Total Points: {gamelog['points'].sum()}")

# Show recent games
gamelog[['gameDate', 'opponentAbbrev', 'goals', 'assists', 'points', 'toi']].head(5)
```

### Multiple Players (Batch)

```python
from scrapernhl import scrapeMultiplePlayerStats

# Get stats for multiple players with progress bar
player_ids = [8478402, 8479318, 8471214, 8477492, 8478550]  # Matthews, McDavid, Crosby, Pastrnak, Draisaitl
all_stats = scrapeMultiplePlayerStats(player_ids, "20232024")

# Show top scorers
print(f"\nFetched stats for {len(all_stats)} players")
all_stats.sort_values('points', ascending=False)[['firstName.default', 'lastName.default', 'points', 'goals', 'assists']].head()
```

## 11. Batch Scraping (Phase 3)

Parallel scraping with rate limiting and progress bars.

```python
from scrapernhl import BatchScraper, console

# Create batch scraper
scraper = BatchScraper(
    max_workers=5,          # Parallel workers
    rate_limit=10.0,        # Max 10 requests/second
    max_retries=3,          # Retry failed requests
    show_progress=True      # Show progress bar
)

# Scrape multiple games
game_ids = [2023020001, 2023020002, 2023020003, 2023020004, 2023020005]
from scrapernhl.nhl.scrapers.games import getGameData

console.print_info(f"Scraping {len(game_ids)} games in parallel...")
result = scraper.scrape_batch(game_ids, getGameData)

console.print_success(f"Successfully scraped {len(result.successful)} games")
if result.failed:
    console.print_warning(f"Failed: {len(result.failed)} games")
```

## Async Scraping (Advanced)

For scraping multiple games efficiently:

```python
import asyncio
from scrapernhl import scrape_game_async

async def scrape_multiple_games(game_ids):
    tasks = [scrape_game_async(game_id) for game_id in game_ids]
    results = await asyncio.gather(*tasks)
    return results

# Run async scraping
game_ids = [2024020001, 2024020002, 2024020003]
results = asyncio.run(scrape_multiple_games(game_ids))
print(f"Scraped {len(results)} games")
```

## See Also

- [Advanced Examples](advanced.md) - Feature engineering, analytics
- [Data Export](export.md) - Saving data to files
- [API Reference](../api.md) - Complete API documentation
