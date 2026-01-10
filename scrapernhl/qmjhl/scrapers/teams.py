import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

def getTeams(season_id, url=None, max_retries=2):
    """
    Scrape team information for any season, adapting to different team structures.
    
    Parameters:
    -----------
    season_id : int
        The season ID to scrape
    url : str, optional
        Specific URL to scrape (auto-generated if None)
    max_retries : int
        Number of retry attempts
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with team data for the season
    """
    
    # Generate URL if not provided
    if url is None:
        # Try multiple possible URL patterns
        url_patterns = [
            f"https://chl.ca/lhjmq/en/schedule/all/{season_id}/",
            f"https://chl.ca/lhjmq/en/schedule/{season_id}/",
            f"https://chl.ca/lhjmq/en/schedule/16/{season_id}/"  # Using a team page as fallback
        ]
    else:
        url_patterns = [url]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    for attempt in range(max_retries):
        for url_to_try in url_patterns:
            try:
                # print(f"Attempt {attempt+1}: Trying {url_to_try}")
                response = requests.get(url_to_try, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Method 1: Look for teams dropdown
                teams_data = extract_teams_from_dropdown(soup, season_id)
                
                # Method 2: If no dropdown, try to extract from schedule table
                if teams_data.empty:
                    teams_data = extract_teams_from_schedule(soup, season_id)
                
                # Method 3: Try API approach as fallback
                if teams_data.empty:
                    teams_data = get_teams_via_api(season_id)
                
                if not teams_data.empty:
                    # print(f"✓ Found {len(teams_data)} teams for season {season_id}")
                    return teams_data
                    
                time.sleep(1)  # Brief delay between attempts
                
            except Exception as e:
                print(f"  Error with {url_to_try}: {e}")
                continue
    
    print(f"✗ Could not scrape teams for season {season_id}")
    return pd.DataFrame(columns=['season_id', 'team_id', 'team_label', 'city', 'nickname', 'url'])

def extract_teams_from_dropdown(soup, season_id):
    """Extract teams from dropdown menu"""
    teams_data = []
    
    # Look for any select element that might contain teams
    select_elements = soup.find_all('select')
    
    for select in select_elements:
        options = select.find_all('option')
        
        # Check if this looks like a teams dropdown (has URLs with team IDs)
        team_options = []
        for option in options:
            value = option.get('value', '')
            text = option.get_text(strip=True)
            
            if value and text and 'All Teams' not in text:
                # Look for team ID in URL pattern
                patterns = [
                    rf'/schedule/(\d+)/{season_id}/',
                    rf'/{season_id}/(\d+)/',
                    rf'/(\d+)/{season_id}/'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, value)
                    if match:
                        team_id = int(match.group(1))
                        team_options.append({
                            'team_id': team_id,
                            'team_label': text,
                            'url': value
                        })
                        break
        
        if team_options:
            # Parse city and nickname
            for team in team_options:
                label = team['team_label']
                city = nickname = None
                
                if ',' in label:
                    parts = [p.strip() for p in label.split(',', 1)]
                    city = parts[0]
                    nickname = parts[1] if len(parts) > 1 else label
                else:
                    city = label
                    nickname = label
                
                teams_data.append({
                    'season_id': season_id,
                    'team_id': team['team_id'],
                    'team_label': label,
                    'city': city,
                    'nickname': nickname,
                    'url': team['url']
                })
            
            break  # Found teams dropdown, stop looking
    
    return pd.DataFrame(teams_data)

def extract_teams_from_schedule(soup, season_id):
    """Extract teams from schedule table if dropdown not available"""
    teams_data = []
    teams_found = set()
    
    # Look for team names in schedule
    # Common patterns: team names might be in table cells, links, or headings
    team_patterns = [
        # Look for team logos or links
        ('img', {'alt': re.compile(r'.+')}),
        ('a', {'href': re.compile(r'team|schedule')}),
        ('span', {'class': re.compile(r'team')}),
    ]
    
    for tag, attrs in team_patterns:
        elements = soup.find_all(tag, attrs)
        for elem in elements:
            # Try to extract team name
            team_name = None
            if tag == 'img':
                team_name = elem.get('alt', '')
            elif tag == 'a':
                team_name = elem.get_text(strip=True)
                # Also check href for team ID
                href = elem.get('href', '')
                match = re.search(r'/(\d+)/', href)
                if match:
                    team_id = int(match.group(1))
                    if team_name and team_id not in teams_found:
                        teams_data.append({
                            'season_id': season_id,
                            'team_id': team_id,
                            'team_label': team_name,
                            'city': team_name,
                            'nickname': team_name,
                            'url': f"https://chl.ca/lhjmq/en/schedule/{team_id}/{season_id}/"
                        })
                        teams_found.add(team_id)
    
    return pd.DataFrame(teams_data)

def get_teams_via_api(season_id):
    """Try to get teams via the HockeyTech API"""
    import json
    
    try:
        # Use the API pattern from earlier
        api_url = "https://lscluster.hockeytech.com/feed/"
        params = {
            'feed': 'modulekit',
            'key': 'f1aa699db3d81487',
            'view': 'scorebar',
            'client_code': 'lhjmq',
            'season_id': season_id,
            'numberofdaysahead': 7,
            'numberofdaysback': 7,
            'fmt': 'json'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        
        if response.status_code == 200:
            # Try to parse JSON/JSONP
            content = response.text
            if content.startswith('jsonp_'):
                json_str = content[content.find('(')+1:content.rfind(')')]
                data = json.loads(json_str)
            else:
                data = response.json()
            
            teams_data = []
            if 'SiteKit' in data and 'Scorebar' in data['SiteKit']:
                games = data['SiteKit']['Scorebar']
                
                # Extract unique teams from games
                teams_found = set()
                for game in games:
                    # Home team
                    if 'HomeID' in game and 'HomeLongName' in game:
                        team_id = int(game['HomeID'])
                        if team_id not in teams_found:
                            teams_data.append({
                                'season_id': season_id,
                                'team_id': team_id,
                                'team_label': game['HomeLongName'],
                                'city': game.get('HomeCity', ''),
                                'nickname': game.get('HomeNickname', ''),
                                'url': f"https://chl.ca/lhjmq/en/schedule/{team_id}/{season_id}/"
                            })
                            teams_found.add(team_id)
                    
                    # Visitor team
                    if 'VisitorID' in game and 'VisitorLongName' in game:
                        team_id = int(game['VisitorID'])
                        if team_id not in teams_found:
                            teams_data.append({
                                'season_id': season_id,
                                'team_id': team_id,
                                'team_label': game['VisitorLongName'],
                                'city': game.get('VisitorCity', ''),
                                'nickname': game.get('VisitorNickname', ''),
                                'url': f"https://chl.ca/lhjmq/en/schedule/{team_id}/{season_id}/"
                            })
                            teams_found.add(team_id)
            
            return pd.DataFrame(teams_data)
    
    except Exception as e:
        print(f"API fallback failed: {e}")
    
    return pd.DataFrame()

