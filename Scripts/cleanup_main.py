"""
Script to clean up main.py by removing extracted UI classes.
"""

def clean_main():
    with open('main.py.backup', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where CharacterApp starts
    char_app_start = content.find('class CharacterApp(QMainWindow):')
    
    # Find where apply_theme starts
    apply_theme_start = content.find('\ndef apply_theme(app):')
    
    # Extract the three parts
    header = content[:52]  # All imports and setup_logging()
    char_app_and_functions = content[char_app_start:apply_theme_start+1]  # CharacterApp + functions
    final_functions = content[apply_theme_start+1:]  # apply_theme + main + if __name__
    
    # Create new header with cleaner imports
    new_header = '''"""
DAOC Character Manager - Main Application Entry Point
A PySide6-based character management application for Dark Age of Camelot.
"""

import os
import sys
import traceback
import logging

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTreeView, QStatusBar, 
    QLabel, QMessageBox, QMenu, QFileDialog, QHeaderView, QInputDialog,
    QToolButton, QSizePolicy, QStyleFactory
)
from PySide6.QtGui import (
    QFont, QStandardItemModel, QStandardItem, QIcon, QAction, 
    QGuiApplication, QPalette
)
from PySide6.QtCore import Qt, QSize, QByteArray

from Functions.character_manager import (
    create_character_data, save_character, get_all_characters, get_character_dir, 
    REALM_ICONS, delete_character, REALMS, rename_character, duplicate_character
)
from Functions.language_manager import lang, get_available_languages
from Functions.config_manager import config, get_config_dir
from Functions.logging_manager import setup_logging, get_log_dir, get_img_dir
from Functions.data_manager import DataManager

# Import UI components from modular UI package
from UI import (
    DebugWindow, QTextEditHandler, LogLevelFilter, LogFileReaderThread,
    CharacterSheetWindow, ColumnsConfigDialog, NewCharacterDialog, ConfigurationDialog,
    CenterIconDelegate, CenterCheckboxDelegate, RealmTitleDelegate
)

# Setup logging at the very beginning
setup_logging()

# Application Constants
APP_NAME = "Character Manager"
APP_VERSION = "0.1"


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catches unhandled exceptions and logs them with full traceback."""
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_string = "".join(tb_lines)
    logging.critical(f"Unhandled exception caught:\\n{tb_string}")


'''
    
    # Combine all parts
    new_content = new_header + char_app_and_functions + final_functions
    
    # Write to new file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ main.py cleaned successfully")
    print(f"  - Old size: {len(content)} characters")
    print(f"  - New size: {len(new_content)} characters")
    print(f"  - Reduced by: {len(content) - len(new_content)} characters")

if __name__ == '__main__':
    clean_main()
