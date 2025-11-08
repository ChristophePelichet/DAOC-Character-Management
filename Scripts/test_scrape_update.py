#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour scrape_character_from_url
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_scrape_update():
    """Teste la récupération des données via URL Herald"""
    
    from Functions.eden_scraper import scrape_character_from_url
    from Functions.cookie_manager import CookieManager
    import json
    
    # URL de test
    url = "https://eden-daoc.net/herald?n=player&k=Odamuss"
    
    print(f"🔍 Test de scrape_character_from_url")
    print(f"URL: {url}")
    print("=" * 80)
    
    # Initialiser le cookie manager
    cookie_manager = CookieManager()
    
    # Check cookies
    if not cookie_manager.cookie_exists():
        print("❌ Aucun cookie trouvé!")
        return
    
    print("✅ Cookies trouvés")
    
    # Appeler scrape_character_from_url
    print("\n📡 Appel de scrape_character_from_url...")
    success, data, error_msg = scrape_character_from_url(url, cookie_manager)
    
    print("\n" + "=" * 80)
    print(f"📊 RÉSULTAT:")
    print(f"Success: {success}")
    print(f"Error: {error_msg}")
    print()
    
    if success and data:
        print("📦 Données retournées:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 80)
        print("🔑 Clés disponibles:")
        for key in data.keys():
            value = data[key]
            value_str = str(value)[:50]  # Tronquer pour l'affichage
            print(f"  - {key}: {value_str}")
    else:
        print("❌ Aucune donnée retournée")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_scrape_update()