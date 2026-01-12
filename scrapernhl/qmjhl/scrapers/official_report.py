"""
QMJHL Official Game Report Scraper

Extracts comprehensive game data from official game reports including:
- Game information (teams, date, arena, officials)
- Team rosters (lineups with positions)
- Penalties
- Goals with on-ice players (+/-)
- Scoring summary
- Goaltender statistics
"""

import requests
from selectolax.parser import HTMLParser
from typing import Dict, List, Optional, Any
import re


def scrape_official_report(game_id: int) -> Dict[str, Any]:
    """
    Scrape official game report for comprehensive game data.

    Args:
        game_id: The QMJHL game ID

    Returns:
        Dictionary containing all extracted game data structured for easy DataFrame conversion
    """
    url = f"https://lscluster.hockeytech.com/game_reports/official-game-report.php?client_code=lhjmq&game_id={game_id}&lang=en"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    if response.encoding is None or response.encoding == 'ISO-8859-1':
        response.encoding = 'utf-8'

    tree = HTMLParser(response.text)

    return {
        'game_info': _extract_game_info(tree),
        'visiting_team': _extract_team_data(tree, 'visiting'),
        'home_team': _extract_team_data(tree, 'home'),
        'goals': _extract_goals(tree),
        'scoring_by_period': _extract_scoring_by_period(tree),
        'power_play': _extract_power_play_opportunities(tree),
        'penalty_summary': _extract_penalty_summary(tree),
        'point_summary': _extract_point_summary(tree),
        'goaltenders': _extract_goaltender_stats(tree),
        'stars_and_times': _extract_stars_and_game_info(tree),
        'referees': _extract_referees(tree),
    }


def _clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace, newlines, and tabs."""
    if not text:
        return ""
    # Replace multiple whitespace/tabs/newlines with single space
    text = re.sub(r'[\s\t\n\r]+', ' ', text)
    # Remove non-breaking spaces
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    # Strip and return
    return text.strip()


def _extract_game_info(tree: HTMLParser) -> Dict[str, Any]:
    """Extract game header information."""
    info = {
        'arena': None,
        'date': None,
        'visiting_team_name': None,
        'visiting_team_score': None,
        'visiting_head_coach': None,
        'visiting_assistant_coaches': [],
        'visiting_staff': [],
        'home_team_name': None,
        'home_team_score': None,
        'home_head_coach': None,
        'home_assistant_coaches': [],
        'home_staff': [],
        'officials': {},
    }

    # Get all text and use regex to extract
    html_text = tree.html

    # Extract arena
    match = re.search(r'<b>ARENA:</b>\s*([^<\n]+)', html_text)
    if match:
        info['arena'] = _clean_text(match.group(1))

    # Extract date
    match = re.search(r'<b>DATE:</b>\s*([^<\n]+)', html_text)
    if match:
        info['date'] = _clean_text(match.group(1))

    # Extract visiting team info
    match = re.search(r'<b>Visiting Team:</b>\s*([^-]+)-\s*(\d+)', html_text)
    if match:
        info['visiting_team_name'] = _clean_text(match.group(1).replace(',', ''))
        info['visiting_team_score'] = int(match.group(2))

    # Extract visiting coaches/staff
    visiting_section = re.search(r'<b>Visiting Team:</b>.*?(?=<b>Home Team:</b>|<td valign)', html_text, re.DOTALL)
    if visiting_section:
        section_text = visiting_section.group(0)
        info['visiting_head_coach'] = _extract_staff_member(section_text, 'Head Coach')
        info['visiting_assistant_coaches'] = _extract_all_staff_members(section_text, 'Assistant Coach')
        info['visiting_staff'] = _extract_other_staff(section_text)

    # Extract home team info
    match = re.search(r'<b>Home Team:</b>\s*([^-]+)-\s*(\d+)', html_text)
    if match:
        info['home_team_name'] = _clean_text(match.group(1).replace(',', ''))
        info['home_team_score'] = int(match.group(2))

    # Extract home coaches/staff
    home_section = re.search(r'<b>Home Team:</b>.*?(?=<td valign|<b>Video Judge)', html_text, re.DOTALL)
    if home_section:
        section_text = home_section.group(0)
        info['home_head_coach'] = _extract_staff_member(section_text, 'Head Coach')
        info['home_assistant_coaches'] = _extract_all_staff_members(section_text, 'Assistant Coach')
        info['home_staff'] = _extract_other_staff(section_text)

    # Extract officials
    officials_types = [
        'Video Judge', 'Time keeper', 'Webscorer', 'Statistician',
        'Announcer', 'Assistant-Statistician', 'Assistant-Statistician 2',
        'Official Scorer', 'Team\'s doctor/match', 'Referee', 'Linesman'
    ]

    for official_type in officials_types:
        match = re.search(f'<b>{re.escape(official_type)}</b>:\\s*([^<\n]+)', html_text)
        if match:
            info['officials'][official_type.lower().replace(' ', '_').replace("'", "")] = _clean_text(match.group(1))

    return info


def _extract_staff_member(text: str, role: str) -> Optional[str]:
    """Extract single staff member by role."""
    # Handle HTML tags
    match = re.search(f'{role}:\\s*([^<\n]+)', text)
    return _clean_text(match.group(1)) if match else None


def _extract_all_staff_members(text: str, role: str) -> List[str]:
    """Extract all staff members with given role."""
    return [m.group(1).strip() for m in re.finditer(f'{role}:\\s*([^<\n]+)', text)]


def _extract_other_staff(text: str) -> List[Dict[str, str]]:
    """Extract other staff members (Athletic Therapist, Trainer)."""
    staff = []
    for role in ['Athletic Therapist', 'Trainer']:
        matches = re.finditer(f'{role}:\\s*([^<\n]+)', text)
        for match in matches:
            staff.append({'role': role, 'name': match.group(1).strip()})
    return staff


def _extract_team_data(tree: HTMLParser, team_type: str) -> Dict[str, Any]:
    """
    Extract team lineup and penalties.

    Args:
        team_type: 'visiting' or 'home'
    """
    html_text = tree.html

    roster = []
    penalties = []

    # Find lineup table - search for the specific team header
    if team_type == 'visiting':
        # Find DRUMMONDVILLE or first team
        re.search(r'<td[^>]*>.*?LINEUP</b>', html_text, re.IGNORECASE)
        re.search(r'<td[^>]*>.*?PENALTIES</b>', html_text, re.IGNORECASE)
    else:
        # Find GATINEAU or second team - get the second occurrence
        matches = list(re.finditer(r'<td[^>]*>.*?LINEUP</b>', html_text, re.IGNORECASE))
        matches[1] if len(matches) > 1 else None
        matches = list(re.finditer(r'<td[^>]*>.*?PENALTIES</b>', html_text, re.IGNORECASE))
        matches[1] if len(matches) > 1 else None

    # Extract roster from all tables
    tables = tree.css('table')

    # Try a simpler approach: just iterate through all tables and find roster/penalty data
    for table in tables:
        rows = table.css('tr')
        if not rows:
            continue

        # Check if this is a lineup table
        first_row_text = rows[0].text() if rows else ""
        if 'LINEUP' in first_row_text:
            # Determine if this is the right team
            is_target_team = False
            if team_type == 'visiting' and len(roster) == 0:
                is_target_team = True
            elif team_type == 'home' and 'GATINEAU' in first_row_text:
                is_target_team = True
            elif team_type == 'home' and len(roster) == 0:
                # Check if we've passed the first lineup table
                pass

            if is_target_team or (team_type == 'visiting' and len(roster) == 0):
                for row in rows[2:]:  # Skip header rows
                    cells = row.css('td')
                    if len(cells) >= 3:
                        position = _clean_text(cells[0].text())
                        number = _clean_text(cells[1].text())
                        name = _clean_text(cells[2].text())

                        # Skip empty rows
                        if not number and not name:
                            continue

                        # Check if player is marked with <B> tag (starting lineup)
                        is_starting = '<B>' in row.html or '<b>' in row.html.lower()

                        roster.append({
                            'position': position if position else None,
                            'number': number if number else None,
                            'name': name,
                            'is_starting': is_starting,
                        })

                if team_type == 'visiting':
                    break

        # Check if this is a penalties table
        if 'PENALTIES' in first_row_text:
            is_target_team = False
            if team_type == 'visiting' and len(penalties) == 0:
                is_target_team = True
            elif team_type == 'home' and 'GATINEAU' in first_row_text:
                is_target_team = True

            if is_target_team or (team_type == 'visiting' and len(penalties) == 0):
                for row in rows[2:]:  # Skip header rows
                    cells = row.css('td')
                    if len(cells) >= 7:
                        period = _clean_text(cells[0].text())
                        number = _clean_text(cells[1].text())
                        minutes = _clean_text(cells[2].text())
                        offense = _clean_text(cells[3].text())
                        time_off = _clean_text(cells[4].text())
                        pp = _clean_text(cells[5].text())
                        ps = _clean_text(cells[6].text())

                        # Skip empty rows
                        if not period:
                            continue

                        penalties.append({
                            'period': period,
                            'player_number': number if number else None,
                            'minutes': minutes,
                            'offense_code': offense if offense else None,
                            'time_off': time_off,
                            'power_play': pp if pp else None,
                            'penalty_shot': ps if ps else None,
                        })

                if team_type == 'visiting':
                    break

    return {
        'roster': roster,
        'penalties': penalties,
    }


def _extract_goals(tree: HTMLParser) -> List[Dict[str, Any]]:
    """
    Extract goals with on-ice players (+/-).

    Returns list of goals, each containing:
    - period
    - time
    - team (which team scored)
    - scorer_number
    - assist1_number
    - assist2_number
    - on_ice_plus (list of jersey numbers for scoring team)
    - on_ice_minus (list of jersey numbers for defending team)
    """
    goals = []
    found_tables = 0

    # Find all tables and look for goal tables
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) < 3:  # Need at least header + 1 data row
            continue

        first_row_html = rows[0].html if rows else ""

        # Check if this table has nested tables (wrapper table has multiple nested tables)
        nested_tables = table.css('table')
        if len(nested_tables) > 1:
            # This is a wrapper table with multiple nested tables, skip it
            continue

        # Check if this is a goals table
        if ' Goals</b>' not in first_row_html:
            continue

        # This is a goals table - assign team based on order
        if found_tables == 0:
            team_type = 'visiting'
        else:
            team_type = 'home'

        found_tables += 1

        # Process goal rows
        for row in rows[2:]:  # Skip header rows
            cells = row.css('td')
            if len(cells) >= 16:  # Need all columns including on-ice players
                period = _clean_text(cells[0].text())
                time = _clean_text(cells[1].text())
                goal_info = _clean_text(cells[3].text())

                if not period or not goal_info:
                    continue

                # Parse scorer and assists (format: "92-20-47")
                scorer = None
                assist1 = None
                assist2 = None
                if goal_info:
                    parts = goal_info.split('-')
                    if len(parts) >= 1:
                        scorer = parts[0].strip()
                    if len(parts) >= 2:
                        assist1 = parts[1].strip() if parts[1].strip() else None
                    if len(parts) >= 3:
                        assist2 = parts[2].strip() if parts[2].strip() else None

                # Extract on-ice players for scoring team (plus)
                on_ice_plus = []
                for i in range(4, 10):  # Columns 4-9 are plus players
                    if i < len(cells):
                        num = _clean_text(cells[i].text())
                        if num:
                            on_ice_plus.append(num)

                # Extract on-ice players for defending team (minus)
                on_ice_minus = []
                for i in range(10, 16):  # Columns 10-15 are minus players
                    if i < len(cells):
                        num = _clean_text(cells[i].text())
                        if num:
                            on_ice_minus.append(num)

                goals.append({
                    'period': period,
                    'time': time,
                    'team': team_type,
                    'scorer_number': scorer,
                    'assist1_number': assist1,
                    'assist2_number': assist2,
                    'on_ice_plus': on_ice_plus,
                    'on_ice_minus': on_ice_minus,
                })

        # Stop after finding both goal tables (visiting and home)
        if found_tables >= 2:
            break

    return goals


def _clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace, newlines, and tabs."""
    if not text:
        return ""
    # Replace multiple whitespace/tabs/newlines with single space
    import re
    text = re.sub(r'[\s\t\n\r]+', ' ', text)
    # Remove non-breaking spaces
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    # Strip and return
    return text.strip()


def _extract_scoring_by_period(tree: HTMLParser) -> Dict[str, Any]:
    """
    Extract the scoring by period table (goals per period for each team).

    Returns dict with visiting and home team scoring by period.
    """
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) < 3:  # Need at least header + 2 teams
            continue

        first_row_html = rows[0].html if rows else ""

        # Look for the SCORING table - check that it's not a wrapper by verifying it has data rows
        if '<b>SCORING</b>' in first_row_html and '<b>Total</b>' in first_row_html:
            # Verify this is not a wrapper table by checking for nested tables
            if '<table' in first_row_html:
                continue

            # Extract periods from header
            header_cells = rows[0].css('td font')
            periods = []
            for cell in header_cells:
                period_text = _clean_text(cell.text())
                if period_text and period_text != 'SCORING':
                    periods.append(period_text)

            # Extract team scores - should be exactly 2 rows after header
            visiting_team_data = {}
            home_team_data = {}

            data_rows = [r for r in rows[1:] if r.css('td')]
            if len(data_rows) >= 2:
                # First data row is visiting team
                cells = data_rows[0].css('td')
                if len(cells) > 1:
                    visiting_team_data = {
                        'team_name': _clean_text(cells[0].text()),
                        'scores_by_period': [_clean_text(c.text()) for c in cells[1:]]
                    }

                # Second data row is home team
                cells = data_rows[1].css('td')
                if len(cells) > 1:
                    home_team_data = {
                        'team_name': _clean_text(cells[0].text()),
                        'scores_by_period': [_clean_text(c.text()) for c in cells[1:]]
                    }

            return {
                'periods': periods,
                'visiting_team': visiting_team_data,
                'home_team': home_team_data
            }

    return {}


def _extract_goaltender_stats(tree: HTMLParser) -> List[Dict[str, Any]]:
    """
    Extract goaltender statistics.

    Returns list of goalies with their stats.
    """
    goalies = []

    # Find goaltender table
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        # Goaltender table should have exactly 3 rows (header + 2 goalies) for a normal game
        if not rows or len(rows) < 2:
            continue

        first_row_html = rows[0].html if rows else ""

        # Check if this is the goaltender stats table - must have specific header with Tot., On, Off
        if '<b>GOALTENDER/SAVES (Time)</b>' in first_row_html and '<b>Tot.</b>' in first_row_html and '<b>On</b>' in first_row_html:
            # Verify not a wrapper - wrapper tables contain nested <table> tags in data rows
            table_html = table.html
            # Count how many times <table appears - if more than 1, it's a wrapper
            if table_html.count('<table') > 1:
                continue

            # Extract periods from header
            header_cells = rows[0].css('td font')
            periods = []
            for cell in header_cells:
                period_text = _clean_text(cell.text())
                if period_text and period_text not in ['GOALTENDER/SAVES (Time)', 'Tot.', 'On', 'Off']:
                    periods.append(period_text)

            # Process goalie rows
            for row in rows[1:]:
                cells = row.css('td')
                if len(cells) < 8:  # Need at least all columns
                    continue

                goalie_info = _clean_text(cells[0].text())

                if not goalie_info or ' - ' not in goalie_info:
                    continue

                # Parse goalie info (e.g., "Dru - Mercer (62:44) (W)")
                team = None
                goalie_name = None
                time_played = None
                result = None

                parts = goalie_info.split(' - ')
                team = parts[0].strip()

                # Parse rest: "Mercer (62:44) (W)"
                rest = parts[1] if len(parts) > 1 else ""
                # Extract name (everything before first parenthesis)
                name_match = re.match(r'^([^(]+)', rest)
                if name_match:
                    goalie_name = name_match.group(1).strip()

                # Extract time
                time_match = re.search(r'\((\d+:\d+)\)', rest)
                if time_match:
                    time_played = time_match.group(1)

                # Extract result (W/L/OTL)
                result_match = re.search(r'\((W|L|OTL|OTW)\)', rest)
                if result_match:
                    result = result_match.group(1)

                # Extract saves by period (skip first and last 3 columns)
                saves_by_period = []
                for i in range(1, len(cells) - 3):
                    save_text = _clean_text(cells[i].text())
                    if save_text:
                        saves_by_period.append(save_text)

                # Extract total, on, off
                total_saves = _clean_text(cells[-3].text())
                on_time = _clean_text(cells[-2].text())
                off_time = _clean_text(cells[-1].text())

                goalies.append({
                    'team': team,
                    'goalie_name': goalie_name,
                    'time_played': time_played,
                    'result': result,
                    'periods': periods,
                    'saves_by_period': saves_by_period,
                    'total_saves': total_saves,
                    'on_time': on_time,
                    'off_time': off_time,
                })

            # Once we find the correct table, stop
            if goalies:
                break

    return goalies


def _extract_power_play_opportunities(tree: HTMLParser) -> Dict[str, Any]:
    """Extract power play opportunities for each team."""
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) != 3:  # Must have header + 2 teams exactly
            continue

        first_row_html = rows[0].html if rows else ""

        if '<b>POWER PLAY OPPORTUNITIES</b>' in first_row_html:
            # Verify not a wrapper
            if '<table' in ' '.join([r.html for r in rows[1:]]):
                continue

            result = {'visiting_team': {}, 'home_team': {}}

            # Extract visiting team (row 1)
            cells = rows[1].css('td')
            if len(cells) >= 2:
                result['visiting_team'] = {
                    'team_name': _clean_text(cells[0].text()),
                    'power_play': _clean_text(cells[1].text())
                }

            # Extract home team (row 2)
            cells = rows[2].css('td')
            if len(cells) >= 2:
                result['home_team'] = {
                    'team_name': _clean_text(cells[0].text()),
                    'power_play': _clean_text(cells[1].text())
                }

            return result

    return {}


def _extract_penalty_summary(tree: HTMLParser) -> Dict[str, Any]:
    """Extract penalty summary (total minutes/infractions) for each team."""
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) != 3:  # Must have header + 2 teams exactly
            continue

        first_row_html = rows[0].html if rows else ""

        if '<b>PENALTY SUMMARY</b>' in first_row_html:
            # Verify not a wrapper
            if '<table' in ' '.join([r.html for r in rows[1:]]):
                continue

            result = {'visiting_team': {}, 'home_team': {}}

            # Extract visiting team (row 1)
            cells = rows[1].css('td')
            if len(cells) >= 2:
                result['visiting_team'] = {
                    'team_name': _clean_text(cells[0].text()),
                    'penalty_summary': _clean_text(cells[1].text())
                }

            # Extract home team (row 2)
            cells = rows[2].css('td')
            if len(cells) >= 2:
                result['home_team'] = {
                    'team_name': _clean_text(cells[0].text()),
                    'penalty_summary': _clean_text(cells[1].text())
                }

            return result

    return {}


def _extract_point_summary(tree: HTMLParser) -> Dict[str, Any]:
    """Extract point summary (goals + assists) for each team."""
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) != 3:  # Must have header + 2 teams exactly
            continue

        first_row_html = rows[0].html if rows else ""

        if '<b>POINT SUMMARY</b>' in first_row_html:
            # Verify not a wrapper
            if '<table' in ' '.join([r.html for r in rows[1:]]):
                continue

            result = {'visiting_team': {}, 'home_team': {}}

            # Extract visiting team (row 1)
            cells = rows[1].css('td')
            if len(cells) >= 2:
                result['visiting_team'] = {
                    'team_name': _clean_text(cells[0].text()),
                    'point_summary': _clean_text(cells[1].text())
                }

            # Extract home team (row 2)
            cells = rows[2].css('td')
            if len(cells) >= 2:
                result['home_team'] = {
                    'team_name': _clean_text(cells[0].text()),
                    'point_summary': _clean_text(cells[1].text())
                }

            return result

    return {}


def _extract_stars_and_game_info(tree: HTMLParser) -> Dict[str, Any]:
    """Extract stars of the game, game time, and attendance."""
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) != 4:  # Must have exactly 4 rows
            continue

        first_row_html = rows[0].html if rows else ""

        if '<b>Stars of the Game</b>' in first_row_html and '<b>TIME OF GAME:</b>' in first_row_html:
            # Verify not a wrapper
            if '<table' in ' '.join([r.html for r in rows[1:]]):
                continue

            stars = []
            start_time = None
            end_time = None
            attendance = None

            # Extract stars and times from rows 1-3
            for row in rows[1:]:
                cells = row.css('td')
                if len(cells) >= 1:
                    star_text = _clean_text(cells[0].text())
                    if star_text:
                        stars.append(star_text)

                if len(cells) >= 3:
                        label = _clean_text(cells[1].text())
                        value = _clean_text(cells[2].text())

                        if 'Start:' in label:
                            start_time = value
                        elif 'End:' in label:
                            end_time = value
                        elif 'Attendance:' in label:
                            attendance = value

            return {
                'stars': stars,
                'start_time': start_time,
                'end_time': end_time,
                'attendance': attendance
            }

    return {}


def _extract_referees(tree: HTMLParser) -> Dict[str, Any]:
    """Extract referee information."""
    tables = tree.css('table')

    for table in tables:
        rows = table.css('tr')
        if not rows or len(rows) < 2:
            continue

        first_row_html = rows[0].html if rows else ""

        if '<b>OFFICIALS</b>' in first_row_html and 'Referee I:' in table.html:
            # Verify not a wrapper
            if '<table' in ' '.join([r.html for r in rows[1:]]):
                continue

            officials = {}

            for row in rows[1:]:
                cells = row.css('td')
                if len(cells) >= 1:
                    text = _clean_text(cells[0].text())

                    if ':' in text:
                        parts = text.split(':', 1)
                        role = parts[0].strip()
                        name = parts[1].strip() if len(parts) > 1 else ''

                        # Clean role name
                        role = role.lower().replace(' ', '_')
                        officials[role] = name

            return officials

    return {}


if __name__ == "__main__":
    # Test with game 30394
    import json

    print("Scraping official report for game 30394...")
    data = scrape_official_report(30394)

    print("\n" + "="*80)
    print("GAME INFO")
    print("="*80)
    print(json.dumps(data['game_info'], indent=2))

    print("\n" + "="*80)
    print("VISITING TEAM ROSTER")
    print("="*80)
    print(f"Found {len(data['visiting_team']['roster'])} players")
    for player in data['visiting_team']['roster'][:3]:
        print(json.dumps(player, indent=2))

    print("\n" + "="*80)
    print("VISITING TEAM PENALTIES")
    print("="*80)
    print(json.dumps(data['visiting_team']['penalties'], indent=2))

    print("\n" + "="*80)
    print("HOME TEAM ROSTER")
    print("="*80)
    print(f"Found {len(data['home_team']['roster'])} players")

    print("\n" + "="*80)
    print("GOALS WITH ON-ICE PLAYERS")
    print("="*80)
    print(json.dumps(data['goals'], indent=2))

    print(f"\n\nTotal goals: {len(data['goals'])}")
