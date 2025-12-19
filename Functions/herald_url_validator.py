"""
Herald URL validation and management functions.

This module handles Herald URL validation, button state management,
and opening Herald URLs in the browser with proper authentication.
"""

import threading
from PySide6.QtWidgets import QMessageBox
from Functions.language_manager import lang
from Functions.logging_manager import get_logger, LOGGER_CHARACTER


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
        3. Enable/disable update_rvr_button accordingly
        4. Set appropriate tooltip

    Examples:
        >>> herald_url_on_text_changed(window, "https://eden-daoc.net/herald?n=player&k=PlayerName")
        # Button enabled, tooltip set to normal
        
        >>> herald_url_on_text_changed(window, "")
        # Button disabled, tooltip set to prompt for URL
    """
    if parent_window.herald_scraping_in_progress:
        return

    is_url_valid = bool(text.strip())

    if hasattr(parent_window, 'update_rvr_button'):
        parent_window.update_rvr_button.setEnabled(is_url_valid)

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
    Open Herald URL in browser with authentication cookies.

    Validates the Herald URL from the text field, ensures proper protocol
    (https://), and opens it in the browser using authenticated cookies.
    Runs in separate thread to avoid blocking UI.

    Args:
        parent_window: CharacterSheetWindow instance with herald_url_edit

    Returns:
        None (opens URL in browser)

    Process:
        1. Extract URL from herald_url_edit field
        2. Validate URL is not empty
        3. Ensure protocol (http:// or https://)
        4. Launch browser in separate thread
        5. Load cookies and navigate to URL
        6. Show error dialog if operation fails

    Examples:
        >>> herald_url_open_url(window)
        # Opens URL from herald_url_edit in browser with cookies
    """
    url = parent_window.herald_url_edit.text().strip()

    if not url:
        QMessageBox.warning(
            parent_window,
            lang.get("herald_url.error.missing_title", default="Missing URL"),
            lang.get(
                "herald_url.error.missing_message",
                default="Please enter a valid Herald URL."
            )
        )
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        parent_window.herald_url_edit.setText(url)

    try:
        thread = threading.Thread(
            target=_herald_url_open_in_thread,
            args=(url,),
            daemon=True
        )
        thread.start()
    except Exception as e:
        logger.error(f"Error starting URL thread: {e}")
        QMessageBox.critical(
            parent_window,
            lang.get("herald_url.error.open_title", default="Error"),
            lang.get(
                "herald_url.error.open_message",
                default=f"Unable to open URL: {str(e)}"
            )
        )


def _herald_url_open_in_thread(url: str) -> None:
    """
    Internal: Open Herald URL with cookies in separate thread.

    Opens the URL in the browser using Selenium with authenticated cookies.
    Handles errors gracefully without blocking UI.

    Args:
        url: Herald URL to open

    Returns:
        None (opens URL in browser)

    Error Handling:
        - Log warnings/errors for debugging
        - Never raise exceptions (thread-safe)
    """
    try:
        from Functions.cookie_manager import CookieManager

        cookie_manager = CookieManager()
        result = cookie_manager.open_url_with_cookies_subprocess(url)

        if not result.get('success', False):
            logger.warning(
                f"Error opening URL: {result.get('message', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Error opening URL with cookies: {e}")


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
        4. Update button enabled states
        5. Set appropriate tooltips

    Button States:
        - Disabled if: Validation running, scraping active, no URL (for RvR)
        - Enabled if: Validation done, no scraping, URL present (for RvR)

    Examples:
        >>> herald_url_update_button_states(window)
        # Disables Update Herald button during validation
        # Disables Update RvR button if no URL or scraping active
    """
    main_window = parent_window.parent()
    is_validation_running = False

    if main_window and hasattr(main_window, 'ui_manager'):
        ui_manager = main_window.ui_manager
        is_validation_running = (
            hasattr(ui_manager, 'eden_status_thread')
            and ui_manager.eden_status_thread
            and ui_manager.eden_status_thread.isRunning()
        )

    validation_tooltip = lang.get(
        "herald_buttons.validation_in_progress",
        default="⏳ Eden validation in progress... Please wait"
    )

    if hasattr(parent_window, 'update_herald_button'):
        if is_validation_running:
            parent_window.update_herald_button.setEnabled(False)
            parent_window.update_herald_button.setToolTip(validation_tooltip)
        else:
            parent_window.update_herald_button.setEnabled(True)
            parent_window.update_herald_button.setToolTip(
                lang.get("character_sheet.labels.update_from_herald_tooltip")
            )

    if hasattr(parent_window, 'update_rvr_button'):
        herald_url = (
            parent_window.herald_url_edit.text().strip()
            if hasattr(parent_window, 'herald_url_edit')
            else ''
        )

        if is_validation_running:
            parent_window.update_rvr_button.setEnabled(False)
            parent_window.update_rvr_button.setToolTip(validation_tooltip)
        elif not herald_url or parent_window.herald_scraping_in_progress:
            parent_window.update_rvr_button.setEnabled(False)
            if not herald_url:
                parent_window.update_rvr_button.setToolTip(
                    lang.get(
                        "herald_url.tooltip_please_configure",
                        default="Please configure Herald URL first"
                    )
                )
        else:
            parent_window.update_rvr_button.setEnabled(True)
            parent_window.update_rvr_button.setToolTip(
                lang.get("update_rvr_pvp_tooltip")
            )
