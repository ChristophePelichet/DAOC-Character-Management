"""
Debug script to examine the HTML structure of the achievements page
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager
from bs4 import BeautifulSoup

def debug_achievements_html():
    """Debug achievements HTML structure"""
    
    # Test URL
    test_url = input("Enter character Herald URL: ").strip()
    
    if not test_url:
        print("❌ No URL provided")
        return
    
    print(f"\n🔍 Debugging achievements HTML for: {test_url}")
    
    # Initialize
    cookie_manager = CookieManager()
    
    if not cookie_manager.cookie_exists():
        print("❌ No cookies found")
        return
    
    scraper = CharacterProfileScraper(cookie_manager)
    
    if not scraper.initialize_driver(headless=False):
        print("❌ Failed to initialize driver")
        return
    
    if not scraper.load_cookies():
        scraper.close()
        print("❌ Failed to load cookies")
        return
    
    # Navigate to achievements page
    # Replace or add &t=achievements parameter
    if '&t=' in test_url:
        achievements_url = test_url
    else:
        # Add &t=achievements to the URL
        achievements_url = f"{test_url}&t=achievements"
    
    print(f"Loading: {achievements_url}")
    scraper.driver.get(achievements_url)
    
    # Wait a bit
    import time
    time.sleep(3)
    
    # Get HTML
    page_source = scraper.driver.page_source
    
    # Save full HTML
    with open("debug_achievements_full.html", 'w', encoding='utf-8') as f:
        f.write(page_source)
    print("✅ Full HTML saved to debug_achievements_full.html")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find player_content
    player_content = soup.find('div', id='player_content')
    
    if player_content:
        print("\n✅ Found player_content div")
        
        # Save player_content only
        with open("debug_achievements_content.html", 'w', encoding='utf-8') as f:
            f.write(player_content.prettify())
        print("✅ Player content saved to debug_achievements_content.html")
        
        # Look for various patterns
        print("\n🔍 Searching for achievement patterns:")
        
        # Pattern 1: div with class achievement
        achievement_divs = player_content.find_all('div', class_='achievement')
        print(f"  - Divs with class 'achievement': {len(achievement_divs)}")
        
        # Pattern 2: tr with class achievement
        achievement_rows = player_content.find_all('tr', class_='achievement')
        print(f"  - Rows with class 'achievement': {len(achievement_rows)}")
        
        # Pattern 3: elements with class 'current'
        current_elements = player_content.find_all(class_='current')
        print(f"  - Elements with class 'current': {len(current_elements)}")
        
        if current_elements:
            print("\n📋 First 5 'current' elements:")
            for i, elem in enumerate(current_elements[:5], 1):
                print(f"  {i}. Tag: {elem.name}, Text: {elem.get_text(strip=True)[:80]}")
        
        # Pattern 4: Look for tables
        tables = player_content.find_all('table')
        print(f"\n  - Tables found: {len(tables)}")
        
        if tables:
            print("\n📋 Table structure:")
            for i, table in enumerate(tables, 1):
                rows = table.find_all('tr')
                print(f"  Table {i}: {len(rows)} rows")
                if rows:
                    first_row = rows[0]
                    cells = first_row.find_all(['td', 'th'])
                    print(f"    First row: {len(cells)} cells")
                    for j, cell in enumerate(cells[:3], 1):
                        print(f"      Cell {j}: {cell.get_text(strip=True)[:50]}")
        
        # Pattern 5: Look for progress patterns in text
        import re
        text = player_content.get_text()
        progress_matches = re.findall(r'\d+/\d+', text)
        print(f"\n  - Progress patterns (X/Y) found: {len(progress_matches)}")
        if progress_matches:
            print(f"    Examples: {progress_matches[:10]}")
        
    else:
        print("\n❌ player_content div NOT found")
        print("Looking for other content containers...")
        
        # Look for any div with id containing 'player' or 'content'
        all_divs = soup.find_all('div', id=True)
        print(f"\nAll divs with IDs: {len(all_divs)}")
        for div in all_divs[:10]:
            print(f"  - {div.get('id')}")
    
    scraper.close()
    print("\n✅ Debug completed")

if __name__ == "__main__":
    debug_achievements_html()
