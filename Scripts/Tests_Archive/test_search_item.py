#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de recherche d'un item spécifique
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Functions.eden_scraper import EdenScraper
from Functions.items_scraper import ItemsScraper
from Functions.cookie_manager import CookieManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def search_specific_item(item_name, realm, class_name=None, slot=None):
    """Recherche un item spécifique"""
    print("=" * 80)
    print(f"RECHERCHE ITEM: {item_name}")
    print(f"ROYAUME: {realm}")
    if class_name:
        print(f"CLASSE: {class_name}")
    if slot:
        print(f"SLOT: {slot}")
    print("=" * 80)
    
    # Initialize
    print("\n1. Initialisation...")
    cookie_manager = CookieManager()
    eden_scraper = EdenScraper(cookie_manager)
    
    if not eden_scraper.initialize_driver(headless=False, minimize=False):
        print("❌ ERREUR: Driver")
        return
    
    # Load cookies directly
    print("\n2. Chargement cookies...")
    eden_scraper.driver.get("https://eden-daoc.net/")
    time.sleep(1)
    
    cookies_list = cookie_manager.get_cookies_for_scraper()
    for cookie in cookies_list:
        try:
            eden_scraper.driver.add_cookie(cookie)
        except:
            pass
    
    eden_scraper.driver.refresh()
    time.sleep(1)
    
    # Navigate to items
    print("\n3. Navigation vers Items Database...")
    items_scraper = ItemsScraper(eden_scraper)
    
    if not items_scraper.navigate_to_market():
        print("❌ ERREUR: Impossible d'accéder à la database")
        input("Appuyez sur Enter pour fermer...")
        eden_scraper.close()
        return
    
    print("✅ Database accessible")
    
    # Apply filters
    print(f"\n4. Application des filtres...")
    
    try:
        # Build search URL with parameters
        # r=1 (Albion), r=2 (Midgard), r=3 (Hibernia), r=0 (All)
        realm_map = {
            "Albion": 1,
            "Midgard": 2,
            "Hibernia": 3,
            "All": 0
        }
        
        # Class IDs (examples, need to be mapped)
        # c=48 seems to be a specific class ID
        # We'll add this as optional parameter
        
        realm_id = realm_map.get(realm, 0)
        
        # URL encode the item name
        import urllib.parse
        item_encoded = urllib.parse.quote(item_name)
        
        # Build base URL
        search_url = f"https://eden-daoc.net/items?s={item_encoded}&r={realm_id}"
        
        # Add class filter if provided
        if class_name:
            # For now, we'll need to map class names to IDs
            # This would require a complete mapping table
            search_url += f"&c={class_name}"  # Assuming class_name can be ID for now
        
        # Add slot filter if provided
        if slot:
            # t= parameter for slot type
            # Format can be simple ID or composite like "41-26"
            search_url += f"&t={slot}"
        
        print(f"   URL: {search_url}")
        print(f"   - Royaume: {realm} (ID: {realm_id})")
        print(f"   - Item: {item_name}")
        if class_name:
            print(f"   - Classe: {class_name}")
        if slot:
            print(f"   - Slot: {slot}")
        
        # Navigate to search URL
        eden_scraper.driver.get(search_url)
        time.sleep(3)
        
        print("\n✅ RECHERCHE EFFECTUÉE")
        print("\n" + "=" * 80)
        print("📋 PAGE OUVERTE - Inspectez manuellement les résultats")
        print("=" * 80)
        print(f"\nRecherche: {item_name}")
        print(f"Royaume: {realm}")
        if class_name:
            print(f"Classe: {class_name}")
        if slot:
            print(f"Slot: {slot}")
        print("\nLe navigateur reste ouvert pour inspection...")
        print("Appuyez sur Enter pour fermer le navigateur...")
        input()
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la recherche: {e}")
        import traceback
        traceback.print_exc()
        print("\nLe navigateur reste ouvert pour inspection...")
        print("Appuyez sur Enter pour fermer...")
        input()
    
    finally:
        eden_scraper.close()
        print("✅ Navigateur fermé")

if __name__ == "__main__":
    # Test avec classe (c=48) et slot (t=41-26)
    search_specific_item("Cape of Legerdemain", "Hibernia", class_name="48", slot="41-26")
