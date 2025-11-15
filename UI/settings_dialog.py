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
        char_path_layout = QHBoxLayout()
        char_path_layout.addWidget(self.char_path_edit)
        char_path_layout.addWidget(browse_char_button)
        paths_layout.addRow(lang.get("config_path_label"), char_path_layout)
        
        # Config Path
        self.config_path_edit = QLineEdit()
        browse_config_button = QPushButton(lang.get("browse_button"))
        browse_config_button.clicked.connect(self._browse_config_folder)
        config_path_layout = QHBoxLayout()
        config_path_layout.addWidget(self.config_path_edit)
        config_path_layout.addWidget(browse_config_button)
        paths_layout.addRow(lang.get("config_file_path_label"), config_path_layout)
        
        # Armor Path
        self.armor_path_edit = QLineEdit()
        browse_armor_button = QPushButton(lang.get("browse_button"))
        browse_armor_button.clicked.connect(self._browse_armor_folder)
        armor_path_layout = QHBoxLayout()
        armor_path_layout.addWidget(self.armor_path_edit)
        armor_path_layout.addWidget(browse_armor_button)
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
        cookies_path_layout = QHBoxLayout()
        cookies_path_layout.addWidget(self.cookies_path_edit)
        cookies_path_layout.addWidget(browse_cookies_button)
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
        """Page 4: Backup Settings"""
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
        
        # Info: This page will be populated with backup settings
        # For now, show a placeholder
        info_label = QLabel(
            "🚧 " + lang.get("settings_backup_placeholder",
                           default="Les paramètres de sauvegarde sont gérés dans le menu Outils > Sauvegardes.\n\n"
                                  "Cette section sera développée dans une future version.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: palette(alternate-base); padding: 20px; border-radius: 5px;")
        layout.addWidget(info_label)
        
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
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(browse_log_button)
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
            line_edit.setText(directory)
            
    def _browse_character_folder(self):
        self._browse_folder(self.char_path_edit, "select_folder_dialog_title")
        
    def _browse_config_folder(self):
        self._browse_folder(self.config_path_edit, "select_config_folder_dialog_title")
        
    def _browse_log_folder(self):
        self._browse_folder(self.log_path_edit, "select_log_folder_dialog_title")
        
    def _browse_armor_folder(self):
        self._browse_folder(self.armor_path_edit, "select_folder_dialog_title")
        
    def _browse_cookies_folder(self):
        self._browse_folder(self.cookies_path_edit, "select_folder_dialog_title")
        
    # === Settings Load/Save ===
    
    def _load_settings(self):
        """Load current settings into the UI"""
        # Paths
        self.char_path_edit.setText(config.get("character_folder") or get_character_dir())
        self.char_path_edit.setCursorPosition(0)
        
        self.config_path_edit.setText(config.get("config_folder") or get_config_dir())
        self.config_path_edit.setCursorPosition(0)
        
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
