# Command-Line Interface (CLI) Examples

The ScraperNHL CLI allows you to scrape multi-league hockey data directly from the command line without writing any Python code. This is perfect for quick data exports, shell scripts, cron jobs, and automated workflows.

## Supported Leagues

ScraperNHL CLI supports 6 hockey leagues:

- **NHL** - National Hockey League
- **PWHL** - Professional Women's Hockey League
- **AHL** - American Hockey League
- **OHL** - Ontario Hockey League
- **WHL** - Western Hockey League
- **QMJHL** - Quebec Maritimes Junior Hockey League

## Getting Started

View available commands:

```bash
python scrapernhl/cli.py --help
```

Output:
```
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

  ScraperNHL - Command-line interface for multi-league hockey data scraping.
  
  Scrape NHL, PWHL, AHL, OHL, WHL, and QMJHL data including teams, schedules, 
  standings, rosters, stats, and games directly from the command line.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  ahl        AHL (American Hockey League) commands.
  draft      Scrape NHL draft data.
  game       Scrape play-by-play data for a specific game.
  ohl        OHL (Ontario Hockey League) commands.
  pwhl       PWHL (Professional Women's Hockey League) commands.
  qmjhl      QMJHL (Quebec Maritimes Junior Hockey League) commands.
  roster     Scrape team roster.
  schedule   Scrape team schedule.
  standings  Scrape NHL standings.
  stats      Scrape team player statistics.
  teams      Scrape all NHL teams.
  whl        WHL (Western Hockey League) commands.
```

## Output Formats

All commands support multiple output formats via the `--format` flag:

- `csv` (default) - Comma-separated values
- `json` - JSON format
- `parquet` - Compressed Parquet format (best for large datasets)
- `excel` - Excel spreadsheet (.xlsx)

Example:
```bash
python scrapernhl/cli.py teams --format json --output teams.json
```

## Teams Command

Scrape information about all NHL teams.

### Basic Usage

```bash
# Default: saves to nhl_teams.csv
python scrapernhl/cli.py teams

# Specify custom output file
python scrapernhl/cli.py teams --output my_teams.csv

# Export as JSON
python scrapernhl/cli.py teams --format json --output teams.json

# Export as Parquet
python scrapernhl/cli.py teams --format parquet --output teams.parquet

# Use Polars instead of Pandas (faster for large datasets)
python scrapernhl/cli.py teams --polars
```

### Example Output

```
Scraping NHL teams...
Successfully scraped 32 teams
Saved to: nhl_teams.csv
```

## Schedule Command

Scrape a team's schedule for a specific season.

### Basic Usage

```bash
python scrapernhl/cli.py schedule TEAM SEASON [OPTIONS]
```

**Arguments:**
- `TEAM` - Team abbreviation (e.g., MTL, TOR, BOS, NYR)
- `SEASON` - Season in format YYYYYYYY (e.g., 20252026)

### Examples

```bash
# Montreal Canadiens 2025-26 schedule
python scrapernhl/cli.py schedule MTL 20252026

# Toronto Maple Leafs with custom output
python scrapernhl/cli.py schedule TOR 20252026 --output tor_schedule.csv

# Boston Bruins as JSON
python scrapernhl/cli.py schedule BOS 20252026 --format json

# Vegas Golden Knights as Parquet
python scrapernhl/cli.py schedule VGK 20252026 --format parquet
```

### Example Output

```
Scraping MTL schedule for 20252026...
Successfully scraped 82 games
Saved to: mtl_schedule_20252026.csv
```

## Standings Command

Scrape NHL standings for a specific date.

### Basic Usage

```bash
# Current standings (uses today's date)
python scrapernhl/cli.py standings

# Standings for specific date (YYYY-MM-DD)
python scrapernhl/cli.py standings 2025-12-25

# Export to different format
python scrapernhl/cli.py standings --format json --output standings.json
```

### Examples

```bash
# Get current standings
python scrapernhl/cli.py standings

# Standings on Christmas 2025
python scrapernhl/cli.py standings 2025-12-25

# Save to custom file
python scrapernhl/cli.py standings --output current_standings.csv
```

### Example Output

```
Scraping NHL standings for 2026-01-01...
Successfully scraped standings for 32 teams
Saved to: nhl_standings_2026-01-01.csv
```

## Roster Command

Scrape a team's roster for a specific season.

### Basic Usage

```bash
python scrapernhl/cli.py roster TEAM SEASON [OPTIONS]
```

### Examples

```bash
# Montreal Canadiens roster
python scrapernhl/cli.py roster MTL 20252026

# Edmonton Oilers roster as JSON
python scrapernhl/cli.py roster EDM 20252026 --format json

# Custom output file
python scrapernhl/cli.py roster TOR 20252026 --output leafs_roster.csv
```

### Example Output

```
Scraping MTL roster for 20252026...
Successfully scraped 28 players
Saved to: mtl_roster_20252026.csv
```

## Stats Command

Scrape player statistics for a team.

### Basic Usage

```bash
python scrapernhl/cli.py stats TEAM SEASON [OPTIONS]
```

### Options

- `--goalies` - Scrape goalie stats instead of skater stats
- `--session` - Session type (2=regular season, 3=playoffs, default: 2)

### Examples

```bash
# Skater stats (default)
python scrapernhl/cli.py stats MTL 20252026

# Goalie stats
python scrapernhl/cli.py stats MTL 20252026 --goalies

# Playoff stats
python scrapernhl/cli.py stats TOR 20252026 --session 3

# Combined example: playoff goalie stats
python scrapernhl/cli.py stats BOS 20252026 --goalies --session 3

# Export to JSON
python scrapernhl/cli.py stats NYR 20252026 --format json
```

### Example Output

```
Scraping MTL skaters stats for 20252026...
Successfully scraped stats for 23 skaters
Saved to: mtl_skaters_20252026.csv
```

## Game Command

Scrape play-by-play data for a specific game.

### Basic Usage

```bash
python scrapernhl/cli.py game GAME_ID [OPTIONS]
```

**Arguments:**
- `GAME_ID` - NHL game ID (e.g., 2024020001)

### Options

- `--with-xg` - Include expected goals (xG) predictions for shot events

### Examples

```bash
# Basic play-by-play
python scrapernhl/cli.py game 2024020001

# With expected goals analysis
python scrapernhl/cli.py game 2024020001 --with-xg

# Export to JSON
python scrapernhl/cli.py game 2024020001 --format json

# Custom output with xG
python scrapernhl/cli.py game 2024020001 --with-xg --output game_with_xg.parquet --format parquet
```

### Example Output

```
Scraping play-by-play for game 2024020001...
Successfully scraped 312 events
Saved to: game_2024020001.csv
```

With xG:
```
Scraping play-by-play for game 2024020001...
Calculated xG for shot events
Successfully scraped 312 events
Saved to: game_2024020001_with_xg.csv
```

## Draft Command

Scrape NHL draft data.

### Basic Usage

```bash
python scrapernhl/cli.py draft YEAR [ROUND] [OPTIONS]
```

**Arguments:**
- `YEAR` - Draft year (e.g., 2024, 2025)
- `ROUND` - Draft round (1-7 or 'all', default: all)

### Examples

```bash
# All rounds
python scrapernhl/cli.py draft 2024

# First round only
python scrapernhl/cli.py draft 2024 1

# Specific round
python scrapernhl/cli.py draft 2024 2

# All rounds as JSON
python scrapernhl/cli.py draft 2025 all --format json

# Custom output
python scrapernhl/cli.py draft 2024 1 --output first_round_2024.csv
```

### Example Output

```
Scraping 2024 NHL draft (round 1)...
Successfully scraped 32 draft picks
Saved to: nhl_draft_2024_r1.csv
```

## Practical Use Cases

### Daily Standings Report

Create a shell script to get daily standings:

```bash
#!/bin/bash
# daily_standings.sh

DATE=$(date +%Y-%m-%d)
python scrapernhl/cli.py standings $DATE --output "standings_$DATE.csv"
echo "Standings saved for $DATE"
```

### Team Data Export

Export all data for your favorite team:

```bash
#!/bin/bash
# export_team_data.sh

TEAM="MTL"
SEASON="20252026"

python scrapernhl/cli.py schedule $TEAM $SEASON --output ${TEAM}_schedule.csv
python scrapernhl/cli.py roster $TEAM $SEASON --output ${TEAM}_roster.csv
python scrapernhl/cli.py stats $TEAM $SEASON --output ${TEAM}_skaters.csv
python scrapernhl/cli.py stats $TEAM $SEASON --goalies --output ${TEAM}_goalies.csv

echo "All $TEAM data exported!"
```

### Automated Game Scraping

Set up a cron job to scrape games after they finish:

```bash
# Cron job: Run every hour during hockey season
0 * * * * /path/to/scrape_recent_games.sh

# scrape_recent_games.sh
#!/bin/bash
for GAME_ID in 2024020100 2024020101 2024020102; do
    python scrapernhl/cli.py game $GAME_ID --with-xg --format parquet
done
```

### Multi-Format Export

Export the same data in multiple formats:

```bash
#!/bin/bash
# multi_format_export.sh

python scrapernhl/cli.py teams --output teams.csv --format csv
python scrapernhl/cli.py teams --output teams.json --format json
python scrapernhl/cli.py teams --output teams.parquet --format parquet

echo "Teams data exported in CSV, JSON, and Parquet formats"
```

## Tips and Best Practices

### Output File Names

If you don't specify `--output`, the CLI automatically generates descriptive filenames:

- `teams` → `nhl_teams.csv`
- `schedule MTL 20252026` → `mtl_schedule_20252026.csv`
- `roster TOR 20252026` → `tor_roster_20252026.csv`
- `game 2024020001` → `game_2024020001.csv`

### Format Selection

Choose the right format for your use case:

- **CSV** - Best for Excel, simple analysis, human-readable
- **JSON** - Best for web apps, APIs, JavaScript
- **Parquet** - Best for large datasets, Python/pandas, analytics (50-80% smaller than CSV)
- **Excel** - Best for sharing with non-technical users

### Performance

For faster processing of large datasets:

- Use `--polars` flag with the `teams` command
- Use `--format parquet` for better compression
- Process multiple files in parallel using shell background jobs (`&`)

### Integration with Python

You can mix CLI and Python usage:

```bash
# Scrape with CLI
python scrapernhl/cli.py schedule MTL 20252026 --output schedule.csv

# Then analyze in Python
python -c "
import pandas as pd
schedule = pd.read_csv('schedule.csv')
print(schedule[schedule['gameState'] == 'OFF'].head())
"
```

## Multi-League Commands

All leagues (PWHL, AHL, OHL, WHL, QMJHL) support the same set of commands with consistent options.

### League Command Groups

Each league has its own command group:

```bash
python scrapernhl/cli.py pwhl --help
python scrapernhl/cli.py ahl --help
python scrapernhl/cli.py ohl --help
python scrapernhl/cli.py whl --help
python scrapernhl/cli.py qmjhl --help
```

### Available Subcommands

Each league supports these subcommands:

- `teams` - Scrape all teams
- `schedule` - Scrape league schedule
- `standings` - Scrape league standings
- `roster` - Scrape team rosters
- `stats` - Scrape player statistics
- `game` - Scrape game play-by-play data

### PWHL Examples

```bash
# Get all PWHL teams
python scrapernhl/cli.py pwhl teams

# Get schedule for specific season
python scrapernhl/cli.py pwhl schedule --season 2024

# Get current standings
python scrapernhl/cli.py pwhl standings

# Get roster for all teams
python scrapernhl/cli.py pwhl roster

# Get roster for specific team
python scrapernhl/cli.py pwhl roster --team-id 1

# Get top 50 skater stats
python scrapernhl/cli.py pwhl stats

# Get goalie stats
python scrapernhl/cli.py pwhl stats --player-type goalie --limit 20

# Get game play-by-play
python scrapernhl/cli.py pwhl game 12345

# Export in different formats
python scrapernhl/cli.py pwhl teams --format json --output pwhl_teams.json
```

### AHL Examples

```bash
# Get all AHL teams
python scrapernhl/cli.py ahl teams

# Get full league schedule
python scrapernhl/cli.py ahl schedule

# Get schedule for specific team
python scrapernhl/cli.py ahl schedule --team-id 123

# Get standings
python scrapernhl/cli.py ahl standings --season 2024

# Get rosters
python scrapernhl/cli.py ahl roster --team-id 123

# Get player stats
python scrapernhl/cli.py ahl stats --player-type skater --limit 100

# Scrape game data
python scrapernhl/cli.py ahl game 54321 --format parquet
```

### OHL Examples

```bash
# Get all OHL teams
python scrapernhl/cli.py ohl teams --season 2024

# Get league schedule
python scrapernhl/cli.py ohl schedule

# Get standings
python scrapernhl/cli.py ohl standings

# Get team roster
python scrapernhl/cli.py ohl roster --team-id 5

# Get top scorers
python scrapernhl/cli.py ohl stats --limit 50

# Get goalie stats
python scrapernhl/cli.py ohl stats --player-type goalie

# Game play-by-play
python scrapernhl/cli.py ohl game 98765
```

### WHL Examples

```bash
# Get WHL teams
python scrapernhl/cli.py whl teams

# Get schedule
python scrapernhl/cli.py whl schedule --season 2024

# Get standings
python scrapernhl/cli.py whl standings --output whl_standings.csv

# Get rosters
python scrapernhl/cli.py whl roster --team-id 10

# Player stats
python scrapernhl/cli.py whl stats --player-type skater

# Game data
python scrapernhl/cli.py whl game 11111 --format json
```

### QMJHL Examples

```bash
# Get QMJHL teams
python scrapernhl/cli.py qmjhl teams

# Get full schedule
python scrapernhl/cli.py qmjhl schedule

# Get standings
python scrapernhl/cli.py qmjhl standings

# Get team roster
python scrapernhl/cli.py qmjhl roster --team-id 7

# Get player stats
python scrapernhl/cli.py qmjhl stats --limit 75

# Get game data
python scrapernhl/cli.py qmjhl game 22222
```

### Multi-League Workflow Example

Scrape data from all leagues:

```bash
#!/bin/bash
# scrape_all_leagues.sh

# NHL
python scrapernhl/cli.py teams --output data/nhl_teams.csv
python scrapernhl/cli.py standings --output data/nhl_standings.csv

# PWHL
python scrapernhl/cli.py pwhl teams --output data/pwhl_teams.csv
python scrapernhl/cli.py pwhl standings --output data/pwhl_standings.csv

# AHL
python scrapernhl/cli.py ahl teams --output data/ahl_teams.csv
python scrapernhl/cli.py ahl standings --output data/ahl_standings.csv

# OHL
python scrapernhl/cli.py ohl teams --output data/ohl_teams.csv
python scrapernhl/cli.py ohl standings --output data/ohl_standings.csv

# WHL
python scrapernhl/cli.py whl teams --output data/whl_teams.csv
python scrapernhl/cli.py whl standings --output data/whl_standings.csv

# QMJHL
python scrapernhl/cli.py qmjhl teams --output data/qmjhl_teams.csv
python scrapernhl/cli.py qmjql standings --output data/qmjhl_standings.csv

echo "All league data exported!"
```

## Common Options

All multi-league commands support these options:

- `--season` - Season ID (optional, uses current season if omitted)
- `--team-id` - Team ID (-1 for all teams, default)
- `--player-type` - Player type for stats (skater/goalie)
- `--limit` - Number of records to return (default: 50)
- `--output` - Custom output file path
- `--format` - Output format (csv/json/parquet/excel)

## See Also

- [Basic Scraping Examples](scraping.md) - Python API examples
- [Advanced Examples](advanced.md) - Data analysis
- [Data Export](export.md) - Exporting from Python
- [API Reference](../api.md) - Complete API documentation
- [Multi-League API Examples](../multi-league-api-examples.md) - Python multi-league usage
