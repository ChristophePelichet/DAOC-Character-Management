#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Affiche les cookies qui sont chargés
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.cookie_manager import CookieManager
import json

cookie_mgr = CookieManager()

print("Vérification des cookies...")
print(f"\nCookie file exists: {cookie_mgr.cookie_exists()}")

if cookie_mgr.cookie_exists():
    cookies = cookie_mgr.get_cookies_for_scraper()
    print(f"\nNombre de cookies: {len(cookies)}")
    print("\nCookies:")
    for i, cookie in enumerate(cookies):
        name = cookie.get('name', 'UNKNOWN')
        value = cookie.get('value', '')[:50]
        domain = cookie.get('domain', '')
        path = cookie.get('path', '')
        expires = cookie.get('expiry', 'N/A')
        print(f"  [{i+1}] {name}")
        print(f"      Domain: {domain}")
        print(f"      Path: {path}")
        print(f"      Value: {value}...")
        print(f"      Expiry: {expires}")
else:
    print("\nPas de cookies trouvés!")
