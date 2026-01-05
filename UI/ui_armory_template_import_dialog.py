"""
Template Import Dialog - Interface for importing armory templates
Refactored version with character context
"""

from pathlib import Path
from UI.ui_sound_manager import SilentMessageBox
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QLineEdit, QComboBox, QMessageBox,
    QFormLayout, QCheckBox
)
from PySide6.QtCore import Qt, Signal

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager
from UI.ui_file_dialogs import dialog_open_template_file
from UI.ui_armory_template_tag_selector import ArmoryTagSelector


class TemplateImportDialog(QDialog):
    """
    Dialog for importing an armory template.
    Can operate in two modes:
    - Character mode: auto-detects class and realm
    - Armory mode (generic): displays dropdowns to select class and realm
    """

    template_imported = Signal(str)  # template_name

    def __init__(self, parent, character, auto_detect_mode=True):
        """
        Initialize dialog with character context.

        Args:
            parent: Parent window
            character: Character dict with class, realm, name, etc.
            auto_detect_mode: If True, auto-detect class/realm from character
                            If False, show dropdowns for manual selection
        """
        super().__init__(parent)

        self.character = character
        self.template_manager = TemplateManager()
        self.selected_file = None
        self.auto_detect_mode = auto_detect_mode

        # Extract character info
        self.character_class = character.get('character_class', '')
        self.character_class_fr = character.get('class_fr', self.character_class)
        self.character_class_de = character.get('class_de', self.character_class)
        self.realm = character.get('realm', 'Albion')
        self.character_name = character.get('name', 'Unknown')

        # Load available classes by realm (for non-auto-detect mode)
        self.classes_by_realm = self._load_classes_by_realm()

        window_title = lang.get(
            "template_import.window_title",
            default="Importer un template"
        )
        self.setWindowTitle(window_title)
        self.resize(600, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self._setup_ui()
        self._connect_signals()
        self._update_preview()

    def _load_classes_by_realm(self):
        """Load available classes for each realm from data file"""
        classes_by_realm = {}
        try:
            from Functions.data_manager import DataManager
            dm = DataManager()
            data = dm.load_classes_races()

            for realm in ['Albion', 'Hibernia', 'Midgard']:
                if realm in data:
                    classes_by_realm[realm] = [
                        cls['name'] for cls in data[realm].get('classes', [])
                    ]
            return classes_by_realm
        except Exception as e:
            import logging
            logging.warning(f"Could not load classes by realm: {e}")
            # Fallback
            return {
                'Albion': [],
                'Hibernia': [],
                'Midgard': []
            }

    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)

        # === File Selection Group ===
        file_group_title = lang.get(
            "template_import.file_group_title",
            default="📂 Fichier source"
        )
        file_group = QGroupBox(file_group_title)
        file_layout = QVBoxLayout()

        # File selection row
        file_row = QHBoxLayout()
        self.file_label = QLabel(
            lang.get(
                "template_import.no_file_selected",
                default="Aucun fichier sélectionné"
            )
        )
        # Use default text color from palette (adapts to theme)
        self.file_label.setStyleSheet("")
        file_row.addWidget(self.file_label, 1)

        self.browse_button = QPushButton(
            lang.get(
                "template_import.browse_button",
                default="📁 Parcourir..."
            )
        )
        self.browse_button.setMinimumWidth(120)
        file_row.addWidget(self.browse_button)

        file_layout.addLayout(file_row)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # === Context Group (read-only, grayed out) ===
        context_group_title = lang.get(
            "template_import.context_group_title",
            default="🎯 Contexte (auto-détecté)"
        )
        context_group = QGroupBox(context_group_title)
        context_layout = QFormLayout()

        # Realm (read-only or dropdown) - FIRST
        if self.auto_detect_mode:
            # Mode auto-detect: affiche juste le realm en lecture seule
            self.realm_label = QLabel(f"<b>{self.realm}</b>")
            self.realm_label.setStyleSheet(
                "padding: 5px; border-radius: 3px; opacity: 0.7;"
            )
            context_layout.addRow(
                lang.get("template_import.realm_label", default="Royaume:"),
                self.realm_label
            )
            self.realm_combo = None
        else:
            # Mode sélection manuelle: affiche un dropdown pour le realm
            self.realm_combo = QComboBox()
            self.realm_combo.addItems(['Albion', 'Hibernia', 'Midgard'])
            self.realm_combo.setCurrentText(self.realm)
            context_layout.addRow(
                lang.get("template_import.realm_label", default="Royaume:"),
                self.realm_combo
            )
            self.realm_label = None

        # Class (read-only or dropdown) - SECOND
        if self.auto_detect_mode:
            # Mode auto-detect: affiche juste la classe en lecture seule
            self.class_label = QLabel(f"<b>{self.character_class}</b>")
            self.class_label.setStyleSheet(
                "padding: 5px; border-radius: 3px; opacity: 0.7;"
            )
            context_layout.addRow(
                lang.get("template_import.class_label", default="Classe:"),
                self.class_label
            )
            self.class_combo = None
        else:
            # Mode sélection manuelle: affiche un dropdown pour la classe
            self.class_combo = QComboBox()
            self.class_combo.addItem("")  # Empty option
            # Will be populated when realm is selected
            context_layout.addRow(
                lang.get("template_import.class_label", default="Classe:"),
                self.class_combo
            )
            self.class_label = None

        context_group.setLayout(context_layout)
        layout.addWidget(context_group)

        # === Information Group (user input) ===
        info_group_title = lang.get(
            "template_import.info_group_title",
            default="📝 Informations"
        )
        info_group = QGroupBox(info_group_title)
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

        # Season row with combo and checkbox
        season_row = QHBoxLayout()
        season_row.addWidget(self.season_combo)

        # Add checkbox to include season in filename (default: unchecked)
        self.include_season_check = QCheckBox(
            lang.get(
                "template_import.include_season_in_name",
                default="Inclure la saison dans le nom"
            )
        )
        self.include_season_check.setChecked(False)  # Default: don't include season
        season_row.addWidget(self.include_season_check)
        season_row.addStretch()

        info_layout.addRow(
            lang.get("template_import.season_label", default="Saison:"),
            season_row
        )

        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText(
            lang.get(
                "template_import.description_placeholder",
                default="Ex: low cost sans ml10"
            )
        )
        self.description_edit.setMaxLength(50)
        info_layout.addRow(
            lang.get("template_import.description_label", default="Description:"),
            self.description_edit
        )

        # Tags selector
        self.tag_selector = ArmoryTagSelector(self)
        info_layout.addRow(
            lang.get("template_import.tags_label", default="Tags (optionnel):"),
            self.tag_selector
        )

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # === Preview Group ===
        preview_group = QGroupBox("📄 Aperçu")
        preview_layout = QVBoxLayout()

        preview_label = QLabel(
            lang.get(
                "template_import.preview_label",
                default="Nom du fichier:"
            )
        )
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

        cancel_button = QPushButton(
            lang.get("template_import.cancel_button", default="Annuler")
        )
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.import_button = QPushButton(
            lang.get(
                "template_import.import_button",
                default="📥 Importer"
            )
        )
        self.import_button.setMinimumWidth(120)
        self.import_button.setMinimumHeight(35)
        self.import_button.setEnabled(False)
        self.import_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "font-weight: bold; border-radius: 5px; } "
            "QPushButton:hover { background-color: #45a049; } "
            "QPushButton:disabled { background-color: #cccccc; "
            "color: #666666; }"
        )
        button_layout.addWidget(self.import_button)

        layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect signals"""
        self.browse_button.clicked.connect(self._browse_file)
        self.import_button.clicked.connect(self._import_template)
        self.description_edit.textChanged.connect(self._update_preview)
        self.season_combo.currentTextChanged.connect(self._update_preview)
        self.include_season_check.stateChanged.connect(self._update_preview)

        # In non-auto-detect mode, connect realm change to update available classes
        if not self.auto_detect_mode and self.realm_combo:
            self.realm_combo.currentTextChanged.connect(self._on_realm_changed)
            # Populate initial classes for current realm
            self._on_realm_changed()

    def _on_realm_changed(self):
        """Update available classes when realm changes"""
        if not self.class_combo or not self.realm_combo:
            return

        current_realm = self.realm_combo.currentText()
        self.class_combo.clear()
        self.class_combo.addItem("")  # Empty option

        if current_realm in self.classes_by_realm:
            self.class_combo.addItems(self.classes_by_realm[current_realm])

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
        include_season = self.include_season_check.isChecked()

        # Enable import button only if file and description are set
        can_import = bool(
            self.selected_file is not None and description
            and season != "Personnalisé..."
        )
        self.import_button.setEnabled(can_import)

        if not description:
            self.preview_name.setText(
                f"⚠️ {lang.get(
                    'template_import.enter_description',
                    default='Veuillez saisir une description'
                )}"
            )
            return

        if season == "Personnalisé...":
            self.preview_name.setText(
                f"⚠️ {lang.get(
                    'template_import.select_season',
                    default='Veuillez sélectionner une saison'
                )}"
            )
            return

        # Generate preview name with include_season parameter
        template_name = self.template_manager.generate_template_name(
            self.character_class,
            season,
            description,
            include_season=include_season
        )

        self.preview_name.setText(f"✓ {template_name}")

    def _import_template(self):
        """Import template with metadata"""
        if not self.selected_file or not self.selected_file.exists():
            SilentMessageBox.warning(
                self,
                lang.get(
                    "template_import.import_error_title",
                    default="Erreur d'import"
                ),
                lang.get(
                    "template_import.invalid_source_file",
                    default="Fichier source invalide"
                )
            )
            return

        # In non-auto-detect mode, check that class and realm are selected
        if not self.auto_detect_mode:
            if not self.class_combo.currentText():
                SilentMessageBox.warning(
                    self,
                    lang.get(
                        "template_import.import_error_title",
                        default="Erreur d'import"
                    ),
                    lang.get(
                        "template_import.select_class",
                        default="Veuillez sélectionner une classe"
                    )
                )
                return

            if not self.realm_combo.currentText():
                SilentMessageBox.warning(
                    self,
                    lang.get(
                        "template_import.import_error_title",
                        default="Erreur d'import"
                    ),
                    lang.get(
                        "template_import.select_realm",
                        default="Veuillez sélectionner un royaume"
                    )
                )
                return

            # Update character class and realm from dropdowns
            self.character_class = self.class_combo.currentText()
            self.realm = self.realm_combo.currentText()
            # For non-character imports, use the English class name for all languages
            self.character_class_fr = self.character_class
            self.character_class_de = self.character_class

        description = self.description_edit.text().strip()
        season = self.season_combo.currentText()
        include_season = self.include_season_check.isChecked()
        tags = self.tag_selector.get_tags()

        if not description:
            SilentMessageBox.warning(
                self,
                lang.get(
                    "template_import.import_error_title",
                    default="Erreur d'import"
                ),
                lang.get(
                    "template_import.enter_description",
                    default="Veuillez saisir une description"
                )
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
                notes="",
                include_season=include_season
            )

            if template_name:
                SilentMessageBox.information(
                    self,
                    lang.get(
                        "template_import.import_success_title",
                        default="Import réussi"
                    ),
                    lang.get(
                        "template_import.import_success_message",
                        default="Template '{name}' importé avec succès"
                    ).format(name=template_name)
                )
                self.template_imported.emit(template_name)
                self.accept()
            else:
                SilentMessageBox.warning(
                    self,
                    lang.get(
                        "template_import.import_error_title",
                        default="Erreur d'import"
                    ),
                    lang.get(
                        "template_import.duplicate_error",
                        default="Un template avec ce nom existe déjà"
                    )
                )

        except Exception as e:
            SilentMessageBox.critical(
                self,
                lang.get(
                    "template_import.import_error_title",
                    default="Erreur d'import"
                ),
                lang.get(
                    "template_import.import_error_message",
                    default="Impossible d'importer le template:\n{error}"
                ).format(error=str(e))
            )
