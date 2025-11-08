#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de recherche Herald en mode visible pour debug
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper

def test_search_visible():
    """Test en mode visible"""
    
    print("\n" + "=" * 80)
    print("🔍 TEST RECHERCHE VISIBLE")
    print("=" * 80)
    
    cookie_manager = CookieManager()
    scraper = EdenScraper(cookie_manager)
    
    print("\n⚙️  Initialisation du driver (mode visible)...")
    if not scraper.initialize_driver(headless=False):
        print("❌ Échec")
        return
    
    print("✅ Driver initialisé")
    
    print("\n🔐 Chargement des cookies...")
    if not scraper.load_cookies():
        print("❌ Échec")
        scraper.close()
        return
    
    print("✅ Cookies chargés")
    
    # URL de recherche
    character_name = input("\n👉 Nom du personnage: ").strip() or "Testchar"
    search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
    
    print(f"\n🔗 Navigation vers: {search_url}")
    scraper.driver.get(search_url)
    
    print("\n⏳ Attente de 30 secondes...")
    print("👀 Observez le navigateur - le bot check se résout-il ?")
    
    for i in range(30):
        time.sleep(1)
        page_source = scraper.driver.page_source
        
        if '<table' in page_source.lower():
            print(f"\n✅ Tableau détecté après {i+1} secondes !")
            break
        elif 'bot check' in page_source.lower():
            if i % 5 == 0:
                print(f"   ... Bot check toujours actif ({i+1}s)")
        else:
            print(f"\n🤔 Page chargée après {i+1} secondes (pas de tableau détecté)")
            break
    
    # Analyse finale
    print("\n" + "=" * 80)
    print("📊 ANALYSE FINALE")
    print("=" * 80)
    
    page_source = scraper.driver.page_source
    print(f"Taille du HTML: {len(page_source)} caractères")
    print(f"Contient 'bot check': {'✅ OUI' if 'bot check' in page_source.lower() else '❌ NON'}")
    print(f"Contient <table>: {'✅ OUI' if '<table' in page_source.lower() else '❌ NON'}")
    print(f"Contient 'result': {'✅ OUI' if 'result' in page_source.lower() else '❌ NON'}")
    
    print("\n⏸️  Appuyez sur Entrée pour fermer...")
    input()
    
    scraper.close()
    print("\n✅ Fermé")


if __name__ == "__main__":
    test_search_visible()