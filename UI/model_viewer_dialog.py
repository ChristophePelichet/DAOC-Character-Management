"""
Model Viewer Dialog - Display 3D model images for items
Shows embedded model images from Img/Models/items/ folder
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from Functions.language_manager import lang
from Functions.path_manager import get_resource_path


class ModelViewerDialog(QDialog):
    """Dialog to display item 3D model images."""
    
    def __init__(self, parent, model_id, item_name="", model_category="unknown"):
        """
        Initialize Model Viewer Dialog.
        
        Args:
            parent: Parent widget
            model_id: Model ID (matches filename in Img/Models/items/)
            item_name: Optional item name for title
            model_category: Optional model category for display
        """
        super().__init__(parent)
        
        self.model_id = str(model_id)
        self.item_name = item_name
        self.model_category = model_category
        
        self._setup_ui()
        self._load_model_image()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Window title
        title = f"{self.item_name} - " if self.item_name else ""
        title += lang.get("model_viewer.title", default="Model Viewer")
        self.setWindowTitle(title)
        
        # Window size and flags
        self.resize(600, 700)
        self.setWindowFlags(
            Qt.Window | 
            Qt.WindowCloseButtonHint | 
            Qt.WindowMinimizeButtonHint
        )
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header: Item info
        header_layout = QHBoxLayout()
        
        # Item name label
        if self.item_name:
            name_label = QLabel(f"<b>{self.item_name}</b>")
            name_label.setStyleSheet("font-size: 14pt;")
            header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # Model ID label
        id_label = QLabel(f"Model ID: {self.model_id}")
        id_label.setStyleSheet("color: gray;")
        header_layout.addWidget(id_label)
        
        layout.addLayout(header_layout)
        
        # Category label
        if self.model_category and self.model_category != "unknown":
            category_label = QLabel(f"Category: {self.model_category}")
            category_label.setStyleSheet("color: #4CAF50; font-style: italic;")
            layout.addWidget(category_label)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.image_label, 1)  # Stretch factor 1
        
        # Footer: Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton(lang.get("model_viewer.close", default="Close"))
        close_button.setMinimumWidth(100)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _load_model_image(self):
        """Load and display the model image."""
        try:
            # Build image path: Img/Models/items/{model_id}.webp
            image_filename = f"{self.model_id}.webp"
            image_path = get_resource_path(f"Img/Models/items/{image_filename}")
            
            # Check if file exists
            if not Path(image_path).exists():
                self._show_no_image_message()
                logging.warning(f"Model image not found: {image_path}")
                return
            
            # Load image
            pixmap = QPixmap(str(image_path))
            
            if pixmap.isNull():
                self._show_no_image_message()
                logging.error(f"Failed to load model image: {image_path}")
                return
            
            # Scale image to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            logging.debug(f"Loaded model image: {image_path}")
            
        except Exception as e:
            self._show_no_image_message()
            logging.error(f"Error loading model image for ID {self.model_id}: {e}")
    
    def _show_no_image_message(self):
        """Display 'no image available' message."""
        message = lang.get(
            "model_viewer.no_image", 
            default="No image available for this model"
        )
        self.image_label.setText(f"<p style='color: gray;'>{message}</p>")
    
    def resizeEvent(self, event):
        """Handle window resize to rescale image."""
        super().resizeEvent(event)
        
        # Reload image at new size if pixmap exists
        if hasattr(self, 'image_label') and not self.image_label.pixmap().isNull():
            self._load_model_image()
