import json
import os
import uuid # To generate unique identifiers

# Define the path to the 'Characters' directory at the project root.
# This assumes that main.py is run from the project root (e.g., d:/my_cool_project).
# os.path.dirname(__file__) -> d:/my_cool_project/Functions
# os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) -> d:/my_cool_project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHARACTER_DIR = os.path.join(PROJECT_ROOT, 'Characters')

def _ensure_character_directory_exists():
    """Checks and creates the 'Characters' directory if it does not exist."""
    if not os.path.exists(CHARACTER_DIR):
        os.makedirs(CHARACTER_DIR)
        print(f"Répertoire créé : {CHARACTER_DIR}")

def create_character_data(name):
    """
    Creates a basic data dictionary for a new character.
    """
    character_id = str(uuid.uuid4()) # Generate a unique ID
    return {
        "id": character_id,
        "name": name,
        "level": 1,
        "health": 100,
        "inventory": []
    }

def save_character(character_data):
    """
    Saves a character's data to a JSON file.
    First, it checks if a character with the same name already exists.
    """
    _ensure_character_directory_exists()
    
    # Sanitize the name: convert to lowercase, replace spaces with underscores,
    # and remove all non-alphanumeric characters (except underscore).
    base_name = character_data['name'].lower().replace(' ', '_')
    sanitized_name = "".join(c for c in base_name if c.isalnum() or c == '_')
    filename = os.path.join(CHARACTER_DIR, f"{sanitized_name}.json")

    # Check if the file already exists to ensure name uniqueness
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
    Scans the 'Characters' directory and returns a list of character names.
    """
    if not os.path.exists(CHARACTER_DIR):
        return []  # Return an empty list if the directory does not exist

    character_names = []
    for filename in os.listdir(CHARACTER_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(CHARACTER_DIR, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'name' in data:
                        character_names.append(data['name'])
            except (json.JSONDecodeError, IOError):
                # Ignore corrupted or unreadable files to avoid crashing the app
                continue
    return sorted(character_names)