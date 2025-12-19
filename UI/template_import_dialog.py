"""
Template Import Dialog - Interface pour importer des templates d'armurerie
Version refactorisée avec contexte de personnage
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QLineEdit, QComboBox, QMessageBox,
    QFormLayout
)
from PySide6.QtCore import Qt, Signal

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager
from UI.ui_file_dialogs import dialog_open_template_file
from UI.widgets.tag_selector import TagSelector


class TemplateImportDialog(QDialog):
    """
    Dialogue pour importer un template d'armurerie depuis la fiche d'un personnage.
    Le contexte (classe, realm) est automatiquement détecté depuis le personnage.
    """
    
    template_imported = Signal(str)  # template_name
    
    def __init__(self, parent, character):
        """
        Initialize dialog with character context.
        
        Args:
            parent: Parent window
            character: Character dict with class, realm, name, etc.
        """
        super().__init__(parent)
        
        self.character = character
        self.template_manager = TemplateManager()
        self.selected_file = None
        
        # Extract character info
        self.character_class = character.get('character_class', '')
        self.character_class_fr = character.get('class_fr', self.character_class)
        self.character_class_de = character.get('class_de', self.character_class)
        self.realm = character.get('realm', 'Albion')
        self.character_name = character.get('name', 'Unknown')
        
        self.setWindowTitle(lang.get("template_import.window_title", default="Importer un template"))
        self.resize(600, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self._setup_ui()
        self._connect_signals()
        self._update_preview()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # === File Selection Group ===
        file_group = QGroupBox(lang.get("template_import.file_group_title", default="📂 Fichier source"))
        file_layout = QVBoxLayout()
        
        # File selection row
        file_row = QHBoxLayout()
        self.file_label = QLabel(lang.get("template_import.no_file_selected", default="Aucun fichier sélectionné"))
        # Use default text color from palette (adapts to theme)
        self.file_label.setStyleSheet("")
        file_row.addWidget(self.file_label, 1)
        
        self.browse_button = QPushButton(lang.get("template_import.browse_button", default="📁 Parcourir..."))
        self.browse_button.setMinimumWidth(120)
        file_row.addWidget(self.browse_button)
        
        file_layout.addLayout(file_row)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # === Context Group (read-only, grayed out) ===
        context_group = QGroupBox(lang.get("template_import.context_group_title", default="🎯 Contexte (auto-détecté)"))
        context_layout = QFormLayout()
        
        # Class (read-only)
        self.class_label = QLabel(f"<b>{self.character_class}</b>")
        # Use theme colors with slight transparency for read-only effect
        self.class_label.setStyleSheet("padding: 5px; border-radius: 3px; opacity: 0.7;")
        context_layout.addRow(
            lang.get("template_import.class_label", default="Classe:"),
            self.class_label
        )
        
        # Realm (read-only)
        self.realm_label = QLabel(f"<b>{self.realm}</b>")
        # Use theme colors with slight transparency for read-only effect
        self.realm_label.setStyleSheet("padding: 5px; border-radius: 3px; opacity: 0.7;")
        context_layout.addRow(
            lang.get("template_import.realm_label", default="Royaume:"),
            self.realm_label
        )
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # === Information Group (user input) ===
        info_group = QGroupBox(lang.get("template_import.info_group_title", default="📝 Informations"))
        info_layout = QFormLayout()
        
        # Season selector (dropdown)
        self.season_combo = QComboBox()
        seasons = self.template_manager.get_available_seasons()
        current_season = self.template_manager.get_current_season()
        
        self.season_combo.addItems(seasons)
        # Add custom option
        self.season_combo.addItem("Personnalisé...")
        
        # Select current season
        if current_season in seasons:
            self.season_combo.setCurrentText(current_season)
        
        info_layout.addRow(
            lang.get("template_import.season_label", default="Saison:"),
            self.season_combo
        )
        
        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText(
            lang.get("template_import.description_placeholder", default="Ex: low cost sans ml10")
        )
        self.description_edit.setMaxLength(50)
        info_layout.addRow(
            lang.get("template_import.description_label", default="Description:"),
            self.description_edit
        )
        
        # Tags selector
        self.tag_selector = TagSelector(self)
        info_layout.addRow(
            lang.get("template_import.tags_label", default="Tags (optionnel):"),
            self.tag_selector
        )
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # === Preview Group ===
        preview_group = QGroupBox("📄 Aperçu")
        preview_layout = QVBoxLayout()
        
        preview_label = QLabel(lang.get("template_import.preview_label", default="Nom du fichier:"))
        preview_layout.addWidget(preview_label)
        
        self.preview_name = QLabel("")
        self.preview_name.setStyleSheet(
            "font-family: monospace; "
            "background: #f0f0f0; "
            "padding: 8px; "
            "border-radius: 3px; "
            "color: #333; "
            "font-weight: bold;"
        )
        self.preview_name.setWordWrap(True)
        preview_layout.addWidget(self.preview_name)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton(lang.get("template_import.cancel_button", default="Annuler"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.import_button = QPushButton(lang.get("template_import.import_button", default="📥 Importer"))
        self.import_button.setMinimumWidth(120)
        self.import_button.setMinimumHeight(35)
        self.import_button.setEnabled(False)
        self.import_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:hover { background-color: #45a049; }"
            "QPushButton:disabled { background-color: #cccccc; color: #666666; }"
        )
        button_layout.addWidget(self.import_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals"""
        self.browse_button.clicked.connect(self._browse_file)
        self.import_button.clicked.connect(self._import_template)
        self.description_edit.textChanged.connect(self._update_preview)
        self.season_combo.currentTextChanged.connect(self._update_preview)
    
    def _browse_file(self):
        """Browse for template file"""
        file_path = dialog_open_template_file(self)
        
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.setText(self.selected_file.name)
            # Use font-weight only, let theme define text color
            self.file_label.setStyleSheet("font-weight: bold;")
            self._update_preview()
    
    def _update_preview(self):
        """Update template name preview"""
        description = self.description_edit.text().strip()
        season = self.season_combo.currentText()
        
        # Enable import button only if file and description are set
        can_import = bool(self.selected_file is not None and description and season != "Personnalisé...")
        self.import_button.setEnabled(can_import)
        
        if not description:
            self.preview_name.setText("⚠️ Veuillez saisir une description")
            return
        
        if season == "Personnalisé...":
            self.preview_name.setText("⚠️ Veuillez sélectionner une saison")
            return
        
        # Generate preview name
        template_name = self.template_manager.generate_template_name(
            self.character_class,
            season,
            description
        )
        
        self.preview_name.setText(f"✓ {template_name}")
    
    def _import_template(self):
        """Import template with metadata"""
        if not self.selected_file or not self.selected_file.exists():
            QMessageBox.warning(
                self,
                lang.get("template_import.import_error_title", default="Erreur d'import"),
                "Fichier source invalide"
            )
            return
        
        description = self.description_edit.text().strip()
        season = self.season_combo.currentText()
        tags = self.tag_selector.get_tags()
        
        if not description:
            QMessageBox.warning(
                self,
                lang.get("template_import.import_error_title", default="Erreur d'import"),
                "Veuillez saisir une description"
            )
            return
        
        # Create template
        try:
            template_name = self.template_manager.create_template(
                source_file=self.selected_file,
                character_class=self.character_class,
                class_fr=self.character_class_fr,
                class_de=self.character_class_de,
                realm=self.realm,
                season=season,
                description=description,
                character_name=self.character_name,
                tags=tags,
                notes=""
            )
            
            if template_name:
                QMessageBox.information(
                    self,
                    lang.get("template_import.import_success_title", default="Import réussi"),
                    lang.get("template_import.import_success_message", default="Template '{name}' importé avec succès").format(
                        name=template_name
                    )
                )
                self.template_imported.emit(template_name)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    lang.get("template_import.import_error_title", default="Erreur d'import"),
                    lang.get("template_import.duplicate_error", default="Un template avec ce nom existe déjà")
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                lang.get("template_import.import_error_title", default="Erreur d'import"),
                lang.get("template_import.import_error_message", default="Impossible d'importer le template:\n{error}").format(
                    error=str(e)
                )
            )
