"""
Test script for Character Profile Wealth Scraper
Tests the new character_profile_scraper.py to verify Money extraction

Usage:
    python Scripts/test_wealth_scraper.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager
from Functions.config_manager import config


def test_single_character():
    """Test scraping Money from a single character"""
    
    # Test URL (Ewo character from Albion)
    test_url = "https://eden-daoc.net/herald?n=player&t=wealth&k=Ewo"
    
    print("=" * 80)
    print("Character Profile Wealth Scraper - Test")
    print("=" * 80)
    print(f"\nTest URL: {test_url}")
    print("\nInitializing scraper...")
    
    # Initialize cookie manager
    cookie_manager = CookieManager()
    
    # Check if cookies exist
    if not cookie_manager.cookie_exists():
        print("\n❌ ERROR: No cookies found!")
        print("Please generate cookies first using the Cookie Manager.")
        return False
    
    print("✅ Cookies found")
    
    # Initialize scraper
    scraper = None
    
    try:
        scraper = CharacterProfileScraper(cookie_manager)
        
        print("\nInitializing WebDriver...")
        if not scraper.initialize_driver(headless=False):  # headless=False to see browser
            print("❌ ERROR: Failed to initialize driver")
            return False
        
        print("✅ WebDriver initialized")
        
        print("\nLoading cookies...")
        if not scraper.load_cookies():
            print("❌ ERROR: Failed to load cookies")
            return False
        
        print("✅ Cookies loaded")
        
        print("\nScraping Money value...")
        print("(Please wait, this may take a few seconds...)")
        
        result = scraper.scrape_wealth_money(test_url)
        
        print("\n" + "-" * 80)
        print("RESULTS:")
        print("-" * 80)
        
        if result['success']:
            print(f"✅ SUCCESS!")
            print(f"   Money: {result['money']}")
        else:
            print(f"❌ FAILED!")
            print(f"   Error: {result['error']}")
            
            # Check if debug file was created
            debug_file = "debug_wealth_page.html"
            if os.path.exists(debug_file):
                print(f"\n   Debug HTML saved to: {debug_file}")
                print(f"   You can open this file to analyze the page structure.")
        
        print("-" * 80)
        
        return result['success']
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            print("\nClosing scraper...")
            scraper.close()
            print("✅ Scraper closed")


def test_multiple_characters():
    """Test scraping Money from multiple characters (if available)"""
    
    # You can add more test URLs here
    test_urls = [
        ("Ewo", "https://eden-daoc.net/herald?n=player&t=wealth&k=Ewo"),
        # Add more characters if you want to test multiple
        # ("CharacterName2", "URL2"),
    ]
    
    print("\n" + "=" * 80)
    print("Testing Multiple Characters")
    print("=" * 80)
    
    cookie_manager = CookieManager()
    
    if not cookie_manager.cookie_exists():
        print("\n❌ ERROR: No cookies found!")
        return False
    
    scraper = None
    results = []
    
    try:
        scraper = CharacterProfileScraper(cookie_manager)
        
        if not scraper.initialize_driver(headless=True):  # headless for batch processing
            print("❌ ERROR: Failed to initialize driver")
            return False
        
        if not scraper.load_cookies():
            print("❌ ERROR: Failed to load cookies")
            return False
        
        for char_name, url in test_urls:
            print(f"\nTesting: {char_name}...")
            result = scraper.scrape_wealth_money(url)
            
            results.append({
                'name': char_name,
                'success': result['success'],
                'money': result['money'],
                'error': result['error']
            })
            
            if result['success']:
                print(f"   ✅ {char_name}: {result['money']}")
            else:
                print(f"   ❌ {char_name}: {result['error']}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\nTotal characters tested: {len(results)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {len(results) - success_count}")
        
        print("\nDetails:")
        for r in results:
            status = "✅" if r['success'] else "❌"
            money = r['money'] if r['success'] else r['error']
            print(f"   {status} {r['name']}: {money}")
        
        return success_count == len(results)
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    print("\n🔍 Character Profile Wealth Scraper Test\n")
    
    # Test single character first
    success = test_single_character()
    
    # If successful and you want to test multiple characters
    # success = test_multiple_characters()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED!")
    else:
        print("❌ TEST FAILED!")
    print("=" * 80)
    print()
    
    sys.exit(0 if success else 1)
