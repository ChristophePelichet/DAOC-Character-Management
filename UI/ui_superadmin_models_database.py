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
from PySide6.QtCore import QThread, Signal
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
        
        # Left panel: Two separated statistics sections (50% width)
        left_panel = self._create_left_panels()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel: Advanced Operations (50% width)
        right_panel = self._create_advanced_operations_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_left_panels(self) -> QWidget:
        """
        Create left panel with two separated statistics sections
        
        Returns:
            QWidget containing both statistics sections
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Section 1: Metadata Statistics
        metadata_group = self._create_metadata_statistics_panel()
        layout.addWidget(metadata_group)
        
        # Section 2: Image Files Statistics
        files_group = self._create_image_files_statistics_panel()
        layout.addWidget(files_group)
        
        layout.addStretch()
        
        return container
    
    def _create_metadata_statistics_panel(self) -> QGroupBox:
        """
        Create metadata statistics panel
        
        Returns:
            QGroupBox with metadata stats and refresh button
        """
        stats_group = QGroupBox(lang.get('models_db.metadata_stats_title', default="📊 Models"))
        stats_layout = QFormLayout()
        
        # Database name
        self.database_name_label = QLabel("models_metadata.json")
        self.database_name_label.setStyleSheet("font-weight: bold; color: #2196f3;")
        stats_layout.addRow(lang.get('models_db.database_name', default="Database:"), 
                           self.database_name_label)
        
        # Total models (metadata)
        self.total_models_label = QLabel("0")
        self.total_models_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.total', default="Total models:"), 
                           self.total_models_label)
        
        # Items count (metadata)
        self.items_label = QLabel("0")
        self.items_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.items', default="Items:"), 
                           self.items_label)
        
        # Mobs count (metadata)
        self.mobs_label = QLabel("0")
        self.mobs_label.setStyleSheet("color: #ce9178;")
        stats_layout.addRow(lang.get('models_db.mobs', default="Mobs:"), 
                           self.mobs_label)
        
        # Icons count (metadata)
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
        
        # Refresh Metadata button
        refresh_metadata_btn = QPushButton(lang.get('models_db.refresh_db_stats', default="🔄 Refresh Database"))
        refresh_metadata_btn.setMinimumHeight(35)
        refresh_metadata_btn.clicked.connect(self._load_metadata_stats)
        stats_layout.addRow("", refresh_metadata_btn)
        
        stats_group.setLayout(stats_layout)
        return stats_group
    
    def _create_image_files_statistics_panel(self) -> QGroupBox:
        """
        Create image files statistics panel
        
        Returns:
            QGroupBox with image file counts and refresh button
        """
        files_group = QGroupBox(lang.get('models_db.image_stats_title', default="🖼️ Models Database"))
        files_layout = QFormLayout()
        
        # Total files
        self.total_files_label = QLabel("0")
        self.total_files_label.setStyleSheet("color: #ce9178;")
        files_layout.addRow(lang.get('models_db.total_files', default="Total files:"), 
                           self.total_files_label)
        
        # Items files
        self.items_files_label = QLabel("0")
        self.items_files_label.setStyleSheet("color: #ce9178;")
        files_layout.addRow(lang.get('models_db.items_files', default="Items files:"), 
                           self.items_files_label)
        
        # Mobs files
        self.mobs_files_label = QLabel("0")
        self.mobs_files_label.setStyleSheet("color: #ce9178;")
        files_layout.addRow(lang.get('models_db.mobs_files', default="Mobs files:"), 
                           self.mobs_files_label)
        
        # Icons files
        self.icons_files_label = QLabel("0")
        self.icons_files_label.setStyleSheet("color: #ce9178;")
        files_layout.addRow(lang.get('models_db.icons_files', default="Icons files:"), 
                           self.icons_files_label)
        
        # Refresh Files button
        refresh_files_btn = QPushButton(lang.get('models_db.refresh_files_stats', default="🔄 Refresh Files"))
        refresh_files_btn.setMinimumHeight(35)
        refresh_files_btn.clicked.connect(self._load_files_stats)
        files_layout.addRow("", refresh_files_btn)
        
        files_group.setLayout(files_layout)
        return files_group
    
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
        
        advanced_layout.addStretch()
        
        advanced_group.setLayout(advanced_layout)
        return advanced_group
    
    def _load_stats(self):
        """Load and display all statistics (metadata + files)"""
        self._load_metadata_stats()
        self._load_files_stats()
    
    def _load_metadata_stats(self):
        """Load and display metadata database statistics"""
        try:
            stats = self.superadmin.get_models_database_stats()
            
            # Update metadata labels
            self.total_models_label.setText(str(stats.get("total_models", 0)))
            self.items_label.setText(str(stats.get("items", 0)))
            self.mobs_label.setText(str(stats.get("mobs", 0)))
            self.icons_label.setText(str(stats.get("icons", 0)))
            self.file_size_label.setText(stats.get("file_size", "Unknown"))
            self.last_updated_label.setText(stats.get("last_updated", "Unknown"))
            
            logging.info("Models metadata stats loaded successfully", extra={"action": "MODELS_DB_METADATA_STATS_LOADED"})
            
        except Exception as e:
            logging.error(f"Error loading models metadata stats: {e}", extra={"action": "MODELS_DB_METADATA_STATS_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                lang.get("models_db.metadata_stats_error", "Failed to load metadata database statistics")
            )
    
    def _load_files_stats(self):
        """Load and display image files statistics"""
        try:
            files = self.superadmin.get_models_files_count()
            
            # Update file count labels
            self.total_files_label.setText(str(files.get("total_files", 0)))
            self.items_files_label.setText(str(files.get("items", 0)))
            self.mobs_files_label.setText(str(files.get("mobs", 0)))
            self.icons_files_label.setText(str(files.get("icons", 0)))
            
            logging.info("Models image files stats loaded successfully", extra={"action": "MODELS_DB_FILES_STATS_LOADED"})
            
        except Exception as e:
            logging.error(f"Error loading models files stats: {e}", extra={"action": "MODELS_DB_FILES_STATS_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                lang.get("models_db.files_stats_error", "Failed to load image files statistics")
            )
    
    def _open_models_viewer(self):
        """Open models database editor dialog"""
        try:
            from UI.ui_models_database_editor import ModelsDataDatabaseEditor
            
            dialog = ModelsDataDatabaseEditor(self)
            dialog.exec()
            
        except ImportError as e:
            logging.error(f"Models Database Editor import error: {e}", extra={"action": "MODELS_EDITOR_IMPORT_ERROR"})
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                f"Import error: {str(e)}"
            )
        except Exception as e:
            logging.error(f"Error opening models editor: {e}", extra={"action": "MODELS_EDITOR_ERROR"})
            import traceback
            QMessageBox.warning(
                self,
                lang.get("error_title", "Error"),
                f"Error: {str(e)}\n\n{traceback.format_exc()}"
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

