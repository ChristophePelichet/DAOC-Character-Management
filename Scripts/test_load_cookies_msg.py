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

# Charger les cookies - cela va suretheless vérifier et retourner True/False
print("Appel de load_cookies()...")
result = scraper.load_cookies()

print(f"\nload_cookies() a retourné: {result}")

# Maintenant vérifions le HTML exact qui a été vu
# Aller de nouveau sur Herald et afficher le HTML
print("\nAffichage du HTML de /herald...")
scraper.driver.get("https://eden-daoc.net/herald")
time.sleep(3)

html = scraper.driver.page_source

# Chercher le message
msg = 'The requested page "herald" is not available.'
if msg in html:
    print(f"✅ Message trouvé!")
    # Afficher le contexte
    idx = html.find(msg)
    print(f"\nContexte autour du message:")
    print(html[max(0, idx-200):idx+200])
else:
    print(f"❌ Message PAS trouvé")
    print(f"\nHTML (premiers 1000 caractères):")
    print(html[:1000])

scraper.close()
