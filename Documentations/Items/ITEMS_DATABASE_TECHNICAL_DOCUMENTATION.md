# Items Database - Technical Documentation
**Version:** 2.0  
**Last Updated:** 2025-11-19  
**Project:** DAOC Character Management  
**Component:** Items Database & Eden Scraping System

---

## Table of Contents

1. [Overview](#overview)
2. [Database Architecture](#database-architecture)
3. [Scraping Methodology](#scraping-methodology)
4. [Technical Implementation](#technical-implementation)
5. [Data Flow & Processing](#data-flow--processing)
6. [API Reference](#api-reference)
7. [Configuration & Mappings](#configuration--mappings)
8. [Best Practices](#best-practices)

---

## 1. Overview

### 1.1 Purpose

The Items Database system provides automated scraping and management of game items from Eden-DAOC's online database. It handles:

- **Multi-realm item discovery** (Albion, Hibernia, Midgard, All)
- **Automated data extraction** with strict filtering
- **Database persistence** with composite key architecture
- **Merchant information tracking** with zone/currency mapping
- **Dual-mode operation** (internal read-only or personal user-managed)

### 1.2 Key Features

✅ **Multi-Realm Support**: Handles items existing in multiple realms  
✅ **Strict Filtering**: Level ≥50, Utility ≥100, exact name matching  
✅ **Data Preservation**: Non-destructive database updates  
✅ **Currency Mapping**: Automatic zone-to-currency conversion  
✅ **Debug Mode**: Selective item refresh for testing  
✅ **Dual-Mode Architecture**: Read-only internal or user-managed personal database  
✅ **Auto-Add Scraped Items**: Optional automatic persistence of scraped data

### 1.3 Dual-Mode Database Architecture

The system implements a **dual-mode database architecture** allowing users to choose between:

#### Mode 1: Internal Database (Read-Only)

**Location:** `Data/items_database_src.json`

**Capabilities:**
- ✅ Search items by name, realm, type
- ✅ View item statistics
- ✅ Scrape items from Eden (temporary storage)
- ✅ Export scraped items to files

**Limitations:**
- ❌ Cannot save scraped items permanently
- ❌ Cannot modify existing items
- ❌ Cannot add custom items
- ❌ No import functionality

**Use Cases:**
- Casual users who don't need data persistence
- Temporary item lookups during gameplay
- Testing/validation without data modification
- Portable installations without write access

#### Mode 2: Personal Database (User-Managed)

**Location:** `Armory/items_database.json`

**Capabilities:**
- ✅ All Mode 1 capabilities
- ✅ **Persistent storage** of scraped items
- ✅ **Auto-add scraped items** (configurable)
- ✅ **Import items** from template files
- ✅ Add custom items manually
- ✅ Modify existing items
- ✅ Reset to internal database copy

**Additional Features:**
- Statistics tracking (internal vs. personal vs. user-added)
- Database version management
- Automatic backups on reset

**Use Cases:**
- Power users building personal item databases
- Guild leaders maintaining shared item lists
- Theorycrafters with custom item data
- Long-term data collection and analysis

#### Mode Configuration

The active mode is controlled by the configuration:
```json
{
  "armory": {
    "use_personal_database": false,  // Mode 1 (default)
    "use_personal_database": true    // Mode 2
  }
}
```

### 1.3 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITEMS DATABASE SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Eden-DAOC   │────────>│   Scraper    │────────>│   Database   │
│  (Web Source)│  HTTP   │  (Selenium)  │  JSON   │   Manager    │
└──────────────┘         └──────────────┘         └──────────────┘
      │                         │                         │
      │ HTML Pages              │ BeautifulSoup          │ Dual-Mode
      │ Search Results          │ Data Extraction        │ ┌─────────┐
      │ Item Details            │ Filtering              │ │ Mode 1  │
      └─────────────────────────┴────────────────────────┘ │ Internal│
                                                            │(R/O)    │
                                                            └─────────┘
                                                            ┌─────────┐
                                                            │ Mode 2  │
                                                            │ Personal│
                                                            │(R/W)    │
                                                            └─────────┘

DATABASE MANAGER ARCHITECTURE
┌─────────────────────────────────────────────────────────────────┐
│                    ItemsDatabaseManager                         │
├─────────────────────────────────────────────────────────────────┤
│  Mode Detection:                                                │
│    ├─> use_personal_database = False → Internal DB              │
│    └─> use_personal_database = True  → Personal DB              │
├─────────────────────────────────────────────────────────────────┤
│  Core Methods:                                                  │
│    ├─> get_active_database_path()    → Returns active DB path  │
│    ├─> search_item()                 → Search in active DB     │
│    ├─> create_personal_database()    → Copy internal → personal│
│    ├─> add_scraped_item()            → Add to personal DB      │
│    ├─> get_statistics()              → DB stats (counts)       │
│    └─> reset_personal_database()     → Restore from internal   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Database Architecture

### 2.1 Database Structure

**File:** `Data/items_database_src.json`

```json
{
  "version": "2.0",
  "description": "DAOC Items Database - Multi-Realm Support",
  "last_updated": "2025-11-19 12:00:00",
  "item_count": 32,
  "notes": [
    "Composite keys format: 'item_name:realm' (lowercase)",
    "Only essential data: ID, name, realm, slot, type, model, damage info, merchant",
    "No stats, resistances, bonuses, level, or quality"
  ],
  "items": {
    "cloth cap:hibernia": { /* Item data */ },
    "cudgel of the undead:albion": { /* Item data */ }
  }
}
```

### 2.2 Composite Key System

**Format:** `"{item_name}:{realm}"` (lowercase)

**Examples:**
- `"cloth cap:albion"` → Cloth Cap (Albion version)
- `"cloth cap:hibernia"` → Cloth Cap (Hibernia version)
- `"soulbinder's belt:all"` → Soulbinder's Belt (common to all realms)

**Key Generation:**
```python
def _get_cache_key(item_name, realm=None):
    normalized_name = item_name.strip().lower()
    normalized_realm = (realm or "All").strip().lower()
    return f"{normalized_name}:{normalized_realm}"
```

### 2.3 Item Data Schema

Each item entry contains **13 fields**:

```json
{
  "id": "163421",                    // Eden item ID
  "name": "Cloth Cap",               // Display name (original case)
  "realm": "Hibernia",               // Albion|Hibernia|Midgard|All
  "slot": "Helm",                    // Equipment slot
  "type": "Cloth",                   // Item type
  "model": "4063",                   // 3D model ID
  "dps": null,                       // Damage per second (weapons only)
  "speed": null,                     // Attack speed (weapons only)
  "damage_type": null,               // Crush|Slash|Thrust (weapons only)
  "usable_by": "ALL",                // Classes or "ALL"
  "merchant_zone": "Drake",          // Merchant zone abbreviation
  "merchant_price": "500",           // Price in zone currency
  "merchant_currency": "Scales",     // Currency name
  "source": "internal"               // Data source identifier
}
```

### 2.4 Field Specifications

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | ✅ Yes | - | Eden database ID |
| `name` | string | ✅ Yes | - | Item name (original case) |
| `realm` | string | ✅ Yes | - | Item realm |
| `slot` | string | ✅ Yes | "Unknown" | Equipment slot |
| `type` | string | ❌ No | null | Item type/category |
| `model` | string | ❌ No | null | 3D model ID |
| `dps` | string | ❌ No | null | Damage per second |
| `speed` | string | ❌ No | null | Weapon speed |
| `damage_type` | string | ❌ No | null | Damage type |
| `usable_by` | string | ✅ Yes | "ALL" | Usable classes |
| `merchant_zone` | string | ❌ No | null | Merchant zone |
| `merchant_price` | string | ❌ No | null | Item price |
| `merchant_currency` | string | ❌ No | null | Currency type |
| `item_category` | string | ❌ No | null | Category for priceless items |
| `ignore_item` | bool | ❌ No | false | Skip price searches |
| `source` | string | ✅ Yes | "internal" | Data source |

---

## 2.5 Item Categorization System

### Overview

The Item Categorization System allows users to categorize items found in Eden without merchant prices (quest rewards, event rewards) instead of showing generic "❓ Unknown" marker.

### Categories

**Available Categories:**

| Key | Icon | Label (EN) | Label (FR) | Label (DE) |
|-----|------|-----------|-----------|------------|
| `quest_reward` | 🏆 | Quest Reward | Quest Reward | Questbelohnung |
| `event_reward` | 🎉 | Event Reward | Event Reward | Event-Belohnung |
| `unknown` | ❓ | Unknown | Unknown | Unbekannt |

**Storage:** `Functions/items_database_manager.py` - `ITEM_CATEGORIES` constant

### Database Fields

#### item_category

**Type:** `string` (optional)  
**Values:** `"quest_reward"`, `"event_reward"`, `"unknown"`, or `null`  
**Purpose:** Categorize items without merchant prices

**Example:**
```json
{
  "battled mantle of samhain:hibernia": {
    "id": "172635",
    "name": "Battled Mantle of Samhain",
    "item_category": "quest_reward"
  }
}
```

#### ignore_item

**Type:** `boolean` (optional)  
**Default:** `false`  
**Purpose:** Exclude item from future price searches

**Auto-Set:** Automatically set to `true` when `item_category` is assigned

**Use Cases:**
- Quest rewards (no merchants, never will have price)
- Event rewards (seasonal items)
- Known priceless items (avoid repeated search failures)

**Example:**
```json
{
  "hibernia medal of honor:hibernia": {
    "id": "172641",
    "name": "Hibernia Medal of Honor",
    "item_category": "quest_reward",
    "ignore_item": true
  }
}
```

### API Methods

**File:** `Functions/items_database_manager.py`

#### get_item_categories()

```python
def get_item_categories() -> dict:
    """
    Get all available item categories.
    
    Returns:
        dict: ITEM_CATEGORIES constant with icon/label_en/label_fr/label_de
    """
```

#### get_category_label()

```python
def get_category_label(category_key: str, language: str = "en") -> str:
    """
    Get localized label for category.
    
    Args:
        category_key: Category key (quest_reward/event_reward/unknown)
        language: Language code (en/fr/de)
    
    Returns:
        str: Localized label or "Unknown" if not found
    
    Example:
        >>> get_category_label("quest_reward", "en")
        "Quest Reward"
    """
```

#### get_category_icon()

```python
def get_category_icon(category_key: str) -> str:
    """
    Get emoji icon for category.
    
    Args:
        category_key: Category key
    
    Returns:
        str: Emoji icon (🏆/🎉/❓)
    
    Example:
        >>> get_category_icon("quest_reward")
        "🏆"
    """
```

#### set_item_category()

```python
def set_item_category(item_name: str, realm: str, category: str) -> bool:
    """
    Set item category and ignore_item flag.
    
    Args:
        item_name: Item name
        realm: Item realm (Albion/Hibernia/Midgard/All)
        category: Category key (quest_reward/event_reward/unknown)
    
    Returns:
        bool: True if successful, False otherwise
    
    Side Effects:
        - Sets item_category field
        - Sets ignore_item to True
        - Saves database
    
    Example:
        >>> set_item_category("Battled Mantle of Samhain", "Hibernia", "quest_reward")
        True
    """
```

### User Workflow

**Categorization Entry Points:**

1. **Search Missing Prices Dialog** (`UI/dialogs.py`)
   ```
   User Action: Select item → Click "Ignore" button
   Result: ItemCategoryDialog opens
   ```

2. **Failed Items Review Dialog** (`UI/failed_items_review_dialog.py`)
   ```
   User Action: Select filtered item → Click "Ignore" button
   Result: ItemCategoryDialog opens
   ```

**ItemCategoryDialog Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│  Categorize Item                              [✖]        │
├─────────────────────────────────────────────────────────────┤
│  Item: Battled Mantle of Samhain (Hibernia)                │
│                                                              │
│  Select a category:                                │
│  ○ 🏆 Quest Reward                                   │
│  ○ 🎉 Event Reward                                │
│  ○ ❓ Unknown                                                │
│                                                              │
│  [✖ Annuler]  [✔ Valider]                                   │
└─────────────────────────────────────────────────────────────┘

1. User selects category (QRadioButton)
2. Clicks "OK"
3. Database updated:
   - item_category = selected category
   - ignore_item = True
4. Dialog closes
5. Item removed from search results (if in Search Missing Prices)
```

### Display Integration

**Template Preview** (`UI/dialogs.py` - `ArmorManagementDialog`)

**Before Categorization:**
```
📊 Battled Mantle             ❓ Unknown              [DB]
```

**After Categorization (quest_reward):**
```
📊 Battled Mantle             🏆 Quest Reward         [DB]
```

**Implementation:**
```python
def get_item_price(item_name: str, realm: str) -> tuple:
    """Returns (price_str, source, category)"""
    
    # Search database (realm-aware)
    db_item = search_item_in_db(item_name, realm)
    
    if db_item:
        category = db_item.get('item_category')
        if category:
            icon = get_category_icon(category)
            label = get_category_label(category, current_language)
            return (f"{icon} {label}", "db", category)
        
        # Has merchant price
        if db_item.get('merchant_price'):
            price = db_item['merchant_price']
            currency = db_item['merchant_currency']
            return (f"💰 {price} {currency}", "db", None)
    
    # No data found
    return ("❓ Unknown", "default", "unknown")
```

### Best Practices

#### ✅ DO: Categorize Quest/Event Items

```python
# Items that will NEVER have merchant prices
quest_items = [
    "Battled Mantle of Samhain",
    "Hibernia Medal of Honor",
    "Epic Quest Reward Item"
]

# Set category to prevent repeated search failures
for item in quest_items:
    set_item_category(item, realm, "quest_reward")
```

#### ✅ DO: Use Unknown for Temporary Items

```python
# Items you're not sure about yet
set_item_category("Mystery Item", realm, "unknown")
# Can recategorize later when confirmed
```

#### ❌ DON'T: Categorize Items with Merchants

```python
# WRONG: Item has merchant price
item_data = {
    "merchant_price": "125",
    "merchant_currency": "Scales",
    "item_category": "quest_reward"  # ← Contradictory!
}

# CORRECT: Only categorize priceless items
if not item.get('merchant_price'):
    set_item_category(item_name, realm, category)
```

#### ✅ DO: Respect ignore_item Flag

```python
# When searching for missing prices
for item in template_items:
    db_item = search_item(item)
    
    if db_item and db_item.get('ignore_item'):
        continue  # Skip this item, already categorized
    
    # Proceed with price search
    scrape_item_price(item)
```

---

## 2.5 Item Categorization System

### Overview

The Item Categorization System allows users to categorize items found in Eden without merchant prices (quest rewards, event rewards) instead of showing generic "❓ Unknown" marker.

### Categories

**Available Categories:**

| Key | Icon | Label (EN) | Label (FR) | Label (DE) |
|-----|------|-----------|-----------|------------|
| `quest_reward` | 🏆 | Quest Reward | Quest Reward | Questbelohnung |
| `event_reward` | 🎉 | Event Reward | Event Reward | Event-Belohnung |
| `unknown` | ❓ | Unknown | Unknown | Unbekannt |

**Storage:** `Functions/items_database_manager.py` - `ITEM_CATEGORIES` constant

### Database Fields

#### item_category

**Type:** `string` (optional)  
**Values:** `"quest_reward"`, `"event_reward"`, `"unknown"`, or `null`  
**Purpose:** Categorize items without merchant prices

**Example:**
```json
{
  "battled mantle of samhain:hibernia": {
    "id": "172635",
    "name": "Battled Mantle of Samhain",
    "item_category": "quest_reward"
  }
}
```

#### ignore_item

**Type:** `boolean` (optional)  
**Default:** `false`  
**Purpose:** Exclude item from future price searches

**Auto-Set:** Automatically set to `true` when `item_category` is assigned

**Use Cases:**
- Quest rewards (no merchants, never will have price)
- Event rewards (seasonal items)
- Known priceless items (avoid repeated search failures)

**Example:**
```json
{
  "hibernia medal of honor:hibernia": {
    "id": "172641",
    "name": "Hibernia Medal of Honor",
    "item_category": "quest_reward",
    "ignore_item": true
  }
}
```

### API Methods

**File:** `Functions/items_database_manager.py`

#### get_item_categories()

```python
def get_item_categories() -> dict:
    """
    Get all available item categories.
    
    Returns:
        dict: ITEM_CATEGORIES constant with icon/label_en/label_fr/label_de
    """
```

#### get_category_label()

```python
def get_category_label(category_key: str, language: str = "en") -> str:
    """
    Get localized label for category.
    
    Args:
        category_key: Category key (quest_reward/event_reward/unknown)
        language: Language code (en/fr/de)
    
    Returns:
        str: Localized label or "Unknown" if not found
    
    Example:
        >>> get_category_label("quest_reward", "en")
        "Quest Reward"
    """
```

#### get_category_icon()

```python
def get_category_icon(category_key: str) -> str:
    """
    Get emoji icon for category.
    
    Args:
        category_key: Category key
    
    Returns:
        str: Emoji icon (🏆/🎉/❓)
    
    Example:
        >>> get_category_icon("quest_reward")
        "🏆"
    """
```

#### set_item_category()

```python
def set_item_category(item_name: str, realm: str, category: str) -> bool:
    """
    Set item category and ignore_item flag.
    
    Args:
        item_name: Item name
        realm: Item realm (Albion/Hibernia/Midgard/All)
        category: Category key (quest_reward/event_reward/unknown)
    
    Returns:
        bool: True if successful, False otherwise
    
    Side Effects:
        - Sets item_category field
        - Sets ignore_item to True
        - Saves database
    
    Example:
        >>> set_item_category("Battled Mantle of Samhain", "Hibernia", "quest_reward")
        True
    """
```

### User Workflow

**Categorization Entry Points:**

1. **Search Missing Prices Dialog** (`UI/dialogs.py`)
   ```
   User Action: Select item → Click "Ignore" button
   Result: ItemCategoryDialog opens
   ```

2. **Failed Items Review Dialog** (`UI/failed_items_review_dialog.py`)
   ```
   User Action: Select filtered item → Click "Ignore" button
   Result: ItemCategoryDialog opens
   ```

**ItemCategoryDialog Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│  Categorize Item                              [✖]        │
├─────────────────────────────────────────────────────────────┤
│  Item: Battled Mantle of Samhain (Hibernia)                │
│                                                              │
│  Select a category:                                │
│  ○ 🏆 Quest Reward                                   │
│  ○ 🎉 Event Reward                                │
│  ○ ❓ Unknown                                                │
│                                                              │
│  [✖ Annuler]  [✔ Valider]                                   │
└─────────────────────────────────────────────────────────────┘

1. User selects category (QRadioButton)
2. Clicks "OK"
3. Database updated:
   - item_category = selected category
   - ignore_item = True
4. Dialog closes
5. Item removed from search results (if in Search Missing Prices)
```

### Display Integration

**Template Preview** (`UI/dialogs.py` - `ArmorManagementDialog`)

**Before Categorization:**
```
📊 Battled Mantle             ❓ Unknown              [DB]
```

**After Categorization (quest_reward):**
```
📊 Battled Mantle             🏆 Quest Reward         [DB]
```

**Implementation:**
```python
def get_item_price(item_name: str, realm: str) -> tuple:
    """Returns (price_str, source, category)"""
    
    # Search database (realm-aware)
    db_item = search_item_in_db(item_name, realm)
    
    if db_item:
        category = db_item.get('item_category')
        if category:
            icon = get_category_icon(category)
            label = get_category_label(category, current_language)
            return (f"{icon} {label}", "db", category)
        
        # Has merchant price
        if db_item.get('merchant_price'):
            price = db_item['merchant_price']
            currency = db_item['merchant_currency']
            return (f"💰 {price} {currency}", "db", None)
    
    # No data found
    return ("❓ Unknown", "default", "unknown")
```

### Best Practices

#### ✅ DO: Categorize Quest/Event Items

```python
# Items that will NEVER have merchant prices
quest_items = [
    "Battled Mantle of Samhain",
    "Hibernia Medal of Honor",
    "Epic Quest Reward Item"
]

# Set category to prevent repeated search failures
for item in quest_items:
    set_item_category(item, realm, "quest_reward")
```

#### ✅ DO: Use Unknown for Temporary Items

```python
# Items you're not sure about yet
set_item_category("Mystery Item", realm, "unknown")
# Can recategorize later when confirmed
```

#### ❌ DON'T: Categorize Items with Merchants

```python
# WRONG: Item has merchant price
item_data = {
    "merchant_price": "125",
    "merchant_currency": "Scales",
    "item_category": "quest_reward"  # ← Contradictory!
}

# CORRECT: Only categorize priceless items
if not item.get('merchant_price'):
    set_item_category(item_name, realm, category)
```

#### ✅ DO: Respect ignore_item Flag

```python
# When searching for missing prices
for item in template_items:
    db_item = search_item(item)
    
    if db_item and db_item.get('ignore_item'):
        continue  # Skip this item, already categorized
    
    # Proceed with price search
    scrape_item_price(item)
```

---

## 3. Scraping Methodology

### 3.1 Multi-Realm Item Discovery

**Challenge:** Items can exist in multiple realms with different IDs.

**Example:** "Cudgel of the Undead"
- Albion: ID 139625
- Hibernia: ID 117565
- Midgard: ID 112493

**Solution:** Search ALL realms (`r=0`), parse ALL results, create separate entries.

### 3.2 Scraping Process Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPING PROCESS FLOW                        │
└─────────────────────────────────────────────────────────────────┘

INPUT: item_name = "Cloth Cap"
   │
   ├──> STEP 1: Search ALL Realms
   │    URL: https://eden-daoc.net/items?s=Cloth%20Cap&r=0
   │    Result: 21 items (including false positives)
   │
   ├──> STEP 2: Parse HTML Results
   │    Extract: result_row elements
   │    Columns: Icon, Name, Type, Slot, Realm Icon, Classes, Level, Utility
   │
   ├──> STEP 3: Apply Strict Filters
   │    Filter 1: Exact name match (case-insensitive)
   │    Filter 2: Level ≥ 50
   │    Filter 3: Utility ≥ 100
   │    Filter 4: Realm icon present
   │    Result: 3 valid items
   │
   ├──> STEP 4: Extract Realm from Icon
   │    hibernia_logo.png → "Hibernia"
   │    midgard_logo.png → "Midgard"
   │    albion_logo.png → "Albion"
   │
   ├──> STEP 5: Scrape Details for Each Variant
   │    URL: https://eden-daoc.net/items?id={item_id}
   │    Extract: slot, type, model, merchant info, etc.
   │
   └──> STEP 6: Save to Database
        Key: "cloth cap:hibernia" → Item data
        Key: "cloth cap:midgard" → Item data
        Key: "cloth cap:albion" → Item data

OUTPUT: 3 database entries created
```

### 3.3 Four Strict Filters

**All filters must pass for an item to be accepted.**

#### Filter 1: Exact Name Match

**Purpose:** Eliminate false positives from Eden's broad search.

**Implementation:**
```python
found_name = row.find_all('td')[1].get_text(strip=True)
if found_name.lower() != item_name.lower():
    continue  # REJECT
```

**Example:**
- Search: "Cloth Cap"
- ✅ ACCEPT: "Cloth Cap"
- ❌ REJECT: "Lightning Embossed Cloth Cap"
- ❌ REJECT: "Gossamer Cloth Cap"

#### Filter 2: Level ≥ 50

**Purpose:** Only endgame items.

**Implementation:**
```python
# Dynamic column detection
for idx, text in enumerate(cells_text):
    val = int(text)
    if 1 <= val <= 51:
        level = val
        level_idx = idx  # Remember column
        break

if level < 50:
    continue  # REJECT
```

**Example:**
- ✅ ACCEPT: Level 50, 51
- ❌ REJECT: Level 45, 35, 10

#### Filter 3: Utility ≥ 100

**Purpose:** Minimum quality threshold.

**Implementation:**
```python
# Skip level column to avoid confusion
for idx, text in enumerate(cells_text):
    if level_idx is not None and idx == level_idx:
        continue  # Skip level column
    val = float(text)
    if val >= 50:
        utility = val
        break

if utility < 100:
    continue  # REJECT
```

**Example:**
- ✅ ACCEPT: Utility 100, 108.5, 150
- ❌ REJECT: Utility 85.7, 66.0

#### Filter 4: Realm Icon Present

**Purpose:** Mandatory realm identification.

**Implementation:**
```python
realm_img = row.find('img', src=re.compile(
    r'(albion_logo|hibernia_logo|midgard_logo|all_logo)\.png'
))

if not realm_img:
    continue  # REJECT - No icon = unknown realm
```

**Icon Mapping:**
```
albion_logo.png    → "Albion"    (Albion-only item)
hibernia_logo.png  → "Hibernia"  (Hibernia-only item)
midgard_logo.png   → "Midgard"   (Midgard-only item)
all_logo.png       → "All"       (Common item, same ID for all realms)
```

**Example:**
- ✅ ACCEPT: `<img src="hrald/img/hibernia_logo.png">`
- ❌ REJECT: No `<img>` tag in realm column

### 3.4 HTML Structure Analysis

**Search Results Page:**

```html
<table id="table_result">
  <tr id="result_row_163421" class="result_row">
    <td class="item_icon">...</td>                    <!-- Column 0: Item icon -->
    <td class="nowrap">Cloth Cap</td>                 <!-- Column 1: Name -->
    <td class="nowrap">Cloth</td>                     <!-- Column 2: Type -->
    <td class="nowrap">Helm</td>                      <!-- Column 3: Slot -->
    <td class="realm_logo">                           <!-- Column 4: Realm icon -->
      <img src="hrald/img/hibernia_logo.png">
    </td>
    <td class="class_icon">...</td>                   <!-- Column 5: Class icon -->
    <td class="nowrap">All</td>                       <!-- Column 6: Classes -->
    <td class="nowrap center">51</td>                 <!-- Column 7: Level -->
    <td class="nowrap center">108.5</td>              <!-- Column 8: Utility -->
  </tr>
</table>
```

**Item Details Page:**

```html
<table id="item_details">
  <tr><td>Slot:</td><td>Helm</td></tr>
  <tr><td>Type:</td><td>Cloth</td></tr>
  <tr><td>Model:</td><td>4063</td></tr>
  <tr><td>Usable by:</td><td>ALL</td></tr>
</table>

<table id="table_merchants">
  <div class="item_mob">
    <tr><td>Name:</td><td>Dragon Merchant</td></tr>
    <tr><td>Zone:</td><td>Dragon's Lair</td></tr>
    <tr><td>Price:</td><td>500 Dragon Scales</td></tr>
  </div>
</table>
```

---

## 4. Technical Implementation

### 4.1 Browser Configuration

#### Isolated Chrome Profile

**Purpose:** Separate profile to avoid conflicts with user's main Chrome browser.

**Path:** `AppData/Eden/ChromeProfile/EdenScraper`

**Chrome Flags:**
```python
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-position=-32000,-32000")  # Minimize
```

**Browser Mode:**
- **Headless:** `False` (Eden requires visible browser for some elements)
- **Minimized:** `True` (faster rendering, Eden compatible)
- **Cookie Support:** Persistent cookies stored in profile

**Benefits:**
- ✅ No interference with user's Chrome sessions
- ✅ Persistent login state (cookies saved)
- ✅ Faster subsequent scraping sessions
- ✅ Isolated cache and history

#### Wait Strategies

**Explicit Waits:**
```python
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "table_result"))
)
```

**Timeout Configuration:**
- Default timeout: 15 seconds
- Configurable per operation
- Prevents indefinite hangs on network issues

### 4.2 Core Components

#### ItemsScraper Class

**File:** `Functions/items_scraper.py`

**Dependencies:**
- `EdenScraper` - Chrome WebDriver management
- `BeautifulSoup4` - HTML parsing
- `Selenium` - Browser automation

**Responsibilities:**
- Search items on Eden-DAOC
- Parse HTML results with BeautifulSoup
- Extract item details
- Apply strict filters
- Manage realm detection
- Handle merchant data extraction

**Key Methods:**

```python
class ItemsScraper:
    def __init__(self, eden_scraper):
        """
        Initialize with EdenScraper instance.
        
        Args:
            eden_scraper: Instance of EdenScraper with active WebDriver
        """
    
    def navigate_to_market(self) -> bool:
        """
        Navigate to Eden items database.
        
        URL: https://eden-daoc.net/items
        
        Process:
            1. Navigate to items page
            2. Wait for page load (WebDriverWait)
            3. Save debug HTML to Logs/items_search_debug/market_page.html
        
        Returns:
            bool: True on success, False on failure
        """
    
    def find_all_item_variants(self, item_name: str) -> List[Dict]:
        """
        Find ALL realm variants of an item.
        Used for database population.
        
        Process:
            1. Search with r=0 (ALL realms)
            2. Parse all result_row elements
            3. Apply 4 strict filters
            4. Extract ID and realm from each valid result
        
        Returns:
            List[Dict]: List of variant dictionaries
            [
                {'id': '163421', 'realm': 'Hibernia', 'name': 'Cloth Cap'},
                {'id': '163452', 'realm': 'Midgard', 'name': 'Cloth Cap'},
                {'id': '163480', 'realm': 'Albion', 'name': 'Cloth Cap'}
            ]
        """
    
    def find_item_for_realm(self, item_name: str, realm: str) -> Dict:
        """
        Find ONE specific variant for a given realm.
        Used for targeted character searches (future use).
        
        Args:
            item_name (str): Item name to search
            realm (str): Specific realm (Albion/Hibernia/Midgard)
        
        Returns:
            Dict: Single variant dictionary
            {'id': '163421', 'realm': 'Hibernia', 'name': 'Cloth Cap'}
        """
        
    def get_item_details(self, item_id: str, realm: str, item_name: str) -> Dict:
        """
        Scrape full item details from item page.
        
        Args:
            item_id (str): Eden item ID
            realm (str): Item realm
            item_name (str): Item name (for logging)
        
        Process:
            1. Navigate to item page (?id={item_id})
            2. Parse item_line_left/right table rows
            3. Extract: slot, type, model, dps, speed, damage_type
            4. Parse merchant information with zone overrides
            5. Save debug HTML to Logs/items_details_debug/
        
        Returns:
            Dict: Complete item data
            {
                'id': '163421',
                'name': 'Cloth Cap',
                'realm': 'Hibernia',
                'slot': 'Helm',
                'type': 'Cloth',
                'model': '4063',
                'usable_by': 'ALL',
                'merchant_zone': 'Drake',
                'merchant_price': '500',
                'merchant_currency': 'Scales',
                ...
            }
        """
    
    def parse_merchant_price(self, price_str: str) -> Dict:
        """
        Parse merchant price string.
        
        Args:
            price_str (str): Price text (e.g., "100 Dragon Scales")
        
        Returns:
            Dict: Parsed price data
            {
                "amount": "100",
                "currency": "Dragon Scales",
                "display": "100 Dragon Scales"
            }
        """
    
    def _save_debug_html(self, filename: str):
        """
        Save current page HTML for debugging.
        
        Location: Logs/items_search_debug/ or Logs/items_details_debug/
        
        Files:
            - market_page.html - Items search page
            - search_results_{item_name}.html - Search results
            - item_{item_id}_clicked.html - Item details page
        """
```

#### Supported Currencies

The `parse_price()` method supports the following currencies:

| Currency | Example | Zone | Notes |
|----------|---------|------|-------|
| **Atlantean Glass** | "50 Atlantean Glass" | ToA | Trials of Atlantis |
| **Dragon Scales** | "100 Dragon Scales" | Drake | Dragon zones (normalized to "Scales") |
| **Seals** | "300 Seals" | DF | Darkness Falls |
| **Grimoire Pages** | "700 Grimoire Pages" | SH | Summoner's Hall (normalized to "Grimoires") |
| **Roots** | "250 Roots" | Epic | Galladoria |
| **Ices** | "600 Tuscaran Glacier Ices" | Epic | Tuscaran Glacier ⭐ **NEW** |
| **Souls** | "400 Souls" | Epic | Epic dungeons ⭐ **NEW** |
| **Aurulite** | "150 Aurulite" | - | Special currency |
| **Orbs** | "75 Orbs" | - | Special currency |
| **Bounty Points** | "100000 bounty points" | - | PvP currency |
| **Gold/Platinum** | "5p 50g" | - | Standard currency |

**Recent Additions (November 2025):**
- ✅ **Ices** - Added support for Tuscaran Glacier currency
- ✅ **Souls** - Added support for Epic dungeon currency

**Parsing Logic:**
```python
# Ices (Tuscaran Glacier)
if 'ice' in price_str:
    amount = int(price_str.split()[0])
    return {'currency': 'Ices', 'amount': amount, 'display': f"{amount} Ices"}

# Souls (Epic dungeon currency)
if 'soul' in price_str:
    amount = int(price_str.split()[0])
    return {'currency': 'Souls', 'amount': amount, 'display': f"{amount} Souls"}
```

**Example:**
```python
# Input: "600 Tuscaran Glacier Ices"
result = parse_price("600 Tuscaran Glacier Ices")
# Output: {'currency': 'Ices', 'amount': 600, 'display': '600 Ices'}

# Input: "400 Souls"
result = parse_price("400 Souls")
# Output: {'currency': 'Souls', 'amount': 400, 'display': '400 Souls'}
```

### 4.2 Filter Implementation Details

**Location:** `Functions/items_scraper.py` lines 875-1030

```python
def find_all_item_variants(self, item_name: str) -> List[Dict]:
    """Find ALL realm variants with strict filtering"""
    
    # Search URL: r=0 for ALL realms
    search_url = f"{self.base_url}?s={encoded_name}&r=0"
    
    # Navigate and wait for results
    self.driver.get(search_url)
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.ID, "table_result"))
    )
    
    # Parse HTML
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    result_rows = soup.find_all('tr', id=re.compile(r'^result_row_\d+$'))
    
    variants = []
    
    for row in result_rows:
        # Extract ID from row attribute
        row_id = row.get('id', '')
        match = re.search(r'result_row_(\d+)', row_id)
        if not match:
            continue
        item_id = match.group(1)
        
        # Extract all cell texts
        cells = row.find_all('td')
        cells_text = [cell.get_text(strip=True) for cell in cells]
        
        # ======== FILTER 1: EXACT NAME MATCH ========
        if len(cells_text) < 2:
            continue
        found_name = cells_text[1]
        if found_name.lower() != item_name.lower():
            self.logger.debug(f"⏭️ SKIP (wrong name): {found_name}")
            continue
        
        # ======== FILTER 2: LEVEL ≥ 50 ========
        level = None
        level_idx = None
        for idx, text in enumerate(cells_text):
            if idx <= 1:  # Skip icon and name columns
                continue
            try:
                val = int(text)
                if 1 <= val <= 51:
                    level = val
                    level_idx = idx
                    break
            except ValueError:
                continue
        
        if level is None or level < 50:
            self.logger.debug(f"⏭️ SKIP (level {level} < 50)")
            continue
        
        # ======== FILTER 3: UTILITY ≥ 100 ========
        utility = None
        for idx, text in enumerate(cells_text):
            if idx <= 1:
                continue
            if level_idx is not None and idx == level_idx:
                continue  # Skip level column
            try:
                val = float(text)
                if val >= 50:  # Utility values are typically 50+
                    utility = val
                    break
            except ValueError:
                continue
        
        if utility is None or utility < 100:
            self.logger.debug(f"⏭️ SKIP (utility {utility} < 100)")
            continue
        
        # ======== FILTER 4: REALM ICON PRESENT ========
        realm_img = row.find('img', src=re.compile(
            r'(albion_logo|hibernia_logo|midgard_logo|all_logo)\.png'
        ))
        
        if not realm_img:
            self.logger.warning(f"⚠️ No realm icon for ID {item_id}, SKIP")
            continue
        
        # Extract realm from icon
        src = realm_img.get('src', '')
        if 'albion_logo' in src:
            item_realm = 'Albion'
        elif 'hibernia_logo' in src:
            item_realm = 'Hibernia'
        elif 'midgard_logo' in src:
            item_realm = 'Midgard'
        elif 'all_logo' in src:
            item_realm = 'All'
        else:
            self.logger.warning(f"⚠️ Unknown realm icon: {src}, SKIP")
            continue
        
        # ======== ALL FILTERS PASSED ========
        variant = {
            'id': item_id,
            'realm': item_realm,
            'name': found_name
        }
        variants.append(variant)
        self.logger.debug(f"✓ Valid variant: {item_realm} → ID {item_id}")
    
    return variants
```

### 4.3 Merchant Data Extraction

**Location:** `Functions/items_scraper.py` lines 1175-1260

```python
def get_item_details(self, item_id: str, realm: str, item_name: str) -> Dict:
    """Extract complete item details including merchant info"""
    
    # ... navigate to item page ...
    
    # Parse merchants section
    merchants_table = soup.find('table', id='table_merchants')
    if merchants_table:
        merchant_divs = merchants_table.find_all('div', class_='item_mob')
        
        for merchant_div in merchant_divs:
            merchant_data = {
                'name': None,
                'zone': None,
                'zone_full': None,
                'price': None,
                'price_parsed': None
            }
            
            # Parse merchant rows
            merchant_rows = merchant_div.find_all('tr')
            for row in merchant_rows:
                row_text = row.get_text(strip=True)
                
                # Zone row (starts with "in ")
                if row_text.startswith('in '):
                    zone_full = row_text.replace('in ', '').split('Loc:')[0].strip()
                    zone_short = self.ZONE_MAPPING.get(zone_full, zone_full)
                    merchant_data['zone'] = zone_short
                    merchant_data['zone_full'] = zone_full
                
                # Price row
                elif row_text.startswith('Price:'):
                    price_text = row_text.replace('Price:', '').strip()
                    merchant_data['price'] = price_text
                    merchant_data['price_parsed'] = self.parse_price(price_text)
                    
                    # Override zone based on currency
                    if merchant_data['price_parsed']:
                        currency = merchant_data['price_parsed']['currency']
                        if currency == 'Atlantean Glass':
                            merchant_data['zone'] = 'ToA'
                        elif currency == 'Seals':
                            merchant_data['zone'] = 'DF'
                        elif currency in ['Roots', 'Souls', 'Ices']:
                            merchant_data['zone'] = 'Epic'
                        elif currency == 'Dragon Scales':
                            merchant_data['price_parsed']['currency'] = 'Scales'
                            merchant_data['zone'] = 'Drake'
                        elif currency == 'Scales':
                            merchant_data['zone'] = 'Drake'
                        elif currency == 'Grimoires':
                            merchant_data['zone'] = 'SH'
            
            if merchant_data['name']:
                item_data['merchants'].append(merchant_data)
    
    # Extract zone and currency for database
    if item_data['merchants']:
        first_merchant = item_data['merchants'][0]
        zone = first_merchant.get('zone')
        item_data['merchant_zone'] = zone
        
        if first_merchant.get('price_parsed'):
            item_data['merchant_price'] = str(
                first_merchant['price_parsed'].get('amount')
            )
        
        # Add currency based on zone
        item_data['merchant_currency'] = self.ZONE_CURRENCY.get(zone)
    
    return item_data
```

### 4.4 HTML Structure Analysis

**Search Results Page:**

```html
<table id="table_result">
  <tr id="result_row_163421" class="result_row">
    <td class="item_icon">...</td>                    <!-- Column 0: Item icon -->
    <td class="nowrap">Cloth Cap</td>                 <!-- Column 1: Name -->
    <td class="nowrap">Cloth</td>                     <!-- Column 2: Type -->
    <td class="nowrap">Helm</td>                      <!-- Column 3: Slot -->
    <td class="realm_logo">                           <!-- Column 4: Realm icon -->
      <img src="hrald/img/hibernia_logo.png">
    </td>
    <td class="class_icon">...</td>                   <!-- Column 5: Class icon -->
    <td class="nowrap">All</td>                       <!-- Column 6: Classes -->
    <td class="nowrap center">51</td>                 <!-- Column 7: Level -->
    <td class="nowrap center">108.5</td>              <!-- Column 8: Utility -->
  </tr>
</table>
```

**Item Details Page:**

```html
<table id="item_details">
  <tr><td>Slot:</td><td>Helm</td></tr>
  <tr><td>Type:</td><td>Cloth</td></tr>
  <tr><td>Model:</td><td>4063</td></tr>
  <tr><td>Usable by:</td><td>ALL</td></tr>
</table>

<table id="table_merchants">
  <div class="item_mob">
    <tr><td>Name:</td><td>Dragon Merchant</td></tr>
    <tr><td>Zone:</td><td>Dragon's Lair</td></tr>
    <tr><td>Price:</td><td>500 Dragon Scales</td></tr>
  </div>
</table>
```

**Name Extraction Challenge:**

The item name is in header row without specific class.

**Solution:**
```python
for row in all_rows:
    if row.find('td', class_='header'):
        nowrap_cells = row.find_all('td', class_='nowrap')
        for cell in nowrap_cells:
            # Skip cells with width style
            if not cell.get('style') or 'width' not in cell.get('style', ''):
                text = cell.get_text(strip=True)
                # Skip cells with digits (utility stats)
                if text and not any(char.isdigit() for char in text):
                    item_data['name'] = text
                    break
```

**Detail Rows Parsing Pattern:**

```python
# Pattern: item_line_left (label) + item_line_right (value)
left_cells = soup.find_all('td', class_='item_line_left')
right_cells = soup.find_all('td', class_='item_line_right')

for left, right in zip(left_cells, right_cells):
    label = left.get_text(strip=True).replace(':', '').lower()
    value = right.get_text(strip=True)
    
    if label == 'type':
        item_data['type'] = value
    elif label == 'slot':
        item_data['slot'] = value
    elif label == 'model':
        item_data['model'] = value
    # ... etc
```

### 4.5 Logging System

**Log Category:** All scraper logs use `extra={"action": "ITEMDB"}`

**Log Levels:**

| Level | Usage | Example |
|-------|-------|---------|
| **INFO** | Navigation, successful operations | `Navigation vers Eden items database` |
| **WARNING** | Item not found, missing data | `Item ID non trouvé: Cloth Cap` |
| **ERROR** | Scraping failures, exceptions | `Erreur navigation market: Timeout` |
| **DEBUG** | Detailed filter results | `⏭️ SKIP (utility 85.7 < 100)` |

**Log Examples:**
```python
logging.info("Navigation vers Eden items database", extra={"action": "ITEMDB"})
logging.warning(f"Item ID non trouvé: {item_name}", extra={"action": "ITEMDB"})
logging.error(f"Erreur navigation market: {e}", extra={"action": "ITEMDB"})
logging.debug(f"⏭️ SKIP (level {level} < 50)")
```

**Debug HTML Files:**

**Location:** 
- `Logs/items_search_debug/` - Search pages
- `Logs/items_details_debug/` - Item detail pages

**Files Created:**
- `market_page.html` - Items search page
- `search_results_{item_name}.html` - Search results for specific item
- `item_{item_id}_clicked.html` - Item details page

**Purpose:** Analyze HTML structure when scraping fails or filters reject items.

### 4.6 Error Handling

#### 1. Navigation Timeout

```python
try:
    WebDriverWait(self.driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
except TimeoutException:
    logging.error("Timeout navigation market", extra={"action": "ITEMDB"})
    return False
```

#### 2. Item Not Found

```python
if not item_id:
    logging.warning(f"Item ID non trouvé: {item_name}", extra={"action": "ITEMDB"})
    return None
```

#### 3. Missing Table Elements

```python
table_result = soup.find('table', id='table_result')
if not table_result:
    logging.warning(f"Table result non trouvée: {item_id}", extra={"action": "ITEMDB"})
    return None
```

#### 4. Malformed HTML

```python
try:
    soup = BeautifulSoup(html, 'html.parser')
except Exception as e:
    logging.error(f"Erreur parsing HTML: {e}", extra={"action": "ITEMDB"})
    return None
```

#### 5. Graceful Degradation

- **Filter failures:** Skip item, continue processing others
- **Network errors:** Retry with exponential backoff (future)
- **Missing merchant data:** Set fields to null, continue
- **Missing optional fields:** Use default values

### 4.7 Database Operations

**Location:** `Functions/superadmin_tools.py` lines 420-635

```python
def refresh_all_items(self, item_filter: List[str] = None):
    """
    Refresh all items in database from Eden.
    
    Args:
        item_filter: Optional list of item names for selective refresh
                     (debug mode)
    
    Process:
        1. Load existing database
        2. Copy to preserve non-refreshed items
        3. For each item:
           a. Find all realm variants
           b. Scrape details for each variant
           c. Create/update database entry
        4. Save updated database
    """
    
    # Load existing database
    data = self._load_database()
    items = data.get("items", {})
    
    # CRITICAL: Preserve existing items
    new_items = dict(items)  # Copy, don't erase!
    
    # Get unique item names
    unique_items = {}
    for key in items.keys():
        item_name = items[key].get('name')
        if item_name:
            unique_items[item_name] = True
    
    # Initialize scraper
    items_scraper = self._get_items_scraper()
    
    # Process each unique item
    for item_name in unique_items.keys():
        # Debug mode: skip if not in filter
        if item_filter is not None and item_name not in item_filter:
            logging.debug(f"⏭️ SKIP (not in filter): {item_name}")
            continue
        
        logging.info(f"Refreshing: {item_name}")
        
        try:
            # Find ALL realm variants
            variants = items_scraper.find_all_item_variants(item_name)
            
            if not variants:
                logging.warning(f"❌ No variants found for: {item_name}")
                failed_count += 1
                continue
            
            variants_found += len(variants)
            
            # Process each variant
            for variant in variants:
                item_id = variant['id']
                realm = variant['realm']
                
                logging.info(f"  Scraping variant: {realm} (ID: {item_id})")
                
                # Get full details
                item_details = items_scraper.get_item_details(
                    item_id, realm, item_name
                )
                
                if not item_details:
                    logging.warning(f"  ⚠️ Failed to get details for {realm} variant")
                    continue
                
                # Create database key
                db_key = f"{item_name.lower()}:{realm.lower()}"
                
                # Check if new or update
                is_new = db_key not in items
                
                # Prepare complete data
                item_data = {
                    "id": item_id,
                    "name": item_name,
                    "realm": realm,
                    "slot": item_details.get("slot", "Unknown"),
                    "type": item_details.get("type"),
                    "model": item_details.get("model"),
                    "dps": item_details.get("dps"),
                    "speed": item_details.get("speed"),
                    "damage_type": item_details.get("damage_type"),
                    "usable_by": item_details.get("usable_by", "ALL"),
                    "merchant_zone": item_details.get("merchant_zone"),
                    "merchant_price": item_details.get("merchant_price"),
                    "merchant_currency": item_details.get("merchant_currency"),
                    "source": "internal"
                }
                
                # Store in new items dict
                new_items[db_key] = item_data
                
                if is_new:
                    items_created += 1
                    logging.info(f"  ✨ NEW: {db_key}")
                else:
                    items_updated += 1
                    logging.info(f"  ♻️ UPDATED: {db_key}")
                
                time.sleep(1)  # Delay between variants
        
        except Exception as e:
            logging.error(f"Error processing {item_name}: {e}")
            failed_count += 1
    
    # Update metadata
    data["items"] = new_items
    data["item_count"] = len(new_items)
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save database
    with open(self.source_db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {
        "success": True,
        "stats": {
            "unique_items_processed": total_items,
            "variants_found": variants_found,
            "items_created": items_created,
            "items_updated": items_updated,
            "failed": failed_count,
            "total_db_entries": len(new_items)
        }
    }
```

---

## 5. Data Flow & Processing

### 5.1 Complete Data Flow Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE DATA FLOW                                │
└───────────────────────────────────────────────────────────────────────────┘

USER ACTION: Refresh Database
      │
      ├──> SuperAdmin Dialog
      │    ├─> Full Refresh (all items)
      │    └─> Debug Mode (select specific items)
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Load Existing Database                                         │
│ File: Data/items_database_src.json                                     │
│ Action: Load items dict, preserve existing data                        │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Initialize Scraper                                             │
│ Component: ItemsScraper                                                 │
│ Browser: Selenium WebDriver (Chrome)                                   │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: For Each Unique Item Name                                      │
│ Source: Existing database keys                                         │
│ Filter: Optional item_filter for debug mode                            │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ├──> Search ALL Realms (r=0)
      │    URL: https://eden-daoc.net/items?s={item_name}&r=0
      │    Wait: table_result element
      │
      ├──> Parse HTML Results
      │    Parser: BeautifulSoup
      │    Target: <tr id="result_row_*"> elements
      │
      ├──> Apply 4 Filters
      │    1. Exact name match (case-insensitive)
      │    2. Level ≥ 50 (dynamic column detection)
      │    3. Utility ≥ 100 (skip level column)
      │    4. Realm icon present (mandatory)
      │
      ├──> Extract Variants
      │    Data: [{id, realm, name}, ...]
      │    Example: 3 variants for multi-realm item
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: For Each Variant                                               │
│ Input: variant_id, realm, item_name                                    │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ├──> Navigate to Item Page
      │    URL: https://eden-daoc.net/items?id={variant_id}
      │
      ├──> Extract Item Details
      │    Slot, Type, Model from main table
      │    DPS, Speed, Damage Type (weapons only)
      │    Usable by classes
      │
      ├──> Extract Merchant Info
      │    Parse merchants table
      │    Zone detection (from zone name or currency)
      │    Price and currency extraction
      │    Zone → Currency mapping
      │
      ├──> Build Complete Item Data
      │    Merge: variant info + scraped details
      │    Generate: composite key "{name}:{realm}"
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Update Database                                                │
│ Key: "cloth cap:hibernia"                                              │
│ Action: Create new or update existing entry                            │
│ Preserve: All non-refreshed items remain in database                   │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Save Database                                                  │
│ Update: item_count, last_updated                                       │
│ Format: JSON with 2-space indentation                                  │
│ Encoding: UTF-8                                                        │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
RESULT: Updated database with all variants
        Statistics: created, updated, failed counts
```

### 5.2 Example: Processing "Cloth Cap"

```
INPUT: item_name = "Cloth Cap"

┌─────────────────────────────────────────────────────────────────┐
│ SEARCH PHASE                                                    │
└─────────────────────────────────────────────────────────────────┘

URL: https://eden-daoc.net/items?s=Cloth%20Cap&r=0

Raw Results (21 items):
  1. Cloth Cap (Level 51, Utility 108.5, Hibernia)      ← VALID
  2. Cloth Cap (Level 51, Utility 108.5, Midgard)       ← VALID
  3. Cloth Cap (Level 51, Utility 108.5, Albion)        ← VALID
  4. Lightning Embossed Cloth Cap (Level 51, Util 85.7) ← REJECT (name)
  5. Gossamer Cloth Cap (Level 45, Utility 80.0)        ← REJECT (level, utility)
  6. Cloth Cap (Level 10, Utility 10.0)                 ← REJECT (level, utility)
  ... (15 more items rejected)

Filtered Results (3 items):
  [{id: '163421', realm: 'Hibernia', name: 'Cloth Cap'},
   {id: '163452', realm: 'Midgard', name: 'Cloth Cap'},
   {id: '163480', realm: 'Albion', name: 'Cloth Cap'}]

┌─────────────────────────────────────────────────────────────────┐
│ DETAILS SCRAPING (×3)                                           │
└─────────────────────────────────────────────────────────────────┘

Variant 1: Hibernia (ID 163421)
  URL: https://eden-daoc.net/items?id=163421
  Extracted:
    slot: "Helm"
    type: "Cloth"
    model: "4063"
    usable_by: "ALL"
    merchant_zone: "Drake"
    merchant_price: "500"
    merchant_currency: "Scales"

Variant 2: Midgard (ID 163452)
  URL: https://eden-daoc.net/items?id=163452
  Extracted:
    slot: "Helm"
    type: "Cloth"
    model: "4070"
    usable_by: "ALL"
    merchant_zone: "Drake"
    merchant_price: "500"
    merchant_currency: "Scales"

Variant 3: Albion (ID 163480)
  URL: https://eden-daoc.net/items?id=163480
  Extracted:
    slot: "Helm"
    type: "Cloth"
    model: "4056"
    usable_by: "ALL"
    merchant_zone: "Drake"
    merchant_price: "500"
    merchant_currency: "Scales"

┌─────────────────────────────────────────────────────────────────┐
│ DATABASE UPDATE                                                 │
└─────────────────────────────────────────────────────────────────┘

Created/Updated Keys:
  1. "cloth cap:hibernia" → {...}
  2. "cloth cap:midgard" → {...}
  3. "cloth cap:albion" → {...}

Statistics:
  variants_found: 3
  items_created: 3 (or items_updated: 3)
  failed: 0
  total_db_entries: 32 (30 existing + 3 new, or 32 updated)

OUTPUT: Database file saved with 3 entries for Cloth Cap
```

---

## 6. API Reference

### 6.1 ItemsDatabaseManager (Dual-Mode Manager)

#### Overview

The `ItemsDatabaseManager` class handles both internal (read-only) and personal (user-managed) databases, providing a unified interface for database operations.

#### get_active_database_path()

```python
def get_active_database_path(self) -> Path:
    """
    Get path to currently active database based on mode.
    
    Returns:
        Path: Database file path
        - Mode 1: Data/items_database_src.json
        - Mode 2: Armory/items_database.json
    
    Example:
        >>> db_path = db_manager.get_active_database_path()
        >>> print(db_path)
        Path('Armory/items_database.json')  # If Mode 2 active
    """
```

#### search_item()

```python
def search_item(self, item_name: str, realm: str = None) -> dict:
    """
    Search for an item in the active database.
    
    Args:
        item_name (str): Item name to search (case-insensitive)
        realm (str, optional): Realm filter ("Albion", "Hibernia", "Midgard")
    
    Returns:
        dict: Item data if found, None otherwise
    
    Example:
        >>> item = db_manager.search_item("Dragon Slayer Sword", realm="Albion")
        >>> item['damage']
        '16.5 DPS'
    """
```

#### create_personal_database()

```python
def create_personal_database(self) -> tuple[bool, str]:
    """
    Create personal database by copying internal database.
    
    Process:
        1. Check if Armory folder exists, create if needed
        2. Copy Data/items_database_src.json → Armory/items_database.json
        3. Update config: use_personal_database = True
        4. Save database path and version to config
    
    Returns:
        tuple[bool, str]: (success, path_or_error_message)
        - (True, path) on success
        - (False, error_message) on failure
    
    Example:
        >>> success, result = db_manager.create_personal_database()
        >>> if success:
        ...     print(f"Database created at: {result}")
        Database created at: C:\...\Armory\items_database.json
    """
```

#### add_scraped_item()

```python
def add_scraped_item(self, item_data: dict) -> bool:
    """
    Add scraped item to personal database.
    
    Requirements:
        - Mode 2 must be active (use_personal_database = True)
        - Personal database file must exist
    
    Features:
        - Realm deduplication: Only adds if item doesn't exist for same realm
        - User tracking: Sets user_added = True in metadata
        - Automatic save: Writes to file immediately
    
    Args:
        item_data (dict): Item properties (name, realm, type, stats, etc.)
    
    Returns:
        bool: True if added successfully, False if already exists or wrong mode
    
    Example:
        >>> item_data = {
        ...     "name": "Custom Sword",
        ...     "realm": "Albion",
        ...     "type": "Weapon",
        ...     "bonus_stats": {"Strength": 10}
        ... }
        >>> success = db_manager.add_scraped_item(item_data)
        >>> print(success)
        True
    """
```

#### get_statistics()

```python
def get_statistics(self) -> dict:
    """
    Get statistics about databases.
    
    Returns:
        dict: Database statistics
        {
            "internal_count": int,     # Items in internal DB
            "personal_count": int,     # Items in personal DB (if Mode 2)
            "user_added_count": int,   # Items added by user (user_added=True)
            "mode": str                # "internal" or "personal"
        }
    
    Example:
        >>> stats = db_manager.get_statistics()
        >>> print(f"You have {stats['user_added_count']} custom items")
        You have 80 custom items
    """
```

#### reset_personal_database()

```python
def reset_personal_database(self) -> bool:
    """
    Reset personal database to fresh copy of internal database.
    
    WARNING: Deletes all user-added items!
    
    Process:
        1. Backup current personal database (optional)
        2. Copy internal database → personal database
        3. Update version tracking in config
    
    Returns:
        bool: True on success, False on failure
    
    Example:
        >>> success = db_manager.reset_personal_database()
        >>> if success:
        ...     print("Database reset to internal version")
    """
```

### 6.2 ItemsScraper Methods

#### find_all_item_variants()

```python
def find_all_item_variants(self, item_name: str) -> List[Dict]:
    """
    Find ALL realm variants of an item.
    
    Args:
        item_name (str): Name of the item to search
    
    Returns:
        List[Dict]: List of variant dictionaries
        [
            {
                'id': str,      # Eden item ID
                'realm': str,   # Albion|Hibernia|Midgard|All
                'name': str     # Item name (original case)
            },
            ...
        ]
    
    Raises:
        Exception: If search fails or timeout occurs
    
    Example:
        >>> variants = scraper.find_all_item_variants("Cloth Cap")
        >>> len(variants)
        3
        >>> variants[0]
        {'id': '163421', 'realm': 'Hibernia', 'name': 'Cloth Cap'}
    """
```

#### get_item_details()

```python
def get_item_details(self, item_id: str, realm: str = "All", 
                     item_name: str = None) -> Dict:
    """
    Scrape complete item details from Eden item page.
    
    Args:
        item_id (str): Eden item ID
        realm (str): Item realm (default: "All")
        item_name (str): Item name (optional, for error context)
    
    Returns:
        Dict: Complete item data with 13 fields
        {
            'id': str,
            'name': str,
            'realm': str,
            'slot': str,
            'type': str | None,
            'model': str | None,
            'dps': str | None,
            'speed': str | None,
            'damage_type': str | None,
            'usable_by': str,
            'merchant_zone': str | None,
            'merchant_price': str | None,
            'merchant_currency': str | None,
            'merchants': List[Dict]  # Full merchant data
        }
    
    Raises:
        Exception: If page load fails or parsing error occurs
    
    Example:
        >>> details = scraper.get_item_details("163421", "Hibernia", "Cloth Cap")
        >>> details['merchant_zone']
        'Drake'
        >>> details['merchant_currency']
        'Scales'
    """
```

### 6.2 SuperAdminTools Methods

#### refresh_all_items()

```python
def refresh_all_items(self, item_filter: List[str] = None) -> Dict:
    """
    Refresh items in database from Eden-DAOC.
    
    Args:
        item_filter (List[str], optional): List of item names to refresh.
                                           If None, refresh all items.
                                           Used for debug/selective refresh.
    
    Returns:
        Dict: Operation result with statistics
        {
            'success': bool,
            'stats': {
                'unique_items_processed': int,
                'variants_found': int,
                'items_created': int,
                'items_updated': int,
                'failed': int,
                'total_db_entries': int
            }
        }
    
    Process:
        1. Load existing database (preserve all items)
        2. Initialize ItemsScraper with Selenium
        3. For each unique item (or filtered items):
           - Find all realm variants
           - Scrape details for each variant
           - Create/update database entries
        4. Save updated database
        5. Return statistics
    
    Example:
        >>> # Full refresh
        >>> result = tools.refresh_all_items()
        >>> result['stats']['variants_found']
        45
        
        >>> # Debug mode: refresh specific items
        >>> result = tools.refresh_all_items(["Cloth Cap", "Cudgel of the Undead"])
        >>> result['stats']['unique_items_processed']
        2
    """
```

---

## 7. Configuration & Mappings

### 7.1 Armory Configuration Schema

**Configuration Section:** `armory`

```json
{
  "armory": {
    "use_personal_database": false,
    "personal_db_created": false,
    "personal_db_path": "",
    "auto_add_scraped_items": true,
    "last_internal_db_version": ""
  }
}
```

**Configuration Keys:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_personal_database` | bool | `false` | Enable Mode 2 (personal DB) |
| `personal_db_created` | bool | `false` | Flag: personal DB created at least once |
| `personal_db_path` | str | `""` | Full path to personal database file |
| `auto_add_scraped_items` | bool | `true` | Auto-add scraped items without prompt |
| `last_internal_db_version` | str | `""` | Version tracking for updates |

**Usage Examples:**

```python
# Check current mode
mode = config.get("armory.use_personal_database")
if mode:
    print("Using personal database")
else:
    print("Using internal database")

# Enable auto-add
config.set("armory.auto_add_scraped_items", True)

# Get personal database path
db_path = config.get("armory.personal_db_path")
```

### 7.2 Zone Mapping

**Purpose:** Convert full zone names to abbreviations.

**Location:** `Functions/items_scraper.py` lines 79-119

```python
ZONE_MAPPING = {
    # Summoner's Hall
    "Passage of Conflict": "SH",
    "Summoner's Hall": "SH",
    
    # Darkness Falls
    "Darkness Falls": "DF",
    
    # Trials of Atlantis
    "Sobekite Eternal": "SE",
    
    # Dragon's Lair
    "Dragon's Lair": "DL",
    "Deep Volcanus": "Volcanus",
    
    # Epic Zones (NEW)
    "Tuscan Glacier": "Epic",
    "Tuscaran Glacier": "Epic",
    "Galladoria": "Epic",
    "Caer Sidi": "Epic",
    
    # RvR Zones
    "Caledonia": "Cale",
    "Thidranki": "Thid",
    "Abermenai": "Aber",
    
    # Capital Cities
    "Camelot": "Camelot",
    "Jordheim": "Jordheim",
    "Tir na Nog": "TNN",
    
    # Oceanus (all variants mapped by realm)
    "Oceanus Notos (Hibernia)": "Oceanus Hib",
    "Oceanus Notos (Albion)": "Oceanus Alb",
    "Oceanus Notos (Midgard)": "Oceanus Mid",
    # ... (12 total Oceanus variants)
}
```

### 7.2 Zone to Currency Mapping

**Purpose:** Automatic currency assignment based on merchant zone.

**Location:** `Functions/items_scraper.py` lines 121-128

```python
ZONE_CURRENCY = {
    "DF": "Seals",              # Darkness Falls
    "SH": "Grimoires",          # Summoner's Hall
    "ToA": "Glasses",           # Trials of Atlantis
    "Drake": "Scales",          # Dragon's Lair
    "Epic": "Souls/Roots/Ices", # Epic Zones (Caer Sidi, Galladoria, Glacier)
    "Epik": "Souls/Roots/Ices"  # Legacy spelling
}
```

**Usage:**
```python
# In get_item_details()
if item_data['merchants']:
    first_merchant = item_data['merchants'][0]
    zone = first_merchant.get('zone')
    item_data['merchant_zone'] = zone
    item_data['merchant_currency'] = self.ZONE_CURRENCY.get(zone)
```

### 7.3 Currency Detection from Price

**Purpose:** Override zone based on detected currency in price string.

**Location:** `Functions/items_scraper.py` lines 1233-1250

```python
# Override zone based on currency
if merchant_data['price_parsed']:
    currency = merchant_data['price_parsed']['currency']
    
    if currency == 'Atlantean Glass':
        merchant_data['zone'] = 'ToA'
    elif currency == 'Seals':
        merchant_data['zone'] = 'DF'
    elif currency in ['Roots', 'Souls', 'Ices']:
        merchant_data['zone'] = 'Epic'
    elif currency == 'Dragon Scales':
        merchant_data['price_parsed']['currency'] = 'Scales'
        merchant_data['zone'] = 'Drake'
    elif currency == 'Scales':
        merchant_data['zone'] = 'Drake'
    elif currency == 'Grimoires':
        merchant_data['zone'] = 'SH'
```

### 7.4 Realm Mapping

**Purpose:** Map realm names to Eden search parameters.

**Location:** `Functions/items_scraper.py` lines 30-35

```python
REALM_MAP = {
    "All": 0,       # Search all realms
    "Albion": 1,    # Albion only
    "Midgard": 2,   # Midgard only
    "Hibernia": 3   # Hibernia only
}
```

**Note:** For `find_all_item_variants()`, we **ALWAYS** use `r=0` (All realms) to discover all variants, regardless of this mapping.

---

## 8. Best Practices

### 8.1 Database Mode Selection

#### ✅ Use Mode 1 (Internal Database) When:

- You're a casual user who doesn't need data persistence
- You only need temporary item lookups during gameplay
- You're testing or validating without modifying data
- You have a portable installation without write access
- You don't want to maintain a personal database

#### ✅ Use Mode 2 (Personal Database) When:

- You want to build a personal item collection
- You need to save scraped items permanently
- You want to add custom items or modifications
- You're a guild leader maintaining shared item lists
- You're a theorycrafter with custom item data
- You want long-term data collection and analysis

### 8.2 Database Management

#### ✅ DO: Preserve Existing Data

```python
# CORRECT: Copy existing items before updating
new_items = dict(items)

# Then update/add new items
new_items[db_key] = item_data
```

#### ❌ DON'T: Erase Database

```python
# WRONG: This erases all non-refreshed items!
new_items = {}  # ← Destroys existing data

# Add new items
new_items[db_key] = item_data
```

### 8.2 Scraping Best Practices

#### Rate Limiting

```python
# Add delay between variants to avoid overloading server
time.sleep(1)  # 1 second between each item detail scrape
```

#### Error Handling

```python
try:
    variants = scraper.find_all_item_variants(item_name)
except Exception as e:
    logging.error(f"Error processing {item_name}: {e}")
    failed_count += 1
    continue  # Don't stop entire refresh for one item
```

#### Timeout Configuration

```python
# Wait for search results with timeout
WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.ID, "table_result"))
)
```

### 8.3 Debug Mode Usage

**When to use:**
- Testing filter changes
- Verifying specific item scraping
- Investigating scraping issues

**How to use:**
```python
# UI: SuperAdmin → Refresh Items → Select specific items
# Programmatically:
result = tools.refresh_all_items(item_filter=["Cloth Cap", "Cudgel of the Undead"])
```

**Benefits:**
- Faster testing (scrape only selected items)
- Easier log analysis
- No risk to full database

### 8.4 Filter Tuning

**Current thresholds:**
- Level: ≥ 50 (endgame items)
- Utility: ≥ 100 (quality threshold)

**To adjust:**
```python
# In find_all_item_variants()

# Level threshold
if level < 50:  # Change 50 to desired minimum
    continue

# Utility threshold
if utility < 100:  # Change 100 to desired minimum
    continue
```

**Considerations:**
- Lower thresholds = more items but more false positives
- Higher thresholds = fewer items but higher quality
- Current settings tested for endgame item collection

### 8.5 HTML Structure Changes

**If Eden updates their HTML:**

1. **Check column order** in search results:
```python
# Current order (verify if scraping fails):
# Column 0: Item icon
# Column 1: Item name
# Column 2: Item type
# Column 3: Slot
# Column 4: Realm icon ← CRITICAL
# Column 5: Class icon
# Column 6: Classes text
# Column 7: Level ← CRITICAL
# Column 8: Utility ← CRITICAL
```

2. **Update column indices** if changed:
```python
# Adjust these in find_all_item_variants()
found_name = cells_text[1]  # Name column
# Level detection: dynamic (searches for integer 1-51)
# Utility detection: dynamic (searches for float ≥50, skips level column)
```

3. **Verify realm icon pattern**:
```python
# Current pattern
realm_img = row.find('img', src=re.compile(
    r'(albion_logo|hibernia_logo|midgard_logo|all_logo)\.png'
))

# If pattern changes, update regex
```

4. **Test with known items** after HTML changes:
```python
test_items = ["Cloth Cap", "Cudgel of the Undead", "Soulbinder's Belt"]
result = tools.refresh_all_items(item_filter=test_items)
# Verify all expected variants found
```

---

## Appendix A: Database Schema Evolution

### Version 1.0 → 2.0 Migration

**Implementation Date:** 2025-11-19  
**Status:** ✅ Complete and Ready for Use  
**Migration Script:** `Scripts/migrate_db_to_v2.py`

#### Changes Overview

**1. Composite Keys (Multi-Realm Support)**

**BEFORE (v1.0):**
```json
{
  "cudgel of the undead": {
    "id": "139625",
    "realm": "Albion"
  }
}
```

**AFTER (v2.0):**
```json
{
  "cudgel of the undead:albion": {
    "id": "139625",
    "realm": "Albion"
  },
  "cudgel of the undead:hibernia": {
    "id": "164123",
    "realm": "Hibernia"
  },
  "cudgel of the undead:midgard": {
    "id": "164074",
    "realm": "Midgard"
  }
}
```

**Benefits:**
- ✅ No more ID collisions for items existing in multiple realms
- ✅ Supports all 4 cases: same name/different IDs, common items, realm-specific, multi-versions
- ✅ Fallback to `:all` realm if specific realm not found

**2. Fields Added in v2.0:**
- ✅ `realm` field (All/Albion/Hibernia/Midgard)
- ✅ `model` - Visual appearance ID (e.g., "3045")
- ✅ `dps` - Damage Per Second (weapons only)
- ✅ `speed` - Weapon Speed (weapons only)
- ✅ `damage_type` - Crush/Slash/Thrust (weapons only)
- ✅ `usable_by` - Classes that can use the item
- ✅ `merchant_currency` - Currency name for merchant purchases

**3. Fields Removed in v2.0:**
- ❌ `level` - Removed (all items are level 50+)
- ❌ `quality` - Removed (all items are quality 100+)
- ❌ `stats` - Removed (only essential data kept)
- ❌ `resistances` - Removed (only essential data kept)
- ❌ `bonuses` - Removed (only essential data kept)

**4. Key Format Change:**
```python
# v1.0 format
key = "cudgel of the undead"

# v2.0 format (composite)
key = "cudgel of the undead:albion"
```

#### Modified Files

**Core Scraper (3 files):**

1. **`Functions/items_scraper.py`**
   - Modified `_get_cache_key()` to generate composite keys (`name:realm`)
   - Modified `_get_item_from_databases()` with fallback to `:all` realm
   - Modified `item_data` structure (added model, dps, speed, damage_type)
   - Added parsing for Model, DPS, Speed, Damage Type fields
   - Removed parsing for Level, Quality, Stats, Resistances, Bonuses

2. **`Functions/items_parser.py`**
   - Modified `search_item_for_database()` to return v2.0 structure
   - Added logging for damage info and model
   - Removed stats/resistances/bonuses from output

3. **`Functions/superadmin_tools.py`**
   - Modified `build_database_from_files()` to generate composite keys
   - Updated database structure to v2.0 format
   - Added notes field with migration info

**Migration Tools (1 file):**

4. **`Scripts/migrate_db_to_v2.py`** (NEW)
   - Automated migration from v1.0 to v2.0
   - Creates timestamped backup before migration
   - Converts all keys to composite format
   - Adds null values for new fields (model, dps, speed, damage_type)
   - Removes old fields (level, quality, stats, resistances, bonuses)

#### Database Statistics

**Before Migration (v1.0):**
- Size: ~70 KB (with stats/resistances/bonuses)
- Key Format: Simple string
- Multi-Realm Support: ❌ No (ID collisions)

**After Migration (v2.0):**
- Size: ~14 KB (essential data only)
- Key Format: Composite `name:realm`
- Multi-Realm Support: ✅ Yes
- Items: 30 entries
- Backup: `Data/Backups/items_database_v1_backup_20251119_072911.json`

#### Search Behavior with v2.0

**Priority Order:**
```python
1. Check database with realm-specific key: "cudgel of the undead:albion"
2. Fallback to "all" realm: "cudgel of the undead:all"
3. Check web cache (same logic)
4. Search online on Eden
```

**Examples:**

**Search for realm-specific item:**
```python
find_item_id("Cudgel of the Undead", realm="Albion")
# → Checks "cudgel of the undead:albion" first
# → Returns ID "139625"
```

**Search for common item:**
```python
find_item_id("Dragonseye Strand", realm="Albion")
# → Checks "dragonseye strand:albion" (not found)
# → Fallback to "dragonseye strand:all" (found!)
# → Returns ID "149092"
```

#### Migration Statistics

```
Version:        v1.0 → v2.0
Total items:    30
Migrated:       30
Skipped:        0
Fields removed: 5 (level, quality, stats, resistances, bonuses)
Fields added:   7 (realm, model, dps, speed, damage_type, usable_by, merchant_currency)
Size change:    ~70 KB → ~14 KB (80% reduction)
```

#### Rollback Procedure

If you need to revert to v1.0:

```powershell
# 1. Restore from backup
Copy-Item "Data\Backups\items_database_v1_backup_20251119_072911.json" "Data\items_database_src.json"

# 2. Revert code changes (git)
git restore Functions/items_scraper.py Functions/items_parser.py Functions/superadmin_tools.py
```

#### Migration Verification Checklist

- [x] Migration script works (v1.0 → v2.0)
- [x] Composite keys generated correctly
- [x] Fallback to `:all` realm works
- [x] New fields (model, dps, speed, damage_type) in structure
- [x] Old fields (level, quality, stats, resistances, bonuses) removed
- [x] Backup created before migration
- [x] Database version updated to 2.0
- [x] Database size reduced significantly
- [ ] Test SuperAdmin build with new format
- [ ] Test search for multi-realm items
- [ ] Test search for "All" realm items

---

## Appendix B: Common Issues & Solutions

### Issue 1: "No variants found"

**Symptoms:**
- Search returns items but all filtered out
- Log shows: `⏭️ SKIP (level X < 50)` or `⏭️ SKIP (utility X < 100)`

**Diagnosis:**
```python
# Enable debug logging in find_all_item_variants()
self.logger.setLevel(logging.DEBUG)

# Check logs for filter rejections
# Example: "⏭️ SKIP (utility 85.7 < 100)"
```

**Solutions:**
1. Verify item actually exists on Eden
2. Check if item meets filter criteria (Level ≥50, Utility ≥100)
3. Temporarily lower filter thresholds for testing
4. Verify HTML structure hasn't changed

### Issue 2: "Wrong realm assigned"

**Symptoms:**
- Item shows "All" but should be realm-specific
- Wrong realm in database

**Diagnosis:**
```python
# Check realm icon detection logs
# Should see: "✓ Variante VALIDE: Hibernia → ID 163421"
# If seeing: "⚠️ Pas d'icône realm pour ID"
```

**Solutions:**
1. Verify realm icon regex pattern matches Eden's HTML:
```python
# Current pattern
r'(albion_logo|hibernia_logo|midgard_logo|all_logo)\.png'

# Check actual HTML for icon paths
```
2. Update regex if Eden changed icon filenames
3. Ensure `ZONE_MAPPING` is up to date

### Issue 3: "Merchant data missing"

**Symptoms:**
- `merchant_zone`: null
- `merchant_price`: null
- `merchant_currency`: null

**Diagnosis:**
```python
# Check if merchants table exists on item page
merchants_table = soup.find('table', id='table_merchants')
if not merchants_table:
    print("Merchants table not found - item not sold by merchant")
```

**Solutions:**
1. Verify item is actually sold by merchant (not all items are)
2. Check if HTML structure changed:
```python
# Look for merchant divs
merchant_divs = merchants_table.find_all('div', class_='item_mob')
```
3. Update merchant parsing code if structure changed
4. Verify `ZONE_CURRENCY` mapping is complete

### Issue 4: "Database erased on refresh"

**Symptoms:**
- Only refreshed items remain in database
- Other items disappear

**Root Cause:**
```python
# WRONG CODE (destroys existing data):
new_items = {}  # ← Creates empty dict

# CORRECT CODE:
new_items = dict(items)  # ← Copies existing data
```

**Solution:**
Ensure `refresh_all_items()` uses `dict(items)` to preserve existing entries.

---

## Appendix C: Testing Checklist

### Pre-Deployment Tests

- [ ] **Filter Accuracy**
  - [ ] Exact name matching (no false positives)
  - [ ] Level filter (≥50)
  - [ ] Utility filter (≥100)
  - [ ] Realm icon detection

- [ ] **Multi-Realm Handling**
  - [ ] Test "Cudgel of the Undead" (3 realms)
  - [ ] Test "Soulbinder's Belt" (All realm)
  - [ ] Test "Cloth Cap" (3 realms)
  - [ ] Verify correct number of variants found

- [ ] **Database Integrity**
  - [ ] Existing items preserved after refresh
  - [ ] Composite keys correct format
  - [ ] All 13 fields populated
  - [ ] No duplicate entries

- [ ] **Merchant Data**
  - [ ] Zone correctly identified
  - [ ] Price extracted
  - [ ] Currency mapped from zone
  - [ ] Epic zones (Caer Sidi, Galladoria, Glacier) → "Epic"

- [ ] **Error Handling**
  - [ ] Graceful failure on network error
  - [ ] Continue on single item failure
  - [ ] Proper logging of errors
  - [ ] Statistics accurate

- [ ] **Dual-Mode System**
  - [ ] Mode 1: Items not saved after scraping
  - [ ] Mode 2: Items saved to personal database
  - [ ] Auto-add works correctly
  - [ ] Database statistics accurate
  - [ ] Reset personal database works

### Debug Mode Tests

```python
# Test 1: Single item
result = tools.refresh_all_items(["Cloth Cap"])
assert result['stats']['variants_found'] == 3

# Test 2: Multi-realm item
result = tools.refresh_all_items(["Cudgel of the Undead"])
assert result['stats']['variants_found'] == 3

# Test 3: All-realm item
result = tools.refresh_all_items(["Soulbinder's Belt"])
assert result['stats']['variants_found'] == 1
assert result['items']['soulbinder\'s belt:all']['realm'] == 'All'
```

---

## Appendix D: Performance Metrics

### Database Size & Performance

**Internal Database (Mode 1):**
- Size: ~14 KB (30 items, essential data only)
- Size with full dataset: ~1-5 MB (1000-5000 items)
- Load time: <100ms
- Search performance: O(n) linear search

**Personal Database (Mode 2):**
- Initial size: Same as internal (~14 KB)
- Grows with user additions
- Search performance: O(n) linear search (acceptable for <10k items)
- Save time: <200ms per item added

**Optimization Considerations:**
- Use realm filtering to reduce search space
- Cache frequently accessed items
- Consider indexing for large databases (>10k items)
- For databases >10k items, consider SQLite migration

### Typical Scraping Times

| Operation | Time | Notes |
|-----------|------|-------|
| Search (single item) | 5-8s | Includes page load + wait |
| Parse results | <1s | BeautifulSoup parsing |
| Filter application | <1s | All 4 filters |
| Item details scrape | 3-5s | Per variant |
| Database save (Mode 1) | <1s | JSON write (internal) |
| Database save (Mode 2) | <200ms | JSON write (personal) |

### Full Refresh Estimates

```
Items in DB: 30 unique items
Average variants per item: 1.5
Total variants: ~45

Time breakdown:
  Search phase: 30 items × 7s = 210s (3.5 min)
  Details phase: 45 variants × 4s = 180s (3 min)
  Delays: 45 variants × 1s = 45s
  Total: ~435s (7.25 minutes)

Actual time may vary based on:
  - Network latency
  - Eden server response time
  - Number of search results per item
```

### Optimization Tips

1. **Parallel Scraping** (future enhancement):
```python
# NOT IMPLEMENTED - Example only
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(scraper.get_item_details, v['id'], v['realm'])
        for v in variants
    ]
```

2. **Caching** (already implemented):
- User cache stores previously scraped items
- Reduces redundant scraping in character creation flow

3. **Selective Refresh**:
- Use debug mode for testing
- Only refresh items that actually changed

---

## Appendix E: Dual-Mode System Details

### UI Integration - Settings Dialog

#### Folder Configuration (Always Visible)
- **Armory folder path**: Browse, Move, Open buttons
- Changes immediately saved to config

#### Database Mode Section
- **Checkbox**: "Activate personal database"
  - Unchecked = Mode 1 (internal)
  - Checked = Mode 2 (personal)

#### Statistics Group (Visible in Mode 2)
- Items in internal database
- Items in personal database
- Items added by user

#### Actions Group (Visible in Mode 2)
- **Reset Database** button: Restore to internal copy
- **WARNING**: Deletes all user-added items

#### Import Section (Visible in Mode 2)
- **Import Items** button: Open import dialog
- Help text explaining import functionality

### Activation Flow

**First-time activation:**
1. User checks "Activate personal database"
2. System detects no personal DB exists
3. Popup: "Create personal database? (X items will be copied)"
4. User clicks Yes → database created at `Armory/items_database.json`
5. UI shows statistics, actions, import sections

**Subsequent activations:**
1. User checks "Activate personal database"
2. System detects existing personal DB
3. Mode switches immediately
4. UI shows statistics, actions, import sections

**Deactivation:**
1. User unchecks checkbox
2. System switches to Mode 1 (internal DB)
3. Statistics, actions, import sections hidden
4. Personal database file remains intact (can reactivate later)

### Auto-Add Integration

When scraping completes and Mode 2 is active:

**If `auto_add_scraped_items = True`:**
- Items automatically added to personal database
- No user interaction required
- Success message shows count

**If `auto_add_scraped_items = False`:**
- Popup: "Add X items to your database?"
- Checkbox: "Always add automatically"
- User can:
  - Yes → Add items + optionally enable auto-add
  - No → Items discarded (not saved)

### Migration & Application Updates

**When a new version includes an updated internal database:**

1. **Mode 1 users**: Automatically use new internal DB
2. **Mode 2 users**: Keep personal DB unchanged
   - Option to reset and copy new internal DB
   - Version tracking in `last_internal_db_version`

**Version Detection:**
```python
current_version = config.get("armory.last_internal_db_version")
internal_version = db_manager.get_internal_db_version()

if current_version != internal_version:
    # Notify user of update available
    # Offer to reset personal DB to get new items
```

### Error Handling

**Database Creation Failures:**
- **Folder permissions**: Check write access to Armory folder
- **Disk space**: Verify sufficient space for copy
- **File locks**: Ensure no other process using database

**Import/Add Failures:**
- **Invalid JSON**: Validate item structure before adding
- **Duplicate detection**: Check realm + name combination
- **Schema validation**: Ensure required fields present

**Recovery:**
- Personal database can always be reset to internal copy
- Config corruption: Falls back to Mode 1 (internal)
- File corruption: Recreate personal database

### Troubleshooting

**Issue: Checkbox won't stay checked**
- **Cause**: Personal database file doesn't exist
- **Solution**: Delete and recreate personal database

**Issue: Items not saving**
- **Cause**: Mode 1 active (read-only)
- **Solution**: Activate Mode 2 (personal database)

**Issue: Statistics not updating**
- **Cause**: Config not reloaded after changes
- **Solution**: Close and reopen settings dialog

**Issue: Database corrupted**
- **Cause**: Manual editing introduced JSON errors
- **Solution**: Reset personal database to internal copy

### Security & Privacy

**Data Storage:**
- All databases stored locally (no cloud sync)
- Plain JSON format (no encryption)
- User responsible for backups

**Portable Mode:**
- Config and databases in application folder
- No registry/AppData dependencies
- Copy entire folder to backup/transfer

---

## Appendix F: Future Enhancements

### Planned Features
- [ ] Database merge tool (combine multiple personal DBs)
- [ ] Import/export personal DB as ZIP
- [ ] Item comparison tool (internal vs. personal)
- [ ] Database optimization (remove duplicates)
- [ ] Advanced search (filters, sorting)
- [ ] Database statistics dashboard

### Under Consideration
- [ ] Cloud sync (optional, encrypted)
- [ ] Collaborative databases (guild sharing)
- [ ] Automatic backups before reset
- [ ] Database compression (SQLite migration)

---

---

## Appendix G: Mass Import System & Threading Architecture (v2.1)

### Overview

The mass import system was completely rewritten in November 2025 to fix critical crashes that occurred during retry operations. The root cause was improper use of `QApplication.processEvents()` in signal callbacks from worker threads.

### Critical Bug Fix: QApplication.processEvents() Removal

#### Problem Identified

**Symptoms:**
- Application crashed immediately after "Retry completed successfully" message
- Crash occurred ONLY when using retry functionality
- Main import worked fine, but retry always failed
- No visible error in worker thread logs

**Root Cause:**
`QApplication.processEvents()` was being called in multiple locations within signal callbacks that were triggered by cross-thread signals from `ImportWorker` (QThread). This caused:

1. **Reentrancy Issues**: Event loop manually pumped while already processing events
2. **Object Deletion Race Conditions**: Objects deleted while still in use
3. **Signal Handler Corruption**: Callbacks re-entered before completing
4. **Qt Event Queue Corruption**: Manual event processing conflicted with automatic processing

**Locations of Dangerous processEvents() Calls:**

```python
# REMOVED - Line 428 in finish_import()
def finish_import(self, success=True):
    self.timer.stop()
    self.ui_refresh_timer.stop()
    self.close_button.setEnabled(True)
    
    QApplication.processEvents()  # ← CRASH TRIGGER #1
    # ... rest of method

# REMOVED - Line 493 in update_stats()
def update_stats(self, **kwargs):
    # ... update UI elements
    QApplication.processEvents()  # ← CRASH TRIGGER #2

# REMOVED - Line 570 in _force_ui_refresh()
def _force_ui_refresh(self):
    QApplication.processEvents()  # ← CRASH TRIGGER #3

# REMOVED - Line 705 in show_review_filtered_btn()
def show_review_filtered_btn(self, filtered_items):
    # ... update button
    QApplication.processEvents()  # ← CRASH TRIGGER #4
```

#### Solution Implemented

**Complete Removal Strategy:**

1. **Removed ALL processEvents() calls** from callback methods
2. **Deleted ui_refresh_timer** mechanism entirely (called processEvents every 50ms)
3. **Deleted _force_ui_refresh()** function
4. **Added explanatory comments** at removal sites

**Why This Works:**

Qt's automatic event loop handles UI updates safely:
- Signals with `Qt.QueuedConnection` are queued and processed safely
- UI updates from main thread happen automatically
- No manual event pumping needed
- Thread-safe by design

**Modified Code:**

```python
# AFTER FIX - finish_import()
def finish_import(self, success=True):
    """Finish import"""
    # NO processEvents() - causes crashes when called from signal callbacks
    self.timer.stop()
    self.close_button.setEnabled(True)
    
    elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
    # ... rest of method (UI updates happen automatically)

# AFTER FIX - update_stats()
def update_stats(self, **kwargs):
    # ... update UI elements
    # NO processEvents() - UI updates automatically via Qt's event loop

# DELETED - _force_ui_refresh() removed entirely

# DELETED - ui_refresh_timer removed entirely
# Lines 384-385, 407, 424, 562-568, 964-965 all removed
```

### Threading Architecture Improvements

#### Worker Thread Signal Connections

**Before Fix (UNSAFE):**
```python
# Direct connections or missing QueuedConnection
self.retry_worker.progress_updated.connect(self.update_stats)
self.retry_worker.log_message.connect(self.log_message)
self.retry_worker.import_finished.connect(on_finished)
```

**After Fix (SAFE):**
```python
# Explicit QueuedConnection for cross-thread safety
from PySide6.QtCore import Qt

self.retry_worker.progress_updated.connect(self.update_stats_slot, Qt.QueuedConnection)
self.retry_worker.log_message.connect(self.log_message_slot, Qt.QueuedConnection)
self.retry_worker.import_finished.connect(on_finished, Qt.QueuedConnection)
```

#### Dedicated Slot Methods

**Added for thread safety:**

```python
def update_stats_slot(self, stats):
    """Slot for update_stats signal from worker thread"""
    self.update_stats(**stats)

def log_message_slot(self, msg, level):
    """Slot for log_message signal from worker thread"""
    self.log_message(msg, level)
```

**Benefits:**
- Clear separation between worker signals and UI updates
- Explicit slot methods are easier to debug
- QueuedConnection works more reliably with named methods
- Better code organization and readability

#### Worker Cleanup Strategy

**Before Fix (UNSAFE):**
```python
def on_finished(success, message, stats):
    self.finish_import(success)
    # Direct deletion - could cause issues
    del self.retry_worker
    self.retry_worker = None
```

**After Fix (SAFE):**
```python
def on_finished(success, message, stats):
    try:
        self.log_message("Retry completed successfully", "info")
        self.finish_import(success)
        
        # Clean up temp files
        for tf in temp_files:
            try:
                Path(tf).unlink()
            except:
                pass
        
        # Schedule worker for deletion instead of immediate cleanup
        if self.retry_worker is not None:
            # Disconnect signals first
            try:
                self.retry_worker.progress_updated.disconnect()
                self.retry_worker.log_message.disconnect()
                self.retry_worker.import_finished.disconnect()
            except:
                pass
            
            # Let Qt handle the deletion properly
            self.retry_worker.deleteLater()
            self.retry_worker = None
            
    except Exception as e:
        self.log_message(f"Error in retry finish: {e}", "error")
        import traceback
        self.log_message(f"Traceback: {traceback.format_exc()}", "error")
```

**Key Improvements:**
1. **Signal Disconnection**: Prevents callbacks on deleted objects
2. **deleteLater()**: Qt-managed delayed deletion
3. **Exception Handling**: Catches and logs any cleanup errors
4. **Null Check**: Verifies worker exists before cleanup

#### Window Close Protection

**Added closeEvent override:**

```python
def closeEvent(self, event):
    """Handle window close event safely"""
    # Wait for worker to finish if running
    if hasattr(self, 'retry_worker') and self.retry_worker is not None:
        if self.retry_worker.isRunning():
            self.retry_worker.wait(5000)  # Wait up to 5 seconds
    
    # Stop timers
    if hasattr(self, 'timer'):
        self.timer.stop()
    
    logger.info("MassImportMonitor closing normally")
    event.accept()
```

**Protection Against:**
- Closing window while worker thread is running
- Timer still firing after window closed
- Orphaned worker threads

### Performance Impact

**Before Fix:**
- UI refresh timer: Every 50ms (20 calls/second)
- processEvents() calls: 4+ per import operation
- Thread safety: Compromised
- Stability: Crashes on retry

**After Fix:**
- UI refresh timer: Removed
- processEvents() calls: 0 (none)
- Thread safety: Guaranteed by Qt
- Stability: No crashes
- Performance: **Improved** (no manual event pumping overhead)

### Testing & Validation

**Test Cases Verified:**

1. ✅ **Normal Import**: Works without crashes
2. ✅ **Retry Single Item**: No crash after completion
3. ✅ **Retry Multiple Items**: All items processed, no crash
4. ✅ **Window Close During Import**: Graceful shutdown
5. ✅ **Rapid UI Updates**: Smooth without processEvents()
6. ✅ **Long-Running Imports**: No UI freeze, no crashes

**Stress Tests:**
- 100+ items import: Stable
- Rapid retry operations: Stable
- Window resize during import: Responsive
- Multiple failed items retry: Stable

### Lessons Learned

**Never use QApplication.processEvents() when:**
1. Inside signal callbacks from worker threads
2. In methods called by cross-thread signals
3. As a "fix" for UI freezing (symptom of poor design)
4. In event loops that Qt manages automatically

**Always use instead:**
1. `Qt.QueuedConnection` for cross-thread signals
2. `deleteLater()` for Qt object cleanup
3. Dedicated slot methods for signal handlers
4. Proper thread synchronization (wait(), mutexes)
5. Qt's automatic event loop processing

**Thread Safety Checklist:**
- [ ] Worker uses QThread, not QRunnable (if signals needed)
- [ ] All cross-thread signals use Qt.QueuedConnection
- [ ] No processEvents() in callbacks
- [ ] Worker cleanup uses deleteLater()
- [ ] closeEvent waits for worker completion
- [ ] Exception handling in all callbacks

---

## 15. Database Editor Interface

### 15.1 Overview

The Database Editor provides a graphical interface for managing the items database with batch operations, search capabilities, and visual progress tracking.

**File:** `UI/database_editor_dialog.py`

**Key Features:**
- ✅ View and search all database items
- ✅ Batch refresh items by ID
- ✅ Full scan with Eden scraping
- ✅ Beautiful step-by-step progress dialogs
- ✅ Dark theme support
- ✅ Real-time status updates
- ✅ Item categorization (Quest/Event rewards)

### 15.2 ProgressStepsDialog Integration

**Purpose:** Replace old QProgressDialog with beautiful step-by-step visualization.

**File:** `UI/progress_dialog_base.py`

**Features:**
- Visual step indicators (⏳ → ✅)
- Progress bar with percentage
- Status messages with colored text
- Cancellation support
- Dark theme compatibility

**Step Configurations:**

```python
# Batch Refresh by ID
DB_EDITOR_BATCH_REFRESH = [
    {"title": "Connect to Eden", "status": "Connecting to Eden Herald..."},
    {"title": "Refresh Items", "status": "Refreshing items from database..."},
    {"title": "Save Database", "status": "Saving database..."},
    {"title": "Results", "status": "Processing results..."}
]

# Full Scan (All Items)
DB_EDITOR_BATCH_SCAN = [
    {"title": "Connect to Eden", "status": "Connecting to Eden Herald..."},
    {"title": "Search Variants", "status": "Searching item variants..."},
    {"title": "Process Variants", "status": "Processing variants..."},
    {"title": "Save Database", "status": "Saving database..."},
    {"title": "Results", "status": "Processing results..."}
]
```

**API Methods:**

```python
progress = ProgressStepsDialog(steps_config, parent, title, width, height)

# Step management
progress.start_step(index)                    # Start step (⏳)
progress.complete_step(index)                 # Complete step (✅)
progress.skip_step(index, reason)             # Skip step (⏭️)
progress.error_step(index, message)           # Error step (❌)

# Progress updates
progress.update_progress(percentage)          # Update progress bar (0-100)
progress.set_status_message(message, color)   # Update status text

# User interaction
cancelled = progress.was_canceled()           # Check if user cancelled
```

### 15.3 Batch Operations

#### Batch Refresh Items by ID

**Function:** `_batch_refresh_items_by_id()`

**Purpose:** Refresh selected items from Eden database.

**Workflow:**
```
1. User selects items in table
2. Clicks "Refresh Selected Items"
3. Progress dialog shows:
   ⏳ Connect to Eden
   ⏳ Refresh Items (1/5, 2/5, ...)
   ⏳ Save Database
   ⏳ Results
4. Table refreshes with updated data
5. Results dialog shows statistics
```

**Implementation:**
```python
def _batch_refresh_items_by_id(self):
    # Initialize progress dialog
    progress = ProgressStepsDialog(DB_EDITOR_BATCH_REFRESH, self)
    progress.show()
    
    # Force UI rendering (fix white window delay)
    for _ in range(3):
        QApplication.processEvents()
    
    # Step 0: Connect to Eden
    progress.start_step(0)
    progress.set_status_message("🔌 Connecting to Eden Herald...")
    
    scraper, error = _connect_to_eden_herald()
    if not scraper:
        progress.error_step(0, error)
        return
    
    progress.complete_step(0)
    
    # Step 1: Refresh items
    progress.start_step(1)
    for idx, item_id in enumerate(selected_ids):
        progress.update_progress(int((idx / total) * 100))
        progress.set_status_message(f"Refreshing item {idx+1}/{total}...")
        
        # Scrape item details
        details = scraper.get_item_details(item_id)
        # Update database
        save_item_to_db(details)
    
    progress.complete_step(1)
    
    # Deferred refresh to prevent UI blocking
    QTimer.singleShot(100, self._refresh_display_after_scan)
    QTimer.singleShot(500, progress.close)
    QTimer.singleShot(600, lambda: self._show_results(stats))
```

#### Full Scan Items

**Function:** `_batch_full_scan_items()`

**Purpose:** Search all realm variants and update database.

**Key Difference:** Uses `find_all_item_variants()` to discover multi-realm items.

### 15.4 Bug Fixes and Improvements

#### Bug Fix: False "Unsaved Changes" Warning

**Problem:** Modified flag stayed True after successful save.

**Root Cause:** `self.modified = True` called AFTER `_save_database()` which already reset it to False.

**Solution:** Removed all 13 instances of `self.modified = True` following save operations.

**Files Modified:**
- `UI/database_editor_dialog.py` (lines 1234, 1456, 1678, etc.)

**Impact:** Warning now only appears when there are actual unsaved changes.

#### Bug Fix: Table Not Refreshing

**Problem:** Item list didn't update after batch operations.

**Root Cause:** Refresh call was missing in finally block.

**Solution:** Added deferred refresh with QTimer.

```python
# Defer refresh to prevent UI blocking
QTimer.singleShot(100, self._refresh_display_after_scan)
```

#### Bug Fix: White Window Delay

**Problem:** Progress window appeared blank for several seconds before showing content.

**Root Cause:** Single `processEvents()` insufficient during Eden connection.

**Solution:** Multiple processEvents + immediate status message.

```python
progress.show()

# Force multiple processEvents to ensure UI is fully rendered
for _ in range(3):
    QApplication.processEvents()

# Immediate status message
progress.set_status_message("🔌 Connecting to Eden Herald...")
QApplication.processEvents()
```

#### Bug Fix: Poor Text Visibility on Dark Themes

**Problem:** Status text barely visible on dark purple themes (black text on dark background).

**Root Cause:** Default text color was #000000 (black).

**Solution:** Changed to white (#FFFFFF) with bold 13pt font.

```python
def set_status_message(self, message: str, color: Optional[str] = None):
    self._set_status_message_ui(message, color if color else "#FFFFFF")

def _set_status_message_ui(self, message: str, color: str):
    self.status_label.setStyleSheet(
        f"padding: 10px; "
        f"border: 1px solid #ccc; "
        f"border-radius: 5px; "
        f"background-color: transparent; "
        f"color: {color}; "
        f"font-size: 13pt; "
        f"font-weight: bold;"
    )
```

**Impact:** Text readable on all themes (light/dark).

### 15.5 Currency Support Enhancement

**Date:** November 24, 2025

**Problem:** Items with "Tuscaran Glacier Ices" price showed "No Price" in database.

**Investigation:** Debug script revealed `parse_price()` returned `None` for "Ices" and "Souls" currencies.

**Solution:** Added support in `parse_price()` for Epic dungeon currencies.

**Files Modified:**
- `Functions/items_scraper.py` - Added Ices and Souls parsing

**Example:**
```python
# Before fix
parse_price("600 Tuscaran Glacier Ices")  # → None ❌

# After fix
parse_price("600 Tuscaran Glacier Ices")  # → {'currency': 'Ices', 'amount': 600, ...} ✅
```

**Impact:** All Epic dungeon items now properly store merchant prices.

### 15.6 Translation Support

All Database Editor UI elements are fully translated:

**Languages:** FR (French), EN (English), DE (German)

**Keys Added to Language/*.json:**
```json
{
  "db_editor_connect": "Connect to Eden",
  "db_editor_refresh_items": "Refresh Items",
  "db_editor_save": "Save Database",
  "db_editor_search_variants": "Search Variants",
  "db_editor_process_variants": "Process Variants",
  "db_editor_batch_refresh": "Batch Refresh",
  "db_editor_batch_search": "Search All Variants",
  "db_editor_batch_process": "Process All Variants",
  "db_editor_results": "Results"
}
```

---

---

## 16. Items Database Migration System

### 16.1 Overview

The Items Database Migration System provides an automated, safe, and intelligent way to update personal items databases when the embedded (internal) database structure or content changes.

**File:** `Functions/items_database_migration.py`

**Key Features:**
- ✅ Automatic version detection (v1 vs v2 structures)
- ✅ Safe migration with automatic backups
- ✅ Intelligent data merging (preserves user customizations)
- ✅ Rollback capability on failure
- ✅ Silent auto-migration on application startup
- ✅ Comprehensive validation and logging

**Migration Scenarios:**
1. **v1 → v2**: Flat structure to metadata-based structure
2. **Future migrations**: Sequential version upgrades (v2→v3, v3→v4, etc.)

### 16.2 Version Detection

#### Database Version Structures

**v1 Structure (Legacy - Flat)**
```json
{
  "items": {
    "cloth cap:hibernia": {
      "id": "163421",
      "name": "Cloth Cap",
      "realm": "Hibernia"
    }
  },
  "item_count": 235,
  "last_updated": "2025-11-15 12:00:00"
}
```

**v2 Structure (Current - Metadata-based)**
```json
{
  "_metadata": {
    "version": 2,
    "last_update": "2025-12-02 14:20:54",
    "item_count": 235,
    "migration_history": [
      {
        "from_version": 1,
        "to_version": 2,
        "date": "2025-12-02 14:52:07",
        "backup_file": "items_database_migration_backup_20251202_145207.zip"
      }
    ]
  },
  "items": {
    "cloth cap:hibernia": {
      "id": "163421",
      "name": "Cloth Cap",
      "realm": "Hibernia",
      "_custom_fields": []
    }
  }
}
```

#### Version Detection Logic

**Function:** `get_db_version(db_data: dict) -> int`

```python
def get_db_version(db_data: dict) -> int:
    """
    Detect database version from structure.
    
    Args:
        db_data (dict): Database JSON content
    
    Returns:
        int: Database version (1 or 2)
        - v1: Flat structure without _metadata
        - v2: Contains _metadata section with version field
    
    Example:
        >>> data = load_database()
        >>> version = get_db_version(data)
        >>> print(f"Database version: v{version}")
        Database version: v2
    """
    if "_metadata" in db_data:
        return db_data["_metadata"].get("version", 2)
    return 1  # Legacy database
```

**Detection Rules:**
1. If `_metadata` section exists → v2+
2. If `_metadata.version` field exists → Use that version number
3. Otherwise → v1 (legacy flat structure)

### 16.3 Migration Process v1 → v2

#### High-Level Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIGRATION WORKFLOW v1 → v2                   │
└─────────────────────────────────────────────────────────────────┘

USER ACTION: Start application (settings dialog opens)
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Auto-Migration Check (Silent)                          │
│ Trigger: SettingsDialog.__init__()                             │
│ Condition: use_personal_database = True                        │
└─────────────────────────────────────────────────────────────────┘
      │
      ├──> Load personal database
      ├──> Detect version: get_db_version()
      │    - Personal DB: v1 (old)
      │    - Embedded DB: v2 (new)
      ├──> Compare versions: 1 < 2 → Migration needed
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Create Backup (Automatic)                              │
│ Function: create_backup()                                       │
│ Location: Backup/Database/                                     │
│ Format: items_database_migration_backup_YYYYMMDD_HHMMSS.zip    │
└─────────────────────────────────────────────────────────────────┘
      │
      ├──> Zip personal database file
      ├──> Save with timestamp
      ├──> Verify backup integrity
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Migrate Data (Intelligent Merge)                       │
│ Function: migrate_v1_to_v2()                                    │
│ Strategy: Preserve custom + Update standard                    │
└─────────────────────────────────────────────────────────────────┘
      │
      ├──> Load embedded database (v2 - source of truth)
      ├──> For each item in personal database:
      │    │
      │    ├──> Check if item exists in embedded DB
      │    │
      │    ├──> CASE 1: Item NOT in embedded DB → Custom item
      │    │    - Keep entire item unchanged
      │    │    - Add _custom_fields = ["*"]
      │    │    - Add to migrated database
      │    │
      │    ├──> CASE 2: Item in embedded DB → Standard item
      │    │    - Load item from embedded DB (latest data)
      │    │    - Compare with personal version
      │    │    - If user has custom fields:
      │    │      • Preserve custom values
      │    │      • Track in _custom_fields array
      │    │    - Merge into migrated database
      │    │
      │    └──> CASE 3: New items in embedded DB
      │         - Add new items from embedded DB
      │         - Mark as standard items (_custom_fields = [])
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Add Metadata Section                                   │
│ Function: _create_metadata_section()                            │
└─────────────────────────────────────────────────────────────────┘
      │
      ├──> Create _metadata object
      ├──> Set version = 2
      ├──> Set last_update = current timestamp
      ├──> Set item_count = len(migrated_items)
      ├──> Add migration history entry:
      │    {
      │      "from_version": 1,
      │      "to_version": 2,
      │      "date": "2025-12-02 14:52:07",
      │      "backup_file": "items_database_migration_backup_...zip"
      │    }
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Validate Migrated Database                             │
│ Function: validate_migrated_database()                          │
└─────────────────────────────────────────────────────────────────┘
      │
      ├──> Check _metadata section exists
      ├──> Verify version = 2
      ├──> Verify items is dict
      ├──> Check migration_history exists
      ├──> Validate no data corruption
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Save Migrated Database                                 │
│ Location: Armory/items_database.json                           │
└─────────────────────────────────────────────────────────────────┘
      │
      ├──> Write to personal database file
      ├──> Format: UTF-8 JSON with 2-space indent
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Log Migration Summary                                  │
└─────────────────────────────────────────────────────────────────┘
      │
      └──> Log statistics:
           - Custom items preserved: 0
           - Standard items updated: 235
           - New items added: 0
           - Migration: v1 → v2
           - Backup: items_database_migration_backup_...zip

RESULT: Personal database updated to v2 structure
        User customizations preserved
        Backup available for rollback if needed
```

#### Data Merging Strategy

**Function:** `merge_item_data(personal_item: dict, embedded_item: dict) -> tuple`

```python
def merge_item_data(personal_item: dict, embedded_item: dict) -> tuple:
    """
    Intelligently merge personal and embedded item data.
    
    Strategy:
        1. Use embedded item as base (latest structure)
        2. Preserve user customizations from personal item
        3. Track custom fields in _custom_fields array
    
    Args:
        personal_item (dict): User's current item data
        embedded_item (dict): Latest embedded item data
    
    Returns:
        tuple: (merged_item, custom_fields_list)
        - merged_item: Combined data with user customizations
        - custom_fields_list: List of fields user customized
    
    Example:
        Personal: {"merchant_price": "600", "custom_note": "Test"}
        Embedded: {"merchant_price": "500", "new_field": "Value"}
        Result:   {"merchant_price": "600", "new_field": "Value", 
                   "_custom_fields": ["merchant_price", "custom_note"]}
    """
    merged = dict(embedded_item)  # Start with embedded (latest)
    custom_fields = []
    
    for key, personal_value in personal_item.items():
        if key.startswith("_"):
            continue  # Skip internal fields
        
        embedded_value = embedded_item.get(key)
        
        # User customization detected
        if embedded_value is None or personal_value != embedded_value:
            merged[key] = personal_value
            custom_fields.append(key)
    
    return merged, custom_fields
```

**Custom Field Tracking:**

```json
{
  "cloth cap:hibernia": {
    "id": "163421",
    "name": "Cloth Cap",
    "merchant_price": "600",        // ← User changed from 500 to 600
    "custom_note": "My favorite",   // ← User added custom field
    "_custom_fields": [
      "merchant_price",
      "custom_note"
    ]
  }
}
```

### 16.4 Backup System

#### Backup Creation

**Function:** `create_backup() -> tuple`

```python
def create_backup() -> tuple[bool, Optional[str]]:
    """
    Create ZIP backup of personal database.
    
    Process:
        1. Check personal database exists
        2. Generate timestamped filename
        3. Create ZIP archive
        4. Verify ZIP integrity
    
    Returns:
        tuple: (success: bool, backup_path: str | None)
        - (True, "Backup/Database/items_database_migration_backup_...zip")
        - (False, None) on failure
    
    Backup Location:
        Backup/Database/items_database_migration_backup_YYYYMMDD_HHMMSS.zip
    
    Example:
        >>> success, backup_path = create_backup()
        >>> if success:
        ...     print(f"Backup created: {backup_path}")
        Backup created: Backup/Database/items_database_migration_backup_20251202_145207.zip
    """
```

**Backup Filename Format:**
```
items_database_migration_backup_YYYYMMDD_HHMMSS.zip

Example:
items_database_migration_backup_20251202_145207.zip
└─ Year: 2025
   └─ Month: 12
      └─ Day: 02
         └─ Hour: 14
            └─ Minute: 52
               └─ Second: 07
```

**Backup Contents:**
```
items_database_migration_backup_20251202_145207.zip
└── items_database.json  (original v1 database)
```

**Backup Folder Structure:**
```
Backup/
└── Database/
    ├── items_database_migration_backup_20251202_145207.zip
    ├── items_database_migration_backup_20251201_103045.zip
    └── items_database_migration_backup_20251130_092130.zip
```

#### Rollback Procedure

**Function:** `rollback_migration(backup_path: str) -> bool`

```python
def rollback_migration(backup_path: str) -> bool:
    """
    Restore database from backup ZIP.
    
    Args:
        backup_path (str): Path to backup ZIP file
    
    Returns:
        bool: True if rollback successful, False otherwise
    
    Process:
        1. Verify backup file exists
        2. Extract items_database.json from ZIP
        3. Overwrite current personal database
        4. Validate restored database
        5. Log rollback operation
    
    Example:
        >>> success = rollback_migration(
        ...     "Backup/Database/items_database_migration_backup_20251202_145207.zip"
        ... )
        >>> if success:
        ...     print("Database restored to v1")
    """
```

**Manual Rollback (if automated rollback fails):**

```powershell
# 1. Extract backup ZIP
Expand-Archive "Backup\Database\items_database_migration_backup_20251202_145207.zip" -DestinationPath "Temp"

# 2. Replace current database
Copy-Item "Temp\items_database.json" "Armory\items_database.json" -Force

# 3. Restart application
```

### 16.5 Validation

#### Post-Migration Validation

**Function:** `validate_migrated_database(data: dict) -> tuple`

```python
def validate_migrated_database(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate migrated database structure and integrity.
    
    Checks:
        1. _metadata section exists
        2. version field = 2
        3. last_update field present
        4. item_count matches actual count
        5. migration_history exists and valid
        6. items dict exists
        7. All items have required fields
    
    Args:
        data (dict): Migrated database content
    
    Returns:
        tuple: (is_valid: bool, error_message: str | None)
        - (True, None) if valid
        - (False, "Missing _metadata section") if invalid
    
    Example:
        >>> valid, error = validate_migrated_database(migrated_data)
        >>> if not valid:
        ...     print(f"Validation failed: {error}")
        ...     rollback_migration(backup_path)
    """
```

**Validation Rules:**

| Check | Description | Failure Action |
|-------|-------------|----------------|
| **Metadata Exists** | `_metadata` section present | Rollback |
| **Version Correct** | `version == 2` | Rollback |
| **Timestamp Valid** | `last_update` is valid datetime string | Warning only |
| **Item Count Match** | `item_count == len(items)` | Warning only |
| **History Present** | `migration_history` array exists | Warning only |
| **Items Dict** | `items` is dictionary | Rollback |
| **Required Fields** | All items have `id`, `name`, `realm` | Rollback |

**Example Validation Log:**
```
2025-12-02 14:52:15 [INFO] ITEMDB: Database validation passed
  ✓ Metadata section present
  ✓ Version: 2
  ✓ Last update: 2025-12-02 14:52:07
  ✓ Item count: 235 (matches actual)
  ✓ Migration history: 1 entry
  ✓ Items structure valid
```

### 16.6 Integration Points

#### Settings Dialog Auto-Migration

**File:** `UI/settings_dialog.py`

**Function:** `_check_items_database_migration()`

```python
def _check_items_database_migration(self):
    """
    Check if items database migration is needed.
    Runs automatically when settings dialog opens.
    
    Conditions:
        - Personal database mode enabled (use_personal_database = True)
        - Personal database file exists
        - Version mismatch detected
    
    Behavior:
        - Silent operation (no user prompts)
        - Only logs to file
        - Errors shown in message box
    
    Called from:
        SettingsDialog.__init__()
    """
    if not self.use_personal_db:
        return  # Mode 1 (internal) - no migration needed
    
    personal_db_path = Path(self.personal_db_path)
    if not personal_db_path.exists():
        return  # No personal database yet
    
    try:
        # Attempt migration
        result = self.migrate_items_db()
        
        if result['migration_applied']:
            logger.info(f"Items database migrated: v{result['personal_version']} → v{result['embedded_version']}")
        else:
            logger.debug("Items database already up to date")
    
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        QMessageBox.warning(
            self,
            "Migration Error",
            f"Failed to check database migration: {e}"
        )
```

**Trigger Point:**
```python
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... UI setup ...
        
        # Auto-migration check (silent)
        self._check_items_database_migration()
```

**User Experience:**
- ✅ **Silent**: No popup dialogs during migration
- ✅ **Automatic**: Runs on every settings dialog open
- ✅ **Safe**: Backup created before migration
- ✅ **Fast**: Typically completes in <1 second
- ✅ **Logged**: All operations logged to file

### 16.7 Testing

#### Test Script

**File:** `Tools/test_items_migration.py`

**Test Suite:**
1. **Version Detection** - Detect v1 and v2 databases
2. **Migration Need Detection** - Determine if migration required
3. **Backup Creation** - Create and verify backup ZIP
4. **Dry-Run Migration** - Simulate migration without changes
5. **Actual Migration** - Perform real migration
6. **Database Validation** - Verify migrated database structure
7. **Rollback** - Restore from backup

**Running Tests:**
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run test suite
python .\Tools\test_items_migration.py
```

**Example Output:**
```
======================================================================
  ITEMS DATABASE MIGRATION - TEST SUITE
======================================================================

TEST 1: Version Detection
  ✓ Embedded database version: v2
  ✓ Personal database version: v1

TEST 2: Migration Need Detection
  Personal version: v1
  Embedded version: v2
  ✓ Migration needed: v1 → v2

TEST 3: Backup Creation
  ✓ Backup created successfully
  Path: Backup/Database\items_database_migration_backup_20251202_145159.zip
  Size: 8,598 bytes

TEST 4: Dry-Run Migration
  Statistics:
    - personal_version: 1
    - embedded_version: 2
    - migration_applied: True
    - custom_items_preserved: 0
    - standard_items_updated: 235
    - new_items_added: 0
  ✓ Dry-run completed successfully

TEST 5: Actual Migration
  Apply migration? (y/n): y
  ✓ Migration completed successfully
  ✓ Migrated database version: v2
    Item count: 235
    Custom items: 0
    Updated items: 235
    New items: 0
    Migration History:
      - v1 → v2 (2025-12-02 14:52:07)

TEST 6: Database Validation
  ✓ Database validation passed

TEST 7: Rollback Test
  Rollback to backup? (y/n): y
  ✓ Rollback successful: Restored from backup

TEST SUMMARY
  ✓ PASS: Version Detection
  ✓ PASS: Migration Need Detection
  ✓ PASS: Backup Creation
  ✓ PASS: Dry-Run Migration
  ✓ PASS: Actual Migration
  ✓ PASS: Database Validation
  ✓ PASS: Rollback
  Total: 7/7 tests passed
  🎉 All tests passed!
```

### 16.8 Logging

**Log Category:** All migration operations use `extra={"action": "ITEMDB"}`

**Log Levels:**

| Level | Usage | Example |
|-------|-------|---------|
| **INFO** | Migration start/complete, version detection | `Migration v1 → v2 started` |
| **WARNING** | Non-critical issues | `Custom fields detected: merchant_price` |
| **ERROR** | Migration failures, validation errors | `Migration failed: Invalid database structure` |
| **DEBUG** | Detailed operation info | `Processing item: cloth cap:hibernia` |

**Log Examples:**
```python
# Migration start
logger.info("Items database migration check started", extra={"action": "ITEMDB"})

# Version detection
logger.info(f"Personal DB version: v{personal_version}", extra={"action": "ITEMDB"})
logger.info(f"Embedded DB version: v{embedded_version}", extra={"action": "ITEMDB"})

# Backup creation
logger.info(f"Backup created: {backup_path}", extra={"action": "ITEMDB"})

# Migration progress
logger.debug(f"Processing custom item: {item_key}", extra={"action": "ITEMDB"})
logger.debug(f"Merging standard item: {item_key}", extra={"action": "ITEMDB"})

# Migration complete
logger.info(f"Migration v{from_v} → v{to_v} completed successfully", extra={"action": "ITEMDB"})
logger.info(f"Custom items preserved: {stats['custom_items_preserved']}", extra={"action": "ITEMDB"})

# Validation
logger.info("Migrated database validation passed", extra={"action": "ITEMDB"})

# Rollback
logger.warning(f"Rollback initiated: {backup_path}", extra={"action": "ITEMDB"})
logger.info("Rollback completed successfully", extra={"action": "ITEMDB"})
```

**Log File Location:** `Logs/application_YYYYMMDD.log`

**Example Log Entry:**
```
2025-12-02 14:52:07 [INFO] ITEMDB: Migration v1 → v2 started
2025-12-02 14:52:07 [INFO] ITEMDB: Backup created: Backup/Database/items_database_migration_backup_20251202_145207.zip
2025-12-02 14:52:08 [DEBUG] ITEMDB: Processing custom item: my custom sword:albion
2025-12-02 14:52:08 [DEBUG] ITEMDB: Merging standard item: cloth cap:hibernia
2025-12-02 14:52:15 [INFO] ITEMDB: Migration v1 → v2 completed successfully
2025-12-02 14:52:15 [INFO] ITEMDB: Custom items preserved: 0
2025-12-02 14:52:15 [INFO] ITEMDB: Standard items updated: 235
2025-12-02 14:52:15 [INFO] ITEMDB: New items added: 0
```

### 16.9 Future Migrations

#### Migration Framework Design

**Sequential Migration Support:**

```python
# Future migration functions
def migrate_v2_to_v3(personal_data: dict, embedded_data: dict) -> dict:
    """
    Migrate from v2 to v3.
    Example: Add new fields, restructure data, etc.
    """
    pass

def migrate_v3_to_v4(personal_data: dict, embedded_data: dict) -> dict:
    """
    Migrate from v3 to v4.
    """
    pass

# Main migration orchestrator
def migrate_personal_database():
    personal_version = get_db_version(personal_data)
    embedded_version = get_db_version(embedded_data)
    
    # Sequential migration path
    if personal_version == 1 and embedded_version == 2:
        migrate_v1_to_v2(personal_data, embedded_data)
    elif personal_version == 1 and embedded_version == 3:
        migrate_v1_to_v2(personal_data, embedded_data)  # First
        migrate_v2_to_v3(personal_data, embedded_data)  # Then
    elif personal_version == 2 and embedded_version == 3:
        migrate_v2_to_v3(personal_data, embedded_data)
    # ... etc.
```

**Migration History Tracking:**

```json
{
  "_metadata": {
    "version": 3,
    "migration_history": [
      {
        "from_version": 1,
        "to_version": 2,
        "date": "2025-12-02 14:52:07",
        "backup_file": "items_database_migration_backup_20251202_145207.zip"
      },
      {
        "from_version": 2,
        "to_version": 3,
        "date": "2025-12-15 10:30:22",
        "backup_file": "items_database_migration_backup_20251215_103022.zip"
      }
    ]
  }
}
```

### 16.10 Best Practices

#### ✅ DO: Always Create Backups

```python
# CORRECT: Backup before migration
success, backup_path = create_backup()
if not success:
    logger.error("Backup creation failed - aborting migration")
    return

# Proceed with migration
migrate_v1_to_v2(personal_data, embedded_data)
```

#### ✅ DO: Validate After Migration

```python
# CORRECT: Validate migrated database
migrated_data = migrate_v1_to_v2(personal_data, embedded_data)

valid, error = validate_migrated_database(migrated_data)
if not valid:
    logger.error(f"Validation failed: {error}")
    rollback_migration(backup_path)
    return False
```

#### ✅ DO: Preserve User Customizations

```python
# CORRECT: Use merge strategy
merged_item, custom_fields = merge_item_data(personal_item, embedded_item)
if custom_fields:
    merged_item["_custom_fields"] = custom_fields
```

#### ❌ DON'T: Overwrite User Data

```python
# WRONG: This loses user customizations!
migrated_items = embedded_data["items"]  # ← Destroys personal data

# CORRECT: Merge intelligently
migrated_items = {}
for key, personal_item in personal_data["items"].items():
    embedded_item = embedded_data["items"].get(key)
    if embedded_item:
        migrated_items[key], _ = merge_item_data(personal_item, embedded_item)
    else:
        migrated_items[key] = personal_item  # Custom item
```

#### ✅ DO: Log Migration Operations

```python
# CORRECT: Comprehensive logging
logger.info(f"Migration v{from_v} → v{to_v} started", extra={"action": "ITEMDB"})
logger.info(f"Custom items preserved: {custom_count}", extra={"action": "ITEMDB"})
logger.info(f"Standard items updated: {updated_count}", extra={"action": "ITEMDB"})
logger.info(f"New items added: {new_count}", extra={"action": "ITEMDB"})
```

### 16.11 Troubleshooting

#### Issue 1: "Migration loops infinitely"

**Symptoms:**
- Migration runs every time settings dialog opens
- Version never updates to v2

**Diagnosis:**
```python
# Check if database is actually being saved
personal_db_path = Path("Armory/items_database.json")
data = json.loads(personal_db_path.read_text(encoding="utf-8"))
print(f"Version in file: {data.get('_metadata', {}).get('version')}")
```

**Solutions:**
1. Verify write permissions on `Armory/` folder
2. Check for file locking issues
3. Ensure migration function saves database
4. Review logs for save errors

#### Issue 2: "Custom items lost after migration"

**Symptoms:**
- User-added items missing after migration
- Only embedded items remain

**Diagnosis:**
```python
# Check migration log for custom items
# Should see: "Processing custom item: my custom sword:albion"
```

**Solutions:**
1. Verify `merge_item_data()` preserves custom items
2. Check for logic errors in custom item detection
3. Restore from backup
4. Manually re-add custom items

#### Issue 3: "Migration fails with validation error"

**Symptoms:**
- Migration completes but validation fails
- Database rollback triggered

**Diagnosis:**
```python
# Check validation error message
valid, error = validate_migrated_database(migrated_data)
print(f"Validation error: {error}")
```

**Solutions:**
1. Review migration logic for structural errors
2. Verify all required fields populated
3. Check for data type mismatches
4. Restore from backup and retry

#### Issue 4: "Backup creation fails"

**Symptoms:**
- Migration aborted before starting
- "Backup creation failed" error

**Diagnosis:**
```python
# Check backup folder exists and is writable
backup_folder = Path("Backup/Database")
print(f"Exists: {backup_folder.exists()}")
print(f"Writable: {os.access(backup_folder, os.W_OK)}")
```

**Solutions:**
1. Create `Backup/Database/` folder manually
2. Check disk space (ZIP requires temporary space)
3. Verify write permissions
4. Close any programs using database file

### 16.12 Related Files

**Core Migration Module:**
- `Functions/items_database_migration.py` - Main migration orchestrator

**Integration Points:**
- `UI/settings_dialog.py` - Auto-migration trigger
- `Functions/items_database_manager.py` - Database manager (loads migrated data)

**Test & Validation:**
- `Tools/test_items_migration.py` - Comprehensive test suite

**Data Files:**
- `Data/items_database_src.json` - Embedded database (v2)
- `Armory/items_database.json` - Personal database (v1 or v2)
- `Backup/Database/items_database_migration_backup_*.zip` - Backups

**Configuration:**
- `Configuration/config.json` - Database mode settings

---

## 17. Item Price Management Module

### 17.1 Overview

The **Item Price Manager** module (`Functions/items_price_manager.py`) provides specialized functions for synchronizing item prices between template metadata and the items database. It handles price validation, deduplication, and missing item detection.

**Purpose:**
- Synchronize template item prices with database prices
- Identify items without prices in templates
- Maintain database as single source of truth for prices
- Support multi-realm item lookup

**Module Location:** `Functions/items_price_manager.py`  
**Lines of Code:** 205  
**Functions:** 2  
**Dependencies:** json, logging, typing (Dict, List, Optional, Any)

### 17.2 Core Functions

#### Function 1: `items_price_sync_template()`

**Purpose:** Synchronize template metadata prices with database, removing duplicates

**Signature:**
```python
def items_price_sync_template(
    metadata_path: str,
    metadata: Dict[str, Any],
    db_manager=None,
    realm: str = ""
) -> int
```

**Parameters:**
- `metadata_path` (str): Full path to template metadata JSON file
- `metadata` (Dict): Parsed metadata dict containing prices
- `db_manager` (optional): ItemsDatabaseManager instance for lookups
- `realm` (str): Target realm (Albion, Hibernia, Midgard, All)

**Returns:** int - Count of items synchronized to database

**Logic Flow:**
1. Check if metadata contains 'prices' dictionary
2. For each item in prices:
   - Search database with realm-specific key (name:realm)
   - Fallback to ":all" suffix search
   - Fallback to generic name search
3. If item found in database with merchant_price:
   - Mark item for removal from JSON (database is source of truth)
4. Remove marked items from metadata prices
5. Save updated metadata back to file
6. Return count of synced items

**Example Usage:**
```python
from Functions.items_price_manager import items_price_sync_template
from Functions.items_database_manager import ItemsDatabaseManager

db_manager = ItemsDatabaseManager()
metadata_path = "Armory/Hibernia/template.metadata.json"
metadata = {"prices": {"Sword": {"price": 100}, ...}}

synced_count = items_price_sync_template(
    metadata_path=metadata_path,
    metadata=metadata,
    db_manager=db_manager,
    realm="Hibernia"
)
print(f"Synced {synced_count} items to database")
```

**Error Handling:**
- Returns 0 if no prices found in metadata
- Catches all exceptions with logging
- Non-blocking: continues if individual lookups fail
- Preserves original metadata if save fails

#### Function 2: `items_price_find_missing()`

**Purpose:** Identify items without prices in template metadata or database

**Signature:**
```python
def items_price_find_missing(
    items_list: List[Dict[str, Any]],
    realm: str,
    db_manager=None,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `items_list` (List[Dict]): List of item dicts from template parse
- `realm` (str): Target realm for lookup
- `db_manager` (optional): ItemsDatabaseManager instance
- `metadata` (optional): Template metadata dict with prices

**Returns:** List[Dict] - Items with price status details

**Logic Flow:**
1. For each item in items_list:
   - Check if price exists in metadata (if provided)
   - Check if price exists in database:
     - Try realm-specific key (name:realm)
     - Try ":all" suffix variant
     - Try generic name search
   - Build result dict with:
     - item name and slot
     - has_price_in_metadata (bool)
     - has_price_in_db (bool)
     - price_value (if found)
     - price_source (metadata/db/none)
2. Return list of items lacking prices

**Example Usage:**
```python
from Functions.items_price_manager import items_price_find_missing
from Functions.items_database_manager import ItemsDatabaseManager

db_manager = ItemsDatabaseManager()
items = [
    {"name": "Sword", "slot": "Right Hand"},
    {"name": "Armor", "slot": "Torso"},
]
metadata = {"prices": {"Sword": {"price": 100}}}

missing = items_price_find_missing(
    items_list=items,
    realm="Hibernia",
    db_manager=db_manager,
    metadata=metadata
)

for item in missing:
    if not item['has_price_in_metadata'] and not item['has_price_in_db']:
        print(f"Missing: {item['name']} ({item['slot']})")
```

**Returns Structure:**
```python
[
    {
        "name": "Armor Item",
        "slot": "Torso",
        "has_price_in_metadata": False,
        "has_price_in_db": False,
        "price_value": None,
        "price_source": "none"
    },
    {
        "name": "Sword",
        "slot": "Right Hand",
        "has_price_in_metadata": True,
        "has_price_in_db": True,
        "price_value": 100,
        "price_source": "metadata"
    }
]
```

**Error Handling:**
- Debug logging for each search attempt
- Non-blocking on lookup failures
- Returns items with is_price_missing=True on any error
- Never crashes, always returns valid list

### 17.3 Integration Points

**UI Integration:**
- `UI/dialogs.py` - ArmorManagementDialog class
  - `_sync_template_prices_with_db()` - Thin wrapper calling `items_price_sync_template()`
  - `search_missing_prices()` - UI method that launches SearchMissingPricesDialog

**Database Integration:**
- `Functions/items_database_manager.py` - ItemsDatabaseManager
  - `get_item()` - Search by name:realm composite key
  - `search_item()` - Generic name search

**Template System:**
- `Functions/template_manager.py` - Loads template metadata
- `Functions/items_price_manager.py` - Works with template metadata dicts

### 17.4 Realm-Aware Price Lookup Strategy

The module implements a robust 3-tier fallback strategy for realm-aware searches:

```python
# Tier 1: Exact realm match
search_key = f"{item_name}:{realm}"
item = db_manager.get_item(search_key)

# Tier 2: Universal items (":all" realm)
if not item:
    search_key = f"{item_name}:all"
    item = db_manager.get_item(search_key)

# Tier 3: Generic fallback
if not item:
    item = db_manager.search_item(item_name)
```

**Rationale:**
- **Tier 1** ensures realm-specific prices are used
- **Tier 2** finds universal items available in all realms
- **Tier 3** catches items by name without realm specificity

### 17.5 Quality Standards

**Code Quality:**
- ✅ PEP 8 compliant (ruff validation: 0 errors)
- ✅ Line length <88 characters
- ✅ Type hints on all parameters and returns
- ✅ Comprehensive docstrings with examples

**Error Handling:**
- ✅ Try-except blocks with logging
- ✅ Graceful degradation on failures
- ✅ Non-blocking operations
- ✅ Debug-level logging for troubleshooting

**Testing:**
- ✅ Syntax validation passed
- ✅ App integration verified
- ✅ Backward compatibility maintained

### 17.6 Best Practices

#### ✅ DO: Use with ItemsDatabaseManager

```python
from Functions.items_database_manager import ItemsDatabaseManager

db_manager = ItemsDatabaseManager()
count = items_price_sync_template(
    metadata_path,
    metadata,
    db_manager=db_manager,  # Pass manager for better results
    realm="Hibernia"
)
```

#### ❌ DON'T: Mix Price Sources

```python
# WRONG: Don't manually update prices in JSON while using this module
# It will remove them!
metadata['prices']['My Sword'] = {'price': 999}  # ← Will be synced away
```

#### ✅ DO: Check Results

```python
missing = items_price_find_missing(items, realm, db_manager, metadata)
no_price_count = len([i for i in missing if not i['has_price_in_metadata'] and not i['has_price_in_db']])
print(f"Items without price: {no_price_count}")
```

### 17.7 Related Files

**Module File:**
- `Functions/items_price_manager.py` - Price management functions

**Integration Points:**
- `UI/dialogs.py` - ArmorManagementDialog wrapper methods
- `Functions/template_manager.py` - Template loading
- `Functions/items_database_manager.py` - Database access

**Dialogs:**
- `UI/dialogs.py:SearchMissingPricesDialog` - UI for missing prices

---

## Document Information

**Created:** 2025-11-19  
**Version:** 2.4  
**Author:** Technical Documentation Team  
**Last Reviewed:** 2025-12-18

**Change Log:**
- **2025-12-18 (v2.4):** Added Item Price Management Module documentation
  - Added items_price_manager.py module section
  - Documented items_price_sync_template() function
  - Documented items_price_find_missing() function
  - Added realm-aware price lookup strategy
  - Added integration points and best practices
  - Added quality standards and error handling
- **2025-12-02 (v2.3):** Merged Items Database Migration documentation
  - Added migration system overview
  - Added v1 → v2 migration process details
  - Added backup and rollback procedures
  - Added validation and testing documentation
  - Added integration points and logging
  - Added best practices and troubleshooting
- **2025-11-24 (v2.2):** Added Database Editor Interface documentation, Currency support for Ices/Souls
- **2025-11-20 (v2.1):** Currency normalization and template system updates
- **2025-11-19 (v2.0):** Initial comprehensive documentation

**Related Documents:**
- `Data/items_database_src.json` - Internal database file
- `Armory/items_database.json` - Personal database file (Mode 2)
- `Functions/items_scraper.py` - Scraper implementation
- `Functions/items_price_manager.py` - Item price synchronization
- `Functions/superadmin_tools.py` - Database management
- `Functions/items_database_manager.py` - Dual-mode manager
- `Functions/items_database_migration.py` - Migration orchestrator
- `UI/dialogs.py` - ArmorManagementDialog with price integration
- `UI/mass_import_monitor.py` - Import monitoring window with threading
- `Tools/test_items_migration.py` - Migration test suite
