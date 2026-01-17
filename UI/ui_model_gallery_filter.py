"""
Model Gallery Filter Panel Widget - UI for filtering models.

Provides filter controls (item type, search) for the model gallery view.
Emits signals when filters change to notify the gallery display to update.

Paired with: Functions/model_gallery_filter.py
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from Functions.model_gallery_builder import model_gallery_build_filter_options


class ModelsFilterPanelWidget(QWidget):
    """
    Filter panel for model gallery.

    Provides search filter for items.
    Emits filter_changed signal when user applies filters.
    """

    # Signal emitted when filters change: (type, subtype, search_query)
    filter_changed = Signal(str, str, str)

    def __init__(self, metadata: dict, parent=None):
        """
        Initialize filter panel.

        Args:
            metadata: Output from model_gallery_load_metadata()
            parent: Parent widget
        """
        super().__init__(parent)
        self.metadata = metadata
        self._setup_ui()
        self._populate_filters()

    def _setup_ui(self):
        """Build UI layout."""
        from Functions.language_manager import lang

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel(
            lang.get("models_overview.filters_title", default="Filters")
        )
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        layout.addWidget(title)

        # Type label - Static 'items'
        type_layout = QHBoxLayout()
        type_layout.addWidget(
            QLabel(lang.get("models_overview.type_label", default="Type:"))
        )
        type_label = QLabel("items")
        type_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        type_layout.addWidget(type_label)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Subtype (Item Type) filter
        subtype_layout = QHBoxLayout()
        subtype_layout.addWidget(
            QLabel(
                lang.get("models_overview.subtype_label",
                        default="Item Type:")
            )
        )
        self.subtype_combo = QComboBox()
        self.subtype_combo.currentIndexChanged.connect(
            self._on_subtype_changed
        )
        subtype_layout.addWidget(self.subtype_combo)
        layout.addLayout(subtype_layout)

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(
            QLabel(lang.get("models_overview.search_label",
                           default="Search:"))
        )
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            lang.get("models_overview.search_placeholder",
                    default="Model ID...")
        )
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Apply button
        self.apply_button = QPushButton(
            lang.get("models_overview.apply_button", default="Apply")
        )
        self.apply_button.clicked.connect(self._on_apply_filters)
        layout.addWidget(self.apply_button)

        layout.addStretch()

        self.setLayout(layout)

    def _populate_filters(self):
        """Populate filter dropdowns with metadata."""
        from Functions.language_manager import lang

        # Handle empty metadata
        if not self.metadata:
            self.subtype_combo.clear()
            self.subtype_combo.addItem(
                lang.get("models_overview.all_types", default="-- All --"),
                None
            )
            return

        # Get item subtypes - extract all subcategories from hierarchical structure
        # metadata['items'] = {'weapon': {'bow': [...], 'sword': [...]}, 'armor': {'helm': [...], ...}}
        items_data = self.metadata.get("items", {})
        
        self.subtype_combo.blockSignals(True)
        self.subtype_combo.clear()
        self.subtype_combo.addItem(
            lang.get("models_overview.all_types", default="-- All --"), None
        )

        # Extract all subcategories from all categories
        all_subcategories = {}
        for category, subcats in items_data.items():
            if isinstance(subcats, dict):
                for subcat_name, model_ids in subcats.items():
                    if subcat_name != "_" and isinstance(model_ids, list):
                        # Store subcategory with count of items
                        all_subcategories[subcat_name] = len(model_ids)

        # Add subcategories to dropdown, sorted by name
        for subcat_name in sorted(all_subcategories.keys()):
            count = all_subcategories[subcat_name]
            display_name = f"{subcat_name.capitalize()} ({count})"
            self.subtype_combo.addItem(display_name, subcat_name)

        self.subtype_combo.blockSignals(False)

    def _on_subtype_changed(self):
        """Handle subtype selection change - auto-trigger filter."""
        type_filter = "items"  # Always items
        subtype_filter = self.subtype_combo.currentData() or ""
        search_query = self.search_input.text().strip()

        self.filter_changed.emit(type_filter, subtype_filter, search_query)

    def _on_search_changed(self):
        """Handle search input change."""
        pass  # Auto-trigger on apply

    def _on_apply_filters(self):
        """Emit filter_changed signal with current filter values."""
        type_filter = "items"  # Always items
        subtype_filter = self.subtype_combo.currentData() or ""
        search_query = self.search_input.text().strip()

        self.filter_changed.emit(type_filter, subtype_filter, search_query)

    def get_filters(self) -> tuple:
        """
        Get current filter values.

        Returns:
            Tuple of (type_filter, subtype_filter, search_query)
        """
        return (
            "items",
            self.subtype_combo.currentData() or "",
            self.search_input.text().strip(),
        )

    def reset_filters(self):
        """Reset all filters to default state."""
        self.subtype_combo.setCurrentIndex(0)
        self.search_input.clear()

    def update_metadata(self, metadata: dict):
        """
        Update metadata and refresh filter options.

        Args:
            metadata: Updated metadata dictionary
        """
        self.metadata = metadata
        self._populate_filters()
