import os
import json
import uuid
import logging
from Functions.config_manager import config

REALMS = ["Albion", "Hibernia", "Midgard"]
REALM_ICONS = {
    "Albion": "albion_logo.png",
    "Hibernia": "hibernia_logo.png",
    "Midgard": "midgard_logo.png"
}

def get_character_dir():
    """Returns the configured character directory."""
    return config.get("character_folder", os.path.join(os.getcwd(), "Characters"))

def create_character_data(name, realm):
    """
    Creates a dictionary for a new character.
    The 'id' is now the character name for file system identification.
    A separate 'uuid' is kept for internal robustness if needed.
    """
    return {
        'id': name, # The main identifier is now the name
        'uuid': str(uuid.uuid4()), # Still keep a unique ID internally
        'name': name,
        'realm': realm,
        'level': 1,
        # Add other default character attributes here
    }

def save_character(character_data):
    """
    Saves character data to a JSON file named after the character,
    inside a subfolder corresponding to its realm.
    e.g., 'Characters/Albion/Merlin.json'
    """
    base_char_dir = get_character_dir()

    character_name = character_data.get('name')
    character_realm = character_data.get('realm')

    if not character_name:
        return False, "Character data must contain a 'name'."
    if not character_realm or character_realm not in REALMS:
        return False, f"Invalid or missing realm for character '{character_name}'."

    # Create the realm-specific directory
    char_dir = os.path.join(base_char_dir, character_realm)
    os.makedirs(char_dir, exist_ok=True)

    file_path = os.path.join(char_dir, f"{character_name}.json")

    if os.path.exists(file_path):
        return False, "char_exists_error"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4)
        logging.info(f"Character '{character_name}' saved to {file_path}")
        return True, "Character saved successfully."
    except Exception as e:
        logging.error(f"Error saving character '{character_name}': {e}")
        return False, f"Failed to save character file: {e}"

def get_all_characters():
    """
    Loads all characters from .json files by walking through realm subdirectories.
    The character 'id' is derived from the filename.
    """
    base_char_dir = get_character_dir()
    if not os.path.exists(base_char_dir):
        return []

    characters = []
    # os.walk will traverse the root and all subdirectories
    for root, _, files in os.walk(base_char_dir):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                        # Ensure the 'id' in the app matches the filename (without extension)
                        char_data['id'] = os.path.splitext(filename)[0]
                        characters.append(char_data)
                except (json.JSONDecodeError, KeyError) as e:
                    logging.warning(f"Could not load or parse {file_path}: {e}")
    return sorted(characters, key=lambda c: c.get('name', '').lower())

def delete_character(character_name):
    """
    Deletes a character's JSON file based on their name.
    """
    if not character_name:
        return False, "Character name not provided."

    base_char_dir = get_character_dir()
    file_to_delete = None

    # Search for the character file in all realm subdirectories
    for realm in REALMS:
        potential_path = os.path.join(base_char_dir, realm, f"{character_name}.json")
        if os.path.exists(potential_path):
            file_to_delete = potential_path
            break

    if file_to_delete:
        try:
            os.remove(file_to_delete)
            logging.info(f"Deleted character file: {file_to_delete}")
            return True, "Character deleted successfully."
        except OSError as e:
            logging.error(f"Error deleting file {file_to_delete}: {e}")
            return False, f"Could not delete character file: {e}"
    else:
        logging.warning(f"Attempted to delete non-existent character file for '{character_name}'.")
        return False, "Character file not found."