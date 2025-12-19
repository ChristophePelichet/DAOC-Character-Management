# 🖼️ Model Visual System - Technical Documentation

**Version**: 1.0
**Date**: November 2025  
**Last Updated**: December 19, 2025 (Item Model Viewer Module - Phase 10)  
**Component**: Complete model management system (3 types: Items, Mobs, Icons)  
**Used by**: Armory, Database Editor, Character Sheet, Item Preview, Model Viewer Dialog  
**Related**: `Img/Models/`, `Tools/DataScraping/download_all_models.py`, `Tools/DataScraping/scrape_models_metadata.py`, `Data/models_metadata.json`, `UI/model_viewer_dialog.py`, `Functions/item_model_viewer.py`  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Image Repository](#image-repository)
4. [Download & Conversion Tool](#download--conversion-tool)
5. [File Storage Structure](#file-storage-structure)
6. [Integration Guide](#integration-guide)
7. [PyInstaller Compatibility](#pyinstaller-compatibility)
8. [Maintenance & Updates](#maintenance--updates)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Model Visual System provides **offline access to 4814+ model images** across 3 categories for complete visual preview throughout the application. This comprehensive system includes items, mobs, and inventory icons with full metadata and categorization.

### Key Features

- ✅ **3444 total item model images** from DAOC game data (IDs 1-5000)
  - **3444 Item models**: Complete coverage of all available weapons, armor, equipment
  - **1000 Mob models**: NPCs, creatures, enemies
  - **370 Inventory icons**: Item icons for UI
- ✅ **Complete metadata system**: 838 models with names and categories
- ✅ **Unified scraping tool**: `scrape_all_daoc_data.py` for all data sources
- ✅ **Offline-first**: All images embedded in application
- ✅ **Optimized format**: WebP compression (63% size reduction for items)
- ✅ **Compact footprint**: ~15 MB total for all images
- ✅ **PyInstaller compatible**: Works with `--onefile` and `--onedir`
- ✅ **Smart categorization**: 25 item subcategories, 8 mob types
- ✅ **Automatic updates**: Professional scraping tool for metadata refresh

### Design Principles

1. **Comprehensive**: Complete coverage of all model types
2. **Professional**: Robust scraping with cache, retry, pagination
3. **Metadata-driven**: Rich categorization (main_category + subcategory)
4. **Performance**: WebP format, caching, smart indexing
5. **Offline**: No network dependency after initial setup
6. **Maintainability**: Automated scraper for easy updates

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         METADATA SYSTEM (models_metadata.json)                   │
│  {                                                               │
│    "items": {                                                    │
│      "132": {                                                    │
│        "name": "briton longbow",                                 │
│        "main_category": "Weapon",                                │
│        "subcategory": "Bow",                                     │
│        "source_url": "..."                                       │
│      }                                                           │
│    },                                                            │
│    "mobs": { ... },                                              │
│    "icons": { ... }                                              │
│  }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              MODEL VISUAL SYSTEM (This System)                   │
│                                                                  │
│  Type: "items", Model ID: "132"                                  │
│      ↓                                                           │
│  Image Path: Img/Models/items/132.webp                           │
│  Metadata: {"name": "briton longbow", "category": "Weapon/Bow"} │
│      ↓                                                           │
│  QPixmap / Display in UI with tooltip                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            IMAGE STORAGE (Img/Models/)                           │
│  items/     : 3444 files | 10.48 MB                              │
│  mobs/      : 1000 files | 4.86 MB                               │
│  icons/items/ : 370 files | 0.18 MB                              │
│  Total: 4814 files | 15.52 MB                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Model Lookup**: Application queries metadata by model ID
2. **Metadata Retrieval**: Get name, category, subcategory from JSON
3. **Path Construction**: `Img/Models/{type}/{model_id}.webp`
4. **Image Loading**: QPixmap loads the WebP image
5. **Rich Display**: Image + name + category in UI (preview, tooltip, etc.)

### Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Image Library (Items)** | 3444 WebP item model images | `Img/Models/items/*.webp` |
| **Image Library (Mobs)** | 1000 WebP mob model images | `Img/Models/mobs/*.webp` |
| **Image Library (Icons)** | 370 WebP inventory icons | `Img/Models/icons/items/*.webp` |
| **Metadata Database** | Model names and categories (838 models) | `Data/models_metadata.json` |
| **Unified Scraper** | Complete data scraper (armor, ranks, models) | `Tools/DataScraping/scrape_all_daoc_data.py` |
| **Download Script** | Download all 3 types from GitHub | `Tools/DataScraping/download_all_models.py` |
| **Metadata Scraper** | Professional scraper with categorization | `Tools/DataScraping/scrape_models_metadata.py` |
| **Item Database** | Item data with model IDs | `Data/items_database_src.json` |
| **Model Viewer Dialog** | Reusable UI component for model display | `UI/model_viewer_dialog.py` |

---

## Image Repository

### Source Repository

**GitHub Repository**: [Eve-of-Darkness/DolModels](https://github.com/Eve-of-Darkness/DolModels)

- **License**: Open source (Dawn of Light project)
- **Paths**: 
  - Items: `src/items/`
  - Mobs: `src/mobs/`
  - Icons: `src/icons/items/`
- **Format**: JPG images
- **Total Files**: 4814+ images (3444 items, 1000 mobs, 370+ icons)
- **Raw URL Pattern**: `https://raw.githubusercontent.com/Eve-of-Darkness/DolModels/master/src/{type}/{ID}.jpg`

**Example URLs**:
```
https://github.com/Eve-of-Darkness/DolModels/raw/master/src/items/132.jpg
https://github.com/Eve-of-Darkness/DolModels/raw/master/src/mobs/1.jpg
https://github.com/Eve-of-Darkness/DolModels/raw/master/src/icons/items/1200.jpg
```

### Los Ojos Website

**Metadata Source**: [Los Ojos Model Viewer](https://daoc.ndlp.info/losojos-001-site1.btempurl.com/ModelViewer/)

- **Purpose**: Model names and categorization
- **Pages**: ItemModels.html, MobModels.html, InventoryModels.html
- **Structure**: Static HTML with hash-based category URLs
- **Features**: Pagination, filtering, model names
- **Scraping Method**: Professional scraper with cache and retry logic

### Image Characteristics

**Original Format (JPG)**:
- Total size: 13.84 MB
- Format: JPEG
- Quality: Variable

**Converted Format (WebP)**:
- Total size: 9.65 MB
- Format: WebP
- Quality: 80% (optimal balance)
- Compression method: 6 (best)
- **Size reduction: 30.2%**

**Breakdown by Type**:
| Type | Files | Original (JPG) | Converted (WebP) | Reduction |
|------|-------|----------------|------------------|-----------|
| Items | 1000 | 12.05 MB | 4.60 MB | 61.8% |
| Mobs | 1000 | ~7 MB | 4.86 MB | ~30% |
| Icons | 370 | ~1 MB | 0.18 MB | ~82% |
| **Total** | **2370** | **~13.84 MB** | **9.65 MB** | **30.2%** |

---

## Download & Conversion Tool

### Script: `download_all_models.py`

**Location**: `Tools/DataScraping/download_all_models.py`

**Purpose**: Download all model images (Items, Mobs, Icons) from GitHub and convert them to optimized WebP format.

### Usage

**Basic Usage** (download all 3 types):
```bash
python Tools/DataScraping/download_all_models.py
```

**Download Specific Type**:
```bash
python Tools/DataScraping/download_all_models.py --types items
python Tools/DataScraping/download_all_models.py --types mobs icons
```

**Force Re-download** (overwrite existing):
```bash
python Tools/DataScraping/download_all_models.py --force
```

**Custom Quality** (adjust WebP compression):
```bash
python Tools/DataScraping/download_all_models.py --quality 90
```

**Help**:
```bash
python Tools/DataScraping/download_all_models.py --help
```

### Features

✅ **Multi-Type Support**: Downloads items, mobs, and icons  
✅ **Smart Resume**: Skips already downloaded files (unless `--force`)  
✅ **Progress Tracking**: Real-time stats per type (processed, failed, size savings)  
✅ **Error Handling**: Automatic retry (3 attempts) with exponential backoff  
✅ **Parallel Downloads**: Efficient batch processing  
✅ **WebP Optimization**: Quality 80%, method 6 (best compression)  
✅ **Statistics**: Final report with size comparison per type

### Model Types Configuration

```python
MODEL_TYPES = {
    'items': {
        'github_path': 'src/items',
        'output_dir': 'Img/Models/items',
        'count': 1000,
        'description': 'Item models (weapons, armor, equipment)'
    },
    'mobs': {
        'github_path': 'src/mobs',
        'output_dir': 'Img/Models/mobs',
        'count': 1000,
        'description': 'Mob models (NPCs, creatures, enemies)'
    },
    'icons': {
        'github_path': 'src/icons/items',
        'output_dir': 'Img/Models/icons/items',
        'count': 370,
        'description': 'Inventory icons'
    }
}
```

### Example Output

```
============================================================
All Model Types Downloader & Converter
============================================================
Will process: items, mobs, icons
WebP quality: 80%
Force re-download: False
============================================================

Processing MODEL TYPE: items
------------------------------------------------------------
[1/1000] Downloading 1.jpg...
Converting to WebP (quality=80)...
✅ 1: 8.5 KB → 2.4 KB (71.8% reduction)

[2/1000] Downloading 2.jpg...
✅ 2: 9.2 KB → 2.7 KB (70.7% reduction)
...
[1000/1000] Complete
------------------------------------------------------------
ITEMS Summary:
  Total: 1000 | Downloaded: 1000 | Skipped: 0 | Failed: 0
  Original: 12.05 MB → Converted: 4.60 MB (61.8% reduction)

Processing MODEL TYPE: mobs
------------------------------------------------------------
[1/1000] Downloading 1.jpg...
...
MOBS Summary:
  Total: 1000 | Downloaded: 1000 | Skipped: 0 | Failed: 0
  Original: ~7 MB → Converted: 4.86 MB (30% reduction)

Processing MODEL TYPE: icons
------------------------------------------------------------
[1/370] Downloading 1200.jpg...
...
ICONS Summary:
  Total: 370 | Downloaded: 370 | Skipped: 0 | Failed: 0
  Original: ~1 MB → Converted: 0.18 MB (82% reduction)

============================================================
GRAND TOTAL
============================================================
Total files: 2370
Downloaded: 2370 new | Skipped: 0 existing | Failed: 0
Original size: ~13.84 MB
Converted size: 9.65 MB
Overall reduction: 30.2%
============================================================
✅ All model types processed successfully!
```

---

## File Storage Structure

### Directory Layout

```
Img/
└── Models/
    └── items/              # Item model images (3444 files)
        ├── 1.webp          # Briton dagger
        ├── 2.webp          # Briton hand axe
        ├── 3.webp          # Briton short sword
        ├── 4.webp          # Briton longsword
        ├── ...
        ├── 14.webp         # Flanged Mace (Cudgel of the Undead model)
        ├── ...
        ├── 3908.webp       # Example mid-range model
        ├── ...
        ├── 4063.webp       # Cloth Cap model
        ├── ...
        └── 4257.webp       # Last available model
```

### File Naming Convention

**Pattern**: `{model_id}.webp`

**Examples**:
- Model ID `1` → `1.webp`
- Model ID `14` → `14.webp`
- Model ID `4063` → `4063.webp`
- Model ID `2238` → `2238.webp`

**Why this naming?**:
- ✅ Direct mapping from database `model` field
- ✅ No index file needed
- ✅ Simple path construction: `f"{model_id}.webp"`
- ✅ Easy to verify/debug (ID visible in filename)

### Git Tracking

**Status**: Images are **tracked in Git**

**Rationale**:
- Small total size (4.60 MB)
- Essential for offline functionality
- Embedded in compiled application
- No dynamic download needed

**.gitignore**: No exclusions for `Img/Models/`

---

## Metadata Scraper

### Script: `scrape_models_metadata.py`

**Location**: `Tools/DataScraping/scrape_models_metadata.py`

**Purpose**: Professional scraper that extracts model metadata (names, categories, subcategories) from Los Ojos website.

### Usage

**Basic Usage** (scrape all):
```bash
python Tools/DataScraping/scrape_models_metadata.py
```

**With Cache** (faster re-runs):
```bash
python Tools/DataScraping/scrape_models_metadata.py --cache
```

**Force Fresh Scrape**:
```bash
python Tools/DataScraping/scrape_models_metadata.py --force
```

### Features

✅ **Professional Architecture**: Robust error handling, retry logic, progress tracking  
✅ **Cache System**: MD5-hashed pages in `.cache/scraping/` for fast re-runs  
✅ **Automatic Categorization**: Extracts main_category + subcategory from website  
✅ **Pagination Support**: Handles multi-page results (up to 22 pages per category)  
✅ **Duplicate Detection**: Prevents overwrites, tracks skipped duplicates  
✅ **3 Model Types**: Items, Mobs, Icons with separate processing  
✅ **Smart URL Extraction**: Discovers hash-based category URLs from main pages  
✅ **Statistics Reporting**: Complete breakdown by category with success/fail counts

### Output Format

**File**: `Data/models_metadata.json`

**Structure**:
```json
{
  "items": {
    "132": {
      "name": "briton longbow",
      "main_category": "Weapon",
      "subcategory": "Bow",
      "source_url": "http://github.com/Eve-of-Darkness/DolModels/raw/master/src/items/132.jpg"
    },
    "471": {
      "name": "Recurve Bow",
      "main_category": "Weapon",
      "subcategory": "Bow",
      "source_url": "..."
    }
  },
  "mobs": {
    "1": {
      "name": "Demon",
      "main_category": "Biped",
      "subcategory": "BipedMale",
      "source_url": "..."
    }
  },
  "icons": {
    "1200": {
      "name": "leather cap",
      "main_category": "Inventory",
      "subcategory": "Icons",
      "source_url": "..."
    }
  }
}
```

### Metadata Statistics

**Total Models**: 838 (with names and categories)
- **Items**: 595 models
  - 25 subcategories (Bow, Sword, Dagger, Shield, Staff, Helm, Chest, etc.)
  - Example: 28 Bows, 308 Swords, 308 Feet armor, etc.
- **Mobs**: 193 models
  - 8 subcategories (BipedMale, BipedFemale, VampiirMale, Demon, Animal, etc.)
- **Icons**: 50 models
  - Inventory category only

### Item Subcategories (25 total)

**Weapons**:
- Bow (28 items)
- Crossbow (16 items)
- Dagger (28 items)
- Flexible (28 items)
- Greave (28 items)
- Instrument (28 items)
- Polearm (28 items)
- Scythe (22 items)
- Shield (28 items)
- Staff (28 items)
- Sword (28 items)
- Throwing (3 items)
- Two Handed (28 items)

**Armor**:
- Cloak (28 items)
- Feet (28 items)
- Hands (28 items)
- Helm (28 items)
- Chest (28 items)
- Legs (28 items)
- Sleeves (28 items)

**Other**:
- Housing (28 items)
- Siege (25 items)
- World (25 items)

### Example Scraping Session

```
============================================================
PROFESSIONAL MODELS METADATA SCRAPER
============================================================
Cache enabled: True
Force re-scrape: False

============================================================
SCRAPING ITEM MODELS
============================================================
Extracting category structure from main page...
Found 2 main categories

Category: Weapon
  Scraping subcategory: Bow (Weapon)
    Page 1: 28 items
    Page 2: 28 items
    Page 3: 28 items
    Total for Bow: 84 items
  
  Scraping subcategory: Sword (Weapon)
    Page 1: 28 items
    Page 2: 28 items
    ... (11 pages total)
    Total for Sword: 308 items

Total Items Scraped: 595

============================================================
SCRAPING MOB MODELS
============================================================
Extracting mob category structure from main page...
Found 2 mob categories

Mob Category: Biped
  Scraping mob category: BipedMale
    Total: 28 mobs
  Scraping mob category: BipedFemale
    Total: 28 mobs

Total Mobs Scraped: 193

============================================================
SCRAPING INVENTORY ICONS
============================================================
Total Icons Scraped: 50

============================================================
SCRAPING SUMMARY
============================================================

ITEMS:
  Total:   595
  Success: 595
  Failed:  0
  Skipped: 3195

MOBS:
  Total:   193
  Success: 193
  Failed:  0
  Skipped: 0

ICONS:
  Total:   50
  Success: 50
  Failed:  0
  Skipped: 0

GRAND TOTAL: 838 models
============================================================

[SUCCESS] Scraping completed successfully in 154.2 seconds!
```

---

## Integration Guide

### Model Viewer Dialog (NEW)

**Component**: `UI/model_viewer_dialog.py`

**Purpose**: Reusable dialog component for displaying item model images with metadata.

**Features**:
- ✅ Displays embedded WebP images from `Img/Models/items/`
- ✅ Shows item name, model ID, and category
- ✅ Auto-scales image to fit window with aspect ratio preservation
- ✅ Handles missing images gracefully
- ✅ Modern UI with dark theme
- ✅ Multilingual support via `lang.get()`
- ✅ Window resize support
- ✅ Non-modal window (doesn't block other dialogs)
- ✅ Supports both 'model_id' and 'model' database fields

**Usage**:

```python
from UI.model_viewer_dialog import ModelViewerDialog

# Basic usage (minimal parameters)
dialog = ModelViewerDialog(
    parent=self,
    model_id="4063"
)
dialog.show()  # Non-modal - doesn't block other windows

# Full usage (with metadata)
dialog = ModelViewerDialog(
    parent=self,
    model_id="4063",
    item_name="Cloth Cap",
    model_category="Armor/Helm"
)
dialog.show()  # Non-modal - doesn't block other windows
```

**Integration in Armory Dialog**:

```python
def _show_item_model(self, item_name):
    """Show model image for the specified item."""
    # Search for item in database with realm fallback
    item_data = self.db_manager.search_item(item_name)
    
    if not item_data:
        # Try with realm suffix
        search_key = f"{item_name.lower()}:{self.realm.lower()}"
        item_data = self.db_manager.search_item(search_key)
    
    if not item_data:
        # Try with :all suffix
        search_key = f"{item_name.lower()}:all"
        item_data = self.db_manager.search_item(search_key)
    
    # Support both 'model_id' and 'model' fields
    model_id = item_data.get('model_id') or item_data.get('model') if item_data else None
    
    if model_id:
        model_category = item_data.get('model_category', 'items')
        
        # Show model viewer dialog (non-modal)
        from UI.model_viewer_dialog import ModelViewerDialog
        dialog = ModelViewerDialog(
            self,
            model_id=model_id,
            item_name=item_name,
            model_category=model_category
        )
        dialog.show()  # Non-modal - doesn't block armory dialog
```

**Clickable Model Icons in Template Preview**:

```python
# In ArmorManagementDialog class
MODEL_SLOTS = {
    'Torso', 'Arms', 'Legs', 'Hands', 'Feet', 'Helmet',  # Armor
    'Cloak',                                              # Cape
    'Two Handed', 'Right Hand', 'Left Hand'              # Weapons
}

# Generate clickable model icon in HTML preview
if item['slot'] in self.MODEL_SLOTS:
    model_icon = f'<a href="model:{item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
    item_text = f"{model_icon}{item['name']} ({item['slot']})"

# Handle click event
self.preview_area.setOpenExternalLinks(False)  # Handle clicks internally
self.preview_area.setOpenLinks(False)  # Prevent default link navigation
self.preview_area.anchorClicked.connect(self._on_model_link_clicked)

def _on_model_link_clicked(self, url):
    """Handle click on model viewer link."""
    if url.scheme() == "model":
        item_name = url.path()
        # Open model viewer without changing current selection/preview
        self._show_item_model(item_name)
        # Prevent default link navigation that would clear the preview
        return
```

### Basic Integration

**Step 1: Get Model ID from Database**

```python
# From item data
item_data = database["items"]["cloth cap:hibernia"]
model_id = item_data.get("model")  # "4063"
```

**Step 2: Load Metadata**

```python
import json
from pathlib import Path

def load_models_metadata() -> dict:
    """Load models metadata from JSON file."""
    metadata_path = Path("Data/models_metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Usage
metadata = load_models_metadata()

# Access item metadata
item_meta = metadata["items"].get(model_id)
if item_meta:
    name = item_meta["name"]              # "cloth cap"
    category = item_meta["main_category"]  # "Armor"
    subcat = item_meta["subcategory"]     # "Helm"
```

**Step 3: Construct Image Path**

```python
from pathlib import Path

def get_model_image_path(model_id: str, model_type: str = "items") -> Path:
    """
    Get image path from model ID.
    
    Args:
        model_id: Model ID from database (e.g., "4063")
        model_type: Type of model - "items", "mobs", or "icons"
        
    Returns:
        Path to WebP image
    """
    return Path(f"Img/Models/{model_type}") / f"{model_id}.webp"

# Usage
image_path = get_model_image_path("4063", "items")
# Returns: Img/Models/items/4063.webp

mob_path = get_model_image_path("1", "mobs")
# Returns: Img/Models/mobs/1.webp
```

**Step 4: Load and Display Image with Rich Info**

```python
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

def display_model_preview(label: QLabel, model_id: str, model_type: str = "items"):
    """
    Display model image with tooltip containing metadata.
    
    Args:
        label: QLabel widget to display image
        model_id: Model ID from database
        model_type: Type of model ("items", "mobs", or "icons")
    """
    if not model_id:
        label.setText("No preview")
        return
    
    # Load metadata
    metadata = load_models_metadata()
    model_meta = metadata.get(model_type, {}).get(model_id)
    
    # Construct path
    image_path = get_model_image_path(model_id, model_type)
    
    if image_path.exists():
        pixmap = QPixmap(str(image_path))
        
        # Scale to fit
        label.setPixmap(pixmap.scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        
        # Set rich tooltip with metadata
        if model_meta:
            tooltip = f"""
            <b>{model_meta['name']}</b><br>
            Category: {model_meta['main_category']} / {model_meta['subcategory']}<br>
            Model ID: {model_id}
            """
            label.setToolTip(tooltip)
    else:
        label.setText(f"Model {model_id}\n(No image)")

# Usage
preview_label = QLabel()
display_model_preview(preview_label, "4063", "items")
```

### Advanced Integration

**With Fallback Image**:

```python
from pathlib import Path
from PySide6.QtGui import QPixmap

def get_model_pixmap(model_id: str, model_type: str = "items", 
                     fallback_path: str = "Img/default_item.png") -> QPixmap:
    """
    Get QPixmap for model with fallback.
    
    Args:
        model_id: Model ID from database
        model_type: Type of model ("items", "mobs", or "icons")
        fallback_path: Path to default image if model not found
        
    Returns:
        QPixmap (model image or fallback)
    """
    if model_id:
        image_path = Path(f"Img/Models/{model_type}/{model_id}.webp")
        if image_path.exists():
            return QPixmap(str(image_path))
    
    # Fallback
    return QPixmap(fallback_path)
```

**With Caching** (performance optimization):

```python
from functools import lru_cache
from PySide6.QtGui import QPixmap

@lru_cache(maxsize=200)
def get_cached_model_pixmap(model_id: str, model_type: str = "items") -> QPixmap:
    """
    Get cached QPixmap for model (avoid re-loading same image).
    
    Args:
        model_id: Model ID from database
        model_type: Type of model ("items", "mobs", or "icons")
        
    Returns:
        Cached QPixmap
    """
    image_path = Path(f"Img/Models/{model_type}/{model_id}.webp")
    if image_path.exists():
        return QPixmap(str(image_path))
    return QPixmap()  # Empty pixmap
```

**Tooltip Preview with Metadata**:

```python
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap

def set_model_tooltip_with_preview(widget: QWidget, model_id: str, model_type: str = "items"):
    """
    Set tooltip with model name, category, and image preview.
    
    Args:
        widget: Widget to add tooltip to
        model_id: Model ID
        model_type: Type of model ("items", "mobs", or "icons")
    """
    # Load metadata
    metadata = load_models_metadata()
    model_meta = metadata.get(model_type, {}).get(model_id)
    
    if model_meta:
        tooltip_html = f"""
        <div style="text-align: center;">
            <img src="Img/Models/{model_type}/{model_id}.webp" width="64" height="64">
            <br>
            <b>{model_meta['name']}</b><br>
            <i>{model_meta['main_category']} / {model_meta['subcategory']}</i>
        </div>
        """
        widget.setToolTip(tooltip_html)
```

### Usage Examples

**In Armory Import Dialog**:
```python
# Show preview when item selected
def on_item_selected(self, item_data):
    model_id = item_data.get("model")
    self.preview_label.clear()
    
    if model_id:
        display_model_preview(self.preview_label, model_id, "items")
```

**In Database Editor** (current implementation):
```python
# Preview button in table row
def _view_model_image(self):
    """Open dialog with large model image preview."""
    model_id = self.model_id_edit.text().strip()
    
    if not model_id:
        QMessageBox.warning(self, "No Model", "No model ID specified.")
        return
    
    image_path = Path(f"Img/Models/items/{model_id}.webp")
    
    if not image_path.exists():
        QMessageBox.warning(self, "Image Not Found", 
                          f"Model image not found:\n{image_path}")
        return
    
    # Show full-size preview in dialog
    pixmap = QPixmap(str(image_path))
    # ... display dialog with pixmap
```

**In Character Sheet**:
```python
# Show equipped item visuals with metadata
def update_equipment_slot(self, slot_label, item_data):
    model_id = item_data.get("model")
    
    if model_id:
        pixmap = get_cached_model_pixmap(model_id, "items")
        slot_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio))
        
        # Add tooltip with item info
        set_model_tooltip_with_preview(slot_label, model_id, "items")
    else:
        slot_label.clear()
```

**Browsing Models by Category**:
```python
def populate_model_browser(self, category: str, subcategory: str):
    """Populate grid with models from specific category."""
    metadata = load_models_metadata()
    
    # Filter models
    filtered = {
        model_id: meta
        for model_id, meta in metadata["items"].items()
        if meta["main_category"] == category 
        and meta["subcategory"] == subcategory
    }
    
    # Display in grid
    for model_id, meta in filtered.items():
        pixmap = get_cached_model_pixmap(model_id, "items")
        # Add to grid with name as label
        # ...
```

---

## PyInstaller Compatibility

### Embedded Resources

**PyInstaller Configuration**: Images and metadata are automatically included via `datas` specification.

**In `.spec` file**:
```python
a = Analysis(
    ['main.py'],
    datas=[
        ('Img', 'Img'),  # Includes all Img/Models subdirectories (items, mobs, icons)
        ('Data/models_metadata.json', 'Data'),  # Include metadata file
        # ... other data files
    ],
    # ... other settings
)
```

### Runtime Path Resolution

**Development Mode** (running from source):
```python
# Direct path works
image_path = Path("Img/Models/items/4063.webp")
```

**Compiled Mode** (`--onefile` or `--onedir`):
```python
import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource (works in dev and compiled modes).
    
    Args:
        relative_path: Relative path from application root
        
    Returns:
        Absolute path to resource
    """
    if getattr(sys, 'frozen', False):
        # Running in compiled mode
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development mode
        base_path = Path(__file__).parent
    
    return base_path / relative_path

# Usage
image_path = get_resource_path("Img/Models/items/4063.webp")
```

### Build Verification

**After building with PyInstaller, verify images and metadata are included**:

```bash
# For --onedir build
ls dist/DAOC-Character-Management/Img/Models/items/*.webp | wc -l
# Should output: 1000

ls dist/DAOC-Character-Management/Img/Models/mobs/*.webp | wc -l
# Should output: 1000

ls dist/DAOC-Character-Management/Img/Models/icons/items/*.webp | wc -l
# Should output: 370

# Check metadata file
cat dist/DAOC-Character-Management/Data/models_metadata.json
# Should show 838 models with names and categories

# For --onefile build (extract and check)
python -c "import sys; sys._MEIPASS" # Get temp extraction path
```

**Size Impact**:
- **Items**: 10.48 MB (3444 files)
- **Mobs**: 4.86 MB (1000 files)
- **Icons**: 0.18 MB (370 files)
- **Metadata**: 0.18 MB (JSON file)
- **Total**: +15.70 MB to executable
- **Compressed** (UPX): ~8-10 MB (WebP already compressed)

---

## Maintenance & Updates

### When to Update Images

**Scenarios**:
1. New game patch adds new item models
2. Image quality improvements available
3. Model ID corrections in database
4. New models discovered in Eve-of-Darkness repo
5. Los Ojos website adds new categories or models

### Update Process

**Step 1: Check for New Models**

```bash
# Check GitHub repo for updates
# Compare local count vs remote count
python -c "import requests; r = requests.get('https://api.github.com/repos/Eve-of-Darkness/DolModels/contents/src/items'); print(f'Remote Items: {len(r.json())} files')"

python -c "import requests; r = requests.get('https://api.github.com/repos/Eve-of-Darkness/DolModels/contents/src/mobs'); print(f'Remote Mobs: {len(r.json())} files')"
```

**Step 2: Run Download Script**

```bash
# Download all model types (items, mobs, icons)
python Tools/DataScraping/download_all_models.py

# Or force re-download all (quality improvements)
python Tools/DataScraping/download_all_models.py --force --quality 85
```

**Step 3: Update Metadata**

```bash
# Re-scrape Los Ojos website for latest metadata
python Tools/DataScraping/scrape_models_metadata.py

# Use cache for faster re-runs (only scrape changed pages)
python Tools/DataScraping/scrape_models_metadata.py --cache

# Force complete re-scrape (ignore cache)
python Tools/DataScraping/scrape_models_metadata.py --force
```

**Step 4: Verify Changes**

```bash
# Check file counts for all types
ls Img/Models/items/*.webp | wc -l    # Should be 1000
ls Img/Models/mobs/*.webp | wc -l     # Should be 1000
ls Img/Models/icons/items/*.webp | wc -l  # Should be 370

# Check total sizes
du -sh Img/Models/items/   # Should be ~4.6 MB
du -sh Img/Models/mobs/    # Should be ~4.9 MB
du -sh Img/Models/icons/   # Should be ~0.2 MB
du -sh Data/models_metadata.json  # Should be ~181 KB

# Check metadata entry count
python -c "import json; m=json.load(open('Data/models_metadata.json')); print(f'Items: {len(m[\"items\"])}, Mobs: {len(m[\"mobs\"])}, Icons: {len(m[\"icons\"])}')"
# Should output: Items: 595, Mobs: 193, Icons: 50
```

**Step 5: Test in Application**

```python
# Test random model IDs across all types
from pathlib import Path

# Test items
item_ids = ["1", "14", "4063", "2238"]
for model_id in item_ids:
    path = Path(f"Img/Models/items/{model_id}.webp")
    print(f"Item {model_id}: {'✅' if path.exists() else '❌'}")

# Test mobs
mob_ids = ["1", "50", "100"]
for model_id in mob_ids:
    path = Path(f"Img/Models/mobs/{model_id}.webp")
    print(f"Mob {model_id}: {'✅' if path.exists() else '❌'}")

# Test metadata
import json
metadata = json.load(open('Data/models_metadata.json'))
print(f"\nMetadata test:")
print(f"Item 132: {metadata['items'].get('132', {}).get('name', 'NOT FOUND')}")
print(f"Mob 1: {metadata['mobs'].get('1', {}).get('name', 'NOT FOUND')}")
```

**Step 6: Commit Changes**

```bash
git add Img/Models/
git add Data/models_metadata.json
git commit -m "Update model images library and metadata"
git push
```

### Quality Adjustments

**Increase Quality** (if images look poor):
```bash
python Tools/DataScraping/download_all_models.py --force --quality 90
# Trade-off: Higher quality = larger size
```

**Decrease Quality** (if size is concern):
```bash
python Tools/DataScraping/download_all_models.py --force --quality 70
# Trade-off: Smaller size = lower quality
```

**Recommended Quality**: 80% (current setting - optimal balance)

### Metadata Updates Only

**If images are current but metadata needs updating**:
```bash
# Just re-scrape metadata (faster than re-downloading images)
python Tools/DataScraping/scrape_models_metadata.py --force

# Verify new categories or names
python -c "import json; m=json.load(open('Data/models_metadata.json')); cats=set(v['subcategory'] for v in m['items'].values()); print(f'Item categories: {sorted(cats)}')"
```

---

## Performance Considerations

### Loading Performance

**Image Loading Time**:
- WebP decode: ~1-2 ms per image
- QPixmap creation: ~1-3 ms
- **Total**: <5 ms per image (negligible)

**Metadata Loading Time**:
- JSON parse: ~10-20 ms for 180 KB file
- Lookup: O(1) dictionary access (~0.001 ms)
- **Total**: Negligible after initial load

**Memory Usage**:
- Uncompressed in memory: ~64x64 RGBA = 16 KB per image
- 100 images cached: ~1.6 MB RAM
- Metadata in memory: ~500 KB (parsed JSON)
- **Total overhead**: Acceptable (<3 MB for typical usage)

### Optimization Strategies

**1. Lazy Loading** (load on demand):
```python
# Only load image when user views it
def on_item_hover(self, model_id):
    pixmap = QPixmap(f"Img/Models/items/{model_id}.webp")
    self.preview.setPixmap(pixmap)
```

**2. Caching** (avoid re-loading):
```python
from functools import lru_cache

@lru_cache(maxsize=200)
def get_model_pixmap(model_id, model_type="items"):
    return QPixmap(f"Img/Models/{model_type}/{model_id}.webp")
```

**3. Metadata Singleton** (load once):
```python
class ModelsMetadata:
    _instance = None
    _metadata = None
    
    @classmethod
    def get(cls):
        if cls._metadata is None:
            with open('Data/models_metadata.json', 'r') as f:
                cls._metadata = json.load(f)
        return cls._metadata

# Usage
metadata = ModelsMetadata.get()
item_name = metadata['items']['132']['name']
```

**4. Thumbnail Pre-generation** (optional):
```python
# Generate 32x32 thumbnails for table views
thumbnail = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
```

### Disk Space

**Total Size**: 15.52 MB (4814 files across 3 types)

**Breakdown**:
- Items: 10.48 MB (3444 files)
- Mobs: 4.86 MB (1000 files)
- Icons: 0.18 MB (370 files)
- Metadata: 0.18 MB (JSON file)

**Comparison**:
- Single HD screenshot: ~2-5 MB
- Small video: ~10-50 MB
- **Conclusion**: Negligible storage impact (~10 MB total)

---

## Troubleshooting

### Image Not Found

**Problem**: `Path("Img/Models/items/4063.webp").exists()` returns `False`

**Solutions**:
1. Check model ID exists in database: `"model": "4063"`
2. Verify file exists: `ls Img/Models/items/4063.webp`
3. Check correct model type folder (items vs mobs vs icons)
4. Re-download specific type:
   ```bash
   python Tools/DataScraping/download_all_models.py --force
   ```

### Metadata Not Found

**Problem**: `metadata['items'].get('132')` returns `None`

**Solutions**:
1. Check metadata file exists: `Data/models_metadata.json`
2. Verify metadata was scraped successfully (838 total entries)
3. Re-scrape metadata:
   ```bash
   python Tools/DataScraping/scrape_models_metadata.py --force
   ```
4. Check model ID exists on Los Ojos website

### Image Not Displaying

**Problem**: Image path exists but doesn't display in UI

**Solutions**:
1. Check QPixmap loading: `pixmap.isNull()`
2. Verify WebP support in Qt:
   ```python
   from PySide6.QtGui import QImageReader
   print(QImageReader.supportedImageFormats())
   # Should include b'webp'
   ```
3. Try absolute path instead of relative
4. Check file permissions
5. Verify model type matches folder (items/mobs/icons)

### Download Script Fails

**Problem**: Script exits with network errors

**Solutions**:
1. Check internet connection
2. Verify GitHub repo is accessible:
   ```bash
   curl https://api.github.com/repos/Eve-of-Darkness/DolModels/contents/src/items
   ```
3. Check firewall/proxy settings
4. Run with `--force` to retry failed downloads

### Scraper Fails

**Problem**: `scrape_models_metadata.py` crashes or returns 0 models

**Solutions**:
1. Clear cache and retry:
   ```bash
   rm -rf .cache/scraping/
   python Tools/DataScraping/scrape_models_metadata.py
   ```
2. Check Los Ojos website is accessible:
   ```bash
   curl https://daoc.ndlp.info/losojos-001-site1.btempurl.com/ModelViewer/
   ```
3. Check for website structure changes (update scraper if needed)
4. Run with verbose output to see errors
5. Check Python dependencies: `requests`, `beautifulsoup4`

### Quality Issues

**Problem**: Images appear blurry or pixelated

**Solutions**:
1. Increase WebP quality:
   ```bash
   python Tools/DataScraping/download_all_models.py --force --quality 90
   ```
2. Check display scaling in UI (use `Qt.SmoothTransformation`)
3. Verify original source image quality on GitHub

### PyInstaller Missing Images

**Problem**: Images work in dev but not in compiled .exe

**Solutions**:
1. Verify `.spec` file includes images in `datas`:
   ```python
   datas=[('Img', 'Img'), ...]
   ```
2. Use `get_resource_path()` helper function
3. Check `sys._MEIPASS` contains images:
   ```python
   import sys
   print(Path(sys._MEIPASS) / "Img/Models/items")
   print(Path(sys._MEIPASS) / "Data/models_metadata.json")
   ```
4. Rebuild with `--clean` flag

---

## Future Enhancements

### Planned Features

1. **Rich Model Info Integration**
   - ✅ **DONE**: ModelViewerDialog component (v2.1)
   - ✅ **DONE**: Clickable model icons in Armory template preview (v2.1)
   - Use metadata for tooltips in Database Editor
   - Display model name + category in Armory dialogs
   - Filter by category in model browser
   - Search models by name or category

2. **Model Viewer Component** (reusable widget)
   - ✅ **DONE**: Basic ModelViewerDialog (v2.1)
   - Drag-drop support
   - Zoom/pan controls
   - Side-by-side comparison
   - Category filtering UI

3. **Batch Preview** (multiple items)
   - Grid layout for templates
   - Complete armor set visualization
   - Mob visualization by type

4. **Search by Appearance** (reverse lookup)
   - Find items with same model ID
   - Visual similarity search
   - Browse all items in a category

5. **Model Metadata Enhancements**
   - Usage count (how many items use this model)
   - Realm-specific variants
   - Model source information
   - Quality ratings

6. **Custom Models** (user uploads)
   - Support user-provided images
   - Override default models
   - Community model sharing

---

## Version History

### v2.1 (December 1, 2025)

**Model Viewer Dialog Integration**:
- ✅ **New Component**: `UI/model_viewer_dialog.py`
  - Reusable dialog for displaying model images
  - Shows item name, model ID, and category
  - Auto-scaling with aspect ratio preservation
  - Dark theme UI with modern styling
  - Multilingual support
- ✅ **Armory Integration**: Clickable 🔍 icons in template preview
  - Shows model icons for armor, cloaks, and weapons
  - Click to open ModelViewerDialog with embedded image
  - No external web links - 100% offline
- ✅ **Architecture**: Professional component design
  - Handles missing images gracefully
  - Uses `get_resource_path()` for PyInstaller compatibility
  - Window resize support with image re-scaling
  - Complete error handling and logging

**Features**:
- Clickable model links in Armory template equipment preview
- Model viewer shows embedded WebP images (no web dependency)
- Slots with visual models: Torso, Arms, Legs, Hands, Feet, Helmet, Cloak, Weapons
- Jewelry slots excluded (no visual models)

### v3.0 (December 19, 2025)

**Phase 10 Refactoring - Item Model Viewer Module**:
- ✅ **Module Extraction**: Created `Functions/item_model_viewer.py` (167 lines)
- ✅ **Functions Extracted**: 2 functions (item_model_on_link_clicked, item_model_show)
- ✅ **Code Quality**:
  - PEP 8 compliant (ruff: 0 errors)
  - Comprehensive docstrings with examples
  - Type hints for all parameters
  - Multi-language support (lang.get())
  - Robust error handling with logging
- ✅ **Integration**: Thin wrappers in ArmorManagementDialog (2 lines each)
- ✅ **Code Reduction**: ~60 lines removed from dialogs.py

**Key Improvements**:
- Separated concerns: UI logic (dialogs.py) vs business logic (item_model_viewer.py)
- Improved testability: Functions can be tested independently
- Reusability: Functions can be used from other UI components
- Better maintainability: Focused, single-purpose module

**Statistics**:
- Lines extracted: 60
- Lines removed from dialogs.py: ~60
- Thin wrappers added: 2 lines
- Module lines: 167 (with docstrings and error handling)

### v2.0 (November 30, 2025)

**Major Update - Comprehensive Model System**:
- ✅ **3 Model Types**: Items (1000), Mobs (1000), Icons (370)
- ✅ **Metadata System**: 838 models with names and categories
- ✅ **Professional Scraper**: Los Ojos website integration
- ✅ **Complete Categorization**: 
  - 25 item subcategories (Bow, Sword, Helm, etc.)
  - 8 mob types (Biped, Vampiir, Demon, Animal, etc.)
  - Full inventory icons
- ✅ **Advanced Features**:
  - Cache system for fast re-runs
  - Pagination support (up to 22 pages per category)
  - Duplicate detection
  - Smart URL extraction (hash-based)
  - 100% success rate scraping
- ✅ **Documentation**: Complete overhaul with examples
- ✅ **Total size**: 9.82 MB (images + metadata)

**Statistics**:
- Total files: 2370 models + 1 metadata file
- Images size: 9.65 MB (WebP)
- Metadata size: 180.6 KB (JSON)
- Size reduction: 30.2% from original 13.84 MB
- Metadata entries: 838 models with full information
- Scraping time: 154.2 seconds
- Success rate: 100% (0 failures)

**Migration Notes**:
- Old `download_model_images.py` → new `download_all_models.py`
- Basic metadata generation → professional `scrape_models_metadata.py`
- Single type (items) → three types (items/mobs/icons)
- Simple file list → rich metadata with categories

### v1.0 (November 2024)

**Initial Release**:
- ✅ 1000 item model images from Eve-of-Darkness repo
- ✅ WebP conversion (80% quality, 61.8% size reduction)
- ✅ Download script with resume capability
- ✅ Basic documentation
- ✅ PyInstaller compatibility
- ✅ Total size: 4.60 MB

**Statistics**:
- Files processed: 1000 (items only)
- Original size: 12.05 MB (JPG)
- Converted size: 4.60 MB (WebP)
- Size reduction: 61.8%
- Average file size: 4.60 KB

**Tool References**:
- Download: `Tools/DataScraping/download_model_images.py` (deprecated in v2.0)

---

## References

**Image Source**: [Eve-of-Darkness/DolModels](https://github.com/Eve-of-Darkness/DolModels)  
**Metadata Source**: [Los Ojos Model Viewer](https://daoc.ndlp.info/losojos-001-site1.btempurl.com/ModelViewer/)  
**WebP Format**: [Google WebP Documentation](https://developers.google.com/speed/webp)  
**PySide6**: [Qt for Python Documentation](https://doc.qt.io/qtforpython/)

---

## Credits

- **Dawn of Light** - Original model pictures
- **Eve of Darkness** - Open source model viewer and GitHub repository
- **Los Ojos Rojos** - Model viewer website and categorization

---

*Last Updated: December 19, 2025 (Version 109 - Phase 10 Item Model Viewer Module)*
