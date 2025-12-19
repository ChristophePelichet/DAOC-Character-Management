"""
UI Getters Module - Simple data retrieval utilities for dialogs.

This module provides utility functions for retrieving data from UI components
without complex business logic. These functions are simple wrappers around
Qt widget queries, designed for code reusability and maintainability.

Functions:
    ui_get_visibility_config() - Get checkbox visibility states from a dialog
    ui_get_selected_category() - Get selected radio button category
    ui_get_selected_changes() - Get selected changes from a table widget
"""

from PyQt5.QtCore import Qt


def ui_get_visibility_config(checkboxes: dict) -> dict:
    """
    Get the visibility state of all checkboxes in a dictionary.

    This function returns a dict mapping checkbox keys to their checked state.
    Used primarily for column visibility configuration in table settings.

    Args:
        checkboxes (dict): Dictionary mapping keys to QCheckBox widgets.
            Format: {key: QCheckBox instance, ...}

    Returns:
        dict: Configuration dict mapping keys to visibility state.
            Format: {key: bool, ...} where bool is checkbox.isChecked()

    Example:
        >>> checkboxes = {"col1": QCheckBox(), "col2": QCheckBox()}
        >>> checkboxes["col1"].setChecked(True)
        >>> config = ui_get_visibility_config(checkboxes)
        >>> config
        {'col1': True, 'col2': False}
    """
    return {key: checkbox.isChecked() for key, checkbox in checkboxes.items()}


def ui_get_selected_category(category_buttons) -> str:
    """
    Get the selected category from a group of radio buttons.

    This function retrieves the category key from the currently checked
    radio button in a button group. Each button should have a "category_key"
    property set.

    Args:
        category_buttons: QButtonGroup instance with category radio buttons.
            Each button should have property("category_key") returning a str.

    Returns:
        str: The category_key property of the checked button, or "unknown"
            if no button is selected.

    Example:
        >>> button_group = QButtonGroup()
        >>> button1 = QRadioButton("Category A")
        >>> button1.setProperty("category_key", "category_a")
        >>> button_group.addButton(button1)
        >>> button_group.button(0).setChecked(True)
        >>> category = ui_get_selected_category(button_group)
        >>> category
        'category_a'
    """
    checked_button = category_buttons.checkedButton()
    if checked_button:
        return checked_button.property("category_key")
    return "unknown"


def ui_get_selected_changes(changes_table) -> dict:
    """
    Get all selected changes from a changes table widget.

    This function iterates through all rows in a table widget and collects
    the changes (field-value pairs) from rows where the checkbox is checked.
    Each row must have the checkbox and field data stored in Qt.UserRole.

    Args:
        changes_table: QTableWidget instance with changes data.
            Row structure:
            - Column 0, Qt.UserRole: QCheckBox widget
            - Column 0, Qt.UserRole + 1: field name (str)
            - Column 0, Qt.UserRole + 2: raw value

    Returns:
        dict: Selected changes mapping field names to their raw values.
            Format: {field_name: value, ...}
            Only includes rows where the checkbox is checked.

    Example:
        >>> table = QTableWidget()
        >>> # Setup row with checkbox, field, and value in UserRole
        >>> item = QTableWidgetItem()
        >>> item.setData(Qt.UserRole, checkbox)
        >>> item.setData(Qt.UserRole + 1, "character_name")
        >>> item.setData(Qt.UserRole + 2, "NewName")
        >>> table.setItem(0, 0, item)
        >>> if checkbox.isChecked():
        ...     selected = ui_get_selected_changes(table)
        ...     selected
        ...     {'character_name': 'NewName'}
    """
    selected = {}

    for row in range(changes_table.rowCount()):
        item = changes_table.item(row, 0)
        if item:
            checkbox = item.data(Qt.UserRole)
            field = item.data(Qt.UserRole + 1)
            value_raw = item.data(Qt.UserRole + 2)

            if checkbox and checkbox.isChecked():
                selected[field] = value_raw

    return selected
