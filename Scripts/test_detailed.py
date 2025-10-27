"""Script de diagnostic détaillé pour comprendre le problème des icônes"""
import os
import sys

# Configuration du chemin
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print("=" * 70)
print("DIAGNOSTIC DÉTAILLÉ - Chargement des icônes de royaume")
print("=" * 70)

# Import des modules
print("\n1. Import des modules...")
try:
    from Functions.character_manager import REALM_ICONS
    from Functions.logging_manager import get_img_dir
    print("   ✓ Modules importés avec succès")
except Exception as e:
    print(f"   ✗ Erreur d'import: {e}")
    sys.exit(1)

# Test de REALM_ICONS
print("\n2. Analyse de REALM_ICONS:")
print(f"   Type: {type(REALM_ICONS)}")
print(f"   Contenu: {REALM_ICONS}")
print(f"   Longueur: {len(REALM_ICONS)}")
print(f"   bool(REALM_ICONS): {bool(REALM_ICONS)}")
print(f"   not REALM_ICONS: {not REALM_ICONS}")

if not REALM_ICONS:
    print("   ❌ PROBLÈME: 'if not REALM_ICONS' est VRAI")
    print("   => Le code va retourner sans charger les icônes!")
else:
    print("   ✓ OK: 'if not REALM_ICONS' est FAUX")
    print("   => Le code va charger les icônes")

# Test du répertoire d'images
print("\n3. Vérification du répertoire d'images:")
img_dir = get_img_dir()
print(f"   Chemin: {img_dir}")
print(f"   Existe: {os.path.exists(img_dir)}")

# Test de chaque icône
print("\n4. Test de création des QIcon (simulation):")
try:
    # Essayer d'importer PySide6
    try:
        from PySide6.QtGui import QIcon
        print("   ✓ PySide6.QtGui.QIcon importé")
        pyside_available = True
    except ImportError:
        print("   ⚠️  PySide6 non disponible (normal si pas installé)")
        print("   => Simulation sans QIcon")
        pyside_available = False
    
    tree_realm_icons = {}
    
    for realm, icon_path in REALM_ICONS.items():
        full_path = os.path.join(img_dir, icon_path)
        exists = os.path.exists(full_path)
        
        print(f"\n   Royaume: {realm}")
        print(f"   Fichier: {icon_path}")
        print(f"   Chemin complet: {full_path}")
        print(f"   Existe: {exists}")
        
        if exists:
            size = os.path.getsize(full_path)
            print(f"   Taille: {size} octets")
            
            if pyside_available:
                try:
                    icon = QIcon(full_path)
                    is_null = icon.isNull()
                    tree_realm_icons[realm] = icon
                    print(f"   QIcon créé: {not is_null}")
                    print(f"   isNull: {is_null}")
                except Exception as e:
                    print(f"   ✗ Erreur création QIcon: {e}")
                    tree_realm_icons[realm] = None
            else:
                tree_realm_icons[realm] = "SIMULATED"
                print(f"   [SIMULÉ] QIcon serait créé")
        else:
            print(f"   ✗ ERREUR: Fichier non trouvé!")
            tree_realm_icons[realm] = None
    
    print(f"\n5. Résultat final:")
    print(f"   tree_realm_icons: {list(tree_realm_icons.keys())}")
    print(f"   Nombre d'icônes chargées: {len([v for v in tree_realm_icons.values() if v is not None])}")
    
    # Test d'utilisation dans le tree
    print(f"\n6. Simulation d'utilisation dans refresh_character_list():")
    test_realms = ["Albion", "Hibernia", "Midgard", "Inexistant"]
    for realm in test_realms:
        icon = tree_realm_icons.get(realm)
        print(f"   realm='{realm}' => icon found: {icon is not None}")
        if icon and pyside_available:
            print(f"      isNull: {icon.isNull()}")
    
except Exception as e:
    print(f"\n   ✗ ERREUR lors des tests: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("FIN DU DIAGNOSTIC")
print("=" * 70)
