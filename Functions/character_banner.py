"""
Character class banner image management and display functions.

This module handles loading and displaying character class banner images
based on the selected realm and class. It provides fallback placeholder
display when banner images are not available.
"""

import os
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from Functions.language_manager import lang
from Functions.path_manager import get_resource_path
from Functions.theme_manager import get_scaled_size
from Functions.logging_manager import get_logger, LOGGER_CHARACTER


logger = get_logger(LOGGER_CHARACTER)


def banner_load_class_image(parent_window, realm: str, class_name: str) -> None:
    """
    Load and display character class banner image.

    Loads the class banner image from Img/Banner/{realm}/{class}.{jpg|png}
    and displays it in the banner label. Falls back to placeholder if image
    not found or fails to load.

    Args:
        parent_window: CharacterSheetWindow instance with banner_label attribute
        realm: Realm name ('Albion', 'Hibernia', or 'Midgard')
        class_name: Character class name (e.g., 'Armsman', 'Ranger')

    Returns:
        None (updates UI via parent_window.banner_label)

    Process:
        1. Validates realm and class name
        2. Maps realm to folder abbreviation (Albion → Alb, etc)
        3. Attempts to load image from Img/Banner/{realm}/{class}.jpg
        4. Falls back to .png extension if .jpg not found
        5. Displays image or calls banner_set_placeholder() if not found
        6. Logs errors if image is corrupted or path invalid

    Examples:
        >>> banner_load_class_image(window, 'Albion', 'Armsman')
        # Loads Img/Banner/Alb/armsman.jpg or .png

        >>> banner_load_class_image(window, 'Midgard', 'Warrior')
        # Loads Img/Banner/Mid/warrior.jpg or .png
    """
    if not class_name:
        parent_window.banner_label.clear()
        parent_window.banner_label.setText(
            lang.get("character_sheet.labels.no_class_selected")
        )
        parent_window.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_window.banner_label.setStyleSheet("color: gray; font-style: italic;")
        return

    realm_map = {
        "Albion": "Alb",
        "Hibernia": "Hib",
        "Midgard": "Mid"
    }
    realm_folder = realm_map.get(realm, realm)

    class_filename = class_name.lower().replace(" ", "_")

    banner_path = get_resource_path(
        os.path.join("Img", "Banner", realm_folder, f"{class_filename}.jpg")
    )

    if not os.path.exists(banner_path):
        banner_path = get_resource_path(
            os.path.join("Img", "Banner", realm_folder, f"{class_filename}.png")
        )

    if os.path.exists(banner_path):
        pixmap = QPixmap(banner_path)
        if not pixmap.isNull():
            parent_window.banner_label.setPixmap(pixmap)
            parent_window.banner_label.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
            )
            parent_window.banner_label.setStyleSheet("")
            logger.debug(f"Loaded banner: {banner_path}")
        else:
            logger.warning(f"Invalid image file: {banner_path}")
            banner_set_placeholder(
                parent_window, f"Invalid\nimage:\n{class_name}"
            )
    else:
        logger.debug(
            f"Banner not found for {realm}/{class_name} at {banner_path}"
        )
        banner_set_placeholder(
            parent_window, f"Banner\nnot found:\n{realm}\n{class_name}"
        )


def banner_set_placeholder(parent_window, text: str) -> None:
    """
    Display placeholder text when banner image is not available.

    Shows a styled text placeholder with gray italic formatting when the
    banner image is missing or cannot be loaded. This provides visual
    feedback to the user.

    Args:
        parent_window: CharacterSheetWindow instance with banner_label attribute
        text: Placeholder text to display (multi-line supported)

    Returns:
        None (updates UI via parent_window.banner_label)

    Process:
        1. Clears any existing pixmap
        2. Sets text with centered alignment
        3. Applies gray italic styling with scaled font size
        4. Text can be multi-line (use \n for line breaks)

    Examples:
        >>> banner_set_placeholder(window, "Banner\nnot found:\nAlbion\nArmsman")
        # Shows 4-line placeholder text

        >>> banner_set_placeholder(window, "Invalid\nimage:\nArmsman")
        # Shows placeholder for corrupted image
    """
    parent_window.banner_label.clear()
    parent_window.banner_label.setText(text)
    parent_window.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    font_size = get_scaled_size(9)
    parent_window.banner_label.setStyleSheet(
        f"color: gray; font-style: italic; font-size: {font_size:.1f}pt;"
    )
