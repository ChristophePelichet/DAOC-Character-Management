# CHANGELOG v0.106 - Logging System & Developer Tools# CHANGELOG v0.106 - Eden Scraping & Auto-Update Fixes



**Date**: 2025-11-01  **Date** : 2025-11-01  

**Version**: 0.106**Version** : 0.106



---## 🐛 Fixes



## 🔧 New Logging System### Eden cookies save path (PyInstaller fix)

- **Problem** : Cookies were not being saved to the `Configuration/` folder by default

### Unified format with ACTION- **Cause** : `CookieManager` was using `Path(__file__).parent.parent` which caused issues with PyInstaller

- **Solution** : Using `get_config_dir()` from `config_manager.py` for global consistency

- **Before**: Inconsistent format, difficult to filter and analyze logs- **Result** : Cookies are now correctly saved in the folder defined by `config_folder` in `config.json`

- **Now**: Standardized format `LOGGER - LEVEL - ACTION - MESSAGE`- **Compatibility** : Works correctly with compiled application and normal execution

- **Example**: `2025-11-01 14:30:00 - BACKUP - INFO - INIT - BackupManager initialized`- **Modified file** : `Functions/cookie_manager.py` (line 22-34)

- **Benefits**:

  * Easy filtering by logger (BACKUP, EDEN, UI, CHARACTER, ROOT)### Column configuration fixed

  * Clear actions for each operation- **Problem 1** : The Herald URL column (index 11) was not included in resize mode (`range(11)` instead of `range(12)`)

  * Complete execution flow traceability- **Problem 2** : The order of Class and Level columns was reversed in the configuration menu

  * Compatible with log analysis tools- **Problem 3** : Visibility mapping used incorrect order and URL column was missing

- **Solution** :

### BACKUP Logger - Backup Module  * `apply_column_resize_mode()` now correctly handles all 12 columns

  * Configuration menu order aligned with TreeView (Class before Level)

- **Files modified**: `backup_manager.py`, `migration_manager.py`  * `column_map` fixed with correct order and URL column inclusion

- **46+ logs tagged** with clear actions- **Impact** : All 12 columns (0-11) are now correctly configurable for resize mode and visibility

- **Standardized actions**: INIT, DIRECTORY, CHECK, STARTUP, TRIGGER, AUTO_TRIGGER, AUTO_PROCEED, AUTO_BLOCKED, MANUAL_TRIGGER, ZIP, RETENTION, SCAN, DELETE, INFO, RESTORE, ERROR- **Modified files** : `Functions/tree_manager.py`, `UI/dialogs.py`

- **Levels**: DEBUG (details), INFO (progress), WARNING (alerts), ERROR (errors)

## ✨ Improvements

### EDEN Logger - Herald Scraper

### Auto-update on character import

- **File**: `eden_scraper.py`- **Before** : If character exists → Error "character already exists"

- **Actions**: INIT, COOKIES, SCRAPE, SEARCH, PARSE, TEST, CLOSE, CLEANUP, ERROR- **Now** : If character exists → Automatic update from Herald 🔄

- **Preserved data** : name, realm, season, server, custom fields

### Enhanced Debug Window- **Updated data** : class, race, guild, level, realm_rank, realm_points, url, notes

- **Detailed report** : Shows number of creations, updates and errors

- **New filter**: Dropdown to filter by logger- **Use case** : Ideal for keeping characters up-to-date via Herald import

- **Options**: All, BACKUP, EDEN, UI, CHARACTER, ROOT- **Modified file** : `UI/dialogs.py` - Function `_import_characters()` (line 2422)



---### Configurable Herald cookies folder

- **New option** : Settings window → "Herald Cookies Directory"

## 🛠️ Log Source Editor - New Development Tool- **Feature** : Specify a custom folder for saving Eden scraping cookies

- **Interface** : "Browse..." button to facilitate folder selection

### Overview- **Default value** : `Configuration/` folder (behavior preserved if not configured)

- **Portable application** : Paths are absolute, no dependency on `__file__`

- **File**: `Tools/log_source_editor.py` (975 lines)- **Persistence** : Configuration is saved in `config.json` under key `"cookies_folder"`

- **Purpose**: Edit logs directly in source code BEFORE compilation- **Fallback logic** : If `cookies_folder` is not set, uses `config_folder` (ensures backward compatibility)

- **Framework**: PySide6 (Qt6) with complete GUI- **Modified files** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`



### Source Code Scanner### Unified folder labels

- **Before** : Mixed labels ("Folder of...", "Directory of...")

- **Technology**: Asynchronous QThread to not block UI- **Now** : All folder paths start with "Directory"

- **Pattern 1**: Detects `logger.info()`, `self.logger.debug()`, `module_logger.warning()`- **Labels** :

- **Pattern 2**: Detects `log_with_action(logger, "info", "message", action="TEST")`  * Character Directory

- **Smart detection**:  * Configuration Directory

  * Extract logger name from file name  * Log Directory

  * Parse `get_logger(LOGGER_XXX)`  * Armor Directory

  * Parse `setup_logger("LOGGER_NAME")`  * Herald Cookies Directory

- **Removed colons** : No more colons at the end of labels (added automatically by QFormLayout)

### User Interface- **Localization** : Complete translations in EN, FR, DE

- **Modified files** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

**Main layout**:

- **Left**: Table of found logs (read-only)### Improved path display

  * Columns: File, Line, Logger, Level, Action, Message, Modified- **Before** : Cursor was at start but text was aligned to end (displaying "...Configuration/" in QLineEdit)

- **Right**: Edit panel- **Now** : `setCursorPosition(0)` applied to all path fields

  * Action: Editable ComboBox with history- **Result** : Beginning of path is visible (e.g., "d:\Projects\Python\..." instead of "...Configuration/")

  * Message: Multi-line QTextEdit- **Modified file** : `UI/dialogs.py` - Method `update_fields()` (line 1260+)

  * Original code: Read-only QTextEdit

### Robust diagnostic system for unexpected crashes

**Toolbar**:- **Global exception handler** : Captures and logs all unhandled exceptions

- 🔍 Scan project- **System signal handler** : Detects SIGTERM, SIGINT and other OS interruptions

- Filters: Logger, Level, Modified only, Text search- **CRITICAL/ERROR logging always active** : Even with debug_mode = OFF, errors are recorded

- Statistics: `📊 X/Y logs | ✏️ Z modified`- **Startup tracing** : Records time (ISO 8601), Python version, active threads

- **Shutdown tracing** : Records exactly when and how the app stops

### Key Features- **Exit code** : Shows the code returned by the Qt event loop

- **Modified files** : `main.py`, `Functions/logging_manager.py`

**1. Action ComboBox with history**

- Pre-filled with all actions found in scan### CHANGELOGs system cleanup and reorganization

- Editable: allows typing new actions- **Old system** : Monolithic CHANGELOGs in `Documentation/` mixing all versions (difficult to navigate)

- Auto-completion based on history- **New system** : Hierarchical structure in `Changelogs/` with clear separation by version and language

- Dynamic addition of new actions- **Structure created** :

  - `Changelogs/Full/` : Detailed CHANGELOGs (~150 lines) for v0.106, v0.104 and earlier versions

**2. Keyboard shortcuts**  - `Changelogs/Simple/` : Concise lists for quick navigation of all 7 versions (v0.1 to v0.106)

- `Enter` in Action field → Apply changes  - Tri-lingual support : FR, EN, DE for each file

- `Ctrl+Enter` in Message field → Apply changes- **Centralized access** : New `CHANGELOG.md` at root with index and navigation to all versions

- **Old content** : Monolithic CHANGELOGs removed from `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)

**3. Filtering system**- **Files created** : 27 files total (6 Full + 21 Simple)

- **By logger**: BACKUP, EDEN, UI, CHARACTER, ROOT, All- **Result** : Much clearer and more maintainable system for finding changes by version and language

- **By level**: DEBUG, INFO, WARNING, ERROR, CRITICAL, All

- **By status**: All, Modified only## 📊 Overall Impact

- **By text**: Search in messages

✅ **More intuitive and fluid import workflow** - No need to delete/reimport existing character  

**4. Save to files**✅ **Transparent stats update from Herald** - Characters automatically update  

- Direct modification of Python source files✅ **Proper error handling with detailed report** - Number of creations, updates and errors  

- Preserves original indentation✅ **Increased flexibility for cookie management** - Customizable paths for scraping  

- Supports f-strings and complex formats✅ **Complete application portability** - Centralized configuration without __file__ dependencies  

✅ **Ability to diagnose unexpected crashes** - Detailed logs of all critical events  

**5. Remember last project**✅ **Consistent and coherent interface** - Unified labels and optimal path display  

- JSON configuration: `Tools/log_editor_config.json`✅ **Automatic backup on modifications** - Each character modification creates a backup with visible logs  

- Automatic loading on startup

- Window title: `🔧 Log Source Editor - ProjectName (X logs)`### Automatic backup system on character updates

- **Problem** : When modifying an existing character (rank, info, armor, skills) or updating from Herald, no backup was triggered

---- **Solution** : Integration of automatic backups with descriptive reason at all modification points

- **Points covered** :

## 🔍 Eden Scraping Fixes  * Herald update after confirmation (main.py)

  * Automatic rank modification (auto_apply_rank)

### Eden cookies save path (PyInstaller fix)  * Manual rank modification (apply_rank_manual)

  * Basic info modification (save_basic_info)

- **Problem**: Cookies didn't save to `Configuration/` folder by default  * Armor/skills modification (CharacterSheetWindow)

- **Solution**: Use `get_config_dir()` from `config_manager.py` for global consistency  * Mass import/update (import dialog)

- **Result**: Cookies now correctly saved in folder defined by `config_folder` in `config.json`- **Backup type** : `backup_characters_force(reason="Update")` → MANUAL (bypass daily limit)

- **Filename** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`

### Auto-update on character import- **Generated logs** : Each modification generates visible logs with `[BACKUP_TRIGGER]` tag :

  ```

- **Before**: If character exists → Error "character already exists"  [BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update

- **Now**: If character exists → Automatic update from Herald 🔄  [BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip

- **Data preserved**: name, realm, season, server, custom data  ```

- **Data updated**: class, race, guild, level, realm_rank, realm_points, url, notes- **Result** : Each character modification automatically creates a backup with descriptive reason and visible logs

- **Modified files** : `main.py`, `UI/dialogs.py`

### Configurable Herald cookies folder- **Documentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` updated with new scenarios



- **New option**: Settings Window → "Herald cookies directory"## 🔗 Modified Files

- **Functionality**: Specify custom folder for Eden scraping cookies

- **Default**: `Configuration/` folder (preserved if not configured)- `main.py`

- `UI/dialogs.py`

---- `Functions/cookie_manager.py`

- `Functions/tree_manager.py`

## 🎨 Interface Improvements- `Functions/logging_manager.py`

- `Language/fr.json`

### Fixed column configuration- `Language/en.json`

- `Language/de.json`

- **Problem 1**: Herald URL column (index 11) not included in resizing- `Documentations/BACKUP_DEBUG_GUIDE.md`

- **Problem 2**: Class and Level column order was reversed in config menu
- **Problem 3**: Visibility mapping used incorrect order and URL column was missing
- **Solution**: All 12 columns (0-11) now correctly configurable

### Unified directory labels

- **Before**: Mixed labels ("Folder of...", "Directory of...")
- **Now**: All folder paths start with "Directory"
- **Labels**: Characters directory, Configuration directory, Logs directory, Armor directory, Herald cookies directory

### Display path start

- **Before**: Cursor at start but text aligned to end
- **Now**: `setCursorPosition(0)` applied to all path fields
- **Result**: Display path start (e.g., "d:\Projects\Python\..." instead of "...Configuration/")

---

## 📚 Documentation

### CHANGELOG system cleanup and reorganization

- **Old system**: Monolithic CHANGELOGs in `Documentation/` mixing all versions
- **New system**: Hierarchical structure at `Changelogs/` with clear separation by version and language
- **Structure**:
  - `Changelogs/Full/`: Detailed CHANGELOGs (~200+ lines)
  - `Changelogs/Simple/`: Concise lists for quick navigation
  - Tri-lingual support: FR, EN, DE

---

## 📊 Statistics

- **Lines of code added**: ~1000+ (log_source_editor.py: 975 lines)
- **Files modified**: 12 files
- **Files created**: 2 files
- **Logs tagged**: 46+ in backup_manager.py, 52+ in eden_scraper.py
- **Standardized actions**: 20+ different actions

---

## 🔄 Migration

**No migration required** - This version is 100% backward compatible with v0.105

---

## 📝 Development Notes

- Log Source Editor is a development tool, not included in main application
- Unified logging format enables better analysis and debugging
- Standardized actions facilitate filtering and searching in logs
