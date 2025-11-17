#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test pour trouver l'ID d'un item spécifique
"""

import urllib.parse
from Functions.eden_scraper import EdenScraper
from Functions.items_scraper import ItemsScraper
from bs4 import BeautifulSoup
import time
import re

def find_item_id(item_name, realm):
    """
    Recherche l'ID d'un item sur Eden (avec cache)
    
    Args:
        item_name: Nom de l'item
        realm: Royaume (Hibernia, Albion, Midgard)
    
    Returns:
        str: ID de l'item ou None
    """
    from Functions.cookie_manager import CookieManager
    
    cookie_manager = CookieManager()
    scraper = EdenScraper(cookie_manager)
    items_scraper = ItemsScraper(scraper)
    
    try:
        # Check cache first
        cached_id = items_scraper.get_item_id_from_cache(item_name, realm)
        if cached_id:
            print(f"🎯 ID trouvé dans le cache: {cached_id}")
            return cached_id
        
        print(f"⚠️ Item non trouvé dans le cache, recherche en ligne...")
        
        # Initialize driver (NOT headless for items database)
        if not scraper.initialize_driver(headless=False, minimize=True):
            print("❌ Erreur initialisation driver")
            return None
        
        # Load cookies directly
        if not scraper.load_cookies():
            print("❌ Erreur chargement cookies")
            scraper.close()
            return None
        
        # Build search URL
        base_url = "https://eden-daoc.net/items"
        realm_id = ItemsScraper.REALM_MAP.get(realm, 0)
        search_encoded = urllib.parse.quote(item_name)
        
        search_url = f"{base_url}?s={search_encoded}&r={realm_id}"
        
        print(f"🔍 Recherche: {item_name} ({realm})")
        print(f"📍 URL: {search_url}")
        
        # Navigate to search URL
        scraper.driver.get(search_url)
        
        # Wait for results table to load (JavaScript dynamic content)
        print("⏳ Attente chargement des résultats...")
        time.sleep(8)  # Increased wait time for JavaScript to load results
        
        # Try to wait for specific element
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for table results
            WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located((By.ID, "table_result"))
            )
            print("✅ Table de résultats chargée")
            
            # Additional wait for JavaScript population
            time.sleep(3)
            
        except Exception as e:
            print(f"⚠️ Timeout attente table: {e}")
            print("   Continuation quand même...")
        
        # Parse results BEFORE saving HTML
        soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
        
        # Save debug HTML AFTER parsing
        from pathlib import Path
        debug_file = Path('Logs/debug_search_result.html')
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(scraper.driver.page_source)
        print(f"💾 HTML sauvegardé: {debug_file}")
        
        # Debug: Print first few rows found
        all_rows = soup.find_all('tr')
        print(f"🔍 Nombre total de <tr> trouvés: {len(all_rows)}")
        
        result_table = soup.find('table', id='table_result')
        if result_table:
            print(f"✅ Table 'table_result' trouvée")
            table_rows = result_table.find_all('tr')
            print(f"   Nombre de lignes dans table: {len(table_rows)}")
            
            # Print content of each row
            for i, row in enumerate(table_rows[:5]):  # First 5 rows
                print(f"   Row {i}: classes={row.get('class')}, id={row.get('id')}, onclick={row.get('onclick')}")
                cells = row.find_all('td')
                if cells:
                    print(f"           Cellules: {len(cells)}, texte 1ère: {cells[0].get_text(strip=True)[:50]}")
        else:
            print(f"❌ Table 'table_result' NON trouvée")
        
        # Look for item in result table
        # The row has: id="result_row_139635" onclick="item_go(139635)" class="result_row hibbg2"
        
        result_table = soup.find('table', id='table_result')
        if not result_table:
            print("❌ Table de résultats non trouvée")
            print("\n⏸️  Navigateur reste ouvert pour inspection...")
            print("   Appuyez sur Entrée pour fermer")
            input()
            scraper.close()
            return None
        
        # Find all result rows (skip header row 0)
        result_rows = result_table.find_all('tr', class_=re.compile(r'result_row'))
        print(f"🔍 {len(result_rows)} lignes de résultats trouvées")
        
        for row in result_rows:
            # Get onclick attribute
            onclick = row.get('onclick', '')
            row_id = row.get('id', '')
            
            # Get all cells
            cells = row.find_all('td')
            
            if len(cells) >= 2:
                # Cell 1 is the item name (cell 0 is icon)
                name_cell = cells[1]
                row_text = name_cell.get_text(strip=True)
                
                print(f"   Item: '{row_text}' | onclick='{onclick}'")
                
                # Check if this is our item (case insensitive)
                if item_name.lower() == row_text.lower() or item_name.lower() in row_text.lower():
                    print(f"✅ Item trouvé: {row_text}")
                    print(f"   onclick: {onclick}")
                    
                    # Extract ID from onclick="item_go(XXXXX)"
                    id_match = re.search(r'item_go\((\d+)\)', onclick)
                    if id_match:
                        item_id = id_match.group(1)
                        print(f"🎯 ID trouvé: {item_id}")
                        
                        # Save to cache
                        items_scraper.save_item_to_cache(item_name, realm, item_id)
                        
                        # Keep browser open for verification
                        print("\n⏸️  Navigateur reste ouvert pour vérification...")
                        print("   Appuyez sur Entrée pour fermer")
                        input()
                        
                        scraper.close()
                        return item_id
        
        # Also try original link search as fallback
        item_links = soup.find_all('a', href=True)
        
        for link in item_links:
            link_text = link.get_text(strip=True)
            href = link['href']
            
            # Check if link text matches item name (case insensitive)
            if item_name.lower() in link_text.lower():
                print(f"✅ Lien trouvé: {link_text}")
                print(f"   URL: {href}")
                
                # Extract ID from URL
                # Common patterns:
                # /items/view?id=12345
                # /items/12345
                # ?id=12345
                
                id_match = re.search(r'[?&]id=(\d+)', href)
                if id_match:
                    item_id = id_match.group(1)
                    print(f"🎯 ID trouvé: {item_id}")
                    
                    # Keep browser open for verification
                    print("\n⏸️  Navigateur reste ouvert pour vérification...")
                    print("   Appuyez sur Entrée pour fermer")
                    input()
                    
                    scraper.close()
                    return item_id
                
                # Try other patterns
                id_match = re.search(r'/items/(\d+)', href)
                if id_match:
                    item_id = id_match.group(1)
                    print(f"🎯 ID trouvé (pattern 2): {item_id}")
                    
                    print("\n⏸️  Navigateur reste ouvert pour vérification...")
                    print("   Appuyez sur Entrée pour fermer")
                    input()
                    
                    scraper.close()
                    return item_id
        
        print("❌ Aucun ID trouvé")
        print("\n⏸️  Navigateur reste ouvert pour inspection...")
        print("   Appuyez sur Entrée pour fermer")
        input()
        
        scraper.close()
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        if scraper.driver:
            print("\n⏸️  Navigateur reste ouvert pour debug...")
            print("   Appuyez sur Entrée pour fermer")
            input()
        
        scraper.close()
        return None


if __name__ == "__main__":
    item_id = find_item_id("Cape of Legerdemain", "Hibernia")
    
    if item_id:
        print(f"\n✅ RÉSULTAT: L'ID de 'Cape of Legerdemain' (Hibernia) est: {item_id}")
    else:
        print(f"\n❌ ÉCHEC: ID non trouvé")
