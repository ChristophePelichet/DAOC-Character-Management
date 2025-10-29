"""
Dialog windows for the DAOC Character Manager application.
"""

import re
import os
import logging
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel, 
    QPushButton, QLineEdit, QComboBox, QCheckBox, QSlider, QMessageBox,
    QDialogButtonBox, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget
)
from PySide6.QtCore import Qt, QThread, Signal
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
        
        # Armor Section (new)
        armor_group = QGroupBox(lang.get("armor_group_title"))
        armor_layout = QVBoxLayout()
        
        # Resistances button (placeholder for now)
        resistances_button = QPushButton(lang.get("resistances_button"))
        resistances_button.setEnabled(False)  # Disabled until functionality is added
        resistances_button.setToolTip("Fonctionnalité à venir : gérer les résistances du personnage")
        armor_layout.addWidget(resistances_button)
        
        # Armor Manager button
        armor_manager_button = QPushButton("📁 Gérer les armures")
        armor_manager_button.clicked.connect(self.open_armor_manager)
        armor_manager_button.setToolTip("Upload et gestion des fichiers d'armure créés avec des logiciels tiers")
        armor_layout.addWidget(armor_manager_button)
        
        armor_group.setLayout(armor_layout)
        
        # Horizontal layout for Info and Armor groups side by side
        top_layout = QHBoxLayout()
        top_layout.addWidget(info_group)
        top_layout.addWidget(armor_group)
        layout.addLayout(top_layout)
        
        # Realm Rank Section
        realm_rank_group = QGroupBox("Rang de Royaume")
        realm_rank_layout = QVBoxLayout()
        
        realm_points = self.character_data.get('realm_points', 0)
        
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

    def open_armor_manager(self):
        """Opens the armor management dialog."""
        character_id = self.character_data.get('id', '')
        if not character_id:
            QMessageBox.warning(self, "Erreur", "Impossible de déterminer l'ID du personnage.")
            return
        
        dialog = ArmorManagementDialog(self, character_id)
        dialog.exec()
    
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
        {"key": "class", "name_key": "column_class", "default": True},  # Class visible by default
        {"key": "race", "name_key": "column_race", "default": False},  # Race hidden by default
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

        # Armor Path
        self.armor_path_edit = QLineEdit()
        browse_armor_button = QPushButton(lang.get("browse_button"))
        browse_armor_button.clicked.connect(self.browse_armor_folder)
        armor_path_layout = QHBoxLayout()
        armor_path_layout.addWidget(self.armor_path_edit)
        armor_path_layout.addWidget(browse_armor_button)
        paths_layout.addRow("Dossier des armures :", armor_path_layout)

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

        # Miscellaneous Settings Group (Position 5)
        misc_group = QGroupBox(lang.get("config_misc_group_title", 
                                        default="Divers"))
        misc_layout = QFormLayout()

        # Disable Disclaimer on Startup
        self.disable_disclaimer_check = QCheckBox(lang.get("config_disable_disclaimer_label", 
                                                            default="Désactiver le message d'avertissement au démarrage"))
        misc_layout.addRow(self.disable_disclaimer_check)
        
        misc_group.setLayout(misc_layout)
        main_layout.addWidget(misc_group)

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
        from Functions.path_manager import get_armor_dir
        
        char_folder = config.get("character_folder") or get_character_dir()
        config_folder = config.get("config_folder") or get_config_dir()
        log_folder = config.get("log_folder") or get_log_dir()
        armor_folder = config.get("armor_folder") or get_armor_dir()
        
        self.char_path_edit.setText(char_folder)
        self.config_path_edit.setText(config_folder)
        self.log_path_edit.setText(log_folder)
        self.armor_path_edit.setText(armor_folder)
        self.debug_mode_check.setChecked(config.get("debug_mode", False))
        self.show_debug_window_check.setChecked(config.get("show_debug_window", False))
        self.disable_disclaimer_check.setChecked(config.get("disable_disclaimer", False))
        
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
    
    def browse_armor_folder(self):
        """Browse for armor folder."""
        self.browse_folder(self.armor_path_edit, "select_folder_dialog_title")


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
    finished = Signal(dict)  # Signal émis avec le résultat du test
    
    def __init__(self, cookie_manager):
        super().__init__()
        self.cookie_manager = cookie_manager
    
    def run(self):
        """Exécute le test de connexion"""
        result = self.cookie_manager.test_eden_connection()
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
            self.connection_thread.quit()
            self.connection_thread.wait()
        
        # Créer et démarrer un nouveau thread
        self.connection_thread = ConnectionTestThread(self.cookie_manager)
        self.connection_thread.finished.connect(self.on_connection_test_finished)
        self.connection_thread.start()
    
    def on_connection_test_finished(self, result):
        """Appelé quand le test de connexion est terminé"""
        # Récupérer les infos actuelles pour mettre à jour l'affichage
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
            
            # Afficher les infos de base immédiatement
            self.expiry_label.setText(
                f"📅 <b>Date d'expiration:</b> {expiry_date.strftime('%d/%m/%Y à %H:%M')}<br/>"
                f"⏰ <b>Validité restante:</b> {days} jours<br/>"
                f"🌐 <b>Accès Eden :</b> <span style='color: gray;'>⏳ Test en cours...</span>"
            )
            
            # Lancer le test de connexion en arrière-plan
            self.start_connection_test()
            
            details = f"📦 Total: {info['total_cookies']} cookies<br/>"
            details += f"✓ Valides: {info['valid_cookies']}<br/>"
            
            if info['session_cookies'] > 0:
                details += f"🔄 Session: {info['session_cookies']}<br/>"
            
            details += f"<br/>📁 Fichier: {info['file_path']}"
            
            self.details_label.setText(details)
            self.delete_button.setEnabled(True)
    
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
            # Importer automatiquement après sélection
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
        
        # Vérifier que le fichier existe avant d'essayer d'importer
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
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de supprimer les cookies."
                )
    
    def generate_cookies(self):
        """Génère de nouveaux cookies via authentification navigateur"""
        
        # Message d'information
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Génération des Cookies")
        msg.setTextFormat(Qt.RichText)
        msg.setText("<b>Génération des cookies Eden</b>")
        msg.setInformativeText(
            "Un navigateur Chrome va s'ouvrir pour vous connecter à Eden-DAOC.<br/><br/>"
            "<b>Étapes :</b><br/>"
            "1. Le navigateur s'ouvrira automatiquement<br/>"
            "2. Connectez-vous avec votre compte Discord<br/>"
            "3. Une fois connecté, revenez ici et cliquez sur OK<br/>"
            "4. Les cookies seront automatiquement sauvegardés"
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        if msg.exec() != QMessageBox.Ok:
            return
        
        # Désactiver les boutons pendant le processus
        self.generate_button.setEnabled(False)
        self.cookie_path_edit.setEnabled(False)
        self.status_label.setText("⏳ <b>Ouverture du navigateur...</b>")
        self.status_label.setStyleSheet("color: blue;")
        
        # Forcer la mise à jour de l'interface
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Générer les cookies
        success, message, driver = self.cookie_manager.generate_cookies_with_browser()
        
        if not success:
            # Erreur lors de l'ouverture
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible d'ouvrir le navigateur :\n\n{message}\n\n"
                "Assurez-vous que Chrome et Selenium sont installés."
            )
            self.generate_button.setEnabled(True)
            self.cookie_path_edit.setEnabled(True)
            self.refresh_status()
            return
        
        # Le navigateur est ouvert
        self.status_label.setText("🌐 <b>Navigateur ouvert - Connectez-vous avec Discord</b>")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()
        
        # Dialogue d'attente
        wait_msg = QMessageBox()
        wait_msg.setIcon(QMessageBox.Information)
        wait_msg.setWindowTitle("En attente de connexion")
        wait_msg.setTextFormat(Qt.RichText)
        wait_msg.setText("<b>Connectez-vous maintenant</b>")
        wait_msg.setInformativeText(
            "Le navigateur Chrome est ouvert.<br/><br/>"
            "Veuillez vous connecter avec Discord dans le navigateur,<br/>"
            "puis cliquez sur OK une fois connecté."
        )
        wait_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        result = wait_msg.exec()
        
        if result == QMessageBox.Ok:
            # Récupérer et sauvegarder les cookies
            self.status_label.setText("💾 <b>Sauvegarde des cookies...</b>")
            self.status_label.setStyleSheet("color: blue;")
            QApplication.processEvents()
            
            success, message, count = self.cookie_manager.save_cookies_from_driver(driver)
            
            # Fermer le navigateur
            try:
                driver.quit()
            except:
                pass
            
            if success:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Les cookies ont été générés avec succès !\n\n"
                    f"{message}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la sauvegarde des cookies :\n\n{message}"
                )
        else:
            # Annulation - fermer le navigateur
            try:
                driver.quit()
            except:
                pass
            
            self.status_label.setText("❌ <b>Génération annulée</b>")
            self.status_label.setStyleSheet("color: red;")
        
        # Réactiver les boutons et actualiser
        self.generate_button.setEnabled(True)
        self.cookie_path_edit.setEnabled(True)
        self.refresh_status()
