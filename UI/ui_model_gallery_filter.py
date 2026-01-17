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
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont



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
        from Functions.language_manager import lang
        self.lang = lang
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

        # Category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(
            QLabel(lang.get("models_overview.category_label",
                           default="Category:"))
        )
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(250)
        self.category_combo.currentIndexChanged.connect(
            self._on_category_changed
        )
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        # Sub-category filter
        subcategory_layout = QHBoxLayout()
        subcategory_layout.addWidget(
            QLabel(lang.get("models_overview.subcategory_label",
                           default="Sub-Category:"))
        )
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setMinimumWidth(250)
        self.subcategory_combo.currentIndexChanged.connect(
            self._on_subcategory_changed
        )
        subcategory_layout.addWidget(self.subcategory_combo)
        layout.addLayout(subcategory_layout)

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

    def _get_category_label(self, category: str) -> str:
        """Get localized label for a category."""
        key_map = {
            "armor": "settings.pages.models_gallery.category_armor",
            "weapon": "settings.pages.models_gallery.category_weapon",
            "other": "settings.pages.models_gallery.category_other",
        }
        fallback_map = {
            "armor": "Armor",
            "weapon": "Weapon",
            "other": "Other",
        }
        key = key_map.get(category, "")
        result = self.lang.get(key, default=fallback_map.get(category, category))
        return result

    def _get_subcategory_label(self, subcategory: str) -> str:
        """Get localized label for a subcategory."""
        key_map = {
            "arms": "settings.pages.models_gallery.subcategory_arms",
            "chest": "settings.pages.models_gallery.subcategory_chest",
            "cloak": "settings.pages.models_gallery.subcategory_cloak",
            "feet": "settings.pages.models_gallery.subcategory_feet",
            "hands": "settings.pages.models_gallery.subcategory_hands",
            "head": "settings.pages.models_gallery.subcategory_head",
            "legs": "settings.pages.models_gallery.subcategory_legs",
            "sleeves": "settings.pages.models_gallery.subcategory_sleeves",
            "shields": "settings.pages.models_gallery.subcategory_shields",
            "torso": "settings.pages.models_gallery.subcategory_torso",
            "bow": "settings.pages.models_gallery.subcategory_bow",
            "crossbow": "settings.pages.models_gallery.subcategory_crossbow",
            "dagger": "settings.pages.models_gallery.subcategory_dagger",
            "flexible": "settings.pages.models_gallery.subcategory_flexible",
            "greave": "settings.pages.models_gallery.subcategory_greave",
            "instrument": "settings.pages.models_gallery.subcategory_instrument",
            "polearm": "settings.pages.models_gallery.subcategory_polearm",
            "scythe": "settings.pages.models_gallery.subcategory_scythe",
            "shield": "settings.pages.models_gallery.subcategory_shield",
            "staff": "settings.pages.models_gallery.subcategory_staff",
            "sword": "settings.pages.models_gallery.subcategory_sword",
            "throwing": "settings.pages.models_gallery.subcategory_throwing",
            "two handed": "settings.pages.models_gallery.subcategory_two_handed",
            "weapons": "settings.pages.models_gallery.subcategory_weapons",
            "boats": "settings.pages.models_gallery.subcategory_boats",
            "deco": "settings.pages.models_gallery.subcategory_deco",
            "housing": "settings.pages.models_gallery.subcategory_housing",
            "misc": "settings.pages.models_gallery.subcategory_misc",
            "quiver": "settings.pages.models_gallery.subcategory_quiver",
            "siege": "settings.pages.models_gallery.subcategory_siege",
            "tents": "settings.pages.models_gallery.subcategory_tents",
            "world": "settings.pages.models_gallery.subcategory_world",
        }
        fallback = subcategory.capitalize()
        key = key_map.get(subcategory, "")
        result = self.lang.get(key, default=fallback)
        return result

    def _populate_filters(self):
        """Populate filter dropdowns with metadata."""
        from Functions.language_manager import lang

        # Handle empty metadata
        if not self.metadata:
            self.category_combo.clear()
            self.category_combo.addItem(
                lang.get("models_overview.category_placeholder", 
                        default="Select your category"), None
            )
            self.subcategory_combo.clear()
            return

        # Get categories from hierarchical structure
        # metadata['items'] = {'weapon': {'bow': [...], 'sword': [...]}, 'armor': {'helm': [...], ...}}
        items_data = self.metadata.get("items", {})
        
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        
        # Add placeholder as first item
        self.category_combo.addItem(
            lang.get("models_overview.category_placeholder", 
                    default="Select your category"), None
        )

        # Add categories to dropdown, sorted by name (no "-- All --" option)
        for category_name in sorted(items_data.keys()):
            if isinstance(items_data[category_name], dict):
                # Count total items in this category
                total_items = sum(
                    len(subcats) if isinstance(subcats, list) else 0
                    for subcats in items_data[category_name].values()
                )
                translated_label = self._get_category_label(category_name)
                display_name = f"{translated_label} ({total_items})"
                self.category_combo.addItem(display_name, category_name)

        self.category_combo.blockSignals(False)
        
        # Clear subcategories - do not populate until category is selected
        self.subcategory_combo.blockSignals(True)
        self.subcategory_combo.clear()
        self.subcategory_combo.blockSignals(False)

    def _populate_subcategories(self):
        """Update subcategory dropdown based on selected category."""
        from Functions.language_manager import lang
        
        items_data = self.metadata.get("items", {})
        selected_category = self.category_combo.currentData()
        
        self.subcategory_combo.blockSignals(True)
        self.subcategory_combo.clear()

        # If no category is selected (currentData() returns None for placeholder), keep subcategories empty
        if not selected_category:
            self.subcategory_combo.blockSignals(False)
            return

        # Add placeholder for subcategory selection
        self.subcategory_combo.addItem(
            lang.get("models_overview.subcategory_placeholder", 
                    default="Select your sub-category"), None
        )

        # If a category is selected, show its subcategories
        if selected_category in items_data:
            subcats = items_data[selected_category]
            if isinstance(subcats, dict):
                for subcat_name in sorted(subcats.keys()):
                    if subcat_name != "_":
                        model_ids = subcats[subcat_name]
                        count = len(model_ids) if isinstance(model_ids, list) else 0
                        translated_label = self._get_subcategory_label(subcat_name)
                        display_name = f"{translated_label} ({count})"
                        self.subcategory_combo.addItem(display_name, subcat_name)

        self.subcategory_combo.blockSignals(False)

    def _on_category_changed(self):
        """Handle category selection change - update subcategories only."""
        self._populate_subcategories()
        # Do NOT emit filter_changed - wait for user to select subcategory

    def _on_subcategory_changed(self):
        """Handle subcategory selection change - emit filter to load models."""
        self._emit_filter_change()

    def _emit_filter_change(self):
        """Emit the filter_changed signal with current values."""
        type_filter = "items"  # Always items
        subtype_filter = self.subcategory_combo.currentData()  # Get selected subtype (not None)
        
        # Only emit if a subcategory is actually selected
        if subtype_filter:
            search_query = self.search_input.text().strip()
            self.filter_changed.emit(type_filter, subtype_filter, search_query)

    def _on_search_changed(self):
        """Handle search input change."""
        pass  # Auto-trigger on apply

    def _on_apply_filters(self):
        """Emit filter_changed signal with current filter values."""
        self._emit_filter_change()

    def get_filters(self) -> tuple:
        """
        Get current filter values.

        Returns:
            Tuple of (type_filter, subtype_filter, search_query)
        """
        return (
            "items",
            self.subcategory_combo.currentData() or "",
            self.search_input.text().strip(),
        )

    def reset_filters(self):
        """Reset all filters to default state."""
        self.category_combo.setCurrentIndex(0)
        self.subcategory_combo.setCurrentIndex(0)
        self.search_input.clear()

    def update_metadata(self, metadata: dict):
        """
        Update metadata and refresh filter options.

        Args:
            metadata: Updated metadata dictionary
        """
        self.metadata = metadata
        self._populate_filters()
