"""
Model Preview Dialog - Full-size image viewer with zoom and navigation.

Displays model images in high resolution with zoom control (mouse wheel)
and navigation between models using arrow keys or buttons.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
)
from PySide6.QtGui import QPixmap, QFont, Qt
from PySide6.QtCore import Qt as QtCore_Qt, QEvent


class ModelPreviewDialog(QDialog):
    """Full-size model image preview with zoom and navigation."""

    def __init__(self, parent=None, model_id: str = None, model_list: list = None, slot_name: str = None):
        """
        Initialize preview dialog.

        Args:
            parent: Parent widget
            model_id: Current model ID to display
            model_list: List of all model IDs (for navigation)
            slot_name: Slot type (Arms, Head, etc.)
        """
        super().__init__(parent)
        self.model_id = model_id
        self.model_list = model_list or []
        self.slot_name = slot_name or "Item"
        self.current_index = 0
        self.zoom_level = 1.0  # 1.0 = fit to screen
        
        # Find current index in list
        if model_id and model_list:
            try:
                self.current_index = model_list.index(model_id)
            except ValueError:
                self.current_index = 0
        
        self._setup_ui()
        self._load_image()
        
        # Set dialog properties
        self.setWindowTitle("Model Preview")
        self.setModal(False)
        self.resize(900, 700)
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

    def _setup_ui(self):
        """Create UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Info bar (model ID, slot, navigation info)
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel()
        info_font = QFont()
        info_font.setPointSize(10)
        self.info_label.setFont(info_font)
        info_layout.addWidget(self.info_label)
        
        info_layout.addStretch()
        
        self.zoom_label = QLabel("100%")
        zoom_font = QFont()
        zoom_font.setPointSize(9)
        self.zoom_label.setFont(zoom_font)
        self.zoom_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.zoom_label)
        
        main_layout.addLayout(info_layout)

        # Scroll area for image (fit to screen)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #1a1a1a; }")
        # Install event filter to handle arrow keys
        self.scroll_area.installEventFilter(self)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(QtCore_Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #1a1a1a;")
        self.scroll_area.setWidget(self.image_label)
        
        main_layout.addWidget(self.scroll_area)

        # Navigation bar
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("← Previous")
        self.prev_button.clicked.connect(self._show_previous)
        self.prev_button.setMaximumWidth(120)
        nav_layout.addWidget(self.prev_button)
        
        nav_layout.addStretch()
        
        self.counter_label = QLabel()
        counter_font = QFont()
        counter_font.setPointSize(9)
        self.counter_label.setFont(counter_font)
        self.counter_label.setStyleSheet("color: #888888;")
        nav_layout.addWidget(self.counter_label)
        
        nav_layout.addStretch()
        
        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self._show_next)
        self.next_button.setMaximumWidth(120)
        nav_layout.addWidget(self.next_button)
        
        main_layout.addLayout(nav_layout)

        # Close button
        self.close_button = QPushButton("Close (Esc)")
        self.close_button.clicked.connect(self.close)
        self.close_button.setMaximumWidth(150)
        main_layout.addWidget(self.close_button)

    def _load_image(self, reset_zoom: bool = True):
        """Load and display current model image."""
        if not self.model_id:
            self.image_label.setText("No model selected")
            self._update_info()
            return

        image_path = Path(f"Img/Models/items/{self.model_id}.webp")
        
        if not image_path.exists():
            self.image_label.setText(f"Image not found:\n{image_path}")
            self._update_info()
            return

        # Load image
        pixmap = QPixmap(str(image_path))
        
        if pixmap.isNull():
            self.image_label.setText(f"Failed to load image:\n{self.model_id}.webp")
            self._update_info()
            return

        # Reset zoom to fit screen (only when changing model, not on zoom)
        if reset_zoom:
            self.zoom_level = 1.0
        self._display_pixmap(pixmap)
        self._update_info()

    def _display_pixmap(self, pixmap: QPixmap):
        """Display pixmap with current zoom level (fit to screen)."""
        if pixmap.isNull():
            return

        # Get scroll area dimensions
        viewport_width = self.scroll_area.viewport().width()
        viewport_height = self.scroll_area.viewport().height()
        
        # Calculate scaled size (fit to screen at zoom level 1.0)
        scaled_pixmap = pixmap.scaledToWidth(
            int(viewport_width * 0.95),
            Qt.SmoothTransformation
        )
        
        # Check if height exceeds viewport
        if scaled_pixmap.height() > viewport_height * 0.9:
            scaled_pixmap = pixmap.scaledToHeight(
                int(viewport_height * 0.9),
                Qt.SmoothTransformation
            )
        
        # Apply zoom level
        zoomed_pixmap = scaled_pixmap.scaledToWidth(
            int(scaled_pixmap.width() * self.zoom_level),
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(zoomed_pixmap)

    def _update_info(self):
        """Update info labels with current model data."""
        if self.model_list and self.model_id:
            counter = f"{self.current_index + 1}/{len(self.model_list)}"
            self.counter_label.setText(counter)
        
        # Info: Model ID and Slot
        self.info_label.setText(f"Model ID: {self.model_id} | Slot: {self.slot_name}")
        
        # Zoom level
        zoom_percent = int(self.zoom_level * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
        
        # Button states
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.model_list) - 1)

    def _show_previous(self):
        """Show previous model in list."""
        if self.current_index > 0:
            self.current_index -= 1
            self.model_id = self.model_list[self.current_index]
            self._load_image()

    def _show_next(self):
        """Show next model in list."""
        if self.current_index < len(self.model_list) - 1:
            self.current_index += 1
            self.model_id = self.model_list[self.current_index]
            self._load_image()

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom."""
        if event.angleDelta().y() > 0:
            # Wheel up = zoom in
            self.zoom_level = min(self.zoom_level + 0.1, 3.0)  # Max 300%
        else:
            # Wheel down = zoom out
            self.zoom_level = max(self.zoom_level - 0.1, 0.5)  # Min 50%
        
        # Redisplay with new zoom level (don't reset zoom)
        if self.model_id:
            image_path = Path(f"Img/Models/items/{self.model_id}.webp")
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    self._display_pixmap(pixmap)
                    self._update_info()
        
        event.accept()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == QtCore_Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore_Qt.Key_Left:
            self._show_previous()
        elif event.key() == QtCore_Qt.Key_Right:
            self._show_next()
        elif event.key() == QtCore_Qt.Key_Home:
            if self.model_list:
                self.current_index = 0
                self.model_id = self.model_list[0]
                self._load_image()
        elif event.key() == QtCore_Qt.Key_End:
            if self.model_list:
                self.current_index = len(self.model_list) - 1
                self.model_id = self.model_list[self.current_index]
                self._load_image()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Handle window resize - re-fit image."""
        super().resizeEvent(event)
        if self.model_id:
            self._load_image()

    def eventFilter(self, obj, event):
        """Intercept keyboard events from scroll area to handle navigation."""
        if obj is self.scroll_area and event.type() == QEvent.KeyPress:
            # Delegate to keyPressEvent so arrow keys work
            self.keyPressEvent(event)
            return True
        return super().eventFilter(obj, event)
