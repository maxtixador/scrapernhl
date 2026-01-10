# NHL Scraper API Example Notebooks

This directory contains Jupyter notebooks demonstrating how to use the various hockey league APIs.

## Available Notebooks

### Individual League Notebooks

Each notebook provides comprehensive examples with **game scrapers** and **schedule access**:

- **[ohl_api_examples.ipynb](ohl_api_examples.ipynb)** - Ontario Hockey League (OHL)
  - 15 sections covering all API features
  - Full play-by-play game scraping
  - Season and team schedules
  - Advanced analytics

- **[whl_api_examples.ipynb](whl_api_examples.ipynb)** - Western Hockey League (WHL)
  - Complete WHL API coverage
  - Game scraping and summaries
  - Division/conference analysis
  - Schedule management

- **[qmjhl_api_examples.ipynb](qmjhl_api_examples.ipynb)** - Quebec Major Junior Hockey League (QMJHL)
  - Full QMJHL examples
  - French-Canadian teams
  - Game and schedule data
  - Statistical analysis

- **[ahl_api_examples.ipynb](ahl_api_examples.ipynb)** - American Hockey League (AHL)
  - Professional development league
  - Game scraping capabilities
  - Team and player analysis
  - Schedule access

- **[pwhl_api_examples.ipynb](pwhl_api_examples.ipynb)** - Professional Women's Hockey League (PWHL)
  - Women's professional league
  - Complete game data
  - Schedule management
  - Player statistics

### Multi-League Notebook

- **[multi_league_api_examples.ipynb](multi_league_api_examples.ipynb)** - Cross-league examples
  - Compare stats across all 5 leagues
  - Side-by-side API demonstrations
  - Advanced pagination and filtering

## What's Covered in Each Notebook

### Core Features (All Notebooks)

1. **Season Information** - Current season ID and configuration
2. **Teams** - All teams with details
3. **Player Stats** - Top skaters and goalies
4. **Recent Games** - Scorebar (past/upcoming games)
5. **📅 Full Season Schedule** - Complete game schedule
6. **📅 Team Schedule** - Team-specific schedule
7. **🎮 Game Scraper** - Play-by-play data extraction
8. **🎮 Game Summary** - Detailed game information
9. **Team Stats** - Team-specific player stats
10. **Standings** - Division/conference rankings
11. **Rookies** - Rookie leaders
12. **Special Teams** - Power play analysis
13. **Pagination** - Large dataset handling
14. **Advanced Analytics** - Custom analysis examples

## New Features ✨

### 1. Game Scraper 🎮

All notebooks now include play-by-play game scraping:

```python
from scrapernhl.ohl.scrapers import games as ohl_games

# Scrape a completed game
pbp_df = ohl_games.scrape_game(game_id, nhlify=True)
display(pbp_df.head(20))
```

### 2. Schedule Access 📅

Get full season or team-specific schedules:

```python
# Full season schedule
schedule = ohl.get_schedule(team_id=-1, season=83, month=-1)

# Team-specific schedule
team_schedule = ohl.get_schedule(team_id=16, season=83)
```

### 3. Display() Usage

All notebooks now use `display()` for DataFrames instead of `print()`:

```python
df = pd.json_normalize(data)
display(df.head(10))  # ✓ Better formatting in Jupyter
```

## Getting Started

### Prerequisites

```bash
# Install the package with all dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Running the Notebooks

```bash
# Start Jupyter Notebook
jupyter notebook

# Or use JupyterLab
jupyter lab
```

Then navigate to the `notebooks/` directory and open any example notebook.

## API Usage Pattern

All leagues follow the same consistent pattern:

```python
from scrapernhl.ohl import api as ohl
from scrapernhl.ohl.scrapers import games as ohl_games

# Get data
teams = ohl.get_teams(season=83)
skaters = ohl.get_skater_stats(season=83, limit=20)
goalies = ohl.get_goalie_stats(season=83, limit=15)
scorebar = ohl.get_scorebar(days_back=7, days_ahead=7)
schedule = ohl.get_schedule(team_id=-1, season=83)

# Scrape game
pbp_df = ohl_games.scrape_game(game_id, nhlify=True)

# Display results
df = pd.json_normalize(data)
display(df)
```

Replace `ohl` with `whl`, `qmjhl`, `ahl`, or `pwhl` for other leagues!

## Data Structure

All API endpoints return data in this format:

```python
[
  {
    "sections": [
      {
        "title": "...",
        "headers": {...},
        "data": [
          {
            "prop": {...},  # Metadata
            "row": {        # Actual data
              "name": "Player Name",
              "team_code": "TOR",
              "goals": 25,
              ...
            }
          }
        ]
      }
    ]
  }
]
```

## Recent Fixes (2026-01-10)

### ✅ Goalie Stats Fixed

The junior leagues (OHL, WHL, QMJHL) now correctly use `position='G'` filter:

```python
# ✓ Now works correctly
goalies = ohl.get_goalie_stats(season=83)
```

### ✅ Empty Results Fixed

Removed problematic parameters that caused empty API responses:
- Removed `league_id` parameter
- Removed `site_id` from player stats calls
- Only send parameters when needed

## Tips & Best Practices

1. **Always use `display()`** for DataFrames in notebooks
2. **Get season ID first** using `get_bootstrap()`
3. **Rate limiting**: 2 requests/second (built-in)
4. **Pagination**: Use `first` and `limit` for large datasets
5. **Game scraping**: Use `nhlify=True` for NHL-style format
6. **Schedules**: Use `team_id=-1` for all teams

## Support

- Issues: Report on GitHub
- Documentation: See `scrapernhl/` module files
- Platform: HockeyTech (OHL, WHL, QMJHL, AHL, PWHL)

## License

See the main repository LICENSE file.
