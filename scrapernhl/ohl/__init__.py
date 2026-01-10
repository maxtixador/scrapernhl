"""
OHL (Ontario Hockey League) Data Scraper

Provides scraping functionality for OHL games using the HockeyTech platform.
"""

from .scrapers.games import scrape_game, getAPIEvents

__all__ = ['scrape_game', 'getAPIEvents']
