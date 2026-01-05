"""
Armor Resistances Dialog UI - Creates and manages the armor resistance table dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from Functions.language_manager import lang
from Functions.armor_resists_manager import (
    armor_resists_load_data,
    armor_resists_get_realms_data,
    armor_resists_get_cell_color
)


def ui_armor_resists_create_dialog(parent=None):
    """
    Create and return the armor resistance table dialog with tabs for each realm.
    
    Args:
        parent: Parent widget.
    
    Returns:
        QDialog: The armor resistance dialog.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(lang.get("armor_resists.dialog.title", default="🛡️ Armor Resistances"))
    
    # Add maximize/minimize buttons
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
    
    layout = QVBoxLayout()
    
    # Tab widget for realms
    tab_widget = QTabWidget()
    
    # Load data
    data = armor_resists_load_data()
    
    if not data:
        dialog.setLayout(layout)
        dialog.setGeometry(100, 100, 600, 400)
        return dialog
    
    realms = armor_resists_get_realms_data(data)
    
    # Create tab for each realm
    realm_mapping = {
        "albion": lang.get("armor_resists.realm.albion", default="Albion"),
        "midgard": lang.get("armor_resists.realm.midgard", default="Midgard"),
        "hibernia": lang.get("armor_resists.realm.hibernia", default="Hibernia")
    }
    
    for realm_key in ["albion", "midgard", "hibernia"]:
        if realm_key in realms:
            table = QTableWidget()
            tab_widget.addTab(table, realm_mapping[realm_key])
            ui_armor_resists_populate_table(table, realms[realm_key])
    
    layout.addWidget(tab_widget)
    dialog.setLayout(layout)
    
    # Auto-adjust size based on content
    ui_armor_resists_adjust_dialog_size(dialog, tab_widget)
    
    return dialog


def ui_armor_resists_load_and_populate(dialog, realm_combo, table):
    """
    Load armor resistance data and populate the realm selector.
    
    Args:
        dialog: The dialog instance.
        realm_combo: The realm combo box.
        table: The table widget.
    """
    pass  # No longer used with tab widget


def ui_armor_resists_adjust_dialog_size(dialog, tab_widget):
    """
    Adjust dialog size based on content (tables and tabs).
    
    Args:
        dialog: The dialog instance.
        tab_widget: The QTabWidget containing the tables.
    """
    # Get the first table to calculate size
    if tab_widget.count() == 0:
        dialog.setGeometry(100, 100, 1000, 500)
        return
    
    first_table = tab_widget.widget(0)
    
    # Calculate required width based on columns
    width = 0
    for col in range(first_table.columnCount()):
        width += first_table.columnWidth(col)
    
    # Add generous spacing for vertical scrollbar, borders, and padding
    width += 150
    
    # Calculate required height based on rows and headers
    height = 0
    
    # Header height
    if first_table.horizontalHeader():
        height += first_table.horizontalHeader().height()
    
    # Rows height
    for row in range(first_table.rowCount()):
        height += first_table.rowHeight(row)
    
    # Add tab bar height
    height += tab_widget.tabBar().height() if tab_widget.tabBar() else 30
    
    # Add spacing for horizontal scrollbar and borders
    height += 80
    
    # Constrain size to reasonable limits
    # Minimum: 1000x500 (wider to accommodate all columns)
    # Maximum: 95% of screen size
    screen = dialog.screen()
    screen_rect = screen.availableGeometry()
    
    max_width = int(screen_rect.width() * 0.95)
    max_height = int(screen_rect.height() * 0.95)
    
    final_width = max(1000, min(width, max_width))
    final_height = max(500, min(height, max_height))
    
    # Center the dialog on screen
    x = (screen_rect.width() - final_width) // 2 + screen_rect.x()
    y = (screen_rect.height() - final_height) // 2 + screen_rect.y()
    
    dialog.setGeometry(x, y, final_width, final_height)



def ui_armor_resists_populate_realm(table, realm_combo):
    """
    Populate the table with data for the selected realm.
    
    Args:
        table: The table widget.
        realm_combo: The realm combo box.
    """
    pass  # No longer used with tab widget


def ui_armor_resists_populate_table(table, realm_data):
    """
    Populate a table with data for a specific realm.
    
    Args:
        table: The table widget.
        realm_data: The realm data dictionary.
    """
    headers = realm_data.get("headers", [])
    rows = realm_data.get("data", [])
    
    # Set table dimensions
    table.setColumnCount(len(headers))
    table.setRowCount(len(rows))
    
    # Hide row numbers
    table.verticalHeader().hide()
    
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
            
            # Display the cell value
            if header_name != "Class" and header_name != "Armor Type":
                # These are resistance values - display raw value (not symbols)
                display_value = str(cell_value)
            else:
                # Class and Armor Type columns - use localized version if available
                localized_key = f"{header_name}_{lang_code}" if lang_code != "en" else header_name
                display_value = row_data.get(localized_key, row_data.get(header_name, ""))
            
            item = QTableWidgetItem(display_value)
            
            # Set color for resistance values (only text color, not background)
            if header_name not in ["Class", "Armor Type"]:
                color = armor_resists_get_cell_color(cell_value)
                if color:
                    text_color = QColor(*color)
                    item.setForeground(QBrush(text_color))
            
            # Center align
            item.setTextAlignment(Qt.AlignCenter)
            
            table.setItem(row_idx, col_idx, item)
    
    # Resize columns to content
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
