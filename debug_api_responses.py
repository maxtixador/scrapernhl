"""Quick debug test for API responses."""

from scrapernhl.pwhl import api as pwhl_api
from scrapernhl.ahl import api as ahl_api
from scrapernhl.ohl import api as ohl_api

print("Testing PWHL (working):")
try:
    data = pwhl_api.get_scorebar(days_ahead=1)
    print(f"  Scorebar: {type(data)} - {len(str(data))} chars")
    
    data = pwhl_api.get_teams()
    print(f"  Teams: {type(data)} - {len(str(data))} chars")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting AHL:")
try:
    import requests
    import json
    
    url = "https://lscluster.hockeytech.com/feed/index.php"
    params = {
        'feed': 'modulekit',
        'view': 'scorebar',
        'key': 'ccb91f29d6744675',
        'client_code': 'ahl',
        'league_id': '4',
        'numberofdaysahead': 1,
        'numberofdaysback': 0
    }
    
    response = requests.get(url, params=params, timeout=30)
    print(f"  Status: {response.status_code}")
    print(f"  Response length: {len(response.text)}")
    print(f"  First 200 chars: {response.text[:200]}")
    
    # Try teams
    params2 = {
        'feed': 'statviewfeed',
        'view': 'teamsForSeason',
        'key': 'ccb91f29d6744675',
        'client_code': 'ahl',
        'league_id': '4',
        'season': '76'
    }
    response2 = requests.get(url, params=params2, timeout=30)
    print(f"\n  Teams status: {response2.status_code}")
    print(f"  Teams response length: {len(response2.text)}")
    print(f"  Teams first 200 chars: {response2.text[:200]}")
    
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting OHL:")
try:
    import requests
    
    url = "https://lscluster.hockeytech.com/feed/index.php"
    params = {
        'feed': 'modulekit',
        'view': 'scorebar',
        'key': '694cfeed58c932db',
        'client_code': 'ohl',
        'league_id': '2',
        'numberofdaysahead': 1,
        'numberofdaysback': 0
    }
    
    response = requests.get(url, params=params, timeout=30)
    print(f"  Status: {response.status_code}")
    print(f"  Response length: {len(response.text)}")
    print(f"  First 200 chars: {response.text[:200]}")
    
except Exception as e:
    print(f"  Error: {e}")
