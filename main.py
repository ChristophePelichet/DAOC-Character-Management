"""
DAOC Character Manager - Main Application Entry Point
A PySide6-based character management application for Dark Age of Camelot.
"""

import os
import sys
import traceback
import logging

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTreeView, QStatusBar, 
    QLabel, QMessageBox, QMenu, QFileDialog, QHeaderView, QInputDialog,
    QToolButton, QSizePolicy, QStyleFactory, QGroupBox, QHBoxLayout,
    QComboBox, QPushButton, QLineEdit, QDialog
)
from PySide6.QtGui import (
    QFont, QStandardItemModel, QStandardItem, QIcon, QAction, 
    QGuiApplication, QPalette
)
from PySide6.QtCore import Qt, QSize, QByteArray, Slot

from Functions.character_manager import (
    create_character_data, save_character, get_all_characters, get_character_dir, 
    REALM_ICONS, delete_character, REALMS, rename_character, duplicate_character
)
from Functions.language_manager import lang, get_available_languages
from Functions.config_manager import config, get_config_dir
from Functions.logging_manager import setup_logging, get_log_dir, get_img_dir
from Functions.path_manager import get_base_path
from Functions.data_manager import DataManager

# Import UI components from modular UI package
from UI import (
    DebugWindow, QTextEditHandler, LogLevelFilter, LogFileReaderThread,
    CharacterSheetWindow, ColumnsConfigDialog, NewCharacterDialog, ConfigurationDialog,
    CenterIconDelegate, CenterCheckboxDelegate, RealmTitleDelegate
)

# Setup logging at the very beginning
setup_logging()

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Application Constants
APP_NAME = "DAOC Character Manager"
APP_VERSION = "0.104"

# ============================================================================


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catches unhandled exceptions and logs them with full traceback."""
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_string = "".join(tb_lines)
    logging.critical(f"Unhandled exception caught:\n{tb_string}")


class CharacterApp(QMainWindow):
    """
    Main class for the character management application.
    Manages the user interface and interactions.
    """
    def __init__(self):
        logging.info("Application starting...")
        super().__init__()
        self.setWindowTitle(lang.get("window_title"))
        self.resize(550, 400)

        # --- Initialize Data Manager ---
        self.data_manager = DataManager()

        # --- Pre-load resources for performance ---
        self._load_icons() # This method now populates self.tree_realm_icons etc. directly
        self.available_languages = get_available_languages()
        self.characters_by_id = {} # For quick access to character data

        self.config_window = None
        self.debug_window = None

        # --- Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Actions, Menus, and Toolbars ---
        self._create_actions()
        # --- Menu Bar ---
        self._create_menu_bar()

        # --- Bulk Actions Bar ---
        self._create_bulk_actions_bar(main_layout)

        # --- Main content ---
        # --- Character List (Treeview) ---
        self.character_tree = QTreeView()
        self.character_tree.setAlternatingRowColors(True)
        self.character_tree.setRootIsDecorated(False) # To make it look like a table
        self.character_tree.setSortingEnabled(True) # Enable column sorting
        main_layout.addWidget(self.character_tree)

        # Apply a stylesheet to show grid lines, as QTreeView doesn't have setShowGrid
        grid_color = "#d6d6d6"
        text_color = "#000000"
        selected_text_color = "#ffffff"
        selected_bg_color = "#0078d4"
        
        self.character_tree.setStyleSheet(f"""
            QTreeView::item {{
                border-right: 1px solid {grid_color};
                color: {text_color};
            }}
            QTreeView::item:selected {{
                color: {selected_text_color};
                background-color: {selected_bg_color};
            }}
            QTreeView {{
                border-bottom: 1px solid {grid_color};
            }}
        """)

        self.tree_model = QStandardItemModel()
        self.character_tree.setModel(self.tree_model)
        
        # Apply custom delegate to center icons in the realm column (column 0)
        self.center_icon_delegate = CenterIconDelegate(self)
        self.character_tree.setItemDelegateForColumn(1, self.center_icon_delegate) # Realm column is now at index 1

        # Apply custom delegate to center the checkbox in the selection column
        self.center_checkbox_delegate = CenterCheckboxDelegate(self)
        self.character_tree.setItemDelegateForColumn(0, self.center_checkbox_delegate) # Selection column is at index 0
        
        # Apply custom delegate for realm title (column 9)
        self.realm_title_delegate = RealmTitleDelegate(self)
        self.character_tree.setItemDelegateForColumn(9, self.realm_title_delegate)

        # --- Bindings ---
        self.character_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.character_tree.customContextMenuRequested.connect(self.on_tree_right_click)
        self.character_tree.doubleClicked.connect(self.on_character_double_click)
        # Log column movements
        self.character_tree.header().sectionMoved.connect(self.on_section_moved)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Initialisation...")
        self.status_bar.addWidget(self.status_label)

        # Load the character list on application startup
        self.refresh_character_list()

        # Create menus that might need re-translation
        self._create_context_menu()

        # Show disclaimer on startup if not disabled
        self.show_startup_disclaimer()

    def show_startup_disclaimer(self):
        """Shows a disclaimer message on startup if not disabled in settings."""
        if not config.get("disable_disclaimer", False):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(lang.get("disclaimer_title", default="Alpha Version - Information"))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(lang.get("disclaimer_message", default="Version Alpha"))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

    def _create_actions(self):
        """Create all QAction objects for the application."""
        # Actions are now created directly in the menu bar method
        pass

    def _create_menu_bar(self):
        """Setup the menu bar with File, View, and Help menus."""
        menubar = self.menuBar()
        menubar.clear()  # Clear existing menus
        
        # File Menu
        file_menu = menubar.addMenu(lang.get("menu_file"))
        
        # File -> New Character
        new_char_action = QAction(lang.get("menu_file_new_character"), self)
        new_char_action.triggered.connect(self.create_new_character)
        file_menu.addAction(new_char_action)
        
        file_menu.addSeparator()
        
        # File -> Settings
        settings_action = QAction(lang.get("menu_file_settings"), self)
        settings_action.triggered.connect(self.open_configuration)
        file_menu.addAction(settings_action)
        
        # View Menu
        view_menu = menubar.addMenu(lang.get("menu_view"))
        
        # View -> Columns
        columns_action = QAction(lang.get("menu_view_columns"), self)
        columns_action.triggered.connect(self.open_columns_configuration)
        view_menu.addAction(columns_action)
        
        # Help Menu
        help_menu = menubar.addMenu(lang.get("menu_help"))
        
        # Help -> About
        about_action = QAction(lang.get("menu_help_about"), self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _create_context_menu(self):
        """Creates or updates the right-click context menu for the tree view."""
        self.context_menu = QMenu(self)

        # Add rename action
        rename_action = self.context_menu.addAction(lang.get("context_menu_rename", default="Renommer"))
        rename_action.triggered.connect(self.rename_selected_character)

        # Add duplicate action
        duplicate_action = self.context_menu.addAction(lang.get("context_menu_duplicate", default="Dupliquer"))
        duplicate_action.triggered.connect(self.duplicate_selected_character)

        self.context_menu.addSeparator()

        # Add armor management action
        armor_action = self.context_menu.addAction(lang.get("context_menu_armor_management", default="Gestion des armures"))
        armor_action.triggered.connect(self.open_armor_management_global)

        self.context_menu.addSeparator()

        # Only keep the action to delete the right-clicked character
        delete_action = self.context_menu.addAction(lang.get("context_menu_delete", default="Supprimer"))
        delete_action.triggered.connect(self.delete_selected_character)

    def _create_bulk_actions_bar(self, parent_layout):
        """Creates the bar for bulk actions above the character list."""
        bulk_actions_group = QGroupBox(lang.get("bulk_actions_group_title", default="Actions sur la sélection"))
        bulk_actions_layout = QHBoxLayout()

        self.bulk_action_combo = QComboBox()
        self.bulk_action_combo.addItem(lang.get("bulk_action_delete", default="Supprimer la sélection"))
        # Add more actions here in the future
        bulk_actions_layout.addWidget(self.bulk_action_combo)

        execute_button = QPushButton(lang.get("bulk_action_execute_button", default="Exécuter"))
        execute_button.clicked.connect(self.execute_bulk_action)
        bulk_actions_layout.addWidget(execute_button)

        bulk_actions_group.setLayout(bulk_actions_layout)
        parent_layout.addWidget(bulk_actions_group)

    def execute_bulk_action(self):
        """Executes the selected bulk action on checked characters."""
        selected_action = self.bulk_action_combo.currentText()
        if selected_action == lang.get("bulk_action_delete"):
            self.delete_checked_characters()

    def _load_icons(self):
        """Loads and resizes all required icons once at startup."""
        logging.debug("Pre-loading UI icons.")
        logging.debug(f"REALM_ICONS type: {type(REALM_ICONS)}, content: {REALM_ICONS}, is_empty: {not REALM_ICONS}, bool: {bool(REALM_ICONS)}")
        self.tree_realm_icons = {}
        img_dir = get_img_dir() # Use the centralized function

        if not REALM_ICONS:
            logging.warning(f"REALM_ICONS dictionary is empty. No realm icons will be loaded. Type: {type(REALM_ICONS)}, Content: {REALM_ICONS}")
            # DO NOT return here - continue loading other icons
        else:
            logging.debug("--- Verification des icônes de royaume ---")
            for realm, icon_path in REALM_ICONS.items():
                logging.debug(f"Royaume: '{realm}' -> Fichier icône attendu: '{icon_path}'")
                try:
                    full_path = os.path.join(img_dir, icon_path)
                    logging.debug(f"Chemin complet: '{full_path}', Existe: {os.path.exists(full_path)}")
                    # For PySide, we just need the QIcon object
                    icon = QIcon(full_path)
                    self.tree_realm_icons[realm] = icon
                    logging.debug(f"Icône créée pour {realm}. isNull: {icon.isNull()}")
                except Exception as e:
                    logging.warning(f"Error loading icon for {realm} at {full_path}: {e}")
                    self.tree_realm_icons[realm] = None
            logging.debug("--- Fin de la vérification ---")
            logging.debug(f"Icônes chargées dans tree_realm_icons: {list(self.tree_realm_icons.keys())}")
        
        logging.debug(f"Icon loading complete. Realm icons loaded: {len(self.tree_realm_icons)}")

    def create_new_character(self):
        """
        Handles the action of creating a new character manually.
        """
        seasons = config.get("seasons", ["S1", "S2", "S3"])
        default_season = config.get("default_season", "S1")
        dialog = NewCharacterDialog(self, realms=REALMS, seasons=seasons, default_season=default_season)
        result = dialog.get_data() if dialog.exec() == QDialog.Accepted else None

        if result:
            character_name, realm, season, level, page, guild, race, class_name = result
            character_data = create_character_data(character_name, realm, season, "Eden", level, page, guild, race, class_name)
            success, response = save_character(character_data)
            if success:
                self.refresh_character_list()
                logging.info(f"Successfully created character '{character_name}' ({race} {class_name}).")
                QMessageBox.information(self, lang.get("success_title"), lang.get("char_saved_success", name=character_name))
            else:
                # If the response is a known error key, translate it. Otherwise, display as is.
                if response == "char_exists_error":
                    error_message = lang.get(response, name=character_name)
                else:
                    error_message = response  # For other potential errors
                logging.error(f"Failed to create character '{character_name}': {error_message}")
                QMessageBox.critical(self, lang.get("error_title"), error_message)
        else:
            logging.info("Character creation cancelled by user.")

    def refresh_character_list(self):
        """Updates the character list in the dropdown menu."""
        logging.debug("Refreshing character list.")
        
        self.tree_model.clear()
        self.characters_by_id.clear()

        # Set headers in new order: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server, Class, Race
        headers = [
            lang.get("column_selection"), 
            lang.get("column_realm"),
            lang.get("column_name"), 
            lang.get("column_level"),
            lang.get("column_realm_rank", default="Rang"),
            lang.get("column_realm_title", default="Titre"),
            lang.get("column_guild", default="Guilde"),
            lang.get("column_page", default="Page"),
            lang.get("column_server", default="Serveur"),
            lang.get("column_class", default="Classe"),
            lang.get("column_race", default="Race")]
        self.tree_model.setHorizontalHeaderLabels(headers)
        
        # Center align the realm column header
        realm_header = self.tree_model.horizontalHeaderItem(1) # Realm is now at index 1
        if realm_header:
            realm_header.setTextAlignment(Qt.AlignCenter)

        # Center align the season column header
        season_header = self.tree_model.horizontalHeaderItem(2) # Season is at index 2
        if season_header:
            season_header.setTextAlignment(Qt.AlignCenter)

        # Center align the level column header
        level_header = self.tree_model.horizontalHeaderItem(5) # Level is at index 5
        if level_header:
            level_header.setTextAlignment(Qt.AlignCenter)

        # Center align the page column header
        page_header = self.tree_model.horizontalHeaderItem(6) # Page is at index 6
        if page_header:
            page_header.setTextAlignment(Qt.AlignCenter)

        # Center align the realm rank column header
        realm_rank_header = self.tree_model.horizontalHeaderItem(8) # Realm Rank is at index 8
        if realm_rank_header:
            realm_rank_header.setTextAlignment(Qt.AlignCenter)

        # Center align the realm title column header
        realm_title_header = self.tree_model.horizontalHeaderItem(9) # Realm Title is at index 9
        if realm_title_header:
            realm_title_header.setTextAlignment(Qt.AlignCenter)

        characters = get_all_characters()
        # Add a detailed log to check the state of the icons dictionary just before the loop
        logging.debug(f"Populating tree with {len(characters)} character(s). tree_realm_icons contains {len(self.tree_realm_icons)} icon(s): {list(self.tree_realm_icons.keys()) if self.tree_realm_icons else 'None'}")

        for i, char in enumerate(characters):
            realm_name = char.get('realm', 'N/A')
            realm_icon = self.tree_realm_icons.get(realm_name) if self.tree_realm_icons else None
            char_id = char.get('id')
            self.characters_by_id[char_id] = char

            logging.debug(f"Character {i+1}/{len(characters)}: '{char.get('name')}' (realm='{realm_name}') - icon found: {realm_icon is not None}, isNull: {realm_icon.isNull() if realm_icon else 'N/A'}")
            # Create items for each column in the row
            item_realm = QStandardItem() # On ne met que l'icône, pas de texte.
            if realm_icon:
                # Store realm name in UserRole+1 for sorting, but don't display it as text
                item_realm.setData(realm_name, Qt.UserRole + 1)  # For sorting
                item_realm.setIcon(realm_icon)
                # Don't call setText() - we only want the icon, no text
            item_realm.setData(char_id, Qt.UserRole) # Store char_id in the item
            item_realm.setTextAlignment(Qt.AlignCenter) # Centrer l'icône
            item_realm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Make non-editable

            item_name = QStandardItem(char.get('name', 'N/A'))
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Make non-editable
            item_level = QStandardItem(str(char.get('level', 1)))
            item_level.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Make non-editable
            item_level.setTextAlignment(Qt.AlignCenter)
            item_page = QStandardItem(str(char.get('page', 1)))
            item_page.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_page.setTextAlignment(Qt.AlignCenter)
            item_guild = QStandardItem(char.get('guild', ''))
            item_guild.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            
            item_server = QStandardItem(char.get('server', 'Eden'))
            item_server.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_server.setTextAlignment(Qt.AlignCenter)
            
            item_class = QStandardItem(char.get('class', ''))
            item_class.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_class.setTextAlignment(Qt.AlignCenter)
            # Ensure the text is not bold
            font = item_class.font()
            font.setBold(False)
            item_class.setFont(font)
            
            item_race = QStandardItem(char.get('race', ''))
            item_race.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_race.setTextAlignment(Qt.AlignCenter)
            
            # Calculate realm rank and title from realm points
            realm_points = char.get('realm_points', 0)
            realm_rank_level = char.get('realm_rank', '1L1')
            realm_title = ""
            
            # Get rank info from DataManager
            rank_info = self.data_manager.get_realm_rank_info(realm_name, realm_points)
            if rank_info:
                realm_rank_level = rank_info['level']
                realm_title = rank_info['title']
            
            item_realm_rank = QStandardItem(str(realm_rank_level))
            item_realm_rank.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_realm_rank.setTextAlignment(Qt.AlignCenter)
            
            item_realm_title = QStandardItem(realm_title)
            item_realm_title.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_realm_title.setTextAlignment(Qt.AlignCenter)
            item_realm_title.setData(realm_name, Qt.UserRole)  # Stocker le royaume pour le delegate
            
            item_selection = QStandardItem()
            item_selection.setCheckable(True)
            item_selection.setCheckState(Qt.Unchecked)
            # Allow checking but not direct text editing
            item_selection.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)

            # New order: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server, Class, Race
            row_items = [item_selection, item_realm, item_name, item_level, item_realm_rank, item_realm_title, item_guild, item_page, item_server, item_class, item_race]
            self.tree_model.appendRow(row_items)

        self.character_tree.header().setStretchLastSection(False)
        
        # Connect the model's dataChanged signal to update selection count
        self.tree_model.dataChanged.connect(self.update_selection_count)

        # Restore header state AFTER the model and headers are set
        header_state_b64 = config.get("tree_view_header_state")
        if header_state_b64:
            logging.debug(f"Attempting to restore header state from config: {header_state_b64}")
            try:
                header_state = QByteArray.fromBase64(header_state_b64.encode('ascii'))
                if self.character_tree.header().restoreState(header_state):
                    logging.info("Successfully restored QTreeView header state.")
                else:
                    logging.warning("Could not restore QTreeView header state. It might be invalid or for a different column setup.")
            except Exception as e:
                logging.error(f"Error restoring header state: {e}")
        
        # Apply column visibility settings
        self.apply_column_visibility()
        
        # Apply column resize mode
        manual_resize = config.get("manual_column_resize", False)
        self.apply_column_resize_mode(manual_resize)
        # Apply column resize mode
        manual_resize = config.get("manual_column_resize", False)
        self.apply_column_resize_mode(manual_resize)

    def apply_column_resize_mode(self, manual_mode=False):
        """Apply column resize mode (automatic or manual).
        
        Args:
            manual_mode: If True, enables manual resizing. If False, uses automatic sizing.
        """
        header = self.character_tree.header()
        
        if manual_mode:
            # Manual mode: Allow user to resize columns freely
            header.setSectionResizeMode(QHeaderView.Interactive)
            logging.debug("Column resize mode: Manual (Interactive)")
        else:
            # Automatic mode: Auto-resize columns with Name column stretching
            for i in range(11):  # 11 columns: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server, Class, Race
                if i == 2:  # Name column (index 2)
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            logging.debug("Column resize mode: Automatic (ResizeToContents + Stretch for Name)")

    def apply_column_visibility(self):
        """Apply column visibility settings from configuration."""
        visibility_config = config.get("column_visibility", {})
        
        # Default visibility settings (server is hidden by default)
        default_visibility = {
            "selection": True,
            "realm": True,
            "name": True,
            "level": True,
            "page": True,
            "guild": True,
            "realm_rank": True,
            "realm_title": True,
            "server": False,  # Server column hidden by default
            "class": True,  # Class column visible by default
            "race": False,  # Race column hidden by default
        }
        
        # Map column keys to their indices with new order: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server, Class, Race
        column_map = {
            "selection": 0,
            "realm": 1,
            "name": 2,
            "level": 3,
            "realm_rank": 4,
            "realm_title": 5,
            "guild": 6,
            "page": 7,
            "server": 8,
            "class": 9,
            "race": 10,
        }
        
        # Apply visibility to each column
        for key, index in column_map.items():
            is_visible = visibility_config.get(key, default_visibility.get(key, True))
            self.character_tree.setColumnHidden(index, not is_visible)
        
        # Redimensionner les colonnes visibles
        for key, index in column_map.items():
            is_visible = visibility_config.get(key, True)
            if is_visible and index != 2:  # Ne pas redimensionner la colonne Nom (elle est en Stretch) - index 2 maintenant
                self.character_tree.resizeColumnToContents(index)
        
        # Réappliquer le mode Stretch sur la colonne Nom si elle est visible
        if visibility_config.get("name", True):
            self.character_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)  # Name column is now at index 2


    def on_tree_right_click(self, position):
        """Shows a context menu on right-click."""
        index = self.character_tree.indexAt(position)
        if index.isValid():
            self.context_menu.exec(self.character_tree.viewport().mapToGlobal(position))

    def delete_selected_character(self):
        """Deletes the character currently selected in the treeview."""
        indexes = self.character_tree.selectedIndexes()
        if indexes:
            # Get the item from the first column of the selected row
            row = indexes[0].row()
            name_item = self.tree_model.item(row, 2) # Name is at index 2
            char_name = name_item.text()
            if char_name:
                self.delete_character(char_name)

    def rename_selected_character(self):
        """Renames the character currently selected in the treeview."""
        indexes = self.character_tree.selectedIndexes()
        if not indexes:
            return

        row = indexes[0].row()
        name_item = self.tree_model.item(row, 2) # Name is at index 2
        old_name = name_item.text()

        if not old_name:
            return

        # Use QInputDialog to get the new name
        new_name, ok = QInputDialog.getText(self,
                                            lang.get("rename_char_dialog_title", default="Renommer le personnage"),
                                            lang.get("rename_char_dialog_prompt", default="Nouveau nom :"),
                                            QLineEdit.Normal,
                                            old_name)

        if ok and new_name:
            new_name = new_name.strip()
            if new_name == old_name:
                return # No change

            if not new_name:
                QMessageBox.warning(self, lang.get("error_title"), lang.get("char_name_empty_error"))
                return

            success, msg = rename_character(old_name, new_name)
            if success:
                self.refresh_character_list()
            else:
                error_msg = lang.get(msg, name=new_name) if msg == "char_exists_error" else msg
                QMessageBox.critical(self, lang.get("error_title"), error_msg)

    def duplicate_selected_character(self):
        """Duplicates the currently selected character."""
        indexes = self.character_tree.selectedIndexes()
        if not indexes:
            return

        row = indexes[0].row()
        name_item = self.tree_model.item(row, 2) # Name is at index 2
        original_name = name_item.text()

        if not original_name:
            return

        original_char_data = self.characters_by_id.get(original_name)
        if not original_char_data:
            logging.error(f"Could not find data for character '{original_name}' to duplicate.")
            return

        # Ask for a new name
        new_name, ok = QInputDialog.getText(self,
                                            lang.get("duplicate_char_dialog_title", default="Dupliquer le personnage"),
                                            lang.get("duplicate_char_dialog_prompt", default="Nom du nouveau personnage :"),
                                            QLineEdit.Normal,
                                            f"{original_name}_copy") # Suggest a default new name

        if ok and new_name:
            new_name = new_name.strip()
            if not new_name:
                QMessageBox.warning(self, lang.get("error_title"), lang.get("char_name_empty_error"))
                return

            success, msg = duplicate_character(original_char_data, new_name)
            if success:
                self.refresh_character_list()
            else:
                error_msg = lang.get(msg, name=new_name) if msg == "char_exists_error" else msg
                QMessageBox.critical(self, lang.get("error_title"), error_msg)

    def get_checked_character_ids(self):
        """Returns a list of character IDs for all checked rows."""
        checked_ids = []
        for row in range(self.tree_model.rowCount()):
            # The checkbox is in the first column (index 0)
            selection_item = self.tree_model.item(row, 0)
            if selection_item and selection_item.checkState() == Qt.Checked:
                # The ID is stored in the realm item of the row (index 1)
                name_item = self.tree_model.item(row, 2) # Name is at index 2
                char_name = name_item.text()
                if char_name:
                    checked_ids.append(char_name)
        return checked_ids

    def delete_checked_characters(self):
        """Deletes all characters that are checked in the tree view."""
        checked_ids = self.get_checked_character_ids()

        if not checked_ids:
            QMessageBox.warning(self, lang.get("info_title"), lang.get("no_characters_selected_warning"))
            return

        reply = QMessageBox.question(self,
                                     lang.get("delete_char_confirm_title"),
                                     lang.get("bulk_delete_confirm_message", count=len(checked_ids)),
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            logging.info(f"User initiated bulk deletion of {len(checked_ids)} characters.")
            for char_name in checked_ids:
                # We skip the individual confirmation dialog by directly calling the backend function
                self.delete_character(char_name, confirm=False)
            self.refresh_character_list()

    def select_all_characters(self):
        """Selects all characters in the tree view."""
        for row in range(self.tree_model.rowCount()):
            selection_item = self.tree_model.item(row, 0)
            if selection_item:
                selection_item.setCheckState(Qt.Checked)
        self.update_selection_count()
        logging.debug(f"All {self.tree_model.rowCount()} characters selected")

    def deselect_all_characters(self):
        """Deselects all characters in the tree view."""
        for row in range(self.tree_model.rowCount()):
            selection_item = self.tree_model.item(row, 0)
            if selection_item:
                selection_item.setCheckState(Qt.Unchecked)
        self.update_selection_count()
        logging.debug("All characters deselected")

    def update_selection_count(self):
        """Updates the status bar with the count of selected characters."""
        checked_ids = self.get_checked_character_ids()
        total = self.tree_model.rowCount()
        
        if len(checked_ids) > 0:
            self.update_status_bar(lang.get("status_bar_selection_count", count=len(checked_ids), total=total))
        else:
            # Restore the default status message
            if hasattr(self, 'load_time'):
                self.update_status_bar(lang.get("status_bar_loaded", duration=self.load_time))
            else:
                self.update_status_bar("")

    def delete_character(self, char_name, confirm=True):
        """Handles the character deletion process."""
        if not char_name:
            logging.warning(f"Attempted to delete character with empty name.")
            return

        reply = QMessageBox.Yes
        if confirm:
            reply = QMessageBox.question(self,
                                         lang.get("delete_char_confirm_title"),
                                         lang.get("delete_char_confirm_message", name=char_name),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, msg = delete_character(char_name)
            if success:
                logging.info(f"Character '{char_name}' deleted by user.")
                if confirm: # Refresh only if it's a single delete action
                    self.refresh_character_list()
            else:
                logging.error(f"Failed to delete character '{char_name}' from UI: {msg}")
                QMessageBox.critical(self, lang.get("error_title"), msg)

    def on_character_double_click(self, index): # Renamed from delete_character_by_id
        """Gère le double-clic sur un personnage dans la liste."""
        if not index.isValid():
            return

        # Prevent sheet from opening when clicking the checkbox column (index 3)
        if index.column() == 0: # Selection column is now at index 0
            return

        # Get the item from the first column to retrieve the ID
        name_item = self.tree_model.item(index.row(), 2) # Name is at index 2
        char_name = name_item.text()

        character_data = self.characters_by_id.get(char_name)
        if character_data:
            char_name = character_data.get('name', 'N/A')
            logging.info(f"Ouverture de la feuille du personnage '{char_name}'.")
            sheet = CharacterSheetWindow(self, character_data)
            sheet.exec() # Show the dialog modally
        else:
            logging.warning(f"Impossible de trouver les données pour le personnage avec le nom '{char_name}' lors du double-clic.")

    @Slot(int, int, int)
    def on_section_moved(self, logical_index, old_visual_index, new_visual_index):
        """Logs when a column is moved by the user."""
        header_item = self.tree_model.horizontalHeaderItem(logical_index)
        column_name = header_item.text() if header_item else f"Column with logical index {logical_index}"
        logging.debug(f"Column '{column_name}' moved from visual position {old_visual_index} to {new_visual_index}.")

    def change_language(self, lang_code):
        """Changes the application language and updates the UI."""
        logging.info(f"Changing language to {lang_code}.")
        config.set("language", lang_code)
        lang.set_language(lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Updates the text of all UI widgets."""
        self.setWindowTitle(lang.get("window_title"))
        self._create_menu_bar()  # Recreate menu bar with new translations
        self.refresh_character_list() # This will update headers
        self._create_context_menu() # Retranslate context menu

        # Update status bar if it exists
        if hasattr(self, 'load_time'):
            self.update_status_bar(lang.get("status_bar_loaded", duration=self.load_time))
        
        # Retranslate the config window if it exists
        if self.config_window:
            self._retranslate_configuration_window()
        
        # Retranslate the debug window if it exists
        if self.debug_window:
            pass # self.debug_window.retranslate() # TODO

    def show_debug_window(self):
        """Creates and shows the debug window, positioning it next to the main window."""
        if not self.debug_window:
            self.debug_window = DebugWindow()
        
        # Position the debug window to the right of the main window
        main_window_geom = self.geometry()
        self.debug_window.move(main_window_geom.right() + 10, main_window_geom.top())
        self.debug_window.show()


    def hide_debug_window(self):
        if self.debug_window:
            self.debug_window.close()
            self.debug_window = None

    def show_about_dialog(self):
        """Displays the 'About' dialog box with application information."""
        title = lang.get("about_dialog_title", app_name=APP_NAME)
        message = lang.get("about_dialog_content", app_name=APP_NAME, version=APP_VERSION)
        QMessageBox.about(self, title, message)

    def update_status_bar(self, message):
        """Updates the text in the status bar."""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)

    def _create_configuration_window(self):
        """Creates the configuration window widgets. Called only once."""
        logging.debug("Creating configuration window for the first time.")
        # TODO: PySide Migration
        pass

    def _update_configuration_fields(self):
        """Refreshes the values in the configuration window from the config."""
        # TODO: PySide Migration
        pass

    def _retranslate_configuration_window(self):
        """Updates the text of all widgets in the configuration window."""
        # TODO: PySide Migration
        pass

    def open_columns_configuration(self):
        """Opens the columns configuration dialog."""
        logging.debug("Opening columns configuration dialog.")
        dialog = ColumnsConfigDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Get the new visibility configuration
            visibility_config = dialog.get_visibility_config()
            config.set("column_visibility", visibility_config)
            # config.set() sauvegarde automatiquement via save_config()
            
            # Apply the new visibility
            self.apply_column_visibility()
            
            QMessageBox.information(self, 
                lang.get("success_title", default="Succès"), 
                lang.get("columns_config_saved", default="Configuration des colonnes sauvegardée."))

    def open_configuration(self):
        """Opens the configuration window."""
        logging.debug("Opening configuration window.")
        seasons = config.get("seasons", ["S1", "S2", "S3"])
        if not seasons:
            seasons = ["S1", "S2", "S3"]
        servers = config.get("servers", ["Eden", "Blackthorn"])
        if not servers:
            servers = ["Eden", "Blackthorn"]
        # Get realms dynamically from DataManager
        realms = self.data_manager.get_realms() if hasattr(self, 'data_manager') else ["Albion", "Hibernia", "Midgard"]
        dialog = ConfigurationDialog(self, self.available_languages, 
                                     available_seasons=seasons,
                                     available_servers=servers,
                                     available_realms=realms)
        if dialog.exec() == QDialog.Accepted:
            self.save_configuration(dialog)

    def save_configuration(self, dialog):
        """Saves the configuration and closes the window."""
        old_debug_mode = config.get("debug_mode", False)
        new_debug_mode = dialog.debug_mode_check.isChecked()

        if not new_debug_mode and old_debug_mode:
            logging.info("Debug mode has been DEACTIVATED. This is the last log entry.")

        config.set("character_folder", dialog.char_path_edit.text())
        config.set("config_folder", dialog.config_path_edit.text())
        config.set("log_folder", dialog.log_path_edit.text())
        config.set("armor_folder", dialog.armor_path_edit.text())
        config.set("debug_mode", new_debug_mode)
        config.set("show_debug_window", dialog.show_debug_window_check.isChecked())
        config.set("disable_disclaimer", dialog.disable_disclaimer_check.isChecked())
        config.set("seasons", dialog.available_seasons) # Preserve the season list
        config.set("servers", dialog.available_servers) # Preserve the server list
        
        new_default_season = dialog.default_season_combo.currentText()
        old_default_season = config.get("default_season", "")
        config.set("default_season", new_default_season)
        if new_default_season != old_default_season:
            logging.debug(f"Default season changed from '{old_default_season}' to '{new_default_season}'")

        new_default_server = dialog.default_server_combo.currentText()
        old_default_server = config.get("default_server", "")
        config.set("default_server", new_default_server)
        if new_default_server != old_default_server:
            logging.debug(f"Default server changed from '{old_default_server}' to '{new_default_server}'")

        new_default_realm = dialog.default_realm_combo.currentText()
        old_default_realm = config.get("default_realm", "")
        config.set("default_realm", new_default_realm)
        if new_default_realm != old_default_realm:
            logging.debug(f"Default realm changed from '{old_default_realm}' to '{new_default_realm}'")

        # Column resize mode
        new_manual_resize = dialog.manual_column_resize_check.isChecked()
        old_manual_resize = config.get("manual_column_resize", False)
        config.set("manual_column_resize", new_manual_resize)
        if new_manual_resize != old_manual_resize:
            logging.debug(f"Column resize mode changed to: {'manual' if new_manual_resize else 'automatic'}")
            # Apply the new resize mode immediately
            self.apply_column_resize_mode(new_manual_resize)

        selected_lang_name = dialog.language_combo.currentText()
        new_lang_code = None
        for code, name in self.available_languages.items():
            if name == selected_lang_name:
                new_lang_code = code
                break
        
        language_changed = new_lang_code and new_lang_code != config.get("language")
        if language_changed:
            config.set("language", new_lang_code)

        setup_logging()

        if new_debug_mode and not old_debug_mode:
            logging.info("Debug mode has been ACTIVATED.")

        QMessageBox.information(self, lang.get("success_title"), lang.get("config_saved_success"))

        if language_changed:
            self.change_language(new_lang_code)
    
    def open_resistances_table(self):
        """Opens the armor resistances table using the data editor."""
        logging.info("Opening armor resistances table from menu.")
        try:
            import subprocess
            import sys
            
            # Get the path to data_editor.py
            tools_dir = os.path.join(get_base_path(), "Tools")
            data_editor_path = os.path.join(tools_dir, "data_editor.py")
            
            if not os.path.exists(data_editor_path):
                QMessageBox.warning(
                    self,
                    "Erreur",
                    f"Le fichier data_editor.py est introuvable à l'emplacement :\n{data_editor_path}"
                )
                return
            
            # Launch data_editor.py in a separate process
            if sys.platform == "win32":
                # Windows: use pythonw to avoid console window
                subprocess.Popen([sys.executable, data_editor_path], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([sys.executable, data_editor_path])
            
            logging.info("Data editor launched successfully.")
            
        except Exception as e:
            logging.error(f"Error launching data editor: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de lancer l'éditeur de données :\n{str(e)}"
            )
    
    def open_armor_management_global(self):
        """Opens the armor management dialog (requires character selection)."""
        logging.info("Armor management requested from menu.")
        
        # Check if a character is selected
        indexes = self.character_tree.selectedIndexes()
        if not indexes:
            QMessageBox.information(
                self,
                lang.get("info_title", default="Information"),
                "Veuillez sélectionner un personnage dans la liste pour accéder à la gestion de ses armures.\n\n"
                "Vous pouvez aussi ouvrir la fiche du personnage et cliquer sur '📁 Gérer les armures'."
            )
            return
        
        # Get character data
        row = indexes[0].row()
        name_item = self.tree_model.item(row, 2)  # Name is at index 2
        character_name = name_item.text()
        
        if not character_name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de déterminer le nom du personnage."
            )
            return
        
        character_data = self.characters_by_id.get(character_name)
        
        if not character_data:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Impossible de trouver les données du personnage '{character_name}'."
            )
            return
        
        # Get character ID
        character_id = character_data.get('id', '')
        if not character_id:
            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de déterminer l'ID du personnage."
            )
            return
        
        # Open armor management dialog
        from UI.dialogs import ArmorManagementDialog
        dialog = ArmorManagementDialog(self, character_id)
        dialog.exec()

    def closeEvent(self, event):
        """Saves application state and ensures all child windows are closed."""
        logging.info("Main window closing. Shutting down application.")
        
        # Save the header state
        header_state = self.character_tree.header().saveState()
        header_state_b64 = header_state.toBase64().data().decode('ascii')
        logging.debug(f"Saving header state: {header_state_b64}")
        config.set("tree_view_header_state", header_state_b64)
        
        if self.debug_window:
            self.debug_window.close()
            
        super().closeEvent(event)


def apply_theme(app):
    """Applies the configured theme to the application."""
    # Clear any previous stylesheet
    app.setStyleSheet("")
    # Try to apply a native Windows look
    if "windowsvista" in QStyleFactory.keys():
        logging.info("Applying 'windowsvista' style for a native Windows look.")
        app.setStyle("windowsvista")
    else: # Fallback to light theme
        logging.info("Applying Light theme (default system style).")


def main():
    """Main function to launch the application."""
    import time
    start_time = time.perf_counter() # Keep time import local to main
    app = QApplication(sys.argv)
    apply_theme(app)
    # Set up global exception handling
    sys.excepthook = global_exception_handler
    
    main_window = CharacterApp()

    # Calculate and store loading time
    end_time = time.perf_counter()
    load_duration = end_time - start_time
    logging.info(f"Application loaded in {load_duration:.4f} seconds.") # type: ignore
    main_window.load_time = load_duration # Store it on the window instance
    main_window.update_status_bar(lang.get("status_bar_loaded", duration=load_duration))
    main_window.show()

    # Show debug window if configured, after the main window is shown and positioned
    if config.get("show_debug_window", False):
        main_window.show_debug_window()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()