# SuperAdmin Tools - Technical Documentation

## Overview
The **SuperAdmin Tools** system provides administrative-level functionality for rapid population and management of the internal armory source database (`Data/items_database_src.json`). This feature is accessible **only during development** via a special command-line flag and is completely hidden in compiled releases.

**Location**: `Functions/superadmin_tools.py` (359 lines)  
**UI Integration**: `UI/settings_dialog.py` (conditional page)  
**Access Method**: `python main.py --admin` (development only)  
**Security**: Triple-layer protection (flag + frozen check + conditional UI)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERADMIN ACCESS CONTROL                 │
│                                                              │
│  python main.py --admin   →   ADMIN_MODE = True             │
│           +                                                  │
│  NOT sys.frozen           →   Development Environment       │
│           ↓                                                  │
│  Settings Page 7: 🔧⚡ SuperAdmin (Conditional)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│               SUPERADMIN TOOLS ARCHITECTURE                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Functions/superadmin_tools.py                      │    │
│  │  - SuperAdminTools(PathManager)                     │    │
│  │  - get_database_stats()                             │    │
│  │  - backup_source_database()                         │    │
│  │  - parse_template_files()                           │    │
│  │  - build_database_from_files()                      │    │
│  │  - clean_duplicates()                               │    │
│  └────────────────────────────────────────────────────┘    │
│                           ↕                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  UI/settings_dialog.py                              │    │
│  │  - Page 7: SuperAdmin (if ADMIN_MODE)               │    │
│  │  - Build Database Section                           │    │
│  │  - Statistics Section                               │    │
│  │  - Advanced Operations Section                      │    │
│  └────────────────────────────────────────────────────┘    │
│                           ↕                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Data/items_database_src.json                       │    │
│  │  - Internal read-only armory database               │    │
│  │  - Managed exclusively via SuperAdmin               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Model

### **Triple-Layer Protection**

```python
# Layer 1: Command-line flag (main.py line 50)
ADMIN_MODE = '--admin' in sys.argv and not getattr(sys, 'frozen', False)

# Layer 2: Frozen check (prevents access in .exe)
not getattr(sys, 'frozen', False)

# Layer 3: Conditional UI (settings_dialog.py lines 88-91)
if ADMIN_MODE:
    self._create_superadmin_page()
```

**Protection Mechanisms**:

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| **Flag** | Explicit opt-in required | Must run `python main.py --admin` |
| **Frozen** | Blocked in compiled .exe | `sys.frozen` check returns False in dev |
| **UI** | No menu access without flag | Page 7 created conditionally |

**Result**: 
- ✅ Development: `python main.py --admin` → SuperAdmin page visible
- ❌ Development: `python main.py` → No SuperAdmin page
- ❌ Production: `.exe --admin` → No SuperAdmin page (frozen check fails)

---

## SuperAdminTools Class

### **Initialization**

```python
from Functions.superadmin_tools import SuperAdminTools

superadmin = SuperAdminTools(path_manager)
```

**Parameters**:
- `path_manager` (PathManager): Required PathManager instance for file paths

**Attributes**:
- `self.path_manager`: PathManager instance
- `self.source_db_path`: Resolved path to `Data/items_database_src.json`
- `self.backup_dir`: Resolved path to `Data/Backups/`

---

## Core Methods

### **1. get_database_stats()**

Retrieves comprehensive statistics about the source database.

```python
stats = superadmin.get_database_stats()
```

**Returns**: `dict` or `None`

```python
{
    "total_items": 1542,
    "albion": 487,
    "hibernia": 521,
    "midgard": 498,
    "all_realms": 36,
    "file_size": "245.7 KB",
    "last_updated": "2025-11-18 14:23:45"
}
```

**Fields**:
- `total_items` (int): Total number of items in database
- `albion` (int): Count of Albion-specific items
- `hibernia` (int): Count of Hibernia-specific items
- `midgard` (int): Count of Midgard-specific items
- `all_realms` (int): Count of all-realm items
- `file_size` (str): Human-readable file size (KB/MB)
- `last_updated` (str): ISO timestamp of last modification

**Returns `None`** if:
- Database file doesn't exist
- JSON parsing error
- Invalid data structure

---

### **2. backup_source_database()**

Creates a timestamped backup of the source database before destructive operations.

```python
success, path_or_error = superadmin.backup_source_database()
```

**Returns**: `(bool, str)`
- `(True, backup_path)`: Backup successful, returns backup file path
- `(False, error_message)`: Backup failed, returns error description

**Backup File Pattern**:
```
Data/Backups/items_database_src_YYYYMMDD_HHMMSS.json
```

**Example**:
```
Data/Backups/items_database_src_20251118_142345.json
```

**Auto-created folder**: If `Data/Backups/` doesn't exist, creates it automatically.

---

### **3. parse_template_files(file_paths, realm)**

Parses one or more .txt template files to extract item data.

```python
items, errors = superadmin.parse_template_files(file_paths, realm)
```

**Parameters**:
- `file_paths` (list[str]): Absolute paths to .txt files
- `realm` (str): Target realm (`"Albion"`, `"Hibernia"`, `"Midgard"`, or `"All Realms"`)

**Returns**: `(list[dict], list[str])`
- `items`: List of parsed item dictionaries
- `errors`: List of error messages from problematic files

**Item Structure**:
```python
{
    "name": "Ethereal Bond Staff",
    "realm": "Hibernia",
    "source": "internal"
}
```

**Template File Format**:
```
Ethereal Bond Staff
Venom Etched Blade
Ancient Oak Bow
```

**Parsing Rules**:
- One item name per line
- Empty lines ignored
- Whitespace trimmed
- Duplicate detection across files
- UTF-8 encoding with BOM handling

**Error Handling**:
- File not found → Error message in `errors` list
- Encoding issues → Attempts fallback encodings
- Invalid format → Skips line, logs warning

---

### **4. build_database_from_files(file_paths, realm, merge=True, remove_duplicates=True, auto_backup=True)**

Main method for building/updating the source database from template files.

```python
success, message, stats = superadmin.build_database_from_files(
    file_paths=["path/to/items1.txt", "path/to/items2.txt"],
    realm="Hibernia",
    merge=True,
    remove_duplicates=True,
    auto_backup=True
)
```

**Parameters**:
- `file_paths` (list[str]): Paths to .txt template files
- `realm` (str): Target realm for items
- `merge` (bool, default=True): Merge with existing data vs replace
- `remove_duplicates` (bool, default=True): Remove duplicate items (same name+realm)
- `auto_backup` (bool, default=True): Create backup before modification

**Returns**: `(bool, str, dict)`
- `success` (bool): Operation result
- `message` (str): Human-readable result message
- `stats` (dict): Statistics about the operation

**Statistics Dictionary**:
```python
{
    "total_items": 1650,          # Final item count
    "added_items": 108,           # Items added during operation
    "existing_items": 1542,       # Items already in database (if merge)
    "removed_duplicates": 12      # Duplicates removed (if enabled)
}
```

**Workflow**:

```
1. Validation
   ├─ Check file_paths not empty
   ├─ Verify realm is valid
   └─ Ensure files exist

2. Auto-Backup (if enabled)
   ├─ Create timestamped backup
   └─ Return error if backup fails

3. Parse Template Files
   ├─ Read each file
   ├─ Extract item names
   ├─ Create item objects
   └─ Collect errors

4. Load Existing Database (if merge=True)
   ├─ Read current items_database_src.json
   ├─ Parse JSON
   └─ Combine with new items

5. Remove Duplicates (if enabled)
   ├─ Identify items with same name+realm
   ├─ Keep first occurrence
   └─ Track removal count

6. Write Database
   ├─ Sort items by name
   ├─ Write to items_database_src.json
   ├─ Indent for readability (2 spaces)
   └─ Calculate final stats

7. Return Results
   └─ success, message, stats
```

**Example Usage**:

```python
# Build database from 3 files, merge with existing, clean duplicates
success, message, stats = superadmin.build_database_from_files(
    file_paths=[
        "C:/Data/hibernia_weapons.txt",
        "C:/Data/hibernia_armor.txt",
        "C:/Data/hibernia_jewelry.txt"
    ],
    realm="Hibernia",
    merge=True,
    remove_duplicates=True,
    auto_backup=True
)

if success:
    print(f"✅ {message}")
    print(f"Total items: {stats['total_items']}")
    print(f"Added: {stats['added_items']}")
    print(f"Duplicates removed: {stats['removed_duplicates']}")
else:
    print(f"❌ {message}")
```

---

### **5. clean_duplicates()**

Removes duplicate items (same name + realm) from the source database.

```python
success, message, count = superadmin.clean_duplicates()
```

**Returns**: `(bool, str, int)`
- `success` (bool): Operation result
- `message` (str): Result description
- `count` (int): Number of duplicates removed

**Duplicate Detection Logic**:
```python
unique_key = (item["name"], item["realm"])
```

**Keeps**: First occurrence of each name+realm combination  
**Removes**: All subsequent duplicates

**Workflow**:

```
1. Load Database
   ├─ Read items_database_src.json
   └─ Parse JSON

2. Auto-Backup
   ├─ Create backup before modification
   └─ Return error if backup fails

3. Find Duplicates
   ├─ Build set of (name, realm) tuples
   ├─ Track seen combinations
   └─ Identify duplicates

4. Remove Duplicates
   ├─ Filter to unique items only
   └─ Count removed items

5. Write Clean Database
   ├─ Save if duplicates found
   ├─ Sort by name
   └─ Return count

6. Return Results
   └─ success, message, removed_count
```

**Example**:

```python
success, message, count = superadmin.clean_duplicates()

if success:
    if count > 0:
        print(f"✅ Removed {count} duplicates")
    else:
        print("✅ No duplicates found")
else:
    print(f"❌ {message}")
```

---

## UI Integration

### **Settings Page 7: SuperAdmin**

**Navigation Item** (conditional):
```python
# UI/settings_dialog.py line 153
if ADMIN_MODE:
    nav_item = QListWidgetItem("🔧⚡ " + lang.get("settings.navigation.superadmin"))
```

**Page Layout**:

```
┌─────────────────────────────────────────────────────────┐
│  🔧⚡ SuperAdmin - Outils Administrateur                  │
│  Gestion avancée de la base source de l'armurerie       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🛡️ Armurerie - Base Source                           │
│  ┌───────────────────────────────────────────────────┐ │
│  │ ⚠️ WARNING: These tools modify the internal       │ │
│  │    read-only database. Use with caution!          │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  📋 Construction de la base source                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Fichiers template (.txt):    [Select files...]    │ │
│  │ Royaume:                      [ Hibernia   ▼ ]    │ │
│  │ ☑ Fusionner avec existant                         │ │
│  │ ☑ Supprimer doublons                              │ │
│  │ ☑ Backup automatique                              │ │
│  │                                                    │ │
│  │                [ ⚡ Construire la base ]           │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────┬─────────────────────────┐ │
│  │ 📊 Statistiques         │ ⚙️ Opérations avancées │ │
│  │ ─────────────────────── │ ───────────────────────│ │
│  │ Base de données:        │                         │ │
│  │   items_database_src.   │ [ Nettoyer doublons ]  │ │
│  │                         │                         │ │
│  │ Total items: 1542       │                         │ │
│  │ Albion: 487             │                         │ │
│  │ Hibernia: 521           │                         │ │
│  │ Midgard: 498            │                         │ │
│  │ Tous royaumes: 36       │                         │ │
│  │ Taille: 245.7 KB        │                         │ │
│  │ MAJ: 2025-11-18 14:23   │                         │ │
│  │                         │                         │ │
│  │   [ Actualiser ]        │                         │ │
│  └─────────────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### **UI Components**

**Section 1: Build Database**
- **File Selection Button**: Opens multi-file dialog for .txt templates
- **Realm Combo**: Albion / Hibernia / Midgard / All Realms
- **Merge Checkbox**: Combine with existing items (default: checked)
- **Remove Duplicates Checkbox**: Clean duplicates after import (default: checked)
- **Auto-Backup Checkbox**: Create backup before operation (default: checked)
- **Execute Button**: Triggers `build_database_from_files()`

**Section 2: Statistics** (Left 50%)
- **Database Name**: Fixed label "items_database_src.json"
- **8 Statistics Labels**: Total, Albion, Hibernia, Midgard, All Realms, File Size, Last Updated
- **Refresh Button**: Calls `get_database_stats()` and updates labels

**Section 3: Advanced Operations** (Right 50%)
- **Clean Duplicates Button**: Triggers `clean_duplicates()`

---

## Translation Keys

### **SuperAdmin Namespace**

All SuperAdmin translations use the `superadmin.*` namespace (no `settings.pages.` prefix).

**Page Title/Navigation**:
- `superadmin.title` - "SuperAdmin - Outils Administrateur"
- `settings.navigation.superadmin` - "SuperAdmin" (no emoji)

**Warning Banner**:
- `superadmin.warning` - Warning message about internal database modification

**Armory Section**:
- `superadmin.armory_section_title` - "🛡️ Armurerie - Base Source"

**Build Group**:
- `superadmin.build_group_title` - "📋 Construction de la base source"
- `superadmin.template_files_label` - "Fichiers template (.txt):"
- `superadmin.template_files_button` - "Sélectionner fichiers..."
- `superadmin.realm_label` - "Royaume:"
- `superadmin.merge_checkbox` - "Fusionner avec existant"
- `superadmin.remove_duplicates_checkbox` - "Supprimer doublons"
- `superadmin.auto_backup_checkbox` - "Backup automatique"
- `superadmin.execute_button` - "⚡ Construire la base"

**Statistics Group**:
- `superadmin.stats_group_title` - "📊 Statistiques de la base source"
- `superadmin.stats_database_name` - "Base de données:"
- `superadmin.stats_total` - "Total items:"
- `superadmin.stats_albion` - "Albion:"
- `superadmin.stats_hibernia` - "Hibernia:"
- `superadmin.stats_midgard` - "Midgard:"
- `superadmin.stats_all_realms` - "Tous royaumes:"
- `superadmin.stats_file_size` - "Taille fichier:"
- `superadmin.stats_last_updated` - "Dernière mise à jour:"
- `superadmin.stats_not_available` - "Non disponible"
- `superadmin.stats_refresh_button` - "Actualiser"

**Advanced Operations Group**:
- `superadmin.advanced_group_title` - "⚙️ Opérations avancées"
- `superadmin.clean_duplicates_button` - "Nettoyer les doublons"
- `superadmin.clean_duplicates_tooltip` - Tooltip text

**Messages**:
- `superadmin.build_success` - Success message template
- `superadmin.build_error` - Error message template
- `superadmin.clean_success` - Clean success message
- `superadmin.clean_no_duplicates` - No duplicates found message
- `superadmin.clean_error` - Clean error message

**Total Keys**: 40+ keys in FR/EN/DE

---

## Workflow Examples

### **Scenario 1: Build Database from Multiple Files**

```
1. User Action: Run `python main.py --admin`
2. Application: ADMIN_MODE = True, Page 7 created
3. User Action: Settings → SuperAdmin navigation
4. User Action: Click "Sélectionner fichiers..."
5. Dialog: Multi-select file dialog opens
6. User Action: Select 3 .txt files:
   - hibernia_weapons.txt
   - hibernia_armor.txt
   - hibernia_jewelry.txt
7. User Action: Select realm "Hibernia"
8. User Action: Check "Fusionner avec existant"
9. User Action: Check "Supprimer doublons"
10. User Action: Check "Backup automatique"
11. User Action: Click "⚡ Construire la base"
12. Backend: Auto-backup created
13. Backend: Parse 3 files → 245 items
14. Backend: Merge with existing 1542 items
15. Backend: Remove 12 duplicates
16. Backend: Write database → 1775 items
17. UI: Progress dialog shows operation
18. UI: Success message with stats
19. UI: Statistics auto-refresh
```

### **Scenario 2: Clean Duplicates Only**

```
1. User Action: Run `python main.py --admin`
2. User Action: Settings → SuperAdmin
3. User Action: Click "Nettoyer les doublons"
4. Backend: Auto-backup created
5. Backend: Load database → 1542 items
6. Backend: Find duplicates → 8 found
7. Backend: Remove duplicates → 1534 items
8. Backend: Write clean database
9. UI: Show message "8 doublons supprimés"
10. UI: Statistics auto-refresh
```

### **Scenario 3: Check Statistics**

```
1. User Action: Run `python main.py --admin`
2. User Action: Settings → SuperAdmin
3. Page Load: auto-refresh statistics
4. UI Display:
   - Total items: 1542
   - Albion: 487
   - Hibernia: 521
   - Midgard: 498
   - All Realms: 36
   - File size: 245.7 KB
   - Last updated: 2025-11-18 14:23:45
5. User Action: Click "Actualiser"
6. Backend: get_database_stats()
7. UI: Labels updated with fresh data
```

---

## File Structure

### **Backend**

```
Functions/
└── superadmin_tools.py (359 lines)
    ├── Class SuperAdminTools (lines 15-359)
    │   ├── __init__(self, path_manager) (lines 24-32)
    │   ├── get_database_stats(self) (lines 34-73)
    │   ├── backup_source_database(self) (lines 75-104)
    │   ├── parse_template_files(self, file_paths, realm) (lines 106-167)
    │   ├── build_database_from_files(self, ...) (lines 169-290)
    │   └── clean_duplicates(self) (lines 292-359)
```

### **UI Integration**

```
UI/
└── settings_dialog.py (2651 lines)
    ├── Conditional Page Creation (lines 88-95)
    ├── Navigation Item (lines 131-155)
    ├── _create_superadmin_page(self) (lines 1140-1320)
    ├── _select_template_files(self) (lines 2420-2450)
    ├── _execute_build_database(self) (lines 2455-2560)
    ├── _refresh_superadmin_stats(self) (lines 2570-2590)
    └── _clean_duplicates(self) (lines 2600-2630)
```

### **Translations**

```
Language/
├── fr.json (superadmin.* keys)
├── en.json (superadmin.* keys)
└── de.json (superadmin.* keys)
```

---

## Error Handling

### **File Operations**

```python
try:
    items, errors = superadmin.parse_template_files(file_paths, realm)
    if errors:
        # Show warning with error list
except Exception as e:
    # Critical error dialog
    QMessageBox.critical(self, "Error", str(e))
```

### **Backup Failures**

```python
if auto_backup:
    success, path_or_error = superadmin.backup_source_database()
    if not success:
        return False, f"Backup failed: {path_or_error}", {}
```

### **Database Write Errors**

```python
try:
    with open(self.source_db_path, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
except Exception as e:
    return False, f"Failed to write database: {str(e)}", {}
```

---

## Performance Considerations

### **Large File Handling**

- **Progress Dialog**: Shows during long operations (100+ items)
- **Streaming Parsing**: Reads template files line-by-line
- **Batch Processing**: Processes all selected files in one operation

### **Memory Efficiency**

- Duplicate detection uses sets (O(1) lookup)
- JSON loaded/saved once per operation (not per item)
- PathManager reused across all operations

### **UI Responsiveness**

```python
QApplication.processEvents()  # Periodic UI updates during long ops
```

---

## Security Best Practices

### **Access Control Checklist**

✅ **Command-line flag required** (`--admin`)  
✅ **Development-only access** (`not sys.frozen`)  
✅ **Conditional UI rendering** (no page without flag)  
✅ **Auto-backup before destructive operations**  
✅ **Explicit user confirmation for file selection**  
✅ **Validation of realm/file paths**  
✅ **Error handling for all file operations**

### **Backup Strategy**

- **Automatic backups** before every database modification
- **Timestamped backups** prevent overwriting
- **Backup folder** organized in `Data/Backups/`
- **No auto-deletion** of old backups (manual cleanup)

---

## Testing Workflow

### **Manual Testing Checklist**

**Access Control**:
- [ ] `python main.py` → No SuperAdmin page
- [ ] `python main.py --admin` → SuperAdmin page visible
- [ ] `.exe --admin` → No SuperAdmin page (frozen check)

**Build Database**:
- [ ] Select 1 file → Import successful
- [ ] Select 3 files → All parsed and merged
- [ ] Empty file → Handled gracefully
- [ ] Invalid file → Error message shown
- [ ] Merge enabled → Combines with existing
- [ ] Merge disabled → Replaces database
- [ ] Remove duplicates → Duplicates removed
- [ ] Auto-backup → Backup created

**Statistics**:
- [ ] Initial load → Stats displayed
- [ ] After build → Stats updated
- [ ] Refresh button → Stats refreshed
- [ ] Empty database → Shows zeros
- [ ] Missing file → Shows "Non disponible"

**Clean Duplicates**:
- [ ] Database with duplicates → Removed correctly
- [ ] No duplicates → Message "No duplicates found"
- [ ] Auto-backup → Backup created before clean

**UI Layout**:
- [ ] Statistics and Advanced side-by-side (50/50)
- [ ] All buttons accessible
- [ ] Responsive resizing

---

## Version History

| Version | Changes |
|---------|---------|
| **0.108** | Initial implementation of SuperAdmin tools |
| | - Backend class SuperAdminTools (359 lines) |
| | - UI page in Settings (conditional) |
| | - Build database from template files |
| | - Statistics tracking |
| | - Duplicate cleaning |
| | - Auto-backup system |
| | - Triple-layer security |
| | - FR/EN/DE translations (40+ keys) |
| | - Side-by-side layout (Statistics + Advanced) |

---

## Related Documentation

- [Dual-Mode Database System](../Armory/DUAL_MODE_DATABASE_EN.md)
- [Settings Architecture](SETTINGS_ARCHITECTURE_EN.md)
- [Path Manager](../Core/PATH_MANAGER_EN.md)
- [Translation System](../Lang/LANGUAGE_V2_TECHNICAL_DOC.md)

---

## Future Enhancements

**Potential Additions**:
- [ ] Batch import from folder (auto-detect .txt files)
- [ ] Template file validation (format check)
- [ ] Import history tracking
- [ ] Undo last build operation
- [ ] Export database to .txt templates
- [ ] Merge conflict resolution UI
- [ ] Custom parsing rules configuration
- [ ] Multi-realm import (parse once, apply to multiple realms)

---

**⚠️ CRITICAL REMINDER**: This feature is for **development use only**. The `--admin` flag and frozen check ensure it never appears in production releases. Always test thoroughly before deploying updates to the source database.
