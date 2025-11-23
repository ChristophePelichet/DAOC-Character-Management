"""
Database Editor Dialog - Direct editing of items_database_src.json

Provides a comprehensive interface for editing the internal items database with:
- Item list with search/filter
- Detailed editor with all fields
- Validation and error prevention
- Auto-backup before modifications
- Undo/Redo support
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QTextEdit, QMessageBox, QSplitter,
    QHeaderView, QCheckBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from Functions.language_manager import lang


class DatabaseEditorDialog(QDialog):
    """Dialog for editing items_database_src.json"""
    
    # Signal emitted when database is modified
    database_modified = Signal()
    
    def __init__(self, parent=None, path_manager=None):
        super().__init__(parent)
        self.path_manager = path_manager
        self.db_path = Path("Data/items_database_src.json")
        self.database = {}
        self.current_item_key = None
        self.modified = False
        self.undo_stack = []
        self.redo_stack = []
        
        # Field definitions for item schema
        self.field_definitions = {
            "id": {"type": "string", "required": True, "label": "Eden ID"},
            "name": {"type": "string", "required": True, "label": "Item Name"},
            "realm": {"type": "combo", "required": True, "label": "Realm", 
                     "values": ["Albion", "Hibernia", "Midgard", "All"]},
            "slot": {"type": "string", "required": True, "label": "Slot"},
            "type": {"type": "string", "required": False, "label": "Type"},
            "model": {"type": "string", "required": False, "label": "Model ID"},
            "dps": {"type": "string", "required": False, "label": "DPS"},
            "speed": {"type": "string", "required": False, "label": "Speed"},
            "damage_type": {"type": "string", "required": False, "label": "Damage Type"},
            "usable_by": {"type": "string", "required": True, "label": "Usable By"},
            "merchant_zone": {"type": "string", "required": False, "label": "Merchant Zone"},
            "merchant_price": {"type": "string", "required": False, "label": "Merchant Price"},
            "merchant_currency": {"type": "string", "required": False, "label": "Merchant Currency"},
            "item_category": {"type": "combo", "required": False, "label": "Category",
                             "values": ["", "quest_reward", "event_reward", "unknown"]},
            "ignore_item": {"type": "bool", "required": False, "label": "Ignore Item"},
            "source": {"type": "combo", "required": True, "label": "Source",
                      "values": ["internal", "user", "scraped"]}
        }
        
        self._init_ui()
        self._load_database()
        
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(lang.get('db_editor.window_title', default="🗄️ Database Editor - items_database_src.json"))
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        main_layout = QVBoxLayout(self)
        
        # === HEADER ===
        header_layout = QHBoxLayout()
        
        title = QLabel(lang.get('db_editor.title', default="🗄️ Database Editor"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Database info
        self.db_info_label = QLabel("")
        self.db_info_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self.db_info_label)
        
        main_layout.addLayout(header_layout)
        
        # === WARNING ===
        warning = QLabel(lang.get('db_editor.warning', 
            default="⚠️ Direct modification of internal database - Changes are immediate and permanent"))
        warning.setStyleSheet("background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 4px; font-weight: bold;")
        warning.setWordWrap(True)
        main_layout.addWidget(warning)
        main_layout.addSpacing(10)
        
        # === TOOLBAR ===
        toolbar_layout = QHBoxLayout()
        
        # Search
        search_label = QLabel(lang.get('db_editor.search_label', default="🔍 Search:"))
        toolbar_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(lang.get('db_editor.search_placeholder', 
            default="Item name, ID, or realm..."))
        self.search_input.textChanged.connect(self._filter_items)
        self.search_input.setMaximumWidth(300)
        toolbar_layout.addWidget(self.search_input)
        
        # Realm filter
        realm_label = QLabel(lang.get('db_editor.realm_label', default="Realm:"))
        toolbar_layout.addWidget(realm_label)
        
        self.realm_filter = QComboBox()
        self.realm_filter.addItems(["All", "Albion", "Hibernia", "Midgard"])
        self.realm_filter.currentTextChanged.connect(self._filter_items)
        self.realm_filter.setMaximumWidth(150)
        toolbar_layout.addWidget(self.realm_filter)
        
        # Category filter
        category_label = QLabel(lang.get('db_editor.category_label', default="Category:"))
        toolbar_layout.addWidget(category_label)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            lang.get('db_editor.filter_all', default="All"),
            lang.get('db_editor.filter_has_price', default="Has Price"),
            lang.get('db_editor.filter_no_price', default="No Price"),
            lang.get('db_editor.filter_quest_reward', default="Quest Reward"),
            lang.get('db_editor.filter_event_reward', default="Event Reward"),
            lang.get('db_editor.filter_unknown', default="Unknown")
        ])
        self.category_filter.currentTextChanged.connect(self._filter_items)
        self.category_filter.setMaximumWidth(150)
        toolbar_layout.addWidget(self.category_filter)
        
        toolbar_layout.addStretch()
        
        # Add Item button
        add_item_btn = QPushButton(lang.get('db_editor.add_item_button', default="➕ Add Item"))
        add_item_btn.clicked.connect(self._add_new_item)
        toolbar_layout.addWidget(add_item_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # === SPLITTER: Items List + Editor ===
        splitter = QSplitter(Qt.Horizontal)
        
        # === LEFT: Items Table ===
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        table_label = QLabel(lang.get('db_editor.items_list_label', default="📋 Items List"))
        table_label_font = table_label.font()
        table_label_font.setBold(True)
        table_label.setFont(table_label_font)
        left_layout.addWidget(table_label)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            lang.get('db_editor.column_key', default="Key"),
            lang.get('db_editor.column_name', default="Name"),
            lang.get('db_editor.column_realm', default="Realm"),
            lang.get('db_editor.column_slot', default="Slot"),
            lang.get('db_editor.column_price', default="Price")
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setSelectionMode(QTableWidget.SingleSelection)
        self.items_table.itemSelectionChanged.connect(self._on_item_selected)
        left_layout.addWidget(self.items_table)
        
        # Item count
        self.item_count_label = QLabel(lang.get('db_editor.items_count', default="0 items"))
        self.item_count_label.setStyleSheet("color: #666;")
        left_layout.addWidget(self.item_count_label)
        
        splitter.addWidget(left_widget)
        
        # === RIGHT: Item Editor ===
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        editor_label = QLabel(lang.get('db_editor.item_editor_label', default="✏️ Item Editor"))
        editor_label_font = editor_label.font()
        editor_label_font.setBold(True)
        editor_label.setFont(editor_label_font)
        right_layout.addWidget(editor_label)
        
        # Editor form (scrollable)
        from PySide6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        editor_widget = QFrame()
        self.editor_form = QFormLayout(editor_widget)
        self.editor_form.setLabelAlignment(Qt.AlignRight)
        
        # Create input widgets for each field
        self.field_widgets = {}
        for field_name, field_def in self.field_definitions.items():
            label_text = field_def["label"]
            if field_def["required"]:
                label_text += " *"
            
            if field_def["type"] == "combo":
                widget = QComboBox()
                widget.addItems(field_def["values"])
            elif field_def["type"] == "bool":
                widget = QCheckBox()
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(lang.get('db_editor.enter_field_placeholder', 
                    default="Enter {field}...").replace('{field}', field_def['label'].lower()))
            
            self.field_widgets[field_name] = widget
            self.editor_form.addRow(label_text + ":", widget)
        
        scroll_area.setWidget(editor_widget)
        right_layout.addWidget(scroll_area)
        
        # Editor buttons
        editor_buttons_layout = QHBoxLayout()
        
        self.save_item_btn = QPushButton(lang.get('db_editor.save_item_button', default="💾 Save Item"))
        self.save_item_btn.clicked.connect(self._save_current_item)
        self.save_item_btn.setEnabled(False)
        editor_buttons_layout.addWidget(self.save_item_btn)
        
        self.delete_item_btn = QPushButton(lang.get('db_editor.delete_item_button', default="🗑️ Delete Item"))
        self.delete_item_btn.clicked.connect(self._delete_current_item)
        self.delete_item_btn.setEnabled(False)
        self.delete_item_btn.setStyleSheet("background-color: #f44336; color: white;")
        editor_buttons_layout.addWidget(self.delete_item_btn)
        
        editor_buttons_layout.addStretch()
        
        right_layout.addLayout(editor_buttons_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 700])  # Initial sizes
        
        main_layout.addWidget(splitter, 1)
        
        # === BOTTOM: Action Buttons ===
        bottom_layout = QHBoxLayout()
        
        # Undo/Redo
        self.undo_btn = QPushButton(lang.get('db_editor.undo_button', default="↶ Undo"))
        self.undo_btn.clicked.connect(self._undo)
        self.undo_btn.setEnabled(False)
        bottom_layout.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton(lang.get('db_editor.redo_button', default="↷ Redo"))
        self.redo_btn.clicked.connect(self._redo)
        self.redo_btn.setEnabled(False)
        bottom_layout.addWidget(self.redo_btn)
        
        bottom_layout.addStretch()
        
        # Reload database
        reload_btn = QPushButton(lang.get('db_editor.reload_button', default="🔄 Reload Database"))
        reload_btn.clicked.connect(self._reload_database)
        bottom_layout.addWidget(reload_btn)
        
        # Close button
        close_btn = QPushButton(lang.get('db_editor.close_button', default="✖ Close"))
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        
        main_layout.addLayout(bottom_layout)
        
    def _load_database(self):
        """Load the database from JSON file"""
        try:
            if not self.db_path.exists():
                QMessageBox.critical(self, lang.get('error_title', default="Error"), 
                    lang.get('db_editor.db_not_found', default="Database file not found:\n{path}").replace('{path}', str(self.db_path)))
                return
            
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
            
            # Update UI
            item_count = self.database.get('item_count', len(self.database.get('items', {})))
            last_updated = self.database.get('last_updated', 'Unknown')
            self.db_info_label.setText(f"Items: {item_count} | Last updated: {last_updated}")
            
            self._populate_table()
            
            logging.info(f"Database loaded: {item_count} items", extra={"action": "DBEDITOR"})
            
        except Exception as e:
            logging.error(f"Error loading database: {e}", exc_info=True, extra={"action": "DBEDITOR"})
            QMessageBox.critical(self, lang.get('error_title', default="Error"), 
                lang.get('db_editor.load_error', default="Failed to load database:\n{error}").replace('{error}', str(e)))
    
    def _populate_table(self):
        """Populate the items table with database content"""
        self.items_table.setRowCount(0)
        
        items = self.database.get('items', {})
        
        for key, item in items.items():
            self._add_table_row(key, item)
        
        self.item_count_label.setText(lang.get('db_editor.items_count_value', default="{count} items").replace('{count}', str(len(items))))
    
    def _add_table_row(self, key: str, item: Dict[str, Any]):
        """Add a row to the items table"""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Key
        key_item = QTableWidgetItem(key)
        key_item.setData(Qt.UserRole, key)  # Store key for later retrieval
        self.items_table.setItem(row, 0, key_item)
        
        # Name
        self.items_table.setItem(row, 1, QTableWidgetItem(item.get('name', '')))
        
        # Realm
        self.items_table.setItem(row, 2, QTableWidgetItem(item.get('realm', '')))
        
        # Slot
        self.items_table.setItem(row, 3, QTableWidgetItem(item.get('slot', '')))
        
        # Price
        price = item.get('merchant_price', '')
        currency = item.get('merchant_currency', '')
        price_text = f"{price} {currency}" if price and currency else ""
        if not price_text and item.get('item_category'):
            # Show category icon
            category = item.get('item_category')
            category_icons = {
                'quest_reward': '🏆',
                'event_reward': '🎉',
                'unknown': '❓'
            }
            price_text = category_icons.get(category, '')
        self.items_table.setItem(row, 4, QTableWidgetItem(price_text))
    
    def _filter_items(self):
        """Filter items table based on search and filters"""
        search_text = self.search_input.text().lower()
        realm_filter = self.realm_filter.currentText()
        category_filter = self.category_filter.currentText()
        
        for row in range(self.items_table.rowCount()):
            show = True
            
            # Get item data
            key = self.items_table.item(row, 0).text()
            name = self.items_table.item(row, 1).text()
            realm = self.items_table.item(row, 2).text()
            price = self.items_table.item(row, 4).text()
            
            # Search filter
            if search_text and search_text not in key.lower() and search_text not in name.lower():
                show = False
            
            # Realm filter
            if realm_filter != "All" and realm != realm_filter:
                show = False
            
            # Category filter
            if category_filter != "All":
                item_key = self.items_table.item(row, 0).data(Qt.UserRole)
                item = self.database.get('items', {}).get(item_key, {})
                
                if category_filter == "Has Price":
                    if not item.get('merchant_price'):
                        show = False
                elif category_filter == "No Price":
                    if item.get('merchant_price'):
                        show = False
                elif category_filter == "Quest Reward":
                    if item.get('item_category') != 'quest_reward':
                        show = False
                elif category_filter == "Event Reward":
                    if item.get('item_category') != 'event_reward':
                        show = False
                elif category_filter == "Unknown":
                    if item.get('item_category') != 'unknown':
                        show = False
            
            self.items_table.setRowHidden(row, not show)
        
        # Update count
        visible_count = sum(1 for row in range(self.items_table.rowCount()) 
                           if not self.items_table.isRowHidden(row))
        total_count = self.items_table.rowCount()
        self.item_count_label.setText(lang.get('db_editor.filtered_count', 
            default="{visible} / {total} items").replace('{visible}', str(visible_count)).replace('{total}', str(total_count)))
    
    def _on_item_selected(self):
        """Handle item selection in table"""
        selected_rows = self.items_table.selectedItems()
        if not selected_rows:
            self._clear_editor()
            return
        
        # Get the key from first column
        row = selected_rows[0].row()
        key_item = self.items_table.item(row, 0)
        if not key_item:
            return
        
        key = key_item.data(Qt.UserRole)
        self._load_item_to_editor(key)
    
    def _load_item_to_editor(self, key: str):
        """Load item data into editor form"""
        self.current_item_key = key
        items = self.database.get('items', {})
        item = items.get(key, {})
        
        # Populate form fields
        for field_name, widget in self.field_widgets.items():
            value = item.get(field_name)
            
            if isinstance(widget, QComboBox):
                if value:
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                else:
                    widget.setCurrentIndex(0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            else:
                widget.setText(str(value) if value is not None else "")
        
        # Enable buttons
        self.save_item_btn.setEnabled(True)
        self.delete_item_btn.setEnabled(True)
    
    def _clear_editor(self):
        """Clear the editor form"""
        self.current_item_key = None
        
        for widget in self.field_widgets.values():
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            else:
                widget.clear()
        
        self.save_item_btn.setEnabled(False)
        self.delete_item_btn.setEnabled(False)
    
    def _save_current_item(self):
        """Save the current item from editor to database"""
        if not self.current_item_key:
            return
        
        # Validate required fields
        for field_name, field_def in self.field_definitions.items():
            if field_def["required"]:
                widget = self.field_widgets[field_name]
                if isinstance(widget, QLineEdit) and not widget.text().strip():
                    QMessageBox.warning(self, lang.get('db_editor.validation_error_title', default="Validation Error"), 
                        lang.get('db_editor.required_field_error', 
                            default="Field '{field}' is required!").replace('{field}', field_def['label']))
                    widget.setFocus()
                    return
        
        # Create backup state for undo
        self._save_undo_state()
        
        # Collect form data
        item_data = {}
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText()
                if not value:  # Empty combo selection
                    value = None
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            else:
                value = widget.text().strip()
                if not value:  # Empty string
                    value = None
            
            item_data[field_name] = value
        
        # Update database
        items = self.database.get('items', {})
        
        # Check if key changed (name or realm changed)
        old_name = items[self.current_item_key].get('name', '').lower()
        old_realm = items[self.current_item_key].get('realm', '').lower()
        new_name = item_data['name'].lower()
        new_realm = item_data['realm'].lower()
        new_key = f"{new_name}:{new_realm}"
        
        if new_key != self.current_item_key:
            # Key changed - delete old, create new
            del items[self.current_item_key]
            items[new_key] = item_data
            self.current_item_key = new_key
        else:
            # Update existing
            items[self.current_item_key] = item_data
        
        # Update metadata
        self.database['item_count'] = len(items)
        self.database['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to file
        self._save_database()
        
        # Refresh UI
        self._populate_table()
        self._filter_items()
        
        # Re-select the item
        for row in range(self.items_table.rowCount()):
            key_item = self.items_table.item(row, 0)
            if key_item and key_item.data(Qt.UserRole) == self.current_item_key:
                self.items_table.selectRow(row)
                break
        
        self.modified = True
        QMessageBox.information(self, lang.get('success_title', default="Success"), 
            lang.get('db_editor.save_success', default="Item '{name}' saved successfully!").replace('{name}', item_data['name']))
    
    def _delete_current_item(self):
        """Delete the current item from database"""
        if not self.current_item_key:
            return
        
        items = self.database.get('items', {})
        item = items.get(self.current_item_key, {})
        item_name = item.get('name', self.current_item_key)
        
        # Confirmation
        reply = QMessageBox.question(self, lang.get('db_editor.delete_confirm_title', default="Confirm Deletion"),
            lang.get('db_editor.delete_confirm_message', 
                default="Delete item '{name}'?\n\nThis action cannot be undone!").replace('{name}', item_name),
            QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        # Create backup state for undo
        self._save_undo_state()
        
        # Delete item
        del items[self.current_item_key]
        
        # Update metadata
        self.database['item_count'] = len(items)
        self.database['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to file
        self._save_database()
        
        # Refresh UI
        self._clear_editor()
        self._populate_table()
        self._filter_items()
        
        self.modified = True
        QMessageBox.information(self, lang.get('success_title', default="Success"), 
            lang.get('db_editor.delete_success', default="Item '{name}' deleted successfully!").replace('{name}', item_name))
    
    def _add_new_item(self):
        """Add a new item to the database"""
        # Prompt for item name and realm
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(lang.get('db_editor.add_new_item_title', default="Add New Item"))
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(lang.get('db_editor.item_name_label', default="Item Name:")))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel(lang.get('db_editor.realm_label', default="Realm:")))
        realm_combo = QComboBox()
        realm_combo.addItems(["Albion", "Hibernia", "Midgard", "All"])
        layout.addWidget(realm_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() != QDialog.Accepted:
            return
        
        item_name = name_input.text().strip()
        item_realm = realm_combo.currentText()
        
        if not item_name:
            QMessageBox.warning(self, lang.get('db_editor.invalid_input_title', default="Invalid Input"), 
                lang.get('db_editor.empty_name_error', default="Item name cannot be empty!"))
            return
        
        # Create key
        key = f"{item_name.lower()}:{item_realm.lower()}"
        
        # Check if exists
        items = self.database.get('items', {})
        if key in items:
            QMessageBox.warning(self, lang.get('db_editor.duplicate_item_title', default="Duplicate Item"), 
                lang.get('db_editor.duplicate_item_message', 
                    default="Item '{name}' ({realm}) already exists!").replace('{name}', item_name).replace('{realm}', item_realm))
            return
        
        # Create backup state for undo
        self._save_undo_state()
        
        # Create new item with default values
        new_item = {
            "id": "",
            "name": item_name,
            "realm": item_realm,
            "slot": "Unknown",
            "type": None,
            "model": None,
            "dps": None,
            "speed": None,
            "damage_type": None,
            "usable_by": "ALL",
            "merchant_zone": None,
            "merchant_price": None,
            "merchant_currency": None,
            "item_category": None,
            "ignore_item": False,
            "source": "user"
        }
        
        items[key] = new_item
        
        # Update metadata
        self.database['item_count'] = len(items)
        self.database['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to file
        self._save_database()
        
        # Refresh UI and select new item
        self._populate_table()
        self._filter_items()
        
        # Select the new item
        for row in range(self.items_table.rowCount()):
            key_item = self.items_table.item(row, 0)
            if key_item and key_item.data(Qt.UserRole) == key:
                self.items_table.selectRow(row)
                break
        
        self.modified = True
    
    def _save_database(self):
        """Save the database to JSON file"""
        try:
            # Create backup before saving
            backup_path = self.db_path.parent / "Backups"
            backup_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"items_database_src_backup_{timestamp}.json"
            
            # Copy current file to backup
            if self.db_path.exists():
                import shutil
                shutil.copy2(self.db_path, backup_file)
                logging.info(f"Backup created: {backup_file}", extra={"action": "DBEDITOR"})
            
            # Save database
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False)
            
            # Update UI
            item_count = self.database.get('item_count', 0)
            last_updated = self.database.get('last_updated', 'Unknown')
            self.db_info_label.setText(f"Items: {item_count} | Last updated: {last_updated}")
            
            logging.info(f"Database saved: {item_count} items", extra={"action": "DBEDITOR"})
            
            # Emit signal
            self.database_modified.emit()
            
        except Exception as e:
            logging.error(f"Error saving database: {e}", exc_info=True, extra={"action": "DBEDITOR"})
            QMessageBox.critical(self, lang.get('error_title', default="Error"), 
                lang.get('db_editor.save_error', default="Failed to save database:\n{error}").replace('{error}', str(e)))
    
    def _reload_database(self):
        """Reload database from file (discard unsaved changes)"""
        if self.modified:
            reply = QMessageBox.question(self, lang.get('db_editor.reload_title', default="Reload Database"),
                lang.get('db_editor.reload_confirm', 
                    default="Reload database from file?\n\nAll unsaved changes will be lost!"),
                QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        
        self._load_database()
        self._clear_editor()
        self.modified = False
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._update_undo_redo_buttons()
    
    def _save_undo_state(self):
        """Save current database state to undo stack"""
        # Deep copy current state
        import copy
        state = copy.deepcopy(self.database)
        self.undo_stack.append(state)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        
        self._update_undo_redo_buttons()
    
    def _undo(self):
        """Undo last action"""
        if not self.undo_stack:
            return
        
        # Save current state to redo stack
        import copy
        self.redo_stack.append(copy.deepcopy(self.database))
        
        # Restore previous state
        self.database = self.undo_stack.pop()
        
        # Save and refresh
        self._save_database()
        self._populate_table()
        self._filter_items()
        self._clear_editor()
        
        self._update_undo_redo_buttons()
    
    def _redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            return
        
        # Save current state to undo stack
        import copy
        self.undo_stack.append(copy.deepcopy(self.database))
        
        # Restore redo state
        self.database = self.redo_stack.pop()
        
        # Save and refresh
        self._save_database()
        self._populate_table()
        self._filter_items()
        self._clear_editor()
        
        self._update_undo_redo_buttons()
    
    def _update_undo_redo_buttons(self):
        """Update undo/redo button states"""
        self.undo_btn.setEnabled(len(self.undo_stack) > 0)
        self.redo_btn.setEnabled(len(self.redo_stack) > 0)
