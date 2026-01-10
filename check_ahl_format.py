"""Check AHL response format more carefully."""

import requests

url = "https://lscluster.hockeytech.com/feed/index.php"

# Test teams endpoint
params = {
    'feed': 'statviewfeed',
    'view': 'teamsForSeason',
    'key': 'ccb91f29d6744675',
    'client_code': 'ahl',
    'league_id': '4',
    'season': '76'
}

response = requests.get(url, params=params, timeout=30)
print(f"Status: {response.status_code}")
print(f"Length: {len(response.text)}")
print(f"First 300 chars:\n{response.text[:300]}")
print(f"\nStarts with '(': {response.text.startswith('(')}")
print(f"Starts with 'angular': {response.text.startswith('angular')}")
