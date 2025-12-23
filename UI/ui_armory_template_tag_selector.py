"""
Armory Tag Selector Widget - Permet la sélection de tags avec auto-complétion
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QCompleter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from Functions.language_manager import lang


class TagBadge(QFrame):
    """Widget badge pour afficher un tag sélectionné"""
    
    removed = Signal(str)  # tag_name
    
    def __init__(self, tag_name, parent=None):
        super().__init__(parent)
        self.tag_name = tag_name
        
        self.setStyleSheet(
            "QFrame { "
            "background-color: #2196F3; "
            "border-radius: 10px; "
            "padding: 3px 8px; "
            "margin: 2px; "
            "}"
        )
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Tag text
        label = QLabel(tag_name)
        label.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
        layout.addWidget(label)
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(255, 255, 255, 0.3); "
            "border: none; "
            "border-radius: 8px; "
            "color: white; "
            "font-weight: bold; "
            "font-size: 12px; "
            "}"
            "QPushButton:hover { "
            "background-color: rgba(255, 255, 255, 0.5); "
            "}"
        )
        remove_btn.clicked.connect(lambda: self.removed.emit(self.tag_name))
        layout.addWidget(remove_btn)


class ArmoryTagSelector(QWidget):
    """
    Widget pour sélectionner des tags avec auto-complétion.
    Limite de 5 tags.
    """
    
    MAX_TAGS = 5
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_tags = []
        self._setup_ui()
        self._load_suggested_tags()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(5)
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Tapez un tag et appuyez sur Entrée...")
        self.tag_input.returnPressed.connect(self._add_tag_from_input)
        input_row.addWidget(self.tag_input, 1)
        
        add_btn = QPushButton("+ Ajouter")
        add_btn.setFixedWidth(80)
        add_btn.clicked.connect(self._add_tag_from_input)
        input_row.addWidget(add_btn)
        
        layout.addLayout(input_row)
        
        # Tags badges container
        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(3)
        self.tags_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.tags_container)
        
        # Suggested tags (clickable)
        suggested_label = QLabel("<i>Tags suggérés :</i>")
        suggested_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(suggested_label)
        
        self.suggested_container = QWidget()
        self.suggested_layout = QHBoxLayout(self.suggested_container)
        self.suggested_layout.setContentsMargins(0, 0, 0, 0)
        self.suggested_layout.setSpacing(5)
        self.suggested_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.suggested_container)
    
    def _load_suggested_tags(self):
        """Load suggested tags from translations"""
        suggested_tags_data = lang.get("template_import.tags_suggested", default={})
        
        # Flatten all categories
        all_tags = []
        for category, tags in suggested_tags_data.items():
            all_tags.extend(tags)
        
        # Setup autocompleter
        completer = QCompleter(all_tags)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.tag_input.setCompleter(completer)
        
        # Create suggested tag buttons (first 10 tags)
        for tag in all_tags[:10]:
            btn = QPushButton(tag)
            btn.setStyleSheet(
                "QPushButton { "
                "background-color: #f0f0f0; "
                "border: 1px solid #ccc; "
                "border-radius: 8px; "
                "padding: 2px 8px; "
                "font-size: 10px; "
                "color: #666; "
                "}"
                "QPushButton:hover { "
                "background-color: #e0e0e0; "
                "border-color: #2196F3; "
                "color: #2196F3; "
                "}"
            )
            btn.clicked.connect(lambda checked, t=tag: self._add_tag(t))
            self.suggested_layout.addWidget(btn)
        
        self.suggested_layout.addStretch()
    
    def _add_tag_from_input(self):
        """Add tag from input field"""
        tag = self.tag_input.text().strip().lower()
        if tag:
            self._add_tag(tag)
            self.tag_input.clear()
    
    def _add_tag(self, tag):
        """Add a tag to selection"""
        # Validate
        if not tag or len(tag) > 20:
            return
        
        # Check limit
        if len(self.selected_tags) >= self.MAX_TAGS:
            return
        
        # Check duplicate
        if tag in self.selected_tags:
            return
        
        # Add tag
        self.selected_tags.append(tag)
        
        # Create badge
        badge = TagBadge(tag, self)
        badge.removed.connect(self._remove_tag)
        self.tags_layout.addWidget(badge)
    
    def _remove_tag(self, tag):
        """Remove a tag from selection"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        
        # Remove badge from layout
        for i in range(self.tags_layout.count()):
            widget = self.tags_layout.itemAt(i).widget()
            if isinstance(widget, TagBadge) and widget.tag_name == tag:
                widget.deleteLater()
                break
    
    def get_tags(self):
        """Get selected tags"""
        return self.selected_tags.copy()
    
    def set_tags(self, tags):
        """Set tags programmatically"""
        # Clear current
        self.selected_tags.clear()
        for i in reversed(range(self.tags_layout.count())):
            widget = self.tags_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add new tags
        for tag in tags[:self.MAX_TAGS]:
            self._add_tag(tag)


# Backward compatibility alias
TagSelector = ArmoryTagSelector
