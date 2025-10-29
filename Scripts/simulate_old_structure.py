"""
Script de test pour simuler une ancienne structure et tester la migration.

Ce script :
1. Sauvegarde la structure actuelle
2. Supprime le marqueur .migration_done
3. Crée une structure ancienne avec des personnages de test
4. Permet de tester le popup de confirmation et la migration

ATTENTION : Utiliser uniquement pour les tests !
"""

import os
import json
import shutil
from datetime import datetime

def simulate_old_structure():
    """Crée une structure ancienne pour tester la migration."""
    
    # Déterminer le chemin du dossier Characters
    base_path = os.path.dirname(os.path.abspath(__file__))
    characters_path = os.path.join(base_path, "Characters")
    
    print("=" * 60)
    print("SIMULATION DE L'ANCIENNE STRUCTURE")
    print("=" * 60)
    
    # Sauvegarder la structure actuelle si elle existe
    if os.path.exists(characters_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"Characters_before_test_{timestamp}"
        backup_path = os.path.join(base_path, backup_name)
        
        print(f"\n1. Sauvegarde de la structure actuelle...")
        print(f"   → {backup_path}")
        shutil.copytree(characters_path, backup_path)
        print("   ✓ Sauvegarde créée")
        
        # Supprimer la structure actuelle
        print(f"\n2. Suppression de la structure actuelle...")
        shutil.rmtree(characters_path)
        print("   ✓ Structure supprimée")
    
    # Créer l'ancienne structure
    print(f"\n3. Création de l'ancienne structure...")
    os.makedirs(characters_path, exist_ok=True)
    
    # Créer des personnages de test dans l'ancienne structure
    realms = ["Albion", "Hibernia", "Midgard"]
    
    for realm in realms:
        realm_path = os.path.join(characters_path, realm)
        os.makedirs(realm_path, exist_ok=True)
        
        # Créer 2 personnages de test par royaume
        for i in range(1, 3):
            character_name = f"Test_{realm}_{i}"
            character_file = os.path.join(realm_path, f"{character_name}.json")
            
            character_data = {
                "name": character_name,
                "realm": realm,
                "level": 50,
                "class": "Warrior",
                "race": "Human",
                "server": "TestServer",
                "guild": "TestGuild",
                "side": 1,
                "realm_points": 100000
            }
            
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=4, ensure_ascii=False)
            
            print(f"   ✓ {character_name}.json créé dans {realm}/")
    
    # Supprimer le marqueur de migration si présent
    migration_flag = os.path.join(characters_path, ".migration_done")
    if os.path.exists(migration_flag):
        os.remove(migration_flag)
        print(f"\n4. Marqueur de migration supprimé")
    
    print("\n" + "=" * 60)
    print("STRUCTURE ANCIENNE CRÉÉE AVEC SUCCÈS")
    print("=" * 60)
    print("\nStructure créée :")
    print("Characters/")
    for realm in realms:
        print(f"├── {realm}/")
        print(f"│   ├── Test_{realm}_1.json")
        print(f"│   └── Test_{realm}_2.json")
    
    print("\nVous pouvez maintenant lancer l'application pour tester la migration.")
    print("Le popup de confirmation devrait s'afficher au démarrage.")
    print("\nPour restaurer votre structure originale, utilisez le dossier de sauvegarde créé.")

if __name__ == "__main__":
    response = input("ATTENTION : Ce script va remplacer votre structure actuelle.\nContinuer ? (oui/non) : ")
    if response.lower() in ['oui', 'yes', 'y', 'o']:
        simulate_old_structure()
    else:
        print("Opération annulée.")
