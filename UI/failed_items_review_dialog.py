"""
Failed Items Review Dialog
Allows user to review and retry items that were filtered during mass import
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                               QCheckBox, QMessageBox, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from Functions.language_manager import LanguageManager

lang = LanguageManager()


class FailedItemsReviewDialog(QDialog):
    """Dialog to review and selectively retry filtered items"""
    
    def __init__(self, filtered_items, parent=None):
        """
        Args:
            filtered_items: List of dicts with keys: name, realm, reason, level, utility, id, original_search
        """
        super().__init__(parent)
        self.filtered_items = filtered_items
        self.selected_items = []
        self.ignored_items = []  # Items to permanently ignore
        
        self.setWindowTitle(lang.get("settings.pages.failed_items.title", default="Review Filtered Items"))
        self.setMinimumSize(800, 500)
        self.setWindowFlags(Qt.Window)
        
        self.setup_ui()
        self.populate_table()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(lang.get("settings.pages.failed_items.header", 
            default=f"📋 {len(self.filtered_items)} item(s) were filtered during import"))
        header_label.setStyleSheet("font-size: 12pt; font-weight: bold; padding: 10px;")
        layout.addWidget(header_label)
        
        # Info label
        info_label = QLabel(lang.get("settings.pages.failed_items.info", 
            default="Select items to retry import WITHOUT filters (Level/Utility restrictions will be ignored)"))
        info_label.setStyleSheet("color: #ce9178; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons bar (top)
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton(lang.get("settings.pages.failed_items.select_all", default="☑ Select All"))
        self.select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton(lang.get("settings.pages.failed_items.deselect_all", default="☐ Deselect All"))
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(self.deselect_all_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            lang.get("settings.pages.failed_items.col_select", default="Select"),
            lang.get("settings.pages.failed_items.col_name", default="Item Name"),
            lang.get("settings.pages.failed_items.col_realm", default="Realm"),
            lang.get("settings.pages.failed_items.col_reason", default="Filter Reason"),
            lang.get("settings.pages.failed_items.col_level", default="Level"),
            lang.get("settings.pages.failed_items.col_utility", default="Utility")
        ])
        
        # Enable text selection for copy/paste
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252526;
                gridline-color: #3a3a3a;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 5px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
            }
        """)
        
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("padding: 5px; color: #9cdcfe;")
        layout.addWidget(self.stats_label)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.retry_btn = QPushButton(lang.get("settings.pages.failed_items.retry_selected", default="🔄 Retry Selected Items"))
        self.retry_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.retry_btn.clicked.connect(self.on_retry_clicked)
        self.retry_btn.setEnabled(False)
        action_layout.addWidget(self.retry_btn)
        
        self.ignore_btn = QPushButton(lang.get("settings.pages.failed_items.ignore_selected", default="🚫 Ignore Selected Items"))
        self.ignore_btn.setStyleSheet("""
            QPushButton {
                background-color: #854545;
                color: white;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #a05555;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.ignore_btn.clicked.connect(self.on_ignore_clicked)
        self.ignore_btn.setEnabled(False)
        action_layout.addWidget(self.ignore_btn)
        
        self.cancel_btn = QPushButton(lang.get("settings.pages.failed_items.close", default="Close"))
        self.cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(action_layout)
    
    def populate_table(self):
        """Populate table with filtered items"""
        self.table.setRowCount(len(self.filtered_items))
        
        for row, item in enumerate(self.filtered_items):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.on_selection_changed)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)
            
            # Item name
            name_item = QTableWidgetItem(item.get('name', 'Unknown'))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable | Qt.ItemIsSelectable)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 1, name_item)
            
            # Realm
            realm = item.get('realm', 'Unknown')
            realm_item = QTableWidgetItem(realm)
            realm_item.setFlags(realm_item.flags() & ~Qt.ItemIsEditable)
            
            # Color by realm
            if realm == 'Albion':
                realm_item.setForeground(QColor("#ff6b6b"))
            elif realm == 'Hibernia':
                realm_item.setForeground(QColor("#4ecdc4"))
            elif realm == 'Midgard':
                realm_item.setForeground(QColor("#95e1d3"))
            else:
                realm_item.setForeground(QColor("#cccccc"))
            
            self.table.setItem(row, 2, realm_item)
            
            # Filter reason
            reason = item.get('reason', 'unknown')
            if reason == 'level_too_low':
                reason_text = lang.get("settings.pages.failed_items.reason_level", default="Level < 50")
                reason_color = QColor("#ce9178")
            elif reason == 'utility_too_low':
                reason_text = lang.get("settings.pages.failed_items.reason_utility", default="Utility < 100")
                reason_color = QColor("#c586c0")
            elif reason == 'no_merchant':
                reason_text = lang.get("settings.pages.failed_items.reason_no_merchant", default="No Merchant")
                reason_color = QColor("#f48771")
            elif reason == 'currency_not_supported':
                currency = item.get('currency', 'Unknown')
                reason_text = lang.get("settings.pages.failed_items.reason_currency", default=f"Currency: {currency}")
                reason_color = QColor("#dcdcaa")
            else:
                reason_text = reason
                reason_color = QColor("#cccccc")
            
            reason_item = QTableWidgetItem(reason_text)
            reason_item.setFlags(reason_item.flags() & ~Qt.ItemIsEditable)
            reason_item.setForeground(reason_color)
            self.table.setItem(row, 3, reason_item)
            
            # Level
            level = item.get('level')
            level_text = str(level) if level is not None else "N/A"
            level_item = QTableWidgetItem(level_text)
            level_item.setFlags(level_item.flags() & ~Qt.ItemIsEditable)
            if level is not None and level < 50:
                level_item.setForeground(QColor("#f48771"))
            self.table.setItem(row, 4, level_item)
            
            # Utility
            utility = item.get('utility')
            utility_text = str(utility) if utility is not None else "N/A"
            utility_item = QTableWidgetItem(utility_text)
            utility_item.setFlags(utility_item.flags() & ~Qt.ItemIsEditable)
            if utility is not None and utility < 100:
                utility_item.setForeground(QColor("#f48771"))
            self.table.setItem(row, 5, utility_item)
        
        self.update_stats()
    
    def select_all(self):
        """Select all items"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(True)
    
    def deselect_all(self):
        """Deselect all items"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(False)
    
    def on_selection_changed(self):
        """Update UI when selection changes"""
        self.update_stats()
    
    def update_stats(self):
        """Update statistics label"""
        selected_count = 0
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        
        self.stats_label.setText(
            lang.get("settings.pages.failed_items.stats", selected=selected_count, total=len(self.filtered_items),
                    default=f"📊 {selected_count} / {len(self.filtered_items)} items selected for retry")
        )
        
        self.retry_btn.setEnabled(selected_count > 0)
        self.retry_btn.setText(
            lang.get("settings.pages.failed_items.retry_selected", count=selected_count, 
                    default=f"🔄 Retry Selected Items ({selected_count})")
        )
        
        self.ignore_btn.setEnabled(selected_count > 0)
        self.ignore_btn.setText(
            lang.get("settings.pages.failed_items.ignore_selected", count=selected_count,
                    default=f"🚫 Ignore Selected Items ({selected_count})")
        )
    
    def on_retry_clicked(self):
        """Handle retry button click"""
        # Collect selected items
        self.selected_items = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                self.selected_items.append(self.filtered_items[row])
        
        if not self.selected_items:
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            lang.get("settings.pages.failed_items.confirm_title", default="Confirm Retry"),
            lang.get("settings.pages.failed_items.confirm_message", count=len(self.selected_items),
                    default=f"Retry import for {len(self.selected_items)} item(s) WITHOUT filters?\n\n"
                            f"⚠️ This will ignore Level and Utility restrictions."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Store selected items but DO NOT close dialog yet
            # The parent will handle the retry and close the dialog when done
            self.accept()
    
    def get_selected_items(self):
        """Return list of selected items for retry"""
        return self.selected_items
    
    def get_ignored_items(self):
        """Return list of items to permanently ignore"""
        return self.ignored_items
    
    def on_ignore_clicked(self):
        """Handle ignore button click"""
        # Collect selected items
        selected = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                selected.append(self.filtered_items[row])
        
        if not selected:
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            lang.get("settings.pages.failed_items.ignore_confirm_title", default="Confirm Ignore"),
            lang.get("settings.pages.failed_items.ignore_confirm_message", count=len(selected),
                    default=f"Permanently ignore {len(selected)} item(s)?\n\n"
                            f"⚠️ These items will never appear in future imports.\n"
                            f"You can manage ignored items later."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.ignored_items = selected
            
            # Remove ignored items from filtered_items and table
            rows_to_remove = []
            for row in range(self.table.rowCount()):
                checkbox_widget = self.table.cellWidget(row, 0)
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    rows_to_remove.append(row)
            
            # Remove rows in reverse order to avoid index issues
            for row in reversed(rows_to_remove):
                self.filtered_items.pop(row)
                self.table.removeRow(row)
            
            # Update header and stats
            header_label = self.findChild(QLabel)
            if header_label:
                header_label.setText(lang.get("settings.pages.failed_items.header", count=len(self.filtered_items),
                    default=f"📋 {len(self.filtered_items)} item(s) were filtered during import"))
            
            self.update_stats()
            
            # Show confirmation message
            QMessageBox.information(
                self,
                lang.get("settings.pages.failed_items.ignore_success_title", default="Items Ignored"),
                lang.get("settings.pages.failed_items.ignore_success_message", count=len(selected),
                        default=f"{len(selected)} item(s) have been marked as ignored.\n\nThey will be processed when you close this dialog.")
            )
            
            # If no items left, close dialog
            if len(self.filtered_items) == 0:
                self.done(2)
