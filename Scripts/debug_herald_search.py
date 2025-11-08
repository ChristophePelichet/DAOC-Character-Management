#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug pour analyser la page de recherche Herald
"""

import sys
from pathlib import Path
import time

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
from bs4 import BeautifulSoup

def debug_search_page(character_name):
    """Analyse la page de recherche Herald"""
    
    print("\n" + "=" * 80)
    print("=" * 80)
    
    # Initialiser
    cookie_manager = CookieManager()
    scraper = EdenScraper(cookie_manager)
    
    if not scraper.initialize_driver(headless=False):  # Mode visible pour debug
        print("❌ Impossible d'initialiser le driver")
        return
    
    if not scraper.load_cookies():
        print("❌ Impossible de charger les cookies")
        scraper.close()
        return
    
    # Construire l'URL
    search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
    print(f"\n🔗 URL: {search_url}")
    
    # Naviguer
    print("⏳ Navigation vers la page...")
    scraper.driver.get(search_url)
    time.sleep(5)  # Attendre plus longtemps
    
    # Retrieve HTML
    page_source = scraper.driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    print("\n" + "=" * 80)
    print("📄 ANALYSE DE LA PAGE")
    print("=" * 80)
    
    # Chercher les tableaux
    tables = soup.find_all('table')
    print(f"\n📊 Nombre de tableaux trouvés: {len(tables)}")
    
    for idx, table in enumerate(tables, 1):
        print(f"\n--- Tableau #{idx} ---")
        
        # Headers
        headers_row = table.find('tr')
        if headers_row:
            headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
            if headers:
                print(f"Headers: {headers}")
        
        # Compter les lignes
        rows = table.find_all('tr')
        print(f"Nombre de lignes: {len(rows)}")
        
        # Afficher the premières lignes
        for row_idx, row in enumerate(rows[:5], 1):
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if cells:
                print(f"  Ligne {row_idx}: {cells}")
    
    # Chercher les divs et sections importantes
    print("\n" + "=" * 80)
    print("🔍 RECHERCHE DE CONTENU")
    print("=" * 80)
    
    # Recherche de "results", "search", "characters"
    keywords = ['result', 'search', 'character', 'player', 'herald']
    for keyword in keywords:
        elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
        if elements:
            print(f"\n🔎 Mot-clé '{keyword}' trouvé {len(elements)} fois")
            for elem in elements[:3]:
                print(f"  → {elem[:100]}")
    
    # Sauvegarder le HTML pour analyse
    html_file = Path(__file__).parent.parent / "Configuration" / "debug_search_page.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(page_source)
    print(f"\n💾 HTML sauvegardé dans: {html_file}")
    
    # Chercher les formulaires
    forms = soup.find_all('form')
    if forms:
        print(f"\n📝 {len(forms)} formulaire(s) trouvé(s)")
        for idx, form in enumerate(forms, 1):
            print(f"\nFormulaire #{idx}:")
            print(f"  Action: {form.get('action', 'N/A')}")
            print(f"  Method: {form.get('method', 'N/A')}")
            inputs = form.find_all('input')
            if inputs:
                print(f"  Inputs: {[inp.get('name', 'N/A') for inp in inputs]}")
    
    print("\n" + "=" * 80)
    print("⏸️  Appuyez sur Entrée pour fermer le navigateur...")
    input()
    
    scraper.close()


if __name__ == "__main__":
    character_name = input("\n👉 Nom du personnage à rechercher: ").strip() or "Testchar"
    debug_search_page(character_name)