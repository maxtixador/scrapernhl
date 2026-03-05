<!-- endpoints.md : documenting leagues API endpoints -->
# Endpoints

This file documents the various API endpoints used to retrieve data from each league's API. All endpoints are read-only public APIs (no authentication required beyond the embedded API keys shown).

Notes:

- All non-NHL endpoints require a `season` parameter, which can be obtained from the Seasons endpoint or the bootstrap data.
- All non-NHL endpoints also require a `league_id` and `site_id`, which are included in the League Configuration Reference table below.
- NHL endpoints do not require a season parameter in the URL, but the season is often required to retrieve the correct data (e.g. for schedules, rosters, stats).
- The NHL Play-by-Play endpoint is available in both JSON (web API) and HTML (nhl.com reports) formats. The other leagues also have HTML reports available but they are not currently scraped by HockeyScraper because they don't provide the complementary JSON endpoints that the NHL does. NHL has events location data in the JSON feed, while the HTML reports have richer descriptions, more event types (e.g. giveaways/takeaways), and players that are on the ice for each event.
- NHL Shifts API might be missing for some games and might no correlate perfectly with Shifts data in the HTML reports.
- AHL, OHL, WHL, PWHL, and QMJHL endpoints follow a similar pattern and structure since they are all provided by the same underlying provider (HockeyTech). However, there are some differences in endpoint parameters and response structure between the AHL/PWHL and OHL/WHL/QMJHL, which are noted in the tables below. *It was a mess to figure out which parameters were required for which endpoints and leagues.*

---

## Response Formats

### NHL (api-web.nhle.com / records.nhl.com)

All NHL JSON endpoints return **plain JSON** (`Content-Type: application/json`). No wrapper to strip.

```python
import requests, json
data = requests.get(url).json()   # ready to use
```

### HockeyTech non-NHL (AHL / PWHL / OHL / WHL / QMJHL)

All HockeyTech endpoints return **JSONP** — the JSON payload is wrapped in a JavaScript callback function call:

```text
angular.callbacks._0({"SiteKit": { ... }})
```

The callback name can vary (`angular.callbacks._0`, `angular.callbacks._1`, a custom function name, etc.).  You **must strip the wrapper** before parsing:

```python
import re, json, requests

def clean_jsonp(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^angular\.callbacks\._\d+\(', '', text)
    text = re.sub(r'^[a-zA-Z_][a-zA-Z0-9_]*\(', '', text)
    if text.startswith('('):
        text = text[1:]
    text = re.sub(r'\);?\s*$', '', text)
    return text.strip()

raw = requests.get(url).text
data = json.loads(clean_jsonp(raw))   # dict, now usable
```

The library's `scrapernhl.utils.clean_jsonp` does exactly this.

### NHL HTML Reports (nhl.com/scores/htmlreports)

These endpoints return **raw HTML** pages (not JSON).  The response body is an HTML string that must be parsed with an HTML parser (e.g. `BeautifulSoup`).  The library handles this internally; `scraper.html_pbp(game_id, raw=True)` returns the HTML string under the `data` key, and `scraper.shifts(game_id, raw=True)` returns `{'home': '<html>…', 'away': '<html>…'}`.

---

## League Configuration Reference

| League | Base URL | Client Code | API Key | League ID | Site ID | PBP Style |
| --- | --- | --- | --- | --- | --- | --- |
| NHL | `https://api-web.nhle.com` | — | — | — | — | native JSON |
| NHL Play-by-Play (HTML) | `https://www.nhl.com/scores/htmlreports` | — | — | — | — | HTML reports |
| AHL | `https://lscluster.hockeytech.com/feed/index.php` | `ahl` | `ccb91f29d6744675` | `4` | `3` | `hockeytech_a` |
| PWHL | `https://lscluster.hockeytech.com/feed/index.php` | `pwhl` | `446521baf8c38984` | `1` | `0` | `hockeytech_a` |
| OHL | `https://lscluster.hockeytech.com/feed/index.php` | `ohl` | `f1aa699db3d81487` | `1` | `1` | `hockeytech_b` |
| WHL | `https://lscluster.hockeytech.com/feed/index.php` | `whl` | `f1aa699db3d81487` | `7` | `0` | `hockeytech_b` |
| QMJHL | `https://cluster.leaguestat.com/feed/index.php` | `lhjmq` | `f322673b6bcae299` | `6` | `0` | `hockeytech_b` |

> **PBP style note:** `hockeytech_a` (AHL/PWHL) uses `feed=statviewfeed&view=gameCenterPlayByPlay`. `hockeytech_b` (OHL/WHL/QMJHL) uses `feed=gc&tab=pxpverbose`.

---

## API Keys

These are the default public API keys embedded in the library. They can be overridden per-league via environment variables.

| League | API Key | Environment Variable Override |
| --- | --- | --- |
| NHL | — (no key required) | — |
| AHL | `ccb91f29d6744675` | `SCRAPERNHL_AHL_API_KEY` |
| PWHL | `446521baf8c38984` | `SCRAPERNHL_PWHL_API_KEY` |
| OHL | `f1aa699db3d81487` | `SCRAPERNHL_OHL_API_KEY` |
| WHL | `f1aa699db3d81487` | `SCRAPERNHL_WHL_API_KEY` |
| QMJHL | `f322673b6bcae299` | `SCRAPERNHL_QMJHL_API_KEY` |

> OHL and WHL share the same default key. The keys are passed as the `key=` query parameter on every HockeyTech request.

---

## Seasons Endpoint

Get all season IDs for a league. Season IDs are required for most other non-NHL endpoints.

| League | Endpoint | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL | [https://api.nhle.com/stats/rest/en/season](https://api.nhle.com/stats/rest/en/season) | JSON | `data[*]` (list of season objects) | IDs in `YYYYYYYY` format (e.g. `20232024`) |
| AHL | [lscluster…bootstrap…ahl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=ccb91f29d6744675&client_code=ahl&league_id=4&site_id=3) | JSONP | `regularSeasons` / `playoffSeasons` (after JSONP strip) | Default season ID: `90` |
| PWHL | [lscluster…bootstrap…pwhl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=446521baf8c38984&client_code=pwhl&league_id=1&site_id=0) | JSONP | `regularSeasons` / `playoffSeasons` | Default season ID: `8` |
| OHL | [lscluster…bootstrap…ohl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=f1aa699db3d81487&client_code=ohl&league_id=1&site_id=1) | JSONP | `regularSeasons` / `playoffSeasons` | Default season ID: `83` |
| WHL | [lscluster…bootstrap…whl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=f1aa699db3d81487&client_code=whl&league_id=7&site_id=0) | JSONP | `regularSeasons` / `playoffSeasons` | Default season ID: `289` |
| QMJHL | [cluster.leaguestat…bootstrap…lhjmq](https://cluster.leaguestat.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=f322673b6bcae299&client_code=lhjmq&league_id=6&site_id=0) | JSONP | `regularSeasons` / `playoffSeasons` | Default season ID: `211`. QMJHL bootstrap **never** populates `playoffSeasons` — see gap-scan logic in the library. |

---

## Play-by-Play Endpoint

| League | Endpoint Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL | `https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play` | JSON | `plays[*]` | `game_id` format: `{season_start_year}{game_type}{game_number}` e.g. `2023020001` |
| NHL (HTML) | `https://www.nhl.com/scores/htmlreports/{YYYY}{YYYY+1}/PL{game_number}.HTM` | HTML | parse with BeautifulSoup | `game_number` = zero-padded last 6 digits of `game_id` e.g. `020001` |
| AHL | `…feed=statviewfeed&view=gameCenterPlayByPlay&game_id={game_id}…` | JSONP | top-level array (after JSONP strip) — each element has an `event` key and a `details` sub-dict | `hockeytech_a` style |
| PWHL | `…feed=statviewfeed&view=gameCenterPlayByPlay&game_id={game_id}…` | JSONP | same as AHL | `hockeytech_a` style |
| OHL | `…feed=gc&tab=pxpverbose&game_id={game_id}…` | JSONP | `GC.Pxpverbose[*]` (after JSONP strip) | `hockeytech_b` style |
| WHL | `…feed=gc&tab=pxpverbose&game_id={game_id}…` | JSONP | `GC.Pxpverbose[*]` | `hockeytech_b` style. **No shot events.** Older seasons (≲ season 283) omit `time` on penalty events. |
| QMJHL | `…feed=gc&tab=pxpverbose&game_id={game_id}…` | JSONP | `GC.Pxpverbose[*]` | `hockeytech_b` style |

---

## Schedule Endpoint

| League | Endpoint Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL | `https://api-web.nhle.com/v1/club-schedule-season/{team}/{season}` | JSON | `games[*]` | `team` = 3-letter code, `season` = `YYYYYYYY` |
| AHL | `…feed=statviewfeed&view=schedule&season={season}&team={team_id}…` | JSONP | `[0].sections[0].data[*].row` (after JSONP strip — array of section objects) | `team=-1` for all teams |
| PWHL | `…feed=statviewfeed&view=schedule&season={season}&team={team_id}…` | JSONP | `[0].sections[0].data[*].row` | `team=-1` for all teams |
| OHL | `…feed=statviewfeed&view=schedule&season={season}&team={team_id}…` | JSONP | `[0].sections[0].data[*].row` | `team=-1` for all teams |
| WHL | `…feed=statviewfeed&view=schedule&season={season}&team={team_id}…` | JSONP | `[0].sections[0].data[*].row` | `team=-1` for all teams |
| QMJHL | `…feed=statviewfeed&view=schedule&season={season}&team={team_id}…` | JSONP | `[0].sections[0].data[*].row` | `team=-1` for all teams |

Optional filters (non-NHL): `month={1-12}`, `location=home|away|homeaway`

---

## Standings Endpoint

| League | Endpoint Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL | `https://api-web.nhle.com/v1/standings/{date}` | JSON | `standings[*]` | `date` = `YYYY-MM-DD`; defaults to today |
| AHL | `…feed=statviewfeed&view=teams&season={season}…` | JSONP | `SiteKit.Standings[*]` (after JSONP strip) | |
| PWHL | `…feed=statviewfeed&view=teams&season={season}…` | JSONP | `SiteKit.Standings[*]` | |
| OHL | `…feed=statviewfeed&view=teams&season={season}…` | JSONP | `[0].sections[*].data[*].row` | |
| WHL | `…feed=statviewfeed&view=teams&season={season}…` | JSONP | `[0].sections[*].data[*].row` | |
| QMJHL | `…feed=statviewfeed&view=teams&season={season}…` | JSONP | `[0].sections[*].data[*].row` | |

Non-NHL parameters:

- `groupTeamsBy`: `division` (default) | `conference` | `league`
- `context`: `overall` (default) | `home` | `away`
- `special`: `false` (default)

---

## Roster Endpoint

| League | Endpoint Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL | `https://api-web.nhle.com/v1/roster/{team}/{season}` | JSON | `forwards[*]` + `defensemen[*]` + `goalies[*]` | `team` = 3-letter code, `season` = `YYYYYYYY` |
| AHL | `…feed=statviewfeed&view=roster&team_id={team_id}&season_id={season}…` | JSONP | `SiteKit.Roster[*]` (after JSONP strip) | |
| PWHL | `…feed=statviewfeed&view=roster&team_id={team_id}&season_id={season}…` | JSONP | `SiteKit.Roster[*]` | |
| OHL | `…feed=statviewfeed&view=roster&team_id={team_id}&season_id={season}…` | JSONP | `roster[0].sections[*].data[*].row` (root dict has a `roster` key) | |
| WHL | `…feed=statviewfeed&view=roster&team_id={team_id}&season_id={season}…` | JSONP | `roster[0].sections[*].data[*].row` | |
| QMJHL | `…feed=statviewfeed&view=roster&team_id={team_id}&season_id={season}…` | JSONP | `roster[0].sections[*].data[*].row` | |

---

## Player Stats Endpoint

### Skaters

| League | Endpoint Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL | `https://api-web.nhle.com/v1/club-stats/{team}/{season}/2` | JSON | `skaters[*]` | Session: `2` = regular season, `3` = playoffs |
| AHL | `…feed=statviewfeed&view=players&season={season}&team={team_id}…` | JSONP | `SiteKit.Players[*]` (after JSONP strip) | `team=all` for all teams |
| PWHL | `…feed=statviewfeed&view=players&season={season}&team={team_id}…` | JSONP | `SiteKit.Players[*]` | `team=all` for all teams |
| OHL | `…feed=statviewfeed&view=players&season={season}&team={team_id}…` | JSONP | `[0].sections[*].data[*].row` | `team=all` for all teams |
| WHL | `…feed=statviewfeed&view=players&season={season}&team={team_id}…` | JSONP | `[0].sections[*].data[*].row` | `team=all` for all teams |
| QMJHL | `…feed=statviewfeed&view=players&season={season}&team={team_id}…` | JSONP | `[0].sections[*].data[*].row` | `team=all` for all teams |

### Goalies

Same endpoint as skaters with `&position=goalies` appended.

| League | Wire format | Data extraction |
| --- | --- | --- |
| AHL / PWHL | JSONP | `SiteKit.Players[*]` |
| OHL / WHL / QMJHL | JSONP | `[0].sections[*].data[*].row` |

---

## Player Page Endpoint (Non-NHL only)

Wire format: **JSONP**.  Returns a player's profile: bio, current season stats, career stats by season, game-by-game log, and optionally shot locations.

Pattern:

```text
{base_url}?feed=statviewfeed&view=player&key={api_key}&client_code={client_code}&league_id={league_id}&player_id={player_id}&season_id={season}&site_id={site_id}&lang=en&statsType={stats_type}
```

| League | Example |
| --- | --- |
| AHL | `https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player&key=ccb91f29d6744675&client_code=ahl&league_id=4&player_id={player_id}&season_id=90&site_id=3&lang=en&statsType=standard` |
| PWHL | `https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player&key=446521baf8c38984&client_code=pwhl&league_id=1&player_id={player_id}&season_id=8&site_id=0&lang=en&statsType=standard` |
| OHL | `https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player&key=f1aa699db3d81487&client_code=ohl&league_id=1&player_id={player_id}&season_id=83&site_id=1&lang=en&statsType=standard` |
| WHL | `https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player&key=f1aa699db3d81487&client_code=whl&league_id=7&player_id={player_id}&season_id=289&site_id=0&lang=en&statsType=standard` |
| QMJHL | `https://cluster.leaguestat.com/feed/index.php?feed=statviewfeed&view=player&key=f322673b6bcae299&client_code=lhjmq&league_id=6&player_id={player_id}&season_id=211&site_id=0&lang=en&statsType=standard` |

Parameters:

- `player_id`: HockeyTech player ID (integer)
- `season_id`: Season ID from the bootstrap data
- `statsType`: `standard` (default, returns full stats) | `bio` (bio only, lighter response)

Data extraction (after JSONP strip): the entire payload is a dict under `SiteKit`.

| Key | Type | Contents |
| --- | --- | --- |
| `SiteKit.info` | dict | Player bio (name, DOB, position, team, etc.) |
| `SiteKit.careerStats` | list | Career totals by season across all leagues |
| `SiteKit.seasonStats` | list | Per-season stats for the current league |
| `SiteKit.gameByGame` | list | Game-by-game log for the selected season |
| `SiteKit.shotLocations` | list | Shot location records (may be absent) |

---

## Teams Endpoint

| League | Endpoint Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| NHL (calendar) | `https://api-web.nhle.com/v1/schedule-calendar/now` | JSON | nested within `gameWeek[*].games[*]` — teams extracted per game | Active teams from current schedule |
| NHL (franchise) | `https://api.nhle.com/stats/rest/en/franchise?sort=fullName&include=lastSeason.id&include=firstSeason.id` | JSON | `data[*]` | Franchise list with first/last season |
| NHL (records) | `https://records.nhl.com/site/api/franchise?…` | JSON | `data[*]` | Full team details with logos |
| NHL (by season) | `https://api-web.nhle.com/v1/standings/{year+1}-01-01` | JSON | `standings[*]` | Derive team list from standings for a given season |
| AHL–QMJHL | See [Bootstrap Endpoint](#bootstrap-endpoint-non-nhl-only) | JSONP | `teams[*]` / `teamsNoAll[*]` (after JSONP strip) | Teams embedded in bootstrap data; root-level keys, no `SiteKit` wrapper |

---

## Bootstrap Endpoint (Non-NHL only)

Wire format: **JSONP** (strip wrapper before parsing — see [Response Formats](#response-formats)).

The bootstrap endpoint returns league metadata: teams, seasons, divisions, conferences, positions, and scorebar. It is fetched automatically on `HockeyScraper` initialization.

Pattern:

```text
{base_url}?feed=statviewfeed&view=bootstrap&season={season}&pageName={page_name}&key={api_key}&client_code={client_code}&league_id={league_id}&site_id={site_id}[&game_id={game_id}]
```

| League | Example (latest season, scorebar page) |
| --- | --- |
| AHL | [lscluster…bootstrap…ahl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=ccb91f29d6744675&client_code=ahl&league_id=4&site_id=3) |
| PWHL | [lscluster…bootstrap…pwhl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=446521baf8c38984&client_code=pwhl&league_id=1&site_id=0) |
| OHL | [lscluster…bootstrap…ohl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=f1aa699db3d81487&client_code=ohl&league_id=1&site_id=1) |
| WHL | [lscluster…bootstrap…whl](https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=f1aa699db3d81487&client_code=whl&league_id=7&site_id=0) |
| QMJHL | [cluster.leaguestat…bootstrap…lhjmq](https://cluster.leaguestat.com/feed/index.php?feed=statviewfeed&view=bootstrap&season=latest&pageName=scorebar&key=f322673b6bcae299&client_code=lhjmq&league_id=6&site_id=0) |

Common `pageName` values: `scorebar`, `schedule`, `standings`, `roster`, `playerStats`

Bootstrap data keys (all after JSONP strip — all keys are at root level, no `SiteKit` wrapper):

| Key | Type | Notes |
| --- | --- | --- |
| `teams` / `teamsNoAll` | `list[dict]` | `teams` includes an "All Teams" placeholder entry; `teamsNoAll` excludes it |
| `regularSeasons` / `playoffSeasons` | `list[dict]` | Season lists. WHL/QMJHL never populate `playoffSeasons`. |
| `divisions` | `list[dict]` | Division list |
| `conferences` | `list[dict]` | Conference list |
| `positions` | `list[dict]` | Player position list |
| `Scorebar` / `SiteKit.Scorebar` | `list[dict]` | Live game scores (only present when games are active). WHL uses top-level `Scorebar`; other leagues use `SiteKit.Scorebar`. |

---

## Scorebar Endpoint (Non-NHL only)

Wire format: **JSONP**.  Returns recent and upcoming games with live scores. Uses the bootstrap endpoint with `pageName=scorebar`.

Pattern:

```text
{base_url}?feed=statviewfeed&view=bootstrap&season={season}&pageName=scorebar&key={api_key}&client_code={client_code}&league_id={league_id}&site_id={site_id}
```

| League | Endpoint (current season) | Data extraction |
| --- | --- | --- |
| AHL | `…season=90&pageName=scorebar&key=ccb91f29d6744675&client_code=ahl…` | `SiteKit.Scorebar[*]` |
| PWHL | `…season=8&pageName=scorebar&key=446521baf8c38984&client_code=pwhl…` | `SiteKit.Scorebar[*]` |
| OHL | `…season=83&pageName=scorebar&key=f1aa699db3d81487&client_code=ohl…` | `SiteKit.Scorebar[*]` |
| WHL | `…season=289&pageName=scorebar&key=f1aa699db3d81487&client_code=whl…` | `Scorebar[*]` (top-level, not under `SiteKit`) |
| QMJHL | `…season=211&pageName=scorebar&key=f322673b6bcae299&client_code=lhjmq…` | `SiteKit.Scorebar[*]` |

---

## NHL-Only Endpoints

### Player Profile & Stats

| Endpoint | Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| Player landing | `https://api-web.nhle.com/v1/player/{player_id}/landing` | JSON | top-level dict | Bio, position, current team, featured season stats, career totals |
| Player game log | `https://api-web.nhle.com/v1/player/{player_id}/game-log/{season}/{game_type}` | JSON | `gameLog[*]` | Per-game stats; `game_type`: `2` = regular season, `3` = playoffs |
| Club stats | `https://api-web.nhle.com/v1/club-stats/{team}/{season}/{session}` | JSON | `skaters[*]` or `goalies[*]` | `session`: `1` = pre-season, `2` = regular season, `3` = playoffs |

### Draft Endpoints

| Endpoint | Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| Draft picks (web API) | `https://api-web.nhle.com/v1/draft/picks/{year}/{round}` | JSON | `picks[*]` | By year and round |
| Draft records | `https://records.nhl.com/site/api/draft?…&cayenneExp=%20draftYear%20=%20{year}…` | JSON | `data[*]` | Full draft data for a given year; nested objects for player/team/franchise |
| Team draft history | `https://records.nhl.com/site/api/draft?…&cayenneExp=franchiseTeam.franchiseId=%22{franchise_id}%22` | JSON | `data[*]` | All draft picks for a franchise |

### HTML Reports (nhl.com)

Wire format: **HTML**.  Parse with BeautifulSoup or similar.  The `game_number` is the zero-padded last 6 digits of the `game_id` (e.g. `game_id=2023020001` → `game_number=020001`).

`scraper.html_pbp(game_id, raw=True)` returns `{'data': '<html>…', 'urls': {…}, 'game_id': …, 'scraped_on': …}`.
`scraper.shifts(game_id, raw=True)` returns `{'home': '<html>…', 'away': '<html>…', 'urls': {…}, 'game_id': …, 'scraped_on': …}`.

| Report | URL Pattern | Notes |
| --- | --- | --- |
| Play-by-play | `https://www.nhl.com/scores/htmlreports/{YYYY}{YYYY+1}/PL{game_number}.HTM` | e.g. `PL020001.HTM` |
| Home team shifts | `https://www.nhl.com/scores/htmlreports/{YYYY}{YYYY+1}/TH{game_number}.HTM` | Home team shift chart |
| Visitor team shifts | `https://www.nhl.com/scores/htmlreports/{YYYY}{YYYY+1}/TV{game_number}.HTM` | Visitor team shift chart |

### Goal Replay

| Endpoint | Pattern | Wire format | Data extraction | Notes |
| --- | --- | --- | --- | --- |
| Goal replay page | `https://www.nhl.com/ppt-replay/goal/{game_id}/{event_id}` | HTML | human-readable page | Human-readable PPT replay page |
| Goal replay JSON | Embedded in PBP as `pptReplayUrl` on goal plays | JSON | top-level list | JSON data for the replay clip |

---

## Endpoint Summary by Category

| Category | NHL | AHL | PWHL | OHL | WHL | QMJHL |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Play-by-play | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Schedule | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Standings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Roster | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Player stats (skaters) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Player stats (goalies) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Teams | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Seasons | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Bootstrap / config | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Scorebar (live scores) | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Draft picks | ✓ | — | — | — | — | — |
| Draft records | ✓ | — | — | — | — | — |
| Team draft history | ✓ | — | — | — | — | — |
| Player profile/landing | ✓ | — | — | — | — | — |
| Player page (profile) | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Player game log | ✓ | — | — | — | — | — |
| HTML play-by-play | ✓ | — | — | — | — | — |
| Shift reports | ✓ | — | — | — | — | — |
| Goal replay | ✓ | — | — | — | — | — |

---

## Play-by-Play: League-Specific Reference

### PBP Style Summary

Two HockeyTech PBP styles are used.  `hockeytech_a` (AHL/PWHL) uses the `gameCenterPlayByPlay` feed; `hockeytech_b` (OHL/WHL/QMJHL) uses the `gc&tab=pxpverbose` feed.  After parsing, the transformer produces a single uniform DataFrame for all leagues.

| Attribute | NHL (native) | hockeytech_a (AHL/PWHL) | hockeytech_b (OHL/WHL/QMJHL) |
| --- | --- | --- | --- |
| Event type field | `typeDescKey` | `event` (string) | `event` (string) |
| Period field | `period` (integer) | `period` → dict `{id, shortName, longName}` → parsed to int | `period` (text "1st"/"OT") + `period_id` (int, always present) |
| OT period identifier | `4`, `5`, … | `"OT1"`, `"OT2"`, … mapped to `4`, `5`, … | `"OT"` or `"1st OT"`, `"2nd OT"`, … mapped to `4`, `5`, … |
| Time-in-period field | `timeInPeriod` (MM:SS) | `time` (MM:SS or HH:MM:SS) | `time` (MM:SS or HH:MM:SS) |
| Coordinates | `xCoord`, `yCoord` (feet, center-ice origin) | `xLocation`, `yLocation` (pixels, top-left origin, canvas 850×400) | `xLocation`, `yLocation` (pixels, center-ice origin, canvas 600×300) |
| Shooter/scorer field | `details.scoringPlayerId` etc. | nested `shooter` / `scorer` / `scoredBy` dicts | flat `scorer_id`, `scorer_first_name`, etc. |
| On-ice players | `homeForwardPlayerIds` etc. | `plus_players` / `minus_players` arrays (key: `id`) | `plus` / `minus` arrays (key: `player_id`) |
| Strength field | `situationCode` | `properties.isPowerPlay` / `isShortHanded` / `isEmptyNet` | `type` / `goal_type` / `power_play` flags |
| Shot events present | ✓ | ✓ | ✗ (WHL); ✓ (OHL, QMJHL) |

---

### Event Types by League

These are the `event` values (lowercased) produced after normalization.  "—" means the league does not emit that event type in its PBP feed.

| Event | NHL | AHL | PWHL | OHL | WHL | QMJHL |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| `goal` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `shot` | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `faceoff` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `hit` | ✓ | — | — | — | — | — |
| `blocked-shot` | ✓ | — | — | — | — | — |
| `missed-shot` | ✓ | — | — | — | — | — |
| `penalty` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `penaltyshot` | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `stoppage` | ✓ | — | — | — | — | — |
| `period-start` | ✓ | — | — | — | — | — |
| `period-end` | ✓ | — | — | — | — | — |
| `goalie-change` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `shootout` | ✓ | — | — | — | — | — |

> **WHL note**: the WHL API does not record shot events — only goals, faceoffs, penalties, and goalie changes are present.  `nhlify_goals` is a no-op for WHL since there are no shot rows to merge.

---

### Coordinate Systems

All leagues' coordinates are normalized to a common system by `transform.py`:

- **x**: −100 ft (left boards) to +100 ft (right boards), center ice = 0
- **y**: −42.5 ft (one board) to +42.5 ft (other board), center ice = 0

Shot distance and angle are computed from the goal post at **(±89, 0)** — the standard NHL goal-line position 11 ft from the end boards.  `abs(x)` is used so both ends map to the same reference point.

| League | Raw canvas size | Raw origin | Raw unit | x conversion | y conversion |
| --- | --- | --- | --- | --- | --- |
| NHL | 200 × 85 ft | center ice | feet (already) | identity | identity |
| AHL / PWHL | 850 × 400 px | top-left corner | pixels | `x_px / 850 × 200 − 100` | `y_px / 400 × 85 − 42.5` |
| OHL / WHL / QMJHL | 600 × 300 px | center ice | pixels | `(x_px − 300) / 3` | `(y_px − 150) × 85/300` |

> The OHL/WHL/QMJHL y-scale is **85/300 ≈ 0.2833 ft/px**, not 1/3.  Using 1/3 would give a ±50 ft rink width instead of the correct ±42.5 ft.

---

### OT Format by League

#### Regular Season vs Playoffs

| League | Reg-season OT | Playoff OT | `ot_period_length` (s) |
| --- | --- | --- | --- |
| NHL | 5-min, 3-on-3, sudden-death (then SO) | 20-min, 5-on-5, sudden-death (no SO) | 300 |
| AHL | 5-min, 3-on-3, sudden-death (then SO) | 20-min, 5-on-5, sudden-death (no SO) | 300 |
| PWHL | 10-min, 3-on-3, sudden-death (then SO) | 20-min, 5-on-5, sudden-death (no SO) | 600 |
| OHL | 5-min, 4-on-4, sudden-death (then SO) | 20-min, 5-on-5, sudden-death (no SO) | 300 |
| WHL | 5-min, 3-on-3, sudden-death (then SO) | 20-min, 5-on-5, sudden-death (no SO) | 300 |
| QMJHL | 5-min, 3-on-3, sudden-death (then SO) | 20-min, 5-on-5, sudden-death (no SO) | 300 |

Pass `is_playoff=True` to `play_by_play()` / `transform_pbp()` so OT `game_seconds` uses 1200 s per period instead of the regular-season length.

#### Historical OT Rule Changes

Use `season_id=` to get the correct OT length for older seasons.  The library looks up `LeagueConfig.ot_period_length_history` — a list of `(first_season_id, ot_seconds)` entries.

| League | Change | Approx. season | Status |
| --- | --- | --- | --- |
| NHL | 5-min OT introduced (replacing 4-on-4) | 2015-16 | Always 300 s in API data range |
| AHL | 5-min 3-on-3 OT introduced | 2015-16 | Always 300 s in API data range |
| PWHL | Launched with 10-min 3-on-3 OT | Season 1 (2023-24) | Always 600 s |
| OHL | 5-min OT throughout modern era | — | Always 300 s in API data range |
| WHL | Changed from 10-min to 5-min OT | ~2019 (season ~266) | TODO: cutoff season unverified |
| QMJHL | Changed from 10-min to 5-min OT | ~2019 (season ~190) | TODO: cutoff season unverified |

> WHL/QMJHL historical entries will be added to `ot_period_length_history` once the exact season ID cutoffs are confirmed.

---

### Known Data Quirks per League

| League | Quirk |
| --- | --- |
| AHL / PWHL | Shot + goal emitted as two separate events at the same timestamp.  `nhlify=True` (default) merges them into a single goal row; the shot's coordinates and type are copied to the goal row. |
| AHL / PWHL | Scorer field alternates between `scorer` and `scoredBy` depending on season.  Both are mapped to `scorerFirstName` / `scorerLastName` / `scorerId`; `scorer` takes precedence and `scoredBy` fills NaNs. |
| AHL / PWHL | `goal_type` encodes strength + empty-net as `"EV"`, `"PP"`, `"SH"`, `"EV.EN"`, `"PP.EN"`, `"SH.EN"`. |
| OHL / WHL / QMJHL | Goal events carry a text period field (`"1st"`, `"OT"`, …); most other events carry a numeric `period_id`.  The transformer prioritises `period_id` and falls back to text-mapped period. |
| WHL | No shot events in the feed — only goals, faceoffs, penalties, and goalie changes.  `shot_distance_ft` and `shot_angle_deg` will be `NaN` for all rows. |
| WHL (pre-~season 283) | Penalty events omit the `time` field at the API level.  Affected rows will have `NaN` for `time_seconds` and `game_seconds`.  This is an upstream data gap. |
| QMJHL | Uses a different base URL (`cluster.leaguestat.com`) instead of `lscluster.hockeytech.com`. |
| NHL | `game_seconds` for OT computed assuming 5-min (300 s) OT periods.  This value in `LeagueConfig` is not used by the NHL pipeline (the NHL API provides absolute `timeInPeriod`); it is present only for consistency. |
