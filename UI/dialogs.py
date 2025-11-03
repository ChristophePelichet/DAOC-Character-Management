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
    QWidget, QTextEdit, QApplication, QProgressBar, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QBrush, QColor, QIcon, QPixmap
from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir
from Functions.character_manager import get_character_dir
from Functions.logging_manager import get_log_dir, get_logger, log_with_action, LOGGER_CHARACTER
from Functions.data_manager import DataManager

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

        self.setWindowTitle(lang.get("character_sheet_title", name=char_name))
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        
        # Eden Herald Section - EN HAUT POUR FACILITER LA MISE À JOUR
        eden_group = QGroupBox("🌐 Eden Herald")
        eden_layout = QVBoxLayout()
        
        # URL du Herald
        url_form_layout = QFormLayout()
        self.herald_url_edit = QLineEdit()
        current_url = self.character_data.get('url', '')
        self.herald_url_edit.setText(current_url)
        self.herald_url_edit.setPlaceholderText("https://eden-daoc.net/herald?n=player&k=NomPersonnage")
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
        # Mettre en évidence le bouton de mise à jour
        self.update_herald_button.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        herald_buttons_layout.addWidget(self.update_herald_button)
        
        # Définir des stretch égaux pour les deux boutons
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
            # Utiliser findData pour sélectionner par itemData (nom anglais) au lieu du texte affiché
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
            # Utiliser findData pour sélectionner par itemData (nom anglais) au lieu du texte affiché
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
        
        # Coming soon message
        coming_soon_label = QLabel(lang.get("statistics_coming_soon"))
        coming_soon_label.setStyleSheet("font-size: 11px; color: gray; text-align: center;")
        coming_soon_label.setAlignment(Qt.AlignCenter)
        statistics_layout.addWidget(coming_soon_label)
        
        statistics_group.setLayout(statistics_layout)
        
        # Horizontal layout for Info and Statistics groups side by side
        top_layout = QHBoxLayout()
        top_layout.addWidget(info_group)
        top_layout.addWidget(statistics_group)
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
                    import sys
                    import logging
                    print("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update")
                    sys.stderr.write("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update\n")
                    sys.stderr.flush()
                    logging.info("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update")
                    self.parent_app.backup_manager.backup_characters_force(reason="Update")
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
                        import sys
                        import logging
                        print("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update")
                        sys.stderr.write("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update\n")
                        sys.stderr.flush()
                        logging.info("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update")
                        self.parent_app.backup_manager.backup_characters_force(reason="Update")
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
                        import sys
                        import logging
                        print("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Basic Info) - Backup with reason=Update")
                        sys.stderr.write("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Basic Info) - Backup with reason=Update\n")
                        sys.stderr.flush()
                        logging.info("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Basic Info) - Backup with reason=Update")
                        self.parent_app.backup_manager.backup_characters_force(reason="Update")
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
        character_id = self.character_data.get('id', '')
        if not character_id:
            QMessageBox.warning(self, "Erreur", "Impossible de déterminer l'ID du personnage.")
            return
        
        dialog = ArmorManagementDialog(self, character_id)
        dialog.exec()
    
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
        
        # Vérifier que l'URL commence par http:// ou https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.herald_url_edit.setText(url)
        
        try:
            # Ouvrir l'URL avec les cookies dans un thread séparé
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
        
        # Vérifier que l'URL commence par http:// ou https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.herald_url_edit.setText(url)
        
        # Créer une fenêtre de progression personnalisée avec animation
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("⏳ Mise à jour en cours...")
        self.progress_dialog.setModal(True)
        self.progress_dialog.setFixedSize(450, 150)
        
        progress_layout = QVBoxLayout(self.progress_dialog)
        progress_layout.setSpacing(15)
        
        # Icône et titre
        title_layout = QHBoxLayout()
        title_label = QLabel("🌐 Récupération des données depuis Eden Herald...")
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        title_layout.addWidget(title_label)
        progress_layout.addLayout(title_layout)
        
        # Message de détail
        detail_label = QLabel("Connexion au serveur et extraction des informations du personnage.")
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet("color: #666; font-size: 10pt;")
        progress_layout.addWidget(detail_label)
        
        # Barre de progression indéterminée (animation)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Mode indéterminé = animation
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(25)
        progress_layout.addWidget(progress_bar)
        
        # Message d'attente
        wait_label = QLabel("⏱️ Veuillez patienter, cette opération peut prendre quelques secondes...")
        wait_label.setStyleSheet("color: #888; font-size: 9pt; font-style: italic;")
        wait_label.setWordWrap(True)
        progress_layout.addWidget(wait_label)
        
        progress_layout.addStretch()
        
        # Créer et démarrer le worker thread
        self.herald_worker = HeraldScraperWorker(url)
        self.herald_worker.finished.connect(self._on_herald_scraping_finished)
        
        # Afficher le dialogue et démarrer le worker
        self.progress_dialog.show()
        self.herald_worker.start()
    
    def _on_herald_scraping_finished(self, success, new_data, error_msg):
        """Callback appelé quand le scraping est terminé"""
        # Fermer et supprimer la fenêtre de progression
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            delattr(self, 'progress_dialog')
        
        if not success:
            QMessageBox.critical(
                self,
                lang.get("update_char_error"),
                f"{lang.get('update_char_error')}: {error_msg}"
            )
            return
        
        # Afficher le dialogue de validation des changements
        dialog = CharacterUpdateDialog(self, self.character_data, new_data, self.character_data['name'])
        
        if dialog.exec() == QDialog.Accepted:
            selected_changes = dialog.get_selected_changes()
            
            if not selected_changes:
                QMessageBox.information(
                    self,
                    lang.get("update_char_cancelled"),
                    lang.get("update_char_no_changes")
                )
                return
            
            # Appliquer les changements sélectionnés directement dans character_data
            for field, value in selected_changes.items():
                self.character_data[field] = value
            
            # Mettre à jour TOUS les champs de l'interface pour l'affichage immédiat
            # (on reconstruit l'affichage complet plutôt que de mettre à jour champ par champ)
            
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
                
                # Mettre à jour l'affichage du rang et du titre
                self.update_rank_display(realm_points)
                
                # Mettre à jour les dropdowns de rang/niveau
                if hasattr(self.parent_app, 'data_manager'):
                    rank_info = self.parent_app.data_manager.get_realm_rank_info(self.realm, realm_points)
                    if rank_info:
                        current_rank = rank_info['rank']
                        level_str = rank_info['level']  # Format "XLY"
                        level_match = re.search(r'L(\d+)', level_str)
                        if level_match:
                            current_level = int(level_match.group(1))
                            
                            # Mettre à jour le dropdown de rang
                            self.rank_combo.blockSignals(True)
                            self.rank_combo.setCurrentIndex(current_rank - 1)
                            self.rank_combo.blockSignals(False)
                            
                            # Mettre à jour le dropdown de niveau
                            self.update_level_dropdown(current_rank, current_level)
            
            # Sauvegarder directement character_data (pas via save_basic_info qui récupère depuis l'interface)
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
                    import sys
                    import logging
                    print("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Skills/Armor) - Backup with reason=Update")
                    sys.stderr.write("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Skills/Armor) - Backup with reason=Update\n")
                    sys.stderr.flush()
                    logging.info("[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Skills/Armor) - Backup with reason=Update")
                    self.parent_app.backup_manager.backup_characters_force(reason="Update")
                except Exception as e:
                    print(f"[BACKUP_TRIGGER] Warning: Backup after skills/armor modification failed: {e}")
                    sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after skills/armor modification failed: {e}\n")
                    sys.stderr.flush()
                    logging.warning(f"[BACKUP_TRIGGER] Backup after skills/armor modification failed: {e}")
            
            # Rafraîchir la liste des personnages dans la fenêtre principale
            if hasattr(self.parent_app, 'tree_manager'):
                self.parent_app.tree_manager.refresh_character_list()
            elif hasattr(self.parent_app, 'refresh_character_list'):
                self.parent_app.refresh_character_list()
            
            # Message de succès
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

        current_default_server = config.get("default_server", "")
        self.default_server_combo.setCurrentText(current_default_server)

        current_default_season = config.get("default_season", "")
        self.default_season_combo.setCurrentText(current_default_season)

        current_default_realm = config.get("default_realm", "")
        self.default_realm_combo.setCurrentText(current_default_realm)

        manual_resize = config.get("manual_column_resize", False)
        self.manual_column_resize_check.setChecked(manual_resize)
        
        # Browser settings
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
        
        # Label pour afficher le navigateur utilisé
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
            
            # Afficher le navigateur utilisé pour le test
            if hasattr(self.cookie_manager, 'last_browser_used') and self.cookie_manager.last_browser_used:
                browser_icon = {'Chrome': '🔵', 'Edge': '🔷', 'Firefox': '🦊'}.get(self.cookie_manager.last_browser_used, '🌐')
                self.browser_label.setText(
                    f"{browser_icon} <i>Test effectué avec: {self.cookie_manager.last_browser_used}</i>"
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
        
        # Réinitialiser le label du navigateur (sera mis à jour après test/génération)
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
            
            # Rafraîchir le statut Eden dans la fenêtre principale
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
                
                # Rafraîchir le statut Eden dans la fenêtre principale
                if self.parent() and hasattr(self.parent(), 'ui_manager'):
                    self.parent().ui_manager.check_eden_status()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de supprimer les cookies."
                )
    
    def generate_cookies(self):
        """Génère de nouveaux cookies via authentification navigateur"""
        
        # Lire la configuration
        from Functions.config_manager import config
        preferred_browser = config.get('preferred_browser', 'Chrome')
        allow_download = config.get('allow_browser_download', False)
        
        # Désactiver les boutons pendant le processus
        self.generate_button.setEnabled(False)
        self.cookie_path_edit.setEnabled(False)
        self.status_label.setText("⏳ <b>Ouverture du navigateur...</b>")
        self.status_label.setStyleSheet("color: blue;")
        
        # Forcer la mise à jour de l'interface
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Générer les cookies (ouvre le navigateur immédiatement)
        success, message, driver = self.cookie_manager.generate_cookies_with_browser(
            preferred_browser=preferred_browser,
            allow_download=allow_download
        )
        
        if not success:
            # Vérifier si c'est un problème de navigateur manquant
            if "Impossible d'initialiser" in message and not allow_download:
                # Proposer de télécharger un driver
                reply = QMessageBox.question(
                    self,
                    "Téléchargement requis",
                    f"Aucun navigateur compatible n'a été trouvé.\n\n"
                    f"Voulez-vous autoriser le téléchargement automatique d'un driver de navigateur ?\n\n"
                    f"Cela nécessite une connexion Internet.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Réessayer avec téléchargement autorisé
                    success, message, driver = self.cookie_manager.generate_cookies_with_browser(
                        preferred_browser=preferred_browser,
                        allow_download=True
                    )
                    
                    if not success:
                        QMessageBox.critical(
                            self,
                            "Erreur",
                            f"Impossible d'ouvrir le navigateur même après téléchargement :\n\n{message}"
                        )
                        self.generate_button.setEnabled(True)
                        self.cookie_path_edit.setEnabled(True)
                        self.refresh_status()
                        return
                else:
                    self.generate_button.setEnabled(True)
                    self.cookie_path_edit.setEnabled(True)
                    self.refresh_status()
                    return
            else:
                # Autre erreur
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'ouvrir le navigateur :\n\n{message}"
                )
                self.generate_button.setEnabled(True)
                self.cookie_path_edit.setEnabled(True)
                self.refresh_status()
                return
        
        # Le navigateur est ouvert
        browser_name = getattr(self.cookie_manager, 'last_browser_used', 'le navigateur')
        self.status_label.setText(f"🌐 <b>{browser_name} ouvert - Connectez-vous avec Discord</b>")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()
        
        # Dialogue d'attente
        wait_msg = QMessageBox()
        wait_msg.setIcon(QMessageBox.Information)
        wait_msg.setWindowTitle("En attente de connexion")
        wait_msg.setTextFormat(Qt.RichText)
        wait_msg.setText("<b>Connectez-vous maintenant</b>")
        wait_msg.setInformativeText(
            f"Le navigateur <b>{browser_name}</b> est ouvert.<br/><br/>"
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
        
        # Afficher le navigateur utilisé après génération réussie
        if success and hasattr(self.cookie_manager, 'last_browser_used') and self.cookie_manager.last_browser_used:
            browser_icon = {'Chrome': '🔵', 'Edge': '🔷', 'Firefox': '🦊'}.get(self.cookie_manager.last_browser_used, '🌐')
            self.browser_label.setText(
                f"{browser_icon} <i>Généré avec: {self.cookie_manager.last_browser_used}</i>"
            )
        
        # Rafraîchir le statut Eden dans la fenêtre principale si les cookies ont été générés
        if success and self.parent() and hasattr(self.parent(), 'ui_manager'):
            self.parent().ui_manager.check_eden_status()


# ============================================================================
# HERALD SEARCH DIALOG
# ============================================================================

class SearchThread(QThread):
    """Thread pour effectuer la recherche Herald en arrière-plan"""
    search_finished = Signal(bool, str, str)  # (success, message, json_path)
    
    def __init__(self, character_name, realm_filter=""):
        super().__init__()
        self.character_name = character_name
        self.realm_filter = realm_filter
    
    def run(self):
        """Exécute la recherche"""
        from Functions.eden_scraper import search_herald_character
        success, message, json_path = search_herald_character(self.character_name, realm_filter=self.realm_filter)
        self.search_finished.emit(success, message, json_path)


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
        self.current_characters = []  # Stocke les données des personnages trouvés
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
                # Redimensionner l'icône à 20x20 pixels pour le combo
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
        
        # Ligne 2 : Sélection du royaume
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
        
        # Zone de résultats
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
        """Appelé à la fermeture de la fenêtre - nettoie les fichiers temporaires"""
        self._cleanup_temp_files()
        super().closeEvent(event)
    
    def accept(self):
        """Appelé quand on ferme avec le bouton Fermer"""
        self._cleanup_temp_files()
        super().accept()
    
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
        
        # Vérifier le minimum de 3 caractères
        if len(character_name) < 3:
            QMessageBox.warning(
                self,
                "Nom trop court",
                "Veuillez entrer au moins 3 caractères pour la recherche."
            )
            return
        
        # Récupérer le filtre de royaume sélectionné
        realm_filter = self.realm_combo.currentData()
        
        # Désactiver les contrôles
        self.search_button.setEnabled(False)
        self.name_input.setEnabled(False)
        self.realm_combo.setEnabled(False)
        
        # Message de statut avec info du royaume
        realm_text = self.realm_combo.currentText()
        if realm_filter:
            self.status_label.setText(f"⏳ Recherche de '{character_name}' dans {realm_text}...")
        else:
            self.status_label.setText(f"⏳ Recherche de '{character_name}' en cours...")
        self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: blue;")
        
        # Lancer le thread avec le filtre de royaume
        self.search_thread = SearchThread(character_name, realm_filter)
        self.search_thread.search_finished.connect(self.on_search_finished)
        self.search_thread.start()
    
    def on_search_finished(self, success, message, json_path):
        """Appelé quand la recherche est terminée"""
        # Réactiver les contrôles
        self.search_button.setEnabled(True)
        self.name_input.setEnabled(True)
        self.realm_combo.setEnabled(True)
        
        if success:
            # Charger et afficher les résultats
            try:
                import json
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                all_characters = data.get('characters', [])
                search_query = data.get('search_query', '').lower()
                
                # Filtrer pour ne garder que les personnages dont le nom commence par les caractères recherchés
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
                        # Déterminer le royaume à partir de la classe
                        class_name = char.get('class', '')
                        realm = self.CLASS_TO_REALM.get(class_name, "Unknown")
                        realm_color = self.REALM_COLORS.get(realm, "#000000")
                        
                        # Créer une couleur de fond pour le royaume (version plus claire pour la lisibilité)
                        bg_color = QColor(realm_color)
                        bg_color.setAlpha(50)  # Transparence pour la lisibilité
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
                    
                    # Stocker les données des personnages
                    self.current_characters = characters
                    
                    # Mettre à jour le message de statut avec le nombre filtré
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
        
        # Récupérer la ligne sélectionnée
        row = self.results_table.rowAt(position.y())
        if row < 0:
            return
        
        # Créer le menu contextuel
        context_menu = QMenu(self)
        
        # Action d'import
        import_action = context_menu.addAction("📥 Importer ce personnage")
        import_action.triggered.connect(lambda: self._import_single_character(row))
        
        # Afficher le menu à la position du curseur
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
        
        # Récupérer les personnages cochés
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
                # Préparer les données du personnage pour l'import
                name = char_data.get('clean_name', char_data.get('name', ''))
                char_class = char_data.get('class', '')
                realm = self.CLASS_TO_REALM.get(char_class, "Unknown")
                
                # Récupérer la saison par défaut depuis la configuration
                default_season = config.get('default_season', 'S1')
                
                # Créer le dictionnaire de données du personnage
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
                    # Valeurs par défaut pour les champs manquants
                    'server': 'Eden',
                    'season': default_season,
                    'mlevel': '0',
                    'clevel': '0',
                    'notes': f"Mis à jour depuis le Herald le {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
                
                # Vérifier si le personnage existe déjà
                existing_chars = get_all_characters()
                existing_char = None
                for c in existing_chars:
                    if c.get('name', '').lower() == name.lower():
                        existing_char = c
                        break
                
                if existing_char:
                    # Le personnage existe, on va le mettre à jour
                    # Construire le chemin du fichier existant
                    base_char_dir = get_character_dir()
                    char_season = existing_char.get('season', 'S1')
                    char_realm = existing_char.get('realm', realm)
                    file_path = os.path.join(base_char_dir, char_season, char_realm, f"{name}.json")
                    
                    if os.path.exists(file_path):
                        # Charger les données existantes pour conserver les infos importantes
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                            
                            # Mettre à jour avec les nouvelles données (seulement les infos pertinentes)
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
        
        # Afficher le résultat
        if success_count > 0 or updated_count > 0:
            message = ""
            if success_count > 0:
                message += f"✅ {success_count} personnage(s) importé(s) avec succès !"
            if updated_count > 0:
                if message:
                    message += "\n"
                message += f"🔄 {updated_count} personnage(s) mis à jour !"
            
            if error_count > 0:
                message += f"\n⚠️ {error_count} erreur(s):\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n... et {len(errors) - 5} autre(s) erreur(s)"
            
            QMessageBox.information(self, "Import terminé", message)
            
            # Rafraîchir l'interface principale
            if hasattr(self.parent(), 'tree_manager') and hasattr(self.parent().tree_manager, 'refresh_character_list'):
                self.parent().tree_manager.refresh_character_list()
            
            # Trigger backup after mass import/update
            parent_app = self.parent()
            if hasattr(parent_app, 'backup_manager'):
                try:
                    import sys
                    import logging
                    print(f"[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - {success_count} created, {updated_count} updated - Backup with reason=Update")
                    sys.stderr.write(f"[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - {success_count} created, {updated_count} updated - Backup with reason=Update\n")
                    sys.stderr.flush()
                    logging.info(f"[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - {success_count} created, {updated_count} updated - Backup with reason=Update")
                    parent_app.backup_manager.backup_characters_force(reason="Update")
                except Exception as e:
                    print(f"[BACKUP_TRIGGER] Warning: Backup after mass import failed: {e}")
                    sys.stderr.write(f"[BACKUP_TRIGGER] Warning: Backup after mass import failed: {e}\n")
                    sys.stderr.flush()
                    logging.warning(f"[BACKUP_TRIGGER] Backup after mass import failed: {e}")
        else:
            error_msg = "❌ Aucun personnage n'a pu être importé ou mis à jour.\n\n"
            error_msg += "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... et {len(errors) - 10} autre(s) erreur(s)"
            QMessageBox.warning(self, "Échec de l'import", error_msg)


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
        
        # Détecter les changements
        self._detect_changes()
        
        layout.addWidget(self.changes_table)
        
        # Boutons de sélection
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
        # Champs à comparer (TOUS les champs importants)
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
            # Cas spécial pour realm_points qui peut contenir des espaces
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
            
            if isinstance(current_value, (int, float)):
                current_value_str = str(current_value)
            else:
                current_value_str = str(current_value) if current_value else ''
            
            if isinstance(new_value, (int, float)):
                new_value_str = str(new_value)
            else:
                new_value_str = str(new_value) if new_value else ''
            
            # Déterminer si c'est un changement
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
            # Case à cocher (seulement si changement)
            if data['has_change']:
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.changes_table.setCellWidget(row, 0, checkbox_widget)
                
                # Stocker la référence de la checkbox et la valeur brute
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
                value_raw = item.data(Qt.UserRole + 2)  # Récupérer la valeur brute
                
                if checkbox and checkbox.isChecked():
                    selected[field] = value_raw  # Utiliser la valeur brute
        
        return selected


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



