"""
Herald UI Wrappers Module - Simple wrapper functions for Herald-related UI operations.

This module provides lightweight wrapper functions that connect UI components to
Herald business logic without complex state management.

Functions:
    herald_ui_update_rvr_stats() - Trigger RvR stats update from Herald URL
"""

from Functions.character_actions_manager import character_herald_update_rvr_stats


def herald_ui_update_rvr_stats(dialog, herald_url_edit) -> None:
    """
    Update RvR statistics from Herald URL entered in the dialog.

    This function is a simple wrapper that extracts the Herald URL from the
    UI text field and triggers the RvR stats update operation. It serves as
    a bridge between UI components and the business logic in character_actions_manager.

    Args:
        dialog: The parent dialog window (CharacterSheetWindow instance).
            Must have access to parent_app and other required attributes.
        herald_url_edit: QLineEdit widget containing the Herald URL.

    Returns:
        None

    Example:
        >>> from PyQt5.QtWidgets import QLineEdit
        >>> url_edit = QLineEdit()
        >>> url_edit.setText("https://herald.daoce.co.uk/character/...")
        >>> herald_ui_update_rvr_stats(dialog, url_edit)
    """
    url = herald_url_edit.text().strip()
    character_herald_update_rvr_stats(dialog, url)
