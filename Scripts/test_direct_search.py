#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Va directement sur une recherche et vérifie le message
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

# VA DIRECTEMENT sur la recherche (pas sur /herald d'abord)
print("Navigation directe vers la page de recherche...")
url = "https://eden-daoc.net/herald?n=search&s=Test&r=alb"
scraper.driver.get(url)

# Attendre
time.sleep(3)

html = scraper.driver.page_source

# Chercher le message d'erreur
msg = 'The requested page "herald" is not available.'
if msg in html:
    print("Message d'erreur TROUVE - Pas connecte!")
else:
    print("Message d'erreur PAS trouve - Peut-etre connecte?")

# Affiche les cookies dans le driver
print("\nCookies dans le driver:")
try:
    cookies = scraper.driver.get_cookies()
    for c in cookies:
        print(f"  - {c.get('name')}")
except:
    print("  Erreur lors de la lecture des cookies")

scraper.close()
