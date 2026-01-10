#!/usr/bin/env python3
"""Investigation script for QMJHL API patterns."""

import requests
import json


def main():
    print('='*80)
    print('QMJHL API INVESTIGATION')
    print('='*80)
    print()
    
    # Pattern 1: modulekit/scorebar
    print('PATTERN 1: modulekit/scorebar (Team-specific schedule)')
    print('-'*80)
    url1 = 'https://lscluster.hockeytech.com/feed/?feed=modulekit&key=f322673b6bcae299&view=scorebar&client_code=lhjmq&numberofdaysahead=365&numberofdaysback=365&season_id=211&team_id=10&lang_code=en&fmt=json'
    
    try:
        r1 = requests.get(url1, timeout=10)
        d1 = r1.json()
        print(f'Status: {r1.status_code}')
        print(f'Top-level keys: {list(d1.keys())}')
        
        if 'SiteKit' in d1:
            sk = d1['SiteKit']
            print(f'SiteKit keys: {list(sk.keys())}')
            if 'Scorebar' in sk:
                games = sk['Scorebar']
                print(f'Number of games: {len(games)}')
                if games:
                    print(f'Sample game keys: {list(games[0].keys())[:15]}...')
                    print(f'Sample values:')
                    for k in list(games[0].keys())[:5]:
                        print(f'  {k}: {games[0][k]}')
    except Exception as e:
        print(f'Error: {e}')
    
    print()
    print('PATTERN 2: statviewfeed/schedule (Full league schedule)')
    print('-'*80)
    url2 = 'https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=schedule&team=-1&season=211&month=-1&location=homeaway&site_id=0&key=f322673b6bcae299&client_code=lhjmq&league_id=6&lang=en&conference_id=-1&division_id=-1'
    
    try:
        r2 = requests.get(url2, timeout=10)
        text2 = r2.text
        
        # Clean JSONP wrapper
        if text2.startswith('angular.callbacks.'):
            start = text2.find('(')
            if start != -1:
                text2 = text2[start + 1:]
                if text2.endswith(');'):
                    text2 = text2[:-2]
                elif text2.endswith(')'):
                    text2 = text2[:-1]
        
        d2 = json.loads(text2)
        print(f'Status: {r2.status_code}')
        print(f'Response type: {type(d2).__name__}')
        
        if isinstance(d2, dict):
            print(f'Top-level keys: {list(d2.keys())}')
            if 'sections' in d2:
                sections = d2['sections']
                print(f'Number of sections: {len(sections)}')
                if sections:
                    print(f'First section keys: {list(sections[0].keys())}')
                    if 'data' in sections[0]:
                        games = sections[0]['data']
                        print(f'Games in first section: {len(games)}')
                        if games:
                            print(f'Sample game keys: {list(games[0].keys())[:15]}...')
                            print(f'Sample values:')
                            for k in list(games[0].keys())[:5]:
                                print(f'  {k}: {games[0][k]}')
        elif isinstance(d2, list):
            print(f'List length: {len(d2)}')
            if d2 and isinstance(d2[0], dict):
                print(f'First item keys: {list(d2[0].keys())[:15]}...')
    except Exception as e:
        print(f'Error: {e}')
    
    print()
    print('='*80)
    print('CONCLUSION:')
    print('='*80)
    print('Pattern 1 (modulekit/scorebar):')
    print('  - Returns team-specific games')
    print('  - Response: {SiteKit: {Scorebar: [games]}}')
    print('  - Best for: Team schedules, scoreboard displays')
    print()
    print('Pattern 2 (statviewfeed/schedule):')
    print('  - Returns full league schedule')
    print('  - Response: {sections: [{data: [games]}]}')
    print('  - Best for: League-wide queries, all teams')


if __name__ == '__main__':
    main()
