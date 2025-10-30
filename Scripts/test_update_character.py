#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour afficher les modifications détectées lors d'une mise à jour depuis Herald
"""

import sys
import json
import logging
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def load_character(character_path):
    """Charge les données d'un personnage depuis son fichier JSON"""
    with open(character_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_data(current_data, new_data):
    """Compare les données actuelles avec les nouvelles données et affiche les différences"""
    
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
    
    print("\n" + "="*80)
    print(f"COMPARAISON DES DONNÉES POUR: {current_data.get('name', 'Inconnu')}")
    print("="*80)
    
    print("\n📊 DONNÉES ACTUELLES:")
    print("-" * 80)
    for field, label in fields_to_check.items():
        value = current_data.get(field, '(non défini)')
        print(f"  {label:25} : {value}")
    
    print("\n📥 NOUVELLES DONNÉES RÉCUPÉRÉES:")
    print("-" * 80)
    for field, label in fields_to_check.items():
        value = new_data.get(field, '(non défini)')
        print(f"  {label:25} : {value}")
    
    print("\n🔍 DIFFÉRENCES DÉTECTÉES:")
    print("-" * 80)
    
    changes = []
    for field, label in fields_to_check.items():
        current_value = current_data.get(field, '')
        new_value = new_data.get(field, '')
        
        # Normaliser les valeurs
        if isinstance(current_value, (int, float)):
            current_value_str = str(current_value)
        else:
            current_value_str = str(current_value) if current_value else ''
        
        if isinstance(new_value, (int, float)):
            new_value_str = str(new_value)
        else:
            new_value_str = str(new_value) if new_value else ''
        
        if current_value_str != new_value_str and new_value_str:
            changes.append({
                'field': field,
                'label': label,
                'current': current_value_str or '(vide)',
                'new': new_value_str
            })
            print(f"  ✓ {label:25} : {current_value_str or '(vide)':15} → {new_value_str}")
    
    if not changes:
        print("  ℹ️  Aucune modification détectée")
    
    print("\n" + "="*80)
    
    return changes

def main():
    """Fonction principale du script de test"""
    
    # Chemin vers le fichier du personnage
    character_path = Path(__file__).parent.parent / "Characters" / "S1" / "Hibernia" / "Ewo.json"
    
    if not character_path.exists():
        print(f"❌ Erreur: Le fichier {character_path} n'existe pas")
        return
    
    print("📁 Chargement du personnage...")
    current_data = load_character(character_path)
    print(f"✅ Personnage chargé: {current_data['name']}")
    
    url = current_data.get('url', '')
    if not url:
        print("❌ Erreur: Aucune URL Herald configurée pour ce personnage")
        return
    
    print(f"\n🌐 URL Herald: {url}")
    print("\n⏳ Récupération des données depuis Herald...")
    print("   (Le navigateur va s'ouvrir et se minimiser)")
    
    # Import dynamique pour éviter les erreurs de module
    from Functions.eden_scraper import scrape_character_from_url
    from Functions.cookie_manager import CookieManager
    
    # Créer le gestionnaire de cookies
    cookie_manager = CookieManager()
    
    # Récupérer les données depuis Herald
    success, new_data, error_msg = scrape_character_from_url(url, cookie_manager)
    
    if not success:
        print(f"\n❌ Erreur lors de la récupération: {error_msg}")
        return
    
    print("\n✅ Données récupérées avec succès!")
    
    # Afficher les données brutes récupérées (avant parsing)
    print("\n📦 DONNÉES BRUTES HERALD (avant parsing):")
    print("-" * 80)
    if 'tables' in new_data:
        print(f"Nombre de tableaux trouvés: {len(new_data.get('tables', []))}")
        for i, table in enumerate(new_data.get('tables', []), 1):
            print(f"\n  Tableau {i}:")
            for row in table[:10]:  # Limiter à 10 premières lignes
                print(f"    {row}")
            if len(table) > 10:
                print(f"    ... et {len(table) - 10} lignes supplémentaires")
    
    if 'h1' in new_data:
        print(f"\nTitres H1: {new_data['h1']}")
    if 'h2' in new_data:
        print(f"Titres H2: {new_data['h2']}")
    if 'h3' in new_data:
        print(f"Titres H3: {new_data['h3']}")
    
    # Afficher les données parsées
    print("\n📦 DONNÉES PARSÉES:")
    print("-" * 80)
    print(json.dumps(new_data, indent=2, ensure_ascii=False))
    
    # Comparer les données
    changes = compare_data(current_data, new_data)
    
    # Résumé
    print(f"\n📊 RÉSUMÉ:")
    print(f"   Nombre de champs comparés: {len(['level', 'class', 'race', 'realm', 'guild', 'realm_points', 'realm_rank', 'realm_level', 'server'])}")
    print(f"   Nombre de modifications: {len(changes)}")
    
    if changes:
        print("\n⚠️  ATTENTION: Des incohérences ont été détectées!")
        print("   Vérifiez que les données extraites correspondent bien à la page Herald.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
