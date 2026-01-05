"""
Armory All Templates Dialog - UI for browsing and managing all templates across realms
Displays all armor templates for each realm with preview functionality
"""

import logging

from UI.ui_sound_manager import SilentMessageBox
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QTextBrowser, QSplitter, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager
from Functions.path_manager import PathManager
from Functions.template_parser import template_parse
from Functions.items_database_manager import ItemsDatabaseManager
from Functions.config_manager import ConfigManager
from Functions.data_manager import DataManager

logger = logging.getLogger(__name__)


class UIArmoryAllTemplates(QMainWindow):
    """Main window for browsing and managing all templates across all realms"""

    def __init__(self, parent=None):
        """Initialize the armory all templates window

        Args:
            parent: Parent widget
        """
        try:
            logger.info("UIArmoryAllTemplates.__init__ called")
            super().__init__(parent)
            self.setWindowTitle(
                lang.get("armory.all_templates_window_title",
                         default="Armory - All Templates")
            )
            self.setGeometry(100, 100, 1400, 800)
            self.setMinimumSize(1000, 600)

            # Initialize managers
            self.template_manager = TemplateManager()
            self.path_manager = PathManager()
            self.config_manager = ConfigManager()
            self.data_manager = DataManager()
            self.db_manager = ItemsDatabaseManager(
                self.config_manager, self.path_manager
            )
            self.tables = {}
            self.previews = {}

            # Maximize the window to use full screen
            self.showMaximized()

            logger.info("Calling _init_ui()")
            self._init_ui()
            self._load_all_templates()
            logger.info("UIArmoryAllTemplates initialization complete")
        except Exception as e:
            import traceback

            error_msg = f"Exception in UIArmoryAllTemplates.__init__: {e}\n"
            logger.error(error_msg + traceback.format_exc())
            raise

    def _init_ui(self):
        """Initialize the user interface with tabs for each realm"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tabs for each realm
        self.realm_tabs = QTabWidget()

        realms = ['Albion', 'Hibernia', 'Midgard']

        for realm in realms:
            # Create a widget for this realm
            realm_widget = self._create_realm_tab(realm)
            self.realm_tabs.addTab(realm_widget, realm)

        main_layout.addWidget(self.realm_tabs)

        # --- Button Section ---
        button_layout = QHBoxLayout()

        import_button_text = lang.get(
            "armoury_dialog.buttons.import_template", default="Import Template"
        )
        import_button = QPushButton(import_button_text)
        import_button.clicked.connect(self.import_template)
        button_layout.addWidget(import_button)

        button_layout.addStretch()

        self.close_button = QPushButton(
            lang.get("window.close", default="Close")
        )
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def _create_realm_tab(self, realm):
        """Create a tab widget for a specific realm

        Args:
            realm: The realm name (Albion, Hibernia, or Midgard)

        Returns:
            QWidget containing the realm's template list and preview
        """
        realm_widget = QWidget()
        layout = QVBoxLayout(realm_widget)

        # Create splitter for table and preview
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Table
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels([
            lang.get("armoury_dialog.table_headers.filename", default="Template"),
            lang.get("armoury_dialog.table_headers.class", default="Class")
        ])
        table.horizontalHeader().setStretchLastSection(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSortingEnabled(True)
        table.sortByColumn(0, Qt.AscendingOrder)
        table.itemSelectionChanged.connect(lambda: self._on_template_selected(realm))
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        def context_menu_cb(pos):
            return self._show_context_menu(realm, pos)
        table.customContextMenuRequested.connect(context_menu_cb)
        # Connect column resize signal to save column widths
        def save_widths_cb():
            return self._save_column_widths(realm)
        table.horizontalHeader().sectionResized.connect(save_widths_cb)
        self.tables[realm] = table

        # Restore saved column widths
        self._restore_column_widths(realm, table)

        splitter.addWidget(table)

        # Right panel: Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Preview header
        preview_title = lang.get(
            "armoury_dialog.preview.title", default="Preview"
        )
        preview_header = QLabel(preview_title)
        preview_header_font = preview_header.font()
        preview_header_font.setBold(True)
        preview_header.setFont(preview_header_font)
        right_layout.addWidget(preview_header)

        # Preview area
        preview_area = QTextBrowser()
        preview_area.setReadOnly(True)
        preview_area.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                border: none;
            }
        """)
        preview_font = QFont("Courier New", 10)
        preview_font.setStyleHint(QFont.Monospace)
        preview_area.setFont(preview_font)
        self.previews[realm] = preview_area

        right_layout.addWidget(preview_area)
        splitter.addWidget(right_widget)

        # Set proportions
        splitter.setSizes([400, 900])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        layout.addWidget(splitter)
        return realm_widget

    def _load_all_templates(self):
        """Load all templates from all realms by reading directory structure"""
        try:
            realms = ['Albion', 'Hibernia', 'Midgard']

            for realm in realms:
                # Get realm directory path - templates are in Armory/[Realm]/Templates/
                realm_dir = self.template_manager.armory_path / realm / "Templates"

                if not realm_dir.exists():
                    logger.warning(f"Realm directory not found: {realm_dir}")
                    continue

                # List all .txt files in the realm directory
                template_files = sorted(realm_dir.glob("*.txt"))
                # Get full filename with extension
                templates = [f.name for f in template_files]

                table = self.tables[realm]
                table.setRowCount(0)

                for template in templates:
                    row = table.rowCount()
                    table.insertRow(row)

                    # Filename column
                    filename_item = QTableWidgetItem(template)
                    filename_item.setData(Qt.UserRole, template)
                    table.setItem(row, 0, filename_item)

                    # Class column - get from metadata
                    class_name = self._get_template_class(realm, template)
                    class_item = QTableWidgetItem(class_name)
                    table.setItem(row, 1, class_item)

                template_count = len(templates)
                log_msg = (
                    f"Loaded {template_count} templates for {realm} "
                    f"from {realm_dir}"
                )
                logger.info(log_msg)

        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            import traceback
            logger.error(traceback.format_exc())
            SilentMessageBox.critical(
                self,
                lang.get("dialogs.titles.error", default="Error"),
                f"Error loading templates: {e}"
            )

    def _get_template_class(self, realm, template_filename):
        """Get template class from metadata file

        Args:
            realm: The realm
            template_filename: Template filename (with .txt extension)

        Returns:
            Class name or "Unknown" if not found
        """
        try:
            metadata_path = (
                self.template_manager._get_metadata_path(realm, template_filename)
            )
            if metadata_path.exists():
                from Functions.template_metadata import TemplateMetadata
                metadata = TemplateMetadata.load(metadata_path)
                if metadata and metadata.character_class:
                    return metadata.character_class
        except Exception as e:
            logger.debug(f"Could not load class for {realm}/{template_filename}: {e}")

        return "Unknown"

    def _on_template_selected(self, realm):
        """Handle template selection

        Args:
            realm: The realm whose template was selected
        """
        table = self.tables[realm]
        selected_rows = table.selectedIndexes()

        if not selected_rows:
            self.previews[realm].clear()
            return

        row = selected_rows[0].row()
        filename = table.item(row, 0).text()

        self._show_preview(realm, filename)

    def _show_preview(self, realm, filename):
        """Display template preview with automatic format detection

        Args:
            realm: The realm
            filename: The template filename (includes .txt extension)
        """
        try:
            # Read template file directly - templates are in Armory/[Realm]/Templates/
            realm_dir = self.template_manager.armory_path / realm / "Templates"
            template_file = realm_dir / filename

            if not template_file.exists():
                error_msg = lang.get(
                    "armoury_dialog.preview.file_not_found",
                    default="File not found"
                ).format(filename=template_file.name)
                self.previews[realm].setHtml(
                    f"<span style='color: red;'>{error_msg}</span>"
                )
                logger.warning(f"Template file not found: {template_file}")
                return

            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse template - automatically detects format (Loki, Zenkcraft, etc.)
            parse_result = template_parse(
                content,
                realm=realm,
                template_manager=self.template_manager,
                db_manager=self.db_manager
            )
            formatted_content, items_without_price = parse_result

            # Convert to HTML with color support
            import re

            # Replace color markers with HTML spans
            color_pattern = r'%%COLOR_START:(.+?)%%(.*?)%%COLOR_END%%'

            def replace_color(match):
                color = match.group(1)
                text = match.group(2)
                return f"<span style='color:{color}'>{text}</span>"

            formatted_content = re.sub(color_pattern, replace_color, formatted_content)

            # Replace spaces OUTSIDE HTML tags
            formatted_content = re.sub(r' (?![^<]*>)', '&nbsp;', formatted_content)

            # Convert newlines to <br>
            html_content = formatted_content.replace('\n', '<br>')
            html_content = f"<div style='line-height: 1.1;'>{html_content}</div>"

            # Display formatted content
            self.previews[realm].setHtml(html_content)

        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            import traceback

            logger.error(traceback.format_exc())
            error_msg = lang.get(
                "armoury_dialog.preview.error",
                default="Error reading file"
            ).format(error=str(e))
            self.previews[realm].setHtml(
                f"<span style='color: red;'>{error_msg}</span>"
            )

    def import_template(self):
        """Open import template dialog for all realms without character."""
        from UI.ui_armory_template_import_dialog import TemplateImportDialog

        # Create a generic character data dict
        generic_character = {
            'character_class': '',
            'class_fr': '',
            'class_de': '',
            'realm': 'Albion',
            'name': 'All Templates'
        }

        # Open template import dialog in non-auto-detect mode
        # Shows dropdowns for manual selection instead of auto-detect
        dialog = TemplateImportDialog(self, generic_character, auto_detect_mode=False)

        # Connect signal to reload templates when import succeeds
        dialog.template_imported.connect(lambda: self._load_all_templates())

        dialog.exec()

    def _show_context_menu(self, realm, pos):
        """Show context menu for template operations"""
        from PySide6.QtWidgets import QMenu

        table = self.tables[realm]
        item = table.itemAt(pos)

        if not item:
            return

        row = table.row(item)
        template_name = table.item(row, 0).text()

        menu = QMenu(self)

        # Edit action
        edit_label = lang.get("template_context_menu.edit", default="Editer")
        edit_text = "✏️ " + edit_label
        edit_action = menu.addAction(edit_text)
        def edit_cb():
            return self._edit_template(realm, template_name)
        edit_action.triggered.connect(edit_cb)

        # Delete action
        delete_label = lang.get("template_context_menu.delete", default="Supprimer")
        delete_text = "🗑️ " + delete_label
        delete_action = menu.addAction(delete_text)
        def delete_cb():
            return self._delete_template(realm, template_name)
        delete_action.triggered.connect(delete_cb)

        menu.addSeparator()

        # Download action
        download_label = lang.get(
            "template_context_menu.download", default="Download"
        )
        download_text = "💾 " + download_label
        download_action = menu.addAction(download_text)
        def download_cb():
            return self._download_template(realm, template_name)
        download_action.triggered.connect(download_cb)

        menu.exec(table.mapToGlobal(pos))

    def _edit_template(self, realm, template_name):
        """Edit template information"""
        from UI.ui_armory_template_edit_dialog import TemplateEditDialog
        from Functions.template_metadata import TemplateMetadata

        try:
            # Load metadata - template_name includes .txt extension
            metadata_path = self.template_manager._get_metadata_path(
                realm, template_name
            )
            logger.debug(f"Looking for metadata at: {metadata_path}")
            logger.debug(f"Metadata exists: {metadata_path.exists()}")
            if not metadata_path.exists():
                from PySide6.QtWidgets import QMessageBox
                error_msg = f"Fichier de métadonnées non trouvé: {metadata_path}"
                logger.error(error_msg)
                SilentMessageBox.warning(
                    self,
                    "Erreur",
                    error_msg
                )
                return

            metadata = TemplateMetadata.load(metadata_path)
            if not metadata:
                from PySide6.QtWidgets import QMessageBox
                error_title = lang.get(
                    "dialogs.titles.error", default="Erreur"
                )
                error_message = lang.get(
                    "template_edit.metadata_invalid",
                    default="Métadonnées invalides"
                )
                SilentMessageBox.warning(self, error_title, error_message)
                return

            # Open edit dialog
            dialog = TemplateEditDialog(self, template_name, realm, metadata)
            if dialog.exec():
                # Reload templates when edit succeeds
                self._load_all_templates()

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            logger.error(f"Error editing template: {e}")
            error_title = lang.get("dialogs.titles.error", default="Erreur")
            error_msg = f"Erreur lors de l'édition du template: {str(e)}"
            SilentMessageBox.critical(self, error_title, error_msg)

    def _delete_template(self, realm, template_name):
        """Delete a template"""
        from PySide6.QtWidgets import QMessageBox

        confirm_title = lang.get(
            "template_context_menu.confirm_delete",
            default="Confirmer la suppression"
        )
        confirm_msg = lang.get(
            "template_context_menu.delete_confirm_message",
            default="Êtes-vous sûr de vouloir supprimer ce template?"
        )
        reply = SilentMessageBox.question(
            self, confirm_title, confirm_msg,
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(template_name, realm):
                self._load_all_templates()
            else:
                error_title = lang.get(
                    "dialogs.titles.error", default="Erreur"
                )
                error_msg = lang.get(
                    "template_context_menu.delete_error",
                    default="Impossible de supprimer le template"
                )
                SilentMessageBox.warning(self, error_title, error_msg)

    def _download_template(self, realm, template_name):
        """Download/export template to user-selected location"""
        try:
            from PySide6.QtWidgets import QFileDialog, QMessageBox
            import shutil

            # Get source file path
            source_file = self.template_manager._get_template_path(
                realm, template_name
            )

            if not source_file.exists():
                error_title = lang.get(
                    "dialogs.titles.error", default="Erreur"
                )
                error_msg = lang.get(
                    "armoury_dialog.messages.file_not_found",
                    default="Fichier non trouvé",
                    filename=template_name
                )
                SilentMessageBox.warning(self, error_title, error_msg)
                return

            # Ask user where to save the file
            save_title = lang.get(
                "armoury_dialog.dialogs.download_file",
                default="Enregistrer le fichier"
            )
            save_filter = lang.get(
                "armoury_dialog.dialogs.all_files",
                default="Tous les fichiers (*.*)"
            )
            save_path, _ = QFileDialog.getSaveFileName(
                self, save_title, template_name, save_filter
            )

            if save_path:
                shutil.copy2(str(source_file), save_path)
                success_title = lang.get(
                    "dialogs.titles.success", default="Succès"
                )
                success_msg = lang.get(
                    "armoury_dialog.messages.download_success",
                    default="Fichier téléchargé avec succès",
                    filename=source_file.name
                )
                SilentMessageBox.information(self, success_title, success_msg)
                logger.info(f"Template downloaded: {save_path}")
        except Exception as e:
            logger.error(f"Error downloading template: {e}")
            error_title = lang.get("dialogs.titles.error", default="Erreur")
            error_msg = lang.get(
                "armoury_dialog.messages.download_error",
                default="Erreur lors du téléchargement",
                error=str(e)
            )
            SilentMessageBox.critical(self, error_title, error_msg)

    def _save_column_widths(self, realm):
        """Save current column widths to config for a realm

        Args:
            realm: The realm name
        """
        try:
            table = self.tables[realm]
            config = ConfigManager()

            # Save width for each column
            column_widths = {}
            for col in range(table.columnCount()):
                column_widths[str(col)] = table.columnWidth(col)

            config.set(
                f"ui.template_view_column_widths.{realm}",
                column_widths,
                save=True
            )
            logger.debug(f"Saved column widths for {realm}: {column_widths}")
        except Exception as e:
            logger.debug(f"Error saving column widths for {realm}: {e}")

    def _restore_column_widths(self, realm, table):
        """Restore column widths from config for a realm

        Args:
            realm: The realm name
            table: The QTableWidget to restore widths for
        """
        try:
            config = ConfigManager()
            config_key = f"ui.template_view_column_widths.{realm}"
            column_widths = config.get(config_key, default=None)

            if (column_widths and isinstance(column_widths, dict)
                    and len(column_widths) == table.columnCount()):
                for col in range(table.columnCount()):
                    width = column_widths.get(str(col), None)
                    if width:
                        table.setColumnWidth(col, int(width))
                logger.debug(
                    f"Restored column widths for {realm}: {column_widths}"
                )
            else:
                # Set default widths if not saved
                table.setColumnWidth(0, 300)  # Template filename
                table.setColumnWidth(1, 100)  # Class
                logger.debug(f"Using default column widths for {realm}")
        except Exception as e:
            logger.debug(f"Error restoring column widths for {realm}: {e}")


