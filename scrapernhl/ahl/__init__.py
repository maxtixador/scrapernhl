"""
AHL (American Hockey League) Data Scraper

Provides scraping functionality for AHL games using the HockeyTech platform.
"""

from .scrapers.games import scrape_game, getAPIEvents

__all__ = ['scrape_game', 'getAPIEvents']
