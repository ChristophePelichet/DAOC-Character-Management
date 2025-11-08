#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test simple de recherche Herald - reprenant la logique originale
"""

import sys
import time
import pickle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def simple_search_test(character_name):
    """Test simple sans toutes les options anti-bot"""
    
    print("\n" + "=" * 80)
    print("🔍 TEST SIMPLE DE RECHERCHE")
    print("=" * 80)
    
    # Charger les cookies
    cookie_file = Path(__file__).parent.parent / "Configuration" / "eden_cookies.pkl"
    
    if not cookie_file.exists():
        print("❌ Pas de cookies trouvés")
        return
    
    with open(cookie_file, 'rb') as f:
        cookies = pickle.load(f)
    
    print(f"✅ {len(cookies)} cookies chargés")
    
    # Initialiser le driver SIMPLE (pas d'options anti-bot)
    print("\n⚙️  Initialisation du driver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Aller sur le domaine principal
        print("🌐 Navigation vers eden-daoc.net...")
        driver.get("https://eden-daoc.net/")
        time.sleep(2)
        
        # Ajouter les cookies
        print("🔐 Injection des cookies...")
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"  ⚠️  Cookie {cookie.get('name')}: {e}")
        
        time.sleep(1)
        
        # URL de recherche
        search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
        print(f"\n🔗 Navigation vers: {search_url}")
        driver.get(search_url)
        
        # Attendre
        print("⏳ Attente 5 secondes...")
        time.sleep(5)
        
        # Analyser
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS")
        print("=" * 80)
        
        has_bot_check = 'bot check' in page_source.lower()
        tables = soup.find_all('table')
        
        print(f"🤖 Bot check: {'❌ OUI' if has_bot_check else '✅ NON'}")
        print(f"📊 Tableaux trouvés: {len(tables)}")
        print(f"📄 Taille HTML: {len(page_source):,} caractères")
        
        if tables:
            print(f"\n✅ SUCCESS ! {len(tables)} tableau(x) trouvé(s)")
            
            # Analyser les tableaux
            for idx, table in enumerate(tables, 1):
                print(f"\n--- Tableau #{idx} ---")
                rows = table.find_all('tr')
                print(f"Lignes: {len(rows)}")
                
                if rows:
                    # Headers
                    header_row = rows[0]
                    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
                    if headers:
                        print(f"Headers: {headers}")
                    
                    # Quelques lignes of Data
                    for row_idx, row in enumerate(rows[1:4], 1):
                        cells = [td.get_text(strip=True) for td in row.find_all('td')]
                        if cells:
                            print(f"  Ligne {row_idx}: {cells}")
        else:
            if has_bot_check:
                print("\n❌ Bot check actif - aucun tableau")
            else:
                print("\n⚠️  Aucun tableau trouvé (mais pas de bot check)")
        
        print("\n⏸️  Appuyez sur Entrée pour fermer...")
        input()
        
    finally:
        driver.quit()
        print("✅ Navigateur fermé")


if __name__ == "__main__":
    character_name = input("\n👉 Nom du personnage: ").strip() or "Ewoline"
    simple_search_test(character_name)