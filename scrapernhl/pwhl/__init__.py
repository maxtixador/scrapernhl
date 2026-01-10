"""
PWHL (Professional Women's Hockey League) Data Scraper

Provides scraping functionality for PWHL games using the HockeyTech platform.
"""

from .scrapers.games import scrape_game, getAPIEvents

__all__ = ['scrape_game', 'getAPIEvents']
