"""Debug script to find data arrays in QMJHL responses"""

import sys
from pathlib import Path
import json

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from scrapernhl.qmjhl.api import fetch_api, QMJHLConfig

def explore_structure(obj, path="root"):
    """Recursively explore structure looking for 'data' arrays"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}"
            if key == "data" and isinstance(value, list):
                print(f"\n✓ Found 'data' array at: {new_path}")
                print(f"  Array length: {len(value)}")
                if len(value) > 0:
                    print(f"  First item keys: {list(value[0].keys())[:10]}")
                    print(f"  Sample item: {json.dumps(value[0], indent=2)[:300]}")
            else:
                explore_structure(value, new_path)
    elif isinstance(obj, list):
        if len(obj) > 0:
            explore_structure(obj[0], f"{path}[0]")

print("=" * 80)
print("Finding 'data' arrays in QMJHL API responses")
print("=" * 80)

# Schedule
print("\n1. Schedule Response Structure:")
schedule_response = fetch_api(
    feed='statviewfeed',
    view='schedule',
    season=211,
    team="-1",
    month="-1",
    location='homeaway'
)
explore_structure(schedule_response, "schedule")

# Player Stats
print("\n\n2. Player Stats Response Structure:")
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
explore_structure(player_stats_response, "player_stats")

# Roster
print("\n\n3. Roster Response Structure:")
roster_response = fetch_api(
    feed='statviewfeed',
    view='roster',
    team=52,
    season=211
)
explore_structure(roster_response, "roster")
