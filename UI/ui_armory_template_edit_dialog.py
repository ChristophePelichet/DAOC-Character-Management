"""
Template Edit Dialog - Interface for editing template metadata information
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QComboBox, QMessageBox, QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager
from Functions.data_manager import DataManager


class TemplateEditDialog(QDialog):
    """
    Dialog for editing template metadata.
    Allows modification of: class, realm, season, description.
    Files are automatically moved to the correct folder.
    """

    def __init__(self, parent, template_name, realm, metadata):
        """
        Initialize dialog.

        Args:
            parent: Parent window
            template_name: Current template filename (without .txt)
            realm: Current realm
            metadata: Template metadata object
        """
        super().__init__(parent)

        self.template_name = template_name
        self.realm = realm
        self.metadata = metadata
        self.template_manager = TemplateManager()
        self.data_manager = DataManager()

        # Load available classes by realm
        self.classes_by_realm = self._load_classes_by_realm()

        window_title = lang.get(
            "template_edit.window_title",
            default="Editer le template - {name}"
        ).format(name=template_name)
        self.setWindowTitle(window_title)
        self.resize(500, 350)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self._setup_ui()
        self._load_current_values()
        self._connect_signals()

    def _load_classes_by_realm(self):
        """Load available classes for each realm"""
        classes_by_realm = {}
        try:
            data = self.data_manager.load_classes_races()

            for realm in ['Albion', 'Hibernia', 'Midgard']:
                if realm in data:
                    classes_by_realm[realm] = [
                        cls['name'] for cls in data[realm].get('classes', [])
                    ]
            return classes_by_realm
        except Exception as e:
            import logging
            logging.warning(f"Could not load classes by realm: {e}")
            return {
                'Albion': [],
                'Hibernia': [],
                'Midgard': []
            }

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Edit group
        info_group_title = lang.get(
            "template_edit.info_group_title",
            default="Informations du template"
        )
        edit_group = QGroupBox(info_group_title)
        edit_layout = QFormLayout()

        # Realm selector
        self.realm_combo = QComboBox()
        self.realm_combo.addItems(['Albion', 'Hibernia', 'Midgard'])
        edit_layout.addRow(
            lang.get("template_edit.realm_label", default="Royaume:"),
            self.realm_combo
        )

        # Class selector
        self.class_combo = QComboBox()
        edit_layout.addRow(
            lang.get("template_edit.class_label", default="Classe:"),
            self.class_combo
        )

        # Season selector
        self.season_combo = QComboBox()
        seasons = self.template_manager.get_available_seasons()
        self.season_combo.addItems(seasons)
        self.season_combo.addItem("Personnalisé...")
        edit_layout.addRow(
            lang.get("template_edit.season_label", default="Saison:"),
            self.season_combo
        )

        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setMaxLength(50)
        edit_layout.addRow(
            lang.get("template_edit.description_label", default="Description:"),
            self.description_edit
        )

        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)

        # Preview group
        preview_label = lang.get(
            "template_edit.preview_label",
            default="Aperçu du nouveau nom"
        )
        preview_group = QGroupBox(preview_label)
        preview_layout = QVBoxLayout()

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

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton(
            lang.get("template_edit.cancel_button", default="Annuler")
        )
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.save_button = QPushButton(
            lang.get("template_edit.save_button", default="Sauvegarder")
        )
        self.save_button.setMinimumWidth(120)
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "font-weight: bold; border-radius: 5px; } "
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.save_button.clicked.connect(self._save_changes)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _load_current_values(self):
        """Load current template values into controls"""
        # Set realm first
        self.realm_combo.setCurrentText(self.realm)

        # Populate classes for the current realm
        current_realm = self.realm_combo.currentText()
        if current_realm in self.classes_by_realm:
            self.class_combo.addItems(self.classes_by_realm[current_realm])

        # Set class to the template's class
        if self.metadata.character_class in self.classes_by_realm.get(self.realm, []):
            self.class_combo.setCurrentText(self.metadata.character_class)

        # Set season
        if self.metadata.season in self.template_manager.get_available_seasons():
            self.season_combo.setCurrentText(self.metadata.season)

        # Set description
        self.description_edit.setText(self.metadata.description or "")

        # Update preview
        self._update_preview()

    def _connect_signals(self):
        """Connect signals"""
        self.realm_combo.currentTextChanged.connect(self._on_realm_changed)
        self.class_combo.currentTextChanged.connect(self._update_preview)
        self.season_combo.currentTextChanged.connect(self._update_preview)
        self.description_edit.textChanged.connect(self._update_preview)

    def _on_realm_changed(self):
        """Update available classes when realm changes"""
        current_realm = self.realm_combo.currentText()
        self.class_combo.clear()

        if current_realm in self.classes_by_realm:
            self.class_combo.addItems(self.classes_by_realm[current_realm])

        self._update_preview()

    def _update_preview(self):
        """Update preview of new template name"""
        character_class = self.class_combo.currentText()
        season = self.season_combo.currentText()
        description = self.description_edit.text().strip()

        if not character_class or not description:
            warning_msg = lang.get(
                "template_edit.fill_all_fields",
                default="Please fill in all fields"
            )
            self.preview_name.setText(f"⚠️ {warning_msg}")
            return

        if season == "Personnalisé...":
            season_msg = lang.get(
                "template_edit.select_valid_season",
                default="Please select a valid season"
            )
            self.preview_name.setText(f"⚠️ {season_msg}")
            return

        # Generate preview
        new_name = self.template_manager.generate_template_name(
            character_class,
            season,
            description,
            include_season=True  # Always include season in editable template name
        )

        self.preview_name.setText(f"✓ {new_name}")

    def _save_changes(self):
        """Save changes and move files if necessary"""
        new_class = self.class_combo.currentText()
        new_realm = self.realm_combo.currentText()
        new_season = self.season_combo.currentText()
        new_description = self.description_edit.text().strip()

        if not new_class or not new_description or new_season == "Personnalisé...":
            QMessageBox.warning(
                self,
                lang.get("template_edit.error_title", default="Erreur"),
                lang.get(
                    "template_edit.invalid_fields",
                    default="Veuillez remplir tous les champs correctement"
                )
            )
            return

        try:
            # Generate new template name
            new_template_name = self.template_manager.generate_template_name(
                new_class,
                new_season,
                new_description,
                include_season=True
            )

            # Get file paths
            old_template_path = self.template_manager._get_template_path(
                self.realm, self.template_name
            )
            old_metadata_path = self.template_manager._get_metadata_path(
                self.realm, self.template_name
            )

            new_template_path = self.template_manager._get_template_path(
                new_realm, new_template_name
            )
            new_metadata_path = self.template_manager._get_metadata_path(
                new_realm, new_template_name
            )

            # Check if new name already exists
            if new_template_path.exists():
                QMessageBox.warning(
                    self,
                    lang.get("template_edit.error_title", default="Erreur"),
                    lang.get(
                        "template_edit.duplicate_error",
                        default="Un template avec ce nom existe déjà"
                    )
                )
                return

            # Move template file
            if old_template_path.exists():
                old_template_path.rename(new_template_path)

            # Move metadata file
            if old_metadata_path.exists():
                old_metadata_path.rename(new_metadata_path)

            # Update metadata
            self.metadata.character_class = new_class

            # Get class info to update translations
            class_info = self.data_manager.get_class_info(new_realm, new_class)
            if class_info:
                self.metadata.class_fr = class_info.get('name_fr', new_class)
                self.metadata.class_de = class_info.get('name_de', new_class)

            self.metadata.realm = new_realm
            self.metadata.season = new_season
            self.metadata.description = new_description
            self.metadata.template_name = new_template_name

            # Save updated metadata
            if self.metadata.save_to_path(new_metadata_path):
                # Update template manager index
                self.template_manager.update_index()

                QMessageBox.information(
                    self,
                    lang.get("template_edit.success_title", default="Succès"),
                    lang.get(
                        "template_edit.success_message",
                        default="Template modifié avec succès"
                    )
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    lang.get("template_edit.error_title", default="Erreur"),
                    lang.get(
                        "template_edit.save_error",
                        default="Impossible de sauvegarder les métadonnées"
                    )
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                lang.get("template_edit.error_title", default="Erreur"),
                lang.get(
                    "template_edit.error_message",
                    default="Erreur lors de la modification:\n{error}"
                ).format(error=str(e))
            )
