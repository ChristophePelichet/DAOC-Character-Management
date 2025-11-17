# Configuration v2 - Technical Documentation
**Version:** v0.108  
**Date:** November 16, 2025  
**Author:** Christophe Pelichet

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration Structure](#configuration-structure)
4. [Migration System](#migration-system)
5. [ConfigManager API](#configmanager-api)
6. [Backward Compatibility](#backward-compatibility)
7. [Validation](#validation)
8. [Usage Guide](#usage-guide)
9. [Maintenance](#maintenance)

---

## Overview

### Objectives

Configuration v2 introduces a **hierarchical structure** to improve:

- ✅ **Organization**: Logical grouping by categories (ui, folders, backup, system, game)
- ✅ **Readability**: Clear and self-documented JSON structure
- ✅ **Maintainability**: Easier to add new options
- ✅ **Extensibility**: Native support for subsections (e.g., backup.characters, backup.cookies)
- ✅ **Security**: Automatic migration with backup and validation

### Major Changes

| Aspect | v1 (Old) | v2 (New) |
|--------|----------|----------|
| **Structure** | Flat (37 keys at root) | Hierarchical (6 sections) |
| **Access** | `config.get("language")` | `config.get("ui.language")` |
| **Organization** | None | Logical by domain |
| **Validation** | Manual | Automatic with schema |
| **Migration** | Manual | Automatic with backup |
| **Backup settings** | 1 single section | 3 subsections (characters/cookies/armor) |
| **Migration tracking** | None | Stored in migrations section |
| **Compatibility** | N/A | 100% backward compatible with v1 |

---

## Architecture

### Components

```
Functions/
├── config_schema.py       # v2 structure definition
├── config_migration.py    # v1→v2 migration logic
└── config_manager.py      # Main manager (modified)

Configuration/
└── config.json            # Configuration file
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Application starts                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│            ConfigManager.load_config()                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│         detect_config_version(config_data)                   │
│         • v1 detected if no "ui", "folders" sections         │
│         • v2 detected if sections present                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
         ┌────────────────┐    ┌────────────────┐
         │   Version v1   │    │   Version v2   │
         └────────┬───────┘    └────────┬───────┘
                  │                     │
                  ▼                     │
    ┌─────────────────────────┐        │
    │ create_backup()          │        │
    │ → config.json.backup_... │        │
    └────────┬────────────────┘        │
             │                          │
             ▼                          │
    ┌─────────────────────────┐        │
    │ migrate_v1_to_v2()       │        │
    │ • Transform structure    │        │
    │ • Map 39 legacy keys     │        │
    └────────┬────────────────┘        │
             │                          │
             ▼                          │
    ┌─────────────────────────┐        │
    │ validate_migrated_config()│       │
    │ • Check sections         │        │
    │ • Verify keys            │        │
    └────────┬────────────────┘        │
             │                          │
             ▼                          │
    ┌─────────────────────────┐        │
    │ save_config()            │        │
    │ → Write v2 to disk       │        │
    └────────┬────────────────┘        │
             │                          │
             └──────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Config v2 loaded in RAM    │
         │   Application can start      │
         └──────────────────────────────┘
```

---

## Configuration Structure

### config_schema.py

#### DEFAULT_CONFIG

Complete v2 configuration structure:

```python
DEFAULT_CONFIG = {
    "ui": {
        "language": "en",                    # Interface language
        "theme": "purple",                   # Visual theme
        "font_scale": 1.0,                   # Font scale
        "column_widths": {},                 # Column widths
        "column_visibility": {},             # Column visibility
        "tree_view_header_state": None,      # TreeView header state
        "manual_column_resize": True         # Manual resize
    },
    "folders": {
        "characters": None,                  # Characters folder
        "logs": None,                        # Logs folder
        "armor": None,                       # Armor folder
        "cookies": None                      # Cookies folder
    },
    "backup": {
        "characters": {
            "auto_daily_backup": True,       # Daily auto backup
            "path": None,                    # Backup path
            "compress": True,                # ZIP compression
            "size_limit_mb": 10,             # Size limit (MB)
            "auto_delete_old": True,         # Delete old backups
            "last_date": None                # Last backup date
        },
        "cookies": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        },
        "armor": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        }
    },
    "system": {
        "debug_mode": False,                 # Debug mode
        "show_debug_window": False,          # Debug window
        "disable_disclaimer": False,         # Disable disclaimer
        "preferred_browser": "Chrome",       # Preferred browser
        "allow_browser_download": False,     # Allow download
        "debug": {
            "save_herald_html": False,       # Save Herald HTML debug file
            "save_test_connection_html": False  # Save connection test HTML debug file
        }
    },
    "game": {
        "servers": ["Eden"],                 # Game servers
        "default_server": "Eden",            # Default server
        "seasons": ["S3"],                   # Available seasons
        "default_season": "S3",              # Default season
        "default_realm": None                # Default realm
    },
    "migrations": {
        "character_structure_done": False,  # Character migration completed
        "character_structure_date": None    # Character migration date (ISO)
    }
}
```

#### VALIDATION_SCHEMA

Validation rules for each key:

```python
VALIDATION_SCHEMA = {
    "ui": {
        "language": {
            "type": str,
            "allowed": ["fr", "en", "de"],
            "default": "en"
        },
        "theme": {
            "type": str,
            "allowed": ["default", "dark", "light", "purple"],
            "default": "purple"
        },
        "font_scale": {
            "type": (int, float),
            "min": 0.5,
            "max": 2.0,
            "default": 1.0
        },
        # ... other UI rules
    },
    # ... other sections
}
```

**Supported validation types:**

- `type`: Expected type(s) - e.g., `str`, `bool`, `int`, `(str, type(None))`
- `allowed`: List of allowed values
- `min` / `max`: Min/max values for numbers
- `default`: Default value

#### LEGACY_KEY_MAPPING

Complete v1 → v2 mapping (39 keys):

```python
LEGACY_KEY_MAPPING = {
    # UI keys
    "language": "ui.language",
    "theme": "ui.theme",
    "font_scale": "ui.font_scale",
    "column_widths": "ui.column_widths",
    "column_visibility": "ui.column_visibility",
    "tree_view_header_state": "ui.tree_view_header_state",
    "manual_column_resize": "ui.manual_column_resize",
    
    # Folders keys
    "character_folder": "folders.characters",
    "log_folder": "folders.logs",
    "armor_folder": "folders.armor",
    "cookies_folder": "folders.cookies",
    
    # Backup - Characters
    "backup_enabled": "backup.characters.auto_daily_backup",
    "backup_path": "backup.characters.path",
    "backup_compress": "backup.characters.compress",
    "backup_size_limit_mb": "backup.characters.size_limit_mb",
    "backup_auto_delete_old": "backup.characters.auto_delete_old",
    "backup_last_date": "backup.characters.last_date",
    
    # Backup - Cookies
    "cookies_backup_enabled": "backup.cookies.auto_daily_backup",
    "cookies_backup_path": "backup.cookies.path",
    "cookies_backup_compress": "backup.cookies.compress",
    "cookies_backup_size_limit_mb": "backup.cookies.size_limit_mb",
    "cookies_backup_auto_delete_old": "backup.cookies.auto_delete_old",
    "cookies_backup_last_date": "backup.cookies.last_date",
    
    # Backup - Armor
    "armor_backup_enabled": "backup.armor.auto_daily_backup",
    "armor_backup_path": "backup.armor.path",
    "armor_backup_compress": "backup.armor.compress",
    "armor_backup_size_limit_mb": "backup.armor.size_limit_mb",
    "armor_backup_auto_delete_old": "backup.armor.auto_delete_old",
    "armor_backup_last_date": "backup.armor.last_date",
    
    # System keys
    "debug_mode": "system.debug_mode",
    "show_debug_window": "system.show_debug_window",
    "disable_disclaimer": "system.disable_disclaimer",
    "preferred_browser": "system.preferred_browser",
    "allow_browser_download": "system.allow_browser_download",
    
    # System Debug keys
    "save_herald_html": "system.debug.save_herald_html",
    "save_test_connection_html": "system.debug.save_test_connection_html",
    
    # Game keys
    "servers": "game.servers",
    "default_server": "game.default_server",
    "seasons": "game.seasons",
    "default_season": "game.default_season",
    "default_realm": "game.default_realm"
}
```

---

## Migration System

### config_migration.py

#### Version Detection

```python
def detect_config_version(config: Dict[str, Any]) -> str:
    """
    Detects configuration version (v1 or v2).
    
    Logic:
    - v2 detected if "ui", "folders", "backup" sections present
    - v1 detected otherwise (flat structure)
    
    Returns:
        "v1" or "v2"
    """
```

#### v1 → v2 Migration

```python
def migrate_v1_to_v2(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrates v1 configuration to v2.
    
    Process:
    1. Create empty v2 structure (copy of DEFAULT_CONFIG)
    2. For each v1 key in old_config:
       a. Look for mapping in LEGACY_KEY_MAPPING
       b. If found: copy value to v2 structure
       c. If not found: log warning + preserve in "unknown" section
    3. Return new structure
    
    Safety:
    - No data lost (unknown keys preserved)
    - Default values applied if missing
    - Detailed logging of each migration
    """
```

#### Backup Creation

```python
def create_backup(config_file: str) -> bool:
    """
    Creates backup before migration.
    
    Format: config.json.backup_YYYYMMDD_HHMMSS
    Example: config.json.backup_20251116_143052
    
    Returns:
        True if success, False otherwise
    """
```

#### Post-Migration Validation

```python
def validate_migrated_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates migrated structure.
    
    Checks:
    - All required sections present (ui, folders, backup, system, game)
    - Backup subsections present (characters, cookies, armor)
    - Critical keys present in each section
    
    Returns:
        (is_valid: bool, errors: List[str])
    """
```

#### Migration Summary

```python
def get_migration_summary(old_config, new_config) -> str:
    """
    Generates detailed migration report.
    
    Contains:
    - Number of migrated keys
    - List of transformations
    - Unknown keys (if any)
    - Final structure
    
    Used for logging and debugging
    """
```

---

## ConfigManager API

### Main Methods

#### load_config()

```python
def load_config(self):
    """
    Loads configuration with automatic migration.
    
    Workflow:
    1. Load config.json
    2. Detect version (v1/v2)
    3. If v1:
       a. Create backup
       b. Migrate to v2
       c. Validate
       d. Save
       e. Log summary
    4. If v2:
       a. Load directly
    5. Return config
    """
```

#### get() - Dotted Notation

```python
def get(self, key: str, default=None) -> Any:
    """
    Retrieves value with dotted notation support.
    
    Examples:
        config.get("ui.language")              # v2 (recommended)
        config.get("language")                 # v1 (legacy, redirected)
        config.get("backup.characters.enabled")
        config.get("nonexistent", "fallback")
    
    Logic:
    1. If "." in key → hierarchical navigation
    2. Else, if key in LEGACY_KEY_MAPPING → redirect to v2 key
    3. Else → search at root (backward compat)
    4. If not found → return default
    """
```

#### set() - Dotted Notation with Validation

```python
def set(self, key: str, value: Any, save=True, validate=False):
    """
    Sets value with dotted notation support.
    
    Parameters:
        key: v2 or v1 key (e.g., "ui.theme" or "theme")
        value: New value
        save: Save immediately to disk
        validate: Validate value before setting
    
    Examples:
        config.set("ui.theme", "purple")
        config.set("theme", "dark")  # Legacy, redirected to ui.theme
        config.set("ui.font_scale", 1.5, validate=True)
    
    Validation (if validate=True):
    - Type checked against VALIDATION_SCHEMA
    - Allowed values verified
    - Min/max verified for numbers
    - Rejected if invalid
    """
```

#### get_section()

```python
def get_section(self, section: str) -> Dict[str, Any]:
    """
    Retrieves complete section.
    
    Examples:
        config.get_section("ui")       # All ui.*
        config.get_section("backup")   # All backup.*
    
    Returns dictionary with all keys in section.
    """
```

---

## Backward Compatibility

### 100% Guarantee

**All old v1 keys continue to work** thanks to LEGACY_KEY_MAPPING.

### Compatibility Examples

```python
# ✅ BEFORE (v1) - Still works
language = config.get("language")
config.set("backup_enabled", True)
theme = config.get("theme", "default")

# ✅ AFTER (v2) - New recommended methods
language = config.get("ui.language")
config.set("backup.characters.auto_daily_backup", True)
theme = config.get("ui.theme", "purple")

# ✅ Both work simultaneously!
```

### Automatic Redirection

When code uses a v1 key:

1. ConfigManager detects legacy key
2. Looks up in LEGACY_KEY_MAPPING
3. Automatically redirects to v2 key
4. Returns value

**Total transparency**: legacy code doesn't need immediate modification.

### Refactored Code

Although backward compatibility is guaranteed, **all code has been refactored** to use v2 notation:

| File | Refactored Occurrences |
|------|------------------------|
| main.py | 53 |
| UI/settings_dialog.py | 46 |
| UI/dialogs.py | 18 |
| Functions/backup_manager.py | 6 |
| Functions/tree_manager.py | Multiple |
| Functions/ui_manager.py | Multiple |
| Functions/logging_manager.py | Multiple |
| Functions/migration_manager.py | Multiple |
| Functions/language_manager.py | Multiple |
| Functions/eden_scraper.py | Multiple |
| Functions/cookie_manager.py | Multiple |

---

## Validation

### validate_value() Function

```python
def validate_value(key_path: str, value: Any) -> bool:
    """
    Validates value against schema.
    
    Checks:
    1. Type (str, int, bool, tuple of types, etc.)
    2. Allowed values (if "allowed" list defined)
    3. Min/Max (for numbers)
    
    Examples:
        validate_value("ui.language", "fr")    # True
        validate_value("ui.language", "es")    # False (not in allowed)
        validate_value("ui.font_scale", 1.5)   # True
        validate_value("ui.font_scale", 3.0)   # False (max=2.0)
    """
```

### Usage in Code

```python
# Explicit validation
if config.validate_value("ui.theme", new_theme):
    config.set("ui.theme", new_theme)
else:
    print("Invalid theme!")

# Automatic validation with set()
config.set("ui.theme", new_theme, validate=True)  # Rejected if invalid
```

---

## Usage Guide

### For Developers

#### Reading Configuration

```python
from Functions.config_manager import ConfigManager

config = ConfigManager()

# Read simple value
language = config.get("ui.language", "en")

# Read complete section
ui_settings = config.get_section("ui")

# Read with deep navigation
backup_path = config.get("backup.characters.path")

# Check migration status
migration_done = config.get("migrations.character_structure_done", False)
```

#### Writing Configuration

```python
# Write value (auto save)
config.set("ui.theme", "purple")

# Write without immediate save
config.set("ui.font_scale", 1.2, save=False)
# ... other modifications ...
config.save_config()  # Batch save

# Write with validation
config.set("ui.theme", "invalid", validate=True)  # Rejected
```

#### Adding New Options

1. **Add to DEFAULT_CONFIG** (config_schema.py):
```python
"system": {
    # ... existing ...
    "new_option": "default_value",
}
```

2. **Add validation to VALIDATION_SCHEMA**:
```python
"system": {
    # ... existing ...
    "new_option": {
        "type": str,
        "allowed": ["value1", "value2"],
        "default": "value1"
    }
}
```

3. **If backward compatibility needed, add to LEGACY_KEY_MAPPING**:
```python
"old_option_name": "system.new_option"
```

4. **Use in code**:
```python
value = config.get("system.new_option")
```

### For Users

#### Automatic Migration

On first use of v0.108:

1. **Automatic backup**: `config.json.backup_20251116_143052`
2. **Migration**: v1 structure → v2
3. **Validation**: Integrity check
4. **Save**: New structure written
5. **Detailed log**: Migration report in console

**No action required** - everything is automatic!

#### config.json File Structure

Before (v1):
```json
{
    "language": "fr",
    "theme": "dark",
    "character_folder": "D:/Characters",
    "backup_enabled": true,
    "debug_mode": false
}
```

After (v2):
```json
{
    "ui": {
        "language": "en",
        "theme": "purple"
    },
    "folders": {
        "characters": "D:/Characters"
    },
    "backup": {
        "characters": {
            "auto_daily_backup": true
        }
    },
    "system": {
        "debug_mode": false
    },
    "migrations": {
        "character_structure_done": false,
        "character_structure_date": null
    }
}
```

---

## Maintenance

### Migration Logs

During migration, following information is logged:

```
[CONFIG MIGRATION] Starting migration from v1 to v2...
[CONFIG MIGRATION] Migrated: language → ui.language = fr
[CONFIG MIGRATION] Migrated: theme → ui.theme = dark
[CONFIG MIGRATION] Migrated: character_folder → folders.characters = D:/Characters
[CONFIG MIGRATION] Migrated: backup_enabled → backup.characters.auto_daily_backup = True
...
[CONFIG MIGRATION] Migration complete: 37 keys migrated
```

### Backup Files

Format: `config.json.backup_YYYYMMDD_HHMMSS`

**Recommended retention**: Keep at least 1 backup in case of issues.

**Manual restoration**:
```powershell
# Backup current version
Copy-Item config.json config.json.current

# Restore from backup
Copy-Item config.json.backup_20251116_143052 config.json
```

### Debugging

#### Check Version

```python
from Functions.config_migration import detect_config_version
import json

with open("Configuration/config.json") as f:
    data = json.load(f)
    version = detect_config_version(data)
    print(f"Version: {version}")
```

#### Validate Configuration

```python
from Functions.config_migration import validate_migrated_config
import json

with open("Configuration/config.json") as f:
    data = json.load(f)
    is_valid, errors = validate_migrated_config(data)
    
    if is_valid:
        print("✅ Valid configuration")
    else:
        print("❌ Errors detected:")
        for error in errors:
            print(f"  - {error}")
```

#### Force Migration

```python
from Functions.config_manager import ConfigManager
from Functions.config_migration import migrate_v1_to_v2, create_backup
import json

# Load current config
with open("Configuration/config.json") as f:
    old_config = json.load(f)

# Create backup
create_backup("Configuration/config.json")

# Migrate
new_config = migrate_v1_to_v2(old_config)

# Save
config = ConfigManager()
config.config = new_config
config.save_config()

print("Forced migration completed")
```

### Common Issues

#### 1. Config Stays in v1

**Symptom**: Migration doesn't trigger.

**Solution**:
- Verify `detect_config_version()` returns "v1"
- Check write permissions on config.json
- Check logs for errors

#### 2. Values Lost After Migration

**Symptom**: Some values are None after migration.

**Solution**:
- Check backup file (`config.json.backup_*`)
- Compare with LEGACY_KEY_MAPPING (key might be missing)
- Add mapping if needed and re-migrate

#### 3. Theme Doesn't Apply

**Symptom**: Default theme doesn't work.

**Cause**: Theme file doesn't exist (e.g., "dracula.json" doesn't exist).

**Solution**:
- Check available themes in `Themes/`
- Use existing theme: "default", "dark", "light", "purple"
- Update DEFAULT_CONFIG with valid theme

---

## Summary of v0.108 Changes

### Nomenclature

| Change | Before | After | Reason |
|--------|--------|-------|--------|
| **backup enabled** | `enabled` | `auto_daily_backup` | More explicit |
| **backup last_date** | Characters only | characters, cookies, armor | Consistency |
| **Default theme** | "default" | "purple" | User choice |
| **Default language** | "fr" | "en" | Internationalization |
| **auto_delete_old** | `False` | `True` | Automatic management |
| **size_limit_mb** | 5 MB (cookies/armor) | 10 MB | More space |

### Modified Files

**New files:**
- `Functions/config_schema.py` (318 lines)
- `Functions/config_migration.py` (186 lines)

**New section in config.json:**
- `migrations`: Tracks automatic migrations (character structure, etc.)
  - Replaces separate `.migration_done` files
  - Centralized migration tracking

**Modified files:**
- `Functions/config_manager.py` (migration integration)
- `main.py` (53 refactored occurrences)
- `UI/settings_dialog.py` (46 occurrences)
- `UI/dialogs.py` (18 occurrences)
- `Functions/backup_manager.py` (6 occurrences)
- 8 other Functions/ files (multiple occurrences each)

**Total:** ~2800 lines added, 11 files modified, 100% backward compatible

---

## Appendices

### Complete v1 → v2 Mapping

| # | v1 Key | v2 Key | Category |
|---|--------|--------|----------|
| 1 | `language` | `ui.language` | UI |
| 2 | `theme` | `ui.theme` | UI |
| 3 | `font_scale` | `ui.font_scale` | UI |
| 4 | `column_widths` | `ui.column_widths` | UI |
| 5 | `column_visibility` | `ui.column_visibility` | UI |
| 6 | `tree_view_header_state` | `ui.tree_view_header_state` | UI |
| 7 | `manual_column_resize` | `ui.manual_column_resize` | UI |
| 8 | `character_folder` | `folders.characters` | Folders |
| 9 | `log_folder` | `folders.logs` | Folders |
| 10 | `armor_folder` | `folders.armor` | Folders |
| 11 | `cookies_folder` | `folders.cookies` | Folders |
| 12 | `backup_enabled` | `backup.characters.auto_daily_backup` | Backup |
| 13 | `backup_path` | `backup.characters.path` | Backup |
| 14 | `backup_compress` | `backup.characters.compress` | Backup |
| 15 | `backup_size_limit_mb` | `backup.characters.size_limit_mb` | Backup |
| 16 | `backup_auto_delete_old` | `backup.characters.auto_delete_old` | Backup |
| 17 | `backup_last_date` | `backup.characters.last_date` | Backup |
| 18 | `cookies_backup_enabled` | `backup.cookies.auto_daily_backup` | Backup |
| 19 | `cookies_backup_path` | `backup.cookies.path` | Backup |
| 20 | `cookies_backup_compress` | `backup.cookies.compress` | Backup |
| 21 | `cookies_backup_size_limit_mb` | `backup.cookies.size_limit_mb` | Backup |
| 22 | `cookies_backup_auto_delete_old` | `backup.cookies.auto_delete_old` | Backup |
| 23 | `cookies_backup_last_date` | `backup.cookies.last_date` | Backup |
| 24 | `armor_backup_enabled` | `backup.armor.auto_daily_backup` | Backup |
| 25 | `armor_backup_path` | `backup.armor.path` | Backup |
| 26 | `armor_backup_compress` | `backup.armor.compress` | Backup |
| 27 | `armor_backup_size_limit_mb` | `backup.armor.size_limit_mb` | Backup |
| 28 | `armor_backup_auto_delete_old` | `backup.armor.auto_delete_old` | Backup |
| 29 | `armor_backup_last_date` | `backup.armor.last_date` | Backup |
| 30 | `debug_mode` | `system.debug_mode` | System |
| 31 | `show_debug_window` | `system.show_debug_window` | System |
| 32 | `disable_disclaimer` | `system.disable_disclaimer` | System |
| 33 | `preferred_browser` | `system.preferred_browser` | System |
| 34 | `allow_browser_download` | `system.allow_browser_download` | System |
| 35 | `save_herald_html` | `system.debug.save_herald_html` | System |
| 36 | `save_test_connection_html` | `system.debug.save_test_connection_html` | System |
| 37 | `servers` | `game.servers` | Game |
| 38 | `default_server` | `game.default_server` | Game |
| 39 | `seasons` | `game.seasons` | Game |
| 40 | `default_season` | `game.default_season` | Game |
| 41 | `default_realm` | `game.default_realm` | Game |

### Available Themes

| ID | Name | File | Description |
|----|------|------|-------------|
| `default` | Light | `default.json` | Light system theme |
| `dark` | Dark | `dark.json` | Dark theme |
| `light` | Light | `default.json` | Alias of default |
| `purple` | Purple | `purple.json` | **Purple theme (default v0.108)** |

---

**End of Technical Documentation**
