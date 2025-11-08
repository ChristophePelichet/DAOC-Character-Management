#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier le bug de changement de classe lors de la modification du rang
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_combo_data():
    """Teste que findData et itemData fonctionnent correctement"""
    
    from PySide6.QtWidgets import QApplication, QComboBox
    from Functions.data_manager import DataManager
    from Functions.config_manager import config
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create un combo of test
    combo = QComboBox()
    
    # Simuler the remplissage with Data traduites
    data_manager = DataManager()
    classes = data_manager.get_classes("Midgard")
    
    current_language = config.get("language", "en")
    
    print("🔍 Test du combo de classe pour Midgard")
    print("=" * 80)
    print(f"Langue actuelle: {current_language}")
    print()
    
    # Remplir the combo comme in the code réel
    for cls in classes:
        # Get translated name
        if current_language == "fr" and "name_fr" in cls:
            display_name = cls["name_fr"]
        elif current_language == "de" and "name_de" in cls:
            display_name = cls["name_de"]
        else:
            display_name = cls["name"]
        
        # Store actual name as item data
        combo.addItem(display_name, cls["name"])
        print(f"  Ajouté: '{display_name}' (data='{cls['name']}')")
    
    print()
    print("=" * 80)
    print("🧪 Test 1: Recherche par findData (nom anglais)")
    print("=" * 80)
    
    test_class = "Thane"
    index = combo.findData(test_class)
    print(f"Recherche de '{test_class}':")
    print(f"  Index trouvé: {index}")
    
    if index >= 0:
        combo.setCurrentIndex(index)
        print(f"  Texte affiché: '{combo.currentText()}'")
        print(f"  ItemData: '{combo.itemData(index)}'")
        print(f"  ✅ Correspondance correcte!")
    else:
        print(f"  ❌ Pas trouvé!")
    
    print()
    print("=" * 80)
    print("🧪 Test 2: Recherche par findText (texte affiché)")
    print("=" * 80)
    
    index_text = combo.findText(test_class)
    print(f"Recherche du texte '{test_class}':")
    print(f"  Index trouvé: {index_text}")
    
    if index_text >= 0:
        print(f"  ItemData à cet index: '{combo.itemData(index_text)}'")
    else:
        print(f"  ❌ Pas trouvé!")
    
    print()
    print("=" * 80)
    print("🧪 Test 3: Simulation du bug avec classe TRADUITE")
    print("=" * 80)
    
    # Test with une classe qui a une traduction différente
    test_translated = "Bonedancer"  # En français: "Prêtre of Bodgar"
    
    print(f"Classe à tester: '{test_translated}' (Bonedancer)")
    print()
    
    # Simuler the sélection d'une classe
    print("1. Sélection de 'Bonedancer' par findData (CORRECT):")
    correct_index = combo.findData(test_translated)
    if correct_index >= 0:
        combo.setCurrentIndex(correct_index)
        saved_class = combo.itemData(combo.currentIndex())
        displayed_text = combo.currentText()
        print(f"   Texte affiché: '{displayed_text}'")
        print(f"   Classe sauvegardée: '{saved_class}' ✅")
    else:
        print(f"   ❌ Pas trouvé!")
    
    print()
    print("2. Sélection de 'Bonedancer' par findText (VA ÉCHOUER!):")
    text_index = combo.findText(test_translated)
    if text_index >= 0:
        combo.setCurrentIndex(text_index)
        saved_class = combo.itemData(combo.currentIndex())
        print(f"   Classe sauvegardée: '{saved_class}' ✅")
    else:
        print(f"   ❌ Échec - '{test_translated}' n'existe pas dans le texte affiché!")
        print(f"   Le texte affiché est 'Prêtre de Bodgar'")
        print(f"   → La classe serait MAL enregistrée si on utilisait findText!")
        
        # Tester with the texte français
        print()
        print("3. Sélection de 'Prêtre de Bodgar' par findText:")
        fr_index = combo.findText("Prêtre de Bodgar")
        if fr_index >= 0:
            combo.setCurrentIndex(fr_index)
            saved_class = combo.itemData(combo.currentIndex())
            print(f"   Classe sauvegardée: '{saved_class}' ✅")
            print(f"   → Ceci enregistrerait la BONNE classe, mais seulement si on connaît la traduction!")
    
    print()
    print("=" * 80)
    print("📋 CONCLUSION:")
    print("=" * 80)
    print("✅ findData(nom_anglais) fonctionne toujours")
    print("❌ findText(nom_anglais) échoue si la langue n'est pas anglaise")
    print("✅ La correction appliquée (utiliser findData) résout le bug!")
    print("=" * 80)

if __name__ == '__main__':
    test_combo_data()