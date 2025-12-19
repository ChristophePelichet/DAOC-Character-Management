"""
Character rename handler module.

This module provides functions for handling character renaming operations with
validation and JSON persistence.
"""

from typing import Tuple


def character_rename_with_validation(
    character_data: dict,
    new_name: str,
    rename_function,
) -> Tuple[bool, str]:
    """
    Rename a character with validation and persistence.

    Handles the complete character renaming workflow including validation,
    JSON file updates, and character data synchronization.

    Args:
        character_data: Dictionary containing character data to update
        new_name: New name for the character (pre-validated)
        rename_function: Function to call for JSON file rename
                        (from Functions.character_manager.rename_character)

    Returns:
        Tuple of (success: bool, message: str)
        - True with empty string on success
        - False with error message on failure

    Raises:
        Exception: If character_data is invalid or rename_function fails

    Example:
        >>> success, msg = character_rename_with_validation(
        ...     char_data, "NewName", rename_character
        ... )
        >>> if success:
        ...     print("Character renamed successfully")
    """
    try:
        old_name = character_data.get('name', '')

        if not old_name:
            return False, "Character name not found in data"

        # Call the rename function to update JSON file
        success, msg = rename_function(old_name, new_name)

        if not success:
            return False, msg

        # Update character data with new name
        character_data['name'] = new_name
        character_data['id'] = new_name

        return True, ""

    except Exception as e:
        return False, f"Rename error: {str(e)}"
