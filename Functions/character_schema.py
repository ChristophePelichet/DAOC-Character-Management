"""
Character Schema Definition and Validation
Defines the expected structure for character JSON files and provides validation functions.
"""

import re
from typing import Dict, Any, List, Tuple

# ============================================================================
# FIELD DEFINITIONS
# ============================================================================

# Required fields that MUST be present in every character file
REQUIRED_FIELDS = {
    "name": str,
    "realm": str,      # Albion, Hibernia, Midgard
    "class": str,
    "race": str,
    "level": int,
    "season": str,     # S1, S2, S3, etc.
    "server": str      # Eden
}

# Optional fields with their default values
OPTIONAL_FIELDS = {
    "id": "",
    "page": 1,
    "guild": "",
    "realm_rank": "",           # Code format: "1L0", "5L3", etc.
    "realm_title": "",          # Text format: "Guardian", "Warlord", etc.
    "realm_points": 0,
    "url": "",                  # Herald URL
    "created_date": "",
    "modified_date": "",
    "armor": {},                # Armor configuration
    "stats": {},                # Character statistics
    "achievements": []          # List of achievements
}

# Expected types for all fields (required + optional)
FIELD_TYPES = {
    # Required
    "name": str,
    "realm": str,
    "class": str,
    "race": str,
    "level": int,
    "season": str,
    "server": str,
    # Optional
    "id": str,
    "page": int,
    "guild": str,
    "realm_rank": str,
    "realm_title": str,
    "realm_points": int,
    "url": str,
    "created_date": str,
    "modified_date": str,
    "armor": dict,
    "stats": dict,
    "achievements": list
}

# Valid realm values
VALID_REALMS = ["Albion", "Hibernia", "Midgard"]

# Valid server values
VALID_SERVERS = ["Eden"]

# Default values
DEFAULT_SEASON = "S3"  # Current active season
DEFAULT_SERVER = "Eden"

# ============================================================================
# SCHEMA FUNCTIONS
# ============================================================================

def get_character_schema() -> Dict[str, Any]:
    """
    Returns the complete expected structure for character JSON files.
    
    Returns:
        dict: Complete character schema with all fields and default values
    """
    schema = {}
    
    # Add required fields with empty/default values
    for field, field_type in REQUIRED_FIELDS.items():
        if field_type == str:
            schema[field] = ""
        elif field_type == int:
            schema[field] = 0
        else:
            schema[field] = None
    
    # Add optional fields with their defaults
    schema.update(OPTIONAL_FIELDS.copy())
    
    return schema

def get_default_season() -> str:
    """
    Returns the default season for characters.
    
    Returns:
        str: Default season identifier (e.g., "S3")
    """
    return DEFAULT_SEASON

def get_default_server() -> str:
    """
    Returns the default server for characters.
    
    Returns:
        str: Default server name (e.g., "Eden")
    """
    return DEFAULT_SERVER

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_season_format(season: str) -> bool:
    """
    Validates that season matches expected format (S followed by digits).
    
    Args:
        season: Season string to validate
        
    Returns:
        bool: True if valid format, False otherwise
        
    Examples:
        >>> validate_season_format("S3")
        True
        >>> validate_season_format("S10")
        True
        >>> validate_season_format("Season3")
        False
        >>> validate_season_format("")
        False
    """
    if not season or not isinstance(season, str):
        return False
    
    return bool(re.match(r'^S\d+$', season.strip()))

def validate_realm(realm: str) -> bool:
    """
    Validates that realm is one of the valid values.
    
    Args:
        realm: Realm string to validate
        
    Returns:
        bool: True if valid realm, False otherwise
    """
    return realm in VALID_REALMS

def validate_server(server: str) -> bool:
    """
    Validates that server is one of the valid values.
    
    Args:
        server: Server string to validate
        
    Returns:
        bool: True if valid server, False otherwise
    """
    return server in VALID_SERVERS

def validate_character_data(char_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates character data structure and content.
    
    Args:
        char_data: Character data dictionary to validate
        
    Returns:
        tuple: (is_valid: bool, errors: List[str])
            - is_valid: True if all validations pass
            - errors: List of validation error messages
            
    Validation checks:
        1. Data is a dictionary
        2. All required fields are present
        3. Field types are correct
        4. Realm is valid
        5. Server is valid
        6. Season format is valid (if present)
        7. Level is positive integer
    """
    errors = []
    
    # Check if data is a dictionary
    if not isinstance(char_data, dict):
        errors.append("Character data must be a dictionary")
        return False, errors
    
    # Check required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in char_data:
            errors.append(f"Missing required field: '{field}'")
            continue
        
        # Check type
        value = char_data[field]
        if not isinstance(value, expected_type):
            errors.append(f"Field '{field}' has wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
    
    # Validate realm
    if "realm" in char_data:
        if not validate_realm(char_data["realm"]):
            errors.append(f"Invalid realm: '{char_data['realm']}'. Must be one of {VALID_REALMS}")
    
    # Validate server
    if "server" in char_data:
        if not validate_server(char_data["server"]):
            errors.append(f"Invalid server: '{char_data['server']}'. Must be one of {VALID_SERVERS}")
    
    # Validate season format (if present)
    if "season" in char_data and char_data["season"]:
        if not validate_season_format(char_data["season"]):
            errors.append(f"Invalid season format: '{char_data['season']}'. Must match pattern 'S<number>' (e.g., S1, S2, S3)")
    
    # Validate level
    if "level" in char_data:
        level = char_data["level"]
        if isinstance(level, int):
            if level < 1 or level > 50:
                errors.append(f"Invalid level: {level}. Must be between 1 and 50")
        else:
            errors.append(f"Level must be an integer, got {type(level).__name__}")
    
    # Check optional fields types (if present)
    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in char_data:
            value = char_data[field]
            if value is not None and not isinstance(value, expected_type):
                errors.append(f"Optional field '{field}' has wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def normalize_character_data(char_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes character data by adding missing optional fields with defaults.
    Does NOT modify required fields.
    
    Args:
        char_data: Original character data
        
    Returns:
        dict: Normalized character data with all fields
    """
    normalized = char_data.copy()
    
    # Add missing optional fields with defaults
    for field, default_value in OPTIONAL_FIELDS.items():
        if field not in normalized:
            if isinstance(default_value, (dict, list)):
                normalized[field] = default_value.copy()
            else:
                normalized[field] = default_value
    
    # Normalize season if missing or invalid
    if "season" not in normalized or not normalized["season"]:
        normalized["season"] = get_default_season()
    elif not validate_season_format(normalized["season"]):
        normalized["season"] = get_default_season()
    
    # Normalize server if missing
    if "server" not in normalized or not normalized["server"]:
        normalized["server"] = get_default_server()
    
    return normalized

def get_character_info_summary(char_data: Dict[str, Any]) -> str:
    """
    Generates a human-readable summary of character information.
    
    Args:
        char_data: Character data dictionary
        
    Returns:
        str: Formatted summary string
    """
    name = char_data.get("name", "Unknown")
    realm = char_data.get("realm", "Unknown")
    char_class = char_data.get("class", "Unknown")
    level = char_data.get("level", 0)
    season = char_data.get("season", "Unknown")
    
    return f"{name} - {realm} {char_class} (Level {level}, {season})"

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Valid character
    valid_char = {
        "name": "Excalibur",
        "realm": "Albion",
        "class": "Paladin",
        "race": "Briton",
        "level": 50,
        "season": "S3",
        "server": "Eden",
        "guild": "Knights of the Round",
        "realm_rank": "5L3",
        "realm_title": "Warlord"
    }
    
    is_valid, errors = validate_character_data(valid_char)
    print(f"Valid character: {is_valid}")
    print(f"Summary: {get_character_info_summary(valid_char)}")
    
    # Example: Invalid character (missing required fields)
    invalid_char = {
        "name": "TestChar",
        "level": 50
    }
    
    is_valid, errors = validate_character_data(invalid_char)
    print(f"\nInvalid character: {is_valid}")
    print(f"Errors: {errors}")
    
    # Example: Normalization
    partial_char = {
        "name": "PartialChar",
        "realm": "Hibernia",
        "class": "Druid",
        "race": "Celt",
        "level": 30
        # Missing season, server, and optional fields
    }
    
    normalized = normalize_character_data(partial_char)
    print(f"\nNormalized character:")
    print(f"  Season: {normalized['season']}")
    print(f"  Server: {normalized['server']}")
    print(f"  Guild: '{normalized['guild']}'")
