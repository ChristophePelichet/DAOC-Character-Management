"""
UI Validation Helper Module

Centralized validation functions for UI input fields and widgets.
Provides consistent validation patterns across dialogs and windows.

Functions follow naming convention: validate_{field_type}_{constraint}

Examples:
    from Functions.ui_validation_helper import validate_non_empty_text
    
    result = validate_non_empty_text(self.name_edit.text())
    if not result['valid']:
        self.show_error(result['message'])
"""

import logging
import re
from pathlib import Path


def validate_non_empty_text(text: str) -> dict:
    """
    Validate that text field is not empty after stripping whitespace.
    
    Args:
        text: Text to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (stripped value if valid)
        }
    """
    stripped = text.strip()
    if not stripped:
        return {
            'valid': False,
            'message': "Ce champ ne peut pas être vide",
            'value': ""
        }
    return {
        'valid': True,
        'message': "",
        'value': stripped
    }


def validate_text_field(text: str, allow_empty: bool = False, 
                       max_length: int = None) -> dict:
    """
    Validate text field with optional constraints.
    
    Args:
        text: Text to validate
        allow_empty: If True, empty text is valid
        max_length: Maximum allowed length (None for no limit)
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (stripped value if valid)
        }
    """
    stripped = text.strip()
    
    # Check empty
    if not stripped and not allow_empty:
        return {
            'valid': False,
            'message': "Ce champ ne peut pas être vide",
            'value': ""
        }
    
    # Check length
    if max_length and len(stripped) > max_length:
        return {
            'valid': False,
            'message': f"Le texte ne peut pas dépasser {max_length} caractères",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': stripped
    }


def validate_url_field(url: str) -> dict:
    """
    Validate Herald URL format.
    
    Checks for:
    - Non-empty
    - Contains 'herald' in URL
    - Valid URL structure (starts with http)
    
    Args:
        url: URL to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (stripped value if valid)
        }
    """
    stripped = url.strip()
    
    if not stripped:
        return {
            'valid': False,
            'message': "L'URL Herald ne peut pas être vide",
            'value': ""
        }
    
    if 'herald' not in stripped.lower():
        return {
            'valid': False,
            'message': "L'URL doit contenir 'herald'",
            'value': ""
        }
    
    if not (stripped.startswith('http://') or stripped.startswith('https://')):
        return {
            'valid': False,
            'message': "L'URL doit commencer par http:// ou https://",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': stripped
    }


def validate_numeric_field(value: str, min_val: int = None, 
                          max_val: int = None) -> dict:
    """
    Validate numeric field with optional min/max constraints.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value (None for no limit)
        max_val: Maximum allowed value (None for no limit)
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': int (converted value if valid, 0 if invalid)
        }
    """
    try:
        num = int(value.strip())
    except (ValueError, AttributeError):
        return {
            'valid': False,
            'message': "La valeur doit être un nombre",
            'value': 0
        }
    
    if min_val is not None and num < min_val:
        return {
            'valid': False,
            'message': f"La valeur doit être au minimum {min_val}",
            'value': 0
        }
    
    if max_val is not None and num > max_val:
        return {
            'valid': False,
            'message': f"La valeur doit être au maximum {max_val}",
            'value': 0
        }
    
    return {
        'valid': True,
        'message': "",
        'value': num
    }


def validate_filepath_exists(filepath: str) -> dict:
    """
    Validate that file path exists and is accessible.
    
    Args:
        filepath: File path to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (absolute path if valid, empty if invalid)
        }
    """
    if not filepath or not filepath.strip():
        return {
            'valid': False,
            'message': "Le chemin de fichier ne peut pas être vide",
            'value': ""
        }
    
    try:
        path = Path(filepath.strip())
        if not path.exists():
            return {
                'valid': False,
                'message': f"Le fichier n'existe pas : {filepath}",
                'value': ""
            }
        return {
            'valid': True,
            'message': "",
            'value': str(path.absolute())
        }
    except Exception as e:
        logging.error(f"Erreur lors de la validation du chemin: {e}")
        return {
            'valid': False,
            'message': f"Chemin invalide : {e}",
            'value': ""
        }


def validate_directory_exists(dirpath: str) -> dict:
    """
    Validate that directory path exists and is accessible.
    
    Args:
        dirpath: Directory path to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (absolute path if valid, empty if invalid)
        }
    """
    if not dirpath or not dirpath.strip():
        return {
            'valid': False,
            'message': "Le chemin de répertoire ne peut pas être vide",
            'value': ""
        }
    
    try:
        path = Path(dirpath.strip())
        if not path.is_dir():
            return {
                'valid': False,
                'message': f"Le répertoire n'existe pas : {dirpath}",
                'value': ""
            }
        return {
            'valid': True,
            'message': "",
            'value': str(path.absolute())
        }
    except Exception as e:
        logging.error(f"Erreur lors de la validation du répertoire: {e}")
        return {
            'valid': False,
            'message': f"Chemin invalide : {e}",
            'value': ""
        }


def validate_email_field(email: str) -> dict:
    """
    Validate email address format.
    
    Args:
        email: Email to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (stripped email if valid)
        }
    """
    stripped = email.strip()
    
    if not stripped:
        return {
            'valid': False,
            'message': "L'adresse email ne peut pas être vide",
            'value': ""
        }
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, stripped):
        return {
            'valid': False,
            'message': "Format email invalide",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': stripped
    }


def validate_not_selected(combo_text: str, placeholder: str = "") -> dict:
    """
    Validate that combo box has a selection (not placeholder/empty).
    
    Args:
        combo_text: Current combo box text
        placeholder: Expected placeholder text to avoid
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (text if valid)
        }
    """
    text = combo_text.strip()
    
    if not text or text == placeholder:
        return {
            'valid': False,
            'message': "Veuillez sélectionner une option",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': text
    }


def validate_multiple_selections(selections: list, min_count: int = 1) -> dict:
    """
    Validate that minimum number of items are selected.
    
    Args:
        selections: List of selected items
        min_count: Minimum required selections
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': list (selections if valid, empty if invalid)
        }
    """
    if not selections or len(selections) < min_count:
        return {
            'valid': False,
            'message': f"Au moins {min_count} sélection(s) requise(s)",
            'value': []
        }
    
    return {
        'valid': True,
        'message': "",
        'value': selections
    }


def validate_character_name(name: str) -> dict:
    """
    Validate character name format.
    
    Checks for:
    - Non-empty
    - Allowed characters (letters, numbers, hyphens, apostrophes)
    - Not too long
    
    Args:
        name: Character name to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (stripped name if valid)
        }
    """
    stripped = name.strip()
    
    if not stripped:
        return {
            'valid': False,
            'message': "Le nom du personnage ne peut pas être vide",
            'value': ""
        }
    
    if len(stripped) > 30:
        return {
            'valid': False,
            'message': "Le nom du personnage ne peut pas dépasser 30 caractères",
            'value': ""
        }
    
    # Allow letters, numbers, hyphens, apostrophes, spaces
    if not re.match(r"^[a-zA-Z0-9\-\' ]+$", stripped):
        return {
            'valid': False,
            'message': "Le nom contient des caractères non autorisés",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': stripped
    }


def validate_guild_name(guild: str) -> dict:
    """
    Validate guild name format.
    
    Checks for:
    - Can be empty (optional field)
    - If provided, must be valid characters
    - Not too long
    
    Args:
        guild: Guild name to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (stripped guild if valid)
        }
    """
    stripped = guild.strip()
    
    # Empty guild is allowed (optional field)
    if not stripped:
        return {
            'valid': True,
            'message': "",
            'value': ""
        }
    
    if len(stripped) > 50:
        return {
            'valid': False,
            'message': "Le nom de guilde ne peut pas dépasser 50 caractères",
            'value': ""
        }
    
    # Allow letters, numbers, hyphens, apostrophes, spaces, special chars for guilds
    if not re.match(r"^[a-zA-Z0-9\-\'\\ &()]+$", stripped):
        return {
            'valid': False,
            'message': "Le nom de guilde contient des caractères non autorisés",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': stripped
    }


def validate_realm_selection(realm: str) -> dict:
    """
    Validate that a realm has been selected.
    
    Args:
        realm: Selected realm name
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (realm if valid)
        }
    """
    if not realm or not realm.strip():
        return {
            'valid': False,
            'message': "Veuillez sélectionner un royaume",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': realm.strip()
    }


def validate_class_selection(class_name: str) -> dict:
    """
    Validate that a class has been selected.
    
    Args:
        class_name: Selected class name
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (class if valid)
        }
    """
    if not class_name or not class_name.strip():
        return {
            'valid': False,
            'message': "Veuillez sélectionner une classe",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': class_name.strip()
    }


def validate_race_selection(race: str) -> dict:
    """
    Validate that a race has been selected.
    
    Args:
        race: Selected race name
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': str (race if valid)
        }
    """
    if not race or not race.strip():
        return {
            'valid': False,
            'message': "Veuillez sélectionner une race",
            'value': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'value': race.strip()
    }


def validate_selection_pair(first: str, second: str, field_names: tuple = ("Champ 1", "Champ 2")) -> dict:
    """
    Validate that both fields in a pair have selections.
    
    Args:
        first: First field value
        second: Second field value
        field_names: Tuple of field names for error message
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (empty if valid),
            'value': bool
        }
    """
    if not first or not first.strip() or not second or not second.strip():
        return {
            'valid': False,
            'message': f"Veuillez sélectionner {field_names[0]} et {field_names[1]}",
            'value': False
        }
    
    return {
        'valid': True,
        'message': "",
        'value': True
    }


# =============================================================================
# WRAPPER FUNCTIONS FOR SPECIFIC DIALOGS
# =============================================================================

def validate_basic_character_info(character_name: str, guild_name: str, 
                                  herald_url: str) -> dict:
    """
    Validate all basic character information fields.
    
    Used in: CharacterSheetWindow.save_basic_info()
    
    Validates:
    - Character name (not required in this context)
    - Guild name (optional)
    - Herald URL (optional)
    
    Args:
        character_name: Character name to validate (may be unused)
        guild_name: Guild name to validate
        herald_url: Herald URL to validate (optional)
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (error message if invalid),
            'guild': str (validated guild),
            'url': str (validated URL)
        }
    """
    # Validate guild (optional field)
    guild_result = validate_guild_name(guild_name)
    if not guild_result['valid']:
        return {
            'valid': False,
            'message': guild_result['message'],
            'guild': "",
            'url': ""
        }
    
    # Validate Herald URL (optional field - only if provided)
    validated_url = ""
    if herald_url.strip():
        url_result = validate_url_field(herald_url)
        if not url_result['valid']:
            return {
                'valid': False,
                'message': url_result['message'],
                'guild': "",
                'url': ""
            }
        validated_url = url_result['value']
    
    return {
        'valid': True,
        'message': "",
        'guild': guild_result['value'],
        'url': validated_url
    }


def validate_character_rename(new_name: str) -> dict:
    """
    Validate character name for rename operation.
    
    Used in: CharacterSheetWindow.rename_character()
    
    Args:
        new_name: New character name to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (error message if invalid),
            'value': str (validated name)
        }
    """
    return validate_character_name(new_name)


def validate_new_character_creation(character_name: str) -> dict:
    """
    Validate character name for new character creation.
    
    Used in: NewCharacterDialog.get_data()
    
    Args:
        character_name: Character name to validate
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (error message if invalid),
            'value': str (validated name)
        }
    """
    return validate_character_name(character_name)


def validate_new_character_dialog_data(character_name: str, guild_name: str) -> dict:
    """
    Validate all fields for new character dialog (character name and optional guild).
    
    Used in: NewCharacterDialog.get_data()
    
    Validates:
    - Character name (required)
    - Guild name (optional)
    
    Args:
        character_name: Character name to validate
        guild_name: Guild name to validate (optional)
        
    Returns:
        dict: {
            'valid': bool,
            'message': str (error message if invalid),
            'name': str (validated name),
            'guild': str (validated guild)
        }
    """
    # Validate character name (required)
    name_result = validate_character_name(character_name)
    if not name_result['valid']:
        return {
            'valid': False,
            'message': name_result['message'],
            'name': "",
            'guild': ""
        }
    
    # Validate guild (optional field)
    guild_result = validate_guild_name(guild_name)
    if not guild_result['valid']:
        return {
            'valid': False,
            'message': guild_result['message'],
            'name': "",
            'guild': ""
        }
    
    return {
        'valid': True,
        'message': "",
        'name': name_result['value'],
        'guild': guild_result['value']
    }

