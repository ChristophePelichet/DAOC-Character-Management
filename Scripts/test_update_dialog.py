#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de la fenêtre de validation avec affichage de tous les champs
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from UI.dialogs import CharacterUpdateDialog

def test_update_dialog():
    """Teste la fenêtre de validation avec toutes les lignes colorées"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Data actuelles (anciennes)
    current_data = {
        'name': 'TestChar',
        'level': 50,
        'class': 'Shaman',
        'race': 'Kobold',
        'realm': 'Midgard',
        'guild': 'Old Guild Name',  # DIFFÉRENT
        'realm_points': 200000,  # DIFFÉRENT
        'realm_rank': '3L5',  # DIFFÉRENT
        'server': 'Eden'  # IDENTIQUE
    }
    
    # Nouvelles Data (depuis Herald)
    new_data = {
        'name': 'TestChar',
        'clean_name': 'TestChar',
        'level': 50,  # IDENTIQUE
        'class': 'Shaman',  # IDENTIQUE
        'race': 'Kobold',  # IDENTIQUE
        'realm': 'Midgard',  # IDENTIQUE
        'guild': 'Deathwish',  # NOUVEAU
        'realm_points': 250994,  # NOUVEAU
        'realm_rank': '4L1',  # NOUVEAU
        'realm_title': 'Elding Vakten',
        'server': 'Eden',  # IDENTIQUE
        'url': 'https://eden-daoc.net/herald?n=player&k=TestChar',
        'rank': '1'
    }
    
    print("🔍 Test de la fenêtre de validation")
    print("=" * 80)
    print("\n📊 Résumé des données:")
    print("\nChamps IDENTIQUES (affichés en vert avec ✓):")
    print("  - Niveau: 50")
    print("  - Classe: Shaman")
    print("  - Race: Kobold")
    print("  - Royaume: Midgard")
    print("  - Serveur: Eden")
    
    print("\nChamps MODIFIÉS (affichés en rouge → vert):")
    print("  - Guilde: 'Old Guild Name' → 'Deathwish'")
    print("  - Points de Royaume: 200000 → 250994")
    print("  - Rang de Royaume: '3L5' → '4L1'")
    
    print("\n" + "=" * 80)
    print("📋 Ouverture de la fenêtre de validation...")
    print("=" * 80)
    
    # Create and afficher the dialogue
    dialog = CharacterUpdateDialog(None, current_data, new_data, 'TestChar')
    result = dialog.exec()
    
    if result:
        selected = dialog.get_selected_changes()
        print("\n✅ Modifications acceptées:")
        for field, value in selected.items():
            print(f"  - {field}: {value}")
    else:
        print("\n❌ Modifications annulées")
    
    print("\n" + "=" * 80)
    print("✅ Test terminé")
    print("=" * 80)

if __name__ == '__main__':
    test_update_dialog()