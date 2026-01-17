"""
Model Gallery Display Widget - Main gallery UI for browsing models.

Displays model thumbnails in a scrollable grid layout with filter integration.
Handles image loading, hover effects, and model selection.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QGridLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont

from Functions.model_gallery_builder import ModelThumbnail


class ModelThumbnailWidget(QFrame):
    """Single model thumbnail widget."""

    # Signal emitted when thumbnail is clicked
    clicked = Signal(str)  # Emits model_id

    def __init__(self, thumbnail: ModelThumbnail, parent=None):
        """
        Initialize thumbnail widget.

        Args:
            thumbnail: ModelThumbnail object
            parent: Parent widget
        """
        super().__init__(parent)
        self.thumbnail = thumbnail
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setCursor(Qt.PointingHandCursor)  # Show clickable cursor
        self.setStyleSheet(
            """
            ModelThumbnailWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: #fff;
            }
            ModelThumbnailWidget:hover {
                border: 1px solid #0066cc;
                background-color: #f0f7ff;
            }
        """
        )
        self._setup_ui()

    def mousePressEvent(self, event):
        """Handle click on thumbnail."""
        self.clicked.emit(self.thumbnail.model_id)
        super().mousePressEvent(event)

    def _setup_ui(self):
        """Build UI."""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self._load_image()
        layout.addWidget(self.image_label)

        # Model ID
        id_label = QLabel(self.thumbnail.display_label)
        id_font = QFont()
        id_font.setPointSize(9)
        id_font.setBold(True)
        id_label.setFont(id_font)
        id_label.setAlignment(Qt.AlignCenter)
        id_label.setStyleSheet("color: #000000; font-weight: bold;")
        layout.addWidget(id_label)

        self.setLayout(layout)

    def _load_image(self):
        """Load and display thumbnail image."""
        from Functions.language_manager import lang

        if self.thumbnail.full_path.exists():
            pixmap = QPixmap(str(self.thumbnail.full_path))
            # Scale to max width 150 while preserving aspect ratio
            scaled_pixmap = pixmap.scaledToWidth(
                150, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            # Placeholder for missing image
            no_image_text = lang.get(
                "models_overview.no_image", default="No image"
            )
            self.image_label.setText(no_image_text)
            self.image_label.setStyleSheet("color: #999;")


class ModelsGalleryDisplayWidget(QWidget):
    """
    Main gallery display widget.

    Shows model thumbnails in a grid layout with scrolling.
    """

    # Signal emitted when a thumbnail is clicked
    thumbnail_clicked = Signal(str)  # Emits model_id

    def __init__(self, parent=None):
        """
        Initialize gallery display.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build UI layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for gallery
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
            }
        """
        )

        # Container widget for grid
        self.container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.container.setLayout(self.grid_layout)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def display_thumbnails(self, thumbnails: list):
        """
        Display thumbnails in grid.

        Args:
            thumbnails: List of ModelThumbnail objects
        """
        from Functions.language_manager import lang

        # Clear existing widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add thumbnails to grid
        if not thumbnails:
            # Show empty state
            empty_text = lang.get(
                "models_overview.no_models", default="No models found"
            )
            empty_label = QLabel(empty_text)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_font = QFont()
            empty_font.setPointSize(12)
            empty_label.setFont(empty_font)
            self.grid_layout.addWidget(empty_label, 0, 0)
            return

        # Display in 5-column grid
        columns = 5
        for idx, thumbnail in enumerate(thumbnails):
            widget = ModelThumbnailWidget(thumbnail)
            # Connect thumbnail click signal to gallery signal
            widget.clicked.connect(self.thumbnail_clicked.emit)
            row = idx // columns
            col = idx % columns
            self.grid_layout.addWidget(widget, row, col)

        # Add stretch at end to push items to top-left
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)

    def clear(self):
        """Clear all displayed thumbnails."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
