"""
Armor Resistances Dialog UI - Creates and manages the armor resistance table dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QPushButton, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from Functions.language_manager import lang
from Functions.armor_resists_manager import (
    armor_resists_load_data,
    armor_resists_get_realms_data,
    armor_resists_format_cell_value,
    armor_resists_get_cell_color
)


def ui_armor_resists_create_dialog(parent=None):
    """
    Create and return the armor resistance table dialog.
    
    Args:
        parent: Parent widget.
    
    Returns:
        QDialog: The armor resistance dialog.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(lang.get("armor_resists.dialog.title", default="🛡️ Armor Resistances"))
    dialog.setGeometry(100, 100, 1000, 600)
    
    layout = QVBoxLayout()
    
    # Realm selector
    selector_layout = QVBoxLayout()
    realm_label = QLabel(lang.get("armor_resists.realm_label", default="Select Realm:"))
    realm_combo = QComboBox()
    selector_layout.addWidget(realm_label)
    selector_layout.addWidget(realm_combo)
    
    layout.addLayout(selector_layout)
    
    # Table widget
    table = QTableWidget()
    table.setColumnCount(0)
    table.setRowCount(0)
    layout.addWidget(table)
    
    # Close button
    close_button = QPushButton(lang.get("common.close_button", default="Close"))
    close_button.clicked.connect(dialog.accept)
    layout.addWidget(close_button)
    
    dialog.setLayout(layout)
    
    # Load and populate data
    ui_armor_resists_load_and_populate(dialog, realm_combo, table)
    
    # Connect realm selection change
    realm_combo.currentIndexChanged.connect(
        lambda: ui_armor_resists_populate_realm(table, realm_combo)
    )
    
    return dialog


def ui_armor_resists_load_and_populate(dialog, realm_combo, table):
    """
    Load armor resistance data and populate the realm selector.
    
    Args:
        dialog: The dialog instance.
        realm_combo: The realm combo box.
        table: The table widget.
    """
    data = armor_resists_load_data()
    
    if not data:
        table.setColumnCount(1)
        table.setRowCount(1)
        item = QTableWidgetItem(lang.get("error.data_load_failed", default="Error loading data"))
        table.setItem(0, 0, item)
        return
    
    realms = armor_resists_get_realms_data(data)
    
    # Populate realm combo box
    realm_mapping = {
        "albion": lang.get("armor_resists.realm.albion", default="Albion"),
        "midgard": lang.get("armor_resists.realm.midgard", default="Midgard"),
        "hibernia": lang.get("armor_resists.realm.hibernia", default="Hibernia")
    }
    
    for realm_key in ["albion", "midgard", "hibernia"]:
        if realm_key in realms:
            realm_combo.addItem(realm_mapping[realm_key], realm_key)
    
    # Populate table with first realm
    if realm_combo.count() > 0:
        ui_armor_resists_populate_realm(table, realm_combo)


def ui_armor_resists_populate_realm(table, realm_combo):
    """
    Populate the table with data for the selected realm.
    
    Args:
        table: The table widget.
        realm_combo: The realm combo box.
    """
    realm_key = realm_combo.currentData()
    
    if not realm_key:
        return
    
    data = armor_resists_load_data()
    realms = armor_resists_get_realms_data(data)
    
    if realm_key not in realms:
        return
    
    realm_data = realms[realm_key]
    headers = realm_data.get("headers", [])
    rows = realm_data.get("data", [])
    
    # Set table dimensions
    table.setColumnCount(len(headers))
    table.setRowCount(len(rows))
    
    # Set headers
    header_names = []
    lang_code = lang.current_language
    for header in headers:
        # Get translated name or default to English name
        name_key = f"name_{lang_code}" if lang_code != "en" else "name"
        header_text = header.get(name_key, header.get("name", ""))
        header_names.append(header_text)
    
    table.setHorizontalHeaderLabels(header_names)
    
    # Populate rows
    for row_idx, row_data in enumerate(rows):
        lang_code = lang.current_language
        for col_idx, header in enumerate(headers):
            header_name = header.get("name", "")
            cell_value = row_data.get(header_name, "")
            
            # Format the cell value
            if header_name != "Class" and header_name != "Armor Type":
                # These are resistance values
                display_value = armor_resists_format_cell_value(cell_value)
            else:
                # Class and Armor Type columns - use localized version if available
                localized_key = f"{header_name}_{lang_code}" if lang_code != "en" else header_name
                display_value = row_data.get(localized_key, row_data.get(header_name, ""))
            
            item = QTableWidgetItem(display_value)
            
            # Set color for resistance values (not for Class/Armor Type columns)
            if header_name not in ["Class", "Armor Type"]:
                color = armor_resists_get_cell_color(cell_value)
                if color:
                    text_color = QColor(255, 255, 255)  # White text
                    bg_color = QColor(*color)
                    item.setBackground(QBrush(bg_color))
                    item.setForeground(QBrush(text_color))
            
            # Center align and bold header row
            item.setTextAlignment(Qt.AlignCenter)
            if row_idx == 0:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            table.setItem(row_idx, col_idx, item)
    
    # Resize columns to content
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)


def ui_armor_resists_apply_cell_colors(table):
    """
    Apply color formatting to all cells in the table based on their values.
    
    Args:
        table: The table widget to format.
    """
    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item is None:
                continue
            
            # Skip class and armor type columns (first two)
            if col < 2:
                continue
            
            # Get the original value and apply color
            value = item.text()
            color = armor_resists_get_cell_color(value)
            
            if color:
                text_color = QColor(255, 255, 255)  # White text
                bg_color = QColor(*color)
                item.setBackground(QBrush(bg_color))
                item.setForeground(QBrush(text_color))
