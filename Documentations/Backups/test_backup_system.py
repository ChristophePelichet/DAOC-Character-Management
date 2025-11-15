"""
Script de test complet du système de backup
============================================

Ce script teste toutes les fonctionnalités du système de sauvegarde :
1. Création de backup au 1er démarrage quotidien
2. Compression ZIP ou copie selon configuration
3. Suppression automatique des vieux backups
4. Respect des limites de stockage
5. Mode illimité (-1)

Usage:
    python Tools/test_backup_system.py
"""

import os
import sys
import json
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.config_manager import ConfigManager
from Functions.backup_manager import BackupManager
from Functions.logging_manager import get_logger

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Affiche un en-tête de section"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_test(test_name):
    """Affiche le nom du test"""
    print(f"{Colors.BOLD}{Colors.BLUE}► TEST: {test_name}{Colors.RESET}")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}  ✓ {message}{Colors.RESET}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}  ✗ {message}{Colors.RESET}")

def print_info(message):
    """Affiche une information"""
    print(f"{Colors.YELLOW}  ℹ {message}{Colors.RESET}")

def get_folder_size(folder_path):
    """Calcule la taille totale d'un dossier en octets"""
    total_size = 0
    if os.path.exists(folder_path):
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
    return total_size

def get_file_size(file_path):
    """Retourne la taille d'un fichier ou dossier"""
    if os.path.isfile(file_path):
        return os.path.getsize(file_path)
    elif os.path.isdir(file_path):
        return get_folder_size(file_path)
    return 0

def count_backups(backup_dir):
    """Compte le nombre de backups dans un dossier"""
    if not os.path.exists(backup_dir):
        return 0
    return len([f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f)) or os.path.isdir(os.path.join(backup_dir, f))])

def setup_test_environment():
    """Prépare l'environnement de test"""
    print_header("PRÉPARATION DE L'ENVIRONNEMENT DE TEST")
    
    # Créer des dossiers de test
    test_base = Path("Test_Backup_System")
    test_characters = test_base / "Characters"
    test_backup = test_base / "Backups" / "Characters"
    test_cookies = test_base / "Cookies"
    test_cookies_backup = test_base / "Backups" / "Cookies"
    
    # Nettoyer si existe déjà
    if test_base.exists():
        print_info("Nettoyage de l'environnement de test précédent...")
        shutil.rmtree(test_base)
    
    # Créer la structure
    test_characters.mkdir(parents=True, exist_ok=True)
    test_backup.mkdir(parents=True, exist_ok=True)
    test_cookies.mkdir(parents=True, exist_ok=True)
    test_cookies_backup.mkdir(parents=True, exist_ok=True)
    
    # Créer des fichiers de test dans Characters
    for i in range(5):
        char_file = test_characters / f"character_{i}.json"
        char_data = {
            "name": f"TestChar{i}",
            "realm": "Albion",
            "level": 50,
            "class": "Armsman",
            "data": "x" * 10000  # ~10KB par fichier
        }
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)
    
    # Créer des fichiers cookies de test
    for i in range(3):
        cookie_file = test_cookies / f"cookies_eden_{i}.txt"
        with open(cookie_file, 'w') as f:
            f.write("session_id=test123456789\n" * 100)  # ~2KB par fichier
    
    print_success(f"Environnement de test créé: {test_base}")
    print_info(f"  Characters: {count_backups(test_characters)} fichiers (~50KB)")
    print_info(f"  Cookies: {count_backups(test_cookies)} fichiers (~6KB)")
    
    return {
        "base": str(test_base),
        "characters": str(test_characters),
        "backup": str(test_backup),
        "cookies": str(test_cookies),
        "cookies_backup": str(test_cookies_backup)
    }

def test_daily_backup(config_mgr, backup_mgr, test_paths):
    """Test 1: Backup au premier démarrage quotidien"""
    print_header("TEST 1: BACKUP AU PREMIER DÉMARRAGE QUOTIDIEN")
    
    # Test 1.1: Première exécution de la journée
    print_test("1.1 - Premier backup de la journée")
    config_mgr.set("backup_last_date", None)
    
    should_backup = backup_mgr.should_backup_today()
    if should_backup:
        print_success("Premier backup détecté correctement")
    else:
        print_error("Le premier backup n'a pas été détecté")
        return False
    
    # Créer le backup
    result = backup_mgr.backup_characters_force(reason="test")
    if result and result.get("success"):
        print_success(f"Backup créé: {result.get('file')}")
    else:
        print_error(f"Échec de création: {result.get('message') if result else 'Aucun résultat'}")
        return False
    
    # Test 1.2: Deuxième tentative dans la même journée
    print_test("1.2 - Deuxième tentative (même jour)")
    should_backup = backup_mgr.should_backup_today()
    if not should_backup:
        print_success("Backup quotidien déjà effectué - correctement ignoré")
    else:
        print_error("Le système devrait ignorer le second backup du jour")
        return False
    
    # Test 1.3: Backup du jour suivant
    print_test("1.3 - Backup du jour suivant")
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    config_mgr.set("backup_last_date", yesterday)
    
    should_backup = backup_mgr.should_backup_today()
    if should_backup:
        print_success("Nouveau jour détecté - backup autorisé")
    else:
        print_error("Le backup du jour suivant n'a pas été détecté")
        return False
    
    print_success("✓ Test des backups quotidiens réussi")
    return True

def test_compression(config_mgr, backup_mgr, test_paths):
    """Test 2: Compression ZIP vs copie simple"""
    print_header("TEST 2: COMPRESSION DES BACKUPS")
    
    backup_dir = test_paths["backup"]
    
    # Nettoyer les backups existants
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            fp = os.path.join(backup_dir, f)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
    
    # Test 2.1: Backup compressé (ZIP)
    print_test("2.1 - Backup avec compression ZIP")
    config_mgr.set("backup_compress", True)
    config_mgr.set("backup_last_date", None)
    
    result = backup_mgr.backup_characters_force(reason="test_zip")
    if result and result.get("success"):
        backup_file = result.get("file")
        if backup_file and backup_file.endswith('.zip'):
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            print_success(f"Backup ZIP créé: {os.path.basename(backup_file)}")
            print_info(f"  Taille: {size_mb:.2f} MB")
        else:
            print_error("Le backup n'est pas un fichier ZIP")
            return False
    else:
        print_error("Échec de création du backup compressé")
        return False
    
    # Nettoyer
    time.sleep(0.1)
    for f in os.listdir(backup_dir):
        fp = os.path.join(backup_dir, f)
        if os.path.isfile(fp):
            os.remove(fp)
        elif os.path.isdir(fp):
            shutil.rmtree(fp)
    
    # Test 2.2: Backup non compressé (copie)
    print_test("2.2 - Backup sans compression (copie)")
    config_mgr.set("backup_compress", False)
    config_mgr.set("backup_last_date", None)
    
    result = backup_mgr.backup_characters_force(reason="test_copy")
    if result and result.get("success"):
        backup_file = result.get("file")
        if backup_file and os.path.isdir(backup_file):
            size_mb = get_folder_size(backup_file) / (1024 * 1024)
            print_success(f"Backup dossier créé: {os.path.basename(backup_file)}")
            print_info(f"  Taille: {size_mb:.2f} MB")
        else:
            print_error("Le backup n'est pas un dossier")
            return False
    else:
        print_error("Échec de création du backup non compressé")
        return False
    
    print_success("✓ Test de compression réussi")
    return True

def test_auto_delete_retention(config_mgr, backup_mgr, test_paths):
    """Test 3: Suppression automatique des vieux backups"""
    print_header("TEST 3: SUPPRESSION AUTOMATIQUE DES VIEUX BACKUPS")
    
    backup_dir = test_paths["backup"]
    
    # Nettoyer
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            fp = os.path.join(backup_dir, f)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
    
    # Test 3.1: Auto-delete activé
    print_test("3.1 - Auto-delete activé avec limite 1 MB")
    config_mgr.set("backup_compress", True)
    config_mgr.set("backup_auto_delete_old", True)
    config_mgr.set("backup_size_limit_mb", 1)  # Limite très basse pour forcer suppression
    
    # Créer plusieurs backups
    print_info("Création de 5 backups...")
    for i in range(5):
        config_mgr.set("backup_last_date", None)
        result = backup_mgr.backup_characters_force(reason=f"test_auto_{i}")
        if result and result.get("success"):
            print_info(f"  Backup {i+1}/5 créé")
        time.sleep(0.2)  # Petit délai pour différencier les dates
    
    # Vérifier le nombre de backups restants
    remaining = count_backups(backup_dir)
    total_size_mb = get_folder_size(backup_dir) / (1024 * 1024)
    
    print_info(f"Backups restants: {remaining}")
    print_info(f"Taille totale: {total_size_mb:.2f} MB (limite: 1 MB)")
    
    if total_size_mb <= 1.1:  # Tolérance de 10%
        print_success(f"Suppression automatique effective - limite respectée")
    else:
        print_error(f"La limite n'est pas respectée: {total_size_mb:.2f} MB > 1 MB")
        return False
    
    # Test 3.2: Auto-delete désactivé
    print_test("3.2 - Auto-delete désactivé")
    
    # Nettoyer
    for f in os.listdir(backup_dir):
        fp = os.path.join(backup_dir, f)
        if os.path.isfile(fp):
            os.remove(fp)
        elif os.path.isdir(fp):
            shutil.rmtree(fp)
    
    config_mgr.set("backup_auto_delete_old", False)
    config_mgr.set("backup_size_limit_mb", 1)
    
    print_info("Création de 5 backups sans auto-delete...")
    for i in range(5):
        config_mgr.set("backup_last_date", None)
        result = backup_mgr.backup_characters_force(reason=f"test_no_auto_{i}")
        if result and result.get("success"):
            print_info(f"  Backup {i+1}/5 créé")
        time.sleep(0.2)
    
    remaining = count_backups(backup_dir)
    total_size_mb = get_folder_size(backup_dir) / (1024 * 1024)
    
    print_info(f"Backups restants: {remaining}")
    print_info(f"Taille totale: {total_size_mb:.2f} MB")
    
    if remaining == 5:
        print_success("Tous les backups conservés (auto-delete désactivé)")
    else:
        print_error(f"Des backups ont été supprimés alors que auto-delete est désactivé")
        return False
    
    print_success("✓ Test de suppression automatique réussi")
    return True

def test_storage_limits(config_mgr, backup_mgr, test_paths):
    """Test 4: Limites de stockage et mode illimité"""
    print_header("TEST 4: LIMITES DE STOCKAGE")
    
    backup_dir = test_paths["backup"]
    
    # Test 4.1: Limite normale
    print_test("4.1 - Limite de 2 MB")
    
    # Nettoyer
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            fp = os.path.join(backup_dir, f)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
    
    config_mgr.set("backup_compress", True)
    config_mgr.set("backup_auto_delete_old", True)
    config_mgr.set("backup_size_limit_mb", 2)
    
    print_info("Création de 10 backups...")
    for i in range(10):
        config_mgr.set("backup_last_date", None)
        result = backup_mgr.backup_characters_force(reason=f"test_limit_{i}")
        if result and result.get("success"):
            print_info(f"  Backup {i+1}/10 créé")
        time.sleep(0.2)
    
    total_size_mb = get_folder_size(backup_dir) / (1024 * 1024)
    print_info(f"Taille totale finale: {total_size_mb:.2f} MB (limite: 2 MB)")
    
    if total_size_mb <= 2.2:  # Tolérance de 10%
        print_success(f"Limite de 2 MB respectée")
    else:
        print_error(f"Limite dépassée: {total_size_mb:.2f} MB")
        return False
    
    # Test 4.2: Mode illimité (-1)
    print_test("4.2 - Mode illimité (-1)")
    
    # Nettoyer
    for f in os.listdir(backup_dir):
        fp = os.path.join(backup_dir, f)
        if os.path.isfile(fp):
            os.remove(fp)
        elif os.path.isdir(fp):
            shutil.rmtree(fp)
    
    config_mgr.set("backup_size_limit_mb", -1)
    config_mgr.set("backup_auto_delete_old", False)  # Auto désactivé en mode -1
    
    print_info("Création de 15 backups en mode illimité...")
    for i in range(15):
        config_mgr.set("backup_last_date", None)
        result = backup_mgr.backup_characters_force(reason=f"test_unlimited_{i}")
        if result and result.get("success"):
            print_info(f"  Backup {i+1}/15 créé")
        time.sleep(0.2)
    
    remaining = count_backups(backup_dir)
    total_size_mb = get_folder_size(backup_dir) / (1024 * 1024)
    
    print_info(f"Backups créés: {remaining}")
    print_info(f"Taille totale: {total_size_mb:.2f} MB (illimité)")
    
    if remaining == 15:
        print_success("Mode illimité: tous les backups conservés")
    else:
        print_error(f"Des backups ont été supprimés en mode illimité")
        return False
    
    print_success("✓ Test des limites de stockage réussi")
    return True

def test_cookies_backup(config_mgr, backup_mgr, test_paths):
    """Test 5: Backups des cookies"""
    print_header("TEST 5: BACKUPS DES COOKIES")
    
    cookies_backup_dir = test_paths["cookies_backup"]
    
    # Nettoyer
    if os.path.exists(cookies_backup_dir):
        for f in os.listdir(cookies_backup_dir):
            fp = os.path.join(cookies_backup_dir, f)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
    
    print_test("5.1 - Backup cookies avec compression")
    config_mgr.set("cookies_backup_enabled", True)
    config_mgr.set("cookies_backup_compress", True)
    config_mgr.set("cookies_backup_auto_delete_old", True)
    config_mgr.set("cookies_backup_size_limit_mb", 1)
    config_mgr.set("cookies_backup_last_date", None)
    
    result = backup_mgr.backup_cookies_force(reason="test")
    if result and result.get("success"):
        backup_file = result.get("file")
        if backup_file and backup_file.endswith('.zip'):
            size_kb = os.path.getsize(backup_file) / 1024
            print_success(f"Backup cookies ZIP créé: {os.path.basename(backup_file)}")
            print_info(f"  Taille: {size_kb:.2f} KB")
        else:
            print_error("Le backup cookies n'est pas un fichier ZIP")
            return False
    else:
        print_error(f"Échec backup cookies: {result.get('message') if result else 'Aucun résultat'}")
        return False
    
    print_test("5.2 - Rétention cookies avec limite")
    print_info("Création de 5 backups cookies...")
    for i in range(4):  # 4 de plus = 5 total
        config_mgr.set("cookies_backup_last_date", None)
        result = backup_mgr.backup_cookies_force(reason=f"test_cookies_{i+2}")
        if result and result.get("success"):
            print_info(f"  Backup cookies {i+2}/5 créé")
        time.sleep(0.2)
    
    remaining = count_backups(cookies_backup_dir)
    total_size_mb = get_folder_size(cookies_backup_dir) / (1024 * 1024)
    
    print_info(f"Backups cookies restants: {remaining}")
    print_info(f"Taille totale: {total_size_mb:.2f} MB (limite: 1 MB)")
    
    if total_size_mb <= 1.1:  # Tolérance
        print_success("Limite cookies respectée")
    else:
        print_error(f"Limite cookies dépassée: {total_size_mb:.2f} MB")
        return False
    
    print_success("✓ Test des backups cookies réussi")
    return True

def cleanup_test_environment(test_paths):
    """Nettoie l'environnement de test"""
    print_header("NETTOYAGE")
    
    test_base = Path(test_paths["base"])
    if test_base.exists():
        shutil.rmtree(test_base)
        print_success("Environnement de test nettoyé")
    else:
        print_info("Rien à nettoyer")

def main():
    """Fonction principale de test"""
    print_header("TESTS DU SYSTÈME DE BACKUP")
    print_info("Démarrage des tests automatisés...")
    
    # Préparer l'environnement
    test_paths = setup_test_environment()
    
    # Créer le gestionnaire de configuration pour les tests
    config_mgr = ConfigManager()
    
    # Sauvegarder la config actuelle
    original_config = {
        "character_folder": config_mgr.get("character_folder"),
        "backup_path": config_mgr.get("backup_path"),
        "cookies_folder": config_mgr.get("cookies_folder"),
        "cookies_backup_path": config_mgr.get("cookies_backup_path"),
    }
    
    # Configurer pour les tests
    config_mgr.set("character_folder", test_paths["characters"])
    config_mgr.set("backup_path", test_paths["backup"])
    config_mgr.set("cookies_folder", test_paths["cookies"])
    config_mgr.set("cookies_backup_path", test_paths["cookies_backup"])
    config_mgr.set("backup_enabled", True)
    config_mgr.set("cookies_backup_enabled", True)
    
    # Créer le gestionnaire de backup
    backup_mgr = BackupManager(config_mgr)
    
    # Exécuter les tests
    results = []
    
    try:
        results.append(("Backup quotidien", test_daily_backup(config_mgr, backup_mgr, test_paths)))
        results.append(("Compression", test_compression(config_mgr, backup_mgr, test_paths)))
        results.append(("Auto-delete", test_auto_delete_retention(config_mgr, backup_mgr, test_paths)))
        results.append(("Limites stockage", test_storage_limits(config_mgr, backup_mgr, test_paths)))
        results.append(("Cookies backup", test_cookies_backup(config_mgr, backup_mgr, test_paths)))
        
    finally:
        # Restaurer la config originale
        for key, value in original_config.items():
            if value:
                config_mgr.set(key, value)
        
        # Nettoyer
        cleanup_test_environment(test_paths)
    
    # Afficher le résumé
    print_header("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ RÉUSSI{Colors.RESET}" if result else f"{Colors.RED}✗ ÉCHOUÉ{Colors.RESET}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Résultat final: {passed}/{total} tests réussis{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ TOUS LES TESTS SONT RÉUSSIS !{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ CERTAINS TESTS ONT ÉCHOUÉ{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
