"""
UI File Dialog Wrapper Module

Centralizes all QFileDialog usage for consistent file selection behavior across dialogs.

This module provides reusable wrappers for file and directory selection operations,
reducing code duplication and ensuring consistent user experience.

Functions:
    dialog_open_file() - Open file selection dialog
    dialog_save_file() - Save file dialog
    dialog_select_directory() - Directory selection with optional initial path
    dialog_open_armor_file() - Armor file selection (with filters)
    dialog_select_backup_path() - Backup directory selection
"""

from PySide6.QtWidgets import QFileDialog
from Functions.language_manager import lang


def dialog_open_file(
    parent,
    title_key: str,
    filter_key: str = "",
    initial_dir: str = ""
) -> str:
    """
    Open file selection dialog.

    Parameters:
        parent: Parent widget
        title_key: Translation key for dialog title
        filter_key: Translation key for file filter (e.g., "All Files")
        initial_dir: Initial directory path (optional)

    Returns:
        str: Selected file path, empty string if cancelled
    """
    title = lang.get(title_key)
    file_filter = lang.get(filter_key) if filter_key else lang.get("all_files")

    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        title,
        initial_dir,
        file_filter
    )

    return file_path if file_path else ""


def dialog_save_file(
    parent,
    title_key: str,
    default_filename: str = "",
    filter_key: str = ""
) -> str:
    """
    Open save file dialog.

    Parameters:
        parent: Parent widget
        title_key: Translation key for dialog title
        default_filename: Default filename (suggestion)
        filter_key: Translation key for file filter

    Returns:
        str: Selected save path, empty string if cancelled
    """
    title = lang.get(title_key)
    file_filter = lang.get(filter_key) if filter_key else lang.get("all_files")

    save_path, _ = QFileDialog.getSaveFileName(
        parent,
        title,
        default_filename,
        file_filter
    )

    return save_path if save_path else ""


def dialog_select_directory(
    parent,
    title_key: str,
    initial_dir: str = ""
) -> str:
    """
    Open directory selection dialog.

    Parameters:
        parent: Parent widget
        title_key: Translation key for dialog title
        initial_dir: Initial directory path (optional)

    Returns:
        str: Selected directory path, empty string if cancelled
    """
    title = lang.get(title_key)

    selected_dir = QFileDialog.getExistingDirectory(
        parent,
        title,
        initial_dir
    )

    return selected_dir if selected_dir else ""


def dialog_open_armor_file(parent) -> str:
    """
    Open armor file selection dialog.

    Wrapper for armor template file selection with appropriate title and filters.

    Parameters:
        parent: Parent widget

    Returns:
        str: Selected file path, empty string if cancelled
    """
    return dialog_open_file(
        parent,
        title_key="cookie_manager.browse_dialog_title",
        filter_key="cookie_manager.browse_dialog_filter",
        initial_dir=""
    )


def dialog_select_backup_path(
    parent,
    current_path: str = ""
) -> str:
    """
    Open backup directory selection dialog.

    Wrapper for backup path selection with current path as default.

    Parameters:
        parent: Parent widget
        current_path: Current path (used as initial directory)

    Returns:
        str: Selected directory path, empty string if cancelled
    """
    return dialog_select_directory(
        parent,
        title_key="backup_path_dialog_title",
        initial_dir=current_path
    )
