"""
Models Overview Widget - Main container for model gallery view.

Integrates filter panel and gallery display in a single cohesive interface.
Acts as the entry point for the Models Overview feature from the main menu.
"""

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
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(
            lang.get("models_overview.window_title",
                    default="Models Overview - Gallery")
        )
        self.setMinimumSize(1200, 800)

        # Load metadata
        self.metadata = model_gallery_load_metadata()

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

        # Builder (background logic)
        self.builder = ModelsGalleryBuilderWidget()

        # Apply initial filter (show all)
        self.builder.apply_filters()

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect filter and gallery signals."""
        # When filter changes, apply new filters
        self.filter_panel.filter_changed.connect(self._on_filters_applied)

        # When builder emits thumbnails, display them
        self.builder.thumbnails_ready.connect(self._on_thumbnails_ready)

        # When builder emits error, show error
        self.builder.error_occurred.connect(self._on_error)

        # Load initial gallery
        self._on_filters_applied("", "", "")

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
        self.gallery_display.display_thumbnails(thumbnails)

        # Update stats
        count = len(thumbnails)
        stats_text = lang.get(
            "models_overview.models_count",
            default="{count} models"
        ).format(count=count)
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
