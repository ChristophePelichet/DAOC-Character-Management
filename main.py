import os
import sys
import traceback
import logging

try:
    import qdarkstyle
    QDARKSTYLE_AVAILABLE = True
except ImportError:
    QDARKSTYLE_AVAILABLE = False

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTreeView, QStatusBar, QLabel, QMessageBox, QMenu, QFileDialog, QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QPushButton, QHBoxLayout, QCheckBox, QTextEdit, QSplitter, QGroupBox, QMenuBar, QToolButton, QSizePolicy, QStyleFactory, QStyledItemDelegate
from PySide6.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon, QAction, QActionGroup
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread, Slot, QRect

from Functions.character_manager import create_character_data, save_character, get_all_characters, get_character_dir, REALM_ICONS, delete_character
from Functions.language_manager import lang, get_available_languages
from Functions.config_manager import config, get_config_dir
from Functions.logging_manager import setup_logging, get_log_dir, get_img_dir

# Setup logging at the very beginning
setup_logging()
if not QDARKSTYLE_AVAILABLE:
    logging.warning("qdarkstyle not found. Dark theme will be unavailable. Run 'pip install qdarkstyle' to enable it.")

# --- Application Constants ---
APP_NAME = "Character Manager"
APP_VERSION = "0.1"

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catches unhandled exceptions and logs them with full traceback."""
    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_string = "".join(tb_lines)
    logging.critical(f"Unhandled exception caught:\n{tb_string}")

class QTextEditHandler(logging.Handler, QObject):
    """A custom logging handler that sends records to a QTextEdit widget."""
    log_updated = Signal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self, parent)

    def emit(self, record):
        msg = self.format(record)
        self.log_updated.emit(msg)

class LogLevelFilter(logging.Filter):
    """Filters log records based on a minimum and maximum level."""
    def __init__(self, min_level, max_level):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record):
        return self.min_level <= record.levelno <= self.max_level

class LogFileReaderThread(QThread):
    """A QThread to monitor a log file without blocking the GUI."""
    new_line = Signal(str)

    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self._is_running = True

    def run(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, 2)  # Go to the end of the file
                while self._is_running:
                    line = f.readline()
                    if line:
                        self.new_line.emit(line)
                    else:
                        self.msleep(100)  # Wait for new lines
        except Exception as e:
            error_message = f"Error monitoring file {self.filepath}: {e}\n"
            self.new_line.emit(error_message)

    def stop(self):
        self._is_running = False

class DebugWindow(QMainWindow):
    """A window that displays log messages."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("debug_window_title"))
        self.setGeometry(100, 100, 1200, 700)
        self.monitoring_thread = None
        self.current_log_level = logging.DEBUG

        # --- Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Menu Bar ---
        self._create_menus()
        
        # --- Button Bar ---
        button_bar_layout = QHBoxLayout()
        test_debug_button = QPushButton(lang.get("test_debug_button"))
        test_debug_button.clicked.connect(self.raise_test_exception)
        button_bar_layout.addWidget(test_debug_button)
        button_bar_layout.addStretch()  # Pushes the button to the left
        main_layout.addLayout(button_bar_layout)

        # --- Main Splitter ---
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # --- Left Pane (Logs & Errors) ---
        left_splitter = QSplitter(Qt.Vertical)
        
        log_group = QGroupBox(lang.get("debug_log_pane_title"))
        log_layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        log_layout.addWidget(self.log_widget)
        log_group.setLayout(log_layout)
        left_splitter.addWidget(log_group)

        error_group = QGroupBox(lang.get("debug_errors_pane_title"))
        error_layout = QVBoxLayout()
        self.error_widget = QTextEdit()
        self.error_widget.setReadOnly(True)
        error_layout.addWidget(self.error_widget)
        error_group.setLayout(error_layout)
        left_splitter.addWidget(error_group)
        
        left_splitter.setSizes([400, 200]) # Initial sizes
        main_splitter.addWidget(left_splitter)

        # --- Right Pane (Log Reader) ---
        reader_group = QGroupBox(lang.get("debug_log_reader_pane_title"))
        reader_layout = QVBoxLayout()
        
        file_bar_layout = QHBoxLayout()
        self.log_file_path_edit = QLineEdit()
        self.log_file_path_edit.setReadOnly(True)
        browse_button = QPushButton(lang.get("browse_button"))
        browse_button.clicked.connect(self.browse_log_file)
        clear_button = QPushButton(lang.get("clear_button_text"))
        clear_button.clicked.connect(self.clear_log_reader)
        file_bar_layout.addWidget(self.log_file_path_edit)
        file_bar_layout.addWidget(browse_button)
        file_bar_layout.addWidget(clear_button)
        reader_layout.addLayout(file_bar_layout)

        self.log_reader_widget = QTextEdit()
        self.log_reader_widget.setReadOnly(True)
        reader_layout.addWidget(self.log_reader_widget)
        reader_group.setLayout(reader_layout)
        main_splitter.addWidget(reader_group)

        main_splitter.setSizes([700, 500])

        # --- Setup Logging Handlers ---
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # General log handler (INFO and below)
        self.log_filter = LogLevelFilter(logging.DEBUG, logging.INFO)
        self.log_handler = QTextEditHandler(self)
        self.log_handler.setFormatter(formatter)
        self.log_handler.addFilter(self.log_filter)
        self.log_handler.log_updated.connect(self.log_widget.append)
        logging.getLogger().addHandler(self.log_handler)

        # Error log handler (WARNING and above)
        self.error_filter = LogLevelFilter(logging.WARNING, logging.CRITICAL)
        self.error_handler = QTextEditHandler(self)
        self.error_handler.setFormatter(formatter)
        self.error_handler.addFilter(self.error_filter)
        self.error_handler.log_updated.connect(self.error_widget.append)
        logging.getLogger().addHandler(self.error_handler)

    def _create_menus(self):
        menu_bar = self.menuBar()

        # --- Level Menu ---
        level_menu = menu_bar.addMenu(lang.get("debug_level_menu"))
        level_action_group = QActionGroup(self)
        level_action_group.setExclusive(True)
        level_action_group.triggered.connect(self.set_log_level)

        log_levels_map = {
            lang.get("debug_level_all"): logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }

        for name, level in log_levels_map.items():
            action = QAction(name, self)
            action.setData(level)
            action.setCheckable(True)
            level_menu.addAction(action)
            level_action_group.addAction(action)
            if level == self.current_log_level:
                action.setChecked(True)

    @Slot(QAction)
    def set_log_level(self, action):
        """Sets the minimum logging level for the handlers."""
        level = action.data()
        self.current_log_level = level
        logging.info(f"Debug window log level set to {logging.getLevelName(level)}")

        # Update filters
        self.log_filter.min_level = level
        self.error_filter.min_level = level
        
        # The handlers will now only receive messages at or above the new level.
        # No need to clear the widgets, as new messages will be filtered.
        
    def raise_test_exception(self):
        """Raises a test exception to verify the handler."""
        logging.info("Raising a test exception...")
        1 / 0

    def browse_log_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, lang.get("debug_log_reader_pane_title"), "", "Log files (*.log);;All files (*.*)")
        if filepath:
            self.log_file_path_edit.setText(filepath)
            self.start_log_monitoring(filepath)

    def clear_log_reader(self):
        self.log_reader_widget.clear()

    def start_log_monitoring(self, filepath):
        self.stop_log_monitoring()
        self.clear_log_reader()
        self.monitoring_thread = LogFileReaderThread(filepath, self)
        self.monitoring_thread.new_line.connect(self.log_reader_widget.append)
        self.monitoring_thread.start()

    def stop_log_monitoring(self):
        if self.monitoring_thread and self.monitoring_thread.isRunning():
            self.monitoring_thread.stop()
            self.monitoring_thread.wait() # Wait for thread to finish

    def closeEvent(self, event):
        """Remove the handler when the window is closed."""
        self.stop_log_monitoring()
        logging.getLogger().removeHandler(self.log_handler)
        logging.getLogger().removeHandler(self.error_handler)
        super().closeEvent(event)

class CharacterSheetWindow(QWidget):
    """Fenêtre pour afficher les détails d'un personnage."""
    def __init__(self, parent, character_data):
        super().__init__(parent)
        self.character_data = character_data
        char_name = self.character_data.get('name', 'N/A')

        self.title(lang.get("character_sheet_title", name=char_name))
        self.geometry("400x500")

        # TODO: PySide Migration
        # layout = QVBoxLayout(self)
        # layout.addWidget(QLabel(f"Feuille pour : {char_name}"))
        # layout.addWidget(QLabel(f"Royaume : {self.character_data.get('realm', 'N/A')}"))
        # layout.addWidget(QLabel(f"Niveau : {self.character_data.get('level', 'N/A')}"))

        # Comportement modal

class NewCharacterDialog(QDialog):
    """A dialog to create a new character with a name and a realm."""
    def __init__(self, parent=None, realms=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("new_char_dialog_title"))

        self.realms = realms if realms else []
        
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        layout.addRow(lang.get("new_char_dialog_prompt"), self.name_edit)

        self.realm_combo = QComboBox(self)
        self.realm_combo.addItems(self.realms)
        layout.addRow(lang.get("new_char_realm_prompt"), self.realm_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        """Returns the entered data if valid."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, lang.get("error_title"), lang.get("char_name_empty_error"))
            return None
        realm = self.realm_combo.currentText()
        return name, realm

class ConfigurationDialog(QDialog):
    """Configuration window for the application."""
    def __init__(self, parent=None, available_languages=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("configuration_window_title"))
        self.setMinimumSize(500, 250)
        self.parent_app = parent
        self.available_languages = available_languages or {}

        layout = QFormLayout(self)

        # Character Path
        self.char_path_edit = QLineEdit()
        browse_char_button = QPushButton(lang.get("browse_button"))
        browse_char_button.clicked.connect(self.browse_character_folder)
        char_path_layout = QHBoxLayout()
        char_path_layout.addWidget(self.char_path_edit)
        char_path_layout.addWidget(browse_char_button)
        layout.addRow(lang.get("config_path_label"), char_path_layout)

        # Config Path
        self.config_path_edit = QLineEdit()
        browse_config_button = QPushButton(lang.get("browse_button"))
        browse_config_button.clicked.connect(self.browse_config_folder)
        config_path_layout = QHBoxLayout()
        config_path_layout.addWidget(self.config_path_edit)
        config_path_layout.addWidget(browse_config_button)
        layout.addRow(lang.get("config_file_path_label"), config_path_layout)

        # Log Path
        self.log_path_edit = QLineEdit()
        browse_log_button = QPushButton(lang.get("browse_button"))
        browse_log_button.clicked.connect(self.browse_log_folder)
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(browse_log_button)
        layout.addRow(lang.get("config_log_path_label"), log_path_layout)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.available_languages.values())
        layout.addRow(lang.get("config_language_label"), self.language_combo)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([lang.get("theme_light"), lang.get("theme_dark")])
        layout.addRow(lang.get("config_theme_label"), self.theme_combo)
        if not QDARKSTYLE_AVAILABLE:
            self.theme_combo.setDisabled(True)
            self.theme_combo.setToolTip(lang.get("qdarkstyle_not_found_tooltip"))


        # Debug Mode
        self.debug_mode_check = QCheckBox(lang.get("config_debug_mode_label"))
        layout.addRow(self.debug_mode_check)

        # Show Debug Window
        self.show_debug_window_check = QCheckBox(lang.get("config_show_debug_window_label"))
        layout.addRow(self.show_debug_window_check)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.update_fields()

    def update_fields(self):
        """Fills the fields with current configuration values."""
        self.char_path_edit.setText(config.get("character_folder", get_character_dir()))
        self.config_path_edit.setText(config.get("config_folder", get_config_dir()))
        self.log_path_edit.setText(config.get("log_folder", get_log_dir()))
        self.debug_mode_check.setChecked(config.get("debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("show_debug_window", False))
        
        current_lang_code = config.get("language", "fr")
        current_lang_name = self.available_languages.get(current_lang_code, "Français")
        self.language_combo.setCurrentText(current_lang_name)

        default_theme = "Dark" if QDARKSTYLE_AVAILABLE else "Light"
        current_theme_value = config.get("theme", default_theme)
        current_theme_text = lang.get("theme_light") if current_theme_value == "Light" else lang.get("theme_dark")
        self.theme_combo.setCurrentText(current_theme_text)

    def browse_folder(self, line_edit, title_key):
        directory = QFileDialog.getExistingDirectory(self, lang.get(title_key))
        if directory:
            line_edit.setText(directory)

    def browse_character_folder(self):
        self.browse_folder(self.char_path_edit, "select_folder_dialog_title")

    def browse_config_folder(self):
        self.browse_folder(self.config_path_edit, "select_config_folder_dialog_title")

    def browse_log_folder(self):
        self.browse_folder(self.log_path_edit, "select_log_folder_dialog_title")

class CenterIconDelegate(QStyledItemDelegate):
    """Delegate personnalisé pour centrer les icônes dans les cellules du TreeView"""
    
    def paint(self, painter, option, index):
        """Dessine l'icône centrée dans la cellule"""
        # Si la cellule contient une icône
        icon = index.data(Qt.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            # Calculer la position centrée
            icon_size = option.decorationSize
            if icon_size.width() == -1:  # Taille par défaut
                icon_size = QSize(16, 16)
            
            # Centrer l'icône dans la cellule
            x = option.rect.x() + (option.rect.width() - icon_size.width()) // 2
            y = option.rect.y() + (option.rect.height() - icon_size.height()) // 2
            
            # Dessiner l'icône
            icon.paint(painter, QRect(x, y, icon_size.width(), icon_size.height()))
        else:
            # Pour les autres cellules, utiliser le comportement par défaut
            super().paint(painter, option, index)

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
        self._create_menus_and_toolbars()

        # --- Main content ---
        # --- Character List (Treeview) ---
        self.character_tree = QTreeView()
        self.character_tree.setAlternatingRowColors(True)
        self.character_tree.setRootIsDecorated(False) # To make it look like a table
        main_layout.addWidget(self.character_tree)

        self.tree_model = QStandardItemModel()
        self.character_tree.setModel(self.tree_model)
        
        # Apply custom delegate to center icons in the realm column (column 0)
        self.center_icon_delegate = CenterIconDelegate(self.character_tree)
        self.character_tree.setItemDelegateForColumn(0, self.center_icon_delegate)

        # --- Bindings ---
        self.character_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.character_tree.customContextMenuRequested.connect(self.on_tree_right_click)
        self.character_tree.doubleClicked.connect(self.on_character_double_click)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Initialisation...")
        self.status_bar.addWidget(self.status_label)

        # Load the character list on application startup
        self.refresh_character_list()

        # Create menus that might need re-translation
        self._create_context_menu()

    def _create_actions(self):
        """Create all QAction objects for the application."""
        self.create_action = QAction(self.add_char_icon, lang.get("create_button_text"), self)
        self.create_action.setToolTip(lang.get("create_char_tooltip"))
        self.create_action.triggered.connect(self.create_new_character)

    def _create_menus_and_toolbars(self):
        """Setup the menu bar and toolbars."""
        # Toolbar
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(self.create_action)

        # Menu Bar
        # We must create a new menu bar and set it to replace the old one on re-translation
        menu_bar = QMenuBar(self)

        # File Menu
        file_menu = menu_bar.addMenu(lang.get("file_menu_label"))
        file_menu.addAction(self.create_action)
        config_action = QAction(lang.get("configuration_menu_label"), self)
        config_action.triggered.connect(self.open_configuration_window)
        file_menu.addAction(config_action)

        file_menu.addSeparator()

        # Help Menu
        help_menu = menu_bar.addMenu(lang.get("help_menu_label", default="?"))
        about_action = QAction(lang.get("about_menu_label"), self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Set the new menu bar as the main window's menu bar
        self.setMenuBar(menu_bar)

    def _create_context_menu(self):
        """Creates or updates the right-click context menu for the tree view."""
        self.context_menu = QMenu(self)
        delete_action = self.context_menu.addAction(lang.get("context_menu_delete"))
        delete_action.triggered.connect(self.delete_selected_character)

    def _load_icons(self):
        """Loads and resizes all required icons once at startup."""
        logging.debug("Pre-loading UI icons.")
        logging.debug(f"REALM_ICONS type: {type(REALM_ICONS)}, content: {REALM_ICONS}, is_empty: {not REALM_ICONS}, bool: {bool(REALM_ICONS)}")
        self.dialog_realm_icons = {}
        self.tree_realm_icons = {}
        self.trash_icon = None
        self.add_char_icon = None
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
                    self.dialog_realm_icons[realm] = icon
                    self.tree_realm_icons[realm] = icon
                    logging.debug(f"Icône créée pour {realm}. isNull: {icon.isNull()}")
                except Exception as e:
                    logging.warning(f"Error loading icon for {realm} at {full_path}: {e}")
                    self.dialog_realm_icons[realm] = None
                    self.tree_realm_icons[realm] = None
            logging.debug("--- Fin de la vérification ---")
            logging.debug(f"Icônes chargées dans tree_realm_icons: {list(self.tree_realm_icons.keys())}")

        # Load trash icon
        try:
            trash_path = os.path.join(img_dir, "bin.png")
            if os.path.exists(trash_path):
                self.trash_icon = QIcon(trash_path)
                logging.debug(f"Trash icon loaded from {trash_path}")
            else:
                logging.error(f"Delete icon 'bin.png' not found at {trash_path}")
        except Exception as e:
            logging.error(f"Error loading trash icon: {e}")

        # Load add character icon
        try:
            add_char_path = os.path.join(img_dir, "icon-plus-50.png")
            if os.path.exists(add_char_path):
                self.add_char_icon = QIcon(add_char_path)
                logging.debug(f"Add character icon loaded from {add_char_path}")
            else:
                logging.error(f"Add character icon 'icon-plus-50.png' not found at {add_char_path}")
        except Exception as e:
            logging.error(f"Error loading add character icon: {e}")
        
        logging.debug(f"Icon loading complete. Realm icons loaded: {len(self.tree_realm_icons)}, Trash icon: {self.trash_icon is not None}, Add icon: {self.add_char_icon is not None}")

    def create_new_character(self):
        """
        Handles the action of creating a new character manually.
        """
        dialog = NewCharacterDialog(self, realms=list(REALM_ICONS.keys()))
        result = dialog.get_data() if dialog.exec() == QDialog.Accepted else None

        if result:
            character_name, realm = result
            character_data = create_character_data(character_name, realm)
            success, response = save_character(character_data)
            if success:
                self.refresh_character_list()
                logging.info(f"Successfully created character '{character_name}'.")
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

        # Set headers
        headers = [lang.get("column_realm"), lang.get("column_name"), lang.get("column_level"), lang.get("column_selection")]
        self.tree_model.setHorizontalHeaderLabels(headers)
        
        # Center align the realm column header
        realm_header = self.tree_model.horizontalHeaderItem(0)
        if realm_header:
            realm_header.setTextAlignment(Qt.AlignCenter)

        characters = get_all_characters()
        # Add a detailed log to check the state of the icons dictionary just before the loop
        logging.debug(f"Populating tree with {len(characters)} character(s). tree_realm_icons contains {len(self.tree_realm_icons)} icon(s): {list(self.tree_realm_icons.keys())}")

        for i, char in enumerate(characters):
            realm_name = char.get('realm', 'N/A')
            realm_icon = self.tree_realm_icons.get(realm_name)
            char_id = char.get('id')
            self.characters_by_id[char_id] = char

            logging.debug(f"Character {i+1}/{len(characters)}: '{char.get('name')}' (realm='{realm_name}') - icon found: {realm_icon is not None}, isNull: {realm_icon.isNull() if realm_icon else 'N/A'}")
            # Create items for each column in the row
            item_realm = QStandardItem() # On ne met que l'icône, pas de texte.
            if realm_icon:
                item_realm.setIcon(realm_icon)
            item_realm.setData(char_id, Qt.UserRole) # Store char_id in the item
            item_realm.setTextAlignment(Qt.AlignCenter) # Centrer l'icône
            item_realm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Make non-editable

            item_name = QStandardItem(char.get('name', 'N/A'))
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Make non-editable
            item_level = QStandardItem(str(char.get('level', 1)))
            item_level.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Make non-editable
            
            item_selection = QStandardItem()
            item_selection.setCheckable(True)
            item_selection.setCheckState(Qt.Unchecked)
            # Allow checking but not direct text editing
            item_selection.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)

            row_items = [item_realm, item_name, item_level, item_selection]
            self.tree_model.appendRow(row_items)

        self.character_tree.resizeColumnToContents(0)
        self.character_tree.resizeColumnToContents(2)
        self.character_tree.resizeColumnToContents(3)
        self.character_tree.header().setStretchLastSection(False)
        self.character_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)

    def on_tree_right_click(self, position):
        """Shows a context menu on right-click."""
        index = self.character_tree.indexAt(position)
        if index.isValid():
            self.context_menu.exec_(self.character_tree.viewport().mapToGlobal(position))

    def delete_selected_character(self):
        """Deletes the character currently selected in the treeview."""
        indexes = self.character_tree.selectedIndexes()
        if indexes:
            # Get the item from the first column of the selected row
            row = indexes[0].row()
            first_column_item = self.tree_model.item(row, 0)
            char_id = first_column_item.data(Qt.UserRole) # Retrieve the stored character ID
            if char_id:
                self.delete_character(char_id)

    def get_checked_character_ids(self):
        """Returns a list of character IDs for all checked rows."""
        checked_ids = []
        for row in range(self.tree_model.rowCount()):
            # The checkbox is in the last column (index 3)
            selection_item = self.tree_model.item(row, 3)
            if selection_item and selection_item.checkState() == Qt.Checked:
                # The ID is stored in the first item of the row (index 0)
                id_item = self.tree_model.item(row, 0)
                char_id = id_item.data(Qt.UserRole)
                if char_id:
                    checked_ids.append(char_id)
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
            for char_id in checked_ids:
                # We skip the individual confirmation dialog by directly calling the backend function
                self.delete_character(char_id, confirm=False)
            self.refresh_character_list()

    def delete_character(self, char_id, confirm=True):
        """Handles the character deletion process."""
        char_data = self.characters_by_id.get(str(char_id))
        if not char_data:
            logging.warning(f"Attempted to delete character with unknown ID: {char_id}")
            return

        reply = QMessageBox.Yes
        if confirm:
            char_name = char_data.get('name', 'N/A')
            reply = QMessageBox.question(self,
                                         lang.get("delete_char_confirm_title"),
                                         lang.get("delete_char_confirm_message", name=char_name),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

        if reply == QMessageBox.Yes:
            char_name = char_data.get('name', 'N/A')
            char_realm = char_data.get('realm')
            success, msg = delete_character(char_id, char_realm, character_name=char_name)
            if success:
                logging.info(f"Character '{char_name}' (ID: {char_id}) deleted by user.")
                if confirm: # Refresh only if it's a single delete action
                    self.refresh_character_list()
            else:
                logging.error(f"Failed to delete character '{char_name}': {msg}")
                QMessageBox.critical(self, lang.get("error_title"), msg)

    def on_character_double_click(self, index): # Renamed from delete_character_by_id
        """Gère le double-clic sur un personnage dans la liste."""
        if not index.isValid():
            return

        # Prevent sheet from opening when clicking the checkbox column (index 3)
        if index.column() == 3:
            return

        # Get the item from the first column to retrieve the ID
        item = self.tree_model.item(index.row(), 0)
        char_id = item.data(Qt.UserRole)

        character_data = self.characters_by_id.get(char_id)
        if character_data:
            char_name = character_data.get('name', 'N/A')
            logging.info(f"Ouverture de la feuille du personnage '{char_name}'.")
            # TODO: PySide Migration: CharacterSheetWindow needs to be a QDialog
            # sheet = CharacterSheetWindow(self, character_data)
            # sheet.show()
        else:
            logging.warning(f"Impossible de trouver les données pour le personnage avec l'ID '{char_id}' lors du double-clic.")

    def change_language(self, lang_code):
        """Changes the application language and updates the UI."""
        logging.info(f"Changing language to {lang_code}.")
        config.set("language", lang_code)
        lang.set_language(lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Updates the text of all UI widgets."""
        self.setWindowTitle(lang.get("window_title"))
        self._load_icons() # Reload icons as part of UI retranslation
        self._create_actions()
        self._create_menus_and_toolbars()
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
        """Displays the 'About' dialog box."""
        title = lang.get("about_message_title", app_name=APP_NAME)
        message = lang.get(
            "about_message_content",
            version=APP_VERSION
        )
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

    def open_configuration_window(self):
        """Opens the configuration window."""
        logging.debug("Opening configuration window.")
        dialog = ConfigurationDialog(self, self.available_languages)
        if dialog.exec() == QDialog.Accepted:
            self.save_configuration(dialog)

    def save_configuration(self, dialog):
        """Saves the configuration and closes the window."""
        old_theme = config.get("theme", "Dark")
        old_debug_mode = config.get("debug_mode", False)
        new_debug_mode = dialog.debug_mode_check.isChecked()

        if not new_debug_mode and old_debug_mode:
            logging.info("Debug mode has been DEACTIVATED. This is the last log entry.")

        config.set("character_folder", dialog.char_path_edit.text())
        config.set("config_folder", dialog.config_path_edit.text())
        config.set("log_folder", dialog.log_path_edit.text())
        config.set("debug_mode", new_debug_mode)
        config.set("show_debug_window", dialog.show_debug_window_check.isChecked())

        selected_lang_name = dialog.language_combo.currentText()
        new_lang_code = None
        for code, name in self.available_languages.items():
            if name == selected_lang_name:
                new_lang_code = code
                break
        
        language_changed = new_lang_code and new_lang_code != config.get("language")
        if language_changed:
            config.set("language", new_lang_code)

        selected_theme_name = dialog.theme_combo.currentText()
        new_theme = "Dark" if selected_theme_name == lang.get("theme_dark") else "Light"
        theme_changed = new_theme != old_theme
        if theme_changed:
            config.set("theme", new_theme)


        setup_logging()

        if new_debug_mode and not old_debug_mode:
            logging.info("Debug mode has been ACTIVATED.")

        QMessageBox.information(self, lang.get("success_title"), lang.get("config_saved_success"))

        if language_changed:
            self.change_language(new_lang_code)
        
        if theme_changed:
            QMessageBox.information(self, lang.get("info_title"), lang.get("theme_change_restart_message"))

    def closeEvent(self, event):
        """Ensures all child windows are closed when the main window is closed."""
        logging.info("Main window closing. Shutting down application.")
        if self.debug_window:
            self.debug_window.close()
        super().closeEvent(event)


def apply_theme(app):
    """Applies the configured theme to the application."""
    # Default to 'Dark' if available, otherwise 'Light'
    default_theme = "Dark" if QDARKSTYLE_AVAILABLE else "Light"
    theme = config.get("theme", default_theme)

    if theme == "Dark" and QDARKSTYLE_AVAILABLE:
        logging.info("Applying Dark theme using 'qdarkstyle' library.")
        app.setStyleSheet(qdarkstyle.load_stylesheet()) # type: ignore
    else: # Fallback to light theme
        # Clear any previous stylesheet (like from the dark theme)
        app.setStyleSheet("")
        # Try to apply a native Windows look
        if "windowsvista" in QStyleFactory.keys():
            logging.info("Applying 'windowsvista' style for a native Windows look.")
            app.setStyle("windowsvista")
        else:
            logging.info("Applying Light theme (default system style).")
        if theme == "Dark" and not QDARKSTYLE_AVAILABLE:
            logging.warning("Dark theme selected but 'qdarkstyle' is not installed. Falling back to Light theme.")

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