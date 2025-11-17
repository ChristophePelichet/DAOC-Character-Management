#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test pour récupérer les détails d'un item via son ID
"""

import urllib.parse
from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
from bs4 import BeautifulSoup
import time
import re

# Mapping des zones vers leurs abréviations
ZONE_MAPPING = {
    "Passage of Conflict": "SH",  # Summoner's Hall
    "Summoner's Hall": "SH",
    "Sobekite Eternal": "SE",
    "Darkness Falls": "DF",
    "Caledonia": "Cale",
    "Thidranki": "Thid",
    "Abermenai": "Aber",
    "Camelot": "Camelot",
    "Jordheim": "Jordheim",
    "Tir na Nog": "TNN",
    "Oceanus Notos (Hibernia)": "Oceanus Hib",
    "Oceanus Notos (Albion)": "Oceanus Alb",
    "Oceanus Notos (Midgard)": "Oceanus Mid",
    "Oceanus Hesperos (Hibernia)": "Oceanus Hib",
    "Oceanus Hesperos (Albion)": "Oceanus Alb",
    "Oceanus Hesperos (Midgard)": "Oceanus Mid",
    "Oceanus Anatole (Hibernia)": "Oceanus Hib",
    "Oceanus Anatole (Albion)": "Oceanus Alb",
    "Oceanus Anatole (Midgard)": "Oceanus Mid",
    "Oceanus Boreas (Hibernia)": "Oceanus Hib",
    "Oceanus Boreas (Albion)": "Oceanus Alb",
    "Oceanus Boreas (Midgard)": "Oceanus Mid",
    "Deep Volcanus": "Volcanus",
    "Dragon's Lair": "DL",
    "Tuscan Glacier": "Glacier",
}


def parse_price(price_str):
    """
    Parse le prix et retourne un dict avec la monnaie et la quantité
    
    Args:
        price_str: String du prix (ex: "700 Grimoire Pages", "5p 50g", "100000 bounty points")
    
    Returns:
        dict: {'currency': str, 'amount': int/float, 'display': str}
    """
    if not price_str:
        return None
    
    price_str = price_str.strip().lower()
    
    # Galladoria Roots
    if 'galladoria' in price_str or 'roots' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Galladoria Roots', 'amount': amount, 'display': f"{amount} Galladoria Roots"}
        except:
            pass
    
    # Atlantean Glass
    if 'atlantean glass' in price_str or 'glass' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Atlantean Glass', 'amount': amount, 'display': f"{amount} Atlantean Glass"}
        except:
            pass
    
    # Dragon Scales
    if 'dragon scale' in price_str or 'scales' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Dragon Scales', 'amount': amount, 'display': f"{amount} Dragon Scales"}
        except:
            pass
    
    # Aurulite
    if 'aurulite' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Aurulite', 'amount': amount, 'display': f"{amount} Aurulite"}
        except:
            pass
    
    # Orbs
    if 'orb' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Orbs', 'amount': amount, 'display': f"{amount} Orbs"}
        except:
            pass
    
    # Seals
    if 'seal' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Seals', 'amount': amount, 'display': f"{amount} Seals"}
        except:
            pass
    
    # Grimoire Pages
    if 'grimoire' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Grimoire Pages', 'amount': amount, 'display': f"{amount} Grimoire Pages"}
        except:
            pass
    
    # Bounty Points
    if 'bounty' in price_str or 'bp' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Bounty Points', 'amount': amount, 'display': f"{amount} BP"}
        except:
            pass
    
    # Roots (Galladoria)
    if 'root' in price_str:
        try:
            amount = int(price_str.split()[0])
            return {'currency': 'Roots', 'amount': amount, 'display': f"{amount} Roots"}
        except:
            pass
    
    # Gold/Platinum (format: "5p 50g 25s 10c" or "500g")
    if 'p' in price_str or 'g' in price_str or 's' in price_str or 'c' in price_str or 'plat' in price_str or 'gold' in price_str:
        total_copper = 0
        
        # Parse platinum (1p = 1000g = 1000000s = 100000000c)
        if 'p' in price_str:
            match = re.search(r'(\d+)\s*p', price_str)
            if match:
                total_copper += int(match.group(1)) * 100000000
        
        # Parse gold (1g = 1000s = 100000c)
        if 'g' in price_str:
            match = re.search(r'(\d+)\s*g', price_str)
            if match:
                total_copper += int(match.group(1)) * 100000
        
        # Parse silver (1s = 100c)
        if 's' in price_str:
            match = re.search(r'(\d+)\s*s', price_str)
            if match:
                total_copper += int(match.group(1)) * 100
        
        # Parse copper
        if 'c' in price_str:
            match = re.search(r'(\d+)\s*c', price_str)
            if match:
                total_copper += int(match.group(1))
        
        if total_copper > 0:
            # Convert back to readable format
            plat = total_copper // 100000000
            gold = (total_copper % 100000000) // 100000
            silver = (total_copper % 100000) // 100
            copper = total_copper % 100
            
            display_parts = []
            if plat > 0:
                display_parts.append(f"{plat}p")
            if gold > 0:
                display_parts.append(f"{gold}g")
            if silver > 0:
                display_parts.append(f"{silver}s")
            if copper > 0:
                display_parts.append(f"{copper}c")
            
            return {
                'currency': 'Gold',
                'amount': total_copper,
                'display': ', '.join(display_parts) if display_parts else '0c'
            }
    
    # Unknown format
    return {'currency': 'Unknown', 'amount': 0, 'display': price_str}


def get_item_details(item_id, realm="Hibernia"):
    """
    Récupère les détails complets d'un item via son ID
    
    Args:
        item_id: ID de l'item (ex: 139635)
        realm: Royaume (optionnel, pour contexte)
    
    Returns:
        dict: Détails de l'item
    """
    cookie_manager = CookieManager()
    scraper = EdenScraper(cookie_manager)
    
    try:
        # Initialize driver (NOT headless for items database)
        if not scraper.initialize_driver(headless=False, minimize=True):
            print("❌ Erreur initialisation driver")
            return None
        
        # Load cookies directly
        if not scraper.load_cookies():
            print("❌ Erreur chargement cookies")
            scraper.close()
            return None
        
        # Build item details URL
        base_url = "https://eden-daoc.net/items"
        item_url = f"{base_url}?id={item_id}"
        
        print(f"🔍 Récupération détails item ID: {item_id}")
        print(f"📍 URL: {item_url}")
        
        # Navigate to item details URL
        scraper.driver.get(item_url)
        
        # Wait for page load
        print("⏳ Attente chargement de la page...")
        time.sleep(5)
        
        # Try to wait for specific element
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for item details to load
            WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            print("✅ Page de détails chargée")
            
            # Additional wait for JavaScript population
            time.sleep(3)
            
        except Exception as e:
            print(f"⚠️ Timeout attente contenu: {e}")
            print("   Continuation quand même...")
        
        # Parse item details
        soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
        
        # Save debug HTML
        from pathlib import Path
        debug_file = Path('Logs/debug_item_details.html')
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(scraper.driver.page_source)
        print(f"💾 HTML sauvegardé: {debug_file}")
        
        # Extract item information from the page content
        # The data is loaded dynamically and appears in tables
        page_text = scraper.driver.page_source
        
        item_data = {
            'id': item_id,
            'name': None,
            'type': None,
            'slot': None,
            'realm': None,
            'classes': [],
            'level': None,
            'quality': None,
            'utility': None,
            'stats': {},
            'resists': {},
            'skills': {},
            'bonuses': {},
            'charges': [],
            'merchants': []  # Liste des vendeurs
        }
        
        # Parse using BeautifulSoup
        soup = BeautifulSoup(page_text, 'html.parser')
        
        # The item name appears to be in a specific div/span
        # Look for patterns we saw in the terminal output
        
        # Find the main content area - try different selectors
        content_divs = [
            soup.find('td', id='content'),
            soup.find('div', id='itm_details'),
            soup.find('div', class_=re.compile(r'item.*detail', re.I))
        ]
        
        content = None
        for div in content_divs:
            if div:
                content = div
                break
        
        if not content:
            # Fallback: use entire body
            content = soup.find('body')
        
        if content:
            # Extract all text and parse it
            all_text = content.get_text('\n', strip=True)
            
            # Debug: show first part
            print(f"\n📝 Début du texte extrait:")
            lines = all_text.split('\n')
            for i, line in enumerate(lines[:50]):
                if line.strip():
                    print(f"   {i}: {line[:80]}")
            
            # Try to find item name (usually first significant text after navigation)
            for line in lines:
                if 'Cape of' in line or 'Legerdemain' in line:
                    if len(line) < 100 and 'Skill' in lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else False:
                        item_data['name'] = line.strip()
                        print(f"\n✅ Nom extrait: {item_data['name']}")
                        break
            
            # Look for Item Details section
            if 'Item Details' in all_text:
                idx = all_text.index('Item Details')
                # Get section until "Magical Bonuses" or end
                end_idx = all_text.find('Magical Bonuses', idx)
                if end_idx == -1:
                    end_idx = idx + 1000
                details_section = all_text[idx:end_idx]
                print(f"\n✅ Section 'Item Details' trouvée:")
                print(details_section[:500])
                
                # Parse Type, Slot, Realm, etc. - more strict matching
                detail_lines = details_section.split('\n')
                i = 0
                while i < len(detail_lines):
                    line = detail_lines[i].strip()
                    
                    # Only match in Item Details section (before Magical Bonuses)
                    if line == 'Type' and i + 1 < len(detail_lines):
                        next_line = detail_lines[i + 1].strip()
                        if next_line in ['Magical', 'Utility', 'Crafted']:
                            item_data['type'] = next_line
                            i += 1
                    elif line == 'Slot' and i + 1 < len(detail_lines):
                        item_data['slot'] = detail_lines[i + 1].strip()
                        i += 1
                    elif line == 'Realm' and i + 1 < len(detail_lines):
                        next_line = detail_lines[i + 1].strip()
                        if next_line in ['Hibernia', 'Albion', 'Midgard']:
                            item_data['realm'] = next_line
                            i += 1
                    elif line == 'Quality' and i + 1 < len(detail_lines):
                        item_data['quality'] = detail_lines[i + 1].strip()
                        i += 1
                    elif line == 'Required Level' and i + 1 < len(detail_lines):
                        item_data['level'] = detail_lines[i + 1].strip()
                        i += 1
                    elif line == 'Usable by' and i + 1 < len(detail_lines):
                        item_data['classes'] = detail_lines[i + 1].strip()
                        i += 1
                    
                    i += 1
            
            # Look for Magical Bonuses section
            if 'Magical Bonuses' in all_text:
                idx = all_text.index('Magical Bonuses')
                bonuses_section = all_text[idx:idx+2000]
                print(f"\n✅ Section 'Magical Bonuses' trouvée:")
                print(bonuses_section[:800])
                
                # Parse stats, skills, resists
                bonus_lines = bonuses_section.split('\n')
                current_category = None
                
                for i, line in enumerate(bonus_lines):
                    line = line.strip()
                    
                    if line in ['Stat', 'ToA', 'Magic', 'Other']:
                        current_category = line
                    elif current_category and i + 1 < len(bonus_lines):
                        # Next line should be the value
                        value_line = bonus_lines[i + 1].strip()
                        
                        if value_line.isdigit():
                            if current_category == 'Stat':
                                item_data['stats'][line] = int(value_line)
                            elif current_category == 'Magic':
                                item_data['skills'][line] = int(value_line)
                            elif current_category == 'ToA':
                                item_data['bonuses'][line] = int(value_line)
                            elif current_category == 'Other' and 'Resist' in line:
                                resist_name = line.replace('Resist:', '').strip()
                                item_data['resists'][resist_name] = int(value_line)
            
            # Look for From Merchants section
            if 'From Merchants' in all_text:
                idx = all_text.index('From Merchants')
                # Get section until "From Market" or other section
                end_idx = all_text.find('From Market', idx)
                if end_idx == -1:
                    end_idx = all_text.find('From Monsters', idx)
                if end_idx == -1:
                    end_idx = idx + 2000
                
                merchants_section = all_text[idx:end_idx]
                print(f"\n✅ Section 'From Merchants' trouvée:")
                print(merchants_section)
                
                # Parse merchant info
                merchant_lines = merchants_section.split('\n')
                i = 0
                current_merchant = None
                
                while i < len(merchant_lines):
                    line = merchant_lines[i].strip()
                    
                    # Skip header and empty lines
                    if line == 'From Merchants' or not line:
                        i += 1
                        continue
                    
                    # Check if line contains "Level:" pattern
                    if 'Level:' in line:
                        # This could be on same line or previous line was name
                        if current_merchant is None:
                            # Previous line should be merchant name
                            if i > 0:
                                merchant_name = merchant_lines[i - 1].strip()
                            else:
                                merchant_name = line.split('Level:')[0].strip()
                            
                            current_merchant = {
                                'name': merchant_name,
                                'level': line.split('Level:')[1].strip() if 'Level:' in line else '',
                                'location': None,
                                'zone': None,
                                'zone_full': None,
                                'price': None
                            }
                    
                    # Location line (starts with "in ")
                    elif line.startswith('in ') and current_merchant:
                        zone_full = line.replace('in ', '').strip()
                        # Convert to short name using mapping
                        zone_short = ZONE_MAPPING.get(zone_full, zone_full)
                        current_merchant['zone'] = zone_short
                        current_merchant['zone_full'] = zone_full
                    
                    # Location coordinates (starts with "Loc:")
                    elif line.startswith('Loc:') and current_merchant:
                        current_merchant['location'] = line.replace('Loc:', '').strip()
                    
                    # Price line (starts with "Price:")
                    elif line.startswith('Price:') and current_merchant:
                        # Price might be on same line or next line
                        price_text = line.replace('Price:', '').strip()
                        if not price_text and i + 1 < len(merchant_lines):
                            # Price on next line
                            price_text = merchant_lines[i + 1].strip()
                            i += 1
                        
                        current_merchant['price'] = price_text
                        current_merchant['price_parsed'] = parse_price(price_text)
                        
                        # Override zone to "ToA" if price is in Atlantean Glass
                        if current_merchant['price_parsed'] and current_merchant['price_parsed']['currency'] == 'Atlantean Glass':
                            current_merchant['zone'] = 'ToA'
                        
                        # Override zone to "DF" if price is in Seals
                        if current_merchant['price_parsed'] and current_merchant['price_parsed']['currency'] == 'Seals':
                            current_merchant['zone'] = 'DF'
                        
                        # Override zone to "Galladoria" if price is in Roots
                        if current_merchant['price_parsed'] and current_merchant['price_parsed']['currency'] == 'Roots':
                            current_merchant['zone'] = 'Galladoria'
                        
                        # Merchant entry complete, add to list
                        if current_merchant['name']:
                            item_data['merchants'].append(current_merchant)
                        current_merchant = None
                    
                    i += 1
        
        print(f"\n📊 Données extraites:")
        print(f"   Nom: {item_data['name']}")
        print(f"   Type: {item_data['type']}")
        print(f"   Slot: {item_data['slot']}")
        print(f"   Royaume: {item_data['realm']}")
        print(f"   Qualité: {item_data['quality']}")
        print(f"   Niveau: {item_data['level']}")
        print(f"   Stats: {item_data['stats']}")
        print(f"   Résistances: {item_data['resists']}")
        print(f"   Compétences: {item_data['skills']}")
        print(f"   Bonus ToA: {item_data['bonuses']}")
        print(f"\n   💰 Vendeurs: {len(item_data['merchants'])}")
        
        # Group merchants by zone and currency
        by_zone = {}
        for merchant in item_data['merchants']:
            zone = merchant['zone']
            if zone not in by_zone:
                by_zone[zone] = []
            by_zone[zone].append(merchant)
        
        # Display by zone with totals
        for zone, merchants in by_zone.items():
            print(f"\n      📍 Zone: {zone}")
            
            # Group by currency
            by_currency = {}
            for merchant in merchants:
                price_info = merchant.get('price_parsed')
                if price_info:
                    currency = price_info['currency']
                    if currency not in by_currency:
                        by_currency[currency] = []
                    by_currency[currency].append(merchant)
            
            # Display merchants and calculate totals
            for currency, merch_list in by_currency.items():
                total = sum(m['price_parsed']['amount'] for m in merch_list if m.get('price_parsed'))
                
                print(f"         💵 {currency}:")
                for m in merch_list:
                    print(f"            • {m['name']} (Lv{m['level']})")
                    print(f"              Loc: {m['location']}")
                    print(f"              Prix: {m['price_parsed']['display']}")
                
                # Display total
                if currency == 'Grimoire Pages':
                    print(f"         ➡️  TOTAL {zone}: {total} Grimoire Pages")
                elif currency == 'Atlantean Glass':
                    print(f"         ➡️  TOTAL {zone}: {total} Atlantean Glass")
                elif currency == 'Dragon Scales':
                    print(f"         ➡️  TOTAL {zone}: {total} Dragon Scales")
                elif currency == 'Aurulite':
                    print(f"         ➡️  TOTAL {zone}: {total} Aurulite")
                elif currency == 'Orbs':
                    print(f"         ➡️  TOTAL {zone}: {total} Orbs")
                elif currency == 'Seals':
                    print(f"         ➡️  TOTAL {zone}: {total} Seals")
                elif currency == 'Seals':
                    print(f"         ➡️  TOTAL {zone}: {total} Seals")
                elif currency == 'Bounty Points':
                    print(f"         ➡️  TOTAL {zone}: {total} BP")
                elif currency == 'Gold':
                    # Convert back to readable format
                    plat = total // 100000000
                    gold = (total % 100000000) // 100000
                    silver = (total % 100000) // 100
                    copper = total % 100
                    
                    parts = []
                    if plat > 0:
                        parts.append(f"{plat}p")
                    if gold > 0:
                        parts.append(f"{gold}g")
                    if silver > 0:
                        parts.append(f"{silver}s")
                    if copper > 0:
                        parts.append(f"{copper}c")
                    
                    print(f"         ➡️  TOTAL {zone}: {', '.join(parts) if parts else '0c'}")
        
        print("\n⏸️  Navigateur reste ouvert pour inspection...")
        print("   Appuyez sur Entrée pour fermer")
        input()
        
        scraper.close()
        return item_data
        
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
    # Test avec Cape of Legerdemain (Grimoire Pages / SH)
    print("=" * 80)
    print("TEST 1: Cape of Legerdemain (ID 139635)")
    print("=" * 80)
    item_details = get_item_details(139635, "Hibernia")
    
    # Test avec Filigree Antalya Ring (Atlantean Glass / ToA)
    print("\n\n" + "=" * 80)
    print("TEST 2: Filigree Antalya Ring (ID 136668)")
    print("=" * 80)
    item_details = get_item_details(136668, "Hibernia")
    
    if item_details:
        print(f"\n✅ RÉSULTAT:")
        print(f"   ID: {item_details['id']}")
        print(f"   Nom: {item_details['name']}")
        print(f"   Type: {item_details['type']}")
        print(f"   Slot: {item_details['slot']}")
    else:
        print(f"\n❌ ÉCHEC: Détails non récupérés")
