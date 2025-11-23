"""
Modern Settings Dialog with Navigation Sidebar
Separated from dialogs.py for better maintainability
"""

import os
import logging
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QDialogButtonBox,
    QFileDialog, QListWidget, QStackedWidget, QWidget, QListWidgetItem,
    QFrame, QMessageBox, QProgressDialog, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir, ConfigManager
from Functions.character_manager import get_character_dir
from Functions.path_manager import PathManager
from Functions.logging_manager import get_log_dir
from Functions.path_manager import get_armor_dir, path_manager
from Functions.backup_manager import BackupManager


class SettingsDialog(QDialog):
    """
    Modern settings dialog with sidebar navigation and stacked pages.
    
    Architecture:
    - Left: Navigation list (QListWidget) with icons
    - Right: Content pages (QStackedWidget)
    - Bottom: Action buttons (Save, Cancel)
    """
    
    def __init__(self, parent=None, available_languages=None, available_seasons=None, 
                 available_servers=None, available_realms=None):
        super().__init__(parent)
        self.parent_app = parent
        self.available_languages = available_languages or {}
        self.available_seasons = available_seasons or []
        self.available_servers = available_servers or []
        self.available_realms = available_realms or []
        
        self.setWindowTitle(lang.get("configuration_window_title"))
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        
        # Enable window resizing with maximize button
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setSizeGripEnabled(True)  # Add resize grip in bottom-right corner
        
        # Make window non-modal (don't block main application)
        self.setModal(False)
        
        # Initialize managers for armory operations
        self.config_manager = ConfigManager()
        self.path_manager = PathManager()
        from Functions.items_database_manager import ItemsDatabaseManager
        self.db_manager = ItemsDatabaseManager(self.config_manager, self.path_manager)
        
        self._init_ui()
        self._load_settings()
        
    def _init_ui(self):
        """Initialize the UI layout with navigation and content areas"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content area (navigation + pages)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # === RIGHT SIDE: Content Pages (create first) ===
        self.pages = QStackedWidget()
        self.pages.setContentsMargins(20, 20, 20, 20)
        
        # Create all pages
        self._create_general_page()
        self._create_themes_page()
        self._create_startup_page()
        self._create_columns_page()
        self._create_herald_page()
        self._create_backup_page()
        self._create_armory_page()
        self._create_debug_page()
        
        # SuperAdmin page (only in --admin mode) - AFTER Debug to keep indexes consistent
        from main import ADMIN_MODE
        if ADMIN_MODE:
            self._create_superadmin_page()
        
        # === LEFT SIDE: Navigation (create after pages) ===
        self.navigation = self._create_navigation()
        content_layout.addWidget(self.navigation)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        content_layout.addWidget(separator)
        
        content_layout.addWidget(self.pages, 1)  # Stretch factor 1 for pages
        
        main_layout.addLayout(content_layout, 1)
        
        # === BOTTOM: Action Buttons ===
        button_box = QDialogButtonBox()
        
        # Add custom buttons in order: Save, Cancel, Close
        save_button = button_box.addButton(lang.get("save_button", default="Sauvegarder"), QDialogButtonBox.ActionRole)
        cancel_button = button_box.addButton(lang.get("cancel_button", default="Annuler"), QDialogButtonBox.ActionRole)
        close_button = button_box.addButton(lang.get("close_button", default="Fermer"), QDialogButtonBox.ActionRole)
        
        # Connect signals
        save_button.clicked.connect(self._save_without_closing)
        cancel_button.clicked.connect(self._cancel_changes)
        close_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.addWidget(button_box)
        main_layout.addLayout(button_layout)
        
    def _create_navigation(self):
        """Create the left sidebar navigation"""
        nav_widget = QListWidget()
        nav_widget.setFixedWidth(200)
        nav_widget.setSpacing(2)
        nav_widget.setIconSize(QSize(20, 20))
        
        # Navigation items with icons
        nav_items = [
            ("📁", lang.get("settings.navigation.general", default="Général")),
            ("🎨", lang.get("settings.navigation.themes", default="Thèmes")),
            ("🚀", lang.get("settings.navigation.startup", default="Démarrage")),
            ("🏛️", lang.get("settings.navigation.columns", default="Colonnes")),
            ("🌐", lang.get("settings.navigation.herald", default="Eden")),
            ("💾", lang.get("settings.navigation.backup", default="Sauvegardes")),
            ("🛡️", lang.get("settings.navigation.armory", default="Armurerie")),
        ]
        
        nav_items.append(("🐛", lang.get("settings.navigation.debug", default="Debug")))
        
        # Add SuperAdmin page conditionally (at the bottom)
        from main import ADMIN_MODE
        if ADMIN_MODE:
            nav_items.append(("🔧", lang.get("settings.navigation.superadmin", default="SuperAdmin")))
        
        for icon, text in nav_items:
            item = QListWidgetItem(f"{icon}  {text}")
            # Make text slightly larger and bold when selected
            font = item.font()
            font.setPointSize(font.pointSize() + 1)
            item.setFont(font)
            nav_widget.addItem(item)
        
        # Connect navigation to page change
        nav_widget.currentRowChanged.connect(self.pages.setCurrentIndex)
        
        # Select first item by default
        nav_widget.setCurrentRow(0)
        
        return nav_widget
        
    def _create_general_page(self):
        """Page 1: General Settings (Paths + Defaults)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_general_title", default="Paramètres Généraux"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(lang.get("settings_general_subtitle", 
                                  default="Chemins des dossiers et valeurs par défaut"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === Paths Group ===
        paths_group = QGroupBox("📁 " + lang.get("config_paths_group_title", 
                                                  default="Chemins des dossiers"))
        paths_layout = QFormLayout()
        
        # Character Path
        self.char_path_edit = QLineEdit()
        browse_char_button = QPushButton(lang.get("browse_button"))
        browse_char_button.clicked.connect(self._browse_character_folder)
        move_char_button = QPushButton("📦 " + lang.get("move_folder_button", default="Déplacer"))
        move_char_button.clicked.connect(lambda: self._move_folder(self.char_path_edit, "character_folder", lang.get("config_path_label")))
        move_char_button.setToolTip(lang.get("move_folder_tooltip", default="Déplacer le dossier et son contenu vers un nouvel emplacement"))
        open_char_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
        open_char_folder_button.clicked.connect(self._open_character_folder)
        char_path_layout = QHBoxLayout()
        char_path_layout.addWidget(self.char_path_edit)
        char_path_layout.addWidget(browse_char_button)
        char_path_layout.addWidget(move_char_button)
        char_path_layout.addWidget(open_char_folder_button)
        paths_layout.addRow(lang.get("config_path_label"), char_path_layout)
        
        # Note: Config folder path is NOT configurable - it must always be next to the executable
        # This avoids circular dependency issues with config.json location
        
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        
        # === Default Values Group ===
        defaults_group = QGroupBox("⚙️ " + lang.get("config_defaults_group_title", 
                                                     default="Valeurs par défaut"))
        defaults_layout = QFormLayout()
        
        # Default Server
        self.default_server_combo = QComboBox()
        self.default_server_combo.addItems(self.available_servers)
        defaults_layout.addRow(lang.get("config_default_server_label"), 
                              self.default_server_combo)
        
        # Default Season
        self.default_season_combo = QComboBox()
        self.default_season_combo.addItems(self.available_seasons)
        defaults_layout.addRow(lang.get("config_default_season_label"), 
                              self.default_season_combo)
        
        # Default Realm
        self.default_realm_combo = QComboBox()
        self.default_realm_combo.addItems(self.available_realms)
        defaults_layout.addRow(lang.get("config_default_realm_label"), 
                              self.default_realm_combo)
        
        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)
        
        # === Language Selection ===
        language_group = QGroupBox("🌍 " + lang.get("config_language_group_title", 
                                                    default="Langue de l'application"))
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.available_languages.values())
        language_layout.addRow(lang.get("config_language_label"), self.language_combo)
        
        language_group.setLayout(language_layout)
        layout.addWidget(language_group)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_themes_page(self):
        """Page 2: Themes & Display"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_themes_title", default="Thèmes & Affichage"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get("settings_themes_subtitle", 
                                  default="Personnalisation de l'interface"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === Theme Selection ===
        theme_group = QGroupBox("🎨 " + lang.get("config_theme_group_title", 
                                                  default="Sélection du thème"))
        theme_layout = QFormLayout()
        
        from Functions.theme_manager import get_available_themes
        self.theme_combo = QComboBox()
        self.available_themes = get_available_themes()
        sorted_themes = sorted(self.available_themes.items(), key=lambda x: x[1])
        for theme_id, theme_name in sorted_themes:
            self.theme_combo.addItem(theme_name, theme_id)
        theme_layout.addRow(lang.get("config_theme_label"), self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # === Font Scale ===
        font_group = QGroupBox("🔤 " + lang.get("config_font_group_title", 
                                                 default="Taille du texte"))
        font_layout = QFormLayout()
        
        self.font_scale_combo = QComboBox()
        self.font_scale_values = [1.0, 1.25, 1.5, 1.75, 2.0]
        for scale in self.font_scale_values:
            self.font_scale_combo.addItem(f"{int(scale * 100)}%", scale)
        font_layout.addRow(lang.get("config_font_scale_label"), self.font_scale_combo)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_startup_page(self):
        """Page 3: Startup Settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_startup_title", default="Démarrage"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get("settings_startup_subtitle", 
                                  default="Options de démarrage de l'application"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === Startup Options ===
        startup_group = QGroupBox("🚀 " + lang.get("config_startup_group_title", 
                                                    default="Options de démarrage"))
        startup_layout = QVBoxLayout()
        
        self.disable_disclaimer_check = QCheckBox(
            lang.get("config_disable_disclaimer_label", 
                    default="Désactiver le message d'avertissement au démarrage")
        )
        self.disable_disclaimer_check.setToolTip(
            "Si activé, le message d'avertissement concernant le scraping ne s'affichera plus au démarrage."
        )
        startup_layout.addWidget(self.disable_disclaimer_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Info about startup
        info_label = QLabel(
            "💡 " + lang.get("settings_startup_info",
                           default="Le message d'avertissement rappelle que le scraping du Herald Eden "
                                  "doit être fait de manière raisonnable.\n\n"
                                  "Il est recommandé de garder ce message activé.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: palette(alternate-base); padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_columns_page(self):
        """Page 4: Columns Configuration"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_columns_title", default="Colonnes"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get("settings_columns_subtitle", 
                                  default="Configuration de l'affichage des colonnes"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === Column Resize Mode ===
        resize_group = QGroupBox("🔄 " + lang.get("config_column_resize_group_title", 
                                                   default="Mode de redimensionnement"))
        resize_layout = QVBoxLayout()
        
        self.manual_column_resize_check = QCheckBox(
            lang.get("config_manual_column_resize_label", 
                    default="Gestion manuelle de la taille des colonnes")
        )
        self.manual_column_resize_check.setToolTip(
            "Si activé, vous pouvez redimensionner manuellement les colonnes.\n"
            "Les largeurs seront sauvegardées automatiquement."
        )
        resize_layout.addWidget(self.manual_column_resize_check)
        
        resize_group.setLayout(resize_layout)
        layout.addWidget(resize_group)
        
        # === Column Visibility ===
        visibility_group = QGroupBox("👁️ " + lang.get("config_column_visibility_group_title", 
                                                       default="Visibilité des colonnes"))
        visibility_layout = QVBoxLayout()
        
        # Import column configuration
        from UI.dialogs import ColumnsConfigDialog
        
        # Create checkboxes for each column
        self.column_checkboxes = {}
        visibility_config = config.get("ui.column_visibility", {})
        
        for col in ColumnsConfigDialog.COLUMNS_CONFIG:
            checkbox = QCheckBox(lang.get(col["name_key"], default=col["key"]))
            is_visible = visibility_config.get(col["key"], col["default"])
            checkbox.setChecked(is_visible)
            self.column_checkboxes[col["key"]] = checkbox
            visibility_layout.addWidget(checkbox)
        
        visibility_group.setLayout(visibility_layout)
        layout.addWidget(visibility_group)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_herald_page(self):
        """Page 3: Eden Settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_herald_title", default="Eden"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get("settings_herald_subtitle", 
                                  default="Configuration de la connexion au Herald"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === Cookies Path (Eden AppData) ===
        cookies_group = QGroupBox("🍪 " + lang.get("config_cookies_group_title", 
                                                    default="Chemin des cookies"))
        cookies_layout = QVBoxLayout()
        
        # Info label
        from Functions.path_manager import get_eden_data_dir
        eden_path = get_eden_data_dir()
        cookies_info = QLabel(lang.get("eden_storage_info", default="Stockage automatique dans") + f": {eden_path}")
        cookies_info.setWordWrap(True)
        cookies_info.setStyleSheet("color: gray; font-size: 9pt; padding: 5px;")
        cookies_layout.addWidget(cookies_info)
        
        # Buttons layout (horizontal)
        buttons_layout = QHBoxLayout()
        
        # Open folder button
        open_cookies_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
        open_cookies_folder_button.clicked.connect(self._open_cookies_folder)
        buttons_layout.addWidget(open_cookies_folder_button)
        
        # Clean Eden button
        clean_eden_button = QPushButton("🗑️ " + lang.get("clean_eden_button", default="Nettoyer Eden"))
        clean_eden_button.clicked.connect(self._clean_eden_folder)
        clean_eden_button.setToolTip(lang.get("clean_eden_tooltip", default="Supprime tous les cookies et fichiers temporaires du profil Chrome"))
        clean_eden_button.setStyleSheet("""
            QPushButton {
                background-color: #D83B01;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #A52A00;
            }
        """)
        buttons_layout.addWidget(clean_eden_button)
        
        cookies_layout.addLayout(buttons_layout)
        
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)
        
        # === Item Cache Path ===
        cache_group = QGroupBox("💾 " + lang.get("config_item_cache_group_title", 
                                                    default="Chemin du cache des items"))
        cache_layout = QVBoxLayout()
        
        # Info label
        import os
        user_profile = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
        if user_profile:
            cache_path = os.path.join(user_profile, 'DAOC_Character_Manager', 'ItemCache')
        else:
            from pathlib import Path
            cache_path = str(Path(__file__).parent.parent / 'Armory')
        
        cache_info = QLabel(lang.get("item_cache_storage_info", default="Stockage automatique dans") + f": {cache_path}")
        cache_info.setWordWrap(True)
        cache_info.setStyleSheet("color: gray; font-size: 9pt; padding: 5px;")
        cache_layout.addWidget(cache_info)
        
        # Buttons layout (horizontal)
        cache_buttons_layout = QHBoxLayout()
        
        # Open folder button
        open_cache_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
        open_cache_folder_button.clicked.connect(self._open_item_cache_folder)
        cache_buttons_layout.addWidget(open_cache_folder_button)
        
        # Clean cache button
        clean_cache_button = QPushButton("🗑️ " + lang.get("clean_cache_button", default="Nettoyer le cache"))
        clean_cache_button.clicked.connect(self._clean_item_cache)
        clean_cache_button.setToolTip(lang.get("clean_cache_tooltip", default="Supprime le cache des items trouvés via recherche web"))
        clean_cache_button.setStyleSheet("""
            QPushButton {
                background-color: #D83B01;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #A52A00;
            }
        """)
        cache_buttons_layout.addWidget(clean_cache_button)
        
        cache_layout.addLayout(cache_buttons_layout)
        
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        # === Browser Settings ===
        browser_group = QGroupBox("🌐 " + lang.get("config_browser_group_title", 
                                                    default="Navigateur"))
        browser_layout = QFormLayout()
        
        from Functions.cookie_manager import CookieManager
        cookie_manager = CookieManager()
        available_browsers = cookie_manager.detect_available_browsers()
        
        self.browser_combo = QComboBox()
        all_browsers = ['Chrome', 'Edge', 'Firefox']
        self.browser_combo.addItems(all_browsers)
        
        if available_browsers:
            tooltip = f"Navigateurs détectés: {', '.join(available_browsers)}"
        else:
            tooltip = "Aucun navigateur détecté"
        self.browser_combo.setToolTip(tooltip)
        
        browser_layout.addRow(lang.get("config_preferred_browser_label", 
                                      default="Navigateur préféré:"), 
                             self.browser_combo)
        
        self.allow_browser_download_check = QCheckBox(
            lang.get("config_allow_browser_download_label",
                    default="Autoriser le téléchargement automatique de drivers")
        )
        self.allow_browser_download_check.setToolTip(
            "Si activé, télécharge automatiquement le driver si le navigateur n'est pas trouvé.\n"
            "Nécessite une connexion Internet."
        )
        browser_layout.addRow(self.allow_browser_download_check)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_backup_page(self):
        """Page 6: Backup Settings"""
        from Functions.backup_manager import get_backup_manager, BackupManager
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_backup_title", default="Sauvegardes"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get("settings_backup_subtitle", 
                                  default="Configuration des sauvegardes automatiques"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # Initialize backup manager
        self.backup_manager = get_backup_manager(config)
        if self.backup_manager is None:
            self.backup_manager = BackupManager(config)
        
        backup_info = self.backup_manager.get_backup_info()
        
        # === CHARACTERS BACKUP ===
        chars_group = QGroupBox("📁 " + lang.get("backup_characters_title", default="Sauvegardes des personnages"))
        chars_layout = QVBoxLayout()
        
        # Enabled checkbox and compress checkbox side by side
        enable_compress_layout = QHBoxLayout()
        
        self.backup_enabled_check = QCheckBox(lang.get("backup_enabled_label", default="Activer les sauvegardes"))
        self.backup_enabled_check.setChecked(config.get("backup.characters.auto_daily_backup", True))
        self.backup_enabled_check.stateChanged.connect(lambda state: self._save_backup_setting("backup_enabled", state == 2))
        enable_compress_layout.addWidget(self.backup_enabled_check)
        
        enable_compress_layout.addSpacing(30)
        
        self.backup_compress_check = QCheckBox(lang.get("backup_compress_label", default="Compresser les sauvegardes (ZIP)"))
        self.backup_compress_check.setChecked(config.get("backup.characters.compress", True))
        self.backup_compress_check.setToolTip(lang.get("backup_compress_tooltip", default="Réduit la taille des sauvegardes"))
        self.backup_compress_check.stateChanged.connect(lambda state: self._save_backup_setting("backup_compress", state == 2))
        enable_compress_layout.addWidget(self.backup_compress_check)
        
        enable_compress_layout.addSpacing(30)
        
        # Auto-delete checkbox
        self.backup_auto_delete_check = QCheckBox(lang.get("backup_auto_delete_label", default="Supprimer auto les anciens"))
        self.backup_auto_delete_check.setChecked(config.get("backup.characters.auto_delete_old", True))
        self.backup_auto_delete_check.setToolTip(lang.get("backup_auto_delete_tooltip", default="Supprime automatiquement les plus anciens backups quand la limite est atteinte"))
        self.backup_auto_delete_check.stateChanged.connect(self._on_backup_auto_delete_changed)
        enable_compress_layout.addWidget(self.backup_auto_delete_check)
        
        enable_compress_layout.addStretch()
        chars_layout.addLayout(enable_compress_layout)
        chars_layout.addSpacing(10)
        
        # Backup path
        path_form = QFormLayout()
        self.backup_path_edit = QLineEdit()
        backup_path = config.get("backup.characters.path")
        if not backup_path:
            from Functions.path_manager import get_base_path
            backup_path = os.path.join(get_base_path(), "Backup", "Characters")
        self.backup_path_edit.setText(backup_path)
        self.backup_path_edit.setReadOnly(True)
        self.backup_path_edit.setCursorPosition(0)
        
        browse_backup_button = QPushButton(lang.get("browse_button", default="Parcourir..."))
        browse_backup_button.clicked.connect(self._browse_backup_path)
        browse_backup_button.setMaximumWidth(100)
        
        move_backup_button = QPushButton("📦 " + lang.get("move_folder_button", default="D\u00e9placer"))
        move_backup_button.clicked.connect(lambda: self._move_folder(self.backup_path_edit, "backup_path", lang.get("backup_path_label", default="Dossier de sauvegarde")))
        move_backup_button.setToolTip(lang.get("move_folder_tooltip", default="D\u00e9placer le dossier et son contenu vers un nouvel emplacement"))
        
        open_backup_folder_button = QPushButton("📂 " + lang.get("backup_open_folder", default="Ouvrir le dossier"))
        open_backup_folder_button.clicked.connect(self._open_backup_folder)
        
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_path_edit)
        backup_path_layout.addWidget(browse_backup_button)
        backup_path_layout.addWidget(move_backup_button)
        backup_path_layout.addWidget(open_backup_folder_button)
        path_form.addRow(lang.get("backup_path_label", default="Dossier de sauvegarde") + " :", backup_path_layout)
        chars_layout.addLayout(path_form)
        chars_layout.addSpacing(10)
        
        # Storage limit + Stats on same line with separator
        stats_layout = QHBoxLayout()
        
        # Storage limit
        stats_layout.addWidget(QLabel(lang.get("backup_size_limit_label", default="Limite de stockage") + " :"))
        self.backup_size_limit_edit = QLineEdit()
        self.backup_size_limit_edit.setText(str(config.get("backup.characters.size_limit_mb", 20)))
        self.backup_size_limit_edit.setMaximumWidth(60)
        self.backup_size_limit_edit.textChanged.connect(self._on_backup_limit_changed)
        stats_layout.addWidget(self.backup_size_limit_edit)
        stats_layout.addWidget(QLabel("MB"))
        stats_layout.addWidget(QLabel(lang.get("backup_size_limit_tooltip", default="(-1 = illimité)")))
        stats_layout.addSpacing(15)
        
        # Vertical separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("color: #888888;")
        stats_layout.addWidget(separator1)
        stats_layout.addSpacing(10)
        
        # Total backups
        total_backups = len(backup_info["backups"])
        stats_layout.addWidget(QLabel(lang.get("backup_total_label", default="Nombre de sauvegardes") + " :"))
        self.backup_total_label = QLabel(f"{total_backups}")
        self.backup_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        stats_layout.addWidget(self.backup_total_label)
        stats_layout.addSpacing(10)
        
        # Vertical separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("color: #888888;")
        stats_layout.addWidget(separator2)
        stats_layout.addSpacing(10)
        
        # Last backup date
        last_backup_date = config.get("backup.characters.last_date")
        if last_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_backup_date)
                last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_backup_str = "N/A"
        else:
            last_backup_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
        stats_layout.addWidget(QLabel(lang.get("backup_last_label", default="Dernière sauvegarde") + " :"))
        self.backup_last_label = QLabel(last_backup_str)
        self.backup_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        stats_layout.addWidget(self.backup_last_label)
        stats_layout.addSpacing(15)
        
        # Vertical separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.VLine)
        separator3.setFrameShadow(QFrame.Sunken)
        separator3.setStyleSheet("color: #888888;")
        stats_layout.addWidget(separator3)
        stats_layout.addSpacing(10)
        
        # Manual backup button
        backup_now_button = QPushButton("💾 " + lang.get("backup_now_button", default="Sauvegarder maintenant"))
        backup_now_button.clicked.connect(self._backup_characters_now)
        backup_now_button.setToolTip(lang.get("backup_now_tooltip", default="Créer une sauvegarde manuelle immédiate"))
        backup_now_button.setMaximumWidth(200)
        stats_layout.addWidget(backup_now_button)
        
        stats_layout.addStretch()
        chars_layout.addLayout(stats_layout)
        chars_layout.addSpacing(15)
        
        chars_group.setLayout(chars_layout)
        layout.addWidget(chars_group)
        
        # === COOKIES BACKUP ===
        cookies_info = self.backup_manager.get_cookies_backup_info()
        cookies_group = QGroupBox("🍪 " + lang.get("backup_cookies_title", default="Sauvegardes des cookies Eden"))
        cookies_layout = QVBoxLayout()
        
        # Enabled checkbox and compress checkbox side by side
        cookies_enable_compress_layout = QHBoxLayout()
        
        self.cookies_backup_enabled_check = QCheckBox(lang.get("backup_enabled_label", default="Activer les sauvegardes"))
        self.cookies_backup_enabled_check.setChecked(config.get("backup.cookies.auto_daily_backup", True))
        self.cookies_backup_enabled_check.stateChanged.connect(lambda state: self._save_backup_setting("cookies_backup_enabled", state == 2))
        cookies_enable_compress_layout.addWidget(self.cookies_backup_enabled_check)
        
        cookies_enable_compress_layout.addSpacing(30)
        
        self.cookies_backup_compress_check = QCheckBox(lang.get("backup_compress_label", default="Compresser les sauvegardes (ZIP)"))
        self.cookies_backup_compress_check.setChecked(config.get("backup.cookies.compress", True))
        self.cookies_backup_compress_check.setToolTip(lang.get("backup_compress_tooltip", default="Réduit la taille des sauvegardes"))
        self.cookies_backup_compress_check.stateChanged.connect(lambda state: self._save_backup_setting("cookies_backup_compress", state == 2))
        cookies_enable_compress_layout.addWidget(self.cookies_backup_compress_check)
        
        cookies_enable_compress_layout.addSpacing(30)
        
        # Auto-delete checkbox for cookies
        self.cookies_backup_auto_delete_check = QCheckBox(lang.get("backup_auto_delete_label", default="Supprimer auto les anciens"))
        self.cookies_backup_auto_delete_check.setChecked(config.get("backup.cookies.auto_delete_old", True))
        self.cookies_backup_auto_delete_check.setToolTip(lang.get("backup_auto_delete_tooltip", default="Supprime automatiquement les plus anciens backups quand la limite est atteinte"))
        self.cookies_backup_auto_delete_check.stateChanged.connect(self._on_cookies_auto_delete_changed)
        cookies_enable_compress_layout.addWidget(self.cookies_backup_auto_delete_check)
        
        cookies_enable_compress_layout.addStretch()
        cookies_layout.addLayout(cookies_enable_compress_layout)
        cookies_layout.addSpacing(10)
        
        # Cookies backup path
        cookies_path_form = QFormLayout()
        self.cookies_backup_path_edit = QLineEdit()
        cookies_backup_path = config.get("backup.cookies.path")
        if not cookies_backup_path:
            from Functions.path_manager import get_base_path
            cookies_backup_path = os.path.join(get_base_path(), "Backup", "Cookies")
        self.cookies_backup_path_edit.setText(cookies_backup_path)
        self.cookies_backup_path_edit.setReadOnly(True)
        self.cookies_backup_path_edit.setCursorPosition(0)
        
        browse_cookies_button = QPushButton(lang.get("browse_button", default="Parcourir..."))
        browse_cookies_button.clicked.connect(self._browse_cookies_backup_path)
        browse_cookies_button.setMaximumWidth(100)
        
        move_cookies_backup_button = QPushButton("📦 " + lang.get("move_folder_button", default="D\u00e9placer"))
        move_cookies_backup_button.clicked.connect(lambda: self._move_folder(self.cookies_backup_path_edit, "cookies_backup_path", lang.get("backup_path_label", default="Dossier de sauvegarde")))
        move_cookies_backup_button.setToolTip(lang.get("move_folder_tooltip", default="D\u00e9placer le dossier et son contenu vers un nouvel emplacement"))
        
        open_cookies_backup_folder_button = QPushButton("📂 " + lang.get("backup_open_folder", default="Ouvrir le dossier"))
        open_cookies_backup_folder_button.clicked.connect(self._open_cookies_backup_folder)
        
        cookies_path_layout = QHBoxLayout()
        cookies_path_layout.addWidget(self.cookies_backup_path_edit)
        cookies_path_layout.addWidget(browse_cookies_button)
        cookies_path_layout.addWidget(move_cookies_backup_button)
        cookies_path_layout.addWidget(open_cookies_backup_folder_button)
        cookies_path_form.addRow(lang.get("backup_path_label", default="Dossier de sauvegarde") + " :", cookies_path_layout)
        cookies_layout.addLayout(cookies_path_form)
        cookies_layout.addSpacing(10)
        
        # Storage limit + Stats on same line with separator
        cookies_stats_layout = QHBoxLayout()
        
        # Storage limit for cookies
        cookies_stats_layout.addWidget(QLabel(lang.get("backup_size_limit_label", default="Limite de stockage") + " :"))
        self.cookies_backup_size_limit_edit = QLineEdit()
        self.cookies_backup_size_limit_edit.setText(str(config.get("backup.cookies.size_limit_mb", 20)))
        self.cookies_backup_size_limit_edit.setMaximumWidth(60)
        self.cookies_backup_size_limit_edit.textChanged.connect(self._on_cookies_limit_changed)
        cookies_stats_layout.addWidget(self.cookies_backup_size_limit_edit)
        cookies_stats_layout.addWidget(QLabel("MB"))
        cookies_stats_layout.addWidget(QLabel(lang.get("backup_size_limit_tooltip", default="(-1 = illimité)")))
        cookies_stats_layout.addSpacing(15)
        
        # Vertical separator
        cookies_separator1 = QFrame()
        cookies_separator1.setFrameShape(QFrame.VLine)
        cookies_separator1.setFrameShadow(QFrame.Sunken)
        cookies_separator1.setStyleSheet("color: #888888;")
        cookies_stats_layout.addWidget(cookies_separator1)
        cookies_stats_layout.addSpacing(10)
        
        # Total cookies backups
        total_cookies_backups = len(cookies_info["backups"])
        cookies_stats_layout.addWidget(QLabel(lang.get("backup_total_label", default="Nombre de sauvegardes") + " :"))
        self.cookies_total_label = QLabel(f"{total_cookies_backups}")
        self.cookies_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        cookies_stats_layout.addWidget(self.cookies_total_label)
        cookies_stats_layout.addSpacing(10)
        
        # Vertical separator
        cookies_separator2 = QFrame()
        cookies_separator2.setFrameShape(QFrame.VLine)
        cookies_separator2.setFrameShadow(QFrame.Sunken)
        cookies_separator2.setStyleSheet("color: #888888;")
        cookies_stats_layout.addWidget(cookies_separator2)
        cookies_stats_layout.addSpacing(10)
        
        # Last cookies backup date
        last_cookies_backup_date = config.get("backup.cookies.last_date")
        if last_cookies_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_cookies_backup_date)
                last_cookies_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_cookies_str = "N/A"
        else:
            last_cookies_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
        cookies_stats_layout.addWidget(QLabel(lang.get("backup_last_label", default="Dernière sauvegarde") + " :"))
        self.cookies_last_label = QLabel(last_cookies_str)
        self.cookies_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        cookies_stats_layout.addWidget(self.cookies_last_label)
        cookies_stats_layout.addSpacing(15)
        
        # Vertical separator
        cookies_separator3 = QFrame()
        cookies_separator3.setFrameShape(QFrame.VLine)
        cookies_separator3.setFrameShadow(QFrame.Sunken)
        cookies_separator3.setStyleSheet("color: #888888;")
        cookies_stats_layout.addWidget(cookies_separator3)
        cookies_stats_layout.addSpacing(10)
        
        # Manual backup button
        cookies_backup_now_button = QPushButton("💾 " + lang.get("backup_now_button", default="Sauvegarder maintenant"))
        cookies_backup_now_button.clicked.connect(self._backup_cookies_now)
        cookies_backup_now_button.setToolTip(lang.get("backup_now_tooltip", default="Créer une sauvegarde manuelle immédiate"))
        cookies_backup_now_button.setMaximumWidth(200)
        cookies_stats_layout.addWidget(cookies_backup_now_button)
        
        cookies_stats_layout.addStretch()
        cookies_layout.addLayout(cookies_stats_layout)
        cookies_layout.addSpacing(15)
        
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)
        
        # === ARMOR BACKUP ===
        armor_info = self.backup_manager.get_armor_backup_info()
        armor_group = QGroupBox("🛡️ " + lang.get("backup_armor_title", default="Sauvegardes des données d'armures"))
        armor_layout = QVBoxLayout()
        
        # Enabled checkbox and compress checkbox side by side
        armor_enable_compress_layout = QHBoxLayout()
        
        self.armor_backup_enabled_check = QCheckBox(lang.get("backup_enabled_label", default="Activer les sauvegardes"))
        self.armor_backup_enabled_check.setChecked(config.get("backup.armor.auto_daily_backup", True))
        self.armor_backup_enabled_check.stateChanged.connect(lambda state: self._save_backup_setting("armor_backup_enabled", state == 2))
        armor_enable_compress_layout.addWidget(self.armor_backup_enabled_check)
        
        armor_enable_compress_layout.addSpacing(30)
        
        self.armor_backup_compress_check = QCheckBox(lang.get("backup_compress_label", default="Compresser les sauvegardes (ZIP)"))
        self.armor_backup_compress_check.setChecked(config.get("backup.armor.compress", True))
        self.armor_backup_compress_check.setToolTip(lang.get("backup_compress_tooltip", default="Réduit la taille des sauvegardes"))
        self.armor_backup_compress_check.stateChanged.connect(lambda state: self._save_backup_setting("armor_backup_compress", state == 2))
        armor_enable_compress_layout.addWidget(self.armor_backup_compress_check)
        
        armor_enable_compress_layout.addSpacing(30)
        
        # Auto-delete checkbox for armor
        self.armor_backup_auto_delete_check = QCheckBox(lang.get("backup_auto_delete_label", default="Supprimer auto les anciens"))
        self.armor_backup_auto_delete_check.setChecked(config.get("backup.armor.auto_delete_old", True))
        self.armor_backup_auto_delete_check.setToolTip(lang.get("backup_auto_delete_tooltip", default="Supprime automatiquement les plus anciens backups quand la limite est atteinte"))
        self.armor_backup_auto_delete_check.stateChanged.connect(self._on_armor_auto_delete_changed)
        armor_enable_compress_layout.addWidget(self.armor_backup_auto_delete_check)
        
        armor_enable_compress_layout.addStretch()
        armor_layout.addLayout(armor_enable_compress_layout)
        armor_layout.addSpacing(10)
        
        # Armor backup path
        armor_path_form = QFormLayout()
        self.armor_backup_path_edit = QLineEdit()
        armor_backup_path = config.get("backup.armor.path")
        if not armor_backup_path:
            from Functions.path_manager import get_base_path
            armor_backup_path = os.path.join(get_base_path(), "Backup", "Armor")
        self.armor_backup_path_edit.setText(armor_backup_path)
        self.armor_backup_path_edit.setReadOnly(True)
        self.armor_backup_path_edit.setCursorPosition(0)
        
        browse_armor_button = QPushButton(lang.get("browse_button", default="Parcourir..."))
        browse_armor_button.clicked.connect(self._browse_armor_backup_path)
        browse_armor_button.setMaximumWidth(100)
        
        move_armor_backup_button = QPushButton("📦 " + lang.get("move_folder_button", default="Déplacer"))
        move_armor_backup_button.clicked.connect(lambda: self._move_folder(self.armor_backup_path_edit, "armor_backup_path", lang.get("backup_path_label", default="Dossier de sauvegarde")))
        move_armor_backup_button.setToolTip(lang.get("move_folder_tooltip", default="Déplacer le dossier et son contenu vers un nouvel emplacement"))
        
        open_armor_backup_folder_button = QPushButton("📂 " + lang.get("backup_open_folder", default="Ouvrir le dossier"))
        open_armor_backup_folder_button.clicked.connect(self._open_armor_backup_folder)
        
        armor_path_layout = QHBoxLayout()
        armor_path_layout.addWidget(self.armor_backup_path_edit)
        armor_path_layout.addWidget(browse_armor_button)
        armor_path_layout.addWidget(move_armor_backup_button)
        armor_path_layout.addWidget(open_armor_backup_folder_button)
        armor_path_form.addRow(lang.get("backup_path_label", default="Dossier de sauvegarde") + " :", armor_path_layout)
        armor_layout.addLayout(armor_path_form)
        armor_layout.addSpacing(10)
        
        # Storage limit + Stats on same line with separator
        armor_stats_layout = QHBoxLayout()
        
        # Storage limit for armor
        armor_stats_layout.addWidget(QLabel(lang.get("backup_size_limit_label", default="Limite de stockage") + " :"))
        self.armor_backup_size_limit_edit = QLineEdit()
        self.armor_backup_size_limit_edit.setText(str(config.get("backup.armor.size_limit_mb", 20)))
        self.armor_backup_size_limit_edit.setMaximumWidth(60)
        self.armor_backup_size_limit_edit.textChanged.connect(self._on_armor_limit_changed)
        armor_stats_layout.addWidget(self.armor_backup_size_limit_edit)
        armor_stats_layout.addWidget(QLabel("MB"))
        armor_stats_layout.addWidget(QLabel(lang.get("backup_size_limit_tooltip", default="(-1 = illimité)")))
        armor_stats_layout.addSpacing(15)
        
        # Vertical separator
        armor_separator1 = QFrame()
        armor_separator1.setFrameShape(QFrame.VLine)
        armor_separator1.setFrameShadow(QFrame.Sunken)
        armor_separator1.setStyleSheet("color: #888888;")
        armor_stats_layout.addWidget(armor_separator1)
        armor_stats_layout.addSpacing(10)
        
        # Total armor backups
        total_armor_backups = len(armor_info["backups"])
        armor_stats_layout.addWidget(QLabel(lang.get("backup_total_label", default="Nombre de sauvegardes") + " :"))
        self.armor_total_label = QLabel(f"{total_armor_backups}")
        self.armor_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        armor_stats_layout.addWidget(self.armor_total_label)
        armor_stats_layout.addSpacing(10)
        
        # Vertical separator
        armor_separator2 = QFrame()
        armor_separator2.setFrameShape(QFrame.VLine)
        armor_separator2.setFrameShadow(QFrame.Sunken)
        armor_separator2.setStyleSheet("color: #888888;")
        armor_stats_layout.addWidget(armor_separator2)
        armor_stats_layout.addSpacing(10)
        
        # Last armor backup date
        last_armor_backup_date = config.get("backup.armor.last_date")
        if last_armor_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_armor_backup_date)
                last_armor_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_armor_str = "N/A"
        else:
            last_armor_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
        armor_stats_layout.addWidget(QLabel(lang.get("backup_last_label", default="Dernière sauvegarde") + " :"))
        self.armor_last_label = QLabel(last_armor_str)
        self.armor_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        armor_stats_layout.addWidget(self.armor_last_label)
        armor_stats_layout.addSpacing(15)
        
        # Vertical separator
        armor_separator3 = QFrame()
        armor_separator3.setFrameShape(QFrame.VLine)
        armor_separator3.setFrameShadow(QFrame.Sunken)
        armor_separator3.setStyleSheet("color: #888888;")
        armor_stats_layout.addWidget(armor_separator3)
        armor_stats_layout.addSpacing(10)
        
        # Manual backup button
        armor_backup_now_button = QPushButton("💾 " + lang.get("backup_now_button", default="Sauvegarder maintenant"))
        armor_backup_now_button.clicked.connect(self._backup_armor_now)
        armor_backup_now_button.setToolTip(lang.get("backup_now_tooltip", default="Créer une sauvegarde manuelle immédiate"))
        armor_backup_now_button.setMaximumWidth(200)
        armor_stats_layout.addWidget(armor_backup_now_button)
        
        armor_stats_layout.addStretch()
        armor_layout.addLayout(armor_stats_layout)
        armor_layout.addSpacing(15)
        
        armor_group.setLayout(armor_layout)
        layout.addWidget(armor_group)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_armory_page(self):
        """Page 7: Armory Settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(f"🛡️ {lang.get('settings.pages.armory.title', default='Armurerie')}")
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get('settings.pages.armory.subtitle', default="Import et gestion de la base de données d'items"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === FOLDER PATH (always visible) ===
        folder_group = QGroupBox("📁 " + lang.get("config_folder_group_title", default="Dossiers"))
        folder_layout = QFormLayout()
        
        # Armor Path
        self.armor_path_edit = QLineEdit()
        browse_armor_button = QPushButton(lang.get("browse_button"))
        browse_armor_button.setMaximumWidth(80)
        browse_armor_button.clicked.connect(self._browse_armor_folder)
        
        move_armor_button = QPushButton(lang.get("move_folder_button"))
        move_armor_button.setMaximumWidth(120)
        move_armor_button.clicked.connect(self._move_armor_folder)
        
        open_armor_folder_button = QPushButton(lang.get("open_folder_button"))
        open_armor_folder_button.setMaximumWidth(100)
        open_armor_folder_button.clicked.connect(self._open_armor_folder)
        
        armor_path_layout = QHBoxLayout()
        armor_path_layout.addWidget(self.armor_path_edit)
        armor_path_layout.addWidget(browse_armor_button)
        armor_path_layout.addWidget(move_armor_button)
        armor_path_layout.addWidget(open_armor_folder_button)
        folder_layout.addRow(lang.get("config_armor_path_label"), armor_path_layout)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        layout.addSpacing(10)
        
        # === DATABASE MODE (en haut de la page) ===
        db_group = QGroupBox(lang.get('armory_settings.group_title', default="🗄️ Base de données d'items"))
        db_layout = QVBoxLayout()
        
        # Enable personal database checkbox
        self.personal_db_check = QCheckBox(lang.get('armory_settings.enable_personal_db', default="Activer la base de données personnelle"))
        self.personal_db_check.setToolTip(lang.get('armory_settings.enable_personal_db_tooltip', 
            default="Copie la base interne dans votre dossier Armory pour permettre les imports et modifications"))
        self.personal_db_check.clicked.connect(self._on_personal_db_toggled)
        db_layout.addWidget(self.personal_db_check)
        
        # Mode info label
        self.mode_info_label = QLabel()
        self.mode_info_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        db_layout.addWidget(self.mode_info_label)
        
        db_layout.addSpacing(10)
        
        # Statistics group (hidden by default)
        self.stats_group = QGroupBox(lang.get('armory_settings.stats_group_title', default="📊 Statistiques"))
        stats_layout = QFormLayout()
        
        self.internal_count_label = QLabel(lang.get('armory_settings.stats_not_available', default="Non disponible"))
        stats_layout.addRow(lang.get('armory_settings.stats_internal_count', default="Items dans la base interne:"), 
                           self.internal_count_label)
        
        self.personal_count_label = QLabel(lang.get('armory_settings.stats_not_available', default="Non disponible"))
        stats_layout.addRow(lang.get('armory_settings.stats_personal_count', default="Items dans votre base:"), 
                           self.personal_count_label)
        
        self.user_added_label = QLabel(lang.get('armory_settings.stats_not_available', default="Non disponible"))
        stats_layout.addRow(lang.get('armory_settings.stats_user_added_count', default="Items ajoutés par vous:"), 
                           self.user_added_label)
        
        self.stats_group.setLayout(stats_layout)
        self.stats_group.setVisible(False)
        db_layout.addWidget(self.stats_group)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        layout.addSpacing(10)
        
        # === IMPORT SECTION ===
        self.import_group = QGroupBox(lang.get('settings.pages.armory.import_group_title', default="📥 Import d'items"))
        import_layout = QVBoxLayout()
        
        # Import button
        self.armory_import_button = QPushButton(lang.get('settings.pages.armory.import_button', default="📥 Importer des items"))
        self.armory_import_button.setMinimumHeight(40)
        self.armory_import_button.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: palette(highlight);
            }
        """)
        self.armory_import_button.clicked.connect(self._open_armory_import)
        import_layout.addWidget(self.armory_import_button)
        
        import_help = QLabel(lang.get('settings.pages.armory.import_help',
            default="💡 Cliquez sur le bouton ci-dessus pour ouvrir l'interface d'import. "
            "Vous pourrez sélectionner un fichier template (.txt), "
            "choisir le royaume et lancer l'import automatique."
        ))
        import_help.setWordWrap(True)
        import_help.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        import_layout.addWidget(import_help)
        
        self.import_group.setLayout(import_layout)
        self.import_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.import_group)
        
        # === RESET SECTION (at the end) ===
        self.actions_group = QGroupBox(lang.get('armory_settings.actions_group_title', default="⚙️ Actions"))
        actions_layout = QVBoxLayout()
        
        self.reset_db_button = QPushButton(lang.get('armory_settings.reset_db_button', default="🔄 Réinitialiser ma base"))
        self.reset_db_button.setToolTip(lang.get('armory_settings.reset_db_tooltip',
            default="Remplace votre base personnelle par une copie fraîche de la base interne (perte de vos ajouts personnels)"))
        self.reset_db_button.clicked.connect(self._reset_personal_database)
        actions_layout.addWidget(self.reset_db_button)
        
        self.actions_group.setLayout(actions_layout)
        self.actions_group.setVisible(False)
        layout.addWidget(self.actions_group)
        
        # Update database mode UI (after all groups are created)
        self._update_armory_database_mode()
        
        layout.addStretch()
        self.pages.addWidget(page)
    
    def _create_superadmin_page(self):
        """Page 8: SuperAdmin Tools (only visible with --admin flag)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel("🔧⚡ " + lang.get('superadmin.title', default='SuperAdmin'))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # === ITEMS DATABASE SECTION ===
        armory_section = QGroupBox("🗄️ " + lang.get('superadmin.items_database_section_title', default="Items Database"))
        armory_layout = QVBoxLayout()
        
        # === WARNING (inside Items Database section) ===
        warning_label = QLabel("⚠️ " + lang.get('superadmin.warning', default='Ces outils modifient la base de données source embarquée. Usage réservé aux développeurs.'))
        warning_label.setStyleSheet("background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; font-weight: bold;")
        warning_label.setWordWrap(True)
        armory_layout.addWidget(warning_label)
        armory_layout.addSpacing(10)
        
        # === STATISTICS AND ADVANCED OPERATIONS (side by side) ===
        stats_advanced_layout = QHBoxLayout()
        
        # === STATISTICS GROUP (left side - 50%) ===
        stats_group = QGroupBox(lang.get('superadmin.stats_group_title', 
            default="📊 Items Database Statistics"))
        stats_layout = QFormLayout()
        
        self.superadmin_stats_dbname = QLabel("items_database_src.json")
        self.superadmin_stats_dbname.setStyleSheet("font-weight: bold; color: #2196f3;")
        stats_layout.addRow(lang.get('superadmin.stats_database_name', default="Base de données:"), 
                           self.superadmin_stats_dbname)
        
        self.superadmin_stats_total = QLabel("0")
        stats_layout.addRow(lang.get('superadmin.stats_total', default="Total items:"), 
                           self.superadmin_stats_total)
        
        self.superadmin_stats_albion = QLabel("0")
        stats_layout.addRow(lang.get('superadmin.stats_albion', default="Albion:"), 
                           self.superadmin_stats_albion)
        
        self.superadmin_stats_hibernia = QLabel("0")
        stats_layout.addRow(lang.get('superadmin.stats_hibernia', default="Hibernia:"), 
                           self.superadmin_stats_hibernia)
        
        self.superadmin_stats_midgard = QLabel("0")
        stats_layout.addRow(lang.get('superadmin.stats_midgard', default="Midgard:"), 
                           self.superadmin_stats_midgard)
        
        self.superadmin_stats_all_realms = QLabel("0")
        stats_layout.addRow(lang.get('superadmin.stats_all_realms', default="Tous royaumes:"), 
                           self.superadmin_stats_all_realms)
        
        self.superadmin_stats_file_size = QLabel("0 KB")
        stats_layout.addRow(lang.get('superadmin.stats_file_size', default="Taille fichier:"), 
                           self.superadmin_stats_file_size)
        
        self.superadmin_stats_last_updated = QLabel(lang.get('superadmin.stats_not_available', default="Non disponible"))
        stats_layout.addRow(lang.get('superadmin.stats_last_updated', default="Dernière mise à jour:"), 
                           self.superadmin_stats_last_updated)
        
        stats_refresh_button = QPushButton(lang.get('superadmin.stats_refresh_button', 
            default="Actualiser"))
        stats_refresh_button.setMinimumHeight(35)
        stats_refresh_button.clicked.connect(self._refresh_superadmin_stats)
        stats_layout.addRow("", stats_refresh_button)
        
        stats_group.setLayout(stats_layout)
        stats_advanced_layout.addWidget(stats_group, 1)  # 50% width
        
        # === ADVANCED OPERATIONS GROUP (right side - 50%) ===
        advanced_group = QGroupBox(lang.get('superadmin.advanced_group_title', 
            default="⚙️ Opérations avancées"))
        advanced_layout = QVBoxLayout()
        
        # Database Import button (first position)
        database_import_button = QPushButton(lang.get('superadmin.database_import_button', 
            default="🔧 Database Management Tools"))
        database_import_button.setMinimumHeight(35)
        database_import_button.setToolTip(lang.get('superadmin.database_import_tooltip', 
            default="Ouvrir la fenêtre Database Management Tools pour sélectionner et importer des templates dans la base source"))
        database_import_button.clicked.connect(self._open_mass_import_monitor)
        advanced_layout.addWidget(database_import_button)
        
        clean_duplicates_button = QPushButton(lang.get('superadmin.clean_duplicates_button', 
            default="🧹 Nettoyer les doublons"))
        clean_duplicates_button.setMinimumHeight(35)
        clean_duplicates_button.setToolTip(lang.get('superadmin.clean_duplicates_tooltip', 
            default="Supprime les items en double (même nom + royaume) dans la base source"))
        clean_duplicates_button.clicked.connect(self._clean_duplicates)
        advanced_layout.addWidget(clean_duplicates_button)
        
        # Refresh All Items button
        refresh_items_button = QPushButton(lang.get('superadmin.refresh_items_button', 
            default="🔄 Rafraîchir tous les items"))
        refresh_items_button.setMinimumHeight(35)
        refresh_items_button.setToolTip(lang.get('superadmin.refresh_items_tooltip', 
            default="Re-scrape tous les items depuis Eden pour mettre à jour les données (Model, DPS, Speed, etc.)"))
        refresh_items_button.clicked.connect(self._refresh_all_items)
        advanced_layout.addWidget(refresh_items_button)
        
        # Database Editor button
        db_editor_button = QPushButton(lang.get('superadmin.database_editor_button', 
            default="🗄️ Database Editor"))
        db_editor_button.setMinimumHeight(35)
        db_editor_button.setToolTip(lang.get('superadmin.database_editor_tooltip', 
            default="Ouvrir l'éditeur de base de données pour modifier directement items_database_src.json"))
        db_editor_button.clicked.connect(self._open_database_editor)
        advanced_layout.addWidget(db_editor_button)
        
        advanced_layout.addStretch()  # Push buttons to top
        
        advanced_group.setLayout(advanced_layout)
        stats_advanced_layout.addWidget(advanced_group, 1)  # 50% width
        
        # Add the horizontal layout to armory layout
        armory_layout.addLayout(stats_advanced_layout)
        
        # Close Items Database section
        armory_section.setLayout(armory_layout)
        layout.addWidget(armory_section)
        
        # Initialize statistics on page creation
        self._refresh_superadmin_stats()
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    def _create_debug_page(self):
        """Page 7: Debug Settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_debug_title", default="Debug"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel(lang.get("settings_debug_subtitle", 
                                  default="Options de débogage et diagnostics"))
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # === Log Folder Path ===
        log_group = QGroupBox("📁 " + lang.get("config_log_folder_group_title", 
                                              default="Dossier des logs"))
        log_layout = QFormLayout()
        
        self.log_path_edit = QLineEdit()
        browse_log_button = QPushButton(lang.get("browse_button"))
        browse_log_button.clicked.connect(self._browse_log_folder)
        move_log_button = QPushButton("📦 " + lang.get("move_folder_button", default="Déplacer"))
        move_log_button.clicked.connect(lambda: self._move_folder(self.log_path_edit, "log_folder", lang.get("config_log_path_label")))
        move_log_button.setToolTip(lang.get("move_folder_tooltip", default="Déplacer le dossier et son contenu vers un nouvel emplacement"))
        open_log_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
        open_log_folder_button.clicked.connect(self._open_log_folder)
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(browse_log_button)
        log_path_layout.addWidget(move_log_button)
        log_path_layout.addWidget(open_log_folder_button)
        log_layout.addRow(lang.get("config_log_path_label"), log_path_layout)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # === Debug Application ===
        debug_app_group = QGroupBox("🐛 " + lang.get("config_debug_app_group_title", 
                                                      default="Debug Application"))
        debug_app_layout = QVBoxLayout()
        
        self.debug_mode_check = QCheckBox(lang.get("config_debug_mode_label"))
        self.debug_mode_check.setToolTip(
            "Active le mode debug et crée un fichier debug.log avec des informations détaillées."
        )
        debug_app_layout.addWidget(self.debug_mode_check)
        
        self.show_debug_window_check = QCheckBox(lang.get("config_show_debug_window_label"))
        self.show_debug_window_check.setToolTip(
            "Affiche automatiquement la fenêtre de debug au démarrage de l'application."
        )
        debug_app_layout.addWidget(self.show_debug_window_check)
        
        debug_app_group.setLayout(debug_app_layout)
        layout.addWidget(debug_app_group)
        
        # === Debug Eden ===
        debug_eden_group = QGroupBox("🌐 " + lang.get("config_debug_eden_group_title", 
                                                       default="Debug Eden"))
        debug_eden_layout = QVBoxLayout()
        
        eden_debug_button = QPushButton(lang.get("menu_help_eden_debug", default="🐛 Fenêtre de debug Eden"))
        eden_debug_button.clicked.connect(lambda: self.parent().open_eden_debug())
        eden_debug_button.setMaximumWidth(300)
        debug_eden_layout.addWidget(eden_debug_button)
        
        # Checkbox: Save Herald HTML
        self.debug_save_herald_html = QCheckBox(lang.get("settings.labels.debug_save_herald_html", 
                                                         default="💾 Sauvegarder HTML Herald (debug_herald_page.html)"))
        self.debug_save_herald_html.setToolTip(lang.get("settings.tooltips.debug_save_herald_html",
                                                        default="Sauvegarde le HTML de la page Herald dans Logs/ pour diagnostic"))
        debug_eden_layout.addWidget(self.debug_save_herald_html)
        
        # Checkbox: Save Test Connection HTML
        self.debug_save_test_connection_html = QCheckBox(lang.get("settings.labels.debug_save_test_connection_html", 
                                                                   default="💾 Sauvegarder HTML Test Connexion (debug_test_connection.html)"))
        self.debug_save_test_connection_html.setToolTip(lang.get("settings.tooltips.debug_save_test_connection_html",
                                                                 default="Sauvegarde le HTML du test de connexion dans Logs/ pour diagnostic"))
        debug_eden_layout.addWidget(self.debug_save_test_connection_html)
        
        debug_eden_group.setLayout(debug_eden_layout)
        layout.addWidget(debug_eden_group)
        
        # Info about debug
        info_label = QLabel(
            "💡 " + lang.get("settings_debug_info",
                           default="Le mode debug est utile pour diagnostiquer des problèmes.\n\n"
                                  "Les logs de debug sont sauvegardés dans le dossier Logs/")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: palette(alternate-base); padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.pages.addWidget(page)
        
    # === Browse Methods ===
    
    def _browse_folder(self, line_edit, title_key):
        """Generic folder browser"""
        directory = QFileDialog.getExistingDirectory(self, lang.get(title_key))
        if directory:
            # Normalize path to use backslashes on Windows
            normalized_directory = directory.replace('/', '\\')
            line_edit.setText(normalized_directory)
            
    def _browse_character_folder(self):
        old_path = self.char_path_edit.text()
        self._browse_folder(self.char_path_edit, "select_folder_dialog_title")
        new_path = self.char_path_edit.text()
        
        # If path changed, save and reload character list
        if old_path != new_path:
            config.set("folders.characters", new_path)
            config.save_config()
            if self.parent():
                self.parent().refresh_character_list()
        
    def _browse_log_folder(self):
        old_path = self.log_path_edit.text()
        self._browse_folder(self.log_path_edit, "select_log_folder_dialog_title")
        new_path = self.log_path_edit.text()
        
        # If path changed, save and reinitialize logging
        if old_path != new_path:
            config.set("folders.logs", new_path)
            config.save_config()
            from Functions.logging_manager import setup_logging
            setup_logging()
        
    def _browse_armor_folder(self):
        old_path = self.armor_path_edit.text()
        self._browse_folder(self.armor_path_edit, "select_folder_dialog_title")
        new_path = self.armor_path_edit.text()
        
        # If path changed, save immediately
        if old_path != new_path:
            config.set("folders.armor", new_path)
            config.save_config()
        
    def _browse_backup_path(self):
        """Browse for backup folder"""
        directory = QFileDialog.getExistingDirectory(self, lang.get("backup_select_folder", default="Sélectionner le dossier de sauvegarde"))
        if directory:
            normalized_directory = directory.replace('/', '\\')
            self.backup_path_edit.setText(normalized_directory)
    
    def _browse_cookies_backup_path(self):
        """Browse for cookies backup folder"""
        directory = QFileDialog.getExistingDirectory(self, lang.get("backup_select_folder", default="Sélectionner le dossier de sauvegarde"))
        if directory:
            normalized_directory = directory.replace('/', '\\')
            self.cookies_backup_path_edit.setText(normalized_directory)
    
    def _backup_characters_now(self):
        """Execute characters backup now"""
        from PySide6.QtWidgets import QMessageBox
        try:
            # Save current path from text field to config and reinitialize backup_manager
            config.set("backup.characters.path", self.backup_path_edit.text())
            config.save_config()
            self.backup_manager = BackupManager(config)
            
            result = self.backup_manager.backup_characters_force()
            if result:
                # Update last backup date display
                from datetime import datetime
                last_backup_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.backup_last_label.setText(last_backup_str)
                self.backup_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
                
                # Update total count
                backup_info = self.backup_manager.get_backup_info()
                self.backup_total_label.setText(str(len(backup_info["backups"])))
                
                QMessageBox.information(self, lang.get("success_title", default="Succès"), 
                                       lang.get("backup_success", default="Sauvegarde créée avec succès"))
            else:
                QMessageBox.warning(self, lang.get("warning_title", default="Attention"),
                                   lang.get("backup_failed", default="La sauvegarde a échoué"))
        except Exception as e:
            QMessageBox.critical(self, lang.get("error_title", default="Erreur"),
                                f"{lang.get('backup_error', default='Erreur lors de la sauvegarde')} : {str(e)}")
    
    def _backup_cookies_now(self):
        """Execute cookies backup now"""
        from PySide6.QtWidgets import QMessageBox
        try:
            # Save current path from text field to config and reinitialize backup_manager
            config.set("backup.cookies.path", self.cookies_backup_path_edit.text())
            config.save_config()
            self.backup_manager = BackupManager(config)
            
            result = self.backup_manager.backup_cookies_force()
            if result:
                # Update last backup date display
                from datetime import datetime
                last_backup_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cookies_last_label.setText(last_backup_str)
                self.cookies_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
                
                # Update total count
                cookies_info = self.backup_manager.get_cookies_backup_info()
                self.cookies_total_label.setText(str(len(cookies_info["backups"])))
                
                QMessageBox.information(self, lang.get("success_title", default="Succès"),
                                       lang.get("backup_success", default="Sauvegarde créée avec succès"))
            else:
                QMessageBox.warning(self, lang.get("warning_title", default="Attention"),
                                   lang.get("backup_failed", default="La sauvegarde a échoué"))
        except Exception as e:
            QMessageBox.critical(self, lang.get("error_title", default="Erreur"),
                                f"{lang.get('backup_error', default='Erreur lors de la sauvegarde')} : {str(e)}")
    
    def _backup_armor_now(self):
        """Execute armor backup now"""
        from PySide6.QtWidgets import QMessageBox
        try:
            # Save current path from text field to config and reinitialize backup_manager
            config.set("backup.armor.path", self.armor_backup_path_edit.text())
            config.save_config()
            self.backup_manager = BackupManager(config)
            
            result = self.backup_manager.backup_armor_force()
            if result:
                # Update last backup date display
                from datetime import datetime
                last_backup_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.armor_last_label.setText(last_backup_str)
                self.armor_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
                
                # Update total count
                armor_info = self.backup_manager.get_armor_backup_info()
                self.armor_total_label.setText(str(len(armor_info["backups"])))
                
                QMessageBox.information(self, lang.get("success_title", default="Succès"),
                                       lang.get("backup_success", default="Sauvegarde créée avec succès"))
            else:
                QMessageBox.warning(self, lang.get("warning_title", default="Attention"),
                                   lang.get("backup_failed", default="La sauvegarde a échoué"))
        except Exception as e:
            QMessageBox.critical(self, lang.get("error_title", default="Erreur"),
                                f"{lang.get('backup_error', default='Erreur lors de la sauvegarde')} : {str(e)}")
    
    def _open_character_folder(self):
        """Open characters folder"""
        import subprocess
        char_path = self.char_path_edit.text()
        if os.path.exists(char_path):
            subprocess.Popen(f'explorer "{char_path}"')
    
    def _move_armor_folder(self):
        """Move armor folder to new location"""
        from PySide6.QtWidgets import QMessageBox
        import shutil
        
        # Browse for new location
        new_location = QFileDialog.getExistingDirectory(
            self, 
            lang.get("select_new_armor_location", default="Sélectionner le nouvel emplacement pour Armory")
        )
        
        if not new_location:
            return
        
        old_path = self.armor_path_edit.text()
        new_path = os.path.join(new_location, "Armory")
        
        if old_path == new_path:
            return
        
        # Confirm move
        reply = QMessageBox.question(
            self,
            lang.get("move_armor_confirm_title", default="Confirmer le déplacement"),
            lang.get("move_armor_confirm_message", 
                    default=f"Déplacer le dossier Armory ?\n\nDe : {old_path}\nVers : {new_path}"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Create new directory if it doesn't exist
                os.makedirs(new_path, exist_ok=True)
                
                # Copy all files
                if os.path.exists(old_path):
                    for item in os.listdir(old_path):
                        s = os.path.join(old_path, item)
                        d = os.path.join(new_path, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                    
                    # Remove old directory
                    shutil.rmtree(old_path)
                
                # Update UI and config
                self.armor_path_edit.setText(new_path)
                config.set("folders.armor", new_path)
                config.save_config()
                
                QMessageBox.information(
                    self,
                    lang.get("move_success_title", default="Succès"),
                    lang.get("move_armor_success", default="Dossier Armory déplacé avec succès")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    lang.get("error_title", default="Erreur"),
                    lang.get("move_armor_error", default=f"Erreur lors du déplacement : {str(e)}")
                )
    
    def _open_armor_folder(self):
        """Open armor folder"""
        import subprocess
        armor_path = self.armor_path_edit.text()
        if os.path.exists(armor_path):
            subprocess.Popen(f'explorer "{armor_path}"')
    
    def _open_cookies_folder(self):
        """Open Eden data folder (AppData)"""
        import subprocess
        from Functions.path_manager import get_eden_data_dir
        eden_path = get_eden_data_dir()
        if os.path.exists(eden_path):
            subprocess.Popen(f'explorer "{eden_path}"')
    
    def _clean_eden_folder(self):
        """Clean all Eden folder content (cookies + Chrome profile)"""
        from PySide6.QtWidgets import QMessageBox
        from Functions.path_manager import get_eden_data_dir
        import shutil
        
        eden_path = get_eden_data_dir()
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            lang.get("clean_eden_confirm_title", default="Confirmer le nettoyage"),
            lang.get("clean_eden_confirm_message", 
                    default=f"⚠️ Cette action va supprimer :\n\n"
                           f"• Tous les cookies Eden\n"
                           f"• Le profil Chrome complet (cache, historique, session)\n\n"
                           f"📁 Dossier : {eden_path}\n\n"
                           f"Vous devrez régénérer vos cookies après cette opération.\n\n"
                           f"Continuer ?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(eden_path):
                    # Delete all content
                    shutil.rmtree(eden_path)
                    # Recreate empty folder
                    os.makedirs(eden_path, exist_ok=True)
                    
                    QMessageBox.information(
                        self,
                        lang.get("clean_eden_success_title", default="Nettoyage réussi"),
                        lang.get("clean_eden_success_message", 
                                default="✅ Le dossier Eden a été nettoyé.\n\n"
                                       "Dossier supprimé.")
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    lang.get("clean_eden_error_title", default="Erreur"),
                    lang.get("clean_eden_error_message", 
                            default=f"❌ Erreur lors du nettoyage :\n\n{str(e)}")
                )
    
    def _open_item_cache_folder(self):
        """Open Item Cache folder (AppData)"""
        import subprocess
        import os
        
        user_profile = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
        if user_profile:
            cache_path = os.path.join(user_profile, 'DAOC_Character_Manager', 'ItemCache')
        else:
            from pathlib import Path
            cache_path = str(Path(__file__).parent.parent / 'Armory')
        
        # Create folder if doesn't exist
        os.makedirs(cache_path, exist_ok=True)
        
        if os.path.exists(cache_path):
            subprocess.Popen(f'explorer "{cache_path}"')
    
    def _clean_item_cache(self):
        """Clean Item Cache folder"""
        from PySide6.QtWidgets import QMessageBox
        import shutil
        import os
        
        user_profile = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
        if user_profile:
            cache_path = os.path.join(user_profile, 'DAOC_Character_Manager', 'ItemCache')
        else:
            from pathlib import Path
            cache_path = str(Path(__file__).parent.parent / 'Armory')
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            lang.get("clean_cache_confirm_title", default="Confirmer le nettoyage"),
            lang.get("clean_cache_confirm_message", 
                    default=f"⚠️ Cette action va supprimer :\n\n"
                           f"• Le cache des items trouvés via recherche web\n\n"
                           f"📁 Dossier : {cache_path}\n\n"
                           f"Les items de la base de données ne seront pas affectés.\n\n"
                           f"Continuer ?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(cache_path):
                    # Delete items_cache.json if exists
                    cache_file = os.path.join(cache_path, 'items_cache.json')
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
                    
                    QMessageBox.information(
                        self,
                        lang.get("clean_cache_success_title", default="Nettoyage réussi"),
                        lang.get("clean_cache_success_message", 
                                default="✅ Le cache des items a été nettoyé.\n\n"
                                       "Cache supprimé.")
                    )
                else:
                    QMessageBox.information(
                        self,
                        lang.get("clean_cache_empty_title", default="Dossier vide"),
                        lang.get("clean_cache_empty_message", 
                                default="ℹ️ Le cache est déjà vide ou n'existe pas.")
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    lang.get("clean_cache_error_title", default="Erreur"),
                    lang.get("clean_cache_error_message", 
                            default=f"❌ Erreur lors du nettoyage :\n\n{str(e)}")
                )
    
    def _open_log_folder(self):
        """Open logs folder"""
        import subprocess
        log_path = self.log_path_edit.text()
        if os.path.exists(log_path):
            subprocess.Popen(f'explorer "{log_path}"')
    
    def _open_backup_folder(self):
        """Open characters backup folder"""
        import subprocess
        backup_path = self.backup_path_edit.text()
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(backup_path):
            os.makedirs(backup_path, exist_ok=True)
        subprocess.Popen(f'explorer "{backup_path}"')
    
    def _open_cookies_backup_folder(self):
        """Open cookies backup folder"""
        import subprocess
        cookies_backup_path = self.cookies_backup_path_edit.text()
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(cookies_backup_path):
            os.makedirs(cookies_backup_path, exist_ok=True)
        subprocess.Popen(f'explorer "{cookies_backup_path}"')
    
    def _move_folder(self, line_edit, config_key, folder_label):
        """Move or create a folder at a new location"""
        import shutil
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import Qt
        
        current_path = line_edit.text()
        source_exists = current_path and os.path.exists(current_path)
        
        # Ask for destination parent directory
        parent_dir = QFileDialog.getExistingDirectory(
            self,
            lang.get("move_folder_select_destination", default="Sélectionnez le dossier parent de destination")
        )
        
        if not parent_dir:
            return  # User cancelled
        
        # Normalize path to use backslashes on Windows
        parent_dir = parent_dir.replace('/', '\\')
        
        # Fixed folder names based on config_key (no user input)
        folder_names = {
            "character_folder": "Characters",
            "armor_folder": "Armory",
            "log_folder": "Logs",
            "cookies_folder": "Cookies",
            "backup_path": "Backups",
            "cookies_backup_path": "Backups",
            "armor_backup_path": "Backups"
        }
        
        folder_name = folder_names.get(config_key, "Data")
        
        # Special handling for backup folders: always use /Backups/ intermediate folder
        if config_key in ["backup_path", "cookies_backup_path", "armor_backup_path"]:
            # For backups: parent_dir/Backups/subfolder_type
            if config_key == "backup_path":
                subfolder_type = "Characters"
            elif config_key == "cookies_backup_path":
                subfolder_type = "Cookies"
            else:  # armor_backup_path
                subfolder_type = "Armor"
            backup_parent = os.path.join(parent_dir, "Backups")
            destination = os.path.join(backup_parent, subfolder_type)
        else:
            destination = os.path.join(parent_dir, folder_name)
        
        # Check if destination already exists and source exists (need to merge)
        destination_exists = os.path.exists(destination)
        if destination_exists and source_exists:
            reply = QMessageBox.question(
                self,
                lang.get("warning_title", default="Attention"),
                f"{lang.get('move_folder_destination_exists', default='Le dossier existe déjà à la destination.')}\n\n"
                f"{destination}\n\n"
                f"{lang.get('move_folder_merge_question', default='Voulez-vous fusionner les fichiers ?')}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                QMessageBox.information(
                    self,
                    lang.get("info_title", default="Information"),
                    lang.get("move_folder_cancelled", default="Opération annulée.")
                )
                return
            # Continue with merge (copytree with dirs_exist_ok=True)
        elif destination_exists and not source_exists:
            # Destination exists but no source to move - just update config
            line_edit.setText(destination)
            config.set(config_key, destination)
            config.save_config()
            self.backup_manager = BackupManager(config)
            
            # Reload character list if Characters folder changed
            if config_key == "character_folder" and self.parent():
                self.parent().refresh_character_list()
            
            # Reinitialize logging if log folder changed
            if config_key == "log_folder":
                from Functions.logging_manager import setup_logging
                setup_logging()
            
            QMessageBox.information(
                self,
                lang.get("success_title", default="Succès"),
                lang.get("move_folder_using_existing", 
                        default=f"Configuration mise à jour pour utiliser :\n{destination}")
            )
            return
        
        # If source exists, confirm move/copy
        if source_exists:
            reply = QMessageBox.question(
                self,
                lang.get("move_folder_confirm_title", default="Confirmer le déplacement"),
                f"{lang.get('move_folder_confirm_message', default='Voulez-vous déplacer le dossier et son contenu ?')}\n\n"
                f"De : {current_path}\n"
                f"Vers : {destination}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        else:
            # Just create new folder
            reply = QMessageBox.question(
                self,
                lang.get("create_folder_confirm_title", default="Créer le dossier"),
                f"{lang.get('create_folder_confirm_message', default='Créer le dossier à cet emplacement ?')}\n\n"
                f"{destination}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        
        # Progress dialog
        progress = QProgressDialog(
            lang.get("move_folder_in_progress", default="Opération en cours..."),
            lang.get("cancel", default="Annuler"),
            0, 0,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle(lang.get("move_folder_title", default="Déplacement"))
        progress.show()
        
        try:
            if source_exists:
                # Copy the folder (dirs_exist_ok allows destination to exist for merge)
                shutil.copytree(current_path, destination, dirs_exist_ok=True)
                
                # Update the line edit
                line_edit.setText(destination)
                
                # Save the new path immediately to config
                config.set(config_key, destination)
                config.save_config()
                
                # Reinitialize backup manager to use new path
                self.backup_manager = BackupManager(config)
                
                # Check if source folder is now empty (all files were moved in merge)
                source_is_empty = False
                if os.path.exists(current_path):
                    remaining_files = [item for item in os.listdir(current_path)]
                    source_is_empty = len(remaining_files) == 0
                
                # Reload character list if Characters folder changed
                if config_key == "character_folder" and self.parent():
                    self.parent().refresh_character_list()
                
                # Reinitialize logging if log folder changed
                if config_key == "log_folder":
                    from Functions.logging_manager import setup_logging
                    setup_logging()
                
                # Ask if user wants to delete old folder (or auto-delete if empty)
                if source_is_empty:
                    # Source is empty after merge, delete automatically
                    shutil.rmtree(current_path)
                    
                    # Check if parent Backup folder is now empty and delete it if so
                    parent_backup = os.path.dirname(current_path)
                    if os.path.exists(parent_backup) and os.path.basename(parent_backup).lower() == "backup":
                        remaining_items = [item for item in os.listdir(parent_backup) 
                                         if os.path.isdir(os.path.join(parent_backup, item))]
                        if not remaining_items:
                            shutil.rmtree(parent_backup)
                    
                    QMessageBox.information(
                        self,
                        lang.get("success_title", default="Succès"),
                        lang.get("move_folder_success", 
                                default=f"Dossier déplacé avec succès vers :\n{destination}")
                    )
                else:
                    # Source still has files, ask user
                    delete_reply = QMessageBox.question(
                        self,
                        lang.get("move_folder_delete_title", default="Supprimer l'ancien dossier ?"),
                        f"{lang.get('move_folder_delete_message', default='Le dossier a été copié avec succès. Voulez-vous supprimer l ancien dossier ?')}\n\n"
                        f"{current_path}",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if delete_reply == QMessageBox.Yes:
                        # Delete the old folder
                        shutil.rmtree(current_path)
                        
                        # Check if parent Backup folder is now empty and delete it if so
                        parent_backup = os.path.dirname(current_path)
                        if os.path.exists(parent_backup) and os.path.basename(parent_backup).lower() == "backup":
                            remaining_items = [item for item in os.listdir(parent_backup) 
                                             if os.path.isdir(os.path.join(parent_backup, item))]
                            if not remaining_items:
                                shutil.rmtree(parent_backup)
                        
                        QMessageBox.information(
                            self,
                            lang.get("success_title", default="Succès"),
                            lang.get("move_folder_success", 
                                    default=f"Dossier déplacé avec succès vers :\n{destination}")
                        )
                    else:
                        QMessageBox.information(
                            self,
                            lang.get("success_title", default="Succès"),
                            lang.get("move_folder_copy_success", 
                                    default=f"Dossier copié avec succès vers :\n{destination}\n\n"
                                           f"L'ancien dossier a été conservé.")
                        )
            else:
                # Create the folder (including intermediate folders for backups)
                os.makedirs(destination, exist_ok=True)
                
                # Update the line edit
                line_edit.setText(destination)
                
                # Save the new path immediately to config
                config.set(config_key, destination)
                config.save_config()
                
                # Reinitialize backup manager to use new path
                self.backup_manager = BackupManager(config)
                
                # Reload character list if Characters folder changed
                if config_key == "character_folder" and self.parent():
                    self.parent().refresh_character_list()
                
                # Reinitialize logging if log folder changed
                if config_key == "log_folder":
                    from Functions.logging_manager import setup_logging
                    setup_logging()
                
                QMessageBox.information(
                    self,
                    lang.get("success_title", default="Succès"),
                    lang.get("create_folder_success", 
                            default=f"Dossier créé avec succès :\n{destination}")
                )
            
            progress.close()
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                lang.get("error_title", default="Erreur"),
                lang.get("move_folder_error", 
                        default=f"Erreur lors du déplacement :\n{str(e)}")
            )
            logging.error(f"Error moving folder: {e}")
        
    # === Settings Load/Save ===
    
    def _load_settings(self):
        """Load current settings into the UI"""
        # Paths
        self.char_path_edit.setText(config.get("folders.characters") or get_character_dir())
        self.char_path_edit.setCursorPosition(0)
        
        # Config folder is not configurable - always next to executable
        
        self.log_path_edit.setText(config.get("folders.logs") or get_log_dir())
        self.log_path_edit.setCursorPosition(0)
        
        self.armor_path_edit.setText(config.get("folders.armor") or get_armor_dir())
        self.armor_path_edit.setCursorPosition(0)
        
        # Note: cookies_path_edit removed - Eden uses automatic AppData location
        
        # General settings
        self.debug_mode_check.setChecked(config.get("system.debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("system.show_debug_window", False))
        self.disable_disclaimer_check.setChecked(config.get("system.disable_disclaimer", False))
        
        # Debug HTML options
        self.debug_save_herald_html.setChecked(config.get("system.debug.save_herald_html", False))
        self.debug_save_test_connection_html.setChecked(config.get("system.debug.save_test_connection_html", False))
        
        # Defaults
        self.default_server_combo.setCurrentText(config.get("game.default_server", ""))
        self.default_season_combo.setCurrentText(config.get("game.default_season", ""))
        self.default_realm_combo.setCurrentText(config.get("game.default_realm", ""))
        
        # Language
        current_lang_code = config.get("ui.language", "en")
        current_lang_name = self.available_languages.get(current_lang_code, "Français")
        self.language_combo.setCurrentText(current_lang_name)
        
        # Theme
        current_theme = config.get("ui.theme", "dracula")
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
            
        # Font scale
        current_font_scale = config.get("ui.font_scale", 1.0)
        scale_index = self.font_scale_combo.findData(current_font_scale)
        if scale_index == -1:
            # Find closest value
            closest_index = 0
            min_diff = abs(self.font_scale_values[0] - current_font_scale)
            for i, scale_value in enumerate(self.font_scale_values):
                diff = abs(scale_value - current_font_scale)
                if diff < min_diff:
                    min_diff = diff
                    closest_index = i
            self.font_scale_combo.setCurrentIndex(closest_index)
        else:
            self.font_scale_combo.setCurrentIndex(scale_index)
            
        # Columns
        self.manual_column_resize_check.setChecked(config.get("ui.manual_column_resize", True))
        
        # Browser
        self.browser_combo.setCurrentText(config.get("system.preferred_browser", "Chrome"))
        self.allow_browser_download_check.setChecked(config.get("system.allow_browser_download", False))
    
    def _on_backup_auto_delete_changed(self, state):
        """Handle Characters backup auto-delete checkbox state change"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import Qt
        
        # If unchecked (user is disabling auto-delete), show warning
        # state is 0 for unchecked, 2 for checked
        if state == 0:  # Qt.CheckState.Unchecked
            reply = QMessageBox.warning(
                self,
                lang.get("backup_auto_delete_warning_title", default="⚠️ Avertissement"),
                lang.get("backup_auto_delete_warning_message", default=(
                    "ATTENTION : Désactiver la suppression automatique peut entraîner :\n\n"
                    "• Saturation de l'espace disque\n"
                    "• Blocage des futures sauvegardes\n"
                    "• Nécessité de gérer manuellement les anciens backups\n\n"
                    "Voulez-vous vraiment désactiver cette protection ?"
                )),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                # User cancelled - recheck the checkbox
                self.backup_auto_delete_check.blockSignals(True)
                self.backup_auto_delete_check.setChecked(True)
                self.backup_auto_delete_check.blockSignals(False)
                return
        
        # Save immediately
        self._save_backup_setting("backup_auto_delete_old", state == 2)
    
    def _on_cookies_auto_delete_changed(self, state):
        """Handle Cookies backup auto-delete checkbox state change"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import Qt
        
        # If unchecked (user is disabling auto-delete), show warning
        # state is 0 for unchecked, 2 for checked
        if state == 0:  # Qt.CheckState.Unchecked
            reply = QMessageBox.warning(
                self,
                lang.get("backup_auto_delete_warning_title", default="⚠️ Avertissement"),
                lang.get("backup_auto_delete_warning_message", default=(
                    "ATTENTION : Désactiver la suppression automatique peut entraîner :\n\n"
                    "• Saturation de l'espace disque\n"
                    "• Blocage des futures sauvegardes\n"
                    "• Nécessité de gérer manuellement les anciens backups\n\n"
                    "Voulez-vous vraiment désactiver cette protection ?"
                )),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                # User cancelled - recheck the checkbox
                self.cookies_backup_auto_delete_check.blockSignals(True)
                self.cookies_backup_auto_delete_check.setChecked(True)
                self.cookies_backup_auto_delete_check.blockSignals(False)
                return
        
        # Save immediately
        self._save_backup_setting("cookies_backup_auto_delete_old", state == 2)
    
    def _on_backup_limit_changed(self, text):
        """Handle Characters backup storage limit change"""
        try:
            limit = int(text)
            if limit == -1:
                # Unlimited - uncheck auto-delete without warning
                self.backup_auto_delete_check.blockSignals(True)
                self.backup_auto_delete_check.setChecked(False)
                self.backup_auto_delete_check.blockSignals(False)
                # Save immediately
                self._save_backup_setting("backup_auto_delete_old", False)
        except ValueError:
            pass  # Invalid input, ignore
    
    def _on_cookies_limit_changed(self, text):
        """Handle Cookies backup storage limit change"""
        try:
            limit = int(text)
            if limit == -1:
                # Unlimited - uncheck auto-delete without warning
                self.cookies_backup_auto_delete_check.blockSignals(True)
                self.cookies_backup_auto_delete_check.setChecked(False)
                self.cookies_backup_auto_delete_check.blockSignals(False)
                # Save immediately
                self._save_backup_setting("cookies_backup_auto_delete_old", False)
        except ValueError:
            pass  # Invalid input, ignore
    
    def _on_armor_auto_delete_changed(self, state):
        """Handle Armor backup auto-delete checkbox state change"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import Qt
        
        # If unchecked (user is disabling auto-delete), show warning
        # state is 0 for unchecked, 2 for checked
        if state == 0:  # Qt.CheckState.Unchecked
            reply = QMessageBox.warning(
                self,
                lang.get("backup_auto_delete_warning_title", default="⚠️ Avertissement"),
                lang.get("backup_auto_delete_warning_message", default=(
                    "ATTENTION : Désactiver la suppression automatique peut entraîner :\n\n"
                    "• Saturation de l'espace disque\n"
                    "• Blocage des futures sauvegardes\n"
                    "• Nécessité de gérer manuellement les anciens backups\n\n"
                    "Voulez-vous vraiment désactiver cette protection ?"
                )),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                # User cancelled - recheck the checkbox
                self.armor_backup_auto_delete_check.blockSignals(True)
                self.armor_backup_auto_delete_check.setChecked(True)
                self.armor_backup_auto_delete_check.blockSignals(False)
                return
        
        # Save immediately
        self._save_backup_setting("armor_backup_auto_delete_old", state == 2)
    
    def _on_armor_limit_changed(self, text):
        """Handle Armor backup storage limit change"""
        try:
            limit = int(text)
            if limit == -1:
                # Unlimited - uncheck auto-delete without warning
                self.armor_backup_auto_delete_check.blockSignals(True)
                self.armor_backup_auto_delete_check.setChecked(False)
                self.armor_backup_auto_delete_check.blockSignals(False)
                # Save immediately
                self._save_backup_setting("armor_backup_auto_delete_old", False)
        except ValueError:
            pass  # Invalid input, ignore
    
    def _save_backup_setting(self, key, value):
        """Save a backup setting immediately to config"""
        config.set(key, value)
        config.save_config()
    
    def _browse_armor_backup_path(self):
        """Browse for armor backup folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            lang.get("backup_path_label", default="Dossier de sauvegarde")
        )
        if folder:
            self.armor_backup_path_edit.setText(folder)
            self.armor_backup_path_edit.setCursorPosition(0)
    
    def _open_armor_backup_folder(self):
        """Open armor backup folder"""
        import subprocess
        armor_backup_path = self.armor_backup_path_edit.text()
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(armor_backup_path):
            os.makedirs(armor_backup_path, exist_ok=True)
        subprocess.Popen(f'explorer "{armor_backup_path}"')
    
    def _save_without_closing(self):
        """Save settings without closing the dialog"""
        # Trigger the accepted signal which will call save_configuration in main.py
        self.accepted.emit()
    
    def _cancel_changes(self):
        """Cancel changes and reload settings"""
        reply = QMessageBox.question(
            self,
            lang.get("warning_title", default="Attention"),
            lang.get("cancel_changes_confirm", default="Annuler les modifications non sauvegardées ?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._load_settings()
    
    def _open_armory_import(self):
        """Ouvre le dialogue d'import d'items pour l'armurerie"""
        from UI.armory_import_dialog import ArmoryImportDialog
        
        dialog = ArmoryImportDialog(self)
        dialog.exec()
        
        # Update database status after import
        # Initialize database manager
        from Functions.items_database_manager import ItemsDatabaseManager
        self.db_manager = ItemsDatabaseManager(self.config_manager, path_manager)
    
    def _update_armory_database_mode(self):
        """Update UI based on current database mode"""
        try:
            use_personal = self.config_manager.config.get('armory', {}).get('use_personal_database', False)
            
            # Update checkbox
            self.personal_db_check.setChecked(use_personal)
            
            # Update mode info label
            if use_personal:
                mode_text = lang.get('armory_settings.mode_info_personal', default="Mode actuel : Base de données personnelle (modifiable)")
                self.mode_info_label.setText(mode_text)
                self.mode_info_label.setStyleSheet("color: #4CAF50; font-style: italic; padding: 5px;")
                
                # Show stats, actions and import groups (only if they exist)
                if hasattr(self, 'stats_group'):
                    self.stats_group.setVisible(True)
                if hasattr(self, 'actions_group'):
                    self.actions_group.setVisible(True)
                if hasattr(self, 'import_group'):
                    self.import_group.setVisible(True)
                
                # Update statistics
                self._update_statistics()
            else:
                mode_text = lang.get('armory_settings.mode_info_internal', default="Mode actuel : Base de données interne (lecture seule)")
                self.mode_info_label.setText(mode_text)
                self.mode_info_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
                
                # Hide stats, actions and import groups (only if they exist)
                if hasattr(self, 'stats_group'):
                    self.stats_group.setVisible(False)
                if hasattr(self, 'actions_group'):
                    self.actions_group.setVisible(False)
                if hasattr(self, 'import_group'):
                    self.import_group.setVisible(False)
                
        except Exception as e:
            logging.error(f"Error updating database mode: {e}", exc_info=True)
    
    def _update_statistics(self):
        """Update database statistics"""
        try:
            stats = self.db_manager.get_statistics()
            
            # Internal count
            internal_count = stats.get("internal_count", 0)
            self.internal_count_label.setText(str(internal_count))
            self.internal_count_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Personal count
            personal_count = stats.get("personal_count", -1)
            if personal_count >= 0:
                self.personal_count_label.setText(str(personal_count))
                self.personal_count_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            else:
                not_available = lang.get('armory_settings.stats_not_available', default="Non disponible")
                self.personal_count_label.setText(not_available)
                self.personal_count_label.setStyleSheet("color: #888;")
            
            # User added count
            user_added = stats.get("user_added_count", -1)
            if user_added >= 0:
                self.user_added_label.setText(str(user_added))
                self.user_added_label.setStyleSheet("color: #2196F3; font-weight: bold;")
            else:
                not_available = lang.get('armory_settings.stats_not_available', default="Non disponible")
                self.user_added_label.setText(not_available)
                self.user_added_label.setStyleSheet("color: #888;")
                
        except Exception as e:
            logging.error(f"Error updating statistics: {e}", exc_info=True)
    
    def _on_personal_db_toggled(self, checked: bool):
        """Handle personal database checkbox toggle"""
        try:
            if checked:
                # Check if personal database file exists
                armor_path = self.config_manager.config.get("folders", {}).get("armor")
                if not armor_path:
                    armor_path = self.path_manager.get_app_root() / "Armory"
                
                personal_db_path = Path(armor_path) / "items_database.json"
                
                if not personal_db_path.exists():
                    # Create personal database
                    stats = self.db_manager.get_statistics()
                    internal_count = stats.get("internal_count", 0)
                    
                    title = lang.get('armory_settings.create_db_title', default="Créer la base personnelle")
                    message = lang.get('armory_settings.create_db_message', 
                        default="Voulez-vous créer votre base de données personnelle ?\nCeci copiera la base interne ({internal_count} items) dans votre dossier Armory.")
                    message = message.replace("{internal_count}", str(internal_count))
                    
                    reply = QMessageBox.question(self, title, message, 
                                                QMessageBox.Yes | QMessageBox.No)
                    
                    if reply == QMessageBox.Yes:
                        success, result = self.db_manager.create_personal_database()
                        
                        if success:
                            # Reload config to reflect changes made by db_manager
                            self.config_manager.load_config()
                            
                            success_title = lang.get('armory_settings.create_db_success_title', default="Base créée")
                            success_message = lang.get('armory_settings.create_db_success_message',
                                default="Base de données personnelle créée avec succès\nEmplacement : {path}")
                            success_message = success_message.replace("{path}", result)
                            
                            QMessageBox.information(self, success_title, success_message)
                            
                            # Update UI to show stats/actions/import sections
                            self._update_armory_database_mode()
                        else:
                            error_title = lang.get('armory_settings.create_db_error_title', default="Erreur de création")
                            error_message = lang.get('armory_settings.create_db_error_message',
                                default="Impossible de créer la base de données personnelle :\n{error}")
                            error_message = error_message.replace("{error}", result)
                            
                            QMessageBox.critical(self, error_title, error_message)
                            
                            # Uncheck checkbox
                            self.personal_db_check.setChecked(False)
                    else:
                        # User cancelled, uncheck checkbox
                        self.personal_db_check.setChecked(False)
                else:
                    # Database file exists, just enable personal database mode
                    self.config_manager.config.setdefault('armory', {})['use_personal_database'] = True
                    self.config_manager.save_config()
                    self._update_armory_database_mode()
            else:
                # Disable personal database mode (switch to internal)
                self.config_manager.config.setdefault('armory', {})['use_personal_database'] = False
                self.config_manager.save_config()
                self._update_armory_database_mode()
                
        except Exception as e:
            logging.error(f"Error toggling personal database: {e}", exc_info=True)
            self.personal_db_check.setChecked(not checked)
    
    def _reset_personal_database(self):
        """Reset personal database to internal copy"""
        try:
            stats = self.db_manager.get_statistics()
            user_count = stats.get("user_added_count", 0)
            internal_count = stats.get("internal_count", 0)
            
            title = lang.get('armory_settings.reset_confirm_title', default="Confirmer la réinitialisation")
            message = lang.get('armory_settings.reset_confirm_message',
                default="Êtes-vous sûr de vouloir réinitialiser votre base de données personnelle ?\n\n"
                       "Ceci supprimera tous vos items ajoutés manuellement ({user_count} items) "
                       "et restaurera la base interne ({internal_count} items).\n\n"
                       "Cette action est irréversible.")
            message = message.replace("{user_count}", str(user_count))
            message = message.replace("{internal_count}", str(internal_count))
            
            reply = QMessageBox.warning(self, title, message,
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success, result = self.db_manager.reset_personal_database()
                
                if success:
                    success_title = lang.get('armory_settings.reset_success_title', default="Base réinitialisée")
                    success_message = lang.get('armory_settings.reset_success_message',
                        default="Base de données personnelle réinitialisée avec succès")
                    
                    QMessageBox.information(self, success_title, success_message)
                    
                    # Update statistics
                    self._update_statistics()
                else:
                    error_title = lang.get('armory_settings.reset_error_title', default="Erreur de réinitialisation")
                    error_message = lang.get('armory_settings.reset_error_message',
                        default="Impossible de réinitialiser la base de données :\n{error}")
                    error_message = error_message.replace("{error}", result)
                    
                    QMessageBox.critical(self, error_title, error_message)
                    
        except Exception as e:
            logging.error(f"Error resetting personal database: {e}", exc_info=True)
            if hasattr(self, 'armory_items_label'):
                self.armory_items_label.setText("Erreur")
                self.armory_items_label.setStyleSheet("color: #f44336;")
    
    # === SUPERADMIN METHODS ===
    
    def _select_template_files(self):
        """Select multiple .txt template files"""
        try:
            title = lang.get('superadmin.select_files_title', 
                default="Sélectionner les fichiers templates")
            file_filter = "Template files (*.txt);;All files (*.*)"
            
            files, _ = QFileDialog.getOpenFileNames(self, title, "", file_filter)
            
            if files:
                self.superadmin_selected_files = files
                count = len(files)
                files_text = lang.get('superadmin.files_selected', 
                    default="{count} fichier(s) sélectionné(s)")
                self.superadmin_files_label.setText(files_text.replace("{count}", str(count)))
                self.superadmin_files_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            else:
                self.superadmin_selected_files = []
                self.superadmin_files_label.setText(
                    lang.get('superadmin.no_files_selected', 
                        default="Aucun fichier sélectionné")
                )
                self.superadmin_files_label.setStyleSheet("color: #888; font-style: italic;")
                
        except Exception as e:
            logging.error(f"Error selecting template files: {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Impossible de sélectionner les fichiers:\n{e}")
    
    def _open_mass_import_monitor(self):
        """Open Database Management Tools window"""
        try:
            from PySide6.QtWidgets import QApplication
            from UI.mass_import_monitor import MassImportMonitor
            
            # Create and show Database Management Tools
            monitor = MassImportMonitor(self)
            
            # Pass default settings to monitor (using default values since widgets were removed)
            monitor.set_default_options(
                realm=None,  # Auto-detection
                merge=True,
                remove_duplicates=True,
                auto_backup=True,
                path_manager=self.path_manager
            )
            
            monitor.show()
            QApplication.processEvents()
            
        except Exception as e:
            logging.error(f"Error opening Database Management Tools: {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture de Database Management Tools:\n{e}")
    
    def _refresh_superadmin_stats(self):
        """Refresh SuperAdmin statistics display"""
        try:
            from Functions.superadmin_tools import SuperAdminTools
            superadmin = SuperAdminTools(self.path_manager)
            
            stats = superadmin.get_database_stats()
            
            self.superadmin_stats_total.setText(str(stats.get("total_items", 0)))
            self.superadmin_stats_albion.setText(str(stats.get("albion", 0)))
            self.superadmin_stats_hibernia.setText(str(stats.get("hibernia", 0)))
            self.superadmin_stats_midgard.setText(str(stats.get("midgard", 0)))
            self.superadmin_stats_all_realms.setText(str(stats.get("all_realms", 0)))
            
            file_size_kb = stats.get("file_size", 0) / 1024
            self.superadmin_stats_file_size.setText(f"{file_size_kb:.1f} KB")
            
            last_updated = stats.get("last_updated", 
                lang.get('superadmin.stats_not_available', default="Non disponible"))
            self.superadmin_stats_last_updated.setText(last_updated)
            
        except Exception as e:
            logging.error(f"Error refreshing SuperAdmin stats: {e}", exc_info=True)
            self.superadmin_stats_total.setText("0")
            self.superadmin_stats_albion.setText("0")
            self.superadmin_stats_hibernia.setText("0")
            self.superadmin_stats_midgard.setText("0")
            self.superadmin_stats_all_realms.setText("0")
    
    def _clean_duplicates(self):
        """Clean duplicate items from source database"""
        try:
            # Confirmation dialog
            title = lang.get('superadmin.clean_confirm_title', 
                default="Confirmer le nettoyage")
            message = lang.get('superadmin.clean_confirm_message',
                default="Voulez-vous nettoyer les doublons de la base source ?\n\n"
                       "Ceci supprimera tous les items avec le même nom + royaume.\n"
                       "Une sauvegarde sera créée automatiquement.")
            
            reply = QMessageBox.question(self, title, message,
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply != QMessageBox.Yes:
                return
            
            # Import SuperAdminTools
            from Functions.superadmin_tools import SuperAdminTools
            superadmin = SuperAdminTools(self.path_manager)
            
            # Execute cleaning
            success, message, removed_count = superadmin.clean_duplicates()
            
            # Show result
            if success:
                removed_label = lang.get('superadmin.clean_removed_count', default="Items supprimés")
                result_message = message + f"\n\n{removed_label}: {removed_count}"
                QMessageBox.information(self,
                    lang.get('superadmin.clean_success_title', 
                        default="Nettoyage réussi"),
                    result_message
                )
                
                # Refresh statistics
                self._refresh_superadmin_stats()
            else:
                QMessageBox.critical(self,
                    lang.get('superadmin.clean_error_title', 
                        default="Erreur de nettoyage"),
                    message
                )
                
        except Exception as e:
            logging.error(f"Error cleaning duplicates: {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Erreur lors du nettoyage:\n{e}")
    
    def _refresh_all_items(self):
        """Refresh all items in the source database from Eden"""
        try:
            # 🔧 DEBUG MODE: Demander si on veut filtrer des items spécifiques
            from PySide6.QtWidgets import QInputDialog
            
            filter_reply = QMessageBox.question(
                self,
                "🔧 Mode Debug",
                "Voulez-vous rafraîchir UNIQUEMENT des items spécifiques ?\n\n"
                "✅ OUI = Sélection manuelle d'items (pour debug)\n"
                "❌ NON = Rafraîchir TOUS les items (30+ items, plusieurs minutes)",
                QMessageBox.Yes | QMessageBox.No
            )
            
            item_filter = None
            if filter_reply == QMessageBox.Yes:
                # Mode DEBUG: Demander les noms des items
                items_text, ok = QInputDialog.getText(
                    self,
                    "🔧 Sélection d'items",
                    "Entrez les noms des items à rafraîchir (séparés par des virgules) :\n\n"
                    "Exemples :\n"
                    "• Cloth Cap\n"
                    "• Cudgel of the Undead, Soulbinder's Belt\n"
                    "• Ring of the Azure\n\n"
                    "⚠️ Respectez la casse exacte (majuscules/minuscules)"
                )
                
                if not ok or not items_text.strip():
                    QMessageBox.information(self, "Annulé", "Opération annulée.")
                    return
                
                # Parser les noms d'items
                item_filter = [name.strip() for name in items_text.split(',') if name.strip()]
                
                if not item_filter:
                    QMessageBox.warning(self, "Erreur", "Aucun item valide saisi.")
                    return
                
                # Confirmation avec liste des items
                confirm_msg = f"Items sélectionnés ({len(item_filter)}) :\n\n"
                confirm_msg += "\n".join(f"• {name}" for name in item_filter)
                confirm_msg += "\n\nContinuer ?"
                
                confirm_reply = QMessageBox.question(self, "Confirmer", confirm_msg)
                if confirm_reply != QMessageBox.Yes:
                    return
            
            # Confirmation dialog
            title = lang.get('superadmin.refresh_confirm_title', 
                default="Confirmer le rafraîchissement")
            
            if item_filter:
                message = f"Rafraîchissement de {len(item_filter)} item(s) sélectionné(s).\n\n"
                message += "Items à traiter :\n" + "\n".join(f"• {name}" for name in item_filter)
                message += "\n\n⚠️ Une sauvegarde sera créée automatiquement."
            else:
                message = lang.get('superadmin.refresh_confirm_message',
                    default="Voulez-vous rafraîchir tous les items de la base source ?\n\n"
                           "Ceci va re-scraper tous les items depuis Eden Herald pour mettre à jour:\n"
                           "• Model ID (pour rendu 3D futur)\n"
                           "• DPS, Speed, Damage Type (armes)\n"
                           "• Type, Slot (équipement)\n"
                           "• Prix et zone marchand\n\n"
                           "⚠️ Cette opération peut prendre plusieurs minutes.\n"
                           "Une sauvegarde sera créée automatiquement.")
            
            reply = QMessageBox.question(self, title, message,
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply != QMessageBox.Yes:
                return
            
            # Create progress dialog
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt
            
            progress = QProgressDialog(
                lang.get('superadmin.refresh_progress_description', 
                    default="Rafraîchissement des items en cours..."),
                lang.get('superadmin.refresh_progress_cancel', default="Annuler"),
                0, 100, self
            )
            progress.setWindowTitle(lang.get('superadmin.refresh_progress_title', 
                default="Rafraîchissement en cours"))
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()
            QApplication.processEvents()
            
            # Progress callback
            def update_progress(current, total, item_name):
                progress.setMaximum(total)
                progress.setValue(current)
                progress.setLabelText(
                    f"{lang.get('superadmin.refresh_progress_description', default='Rafraîchissement des items en cours...')}\n\n"
                    f"Item {current}/{total}: {item_name}"
                )
                QApplication.processEvents()
                
                # Check for cancellation
                if progress.wasCanceled():
                    raise InterruptedError("User cancelled refresh")
            
            # Import SuperAdminTools
            logging.info("REFRESH: Importing SuperAdminTools...")
            from Functions.superadmin_tools import SuperAdminTools
            logging.info("REFRESH: Creating SuperAdminTools instance...")
            superadmin = SuperAdminTools(self.path_manager)
            logging.info(f"REFRESH: SuperAdminTools initialized with source_db_path={superadmin.source_db_path}")
            
            # Execute refresh
            try:
                logging.info(f"REFRESH: Calling refresh_all_items with filter={item_filter}...")
                success, message, stats = superadmin.refresh_all_items(
                    progress_callback=update_progress,
                    item_filter=item_filter  # None = tous les items, ou liste spécifique
                )
                logging.info(f"REFRESH: Result - success={success}, stats={stats}")
            except InterruptedError:
                progress.close()
                QMessageBox.information(self,
                    lang.get('superadmin.refresh_cancelled_title', default="Rafraîchissement annulé"),
                    lang.get('superadmin.refresh_cancelled_message', 
                        default="Le rafraîchissement a été annulé.\n\n"
                               "Les items traités avant l'annulation ont été sauvegardés.")
                )
                # Refresh statistics anyway
                self._refresh_superadmin_stats()
                return
            
            progress.close()
            
            # Show result
            if success:
                stats_text = f"\n\n{lang.get('superadmin.stats_title', default='Statistiques')}:\n"
                stats_text += f"• {lang.get('superadmin.refresh_stats_total', default='Total items')}: {stats.get('total_items', 0)}\n"
                stats_text += f"• {lang.get('superadmin.refresh_stats_updated', default='Mis à jour')}: {stats.get('updated', 0)}\n"
                stats_text += f"• {lang.get('superadmin.refresh_stats_skipped', default='Inchangés')}: {stats.get('skipped', 0)}\n"
                stats_text += f"• {lang.get('superadmin.refresh_stats_failed', default='Échecs')}: {stats.get('failed', 0)}\n\n"
                
                fields = stats.get('fields_updated', {})
                stats_text += f"{lang.get('superadmin.refresh_fields_updated', default='Champs mis à jour')}:\n"
                stats_text += f"• Model: {fields.get('model', 0)}\n"
                stats_text += f"• DPS: {fields.get('dps', 0)}\n"
                stats_text += f"• Speed: {fields.get('speed', 0)}\n"
                stats_text += f"• Damage Type: {fields.get('damage_type', 0)}\n"
                stats_text += f"• Type: {fields.get('type', 0)}\n"
                stats_text += f"• Slot: {fields.get('slot', 0)}"
                
                QMessageBox.information(self,
                    lang.get('superadmin.refresh_success_title', 
                        default="Rafraîchissement réussi"),
                    message + stats_text
                )
                
                # Refresh statistics
                self._refresh_superadmin_stats()
            else:
                QMessageBox.critical(self,
                    lang.get('superadmin.refresh_error_title', 
                        default="Erreur de rafraîchissement"),
                    message
                )
                
        except Exception as e:
            logging.error(f"Error refreshing items: {e}", exc_info=True)
            QMessageBox.critical(self, 
                lang.get("error_title", default="Erreur"), 
                lang.get("superadmin.refresh_error_message", 
                    default="Erreur lors du rafraîchissement:\n{error}").replace("{error}", str(e))
            )
    
    def _open_database_editor(self):
        """Open Database Editor dialog for direct database editing"""
        try:
            from UI.database_editor_dialog import DatabaseEditorDialog
            
            dialog = DatabaseEditorDialog(self, self.path_manager)
            
            # Connect signal to refresh stats when database is modified
            dialog.database_modified.connect(self._refresh_superadmin_stats)
            
            dialog.exec()
            
        except Exception as e:
            logging.error(f"Error opening database editor: {e}", exc_info=True)
            QMessageBox.critical(self, 
                lang.get("error_title", default="Erreur"),
                f"Erreur lors de l'ouverture de l'éditeur:\n{str(e)}"
            )



