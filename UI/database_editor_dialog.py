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
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QTextEdit, QMessageBox, QSplitter,
    QHeaderView, QCheckBox, QSpinBox, QFrame, QApplication, QDialog,
    QDialogButtonBox, QRadioButton, QListWidget, QProgressDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from Functions.language_manager import lang


class DatabaseEditorDialog(QMainWindow):
    """Window for editing items_database_src.json (non-modal, resizable)"""
    
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
        self.setWindowTitle(lang.get('db_editor.window_title', default="🗄️ Database - Editor - items_database_src.json"))
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        # Create central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
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
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels([
            lang.get('db_editor.column_name', default="Name"),
            lang.get('db_editor.column_key', default="Key"),
            lang.get('db_editor.column_realm', default="Realm"),
            lang.get('db_editor.column_slot', default="Slot"),
            lang.get('db_editor.column_price', default="Price"),
            lang.get('db_editor.column_ignore', default="Ignore Item")
        ])
        # Make all columns resizable by user
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # Set initial widths
        self.items_table.setColumnWidth(0, 250)  # Name
        self.items_table.setColumnWidth(1, 200)  # Key
        self.items_table.setColumnWidth(2, 100)  # Realm
        self.items_table.setColumnWidth(3, 100)  # Slot
        self.items_table.setColumnWidth(4, 150)  # Price
        self.items_table.setColumnWidth(5, 100)  # Ignore Item
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setSelectionMode(QTableWidget.ExtendedSelection)  # Allow multi-selection with Ctrl/Shift
        self.items_table.itemSelectionChanged.connect(self._on_item_selected)
        
        # Enable context menu (right-click)
        self.items_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.items_table.customContextMenuRequested.connect(self._show_context_menu)
        
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
            
            # Special handling for "id" field (Eden ID) - add a button to open Eden page
            if field_name == "id":
                id_layout = QHBoxLayout()
                id_layout.addWidget(widget)
                
                open_eden_btn = QPushButton("🔗")
                open_eden_btn.setToolTip(lang.get('db_editor.open_eden_tooltip', default="Open item page on Eden Herald"))
                open_eden_btn.setMaximumWidth(40)
                open_eden_btn.clicked.connect(self._open_item_in_eden)
                id_layout.addWidget(open_eden_btn)
                
                self.editor_form.addRow(label_text + ":", id_layout)
            # Special handling for "model" field (Model ID) - add a button to view model image
            elif field_name == "model":
                model_layout = QHBoxLayout()
                model_layout.addWidget(widget)
                
                view_model_btn = QPushButton("🖼️")
                view_model_btn.setToolTip(lang.get('db_editor.view_model_tooltip', default="View model image"))
                view_model_btn.setMaximumWidth(40)
                view_model_btn.clicked.connect(self._view_model_image)
                model_layout.addWidget(view_model_btn)
                
                self.editor_form.addRow(label_text + ":", model_layout)
            else:
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
        close_btn.clicked.connect(self.close)
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
        # Disable updates during population for better performance
        self.items_table.setUpdatesEnabled(False)
        self.items_table.setSortingEnabled(False)
        
        try:
            self.items_table.setRowCount(0)
            
            items = self.database.get('items', {})
            
            for key, item in items.items():
                self._add_table_row(key, item)
            
            self.item_count_label.setText(lang.get('db_editor.items_count_value', default="{count} items").replace('{count}', str(len(items))))
        finally:
            # Re-enable updates and sorting
            self.items_table.setSortingEnabled(True)
            self.items_table.setUpdatesEnabled(True)
    
    def _add_table_row(self, key: str, item: Dict[str, Any]):
        """Add a row to the items table"""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Name (column 0)
        self.items_table.setItem(row, 0, QTableWidgetItem(item.get('name', '')))
        
        # Key (column 1)
        key_item = QTableWidgetItem(key)
        key_item.setData(Qt.UserRole, key)  # Store key for later retrieval
        self.items_table.setItem(row, 1, key_item)
        
        # Realm (column 2)
        self.items_table.setItem(row, 2, QTableWidgetItem(item.get('realm', '')))
        
        # Slot (column 3)
        self.items_table.setItem(row, 3, QTableWidgetItem(item.get('slot', '')))
        
        # Price (column 4)
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
        
        # Ignore Item (column 5)
        ignore_item = item.get('ignore_item', False)
        ignore_text = lang.get('db_editor.yes', default="Yes") if ignore_item else lang.get('db_editor.no', default="No")
        self.items_table.setItem(row, 5, QTableWidgetItem(ignore_text))
    
    def _filter_items(self):
        """Filter items table based on search and filters"""
        # Disable updates during filtering for better performance
        self.items_table.setUpdatesEnabled(False)
        
        try:
            search_text = self.search_input.text().lower()
            realm_filter = self.realm_filter.currentText()
            category_filter_index = self.category_filter.currentIndex()  # Use index instead of text
            
            visible_count = 0
            
            for row in range(self.items_table.rowCount()):
                show = True
                
                # Get item data (column indices: 0=Name, 1=Key, 2=Realm, 3=Slot, 4=Price, 5=Ignore)
                name = self.items_table.item(row, 0).text()
                key = self.items_table.item(row, 1).text()
                realm = self.items_table.item(row, 2).text()
                price = self.items_table.item(row, 4).text()
                
                # Search filter
                if search_text and search_text not in key.lower() and search_text not in name.lower():
                    show = False
                
                # Realm filter
                if show and realm_filter != "All" and realm != realm_filter:
                    show = False
                
                # Category filter (0=All, 1=Has Price, 2=No Price, 3=Quest Reward, 4=Event Reward, 5=Unknown)
                if show and category_filter_index > 0:
                    item_key = self.items_table.item(row, 1).data(Qt.UserRole)
                    item = self.database.get('items', {}).get(item_key, {})
                    
                    if category_filter_index == 1:  # Has Price
                        if not item.get('merchant_price'):
                            show = False
                    elif category_filter_index == 2:  # No Price
                        # Show only items without price AND without category (exclude quest/event rewards)
                        if item.get('merchant_price') or item.get('item_category'):
                            show = False
                    elif category_filter_index == 3:  # Quest Reward
                        if item.get('item_category') != 'quest_reward':
                            show = False
                    elif category_filter_index == 4:  # Event Reward
                        if item.get('item_category') != 'event_reward':
                            show = False
                    elif category_filter_index == 5:  # Unknown
                        if item.get('item_category') != 'unknown':
                            show = False
                
                self.items_table.setRowHidden(row, not show)
                if show:
                    visible_count += 1
            
            # Update count
            total_count = self.items_table.rowCount()
            self.item_count_label.setText(lang.get('db_editor.filtered_count', 
                default="{visible} / {total} items").replace('{visible}', str(visible_count)).replace('{total}', str(total_count)))
        finally:
            # Re-enable updates
            self.items_table.setUpdatesEnabled(True)
    
    def _on_item_selected(self):
        """Handle item selection in table"""
        selected_rows = self.items_table.selectedItems()
        if not selected_rows:
            self._clear_editor()
            return
        
        # Get the key from column 1 (Key column)
        row = selected_rows[0].row()
        key_item = self.items_table.item(row, 1)
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
    
    def _save_database(self):
        """Save the database to JSON file using centralized backup system"""
        try:
            # Use centralized backup directory (Database/ subfolder)
            from Functions.config_manager import config
            backup_base = config.get("backup_path")
            if backup_base:
                backup_path = Path(backup_base).parent / "Database"
            else:
                # Fallback to old location
                backup_path = self.db_path.parent / "Backups"
            backup_path.mkdir(parents=True, exist_ok=True)
            
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
            
            # Reset modified flag since changes are now saved
            self.modified = False
            
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
    
    def closeEvent(self, event):
        """Handle window close event - check for unsaved changes"""
        if self.modified:
            reply = QMessageBox.question(
                self,
                lang.get('db_editor.close_title', default="Close Editor"),
                lang.get('db_editor.close_confirm', 
                    default="You have unsaved changes.\n\nClose without saving?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                event.ignore()  # Cancel close
                return
        
        # Accept close
        event.accept()
    
    def _show_context_menu(self, position):
        """Show context menu on right-click in items table"""
        # Get selected rows
        selected_rows = self.items_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        # Get selected items data
        selected_items_data = []
        for index in selected_rows:
            row = index.row()
            key_item = self.items_table.item(row, 1)
            if key_item:
                item_key = key_item.data(Qt.UserRole)
                if item_key in self.database.get('items', {}):
                    item_data = self.database['items'][item_key]
                    selected_items_data.append({
                        'key': item_key,
                        'name': item_data.get('name', ''),
                        'id': item_data.get('id', '')
                    })
        
        if not selected_items_data:
            return
        
        # Create context menu
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        
        # Check if multiple items selected
        is_multi_selection = len(selected_items_data) > 1
        
        if is_multi_selection:
            # Multi-selection menu
            menu.addSection(f"📋 {len(selected_items_data)} {lang.get('db_editor.items_selected', default='items selected')}")
            
            # Batch Refresh by ID
            has_ids = all(item['id'] for item in selected_items_data)
            if has_ids:
                batch_refresh_action = QAction(f"🔄 {lang.get('db_editor.batch_refresh_by_id', default='Batch Refresh by ID')} ({len(selected_items_data)} items)", self)
                batch_refresh_action.triggered.connect(lambda: self._batch_refresh_items_by_id(selected_items_data))
                menu.addAction(batch_refresh_action)
            else:
                no_id_action = QAction(lang.get('db_editor.some_items_no_id', default='⚠️ Some items have no ID'), self)
                no_id_action.setEnabled(False)
                menu.addAction(no_id_action)
            
            # Batch Full Scan
            batch_full_scan_action = QAction(f"🔍 {lang.get('db_editor.batch_full_scan', default='Batch Full Scan')} ({len(selected_items_data)} items)", self)
            batch_full_scan_action.triggered.connect(lambda: self._batch_full_scan_items(selected_items_data))
            menu.addAction(batch_full_scan_action)
            
            # Batch Tag
            menu.addSeparator()
            tag_menu = menu.addMenu(f"🏷️ {lang.get('db_editor.batch_tag_category', default='Batch Tag Category')}")
            
            quest_action = QAction(f"🏆 {lang.get('db_editor.tag_quest_reward', default='Quest Reward')}", self)
            quest_action.triggered.connect(lambda: self._batch_tag_items(selected_items_data, 'quest_reward'))
            tag_menu.addAction(quest_action)
            
            event_action = QAction(f"🎉 {lang.get('db_editor.tag_event_reward', default='Event Reward')}", self)
            event_action.triggered.connect(lambda: self._batch_tag_items(selected_items_data, 'event_reward'))
            tag_menu.addAction(event_action)
            
            unknown_action = QAction(f"❓ {lang.get('db_editor.tag_unknown', default='Unknown Source')}", self)
            unknown_action.triggered.connect(lambda: self._batch_tag_items(selected_items_data, 'unknown'))
            tag_menu.addAction(unknown_action)
            
        else:
            # Single-selection menu (existing behavior)
            item = selected_items_data[0]
            item_key = item['key']
            item_name = item['name']
            item_id = item['id']
            
            # 1. Refresh from Eden by ID (precise)
            if item_id:
                refresh_action = QAction(f"🔄 {lang.get('db_editor.refresh_from_eden', default='Refresh from Eden')} (ID: {item_id})", self)
                refresh_action.triggered.connect(lambda: self._refresh_item_from_eden(item_key, item_id, item_name))
                menu.addAction(refresh_action)
            else:
                no_id_action = QAction(lang.get('db_editor.no_id_available', default='⚠️ No ID available for refresh'), self)
                no_id_action.setEnabled(False)
                menu.addAction(no_id_action)
            
            # 2. Full scan by name (all realms/variants)
            full_scan_action = QAction(f"🔍 {lang.get('db_editor.full_scan_item', default='Full Scan - All Variants')} ({item_name})", self)
            full_scan_action.triggered.connect(lambda: self._full_scan_item(item_name))
            menu.addAction(full_scan_action)
            
            # 3. Separator
            menu.addSeparator()
            
            # 4. Tag item category
            tag_menu = menu.addMenu(f"🏷️ {lang.get('db_editor.tag_item_category', default='Tag Category')}")
            
            quest_action = QAction(f"🏆 {lang.get('db_editor.tag_quest_reward', default='Quest Reward')}", self)
            quest_action.triggered.connect(lambda: self._quick_tag_item(item_key, 'quest_reward'))
            tag_menu.addAction(quest_action)
            
            event_action = QAction(f"🎉 {lang.get('db_editor.tag_event_reward', default='Event Reward')}", self)
            event_action.triggered.connect(lambda: self._quick_tag_item(item_key, 'event_reward'))
            tag_menu.addAction(event_action)
            
            unknown_action = QAction(f"❓ {lang.get('db_editor.tag_unknown', default='Unknown Source')}", self)
            unknown_action.triggered.connect(lambda: self._quick_tag_item(item_key, 'unknown'))
            tag_menu.addAction(unknown_action)
            
            tag_menu.addSeparator()
            
            remove_tag_action = QAction(f"🗑️ {lang.get('db_editor.remove_tag', default='Remove Tag')}", self)
            remove_tag_action.triggered.connect(lambda: self._remove_item_tag(item_key))
            tag_menu.addAction(remove_tag_action)
        
        # Show menu at cursor position
        menu.exec(self.items_table.viewport().mapToGlobal(position))
    
    def _refresh_item_from_eden(self, item_key, item_id, item_name):
        """Refresh item data from Eden using its ID"""
        try:
            # Confirmation dialog
            reply = QMessageBox.question(
                self,
                lang.get('db_editor.refresh_confirm_title', default="Refresh Item"),
                lang.get('db_editor.refresh_confirm_message',
                    default="Refresh '{name}' from Eden Herald?\n\n"
                           "This will update:\n"
                           "• Model ID\n"
                           "• DPS, Speed, Damage Type (weapons)\n"
                           "• Type, Slot\n"
                           "• Merchant price and zone\n\n"
                           "Filters (level/utility) will be BYPASSED.").replace('{name}', item_name),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Show progress message
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog(
                lang.get('db_editor.refresh_progress', default="Connecting to Eden Herald..."),
                None, 0, 0, self
            )
            progress.setWindowTitle(lang.get('db_editor.refresh_progress_title', default="Refreshing Item"))
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QApplication.processEvents()
            
            # Import required modules
            from Functions.eden_scraper import _connect_to_eden_herald
            from Functions.items_scraper import ItemsScraper
            
            # Connect to Eden
            progress.setLabelText(lang.get('db_editor.refresh_connecting', default="Connecting to Eden Herald..."))
            QApplication.processEvents()
            
            eden_scraper, error_message = _connect_to_eden_herald(headless=False)
            if not eden_scraper:
                progress.close()
                QMessageBox.critical(self,
                    lang.get('error_title', default="Error"),
                    f"{lang.get('db_editor.refresh_connect_error', default='Failed to connect to Eden Herald')}:\n{error_message}")
                return
            
            try:
                items_scraper = ItemsScraper(eden_scraper)
                
                # Get item details by ID
                progress.setLabelText(lang.get('db_editor.refresh_fetching', 
                    default="Fetching item details from Eden..."))
                QApplication.processEvents()
                
                item_details = items_scraper.get_item_details(
                    item_id=item_id,
                    realm=self.database['items'][item_key].get('realm', 'All'),
                    item_name=item_name
                )
                
                if not item_details:
                    progress.close()
                    QMessageBox.warning(self,
                        lang.get('warning_title', default="Warning"),
                        lang.get('db_editor.refresh_no_data', default="No data retrieved from Eden."))
                    return
                
                # Update database with new data (only non-empty fields)
                progress.setLabelText(lang.get('db_editor.refresh_updating', default="Updating database..."))
                QApplication.processEvents()
                
                updated_fields = []
                for field in ['model', 'dps', 'speed', 'damage_type', 'type', 'slot', 
                             'merchant_zone', 'merchant_price', 'merchant_currency']:
                    if field in item_details and item_details[field]:
                        old_value = self.database['items'][item_key].get(field)
                        new_value = item_details[field]
                        if old_value != new_value:
                            self.database['items'][item_key][field] = new_value
                            updated_fields.append(f"{field}: {old_value} → {new_value}")
                
                progress.close()
                
                # If no merchant price found, ask user to tag the item
                if not item_details.get('merchant_price'):
                    self._prompt_tag_no_price_item(item_key, item_name)
                
                if updated_fields:
                    # Save changes
                    self._save_database()
                    
                    # Show success with details
                    QMessageBox.information(self,
                        lang.get('success_title', default="Success"),
                        f"{lang.get('db_editor.refresh_success', default='Item refreshed successfully!')}\n\n"
                        f"{lang.get('db_editor.updated_fields', default='Updated fields')}:\n" +
                        "\n".join(updated_fields))
                    
                    # Defer refresh to prevent UI blocking
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self._refresh_display_after_update(item_key))
                else:
                    QMessageBox.information(self,
                        lang.get('info_title', default="Information"),
                        lang.get('db_editor.refresh_no_changes', default="No changes detected."))
                
            finally:
                # Always close scraper
                eden_scraper.close()
                
        except Exception as e:
            logging.error(f"Error refreshing item from Eden: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.refresh_error', default='Failed to refresh item')}:\n{str(e)}")
    
    def _full_scan_item(self, item_name):
        """Full scan of item by name - finds all variants across all realms"""
        try:
            # Confirmation dialog
            reply = QMessageBox.question(
                self,
                lang.get('db_editor.full_scan_confirm_title', default="Full Scan Item"),
                lang.get('db_editor.full_scan_confirm_message',
                    default="Perform full scan for '{name}'?\n\n"
                           "This will:\n"
                           "• Search all realms (Albion, Hibernia, Midgard, All)\n"
                           "• Find all variants of this item\n"
                           "• Create/update entries for each realm found\n"
                           "• Bypass level/utility filters\n\n"
                           "⚠️ This may add new items if variants are found in other realms.").replace('{name}', item_name),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Show progress dialog
            progress = QProgressDialog(
                lang.get('db_editor.full_scan_progress', default="Scanning all variants..."),
                None, 0, 0, self
            )
            progress.setWindowTitle(lang.get('db_editor.full_scan_progress_title', default="Full Scan"))
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QApplication.processEvents()
            
            # Import required modules
            from Functions.eden_scraper import _connect_to_eden_herald
            from Functions.items_scraper import ItemsScraper
            
            # Connect to Eden
            progress.setLabelText(lang.get('db_editor.full_scan_connecting', default="Connecting to Eden Herald..."))
            QApplication.processEvents()
            
            eden_scraper, error_message = _connect_to_eden_herald(headless=False)
            if not eden_scraper:
                progress.close()
                QMessageBox.critical(self,
                    lang.get('error_title', default="Error"),
                    f"{lang.get('db_editor.full_scan_connect_error', default='Failed to connect to Eden Herald')}:\n{error_message}")
                return
            
            try:
                items_scraper = ItemsScraper(eden_scraper)
                
                # Find all variants (skip_filters=True by default)
                progress.setLabelText(lang.get('db_editor.full_scan_searching', 
                    default="Searching all variants on Eden..."))
                QApplication.processEvents()
                
                variants = items_scraper.find_all_item_variants(item_name, skip_filters=True)
                
                if not variants:
                    progress.close()
                    QMessageBox.warning(self,
                        lang.get('warning_title', default="Warning"),
                        lang.get('db_editor.full_scan_no_variants', 
                            default="No variants found for '{name}'.").replace('{name}', item_name))
                    return
                
                # Process each variant
                progress.setLabelText(lang.get('db_editor.full_scan_processing', 
                    default=f"Processing {len(variants)} variant(s)..."))
                QApplication.processEvents()
                
                # STEP 1: Remove all old entries with this item name
                # (to avoid duplicates when realm structure changes)
                old_keys_to_remove = []
                for key, item_data in self.database.get('items', {}).items():
                    if item_data.get('name') == item_name:
                        old_keys_to_remove.append(key)
                
                for key in old_keys_to_remove:
                    del self.database['items'][key]
                
                # STEP 2: Add all new variants
                items_added = 0
                items_updated = 0
                updated_details = []
                items_without_price = []  # Track items without price
                
                for variant in variants:
                    variant_id = variant.get('id')
                    variant_realm = variant.get('realm', 'All')
                    
                    # Generate item key
                    item_key = f"{item_name}_{variant_realm}"
                    
                    # Get full details
                    item_details = items_scraper.get_item_details(
                        item_id=variant_id,
                        realm=variant_realm,
                        item_name=item_name
                    )
                    
                    if not item_details:
                        continue
                    
                    # All items are new since we removed old entries
                    # Add new variant
                    self.database['items'][item_key] = {
                        'id': item_details.get('id', ''),
                        'name': item_name,
                        'realm': variant_realm,
                        'slot': item_details.get('slot', ''),
                        'type': item_details.get('type', ''),
                        'model': item_details.get('model', ''),
                        'dps': item_details.get('dps', ''),
                        'speed': item_details.get('speed', ''),
                        'damage_type': item_details.get('damage_type', ''),
                        'usable_by': item_details.get('usable_by', 'ALL'),
                        'merchant_zone': item_details.get('merchant_zone', ''),
                        'merchant_price': item_details.get('merchant_price', ''),
                        'merchant_currency': item_details.get('merchant_currency', ''),
                        'item_category': '',
                        'ignore_item': False,
                        'source': 'scraped'
                    }
                    items_added += 1
                    updated_details.append(f"{variant_realm}: ADDED (ID: {item_details.get('id', 'N/A')})")
                    
                    # Track items without price for tagging
                    if not item_details.get('merchant_price'):
                        items_without_price.append((item_key, item_name, variant_realm))
                
                progress.close()
                
                # Save changes
                if items_added > 0:
                    self._save_database()
                    
                    # Show success
                    result_message = f"{lang.get('db_editor.full_scan_success', default='Full scan completed!')}\n\n"
                    result_message += f"{lang.get('db_editor.full_scan_removed', default='Old entries removed')}: {len(old_keys_to_remove)}\n"
                    result_message += f"{lang.get('db_editor.full_scan_variants_found', default='Variants found')}: {len(variants)}\n"
                    result_message += f"{lang.get('db_editor.full_scan_added', default='Added')}: {items_added}\n\n"
                    
                    if updated_details:
                        result_message += f"{lang.get('db_editor.full_scan_details', default='Details')}:\n"
                        result_message += "\n".join(updated_details[:10])  # Limit to first 10
                        if len(updated_details) > 10:
                            result_message += f"\n... ({len(updated_details) - 10} more)"
                    
                    QMessageBox.information(self,
                        lang.get('success_title', default="Success"),
                        result_message)
                    
                    # Defer refresh to prevent UI blocking
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, self._refresh_display_after_scan)
                    
                    # If items without price were found, prompt user to tag them (after refresh)
                    if items_without_price:
                        QTimer.singleShot(100, lambda: self._prompt_tag_multiple_no_price_items(items_without_price))
                else:
                    QMessageBox.information(self,
                        lang.get('info_title', default="Information"),
                        lang.get('db_editor.full_scan_no_changes', 
                            default=f"Scanned {len(variants)} variant(s), no changes needed."))
                
            finally:
                # Always close scraper
                eden_scraper.close()
                
        except Exception as e:
            logging.error(f"Error during full scan: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.full_scan_error', default='Failed to perform full scan')}:\\n{str(e)}")
    
    def _prompt_tag_no_price_item(self, item_key: str, item_name: str):
        """Prompt user to tag an item without merchant price"""
        reply = QMessageBox.question(
            self,
            lang.get('db_editor.tag_no_price_title', default="No Merchant Price Found"),
            lang.get('db_editor.tag_no_price_message',
                default="No merchant price found for '{name}'.\n\n"
                       "Would you like to tag this item as:\n"
                       "• Quest Reward (🏆)\n"
                       "• Event Reward (🎉)\n"
                       "• Unknown source (❓)\n\n"
                       "This helps identify items that cannot be bought from merchants.").replace('{name}', item_name),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Show dialog with category options
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle(lang.get('db_editor.tag_category_title', default="Select Item Category"))
            layout = QVBoxLayout(dialog)
            
            # Category radio buttons
            quest_radio = QRadioButton("🏆 " + lang.get('db_editor.tag_quest_reward', default="Quest Reward"))
            event_radio = QRadioButton("🎉 " + lang.get('db_editor.tag_event_reward', default="Event Reward"))
            unknown_radio = QRadioButton("❓ " + lang.get('db_editor.tag_unknown', default="Unknown Source"))
            quest_radio.setChecked(True)  # Default selection
            
            layout.addWidget(quest_radio)
            layout.addWidget(event_radio)
            layout.addWidget(unknown_radio)
            
            # Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec() == QDialog.Accepted:
                # Determine selected category
                if quest_radio.isChecked():
                    category = 'quest_reward'
                elif event_radio.isChecked():
                    category = 'event_reward'
                else:
                    category = 'unknown'
                
                # Update item in database
                self.database['items'][item_key]['item_category'] = category
                self.database['items'][item_key]['ignore_item'] = (category != 'unknown')  # Ignore if categorized
                self._save_database()
                
                # Refresh display
                self._populate_table()
                self._filter_items()
                
                QMessageBox.information(self,
                    lang.get('success_title', default="Success"),
                    lang.get('db_editor.tag_success', default="Item tagged successfully!"))
    
    def _prompt_tag_multiple_no_price_items(self, items_list: list):
        """Prompt user to tag multiple items without merchant price
        
        Args:
            items_list: List of tuples (item_key, item_name, realm)
        """
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QDialogButtonBox, QRadioButton, QGroupBox
        
        reply = QMessageBox.question(
            self,
            lang.get('db_editor.tag_multiple_no_price_title', default="Items Without Merchant Price"),
            lang.get('db_editor.tag_multiple_no_price_message',
                default="{count} item(s) found without merchant price.\n\n"
                       "Would you like to tag them as Quest/Event rewards?").replace('{count}', str(len(items_list))),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(lang.get('db_editor.tag_multiple_title', default="Tag Items Without Price"))
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_label = QLabel(lang.get('db_editor.tag_multiple_info',
            default="Select a category to apply to all items listed below:"))
        layout.addWidget(info_label)
        
        # Category selection
        category_group = QGroupBox(lang.get('db_editor.tag_category_label', default="Category"))
        category_layout = QVBoxLayout()
        
        quest_radio = QRadioButton("🏆 " + lang.get('db_editor.tag_quest_reward', default="Quest Reward"))
        event_radio = QRadioButton("🎉 " + lang.get('db_editor.tag_event_reward', default="Event Reward"))
        unknown_radio = QRadioButton("❓ " + lang.get('db_editor.tag_unknown', default="Unknown Source"))
        quest_radio.setChecked(True)
        
        category_layout.addWidget(quest_radio)
        category_layout.addWidget(event_radio)
        category_layout.addWidget(unknown_radio)
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # Items list
        items_label = QLabel(lang.get('db_editor.tag_items_label', default="Items to tag:"))
        layout.addWidget(items_label)
        
        items_listwidget = QListWidget()
        for item_key, item_name, realm in items_list:
            items_listwidget.addItem(f"{item_name} ({realm})")
        layout.addWidget(items_listwidget)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            # Determine selected category
            if quest_radio.isChecked():
                category = 'quest_reward'
            elif event_radio.isChecked():
                category = 'event_reward'
            else:
                category = 'unknown'
            
            # Update all items
            for item_key, item_name, realm in items_list:
                if item_key in self.database['items']:
                    self.database['items'][item_key]['item_category'] = category
                    self.database['items'][item_key]['ignore_item'] = (category != 'unknown')  # Ignore if categorized
            
            self._save_database()
            
            # Refresh display
            self._populate_table()
            self._filter_items()
            
            QMessageBox.information(self,
                lang.get('success_title', default="Success"),
                lang.get('db_editor.tag_multiple_success',
                    default="{count} item(s) tagged successfully!").replace('{count}', str(len(items_list))))
    
    def _refresh_display_after_update(self, item_key: str):
        """Refresh display after item update and reselect the updated item"""
        try:
            # Refresh display
            self._populate_table()
            self._filter_items()
            
            # Select the updated item (search by key in column 1)
            for row in range(self.items_table.rowCount()):
                key_item = self.items_table.item(row, 1)
                if key_item and key_item.data(Qt.UserRole) == item_key:
                    self.items_table.selectRow(row)
                    break
        except Exception as e:
            logging.error(f"Error refreshing display: {e}", exc_info=True)
    
    def _refresh_display_after_scan(self):
        """Refresh display after full scan"""
        try:
            self._populate_table()
            self._filter_items()
        except Exception as e:
            logging.error(f"Error refreshing display: {e}", exc_info=True)
    
    def _quick_tag_item(self, item_key: str, category: str):
        """Quickly tag an item with a category from context menu
        
        Args:
            item_key: Item key in database
            category: Category to set ('quest_reward', 'event_reward', 'unknown')
        """
        try:
            if item_key not in self.database['items']:
                return
            
            # Update item
            self.database['items'][item_key]['item_category'] = category
            self.database['items'][item_key]['ignore_item'] = (category != 'unknown')
            
            # Save and refresh
            self._save_database()
            
            # Defer refresh to prevent UI blocking
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._refresh_display_after_update(item_key))
            
        except Exception as e:
            logging.error(f"Error tagging item: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.tag_error', default='Failed to tag item')}:\n{str(e)}")
    
    def _remove_item_tag(self, item_key: str):
        """Remove category tag from an item
        
        Args:
            item_key: Item key in database
        """
        try:
            if item_key not in self.database['items']:
                return
            
            # Remove category and ignore flag
            self.database['items'][item_key]['item_category'] = ''
            self.database['items'][item_key]['ignore_item'] = False
            
            # Save and refresh
            self._save_database()
            
            # Defer refresh to prevent UI blocking
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._refresh_display_after_update(item_key))
            
        except Exception as e:
            logging.error(f"Error removing tag: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.remove_tag_error', default='Failed to remove tag')}:\n{str(e)}")
    
    def _open_item_in_eden(self):
        """Open the current item's page on Eden Herald in browser"""
        try:
            # Get item ID from the editor field
            item_id = self.field_widgets.get('id')
            if not item_id:
                return
            
            eden_id = item_id.text().strip()
            if not eden_id:
                QMessageBox.warning(self,
                    lang.get('warning_title', default="Warning"),
                    lang.get('db_editor.no_eden_id', default="No Eden ID available for this item."))
                return
            
            # Construct Eden URL for items page
            # Format: https://eden-daoc.net/items?id={id}
            url = f"https://eden-daoc.net/items?id={eden_id}"
            
            # Open in default browser
            webbrowser.open(url)
            logging.info(f"Opened Eden item page: {url}", extra={"action": "DBEDITOR"})
            
        except Exception as e:
            logging.error(f"Error opening Eden page: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.open_eden_error', default='Failed to open Eden page')}:\n{str(e)}")
    
    def _view_model_image(self):
        """View the model image in a preview dialog"""
        try:
            # Get model ID from the editor field
            model_widget = self.field_widgets.get('model')
            if not model_widget:
                return
            
            model_id = model_widget.text().strip()
            if not model_id:
                QMessageBox.warning(self,
                    lang.get('warning_title', default="Warning"),
                    lang.get('db_editor.no_model_id', default="No Model ID available for this item."))
                return
            
            # Construct path to model image
            from pathlib import Path
            model_path = Path(f"Img/Models/items/{model_id}.webp")
            
            if not model_path.exists():
                QMessageBox.warning(self,
                    lang.get('warning_title', default="Warning"),
                    lang.get('db_editor.model_not_found', default="Model image not found:\n{path}").replace('{path}', str(model_path)))
                return
            
            # Create preview dialog
            from PySide6.QtGui import QPixmap
            
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle(lang.get('db_editor.model_preview_title', default="Model Preview - ID: {id}").replace('{id}', model_id))
            preview_dialog.setModal(True)
            
            layout = QVBoxLayout(preview_dialog)
            
            # Model image label
            image_label = QLabel()
            pixmap = QPixmap(str(model_path))
            
            # Scale image if too large (max 512x512)
            if pixmap.width() > 512 or pixmap.height() > 512:
                pixmap = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
            
            # Model ID info
            info_label = QLabel(f"<b>{lang.get('db_editor.model_id_label', default='Model ID')}:</b> {model_id}")
            info_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(info_label)
            
            # Close button
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.rejected.connect(preview_dialog.reject)
            layout.addWidget(button_box)
            
            preview_dialog.resize(550, 600)
            preview_dialog.exec()
            
            logging.info(f"Viewed model image: {model_id}", extra={"action": "DBEDITOR"})
            
        except Exception as e:
            logging.error(f"Error viewing model image: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.view_model_error', default='Failed to view model image')}:\n{str(e)}")
    
    def _batch_refresh_items_by_id(self, items_data: list):
        """Batch refresh multiple items by their IDs
        
        Args:
            items_data: List of dicts with 'key', 'name', 'id'
        """
        try:
            # Confirmation
            reply = QMessageBox.question(
                self,
                lang.get('db_editor.batch_refresh_confirm_title', default="Batch Refresh Items"),
                lang.get('db_editor.batch_refresh_confirm_message',
                    default="Refresh {count} item(s) from Eden Herald by ID?\n\n"
                           "This will update all selected items.").replace('{count}', str(len(items_data))),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Create progress dialog with beautiful steps
            from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
            
            steps = StepConfiguration.build_steps(
                StepConfiguration.DB_EDITOR_BATCH_REFRESH,
                StepConfiguration.CLEANUP
            )
            
            progress = ProgressStepsDialog(
                parent=self,
                title=lang.get('db_editor.batch_refresh_title', default="🔄 Batch Refresh Items"),
                steps=steps,
                description=lang.get('db_editor.batch_refresh_desc', 
                    default=f"Refreshing {len(items_data)} item(s) from Eden Herald by ID..."),
                show_progress_bar=True,
                determinate_progress=True,
                allow_cancel=True
            )
            
            progress.show()
            # Force multiple processEvents to ensure UI is fully rendered
            for _ in range(3):
                QApplication.processEvents()
            
            # Step 0: Connect to Eden
            progress.start_step(0)
            progress.set_status_message("🔌 Connecting to Eden Herald...")
            QApplication.processEvents()
            from Functions.eden_scraper import _connect_to_eden_herald
            from Functions.items_scraper import ItemsScraper
            
            eden_scraper, error_message = _connect_to_eden_herald(headless=False)
            if not eden_scraper:
                progress.close()
                QMessageBox.critical(self,
                    lang.get('error_title', default="Error"),
                    f"{lang.get('db_editor.refresh_connect_error', default='Failed to connect to Eden Herald')}:\n{error_message}")
                return
            
            progress.complete_step(0)
            
            try:
                # Step 1: Refresh items
                progress.start_step(1)
                items_scraper = ItemsScraper(eden_scraper)
                
                items_updated = 0
                items_failed = 0
                
                for i, item_data in enumerate(items_data):
                    if progress.was_canceled():
                        break
                    
                    # Update progress percentage
                    percentage = int((i / len(items_data)) * 100)
                    progress.update_progress(percentage)
                    progress.set_status_message(f"⏳ {item_data['name']} ({i+1}/{len(items_data)})")
                    QApplication.processEvents()
                    
                    # Get item details
                    item_key = item_data['key']
                    item_details = items_scraper.get_item_details(
                        item_id=item_data['id'],
                        realm=self.database['items'][item_key].get('realm', 'All'),
                        item_name=item_data['name']
                    )
                    
                    if item_details:
                        # Update database
                        for field in ['model', 'dps', 'speed', 'damage_type', 'type', 'slot',
                                     'merchant_zone', 'merchant_price', 'merchant_currency']:
                            if field in item_details and item_details[field]:
                                self.database['items'][item_key][field] = item_details[field]
                        items_updated += 1
                    else:
                        items_failed += 1
                
                progress.update_progress(100)
                progress.complete_step(1)
                
                # Step 2: Save
                if items_updated > 0:
                    progress.start_step(2)
                    self._save_database()
                    progress.complete_step(2)
                else:
                    progress.skip_step(2, "No items updated")
                
                # Step 3: Cleanup
                progress.start_step(3)
                
            finally:
                eden_scraper.close()
                progress.complete_step(3)
                
                # Defer refresh to prevent UI blocking
                from PySide6.QtCore import QTimer
                QTimer.singleShot(100, self._refresh_display_after_scan)
                
                # Close progress dialog after a short delay
                QTimer.singleShot(500, progress.close)
                
                # Show summary
                QTimer.singleShot(600, lambda: QMessageBox.information(self,
                    lang.get('success_title', default="Success"),
                    lang.get('db_editor.batch_refresh_success',
                        default="Batch refresh completed!\n\n"
                               "Updated: {updated}\nFailed: {failed}").replace('{updated}', str(items_updated)).replace('{failed}', str(items_failed))))
                
        except Exception as e:
            logging.error(f"Error in batch refresh: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.batch_refresh_error', default='Batch refresh failed')}:\n{str(e)}")
    
    def _batch_full_scan_items(self, items_data: list):
        """Batch full scan multiple items by name - processes all items without interruption
        
        Args:
            items_data: List of dicts with 'key', 'name', 'id'
        """
        try:
            # Get unique item names (avoid duplicates from same item with different realms)
            unique_names = list(set(item['name'] for item in items_data))
            
            # Confirmation
            reply = QMessageBox.question(
                self,
                lang.get('db_editor.batch_full_scan_confirm_title', default="Batch Full Scan"),
                lang.get('db_editor.batch_full_scan_confirm_message',
                    default="Perform full scan for {count} item(s)?\n\n"
                           "This will search all variants across all realms.\n"
                           "Process will run without interruption until completion.").replace('{count}', str(len(unique_names))),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Create progress dialog with beautiful steps
            from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration
            
            steps = StepConfiguration.build_steps(
                StepConfiguration.DB_EDITOR_BATCH_SCAN,
                StepConfiguration.CLEANUP
            )
            
            progress = ProgressStepsDialog(
                parent=self,
                title=lang.get('db_editor.batch_full_scan_title', default="🔍 Batch Full Scan"),
                steps=steps,
                description=lang.get('db_editor.batch_full_scan_desc', 
                    default=f"Searching all variants for {len(unique_names)} item(s)..."),
                show_progress_bar=True,
                determinate_progress=True,
                allow_cancel=True
            )
            
            progress.show()
            # Force multiple processEvents to ensure UI is fully rendered
            for _ in range(3):
                QApplication.processEvents()
            
            # Step 0: Connect to Eden
            progress.start_step(0)
            progress.set_status_message("🔌 Connecting to Eden Herald...")
            QApplication.processEvents()
            from Functions.eden_scraper import _connect_to_eden_herald
            from Functions.items_scraper import ItemsScraper
            
            eden_scraper, error_message = _connect_to_eden_herald(headless=False)
            if not eden_scraper:
                progress.error_step(0, error_message)
                progress.close()
                QMessageBox.critical(self,
                    lang.get('error_title', default="Error"),
                    f"{lang.get('db_editor.full_scan_connect_error', default='Failed to connect to Eden Herald')}:\n{error_message}")
                return
            
            progress.complete_step(0)
            
            try:
                items_scraper = ItemsScraper(eden_scraper)
                
                # Results tracking
                total_variants_found = 0
                total_items_added = 0
                items_without_price = []  # [(key, name, realm), ...]
                scan_results = []  # [(item_name, variants_count, added_count), ...]
                
                # Step 1: Batch search
                progress.start_step(1)
                
                # Step 2: Batch process
                progress.start_step(2)
                
                # Process each unique item name
                for i, item_name in enumerate(unique_names):
                    if progress.was_canceled():
                        break
                    
                    # Update progress
                    percentage = int((i / len(unique_names)) * 100)
                    progress.update_progress(percentage)
                    progress.set_status_message(f"🔍 {item_name} ({i+1}/{len(unique_names)})")
                    QApplication.processEvents()
                    
                    # Find all variants
                    variants = items_scraper.find_all_item_variants(item_name, skip_filters=True)
                    
                    if not variants:
                        scan_results.append((item_name, 0, 0))
                        continue
                    
                    total_variants_found += len(variants)
                    
                    # Remove old entries for this item name
                    old_keys_to_remove = [
                        key for key, item_data in self.database.get('items', {}).items()
                        if item_data.get('name') == item_name
                    ]
                    for key in old_keys_to_remove:
                        del self.database['items'][key]
                    
                    # Add all new variants
                    items_added = 0
                    for variant in variants:
                        variant_id = variant.get('id')
                        variant_realm = variant.get('realm', 'All')
                        
                        # Generate item key
                        item_key = f"{item_name}_{variant_realm}"
                        
                        # Get full details
                        item_details = items_scraper.get_item_details(
                            item_id=variant_id,
                            realm=variant_realm,
                            item_name=item_name
                        )
                        
                        if not item_details:
                            continue
                        
                        # Add new variant
                        self.database['items'][item_key] = {
                            'id': item_details.get('id', ''),
                            'name': item_name,
                            'realm': variant_realm,
                            'slot': item_details.get('slot', ''),
                            'type': item_details.get('type', ''),
                            'model': item_details.get('model', ''),
                            'dps': item_details.get('dps', ''),
                            'speed': item_details.get('speed', ''),
                            'damage_type': item_details.get('damage_type', ''),
                            'usable_by': item_details.get('usable_by', 'ALL'),
                            'merchant_zone': item_details.get('merchant_zone', ''),
                            'merchant_price': item_details.get('merchant_price', ''),
                            'merchant_currency': item_details.get('merchant_currency', ''),
                            'item_category': '',
                            'ignore_item': False,
                            'source': 'scraped'
                        }
                        items_added += 1
                        total_items_added += 1
                        
                        # Track items without price
                        if not item_details.get('merchant_price'):
                            items_without_price.append((item_key, item_name, variant_realm))
                    
                    scan_results.append((item_name, len(variants), items_added))
                
                progress.update_progress(100)
                progress.complete_step(2)
                
                # Step 3: Save
                if total_items_added > 0:
                    progress.start_step(3)
                    self._save_database()
                    progress.complete_step(3)
                else:
                    progress.skip_step(3, "No items added")
                
                # Step 4: Results (skip, shown separately)
                progress.skip_step(4, "Shown in separate dialog")
                
                # Step 5: Cleanup
                progress.start_step(5)
                
            finally:
                eden_scraper.close()
                progress.complete_step(5)
                
                # Defer refresh to prevent UI blocking
                from PySide6.QtCore import QTimer
                QTimer.singleShot(100, self._refresh_display_after_scan)
                
                # Close progress and show results with delays to prevent blocking
                QTimer.singleShot(500, progress.close)
                QTimer.singleShot(600, lambda: self._show_batch_scan_results(
                    scan_results, total_variants_found, total_items_added, items_without_price))
                
        except Exception as e:
            logging.error(f"Error in batch full scan: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.batch_full_scan_error', default='Batch full scan failed')}:\n{str(e)}")
    
    def _show_batch_scan_results(self, scan_results: list, total_variants: int, total_added: int, items_without_price: list):
        """Show batch scan results in a dialog with option to tag items without price
        
        Args:
            scan_results: List of (item_name, variants_count, added_count) tuples
            total_variants: Total number of variants found
            total_added: Total number of items added
            items_without_price: List of (key, name, realm) tuples for items without price
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(lang.get('db_editor.batch_scan_results_title', default="Batch Scan Results"))
        dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout(dialog)
        
        # Summary label
        summary_text = f"<b>{lang.get('db_editor.batch_scan_summary', default='Scan Summary')}:</b><br>"
        summary_text += f"{lang.get('db_editor.batch_scan_items_scanned', default='Items scanned')}: {len(scan_results)}<br>"
        summary_text += f"{lang.get('db_editor.batch_scan_variants_found', default='Total variants found')}: {total_variants}<br>"
        summary_text += f"{lang.get('db_editor.batch_scan_items_added', default='Items added/updated')}: {total_added}<br>"
        summary_text += f"{lang.get('db_editor.batch_scan_no_price', default='Items without price')}: {len(items_without_price)}"
        
        summary_label = QLabel(summary_text)
        layout.addWidget(summary_label)
        
        # Details table
        details_label = QLabel(f"<b>{lang.get('db_editor.batch_scan_details', default='Details')}:</b>")
        layout.addWidget(details_label)
        
        details_table = QTableWidget()
        details_table.setColumnCount(3)
        details_table.setHorizontalHeaderLabels([
            lang.get('db_editor.item_name', default="Item Name"),
            lang.get('db_editor.variants_found', default="Variants Found"),
            lang.get('db_editor.items_added', default="Added")
        ])
        details_table.horizontalHeader().setStretchLastSection(True)
        details_table.setEditTriggers(QTableWidget.NoEditTriggers)
        details_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        details_table.setRowCount(len(scan_results))
        for row, (item_name, variants_count, added_count) in enumerate(scan_results):
            details_table.setItem(row, 0, QTableWidgetItem(item_name))
            details_table.setItem(row, 1, QTableWidgetItem(str(variants_count)))
            details_table.setItem(row, 2, QTableWidgetItem(str(added_count)))
        
        details_table.resizeColumnsToContents()
        layout.addWidget(details_table)
        
        # Items without price section
        if items_without_price:
            no_price_label = QLabel(f"<b>{lang.get('db_editor.batch_scan_no_price_items', default='Items without price')}:</b>")
            layout.addWidget(no_price_label)
            
            no_price_list = QListWidget()
            no_price_list.setMaximumHeight(150)
            for item_key, item_name, realm in items_without_price:
                no_price_list.addItem(f"{item_name} ({realm})")
            layout.addWidget(no_price_list)
            
            # Tag button
            tag_button = QPushButton(f"🏷️ {lang.get('db_editor.batch_scan_tag_items', default='Tag Items Without Price')}")
            tag_button.clicked.connect(lambda: self._tag_items_from_batch_scan(items_without_price, dialog))
            layout.addWidget(tag_button)
        
        # Close button
        close_button = QPushButton(lang.get('close', default="Close"))
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def _tag_items_from_batch_scan(self, items_without_price: list, parent_dialog: QDialog):
        """Tag items without price from batch scan results
        
        Args:
            items_without_price: List of (key, name, realm) tuples
            parent_dialog: Parent dialog to close after tagging
        """
        try:
            # Ask for category
            category_dialog = QDialog(parent_dialog)
            category_dialog.setWindowTitle(lang.get('db_editor.tag_category_title', default="Select Category"))
            category_dialog.setMinimumWidth(400)
            category_layout = QVBoxLayout(category_dialog)
            
            info_label = QLabel(lang.get('db_editor.tag_category_info',
                default=f"Select a category for {len(items_without_price)} item(s):"))
            category_layout.addWidget(info_label)
            
            category_group = QGroupBox(lang.get('db_editor.tag_category_label', default="Category"))
            category_button_layout = QVBoxLayout()
            
            quest_radio = QRadioButton("🏆 " + lang.get('db_editor.tag_quest_reward', default="Quest Reward"))
            event_radio = QRadioButton("🎉 " + lang.get('db_editor.tag_event_reward', default="Event Reward"))
            unknown_radio = QRadioButton("❓ " + lang.get('db_editor.tag_unknown', default="Unknown Source"))
            quest_radio.setChecked(True)
            
            category_button_layout.addWidget(quest_radio)
            category_button_layout.addWidget(event_radio)
            category_button_layout.addWidget(unknown_radio)
            category_group.setLayout(category_button_layout)
            category_layout.addWidget(category_group)
            
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(category_dialog.accept)
            buttons.rejected.connect(category_dialog.reject)
            category_layout.addWidget(buttons)
            
            if category_dialog.exec() != QDialog.Accepted:
                return
            
            # Determine selected category
            if quest_radio.isChecked():
                category = 'quest_reward'
            elif event_radio.isChecked():
                category = 'event_reward'
            else:
                category = 'unknown'
            
            # Apply tag to all items
            for item_key, item_name, realm in items_without_price:
                if item_key in self.database['items']:
                    self.database['items'][item_key]['item_category'] = category
                    self.database['items'][item_key]['ignore_item'] = (category != 'unknown')
            
            # Save and refresh
            self._save_database()
            
            # Refresh display
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._refresh_display_after_scan)
            
            # Close parent dialog
            parent_dialog.accept()
            
            QMessageBox.information(self,
                lang.get('success_title', default="Success"),
                lang.get('db_editor.batch_tag_success',
                    default="{count} item(s) tagged successfully!").replace('{count}', str(len(items_without_price))))
            
        except Exception as e:
            logging.error(f"Error tagging items from batch scan: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.batch_tag_error', default='Failed to tag items')}:\n{str(e)}")
    
    def _batch_tag_items(self, items_data: list, category: str):
        """Batch tag multiple items with a category
        
        Args:
            items_data: List of dicts with 'key', 'name', 'id'
            category: Category to apply
        """
        try:
            # Apply tag to all selected items
            for item_data in items_data:
                item_key = item_data['key']
                if item_key in self.database['items']:
                    self.database['items'][item_key]['item_category'] = category
                    self.database['items'][item_key]['ignore_item'] = (category != 'unknown')
            
            # Save and refresh
            self._save_database()
            
            # Defer refresh
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._refresh_display_after_scan)
            
        except Exception as e:
            logging.error(f"Error in batch tagging: {e}", exc_info=True)
            QMessageBox.critical(self,
                lang.get('error_title', default="Error"),
                f"{lang.get('db_editor.batch_tag_error', default='Batch tagging failed')}:\n{str(e)}")







