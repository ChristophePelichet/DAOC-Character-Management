# 👤 Character System - Technical Documentation

**Version**: 2.5  
**Date**: December 2025  
**Last Updated**: December 19, 2025 (Character Rename Handler module added - Phase 17)  
**Components**: `UI/dialogs.py` (CharacterSheetWindow), `Functions/character_validator.py`, `Functions/character_rr_calculator.py`, `Functions/character_herald_scrapper.py`, `Functions/character_banner.py`, `Functions/character_achievement_formatter.py`, `Functions/character_rename_handler.py`  
**Related**: `Functions/character_manager.py`, `Functions/character_schema.py`, `Functions/character_migration.py`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Character Validator Module (Phase 4)](#character-validator-module-phase-4)
3. [Character RR Calculator Module (Phase 5)](#character-rr-calculator-module-phase-5)
4. [Character Herald Scrapper Module (Phase 6)](#character-herald-scrapper-module-phase-6)
5. [Character Banner Module (Phase 7)](#character-banner-module-phase-7)
6. [Character Achievement Formatter Module (Phase 11)](#character-achievement-formatter-module-phase-11)
7. [Character Rename Handler Module (Phase 17)](#character-rename-handler-module-phase-17)
8. [Character Schema](#character-schema)
9. [Migration System](#migration-system)
10. [Integration](#integration)
11. [Error Handling](#error-handling)
12. [Usage Guide](#usage-guide)
13. [Implementation Progress](#implementation-progress)

---

## Overview

The Character System provides comprehensive character management including:

- **Character Data Validation**: Class/race validation and dropdown population with multi-language support
- **Character Realm Rank**: RR calculations, level filtering, and progression tracking
- **Character Schema**: Strict validation of character JSON structure
- **Character Migration**: Automatic migration from old flat structure to season-based hierarchy
- **Character UI**: Character sheet with real-time data updates

### Key Features

- ✅ **Multi-language support** (EN/FR/DE) for class and race names
- ✅ **Realm-aware class/race filtering** for valid game combinations
- ✅ **Realm Rank calculations** from realm points with progression info
- ✅ **Level filtering** based on rank restrictions
- ✅ **Automatic data persistence** with character_data updates
- ✅ **Cascade updates** when realm or class changes
- ✅ **Schema validation** with strict requirements
- ✅ **Automatic migration** from old to new structure
- ✅ **Complete backup** with rollback capability

### System Components

1. **Character Validator** - Class/race management and validation (Phase 4)
2. **Character RR Calculator** - Realm rank calculations and level management (Phase 5)
3. **Character Herald Scrapper** - Herald data scraping and stats UI updates (Phase 6)
4. **Character Banner** - Class banner image management and display (Phase 7)
5. **Character Schema** - Data structure definition and validation
6. **Character Migration** - Automatic old→new structure migration
7. **Character Manager** - Main integration and lifecycle management

---

## Character Validator Module (Phase 4)

### Overview

The Character Validator module (`Functions/character_validator.py`) provides functions for character class and race validation with automatic dropdown population and multi-language display support.

**Extracted from**: `UI/dialogs.py` CharacterSheetWindow class  
**Date Completed**: December 18, 2025  
**Lines Removed from dialogs.py**: ~80  
**Lines in new module**: ~280  
**Functions Extracted**: 5

### Architecture

#### Core Functions

The module provides 5 main functions for character validation and UI update:

```python
# Data retrieval functions
character_get_classes_for_realm(data_manager, realm)
character_get_races_for_class(data_manager, realm, class_name=None)

# UI population functions
character_populate_classes_combo(combo_widget, data_manager, realm)
character_populate_races_combo(combo_widget, data_manager, realm, class_name=None)

# Event handlers
character_handle_realm_change(combo_realm, combo_class, combo_race, data_manager, character_data)
character_handle_class_change(combo_class, combo_race, data_manager, realm, character_data)
character_handle_race_change(combo_race, character_data)
```

#### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│         Character Sheet Window (dialogs.py)                 │
│    (User selects realm/class/race in dropdowns)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  Event Handler (dialogs.py)  │
          │  _on_realm_changed_sheet()  │
          │  _on_class_changed_sheet()  │
          │  _on_race_changed_sheet()   │
          └──────────────┬───────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────┐
    │  character_validator.py Functions         │
    │  character_handle_*_change()               │
    │  • Validate selection                      │
    │  • Update character_data dict              │
    │  • Return new value                        │
    └────────────────┬───────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ▼                          ▼
   ┌─────────────┐          ┌──────────────────┐
   │ character_  │          │ UI Update        │
   │ populate_   │          │ (dialogs.py)     │
   │ *_combo()   │          │ _update_banner() │
   │             │          │ (triggers)       │
   │ • Clear     │          └──────────────────┘
   │ • Get data  │
   │ • Add items │
   │ • Translate │
   └─────────────┘
```

### Functions Reference

#### 1. character_get_classes_for_realm()

**Purpose**: Retrieve available classes for a specific realm

**Signature**:
```python
def character_get_classes_for_realm(data_manager, realm: str) -> list
```

**Parameters**:
- `data_manager`: DataManager instance
- `realm`: Realm name (e.g., 'Albion', 'Hibernia', 'Midgard')

**Returns**: List of class dictionaries with:
- `name`: Actual English class name
- `name_fr`: French translation (if available)
- `name_de`: German translation (if available)

**Example**:
```python
classes = character_get_classes_for_realm(data_manager, 'Albion')
# Returns: [
#     {'name': 'Paladin', 'name_fr': 'Paladin', 'name_de': 'Paladin'},
#     {'name': 'Cleric', 'name_fr': 'Clerc', 'name_de': 'Priester'},
#     ...
# ]
```

#### 2. character_get_races_for_class()

**Purpose**: Retrieve available races for a realm, optionally filtered by class

**Signature**:
```python
def character_get_races_for_class(data_manager, realm: str, class_name: str = None) -> list
```

**Parameters**:
- `data_manager`: DataManager instance
- `realm`: Realm name
- `class_name`: Optional class name to filter available races. If None, returns all races.

**Returns**: List of race dictionaries with name and translations

**Example**:
```python
# All races in Albion
races = character_get_races_for_class(data_manager, 'Albion')

# Only races available for Paladin in Albion
races = character_get_races_for_class(data_manager, 'Albion', 'Paladin')
```

#### 3. character_populate_classes_combo()

**Purpose**: Populate QComboBox widget with translated class names

**Signature**:
```python
def character_populate_classes_combo(combo_widget, data_manager, realm: str) -> None
```

**Features**:
- ✅ Clears existing items
- ✅ Retrieves classes for realm
- ✅ Displays translated names based on `config.get("ui.language")`
- ✅ Stores actual English name as itemData for programmatic access
- ✅ Handles missing translations gracefully

**Language Support**:
```
Current Language: FR
Display: "Clerc" (translated)
ItemData: "Cleric" (actual name)

Current Language: EN
Display: "Cleric"
ItemData: "Cleric"
```

#### 4. character_populate_races_combo()

**Purpose**: Populate QComboBox widget with translated race names, optionally filtered by class

**Signature**:
```python
def character_populate_races_combo(combo_widget, data_manager, realm: str, class_name: str = None) -> None
```

**Features**:
- ✅ Clears existing items
- ✅ Retrieves races (all or filtered by class)
- ✅ Translates display names
- ✅ Stores actual names as itemData
- ✅ Handles cascading validation

#### 5. character_handle_realm_change()

**Purpose**: Handle realm selection change with cascade updates

**Signature**:
```python
def character_handle_realm_change(combo_realm, combo_class, combo_race, data_manager, character_data: dict) -> str
```

**Behavior**:
1. Gets new realm from combo_realm
2. Updates `character_data['realm']` with new realm
3. Calls `character_populate_classes_combo()` to refresh available classes
4. Calls `character_populate_races_combo()` to refresh available races (no class selected)
5. Returns new realm name

**Data Updates**: Updates character_data dict in place

**Example**:
```python
new_realm = character_handle_realm_change(
    self.realm_combo, self.class_combo, self.race_combo,
    self.data_manager, self.character_data
)
# After: character_data['realm'] = new_realm
# After: Both class and race combos refreshed
```

#### 6. character_handle_class_change()

**Purpose**: Handle class selection change with race filtering

**Signature**:
```python
def character_handle_class_change(combo_class, combo_race, data_manager, realm: str, character_data: dict) -> str
```

**Behavior**:
1. Gets selected class from combo_class itemData
2. Updates `character_data['class']` with new class
3. Calls `character_populate_races_combo()` with class filter
4. Returns new class name

**Data Updates**: Updates character_data dict in place

**Example**:
```python
new_class = character_handle_class_change(
    self.class_combo, self.race_combo,
    self.data_manager, self.realm, self.character_data
)
# After: character_data['class'] = new_class
# After: race_combo shows only valid races for new class
```

#### 7. character_handle_race_change()

**Purpose**: Handle race selection change

**Signature**:
```python
def character_handle_race_change(combo_race, character_data: dict) -> str
```

**Behavior**:
1. Gets selected race from combo_race itemData
2. Updates `character_data['race']` with new race
3. Returns new race name

**Note**: Currently a placeholder. Future enhancements could include banner updates or race-specific logic.

---

## Character RR Calculator Module (Phase 5)

### Overview

The Character RR Calculator module (`Functions/character_rr_calculator.py`) provides functions for character realm rank calculations, including rank determination from realm points, level filtering based on rank restrictions, and progression information to the next rank level.

**Extracted from**: `UI/dialogs.py` CharacterSheetWindow class  
**Date Completed**: December 18, 2025  
**Lines Removed from dialogs.py**: ~50  
**Lines in new module**: ~200  
**Functions Extracted**: 3

### Architecture

#### Core Functions

The module provides 3 main functions for realm rank management:

```python
# Level management
character_rr_get_valid_levels(rank) -> list

# Progression information
character_rr_calculate_points_info(data_manager, realm, rank, level) -> dict

# Rank calculation from points
character_rr_calculate_from_points(data_manager, realm, realm_points) -> dict
```

#### Realm Rank System

- **14 Ranks** (1-14) with multiple levels per rank
- **Rank 1**: levels 0-10 (11 levels)
- **Ranks 2-14**: levels 0-9 (10 levels each)
- **Data Source**: `realm_ranks.json` (loaded via DataManager)
- **Level String Format**: `{rank}L{level}` (e.g., "5L3" for Rank 5 Level 3)

### Function Reference

#### 1. character_rr_get_valid_levels()

**Purpose**: Get valid level range for a given realm rank

**Signature**:
```python
def character_rr_get_valid_levels(rank: int) -> list
```

**Parameters**:
- `rank` (int): Realm rank number (1-14)

**Returns**:
- List of valid level numbers for this rank
- Rank 1: [0, 1, 2, ..., 10]
- Other ranks: [0, 1, 2, ..., 9]

**Example**:
```python
levels = character_rr_get_valid_levels(1)
# Returns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

levels = character_rr_get_valid_levels(5)
# Returns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

#### 2. character_rr_calculate_points_info()

**Purpose**: Get progression information from current rank/level to next level

**Signature**:
```python
def character_rr_calculate_points_info(data_manager, realm: str, rank: int, level: int) -> dict
```

**Parameters**:
- `data_manager`: DataManager instance for accessing rank data
- `realm` (str): Realm name (e.g., 'Albion', 'Midgard', 'Hibernia')
- `rank` (int): Current realm rank (1-14)
- `level` (int): Current level within rank (0-10 for rank 1, 0-9 for others)

**Returns**:
```python
{
    'current_points': int,        # RP at current level
    'next_points': int,           # RP at next level
    'percentage': float,          # Completion % (0-100)
    'current_level_str': str     # e.g., "1L5"
}
```

**Behavior**:
1. Constructs level string from rank and level
2. Looks up current rank info from data_manager
3. Determines next level (or next rank if at max level)
4. Calculates progression percentage
5. Returns dict with all progression info

**Example**:
```python
info = character_rr_calculate_points_info(
    data_manager, 'Albion', 1, 5
)
# Returns:
# {
#     'current_points': 12345,
#     'next_points': 15000,
#     'percentage': 23.5,
#     'current_level_str': '1L5'
# }
```

#### 3. character_rr_calculate_from_points()

**Purpose**: Calculate realm rank and level from total realm points

**Signature**:
```python
def character_rr_calculate_from_points(data_manager, realm: str, realm_points) -> dict
```

**Parameters**:
- `data_manager`: DataManager instance for accessing rank data
- `realm` (str): Realm name (e.g., 'Albion', 'Midgard', 'Hibernia')
- `realm_points` (int or str): Total realm points (handles string with commas/spaces)

**Returns**:
```python
{
    'rank': int,              # Rank number (1-14)
    'level': int,             # Level within rank (0-10 or 0-9)
    'title': str,             # Rank title (e.g., "Guardian", "Hero")
    'level_str': str,         # e.g., "1L5"
    'realm_points': int      # Total realm points
}
```

**Behavior**:
1. Normalizes realm_points (removes commas, spaces, non-breaking spaces)
2. Calls `data_manager.get_realm_rank_info()` for lookup
3. Returns rank info or falls back to Rank 1 Guardian if lookup fails
4. Graceful error handling with logging

**Example**:
```python
info = character_rr_calculate_from_points(
    data_manager, 'Albion', 1500000
)
# Returns:
# {
#     'rank': 5,
#     'level': 3,
#     'title': 'Hero',
#     'level_str': '5L3',
#     'realm_points': 1500000
# }

# Also handles string input with formatting
info = character_rr_calculate_from_points(
    data_manager, 'Albion', "1,500,000"
)
# Works the same way - normalizes the string
```

### Integration with dialogs.py

The CharacterSheetWindow class uses thin wrapper methods that call the calculator functions:

```python
# Update level dropdown with valid levels for rank
valid_levels = character_rr_get_valid_levels(rank)
for level in valid_levels:
    self.level_combo_rank.addItem(f"L{level}", level)

# Get progression info for display
info = character_rr_calculate_points_info(
    self.parent_app.data_manager, self.realm, rank, level
)

# Calculate rank from realm points
rank_info = character_rr_calculate_from_points(
    self.parent_app.data_manager, self.realm, realm_points
)
```

### Integration with dialogs.py

The CharacterSheetWindow class now uses thin wrapper methods that call the character_validator functions:

```python
def _populate_classes_sheet(self):
    """Populates class dropdown based on selected realm."""
    character_populate_classes_combo(
        self.class_combo, self.data_manager, self.realm_combo.currentText()
    )

def _on_realm_changed_sheet(self):
    """Called when realm is changed in character sheet."""
    character_handle_realm_change(
        self.realm_combo, self.class_combo, self.race_combo,
        self.data_manager, self.character_data
    )
    # UI update after logic
    self._update_class_banner()
```

**Separation of Concerns**:
- **character_validator.py**: Business logic (data retrieval, validation, updates)
- **dialogs.py**: UI logic (thin wrappers, banner updates, signal handling)

### Multi-Language Support

All functions respect the active UI language setting:

```python
current_language = config.get("ui.language", "en")
```

**Supported Languages**:
- `en`: English (default)
- `fr`: French
- `de`: German

**Fallback Logic**:
```
If current_language is French:
  Try "name_fr" field
  If not available, use "name"
If current_language is German:
  Try "name_de" field
  If not available, use "name"
If current_language is English:
  Use "name" field
```

### Error Handling

All functions include try-except blocks with logging:

```python
try:
    # Function logic
except Exception as e:
    logger.error(f"Failed to handle realm change: {e}")
    return combo_realm.currentText()  # Graceful fallback
```

### Quality Metrics

- ✅ **PEP 8 Compliant**: All lines < 88 chars (Black format)
- ✅ **Type Hints**: Full type annotations on all functions
- ✅ **Docstrings**: Comprehensive docstrings with examples
- ✅ **Logging**: Proper error logging and debug messages
- ✅ **No Hardcoded Strings**: All user-facing text uses lang.get() or comes from data
- ✅ **Ruff Checks**: All pass (F401, E722, etc.)

### Migration from CharacterSheetWindow

**Before Phase 4**:
- 80 lines of class/race population logic in dialogs.py
- Duplicated translation logic
- Event handlers mixed business and UI logic

**After Phase 4**:
- 5 thin wrapper methods in dialogs.py (~40 lines)
- 280 lines of reusable, tested functions in character_validator.py
- Clean separation of concerns
- Reusable for other UI contexts (settings dialog, import dialog, etc.)

---

## Character Banner Module (Phase 7)

### Overview

The Character Banner module (`Functions/character_banner.py`) provides functions for loading and displaying character class banner images with fallback placeholder support.

**Extracted from**: `UI/dialogs.py` CharacterSheetWindow class  
**Date Completed**: December 19, 2025  
**Lines Removed from dialogs.py**: ~54  
**Lines in new module**: ~141  
**Functions Extracted**: 2

### Architecture

#### Core Functions

The module provides 2 main functions for banner management:

```python
banner_load_class_image(parent_window, realm, class_name)
banner_set_placeholder(parent_window, text)
```

#### Function Details

##### banner_load_class_image()

**Signature**:
```python
def banner_load_class_image(parent_window, realm: str, class_name: str) -> None:
    """Load and display character class banner image."""
```

**Purpose**: Load class banner from file system and display in UI with fallback to placeholder

**Parameters**:
- `parent_window`: CharacterSheetWindow instance with banner_label attribute (QLabel)
- `realm`: Realm name ('Albion', 'Hibernia', or 'Midgard')
- `class_name`: Character class name (e.g., 'Armsman', 'Ranger')

**Process**:
1. Validates class_name is provided
2. Maps realm to folder abbreviation (Albion→Alb, Hibernia→Hib, Midgard→Mid)
3. Normalizes class name for filename (lowercase, spaces → underscores)
4. Attempts to load image from Img/Banner/{realm}/{class}.jpg
5. Falls back to .png extension if .jpg not found
6. Loads and displays QPixmap with top-center alignment
7. Calls banner_set_placeholder() if image invalid or missing
8. Logs debug/warning messages for troubleshooting

**Example**:
```python
realm = self.character_data.get('realm', 'Albion')
class_name = self.character_data.get('class', '')
banner_load_class_image(self, realm, class_name)
```

**Error Handling**:
- Empty class name → Shows placeholder with translation key
- Missing image file → Shows placeholder with "Banner not found: {realm}/{class}"
- Corrupted image file → Shows placeholder with "Invalid image: {class}"
- Logs detailed messages for debugging

##### banner_set_placeholder()

**Signature**:
```python
def banner_set_placeholder(parent_window, text: str) -> None:
    """Display placeholder text when banner image is not available."""
```

**Purpose**: Show styled text placeholder when banner image unavailable

**Parameters**:
- `parent_window`: CharacterSheetWindow instance with banner_label attribute (QLabel)
- `text`: Placeholder text to display (supports multi-line with \n)

**Process**:
1. Clears any existing pixmap from label
2. Sets text with centered alignment
3. Applies gray italic styling with scaled 9pt font size

**Styling Applied**:
```css
color: gray;
font-style: italic;
font-size: {scaled_9pt}pt;
```

### Dependencies

**Internal Dependencies**:
- `Functions.language_manager.lang` - For translation keys
- `Functions.path_manager.get_resource_path()` - PyInstaller compatibility
- `Functions.theme_manager.get_scaled_size()` - UI scaling support
- `Functions.logging_manager` - Debug/error logging

**External Dependencies**:
- `PySide6.QtGui.QPixmap` - Image loading
- `PySide6.QtCore.Qt` - Alignment flags
- `os` - File path operations

### Quality Metrics

- ✅ PEP 8 Compliant (ruff: 0 errors)
- ✅ Type Hints: Complete for all parameters and returns
- ✅ Docstrings: Comprehensive with examples and process flows
- ✅ Logging: Debug and warning messages for troubleshooting
- ✅ No Hardcoded Strings: Uses lang.get() for UI text
- ✅ No French Comments: 100% English documentation

### Integration Points

**Where banner_load_class_image() is called**:
- When character realm changes in dropdown
- When character class changes in dropdown
- When character data is updated from external sources

**Where banner_set_placeholder() is called**:
- From banner_load_class_image() when image not found or corrupted
- For manual placeholder display in error states

---

## Character Achievement Formatter Module (Phase 11)

### Overview

The Character Achievement Formatter Module provides functions for formatting and displaying character achievements with a clean, organized 2-column layout.

**File**: `Functions/character_achievement_formatter.py` (256 lines)

**Key Features**:
- ✅ 2-column layout with vertical separator
- ✅ Up to 8 achievements per column
- ✅ Displays title, progress (e.g., "5/10"), and current tier
- ✅ Placeholder for empty achievement lists
- ✅ Consistent styling with theme integration
- ✅ Error handling with graceful fallback

### Functions

#### character_update_achievements_display()

**Purpose**: Update achievements display with the provided list

**Signature**:
```python
def character_update_achievements_display(parent_window, achievements_list) -> None
```

**Parameters**:
- `parent_window`: CharacterSheetWindow instance with:
  - `achievements_container_layout`: QVBoxLayout for container
- `achievements_list`: List of dicts with keys:
  - `'title'`: Achievement name (str)
  - `'progress'`: Progress indicator like "5/10" (str)
  - `'current'`: Current tier or rank, or "None" (str)

**Returns**: None (updates parent_window.achievements_container_layout in-place)

**Behavior**:
1. Clears existing widgets from achievements_container_layout
2. Shows placeholder if no achievements exist
3. Splits achievements into 2 groups of 8 (first 8, rest)
4. Creates first grid layout (left column) with styling
5. Adds vertical separator line if second column exists
6. Creates second grid layout (right column) with styling
7. Adds columns to main layout with stretch factors
8. Adds final stretch to push content up

**Layout Structure**:
```
┌─────────────────────────────────────────────────────┐
│  Title 1        5/10  (Tier)  │  Title 9        2/10  (Tier) │
│  Title 2        3/10  (Tier)  │  Title 10       0/10         │
│  Title 3        8/10  (Tier)  │  Title 11       1/10  (Tier) │
│  ...                         │  ...                         │
└─────────────────────────────────────────────────────┘
```

**Styling Details**:
- Title font: 9pt (scaled), left aligned
- Progress: Bold, 9pt (scaled), right aligned
- Current tier: 8pt (scaled), gray (#6c757d), italic, left aligned
- Separator: Vertical line with light gray color (#cccccc)
- Empty state: Gray italic dash (—)

**Example**:
```python
from Functions.character_achievement_formatter import character_update_achievements_display

achievements = [
    {'title': 'First Victory', 'progress': '1/1', 'current': 'Gold'},
    {'title': 'Realm Rank 5', 'progress': '5/5', 'current': None},
    # ... more achievements
]
character_update_achievements_display(window, achievements)
# Layout is updated with achievements in 2 columns
```

**Integration Points**:
- Called from `CharacterSheetWindow._update_achievements_display()` (thin wrapper)
- Receives data from character_data['achievements']
- Updates `self.achievements_container_layout` directly

**Error Handling**:
- Missing keys handled with `.get()` and defaults
- "None" string tier ignored (treated as empty)
- Empty list shows placeholder
- Exceptions caught and logged, placeholder shown as fallback

**Code Quality**:
- ✅ PEP 8 compliant (ruff: 0 errors)
- ✅ Type hints for all parameters
- ✅ Comprehensive docstrings with examples
- ✅ No hardcoded strings
- ✅ Robust error handling with logging

---

## Character Rename Handler Module (Phase 17)

### Overview

The Character Rename Handler module (`Functions/character_rename_handler.py`) provides functions for handling character renaming operations with validation and JSON persistence.

**Extracted from**: `UI/dialogs.py` CharacterSheetWindow.rename_character() method  
**Date Completed**: December 19, 2025  
**Lines Removed from dialogs.py**: ~41 lines  
**Lines in new module**: ~60 lines  
**Functions Extracted**: 1

### Key Features

- ✅ **Clean separation of concerns** - Rename logic decoupled from UI
- ✅ **Proper error handling** - Graceful failure with detailed messages
- ✅ **Data consistency** - Updates both character_data dict and JSON file
- ✅ **Type hints** - Complete type annotations for all parameters
- ✅ **English documentation** - Comprehensive docstrings with examples
- ✅ **Reusable module** - Can be called from any context

### Core Function

The module provides 1 main function:

```python
character_rename_with_validation(
    character_data: dict,
    new_name: str,
    rename_function,
) -> Tuple[bool, str]
```

**Purpose**: Rename a character with validation and persistence

**Parameters**:
- `character_data`: Dictionary containing character data to update (must contain 'name' key)
- `new_name`: New name for the character (pre-validated by caller)
- `rename_function`: Function to call for JSON file rename (signature: `(old_name, new_name) -> (bool, str)`)

**Returns**: Tuple of (success: bool, message: str)
- On success: `(True, "")`
- On failure: `(False, "Error message")`

**Behavior**:
1. Retrieves old name from character_data['name']
2. Validates that old name exists
3. Calls rename_function(old_name, new_name)
4. On success:
   - Updates character_data['name'] = new_name
   - Updates character_data['id'] = new_name
   - Returns success
5. On failure: Returns error message from rename_function
6. On exception: Catches and returns formatted error message

**Example**:
```python
from Functions.character_rename_handler import character_rename_with_validation
from Functions.character_manager import rename_character

# In CharacterSheetWindow.rename_character() after validation
success, msg = character_rename_with_validation(
    self.character_data,
    "NewCharacterName",
    rename_character
)

if success:
    # Update UI
    self.setWindowTitle(f"Fiche personnage - NewCharacterName")
    self.parent_app.refresh_character_list()
else:
    # Show error
    msg_show_error(self, "titles.error", f"Échec du renommage : {msg}")
    self.name_edit.setText(old_name)
```

### Integration with CharacterSheetWindow

The `rename_character()` method in `CharacterSheetWindow` now acts as a thin wrapper:

```python
def rename_character(self):
    """Renames the character with validation."""
    try:
        old_name = self.character_data.get('name', '')
        
        # Validate new name format (business logic in dialogs.py)
        result = validate_character_rename(self.name_edit.text())
        if not result['valid']:
            msg_show_warning(self, "titles.warning", result['message'])
            self.name_edit.setText(old_name)
            return
        
        new_name = result['value']
        if old_name == new_name:
            msg_show_info_with_details(self, "titles.info", "Le nom n'a pas changé.")
            return
        
        # Show confirmation dialog
        if msg_show_confirmation(self, "Confirmer le renommage", 
                                f"Renommer '{old_name}' en '{new_name}' ?"):
            from Functions.character_manager import rename_character
            from Functions.character_rename_handler import character_rename_with_validation
            
            # Call extracted function
            success, msg = character_rename_with_validation(
                self.character_data, new_name, rename_character
            )
            
            if success:
                # Update UI elements
                self.setWindowTitle(f"Fiche personnage - {new_name}")
                if hasattr(self.parent_app, 'refresh_character_list'):
                    self.parent_app.refresh_character_list()
            else:
                msg_show_error(self, "titles.error", f"Échec du renommage : {msg}")
                self.name_edit.setText(old_name)
                
    except Exception as e:
        msg_show_error(self, "titles.error", f"Erreur lors du renommage : {str(e)}")
        if hasattr(self, 'character_data'):
            self.name_edit.setText(self.character_data.get('name', ''))
```

### Quality Metrics

- ✅ **PEP 8 compliant**: Ruff validation passed (0 errors)
- ✅ **Type hints**: Complete annotations for all parameters
- ✅ **Docstrings**: Comprehensive English documentation with examples
- ✅ **No hardcoded strings**: All error messages use format strings
- ✅ **No French comments**: 100% English documentation
- ✅ **Robust error handling**: All error paths handled
- ✅ **Syntax validation**: Python syntax check passed
- ✅ **Import testing**: Module imports correctly

### Benefits of this Design

- ✅ Rename logic is testable and reusable
- ✅ UI handling stays in dialogs.py (appropriate layer)
- ✅ Error messages can be customized per context
- ✅ Easy to extend for other rename contexts
- ✅ Reduced complexity in CharacterSheetWindow class

---

## Character Schema


### character_schema.py

#### Purpose

Defines the expected structure for character JSON files and provides validation functions.

#### Required Fields

Each character must contain:

```json
{
  "name": "CharacterName",           // Required: String, 2-50 chars
  "realm": "Albion|Hibernia|Midgard", // Required: Valid realm
  "class": "Paladin|Ranger|...",      // Required: Valid class
  "race": "Human|Elf|...",            // Required: Valid race for realm/class combo
  "level": 50,                         // Required: Integer 1-50 or "BL" string
  "gender": "Male|Female",             // Required: Exact match
  "season": "S1|S2|S3|...",           // Required after migration
  // ... other optional fields
}
```

#### Validation Functions

**validate_character_data(character_dict)**
- Validates all required fields
- Checks data types
- Validates realm/class/race combinations
- Raises CharacterValidationError on failure

---

## Migration System

### Overview

The Character Migration System provides **automatic and transparent** migration of character files from the old flat structure to a new season-based hierarchical structure.

**Key Goals**:
- ✅ **Zero user interaction** - Fully automatic migration
- ✅ **Data safety** - Complete backup before migration
- ✅ **Validation** - Strict schema validation
- ✅ **Rollback** - Automatic recovery on any error
- ✅ **One-time execution** - Flag prevents duplicate migrations

### Architecture

```
Functions/
├─ character_schema.py      # Schema definition and validation
├─ character_migration.py   # Migration logic
└─ character_manager.py     # Integration point

Configuration/
└─ config.json              # Migration tracking

Backup/
└─ Characters/
    └─ Characters_migration_backup_*.zip
```

### Migration Workflow

```
Application Start
    │
    ▼
Check: is_migration_done()?
    │
    ├─> Yes: Skip migration
    │
    └─> No: Detect old structure
            │
            ├─> Old files found: Backup → Migrate → Validate
            │
            └─> No old files: Mark as done
```

### Data Structure Changes

**Old Structure**:
```
Characters/
  ├─ Albion/
  │   ├─ Merlin.json
  │   └─ Arthur.json
  ├─ Hibernia/
  │   └─ Cuchulainn.json
  └─ Midgard/
      └─ Thor.json
```

**New Structure**:
```
Characters/
  ├─ S3/
  │   ├─ Albion/
  │   │   ├─ Merlin.json
  │   │   └─ Arthur.json
  │   ├─ Hibernia/
  │   │   └─ Cuchulainn.json
  │   └─ Midgard/
  │       └─ Thor.json
  └─ Backups/
      └─ Characters_migration_backup_*.zip
```

---

## Integration

### How It Works Together

1. **Application Start** → character_manager module loaded
2. **Migration Check** → Automatic one-time migration executed if needed
3. **Character Sheet Open** → Uses character_validator for class/race dropdowns
4. **Character Saved** → Validates using character_schema before persistence

### Configuration

```json
{
  "migrations": {
    "character_structure_done": false  // Set to true after migration
  }
}
```

---

## Character Herald Scrapper Module (Phase 6)

### Overview

The Character Herald Scrapper module (`Functions/character_herald_scrapper.py`) provides functions for scraping character data from Herald and applying scraped statistics to the UI and character data structure. It supports both complete character updates and partial RvR-only updates.

**Extracted from**: `UI/dialogs.py` CharacterSheetWindow class  
**Date**: December 18, 2025 (Phase 6)  
**Lines in new module**: ~422  
**Functions Extracted**: 4

### Architecture

#### Core Functions

The module provides 4 main functions for Herald scraping and data updates:

```python
# Scraping orchestration functions
character_herald_update(parent_window, url)
character_herald_update_rvr_stats(parent_window, url)

# UI update functions
character_herald_apply_scraped_stats(parent_window, result_rvr, result_pvp, result_pve, result_wealth, result_achievements)
character_herald_apply_partial_stats(parent_window, result_rvr, result_pvp, result_pve, result_wealth, result_achievements)
```

#### Data Flow

```
┌─────────────────────────────────────────────────────┐
│       Character Sheet Window (dialogs.py)           │
│    User clicks "Scrape Herald" or "Update RvR"      │
└──────────────────────┬────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  character_herald_scrapper.py    │
        │  character_herald_update() or    │
        │  character_herald_update_rvr()   │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    ┌─────────────┐          ┌──────────────┐
    │ URL Check & │          │ Thread Setup │
    │ Formatting  │          │ (Browser)    │
    └────┬────────┘          └────┬─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
          ┌──────────────────────────┐
          │  HeraldScraperWorker or  │
          │  CharacterUpdateThread   │
          │  (Scrapes from Herald)   │
          └──────────────┬───────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │ Scraped Data Dict with:      │
          │ - result_rvr                 │
          │ - result_pvp                 │
          │ - result_pve                 │
          │ - result_wealth              │
          │ - result_achievements        │
          └──────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
   Complete Update              Partial Update
   character_herald_            character_herald_
   apply_scraped_stats()        apply_partial_stats()
         │                               │
         ▼                               ▼
   UI Labels Updated            Selected Labels Updated
   character_data updated       character_data updated
                                Save triggered
```

### Functions Reference

#### 1. character_herald_update()

**Purpose**: Main entry point for complete character update from Herald

**Signature**:
```python
def character_herald_update(parent_window, url: str) -> None
```

**Parameters**:
- `parent_window`: CharacterSheetWindow instance with UI elements
- `url`: Herald URL to scrape (with or without protocol)

**Returns**: None (operates via signals)

**Process**:
1. Validates Herald URL format
2. Adds https:// if protocol missing
3. Disables Herald buttons during update
4. Launches CharacterUpdateThread
5. Shows ProgressStepsDialog with CHARACTER_UPDATE steps
6. Receives update_finished signal when complete

**Example**:
```python
# Called from CharacterSheetWindow
character_herald_update(self, "daoc.gamerlaunch.com/heroes/merlin")
# Opens browser, scrapes full character data, updates all UI fields
```

#### 2. character_herald_update_rvr_stats()

**Purpose**: Fast update for RvR statistics only

**Signature**:
```python
def character_herald_update_rvr_stats(parent_window, url: str) -> None
```

**Parameters**:
- `parent_window`: CharacterSheetWindow instance
- `url`: Herald URL

**Returns**: None (operates via signals)

**Process**:
1. Validates URL format
2. Launches lighter StatsUpdateThread (not full CharacterUpdateThread)
3. Shows ProgressStepsDialog with STATS_SCRAPING steps
4. Receives stats_updated signal when complete
5. Faster than full character update

**Example**:
```python
# Called when user wants quick RvR refresh
character_herald_update_rvr_stats(self, "daoc.gamerlaunch.com/heroes/merlin")
# Scrapes only tower/keep/relic captures
```

#### 3. character_herald_apply_scraped_stats()

**Purpose**: Apply all scraped statistics to UI and character data

**Signature**:
```python
def character_herald_apply_scraped_stats(
    parent_window,
    result_rvr: dict,
    result_pvp: dict,
    result_pve: dict,
    result_wealth: dict,
    result_achievements: dict
) -> None
```

**Parameters**:
- `parent_window`: CharacterSheetWindow instance
- `result_rvr`: Dict with tower/keep/relic capture counts
- `result_pvp`: Dict with solo_kills, deathblows, kills (by realm)
- `result_pve`: Dict with dragon/legion/mini-dragon kills, epic encounters
- `result_wealth`: Dict with money amount
- `result_achievements`: Dict with achievements list

**Returns**: None (updates UI and character_data)

**Updates**:
- Tower, Keep, Relic captures labels
- PvP stats (Solo Kills, Deathblows, Kills) with per-realm breakdown
- PvE stats (Dragon, Legion, Mini-Dragon kills, Epic encounters/dungeons, Sobekite)
- Money label
- Achievements display (if provided)

**Example**:
```python
# Called after successful full character scrape
character_herald_apply_scraped_stats(
    self,
    result_rvr={'tower_captures': 42, 'keep_captures': 10, 'relic_captures': 2},
    result_pvp={'solo_kills': 156, 'deathblows': 89, 'kills': 245, ...},
    result_pve={'dragon_kills': 12, 'legion_kills': 5, ...},
    result_wealth={'money': 1500000},
    result_achievements={'success': True, 'achievements': [...]}
)
# All UI labels updated with formatted numbers
```

#### 4. character_herald_apply_partial_stats()

**Purpose**: Apply selective statistics to UI and character data

**Signature**:
```python
def character_herald_apply_partial_stats(
    parent_window,
    result_rvr: dict,
    result_pvp: dict,
    result_pve: dict,
    result_wealth: dict,
    result_achievements: dict
) -> None
```

**Parameters**: Same as apply_scraped_stats()

**Returns**: None (updates UI and character_data, saves when needed)

**Behavior**:
- Only updates fields if result_*['success'] is True
- Saves character data after each successful update
- Calls save_character() immediately after updating each stat type
- Supports selective updates (only update what was successfully scraped)

**Example**:
```python
# Called after RvR-only scrape
character_herald_apply_partial_stats(
    self,
    result_rvr={'success': True, 'tower_captures': 42, ...},
    result_pvp={},  # Empty, skip PvP
    result_pve={},  # Empty, skip PvE
    result_wealth={},  # Empty, skip wealth
    result_achievements={}  # Empty, skip achievements
)
# Only RvR labels updated, character saved
```

### Data Structures

#### RvR Result Dictionary
```python
result_rvr = {
    'success': True,
    'tower_captures': 42,
    'keep_captures': 10,
    'relic_captures': 2
}
```

#### PvP Result Dictionary
```python
result_pvp = {
    'success': True,
    'solo_kills': 156,
    'solo_kills_alb': 52,
    'solo_kills_hib': 48,
    'solo_kills_mid': 56,
    'deathblows': 89,
    'deathblows_alb': 30,
    'deathblows_hib': 28,
    'deathblows_mid': 31,
    'kills': 245,
    'kills_alb': 82,
    'kills_hib': 81,
    'kills_mid': 82
}
```

#### PvE Result Dictionary
```python
result_pve = {
    'success': True,
    'dragon_kills': 12,
    'legion_kills': 5,
    'mini_dragon_kills': 28,
    'epic_encounters': 7,
    'epic_dungeons': 3,
    'sobekite': 145
}
```

#### Wealth Result Dictionary
```python
result_wealth = {
    'success': True,
    'money': 1500000
}
```

#### Achievements Result Dictionary
```python
result_achievements = {
    'success': True,
    'achievements': [
        'First Kill',
        'Leveled up',
        ...
    ]
}
```

### Quality Metrics

- ✅ PEP 8 compliant
- ✅ Type hints complete (for parameters and process flow)
- ✅ Docstrings comprehensive with examples
- ✅ Error handling robust (URL validation, thread safety)
- ✅ No hardcoded strings (all use lang.get())
- ✅ No French comments (100% English)
- ✅ Syntax validation: ✅ PASSED

---

## Error Handling

### Character Validator

- ✅ Graceful fallback on missing translations
- ✅ Proper exception catching and logging
- ✅ Returns sensible defaults (empty lists, empty strings)

### Character Schema

- ✅ Detailed validation error messages
- ✅ Custom CharacterValidationError exceptions
- ✅ Logs all validation failures

### Character Migration

- ✅ Complete backup before any changes
- ✅ Automatic rollback on validation failure
- ✅ Detailed migration logging
- ✅ Cleanup on success

---

## Implementation Progress

### Phase 4: Character Validator Extraction (Completed - Dec 18, 2025)

**Status**: ✅ COMPLETED

**What Was Done**:
1. ✅ Created `Functions/character_validator.py` (280 lines)
2. ✅ Extracted 5 functions from CharacterSheetWindow
3. ✅ Updated dialogs.py with thin wrapper methods
4. ✅ Implemented multi-language support
5. ✅ Added comprehensive error handling
6. ✅ Ruff validation: All checks passed
7. ✅ Syntax validation: All checks passed

**Functions Extracted**:
- `character_get_classes_for_realm()` - Data retrieval
- `character_get_races_for_class()` - Data retrieval with filtering
- `character_populate_classes_combo()` - UI population
- `character_populate_races_combo()` - UI population with filtering
- `character_handle_realm_change()` - Event handler with cascade updates
- `character_handle_class_change()` - Event handler with filtering
- `character_handle_race_change()` - Event handler

**Code Removed from dialogs.py**: ~80 lines  
**Code Added to character_validator.py**: ~280 lines  
**Net Impact**: Better separation of concerns, reusable module

**Quality Metrics**:
- ✅ PEP 8 compliant
- ✅ Type hints complete
- ✅ Docstrings comprehensive
- ✅ Error handling robust
- ✅ Ruff checks: 0 errors (ignoring E501)
- ✅ Syntax validation: ✅ PASSED

### Phase 5: Character RR Calculator Extraction (Completed - Dec 18, 2025)

**Status**: ✅ COMPLETED

**What Was Done**:
1. ✅ Created `Functions/character_rr_calculator.py` (209 lines)
2. ✅ Extracted 3 functions from CharacterSheetWindow
3. ✅ Updated dialogs.py with thin wrapper methods
4. ✅ Implemented realm rank calculations
5. ✅ Added level filtering based on rank restrictions
6. ✅ Added progression information calculation
7. ✅ Ruff validation: All checks passed
8. ✅ Syntax validation: All checks passed

**Functions Extracted**:
- `character_rr_get_valid_levels()` - Get valid level range for rank
- `character_rr_calculate_points_info()` - Get progression to next level
- `character_rr_calculate_from_points()` - Calculate rank from realm points

**Code Removed from dialogs.py**: ~50 lines  
**Code Added to character_rr_calculator.py**: ~209 lines  
**Net Impact**: Realm rank calculations isolated and reusable

**Quality Metrics**:
- ✅ PEP 8 compliant
- ✅ Type hints complete
- ✅ Docstrings comprehensive
- ✅ Error handling robust
- ✅ Ruff checks: 0 errors (ignoring E501)
- ✅ Syntax validation: ✅ PASSED

### Phase 6: Character Herald Scrapper Extraction (Completed - Dec 18, 2025)

**Status**: ✅ COMPLETED

**What Was Done**:
1. ✅ Created `Functions/character_herald_scrapper.py` (422 lines)
2. ✅ Extracted 4 functions from CharacterSheetWindow
3. ✅ Updated dialogs.py with imports for new module
4. ✅ Implemented Herald URL validation and scraping orchestration
5. ✅ Implemented complete and partial stats UI updates
6. ✅ Added comprehensive docstrings with examples
7. ✅ Syntax validation: All checks passed

**Functions Extracted**:
- `character_herald_update()` - Main entry point for complete character update
- `character_herald_update_rvr_stats()` - Fast RvR-only update
- `character_herald_apply_scraped_stats()` - Apply all scraped stats to UI
- `character_herald_apply_partial_stats()` - Apply selective stats to UI

**Code Structure**:
- `character_herald_scrapper.py`: ~422 lines (new module)
- dialogs.py: Updated with imports and thin wrappers

**Quality Metrics**:
- ✅ PEP 8 compliant
- ✅ Type hints present (for parameters)
- ✅ Docstrings comprehensive with examples
- ✅ Error handling robust (URL validation, thread-safe)
- ✅ No hardcoded strings (uses lang.get())
- ✅ No French comments (100% English)
- ✅ Syntax validation: ✅ PASSED

### Phase 7: Character Banner Management Extraction (Completed - Dec 19, 2025)

**Status**: ✅ COMPLETED

**What Was Done**:
1. ✅ Created `Functions/character_banner.py` (141 lines)
2. ✅ Extracted 2 functions from CharacterSheetWindow
3. ✅ Updated dialogs.py with imports and thin wrapper methods
4. ✅ Implemented banner image loading with .jpg/.png fallback
5. ✅ Implemented placeholder display with scaled font support
6. ✅ Added comprehensive docstrings with examples
7. ✅ Ruff validation: All checks passed
8. ✅ Syntax validation: All checks passed

**Functions Extracted**:
- `banner_load_class_image()` - Load and display class banner with error handling
- `banner_set_placeholder()` - Display styled placeholder text when banner unavailable

**Code Removed from dialogs.py**: ~54 lines  
**Code Added to character_banner.py**: ~141 lines  
**Net Impact**: Better separation of concerns, reusable module

**Quality Metrics**:
- ✅ PEP 8 compliant (ruff: 0 errors)
- ✅ Type hints complete
- ✅ Docstrings comprehensive with examples
- ✅ Error handling robust (file validation, logging)
- ✅ No hardcoded strings (uses lang.get())
- ✅ Ruff checks: 0 errors
- ✅ Syntax validation: ✅ PASSED

---

## Commit Information

**Branch**: `refactor/v0.109-dialogs-cleanup`  
**Related Phases**:
- Phase 1: Template Parser extraction ✅
- Phase 2: Item Price Manager extraction ✅
- Phase 3: Ruff cleanup ✅
- Phase 4: Character Validator extraction ✅
- Phase 5: Character RR Calculator extraction ✅
- Phase 6: Character Herald Scrapper extraction ✅
- Phase 7: Character Banner Management extraction ✅
- Phase 17: Character Rename Handler extraction ✅

---

**Documentation Last Updated**: December 19, 2025  
**Next Phase**: Simple UI Utility Functions extraction (Phase 18)
