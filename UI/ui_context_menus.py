"""
UI context menu builder module.

This module provides functions for creating and displaying context menus
in various UI dialogs with consistent styling and behavior.
"""

from PySide6.QtWidgets import QMenu
from Functions.language_manager import lang


def ui_show_armor_context_menu(parent, table, position, filename, callbacks):
    """
    Show armor context menu with download and delete actions.

    Creates and displays a context menu for armor files with standard actions.
    Actions are connected to provided callback functions.

    Args:
        parent: Parent widget (dialog/window) for menu ownership
        table: QTableWidget to get viewport from for menu positioning
        position: QPoint position where menu was requested (from right-click)
        filename: Armor filename for the selected row
        callbacks: Dictionary with action callback functions:
                  - 'download': callable(filename) - Download/export handler
                  - 'delete': callable(filename) - Delete armor handler

    Returns:
        None (displays menu directly)

    Example:
        >>> callbacks = {
        ...     'download': self.download_armor,
        ...     'delete': self.delete_armor,
        ... }
        >>> ui_show_armor_context_menu(
        ...     self, self.table, position, filename, callbacks
        ... )

    Note:
        - All action labels are translated via lang.get()
        - Menu is displayed at cursor position in viewport coordinates
        - Each callback receives filename as parameter
    """
    # Create context menu
    menu = QMenu(parent)

    # Download action
    download_action = menu.addAction(
        lang.get("armoury_dialog.context_menu.download")
    )
    download_action.triggered.connect(
        lambda: callbacks['download'](filename)
    )

    menu.addSeparator()

    # Delete action
    delete_action = menu.addAction(
        lang.get("armoury_dialog.context_menu.delete")
    )
    delete_action.triggered.connect(lambda: callbacks['delete'](filename))

    # Show menu at cursor position
    menu.exec_(table.viewport().mapToGlobal(position))
