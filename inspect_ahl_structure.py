"""Inspect AHL/PWHL data structure"""

import json
import requests

# Get AHL data
ahl_url = (
    "https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed"
    "&view=gameCenterPlayByPlay&game_id=1028297&key=ccb91f29d6744675"
    "&client_code=ahl&lang=en&league_id="
)

response = requests.get(ahl_url, timeout=10)
content = response.text

# Remove wrapping parentheses
if content.startswith('(['):
    content = content[1:-1]

data = json.loads(content)

print("=" * 80)
print("AHL Data Structure")
print("=" * 80)
print(f"Type: {type(data)}")
print(f"Length: {len(data)}")
print(f"\nFirst event:")
print(json.dumps(data[0], indent=2))
print(f"\nSecond event (if different):")
print(json.dumps(data[1], indent=2))

# Check if there's a shot or goal event
for i, event in enumerate(data[:50]):
    if event.get('event') in ['shot', 'goal']:
        print(f"\nEvent {i} - {event.get('event').upper()}:")
        print(json.dumps(event, indent=2))
        break
