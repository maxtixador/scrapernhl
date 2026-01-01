---
title: "Version 0.1.4 Released"
date: 2026-01-01
tags: ["announcement", "release"]
categories: ["announcements"]
draft: false
---

# ANNOUNCEMENT: Version 0.1.4 Released
*Date: January 1st, 2026*

I am delighted to announce the release of version 0.1.4 of the scraper package! This update brings several new features, improvements, and bug fixes that enhance the overall user experience.

Most importantly, this release marks a significant milestone with the introduction of a comprehensive documentation website. The new documentation provides detailed information on how to use the scraper, including tutorials, examples, and API references.

I worked extremely hard on this release, focusing on modularizing the codebase, standardizing the code style, and adding unit tests to ensure reliability. The monolithic 5000+ line scraper.py has been split into focused, single-responsibility modules organized by function (scrapers, core utilities, features, analysis). Additionally, I have integrated command-line interface (CLI) support, allowing users to run the scraper directly from the terminal.

I have also included new tutorials and examples to help users get started quickly and make the most of the scraper's capabilities. The new modular structure provides faster imports (~100ms vs 2-3s previously), better code organization, and maintains 100% backward compatibility with existing code.

Don't hesitate to give feedback or report any issues you encounter. Your input is invaluable in helping me improve the scraper further.

Finally, I encourage developers to contribute to the project. Whether it's through code contributions, documentation improvements, or feature suggestions, your involvement is greatly appreciated. Let's make this scraper the best it can be to encourage public research in hockey analytics!

## New Features

### Summary of New Features
- **Documentation**: There is finally a documentation website!
- **Modularization**: The codebase has been completely restructured from a single 5000+ line file into focused modules:
  - `scrapernhl.scrapers.*` - Individual data scrapers (teams, schedule, standings, roster, stats, draft, games)
  - `scrapernhl.core.*` - Core utilities (HTTP fetching with retry logic, helper functions)
  - `scrapernhl.config` - Centralized configuration and API endpoints
  - Original code (with minor improvements) safely backed up as `scraper_legacy.py`
  - **100% backward compatible** - all existing code works without changes
  - **Lazy loading** - heavy dependencies (xgboost) only load when needed
  - **Faster imports** - basic scrapers load in ~100ms (vs 2-3s previously)
- **Standardization**: Code style has been standardized across the project to improve readability and consistency.
- **Testing**: Comprehensive unit tests have been added (`tests/test_modular.py`) to ensure code reliability and facilitate future development.
- **CLI Integration**: You can now run the scraper directly from the command line interface (CLI) for easier access and faster execution.
- **Tutorials and Examples**: New tutorials and examples have been added to help users get started and make the most of the scraper's capabilities. 
- **Performance Improvements**: Optimizations have been made to improve the speed and efficiency of the scraper.

### 1. Documentation Website
The new documentation website provides comprehensive information on how to use the scraper, including tutorials, examples, and API references. It is designed to help users quickly get started and make the most of the scraper's capabilities. You can access the documentation [here](https://maxtixador.github.io/scrapernhl/).

### 2. Modular Codebase
The codebase has been restructured into focused modules, each responsible for a specific aspect of the scraper's functionality. This modular approach improves code organization, readability, and maintainability. The original monolithic code has been preserved in `scraper_legacy.py` for reference.
 
I have ensured that all existing code remains fully functional without any changes, maintaining 100% backward compatibility. Additionally, the modular structure allows for faster imports, with basic scrapers loading in approximately 100 milliseconds compared to 2-3 seconds previously.

### 3. Standardized Code Style
To enhance readability and consistency across the project, I have standardized the code style. This includes adhering to best practices and conventions, making it easier for developers to understand and contribute to the codebase. I don't use *black* or *flake8* yet, but I may consider it in future releases. Let me know if you have strong opinions on this!

### 4. Comprehensive Testing
I have added comprehensive unit tests in `tests/test_modular.py` to ensure the reliability of the codebase. These tests cover various aspects of the scraper's functionality and help identify potential issues early in the development process. The testing framework facilitates future development and ensures that new features do not introduce regressions.

Testing has always been a weak point of mine, so I am particularly proud of this addition! I think there are still some edge cases that need to be covered, so please report any bugs you find. I could also use help writing more tests if anyone is interested.

### 5. CLI Integration
The scraper can now be run directly from the command line interface (CLI), providing users with easier access and faster execution. This feature allows users to quickly scrape data without needing to write additional code.

The CLI supports all major scraping functions with flexible output formats (CSV, JSON, Parquet, Excel):

```bash
# Get help
python scrapernhl/cli.py --help

# Scrape all NHL teams
python scrapernhl/cli.py teams --output nhl_teams.csv

# Scrape team schedule
python scrapernhl/cli.py schedule MTL 20252026 --output mtl_schedule.json --format json

# Scrape current standings
python scrapernhl/cli.py standings

# Scrape team roster
python scrapernhl/cli.py roster TOR 20252026

# Scrape player stats (add --goalies for goalie stats)
python scrapernhl/cli.py stats MTL 20252026 --output mtl_skaters.csv

# Scrape game play-by-play (add --with-xg for expected goals)
python scrapernhl/cli.py game 2024020001 --with-xg

# Scrape draft data
python scrapernhl/cli.py draft 2024 1  # First round only
python scrapernhl/cli.py draft 2024 all  # All rounds
```

The CLI makes it easy to integrate NHL data scraping into shell scripts, cron jobs, or automated workflows without writing any Python code.

### 6. Tutorials and Examples
To help users get started and make the most of the scraper's capabilities, I have added new tutorials and examples. These resources cover various use cases and demonstrate how to effectively utilize the scraper for hockey analytics. You can find the examples in the `docs/examples` directory of the documentation website.

For now, there are no exemples for data visualization, but I plan to add some in the future!


## Future Plans
Looking ahead, we plan to continue enhancing the scraper with additional features and improvements. Future updates may include:
- **Arena Adjusted Event Coordinates**: Implementing arena-adjusted event coordinates for more accurate data representation.
- **Data Visualization Tools**: Adding tools for visualizing scraped data to facilitate analysis and insights.
- **Manual Data Input**: Enabling users to manually input data for scenarios where automated scraping may not be feasible.
- **Docker Support**: Introducing Docker support for easier deployment and environment management.
- **Database Integration**: Scraping data all the time can be resource-intensive. I will explore creating a database people can connect to instead of scraping on their own machines.
- **New Leagues**: Expanding support to include additional hockey leagues (looking closely at the PWHL) beyond the NHL.
- **`Dev module`**: A new development module to streamline the development process and enhance collaboration. Same ScraperNHL functions, but with additional logging and error handling for debugging purposes and extra features (runtime, caching, messages) for extended development.
- **Improved Error Handling**: Enhanced error handling mechanisms to provide more informative feedback and improve user experience.
- **More Examples and Tutorials**: Continuing to add more examples and tutorials to help users get the most out of the scraper. *I don't think I will wait for another major release to add these!*

*By [Max](https://x.com/woumaxx), your favorite hockey analytics enthusiast*