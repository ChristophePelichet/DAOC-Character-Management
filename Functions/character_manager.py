import os
import json
import uuid
import logging
from Functions.config_manager import config
from Functions.path_manager import get_base_path

REALMS = ["Albion", "Hibernia", "Midgard"]
REALM_ICONS = {
    "Albion": "albion_logo.png",
    "Hibernia": "hibernia_logo.png",
    "Midgard": "midgard_logo.png"
}

def get_character_dir():
    """Returns the configured character directory."""
    default_path = os.path.join(get_base_path(), "Characters")
    return config.get("character_folder") or default_path

def create_character_data(name, realm, season, server, level=1, page=1, guild=""):
    """
    Creates a dictionary for a new character.
    The 'id' is now the character name for file system identification.
    A separate 'uuid' is kept for internal robustness if needed.
    """
    return {
        'id': name,  # The main identifier is now the name
        'uuid': str(uuid.uuid4()),  # Still keep a unique ID internally
        'name': name,
        'realm': realm,
        'level': level,
        'season': season,
        'server': server,
        'page': page,
        'guild': guild,
        'realm_rank': '1L1',
        # Add other default character attributes here
    }

def save_character(character_data, allow_overwrite=False):
    """
    Saves character data to a JSON file named after the character,
    inside a subfolder corresponding to its realm.
    e.g., 'Characters/Albion/Merlin.json'
    
    Args:
        character_data: The character data to save
        allow_overwrite: If True, allows overwriting existing files (for updates)
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

    # Only check for existing file if we're not allowing overwrites
    if not allow_overwrite and os.path.exists(file_path):
        return False, "char_exists_error"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4)
        logging.info(f"Character '{character_name}' saved to {file_path}")
        return True, "Character saved successfully."
    except Exception as e:
        logging.error(f"Error saving character '{character_name}': {e}")
        return False, f"Failed to save character file: {e}"

def duplicate_character(original_char_data, new_name):
    """
    Duplicates a character with a new name.
    """
    if not original_char_data or not new_name:
        return False, "Original character data and new name must be provided."

    original_name = original_char_data.get('name', 'N/A')
    logging.debug(f"Duplicating character '{original_name}' to new character '{new_name}'.")

    # Create a deep copy to avoid modifying the original data
    new_char_data = original_char_data.copy()

    # Update essential fields for the new character
    new_char_data['name'] = new_name
    new_char_data['id'] = new_name
    new_char_data['uuid'] = str(uuid.uuid4()) # Assign a new unique ID

    return save_character(new_char_data)

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

def rename_character(old_name, new_name):
    """
    Renames a character, which involves renaming the file and updating its content.
    """
    if not old_name or not new_name:
        return False, "Old and new names must be provided."

    if old_name == new_name:
        return True, "Names are the same, no action taken."

    base_char_dir = get_character_dir()
    old_file_path = None
    character_realm = None

    # Find the old character file and its realm
    for realm in REALMS:
        potential_path = os.path.join(base_char_dir, realm, f"{old_name}.json")
        if os.path.exists(potential_path):
            old_file_path = potential_path
            character_realm = realm
            break
    
    if not old_file_path:
        return False, f"Character '{old_name}' not found."

    # Check if the new name already exists in the same realm
    new_file_path = os.path.join(base_char_dir, character_realm, f"{new_name}.json")
    if os.path.exists(new_file_path):
        return False, "char_exists_error"

    try:
        # Read the content of the old file
        with open(old_file_path, 'r', encoding='utf-8') as f:
            char_data = json.load(f)

        # Update the name and id inside the data
        char_data['name'] = new_name
        char_data['id'] = new_name

        # Write the updated data to the new file
        with open(new_file_path, 'w', encoding='utf-8') as f:
            json.dump(char_data, f, indent=4)

        # Remove the old file
        os.remove(old_file_path)
        logging.info(f"Character '{old_name}' renamed to '{new_name}'.")
        return True, "Character renamed successfully."
    except (IOError, json.JSONDecodeError, OSError) as e:
        logging.error(f"Error renaming character from '{old_name}' to '{new_name}': {e}")
        # Clean up the new file if it was created
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        return False, f"Failed to rename character: {e}"

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

def move_character_to_realm(character_data, old_realm, new_realm):
    """
    Moves a character from one realm directory to another.
    
    Args:
        character_data (dict): The character data
        old_realm (str): The current realm
        new_realm (str): The new realm
        
    Returns:
        tuple: (success, message)
    """
    if old_realm == new_realm:
        return True, "No realm change needed."
    
    if new_realm not in REALMS:
        return False, f"Invalid realm: {new_realm}"
    
    character_name = character_data.get('name')
    if not character_name:
        return False, "Character name not found in data."
    
    # Get base character directory
    base_char_dir = get_character_dir()
    
    # Old and new file paths
    old_file_path = os.path.join(base_char_dir, old_realm, f"{character_name}.json")
    new_file_path = os.path.join(base_char_dir, new_realm, f"{character_name}.json")
    
    try:
        # Check if old file exists
        if not os.path.exists(old_file_path):
            return False, f"Original character file not found: {old_file_path}"
        
        # Create new realm directory if it doesn't exist
        new_realm_dir = os.path.join(base_char_dir, new_realm)
        os.makedirs(new_realm_dir, exist_ok=True)
        
        # Check if new file already exists
        if os.path.exists(new_file_path):
            return False, f"Character with same name already exists in {new_realm}."
        
        # Update character data with new realm
        character_data['realm'] = new_realm
        
        # Save to new location
        with open(new_file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4)
        
        # Remove old file
        os.remove(old_file_path)
        
        logging.info(f"Character '{character_name}' moved from {old_realm} to {new_realm}.")
        return True, f"Character moved to {new_realm} successfully."
        
    except Exception as e:
        logging.error(f"Error moving character '{character_name}' from {old_realm} to {new_realm}: {e}")
        # Try to clean up if new file was created but old wasn't deleted
        if os.path.exists(new_file_path) and os.path.exists(old_file_path):
            try:
                os.remove(new_file_path)
            except:
                pass
        return False, f"Failed to move character: {e}"