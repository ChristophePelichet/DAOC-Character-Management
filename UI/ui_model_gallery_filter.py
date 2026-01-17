"""
Model Gallery Filter Panel Widget - UI for filtering models.

Provides filter controls (type, subtype, search) for the model gallery view.
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

    Provides controls to filter models by type, subtype, and search.
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

        # Type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(
            QLabel(lang.get("models_overview.type_label", default="Type:"))
        )
        self.type_combo = QComboBox()
        self.type_combo.addItem(
            lang.get("models_overview.all_types", default="-- All --"), None
        )
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Subtype filter
        subtype_layout = QHBoxLayout()
        subtype_layout.addWidget(
            QLabel(
                lang.get("models_overview.subtype_label",
                        default="Subtype:")
            )
        )
        self.subtype_combo = QComboBox()
        self.subtype_combo.setEnabled(False)
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

        options = model_gallery_build_filter_options(self.metadata)

        # Populate types
        self.type_combo.blockSignals(True)
        self.type_combo.clear()
        self.type_combo.addItem(
            lang.get("models_overview.all_types", default="-- All --"), None
        )

        for type_name in options["types"]:
            self.type_combo.addItem(type_name, type_name)

        self.type_combo.blockSignals(False)

    def _on_type_changed(self):
        """Handle type selection change."""
        from Functions.language_manager import lang

        type_name = self.type_combo.currentData()

        # Update subtype combo
        self.subtype_combo.blockSignals(True)
        self.subtype_combo.clear()

        if type_name:
            options = model_gallery_build_filter_options(self.metadata)
            subtypes = options["subtypes_by_type"].get(type_name, [])

            self.subtype_combo.setEnabled(len(subtypes) > 0)

            if subtypes:
                self.subtype_combo.addItem(
                    lang.get(
                        "models_overview.all_types", default="-- All --"
                    ),
                    None
                )
                for subtype_name in subtypes:
                    self.subtype_combo.addItem(subtype_name, subtype_name)
        else:
            self.subtype_combo.setEnabled(False)

        self.subtype_combo.blockSignals(False)

    def _on_subtype_changed(self):
        """Handle subtype selection change."""
        pass  # Auto-trigger on apply

    def _on_search_changed(self):
        """Handle search input change."""
        pass  # Auto-trigger on apply

    def _on_apply_filters(self):
        """Emit filter_changed signal with current filter values."""
        type_filter = self.type_combo.currentData() or ""
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
            self.type_combo.currentData() or "",
            self.subtype_combo.currentData() or "",
            self.search_input.text().strip(),
        )

    def reset_filters(self):
        """Reset all filters to default state."""
        self.type_combo.setCurrentIndex(0)
        self.search_input.clear()
