"""
Debug window and logging utilities for the DAOC Character Manager.
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QTextEdit, QPushButton, QLineEdit, QSplitter, QFileDialog
)
from PySide6.QtCore import QThread, QObject, Signal, Slot, Qt
from PySide6.QtGui import QAction, QActionGroup
from Functions.language_manager import lang


class QTextEditHandler(logging.Handler, QObject):
    """A custom logging handler that sends log records to a QTextEdit widget."""
    
    log_updated = Signal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self, parent)

    def emit(self, record):
        msg = self.format(record)
        self.log_updated.emit(msg)


class LogLevelFilter(logging.Filter):
    """Filters log records based on a minimum and maximum level."""
    
    def __init__(self, min_level, max_level):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record):
        return self.min_level <= record.levelno <= self.max_level


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

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Menu Bar
        self._create_menus()
        
        # Button Bar
        button_bar_layout = QHBoxLayout()
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
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # General log handler (INFO and below)
        self.log_filter = LogLevelFilter(logging.DEBUG, logging.INFO)
        self.log_handler = QTextEditHandler(self)
        self.log_handler.setFormatter(formatter)
        self.log_handler.addFilter(self.log_filter)
        self.log_handler.log_updated.connect(self.log_widget.append)
        logging.getLogger().addHandler(self.log_handler)

        # Error log handler (WARNING and above)
        self.error_filter = LogLevelFilter(logging.WARNING, logging.CRITICAL)
        self.error_handler = QTextEditHandler(self)
        self.error_handler.setFormatter(formatter)
        self.error_handler.addFilter(self.error_filter)
        self.error_handler.log_updated.connect(self.error_widget.append)
        logging.getLogger().addHandler(self.error_handler)

    def _create_menus(self):
        """Create the menu bar with log level options."""
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

    @Slot(QAction)
    def set_log_level(self, action):
        """Sets the minimum logging level for the handlers."""
        level = action.data()
        self.current_log_level = level
        logging.info(f"Debug window log level set to {logging.getLevelName(level)}")

        # Update filters
        self.log_filter.min_level = level
        self.error_filter.min_level = level
        
    def raise_test_exception(self):
        """Raises a test exception to verify the logging system."""
        logging.info("Raising a test exception...")
        1 / 0

    def browse_log_file(self):
        """Open a file dialog to select a log file to monitor."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            lang.get("debug_log_reader_pane_title"), 
            "", 
            "Log files (*.log);;All files (*.*)"
        )
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
