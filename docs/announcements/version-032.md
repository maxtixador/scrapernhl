---
title: "Version 0.3.2 Released — Strength-Label Fix & Dependency Updates"
date: 2026-03-07
tags: ["announcement", "release", "bugfix"]
categories: ["announcements"]
---

# ANNOUNCEMENT: Version 0.3.2 Released
*March 7th, 2026*

Version 0.3.2 is a targeted patch release fixing a long-standing bug in the NHL analytics pipeline where the alphabetically **second** team received mirrored (incorrect) strength labels in all per-player and per-combo stat functions. If you have ever run `on_ice_stats()`, `combo_on_ice_stats()`, or `team_strength_aggregates()` and noticed that one team's `5v4` and `4v5` buckets seemed swapped, this release is for you.

Upgrade:

```bash
pip install --upgrade scrapernhl
```

---

## What Changed

### Fix: Strength State Mirroring for the Alphabetically Second Team (PR #10)

When computing per-player and per-combination on-ice statistics the scraper groups each second of play by the game strength seen by the **focus team** (e.g. `"5v4"` = power play, `"4v5"` = penalty kill). Internally, strength labels are derived from the raw shift matrix which is keyed by the home team. For the alphabetically **first** team this happened to produce the correct per-team view. For the alphabetically **second** team the labels were mirrored — the power-play bucket was labelled `"4v5"` and the penalty-kill bucket was labelled `"5v4"`.

**Affected functions (all NHL-only):**

| Function | Effect of fix |
|---|---|
| `on_ice_stats()` / `on_ice_stats_by_player_strength()` | Strength bucket rows now reflect the focus team's perspective |
| `toi_by_player_and_strength()` | TOI split by `EV / PP / PK` is now accurate for both teams |
| `combo_on_ice_stats()` | Combination TOI/shot buckets correct for both teams |
| `combo_on_ice_stats_both_teams()` | No longer requires manual column swapping when comparing teams |
| `team_strength_aggregates()` | Team-level Corsi/Fenwick/TOI split now correct for both teams |

Before this fix, comparing two teams' analytics from the same game would yield identical power-play and penalty-kill splits for both — they were always reported from the first alphabetical team's perspective.

**Example:**

```python
from scrapernhl import HockeyScraper

nhl = HockeyScraper('nhl')
pbp = nhl.scrape_game(2024021001)   # BOS (first alpha) vs MTL (second alpha)

# Before 0.3.2 — MTL's PP/PK buckets were swapped
# After  0.3.2 — each team sees the correct perspective
stats = nhl.on_ice_stats(pbp)
bos_pp = stats[stats['team'] == 'BOS'][stats['strength'] == '5v4']
mtl_pp = stats[stats['team'] == 'MTL'][stats['strength'] == '5v4']
```

---

### Fix: `urllib3` Minimum Version (2.0.0 → 2.0.7)

`urllib3` versions below 2.0.7 contain a bug that silently truncates chunked HTTP responses. For long game PBP requests this could produce incomplete DataFrames with no error or warning. The minimum is now pinned to `2.0.7`.

---

### Fix: `pandas` Updated to `>=2.2.3`

Pinned `pandas` to `>=2.2.3` to ensure compatibility with NumPy 2.x and avoid a `FutureWarning` / `TypeError` in certain DataFrame merge operations used inside the PBP pipeline.

---

### Fix: PWHL Full Name in README

Corrected the Professional Women's Hockey League full name from "Provincial" to "Professional" in the README introduction text.

---

## Using the Legacy Scraper

The `scraper_legacy.py` module remains fully functional and is still the recommended path for the full NHL analytics pipeline. All heavy functions — `scrape_game()`, `on_ice_stats()`, `combo_on_ice_stats()`, `team_strength_aggregates()`, and the full TOI/RAPM pipeline — live there and are lazy-loaded through `scrapernhl.nhl.scraper` to keep import time low.

See the [Legacy Scraper section of the API Reference](../api.md#legacy-nhl-scraper-scraper_legacypy) for the full function list and import patterns.

---

## Upgrading

```bash
pip install --upgrade scrapernhl
```

No breaking changes. No migration required. This is a drop-in replacement for 0.3.1.

---

## Resources

- **Documentation**: [maxtixador.github.io/scrapernhl](https://maxtixador.github.io/scrapernhl/)
- **API Reference**: [api.md](../api.md)
- **Changelog**: [CHANGELOG.md](https://github.com/maxtixador/scrapernhl/blob/master/CHANGELOG.md)
- **GitHub**: [maxtixador/scrapernhl](https://github.com/maxtixador/scrapernhl)

---

Happy scraping!

---

**Full Changelog**: [v0.3.1...v0.3.2](https://github.com/maxtixador/scrapernhl/compare/v0.3.1...v0.3.2)
