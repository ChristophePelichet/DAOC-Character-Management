"""
Template Preview Dialog - Affiche un aperçu détaillé d'un template
"""

from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QFormLayout, QSplitter, QWidget
)
from PySide6.QtCore import Qt

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager


class TemplatePreviewDialog(QDialog):
    """
    Dialogue pour prévisualiser un template avant de le charger.
    Affiche métadonnées, liste d'items et statistiques.
    """
    
    def __init__(self, parent, template_name, metadata):
        super().__init__(parent)
        
        self.template_name = template_name
        self.metadata = metadata
        self.template_manager = TemplateManager()
        
        self.setWindowTitle(
            lang.get("template_preview.window_title", default="Aperçu du template - {name}").format(
                name=template_name
            )
        )
        self.resize(700, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self._setup_ui()
        self._load_template_content()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Splitter for metadata and items
        splitter = QSplitter(Qt.Vertical)
        
        # === Metadata Group ===
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        
        metadata_group = QGroupBox(lang.get("template_preview.metadata_group", default="📋 Informations"))
        metadata_form = QFormLayout()
        
        # Class
        metadata_form.addRow(
            lang.get("template_preview.label_class", default="Classe:"),
            QLabel(f"<b>{self.metadata.character_class}</b> ({self.metadata.class_fr} / {self.metadata.class_de})")
        )
        
        # Realm
        metadata_form.addRow(
            lang.get("template_preview.label_realm", default="Royaume:"),
            QLabel(f"<b>{self.metadata.realm}</b>")
        )
        
        # Season
        metadata_form.addRow(
            lang.get("template_preview.label_season", default="Saison:"),
            QLabel(f"<b>{self.metadata.season}</b>")
        )
        
        # Description
        metadata_form.addRow(
            lang.get("template_preview.label_description", default="Description:"),
            QLabel(self.metadata.description)
        )
        
        # Tags
        if self.metadata.tags:
            tags_str = " • ".join([f"<span style='background:#2196F3; color:white; padding:2px 6px; border-radius:8px; font-size:10px;'>{tag}</span>" for tag in self.metadata.tags])
            tags_label = QLabel(tags_str)
            tags_label.setTextFormat(Qt.RichText)
            metadata_form.addRow(
                lang.get("template_preview.label_tags", default="Tags:"),
                tags_label
            )
        
        # Source file
        metadata_form.addRow(
            lang.get("template_preview.label_source", default="Fichier source:"),
            QLabel(f"<i>{self.metadata.source_file}</i>")
        )
        
        # Imported by
        metadata_form.addRow(
            lang.get("template_preview.label_imported_by", default="Importé par:"),
            QLabel(self.metadata.imported_by_character)
        )
        
        # Import date
        import_date = datetime.fromisoformat(self.metadata.import_date).strftime("%d/%m/%Y %H:%M")
        metadata_form.addRow(
            lang.get("template_preview.label_import_date", default="Date d'import:"),
            QLabel(import_date)
        )
        
        # Notes
        if self.metadata.notes:
            notes_label = QLabel(self.metadata.notes)
            notes_label.setWordWrap(True)
            metadata_form.addRow(
                lang.get("template_preview.label_notes", default="Notes:"),
                notes_label
            )
        
        metadata_group.setLayout(metadata_form)
        metadata_layout.addWidget(metadata_group)
        
        # === Stats Group ===
        stats_group = QGroupBox(lang.get("template_preview.stats_group", default="📊 Statistiques"))
        stats_form = QFormLayout()
        
        stats_form.addRow(
            lang.get("template_preview.stats_total_items", default="Total items:"),
            QLabel(f"<b>{self.metadata.item_count}</b>")
        )
        
        # TODO: Add slots covered count when template content is parsed
        
        stats_group.setLayout(stats_form)
        metadata_layout.addWidget(stats_group)
        
        splitter.addWidget(metadata_widget)
        
        # === Items List Group ===
        items_group = QGroupBox(
            lang.get("template_preview.items_group", default="📦 Items ({count})").format(
                count=self.metadata.item_count
            )
        )
        items_layout = QVBoxLayout()
        
        self.items_text = QTextEdit()
        self.items_text.setReadOnly(True)
        self.items_text.setStyleSheet(
            "font-family: monospace; "
            "font-size: 11px; "
            "background-color: white; "
            "color: #333;"
        )
        items_layout.addWidget(self.items_text)
        
        items_group.setLayout(items_layout)
        splitter.addWidget(items_group)
        
        layout.addWidget(splitter)
        
        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton(lang.get("template_preview.button_close", default="Fermer"))
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)
        
        load_button = QPushButton(lang.get("template_preview.button_load", default="📥 Charger ce template"))
        load_button.setMinimumWidth(150)
        load_button.setMinimumHeight(35)
        load_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        load_button.clicked.connect(self.accept)
        button_layout.addWidget(load_button)
        
        layout.addLayout(button_layout)
    
    def _load_template_content(self):
        """Load and display template file content"""
        try:
            template_file = self.template_manager.armory_path / self.template_name
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Display items (one per line)
                items = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Format with numbers
                formatted = "\n".join([f"{i+1:3}. {item}" for i, item in enumerate(items)])
                self.items_text.setText(formatted)
            else:
                self.items_text.setText("⚠️ Fichier template introuvable")
        
        except Exception as e:
            self.items_text.setText(f"❌ Erreur de lecture: {e}")
