#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test EXACT: Cherche le message sur la page /herald comme fait load_cookies()
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
import time

cookie_mgr = CookieManager()
scraper = EdenScraper(cookie_mgr)

if not scraper.initialize_driver(headless=False):
    exit(1)

# Charger les cookies - cela va suretheless verifier et retourner True/False
print("Appel de load_cookies()...")
result = scraper.load_cookies()

print(f"\nload_cookies() a retourne: {result}")

# Maintenant verifions le HTML exact qui a ete vu
# Aller de nouveau sur Herald et afficher le HTML
print("\nAffichage du HTML de /herald...")
scraper.driver.get("https://eden-daoc.net/herald")
time.sleep(3)

html = scraper.driver.page_source

# Chercher le message
msg = 'The requested page "herald" is not available.'
if msg in html:
    print(f"Message trouve!")
else:
    print(f"Message PAS trouve")

scraper.close()
