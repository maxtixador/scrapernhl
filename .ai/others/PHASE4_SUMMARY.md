## Phase 4 Implementation: Analytics + Visualization

**Status**: ✅ Complete  
**Date**: January 2026  
**Version**: 0.1.4

## Overview

Phase 4 adds comprehensive analytics functions and rich visualization utilities to the ScraperNHL package. This phase completes the transformation from a simple scraping tool to a full-featured NHL data analysis platform.

## New Features

### 1. Advanced Analytics Module (`scrapernhl/analytics.py`)

Professional-grade analytics functions for NHL data analysis.

#### Shot Quality Metrics

**`calculate_shot_distance(x, y, goal_x)`**
- Calculate Euclidean distance from goal
- Default goal position: x=89.0 (right side)

**`calculate_shot_angle(x, y, goal_x)`**
- Calculate shot angle in degrees
- Range: -90° to 90°

**`identify_scoring_chances(df, distance_col, angle_col)`**
- Classify shots as high/medium/low danger
- **High Danger**: < 25ft and < 45° angle
- **Medium Danger**: < 50ft or < 45° angle
- **Low Danger**: Far distance or poor angle

```python
from scrapernhl import identify_scoring_chances

shots_with_chances = identify_scoring_chances(shots_df)
high_danger = shots_with_chances[shots_with_chances['scoring_chance'] == 'high']
print(f"High danger shots: {len(high_danger)}")
```

#### Advanced Team Metrics

**`calculate_corsi(df, team)`**
- Corsi = Shots + Missed Shots + Blocked Shots
- Returns: CF, CA, C+/-, C%

**`calculate_fenwick(df, team)`**
- Fenwick = Shots + Missed Shots (excludes blocks)
- Returns: FF, FA, F+/-, F%

```python
from scrapernhl import calculate_corsi, calculate_fenwick

corsi = calculate_corsi(plays_df, "TOR")
fenwick = calculate_fenwick(plays_df, "TOR")

print(f"Corsi%: {corsi['corsi_percentage']:.1f}%")
print(f"Fenwick%: {fenwick['fenwick_percentage']:.1f}%")
```

**`calculate_team_stats_summary(df, team, include_advanced=True)`**
- Comprehensive team statistics
- Goals, shots, shooting %, hits, giveaways, takeaways
- Faceoffs, penalties
- Optional: Corsi and Fenwick

#### Player Analytics

**`calculate_player_toi(shifts_df, player_id)`**
- Total time on ice (seconds and minutes)
- Average shift length
- Number of shifts

**`calculate_zone_start_percentage(shifts_df, player_id)`**
- Offensive zone starts
- Defensive zone starts
- Neutral zone starts
- On-the-fly shifts
- OZS% (offensive zone start percentage)

**`calculate_player_stats_summary(plays_df, shifts_df, player_id)`**
- Goals, shots, hits, takeaways, giveaways
- TOI statistics
- Zone start metrics

```python
from scrapernhl import calculate_player_toi, calculate_zone_start_percentage

toi = calculate_player_toi(shifts_df, 8478402)
zone_starts = calculate_zone_start_percentage(shifts_df, 8478402)

print(f"TOI: {toi['total_toi_minutes']:.1f} min")
print(f"OZS%: {zone_starts['offensive_zone_start_pct']:.1f}%")
```

#### Situational Analysis

**`calculate_score_effects(df, team, score_diff_col)`**
- Analyze performance by score differential
- Categories: trailing (2+), down 1, tied, up 1, leading (2+)
- Corsi metrics for each situation

**`analyze_shooting_patterns(df, distance_bins)`**
- Shot distribution by distance
- Goals and shooting % by distance bin
- Default bins: 0-20, 20-40, 40-60, 60-100 feet

```python
from scrapernhl import analyze_shooting_patterns

patterns = analyze_shooting_patterns(plays_df)
# distance_range | total_shots | goals | shooting_percentage
# 0-20ft         | 45          | 12    | 26.7%
# 20-40ft        | 78          | 8     | 10.3%
# ...
```

#### Comprehensive Reports

**`create_analytics_report(plays_df, shifts_df, team)`**
- All-in-one analytics report
- Team statistics
- Advanced metrics (Corsi/Fenwick)
- Score effects analysis
- Shooting patterns
- Returns: Dict or DataFrame

```python
from scrapernhl import create_analytics_report

report = create_analytics_report(plays_df, shifts_df, "TOR")
print(report['team_stats']['goals'])
print(report['team_stats']['corsi'])
```

### 2. Visualization Module (`scrapernhl/visualization.py`)

Rich-formatted console visualizations for analytics output.

#### Table Displays

**`display_team_stats(stats, title)`**
- Formatted table of team statistics
- Auto-formatted values (floats, percentages)

**`display_advanced_stats(corsi, fenwick, title)`**
- Side-by-side Corsi and Fenwick display
- For/Against/Differential/Percentage columns

**`display_player_summary(stats, player_name)`**
- Offensive stats (goals, shots, hits)
- TOI metrics
- Zone start breakdown

```python
from scrapernhl import display_team_stats, display_advanced_stats

stats = calculate_team_stats_summary(plays_df, "TOR")
display_team_stats({'team': 'TOR', 'team_stats': stats})

display_advanced_stats(stats['corsi'], stats['fenwick'])
```

**`display_scoring_chances(df, team)`**
- Breakdown of high/medium/low danger chances
- Count and percentage for each category

**`display_shooting_patterns(shooting_df, title)`**
- Distance bins with shots, goals, shooting %
- Formatted table output

**`display_score_effects(score_effects, title)`**
- Performance by score differential
- CF, CA, CF% for each situation

**`display_top_players(players_df, stat, n, title)`**
- Leaderboard for any statistic
- Top N players with rank

```python
from scrapernhl import display_top_players

display_top_players(players_df, stat='goals', n=10)
# Rank | Player           | Goals
# 1    | Connor McDavid   | 32
# 2    | Auston Matthews  | 30
# ...
```

#### Game Summaries

**`display_game_summary(game_data, show_scoring, show_stats)`**
- Complete game overview
- Final score
- Team statistics comparison
- Shots, faceoffs, PP, PIM, hits, blocks

#### Full Reports

**`print_analytics_summary(report)`**
- Print entire analytics report to console
- Formatted sections with tables
- Team stats, advanced metrics, score effects, shooting patterns

```python
from scrapernhl import create_analytics_report, print_analytics_summary

report = create_analytics_report(plays_df, None, "TOR")
print_analytics_summary(report)

# Output:
# ═══════════════════════════════════════════
#  Analytics Report - TOR
# ═══════════════════════════════════════════
# 
# Team Statistics
# ┌─────────────┬────────┐
# │ Metric      │ Value  │
# ├─────────────┼────────┤
# │ Goals       │ 4      │
# │ Shots       │ 32     │
# ...
```

### 3. Legacy Code Migration

Updated `scrapernhl/scraper_legacy.py` to use new infrastructure:
- ✅ New logging system (`get_logger()`)
- ✅ Progress bars (`create_progress_bar()`)
- ✅ Caching (`@cached` decorator)
- ✅ Exception handling (APIError, RateLimitError)
- ✅ Shared config (DEFAULT_HEADERS, DEFAULT_TIMEOUT)
- ✅ Console output (`console.print_success()`)

### 4. Updated Exports

All analytics and visualization functions exported from package root:

```python
from scrapernhl import (
    # Analytics
    identify_scoring_chances,
    calculate_corsi,
    calculate_fenwick,
    calculate_player_toi,
    calculate_zone_start_percentage,
    calculate_team_stats_summary,
    calculate_player_stats_summary,
    calculate_score_effects,
    analyze_shooting_patterns,
    create_analytics_report,
    
    # Visualization
    display_team_stats,
    display_advanced_stats,
    display_player_summary,
    display_scoring_chances,
    display_shooting_patterns,
    display_score_effects,
    display_game_summary,
    display_top_players,
    print_analytics_summary,
)
```

## Use Cases

### 1. Shot Quality Analysis
```python
from scrapernhl import identify_scoring_chances, display_scoring_chances
from scrapernhl.scrapers.games import scrapePlays

# Get game data
plays = scrapePlays(2023020001)

# Filter to shots
shots = plays[plays['typeDescKey'].isin(['shot-on-goal', 'goal', 'missed-shot'])]

# Classify by danger
shots_with_chances = identify_scoring_chances(shots)

# Display breakdown
display_scoring_chances(shots_with_chances, team="TOR")

# Analyze high danger shots
high_danger = shots_with_chances[shots_with_chances['scoring_chance'] == 'high']
print(f"High danger shooting %: {len(high_danger[high_danger['typeDescKey'] == 'goal']) / len(high_danger) * 100:.1f}%")
```

### 2. Team Performance Report
```python
from scrapernhl import create_analytics_report, print_analytics_summary

# Create comprehensive report
report = create_analytics_report(plays_df, shifts_df, "TOR")

# Print formatted report
print_analytics_summary(report)

# Access specific metrics
corsi_pct = report['team_stats']['corsi']['corsi_percentage']
fenwick_pct = report['team_stats']['fenwick']['fenwick_percentage']
```

### 3. Player Impact Analysis
```python
from scrapernhl import calculate_player_stats_summary, display_player_summary

# Get player stats
player_stats = calculate_player_stats_summary(plays_df, shifts_df, 8478402)

# Display formatted summary
display_player_summary(player_stats, player_name="Auston Matthews")

# Calculate per-60 rates
toi_minutes = player_stats['total_toi_minutes']
goals_per_60 = (player_stats['goals'] / toi_minutes) * 60
print(f"Goals/60: {goals_per_60:.2f}")
```

### 4. Shooting Pattern Analysis
```python
from scrapernhl import analyze_shooting_patterns, display_shooting_patterns

# Analyze by distance
patterns = analyze_shooting_patterns(plays_df)

# Display
display_shooting_patterns(patterns)

# Find optimal shooting distance
best_distance = patterns.loc[patterns['shooting_percentage'].idxmax(), 'distance_range']
print(f"Best shooting %: {best_distance}")
```

### 5. Score Effects Study
```python
from scrapernhl import calculate_score_effects, display_score_effects

# Analyze by game state
score_effects = calculate_score_effects(plays_df, "TOR")

# Display
display_score_effects(score_effects)

# Compare trailing vs leading
trailing_cf_pct = score_effects['trailing']['corsi_percentage']
leading_cf_pct = score_effects['leading']['corsi_percentage']
print(f"CF% when trailing: {trailing_cf_pct:.1f}%")
print(f"CF% when leading: {leading_cf_pct:.1f}%")
```

### 6. Player Leaderboard
```python
from scrapernhl import scrapeMultiplePlayerStats, display_top_players

# Get player stats
player_ids = [8478402, 8479318, 8480012, 8478483, 8477934]
stats_df = scrapeMultiplePlayerStats(player_ids, "20232024")

# Display top scorers
display_top_players(stats_df, stat='goals', n=5, title="Top Goal Scorers")
```

## Analytics Functions Reference

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `calculate_shot_distance` | x, y, goal_x | float | Distance to goal |
| `calculate_shot_angle` | x, y, goal_x | float | Angle to goal |
| `identify_scoring_chances` | DataFrame | DataFrame | Add scoring_chance column |
| `calculate_corsi` | DataFrame, team | Dict | Corsi metrics |
| `calculate_fenwick` | DataFrame, team | Dict | Fenwick metrics |
| `calculate_player_toi` | shifts_df, player_id | Dict | TOI statistics |
| `calculate_zone_start_percentage` | shifts_df, player_id | Dict | Zone start % |
| `calculate_team_stats_summary` | plays_df, team | Dict | Team statistics |
| `calculate_player_stats_summary` | plays_df, shifts_df, player_id | Dict | Player statistics |
| `calculate_score_effects` | plays_df, team | Dict | Stats by score |
| `analyze_shooting_patterns` | plays_df, bins | DataFrame | Shooting by distance |
| `create_analytics_report` | plays_df, shifts_df, team | Dict | Full report |

## Visualization Functions Reference

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `display_team_stats` | stats_dict, title | None | Print team stats table |
| `display_advanced_stats` | corsi, fenwick, title | None | Print Corsi/Fenwick |
| `display_player_summary` | stats_dict, name | None | Print player stats |
| `display_scoring_chances` | DataFrame, team | None | Print chance breakdown |
| `display_shooting_patterns` | shooting_df, title | None | Print shooting analysis |
| `display_score_effects` | score_effects, title | None | Print score effects |
| `display_game_summary` | game_data, flags | None | Print game overview |
| `display_top_players` | players_df, stat, n | None | Print leaderboard |
| `print_analytics_summary` | report | None | Print full report |

## Demo Script

Run the Phase 4 demo:
```bash
python examples/phase4_demo.py
```

Demonstrations:
1. Scoring chance classification
2. Advanced statistics (Corsi/Fenwick)
3. Shooting pattern analysis
4. Team statistics summary
5. Score effects analysis (optional)
6. Custom analysis workflow
7. Full analytics report (optional)

## File Structure

```
scrapernhl/
├── analytics.py           (NEW - 550 lines)
├── visualization.py       (NEW - 430 lines)
├── scraper_legacy.py      (UPDATED - infrastructure migration)
└── __init__.py            (UPDATED - new exports)

examples/
└── phase4_demo.py         (NEW - demo script)
```

## Key Concepts

### Scoring Chances
- **High Danger**: Close range (< 25ft) with good angle (< 45°)
- **Medium Danger**: Medium range (< 50ft) OR good angle
- **Low Danger**: Far range OR poor angle

### Corsi vs Fenwick
- **Corsi**: All shot attempts (shots + misses + blocks)
- **Fenwick**: Unblocked shot attempts (shots + misses, excludes blocks)
- **Usage**: Fenwick better for offensive contribution (blocks aren't controlled)

### Zone Start %
- **Offensive Zone Starts**: Shifts starting in offensive zone
- **Defensive Zone Starts**: Shifts starting in defensive zone
- **OZS%**: (Offensive / (Offensive + Defensive)) * 100
- **Usage**: Context for possession metrics

### Score Effects
- Teams trailing: More aggressive, higher shot attempts
- Teams leading: More defensive, lower shot attempts
- **Score-adjusted**: Normalize metrics by game state

## What's New in Phase 4

✅ **Analytics Module**
- 12 analytics functions
- Shot quality metrics
- Advanced team metrics (Corsi, Fenwick)
- Player performance metrics
- Situational analysis
- Comprehensive reports

✅ **Visualization Module**
- 9 display functions
- Rich-formatted tables
- Consistent styling
- Professional output
- Quick data inspection

✅ **Legacy Migration**
- Updated logging
- Progress bars integration
- Exception handling
- Caching support
- Shared configuration

✅ **Complete Package**
- End-to-end data pipeline
- Scraping → Processing → Analytics → Visualization
- Professional-grade tools
- Production-ready

## All Phases Complete! 🎉

### Phase 1: Foundation
- Exception hierarchy
- Colored logging
- Data validation

### Phase 2: UX Enhancement
- Progress bars (Rich)
- File-based caching
- Styled output

### Phase 3: Data Collection
- Player statistics
- Batch processing
- Parallel scraping

### Phase 4: Analytics
- Advanced metrics
- Visualization
- Comprehensive reports

## What's Next?

The package now has everything needed for:
- Professional NHL data scraping
- Advanced analytics
- Team/player performance analysis
- Production deployments
- Research projects

Potential future enhancements:
- Machine learning integration (expanded xG models)
- Real-time game tracking
- Database storage utilities
- REST API wrapper
- Web dashboard

---

**Implementation**: Complete ✅  
**Tests**: Manual verification via demo script  
**Documentation**: This file + inline docstrings  
**Breaking Changes**: None (fully backward compatible)
