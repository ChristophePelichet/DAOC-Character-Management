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
    QPushButton, QLineEdit, QComboBox, QCheckBox, QMessageBox,
    QDialogButtonBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget, QTextEdit, QApplication, QProgressBar, QMenu, QGridLayout,
    QFrame, QScrollArea, QSplitter, QListWidget, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QBrush, QColor, QIcon, QPixmap
from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir
from Functions.character_manager import get_character_dir
from Functions.logging_manager import get_log_dir, get_logger, log_with_action, LOGGER_CHARACTER
from Functions.data_manager import DataManager
from Functions.theme_manager import get_scaled_size
from Functions.items_database_manager import ItemsDatabaseManager
from Functions.items_price_manager import items_price_sync_template
from Functions.character_validator import (
    character_populate_classes_combo, character_populate_races_combo,
    character_handle_realm_change, character_handle_class_change,
    character_handle_race_change
)
from Functions.character_rr_calculator import (
    character_rr_get_valid_levels, character_rr_calculate_points_info,
    character_rr_calculate_from_points
)
from Functions.character_herald_scrapper import (
    character_herald_update,
    character_herald_apply_scraped_stats, character_herald_apply_partial_stats
)
from Functions.character_banner import (
    banner_load_class_image, banner_set_placeholder
)
from Functions.herald_url_validator import (
    herald_url_on_text_changed, herald_url_open_url,
    herald_url_update_button_states
)
from Functions.ui_validation_helper import (
    validate_basic_character_info,
    validate_character_rename, validate_new_character_dialog_data
)
from Functions.armor_upload_handler import (
    armor_upload_file, armor_import_template, armor_open_file,
    armor_delete_file
)
from Functions.item_model_viewer import (
    item_model_on_link_clicked, item_model_show
)
from Functions.character_achievement_formatter import (
    character_update_achievements_display
)
from UI.ui_message_helper import (
    msg_show_success, msg_show_error, msg_show_warning, 
    msg_show_confirmation, msg_show_info_with_details
)
from UI.ui_state_manager import (
    ui_state_set_herald_buttons, ui_state_set_armor_buttons,
    ui_state_on_selection_changed
)
from UI.ui_file_dialogs import (
    dialog_open_file, dialog_save_file, dialog_select_directory,
    dialog_select_backup_path
)
from UI.ui_getters import (
    ui_get_visibility_config, ui_get_selected_category, ui_get_selected_changes
)

# Get CHARACTER logger
logger_char = get_logger(LOGGER_CHARACTER)


class HeraldScraperWorker(QThread):
    """Worker thread pour scraper Herald sans bloquer l'interface"""
    finished = Signal(bool, object, str)  # success, data, error_msg
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        """Execute scraping in background"""
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
        
        # Flag to know if Herald scraping is in progress
        self.herald_scraping_in_progress = False

        self.setWindowTitle(lang.get("character_sheet_title", name=char_name))
        self.resize(500, 400)
        
        # Enable window resizing and minimize button
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setSizeGripEnabled(True)  # Add resize grip in bottom-right corner
        
        # Connect to Herald validation end signal if available
        if hasattr(parent, 'ui_manager'):
            ui_manager = parent.ui_manager
            # Connect to Eden thread finished signal to reactivate buttons
            if hasattr(ui_manager, 'eden_status_thread') and ui_manager.eden_status_thread:
                ui_manager.eden_status_thread.finished.connect(self._update_herald_buttons_state)
            # Initialize button states after creation (via QTimer to ensure they exist)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._update_herald_buttons_state)

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
        
        # Eden Herald Section - AT THE TOP to FACILITATE UPDATE
        eden_group = QGroupBox(lang.get("character_sheet.labels.eden_herald"))
        eden_layout = QVBoxLayout()
        
        # URL du Herald
        url_form_layout = QFormLayout()
        self.herald_url_edit = QLineEdit()
        current_url = self.character_data.get('url', '')
        self.herald_url_edit.setText(current_url)
        self.herald_url_edit.setPlaceholderText(lang.get("character_sheet.labels.herald_url_placeholder"))
        self.herald_url_edit.textChanged.connect(self.on_herald_url_changed)
        url_form_layout.addRow(lang.get("character_sheet.labels.herald_url"), self.herald_url_edit)
        eden_layout.addLayout(url_form_layout)
        
        # Boutons d'action Herald
        herald_buttons_layout = QHBoxLayout()
        
        self.open_herald_button = QPushButton(lang.get("character_sheet.labels.open_browser"))
        self.open_herald_button.setToolTip(lang.get("character_sheet.labels.open_browser_tooltip"))
        self.open_herald_button.clicked.connect(self.open_herald_url)
        self.open_herald_button.setMinimumHeight(28)
        herald_buttons_layout.addWidget(self.open_herald_button)
        
        self.update_herald_button = QPushButton(lang.get("character_sheet.labels.update_from_herald"))
        self.update_herald_button.setToolTip(lang.get("character_sheet.labels.update_from_herald_tooltip"))
        self.update_herald_button.clicked.connect(self.update_from_herald)
        self.update_herald_button.setMinimumHeight(30)
        # Highlight the update button
        self.update_herald_button.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        herald_buttons_layout.addWidget(self.update_herald_button)
        
        # Set equal stretch for both buttons
        herald_buttons_layout.setStretch(0, 1)
        herald_buttons_layout.setStretch(1, 1)
        
        eden_layout.addLayout(herald_buttons_layout)
        eden_group.setLayout(eden_layout)
        layout.addWidget(eden_group)
        
        # Visual separator
        layout.addSpacing(10)
        
        # Basic Information Section
        info_group = QGroupBox(lang.get("character_sheet.labels.general_info"))
        info_layout = QFormLayout()
        
        # Editable name field with Enter key support
        self.name_edit = QLineEdit()
        self.name_edit.setText(char_name)
        self.name_edit.setPlaceholderText(lang.get("character_sheet.labels.name_placeholder"))
        self.name_edit.returnPressed.connect(self.rename_character)  # Rename on Enter key
        info_layout.addRow(lang.get("character_sheet.labels.name"), self.name_edit)
        
        # Editable realm dropdown
        self.realm_combo = QComboBox()
        from Functions.character_manager import REALMS
        self.realm_combo.addItems(REALMS)
        self.realm_combo.setCurrentText(self.realm)
        self.realm_combo.currentTextChanged.connect(self._on_realm_changed_sheet)
        info_layout.addRow(lang.get("character_sheet.labels.realm"), self.realm_combo)
        
        # Initialize DataManager for race/class data
        self.data_manager = DataManager()
        
        # Editable class dropdown (BEFORE race)
        self.class_combo = QComboBox()
        self._populate_classes_sheet()
        current_class = self.character_data.get('class', '')
        if current_class:
            # Use findData to select by itemData (English name) instead of displayed text
            class_index = self.class_combo.findData(current_class)
            if class_index >= 0:
                self.class_combo.setCurrentIndex(class_index)
        self.class_combo.currentTextChanged.connect(self._on_class_changed_sheet)
        info_layout.addRow(lang.get("character_sheet.labels.class"), self.class_combo)
        
        # Editable race dropdown (AFTER class)
        self.race_combo = QComboBox()
        self._populate_races_sheet()
        current_race = self.character_data.get('race', '')
        if current_race:
            # Use findData to select by itemData (English name) instead of displayed text
            race_index = self.race_combo.findData(current_race)
            if race_index >= 0:
                self.race_combo.setCurrentIndex(race_index)
        self.race_combo.currentTextChanged.connect(self._on_race_changed_sheet)
        info_layout.addRow(lang.get("character_sheet.labels.race"), self.race_combo)
        
        # Editable level dropdown (1-50)
        self.level_combo = QComboBox()
        self.level_combo.addItems([str(i) for i in range(1, 51)])
        current_level = self.character_data.get('level', 1)
        self.level_combo.setCurrentText(str(current_level))
        info_layout.addRow(lang.get("character_sheet.labels.level"), self.level_combo)
        
        # Editable season dropdown
        self.season_combo = QComboBox()
        from Functions.config_manager import config
        seasons = config.get("game.seasons", ["S3"])
        self.season_combo.addItems(seasons)
        current_season = self.character_data.get('season', 'S3')
        self.season_combo.setCurrentText(current_season)
        info_layout.addRow(lang.get("character_sheet.labels.season"), self.season_combo)
        
        # Editable server dropdown
        self.server_combo = QComboBox()
        servers = config.get("game.servers", ["Eden"])
        self.server_combo.addItems(servers)
        current_server = self.character_data.get('server', 'Eden')
        self.server_combo.setCurrentText(current_server)
        info_layout.addRow(lang.get("character_sheet.labels.server"), self.server_combo)
        
        # Editable page dropdown (1-5)
        self.page_combo = QComboBox()
        self.page_combo.addItems([str(i) for i in range(1, 6)])
        current_page = self.character_data.get('page', 1)
        self.page_combo.setCurrentText(str(current_page))
        info_layout.addRow(lang.get("character_sheet.labels.page"), self.page_combo)
        
        # Editable guild text field
        self.guild_edit = QLineEdit()
        self.guild_edit.setText(self.character_data.get('guild', ''))
        self.guild_edit.setPlaceholderText(lang.get("character_sheet.labels.guild_placeholder"))
        info_layout.addRow(lang.get("character_sheet.labels.guild"), self.guild_edit)
        
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
        
        ui_state_set_herald_buttons(
            self,
            character_selected=True,
            herald_url=herald_url,
            scraping_active=False,
            validation_active=not herald_validation_done
        )
        
        # Subscribe to validation end signal to reactivate the button
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
        realm_rank_group = QGroupBox(lang.get("character_sheet.labels.realm_rank_group"))
        realm_rank_layout = QVBoxLayout()
        
        realm_points = self.character_data.get('realm_points', 0)
        # Convert realm_points to integer if it's a string
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
        rank_dropdown_layout.addWidget(QLabel(lang.get("character_sheet.labels.rank")))
        
        self.rank_combo = QComboBox()
        for i in range(1, 15):  # Ranks 1-14
            self.rank_combo.addItem(str(i), i)
        self.rank_combo.setCurrentIndex(current_rank - 1)
        self.rank_combo.currentIndexChanged.connect(self.on_rank_changed)
        rank_dropdown_layout.addWidget(self.rank_combo)
        
        # Level dropdown (0-10 for rank 1, 0-9 for others)
        rank_dropdown_layout.addWidget(QLabel(lang.get("character_sheet.labels.rank_level")))
        
        self.level_combo_rank = QComboBox()
        self.update_level_dropdown(current_rank, current_level)
        self.level_combo_rank.currentIndexChanged.connect(self.on_level_changed)
        rank_dropdown_layout.addWidget(self.level_combo_rank)
        
        rank_dropdown_layout.addStretch()  # Push controls to the left
        
        realm_rank_layout.addLayout(rank_dropdown_layout)
        
        realm_rank_group.setLayout(realm_rank_layout)
        layout.addWidget(realm_rank_group)
        
        # Armor Manager button (moved here after Realm Rank section)
        armor_manager_button = QPushButton(lang.get("character_sheet.labels.armor_manager"))
        armor_manager_button.clicked.connect(self.open_armor_manager)
        armor_manager_button.setToolTip(lang.get("character_sheet.labels.armor_manager_tooltip"))
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
        realm = self.character_data.get('realm', 'Albion')
        class_name = self.character_data.get('class', '')
        banner_load_class_image(self, realm, class_name)
    
    def _set_banner_placeholder(self, text):
        """Set placeholder text for banner"""
        banner_set_placeholder(self, text)
    
    def _populate_classes_sheet(self):
        """Populates class dropdown based on selected realm."""
        character_populate_classes_combo(self.class_combo, self.data_manager, self.realm_combo.currentText())

    def _populate_races_sheet(self):
        """Populates race dropdown based on selected class and realm."""
        realm = self.realm_combo.currentText()
        class_index = self.class_combo.currentIndex()
        class_name = self.class_combo.itemData(class_index) if class_index >= 0 else None
        character_populate_races_combo(self.race_combo, self.data_manager, realm, class_name)
    
    def _on_realm_changed_sheet(self):
        """Called when realm is changed in character sheet."""
        character_handle_realm_change(
            self.realm_combo, self.class_combo, self.race_combo,
            self.data_manager, self.character_data
        )
        # Update banner after realm change
        self._update_class_banner()
    
    def _on_class_changed_sheet(self):
        """Called when class is changed in character sheet."""
        character_handle_class_change(
            self.class_combo, self.race_combo,
            self.data_manager, self.realm_combo.currentText(),
            self.character_data
        )
        # Update banner after class change
        self._update_class_banner()
    
    def _on_race_changed_sheet(self):
        """Called when race is changed in character sheet."""
        character_handle_race_change(self.race_combo, self.character_data)
    
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
        self.level_combo_rank.blockSignals(True)
        self.level_combo_rank.clear()

        valid_levels = character_rr_get_valid_levels(rank)
        for level in valid_levels:
            self.level_combo_rank.addItem(f"L{level}", level)

        # Set current level
        if current_level <= valid_levels[-1]:
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

        info = character_rr_calculate_points_info(
            self.parent_app.data_manager, self.realm, rank, level
        )

        if info:
            level_str = info.get('current_level_str', f"{rank}L{level}")
            rank_data = self.parent_app.data_manager.get_rank_by_level(self.realm, level_str)
            if rank_data:
                self.rank_title_label.setText(
                    f"Rank {rank_data['rank']} - {rank_data['title']} "
                    f"({rank_data['level']} - {rank_data['realm_points']:,} RP)"
                )
    
    def update_rank_display(self, realm_points):
        """Updates current rank and title display."""
        if not hasattr(self.parent_app, 'data_manager'):
            return

        rank_info = character_rr_calculate_from_points(
            self.parent_app.data_manager, self.realm, realm_points
        )

        if rank_info:
            self.rank_title_label.setText(
                f"Rank {rank_info['rank']} - {rank_info['title']} "
                f"({rank_info['level']} - {rank_info['realm_points']:,} RP)"
            )
    
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
                QMessageBox.information(self, lang.get("dialogs.titles.success"), lang.get("character_sheet.messages.rank_update_success", level=level_str, rp=new_rp))
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
            
            # Validate all basic character info fields using centralized validation
            validation_result = validate_basic_character_info(
                "",  # character_name not used in this context
                self.guild_edit.text(),
                self.herald_url_edit.text()
            )
            if not validation_result['valid']:
                QMessageBox.critical(self, "Erreur", validation_result['message'])
                return
            
            new_guild = validation_result['guild']
            herald_url = validation_result['url']
            
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
            
            msg_show_success(self, "titles.success", "character_sheet.messages.info_update_success")
            # Refresh list in parent
            if hasattr(self.parent_app, 'refresh_character_list'):
                self.parent_app.refresh_character_list()
                
        except Exception as e:
            log_with_action(logger_char, "error", f"Error saving basic info: {str(e)}", action="ERROR")
            msg_show_error(self, "titles.error", "character_sheet.messages.save_error", error=str(e))

    def open_armor_manager(self):
        """Opens the armor management dialog."""
        try:
            season = self.character_data.get('season', 'S3')
            realm = self.character_data.get('realm', '')
            character_name = self.character_data.get('name', '')
            
            if not realm or not character_name:
                QMessageBox.warning(self, lang.get("dialogs.titles.error"), lang.get("character_sheet.messages.character_id_error"))
                return
            
            dialog = ArmorManagementDialog(self, season, realm, character_name, self.character_data)
            dialog.show()  # Non-modal: permet d'utiliser le reste de l'application
        except Exception as e:
            import traceback
            error_msg = lang.get("character_sheet.messages.armor_manager_error", error=str(e), traceback=traceback.format_exc())
            logging.error(error_msg)
            QMessageBox.critical(self, lang.get("dialogs.titles.error"), error_msg)
    
    def on_herald_url_changed(self, text):
        """Enable/disable the stats update button based on the Herald URL"""
        herald_url_on_text_changed(self, text)
    
    def _is_herald_validation_done(self):
        """Check if Herald startup validation is complete"""
        if not hasattr(self.parent_app, 'ui_manager'):
            return True  # If no ui_manager, consider as done
        
        # Check if validation thread is running
        if hasattr(self.parent_app.ui_manager, 'eden_status_thread'):
            thread = self.parent_app.ui_manager.eden_status_thread
            if thread and thread.isRunning():
                return False
        
        return True
    
    def _on_herald_validation_finished(self, accessible, message):
        """Called when Herald startup validation completes"""
        # Re-enable button if Herald accessible AND a URL is configured
        herald_url = self.character_data.get('url', '').strip()
        ui_state_set_herald_buttons(
            self,
            character_selected=True,
            herald_url=herald_url,
            scraping_active=False,
            validation_active=False
        )
    
    def show_stats_info(self):
        """Display an information window about statistics"""
        msg_show_info_with_details(
            self,
            "stats_info_title",
            lang.get("stats_info_message")
        )
    
    def _update_achievements_display(self, achievements_list):
        """Update achievements display with the provided list."""
        character_update_achievements_display(self, achievements_list)
    
    def open_herald_url(self):
        """Ouvre l'URL du Herald dans le navigateur avec les cookies"""
        herald_url_open_url(self)
    
    def update_rvr_stats(self):
        """Update RvR statistics from Herald"""
        from Functions.herald_ui_wrappers import herald_ui_update_rvr_stats
        herald_ui_update_rvr_stats(self, self.herald_url_edit)
    
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
        """✅ Pattern 4: Called when user closes stats dialog"""
        import logging
        logging.info("Dialogue stats fermé par utilisateur - Arrêt mise à jour")
        
        # Stop thread cleanly
        self._stop_stats_thread()
        
        # Re-enable button using state manager
        herald_url = self.character_data.get('url', '').strip()
        ui_state_set_herald_buttons(
            self,
            character_selected=True,
            herald_url=herald_url,
            scraping_active=False,
            validation_active=False
        )
    
    def _stop_stats_thread(self):
        """✅ Pattern 2 + 3: Stop stats thread with complete cleanup"""
        if hasattr(self, 'stats_update_thread') and self.stats_update_thread:
            if self.stats_update_thread.isRunning():
                # 1. Request graceful stop
                self.stats_update_thread.request_stop()
                
                # 2. Disconnect signals
                try:
                    self.stats_update_thread.step_started.disconnect()
                    self.stats_update_thread.step_completed.disconnect()
                    self.stats_update_thread.step_error.disconnect()
                    self.stats_update_thread.stats_updated.disconnect()
                    self.stats_update_thread.update_failed.disconnect()
                except Exception:
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
            except Exception:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
    
    def _on_stats_updated(self, results):
        """Called when stats are updated (success or partial)"""
        from PySide6.QtCore import QTimer
        
        # Fermer le dialogue de progression
        if hasattr(self, 'progress_dialog'):
            success_text = lang.get("progress_stats_complete", default="✅ Statistiques récupérées")
            self.progress_dialog.complete_all(success_text)
            QTimer.singleShot(1500, self.progress_dialog.close)
        
        # Extract results
        result_rvr = results.get('rvr', {})
        result_pvp = results.get('pvp', {})
        result_pve = results.get('pve', {})
        result_wealth = results.get('wealth', {})
        result_achievements = results.get('achievements', {})
        
        all_success = result_rvr.get('success') and result_pvp.get('success') and result_pve.get('success') and result_wealth.get('success')
        
        if all_success:
            # Complete successful update
            self._update_all_stats_ui(result_rvr, result_pvp, result_pve, result_wealth, result_achievements)
            
            # Sauvegarder dans le JSON
            from Functions.character_manager import save_character
            success, msg = save_character(self.character_data, allow_overwrite=True)
            
            if success:
                # Success message
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
                    lang.get("dialogs.titles.success"),
                    f"{lang.get('character_sheet.messages.stats_update_success')}\n\n"
                    f"{lang.get('character_sheet.sections.rvr')}\n"
                    f"🗼 Tower Captures: {tower:,}\n"
                    f"🏰 Keep Captures: {keep:,}\n"
                    f"💎 Relic Captures: {relic:,}\n\n"
                    f"{lang.get('character_sheet.sections.pvp')}\n"
                    f"⚔️ Solo Kills: {solo_kills:,} (Alb: {solo_kills_alb:,}, Hib: {solo_kills_hib:,}, Mid: {solo_kills_mid:,})\n"
                    f"💀 Deathblows: {deathblows:,} (Alb: {deathblows_alb:,}, Hib: {deathblows_hib:,}, Mid: {deathblows_mid:,})\n"
                    f"🎯 Kills: {kills:,} (Alb: {kills_alb:,}, Hib: {kills_hib:,}, Mid: {kills_mid:,})\n\n"
                    f"{lang.get('character_sheet.sections.pve')}\n"
                    f"🐉 Dragons: {dragon_kills:,}  |  👹 Légions: {legion_kills:,}\n"
                    f"🐲 Mini Dragons: {mini_dragon_kills:,}  |  ⚔️ Epic Encounters: {epic_encounters:,}\n"
                    f"🏛️ Epic Dungeons: {epic_dungeons:,}  |  🐊 Sobekite: {sobekite:,}\n\n"
                    f"{lang.get('character_sheet.sections.wealth')}\n"
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
                    lang.get("dialogs.titles.warning"),
                    lang.get("character_sheet.messages.stats_save_error", msg=msg)
                )
        
        elif result_rvr.get('success') and not result_pvp.get('success'):
            # Partial update: RvR OK, PvP KO
            self._update_partial_stats_ui(result_rvr, None, None, None, None)
            
            QMessageBox.warning(
                self,
                lang.get("character_sheet.messages.partial_update_title"),
                lang.get("character_sheet.messages.rvr_success_pvp_failed", error=result_pvp.get('error', lang.get("character_sheet.messages.unknown_error")))
            )
        
        elif not result_rvr.get('success') and result_pvp.get('success'):
            # Partial update: PvP OK, RvR KO
            self._update_partial_stats_ui(None, result_pvp, None, None, None)
            
            QMessageBox.warning(
                self,
                lang.get("character_sheet.messages.partial_update_title"),
                lang.get("character_sheet.messages.pvp_success_rvr_failed", error=result_rvr.get('error', lang.get("character_sheet.messages.unknown_error")))
            )
        
        else:
            # Complete or multiple failure
            error_msg = f"{lang.get('character_sheet.messages.stats_fetch_failed')}\n\n"
            if not result_rvr.get('success'):
                error_msg += f"❌ RvR Captures: {result_rvr.get('error', lang.get('character_sheet.messages.unknown_error'))}\n"
            if not result_pvp.get('success'):
                error_msg += f"❌ PvP Stats: {result_pvp.get('error', lang.get('character_sheet.messages.unknown_error'))}\n"
            if not result_pve.get('success'):
                error_msg += f"❌ PvE Stats: {result_pve.get('error', lang.get('character_sheet.messages.unknown_error'))}\n"
            if not result_wealth.get('success'):
                error_msg += f"❌ Wealth: {result_wealth.get('error', lang.get('character_sheet.messages.unknown_error'))}\n"
            
            QMessageBox.critical(self, lang.get("character_sheet.messages.stats_fetch_error_title"), error_msg)
        
        # Réactiver le bouton avec state manager
        if not self.herald_scraping_in_progress:
            herald_url = self.character_data.get('url', '').strip()
            ui_state_set_herald_buttons(
                self,
                character_selected=True,
                herald_url=herald_url,
                scraping_active=False,
                validation_active=False
            )
    
    def _on_stats_failed(self, error_message):
        """Called in case of complete update failure"""
        from PySide6.QtCore import QTimer
        
        # Fermer le dialogue de progression
        if hasattr(self, 'progress_dialog'):
            error_text = lang.get("progress_error", default="❌ {error}", error=error_message)
            self.progress_dialog.set_status_message(error_text, "#F44336")
            QTimer.singleShot(2000, self.progress_dialog.close)
        
        # Afficher l'erreur
        QMessageBox.critical(
            self,
            lang.get("character_sheet.messages.stats_fetch_error_title"),
            f"{lang.get('character_sheet.messages.stats_fetch_failed')}\n{error_message}"
        )
        
        # Re-enable buttons with state manager
        if not self.herald_scraping_in_progress:
            herald_url = self.character_data.get('url', '').strip()
            ui_state_set_herald_buttons(
                self,
                character_selected=True,
                herald_url=herald_url,
                scraping_active=False,
                validation_active=False
            )
        
        log_with_action(logger_char, "error", f"Stats update error: {error_message}", action="ERROR")
    
    def _update_herald_buttons_state(self):
        """Update Herald button states based on Eden validation status"""
        herald_url_update_button_states(self)
    
    def _update_all_stats_ui(self, result_rvr, result_pvp, result_pve, result_wealth, result_achievements):
        """Update all UI labels with complete stats"""
        character_herald_apply_scraped_stats(
            self, result_rvr, result_pvp, result_pve, result_wealth, result_achievements
        )
    
    def _update_partial_stats_ui(self, result_rvr, result_pvp, result_pve, result_wealth, result_achievements):
        """Update UI and character_data for partial update"""
        character_herald_apply_partial_stats(
            self, result_rvr, result_pvp, result_pve, result_wealth, result_achievements
        )
    
    def update_from_herald(self):
        """Update character data from Herald"""
        url = self.herald_url_edit.text().strip()
        character_herald_update(self, url)
    
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
        """✅ Pattern 4: Called when user closes character update dialog"""
        import logging
        logging.info("Dialogue character update fermé par utilisateur - Arrêt mise à jour")
        
        # Stop thread cleanly
        self._stop_char_update_thread()
        
        # Re-enable buttons using state manager
        self.herald_scraping_in_progress = False
        herald_url = self.character_data.get('url', '').strip()
        ui_state_set_herald_buttons(
            self,
            character_selected=True,
            herald_url=herald_url,
            scraping_active=False,
            validation_active=False
        )
    
    def _stop_char_update_thread(self):
        """✅ Pattern 2 + 3: Stop character update thread with complete cleanup"""
        if hasattr(self, 'char_update_thread') and self.char_update_thread:
            if self.char_update_thread.isRunning():
                # 1. Request graceful stop
                self.char_update_thread.request_stop()
                
                # 2. Disconnect signals
                try:
                    self.char_update_thread.step_started.disconnect()
                    self.char_update_thread.step_completed.disconnect()
                    self.char_update_thread.step_error.disconnect()
                    self.char_update_thread.update_finished.disconnect()
                except Exception:
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
            except Exception:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
    
    def closeEvent(self, event):
        """✅ Pattern 5: Cleanup threads when closing character sheet window"""
        import logging
        logging.info("CharacterSheetWindow closing - Stopping update thread if running")
        
        # Stop character update thread if running
        self._stop_char_update_thread()
        
        # Accept close event
        event.accept()
    
    def _on_herald_scraping_finished(self, success, new_data, error_msg):
        """Callback called when scraping is complete"""
        from PySide6.QtCore import QTimer
        
        # Mark that Herald scraping is complete
        self.herald_scraping_in_progress = False
        
        # Close progress dialog with success or error message
        if hasattr(self, 'progress_dialog'):
            if success:
                success_text = lang.get("progress_character_complete", default="✅ Données récupérées")
                self.progress_dialog.complete_all(success_text)
                QTimer.singleShot(1500, self.progress_dialog.close)
            else:
                error_text = lang.get("progress_error", default="❌ {error}", error=error_msg)
                self.progress_dialog.set_status_message(error_text, "#F44336")
                QTimer.singleShot(2000, self.progress_dialog.close)
        
        # Use try/finally to guarantee button re-enabling and thread cleanup
        try:
            if not success:
                # ✅ CRITICAL: Stop thread BEFORE displaying error
                self._stop_char_update_thread()
                
                QMessageBox.critical(
                    self,
                    lang.get("update_char_error"),
                    f"{lang.get('update_char_error')}: {error_msg}"
                )
                return
            
            # Create dialog to detect changes
            dialog = CharacterUpdateDialog(self, self.character_data, new_data, self.character_data['name'])
            
            # Check if there's at least one change
            if not dialog.has_changes():
                # ✅ CRITICAL: Stop thread BEFORE displaying message
                self._stop_char_update_thread()
                
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
                
                # Apply selected changes directly to character_data
                for field, value in selected_changes.items():
                    self.character_data[field] = value
                
                # Update all interface fields for immediate display
                # (rebuild complete display rather than update field by field)
                
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
                    
                    # Update rank and title display
                    self.update_rank_display(realm_points)
                    
                    # Update rank/level dropdowns
                    if hasattr(self.parent_app, 'data_manager'):
                        rank_info = self.parent_app.data_manager.get_realm_rank_info(self.realm, realm_points)
                        if rank_info:
                            current_rank = rank_info['rank']
                            level_str = rank_info['level']  # Format "XLY"
                            level_match = re.search(r'L(\d+)', level_str)
                            if level_match:
                                current_level = int(level_match.group(1))
                                
                                # Update rank dropdown
                                self.rank_combo.blockSignals(True)
                                self.rank_combo.setCurrentIndex(current_rank - 1)
                                self.rank_combo.blockSignals(False)
                                
                                # Update level dropdown
                                self.update_level_dropdown(current_rank, current_level)
                
                # Save character_data directly (not via save_basic_info which retrieves from interface)
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
                
                # Refresh character list in main window
                if hasattr(self.parent_app, 'tree_manager'):
                    self.parent_app.tree_manager.refresh_character_list()
                elif hasattr(self.parent_app, 'refresh_character_list'):
                    self.parent_app.refresh_character_list()
                
                # Success message
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
            # ✅ Final cleanup if not already done (security)
            if hasattr(self, 'char_update_thread') and self.char_update_thread:
                self._stop_char_update_thread()
            
            # Always re-enable all buttons, even in case of error or early return
            herald_url = self.character_data.get('url', '').strip()
            ui_state_set_herald_buttons(
                self,
                character_selected=True,
                herald_url=herald_url,
                scraping_active=False,
                validation_active=False
            )
            
            # Force visual update
            QApplication.processEvents()
    
    def rename_character(self):
        """Renames the character with validation."""
        try:
            old_name = self.character_data.get('name', '')
            
            # Validate new name using centralized validation
            result = validate_character_rename(self.name_edit.text())
            if not result['valid']:
                msg_show_warning(self, "titles.warning", result['message'])
                self.name_edit.setText(old_name)
                return
            
            new_name = result['value']
            if old_name == new_name:
                msg_show_info_with_details(self, "titles.info", "Le nom n'a pas changé.")
                return
            
            # Confirm rename
            if msg_show_confirmation(self, "Confirmer le renommage", f"Renommer '{old_name}' en '{new_name}' ?"):
                from Functions.character_manager import rename_character
                from Functions.character_rename_handler import character_rename_with_validation
                
                success, msg = character_rename_with_validation(
                    self.character_data, new_name, rename_character
                )
                
                if success:
                    # Update window title
                    self.setWindowTitle(f"Fiche personnage - {new_name}")
                    
                    # Refresh list in parent
                    if hasattr(self.parent_app, 'refresh_character_list'):
                        self.parent_app.refresh_character_list()
                else:
                    msg_show_error(self, "titles.error", f"Échec du renommage : {msg}")
                    self.name_edit.setText(old_name)  # Reset to original name
                    
        except Exception as e:
            msg_show_error(self, "titles.error", f"Erreur lors du renommage : {str(e)}")
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
        current_visibility = config.get("ui.column_visibility", {})
        
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
        return ui_get_visibility_config(self.checkboxes)


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
        current_lang = config.get("ui.language", "en")
        
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
        current_lang = config.get("ui.language", "en")
        
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

    def accept(self):
        """Override accept to validate before closing the dialog."""
        # Validate character name and guild
        validation_result = validate_new_character_dialog_data(
            self.name_edit.text(),
            self.guild_edit.text()
        )
        if not validation_result['valid']:
            QMessageBox.warning(self, lang.get("error_title"), validation_result['message'])
            return  # Don't close dialog, stay open for correction
        
        # Validate race/class combination
        realm = self.realm_combo.currentText()
        race = self.race_combo.currentData()
        class_name = self.class_combo.currentData()
        
        if race and class_name:
            if not self.data_manager.is_race_class_compatible(realm, race, class_name):
                QMessageBox.warning(
                    self,
                    lang.get("error_title"),
                    lang.get("invalid_race_class_combo", default=f"La race {race} ne peut pas jouer la classe {class_name}")
                )
                return  # Don't close dialog, stay open for correction
        
        # All validations passed, close the dialog
        super().accept()

    def get_data(self):
        """Returns the entered data (validation already done in accept())."""
        validation_result = validate_new_character_dialog_data(
            self.name_edit.text(),
            self.guild_edit.text()
        )
        name = validation_result['name']
        guild = validation_result['guild']
        
        realm = self.realm_combo.currentText()
        race = self.race_combo.currentData()
        class_name = self.class_combo.currentData()
        season = self.season_combo.currentText()
        level = int(self.level_combo.currentText())
        page = int(self.page_combo.currentText())
        
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
        # Sort themes alphabetically by name
        sorted_themes = sorted(self.available_themes.items(), key=lambda x: x[1])
        for theme_id, theme_name in sorted_themes:
            self.theme_combo.addItem(theme_name, theme_id)
        general_layout.addRow(lang.get("config_theme_label"), self.theme_combo)
        
        # Font Scale ComboBox (100% to 200% in steps of 25%)
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
        
        # Indicate which browsers are detected
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

        # Armory Settings (Position 4)
        logging.debug("Creating Armory settings group")
        armory_group = QGroupBox("🛡️ Armurerie")
        armory_layout = QVBoxLayout()
        
        # Description
        armory_desc = QLabel(
            "L'armurerie permet d'importer des items depuis des fichiers Zenkcraft\n"
            "et de créer une base de données locale d'items."
        )
        armory_desc.setWordWrap(True)
        armory_desc.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        armory_layout.addWidget(armory_desc)
        
        # Import button
        self.armory_import_button = QPushButton("📥 Importer des items depuis Zenkcraft")
        self.armory_import_button.setMinimumHeight(40)
        self.armory_import_button.setToolTip(
            "Ouvre l'interface d'import pour ajouter des items\n"
            "depuis des fichiers templates Zenkcraft (.txt)"
        )
        self.armory_import_button.clicked.connect(self.open_armory_import)
        armory_layout.addWidget(self.armory_import_button)
        
        # Database info
        armory_info_layout = QHBoxLayout()
        armory_info_layout.addWidget(QLabel("📊 Base de données:"))
        self.armory_db_info_label = QLabel("Aucune base chargée")
        self.armory_db_info_label.setStyleSheet("color: #888;")
        armory_info_layout.addWidget(self.armory_db_info_label, 1)
        armory_layout.addLayout(armory_info_layout)
        
        armory_group.setLayout(armory_layout)
        content_layout.addWidget(armory_group)
        logging.debug("Armory settings group added to content_layout")

        # Debug Settings (Position 5 - Last)
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
        
        # Add content widget to scrollable area
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
        
        char_folder = config.get("folders.characters") or get_character_dir()
        # Config folder is NOT configurable - always next to executable
        log_folder = config.get("folders.logs") or get_log_dir()
        armor_folder = config.get("folders.armor") or get_armor_dir()
        cookies_folder = config.get("folders.cookies") or get_config_dir()
        
        self.char_path_edit.setText(char_folder)
        self.char_path_edit.setCursorPosition(0)
        self.config_path_edit.setText(get_config_dir())
        self.config_path_edit.setCursorPosition(0)
        self.log_path_edit.setText(log_folder)
        self.log_path_edit.setCursorPosition(0)
        self.armor_path_edit.setText(armor_folder)
        self.armor_path_edit.setCursorPosition(0)
        self.cookies_path_edit.setText(cookies_folder)
        self.cookies_path_edit.setCursorPosition(0)
        self.debug_mode_check.setChecked(config.get("system.debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("system.show_debug_window", False))
        self.disable_disclaimer_check.setChecked(config.get("system.disable_disclaimer", False))
        
        current_lang_code = config.get("ui.language", "en")
        current_lang_name = self.available_languages.get(current_lang_code, "Français")
        self.language_combo.setCurrentText(current_lang_name)

        # Theme
        current_theme = config.get("ui.theme", "dracula")
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        # Font Scale
        current_font_scale = config.get("ui.font_scale", 1.0)
        # Find index matching value in ComboBox
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

        current_default_server = config.get("game.default_server", "")
        self.default_server_combo.setCurrentText(current_default_server)

        current_default_season = config.get("game.default_season", "")
        self.default_season_combo.setCurrentText(current_default_season)

        current_default_realm = config.get("game.default_realm", "")
        self.default_realm_combo.setCurrentText(current_default_realm)

        
        manual_resize = config.get("ui.manual_column_resize", True)
        self.manual_column_resize_check.setChecked(manual_resize)        # Browser settings
        preferred_browser = config.get("system.preferred_browser", "Chrome")
        self.browser_combo.setCurrentText(preferred_browser)
        
        allow_download = config.get("system.allow_browser_download", False)
        self.allow_browser_download_check.setChecked(allow_download)
        
        # Update armory database info
        self.update_armory_db_info()

    def browse_folder(self, line_edit, title_key):
        """Generic folder browser."""
        directory = dialog_select_directory(self, title_key)
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
    
    def open_armory_import(self):
        """Open item import dialog for armory"""
        from UI.armory_import_dialog import ArmoryImportDialog
        
        dialog = ArmoryImportDialog(self)
        dialog.exec()
        
        # Update database info after import
        self.update_armory_db_info()
    
    def update_armory_db_info(self):
        """Update armory database information"""
        # Check if the label exists (in case method is called before UI is fully created)
        if not hasattr(self, 'armory_db_info_label'):
            return
            
        try:
            import json
            from pathlib import Path
            
            armor_path = config.get('folders.armor')
            if not armor_path:
                self.armory_db_info_label.setText("Chemin non configuré")
                self.armory_db_info_label.setStyleSheet("color: #f44336;")
                return
            
            armor_path = Path(armor_path)
            
            # Count items in all databases
            total_items = 0
            realms = ['albion', 'hibernia', 'midgard']
            
            for realm in realms:
                db_file = armor_path / f"items_database_{realm}.json"
                if db_file.exists():
                    with open(db_file, 'r', encoding='utf-8') as f:
                        database = json.load(f)
                        total_items += len(database.get('items', {}))
            
            if total_items > 0:
                self.armory_db_info_label.setText(f"{total_items} items disponibles")
                self.armory_db_info_label.setStyleSheet("color: #4CAF50;")
            else:
                self.armory_db_info_label.setText("Aucun item")
                self.armory_db_info_label.setStyleSheet("color: #888;")
                
        except Exception as e:
            logging.error(f"Erreur lecture database armory: {e}", exc_info=True)
            if hasattr(self, 'armory_db_info_label'):
                self.armory_db_info_label.setText("Erreur")
                self.armory_db_info_label.setStyleSheet("color: #f44336;")


class ArmorManagementDialog(QDialog):
    """Dialog for managing armor templates for a specific character."""
    
    def __init__(self, parent, season, realm, character_name, character_data=None):
        super().__init__(parent)
        self.season = season
        self.realm = realm
        self.character_name = character_name
        self.character_data = character_data or {}
        
        # Initialize DataManager for class translations
        from Functions.data_manager import DataManager
        self.data_manager = DataManager()
        
        from Functions.armor_manager import ArmorManager
        from Functions.template_manager import TemplateManager
        from Functions.items_database_manager import ItemsDatabaseManager
        from Functions.config_manager import ConfigManager
        from Functions.path_manager import PathManager
        
        self.armor_manager = ArmorManager(season, realm, character_name)
        self.template_manager = TemplateManager()
        
        # Initialize ItemsDatabaseManager for price lookups
        self.config_manager = ConfigManager()
        self.path_manager = PathManager()
        self.db_manager = ItemsDatabaseManager(self.config_manager, self.path_manager)
        
        # Track items without prices for search functionality
        self.items_without_price = []
        
        self.setWindowTitle(lang.get("armoury_dialog.title", name=character_name, realm=realm, season=season))
        self.resize(1400, 700)  # Larger window for better split visibility
        
        # Enable window buttons (minimize, maximize, close)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        
        # Create horizontal splitter for table and preview (no info label)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing
        
        # Left panel: Table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Armor files table
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels([
            lang.get("armoury_dialog.table_headers.filename")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.table)
        
        splitter.addWidget(left_widget)
        
        # Right panel: Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview header
        preview_header = QLabel(lang.get("armoury_dialog.preview.title"))
        preview_header_font = preview_header.font()
        preview_header_font.setBold(True)
        preview_header_font.setPointSize(preview_header_font.pointSize() + 1)
        preview_header.setFont(preview_header_font)
        right_layout.addWidget(preview_header)
        
        # Preview content area - Container widget with dark theme
        preview_container = QWidget()
        preview_container_layout = QVBoxLayout(preview_container)
        preview_container_layout.setContentsMargins(0, 0, 0, 0)
        preview_container_layout.setSpacing(10)
        
        # Apply dark theme to entire preview container
        from PySide6.QtGui import QFont
        preview_container.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: none;
            }
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                gridline-color: #404040;
                border: none;
            }
            QTableWidget::item {
                color: #e0e0e0;
                background-color: #2b2b2b;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #404040;
                padding: 4px;
            }
        """)
        
        # 1. Text preview area - Use QTextBrowser for clickable links
        from PySide6.QtWidgets import QTextBrowser
        self.preview_area = QTextBrowser()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText(lang.get("armoury_dialog.preview.no_selection"))
        self.preview_area.setMinimumWidth(350)
        
        # Enable clickable links for model viewer
        self.preview_area.setOpenExternalLinks(False)  # Handle clicks internally
        self.preview_area.setOpenLinks(False)  # Prevent default link navigation
        self.preview_area.anchorClicked.connect(self._on_model_link_clicked)
        
        # Force Courier New font
        preview_font = QFont("Courier New", 10)
        preview_font.setStyleHint(QFont.Monospace)
        self.preview_area.setFont(preview_font)
        
        preview_container_layout.addWidget(self.preview_area, 1)  # Stretch factor 1
        
        # Add preview container to right layout
        right_layout.addWidget(preview_container)
        
        # Button layout for preview actions
        preview_buttons_layout = QHBoxLayout()
        
        # Download button in preview panel
        self.preview_download_button = QPushButton(lang.get("armoury_dialog.context_menu.download", default="Download"))
        self.preview_download_button.setEnabled(False)  # Disabled until file selected
        self.preview_download_button.clicked.connect(self.download_selected_armor)
        preview_buttons_layout.addWidget(self.preview_download_button)
        
        # Search missing prices button
        self.search_prices_button = QPushButton("🔍 " + lang.get("armoury_dialog.buttons.search_missing_prices", default="Search Missing Prices"))
        self.search_prices_button.setEnabled(False)  # Disabled until items_without_price is populated
        self.search_prices_button.clicked.connect(self.search_missing_prices)
        self.search_prices_button.setToolTip(lang.get("armoury_dialog.tooltips.search_missing_prices", default="Search online for items without price in database"))
        preview_buttons_layout.addWidget(self.search_prices_button)
        
        right_layout.addLayout(preview_buttons_layout)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions (30% table, 70% preview)
        # Force initial sizes based on window width (1400 * 0.3 = 420, 1400 * 0.7 = 980)
        splitter.setSizes([420, 980])
        splitter.setStretchFactor(0, 3)  # Left panel gets less stretch
        splitter.setStretchFactor(1, 7)  # Right panel gets more stretch
        
        layout.addWidget(splitter, 1)  # Stretch factor 1 = take all available space
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_template_button = QPushButton(lang.get("armoury_dialog.buttons.import_template"))
        import_template_button.clicked.connect(self.import_template)
        button_layout.addWidget(import_template_button)
        
        refresh_button = QPushButton(lang.get("armoury_dialog.buttons.refresh"))
        refresh_button.clicked.connect(self.refresh_list)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton(lang.get("armoury_dialog.buttons.close"))
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Load initial data
        self.refresh_list()
    
    def refresh_list(self):
        """Refreshes the armor files list using TemplateManager."""
        try:
            # Get character class from character_data
            character_class = self.character_data.get('class', '')
            
            if not character_class:
                logging.warning("No character class found, cannot filter templates")
                self.table.setRowCount(0)
                return
            
            # Use TemplateManager to get templates for this class and realm
            templates = self.template_manager.search_templates(
                character_class=character_class,
                season=None  # Show all seasons for now
            )
            
            # Filter by realm
            realm_templates = [t for t in templates if t.get('metadata') and t['metadata'].realm == self.realm]
            
            self.table.setRowCount(len(realm_templates))
            
            for row, template in enumerate(realm_templates):
                # Filename only (Season and Modified Date now shown in preview)
                filename_item = QTableWidgetItem(template['file'])
                self.table.setItem(row, 0, filename_item)
            
            logging.info(f"Liste des templates actualisée : {len(realm_templates)} fichier(s) pour classe {character_class}")
            
        except Exception as e:
            logging.error(f"Erreur lors du rafraîchissement de la liste des templates : {e}")
            QMessageBox.critical(self, lang.get("dialogs.titles.error"), lang.get("armoury_dialog.messages.refresh_error", error=str(e)))
    
    def upload_armor(self):
        """Opens file dialog to upload an armor file."""
        armor_upload_file(self, self.armor_manager, self.season, self.character_name, self.realm)
    
    def import_template(self):
        """Opens new template import dialog."""
        armor_import_template(
            self, self.character_data, self.data_manager, self.template_manager
        )
    
    def _sync_template_prices_with_db(self, metadata_path, metadata):
        """
        Sync template prices with database.
        Wrapper around items_price_sync_template() for backward compatibility.
        
        Args:
            metadata_path: Path to the metadata JSON file
            metadata: Loaded metadata dict
        """
        items_price_sync_template(
            metadata_path=metadata_path,
            metadata=metadata,
            db_manager=self.db_manager,
            realm=self.realm
        )
    
    def parse_zenkcraft_template(self, content, season=""):
        """
        Main parser - detects template format and delegates to specific parser.
        
        Wrapper around template_parse() for backward compatibility.
        
        Supports:
        - Zenkcraft format (default)
        - Loki format (Slot (Item):)
        
        Returns:
            tuple: (formatted_content: str, items_without_price: list)
        """
        from Functions.template_parser import template_parse
        return template_parse(content, self.realm, self.template_manager, self.db_manager)
    
    
    def on_selection_changed(self):
        """Updates the preview when a file is selected."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.preview_area.clear()
            self.preview_area.setPlaceholderText(lang.get("armoury_dialog.preview.no_selection"))
            ui_state_set_armor_buttons(
                self,
                character_selected=False,
                file_selected=False,
                items_without_price=False,
                db_manager=self.db_manager
            )
            return
        
        # Get filename from the first column of selected row
        row = selected_items[0].row()
        filename = self.table.item(row, 0).text()
        
        # Update button states
        ui_state_set_armor_buttons(
            self,
            character_selected=True,
            file_selected=True,
            items_without_price=False,
            db_manager=self.db_manager
        )
        
        try:
            # Get file path using TemplateManager
            template_path = self.template_manager._get_template_path(self.realm, filename)
            
            if not template_path.exists():
                self.preview_area.setPlainText(lang.get("armoury_dialog.preview.file_not_found", filename=filename))
                return
            
            # Read file content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse and format Zenkcraft template
            # Returns tuple: (formatted_content, items_without_price)
            parse_result = self.parse_zenkcraft_template(content, self.season)
            formatted_content, items_without_price = parse_result
            
            # Store items_without_price for search button state
            self.items_without_price = items_without_price
            
            # Convert to HTML with color support
            import re
            
            # Step 1: Replace color markers with HTML spans
            color_pattern = r'%%COLOR_START:(.+?)%%(.*?)%%COLOR_END%%'
            
            def replace_color(match):
                color = match.group(1)
                text = match.group(2)
                return f"<span style='color:{color}'>{text}</span>"
            
            formatted_content = re.sub(color_pattern, replace_color, formatted_content)
            
            # Step 2: Replace spaces OUTSIDE HTML tags (negative lookahead to avoid spaces inside <...>)
            formatted_content = re.sub(r' (?![^<]*>)', '&nbsp;', formatted_content)
            
            # Step 3: Convert newlines to <br>
            html_content = formatted_content.replace('\n', '<br>')
            html_content = f"<div style='line-height: 1.1;'>{html_content}</div>"
            
            # Display formatted content
            self.preview_area.setHtml(html_content)
            
            # Update search button based on items_without_price
            has_items_without_price = bool(self.items_without_price)
            ui_state_set_armor_buttons(
                self,
                character_selected=True,
                file_selected=True,
                items_without_price=has_items_without_price,
                db_manager=self.db_manager
            )
            
            if has_items_without_price:
                button_text = lang.get("armoury_dialog.buttons.search_missing_prices", default="Search Missing Prices")
                self.search_prices_button.setText(f"🔍 {button_text} ({len(self.items_without_price)} items)")
            else:
                button_text = lang.get("armoury_dialog.buttons.search_missing_prices", default="Search Missing Prices")
                self.search_prices_button.setText(f"🔍 {button_text}")
                
        except Exception as e:
            logging.error(f"Erreur lors de la prévisualisation : {e}")
            self.preview_area.setPlainText(lang.get("armoury_dialog.preview.error", error=str(e)))
    
    def _on_model_link_clicked(self, url):
        """Handle click on model viewer link in preview."""
        item_model_on_link_clicked(self, url)
    
    def _show_item_model(self, item_name):
        """Show model image for the specified item."""
        item_model_show(self, item_name)
    
    def open_armor(self, filename):
        """Opens an armor file with the default application."""
        armor_open_file(self, self.template_manager, self.realm, filename)
    
    def delete_armor(self, filename):
        """Deletes an armor file after confirmation."""
        armor_delete_file(self, self.template_manager, self.realm, filename)
    
    def download_selected_armor(self):
        """Downloads the currently selected armor file (called from preview panel button)."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        # Get filename from selected row
        row = selected_items[0].row()
        filename = self.table.item(row, 0).text()
        
        # Call existing download method
        self.download_armor(filename)
    
    def show_context_menu(self, position):
        """Shows context menu for armor files."""
        # Get the selected row
        item = self.table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        filename = self.table.item(row, 0).text()
        
        # Build and show context menu
        from UI.ui_context_menus import ui_show_armor_context_menu
        callbacks = {
            'view': self.view_armor,
            'download': self.download_armor,
            'open': self.open_armor,
            'delete': self.delete_armor,
        }
        ui_show_armor_context_menu(self, self.table, position, filename, callbacks)
    
    def view_armor(self, filename):
        """Opens armor viewer dialog."""
        # Placeholder for future armor viewer implementation
        QMessageBox.information(
            self,
            lang.get("armoury_dialog.messages.view_title"),
            lang.get("armoury_dialog.messages.view_placeholder", filename=filename)
        )
    
    def download_armor(self, filename):
        """Downloads/exports the armor file to a user-selected location."""
        try:
            # Get source file path using TemplateManager
            source_file = self.template_manager._get_template_path(self.realm, filename)
            
            if not source_file.exists():
                QMessageBox.warning(
                    self,
                    lang.get("dialogs.titles.error"),
                    lang.get("armoury_dialog.messages.file_not_found", filename=filename)
                )
                return
            
            # Ask user where to save the file
            save_path = dialog_save_file(
                self,
                title_key="armoury_dialog.dialogs.download_file",
                default_filename=filename,
                filter_key="armoury_dialog.dialogs.all_files"
            )
            
            if save_path:
                import shutil
                shutil.copy2(str(source_file), save_path)
                QMessageBox.information(
                    self,
                    lang.get("dialogs.titles.success"),
                    lang.get("armoury_dialog.messages.download_success", filename=os.path.basename(save_path))
                )
                logging.info(f"Fichier d'armure téléchargé : {save_path}")
        except Exception as e:
            logging.error(f"Erreur lors du téléchargement du fichier d'armure : {e}")
            QMessageBox.critical(self, lang.get("dialogs.titles.error"), lang.get("armoury_dialog.messages.download_error", error=str(e)))
    
    def search_missing_prices(self):
        """Search for missing item prices online using Eden scraper.
        Wrapper around items_price_find_missing() for backward compatibility."""
        if not hasattr(self, 'items_without_price') or not self.items_without_price:
            QMessageBox.information(
                self,
                lang.get("armoury_dialog.search_prices.title", default="Search Prices"),
                lang.get("armoury_dialog.search_prices.no_items", default="No items without price to search.")
            )
            return
        
        # Get selected filename
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                lang.get("armoury_dialog.search_prices.title", default="Search Prices"),
                lang.get("armoury_dialog.search_prices.no_selection", default="Please select an armor file first.")
            )
            return
        
        filename = selected_items[0].text()
        
        # Show search dialog
        from Functions.cookie_manager import CookieManager
        
        dialog = SearchMissingPricesDialog(
            self,
            self.items_without_price,
            self.realm,
            self.template_manager,
            filename,
            CookieManager()
        )
        
        if dialog.exec() == QDialog.Accepted:
            # Refresh preview to show updated prices
            self.on_selection_changed()


class ArmorUploadPreviewDialog(QDialog):
    """Dialog to preview and configure armor file upload before final import."""
    
    def __init__(self, parent, file_path, current_season, available_seasons, realm, character_name):
        super().__init__(parent)
        self.file_path = file_path
        self.current_season = current_season
        self.available_seasons = available_seasons
        self.realm = realm
        self.character_name = character_name
        
        self.setWindowTitle(lang.get("armoury_upload.title"))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(lang.get("armoury_upload.header"))
        title_font = title_label.font()
        title_font.setPointSize(title_font.pointSize() + 2)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addSpacing(10)
        
        # File information group
        file_group = QGroupBox(lang.get("armoury_upload.file_info.title"))
        file_layout = QFormLayout()
        
        # Original filename
        original_filename = os.path.basename(file_path)
        file_layout.addRow(lang.get("armoury_upload.file_info.source"), QLabel(original_filename))
        
        # File size
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        size_text = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{file_size / 1024:.2f} KB"
        file_layout.addRow(lang.get("armoury_upload.file_info.size"), QLabel(size_text))
        
        # File type
        file_ext = os.path.splitext(original_filename)[1]
        file_layout.addRow(lang.get("armoury_upload.file_info.type"), QLabel(file_ext if file_ext else lang.get("armoury_upload.file_info.no_extension")))
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        layout.addSpacing(10)
        
        # Import configuration group
        config_group = QGroupBox(lang.get("armoury_upload.config.title"))
        config_layout = QFormLayout()
        
        # Filename editor
        self.filename_edit = QLineEdit()
        self.filename_edit.setText(original_filename)
        self.filename_edit.setPlaceholderText(lang.get("armoury_upload.config.filename_placeholder"))
        config_layout.addRow(lang.get("armoury_upload.config.filename"), self.filename_edit)
        
        # Season selector
        self.season_combo = QComboBox()
        self.season_combo.addItems(available_seasons)
        
        # Set current season as default
        current_index = self.season_combo.findText(current_season)
        if current_index >= 0:
            self.season_combo.setCurrentIndex(current_index)
        
        season_help = QLabel(lang.get("armoury_upload.config.season_help"))
        season_help.setStyleSheet("color: gray; font-style: italic;")
        
        config_layout.addRow(lang.get("armoury_upload.config.season"), self.season_combo)
        config_layout.addRow("", season_help)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        layout.addSpacing(10)
        
        # Destination preview
        dest_group = QGroupBox(lang.get("armoury_upload.destination.title"))
        dest_layout = QVBoxLayout()
        
        self.dest_label = QLabel()
        self.dest_label.setWordWrap(True)
        # Use semi-transparent background that adapts to theme, with border for visibility
        self.dest_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: rgba(128, 128, 128, 0.15);
                border: 1px solid rgba(128, 128, 128, 0.3);
                border-radius: 5px;
            }
        """)
        self._update_destination_preview()
        dest_layout.addWidget(self.dest_label)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Connect signals to update preview
        self.filename_edit.textChanged.connect(self._update_destination_preview)
        self.season_combo.currentTextChanged.connect(self._update_destination_preview)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton(lang.get("armoury_upload.buttons.cancel"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        import_button = QPushButton(lang.get("armoury_upload.buttons.import"))
        import_button.setDefault(True)
        import_button.clicked.connect(self.accept)
        button_layout.addWidget(import_button)
        
        layout.addLayout(button_layout)
    
    def _update_destination_preview(self):
        """Updates the destination path preview."""
        from Functions.path_manager import get_armory_dir
        
        filename = self.filename_edit.text().strip() or os.path.basename(self.file_path)
        season = self.season_combo.currentText()
        
        dest_dir = get_armory_dir(season, self.realm, self.character_name)
        dest_path = os.path.join(dest_dir, filename)
        
        # Normalize path for display
        dest_path = os.path.normpath(dest_path)
        
        self.dest_label.setText(f"📁 {dest_path}")


class ConnectionTestThread(QThread):
    """Thread to test Eden connection in background"""
    finished = Signal(dict)  # Signal emitted with test result
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Don't store reference to cookie_manager
        # to avoid issues if window is destroyed
    
    def run(self):
        """Execute connection test"""
        # Create local CookieManager instance to avoid references
        # to destroyed objects if window is closed during test
        from Functions.cookie_manager import CookieManager
        cookie_manager = CookieManager()
        result = cookie_manager.test_eden_connection()
        self.finished.emit(result)


class CookieManagerDialog(QDialog):
    """Dialog to manage Eden cookies for scraping"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("cookie_manager.window_title"))
        self.resize(600, 400)
        
        # Importer le gestionnaire de cookies
        from Functions.cookie_manager import CookieManager
        self.cookie_manager = CookieManager()
        
        # Thread pour le test de connexion
        self.connection_thread = None
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Titre et description
        title_label = QLabel(f"<h2>{lang.get('cookie_manager.title')}</h2>")
        title_label.setTextFormat(Qt.RichText)
        layout.addWidget(title_label)
        
        layout.addSpacing(10)
        
        # Zone d'information sur les cookies
        info_group = QGroupBox(lang.get("cookie_manager.info_group_title"))
        info_layout = QVBoxLayout()
        
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setTextFormat(Qt.RichText)
        info_layout.addWidget(self.status_label)
        
        self.expiry_label = QLabel()
        self.expiry_label.setWordWrap(True)
        self.expiry_label.setTextFormat(Qt.RichText)
        info_layout.addWidget(self.expiry_label)
        
        # Label to display browser used
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
        import_group = QGroupBox(lang.get("cookie_manager.import_group_title"))
        import_layout = QHBoxLayout()
        
        import_label = QLabel(lang.get("cookie_manager.file_path_label"))
        import_layout.addWidget(import_label)
        
        self.cookie_path_edit = QLineEdit()
        self.cookie_path_edit.setPlaceholderText(lang.get("cookie_manager.file_path_placeholder"))
        self.cookie_path_edit.returnPressed.connect(self.import_from_path)
        import_layout.addWidget(self.cookie_path_edit)
        
        browse_button = QPushButton(lang.get("buttons.cookie_browse"))
        browse_button.clicked.connect(self.browse_cookie_file)
        import_layout.addWidget(browse_button)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.generate_button = QPushButton(lang.get("buttons.cookie_generate"))
        self.generate_button.setToolTip(lang.get("cookie_manager.generate_tooltip"))
        self.generate_button.clicked.connect(self.generate_cookies)
        buttons_layout.addWidget(self.generate_button)
        
        self.refresh_button = QPushButton(lang.get("buttons.eden_refresh"))
        self.refresh_button.clicked.connect(self.refresh_status)
        buttons_layout.addWidget(self.refresh_button)
        
        self.delete_button = QPushButton(lang.get("buttons.cookie_delete"))
        self.delete_button.clicked.connect(self.delete_cookies)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        
        # Section Chrome Profile Management
        chrome_group = QGroupBox(lang.get("cookie_manager.chrome_profile_section"))
        chrome_layout = QVBoxLayout()
        
        # Affichage taille du profil
        self.chrome_profile_size_label = QLabel()
        self.chrome_profile_size_label.setWordWrap(True)
        chrome_layout.addWidget(self.chrome_profile_size_label)
        
        # Note: Purge button removed - use "Clean Eden" in Herald settings
        
        chrome_group.setLayout(chrome_layout)
        layout.addWidget(chrome_group)
        
        # Bouton de fermeture
        close_button = QPushButton(lang.get("buttons.close"))
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # Display initial state and profile size
        self.refresh_status()
        self.update_chrome_profile_size()
    
    def start_connection_test(self):
        """Start connection test in background"""
        # Cancel ongoing test if existing
        if self.connection_thread and self.connection_thread.isRunning():
            try:
                self.connection_thread.finished.disconnect()
            except Exception:
                pass
            self.connection_thread.quit()
            self.connection_thread.wait()
        
        # Create new thread with main window as parent
        # so it survives closing this dialog window
        main_window = self.parent() if self.parent() else None
        self.connection_thread = ConnectionTestThread(parent=main_window)
        self.connection_thread.finished.connect(self.on_connection_test_finished)
        self.connection_thread.start()
    
    def on_connection_test_finished(self, result):
        """Called when connection test is complete"""
        # Retrieve current info to update display
        info = self.cookie_manager.get_cookie_info()
        if info and info['is_valid']:
            expiry_date = info['expiry_date']
            now = datetime.now()
            duration = expiry_date - now
            days = duration.days
            
            # Construire le statut de connexion
            if result['accessible']:
                connection_status = f"{lang.get('cookie_manager.eden_access')} {lang.get('cookie_manager.eden_connected')}"
            else:
                if result['status_code']:
                    connection_status = f"{lang.get('cookie_manager.eden_access')} <span style='color: red;'>❌ {result['message']}</span>"
                else:
                    connection_status = f"{lang.get('cookie_manager.eden_access')} <span style='color: orange;'>⚠️ {result['message']}</span>"
            
            # Update display
            self.expiry_label.setText(
                f"{lang.get('cookie_manager.expiry_date', date=expiry_date.strftime('%d/%m/%Y à %H:%M'))}<br/>"
                f"{lang.get('cookie_manager.remaining_validity', days=days)}<br/>"
                f"{connection_status}"
            )
            
            # Display browser used for test (if available in result)
            browser_used = result.get('browser_used')
            if browser_used:
                browser_icon = {'Chrome': '🔵', 'Edge': '🔷', 'Firefox': '🦊'}.get(browser_used, '🌐')
                self.browser_label.setText(
                    lang.get('cookie_manager.test_with_browser', icon=browser_icon, browser=browser_used)
                )
            else:
                self.browser_label.setText("")
    
    def refresh_status(self):
        """Update cookie status display"""
        info = self.cookie_manager.get_cookie_info()
        
        if info is None:
            # Aucun cookie
            self.status_label.setText(lang.get("cookie_manager.status_no_cookies"))
            self.status_label.setStyleSheet("color: red;")
            self.expiry_label.setText("")
            self.details_label.setText(
                lang.get("cookie_manager.details_need_import")
            )
            ui_state_on_selection_changed(self, selection_count=0, is_valid=False, enable_delete=False)
            
        elif info.get('error'):
            # Erreur de lecture
            self.status_label.setText(lang.get("cookie_manager.status_read_error"))
            self.status_label.setStyleSheet("color: orange;")
            self.expiry_label.setText("")
            self.details_label.setText(f"Erreur: {info['error']}")
            ui_state_on_selection_changed(self, selection_count=1, is_valid=True, enable_delete=True)
            
        elif not info['is_valid']:
            # Expired cookies
            self.status_label.setText(lang.get("cookie_manager.status_expired"))
            self.status_label.setStyleSheet("color: orange;")
            self.expiry_label.setText("")
            
            details = lang.get("cookie_manager.total_cookies", count=info['total_cookies']) + "<br/>"
            details += lang.get("cookie_manager.expired_cookies", count=info['expired_cookies']) + "<br/>"
            details += lang.get("cookie_manager.valid_cookies", count=info['valid_cookies']) + "<br/>"
            details += lang.get("cookie_manager.details_need_new")
            
            self.details_label.setText(details)
            ui_state_on_selection_changed(self, selection_count=1, is_valid=True, enable_delete=True)
            
        else:
            # Cookies valides
            self.status_label.setText(lang.get("cookie_manager.status_valid"))
            self.status_label.setStyleSheet("color: green;")
            
            expiry_date = info['expiry_date']
            now = datetime.now()
            duration = expiry_date - now
            days = duration.days
            
            self.expiry_label.setText(
                f"{lang.get('cookie_manager.expiry_date', date=expiry_date.strftime('%d/%m/%Y à %H:%M'))}<br/>"
                f"{lang.get('cookie_manager.remaining_validity', days=days)}"
            )
            
            if days < 7:
                self.expiry_label.setStyleSheet("color: orange;")
            else:
                self.expiry_label.setStyleSheet("color: green;")
            
            # Display base info immediately
            self.expiry_label.setText(
                f"{lang.get('cookie_manager.expiry_date', date=expiry_date.strftime('%d/%m/%Y à %H:%M'))}<br/>"
                f"{lang.get('cookie_manager.remaining_validity', days=days)}<br/>"
                f"{lang.get('cookie_manager.eden_access')} {lang.get('cookie_manager.eden_testing')}"
            )
            
            # Launch connection test in background
            self.start_connection_test()
            
            details = lang.get("cookie_manager.total_cookies_display", count=info['total_cookies']) + "<br/>"
            details += lang.get("cookie_manager.valid_cookies_display", count=info['valid_cookies']) + "<br/>"
            
            if info['session_cookies'] > 0:
                details += lang.get("cookie_manager.session_cookies", count=info['session_cookies']) + "<br/>"
            
            details += lang.get("cookie_manager.file_location", path=info['file_path'])
            
            self.details_label.setText(details)
            ui_state_on_selection_changed(self, selection_count=1, is_valid=True, enable_delete=True)
        
        # Reset browser label (will be updated after test/generation)
        if not (info and info.get('is_valid')):
            self.browser_label.setText("")
    
    def browse_cookie_file(self):
        """Open dialog to select a cookie file"""
        file_path = dialog_open_file(
            self,
            title_key="cookie_manager.browse_dialog_title",
            filter_key="cookie_manager.browse_dialog_filter"
        )
        
        if file_path:
            self.cookie_path_edit.setText(file_path)
            # Auto-import after selection
            self.import_from_path()
    
    def import_from_path(self):
        """Importe un fichier de cookies depuis le chemin saisi"""
        file_path = self.cookie_path_edit.text().strip()
        
        if not file_path:
            QMessageBox.warning(
                self,
                lang.get("cookie_manager.import_warning_title"),
                lang.get("cookie_manager.import_warning_message")
            )
            return
        
        # Check that the File existe before d'essayer d'importer
        import os
        
        if not os.path.exists(file_path):
            QMessageBox.critical(
                self,
                lang.get("cookie_manager.import_error_not_exists_title"),
                lang.get("cookie_manager.import_error_not_exists_message", path=file_path)
            )
            return
        
        success = self.cookie_manager.import_cookie_file(file_path)
        
        if success:
            QMessageBox.information(
                self,
                lang.get("cookie_manager.import_success_title"),
                lang.get("cookie_manager.import_success_message")
            )
            self.cookie_path_edit.clear()
            self.refresh_status()
            
            # Refresh Eden status in main window
            if self.parent() and hasattr(self.parent(), 'ui_manager'):
                self.parent().ui_manager.check_eden_status()
        else:
            QMessageBox.critical(
                self,
                lang.get("cookie_manager.import_error_title"),
                lang.get("cookie_manager.import_error_message", path=file_path)
            )
    
    def delete_cookies(self):
        """Delete cookies after confirmation"""
        reply = QMessageBox.question(
            self,
            lang.get("cookie_manager.delete_confirm_title"),
            lang.get("cookie_manager.delete_confirm_message"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.cookie_manager.delete_cookies()
            
            if success:
                QMessageBox.information(
                    self,
                    lang.get("cookie_manager.delete_success_title"),
                    lang.get("cookie_manager.delete_success_message")
                )
                self.refresh_status()
                
                # Refresh Eden status in main window
                if self.parent() and hasattr(self.parent(), 'ui_manager'):
                    self.parent().ui_manager.check_eden_status()
            else:
                QMessageBox.critical(
                    self,
                    lang.get("cookie_manager.delete_error_title"),
                    lang.get("cookie_manager.delete_error_message")
                )
    
    def update_chrome_profile_size(self):
        """Update Chrome profile size display"""
        size_bytes = self.cookie_manager.get_chrome_profile_size()
        
        if size_bytes == 0:
            size_text = lang.get("cookie_manager.chrome_profile_size_empty")
        elif size_bytes < 1024:
            size_text = lang.get("cookie_manager.chrome_profile_size", size=f"{size_bytes} B")
        elif size_bytes < 1024 * 1024:
            size_kb = size_bytes / 1024
            size_text = lang.get("cookie_manager.chrome_profile_size", size=f"{size_kb:.1f} KB")
        else:
            size_mb = size_bytes / (1024 * 1024)
            size_text = lang.get("cookie_manager.chrome_profile_size", size=f"{size_mb:.1f} MB")
        
        self.chrome_profile_size_label.setText(size_text)
    
    def generate_cookies(self):
        """Generate new cookies via browser authentication (MIGRATED VERSION)"""
        
        # Read configuration
        from Functions.config_manager import config
        preferred_browser = config.get('system.preferred_browser', 'Chrome')
        allow_download = config.get('system.allow_browser_download', False)
        
        # Import components
        from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
        
        # Build steps (NO Herald connection - cookie generation)
        steps = StepConfiguration.build_steps(
            StepConfiguration.COOKIE_GENERATION  # 6 steps
        )
        
        # Create progress dialog
        self.progress_dialog = ProgressStepsDialog(
            parent=self,
            title=lang.get("progress_cookie_gen_title", default="🍪 Génération des cookies..."),
            steps=steps,
            description=lang.get("progress_cookie_gen_desc", default="Ouverture du navigateur pour authentification Discord"),
            show_progress_bar=True,
            determinate_progress=True,
            allow_cancel=True  # Permet annulation
        )
        
        # Create thread
        self.cookie_gen_thread = CookieGenThread(preferred_browser, allow_download)
        
        # ✅ Pattern 1: Connect via wrappers thread-safe
        self.cookie_gen_thread.step_started.connect(self._on_cookie_step_started)
        self.cookie_gen_thread.step_completed.connect(self._on_cookie_step_completed)
        self.cookie_gen_thread.step_error.connect(self._on_cookie_step_error)
        self.cookie_gen_thread.generation_finished.connect(self._on_cookie_generation_finished)
        self.cookie_gen_thread.user_action_required.connect(self._on_cookie_user_action_required)
        
        # ✅ Pattern 4: Connect rejected signal
        self.progress_dialog.rejected.connect(self._on_cookie_progress_dialog_closed)
        
        # Disable buttons during generation
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
        """Interactive dialog to confirm user connection (Step 2)"""
        from PySide6.QtWidgets import QMessageBox
        
        # Create confirmation dialog
        wait_msg = QMessageBox(self)
        wait_msg.setIcon(QMessageBox.Information)
        wait_msg.setWindowTitle(lang.get("cookie_manager.user_action_title"))
        wait_msg.setTextFormat(Qt.RichText)
        wait_msg.setText(lang.get("cookie_manager.user_action_header"))
        wait_msg.setInformativeText(message)
        wait_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        result = wait_msg.exec()
        
        # Inform thread of user decision
        if result == QMessageBox.Ok:
            self.cookie_gen_thread.set_user_confirmation(True)
        else:
            # Annulation
            self.cookie_gen_thread.set_user_confirmation(False)
            self._stop_cookie_gen_thread()
    
    def _on_cookie_progress_dialog_closed(self):
        """✅ Pattern 4: Clean stop when dialog closed by user"""
        import logging
        logging.info("Dialogue cookie gen fermé par utilisateur - Arrêt génération")
        self._stop_cookie_gen_thread()
    
    def _stop_cookie_gen_thread(self):
        """✅ Pattern 2+3: Clean thread stop with cleanup BEFORE terminate"""
        if hasattr(self, 'cookie_gen_thread') and self.cookie_gen_thread:
            if self.cookie_gen_thread.isRunning():
                # ✅ Pattern 3: Request graceful stop
                self.cookie_gen_thread.request_stop()
                
                # Disconnect signals
                try:
                    self.cookie_gen_thread.step_started.disconnect()
                    self.cookie_gen_thread.step_completed.disconnect()
                    self.cookie_gen_thread.step_error.disconnect()
                    self.cookie_gen_thread.generation_finished.disconnect()
                    self.cookie_gen_thread.user_action_required.disconnect()
                except Exception:
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
            except Exception:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                delattr(self, 'progress_dialog')
        
        # Re-enable buttons
        self.generate_button.setEnabled(True)
        self.cookie_path_edit.setEnabled(True)
    
    def _on_cookie_generation_finished(self, success, message, cookie_count):
        """Callback called when generation is complete"""
        from PySide6.QtCore import QTimer
        
        # Display success/error in dialog
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
                # Dialog already deleted
                self._process_cookie_result(success, message, cookie_count)
        else:
            self._process_cookie_result(success, message, cookie_count)
    
    def _process_cookie_result(self, success, message, cookie_count):
        """Process generation result after displaying status"""
        # Close and cleanup
        self._stop_cookie_gen_thread()
        
        # Display final result
        if success:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                lang.get("cookie_manager.import_success_title"),
                f"{lang.get('cookie_manager.import_success_message')}\n\n{message}"
            )
        elif message and "Annulé" not in message:
            # Display error only if not cancelled
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                lang.get("cookie_manager.import_error_title"),
                f"{lang.get('cookie_manager.import_error_title')} :\n\n{message}"
            )
        
        # Actualiser le statut
        self.refresh_status()
        
        # Refresh Eden status in main window if cookies generated
        if success and self.parent() and hasattr(self.parent(), 'ui_manager'):
            self.parent().ui_manager.check_eden_status()
    
    def closeEvent(self, event):
        """
        Gère la fermeture de la fenêtre.
        Le thread continue en arrière-plan (avec parent=main_window) jusqu'à sa fin naturelle.
        """
        # If connection test thread is running, disconnect our callback
        # Thread will continue with its parent (main_window) and terminate cleanly
        if self.connection_thread and self.connection_thread.isRunning():
            try:
                self.connection_thread.finished.disconnect(self.on_connection_test_finished)
            except Exception:
                pass
            # No longer keep reference to thread
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
        
        # ✅ Pattern 3: Interruption flag
        self._stop_requested = False
        
        # ✅ Pattern 2: External resource reference (Selenium driver)
        self._driver = None
        
        # Variable to store if user confirmed connection
        self._user_confirmed = False
    
    def request_stop(self):
        """✅ Pattern 3: Request graceful stop"""
        self._stop_requested = True
    
    def cleanup_external_resources(self):
        """✅ Pattern 2: Forced driver cleanup (called from main thread)"""
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
        """Called from main thread when user confirms/cancels"""
        self._user_confirmed = confirmed
    
    def run(self):
        """Execute cookie generation with thread safety"""
        import logging
        import time
        logger = logging.getLogger(__name__)
        
        from Functions.cookie_manager import CookieManager
        
        cookie_manager = CookieManager()
        driver = None
        
        # Variables for result (emitted AFTER all steps)
        result_success = False
        result_message = ""
        result_count = 0
        
        try:
            # Step 0: Browser configuration
            self.step_started.emit(0)
            logger.info(f"Configuration navigateur: {self.preferred_browser}, download={self.allow_download}")
            time.sleep(0.5)  # Simuler configuration
            self.step_completed.emit(0)
            
            if self._stop_requested:
                return
            
            # Step 1: Opening login page
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
            
            # Step 2: Waiting for user connection (INTERACTIVE)
            self.step_started.emit(2)
            logger.info("Attente connexion utilisateur...")
            
            # Emit signal to request user confirmation
            self.user_action_required.emit(
                browser_name,
                lang.get("cookie_manager.browser_opened_message", browser=browser_name)
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
            
            # Step 3: Cookie extraction
            self.step_started.emit(3)
            logger.info("Extraction des cookies depuis le navigateur...")
            
            # Cookies are already in driver, move to save step
            time.sleep(0.5)  # Small delay to let cookies stabilize
            
            logger.info("Cookies extraits")
            self.step_completed.emit(3)
            
            if self._stop_requested:
                return
            
            # Step 4: Cookie saving
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
            
            # Step 5: Validation and verification
            self.step_started.emit(5)
            logger.info("Validation des cookies...")
            
            # Verify that cookies are valid
            info = cookie_manager.get_cookie_info()
            if info and info.get('is_valid'):
                logger.info("Cookies validés avec succès")
                self.step_completed.emit(5)
                
                # Store success
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
            # Browser closing (no dedicated step in COOKIE_GENERATION)
            if driver:
                try:
                    logger.info("Fermeture navigateur cookies...")
                    driver.quit()
                    logger.info("Navigateur fermé")
                except Exception as e:
                    logger.warning(f"Erreur fermeture navigateur: {e}")
            
            # Emit final signal
            logger.info(f"Émission signal generation_finished - success={result_success}, count={result_count}")
            self.generation_finished.emit(result_success, result_message, result_count)


# ============================================================================
# HERALD SEARCH DIALOG
# ============================================================================

class SearchThread(QThread):
    """Thread to perform Herald search in background"""
    search_finished = Signal(bool, str, str)  # (success, message, json_path)
    progress_update = Signal(str)  # (status_message) - LEGACY for compatibility
    step_started = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_completed = Signal(int)  # (step_index) - NOUVEAU pour ProgressStepsDialog
    step_error = Signal(int, str)  # (step_index, error_message) - NOUVEAU pour ProgressStepsDialog
    
    def __init__(self, character_name, realm_filter="", lang=None):
        super().__init__()
        self.character_name = character_name
        self.realm_filter = realm_filter
        self.lang = lang
        self._stop_requested = False  # Flag for graceful stop
        self._scraper = None  # Reference to scraper for external cleanup
    
    def request_stop(self):
        """Request thread stop (called from main thread)"""
        self._stop_requested = True
    
    def cleanup_driver(self):
        """Close browser safely (called from main thread)"""
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
        """Emit step start signals (new + legacy)"""
        self.step_started.emit(step_index)
        self.progress_update.emit(message)  # Keep compatibility
    
    def _emit_step_complete(self, step_index):
        """Emit step complete signal"""
        self.step_completed.emit(step_index)
    
    def run(self):
        """Execute search with progress updates"""
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
        
        # Variables for result (signal emitted AFTER Step 8 in finally)
        result_success = False
        result_message = ""
        result_json_path = ""
        
        try:
            # Step 0: Cookie verification
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
            
            # Step 1: Browser initialization
            self._emit_step_start(1, "🌐 Initialisation du navigateur Chrome...")
            scraper = EdenScraper(cookie_manager)
            self._scraper = scraper  # Store reference for external cleanup
            
            if not scraper.initialize_driver(headless=False):
                module_logger.error("Impossible d'initialiser le navigateur", extra={"action": "SEARCH"})
                self.step_error.emit(1, "Impossible d'initialiser le navigateur")
                result_message = "Impossible d'initialiser le navigateur Chrome."
                return
            
            module_logger.info("Navigateur initialisé avec succès", extra={"action": "SEARCH"})
            self._emit_step_complete(1)
            
            # Step 2: Loading cookies
            self._emit_step_start(2, "🍪 Chargement des cookies dans le navigateur...")
            if not scraper.load_cookies():
                module_logger.error("Impossible de charger les cookies dans le navigateur", extra={"action": "SEARCH"})
                self.step_error.emit(2, "Impossible de charger les cookies")
                result_message = "Impossible de charger les cookies."
                return
            
            module_logger.info("Cookies chargés dans le navigateur - Authentification complétée", extra={"action": "SEARCH"})
            self._emit_step_complete(2)
            
            # Check if stop requested
            if self._stop_requested:
                module_logger.info("Arrêt demandé par l'utilisateur (après étape 2)", extra={"action": "SEARCH"})
                return
            
            # Step 3: Navigation to search page
            if self.realm_filter:
                search_url = f"https://eden-daoc.net/herald?n=search&r={self.realm_filter}&s={self.character_name}"
            else:
                search_url = f"https://eden-daoc.net/herald?n=search&s={self.character_name}"
            
            self._emit_step_start(3, f"🔍 Recherche de '{self.character_name}' sur Eden Herald...")
            module_logger.info(f"Recherche Herald: {search_url}", extra={"action": "SEARCH"})
            
            scraper.driver.get(search_url)
            self._emit_step_complete(3)
            
            # Check if stop requested
            if self._stop_requested:
                module_logger.info("Arrêt demandé par l'utilisateur (après étape 3)", extra={"action": "SEARCH"})
                return
            
            # Step 4: Wait for page loading
            self._emit_step_start(4, "⏳ Chargement de la page de recherche...")
            module_logger.info("Attente du chargement de la page de recherche (5 secondes)...", extra={"action": "SEARCH"})
            
            # Interruptible sleep (check flag every 0.5 seconds)
            for i in range(10):  # 10 x 0.5s = 5s
                if self._stop_requested:
                    module_logger.info("Arrêt demandé par l'utilisateur (pendant sleep)", extra={"action": "SEARCH"})
                    return
                time.sleep(0.5)
            
            self._emit_step_complete(4)
            
            # Check if stop requested
            if self._stop_requested:
                module_logger.info("Arrêt demandé par l'utilisateur (après étape 4)", extra={"action": "SEARCH"})
                return
            
            # Step 5: Data extraction
            self._emit_step_start(5, "📊Sentence Extraction des résultats de recherche...")
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
                if len(rows) > 1:  # At least header and one line
                    headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
                    
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if cells:
                            result = {}
                            for idx, cell in enumerate(cells):
                                header = headers[idx] if idx < len(headers) else f"col_{idx}"
                                result[header] = cell.get_text(strip=True)
                                
                                # Extract links
                                links = cell.find_all('a')
                                if links:
                                    result[f"{header}_links"] = [a.get('href', '') for a in links]
                            
                            if result:
                                search_data['results'].append(result)
            
            self._emit_step_complete(5)
            
            # Step 6: Saving results
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
            
            # Step 7: Character formatting
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
                        # Fallback: build URL from name if no link found
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
            
            # Add formatted list to JSON
            search_data['characters'] = characters
            search_data['search_query'] = self.character_name
            
            # Re-save with formatted data
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, indent=2, ensure_ascii=False)
            
            module_logger.info(f"{len(characters)} personnage(s) trouvé(s) et sauvegardé(s) dans: {json_path}", extra={"action": "SEARCH"})
            self._emit_step_complete(7)
            
            # No step 8 here (browser closing) - will be in finally
            
            # Store success (signal emitted AFTER Step 8 in finally)
            result_success = True
            if self.lang:
                result_message = self.lang.get("herald_search.search_complete", count=len(characters), default=f"{len(characters)} personnage(s) trouvé(s)")
            else:
                result_message = f"{len(characters)} personnage(s) trouvé(s)"
            result_json_path = str(json_path)
            
        except Exception as e:
            module_logger.error(f"Erreur lors de la recherche: {str(e)}", extra={"action": "SEARCH"}, exc_info=True)
            result_message = f"Erreur: {str(e)}"
            
        finally:
            # Step 8: Close browser cleanly
            if scraper and scraper.driver:
                try:
                    self._emit_step_start(8, "🔄 Fermeture du navigateur...")
                    scraper.driver.quit()
                    module_logger.info("Navigateur fermé", extra={"action": "SEARCH"})
                    self._emit_step_complete(8)
                except Exception as e:
                    module_logger.warning(f"Erreur lors de la fermeture du navigateur: {e}", extra={"action": "SEARCH"})
                    self.step_error.emit(8, f"Erreur fermeture: {str(e)}")
            
            # Emit signal AFTER Step 8 (complete closing)
            module_logger.info(f"Émission signal search_finished - success={result_success}, message={result_message}")
            self.search_finished.emit(result_success, result_message, result_json_path)


# ============================================================================
# STATS UPDATE THREAD (RvR/PvP/PvE/Wealth/Achievements)
# ============================================================================

class StatsUpdateThread(QThread):
    """Thread to update statistics from Herald"""
    
    # Signals
    stats_updated = Signal(dict)  # (results_dict) - Emitted when update completed successfully
    update_failed = Signal(str)  # (error_message) - Emitted in case of complete failure
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
        from Functions.language_manager import lang
        self.lang = lang
        
        self.setWindowTitle(lang.get("herald_search.window_title"))
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
        title_label = QLabel(f"<h2>{self.lang.get('herald_search.title_label')}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.lang.get("herald_search.description"))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: gray; padding: 10px;")
        layout.addWidget(desc_label)
        
        # Groupe de recherche
        search_group = QGroupBox(self.lang.get("herald_search.search_group_title"))
        search_layout = QVBoxLayout()
        
        # Ligne 1 : Champ de saisie du nom
        input_layout = QHBoxLayout()
        input_label = QLabel(self.lang.get("herald_search.name_label"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.lang.get("herald_search.name_placeholder"))
        self.name_input.returnPressed.connect(self.start_search)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.name_input)
        search_layout.addLayout(input_layout)
        
        # Ligne 2 : Sélection of the royaume
        realm_layout = QHBoxLayout()
        realm_label = QLabel(self.lang.get("herald_search.realm_label"))
        self.realm_combo = QComboBox()
        self.realm_combo.addItem(self.lang.get("herald_search.realm_all"), "")  # Par défaut
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
        self.realm_combo.setToolTip(self.lang.get("herald_search.realm_tooltip"))
        realm_layout.addWidget(realm_label)
        realm_layout.addWidget(self.realm_combo)
        realm_layout.addStretch()
        search_layout.addLayout(realm_layout)
        
        # Statut
        self.status_label = QLabel(self.lang.get("herald_search.status_ready"))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        search_layout.addWidget(self.status_label)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Zone of Results
        results_group = QGroupBox(self.lang.get("herald_search.results_group_title"))
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
        columns = [
            self.lang.get("herald_search.column_check"),
            self.lang.get("herald_search.column_realm"),
            self.lang.get("herald_search.column_name"),
            self.lang.get("herald_search.column_class"),
            self.lang.get("herald_search.column_race"),
            self.lang.get("herald_search.column_guild"),
            self.lang.get("herald_search.column_level"),
            self.lang.get("herald_search.column_rp"),
            self.lang.get("herald_search.column_realm_rank")
        ]
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
        
        self.search_button = QPushButton(self.lang.get("herald_search.search_button"))
        self.search_button.clicked.connect(self.start_search)
        self.search_button.setDefault(True)
        button_layout.addWidget(self.search_button)
        
        button_layout.addStretch()
        
        # Boutons d'import
        self.import_selected_button = QPushButton(self.lang.get("herald_search.import_selected_button"))
        self.import_selected_button.clicked.connect(self.import_selected_characters)
        self.import_selected_button.setEnabled(False)
        self.import_selected_button.setToolTip(self.lang.get("herald_search.import_selected_tooltip"))
        button_layout.addWidget(self.import_selected_button)
        
        self.import_all_button = QPushButton(self.lang.get("herald_search.import_all_button"))
        self.import_all_button.clicked.connect(self.import_all_characters)
        self.import_all_button.setEnabled(False)
        self.import_all_button.setToolTip(self.lang.get("herald_search.import_all_tooltip"))
        button_layout.addWidget(self.import_all_button)
        
        close_button = QPushButton(self.lang.get("herald_search.close_button"))
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
        # Cleanup asynchrone pour éviter la latence à la fermeture
        QTimer.singleShot(0, self._async_full_cleanup)
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
                except Exception:
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
            except Exception:
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
                except Exception:
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
                                except Exception:
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
            except Exception:
                pass
            
            # Supprimer l'attribut seulement s'il existe encore
            if hasattr(self, 'progress_dialog'):
                try:
                    delattr(self, 'progress_dialog')
                except Exception:
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
                self.lang.get("herald_search.name_required_title"),
                self.lang.get("herald_search.name_required_message")
            )
            return
        
        # Check the minimum of 3 caractères
        if len(character_name) < 3:
            QMessageBox.warning(
                self,
                self.lang.get("herald_search.name_too_short_title"),
                self.lang.get("herald_search.name_too_short_message")
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
            title = self.lang.get("herald_search.search_title_realm", name=character_name, realm=realm_text, default=f"🔍 Recherche de '{character_name}' dans {realm_text}...")
            description = self.lang.get("herald_search.search_description_realm", realm=realm_text, default=f"Connexion à Eden Herald et recherche de personnages dans le royaume {realm_text}")
        else:
            title = self.lang.get("herald_search.search_title_all", name=character_name, default=f"🔍 Recherche de '{character_name}' sur Eden Herald...")
            description = self.lang.get("herald_search.search_description_all", default="Connexion à Eden Herald et recherche de personnages dans tous les royaumes")
        
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
        
        # Lancer le thread avec le filtre de royaume et l'objet lang
        self.search_thread = SearchThread(character_name, realm_filter, self.lang)
        
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
        except Exception:
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
                QTimer.singleShot(2000, self.progress_dialog.close)
        
        # Réactiver the contrôles
        self.search_button.setEnabled(True)
        self.name_input.setEnabled(True)
        self.realm_combo.setEnabled(True)
        
        if success and json_path:
            # Load and afficher the Results
            try:
                import json
                from pathlib import Path
                
                # Vérifier que le fichier existe
                if not Path(json_path).exists():
                    raise FileNotFoundError(f"Le fichier de résultats n'existe pas: {json_path}")
                
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
                    self.status_label.setText(self.lang.get("herald_search.status_found", count=count, query=search_query))
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
                    self.status_label.setText(self.lang.get("herald_search.status_no_results", query=data['search_query']))
                    self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: orange;")
                    
            except Exception as e:
                self.current_characters = []
                self.import_all_button.setEnabled(False)
                self.import_selected_button.setEnabled(False)
                self.status_label.setText(self.lang.get("herald_search.status_read_error", error=str(e)))
                self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: red;")
        else:
            self.current_characters = []
            self.import_all_button.setEnabled(False)
            self.import_selected_button.setEnabled(False)
            self.status_label.setText(self.lang.get("herald_search.status_search_error", message=message))
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
        import_action = context_menu.addAction(self.lang.get("herald_search.context_menu_import"))
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
            self.lang.get("herald_search.confirm_import_single_title"),
            self.lang.get("herald_search.confirm_import_single_message", name=char_name),
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
                self.lang.get("herald_search.no_selection_title"),
                self.lang.get("herald_search.no_selection_message")
            )
            return
        
        # Confirmer l'import
        count = len(selected_chars)
        reply = QMessageBox.question(
            self,
            self.lang.get("herald_search.confirm_import_selected_title"),
            self.lang.get("herald_search.confirm_import_selected_message", count=count),
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
            self.lang.get("herald_search.confirm_import_all_title"),
            self.lang.get("herald_search.confirm_import_all_message", count=count),
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
                default_season = config.get('game.default_season', 'S3')
                
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
                    char_season = existing_char.get('season', 'S3')
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
            
            QMessageBox.information(self, lang.get("messages.info.herald_import_complete_title"), message)
            
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
            QMessageBox.warning(self, lang.get("messages.info.herald_import_complete_title"), error_msg)


class CharacterUpdateDialog(QDialog):
    """Dialogue pour valider les mises à jour d'un personnage depuis Herald."""
    
    def __init__(self, parent, current_data, new_data, character_name):
        super().__init__(parent)
        self.current_data = current_data
        self.new_data = new_data
        self.character_name = character_name
        self.changes = {}
        
        self.setWindowTitle(lang.get("dialogs.character_update.title", default="Mise à jour - {name}").format(name=character_name))
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # En-tête
        header_label = QLabel(f"<h2>{lang.get('dialogs.character_update.header', default='Mise à jour du personnage: {name}').format(name=character_name)}</h2>")
        layout.addWidget(header_label)
        
        info_label = QLabel(
            lang.get(
                "dialogs.character_update.comparison_info",
                default="<b>Comparaison des données :</b><br>"
                        "• <span style='color: green;'>✓</span> = Valeurs identiques (pas de changement)<br>"
                        "• <span style='color: red;'>Valeur actuelle</span> → <span style='color: green;'><b>Nouvelle valeur</b></span> = Changement détecté<br>"
                        "Cochez les modifications que vous souhaitez appliquer."
            )
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Tableau des modifications
        self.changes_table = QTableWidget()
        self.changes_table.setColumnCount(4)
        self.changes_table.setHorizontalHeaderLabels([
            lang.get("dialogs.character_update.apply_column", default="Appliquer"),
            lang.get("dialogs.character_update.field_column", default="Champ"),
            lang.get("dialogs.character_update.current_column", default="Valeur actuelle"),
            lang.get("dialogs.character_update.new_column", default="Nouvelle valeur")
        ])
        self.changes_table.horizontalHeader().setStretchLastSection(True)
        self.changes_table.setSelectionMode(QTableWidget.NoSelection)
        
        # Détecter the changements
        self._detect_changes()
        
        layout.addWidget(self.changes_table)
        
        # Boutons of sélection
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton(lang.get("dialogs.character_update.select_all", default="Tout sélectionner"))
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton(lang.get("dialogs.character_update.deselect_all", default="Tout désélectionner"))
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
        ok_button.setText(lang.get("dialogs.character_update.apply_changes", default="Appliquer les modifications"))
        
        layout.addWidget(button_box)
    
    def _detect_changes(self):
        """Détecte les changements entre les données actuelles et nouvelles."""
        # Champs à comparer (all the champs importants)
        fields_to_check = {
            'level': lang.get('dialogs.character_update.field_level', default='Niveau'),
            'class': lang.get('dialogs.character_update.field_class', default='Classe'),
            'race': lang.get('dialogs.character_update.field_race', default='Race'),
            'realm': lang.get('dialogs.character_update.field_realm', default='Royaume'),
            'guild': lang.get('dialogs.character_update.field_guild', default='Guilde'),
            'realm_points': lang.get('dialogs.character_update.field_realm_points', default='Points de Royaume'),
            'realm_rank': lang.get('dialogs.character_update.field_realm_rank', default='Rang de Royaume'),
            'server': lang.get('dialogs.character_update.field_server', default='Serveur')
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
                    except Exception:
                        pass
                if isinstance(current_value, str):
                    current_value = current_value.replace(' ', '').replace(',', '')
                    try:
                        current_value = int(current_value)
                    except Exception:
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
            
            empty_text = lang.get('dialogs.character_update.empty_value', default='(vide)')
            all_rows.append({
                'field': field,
                'label': label,
                'current': current_value_str or empty_text,
                'new': new_value_str or empty_text,
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
        return ui_get_selected_changes(self.changes_table)
    
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
            except Exception:
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
            except Exception:
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
        selected_dir = dialog_select_backup_path(self, current_path)
        if selected_dir:
            self.path_edit.setText(selected_dir)
            self.path_edit.setCursorPosition(0)
    
    def browse_cookies_backup_path(self):
        """Open directory selection dialog for cookies backup path."""
        current_path = self.cookies_path_edit.text()
        selected_dir = dialog_select_backup_path(self, current_path)
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
            except Exception:
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
            except Exception:
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


class SearchMissingPricesDialog(QDialog):
    """Dialog to search for missing item prices online."""
    
    def __init__(self, parent, items_without_price, realm, template_manager, filename, cookie_manager):
        super().__init__(parent)
        self.items_without_price = items_without_price
        self.realm = realm
        self.template_manager = template_manager
        self.filename = filename
        self.cookie_manager = cookie_manager
        self.active_scraper = None  # Track active scraper for cleanup
        
        self.setWindowTitle(lang.get("search_prices_dialog.title", default="Search Missing Prices"))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_text = lang.get(
            "search_prices_dialog.info",
            default=f"Found {len(items_without_price)} item(s) without price in database.\nClick 'Search All' to search online or select individual items."
        )
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Items list
        self.items_list = QListWidget()
        self.items_list.addItems(items_without_price)
        self.items_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.items_list)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton(lang.get("search_prices_dialog.select_all", default="Select All"))
        self.select_all_button.clicked.connect(self.select_all_items)
        button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton(lang.get("search_prices_dialog.deselect_all", default="Deselect All"))
        self.deselect_all_button.clicked.connect(self.deselect_all_items)
        button_layout.addWidget(self.deselect_all_button)
        
        button_layout.addStretch()
        
        self.search_button = QPushButton(lang.get("search_prices_dialog.search_selected", default="Search Selected"))
        self.search_button.clicked.connect(self.search_selected_items)
        button_layout.addWidget(self.search_button)
        
        self.close_button = QPushButton(lang.get("search_prices_dialog.close", default="Close"))
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def select_all_items(self):
        """Select all items in the list."""
        for i in range(self.items_list.count()):
            self.items_list.item(i).setSelected(True)
    
    def deselect_all_items(self):
        """Deselect all items in the list."""
        self.items_list.clearSelection()
    
    def _update_template_price(self, item_name, price):
        """Update item price directly in template metadata JSON file.
        
        Args:
            item_name: Name of the item to update
            price: Price string to set (e.g., "1g 50s 25c")
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import json
            
            # Get metadata JSON path (not the template text file)
            metadata_path = self.template_manager._get_metadata_path(self.realm, self.filename)
            
            # Load or create metadata
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                # Create new metadata structure
                metadata = {
                    "template_name": self.filename,
                    "realm": self.realm,
                    "prices": {}
                }
            
            # Ensure prices dict exists
            if 'prices' not in metadata:
                metadata['prices'] = {}
            
            # Update price
            metadata['prices'][item_name] = price
            
            # Create directory if needed
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Updated {item_name} price to {price} in metadata: {metadata_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating template price: {e}", exc_info=True)
            return False
    
    def search_selected_items(self):
        """Search for prices of selected items."""
        selected_items = [item.text() for item in self.items_list.selectedItems()]
        
        if not selected_items:
            QMessageBox.warning(
                self,
                lang.get("search_prices_dialog.no_selection_title", default="No Selection"),
                lang.get("search_prices_dialog.no_selection_message", default="Please select items to search.")
            )
            return
        
        # Confirm action
        reply = QMessageBox.question(
            self,
            lang.get("search_prices_dialog.confirm_title", default="Confirm Search"),
            lang.get("search_prices_dialog.confirm_message", default=f"Search online for {len(selected_items)} item(s)?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Disable buttons during search
        self.search_button.setEnabled(False)
        self.select_all_button.setEnabled(False)
        self.deselect_all_button.setEnabled(False)
        self.close_button.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(selected_items))
        self.progress_bar.setValue(0)
        
        # Perform search
        eden_scraper = None  # Track scraper for cleanup
        try:
            self.status_label.setText(lang.get("search_prices_dialog.status_connecting", default="Connecting to Eden Herald..."))
            QApplication.processEvents()
            
            # Initialize scraper using centralized connection function (like CharacterProfileScraper.connect())
            from Functions.cookie_manager import CookieManager
            from Functions.eden_scraper import _connect_to_eden_herald
            from Functions.items_scraper import ItemsScraper
            
            cookie_manager = CookieManager()
            
            # Use centralized connection function that handles everything
            eden_scraper, error_message = _connect_to_eden_herald(
                cookie_manager=cookie_manager,
                headless=False  # Visible browser
            )
            
            # Store in instance variable for cleanup on dialog close
            self.active_scraper = eden_scraper
            
            if not eden_scraper:
                QMessageBox.critical(
                    self,
                    lang.get("search_prices_dialog.error_title", default="Connection Error"),
                    error_message or lang.get("search_prices_dialog.error_connection", default="Failed to connect to Eden Herald")
                )
                return
            
            # Create ItemsScraper with connected scraper
            items_scraper = ItemsScraper(eden_scraper)
            
            # Search each item
            found_count = 0
            failed_items = []
            
            for idx, item_name in enumerate(selected_items):
                self.status_label.setText(lang.get("search_prices_dialog.status_searching", default=f"Searching: {item_name}..."))
                QApplication.processEvents()
                
                try:
                    # Search item WITHOUT filters (user wants all results for missing prices)
                    from Functions.items_parser import search_item_for_database
                    item_data = search_item_for_database(item_name, items_scraper, self.realm, force_scrape=True, skip_filters=True)
                    
                    if item_data and item_data.get('merchant_price'):
                        # Format price with currency
                        price = item_data.get('merchant_price')
                        currency = item_data.get('merchant_currency', '')
                        price_with_currency = f"{price} {currency}" if currency else price
                        
                        # Update template JSON directly
                        success = self._update_template_price(item_name, price_with_currency)
                        if success:
                            found_count += 1
                            logging.info(f"Added price for {item_name}: {price_with_currency}")
                        else:
                            failed_items.append(f"{item_name} (save error)")
                            logging.error(f"Failed to save {item_name} to template")
                    else:
                        # No price found - offer categorization
                        logging.warning(f"No price found for {item_name}")
                        
                        # Show categorization dialog
                        category_dialog = ItemCategoryDialog(item_name, parent=self)
                        if category_dialog.exec() == QDialog.Accepted:
                            selected_category = category_dialog.get_selected_category()
                            
                            # Save category to database
                            ItemsDatabaseManager.set_item_category(item_name, selected_category)
                            
                            # Get category label for display
                            ItemsDatabaseManager.get_category_label(selected_category, lang.current_language)
                            ItemsDatabaseManager.get_category_icon(selected_category)
                            
                            found_count += 1  # Count as handled
                            logging.info(f"Categorized {item_name} as: {selected_category}")
                        else:
                            # User cancelled categorization
                            failed_items.append(f"{item_name} (not categorized)")
                            logging.warning(f"User cancelled categorization for {item_name}")
                
                except Exception as e:
                    failed_items.append(f"{item_name} (error: {str(e)})")
                    logging.error(f"Error searching {item_name}: {e}", exc_info=True)
                
                self.progress_bar.setValue(idx + 1)
                QApplication.processEvents()
            
            # Show results
            result_message = lang.get(
                "search_prices_dialog.results",
                default=f"Search completed:\n✅ Found: {found_count}/{len(selected_items)}\n❌ Failed: {len(failed_items)}"
            )
            
            if failed_items:
                result_message += "\n\nFailed items:\n" + "\n".join(failed_items[:10])
                if len(failed_items) > 10:
                    result_message += f"\n... and {len(failed_items) - 10} more"
            
            QMessageBox.information(
                self,
                lang.get("search_prices_dialog.complete_title", default="Search Complete"),
                result_message
            )
            
            self.status_label.setText(lang.get("search_prices_dialog.status_complete", default=f"Complete: {found_count} prices added"))
            
            # Refresh parent preview to show updated prices
            if found_count > 0 and hasattr(self.parent(), 'on_selection_changed'):
                self.parent().on_selection_changed()
                
                # Refresh the items list in this dialog to remove found items
                self._refresh_items_list()
            
        except Exception as e:
            logging.error(f"Error during price search: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                lang.get("search_prices_dialog.error_title", default="Error"),
                lang.get("search_prices_dialog.error_search", default=f"Search failed:\n{str(e)}")
            )
        
        finally:
            # CRITICAL: Always close browser to prevent zombie processes
            if eden_scraper:
                try:
                    eden_scraper.close()
                    logging.info("Eden scraper closed successfully")
                except Exception as e:
                    logging.error(f"Error closing scraper: {e}", exc_info=True)
            
            self.active_scraper = None  # Clear reference
            self._reset_ui()
    
    def closeEvent(self, event):
        """Clean up scraper when dialog is closed."""
        if self.active_scraper:
            try:
                logging.info("Closing active scraper on dialog close")
                self.active_scraper.close()
                self.active_scraper = None
            except Exception as e:
                logging.error(f"Error closing scraper on dialog close: {e}", exc_info=True)
        
        super().closeEvent(event)
    
    def _reset_ui(self):
        """Reset UI elements after search."""
        self.search_button.setEnabled(True)
        self.select_all_button.setEnabled(True)
        self.deselect_all_button.setEnabled(True)
        self.close_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def _refresh_items_list(self):
        """Refresh the items list from parent to remove items that now have prices."""
        if hasattr(self.parent(), 'items_without_price'):
            # Get updated list from parent
            updated_items = self.parent().items_without_price
            
            # Update our internal list
            self.items_without_price = updated_items
            
            # Clear and repopulate the list widget
            self.items_list.clear()
            self.items_list.addItems(updated_items)


# ============================================================================
# ITEM CATEGORY DIALOG
# ============================================================================

class ItemCategoryDialog(QDialog):
    """Dialog to categorize an item without price (quest_reward, event_reward, unknown)"""
    
    def __init__(self, item_name, parent=None):
        from Functions.language_manager import lang
        super().__init__(parent)
        self.item_name = item_name
        self.selected_category = None
        
        self.setWindowTitle(lang.get("item_category_dialog.title", default="Categorize Item"))
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.resize(500, 250)
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_text = lang.get(
            "item_category_dialog.info",
            default=f"Item '{item_name}' has no price in database.\nPlease categorize this item:"
        )
        info_label = QLabel(info_text.replace("{item_name}", item_name))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 11pt; padding: 10px;")
        layout.addWidget(info_label)
        
        # Category selection
        category_group = QGroupBox(lang.get("item_category_dialog.category_group", default="Category"))
        category_layout = QVBoxLayout(category_group)
        
        from Functions.items_database_manager import ItemsDatabaseManager
        categories = ItemsDatabaseManager.get_item_categories()
        
        self.category_buttons = QButtonGroup(self)
        
        # Create radio button for each category (except 'unknown')
        for category_key, category_data in categories.items():
            if category_key == "unknown":
                continue  # Skip unknown, it's the default fallback
            
            icon = category_data["icon"]
            # Get label in current language
            from Functions.language_manager import lang
            current_lang = lang.current_language if hasattr(lang, 'current_language') else 'en'
            label = ItemsDatabaseManager.get_category_label(category_key, current_lang)
            
            radio = QRadioButton(f"{icon}  {label}")
            radio.setProperty("category_key", category_key)
            radio.setStyleSheet("font-size: 10pt; padding: 5px;")
            self.category_buttons.addButton(radio)
            category_layout.addWidget(radio)
        
        # Select first option by default
        if self.category_buttons.buttons():
            self.category_buttons.buttons()[0].setChecked(True)
        
        layout.addWidget(category_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(lang.get("item_category_dialog.cancel", default="Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton(lang.get("item_category_dialog.ok", default="OK"))
        ok_btn.setStyleSheet("background-color: #0e639c; color: white; padding: 5px 15px;")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def get_selected_category(self):
        """Get the selected category key"""
        return ui_get_selected_category(self.category_buttons)
