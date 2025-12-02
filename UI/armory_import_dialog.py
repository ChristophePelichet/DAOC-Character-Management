"""
Armory Import Dialog - Interface pour importer des items depuis des fichiers template
"""

import os
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QGroupBox, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QSplitter, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QFont, QDesktopServices

from Functions.language_manager import lang
from Functions.config_manager import config


class ItemImportWorker(QThread):
    """Worker thread pour importer des items en arrière-plan"""
    progress = Signal(int, int, str)  # current, total, message
    item_found = Signal(dict)  # item data
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, file_path, realm, debug_mode=False):
        super().__init__()
        self.file_path = file_path
        self.realm = realm
        self.debug_mode = debug_mode
        self.items_data = []
        
    def run(self):
        """Exécute l'import en arrière-plan"""
        try:
            from Functions.items_parser import parse_template_file
            from Functions.cookie_manager import CookieManager
            from Functions.eden_scraper import EdenScraper
            from Functions.items_scraper import ItemsScraper
            
            # Parse le fichier template
            reading_file = lang.get("armory_import.reading_file", default="Lecture du fichier...")
            self.progress.emit(0, 100, f"📖 {reading_file}")
            items = parse_template_file(self.file_path)
            
            if not items:
                self.finished.emit(False, "Aucun item trouvé dans le fichier")
                return
            
            # DEBUG: Limiter au premier item seulement
            if self.debug_mode and len(items) > 1:
                items = items[:1]
                self.progress.emit(0, 1, "🐛 MODE DEBUG: Traitement du 1er item uniquement")
            
            total_items = len(items)
            self.progress.emit(0, total_items, f"📦 {total_items} items à traiter")
            
            # Initialize scraper
            self.progress.emit(0, total_items, "🔧 Initialisation du scraper...")
            cookie_manager = CookieManager()
            eden_scraper = EdenScraper(cookie_manager)
            
            if not eden_scraper.initialize_driver(headless=False, minimize=False):
                self.finished.emit(False, "Erreur d'initialisation du driver")
                return
            
            if not eden_scraper.load_cookies():
                eden_scraper.close()
                self.finished.emit(False, "Erreur de chargement des cookies")
                return
            
            items_scraper = ItemsScraper(eden_scraper)
            
            # Process each item
            success_count = 0
            failed_count = 0
            
            for i, item_name in enumerate(items, 1):
                # items is now a list of strings (item names)
                self.progress.emit(i, total_items, f"🔍 Recherche: {item_name}")
                
                try:
                    # Search for item ID
                    item_id = items_scraper.find_item_id(item_name, self.realm)
                    
                    if not item_id:
                        self.progress.emit(i, total_items, f"❌ Non trouvé: {item_name}")
                        failed_count += 1
                        continue
                    
                    # Get item details
                    self.progress.emit(i, total_items, f"📄 Détails: {item_name}")
                    details = items_scraper.get_item_details(item_id, self.realm, item_name=item_name)
                    
                    # Filter out quest items (zone="Devices")
                    if details and details.get('name'):
                        merchants = details.get('merchants', [])
                        # Skip if no merchants (Devices/quest items)
                        if not merchants:
                            self.progress.emit(i, total_items, f"⚠️ Ignoré (objet de quête): {item_name}")
                            continue
                        
                        self.item_found.emit(details)
                        success_count += 1
                        self.progress.emit(i, total_items, f"✅ Trouvé: {item_name}")
                    else:
                        failed_count += 1
                        self.progress.emit(i, total_items, f"⚠️ Détails incomplets: {item_name}")
                        
                except Exception as e:
                    logging.error(f"Erreur traitement item {item_name}: {e}")
                    failed_count += 1
                    self.progress.emit(i, total_items, f"❌ Erreur: {item_name}")
            
            # Close scraper
            eden_scraper.close()
            
            # Finish
            import_finished = lang.get("armory_import.import_finished_message", default="Import terminé")
            message = f"✅ {import_finished}: {success_count} réussis, {failed_count} échoués"
            self.finished.emit(True, message)
            
        except Exception as e:
            logging.error(f"Erreur dans ItemImportWorker: {e}", exc_info=True)
            self.finished.emit(False, f"Erreur: {str(e)}")


class ArmoryImportDialog(QDialog):
    """
    Dialogue pour importer des items depuis des fichiers template (.txt)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("armory_import.window_title", default="Armurerie - Import d'items"))
        self.resize(900, 700)
        
        # Activer le redimensionnement et les boutons min/max
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        self.import_worker = None
        self.imported_items = []
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # === File Selection Group ===
        file_group = QGroupBox(lang.get("armory_import.file_group_title", default="📂 Fichier Zenkcraft"))
        file_layout = QVBoxLayout()
        
        # File selection row
        file_row = QHBoxLayout()
        self.file_label = QLabel(lang.get("armory_import.no_file_selected", default="Aucun fichier sélectionné"))
        self.file_label.setStyleSheet("color: #888;")
        file_row.addWidget(self.file_label, 1)
        
        self.browse_button = QPushButton(lang.get("armory_import.browse_button", default="📁 Parcourir..."))
        self.browse_button.setMinimumWidth(120)
        file_row.addWidget(self.browse_button)
        
        file_layout.addLayout(file_row)
        
        # Realm selection row
        realm_row = QHBoxLayout()
        realm_row.addWidget(QLabel(lang.get("armory_import.realm_label", default="🏰 Royaume:")))
        
        from PySide6.QtWidgets import QComboBox
        self.realm_combo = QComboBox()
        self.realm_combo.addItems(["Albion", "Hibernia", "Midgard"])
        realm_row.addWidget(self.realm_combo, 1)
        
        file_layout.addLayout(realm_row)
        
        # Debug mode checkbox
        from PySide6.QtWidgets import QCheckBox
        self.debug_checkbox = QCheckBox("🐛 Mode Debug (1er item uniquement)")
        self.debug_checkbox.setChecked(True)  # Activé par défaut
        self.debug_checkbox.setStyleSheet("color: #FF9800; font-weight: bold;")
        file_layout.addWidget(self.debug_checkbox)
        
        # Import button
        self.import_button = QPushButton(lang.get("armory_import.start_import_button", default="▶️ Démarrer l'import"))
        self.import_button.setEnabled(False)
        self.import_button.setMinimumHeight(40)
        file_layout.addWidget(self.import_button)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # === Progress Group ===
        progress_group = QGroupBox(lang.get("armory_import.progress_group_title", default="⌛ Progression"))
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel(lang.get("armory_import.waiting_status", default="En attente..."))
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # === Results Splitter ===
        splitter = QSplitter(Qt.Vertical)
        
        # Items Table
        items_group = QGroupBox(lang.get("armory_import.items_found_group_title", default="📦 Items trouvés"))
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget(0, 7)
        self.items_table.setHorizontalHeaderLabels([
            lang.get("armory_import.table_columns.id", default="ID"),
            lang.get("armory_import.table_columns.name", default="Nom"),
            lang.get("armory_import.table_columns.type", default="Type"),
            lang.get("armory_import.table_columns.slot", default="Slot"),
            lang.get("armory_import.table_columns.zone", default="Zone"),
            lang.get("armory_import.table_columns.price", default="Prix"),
            lang.get("armory_import.table_columns.currency", default="Devises")
        ])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        splitter.addWidget(items_group)
        
        # Details Text
        details_group = QGroupBox(lang.get("armory_import.details_group_title", default="ℹ️ Détails de l'item sélectionné"))
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Consolas", 9))
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        splitter.addWidget(details_group)
        
        splitter.setSizes([400, 200])
        layout.addWidget(splitter, 1)
        
        # === Action Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton(lang.get("armory_import.save_database_button", default="💾 Sauvegarder la base de données"))
        self.save_button.setEnabled(False)
        self.save_button.setMinimumHeight(35)
        button_layout.addWidget(self.save_button)
        
        self.close_button = QPushButton(lang.get("armory_import.close_button", default="✖️ Fermer"))
        self.close_button.setMinimumHeight(35)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def _connect_signals(self):
        """Connecte les signaux"""
        self.browse_button.clicked.connect(self._browse_file)
        self.import_button.clicked.connect(self._start_import)
        self.save_button.clicked.connect(self._save_database)
        self.close_button.clicked.connect(self._close_dialog)
        self.items_table.itemSelectionChanged.connect(self._on_item_selected)
        self.items_table.cellClicked.connect(self._on_cell_clicked)
        
    def _browse_file(self):
        """Ouvre un dialogue pour sélectionner le fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier Zenkcraft",
            str(Path.home()),
            "Fichiers Zenkcraft (*.txt);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.import_button.setEnabled(True)
            
    def _start_import(self):
        """Démarre l'import"""
        if not hasattr(self, 'file_path'):
            return
        
        # Disable controls during import
        self.import_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.realm_combo.setEnabled(False)
        
        # Clear previous results
        self.imported_items.clear()
        self.items_table.setRowCount(0)
        self.details_text.clear()
        
        # Create and start worker
        realm = self.realm_combo.currentText()
        debug_mode = self.debug_checkbox.isChecked()
        self.import_worker = ItemImportWorker(self.file_path, realm, debug_mode)
        self.import_worker.progress.connect(self._on_progress)
        self.import_worker.item_found.connect(self._on_item_found)
        self.import_worker.finished.connect(self._on_import_finished)
        self.import_worker.start()
        
    def _on_progress(self, current, total, message):
        """Met à jour la progression"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(message)
        
    def _on_item_found(self, item_data):
        """Ajoute un item trouvé à la table"""
        self.imported_items.append(item_data)
        
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # ID avec lien cliquable (stocker l'ID dans UserRole)
        item_id = item_data.get('id', 'N/A')
        id_item = QTableWidgetItem(str(item_id))
        id_item.setData(Qt.UserRole, item_id)  # Stocker l'ID pour le lien
        id_item.setForeground(Qt.blue)  # Couleur bleue pour indiquer le lien
        id_item.setToolTip(f"Cliquer pour ouvrir sur Eden (ID: {item_id})")
        self.items_table.setItem(row, 0, id_item)
        
        self.items_table.setItem(row, 1, QTableWidgetItem(item_data.get('name', 'N/A')))
        self.items_table.setItem(row, 2, QTableWidgetItem(item_data.get('type', 'N/A')))
        self.items_table.setItem(row, 3, QTableWidgetItem(item_data.get('slot', 'N/A')))
        
        # Zone, Prix et Devises (premier marchand)
        merchants = item_data.get('merchants', [])
        if merchants:
            zone = merchants[0].get('zone', 'N/A')
            price_parsed = merchants[0].get('price_parsed', {})
            # Prix : seulement les chiffres
            price_display = str(price_parsed.get('amount', '')) if price_parsed else ''
            currency_display = price_parsed.get('currency', '') if price_parsed else ''
            self.items_table.setItem(row, 4, QTableWidgetItem(zone))
            self.items_table.setItem(row, 5, QTableWidgetItem(price_display))
            self.items_table.setItem(row, 6, QTableWidgetItem(currency_display))
        else:
            self.items_table.setItem(row, 4, QTableWidgetItem('Devices'))
            self.items_table.setItem(row, 5, QTableWidgetItem(''))
            self.items_table.setItem(row, 6, QTableWidgetItem(''))
        
        # Auto-resize columns
        self.items_table.resizeColumnsToContents()
        
    def _on_import_finished(self, success, message):
        """Traite la fin de l'import"""
        self.progress_label.setText(message)
        
        # Re-enable controls
        self.import_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.realm_combo.setEnabled(True)
        
        if success and self.imported_items:
            # Check if personal database is enabled
            from Functions.config_manager import config
            use_personal = config.get('armory.use_personal_database', default=False)
            auto_add = config.get('armory.auto_add_scraped_items', default=True)
            
            if use_personal and auto_add:
                # Auto-add scraped items to personal database
                self._auto_add_scraped_items()
            elif use_personal and not auto_add:
                # Ask user if they want to add scraped items
                self._ask_add_scraped_items()
            
            # Enable save button for template imports (not for scraped items)
            self.save_button.setEnabled(True)
            
            QMessageBox.information(self, 
                lang.get("armory_import.import_finished_title", default="Import terminé"), 
                message)
        elif not success:
            QMessageBox.warning(self, 
                lang.get("armory_import.import_error_title", default="Erreur d'import"), 
                message)
    
    def _auto_add_scraped_items(self):
        """Automatically add all scraped items to personal database"""
        try:
            from Functions.items_database_manager import ItemsDatabaseManager
            from Functions.config_manager import ConfigManager
            from Functions.path_manager import path_manager
            
            config_manager = ConfigManager()
            db_manager = ItemsDatabaseManager(config_manager, path_manager)
            
            added_count = 0
            realm = self.realm_combo.currentText()
            
            for item_data in self.imported_items:
                success, message = db_manager.add_scraped_item(item_data, realm)
                if success:
                    added_count += 1
            
            if added_count > 0:
                success_message = lang.get('armory_settings.add_scraped_success', 
                    default="Item ajouté : {item_name}")
                QMessageBox.information(self, 
                    lang.get("armory_import.import_finished_title", default="Import terminé"),
                    f"{added_count} items ajoutés à votre base de données personnelle")
                
        except Exception as e:
            logging.error(f"Error auto-adding scraped items: {e}", exc_info=True)
    
    def _ask_add_scraped_items(self):
        """Ask user if they want to add scraped items to personal database"""
        try:
            from Functions.items_database_manager import ItemsDatabaseManager
            from Functions.config_manager import ConfigManager, config
            from Functions.path_manager import path_manager
            
            # Create custom dialog with checkbox
            dialog = QMessageBox(self)
            dialog.setWindowTitle(lang.get('armory_settings.add_scraped_item_title', 
                default="Ajouter à votre base ?"))
            
            item_count = len(self.imported_items)
            message = f"{item_count} items ont été trouvés sur Eden.\n"
            message += "Voulez-vous les ajouter à votre base de données personnelle ?"
            dialog.setText(message)
            
            # Add checkbox for "Always add automatically"
            always_check = QCheckBox(lang.get('armory_settings.add_scraped_item_always', 
                default="Toujours ajouter automatiquement"))
            dialog.setCheckBox(always_check)
            
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog.setDefaultButton(QMessageBox.Yes)
            
            reply = dialog.exec()
            
            # Save preference if "Always add" is checked
            if always_check.isChecked():
                config.set('armory.auto_add_scraped_items', True)
                config.save()
            
            if reply == QMessageBox.Yes:
                # Add items to personal database
                config_manager = ConfigManager()
                db_manager = ItemsDatabaseManager(config_manager, path_manager)
                
                added_count = 0
                realm = self.realm_combo.currentText()
                
                for item_data in self.imported_items:
                    success, message = db_manager.add_scraped_item(item_data, realm)
                    if success:
                        added_count += 1
                
                if added_count > 0:
                    QMessageBox.information(self,
                        lang.get("armory_import.import_finished_title", default="Import terminé"),
                        f"{added_count} items ajoutés à votre base de données personnelle")
                        
        except Exception as e:
            logging.error(f"Error asking to add scraped items: {e}", exc_info=True)
            
    def _on_item_selected(self):
        """Affiche les détails de l'item sélectionné"""
        selected_rows = self.items_table.selectedIndexes()
        if not selected_rows:
            self.details_text.clear()
            return
        
        row = selected_rows[0].row()
        if row >= len(self.imported_items):
            return
        
        item = self.imported_items[row]
        
        # Format details
        details = f"=== {item.get('name', 'N/A')} ===\n\n"
        details += f"ID: {item.get('id', 'N/A')}\n"
        details += f"Type: {item.get('type', 'N/A')}\n"
        details += f"Slot: {item.get('slot', 'N/A')}\n"
        details += f"Qualité: {item.get('quality', 'N/A')}%\n"
        details += f"Niveau: {item.get('level', 'N/A')}\n"
        details += f"Royaume: {item.get('realm', 'N/A')}\n"
        
        # Stats
        stats = item.get('stats', {})
        if stats:
            details += "\n--- Stats ---\n"
            for stat, value in stats.items():
                details += f"  {stat}: {value}\n"
        
        # Resistances
        resists = item.get('resistances', {})
        if resists:
            details += "\n--- Résistances ---\n"
            for resist, value in resists.items():
                details += f"  {resist}: {value}\n"
        
        # Bonuses
        bonuses = item.get('bonuses', {})
        if bonuses:
            details += "\n--- Bonus ---\n"
            for bonus, value in bonuses.items():
                details += f"  {bonus}: {value}\n"
        
        # Merchants
        merchants = item.get('merchants', [])
        if merchants:
            details += f"\n--- Marchands ({len(merchants)}) ---\n"
            for i, merchant in enumerate(merchants, 1):
                details += f"\n  Marchand #{i}:\n"
                details += f"    Nom: {merchant.get('name', 'N/A')}\n"
                details += f"    Zone: {merchant.get('zone', 'N/A')}\n"
                details += f"    Lieu: {merchant.get('zone_full', 'N/A')}\n"
                details += f"    Position: {merchant.get('location', 'N/A')}\n"
                
                price_parsed = merchant.get('price_parsed')
                if price_parsed:
                    details += f"    Prix: {price_parsed.get('display', 'N/A')}\n"
                    details += f"    Devise: {price_parsed.get('currency', 'N/A')}\n"
                else:
                    details += f"    Prix: {merchant.get('price', 'N/A')}\n"
        
        self.details_text.setPlainText(details)
    
    def _on_cell_clicked(self, row, column):
        """Gère le clic sur une cellule (ouvre l'URL si colonne ID)"""
        if column == 0:  # Colonne ID
            item = self.items_table.item(row, 0)
            if item:
                item_id = item.data(Qt.UserRole)
                if item_id and item_id != 'N/A':
                    url = f"https://eden-daoc.net/items?id={item_id}"
                    QDesktopServices.openUrl(QUrl(url))
        
    def _save_database(self):
        """Sauvegarde les items dans la base de données"""
        if not self.imported_items:
            return
        
        try:
            import json
            from datetime import datetime
            
            # Get armor path from config (user's Armory folder)
            armor_path = config.get('folders.armor')
            if not armor_path:
                QMessageBox.warning(
                    self,
                    lang.get("armory_import.path_not_configured_title", default="Chemin non configuré"),
                    lang.get("armory_import.path_not_configured_message", default="Veuillez configurer le chemin de l'armurerie dans les paramètres.")
                )
                return
            
            armor_path = Path(armor_path)
            armor_path.mkdir(parents=True, exist_ok=True)
            
            # Single database file for all realms
            db_file = armor_path / "items_database.json"
            
            # Load existing database if exists
            if db_file.exists():
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
            else:
                database = {
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'items': {}
                }
            
            # Add imported items (check by name AND id to handle cross-realm items)
            realm = self.realm_combo.currentText()
            for item in self.imported_items:
                item_id = str(item.get('id'))
                item_name = item.get('name', '').strip().lower()
                
                # Search for existing item by name first
                existing_key = None
                for key, existing_item in database['items'].items():
                    if existing_item.get('name', '').strip().lower() == item_name:
                        existing_key = key
                        break
                
                if existing_key:
                    # Item exists with same name (may have different ID per realm)
                    existing_realms = database['items'][existing_key].get('realms', {})
                    
                    # Store ID per realm (some items have different IDs per realm)
                    if realm not in existing_realms:
                        existing_realms[realm] = item_id
                    
                    database['items'][existing_key]['realms'] = existing_realms
                    
                    # Update other fields (keep most recent data)
                    database['items'][existing_key].update({
                        k: v for k, v in item.items() 
                        if k not in ['id', 'realm', 'realms']
                    })
                else:
                    # New item - use ID as key
                    item['realms'] = {realm: item_id}
                    # Remove single 'realm' field if exists
                    item.pop('realm', None)
                    database['items'][item_id] = item
            
            # Update metadata
            database['updated'] = datetime.now().isoformat()
            database['item_count'] = len(database['items'])
            
            # Save database
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            save_success_msg = lang.get("armory_import.save_success_message", default="Base de données sauvegardée")
            db_name = db_file.name
            QMessageBox.information(
                self,
                lang.get("armory_import.save_success_title", default="Sauvegarde réussie"),
                f"{save_success_msg}:\n\n"
                f"📁 {db_name}\n"
                f"📂 {db_file.parent}\n\n"
                f"✅ {len(self.imported_items)} items ajoutés/mis à jour"
            )
            
        except Exception as e:
            logging.error(f"Erreur sauvegarde database: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                lang.get("armory_import.save_error_title", default="Erreur de sauvegarde"),
                f"Impossible de sauvegarder la base de données:\n{str(e)}"
            )
            
    def _close_dialog(self):
        """Ferme le dialogue"""
        # Check if import is running
        if self.import_worker and self.import_worker.isRunning():
            reply = QMessageBox.question(
                self,
                lang.get("armory_import.import_in_progress_title", default="Import en cours"),
                lang.get("armory_import.import_in_progress_message", default="Un import est en cours. Voulez-vous vraiment fermer ?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.import_worker.terminate()
                self.import_worker.wait()
            else:
                return
        
        self.accept()
