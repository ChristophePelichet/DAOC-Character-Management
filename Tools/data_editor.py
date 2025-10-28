"""
DAOC Data Editor - Visual editor for JSON data files
Allows easy editing of classes, races, stats, and realm ranks
"""

import sys
import json
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QMessageBox, QFileDialog,
    QHeaderView, QGroupBox, QFormLayout, QListWidget, QSplitter,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class DataEditor(QMainWindow):
    """Main window for the DAOC Data Editor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DAOC Data Editor - Éditeur de données")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data storage
        self.classes_races_data = {}
        self.realm_ranks_data = {}
        self.data_modified = False
        self.realms_list = []  # Will be populated from JSON
        
        # Track currently edited class
        self.current_editing_realm = None
        self.current_editing_row = -1
        
        # File paths
        self.classes_races_file = Path("Data/classes_races.json")
        self.realm_ranks_files = {}  # Will be populated dynamically
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🎮 DAOC Data Editor")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_classes_races_tab()
        self.create_realm_ranks_tab()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Sauvegarder tout")
        self.save_button.clicked.connect(self.save_all_data)
        self.save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        button_layout.addWidget(self.save_button)
        
        self.reload_button = QPushButton("🔄 Recharger")
        self.reload_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.reload_button)
        
        self.close_button = QPushButton("❌ Fermer")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Prêt")
    
    def create_classes_races_tab(self):
        """Create the Classes & Races editor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Realm selector
        realm_layout = QHBoxLayout()
        realm_layout.addWidget(QLabel("Royaume :"))
        self.realm_combo = QComboBox()
        # Realms will be populated dynamically from JSON in load_data()
        self.realm_combo.currentTextChanged.connect(self.on_realm_changed)
        realm_layout.addWidget(self.realm_combo)
        realm_layout.addStretch()
        layout.addLayout(realm_layout)
        
        # Splitter for classes and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Classes list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("📋 Classes disponibles :"))
        
        self.classes_list = QListWidget()
        self.classes_list.currentRowChanged.connect(self.on_class_selected)
        left_layout.addWidget(self.classes_list)
        
        # Add/Remove class buttons
        class_buttons = QHBoxLayout()
        add_class_btn = QPushButton("➕ Ajouter")
        add_class_btn.clicked.connect(self.add_class)
        class_buttons.addWidget(add_class_btn)
        
        remove_class_btn = QPushButton("➖ Supprimer")
        remove_class_btn.clicked.connect(self.remove_class)
        class_buttons.addWidget(remove_class_btn)
        
        left_layout.addLayout(class_buttons)
        splitter.addWidget(left_widget)
        
        # Right: Class details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Class info group
        class_info_group = QGroupBox("📝 Informations de la classe")
        class_info_layout = QFormLayout()
        
        self.class_name_edit = QLineEdit()
        self.class_name_edit.textChanged.connect(self.mark_modified)
        class_info_layout.addRow("Nom (EN) :", self.class_name_edit)
        
        self.class_name_fr_edit = QLineEdit()
        self.class_name_fr_edit.textChanged.connect(self.mark_modified)
        class_info_layout.addRow("Nom (FR) :", self.class_name_fr_edit)
        
        self.class_name_de_edit = QLineEdit()
        self.class_name_de_edit.textChanged.connect(self.mark_modified)
        class_info_layout.addRow("Nom (DE) :", self.class_name_de_edit)
        
        class_info_group.setLayout(class_info_layout)
        right_layout.addWidget(class_info_group)
        
        # Races group
        races_group = QGroupBox("👤 Races disponibles")
        races_layout = QVBoxLayout()
        
        self.races_checkboxes = {}
        self.races_scroll = QWidget()
        self.races_scroll_layout = QVBoxLayout(self.races_scroll)
        
        # Races will be populated dynamically from JSON in populate_races_checkboxes()
        
        races_layout.addWidget(self.races_scroll)
        races_group.setLayout(races_layout)
        right_layout.addWidget(races_group)
        
        # Specializations group
        specs_group = QGroupBox("🎯 Spécialisations")
        specs_layout = QVBoxLayout()
        
        self.specs_text = QTextEdit()
        self.specs_text.setPlaceholderText(
            'Format JSON:\n[\n  {"name": "EN", "name_fr": "FR", "name_de": "DE"},\n  ...\n]'
        )
        self.specs_text.textChanged.connect(self.mark_modified)
        specs_layout.addWidget(self.specs_text)
        
        specs_group.setLayout(specs_layout)
        right_layout.addWidget(specs_group)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 900])
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "🎭 Classes & Races")
    
    def create_realm_ranks_tab(self):
        """Create the Realm Ranks editor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Realm selector
        realm_layout = QHBoxLayout()
        realm_layout.addWidget(QLabel("Royaume :"))
        self.ranks_realm_combo = QComboBox()
        # Realms will be populated dynamically from JSON in load_data()
        self.ranks_realm_combo.currentTextChanged.connect(self.on_ranks_realm_changed)
        realm_layout.addWidget(self.ranks_realm_combo)
        realm_layout.addStretch()
        layout.addLayout(realm_layout)
        
        # Table for ranks
        self.ranks_table = QTableWidget()
        self.ranks_table.setColumnCount(4)
        self.ranks_table.setHorizontalHeaderLabels(["Rank", "Level", "Realm Points", "Title"])
        self.ranks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ranks_table.itemChanged.connect(self.on_rank_item_changed)
        layout.addWidget(self.ranks_table)
        
        # Buttons
        ranks_buttons = QHBoxLayout()
        
        add_rank_btn = QPushButton("➕ Ajouter rang")
        add_rank_btn.clicked.connect(self.add_rank)
        ranks_buttons.addWidget(add_rank_btn)
        
        remove_rank_btn = QPushButton("➖ Supprimer rang")
        remove_rank_btn.clicked.connect(self.remove_rank)
        ranks_buttons.addWidget(remove_rank_btn)
        
        ranks_buttons.addStretch()
        layout.addLayout(ranks_buttons)
        
        self.tabs.addTab(tab, "🏆 Realm Ranks")
    
    def load_data(self):
        """Load all data from JSON files"""
        try:
            # Load classes & races
            if self.classes_races_file.exists():
                with open(self.classes_races_file, 'r', encoding='utf-8') as f:
                    self.classes_races_data = json.load(f)
                logging.info(f"Loaded classes & races data from {self.classes_races_file}")
                
                # Extract realms from JSON data
                self.realms_list = list(self.classes_races_data.keys())
                
                # Build realm_ranks_files dynamically based on realms found
                self.realm_ranks_files = {
                    realm: Path(f"Data/realm_ranks_{realm.lower()}.json")
                    for realm in self.realms_list
                }
            else:
                QMessageBox.warning(self, "Fichier manquant", 
                                    f"Le fichier {self.classes_races_file} n'existe pas.")
                # Fallback to default structure
                self.realms_list = ["Albion", "Hibernia", "Midgard"]
                self.classes_races_data = {realm: {"classes": [], "races": []} for realm in self.realms_list}
                self.realm_ranks_files = {
                    realm: Path(f"Data/realm_ranks_{realm.lower()}.json")
                    for realm in self.realms_list
                }
            
            # Update combo boxes with dynamic realms
            self.realm_combo.clear()
            self.realm_combo.addItems(self.realms_list)
            self.ranks_realm_combo.clear()
            self.ranks_realm_combo.addItems(self.realms_list)
            
            # Load realm ranks
            for realm, file_path in self.realm_ranks_files.items():
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.realm_ranks_data[realm] = json.load(f)
                    logging.info(f"Loaded realm ranks for {realm}")
                else:
                    self.realm_ranks_data[realm] = []
            
            # Populate races checkboxes dynamically
            self.populate_races_checkboxes()
            
            # Refresh UI
            self.on_realm_changed(self.realm_combo.currentText())
            self.on_ranks_realm_changed(self.ranks_realm_combo.currentText())
            
            self.data_modified = False
            self.statusBar().showMessage("Données chargées avec succès")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")
            logging.error(f"Error loading data: {e}")
    
    def populate_races_checkboxes(self):
        """Populate races checkboxes dynamically from all realms"""
        # Clear existing checkboxes
        for checkbox in self.races_checkboxes.values():
            checkbox.deleteLater()
        self.races_checkboxes.clear()
        
        # Collect all unique race names from all realms
        all_races = set()
        for realm_data in self.classes_races_data.values():
            if 'races' in realm_data:
                for race in realm_data['races']:
                    if isinstance(race, dict) and 'name' in race:
                        all_races.add(race['name'])
        
        # Create checkboxes for each unique race
        for race_name in sorted(all_races):
            checkbox = QCheckBox(race_name)
            checkbox.stateChanged.connect(self.mark_modified)
            self.races_checkboxes[race_name] = checkbox
            self.races_scroll_layout.addWidget(checkbox)
    
    def save_all_data(self):
        """Save all data to JSON files"""
        try:
            # Save current class if editing
            self.save_current_class()
            
            # Save classes & races
            with open(self.classes_races_file, 'w', encoding='utf-8') as f:
                json.dump(self.classes_races_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved classes & races to {self.classes_races_file}")
            
            # Save realm ranks
            for realm, file_path in self.realm_ranks_files.items():
                if realm in self.realm_ranks_data:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.realm_ranks_data[realm], f, ensure_ascii=False, indent=2)
                    logging.info(f"Saved realm ranks for {realm}")
            
            self.data_modified = False
            self.statusBar().showMessage("✅ Toutes les données ont été sauvegardées")
            QMessageBox.information(self, "Succès", "Toutes les données ont été sauvegardées avec succès !")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
            logging.error(f"Error saving data: {e}")
    
    def on_realm_changed(self, realm):
        """Called when realm changes in classes tab"""
        # Save current class before switching realm
        self.save_current_class()
        
        # Clear current editing state
        self.current_editing_realm = None
        self.current_editing_row = -1
        
        self.classes_list.clear()
        
        if realm in self.classes_races_data:
            realm_data = self.classes_races_data[realm]
            # Handle both old format (list) and new format (dict with 'classes' key)
            if isinstance(realm_data, dict) and 'classes' in realm_data:
                classes_list = realm_data['classes']
            elif isinstance(realm_data, list):
                classes_list = realm_data
            else:
                classes_list = []
            
            for class_info in classes_list:
                # Handle both dict and string formats
                if isinstance(class_info, dict):
                    class_name = class_info.get("name", "Unknown")
                else:
                    class_name = str(class_info)
                self.classes_list.addItem(class_name)
    
    def on_class_selected(self, row):
        """Called when a class is selected"""
        if row < 0:
            # Clear current editing state
            self.current_editing_realm = None
            self.current_editing_row = -1
            return
        
        # Save previous class first
        self.save_current_class()
        
        realm = self.realm_combo.currentText()
        if realm not in self.classes_races_data:
            return
        
        # Get classes list (handle both old and new format)
        realm_data = self.classes_races_data[realm]
        if isinstance(realm_data, dict) and 'classes' in realm_data:
            classes_list = realm_data['classes']
        elif isinstance(realm_data, list):
            classes_list = realm_data
        else:
            return
        
        if row >= len(classes_list):
            return
        
        # Store current editing context
        self.current_editing_realm = realm
        self.current_editing_row = row
        
        class_info = classes_list[row]
        
        # Convert to dict if it's a string (for backward compatibility)
        if not isinstance(class_info, dict):
            class_info = {
                "name": str(class_info),
                "name_fr": str(class_info),
                "name_de": str(class_info),
                "races": [],
                "specializations": []
            }
            classes_list[row] = class_info
        
        # Block signals while updating
        self.class_name_edit.blockSignals(True)
        self.class_name_fr_edit.blockSignals(True)
        self.class_name_de_edit.blockSignals(True)
        self.specs_text.blockSignals(True)
        
        # Update fields
        self.class_name_edit.setText(class_info.get("name", ""))
        self.class_name_fr_edit.setText(class_info.get("name_fr", ""))
        self.class_name_de_edit.setText(class_info.get("name_de", ""))
        
        # Update races checkboxes
        class_races = class_info.get("races", [])
        for race, checkbox in self.races_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(race in class_races)
            checkbox.blockSignals(False)
        
        # Update specializations
        specs = class_info.get("specializations", [])
        self.specs_text.setPlainText(json.dumps(specs, ensure_ascii=False, indent=2))
        
        # Unblock signals
        self.class_name_edit.blockSignals(False)
        self.class_name_fr_edit.blockSignals(False)
        self.class_name_de_edit.blockSignals(False)
        self.specs_text.blockSignals(False)
    
    def save_current_class(self):
        """Save currently edited class"""
        # Use stored values instead of current UI state
        if self.current_editing_row < 0 or self.current_editing_realm is None:
            return
        
        realm = self.current_editing_realm
        row = self.current_editing_row
        
        if realm not in self.classes_races_data:
            return
        
        # Get classes list (handle both old and new format)
        realm_data = self.classes_races_data[realm]
        if isinstance(realm_data, dict) and 'classes' in realm_data:
            classes_list = realm_data['classes']
        elif isinstance(realm_data, list):
            classes_list = realm_data
        else:
            return
        
        if row >= len(classes_list):
            return
        
        class_info = classes_list[row]
        
        # Convert to dict if it's a string
        if not isinstance(class_info, dict):
            class_info = {
                "name": "",
                "name_fr": "",
                "name_de": "",
                "races": [],
                "specializations": []
            }
            classes_list[row] = class_info
        
        # Update basic info
        class_info["name"] = self.class_name_edit.text()
        class_info["name_fr"] = self.class_name_fr_edit.text()
        class_info["name_de"] = self.class_name_de_edit.text()
        
        # Update races
        class_info["races"] = [race for race, checkbox in self.races_checkboxes.items() 
                               if checkbox.isChecked()]
        
        # Update specializations
        try:
            specs_text = self.specs_text.toPlainText()
            if specs_text.strip():
                class_info["specializations"] = json.loads(specs_text)
            else:
                class_info["specializations"] = []
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON for specializations: {e}")
    
    def add_class(self):
        """Add a new class"""
        realm = self.realm_combo.currentText()
        
        new_class = {
            "name": "NewClass",
            "name_fr": "NouvelleClasse",
            "name_de": "NeueKlasse",
            "races": [],
            "specializations": []
        }
        
        # Get classes list (handle both old and new format)
        realm_data = self.classes_races_data[realm]
        if isinstance(realm_data, dict) and 'classes' in realm_data:
            classes_list = realm_data['classes']
        elif isinstance(realm_data, list):
            classes_list = realm_data
        else:
            # Initialize as new format
            self.classes_races_data[realm] = {'classes': [], 'races': []}
            classes_list = self.classes_races_data[realm]['classes']
        
        classes_list.append(new_class)
        self.classes_list.addItem(new_class["name"])
        self.classes_list.setCurrentRow(self.classes_list.count() - 1)
        self.mark_modified()
    
    def remove_class(self):
        """Remove selected class"""
        row = self.classes_list.currentRow()
        if row < 0:
            return
        
        realm = self.realm_combo.currentText()
        
        # Get classes list (handle both old and new format)
        realm_data = self.classes_races_data[realm]
        if isinstance(realm_data, dict) and 'classes' in realm_data:
            classes_list = realm_data['classes']
        elif isinstance(realm_data, list):
            classes_list = realm_data
        else:
            return
        
        if row >= len(classes_list):
            return
        
        class_name = classes_list[row].get("name", "") if isinstance(classes_list[row], dict) else str(classes_list[row])
        
        reply = QMessageBox.question(
            self, "Confirmer",
            f"Supprimer la classe '{class_name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del classes_list[row]
            self.classes_list.takeItem(row)
            self.mark_modified()
    
    def on_ranks_realm_changed(self, realm):
        """Called when realm changes in ranks tab"""
        if realm not in self.realm_ranks_data:
            return
        
        ranks = self.realm_ranks_data[realm]
        
        self.ranks_table.blockSignals(True)
        self.ranks_table.setRowCount(len(ranks))
        
        for i, rank_info in enumerate(ranks):
            self.ranks_table.setItem(i, 0, QTableWidgetItem(str(rank_info.get("rank", ""))))
            self.ranks_table.setItem(i, 1, QTableWidgetItem(rank_info.get("level", "")))
            self.ranks_table.setItem(i, 2, QTableWidgetItem(str(rank_info.get("realm_points", ""))))
            self.ranks_table.setItem(i, 3, QTableWidgetItem(rank_info.get("title", "")))
        
        self.ranks_table.blockSignals(False)
    
    def on_rank_item_changed(self, item):
        """Called when a rank table item is changed"""
        row = item.row()
        col = item.column()
        realm = self.ranks_realm_combo.currentText()
        
        if realm not in self.realm_ranks_data or row >= len(self.realm_ranks_data[realm]):
            return
        
        rank_info = self.realm_ranks_data[realm][row]
        
        if col == 0:  # Rank
            try:
                rank_info["rank"] = int(item.text())
            except ValueError:
                pass
        elif col == 1:  # Level
            rank_info["level"] = item.text()
        elif col == 2:  # Realm Points
            try:
                rank_info["realm_points"] = int(item.text())
            except ValueError:
                pass
        elif col == 3:  # Title
            rank_info["title"] = item.text()
        
        self.mark_modified()
    
    def add_rank(self):
        """Add a new rank"""
        realm = self.ranks_realm_combo.currentText()
        
        new_rank = {
            "rank": 1,
            "level": "1L1",
            "realm_points": 0,
            "title": "New Rank"
        }
        
        self.realm_ranks_data[realm].append(new_rank)
        self.on_ranks_realm_changed(realm)
        self.mark_modified()
    
    def remove_rank(self):
        """Remove selected rank"""
        row = self.ranks_table.currentRow()
        if row < 0:
            return
        
        realm = self.ranks_realm_combo.currentText()
        
        reply = QMessageBox.question(
            self, "Confirmer",
            f"Supprimer ce rang ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.realm_ranks_data[realm][row]
            self.on_ranks_realm_changed(realm)
            self.mark_modified()
    
    def mark_modified(self):
        """Mark data as modified"""
        if not self.data_modified:
            self.data_modified = True
            self.statusBar().showMessage("⚠️ Données modifiées (non sauvegardées)")
    
    def closeEvent(self, event):
        """Called when window is closing"""
        if self.data_modified:
            reply = QMessageBox.question(
                self, "Modifications non sauvegardées",
                "Des modifications n'ont pas été sauvegardées. Voulez-vous quitter ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()


def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    editor = DataEditor()
    editor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
