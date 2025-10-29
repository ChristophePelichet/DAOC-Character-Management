"""
Script de test pour vérifier la nouvelle structure de sauvegarde compressée.

Ce script teste :
1. La création du dossier Backup/Characters/
2. La compression en .zip
3. Le contenu de l'archive
"""

import os
import sys
import zipfile
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.migration_manager import backup_characters, get_backup_path
from Functions.path_manager import get_base_path

def test_backup_structure():
    """Teste la structure de sauvegarde."""
    print("=" * 60)
    print("TEST DE LA STRUCTURE DE SAUVEGARDE")
    print("=" * 60)
    
    # Afficher le chemin de base
    base_path = get_base_path()
    print(f"\nChemin de base : {base_path}")
    
    # Afficher le chemin de sauvegarde prévu
    backup_path = get_backup_path()
    print(f"\nChemin de sauvegarde prévu : {backup_path}")
    print(f"Extension : {os.path.splitext(backup_path)[1]}")
    
    # Vérifier la structure du chemin
    backup_dir = os.path.dirname(backup_path)
    print(f"\nRépertoire de sauvegarde : {backup_dir}")
    print(f"Doit se terminer par : Backup{os.sep}Characters")
    
    expected_end = os.path.join("Backup", "Characters")
    if backup_dir.endswith(expected_end):
        print("✓ Structure du chemin correcte")
    else:
        print("✗ Structure du chemin incorrecte")
    
    # Test de création de sauvegarde (si Characters existe)
    char_dir = os.path.join(base_path, "Characters")
    if os.path.exists(char_dir):
        print(f"\n\nTest de création de sauvegarde...")
        print(f"Dossier Characters trouvé : {char_dir}")
        
        response = input("\nVoulez-vous créer une sauvegarde de test ? (oui/non) : ")
        if response.lower() in ['oui', 'yes', 'y', 'o']:
            success, backup_path, message = backup_characters()
            
            if success:
                print(f"\n✓ {message}")
                print(f"Fichier créé : {backup_path}")
                
                # Vérifier que c'est un fichier zip valide
                if zipfile.is_zipfile(backup_path):
                    print("✓ Fichier ZIP valide")
                    
                    # Lister le contenu
                    print("\nContenu de l'archive :")
                    with zipfile.ZipFile(backup_path, 'r') as zipf:
                        for info in zipf.infolist():
                            size_kb = info.file_size / 1024
                            print(f"  - {info.filename} ({size_kb:.2f} KB)")
                    
                    # Afficher la taille totale
                    total_size = os.path.getsize(backup_path)
                    print(f"\nTaille totale de l'archive : {total_size / 1024:.2f} KB")
                else:
                    print("✗ Le fichier n'est pas un ZIP valide")
            else:
                print(f"\n✗ Échec : {message}")
    else:
        print(f"\n⚠ Dossier Characters non trouvé : {char_dir}")
        print("Créez d'abord des personnages pour tester la sauvegarde.")
    
    print("\n" + "=" * 60)
    print("TEST TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    test_backup_structure()
