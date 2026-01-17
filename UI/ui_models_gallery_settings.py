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
                "settings.models_gallery.title",
                default="Models Gallery",
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
                "settings.models_gallery.description",
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
        checkbox_layout.setSpacing(15)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)

        # Define category order: Armor, Weapon, Other
        category_order = ["armor", "weapon", "other"]
        
        # 3-column layout for categories
        categories_grid_layout = QHBoxLayout()
        categories_grid_layout.setSpacing(15)

        for category in category_order:
            if category not in self.subcategories_by_category:
                continue
                
            # Create a frame for this category
            category_frame = QFrame()
            category_frame.setStyleSheet("QFrame { border: 1px solid #cccccc; border-radius: 5px; }")
            category_frame.setLineWidth(1)
            
            category_vertical_layout = QVBoxLayout()
            category_vertical_layout.setSpacing(8)
            category_vertical_layout.setContentsMargins(10, 10, 10, 10)

            # Category header checkbox - use localized name
            category_label = self._get_category_label(category)
            category_checkbox = QCheckBox(category_label)
            category_checkbox.setFont(QFont())
            category_checkbox.stateChanged.connect(
                lambda state, cat=category: self._on_category_checkbox_changed(cat, state)
            )
            category_vertical_layout.addWidget(category_checkbox)
            self.category_checkboxes[category] = category_checkbox

            # Add separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            category_vertical_layout.addWidget(separator)

            # Subcategory checkboxes
            subcategories = self.subcategories_by_category[category]
            for subcategory in subcategories:
                checkbox_key = f"{category}/{subcategory}"
                # Subcategory label - use localized name
                subcat_label = self._get_subcategory_label(category, subcategory)
                subcat_checkbox = QCheckBox(subcat_label)
                subcat_checkbox.setFont(QFont())
                subcat_checkbox.stateChanged.connect(self._on_checkbox_changed)
                category_vertical_layout.addWidget(subcat_checkbox)
                self.checkboxes[checkbox_key] = subcat_checkbox
                # Store reference to parent category checkbox for sync
                subcat_checkbox.category = category
                subcat_checkbox.category_checkbox = category_checkbox

            category_vertical_layout.addStretch()
            category_frame.setLayout(category_vertical_layout)
            categories_grid_layout.addWidget(category_frame, 1)

        checkbox_layout.addLayout(categories_grid_layout)
        checkbox_layout.addStretch()
        checkbox_container.setLayout(checkbox_layout)
        scroll_area.setWidget(checkbox_container)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def _get_category_label(self, category: str) -> str:
        """Get localized label for a category."""
        key_map = {
            "armor": "settings.models_gallery.category_armor",
            "weapon": "settings.models_gallery.category_weapon",
            "other": "settings.models_gallery.category_other",
        }
        fallback_map = {
            "armor": "Armor",
            "weapon": "Weapon",
            "other": "Other",
        }
        return self.lang.get(key_map.get(category, ""), default=fallback_map.get(category, category))

    def _get_subcategory_label(self, category: str, subcategory: str) -> str:
        """Get localized label for a subcategory."""
        key_map = {
            "arms": "settings.models_gallery.subcategory_arms",
            "cloaks": "settings.models_gallery.subcategory_cloaks",
            "feet": "settings.models_gallery.subcategory_feet",
            "hands": "settings.models_gallery.subcategory_hands",
            "head": "settings.models_gallery.subcategory_head",
            "legs": "settings.models_gallery.subcategory_legs",
            "shields": "settings.models_gallery.subcategory_shields",
            "torso": "settings.models_gallery.subcategory_torso",
            "boats": "settings.models_gallery.subcategory_boats",
            "deco": "settings.models_gallery.subcategory_deco",
            "misc": "settings.models_gallery.subcategory_misc",
            "quiver": "settings.models_gallery.subcategory_quiver",
            "siege": "settings.models_gallery.subcategory_siege",
            "tents": "settings.models_gallery.subcategory_tents",
        }
        fallback = subcategory.capitalize()
        return self.lang.get(key_map.get(subcategory, ""), default=fallback)

    def _load_settings(self):
        """Load settings from configuration and update checkboxes."""
        visible_slots = self.config.get(
            "models_gallery.visible_slots", 
            None
        )
        
        # Default: Armor and Weapon checked, Other unchecked
        if visible_slots is None:
            # Get all subcategories for armor and weapons
            visible_slots = []
            if "armor" in self.subcategories_by_category:
                visible_slots.extend(self.subcategories_by_category["armor"])
            if "weapon" in self.subcategories_by_category:
                visible_slots.extend(self.subcategories_by_category["weapon"])

        # Check subcategory checkboxes based on visible_slots
        for checkbox_key, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)
            # checkbox_key is "category/subcategory", extract subcategory name
            subcategory_name = checkbox_key.split("/")[1]
            # Check if this subcategory is in visible_slots (case-insensitive comparison)
            checkbox.setChecked(subcategory_name.lower() in [s.lower() for s in visible_slots])
            checkbox.blockSignals(False)

        # Update category checkboxes based on subcategory states
        for category in self.category_checkboxes.keys():
            self._update_category_checkbox_state(category)

        logging.info(f"Loaded models gallery settings: {len(visible_slots)} visible subcategories")

    def _on_checkbox_changed(self):
        """Handle checkbox state changes - save to config and update category state."""
        # Update category checkbox states based on subcategories
        for category in self.category_checkboxes.keys():
            self._update_category_checkbox_state(category)
        
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

    def _on_category_checkbox_changed(self, category: str, state: int):
        """
        Handle category checkbox state changes - update all subcategories.
        
        Args:
            category: The category name (armor, weapon, other)
            state: The new state (2=checked, 0=unchecked)
        """
        # Set all subcategories to the same state as the category
        is_checked = state == 2  # Qt.CheckState.Checked value
        
        for subcategory in self.subcategories_by_category.get(category, []):
            checkbox_key = f"{category}/{subcategory}"
            if checkbox_key in self.checkboxes:
                self.checkboxes[checkbox_key].blockSignals(True)
                self.checkboxes[checkbox_key].setChecked(is_checked)
                self.checkboxes[checkbox_key].blockSignals(False)
        
        # Manually save changes (without updating category state to avoid loops)
        visible_slots = []
        for cat in sorted(self.subcategories_by_category.keys()):
            for subcat in self.subcategories_by_category[cat]:
                checkbox_key = f"{cat}/{subcat}"
                if checkbox_key in self.checkboxes and self.checkboxes[checkbox_key].isChecked():
                    visible_slots.append(subcat)
        
        logging.info(f"Category '{category}' toggled to {is_checked}: {len(visible_slots)} items visible")
        self.config.set("models_gallery.visible_slots", visible_slots)
        self.config.save_config()

    def _update_category_checkbox_state(self, category: str):
        """
        Update category checkbox state based on subcategory states.
        
        Args:
            category: The category name
        """
        from PySide6.QtCore import Qt
        
        subcategories = self.subcategories_by_category.get(category, [])
        if not subcategories:
            return
        
        # Count checked subcategories
        checked_count = sum(
            1 for subcat in subcategories
            if self.checkboxes.get(f"{category}/{subcat}", QCheckBox()).isChecked()
        )
        
        # Update category checkbox state
        category_checkbox = self.category_checkboxes.get(category)
        if category_checkbox:
            category_checkbox.blockSignals(True)
            if checked_count == len(subcategories):
                # All checked
                category_checkbox.setCheckState(Qt.CheckState.Checked)
            elif checked_count == 0:
                # None checked
                category_checkbox.setCheckState(Qt.CheckState.Unchecked)
            else:
                # Partially checked
                category_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
            category_checkbox.blockSignals(False)

    def retranslate_ui(self):
        """Retranslate all labels when language changes."""
        # Update category checkbox labels
        for category, checkbox in self.category_checkboxes.items():
            category_label = self._get_category_label(category)
            checkbox.setText(category_label)
        
        # Update subcategory checkbox labels
        for checkbox_key, checkbox in self.checkboxes.items():
            category, subcategory = checkbox_key.split("/")
            subcat_label = self._get_subcategory_label(category, subcategory)
            checkbox.setText(subcat_label)

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

