"""
Database Management Tools Window
Detailed monitoring window for database management and mass item import
"""

import logging
from datetime import datetime
from UI.ui_sound_manager import SilentMessageBox
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTextEdit, QPushButton, QLabel, QProgressBar,
    QGridLayout, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor

from Functions.language_manager import lang
from UI.ui_file_dialogs import (
    dialog_select_multiple_files,
    dialog_save_file
)


class MassImportMonitor(QMainWindow):
    """Monitoring window for mass import with detailed logs and statistics"""
    
    def __init__(self, parent=None, target_db="embedded"):
        super().__init__(parent)
        self.target_db = target_db  # "embedded" or "personal"
        
        # Set window title (same for both modes)
        title = lang.get("settings.pages.mass_import_monitor.window_title", default="📦 Template Import Items Tools")
        self.setWindowTitle(title)
        self.setGeometry(150, 100, 1200, 700)
        
        # Make window independent and always movable
        self.setWindowFlags(
            Qt.Window  # Independent window (removed StaysOnTop)
        )
        
        # CRITICAL: Prevent this window from closing the entire application
        self.setAttribute(Qt.WA_QuitOnClose, False)
        
        # Tracking variables
        self.start_time = None
        self.items_processed = 0
        self.items_total = 0
        self.variants_found = 0
        self.items_added = 0
        self.items_failed = 0
        self.duplicates_skipped = 0
        self.current_item = None
        self.error_list = []  # Error list for tracking
        self.filtered_items = []  # Items filtered by level/utility restrictions
        self.retry_worker = None  # Worker for retry operations
        self.main_worker = None  # Worker for main import
        
        # Import parameters (set when prepare_import is called)
        self.pending_import_params = None  # Will store: {file_paths, realm, merge, remove_duplicates, auto_backup, source_db_path, path_manager}
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # === HEADER: Title and time ===
        header_layout = QHBoxLayout()
        
        title_label = QLabel(lang.get("settings.pages.mass_import_monitor.title", default="📦 Mass Import - Real-Time Monitoring"))
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #4ec9b0;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.time_label = QLabel("⏱️ 00:00:00")
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #569cd6;
            }
        """)
        header_layout.addWidget(self.time_label)
        
        main_layout.addLayout(header_layout)
        
        # === OPTIONS PANEL ===
        options_group = QGroupBox(lang.get("settings.pages.mass_import_monitor.options_group", default="⚙️ Import Options"))
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        options_layout = QHBoxLayout()
        
        # Realm selection
        realm_label = QLabel(lang.get('superadmin.realm_label', default="Realm:"))
        self.realm_combo = QComboBox()
        self.realm_combo.addItem(lang.get('superadmin.realm_auto', default="Auto-detection"))
        self.realm_combo.addItem("Albion")
        self.realm_combo.addItem("Hibernia")
        self.realm_combo.addItem("Midgard")
        self.realm_combo.setToolTip(lang.get('superadmin.realm_tooltip', 
            default="Item realm (auto-detection from file names if enabled)"))
        options_layout.addWidget(realm_label)
        options_layout.addWidget(self.realm_combo)
        
        options_layout.addSpacing(20)
        
        # Checkboxes
        self.merge_check = QCheckBox(lang.get('superadmin.options_merge', 
            default="Merge with existing database"))
        self.merge_check.setToolTip(lang.get('superadmin.options_merge_tooltip', 
            default="If unchecked, database will be overwritten. If checked, new items will be added to existing database."))
        self.merge_check.setChecked(True)
        options_layout.addWidget(self.merge_check)
        
        self.dedup_check = QCheckBox(lang.get('superadmin.options_remove_duplicates', 
            default="Remove duplicates"))
        self.dedup_check.setToolTip(lang.get('superadmin.options_remove_duplicates_tooltip', 
            default="Remove items with same name + realm"))
        self.dedup_check.setChecked(True)
        options_layout.addWidget(self.dedup_check)
        
        self.backup_check = QCheckBox(lang.get('superadmin.options_auto_backup', 
            default="Auto-backup"))
        self.backup_check.setToolTip(lang.get('superadmin.options_auto_backup_tooltip', 
            default="Create timestamped backup before modification"))
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.backup_check)
        
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # === STATISTICS PANEL ===
        stats_group = QGroupBox(lang.get("settings.pages.mass_import_monitor.stats_group", default="📊 Real-Time Statistics"))
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        stats_layout = QGridLayout()
        stats_layout.setSpacing(10)
        
        # Row 1: Unique items and variants
        self.unique_items_label = QLabel(lang.get("settings.pages.mass_import_monitor.unique_items", default="🔍 Unique items:") + " 0")
        self.unique_items_label.setStyleSheet("font-size: 11pt; color: #dcdcaa;")
        stats_layout.addWidget(self.unique_items_label, 0, 0)
        
        self.variants_label = QLabel(lang.get("settings.pages.mass_import_monitor.variants_found", default="🌐 Variants found:") + " 0")
        self.variants_label.setStyleSheet("font-size: 11pt; color: #569cd6;")
        stats_layout.addWidget(self.variants_label, 0, 1)
        
        self.processed_label = QLabel(lang.get("settings.pages.mass_import_monitor.items_processed", default="⚙️ Items processed:") + " 0 / 0")
        self.processed_label.setStyleSheet("font-size: 11pt; color: #9cdcfe;")
        stats_layout.addWidget(self.processed_label, 0, 2)
        
        # Row 2: Results
        self.added_label = QLabel(lang.get("settings.pages.mass_import_monitor.added", default="✅ Added:") + " 0")
        self.added_label.setStyleSheet("font-size: 11pt; color: #4ec9b0;")
        stats_layout.addWidget(self.added_label, 1, 0)
        
        self.duplicates_label = QLabel(lang.get("settings.pages.mass_import_monitor.duplicates", default="⏭️ Doublons ignorés:") + " 0")
        self.duplicates_label.setStyleSheet("font-size: 11pt; color: #ce9178;")
        stats_layout.addWidget(self.duplicates_label, 1, 1)
        
        self.failed_label = QLabel(lang.get("settings.pages.mass_import_monitor.failed", default="❌ Échecs:") + " 0")
        self.failed_label.setStyleSheet("font-size: 11pt; color: #f48771;")
        stats_layout.addWidget(self.failed_label, 1, 2)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # === HORIZONTAL LAYOUT: LOGS + FILES (50/50) ===
        files_logs_layout = QHBoxLayout()
        
        # === LOGS PANEL (LEFT) ===
        logs_group = QGroupBox(lang.get("settings.pages.mass_import_monitor.logs_group", default="📋 Logs Détaillés"))
        logs_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        logs_layout = QVBoxLayout()
        
        # Button bar above logs
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton(lang.get("settings.pages.mass_import_monitor.clear_button", default="🗑️ Effacer"))
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        self.export_button = QPushButton(lang.get("settings.pages.mass_import_monitor.export_button", default="💾 Exporter"))
        self.export_button.clicked.connect(self.export_logs)
        self.export_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        
        self.autoscroll_label = QLabel(lang.get("settings.pages.mass_import_monitor.autoscroll", default="📜 Auto-scroll: ON"))
        self.autoscroll_label.setStyleSheet("color: #4ec9b0; font-size: 9pt;")
        button_layout.addWidget(self.autoscroll_label)
        
        logs_layout.addLayout(button_layout)
        
        # Log area with coloring
        self.logs_widget = QTextEdit()
        self.logs_widget.setReadOnly(True)
        self.logs_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
            }
        """)
        logs_layout.addWidget(self.logs_widget)
        
        logs_group.setLayout(logs_layout)
        files_logs_layout.addWidget(logs_group, stretch=1)
        
        # === FILES PANEL (RIGHT) ===
        files_group = QGroupBox(lang.get("settings.pages.mass_import_monitor.files_group", default="📁 Fichiers Template"))
        files_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        files_layout = QVBoxLayout()
        
        self.files_widget = QTextEdit()
        self.files_widget.setReadOnly(True)
        self.files_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcaa;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
            }
        """)
        files_layout.addWidget(self.files_widget)
        
        files_group.setLayout(files_layout)
        files_logs_layout.addWidget(files_group, stretch=1)
        
        # Add horizontal layout to main
        main_layout.addLayout(files_logs_layout, stretch=1)
        
        # === PROGRESS BAR ===
        progress_group = QGroupBox(lang.get("settings.pages.mass_import_monitor.progress_group", default="📈 Progression"))
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                font-size: 10pt;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4ec9b0, stop: 1 #569cd6
                );
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.current_item_label = QLabel(lang.get("settings.pages.mass_import_monitor.waiting", default="En attente..."))
        self.current_item_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #808080;
                font-style: italic;
                padding: 5px;
            }
        """)
        self.current_item_label.setAlignment(Qt.AlignCenter)
        self.current_item_label.setWordWrap(True)  # Allow line wrap for long names
        progress_layout.addWidget(self.current_item_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # === ERRORS PANEL ===
        errors_group = QGroupBox(lang.get("settings.pages.mass_import_monitor.errors_group", default="⚠️ Suivi des Erreurs"))
        errors_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f48771;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        errors_layout = QVBoxLayout()
        
        # Error buttons
        error_buttons_layout = QHBoxLayout()
        
        self.clear_errors_button = QPushButton(lang.get("settings.pages.mass_import_monitor.clear_errors", default="🗑️ Effacer erreurs"))
        self.clear_errors_button.clicked.connect(self.clear_errors)
        self.clear_errors_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        error_buttons_layout.addWidget(self.clear_errors_button)
        
        self.export_errors_button = QPushButton(lang.get("settings.pages.mass_import_monitor.export_errors", default="💾 Exporter erreurs"))
        self.export_errors_button.clicked.connect(self.export_errors)
        self.export_errors_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        error_buttons_layout.addWidget(self.export_errors_button)
        
        error_buttons_layout.addStretch()
        
        self.error_count_label = QLabel(lang.get("settings.pages.mass_import_monitor.error_count", count=0, default="0 erreur(s)"))
        self.error_count_label.setStyleSheet("color: #f48771; font-weight: bold; font-size: 10pt;")
        error_buttons_layout.addWidget(self.error_count_label)
        
        errors_layout.addLayout(error_buttons_layout)
        
        # Error area
        self.errors_widget = QTextEdit()
        self.errors_widget.setReadOnly(True)
        self.errors_widget.setMaximumHeight(150)  # Limited height
        self.errors_widget.setStyleSheet("""
            QTextEdit {
                background-color: #2d1f1f;
                color: #f48771;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                border: 1px solid #f48771;
                border-radius: 3px;
            }
        """)
        errors_layout.addWidget(self.errors_widget)
        
        errors_group.setLayout(errors_layout)
        main_layout.addWidget(errors_group)
        
        # === FOOTER ===
        footer_layout = QHBoxLayout()
        
        self.info_label = QLabel(lang.get("settings.pages.mass_import_monitor.ready", default="Prêt à démarrer l'import..."))
        self.info_label.setStyleSheet("color: #808080; font-style: italic; font-size: 9pt;")
        footer_layout.addWidget(self.info_label)
        
        footer_layout.addStretch()
        
        # Start button (initially visible, hidden after start)
        self.start_button = QPushButton(lang.get("settings.pages.mass_import_monitor.start_button", default="▶️ Start Import"))
        self.start_button.clicked.connect(self.start_import_manual)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4ec9b0;
                color: #1e1e1e;
                padding: 8px 25px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5ed9c0;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #808080;
            }
        """)
        footer_layout.addWidget(self.start_button)
        
        self.review_filtered_btn = QPushButton(lang.get("settings.pages.mass_import_monitor.review_filtered", default="🔍 Review Filtered Items"))
        self.review_filtered_btn.clicked.connect(self.open_review_filtered_dialog)
        self.review_filtered_btn.setVisible(False)  # Hidden until filtered items exist
        self.review_filtered_btn.setStyleSheet("""
            QPushButton {
                background-color: #ce9178;
                color: #1e1e1e;
                padding: 5px 20px;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d4a574;
            }
        """)
        footer_layout.addWidget(self.review_filtered_btn)
        
        self.close_button = QPushButton(lang.get("settings.pages.mass_import_monitor.close_button", default="❌ Fermer"))
        self.close_button.clicked.connect(self.close)
        self.close_button.setEnabled(False)  # Disabled during import
        self.close_button.setStyleSheet("""
            QPushButton {
                padding: 5px 20px;
                font-size: 10pt;
            }
        """)
        footer_layout.addWidget(self.close_button)
        
        main_layout.addLayout(footer_layout)
        
        # Timer to update elapsed time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        
        # Auto-scroll enabled by default
        self.auto_scroll = True
        
        self.log_count = 0
    
    def start_import(self, total_items, template_files=None):
        """Start import with total number of items and optional template files list"""
        self.start_time = datetime.now()
        self.items_total = total_items
        self.items_processed = 0
        self.variants_found = 0
        self.items_added = 0
        self.items_failed = 0
        self.duplicates_skipped = 0
        
        # Display template files if provided
        if template_files:
            files_text = "\n".join([f"📄 {file}" for file in template_files])
            self.files_widget.setHtml(f'<pre style="color: #dcdcaa;">{files_text}</pre>')
        
        self.progress_bar.setMaximum(total_items)
        self.progress_bar.setValue(0)
        
        self.timer.start(100)  # Update every 100ms
        
        self.close_button.setEnabled(False)
        
        self.log_message(lang.get("settings.pages.mass_import_monitor.start_import_message", default="Démarrage de l'import en masse..."), "info")
        if template_files:
            self.log_message(lang.get("settings.pages.mass_import_monitor.template_files_count", count=len(template_files), default=f"{len(template_files)} fichier(s) template à parser"), "info")
        self.log_message(lang.get("settings.pages.mass_import_monitor.unique_items_to_process", count=total_items, default=f"{total_items} items uniques à traiter"), "info")
    
    def set_default_options(self, realm, merge, remove_duplicates, auto_backup, path_manager):
        """Set default import options and initialize UI widgets"""
        from pathlib import Path
        
        # Store path_manager
        self.path_manager = path_manager
        
        # Set database path based on target_db mode
        if self.target_db == "personal":
            # User's personal database in Armory folder
            from Functions.config_manager import config
            armor_path = config.get('folders.armor')
            if armor_path:
                self.source_db_path = Path(armor_path) / "items_database.json"
            else:
                self.source_db_path = path_manager.get_app_root() / "Armory" / "items_database.json"
        else:
            # SuperAdmin embedded database
            self.source_db_path = Path("Data/items_database_src.json")
        
        # Set widget values from parameters
        realm_map = {None: 0, "Albion": 1, "Hibernia": 2, "Midgard": 3}
        self.realm_combo.setCurrentIndex(realm_map.get(realm, 0))
        self.merge_check.setChecked(merge)
        self.dedup_check.setChecked(remove_duplicates)
        self.backup_check.setChecked(auto_backup)
        
        # Update info label to show ready state
        self.info_label.setText(lang.get("settings.pages.mass_import_monitor.select_files_message", 
            default="📂 Click 'Select Templates' to choose template files to import."))
        self.info_label.setStyleSheet("color: #569cd6; font-style: italic; font-size: 10pt;")
        
        # Disable start button until files are selected
        self.start_button.setEnabled(False)
        self.start_button.setText(lang.get("settings.pages.mass_import_monitor.select_templates_button", 
            default="📁 Select Templates"))
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.select_template_files)
        self.start_button.setEnabled(True)
        
        self.log_message(lang.get("settings.pages.mass_import_monitor.ready_to_select", 
            default="✅ Ready. Please select template files to import."), "info")
    
    def select_template_files(self):
        """Open file dialog to select template files"""
        try:
            files = dialog_select_multiple_files(
                self,
                title_key='superadmin.select_files_title',
                filter_key="superadmin.files_filter"
            )
            
            if files:
                # Files selected - prepare import
                from pathlib import Path
                
                # Display template files
                template_file_names = [Path(fp).name for fp in files]
                files_text = "\n".join([f"📄 {file}" for file in template_file_names])
                self.files_widget.setHtml(f'<pre style="color: #dcdcaa;">{files_text}</pre>')
                
                # Get options from widgets
                realm_index = self.realm_combo.currentIndex()
                realm_map = {0: None, 1: "Albion", 2: "Hibernia", 3: "Midgard"}
                realm = realm_map[realm_index]
                
                # Prepare import with selected files and current widget values
                self.prepare_import(
                    file_paths=files,
                    realm=realm,
                    merge=self.merge_check.isChecked(),
                    remove_duplicates=self.dedup_check.isChecked(),
                    auto_backup=self.backup_check.isChecked(),
                    source_db_path=self.source_db_path,
                    path_manager=self.path_manager
                )
                
                # Change button to Start Import
                self.start_button.setText(lang.get("settings.pages.mass_import_monitor.start_button", 
                    default="▶️ Start Import"))
                self.start_button.clicked.disconnect()
                self.start_button.clicked.connect(self.start_import_manual)
                
            else:
                # No files selected
                self.log_message(lang.get("settings.pages.mass_import_monitor.no_files_selected", 
                    default="⚠️ No files selected."), "warning")
                
        except Exception as e:
            logging.error(f"Error selecting template files: {e}", exc_info=True)
            self.log_message(f"❌ Error selecting files: {e}", "error")
    
    def prepare_import(self, file_paths, realm, merge, remove_duplicates, auto_backup, source_db_path, path_manager):
        """Prepare import parameters without starting - wait for manual start"""
        self.pending_import_params = {
            'file_paths': file_paths,
            'realm': realm,
            'merge': merge,
            'remove_duplicates': remove_duplicates,
            'auto_backup': auto_backup,
            'source_db_path': source_db_path,
            'path_manager': path_manager
        }
        
        # Display template files
        from pathlib import Path
        template_file_names = [Path(fp).name for fp in file_paths]
        files_text = "\n".join([f"📄 {file}" for file in template_file_names])
        self.files_widget.setHtml(f'<pre style="color: #dcdcaa;">{files_text}</pre>')
        
        # Update info label
        self.info_label.setText(lang.get("settings.pages.mass_import_monitor.ready_to_start", count=len(file_paths), default=f"✅ Ready to import {len(file_paths)} template(s). Click 'Start Import' to begin."))
        self.info_label.setStyleSheet("color: #4ec9b0; font-style: normal; font-size: 10pt; font-weight: bold;")
        
        # Enable start button
        self.start_button.setEnabled(True)
        
        self.log_message(lang.get("settings.pages.mass_import_monitor.import_prepared", count=len(file_paths), default=f"📥 {len(file_paths)} template file(s) loaded. Ready to start."), "info")
    
    def start_import_manual(self):
        """Manually start the import with prepared parameters"""
        if not self.pending_import_params:
            self.log_message("❌ No import prepared. Please load templates first.", "error")
            return
        
        # Disable start button
        self.start_button.setEnabled(False)
        self.start_button.setVisible(False)
        
        # Import and start worker
        from Functions.import_worker import ImportWorker
        from PySide6.QtCore import Qt
        from pathlib import Path
        
        params = self.pending_import_params
        
        self.main_worker = ImportWorker(
            file_paths=params['file_paths'],
            realm=params['realm'],
            merge=params['merge'],
            remove_duplicates=params['remove_duplicates'],
            auto_backup=params['auto_backup'],
            source_db_path=params['source_db_path'],
            path_manager=params['path_manager']
        )
        
        # Connect signals
        self.main_worker.progress_updated.connect(self.update_stats_slot)
        self.main_worker.log_message.connect(self.log_message_slot)
        
        def on_import_finished(success, message, stats):
            """Handle import completion (business logic)"""
            try:
                self.finish_import(success)
                
                # Pass filtered items to monitor for review option
                if stats and 'filtered_items' in stats:
                    self.set_filtered_items(stats['filtered_items'])
                    
            except Exception as e:
                self.log_message(f"Error in import finish: {e}", "error")
                import traceback
                self.log_message(f"Traceback: {traceback.format_exc()}", "error")
        
        def on_thread_finished():
            """Handle thread termination (cleanup resources)"""
            try:
                self.log_message("Main import worker thread finished, cleaning up...", "info")
                
                if self.main_worker is not None:
                    # Wait for thread to fully stop
                    if not self.main_worker.wait(5000):  # Wait up to 5 seconds
                        self.log_message("Warning: Thread did not finish in time", "warning")
                    
                    # Disconnect signals safely
                    try:
                        self.main_worker.progress_updated.disconnect()
                        self.main_worker.log_message.disconnect()
                        self.main_worker.import_finished.disconnect()
                        self.main_worker.finished.disconnect()
                    except Exception:
                        pass
                    
                    # Schedule deletion
                    self.main_worker.deleteLater()
                    self.main_worker = None
                    self.log_message("Main import worker cleaned up successfully", "info")
                    
            except Exception as cleanup_error:
                self.log_message(f"Error in thread cleanup: {cleanup_error}", "warning")
                import traceback
                self.log_message(f"Traceback: {traceback.format_exc()}", "warning")
        
        # Connect import_finished for business logic
        self.main_worker.import_finished.connect(on_import_finished, Qt.QueuedConnection)
        
        # Connect finished (QThread signal) for cleanup - this is emitted when thread actually stops
        self.main_worker.finished.connect(on_thread_finished, Qt.QueuedConnection)
        
        # Start import UI
        total_items = len(params['file_paths'])
        template_file_names = [Path(fp).name for fp in params['file_paths']]
        self.start_import(total_items, template_files=template_file_names)
        
        # Start worker thread
        self.main_worker.start()
    
    def finish_import(self, success=True):
        """Finish import"""
        # NO processEvents() - causes crashes when called from signal callbacks
        self.timer.stop()
        self.close_button.setEnabled(True)
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        if success:
            self.log_message("", "separator")
            self.log_message(lang.get("settings.pages.mass_import_monitor.import_finished_success", duration=self.format_duration(elapsed), default=f"Import terminé avec succès en {self.format_duration(elapsed)}"), "success")
            self.log_message(lang.get("settings.pages.mass_import_monitor.import_summary", added=self.items_added, duplicates=self.duplicates_skipped, failed=self.items_failed, default=f"Résumé: {self.items_added} ajoutés, {self.duplicates_skipped} doublons, {self.items_failed} échecs"), "info")
            self.info_label.setText(lang.get("settings.pages.mass_import_monitor.import_finished_message", count=self.items_added, default=f"✅ Import terminé - {self.items_added} items ajoutés"))
        else:
            self.log_message("", "separator")
            self.log_message(lang.get("settings.pages.mass_import_monitor.import_finished_errors", default="Import terminé avec des erreurs"), "error")
            self.info_label.setText(lang.get("settings.pages.mass_import_monitor.import_finished_error_message", default="❌ Import terminé avec des erreurs"))
    
    def update_stats(self, **kwargs):
        """Update statistics
        
        Args:
            processed: Number of unique items processed
            total: Total number of items (to update progress bar max)
            variants: Number of variants found
            added: Number of items added to DB
            failed: Number of failures
            duplicates: Number of duplicates skipped
            current_item: Name of item being processed
        """
        
        if 'total' in kwargs:
            self.items_total = kwargs['total']
            self.progress_bar.setMaximum(self.items_total)
        
        if 'processed' in kwargs:
            self.items_processed = kwargs['processed']
            self.processed_label.setText(f"{lang.get('settings.pages.mass_import_monitor.items_processed', default='⚙️ Items traités:')} {self.items_processed} / {self.items_total}")
            
            # Update progress bar
            if self.items_total > 0:
                self.progress_bar.setValue(self.items_processed)
        
        if 'variants' in kwargs:
            self.variants_found = kwargs['variants']
            self.variants_label.setText(f"{lang.get('settings.pages.mass_import_monitor.variants_found', default='🌐 Variantes trouvées:')} {self.variants_found}")
        
        if 'added' in kwargs:
            self.items_added = kwargs['added']
            self.added_label.setText(f"{lang.get('settings.pages.mass_import_monitor.added', default='✅ Ajoutés:')} {self.items_added}")
        
        if 'failed' in kwargs:
            self.items_failed = kwargs['failed']
            self.failed_label.setText(f"{lang.get('settings.pages.mass_import_monitor.failed', default='❌ Échecs:')} {self.items_failed}")
        
        if 'duplicates' in kwargs:
            self.duplicates_skipped = kwargs['duplicates']
            self.duplicates_label.setText(f"{lang.get('settings.pages.mass_import_monitor.duplicates', default='⏭️ Doublons ignorés:')} {self.duplicates_skipped}")
        
        if 'current_item' in kwargs:
            self.current_item = kwargs['current_item']
            if self.current_item:
                self.current_item_label.setText(f"{lang.get('mass_import_monitor.processing', default='🔍 En cours:')} {self.current_item}")
            else:
                self.current_item_label.setText(lang.get('mass_import_monitor.waiting', default='En attente...'))
        
        # Update unique items count
        self.unique_items_label.setText(f"{lang.get('settings.pages.mass_import_monitor.unique_items', default='🔍 Items uniques:')} {self.items_total}")
        
        # NO processEvents() - UI updates automatically via Qt's event loop
    
    def update_stats_slot(self, stats):
        """Slot for update_stats signal from worker thread"""
        self.update_stats(**stats)
    
    def log_message_slot(self, msg, level):
        """Slot for log_message signal from worker thread"""
        self.log_message(msg, level)
    
    def log_message(self, message, level="info"):
        """Add message to log with coloring
        
        Args:
            message: Message text
            level: Message type (info, success, error, warning, search, variant, duplicate, separator)
        """
        self.log_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine color and icon based on level
        if level == "success":
            color = "#4ec9b0"  # Green
            icon = "✅"
        elif level == "error":
            color = "#f48771"  # Red
            icon = "❌"
        elif level == "warning":
            color = "#ce9178"  # Orange
            icon = "⚠️"
        elif level == "search":
            color = "#dcdcaa"  # Yellow
            icon = "🔍"
        elif level == "variant":
            color = "#569cd6"  # Blue
            icon = "🌐"
        elif level == "duplicate":
            color = "#c586c0"  # Purple
            icon = "⏭️"
        elif level == "separator":
            # Separator line
            self.logs_widget.append('<span style="color: #3a3a3a;">═══════════════════════════════════════════════════════════════════════════════════════════════════════</span>')
            return
        else:  # info
            color = "#9cdcfe"  # Light blue
            icon = "ℹ️"
        
        # Build HTML message
        html_message = f'<span style="color: #808080;">{timestamp}</span> <span style="color: {color};">{icon} {message}</span>'
        
        self.logs_widget.append(html_message)
        
        # Add to errors if level = error or warning
        if level in ("error", "warning"):
            error_entry = f"[{timestamp}] {icon} {message}"
            self.error_list.append(error_entry)
            self.errors_widget.append(f'<span style="color: {color};">{error_entry}</span>')
            self.error_count_label.setText(lang.get('mass_import_monitor.error_count', count=len(self.error_list), default=f"{len(self.error_list)} erreur(s)"))
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            cursor = self.logs_widget.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.logs_widget.setTextCursor(cursor)
    
    def update_elapsed_time(self):
        """Update elapsed time"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_label.setText(f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def clear_logs(self):
        """Clear logs"""
        self.logs_widget.clear()
        self.log_count = 0
        self.log_message(lang.get('mass_import_monitor.logs_cleared', default='Logs effacés'), "info")
    
    def clear_errors(self):
        """Clear error list"""
        self.error_list.clear()
        self.errors_widget.clear()
        self.error_count_label.setText(lang.get('mass_import_monitor.error_count', count=0, default='0 erreur(s)'))
    
    def export_errors(self):
        """Export only errors to file"""
        if not self.error_list:
            from PySide6.QtWidgets import QMessageBox
            SilentMessageBox.information(self, lang.get('mass_import_monitor.export_errors', default='Export erreurs'), 
                                   lang.get('mass_import_monitor.no_errors', default='Aucune erreur à exporter'))
            return
        
        file_path = dialog_save_file(self, "mass_import_monitor.export_errors_title")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Header
                    f.write("=" * 80 + "\n")
                    f.write("MASS IMPORT ERRORS - DAOC Character Manager\n")
                    f.write("=" * 80 + "\n\n")
                    
                    f.write(f"Total errors: {len(self.error_list)}\n")
                    if self.start_time:
                        f.write(f"Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    f.write("\n" + "=" * 80 + "\n\n")
                    
                    # Errors
                    for error in self.error_list:
                        f.write(error + "\n")
                
                from PySide6.QtWidgets import QMessageBox
                SilentMessageBox.information(self, lang.get('mass_import_monitor.export_errors', default='Export erreurs'), 
                                       f"{lang.get('mass_import_monitor.export_success', default='Erreurs exportées vers:')}\n{file_path}")
            
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                SilentMessageBox.critical(self, lang.get('mass_import_monitor.export_errors', default='Export erreurs'), 
                                    f"{lang.get('mass_import_monitor.export_error', default='Impossible d\'exporter les erreurs:')}\n{e}")
    
    def export_logs(self):
        """Export logs to file"""
        file_path = dialog_save_file(self, "mass_import_monitor.export_logs_title")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Header
                    f.write("=" * 80 + "\n")
                    f.write("MASS IMPORT LOG - DAOC Character Manager\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Statistics
                    f.write("STATISTICS:\n")
                    f.write(f"  Unique items: {self.items_total}\n")
                    f.write(f"  Variants found: {self.variants_found}\n")
                    f.write(f"  Items processed: {self.items_processed}\n")
                    f.write(f"  Items added: {self.items_added}\n")
                    f.write(f"  Duplicates skipped: {self.duplicates_skipped}\n")
                    f.write(f"  Failures: {self.items_failed}\n")
                    
                    if self.start_time:
                        elapsed = (datetime.now() - self.start_time).total_seconds()
                        f.write(f"  Duration: {self.format_duration(elapsed)}\n")
                    
                    f.write("\n" + "=" * 80 + "\n\n")
                    
                    # Logs
                    f.write("LOGS:\n\n")
                    f.write(self.logs_widget.toPlainText())
                
                export_msg = lang.get('mass_import_monitor.export_log_success', default='Logs exportés vers:')
                self.info_label.setText(f"✅ {export_msg} {file_path}")
                self.log_message(f"{export_msg} {file_path}", "success")
            except Exception as e:
                error_msg = lang.get('mass_import_monitor.export_log_error', default='Impossible d\'exporter les logs:')
                self.info_label.setText(f"❌ {error_msg} {e}")
                self.log_message(f"{error_msg} {e}", "error")
    
    def set_filtered_items(self, filtered_items):
        """Store filtered items and show review button if items exist"""
        import logging
        
        logging.info(f"set_filtered_items called with {len(filtered_items) if filtered_items else 0} items")
        
        self.filtered_items = filtered_items
        if filtered_items and len(filtered_items) > 0:
            self.review_filtered_btn.setVisible(True)
            self.review_filtered_btn.setText(
                lang.get("settings.pages.mass_import_monitor.review_filtered", count=len(filtered_items),
                        default=f"🔍 Review Filtered Items ({len(filtered_items)})")
            )
            self.log_message(lang.get("settings.pages.mass_import_monitor.filtered_items_warning", count=len(filtered_items), default=f"{len(filtered_items)} item(s) were filtered (Level/Utility restrictions)"), "warning")
            logging.info(f"Review button shown with {len(filtered_items)} items")
            
            # NO processEvents() - UI updates automatically
        else:
            self.review_filtered_btn.setVisible(False)
            logging.info("Review button hidden (no filtered items)")
    
    def open_review_filtered_dialog(self):
        """Open dialog to review and retry filtered items"""
        if not self.filtered_items:
            return
        
        from UI.failed_items_review_dialog import FailedItemsReviewDialog
        
        dialog = FailedItemsReviewDialog(self.filtered_items, self)
        result = dialog.exec()
        
        if result == 1:  # Accepted (Retry)
            selected_items = dialog.get_selected_items()
            self.log_message(f"DEBUG: Retrieved {len(selected_items)} selected items from dialog", "info")
            if selected_items:
                self.log_message("", "separator")
                self.log_message(lang.get("settings.pages.mass_import_monitor.retry_filtered_message", count=len(selected_items), default=f"🔄 Retrying {len(selected_items)} filtered item(s) WITHOUT restrictions..."), "info")
                
                # Show the dialog is closed, import will continue in background
                from PySide6.QtWidgets import QMessageBox
                SilentMessageBox.information(
                    self,
                    lang.get("settings.pages.mass_import_monitor.retry_in_progress_title", default="Retry in Progress"),
                    lang.get("settings.pages.mass_import_monitor.retry_in_progress_message", count=len(selected_items), default=f"Retrying {len(selected_items)} item(s).\n\nThe import will continue in the Database Management Tools window.")
                )
                
                self.emit_retry_request(selected_items)
            else:
                self.log_message("DEBUG: No items selected, skipping retry", "warning")
        
        elif result == 2:  # Custom code for Ignore
            ignored_items = dialog.get_ignored_items()
            if ignored_items:
                self.log_message("", "separator")
                self.log_message(lang.get("settings.pages.mass_import_monitor.ignore_items_message", count=len(ignored_items), default=f"🚫 Ignoring {len(ignored_items)} item(s) permanently..."), "info")
                self.mark_items_as_ignored(ignored_items)
    
    def emit_retry_request(self, items_to_retry):
        """Emit signal or callback to retry import for specific items"""
        items_names = ', '.join([i.get('name', 'Unknown') for i in items_to_retry])
        self.log_message(lang.get("settings.pages.mass_import_monitor.retry_requested_for", items=items_names, default=f"📝 Retry requested for: {items_names}"), "info")
        
        # Create a new worker to retry these items WITHOUT filters
        try:
            from Functions.import_worker import ImportWorker
        except ImportError as e:
            self.log_message(f"Error importing ImportWorker: {e}", "error")
            return
        
        from pathlib import Path
        import tempfile
        
        temp_files = []
        
        try:
            # Group items by realm to create one temp file per realm
            items_by_realm = {}
            for item in items_to_retry:
                realm = item.get('realm', 'All')
                if realm not in items_by_realm:
                    items_by_realm[realm] = []
                items_by_realm[realm].append(item)
            
            # Create temp file for each realm
            for realm, items in items_by_realm.items():
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                
                temp_file.write(f"Retry Template - {realm}\n\n")
                
                for idx, item in enumerate(items):
                    item_name = item.get('name', item.get('original_search', 'Unknown'))
                    item_id = item.get('id', '')
                    
                    # Create simple Zenkcraft-compatible format
                    temp_file.write(f"Item{idx}\n")
                    temp_file.write(f"Name: {item_name}\n")
                    if item_id:
                        temp_file.write(f"ID: {item_id}\n")  # Include Eden ID if available
                    temp_file.write("Level: 51 (100% Quality)\n")
                    temp_file.write("Utility: 100\n")
                    temp_file.write("Source Type: Loot\n\n")
                
                temp_file.close()
                temp_files.append(temp_file.name)
            
            # Create worker with skip_filters=True
            try:
                # Store worker reference to prevent garbage collection
                self.retry_worker = ImportWorker(
                    file_paths=temp_files,
                    realm="All",
                    merge=True,
                    remove_duplicates=True,
                    auto_backup=False,
                    source_db_path=self.source_db_path,  # Use configured path (embedded or personal)
                    path_manager=self.path_manager,
                    skip_filters_mode=True  # NEW PARAMETER
                )
                
            except Exception as e:
                self.log_message(f"Error creating worker: {e}", "error")
                import traceback
                self.log_message(f"Traceback: {traceback.format_exc()}", "error")
                # Clean up temp files
                for tf in temp_files:
                    try:
                        Path(tf).unlink()
                    except Exception:
                        pass
                return
            
            # Connect signals
            from PySide6.QtCore import Qt
            self.retry_worker.progress_updated.connect(self.update_stats_slot)
            self.retry_worker.log_message.connect(self.log_message_slot)
            
            # Reset stats for retry
            self.items_processed = 0
            self.items_added = 0
            self.items_failed = 0
            self.duplicates_skipped = 0
            
            def on_import_finished(success, message, stats):
                """Handle import completion (business logic)"""
                try:
                    self.log_message("Retry completed successfully", "info")
                    self.finish_import(success)
                    
                    # Clean up temp files
                    for tf in temp_files:
                        try:
                            Path(tf).unlink()
                        except Exception:
                            pass
                        
                except Exception as e:
                    self.log_message(f"Error in retry finish: {e}", "error")
                    import traceback
                    self.log_message(f"Traceback: {traceback.format_exc()}", "error")
            
            def on_thread_finished():
                """Handle thread termination (cleanup resources)"""
                try:
                    self.log_message("Retry worker thread finished, cleaning up...", "info")
                    
                    if self.retry_worker is not None:
                        # Wait for thread to fully stop
                        if not self.retry_worker.wait(5000):  # Wait up to 5 seconds
                            self.log_message("Warning: Thread did not finish in time", "warning")
                        
                        # Disconnect signals safely
                        try:
                            self.retry_worker.progress_updated.disconnect()
                            self.retry_worker.log_message.disconnect()
                            self.retry_worker.import_finished.disconnect()
                            self.retry_worker.finished.disconnect()
                        except Exception:
                            pass
                        
                        # Schedule deletion
                        self.retry_worker.deleteLater()
                        self.retry_worker = None
                        self.log_message("Retry worker cleaned up successfully", "info")
                        
                except Exception as cleanup_error:
                    self.log_message(f"Error in thread cleanup: {cleanup_error}", "warning")
                    import traceback
                    self.log_message(f"Traceback: {traceback.format_exc()}", "warning")
            
            # Connect import_finished for business logic
            self.retry_worker.import_finished.connect(on_import_finished, Qt.QueuedConnection)
            
            # Connect finished (QThread signal) for cleanup - this is emitted when thread actually stops
            self.retry_worker.finished.connect(on_thread_finished, Qt.QueuedConnection)
            
            # Start retry
            self.start_import(len(items_to_retry))
            
            # Keep close button enabled during retry so user can close if needed
            self.close_button.setEnabled(True)
            
            self.retry_worker.start()
            
        except Exception as e:
            self.log_message(f"CRASH during retry: {str(e)}", "error")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")
            # Clean up temp files
            for tf in temp_files:
                try:
                    Path(tf).unlink()
                except Exception:
                    pass
    
    def mark_items_as_ignored(self, items_to_ignore):
        """Mark items as permanently ignored in the database"""
        try:
            import json
            
            # Use the appropriate database path (embedded or personal)
            db_path = self.source_db_path
            if not db_path.exists():
                self.log_message(f"⚠️ Database not found: {db_path}", "warning")
                return
            
            # Load DB
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            
            items_dict = db_data.get('items', {})
            ignored_count = 0
            
            for item in items_to_ignore:
                item_name = item.get('name', item.get('original_search', 'Unknown')).lower()
                item_realm = item.get('realm', 'All')
                item_id = item.get('id', '')
                
                # Create key pattern (name:realm or just name)
                key_base = f"{item_name}:{item_realm.lower()}"
                
                # Try to find matching item(s) in DB
                found = False
                for key, item_data in items_dict.items():
                    # Match by name and realm, or by ID if available
                    if key.startswith(item_name + ":") or (item_id and item_data.get('id') == item_id):
                        item_data['ignore_item'] = True
                        ignored_count += 1
                        found = True
                        self.log_message(lang.get("settings.pages.mass_import_monitor.item_marked_ignored", name=item_name, default=f"  ✓ Marked '{item_name}' as ignored"), "info")
                
                if not found:
                    # Item not in DB yet, add it with ignore flag
                    items_dict[key_base] = {
                        "id": item_id,
                        "name": item_name,
                        "realm": item_realm,
                        "ignore_item": True
                    }
                    ignored_count += 1
                    self.log_message(lang.get("settings.pages.mass_import_monitor.item_added_ignore_list", name=item_name, default=f"  ✓ Added '{item_name}' to ignore list"), "info")
            
            # Save updated DB
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, indent=2, ensure_ascii=False)
            
            self.log_message(lang.get("settings.pages.mass_import_monitor.items_ignored_success", count=ignored_count, default=f"✅ Successfully ignored {ignored_count} item(s)"), "success")
            
            # Remove ignored items from filtered_items list
            self.filtered_items = [
                item for item in self.filtered_items
                if item not in items_to_ignore
            ]
            
            # Update button visibility
            self.set_filtered_items(self.filtered_items)
            
        except Exception as e:
            self.log_message(lang.get("settings.pages.mass_import_monitor.error_marking_ignored", error=str(e), default=f"❌ Error marking items as ignored: {e}"), "error")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")
    
    def closeEvent(self, event):
        """Handle window close event"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("MassImportMonitor closeEvent triggered")
        
        # If a retry worker is running, warn and wait
        if hasattr(self, 'retry_worker') and self.retry_worker is not None:
            if self.retry_worker.isRunning():
                logger.warning("Retry worker still running, waiting for completion...")
                self.retry_worker.wait(5000)  # Wait up to 5 seconds
                logger.info("Retry worker finished")
        
        # Stop timers
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        logger.info("MassImportMonitor closing normally")
        event.accept()


