# 🛡️ Armory Import System - Technical Documentation

**Version**: 1.0  
**Date**: November 2025  
**Component**: `UI/armory_import_dialog.py`  
**Related**: `Functions/items_scraper.py`, `Functions/items_parser.py`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Import Workflow](#import-workflow)
4. [Multi-Realm Items Management](#multi-realm-items-management)
5. [Database Structure](#database-structure)
6. [UI Components](#ui-components)
7. [Background Processing](#background-processing)
8. [Error Handling](#error-handling)
9. [Translation Support](#translation-support)

---

## Overview

The Armory Import System allows users to import items from template files (e.g., Zenkcraft format) into a centralized database. The system:

- **Parses** template files to extract item names
- **Scrapes** Eden items database for complete item details
- **Filters** only loot items (excludes quest items/Devices)
- **Manages** multi-realm items with different IDs
- **Saves** to a unified `items_database.json` in user's Armory folder

### Key Features

- ✅ **Background processing** with QThread worker
- ✅ **Real-time progress** updates with item count
- ✅ **Multi-realm support** (same item can have different IDs per realm)
- ✅ **Smart deduplication** (name-based matching)
- ✅ **Debug mode** (test with single item)
- ✅ **Clickable IDs** (open Eden item page in browser)
- ✅ **Full translations** (FR/EN/DE)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ArmoryImportDialog (UI)                     │
│  - File selection (template .txt)                           │
│  - Realm selection (Albion/Hibernia/Midgard)                │
│  - Debug mode checkbox                                       │
│  - Progress bar + status label                              │
│  - Items table (7 columns)                                   │
│  - Details panel (selected item)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              ItemImportWorker (QThread)                      │
│  1. Parse template file → extract item names                │
│  2. Initialize Eden scraper (isolated Chrome profile)       │
│  3. For each item:                                           │
│     - Find item ID on Eden                                   │
│     - Get item details (stats, merchants, etc.)             │
│     - Filter quest items (no merchants)                     │
│     - Emit progress + item_found signal                     │
│  4. Close scraper                                            │
│  5. Emit finished signal                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   items_database.json                        │
│  {                                                           │
│    "version": "1.0",                                         │
│    "created": "2025-11-18T...",                              │
│    "updated": "2025-11-18T...",                              │
│    "items": {                                                │
│      "item_id": {                                            │
│        "name": "Item Name",                                  │
│        "realms": {"Hibernia": "123", "Albion": "456"},      │
│        "type": "Armor",                                      │
│        "slot": "Torso",                                      │
│        "merchants": [...],                                   │
│        ...                                                   │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Import Workflow

### 1. File Selection

```python
# User selects template file via QFileDialog
file_path = QFileDialog.getOpenFileName(
    self,
    lang.get("armory_import.select_file"),
    "",
    lang.get("armory_import.file_filter")  # "Template files (*.txt)"
)
```

### 2. Template Parsing

**File**: `Functions/items_parser.py`  
**Function**: `parse_template_file(file_path)`

```python
# Extract item names from template
# Format: Name: <item_name>\nSource Type: Loot
items = parse_template_file(file_path)
# Returns: ['Item Name 1', 'Item Name 2', ...]
```

**Filters**:
- Only blocks containing `Name:` AND `Source Type: Loot`
- Removes duplicates

### 3. Eden Scraping

**File**: `Functions/items_scraper.py`  
**Class**: `ItemsScraper`

For each item name:

```python
# Step 1: Find item ID
item_id = items_scraper.find_item_id(item_name, realm)
# Methods: onclick="item_go(ID)" or <tr id="result_row_ID">

# Step 2: Get item details
details = items_scraper.get_item_details(item_id, realm, item_name)
# Returns: {id, name, type, slot, quality, level, stats, resistances, bonuses, merchants}
```

**Merchant Parsing** (with zone overrides):
```python
if currency == 'Roots':
    zone = 'Epik'
elif currency == 'Dragon Scales':
    currency = 'Scales'
    zone = 'Drake'
elif currency == 'Scales':
    zone = 'Drake'
elif currency == 'Atlantean Glass':
    zone = 'ToA'
elif currency == 'Seals':
    zone = 'DF'
```

### 4. Quest Item Filtering

```python
# Skip items with no merchants (quest items / Devices)
if details and details.get('name'):
    merchants = details.get('merchants', [])
    if not merchants:
        self.progress.emit(i, total_items, f"⚠️ Ignoré (objet de quête): {item_name}")
        continue
```

### 5. Database Save

**Location**: `{armor_path}/items_database.json`  
**Logic**: Smart deduplication by name

```python
# Check if item exists by NAME (case-insensitive)
for key, existing_item in database['items'].items():
    if existing_item.get('name', '').strip().lower() == item_name:
        # Merge realms: {"Hibernia": "123", "Albion": "456"}
        existing_realms[realm] = item_id
        break
```

---

## Multi-Realm Items Management

### Problem

Same item can:
- **Option 1**: Have same ID across all realms (e.g., ID 100 for all 3 realms)
- **Option 2**: Have different IDs per realm (e.g., ID 100 Hibernia, ID 200 Albion, ID 300 Midgard)

### Solution

Store `realms` as dictionary mapping realm → ID:

```json
{
  "items": {
    "100": {
      "name": "Cloak of Shadows",
      "realms": {
        "Hibernia": "100",
        "Albion": "200",
        "Midgard": "300"
      },
      "type": "Armor",
      "slot": "Cloak",
      "merchants": [...]
    }
  }
}
```

### Deduplication Logic

1. **Search by name** (case-insensitive)
2. If found → **merge realms** dictionary
3. If not found → **create new entry** with `realms: {realm: id}`

---

## Database Structure

### `items_database.json`

```json
{
  "version": "1.0",
  "created": "2025-11-18T10:30:00.000000",
  "updated": "2025-11-18T15:45:00.000000",
  "item_count": 150,
  "items": {
    "item_id_1": {
      "id": "123456",
      "name": "Rigid Razorback Jerkin",
      "realms": {
        "Hibernia": "123456",
        "Albion": "789012"
      },
      "type": "Armor",
      "slot": "Torso",
      "quality": "100%",
      "level": "51",
      "stats": {
        "Strength": "+16",
        "Constitution": "+15"
      },
      "resistances": {
        "Crush": "3%",
        "Thrust": "3%"
      },
      "bonuses": {},
      "merchants": [
        {
          "name": "Merchant Name",
          "zone": "Drake",
          "zone_full": "Dragon Zone",
          "location": "loc=12345,67890",
          "level": "50",
          "price": "100 Dragon Scales",
          "price_parsed": {
            "amount": "100",
            "currency": "Scales",
            "display": "100 Scales"
          }
        }
      ]
    }
  }
}
```

---

## UI Components

### 1. File Group

- **Label**: Current file name
- **Browse Button**: Open QFileDialog
- **Realm Combo**: Albion / Hibernia / Midgard
- **Debug Checkbox**: Limit to 1 item for testing

### 2. Progress Group

- **Progress Bar**: 0-100% with item count
- **Status Label**: Current operation (e.g., "🔍 Recherche: Item Name")

### 3. Items Table (7 columns)

| Column | Description | Special |
|--------|-------------|---------|
| ID | Item ID | **Clickable** (opens Eden URL) |
| Name | Item name | - |
| Type | Item type (Armor, Weapon, etc.) | - |
| Slot | Equipment slot | - |
| Zone | Merchant zone | - |
| Price | Merchant price (amount only) | - |
| Currency | Price currency (Scales, Roots, etc.) | - |

**Clickable ID**:
```python
def _on_cell_clicked(self, row, column):
    if column == 0:  # ID column
        item_id = self.items_table.item(row, 0).data(Qt.UserRole)
        url = f"https://eden-daoc.net/items?id={item_id}"
        QDesktopServices.openUrl(QUrl(url))
```

### 4. Details Panel

Shows full item information:
- ID, Name, Type, Slot, Quality, Level
- Stats (Strength, Dexterity, etc.)
- Resistances (Crush, Slash, Thrust, etc.)
- Bonuses
- **Merchants** (name, zone, location, price, currency)

---

## Background Processing

### ItemImportWorker (QThread)

**Purpose**: Avoid freezing UI during long scraping operations

**Signals**:
```python
class ItemImportWorker(QThread):
    progress = Signal(int, int, str)  # current, total, message
    item_found = Signal(dict)         # item data
    finished = Signal(bool, str)      # success, message
```

**Workflow**:
```python
def run(self):
    # 1. Parse template
    items = parse_template_file(self.file_path)
    
    # 2. Initialize scraper
    cookie_manager = CookieManager()
    eden_scraper = EdenScraper(cookie_manager)
    eden_scraper.initialize_driver(headless=False, minimize=True)
    
    # 3. Process items
    for i, item_name in enumerate(items, 1):
        self.progress.emit(i, total, f"🔍 {item_name}")
        
        item_id = items_scraper.find_item_id(item_name, realm)
        details = items_scraper.get_item_details(item_id, realm, item_name)
        
        if details and details.get('merchants'):
            self.item_found.emit(details)
    
    # 4. Cleanup
    eden_scraper.close()
    self.finished.emit(True, f"✅ Import terminé: {success_count} réussis")
```

**Thread Safety**:
- ✅ Scraper initialized/closed within thread
- ✅ Signals used for UI updates (not direct manipulation)
- ✅ Worker stored as instance variable to prevent premature deletion

---

## Error Handling

### 1. File Not Found
```python
if not file_path or not Path(file_path).exists():
    QMessageBox.warning(self, "Erreur", "Fichier introuvable")
    return
```

### 2. No Items Found
```python
if not items:
    self.finished.emit(False, "Aucun item trouvé dans le fichier")
    return
```

### 3. Scraper Initialization Failed
```python
if not eden_scraper.initialize_driver():
    self.finished.emit(False, "Erreur initialisation scraper")
    return
```

### 4. Item Not Found on Eden
```python
if not item_id:
    logging.warning(f"Item ID non trouvé: {item_name}")
    failed_count += 1
    continue
```

### 5. Quest Item (No Merchants)
```python
if not details.get('merchants'):
    self.progress.emit(i, total, f"⚠️ Ignoré (objet de quête): {item_name}")
    continue
```

---

## Translation Support

### Translation Keys

**File Group**:
- `armory_import.file_group_title` → "📂 Fichier Template"
- `armory_import.browse_button` → "📁 Parcourir..."
- `armory_import.realm_label` → "🏰 Royaume:"

**Table Columns**:
- `armory_import.table_columns.id` → "ID"
- `armory_import.table_columns.name` → "Nom"
- `armory_import.table_columns.type` → "Type"
- `armory_import.table_columns.slot` → "Slot"
- `armory_import.table_columns.zone` → "Zone"
- `armory_import.table_columns.price` → "Prix"
- `armory_import.table_columns.currency` → "Devises"

**Dialogs**:
- `armory_import.import_finished_title` → "Import terminé"
- `armory_import.save_success_title` → "Sauvegarde réussie"
- `armory_import.save_success_message` → "Base de données sauvegardée"

**Supported Languages**: FR (complete), EN (complete), DE (complete)

---

## Usage Example

### 1. Open Armory Import

Settings → Armory Tab → "Import Items" button

### 2. Select File

Browse → Select template file (e.g., `my_armor_set.txt`)

### 3. Choose Realm

Select realm from dropdown (Hibernia / Albion / Midgard)

### 4. Start Import

Click "▶️ Démarrer l'import"

### 5. Monitor Progress

Watch progress bar and status label for each item

### 6. Review Results

- Check items table (7 columns)
- Click ID to open Eden page
- Select item to see full details

### 7. Save Database

Click "💾 Sauvegarder la base de données"

Database saved to: `{armor_path}/items_database.json`

---

## Debug Mode

Enable debug mode to test with only 1 item:

```python
if self.debug_mode and len(items) > 1:
    items = items[:1]
    self.progress.emit(0, 1, "🐛 MODE DEBUG: Traitement du 1er item uniquement")
```

**Use Case**: Test scraping configuration without waiting for full import

---

## Performance Considerations

### Browser Isolation

- **Dedicated Chrome profile**: `AppData/Eden/ChromeProfile/EdenScraper`
- **Flags**: `--disable-sync`, `--no-first-run`, `--disable-blink-features=AutomationControlled`
- **Minimized window**: `--window-position=-32000,-32000`

### Scraping Speed

- **Headless**: Disabled (Eden requires visible browser for some elements)
- **Minimize**: Enabled (faster than headless, Eden compatible)
- **Average**: ~2-3 seconds per item (includes search + details)

### Database Size

- **Average item**: ~500 bytes (with merchants)
- **100 items**: ~50 KB
- **1000 items**: ~500 KB

---

## Future Improvements

- [ ] Cache item IDs to avoid re-scraping
- [ ] Batch import (multiple template files)
- [ ] Export database to CSV/Excel
- [ ] Item search/filter in database
- [ ] Automatic update check (detect new items on Eden)
- [ ] Template format auto-detection (support multiple formats)

---

**End of Document** - For more details, see:
- [ITEMS_SCRAPER_TECHNICAL_EN.md](ITEMS_SCRAPER_TECHNICAL_EN.md)
- [ITEMS_PARSER_EN.md](ITEMS_PARSER_EN.md)
- [ARMORY_USER_GUIDE_FR.md](ARMORY_USER_GUIDE_FR.md)
