#!/usr/bin/env python3
"""
Log Source Editor - Outil pour éditer les logs directement dans le code source

Permet de:
- Scanner tous les fichiers Python du projet
- Trouver tous les appels de logging (logger.info, logger.debug, etc.)
- Afficher et éditer les ACTIONS et MESSAGES
- Sauvegarder les modifications dans les fichiers source
- Mémoriser le dernier projet édité et le charger automatiquement au démarrage

Fonctionnalités:
- 🔍 Scan récursif de tous les fichiers .py
- 📋 Table interactive avec filtres (Logger, Level, Modified)
- ✏️ Éditeur avec ComboBox d'actions (historique + auto-complétion)
- ⌨️ Raccourcis clavier (Enter, Ctrl+Enter)
- 💾 Sauvegarde directe dans les fichiers source
- 📂 Chargement automatique du dernier projet au démarrage
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QLineEdit, QTextEdit, QMessageBox, QHeaderView, QProgressBar,
    QGroupBox, QSplitter, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QColor, QFont, QKeySequence, QShortcut

# Import des loggers constants depuis le système de logging
sys.path.insert(0, str(Path(__file__).parent.parent))
from Functions.logging_manager import ALL_LOGGERS, LOGGER_ROOT


class LogEntry:
    """Représente un log trouvé dans le code source"""
    def __init__(self, file_path: str, line_number: int, logger_name: str, 
                 level: str, action: str, message: str, full_line: str):
        self.file_path = file_path
        self.line_number = line_number
        self.logger_name = logger_name
        self.level = level
        self.action = action  # Peut être vide
        self.message = message
        self.full_line = full_line  # Ligne complète pour remplacement
        self.modified = False
        self.new_logger = logger_name  # Nouveau logger (peut être changé)
        self.new_action = action
        self.new_message = message
    
    def __eq__(self, other):
        """Comparer deux logs par fichier + ligne"""
        if not isinstance(other, LogEntry):
            return False
        return self.file_path == other.file_path and self.line_number == other.line_number
    
    def __hash__(self):
        """Hash pour pouvoir utiliser dans des sets/dicts"""
        return hash((self.file_path, self.line_number))


class LogScanner(QThread):
    """Thread pour scanner les fichiers et trouver les logs"""
    progress = Signal(int, int)  # (current, total)
    log_found = Signal(LogEntry)
    finished_scanning = Signal(int)  # total logs found
    
    def __init__(self, root_path: str):
        super().__init__()
        self.root_path = Path(root_path)
        self.count = 0  # Compteur simple au lieu d'une liste
        
    def run(self):
        """Scanner tous les fichiers Python"""
        # Patterns pour détecter les logs
        # Pattern 1: logger.info(), self.logger.debug(), module_logger.warning()
        logger_pattern = re.compile(
            r'(?:self\.)?(?:module_)?logger\.(?P<level>debug|info|warning|error|critical)\s*\(',
            re.IGNORECASE
        )
        
        # Pattern 2: log_with_action(logger, "info", ...)
        log_with_action_pattern = re.compile(
            r'log_with_action\s*\([^,]+,\s*["\'](?P<level>debug|info|warning|error|critical)["\']',
            re.IGNORECASE
        )
        
        # Trouver tous les fichiers Python
        py_files = list(self.root_path.rglob("*.py"))
        total = len(py_files)
        
        for idx, file_path in enumerate(py_files):
            self.progress.emit(idx + 1, total)
            
            # Skip __pycache__, .venv, build, dist
            skip_dirs = ['__pycache__', '.venv', 'build', 'dist', '.git']
            if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.splitlines()
                    
                # Chercher les logs ligne par ligne
                for line_num, line in enumerate(lines, start=1):
                    # Essayer le pattern logger.xxx()
                    match = logger_pattern.search(line)
                    if not match:
                        # Essayer le pattern log_with_action()
                        match = log_with_action_pattern.search(line)
                    
                    if match:
                        # Extraire le level
                        level = match.group('level').upper()
                        
                        # Extraire le logger name du contexte du fichier
                        logger_name = self._detect_logger_name(file_path, lines)
                        
                        # Parser le contenu pour extraire message et action
                        action, message = self._parse_log_content(line)
                        
                        # Créer l'entrée
                        log_entry = LogEntry(
                            file_path=str(file_path),
                            line_number=line_num,
                            logger_name=logger_name,
                            level=level,
                            action=action,
                            message=message,
                            full_line=line.strip()
                        )
                        
                        # Émettre le log trouvé (sera ajouté dans _on_log_found)
                        self.log_found.emit(log_entry)
                        self.count += 1
                        
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                
        self.finished_scanning.emit(self.count)
    
    def _detect_logger_name(self, file_path: Path, lines) -> str:
        """Détecte le nom du logger en analysant le fichier"""
        file_str = str(file_path).lower()
        
        # Mapping basé sur le chemin du fichier
        if 'eden_scraper' in file_str or 'eden' in file_str:
            return 'EDEN'
        elif 'backup' in file_str or 'migration' in file_str:
            return 'BACKUP'
        elif 'ui' in file_str or 'window' in file_str:
            return 'UI'
        elif 'character' in file_str:
            return 'CHARACTER'
        
        # Chercher dans le code: get_logger(LOGGER_XXX) ou setup_logger("LOGGER_NAME")
        for line in lines:
            # get_logger(LOGGER_BACKUP)
            if 'get_logger' in line and 'LOGGER_' in line:
                match = re.search(r'get_logger\(LOGGER_([A-Z_]+)\)', line)
                if match:
                    return match.group(1)
            # setup_logger("LOGGER_NAME")
            if 'setup_logger' in line:
                match = re.search(r'setup_logger\(["\']([A-Z_]+)["\']', line)
                if match:
                    return match.group(1)
        
        return 'ROOT'
    
    def _parse_log_content(self, line: str) -> Tuple[str, str]:
        """Parse le contenu d'un log pour extraire action et message"""
        action = ""
        message = ""
        
        # Cas 1: log_with_action(logger, "level", "message", action="ACTION")
        if 'log_with_action' in line:
            # Extraire l'action du paramètre action="..."
            action_match = re.search(r'action\s*=\s*["\']([^"\']+)["\']', line)
            if action_match:
                action = action_match.group(1)
            
            # Extraire le message (troisième paramètre)
            msg_match = re.search(r'log_with_action\([^,]+,\s*["\'][^"\']+["\']\s*,\s*([fFrRbB]?["\'])(.+?)(?:\1)', line)
            if msg_match:
                message = msg_match.group(2)
            else:
                # Fallback: chercher la première string après la virgule
                msg_fallback = re.search(r'log_with_action\([^,]+,\s*["\'][^"\']+["\']\s*,\s*([^,]+)', line)
                if msg_fallback:
                    message = msg_fallback.group(1).strip()
        else:
            # Cas 2: logger.info("message", extra={"action": "..."})
            # Chercher extra={"action": "..."} ou extra={'action': '...'}
            action_match = re.search(r'extra\s*=\s*{\s*["\']action["\']\s*:\s*["\']([^"\']+)["\']', line)
            if action_match:
                action = action_match.group(1)
            
            # Extraire le message (première string dans l'appel)
            # Gérer les f-strings, strings normales, et concaténations
            msg_match = re.search(r'logger\.\w+\s*\(\s*([fFrRbB]?["\'])(.*?)(?:["\'])', line)
            if msg_match:
                message = msg_match.group(2)
            else:
                # Fallback: prendre tout après la parenthèse jusqu'à la virgule ou fin
                msg_fallback = re.search(r'logger\.\w+\s*\(\s*(.+?)(?:,|\))', line)
                if msg_fallback:
                    message = msg_fallback.group(1).strip()
        
        # Limiter la longueur pour l'affichage
        if len(message) > 80:
            message = message[:80] + "..."
            
        return action, message


class LogSourceEditor(QMainWindow):
    """
    Éditeur de logs au niveau du code source
    Permet de scanner, visualiser et modifier les logs avant compilation
    """
    
    # Fichier de configuration pour sauvegarder les préférences
    CONFIG_FILE = Path(__file__).parent / "log_editor_config.json"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Log Source Editor - Modifier les logs avant compilation")
        self.setGeometry(100, 100, 1400, 800)
        
        self.logs = []  # Liste de LogEntry
        self.current_log = None
        self._updating = False  # Flag pour éviter les boucles de mise à jour
        self.last_project_path = None  # Chemin du dernier projet scanné
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Table des logs (gauche)
        table_group = self._create_log_table()
        splitter.addWidget(table_group)
        
        # Éditeur (droite)
        editor_group = self._create_editor()
        splitter.addWidget(editor_group)
        
        splitter.setSizes([800, 600])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Prêt")
        main_layout.addWidget(self.status_label)
        
        # Charger la configuration et le dernier projet
        self._load_config()
        
    def _load_config(self):
        """Charge la configuration sauvegardée"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.last_project_path = config.get('last_project_path')
                    
                    # Charger automatiquement le dernier projet si le chemin existe
                    if self.last_project_path and Path(self.last_project_path).exists():
                        # Scanner après un court délai pour permettre à l'UI de se charger
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(100, lambda: self._scan_path(self.last_project_path))
                        self.status_label.setText(f"📂 Chargement du dernier projet: {self.last_project_path}")
                    elif self.last_project_path:
                        self.status_label.setText(f"⚠️ Dernier projet introuvable: {self.last_project_path}")
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
    
    def _save_config(self):
        """Sauvegarde la configuration"""
        try:
            config = {
                'last_project_path': self.last_project_path
            }
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
        
    def _create_toolbar(self) -> QWidget:
        """Crée la barre d'outils"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        
        # Bouton scanner
        scan_btn = QPushButton("🔍 Scanner le projet")
        scan_btn.clicked.connect(self.scan_project)
        toolbar_layout.addWidget(scan_btn)
        
        toolbar_layout.addSpacing(20)
        
        # Filtre par logger - Pre-remplir avec les loggers existants
        toolbar_layout.addWidget(QLabel("Logger:"))
        self.logger_filter = QComboBox()
        self.logger_filter.addItem("Tous", "ALL")
        # Ajouter les loggers du système
        for logger_name in ALL_LOGGERS:
            self.logger_filter.addItem(logger_name, logger_name)
        self.logger_filter.addItem(LOGGER_ROOT, LOGGER_ROOT)
        self.logger_filter.currentTextChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.logger_filter)
        
        # Filtre par level
        toolbar_layout.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["Tous", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.level_filter)
        
        # Filtre "Modifiés uniquement"
        toolbar_layout.addWidget(QLabel("Affichage:"))
        self.modified_filter = QComboBox()
        self.modified_filter.addItems(["Tous", "Modifiés uniquement"])
        self.modified_filter.currentTextChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.modified_filter)
        
        # Recherche
        toolbar_layout.addWidget(QLabel("🔎"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Rechercher dans les messages...")
        self.search_box.textChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.search_box)
        
        toolbar_layout.addStretch()
        
        # Statistiques
        self.stats_label = QLabel("📊 0 logs")
        toolbar_layout.addWidget(self.stats_label)
        
        toolbar_layout.addSpacing(20)
        
        # Bouton sauvegarder
        save_btn = QPushButton("💾 Sauvegarder les modifications")
        save_btn.clicked.connect(self.save_modifications)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;")
        toolbar_layout.addWidget(save_btn)
        
        return toolbar_widget
    
    def _create_log_table(self) -> QGroupBox:
        """Crée la table affichant les logs"""
        group = QGroupBox("📋 Logs trouvés dans le code")
        layout = QVBoxLayout(group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Table
        self.table = QTableWidget(0, 7)  # 7 colonnes
        self.table.setHorizontalHeaderLabels([
            "Fichier", "Ligne", "Logger", "Level", "Action", "Message", "Modifié"
        ])
        
        # IMPORTANT: Table en lecture seule - utiliser l'éditeur à droite pour modifier
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Configurer les colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Fichier
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Ligne
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Logger
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Level
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Action
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Message
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Modifié
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_log_selected)
        
        layout.addWidget(self.table)
        
        return group
    
    def _create_editor(self) -> QGroupBox:
        """Crée l'éditeur pour modifier un log"""
        group = QGroupBox("✏️ Éditeur de log")
        layout = QVBoxLayout(group)
        
        # Info fichier
        self.file_label = QLabel("Aucun log sélectionné")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)
        
        # Logger (éditable via ComboBox) et Level (lecture seule)
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Logger:"))
        self.logger_combo = QComboBox()
        self.logger_combo.addItem("ROOT", LOGGER_ROOT)
        for logger_name in ALL_LOGGERS:
            self.logger_combo.addItem(logger_name, logger_name)
        self.logger_combo.setToolTip("Sélectionner le logger pour ce log")
        info_layout.addWidget(self.logger_combo)
        
        info_layout.addWidget(QLabel("Level:"))
        self.level_display = QLineEdit()
        self.level_display.setReadOnly(True)
        info_layout.addWidget(self.level_display)
        layout.addLayout(info_layout)
        
        # Action (combobox éditable avec historique)
        layout.addWidget(QLabel("🎯 Action: (Enter pour appliquer)"))
        self.action_combo = QComboBox()
        self.action_combo.setEditable(True)
        self.action_combo.setInsertPolicy(QComboBox.NoInsert)  # Ne pas ajouter automatiquement
        self.action_combo.lineEdit().setPlaceholderText("Ex: INIT, TEST, SCRAPE, SEARCH, etc.")
        self.action_combo.lineEdit().returnPressed.connect(self.apply_changes)  # Enter pour appliquer
        layout.addWidget(self.action_combo)
        
        # Message (éditable)
        layout.addWidget(QLabel("💬 Message: (Ctrl+Enter pour appliquer)"))
        self.message_edit = QTextEdit()
        self.message_edit.setMaximumHeight(150)
        layout.addWidget(self.message_edit)
        
        # Raccourci Ctrl+Enter pour appliquer depuis le champ Message
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.message_edit)
        shortcut.activated.connect(self.apply_changes)
        
        # Code original
        layout.addWidget(QLabel("📄 Code original:"))
        self.original_code = QTextEdit()
        self.original_code.setReadOnly(True)
        self.original_code.setMaximumHeight(100)
        self.original_code.setStyleSheet("background-color: #f5f5f5; font-family: 'Courier New';")
        layout.addWidget(self.original_code)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Appliquer")
        apply_btn.clicked.connect(self.apply_changes)
        apply_btn.setToolTip("Appliquer les modifications à ce log")
        btn_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("↩️ Réinitialiser")
        reset_btn.clicked.connect(self.reset_changes)
        reset_btn.setToolTip("Annuler les modifications")
        btn_layout.addWidget(reset_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        return group
    
    def scan_project(self):
        """Scanner le projet pour trouver les logs"""
        # Par défaut, utiliser le dernier projet ou le dossier parent (racine du projet)
        default_path = self.last_project_path if self.last_project_path and Path(self.last_project_path).exists() else str(Path(__file__).parent.parent)
        
        project_root = QFileDialog.getExistingDirectory(
            self, "Sélectionner le dossier du projet",
            default_path
        )
        
        if not project_root:
            return
        
        # Sauvegarder le chemin du projet
        self.last_project_path = project_root
        self._save_config()
        
        # Lancer le scan
        self._scan_path(project_root)
    
    def _scan_path(self, project_root: str):
        """Scanner un chemin spécifique"""
        # Confirmation si beaucoup de fichiers
        py_count = len(list(Path(project_root).rglob("*.py")))
        
        reply = QMessageBox.question(
            self,
            "Confirmer le scan",
            f"🔍 Scanner {py_count} fichiers Python dans :\n{project_root}\n\n"
            f"Voulez-vous continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Clear table
        self.table.setRowCount(0)
        self.logs.clear()
        self.current_log = None
        
        # Réinitialiser l'éditeur
        self.file_label.setText("Aucun log sélectionné")
        self.logger_display.clear()
        self.level_display.clear()
        self.action_combo.clearEditText()
        self.message_edit.clear()
        self.original_code.clear()
        
        # Lancer le scan
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🔍 Scan en cours...")
        
        self.scanner = LogScanner(project_root)
        self.scanner.progress.connect(self._on_scan_progress)
        self.scanner.log_found.connect(self._on_log_found)
        self.scanner.finished_scanning.connect(self._on_scan_finished)
        self.scanner.start()
    
    def _on_scan_progress(self, current, total):
        """Mise à jour de la progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
    def _on_log_found(self, log_entry: LogEntry):
        """Ajouter un log à la table"""
        self.logs.append(log_entry)
        self._add_log_to_table(log_entry)
        
        # Mettre à jour les statistiques
        self._update_stats()
    
    def _add_log_to_table(self, log: LogEntry):
        """Ajouter une ligne à la table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Fichier (relatif)
        file_item = QTableWidgetItem(Path(log.file_path).name)
        file_item.setToolTip(log.file_path)
        file_item.setData(Qt.UserRole, log)
        self.table.setItem(row, 0, file_item)
        
        # Ligne
        self.table.setItem(row, 1, QTableWidgetItem(str(log.line_number)))
        
        # Logger
        logger_item = QTableWidgetItem(log.logger_name)
        logger_item.setForeground(QColor("#2196F3"))
        self.table.setItem(row, 2, logger_item)
        
        # Level
        level_item = QTableWidgetItem(log.level)
        level_colors = {
            "DEBUG": QColor("#9E9E9E"),
            "INFO": QColor("#4CAF50"),
            "WARNING": QColor("#FF9800"),
            "ERROR": QColor("#F44336"),
            "CRITICAL": QColor("#B71C1C")
        }
        level_item.setForeground(level_colors.get(log.level, QColor("#000000")))
        font = QFont()
        font.setBold(True)
        level_item.setFont(font)
        self.table.setItem(row, 3, level_item)
        
        # Action
        action_text = log.action if log.action else "-"
        action_item = QTableWidgetItem(action_text)
        if not log.action:
            action_item.setForeground(QColor("#999999"))
        self.table.setItem(row, 4, action_item)
        
        # Message
        msg_preview = log.message[:60] + "..." if len(log.message) > 60 else log.message
        self.table.setItem(row, 5, QTableWidgetItem(msg_preview))
        
        # Modifié
        modified_item = QTableWidgetItem("✓" if log.modified else "")
        modified_item.setTextAlignment(Qt.AlignCenter)
        if log.modified:
            modified_item.setForeground(QColor("#4CAF50"))
        self.table.setItem(row, 6, modified_item)
    
    def _on_scan_finished(self, total):
        """Scan terminé"""
        self.progress_bar.setVisible(False)
        self._update_stats()
        
        # Collecter toutes les actions uniques déjà présentes
        unique_actions = set()
        for log in self.logs:
            if log.action:  # Ignorer les actions vides
                unique_actions.add(log.action)
        
        # Pré-remplir le combobox avec les actions trouvées
        self.action_combo.clear()
        for action in sorted(unique_actions):
            self.action_combo.addItem(action)
        
        # Statistiques détaillées
        by_logger = {}
        by_level = {}
        with_action = 0
        without_action = 0
        
        for log in self.logs:
            by_logger[log.logger_name] = by_logger.get(log.logger_name, 0) + 1
            by_level[log.level] = by_level.get(log.level, 0) + 1
            if log.action:
                with_action += 1
            else:
                without_action += 1
        
        # Mettre à jour le titre de la fenêtre avec le projet scanné
        project_name = Path(self.scanner.root_path).name
        self.setWindowTitle(f"🔧 Log Source Editor - {project_name} ({total} logs)")
        
        # Construire le message
        stats_msg = f"✅ Scan terminé : {total} logs trouvés\n\n"
        
        stats_msg += "📊 Par Logger :\n"
        for logger, count in sorted(by_logger.items()):
            stats_msg += f"   • {logger}: {count}\n"
        
        stats_msg += "\n📊 Par Level :\n"
        for level, count in sorted(by_level.items()):
            stats_msg += f"   • {level}: {count}\n"
        
        stats_msg += f"\n🎯 Actions :\n"
        stats_msg += f"   • Avec action: {with_action}\n"
        stats_msg += f"   • Sans action: {without_action}\n"
        if unique_actions:
            stats_msg += f"   • Actions trouvées: {', '.join(sorted(unique_actions))}\n"
        
        self.status_label.setText(f"✅ {total} logs trouvés")
        
        QMessageBox.information(
            self,
            "Scan terminé",
            stats_msg
        )
    
    def on_log_selected(self):
        """Un log a été sélectionné dans la table"""
        # Ne pas traiter si on est en train de mettre à jour
        if self._updating:
            return
        
        selected = self.table.selectedItems()
        if not selected:
            return
        
        # Récupérer le log
        row = selected[0].row()
        log = self.table.item(row, 0).data(Qt.UserRole)
        
        # Si c'est le même log, ne pas recharger (pour ne pas écraser les modifications en cours)
        if self.current_log == log:
            return
        
        self.current_log = log
        
        # Remplir l'éditeur
        self.file_label.setText(f"📁 {log.file_path}\n📍 Ligne {log.line_number}")
        self.logger_combo.setCurrentText(log.new_logger)
        self.level_display.setText(log.level)
        self.action_combo.setEditText(log.new_action)
        self.message_edit.setPlainText(log.new_message)
        self.original_code.setPlainText(log.full_line)
    
    def apply_changes(self):
        """Appliquer les modifications au log courant"""
        # Bloquer les mises à jour pour éviter que on_log_selected écrase les champs
        self._updating = True
        
        try:
            if not self.current_log:
                return
            
            # Récupérer les nouvelles valeurs
            new_logger = self.logger_combo.currentData()
            new_action = self.action_combo.currentText().strip()
            new_message = self.message_edit.toPlainText().strip()
            
            # Ajouter l'action à l'historique si elle n'existe pas et n'est pas vide
            if new_action and self.action_combo.findText(new_action) == -1:
                self.action_combo.addItem(new_action)
            
            # Vérifier si changé par rapport aux valeurs ORIGINALES
            if new_logger != self.current_log.logger_name or new_action != self.current_log.action or new_message != self.current_log.message:
                self.current_log.new_logger = new_logger
                self.current_log.new_action = new_action
                self.current_log.new_message = new_message
                self.current_log.modified = True
                
                # Mettre à jour la table
                self._refresh_table_row()
                self._update_stats()
                
                self.status_label.setText(f"✏️ Log modifié : {Path(self.current_log.file_path).name}:{self.current_log.line_number}")
            else:
                # Pas de changement par rapport à l'original
                self.current_log.new_logger = new_logger
                self.current_log.new_action = new_action
                self.current_log.new_message = new_message
                self.current_log.modified = False
                
                # Mettre à jour la table
                self._refresh_table_row()
                self._update_stats()
                
                self.status_label.setText("Aucune modification (identique à l'original)")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'application des modifications:\n{e}")
        finally:
            # Toujours débloquer
            self._updating = False
    
    def reset_changes(self):
        """Réinitialiser les modifications"""
        if not self.current_log:
            return
        
        self.current_log.new_logger = self.current_log.logger_name
        self.current_log.new_action = self.current_log.action
        self.current_log.new_message = self.current_log.message
        self.current_log.modified = False
        
        self.logger_combo.setCurrentText(self.current_log.logger_name)
        self.action_combo.setEditText(self.current_log.action)
        self.message_edit.setPlainText(self.current_log.message)
        
        self._refresh_table_row()
        self._update_stats()
        self.status_label.setText("↩️ Modifications annulées")
    
    def _refresh_table_row(self):
        """Rafraîchir la ligne de la table pour le log courant"""
        # Bloquer les signaux pendant la mise à jour pour éviter les boucles
        self.table.blockSignals(True)
        
        for row in range(self.table.rowCount()):
            log = self.table.item(row, 0).data(Qt.UserRole)
            if log == self.current_log:
                # Mettre à jour logger si changé
                logger_text = log.new_logger if log.new_logger else log.logger_name
                self.table.item(row, 2).setText(logger_text)
                
                # Mettre à jour action
                action_text = log.new_action if log.new_action else "-"
                self.table.item(row, 4).setText(action_text)
                
                # Mettre à jour message
                msg_preview = log.new_message[:60] + "..." if len(log.new_message) > 60 else log.new_message
                self.table.item(row, 5).setText(msg_preview)
                
                # Mettre à jour "Modifié"
                modified_item = self.table.item(row, 6)
                modified_item.setText("✓" if log.modified else "")
                modified_item.setForeground(QColor("#4CAF50") if log.modified else QColor("#000000"))
                break
        
        # Débloquer les signaux
        self.table.blockSignals(False)
    
    def apply_filter(self):
        """Appliquer les filtres à la table"""
        logger_filter = self.logger_filter.currentText()
        level_filter = self.level_filter.currentText()
        modified_filter = self.modified_filter.currentText()
        search_text = self.search_box.text().lower()
        
        visible_count = 0
        
        for row in range(self.table.rowCount()):
            log = self.table.item(row, 0).data(Qt.UserRole)
            
            # Filtre logger
            show = True
            if logger_filter != "Tous" and log.logger_name != logger_filter:
                show = False
            
            # Filtre level
            if level_filter != "Tous" and log.level != level_filter:
                show = False
            
            # Filtre modifié
            if modified_filter == "Modifiés uniquement" and not log.modified:
                show = False
            
            # Recherche dans message
            if search_text:
                if search_text not in log.message.lower() and search_text not in log.new_message.lower():
                    show = False
            
            self.table.setRowHidden(row, not show)
            if show:
                visible_count += 1
        
        # Mettre à jour les statistiques
        self._update_stats(visible_count)
    
    def _update_stats(self, visible_count=None):
        """Mettre à jour les statistiques affichées"""
        total = len(self.logs)
        modified = sum(1 for log in self.logs if log.modified)
        
        if visible_count is None:
            visible_count = total
        
        stats_text = f"📊 {visible_count}/{total} logs"
        if modified > 0:
            stats_text += f" | ✏️ {modified} modifié{'s' if modified > 1 else ''}"
        
        self.stats_label.setText(stats_text)
    
    def save_modifications(self):
        """Sauvegarder toutes les modifications dans les fichiers source"""
        modified_logs = [log for log in self.logs if log.modified]
        
        if not modified_logs:
            QMessageBox.information(self, "Aucune modification", "Aucun log n'a été modifié.")
            return
        
        # Afficher un aperçu des modifications
        preview = "📝 Aperçu des modifications :\n\n"
        file_groups = {}
        for log in modified_logs:
            if log.file_path not in file_groups:
                file_groups[log.file_path] = []
            file_groups[log.file_path].append(log)
        
        for file_path, logs in list(file_groups.items())[:5]:  # Montrer max 5 fichiers
            preview += f"📁 {Path(file_path).name}:\n"
            for log in logs[:3]:  # Max 3 logs par fichier
                preview += f"   Ligne {log.line_number}: {log.action or '-'} → {log.new_action or '-'}\n"
            if len(logs) > 3:
                preview += f"   ... et {len(logs)-3} autres\n"
            preview += "\n"
        
        if len(file_groups) > 5:
            preview += f"... et {len(file_groups)-5} autres fichiers\n\n"
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            "Confirmer la sauvegarde",
            f"{preview}"
            f"⚠️ Total: {len(modified_logs)} log(s) dans {len(file_groups)} fichier(s)\n\n"
            f"Cette opération va modifier vos fichiers Python.\n"
            f"Assurez-vous d'avoir un backup ou un commit git.\n\n"
            f"Voulez-vous continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Grouper par fichier
        files_to_modify = {}
        for log in modified_logs:
            if log.file_path not in files_to_modify:
                files_to_modify[log.file_path] = []
            files_to_modify[log.file_path].append(log)
        
        # Modifier chaque fichier
        success_count = 0
        error_files = []
        
        for file_path, logs in files_to_modify.items():
            try:
                # Lire le fichier
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Modifier les lignes (en ordre inverse pour ne pas décaler les numéros)
                for log in sorted(logs, key=lambda x: x.line_number, reverse=True):
                    line_idx = log.line_number - 1
                    if line_idx < len(lines):
                        # Construire la nouvelle ligne
                        new_line = self._build_new_log_line(log, lines[line_idx])
                        lines[line_idx] = new_line
                        success_count += 1
                
                # Écrire le fichier
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                    
            except Exception as e:
                error_files.append(f"{Path(file_path).name}: {str(e)}")
        
        # Message de résultat
        result_msg = f"✅ {success_count} log(s) modifié(s) dans {len(files_to_modify)} fichier(s) !"
        
        if error_files:
            result_msg += f"\n\n⚠️ Erreurs sur {len(error_files)} fichier(s):\n"
            result_msg += "\n".join(error_files[:5])
            if len(error_files) > 5:
                result_msg += f"\n... et {len(error_files)-5} autres"
        
        QMessageBox.information(
            self,
            "Sauvegarde terminée",
            result_msg
        )
        
        # Réinitialiser les flags "modified"
        for log in modified_logs:
            log.modified = False
            log.action = log.new_action
            log.message = log.new_message
            log.logger_name = log.new_logger
        
        # Rafraîchir la table
        for row in range(self.table.rowCount()):
            log = self.table.item(row, 0).data(Qt.UserRole)
            self.table.item(row, 6).setText("")
        
        self._update_stats()
        self.status_label.setText(f"💾 {success_count} logs sauvegardés")
    
    def _build_new_log_line(self, log: LogEntry, original_line: str) -> str:
        """Construire la nouvelle ligne de log avec préservation du format"""
        # Garder l'indentation exacte
        indent = len(original_line) - len(original_line.lstrip())
        indent_str = original_line[:indent]
        
        # Détecter le préfixe du logger (self., module_, etc.)
        logger_prefix = ""
        if "self.logger" in original_line:
            logger_prefix = "self."
        elif "module_logger" in original_line:
            logger_prefix = "module_"
        
        level_lower = log.level.lower()
        
        # Garder le format du message original (f-string, string normale, etc.)
        original_msg = original_line.strip()
        
        # Détecter si c'est une f-string
        is_fstring = re.search(r'logger\.\w+\s*\(\s*f["\']', original_line)
        
        # Construire le nouveau message
        if is_fstring:
            # Préserver la f-string
            new_msg = f'f"{log.new_message}"'
        else:
            # String normale - échapper les guillemets
            msg_escaped = log.new_message.replace('"', '\\"')
            new_msg = f'"{msg_escaped}"'
        
        # Vérifier si le logger a changé - utiliser log_with_action si action existe
        if log.new_action:
            # Format: log_with_action(logger, "level", message, action="ACTION")
            # Échapper les guillemets dans le message pour log_with_action
            msg_for_func = log.new_message.replace('"', '\\"')
            new_line = f'{indent_str}log_with_action({log.new_logger}, "{level_lower}", "{msg_for_func}", action="{log.new_action}")\n'
        else:
            # Format standard: logger.level(message) ou nouveau logger
            new_line = f'{indent_str}{logger_prefix}{log.new_logger}.{level_lower}({new_msg})\n'
        
        return new_line


def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    window = LogSourceEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
