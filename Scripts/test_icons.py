"""Script de test pour vérifier le chargement des icônes"""
import os
import sys
import logging

# Configuration du logging pour le test
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s'
)

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from Functions.character_manager import REALM_ICONS
from Functions.logging_manager import get_img_dir

print("=" * 60)
print("Test de chargement des icônes de royaume")
print("=" * 60)

print(f"\n1. Contenu de REALM_ICONS:")
print(f"   Type: {type(REALM_ICONS)}")
print(f"   Contenu: {REALM_ICONS}")
print(f"   Est vide (not REALM_ICONS): {not REALM_ICONS}")
print(f"   Booléen (bool(REALM_ICONS)): {bool(REALM_ICONS)}")
print(f"   Nombre d'éléments: {len(REALM_ICONS)}")

print(f"\n2. Répertoire des images:")
img_dir = get_img_dir()
print(f"   Chemin: {img_dir}")
print(f"   Existe: {os.path.exists(img_dir)}")

if os.path.exists(img_dir):
    print(f"\n3. Contenu du répertoire Img:")
    files = os.listdir(img_dir)
    for item in sorted(files):
        print(f"   - {item}")
    print(f"   Total: {len(files)} fichier(s)")

print(f"\n4. Vérification détaillée de chaque icône:")
all_ok = True
for realm, icon_filename in REALM_ICONS.items():
    full_path = os.path.join(img_dir, icon_filename)
    exists = os.path.exists(full_path)
    if exists:
        size = os.path.getsize(full_path)
        print(f"   ✓ {realm}: {icon_filename}")
        print(f"     Chemin: {full_path}")
        print(f"     Taille: {size} octets")
    else:
        print(f"   ✗ {realm}: {icon_filename}")
        print(f"     ERREUR: Fichier non trouvé à {full_path}")
        all_ok = False

print(f"\n5. Test de simulation du chargement:")
try:
    # Simuler le test de la condition dans _load_icons()
    if not REALM_ICONS:
        print("   ✗ PROBLÈME: La condition 'if not REALM_ICONS' serait VRAIE")
        print("     Les icônes ne seraient PAS chargées!")
    else:
        print("   ✓ OK: La condition 'if not REALM_ICONS' est FAUSSE")
        print("     Les icônes seront chargées correctement")
except Exception as e:
    print(f"   ✗ ERREUR lors du test: {e}")
    all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("✓ RÉSULTAT: Tous les tests sont passés avec succès!")
else:
    print("✗ RÉSULTAT: Certains tests ont échoué!")
print("=" * 60)

