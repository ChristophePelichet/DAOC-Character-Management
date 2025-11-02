#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test complet du flux Herald
Teste: load_cookies() et scrape_search_results() en parallèle
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

def test_full_flow():
    print("\n" + "="*80)
    print("TEST COMPLET DU FLUX HERALD")
    print("="*80)
    
    # Initialiser le cookie manager
    cookie_mgr = CookieManager()
    
    # Créer le scraper
    scraper = EdenScraper(cookie_mgr)
    
    # Initialiser le driver
    print("\n[1] Initialisation du driver...")
    if not scraper.initialize_driver(headless=False):  # headless=False pour voir ce qui se passe
        print("❌ Erreur lors de l'initialisation du driver")
        return
    
    # Charger les cookies
    print("\n[2] Chargement des cookies...")
    cookies_loaded = scraper.load_cookies()
    print(f"Résultat load_cookies(): {cookies_loaded}")
    
    # Faire une recherche
    print("\n[3] Recherche de personnage...")
    results = scraper.scrape_search_results("Elara", realm="alb")
    print(f"Résultats de recherche: {len(results)} personnages trouvés")
    
    if len(results) == 0:
        print("⚠️  AUCUN RÉSULTAT!")
        print("Cela peut signifier:")
        print("  - Les cookies ne sont pas valides")
        print("  - Herald n'est pas accessible")
        print("  - La recherche est retournée vide")
    else:
        print("✅ Résultats trouvés:")
        for char in results[:5]:
            print(f"   - {char}")
    
    # Fermer
    scraper.close()
    print("\n" + "="*80)
    print("FIN DU TEST")
    print("="*80)

if __name__ == "__main__":
    test_full_flow()
