"""
SuperAdmin Models Database Widget

Displays models database statistics and advanced operations for managing
the models metadata and configuration in SuperAdmin mode.

Design: Two-column layout similar to Source Database Statistics
- Left: Statistics panel (total models, items, mobs, icons, file size, last updated)
- Right: Advanced operations buttons (Models Viewer, Refresh Metadata)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
import logging

from Functions.language_manager import lang
from Functions.superadmin_tools import SuperAdminTools
from Functions.path_manager import PathManager


class ModelsMetadataRefreshWorker(QThread):
    """Worker thread for refreshing models metadata from Los Ojos website"""
    
    finished = Signal()
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self):
        """Initialize refresh worker"""
        super().__init__()
        self.path_manager = PathManager()
        self.superadmin = SuperAdminTools(self.path_manager)
    
    def run(self):
        """Run metadata refresh in background thread"""
        try:
            self.progress.emit(lang.get("models_db_refreshing_metadata", "Refreshing metadata..."))
            
            # Run the refresh process
            success, message, stats = self.superadmin.refresh_database()
            
            if success:
                self.progress.emit(lang.get("models_db_refresh_success", "Metadata refreshed successfully!"))
            else:
                self.error.emit(message)
            
            self.finished.emit()
            
        except Exception as e:
            logging.error(f"Error refreshing models metadata: {e}", extra={"action": "MODELS_DB_REFRESH_ERROR"})
            self.error.emit(f"Error: {str(e)}")
            self.finished.emit()


class SuperAdminModelsDatabaseWidget(QWidget):
    """
    SuperAdmin Models Database management widget.
    
    Displays:
    - Left panel: Models database statistics
    - Right panel: Advanced operations buttons
    
    Features:
    - Real-time stats display (total models, items, mobs, icons, file size, last updated)
    - Refresh metadata from Los Ojos website
    - Models database viewer (list all models)
    """
    
    def __init__(self, parent=None):
        """
        Initialize Models Database widget
        
        Args:
            parent: Parent widget (usually Settings dialog)
        """
        super().__init__(parent)
        self.path_manager = PathManager()
        self.superadmin = SuperAdminTools(self.path_manager)
        self.refresh_worker = None
        self._setup_ui()
        self._load_stats()
    
    def _setup_ui(self):
        """Create the UI layout and widgets"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel: Statistics
        left_panel = self._create_statistics_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel: Advanced Operations
        right_panel = self._create_advanced_operations_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_statistics_panel(self) -> QWidget:
        """
        Create left panel with models database statistics
        
        Returns:
            QWidget containing statistics display
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # Title
        title = QLabel(lang.get("models_db_statistics_title", "Models Database Statistics"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 2)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Stats container (styled like database stats)
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 12px;
            }
        """)
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(6)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create stat labels
        self.total_models_label = self._create_stat_label(
            lang.get("models_db_total", "Total models"),
            "0"
        )
        stats_layout.addWidget(self.total_models_label)
        
        self.items_label = self._create_stat_label(
            lang.get("models_db_items", "Items"),
            "0"
        )
        stats_layout.addWidget(self.items_label)
        
        self.mobs_label = self._create_stat_label(
            lang.get("models_db_mobs", "Mobs"),
            "0"
        )
        stats_layout.addWidget(self.mobs_label)
        
        self.icons_label = self._create_stat_label(
            lang.get("models_db_icons", "Icons"),
            "0"
        )
        stats_layout.addWidget(self.icons_label)
        
        self.file_size_label = self._create_stat_label(
            lang.get("models_db_file_size", "File size"),
            "0 B"
        )
        stats_layout.addWidget(self.file_size_label)
        
        self.last_updated_label = self._create_stat_label(
            lang.get("models_db_last_updated", "Last updated"),
            lang.get("models_db_unknown", "Unknown")
        )
        stats_layout.addWidget(self.last_updated_label)
        
        layout.addWidget(stats_widget)
        
        # Refresh button for stats
        refresh_stats_btn = QPushButton(lang.get("models_db_refresh_stats", "🔄 Refresh Stats"))
        refresh_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0a4a7d;
            }
        """)
        refresh_stats_btn.clicked.connect(self._load_stats)
        layout.addWidget(refresh_stats_btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_stat_label(self, label_text: str, value_text: str) -> QWidget:
        """
        Create a single statistic label with name and value
        
        Args:
            label_text: Label text (left side)
            value_text: Value text (right side, colored)
            
        Returns:
            QWidget containing the stat display
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QLabel(label_text + ":")
        label.setStyleSheet("color: #cccccc; font-size: 11px;")
        layout.addWidget(label)
        
        layout.addStretch()
        
        # Value
        value = QLabel(value_text)
        value.setStyleSheet("color: #ce9178; font-weight: bold; font-size: 11px;")
        value.setAlignment(Qt.AlignRight)
        layout.addWidget(value)
        
        container.value_label = value
        return container
    
    def _create_advanced_operations_panel(self) -> QWidget:
        """
        Create right panel with advanced operations buttons
        
        Returns:
            QWidget containing operation buttons
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Title
        title = QLabel(lang.get("superadmin_advanced_operations", "Advanced Operations"))
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 2)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Models Database Viewer button
        viewer_btn = QPushButton(lang.get("models_db_viewer_btn", "🔍 Models Database Viewer"))
        viewer_btn.setStyleSheet(self._get_button_style())
        viewer_btn.clicked.connect(self._open_models_viewer)
        layout.addWidget(viewer_btn)
        
        # Refresh Metadata button
        refresh_btn = QPushButton(lang.get("models_db_refresh_metadata_btn", "🔄 Refresh Metadata"))
        refresh_btn.setStyleSheet(self._get_button_style())
        refresh_btn.clicked.connect(self._refresh_metadata)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        return panel
    
    def _get_button_style(self) -> str:
        """
        Get button stylesheet for operation buttons
        
        Returns:
            CSS stylesheet string
        """
        return """
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0a4a7d;
            }
        """
    
    def _load_stats(self):
        """Load and display models database statistics"""
        try:
            stats = self.superadmin.get_models_database_stats()
            
            # Update labels
            self.total_models_label.value_label.setText(str(stats.get("total_models", 0)))
            self.items_label.value_label.setText(str(stats.get("items", 0)))
            self.mobs_label.value_label.setText(str(stats.get("mobs", 0)))
            self.icons_label.value_label.setText(str(stats.get("icons", 0)))
            self.file_size_label.value_label.setText(stats.get("file_size", "Unknown"))
            self.last_updated_label.value_label.setText(stats.get("last_updated", "Unknown"))
            
            logging.info("Models database stats loaded successfully", extra={"action": "MODELS_DB_STATS_LOADED"})
            
        except Exception as e:
            logging.error(f"Error loading models database stats: {e}", extra={"action": "MODELS_DB_STATS_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                lang.get("models_db_stats_error", "Failed to load models database statistics")
            )
    
    def _open_models_viewer(self):
        """Open models database viewer dialog"""
        try:
            from UI.ui_models_database_viewer import ModelsDatabaseViewerDialog
            
            dialog = ModelsDatabaseViewerDialog(self)
            dialog.exec()
            
        except ImportError:
            logging.error("Models Database Viewer not available", extra={"action": "MODELS_VIEWER_IMPORT_ERROR"})
            QMessageBox.information(
                self,
                lang.get("info_title", "Information"),
                lang.get("models_db_viewer_coming_soon", "Models Database Viewer coming soon...")
            )
        except Exception as e:
            logging.error(f"Error opening models viewer: {e}", extra={"action": "MODELS_VIEWER_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                lang.get("models_db_viewer_error", "Error opening Models Database Viewer")
            )
    
    def _refresh_metadata(self):
        """Refresh models metadata from Los Ojos website"""
        try:
            # Confirm action
            reply = QMessageBox.question(
                self,
                lang.get("models_db_refresh_confirm_title", "Refresh Metadata"),
                lang.get("models_db_refresh_confirm_msg", "This will re-scrape the metadata from Los Ojos website. Continue?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            # Show progress message
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle(lang.get("processing_title", "Processing"))
            progress_dialog.setText(lang.get("models_db_refreshing", "Refreshing metadata..."))
            progress_dialog.setStandardButtons(QMessageBox.NoButton)
            progress_dialog.show()
            
            # Create and run worker thread
            self.refresh_worker = ModelsMetadataRefreshWorker()
            self.refresh_worker.finished.connect(lambda: self._on_refresh_finished(progress_dialog))
            self.refresh_worker.error.connect(lambda e: self._on_refresh_error(e, progress_dialog))
            self.refresh_worker.progress.connect(lambda msg: progress_dialog.setText(msg))
            self.refresh_worker.start()
            
        except Exception as e:
            logging.error(f"Error refreshing metadata: {e}", extra={"action": "MODELS_DB_REFRESH_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                f"{lang.get('models_db_refresh_error', 'Error refreshing metadata')}: {str(e)}"
            )
    
    def _on_refresh_finished(self, dialog: QDialog):
        """Handle metadata refresh completion"""
        dialog.close()
        
        # Reload stats
        self._load_stats()
        
        QMessageBox.information(
            self,
            lang.get("models_db_refresh_complete_title", "Refresh Complete"),
            lang.get("models_db_refresh_complete_msg", "Metadata has been refreshed successfully!")
        )
    
    def _on_refresh_error(self, error_msg: str, dialog: QDialog):
        """Handle metadata refresh error"""
        dialog.close()
        
        logging.error(f"Metadata refresh error: {error_msg}", extra={"action": "MODELS_DB_REFRESH_ERROR"})
        QMessageBox.warning(
            self,
            lang.get("error_title", "Error"),
            f"{lang.get('models_db_refresh_error', 'Error refreshing metadata')}:\n{error_msg}"
        )
