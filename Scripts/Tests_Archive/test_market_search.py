#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test du MarketScraper - Recherche d'items spécifiques
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

def test_market_search():
    """Test de recherche dans la database items"""
    print("=" * 80)
    print("TEST ITEM DATABASE SCRAPER - Recherche d'items")
    print("=" * 80)
    
    # Initialize cookie manager
    print("\n1. Initialisation du Cookie Manager...")
    cookie_manager = CookieManager()
    
    # Initialize Eden scraper
    print("\n2. Initialisation du Scraper Eden...")
    eden_scraper = EdenScraper(cookie_manager)
    
    # Initialize driver (NON-headless pour accès market)
    print("\n3. Initialisation du driver Selenium (mode visible, NON minimisé)...")
    if not eden_scraper.initialize_driver(headless=False, minimize=False):
        print("❌ ERREUR: Impossible d'initialiser le driver")
        return
    
    print("✅ Driver initialisé")
    
    # Load cookies DIRECTEMENT sans passer par Herald
    print("\n4. Chargement des cookies (direct, sans Herald)...")
    try:
        # Navigate to root
        eden_scraper.driver.get("https://eden-daoc.net/")
        time.sleep(1)
        
        # Get and add cookies
        cookies_list = cookie_manager.get_cookies_for_scraper()
        if not cookies_list:
            print("❌ ERREUR: Aucun cookie disponible")
            eden_scraper.close()
            return
        
        cookies_added = 0
        for cookie in cookies_list:
            try:
                eden_scraper.driver.add_cookie(cookie)
                cookies_added += 1
            except:
                pass
        
        print(f"✅ {cookies_added}/{len(cookies_list)} cookies chargés")
        
        # Refresh pour activer la session
        eden_scraper.driver.refresh()
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ ERREUR chargement cookies: {e}")
        eden_scraper.close()
        return
    
    # Initialize items scraper
    print("\n5. Initialisation du Items Scraper...")
    market_scraper = ItemsScraper(eden_scraper)
    
    # Navigate to market
    print("\n6. Navigation vers la Database Items...")
    if not market_scraper.navigate_to_market():
        print("❌ ERREUR: Impossible d'accéder à la database items")
        print("\n⏸️  Le navigateur reste ouvert pour inspection...")
        print("   Vérifiez manuellement la page, puis appuyez sur Enter pour fermer...")
        input()
        eden_scraper.close()
        return
    
    print("✅ Database Items accessible")
    
    # Test 1: Search by slot (Helmet)
    print("\n" + "=" * 80)
    print("TEST 1: Recherche par Slot (Helmet)")
    print("=" * 80)
    
    try:
        # Select Helmet in slot dropdown
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        
        slot_select = Select(eden_scraper.driver.find_element(By.ID, "select_slot"))
        slot_select.select_by_visible_text("Helm")
        print("✅ Filtre 'Helm' sélectionné")
        
        time.sleep(3)  # Wait for results to load
        
        # Save HTML to inspect results
        html_content = eden_scraper.driver.page_source
        debug_file = project_root / 'Logs' / 'debug_market_results_helm.html'
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 Résultats sauvegardés dans: {debug_file}")
        print(f"   Taille HTML: {len(html_content)} caractères")
        
        # Try to parse results
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for result indicators
        tables = soup.find_all('table')
        print(f"\n📊 Tables trouvées: {len(tables)}")
        
        # Look for item rows/containers
        items_found = 0
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:  # Has data rows (not just header)
                print(f"\n   Table avec {len(rows)} lignes:")
                # Show first few rows
                for i, row in enumerate(rows[:5]):
                    cells = row.find_all(['th', 'td'])
                    if cells:
                        row_text = ' | '.join([cell.get_text(strip=True)[:30] for cell in cells])
                        print(f"      Row {i}: {row_text}")
                        if i > 0:  # Not header
                            items_found += 1
        
        print(f"\n📦 Items potentiels trouvés: {items_found}")
        
        # Pause to allow manual inspection
        print("\n⏸️  Le navigateur reste ouvert pour inspection manuelle...")
        print("   Appuyez sur Enter pour continuer...")
        input()
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close driver
        print("\n7. Fermeture du driver...")
        eden_scraper.close()
        print("✅ Driver fermé")

if __name__ == "__main__":
    test_market_search()
