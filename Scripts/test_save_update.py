#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de la sauvegarde des modifications après mise à jour Herald
"""

import sys
from pathlib import Path
import json
import tempfile
import shutil

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_save_after_update():
    """Teste que les modifications sont bien sauvegardées"""
    
    from Functions.character_manager import save_character
    
    print("🔍 Test de sauvegarde après mise à jour")
    print("=" * 80)
    
    # Créer un personnage de test dans le dossier Characters réel
    test_char = {
        'id': 'TestUpdateChar',
        'uuid': 'test-uuid-123',
        'name': 'TestUpdateChar',
        'realm': 'Midgard',
        'race': 'Kobold',
        'class': 'Shaman',
        'level': 1,
        'season': 'S1',
        'server': 'Eden',
        'page': 1,
        'guild': 'Old Guild',
        'realm_rank': '1L1',
        'realm_points': 0,
        'url': 'https://eden-daoc.net/herald?n=player&k=TestUpdateChar'
    }
    
    print("\n📊 Données initiales du personnage:")
    print(f"  - Nom: {test_char['name']}")
    print(f"  - Guilde: {test_char['guild']}")
    print(f"  - Rang: {test_char['realm_rank']}")
    print(f"  - RP: {test_char['realm_points']}")
    print(f"  - Level: {test_char['level']}")
    
    # Sauvegarder le personnage initial
    print("\n💾 Sauvegarde initiale...")
    success, msg = save_character(test_char, allow_overwrite=False)
    
    if not success:
        # Si le fichier existe déjà, le supprimer et réessayer
        if "char_exists_error" in msg or "exists" in msg.lower():
            print(f"⚠️  Le fichier existe déjà, suppression...")
            from Functions.path_manager import get_base_path
            import os
            char_file = os.path.join(get_base_path(), "Characters", "S1", "Midgard", "TestUpdateChar.json")
            if os.path.exists(char_file):
                os.remove(char_file)
                print(f"🗑️  Fichier supprimé: {char_file}")
                success, msg = save_character(test_char, allow_overwrite=False)
            
    if not success:
        print(f"❌ Échec: {msg}")
        return
    
    print(f"✅ Sauvegarde réussie")
    
    # Vérifier le fichier créé
    from Functions.path_manager import get_base_path
    import os
    char_file = os.path.join(get_base_path(), "Characters", "S1", "Midgard", "TestUpdateChar.json")
    print(f"\n📂 Fichier créé: {char_file}")
    
    if not os.path.exists(char_file):
        print("❌ Le fichier n'a pas été créé!")
        return
    
    with open(char_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    print("\n✅ Données sauvegardées:")
    print(f"  - Guilde: {saved_data['guild']}")
    print(f"  - Rang: {saved_data['realm_rank']}")
    print(f"  - RP: {saved_data['realm_points']}")
    
    # Simuler une mise à jour Herald
    print("\n" + "=" * 80)
    print("🔄 SIMULATION DE MISE À JOUR HERALD")
    print("=" * 80)
    
    selected_changes = {
        'guild': 'New Guild Name',
        'realm_rank': '4L1',
        'realm_points': 250994,
        'level': 50
    }
    
    print("\n📝 Changements à appliquer:")
    for field, value in selected_changes.items():
        old_value = test_char.get(field, '(vide)')
        print(f"  - {field}: {old_value} → {value}")
    
    # Appliquer les changements (comme dans le code réel)
    for field, value in selected_changes.items():
        test_char[field] = value
    
    print("\n💾 Sauvegarde avec allow_overwrite=True...")
    success, msg = save_character(test_char, allow_overwrite=True)
    
    if not success:
        print(f"❌ Échec de la sauvegarde: {msg}")
        return
    
    print(f"✅ Sauvegarde réussie: {msg}")
    
    # Recharger le fichier pour vérifier
    print("\n📂 Vérification du fichier sauvegardé...")
    with open(char_file, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION DES DONNÉES SAUVEGARDÉES")
    print("=" * 80)
    
    all_correct = True
    for field, expected_value in selected_changes.items():
        actual_value = updated_data.get(field)
        match = (str(actual_value) == str(expected_value))
        
        status = "✅" if match else "❌"
        print(f"{status} {field}: {actual_value} (attendu: {expected_value})")
        
        if not match:
            all_correct = False
    
    print("\n" + "=" * 80)
    if all_correct:
        print("✅ SUCCÈS - Toutes les modifications ont été sauvegardées correctement!")
    else:
        print("❌ ÉCHEC - Certaines modifications n'ont pas été sauvegardées!")
    print("=" * 80)
    
    # Nettoyer
    print(f"\n🗑️  Nettoyage du fichier de test...")
    if os.path.exists(char_file):
        os.remove(char_file)
        print(f"✅ Fichier supprimé: {char_file}")

if __name__ == '__main__':
    test_save_after_update()
