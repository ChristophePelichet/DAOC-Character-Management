#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rapide de la recherche headless
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.eden_scraper import search_herald_character

print("\n" + "=" * 80)
print("🔍 TEST RECHERCHE HERALD EN MODE HEADLESS")
print("=" * 80)

character_name = input("\n👉 Nom du personnage: ").strip() or "Ewoline"

print(f"\n🔍 Recherche de '{character_name}' en cours (mode headless)...")
print("⏳ Le navigateur ne devrait PAS s'ouvrir...")

success, message, json_path = search_herald_character(character_name)

print("\n" + "=" * 80)
if success:
    print("✅ SUCCÈS")
    print("=" * 80)
    print(f"📊 {message}")
    print(f"📄 Fichier: {json_path}")
    
    # Afficher les résultats
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    characters = data.get('characters', [])
    if characters:
        print(f"\n🎯 Personnages trouvés:\n")
        for char in characters:
            print(f"  • {char['name']} - {char['class']} ({char['race']})")
            print(f"    Guilde: {char['guild']}")
            print(f"    URL: {char['url']}")
            print()
else:
    print("❌ ÉCHEC")
    print("=" * 80)
    print(f"Message: {message}")

print("=" * 80)
