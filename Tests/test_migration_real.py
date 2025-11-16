"""
Test de migration en conditions réelles
Teste la migration du config.json actuel
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.config_manager import ConfigManager

print("=" * 70)
print("TEST DE MIGRATION - CONFIG.JSON RÉEL")
print("=" * 70)
print()

# Test 1: Load config (triggers migration if needed)
print("📂 Chargement de la configuration...")
config = ConfigManager()

print()
print("=" * 70)
print("TESTS D'ACCÈS AUX VALEURS")
print("=" * 70)
print()

# Test 2: Access with new dotted notation
print("✅ Test notation pointée (v2):")
print(f"  - ui.language = {config.get('ui.language')}")
print(f"  - ui.theme = {config.get('ui.theme')}")
print(f"  - folders.characters = {config.get('folders.characters')}")
print(f"  - backup.characters.enabled = {config.get('backup.characters.enabled')}")
print(f"  - system.debug_mode = {config.get('system.debug_mode')}")

print()

# Test 3: Access with legacy keys (backward compatibility)
print("✅ Test clés legacy (v1 - rétrocompatibilité):")
print(f"  - language = {config.get('language')}")
print(f"  - theme = {config.get('theme')}")
print(f"  - character_folder = {config.get('character_folder')}")
print(f"  - backup_enabled = {config.get('backup_enabled')}")
print(f"  - debug_mode = {config.get('debug_mode')}")

print()

# Test 4: Get sections
print("✅ Test accès sections complètes:")
ui_section = config.get_section('ui')
print(f"  - Section UI: {len(ui_section)} clés")
folders_section = config.get_section('folders')
print(f"  - Section Folders: {len(folders_section)} clés")
backup_section = config.get_section('backup')
print(f"  - Section Backup: {len(backup_section)} sous-sections")

print()

# Test 5: Verify structure
print("=" * 70)
print("VÉRIFICATION DE LA STRUCTURE")
print("=" * 70)
print()

expected_sections = ["ui", "folders", "backup", "system", "game"]
for section in expected_sections:
    exists = section in config.config
    status = "✅" if exists else "❌"
    print(f"{status} Section '{section}': {'Présente' if exists else 'Manquante'}")

print()

# Test 6: Verify backup subsections
backup_subsections = ["characters", "cookies", "armor"]
for subsection in backup_subsections:
    exists = subsection in config.config.get("backup", {})
    status = "✅" if exists else "❌"
    print(f"{status} Backup '{subsection}': {'Présent' if exists else 'Manquant'}")

print()

# Test 7: Verify critical values preserved
print("=" * 70)
print("VÉRIFICATION DES VALEURS CRITIQUES")
print("=" * 70)
print()

critical_checks = [
    ("Langue", config.get('ui.language'), "fr"),
    ("Thème", config.get('ui.theme'), "default"),
    ("Dossier personnages", config.get('folders.characters') is not None, True),
    ("Backup activé", config.get('backup.characters.enabled'), True),
    ("Mode debug", config.get('system.debug_mode'), False),
]

all_ok = True
for name, actual, expected in critical_checks:
    ok = actual == expected
    status = "✅" if ok else "❌"
    print(f"{status} {name}: {actual} {'(OK)' if ok else f'(Attendu: {expected})'}")
    if not ok:
        all_ok = False

print()

# Final summary
print("=" * 70)
print("RÉSULTAT FINAL")
print("=" * 70)
print()

if all_ok:
    print("✅ MIGRATION RÉUSSIE - Toutes les vérifications sont OK")
else:
    print("❌ PROBLÈME DÉTECTÉ - Vérifier les erreurs ci-dessus")

print()
print("💾 La configuration migrée a été sauvegardée dans config.json")
print("📋 L'ancienne version est dans config.json.manual_backup")
print()
