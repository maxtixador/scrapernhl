# Contributing to ScraperNHL

First off, thank you for considering contributing to ScraperNHL! This project exists to serve the hockey analytics community, and contributions of all kinds are welcome.

## Ways to Contribute

- **Bug Reports**: Found a bug? Let us know!
- **Feature Requests**: Have an idea? Share it!
- **Code Contributions**: Fix bugs, add features, improve performance
- **Documentation**: Improve guides, fix typos, add examples
- **Examples**: Share notebooks, use cases, or tutorials
- **Testing**: Help expand test coverage

## Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/scrapernhl.git
   cd scrapernhl
   ```

2. **Create Virtual Environment**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Or using venv
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Development Dependencies**
   ```bash
   # Install package in editable mode with dev dependencies
   pip install -e ".[dev]"

   # Or with uv
   uv pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   # Test import
   python -c "from scrapernhl import scrapeTeams; print('✓ Installation successful')"

   # Run tests
   pytest tests/
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Your Changes

- Write clear, readable code
- Follow existing code style (we're considering Black/Ruff in the future)
- Add docstrings to new functions
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_modular.py -v

# Check test coverage
pytest tests/ --cov=scrapernhl --cov-report=term-missing

# Test CLI commands
scrapernhl teams --output test.csv
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: brief description of what changed"
```

Good commit message examples:
- `Add support for playoff statistics scraping`
- `Fix bug in schedule parsing for postponed games`
- `Update API documentation with new examples`
- `Refactor HTTP retry logic for better error handling`

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference any related issues (`Fixes #123`)
- Screenshots/examples if applicable

## Code Style Guidelines

### Python Code

- **Python Version**: 3.9+ (tested on 3.9-3.13)
- **Line Length**: ~100 characters (flexible)
- **Imports**: Group stdlib, third-party, local imports
- **Type Hints**: Encouraged but not required yet
- **Docstrings**: Use for all public functions

Example function:

```python
def scrapeTeams(source: str = "default", output_format: str = "pandas"):
    """
    Scrapes NHL team data and returns as DataFrame.

    Args:
        source: Data source. Options: "default", "calendar", "records"
        output_format: Output format. Options: "pandas", "polars"

    Returns:
        pd.DataFrame or pl.DataFrame: Team data with metadata

    Example:
        >>> teams = scrapeTeams()
        >>> teams_polars = scrapeTeams(output_format="polars")
    """
    # Implementation
```

### Documentation

- Use Markdown for all documentation files
- Keep line length reasonable (~80-100 chars)
- Use code blocks with language specification
- Add examples where helpful

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names

Example test:

```python
def test_scrape_teams_returns_dataframe():
    """Test that scrapeTeams returns a pandas DataFrame."""
    teams = scrapeTeams()
    assert isinstance(teams, pd.DataFrame)
    assert len(teams) > 0
    assert "teamName" in teams.columns
```

### Test Coverage

- Aim for high coverage of new code
- Test both success and failure cases
- Mock external API calls when appropriate

## Documentation Contributions

### Updating Documentation

Documentation lives in the `docs/` directory and uses MkDocs Material.

1. **Edit Markdown Files**
   ```bash
   # Edit files in docs/
   vim docs/getting-started.md
   ```

2. **Preview Locally**
   ```bash
   mkdocs serve
   # Open http://127.0.0.1:8000
   ```

3. **Build Documentation**
   ```bash
   mkdocs build
   ```

### Adding Examples

- Add Jupyter notebooks to `notebooks/` directory
- Include clear explanations and outputs
- Test notebooks before committing
- Reference notebooks in documentation

## Reporting Bugs

### Before Submitting

1. Check existing issues to avoid duplicates
2. Try the latest version from GitHub
3. Collect relevant information:
   - ScraperNHL version
   - Python version
   - Operating system
   - Steps to reproduce
   - Error messages/stack traces

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
1. Step 1
2. Step 2
3. See error

**Expected Behavior**
What should happen

**Environment**
- ScraperNHL version: 0.1.4
- Python version: 3.12.1
- OS: macOS 14.0

**Additional Context**
Error messages, screenshots, etc.
```

## Feature Requests

We love hearing new ideas! When requesting features:

1. **Check existing issues** to see if someone already suggested it
2. **Describe the use case** - What problem does it solve?
3. **Provide examples** - How would it work?
4. **Consider alternatives** - Are there other approaches?

## Questions?

- **Documentation**: https://maxtixador.github.io/scrapernhl/
- **Issues**: https://github.com/maxtixador/scrapernhl/issues
- **Email**: maxtixador@gmail.com
- **Twitter/X**: [@woumaxx](https://x.com/woumaxx)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Unacceptable Behavior

- Harassment, discrimination, or trolling
- Spam or off-topic content
- Publishing others' private information

## Recognition

Contributors will be:
- Listed in release notes
- Credited in documentation
- Part of the hockey analytics community!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ScraperNHL! Together we're building better tools for hockey analytics.
