#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de l'accès direct à un personnage (sans passer par la recherche)
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
from bs4 import BeautifulSoup

def test_direct_player_access():
    """Test l'accès direct à un personnage"""
    
    print("\n" + "=" * 80)
    print("🎯 TEST ACCÈS DIRECT PERSONNAGE")
    print("=" * 80)
    
    cookie_manager = CookieManager()
    scraper = EdenScraper(cookie_manager)
    
    if not scraper.initialize_driver(headless=False):
        print("❌ Échec initialisation")
        return
    
    if not scraper.load_cookies():
        print("❌ Échec chargement cookies")
        scraper.close()
        return
    
    print("✅ Driver prêt\n")
    
    # Demander le nom
    character_name = input("👉 Nom du personnage à tester: ").strip() or "Testchar"
    
    # URL directe
    direct_url = f"https://eden-daoc.net/herald?n=player&k={character_name}"
    
    print(f"\n🔗 URL: {direct_url}")
    print("⏳ Navigation...")
    
    scraper.driver.get(direct_url)
    
    # Attendre et analyser
    print("⏳ Attente 10 secondes...")
    for i in range(10):
        time.sleep(1)
        page_source = scraper.driver.page_source
        
        if '<table' in page_source.lower():
            print(f"✅ Tableau détecté après {i+1} secondes !")
            break
        elif 'bot check' in page_source.lower():
            if i == 0 or i == 4 or i == 9:
                print(f"   ⏳ Bot check actif... ({i+1}s)")
        elif 'not found' in page_source.lower() or 'introuvable' in page_source.lower():
            print(f"⚠️  Personnage non trouvé après {i+1} secondes")
            break
    
    # Analyse finale
    print("\n" + "=" * 80)
    print("📊 ANALYSE")
    print("=" * 80)
    
    page_source = scraper.driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    has_bot_check = 'bot check' in page_source.lower()
    tables = soup.find_all('table')
    
    print(f"🤖 Bot check: {'❌ OUI' if has_bot_check else '✅ NON'}")
    print(f"📊 Tableaux: {len(tables)}")
    print(f"📄 Taille HTML: {len(page_source)} caractères")
    
    # Chercher des indices
    if 'not found' in page_source.lower():
        print("⚠️  Message 'not found' détecté")
    if 'character' in page_source.lower():
        print("✅ Mot 'character' trouvé dans la page")
    if 'realm' in page_source.lower():
        print("✅ Mot 'realm' trouvé dans la page")
    
    # Afficher le titre de la page
    title = soup.find('title')
    if title:
        print(f"📌 Titre: {title.get_text(strip=True)}")
    
    # Afficher les en-têtes de tableaux
    if tables:
        print(f"\n📋 En-têtes des tableaux:")
        for idx, table in enumerate(tables[:3], 1):
            headers_row = table.find('tr')
            if headers_row:
                headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
                if headers:
                    print(f"   Tableau {idx}: {headers}")
    
    # Sauvegarder HTML
    html_file = Path(__file__).parent.parent / "Configuration" / f"debug_player_{character_name}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(page_source)
    print(f"\n💾 HTML sauvegardé: {html_file}")
    
    print("\n⏸️  Appuyez sur Entrée pour fermer...")
    input()
    
    scraper.close()
    print("✅ Fermé")


if __name__ == "__main__":
    test_direct_player_access()
