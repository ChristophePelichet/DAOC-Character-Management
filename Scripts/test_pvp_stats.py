"""
Script de test pour le scraping des statistiques PvP
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager

def test_pvp_stats():
    """Test PvP statistics scraping"""
    
    # Ask for character URL
    print("=== Test PvP Statistics Scraper ===\n")
    character_url = input("Enter character Herald URL (or press Enter for default): ").strip()
    
    if not character_url:
        # Use default URL - you should replace with a real URL
        character_url = "https://eden-daoc.net/herald?n=player&k=Ewo"
        print(f"Using default URL: {character_url}\n")
    
    # Check cookies
    cookie_manager = CookieManager()
    if not cookie_manager.cookie_exists():
        print("❌ No cookies found. Please generate cookies first.")
        return
    
    print("✅ Cookies found")
    
    # Initialize scraper
    print("Initializing browser...")
    scraper = CharacterProfileScraper(cookie_manager)
    
    if not scraper.initialize_driver(headless=False):
        print("❌ Failed to initialize browser")
        return
    
    print("✅ Browser initialized")
    
    # Load cookies
    print("Loading cookies...")
    if not scraper.load_cookies():
        scraper.close()
        print("❌ Failed to load cookies")
        return
    
    print("✅ Cookies loaded")
    
    # Scrape PvP stats
    print("\n📊 Scraping PvP statistics...")
    result = scraper.scrape_pvp_stats(character_url)
    
    scraper.close()
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"Success: {result['success']}")
    
    if result['success']:
        print("\n✅ PvP Statistics Successfully Retrieved:")
        print(f"\n⚔️  Solo Kills: {result['solo_kills']:,}")
        print(f"   → Albion:   {result['solo_kills_alb']:,}")
        print(f"   → Hibernia: {result['solo_kills_hib']:,}")
        print(f"   → Midgard:  {result['solo_kills_mid']:,}")
        
        print(f"\n💀 Deathblows: {result['deathblows']:,}")
        print(f"   → Albion:   {result['deathblows_alb']:,}")
        print(f"   → Hibernia: {result['deathblows_hib']:,}")
        print(f"   → Midgard:  {result['deathblows_mid']:,}")
        
        print(f"\n🎯 Kills: {result['kills']:,}")
        print(f"   → Albion:   {result['kills_alb']:,}")
        print(f"   → Hibernia: {result['kills_hib']:,}")
        print(f"   → Midgard:  {result['kills_mid']:,}")
    else:
        print(f"\n❌ Failed to retrieve PvP statistics")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Show partial data
        print("\nPartial data retrieved:")
        for key, value in result.items():
            if key not in ['success', 'error']:
                print(f"  {key}: {value}")
    
    print("="*60)

if __name__ == "__main__":
    test_pvp_stats()
