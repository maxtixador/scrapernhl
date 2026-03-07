# Basic Scraping Examples

Examples showing how to scrape hockey data using the `HockeyScraper` client.

## Setup

```python
from scrapernhl import HockeyScraper
```

---

## 1. NHL Teams

```python
nhl = HockeyScraper('nhl')

# Active teams from the schedule calendar (default)
teams = nhl.scrape_teams()
print(f"Found {len(teams)} teams")
teams[['abbrev', 'placeName.default', 'commonName.default']].head(10)

# Franchise list with first/last season
teams_franchise = nhl.scrape_teams(source='franchise')

# Franchise list with logos and full details (from Records API)
teams_records = nhl.scrape_teams(source='records')
```

---

## 2. Team Schedule

```python
nhl = HockeyScraper('nhl')

# Montreal Canadiens schedule for 2025-26
schedule = nhl.schedule(team='MTL', season=20252026)
print(f"MTL has {len(schedule)} games")

schedule[['gameDate', 'homeTeam.abbrev', 'homeTeam.score',
          'awayTeam.abbrev', 'awayTeam.score', 'gameState']].head()
```

---

## 3. Standings

```python
nhl = HockeyScraper('nhl')

# Current season standings
standings = nhl.standings()
standings[['teamName.default', 'gamesPlayed', 'wins', 'losses', 'otLosses', 'points']] \
    .sort_values('points', ascending=False).head(10)

# Standings for a specific date
standings_dated = nhl.standings_by_date('2025-12-25')
```

---

## 4. Team Roster

```python
nhl = HockeyScraper('nhl')

roster = nhl.roster(team='MTL', season=20252026)

forwards   = roster[roster['positionCode'].isin(['C', 'L', 'R'])]
defensemen = roster[roster['positionCode'] == 'D']
goalies    = roster[roster['positionCode'] == 'G']

print(f"Forwards: {len(forwards)}, Defense: {len(defensemen)}, Goalies: {len(goalies)}")
forwards[['firstName.default', 'lastName.default', 'positionCode',
          'sweaterNumber', 'heightInInches', 'weightInPounds']].head(10)
```

---

## 5. Player Statistics

```python
nhl = HockeyScraper('nhl')

# Skater stats for a team
skaters = nhl.team_stats(team='MTL', season=20252026, goalies=False)
print("Top 10 scorers:")
skaters.nlargest(10, 'points')[['firstName.default', 'lastName.default',
                                'gamesPlayed', 'goals', 'assists', 'points']]

# Goalie stats
goalies_df = nhl.team_stats(team='MTL', season=20252026, goalies=True)
goalies_df[['firstName.default', 'lastName.default',
            'gamesPlayed', 'wins', 'losses', 'savePercentage']]
```

---

## 6. Play-by-Play Data

```python
nhl = HockeyScraper('nhl')

# JSON API only (fast — no on-ice player lists)
pbp = nhl.play_by_play(2024020001)
print(f"Game has {len(pbp)} events")

pbp['typeDescKey'].value_counts().head(10)
pbp[['periodDescriptor.number', 'timeInPeriod', 'typeDescKey']].head(10)

# Full pipeline (HTML + JSON merged, includes on-ice player lists)
full_pbp = nhl.scrape_game(2024020001)
print(full_pbp.columns.tolist())
```

---

## 7. Draft Data

```python
nhl = HockeyScraper('nhl')

# First round only
r1 = nhl.draft(year=2024, round=1)
print(f"2024 Round 1: {len(r1)} picks")
r1[['round', 'pickInRound', 'overallPick', 'teamAbbrev',
    'firstName.default', 'lastName.default', 'positionCode']].head(10)

# All rounds
draft_all = nhl.draft(year=2024, round='all')
print(f"2024 Draft total picks: {len(draft_all)}")
```

---

## 8. Non-NHL Leagues

All non-NHL leagues share the same method signatures:

```python
ahl = HockeyScraper('ahl')

# Standings
standings = ahl.standings(season=90)

# Skater stats
skaters = ahl.player_stats(season=90, position='skaters')
goalies = ahl.player_stats(season=90, position='goalies')

# Schedule
schedule = ahl.schedule(season=90)

# Roster — requires a numeric team ID from bootstrap
teams = ahl.teams      # list of dicts with 'id', 'name', ...
roster = ahl.roster(team=str(teams[0]['id']))

# Play-by-play
pbp = ahl.play_by_play(1027781)

# Same pattern for PWHL, OHL, WHL, QMJHL
pwhl = HockeyScraper('pwhl')
pwhl_standings = pwhl.standings()
```

### Bootstrap Accessors (non-NHL)

```python
ahl = HockeyScraper('ahl')

# Current season and league IDs
print(ahl.current_season_id)    # e.g. '90'
print(ahl.current_league_id)    # e.g. '6'

# Teams, seasons, divisions
teams       = ahl.get_teams()
seasons     = ahl.get_seasons('regular')  # 'regular', 'playoff', or 'all'
season      = ahl.get_current_season()
conferences = ahl.get_conferences()
divisions   = ahl.get_divisions()

# Look up a team by ID or code
team_by_id   = ahl.get_team_by_id('390')
team_by_code = ahl.get_team_by_code('MIL')
```

---

## 9. Scraping Multiple Games

```python
nhl = HockeyScraper('nhl')

game_ids = [2024020001, 2024020002, 2024020003]
pbp_all = nhl.scrape_multiple_games(game_ids)
print(f"Total events across {len(game_ids)} games: {len(pbp_all)}")
print(pbp_all['game_id'].value_counts())
```

---

## 10. Functional API (One-Liner)

```python
from scrapernhl import scrape

pbp      = scrape('ahl', 'pbp', game_id=1027781)
stats    = scrape('ahl', 'stats', season=90, position='skaters')
schedule = scrape('nhl', 'schedule', team='MTL', season=20232024)
```

---

## See Also

- [Advanced Examples](advanced.md) - NHL analytics pipeline
- [Data Export](export.md) - Saving data to files
- [API Reference](../api.md) - Complete API documentation
