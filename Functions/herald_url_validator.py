"""
Herald URL validation and management functions.

This module handles Herald URL validation, button state management,
and opening Herald URLs in the browser with proper authentication.
"""

import threading
from PySide6.QtWidgets import QMessageBox
from Functions.language_manager import lang
from Functions.debug_logging_manager import get_logger, LOGGER_CHARACTER


logger = get_logger(LOGGER_CHARACTER)


def herald_url_on_text_changed(parent_window, text: str) -> None:
    """
    Handle Herald URL text change and update button states.

    Validates the Herald URL and enables/disables the stats update button
    based on whether a valid URL is provided and no scraping is in progress.

    Args:
        parent_window: CharacterSheetWindow instance with herald_url_edit
        text: Current text in the Herald URL field

    Returns:
        None (updates UI via parent_window)

    Process:
        1. Check if Herald scraping is in progress (return if true)
        2. Validate URL is not empty
        3. Enable/disable update buttons using state manager
        4. Update button tooltips accordingly

    Examples:
        >>> herald_url_on_text_changed(window, "https://eden-daoc.net/herald?n=player&k=PlayerName")
        # Buttons enabled, tooltip set to normal
        
        >>> herald_url_on_text_changed(window, "")
        # Buttons disabled, tooltip set to prompt for URL
    """
    from UI.ui_state_manager import ui_state_set_herald_buttons
    
    if parent_window.herald_scraping_in_progress:
        return

    is_url_valid = bool(text.strip())
    
    # Update state using state manager
    ui_state_set_herald_buttons(
        parent_window,
        character_selected=True,
        herald_url=text.strip(),
        scraping_active=False,
        validation_active=False
    )
    
    # Update tooltips
    if hasattr(parent_window, 'update_rvr_button'):
        if is_url_valid:
            parent_window.update_rvr_button.setToolTip(
                lang.get("update_rvr_pvp_tooltip")
            )
        else:
            parent_window.update_rvr_button.setToolTip(
                lang.get("herald_url.tooltip_please_configure", default="Please configure Herald URL first")
            )


def herald_url_open_url(parent_window) -> None:
    """
    Open Herald URL in default browser.

    Simple function to open the Herald URL in the user's default browser.
    No cookies, no Selenium - just open the URL.

    Args:
        parent_window: CharacterSheetWindow instance with character_data

    Returns:
        None (opens URL in browser)

    Examples:
        >>> herald_url_open_url(window)
        # Opens Herald URL in default browser
    """
    import webbrowser
    
    # Get URL from character data (source of truth)
    url = parent_window.character_data.get('url', '').strip()

    if not url:
        msg_show_warning(
            parent_window,
            "titles.warning",
            "herald_url.error.missing_message"
        )
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        # Simply open the URL in the default browser
        webbrowser.open(url)
    except Exception as e:
        msg_show_error(
            parent_window,
            "titles.error",
            f"!Failed to open browser: {str(e)}"
        )


def _herald_url_open_in_thread(url: str) -> None:
    """
    Internal: Open Herald URL in browser in separate thread.

    Simply opens the URL in the default browser without blocking UI.

    Args:
        url: Herald URL to open

    Returns:
        None (opens URL in browser)
    """
    try:
        import webbrowser
        webbrowser.open(url)
        logger.info(f"Opened Herald URL in browser: {url}")
    except Exception as e:
        logger.error(f"Error opening URL in browser: {e}")


def herald_url_update_button_states(parent_window) -> None:
    """
    Update Herald button states based on validation and scraping status.

    Manages enable/disable state of Herald buttons based on:
    - Eden validation thread running
    - Herald URL presence
    - Active Herald scraping operations

    Args:
        parent_window: CharacterSheetWindow instance with Herald buttons

    Returns:
        None (updates UI via parent_window)

    Process:
        1. Check if Eden validation is in progress
        2. Check if Herald URL is configured
        3. Check if Herald scraping is active
        4. Update button enabled states using state manager
        5. Set appropriate tooltips

    Button States:
        - Disabled if: Validation running, scraping active, no URL
        - Enabled if: Validation done, no scraping, URL present

    Examples:
        >>> herald_url_update_button_states(window)
        # Disables Herald buttons during validation
        # Disables buttons if no URL configured
    """
    from UI.ui_state_manager import ui_state_set_herald_buttons
    
    main_window = parent_window.parent()
    is_validation_running = False

    if main_window and hasattr(main_window, 'ui_manager'):
        ui_manager = main_window.ui_manager
        is_validation_running = (
            hasattr(ui_manager, 'eden_status_thread')
            and ui_manager.eden_status_thread
            and ui_manager.eden_status_thread.isRunning()
        )

    # Get herald URL from character data
    herald_url = parent_window.character_data.get('url', '').strip()
    
    # Update button states using state manager
    ui_state_set_herald_buttons(
        parent_window,
        character_selected=True,
        herald_url=herald_url,
        scraping_active=parent_window.herald_scraping_in_progress,
        validation_active=is_validation_running
    )
    
    # Update tooltips
    validation_tooltip = lang.get(
        "herald_buttons.validation_in_progress",
        default="⏳ Eden validation in progress... Please wait"
    )

    if hasattr(parent_window, 'update_herald_button'):
        if is_validation_running:
            parent_window.update_herald_button.setToolTip(validation_tooltip)
        else:
            parent_window.update_herald_button.setToolTip(
                lang.get("character_sheet.labels.update_from_herald_tooltip")
            )

    if hasattr(parent_window, 'update_rvr_button'):
        # Update tooltips for RvR button based on state
        if is_validation_running:
            parent_window.update_rvr_button.setToolTip(validation_tooltip)
        elif not herald_url:
            parent_window.update_rvr_button.setToolTip(
                lang.get(
                    "herald_url.tooltip_please_configure",
                    default="Please configure Herald URL first"
                )
            )
        else:
            parent_window.update_rvr_button.setToolTip(
                lang.get("update_rvr_pvp_tooltip")
            )
