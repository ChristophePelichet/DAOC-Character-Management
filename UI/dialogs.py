"""
Dialog windows for the DAOC Character Manager application.
"""

import re
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel, 
    QPushButton, QLineEdit, QComboBox, QCheckBox, QSlider, QMessageBox,
    QDialogButtonBox, QFileDialog
)
from PySide6.QtCore import Qt
from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir
from Functions.character_manager import get_character_dir
from Functions.logging_manager import get_log_dir


class CharacterSheetWindow(QDialog):
    """Window to display character details."""
    
    def __init__(self, parent, character_data):
        super().__init__(parent)
        self.character_data = character_data
        self.parent_app = parent
        char_name = self.character_data.get('name', 'N/A')
        self.realm = self.character_data.get('realm', 'Albion')

        self.setWindowTitle(lang.get("character_sheet_title", name=char_name))
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        
        # Basic Information Section
        info_group = QGroupBox("Informations générales")
        info_layout = QFormLayout()
        info_layout.addRow("Nom :", QLabel(char_name))
        info_layout.addRow("Royaume :", QLabel(self.realm))
        info_layout.addRow("Niveau :", QLabel(str(self.character_data.get('level', 'N/A'))))
        info_layout.addRow("Saison :", QLabel(self.character_data.get('season', 'N/A')))
        info_layout.addRow("Serveur :", QLabel(self.character_data.get('server', 'N/A')))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Realm Rank Section
        realm_rank_group = QGroupBox("Rang de Royaume")
        realm_rank_layout = QVBoxLayout()
        
        realm_points = self.character_data.get('realm_points', 0)
        
        # Current rank and title display
        self.rank_title_label = QLabel()
        self.rank_title_label.setAlignment(Qt.AlignCenter)
        self.update_rank_display(realm_points)
        
        # Styling for title label (bold and colored)
        realm_colors = {
            "Albion": "#CC0000",
            "Hibernia": "#00AA00",
            "Midgard": "#0066CC"
        }
        color = realm_colors.get(self.realm, "#000000")
        self.rank_title_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {color};")
        realm_rank_layout.addWidget(self.rank_title_label)
        
        # Separator
        realm_rank_layout.addWidget(QLabel(""))
        
        # Manual Rank Control Section
        control_group = QGroupBox("Ajustement du Rang")
        control_layout = QVBoxLayout()
        
        # Rank slider (1-14)
        rank_slider_layout = QHBoxLayout()
        rank_slider_layout.addWidget(QLabel("Rang :"))
        
        self.rank_slider = QSlider(Qt.Horizontal)
        self.rank_slider.setMinimum(1)
        self.rank_slider.setMaximum(14)
        self.rank_slider.setTickPosition(QSlider.TicksBelow)
        self.rank_slider.setTickInterval(1)
        
        # Get current rank
        current_rank = 1
        if hasattr(parent, 'data_manager'):
            rank_info = parent.data_manager.get_realm_rank_info(self.realm, realm_points)
            if rank_info:
                current_rank = rank_info['rank']
        
        self.rank_slider.setValue(current_rank)
        self.rank_slider.valueChanged.connect(self.on_rank_changed)
        rank_slider_layout.addWidget(self.rank_slider)
        
        self.rank_value_label = QLabel(f"Rank {current_rank}")
        self.rank_value_label.setMinimumWidth(60)
        rank_slider_layout.addWidget(self.rank_value_label)
        control_layout.addLayout(rank_slider_layout)
        
        # Level slider (1-10 per rank, except rank 1 which has 9 levels)
        level_slider_layout = QHBoxLayout()
        level_slider_layout.addWidget(QLabel("Niveau :"))
        
        self.level_slider = QSlider(Qt.Horizontal)
        self.level_slider.setMinimum(1)
        self.level_slider.setMaximum(10)
        self.level_slider.setTickPosition(QSlider.TicksBelow)
        self.level_slider.setTickInterval(1)
        
        # Get current level
        current_level = 1
        if hasattr(parent, 'data_manager') and rank_info:
            level_str = rank_info['level']  # Format "XLY"
            level_match = re.search(r'L(\d+)', level_str)
            if level_match:
                current_level = int(level_match.group(1))
        
        self.level_slider.setValue(current_level)
        self.level_slider.valueChanged.connect(self.on_level_changed)
        level_slider_layout.addWidget(self.level_slider)
        
        self.level_value_label = QLabel(f"L{current_level}")
        self.level_value_label.setMinimumWidth(40)
        level_slider_layout.addWidget(self.level_value_label)
        control_layout.addLayout(level_slider_layout)
        
        # Display RP info for this rank/level
        self.rp_info_label = QLabel()
        self.rp_info_label.setAlignment(Qt.AlignCenter)
        self.update_rp_info()
        control_layout.addWidget(self.rp_info_label)
        
        # Apply button
        apply_button = QPushButton("Appliquer ce rang")
        apply_button.clicked.connect(self.apply_rank)
        control_layout.addWidget(apply_button)
        
        control_group.setLayout(control_layout)
        realm_rank_layout.addWidget(control_group)
        
        realm_rank_group.setLayout(realm_rank_layout)
        layout.addWidget(realm_rank_group)
        
        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_rank_changed(self, value):
        """Called when rank slider changes."""
        self.rank_value_label.setText(f"Rank {value}")
        # Adjust max level slider (rank 1 = 9 levels, others = 10)
        max_level = 9 if value == 1 else 10
        self.level_slider.setMaximum(max_level)
        if self.level_slider.value() > max_level:
            self.level_slider.setValue(max_level)
        self.update_rp_info()
    
    def on_level_changed(self, value):
        """Called when level slider changes."""
        self.level_value_label.setText(f"L{value}")
        self.update_rp_info()
    
    def update_rp_info(self):
        """Updates RP display for the selected rank/level."""
        if not hasattr(self.parent_app, 'data_manager'):
            return
        
        rank = self.rank_slider.value()
        level = self.level_slider.value()
        level_str = f"{rank}L{level}"
        
        # Find RP for this level
        rank_info = self.parent_app.data_manager.get_rank_by_level(self.realm, level_str)
        if rank_info:
            self.rp_info_label.setText(
                f"Ce rang nécessite : {rank_info['realm_points']:,} RP\n"
                f"Titre : {rank_info['title']}"
            )
        else:
            self.rp_info_label.setText("Informations non disponibles")
    
    def update_rank_display(self, realm_points):
        """Updates current rank and title display."""
        if hasattr(self.parent_app, 'data_manager'):
            rank_info = self.parent_app.data_manager.get_realm_rank_info(self.realm, realm_points)
            if rank_info:
                self.rank_title_label.setText(
                    f"Rank {rank_info['rank']} - {rank_info['title']}\n"
                    f"({rank_info['level']} - {realm_points:,} RP)"
                )
            else:
                self.rank_title_label.setText(f"Rank 1 - Guardian\n(1L1 - 0 RP)")
        else:
            realm_rank = self.character_data.get('realm_rank', '1L1')
            self.rank_title_label.setText(f"{realm_rank} - {realm_points:,} RP")
    
    def apply_rank(self):
        """Applies the selected rank to the character."""
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
                QMessageBox.information(self, "Succès", f"Rang mis à jour : {level_str}\nRealm Points : {new_rp:,}")
                # Update display
                self.update_rank_display(new_rp)
                # Refresh list
                if hasattr(self.parent_app, 'refresh_character_list'):
                    self.parent_app.refresh_character_list()
            else:
                QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde : {msg}")


class ColumnsConfigDialog(QDialog):
    """Dialog to configure which columns are visible in the character list."""
    
    # Define all available columns with their default visibility
    COLUMNS_CONFIG = [
        {"key": "selection", "name_key": "column_selection", "default": True},
        {"key": "realm", "name_key": "column_realm", "default": True},
        {"key": "season", "name_key": "column_season", "default": True},
        {"key": "server", "name_key": "column_server", "default": True},
        {"key": "name", "name_key": "column_name", "default": True},
        {"key": "level", "name_key": "column_level", "default": True},
        {"key": "realm_rank", "name_key": "column_realm_rank", "default": True},
        {"key": "realm_title", "name_key": "column_realm_title", "default": True},
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
    
    def __init__(self, parent=None, realms=None, servers=None, default_server=None, 
                 seasons=None, default_season=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("new_char_dialog_title"))

        self.realms = realms if realms else []
        self.servers = servers if servers else []
        self.seasons = seasons if seasons else []
        self.default_server = default_server
        self.default_season = default_season
        
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        layout.addRow(lang.get("new_char_dialog_prompt"), self.name_edit)

        self.realm_combo = QComboBox(self)
        self.realm_combo.addItems(self.realms)
        layout.addRow(lang.get("new_char_realm_prompt"), self.realm_combo)
        
        # Server before Season
        self.server_combo = QComboBox(self)
        self.server_combo.addItems(self.servers)
        self.server_combo.setCurrentText(self.default_server)
        layout.addRow(lang.get("new_char_server_prompt", default="Serveur :"), self.server_combo)

        # Season
        self.season_combo = QComboBox(self)
        self.season_combo.addItems(self.seasons)
        self.season_combo.setCurrentText(self.default_season)
        layout.addRow(lang.get("new_char_season_prompt", default="Saison :"), self.season_combo)
        # Connect signal for debugging
        self.season_combo.currentTextChanged.connect(self._on_season_changed)

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
        season = self.season_combo.currentText()
        server = self.server_combo.currentText()
        return name, realm, season, server
    
    def _on_season_changed(self, new_season):
        logging.debug(f"New character dialog: Season changed to '{new_season}'")


class ConfigurationDialog(QDialog):
    """Configuration window for the application."""
    
    def __init__(self, parent=None, available_languages=None, available_servers=None, 
                 available_seasons=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("configuration_window_title"))
        self.setMinimumSize(500, 250)
        self.parent_app = parent
        self.available_languages = available_languages or {}
        self.available_servers = available_servers or []
        self.available_seasons = available_seasons or []

        main_layout = QVBoxLayout(self)

        # General Settings
        form_layout = QFormLayout()

        # Character Path
        self.char_path_edit = QLineEdit()
        browse_char_button = QPushButton(lang.get("browse_button"))
        browse_char_button.clicked.connect(self.browse_character_folder)
        char_path_layout = QHBoxLayout()
        char_path_layout.addWidget(self.char_path_edit)
        char_path_layout.addWidget(browse_char_button)
        form_layout.addRow(lang.get("config_path_label"), char_path_layout)

        # Config Path
        self.config_path_edit = QLineEdit()
        browse_config_button = QPushButton(lang.get("browse_button"))
        browse_config_button.clicked.connect(self.browse_config_folder)
        config_path_layout = QHBoxLayout()
        config_path_layout.addWidget(self.config_path_edit)
        config_path_layout.addWidget(browse_config_button)
        form_layout.addRow(lang.get("config_file_path_label"), config_path_layout)

        # Log Path
        self.log_path_edit = QLineEdit()
        browse_log_button = QPushButton(lang.get("browse_button"))
        browse_log_button.clicked.connect(self.browse_log_folder)
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(browse_log_button)
        form_layout.addRow(lang.get("config_log_path_label"), log_path_layout)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.available_languages.values())
        form_layout.addRow(lang.get("config_language_label"), self.language_combo)

        # Debug Mode
        self.debug_mode_check = QCheckBox(lang.get("config_debug_mode_label"))
        form_layout.addRow(self.debug_mode_check)

        # Show Debug Window
        self.show_debug_window_check = QCheckBox(lang.get("config_show_debug_window_label"))
        form_layout.addRow(self.show_debug_window_check)
        main_layout.addLayout(form_layout)

        # Server & Season Settings
        server_season_group = QGroupBox(lang.get("config_server_season_group_title", 
                                                  default="Serveur & Saison"))
        server_season_layout = QFormLayout()

        # Default Server
        self.default_server_combo = QComboBox()
        self.default_server_combo.addItems(self.available_servers)
        server_season_layout.addRow(lang.get("config_default_server_label", 
                                             default="Serveur par défaut"), 
                                    self.default_server_combo)

        # Default Season
        self.default_season_combo = QComboBox()
        self.default_season_combo.addItems(self.available_seasons)
        server_season_layout.addRow(lang.get("config_default_season_label", 
                                             default="Saison par défaut"), 
                                    self.default_season_combo)

        server_season_group.setLayout(server_season_layout)
        main_layout.addWidget(server_season_group)

        main_layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

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

        current_default_server = config.get("default_server", "")
        self.default_server_combo.setCurrentText(current_default_server)

        current_default_season = config.get("default_season", "")
        self.default_season_combo.setCurrentText(current_default_season)

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
