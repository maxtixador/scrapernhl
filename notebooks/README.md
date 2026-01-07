# NHL Scraper Notebooks

Interactive Jupyter notebooks demonstrating the `scrapernhl` package functionality.

## Notebooks

### 1. [Basic Scraping](01_basic_scraping.ipynb)
Introduction to scraping NHL data:
- Teams, schedules, standings
- Rosters and player statistics
- Play-by-play data
- Draft information
- Using Polars vs Pandas
- Backward compatibility

### 2. [Advanced Analytics](02_advanced_analytics.ipynb)
Advanced features and analytics:
- Expected Goals (xG) calculation
- Time on Ice (TOI) analysis
- Player combinations (lines, pairs)
- On-ice statistics (Corsi, xG differential)
- Team-level aggregates
- Multi-game season analysis
- Phase 4: Advanced analytics and visualization
- Shot metrics and scoring chances
- Comprehensive analytics reports

### 3. [Data Export](03_data_export.ipynb)
Exporting data to various formats:
- CSV, Excel, JSON
- Parquet (compressed)
- SQLite database
- Incremental/append mode
- Custom formatting
- Using Polars for fast exports

### 4. [Comprehensive Testing](04_comprehensive_testing.ipynb)
Complete testing of all Phase 1-4 features:
- Phase 1: Error handling, logging, validation
- Phase 2: Progress bars, caching, styled console output
- Phase 3: Player stats, batch scraping, parallel processing
- Phase 4: Advanced analytics and visualization
- Full workflow examples with all features

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/maxtixador/scrapernhl.git
cd nhl_scraper

# Install in development mode
pip install -e .

# Install Jupyter (if not already installed)
pip install jupyter

# Optional: Install additional dependencies for advanced features
pip install xgboost openpyxl
```

### Running the Notebooks

```bash
# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

Then navigate to the `notebooks/` directory and open any notebook.

## Requirements

**Basic scraping (notebooks 1 & 3):**
- pandas or polars
- requests
- selectolax or beautifulsoup4

**Advanced analytics (notebook 2):**
- All basic requirements
- xgboost (for expected goals)
- numpy

**Export examples:**
- openpyxl (for Excel export)
- pyarrow or fastparquet (for Parquet export)

## Testing Examples

These notebooks serve dual purposes:
1. **Documentation**: Learn how to use the package
2. **Testing**: Verify that all features work correctly

Run all cells in each notebook to confirm:
- All imports work
- All scrapers return data
- All export methods succeed
- Advanced analytics calculate correctly

## Modular Structure

All notebooks use the new modular structure introduced in v0.1.4:

```python
# New modular imports (recommended)
from scrapernhl.scrapers.teams import scrapeTeams
from scrapernhl.scrapers.games import scrapePlays
from scrapernhl import scrape_game, engineer_xg_features

# Old style still works (backward compatible)
from scrapernhl import scrapeTeams, scrapePlays
```

## See Also

- [Documentation](../docs/) - Full documentation
- [API Reference](../docs/api.md) - Complete function reference
- [Examples](../docs/examples/) - Code examples in markdown
- [Getting Started](../docs/getting-started.md) - Quick start guide

## Contributing

Found an issue or want to add an example? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Add your notebook or improvements
4. Submit a pull request

## License

See [LICENSE](../docs/LICENSE) for details.
