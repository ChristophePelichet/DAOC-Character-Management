#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test complet pour la mise à jour d'un personnage
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_update_full():
    """Teste la mise à jour complète avec détection des changements"""
    
    from Functions.eden_scraper import scrape_character_from_url
    from Functions.cookie_manager import CookieManager
    import json
    
    # URL de test
    url = "https://eden-daoc.net/herald?n=player&k=Odamuss"
    
    # Données actuelles du personnage (simulées - anciennes données)
    current_data = {
        'name': 'Odamuss',
        'level': 50,
        'class': 'Thane',
        'race': 'Troll',
        'realm': 'Midgard',
        'guild': 'Old Guild Name',  # Différent
        'realm_points': 600000,  # Différent
        'realm_rank': 'Old Rank',  # Différent
        'realm_level': '5L1',  # Différent
        'server': 'Eden'
    }
    
    print(f"🔍 Test de mise à jour complète")
    print(f"URL: {url}")
    print("=" * 80)
    print("\n📋 Données ACTUELLES (simulées):")
    print(json.dumps(current_data, indent=2, ensure_ascii=False))
    
    # Initialiser le cookie manager
    cookie_manager = CookieManager()
    
    # Vérifier les cookies
    if not cookie_manager.cookie_exists():
        print("\n❌ Aucun cookie trouvé!")
        return
    
    print("\n✅ Cookies trouvés")
    
    # Récupérer les nouvelles données
    print("\n📡 Récupération des données depuis Herald...")
    success, new_data, error_msg = scrape_character_from_url(url, cookie_manager)
    
    if not success:
        print(f"\n❌ Erreur: {error_msg}")
        return
    
    print("\n✅ Données récupérées!")
    print("\n📋 Données NOUVELLES (depuis Herald):")
    print(json.dumps(new_data, indent=2, ensure_ascii=False))
    
    # Détecter les changements
    print("\n" + "=" * 80)
    print("🔍 DÉTECTION DES CHANGEMENTS:")
    print("=" * 80)
    
    fields_to_check = {
        'level': 'Niveau',
        'class': 'Classe',
        'race': 'Race',
        'realm': 'Royaume',
        'guild': 'Guilde',
        'realm_points': 'Points de Royaume',
        'realm_rank': 'Rang de Royaume',
        'realm_level': 'Niveau de Royaume',
        'server': 'Serveur'
    }
    
    changes_found = False
    for field, label in fields_to_check.items():
        current_value = current_data.get(field, '')
        new_value = new_data.get(field, '')
        
        # Normaliser pour la comparaison
        current_str = str(current_value) if current_value is not None else ''
        new_str = str(new_value) if new_value is not None else ''
        
        if current_str != new_str and new_str:
            print(f"\n🔄 {label}:")
            print(f"   Actuel: {current_str}")
            print(f"   Nouveau: {new_str}")
            changes_found = True
    
    if not changes_found:
        print("\n✅ Aucun changement détecté - Les données sont à jour")
    else:
        print("\n" + "=" * 80)
        print("✅ Test réussi - Changements détectés correctement")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_update_full()
