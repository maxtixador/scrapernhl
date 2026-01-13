# ScraperNHL CLI - Quick Reference

## Installation & Setup
```bash
pip install scrapernhl
# Or from source
git clone https://github.com/maxtixador/scrapernhl.git
cd scrapernhl
pip install -e .
```

## Quick Start

### NHL (Original)
```bash
scrapernhl teams                              # Get all teams
scrapernhl schedule MTL 20252026              # Team schedule
scrapernhl standings 2026-01-12               # Current standings
scrapernhl roster MTL 20252026                # Team roster
scrapernhl stats MTL 20252026                 # Team stats
scrapernhl game 2024020001                    # Game play-by-play
scrapernhl draft 2024                         # Draft data
```

### Multi-League (New in v0.1.5)
```bash
# PWHL
scrapernhl pwhl teams
scrapernhl pwhl schedule
scrapernhl pwhl standings
scrapernhl pwhl stats --player-type skater --limit 50
scrapernhl pwhl stats --player-type goalie --limit 20
scrapernhl pwhl game 12345

# AHL
scrapernhl ahl teams
scrapernhl ahl schedule --team-id 5
scrapernhl ahl standings
scrapernhl ahl stats --player-type skater

# OHL
scrapernhl ohl teams
scrapernhl ohl schedule --team-id 2
scrapernhl ohl standings
scrapernhl ohl game 28155

# WHL
scrapernhl whl teams
scrapernhl whl schedule
scrapernhl whl standings
scrapernhl whl stats --player-type skater

# QMJHL
scrapernhl qmjhl teams
scrapernhl qmjql schedule --team-id 3
scrapernhl qmjhl standings
scrapernhl qmjhl stats --player-type goalie
```

## Output Formats

### CSV (default)
```bash
scrapernhl pwhl teams --output teams.csv
# or
scrapernhl pwhl teams --output teams.csv --format csv
```

### JSON
```bash
scrapernhl ahl standings --output standings.json --format json
```

### Parquet
```bash
scrapernhl ohl teams --output teams.parquet --format parquet
```

### Excel
```bash
scrapernhl whl stats --output stats.xlsx --format excel
# Note: Requires openpyxl (pip install openpyxl)
```

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--output`, `-o` | Output file path | `--output data.csv` |
| `--format`, `-f` | Output format | `--format json` |
| `--season` | Season ID | `--season 2024` |
| `--team-id` | Team ID (-1 for all) | `--team-id 5` |
| `--player-type` | skater or goalie | `--player-type goalie` |
| `--limit` | Number of records | `--limit 100` |
| `--help` | Show help | `scrapernhl pwhl --help` |

## Examples by Use Case

### Get all teams from all leagues
```bash
scrapernhl teams --output nhl_teams.csv
scrapernhl pwhl teams --output pwhl_teams.csv
scrapernhl ahl teams --output ahl_teams.csv
scrapernhl ohl teams --output ohl_teams.csv
scrapernhl whl teams --output whl_teams.csv
scrapernhl qmjhl teams --output qmjhl_teams.csv
```

### Get current standings
```bash
scrapernhl standings --output nhl_standings.csv
scrapernhl pwhl standings --output pwhl_standings.csv
scrapernhl ahl standings --output ahl_standings.csv
scrapernhl ohl standings --output ohl_standings.csv
scrapernhl whl standings --output whl_standings.csv
scrapernhl qmjhl standings --output qmjhl_standings.csv
```

### Get player stats
```bash
# Top 50 skaters
scrapernhl pwhl stats --player-type skater --limit 50 --output skaters.csv

# All goalies
scrapernhl ahl stats --player-type goalie --output goalies.csv

# Specific season
scrapernhl ohl stats --season 83 --player-type skater --output ohl_stats.csv
```

### Export in different formats
```bash
# Same data, multiple formats
scrapernhl pwhl teams --output teams.csv --format csv
scrapernhl pwhl teams --output teams.json --format json
scrapernhl pwhl teams --output teams.parquet --format parquet
```

## Help Commands

```bash
# Main help
scrapernhl --help

# League-specific help
scrapernhl pwhl --help
scrapernhl ahl --help
scrapernhl ohl --help
scrapernhl whl --help
scrapernhl qmjhl --help

# Command-specific help
scrapernhl pwhl stats --help
scrapernhl ahl schedule --help
```

## Tips

1. **Use absolute paths** for output files
2. **Check available teams** before filtering by team-id
3. **Start with small limits** when testing stats commands
4. **Use JSON format** for nested data structures
5. **Use Parquet format** for large datasets
6. **Check season IDs** - they differ by league

## Troubleshooting

### Command not found
```bash
# Ensure scrapernhl is installed
pip install scrapernhl
# Or use python -m
python -m scrapernhl.cli --help
```

### Module not found errors
```bash
# Reinstall package
pip install --upgrade scrapernhl
```

### Excel format not working
```bash
# Install openpyxl
pip install openpyxl
```

### Empty results
- Check season ID (may need to specify)
- Verify team-id exists for that league
- Some data may not be available for all teams/seasons

## Python API Alternative

If you prefer Python code over CLI:
```python
# Instead of: scrapernhl pwhl teams
from scrapernhl.pwhl.scrapers import scrapeTeams
teams = scrapeTeams()

# Instead of: scrapernhl ahl stats
from scrapernhl.ahl.scrapers import scrapePlayerStats
stats = scrapePlayerStats(player_type='skater', limit=50)
```

## More Information

- Documentation: https://maxtixador.github.io/scrapernhl/
- API Reference: https://maxtixador.github.io/scrapernhl/api/
- GitHub: https://github.com/maxtixador/scrapernhl
- Issues: https://github.com/maxtixador/scrapernhl/issues
