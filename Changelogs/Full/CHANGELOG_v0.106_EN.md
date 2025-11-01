# CHANGELOG v0.106 - Eden Scraping & Auto-Update Fixes

**Date** : 2025-11-01  
**Version** : 0.106

## 🐛 Fixes

### Eden cookies save path (PyInstaller fix)
- **Problem** : Cookies were not being saved to the `Configuration/` folder by default
- **Cause** : `CookieManager` was using `Path(__file__).parent.parent` which caused issues with PyInstaller
- **Solution** : Using `get_config_dir()` from `config_manager.py` for global consistency
- **Result** : Cookies are now correctly saved in the folder defined by `config_folder` in `config.json`
- **Compatibility** : Works correctly with compiled application and normal execution
- **Modified file** : `Functions/cookie_manager.py` (line 22-34)

### Column configuration fixed
- **Problem 1** : The Herald URL column (index 11) was not included in resize mode (`range(11)` instead of `range(12)`)
- **Problem 2** : The order of Class and Level columns was reversed in the configuration menu
- **Problem 3** : Visibility mapping used incorrect order and URL column was missing
- **Solution** :
  * `apply_column_resize_mode()` now correctly handles all 12 columns
  * Configuration menu order aligned with TreeView (Class before Level)
  * `column_map` fixed with correct order and URL column inclusion
- **Impact** : All 12 columns (0-11) are now correctly configurable for resize mode and visibility
- **Modified files** : `Functions/tree_manager.py`, `UI/dialogs.py`

## ✨ Improvements

### Auto-update on character import
- **Before** : If character exists → Error "character already exists"
- **Now** : If character exists → Automatic update from Herald 🔄
- **Preserved data** : name, realm, season, server, custom fields
- **Updated data** : class, race, guild, level, realm_rank, realm_points, url, notes
- **Detailed report** : Shows number of creations, updates and errors
- **Use case** : Ideal for keeping characters up-to-date via Herald import
- **Modified file** : `UI/dialogs.py` - Function `_import_characters()` (line 2422)

### Configurable Herald cookies folder
- **New option** : Settings window → "Herald Cookies Directory"
- **Feature** : Specify a custom folder for saving Eden scraping cookies
- **Interface** : "Browse..." button to facilitate folder selection
- **Default value** : `Configuration/` folder (behavior preserved if not configured)
- **Portable application** : Paths are absolute, no dependency on `__file__`
- **Persistence** : Configuration is saved in `config.json` under key `"cookies_folder"`
- **Fallback logic** : If `cookies_folder` is not set, uses `config_folder` (ensures backward compatibility)
- **Modified files** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

### Unified folder labels
- **Before** : Mixed labels ("Folder of...", "Directory of...")
- **Now** : All folder paths start with "Directory"
- **Labels** :
  * Character Directory
  * Configuration Directory
  * Log Directory
  * Armor Directory
  * Herald Cookies Directory
- **Removed colons** : No more colons at the end of labels (added automatically by QFormLayout)
- **Localization** : Complete translations in EN, FR, DE
- **Modified files** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Improved path display
- **Before** : Cursor was at start but text was aligned to end (displaying "...Configuration/" in QLineEdit)
- **Now** : `setCursorPosition(0)` applied to all path fields
- **Result** : Beginning of path is visible (e.g., "d:\Projects\Python\..." instead of "...Configuration/")
- **Modified file** : `UI/dialogs.py` - Method `update_fields()` (line 1260+)

### Robust diagnostic system for unexpected crashes
- **Global exception handler** : Captures and logs all unhandled exceptions
- **System signal handler** : Detects SIGTERM, SIGINT and other OS interruptions
- **CRITICAL/ERROR logging always active** : Even with debug_mode = OFF, errors are recorded
- **Startup tracing** : Records time (ISO 8601), Python version, active threads
- **Shutdown tracing** : Records exactly when and how the app stops
- **Exit code** : Shows the code returned by the Qt event loop
- **Modified files** : `main.py`, `Functions/logging_manager.py`

### CHANGELOGs system cleanup and reorganization
- **Old system** : Monolithic CHANGELOGs in `Documentation/` mixing all versions (difficult to navigate)
- **New system** : Hierarchical structure in `Changelogs/` with clear separation by version and language
- **Structure created** :
  - `Changelogs/Full/` : Detailed CHANGELOGs (~150 lines) for v0.106, v0.104 and earlier versions
  - `Changelogs/Simple/` : Concise lists for quick navigation of all 7 versions (v0.1 to v0.106)
  - Tri-lingual support : FR, EN, DE for each file
- **Centralized access** : New `CHANGELOG.md` at root with index and navigation to all versions
- **Old content** : Monolithic CHANGELOGs removed from `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)
- **Files created** : 27 files total (6 Full + 21 Simple)
- **Result** : Much clearer and more maintainable system for finding changes by version and language

## 📊 Overall Impact

✅ **More intuitive and fluid import workflow** - No need to delete/reimport existing character  
✅ **Transparent stats update from Herald** - Characters automatically update  
✅ **Proper error handling with detailed report** - Number of creations, updates and errors  
✅ **Increased flexibility for cookie management** - Customizable paths for scraping  
✅ **Complete application portability** - Centralized configuration without __file__ dependencies  
✅ **Ability to diagnose unexpected crashes** - Detailed logs of all critical events  
✅ **Consistent and coherent interface** - Unified labels and optimal path display  

## 🔗 Modified Files

- `main.py`
- `UI/dialogs.py`
- `Functions/cookie_manager.py`
- `Functions/tree_manager.py`
- `Functions/logging_manager.py`
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`
