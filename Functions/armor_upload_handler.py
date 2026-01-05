"""
Armor upload and preview handler functions.

This module handles armor file operations including uploading, importing templates,
opening armor files, and deleting armor files with proper validation and user feedback.
"""

import os
import platform
import subprocess

from UI.ui_sound_manager import SilentMessageBox
from PySide6.QtWidgets import QMessageBox, QFileDialog, QDialog
from Functions.language_manager import lang
from Functions.debug_logging_manager import get_logger, LOGGER_UI

logger = get_logger(LOGGER_UI)


def armor_upload_file(
    parent_window,
    armor_manager,
    season,
    character_name,
    realm
) -> None:
    """
    Open file dialog and upload armor file.

    Displays file selection dialog, preview dialog for season/filename confirmation,
    and handles the actual file upload. Supports cross-season upload with ArmorManager.

    Args:
        parent_window: ArmorManagementDialog instance with UI elements
        armor_manager: Current ArmorManager instance for target season
        season: Current season (may be overridden in preview)
        character_name: Character name for target path
        realm: Character realm for target path

    Returns:
        None (displays dialogs and updates UI)

    Process:
        1. Open file dialog to select armor file
        2. If file selected, show preview/confirm dialog
        3. Get target season and filename from preview dialog
        4. Create target ArmorManager if season changed
        5. Upload file using armor_manager.upload_armor()
        6. Show success/error message
        7. Refresh UI if same season

    Examples:
        >>> armor_upload_file(dialog, armor_manager, "S3", "TestChar", "Albion")
        # Opens file dialog and handles upload with preview
    """
    from UI.dialogs import ArmorUploadPreviewDialog
    from Functions.config_manager import config

    file_path, _ = QFileDialog.getOpenFileName(
        parent_window,
        lang.get("armoury_dialog.dialogs.select_file"),
        "",
        lang.get("armoury_dialog.dialogs.all_files")
    )

    if not file_path:
        return

    try:
        available_seasons = config.get("game.seasons", ["S3"])

        preview_dialog = ArmorUploadPreviewDialog(
            parent_window,
            file_path,
            season,
            available_seasons,
            realm,
            character_name
        )

        if preview_dialog.exec() != QDialog.Accepted:
            return

        target_season = preview_dialog.season_combo.currentText()
        new_filename = preview_dialog.filename_edit.text().strip()

        if target_season != season:
            from Functions.armor_manager import ArmorManager
            target_armor_manager = ArmorManager(target_season, realm, character_name)
        else:
            target_armor_manager = armor_manager

        result_path = target_armor_manager.upload_armor(file_path, new_filename)

        season_info = (
            lang.get(
                "armoury_dialog.messages.season_info",
                season=target_season
            )
            if target_season != season
            else ""
        )

        SilentMessageBox.information(
            parent_window,
            lang.get("dialogs.titles.success"),
            lang.get(
                "armoury_dialog.messages.upload_success",
                filename=os.path.basename(result_path),
                season_info=season_info
            )
        )

        if target_season == season:
            parent_window.refresh_list()

        logger.info(
            f"Armor file uploaded: {result_path} (Season: {target_season})"
        )

    except Exception as e:
        logger.error(f"Error uploading armor file: {e}")
        SilentMessageBox.critical(
            parent_window,
            lang.get("dialogs.titles.error"),
            lang.get(
                "armoury_dialog.messages.upload_error",
                error=str(e)
            )
        )


def armor_import_template(
    parent_window,
    character_data,
    data_manager,
    template_manager
) -> None:
    """
    Open template import dialog for armor.

    Validates character has a class, prepares localized class names,
    and launches TemplateImportDialog. Updates template index on successful import.

    Args:
        parent_window: ArmorManagementDialog instance
        character_data: Character data dict with class, realm, name
        data_manager: DataManager instance for class lookups
        template_manager: TemplateManager instance for imports

    Returns:
        None (displays dialog and shows confirmation message)

    Process:
        1. Validate character has a class defined
        2. Get class translations (FR, DE) from data_manager
        3. Prepare character_data dict with localized names
        4. Launch TemplateImportDialog
        5. Connect template_imported signal to refresh
        6. Show success message on completion

    Examples:
        >>> armor_import_template(dialog, char_data, data_manager, template_manager)
        # Validates class and opens template import dialog
    """
    from UI.ui_armory_template_import_dialog import TemplateImportDialog

    character_class = character_data.get('class', '')
    realm = character_data.get('realm', '')
    name = character_data.get('name', '')

    if not character_class:
        SilentMessageBox.warning(
            parent_window,
            lang.get("template_import.error_title"),
            lang.get("template_import.error_no_class")
        )
        return

    class_fr = character_class
    class_de = character_class

    if data_manager:
        realm_classes = data_manager.get_classes(realm)
        for cls in realm_classes:
            if cls.get('name') == character_class:
                class_fr = cls.get('name_fr', character_class)
                class_de = cls.get('name_de', character_class)
                break

    character_data_import = {
        'character_class': character_class,
        'class_fr': class_fr,
        'class_de': class_de,
        'realm': realm,
        'name': name
    }

    dialog = TemplateImportDialog(parent_window, character_data_import)
    dialog.template_imported.connect(lambda: (
        template_manager.update_index(),
        parent_window.refresh_list()
    ))

    if dialog.exec() == QDialog.Accepted:
        SilentMessageBox.information(
            parent_window,
            lang.get("dialogs.titles.success"),
            lang.get(
                "armoury_dialog.messages.template_import_success",
                default="Template imported successfully!"
            )
        )


def armor_open_file(
    parent_window,
    template_manager,
    realm,
    filename: str
) -> None:
    """
    Open armor file with system default application.

    Gets template file path, validates existence, and opens with platform-specific
    application launcher (Windows/macOS/Linux).

    Args:
        parent_window: ArmorManagementDialog instance
        template_manager: TemplateManager instance for path lookup
        realm: Armor realm for path resolution
        filename: Armor filename to open

    Returns:
        None (opens file in external application)

    Process:
        1. Get template file path from template_manager
        2. Validate file exists
        3. Determine platform (Windows/macOS/Linux)
        4. Launch with os.startfile (Windows) or subprocess
        5. Log operation or show error

    Examples:
        >>> armor_open_file(dialog, template_manager, "Albion", "myarmor.txt")
        # Opens myarmor.txt with default application
    """
    try:
        template_path = template_manager._get_template_path(realm, filename)

        if not template_path.exists():
            SilentMessageBox.warning(
                parent_window,
                lang.get("dialogs.titles.error"),
                lang.get(
                    "armoury_dialog.messages.file_not_found",
                    filename=filename
                )
            )
            return

        if platform.system() == 'Windows':
            os.startfile(str(template_path))
        elif platform.system() == 'Darwin':
            subprocess.run(['open', str(template_path)])
        else:
            subprocess.run(['xdg-open', str(template_path)])

        logger.info(f"Opened armor file: {filename}")

    except Exception as e:
        logger.error(f"Error opening armor file: {e}")
        SilentMessageBox.critical(
            parent_window,
            lang.get("dialogs.titles.error"),
            lang.get(
                "armoury_dialog.messages.open_error",
                error=str(e)
            )
        )


def armor_delete_file(
    parent_window,
    template_manager,
    realm,
    filename: str
) -> None:
    """
    Delete armor file after user confirmation.

    Shows confirmation dialog, then deletes file using TemplateManager.
    Refreshes UI list on successful deletion.

    Args:
        parent_window: ArmorManagementDialog instance with refresh_list()
        template_manager: TemplateManager instance for deletion
        realm: Armor realm for deletion
        filename: Armor filename to delete

    Returns:
        None (deletes file and updates UI)

    Process:
        1. Show confirmation dialog with filename
        2. If user confirms deletion:
           a. Call template_manager.delete_template()
           b. Show success message
           c. Call refresh_list() to update UI
           d. Log deletion
        3. If deletion fails, show error message

    Examples:
        >>> armor_delete_file(dialog, template_manager, "Albion", "oldarmor.txt")
        # Shows confirmation, deletes file, refreshes list
    """
    reply = SilentMessageBox.question(
        parent_window,
        lang.get("armoury_dialog.dialogs.confirm_delete"),
        lang.get(
            "armoury_dialog.messages.delete_confirm",
            filename=filename
        ),
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )

    if reply != QMessageBox.Yes:
        return

    try:
        success = template_manager.delete_template(filename, realm)

        if success:
            SilentMessageBox.information(
                parent_window,
                lang.get("dialogs.titles.success"),
                lang.get(
                    "armoury_dialog.messages.delete_success",
                    filename=filename
                )
            )
            parent_window.refresh_list()
            logger.info(f"Armor file deleted: {filename}")
        else:
            SilentMessageBox.warning(
                parent_window,
                lang.get("dialogs.titles.error"),
                lang.get(
                    "armoury_dialog.messages.delete_error",
                    error="Delete operation failed"
                )
            )

    except Exception as e:
        logger.error(f"Error deleting armor file: {e}")
        SilentMessageBox.critical(
            parent_window,
            lang.get("dialogs.titles.error"),
            lang.get(
                "armoury_dialog.messages.delete_error",
                error=str(e)
            )
        )
