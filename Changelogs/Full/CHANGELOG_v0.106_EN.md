# CHANGELOG v0.106 - Logging System, Cookie Backup & Enhancements

**Date**: 2025-11-01  
**Version**: 0.106

---

## 🔧 New Logging System

### Unified format with ACTION

- **Before**: Inconsistent format, difficult to filter and analyze logs
- **Now**: Standardized format `LOGGER - LEVEL - ACTION - MESSAGE`
- **Example**: `2025-11-01 14:30:00 - BACKUP - INFO - INIT - BackupManager initialized`

**Benefits**:
- Easy filtering by logger (BACKUP, EDEN, UI, CHARACTER, ROOT)
- Clear actions for each operation
- Complete execution flow traceability
- Compatible with log analysis tools

**Implementation**:
- New `ContextualFormatter` in `logging_manager.py`
- Action handling: Uses `extra={"action": "VALUE"}` in logs
- Fallback: Displays "-" if no action is provided
- Helper function: `log_with_action(logger, level, message, action="XXX")`

### BACKUP Logger - Backup Module

- **Modified files**: `backup_manager.py`, `migration_manager.py`
- **46+ logs tagged** with clear actions

**Standardized actions**:
- `INIT` - BackupManager initialization
- `DIRECTORY` - Backup directory creation/verification
- `CHECK` - Check if backup is needed today
- `STARTUP` - Automatic backup on startup
- `TRIGGER` - Automatic backup trigger
- `AUTO_TRIGGER` - Auto-backup start
- `AUTO_PROCEED` - Auto-backup continuation
- `AUTO_BLOCKED` - Auto-backup blocked (already done)
- `MANUAL_TRIGGER` - Manual backup triggered
- `ZIP` - ZIP compression in progress
- `RETENTION` - Retention management (old backup deletion)
- `SCAN` - Existing backup scan
- `DELETE` - Backup deletion
- `INFO` - Backup information
- `RESTORE` - Backup restore
- `ERROR` - General errors

**Levels**: DEBUG (details), INFO (progress), WARNING (alerts), ERROR (errors)

**Traceability**: Detailed logs for each backup process step

### EDEN Logger - Herald Scraper

- **File**: `eden_scraper.py`
- **Actions**: INIT, COOKIES, SCRAPE, SEARCH, PARSE, TEST, CLOSE, CLEANUP, ERROR
- **All logs** now use `extra={"action": "XXX"}`

---

## 🛠️ Log Source Editor - New Development Tool

### Overview

- **File**: `Tools/log_source_editor.py` (975 lines)
- **Purpose**: Edit logs directly in source code BEFORE compilation
- **Framework**: PySide6 (Qt6) with complete GUI

### Source Code Scanner

- **Technology**: Asynchronous QThread to not block UI
- **Pattern 1**: Detects `logger.info()`, `self.logger.debug()`, `module_logger.warning()`
- **Pattern 2**: Detects `log_with_action(logger, "info", "message", action="TEST")`

**Smart detection**:
- Logger name extraction from filename
- Parsing `get_logger(LOGGER_XXX)`
- Parsing `setup_logger("LOGGER_NAME")`

**Parsing**:
- Action extraction from `action="XXX"` or `extra={"action": "XXX"}`
- Message extraction (supports f-strings, normal strings, concatenations)
- Level retrieval (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### User Interface

**Main layout**:
- **Left**: Table of found logs (read-only)
  - Columns: File, Line, Logger, Level, Action, Message, Modified
  - Protection: `setEditTriggers(QTableWidget.NoEditTriggers)`
- **Right**: Edit panel
  - File/Line/Logger/Level (display)
  - Action: Editable ComboBox with history
  - Message: Multi-line QTextEdit
  - Original code: Read-only QTextEdit
  - Buttons: Apply, Reset

**Toolbar**:
- 🔍 Scan project
- Filters: Logger (dropdown), Level (dropdown), Modified only, Text search
- Statistics: `📊 X/Y logs | ✏️ Z modified`

### Key Features

**1. Action ComboBox with history**
- Pre-filled with all actions found in scan
- Editable: allows typing new actions
- Auto-completion: suggestions based on history
- Dynamic addition: new actions automatically added to list
- Policy: `NoInsert` to control addition manually

**2. Keyboard shortcuts**
- `Enter` in Action field → Applies modifications
- `Ctrl+Enter` in Message field → Applies modifications
- Arrow navigation in table

**3. Filtering system**
- **By logger**: BACKUP, EDEN, UI, CHARACTER, ROOT, All
- **By level**: DEBUG, INFO, WARNING, ERROR, CRITICAL, All
- **By status**: All, Modified only
- **By text**: Search in messages
- Real-time statistics update

**4. File saving**
- Direct Python source file modification
- Original indentation preservation
- Support for f-strings and complex formats
- `self.logger` and `module_logger` handling
- Safe line-by-line replacement

**5. Last project memory**
- JSON configuration: `Tools/log_editor_config.json`
- Automatic loading on startup (100ms delay)
- Default selection in dialog
- Window title: `🔧 Log Source Editor - ProjectName (X logs)`

**6. Protections and validations**
- `_updating` flag: prevents recursive update loops
- `blockSignals(True)`: during table updates
- `__eq__` and `__hash__` comparison: avoids reloading same log
- Pre-save check: detects unmodified files

### User Workflow

1. **Launch**: `.venv\Scripts\python.exe Tools\log_source_editor.py`
2. **Auto scan**: Last project loads automatically
3. **Filtering**: Select "Logger: BACKUP" to see backup module logs
4. **Selection**: Click on a log in the table
5. **Editing**:
   - Choose action from dropdown or type a new one
   - Modify message if needed
6. **Apply**: Press Enter or click "Apply"
7. **Repeat**: Navigate with ↓ for next log
8. **Save**: Click "💾 Save" to write to source files

### Displayed Statistics (After scan)

```
✅ Scan complete: 144 logs found

📊 By Logger:
   BACKUP: 46
   EDEN: 52
   ROOT: 30
   UI: 16

📊 By Level:
   INFO: 80
   DEBUG: 40
   WARNING: 15
   ERROR: 9

📊 Actions:
   • Found actions: CHECK, DELETE, DIRECTORY, ERROR, INIT, PARSE, RETENTION, RESTORE, SCAN, SCRAPE, TRIGGER, ZIP
   • With action: 120
   • Without action: 24
```

---

## 🐛 Fixes

### Eden cookies save path (PyInstaller fix)

- **Problem**: Cookies were not being saved to the `Configuration/` folder by default
- **Cause**: `CookieManager` was using `Path(__file__).parent.parent` which caused PyInstaller issues
- **Solution**: Using `get_config_dir()` from `config_manager.py` for global consistency
- **Result**: Cookies are now correctly saved in the folder defined by `config_folder` in `config.json`
- **Compatibility**: Works correctly with compiled application and normal execution
- **Modified file**: `Functions/cookie_manager.py`

### Column configuration fixed

- **Problem 1**: Herald URL column (index 11) was not included in resize mode (`range(11)` instead of `range(12)`)
- **Problem 2**: Class and Level column order was reversed in configuration menu
- **Problem 3**: Visibility mapping used incorrect order and URL column was missing

**Solution**:
- `apply_column_resize_mode()` now correctly handles all 12 columns
- Configuration menu order aligned with TreeView (Class before Level)
- `column_map` fixed with correct order and URL column inclusion

**Impact**: All 12 columns (0-11) are now correctly configurable for resize mode and visibility

**Modified files**: `Functions/tree_manager.py`, `UI/dialogs.py`

### 🧬 Herald Authentication - Simplified & Reliable Detection

- **Problem**: Authentication detection with multiple unreliable criteria
- **Cause**: Invalid cookies or inconsistent detection technique
- **Solution**: Detection based on single definitive criterion

**Detection logic**:
- Error message `'The requested page "herald" is not available.'` = NOT CONNECTED
- Absence of error message = CONNECTED (can scrape data)

**Consistency**:
- Identical logic between `test_eden_connection()` (cookie_manager.py) and `load_cookies()` (eden_scraper.py)
- Invalid cookies correctly detected and reported
- Tests validated with approximately 58 Herald search results

**Modified files**: `Functions/cookie_manager.py`, `Functions/eden_scraper.py`

---

## ✨ Improvements

### Auto-update on character import

- **Before**: If character exists → Error "character already exists"
- **Now**: If character exists → Automatic update from Herald 🔄

**Preserved data**: name, realm, season, server, custom fields

**Updated data**: class, race, guild, level, realm_rank, realm_points, url, notes

**Detailed report**: Shows number of creations, updates and errors

**Use case**: Ideal for keeping characters up-to-date via Herald import

**Modified file**: `UI/dialogs.py` - Function `_import_characters()` (line 2422)

### Configurable Herald cookies folder

- **New option**: Settings window → "Herald Cookies Directory"
- **Feature**: Specify a custom folder for saving Eden scraping cookies
- **Interface**: "Browse..." button to facilitate folder selection
- **Default value**: `Configuration/` folder (behavior preserved if not configured)
- **Portable application**: Paths are absolute, no dependency on `__file__`
- **Persistence**: Configuration is saved in `config.json` under key `"cookies_folder"`
- **Fallback logic**: If `cookies_folder` is not set, uses `config_folder` (ensures backward compatibility)

**Modified files**: `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

### Enhanced Debug Window

- **New filter**: Dropdown to filter by logger
- **Options**: All, BACKUP, EDEN, UI, CHARACTER, ROOT

**Modified file**: `UI/debug_window.py`

### Unified folder labels

- **Before**: Mixed labels ("Folder of...", "Directory of...")
- **Now**: All folder paths start with "Directory"

**Labels**:
- Directory of characters
- Directory of configuration
- Directory of logs
- Directory of armor
- Directory of Herald cookies

**Colon removal**: No more colons at end of labels (added automatically by QFormLayout)

**Localization**: Complete translations in EN, FR, DE

**Modified files**: `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Path beginning display

- **Before**: Cursor at beginning but text aligned to end (displayed "...Configuration/" in QLineEdit)
- **Now**: `setCursorPosition(0)` applied to all path fields
- **Result**: Display beginning of path (e.g.: "d:\Projects\Python\..." instead of "...Configuration/")

**Modified file**: `UI/dialogs.py` - Method `update_fields()`

### Robust diagnostic system for unexpected stops

- **Global exception handler**: Captures and logs all unhandled exceptions
- **System signal handler**: Detects SIGTERM, SIGINT and other OS interruptions
- **Always-active CRITICAL/ERROR logging**: Even with debug_mode = OFF, errors are recorded
- **Startup tracing**: Records time (ISO 8601), Python version, active threads
- **Shutdown tracing**: Records exactly when and how app stops
- **Exit code**: Displays code returned by Qt event loop

**Modified files**: `main.py`, `Functions/logging_manager.py`

### 🎛️ Herald Button Controls

- **Buttons**: "Refresh" and "Herald Search" automatically disabled
- **Disable conditions**:
  - When no cookie is detected
  - When cookies are expired
- **Synchronization**: Button state synchronized with connection status
- **User message**: Clear - "No cookie detected"

**Logic**: If `cookie_exists()` returns False or cookies invalid → buttons disabled

**Modified file**: `UI/ui_manager.py` - Function `update_eden_status()`

### Automatic save system on character updates

- **Problem**: When modifying existing character (rank, info, armor, skills) or Herald update, no save was triggered
- **Solution**: Integration of automatic backups with descriptive reason at all modification points

**Covered points**:
- Herald update after confirmation (main.py)
- Automatic rank modification (auto_apply_rank)
- Manual rank modification (apply_rank_manual)
- Basic info modification (save_basic_info)
- Armor/skills modification (CharacterSheetWindow)
- Massive import/update (import dialog)

**Backup type**: `backup_characters_force(reason="Update")` → MANUAL (bypass daily limit)

**Filename**: `backup_characters_YYYYMMDD_HHMMSS_Update.zip`

**Generated logs**: Each modification generates visible logs with `[BACKUP_TRIGGER]` tag:

```
[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip
```

**Result**: Each character modification automatically creates backup with descriptive reason and visible logs

**Modified files**: `main.py`, `UI/dialogs.py`

**Documentation**: `Documentations/BACKUP_DEBUG_GUIDE.md` updated with new scenarios

---

## 🎨 Interface Improvements

### Column configuration

- All 12 columns (0-11) correctly configurable
- Resize mode and visibility functional
- Configuration menu aligned with TreeView

### Unified labels

- All folder paths start with "Directory"
- Removal of unnecessary colons
- Consistent and professional interface

### Optimized path display

- Beginning of paths visible (no "...")
- Cursor at beginning of fields
- Better readability for user

### Realm sorting

**Problem**: The Realm column did not allow sorting by clicking the header

**Solution**:
- Added custom `RealmSortProxyModel`
- Implementation of `lessThan()` for column 1 (Realm)
- Use of `Qt.UserRole + 2` to store sorting data
- Proxy intercepts sorting and uses realm name

**Modified files**:
- `Functions/tree_manager.py`: Added `RealmSortProxyModel` class
- Import of `QSortFilterProxyModel` from `PySide6.QtCore`
- Proxy configuration in `__init__()`: `self.proxy_model.setSourceModel(self.model)`

**Result**:
- ✅ Functional alphabetical sorting (Albion → Hibernia → Midgard)
- ✅ Realm icons always displayed (without text)
- ✅ Existing delegate preserved (`CenterIconDelegate`)

### Herald URL column width

**Problem**: Herald button was crushed in too narrow URL column

**Solution**:
- Minimum width of 120px set for column 11 (URL)
- Applied in `apply_column_resize_mode()` after `ResizeToContents`

**Code**:
```python
# Set minimum width for URL column (11)
self.tree_view.setColumnWidth(11, 120)
```

**Result**:
- ✅ Herald button perfectly visible
- ✅ Comfortable space for interaction
- ✅ No impact on other columns

### Proxy model index mapping for character operations

**Problem**: After sorting by realm (or any column), character operations showed/deleted/opened wrong character
- Delete confirmation showed different character name
- Opening character sheet opened wrong character
- Herald update targeted wrong character

**Root cause**: With `QSortFilterProxyModel`, TreeView indices (sorted view) don't match source model indices (storage). Operations were using proxy indices directly on source model.

**Solution**: Use `mapToSource()` to translate proxy indices to source indices before accessing model data

**Modified methods**:
- `get_selected_character()` in `tree_manager.py` - Used by delete, rename, duplicate operations
- `open_character_sheet()` in `character_actions_manager.py` - Double-click to open character sheet
- `update_character_from_herald()` in `main.py` - Right-click menu to update from Herald

**Code example**:
```python
# Before (incorrect with proxy model):
row = indexes[0].row()
name_item = self.model.item(row, 2)

# After (correct with proxy model):
proxy_index = indexes[0]
source_index = self.proxy_model.mapToSource(proxy_index)
row = source_index.row()
name_item = self.model.item(row, 2)
```

**Result**:
- ✅ Delete confirms correct character
- ✅ Character sheet opens correct character
- ✅ Herald update targets correct character
- ✅ All operations work correctly with any sorting

### Character sheet Save button behavior

**Improvement**: Save button no longer closes the character sheet window automatically

**Before**: Clicking Save would save the character info and immediately close the window

**Now**: Clicking Save saves the character info and keeps the window open, allowing users to continue editing other fields

**Use case**: Users can now modify multiple fields and save them sequentially without reopening the character sheet each time

**Result**:
- ✅ More efficient workflow for multiple modifications
- ✅ Users explicitly close the window with the Close button
- ✅ Better user control over the editing session

### Herald buttons uniform design

**Improvement**: Both Herald buttons (Open in browser and Update from Herald) now have uniform size and layout

**Changes**:
- Equal width distribution using `setStretch(1, 1)` for both buttons
- Consistent minimum height of 30px for both buttons
- Improved visual balance and professional appearance

**Result**:
- ✅ Consistent button sizing in Herald section
- ✅ Better visual design and symmetry
- ✅ Enhanced user interface cohesion

### Main window layout improvements - Herald and Currency sections

**Enhancement**: Redesigned the bottom status section of the main window for better ergonomics

**Changes**:
- Split bottom section into two equal columns:
  - **Left column**: "Status Eden Herald" section (reduced to 50% width)
  - **Right column**: New "Monnaie" section with "🔜 Feature à venir" placeholder
- Reorganized Herald buttons:
  - Changed layout from vertical to horizontal
  - Reduced to emoji + text format (🔄 Actualiser, 🔍 Recherche, ⚙️ Gérer)
  - All three buttons same size (750px width × 35px height)
  - Compact with reduced font size and spacing
- Optimized dimensions:
  - Height: 35px (more compact than before)
  - Width: 750px per button (wide format for better visibility)
  - All elements aligned horizontally for consistency

**Result**:
- ✅ Better main window ergonomics and layout
- ✅ Improved space utilization
- ✅ All Herald buttons same size and visually balanced
- ✅ Preparation for future Currency feature
- ✅ More compact and efficient interface

### Character sheet layout improvements - Statistics section

**Enhancement**: Reorganized the character detail sheet for better readability and functionality

**Changes**:
- Renamed "Armor" section to "Statistics" (all 3 languages)
- Removed disabled "Resistances" button (grayed out placeholder)
- Added "🔜 Feature coming soon" text in Statistics section
- Relocated "Manage Armor" button below "Realm Rank" section
- Improved visual hierarchy and section organization

**Result**:
- ✅ Clearer section naming (Statistics vs Armor)
- ✅ Removed disabled UI elements for cleaner appearance
- ✅ Better visual flow with button placement
- ✅ Placeholder indicates future features clearly
- ✅ More intuitive character sheet layout

---

## 🐛 Bug Fixes - PyInstaller .exe Stability

### Fix: PyInstaller noconsole crash - sys.stderr/stdout None handling

**Issue**: Application crashed on startup with `AttributeError: 'NoneType' object has no attribute 'flush'`

**Root cause**: When PyInstaller compiles the application in `--noconsole` mode (no Windows console), `sys.stderr` and `sys.stdout` are automatically set to `None`. The code was calling `sys.stderr.flush()` without checking if `sys.stderr` existed, causing immediate crash.

**Affected locations**:
- `main.py` - Global initialization
- `Functions/backup_manager.py` - Line 30 in `__init__()`
- `UI/dialogs.py` - 10+ occurrences in various dialogs

**Solution implemented**:
```python
# Fix for PyInstaller --noconsole mode: sys.stderr/stdout can be None
if sys.stderr is None:
    sys.stderr = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')
if sys.stdout is None:
    sys.stdout = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')
```

**Result**:
- ✅ Application starts successfully in `--noconsole` mode
- ✅ No more `NoneType` crashes
- ✅ Logs still written correctly to files
- ✅ .exe fully functional

**Files modified**: `main.py`, `backup_manager.py`, `dialogs.py`

### Fix: Prevent silent crash during Herald connection test

**Issue**: The .exe application crashed silently (without logs) during Herald Eden connection verification. No error messages, no logs, no traceback - complete silent crash.

**Root causes identified**:
1. **Selenium import** could fail in PyInstaller .exe without proper logging
2. **Driver initialization** could return `None` and cause crash in `driver.quit()`
3. **Uncaught exceptions** in `EdenStatusThread` thread crashed the entire process
4. **No complete traceback** for debugging errors

**Vulnerable code path**:
- `cookie_manager.test_eden_connection()` - Main test method
- `ui_manager.EdenStatusThread.run()` - Background verification thread
- Selenium WebDriver initialization and cleanup

**Solutions implemented**:

**In `cookie_manager.py`**:
- Initialize `driver = None` at method start for safe cleanup
- Separate `try-except` for Selenium imports with explicit error messages
- Check `if not driver` before any driver operations
- Protected `finally` block with `if driver:` before `driver.quit()`
- Complete logging with `traceback.format_exc()` for debugging
- Fixed indentation in debug file save block

**In `ui_manager.py`**:
- Global `try-except` in `EdenStatusThread.run()`
- Complete exception logging with traceback
- Emit error signal instead of crashing
- UI remains responsive even on error

**Enhanced error handling structure**:
```python
driver = None  # Safe initialization
try:
    # Separated import with specific error handling
    try:
        from selenium import webdriver
    except ImportError as e:
        # Log and return structured error
        
    # Driver initialization
    driver, browser = self._initialize_browser_driver(...)
    if not driver:
        # Early return with error message
        
    # Selenium operations...
    
except Exception as e:
    # Complete traceback logging
    traceback_details = traceback.format_exc()
    logger.error(f"CRASH: {e}\n{traceback_details}")
    
finally:
    # Safe cleanup
    if driver:
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Driver cleanup error: {e}")
```

**Result**:
- ✅ No more silent crashes
- ✅ All exceptions logged to `Logs/debug.log`
- ✅ Clear error messages for users
- ✅ Application remains stable even if Herald test fails
- ✅ Complete traceback available for debugging
- ✅ Thread crashes don't kill the entire application

**Files modified**: `cookie_manager.py` (117 lines changed), `ui_manager.py`

**Testing**: Validated in compiled .exe with various error scenarios (no browser, network issues, invalid cookies)

### Fix: Backup logging errors - proper error messages in logs

**Issue**: Backup logs showed meaningless literal strings instead of actual error messages:
```
2025-11-03 14:14:28 - BACKUP - ERROR - INFO - error_msg
2025-11-03 14:20:18 - BACKUP - ERROR - INFO - error_msg
```

**Root cause**: The code was logging string literals `"error_msg"` and `"success_msg"` instead of the actual variable contents. Additionally, f-string formatting was malformed with escaped quotes.

**Problematic code**:
```python
# Lines 185, 223 - Literal strings logged instead of variables
self.logger.error("error_msg", extra={"action": "INFO"})
self.logger.info("success_msg", extra={"action": "INFO"})

# Line 200-202 - Malformed f-strings
self.logger.info("Creating compressed backup: {os.path.basename(backup_file)}\", action=", ...)
```

**Fixed code**:
```python
# Proper variable logging with log_with_action
log_with_action(self.logger, "error", error_msg, action="CHECK")
log_with_action(self.logger, "info", success_msg, action="SUCCESS")

# Correct f-string formatting
log_with_action(self.logger, "info", f"Creating compressed backup: {os.path.basename(backup_file)}", action="ZIP")
```

**Changes made**:
- **Line 185**: Use `log_with_action()` with actual `error_msg` variable instead of literal string
- **Line 200**: Fixed f-string formatting for compressed backup message
- **Line 202**: Changed action from `ZIP` to `COPY` for uncompressed backups (proper categorization)
- **Line 215**: Use `log_with_action()` with actual `success_msg` variable instead of literal string
- **Line 223**: Use `log_with_action()` with actual `error_msg` variable instead of literal string
- Proper action tags: `CHECK`, `ZIP`, `COPY`, `SUCCESS`, `ERROR`, `RETENTION`

**Result**:
- ✅ Clear error messages in logs: `BACKUP - ERROR - CHECK - Characters folder not found`
- ✅ Success messages show actual filenames: `BACKUP - INFO - SUCCESS - Backup created: backup_characters_20251106_153045_Delete.zip`
- ✅ All backup operations fully traceable with meaningful log messages
- ✅ Proper action categorization for easier debugging
- ✅ No more meaningless "error_msg" or "success_msg" literals in logs

**Files modified**: `backup_manager.py` (6 lines changed)

**Impact**: This fix makes it much easier to debug backup issues by providing clear, actionable error messages instead of placeholder text.

---

## 🧹 Repository Cleanup

- **Deletion of 13 temporary debug scripts**
- **Deletion of 3 debugging HTML files**
- **Clean and maintainable repository**
- **Performance optimization**

**Deleted files**:
- analyze_search_structure.py
- debug_comparison.py
- debug_herald_content.py
- debug_search_html.py
- debug_test_connection.py
- save_search_html.py
- show_cookies.py
- test_direct_search.py
- test_full_flow.py
- test_herald_detection.py
- test_identical_flow.py
- test_load_cookies_msg.py
- test_simple.py
- debug_herald_page.html
- debug_test_connection.html
- search_result.html

---

## 📚 Documentation

### Cleanup and reorganization of CHANGELOG system

- **Old system**: Monolithic CHANGELOGs in `Documentation/` mixing all versions (difficult to navigate)
- **New system**: Hierarchical structure in `Changelogs/` with clear version and language separation

**Created structure**:
- `Changelogs/Full/`: Detailed CHANGELOGs (~200+ lines) for v0.106, v0.104 and earlier versions
- `Changelogs/Simple/`: Concise lists for quick navigation of all versions (v0.1 to v0.106)
- Trilingual support: EN, FR, DE for each file

**Centralized access**: New `CHANGELOG.md` at root with index and navigation to all versions

**Old content**: Monolithic CHANGELOGs removed from `Documentation/`

**Created files**: 27+ files in total (6 Full + 21 Simple)

**Result**: Much clearer and more maintainable system for finding changes by version and language

---

## 📊 Statistics

- **Code lines added**: ~1000+ (log_source_editor.py: 975 lines)
- **Modified files**: 12 files
- **Created files**: 2 files (log_source_editor.py, log_editor_config.json)
- **Tagged logs**: 46+ in backup_manager.py, 52+ in eden_scraper.py
- **Standardized actions**: 20+ different actions
- **Tests performed**: Scanning, filtering, editing, saving validated

---

## 🔗 Modified Files

- `main.py`
- `UI/dialogs.py`
- `UI/ui_manager.py`
- `UI/debug_window.py`
- `Functions/cookie_manager.py`
- `Functions/eden_scraper.py`
- `Functions/tree_manager.py`
- `Functions/logging_manager.py`
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`
- `Documentations/BACKUP_DEBUG_GUIDE.md`

---

## 📊 Overall Impact

✅ **More intuitive and fluid import workflow** - No need to delete/re-import existing character

✅ **Transparent stats update from Herald** - Characters automatically update

✅ **Clean error handling with detailed report** - Number of creations, updates and errors

✅ **Increased cookie management flexibility** - Customizable paths for scraping

✅ **Complete application portability** - Centralized configuration without __file__ dependencies

✅ **Ability to diagnose unexpected stops** - Detailed logs of all critical events

✅ **Consistent and coherent interface** - Unified labels and optimal path display

✅ **Automatic save on modifications** - Each character modification creates a backup with visible logs

---

## 🔄 Migration

**No migration required** - This version is 100% backward compatible with v0.105

---

## 🐛 Known Bugs

No known bugs to date.

---

## 📝 Development Notes

- The Log Source Editor is a development tool, not included in main application
- The tool greatly facilitates logging system maintenance and improvement
- Unified logging format allows better analysis and debugging
- Standardized actions facilitate filtering and log searching
