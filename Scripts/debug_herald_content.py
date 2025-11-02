#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour déboguer le contenu exact de la page Herald
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.cookie_manager import CookieManager
import time

cookie_mgr = CookieManager()

if not cookie_mgr.cookie_exists():
    print("Pas de cookies")
    sys.exit(1)

driver, _ = cookie_mgr._initialize_browser_driver(
    headless=False,
    preferred_browser='Chrome',
    allow_download=False
)

try:
    # Étapes de connexion
    driver.get("https://eden-daoc.net/")
    time.sleep(2)
    
    cookies_list = cookie_mgr.get_cookies_for_scraper()
    for cookie in cookies_list:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    
    driver.refresh()
    time.sleep(2)
    
    # Aller sur Herald
    driver.get("https://eden-daoc.net/herald")
    time.sleep(3)
    
    page_source = driver.page_source
    
    print("=" * 80)
    print("CONTENU COMPLET DE LA PAGE (200 premiers caractères)")
    print("=" * 80)
    print(page_source[:200])
    print("=" * 80)
    print("RECHERCHE DES MESSAGES D'ERREUR")
    print("=" * 80)
    
    # Chercher toutes les variations possibles du message
    patterns = [
        'The requested page "herald" is not available.',
        'The requested page "herald" is not available',
        'is not available',
        'requested page',
        'herald',
        'not available',
    ]
    
    for pattern in patterns:
        found = pattern in page_source
        print(f"'{pattern}' : {found}")
    
    # Chercher aussi dans les sections HTML pertinentes
    print("\n" + "=" * 80)
    print("RECHERCHE DANS LE CONTENU (body)")
    print("=" * 80)
    
    # Trouver la position de <body> et afficher son contenu
    if '<body' in page_source:
        body_start = page_source.find('<body')
        body_start = page_source.find('>', body_start) + 1
        body_content = page_source[body_start:body_start+2000]
        print(body_content)
    
    # Afficher un extrait plus grand
    print("\n" + "=" * 80)
    print("EXTRAIT COMPLET (1000 caractères)")
    print("=" * 80)
    print(page_source[:1000])
    
finally:
    driver.quit()
