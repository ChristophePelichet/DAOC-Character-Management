#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la correction du rang de royaume
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_realm_rank_fix():
    """Teste que le rang de royaume est correctement inversé"""
    
    from Functions.eden_scraper import search_herald_character
    import json
    
    # Chercher un personnage
    character_name = "Adiseasewoman"  # Nom du dernier JSON valide
    
    print(f"🔍 Test de la correction du rang de royaume")
    print(f"Personnage: {character_name}")
    print("=" * 80)
    
    # Faire une recherche
    print("\n📡 Recherche du personnage sur Herald...")
    success, message, characters_file = search_herald_character(character_name)
    
    if not success:
        print(f"\n❌ Erreur: {message}")
        return
    
    print(f"✅ Recherche réussie: {message}")
    
    # Charger les résultats
    with open(characters_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    characters = results.get('characters', [])
    
    if not characters:
        print("❌ Aucun personnage trouvé!")
        return
    
    # Prendre le premier personnage
    char_data = characters[0]
    
    print("\n" + "=" * 80)
    print("� DONNÉES BRUTES DU JSON (avant normalisation):")
    print("=" * 80)
    
    print(f"\n🔹 Nom: {char_data.get('name')}")
    print(f"🔹 Classe: {char_data.get('class')}")
    print(f"🔹 Race: {char_data.get('race')}")
    print(f"🔹 Level: {char_data.get('level')}")
    print(f"🔹 Guilde: {char_data.get('guild')}")
    print(f"🔹 Points de Royaume: {char_data.get('realm_points')}")
    
    print(f"\n🔸 CHAMPS BRUTS DU JSON:")
    print(f"   realm_rank = '{char_data.get('realm_rank')}'")
    print(f"   realm_level = '{char_data.get('realm_level')}'")
    
    # Normaliser les données
    from Functions.eden_scraper import _normalize_herald_data
    normalized = _normalize_herald_data(char_data)
    
    print("\n" + "=" * 80)
    print("📊 DONNÉES NORMALISÉES (après correction):")
    print("=" * 80)
    
    print(f"\n🔹 Nom: {normalized.get('name')}")
    print(f"🔹 Classe: {normalized.get('class')}")
    print(f"🔹 Race: {normalized.get('race')}")
    print(f"🔹 Royaume: {normalized.get('realm')}")
    print(f"🔹 Level: {normalized.get('level')}")
    print(f"🔹 Guilde: {normalized.get('guild')}")
    print(f"🔹 Serveur: {normalized.get('server')}")
    print(f"� Points de Royaume: {normalized.get('realm_points')}")
    
    # LES CHAMPS CRITIQUES À VÉRIFIER
    realm_rank = normalized.get('realm_rank', '')
    realm_title = normalized.get('realm_title', '')
    
    print(f"\n🎯 RANG DE ROYAUME (CODE) - Utilisé dans le programme:")
    print(f"   realm_rank = '{realm_rank}'")
    print(f"   Format attendu: XLY (ex: 5L2, 4L1)")
    
    # Vérifier le format
    import re
    if re.match(r'^\d+L\d+$', realm_rank):
        print(f"   ✅ Format correct!")
    else:
        print(f"   ❌ Format INCORRECT! Devrait être XLY, pas un titre texte")
    
    print(f"\n🎯 TITRE DE ROYAUME (TEXTE) - Pour affichage:")
    print(f"   realm_title = '{realm_title}'")
    print(f"   Format attendu: Texte (ex: 'Stormur Vakten', 'Elding Vakten')")
    
    if realm_title and not re.match(r'^\d+L\d+$', realm_title):
        print(f"   ✅ Format correct!")
    else:
        print(f"   ⚠️  Titre vide ou format bizarre")
    
    print("\n" + "=" * 80)
    print("📋 TOUTES LES DONNÉES NORMALISÉES:")
    print("=" * 80)
    print(json.dumps(normalized, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("✅ Test terminé")
    print("=" * 80)

if __name__ == '__main__':
    test_realm_rank_fix()
