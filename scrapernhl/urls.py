# scrapernhl/urls.py
"""URL builders for every league / endpoint combination."""

from datetime import datetime

from .config import LeagueConfig


def build_bootstrap_url(config: LeagueConfig, game_id: int | None, season: str, page_name: str, **filters) -> str:
    params = f"?feed=statviewfeed&view=bootstrap&season={season}"
    params += f"&pageName={page_name}"
    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"
    params += f"&site_id={config.site_id}"

    if game_id is not None:
        params += f"&game_id={game_id}"

    for key, value in filters.items():
        params += f"&{key}={value}"

    return f"{config.base_url}{params}"


def build_pbp_url(league: str, config: LeagueConfig, game_id: int) -> str:
    if league == "nhl":
        return f"{config.base_url}/v1/gamecenter/{game_id}/play-by-play"

    if config.pbp_style == "hockeytech_a":
        params = f"?feed=statviewfeed&view=gameCenterPlayByPlay&game_id={game_id}"
    else:
        params = f"?feed=gc&tab=pxpverbose&game_id={game_id}"

    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"
    params += "&fmt=json&lang=en"

    return f"{config.base_url}{params}"


def build_stats_url(league: str, config: LeagueConfig, season: int, team: str, position: str, **filters) -> str:
    if league == "nhl":
        return f"{config.base_url}/v1/club-stats/{team}/{season}/2"

    view = "players"
    if position == "goalies":
        filters["position"] = "goalies"

    # HockeyTech APIs default to 20 results; request all players.
    filters.setdefault("start", 0)
    filters.setdefault("limit", 2000)

    params = f"?feed=statviewfeed&view={view}&season={season}&team={team}"
    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"
    params += f"&site_id={config.site_id}"

    for key, value in filters.items():
        params += f"&{key}={value}"

    return f"{config.base_url}{params}"


def build_schedule_url(league: str, config: LeagueConfig, team: str, season: int, **filters) -> str:
    if league == "nhl":
        return f"{config.base_url}/v1/club-schedule-season/{team}/{season}"

    params = f"?feed=statviewfeed&view=schedule&season={season}&team={team}"
    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"

    for key, value in filters.items():
        params += f"&{key}={value}"

    return f"{config.base_url}{params}"


def build_roster_url(league: str, config: LeagueConfig, team: str, season: int) -> str:
    if league == "nhl":
        return f"{config.base_url}/v1/roster/{team}/{season}"

    params = f"?feed=statviewfeed&view=roster&team_id={team}&season_id={season}"
    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"

    return f"{config.base_url}{params}"


_NHL_BASE = "https://api-web.nhle.com"


def build_nhl_pbp_url(game_id: int | str) -> str:
    """NHL: play-by-play for a game."""
    return f"{_NHL_BASE}/v1/gamecenter/{game_id}/play-by-play"


def build_nhl_schedule_url(team: str, season: int | str) -> str:
    """NHL: full season schedule for a team."""
    return f"{_NHL_BASE}/v1/club-schedule-season/{team}/{season}"


def build_nhl_standings_url(date: str) -> str:
    """NHL: standings for a specific date (YYYY-MM-DD)."""
    return f"{_NHL_BASE}/v1/standings/{date}"


def build_nhl_roster_url(team: str, season: int | str) -> str:
    """NHL: roster for a team and season."""
    return f"{_NHL_BASE}/v1/roster/{team}/{season}"


def build_nhl_club_stats_url(team: str, season: int | str, session: int | str = 2) -> str:
    """NHL: skater/goalie stats for a team, season, and session."""
    return f"{_NHL_BASE}/v1/club-stats/{team}/{season}/{session}"


def build_teams_by_season_url(config: LeagueConfig, season: int) -> str:
    """NHL: standings endpoint used to derive the team list for a given season."""
    year = int(str(season)[:4])
    date = f"{year + 1}-01-01"
    return f"{config.base_url}/v1/standings/{date}"


def build_nhl_seasons_url() -> str:
    """NHL: full seasons list from the stats REST API."""
    return "https://api.nhle.com/stats/rest/en/season"


# ---------------------------------------------------------------------------
# NHL-only endpoints (used by scraper_legacy / analytics layer)
# ---------------------------------------------------------------------------

def build_nhl_schedule_calendar_url() -> str:
    """NHL: current schedule calendar (used to resolve active teams)."""
    return "https://api-web.nhle.com/v1/schedule-calendar/now"


def build_nhl_franchise_url() -> str:
    """NHL stats REST API: franchise list with first/last season."""
    return (
        "https://api.nhle.com/stats/rest/en/franchise"
        "?sort=fullName&include=lastSeason.id&include=firstSeason.id"
    )


def build_nhl_records_franchise_url() -> str:
    """NHL records API: franchise list with full team details and logos."""
    return (
        "https://records.nhl.com/site/api/franchise"
        "?include=teams.id"
        "&include=teams.active"
        "&include=teams.triCode"
        "&include=teams.placeName"
        "&include=teams.commonName"
        "&include=teams.fullName"
        "&include=teams.logos"
        "&include=teams.conference.name"
        "&include=teams.division.name"
        "&include=teams.franchiseTeam.firstSeason.id"
        "&include=teams.franchiseTeam.lastSeason.id"
    )


def build_nhl_draft_picks_url(year: int, round: int) -> str:  # noqa: A002
    """NHL: draft picks for a specific year and round."""
    return f"https://api-web.nhle.com/v1/draft/picks/{year}/{round}"


def build_nhl_records_draft_url(year: int) -> str:
    """NHL records API: all draft picks for a given year."""
    return (
        f"https://records.nhl.com/site/api/draft"
        f"?include=draftProspect.id"
        f"&include=player.birthStateProvince"
        f"&include=player.birthCountry"
        f"&include=player.position"
        f"&include=player.onRoster"
        f"&include=player.yearsPro"
        f"&include=player.firstName"
        f"&include=player.lastName"
        f"&include=player.id"
        f"&include=team.id"
        f"&include=team.placeName"
        f"&include=team.commonName"
        f"&include=team.fullName"
        f"&include=team.triCode"
        f"&include=team.logos"
        f"&include=franchiseTeam.franchise.mostRecentTeamId"
        f"&include=franchiseTeam.franchise.teamCommonName"
        f"&include=franchiseTeam.franchise.teamPlaceName"
        f"&cayenneExp=%20draftYear%20=%20{year}&start=0&limit=500"
    )


def build_nhl_records_team_draft_history_url(franchise: int | str) -> str:
    """NHL records API: full draft history for a specific franchise."""
    return (
        f"https://records.nhl.com/site/api/draft"
        f"?include=draftProspect.id"
        f"&include=franchiseTeam"
        f"&include=player.birthStateProvince"
        f"&include=player.birthCountry"
        f"&include=player.position"
        f"&include=player.onRoster"
        f"&include=player.yearsPro"
        f"&include=player.firstName"
        f"&include=player.lastName"
        f"&include=player.id"
        f"&include=team.id"
        f"&include=team.placeName"
        f"&include=team.commonName"
        f"&include=team.fullName"
        f"&include=team.triCode"
        f"&include=team.logos"
        f"&cayenneExp=franchiseTeam.franchiseId=%22{franchise}%22"
    )


def build_nhl_goal_replay_url(game_id: str, event_id: str) -> str:
    """NHL: PPT goal replay URL."""
    return f"https://www.nhl.com/ppt-replay/goal/{game_id}/{event_id}"


def build_nhl_player_landing_url(player_id: int) -> str:
    """NHL: player bio, position, current team, and career stats landing page."""
    return f"{_NHL_BASE}/v1/player/{player_id}/landing"


def build_nhl_player_game_log_url(player_id: int, season: int | str, game_type: int = 2) -> str:
    """NHL: per-game player stats for a given season.

    Parameters:
    - game_type: 2 = regular season, 3 = playoffs
    """
    return f"{_NHL_BASE}/v1/player/{player_id}/game-log/{season}/{game_type}"


def _nhl_html_report_parts(game_id: str) -> tuple[str, str, str]:
    """Return (first_year, second_year, short_id) derived from a game_id string."""
    first_year = game_id[:4]
    second_year = str(int(first_year) + 1)
    short_id = game_id[-6:].zfill(6)
    return first_year, second_year, short_id


def build_nhl_html_pbp_url(game_id: str) -> str:
    """NHL: HTML play-by-play report from nhl.com."""
    first_year, second_year, short_id = _nhl_html_report_parts(game_id)
    return f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/PL{short_id}.HTM"


def build_nhl_html_shifts_home_url(game_id: str) -> str:
    """NHL: HTML home-team shift report from nhl.com."""
    first_year, second_year, short_id = _nhl_html_report_parts(game_id)
    return f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/TH{short_id}.HTM"


def build_nhl_html_shifts_visitor_url(game_id: str) -> str:
    """NHL: HTML visiting-team shift report from nhl.com."""
    first_year, second_year, short_id = _nhl_html_report_parts(game_id)
    return f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/TV{short_id}.HTM"


def build_player_page_url(config: LeagueConfig, player_id: int, season: int, stats_type: str = "standard") -> str:
    """HockeyTech: player profile page (bio, career stats, season stats, game log).

    Parameters:
    - player_id: HockeyTech player ID
    - season: Season ID (e.g. 90 for AHL)
    - stats_type: 'standard' (default) or 'bio' (bio only)
    """
    params = f"?feed=statviewfeed&view=player"
    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"
    params += f"&player_id={player_id}"
    params += f"&season_id={season}"
    params += f"&site_id={config.site_id}"
    params += f"&lang=en"
    if stats_type:
        params += f"&statsType={stats_type}"

    return f"{config.base_url}{params}"


def build_standings_url(league: str, config: LeagueConfig, season: int, **filters) -> str:
    if league == "nhl":
        date = filters.get("date", datetime.now().strftime("%Y-%m-%d"))
        return f"{config.base_url}/v1/standings/{date}"

    group_by = filters.pop("groupTeamsBy", "division")
    context = filters.pop("context", "overall")
    special = filters.pop("special", "false")

    params = f"?feed=statviewfeed&view=teams&season={season}"
    params += f"&key={config.api_key}"
    params += f"&client_code={config.client_code}"
    params += f"&league_id={config.league_id}"
    params += f"&site_id={config.site_id}"
    params += f"&groupTeamsBy={group_by}"
    params += f"&context={context}"
    params += f"&special={special}"

    for key, value in filters.items():
        params += f"&{key}={value}"

    return f"{config.base_url}{params}"
