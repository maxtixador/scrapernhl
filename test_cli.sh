#!/bin/bash
# CLI Test Script for ScraperNHL Multi-League Support
# Tests all league commands to verify functionality

set -e  # Exit on error

echo "=== Testing ScraperNHL CLI Multi-League Support ==="
echo ""

# Activate virtual environment
source .venv/bin/activate

# Test NHL commands (existing functionality)
echo "1. Testing NHL teams..."
python -m scrapernhl.cli teams --output /tmp/test_nhl_teams.csv
echo "   ✓ NHL teams working"
echo ""

# Test PWHL commands
echo "2. Testing PWHL commands..."
python -m scrapernhl.cli pwhl teams --output /tmp/test_pwhl_teams.csv
python -m scrapernhl.cli pwhl schedule --output /tmp/test_pwhl_schedule.csv
python -m scrapernhl.cli pwhl standings --output /tmp/test_pwhl_standings.csv
python -m scrapernhl.cli pwhl stats --player-type skater --limit 10 --output /tmp/test_pwhl_stats.csv
echo "   ✓ PWHL commands working"
echo ""

# Test AHL commands
echo "3. Testing AHL commands..."
python -m scrapernhl.cli ahl teams --output /tmp/test_ahl_teams.csv
python -m scrapernhl.cli ahl schedule --team-id 1 --output /tmp/test_ahl_schedule.csv
python -m scrapernhl.cli ahl standings --output /tmp/test_ahl_standings.csv
python -m scrapernhl.cli ahl stats --player-type goalie --limit 10 --output /tmp/test_ahl_goalies.csv
echo "   ✓ AHL commands working"
echo ""

# Test OHL commands
echo "4. Testing OHL commands..."
python -m scrapernhl.cli ohl teams --output /tmp/test_ohl_teams.csv
python -m scrapernhl.cli ohl schedule --team-id 2 --output /tmp/test_ohl_schedule.csv
python -m scrapernhl.cli ohl standings --output /tmp/test_ohl_standings.csv
echo "   ✓ OHL commands working"
echo ""

# Test WHL commands
echo "5. Testing WHL commands..."
python -m scrapernhl.cli whl teams --output /tmp/test_whl_teams.csv
python -m scrapernhl.cli whl standings --output /tmp/test_whl_standings.json --format json
python -m scrapernhl.cli whl stats --player-type skater --limit 10 --output /tmp/test_whl_stats.csv
echo "   ✓ WHL commands working"
echo ""

# Test QMJHL commands
echo "6. Testing QMJHL commands..."
python -m scrapernhl.cli qmjhl teams --output /tmp/test_qmjhl_teams.csv
python -m scrapernhl.cli qmjhl schedule --team-id 3 --output /tmp/test_qmjql_schedule.csv
python -m scrapernhl.cli qmjhl stats --player-type skater --limit 10 --output /tmp/test_qmjhl_stats.csv
echo "   ✓ QMJHL commands working"
echo ""

# Test different output formats
echo "7. Testing output formats..."
python -m scrapernhl.cli pwhl teams --output /tmp/test_format.csv --format csv
python -m scrapernhl.cli pwhl teams --output /tmp/test_format.json --format json
python -m scrapernhl.cli pwhl teams --output /tmp/test_format.parquet --format parquet
echo "   ✓ CSV, JSON, and Parquet formats working"
echo ""

# Verify files were created
echo "8. Verifying output files..."
test -f /tmp/test_nhl_teams.csv && echo "   ✓ NHL teams file created"
test -f /tmp/test_pwhl_teams.csv && echo "   ✓ PWHL teams file created"
test -f /tmp/test_ahl_teams.csv && echo "   ✓ AHL teams file created"
test -f /tmp/test_ohl_teams.csv && echo "   ✓ OHL teams file created"
test -f /tmp/test_whl_teams.csv && echo "   ✓ WHL teams file created"
test -f /tmp/test_qmjhl_teams.csv && echo "   ✓ QMJHL teams file created"
test -f /tmp/test_format.parquet && echo "   ✓ Parquet format file created"
echo ""

echo "=== All CLI tests passed! ==="
echo ""
echo "Supported leagues:"
echo "  - NHL (National Hockey League)"
echo "  - PWHL (Professional Women's Hockey League)"
echo "  - AHL (American Hockey League)"
echo "  - OHL (Ontario Hockey League)"
echo "  - WHL (Western Hockey League)"
echo "  - QMJHL (Quebec Maritimes Junior Hockey League)"
echo ""
echo "Available commands per league:"
echo "  - teams: Scrape all teams"
echo "  - schedule: Scrape game schedule"
echo "  - standings: Scrape league standings"
echo "  - stats: Scrape player statistics"
echo "  - roster: Scrape team rosters"
echo "  - game: Scrape play-by-play data"
echo ""
echo "Supported output formats: csv, json, parquet, excel"
