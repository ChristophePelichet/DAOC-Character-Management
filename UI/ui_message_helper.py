"""
UI Message Helper Module

Centralized message box handling for consistent UI feedback across the application.
All messages are translated via lang.get() and can include dynamic parameters.

Functions:
    msg_show_success() - Display success message
    msg_show_error() - Display error message with logging
    msg_show_warning() - Display warning message with logging
    msg_show_confirmation() - Show yes/no confirmation dialog
    msg_show_info_with_details() - Display info with formatted details

Example:
    msg_show_success(
        parent_window,
        "dialogs.titles.success",
        "character_sheet.messages.rank_update_success",
        level="Level 10",
        rp=5000
    )

    if msg_show_confirmation(parent_window, "Delete?", "Really delete this item?"):
        # User clicked Yes
        pass
"""

from PySide6.QtWidgets import QMessageBox
from UI.ui_sound_manager import SilentMessageBox

from Functions.language_manager import lang
from Functions.debug_logging_manager import get_logger, log_with_action, LOGGER_CHARACTER


logger_ui = get_logger(LOGGER_CHARACTER)


def msg_show_success(parent, title_key: str, message_key: str, **kwargs) -> None:
    """
    Display a success message dialog.

    Args:
        parent: Parent widget for the message box
        title_key: Language key for dialog title (e.g., "dialogs.titles.success")
        message_key: Language key for message text
        **kwargs: Dynamic parameters for message formatting (e.g., level="Level 10")

    Example:
        msg_show_success(
            self,
            "dialogs.titles.success",
            "character_sheet.messages.rank_update_success",
            level="Level 10",
            rp=5000
        )
    """
    title = lang.get(title_key, default="Success")
    message = lang.get(
        message_key, default="Operation completed successfully", **kwargs
    )

    SilentMessageBox.information(parent, title, message)
    logger_ui.info(f"Success: {message_key}")


def msg_show_error(parent, title_key: str, message_key: str, **kwargs) -> None:
    """
    Display an error message dialog with automatic logging.

    Args:
        parent: Parent widget for the message box
        title_key: Language key for dialog title (e.g., "titles.error")
        message_key: Language key for error message, or plain text if starts with "!"
        **kwargs: Dynamic parameters for message formatting

    Note:
        If message_key starts with "!", it will be treated as plain text
        instead of a lang key. Example: msg_show_error(
            self, "titles.error", "!Plain text error message"
        )

    Example:
        msg_show_error(
            self,
            "titles.error",
            "character_sheet.messages.save_error",
            error="File not found"
        )
    """
    title = lang.get(title_key, default="Error")

    # Check if message is plain text (starts with !)
    if message_key.startswith("!"):
        message = message_key[1:]  # Remove the ! prefix
    else:
        message = lang.get(message_key, default="An error occurred", **kwargs)

    SilentMessageBox.critical(parent, title, message)
    log_with_action(logger_ui, "error", f"Error: {message}", action="ERROR")


def msg_show_warning(parent, title_key: str, message_key: str, **kwargs) -> None:
    """
    Display a warning message dialog with automatic logging.

    Args:
        parent: Parent widget for the message box
        title_key: Language key for dialog title (e.g., "titles.warning")
        message_key: Language key for warning message, or plain text if starts with "!"
        **kwargs: Dynamic parameters for message formatting

    Note:
        If message_key starts with "!", it will be treated as plain text
        instead of a lang key. Example: msg_show_warning(
            self, "titles.warning", "!Plain text message"
        )

    Example:
        msg_show_warning(
            self,
            "titles.warning",
            "char_name_empty"
        )
    """
    title = lang.get(title_key, default="Warning")

    # Check if message is plain text (starts with !)
    if message_key.startswith("!"):
        message = message_key[1:]  # Remove the ! prefix
    else:
        message = lang.get(message_key, default="Warning", **kwargs)

    SilentMessageBox.warning(parent, title, message)
    log_with_action(logger_ui, "warning", f"Warning: {message}", action="WARNING")


def msg_show_confirmation(parent, title: str, message: str) -> bool:
    """
    Display a yes/no confirmation dialog.

    Returns True if user clicked "Yes", False otherwise.

    Args:
        parent: Parent widget for the message box
        title: Dialog title text (not translated, for simple confirmations)
        message: Dialog message text

    Returns:
        bool: True if user clicked Yes, False if clicked No or cancelled

    Example:
        if msg_show_confirmation(self, "Delete Character?", "Are you sure?"):
            # Delete the character
            pass
    """
    reply = SilentMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No  # Default to No for safety
    )
    return reply == QMessageBox.Yes


def msg_show_info_with_details(parent, title_key: str, details_text: str) -> None:
    """
    Display an info message with formatted multi-line details.

    Useful for displaying complex information like update results with multiple stats.

    Args:
        parent: Parent widget for the message box
        title_key: Language key for dialog title
        details_text: Formatted details text (can contain newlines and formatting)

    Example:
        msg_show_info_with_details(
            self,
            "character_sheet.messages.stats_update_success",
            f"Tower Captures: {tower}\\n"
            f"Keep Captures: {keep}\\n"
            f"Solo Kills: {solo_kills}"
        )
    """
    title = lang.get(title_key, default="Information")

    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(details_text)
    dialog.setIcon(QMessageBox.Information)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec()

    logger_ui.info(f"Info displayed: {title_key}")
