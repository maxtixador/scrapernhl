"""Debug script to inspect full QMJHL API response structure"""

import sys
from pathlib import Path
import json

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from scrapernhl.qmjhl.api import fetch_api, QMJHLConfig

print("=" * 80)
print("Inspecting Full QMJHL API Responses")
print("=" * 80)

# Schedule
print("\n1. Schedule API Response (first 1000 chars):")
schedule_response = fetch_api(
    feed='statviewfeed',
    view='schedule',
    season=211,
    team="-1",
    month="-1",
    location='homeaway'
)
print(json.dumps(schedule_response, indent=2)[:1000])

# Roster
print("\n\n2. Roster API Response (first 1000 chars):")
roster_response = fetch_api(
    feed='statviewfeed',
    view='roster',
    team=52,
    season=211
)
print(json.dumps(roster_response, indent=2)[:1000])

# Player Stats
print("\n\n3. Player Stats API Response (first 1000 chars):")
player_stats_response = fetch_api(
    feed='statviewfeed',
    view='players',
    season=211,
    sort='points',
    statsType='standard',
    first=0,
    limit=5,
    qualified='qualified',
    site_id=QMJHLConfig.SITE_ID
)
print(json.dumps(player_stats_response, indent=2)[:1000])
