"""
Models Database Editor Widget

Allows editing the models metadata database with:
- Creating new subtypes
- Editing entries to change subtypes
- Adding new images with subtypes
- Preview of images before assigning subtypes
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QSplitter, QGroupBox, QMessageBox,
    QFileDialog, QDialog as QFileSelectionDialog, QInputDialog,
    QProgressBar, QScrollArea, QFrame
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, QTimer

from Functions.language_manager import lang
from Functions.path_manager import PathManager, get_base_path


class ModelsDataDatabaseEditor(QDialog):
    """Main dialog for editing models database"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.get('models_db.viewer_btn', default="🔍 Database Editor"))
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        # Load metadata
        base_path = Path(get_base_path())
        self.metadata_path = base_path / "Data" / "models_metadata.json"
        self.models_dir = base_path / "Img" / "Models"
        self.metadata = self._load_metadata()
        
        # Load subtypes BEFORE creating UI
        self._load_subtypes()

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Toolbar with window controls
        toolbar_layout = QHBoxLayout()
        
        minimize_btn = QPushButton("➖")
        minimize_btn.setMaximumWidth(40)
        minimize_btn.clicked.connect(self.showMinimized)
        toolbar_layout.addWidget(minimize_btn)
        
        maximize_btn = QPushButton("⬜")
        maximize_btn.setMaximumWidth(40)
        maximize_btn.clicked.connect(self._toggle_maximize)
        toolbar_layout.addWidget(maximize_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Create tabs
        tabs = QTabWidget()
        
        # Tab 0: Missing Images
        missing_tab = self._create_missing_images_tab()
        tabs.addTab(missing_tab, "🚨 Missing Images")
        
        # Tab 1: Edit Entries
        edit_tab = self._create_edit_entries_tab()
        tabs.addTab(edit_tab, "📝 Edit Entries")

        # Tab 2: Add New Image
        add_tab = self._create_add_image_tab()
        tabs.addTab(add_tab, "➕ Add Image")

        # Tab 3: Manage Subtypes
        subtypes_tab = self._create_manage_subtypes_tab()
        tabs.addTab(subtypes_tab, "🏷️ Manage Subtypes")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self._save_metadata)
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        
        self.is_maximized = False

    def _toggle_maximize(self):
        """Toggle window maximize/restore"""
        if self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    def _create_missing_images_tab(self) -> QWidget:
        """Create tab for managing missing images (not in metadata)"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("🚨 Images Without Metadata"))

        # Scan for missing images
        scan_btn = QPushButton("🔍 Scan for Missing Images")
        scan_btn.clicked.connect(self._scan_missing_images)
        layout.addWidget(scan_btn)

        # List of missing images
        self.missing_images_list = QListWidget()
        self.missing_images_list.itemClicked.connect(self._on_missing_image_selected)
        layout.addWidget(self.missing_images_list)

        # Quick add panel
        add_group = QGroupBox("Quick Add to Database")
        add_layout = QVBoxLayout()

        add_layout.addWidget(QLabel("🖼️ Preview:"))
        self.missing_preview = QLabel()
        self.missing_preview.setMinimumSize(300, 300)
        self.missing_preview.setStyleSheet("border: 1px solid gray; background-color: #222;")
        self.missing_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_layout.addWidget(self.missing_preview)

        add_layout.addWidget(QLabel("Image Info:"))
        self.missing_info = QLabel()
        add_layout.addWidget(self.missing_info)

        add_layout.addWidget(QLabel("Entry ID:"))
        self.missing_id = QLineEdit()
        add_layout.addWidget(self.missing_id)

        add_layout.addWidget(QLabel("Name:"))
        self.missing_name = QLineEdit()
        add_layout.addWidget(self.missing_name)

        add_layout.addWidget(QLabel("Main Category:"))
        self.missing_main_cat = QComboBox()
        self.missing_main_cat.addItems(self._get_all_categories())
        add_layout.addWidget(self.missing_main_cat)

        add_layout.addWidget(QLabel("Subcategory:"))
        self.missing_subcat = QComboBox()
        self.missing_subcat.addItems(self._get_all_subtypes())
        add_layout.addWidget(self.missing_subcat)

        add_btn = QPushButton("✅ Add This Image to Database")
        add_btn.clicked.connect(self._add_missing_image_to_db)
        add_layout.addWidget(add_btn)

        skip_btn = QPushButton("⏭️ Skip This Image")
        skip_btn.clicked.connect(self._skip_missing_image)
        add_layout.addWidget(skip_btn)

        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        widget.setLayout(layout)
        return widget


    def _create_edit_entries_tab(self) -> QWidget:
        """Create tab for editing existing entries"""
        widget = QWidget()
        layout = QHBoxLayout()

        # Left side: List of entries
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📋 Entries:"))

        # Search/filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or ID...")
        self.search_input.textChanged.connect(self._filter_entries)
        search_layout.addWidget(self.search_input)

        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(self._get_all_categories())
        self.category_filter.currentTextChanged.connect(self._filter_entries)
        search_layout.addWidget(QLabel("Category:"))
        search_layout.addWidget(self.category_filter)

        left_layout.addLayout(search_layout)

        # List widget
        self.entries_list = QListWidget()
        self.entries_list.itemClicked.connect(self._on_entry_selected)
        left_layout.addWidget(self.entries_list)

        # Right side: Edit panel
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("🖼️ Preview:"))

        # Image preview
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #222;")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.preview_label)

        # Edit controls
        edit_group = QGroupBox("Edit Entry")
        edit_layout = QVBoxLayout()

        edit_layout.addWidget(QLabel("Entry ID:"))
        self.entry_id_label = QLabel()
        edit_layout.addWidget(self.entry_id_label)

        edit_layout.addWidget(QLabel("Name:"))
        self.entry_name = QLineEdit()
        self.entry_name.setReadOnly(True)
        edit_layout.addWidget(self.entry_name)

        edit_layout.addWidget(QLabel("Main Category:"))
        self.entry_main_cat = QLineEdit()
        self.entry_main_cat.setReadOnly(True)
        edit_layout.addWidget(self.entry_main_cat)

        edit_layout.addWidget(QLabel("Subcategory:"))
        self.entry_subcat = QComboBox()
        self.entry_subcat.currentTextChanged.connect(self._on_subcat_changed)
        edit_layout.addWidget(self.entry_subcat)

        edit_group.setLayout(edit_layout)
        right_layout.addWidget(edit_group)

        # Apply button
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.clicked.connect(self._apply_entry_changes)
        right_layout.addWidget(apply_btn)

        right_layout.addStretch()

        # Combine left and right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        widget.setLayout(layout)

        # Populate entries list
        self._populate_entries_list()

        return widget

    def _create_add_image_tab(self) -> QWidget:
        """Create tab for adding new images"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("➕ Add New Image to Database"))

        # Select image file
        file_group = QGroupBox("1️⃣ Select Image")
        file_layout = QVBoxLayout()

        self.selected_file_label = QLabel("No file selected")
        self.selected_file_label.setStyleSheet("padding: 10px; background-color: #333; border-radius: 4px;")
        file_layout.addWidget(self.selected_file_label)

        browse_btn = QPushButton("🗂️ Browse Images")
        browse_btn.clicked.connect(self._browse_image_file)
        file_layout.addWidget(browse_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Preview
        preview_group = QGroupBox("2️⃣ Preview")
        preview_layout = QVBoxLayout()

        self.add_preview_label = QLabel()
        self.add_preview_label.setMinimumSize(400, 400)
        self.add_preview_label.setStyleSheet("border: 1px solid gray; background-color: #222;")
        self.add_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.add_preview_label)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Entry details
        details_group = QGroupBox("3️⃣ Entry Details")
        details_layout = QVBoxLayout()

        details_layout.addWidget(QLabel("Entry ID:"))
        self.add_entry_id = QLineEdit()
        self.add_entry_id.setPlaceholderText("e.g., 132")
        details_layout.addWidget(self.add_entry_id)

        details_layout.addWidget(QLabel("Name:"))
        self.add_entry_name = QLineEdit()
        self.add_entry_name.setPlaceholderText("e.g., Briton Longbow")
        details_layout.addWidget(self.add_entry_name)

        details_layout.addWidget(QLabel("Main Category:"))
        self.add_main_cat = QComboBox()
        self.add_main_cat.addItems(self._get_all_categories())
        details_layout.addWidget(self.add_main_cat)

        details_layout.addWidget(QLabel("Subcategory:"))
        self.add_subcat = QComboBox()
        self.add_subcat.addItems(self._get_all_subtypes())
        details_layout.addWidget(self.add_subcat)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Add button
        add_btn = QPushButton("✅ Add Image to Database")
        add_btn.clicked.connect(self._add_image_to_db)
        layout.addWidget(add_btn)

        layout.addStretch()
        widget.setLayout(layout)

        return widget

    def _create_manage_subtypes_tab(self) -> QWidget:
        """Create tab for managing subtypes"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("🏷️ Manage Subtypes"))

        # List of subtypes
        layout.addWidget(QLabel("Current Subtypes:"))
        self.subtypes_list = QListWidget()
        self.subtypes_list.itemClicked.connect(self._on_subtype_selected)
        layout.addWidget(self.subtypes_list)

        # Add new subtype
        add_group = QGroupBox("Add New Subtype")
        add_layout = QVBoxLayout()

        add_layout.addWidget(QLabel("Subtype Name:"))
        self.new_subtype_input = QLineEdit()
        self.new_subtype_input.setPlaceholderText("e.g., Axe, Sword, Shield...")
        add_layout.addWidget(self.new_subtype_input)

        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        # Buttons
        button_layout = QHBoxLayout()

        create_btn = QPushButton("➕ Create New Subtype")
        create_btn.clicked.connect(self._create_new_subtype)
        button_layout.addWidget(create_btn)

        delete_btn = QPushButton("❌ Delete Selected Subtype")
        delete_btn.clicked.connect(self._delete_subtype)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from JSON file"""
        try:
            if not self.metadata_path.exists():
                QMessageBox.warning(self, "Warning", f"Metadata file not found: {self.metadata_path}")
                return {}
            
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load metadata: {e}")
            return {}

    def _load_subtypes(self):
        """Load all available subtypes"""
        self.subtypes = set()
        for category in self.metadata.values():
            for entry in category.values():
                if isinstance(entry, dict) and 'subcategory' in entry:
                    self.subtypes.add(entry['subcategory'])
        self.subtypes = sorted(list(self.subtypes))

    def _get_all_categories(self) -> List[str]:
        """Get all main categories"""
        categories = set()
        for category in self.metadata.values():
            for entry in category.values():
                if isinstance(entry, dict) and 'main_category' in entry:
                    categories.add(entry['main_category'])
        return sorted(list(categories))

    def _get_all_subtypes(self) -> List[str]:
        """Get all subtypes"""
        return self.subtypes + ["<New Subtype...>"]

    def _populate_entries_list(self):
        """Populate the entries list"""
        self.entries_list.clear()
        self.all_entries = []

        for category_name, entries in self.metadata.items():
            for entry_id, entry_data in entries.items():
                if isinstance(entry_data, dict):
                    name = entry_data.get('name', 'Unknown')
                    subcat = entry_data.get('subcategory', 'Unknown')
                    self.all_entries.append({
                        'category': category_name,
                        'id': entry_id,
                        'name': name,
                        'main_category': entry_data.get('main_category', ''),
                        'subcategory': subcat
                    })

        self._filter_entries()

    def _filter_entries(self):
        """Filter entries based on search and category"""
        self.entries_list.clear()
        search_text = self.search_input.text().lower()
        category_filter = self.category_filter.currentText()

        for entry in self.all_entries:
            # Filter by category
            if category_filter != "All Categories" and entry['main_category'] != category_filter:
                continue

            # Filter by search text
            if search_text and search_text not in entry['name'].lower() and search_text not in entry['id'].lower():
                continue

            item = QListWidgetItem(f"{entry['id']} - {entry['name']} ({entry['subcategory']})")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.entries_list.addItem(item)

    def _on_entry_selected(self, item: QListWidgetItem):
        """Handle entry selection"""
        entry = item.data(Qt.ItemDataRole.UserRole)

        self.current_entry = entry
        self.entry_id_label.setText(entry['id'])
        self.entry_name.setText(entry['name'])
        self.entry_main_cat.setText(entry['main_category'])

        # Load preview image
        self._load_entry_preview(entry)

        # Update subcategory combo
        self.entry_subcat.blockSignals(True)
        self.entry_subcat.clear()
        self.entry_subcat.addItems(self._get_all_subtypes())
        self.entry_subcat.setCurrentText(entry['subcategory'])
        self.entry_subcat.blockSignals(False)

    def _load_entry_preview(self, entry: Dict[str, str]):
        """Load preview image for entry"""
        category_dir = self.models_dir / entry['category']
        image_path = category_dir / f"{entry['id']}.webp"

        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            scaled_pixmap = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText(f"Image not found:\n{image_path}")

    def _on_subcat_changed(self, text: str):
        """Handle subcategory change"""
        if text == "<New Subtype...>":
            new_subtype, ok = QInputDialog.getText(
                self,
                "New Subtype",
                "Enter new subcategory name:"
            )
            if ok and new_subtype:
                self.subtypes.append(new_subtype)
                self.entry_subcat.blockSignals(True)
                self.entry_subcat.setCurrentText(new_subtype)
                self.entry_subcat.blockSignals(False)

    def _apply_entry_changes(self):
        """Apply changes to current entry"""
        if not hasattr(self, 'current_entry'):
            QMessageBox.warning(self, "Warning", "No entry selected")
            return

        new_subcat = self.entry_subcat.currentText()
        category = self.current_entry['category']
        entry_id = self.current_entry['id']

        self.metadata[category][entry_id]['subcategory'] = new_subcat
        self.current_entry['subcategory'] = new_subcat

        QMessageBox.information(self, "Success", f"Entry {entry_id} updated successfully!")
        self._populate_entries_list()

    def _browse_image_file(self):
        """Browse for image file"""
        file_dialog = QFileDialog()
        start_dir = str(self.models_dir) if self.models_dir.exists() else str(Path.home())
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Image",
            start_dir,
            "Image Files (*.webp *.jpg *.png);;All Files (*)"
        )

        if file_path:
            self.selected_image_path = file_path
            self.selected_file_label.setText(f"Selected: {Path(file_path).name}")

            # Load preview
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            self.add_preview_label.setPixmap(scaled)

    def _add_image_to_db(self):
        """Add selected image to database"""
        if not hasattr(self, 'selected_image_path'):
            QMessageBox.warning(self, "Warning", "No image selected")
            return

        entry_id = self.add_entry_id.text().strip()
        entry_name = self.add_entry_name.text().strip()
        main_cat = self.add_main_cat.currentText()
        subcat = self.add_subcat.currentText()

        if not all([entry_id, entry_name]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields")
            return

        # Add to metadata
        if main_cat not in self.metadata:
            self.metadata[main_cat] = {}

        self.metadata[main_cat][entry_id] = {
            'name': entry_name,
            'main_category': main_cat,
            'subcategory': subcat,
            'source_url': ''
        }

        QMessageBox.information(self, "Success", f"Entry {entry_id} added successfully!")
        self._populate_entries_list()
        self.add_entry_id.clear()
        self.add_entry_name.clear()
        self.add_preview_label.clear()
        self.selected_file_label.setText("No file selected")

    def _populate_subtypes_list(self):
        """Populate subtypes list"""
        self.subtypes_list.clear()
        for subtype in self.subtypes:
            self.subtypes_list.addItem(subtype)

    def _on_subtype_selected(self, item: QListWidgetItem):
        """Handle subtype selection"""
        self.selected_subtype = item.text()

    def _create_new_subtype(self):
        """Create new subtype"""
        name = self.new_subtype_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a subtype name")
            return

        if name in self.subtypes:
            QMessageBox.warning(self, "Warning", "This subtype already exists")
            return

        self.subtypes.append(name)
        self.subtypes.sort()
        self._populate_subtypes_list()
        self.new_subtype_input.clear()

        QMessageBox.information(self, "Success", f"Subtype '{name}' created!")

    def _delete_subtype(self):
        """Delete selected subtype"""
        if not hasattr(self, 'selected_subtype'):
            QMessageBox.warning(self, "Warning", "No subtype selected")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete subtype '{self.selected_subtype}'?\n\nEntries using this subtype will not be deleted."
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.subtypes.remove(self.selected_subtype)
            self._populate_subtypes_list()
            QMessageBox.information(self, "Success", "Subtype deleted!")

    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Success", "Database saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save database: {e}")

    def closeEvent(self, event):
        """Handle dialog close"""
        reply = QMessageBox.question(
            self,
            "Save Changes?",
            "Do you want to save your changes before closing?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._save_metadata()

        event.accept()
    def _scan_missing_images(self):
        """Scan for images that don't have metadata entries"""
        self.missing_images_list.clear()
        self.missing_images = []

        # Get all image files from the directories
        for category_dir in ["items", "mobs", "icons"]:
            full_dir = self.models_dir / category_dir
            if not full_dir.exists():
                continue

            for image_file in full_dir.glob("*.webp"):
                image_id = image_file.stem  # Get filename without extension
                
                # Check if this ID exists in metadata
                found = False
                for category in self.metadata.values():
                    if image_id in category:
                        found = True
                        break

                if not found:
                    self.missing_images.append({
                        'id': image_id,
                        'file': image_file,
                        'category': category_dir,
                        'file_size': image_file.stat().st_size
                    })

        # Display missing images
        for img in sorted(self.missing_images, key=lambda x: x['id']):
            item = QListWidgetItem(f"{img['id']} ({img['category']})")
            item.setData(Qt.ItemDataRole.UserRole, img)
            self.missing_images_list.addItem(item)

        QMessageBox.information(self, "Scan Complete", f"Found {len(self.missing_images)} images without metadata")

    def _on_missing_image_selected(self, item: QListWidgetItem):
        """Handle missing image selection"""
        img = item.data(Qt.ItemDataRole.UserRole)
        self.current_missing_image = img

        # Load preview
        pixmap = QPixmap(str(img['file']))
        scaled = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
        self.missing_preview.setPixmap(scaled)

        # Display info
        file_size_kb = img['file_size'] / 1024
        info = f"File: {img['file'].name}\nSize: {file_size_kb:.1f} KB\nCategory: {img['category']}"
        self.missing_info.setText(info)

        # Pre-fill ID
        self.missing_id.setText(img['id'])
        self.missing_name.clear()

    def _add_missing_image_to_db(self):
        """Add the selected missing image to database"""
        if not hasattr(self, 'current_missing_image'):
            QMessageBox.warning(self, "Warning", "No image selected")
            return

        entry_id = self.missing_id.text().strip()
        entry_name = self.missing_name.text().strip()
        main_cat = self.missing_main_cat.currentText()
        subcat = self.missing_subcat.currentText()

        if not entry_name:
            QMessageBox.warning(self, "Warning", "Please enter an image name")
            return

        # Add to metadata
        if main_cat not in self.metadata:
            self.metadata[main_cat] = {}

        self.metadata[main_cat][entry_id] = {
            'name': entry_name,
            'main_category': main_cat,
            'subcategory': subcat,
            'source_url': ''
        }

        QMessageBox.information(self, "Success", f"Image {entry_id} added to database!")
        self._skip_missing_image()

    def _skip_missing_image(self):
        """Skip current missing image and move to next"""
        current_row = self.missing_images_list.currentRow()
        if current_row >= 0:
            self.missing_images_list.takeItem(current_row)
            
            # Select next item
            if self.missing_images_list.count() > 0:
                self.missing_images_list.setCurrentRow(min(current_row, self.missing_images_list.count() - 1))
                self.missing_images_list.itemClicked.emit(self.missing_images_list.currentItem())
            else:
                self.missing_preview.clear()
                self.missing_info.setText("No more images")