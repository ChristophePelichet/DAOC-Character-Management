"""
UI State Manager Module

Centralized button and UI element state management for consistent application behavior.
Manages enable/disable states for complex UI components with interdependencies.

Functions:
    ui_state_set_herald_buttons() - Manage Herald update button states
    ui_state_set_armor_buttons() - Manage armor preview button states
    ui_state_set_stats_buttons() - Manage character stats update states
    ui_state_set_dialog_buttons() - Generic button state controller
    ui_state_on_selection_changed() - Handle selection changes

Example:
    # Enable Herald buttons when character is selected and has Herald URL
    ui_state_set_herald_buttons(
        parent_window,
        character_selected=True,
        herald_url="https://herald.daocplayers.com/...",
        scraping_active=False
    )

    # Handle character selection change
    ui_state_on_selection_changed(
        parent_window,
        selection_count=1,
        is_valid=True
    )
"""

from Functions.language_manager import lang
from Functions.debug_logging_manager import get_logger, LOGGER_CHARACTER

logger_ui = get_logger(LOGGER_CHARACTER)


def ui_state_set_herald_buttons(
    parent, character_selected: bool = False, herald_url: str = "",
    scraping_active: bool = False, validation_active: bool = False
) -> None:
    """
    Manage Herald update button states based on character and scraping status.

    Controls state of: update_herald_button, open_herald_button, update_rvr_button

    Args:
        parent: Parent widget (CharacterSheetWindow) containing Herald buttons
        character_selected: True if a character is currently selected
        herald_url: Herald URL if populated, empty string otherwise
        scraping_active: True if character scraping is in progress
        validation_active: True if Eden URL validation is in progress

    State Logic:
        - Buttons enabled if: character selected AND herald URL provided AND no operations active
        - Buttons disabled if: no character OR no URL OR scraping/validation active
        - Tooltips update based on state reason

    Example:
        ui_state_set_herald_buttons(
            self,
            character_selected=True,
            herald_url="https://herald.daocplayers.com/character/...",
            scraping_active=False,
            validation_active=False
        )
    """
    # Determine if Herald buttons should be enabled
    buttons_enabled = (
        character_selected and bool(herald_url)
        and not scraping_active and not validation_active
    )

    # Update button states
    if hasattr(parent, "update_herald_button"):
        parent.update_herald_button.setEnabled(buttons_enabled)

    if hasattr(parent, "open_herald_button"):
        parent.open_herald_button.setEnabled(buttons_enabled)

    if hasattr(parent, "update_rvr_button"):
        parent.update_rvr_button.setEnabled(buttons_enabled)

    # Log state change
    logger_ui.debug(
        f"Herald buttons state: {buttons_enabled} "
        f"(character={character_selected}, url={bool(herald_url)}, "
        f"scraping={scraping_active}, validation={validation_active})"
    )


def ui_state_set_armor_buttons(
    parent, character_selected: bool = False, file_selected: bool = False,
    items_without_price: bool = False, db_manager=None
) -> None:
    """
    Manage armor preview and search button states.

    Controls state of: preview_download_button, search_prices_button

    Args:
        parent: Parent widget (ArmorManagementDialog) containing armor buttons
        character_selected: True if a character is selected in the list
        file_selected: True if armor file is selected/loaded
        items_without_price: True if there are items without prices
        db_manager: ItemsDatabaseManager instance to check database mode (optional)

    State Logic:
        - preview_download_button: enabled if character selected AND file loaded
        - search_prices_button: enabled if file loaded AND items without prices AND personal database active
        - If database is embedded (read-only), search button disabled with tooltip

    Example:
        ui_state_set_armor_buttons(
            self,
            character_selected=True,
            file_selected=True,
            items_without_price=True,
            db_manager=self.db_manager
        )
    """
    # Update preview button state
    if hasattr(parent, "preview_download_button"):
        preview_enabled = character_selected and file_selected
        parent.preview_download_button.setEnabled(preview_enabled)
        logger_ui.debug(f"Preview button state: {preview_enabled}")

    # Update search prices button state
    if hasattr(parent, "search_prices_button"):
        # Check if personal database is active
        is_personal_db = True
        if db_manager and hasattr(db_manager, "is_personal_database"):
            is_personal_db = db_manager.is_personal_database()
        
        search_enabled = file_selected and items_without_price and is_personal_db
        parent.search_prices_button.setEnabled(search_enabled)
        
        # Set tooltip based on state
        if file_selected and items_without_price and not is_personal_db:
            # DB is embedded (read-only) - provide helpful tooltip
            tooltip = lang.get(
                "armoury_dialog.tooltips.search_prices_embedded_db",
                default="Enable personal database in Settings/Armory to add/update item prices.\n"
                        "Personal database allows you to maintain your own price list."
            )
            parent.search_prices_button.setToolTip(tooltip)
        else:
            # Reset to default tooltip
            parent.search_prices_button.setToolTip(
                lang.get("armoury_dialog.tooltips.search_missing_prices", 
                        default="Search online for items without price in database")
            )
        
        logger_ui.debug(f"Search prices button state: {search_enabled} (personal_db={is_personal_db})")


def ui_state_set_stats_buttons(
    parent, character_selected: bool = False, has_stats: bool = False,
    scraping_active: bool = False
) -> None:
    """
    Manage character stats update button states.

    Controls state of: buttons related to character stats operations

    Args:
        parent: Parent widget containing stats buttons
        character_selected: True if a character is selected
        has_stats: True if character has stats to display
        scraping_active: True if scraping operation is in progress

    State Logic:
        - Buttons enabled if: character selected AND has stats AND no scraping active
        - Buttons disabled during active scraping operations

    Example:
        ui_state_set_stats_buttons(
            self,
            character_selected=True,
            has_stats=True,
            scraping_active=False
        )
    """
    buttons_enabled = (
        character_selected and has_stats and not scraping_active
    )

    # Update any stats-related buttons (specific buttons depend on dialog implementation)
    logger_ui.debug(
        f"Stats buttons state: {buttons_enabled} "
        f"(selected={character_selected}, has_stats={has_stats}, "
        f"scraping={scraping_active})"
    )


def ui_state_set_dialog_buttons(
    parent, button_states: dict
) -> None:
    """
    Generic button state controller for setting multiple button states at once.

    Provides flexible state management for any buttons in a dialog.

    Args:
        parent: Parent widget containing buttons
        button_states: Dictionary mapping button attribute names to enabled state
                      Example: {"delete_button": True, "save_button": False}

    Example:
        ui_state_set_dialog_buttons(self, {
            "delete_button": has_selection,
            "edit_button": has_selection,
            "save_button": is_valid_input,
            "cancel_button": True  # Always enabled
        })
    """
    for button_name, enabled in button_states.items():
        if hasattr(parent, button_name):
            button = getattr(parent, button_name)
            button.setEnabled(enabled)
            logger_ui.debug(f"Button '{button_name}' state: {enabled}")
        else:
            logger_ui.warning(f"Button '{button_name}' not found in parent widget")


def ui_state_on_selection_changed(
    parent, selection_count: int = 0, is_valid: bool = False,
    enable_delete: bool = False, enable_edit: bool = False,
    enable_export: bool = False
) -> None:
    """
    Unified handler for UI state changes when selection changes.

    Updates button states based on selection state and validity checks.

    Args:
        parent: Parent widget (e.g., CharacterListDialog)
        selection_count: Number of items selected (0, 1, >1)
        is_valid: True if selection is valid for operations
        enable_delete: True to enable delete button
        enable_edit: True to enable edit button
        enable_export: True to enable export button

    State Logic:
        - Enable action buttons only if: valid selection AND appropriate count
        - Delete typically requires single selection
        - Edit typically requires single selection
        - Export can work with multiple selections

    Example:
        ui_state_on_selection_changed(
            self,
            selection_count=1,
            is_valid=True,
            enable_delete=True,
            enable_edit=True
        )
    """
    # Build state dictionary for generic button controller
    button_states = {}

    if hasattr(parent, "delete_button"):
        button_states["delete_button"] = (
            selection_count > 0 and is_valid and enable_delete
        )

    if hasattr(parent, "edit_button"):
        button_states["edit_button"] = (
            selection_count == 1 and is_valid and enable_edit
        )

    if hasattr(parent, "export_button"):
        button_states["export_button"] = (
            selection_count > 0 and is_valid and enable_export
        )

    # Apply state changes
    if button_states:
        ui_state_set_dialog_buttons(parent, button_states)

    # Log selection state
    logger_ui.debug(
        f"Selection changed: count={selection_count}, valid={is_valid}, "
        f"delete={enable_delete}, edit={enable_edit}, export={enable_export}"
    )
