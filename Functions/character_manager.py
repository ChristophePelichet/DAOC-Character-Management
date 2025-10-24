import json
import os
import uuid # To generate unique identifiers
import logging
from .config_manager import config
from .path_manager import get_base_path

logger = logging.getLogger(__name__)

# --- Realm to Icon Mapping ---
REALM_ICONS = {
    "Albion": "albion_logo.png",
    "Hibernia": "hibernia_logo.png",
    "Midgard": "midgard_logo.png"
}

def get_character_dir():
    """
    Gets the character directory from the config.
    If not set, defaults to a 'Characters' folder in the project root.
    """
    path = config.get("character_folder")
    if path and os.path.isdir(path):
        return path
    return os.path.join(get_base_path(), 'Characters')

def create_character_data(name, realm):
    """
    Creates a basic data dictionary for a new character.
    """
    icon_filename = REALM_ICONS.get(realm, "default.png") # Get icon filename, with a fallback
    character_id = str(uuid.uuid4()) # Generate a unique ID
    return {
        "id": character_id,
        "name": name,
        "realm": realm,
        # We store only the filename, not the full path.
        "icon": icon_filename,
        "level": 1,
        "health": 100,
        "inventory": []
    }

def save_character(character_data):
    """
    Saves a character's data to a JSON file.
    First, it checks if a character with the same name already exists.
    """
    main_character_dir = get_character_dir()
    realm = character_data.get("realm")

    if not realm:
        return False, "Realm information is missing."

    realm_dir = os.path.join(main_character_dir, realm)
    os.makedirs(realm_dir, exist_ok=True)
    
    # Check for name uniqueness before sanitizing for filename
    existing_names_lower = {char['name'].lower() for char in get_all_characters()}
    if character_data['name'].lower() in existing_names_lower:
        # Return a specific error key for the UI to handle translation
        return False, "char_exists_error"

    # Use the unique character ID as the filename to avoid sanitization issues.
    character_id = character_data.get("id")
    filename = os.path.join(realm_dir, f"{character_id}.json")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4, ensure_ascii=False)
        return True, f"Character '{character_data['name']}' saved to {filename}"
    except (IOError, OSError) as e:
        return False, f"Error while saving character: {e}"

def get_all_characters():
    """
    Scans the 'Characters' directory and its realm subdirectories,
    and returns a list of dictionaries, each containing character details.
    """
    character_dir = get_character_dir()
    if not os.path.exists(character_dir):
        return []  # Return an empty list if the directory does not exist

    characters = []
    for realm in REALM_ICONS.keys():
        realm_dir = os.path.join(character_dir, realm)
        if os.path.isdir(realm_dir):
            for filename in os.listdir(realm_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(realm_dir, filename), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Add essential data for the list view
                            characters.append(data)
                    except (json.JSONDecodeError, IOError) as e:
                        logger.warning(f"Could not read or parse character file {filename}: {e}")
                        continue
    return sorted(characters, key=lambda x: (x.get('realm', ''), x.get('name', '').lower()))

def delete_character(character_id, realm, character_name=None):
    """
    Deletes a character's JSON file. It first tries to delete by ID,
    and as a fallback, tries to delete by the character name for backward compatibility.
    Returns True on success, False on failure.
    """
    if not realm:
        logger.error("Attempted to delete a character with missing realm.")
        return False, "Missing character realm."

    character_dir = get_character_dir()
    
    # Primary strategy: delete by ID
    file_path_by_id = os.path.join(character_dir, realm, f"{character_id}.json")
    # Fallback strategy: delete by name (for older files)
    file_path_by_name = os.path.join(character_dir, realm, f"{character_name}.json") if character_name else None

    path_to_delete = None
    if os.path.exists(file_path_by_id):
        path_to_delete = file_path_by_id
    elif file_path_by_name and os.path.exists(file_path_by_name):
        path_to_delete = file_path_by_name

    if path_to_delete:
        try:
            os.remove(path_to_delete)
            logger.info(f"Successfully deleted character file: {path_to_delete}")
            return True, "Character deleted successfully."
        except OSError as e:
            logger.error(f"Error deleting character file {path_to_delete}: {e}")
            return False, f"OS error while deleting file: {e}"
    else:
        logger.warning(f"Attempted to delete a non-existent character file. Tried: {file_path_by_id} and {file_path_by_name}")
        return False, "Character file not found."