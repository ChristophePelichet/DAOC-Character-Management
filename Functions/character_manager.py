import json
import os
import uuid # Pour générer des identifiants uniques

# Définir le chemin du répertoire 'Characters' à la racine du projet.
# Cela suppose que main.py est exécuté depuis la racine du projet (d:/mon_super_projet).
# os.path.dirname(__file__) -> d:/mon_super_projet/Functions
# os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) -> d:/mon_super_projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHARACTER_DIR = os.path.join(PROJECT_ROOT, 'Characters')

def _ensure_character_directory_exists():
    """Vérifie et crée le répertoire 'Characters' s'il n'existe pas."""
    if not os.path.exists(CHARACTER_DIR):
        os.makedirs(CHARACTER_DIR)
        print(f"Répertoire créé : {CHARACTER_DIR}")

def create_character_data(name):
    """
    Crée un dictionnaire de données de base pour un nouveau personnage.
    """
    character_id = str(uuid.uuid4()) # Génère un ID unique
    return {
        "id": character_id,
        "name": name,
        "level": 1,
        "health": 100,
        "inventory": []
    }

def save_character(character_data):
    """
    Sauvegarde les données d'un personnage dans un fichier JSON.
    Vérifie d'abord si un personnage avec le même nom existe déjà.
    """
    _ensure_character_directory_exists()
    
    # Nettoie le nom : conversion en minuscules, remplacement des espaces par des underscores,
    # et suppression de tous les caractères non alphanumériques (et non underscore).
    base_name = character_data['name'].lower().replace(' ', '_')
    sanitized_name = "".join(c for c in base_name if c.isalnum() or c == '_')
    filename = os.path.join(CHARACTER_DIR, f"{sanitized_name}.json")

    # Vérifier si le fichier existe déjà pour garantir l'unicité du nom
    if os.path.exists(filename):
        return False, f"Un personnage nommé '{character_data['name']}' existe déjà."

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4, ensure_ascii=False)
        return True, f"Personnage '{character_data['name']}' sauvegardé dans {filename}"
    except IOError as e:
        return False, f"Erreur lors de la sauvegarde du personnage : {e}"

def get_all_characters():
    """
    Scanne le répertoire 'Characters' et retourne une liste des noms de personnages.
    """
    if not os.path.exists(CHARACTER_DIR):
        return []  # Retourne une liste vide si le répertoire n'existe pas

    character_names = []
    for filename in os.listdir(CHARACTER_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(CHARACTER_DIR, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'name' in data:
                        character_names.append(data['name'])
            except (json.JSONDecodeError, IOError):
                # Ignorer les fichiers corrompus ou illisibles pour ne pas planter l'app
                continue
    return sorted(character_names)