"""
Script de test pour vérifier la détection de migration lors du changement de chemin
du dossier Characters dans la configuration.

Ce script simule le scénario où l'utilisateur change le chemin du dossier Characters
vers un dossier qui utilise l'ancienne structure (Characters/Realm/) au lieu de la
nouvelle structure (Characters/Season/Realm/).
"""

import sys
import os

# Ajouter le dossier parent au PYTHONPATH pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.config_manager import config
from Functions.migration_manager import check_migration_needed, is_migration_done
from Functions.path_manager import get_base_path

def test_migration_detection():
    """Test de la détection de migration nécessaire."""
    print("=" * 70)
    print("TEST: Détection de migration lors du changement de chemin")
    print("=" * 70)
    
    # 1. Afficher le chemin actuel
    current_path = config.get("character_folder", "")
    print(f"\n1. Chemin actuel du dossier Characters:")
    print(f"   {current_path}")
    
    # 2. Vérifier l'état actuel
    print(f"\n2. État de la migration actuelle:")
    print(f"   - Migration nécessaire: {check_migration_needed()}")
    print(f"   - Migration effectuée: {is_migration_done()}")
    
    # 3. Créer un dossier de test avec l'ancienne structure
    base_path = get_base_path()
    test_path = os.path.join(base_path, "Characters_Test_Old_Structure")
    
    print(f"\n3. Création d'un dossier test avec ancienne structure:")
    print(f"   {test_path}")
    
    # Créer la structure: Characters_Test_Old_Structure/Albion/
    os.makedirs(os.path.join(test_path, "Albion"), exist_ok=True)
    os.makedirs(os.path.join(test_path, "Hibernia"), exist_ok=True)
    os.makedirs(os.path.join(test_path, "Midgard"), exist_ok=True)
    
    # Créer un fichier JSON test dans Albion
    test_file = os.path.join(test_path, "Albion", "TestChar.json")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write('{"name": "TestChar", "realm": "Albion", "level": 1}')
    
    print("   ✅ Structure créée avec succès")
    
    # 4. Simuler le changement de chemin
    print(f"\n4. Simulation du changement de chemin:")
    old_char_folder = config.get("character_folder", "")
    config.set("character_folder", test_path)
    print(f"   Ancien chemin: {old_char_folder}")
    print(f"   Nouveau chemin: {test_path}")
    
    # 5. Vérifier si migration est nécessaire sur le nouveau chemin
    print(f"\n5. Vérification de la migration sur le nouveau chemin:")
    migration_needed = check_migration_needed()
    migration_done = is_migration_done()
    print(f"   - Migration nécessaire: {migration_needed}")
    print(f"   - Migration effectuée: {migration_done}")
    
    # 6. Résultat attendu
    print(f"\n6. Résultat:")
    if migration_needed and not migration_done:
        print("   ✅ SUCCÈS: La migration est correctement détectée comme nécessaire")
        print("   ℹ️  L'utilisateur devrait voir un popup d'avertissement")
    elif not migration_needed:
        print("   ⚠️  ATTENTION: Aucune migration détectée (structure déjà correcte?)")
    elif migration_done:
        print("   ⚠️  ATTENTION: Migration marquée comme effectuée")
    else:
        print("   ❌ ERREUR: État inattendu")
    
    # 7. Restaurer la configuration
    print(f"\n7. Restauration de la configuration:")
    config.set("character_folder", old_char_folder)
    print(f"   Configuration restaurée à: {old_char_folder}")
    
    # 8. Nettoyage optionnel
    print(f"\n8. Nettoyage:")
    print(f"   Le dossier test reste à: {test_path}")
    print(f"   Vous pouvez le supprimer manuellement si nécessaire")
    
    print("\n" + "=" * 70)
    print("FIN DU TEST")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_migration_detection()
    except Exception as e:
        print(f"\n❌ ERREUR lors du test: {e}")
        import traceback
        traceback.print_exc()
