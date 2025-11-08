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
        self.armor_resists_data = {}
        self.data_modified = False
        self.realms_list = []  # Will be populated from JSON
        
        # Mapping between realm names and armor table keys
        self.armor_table_mapping = {
            "Albion": "table_1",
            "Hibernia": "table_2",
            "Midgard": "table_3"
        }
        self.armor_table_reverse_mapping = {v: k for k, v in self.armor_table_mapping.items()}
        
        # Track currently edited class
        self.current_editing_realm = None
        self.current_editing_row = -1
        
        # File paths
        self.classes_races_file = Path("Data/classes_races.json")
        self.realm_ranks_file = Path("Data/realm_ranks.json")
        self.armor_resists_file = Path("Data/armor_resists.json")
        
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
        self.create_armor_resists_tab()
        
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
    
    def create_armor_resists_tab(self):
        """Create the Armor Resistances editor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info label
        info_label = QLabel("📊 Résistances d'armure par classe (EN / FR / DE)")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 10px;")
        layout.addWidget(info_label)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Realm selector
        controls_layout.addWidget(QLabel("Royaume :"))
        self.armor_table_combo = QComboBox()
        self.armor_table_combo.currentTextChanged.connect(self.on_armor_table_changed)
        controls_layout.addWidget(self.armor_table_combo)
        
        controls_layout.addStretch()
        
        # Language filter
        controls_layout.addWidget(QLabel("Afficher :"))
        self.armor_lang_filter = QComboBox()
        self.armor_lang_filter.addItems(["Toutes les langues", "EN seulement", "FR seulement", "DE seulement"])
        self.armor_lang_filter.currentTextChanged.connect(self.on_armor_lang_filter_changed)
        controls_layout.addWidget(self.armor_lang_filter)
        
        layout.addLayout(controls_layout)
        
        # Table for armor resists with all languages
        self.armor_table = QTableWidget()
        # 3 columns per field (EN, FR, DE) for Class and Armor Type
        # 3 columns per resist type (EN, FR, DE) for 9 resist types
        # Total: Class(3) + Armor Type(3) + 9 resists * 3 = 33 columns
        self.armor_table.setColumnCount(33)
        
        headers = []
        # Class columns
        headers.extend(["Class (EN)", "Classe (FR)", "Klasse (DE)"])
        # Armor Type columns
        headers.extend(["Armor Type (EN)", "Type d'armure (FR)", "Rüstungstyp (DE)"])
        # Resist columns (9 types x 3 languages)
        resist_types = [
            ("Thrust", "Perforation", "Stoß"),
            ("Crush", "Contondant", "Wucht"),
            ("Slash", "Tranchant", "Hieb"),
            ("Cold", "Froid", "Kälte"),
            ("Energy", "Énergie", "Energie"),
            ("Heat", "Chaleur", "Hitze"),
            ("Matter", "Matière", "Materie"),
            ("Spirit", "Esprit", "Geist"),
            ("Body", "Corps", "Körper")
        ]
        for en, fr, de in resist_types:
            headers.extend([f"{en} (EN)", f"{fr} (FR)", f"{de} (DE)"])
        
        self.armor_table.setHorizontalHeaderLabels(headers)
        self.armor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.armor_table.itemChanged.connect(self.on_armor_item_changed)
        layout.addWidget(self.armor_table)
        
        # Store column indices for easy access
        self.armor_column_mapping = {
            'Class': 0, 'Class_fr': 1, 'Class_de': 2,
            'Armor Type': 3, 'Armor Type_fr': 4, 'Armor Type_de': 5,
            'Thrust': 6, 'Thrust_fr': 7, 'Thrust_de': 8,
            'Crush': 9, 'Crush_fr': 10, 'Crush_de': 11,
            'Slash': 12, 'Slash_fr': 13, 'Slash_de': 14,
            'Cold': 15, 'Cold_fr': 16, 'Cold_de': 17,
            'Energy': 18, 'Energy_fr': 19, 'Energy_de': 20,
            'Heat': 21, 'Heat_fr': 22, 'Heat_de': 23,
            'Matter': 24, 'Matter_fr': 25, 'Matter_de': 26,
            'Spirit': 27, 'Spirit_fr': 28, 'Spirit_de': 29,
            'Body': 30, 'Body_fr': 31, 'Body_de': 32
        }
        
        # Buttons
        armor_buttons = QHBoxLayout()
        
        add_armor_btn = QPushButton("➕ Ajouter classe")
        add_armor_btn.clicked.connect(self.add_armor_class)
        armor_buttons.addWidget(add_armor_btn)
        
        remove_armor_btn = QPushButton("➖ Supprimer classe")
        remove_armor_btn.clicked.connect(self.remove_armor_class)
        armor_buttons.addWidget(remove_armor_btn)
        
        armor_buttons.addStretch()
        layout.addLayout(armor_buttons)
        
        self.tabs.addTab(tab, "🛡️ Résistances d'Armure")
    
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
            else:
                QMessageBox.warning(self, "Fichier manquant", 
                                    f"Le fichier {self.classes_races_file} n'existe pas.")
                # Fallback to default structure
                self.realms_list = ["Albion", "Hibernia", "Midgard"]
                self.classes_races_data = {realm: {"classes": [], "races": []} for realm in self.realms_list}
            
            # Update combo boxes with dynamic realms
            self.realm_combo.clear()
            self.realm_combo.addItems(self.realms_list)
            self.ranks_realm_combo.clear()
            self.ranks_realm_combo.addItems(self.realms_list)
            
            # Load realm ranks from single file
            if self.realm_ranks_file.exists():
                with open(self.realm_ranks_file, 'r', encoding='utf-8') as f:
                    self.realm_ranks_data = json.load(f)
                logging.info(f"Loaded realm ranks from {self.realm_ranks_file}")
            else:
                self.realm_ranks_data = {realm: [] for realm in self.realms_list}
                QMessageBox.warning(self, "Fichier manquant", 
                                    f"Le fichier {self.realm_ranks_file} n'existe pas.")
            
            # Load armor resistances
            if self.armor_resists_file.exists():
                with open(self.armor_resists_file, 'r', encoding='utf-8') as f:
                    self.armor_resists_data = json.load(f)
                logging.info(f"Loaded armor resists from {self.armor_resists_file}")
                
                # Populate armor table combo with realm names instead of table keys
                self.armor_table_combo.clear()
                if 'tables' in self.armor_resists_data:
                    # Add realms in order: Albion, Hibernia, Midgard
                    for realm in ["Albion", "Hibernia", "Midgard"]:
                        table_key = self.armor_table_mapping.get(realm)
                        if table_key and table_key in self.armor_resists_data['tables']:
                            self.armor_table_combo.addItem(realm)
            else:
                self.armor_resists_data = {"armor_types": [], "resist_types": [], "tables": {}}
                QMessageBox.warning(self, "Fichier manquant", 
                                    f"Le fichier {self.armor_resists_file} n'existe pas.")
            
            # Populate races checkboxes dynamically
            self.populate_races_checkboxes()
            
            # Refresh UI
            self.on_realm_changed(self.realm_combo.currentText())
            self.on_ranks_realm_changed(self.ranks_realm_combo.currentText())
            if self.armor_table_combo.count() > 0:
                self.on_armor_table_changed(self.armor_table_combo.currentText())
            
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
            
            # Save realm ranks to single file
            with open(self.realm_ranks_file, 'w', encoding='utf-8') as f:
                json.dump(self.realm_ranks_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved realm ranks to {self.realm_ranks_file}")
            
            # Save armor resistances
            with open(self.armor_resists_file, 'w', encoding='utf-8') as f:
                json.dump(self.armor_resists_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved armor resists to {self.armor_resists_file}")
            
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
    
    def on_armor_table_changed(self, realm_name):
        """Called when armor realm selection changes"""
        if not realm_name or 'tables' not in self.armor_resists_data:
            return
        
        # Convert realm name to table key
        table_key = self.armor_table_mapping.get(realm_name)
        if not table_key or table_key not in self.armor_resists_data['tables']:
            return
        
        table_data = self.armor_resists_data['tables'][table_key]
        data_rows = table_data.get('data', [])
        
        self.armor_table.blockSignals(True)
        self.armor_table.setRowCount(len(data_rows))
        
        for i, row_data in enumerate(data_rows):
            # Class (EN, FR, DE)
            self.armor_table.setItem(i, 0, QTableWidgetItem(row_data.get("Class", "")))
            self.armor_table.setItem(i, 1, QTableWidgetItem(row_data.get("Class_fr", "")))
            self.armor_table.setItem(i, 2, QTableWidgetItem(row_data.get("Class_de", "")))
            
            # Armor Type (EN, FR, DE)
            self.armor_table.setItem(i, 3, QTableWidgetItem(row_data.get("Armor Type", "")))
            self.armor_table.setItem(i, 4, QTableWidgetItem(row_data.get("Armor Type_fr", "")))
            self.armor_table.setItem(i, 5, QTableWidgetItem(row_data.get("Armor Type_de", "")))
            
            # Resist types (EN, FR, DE for each)
            resist_keys = ['Thrust', 'Crush', 'Slash', 'Cold', 'Energy', 'Heat', 'Matter', 'Spirit', 'Body']
            col = 6
            for key in resist_keys:
                self.armor_table.setItem(i, col, QTableWidgetItem(row_data.get(key, "")))
                self.armor_table.setItem(i, col + 1, QTableWidgetItem(row_data.get(f"{key}_fr", "")))
                self.armor_table.setItem(i, col + 2, QTableWidgetItem(row_data.get(f"{key}_de", "")))
                col += 3
        
        self.armor_table.blockSignals(False)
        
        # Apply language filter if any
        self.on_armor_lang_filter_changed(self.armor_lang_filter.currentText())
    
    def on_armor_lang_filter_changed(self, filter_text):
        """Called when language filter changes"""
        if not hasattr(self, 'armor_table'):
            return
        
        # Show/hide columns based on filter
        if filter_text == "EN seulement":
            # Show only EN columns (0, 3, 6, 9, 12, ...)
            for col in range(self.armor_table.columnCount()):
                if col % 3 == 0:  # EN columns
                    self.armor_table.setColumnHidden(col, False)
                else:  # FR and DE columns
                    self.armor_table.setColumnHidden(col, True)
        elif filter_text == "FR seulement":
            # Show only FR columns (1, 4, 7, 10, 13, ...)
            for col in range(self.armor_table.columnCount()):
                if col % 3 == 1:  # FR columns
                    self.armor_table.setColumnHidden(col, False)
                else:  # EN and DE columns
                    self.armor_table.setColumnHidden(col, True)
        elif filter_text == "DE seulement":
            # Show only DE columns (2, 5, 8, 11, 14, ...)
            for col in range(self.armor_table.columnCount()):
                if col % 3 == 2:  # DE columns
                    self.armor_table.setColumnHidden(col, False)
                else:  # EN and FR columns
                    self.armor_table.setColumnHidden(col, True)
        else:  # "Toutes les langues"
            # Show all columns
            for col in range(self.armor_table.columnCount()):
                self.armor_table.setColumnHidden(col, False)
    
    def on_armor_item_changed(self, item):
        """Called when an armor table item is changed"""
        row = item.row()
        col = item.column()
        realm_name = self.armor_table_combo.currentText()
        
        # Convert realm name to table key
        table_key = self.armor_table_mapping.get(realm_name)
        if not table_key or 'tables' not in self.armor_resists_data:
            return
        
        if table_key not in self.armor_resists_data['tables']:
            return
        
        table_data = self.armor_resists_data['tables'][table_key]
        data_rows = table_data.get('data', [])
        
        if row >= len(data_rows):
            return
        
        row_data = data_rows[row]
        
        # Find which field was changed using reverse mapping
        field_name = None
        for key, col_idx in self.armor_column_mapping.items():
            if col_idx == col:
                field_name = key
                break
        
        if field_name:
            row_data[field_name] = item.text()
            self.mark_modified()
    
    def add_armor_class(self):
        """Add a new armor class entry"""
        realm_name = self.armor_table_combo.currentText()
        
        # Convert realm name to table key
        table_key = self.armor_table_mapping.get(realm_name)
        if not table_key or 'tables' not in self.armor_resists_data:
            QMessageBox.warning(self, "Erreur", "Aucun royaume sélectionné")
            return
        
        if table_key not in self.armor_resists_data['tables']:
            return
        
        new_entry = {
            "Class": "NewClass",
            "Class_fr": "NouvelleClasse",
            "Class_de": "NeueKlasse",
            "Armor Type": "Unknown",
            "Armor Type_fr": "Inconnu",
            "Armor Type_de": "Unbekannt",
            "Thrust": "Neutral",
            "Thrust_fr": "Neutre",
            "Thrust_de": "Neutral",
            "Crush": "Neutral",
            "Crush_fr": "Neutre",
            "Crush_de": "Neutral",
            "Slash": "Neutral",
            "Slash_fr": "Neutre",
            "Slash_de": "Neutral",
            "Cold": "Neutral",
            "Cold_fr": "Neutre",
            "Cold_de": "Neutral",
            "Energy": "Neutral",
            "Energy_fr": "Neutre",
            "Energy_de": "Neutral",
            "Heat": "Neutral",
            "Heat_fr": "Neutre",
            "Heat_de": "Neutral",
            "Matter": "Neutral",
            "Matter_fr": "Neutre",
            "Matter_de": "Neutral",
            "Spirit": "Neutral",
            "Spirit_fr": "Neutre",
            "Spirit_de": "Neutral",
            "Body": "Neutral",
            "Body_fr": "Neutre",
            "Body_de": "Neutral"
        }
        
        self.armor_resists_data['tables'][table_key]['data'].append(new_entry)
        self.on_armor_table_changed(realm_name)
        self.mark_modified()
    
    def remove_armor_class(self):
        """Remove selected armor class entry"""
        row = self.armor_table.currentRow()
        if row < 0:
            return
        
        realm_name = self.armor_table_combo.currentText()
        
        # Convert realm name to table key
        table_key = self.armor_table_mapping.get(realm_name)
        if not table_key or 'tables' not in self.armor_resists_data:
            return
        
        if table_key not in self.armor_resists_data['tables']:
            return
        
        table_data = self.armor_resists_data['tables'][table_key]
        data_rows = table_data.get('data', [])
        
        if row >= len(data_rows):
            return
        
        class_name = data_rows[row].get("Class", "")
        
        reply = QMessageBox.question(
            self, "Confirmer",
            f"Supprimer la classe '{class_name}' de {realm_name} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del data_rows[row]
            self.on_armor_table_changed(realm_name)
            self.mark_modified()
    
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