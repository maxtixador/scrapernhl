
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import json

def getSeasons(url="https://chl.ca/lhjmq/en/schedule/"):
    """
    Scrape all seasons metadata from LHJMQ schedule page

    Parameters:
    -----------
    url : str
        URL of the schedule page (default is current schedule)

    Returns:
    --------
    pandas.DataFrame
        DataFrame with columns: season_id, label, year, season_type
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        # print(f"Scraping from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the seasons dropdown
        seasons_select = soup.find('select', {'id': 'seasons'})

        if not seasons_select:
            # Try alternative selectors
            seasons_select = soup.find('select', class_='form-select')
            seasons_select = soup.find('select', {'name': lambda x: x and 'season' in x.lower()})

        if not seasons_select:
            raise ValueError("Could not find seasons dropdown on the page")

        # Extract data from options
        seasons_data = []

        for option in seasons_select.find_all('option'):
            option_value = option.get('value', '').strip()
            option_text = option.get_text(strip=True)

            if not option_value or not option_text:
                continue

            # Extract season_id from URL (last number before trailing slash)
            # URL format: https://chl.ca/lhjmq/en/schedule/16/211/
            match = re.search(r'/(\d+)/?$', option_value.rstrip('/'))
            if not match:
                continue

            season_id = int(match.group(1))
            label = option_text

            # Extract year and season type
            year, season_type = parse_season_label(label)

            seasons_data.append({
                'season_id': season_id,
                'label': label,
                'year': year,
                'season_type': season_type
            })

        # Create DataFrame and sort by season_id (most recent first)
        df = pd.DataFrame(seasons_data)
        df = df.sort_values('season_id', ascending=False).reset_index(drop=True)

        df.loc[df["season_type"].isin(["regular", "preseason"]), "year"] = df["year"] + 1

        # print(f"Successfully scraped {len(df)} seasons")
        return df

    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return pd.DataFrame(columns=['season_id', 'label', 'year', 'season_type'])
    except Exception as e:
        print(f"Error parsing data: {e}")
        return pd.DataFrame(columns=['season_id', 'label', 'year', 'season_type'])

def parse_season_label(label):
    """
    Parse season label to extract year and season type

    Examples:
    - "2025-26 | Regular Season" → (2025, "regular")
    - "Pre-Season 2025" → (2025, "preseason")
    - "2025 | Playoffs" → (2025, "postseason")
    """

    label_lower = label.lower()

    # Initialize defaults
    year = None
    season_type = "unknown"

    # Try to extract year - look for 4-digit years
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', label)
    if year_match:
        year = int(year_match.group(1))

    # Determine season type
    if 'pre-season' in label_lower or 'preseason' in label_lower:
        season_type = "preseason"
    elif 'playoff' in label_lower or 'postseason' in label_lower:
        season_type = "postseason"
    elif 'regular' in label_lower:
        season_type = "regular"
    elif '|' in label:
        # If it has a pipe but no clear type, check second part
        parts = [p.strip().lower() for p in label.split('|')]
        if len(parts) > 1:
            if 'regular' in parts[1]:
                season_type = "regular"
            elif 'playoff' in parts[1]:
                season_type = "postseason"

    return year, season_type


def getSchedule(team_id: [int, str], season_id = 211) -> pd.DataFrame:
    """
    Fetch the schedule for a given team and season from LHJMQ.

    Parameters:
    -----------
    team_code : str
        The team's code (e.g., "GAT" for Gatineau).
    season_id : int
        The season ID to fetch the schedule for.
    """
    team_id = str(team_id)

    url = f"https://lscluster.hockeytech.com/feed/?feed=modulekit&key=f1aa699db3d81487&view=scorebar&client_code=lhjmq&**numberofdaysahead=365&numberofdaysback=365&season_id={season_id}&team_id={team_id}&lang_code=en&fmt=json"

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        data = json.loads(response.text)['SiteKit']["Scorebar"]

        df = pd.json_normalize(data)
        df = df[df['SeasonID'].isin([season_id, int(season_id), str(season_id)])]
        return df
    except requests.RequestException as e:
        print(f"Error fetching schedule: {e}")
        return pd.DataFrame()






