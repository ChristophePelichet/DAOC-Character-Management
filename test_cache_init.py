#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de l'initialisation du cache
"""

from Functions.items_scraper import ItemsScraper
from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
import json

# Initialize dependencies
cm = CookieManager()
eden = EdenScraper(cm)
scraper = ItemsScraper(eden)

print('✅ Cache créé avec succès')

# Load and display cache
with open('Armory/items_cache.json', encoding='utf-8') as f:
    cache = json.load(f)
    
print(f"📦 Items dans cache: {len(cache['items'])}")
print(f"📝 Description: {cache['description']}")
print(f"🔄 Source: {cache['source']}")

# Display items
print("\nItems:")
for key, item in cache['items'].items():
    print(f"  - {item['name']} (ID: {item['id']}) - {item.get('merchant_zone', 'N/A')}: {item.get('merchant_price', 'N/A')}")
