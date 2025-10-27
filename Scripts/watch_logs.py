"""Script de surveillance des logs en temps réel"""
import time
import os

log_file = r"d:\Projets\Python\DAOC---Gestion-des-personnages\Logs\debug.log"

print("=" * 70)
print("SURVEILLANCE DU FICHIER DE LOG EN TEMPS RÉEL")
print("=" * 70)
print(f"\nFichier surveillé: {log_file}")
print("\nINSTRUCTIONS:")
print("1. Laissez ce script tourner")
print("2. Lancez l'application (F5 dans VS Code)")
print("3. Les logs apparaîtront ici en temps réel")
print("4. Appuyez sur Ctrl+C pour arrêter la surveillance")
print("\n" + "-" * 70)
print("En attente des logs...\n")

# Créer le fichier s'il n'existe pas
if not os.path.exists(log_file):
    open(log_file, 'w').close()

# Position actuelle dans le fichier
last_position = 0

try:
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        # Aller à la fin du fichier
        f.seek(0, 2)
        last_position = f.tell()
        
        while True:
            # Lire les nouvelles lignes
            f.seek(last_position)
            new_lines = f.read()
            
            if new_lines:
                # Afficher les lignes pertinentes en couleur
                for line in new_lines.strip().split('\n'):
                    if any(keyword in line for keyword in [
                        'REALM_ICONS', 'Verification', 'tree_realm_icons',
                        'Populating tree', 'Icon loading', 'icon found', 
                        'Pre-loading', 'Application starting'
                    ]):
                        print(f">>> {line}")
                    elif 'ERROR' in line or 'WARNING' in line or 'CRITICAL' in line:
                        print(f"!!! {line}")
                    elif 'DEBUG' in line:
                        print(f"... {line}")
                    
                last_position = f.tell()
            
            time.sleep(0.5)
            
except KeyboardInterrupt:
    print("\n\n" + "-" * 70)
    print("Surveillance arrêtée.")
    print("-" * 70)
