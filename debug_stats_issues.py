"""Debug goalie stats and team stats issues"""

import sys
from pathlib import Path
import json

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from scrapernhl.qmjhl.api import fetch_api, QMJHLConfig

print("=" * 80)
print("Investigating goalie stats and team stats")
print("=" * 80)

print("\n1. Goalie Stats API Response:")
try:
    goalie_response = fetch_api(
        feed='statviewfeed',
        view='goalies',
        season=211,
        sort='saves',
        statsType='standard',
        first=0,
        limit=10,
        qualified='qualified',
        site_id=QMJHLConfig.SITE_ID
    )
    print("Success!")
    print(json.dumps(goalie_response, indent=2)[:1500])
except Exception as e:
    print(f"Error: {e}")

print("\n\n2. Team Stats API Response:")
try:
    team_stats_response = fetch_api(
        feed='statviewfeed',
        view='teams',
        season=211,
        statsType='standard',
        context='overall'
    )
    print("Success!")
    print(json.dumps(team_stats_response, indent=2)[:1500])
except Exception as e:
    print(f"Error: {e}")
