"""
Template Preview Dialog - Affiche un aperçu détaillé d'un template
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QFormLayout, QSplitter, QWidget,
    QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager
from Functions.items_database_manager import ItemsDatabaseManager


class TemplatePreviewDialog(QDialog):
    """
    Dialogue pour prévisualiser un template avant de le charger.
    Affiche métadonnées, liste d'items et statistiques.
    """
    
    def __init__(self, parent, template_name, metadata):
        super().__init__(parent)
        
        self.template_name = template_name
        self.metadata = metadata
        self.template_manager = TemplateManager()
        self.db_manager = ItemsDatabaseManager()
        
        # Track owned items
        self.items_data = []  # List of {name, price, currency, owned}
        self.currency_totals = defaultdict(lambda: {"total": 0, "owned": 0, "missing": 0})
        
        self.setWindowTitle(
            lang.get("template_preview.window_title", default="Aperçu du template - {name}").format(
                name=template_name
            )
        )
        self.resize(900, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self._setup_ui()
        self._load_template_content()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Splitter for metadata and items
        splitter = QSplitter(Qt.Vertical)
        
        # === Metadata Group ===
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        
        metadata_group = QGroupBox(lang.get("template_preview.metadata_group", default="📋 Informations"))
        metadata_form = QFormLayout()
        
        # Class
        metadata_form.addRow(
            lang.get("template_preview.label_class", default="Classe:"),
            QLabel(f"<b>{self.metadata.character_class}</b> ({self.metadata.class_fr} / {self.metadata.class_de})")
        )
        
        # Realm
        metadata_form.addRow(
            lang.get("template_preview.label_realm", default="Royaume:"),
            QLabel(f"<b>{self.metadata.realm}</b>")
        )
        
        # Season
        metadata_form.addRow(
            lang.get("template_preview.label_season", default="Saison:"),
            QLabel(f"<b>{self.metadata.season}</b>")
        )
        
        # Description
        metadata_form.addRow(
            lang.get("template_preview.label_description", default="Description:"),
            QLabel(self.metadata.description)
        )
        
        # Tags
        if self.metadata.tags:
            tags_str = " • ".join([f"<span style='background:#2196F3; color:white; padding:2px 6px; border-radius:8px; font-size:10px;'>{tag}</span>" for tag in self.metadata.tags])
            tags_label = QLabel(tags_str)
            tags_label.setTextFormat(Qt.RichText)
            metadata_form.addRow(
                lang.get("template_preview.label_tags", default="Tags:"),
                tags_label
            )
        
        # Source file
        metadata_form.addRow(
            lang.get("template_preview.label_source", default="Fichier source:"),
            QLabel(f"<i>{self.metadata.source_file}</i>")
        )
        
        # Imported by
        metadata_form.addRow(
            lang.get("template_preview.label_imported_by", default="Importé par:"),
            QLabel(self.metadata.imported_by_character)
        )
        
        # Import date
        import_date = datetime.fromisoformat(self.metadata.import_date).strftime("%d/%m/%Y %H:%M")
        metadata_form.addRow(
            lang.get("template_preview.label_import_date", default="Date d'import:"),
            QLabel(import_date)
        )
        
        # Notes
        if self.metadata.notes:
            notes_label = QLabel(self.metadata.notes)
            notes_label.setWordWrap(True)
            metadata_form.addRow(
                lang.get("template_preview.label_notes", default="Notes:"),
                notes_label
            )
        
        metadata_group.setLayout(metadata_form)
        metadata_layout.addWidget(metadata_group)
        
        # === Stats Group ===
        stats_group = QGroupBox(lang.get("template_preview.stats_group", default="📊 Statistiques"))
        stats_form = QFormLayout()
        
        stats_form.addRow(
            lang.get("template_preview.stats_total_items", default="Total items:"),
            QLabel(f"<b>{self.metadata.item_count}</b>")
        )
        
        # TODO: Add slots covered count when template content is parsed
        
        stats_group.setLayout(stats_form)
        metadata_layout.addWidget(stats_group)
        
        # === Currency Summary Group ===
        self.currency_group = QGroupBox(lang.get("template_preview.currency_group", default="💰 Résumé des devises"))
        self.currency_layout = QVBoxLayout()
        self.currency_labels = {}  # Will store labels for each currency
        self.currency_group.setLayout(self.currency_layout)
        metadata_layout.addWidget(self.currency_group)
        
        splitter.addWidget(metadata_widget)
        
        # === Items List Group ===
        items_group = QGroupBox(
            lang.get("template_preview.items_group", default="📦 Items ({count})").format(
                count=self.metadata.item_count
            )
        )
        items_layout = QVBoxLayout()
        
        # Table with checkboxes
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            lang.get("template_preview.col_owned", default="✓"),
            lang.get("template_preview.col_item", default="Item"),
            lang.get("template_preview.col_price", default="Prix"),
            lang.get("template_preview.col_currency", default="Devise"),
            lang.get("template_preview.col_zone", default="Zone")
        ])
        
        # Column widths
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Item name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Currency
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Zone
        
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        splitter.addWidget(items_group)
        
        layout.addWidget(splitter)
        
        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton(lang.get("template_preview.button_close", default="Fermer"))
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)
        
        load_button = QPushButton(lang.get("template_preview.button_load", default="📥 Charger ce template"))
        load_button.setMinimumWidth(150)
        load_button.setMinimumHeight(35)
        load_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        load_button.clicked.connect(self.accept)
        button_layout.addWidget(load_button)
        
        layout.addLayout(button_layout)
    
    def _load_template_content(self):
        """Load and display template file content with prices from template JSON or database"""
        try:
            template_file = self.template_manager.armory_path / self.metadata.realm / self.template_name
            
            if not template_file.exists():
                # Try without realm subdirectory (old format)
                template_file = self.template_manager.armory_path / self.template_name
            
            # Load template JSON metadata for prices
            json_file = template_file.parent / "Json" / f"{template_file.name}.json"
            if not json_file.exists():
                # Try old location (same folder as template)
                json_file = template_file.with_suffix('.txt.json')
            
            template_prices = {}
            if json_file.exists():
                import json
                with open(json_file, 'r', encoding='utf-8') as f:
                    template_json = json.load(f)
                    template_prices = template_json.get('prices', {})
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract items (one per line)
                items = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Populate table with items and prices
                self.items_table.setRowCount(len(items))
                
                for i, item_name in enumerate(items):
                    # Build cache key for template prices
                    cache_key = f"{item_name}:{self.metadata.realm}"
                    
                    # Extract price info - PRIORITY: Template JSON > Database
                    price = "?"
                    currency = "?"
                    zone = "?"
                    source = None  # Track where price comes from
                    
                    # 1. Check template JSON prices FIRST
                    if cache_key in template_prices:
                        price_data = template_prices[cache_key]
                        price = price_data.get('price', '?')
                        currency = price_data.get('currency', '?')
                        zone = price_data.get('zone', '?')
                        source = 'template_json'
                    
                    # 2. If not in template JSON, search database
                    if price == '?' or currency == '?':
                        item_data = self.db_manager.search_item(item_name, self.metadata.realm)
                        
                        if not item_data:
                            # Try "All" realm if not found
                            item_data = self.db_manager.search_item(item_name, "All")
                        
                        if item_data:
                            price = item_data.get('merchant_price', '?')
                            currency = item_data.get('merchant_currency', '?')
                            zone = item_data.get('merchant_zone', '?')
                            source = 'database'
                    
                    # Store item data
                    item_info = {
                        'name': item_name,
                        'price': price,
                        'currency': currency,
                        'zone': zone,
                        'owned': False,
                        'source': source  # For debugging
                    }
                    self.items_data.append(item_info)
                    
                    # Add to currency totals
                    if price != '?' and currency != '?':
                        try:
                            price_int = int(price)
                            self.currency_totals[currency]["total"] += price_int
                            self.currency_totals[currency]["missing"] += price_int
                        except ValueError:
                            pass
                    
                    # Checkbox column
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)
                    checkbox.stateChanged.connect(lambda state, row=i: self._on_checkbox_changed(row, state))
                    checkbox_widget = QWidget()
                    checkbox_layout = QHBoxLayout(checkbox_widget)
                    checkbox_layout.addWidget(checkbox)
                    checkbox_layout.setAlignment(Qt.AlignCenter)
                    checkbox_layout.setContentsMargins(0, 0, 0, 0)
                    self.items_table.setCellWidget(i, 0, checkbox_widget)
                    
                    # Item name
                    name_item = QTableWidgetItem(item_name)
                    name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                    self.items_table.setItem(i, 1, name_item)
                    
                    # Price
                    price_item = QTableWidgetItem(price)
                    price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.items_table.setItem(i, 2, price_item)
                    
                    # Currency
                    currency_item = QTableWidgetItem(currency)
                    currency_item.setFlags(currency_item.flags() & ~Qt.ItemIsEditable)
                    self.items_table.setItem(i, 3, currency_item)
                    
                    # Zone
                    zone_item = QTableWidgetItem(zone)
                    zone_item.setFlags(zone_item.flags() & ~Qt.ItemIsEditable)
                    self.items_table.setItem(i, 4, zone_item)
                
                # Update currency summary
                self._update_currency_summary()
            
            else:
                self.items_table.setRowCount(1)
                error_item = QTableWidgetItem("⚠️ Fichier template introuvable")
                self.items_table.setItem(0, 1, error_item)
        
        except Exception as e:
            self.items_table.setRowCount(1)
            error_item = QTableWidgetItem(f"❌ Erreur de lecture: {e}")
            self.items_table.setItem(0, 1, error_item)
    
    def _on_checkbox_changed(self, row, state):
        """Handle checkbox state change"""
        item_info = self.items_data[row]
        item_info['owned'] = (state == Qt.Checked)
        
        # Update currency totals
        price = item_info['price']
        currency = item_info['currency']
        
        if price != '?' and currency != '?':
            try:
                price_int = int(price)
                if item_info['owned']:
                    self.currency_totals[currency]["owned"] += price_int
                    self.currency_totals[currency]["missing"] -= price_int
                else:
                    self.currency_totals[currency]["owned"] -= price_int
                    self.currency_totals[currency]["missing"] += price_int
            except ValueError:
                pass
        
        # Update display
        self._update_currency_summary()
    
    def _update_currency_summary(self):
        """Update the currency summary display"""
        # Clear existing labels
        while self.currency_layout.count():
            child = self.currency_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Sort currencies by total descending
        sorted_currencies = sorted(
            self.currency_totals.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        
        if not sorted_currencies:
            no_prices = QLabel(lang.get("template_preview.no_prices", default="Aucun prix disponible"))
            no_prices.setStyleSheet("color: gray; font-style: italic;")
            self.currency_layout.addWidget(no_prices)
        else:
            for currency, amounts in sorted_currencies:
                # Create layout for this currency
                currency_widget = QWidget()
                currency_h_layout = QHBoxLayout(currency_widget)
                currency_h_layout.setContentsMargins(5, 2, 5, 2)
                
                # Currency name
                currency_label = QLabel(f"<b>{currency}:</b>")
                currency_label.setMinimumWidth(100)
                currency_h_layout.addWidget(currency_label)
                
                # Total
                total_label = QLabel(lang.get("template_preview.currency_total", default="Total: {total}").format(total=amounts["total"]))
                total_label.setMinimumWidth(120)
                currency_h_layout.addWidget(total_label)
                
                # Owned (green)
                owned_label = QLabel(lang.get("template_preview.currency_owned", default="Possédé: {owned}").format(owned=amounts["owned"]))
                owned_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                owned_label.setMinimumWidth(120)
                currency_h_layout.addWidget(owned_label)
                
                # Missing (red)
                missing_label = QLabel(lang.get("template_preview.currency_missing", default="Manquant: {missing}").format(missing=amounts["missing"]))
                missing_label.setStyleSheet("color: #F44336; font-weight: bold;")
                missing_label.setMinimumWidth(130)
                currency_h_layout.addWidget(missing_label)
                
                currency_h_layout.addStretch()
                
                self.currency_layout.addWidget(currency_widget)
