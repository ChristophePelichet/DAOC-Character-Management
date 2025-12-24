"""
Debug window and logging utilities for the DAOC Character Manager.
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QTextEdit, QPushButton, QLineEdit, QSplitter, QLabel,
    QComboBox
)
from PySide6.QtCore import QThread, Signal, Slot, Qt
from PySide6.QtGui import QAction, QActionGroup
from Functions.language_manager import lang
from Functions.debug_logging_manager import ALL_LOGGERS
from UI.ui_file_dialogs import (
    dialog_open_file,
    dialog_save_file
)


class QTextEditHandler(logging.Handler):
    """A custom logging handler that sends log records to a QTextEdit widget via callback."""

    def __init__(self, callback):
        logging.Handler.__init__(self)
        self.callback = callback

    def emit(self, record):
        """Override logging.Handler.emit() to send logs via callback."""
        msg = self.format(record)
        if self.callback:
            self.callback(msg)


class LogLevelFilter(logging.Filter):
    """Filters log records based on a minimum and maximum level."""
    
    def __init__(self, min_level, max_level):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record):
        return self.min_level <= record.levelno <= self.max_level


class LoggerNameFilter(logging.Filter):
    """Filter logs based on logger name."""
    
    def __init__(self, allowed_loggers=None):
        super().__init__()
        self.allowed_loggers = allowed_loggers if allowed_loggers else []

    def filter(self, record):
        if not self.allowed_loggers:
            return True
        # Map 'ROOT' to 'root' (actual root logger name in Python logging)
        # and allow the specified loggers
        display_name = 'ROOT' if record.name == 'root' else record.name
        return display_name in self.allowed_loggers or record.name == 'root'
    
    def set_allowed_loggers(self, loggers):
        """Update the list of allowed loggers."""
        self.allowed_loggers = loggers if loggers else []


class LogFileReaderThread(QThread):
    """A QThread to monitor a log file without blocking the GUI."""
    
    new_line = Signal(str)

    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self._is_running = True

    def run(self):
        """Monitor the log file for new lines."""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, 2)  # Go to the end of the file
                while self._is_running:
                    line = f.readline()
                    if line:
                        self.new_line.emit(line)
                    else:
                        self.msleep(100)  # Wait for new lines
        except Exception as e:
            error_message = f"Error monitoring file {self.filepath}: {e}\n"
            self.new_line.emit(error_message)

    def stop(self):
        """Stop monitoring the log file."""
        self._is_running = False


class DebugWindow(QMainWindow):
    """A window that displays log messages in real-time."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("debug_window_title"))
        self.setGeometry(100, 100, 1200, 700)
        self.monitoring_thread = None
        self.current_log_level = logging.DEBUG
        self.current_loggers = []  # All loggers selected by default

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Menu Bar
        self._create_menus()
        
        # Button Bar with Logger Dropdown
        button_bar_layout = QHBoxLayout()
        
        # Logger dropdown
        logger_label = QLabel("🔍 Filter Logger:")
        self.logger_combo = QComboBox()
        self.logger_combo.addItem("📋 All Loggers", ALL_LOGGERS + ['ROOT'])
        self.logger_combo.addItem("─" * 30)  # Separator
        for logger_name in ALL_LOGGERS:
            self.logger_combo.addItem(f"  {logger_name}", [logger_name, 'ROOT'])
        self.logger_combo.currentIndexChanged.connect(self._on_logger_combo_changed)
        button_bar_layout.addWidget(logger_label)
        button_bar_layout.addWidget(self.logger_combo)
        button_bar_layout.addSpacing(20)
        
        test_debug_button = QPushButton(lang.get("test_debug_button"))
        test_debug_button.clicked.connect(self.raise_test_exception)
        button_bar_layout.addWidget(test_debug_button)
        button_bar_layout.addStretch()
        main_layout.addLayout(button_bar_layout)

        # Main Splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left Pane (Logs & Errors)
        left_splitter = QSplitter(Qt.Vertical)
        
        log_group = QGroupBox(lang.get("debug_log_pane_title"))
        log_layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        log_layout.addWidget(self.log_widget)
        log_group.setLayout(log_layout)
        left_splitter.addWidget(log_group)

        error_group = QGroupBox(lang.get("debug_errors_pane_title"))
        error_layout = QVBoxLayout()
        self.error_widget = QTextEdit()
        self.error_widget.setReadOnly(True)
        error_layout.addWidget(self.error_widget)
        error_group.setLayout(error_layout)
        left_splitter.addWidget(error_group)
        
        left_splitter.setSizes([400, 200])
        main_splitter.addWidget(left_splitter)

        # Right Pane (Log Reader)
        reader_group = QGroupBox(lang.get("debug_log_reader_pane_title"))
        reader_layout = QVBoxLayout()
        
        file_bar_layout = QHBoxLayout()
        self.log_file_path_edit = QLineEdit()
        self.log_file_path_edit.setReadOnly(True)
        browse_button = QPushButton(lang.get("browse_button"))
        browse_button.clicked.connect(self.browse_log_file)
        clear_button = QPushButton(lang.get("clear_button_text"))
        clear_button.clicked.connect(self.clear_log_reader)
        file_bar_layout.addWidget(self.log_file_path_edit)
        file_bar_layout.addWidget(browse_button)
        file_bar_layout.addWidget(clear_button)
        reader_layout.addLayout(file_bar_layout)

        self.log_reader_widget = QTextEdit()
        self.log_reader_widget.setReadOnly(True)
        reader_layout.addWidget(self.log_reader_widget)
        reader_group.setLayout(reader_layout)
        main_splitter.addWidget(reader_group)

        main_splitter.setSizes([700, 500])

        # Setup Logging Handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create logger name filter (allow all loggers by default)
        self.logger_filter = LoggerNameFilter(ALL_LOGGERS + ['ROOT'])
        
        # General log handler (INFO and below)
        self.log_filter = LogLevelFilter(logging.DEBUG, logging.INFO)
        self.log_handler = QTextEditHandler(self.log_widget.append)
        self.log_handler.setFormatter(formatter)
        self.log_handler.addFilter(self.log_filter)
        self.log_handler.addFilter(self.logger_filter)
        logging.getLogger().addHandler(self.log_handler)

        # Error log handler (WARNING and above)
        self.error_filter = LogLevelFilter(logging.WARNING, logging.CRITICAL)
        self.error_handler = QTextEditHandler(self.error_widget.append)
        self.error_handler.setFormatter(formatter)
        self.error_handler.addFilter(self.error_filter)
        self.error_handler.addFilter(self.logger_filter)
        logging.getLogger().addHandler(self.error_handler)

    def _create_menus(self):
        """Create the menu bar with log level and logger filter options."""
        menu_bar = self.menuBar()

        # Level Menu
        level_menu = menu_bar.addMenu(lang.get("debug_level_menu"))
        level_action_group = QActionGroup(self)
        level_action_group.setExclusive(True)
        level_action_group.triggered.connect(self.set_log_level)

        log_levels_map = {
            lang.get("debug_level_all"): logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }

        for name, level in log_levels_map.items():
            action = QAction(name, self)
            action.setData(level)
            action.setCheckable(True)
            level_menu.addAction(action)
            level_action_group.addAction(action)
            if level == self.current_log_level:
                action.setChecked(True)

        # Logger Menu
        logger_menu = menu_bar.addMenu("Loggers")
        logger_action_group = QActionGroup(self)
        logger_action_group.setExclusive(True)
        logger_action_group.triggered.connect(self.set_logger_filter)

        # "All Loggers" option
        all_loggers_action = QAction("All Loggers", self)
        all_loggers_action.setData(ALL_LOGGERS + ['ROOT'])
        all_loggers_action.setCheckable(True)
        all_loggers_action.setChecked(True)
        logger_menu.addAction(all_loggers_action)
        logger_action_group.addAction(all_loggers_action)

        logger_menu.addSeparator()

        # Individual logger options
        for logger_name in ALL_LOGGERS:
            action = QAction(logger_name, self)
            action.setData([logger_name, 'ROOT'])  # Include ROOT with each logger
            action.setCheckable(True)
            logger_menu.addAction(action)
            logger_action_group.addAction(action)

    @Slot(QAction)
    def set_log_level(self, action):
        """Sets the minimum logging level for the handlers."""
        level = action.data()
        self.current_log_level = level
        logging.info(f"Debug window log level set to {logging.getLevelName(level)}")

        # Update filters
        self.log_filter.min_level = level
        self.error_filter.min_level = level

    @Slot(QAction)
    def set_logger_filter(self, action):
        """Update the logger filter based on the selected option."""
        loggers = action.data()
        self.current_loggers = loggers
        self.logger_filter.set_allowed_loggers(loggers)
        
        selected = ", ".join(loggers)
        logging.info(f"Debug window logger filter set to: {selected}")
    
    @Slot(int)
    def _on_logger_combo_changed(self, index):
        """Handle logger dropdown selection change."""
        if index < 0:
            return
        
        # Skip separator
        if self.logger_combo.itemText(index).startswith("─"):
            self.logger_combo.setCurrentIndex(0)
            return
        
        loggers = self.logger_combo.itemData(index)
        self.current_loggers = loggers
        self.logger_filter.set_allowed_loggers(loggers)
        
        selected = ", ".join(loggers)
        logging.info(f"🔍 Debug window logger filter set to: {selected}")
        
    def raise_test_exception(self):
        """Raises a test exception to verify the logging system."""
        logging.info("Raising a test exception...")
        1 / 0

    def browse_log_file(self):
        """Open a file dialog to select a log file to monitor."""
        filepath = dialog_open_file(self, "debug_log_reader_pane_title")
        if filepath:
            self.log_file_path_edit.setText(filepath)
            self.start_log_monitoring(filepath)

    def clear_log_reader(self):
        """Clear the log reader display."""
        self.log_reader_widget.clear()

    def start_log_monitoring(self, filepath):
        """Start monitoring a log file in a background thread."""
        self.stop_log_monitoring()
        self.clear_log_reader()
        self.monitoring_thread = LogFileReaderThread(filepath, self)
        self.monitoring_thread.new_line.connect(self.log_reader_widget.append)
        self.monitoring_thread.start()

    def stop_log_monitoring(self):
        """Stop the log monitoring thread."""
        if self.monitoring_thread and self.monitoring_thread.isRunning():
            self.monitoring_thread.stop()
            self.monitoring_thread.wait()

    def closeEvent(self, event):
        """Clean up when the window is closed."""
        self.stop_log_monitoring()
        logging.getLogger().removeHandler(self.log_handler)
        logging.getLogger().removeHandler(self.error_handler)
        super().closeEvent(event)


# ============================================================================
# EDEN DEBUG WINDOW
# ============================================================================

class EdenDebugWindow(QMainWindow):
    """Dedicated debug window for Eden connections, cookies and Herald"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("eden_debug_window.title", default="🌐 Debug Eden - Connexions & Cookies"))
        self.setGeometry(150, 150, 1000, 600)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton(lang.get("eden_debug_window.clear_button", default="🗑️ Effacer"))
        self.clear_button.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_button)
        
        self.export_button = QPushButton(lang.get("eden_debug_window.export_button", default="💾 Exporter"))
        self.export_button.clicked.connect(self.export_logs)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Log area with syntax highlighting
        self.logs_group = QGroupBox(lang.get("eden_debug_window.logs_title", default="📋 Logs Eden en temps réel"))
        logs_layout = QVBoxLayout()
        
        self.logs_widget = QTextEdit()
        self.logs_widget.setReadOnly(True)
        self.logs_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        logs_layout.addWidget(self.logs_widget)
        self.logs_group.setLayout(logs_layout)
        main_layout.addWidget(self.logs_group)
        
        # Info footer
        self.info_label = QLabel(lang.get("eden_debug_window.ready_text", default="Prêt à capturer les logs Eden..."))
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.info_label)
        
        # Setup of the Eden-specific handler
        self.eden_handler = QTextEditHandler(self.append_colored_log)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.eden_handler.setFormatter(formatter)
        
        # Add the handler to the Eden logger (use constant from debug_logging_manager)
        from Functions.debug_logging_manager import LOGGER_EDEN
        eden_logger = logging.getLogger(LOGGER_EDEN)
        eden_logger.addHandler(self.eden_handler)
        eden_logger.setLevel(logging.DEBUG)
        
        self.log_count = 0
    
    def append_colored_log(self, message):
        """Add a log with syntax highlighting"""
        self.log_count += 1
        
        # Extraire le niveau et le message
        if ' - ' in message:
            timestamp, content = message.split(' - ', 1)
        else:
            timestamp = ""
            content = message
        
        # Color based on keywords
        if '✅' in content or 'succès' in content.lower() or 'réussi' in content.lower():
            color = '#4ec9b0'  # Vert clair
            icon = '✅'
        elif '❌' in content or 'erreur' in content.lower() or 'échec' in content.lower():
            color = '#f48771'  # Rouge
            icon = '❌'
        elif '⚠️' in content or 'warning' in content.lower() or 'attention' in content.lower():
            color = '#ce9178'  # Orange
            icon = '⚠️'
        elif '🔍' in content or 'recherche' in content.lower() or 'détection' in content.lower():
            color = '#dcdcaa'  # Jaune
            icon = '🔍'
        elif '🌐' in content or 'navigateur' in content.lower() or 'browser' in content.lower():
            color = '#569cd6'  # Bleu
            icon = '🌐'
        elif '🍪' in content or 'cookie' in content.lower():
            color = '#c586c0'  # Violet
            icon = '🍪'
        elif '📋' in content or 'configuration' in content.lower() or 'config' in content.lower():
            color = '#9cdcfe'  # Bleu clair
            icon = '📋'
        else:
            color = '#d4d4d4'  # Blanc
            icon = '•'
        
        # Build the formatted message
        html_message = f'<span style="color: #808080;">{timestamp}</span> <span style="color: {color};">{icon} {content}</span>'
        
        self.logs_widget.append(html_message)
        self.info_label.setText(f"📊 {self.log_count} logs capturés")
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs_widget.clear()
        self.log_count = 0
        self.info_label.setText("Logs effacés - Prêt à capturer de nouveaux logs")
    
    def export_logs(self):
        """Export logs to a file"""
        file_path = dialog_save_file(self, "debug_export_logs_title")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_widget.toPlainText())
                self.info_label.setText(f"✅ Logs exportés: {file_path}")
            except Exception as e:
                self.info_label.setText(f"❌ Erreur d'export: {e}")
    
    def retranslate_ui(self):
        """Update UI text when language changes"""
        self.setWindowTitle(lang.get("eden_debug_window.title", default="🌐 Debug Eden - Connexions & Cookies"))
        self.clear_button.setText(lang.get("eden_debug_window.clear_button", default="🗑️ Effacer"))
        self.export_button.setText(lang.get("eden_debug_window.export_button", default="💾 Exporter"))
        self.logs_group.setTitle(lang.get("eden_debug_window.logs_title", default="📋 Logs Eden en temps réel"))
        self.info_label.setText(lang.get("eden_debug_window.ready_text", default="Prêt à capturer les logs Eden..."))
    
    def closeEvent(self, event):
        """Clean up when closing the window"""
        eden_logger = logging.getLogger('eden')
        eden_logger.removeHandler(self.eden_handler)
        super().closeEvent(event)
