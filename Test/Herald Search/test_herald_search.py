#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour la fonction de recherche Herald
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.eden_scraper import search_herald_character
from Functions.cookie_manager import CookieManager

def main():
    print("\n" + "=" * 80)
    print("🔍 TEST DE RECHERCHE HERALD")
    print("=" * 80)
    
    # Vérifier les cookies
    print("\n📋 Vérification des cookies...")
    cookie_manager = CookieManager()
    
    if not cookie_manager.cookie_exists():
        print("❌ Aucun cookie trouvé. Veuillez générer ou importer des cookies d'abord.")
        return
    
    info = cookie_manager.get_cookie_info()
    print(f"✅ Cookies trouvés: {info['total_cookies']} cookie(s)")
    print(f"   Valide: {'✅ Oui' if info['is_valid'] else '❌ Non'}")
    if info.get('expiry_date'):
        print(f"   Expiration: {info['expiry_date']}")
    
    # Demander le nom du personnage
    print("\n" + "=" * 80)
    character_name = input("👉 Entrez le nom du personnage à rechercher: ").strip()
    
    if not character_name:
        print("❌ Nom vide. Abandon.")
        return
    
    # Lancer la recherche
    print(f"\n🔍 Recherche de '{character_name}' en cours...")
    print("⏳ Veuillez patienter...")
    
    success, message, json_path = search_herald_character(character_name)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ SUCCÈS")
        print("=" * 80)
        print(f"📊 {message}")
        print(f"📄 Fichier JSON: {json_path}")
        print("\n💡 Utilisez Scripts/view_search_results.py pour voir les résultats")
    else:
        print("❌ ÉCHEC")
        print("=" * 80)
        print(f"Message: {message}")
    
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
