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
from Functions.data_manager import DataManager


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
            self.class_combo.setCurrentText(current_class)
        self.class_combo.currentTextChanged.connect(self._on_class_changed_sheet)
        info_layout.addRow(lang.get("new_char_class_prompt", default="Classe :"), self.class_combo)
        
        # Editable race dropdown (AFTER class)
        self.race_combo = QComboBox()
        self._populate_races_sheet()
        current_race = self.character_data.get('race', '')
        if current_race:
            self.race_combo.setCurrentText(current_race)
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
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        button_box.accepted.connect(self.save_basic_info)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
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
    
    def _on_class_changed_sheet(self):
        """Called when class is changed in character sheet."""
        self._populate_races_sheet()
    
    def _on_race_changed_sheet(self):
        """Called when race is changed in character sheet (no action needed)."""
        pass
    
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
                self.rank_title_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {color};")
            
            # Update character data
            self.character_data['realm'] = new_realm
            self.character_data['level'] = new_level
            self.character_data['season'] = new_season
            self.character_data['server'] = new_server
            self.character_data['page'] = new_page
            self.character_data['guild'] = new_guild
            self.character_data['race'] = new_race
            self.character_data['class'] = new_class
            
            # Save character (it's already moved if realm changed)
            if old_realm == new_realm:
                from Functions.character_manager import save_character
                success, msg = save_character(self.character_data, allow_overwrite=True)
                if not success:
                    QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde : {msg}")
                    return
            
            QMessageBox.information(self, "Succès", "Informations du personnage mises à jour avec succès !")
            # Refresh list in parent
            if hasattr(self.parent_app, 'refresh_character_list'):
                self.parent_app.refresh_character_list()
            self.accept()  # Close dialog
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

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
        {"key": "level", "name_key": "column_level", "default": True},
        {"key": "realm_rank", "name_key": "column_realm_rank", "default": True},
        {"key": "realm_title", "name_key": "column_realm_title", "default": True},
        {"key": "guild", "name_key": "column_guild", "default": True},
        {"key": "page", "name_key": "column_page", "default": True},
        {"key": "server", "name_key": "column_server", "default": False},  # Server hidden by default
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
        self.setMinimumSize(500, 400)
        self.parent_app = parent
        self.available_languages = available_languages or {}
        self.available_seasons = available_seasons or []
        self.available_servers = available_servers or []
        self.available_realms = available_realms or []

        main_layout = QVBoxLayout(self)

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

        paths_group.setLayout(paths_layout)
        main_layout.addWidget(paths_group)

        # General Settings (Position 2)
        general_group = QGroupBox(lang.get("config_general_group_title", 
                                           default="Paramètres généraux"))
        general_layout = QFormLayout()

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.available_languages.values())
        general_layout.addRow(lang.get("config_language_label"), self.language_combo)
        
        # Column resize mode
        self.manual_column_resize_check = QCheckBox(lang.get("config_manual_column_resize_label", 
                                                              default="Gestion manuelle de la taille des colonnes"))
        general_layout.addRow(self.manual_column_resize_check)
        
        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)

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
        main_layout.addWidget(server_group)

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
        main_layout.addWidget(debug_group)

        main_layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.update_fields()

    def update_fields(self):
        """Fills the fields with current configuration values."""
        # Use 'or' to handle None or empty string values and fallback to default paths
        char_folder = config.get("character_folder") or get_character_dir()
        config_folder = config.get("config_folder") or get_config_dir()
        log_folder = config.get("log_folder") or get_log_dir()
        
        self.char_path_edit.setText(char_folder)
        self.config_path_edit.setText(config_folder)
        self.log_path_edit.setText(log_folder)
        self.debug_mode_check.setChecked(config.get("debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("show_debug_window", False))
        
        current_lang_code = config.get("language", "fr")
        current_lang_name = self.available_languages.get(current_lang_code, "Français")
        self.language_combo.setCurrentText(current_lang_name)

        current_default_server = config.get("default_server", "")
        self.default_server_combo.setCurrentText(current_default_server)

        current_default_season = config.get("default_season", "")
        self.default_season_combo.setCurrentText(current_default_season)

        current_default_realm = config.get("default_realm", "")
        self.default_realm_combo.setCurrentText(current_default_realm)

        manual_resize = config.get("manual_column_resize", False)
        self.manual_column_resize_check.setChecked(manual_resize)

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
