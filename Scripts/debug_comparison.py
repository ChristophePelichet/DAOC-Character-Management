#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug complet - Compare test_eden_connection() vs load_cookies()
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
import json

def main():
    print("\n" + "="*80)
    print("DEBUG COMPLET - Comparaison test vs scraper")
    print("="*80)
    
    cookie_mgr = CookieManager()
    
    # Test 1: test_eden_connection()
    print("\n[ÉTAPE 1] Exécution de test_eden_connection()...")
    result_test = cookie_mgr.test_eden_connection()
    print(f"\nRésultat test_eden_connection():")
    print(f"  - success: {result_test.get('success')}")
    print(f"  - accessible: {result_test.get('accessible')}")
    print(f"  - message: {result_test.get('message')}")
    print(f"  - status_code: {result_test.get('status_code')}")
    
    # Test 2: load_cookies() depuis scraper
    print("\n[ÉTAPE 2] Test du scraper avec load_cookies()...")
    scraper = EdenScraper(cookie_mgr)
    
    if not scraper.initialize_driver(headless=False):
        print("❌ Impossible d'initialiser le driver")
        return
    
    cookies_loaded = scraper.load_cookies()
    print(f"\nRésultat load_cookies(): {cookies_loaded}")
    
    # Test 3: Tenter une recherche
    print("\n[ÉTAPE 3] Tentative de recherche...")
    results = scraper.scrape_search_results("Test", realm="alb")
    print(f"Résultats trouvés: {len(results)}")
    
    scraper.close()
    
    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ:")
    print("="*80)
    print(f"test_eden_connection() dit: {'✅ CONNECTÉ' if result_test.get('accessible') else '❌ NON CONNECTÉ'}")
    print(f"load_cookies() dit: {'✅ CONNECTÉ' if cookies_loaded else '❌ NON CONNECTÉ'}")
    print(f"Recherche a trouvé: {len(results)} personnages")
    print("\nINCOHÉRENCE?")
    if result_test.get('accessible') != cookies_loaded:
        print("⚠️  LES DEUX TESTS DONNENT DES RÉSULTATS DIFFÉRENTS!")
    if result_test.get('accessible') and len(results) == 0:
        print("⚠️  TEST DIT OK MAIS RECHERCHE RETOURNE RIEN!")
    
    print("="*80)

if __name__ == "__main__":
    main()
