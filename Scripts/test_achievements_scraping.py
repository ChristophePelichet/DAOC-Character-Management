"""
Test script for achievements scraping functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager

def test_achievements_scraping():
    """Test achievements scraping from Herald"""
    
    # Test URL - replace with actual character URL
    test_url = input("Enter character Herald URL (e.g., https://...): ").strip()
    
    if not test_url:
        print("❌ No URL provided")
        return
    
    print(f"\n🔍 Testing achievements scraping for: {test_url}")
    print("=" * 60)
    
    # Initialize cookie manager
    cookie_manager = CookieManager()
    
    if not cookie_manager.cookie_exists():
        print("❌ No cookies found. Please generate cookies first.")
        return
    
    # Initialize scraper
    scraper = CharacterProfileScraper(cookie_manager)
    
    if not scraper.initialize_driver(headless=False):
        print("❌ Failed to initialize driver")
        return
    
    # Load cookies
    if not scraper.load_cookies():
        scraper.close()
        print("❌ Failed to load cookies")
        return
    
    print("✅ Cookies loaded successfully")
    
    # Scrape achievements
    print("\n📊 Scraping achievements...")
    result = scraper.scrape_achievements(test_url)
    
    # Close scraper
    scraper.close()
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    
    if result['success']:
        achievements = result['achievements']
        print(f"✅ Success! Found {len(achievements)} achievements\n")
        
        if achievements:
            print("Achievements List:")
            print("-" * 60)
            for i, achievement in enumerate(achievements, 1):
                title = achievement.get('title', 'Unknown')
                progress = achievement.get('progress', '0/0')
                current = achievement.get('current', None)
                
                print(f"{i}. {title:50s} {progress}")
                if current and current != "None":
                    print(f"   → Current: {current}")
        else:
            print("ℹ️ No achievements found")
    else:
        error = result.get('error', 'Unknown error')
        print(f"❌ Failed: {error}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("🏆 DAOC Character Manager - Achievements Scraping Test")
    print("=" * 60)
    test_achievements_scraping()
    print("\n✅ Test completed")
