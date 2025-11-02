#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sauvegarde le HTML complet pour inspection
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
import time

cookie_mgr = CookieManager()
scraper = EdenScraper(cookie_mgr)

if not scraper.initialize_driver(headless=False):
    print("Erreur")
    exit(1)

# Charger les cookies
scraper.load_cookies()

# Aller sur la recherche
url = "https://eden-daoc.net/herald?n=search&s=Elara&r=alb"
print(f"Navigation vers {url}...")
scraper.driver.get(url)
time.sleep(4)

html = scraper.driver.page_source

# Sauvegarder
with open(r"D:\Projets\Python\DAOC-Character-Management\Scripts\search_result.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ HTML sauvegardé (taille: {len(html)} caractères)")
print(f"Fichier: D:\\Projets\\Python\\DAOC-Character-Management\\Scripts\\search_result.html")

scraper.close()
