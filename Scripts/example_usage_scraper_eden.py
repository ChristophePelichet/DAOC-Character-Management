#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemple d'utilisation du module Eden Scraper dans DAOC-Character-Management
"""

from eden_scraper import PersistentScraper
import json

def scrape_character(character_name):
    """Scraper un personnage par son nom"""
    url = f"https://eden-daoc.net/herald?n=player&k={character_name}"
    
    print(f"📡 Scraping du personnage: {character_name}")
    
    scraper = PersistentScraper(cookie_file='eden_scraper/session_cookies.pkl')
    data = scraper.scrape_with_session(url)
    
    if data:
        # Sauvegarder les données
        filename = f"data_{character_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Données sauvegardées: {filename}")
        return data
    else:
        print("❌ Échec du scraping")
        return None

def scrape_multiple_characters(character_names):
    """Scraper plusieurs personnages"""
    results = {}
    
    for name in character_names:
        print(f"\n{'='*60}")
        data = scrape_character(name)
        if data:
            results[name] = data
    
    print(f"\n✅ {len(results)}/{len(character_names)} personnages scrapés avec succès")
    return results

if __name__ == "__main__":
    # Exemple 1: Scraper un seul personnage
    scrape_character("Ewolinette")
    
    # Exemple 2: Scraper plusieurs personnages
    # characters = ["Ewolia", "Ewoline", "Ewolinette", "Ewolinne"]
    # scrape_multiple_characters(characters)
