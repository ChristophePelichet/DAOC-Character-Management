#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test du scraper de production avec les nouvelles méthodes
"""

from Functions.items_scraper import ItemsScraper
from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager

# Initialize
cookie_manager = CookieManager()
eden_scraper = EdenScraper(cookie_manager)

# Initialize driver
if not eden_scraper.initialize_driver(headless=False, minimize=True):
    print("❌ Erreur initialisation driver")
    exit(1)

# Load cookies
if not eden_scraper.load_cookies():
    print("❌ Erreur chargement cookies")
    eden_scraper.close()
    exit(1)

items_scraper = ItemsScraper(eden_scraper)
print("✅ Scraper initialisé\n")

# Test find_item_id
print("=" * 80)
print("TEST: find_item_id()")
print("=" * 80)
item_id = items_scraper.find_item_id("Cape of Legerdemain", "Hibernia")
print(f"Résultat: {item_id}\n")

# Test get_item_details
if item_id:
    print("=" * 80)
    print("TEST: get_item_details()")
    print("=" * 80)
    details = items_scraper.get_item_details(item_id, "Hibernia")
    
    if details:
        print(f"Name: {details.get('name')}")
        print(f"Slot: {details.get('slot')}")
        print(f"Type: {details.get('type')}")
        print(f"Level: {details.get('level')}")
        
        merchants = details.get('merchants', [])
        if merchants:
            print(f"\nMerchants: {len(merchants)}")
            for m in merchants:
                price_parsed = m.get('price_parsed')
                price_display = price_parsed.get('display') if price_parsed else m.get('price')
                print(f"  - {m.get('name')} in {m.get('zone')} ({m.get('zone_full')})")
                print(f"    Price: {price_display}")

# Test parse_price
print("\n" + "=" * 80)
print("TEST: parse_price()")
print("=" * 80)
test_prices = [
    "700 Grimoire Pages",
    "600 Roots",
    "500 Atlantean Glass",
    "100 Seals"
]

for price_str in test_prices:
    result = ItemsScraper.parse_price(price_str)
    if result:
        print(f"{price_str:30} -> {result['currency']:20} ({result['amount']})")

# Close
eden_scraper.close()
print("\n✅ Tests terminés")
