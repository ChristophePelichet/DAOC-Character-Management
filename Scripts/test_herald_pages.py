#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test des différentes pages du Herald pour trouver la meilleure méthode de recherche
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
from bs4 import BeautifulSoup

def test_herald_pages():
    """Test plusieurs pages du Herald"""
    
    print("\n" + "=" * 80)
    print("🔍 TEST DES PAGES HERALD")
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
    
    # Liste des pages à tester
    pages = [
        ("Page principale", "https://eden-daoc.net/herald"),
        ("Top players", "https://eden-daoc.net/herald?n=top_players&r=hib"),
        ("Formulaire recherche", "https://eden-daoc.net/herald?n=search"),
    ]
    
    for title, url in pages:
        print("=" * 80)
        print(f"📄 {title}")
        print(f"🔗 {url}")
        print("-" * 80)
        
        scraper.driver.get(url)
        
        # Attendre et analyser
        print("⏳ Attente 5 secondes...")
        time.sleep(5)
        
        page_source = scraper.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Analyse
        has_bot_check = 'bot check' in page_source.lower()
        tables = soup.find_all('table')
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        
        print(f"🤖 Bot check: {'❌ OUI' if has_bot_check else '✅ NON'}")
        print(f"📊 Tableaux: {len(tables)}")
        print(f"📝 Formulaires: {len(forms)}")
        print(f"⌨️  Inputs: {len(inputs)}")
        
        # Chercher un champ de recherche
        search_inputs = [inp for inp in inputs if inp.get('type') in ['text', 'search'] or 'search' in str(inp.get('name', '')).lower()]
        if search_inputs:
            print(f"🔍 Champs de recherche trouvés:")
            for inp in search_inputs[:3]:
                print(f"   - name: {inp.get('name')}, type: {inp.get('type')}, placeholder: {inp.get('placeholder')}")
        
        # Chercher des liens de recherche
        links = soup.find_all('a', href=True)
        search_links = [link for link in links if 'search' in link.get('href', '').lower()]
        if search_links:
            print(f"🔗 Liens de recherche trouvés: {len(search_links)}")
            for link in search_links[:3]:
                print(f"   - {link.get_text(strip=True)}: {link.get('href')}")
        
        print()
    
    print("=" * 80)
    print("⏸️  Appuyez sur Entrée pour fermer...")
    input()
    
    scraper.close()


if __name__ == "__main__":
    test_herald_pages()
