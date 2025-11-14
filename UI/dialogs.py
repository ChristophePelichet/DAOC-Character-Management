"""
Dialog windows for the DAOC Character Manager application.
"""

import re
import os
import sys
import logging
from datetime import datetime

# Fix for PyInstaller --noconsole mode: sys.stderr can be None
if sys.stderr is None:
    sys.stderr = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel, 
    QPushButton, QLineEdit, QComboBox, QCheckBox, QSlider, QMessageBox,
    QDialogButtonBox, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget, QTextEdit, QApplication, QProgressBar, QMenu, QGridLayout, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QBrush, QColor, QIcon, QPixmap
from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir
from Functions.character_manager import get_character_dir
from Functions.logging_manager import get_log_dir, get_logger, log_with_action, LOGGER_CHARACTER
from Functions.data_manager import DataManager
from Functions.theme_manager import get_scaled_size

# Get CHARACTER logger
logger_char = get_logger(LOGGER_CHARACTER)


class HeraldScraperWorker(QThread):
    """Worker thread pour scraper Herald sans bloquer l'interface"""
    finished = Signal(bool, object, str)  # success, data, error_msg
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        """Exécute le scraping en arrière-plan"""
        try:
            from Functions.eden_scraper import scrape_character_from_url
            from Functions.cookie_manager import CookieManager
            
            cookie_manager = CookieManager()
            success, new_data, error_msg = scrape_character_from_url(self.url, cookie_manager)
            self.finished.emit(success, new_data, error_msg)
            
        except Exception as e:
            logging.error(f"Erreur dans le worker Herald: {e}", exc_info=True)
            self.finished.emit(False, None, str(e))


class CharacterSheetWindow(QDialog):
    """Window to display character details."""
    
    def __init__(self, parent, character_data):
        super().__init__(parent)
        self.character_data = character_data
        self.parent_app = parent
        char_name = self.character_data.get('name', 'N/A')
        self.realm = self.character_data.get('realm', 'Albion')
        
        # Flag pour savoir si un scraping Herald est en cours
        self.herald_scraping_in_progress = False

        self.setWindowTitle(lang.get("character_sheet_title", name=char_name))
        self.resize(500, 400)
        
        # Enable window resizing
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setSizeGripEnabled(True)  # Add resize grip in bottom-right corner
        
        # Connecter au signal de fin de validation Herald si disponible
        if hasattr(parent, 'ui_manager') and hasattr(parent.ui_manager, 'eden_status_thread'):
            # Créer une connexion pour réactiver le bouton quand la validation se termine
            pass  # On gérera ça après la création du bouton

        # Main horizontal layout: Banner (left) + Content (right)
        main_horizontal = QHBoxLayout(self)
        
        # === LEFT SIDE: Class Banner ===
        self.banner_label = QLabel()
        self.banner_label.setMinimumWidth(150)  # Minimum width for banner
        self.banner_label.setMaximumWidth(200)  # Maximum width for banner
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.banner_label.setScaledContents(True)  # Scale to fill the label
        from PySide6.QtWidgets import QSizePolicy
        self.banner_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._update_class_banner()  # Load initial banner
        main_horizontal.addWidget(self.banner_label)
        
        # === RIGHT SIDE: All content ===
        layout = QVBoxLayout()
        
        # Eden Herald Section - EN HAUT for FACILITER the MISE À JOUR
        eden_group = QGroupBox("🌐 Eden Herald")
        eden_layout = QVBoxLayout()
        
        # URL du Herald
        url_form_layout = QFormLayout()
        self.herald_url_edit = QLineEdit()
        current_url = self.character_data.get('url', '')
        self.herald_url_edit.setText(current_url)
        self.herald_url_edit.setPlaceholderText("https://eden-daoc.net/herald?n=player&k=NomPersonnage")
        self.herald_url_edit.textChanged.connect(self.on_herald_url_changed)
        url_form_layout.addRow("URL Herald :", self.herald_url_edit)
        eden_layout.addLayout(url_form_layout)
        
        # Boutons d'action Herald
        herald_buttons_layout = QHBoxLayout()
        
        self.open_herald_button = QPushButton("🌐 Ouvrir dans le navigateur")
        self.open_herald_button.setToolTip("Ouvrir la page Herald dans le navigateur")
        self.open_herald_button.clicked.connect(self.open_herald_url)
        self.open_herald_button.setMinimumHeight(28)
        herald_buttons_layout.addWidget(self.open_herald_button)
        
        self.update_herald_button = QPushButton("🔄 Mettre à jour depuis Herald")
        self.update_herald_button.setToolTip("Récupérer et mettre à jour les données depuis Herald")
        self.update_herald_button.clicked.connect(self.update_from_herald)
        self.update_herald_button.setMinimumHeight(30)
        # Mettre en évidence the bouton of mise à jour
        self.update_herald_button.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        herald_buttons_layout.addWidget(self.update_herald_button)
        
        # Définir des stretch égaux for the deux boutons
        herald_buttons_layout.setStretch(0, 1)
        herald_buttons_layout.setStretch(1, 1)
        
        eden_layout.addLayout(herald_buttons_layout)
        eden_group.setLayout(eden_layout)
        layout.addWidget(eden_group)
        
        # Séparateur visuel
        layout.addSpacing(10)
        
        # Basic Information Section
        info_group = QGroupBox("Informations générales")
        info_layout = QFormLayout()
        
        # Editable name field with Enter key support
        self.name_edit = QLineEdit()
        self.name_edit.setText(char_name)
        self.name_edit.setPlaceholderText("Nom du personnage (Appuyez sur Entrée pour renommer)")
        self.name_edit.returnPressed.connect(self.rename_character)  # Rename on Enter key
        info_layout.addRow("Nom :", self.name_edit)
        
        # Editable realm dropdown
        self.realm_combo = QComboBox()
        from Functions.character_manager import REALMS
        self.realm_combo.addItems(REALMS)
        self.realm_combo.setCurrentText(self.realm)
        self.realm_combo.currentTextChanged.connect(self._on_realm_changed_sheet)
        info_layout.addRow("Royaume :", self.realm_combo)
        
        # Initialize DataManager for race/class data
        self.data_manager = DataManager()
        
        # Editable class dropdown (BEFORE race)
        self.class_combo = QComboBox()
        self._populate_classes_sheet()
        current_class = self.character_data.get('class', '')
        if current_class:
            # Utiliser findData for sélectionner par itemData (nom anglais) au lieu of the texte affiché
            class_index = self.class_combo.findData(current_class)
            if class_index >= 0:
                self.class_combo.setCurrentIndex(class_index)
        self.class_combo.currentTextChanged.connect(self._on_class_changed_sheet)
        info_layout.addRow(lang.get("new_char_class_prompt", default="Classe :"), self.class_combo)
        
        # Editable race dropdown (AFTER class)
        self.race_combo = QComboBox()
        self._populate_races_sheet()
        current_race = self.character_data.get('race', '')
        if current_race:
            # Utiliser findData for sélectionner par itemData (nom anglais) au lieu of the texte affiché
            race_index = self.race_combo.findData(current_race)
            if race_index >= 0:
                self.race_combo.setCurrentIndex(race_index)
        self.race_combo.currentTextChanged.connect(self._on_race_changed_sheet)
        info_layout.addRow(lang.get("new_char_race_prompt", default="Race :"), self.race_combo)
        
        # Editable level dropdown (1-50)
        self.level_combo = QComboBox()
        self.level_combo.addItems([str(i) for i in range(1, 51)])
        current_level = self.character_data.get('level', 1)
        self.level_combo.setCurrentText(str(current_level))
        info_layout.addRow("Niveau :", self.level_combo)
        
        # Editable season dropdown
        self.season_combo = QComboBox()
        from Functions.config_manager import config
        seasons = config.get("seasons", ["S1", "S2", "S3"])
        self.season_combo.addItems(seasons)
        current_season = self.character_data.get('season', 'S1')
        self.season_combo.setCurrentText(current_season)
        info_layout.addRow("Saison :", self.season_combo)
        
        # Editable server dropdown
        self.server_combo = QComboBox()
        servers = config.get("servers", ["Eden", "Blackthorn"])
        self.server_combo.addItems(servers)
        current_server = self.character_data.get('server', 'Eden')
        self.server_combo.setCurrentText(current_server)
        info_layout.addRow("Serveur :", self.server_combo)
        
        # Editable page dropdown (1-5)
        self.page_combo = QComboBox()
        self.page_combo.addItems([str(i) for i in range(1, 6)])
        current_page = self.character_data.get('page', 1)
        self.page_combo.setCurrentText(str(current_page))
        info_layout.addRow("Page :", self.page_combo)
        
        # Editable guild text field
        self.guild_edit = QLineEdit()
        self.guild_edit.setText(self.character_data.get('guild', ''))
        self.guild_edit.setPlaceholderText("Nom de la guilde")
        info_layout.addRow("Guilde :", self.guild_edit)
        
        info_group.setLayout(info_layout)
        
        # Statistics Section (renamed from Armor)
        statistics_group = QGroupBox(lang.get("armor_group_title"))
        statistics_layout = QVBoxLayout()
        
        # === RvR and PvP Sub-sections (side by side with equal width) ===
        rvr_pvp_horizontal = QHBoxLayout()
        
        # === RvR Sub-section (Captures only) ===
        rvr_subgroup = QGroupBox(lang.get("rvr_section_title"))
        rvr_subgroup.setMinimumWidth(250)
        rvr_sublayout = QVBoxLayout()
        
        # RvR Captures
        rvr_captures_form = QFormLayout()
        
        # Tower Captures
        self.tower_captures_label = QLabel("—")
        self.tower_captures_label.setStyleSheet("font-weight: bold;")
        rvr_captures_form.addRow(lang.get("tower_captures_label"), self.tower_captures_label)
        
        # Keep Captures
        self.keep_captures_label = QLabel("—")
        self.keep_captures_label.setStyleSheet("font-weight: bold;")
        rvr_captures_form.addRow(lang.get("keep_captures_label"), self.keep_captures_label)
        
        # Relic Captures
        self.relic_captures_label = QLabel("—")
        self.relic_captures_label.setStyleSheet("font-weight: bold;")
        rvr_captures_form.addRow(lang.get("relic_captures_label"), self.relic_captures_label)
        
        rvr_sublayout.addLayout(rvr_captures_form)
        
        # Load existing RvR Captures values if available
        tower_val = self.character_data.get('tower_captures')
        keep_val = self.character_data.get('keep_captures')
        relic_val = self.character_data.get('relic_captures')
        
        if tower_val is not None:
            self.tower_captures_label.setText(f"{tower_val:,}")
        if keep_val is not None:
            self.keep_captures_label.setText(f"{keep_val:,}")
        if relic_val is not None:
            self.relic_captures_label.setText(f"{relic_val:,}")
        
        rvr_subgroup.setLayout(rvr_sublayout)
        rvr_pvp_horizontal.addWidget(rvr_subgroup, 1)  # Stretch factor 1 for 50%
        
        # === PvP Sub-section (Kills with realm breakdown) ===
        pvp_subgroup = QGroupBox(lang.get("pvp_section_title"))
        pvp_subgroup.setMinimumWidth(250)
        pvp_sublayout = QVBoxLayout()
        
        # Use QGridLayout for proper alignment
        pvp_grid = QGridLayout()
        pvp_grid.setSpacing(5)
        
        # Solo Kills (row 0)
        solo_kills_label_text = QLabel(lang.get("solo_kills_label"))
        self.solo_kills_label = QLabel("—")
        self.solo_kills_label.setStyleSheet("font-weight: bold;")
        self.solo_kills_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.solo_kills_detail_label = QLabel("")
        self.solo_kills_detail_label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt; color: gray;")
        self.solo_kills_detail_label.setWordWrap(False)  # Prevent wrapping for horizontal scroll
        pvp_grid.addWidget(solo_kills_label_text, 0, 0)
        pvp_grid.addWidget(self.solo_kills_label, 0, 1)
        pvp_grid.addWidget(self.solo_kills_detail_label, 0, 2)
        
        # Deathblows (row 1)
        deathblows_label_text = QLabel(lang.get("deathblows_label"))
        self.deathblows_label = QLabel("—")
        self.deathblows_label.setStyleSheet("font-weight: bold;")
        self.deathblows_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.deathblows_detail_label = QLabel("")
        self.deathblows_detail_label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt; color: gray;")
        self.deathblows_detail_label.setWordWrap(False)  # Prevent wrapping for horizontal scroll
        pvp_grid.addWidget(deathblows_label_text, 1, 0)
        pvp_grid.addWidget(self.deathblows_label, 1, 1)
        pvp_grid.addWidget(self.deathblows_detail_label, 1, 2)
        
        # Kills (row 2)
        kills_label_text = QLabel(lang.get("kills_label"))
        self.kills_label = QLabel("—")
        self.kills_label.setStyleSheet("font-weight: bold;")
        self.kills_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.kills_detail_label = QLabel("")
        self.kills_detail_label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt; color: gray;")
        self.kills_detail_label.setWordWrap(False)  # Prevent wrapping for horizontal scroll
        pvp_grid.addWidget(kills_label_text, 2, 0)
        pvp_grid.addWidget(self.kills_label, 2, 1)
        pvp_grid.addWidget(self.kills_detail_label, 2, 2)
        
        # Add stretch to column 3 to push everything to the left
        pvp_grid.setColumnStretch(3, 1)
        
        pvp_sublayout.addLayout(pvp_grid)
        
        # Load existing PvP values if available (with realm breakdown)
        solo_kills_val = self.character_data.get('solo_kills')
        solo_kills_alb = self.character_data.get('solo_kills_alb')
        solo_kills_hib = self.character_data.get('solo_kills_hib')
        solo_kills_mid = self.character_data.get('solo_kills_mid')
        
        deathblows_val = self.character_data.get('deathblows')
        deathblows_alb = self.character_data.get('deathblows_alb')
        deathblows_hib = self.character_data.get('deathblows_hib')
        deathblows_mid = self.character_data.get('deathblows_mid')
        
        kills_val = self.character_data.get('kills')
        kills_alb = self.character_data.get('kills_alb')
        kills_hib = self.character_data.get('kills_hib')
        kills_mid = self.character_data.get('kills_mid')
        
        if solo_kills_val is not None:
            self.solo_kills_label.setText(f"{solo_kills_val:,}")
            if solo_kills_alb is not None and solo_kills_hib is not None and solo_kills_mid is not None:
                self.solo_kills_detail_label.setText(
                    f'→ <span style="color: #C41E3A;">Alb</span>: {solo_kills_alb:,}  |  '
                    f'<span style="color: #228B22;">Hib</span>: {solo_kills_hib:,}  |  '
                    f'<span style="color: #4169E1;">Mid</span>: {solo_kills_mid:,}'
                )
        
        if deathblows_val is not None:
            self.deathblows_label.setText(f"{deathblows_val:,}")
            if deathblows_alb is not None and deathblows_hib is not None and deathblows_mid is not None:
                self.deathblows_detail_label.setText(
                    f'→ <span style="color: #C41E3A;">Alb</span>: {deathblows_alb:,}  |  '
                    f'<span style="color: #228B22;">Hib</span>: {deathblows_hib:,}  |  '
                    f'<span style="color: #4169E1;">Mid</span>: {deathblows_mid:,}'
                )
        
        if kills_val is not None:
            self.kills_label.setText(f"{kills_val:,}")
            if kills_alb is not None and kills_hib is not None and kills_mid is not None:
                self.kills_detail_label.setText(
                    f'→ <span style="color: #C41E3A;">Alb</span>: {kills_alb:,}  |  '
                    f'<span style="color: #228B22;">Hib</span>: {kills_hib:,}  |  '
                    f'<span style="color: #4169E1;">Mid</span>: {kills_mid:,}'
                )
        
        pvp_subgroup.setLayout(pvp_sublayout)
        rvr_pvp_horizontal.addWidget(pvp_subgroup, 1)  # Stretch factor 1 for 50%
        
        # Add the horizontal layout containing both RvR and PvP to statistics
        statistics_layout.addLayout(rvr_pvp_horizontal)
        
        # === PvE and Achievements Sub-sections (side by side with equal width) ===
        pve_achievements_horizontal = QHBoxLayout()
        
        # === PvE Sub-section ===
        pve_subgroup = QGroupBox(lang.get("pve_section_title"))
        pve_subgroup.setMinimumWidth(250)
        pve_sublayout = QVBoxLayout()
        
        # Create grid layout for 2 columns with separator
        pve_grid = QGridLayout()
        pve_grid.setHorizontalSpacing(5)
        pve_grid.setVerticalSpacing(5)
        
        # Column 1 (left)
        # Dragon Kills
        dragon_label = QLabel("🐉 " + lang.get("dragon_kills_label"))
        self.dragon_kills_value = QLabel("—")
        self.dragon_kills_value.setStyleSheet("font-weight: bold;")
        pve_grid.addWidget(dragon_label, 0, 0)
        pve_grid.addWidget(self.dragon_kills_value, 0, 1)
        
        # Mini Dragon Kills
        mini_dragon_label = QLabel("🐲 " + lang.get("mini_dragon_kills_label"))
        self.mini_dragon_kills_value = QLabel("—")
        self.mini_dragon_kills_value.setStyleSheet("font-weight: bold;")
        pve_grid.addWidget(mini_dragon_label, 1, 0)
        pve_grid.addWidget(self.mini_dragon_kills_value, 1, 1)
        
        # Epic Dungeons
        epic_dungeons_label = QLabel("🏛️ " + lang.get("epic_dungeons_label"))
        self.epic_dungeons_value = QLabel("—")
        self.epic_dungeons_value.setStyleSheet("font-weight: bold;")
        pve_grid.addWidget(epic_dungeons_label, 2, 0)
        pve_grid.addWidget(self.epic_dungeons_value, 2, 1)
        
        # Vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: gray;")
        pve_grid.addWidget(separator, 0, 2, 3, 1)  # Spans 3 rows
        
        # Column 2 (right)
        # Legion Kills
        legion_label = QLabel("👹 " + lang.get("legion_kills_label"))
        self.legion_kills_value = QLabel("—")
        self.legion_kills_value.setStyleSheet("font-weight: bold;")
        pve_grid.addWidget(legion_label, 0, 3)
        pve_grid.addWidget(self.legion_kills_value, 0, 4)
        
        # Epic Encounters
        epic_encounters_label = QLabel("⚔️ " + lang.get("epic_encounters_label"))
        self.epic_encounters_value = QLabel("—")
        self.epic_encounters_value.setStyleSheet("font-weight: bold;")
        pve_grid.addWidget(epic_encounters_label, 1, 3)
        pve_grid.addWidget(self.epic_encounters_value, 1, 4)
        
        # Sobekite
        sobekite_label = QLabel("🐊 " + lang.get("sobekite_label"))
        self.sobekite_value = QLabel("—")
        self.sobekite_value.setStyleSheet("font-weight: bold;")
        pve_grid.addWidget(sobekite_label, 2, 3)
        pve_grid.addWidget(self.sobekite_value, 2, 4)
        
        pve_sublayout.addLayout(pve_grid)
        
        # Load existing PvE values if available
        dragon_kills = self.character_data.get('dragon_kills')
        legion_kills = self.character_data.get('legion_kills')
        mini_dragon_kills = self.character_data.get('mini_dragon_kills')
        epic_encounters = self.character_data.get('epic_encounters')
        epic_dungeons = self.character_data.get('epic_dungeons')
        sobekite = self.character_data.get('sobekite')
        
        if dragon_kills is not None:
            self.dragon_kills_value.setText(f"{dragon_kills:,}")
        if legion_kills is not None:
            self.legion_kills_value.setText(f"{legion_kills:,}")
        if mini_dragon_kills is not None:
            self.mini_dragon_kills_value.setText(f"{mini_dragon_kills:,}")
        if epic_encounters is not None:
            self.epic_encounters_value.setText(f"{epic_encounters:,}")
        if epic_dungeons is not None:
            self.epic_dungeons_value.setText(f"{epic_dungeons:,}")
        if sobekite is not None:
            self.sobekite_value.setText(f"{sobekite:,}")
        
        pve_subgroup.setLayout(pve_sublayout)
        pve_achievements_horizontal.addWidget(pve_subgroup, 1)  # Stretch factor 1 for 50%
        
        # === Wealth Sub-section ===
        wealth_subgroup = QGroupBox(lang.get("wealth_section_title"))
        wealth_subgroup.setMinimumWidth(250)
        wealth_layout = QFormLayout()
        
        # Money display
        self.money_label = QLabel("—")
        self.money_label.setStyleSheet(f"font-weight: bold; font-size: {get_scaled_size(9):.1f}pt;")
        wealth_layout.addRow(lang.get("total_wealth_label"), self.money_label)
        
        # Load existing wealth value if available
        money_value = self.character_data.get('money')
        if money_value is not None:
            # Money is a string like "18p 128g", display as-is
            self.money_label.setText(str(money_value))
        
        wealth_subgroup.setLayout(wealth_layout)
        pve_achievements_horizontal.addWidget(wealth_subgroup, 1)  # Stretch factor 1 for 50%
        
        # Add the horizontal layout containing both PvE and Wealth to statistics
        statistics_layout.addLayout(pve_achievements_horizontal)
        
        # === Achievements Section (full width) ===
        achievements_group = QGroupBox(lang.get("achievements_section_title"))
        achievements_layout = QVBoxLayout()
        
        # Container for achievements (no scroll area)
        self.achievements_container_layout = QVBoxLayout()
        self.achievements_container_layout.setSpacing(3)
        self.achievements_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initial placeholder
        achievements_placeholder = QLabel("—")
        achievements_placeholder.setStyleSheet("color: gray; font-style: italic;")
        achievements_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.achievements_container_layout.addWidget(achievements_placeholder)
        self.achievements_container_layout.addStretch()
        
        achievements_layout.addLayout(self.achievements_container_layout)
        
        # Load existing achievements if available
        achievements_data = self.character_data.get('achievements', [])
        if achievements_data and len(achievements_data) > 0:
            self._update_achievements_display(achievements_data)
        
        achievements_group.setLayout(achievements_layout)
        statistics_layout.addWidget(achievements_group)
        
        # Horizontal layout for buttons (Update Stats + Info)
        buttons_layout = QHBoxLayout()
        
        # Update button for RvR/PvP/PvE/Wealth stats
        self.update_rvr_button = QPushButton(lang.get("update_rvr_pvp_button"))
        self.update_rvr_button.setToolTip(lang.get("update_rvr_pvp_tooltip"))
        self.update_rvr_button.clicked.connect(self.update_rvr_stats)
        self.update_rvr_button.setMaximumWidth(200)
        
        # Info button for statistics explanation
        self.stats_info_button = QPushButton(lang.get("stats_info_button"))
        self.stats_info_button.setToolTip(lang.get("stats_info_tooltip"))
        self.stats_info_button.clicked.connect(self.show_stats_info)
        self.stats_info_button.setMaximumWidth(150)
        
        # Disable button if no Herald URL or if Herald validation is in progress
        herald_url = self.character_data.get('url', '').strip()
        herald_validation_done = self._is_herald_validation_done()
        
        if not herald_url:
            self.update_rvr_button.setEnabled(False)
            self.update_rvr_button.setToolTip("Veuillez d'abord configurer l'URL Herald")
        elif not herald_validation_done:
            self.update_rvr_button.setEnabled(False)
            self.update_rvr_button.setToolTip("⏳ Validation Herald en cours au démarrage...")
            # S'abonner au signal de fin de validation pour réactiver le bouton
            if hasattr(self.parent_app, 'ui_manager') and hasattr(self.parent_app.ui_manager, 'eden_status_thread'):
                thread = self.parent_app.ui_manager.eden_status_thread
                if thread:
                    thread.status_updated.connect(self._on_herald_validation_finished)
        
        buttons_layout.addWidget(self.update_rvr_button)
        buttons_layout.addWidget(self.stats_info_button)
        buttons_layout.addStretch()  # Push buttons to the left
        
        statistics_layout.addLayout(buttons_layout)
        
        statistics_group.setLayout(statistics_layout)
        
        # Horizontal layout for Info and Statistics groups side by side
        top_layout = QHBoxLayout()
        top_layout.addWidget(info_group, 1)  # 50% stretch
        top_layout.addWidget(statistics_group, 1)  # 50% stretch
        layout.addLayout(top_layout)
        
        # Realm Rank Section
        realm_rank_group = QGroupBox("Rang de Royaume")
        realm_rank_layout = QVBoxLayout()
        
        realm_points = self.character_data.get('realm_points', 0)
        # Convertir realm_points en entier s'il s'agit d'une chaîne
        if isinstance(realm_points, str):
            realm_points = int(realm_points.replace(' ', '').replace('\xa0', '').replace(',', ''))
        
        # Get current rank and level
        current_rank = 1
        current_level = 1
        rank_info = None
        if hasattr(parent, 'data_manager'):
            rank_info = parent.data_manager.get_realm_rank_info(self.realm, realm_points)
            if rank_info:
                current_rank = rank_info['rank']
                level_str = rank_info['level']  # Format "XLY"
                level_match = re.search(r'L(\d+)', level_str)
                if level_match:
                    current_level = int(level_match.group(1))
        
        # Current rank and title display at the top with realm color
        self.rank_title_label = QLabel()
        self.rank_title_label.setAlignment(Qt.AlignLeft)
        self.update_rank_display(realm_points)
        
        # Styling for title label (same size as controls)
        realm_colors = {
            "Albion": "#CC0000",
            "Hibernia": "#00AA00",
            "Midgard": "#0066CC"
        }
        color = realm_colors.get(self.realm, "#000000")
        self.rank_title_label.setStyleSheet(f"font-weight: bold; color: {color};")
        realm_rank_layout.addWidget(self.rank_title_label)
        
        # Rank and Level dropdowns on a single line below the title
        rank_dropdown_layout = QHBoxLayout()
        rank_dropdown_layout.addWidget(QLabel("Rang :"))
        
        self.rank_combo = QComboBox()
        for i in range(1, 15):  # Ranks 1-14
            self.rank_combo.addItem(str(i), i)
        self.rank_combo.setCurrentIndex(current_rank - 1)
        self.rank_combo.currentIndexChanged.connect(self.on_rank_changed)
        rank_dropdown_layout.addWidget(self.rank_combo)
        
        # Level dropdown (0-10 for rank 1, 0-9 for others)
        rank_dropdown_layout.addWidget(QLabel("Niveau :"))
        
        self.level_combo_rank = QComboBox()
        self.update_level_dropdown(current_rank, current_level)
        self.level_combo_rank.currentIndexChanged.connect(self.on_level_changed)
        rank_dropdown_layout.addWidget(self.level_combo_rank)
        
        rank_dropdown_layout.addStretch()  # Push controls to the left
        
        realm_rank_layout.addLayout(rank_dropdown_layout)
        
        realm_rank_group.setLayout(realm_rank_layout)
        layout.addWidget(realm_rank_group)
        
        # Armor Manager button (moved here after Realm Rank section)
        armor_manager_button = QPushButton("📁 Gérer les armures")
        armor_manager_button.clicked.connect(self.open_armor_manager)
        armor_manager_button.setToolTip("Upload et gestion des fichiers d'armure créés avec des logiciels tiers")
        layout.addWidget(armor_manager_button)
        
        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        button_box.accepted.connect(self.save_basic_info)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Add content layout to main horizontal layout
        main_horizontal.addLayout(layout, 1)  # Stretch factor 1 for content
    
    def _update_class_banner(self):
        """Update the class banner image based on current class and realm"""
        from Functions.path_manager import get_resource_path
        
        realm = self.character_data.get('realm', 'Albion')
        class_name = self.character_data.get('class', '')
        
        if not class_name:
            # No class selected, show placeholder or hide
            self.banner_label.clear()
            self.banner_label.setText("No\nClass\nSelected")
            self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.banner_label.setStyleSheet("color: gray; font-style: italic;")
            return
        
        # Build banner path: Img/Banner/{realm}/{class}.jpg
        # Normalize realm and class names (handle abbreviations)
        realm_map = {
            "Albion": "Alb",
            "Hibernia": "Hib",
            "Midgard": "Mid"
        }
        realm_folder = realm_map.get(realm, realm)
        
        # Class name should be lowercase for filename
        class_filename = class_name.lower().replace(" ", "_")
        
        # Use get_resource_path for PyInstaller compatibility
        banner_path = get_resource_path(os.path.join("Img", "Banner", realm_folder, f"{class_filename}.jpg"))
        
        # Try with .png if .jpg doesn't exist
        if not os.path.exists(banner_path):
            banner_path = get_resource_path(os.path.join("Img", "Banner", realm_folder, f"{class_filename}.png"))
        
        if os.path.exists(banner_path):
            pixmap = QPixmap(banner_path)
            if not pixmap.isNull():
                # Set pixmap without scaling - Qt will handle scaling with setScaledContents(True)
                self.banner_label.setPixmap(pixmap)
                self.banner_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
                self.banner_label.setStyleSheet("")
            else:
                self._set_banner_placeholder(f"Invalid\nimage:\n{class_name}")
        else:
            # Banner not found
            self._set_banner_placeholder(f"Banner\nnot found:\n{realm}\n{class_name}")
    
    def _set_banner_placeholder(self, text):
        """Set placeholder text for banner"""
        self.banner_label.clear()
        self.banner_label.setText(text)
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner_label.setStyleSheet(f"color: gray; font-style: italic; font-size: {get_scaled_size(9):.1f}pt;")
    
    def _populate_classes_sheet(self):
        """Populates class dropdown based on selected realm."""
        self.class_combo.clear()
        realm = self.realm_combo.currentText()
        
        # Get all classes for the realm
        classes = self.data_manager.get_classes(realm)
        current_language = config.get("language", "en")
        
        for cls in classes:
            # Get translated name
            if current_language == "fr" and "name_fr" in cls:
                display_name = cls["name_fr"]
            elif current_language == "de" and "name_de" in cls:
                display_name = cls["name_de"]
            else:
                display_name = cls["name"]
            
            # Store actual name as item data
            self.class_combo.addItem(display_name, cls["name"])
    
    def _populate_races_sheet(self):
        """Populates race dropdown based on selected class and realm."""
        self.race_combo.clear()
        realm = self.realm_combo.currentText()
        
        # Get selected class (actual name from item data)
        class_index = self.class_combo.currentIndex()
        if class_index < 0:
            # If no class selected, show all races
            races = self.data_manager.get_races(realm)
        else:
            class_name = self.class_combo.itemData(class_index)
            if not class_name:
                races = self.data_manager.get_races(realm)
            else:
                # Filter races that can be this class
                races = self.data_manager.get_available_races_for_class(realm, class_name)
        
        current_language = config.get("language", "en")
        
        for race in races:
            # Get translated name
            if current_language == "fr" and "name_fr" in race:
                display_name = race["name_fr"]
            elif current_language == "de" and "name_de" in race:
                display_name = race["name_de"]
            else:
                display_name = race["name"]
            
            # Store actual name as item data
            self.race_combo.addItem(display_name, race["name"])
    
    def _on_realm_changed_sheet(self):
        """Called when realm is changed in character sheet."""
        self._populate_classes_sheet()
        self._populate_races_sheet()
        # Update character_data and banner
        self.character_data['realm'] = self.realm_combo.currentText()
        self._update_class_banner()
    
    def _on_class_changed_sheet(self):
        """Called when class is changed in character sheet."""
        self._populate_races_sheet()
        # Update character_data and banner
        class_data = self.class_combo.currentData()
        if class_data:
            self.character_data['class'] = class_data
            self._update_class_banner()
    
    def _on_race_changed_sheet(self):
        """Called when race is changed in character sheet (no action needed)."""
        pass
    
    def on_rank_changed(self, value):
        """Called when rank dropdown changes."""
        rank = self.rank_combo.currentData()
        level = self.level_combo_rank.currentData()
        
        # Update level dropdown for new rank
        self.update_level_dropdown(rank, level)
        
        # Update RP info and auto-save
        self.update_rp_info()
        self.auto_apply_rank()
    
    def on_level_changed(self, value):
        """Called when level dropdown changes."""
        # Update RP info and auto-save
        self.update_rp_info()
        self.auto_apply_rank()
    
    def update_level_dropdown(self, rank, current_level=1):
        """Updates level dropdown based on selected rank."""
        self.level_combo_rank.blockSignals(True)  # Prevent triggering change event
        self.level_combo_rank.clear()
        
        # Rank 1 has levels 0-10, others have 0-9
        max_level = 10 if rank == 1 else 9
        for i in range(0, max_level + 1):
            self.level_combo_rank.addItem(f"L{i}", i)
        
        # Set current level
        if current_level <= max_level:
            self.level_combo_rank.setCurrentIndex(current_level)
        else:
            self.level_combo_rank.setCurrentIndex(0)
        
        self.level_combo_rank.blockSignals(False)
    
    def update_rp_info(self):
        """Updates RP display for the selected rank/level."""
        if not hasattr(self.parent_app, 'data_manager'):
            return
        
        rank = self.rank_combo.currentData()
        level = self.level_combo_rank.currentData()
        level_str = f"{rank}L{level}"
        
        # Find RP for this level and update the main display
        rank_info = self.parent_app.data_manager.get_rank_by_level(self.realm, level_str)
        if rank_info:
            self.rank_title_label.setText(
                f"Rank {rank_info['rank']} - {rank_info['title']} ({rank_info['level']} - {rank_info['realm_points']:,} RP)"
            )
    
    def update_rank_display(self, realm_points):
        """Updates current rank and title display."""
        # Convertir realm_points en entier s'il s'agit d'une chaîne
        if isinstance(realm_points, str):
            realm_points = int(realm_points.replace(' ', '').replace('\xa0', '').replace(',', ''))
        
        if hasattr(self.parent_app, 'data_manager'):
            rank_info = self.parent_app.data_manager.get_realm_rank_info(self.realm, realm_points)
            if rank_info:
                self.rank_title_label.setText(
                    f"Rank {rank_info['rank']} - {rank_info['title']} ({rank_info['level']} - {realm_points:,} RP)"
                )
            else:
                self.rank_title_label.setText(f"Rank 1 - Guardian (1L1 - 0 RP)")
        else:
            realm_rank = self.character_data.get('realm_rank', '1L1')
            self.rank_title_label.setText(f"{realm_rank} - {realm_points:,} RP")
    
    def auto_apply_rank(self):
        """Automatically applies the selected rank to the character (no confirmation)."""
        rank = self.rank_combo.currentData()
        level = self.level_combo_rank.currentData()
        level_str = f"{rank}L{level}"
        
        if not hasattr(self.parent_app, 'data_manager'):
            return
        
        # Get RP for this level
        rank_info = self.parent_app.data_manager.get_rank_by_level(self.realm, level_str)
        if not rank_info:
            return
        
        new_rp = rank_info['realm_points']
        
        # Update data silently (no confirmation dialog)
        self.character_data['realm_points'] = new_rp
        self.character_data['realm_rank'] = level_str
        
        # Save (allow overwrite since we're updating an existing character)
        from Functions.character_manager import save_character
        success, msg = save_character(self.character_data, allow_overwrite=True)
        
        if success:
            # Update display
            self.update_rank_display(new_rp)
            # Refresh list
            if hasattr(self.parent_app, 'refresh_character_list'):
                self.parent_app.refresh_character_list()
            
            log_with_action(logger_char, "info", f"Character rank auto-applied to {level_str} with {new_rp:,} RP", action="RANK_UPDATE")
            
            # Trigger backup after character modification
            if hasattr(self.parent_app, 'backup_manager'):
                try:
                    char_name = self.character_data.get('name', 'Unknown')
                    import sys
                    import logging
                    print(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) '{char_name}' - Backup with reason=Update")
                    sys.stderr.write(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) '{char_name}' - Backup with reason=Update\n")
                    sys.stderr.flush()
                    logging.info(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) '{char_name}' - Backup with reason=Update")
                    self.parent_app.backup_manager.backup_characters_force(reason="Update", character_name=char_name)
                except Exception as e:
                    print(f"[BACKUP_TRIGGER] Warning: Backup after rank modification failed: {e}")
                    sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after rank modification failed: {e}\n")
                    sys.stderr.flush()
                    logging.warning(f"[BACKUP_TRIGGER] Backup after rank modification failed: {e}")
    
    def apply_rank(self):
        """Old apply_rank method - kept for backwards compatibility but not used anymore."""
        rank = self.rank_slider.value()
        level = self.level_slider.value()
        level_str = f"{rank}L{level}"
        
        if not hasattr(self.parent_app, 'data_manager'):
            QMessageBox.warning(self, "Erreur", "Data Manager non disponible")
            return
        
        # Get RP for this level
        rank_info = self.parent_app.data_manager.get_rank_by_level(self.realm, level_str)
        if not rank_info:
            QMessageBox.warning(self, "Erreur", f"Impossible de trouver les données pour {level_str}")
            return
        
        new_rp = rank_info['realm_points']
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirmer",
            f"Définir le rang à {level_str} ({rank_info['title']}) ?\n"
            f"Cela définira les Realm Points à {new_rp:,}.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Update data
            self.character_data['realm_points'] = new_rp
            self.character_data['realm_rank'] = level_str
            
            # Save (allow overwrite since we're updating an existing character)
            from Functions.character_manager import save_character
            success, msg = save_character(self.character_data, allow_overwrite=True)
            
            if success:
                log_with_action(logger_char, "info", f"Character rank applied to {level_str} with {new_rp:,} RP after confirmation", action="RANK_UPDATE")
                QMessageBox.information(self, "Succès", f"Rang mis à jour : {level_str}\nRealm Points : {new_rp:,}")
                # Update display
                self.update_rank_display(new_rp)
                # Refresh list
                if hasattr(self.parent_app, 'refresh_character_list'):
                    self.parent_app.refresh_character_list()
                
                # Trigger backup after character modification
                if hasattr(self.parent_app, 'backup_manager'):
                    try:
                        char_name = self.character_data.get('name', 'Unknown')
                        import sys
                        import logging
                        print(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) '{char_name}' - Backup with reason=Update")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) '{char_name}' - Backup with reason=Update\n")
                        sys.stderr.flush()
                        logging.info(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) '{char_name}' - Backup with reason=Update")
                        self.parent_app.backup_manager.backup_characters_force(reason="Update", character_name=char_name)
                    except Exception as e:
                        print(f"[BACKUP_TRIGGER] Warning: Backup after rank modification failed: {e}")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after rank modification failed: {e}\n")
                        sys.stderr.flush()
                        logging.warning(f"[BACKUP_TRIGGER] Backup after rank modification failed: {e}")
            else:
                log_with_action(logger_char, "error", f"Failed to apply rank {level_str}: {msg}", action="ERROR")
                QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde : {msg}")

    def save_basic_info(self):
        """Saves the basic character information (realm, level, season, server, page, guild, race and class)."""
        try:
            # Get current values
            new_realm = self.realm_combo.currentText()
            new_level = int(self.level_combo.currentText())
            new_season = self.season_combo.currentText()
            new_server = self.server_combo.currentText()
            new_page = int(self.page_combo.currentText())
            new_guild = self.guild_edit.text().strip()
            
            # Get race and class (actual names from item data)
            race_index = self.race_combo.currentIndex()
            class_index = self.class_combo.currentIndex()
            
            new_race = self.race_combo.itemData(race_index) if race_index >= 0 else ""
            new_class = self.class_combo.itemData(class_index) if class_index >= 0 else ""
            
            # Validate race/class combination
            if new_race and new_class:
                if not self.data_manager.is_race_class_compatible(new_realm, new_race, new_class):
                    QMessageBox.critical(
                        self, 
                        "Erreur", 
                        lang.get("invalid_race_class_combo", default="Cette combinaison de race et classe n'est pas valide.")
                    )
                    return
            
            old_realm = self.character_data.get('realm', self.realm)
            
            # Handle realm change if needed
            if old_realm != new_realm:
                from Functions.character_manager import move_character_to_realm
                success, msg = move_character_to_realm(self.character_data, old_realm, new_realm)
                if not success:
                    QMessageBox.critical(self, "Erreur", f"Échec du changement de royaume : {msg}")
                    return
                
                # Update local realm reference for color updates
                self.realm = new_realm
                
                # Update rank title color
                realm_colors = {
                    "Albion": "#CC0000",
                    "Hibernia": "#00AA00",
                    "Midgard": "#0066CC"
                }
                color = realm_colors.get(self.realm, "#000000")
                self.rank_title_label.setStyleSheet(f"font-size: {get_scaled_size(16):.1f}pt; font-weight: bold; color: {color};")
            
            # Update character data
            self.character_data['realm'] = new_realm
            self.character_data['level'] = new_level
            self.character_data['season'] = new_season
            self.character_data['server'] = new_server
            self.character_data['page'] = new_page
            self.character_data['guild'] = new_guild
            self.character_data['race'] = new_race
            self.character_data['class'] = new_class
            
            # Save Eden Herald URL
            herald_url = self.herald_url_edit.text().strip()
            if herald_url:
                self.character_data['url'] = herald_url
            
            # Save character (it's already moved if realm changed)
            if old_realm == new_realm:
                from Functions.character_manager import save_character
                success, msg = save_character(self.character_data, allow_overwrite=True)
                if not success:
                    QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde : {msg}")
                    return
                
                log_with_action(logger_char, "info", f"Character basic info updated: Level={new_level}, Season={new_season}, Guild={new_guild}", action="INFO_UPDATE")
                
                # Trigger backup after character modification
                if hasattr(self.parent_app, 'backup_manager'):
                    try:
                        char_name = self.character_data.get('name', 'Unknown')
                        import sys
                        import logging
                        print(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Basic Info) '{char_name}' - Backup with reason=Update")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Basic Info) '{char_name}' - Backup with reason=Update\n")
                        sys.stderr.flush()
                        logging.info(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Basic Info) '{char_name}' - Backup with reason=Update")
                        self.parent_app.backup_manager.backup_characters_force(reason="Update", character_name=char_name)
                    except Exception as e:
                        print(f"[BACKUP_TRIGGER] Warning: Backup after basic info modification failed: {e}")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after basic info modification failed: {e}\n")
                        sys.stderr.flush()
                        logging.warning(f"[BACKUP_TRIGGER] Backup after basic info modification failed: {e}")
            
            QMessageBox.information(self, "Succès", "Informations du personnage mises à jour avec succès !")
            # Refresh list in parent
            if hasattr(self.parent_app, 'refresh_character_list'):
                self.parent_app.refresh_character_list()
                
        except Exception as e:
            log_with_action(logger_char, "error", f"Error saving basic info: {str(e)}", action="ERROR")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

    def open_armor_manager(self):
        """Opens the armor management dialog."""
        try:
            character_id = self.character_data.get('id', '')
            if not character_id:
                QMessageBox.warning(self, "Erreur", "Impossible de déterminer l'ID du personnage.")
                return
            
            dialog = ArmorManagementDialog(self, character_id)
            dialog.exec()
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'ouverture de la gestion des armures:\n{str(e)}\n\n{traceback.format_exc()}"
            logging.error(error_msg)
            QMessageBox.critical(self, "Erreur", error_msg)
    
    def on_herald_url_changed(self, text):
        """Active/désactive le bouton de mise à jour des stats selon l'URL Herald"""
        # Ne pas réactiver les boutons si un scraping Herald est en cours
        if self.herald_scraping_in_progress:
            return
            
        is_url_valid = bool(text.strip())
        self.update_rvr_button.setEnabled(is_url_valid)
        
        if is_url_valid:
            self.update_rvr_button.setToolTip(lang.get("update_rvr_pvp_tooltip"))
        else:
            self.update_rvr_button.setToolTip("Veuillez d'abord configurer l'URL Herald")
    
    def _is_herald_validation_done(self):
        """Vérifie si la validation Herald du démarrage est terminée"""
        if not hasattr(self.parent_app, 'ui_manager'):
            return True  # Si pas de ui_manager, considérer comme fait
        
        # Vérifier si le thread de validation est en cours
        if hasattr(self.parent_app.ui_manager, 'eden_status_thread'):
            thread = self.parent_app.ui_manager.eden_status_thread
            if thread and thread.isRunning():
                return False
        
        return True
    
    def _on_herald_validation_finished(self, accessible, message):
        """Appelé quand la validation Herald du démarrage se termine"""
        # Réactiver le bouton si Herald accessible ET qu'une URL est configurée
        herald_url = self.character_data.get('url', '').strip()
        if accessible and herald_url:
            self.update_rvr_button.setEnabled(True)
            self.update_rvr_button.setToolTip(lang.get("update_rvr_pvp_tooltip"))
    
    def show_stats_info(self):
        """Affiche une fenêtre d'information sur les statistiques"""
        QMessageBox.information(
            self,
            lang.get("stats_info_title"),
            lang.get("stats_info_message")
        )
    
    def _update_achievements_display(self, achievements_list):
        """
        Update achievements display with the provided list.
        Uses QGridLayout in 2 columns of 8 achievements with vertical separator.
        
        Args:
            achievements_list: List of dicts with 'title', 'progress', and 'current' keys
        """
        # Clear existing widgets
        while self.achievements_container_layout.count():
            item = self.achievements_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layouts
                while item.layout().count():
                    nested_item = item.layout().takeAt(0)
                    if nested_item.widget():
                        nested_item.widget().deleteLater()
        
        if not achievements_list or len(achievements_list) == 0:
            # Show placeholder
            placeholder = QLabel("—")
            placeholder.setStyleSheet("color: gray; font-style: italic;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.achievements_container_layout.addWidget(placeholder)
            self.achievements_container_layout.addStretch()
            return
        
        # Create horizontal layout for 2 columns
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(15)
        
        # Split achievements into 2 groups of 8 (or less)
        mid_point = 8
        first_column = achievements_list[:mid_point]
        second_column = achievements_list[mid_point:]
        
        # === First column (left) ===
        first_grid = QGridLayout()
        first_grid.setHorizontalSpacing(10)
        first_grid.setVerticalSpacing(2)
        first_grid.setColumnStretch(0, 3)  # Title column
        first_grid.setColumnStretch(1, 0)  # Progress column (fixed)
        first_grid.setColumnStretch(2, 2)  # Current tier column
        
        for row, achievement in enumerate(first_column):
            title = achievement.get('title', 'Unknown')
            progress = achievement.get('progress', '0/0')
            current_tier = achievement.get('current', None)
            
            # Title
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt;")
            first_grid.addWidget(title_label, row, 0, Qt.AlignmentFlag.AlignLeft)
            
            # Progress
            progress_label = QLabel(progress)
            progress_label.setStyleSheet(f"font-weight: bold; font-size: {get_scaled_size(9):.1f}pt;")
            first_grid.addWidget(progress_label, row, 1, Qt.AlignmentFlag.AlignRight)
            
            # Current tier
            if current_tier and current_tier != "None":
                current_label = QLabel(f"({current_tier})")
                current_label.setStyleSheet(f"font-size: {get_scaled_size(8):.1f}pt; color: #6c757d; font-style: italic;")
                first_grid.addWidget(current_label, row, 2, Qt.AlignmentFlag.AlignLeft)
        
        columns_layout.addLayout(first_grid, 1)  # Stretch factor 1
        
        # === Vertical separator ===
        if second_column:  # Only add separator if there's a second column
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.VLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("color: #cccccc;")
            columns_layout.addWidget(separator)
        
        # === Second column (right) ===
        if second_column:
            second_grid = QGridLayout()
            second_grid.setHorizontalSpacing(10)
            second_grid.setVerticalSpacing(2)
            second_grid.setColumnStretch(0, 3)  # Title column
            second_grid.setColumnStretch(1, 0)  # Progress column (fixed)
            second_grid.setColumnStretch(2, 2)  # Current tier column
            
            for row, achievement in enumerate(second_column):
                title = achievement.get('title', 'Unknown')
                progress = achievement.get('progress', '0/0')
                current_tier = achievement.get('current', None)
                
                # Title
                title_label = QLabel(title)
                title_label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt;")
                second_grid.addWidget(title_label, row, 0, Qt.AlignmentFlag.AlignLeft)
                
                # Progress
                progress_label = QLabel(progress)
                progress_label.setStyleSheet(f"font-weight: bold; font-size: {get_scaled_size(9):.1f}pt;")
                second_grid.addWidget(progress_label, row, 1, Qt.AlignmentFlag.AlignRight)
                
                # Current tier
                if current_tier and current_tier != "None":
                    current_label = QLabel(f"({current_tier})")
                    current_label.setStyleSheet(f"font-size: {get_scaled_size(8):.1f}pt; color: #6c757d; font-style: italic;")
                    second_grid.addWidget(current_label, row, 2, Qt.AlignmentFlag.AlignLeft)
            
            columns_layout.addLayout(second_grid, 1)  # Stretch factor 1
        
        # Add columns layout to container
        self.achievements_container_layout.addLayout(columns_layout)
        
        # Add stretch at the end
        self.achievements_container_layout.addStretch()
    
    def open_herald_url(self):
        """Ouvre l'URL du Herald dans le navigateur avec les cookies"""
        url = self.herald_url_edit.text().strip()
        
        if not url:
            QMessageBox.warning(
                self,
                "URL manquante",
                "Veuillez entrer une URL Herald valide."
            )
            return
        
        # Check that l'URL commence par http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.herald_url_edit.setText(url)
        
        try:
            # Ouvrir l'URL with the cookies in un thread séparé
            import threading
            thread = threading.Thread(target=self._open_url_in_thread, args=(url,), daemon=True)
            thread.start()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible d'ouvrir l'URL : {str(e)}"
            )
    
    def _open_url_in_thread(self, url):
        """Ouvre l'URL avec les cookies dans un thread séparé."""
        try:
            from Functions.cookie_manager import CookieManager
            cookie_manager = CookieManager()
            result = cookie_manager.open_url_with_cookies_subprocess(url)
            
            if not result.get('success', False):
                import logging
                logging.warning(f"Erreur lors de l'ouverture de l'URL: {result.get('message', 'Erreur inconnue')}")
        except Exception as e:
            import logging
            logging.error(f"Erreur lors de l'ouverture de l'URL avec cookies: {e}")
    
    def update_rvr_stats(self):
        """Met à jour les statistiques RvR depuis le Herald"""
        url = self.herald_url_edit.text().strip()
        
        if not url:
            QMessageBox.warning(
                self,
                "URL manquante",
                "Veuillez entrer une URL Herald valide pour récupérer les statistiques."
            )
            return
        
        # Check URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.herald_url_edit.setText(url)
        
        # Désactiver le bouton pendant la mise à jour
        self.update_rvr_button.setEnabled(False)
        
        # Import des composants nécessaires
        from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
        
        # Construire les étapes (SCRAPER_INIT + STATS_SCRAPING + CLEANUP)
        steps = StepConfiguration.build_steps(
            StepConfiguration.SCRAPER_INIT,   # Step 0: Init scraper
            StepConfiguration.STATS_SCRAPING, # Steps 1-5: RvR, PvP, PvE, Wealth, Achievements
            StepConfiguration.CLEANUP         # Step 6: Close browser
        )
        
        # Créer le dialogue de progression
        self.progress_dialog = ProgressStepsDialog(
            parent=self,
            title=lang.get("progress_stats_update_title", default="📊 Mise à jour des statistiques..."),
            steps=steps,
            description=lang.get("progress_stats_update_desc", default="Récupération des statistiques RvR, PvP, PvE et Wealth depuis le Herald Eden"),
            show_progress_bar=True,
            determinate_progress=True,  # Mode avec pourcentage
            allow_cancel=False
        )
        
        # Créer le thread de mise à jour
        self.stats_update_thread = StatsUpdateThread(url)
        
        # ✅ Pattern 1 : Connecter via wrappers thread-safe
        self.stats_update_thread.step_started.connect(self._on_stats_step_started)
        self.stats_update_thread.step_completed.connect(self._on_stats_step_completed)
        self.stats_update_thread.step_error.connect(self._on_stats_step_error)
        
        # Connecter les signaux de fin
        self.stats_update_thread.stats_updated.connect(self._on_stats_updated)
        self.stats_update_thread.update_failed.connect(self._on_stats_failed)
        
        # ✅ Pattern 4 : Connecter rejected AVANT show()
        self.progress_dialog.rejected.connect(self._on_stats_progress_dialog_closed)
        
        # Afficher le dialogue et démarrer le worker
        self.progress_dialog.show()
        self.stats_update_thread.start()
    
    # ✅ Pattern 1 : Wrappers thread-safe pour stats update
    def _on_stats_step_started(self, step_index):
        """Wrapper thread-safe pour start_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.start_step(step_index)
            except RuntimeError:
                pass
    
    def _on_stats_step_completed(self, step_index):
        """Wrapper thread-safe pour complete_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.complete_step(step_index)
            except RuntimeError:
                pass
    
    def _on_stats_step_error(self, step_index, error_message):
        """Wrapper thread-safe pour error_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.error_step(step_index, error_message)
            except RuntimeError:
                pass
    
    def _on_stats_progress_dialog_closed(self):
        """✅ Pattern 4 : Appelé quand utilisateur ferme le dialogue de stats"""
        import logging
        logging.info("Dialogue stats fermé par utilisateur - Arrêt mise à jour")
        
        # Arrêter le thread proprement
        self._stop_stats_thread()
        
        # Réactiver le bouton
        if not self.herald_scraping_in_progress:
            self.update_rvr_button.setEnabled(True)
    
    def _stop_stats_thread(self):
        """✅ Pattern 2 + 3 : Arrête le thread stats avec cleanup complet"""
        if hasattr(self, 'stats_update_thread') and self.stats_update_thread:
            if self.stats_update_thread.isRunning():
                # 1. Demander arrêt gracieux
                self.stats_update_thread.request_stop()
                
                # 2. Déconnecter signaux
                try:
                    self.stats_update_thread.step_started.disconnect()
                    self.stats_update_thread.step_completed.disconnect()
                    self.stats_update_thread.step_error.disconnect()
                    self.stats_update_thread.stats_updated.disconnect()
                    self.stats_update_thread.update_failed.disconnect()
                except:
                    pass
                
                # 3. Attendre 3s
                self.stats_update_thread.wait(3000)
                
                # 4. ✅ CRITIQUE : Cleanup AVANT terminate()
                if self.stats_update_thread.isRunning():
                    import logging
                    logging.warning("Thread stats non terminé - Cleanup forcé")
                    self.stats_update_thread.cleanup_external_resources()
                    self.stats_update_thread.terminate()
                    self.stats_update_thread.wait()
                
                import logging
                logging.info("Thread stats arrêté proprement")
            
            self.stats_update_thread = None
        
        # Fermer le dialogue
        if hasattr(self, 'progress_dialog'):
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
    
    def _on_stats_updated(self, results):
        """Appelé quand les stats sont mises à jour (succès ou partiel)"""
        from PySide6.QtCore import QTimer
        
        # Fermer le dialogue de progression
        if hasattr(self, 'progress_dialog'):
            success_text = lang.get("progress_stats_complete", default="✅ Statistiques récupérées")
            self.progress_dialog.complete_all(success_text)
            QTimer.singleShot(1500, self.progress_dialog.close)
        
        # Extraire les résultats
        result_rvr = results.get('rvr', {})
        result_pvp = results.get('pvp', {})
        result_pve = results.get('pve', {})
        result_wealth = results.get('wealth', {})
        result_achievements = results.get('achievements', {})
        
        all_success = result_rvr.get('success') and result_pvp.get('success') and result_pve.get('success') and result_wealth.get('success')
        
        if all_success:
            # Mise à jour complète réussie
            self._update_all_stats_ui(result_rvr, result_pvp, result_pve, result_wealth, result_achievements)
            
            # Sauvegarder dans le JSON
            from Functions.character_manager import save_character
            success, msg = save_character(self.character_data, allow_overwrite=True)
            
            if success:
                # Message de succès
                tower = result_rvr['tower_captures']
                keep = result_rvr['keep_captures']
                relic = result_rvr['relic_captures']
                solo_kills = result_pvp['solo_kills']
                solo_kills_alb = result_pvp['solo_kills_alb']
                solo_kills_hib = result_pvp['solo_kills_hib']
                solo_kills_mid = result_pvp['solo_kills_mid']
                deathblows = result_pvp['deathblows']
                deathblows_alb = result_pvp['deathblows_alb']
                deathblows_hib = result_pvp['deathblows_hib']
                deathblows_mid = result_pvp['deathblows_mid']
                kills = result_pvp['kills']
                kills_alb = result_pvp['kills_alb']
                kills_hib = result_pvp['kills_hib']
                kills_mid = result_pvp['kills_mid']
                dragon_kills = result_pve['dragon_kills']
                legion_kills = result_pve['legion_kills']
                mini_dragon_kills = result_pve['mini_dragon_kills']
                epic_encounters = result_pve['epic_encounters']
                epic_dungeons = result_pve['epic_dungeons']
                sobekite = result_pve['sobekite']
                money = result_wealth['money']
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Statistiques mises à jour :\n\n"
                    f"⚔️ RvR\n"
                    f"🗼 Tower Captures: {tower:,}\n"
                    f"🏰 Keep Captures: {keep:,}\n"
                    f"💎 Relic Captures: {relic:,}\n\n"
                    f"🗡️ PvP\n"
                    f"⚔️ Solo Kills: {solo_kills:,} (Alb: {solo_kills_alb:,}, Hib: {solo_kills_hib:,}, Mid: {solo_kills_mid:,})\n"
                    f"💀 Deathblows: {deathblows:,} (Alb: {deathblows_alb:,}, Hib: {deathblows_hib:,}, Mid: {deathblows_mid:,})\n"
                    f"🎯 Kills: {kills:,} (Alb: {kills_alb:,}, Hib: {kills_hib:,}, Mid: {kills_mid:,})\n\n"
                    f"🐉 PvE\n"
                    f"🐉 Dragons: {dragon_kills:,}  |  👹 Légions: {legion_kills:,}\n"
                    f"🐲 Mini Dragons: {mini_dragon_kills:,}  |  ⚔️ Epic Encounters: {epic_encounters:,}\n"
                    f"🏛️ Epic Dungeons: {epic_dungeons:,}  |  🐊 Sobekite: {sobekite:,}\n\n"
                    f"💰 Monnaie\n"
                    f"Total: {money}"
                )
                
                log_with_action(logger_char, "info", 
                              f"RvR stats updated: T={tower}, K={keep}, R={relic}, "
                              f"SK={solo_kills}(A:{solo_kills_alb},H:{solo_kills_hib},M:{solo_kills_mid}), "
                              f"DB={deathblows}(A:{deathblows_alb},H:{deathblows_hib},M:{deathblows_mid}), "
                              f"K={kills}(A:{kills_alb},H:{kills_hib},M:{kills_mid})", 
                              action="RVR_UPDATE")
            else:
                QMessageBox.warning(
                    self,
                    "Avertissement",
                    f"Statistiques récupérées mais erreur de sauvegarde : {msg}"
                )
        
        elif result_rvr.get('success') and not result_pvp.get('success'):
            # Mise à jour partielle : RvR OK, PvP KO
            self._update_partial_stats_ui(result_rvr, None, None, None, None)
            
            QMessageBox.warning(
                self,
                "Mise à jour partielle",
                f"✅ RvR Captures récupérées avec succès\n"
                f"❌ Statistiques PvP non disponibles\n\n"
                f"Erreur PvP: {result_pvp.get('error', 'Erreur inconnue')}\n\n"
                f"Cela peut arriver si le personnage n'a pas encore de statistiques PvP.\n"
                f"Les Tower/Keep/Relic Captures ont été sauvegardées."
            )
        
        elif not result_rvr.get('success') and result_pvp.get('success'):
            # Mise à jour partielle : PvP OK, RvR KO
            self._update_partial_stats_ui(None, result_pvp, None, None, None)
            
            QMessageBox.warning(
                self,
                "Mise à jour partielle",
                f"❌ RvR Captures non disponibles\n"
                f"✅ Statistiques PvP récupérées avec succès\n\n"
                f"Erreur RvR: {result_rvr.get('error', 'Erreur inconnue')}\n\n"
                f"Les statistiques PvP ont été sauvegardées."
            )
        
        else:
            # Échec complet ou multiple
            error_msg = "Impossible de récupérer les statistiques :\n\n"
            if not result_rvr.get('success'):
                error_msg += f"❌ RvR Captures: {result_rvr.get('error', 'Erreur inconnue')}\n"
            if not result_pvp.get('success'):
                error_msg += f"❌ PvP Stats: {result_pvp.get('error', 'Erreur inconnue')}\n"
            if not result_pve.get('success'):
                error_msg += f"❌ PvE Stats: {result_pve.get('error', 'Erreur inconnue')}\n"
            if not result_wealth.get('success'):
                error_msg += f"❌ Wealth: {result_wealth.get('error', 'Erreur inconnue')}\n"
            
            QMessageBox.critical(self, "Erreur", error_msg)
        
        # Réactiver le bouton
        if not self.herald_scraping_in_progress:
            self.update_rvr_button.setEnabled(True)
    
    def _on_stats_failed(self, error_message):
        """Appelé en cas d'échec complet de la mise à jour"""
        from PySide6.QtCore import QTimer
        
        # Fermer le dialogue de progression
        if hasattr(self, 'progress_dialog'):
            error_text = lang.get("progress_error", default="❌ {error}", error=error_message)
            self.progress_dialog.set_status_message(error_text, "#F44336")
            QTimer.singleShot(2000, self.progress_dialog.close)
        
        # Afficher l'erreur
        QMessageBox.critical(
            self,
            "Erreur",
            f"Erreur lors de la mise à jour des stats:\n{error_message}"
        )
        
        # Réactiver le bouton
        if not self.herald_scraping_in_progress:
            self.update_rvr_button.setEnabled(True)
        
        log_with_action(logger_char, "error", f"Stats update error: {error_message}", action="ERROR")
    
    def _update_all_stats_ui(self, result_rvr, result_pvp, result_pve, result_wealth, result_achievements):
        """Met à jour tous les labels UI avec les stats complètes"""
        # RvR Captures
        tower = result_rvr['tower_captures']
        keep = result_rvr['keep_captures']
        relic = result_rvr['relic_captures']
        
        self.tower_captures_label.setText(f"{tower:,}")
        self.keep_captures_label.setText(f"{keep:,}")
        self.relic_captures_label.setText(f"{relic:,}")
        
        # PvP Stats
        solo_kills = result_pvp['solo_kills']
        solo_kills_alb = result_pvp['solo_kills_alb']
        solo_kills_hib = result_pvp['solo_kills_hib']
        solo_kills_mid = result_pvp['solo_kills_mid']
        
        deathblows = result_pvp['deathblows']
        deathblows_alb = result_pvp['deathblows_alb']
        deathblows_hib = result_pvp['deathblows_hib']
        deathblows_mid = result_pvp['deathblows_mid']
        
        kills = result_pvp['kills']
        kills_alb = result_pvp['kills_alb']
        kills_hib = result_pvp['kills_hib']
        kills_mid = result_pvp['kills_mid']
        
        self.solo_kills_label.setText(f"{solo_kills:,}")
        self.deathblows_label.setText(f"{deathblows:,}")
        self.kills_label.setText(f"{kills:,}")
        
        self.solo_kills_detail_label.setText(
            f'→ <span style="color: #C41E3A;">Alb</span>: {solo_kills_alb:,}  |  '
            f'<span style="color: #228B22;">Hib</span>: {solo_kills_hib:,}  |  '
            f'<span style="color: #4169E1;">Mid</span>: {solo_kills_mid:,}'
        )
        self.deathblows_detail_label.setText(
            f'→ <span style="color: #C41E3A;">Alb</span>: {deathblows_alb:,}  |  '
            f'<span style="color: #228B22;">Hib</span>: {deathblows_hib:,}  |  '
            f'<span style="color: #4169E1;">Mid</span>: {deathblows_mid:,}'
        )
        self.kills_detail_label.setText(
            f'→ <span style="color: #C41E3A;">Alb</span>: {kills_alb:,}  |  '
            f'<span style="color: #228B22;">Hib</span>: {kills_hib:,}  |  '
            f'<span style="color: #4169E1;">Mid</span>: {kills_mid:,}'
        )
        
        # PvE Stats
        dragon_kills = result_pve['dragon_kills']
        legion_kills = result_pve['legion_kills']
        mini_dragon_kills = result_pve['mini_dragon_kills']
        epic_encounters = result_pve['epic_encounters']
        epic_dungeons = result_pve['epic_dungeons']
        sobekite = result_pve['sobekite']
        
        self.dragon_kills_value.setText(f"{dragon_kills:,}")
        self.legion_kills_value.setText(f"{legion_kills:,}")
        self.mini_dragon_kills_value.setText(f"{mini_dragon_kills:,}")
        self.epic_encounters_value.setText(f"{epic_encounters:,}")
        self.epic_dungeons_value.setText(f"{epic_dungeons:,}")
        self.sobekite_value.setText(f"{sobekite:,}")
        
        # Wealth
        money = result_wealth['money']
        self.money_label.setText(str(money))
        
        # Achievements (optionnel)
        if result_achievements.get('success'):
            achievements = result_achievements['achievements']
            self._update_achievements_display(achievements)
            self.character_data['achievements'] = achievements
        
        # Mettre à jour character_data
        self.character_data['tower_captures'] = tower
        self.character_data['keep_captures'] = keep
        self.character_data['relic_captures'] = relic
        
        self.character_data['solo_kills'] = solo_kills
        self.character_data['deathblows'] = deathblows
        self.character_data['kills'] = kills
        self.character_data['solo_kills_alb'] = solo_kills_alb
        self.character_data['solo_kills_hib'] = solo_kills_hib
        self.character_data['solo_kills_mid'] = solo_kills_mid
        self.character_data['deathblows_alb'] = deathblows_alb
        self.character_data['deathblows_hib'] = deathblows_hib
        self.character_data['deathblows_mid'] = deathblows_mid
        self.character_data['kills_alb'] = kills_alb
        self.character_data['kills_hib'] = kills_hib
        self.character_data['kills_mid'] = kills_mid
        
        self.character_data['dragon_kills'] = dragon_kills
        self.character_data['legion_kills'] = legion_kills
        self.character_data['mini_dragon_kills'] = mini_dragon_kills
        self.character_data['epic_encounters'] = epic_encounters
        self.character_data['epic_dungeons'] = epic_dungeons
        self.character_data['sobekite'] = sobekite
        
        self.character_data['money'] = money
    
    def _update_partial_stats_ui(self, result_rvr, result_pvp, result_pve, result_wealth, result_achievements):
        """Met à jour UI et character_data pour mise à jour partielle"""
        from Functions.character_manager import save_character
        
        if result_rvr and result_rvr.get('success'):
            tower = result_rvr['tower_captures']
            keep = result_rvr['keep_captures']
            relic = result_rvr['relic_captures']
            
            self.tower_captures_label.setText(f"{tower:,}")
            self.keep_captures_label.setText(f"{keep:,}")
            self.relic_captures_label.setText(f"{relic:,}")
            
            self.character_data['tower_captures'] = tower
            self.character_data['keep_captures'] = keep
            self.character_data['relic_captures'] = relic
            
            save_character(self.character_data, allow_overwrite=True)
        
        if result_pvp and result_pvp.get('success'):
            solo_kills = result_pvp['solo_kills']
            solo_kills_alb = result_pvp['solo_kills_alb']
            solo_kills_hib = result_pvp['solo_kills_hib']
            solo_kills_mid = result_pvp['solo_kills_mid']
            
            deathblows = result_pvp['deathblows']
            deathblows_alb = result_pvp['deathblows_alb']
            deathblows_hib = result_pvp['deathblows_hib']
            deathblows_mid = result_pvp['deathblows_mid']
            
            kills = result_pvp['kills']
            kills_alb = result_pvp['kills_alb']
            kills_hib = result_pvp['kills_hib']
            kills_mid = result_pvp['kills_mid']
            
            self.solo_kills_label.setText(f"{solo_kills:,}")
            self.deathblows_label.setText(f"{deathblows:,}")
            self.kills_label.setText(f"{kills:,}")
            
            self.solo_kills_detail_label.setText(
                f'→ <span style="color: #C41E3A;">Alb</span>: {solo_kills_alb:,}  |  '
                f'<span style="color: #228B22;">Hib</span>: {solo_kills_hib:,}  |  '
                f'<span style="color: #4169E1;">Mid</span>: {solo_kills_mid:,}'
            )
            self.deathblows_detail_label.setText(
                f'→ <span style="color: #C41E3A;">Alb</span>: {deathblows_alb:,}  |  '
                f'<span style="color: #228B22;">Hib</span>: {deathblows_hib:,}  |  '
                f'<span style="color: #4169E1;">Mid</span>: {deathblows_mid:,}'
            )
            self.kills_detail_label.setText(
                f'→ <span style="color: #C41E3A;">Alb</span>: {kills_alb:,}  |  '
                f'<span style="color: #228B22;">Hib</span>: {kills_hib:,}  |  '
                f'<span style="color: #4169E1;">Mid</span>: {kills_mid:,}'
            )
            
            self.character_data['solo_kills'] = solo_kills
            self.character_data['deathblows'] = deathblows
            self.character_data['kills'] = kills
            self.character_data['solo_kills_alb'] = solo_kills_alb
            self.character_data['solo_kills_hib'] = solo_kills_hib
            self.character_data['solo_kills_mid'] = solo_kills_mid
            self.character_data['deathblows_alb'] = deathblows_alb
            self.character_data['deathblows_hib'] = deathblows_hib
            self.character_data['deathblows_mid'] = deathblows_mid
            self.character_data['kills_alb'] = kills_alb
            self.character_data['kills_hib'] = kills_hib
            self.character_data['kills_mid'] = kills_mid
            
            save_character(self.character_data, allow_overwrite=True)
    
    def update_from_herald(self):
        """Met à jour les données du personnage depuis Herald"""
        url = self.herald_url_edit.text().strip()
        
        if not url:
            QMessageBox.warning(
                self,
                lang.get("update_char_error"),
                lang.get("update_char_no_url")
            )
            return
        
        # Marquer qu'un scraping Herald est en cours AVANT toute modification d'URL
        self.herald_scraping_in_progress = True
        
        # Check URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.herald_url_edit.setText(url)
        
        # Désactiver tous les boutons pendant la mise à jour
        self.update_herald_button.setEnabled(False)
        self.open_herald_button.setEnabled(False)
        self.update_rvr_button.setEnabled(False)
        
        # Import des composants nécessaires
        from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
        
        # Construire les étapes (CHARACTER_UPDATE)
        steps = StepConfiguration.build_steps(
            StepConfiguration.CHARACTER_UPDATE  # 8 steps: Extract name → Init → Load cookies → Navigate → Wait → Extract data → Format → Close
        )
        
        # Créer le dialogue de progression
        self.progress_dialog = ProgressStepsDialog(
            parent=self,
            title=lang.get("progress_character_update_title", default="🌐 Mise à jour depuis Herald..."),
            steps=steps,
            description=lang.get("progress_character_update_desc", default="Récupération des informations du personnage depuis Eden Herald"),
            show_progress_bar=True,
            determinate_progress=True,
            allow_cancel=False
        )
        
        # Créer le thread de mise à jour
        self.char_update_thread = CharacterUpdateThread(url)
        
        # ✅ Pattern 1 : Connecter via wrappers thread-safe
        self.char_update_thread.step_started.connect(self._on_char_update_step_started)
        self.char_update_thread.step_completed.connect(self._on_char_update_step_completed)
        self.char_update_thread.step_error.connect(self._on_char_update_step_error)
        
        # Connecter signal de fin
        self.char_update_thread.update_finished.connect(self._on_herald_scraping_finished)
        
        # ✅ Pattern 4 : Connecter rejected AVANT show()
        self.progress_dialog.rejected.connect(self._on_char_update_progress_dialog_closed)
        
        # Afficher le dialogue et démarrer le worker
        self.progress_dialog.show()
        self.char_update_thread.start()
    
    # ✅ Pattern 1 : Wrappers thread-safe pour character update
    def _on_char_update_step_started(self, step_index):
        """Wrapper thread-safe pour start_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.start_step(step_index)
            except RuntimeError:
                pass
    
    def _on_char_update_step_completed(self, step_index):
        """Wrapper thread-safe pour complete_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.complete_step(step_index)
            except RuntimeError:
                pass
    
    def _on_char_update_step_error(self, step_index, error_message):
        """Wrapper thread-safe pour error_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.error_step(step_index, error_message)
            except RuntimeError:
                pass
    
    def _on_char_update_progress_dialog_closed(self):
        """✅ Pattern 4 : Appelé quand utilisateur ferme le dialogue de character update"""
        import logging
        logging.info("Dialogue character update fermé par utilisateur - Arrêt mise à jour")
        
        # Arrêter le thread proprement
        self._stop_char_update_thread()
        
        # Réactiver les boutons
        self.herald_scraping_in_progress = False
        self.update_herald_button.setEnabled(True)
        self.open_herald_button.setEnabled(True)
        if not self.herald_scraping_in_progress:
            self.update_rvr_button.setEnabled(True)
    
    def _stop_char_update_thread(self):
        """✅ Pattern 2 + 3 : Arrête le thread character update avec cleanup complet"""
        if hasattr(self, 'char_update_thread') and self.char_update_thread:
            if self.char_update_thread.isRunning():
                # 1. Demander arrêt gracieux
                self.char_update_thread.request_stop()
                
                # 2. Déconnecter signaux
                try:
                    self.char_update_thread.step_started.disconnect()
                    self.char_update_thread.step_completed.disconnect()
                    self.char_update_thread.step_error.disconnect()
                    self.char_update_thread.update_finished.disconnect()
                except:
                    pass
                
                # 3. Attendre 3s
                self.char_update_thread.wait(3000)
                
                # 4. ✅ CRITIQUE : Cleanup AVANT terminate()
                if self.char_update_thread.isRunning():
                    import logging
                    logging.warning("Thread character update non terminé - Cleanup forcé")
                    self.char_update_thread.cleanup_external_resources()
                    self.char_update_thread.terminate()
                    self.char_update_thread.wait()
                
                import logging
                logging.info("Thread character update arrêté proprement")
            
            self.char_update_thread = None
        
        # Fermer le dialogue
        if hasattr(self, 'progress_dialog'):
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
    
    def _on_herald_scraping_finished(self, success, new_data, error_msg):
        """Callback appelé quand le scraping est terminé"""
        from PySide6.QtCore import QTimer
        
        # Marquer que le scraping Herald est terminé
        self.herald_scraping_in_progress = False
        
        # Fermer le dialogue de progression avec message de succès ou erreur
        if hasattr(self, 'progress_dialog'):
            if success:
                success_text = lang.get("progress_character_complete", default="✅ Données récupérées")
                self.progress_dialog.complete_all(success_text)
                QTimer.singleShot(1500, self.progress_dialog.close)
            else:
                error_text = lang.get("progress_error", default="❌ {error}", error=error_msg)
                self.progress_dialog.set_status_message(error_text, "#F44336")
                QTimer.singleShot(2000, self.progress_dialog.close)
        
        # Utiliser try/finally pour garantir la réactivation des boutons
        try:
            if not success:
                QMessageBox.critical(
                    self,
                    lang.get("update_char_error"),
                    f"{lang.get('update_char_error')}: {error_msg}"
                )
                return
            
            # Créer le dialogue pour détecter les changements
            dialog = CharacterUpdateDialog(self, self.character_data, new_data, self.character_data['name'])
            
            # Vérifier s'il y a au moins un changement
            if not dialog.has_changes():
                QMessageBox.information(
                    self,
                    lang.get("update_char_no_changes_title", default="Aucune mise à jour"),
                    lang.get("update_char_already_uptodate", default="Le personnage est déjà à jour. Aucune modification détectée.")
                )
                return
            
            # Afficher le dialogue de validation des changements
            if dialog.exec() == QDialog.Accepted:
                selected_changes = dialog.get_selected_changes()
                
                if not selected_changes:
                    QMessageBox.information(
                        self,
                        lang.get("update_char_cancelled"),
                        lang.get("update_char_no_changes")
                    )
                    return
                
                # Appliquer the changements sélectionnés directement in character_data
                for field, value in selected_changes.items():
                    self.character_data[field] = value
                
                # Mettre à jour all the champs of l'interface for l'affichage immédiat
                # (on reconstruit l'affichage complet plutôt that of mettre à jour champ par champ)
                
                # Level
                if 'level' in selected_changes:
                    self.level_combo.setCurrentText(str(selected_changes['level']))
                
                # Class
                if 'class' in selected_changes:
                    index = self.class_combo.findData(selected_changes['class'])
                    if index >= 0:
                        self.class_combo.setCurrentIndex(index)
                
                # Race
                if 'race' in selected_changes:
                    index = self.race_combo.findData(selected_changes['race'])
                    if index >= 0:
                        self.race_combo.setCurrentIndex(index)
                
                # Guild
                if 'guild' in selected_changes:
                    self.guild_edit.setText(selected_changes['guild'])
                
                # URL Herald
                if 'url' in selected_changes:
                    self.herald_url_edit.setText(selected_changes['url'])
                
                # Realm Points et Realm Rank
                if 'realm_points' in selected_changes or 'realm_rank' in selected_changes:
                    realm_points = self.character_data.get('realm_points', 0)
                    if isinstance(realm_points, str):
                        realm_points = int(realm_points.replace(' ', '').replace('\xa0', '').replace(',', ''))
                    
                    # Mettre à jour l'affichage of the rang and of the titre
                    self.update_rank_display(realm_points)
                    
                    # Mettre à jour the dropdowns of rang/niveau
                    if hasattr(self.parent_app, 'data_manager'):
                        rank_info = self.parent_app.data_manager.get_realm_rank_info(self.realm, realm_points)
                        if rank_info:
                            current_rank = rank_info['rank']
                            level_str = rank_info['level']  # Format "XLY"
                            level_match = re.search(r'L(\d+)', level_str)
                            if level_match:
                                current_level = int(level_match.group(1))
                                
                                # Mettre à jour the dropdown of rang
                                self.rank_combo.blockSignals(True)
                                self.rank_combo.setCurrentIndex(current_rank - 1)
                                self.rank_combo.blockSignals(False)
                                
                                # Mettre à jour the dropdown of niveau
                                self.update_level_dropdown(current_rank, current_level)
                
                # Save directement character_data (not via save_basic_info qui récupère depuis l'interface)
                from Functions.character_manager import save_character
                success, msg = save_character(self.character_data, allow_overwrite=True)
                
                if not success:
                    QMessageBox.critical(
                        self,
                        lang.get("error_title", default="Erreur"),
                        f"Échec de la sauvegarde : {msg}"
                    )
                    return
                
                # Trigger backup after character modification
                if hasattr(self.parent_app, 'backup_manager'):
                    try:
                        char_name = self.character_data.get('name', 'Unknown')
                        import sys
                        import logging
                        print(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Skills/Armor) '{char_name}' - Backup with reason=Update")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Skills/Armor) '{char_name}' - Backup with reason=Update\n")
                        sys.stderr.flush()
                        logging.info(f"[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Skills/Armor) '{char_name}' - Backup with reason=Update")
                        self.parent_app.backup_manager.backup_characters_force(reason="Update", character_name=char_name)
                    except Exception as e:
                        print(f"[BACKUP_TRIGGER] Warning: Backup after skills/armor modification failed: {e}")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after skills/armor modification failed: {e}\n")
                        sys.stderr.flush()
                        logging.warning(f"[BACKUP_TRIGGER] Backup after skills/armor modification failed: {e}")
                
                # Rafraîchir the liste des personnages in the fenêtre principale
                if hasattr(self.parent_app, 'tree_manager'):
                    self.parent_app.tree_manager.refresh_character_list()
                elif hasattr(self.parent_app, 'refresh_character_list'):
                    self.parent_app.refresh_character_list()
                
                # Message of succès
                QMessageBox.information(
                    self,
                    lang.get("success_title", default="Succès"),
                    lang.get("update_char_success")
                )
            else:
                QMessageBox.information(
                    self,
                    lang.get("update_char_cancelled"),
                    lang.get("update_char_cancelled")
                )
        
        finally:
            # Réactiver tous les boutons TOUJOURS, même en cas d'erreur ou de return anticipé
            herald_url = self.herald_url_edit.text().strip()
            
            self.update_herald_button.setEnabled(bool(herald_url))
            self.open_herald_button.setEnabled(bool(herald_url))
            self.update_rvr_button.setEnabled(bool(herald_url))
            
            # Forcer la mise à jour visuelle
            QApplication.processEvents()
    
    def rename_character(self):
        """Renames the character with validation."""
        try:
            old_name = self.character_data.get('name', '')
            new_name = self.name_edit.text().strip()
            
            if not new_name:
                QMessageBox.warning(self, "Erreur", "Le nom du personnage ne peut pas être vide.")
                self.name_edit.setText(old_name)  # Reset to original name
                return
            
            if old_name == new_name:
                QMessageBox.information(self, "Information", "Le nom n'a pas changé.")
                return
            
            # Confirm rename
            reply = QMessageBox.question(
                self,
                "Confirmer le renommage",
                f"Renommer '{old_name}' en '{new_name}' ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                from Functions.character_manager import rename_character
                success, msg = rename_character(old_name, new_name)
                
                if success:
                    # Update character data
                    self.character_data['name'] = new_name
                    self.character_data['id'] = new_name
                    
                    # Update window title
                    self.setWindowTitle(f"Fiche personnage - {new_name}")
                    
                    # Refresh list in parent
                    if hasattr(self.parent_app, 'refresh_character_list'):
                        self.parent_app.refresh_character_list()
                else:
                    error_msg = "Un personnage avec ce nom existe déjà." if msg == "char_exists_error" else msg
                    QMessageBox.critical(self, "Erreur", f"Échec du renommage : {error_msg}")
                    self.name_edit.setText(old_name)  # Reset to original name
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du renommage : {str(e)}")
            # Reset to original name in case of error
            if hasattr(self, 'character_data'):
                self.name_edit.setText(self.character_data.get('name', ''))


class ColumnsConfigDialog(QDialog):
    """Dialog to configure which columns are visible in the character list."""
    
    # Define all available columns with their default visibility
    COLUMNS_CONFIG = [
        {"key": "selection", "name_key": "column_selection", "default": True},
        {"key": "realm", "name_key": "column_realm", "default": True},
        {"key": "name", "name_key": "column_name", "default": True},
        {"key": "class", "name_key": "column_class", "default": True},  # Class visible by default
        {"key": "level", "name_key": "column_level", "default": True},
        {"key": "realm_rank", "name_key": "column_realm_rank", "default": True},
        {"key": "realm_title", "name_key": "column_realm_title", "default": True},
        {"key": "guild", "name_key": "column_guild", "default": True},
        {"key": "page", "name_key": "column_page", "default": True},
        {"key": "server", "name_key": "column_server", "default": False},  # Server hidden by default
        {"key": "race", "name_key": "column_race", "default": False},  # Race hidden by default
        {"key": "url", "name_key": "column_url", "default": False},  # URL hidden by default
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("columns_config_title", default="Configuration des colonnes"))
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Description
        desc_label = QLabel(lang.get("columns_config_desc", default="Sélectionnez les colonnes à afficher :"))
        layout.addWidget(desc_label)
        
        # Checkboxes for each column
        self.checkboxes = {}
        current_visibility = config.get("column_visibility", {})
        
        for col in self.COLUMNS_CONFIG:
            checkbox = QCheckBox(lang.get(col["name_key"], default=col["key"]))
            # Get visibility from config, or use default
            is_visible = current_visibility.get(col["key"], col["default"])
            checkbox.setChecked(is_visible)
            self.checkboxes[col["key"]] = checkbox
            layout.addWidget(checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton(lang.get("columns_select_all", default="Tout sélectionner"))
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton(lang.get("columns_deselect_all", default="Tout désélectionner"))
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        # OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def select_all(self):
        """Check all checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """Uncheck all checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def get_visibility_config(self):
        """Returns a dictionary with the visibility state of each column."""
        return {key: checkbox.isChecked() for key, checkbox in self.checkboxes.items()}


class NewCharacterDialog(QDialog):
    """A dialog to create a new character with a name and a realm."""
    
    def __init__(self, parent=None, realms=None, seasons=None, default_season=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("new_char_dialog_title"))

        self.realms = realms if realms else []
        self.seasons = seasons if seasons else []
        self.default_season = default_season
        self.data_manager = DataManager()
        
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        layout.addRow(lang.get("new_char_dialog_prompt"), self.name_edit)

        self.realm_combo = QComboBox(self)
        self.realm_combo.addItems(self.realms)
        self.realm_combo.currentTextChanged.connect(self._on_realm_changed)
        layout.addRow(lang.get("new_char_realm_prompt"), self.realm_combo)
        
        # Class selection (BEFORE race)
        self.class_combo = QComboBox(self)
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        layout.addRow(lang.get("new_char_class_prompt", default="Classe :"), self.class_combo)
        
        # Race selection (AFTER class)
        self.race_combo = QComboBox(self)
        self.race_combo.currentTextChanged.connect(self._on_race_changed)
        layout.addRow(lang.get("new_char_race_prompt", default="Race :"), self.race_combo)
        
        # Season
        self.season_combo = QComboBox(self)
        self.season_combo.addItems(self.seasons)
        self.season_combo.setCurrentText(self.default_season)
        layout.addRow(lang.get("new_char_season_prompt", default="Saison :"), self.season_combo)
        # Connect signal for debugging
        self.season_combo.currentTextChanged.connect(self._on_season_changed)

        # Level dropdown (1-50)
        self.level_combo = QComboBox(self)
        for i in range(1, 51):
            self.level_combo.addItem(str(i))
        layout.addRow(lang.get("new_char_level_prompt", default="Niveau :"), self.level_combo)

        # Page dropdown (1-5)
        self.page_combo = QComboBox(self)
        for i in range(1, 6):
            self.page_combo.addItem(str(i))
        layout.addRow(lang.get("new_char_page_prompt", default="Page :"), self.page_combo)

        # Guild text input
        self.guild_edit = QLineEdit(self)
        layout.addRow(lang.get("new_char_guild_prompt", default="Guilde :"), self.guild_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize race and class combos with first realm
        if self.realms:
            self._on_realm_changed(self.realm_combo.currentText())

    def _on_realm_changed(self, realm):
        """Called when realm changes - updates available classes"""
        if not realm:
            return
        
        # Get current language
        current_lang = config.get("language", "fr")
        
        # Update classes
        self.class_combo.clear()
        classes = self.data_manager.get_classes(realm)
        
        lang_key = "name_fr" if current_lang == "fr" else "name_de" if current_lang == "de" else "name"
        for cls in classes:
            self.class_combo.addItem(cls.get(lang_key, cls["name"]), cls["name"])
        
        # Trigger class change to update races
        if classes:
            self._on_class_changed(classes[0]["name"])
    
    def _on_class_changed(self, class_display_name):
        """Called when class changes - filters available races"""
        realm = self.realm_combo.currentText()
        if not realm:
            return
        
        # Get the actual class name (stored in itemData)
        class_name = self.class_combo.currentData()
        if not class_name:
            return
        
        # Get current language
        current_lang = config.get("language", "fr")
        
        # Update races available for this class
        self.race_combo.clear()
        available_races = self.data_manager.get_available_races_for_class(realm, class_name)
        
        lang_key = "name_fr" if current_lang == "fr" else "name_de" if current_lang == "de" else "name"
        for race_info in available_races:
            self.race_combo.addItem(race_info.get(lang_key, race_info["name"]), race_info["name"])
    
    def _on_race_changed(self, race_display_name):
        """Called when race changes - validates the combination"""
        realm = self.realm_combo.currentText()
        race_name = self.race_combo.currentData()
        class_name = self.class_combo.currentData()
        
        if realm and race_name and class_name:
            if not self.data_manager.is_race_class_compatible(realm, race_name, class_name):
                logging.warning(f"Invalid combination: {race_name} cannot be {class_name}")

    def get_data(self):
        """Returns the entered data if valid."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, lang.get("error_title"), lang.get("char_name_empty_error"))
            return None
        realm = self.realm_combo.currentText()
        race = self.race_combo.currentData()  # Get actual race name
        class_name = self.class_combo.currentData()  # Get actual class name
        season = self.season_combo.currentText()
        level = int(self.level_combo.currentText())
        page = int(self.page_combo.currentText())
        guild = self.guild_edit.text().strip()
        
        # Validate race/class combination
        if race and class_name:
            if not self.data_manager.is_race_class_compatible(realm, race, class_name):
                QMessageBox.warning(
                    self,
                    lang.get("error_title"),
                    lang.get("invalid_race_class_combo", default=f"La race {race} ne peut pas jouer la classe {class_name}")
                )
                return None
        
        return name, realm, season, level, page, guild, race, class_name
    
    def _on_season_changed(self, new_season):
        logging.debug(f"New character dialog: Season changed to '{new_season}'")


class ConfigurationDialog(QDialog):
    """Configuration window for the application."""
    
    def __init__(self, parent=None, available_languages=None, available_seasons=None, available_servers=None, available_realms=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("configuration_window_title"))
        self.setMinimumSize(600, 500)
        self.resize(700, 700)  # Taille initiale confortable
        self.parent_app = parent
        self.available_languages = available_languages or {}
        self.available_seasons = available_seasons or []
        self.available_servers = available_servers or []
        self.available_realms = available_realms or []

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zone scrollable pour tout le contenu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Widget conteneur pour le contenu scrollable
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Paths Settings Group (Position 1)
        paths_group = QGroupBox(lang.get("config_paths_group_title", 
                                         default="Chemins des dossiers"))
        paths_layout = QFormLayout()

        # Character Path
        self.char_path_edit = QLineEdit()
        browse_char_button = QPushButton(lang.get("browse_button"))
        browse_char_button.clicked.connect(self.browse_character_folder)
        char_path_layout = QHBoxLayout()
        char_path_layout.addWidget(self.char_path_edit)
        char_path_layout.addWidget(browse_char_button)
        paths_layout.addRow(lang.get("config_path_label"), char_path_layout)

        # Config Path
        self.config_path_edit = QLineEdit()
        browse_config_button = QPushButton(lang.get("browse_button"))
        browse_config_button.clicked.connect(self.browse_config_folder)
        config_path_layout = QHBoxLayout()
        config_path_layout.addWidget(self.config_path_edit)
        config_path_layout.addWidget(browse_config_button)
        paths_layout.addRow(lang.get("config_file_path_label"), config_path_layout)

        # Log Path
        self.log_path_edit = QLineEdit()
        browse_log_button = QPushButton(lang.get("browse_button"))
        browse_log_button.clicked.connect(self.browse_log_folder)
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(browse_log_button)
        paths_layout.addRow(lang.get("config_log_path_label"), log_path_layout)

        # Armor Path
        self.armor_path_edit = QLineEdit()
        browse_armor_button = QPushButton(lang.get("browse_button"))
        browse_armor_button.clicked.connect(self.browse_armor_folder)
        armor_path_layout = QHBoxLayout()
        armor_path_layout.addWidget(self.armor_path_edit)
        armor_path_layout.addWidget(browse_armor_button)
        paths_layout.addRow(lang.get("config_armor_path_label"), armor_path_layout)

        # Cookies Path (for Herald scraping)
        self.cookies_path_edit = QLineEdit()
        browse_cookies_button = QPushButton(lang.get("browse_button"))
        browse_cookies_button.clicked.connect(self.browse_cookies_folder)
        cookies_path_layout = QHBoxLayout()
        cookies_path_layout.addWidget(self.cookies_path_edit)
        cookies_path_layout.addWidget(browse_cookies_button)
        paths_layout.addRow(lang.get("config_cookies_path_label"), cookies_path_layout)

        paths_group.setLayout(paths_layout)
        content_layout.addWidget(paths_group)

        # General Settings (Position 2)
        general_group = QGroupBox(lang.get("config_general_group_title", 
                                           default="Paramètres généraux"))
        general_layout = QFormLayout()

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.available_languages.values())
        general_layout.addRow(lang.get("config_language_label"), self.language_combo)
        
        # Theme
        from Functions.theme_manager import get_available_themes
        self.theme_combo = QComboBox()
        self.available_themes = get_available_themes()
        # Trier les thèmes par nom (alphabétique)
        sorted_themes = sorted(self.available_themes.items(), key=lambda x: x[1])
        for theme_id, theme_name in sorted_themes:
            self.theme_combo.addItem(theme_name, theme_id)
        general_layout.addRow(lang.get("config_theme_label"), self.theme_combo)
        
        # Font Scale ComboBox (100% à 200% par pas de 25%)
        self.font_scale_combo = QComboBox()
        self.font_scale_values = [1.0, 1.25, 1.5, 1.75, 2.0]  # 100%, 125%, 150%, 175%, 200%
        for scale in self.font_scale_values:
            self.font_scale_combo.addItem(f"{int(scale * 100)}%", scale)
        general_layout.addRow(lang.get("config_font_scale_label"), self.font_scale_combo)
        
        # Column resize mode
        self.manual_column_resize_check = QCheckBox(lang.get("config_manual_column_resize_label", 
                                                              default="Gestion manuelle de la taille des colonnes"))
        general_layout.addRow(self.manual_column_resize_check)
        
        # Preferred Browser
        from Functions.cookie_manager import CookieManager
        cookie_manager = CookieManager()
        available_browsers = cookie_manager.detect_available_browsers()
        
        self.browser_combo = QComboBox()
        # Toujours afficher tous les navigateurs possibles
        all_browsers = ['Chrome', 'Edge', 'Firefox']
        self.browser_combo.addItems(all_browsers)
        
        # Indiquer quels navigateurs sont détectés
        if available_browsers:
            tooltip = f"Navigateurs détectés sur cette machine: {', '.join(available_browsers)}"
        else:
            tooltip = "Aucun navigateur détecté. Sélectionnez celui à installer ou utiliser."
        self.browser_combo.setToolTip(tooltip)
        
        general_layout.addRow("🌐 Navigateur préféré:", self.browser_combo)
        
        # Allow browser download
        self.allow_browser_download_check = QCheckBox(
            "Autoriser le téléchargement automatique de drivers"
        )
        self.allow_browser_download_check.setToolTip(
            "Si activé, télécharge automatiquement le driver si le navigateur n'est pas trouvé.\n"
            "Nécessite une connexion Internet."
        )
        general_layout.addRow(self.allow_browser_download_check)
        
        general_group.setLayout(general_layout)
        content_layout.addWidget(general_group)

        # Server Settings (Position 3)
        server_group = QGroupBox(lang.get("config_season_group_title", 
                                          default="Configuration Serveur"))
        server_layout = QFormLayout()

        # Default Server
        self.default_server_combo = QComboBox()
        self.default_server_combo.addItems(self.available_servers)
        server_layout.addRow(lang.get("config_default_server_label", 
                                      default="Serveur par défaut"), 
                            self.default_server_combo)

        # Default Season
        self.default_season_combo = QComboBox()
        self.default_season_combo.addItems(self.available_seasons)
        server_layout.addRow(lang.get("config_default_season_label", 
                                     default="Saison par défaut"), 
                            self.default_season_combo)

        # Default Realm
        self.default_realm_combo = QComboBox()
        self.default_realm_combo.addItems(self.available_realms)
        server_layout.addRow(lang.get("config_default_realm_label", 
                                      default="Royaume par défaut"), 
                            self.default_realm_combo)

        server_group.setLayout(server_layout)
        content_layout.addWidget(server_group)

        # Debug Settings (Position 4 - Last)
        debug_group = QGroupBox(lang.get("config_debug_group_title", 
                                         default="Debug"))
        debug_layout = QFormLayout()

        # Debug Mode
        self.debug_mode_check = QCheckBox(lang.get("config_debug_mode_label"))
        debug_layout.addRow(self.debug_mode_check)

        # Show Debug Window
        self.show_debug_window_check = QCheckBox(lang.get("config_show_debug_window_label"))
        debug_layout.addRow(self.show_debug_window_check)
        
        debug_group.setLayout(debug_layout)
        content_layout.addWidget(debug_group)

        # Miscellaneous Settings Group (Position 5)
        misc_group = QGroupBox(lang.get("config_misc_group_title", 
                                        default="Divers"))
        misc_layout = QFormLayout()

        # Disable Disclaimer on Startup
        self.disable_disclaimer_check = QCheckBox(lang.get("config_disable_disclaimer_label", 
                                                            default="Désactiver le message d'avertissement au démarrage"))
        misc_layout.addRow(self.disable_disclaimer_check)
        
        misc_group.setLayout(misc_layout)
        content_layout.addWidget(misc_group)

        content_layout.addStretch()
        
        # Ajouter le widget de contenu à la zone scrollable
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.update_fields()

    def update_fields(self):
        """Fills the fields with current configuration values."""
        # Use 'or' to handle None or empty string values and fallback to default paths
        from Functions.path_manager import get_armor_dir
        
        char_folder = config.get("character_folder") or get_character_dir()
        config_folder = config.get("config_folder") or get_config_dir()
        log_folder = config.get("log_folder") or get_log_dir()
        armor_folder = config.get("armor_folder") or get_armor_dir()
        cookies_folder = config.get("cookies_folder") or get_config_dir()
        
        self.char_path_edit.setText(char_folder)
        self.char_path_edit.setCursorPosition(0)
        self.config_path_edit.setText(config_folder)
        self.config_path_edit.setCursorPosition(0)
        self.log_path_edit.setText(log_folder)
        self.log_path_edit.setCursorPosition(0)
        self.armor_path_edit.setText(armor_folder)
        self.armor_path_edit.setCursorPosition(0)
        self.cookies_path_edit.setText(cookies_folder)
        self.cookies_path_edit.setCursorPosition(0)
        self.debug_mode_check.setChecked(config.get("debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("show_debug_window", False))
        self.disable_disclaimer_check.setChecked(config.get("disable_disclaimer", False))
        
        current_lang_code = config.get("language", "fr")
        current_lang_name = self.available_languages.get(current_lang_code, "Français")
        self.language_combo.setCurrentText(current_lang_name)

        # Theme
        current_theme = config.get("theme", "default")
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        # Font Scale
        current_font_scale = config.get("font_scale", 1.0)
        # Trouver l'index correspondant à la valeur dans le ComboBox
        scale_index = self.font_scale_combo.findData(current_font_scale)
        if scale_index == -1:  # Si la valeur exacte n'existe pas, trouver la plus proche
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

        current_default_server = config.get("default_server", "")
        self.default_server_combo.setCurrentText(current_default_server)

        current_default_season = config.get("default_season", "")
        self.default_season_combo.setCurrentText(current_default_season)

        current_default_realm = config.get("default_realm", "")
        self.default_realm_combo.setCurrentText(current_default_realm)

        
        manual_resize = config.get("manual_column_resize", True)
        self.manual_column_resize_check.setChecked(manual_resize)        # Browser settings
        preferred_browser = config.get("preferred_browser", "Chrome")
        self.browser_combo.setCurrentText(preferred_browser)
        
        allow_download = config.get("allow_browser_download", False)
        self.allow_browser_download_check.setChecked(allow_download)

    def browse_folder(self, line_edit, title_key):
        """Generic folder browser."""
        directory = QFileDialog.getExistingDirectory(self, lang.get(title_key))
        if directory:
            line_edit.setText(directory)

    def browse_character_folder(self):
        self.browse_folder(self.char_path_edit, "select_folder_dialog_title")

    def browse_config_folder(self):
        self.browse_folder(self.config_path_edit, "select_config_folder_dialog_title")

    def browse_log_folder(self):
        self.browse_folder(self.log_path_edit, "select_log_folder_dialog_title")
    
    def browse_armor_folder(self):
        """Browse for armor folder."""
        self.browse_folder(self.armor_path_edit, "select_folder_dialog_title")
    
    def browse_cookies_folder(self):
        """Browse for cookies folder."""
        self.browse_folder(self.cookies_path_edit, "select_folder_dialog_title")


class ArmorManagementDialog(QDialog):
    """Dialog for managing armor files for a specific character."""
    
    def __init__(self, parent, character_id):
        super().__init__(parent)
        self.character_id = character_id
        
        from Functions.armor_manager import ArmorManager
        self.armor_manager = ArmorManager(character_id)
        
        self.setWindowTitle(f"Gestion des armures - Personnage {character_id}")
        self.resize(700, 450)
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel("Gérez les fichiers d'armure créés avec des logiciels tiers (formats : .png, .jpg, .pdf, .txt, etc.)")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Armor files table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nom du fichier", "Taille", "Date de modification", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        upload_button = QPushButton("📤 Uploader un fichier")
        upload_button.clicked.connect(self.upload_armor)
        button_layout.addWidget(upload_button)
        
        refresh_button = QPushButton("🔄 Actualiser")
        refresh_button.clicked.connect(self.refresh_list)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Load initial data
        self.refresh_list()
    
    def refresh_list(self):
        """Refreshes the armor files list."""
        try:
            armors = self.armor_manager.list_armors()
            self.table.setRowCount(len(armors))
            
            for row, armor in enumerate(armors):
                # Filename
                filename_item = QTableWidgetItem(armor['filename'])
                self.table.setItem(row, 0, filename_item)
                
                # Size
                size_mb = armor['size'] / (1024 * 1024)
                size_text = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{armor['size'] / 1024:.2f} KB"
                size_item = QTableWidgetItem(size_text)
                self.table.setItem(row, 1, size_item)
                
                # Modified date
                modified_date = datetime.fromtimestamp(armor['modified']).strftime("%d/%m/%Y %H:%M")
                date_item = QTableWidgetItem(modified_date)
                self.table.setItem(row, 2, date_item)
                
                # Actions buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 2, 4, 2)
                
                open_button = QPushButton("🔍 Ouvrir")
                open_button.setToolTip("Ouvrir le fichier avec l'application par défaut")
                open_button.clicked.connect(lambda checked, f=armor['filename']: self.open_armor(f))
                actions_layout.addWidget(open_button)
                
                delete_button = QPushButton("🗑️ Supprimer")
                delete_button.setToolTip("Supprimer ce fichier d'armure")
                delete_button.clicked.connect(lambda checked, f=armor['filename']: self.delete_armor(f))
                actions_layout.addWidget(delete_button)
                
                self.table.setCellWidget(row, 3, actions_widget)
            
            logging.info(f"Liste des armures actualisée : {len(armors)} fichier(s)")
            
        except Exception as e:
            logging.error(f"Erreur lors du rafraîchissement de la liste des armures : {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la liste des armures :\n{str(e)}")
    
    def upload_armor(self):
        """Opens file dialog to upload an armor file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier d'armure",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if file_path:
            try:
                result_path = self.armor_manager.upload_armor(file_path)
                QMessageBox.information(self, "Succès", f"Fichier uploadé avec succès :\n{os.path.basename(result_path)}")
                self.refresh_list()
                logging.info(f"Fichier d'armure uploadé : {result_path}")
            except Exception as e:
                logging.error(f"Erreur lors de l'upload du fichier d'armure : {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'uploader le fichier :\n{str(e)}")
    
    def open_armor(self, filename):
        """Opens an armor file with the default application."""
        try:
            self.armor_manager.open_armor(filename)
            logging.info(f"Ouverture du fichier d'armure : {filename}")
        except Exception as e:
            logging.error(f"Erreur lors de l'ouverture du fichier d'armure : {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier :\n{str(e)}")
    
    def delete_armor(self, filename):
        """Deletes an armor file after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le fichier '{filename}' ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.armor_manager.delete_armor(filename)
                QMessageBox.information(self, "Succès", f"Fichier '{filename}' supprimé avec succès.")
                self.refresh_list()
                logging.info(f"Fichier d'armure supprimé : {filename}")
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du fichier d'armure : {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le fichier :\n{str(e)}")


class ConnectionTestThread(QThread):
    """Thread pour tester la connexion Eden en arrière-plan"""
    finished = Signal(dict)  # Signal émis with the résultat of the test
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Ne pas stocker de référence à cookie_manager
        # pour éviter les problèmes si la fenêtre est détruite
    
    def run(self):
        """Exécute le test de connexion"""
        # Créer une instance locale de CookieManager pour éviter les références
        # à des objets détruits si la fenêtre est fermée pendant le test
        from Functions.cookie_manager import CookieManager
        cookie_manager = CookieManager()
        result = cookie_manager.test_eden_connection()
        self.finished.emit(result)


class CookieManagerDialog(QDialog):
    """Dialog pour gérer les cookies Eden pour le scraping"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Cookies Eden")
        self.resize(600, 400)
        
        # Importer le gestionnaire de cookies
        from Functions.cookie_manager import CookieManager
        self.cookie_manager = CookieManager()
        
        # Thread pour le test de connexion
        self.connection_thread = None
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Titre et description
        title_label = QLabel("<h2>🍪 Gestion des Cookies Eden</h2>")
        title_label.setTextFormat(Qt.RichText)
        layout.addWidget(title_label)
        
        layout.addSpacing(10)
        
        # Zone d'information sur les cookies
        info_group = QGroupBox("📊 État des Cookies")
        info_layout = QVBoxLayout()
        
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setTextFormat(Qt.RichText)
        info_layout.addWidget(self.status_label)
        
        self.expiry_label = QLabel()
        self.expiry_label.setWordWrap(True)
        self.expiry_label.setTextFormat(Qt.RichText)
        info_layout.addWidget(self.expiry_label)
        
        # Label for afficher the navigateur utilisé
        self.browser_label = QLabel()
        self.browser_label.setWordWrap(True)
        self.browser_label.setTextFormat(Qt.RichText)
        self.browser_label.setStyleSheet("color: #666; font-style: italic;")
        info_layout.addWidget(self.browser_label)
        
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        info_layout.addWidget(self.details_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Section import manuel
        import_group = QGroupBox("📂 Import Manuel")
        import_layout = QHBoxLayout()
        
        import_label = QLabel("Chemin du fichier :")
        import_layout.addWidget(import_label)
        
        self.cookie_path_edit = QLineEdit()
        self.cookie_path_edit.setPlaceholderText("Sélectionnez un fichier .pkl ou saisissez le chemin")
        self.cookie_path_edit.returnPressed.connect(self.import_from_path)
        import_layout.addWidget(self.cookie_path_edit)
        
        browse_button = QPushButton("📁 Parcourir")
        browse_button.clicked.connect(self.browse_cookie_file)
        import_layout.addWidget(browse_button)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("🔐 Générer des Cookies")
        self.generate_button.setToolTip("Ouvre un navigateur pour se connecter et récupérer les cookies")
        self.generate_button.clicked.connect(self.generate_cookies)
        buttons_layout.addWidget(self.generate_button)
        
        self.refresh_button = QPushButton("🔄 Actualiser")
        self.refresh_button.clicked.connect(self.refresh_status)
        buttons_layout.addWidget(self.refresh_button)
        
        self.delete_button = QPushButton("🗑️ Supprimer")
        self.delete_button.clicked.connect(self.delete_cookies)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        
        # Bouton de fermeture
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # Afficher l'état initial
        self.refresh_status()
    
    def start_connection_test(self):
        """Lance le test de connexion en arrière-plan"""
        # Annuler un test en cours si existant
        if self.connection_thread and self.connection_thread.isRunning():
            try:
                self.connection_thread.finished.disconnect()
            except:
                pass
            self.connection_thread.quit()
            self.connection_thread.wait()
        
        # Créer un nouveau thread avec la fenêtre principale comme parent
        # pour qu'il survive à la fermeture de cette fenêtre de dialog
        main_window = self.parent() if self.parent() else None
        self.connection_thread = ConnectionTestThread(parent=main_window)
        self.connection_thread.finished.connect(self.on_connection_test_finished)
        self.connection_thread.start()
    
    def on_connection_test_finished(self, result):
        """Appelé quand le test de connexion est terminé"""
        # Retrieve the infos actuelles for mettre à jour l'affichage
        info = self.cookie_manager.get_cookie_info()
        if info and info['is_valid']:
            expiry_date = info['expiry_date']
            now = datetime.now()
            duration = expiry_date - now
            days = duration.days
            
            # Construire le statut de connexion
            if result['accessible']:
                connection_status = "🌐 <b>Accès Eden :</b> <span style='color: green;'>✅ Connecté</span>"
            else:
                if result['status_code']:
                    connection_status = f"🌐 <b>Accès Eden :</b> <span style='color: red;'>❌ {result['message']}</span>"
                else:
                    connection_status = f"🌐 <b>Accès Eden :</b> <span style='color: orange;'>⚠️ {result['message']}</span>"
            
            # Mettre à jour l'affichage
            self.expiry_label.setText(
                f"📅 <b>Date d'expiration:</b> {expiry_date.strftime('%d/%m/%Y à %H:%M')}<br/>"
                f"⏰ <b>Validité restante:</b> {days} jours<br/>"
                f"{connection_status}"
            )
            
            # Afficher le navigateur utilisé pour le test (si disponible dans le résultat)
            browser_used = result.get('browser_used')
            if browser_used:
                browser_icon = {'Chrome': '🔵', 'Edge': '🔷', 'Firefox': '🦊'}.get(browser_used, '🌐')
                self.browser_label.setText(
                    f"{browser_icon} <i>Test effectué avec: {browser_used}</i>"
                )
            else:
                self.browser_label.setText("")
    
    def refresh_status(self):
        """Actualise l'affichage de l'état des cookies"""
        info = self.cookie_manager.get_cookie_info()
        
        if info is None:
            # Aucun cookie
            self.status_label.setText("❌ <b>Aucun cookie trouvé</b>")
            self.status_label.setStyleSheet("color: red;")
            self.expiry_label.setText("")
            self.details_label.setText(
                "Pour utiliser le scraper Eden, vous devez importer un fichier de cookies.<br/>"
                "Utilisez le bouton 'Importer des Cookies' ci-dessous."
            )
            self.delete_button.setEnabled(False)
            
        elif info.get('error'):
            # Erreur de lecture
            self.status_label.setText("⚠️ <b>Erreur de lecture</b>")
            self.status_label.setStyleSheet("color: orange;")
            self.expiry_label.setText("")
            self.details_label.setText(f"Erreur: {info['error']}")
            self.delete_button.setEnabled(True)
            
        elif not info['is_valid']:
            # Cookies expirés
            self.status_label.setText("⚠️ <b>Cookies expirés</b>")
            self.status_label.setStyleSheet("color: orange;")
            self.expiry_label.setText("")
            
            details = f"Total: {info['total_cookies']} cookies<br/>"
            details += f"Expirés: {info['expired_cookies']}<br/>"
            details += f"Valides: {info['valid_cookies']}<br/>"
            details += "<br/>Vous devez importer de nouveaux cookies."
            
            self.details_label.setText(details)
            self.delete_button.setEnabled(True)
            
        else:
            # Cookies valides
            self.status_label.setText("✅ <b>Cookies valides</b>")
            self.status_label.setStyleSheet("color: green;")
            
            expiry_date = info['expiry_date']
            now = datetime.now()
            duration = expiry_date - now
            days = duration.days
            
            self.expiry_label.setText(
                f"📅 <b>Date d'expiration:</b> {expiry_date.strftime('%d/%m/%Y à %H:%M')}<br/>"
                f"⏰ <b>Validité restante:</b> {days} jours"
            )
            
            if days < 7:
                self.expiry_label.setStyleSheet("color: orange;")
            else:
                self.expiry_label.setStyleSheet("color: green;")
            
            # Afficher the infos of base immédiatement
            self.expiry_label.setText(
                f"📅 <b>Date d'expiration:</b> {expiry_date.strftime('%d/%m/%Y à %H:%M')}<br/>"
                f"⏰ <b>Validité restante:</b> {days} jours<br/>"
                f"🌐 <b>Accès Eden :</b> <span style='color: gray;'>⏳ Test en cours...</span>"
            )
            
            # Lancer the test of connexion en arrière-plan
            self.start_connection_test()
            
            details = f"📦 Total: {info['total_cookies']} cookies<br/>"
            details += f"✓ Valides: {info['valid_cookies']}<br/>"
            
            if info['session_cookies'] > 0:
                details += f"🔄 Session: {info['session_cookies']}<br/>"
            
            details += f"<br/>📁 Fichier: {info['file_path']}"
            
            self.details_label.setText(details)
            self.delete_button.setEnabled(True)
        
        # Réinitialiser the label of the navigateur (sera mis à jour after test/génération)
        if not (info and info.get('is_valid')):
            self.browser_label.setText("")
    
    def browse_cookie_file(self):
        """Ouvre un dialog pour sélectionner un fichier de cookies"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier de cookies",
            "",
            "Fichiers Pickle (*.pkl);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.cookie_path_edit.setText(file_path)
            # Importer automatiquement after sélection
            self.import_from_path()
    
    def import_from_path(self):
        """Importe un fichier de cookies depuis le chemin saisi"""
        file_path = self.cookie_path_edit.text().strip()
        
        if not file_path:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner ou saisir un chemin de fichier."
            )
            return
        
        # Check that the File existe before d'essayer d'importer
        from pathlib import Path
        import os
        
        if not os.path.exists(file_path):
            QMessageBox.critical(
                self,
                "Erreur",
                f"Le fichier n'existe pas :\n\n{file_path}\n\n"
                "Vérifiez le chemin et réessayez."
            )
            return
        
        success = self.cookie_manager.import_cookie_file(file_path)
        
        if success:
            QMessageBox.information(
                self,
                "Succès",
                "Les cookies ont été importés avec succès !"
            )
            self.cookie_path_edit.clear()
            self.refresh_status()
            
            # Rafraîchir the statut Eden in the fenêtre principale
            if self.parent() and hasattr(self.parent(), 'ui_manager'):
                self.parent().ui_manager.check_eden_status()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible d'importer le fichier de cookies.\n\n"
                f"Fichier : {file_path}\n\n"
                "Le fichier doit être un fichier .pkl valide contenant des cookies."
            )
    
    def delete_cookies(self):
        """Supprime les cookies après confirmation"""
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer les cookies ?\n\n"
            "Une sauvegarde sera créée automatiquement.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.cookie_manager.delete_cookies()
            
            if success:
                QMessageBox.information(
                    self,
                    "Succès",
                    "Les cookies ont été supprimés."
                )
                self.refresh_status()
                
                # Rafraîchir the statut Eden in the fenêtre principale
                if self.parent() and hasattr(self.parent(), 'ui_manager'):
                    self.parent().ui_manager.check_eden_status()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de supprimer les cookies."
                )
    
    def generate_cookies(self):
        """Génère de nouveaux cookies via authentification navigateur (VERSION MIGRÉE)"""
        
        # Lire la configuration
        from Functions.config_manager import config
        preferred_browser = config.get('preferred_browser', 'Chrome')
        allow_download = config.get('allow_browser_download', False)
        
        # Import des composants
        from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
        
        # Construire les étapes (PAS de connexion Herald - génération cookies)
        steps = StepConfiguration.build_steps(
            StepConfiguration.COOKIE_GENERATION  # 6 étapes
        )
        
        # Créer le dialogue de progression
        self.progress_dialog = ProgressStepsDialog(
            parent=self,
            title=lang.get("progress_cookie_gen_title", default="🍪 Génération des cookies..."),
            steps=steps,
            description=lang.get("progress_cookie_gen_desc", default="Ouverture du navigateur pour authentification Discord"),
            show_progress_bar=True,
            determinate_progress=True,
            allow_cancel=True  # Permet annulation
        )
        
        # Créer le thread
        self.cookie_gen_thread = CookieGenThread(preferred_browser, allow_download)
        
        # ✅ Pattern 1: Connect via wrappers thread-safe
        self.cookie_gen_thread.step_started.connect(self._on_cookie_step_started)
        self.cookie_gen_thread.step_completed.connect(self._on_cookie_step_completed)
        self.cookie_gen_thread.step_error.connect(self._on_cookie_step_error)
        self.cookie_gen_thread.generation_finished.connect(self._on_cookie_generation_finished)
        self.cookie_gen_thread.user_action_required.connect(self._on_cookie_user_action_required)
        
        # ✅ Pattern 4: Connect rejected signal
        self.progress_dialog.rejected.connect(self._on_cookie_progress_dialog_closed)
        
        # Désactiver boutons pendant génération
        self.generate_button.setEnabled(False)
        self.cookie_path_edit.setEnabled(False)
        
        # Show dialog and start thread
        self.progress_dialog.show()
        self.cookie_gen_thread.start()
    
    # ============================================================================
    # WRAPPERS THREAD-SAFE POUR COOKIE GENERATION
    # ============================================================================
    
    def _on_cookie_step_started(self, step_index):
        """✅ Pattern 1: Wrapper thread-safe pour step_started"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.start_step(step_index)
            except RuntimeError:
                pass
    
    def _on_cookie_step_completed(self, step_index):
        """✅ Pattern 1: Wrapper thread-safe pour step_completed"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.complete_step(step_index)
            except RuntimeError:
                pass
    
    def _on_cookie_step_error(self, step_index, error_message):
        """✅ Pattern 1: Wrapper thread-safe pour step_error"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.error_step(step_index, error_message)
            except RuntimeError:
                pass
    
    def _on_cookie_user_action_required(self, browser_name, message):
        """Dialogue interactif pour confirmer connexion utilisateur (Étape 2)"""
        from PySide6.QtWidgets import QMessageBox
        
        # Créer dialogue de confirmation
        wait_msg = QMessageBox(self)
        wait_msg.setIcon(QMessageBox.Information)
        wait_msg.setWindowTitle("En attente de connexion")
        wait_msg.setTextFormat(Qt.RichText)
        wait_msg.setText("<b>Connectez-vous maintenant</b>")
        wait_msg.setInformativeText(message)
        wait_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        result = wait_msg.exec()
        
        # Informer le thread de la décision utilisateur
        if result == QMessageBox.Ok:
            self.cookie_gen_thread.set_user_confirmation(True)
        else:
            # Annulation
            self.cookie_gen_thread.set_user_confirmation(False)
            self._stop_cookie_gen_thread()
    
    def _on_cookie_progress_dialog_closed(self):
        """✅ Pattern 4: Arrêt propre quand dialog fermé par utilisateur"""
        import logging
        logging.info("Dialogue cookie gen fermé par utilisateur - Arrêt génération")
        self._stop_cookie_gen_thread()
    
    def _stop_cookie_gen_thread(self):
        """✅ Pattern 2+3: Arrêt propre du thread avec cleanup AVANT terminate"""
        if hasattr(self, 'cookie_gen_thread') and self.cookie_gen_thread:
            if self.cookie_gen_thread.isRunning():
                # ✅ Pattern 3: Demander arrêt gracieux
                self.cookie_gen_thread.request_stop()
                
                # Déconnecter les signaux
                try:
                    self.cookie_gen_thread.step_started.disconnect()
                    self.cookie_gen_thread.step_completed.disconnect()
                    self.cookie_gen_thread.step_error.disconnect()
                    self.cookie_gen_thread.generation_finished.disconnect()
                    self.cookie_gen_thread.user_action_required.disconnect()
                except:
                    pass
                
                # Attendre 3 secondes
                self.cookie_gen_thread.wait(3000)
                
                # ✅ Pattern 2: Cleanup AVANT terminate si toujours running
                if self.cookie_gen_thread.isRunning():
                    import logging
                    logging.warning("Thread cookie gen non terminé - Cleanup forcé")
                    self.cookie_gen_thread.cleanup_external_resources()
                    self.cookie_gen_thread.terminate()
                    self.cookie_gen_thread.wait()
                
                import logging
                logging.info("Thread cookie gen arrêté proprement")
            
            self.cookie_gen_thread = None
        
        # Nettoyer le dialogue
        if hasattr(self, 'progress_dialog'):
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
        
        # Réactiver boutons
        self.generate_button.setEnabled(True)
        self.cookie_path_edit.setEnabled(True)
    
    def _on_cookie_generation_finished(self, success, message, cookie_count):
        """Callback appelé quand la génération est terminée"""
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QMessageBox
        
        # Afficher succès/erreur dans le dialogue
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                if success:
                    success_text = lang.get("progress_cookie_success", default="✅ {count} cookies générés !", count=cookie_count)
                    self.progress_dialog.set_status_message(success_text, "#4CAF50")
                else:
                    error_text = lang.get("progress_error", default="❌ {error}", error=message)
                    self.progress_dialog.set_status_message(error_text, "#f44336")
                
                # Attendre 1.5s puis fermer
                QTimer.singleShot(1500, lambda: self._process_cookie_result(success, message, cookie_count))
            except RuntimeError:
                # Dialog déjà supprimé
                self._process_cookie_result(success, message, cookie_count)
        else:
            self._process_cookie_result(success, message, cookie_count)
    
    def _process_cookie_result(self, success, message, cookie_count):
        """Traiter le résultat de la génération après affichage du status"""
        # Fermer et nettoyer
        self._stop_cookie_gen_thread()
        
        # Afficher résultat final
        if success:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Succès",
                f"Les cookies ont été générés avec succès !\n\n{message}"
            )
        elif message and "Annulé" not in message:
            # Afficher erreur seulement si pas annulé
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la génération des cookies :\n\n{message}"
            )
        
        # Actualiser le statut
        self.refresh_status()
        
        # Rafraîchir le statut Eden dans la fenêtre principale si cookies générés
        if success and self.parent() and hasattr(self.parent(), 'ui_manager'):
            self.parent().ui_manager.check_eden_status()
    
    def closeEvent(self, event):
        """
        Gère la fermeture de la fenêtre.
        Le thread continue en arrière-plan (avec parent=main_window) jusqu'à sa fin naturelle.
        """
        # Si un thread de connexion est en cours, déconnecter notre callback
        # Le thread continuera avec son parent (main_window) et se terminera proprement
        if self.connection_thread and self.connection_thread.isRunning():
            try:
                self.connection_thread.finished.disconnect(self.on_connection_test_finished)
            except:
                pass
            # Ne plus garder de référence au thread
            self.connection_thread = None
        
        # Accepter la fermeture
        event.accept()


# ============================================================================
# COOKIE GENERATION THREAD
# ============================================================================

class CookieGenThread(QThread):
    """Thread pour générer les cookies Eden avec interaction utilisateur"""
    
    # Signaux
    generation_finished = Signal(bool, str, int)  # (success, message, cookie_count)
    step_started = Signal(int)  # (step_index)
    step_completed = Signal(int)  # (step_index)
    step_error = Signal(int, str)  # (step_index, error_message)
    user_action_required = Signal(str, str)  # (browser_name, message) - Pour dialogue interactif
    
    def __init__(self, preferred_browser=None, allow_download=False):
        super().__init__()
        self.preferred_browser = preferred_browser or 'Chrome'
        self.allow_download = allow_download
        
        # ✅ Pattern 3 : Flag d'interruption
        self._stop_requested = False
        
        # ✅ Pattern 2 : Référence ressource externe (driver Selenium)
        self._driver = None
        
        # Variable pour stocker si l'utilisateur a confirmé la connexion
        self._user_confirmed = False
    
    def request_stop(self):
        """✅ Pattern 3 : Demande arrêt gracieux"""
        self._stop_requested = True
    
    def cleanup_external_resources(self):
        """✅ Pattern 2 : Cleanup forcé du driver (appelé depuis thread principal)"""
        import logging
        logger = logging.getLogger(__name__)
        
        if self._driver:
            try:
                logger.info("Cleanup forcé : Fermeture navigateur cookies")
                self._driver.quit()
                logger.info("Navigateur fermé avec succès")
            except Exception as e:
                logger.warning(f"Erreur cleanup driver: {e}")
            finally:
                self._driver = None
    
    def set_user_confirmation(self, confirmed):
        """Appelé depuis le thread principal quand l'utilisateur confirme/annule"""
        self._user_confirmed = confirmed
    
    def run(self):
        """Exécute la génération de cookies avec sécurité thread"""
        import logging
        import time
        logger = logging.getLogger(__name__)
        
        from Functions.cookie_manager import CookieManager
        
        cookie_manager = CookieManager()
        driver = None
        
        # Variables pour résultat (émis APRÈS toutes les étapes)
        result_success = False
        result_message = ""
        result_count = 0
        
        try:
            # Étape 0 : Configuration du navigateur
            self.step_started.emit(0)
            logger.info(f"Configuration navigateur: {self.preferred_browser}, download={self.allow_download}")
            time.sleep(0.5)  # Simuler configuration
            self.step_completed.emit(0)
            
            if self._stop_requested:
                return
            
            # Étape 1 : Ouverture de la page de connexion
            self.step_started.emit(1)
            logger.info("Initialisation navigateur pour génération cookies...")
            
            success, message, driver = cookie_manager.generate_cookies_with_browser(
                preferred_browser=self.preferred_browser,
                allow_download=self.allow_download
            )
            
            if not success:
                error_msg = f"Impossible d'ouvrir le navigateur: {message}"
                logger.error(error_msg)
                self.step_error.emit(1, error_msg)
                result_message = error_msg
                return
            
            self._driver = driver  # ✅ Pattern 2 : Stocker pour cleanup externe
            browser_name = getattr(cookie_manager, 'last_browser_used', 'navigateur')
            
            logger.info(f"Navigateur {browser_name} ouvert avec succès")
            self.step_completed.emit(1)
            
            if self._stop_requested:
                return
            
            # Étape 2 : En attente de la connexion utilisateur (INTERACTIF)
            self.step_started.emit(2)
            logger.info("Attente connexion utilisateur...")
            
            # Émettre signal pour demander confirmation utilisateur
            self.user_action_required.emit(
                browser_name,
                f"Le navigateur {browser_name} est ouvert.\n\nConnectez-vous avec Discord, puis cliquez sur OK."
            )
            
            # Attendre confirmation avec sleep interruptible (max 5 minutes)
            wait_seconds = 0
            max_wait = 300  # 5 minutes
            
            while not self._user_confirmed and wait_seconds < max_wait:
                if self._stop_requested:
                    logger.info("Arrêt demandé pendant attente utilisateur")
                    result_message = "Annulé par l'utilisateur"
                    return
                
                time.sleep(0.5)
                wait_seconds += 0.5
            
            if not self._user_confirmed:
                error_msg = "Timeout : Aucune confirmation utilisateur après 5 minutes"
                logger.warning(error_msg)
                self.step_error.emit(2, "Timeout")
                result_message = error_msg
                return
            
            logger.info("Connexion utilisateur confirmée")
            self.step_completed.emit(2)
            
            if self._stop_requested:
                return
            
            # Étape 3 : Extraction des cookies
            self.step_started.emit(3)
            logger.info("Extraction des cookies depuis le navigateur...")
            
            # Les cookies sont déjà dans le driver, on passe à la sauvegarde
            time.sleep(0.5)  # Petit délai pour laisser les cookies se stabiliser
            
            logger.info("Cookies extraits")
            self.step_completed.emit(3)
            
            if self._stop_requested:
                return
            
            # Étape 4 : Sauvegarde des cookies
            self.step_started.emit(4)
            logger.info("Sauvegarde des cookies...")
            
            success, message, count = cookie_manager.save_cookies_from_driver(driver)
            
            if not success:
                error_msg = f"Erreur sauvegarde cookies: {message}"
                logger.error(error_msg)
                self.step_error.emit(4, error_msg)
                result_message = error_msg
                return
            
            logger.info(f"Cookies sauvegardés: {count}")
            self.step_completed.emit(4)
            
            if self._stop_requested:
                return
            
            # Étape 5 : Validation et vérification
            self.step_started.emit(5)
            logger.info("Validation des cookies...")
            
            # Vérifier que les cookies sont valides
            info = cookie_manager.get_cookie_info()
            if info and info.get('is_valid'):
                logger.info("Cookies validés avec succès")
                self.step_completed.emit(5)
                
                # Stocker le succès
                result_success = True
                result_message = message
                result_count = count
            else:
                error_msg = "Les cookies sauvegardés ne sont pas valides"
                logger.error(error_msg)
                self.step_error.emit(5, error_msg)
                result_message = error_msg
        
        except Exception as e:
            logger.error(f"Erreur génération cookies: {e}", exc_info=True)
            result_message = f"Erreur: {str(e)}"
        
        finally:
            # Fermeture du navigateur (pas d'étape dédiée dans COOKIE_GENERATION)
            if driver:
                try:
                    logger.info("Fermeture navigateur cookies...")
                    driver.quit()
                    logger.info("Navigateur fermé")
                except Exception as e:
                    logger.warning(f"Erreur fermeture navigateur: {e}")
            
            # Émettre le signal final
            logger.info(f"Émission signal generation_finished - success={result_success}, count={result_count}")
            self.generation_finished.emit(result_success, result_message, result_count)


# ============================================================================
# HERALD SEARCH DIALOG
# ============================================================================

class SearchThread(QThread):
    """Thread pour effectuer la recherche Herald en arrière-plan"""
    search_finished = Signal(bool, str, str)  # (success, message, json_path)
    progress_update = Signal(str)  # (status_message) - LEGACY pour compatibilité
    step_started = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_completed = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_error = Signal(int, str)  # (step_index, error_message) - NOUVEAU pour ProgressStepsDialog
    
    def __init__(self, character_name, realm_filter=""):
        super().__init__()
        self.character_name = character_name
        self.realm_filter = realm_filter
        self._stop_requested = False  # Flag pour arrêt gracieux
        self._scraper = None  # Référence au scraper pour cleanup externe
    
    def request_stop(self):
        """Demande l'arrêt du thread (appelé depuis le thread principal)"""
        self._stop_requested = True
    
    def cleanup_driver(self):
        """Ferme le navigateur de manière sécurisée (appelé depuis thread principal)"""
        import logging
        module_logger = logging.getLogger(__name__)
        
        if self._scraper and hasattr(self._scraper, 'driver') and self._scraper.driver:
            try:
                module_logger.info("Cleanup: Fermeture forcée du navigateur")
                self._scraper.driver.quit()
                module_logger.info("Cleanup: Navigateur fermé avec succès")
            except Exception as e:
                module_logger.warning(f"Cleanup: Erreur lors de la fermeture: {e}")
            finally:
                self._scraper = None
    
    def _emit_step_start(self, step_index, message):
        """Émet les signaux de début d'étape (nouveau + legacy)"""
        self.step_started.emit(step_index)
        self.progress_update.emit(message)  # Garde compatibilité
    
    def _emit_step_complete(self, step_index):
        """Émet le signal de fin d'étape"""
        self.step_completed.emit(step_index)
    
    def run(self):
        """Exécute la recherche avec des mises à jour de progression"""
        from Functions.cookie_manager import CookieManager
        from Functions.eden_scraper import EdenScraper
        from bs4 import BeautifulSoup
        from datetime import datetime
        from pathlib import Path
        import tempfile
        import time
        import json
        import logging
        
        module_logger = logging.getLogger(__name__)
        scraper = None
        
        # Variables pour résultat (signal émis APRÈS Step 8 dans finally)
        result_success = False
        result_message = ""
        result_json_path = ""
        
        try:
            # Étape 0 : Vérification des cookies
            self._emit_step_start(0, "🔐 Vérification des cookies d'authentification...")
            module_logger.info(f"Début de la recherche Herald pour: {self.character_name}", extra={"action": "SEARCH"})
            
            cookie_manager = CookieManager()
            
            if not cookie_manager.cookie_exists():
                module_logger.error("Aucun cookie trouvé", extra={"action": "SEARCH"})
                self.step_error.emit(0, "Aucun cookie trouvé")
                result_message = "Aucun cookie trouvé. Veuillez générer ou importer des cookies d'abord."
                return
            
            info = cookie_manager.get_cookie_info()
            if not info or not info.get('is_valid'):
                module_logger.error("Cookies expirés", extra={"action": "SEARCH"})
                self.step_error.emit(0, "Cookies expirés")
                result_message = "Les cookies ont expiré. Veuillez les regénérer."
                return
            
            module_logger.info(f"Cookies valides - {info.get('cookie_count', 0)} cookies chargés", extra={"action": "SEARCH"})
            self._emit_step_complete(0)
            
            # Étape 1 : Initialisation du navigateur
            self._emit_step_start(1, "🌐 Initialisation du navigateur Chrome...")
            scraper = EdenScraper(cookie_manager)
            self._scraper = scraper  # Stocke référence pour cleanup externe
            
            if not scraper.initialize_driver(headless=False):
                module_logger.error("Impossible d'initialiser le navigateur", extra={"action": "SEARCH"})
                self.step_error.emit(1, "Impossible d'initialiser le navigateur")
                result_message = "Impossible d'initialiser le navigateur Chrome."
                return
            
            module_logger.info("Navigateur initialisé avec succès", extra={"action": "SEARCH"})
            self._emit_step_complete(1)
            
            # Étape 2 : Chargement des cookies
            self._emit_step_start(2, "🍪 Chargement des cookies dans le navigateur...")
            if not scraper.load_cookies():
                module_logger.error("Impossible de charger les cookies dans le navigateur", extra={"action": "SEARCH"})
                self.step_error.emit(2, "Impossible de charger les cookies")
                result_message = "Impossible de charger les cookies."
                return
            
            module_logger.info("Cookies chargés dans le navigateur - Authentification complétée", extra={"action": "SEARCH"})
            self._emit_step_complete(2)
            
            # Vérifier si arrêt demandé
            if self._stop_requested:
                module_logger.info("Arrêt demandé par l'utilisateur (après étape 2)", extra={"action": "SEARCH"})
                return
            
            # Étape 3 : Navigation vers la page de recherche
            if self.realm_filter:
                search_url = f"https://eden-daoc.net/herald?n=search&r={self.realm_filter}&s={self.character_name}"
            else:
                search_url = f"https://eden-daoc.net/herald?n=search&s={self.character_name}"
            
            self._emit_step_start(3, f"🔍 Recherche de '{self.character_name}' sur Eden Herald...")
            module_logger.info(f"Recherche Herald: {search_url}", extra={"action": "SEARCH"})
            
            scraper.driver.get(search_url)
            self._emit_step_complete(3)
            
            # Vérifier si arrêt demandé
            if self._stop_requested:
                module_logger.info("Arrêt demandé par l'utilisateur (après étape 3)", extra={"action": "SEARCH"})
                return
            
            # Étape 4 : Attente du chargement de la page
            self._emit_step_start(4, "⏳ Chargement de la page de recherche...")
            module_logger.info("Attente du chargement de la page de recherche (5 secondes)...", extra={"action": "SEARCH"})
            
            # Sleep interruptible (vérifier le flag toutes les 0.5 secondes)
            for i in range(10):  # 10 x 0.5s = 5s
                if self._stop_requested:
                    module_logger.info("Arrêt demandé par l'utilisateur (pendant sleep)", extra={"action": "SEARCH"})
                    return
                time.sleep(0.5)
            
            self._emit_step_complete(4)
            
            # Vérifier si arrêt demandé
            if self._stop_requested:
                module_logger.info("Arrêt demandé par l'utilisateur (après étape 4)", extra={"action": "SEARCH"})
                return
            
            # Étape 5 : Extraction des données
            self._emit_step_start(5, "📊 Extraction des résultats de recherche...")
            page_source = scraper.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            module_logger.info(f"Page chargée - Taille: {len(page_source)} caractères", extra={"action": "SEARCH"})
            
            # Extract data de recherche
            search_data = {
                'character_name': self.character_name,
                'search_url': search_url,
                'timestamp': datetime.now().isoformat(),
                'results': []
            }
            
            # Search results in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 1:  # Au moins un header et une ligne
                    headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
                    
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if cells:
                            result = {}
                            for idx, cell in enumerate(cells):
                                header = headers[idx] if idx < len(headers) else f"col_{idx}"
                                result[header] = cell.get_text(strip=True)
                                
                                # Extraire les liens
                                links = cell.find_all('a')
                                if links:
                                    result[f"{header}_links"] = [a.get('href', '') for a in links]
                            
                            if result:
                                search_data['results'].append(result)
            
            self._emit_step_complete(5)
            
            # Étape 6 : Sauvegarde des résultats
            self._emit_step_start(6, "💾 Sauvegarde des résultats...")
            
            # Utiliser le dossier temporaire de l'OS
            temp_dir = Path(tempfile.gettempdir()) / "EdenSearchResult"
            temp_dir.mkdir(exist_ok=True)
            
            module_logger.info(f"Dossier temporaire: {temp_dir}", extra={"action": "CLEANUP"})
            
            # Clean old files before creating new ones
            old_files_list = list(temp_dir.glob("*.json"))
            if old_files_list:
                module_logger.info(f"Nettoyage de {len(old_files_list)} fichier(s) ancien(s)...", extra={"action": "CLEANUP"})
                
                for old_file in old_files_list:
                    try:
                        module_logger.debug(f"Suppression: {old_file.name}", extra={"action": "CLEANUP"})
                        old_file.unlink()
                        module_logger.info(f"✅ Fichier supprimé: {old_file.name}", extra={"action": "CLEANUP"})
                    except Exception as e:
                        module_logger.warning(f"❌ Impossible de supprimer {old_file.name}: {e}", extra={"action": "CLEANUP"})
            else:
                module_logger.info("Aucun ancien fichier à nettoyer", extra={"action": "CLEANUP"})
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"search_{self.character_name}_{timestamp}.json"
            json_path = temp_dir / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, indent=2, ensure_ascii=False)
            
            self._emit_step_complete(6)
            
            # Étape 7 : Formatage des personnages
            self._emit_step_start(7, "🎯 Formatage des personnages trouvés...")
            characters = []
            for result in search_data['results']:
                # Check if it's a character row
                if (result.get('col_1') and 
                    result.get('col_3') and 
                    len(result.get('col_1', '')) > 0 and
                    result.get('col_0') and
                    result.get('col_0', '').isdigit()):
                    
                    rank = result.get('col_0', '')
                    name = result.get('col_1', '').strip()
                    char_class = result.get('col_3', '').strip()
                    race = result.get('col_5', '').strip()
                    guild = result.get('col_7', '').strip()
                    level = result.get('col_8', '').strip()
                    rp = result.get('col_9', '').strip()
                    realm_rank = result.get('col_10', '').strip()
                    realm_level = result.get('col_11', '').strip()
                    
                    # Extraire l'URL depuis les liens (col_1 contient le nom avec le lien)
                    url = ""
                    if 'col_1_links' in result and result['col_1_links']:
                        href = result['col_1_links'][0]
                        if href.startswith('?'):
                            url = f"https://eden-daoc.net/herald{href}"
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = f"https://eden-daoc.net{href}"
                    else:
                        # Fallback : construire l'URL à partir du nom si aucun lien trouvé
                        clean_name = name.split()[0] if name else ""
                        if clean_name:
                            url = f"https://eden-daoc.net/herald?n=player&k={clean_name}"
                    
                    # Nettoyer le nom (retirer les codes couleur HTML)
                    import re
                    clean_name = re.sub(r'<[^>]+>', '', name)
                    
                    characters.append({
                        'rank': rank,
                        'name': name,
                        'clean_name': clean_name,
                        'class': char_class,
                        'race': race,
                        'guild': guild,
                        'level': level,
                        'realm_points': rp,
                        'realm_rank': realm_rank,
                        'realm_level': realm_level,
                        'url': url
                    })
            
            # Ajouter la liste formatée au JSON
            search_data['characters'] = characters
            search_data['search_query'] = self.character_name
            
            # Re-sauvegarder avec les données formatées
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, indent=2, ensure_ascii=False)
            
            module_logger.info(f"{len(characters)} personnage(s) trouvé(s) et sauvegardé(s) dans: {json_path}", extra={"action": "SEARCH"})
            self._emit_step_complete(7)
            
            # Pas d'étape 8 ici (fermeture navigateur) - sera dans finally
            
            # Stocker le succès (signal émis APRÈS Step 8 dans finally)
            result_success = True
            result_message = f"{len(characters)} personnage(s) trouvé(s)"
            result_json_path = str(json_path)
            
        except Exception as e:
            module_logger.error(f"Erreur lors de la recherche: {str(e)}", extra={"action": "SEARCH"}, exc_info=True)
            result_message = f"Erreur: {str(e)}"
            
        finally:
            # Étape 8 : Fermer le navigateur proprement
            if scraper and scraper.driver:
                try:
                    self._emit_step_start(8, "🔄 Fermeture du navigateur...")
                    scraper.driver.quit()
                    module_logger.info("Navigateur fermé", extra={"action": "SEARCH"})
                    self._emit_step_complete(8)
                except Exception as e:
                    module_logger.warning(f"Erreur lors de la fermeture du navigateur: {e}", extra={"action": "SEARCH"})
                    self.step_error.emit(8, f"Erreur fermeture: {str(e)}")
            
            # Émettre le signal APRÈS Step 8 (fermeture complète)
            module_logger.info(f"Émission signal search_finished - success={result_success}, message={result_message}")
            self.search_finished.emit(result_success, result_message, result_json_path)


# ============================================================================
# STATS UPDATE THREAD (RvR/PvP/PvE/Wealth/Achievements)
# ============================================================================

class StatsUpdateThread(QThread):
    """Thread pour mettre à jour les statistiques depuis le Herald"""
    
    # Signaux
    stats_updated = Signal(dict)  # (results_dict) - Émis quand mise à jour terminée avec succès
    update_failed = Signal(str)  # (error_message) - Émis en cas d'échec complet
    step_started = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_completed = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_error = Signal(int, str)  # (step_index, error_message) - NOUVEAU pour ProgressStepsDialog
    
    def __init__(self, character_url):
        super().__init__()
        self.character_url = character_url
        
        # ✅ Pattern 3 : Flag d'interruption
        self._stop_requested = False
        
        # ✅ Pattern 2 : Référence ressource externe (scraper)
        self._scraper = None
    
    def request_stop(self):
        """✅ Pattern 3 : Demande arrêt gracieux"""
        self._stop_requested = True
    
    def cleanup_external_resources(self):
        """✅ Pattern 2 : Cleanup forcé du scraper (appelé depuis thread principal)"""
        import logging
        logger = logging.getLogger(__name__)
        
        if self._scraper:
            try:
                logger.info("Cleanup forcé : Fermeture scraper stats")
                self._scraper.close()
                logger.info("Scraper fermé avec succès")
            except Exception as e:
                logger.warning(f"Erreur cleanup scraper: {e}")
            finally:
                self._scraper = None
    
    def run(self):
        """Exécute la mise à jour des statistiques avec sécurité thread"""
        import logging
        logger = logging.getLogger(__name__)
        
        from Functions.character_profile_scraper import CharacterProfileScraper
        
        scraper = None
        results = {
            'success': False,
            'rvr': None,
            'pvp': None,
            'pve': None,
            'wealth': None,
            'achievements': None,
            'error': None
        }
        
        # Variables pour signal (émis APRÈS Step 6 dans finally)
        emit_signal = None  # 'stats_updated' ou 'update_failed'
        emit_data = None    # results ou error_message
        
        try:
            # Étape 0 : Initialisation du scraper
            self.step_started.emit(0)
            logger.info(f"Initialisation scraper pour {self.character_url}")
            
            scraper = CharacterProfileScraper()
            self._scraper = scraper  # ✅ Pattern 2 : Stocker pour cleanup externe
            
            success, error_message = scraper.connect(headless=False)
            
            if not success:
                logger.error(f"Échec connexion scraper: {error_message}")
                self.step_error.emit(0, f"Connexion impossible: {error_message}")
                emit_signal = 'update_failed'
                emit_data = f"Impossible de se connecter au Herald Eden:\n{error_message}"
                return
            
            logger.info("Scraper initialisé avec succès")
            self.step_completed.emit(0)
            
            # ✅ Pattern 3 : Check après opération critique
            if self._stop_requested:
                logger.info("Arrêt demandé après init scraper")
                return
            
            # Étape 1 : Scraping RvR Captures
            self.step_started.emit(1)
            logger.info("Scraping RvR captures...")
            
            results['rvr'] = scraper.scrape_rvr_captures(self.character_url)
            
            if results['rvr']['success']:
                logger.info(f"RvR captures récupérées: T={results['rvr']['tower_captures']}, K={results['rvr']['keep_captures']}, R={results['rvr']['relic_captures']}")
                self.step_completed.emit(1)
            else:
                logger.warning(f"Échec RvR: {results['rvr'].get('error', 'Erreur inconnue')}")
                self.step_error.emit(1, f"RvR: {results['rvr'].get('error', 'Erreur inconnue')}")
            
            if self._stop_requested:
                return
            
            # Étape 2 : Scraping PvP Stats
            self.step_started.emit(2)
            logger.info("Scraping PvP stats...")
            
            results['pvp'] = scraper.scrape_pvp_stats(self.character_url)
            
            if results['pvp']['success']:
                logger.info(f"PvP stats récupérées: SK={results['pvp']['solo_kills']}, DB={results['pvp']['deathblows']}, K={results['pvp']['kills']}")
                self.step_completed.emit(2)
            else:
                logger.warning(f"Échec PvP: {results['pvp'].get('error', 'Erreur inconnue')}")
                self.step_error.emit(2, f"PvP: {results['pvp'].get('error', 'Erreur inconnue')}")
            
            if self._stop_requested:
                return
            
            # Étape 3 : Scraping PvE Stats
            self.step_started.emit(3)
            logger.info("Scraping PvE stats...")
            
            results['pve'] = scraper.scrape_pve_stats(self.character_url)
            
            if results['pve']['success']:
                logger.info(f"PvE stats récupérées: Dragons={results['pve']['dragon_kills']}, Legion={results['pve']['legion_kills']}")
                self.step_completed.emit(3)
            else:
                logger.warning(f"Échec PvE: {results['pve'].get('error', 'Erreur inconnue')}")
                self.step_error.emit(3, f"PvE: {results['pve'].get('error', 'Erreur inconnue')}")
            
            if self._stop_requested:
                return
            
            # Étape 4 : Scraping Wealth (Money)
            self.step_started.emit(4)
            logger.info("Scraping wealth...")
            
            results['wealth'] = scraper.scrape_wealth_money(self.character_url)
            
            if results['wealth']['success']:
                logger.info(f"Wealth récupérée: {results['wealth']['money']}")
                self.step_completed.emit(4)
            else:
                logger.warning(f"Échec Wealth: {results['wealth'].get('error', 'Erreur inconnue')}")
                self.step_error.emit(4, f"Wealth: {results['wealth'].get('error', 'Erreur inconnue')}")
            
            if self._stop_requested:
                return
            
            # Étape 5 : Scraping Achievements (conditionnel - ne bloque pas si échec)
            self.step_started.emit(5)
            logger.info("Scraping achievements...")
            
            results['achievements'] = scraper.scrape_achievements(self.character_url)
            
            if results['achievements']['success']:
                logger.info(f"Achievements récupérés: {len(results['achievements']['achievements'])} achievements")
                self.step_completed.emit(5)
            else:
                logger.warning(f"Échec Achievements: {results['achievements'].get('error', 'Erreur inconnue')}")
                # Pas d'erreur bloquante pour achievements
                self.step_completed.emit(5)  # Marqué complété même si échec (conditionnel)
            
            # Vérifier si au moins RvR/PvP/PvE/Wealth ont réussi
            all_critical_success = (
                results['rvr']['success'] and 
                results['pvp']['success'] and 
                results['pve']['success'] and 
                results['wealth']['success']
            )
            
            if all_critical_success:
                results['success'] = True
                logger.info("Toutes les stats critiques récupérées avec succès")
                emit_signal = 'stats_updated'
                emit_data = results
            else:
                # Échec partiel ou complet
                error_parts = []
                if not results['rvr']['success']:
                    error_parts.append(f"RvR: {results['rvr'].get('error', '?')}")
                if not results['pvp']['success']:
                    error_parts.append(f"PvP: {results['pvp'].get('error', '?')}")
                if not results['pve']['success']:
                    error_parts.append(f"PvE: {results['pve'].get('error', '?')}")
                if not results['wealth']['success']:
                    error_parts.append(f"Wealth: {results['wealth'].get('error', '?')}")
                
                error_msg = "Échec de récupération:\n" + "\n".join(error_parts)
                results['error'] = error_msg
                logger.error(f"Échec mise à jour stats: {error_msg}")
                
                # Émettre quand même results pour mise à jour partielle possible
                emit_signal = 'stats_updated'
                emit_data = results
        
        except Exception as e:
            logger.error(f"Erreur update stats: {e}", exc_info=True)
            emit_signal = 'update_failed'
            emit_data = f"Erreur inattendue: {str(e)}"
        
        finally:
            # ✅ Pattern 2 : Cleanup normal (s'exécute si pas terminate())
            # Étape 6 : Fermeture scraper
            if scraper:
                try:
                    self.step_started.emit(6)
                    logger.info("Fermeture scraper...")
                    scraper.close()
                    logger.info("Scraper fermé")
                    self.step_completed.emit(6)
                except Exception as e:
                    logger.warning(f"Erreur fermeture scraper: {e}")
                    self.step_error.emit(6, f"Erreur fermeture: {str(e)}")
            
            # Émettre le signal APRÈS Step 6 (fermeture complète)
            if emit_signal == 'stats_updated':
                logger.info(f"Émission signal stats_updated - success={emit_data.get('success', False)}")
                self.stats_updated.emit(emit_data)
            elif emit_signal == 'update_failed':
                logger.info(f"Émission signal update_failed - error={emit_data}")
                self.update_failed.emit(emit_data)


# ============================================================================
# CHARACTER UPDATE THREAD (Herald Character Data Update)
# ============================================================================

class CharacterUpdateThread(QThread):
    """Thread pour mettre à jour les données d'un personnage depuis Herald"""
    
    # Signaux
    update_finished = Signal(bool, object, str)  # (success, new_data, error_msg)
    step_started = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_completed = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog  
    step_error = Signal(int, str)  # (step_index, error_message) - NOUVEAU pour ProgressStepsDialog
    
    def __init__(self, character_url):
        super().__init__()
        self.character_url = character_url
        
        # ✅ Pattern 3 : Flag d'interruption
        self._stop_requested = False
        
        # ✅ Pattern 2 : Référence ressource externe (scraper Selenium)
        self._scraper = None
    
    def request_stop(self):
        """✅ Pattern 3 : Demande arrêt gracieux"""
        self._stop_requested = True
    
    def cleanup_external_resources(self):
        """✅ Pattern 2 : Cleanup forcé du scraper Selenium (appelé depuis thread principal)"""
        import logging
        logger = logging.getLogger(__name__)
        
        if self._scraper:
            try:
                logger.info("Cleanup forcé : Fermeture scraper character update")
                self._scraper.close()
                logger.info("Scraper fermé avec succès")
            except Exception as e:
                logger.warning(f"Erreur cleanup scraper: {e}")
            finally:
                self._scraper = None
    
    def run(self):
        """Exécute la mise à jour du personnage avec sécurité thread"""
        import logging
        import time
        import traceback
        from datetime import datetime
        from urllib.parse import urlparse, parse_qs
        from bs4 import BeautifulSoup
        
        logger = logging.getLogger(__name__)
        
        from Functions.cookie_manager import CookieManager
        from Functions.eden_scraper import EdenScraper, _normalize_herald_data
        
        scraper = None
        
        # Variables pour stocker le résultat (émis APRÈS Step 7 dans finally)
        result_success = False
        result_data = None
        result_error = ""
        
        try:
            # Étape 0 : Extraction du nom du personnage depuis URL
            self.step_started.emit(0)
            logger.info(f"Extraction nom depuis URL: {self.character_url}")
            
            parsed_url = urlparse(self.character_url)
            query_params = parse_qs(parsed_url.query)
            character_name = query_params.get('k', [''])[0]
            
            if not character_name:
                error_msg = "Impossible d'extraire le nom du personnage de l'URL"
                logger.error(error_msg)
                self.step_error.emit(0, error_msg)
                result_error = error_msg
                return
            
            logger.info(f"Nom extrait: {character_name}")
            self.step_completed.emit(0)
            
            # ✅ Pattern 3 : Check après opération critique
            if self._stop_requested:
                logger.info("Arrêt demandé après extraction nom")
                return
            
            # Étape 1 : Initialisation du scraper
            self.step_started.emit(1)
            logger.info("Initialisation scraper Herald...")
            
            cookie_manager = CookieManager()
            scraper = EdenScraper(cookie_manager)
            self._scraper = scraper  # ✅ Pattern 2 : Stocker pour cleanup externe
            
            if not scraper.initialize_driver(headless=False):
                error_msg = "Impossible d'initialiser le navigateur"
                logger.error(error_msg)
                self.step_error.emit(1, error_msg)
                result_error = error_msg
                return
            
            logger.info("Scraper initialisé")
            self.step_completed.emit(1)
            
            if self._stop_requested:
                return
            
            # Étape 2 : Chargement des cookies
            self.step_started.emit(2)
            logger.info("Chargement des cookies...")
            
            if not scraper.load_cookies():
                error_msg = "Impossible de charger les cookies"
                logger.error(error_msg)
                self.step_error.emit(2, error_msg)
                result_error = error_msg
                return
            
            logger.info("Cookies chargés")
            self.step_completed.emit(2)
            
            if self._stop_requested:
                return
            
            # Étape 3 : Navigation vers la page de recherche
            self.step_started.emit(3)
            search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
            logger.info(f"Navigation vers: {search_url}")
            
            scraper.driver.get(search_url)
            
            logger.info("Page chargée")
            self.step_completed.emit(3)
            
            if self._stop_requested:
                return
            
            # Étape 4 : Attente du chargement (interruptible)
            self.step_started.emit(4)
            logger.info("Attente chargement page...")
            
            # ✅ Pattern 3 : Sleep interruptible (5 secondes)
            for i in range(10):  # 10 x 0.5s = 5s
                if self._stop_requested:
                    logger.info("Arrêt demandé pendant sleep")
                    return
                time.sleep(0.5)
            
            logger.info("Chargement terminé")
            self.step_completed.emit(4)
            
            if self._stop_requested:
                return
            
            # Étape 5 : Extraction des données
            self.step_started.emit(5)
            logger.info("Extraction données HTML...")
            
            page_source = scraper.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            logger.info(f"Page analysée: {len(page_source)} caractères")
            
            # Parser les résultats
            search_data = {
                'character_name': character_name,
                'search_url': search_url,
                'timestamp': datetime.now().isoformat(),
                'results': []
            }
            
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 1:
                    headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
                    
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if cells:
                            result = {}
                            for idx, cell in enumerate(cells):
                                header = headers[idx] if idx < len(headers) else f"col_{idx}"
                                result[header] = cell.get_text(strip=True)
                                
                                links = cell.find_all('a')
                                if links:
                                    result[f"{header}_links"] = [a.get('href', '') for a in links]
                            
                            if result:
                                search_data['results'].append(result)
            
            logger.info(f"Extraction terminée: {len(search_data['results'])} résultats")
            self.step_completed.emit(5)
            
            if self._stop_requested:
                return
            
            # Étape 6 : Formatage des résultats
            self.step_started.emit(6)
            logger.info("Formatage des personnages...")
            
            characters = []
            for result in search_data['results']:
                if (result.get('col_1') and 
                    result.get('col_3') and 
                    len(result.get('col_1', '')) > 0 and
                    result.get('col_0') and
                    result.get('col_0', '').isdigit()):
                    
                    rank = result.get('col_0', '')
                    name = result.get('col_1', '').strip()
                    char_class = result.get('col_3', '').strip()
                    race = result.get('col_5', '').strip()
                    guild = result.get('col_7', '').strip()
                    level = result.get('col_8', '').strip()
                    rp = result.get('col_9', '').strip()
                    realm_rank = result.get('col_10', '').strip()
                    realm_level = result.get('col_11', '').strip()
                    
                    # Extraire l'URL
                    url = ""
                    if 'col_1_links' in result and result['col_1_links']:
                        href = result['col_1_links'][0]
                        if href.startswith('?'):
                            url = f"https://eden-daoc.net/herald{href}"
                        elif href.startswith('/'):
                            url = f"https://eden-daoc.net{href}"
                        elif not href.startswith('http'):
                            url = f"https://eden-daoc.net/herald?{href}"
                        else:
                            url = href
                    else:
                        clean_name = name.split()[0]
                        url = f"https://eden-daoc.net/herald?n=player&k={clean_name}"
                    
                    if name and char_class:
                        clean_name = name.split()[0]
                        
                        characters.append({
                            'rank': rank,
                            'name': name,
                            'clean_name': clean_name,
                            'class': char_class,
                            'race': race,
                            'guild': guild,
                            'level': level,
                            'realm_points': rp,
                            'realm_rank': realm_rank,
                            'realm_level': realm_level,
                            'url': url
                        })
            
            if not characters:
                error_msg = f"Aucun personnage trouvé pour '{character_name}'"
                logger.error(error_msg)
                self.step_error.emit(6, error_msg)
                result_error = error_msg
                return
            
            # Trouver le personnage exact
            target_char = None
            for char in characters:
                if char.get('clean_name', '').lower() == character_name.lower():
                    target_char = char
                    break
            
            if not target_char and characters:
                target_char = characters[0]
                logger.warning(f"Pas de correspondance exacte, utilisation du premier résultat: {target_char.get('name', 'Unknown')}")
            
            if not target_char:
                error_msg = "Personnage non trouvé dans les résultats"
                logger.error(error_msg)
                self.step_error.emit(6, error_msg)
                result_error = error_msg
                return
            
            # Normaliser les données
            normalized_data = _normalize_herald_data(target_char)
            
            logger.info(f"Formatage terminé pour: {normalized_data.get('name', 'Unknown')}")
            self.step_completed.emit(6)
            
            # Stocker le succès (signal émis APRÈS Step 7 dans finally)
            logger.info("Mise à jour personnage réussie")
            result_success = True
            result_data = normalized_data
        
        except Exception as e:
            logger.error(f"Erreur mise à jour personnage: {e}", exc_info=True)
            result_error = f"Erreur: {str(e)}"
        
        finally:
            # ✅ Pattern 2 : Cleanup normal (s'exécute si pas terminate())
            # Étape 7 : Fermeture scraper
            if scraper and scraper.driver:
                try:
                    self.step_started.emit(7)
                    logger.info("Fermeture navigateur...")
                    scraper.driver.quit()
                    logger.info("Navigateur fermé")
                    self.step_completed.emit(7)
                except Exception as e:
                    logger.warning(f"Erreur fermeture navigateur: {e}")
                    self.step_error.emit(7, f"Erreur fermeture: {str(e)}")
            
            # Émettre le signal APRÈS Step 7 (fermeture complète)
            logger.info(f"Émission signal update_finished - success={result_success}, error={result_error}")
            self.update_finished.emit(result_success, result_data, result_error)


class HeraldSearchDialog(QDialog):
    """Fenêtre de recherche de personnage sur le Herald Eden"""
    
    # Mapping classe → royaume
    CLASS_TO_REALM = {
        # Albion
        "Armsman": "Albion", "Cabalist": "Albion", "Cleric": "Albion", "Friar": "Albion",
        "Heretic": "Albion", "Infiltrator": "Albion", "Mercenary": "Albion", "Minstrel": "Albion",
        "Necromancer": "Albion", "Paladin": "Albion", "Reaver": "Albion", "Scout": "Albion",
        "Sorcerer": "Albion", "Theurgist": "Albion", "Wizard": "Albion",
        # Midgard
        "Berserker": "Midgard", "Bonedancer": "Midgard", "Healer": "Midgard", "Hunter": "Midgard",
        "Runemaster": "Midgard", "Savage": "Midgard", "Shadowblade": "Midgard", "Shaman": "Midgard",
        "Skald": "Midgard", "Spiritmaster": "Midgard", "Thane": "Midgard", "Valkyrie": "Midgard",
        "Warlock": "Midgard", "Warrior": "Midgard",
        # Hibernia
        "Animist": "Hibernia", "Bainshee": "Hibernia", "Bard": "Hibernia", "Blademaster": "Hibernia",
        "Champion": "Hibernia", "Druid": "Hibernia", "Eldritch": "Hibernia", "Enchanter": "Hibernia",
        "Hero": "Hibernia", "Mentalist": "Hibernia", "Nightshade": "Hibernia", "Ranger": "Hibernia",
        "Valewalker": "Hibernia", "Vampiir": "Hibernia", "Warden": "Hibernia"
    }
    
    # Couleurs des royaumes (depuis UI/delegates.py)
    REALM_COLORS = {
        "Albion": "#CC0000",      # Rouge
        "Midgard": "#0066CC",     # Bleu
        "Hibernia": "#00AA00"     # Vert
    }
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("🔍 Recherche Herald Eden")
        self.resize(700, 600)
        self.search_thread = None
        self.temp_json_path = None  # Stocke le chemin du fichier temp
        self.current_characters = []  # Stocke the Data des personnages trouvés
        self._load_realm_icons_for_combo()
        
        self.init_ui()
    
    def _load_realm_icons_for_combo(self):
        """Charge les icônes des royaumes pour le menu déroulant"""
        from pathlib import Path
        
        self.realm_combo_icons = {}
        realm_logos = {
            "Albion": "Img/albion_logo.png",
            "Midgard": "Img/midgard_logo.png",
            "Hibernia": "Img/hibernia_logo.png"
        }
        
        for realm, logo_path in realm_logos.items():
            full_path = Path(logo_path)
            if full_path.exists():
                pixmap = QPixmap(str(full_path))
                # Redimensionner l'icône à 20x20 pixels for the combo
                scaled_pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.realm_combo_icons[realm] = QIcon(scaled_pixmap)
            else:
                logging.warning(f"Logo introuvable pour {realm}: {logo_path}")
        
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("<h2>🔍 Recherche de Personnage</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Entrez le nom du personnage à rechercher sur le Herald Eden-DAOC.\n"
            "Les résultats seront affichés ci-dessous."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: gray; padding: 10px;")
        layout.addWidget(desc_label)
        
        # Groupe de recherche
        search_group = QGroupBox("Recherche")
        search_layout = QVBoxLayout()
        
        # Ligne 1 : Champ de saisie du nom
        input_layout = QHBoxLayout()
        input_label = QLabel("Nom du personnage :")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Minimum 3 caractères (ex: Alb, Tho, Ely...)")
        self.name_input.returnPressed.connect(self.start_search)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.name_input)
        search_layout.addLayout(input_layout)
        
        # Ligne 2 : Sélection of the royaume
        realm_layout = QHBoxLayout()
        realm_label = QLabel("Royaume :")
        self.realm_combo = QComboBox()
        self.realm_combo.addItem("Tous les royaumes", "")  # Par défaut
        if "Albion" in self.realm_combo_icons:
            self.realm_combo.addItem(self.realm_combo_icons["Albion"], "Albion", "alb")
        else:
            self.realm_combo.addItem("🔴 Albion", "alb")
        if "Midgard" in self.realm_combo_icons:
            self.realm_combo.addItem(self.realm_combo_icons["Midgard"], "Midgard", "mid")
        else:
            self.realm_combo.addItem("🔵 Midgard", "mid")
        if "Hibernia" in self.realm_combo_icons:
            self.realm_combo.addItem(self.realm_combo_icons["Hibernia"], "Hibernia", "hib")
        else:
            self.realm_combo.addItem("🟢 Hibernia", "hib")
        self.realm_combo.setToolTip("Sélectionnez un royaume pour affiner la recherche")
        realm_layout.addWidget(realm_label)
        realm_layout.addWidget(self.realm_combo)
        realm_layout.addStretch()
        search_layout.addLayout(realm_layout)
        
        # Statut
        self.status_label = QLabel("Prêt à rechercher")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        search_layout.addWidget(self.status_label)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Zone of Results
        results_group = QGroupBox("Résultats")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setMinimumHeight(250)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Configurer les colonnes (sans URL)
        columns = ["☑", "Royaume", "Nom", "Classe", "Race", "Guilde", "Niveau", "RP", "Realm Rank"]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Ajuster les colonnes
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(len(columns) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        results_layout.addWidget(self.results_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.search_button = QPushButton("🔍 Rechercher")
        self.search_button.clicked.connect(self.start_search)
        self.search_button.setDefault(True)
        button_layout.addWidget(self.search_button)
        
        button_layout.addStretch()
        
        # Boutons d'import
        self.import_selected_button = QPushButton("📥 Importer sélection")
        self.import_selected_button.clicked.connect(self.import_selected_characters)
        self.import_selected_button.setEnabled(False)
        self.import_selected_button.setToolTip("Importer les personnages cochés")
        button_layout.addWidget(self.import_selected_button)
        
        self.import_all_button = QPushButton("📥 Importer tout")
        self.import_all_button.clicked.connect(self.import_all_characters)
        self.import_all_button.setEnabled(False)
        self.import_all_button.setToolTip("Importer tous les personnages trouvés")
        button_layout.addWidget(self.import_all_button)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def closeEvent(self, event):
        """Appelé à la fermeture de la fenêtre - nettoie les fichiers temporaires et arrête le thread"""
        # Cleanup asynchrone sans bloquer la fermeture
        QTimer.singleShot(0, self._async_full_cleanup)
        
        # Appeler la méthode parent pour fermer réellement la fenêtre
        super().closeEvent(event)
    
    def _async_full_cleanup(self):
        """Cleanup complet de manière asynchrone"""
        try:
            self._stop_search_thread_async()
            self._cleanup_temp_files()
        except Exception as e:
            logging.warning(f"Erreur pendant le cleanup async: {e}")
    
    def accept(self):
        """Appelé quand on ferme avec le bouton Fermer"""
        self._stop_search_thread_async()
        self._cleanup_temp_files()
        super().accept()
    
    def _stop_search_thread(self):
        """Arrête le thread de recherche s'il est en cours d'exécution (VERSION SYNCHRONE - utilisée par progress dialog)"""
        if hasattr(self, 'search_thread') and self.search_thread is not None:
            if self.search_thread.isRunning():
                # Demander l'arrêt gracieux du thread
                self.search_thread.request_stop()
                
                # Déconnecter les signaux pour éviter les erreurs
                try:
                    self.search_thread.search_finished.disconnect()
                    # Déconnecter les NOUVEAUX signaux (step_started, step_completed, step_error)
                    self.search_thread.step_started.disconnect()
                    self.search_thread.step_completed.disconnect()
                    self.search_thread.step_error.disconnect()
                except:
                    pass
                
                # Attendre que le thread se termine (avec timeout de 3 secondes)
                # Le thread devrait s'arrêter rapidement grâce au flag _stop_requested
                self.search_thread.wait(3000)
                
                # Si le thread ne s'est pas terminé, forcer le cleanup du navigateur AVANT terminate()
                if self.search_thread.isRunning():
                    logging.warning("Thread non terminé après 3s - Cleanup forcé du navigateur")
                    self.search_thread.cleanup_driver()  # ✅ Ferme le navigateur depuis thread principal
                    self.search_thread.terminate()
                    self.search_thread.wait()
                
                logging.info("Thread de recherche Herald arrêté proprement")
            
            self.search_thread = None
        
        # Fermer la fenêtre de progression si elle existe
        if hasattr(self, 'progress_dialog'):
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
    
    def _stop_search_thread_async(self):
        """Arrête le thread de recherche de manière asynchrone (VERSION NON-BLOQUANTE pour fermeture fenêtre)"""
        if hasattr(self, 'search_thread') and self.search_thread is not None:
            # Capturer la référence du thread AVANT de passer à l'async
            thread_ref = self.search_thread
            
            if thread_ref.isRunning():
                # Demander l'arrêt gracieux du thread
                thread_ref.request_stop()
                
                # Déconnecter les signaux pour éviter les erreurs
                try:
                    thread_ref.search_finished.disconnect()
                    thread_ref.step_started.disconnect()
                    thread_ref.step_completed.disconnect()
                    thread_ref.step_error.disconnect()
                except:
                    pass
                
                # Cleanup asynchrone avec QTimer pour ne pas bloquer la fermeture
                def _async_thread_cleanup():
                    try:
                        if thread_ref and thread_ref.isRunning():
                            # Attendre 100ms que le thread s'arrête
                            thread_ref.wait(100)
                            
                            if thread_ref.isRunning():
                                logging.warning("Thread encore actif - Cleanup forcé du navigateur")
                                try:
                                    thread_ref.cleanup_driver()
                                    thread_ref.terminate()
                                    thread_ref.wait()
                                except:
                                    pass
                            
                            logging.info("Thread de recherche Herald arrêté (async)")
                    except Exception as e:
                        logging.warning(f"Erreur lors du cleanup async du thread: {e}")
                
                # Exécuter le cleanup après 50ms pour ne pas bloquer la fermeture
                QTimer.singleShot(50, _async_thread_cleanup)
            
            # Nettoyer immédiatement la référence dans self
            self.search_thread = None
        
        # Fermer la fenêtre de progression si elle existe
        if hasattr(self, 'progress_dialog'):
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                try:
                    delattr(self, 'progress_dialog')
                except:
                    pass
    
    def _cleanup_temp_files(self):
        """Supprime les fichiers temporaires de recherche"""
        import tempfile
        from pathlib import Path
        
        try:
            temp_dir = Path(tempfile.gettempdir()) / "EdenSearchResult"
            if temp_dir.exists():
                for file in temp_dir.glob("*.json"):
                    try:
                        file.unlink()
                        logging.info(f"Fichier temporaire supprimé: {file}")
                    except Exception as e:
                        logging.warning(f"Impossible de supprimer {file}: {e}")
        except Exception as e:
            logging.warning(f"Erreur lors du nettoyage des fichiers temporaires: {e}")
    
    def start_search(self):
        """Lance la recherche"""
        character_name = self.name_input.text().strip()
        
        if not character_name:
            QMessageBox.warning(
                self,
                "Nom requis",
                "Veuillez entrer un nom de personnage à rechercher."
            )
            return
        
        # Check the minimum of 3 caractères
        if len(character_name) < 3:
            QMessageBox.warning(
                self,
                "Nom trop court",
                "Veuillez entrer au moins 3 caractères pour la recherche."
            )
            return
        
        # Retrieve the filtre of royaume sélectionné
        realm_filter = self.realm_combo.currentData()
        
        # Désactiver the contrôles
        self.search_button.setEnabled(False)
        self.name_input.setEnabled(False)
        self.realm_combo.setEnabled(False)
        
        # === NOUVEAU SYSTÈME : Utiliser ProgressStepsDialog ===
        from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
        
        # Créer les étapes pour la recherche Herald
        steps = StepConfiguration.build_steps(
            StepConfiguration.HERALD_CONNECTION,
            StepConfiguration.HERALD_SEARCH,
            StepConfiguration.CLEANUP
        )
        
        # Construire le titre et la description
        realm_text = self.realm_combo.currentText()
        if realm_filter:
            title = f"🔍 Recherche de '{character_name}' dans {realm_text}..."
            description = f"Connexion à Eden Herald et recherche de personnages dans le royaume {realm_text}"
        else:
            title = f"🔍 Recherche de '{character_name}' sur Eden Herald..."
            description = "Connexion à Eden Herald et recherche de personnages dans tous les royaumes"
        
        # Créer le dialogue de progression
        self.progress_dialog = ProgressStepsDialog(
            parent=self,
            title=title,
            steps=steps,
            description=description,
            show_progress_bar=True,
            determinate_progress=True,  # Mode avec pourcentage
            allow_cancel=False  # Pas d'annulation pour l'instant
        )
        
        # Lancer le thread avec le filtre de royaume
        self.search_thread = SearchThread(character_name, realm_filter)
        
        # Connecter les NOUVEAUX signaux step_started/step_completed
        self.search_thread.step_started.connect(self._on_step_started)
        self.search_thread.step_completed.connect(self._on_step_completed)
        self.search_thread.step_error.connect(self._on_step_error)
        
        # Connecter le signal de fin
        self.search_thread.search_finished.connect(self.on_search_finished)
        
        # IMPORTANT : Connecter le signal rejected pour gérer la fermeture du dialogue
        self.progress_dialog.rejected.connect(self._on_progress_dialog_closed)
        
        # Afficher le dialogue et démarrer le worker
        self.progress_dialog.show()
        self.search_thread.start()
    
    def _on_step_started(self, step_index):
        """Wrapper thread-safe pour start_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.start_step(step_index)
            except RuntimeError:
                # Le dialogue a été détruit
                pass
    
    def _on_step_completed(self, step_index):
        """Wrapper thread-safe pour complete_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.complete_step(step_index)
            except RuntimeError:
                # Le dialogue a été détruit
                pass
    
    def _on_step_error(self, step_index, error_message):
        """Wrapper thread-safe pour error_step"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.error_step(step_index, error_message)
            except RuntimeError:
                # Le dialogue a été détruit
                pass
    
    def _on_progress_dialog_closed(self):
        """Appelé quand l'utilisateur ferme le dialogue de progression"""
        logging.info("Dialogue de progression fermé par l'utilisateur - Arrêt de la recherche")
        
        # Arrêter le thread de recherche proprement
        self._stop_search_thread()
        
        # Réactiver les contrôles
        self.search_button.setEnabled(True)
        self.name_input.setEnabled(True)
        self.realm_combo.setEnabled(True)
    
    # === ANCIENNE MÉTHODE (LEGACY - Conservée pour référence) ===
    # def _on_search_progress_update(self, status_message):
    #     """Met à jour le message de progression pendant la recherche"""
    #     # REMPLACÉE par le système ProgressStepsDialog
    #     # Les signaux step_started/step_completed sont maintenant utilisés
    #     pass
    
    def _get_scaled_size(self, base_size):
        """Helper pour obtenir la taille scalée"""
        try:
            from Functions.theme_manager import get_scaled_size
            return get_scaled_size(base_size)
        except:
            return base_size
    
    def on_search_finished(self, success, message, json_path):
        """Appelé quand la recherche est terminée"""
        # === NOUVEAU : Utiliser complete_all() ou afficher erreur ===
        if hasattr(self, 'progress_dialog'):
            if success:
                # Succès : compléter toutes les étapes
                self.progress_dialog.complete_all(f"✅ {message}")
            else:
                # Erreur : afficher le message d'erreur
                self.progress_dialog.set_status_message(f"❌ {message}", "#F44336")
            
            # Le dialogue se fermera automatiquement après complete_all()
            # Mais on le ferme manuellement si erreur
            if not success:
                import time
                QTimer.singleShot(2000, self.progress_dialog.close)
        
        # Réactiver the contrôles
        self.search_button.setEnabled(True)
        self.name_input.setEnabled(True)
        self.realm_combo.setEnabled(True)
        
        if success:
            # Load and afficher the Results
            try:
                import json
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                all_characters = data.get('characters', [])
                search_query = data.get('search_query', '').lower()
                
                # Filtrer for ne garder that the personnages dont the nom commence par the caractères recherchés
                characters = []
                for char in all_characters:
                    char_name = char.get('clean_name', char.get('name', '')).lower()
                    if char_name.startswith(search_query):
                        characters.append(char)
                
                # Vider le tableau
                self.results_table.setRowCount(0)
                
                if characters:
                    # Remplir le tableau
                    self.results_table.setRowCount(len(characters))
                    
                    for row, char in enumerate(characters):
                        # Déterminer the royaume à partir of the classe
                        class_name = char.get('class', '')
                        realm = self.CLASS_TO_REALM.get(class_name, "Unknown")
                        realm_color = self.REALM_COLORS.get(realm, "#000000")
                        
                        # Create une couleur of fond for the royaume (version plus claire for the lisibilité)
                        bg_color = QColor(realm_color)
                        bg_color.setAlpha(50)  # Transparence for the lisibilité
                        bg_brush = QBrush(bg_color)
                        
                        # Case à cocher (colonne 0)
                        checkbox_item = QTableWidgetItem()
                        checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                        checkbox_item.setCheckState(Qt.Unchecked)
                        checkbox_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 0, checkbox_item)
                        
                        # Royaume (colonne 1)
                        realm_item = QTableWidgetItem(realm)
                        realm_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 1, realm_item)
                        
                        # Nom (colonne 2)
                        name_item = QTableWidgetItem(char.get('name', ''))
                        name_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 2, name_item)
                        
                        # Classe (colonne 3)
                        class_item = QTableWidgetItem(class_name)
                        class_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 3, class_item)
                        
                        # Race (colonne 4)
                        race_item = QTableWidgetItem(char.get('race', ''))
                        race_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 4, race_item)
                        
                        # Guilde (colonne 5)
                        guild_item = QTableWidgetItem(char.get('guild', ''))
                        guild_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 5, guild_item)
                        
                        # Niveau (colonne 6)
                        level_item = QTableWidgetItem(char.get('level', ''))
                        level_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 6, level_item)
                        
                        # RP (colonne 7)
                        rp_item = QTableWidgetItem(char.get('realm_points', ''))
                        rp_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 7, rp_item)
                        
                        # Realm Rank (colonne 8)
                        realm_rank = f"{char.get('realm_rank', '')} ({char.get('realm_level', '')})"
                        rr_item = QTableWidgetItem(realm_rank)
                        rr_item.setBackground(bg_brush)
                        self.results_table.setItem(row, 8, rr_item)
                    
                    # Stocker the Data des personnages
                    self.current_characters = characters
                    
                    # Mettre à jour the message of statut with the nombre filtré
                    count = len(characters)
                    self.status_label.setText(f"✅ {count} personnage(s) trouvé(s) commençant par '{search_query}'")
                    self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: green; font-weight: bold;")
                    
                    # Activer les boutons d'import
                    self.import_all_button.setEnabled(True)
                    self.import_selected_button.setEnabled(True)
                else:
                    # Aucun personnage trouvé
                    self.current_characters = []
                    self.import_all_button.setEnabled(False)
                    self.import_selected_button.setEnabled(False)
                    # Afficher un message dans le statut
                    self.status_label.setText(f"⚠️ Aucun personnage trouvé pour '{data['search_query']}'")
                    self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: orange;")
                    
            except Exception as e:
                self.current_characters = []
                self.import_all_button.setEnabled(False)
                self.import_selected_button.setEnabled(False)
                self.status_label.setText(f"❌ Erreur de lecture: {str(e)}")
                self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: red;")
        else:
            self.current_characters = []
            self.import_all_button.setEnabled(False)
            self.import_selected_button.setEnabled(False)
            self.status_label.setText(f"❌ Erreur : {message}")
            self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: red;")
            # Vider le tableau en cas d'erreur
            self.results_table.setRowCount(0)
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel sur la table de résultats"""
        if not self.current_characters:
            return
        
        # Retrieve the ligne sélectionnée
        row = self.results_table.rowAt(position.y())
        if row < 0:
            return
        
        # Create the menu contextuel
        context_menu = QMenu(self)
        
        # Action d'import
        import_action = context_menu.addAction("📥 Importer ce personnage")
        import_action.triggered.connect(lambda: self._import_single_character(row))
        
        # Afficher the menu à the position of the curseur
        context_menu.exec_(self.results_table.viewport().mapToGlobal(position))
    
    def _import_single_character(self, row):
        """Importe un personnage spécifique depuis la table"""
        if row < 0 or row >= len(self.current_characters):
            return
        
        char_data = self.current_characters[row]
        
        # Confirmer l'import
        char_name = char_data.get('clean_name', char_data.get('name', ''))
        reply = QMessageBox.question(
            self,
            "Confirmer l'import",
            f"Voulez-vous importer le personnage '{char_name}' ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._import_characters([char_data])
    
    def import_selected_characters(self):
        """Importe les personnages cochés"""
        if not self.current_characters:
            return
        
        # Retrieve the personnages cochés
        selected_chars = []
        for row in range(self.results_table.rowCount()):
            checkbox_item = self.results_table.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                if row < len(self.current_characters):
                    selected_chars.append(self.current_characters[row])
        
        if not selected_chars:
            QMessageBox.warning(
                self,
                "Aucune sélection",
                "Veuillez cocher au moins un personnage à importer."
            )
            return
        
        # Confirmer l'import
        count = len(selected_chars)
        reply = QMessageBox.question(
            self,
            "Confirmer l'import",
            f"Voulez-vous importer {count} personnage(s) sélectionné(s) ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._import_characters(selected_chars)
    
    def import_all_characters(self):
        """Importe tous les personnages trouvés"""
        if not self.current_characters:
            return
        
        # Confirmer l'import
        count = len(self.current_characters)
        reply = QMessageBox.question(
            self,
            "Confirmer l'import",
            f"Voulez-vous importer tous les {count} personnage(s) trouvé(s) ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._import_characters(self.current_characters)
    
    def _import_characters(self, characters):
        """Importe une liste de personnages dans la base de données"""
        from Functions.character_manager import save_character, get_all_characters
        import json
        import os
        from Functions.character_manager import get_character_dir
        
        success_count = 0
        error_count = 0
        errors = []
        updated_count = 0
        
        for char_data in characters:
            try:
                # Préparer the Data of the personnage for l'import
                name = char_data.get('clean_name', char_data.get('name', ''))
                char_class = char_data.get('class', '')
                realm = self.CLASS_TO_REALM.get(char_class, "Unknown")
                
                # Retrieve the saison par défaut depuis the Configuration
                default_season = config.get('default_season', 'S3')
                
                # Create the dictionnaire of Data of the personnage
                character_data = {
                    'name': name,
                    'class': char_class,
                    'race': char_data.get('race', ''),
                    'realm': realm,
                    'guild': char_data.get('guild', ''),
                    'level': char_data.get('level', '50'),
                    'realm_rank': char_data.get('realm_rank', ''),
                    'realm_level': char_data.get('realm_level', ''),
                    'realm_points': char_data.get('realm_points', '0'),
                    'url': char_data.get('url', ''),
                    # Valeurs par défaut for the champs manquants
                    'server': 'Eden',
                    'season': default_season,
                    'mlevel': '0',
                    'clevel': '0',
                    'notes': f"Mis à jour depuis le Herald le {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
                
                # Check if the personnage existe déjà
                existing_chars = get_all_characters()
                existing_char = None
                for c in existing_chars:
                    if c.get('name', '').lower() == name.lower():
                        existing_char = c
                        break
                
                if existing_char:
                    # the personnage existe, on va the mettre à jour
                    # Construire le chemin du fichier existant
                    base_char_dir = get_character_dir()
                    char_season = existing_char.get('season', 'S1')
                    char_realm = existing_char.get('realm', realm)
                    file_path = os.path.join(base_char_dir, char_season, char_realm, f"{name}.json")
                    
                    if os.path.exists(file_path):
                        # Load the Data existantes for conserver the infos importantes
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                            
                            # Mettre à jour with the nouvelles Data (seulement the infos pertinentes)
                            existing_data.update({
                                'class': character_data['class'],
                                'race': character_data['race'],
                                'guild': character_data['guild'],
                                'level': character_data['level'],
                                'realm_rank': character_data['realm_rank'],
                                'realm_level': character_data['realm_level'],
                                'realm_points': character_data['realm_points'],
                                'url': character_data['url'],
                                'notes': character_data['notes']
                            })
                            
                            # Sauvegarder avec allow_overwrite=True
                            success, msg = save_character(existing_data, allow_overwrite=True)
                            if success:
                                updated_count += 1
                            else:
                                error_count += 1
                                errors.append(f"{name}: erreur lors de la mise à jour - {msg}")
                        except json.JSONDecodeError:
                            error_count += 1
                            errors.append(f"{name}: impossible de lire le fichier existant")
                    else:
                        error_count += 1
                        errors.append(f"{name}: fichier existant introuvable")
                else:
                    # Le personnage n'existe pas, on l'ajoute
                    success, msg = save_character(character_data)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"{name}: {msg}")
                
            except Exception as e:
                error_count += 1
                errors.append(f"{char_data.get('name', 'Unknown')}: {str(e)}")
                logging.error(f"Erreur lors de l'import de {char_data.get('name')}: {e}", exc_info=True)
        
        # Afficher the résultat
        if success_count > 0 or updated_count > 0:
            message = ""
            if success_count > 0:
                message += lang.get("herald_import_success", count=success_count)
            if updated_count > 0:
                if message:
                    message += "\n"
                message += lang.get("herald_import_updated", count=updated_count)
            
            if error_count > 0:
                message += f"\n{lang.get('herald_import_errors', count=error_count)}\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n{lang.get('herald_import_more_errors', count=len(errors) - 5)}"
            
            QMessageBox.information(self, lang.get("herald_import_complete_title"), message)
            
            # Rafraîchir l'interface principale de manière asynchrone pour éviter le freeze
            if hasattr(self.parent(), 'tree_manager') and hasattr(self.parent().tree_manager, 'refresh_character_list'):
                QTimer.singleShot(100, self.parent().tree_manager.refresh_character_list)
            
            # Trigger backup after mass import/update de manière asynchrone
            parent_app = self.parent()
            if hasattr(parent_app, 'backup_manager'):
                def _async_backup():
                    try:
                        import sys
                        import logging
                        print(f"[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - {success_count} created, {updated_count} updated - Backup with reason=Update")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - {success_count} created, {updated_count} updated - Backup with reason=Update\n")
                        sys.stderr.flush()
                        logging.info(f"[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - {success_count} created, {updated_count} updated - Backup with reason=Update")
                        parent_app.backup_manager.backup_characters_force(reason="Update", character_name="multi")
                    except Exception as e:
                        print(f"[BACKUP_TRIGGER] Warning: Backup after mass import failed: {e}")
                        sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after mass import failed: {e}\n")
                        sys.stderr.flush()
                        logging.warning(f"[BACKUP_TRIGGER] Backup after mass import failed: {e}")
                
                QTimer.singleShot(200, _async_backup)
        else:
            error_msg = lang.get("herald_import_no_success") + "\n\n"
            error_msg += "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n{lang.get('herald_import_more_errors', count=len(errors) - 10)}"
            QMessageBox.warning(self, lang.get("herald_import_complete_title"), error_msg)


class CharacterUpdateDialog(QDialog):
    """Dialogue pour valider les mises à jour d'un personnage depuis Herald."""
    
    def __init__(self, parent, current_data, new_data, character_name):
        super().__init__(parent)
        self.current_data = current_data
        self.new_data = new_data
        self.character_name = character_name
        self.changes = {}
        
        self.setWindowTitle(f"Mise à jour - {character_name}")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # En-tête
        header_label = QLabel(f"<h2>Mise à jour du personnage: {character_name}</h2>")
        layout.addWidget(header_label)
        
        info_label = QLabel(
            "<b>Comparaison des données :</b><br>"
            "• <span style='color: green;'>✓</span> = Valeurs identiques (pas de changement)<br>"
            "• <span style='color: red;'>Valeur actuelle</span> → <span style='color: green;'><b>Nouvelle valeur</b></span> = Changement détecté<br>"
            "Cochez les modifications que vous souhaitez appliquer."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Tableau des modifications
        self.changes_table = QTableWidget()
        self.changes_table.setColumnCount(4)
        self.changes_table.setHorizontalHeaderLabels(["Appliquer", "Champ", "Valeur actuelle", "Nouvelle valeur"])
        self.changes_table.horizontalHeader().setStretchLastSection(True)
        self.changes_table.setSelectionMode(QTableWidget.NoSelection)
        
        # Détecter the changements
        self._detect_changes()
        
        layout.addWidget(self.changes_table)
        
        # Boutons of sélection
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Tout sélectionner")
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Tout désélectionner")
        deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Boutons OK/Annuler
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Changer le texte du bouton OK
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Appliquer les modifications")
        
        layout.addWidget(button_box)
    
    def _detect_changes(self):
        """Détecte les changements entre les données actuelles et nouvelles."""
        # Champs à comparer (all the champs importants)
        fields_to_check = {
            'level': 'Niveau',
            'class': 'Classe',
            'race': 'Race',
            'realm': 'Royaume',
            'guild': 'Guilde',
            'realm_points': 'Points de Royaume',
            'realm_rank': 'Rang de Royaume',
            'server': 'Serveur'
        }
        
        all_rows = []
        
        for field, label in fields_to_check.items():
            current_value = self.current_data.get(field, '')
            new_value = self.new_data.get(field, '')
            
            # Normaliser les valeurs pour la comparaison
            # Cas spécial for realm_points qui can contenir des espaces
            if field == 'realm_points':
                # Nettoyer les espaces dans les realm_points
                if isinstance(new_value, str):
                    new_value = new_value.replace(' ', '').replace(',', '')
                    try:
                        new_value = int(new_value)
                    except:
                        pass
                if isinstance(current_value, str):
                    current_value = current_value.replace(' ', '').replace(',', '')
                    try:
                        current_value = int(current_value)
                    except:
                        pass
            
            # Cas spécial pour realm_rank : s'assurer qu'on compare les codes (XLY) et pas les titres
            # Le fichier JSON peut contenir soit le code (correct), soit le titre (ancien format)
            # Le Herald retourne toujours le code via _normalize_character_data()
            if field == 'realm_rank':
                # Vérifier si current_value est un titre (contient des espaces/lettres non-format XLY)
                if isinstance(current_value, str) and current_value:
                    # Format XLY: chiffre(s) + L + chiffre(s) (ex: "5L9", "10L3")
                    import re
                    if not re.match(r'^\d+L\d+$', current_value.strip()):
                        # current_value est probablement un titre (ex: "Raven Ardent")
                        # Recalculer le rang depuis realm_points si disponible
                        realm_points = self.current_data.get('realm_points', 0)
                        realm = self.current_data.get('realm', 'Albion')
                        if realm_points and hasattr(self.parent(), 'data_manager'):
                            try:
                                # Convertir realm_points en int si nécessaire
                                if isinstance(realm_points, str):
                                    realm_points = int(realm_points.replace(' ', '').replace(',', ''))
                                
                                rank_info = self.parent().data_manager.get_realm_rank_info(realm, realm_points)
                                if rank_info:
                                    current_value = rank_info['level']  # Code XLY correct
                            except Exception as e:
                                import logging
                                logging.warning(f"Impossible de recalculer realm_rank depuis realm_points: {e}")
            
            if isinstance(current_value, (int, float)):
                current_value_str = str(current_value)
            else:
                current_value_str = str(current_value) if current_value else ''
            
            if isinstance(new_value, (int, float)):
                new_value_str = str(new_value)
            else:
                new_value_str = str(new_value) if new_value else ''
            
            # Déterminer if c'est un changement
            has_change = (current_value_str != new_value_str and new_value_str)
            
            all_rows.append({
                'field': field,
                'label': label,
                'current': current_value_str or '(vide)',
                'new': new_value_str or '(vide)',
                'new_value_raw': new_value,
                'has_change': has_change
            })
        
        # Remplir le tableau avec TOUTES les lignes
        self.changes_table.setRowCount(len(all_rows))
        
        for row, data in enumerate(all_rows):
            # Case à cocher (seulement if changement)
            if data['has_change']:
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.changes_table.setCellWidget(row, 0, checkbox_widget)
                
                # Stocker the référence of the checkbox and the valeur brute
                self.changes_table.setItem(row, 0, QTableWidgetItem())
                self.changes_table.item(row, 0).setData(Qt.UserRole, checkbox)
                self.changes_table.item(row, 0).setData(Qt.UserRole + 1, data['field'])
                self.changes_table.item(row, 0).setData(Qt.UserRole + 2, data['new_value_raw'])
            else:
                # Pas de checkbox pour les valeurs identiques
                item = QTableWidgetItem("✓")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QBrush(QColor(0, 150, 0)))  # Vert
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.changes_table.setItem(row, 0, item)
            
            # Label du champ
            field_item = QTableWidgetItem(data['label'])
            if not data['has_change']:
                field_item.setForeground(QBrush(QColor(100, 100, 100)))  # Gris
            self.changes_table.setItem(row, 1, field_item)
            
            # Valeur actuelle
            current_item = QTableWidgetItem(data['current'])
            if data['has_change']:
                current_item.setForeground(QBrush(QColor(200, 0, 0)))  # Rouge
            else:
                current_item.setForeground(QBrush(QColor(100, 100, 100)))  # Gris
            self.changes_table.setItem(row, 2, current_item)
            
            # Nouvelle valeur
            new_value_item = QTableWidgetItem(data['new'])
            if data['has_change']:
                # En gras et vert pour les changements
                font = new_value_item.font()
                font.setBold(True)
                new_value_item.setFont(font)
                new_value_item.setForeground(QBrush(QColor(0, 150, 0)))  # Vert
            else:
                # Gris pour les valeurs identiques
                new_value_item.setForeground(QBrush(QColor(100, 100, 100)))
            self.changes_table.setItem(row, 3, new_value_item)
        
        # Ajuster les colonnes
        self.changes_table.resizeColumnsToContents()
        self.changes_table.setColumnWidth(0, 80)
    
    def _select_all(self):
        """Sélectionne toutes les modifications."""
        for row in range(self.changes_table.rowCount()):
            item = self.changes_table.item(row, 0)
            if item:
                checkbox = item.data(Qt.UserRole)
                if checkbox:
                    checkbox.setChecked(True)
    
    def _deselect_all(self):
        """Désélectionne toutes les modifications."""
        for row in range(self.changes_table.rowCount()):
            item = self.changes_table.item(row, 0)
            if item:
                checkbox = item.data(Qt.UserRole)
                if checkbox:
                    checkbox.setChecked(False)
    
    def get_selected_changes(self):
        """Retourne les modifications sélectionnées."""
        selected = {}
        
        
        for row in range(self.changes_table.rowCount()):
            item = self.changes_table.item(row, 0)
            if item:
                checkbox = item.data(Qt.UserRole)
                field = item.data(Qt.UserRole + 1)
                value_raw = item.data(Qt.UserRole + 2)  # Retrieve the valeur brute
                
                if checkbox and checkbox.isChecked():
                    selected[field] = value_raw  # Utiliser la valeur brute
        
        return selected
    
    def has_changes(self):
        """Retourne True s'il y a au moins un changement détecté."""
        for row in range(self.changes_table.rowCount()):
            item = self.changes_table.item(row, 0)
            if item:
                checkbox = item.data(Qt.UserRole)
                if checkbox:  # S'il y a une checkbox, c'est qu'il y a un changement
                    return True
        return False


class BackupSettingsDialog(QDialog):
    """Dialog for configuring character backup settings."""
    
    def __init__(self, parent, backup_manager):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.config_manager = backup_manager.config_manager
        self.setWindowTitle(lang.get("backup_settings_title"))
        self.resize(1400, 800)
        
        main_layout = QVBoxLayout(self)
        
        # Get backup info once for use in multiple sections
        backup_info = self.backup_manager.get_backup_info()
        
        # ============ SECTION 1: CHARACTERS ============
        chars_group = QGroupBox("📁 Characters")
        chars_layout = QVBoxLayout()
        
        # Enabled/Disabled checkbox
        enabled_layout = QHBoxLayout()
        self.enabled_checkbox = QCheckBox(lang.get("backup_enabled_label"))
        self.enabled_checkbox.setChecked(self.config_manager.get("backup_enabled", True))
        enabled_layout.addWidget(self.enabled_checkbox)
        enabled_layout.addStretch()
        chars_layout.addLayout(enabled_layout)
        chars_layout.addSpacing(5)
        
        # Path Configuration
        path_layout = QFormLayout()
        path_row_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        backup_path = self.config_manager.get("backup_path")
        if not backup_path:
            from Functions.path_manager import get_base_path
            backup_path = os.path.join(get_base_path(), "Backup", "Characters")
        self.path_edit.setText(backup_path)
        self.path_edit.setReadOnly(True)
        self.path_edit.setCursorPosition(0)
        path_row_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton(lang.get("browse_button"))
        browse_button.setMaximumWidth(100)
        browse_button.clicked.connect(self.browse_backup_path)
        path_row_layout.addWidget(browse_button)
        path_layout.addRow(lang.get("backup_path_label") + " :", path_row_layout)
        
        chars_layout.addLayout(path_layout)
        chars_layout.addSpacing(10)
        
        # Compression Setting
        compression_layout = QHBoxLayout()
        self.compress_checkbox = QCheckBox(lang.get("backup_compress_label"))
        self.compress_checkbox.setChecked(self.config_manager.get("backup_compress", True))
        self.compress_checkbox.setToolTip(lang.get("backup_compress_tooltip"))
        compression_layout.addWidget(self.compress_checkbox)
        compression_layout.addStretch()
        chars_layout.addLayout(compression_layout)
        chars_layout.addSpacing(10)
        
        # Retention Settings (size limit only)
        retention_layout = QFormLayout()
        
        # Size limit
        size_limit_layout = QHBoxLayout()
        self.size_limit_spin = QLineEdit()
        self.size_limit_spin.setText(str(self.config_manager.get("backup_size_limit_mb", 20)))
        self.size_limit_spin.setMaximumWidth(80)
        size_limit_layout.addWidget(self.size_limit_spin)
        size_limit_layout.addWidget(QLabel("MB"))
        size_limit_layout.addWidget(QLabel(lang.get("backup_size_limit_tooltip")))
        size_limit_layout.addStretch()
        retention_layout.addRow(lang.get("backup_size_limit_label"), size_limit_layout)
        
        chars_layout.addLayout(retention_layout)
        chars_layout.addSpacing(10)
        
        # Last backup date and count info in Characters section
        info_layout = QFormLayout()
        
        # Total backups count (FIRST)
        total_backups = len(backup_info["backups"])
        self.total_label = QLabel(f"{total_backups}")
        self.total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        info_layout.addRow("Nombre de sauvegardes :", self.total_label)
        
        # Last backup date (SECOND)
        last_backup_date = self.config_manager.get("backup_last_date")
        if last_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_backup_date)
                last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_backup_str = "N/A"
        else:
            last_backup_str = "Aucune sauvegarde"
        self.last_backup_label = QLabel(last_backup_str)
        self.last_backup_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        info_layout.addRow("Dernière sauvegarde :", self.last_backup_label)
        
        chars_layout.addLayout(info_layout)
        chars_layout.addSpacing(15)
        
        # Backup Now Button in Characters section (auto-size to fit text)
        backup_button_layout = QHBoxLayout()
        backup_now_button = QPushButton(lang.get("backup_now_button"))
        backup_now_button.setStyleSheet("QPushButton { padding: 6px 12px; font-weight: bold; background-color: #0078D4; color: white; border-radius: 4px; }")
        backup_now_button.clicked.connect(self.backup_now)
        from PySide6.QtWidgets import QSizePolicy
        backup_now_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        backup_button_layout.addWidget(backup_now_button)
        
        # Open backup folder button for Characters
        open_folder_button = QPushButton("📂 Ouvrir le dossier")
        open_folder_button.setStyleSheet("QPushButton { padding: 6px 12px; font-weight: bold; background-color: #107C10; color: white; border-radius: 4px; }")
        open_folder_button.clicked.connect(self.open_characters_backup_folder)
        open_folder_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        backup_button_layout.addWidget(open_folder_button)
        
        backup_button_layout.addStretch()
        chars_layout.addLayout(backup_button_layout)
        
        chars_group.setLayout(chars_layout)
        
        # ============ SECTION 1.5: COOKIES EDEN ============
        cookies_info = self.backup_manager.get_cookies_backup_info()
        
        cookies_group = QGroupBox("🍪 Cookies Eden")
        cookies_layout = QVBoxLayout()
        
        # Enabled/Disabled checkbox
        cookies_enabled_layout = QHBoxLayout()
        self.cookies_enabled_checkbox = QCheckBox(lang.get("backup_enabled_label"))
        self.cookies_enabled_checkbox.setChecked(self.config_manager.get("cookies_backup_enabled", True))
        cookies_enabled_layout.addWidget(self.cookies_enabled_checkbox)
        cookies_enabled_layout.addStretch()
        cookies_layout.addLayout(cookies_enabled_layout)
        cookies_layout.addSpacing(5)
        
        # Path Configuration
        cookies_path_layout = QFormLayout()
        cookies_path_row_layout = QHBoxLayout()
        self.cookies_path_edit = QLineEdit()
        cookies_backup_path = self.config_manager.get("cookies_backup_path")
        if not cookies_backup_path:
            from Functions.path_manager import get_base_path
            cookies_backup_path = os.path.join(get_base_path(), "Backup", "Cookies")
        self.cookies_path_edit.setText(cookies_backup_path)
        self.cookies_path_edit.setReadOnly(True)
        self.cookies_path_edit.setCursorPosition(0)
        cookies_path_row_layout.addWidget(self.cookies_path_edit)
        
        browse_cookies_button = QPushButton(lang.get("browse_button"))
        browse_cookies_button.setMaximumWidth(100)
        browse_cookies_button.clicked.connect(self.browse_cookies_backup_path)
        cookies_path_row_layout.addWidget(browse_cookies_button)
        cookies_path_layout.addRow(lang.get("backup_path_label") + " :", cookies_path_row_layout)
        
        cookies_layout.addLayout(cookies_path_layout)
        cookies_layout.addSpacing(10)
        
        # Compression Setting
        cookies_compression_layout = QHBoxLayout()
        self.cookies_compress_checkbox = QCheckBox(lang.get("backup_compress_label"))
        self.cookies_compress_checkbox.setChecked(self.config_manager.get("cookies_backup_compress", True))
        self.cookies_compress_checkbox.setToolTip(lang.get("backup_compress_tooltip"))
        cookies_compression_layout.addWidget(self.cookies_compress_checkbox)
        cookies_compression_layout.addStretch()
        cookies_layout.addLayout(cookies_compression_layout)
        cookies_layout.addSpacing(10)
        
        # Retention Settings (size limit only)
        cookies_retention_layout = QFormLayout()
        
        # Size limit
        cookies_size_limit_layout = QHBoxLayout()
        self.cookies_size_limit_spin = QLineEdit()
        self.cookies_size_limit_spin.setText(str(self.config_manager.get("cookies_backup_size_limit_mb", 10)))
        self.cookies_size_limit_spin.setMaximumWidth(80)
        cookies_size_limit_layout.addWidget(self.cookies_size_limit_spin)
        cookies_size_limit_layout.addWidget(QLabel("MB"))
        cookies_size_limit_layout.addWidget(QLabel(lang.get("backup_size_limit_tooltip")))
        cookies_size_limit_layout.addStretch()
        cookies_retention_layout.addRow(lang.get("backup_size_limit_label"), cookies_size_limit_layout)
        
        cookies_layout.addLayout(cookies_retention_layout)
        cookies_layout.addSpacing(10)
        
        # Last cookies backup date and count info
        cookies_info_layout = QFormLayout()
        
        # Total backups count (FIRST)
        cookies_total_backups = len(cookies_info["backups"])
        self.cookies_total_label = QLabel(f"{cookies_total_backups}")
        self.cookies_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        cookies_info_layout.addRow("Nombre de sauvegardes :", self.cookies_total_label)
        
        # Last backup date (SECOND)
        cookies_last_backup_date = self.config_manager.get("cookies_backup_last_date")
        if cookies_last_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(cookies_last_backup_date)
                cookies_last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                cookies_last_backup_str = "N/A"
        else:
            cookies_last_backup_str = "Aucune sauvegarde"
        self.cookies_last_backup_label = QLabel(cookies_last_backup_str)
        self.cookies_last_backup_label.setStyleSheet("font-weight: bold; color: #0078D4;")
        cookies_info_layout.addRow("Dernière sauvegarde :", self.cookies_last_backup_label)
        
        cookies_layout.addLayout(cookies_info_layout)
        cookies_layout.addSpacing(10)
        
        # Usage info for cookies
        cookies_current_mb = cookies_info["current_usage_mb"]
        cookies_size_limit = cookies_info["size_limit_mb"]
        
        cookies_usage_form = QFormLayout()
        self.cookies_usage_label = QLabel()
        self.update_cookies_usage_display(cookies_current_mb, cookies_size_limit)
        cookies_usage_form.addRow(lang.get("backup_usage_label") + " :", self.cookies_usage_label)
        
        cookies_layout.addLayout(cookies_usage_form)
        cookies_layout.addSpacing(15)
        
        # Backup Now Button in Cookies section
        cookies_backup_button_layout = QHBoxLayout()
        cookies_backup_now_button = QPushButton(lang.get("backup_now_button"))
        cookies_backup_now_button.setStyleSheet("QPushButton { padding: 6px 12px; font-weight: bold; background-color: #0078D4; color: white; border-radius: 4px; }")
        cookies_backup_now_button.clicked.connect(self.backup_cookies_now)
        cookies_backup_now_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cookies_backup_button_layout.addWidget(cookies_backup_now_button)
        
        # Open backup folder button for Cookies
        open_cookies_folder_button = QPushButton("📂 Ouvrir le dossier")
        open_cookies_folder_button.setStyleSheet("QPushButton { padding: 6px 12px; font-weight: bold; background-color: #107C10; color: white; border-radius: 4px; }")
        open_cookies_folder_button.clicked.connect(self.open_cookies_backup_folder)
        open_cookies_folder_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cookies_backup_button_layout.addWidget(open_cookies_folder_button)
        
        cookies_backup_button_layout.addStretch()
        cookies_layout.addLayout(cookies_backup_button_layout)
        
        cookies_group.setLayout(cookies_layout)
        
        # ============ SECTION 1 & 1.5: Add both sections side by side ============
        sections_layout = QHBoxLayout()
        sections_layout.addWidget(chars_group)
        sections_layout.addWidget(cookies_group)
        main_layout.addLayout(sections_layout)
        
        # ============ SECTION 2: STATISTIQUES ============
        stats_group = QGroupBox("Statistiques de Stockage")
        stats_layout = QVBoxLayout()
        
        # Current Usage
        current_mb = backup_info["current_usage_mb"]
        size_limit = backup_info["size_limit_mb"]
        
        stats_form = QFormLayout()
        self.usage_label = QLabel()
        self.update_usage_display(current_mb, size_limit)
        stats_form.addRow(lang.get("backup_usage_label") + " (Characters) :", self.usage_label)
        
        stats_layout.addLayout(stats_form)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # ============ SECTION 3: DERNIÈRES SAUVEGARDES ============
        recent_group = QGroupBox("⏱️ Dernières Sauvegardes")
        recent_layout = QVBoxLayout()
        
        self.backups_list = QTextEdit()
        self.backups_list.setReadOnly(True)
        self.backups_list.setMinimumHeight(150)
        self.update_backups_list(backup_info["backups"])
        recent_layout.addWidget(self.backups_list)
        
        recent_group.setLayout(recent_layout)
        main_layout.addWidget(recent_group)
        
        # ============ Dialog Buttons ============
        main_layout.addSpacing(10)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def browse_backup_path(self):
        """Open directory selection dialog for backup path."""
        current_path = self.path_edit.text()
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            lang.get("backup_path_dialog_title"),
            current_path
        )
        if selected_dir:
            self.path_edit.setText(selected_dir)
            self.path_edit.setCursorPosition(0)
    
    def browse_cookies_backup_path(self):
        """Open directory selection dialog for cookies backup path."""
        current_path = self.cookies_path_edit.text()
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            lang.get("backup_path_dialog_title"),
            current_path
        )
        if selected_dir:
            self.cookies_path_edit.setText(selected_dir)
            self.cookies_path_edit.setCursorPosition(0)
    
    def open_characters_backup_folder(self):
        """Open the Characters backup folder in file explorer."""
        import subprocess
        import platform
        
        backup_path = self.path_edit.text()
        if not backup_path or not os.path.exists(backup_path):
            QMessageBox.warning(self, "Attention", "Le dossier de sauvegarde n'existe pas ou n'est pas valide.")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(backup_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", backup_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", backup_path])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dossier : {str(e)}")
    
    def open_cookies_backup_folder(self):
        """Open the Cookies backup folder in file explorer."""
        import subprocess
        import platform
        
        backup_path = self.cookies_path_edit.text()
        if not backup_path or not os.path.exists(backup_path):
            QMessageBox.warning(self, "Attention", "Le dossier de sauvegarde n'existe pas ou n'est pas valide.")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(backup_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", backup_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", backup_path])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dossier : {str(e)}")
    
    def update_usage_display(self, current_mb, size_limit_mb):
        """Update the usage display label with better formatting."""
        if size_limit_mb > 0:
            percentage = (current_mb / size_limit_mb) * 100 if size_limit_mb > 0 else 0
            
            # Color based on usage
            if percentage > 90:
                color = "#FF4444"  # Red
                status = "⚠️ Presque plein"
            elif percentage > 70:
                color = "#FFAA00"  # Orange
                status = "⚡ Modéré"
            else:
                color = "#00AA00"  # Green
                status = "✓ Normal"
            
            usage_text = f"<span style='color: {color}; font-weight: bold;'>{current_mb} MB / {size_limit_mb} MB ({percentage:.1f}%) - {status}</span>"
            self.usage_label.setText(usage_text)
        else:
            self.usage_label.setText(f"<b>{current_mb} MB</b> (Illimité - pas de limite)")

    
    def update_backups_list(self, backups):
        """Update the backups list display."""
        text = ""
        for backup in backups:
            text += f"• {backup['name']} ({backup['size_mb']} MB) - {backup['date']}\n"
        
        if not backups:
            text = lang.get("backup_no_backups_yet")
        
        self.backups_list.setText(text)
    
    def update_cookies_info_display(self, cookies_info):
        """Update the cookies backup info display with latest data."""
        # Update backups count
        cookies_total_backups = len(cookies_info["backups"])
        self.cookies_total_label.setText(f"{cookies_total_backups}")
        
        # Update last backup date
        cookies_last_backup_date = self.config_manager.get("cookies_backup_last_date")
        if cookies_last_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(cookies_last_backup_date)
                cookies_last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                cookies_last_backup_str = "N/A"
        else:
            cookies_last_backup_str = "Aucune sauvegarde"
        self.cookies_last_backup_label.setText(cookies_last_backup_str)
        
        # Update usage display for cookies
        if hasattr(self, 'cookies_usage_label'):
            current_mb = cookies_info["current_usage_mb"]
            size_limit = cookies_info["size_limit_mb"]
            self.update_cookies_usage_display(current_mb, size_limit)
    
    def update_cookies_usage_display(self, current_mb, size_limit_mb):
        """Update the cookies usage display label with better formatting."""
        if size_limit_mb > 0:
            percentage = (current_mb / size_limit_mb) * 100 if size_limit_mb > 0 else 0
            
            # Color based on usage
            if percentage > 90:
                color = "#FF4444"  # Red
                status = "⚠️ Presque plein"
            elif percentage > 70:
                color = "#FFAA00"  # Orange
                status = "⚡ Modéré"
            else:
                color = "#00AA00"  # Green
                status = "✓ Normal"
            
            usage_text = f"<span style='color: {color}; font-weight: bold;'>{current_mb} MB / {size_limit_mb} MB ({percentage:.1f}%) - {status}</span>"
            self.cookies_usage_label.setText(usage_text)
        else:
            self.cookies_usage_label.setText(f"<b>{current_mb} MB</b> (Illimité - pas de limite)")
    
    def update_characters_info_display(self, backup_info):
        """Update the characters backup info display with latest data."""
        # Update backups count
        total_backups = len(backup_info["backups"])
        self.total_label.setText(f"{total_backups}")
        
        # Update last backup date
        last_backup_date = self.config_manager.get("backup_last_date")
        if last_backup_date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_backup_date)
                last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_backup_str = "N/A"
        else:
            last_backup_str = "Aucune sauvegarde"
        self.last_backup_label.setText(last_backup_str)
        
        # Update usage display for characters
        if hasattr(self, 'usage_label'):
            current_mb = backup_info["current_usage_mb"]
            size_limit = backup_info["size_limit_mb"]
            self.update_usage_display(current_mb, size_limit)
    
    def backup_now(self):
        """Perform a backup immediately, ignoring daily limit."""
        import sys
        import logging
        
        print("[UI_BACKUP] Manual backup button clicked - Starting backup process...")
        sys.stdout.flush()
        logging.info("[UI_BACKUP] Manual backup initiated from settings dialog")
        
        result = self.backup_manager.backup_characters_force()
        
        print(f"[UI_BACKUP] Backup result: {result['success']} - {result['message']}")
        sys.stdout.flush()
        
        if result["success"]:
            print("[UI_BACKUP] SUCCESS - Updating display...")
            sys.stdout.flush()
            QMessageBox.information(
                self,
                lang.get("backup_success_title"),
                result["message"]
            )
            # Refresh characters backup info
            backup_info = self.backup_manager.get_backup_info()
            self.update_characters_info_display(backup_info)
            self.update_backups_list(backup_info["backups"])
            print("[UI_BACKUP] Display updated successfully")
            sys.stdout.flush()
        else:
            print("[UI_BACKUP] FAILED - Showing error message...")
            sys.stdout.flush()
            QMessageBox.warning(
                self,
                lang.get("backup_error_title"),
                result["message"]
            )
    
    def backup_cookies_now(self):
        """Perform a cookies backup immediately, ignoring daily limit."""
        import sys
        import logging
        
        print("[UI_BACKUP_COOKIES] Manual cookies backup button clicked - Starting backup process...")
        sys.stdout.flush()
        logging.info("[UI_BACKUP_COOKIES] Manual cookies backup initiated from settings dialog")
        
        result = self.backup_manager.backup_cookies_force()
        
        print(f"[UI_BACKUP_COOKIES] Backup result: {result['success']} - {result['message']}")
        sys.stdout.flush()
        
        if result["success"]:
            print("[UI_BACKUP_COOKIES] SUCCESS - Updating display...")
            sys.stdout.flush()
            QMessageBox.information(
                self,
                lang.get("backup_success_title"),
                result["message"]
            )
            # Refresh cookies backup info
            cookies_info = self.backup_manager.get_cookies_backup_info()
            self.update_cookies_info_display(cookies_info)
            print("[UI_BACKUP_COOKIES] Display updated successfully")
            sys.stdout.flush()
        else:
            print("[UI_BACKUP_COOKIES] FAILED - Showing error message...")
            sys.stdout.flush()
            QMessageBox.warning(
                self,
                lang.get("backup_error_title"),
                result["message"]
            )
    
    def accept(self):
        """Save settings and close dialog."""
        try:
            # Validate and save settings for CHARACTERS
            backup_path = self.path_edit.text()
            if backup_path:
                self.config_manager.set("backup_path", backup_path)
            
            self.config_manager.set("backup_enabled", self.enabled_checkbox.isChecked())
            self.config_manager.set("backup_compress", self.compress_checkbox.isChecked())
            
            # Validate numeric inputs for size limit only
            try:
                size_limit = int(self.size_limit_spin.text())
                self.config_manager.set("backup_size_limit_mb", size_limit)
            except ValueError:
                QMessageBox.warning(self, lang.get("error_title"),
                                  lang.get("backup_invalid_size_limit"))
                return
            
            # Update backup manager with new settings for characters
            self.backup_manager.backup_dir = self.backup_manager._get_backup_dir()
            self.backup_manager._ensure_backup_dir()
            
            # Validate and save settings for COOKIES
            cookies_backup_path = self.cookies_path_edit.text()
            if cookies_backup_path:
                self.config_manager.set("cookies_backup_path", cookies_backup_path)
            
            self.config_manager.set("cookies_backup_enabled", self.cookies_enabled_checkbox.isChecked())
            self.config_manager.set("cookies_backup_compress", self.cookies_compress_checkbox.isChecked())
            
            # Validate numeric inputs for cookies size limit
            try:
                cookies_size_limit = int(self.cookies_size_limit_spin.text())
                self.config_manager.set("cookies_backup_size_limit_mb", cookies_size_limit)
            except ValueError:
                QMessageBox.warning(self, lang.get("error_title"),
                                  lang.get("backup_invalid_size_limit"))
                return
            
            # Update backup manager with new settings for cookies
            self.backup_manager._ensure_cookies_backup_dir()
            
            QMessageBox.information(
                self,
                lang.get("backup_settings_saved_title"),
                lang.get("backup_settings_saved_message")
            )
            
            super().accept()
        
        except Exception as e:
            logging.error(f"Error saving backup settings: {e}", exc_info=True)
            QMessageBox.critical(self, lang.get("error_title"),
                               f"{lang.get('backup_settings_error')} : {str(e)}")