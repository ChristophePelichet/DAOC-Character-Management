"""
Modern Settings Dialog with Navigation Sidebar
Separated from dialogs.py for better maintainability
"""

import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QDialogButtonBox,
    QFileDialog, QListWidget, QStackedWidget, QWidget, QListWidgetItem,
    QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir
from Functions.character_manager import get_character_dir
from Functions.logging_manager import get_log_dir
from Functions.path_manager import get_armor_dir


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
        self._create_debug_page()
        
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
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
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
            ("📁", lang.get("settings_nav_general", default="Général")),
            ("🎨", lang.get("settings_nav_themes", default="Thèmes")),
            ("🚀", lang.get("settings_nav_startup", default="Démarrage")),
            ("🏛️", lang.get("settings_nav_columns", default="Colonnes")),
            ("🌐", lang.get("settings_nav_herald", default="Herald Eden")),
            ("💾", lang.get("settings_nav_backup", default="Sauvegardes")),
            ("🐛", lang.get("settings_nav_debug", default="Debug")),
        ]
        
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
        
        # Armor Path
        self.armor_path_edit = QLineEdit()
        browse_armor_button = QPushButton(lang.get("browse_button"))
        browse_armor_button.clicked.connect(self._browse_armor_folder)
        move_armor_button = QPushButton("📦 " + lang.get("move_folder_button", default="Déplacer"))
        move_armor_button.clicked.connect(lambda: self._move_folder(self.armor_path_edit, "armor_folder", lang.get("config_armor_path_label")))
        move_armor_button.setToolTip(lang.get("move_folder_tooltip", default="Déplacer le dossier et son contenu vers un nouvel emplacement"))
        open_armor_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
        open_armor_folder_button.clicked.connect(self._open_armor_folder)
        armor_path_layout = QHBoxLayout()
        armor_path_layout.addWidget(self.armor_path_edit)
        armor_path_layout.addWidget(browse_armor_button)
        armor_path_layout.addWidget(move_armor_button)
        armor_path_layout.addWidget(open_armor_folder_button)
        paths_layout.addRow(lang.get("config_armor_path_label"), armor_path_layout)
        
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
        visibility_config = config.get("column_visibility", {})
        
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
        """Page 3: Herald Eden Settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel(lang.get("settings_herald_title", default="Herald Eden"))
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
        
        # === Cookies Path ===
        cookies_group = QGroupBox("🍪 " + lang.get("config_cookies_group_title", 
                                                    default="Chemin des cookies"))
        cookies_layout = QFormLayout()
        
        self.cookies_path_edit = QLineEdit()
        browse_cookies_button = QPushButton(lang.get("browse_button"))
        browse_cookies_button.clicked.connect(self._browse_cookies_folder)
        move_cookies_button = QPushButton("📦 " + lang.get("move_folder_button", default="Déplacer"))
        move_cookies_button.clicked.connect(lambda: self._move_folder(self.cookies_path_edit, "cookies_folder", lang.get("config_cookies_path_label")))
        move_cookies_button.setToolTip(lang.get("move_folder_tooltip", default="Déplacer le dossier et son contenu vers un nouvel emplacement"))
        open_cookies_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
        open_cookies_folder_button.clicked.connect(self._open_cookies_folder)
        cookies_path_layout = QHBoxLayout()
        cookies_path_layout.addWidget(self.cookies_path_edit)
        cookies_path_layout.addWidget(browse_cookies_button)
        cookies_path_layout.addWidget(move_cookies_button)
        cookies_path_layout.addWidget(open_cookies_folder_button)
        cookies_layout.addRow(lang.get("config_cookies_path_label"), cookies_path_layout)
        
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)
        
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
        
        # Info box
        info_label = QLabel(
            "💡 " + lang.get("settings_herald_info",
                           default="Pour gérer vos cookies Herald, utilisez le bouton 'Gérer...' "
                                  "dans la section Herald Eden de la fenêtre principale.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: palette(alternate-base); padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        
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
        self.backup_enabled_check.setChecked(config.get("backup_enabled", True))
        enable_compress_layout.addWidget(self.backup_enabled_check)
        
        enable_compress_layout.addSpacing(30)
        
        self.backup_compress_check = QCheckBox(lang.get("backup_compress_label", default="Compresser les sauvegardes (ZIP)"))
        self.backup_compress_check.setChecked(config.get("backup_compress", True))
        self.backup_compress_check.setToolTip(lang.get("backup_compress_tooltip", default="Réduit la taille des sauvegardes"))
        enable_compress_layout.addWidget(self.backup_compress_check)
        
        enable_compress_layout.addStretch()
        chars_layout.addLayout(enable_compress_layout)
        chars_layout.addSpacing(10)
        
        # Backup path
        path_form = QFormLayout()
        self.backup_path_edit = QLineEdit()
        backup_path = config.get("backup_path")
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
        
        # Size limit
        size_form = QFormLayout()
        self.backup_size_limit_edit = QLineEdit()
        self.backup_size_limit_edit.setText(str(config.get("backup_size_limit_mb", 20)))
        self.backup_size_limit_edit.setMaximumWidth(80)
        
        size_limit_layout = QHBoxLayout()
        size_limit_layout.addWidget(self.backup_size_limit_edit)
        size_limit_layout.addWidget(QLabel("MB"))
        size_limit_layout.addWidget(QLabel(lang.get("backup_size_limit_tooltip", default="Limite totale")))
        size_limit_layout.addStretch()
        size_form.addRow(lang.get("backup_size_limit_label", default="Limite de taille"), size_limit_layout)
        chars_layout.addLayout(size_form)
        chars_layout.addSpacing(10)
        
        # Info - Total and Last Backup side by side
        info_layout = QHBoxLayout()
        
        # Total backups
        total_backups = len(backup_info["backups"])
        total_label_text = QLabel(lang.get("backup_total_label", default="Nombre de sauvegardes") + " :")
        self.backup_total_label = QLabel(f"{total_backups}")
        self.backup_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        info_layout.addWidget(total_label_text)
        info_layout.addWidget(self.backup_total_label)
        
        info_layout.addSpacing(30)
        
        # Last backup date
        last_backup_date = config.get("backup_last_date")
        if last_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_backup_date)
                last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_backup_str = "N/A"
        else:
            last_backup_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
        last_label_text = QLabel(lang.get("backup_last_label", default="Dernière sauvegarde") + " :")
        self.backup_last_label = QLabel(last_backup_str)
        self.backup_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        info_layout.addWidget(last_label_text)
        info_layout.addWidget(self.backup_last_label)
        
        info_layout.addStretch()
        chars_layout.addLayout(info_layout)
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
        self.cookies_backup_enabled_check.setChecked(config.get("cookies_backup_enabled", True))
        cookies_enable_compress_layout.addWidget(self.cookies_backup_enabled_check)
        
        cookies_enable_compress_layout.addSpacing(30)
        
        self.cookies_backup_compress_check = QCheckBox(lang.get("backup_compress_label", default="Compresser les sauvegardes (ZIP)"))
        self.cookies_backup_compress_check.setChecked(config.get("cookies_backup_compress", True))
        self.cookies_backup_compress_check.setToolTip(lang.get("backup_compress_tooltip", default="Réduit la taille des sauvegardes"))
        cookies_enable_compress_layout.addWidget(self.cookies_backup_compress_check)
        
        cookies_enable_compress_layout.addStretch()
        cookies_layout.addLayout(cookies_enable_compress_layout)
        cookies_layout.addSpacing(10)
        
        # Cookies backup path
        cookies_path_form = QFormLayout()
        self.cookies_backup_path_edit = QLineEdit()
        cookies_backup_path = config.get("cookies_backup_path")
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
        
        # Cookies info - Total and Last Backup side by side
        cookies_info_layout = QHBoxLayout()
        
        # Total cookies backups
        total_cookies_backups = len(cookies_info["backups"])
        cookies_total_label_text = QLabel(lang.get("backup_total_label", default="Nombre de sauvegardes") + " :")
        self.cookies_total_label = QLabel(f"{total_cookies_backups}")
        self.cookies_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        cookies_info_layout.addWidget(cookies_total_label_text)
        cookies_info_layout.addWidget(self.cookies_total_label)
        
        cookies_info_layout.addSpacing(30)
        
        # Last cookies backup date
        last_cookies_backup_date = config.get("cookies_backup_last_date")
        if last_cookies_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_cookies_backup_date)
                last_cookies_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_cookies_str = "N/A"
        else:
            last_cookies_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
        cookies_last_label_text = QLabel(lang.get("backup_last_label", default="Dernière sauvegarde") + " :")
        self.cookies_last_label = QLabel(last_cookies_str)
        self.cookies_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        cookies_info_layout.addWidget(cookies_last_label_text)
        cookies_info_layout.addWidget(self.cookies_last_label)
        
        cookies_info_layout.addStretch()
        cookies_layout.addLayout(cookies_info_layout)
        cookies_layout.addSpacing(15)
        
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)
        
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
        self._browse_folder(self.char_path_edit, "select_folder_dialog_title")
        
    def _browse_log_folder(self):
        self._browse_folder(self.log_path_edit, "select_log_folder_dialog_title")
        
    def _browse_armor_folder(self):
        self._browse_folder(self.armor_path_edit, "select_folder_dialog_title")
        
    def _browse_cookies_folder(self):
        self._browse_folder(self.cookies_path_edit, "select_folder_dialog_title")
    
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
    
    def _backup_now(self):
        """Execute characters backup now"""
        from PySide6.QtWidgets import QMessageBox
        try:
            result = self.backup_manager.create_backup()
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
            result = self.backup_manager.backup_cookies()
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
    
    def _open_character_folder(self):
        """Open characters folder"""
        import subprocess
        char_path = self.char_path_edit.text()
        if os.path.exists(char_path):
            subprocess.Popen(f'explorer "{char_path}"')
    
    def _open_armor_folder(self):
        """Open armor folder"""
        import subprocess
        armor_path = self.armor_path_edit.text()
        if os.path.exists(armor_path):
            subprocess.Popen(f'explorer "{armor_path}"')
    
    def _open_cookies_folder(self):
        """Open cookies folder"""
        import subprocess
        cookies_path = self.cookies_path_edit.text()
        if os.path.exists(cookies_path):
            subprocess.Popen(f'explorer "{cookies_path}"')
    
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
        if os.path.exists(backup_path):
            subprocess.Popen(f'explorer "{backup_path}"')
    
    def _open_cookies_backup_folder(self):
        """Open cookies backup folder"""
        import subprocess
        cookies_backup_path = self.cookies_backup_path_edit.text()
        if os.path.exists(cookies_backup_path):
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
            "armor_folder": "Armor",
            "log_folder": "Logs",
            "cookies_folder": "Cookies",
            "backup_path": "Backups",
            "cookies_backup_path": "Backups"
        }
        
        folder_name = folder_names.get(config_key, "Data")
        
        # Special handling for backup folders: always use /Backups/ intermediate folder
        if config_key in ["backup_path", "cookies_backup_path"]:
            # For backups: parent_dir/Backups/subfolder_type
            subfolder_type = "Characters" if config_key == "backup_path" else "Cookies"
            backup_parent = os.path.join(parent_dir, "Backups")
            destination = os.path.join(backup_parent, subfolder_type)
        else:
            destination = os.path.join(parent_dir, folder_name)
        
        # Check if destination already exists
        if os.path.exists(destination):
            reply = QMessageBox.question(
                self,
                lang.get("warning_title", default="Attention"),
                f"{lang.get('move_folder_destination_exists', default='Le dossier existe déjà à la destination.')}\n\n"
                f"{destination}\n\n"
                f"{lang.get('move_folder_use_existing', default='Voulez-vous utiliser ce dossier existant ?')}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Use existing folder - just update the config
                line_edit.setText(destination)
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
                # Copy the folder
                shutil.copytree(current_path, destination)
                
                # Update the line edit
                line_edit.setText(destination)
                
                # Ask if user wants to delete old folder
                delete_reply = QMessageBox.question(
                    self,
                    lang.get("move_folder_delete_title", default="Supprimer l'ancien dossier ?"),
                    f"{lang.get('move_folder_delete_message', default='Le dossier a été copié avec succès. Voulez-vous supprimer l ancien dossier ?')}\n\n"
                    f"{current_path}",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if delete_reply == QMessageBox.Yes:
                    shutil.rmtree(current_path)
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
        self.char_path_edit.setText(config.get("character_folder") or get_character_dir())
        self.char_path_edit.setCursorPosition(0)
        
        # Config folder is not configurable - always next to executable
        
        self.log_path_edit.setText(config.get("log_folder") or get_log_dir())
        self.log_path_edit.setCursorPosition(0)
        
        self.armor_path_edit.setText(config.get("armor_folder") or get_armor_dir())
        self.armor_path_edit.setCursorPosition(0)
        
        self.cookies_path_edit.setText(config.get("cookies_folder") or get_config_dir())
        self.cookies_path_edit.setCursorPosition(0)
        
        # General settings
        self.debug_mode_check.setChecked(config.get("debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("show_debug_window", False))
        self.disable_disclaimer_check.setChecked(config.get("disable_disclaimer", False))
        
        # Defaults
        self.default_server_combo.setCurrentText(config.get("default_server", ""))
        self.default_season_combo.setCurrentText(config.get("default_season", ""))
        self.default_realm_combo.setCurrentText(config.get("default_realm", ""))
        
        # Language
        current_lang_code = config.get("language", "fr")
        current_lang_name = self.available_languages.get(current_lang_code, "Français")
        self.language_combo.setCurrentText(current_lang_name)
        
        # Theme
        current_theme = config.get("theme", "default")
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
            
        # Font scale
        current_font_scale = config.get("font_scale", 1.0)
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
        self.manual_column_resize_check.setChecked(config.get("manual_column_resize", True))
        
        # Browser
        self.browser_combo.setCurrentText(config.get("preferred_browser", "Chrome"))
        self.allow_browser_download_check.setChecked(config.get("allow_browser_download", False))
