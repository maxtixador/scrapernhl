# Advanced Examples

Advanced usage patterns for data analysis and feature engineering.

## Find a Recent Completed Game

```python
from scrapernhl.scrapers.schedule import scrapeSchedule
from datetime import datetime

# Get recent games from any team
schedule = scrapeSchedule("MTL", "20252026")
completed = schedule[schedule['gameState'] == 'OFF']

if len(completed) > 0:
    game_id = completed.iloc[0]['id']
    game_info = completed.iloc[0]
    print(f"Using game: {game_info['awayTeam.abbrev']} @ {game_info['homeTeam.abbrev']}")
    print(f"Date: {game_info['gameDate']}")
    print(f"Game ID: {game_id}")
else:
    print("No completed games found. Using a known game ID...")
    game_id = 2024020001
```

## Working with Complete Game Data

```python
from scrapernhl import scrape_game

# Get comprehensive game data
game_tuple = scrape_game(game_id=game_id, include_tuple=True)

pbp = game_tuple.data

print(f"Game: {game_tuple.awayTeam} @ {game_tuple.homeTeam}")
print(f"Total events: {len(pbp)}")

print("\nRosters:")
game_tuple.rosters
```

## Expected Goals (xG) Features

```python
from scrapernhl import engineer_xg_features, predict_xg_for_pbp

# Engineer xG features
pbp_with_features = engineer_xg_features(pbp)

# Predict xG
pbp_with_xg = predict_xg_for_pbp(pbp_with_features)

# Get shots and goals
shots = pbp_with_xg[pbp_with_xg['Event'].isin(['SHOT', 'GOAL', 'MISS'])].copy()

print(f"Total shot attempts: {len(shots)}")

print("\nShot attempts with xG:")
shots[['period', 'timeInPeriod', 'Event', 'eventTeam', 'player1Id', 'xG', 'distanceFromGoal']].head(10)

# Calculate team xG totals
home_team = game_tuple.homeTeam
away_team = game_tuple.awayTeam

home_shots = shots[shots['eventTeam'] == home_team]
away_shots = shots[shots['eventTeam'] == away_team]

home_xg = home_shots['xG'].sum()
away_xg = away_shots['xG'].sum()

home_goals = len(pbp[(pbp['Event'] == 'GOAL') & (pbp['eventTeam'] == home_team)])
away_goals = len(pbp[(pbp['Event'] == 'GOAL') & (pbp['eventTeam'] == away_team)])

print(f"\n{away_team} @ {home_team}")
print(f"Score: {away_goals} - {home_goals}")
print(f"xG: {away_xg:.2f} - {home_xg:.2f}")
print(f"xG differential: {home_xg - away_xg:.2f} (positive favors {home_team})")
```

## Time on Ice (TOI) Analysis

```python
from scrapernhl import toi_by_strength

# Calculate TOI by strength
toi_df = toi_by_strength(pbp)

print("TOI by strength:")
toi_df.head(10)

# Calculate individual player stats
from scrapernhl import combo_on_ice_stats_both_teams

combo_stats = combo_on_ice_stats_both_teams(
    pbp,
    n_team=1,
    m_opp=0,          # set 0 for "vs ANY"
    min_TOI=0,
    include_goalies=False,
    rates=True,
    player_df=game_tuple.rosters  # DataFrame with ids/teams/positions
)

combo_stats[['player1Id', 'player1Name', 'player1Position', 'player1Number', 'team', 'opp', 'strength', 'seconds', 'minutes']]
```

## Player Combinations Analysis

### Defensive Pairs (2-player combinations)

```python
# Get 2-player combinations (defensive pairs)
combo_stats_2 = combo_on_ice_stats_both_teams(
    pbp,
    n_team=2,
    m_opp=0,          # set 0 for "vs ANY"
    min_TOI=60,
    include_goalies=False,
    rates=True,
    player_df=game_tuple.rosters  # DataFrame with ids/teams/positions
)

top_10_pairs_5v5 = (combo_stats_2
                    .query("team_combo_pos == '2D'")  # Get defensive pairs
                    .query("strength == '5v5'")  # Filter for 5v5
                    .nlargest(10, 'seconds')
                    )[['team_combo', 'team_combo_ids', 'team', 'opp', 'strength', 'seconds', 'minutes']]

print("Most common defensive pairs (5v5):")
top_10_pairs_5v5
```

### Forward Lines (3-player combinations)

```python
# Get 3-player combinations (forward lines)
combo_stats_3 = combo_on_ice_stats_both_teams(
    pbp,
    n_team=3,
    m_opp=0,          # set 0 for "vs ANY"
    min_TOI=60,
    include_goalies=False,
    rates=True,
    player_df=game_tuple.rosters  # DataFrame with ids/teams/positions
)

top_10_lines_5v5 = (combo_stats_3
                    .query("team_combo_pos == '3F'")  # Get offensive lines
                    .query("strength == '5v5'")  # Filter for 5v5
                    .nlargest(10, 'seconds')
                    )[['team_combo', 'team_combo_ids', 'team', 'opp', 'strength', 'seconds', 'minutes']]

print("Most common offensive lines (5v5):")
top_10_lines_5v5
```

## On-Ice Statistics by Player

```python
from scrapernhl import scrape_game, on_ice_stats_by_player_strength

# Get game with xG
pbp, _ = scrape_game(2024020001)

# Calculate on-ice stats for each player
player_stats = on_ice_stats_by_player_strength(
    pbp,
    include_goalies=False,
    rates=True  # Convert to per-60 rates
)

# Show top players by Corsi For %
print("Best Corsi For % (min 5 min TOI):")
cf_leaders = player_stats[player_stats['TOI'] >= 5].nlargest(10, 'CF%')
print(cf_leaders[['player', 'team', 'strength', 'TOI', 'CF', 'CA', 'CF%']])

# Show players with best xG differential
print("\\nBest xG differential:")
xg_leaders = player_stats[player_stats['TOI'] >= 5]
xg_leaders['xG_diff'] = xg_leaders['xG'] - xg_leaders['xGA']
print(xg_leaders.nlargest(10, 'xG_diff')[['player', 'team', 'xG', 'xGA', 'xG_diff']])
```

## Team-Level Aggregates

```python
from scrapernhl import team_strength_aggregates

# Calculate team stats by strength
team_stats = team_strength_aggregates(
    pbp_with_xg,
    include_goalies=False,
    rates=True,
    min_TOI=1
)

print("Team statistics by strength:")
team_stats[['team', 'minutes', 'CF', 'CA', 'xG', 'xGA', 'GF', 'GA']].sort_values(by=['minutes'], ascending=False)

# 5v5 stats only
stats_5v5 = team_stats[team_stats['strength'] == '5v5'].copy()

print("\n5v5 Team Stats:")
stats_5v5[['team', 'minutes', 'CF', 'CA', 'xG', 'xGA', 'GF', 'GA']]
```

## Multi-Game Season Analysis

```python
import pandas as pd

# Scrape multiple games (just 3 for demonstration)
print("Scraping multiple games for season analysis...")

game_ids_to_scrape = completed.head(3)['id'].tolist()
all_team_stats = []

for gid in game_ids_to_scrape:
    try:
        print(f"Processing game {gid}...")
        game_tuple = scrape_game(gid, include_tuple=True)
        pbp = game_tuple.data
        pbp = engineer_xg_features(pbp)
        pbp = predict_xg_for_pbp(pbp)
        
        stats = team_strength_aggregates(pbp)
        stats['game_id'] = gid
        all_team_stats.append(stats)
    except Exception as e:
        print(f"Error with game {gid}: {e}")

# Combine all games
if all_team_stats:
    season_stats = pd.concat(all_team_stats, ignore_index=True)
    
    # Aggregate by team
    team_summary = season_stats.groupby('team').agg({
        'minutes': 'sum',
        'CF': 'sum',
        'CA': 'sum',
        'xG': 'sum',
        'xGA': 'sum',
        'GF': 'sum',
        'GA': 'sum'
    }).reset_index()
    
    team_summary['CF%'] = 100 * team_summary['CF'] / (team_summary['CF'] + team_summary['CA'])
    
    print("\\nSeason stats across sampled games:")
    team_summary
```

## Phase 4: Advanced Analytics

The Phase 4 analytics module provides comprehensive statistical analysis and visualization capabilities.

### Shot Metrics and Scoring Chances

```python
from scrapernhl import (
    identify_scoring_chances,
    display_scoring_chances,
    engineer_xg_features
)

# Get game data
game_tuple = scrape_game(game_id, include_tuple=True)
pbp = game_tuple.data

# Calculate shot metrics (distance and angle are calculated by engineer_xg_features)
pbp = engineer_xg_features(pbp)

# Identify high-danger, medium-danger, and low-danger chances
pbp = identify_scoring_chances(pbp)

# Display scoring chances summary
display_scoring_chances(pbp, game_tuple.homeTeam, game_tuple.awayTeam)
```

### Advanced Corsi and Fenwick

```python
from scrapernhl import calculate_corsi, calculate_fenwick, display_advanced_stats

# Calculate possession metrics
corsi_df = calculate_corsi(pbp)
fenwick_df = calculate_fenwick(pbp)

print("\\nCorsi metrics (all shot attempts):")
print(corsi_df)

print("\\nFenwick metrics (unblocked shot attempts):")
print(fenwick_df)

# Display formatted advanced stats
display_advanced_stats(corsi_df, fenwick_df, game_tuple.homeTeam, game_tuple.awayTeam)
```

### Player Time on Ice Analysis

```python
from scrapernhl import calculate_player_toi, calculate_zone_start_percentage

# Calculate player TOI by strength
player_toi = calculate_player_toi(pbp, game_tuple.rosters)

print("\\nTop 5 players by 5v5 TOI:")
top_5v5_toi = player_toi[player_toi['strength'] == '5v5'].nlargest(5, 'toi_seconds')
print(top_5v5_toi[['player_name', 'team', 'toi_minutes']])

# Calculate zone start percentages
zone_starts = calculate_zone_start_percentage(pbp, game_tuple.rosters)

print("\\nPlayers with most offensive zone starts:")
top_ozone = zone_starts.nlargest(5, 'ozone_start_pct')
print(top_ozone[['player_name', 'team', 'ozone_starts', 'dzone_starts', 'ozone_start_pct']])
```

### Score Effects Analysis

```python
from scrapernhl import calculate_score_effects, display_score_effects

# Analyze how score differential affects play
score_effects = calculate_score_effects(pbp)

print("\\nScore Effects (how teams perform when leading/trailing/tied):")
print(score_effects)

# Display formatted score effects
display_score_effects(score_effects)
```

### Shooting Patterns Analysis

```python
from scrapernhl import analyze_shooting_patterns, display_shooting_patterns

# Analyze shooting patterns by location and type
shooting_patterns = analyze_shooting_patterns(pbp)

print("\\nShooting patterns by team:")
print(shooting_patterns)

# Display formatted shooting patterns
display_shooting_patterns(shooting_patterns)
```

### Comprehensive Analytics Report

```python
from scrapernhl import create_analytics_report, display_game_summary

# Generate complete analytics report
report = create_analytics_report(pbp, game_tuple.rosters)

print("\\nGame Summary:")
print(f"Home: {report['home_team']}, Away: {report['away_team']}")
print(f"Score: {report['home_goals']}-{report['away_goals']}")

# Display beautifully formatted game summary
display_game_summary(
    report, 
    game_tuple.homeTeam, 
    game_tuple.awayTeam,
    show_players=True,
    show_scoring_chances=True
)

# Access individual report sections
print("\\nTeam Stats:")
print(report['team_stats'])

print("\\nTop Players:")
print(report['top_players'])

print("\\nScoring Chances:")
print(report['scoring_chances'])
```

### Team and Player Summary Stats

```python
from scrapernhl import (
    calculate_team_stats_summary,
    calculate_player_stats_summary,
    display_team_stats,
    display_player_summary,
    display_top_players
)

# Calculate team summary statistics
team_stats = calculate_team_stats_summary(pbp, game_tuple.rosters)

print("\\nTeam Statistics Summary:")
print(team_stats)

# Display formatted team stats
display_team_stats(team_stats, game_tuple.homeTeam, game_tuple.awayTeam)

# Calculate player summary statistics
player_stats = calculate_player_stats_summary(pbp, game_tuple.rosters)

print("\\nTop 5 players by goals:")
top_scorers = player_stats.nlargest(5, 'goals')
print(top_scorers[['player_name', 'team', 'goals', 'assists', 'points', 'shots']])

# Display formatted player summaries
for _, player in top_scorers.iterrows():
    display_player_summary(player)

# Display top players table
display_top_players(player_stats, metric='points', n=10)
```

### Complete Analytics Workflow

```python
from scrapernhl import print_analytics_summary

# Complete workflow: scrape, analyze, and display
game_id = 2024020001

# 1. Scrape game data
game_tuple = scrape_game(game_id, include_tuple=True)
pbp = game_tuple.data

# 2. Engineer features (includes shot distance and angle)
pbp = engineer_xg_features(pbp)
pbp = predict_xg_for_pbp(pbp)
pbp = identify_scoring_chances(pbp)

# 3. Calculate all metrics
home_corsi = calculate_corsi(pbp, game_tuple.homeTeam)
home_fenwick = calculate_fenwick(pbp, game_tuple.homeTeam)
player_toi = calculate_player_toi(pbp, game_tuple.rosters)
zone_starts = calculate_zone_start_percentage(pbp, game_tuple.rosters)
score_effects = calculate_score_effects(pbp, game_tuple.homeTeam)
shooting_patterns = analyze_shooting_patterns(pbp)

# 4. Generate comprehensive report for home team
report = create_analytics_report(
    pbp,
    shifts_df=None,
    team=game_tuple.homeTeam
)

# 5. Display everything beautifully
print_analytics_summary(report)
```

## See Also

- [API Reference](../api.md) - Complete function documentation
- [Getting Started](../getting-started.md) - Basic usage examples
- [Scraping Examples](scraping.md) - Data collection examples
