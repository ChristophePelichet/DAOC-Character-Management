"""
Models Gallery Settings Widget - Configure visible model slots.

Provides checkboxes to enable/disable visibility of model slots (Weapons, Armor variants, etc.)
in the Models Gallery. Changes are saved to the configuration file.
"""

import logging
from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QScrollArea,
    QFrame,
)
from PySide6.QtGui import QFont


class ModelsGallerySettingsWidget(QWidget):
    """
    Settings widget for configuring visible model slots.

    Provides a hierarchical list of checkboxes for each model category and subcategory
    that can be toggled to show/hide them in the Models Gallery view.
    """

    def __init__(self, parent=None):
        """
        Initialize models gallery settings.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        from Functions.config_manager import config
        from Functions.language_manager import lang
        from Functions.model_database_manager import model_gallery_load_metadata

        self.config = config
        self.lang = lang
        self.checkboxes = {}  # Maps "category/subcategory" -> checkbox
        self.category_checkboxes = {}  # Maps "category" -> checkbox
        
        # Load metadata to get categories and subcategories
        self.metadata = model_gallery_load_metadata()
        self.subcategories_by_category: Dict[str, List[str]] = {}
        
        # Build subcategories map
        if self.metadata and "items" in self.metadata:
            for category, subcats in self.metadata["items"].items():
                if isinstance(subcats, dict):
                    self.subcategories_by_category[category] = sorted([
                        subcat for subcat in subcats.keys() if subcat != "_"
                    ])

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Build UI layout."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel(
            self.lang.get(
                "settings.models_gallery_title",
                default="Models Gallery - Visible Slots",
            )
        )
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        description = QLabel(
            self.lang.get(
                "settings.models_gallery_description",
                default="Select which model categories should be visible in the gallery:",
            )
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # Container for checkboxes
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setSpacing(5)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)

        # Create hierarchical checkboxes: Category > Subcategory
        for category in sorted(self.subcategories_by_category.keys()):
            # Category checkbox
            category_checkbox = QCheckBox(category.capitalize())
            category_checkbox.setFont(QFont())
            category_checkbox.stateChanged.connect(self._on_checkbox_changed)
            checkbox_layout.addWidget(category_checkbox)
            self.category_checkboxes[category] = category_checkbox

            # Subcategory checkboxes (indented)
            subcategories = self.subcategories_by_category[category]
            for subcategory in subcategories:
                # Indent subcategories
                subcat_layout = QHBoxLayout()
                subcat_layout.setContentsMargins(20, 0, 0, 0)
                
                checkbox_key = f"{category}/{subcategory}"
                subcat_checkbox = QCheckBox(subcategory.capitalize())
                subcat_checkbox.setFont(QFont())
                subcat_checkbox.stateChanged.connect(self._on_checkbox_changed)
                subcat_layout.addWidget(subcat_checkbox)
                subcat_layout.addStretch()
                
                checkbox_layout.addLayout(subcat_layout)
                self.checkboxes[checkbox_key] = subcat_checkbox

        checkbox_layout.addStretch()
        checkbox_container.setLayout(checkbox_layout)
        scroll_area.setWidget(checkbox_container)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def _load_settings(self):
        """Load settings from configuration and update checkboxes."""
        visible_slots = self.config.get(
            "models_gallery.visible_slots", 
            ["arms", "boats", "bow", "cloaks", "chest", "feet", "hands", 
             "head", "helm", "legs", "misc", "quiver", "shield", "sword", 
             "torso", "tents", "siege", "deco"]
        )

        # Check subcategory checkboxes based on visible_slots
        for checkbox_key, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)
            # checkbox_key is "category/subcategory", extract subcategory name
            subcategory_name = checkbox_key.split("/")[1]
            # Check if this subcategory is in visible_slots (case-insensitive comparison)
            checkbox.setChecked(subcategory_name.lower() in [s.lower() for s in visible_slots])
            checkbox.blockSignals(False)

        logging.info(f"Loaded models gallery settings: {len(visible_slots)} visible subcategories")

    def _on_checkbox_changed(self):
        """Handle checkbox state changes - save to config."""
        # Collect visible subcategories (not categories, but the actual items to show)
        visible_slots = []
        
        for category in sorted(self.subcategories_by_category.keys()):
            for subcategory in self.subcategories_by_category[category]:
                checkbox_key = f"{category}/{subcategory}"
                if checkbox_key in self.checkboxes and self.checkboxes[checkbox_key].isChecked():
                    # Store as "category/subcategory" for filtering
                    visible_slots.append(subcategory)

        logging.info(f"Updating visible slots: {visible_slots}")
        self.config.set("models_gallery.visible_slots", visible_slots)
        self.config.save_config()
        logging.info("Models gallery settings saved")

    def get_visible_slots(self) -> List[str]:
        """
        Get currently selected visible slots.

        Returns:
            List of slot names that should be visible
        """
        visible_slots = []
        for checkbox_key, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                visible_slots.append(checkbox_key.split("/")[1])
        return visible_slots

