"""
Mass Import Monitor Window
Detailed monitoring window for mass item import
"""

import logging
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTextEdit, QPushButton, QLabel, QProgressBar, QFileDialog,
    QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor

from Functions.language_manager import lang


class MassImportMonitor(QMainWindow):
    """Monitoring window for mass import with detailed logs and statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get("mass_import_monitor.window_title", default="📦 Mass Import Monitor"))
        self.setGeometry(150, 100, 1200, 700)
        
        # Make window independent and always movable
        self.setWindowFlags(
            Qt.Window  # Independent window (removed StaysOnTop)
        )
        
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
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # === HEADER: Title and time ===
        header_layout = QHBoxLayout()
        
        title_label = QLabel(lang.get("mass_import_monitor.title", default="📦 Import en Masse - Monitoring en Temps Réel"))
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
        
        # === STATISTICS PANEL ===
        stats_group = QGroupBox(lang.get("mass_import_monitor.stats_group", default="📊 Statistiques en Temps Réel"))
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
        self.unique_items_label = QLabel(lang.get("mass_import_monitor.unique_items", default="🔍 Items uniques:") + " 0")
        self.unique_items_label.setStyleSheet("font-size: 11pt; color: #dcdcaa;")
        stats_layout.addWidget(self.unique_items_label, 0, 0)
        
        self.variants_label = QLabel(lang.get("mass_import_monitor.variants_found", default="🌐 Variantes trouvées:") + " 0")
        self.variants_label.setStyleSheet("font-size: 11pt; color: #569cd6;")
        stats_layout.addWidget(self.variants_label, 0, 1)
        
        self.processed_label = QLabel(lang.get("mass_import_monitor.items_processed", default="⚙️ Items traités:") + " 0 / 0")
        self.processed_label.setStyleSheet("font-size: 11pt; color: #9cdcfe;")
        stats_layout.addWidget(self.processed_label, 0, 2)
        
        # Row 2: Results
        self.added_label = QLabel(lang.get("mass_import_monitor.added", default="✅ Ajoutés:") + " 0")
        self.added_label.setStyleSheet("font-size: 11pt; color: #4ec9b0;")
        stats_layout.addWidget(self.added_label, 1, 0)
        
        self.duplicates_label = QLabel(lang.get("mass_import_monitor.duplicates", default="⏭️ Doublons ignorés:") + " 0")
        self.duplicates_label.setStyleSheet("font-size: 11pt; color: #ce9178;")
        stats_layout.addWidget(self.duplicates_label, 1, 1)
        
        self.failed_label = QLabel(lang.get("mass_import_monitor.failed", default="❌ Échecs:") + " 0")
        self.failed_label.setStyleSheet("font-size: 11pt; color: #f48771;")
        stats_layout.addWidget(self.failed_label, 1, 2)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # === HORIZONTAL LAYOUT: LOGS + FILES (50/50) ===
        files_logs_layout = QHBoxLayout()
        
        # === LOGS PANEL (LEFT) ===
        logs_group = QGroupBox(lang.get("mass_import_monitor.logs_group", default="📋 Logs Détaillés"))
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
        
        self.clear_button = QPushButton(lang.get("mass_import_monitor.clear_button", default="🗑️ Effacer"))
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        self.export_button = QPushButton(lang.get("mass_import_monitor.export_button", default="💾 Exporter"))
        self.export_button.clicked.connect(self.export_logs)
        self.export_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        
        self.autoscroll_label = QLabel(lang.get("mass_import_monitor.autoscroll", default="📜 Auto-scroll: ON"))
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
        files_group = QGroupBox(lang.get("mass_import_monitor.files_group", default="📁 Fichiers Template"))
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
        progress_group = QGroupBox(lang.get("mass_import_monitor.progress_group", default="📈 Progression"))
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
        
        self.current_item_label = QLabel(lang.get("mass_import_monitor.waiting", default="En attente..."))
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
        errors_group = QGroupBox(lang.get("mass_import_monitor.errors_group", default="⚠️ Suivi des Erreurs"))
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
        
        self.clear_errors_button = QPushButton(lang.get("mass_import_monitor.clear_errors", default="🗑️ Effacer erreurs"))
        self.clear_errors_button.clicked.connect(self.clear_errors)
        self.clear_errors_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        error_buttons_layout.addWidget(self.clear_errors_button)
        
        self.export_errors_button = QPushButton(lang.get("mass_import_monitor.export_errors", default="💾 Exporter erreurs"))
        self.export_errors_button.clicked.connect(self.export_errors)
        self.export_errors_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                font-size: 10pt;
            }
        """)
        error_buttons_layout.addWidget(self.export_errors_button)
        
        error_buttons_layout.addStretch()
        
        self.error_count_label = QLabel(lang.get("mass_import_monitor.error_count", count=0, default="0 erreur(s)"))
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
        
        self.info_label = QLabel(lang.get("mass_import_monitor.ready", default="Prêt à démarrer l'import..."))
        self.info_label.setStyleSheet("color: #808080; font-style: italic; font-size: 9pt;")
        footer_layout.addWidget(self.info_label)
        
        footer_layout.addStretch()
        
        self.review_filtered_btn = QPushButton(lang.get("mass_import_monitor.review_filtered", default="🔍 Review Filtered Items"))
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
        
        self.close_button = QPushButton(lang.get("mass_import_monitor.close_button", default="❌ Fermer"))
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
        
        # Timer to force UI refresh during import (anti-freeze)
        self.ui_refresh_timer = QTimer()
        self.ui_refresh_timer.timeout.connect(self._force_ui_refresh)
        
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
        self.ui_refresh_timer.start(50)  # Force UI refresh every 50ms (anti-freeze)
        
        self.close_button.setEnabled(False)
        
        self.log_message("Démarrage de l'import en masse...", "info")
        if template_files:
            self.log_message(f"{len(template_files)} fichier(s) template à parser", "info")
        self.log_message(f"{total_items} items uniques à traiter", "info")
    
    def finish_import(self, success=True):
        """Finish import"""
        from PySide6.QtWidgets import QApplication
        
        self.timer.stop()
        self.ui_refresh_timer.stop()  # Stop anti-freeze timer
        self.close_button.setEnabled(True)
        
        # Force UI update
        QApplication.processEvents()
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        if success:
            self.log_message("", "separator")
            self.log_message(f"Import terminé avec succès en {self.format_duration(elapsed)}", "success")
            self.log_message(f"Résumé: {self.items_added} ajoutés, {self.duplicates_skipped} doublons, {self.items_failed} échecs", "info")
            self.info_label.setText(f"✅ Import terminé - {self.items_added} items ajoutés")
        else:
            self.log_message("", "separator")
            self.log_message("Import terminé avec des erreurs", "error")
            self.info_label.setText("❌ Import terminé avec des erreurs")
    
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
        from PySide6.QtWidgets import QApplication
        
        if 'total' in kwargs:
            self.items_total = kwargs['total']
            self.progress_bar.setMaximum(self.items_total)
        
        if 'processed' in kwargs:
            self.items_processed = kwargs['processed']
            self.processed_label.setText(f"{lang.get('mass_import_monitor.items_processed', default='⚙️ Items traités:')} {self.items_processed} / {self.items_total}")
            
            # Update progress bar
            if self.items_total > 0:
                progress = int((self.items_processed / self.items_total) * 100)
                self.progress_bar.setValue(self.items_processed)
        
        if 'variants' in kwargs:
            self.variants_found = kwargs['variants']
            self.variants_label.setText(f"{lang.get('mass_import_monitor.variants_found', default='🌐 Variantes trouvées:')} {self.variants_found}")
        
        if 'added' in kwargs:
            self.items_added = kwargs['added']
            self.added_label.setText(f"{lang.get('mass_import_monitor.added', default='✅ Ajoutés:')} {self.items_added}")
        
        if 'failed' in kwargs:
            self.items_failed = kwargs['failed']
            self.failed_label.setText(f"{lang.get('mass_import_monitor.failed', default='❌ Échecs:')} {self.items_failed}")
        
        if 'duplicates' in kwargs:
            self.duplicates_skipped = kwargs['duplicates']
            self.duplicates_label.setText(f"{lang.get('mass_import_monitor.duplicates', default='⏭️ Doublons ignorés:')} {self.duplicates_skipped}")
        
        if 'current_item' in kwargs:
            self.current_item = kwargs['current_item']
            if self.current_item:
                self.current_item_label.setText(f"{lang.get('mass_import_monitor.processing', default='🔍 En cours:')} {self.current_item}")
            else:
                self.current_item_label.setText(lang.get('mass_import_monitor.waiting', default='En attente...'))
        
        # Update unique items count
        self.unique_items_label.setText(f"{lang.get('mass_import_monitor.unique_items', default='🔍 Items uniques:')} {self.items_total}")
        
        # Force UI refresh to prevent freezing
        QApplication.processEvents()
    
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
    
    def _force_ui_refresh(self):
        """Force UI refresh to prevent freeze (called every 50ms)"""
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
    
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
            QMessageBox.information(self, lang.get('mass_import_monitor.export_errors', default='Export erreurs'), 
                                   lang.get('mass_import_monitor.no_errors', default='Aucune erreur à exporter'))
            return
        
        filename = f"mass_import_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les erreurs d'import",
            filename,
            "Fichiers texte (*.txt);;Tous les fichiers (*.*)"
        )
        
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
                QMessageBox.information(self, lang.get('mass_import_monitor.export_errors', default='Export erreurs'), 
                                       f"{lang.get('mass_import_monitor.export_success', default='Erreurs exportées vers:')}\n{file_path}")
            
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, lang.get('mass_import_monitor.export_errors', default='Export erreurs'), 
                                    f"{lang.get('mass_import_monitor.export_error', default='Impossible d\'exporter les erreurs:')}\n{e}")
    
    def export_logs(self):
        """Export logs to file"""
        filename = f"mass_import_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les logs d'import",
            filename,
            "Fichiers texte (*.txt);;Tous les fichiers (*.*)"
        )
        
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
        from PySide6.QtWidgets import QApplication
        
        logging.info(f"set_filtered_items called with {len(filtered_items) if filtered_items else 0} items")
        
        self.filtered_items = filtered_items
        if filtered_items and len(filtered_items) > 0:
            self.review_filtered_btn.setVisible(True)
            self.review_filtered_btn.setText(
                lang.get("mass_import_monitor.review_filtered", count=len(filtered_items),
                        default=f"🔍 Review Filtered Items ({len(filtered_items)})")
            )
            self.log_message(f"{len(filtered_items)} item(s) were filtered (Level/Utility restrictions)", "warning")
            logging.info(f"Review button shown with {len(filtered_items)} items")
            
            # Force UI update
            QApplication.processEvents()
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
                self.log_message(f"🔄 Retrying {len(selected_items)} filtered item(s) WITHOUT restrictions...", "info")
                self.emit_retry_request(selected_items)
            else:
                self.log_message("DEBUG: No items selected, skipping retry", "warning")
        
        elif result == 2:  # Custom code for Ignore
            ignored_items = dialog.get_ignored_items()
            if ignored_items:
                self.log_message("", "separator")
                self.log_message(f"🚫 Ignoring {len(ignored_items)} item(s) permanently...", "info")
                self.mark_items_as_ignored(ignored_items)
    
    def emit_retry_request(self, items_to_retry):
        """Emit signal or callback to retry import for specific items"""
        self.log_message(f"📝 Retry requested for: {', '.join([i.get('name', 'Unknown') for i in items_to_retry])}", "info")
        
        # Create a new worker to retry these items WITHOUT filters
        from Functions.import_worker import ImportWorker
        from Functions.superadmin_tools import SuperAdminTools
        from PySide6.QtCore import QEventLoop
        
        # Create temporary file paths with just the item names
        import tempfile
        from pathlib import Path
        
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
                worker = ImportWorker(
                    file_paths=temp_files,
                    realm="All",
                    merge=True,
                    remove_duplicates=True,
                    auto_backup=False,
                    source_db_path=Path("Data/items_database_src.json"),
                    path_manager=None,
                    skip_filters_mode=True  # NEW PARAMETER
                )
            except Exception as e:
                self.log_message(f"Error creating worker: {e}", "error")
                # Clean up temp files
                for tf in temp_files:
                    try:
                        Path(tf).unlink()
                    except:
                        pass
                return
            
            # Connect signals
            worker.progress_updated.connect(lambda stats: self.update_stats(**stats))
            worker.log_message.connect(lambda msg, level: self.log_message(msg, level))
            
            # Reset stats for retry
            self.items_processed = 0
            self.items_added = 0
            self.items_failed = 0
            self.duplicates_skipped = 0
            
            def on_finished(success, message, stats):
                try:
                    self.finish_import(success)
                    
                    # Clean up temp files
                    for tf in temp_files:
                        try:
                            Path(tf).unlink()
                        except:
                            pass
                    
                    self.log_message("Retry completed successfully", "info")
                except Exception as e:
                    self.log_message(f"Error in retry finish: {e}", "error")
            
            worker.import_finished.connect(on_finished)
            
            # Start retry
            self.start_import(len(items_to_retry))
            worker.start()
            
        except Exception as e:
            self.log_message(f"CRASH during retry: {str(e)}", "error")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")
            # Clean up temp files
            for tf in temp_files:
                try:
                    Path(tf).unlink()
                except:
                    pass
    
    def mark_items_as_ignored(self, items_to_ignore):
        """Mark items as permanently ignored in the database"""
        try:
            from pathlib import Path
            import json
            
            db_path = Path("Data/items_database_src.json")
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
                        self.log_message(f"  ✓ Marked '{item_name}' as ignored", "info")
                
                if not found:
                    # Item not in DB yet, add it with ignore flag
                    items_dict[key_base] = {
                        "id": item_id,
                        "name": item_name,
                        "realm": item_realm,
                        "ignore_item": True
                    }
                    ignored_count += 1
                    self.log_message(f"  ✓ Added '{item_name}' to ignore list", "info")
            
            # Save updated DB
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, indent=2, ensure_ascii=False)
            
            self.log_message(f"✅ Successfully ignored {ignored_count} item(s)", "success")
            
            # Remove ignored items from filtered_items list
            self.filtered_items = [
                item for item in self.filtered_items
                if item not in items_to_ignore
            ]
            
            # Update button visibility
            self.set_filtered_items(self.filtered_items)
            
        except Exception as e:
            self.log_message(f"❌ Error marking items as ignored: {e}", "error")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")


