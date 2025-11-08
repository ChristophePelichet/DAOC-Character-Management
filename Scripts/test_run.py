"""Script pour tester le chargement des icônes avec logs détaillés"""
import subprocess
import time
import os

log_file = r"d:\Projets\Python\DAOC---Gestion-des-personnages\Logs\debug.log"

print("=" * 70)
print("Test du chargement des icônes - Affichage des logs en temps réel")
print("=" * 70)
print("\nLancement de l'application...")
print("Fermez l'application pour voir le résumé des logs\n")
print("-" * 70)

# Lancer l'application en arrière-plan
proc = subprocess.Popen(
    ["python", "main.py"],
    cwd=r"d:\Projets\Python\DAOC---Gestion-des-personnages"
)

# Wait un peu that l'application démarre
time.sleep(2)

# Lire et afficher les nouveaux logs
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = f.read()
        if logs:
            print("\n📋 LOGS GÉNÉRÉS:\n")
            # Filtrer les logs pertinents
            for line in logs.split('\n'):
                if any(keyword in line for keyword in [
                    'REALM_ICONS', 'Verification', 'tree_realm_icons',
                    'Populating tree', 'Icon loading', 'Character', 'icon found'
                ]):
                    print(line)
        else:
            print("\n⚠️ Aucun log généré pour le moment")
            print("Vérifiez que debug_mode est activé dans Configuration/config.json")
else:
    print("\n❌ Fichier de log introuvable!")

print("\n" + "-" * 70)
print("L'application est en cours d'exécution...")
print("Fermez la fenêtre de l'application pour continuer.")
print("-" * 70)