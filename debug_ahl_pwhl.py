"""Debug script to inspect AHL and PWHL API responses"""

import requests

# Test AHL
print("=" * 80)
print("AHL API Test")
print("=" * 80)

ahl_url = (
    "https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed"
    "&view=gameCenterPlayByPlay&game_id=1028297&key=ccb91f29d6744675"
    "&client_code=ahl&lang=en&league_id="
)

print(f"URL: {ahl_url}")
print()

try:
    response = requests.get(ahl_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Content Length: {len(response.text)}")
    print(f"\nFirst 500 chars of response:")
    print(response.text[:500])
    print()
    
    if response.text:
        print("Response is not empty, checking format...")
        if response.text.startswith('<!DOCTYPE') or response.text.startswith('<html'):
            print("⚠ Response is HTML, not JSON")
        elif 'angular.callbacks' in response.text:
            print("✓ Response is JSONP with angular.callbacks")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("PWHL API Test")
print("=" * 80)

pwhl_url = (
    "https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed"
    "&view=gameCenterPlayByPlay&game_id=210&key=446521baf8c38984"
    "&client_code=pwhl&lang=en&league_id="
)

print(f"URL: {pwhl_url}")
print()

try:
    response = requests.get(pwhl_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Content Length: {len(response.text)}")
    print(f"\nFirst 500 chars of response:")
    print(response.text[:500])
    print()
    
    if response.text:
        print("Response is not empty, checking format...")
        if response.text.startswith('<!DOCTYPE') or response.text.startswith('<html'):
            print("⚠ Response is HTML, not JSON")
        elif 'angular.callbacks' in response.text:
            print("✓ Response is JSONP with angular.callbacks")
except Exception as e:
    print(f"Error: {e}")
