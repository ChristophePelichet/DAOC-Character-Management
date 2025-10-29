#!/usr/bin/env python3
"""
Script de nettoyage de projet
Supprime les dossiers temporaires et de données pour démarrer une nouvelle branche propre.

Usage:
    python Scripts/clean_project.py
    python Scripts/clean_project.py --dry-run  # Affiche ce qui sera supprimé sans rien supprimer
    python Scripts/clean_project.py --no-git   # Ne crée pas de nouvelle branche Git
"""

import os
import sys
import shutil
from pathlib import Path
import argparse
import subprocess


# Dossiers à supprimer
FOLDERS_TO_CLEAN = [
    "Backup",
    "build",
    "dist",
    "Characters",
    "Configuration",
    "Logs"
]

# Dossiers de cache à supprimer
CACHE_FOLDERS = [
    "__pycache__",
    "Functions/__pycache__",
    "UI/__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache"
]

# Extensions de fichiers cache à supprimer
CACHE_EXTENSIONS = [
    ".pyc",
    ".pyo",
    ".pyd"
]


def get_project_root():
    """Retourne le chemin racine du projet"""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def delete_folder(folder_path: Path, dry_run: bool = False) -> bool:
    """
    Supprime un dossier et son contenu
    
    Args:
        folder_path: Chemin du dossier à supprimer
        dry_run: Si True, n'effectue pas la suppression (mode simulation)
    
    Returns:
        True si le dossier a été supprimé (ou aurait été supprimé en mode dry_run)
    """
    if not folder_path.exists():
        return False
    
    if not folder_path.is_dir():
        print(f"  ⚠️  '{folder_path.name}' n'est pas un dossier (ignoré)")
        return False
    
    # Compter les fichiers
    file_count = sum(1 for _ in folder_path.rglob('*') if _.is_file())
    
    if dry_run:
        print(f"  🔍 '{folder_path}' serait supprimé ({file_count} fichiers)")
        return True
    
    try:
        shutil.rmtree(folder_path)
        print(f"  ✅ '{folder_path}' supprimé ({file_count} fichiers)")
        return True
    except Exception as e:
        print(f"  ❌ Erreur lors de la suppression de '{folder_path}': {e}")
        return False


def clean_cache_files(project_root: Path, dry_run: bool = False) -> int:
    """
    Supprime tous les fichiers de cache Python
    
    Args:
        project_root: Racine du projet
        dry_run: Si True, simule les suppressions
    
    Returns:
        Nombre de fichiers supprimés
    """
    deleted_count = 0
    
    for ext in CACHE_EXTENSIONS:
        cache_files = list(project_root.rglob(f"*{ext}"))
        for cache_file in cache_files:
            if dry_run:
                print(f"  🔍 '{cache_file.relative_to(project_root)}' serait supprimé")
                deleted_count += 1
            else:
                try:
                    cache_file.unlink()
                    print(f"  ✅ '{cache_file.relative_to(project_root)}' supprimé")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ❌ Erreur: {cache_file.name}: {e}")
    
    return deleted_count


def run_git_command(command: list, cwd: Path) -> tuple[bool, str]:
    """
    Exécute une commande Git
    
    Args:
        command: Liste des arguments de la commande
        cwd: Répertoire de travail
    
    Returns:
        Tuple (succès, sortie)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def create_new_branch(project_root: Path):
    """
    Crée une nouvelle branche Git et la pousse vers le dépôt distant
    
    Args:
        project_root: Racine du projet
    """
    print("\n" + "=" * 60)
    print("🌿 CRÉATION D'UNE NOUVELLE BRANCHE GIT")
    print("=" * 60)
    
    # Vérifier que c'est un dépôt Git
    if not (project_root / ".git").exists():
        print("❌ Ce n'est pas un dépôt Git")
        return
    
    # Obtenir la branche actuelle
    success, current_branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], project_root)
    if success:
        print(f"📍 Branche actuelle: {current_branch}")
    
    # Demander le nom de la nouvelle branche
    print("\n💡 Entrez le nom de la nouvelle branche")
    print("   (ex: Feature_NewUI, Bugfix_Issue123, Refactoring_105, etc.)")
    branch_name = input("\n🌿 Nom de la branche: ").strip()
    
    if not branch_name:
        print("❌ Nom de branche vide, création annulée")
        return
    
    # Vérifier que la branche n'existe pas déjà
    success, branches = run_git_command(["git", "branch", "--list", branch_name], project_root)
    if success and branches:
        print(f"❌ La branche '{branch_name}' existe déjà localement")
        return
    
    print(f"\n🔨 Création de la branche '{branch_name}'...")
    success, output = run_git_command(["git", "checkout", "-b", branch_name], project_root)
    
    if not success:
        print(f"❌ Erreur lors de la création de la branche: {output}")
        return
    
    print(f"✅ Branche '{branch_name}' créée et activée")
    
    # Demander confirmation pour le push
    print(f"\n📤 Voulez-vous pousser la branche '{branch_name}' vers le dépôt distant?")
    response = input("   (oui/non): ").strip().lower()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("⏭️  Push annulé - La branche existe seulement en local")
        return
    
    print(f"\n📤 Push de la branche '{branch_name}' vers origin...")
    success, output = run_git_command(
        ["git", "push", "-u", "origin", branch_name],
        project_root
    )
    
    if success:
        print(f"✅ Branche '{branch_name}' poussée vers le dépôt distant")
        print(f"\n🎉 Vous êtes maintenant sur la branche '{branch_name}' et elle est trackée sur origin")
    else:
        print(f"❌ Erreur lors du push: {output}")
        print(f"💡 La branche existe localement, vous pouvez pusher manuellement plus tard")


def clean_project(dry_run: bool = False, create_branch: bool = True):
    """
    Nettoie le projet en supprimant les dossiers temporaires
    
    Args:
        dry_run: Si True, simule les suppressions sans les effectuer
        create_branch: Si True, propose de créer une nouvelle branche Git
    """
    project_root = get_project_root()
    
    print("=" * 60)
    print("🧹 NETTOYAGE DU PROJET DAOC CHARACTER MANAGER")
    print("=" * 60)
    print(f"📁 Racine du projet: {project_root}")
    
    if dry_run:
        print("⚠️  MODE SIMULATION (aucune suppression réelle)")
    
    print("\n🗑️  Dossiers principaux à nettoyer:")
    for folder in FOLDERS_TO_CLEAN:
        print(f"   • {folder}")
    
    print("\n🗑️  Caches à nettoyer:")
    for folder in CACHE_FOLDERS:
        print(f"   • {folder}")
    print(f"   • Fichiers: {', '.join(CACHE_EXTENSIONS)}")
    
    print("\n" + "-" * 60)
    
    # Confirmation
    if not dry_run:
        print("\n⚠️  ATTENTION: Cette action est irréversible!")
        response = input("Voulez-vous continuer? (oui/non): ").strip().lower()
        if response not in ['oui', 'o', 'yes', 'y']:
            print("\n❌ Nettoyage annulé par l'utilisateur")
            return
        print()
    
    # Suppression des dossiers principaux
    print("📦 Nettoyage des dossiers principaux...")
    deleted_folders = 0
    for folder_name in FOLDERS_TO_CLEAN:
        folder_path = project_root / folder_name
        if delete_folder(folder_path, dry_run):
            deleted_folders += 1
    
    # Suppression des caches
    print("\n🗂️  Nettoyage des dossiers de cache...")
    deleted_cache_folders = 0
    for cache_folder in CACHE_FOLDERS:
        cache_path = project_root / cache_folder
        if delete_folder(cache_path, dry_run):
            deleted_cache_folders += 1
    
    # Suppression des fichiers de cache
    print("\n📄 Nettoyage des fichiers de cache...")
    deleted_cache_files = clean_cache_files(project_root, dry_run)
    
    # Résumé
    print("\n" + "=" * 60)
    if dry_run:
        print(f"✅ Dossiers principaux: {deleted_folders}/{len(FOLDERS_TO_CLEAN)} seraient supprimés")
        print(f"✅ Dossiers de cache: {deleted_cache_folders} seraient supprimés")
        print(f"✅ Fichiers de cache: {deleted_cache_files} seraient supprimés")
        print("\n💡 Relancez sans --dry-run pour effectuer le nettoyage")
    else:
        print(f"✅ Dossiers principaux: {deleted_folders}/{len(FOLDERS_TO_CLEAN)} supprimés")
        print(f"✅ Dossiers de cache: {deleted_cache_folders} supprimés")
        print(f"✅ Fichiers de cache: {deleted_cache_files} supprimés")
        print(f"\n🎉 Nettoyage terminé!")
    print("=" * 60)
    
    # Création de branche Git
    if not dry_run and create_branch:
        print("\n")
        response = input("🌿 Voulez-vous créer une nouvelle branche Git? (oui/non): ").strip().lower()
        if response in ['oui', 'o', 'yes', 'y']:
            create_new_branch(project_root)
        else:
            print("⏭️  Création de branche ignorée")


def main():
    parser = argparse.ArgumentParser(
        description="Nettoie le projet en supprimant les dossiers temporaires et de données",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python Scripts/clean_project.py                 # Nettoie le projet et propose création branche
  python Scripts/clean_project.py --dry-run       # Simule le nettoyage
  python Scripts/clean_project.py -d              # Simule le nettoyage (forme courte)
  python Scripts/clean_project.py --no-git        # Nettoie sans créer de branche Git
        """
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help="Simule les suppressions sans les effectuer réellement"
    )
    
    parser.add_argument(
        '--no-git',
        action='store_true',
        help="Ne propose pas de créer une nouvelle branche Git"
    )
    
    args = parser.parse_args()
    
    try:
        clean_project(dry_run=args.dry_run, create_branch=not args.no_git)
    except KeyboardInterrupt:
        print("\n\n❌ Nettoyage interrompu par l'utilisateur (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
