# AI Development Guidelines for ScraperNHL

This document contains instructions for AI assistants working on the ScraperNHL project.

## General Principles

### Communication Style
- **NO EMOJIS** unless explicitly requested by the user
- Use clear, professional, technical language
- Be concise but thorough
- Focus on facts and implementation details

### Documentation
- All internal development summaries and session notes must be stored in `.ai/summaries/`
- Public-facing documentation goes in `docs/` or root-level MD files
- Keep internal technical discussions separate from user documentation

### Code Standards
- Follow PEP 8 for Python code
- Use Google-style docstrings
- Type hints are required for all functions
- Maximum line length: 100 characters

### Project Structure
- **Generic/Shared Code**: `scrapernhl/core/`, `scrapernhl/exceptions.py`, `scrapernhl/visualization.py`
- **League-Specific Code**: `scrapernhl/nhl/`, `scrapernhl/ohl/` (future), etc.
- **Tests**: `tests/` directory
- **Examples**: `examples/` directory
- **Documentation**: `docs/` for public docs, `.ai/` for internal AI docs

## Multi-League Architecture

The package is organized to support multiple hockey leagues:

```
scrapernhl/
├── core/              # Shared utilities (logging, caching, HTTP, etc.)
├── nhl/               # NHL-specific scrapers and analytics
├── ohl/               # OHL-specific (future)
├── whl/               # WHL-specific (future)
├── qmjhl/             # QMJHL-specific (future)
└── pwhl/              # PWHL-specific (future)
```

### Adding New Leagues
1. Create `scrapernhl/{league}/` directory
2. Implement scrapers in `scrapernhl/{league}/scrapers/`
3. Reuse utilities from `scrapernhl/core/`
4. Add league-specific analytics if needed
5. Export functions from `scrapernhl/{league}/__init__.py`

## Backward Compatibility

**CRITICAL**: All changes must maintain backward compatibility.
- Existing imports must continue to work
- Main package (`scrapernhl/__init__.py`) re-exports from league modules
- Users should not need to change their code

## Testing Requirements

- All new features require tests in `tests/`
- Run test suite before committing: `python tests/test_reorganization.py`
- Minimum 80% code coverage for new modules
- Test both pandas and polars DataFrame support

## Documentation Updates

When adding features:
1. Update API reference in `docs/api.md`
2. Add examples to `docs/examples/`
3. Update relevant phase summaries (PHASE2_SUMMARY.md, etc.)
4. Add internal notes to `.ai/summaries/` (not public)

## File Organization Rules

### Public Documentation (Visible to Users)
- `README.md` - Project overview and quick start
- `docs/` - Full documentation site
- `PHASE*.md` - Feature implementation summaries
- `IMPLEMENTATION_COMPLETE.md` - Overall project status

### Internal Documentation (Hidden from Users)
- `.ai/GUIDELINES.md` - This file (AI instructions)
- `.ai/summaries/` - Development session notes and internal summaries
- `.ai/decisions/` - Architectural decisions and rationales

## Commit Message Format

Use conventional commits:
```
feat: add OHL team scraper
fix: resolve caching issue in schedule scraper
docs: update API reference for analytics module
refactor: reorganize NHL scrapers into subdirectory
test: add tests for batch processing
```

## Common Tasks

### Adding a New Scraper Function
1. Create in appropriate league module (e.g., `scrapernhl/nhl/scrapers/`)
2. Use `@cached` decorator if data doesn't change frequently
3. Add error handling with proper exceptions
4. Support both pandas and polars output
5. Add docstring with examples
6. Export from `__init__.py`
7. Add tests

### Modifying Core Utilities
1. Ensure changes are league-agnostic
2. Update all affected league modules
3. Run full test suite
4. Update documentation

### Creating Analytics Functions
1. Place in league-specific analytics module
2. Support both pandas and polars DataFrames
3. Return standardized output format
4. Add visualization companion function if applicable
5. Document metrics and formulas

## Package Management

### Python Environment
**ALWAYS use `.venv` as the virtual environment** (not `nhl_env` or any other name).

The project uses `.venv` which is already configured and tracked by `uv`. To activate:
```bash
source .venv/bin/activate
```

### Use `uv` for Package Operations
**ALWAYS use `uv` instead of `pip` for all package management operations.**

`uv` is an extremely fast Python package installer and resolver written in Rust. It's already configured for this project.

#### Common Commands:
```bash
# Activate the virtual environment first
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .

# Install with specific groups
uv pip install -e ".[dev]"
uv pip install -e ".[test]"

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Sync dependencies from lock file
uv sync

# Update dependencies
uv lock --upgrade

# Install specific package version
uv pip install package-name==1.2.3
```

#### Why uv?
- **10-100x faster** than pip for package installation
- Better dependency resolution
- Compatible with pip (uses same package index)
- Creates reproducible environments with `uv.lock`
- Drop-in replacement for pip commands
- Automatically uses `.venv` when present

#### When Reinstalling the Package:
After making changes to the code, simply run:
```bash
source .venv/bin/activate
uv pip install -e .
```

Note: `uv` is smart enough to detect changes without `--force-reinstall`

## Dependencies

### Core Dependencies
- pandas >= 2.0.0
- polars >= 0.20.0
- requests >= 2.31.0
- rich >= 13.0.0

### Optional Dependencies
- xgboost >= 2.0.0 (for xG models)
- jupyterlab >= 4.0.0 (for notebooks)
- beautifulsoup4 >= 4.12.0 (for HTML parsing)

## Performance Considerations

- Use caching liberally (`@cached` decorator)
- Implement rate limiting for API calls
- Support parallel processing with `BatchScraper`
- Lazy load heavy dependencies
- Profile slow operations

## Security

- Never commit API keys or tokens
- Validate all user inputs
- Sanitize data from external sources
- Use secure HTTPS connections
- Follow NHL API terms of service

## Error Handling

Use the exception hierarchy:
- `ScraperNHLError` - Base exception
- `APIError` - API-related errors
- `RateLimitError` - Rate limiting errors
- `DataValidationError` - Data quality errors
- `CacheError` - Caching errors
- `ParsingError` - HTML/JSON parsing errors

## Logging

- Use `get_logger(__name__)` from `scrapernhl.core.logging_config`
- Log levels: DEBUG (development), INFO (user actions), WARNING (recoverable issues), ERROR (failures)
- No sensitive data in logs

## Progress Indication

- Use `create_progress_bar()` for long operations
- Use `console.print_info/success/warning/error()` for status messages
- Show ETA and percentage for batch operations

## Release Process

1. Update version in `pyproject.toml` and `__init__.py`
2. Run full test suite
3. Update CHANGELOG.md
4. Update documentation
5. Create git tag
6. Build package: `python -m build`
7. Publish to PyPI: `python -m twine upload dist/*`

## Getting Help

- Check existing phase summaries for implementation patterns
- Review test files for usage examples
- Read core module docstrings for utility functions
- Consult `.ai/summaries/` for development history

---

**Remember**: No emojis, clear documentation, maintain backward compatibility, and keep internal docs in `.ai/`.
