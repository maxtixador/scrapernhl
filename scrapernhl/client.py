# scrapernhl/client.py
"""Unified client for all hockey leagues."""

import json
from typing import Literal

import pandas as pd

from .config import CACHE_TTL, LEAGUES, LeagueType
from .core.logging_config import get_logger
from .enrichment import enrich_roster, enrich_schedule, enrich_standings, enrich_stats
from .parsers import (
    parse_pbp,
    parse_player_page,
    parse_roster,
    parse_schedule,
    parse_standings,
    parse_stats,
)
from .transform import transform_pbp
from .urls import (
    build_bootstrap_url,
    build_nhl_club_stats_url,
    build_nhl_draft_picks_url,
    build_nhl_franchise_url,
    build_nhl_html_pbp_url,
    build_nhl_html_shifts_home_url,
    build_nhl_html_shifts_visitor_url,
    build_nhl_player_game_log_url,
    build_nhl_player_landing_url,
    build_nhl_records_draft_url,
    build_nhl_records_franchise_url,
    build_nhl_records_team_draft_history_url,
    build_nhl_schedule_calendar_url,
    build_nhl_seasons_url,
    build_nhl_standings_url,
    build_pbp_url,
    build_player_page_url,
    build_roster_url,
    build_schedule_url,
    build_standings_url,
    build_stats_url,
    build_teams_by_season_url,
)
from .utils import Cache, RateLimiter, clean_jsonp, get_session, validate_game_id

LOG = get_logger(__name__)


class HockeyScraper:
    """Unified scraper for all hockey leagues."""

    def __init__(self, league: LeagueType):
        """Create a scraper for the given league.

        Parameters:
        - league: One of 'nhl', 'ahl', 'pwhl', 'ohl', 'whl', 'qmjhl'

        Public attributes:
        - league (str): Normalised league code
        - config (LeagueConfig): League settings — api_key, league_id, site_id, base_url,
          pbp_style, canvas_size, rate limits. Useful when building custom HTTP requests.
        - bootstrap_data (dict | None): League metadata, fetched on first access (non-NHL only).
          Contains teams, seasons, divisions, conferences, and current scorebar.
        """
        self.league = league.lower()
        self.config = LEAGUES[self.league]
        self.session = get_session()
        self.cache = Cache()
        self.limiter = RateLimiter(
            calls=self.config.rate_limit_calls,
            period=self.config.rate_limit_period
        ) if self.league != 'nhl' else None

        # Bootstrap data is fetched lazily on first access (non-NHL only)
        self._bootstrap_data: dict | None = None
        # Lazily populated for QMJHL/WHL which don't expose playoff seasons in bootstrap
        self._extra_seasons: list[dict] | None = None

    def _fetch_bootstrap_on_init(self) -> dict | None:
        """
        Fetch bootstrap data during initialization for non-NHL leagues.

        Returns:
            Bootstrap data dict, or None if fetch fails
        """
        try:
            url = build_bootstrap_url(
                self.config,
                game_id=None,
                season='latest',
                page_name='scorebar',
            )
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            text = clean_jsonp(response.text)
            return json.loads(text) if text else {}
        except Exception:
            # Non-critical: user can still call bootstrap() explicitly
            return None

    # ========================================================================
    # Bootstrap Properties (convenience accessors)
    # ========================================================================

    @property
    def bootstrap_data(self) -> dict | None:
        """Full bootstrap response dict (lazy-fetched on first access for non-NHL leagues)."""
        if self._bootstrap_data is None and self.league != 'nhl':
            self._bootstrap_data = self._fetch_bootstrap_on_init()
        return self._bootstrap_data

    @bootstrap_data.setter
    def bootstrap_data(self, value: dict | None) -> None:
        self._bootstrap_data = value

    @property
    def _bootstrap(self) -> dict:
        """Safe access to the current league's bootstrap subtree (lazy-fetched for non-NHL)."""
        data = self.bootstrap_data
        if not data:
            return {}
        return data.get(self.league, data)

    @property
    def teams(self) -> list:
        """Get teams from bootstrap data (excludes 'All Teams' option)."""
        return self.get_teams(include_all=False)

    @property
    def current_season_id(self) -> str | None:
        """Get current season ID from bootstrap data."""
        return self.get_current_season_id()

    @property
    def current_league_id(self) -> str | None:
        """Get current league ID from bootstrap data."""
        return self.get_current_league_id()

    # ========================================================================
    # League-Aware Bootstrap Extraction Methods
    # ========================================================================

    def get_current_season_id(self) -> str | None:
        return self._bootstrap.get("current_season_id")

    def get_current_league_id(self) -> str | None:
        return self._bootstrap.get("current_league_id")

    def get_teams(self, include_all: bool = False) -> list[dict]:
        key = "teams" if include_all else "teamsNoAll"
        return self._bootstrap.get(key, [])

    def get_team_by_id(self, team_id: str | int) -> dict | None:
        team_id = str(team_id)
        for team in self.get_teams(include_all=True):
            if str(team.get("id")) == team_id:
                return team
        return None

    def get_team_by_code(self, team_code: str) -> dict | None:
        team_code = team_code.strip().upper()
        for team in self.get_teams(include_all=True):
            if team.get("team_code", "").upper() == team_code:
                return team
        return None

    def get_seasons(self, season_type: Literal["all", "regular", "playoff"] = "all") -> list[dict]:
        b = self._bootstrap
        regular = b.get("regularSeasons", [])
        playoff = b.get("playoffSeasons", [])
        all_seasons = b.get("seasons", [])

        # QMJHL and WHL never populate playoffSeasons or the combined seasons list in
        # their bootstrap responses. Lazily probe the ID gaps between regular seasons to
        # discover playoff/preseason IDs that the API omits.
        if not playoff and not all_seasons and self.league in ('qmjhl', 'whl'):
            if self._extra_seasons is None:
                self._extra_seasons = self._scan_gap_seasons()
            playoff = [s for s in self._extra_seasons if s.get('_season_type') == 'playoff']
            all_seasons = regular + self._extra_seasons

        if season_type == "regular":
            return regular
        if season_type == "playoff":
            return playoff
        return all_seasons if all_seasons else regular + playoff

    def get_current_season(self) -> dict | None:
        sid = self.get_current_season_id()
        if not sid:
            return None
        for season in self.get_seasons("all"):
            if str(season.get("id")) == str(sid):
                return season
        return None

    def get_conferences(self, include_all: bool = True) -> list[dict]:
        key = "conferencesAll" if include_all else "conferences"
        return self._bootstrap.get(key, [])

    def get_divisions(self, include_all: bool = True) -> list[dict]:
        key = "divisionsAll" if include_all else "divisions"
        return self._bootstrap.get(key, [])

    def get_positions(self, normalize: bool = True) -> list[dict]:
        positions = self._bootstrap.get("positions", [])
        if not normalize or self.league != "pwhl":
            return positions
        normalized = []
        for p in positions:
            p = dict(p)
            if p.get("name") == "Defenders":
                p["name"] = "Defencemen"
            normalized.append(p)
        return normalized

    def get_goalie_filters(self) -> list[dict]:
        return self._bootstrap.get("goalies", [])

    def get_first_season_year(self) -> str | None:
        return self._bootstrap.get("first_season_year")

    def is_bilingual(self) -> bool:
        return "fr" in self._bootstrap.get("svfLanguages", [])

    def get_league_metadata(self) -> dict:
        leagues = self._bootstrap.get("leagues", [])
        for league in leagues:
            if league.get("code") == self.league:
                return dict(league)
        if leagues:
            return dict(leagues[0])
        return {
            "id": None,
            "name": self.league.upper(),
            "short_name": self.league.upper(),
            "code": self.league,
            "logo_image": "",
        }

    def get_config_flag(self, key: str, default=False):
        config = self._bootstrap.get("svfConfig", {})
        return config.get(key, default)

    def get_player_no_pic_override(self) -> str | None:
        return self._bootstrap.get("playerNoPicLogoOverride")

    def is_playoffs_active(self) -> bool:
        return bool(self._bootstrap.get("playoffSeasons"))

    def get_show_expanded_goalies(self) -> bool:
        return bool(self._bootstrap.get("showExpandedGoaliesOption"))

    def _get_season_bootstrap(self, season: int | None = None) -> dict:
        if season is None:
            season = self.config.default_season

        current_season = self.get_current_season_id()
        if str(season) == str(current_season) or not self.bootstrap_data:
            return self._bootstrap

        try:
            data = self.bootstrap(season=season)
            return data.get(self.league, data)
        except Exception:
            return self._bootstrap

    def _stamp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lineage columns (scraped_at, league) to any silver-layer DataFrame.

        Called at the end of every data method that returns a DataFrame.
        PBP already gets these columns from transform._add_metadata().
        """
        from datetime import datetime, timezone
        if 'scraped_at' not in df.columns:
            df['scraped_at'] = datetime.now(timezone.utc).isoformat()
        if 'league' not in df.columns:
            df['league'] = self.league
        return df

    # ========================================================================
    # Core Methods
    # ========================================================================

    def play_by_play(
        self,
        game_id: int,
        nhlify: bool = True,
        raw: bool = False,
        season_id: int | None = None,
        is_playoff: bool = False,
    ) -> pd.DataFrame | dict:
        """Get play-by-play data.

        Parameters:
        - raw: If True, return the unprocessed API response dict instead of a DataFrame.
        - season_id: League-specific season ID (e.g. 90 for AHL 2024-25).
          Used to look up the correct OT length for leagues where the format
          has changed over time.  Defaults to the league's default_season.
        - is_playoff: Set True for playoff games so OT game_seconds are
          computed with 20-min periods instead of the regular-season OT length.
        """
        game_id = validate_game_id(game_id)
        url = build_pbp_url(self.league, self.config, game_id)
        data = self._fetch(url, cache_ttl=CACHE_TTL['pbp'])

        if raw:
            return data

        resolved_season = season_id if season_id is not None else self.config.default_season
        events = parse_pbp(self.league, self.config.pbp_style, data)
        df = transform_pbp(
            events,
            self.league,
            nhlify=nhlify,
            game_id=game_id,
            season_id=resolved_season,
            is_playoff=is_playoff,
        )

        return df

    def player_stats(
        self,
        season: int | None = None,
        team: str = 'all',
        position: Literal['skaters', 'goalies'] = 'skaters',
        raw: bool = False,
        **filters,
    ) -> pd.DataFrame | dict:
        """Get player statistics.

        Parameters:
        - raw: If True, return the unprocessed API response dict instead of a DataFrame.
        """
        season = season or self.config.default_season
        url = build_stats_url(self.league, self.config, season, team, position, **filters)
        data = self._fetch(url, cache_ttl=CACHE_TTL['stats'])

        if raw:
            return data

        players = parse_stats(self.league, data, position)
        df = pd.json_normalize(players)

        if self.league != 'nhl':
            season_bootstrap = self._get_season_bootstrap(season)
            df = enrich_stats(df, season_bootstrap, season, self.league)

        return self._stamp(df)

    def schedule(self, team: str = 'all', season: int | None = None, raw: bool = False, **filters) -> pd.DataFrame | dict:
        """Get team schedule.

        Parameters:
        - raw: If True, return the unprocessed API response dict instead of a DataFrame.
        """
        season = season or self.config.default_season
        url = build_schedule_url(self.league, self.config, team, season, **filters)
        data = self._fetch(url, cache_ttl=CACHE_TTL['schedule'])

        if raw:
            return data

        games = parse_schedule(self.league, data)
        df = pd.json_normalize(games)

        if self.league != 'nhl':
            season_bootstrap = self._get_season_bootstrap(season)
            df = self._format_hockeytech_schedule(df)
            df = enrich_schedule(df, season_bootstrap, season, self.league)

        return self._stamp(df)

    def roster(self, team: str, season: int | None = None, raw: bool = False) -> pd.DataFrame | dict:
        """Get team roster.

        Parameters:
        - team: Numeric team ID or team abbreviation code (e.g. 'MTL' for NHL, '54' or 'Rou' for QMJHL).
          Non-numeric codes are automatically resolved to numeric IDs via bootstrap data.
        - raw: If True, return the unprocessed API response dict instead of a DataFrame.
        """
        season = season or self.config.default_season

        # HockeyTech roster endpoint requires a numeric team_id; resolve abbreviation codes.
        if self.league != 'nhl' and not str(team).lstrip('-').isdigit():
            resolved = self.get_team_by_code(str(team))
            if resolved:
                team = resolved['id']

        url = build_roster_url(self.league, self.config, team, season)
        data = self._fetch(url, cache_ttl=CACHE_TTL['roster'])

        if raw:
            return data

        players = parse_roster(self.league, data)
        df = pd.json_normalize(players)

        if self.league != 'nhl':
            season_bootstrap = self._get_season_bootstrap(season)
            df = enrich_roster(df, season_bootstrap, season, self.league, team)

        return self._stamp(df)

    def standings(self, season: int | None = None, raw: bool = False, **filters) -> pd.DataFrame | dict:
        """Get league standings.

        Parameters:
        - raw: If True, return the unprocessed API response dict instead of a DataFrame.
        """
        season = season or self.config.default_season
        url = build_standings_url(self.league, self.config, season, **filters)
        data = self._fetch(url, cache_ttl=CACHE_TTL['standings'])

        if raw:
            return data

        teams = parse_standings(self.league, data)
        df = pd.json_normalize(teams)

        if self.league != 'nhl':
            season_bootstrap = self._get_season_bootstrap(season)
            df = enrich_standings(df, season_bootstrap, season, self.league)

        return self._stamp(df)

    def player_profile(self, player_id: int, season: int | None = None, stats_type: str = "standard", raw: bool = False) -> dict:
        """Get a player's profile page from the HockeyTech API (non-NHL only).

        Returns a dict with keys: 'info' (bio), 'careerStats', 'seasonStats',
        'gameByGame', and potentially 'shotLocations'.

        Parameters:
        - player_id: HockeyTech player ID
        - season: Season ID. Defaults to the league's current season.
        - stats_type: 'standard' (default, includes stats) or 'bio' (bio only)
        - raw: If True, return the unprocessed API response dict instead.
        """
        if self.league == 'nhl':
            raise NotImplementedError(
                "player_profile() is for non-NHL leagues. "
                "Use player_landing() or player_game_log() for NHL."
            )
        season = season or self.config.default_season
        url = build_player_page_url(self.config, player_id, season, stats_type)
        data = self._fetch(url, cache_ttl=CACHE_TTL['stats'])

        if raw:
            return data

        return parse_player_page(data)

    # ========================================================================
    # Raw Access
    # ========================================================================

    def url_for(self, data_type: str, **kwargs) -> str:
        """Return the URL that would be fetched for a given data type.

        Useful for debugging, curl inspection, or building custom HTTP requests.
        See _build_url for the full list of supported data_type values.

        Examples:
            scraper.url_for('pbp', game_id=2023020001)
            scraper.url_for('standings', season=90)
            scraper.url_for('html_pbp', game_id=2023020001)
            scraper.url_for('draft', year=2024, round=1)
            scraper.url_for('player_game_log', player_id=8478402, season=20232024)
        """
        return self._build_url(data_type, **kwargs)

    def fetch_raw(self, data_type: str, **kwargs) -> dict:
        """Fetch the raw API response dict for a given data type, bypassing all parsing.

        Returns the unprocessed JSON exactly as the API sends it, with caching
        and rate limiting still applied. Use url_for() to inspect the URL first,
        or raw_source() to bypass the cache and get the true wire payload.

        See _build_url for the full list of supported data_type values.

        Examples:
            scraper.fetch_raw('pbp', game_id=2023020001)
            scraper.fetch_raw('player_profile', player_id=8478402)
            scraper.fetch_raw('standings', season=90, context='home')
            scraper.fetch_raw('team_stats', team='MTL', season=20252026)
        """
        url = self._build_url(data_type, **kwargs)
        return self._fetch(url, cache_ttl=0)

    # ========================================================================
    # Convenience Aliases
    # ========================================================================

    def scrape_pbp(self, game_id: int, **kwargs) -> pd.DataFrame:
        """Alias for play_by_play()."""
        return self.play_by_play(game_id, **kwargs)

    def scrape_game_pbp(self, game_id: int, **kwargs) -> pd.DataFrame:
        """Alias for play_by_play() (all leagues)."""
        return self.play_by_play(game_id, **kwargs)

    def scrape_schedule(self, team: str = 'all', season: int | None = None, **kwargs) -> pd.DataFrame:
        """Alias for schedule()."""
        return self.schedule(team, season, **kwargs)

    def scrape_roster(self, team: str, season: int | None = None) -> pd.DataFrame:
        """Alias for roster()."""
        return self.roster(team, season)

    def scrape_standings(self, season: int | None = None, **kwargs) -> pd.DataFrame:
        """Alias for standings()."""
        return self.standings(season, **kwargs)

    def scrape_skaters(self, season: int | None = None, team: str = 'all', **kwargs) -> pd.DataFrame:
        """Get skater stats."""
        return self.player_stats(season, team, position='skaters', **kwargs)

    def scrape_goalies(self, season: int | None = None, team: str = 'all', **kwargs) -> pd.DataFrame:
        """Get goalie stats."""
        return self.player_stats(season, team, position='goalies', **kwargs)

    def scrape_teams(self, source: str = "calendar", raw: bool = False) -> pd.DataFrame | dict:
        """Get NHL team data from various public endpoints.

        Parameters:
        - source: One of ["calendar", "franchise", "records"]
          - "calendar": active teams from the schedule calendar (default)
          - "franchise": franchise list with first/last season from stats REST API
          - "records": franchise list with full team details and logos from records API
        - raw: If True, return the unprocessed API response dict instead of a DataFrame.
        """
        if self.league != 'nhl':
            raise NotImplementedError("scrape_teams() with source is only available for NHL.")

        from .urls import (
            build_nhl_franchise_url,
            build_nhl_records_franchise_url,
            build_nhl_schedule_calendar_url,
        )

        source_urls = {
            "calendar": build_nhl_schedule_calendar_url(),
            "franchise": build_nhl_franchise_url(),
            "records": build_nhl_records_franchise_url(),
        }

        if source not in source_urls:
            raise ValueError(f"Invalid source '{source}'. Must be one of: {list(source_urls)}")

        url = source_urls[source]
        data = self._fetch(url, cache_ttl=CACHE_TTL['standings'])

        if raw:
            return data

        if isinstance(data, dict) and "data" in data:
            records = data["data"]
        elif isinstance(data, dict) and "teams" in data:
            records = data["teams"]
        elif isinstance(data, list):
            records = data
        else:
            records = [data]

        df = pd.json_normalize(records)
        df['source'] = source
        df['league'] = self.league
        return self._stamp(df)

    def teams_by_season(self, season: int | None = None, raw: bool = False) -> pd.DataFrame | dict | list:
        """Get teams for a specific season.

        Parameters:
        - raw: If True, return the unprocessed API response (dict for NHL, list for non-NHL).
        """
        season = season or self.config.default_season

        if self.league == 'nhl':
            from .urls import build_teams_by_season_url
            url = build_teams_by_season_url(self.config, season)
            data = self._fetch(url, cache_ttl=CACHE_TTL['standings'])
            if raw:
                return data
            df = pd.json_normalize(data.get('standings', []))
            df['season'] = str(season)
            df['league'] = self.league
            return self._stamp(df)

        season_bootstrap = self._get_season_bootstrap(season)
        if raw:
            return season_bootstrap
        teams = season_bootstrap.get("teamsNoAll", season_bootstrap.get("teams", []))
        df = pd.json_normalize(teams)
        df['season'] = str(season)
        df['league'] = self.league
        return self._stamp(df)

    def seasons(self, season_type: Literal["all", "regular", "playoff"] = "all", raw: bool = False) -> pd.DataFrame | dict | list:
        """Get seasons data for the league.

        Parameters:
        - raw: If True, return the unprocessed API response (dict for NHL, list for non-NHL).
        """
        if self.league == 'nhl':
            from .urls import build_nhl_seasons_url
            url = build_nhl_seasons_url()
            data = self._fetch(url, cache_ttl=CACHE_TTL['standings'])
            if raw:
                return data
            df = pd.json_normalize(data.get('data', []))
            df['league'] = self.league
            return self._stamp(df)

        if raw:
            return self.bootstrap_data or {}
        seasons_list = self.get_seasons(season_type)
        df = pd.json_normalize(seasons_list)
        df['league'] = self.league
        return self._stamp(df)

    # ========================================================================
    # Bootstrap / Configuration
    # ========================================================================

    def bootstrap(
        self,
        game_id: int | None = None,
        season: str = 'latest',
        page_name: str = 'scorebar',
        **filters,
    ) -> dict:
        """Get bootstrap/configuration data for the league (non-NHL only)."""
        if self.league == 'nhl':
            raise NotImplementedError("Bootstrap endpoint not available for NHL.")

        url = build_bootstrap_url(self.config, game_id, season, page_name, **filters)
        return self._fetch(url, cache_ttl=CACHE_TTL['standings'])

    # ========================================================================
    # Batch Operations
    # ========================================================================

    def scrape_multiple_games(self, game_ids: list[int], **kwargs) -> pd.DataFrame:
        """Scrape multiple games and concatenate."""
        dfs = []
        for game_id in game_ids:
            try:
                df = self.play_by_play(game_id, **kwargs)
                dfs.append(df)
            except Exception as e:
                LOG.warning(f"Failed to scrape game {game_id}: {e}")
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    # ========================================================================
    # NHL-only Methods
    # ========================================================================

    def _nhl_only(self, method_name: str):
        if self.league != 'nhl':
            raise NotImplementedError(f"{method_name}() is only available for NHL.")

    def get_game_data(self, game_id: int | str, add_goal_replay: bool = False) -> dict:
        """Get raw NHL play-by-play JSON dict for a game.

        Parameters:
        - game_id: NHL game ID
        - add_goal_replay: Whether to fetch goal replay URLs (default False)

        Returns:
        - dict: Full API response with enriched play records
        """
        self._nhl_only("get_game_data")
        from .nhl.scraper_legacy import getGameData
        return getGameData(game_id, addGoalReplayData=add_goal_replay)

    def scrape_plays(self, game_id: int | str, add_goal_replay: bool = False) -> pd.DataFrame:
        """Get NHL play-by-play data from JSON API as a DataFrame.

        Parameters:
        - game_id: NHL game ID
        - add_goal_replay: Whether to fetch goal replay URLs (default False)

        Returns:
        - pd.DataFrame: Play-by-play records with game metadata
        """
        self._nhl_only("scrape_plays")
        from .nhl.scraper_legacy import scrapePlays
        return scrapePlays(game_id, addGoalReplayData=add_goal_replay, output_format="pandas")

    def standings_by_date(self, date: str | None = None, raw: bool = False) -> pd.DataFrame | list:
        """Get NHL standings for a specific date.

        Parameters:
        - date: Date string in 'YYYY-MM-DD' format. Defaults to Jan 1 of the previous year.
        - raw: If True, return the unprocessed list of records instead of a DataFrame.

        Returns:
        - pd.DataFrame (or list if raw=True): Standings data
        """
        self._nhl_only("standings_by_date")
        if raw:
            from .nhl.scraper_legacy import getStandingsData
            return getStandingsData(date)
        from .nhl.scraper_legacy import scrapeStandings
        return scrapeStandings(date=date, output_format="pandas")

    def team_stats(
        self,
        team: str,
        season: int | str | None = None,
        session: int | str = 2,
        goalies: bool = False,
        raw: bool = False,
    ) -> pd.DataFrame | list:
        """Get NHL team/club statistics.

        Parameters:
        - team: Team abbreviation (e.g., 'MTL')
        - season: Season ID (e.g., 20242025). Defaults to current season.
        - session: 1=pre-season, 2=regular season, 3=playoffs (default 2)
        - goalies: If True, return goalie stats; otherwise skater stats
        - raw: If True, return the unprocessed list of records instead of a DataFrame.

        Returns:
        - pd.DataFrame (or list if raw=True): Player statistics for the team
        """
        self._nhl_only("team_stats")
        season = season or self.config.default_season
        if raw:
            from .nhl.scraper_legacy import getTeamStatsData
            return getTeamStatsData(team, season, session, goalies)
        from .nhl.scraper_legacy import scrapeTeamStats
        return scrapeTeamStats(team, season, session, goalies, output_format="pandas")

    def draft(self, year: int | str = 2024, round: int | str = "all", raw: bool = False) -> pd.DataFrame | list:  # noqa: A002
        """Get NHL draft picks for a given year and round.

        Parameters:
        - year: Draft year (e.g., 2024)
        - round: Round number or 'all' for all rounds (default 'all')
        - raw: If True, return the unprocessed list of records instead of a DataFrame.

        Returns:
        - pd.DataFrame (or list if raw=True): Draft pick records
        """
        self._nhl_only("draft")
        if raw:
            from .nhl.scraper_legacy import getDraftData
            return getDraftData(year, round)
        from .nhl.scraper_legacy import scrapeDraftData
        return scrapeDraftData(year, round, output_format="pandas")

    def draft_records(self, year: int | str = 2025, raw: bool = False) -> pd.DataFrame | list:
        """Get NHL draft records from the NHL Records API.

        Parameters:
        - year: Draft year (e.g., 2025)
        - raw: If True, return the unprocessed list of records instead of a DataFrame.

        Returns:
        - pd.DataFrame (or list if raw=True): Draft records with detailed player and team info
        """
        self._nhl_only("draft_records")
        if raw:
            from .nhl.scraper_legacy import getRecordsDraftData
            return getRecordsDraftData(year)
        from .nhl.scraper_legacy import scrapeDraftRecords
        return scrapeDraftRecords(year, output_format="pandas")

    def team_draft_history(self, franchise: int | str = 1, raw: bool = False) -> pd.DataFrame | list:
        """Get NHL draft history for a specific franchise.

        Parameters:
        - franchise: Franchise ID (e.g., 1 for New Jersey Devils)
        - raw: If True, return the unprocessed list of records instead of a DataFrame.

        Returns:
        - pd.DataFrame (or list if raw=True): All draft picks for the franchise
        """
        self._nhl_only("team_draft_history")
        if raw:
            from .nhl.scraper_legacy import getRecordsTeamDraftHistoryData
            return getRecordsTeamDraftHistoryData(franchise)
        from .nhl.scraper_legacy import scrapeTeamDraftHistory
        return scrapeTeamDraftHistory(franchise, output_format="pandas")

    def goal_replay(self, json_url: str) -> list[dict]:
        """Get NHL goal replay data from a PPT replay URL.

        Parameters:
        - json_url: The pptReplayUrl from a goal play record

        Returns:
        - list[dict]: Goal replay data
        """
        self._nhl_only("goal_replay")
        from .nhl.scraper_legacy import getGoalReplayData
        return getGoalReplayData(json_url)

    def html_pbp(self, game_id: int | str, raw: bool = False, return_raw: bool = False) -> pd.DataFrame | dict | tuple:
        """Scrape and parse NHL HTML play-by-play report.

        Parameters:
        - game_id: NHL game ID
        - raw: If True, return the raw HTML response dict with keys
          'data' (HTML string), 'urls', 'game_id', 'scraped_on', 'source'.
        - return_raw: Legacy flag; if True return (DataFrame, parsed_dict) tuple.

        Returns:
        - pd.DataFrame, dict (if raw=True), or tuple (if return_raw=True)
        """
        self._nhl_only("html_pbp")
        if raw:
            from .nhl.scraper_legacy import scrapeHtmlPbp
            return scrapeHtmlPbp(game_id)
        from .nhl.scraper_legacy import scrape_html_pbp
        return scrape_html_pbp(game_id, return_raw=return_raw)

    def shifts(self, game_id: int | str, raw: bool = False) -> pd.DataFrame | dict:
        """Scrape NHL HTML shift reports for a game.

        Parameters:
        - game_id: NHL game ID
        - raw: If True, return the raw HTML response dict with keys
          'home' (HTML string), 'away' (HTML string), 'urls', 'game_id',
          'scraped_on', 'source'.

        Returns:
        - pd.DataFrame (or dict if raw=True): Shift data for all players
        """
        self._nhl_only("shifts")
        if raw:
            from .nhl.scraper_legacy import scrapeHTMLShifts
            return scrapeHTMLShifts(game_id)
        from .nhl.scraper_legacy import scrape_shifts
        return scrape_shifts(game_id)

    def scrape_game(
        self,
        game_id: int | str,
        add_goal_replay: bool = False,
        include_tuple: bool = False,
    ) -> pd.DataFrame:
        """Full NHL game pipeline combining HTML PBP, HTML shifts, and JSON API data.

        Merges event data with on-ice player assignments, strength state,
        and zone start qualifiers.

        Parameters:
        - game_id: NHL game ID
        - add_goal_replay: Whether to fetch goal replay data (default False)
        - include_tuple: If True, return (DataFrame, metadata_dict) tuple

        Returns:
        - pd.DataFrame (or tuple if include_tuple=True): Fully enriched PBP data
        """
        self._nhl_only("scrape_game")
        from .nhl.scraper_legacy import scrape_game as _scrape_game
        return _scrape_game(game_id, addGoalReplayData=add_goal_replay, include_tuple=include_tuple)

    # ========================================================================
    # NHL Analytics / Advanced Stats
    # ========================================================================

    def build_shifts_events(self, shifts: pd.DataFrame) -> pd.DataFrame:
        """Convert shift data into ON/OFF events for play-by-play analysis.

        Parameters:
        - shifts: DataFrame from shifts()

        Returns:
        - pd.DataFrame: Shift ON/OFF events
        """
        self._nhl_only("build_shifts_events")
        from .nhl.scraper_legacy import build_shifts_events
        return build_shifts_events(shifts)

    def build_on_ice_long(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert list-based on-ice columns into a tidy long format table.

        Parameters:
        - df: PBP DataFrame with list-based on-ice columns

        Returns:
        - pd.DataFrame: Long-format on-ice table (no numbered wide columns)
        """
        self._nhl_only("build_on_ice_long")
        from .nhl.scraper_legacy import build_on_ice_long
        return build_on_ice_long(df)

    def build_on_ice_wide(
        self,
        df: pd.DataFrame,
        max_skaters: int = 6,
        include_goalie: bool = True,
        drop_list_cols: bool = False,
    ) -> pd.DataFrame:
        """Expand on-ice player lists into named wide columns (skater_1..N, goalie).

        Parameters:
        - df: PBP DataFrame with list-based on-ice columns
        - max_skaters: Max number of skater columns per team (default 6)
        - include_goalie: Whether to include goalie columns (default True)
        - drop_list_cols: Whether to drop the original list columns (default False)

        Returns:
        - pd.DataFrame: PBP with expanded wide on-ice columns
        """
        self._nhl_only("build_on_ice_wide")
        from .nhl.scraper_legacy import build_on_ice_wide
        return build_on_ice_wide(df, max_skaters=max_skaters, include_goalie=include_goalie, drop_list_cols=drop_list_cols)

    def seconds_matrix(self, df: pd.DataFrame, shifts: pd.DataFrame) -> pd.DataFrame:
        """Create boolean player-by-second on-ice matrix.

        Parameters:
        - df: PBP DataFrame from scrape_game()
        - shifts: Shifts DataFrame from shifts()

        Returns:
        - pd.DataFrame: Matrix where rows=players, columns=game seconds, values=on-ice boolean
        """
        self._nhl_only("seconds_matrix")
        from .nhl.scraper_legacy import seconds_matrix
        return seconds_matrix(df, shifts)

    def strengths_by_second(self, matrix_df: pd.DataFrame) -> pd.DataFrame:
        """Get per-second strength state table from a player-by-second matrix.

        Parameters:
        - matrix_df: Output from seconds_matrix()

        Returns:
        - pd.DataFrame: Per-second strength counts and labels for home/away
        """
        self._nhl_only("strengths_by_second")
        from .nhl.scraper_legacy import strengths_by_second
        return strengths_by_second(matrix_df)

    def toi_by_strength_all(
        self,
        matrix_df: pd.DataFrame,
        strengths_df: pd.DataFrame,
        in_seconds: bool = False,
    ) -> pd.DataFrame:
        """Get total time-on-ice per player per strength state.

        Parameters:
        - matrix_df: Output from seconds_matrix()
        - strengths_df: Output from strengths_by_second()
        - in_seconds: Return TOI in seconds instead of minutes (default False)

        Returns:
        - pd.DataFrame: Per-player, per-strength TOI
        """
        self._nhl_only("toi_by_strength_all")
        from .nhl.scraper_legacy import toi_by_strength_all
        return toi_by_strength_all(matrix_df, strengths_df, in_seconds=in_seconds)

    def shared_toi_teammates(
        self,
        matrix_df: pd.DataFrame,
        strengths_df: pd.DataFrame,
        in_seconds: bool = False,
    ) -> pd.DataFrame:
        """Get pairwise teammate shared time-on-ice by strength state.

        Parameters:
        - matrix_df: Output from seconds_matrix()
        - strengths_df: Output from strengths_by_second()
        - in_seconds: Return TOI in seconds instead of minutes (default False)

        Returns:
        - pd.DataFrame: Pairwise teammate TOI by strength
        """
        self._nhl_only("shared_toi_teammates")
        from .nhl.scraper_legacy import shared_toi_teammates_by_strength
        return shared_toi_teammates_by_strength(matrix_df, strengths_df, in_seconds=in_seconds)

    def shared_toi_opponents(
        self,
        matrix_df: pd.DataFrame,
        strengths_df: pd.DataFrame,
        in_seconds: bool = False,
    ) -> pd.DataFrame:
        """Get cross-team opponent shared time-on-ice by strength state.

        Parameters:
        - matrix_df: Output from seconds_matrix()
        - strengths_df: Output from strengths_by_second()
        - in_seconds: Return TOI in seconds instead of minutes (default False)

        Returns:
        - pd.DataFrame: Pairwise opponent TOI by strength
        """
        self._nhl_only("shared_toi_opponents")
        from .nhl.scraper_legacy import shared_toi_opponents_by_strength
        return shared_toi_opponents_by_strength(matrix_df, strengths_df, in_seconds=in_seconds)

    def on_ice_stats(
        self,
        pbp: pd.DataFrame,
        include_goalies: bool = False,
        rates: bool = False,
    ) -> pd.DataFrame:
        """Compute per-player, per-strength on-ice stats (Corsi, Fenwick, TOI).

        Metrics: CF/CA, FF/FA, SF/SA, GF/GA, PF/PA.

        Parameters:
        - pbp: Play-by-play DataFrame from scrape_game()
        - include_goalies: Whether to include goalies in output (default False)
        - rates: Whether to add per-60 rate columns (default False)

        Returns:
        - pd.DataFrame: Per-player, per-strength on-ice stats
        """
        self._nhl_only("on_ice_stats")
        from .nhl.scraper_legacy import on_ice_stats_by_player_strength
        return on_ice_stats_by_player_strength(pbp, include_goalies=include_goalies, rates=rates)

    def combo_on_ice_stats(
        self,
        pbp: pd.DataFrame,
        focus_team: str,
        n_team: int = 2,
        m_opp: int = 0,
        min_toi: int = 15,
        include_goalies: bool = False,
        rates: bool = False,
    ) -> pd.DataFrame:
        """Compute on-ice stats for player combinations on a focus team.

        Parameters:
        - pbp: Play-by-play DataFrame from scrape_game()
        - focus_team: Team abbreviation to compute combos for
        - n_team: Size of player combinations on the focus team (default 2)
        - m_opp: Size of opponent player combinations to cross against (default 0)
        - min_toi: Minimum TOI in seconds to include a combo (default 15)
        - include_goalies: Whether to include goalies in combinations (default False)
        - rates: Whether to add per-60 rate columns (default False)

        Returns:
        - pd.DataFrame: Combination on-ice stats by strength
        """
        self._nhl_only("combo_on_ice_stats")
        from .nhl.scraper_legacy import combo_on_ice_stats as _combo_on_ice_stats
        return _combo_on_ice_stats(
            pbp, focus_team=focus_team, n_team=n_team, m_opp=m_opp,
            min_TOI=min_toi, include_goalies=include_goalies, rates=rates,
        )

    def team_strength_aggregates(self, pbp: pd.DataFrame, rates: bool = False) -> pd.DataFrame:
        """Aggregate on-ice shot/goal stats by team and strength state.

        Parameters:
        - pbp: Play-by-play DataFrame from scrape_game()
        - rates: Whether to add per-60 rate columns (default False)

        Returns:
        - pd.DataFrame: Per-team, per-strength aggregated stats
        """
        self._nhl_only("team_strength_aggregates")
        from .nhl.scraper_legacy import team_strength_aggregates
        return team_strength_aggregates(pbp, rates=rates)

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _scan_gap_seasons(self) -> list[dict]:
        """Discover non-regular season IDs for QMJHL/WHL by probing ID gaps between regular seasons.

        These leagues never populate ``playoffSeasons`` or the combined ``seasons`` list in their
        bootstrap responses, so playoff/preseason IDs are invisible unless explicitly probed.
        We infer season type from when games are played (Mar–Jun → playoffs, Jul–Sep → pre-season).
        """
        import re

        regular = self._bootstrap.get('regularSeasons', [])
        regular_ids = sorted(int(s['id']) for s in regular)
        if len(regular_ids) < 2:
            return []

        # Only probe gaps between the most recent 3 regular seasons to limit API calls
        recent = regular_ids[-3:]
        gap_ids: list[int] = []
        for i in range(len(recent) - 1):
            gap_ids.extend(range(recent[i] + 1, recent[i + 1]))

        if not gap_ids:
            return []

        month_abbrs = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
        }

        def parse_month(date_str: str) -> int:
            for abbr, num in month_abbrs.items():
                if abbr in date_str:
                    return num
            return 0

        def make_name(sid: int, s_type: str) -> str:
            prev = next(
                (s for s in sorted(regular, key=lambda x: -int(x['id'])) if int(s['id']) < sid),
                None,
            )
            nxt = next(
                (s for s in sorted(regular, key=lambda x: int(x['id'])) if int(s['id']) > sid),
                None,
            )
            m_prev = re.search(r'(\d{4})\s*[-\u2013]\s*\d{2}', (prev or {}).get('name', ''))
            m_next = re.search(r'(\d{4})\s*[-\u2013]\s*\d{2}', (nxt or {}).get('name', ''))
            if s_type == 'playoff' and m_prev:
                return f'{int(m_prev.group(1)) + 1} Playoffs'
            if s_type == 'preseason' and m_next:
                yr = int(m_next.group(1))
                return f'{yr}-{str(yr + 1)[2:]} Pre-Season'
            return f'Season {sid}'

        discovered: list[dict] = []
        for sid in gap_ids:
            try:
                url = build_schedule_url(self.league, self.config, '0', sid)
                data = self._fetch(url, cache_ttl=CACHE_TTL['standings'])
                if not isinstance(data, list) or not data:
                    continue
                sections = data[0].get('sections', [])
                if not sections:
                    continue
                games = sections[0].get('data', [])
                if not games:
                    continue
                first_month = parse_month(games[0].get('row', {}).get('date_with_day', ''))
                if 3 <= first_month <= 6:
                    s_type = 'playoff'
                elif 7 <= first_month <= 9:
                    s_type = 'preseason'
                else:
                    s_type = 'other'
                discovered.append({
                    'id': str(sid),
                    'name': make_name(sid, s_type),
                    '_season_type': s_type,
                })
            except Exception:
                continue

        return discovered

    def _fetch(self, url: str, cache_ttl: int) -> dict:
        """Fetch data with caching and rate limiting."""
        if cache_ttl > 0:
            cached = self.cache.get(url)
            if cached:
                return cached

        if self.limiter:
            self.limiter.wait()

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        if self.league == 'nhl':
            data = response.json()
        else:
            text = clean_jsonp(response.text)
            data = json.loads(text) if text else {}

        if cache_ttl > 0:
            self.cache.set(url, data, cache_ttl)

        return data

    def _build_url(self, data_type: str, **kwargs) -> str:  # noqa: PLR0912
        """Build a URL for the given data_type. Used by url_for(), fetch_raw(), and raw_source().

        Supported data_type values (all leagues unless noted):
            pbp, stats, schedule, roster, standings, bootstrap/scorebar,
            player_profile, player_game_log (NHL),
            teams (NHL, source='calendar'|'franchise'|'records'),
            teams_by_season, seasons,
            html_pbp (NHL), shifts_home (NHL), shifts_away (NHL),
            standings_by_date (NHL, date='YYYY-MM-DD'),
            team_stats (NHL, team=, season=, session=),
            draft (NHL, year=, round=),
            draft_records (NHL, year=),
            team_draft_history (NHL, franchise=).
        """
        season = kwargs.get('season', self.config.default_season)
        match data_type:
            case 'pbp':
                return build_pbp_url(self.league, self.config, validate_game_id(kwargs['game_id']))
            case 'stats':
                return build_stats_url(
                    self.league, self.config, season,
                    kwargs.get('team', 'all'),
                    kwargs.get('position', 'skaters'),
                )
            case 'schedule':
                return build_schedule_url(self.league, self.config, kwargs.get('team', 'all'), season)
            case 'roster':
                return build_roster_url(self.league, self.config, kwargs['team'], season)
            case 'standings':
                return build_standings_url(self.league, self.config, season)
            case 'bootstrap' | 'scorebar':
                return build_bootstrap_url(
                    self.config,
                    game_id=kwargs.get('game_id'),
                    season=kwargs.get('season', 'latest'),
                    page_name=kwargs.get('page_name', 'scorebar'),
                )
            case 'player_profile':
                if self.league == 'nhl':
                    return build_nhl_player_landing_url(kwargs['player_id'])
                return build_player_page_url(
                    self.config, kwargs['player_id'], season,
                    kwargs.get('stats_type', 'standard'),
                )
            case 'player_game_log':
                self._nhl_only('player_game_log')
                return build_nhl_player_game_log_url(
                    kwargs['player_id'],
                    kwargs.get('season', self.config.default_season),
                    kwargs.get('game_type', 2),
                )
            # ----------------------------------------------------------------
            # NHL + non-NHL team / season discovery
            # ----------------------------------------------------------------
            case 'teams':
                self._nhl_only('teams')
                source = kwargs.get('source', 'calendar')
                if source == 'franchise':
                    return build_nhl_franchise_url()
                if source == 'records':
                    return build_nhl_records_franchise_url()
                return build_nhl_schedule_calendar_url()  # 'calendar' (default)
            case 'teams_by_season':
                if self.league == 'nhl':
                    return build_teams_by_season_url(self.config, season)
                # Non-NHL: bootstrap carries team list for the season
                return build_bootstrap_url(
                    self.config,
                    game_id=None,
                    season=season,
                    page_name='scorebar',
                )
            case 'seasons':
                if self.league == 'nhl':
                    return build_nhl_seasons_url()
                return build_bootstrap_url(
                    self.config,
                    game_id=None,
                    season='latest',
                    page_name='scorebar',
                )
            # ----------------------------------------------------------------
            # NHL-only HTML reports
            # ----------------------------------------------------------------
            case 'html_pbp':
                self._nhl_only('html_pbp')
                return build_nhl_html_pbp_url(str(kwargs['game_id']))
            case 'shifts_home':
                self._nhl_only('shifts_home')
                return build_nhl_html_shifts_home_url(str(kwargs['game_id']))
            case 'shifts_away':
                self._nhl_only('shifts_away')
                return build_nhl_html_shifts_visitor_url(str(kwargs['game_id']))
            # ----------------------------------------------------------------
            # NHL-only JSON endpoints
            # ----------------------------------------------------------------
            case 'standings_by_date':
                self._nhl_only('standings_by_date')
                from datetime import datetime as _dt
                date = kwargs.get('date', _dt.now().strftime('%Y-%m-%d'))
                return build_nhl_standings_url(date)
            case 'team_stats':
                self._nhl_only('team_stats')
                return build_nhl_club_stats_url(
                    kwargs['team'],
                    kwargs.get('season', self.config.default_season),
                    kwargs.get('session', 2),
                )
            case 'draft':
                self._nhl_only('draft')
                return build_nhl_draft_picks_url(
                    kwargs.get('year', 2024),
                    kwargs.get('round', 1),
                )
            case 'draft_records':
                self._nhl_only('draft_records')
                return build_nhl_records_draft_url(kwargs.get('year', 2025))
            case 'team_draft_history':
                self._nhl_only('team_draft_history')
                return build_nhl_records_team_draft_history_url(kwargs.get('franchise', 1))
            case _:
                raise ValueError(
                    f"Unknown data_type '{data_type}'. "
                    "See _build_url docstring for supported values."
                )

    def raw_source(self, endpoint: str, **kwargs) -> dict:
        """Fetch the raw HTTP response for bronze-layer (source-of-truth) storage.

        Returns the unmodified wire payload from the source API, bypassing the
        cache and all parsing / transformation.  Store the result as-is in a
        bronze database; apply transformations in the silver layer later.

        Parameters:
        - endpoint: Any endpoint supported by _build_url — see its docstring for
          the full list: 'pbp', 'stats', 'schedule', 'roster', 'standings',
          'bootstrap', 'player_profile', 'player_game_log', 'teams',
          'teams_by_season', 'seasons', 'html_pbp', 'shifts' (returns home+away),
          'standings_by_date', 'team_stats', 'draft', 'draft_records',
          'team_draft_history'.  Pass 'shifts_home'/'shifts_away' to fetch a
          single HTML report instead of both.
        - **kwargs: Same keyword arguments as the corresponding data method.

        Returns:
        - dict with keys:
            url (str): Source URL (list[str] for 'shifts')
            raw_text (str): Unmodified wire body — JSON, JSONP, or HTML
            scraped_at (str): ISO-8601 UTC timestamp
            content_type (str): Content-Type response header
            status_code (int): HTTP status code
            league (str): League code
            endpoint (str): Endpoint name
          For 'shifts', returns a dict with 'home' and 'away' sub-records
          instead of a flat structure.

        Examples:
            # All leagues — PBP bronze record
            >>> rec = HockeyScraper('ahl').raw_source('pbp', game_id=1027781)
            >>> rec['raw_text']   # raw JSONP string, untouched

            # NHL JSON API
            >>> rec = HockeyScraper('nhl').raw_source('standings_by_date', date='2026-03-01')
            >>> rec = HockeyScraper('nhl').raw_source('draft', year=2024, round=1)
            >>> rec = HockeyScraper('nhl').raw_source('team_stats', team='MTL', season=20252026)

            # NHL HTML reports
            >>> rec = HockeyScraper('nhl').raw_source('html_pbp', game_id=2023020001)
            >>> shifts = HockeyScraper('nhl').raw_source('shifts', game_id=2023020001)
            >>> shifts['home']['raw_text']  # home HTML shift report
            >>> shifts['away']['raw_text']  # away HTML shift report
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()

        # 'shifts' is a special case: two separate HTML pages (home + away)
        if endpoint == 'shifts':
            self._nhl_only('shifts')
            home_url = build_nhl_html_shifts_home_url(str(kwargs['game_id']))
            away_url = build_nhl_html_shifts_visitor_url(str(kwargs['game_id']))
            if self.limiter:
                self.limiter.wait()
            home_resp = self.session.get(home_url, timeout=30)
            home_resp.raise_for_status()
            if self.limiter:
                self.limiter.wait()
            away_resp = self.session.get(away_url, timeout=30)
            away_resp.raise_for_status()
            return {
                "home": {
                    "url": home_url,
                    "raw_text": home_resp.text,
                    "scraped_at": now,
                    "content_type": home_resp.headers.get("Content-Type", ""),
                    "status_code": home_resp.status_code,
                },
                "away": {
                    "url": away_url,
                    "raw_text": away_resp.text,
                    "scraped_at": now,
                    "content_type": away_resp.headers.get("Content-Type", ""),
                    "status_code": away_resp.status_code,
                },
                "league": self.league,
                "endpoint": endpoint,
                "game_id": kwargs.get('game_id'),
                "scraped_at": now,
            }

        url = self._build_url(endpoint, **kwargs)

        if self.limiter:
            self.limiter.wait()

        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()

        return {
            "url": url,
            "raw_text": resp.text,
            "scraped_at": now,
            "content_type": resp.headers.get("Content-Type", ""),
            "status_code": resp.status_code,
            "league": self.league,
            "endpoint": endpoint,
        }

    def _format_hockeytech_schedule(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename raw HockeyTech schedule columns to consistent names."""
        column_map = {
            "prop.home_team_city.teamLink": "homeId",
            "prop.visiting_team_city.teamLink": "awayId",
            "prop.game_summary.gameLink": "gameId_",
            "row.game_id": "gameId",
            "row.date_with_day": "date",
            "row.home_goal_count": "homeScore",
            "row.visiting_goal_count": "awayScore",
            "row.attendance\t": "attendance",
            "row.game_status": "gameStatus",
            "row.home_team_city": "homeCity",
            "row.visiting_team_city": "awayCity",
            "row.venue_name": "venue",
        }
        df = df.rename(columns=column_map)
        cols_to_drop = [col for col in df.columns if col.startswith('prop.') or col.startswith('row.')]
        df = df.drop(columns=cols_to_drop)
        # Some leagues (e.g. QMJHL) lack row.game_id — promote gameId_ fallback
        if 'gameId' not in df.columns and 'gameId_' in df.columns:
            df = df.rename(columns={'gameId_': 'gameId'})
        elif 'gameId_' in df.columns:
            df = df.drop(columns=['gameId_'])
        return df
