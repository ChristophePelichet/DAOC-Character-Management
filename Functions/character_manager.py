import os
import json
import uuid
import logging
from Functions.config_manager import config
from Functions.path_manager import get_base_path
from Functions.logging_manager import get_logger, log_with_action, LOGGER_CHARACTER

# Get CHARACTER logger
logger = get_logger(LOGGER_CHARACTER)

# Lazy load to avoid circular imports
_data_manager = None

def _get_data_manager():
    """Lazy initialization of DataManager to avoid circular imports"""
    global _data_manager
    if _data_manager is None:
        from Functions.data_manager import DataManager
        _data_manager = DataManager()
    return _data_manager

def get_realms():
    """Returns the list of realms from JSON data"""
    return _get_data_manager().get_realms()

# Keep REALMS as a callable for backward compatibility
REALMS = get_realms()

REALM_ICONS = {
    "Albion": "albion_logo.png",
    "Hibernia": "hibernia_logo.png",
    "Midgard": "midgard_logo.png"
}

def get_character_dir():
    """Returns the configured character directory."""
    default_path = os.path.join(get_base_path(), "Characters")
    return config.get("character_folder") or default_path

def create_character_data(name, realm, season, server, level=1, page=1, guild="", race="", class_name=""):
    """
    Creates a dictionary for a new character.
    The 'id' is now the character name for file system identification.
    A separate 'uuid' is kept for internal robustness if needed.
    """
    log_with_action(logger, "debug", f"Creating character data for '{name}' in {realm}", action="CREATE")
    return {
        'id': name,  # The main identifier is now the name
        'uuid': str(uuid.uuid4()),  # Still keep a unique ID internally
        'name': name,
        'realm': realm,
        'race': race,
        'class': class_name,
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
    inside a subfolder corresponding to its season and realm.
    e.g., 'Characters/S1/Albion/Merlin.json'
    
    Args:
        character_data: The character data to save
        allow_overwrite: If True, allows overwriting existing files (for updates)
    """
    base_char_dir = get_character_dir()

    character_name = character_data.get('name')
    character_realm = character_data.get('realm')
    character_season = character_data.get('season', 'S1')  # Default to S1 if not specified

    if not character_name:
        return False, "Character data must contain a 'name'."
    if not character_realm or character_realm not in REALMS:
        return False, f"Invalid or missing realm for character '{character_name}'."
    if not character_season:
        character_season = 'S1'
        logging.warning(f"Character '{character_name}' has no season, defaulting to S1")

    # Create the season/realm-specific directory
    season_dir = os.path.join(base_char_dir, character_season)
    char_dir = os.path.join(season_dir, character_realm)
    
    # Log if creating the directory structure for the first time
    if not os.path.exists(char_dir):
        os.makedirs(char_dir, exist_ok=True)
        log_with_action(logger, "info", f"Created character directory: {char_dir}", action="DIRECTORY")
    else:
        os.makedirs(char_dir, exist_ok=True)

    file_path = os.path.join(char_dir, f"{character_name}.json")

    # Only check for existing file if we're not allowing overwrites
    if not allow_overwrite and os.path.exists(file_path):
        log_with_action(logger, "warning", f"Character '{character_name}' already exists at {file_path}", action="CREATE")
        return False, "char_exists_error"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4)
        log_with_action(logger, "info", f"Character '{character_name}' saved to {file_path}", action="CREATE")
        return True, "Character saved successfully."
    except Exception as e:
        error_msg = f"Error saving character '{character_name}': {e}"
        log_with_action(logger, "error", error_msg, action="ERROR")
        return False, f"Failed to save character file: {e}"

def duplicate_character(original_char_data, new_name):
    """
    Duplicates a character with a new name.
    """
    if not original_char_data or not new_name:
        return False, "Original character data and new name must be provided."

    original_name = original_char_data.get('name', 'N/A')
    log_with_action(logger, "info", f"Duplicating character '{original_name}' to new character '{new_name}'", action="DUPLICATE")

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
    
    log_with_action(logger, "debug", f"Loaded {len(characters)} characters from disk", action="LOAD")
    return sorted(characters, key=lambda c: c.get('name', '').lower())

def rename_character(old_name, new_name):
    """
    Renames a character, which involves renaming the file and updating its content.
    Works with new Season/Realm structure.
    """
    if not old_name or not new_name:
        return False, "Old and new names must be provided."

    if old_name == new_name:
        log_with_action(logger, "debug", f"Rename attempt: old and new names are the same ('{old_name}')", action="RENAME")
        return True, "Names are the same, no action taken."

    base_char_dir = get_character_dir()
    old_file_path = None
    character_realm = None
    character_season = None

    # Find the old character file by searching through Season/Realm folders
    for root, dirs, files in os.walk(base_char_dir):
        if f"{old_name}.json" in files:
            old_file_path = os.path.join(root, f"{old_name}.json")
            # Extract season and realm from path
            path_parts = root.replace(base_char_dir, "").strip(os.sep).split(os.sep)
            if len(path_parts) >= 2:
                character_season = path_parts[0]
                character_realm = path_parts[1]
            break
    
    if not old_file_path:
        log_with_action(logger, "warning", f"Character '{old_name}' not found for rename", action="ERROR")
        return False, f"Character '{old_name}' not found."

    # Check if the new name already exists in the same season/realm
    new_file_path = os.path.join(base_char_dir, character_season, character_realm, f"{new_name}.json")
    if os.path.exists(new_file_path):
        log_with_action(logger, "warning", f"Target name '{new_name}' already exists", action="ERROR")
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
        log_with_action(logger, "info", f"Character renamed from '{old_name}' to '{new_name}'", action="RENAME")
        return True, "Character renamed successfully."
    except (IOError, json.JSONDecodeError, OSError) as e:
        error_msg = f"Error renaming character from '{old_name}' to '{new_name}': {e}"
        log_with_action(logger, "error", error_msg, action="ERROR")
        # Clean up the new file if it was created
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        return False, f"Failed to rename character: {e}"

def delete_character(character_name):
    """
    Deletes a character's JSON file based on their name.
    Works with new Season/Realm structure.
    """
    if not character_name:
        return False, "Character name not provided."

    base_char_dir = get_character_dir()
    file_to_delete = None

    # Search for the character file by walking through Season/Realm folders
    for root, dirs, files in os.walk(base_char_dir):
        if f"{character_name}.json" in files:
            file_to_delete = os.path.join(root, f"{character_name}.json")
            break

    if file_to_delete:
        try:
            os.remove(file_to_delete)
            log_with_action(logger, "info", f"Character '{character_name}' deleted from {file_to_delete}", action="DELETE")
            return True, "Character deleted successfully."
        except OSError as e:
            error_msg = f"Error deleting file {file_to_delete}: {e}"
            log_with_action(logger, "error", error_msg, action="ERROR")
            return False, f"Could not delete character file: {e}"
    else:
        log_with_action(logger, "warning", f"Attempted to delete non-existent character '{character_name}'", action="ERROR")
        return False, "Character file not found."

def move_character_to_realm(character_data, old_realm, new_realm):
    """
    Moves a character from one realm directory to another.
    Works with new Season/Realm structure.
    
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
    character_season = character_data.get('season', 'S1')
    if not character_name:
        return False, "Character name not found in data."
    
    # Get base character directory
    base_char_dir = get_character_dir()
    
    # Old and new file paths (within same season)
    old_file_path = os.path.join(base_char_dir, character_season, old_realm, f"{character_name}.json")
    new_file_path = os.path.join(base_char_dir, character_season, new_realm, f"{character_name}.json")
    
    try:
        # Check if old file exists
        if not os.path.exists(old_file_path):
            return False, f"Original character file not found: {old_file_path}"
        
        # Create new season/realm directory if it doesn't exist
        new_realm_dir = os.path.join(base_char_dir, character_season, new_realm)
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
        
        log_with_action(logger, "info", f"Character '{character_name}' moved from {old_realm} to {new_realm}", action="UPDATE")
        return True, f"Character moved to {new_realm} successfully."
        
    except Exception as e:
        log_with_action(logger, "error", f"Error moving character '{character_name}' from {old_realm} to {new_realm}: {e}", action="ERROR")
        # Try to clean up if new file was created but old wasn't deleted
        if os.path.exists(new_file_path) and os.path.exists(old_file_path):
            try:
                os.remove(new_file_path)
            except:
                pass
        return False, f"Failed to move character: {e}"