# Command-Line Interface (CLI) Examples

The ScraperNHL CLI lets you scrape multi-league hockey data directly from the terminal without writing Python. Useful for quick exports, shell scripts, and cron jobs.

## Supported Leagues

ScraperNHL supports 6 leagues: NHL, PWHL, AHL, OHL, WHL, QMJHL.

NHL commands are **top-level** (e.g. `python -m scrapernhl standings`).
Non-NHL leagues use **subcommands** (e.g. `python -m scrapernhl ahl standings`).

---

## Getting Help

```bash
python -m scrapernhl --help
python -m scrapernhl ahl --help
python -m scrapernhl pwhl --help
```

---

## Output Formats

All commands support `--format` / `-f`:

- `csv` (default) — comma-separated
- `json` — JSON records
- `parquet` — compressed Parquet (best for large datasets)
- `excel` — Excel spreadsheet (.xlsx)

Use `--output` / `-o` to set a custom file path.

---

## NHL Commands

NHL commands run at the top level (no league subcommand):

### Teams

```bash
# Default: saves to nhl_teams.csv
python -m scrapernhl teams

# Custom output
python -m scrapernhl teams --output my_teams.csv
python -m scrapernhl teams --format json --output teams.json
python -m scrapernhl teams --format parquet --output teams.parquet
```

### Schedule

```bash
# Montreal Canadiens 2025-26 schedule
python -m scrapernhl schedule MTL 20252026

# Custom output
python -m scrapernhl schedule TOR 20252026 --output tor_schedule.csv
python -m scrapernhl schedule BOS 20252026 --format json
```

### Standings

```bash
# Current standings (uses today's date)
python -m scrapernhl standings

# Standings for a specific date (YYYY-MM-DD)
python -m scrapernhl standings 2025-12-25

# Save to file
python -m scrapernhl standings --format json --output standings.json
```

### Roster

```bash
python -m scrapernhl roster MTL 20252026
python -m scrapernhl roster EDM 20252026 --format json
python -m scrapernhl roster TOR 20252026 --output leafs_roster.csv
```

### Stats

```bash
# Skater stats (default)
python -m scrapernhl stats MTL 20252026

# Goalie stats
python -m scrapernhl stats MTL 20252026 --goalies

# Playoff stats
python -m scrapernhl stats TOR 20252026 --session 3

# Export to JSON
python -m scrapernhl stats NYR 20252026 --format json
```

### Game (Play-by-Play)

```bash
python -m scrapernhl game 2024020001
python -m scrapernhl game 2024020001 --format json
python -m scrapernhl game 2024020001 --output pbp.parquet --format parquet
```

### Draft

```bash
# All rounds
python -m scrapernhl draft 2024

# First round only
python -m scrapernhl draft 2024 1

# All rounds as JSON
python -m scrapernhl draft 2025 all --format json
```

---

## Non-NHL League Commands

PWHL, AHL, OHL, WHL, and QMJHL all use the same subcommand structure:

```
python -m scrapernhl <league> <command> [options]
```

### Common Options

| Option | Description |
|--------|-------------|
| `--season` | Season ID (e.g. `90` for AHL 2024-25) |
| `--team-id` | Numeric team ID |
| `--player-type` | `skater` or `goalie` |
| `--limit` | Max records to return (default: 50) |
| `--output` / `-o` | Output file path |
| `--format` / `-f` | Output format (csv/json/parquet/excel) |

### AHL Examples

```bash
python -m scrapernhl ahl teams
python -m scrapernhl ahl schedule
python -m scrapernhl ahl schedule --team-id 123
python -m scrapernhl ahl standings --season 90
python -m scrapernhl ahl roster --team-id 123
python -m scrapernhl ahl stats --player-type skater --limit 100
python -m scrapernhl ahl stats --player-type goalie
python -m scrapernhl ahl game 1027781
python -m scrapernhl ahl game 1027781 --format parquet
```

### PWHL Examples

```bash
python -m scrapernhl pwhl teams
python -m scrapernhl pwhl standings
python -m scrapernhl pwhl schedule
python -m scrapernhl pwhl roster --team-id 1
python -m scrapernhl pwhl stats
python -m scrapernhl pwhl stats --player-type goalie --limit 20
python -m scrapernhl pwhl game 12345
```

### OHL Examples

```bash
python -m scrapernhl ohl teams
python -m scrapernhl ohl standings
python -m scrapernhl ohl schedule
python -m scrapernhl ohl roster --team-id 5
python -m scrapernhl ohl stats --limit 50
python -m scrapernhl ohl stats --player-type goalie
python -m scrapernhl ohl game 98765
```

### WHL Examples

```bash
python -m scrapernhl whl teams
python -m scrapernhl whl standings --output whl_standings.csv
python -m scrapernhl whl schedule
python -m scrapernhl whl roster --team-id 10
python -m scrapernhl whl stats --player-type skater
python -m scrapernhl whl game 11111 --format json
```

### QMJHL Examples

```bash
python -m scrapernhl qmjhl teams
python -m scrapernhl qmjhl standings
python -m scrapernhl qmjhl schedule
python -m scrapernhl qmjhl roster --team-id 7
python -m scrapernhl qmjhl stats --limit 75
python -m scrapernhl qmjhl game 22222
```

---

## Practical Examples

### Daily Standings Report

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
python -m scrapernhl standings $DATE --output "standings_$DATE.csv"
echo "Standings saved for $DATE"
```

### Team Data Export

```bash
#!/bin/bash
TEAM="MTL"
SEASON="20252026"

python -m scrapernhl schedule $TEAM $SEASON --output ${TEAM}_schedule.csv
python -m scrapernhl roster  $TEAM $SEASON --output ${TEAM}_roster.csv
python -m scrapernhl stats   $TEAM $SEASON --output ${TEAM}_skaters.csv
python -m scrapernhl stats   $TEAM $SEASON --goalies --output ${TEAM}_goalies.csv
```

### All Leagues Export

```bash
#!/bin/bash
# NHL
python -m scrapernhl teams     --output data/nhl_teams.csv
python -m scrapernhl standings --output data/nhl_standings.csv

# PWHL
python -m scrapernhl pwhl teams     --output data/pwhl_teams.csv
python -m scrapernhl pwhl standings --output data/pwhl_standings.csv

# AHL
python -m scrapernhl ahl teams     --output data/ahl_teams.csv
python -m scrapernhl ahl standings --output data/ahl_standings.csv

# OHL
python -m scrapernhl ohl teams     --output data/ohl_teams.csv
python -m scrapernhl ohl standings --output data/ohl_standings.csv

# WHL
python -m scrapernhl whl teams     --output data/whl_teams.csv
python -m scrapernhl whl standings --output data/whl_standings.csv

# QMJHL
python -m scrapernhl qmjhl teams     --output data/qmjhl_teams.csv
python -m scrapernhl qmjhl standings --output data/qmjhl_standings.csv
```

---

## Format Tips

| Format | Best for |
|--------|----------|
| CSV | Excel, human-readable, simple analysis |
| JSON | Web apps, APIs |
| Parquet | Large datasets, Python/pandas (50–80% smaller than CSV) |
| Excel | Sharing with non-technical users |

---

## See Also

- [Basic Scraping Examples](scraping.md) - Python API examples
- [Advanced Examples](advanced.md) - Data analysis
- [Data Export](export.md) - Exporting from Python
- [API Reference](../api.md) - Complete API documentation
