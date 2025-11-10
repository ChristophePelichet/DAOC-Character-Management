"""
Test script for RvR Captures scraper
Tests the scrape_rvr_captures function to retrieve Tower, Keep, and Relic captures

Usage:
    python Scripts/test_rvr_captures.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager


def test_rvr_captures():
    """Test RvR captures extraction"""
    
    print("\n" + "=" * 80)
    print("RvR Captures Scraper Test")
    print("=" * 80)
    
    # Test URL
    test_url = "https://eden-daoc.net/herald?n=player&k=Ewo"
    print(f"\nTest character: Ewo")
    print(f"URL: {test_url}")
    
    print("\n" + "-" * 80)
    print("Initializing scraper...")
    print("-" * 80)
    
    # Initialize cookie manager and scraper
    cookie_manager = CookieManager()
    
    if not cookie_manager.cookie_exists():
        print("\n❌ ERROR: No cookies found!")
        print("Please generate cookies using the Cookie Manager first.")
        return False
    
    scraper = CharacterProfileScraper(cookie_manager)
    
    # Initialize driver (visible browser to see what happens)
    print("Starting browser...")
    if not scraper.initialize_driver(headless=False):
        print("❌ Failed to initialize browser driver")
        return False
    
    print("✅ Browser initialized")
    
    # Load cookies
    print("\nLoading cookies and authenticating...")
    if not scraper.load_cookies():
        print("❌ Failed to load cookies or authenticate")
        scraper.close()
        return False
    
    print("✅ Authenticated successfully")
    
    # Scrape RvR captures
    print("\n" + "-" * 80)
    print("Scraping RvR capture statistics...")
    print("-" * 80)
    
    result = scraper.scrape_rvr_captures(test_url)
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if result['success']:
        print("\n✅ SUCCESS!")
        print("\nRvR Capture Statistics:")
        print(f"  Tower Captures:  {result['tower_captures']:,}")
        print(f"  Keep Captures:   {result['keep_captures']:,}")
        print(f"  Relic Captures:  {result['relic_captures']:,}")
    else:
        print("\n❌ FAILED!")
        print(f"\nError: {result.get('error', 'Unknown error')}")
        print("\nPartial results:")
        print(f"  Tower Captures:  {result['tower_captures']}")
        print(f"  Keep Captures:   {result['keep_captures']}")
        print(f"  Relic Captures:  {result['relic_captures']}")
    
    print("=" * 80)
    
    # Cleanup
    print("\nClosing browser...")
    scraper.close()
    print("✅ Done")
    
    return result['success']


if __name__ == "__main__":
    print("\n🏰 RvR Captures Scraper Test\n")
    
    success = test_rvr_captures()
    
    print()
    sys.exit(0 if success else 1)
