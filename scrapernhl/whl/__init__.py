"""
WHL (Western Hockey League) Data Scraper

Provides scraping functionality for WHL games using the HockeyTech platform.
"""

from .scrapers.games import scrape_game, getAPIEvents

__all__ = ['scrape_game', 'getAPIEvents']
