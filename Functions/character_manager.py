import json
import os
import uuid # To generate unique identifiers
import logging
from .config_manager import config
from .path_manager import get_base_path

logger = logging.getLogger(__name__)

def get_character_dir():
    """
    Gets the character directory from the config.
    If not set, defaults to a 'Characters' folder in the project root.
    """
    path = config.get("character_folder")
    if path and os.path.isdir(path):
        return path
    return os.path.join(get_base_path(), 'Characters')

def _ensure_character_directory_exists():
    """Checks and creates the 'Characters' directory if it does not exist."""
    character_dir = get_character_dir()
    if not os.path.exists(character_dir):
        os.makedirs(character_dir)
        logger.info(f"Directory created: {character_dir}")

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
    filename = os.path.join(get_character_dir(), f"{sanitized_name}.json")

    # Check if the file already exists to ensure name uniqueness
    if os.path.exists(filename):
        return False, f"Un personnage nommé '{character_data['name']}' existe déjà."

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4, ensure_ascii=False)
        return True, f"Personnage '{character_data['name']}' sauvegardé dans {filename}"
    except (IOError, OSError) as e:
        return False, f"Erreur lors de la sauvegarde du personnage : {e}"

def get_all_characters():
    """
    Scans the 'Characters' directory and returns a list of character names.
    """
    character_dir = get_character_dir()
    if not os.path.exists(character_dir):
        return []  # Return an empty list if the directory does not exist

    character_names = []
    for filename in os.listdir(character_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(character_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'name' in data:
                        character_names.append(data['name'])
            except (json.JSONDecodeError, IOError) as e:
                # Ignore corrupted or unreadable files to avoid crashing the app
                logger.warning(f"Could not read or parse character file {filename}: {e}")
                continue
    return sorted(character_names)