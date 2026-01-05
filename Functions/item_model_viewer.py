"""Item Model Viewer Module - Handle 3D item model display functionality.

This module provides functions for displaying item models in dialogs.
Extracted from UI/dialogs.py ArmorManagementDialog class (Phase 10 refactoring).

Functions:
    - item_model_on_link_clicked: Handle click on model viewer link in preview
    - item_model_show: Display model image for the specified item

Naming Convention: item_model_{action}_{object}

Language: English (code and comments)
"""

from UI.ui_sound_manager import SilentMessageBox
from PySide6.QtWidgets import QMessageBox

from Functions.language_manager import lang
from Functions.debug_logging_manager import get_logger, LOGGER_UI

# Get logger instance
logger = get_logger(LOGGER_UI)


def item_model_on_link_clicked(parent_window, url) -> None:
    """Handle click on model viewer link in preview.

    Intercepts model:// URL clicks and displays the item model viewer dialog.
    Prevents default link navigation that would clear the preview.

    Process:
        1. Check if URL scheme is "model" (custom protocol)
        2. Extract item name from URL path
        3. Call item_model_show() to display model
        4. Return early to prevent default navigation

    Parameters:
        parent_window: ArmorManagementDialog instance with db_manager, realm
        url: QUrl object from linkClicked signal (scheme="model", path=item_name)

    Returns:
        None (displays model in separate dialog)

    Example:
        >>> # Connected to preview_area.anchorClicked signal
        >>> def preview_link_clicked(url):
        ...     item_model_on_link_clicked(self, url)
        >>> preview_area.anchorClicked.connect(preview_link_clicked)

    Error Handling:
        - Logs error if URL parsing fails
        - Non-fatal (does not propagate exception)
    """
    try:
        # Check if this is a model link
        if url.scheme() == "model":
            item_name = url.path()
            # Open model viewer without changing current selection/preview
            item_model_show(parent_window, item_name)
            # Prevent default link navigation that would clear the preview
            return
    except Exception as e:
        logger.error(f"Error handling model link click: {e}")


def item_model_show(parent_window, item_name: str) -> None:
    """Display model image for the specified item in a dialog.

    Searches for item in database, retrieves model ID, and displays model viewer dialog
    (non-modal window). Uses multi-source search with fallback chain:
        1. Direct item name search
        2. Realm-specific search (name:realm)
        3. All realms search (name:all)

    Process:
        1. Search database for item by name (multiple fallbacks)
        2. Extract model_id (supports both 'model_id' and 'model' fields)
        3. Get model_category from item data (default: 'items')
        4. Create and show ModelViewerDialog (non-modal)
        5. Show error message if model not found

    Parameters:
        parent_window: ArmorManagementDialog instance with:
            - db_manager: DatabaseManager instance for item search
            - realm: Character realm (Albion/Hibernia/Midgard)
        item_name: Name of item to display model for (str)

    Returns:
        None (displays dialog)

    Example:
        >>> # Show model for "Sleeves of Strife"
        >>> item_model_show(armor_dialog, "Sleeves of Strife")
        >>> # Dialog opens with item model image

    Error Handling:
        - Gracefully handles missing items (shows info message)
        - Catches and logs exceptions
        - Shows error dialog on critical failures
        - Supports both 'model_id' and 'model' database fields for compatibility
    """
    try:
        # Search for item in database
        item_data = parent_window.db_manager.search_item(item_name)

        if not item_data:
            # Try with realm suffix
            item_name_lower = item_name.lower()
            realm_lower = parent_window.realm.lower()
            search_key = f"{item_name_lower}:{realm_lower}"
            item_data = parent_window.db_manager.search_item(search_key)

        if not item_data:
            # Try with :all suffix
            search_key = f"{item_name.lower()}:all"
            item_data = parent_window.db_manager.search_item(search_key)

        # Support both 'model_id' and 'model' fields
        model_id = (
            item_data.get("model_id") or item_data.get("model")
            if item_data
            else None
        )

        if model_id:
            model_category = item_data.get("model_category", "items")

            # Show model viewer dialog with embedded image (non-modal)
            from UI.model_viewer_dialog import ModelViewerDialog

            dialog = ModelViewerDialog(
                parent_window,
                model_id=model_id,
                item_name=item_name,
                model_category=model_category,
            )
            dialog.show()
        else:
            SilentMessageBox.information(
                parent_window,
                lang.get("dialogs.titles.info", default="Information"),
                lang.get(
                    "armoury_dialog.messages.no_model_found",
                    default=f"No model information found for '{item_name}'.",
                    item_name=item_name,
                ),
            )
    except Exception as e:
        logger.error(f"Error showing item model for '{item_name}': {e}")
        SilentMessageBox.critical(
            parent_window,
            lang.get("dialogs.titles.error", default="Error"),
            lang.get(
                "armoury_dialog.messages.model_viewer_error",
                default=f"Error opening model viewer: {str(e)}",
                error=str(e),
            ),
        )
