#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test IDENTIQUE - Même code pour les deux détections
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
import time

def test_herald_page(name, driver):
    """Test une page Herald avec un driver"""
    print(f"\n[{name}] Navigation...")
    driver.get("https://eden-daoc.net/herald")
    time.sleep(4)
    
    html = driver.page_source
    
    # Vérifier
    has_logged_in = 'username_logged_in' in html
    has_username_class = 'class="username"' in html
    has_error = 'The requested page "herald" is not available.' in html
    
    print(f"  - username_logged_in: {has_logged_in}")
    print(f"  - class=\"username\": {has_username_class}")
    print(f"  - error message: {has_error}")
    print(f"  - HTML size: {len(html)}")
    
    return has_logged_in or has_username_class

# Test 1: Via test_eden_connection()
print("="*60)
print("TEST 1: via test_eden_connection()")
print("="*60)
cookie_mgr = CookieManager()
result1 = test_herald_page("test_eden_connection", cookie_mgr._initialize_browser_driver(headless=True)[0])

# Test 2: Via load_cookies()
print("\n" + "="*60)
print("TEST 2: via load_cookies()")
print("="*60)
scraper = EdenScraper(cookie_mgr)
scraper.initialize_driver(headless=True)
scraper.load_cookies()
result2 = test_herald_page("load_cookies", scraper.driver)

# Résumé
print("\n" + "="*60)
print("RÉSUMÉ")
print("="*60)
print(f"test_eden_connection: {'CONNECTÉ' if result1 else 'NON CONNECTÉ'}")
print(f"load_cookies: {'CONNECTÉ' if result2 else 'NON CONNECTÉ'}")

# Fermer les drivers
if result1 is not None:  # If it's a driver object
    try:
        # Get the driver from the tuple if needed
        if isinstance(result1, bool):
            print("\nNote: result1 is bool, driver already closed")
    except:
        pass

scraper.close()
