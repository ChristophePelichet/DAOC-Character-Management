#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug détaillé: Affiche le HTML exact pour chaque étape
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import time

def debug_search():
    print("\n" + "="*80)
    print("DEBUG DÉTAILLÉ - HTML à chaque étape")
    print("="*80)
    
    cookie_mgr = CookieManager()
    scraper = EdenScraper(cookie_mgr)
    
    # Initialiser
    if not scraper.initialize_driver(headless=False):
        print("❌ Erreur init driver")
        return
    
    # Charger les cookies
    print("\n[ÉTAPE 1] load_cookies()...")
    result = scraper.load_cookies()
    print(f"Résultat: {result}")
    
    # Aller sur la page de recherche
    print("\n[ÉTAPE 2] Navigation vers page de recherche...")
    url = "https://eden-daoc.net/herald?n=search&s=Test&r=alb"
    print(f"URL: {url}")
    
    scraper.driver.get(url)
    time.sleep(3)
    
    html = scraper.driver.page_source
    
    # Chercher le message d'erreur
    error_msg = 'The requested page "herald" is not available.'
    has_error = error_msg in html
    
    print(f"\n[RÉSULTAT] Message d'erreur présent: {has_error}")
    
    # Afficher les premiers 2000 caractères du HTML
    print(f"\n[HTML - Premiers 2000 caractères]:")
    print("="*80)
    print(html[:2000])
    print("="*80)
    
    # Chercher "search" ou "résultats"
    if "search" in html.lower():
        print("\n✅ Mot 'search' trouvé dans le HTML")
    else:
        print("\n❌ Mot 'search' PAS trouvé dans le HTML")
    
    if "<table" in html.lower():
        print("✅ Tag <table> trouvé")
    else:
        print("❌ Tag <table> PAS trouvé")
    
    if "Information" in html and error_msg in html:
        print("❌ ERREUR DETECTÉE: Page non accessible")
    
    scraper.close()

if __name__ == "__main__":
    debug_search()
