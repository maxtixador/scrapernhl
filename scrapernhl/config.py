# scrapernhl/config.py
"""All league configurations and constants."""

import logging
import os
from dataclasses import dataclass
from typing import Literal

_LOG = logging.getLogger(__name__)


def _api_key(env_var: str, default: str) -> str:
    """Return the value of *env_var* if set, otherwise *default*.

    Logs a warning when falling back to the hardcoded default so operators
    know to set the environment variable in production.
    """
    value = os.environ.get(env_var)
    if value is None:
        _LOG.debug(
            "Environment variable %s not set; using bundled default key. "
            "Set %s to suppress this message.",
            env_var,
            env_var,
        )
        return default
    return value


LeagueType = Literal['nhl', 'ahl', 'ohl', 'whl', 'qmjhl', 'pwhl']


@dataclass
class LeagueConfig:
    """Configuration for a single league."""

    name: str
    client_code: str | None
    api_key: str | None
    league_id: int | None
    site_id: int | None
    default_season: int
    base_url: str
    pbp_style: Literal['nhl', 'hockeytech_a', 'hockeytech_b']
    canvas_size: tuple[int, int]
    rate_limit_calls: int = 2
    rate_limit_period: float = 1.0
    # Length of a single OT period in seconds for the *current* regular-season
    # format.  Playoff OT is always 20-min (1200 s) full periods.
    ot_period_length: int = 1200
    # Historical OT length changes: ordered list of (first_season_id, ot_secs).
    # The entry with the highest first_season_id that is still <= the queried
    # season_id wins.  An empty tuple means ot_period_length applies for all
    # seasons in the API data range.
    ot_period_length_history: tuple[tuple[int, int], ...] = ()


def get_ot_period_length(
    config: 'LeagueConfig',
    season_id: int | None = None,
    is_playoff: bool = False,
) -> int:
    """Return the OT period length in seconds for a given season.

    Playoff OT is always 1200 s (20-min full periods, sudden death) for all
    leagues regardless of the regular-season format.

    If *season_id* is None, or the league has no recorded history, the current
    ``ot_period_length`` value is returned.
    """
    if is_playoff:
        return 1200

    if season_id is None or not config.ot_period_length_history:
        return config.ot_period_length

    # Walk history sorted descending; return the ot_seconds for the highest
    # first_season_id that does not exceed the queried season_id.
    best = config.ot_period_length  # fallback if season predates all records
    for first_season, ot_secs in sorted(
        config.ot_period_length_history, reverse=True
    ):
        if season_id >= first_season:
            best = ot_secs
            break

    return best


# League configurations
LEAGUES: dict[LeagueType, LeagueConfig] = {
    'nhl': LeagueConfig(
        name='NHL',
        client_code=None,
        api_key=None,
        league_id=None,
        site_id=None,
        default_season=20252026,
        base_url='https://api-web.nhle.com',
        pbp_style='nhl',
        canvas_size=(200, 85),  # Already in feet
        rate_limit_calls=100,  # Generous for public API
    ),
    'ahl': LeagueConfig(
        name='AHL',
        client_code='ahl',
        api_key=_api_key('SCRAPERNHL_AHL_API_KEY', 'ccb91f29d6744675'),
        league_id=4,
        site_id=3,
        default_season=90,
        base_url='https://lscluster.hockeytech.com/feed/index.php',
        pbp_style='hockeytech_a',
        canvas_size=(850, 400),
        ot_period_length=300,   # 5-min 3-on-3 OT (regular season)
    ),
    'pwhl': LeagueConfig(
        name='PWHL',
        client_code='pwhl',
        api_key=_api_key('SCRAPERNHL_PWHL_API_KEY', '446521baf8c38984'),
        league_id=1,
        site_id=0,
        default_season=8,
        base_url='https://lscluster.hockeytech.com/feed/index.php',
        pbp_style='hockeytech_a',
        canvas_size=(850, 400),
        ot_period_length=600,   # 10-min 3v3 OT (regular season; unique to PWHL)
    ),
    'ohl': LeagueConfig(
        name='OHL',
        client_code='ohl',
        api_key=_api_key('SCRAPERNHL_OHL_API_KEY', 'f1aa699db3d81487'),
        league_id=1,
        site_id=1,
        default_season=83,
        base_url='https://lscluster.hockeytech.com/feed/index.php',
        pbp_style='hockeytech_b',
        canvas_size=(600, 300),
        ot_period_length=300,   # 5-min 4-on-4 OT (regular season)
    ),
    'whl': LeagueConfig(
        name='WHL',
        client_code='whl',
        api_key=_api_key('SCRAPERNHL_WHL_API_KEY', 'f1aa699db3d81487'),
        league_id=7,
        site_id=0,
        default_season=289,
        base_url='https://lscluster.hockeytech.com/feed/index.php',
        pbp_style='hockeytech_b',
        canvas_size=(600, 300),
        ot_period_length=300,   # 5-min 3-on-3 OT (regular season)
        # TODO: WHL used 10-min OT before ~2019; exact first season_id for
        # the 5-min change is unverified.  Add entry like (266, 300) once
        # the cutoff season is confirmed.
    ),
    'qmjhl': LeagueConfig(
        name='QMJHL',
        client_code='lhjmq',
        api_key=_api_key('SCRAPERNHL_QMJHL_API_KEY', 'f322673b6bcae299'),
        league_id=6,
        site_id=0,
        default_season=211,
        base_url='https://cluster.leaguestat.com/feed/index.php',
        pbp_style='hockeytech_b',
        canvas_size=(600, 300),
        ot_period_length=300,   # 5-min 3-on-3 OT (regular season)
        # TODO: QMJHL used 10-min OT before ~2019; exact first season_id for
        # the 5-min change is unverified.  Add entry like (190, 300) once
        # the cutoff season is confirmed.
    ),
}

# Cache TTLs (seconds)
CACHE_TTL = {
    'pbp': 0,           # No cache for live data
    'schedule': 3600,   # 1 hour
    'roster': 86400,    # 24 hours
    'player': 86400,    # 24 hours
    'stats': 3600,      # 1 hour
    'standings': 1800,  # 30 minutes
}

month_mapping = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12',
}

# Mapping for month for if it is at the seasonStartYear or seasonEndYear
month_start_end_mapping = {
    "seasonStartYear": {
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    },
    "seasonEndYear": {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
    }
}
