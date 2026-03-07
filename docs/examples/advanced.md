# Advanced Analytics Examples

Advanced usage patterns for the NHL analytics pipeline using `HockeyScraper`.

All analytics methods require `HockeyScraper('nhl')` — they are NHL-only.

---

## Full Game Pipeline

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')
game_id = 2024020001

# Full game data — HTML PBP + shifts + JSON API merged, with on-ice player lists
pbp    = nhl.scrape_game(game_id)
shifts = nhl.shifts(game_id)

print(f"Game has {len(pbp)} events")
print(pbp.columns.tolist())
```

---

## Per-Player On-Ice Stats (Corsi, Fenwick, TOI)

```python
nhl = HockeyScraper('nhl')

pbp = nhl.scrape_game(2024020001)

# Per-player, per-strength on-ice stats
player_stats = nhl.on_ice_stats(pbp, rates=True)

# Best CF% among players with at least 5 min of 5v5 TOI
cf_leaders = (player_stats
    .query("strength == '5v5' and TOI >= 5")
    .nlargest(10, 'CF%'))
print(cf_leaders[['player', 'team', 'TOI', 'CF', 'CA', 'CF%']])
```

---

## Team Strength-State Aggregates

```python
nhl = HockeyScraper('nhl')

pbp = nhl.scrape_game(2024020001)

team_stats = nhl.team_strength_aggregates(pbp, rates=True)

# 5v5 only
stats_5v5 = team_stats.query("strength == '5v5'")
print(stats_5v5[['team', 'minutes', 'CF', 'CA', 'GF', 'GA']])
```

---

## Player Combination Stats

### Individual player stats (1-player combos)

```python
nhl = HockeyScraper('nhl')

pbp = nhl.scrape_game(2024020001)

# Stats for every player on a focus team
combos_1 = nhl.combo_on_ice_stats(pbp, focus_team='MTL', n_team=1, rates=True)
combos_1[['player1Id', 'player1Name', 'team', 'strength', 'seconds', 'minutes']].head(10)
```

### Defensive pairs (2-player combinations)

```python
combos_2 = nhl.combo_on_ice_stats(pbp, focus_team='MTL', n_team=2, min_toi=60, rates=True)

top_d_pairs = (combos_2
    .query("team_combo_pos == '2D' and strength == '5v5'")
    .nlargest(10, 'seconds'))
print(top_d_pairs[['team_combo', 'team', 'strength', 'seconds', 'minutes']])
```

### Forward lines (3-player combinations)

```python
combos_3 = nhl.combo_on_ice_stats(pbp, focus_team='MTL', n_team=3, min_toi=60, rates=True)

top_lines = (combos_3
    .query("team_combo_pos == '3F' and strength == '5v5'")
    .nlargest(10, 'seconds'))
print(top_lines[['team_combo', 'team', 'strength', 'seconds', 'minutes']])
```

---

## Time-on-Ice Matrix Analysis

```python
nhl = HockeyScraper('nhl')

pbp    = nhl.scrape_game(2024020001)
shifts = nhl.shifts(2024020001)

# Build player-by-second boolean on-ice matrix
matrix = nhl.seconds_matrix(pbp, shifts)

# Per-second strength-state table (home/away skater counts)
strengths = nhl.strengths_by_second(matrix)

# Per-player, per-strength TOI (in minutes)
toi = nhl.toi_by_strength_all(matrix, strengths)
print(toi.head(10))

# Pairwise teammate shared TOI
pairs = nhl.shared_toi_teammates(matrix, strengths)
print(pairs.head(10))

# Cross-team opponent shared TOI
opponents = nhl.shared_toi_opponents(matrix, strengths)
print(opponents.head(10))
```

---

## Multi-Game Season Analysis

```python
import pandas as pd
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')

# Get completed games from a team's schedule
schedule = nhl.schedule(team='MTL', season=20252026)
completed = schedule[schedule['gameState'] == 'OFF']
game_ids  = completed.head(5)['id'].tolist()

# Scrape and aggregate
all_team_stats = []
for gid in game_ids:
    try:
        pbp   = nhl.scrape_game(gid)
        stats = nhl.team_strength_aggregates(pbp)
        stats['game_id'] = gid
        all_team_stats.append(stats)
    except Exception as e:
        print(f"Skipping game {gid}: {e}")

season_stats = pd.concat(all_team_stats, ignore_index=True)

# Aggregate by team
summary = (season_stats
    .groupby('team')
    .agg(minutes=('minutes', 'sum'), CF=('CF', 'sum'), CA=('CA', 'sum'),
         GF=('GF', 'sum'), GA=('GA', 'sum'))
    .reset_index()
    .assign(**{'CF%': lambda df: 100 * df['CF'] / (df['CF'] + df['CA'])}))

print(summary.sort_values('CF%', ascending=False))
```

---

## On-Ice Format Helpers

```python
nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2024020001)

# Convert list-based on-ice columns to tidy long format
long_df = nhl.build_on_ice_long(pbp)

# Expand on-ice lists into named wide columns (skater_1..6, goalie)
wide_df = nhl.build_on_ice_wide(pbp, max_skaters=6, include_goalie=True)

# Convert shifts to ON/OFF event rows
shifts     = nhl.shifts(2024020001)
shift_evts = nhl.build_shifts_events(shifts)
```

---

## Goal Replay Tracking Data

```python
from scrapernhl import HockeyScraper, tracking_dict_to_df

nhl = HockeyScraper('nhl')

# Get raw play data with replay URLs attached
pbp_raw = nhl.scrape_plays(2024020001, add_goal_replay=True)

# Pick the first goal that has a replay URL
goals = pbp_raw[pbp_raw.get('pptReplayUrl', pd.Series()).notna()]
if not goals.empty:
    replay_url = goals.iloc[0]['pptReplayUrl']
    replay     = nhl.goal_replay(replay_url)
    tracking   = tracking_dict_to_df(replay)
    print(tracking.head())
```

---

## See Also

- [API Reference](../api.md) - Complete method documentation
- [Getting Started](../getting-started.md) - Basic usage examples
- [Scraping Examples](scraping.md) - Data collection examples
