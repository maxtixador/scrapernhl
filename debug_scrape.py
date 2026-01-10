#!/usr/bin/env python3
"""
Debug version of scrape_game to see what's happening
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_scrape(game_id=31918):
    url = f"https://chl.ca/lhjmq/en/gamecentre/{game_id}/play_by_play/"
    print(f"Testing URL: {url}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser
        
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        
        page = await context.new_page()
        
        try:
            print("1. Loading page...")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            print(f"   Status: {response.status if response else 'None'}")
            print(f"   URL: {page.url}")
            
            print("\n2. Checking for .row.plays container...")
            try:
                await page.wait_for_selector(".row.plays", state="attached", timeout=5000)
                print("   ✓ Found .row.plays")
                
                # Check for play rows
                print("\n3. Checking for play/goal/penalty rows...")
                rows = await page.query_selector_all(".row.plays > .play, .row.plays > .penalty, .row.plays > .goal")
                print(f"   Found {len(rows)} event rows")
                
                if len(rows) == 0:
                    print("\n4. Checking what's inside .row.plays...")
                    plays_container = await page.query_selector(".row.plays")
                    if plays_container:
                        inner_html = await plays_container.inner_html()
                        print(f"   Container HTML length: {len(inner_html)}")
                        print(f"   First 500 chars:\n{inner_html[:500]}")
                
            except Exception as e:
                print(f"   ✗ .row.plays not found: {e}")
                
                # Try to find what IS on the page
                print("\n3. Checking page content...")
                html = await page.content()
                print(f"   Page length: {len(html)} chars")
                
                # Check for common selectors
                selectors_to_check = [
                    ".gamecentre", ".game-center", "#gamecentre",
                    ".plays", ".play-by-play", ".pbp",
                    "[class*='play']", "[class*='game']",
                ]
                
                for sel in selectors_to_check:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            print(f"   ✓ Found: {sel}")
                    except:
                        pass
                
                # Save HTML for inspection
                with open("/Users/max/nhl_scraper/debug_page.html", "w") as f:
                    f.write(html)
                print("\n   Saved page HTML to debug_page.html")
                
        finally:
            await asyncio.sleep(2)  # Let you see the page
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_scrape())
