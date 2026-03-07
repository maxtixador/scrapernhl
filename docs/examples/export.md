# Data Export Examples

Learn how to save scraped data to various file formats.

## Setup

```python
import pandas as pd
import os
from datetime import datetime
from scrapernhl import HockeyScraper

# Create output directory
os.makedirs('output', exist_ok=True)
```

---

## Export to CSV

```python
nhl = HockeyScraper('nhl')

# Scrape teams
teams = nhl.scrape_teams()
teams.to_csv('output/nhl_teams.csv', index=False)
print(f"Saved {len(teams)} teams to output/nhl_teams.csv")

# Scrape schedule
schedule = nhl.schedule(team='MTL', season=20252026)
schedule.to_csv('output/mtl_schedule.csv', index=False)
print(f"Saved {len(schedule)} games to output/mtl_schedule.csv")
```

---

## Export to Excel (Multiple Sheets)

```python
nhl = HockeyScraper('nhl')

standings = nhl.standings()
skaters   = nhl.team_stats(team='MTL', season=20252026, goalies=False)
goalies   = nhl.team_stats(team='MTL', season=20252026, goalies=True)

with pd.ExcelWriter('output/nhl_data.xlsx', engine='openpyxl') as writer:
    standings.to_excel(writer, sheet_name='Standings', index=False)
    skaters.to_excel(writer, sheet_name='Skaters', index=False)
    goalies.to_excel(writer, sheet_name='Goalies', index=False)

print("Saved Excel file with 3 sheets to output/nhl_data.xlsx")
```

---

## Export to JSON

```python
nhl = HockeyScraper('nhl')

pbp = nhl.play_by_play(2024020001)

# Pretty printed
pbp.to_json('output/game_pbp.json', orient='records', indent=2)
print(f"Saved {len(pbp)} events to output/game_pbp.json")

# JSON lines (more efficient for large files)
pbp.to_json('output/game_pbp.jsonl', orient='records', lines=True)

# Compare file sizes
json_size  = os.path.getsize('output/game_pbp.json')  / 1024
jsonl_size = os.path.getsize('output/game_pbp.jsonl') / 1024
print(f"File sizes: JSON={json_size:.1f}KB, JSONL={jsonl_size:.1f}KB")
```

---

## Export to Parquet (Recommended for Large Datasets)

```python
nhl = HockeyScraper('nhl')

game_ids = [2024020001, 2024020002, 2024020003]
combined = nhl.scrape_multiple_games(game_ids)

# Save as Parquet (compressed)
combined.to_parquet('output/games_pbp.parquet', index=False, compression='snappy')
print(f"Saved {len(combined)} events to output/games_pbp.parquet")

# Verify round-trip
loaded = pd.read_parquet('output/games_pbp.parquet')
print(f"Verified: Loaded {len(loaded)} events")

# Compare size with CSV
combined.to_csv('output/games_pbp.csv', index=False)
parquet_size = os.path.getsize('output/games_pbp.parquet') / 1024
csv_size     = os.path.getsize('output/games_pbp.csv') / 1024
print(f"Parquet={parquet_size:.1f}KB, CSV={csv_size:.1f}KB  "
      f"({100 * (1 - parquet_size/csv_size):.0f}% smaller)")
```

---

## Export to SQLite Database

```python
import sqlite3
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')

teams     = nhl.scrape_teams()
standings = nhl.standings()
schedule  = nhl.schedule(team='MTL', season=20252026)

conn = sqlite3.connect('output/nhl_data.db')
teams.to_sql('teams',     conn, if_exists='replace', index=False)
standings.to_sql('standings', conn, if_exists='replace', index=False)
schedule.to_sql('schedule',  conn, if_exists='replace', index=False)
conn.close()

print("Saved to SQLite: output/nhl_data.db")
print(f"  teams={len(teams)}, standings={len(standings)}, schedule={len(schedule)}")
```

---

## Incremental Append

```python
nhl = HockeyScraper('nhl')

output_file = 'output/incremental_games.csv'
game_ids    = [2024020001, 2024020002, 2024020003]

for gid in game_ids:
    pbp = nhl.play_by_play(gid)
    if os.path.exists(output_file):
        pbp.to_csv(output_file, mode='a', header=False, index=False)
    else:
        pbp.to_csv(output_file, mode='w', header=True, index=False)
    print(f"  Game {gid}: {len(pbp)} events appended")

total = len(pd.read_csv(output_file))
print(f"Total events: {total}")
```

---

## Export Selected Columns

```python
nhl = HockeyScraper('nhl')

roster = nhl.roster(team='MTL', season=20252026)

cols = ['firstName.default', 'lastName.default', 'sweaterNumber',
        'positionCode', 'heightInInches', 'weightInPounds']
roster[cols].to_csv('output/mtl_roster_simple.csv', index=False)
print(f"Saved simplified roster to output/mtl_roster_simple.csv")
```

---

## Non-NHL League Export

```python
from scrapernhl import HockeyScraper

ahl = HockeyScraper('ahl')

# Export AHL standings for the current season
standings = ahl.standings(season=90)
standings.to_csv('output/ahl_standings.csv', index=False)

# Export AHL skater stats
skaters = ahl.player_stats(season=90, position='skaters')
skaters.to_parquet('output/ahl_skaters.parquet', index=False)

print(f"AHL standings: {len(standings)} teams")
print(f"AHL skaters:   {len(skaters)} players")
```

---

## List Exported Files

```python
output_files = sorted(os.listdir('output'))
print(f"Exported {len(output_files)} files:\n")
for f in output_files:
    size = os.path.getsize(os.path.join('output', f)) / 1024
    print(f"  {f:<40} {size:>8.1f} KB")
```

---

## See Also

- [Basic Scraping](scraping.md) - Getting the data
- [Advanced Examples](advanced.md) - Analytics pipeline
- [API Reference](../api.md) - Function documentation
