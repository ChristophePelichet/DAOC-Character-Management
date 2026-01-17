"""
Models Overview Widget - Main container for model gallery view.

Integrates filter panel and gallery display in a single cohesive interface.
Acts as the entry point for the Models Overview feature from the main menu.
"""

import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from UI.ui_model_gallery_filter import ModelsFilterPanelWidget
from UI.ui_model_gallery_display import ModelsGalleryDisplayWidget
from UI.ui_model_gallery_builder import ModelsGalleryBuilderWidget
from Functions.model_database_manager import model_gallery_load_metadata
from Functions.language_manager import lang


class ModelsOverviewWidget(QWidget):
    """
    Main Models Overview Gallery widget.

    Combines filter controls and gallery display in a single interface.
    Can be embedded in a window or dialog.
    """

    def __init__(self, parent=None):
        """
        Initialize Models Overview widget.

        Args:
            parent: Parent widget (optional, usually None for standalone window)
        """
        super().__init__(parent)
        self.setWindowTitle(
            lang.get("models_overview.window_title",
                    default="Models Overview - Gallery")
        )

        # Load metadata directly (should be fast)
        logging.info("Loading metadata...")
        self.metadata = model_gallery_load_metadata()
        logging.info(f"Metadata loaded: {len(self.metadata)} types")

        # Initialize components
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Build UI layout."""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left: Filter panel
        self.filter_panel = ModelsFilterPanelWidget(self.metadata)
        self.filter_panel.setMinimumWidth(200)
        self.filter_panel.setMaximumWidth(250)
        main_layout.addWidget(self.filter_panel)

        # Right: Gallery + stats
        right_layout = QVBoxLayout()

        # Title bar
        title_layout = QHBoxLayout()
        title_label = QLabel(
            lang.get("models_overview.gallery_title",
                    default="🖼️ Model Gallery")
        )
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.stats_label = QLabel()
        title_layout.addWidget(self.stats_label)
        right_layout.addLayout(title_layout)

        # Gallery display
        self.gallery_display = ModelsGalleryDisplayWidget()
        right_layout.addWidget(self.gallery_display)

        # Builder (background logic) - metadata will be set later
        self.builder = ModelsGalleryBuilderWidget()

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect filter and gallery signals."""
        logging.info("Widget: connecting signals...")
        
        # When filter changes, apply new filters
        self.filter_panel.filter_changed.connect(self._on_filters_applied)
        logging.info("Widget: connected filter_changed signal")

        # When builder emits thumbnails, display them
        self.builder.thumbnails_ready.connect(self._on_thumbnails_ready)
        logging.info("Widget: connected thumbnails_ready signal")

        # When builder emits error, show error
        self.builder.error_occurred.connect(self._on_error)
        logging.info("Widget: connected error_occurred signal")

        # NOW set metadata on the builder (after signals are connected)
        logging.info("Widget: setting metadata on builder...")
        self.builder.set_metadata(self.metadata)
        logging.info("Widget: metadata set on builder")
        
        # Show initial state: "Select filters and click Apply"
        initial_text = lang.get(
            "models_overview.models_count",
            default="{count} models"
        ).format(count=0)
        self.stats_label.setText(initial_text)

    def _on_filters_applied(
        self, type_filter: str, subtype_filter: str, search_query: str
    ):
        """
        Handle filter changes from filter panel.

        Args:
            type_filter: Type filter value
            subtype_filter: Subtype filter value
            search_query: Search query value
        """
        self.builder.apply_filters(
            type_filter, subtype_filter, search_query
        )

    def _on_thumbnails_ready(self, thumbnails: list):
        """
        Handle thumbnails ready from builder.

        Args:
            thumbnails: List of ModelThumbnail objects
        """
        logging.info(f"Widget: _on_thumbnails_ready called with {len(thumbnails)} thumbnails")
        self.gallery_display.display_thumbnails(thumbnails)

        # Update stats
        count = len(thumbnails)
        stats_text = lang.get(
            "models_overview.models_count",
            default="{count} models"
        ).format(count=count)
        logging.info(f"Widget: updating stats label to '{stats_text}'")
        self.stats_label.setText(stats_text)

    def _on_error(self, error_message: str):
        """
        Handle error from builder.

        Args:
            error_message: Error message string
        """
        self.gallery_display.display_thumbnails([])
        error_text = lang.get(
            "models_overview.error_prefix", default="❌ Error: "
        )
        self.stats_label.setText(f"{error_text}{error_message}")
