# 🛡️ Armory System - Technical Documentation

**Version**: 2.0  
**Date**: November 2025  
**Last Updated**: November 20, 2025  
**Component**: `UI/armory_import_dialog.py`, `UI/mass_import_monitor.py`, `UI/template_import_dialog.py`  
**Related**: `Functions/items_scraper.py`, `Functions/items_parser.py`, `Functions/import_worker.py`, `Functions/build_items_database.py`, `Functions/template_manager.py`, `Functions/template_metadata.py`  
**Branch**: 108_Imp_Armo (21 commits)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Template System](#template-system)
3. [Architecture](#architecture)
4. [Import Workflow](#import-workflow)
5. [Mass Import System](#mass-import-system)
6. [Price Search System](#price-search-system)
7. [Multi-Realm Items Management](#multi-realm-items-management)
8. [Database Structure](#database-structure)
9. [UI Components](#ui-components)
10. [Background Processing](#background-processing)
11. [Error Handling](#error-handling)
12. [Translation Support](#translation-support)
13. [Critical Bug Fixes](#critical-bug-fixes)
14. [Implementation Progress](#implementation-progress)
15. [Commit History](#commit-history)

---

## Overview

The Armory Import System is a comprehensive solution for managing armor templates and importing items from Eden-DAOC database. The system provides:

- **Template Management**: Character-centric template system with metadata, tags, and seasons
- **Mass Import**: Batch import of items from template files with real-time monitoring
- **Price Search**: Automated search for missing merchant prices via Eden scraping
- **Multi-Realm Support**: Automatic detection of item variants across all realms
- **Database Persistence**: Dual-mode architecture (read-only internal or user-managed personal)

### System Components

The system is composed of three main subsystems:

1. **Template System** - Contextual import from character sheet with automatic class detection
2. **Mass Import System** - Batch processing with QThread workers and retry mechanism
3. **Price Search System** - Missing price detection and Eden scraping integration

### Key Features

- ✅ **Background processing** with QThread worker
- ✅ **Real-time progress** updates with item count
- ✅ **Multi-realm support** (same item can have different IDs per realm)
- ✅ **Smart deduplication** (name-based matching)
- ✅ **Debug mode** (test with single item)
- ✅ **Clickable IDs** (open Eden item page in browser)
- ✅ **Full translations** (FR/EN/DE)
- ✅ **Mass Import System** with manual start and real-time monitoring
- ✅ **Price Search** for missing merchant prices with JSON storage
- ✅ **Auto-sync prices** between template JSON and database
- ✅ **Retry system** for filtered items with bypass_filters flag
- ✅ **Multi-variant detection** (same item across multiple realms)
- ✅ **Thread-safe operations** with separate import/cleanup callbacks
- ✅ **Template metadata** with tags, seasons, and rich information
- ✅ **Class-based filtering** (only relevant templates shown per character)
- ✅ **Standardized naming** ({Class}_{Season}_{Description}.txt)

---

## Template System

### Overview

The Template System provides character-centric management of armor templates with automatic class detection, standardized naming, and rich metadata.

**Key Principles:**
- Templates are imported **from character sheet** for automatic context
- Organized by **realm** (Hibernia/, Albion/, Midgard/)
- **Standardized naming convention** with class, season, and description
- **Metadata JSON files** store tags, import info, and prices
- **Class-based filtering** ensures only relevant templates are shown

### Template Import from Character Sheet

**Entry Point:** Character sheet window only (not Settings)

**Workflow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEMPLATE IMPORT WORKFLOW                      │
└─────────────────────────────────────────────────────────────────┘

1. User opens character "Ewosong" (Bard, Hibernia)
   │
2. Clicks "Import Template" button in character sheet
   │
3. Import dialog opens with auto-filled context:
   ├─> Class: Bard (auto-detected)
   ├─> Realm: Hibernia (auto-detected)
   ├─> Season: S3 (current season from config)
   └─> Description: [user enters "basique sans ml10"]
   │
4. System generates template filename:
   └─> Bard_S3_basique_sans_ml10.txt
   │
5. Template saved in:
   └─> Armory/Hibernia/Bard_S3_basique_sans_ml10.txt
   │
6. Metadata JSON created:
   └─> Armory/Hibernia/Json/Bard_S3_basique_sans_ml10.txt.json
   │
7. Template visible only for Bard characters
```

### Standardized Naming Convention

**Format:** `{Class}_{Season}_{Description}.txt`

**Components:**
- **Class**: English class name (Bard, Cleric, Warrior, etc.)
- **Season**: Season identifier (S1, S2, S3, Custom)
- **Description**: User-provided text (normalized)

**Normalization Rules:**
- Spaces → underscores `_`
- Accents removed (é→e, à→a, etc.)
- Special characters removed (except `-` and `_`)
- Case preserved for readability
- Max 50 characters

**Examples:**
```
✅ Bard_S3_Low_Cost_Sans_ML10.txt
✅ Cleric_S2_Full_RvR_ML10.txt
✅ Warrior_S3_Budget_PvE.txt
✅ Sorcerer_S1_Template_Eden_Officiel.txt
```

### Template Metadata Structure

**File:** `{template_name}.txt.json`

**Location:** `Armory/{Realm}/Json/{template_name}.txt.json`

**Structure:**
```json
{
  "version": "1.0",
  "template_name": "Bard_S3_basique_sans_ml10.txt",
  "metadata": {
    "class": "Bard",
    "class_fr": "Barde",
    "class_de": "Barde",
    "realm": "Hibernia",
    "season": "S3",
    "description": "basique_sans_ml10",
    "tags": ["low-cost", "pve", "beginner"],
    "source_file": "Eden - Hibernia - Bard_Summary.txt",
    "import_date": "2025-11-20T19:00:55.669922",
    "imported_by_character": "Ewosong TheBlindWoman",
    "item_count": 271,
    "auto_generated": true
  },
  "notes": "",
  "prices": {
    "Cloth Cap:Hibernia": {
      "price": "500",
      "currency": "Scales",
      "zone": "Drake"
    }
  }
}
```

**Metadata Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `class` | string | ✅ | Class name (EN) |
| `class_fr` | string | ✅ | Class name (FR) |
| `class_de` | string | ✅ | Class name (DE) |
| `realm` | string | ✅ | Albion/Hibernia/Midgard |
| `season` | string | ✅ | Season (S1, S2, S3, etc.) |
| `description` | string | ✅ | Short description |
| `tags` | array | ❌ | Free-form tags (max 5) |
| `source_file` | string | ✅ | Original source filename |
| `import_date` | ISO 8601 | ✅ | Import timestamp |
| `imported_by_character` | string | ✅ | Character name |
| `item_count` | int | ✅ | Number of items |
| `auto_generated` | bool | ✅ | Auto-generated flag |
| `prices` | object | ❌ | Missing prices storage |

### Tag System

**Purpose:** Categorize templates for easy search and filtering

**Suggested Tags:**

| Category | Tags |
|----------|------|
| **Budget** | `low-cost`, `budget`, `premium`, `high-end` |
| **Content** | `pve`, `pvp`, `rvr`, `solo`, `group` |
| **Level** | `beginner`, `intermediate`, `advanced` |
| **ML** | `ml1`, `ml5`, `ml10`, `no-ml` |
| **Source** | `eden`, `official`, `community`, `personal` |
| **Spec** | `heal`, `dps`, `tank`, `support`, `cc` |

**UI Features:**
- Auto-completion with predefined tags
- Clickable tag badges
- Custom tag creation
- Maximum 5 tags per template

### Template Index

**File:** `Armory/.template_index.json`

**Purpose:** Fast search/filter without reading all JSON files

**Structure:**
```json
{
  "version": "1.0",
  "last_updated": "2025-11-20T19:00:55.670234",
  "templates": [
    {
      "file": "Bard_S3_basique_sans_ml10.txt",
      "class": "Bard",
      "realm": "Hibernia",
      "season": "S3",
      "tags": ["low-cost"],
      "item_count": 271,
      "import_date": "2025-11-20T19:00:55.669922"
    }
  ]
}
```

**Auto-Update:** Index rebuilt on template import/delete/modify

### Class-Based Filtering

**Rule:** Character only sees templates matching their class

**Example:**

```python
# Character: "Ewosong" (Bard, Hibernia)

Visible templates:
  ✅ Bard_S3_basique_sans_ml10.txt
  ✅ Bard_S3_Budget_PvE.txt
  ✅ Bard_S2_Full_RvR.txt

Hidden templates:
  ❌ Cleric_S3_Heal_Spec.txt (different class)
  ❌ Warrior_S3_Tank.txt (different class)
  ❌ Sorcerer_S1_Nuke.txt (different class)
```

### Season Management

**Configuration:** `Configuration/config.json`

```json
{
  "game": {
    "seasons": ["S1", "S2", "S3"],
    "default_season": "S3"
  }
}
```

**UI Behavior:**
- Current season pre-selected in import dialog
- All seasons available in dropdown
- "Custom" option for free-form entry (dynamically added to list)

### File Organization

```
Armory/
├── Hibernia/
│   ├── Bard_S3_basique_sans_ml10.txt
│   ├── Druid_S3_heal_spec.txt
│   └── Json/
│       ├── Bard_S3_basique_sans_ml10.txt.json
│       └── Druid_S3_heal_spec.txt.json
├── Albion/
│   ├── Cleric_S3_heal.txt
│   └── Json/
│       └── Cleric_S3_heal.txt.json
├── Midgard/
│   ├── Shaman_S3_support.txt
│   └── Json/
│       └── Shaman_S3_support.txt.json
├── S3/                          # Exported templates by season
├── .template_index.json         # Global index
└── items_database.json          # Personal database (dual-mode)

Data/
└── items_database_src.json      # Internal database (read-only)
```

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

## Mass Import System

### Overview

The Mass Import System allows importing multiple items from template files with real-time monitoring and manual control.

**Key Features:**
- **Manual Start Button**: User controls when import begins (no auto-start)
- **Real-time Monitoring**: Live progress with item count and status updates
- **QThread Worker**: Background processing without UI freeze
- **Multi-variant Support**: Automatically finds all realm versions of each item
- **Retry System**: Failed/filtered items can be retried with bypass_filters flag
- **Thread Safety**: Separate callbacks for business logic vs resource cleanup

### Mass Import Monitor Window

**File:** `UI/mass_import_monitor.py`

**Components:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Import en masse - 271 items                        [✖]         │
├─────────────────────────────────────────────────────────────────┤
│  [▶️ Démarrer l'import]                                         │
│                                                                  │
│  Progress: ████████░░░░░░░░░░░░ 45/271 (16%)                   │
│  Status: 🔍 Recherche: Cloth Cap (Hibernia)                     │
│                                                                  │
│  ✅ Réussis: 40                                                 │
│  ⏭️ Ignorés: 5                                                  │
│  ❌ Échecs: 0                                                   │
│                                                                  │
│  [📋 Examiner les items filtrés]                               │
└─────────────────────────────────────────────────────────────────┘
```

**Workflow:**

1. **Preparation Phase** (prepare_import):
   ```python
   def prepare_import(self, items, realm):
       """Setup import without starting"""
       self.items = items
       self.realm = realm
       self.start_button.setEnabled(True)
       self.status_label.setText(lang.get("mass_import.ready_to_start", 
                                           count=len(items)))
   ```

2. **Manual Start** (start_import_manual):
   ```python
   def start_import_manual(self):
       """User clicks Start Import button"""
       self.start_button.setEnabled(False)
       self.start_button.setText(lang.get("mass_import.import_in_progress"))
       
       # Create and start worker
       self.worker = ImportWorker(self.items, self.realm, 
                                  skip_filters_mode=False)
       self.worker.progress.connect(self.on_progress)
       self.worker.item_found.connect(self.on_item_found)
       self.worker.import_finished.connect(self.on_import_finished)
       self.worker.finished.connect(self.on_thread_finished)
       self.worker.start()
   ```

3. **Progress Updates**:
   - Live count of succeeded/ignored/failed items
   - Current item being processed with status emoji
   - Progress bar percentage
   - Time estimation (future enhancement)

4. **Completion**:
   - Summary message with final counts
   - "Examiner les items filtrés" button appears if items were filtered
   - Window stays open for user review

### Import Worker (QThread)

**File:** `Functions/import_worker.py`

**Signals:**
```python
class ImportWorker(QThread):
    progress = Signal(int, int, str)           # current, total, message
    item_found = Signal(dict)                  # item data
    item_filtered = Signal(str, str, str)      # name, realm, reason
    import_finished = Signal(bool, str, int, int, int)  # success, msg, succeeded, ignored, failed
    # Note: finished signal inherited from QThread
```

**Critical: Separate Callbacks**

```python
# In MassImportMonitor.__init__:
self.worker.import_finished.connect(self.on_import_finished)  # Business logic
self.worker.finished.connect(self.on_thread_finished)         # Cleanup

def on_import_finished(self, success, message, succeeded, ignored, failed):
    """Handle import completion (business logic)"""
    self.success_count = succeeded
    self.ignored_count = ignored
    self.failed_count = failed
    self.update_counts()
    
    # Show review button if filtered items exist
    if self.filtered_items:
        self.review_button.setVisible(True)

def on_thread_finished(self):
    """Handle thread termination (resource cleanup)"""
    if self.worker:
        self.worker.wait(5000)  # Wait max 5 seconds
        self.worker.deleteLater()
        self.worker = None
```

**Why Separate?** Prevents "QThread: Destroyed while thread is still running" crash.

### Retry System with bypass_filters

**Problem:** Items filtered by strict rules (level <50, utility <100) might be needed in templates.

**Solution:** `bypass_filters` flag stored in database

**Location:** `Functions/import_worker.py` lines 180-210

```python
def run(self):
    for item_name in self.items:
        # Find all variants (multi-realm)
        variants = items_scraper.find_all_item_variants(item_name)
        
        for variant in variants:
            # Check if item exists in database
            cache_key = f"{item_name.lower()}:{variant['realm'].lower()}"
            existing_item = db_manager.search_item(item_name, variant['realm'])
            
            if existing_item:
                # DUPLICATE DETECTED
                if self.skip_filters_mode:
                    # ADD bypass_filters flag
                    existing_item["bypass_filters"] = True
                    db_manager.save_database()
                    self.progress.emit(i, total, f"✅ Duplicate updated: {item_name}")
                else:
                    self.progress.emit(i, total, f"⏭️ Duplicate ignored: {item_name}")
            else:
                # New item - normal import flow
                ...
```

**Failed Items Review Dialog:**

**File:** `UI/failed_items_review_dialog.py`

Shows filtered items with reason and allows retry with bypass_filters:

```
┌─────────────────────────────────────────────────────────────────┐
│  Items filtrés - 5 items                             [✖]        │
├─────────────────────────────────────────────────────────────────┤
│  Nom                     │ Realm    │ Raison                    │
│  Low Level Helm          │ Hibernia │ Level 45 < 50             │
│  Weak Cloth Gloves       │ Albion   │ Utility 85.7 < 100        │
│  Quest Ring              │ Midgard  │ No merchants              │
│                                                                  │
│  [❌ Fermer]  [🔄 Réessayer avec bypass_filters]               │
└─────────────────────────────────────────────────────────────────┘
```

When retry is clicked:
1. Creates new ImportWorker with `skip_filters_mode=True`
2. Searches database for existing items
3. Adds `bypass_filters: true` flag to duplicates
4. Imports new items normally (already bypassed strict filters in scraper)

---

## Price Search System

### Overview

Allows searching for missing merchant prices in template items and storing them in template metadata JSON.

**Use Case:** Template imported from Eden Summary (no prices) → Search prices → Store in JSON → Sync with database

### Search Missing Prices Dialog

**File:** `UI/dialogs.py` class `SearchMissingPricesDialog`

**Components:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Rechercher les prix manquants                       [✖]        │
├─────────────────────────────────────────────────────────────────┤
│  Items sans prix: 42                                            │
│  Filtrer par devise: [Toutes ▼] [Scales] [Roots] [Seals] ...   │
│                                                                  │
│  ☐ Ring of the Azure        (Hibernia) - Drake                  │
│  ☐ Cloth Cap                (Hibernia) - Drake                  │
│  ☑ Soulbinder's Belt        (All)      - Drake                  │
│                                                                  │
│  [✖ Fermer]  [🔍 Importer les prix sélectionnés]               │
└─────────────────────────────────────────────────────────────────┘
```

**Workflow:**

1. **Load template** → Parse items → Check database for prices
2. **Display items** with missing merchant_price
3. **User selects** items to import prices for
4. **Scrape Eden** for each selected item
5. **Store prices** in template JSON metadata:
   ```json
   {
     "prices": {
       "Ring of the Azure:Hibernia": {
         "price": "500",
         "currency": "Scales",
         "zone": "Drake"
       }
     }
   }
   ```
6. **Auto-refresh** dialog to remove newly priced items

### Price Synchronization

**File:** `UI/dialogs.py` method `_sync_template_prices_with_db()`

**Purpose:** Remove prices from JSON that now exist in database (avoid duplication)

```python
def _sync_template_prices_with_db(self):
    """Sync template prices with database"""
    template_path = self.template_path
    json_path = template_path.replace('.txt', '.txt.json')
    
    # Load metadata
    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    prices = metadata.get('prices', {})
    if not prices:
        return
    
    # Check each price against database
    for cache_key in list(prices.keys()):
        name, realm = cache_key.split(':')
        db_item = db_manager.search_item(name, realm)
        
        if db_item and db_item.get('merchant_price'):
            # Price exists in DB → Remove from JSON
            del prices[cache_key]
    
    # Save updated metadata
    metadata['prices'] = prices
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
```

**Called:**
- On dialog open (load template)
- After successful price import (auto-refresh)

### Currency Display with Fallback

**Problem:** Some items missing `merchant_currency` in database but have `merchant_zone`

**Solution:** Zone-to-currency mapping

```python
currency_map = {
    'Drake': 'Scales',
    'Phoenix': 'Souls/Roots/Ices',
    'Demon': 'Glasses',
    'Summoner': 'Seals',
    'Behemoth': 'Grimoires'
}

currency = item.get('merchant_currency')
if not currency and item.get('merchant_zone'):
    currency = currency_map.get(item['merchant_zone'], '')
```

**Database Field Added:**

```json
{
  "ring of the azure:hibernia": {
    "merchant_zone": "Drake",
    "merchant_price": "500",
    "merchant_currency": "Scales"  // ← ADDED
  }
}
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

## Critical Bug Fixes

### 1. QThread Crash on Worker Termination

**Problem:** Application crashed when import worker thread terminated.

**Error:** `QThread: Destroyed while thread is still running`

**Root Cause:** Calling `deleteLater()` on worker before `finished` signal emitted and `wait()` completed.

**Solution:** Separate callbacks for business logic vs cleanup

```python
# BEFORE (BROKEN):
self.worker.finished.connect(self.on_import_finished)

def on_import_finished(self):
    # Business logic + cleanup mixed
    self.update_ui()
    self.worker.deleteLater()  # ❌ TOO EARLY

# AFTER (FIXED):
self.worker.import_finished.connect(self.on_import_finished)  # Custom signal
self.worker.finished.connect(self.on_thread_finished)         # QThread signal

def on_import_finished(self, success, message, ...):
    """Business logic only"""
    self.update_ui()

def on_thread_finished(self):
    """Cleanup only"""
    if self.worker:
        self.worker.wait(5000)      # ✅ Wait for thread
        self.worker.deleteLater()   # ✅ Safe now
        self.worker = None
```

**Files Fixed:**
- `UI/mass_import_monitor.py`
- `UI/failed_items_review_dialog.py`

### 2. QApplication.processEvents() Removal

**Problem:** Random crashes and UI freezes during mass import.

**Root Cause:** `QApplication.processEvents()` is dangerous in QThread context - can cause race conditions and deadlocks.

**Solution:** Remove ALL processEvents() calls, rely on proper signal/slot architecture

```python
# BEFORE (DANGEROUS):
for item in items:
    process_item(item)
    QApplication.processEvents()  # ❌ CRASH RISK

# AFTER (SAFE):
# Emit signals, let Qt handle event loop
self.progress.emit(current, total, message)
```

**Files Fixed:**
- `Functions/import_worker.py`
- `UI/mass_import_monitor.py`

### 3. TypeError in Template Import Dialog

**Problem:** `TypeError: 'PySide6.QtWidgets.QWidget.setEnabled' called with wrong argument types`

**Root Cause:** Python truthiness - empty string `""` is falsy but not `False` type

```python
# BEFORE (BROKEN):
description = self.description_edit.text()
can_import = self.selected_file and description and season != "Personnalisé..."
self.import_button.setEnabled(can_import)  # ❌ can_import might be ""

# AFTER (FIXED):
can_import = bool(self.selected_file is not None and 
                  description and 
                  season != "Personnalisé...")
self.import_button.setEnabled(can_import)  # ✅ Always True/False
```

**File Fixed:** `UI/template_import_dialog.py`

### 4. Language Manager Singleton Issue

**Problem:** Dialogs not translating when language changed.

**Root Cause:** Creating new `LanguageManager()` instances instead of using global singleton

```python
# BEFORE (BROKEN):
from Functions.language_manager import LanguageManager
lang = LanguageManager()  # ❌ New instance, not connected to global

# AFTER (FIXED):
from Functions.language_manager import lang  # ✅ Global singleton
```

**Files Fixed:**
- `UI/mass_import_monitor.py`
- `UI/failed_items_review_dialog.py`

### 5. Missing {count} Placeholder Replacement

**Problem:** Message displayed `"Prêt à importer {count} items"` instead of actual number.

**Root Cause:** Placeholder not passed to `lang.get()`

```python
# BEFORE (BROKEN):
message = lang.get("mass_import.ready_to_start")  # ❌ {count} not replaced

# AFTER (FIXED):
message = lang.get("mass_import.ready_to_start", count=len(items))  # ✅
```

**File Fixed:** `UI/mass_import_monitor.py`

### 6. Window Closing Entire Application

**Problem:** Closing Mass Import Monitor window closed entire application.

**Root Cause:** Default Qt behavior for QMainWindow/QDialog with application-level window management.

**Solution:** Set `Qt.WA_QuitOnClose` attribute to `False`

```python
# In MassImportMonitor.__init__:
self.setAttribute(Qt.WA_QuitOnClose, False)  # ✅ Don't quit app on close
```

**File Fixed:** `UI/mass_import_monitor.py`

### 7. Auto-Refresh Missing Prices Dialog

**Problem:** After successful price import, dialog still showed imported items.

**Root Cause:** No refresh mechanism after import completion.

**Solution:** Add `_refresh_items_list()` method called on import_finished signal

```python
def _refresh_items_list(self):
    """Reload template and refresh item list"""
    self._sync_template_prices_with_db()  # Sync JSON with DB
    self._load_template_items()           # Reload items
    self._filter_items()                  # Reapply filters
```

**File Fixed:** `UI/dialogs.py`

### 8. bypass_filters Flag Not Added to Duplicates

**Problem:** When retrying filtered items, duplicates weren't flagged with `bypass_filters: true`.

**Root Cause:** Conditional check missing in duplicate handling logic.

**Solution:** Add flag update when in skip_filters_mode

```python
if existing_item:
    # Item already exists
    if self.skip_filters_mode:
        # ADD bypass_filters flag for retry operation
        existing_item["bypass_filters"] = True
        db_manager.save_database()
```

**File Fixed:** `Functions/import_worker.py`

---

## Implementation Progress

### Phase 1-4: Core System Implementation ✅ COMPLETED

**Completed Features:**
- ✅ Data structures and configuration
- ✅ Contextual import interface
- ✅ Template list and filtering
- ✅ Advanced features (index, search)
- ✅ Mass import with monitoring
- ✅ Missing price search
- ✅ Retry system with bypass_filters
- ✅ Full multi-realm support
- ✅ Robust QThread architecture
- ✅ FR/EN/DE translations

### Phase 5: Migration and Testing 🔄 IN PROGRESS

**Completed:**
- ✅ Mass import system testing
- ✅ Price search testing
- ✅ Filtered items retry testing

**Pending:**
- [ ] Migration script for old templates
- [ ] Complete user documentation

### Phase 6: Cleanup and Polish 📅 PLANNED

**To Do:**
- [ ] Remove import code from Settings
- [ ] Integration in CharacterSheetWindow (Templates tab)
- [ ] UI polish (icons, tooltips)
- [ ] Final user testing

### Backend Components

**Created:**
- `Functions/template_metadata.py` - Metadata management
- `Functions/template_manager.py` - Main manager (CRUD, filtering, index)
- `Functions/config_manager.py` - Season methods
- `Functions/import_worker.py` - QThread worker with bypass_filters
- `Functions/items_database_manager.py` - Database manager (dual-mode)
- `Functions/items_scraper.py` - Eden scraper with multi-realm filtering
- `Functions/build_items_database.py` - DB builder with level≥50 and utility≥100 filters

**Modified:**
- `Functions/config_manager.py` - Added `get_current_season()`, `get_available_seasons()`, `add_season()`, `set_current_season()`

### UI Components

**Created:**
- `UI/template_import_dialog.py` - Contextual import dialog
- `UI/widgets/tag_selector.py` - Tag selection widget
- `UI/widgets/template_list_widget.py` - Template list with search/filter
- `UI/dialogs/template_preview_dialog.py` - Preview dialog
- `UI/mass_import_monitor.py` - Mass import monitor with manual start
- `UI/failed_items_review_dialog.py` - Filtered items review with retry

**Modified:**
- `UI/dialogs.py` - Added SearchMissingPricesDialog and price sync

### Translation Support

**Added 6 new sections** in `Language/{fr,en,de}.json`:
- `template_import` - Import interface (17 keys)
- `template_list` - List and filters (14 keys)
- `template_preview` - Preview dialog (13 keys)
- `mass_import` - Mass import (20+ keys)
- `failed_items_review` - Filtered items review (15+ keys)
- `search_missing_prices` - Missing price search (10+ keys)

**Language Fixes:**
- Fixed LanguageManager singleton (use global `lang` instead of creating new instances)
- Full support for dynamic language switching with retranslate_ui()

### Configuration

Uses existing `game` section in `config.json`:
```json
{
  "game": {
    "seasons": ["S3"],
    "default_season": "S3"
  }
}
```

### Breaking Changes

**Removed (future version):**
- ❌ Template import from Settings (will be removed, import only from character sheet)

**Preserved:**
- ✅ Current armor display in character sheet (design unchanged)
- ✅ Items database (unchanged)
- ✅ Scraping system (unchanged)

---

## Commit History

### Branch 108_Imp_Armo - 21 Commits

1. **963caed** - `feat: add manual start button and fix language support in mass import`
   - Added manual "Start Import" button in mass import monitor
   - Fixed LanguageManager singleton (global lang)
   - Separated on_import_finished/on_thread_finished callbacks
   - Fixed {count} placeholder replacement

2. **68a839d** - `fix: prevent app crash when retry worker thread terminates`
   - QThread cleanup with wait(5000) before deleteLater()
   - Separated import vs thread finished callbacks

3. **1c53912** - `feat: auto-sync template prices with DB and fix missing currency display`
   - Automatic price sync JSON ↔ DB
   - Added merchant_currency with zone-based fallback
   - Auto-refresh SearchMissingPricesDialog

4. **71cffc8** - `fix: TypeError in template import dialog and auto-refresh missing prices list`
   - bool() wrapping for setEnabled()
   - Auto-refresh after successful import

5. **16851dd** - `feat: Add online price search for armor templates with JSON metadata storage`
   - SearchMissingPricesDialog
   - Price storage in metadata JSON
   - Manual missing price import

6. **c7a85ae** - `Fix: Implement language switching for bulk action buttons and dialogs`
   - Dynamic language switching support
   - retranslate_ui() for all dialogs

7. **0b751bd** - `docs(items): Update technical documentation with mass import threading fixes`
   - QThread architecture documentation

8. **4f3b84f** - `fix(mass-import): Remove dangerous QApplication.processEvents() calls`
   - Removed processEvents() (crash risk)
   - Improved QThread stability

9. **7c170f5** - `fix(ui): resolve retry crash and improve dialog UX in mass import monitor`
   - Fixed retry worker crash
   - Qt.WA_QuitOnClose(False)

10. **57ab579** - `feat(mass-import): add ignore items system with retry improvements`
    - bypass_filters system
    - FailedItemsReviewDialog
    - Automatic retry with flag

11. **d7d605e** - `fix(items): unified mass import with multi-variant logic`
    - Multi-realm item support
    - Unified Text Files + Zenkcraft import

12. **25c6146** - `feat(armory): implement character-centric template system with realm organization`
    - Realm-based organization (Hibernia/Albion/Midgard/)
    - Contextual import from character sheet
    - Metadata JSON with tags and seasons

13. **a8cce6d** - `feat(items): Complete items database system with multi-realm support`
    - Database v2.0 composite keys
    - Complete technical documentation

14. **11f4917 to f32dd51** - System foundations (DB, scraper, dual-mode)

**Statistics:**
- **21 commits** total
- **108 items** in database (vs 92 before)
- **6 translation sections** added
- **8 critical bugs** fixed
- **3 new UI dialogs**
- **Thread-safe** complete architecture

---

**End of Document** - For more details, see:
- [ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md](../Items/ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md)
- [ITEMS_SCRAPER_TECHNICAL_EN.md](ITEMS_SCRAPER_TECHNICAL_EN.md)
- [ITEMS_PARSER_EN.md](ITEMS_PARSER_EN.md)

**Developer:** GitHub Copilot  
**Created:** November 19, 2025  
**Last Updated:** November 20, 2025  
**Version:** 2.0  
**Branch:** 108_Imp_Armo
