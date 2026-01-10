"""Debug script to inspect QMJHL API response structure"""

import sys
from pathlib import Path
import json

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from scrapernhl.qmjhl.scrapers.schedule_new import getScheduleData
from scrapernhl.qmjhl.scrapers.standings import getStandingsData
from scrapernhl.qmjhl.scrapers.stats import getPlayerStatsData, getTeamStatsData
from scrapernhl.qmjhl.scrapers.roster import getRosterData

print("=" * 80)
print("Inspecting QMJHL API responses")
print("=" * 80)

print("\n1. Schedule Data:")
schedule = getScheduleData(season=211, team_id=-1, month=-1)
print(json.dumps(schedule[0] if schedule else {}, indent=2)[:500])

print("\n2. Standings Data:")
standings = getStandingsData(season=211)
print(json.dumps(standings[0] if standings else {}, indent=2)[:500])

print("\n3. Player Stats Data:")
player_stats = getPlayerStatsData(season=211, player_type='skater', limit=5)
print(json.dumps(player_stats[0] if player_stats else {}, indent=2)[:500])

print("\n4. Team Stats Data:")
team_stats = getTeamStatsData(season=211)
print(json.dumps(team_stats[0] if team_stats else {}, indent=2)[:500])

print("\n5. Roster Data:")
roster = getRosterData(team_id=52, season=211)
print(json.dumps(roster[0] if roster else {}, indent=2)[:500])
