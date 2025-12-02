"""
Template List Widget - Affiche et gère les templates disponibles pour une classe
"""

from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QScrollArea, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from Functions.language_manager import lang
from Functions.template_manager import TemplateManager
from UI.dialog_templates.template_preview_dialog import TemplatePreviewDialog


class TemplateCard(QFrame):
    """Card widget pour afficher un template"""
    
    preview_clicked = Signal(str)  # template_name
    load_clicked = Signal(str)     # template_name
    delete_clicked = Signal(str)   # template_name
    
    def __init__(self, template_file, metadata, parent=None):
        super().__init__(parent)
        
        self.template_file = template_file
        self.metadata = metadata
        
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
        self.setStyleSheet(
            "QFrame { "
            "background-color: white; "
            "border: 1px solid #ddd; "
            "border-radius: 5px; "
            "padding: 10px; "
            "margin: 5px; "
            "}"
            "QFrame:hover { "
            "border-color: #2196F3; "
            "background-color: #f8f9fa; "
            "}"
        )
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface de la card"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header: Template name
        name_label = QLabel(f"<b>{self.template_file}</b>")
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(name_label)
        
        # Season and tags
        meta_text = f"🎮 {self.metadata.season}"
        if self.metadata.tags:
            tags_str = " • ".join(self.metadata.tags[:3])
            meta_text += f" • 🏷️ {tags_str}"
        
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(meta_label)
        
        # Description
        desc_label = QLabel(self.metadata.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        layout.addWidget(desc_label)
        
        # Stats
        import_date = datetime.fromisoformat(self.metadata.import_date).strftime("%d/%m/%Y")
        stats_text = lang.get("template_list.info_items", default="{count} items").format(
            count=self.metadata.item_count
        )
        stats_text += " • " + lang.get("template_list.info_imported", default="Importé le {date}").format(
            date=import_date
        )
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 10px; color: #999;")
        layout.addWidget(stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        preview_btn = QPushButton(lang.get("template_list.button_preview", default="👁️ Aperçu"))
        preview_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; border-radius: 3px; padding: 5px 10px; font-size: 11px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        preview_btn.clicked.connect(lambda: self.preview_clicked.emit(self.template_file))
        button_layout.addWidget(preview_btn)
        
        load_btn = QPushButton(lang.get("template_list.button_load", default="📥 Charger"))
        load_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 3px; padding: 5px 10px; font-size: 11px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        load_btn.clicked.connect(lambda: self.load_clicked.emit(self.template_file))
        button_layout.addWidget(load_btn)
        
        delete_btn = QPushButton(lang.get("template_list.button_delete", default="🗑️ Supprimer"))
        delete_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; border-radius: 3px; padding: 5px 10px; font-size: 11px; }"
            "QPushButton:hover { background-color: #da190b; }"
        )
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.template_file))
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)


class TemplateListWidget(QWidget):
    """
    Widget pour afficher et gérer les templates disponibles pour une classe.
    Inclut recherche, filtrage et tri.
    """
    
    template_loaded = Signal(str)  # template_name
    
    def __init__(self, parent, character_class):
        super().__init__(parent)
        
        self.character_class = character_class
        self.template_manager = TemplateManager()
        self.templates = []
        
        self._setup_ui()
        self._connect_signals()
        self.load_templates()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Header
        header_label = QLabel(lang.get("template_list.title", default="Templates disponibles"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        layout.addWidget(header_label)
        
        # Filters row
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            lang.get("template_list.search_placeholder", default="Rechercher...")
        )
        filters_layout.addWidget(self.search_input, 2)
        
        # Season filter
        filters_layout.addWidget(QLabel(lang.get("template_list.filter_season_label", default="Saison:")))
        self.season_filter = QComboBox()
        self.season_filter.addItem(lang.get("template_list.filter_season_all", default="Toutes"))
        seasons = self.template_manager.get_available_seasons()
        self.season_filter.addItems(seasons)
        filters_layout.addWidget(self.season_filter, 1)
        
        # Sort
        filters_layout.addWidget(QLabel(lang.get("template_list.sort_label", default="Trier par:")))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            lang.get("template_list.sort_date", default="Date (récent)"),
            lang.get("template_list.sort_name", default="Nom (A-Z)"),
            lang.get("template_list.sort_items", default="Nombre d'items")
        ])
        filters_layout.addWidget(self.sort_combo, 1)
        
        layout.addLayout(filters_layout)
        
        # Templates scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.templates_container = QWidget()
        self.templates_layout = QVBoxLayout(self.templates_container)
        self.templates_layout.setSpacing(5)
        self.templates_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.templates_container)
        layout.addWidget(scroll)
        
        # No templates label
        self.no_templates_label = QLabel(
            lang.get("template_list.no_templates", default="Aucun template trouvé pour cette classe")
        )
        self.no_templates_label.setAlignment(Qt.AlignCenter)
        self.no_templates_label.setStyleSheet("color: #999; font-size: 12px; padding: 20px;")
        self.no_templates_label.hide()
        self.templates_layout.addWidget(self.no_templates_label)
    
    def _connect_signals(self):
        """Connect signals"""
        self.search_input.textChanged.connect(self._filter_templates)
        self.season_filter.currentTextChanged.connect(self._filter_templates)
        self.sort_combo.currentIndexChanged.connect(self._filter_templates)
    
    def load_templates(self):
        """Load templates for the character class"""
        self.templates = self.template_manager.get_templates_for_class(self.character_class)
        self._display_templates(self.templates)
    
    def _display_templates(self, templates):
        """Display templates in the list"""
        # Clear existing cards
        for i in reversed(range(self.templates_layout.count())):
            widget = self.templates_layout.itemAt(i).widget()
            if widget and widget != self.no_templates_label:
                widget.deleteLater()
        
        if not templates:
            self.no_templates_label.show()
            return
        
        self.no_templates_label.hide()
        
        # Create cards
        for template_data in templates:
            card = TemplateCard(
                template_data["file"],
                template_data["metadata"],
                self
            )
            card.preview_clicked.connect(self._show_preview)
            card.load_clicked.connect(self._load_template)
            card.delete_clicked.connect(self._delete_template)
            
            self.templates_layout.addWidget(card)
    
    def _filter_templates(self):
        """Filter and sort templates"""
        search_text = self.search_input.text().lower()
        season_filter = self.season_filter.currentText()
        sort_index = self.sort_combo.currentIndex()
        
        # Filter
        filtered = self.templates.copy()
        
        # Filter by search
        if search_text:
            filtered = [
                t for t in filtered
                if search_text in t["file"].lower() or search_text in t["metadata"].description.lower()
            ]
        
        # Filter by season
        if season_filter != lang.get("template_list.filter_season_all", default="Toutes"):
            filtered = [t for t in filtered if t["metadata"].season == season_filter]
        
        # Sort
        if sort_index == 0:  # Date (recent)
            filtered.sort(key=lambda t: t["metadata"].import_date, reverse=True)
        elif sort_index == 1:  # Name (A-Z)
            filtered.sort(key=lambda t: t["file"])
        elif sort_index == 2:  # Item count
            filtered.sort(key=lambda t: t["metadata"].item_count, reverse=True)
        
        self._display_templates(filtered)
    
    def _show_preview(self, template_name):
        """Show template preview dialog"""
        # Find template metadata
        template_data = next((t for t in self.templates if t["file"] == template_name), None)
        if not template_data:
            return
        
        # Open preview dialog
        dialog = TemplatePreviewDialog(self, template_name, template_data["metadata"])
        if dialog.exec():
            # User clicked "Load" in preview
            self._load_template(template_name)
    
    def _load_template(self, template_name):
        """Load template into character"""
        # TODO: Implement template loading logic
        QMessageBox.information(
            self,
            lang.get("template_list.load_success", default="Template chargé"),
            f"Chargement du template: {template_name}\n\n(À implémenter: chargement des items)"
        )
        self.template_loaded.emit(template_name)
    
    def _delete_template(self, template_name):
        """Delete a template"""
        # Confirm
        reply = QMessageBox.question(
            self,
            lang.get("template_list.delete_confirm_title", default="Confirmer la suppression"),
            lang.get("template_list.delete_confirm_message", default="Êtes-vous sûr de vouloir supprimer le template '{name}' ?\nCette action est irréversible.").format(
                name=template_name
            ),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(template_name):
                QMessageBox.information(
                    self,
                    lang.get("template_list.delete_success", default="Template supprimé"),
                    f"Template supprimé: {template_name}"
                )
                # Reload
                self.load_templates()
            else:
                QMessageBox.critical(
                    self,
                    lang.get("template_list.delete_error", default="Erreur lors de la suppression"),
                    f"Impossible de supprimer: {template_name}"
                )
