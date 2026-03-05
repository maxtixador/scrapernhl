"""ScraperNHL - Unified hockey data scraper."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("scrapernhl")
except PackageNotFoundError:
    __version__ = "unknown"

from .client import HockeyScraper
from .config import LeagueType
from .transform import tracking_dict_to_df

__all__ = ['scrape', 'HockeyScraper', 'tracking_dict_to_df']


# Functional API (DeepSeek style)
def scrape(league: LeagueType, data_type: str = 'pbp', **kwargs):
    """
    Simple functional interface.

    Examples:
        >>> scrape('qmjhl', 'pbp', game_id=31171)
        >>> scrape('ahl', 'stats', season=90, position='skaters')
        >>> scrape('ohl', 'teams', season=83)
        >>> scrape('nhl', 'teams_by_season', season=20242025)
        >>> scrape('pwhl', 'seasons')
    """
    scraper = HockeyScraper(league)

    methods = {
        'pbp': scraper.play_by_play,
        'stats': scraper.player_stats,
        'schedule': scraper.schedule,
        'roster': scraper.roster,
        'standings': scraper.standings,
        'teams': scraper.scrape_teams if league.lower() == 'nhl' else scraper.teams_by_season,
        'teams_by_season': scraper.teams_by_season,
        'scrape_teams': scraper.scrape_teams,
        'seasons': scraper.seasons,
    }

    if data_type not in methods:
        raise ValueError(f"Invalid data_type: {data_type}")

    return methods[data_type](**kwargs)
