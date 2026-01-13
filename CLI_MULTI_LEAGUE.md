# CLI Multi-League Support - Implementation Summary

## Overview
Successfully added CLI support for all 6 hockey leagues:
- **NHL** (National Hockey League) - existing
- **PWHL** (Professional Women's Hockey League) - NEW
- **AHL** (American Hockey League) - NEW
- **OHL** (Ontario Hockey League) - NEW
- **WHL** (Western Hockey League) - NEW
- **QMJHL** (Quebec Maritimes Junior Hockey League) - NEW

## CLI Structure

### Main Commands (NHL)
```bash
scrapernhl teams          # NHL teams
scrapernhl schedule       # NHL schedule
scrapernhl standings      # NHL standings
scrapernhl roster         # NHL roster
scrapernhl stats          # NHL stats
scrapernhl game           # NHL game data
scrapernhl draft          # NHL draft data
```

### League Subcommands (Multi-League)
```bash
scrapernhl pwhl teams     # PWHL teams
scrapernhl ahl teams      # AHL teams
scrapernhl ohl teams      # OHL teams
scrapernhl whl teams      # WHL teams
scrapernhl qmjhl teams    # QMJHL teams
```

Each league supports these subcommands:
- `teams` - Scrape all teams
- `schedule` - Scrape game schedule
- `standings` - Scrape league standings
- `stats` - Scrape player statistics
- `roster` - Scrape team rosters
- `game` - Scrape play-by-play data

## Usage Examples

### PWHL Examples
```bash
# Get all PWHL teams
scrapernhl pwhl teams --output pwhl_teams.csv

# Get PWHL schedule
scrapernhl pwhl schedule --output pwhl_schedule.csv

# Get PWHL standings
scrapernhl pwhl standings --output pwhl_standings.json --format json

# Get PWHL skater stats (top 50)
scrapernhl pwhl stats --player-type skater --limit 50 --output pwhl_skaters.csv

# Get PWHL goalie stats
scrapernhl pwhl stats --player-type goalie --limit 20 --output pwhl_goalies.csv

# Get PWHL play-by-play for a game
scrapernhl pwhl game 12345 --output pwhl_game.csv
```

### AHL Examples
```bash
# Get all AHL teams
scrapernhl ahl teams --output ahl_teams.csv

# Get AHL schedule for specific team
scrapernhl ahl schedule --team-id 5 --output ahl_schedule.csv

# Get AHL standings
scrapernhl ahl standings --output ahl_standings.csv

# Get AHL player stats
scrapernhl ahl stats --player-type skater --limit 100 --output ahl_stats.csv
```

### OHL Examples
```bash
# Get all OHL teams
scrapernhl ohl teams --output ohl_teams.csv

# Get OHL schedule
scrapernhl ohl schedule --team-id 2 --output ohl_schedule.csv

# Get OHL standings
scrapernhl ohl standings --output ohl_standings.csv

# Get OHL game data
scrapernhl ohl game 28155 --output ohl_game.csv
```

### WHL Examples
```bash
# Get WHL teams
scrapernhl whl teams --output whl_teams.csv

# Get WHL standings (JSON format)
scrapernhl whl standings --output whl_standings.json --format json

# Get WHL player stats
scrapernhl whl stats --player-type skater --limit 50 --output whl_stats.csv
```

### QMJHL Examples
```bash
# Get QMJHL teams
scrapernhl qmjhl teams --output qmjhl_teams.csv

# Get QMJHL schedule for specific team
scrapernhl qmjhl schedule --team-id 3 --output qmjhl_schedule.csv

# Get QMJHL player stats
scrapernhl qmjhl stats --player-type skater --limit 25 --output qmjhl_stats.csv
```

## Common Options

### Output Formats
All commands support multiple output formats:
- `--format csv` (default)
- `--format json`
- `--format parquet`
- `--format excel` (requires openpyxl)

### Common Parameters
- `--season <ID>` - Specify season (optional, defaults to current)
- `--team-id <ID>` - Filter by team (-1 for all teams)
- `--player-type <TYPE>` - Choose 'skater' or 'goalie'
- `--limit <N>` - Limit number of results
- `--output <PATH>` - Output file path
- `--format <FORMAT>` - Output format

## Implementation Details

### Code Structure
```python
# League command groups
@cli.group()
def pwhl():
    """PWHL commands."""
    pass

# Command factory pattern
def create_league_commands(group, league_name, module_path):
    """Create standard commands for a league."""
    # Creates: teams, schedule, standings, roster, stats, game
    ...

# Register all leagues
create_league_commands(pwhl, 'PWHL', 'pwhl')
create_league_commands(ahl, 'AHL', 'ahl')
create_league_commands(ohl, 'OHL', 'ohl')
create_league_commands(whl, 'WHL', 'whl')
create_league_commands(qmjhl, 'QMJHL', 'qmjhl')
```

### Key Features
1. **Unified Interface** - Same commands across all leagues
2. **Flexible Parameters** - Adapts to different API signatures
3. **Multiple Formats** - CSV, JSON, Parquet, Excel support
4. **Error Handling** - Clear error messages
5. **No Emojis** - Clean, professional output
6. **Lazy Imports** - Fast startup time

## Testing

### Test Script
Run `./test_cli.sh` to test all commands across all leagues.

### Manual Testing
```bash
# Test help
python -m scrapernhl.cli --help
python -m scrapernhl.cli pwhl --help

# Test each league
python -m scrapernhl.cli pwhl teams --output /tmp/test.csv
python -m scrapernhl.cli ahl teams --output /tmp/test.csv
python -m scrapernhl.cli ohl teams --output /tmp/test.csv
python -m scrapernhl.cli whl teams --output /tmp/test.csv
python -m scrapernhl.cli qmjhl teams --output /tmp/test.csv
```

## Test Results

All commands successfully tested:
- ✓ NHL commands (teams, schedule, standings, roster, stats, game, draft)
- ✓ PWHL commands (teams, schedule, standings, stats)
- ✓ AHL commands (teams, schedule, standings, stats)
- ✓ OHL commands (teams, schedule, standings, game)
- ✓ WHL commands (teams, standings, stats)
- ✓ QMJHL commands (teams, schedule, stats)
- ✓ Multiple output formats (CSV, JSON, Parquet)
- ✓ 21+ test files created successfully

## Known Limitations

1. **Excel format** requires openpyxl (optional dependency)
2. **Some parquet conversions** may fail with mixed data types (rare)
3. **Empty rosters** for some team/season combinations (API data availability)

## Version
- CLI version: 0.1.5
- Added: January 2026
- Tested on: Python 3.12, macOS

## Future Enhancements
- Add batch processing flag for multiple teams/games
- Add date range filters for schedules
- Add verbose/quiet output options
- Add progress bars for long operations
- Add caching controls
