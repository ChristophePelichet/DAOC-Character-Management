"""
SuperAdmin Models Database Widget

Displays models database statistics and advanced operations for managing
the models metadata and configuration in SuperAdmin mode.

Design: Two-column layout identical to Source Database Statistics
- Left: Statistics panel (total models, items, mobs, icons, file size, last updated)
- Right: Advanced operations buttons (Models Viewer, Refresh Metadata)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QDialog,
    QGroupBox, QFormLayout
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
            self.progress.emit(lang.get("models_db.refreshing_metadata", "Refreshing metadata..."))
            
            # Run the refresh process
            success, message, stats = self.superadmin.refresh_database()
            
            if success:
                self.progress.emit(lang.get("models_db.refresh_success", "Metadata refreshed successfully!"))
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
    
    Layout identical to Source Database Statistics:
    - Left panel: Models database statistics (using QFormLayout)
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
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel: Statistics (50% width)
        left_panel = self._create_statistics_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel: Advanced Operations (50% width)
        right_panel = self._create_advanced_operations_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_statistics_panel(self) -> QGroupBox:
        """
        Create left panel with models database statistics
        
        Returns:
            QGroupBox containing statistics display
        """
        stats_group = QGroupBox(lang.get('models_db.statistics_title', default="Models Database Statistics"))
        stats_layout = QFormLayout()
        
        # Total models
        self.total_models_label = QLabel("0")
        self.total_models_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.total', default="Total models:"), 
                           self.total_models_label)
        
        # Items count
        self.items_label = QLabel("0")
        self.items_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.items', default="Items:"), 
                           self.items_label)
        
        # Mobs count
        self.mobs_label = QLabel("0")
        self.mobs_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.mobs', default="Mobs:"), 
                           self.mobs_label)
        
        # Icons count
        self.icons_label = QLabel("0")
        self.icons_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.icons', default="Icons:"), 
                           self.icons_label)
        
        # File size
        self.file_size_label = QLabel("0 B")
        self.file_size_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.file_size', default="File size:"), 
                           self.file_size_label)
        
        # Last updated
        self.last_updated_label = QLabel(lang.get('models_db.unknown', default="Unknown"))
        self.last_updated_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.last_updated', default="Last updated:"), 
                           self.last_updated_label)
        
        # Refresh Stats button
        refresh_stats_btn = QPushButton(lang.get('models_db.refresh_stats', default="🔄 Refresh Stats"))
        refresh_stats_btn.setMinimumHeight(35)
        refresh_stats_btn.clicked.connect(self._load_stats)
        stats_layout.addRow("", refresh_stats_btn)
        
        stats_group.setLayout(stats_layout)
        return stats_group
    
    def _create_advanced_operations_panel(self) -> QGroupBox:
        """
        Create right panel with advanced operations buttons
        
        Returns:
            QGroupBox containing operation buttons
        """
        advanced_group = QGroupBox(lang.get('superadmin.advanced_group_title', 
            default="⚙️ Advanced Operations"))
        advanced_layout = QVBoxLayout()
        
        # Models Database Viewer button
        viewer_btn = QPushButton(lang.get('models_db.viewer_btn', default="🔍 Models Database Viewer"))
        viewer_btn.setMinimumHeight(35)
        viewer_btn.setToolTip(lang.get('models_db.viewer_tooltip', 
            default="View and explore all models in the database"))
        viewer_btn.clicked.connect(self._open_models_viewer)
        advanced_layout.addWidget(viewer_btn)
        
        # Refresh Metadata button
        refresh_btn = QPushButton(lang.get('models_db.refresh_metadata_btn', default="🔄 Refresh Metadata"))
        refresh_btn.setMinimumHeight(35)
        refresh_btn.setToolTip(lang.get('models_db.refresh_metadata_tooltip', 
            default="Re-scrape models metadata from Los Ojos website"))
        refresh_btn.clicked.connect(self._refresh_metadata)
        advanced_layout.addWidget(refresh_btn)
        
        advanced_layout.addStretch()
        
        advanced_group.setLayout(advanced_layout)
        return advanced_group
    
    def _load_stats(self):
        """Load and display models database statistics"""
        try:
            stats = self.superadmin.get_models_database_stats()
            
            # Update labels
            self.total_models_label.setText(str(stats.get("total_models", 0)))
            self.items_label.setText(str(stats.get("items", 0)))
            self.mobs_label.setText(str(stats.get("mobs", 0)))
            self.icons_label.setText(str(stats.get("icons", 0)))
            self.file_size_label.setText(stats.get("file_size", "Unknown"))
            self.last_updated_label.setText(stats.get("last_updated", "Unknown"))
            
            logging.info("Models database stats loaded successfully", extra={"action": "MODELS_DB_STATS_LOADED"})
            
        except Exception as e:
            logging.error(f"Error loading models database stats: {e}", extra={"action": "MODELS_DB_STATS_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                lang.get("models_db.stats_error", "Failed to load models database statistics")
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
                lang.get("models_db.viewer_coming_soon", "Models Database Viewer coming soon...")
            )
        except Exception as e:
            logging.error(f"Error opening models viewer: {e}", extra={"action": "MODELS_VIEWER_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                lang.get("models_db.viewer_error", "Error opening Models Database Viewer")
            )
    
    def _refresh_metadata(self):
        """Refresh models metadata from Los Ojos website"""
        try:
            # Confirm action
            reply = QMessageBox.question(
                self,
                lang.get('models_db.refresh_confirm_title', default="Refresh Metadata"),
                lang.get('models_db.refresh_confirm_msg', default="This will re-scrape the metadata from Los Ojos website. Continue?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            # Show progress message
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle(lang.get("superadmin.progress_title", "Building..."))
            progress_dialog.setText(lang.get('models_db.refreshing', default="Refreshing metadata..."))
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
                f"{lang.get('models_db.refresh_error', 'Error refreshing metadata')}: {str(e)}"
            )
    
    def _on_refresh_finished(self, dialog: QDialog):
        """Handle metadata refresh completion"""
        dialog.close()
        
        # Reload stats
        self._load_stats()
        
        QMessageBox.information(
            self,
            lang.get('models_db.refresh_complete_title', default="Refresh Complete"),
            lang.get('models_db.refresh_complete_msg', default="Metadata has been refreshed successfully!")
        )
    
    def _on_refresh_error(self, error_msg: str, dialog: QDialog):
        """Handle metadata refresh error"""
        dialog.close()
        
        logging.error(f"Metadata refresh error: {error_msg}", extra={"action": "MODELS_DB_REFRESH_ERROR"})
        QMessageBox.warning(
            self,
            lang.get("error_title", "Error"),
            f"{lang.get('models_db.refresh_error', 'Error refreshing metadata')}:\n{error_msg}"
        )

