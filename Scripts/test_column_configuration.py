"""
Test de la configuration des colonnes visibles
"""

import sys
from PySide6.QtWidgets import QApplication
from main import CharacterApp

def test_column_visibility():
    """Teste la fonctionnalité de configuration des colonnes."""
    print("🧪 Test de la configuration des colonnes")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    window = CharacterApp()
    
    # Vérifier que la méthode existe
    assert hasattr(window, 'apply_column_visibility'), "❌ Méthode apply_column_visibility non trouvée"
    print("✅ Méthode apply_column_visibility existe")
    
    assert hasattr(window, 'open_columns_configuration'), "❌ Méthode open_columns_configuration non trouvée"
    print("✅ Méthode open_columns_configuration existe")
    
    # Vérifier que l'action existe
    assert hasattr(window, 'columns_action'), "❌ Action columns_action non trouvée"
    print("✅ Action columns_action existe")
    
    # Vérifier la configuration initiale
    from Functions.config_manager import config
    visibility = config.get("column_visibility", {})
    print(f"\n📋 Configuration actuelle des colonnes :")
    if visibility:
        for key, value in visibility.items():
            status = "✅ Visible" if value else "❌ Masquée"
            print(f"   - {key}: {status}")
    else:
        print("   Aucune configuration personnalisée (toutes visibles par défaut)")
    
    # Vérifier que le TreeView existe
    assert hasattr(window, 'character_tree'), "❌ TreeView non trouvé"
    print("\n✅ TreeView trouvé")
    
    # Compter les colonnes
    model = window.tree_model
    column_count = model.columnCount()
    print(f"📊 Nombre de colonnes dans le modèle : {column_count}")
    
    expected_columns = 8  # selection, realm, season, server, name, level, realm_rank, realm_title
    assert column_count == expected_columns, f"❌ Nombre de colonnes incorrect (attendu {expected_columns}, obtenu {column_count})"
    print(f"✅ Nombre de colonnes correct ({expected_columns})")
    
    # Afficher les headers
    print(f"\n📋 En-têtes des colonnes :")
    for i in range(column_count):
        header = model.horizontalHeaderItem(i)
        if header:
            print(f"   {i}: {header.text()}")
    
    print("\n" + "=" * 50)
    print("✅ Tous les tests sont passés avec succès !")
    print("\n💡 Pour tester l'interface :")
    print("   1. Lancez l'application : python main.py")
    print("   2. Cliquez sur le bouton 'Colonnes' dans la toolbar")
    print("   3. Décochez certaines colonnes et validez")
    print("   4. Vérifiez que les colonnes sont masquées")
    print("   5. Redémarrez l'application")
    print("   6. Vérifiez que la configuration est conservée")
    
    return True

if __name__ == "__main__":
    try:
        test_column_visibility()
    except AssertionError as e:
        print(f"\n❌ Échec du test : {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
