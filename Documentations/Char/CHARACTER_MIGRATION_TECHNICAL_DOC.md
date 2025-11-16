# Character Migration System - Technical Documentation
**Version:** v0.108  
**Date:** November 16, 2025  
**Author:** Christophe Pelichet

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Character Schema](#character-schema)
4. [Migration System](#migration-system)
5. [Integration](#integration)
6. [Migration Tracking](#migration-tracking)
7. [Error Handling & Rollback](#error-handling--rollback)
8. [Usage Guide](#usage-guide)
9. [Maintenance](#maintenance)

---

## Overview

### Objectives

The Character Migration System provides **automatic and transparent** migration of character files from the old flat structure to a new season-based hierarchical structure.

**Key Goals:**
- ✅ **Zero user interaction** - Fully automatic migration
- ✅ **Data safety** - Complete backup before migration
- ✅ **Validation** - Strict schema validation for all character data
- ✅ **Rollback** - Automatic recovery on any error
- ✅ **One-time execution** - Flag prevents duplicate migrations
- ✅ **Centralized tracking** - Migration status stored in `config.json`

### Major Changes

| Aspect | Old Structure | New Structure |
|--------|---------------|---------------|
| **Directory Layout** | `Characters/Realm/` | `Characters/Season/Realm/` |
| **Season Field** | Optional | Required (auto-added if missing) |
| **Validation** | None | Comprehensive schema validation |
| **Migration Tracking** | N/A | Stored in `config.json` (`migrations` section) |
| **Backup** | Manual | Automatic ZIP with timestamp |
| **Rollback** | Manual | Automatic on any error |

### Structure Comparison

**Old Structure (Pre-Migration):**
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

**New Structure (Post-Migration):**
```
Characters/
  ├─ S3/  (Current season)
  │   ├─ Albion/
  │   │   ├─ Merlin.json
  │   │   └─ Arthur.json
  │   ├─ Hibernia/
  │   │   └─ Cuchulainn.json
  │   └─ Midgard/
  │       └─ Thor.json
  └─ S1/  (Previous seasons - if any)
      └─ ...

Configuration/
  └─ config.json  (contains migrations.character_structure_done = true)
```

---

## Architecture

### Components

```
Functions/
├─ character_schema.py      # Schema definition and validation
├─ character_migration.py   # Migration logic and orchestration
└─ character_manager.py     # Integration point (auto-execution)

Configuration/
└─ config.json              # Migration tracking (migrations section)

Backup/
└─ Characters/
    └─ Characters_migration_backup_YYYYMMDD_HHMMSS.zip
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│           Application starts (main.py)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│    character_manager module loaded                           │
│    → _run_character_migration() executed                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│         Check: is_migration_done()?                          │
│         (reads config.json migrations section)               │
└────────────────────────────┬────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
         ┌────────────────┐    ┌────────────────┐
         │   Already Done │    │ Not Done Yet   │
         └────────┬───────┘    └────────┬───────┘
                  │                     │
                  ▼                     ▼
         ┌────────────────┐    ┌────────────────────────┐
         │ Log: Skip      │    │ detect_old_structure() │
         │ Return         │    └────────┬───────────────┘
         └────────────────┘             │
                                        ▼
                          ┌─────────────────────────────┐
                          │  Old structure detected?    │
                          └─────────────┬───────────────┘
                                        │
                              ┌─────────┴─────────┐
                              │                   │
                              ▼                   ▼
                     ┌────────────────┐  ┌────────────────┐
                     │   No files     │  │  Files found   │
                     └────────┬───────┘  └────────┬───────┘
                              │                   │
                              ▼                   ▼
                     ┌────────────────┐  ┌────────────────────┐
                     │ Mark as done   │  │ backup_characters() │
                     │ Return         │  │ → ZIP backup       │
                     └────────────────┘  └────────┬───────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────────┐
                                         │ Backup successful?  │
                                         └────────┬────────────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │                           │
                                    ▼                           ▼
                           ┌────────────────┐        ┌──────────────────────┐
                           │ Backup failed  │        │ migrate_all_chars()  │
                           │ Abort          │        │ • Loop through files │
                           └────────────────┘        │ • Validate each      │
                                                     │ • Track successes    │
                                                     └──────────┬───────────┘
                                                                │
                                                                ▼
                                                     ┌──────────────────────┐
                                                     │ All migrations OK?   │
                                                     └──────────┬───────────┘
                                                                │
                                                  ┌─────────────┴─────────────┐
                                                  │                           │
                                                  ▼                           ▼
                                         ┌────────────────┐        ┌─────────────────────┐
                                         │ Some failures  │        │ All successful      │
                                         └────────┬───────┘        └─────────┬───────────┘
                                                  │                          │
                                                  ▼                          ▼
                                         ┌────────────────┐        ┌─────────────────────┐
                                         │ rollback_      │        │ cleanup_old_files() │
                                         │ migration()    │        │ mark_migration_done()│
                                         │ Remove new     │        │ (in config.json)    │
                                         │ files          │        └─────────┬───────────┘
                                         └────────────────┘                  │
                                                                             ▼
                                                                  ┌──────────────────────┐
                                                                  │ Migration Complete   │
                                                                  │ Application starts   │
                                                                  └──────────────────────┘
```

---

## Character Schema

### character_schema.py

#### Purpose

Defines the expected structure for character JSON files and provides validation functions.

#### Required Fields

```python
REQUIRED_FIELDS = {
    "name": str,        # Character name
    "realm": str,       # Albion, Hibernia, Midgard
    "class": str,       # Character class
    "race": str,        # Character race
    "level": int,       # 1-50
    "season": str,      # S1, S2, S3, etc.
    "server": str       # Eden
}
```

**Validation Rules:**
- `name`: Non-empty string
- `realm`: Must be one of `["Albion", "Hibernia", "Midgard"]`
- `class`: Non-empty string
- `race`: Non-empty string
- `level`: Integer between 1 and 50
- `season`: Must match pattern `S\d+` (e.g., S1, S2, S3)
- `server`: Must be one of `["Eden"]`

#### Optional Fields

```python
OPTIONAL_FIELDS = {
    "id": "",                   # Character ID
    "page": 1,                  # Herald page number
    "guild": "",                # Guild name
    "realm_rank": "",           # Code format: "1L0", "5L3"
    "realm_title": "",          # Text format: "Guardian", "Warlord"
    "realm_points": 0,          # RvR points
    "url": "",                  # Herald URL
    "created_date": "",         # Creation timestamp
    "modified_date": "",        # Last modification timestamp
    "armor": {},                # Armor configuration
    "stats": {},                # Character statistics
    "achievements": []          # List of achievements
}
```

#### Key Functions

##### validate_character_data()

```python
def validate_character_data(char_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates character data structure and content.
    
    Args:
        char_data: Character data dictionary to validate
        
    Returns:
        tuple: (is_valid: bool, errors: List[str])
    
    Validation Checks:
        1. Data is a dictionary
        2. All required fields are present
        3. Field types are correct
        4. Realm is valid (Albion/Hibernia/Midgard)
        5. Server is valid (Eden)
        6. Season format is valid (S + number)
        7. Level is between 1 and 50
        8. Optional fields have correct types (if present)
    
    Example:
        is_valid, errors = validate_character_data(char_data)
        if not is_valid:
            print("Validation errors:", errors)
    """
```

##### normalize_character_data()

```python
def normalize_character_data(char_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes character data by adding missing optional fields with defaults.
    
    Args:
        char_data: Original character data
        
    Returns:
        dict: Normalized character data with all fields
    
    Operations:
        - Adds missing optional fields with default values
        - Sets season to S3 if missing or invalid
        - Sets server to Eden if missing
        - Preserves all existing data
    
    Example:
        normalized = normalize_character_data(char_data)
        # normalized now has all optional fields with defaults
    """
```

##### validate_season_format()

```python
def validate_season_format(season: str) -> bool:
    """
    Validates that season matches expected format (S followed by digits).
    
    Args:
        season: Season string to validate
        
    Returns:
        bool: True if valid format, False otherwise
        
    Examples:
        validate_season_format("S3")     # True
        validate_season_format("S10")    # True
        validate_season_format("Season3") # False
        validate_season_format("")       # False
    """
```

##### get_character_info_summary()

```python
def get_character_info_summary(char_data: Dict[str, Any]) -> str:
    """
    Generates a human-readable summary of character information.
    
    Args:
        char_data: Character data dictionary
        
    Returns:
        str: Formatted summary string
    
    Example:
        summary = get_character_info_summary(char_data)
        # Returns: "Merlin - Albion Wizard (Level 50, S3)"
    """
```

---

## Migration System

### character_migration.py

#### Purpose

Handles the complete migration process from old structure to new structure with backup, validation, and rollback capabilities.

#### Constants

```python
CHARACTERS_DIR = "Characters"
BACKUP_DIR = "Backup/Characters"
```

#### Core Functions

##### detect_old_structure()

```python
def detect_old_structure() -> bool:
    """
    Detects if old character structure exists (Characters/Realm/*.json).
    
    Detection Logic:
        1. Check if Characters/ directory exists
        2. For each realm (Albion, Hibernia, Midgard):
           - Check if Characters/Realm/ folder exists
           - Check if folder contains any .json files
        3. Return True if any realm folder has JSON files
    
    Returns:
        bool: True if old structure detected, False otherwise
    
    Example:
        if detect_old_structure():
            print("Old structure found, migration needed")
    """
```

##### backup_characters()

```python
def backup_characters() -> Tuple[Optional[str], int]:
    """
    Creates ZIP backup of all existing character files.
    
    Process:
        1. Create Backup/Characters/ directory if needed
        2. Generate timestamped filename
        3. Create ZIP archive
        4. Walk through Characters/ directory
        5. Add all .json files to ZIP
        6. Validate ZIP integrity (testzip)
        7. Return backup path and file count
    
    Backup Format:
        Characters_migration_backup_YYYYMMDD_HHMMSS.zip
        Example: Characters_migration_backup_20251116_143052.zip
    
    ZIP Structure:
        Characters/
          ├─ Albion/
          │   └─ Merlin.json
          ├─ Hibernia/
          │   └─ Cuchulainn.json
          └─ Midgard/
              └─ Thor.json
    
    Returns:
        tuple: (backup_path: str or None, file_count: int)
            - backup_path: Path to created ZIP file, or None if failed
            - file_count: Number of files backed up
    
    Safety Features:
        - Validates ZIP integrity after creation
        - Removes corrupted ZIP files
        - Returns None if backup fails
    """
```

##### migrate_character_file()

```python
def migrate_character_file(old_path: str, char_data: Dict[str, Any]) -> Optional[str]:
    """
    Migrates a single character file to new structure.
    
    Process:
        1. Normalize character data (add missing fields)
        2. Validate normalized data against schema
        3. Determine season from data (or use default S3)
        4. Extract realm from data
        5. Build new path: Characters/Season/Realm/filename.json
        6. Create destination directory
        7. Write normalized data to new location
        8. Verify file was written correctly
        9. Verify file contains valid JSON
        10. Return new file path
    
    Args:
        old_path: Path to old character file
        char_data: Character data dictionary
        
    Returns:
        str: New file path if successful, None otherwise
    
    Season Detection:
        - If char_data has 'season' field and it's valid → use it
        - Otherwise → use default season (S3)
    
    Example:
        old_path = "Characters/Albion/Merlin.json"
        new_path = migrate_character_file(old_path, char_data)
        # Returns: "Characters/S3/Albion/Merlin.json"
    
    Error Handling:
        - Validation failure → return None
        - Invalid realm → return None
        - File write failure → return None
        - Invalid JSON → delete new file, return None
    """
```

##### migrate_all_characters()

```python
def migrate_all_characters() -> Tuple[bool, str, Dict[str, Any]]:
    """
    Migrates all character files from old structure to new structure.
    
    Process:
        1. Initialize statistics tracking
        2. For each realm (Albion, Hibernia, Midgard):
           a. Check if realm folder exists
           b. Get all .json files in realm folder
           c. For each .json file:
              - Read character data
              - Migrate file using migrate_character_file()
              - Track success/failure
              - Log progress
        3. Check if all files migrated successfully
        4. If any failures → rollback
        5. If all successful → cleanup old structure
        6. Return result with statistics
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
            - success: True if all files migrated successfully
            - message: Status message
            - stats: Dictionary with migration statistics
    
    Statistics Dictionary:
        {
            "total": 10,              # Total files found
            "migrated": 10,           # Successfully migrated
            "failed": 0,              # Failed migrations
            "skipped": 0,             # Skipped files
            "migrated_files": [...],  # List of new file paths
            "old_files": [...]        # List of old file paths
        }
    
    Rollback Trigger:
        - Any file fails to migrate
        - Any unexpected error occurs
    
    Example:
        success, message, stats = migrate_all_characters()
        if success:
            print(f"Migrated {stats['migrated']} characters")
        else:
            print(f"Migration failed: {message}")
    """
```

##### rollback_migration()

```python
def rollback_migration(migrated_files: List[str]) -> int:
    """
    Rolls back migration by removing newly created files.
    
    Process:
        1. For each file in migrated_files:
           - Check if file exists
           - Delete file
           - Log deletion
        2. Return count of files deleted
    
    Args:
        migrated_files: List of file paths that were migrated
        
    Returns:
        int: Number of files rolled back
    
    Safety:
        - Only removes files that were just created
        - Leaves original files untouched (they're in backup)
        - Logs each rollback operation
    
    Example:
        rolled_back = rollback_migration(stats["migrated_files"])
        print(f"Rolled back {rolled_back} files")
    """
```

##### cleanup_old_structure()

```python
def cleanup_old_structure(old_files: List[str]):
    """
    Removes old character files and empty realm directories.
    
    Process:
        1. Delete all old character files
        2. For each realm directory:
           - Check if directory is empty
           - If empty → remove directory
        3. Log cleanup operations
    
    Args:
        old_files: List of old file paths to remove
    
    Safety:
        - Only called after successful migration
        - Only removes files explicitly listed
        - Only removes empty directories
    
    Example:
        cleanup_old_structure(stats["old_files"])
    """
```

##### run_migration()

```python
def run_migration(silent: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Main migration orchestration function.
    
    Complete Workflow:
        1. Log migration start
        2. Check if already done (via config.json)
           → If yes, return early
        3. Detect old structure
           → If no old files, mark as done and return
        4. Create backup
           → If backup fails, abort
        5. Run migration (migrate_all_characters)
        6. If successful:
           → Mark migration as done in config.json
           → Log statistics
        7. If failed:
           → Rollback already performed by migrate_all_characters
           → Log error
        8. Return result
    
    Args:
        silent: If True, only log to file. If False, print to console.
        
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    
    Possible Stats Status Values:
        - "already_done": Migration was already completed
        - "nothing_to_migrate": No old structure detected
        - "backup_failed": Backup creation failed
        - Normal stats dict: Migration attempted
    
    Example:
        success, message, stats = run_migration(silent=False)
        if success:
            print("Migration completed successfully")
        else:
            print(f"Migration failed: {message}")
    """
```

---

## Integration

### character_manager.py

#### Auto-Execution on Module Load

The migration system is integrated into `character_manager.py` and executes **automatically** when the module is loaded.

```python
# At the end of character_manager.py

def _run_character_migration():
    """
    Runs automatic character file migration at startup.
    
    This function is called automatically when the character_manager 
    module is loaded. Migration is silent and transparent to the user.
    
    Features:
        - Silent execution (no user interaction)
        - Error logging without blocking app startup
        - Uses config.json for migration tracking
        - Only runs once (flag prevents re-runs)
    
    Error Handling:
        - ImportError: Migration module not available (logged, not fatal)
        - Exception: Unexpected error (logged, not fatal)
        - Migration failure: Error logged, app continues
    """
    try:
        from Functions.character_migration import run_migration
        
        # Run migration silently
        success, message, stats = run_migration(silent=True)
        
        if success:
            status = stats.get("status", "migrated")
            if status == "already_done":
                logger.debug("Character migration: Already completed")
            elif status == "nothing_to_migrate":
                logger.debug("Character migration: No old structure detected")
            else:
                migrated = stats.get("migrated", 0)
                logger.info(f"Character migration: Successfully migrated {migrated} character(s)")
        else:
            # Log error but don't block application startup
            logger.error(f"Character migration failed: {message}")
            
    except ImportError:
        logger.warning("Character migration module not found, skipping migration")
    except Exception as e:
        logger.error(f"Unexpected error during character migration: {e}")

# Run migration automatically when module is loaded
_run_character_migration()
```

#### Execution Context

**When:** Module load time (when `character_manager` is first imported)  
**Where:** `main.py` imports `character_manager` early in startup  
**How:** Automatic, no function call needed  
**User Impact:** None (completely transparent)

---

## Migration Tracking

### config.json Integration

Unlike config/language migrations (which modify the file structure itself), character migration requires explicit tracking because:
- Files are **moved** (not modified in place)
- Old structure could theoretically reappear
- Need to prevent duplicate migrations

#### Migration Section

```json
{
    "ui": { ... },
    "folders": { ... },
    "backup": { ... },
    "system": { ... },
    "game": { ... },
    "migrations": {
        "character_structure_done": false,
        "character_structure_date": null
    }
}
```

#### Schema Definition

From `config_schema.py`:

```python
DEFAULT_CONFIG = {
    # ... other sections ...
    "migrations": {
        "character_structure_done": False,  # Boolean flag
        "character_structure_date": None    # ISO timestamp
    }
}
```

#### Migration Tracking Functions

##### is_migration_done()

```python
def is_migration_done() -> bool:
    """
    Checks if migration has already been completed by reading config.json.
    
    Process:
        1. Get config manager instance
        2. Read migrations section from config
        3. Check character_structure_done flag
        4. Return boolean result
    
    Returns:
        bool: True if migration flag is set in config, False otherwise
    
    Safety:
        - Returns False if config manager not available
        - Returns False if migrations section missing
        - Returns False on any error
    
    Example:
        if is_migration_done():
            print("Migration already completed")
        else:
            print("Migration needed")
    """
```

##### mark_migration_done()

```python
def mark_migration_done():
    """
    Marks migration as complete in config.json.
    
    Process:
        1. Get config manager instance
        2. Ensure migrations section exists
        3. Set character_structure_done = True
        4. Set character_structure_date = current timestamp (ISO format)
        5. Save config to disk
    
    Config Changes:
        migrations.character_structure_done: false → true
        migrations.character_structure_date: null → "2025-11-16T14:30:52.123456"
    
    Safety:
        - Creates migrations section if missing
        - Logs error if config manager unavailable
        - Uses ISO 8601 timestamp format
    
    Example (config.json after migration):
        {
            "migrations": {
                "character_structure_done": true,
                "character_structure_date": "2025-11-16T14:30:52.123456"
            }
        }
    """
```

#### Benefits of config.json Tracking

| Aspect | config.json | Separate .migration_done File |
|--------|-------------|-------------------------------|
| **Centralization** | ✅ All migrations in one place | ❌ Scattered flag files |
| **Visibility** | ✅ User can see in config | ❌ Hidden dot file |
| **Backup** | ✅ Included in config backups | ❌ Might be missed |
| **Extensibility** | ✅ Easy to add more migration flags | ❌ Need more files |
| **Consistency** | ✅ Same as config/language pattern | ❌ Different approach |
| **Timestamp** | ✅ Stored with migration date | ❌ Only file existence |

---

## Error Handling & Rollback

### Error Scenarios

#### 1. Backup Failure

**Trigger:** ZIP creation fails, ZIP is corrupted

**Action:**
```python
if backup_path is None:
    logger.error("Failed to create backup, migration aborted")
    return False, "backup_failed", {...}
```

**Result:** Migration aborted, no files touched

#### 2. Validation Failure

**Trigger:** Character data doesn't match schema

**Action:**
```python
is_valid, errors = validate_character_data(char_data)
if not is_valid:
    logger.error(f"Validation failed: {errors}")
    return None  # File not migrated
```

**Result:** File skipped, added to failures count

#### 3. File Write Failure

**Trigger:** Disk full, permissions error, path issues

**Action:**
```python
try:
    with open(new_path, 'w') as f:
        json.dump(data, f)
except Exception as e:
    logger.error(f"Failed to write {new_path}: {e}")
    return None
```

**Result:** File skipped, added to failures count

#### 4. Any Migration Failure

**Trigger:** stats["failed"] > 0

**Action:**
```python
if stats["failed"] > 0:
    rollback_count = rollback_migration(stats["migrated_files"])
    return False, f"Migration failed: {stats['failed']} errors. Rolled back {rollback_count} files.", stats
```

**Result:** All migrated files deleted, original files preserved

### Rollback Mechanism

#### Automatic Rollback

Rollback is **automatic** and triggered by:
- Any file failing validation
- Any file failing to migrate
- Any unexpected error during migration

#### Rollback Process

```python
def rollback_migration(migrated_files: List[str]) -> int:
    """
    1. For each successfully migrated file:
       - Delete new file (Characters/Season/Realm/*.json)
       - Log deletion
    2. Leave original files untouched (in backup)
    3. Return count of deleted files
    """
```

#### Post-Rollback State

After rollback:
- ✅ New structure removed (Characters/Season/...)
- ✅ Old structure intact (Characters/Realm/...)
- ✅ Backup ZIP preserved (Backup/Characters/*.zip)
- ✅ Migration flag NOT set (can retry)
- ✅ User can investigate logs and retry

### Backup Preservation

**Important:** Backup ZIP is **NEVER** deleted, even after successful migration.

**Rationale:**
- Manual recovery possible if needed
- Provides audit trail
- Minimal disk space cost
- User can delete manually if desired

---

## Usage Guide

### For Developers

#### Running Migration Manually

```python
from Functions.character_migration import run_migration

# Run migration
success, message, stats = run_migration(silent=False)

if success:
    print(f"✅ Migration successful: {stats['migrated']} characters")
else:
    print(f"❌ Migration failed: {message}")
    print(f"   Failed: {stats['failed']}")
```

#### Checking Migration Status

```python
from Functions.character_migration import is_migration_done
from Functions.config_manager import config

# Method 1: Using function
if is_migration_done():
    print("Migration completed")

# Method 2: Reading config directly
status = config.get("migrations.character_structure_done", False)
date = config.get("migrations.character_structure_date", None)
print(f"Migration done: {status}, Date: {date}")
```

#### Validating Character Data

```python
from Functions.character_schema import validate_character_data
import json

# Load character file
with open("Characters/S3/Albion/Merlin.json", 'r') as f:
    char_data = json.load(f)

# Validate
is_valid, errors = validate_character_data(char_data)

if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

#### Normalizing Character Data

```python
from Functions.character_schema import normalize_character_data

# Normalize (adds missing optional fields)
normalized = normalize_character_data(char_data)

# Check added fields
if "season" not in char_data and "season" in normalized:
    print(f"Season added: {normalized['season']}")
```

### For Users

#### Automatic Migration

**When:** First application startup after upgrade to v0.108

**Process:**
1. Application starts
2. `character_manager` module loads
3. Migration runs automatically (silent)
4. Logs written to console/file
5. Application continues normally

**No user action required!**

#### Checking Migration Status

**Option 1: Check config.json**

Open `Configuration/config.json` and look for:

```json
{
    "migrations": {
        "character_structure_done": true,
        "character_structure_date": "2025-11-16T14:30:52.123456"
    }
}
```

**Option 2: Check directory structure**

Old structure (before migration):
```
Characters/
  ├─ Albion/
  ├─ Hibernia/
  └─ Midgard/
```

New structure (after migration):
```
Characters/
  └─ S3/
      ├─ Albion/
      ├─ Hibernia/
      └─ Midgard/
```

**Option 3: Check logs**

Look for log entries like:
```
[CHARACTER] Character migration: Successfully migrated 10 character(s)
```

#### Backup Location

After migration, backup is located at:
```
Backup/
  └─ Characters/
      └─ Characters_migration_backup_20251116_143052.zip
```

**Recommended:** Keep this backup until you verify all characters are accessible.

#### Manual Restoration

If you need to restore from backup:

```powershell
# 1. Extract backup ZIP
Expand-Archive -Path "Backup/Characters/Characters_migration_backup_20251116_143052.zip" -DestinationPath "Backup/Characters/Extracted"

# 2. Remove new structure
Remove-Item -Path "Characters/S3" -Recurse -Force

# 3. Copy old structure back
Copy-Item -Path "Backup/Characters/Extracted/Characters/*" -Destination "Characters/" -Recurse

# 4. Reset migration flag in config.json
# Edit Configuration/config.json:
# Change "character_structure_done": true → false
```

---

## Maintenance

### Migration Logs

During migration, comprehensive logging is performed:

```
[INFO] Character migration: Starting
[DEBUG] Migration flag found in config.json (completed: 2025-11-16T14:30:52.123456)
[INFO] Character migration: Already completed
```

Or:

```
[INFO] Character migration: Starting
[DEBUG] No migration flag in config.json
[INFO] Old structure detected: Characters/Albion contains 5 character(s)
[INFO] Backup created: Backup/Characters/Characters_migration_backup_20251116_143052.zip (10 files)
[INFO] ✓ Merlin - Albion Wizard (Level 50, S3)
[INFO] ✓ Arthur - Albion Paladin (Level 50, S3)
...
[INFO] Migration successful: 10/10 characters migrated
[INFO] Migration marked as complete in config.json
```

### Debugging

#### Force Re-Migration

```python
from Functions.config_manager import config

# Reset migration flag
config.set("migrations.character_structure_done", False)
config.set("migrations.character_structure_date", None)

# Restart application to trigger migration
```

#### Check Schema Compliance

```python
from Functions.character_schema import validate_character_data
import json
import os

def check_all_characters():
    """Validate all character files against schema"""
    for root, dirs, files in os.walk("Characters"):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    data = json.load(f)
                
                is_valid, errors = validate_character_data(data)
                if not is_valid:
                    print(f"\n❌ {path}:")
                    for error in errors:
                        print(f"   - {error}")
                else:
                    print(f"✅ {path}")

check_all_characters()
```

#### Verify Backup Integrity

```python
import zipfile

backup_path = "Backup/Characters/Characters_migration_backup_20251116_143052.zip"

with zipfile.ZipFile(backup_path, 'r') as zipf:
    # Test ZIP integrity
    result = zipf.testzip()
    
    if result is None:
        print("✅ Backup ZIP is valid")
        
        # List contents
        print("\nBackup contents:")
        for info in zipf.filelist:
            print(f"  {info.filename} ({info.file_size} bytes)")
    else:
        print(f"❌ Corrupted file in backup: {result}")
```

### Common Issues

#### 1. Migration Runs Every Startup

**Symptom:** Migration logs appear on every application start

**Cause:** Migration flag not being set in config.json

**Solution:**
```python
# Check if config manager is working
from Functions.config_manager import config
print(config.get("migrations.character_structure_done"))

# Manually set flag if needed
config.set("migrations.character_structure_done", True)
config.set("migrations.character_structure_date", "2025-11-16T14:30:52")
```

#### 2. Some Characters Missing After Migration

**Symptom:** Not all characters visible in application

**Cause:** Files might be in wrong season folder

**Solution:**
```python
# List all character files
import os

for root, dirs, files in os.walk("Characters"):
    for file in files:
        if file.endswith('.json'):
            path = os.path.join(root, file)
            print(f"Found: {path}")
```

#### 3. Validation Errors During Migration

**Symptom:** Migration logs show validation errors

**Cause:** Character files have missing/invalid required fields

**Solution:**
1. Check migration logs for specific errors
2. Restore from backup
3. Manually fix invalid files
4. Reset migration flag and retry

```python
# Example: Fix missing season field
import json
import os

def fix_missing_season(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    if "season" not in data or not data["season"]:
        data["season"] = "S3"
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Fixed: {file_path}")
```

#### 4. Backup File Too Large

**Symptom:** Backup ZIP is very large

**Cause:** Many characters or large stats/armor data

**Solution:**
- Normal behavior, keep the backup
- If needed, compress backup further:

```powershell
# Re-compress with maximum compression
7z a -tzip -mx=9 Characters_backup_compressed.zip Backup/Characters/Characters_migration_backup_*.zip
```

### Future Migrations

The migration system is designed to be extensible for future needs.

#### Adding New Migration Types

Example: Migrating armor configuration format

```python
# In config_schema.py
DEFAULT_CONFIG = {
    # ... existing ...
    "migrations": {
        "character_structure_done": False,
        "character_structure_date": None,
        "armor_format_done": False,        # NEW
        "armor_format_date": None          # NEW
    }
}

# Create new migration module
# Functions/armor_migration.py
def migrate_armor_format():
    """Migrate armor configuration from v1 to v2 format"""
    if config.get("migrations.armor_format_done"):
        return  # Already done
    
    # Migration logic...
    
    # Mark as done
    config.set("migrations.armor_format_done", True)
    config.set("migrations.armor_format_date", datetime.now().isoformat())
```

---

## Summary

### Key Features

| Feature | Description |
|---------|-------------|
| **Automatic** | Runs on first startup, no user action needed |
| **Safe** | Full backup before migration, automatic rollback on error |
| **Validated** | Strict schema validation for all character data |
| **Tracked** | Migration status stored in config.json |
| **Logged** | Complete operation logging for debugging |
| **One-time** | Flag prevents duplicate migrations |
| **Transparent** | Silent execution, no UI popups |

### File Changes

**New Files:**
- `Functions/character_schema.py` (390 lines)
- `Functions/character_migration.py` (481 lines)

**Modified Files:**
- `Functions/character_manager.py` (+45 lines)
- `Functions/config_schema.py` (+4 lines)

**Documentation:**
- `Documentations/Char/CHARACTER_MIGRATION_PLAN.md`
- `Documentations/Char/CHARACTER_MIGRATION_TECHNICAL_DOC.md` (this file)

**Total:** ~916 lines of new code, 2 new modules, fully automatic migration system

---

**End of Technical Documentation**
