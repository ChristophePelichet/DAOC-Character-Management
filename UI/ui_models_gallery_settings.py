"""
Models Gallery Settings Widget - Configure visible model slots.

Provides checkboxes to enable/disable visibility of model slots (Weapons, Armor variants, etc.)
in the Models Gallery. Changes are saved to the configuration file.
"""

import logging
from typing import List
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

    Provides a list of checkboxes for each model slot (Weapons, Arms, Head, etc.)
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

        self.config = config
        self.lang = lang
        self.checkboxes = {}

        # List of all available model slots
        self.all_slots = [
            "Weapons",
            "Arms",
            "Hands",
            "Feet",
            "Legs",
            "Torso",
            "Head",
            "Shields",
            "Cloaks",
            "Quiver",
            "Misc",
            "Siege",
            "Boats",
            "Tents",
            "Deco",
        ]

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
                default="Select which model slots should be visible in the gallery:",
            )
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # Container for checkboxes in a grid
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setSpacing(5)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)

        # Create checkboxes for each slot
        for slot_name in self.all_slots:
            checkbox = QCheckBox(slot_name)
            checkbox.setFont(QFont())
            checkbox.stateChanged.connect(self._on_checkbox_changed)
            checkbox_layout.addWidget(checkbox)
            self.checkboxes[slot_name] = checkbox

        checkbox_layout.addStretch()
        checkbox_container.setLayout(checkbox_layout)
        scroll_area.setWidget(checkbox_container)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def _load_settings(self):
        """Load settings from configuration and update checkboxes."""
        visible_slots = self.config.get(
            "models_gallery.visible_slots", self.all_slots
        )

        for slot_name, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(slot_name in visible_slots)
            checkbox.blockSignals(False)

        logging.info(f"Loaded models gallery settings: {len(visible_slots)} visible slots")

    def _on_checkbox_changed(self):
        """Handle checkbox state changes - save to config."""
        visible_slots = [
            slot_name
            for slot_name, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        ]

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
        return [
            slot_name
            for slot_name, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        ]
