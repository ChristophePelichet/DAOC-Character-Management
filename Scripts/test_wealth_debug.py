"""
Debug script for Wealth scraper
Tests with detailed logging to see what's happening

Usage:
    python Scripts/test_wealth_debug.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.wealth_manager import get_first_character_per_realm
from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager
from Functions.config_manager import config


def test_debug():
    """Debug test with detailed output"""
    
    print("=" * 80)
    print("Wealth Scraper - DEBUG TEST")
    print("=" * 80)
    
    # Get character folder
    character_folder = config.get('character_folder')
    print(f"\n1. Character folder: {character_folder}")
    
    # Get first character per realm
    print("\n2. Getting first character per realm...")
    characters = get_first_character_per_realm(character_folder)
    
    for realm, char_info in characters.items():
        if char_info:
            print(f"   {realm}: {char_info['name']}")
            print(f"      URL: {char_info['url']}")
        else:
            print(f"   {realm}: No character")
    
    # Test with Albion character if available
    if characters['Albion']:
        print("\n3. Testing with Albion character...")
        char_url = characters['Albion']['url']
        char_name = characters['Albion']['name']
        
        print(f"   Character: {char_name}")
        print(f"   URL: {char_url}")
        
        # Initialize scraper (NOT headless so we can see)
        print("\n4. Initializing scraper (visible browser)...")
        cookie_manager = CookieManager()
        scraper = CharacterProfileScraper(cookie_manager)
        
        if not scraper.initialize_driver(headless=False):
            print("   ❌ Failed to initialize driver")
            return
        
        print("   ✅ Driver initialized")
        
        # Load cookies
        print("\n5. Loading cookies...")
        if not scraper.load_cookies():
            print("   ❌ Failed to load cookies")
            scraper.close()
            return
        
        print("   ✅ Cookies loaded")
        
        # Scrape wealth
        print(f"\n6. Scraping wealth for {char_name}...")
        print(f"   Navigating to: {char_url}")
        
        result = scraper.scrape_wealth_money(char_url)
        
        print("\n7. Results:")
        print(f"   Success: {result['success']}")
        print(f"   Money: {result.get('money', 'None')}")
        print(f"   Error: {result.get('error', 'None')}")
        
        # Close
        print("\n8. Closing browser...")
        scraper.close()
        
        print("\n" + "=" * 80)
        if result['success']:
            print("✅ TEST PASSED!")
            print(f"Money: {result['money']}")
        else:
            print("❌ TEST FAILED!")
            print(f"Error: {result.get('error')}")
        print("=" * 80)
    else:
        print("\n❌ No Albion character found for testing")


if __name__ == "__main__":
    test_debug()
