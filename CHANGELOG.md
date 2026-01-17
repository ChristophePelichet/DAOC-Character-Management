# 📋 Changelog - DAOC Character Management

## v0.110

### ✨ Features

**Models Overview Gallery - Image Browser & Filter System**
- New Models Overview Gallery accessible from Tools menu (🖼️ icon)
- Browse and filter model thumbnails in interactive grid layout (5-column responsive grid)
- Filter by Type (armor, weapons, mobs, decorations, misc models, etc.)
- Filter by SubType (arms, feet, hands, legs, torso, shields for armor; specific types for other categories)
- Search by Model ID with partial matching capability
- Automatic metadata discovery from Img/ directory structure with hierarchical indexing
- Dynamic filter population based on available models in system
- Display model count statistics and real-time result updates
- Support for multiple image formats (JPG, PNG, WebP) with automatic fallback handling
- Professional 5-column grid layout with hover effects and image scaling
- Error handling with user-friendly messages in all 3 supported languages (EN, FR, DE)

**Architecture & Code Quality**
- Domain-driven naming convention: `model_gallery_*` function prefix for all gallery operations
- UI/Functions coupling convention: `ui_model_gallery_*` paired files for related UI components
- Clean separation of concerns: Functions (business logic) vs UI (presentation layer)
- Qt Signal/Slot based component communication with zero coupling
- PEP8 compliant code with comprehensive English docstrings
- All UI strings use `lang.get()` for internationalization (no hardcoded text)
- Type-safe `ModelThumbnail` dataclass for thumbnail representation
- Comprehensive error handling with try/catch and logging

## v0.109

### 🐛 Bug Fixes

**Language Selection & About Dialog Translation**
- Fixed About and Credits dialogs not translating based on selected language
- Implemented full multilingual support (FR/EN/DE) for all dialog elements

**Herald Search Dialog - Realm Combobox**
- Fixed realm combobox text truncation where "Midgard" was displayed as "Mi...rd"

**Herald Search Dialog - Realm Icons in PyInstaller**
- Fixed missing realm icons in compiled executable
- Icons now load correctly from bundled resources using get_resource_path()
- Realm logos display properly in Herald search dialog (Albion red, Midgard blue, Hibernia magenta)

**Herald Search Dialog - Critical UI Freeze Bug**
- Fixed 4+ second UI freeze when closing Herald search dialog after performing a search

**Herald Search Dialog - Invalid Character Bug (Filename)**
- Fixed JSON error when searching for character names containing special characters (* ? " < > | : \ /)

**Debug Settings Panel - Info Text Removal**
- Removed redundant debug mode information text from Settings > Debug panel
- Cleaned up language files (removed hardcoded info messages)

**Eden Debug Window - Translation Support**
- Added translation support for Eden Debug window (title, buttons, labels)
- Implemented `retranslate_ui()` method for dynamic language switching
- Textures now respect user language preference (FR/EN/DE)
 
### ✨ Features

**Sound Control System**
- Global on/off toggle for all message dialogs in Settings > Audio Settings
- Default enabled for backward compatibility
- Complete sound suppression when disabled (no system beeps)

**Armor Resistances Table Viewer**
- Interactive table viewer for armor resistance values across all DAOC realms (Albion, Midgard, Hibernia)
- Tab-based realm navigation with realm logo icons
- Configurable display modes: compact (5 armor types) or detailed (16+ rows with classes)
- Sortable columns (click headers to sort ascending/descending with numeric awareness)
- Color-coded resistance values (Green = Resistant, Orange = Neutral, Red = Vulnerable)
- Settings integration for persistent configuration

**Armory Template Preview - Copper to Platinum Price Conversion**
- Implemented automatic conversion of raw copper prices to human-readable Platinum (PP) format

**All-Templates View & Template Management**
- New multi-realm view with tabs (Albion, Hibernia, Midgard) for browsing all templates
- Template editing dialog with real-time filename preview
- Column sorting and width persistence in template table
- Optional season inclusion in template filenames

**Herald Search Dialog Window Controls**
- Custom title bar with minimize (−) and maximize (□) buttons
- Toggle maximize button shows window state (□ = normal, ▢ = maximized)
- Flexible window sizing for better workspace management
- Visual feedback with state indicator changes

### 🧹 Code Quality - Ruff PEP 8 Cleanup

**Compliance Status**
- All modified files validated with ruff (21 files checked)
- 26 initial violations identified and resolved
- Final status: ✅ 0 errors - All files PEP 8 compliant

**Corrections Applied**
- Removed 21 unused imports (QMessageBox, Optional, QTextEdit, QSpinBox, QFont, Qt, QSize)
- Removed 5 unused variables (price, old_name, old_realm, items_updated, logging)
- Added missing SilentMessageBox import in character_herald_scrapper.py

### ♻️ Code Refactoring - dialogs.py Module Extraction & UI Helper Systems (Complete)

**Extraction Scope**: Extract business logic from `UI/dialogs.py` into dedicated domain-specific modules for improved maintainability, testability, and code reuse. Consolidate input validation and file dialogs into centralized helper modules.

**19 Phases Completed** - Extracted 65+ functions into 19 new modules, removed ~3950+ lines from dialogs.py:

1. **Phase 1**: Template Parser (`Functions/template_parser.py` - 1392 lines)
   - Template format detection, parsing (Loki/Zenkcraft), price lookup, item formatting
   - Returns tuple: (formatted_content, items_without_price) for complete workflow integration
   
2. **Phase 2**: Item Price Manager (`Functions/items_price_manager.py` - 205 lines)
   - Template price sync with database, missing price detection
   
3. **Phase 3**: Ruff Compliance Cleanup
   - Fixed 19 E722, 2 F841, 1 F823, 4 pre-extraction errors → 0 errors
   
4. **Phase 4**: Character Validator (`Functions/character_validator.py` - 280 lines)
   - Class/race retrieval, combo population, realm/class/race change handlers
   
5. **Phase 5**: Character Realm Rank Calculator (`Functions/character_rr_calculator.py` - 209 lines)
   - Valid level retrieval, points progression, rank calculation with realm-aware restrictions
   
6. **Phase 6**: Character Herald Scrapper (`Functions/character_herald_scrapper.py` - 422 lines)
   - Complete/RvR-only character update, stats UI updates with selective loading
   
7. **Phase 7**: Character Banner Management (`Functions/character_banner.py` - 141 lines)
   - Class banner image loading with realm/class mapping, fallback support
   
8. **Phase 8**: Herald URL Validation (`Functions/herald_url_validator.py` - 236 lines)
   - URL validation, button state management, browser opening with cookies
   
9. **Phase 9**: Armor Upload & Management (`Functions/armor_upload_handler.py` - 362 lines)
   - File upload with cross-season support, template import, file opening, deletion

10. **Phase 10**: Item Model Viewer (`Functions/item_model_viewer.py` - 167 lines)
    - Model link click handling, item model display with multi-source search, error handling

11. **Phase 11**: Character Achievement Formatter (`Functions/character_achievement_formatter.py` - 256 lines)
    - Achievements display formatting with 2-column layout, progress tracking, tier display

12. **Phase 12**: UI Message Helper (`UI/ui_message_helper.py` - 195 lines)
    - Centralized QMessageBox handling with automatic translation and logging
    - 5 functions: success, error, warning, confirmation, info_with_details
    - Support for dynamic parameters and plain text messages

13. **Phase 13**: UI State Manager (`UI/ui_state_manager.py` - 285 lines)
    - Centralized button state management for all dialogs
    - 5 functions: herald buttons, armor buttons, stats buttons, generic multi-button, selection handler
    - State validation with database mode checks (embedded vs. personal)
    - Intelligent tooltip management for user guidance
    - Added `is_personal_database()` method to `ItemsDatabaseManager` for database mode detection

14. **Phase 14**: UI Validation Helper (`Functions/ui_validation_helper.py` - 680+ lines)
    - Centralized input field validation across all dialogs
    - 15 core validation functions: text fields, URLs, emails, numeric fields, file paths, selections
    - 4 wrapper functions for dialog-specific validation scenarios
    - Eliminates 20+ repetitive validation patterns from dialogs.py
    - Returns consistent dict format with 'valid', 'message', and value fields
    - Zero inline validation code in dialogs.py

15. **Phase 15**: UI File Dialog Wrapper (`UI/ui_file_dialogs.py` - 140 lines)
    - Centralized QFileDialog usage for consistent file selection behavior
    - 5 wrapper functions: open file, save file, select directory, open armor file, select backup path
    - Automatic translation support via lang.get()
    - Eliminates scattered QFileDialog calls and repeated setup code
    - Zero direct QFileDialog usage in dialogs.py

16. **Phase 16**: Extended UI File Dialogs (`UI/ui_file_dialogs.py` - 280+ lines total)
    - Extended wrapper module to handle QFileDialog calls in non-dialogs.py UI files
    - 5 additional wrapper functions: open template file, select multiple files, save report, open/save log files
    - Refactored 4 UI files: template_import_dialog.py, settings_dialog.py, mass_import_monitor.py, debug_window.py
    - Centralized 13 additional QFileDialog calls from other UI modules
    - All file dialogs now use consistent lang.get() translation pattern
    - Complete elimination of direct QFileDialog imports from UI layer (except ui_file_dialogs.py)

17. **Phase 17**: Character Rename Handler (`Functions/character_rename_handler.py` - 60 lines)
    - Character renaming logic extraction with validation and persistence
    - 1 function: character_rename_with_validation() for complete rename workflow
    - Decoupled rename logic from UI layer, reusable across contexts

18. **Phase 18**: Armor Context Menu Builder (`UI/ui_context_menus.py` - 88 lines)
    - Context menu construction for armor files with standard actions
    - 1 function: ui_show_armor_context_menu() handles view, download, open, delete actions
    - Consistent menu styling and action callback pattern
    - Complete UI component extraction with thin wrapper in dialogs.py

19. **Phase 19**: Simple Getters & Setters (`UI/ui_getters.py` - 119 lines, `Functions/herald_ui_wrappers.py` - 37 lines)
    - Pure utility functions for data retrieval from UI components
    - 4 functions: ui_get_visibility_config(), ui_get_selected_category(), ui_get_selected_changes(), herald_ui_update_rvr_stats()
    - Separated UI concerns from business logic with thin wrappers

**Refactoring Statistics**:
- Total functions extracted: 65+
- Total lines extracted: ~3950+ lines
- Thin wrappers in dialogs.py: ~260 lines
- Net code reduction: ~3690 lines
- Modules created: 19 dedicated domain-specific modules
- QFileDialog calls centralized: 18 (5 in dialogs.py + 13 in other UI files)

**Quality Standards Applied**:
- ✅ Domain-driven naming conventions for all modules and functions
- ✅ PEP 8 compliant (ruff validation: 0 errors across all modules, ignoring F401/E501)
- ✅ Type hints and comprehensive docstrings (English only)
- ✅ Zero hardcoded UI strings (all use `lang.get()` with translation fallbacks)
- ✅ English-only code and comments
- ✅ Complete documentation updates (DIALOG_TECHNICAL_DOCUMENTATION.md, DIALOG_STATE_TECHNICAL_DOCUMENTATION.md, ARMORY_TECHNICAL_DOCUMENTATION.md, etc.)

### ♻️ Debug Logging System Refactoring & Organization

**Module & File Renaming**:
- `logging_manager.py` → `Functions/debug_logging_manager.py` (clarity on debug-specific purpose)
- `debug_window.py` → `UI/ui_debug_window.py` (UI naming consistency)
- `log_source_editor.py` → `Tools/Debug-Log/tools_debug_log_editor.py` (tool-specific naming prefix)
- `watch_logs.py` → `Tools/Debug-Log/tools_debug_watch_logs.py` (tool-specific naming prefix)

**Organization**:
- Created dedicated `Tools/Debug-Log/` directory for all debug utilities
- Updated 25+ imports across entire codebase to reference new module locations
- Updated all docstrings: 100% English (converted 24+ French docstrings to English)

**Documentation**:
- Consolidated 3 separate guides into comprehensive `DEBUG_TECHNICAL_DOCUMENTATION.md` (v2.0)
- Merged: DEBUG v1.0 + LOG_SOURCE_EDITOR_V0.2 + LOGGER_REALTIME_GUIDE
- Removed obsolete documentation: LOG_SOURCE_EDITOR_V0.2.md, LOGGER_REALTIME_GUIDE_FR.md
- Added: System architecture diagrams, tool reference tables, usage examples

**Code Quality**:
- ✅ 100% Ruff compliance (all debug modules verified)
- ✅ 100% English docstrings and comments
- ✅ PEP 8 adherence across all debug utilities

**Key Improvements**:
- Centralized button state management reduces scattered `.setEnabled()` calls
- Template parser returns items_without_price for accurate button state
- Database mode validation ensures buttons reflect actual capabilities
- Intelligent tooltips guide users when features are unavailable
- All validation logic consolidated in ui_validation_helper.py (zero validation code in dialogs.py)
- Consistent error messages and validation rules across all dialogs
- Complete separation of concerns: business logic extracted from UI layer

### 🐛 Bug Fixes & UI Improvements (dialogs.py Refactoring)
- **Dialog Validation Flow**: NewCharacterDialog stays open on validation errors, allowing users to correct input without losing context
  - Override dialog's `accept()` method to validate before closing
  - Invalid name/guild shows error message but keeps dialog open
  - Invalid race/class combination also keeps dialog open for correction
- **Window Controls**: Enable minimize button on CharacterSheetWindow
  - Minimize button no longer greyed out when viewing character details
  - All three window controls now functional: minimize, maximize, close
- **Settings/Eden Translation**: Complete translation system for Eden settings section
  - Translate all hardcoded French text in "Chemin des cookies" and "Chemin du cache des items" sections
  - Translate cleanup confirmation dialogs (Clean Eden, Clean Cache)
  - Translate "Ouvrir le dossier" buttons and "Stockage automatique dans" labels
  - Add 6 new translation keys in settings.herald section
  - Add cleanup confirmation messages in settings.herald section (title + message for both Eden and Cache)
  - Full FR/EN/DE support for all Eden settings UI elements
  - Fix JSON structure to prevent key duplication in language files
  - All translations use lang.get() system for dynamic language switching

---

## v0.108

### 🎉 Armory Features
- 📦 **Items Database System**: Dual-mode architecture with 227 items
  - **Read-Only Internal Database** : Pre-populated database with 227 items for all users
  - **User-Managed Personal Database** : Optional personal database with full write access
    - Toggle between internal and personal database in Settings/Armory
    - Auto-add scraped items option (configurable)
    - Import items from templates directly to personal database
    - Statistics tracking (internal vs. personal vs. user-added items)
    - Reset to internal database with automatic backup
  - Multi-realm support with automatic item detection
  - External template format support (non-Zenkcraft software)
  - 16 equipment slots parsing capability
- 🛡️ **Armor Management**: Complete armor template management system
- 📋 **Template Preview**: Full visualization with stats, resists, equipment
- 🔍 **Visual Models**: 3444 item images (weapons/armor/jewelry) with clickable 🔍 icon
- 💰 **Merchant Prices**: Automatic missing price lookup via Eden scraping
- 🏷️ **Categorization**: Category assignment (Quest/Event) for items without prices
- 📂 **Loki Template Support**: Full support for Loki template format
  - Automatic format detection (Loki vs Zenkcraft)
  - Parse stats, resists, skills, and bonuses sections
  - Filter out crafted items (with Quality:)
  - Support for all 16 equipment slots including Chest/Head

### 🚀 Performance
- ⚡ **Eden Connection Test**: 50%+ faster (7-8s → 3-4s, 10s cache)

### 🎉 Other Features
- 🌐 **Dedicated Chrome Profile**: Complete browser isolation in AppData
- 💾 **Auto Migration**: Characters/Realm/ → Characters/Season/Realm/ restructuring
- 🎨 **Purple Theme**: New violet/pink theme (based on Dracula theme)
- ⌨️ **Shortcuts**: Ctrl+N (new), Ctrl+F (Herald)

### 🧰 Improvements
- 💾 **Optimized Backup**: Cookies 10 KB instead of 50+ MB (99% reduction)
- 🔄 **Config v2**: Hierarchical structure with automatic migration
- 🎨 **Instant Theme**: Change without restart
- 📊 **Template Parser**: Refactored into 3 separate parsers with format auto-detection
- 🔍 **Items Refresh**: Single item refresh now searches new items instead of filtering existing DB
- 🐛 **Debug Options**: Config option to enable/disable Items Database HTML debug saving

### 🐛 Fixes
- 🔍 Support for 'model' + 'model_id' fields for DB compatibility
- 🪟 Non-modal model viewer window (smooth navigation)
- 🔗 Template stays visible after clicking 🔍
- 🎨 Purple theme: visible text, readable placeholder
- 🌍 Herald/Stats/Buttons translations (FR/EN/DE)
- 📝 Replace emoji prints with logging to avoid Windows encoding errors in items parser

---

### ✨ Addition (Previous Features)

**Multilingual Support for Progress Dialogs**
- 🌍 58 new FR/EN/DE translations for all progress dialogs and import messages
- 📚 Complete technical documentation with diagrams (PROGRESS_DIALOG_SYSTEM_EN.md, 1900+ lines)
- 🎯 Full 3-language support for user interface

### 📚 Documentation

**Eden Scraping Technical Documentation**
- 📝 3 detailed English documentations (2000+ lines)
- 📊 ASCII graphic flowcharts
- 💡 Practical examples and troubleshooting guides
- 🎯 Unified architecture documented

### 🐛 Fix

**Column Widths Not Saved**
- 🛡️ Manually resized columns lost on restart
- 🔧 Automatic width saving in config.json
- 🎯 Persistent column configuration between sessions

**Missing URL on Import**
- 🛡️ Fix Herald URL not saved during character import
- 🔧 Added forgotten URL fallback during SearchThread refactoring
- 🎯 Imported characters now contain their URL for auto updates

**Herald Close Crash**
- 🛡️ Fix crash when closing search window
- 🔧 Complete protection: thread stop, signal disconnect, exception handling
- 🎯 Safe close anytime without crash

**Message Formatting Error**
- 🛡️ Fix "Index out of range" crash when displaying messages
- 🔧 Migration to named parameters ({char_name}, {count}, {error})
- 🎯 Translated messages displayed correctly with dynamic values

**Herald Search Window Freeze**
- 🛡️ Fix slow close (2-3 clicks needed) + freeze after import
- 🔧 Asynchronous cleanup of threads and resources (QTimer.singleShot)
- 🎯 Instant close (<100ms), no freeze, background refresh/backup

**Untranslated Import Messages**
- 🛡️ "Import complete" messages hardcoded in French
- 🔧 6 new FR/EN/DE translation keys
- 🎯 100% multilingual Herald interface

**Inconsistent Context Menu Behavior**
- 🛡️ Context menu showed empty window, character sheet showed message
- 🎯 Uniform behavior between character sheet and context menu

### 🧰 Modification

**Herald Search Improvement**
- 🎨 New progress window with 9 detailed steps
- ✅ Visual status system: Waiting (⏺️), In Progress (⏳), Completed (✅)
- 📋 All steps remain visible with status indication
- 🔄 Automatic step updates as progress advances
- 🎯 Complete visual feedback for user
- 🔧 Refactoring wealth_manager.py to centralized `_connect_to_eden_herald()` function
- 📊 Complete CharacterProfileScraper + WealthManager documentation (CHARACTER_STATS_SCRAPER_EN.md, 2000+ lines)

**Migration to Translation System**
- 🔄 All dialog texts now automatically translated
- 🌐 4 migrated dialogs: Update stats, Update character (×2), Generate cookies
- ✅ Fully multilingual interface (FR/EN/DE)

### 🔚 Removal

**Documentation Cleanup**
- 🗑️ Deletion of 20+ obsolete files (~4000 lines)
- 🧹 Final clean and consolidated documentation

**"Check Structure" Option**
- 🛡️ Obsolete migration feature removed
- 🎯 Simplified interface, manual option removed

**Incorrect Realm Rank in Comparison**
- 🛡️ Displaying title ("Raven Ardent") instead of code (5L9) causing false changes
- 🔧 Automatic detection and recalculation from realm points
- 🎯 Correct comparison, no more false positives

**Empty Comparison Window**
- 🛡️ Window opened even without detected changes
- 🔧 Prior check + "Character already up to date" message
- 🎯 No empty window, clear message

---

# ✨ v0.107

### 🎉 Addition 

**Configurable Theme System**
- 🌓 Two available themes: Light (default) and Dark
- ⚙️ Theme selector in configuration menu
- 🔄 Instant theme change without restart

**Text Scaling System**
- 📏 Text size dropdown with 5 levels: 100%, 125%, 150%, 175%, 200%
- 🔄 Instant application without application restart
- 🎯 Base font scaling (9pt Segoe UI on Windows)
- 📐 Automatic CSS stylesheet scaling for themes
- 🖋️ Scaling of all Python inline styles (18 modified labels)

**Responsive Interface**
- 📜 Scrollable area in configuration window
- 📐 Increased minimum size: 600×500 pixels (instead of 500×400)
- 🖥️ Comfortable initial size: 700×700 pixels
- ↕️ Automatic scroll if window too small

**Version Check System**
- 🔄 Automatic check on application startup
- 📊 Current version display
- 🌐 Latest available version display (from GitHub)
- 🔘 Manual "🔄 Check" button to rerun check
- ✅ Visual indicators: ✓ green (up to date) or ✗ red (outdated)
- 🔗 Clickable download link to GitHub Releases (if update available)

**Class Banner System**
- 🖼️ Visual banners for 44 DAOC classes (Albion, Hibernia, Midgard) [©️Eden Daoc](https://eden-daoc.net/)
- 📱 Responsive design adapting to window height
- 🔄 Automatic update when changing class/realm

**Complete Herald Statistics**
- ⚔️ RvR Section: Tower Captures, Keep Captures, Relic Captures
- 🗡️ PvP Section: Solo Kills, Deathblows, Kills (with Alb/Hib/Mid realm detail)
- 🐉 PvE Section: Dragons, Legions, Mini Dragons, Epic Encounters, Epic Dungeons, Sobekite
- 💰 Wealth Section: Currency in "18p 128g 45s 12c" format
- 🏆 Achievements Section: 16 achievements displayed

**"Information" Button**
- ℹ️ Button next to "Refresh Stats" button
- 📝 Explanatory message about cumulative nature of statistics

### 🧰 Modification

**"Refresh Stats" Button**
- 🎯 Intelligent state management (grayed during Herald validation at startup)
- ⏸️ Automatic disable during Herald scraping
- 🔒 Guaranteed reactivation with `try/finally` pattern
- 📢 Detailed error messages for RvR/PvP/PvE/Wealth

**Currency Display**
- 🔤 Font size reduced from 11pt to 9pt (better visual harmony)
- 💪 Bold style preserved

### 🐛 Fix

**Error Messages**
- 📝 Fix incomplete error messages (added missing PvE and Wealth)
- 📢 Display of ALL errors (RvR/PvP/PvE/Wealth)

**Currency Formatting**
- 🔢 Fix TypeError with `f"{money:,}"` on string
- 💱 Use of `str(money)` for direct display

**Herald Connection Test**
- 💥 Fix crash during connection errors
- 🔐 Added `finally` block to close driver properly

**Statistics Display**
- 📱 Fix RvR/PvP/PvE/Wealth/Achievements sections truncated on small screens
- 📏 Fix full height of statistics sections (removed QScrollArea)
- 📄 Added `setWordWrap(False)` on PvP labels to avoid line wrap

**Debug Files**
- 🗑️ Deletion of automatically created HTML files
- 📝 Added to .gitignore

### 🔚 Removal

No features removed in this version.

---

# ✨ v0.106 - 2025-11-07

### 🎉 Addition

**Logging System**
- 📋 Unified format: `LOGGER - LEVEL - ACTION - MESSAGE`
- 🏷️ BACKUP Logger: all backup module logs tagged
- 🏷️ EDEN Logger: all Eden scraper logs tagged
- 🎯 Standardized actions for each module
- 🔍 Improved debug window with logger filter

**Eden Cookies Backup**
- 📅 Automatic daily cookie backup at startup
- 📂 Dedicated "Eden Cookies" section in backup window
- ⚙️ Identical options to Characters: compression, storage limit
- 💾 "Backup Now" button for immediate forced backup
- 📁 "Open Folder" button for direct access
- 🔄 Automatic refresh after backup
- 📊 Display of backup count and last backup date

**Interface**
- 🖥️ Main window layout redesign with Currency section
- 📏 Herald status bar optimizations (750px × 35px buttons)
- 📋 Character sheet redesign (Statistics rename, Resistances removal)
- 🔧 "Manage Armor" button relocation

### 🧰 Modification

**Backup Module**
- 🏷️ Character name included in backup files
- 📝 Format: `backup_characters_20251107_143025_Update_Merlin.zip`
- 📝 Multiple: `backup_characters_20251107_143025_Update_multi.zip`
- 🔍 Immediate character identification
- 📊 Improved logs: INFO instead of ERROR on first startup
- ✅ Clear error message: "No characters to backup"
- 🏷️ 46+ logs tagged with clear actions

**Herald Performance**
- ⚡ Herald timeout reduction by 17.4% (-4.6 seconds per search)
- 🎯 Character search: 26.5s → 21.9s (-4.6 seconds)
- ✅ 25/25 successful tests (100% stable, 0 crash)

**Interface**
- 📏 Herald URL column width optimized (120px minimum)
- 🔘 Uniform Herald button size in sheet
- 🖥️ Backup window enlarged (1400x800)
- 📂 Side-by-side layout: Characters and Eden Cookies

**Configuration**
- 🎯 Default season: S3 instead of S1
- ⚙️ Manual columns: Manual management enabled by default
- 📁 Conditional logs: Created ONLY if debug_mode enabled

### 🐛 Fix

**Eden Herald**
- 💥 Fix brutal crash during Herald search errors
- 🔐 Clean WebDriver close in all error paths
- 📝 Full stacktrace logging for diagnosis
- ✅ Stability test: 25/25 successful searches (100% stable)
- 🛠️ Automated test script for continuous validation
- 📁 Cookie path correction (PyInstaller fix)
- 🔄 Auto-update during character import
- 📂 Configurable Herald cookies folder
- 🔐 Herald connection test protection
- 📦 Selenium import error handling
- 🔒 Driver cleanup protection

**Interface**
- 🔧 Column configuration correction (12 columns)
- 🏷️ Label unification ("Directory")
- 📊 Path start display
- 🔍 Robust diagnostic system for unexpected stops
- ↕️ Functional realm sorting (added RealmSortProxyModel)
- 🗺️ Proxy model mapping for sorted operations
- ✅ Save button in sheet no longer closes window

**Code Quality**
- 🧹 Code cleanup: 74 excessive blank lines removed
- 📦 Reduced exe size: Estimated -1 to 2 MB (-2 to 4%)
- 📋 Corrected version: "About" window now displays v0.106
- 🔧 Migration fix: No more "migration_done" error
- 💻 67 production files modified for optimal quality
- 🔒 sys.stderr/stdout None handling
- 🧵 Thread exception capture
- 📝 Full traceback logging
- ✅ Backup logging errors corrected

### 🔚 Removal

No features removed in this version.

---

# ✨ v0.105 - 2025-11-01

### 🎉 Addition

**Eden Scraper**
- 🌐 Complete Eden Scraper module
- 🍪 Cookie manager with GUI interface
- 📥 Bulk character import
- 🌐 Multi-browser support (Chrome, Edge, Firefox)
- 🔧 3-tier system ChromeDriver
- ⚙️ Browser configuration in settings
- 📊 Herald status bar
- 💬 Herald import dialog
- 🐛 Eden debug window
- 🎨 Log syntax highlighting
- 🔄 Character update from Herald
- 📝 Dedicated Eden logger

**Interface**
- 🎯 Automatic default season assignment
- 🖱️ Context menu for quick import (right-click)
- ❓ Integrated help system with Markdown
- ✅ Automatic JSON structure validation
- 🔍 Manual structure check (Help menu)

### 🧰 Modification

No major modifications in this version.

### 🐛 Fix

**Eden Scraper**
- 🔧 Fix changing class when modifying rank
- 📝 Herald data normalization
- 💾 Fix saving Herald modifications
- 🔍 Optimized browser detection

### 🔚 Removal

No features removed in this version.

---

# ✨ v0.104 - 2025-10-25

### 🎉 Addition

**Complete Refactoring**
- 🔧 Complete refactoring into 3 managers
- ⚡ Performance optimization (-22% loading)
- 📉 Code reduction (-61% main.py)
- 🗂️ New Season/Realm structure

**Automatic Migration**
- 🔄 Automatic migration with ZIP backup
- 💬 Trilingual confirmation popup
- 📦 Compressed backups (70-90% savings)
- ✅ Automatic integrity check
- ↩️ Automatic rollback on error
- 📝 Complete JSON validation

**Interface**
- 📋 Class and Race columns
- 👑 Realm Rank with dropdowns
- 💾 Automatic rank saving
- 📂 Traditional Windows menu

**Documentation**
- 🧹 Project cleanup script
- 📚 MIGRATION_SECURITY documentation
- 🧪 Migration test scripts
- 📖 Complete documentation reorganization

### 🧰 Modification

No major modifications in this version.

### 🐛 Fix

No bugs fixed in this version.

### 🔚 Removal

No features removed in this version.

---

# ✨ v0.103 - 2025-10-20

### 🎉 Addition

**Races and Classes**
- 🧬 Race and class selection
- 🔍 Dynamic race/class filtering
- ✅ Automatic race/class validation
- 🌍 Specialization translations (FR/EN/DE)
- 📊 Complete data system (44 classes, 18 races)
- 📚 188 translated specializations
- 🎮 Eden support (adapted classes)

**Interface**
- 📏 Column width management
- 🤖 Automatic/manual mode for columns

### 🧰 Modification

No major modifications in this version.

### 🐛 Fix

No bugs fixed in this version.

### 🔚 Removal

No features removed in this version.

---

# ✨ v0.102 - 2025-10-15

### 🎉 Addition

**Multi-Server**
- 🌐 Server column restoration (Eden/Blackthorn)
- ⚙️ Default server configuration
- 📋 Server dropdown in character sheet
- 👁️ Server column hidden by default

**Rename**
- ✏️ Simplified rename
- ⚡ Quick rename (Enter key)

### 🧰 Modification

No major modifications in this version.

### 🐛 Fix

- 💬 Simplified error messages
- 🔧 RealmTitleDelegate correction

### 🔚 Removal

No features removed in this version.

---

# ✨ v0.101 - 2025-10-10

### 🎉 Addition

**Windows Menu Interface**
- 📂 File menu (New character, Settings)
- 👁️ View menu (Columns)
- ❓ Help menu (About)
- 🌍 Menu translations (FR/EN/DE)

**Editing**
- ✏️ Realm, level, season, page, guild editing
- 🔄 Automatic move on realm change
- 🖱️ Rename via context menu

**Optimization**
- ⚡ Icon loading optimization
- 🎨 Interface simplification

### 🧰 Modification

- 🌐 Server automatically set to "Eden"

### 🐛 Fix

No bugs fixed in this version.

### 🔚 Removal

- ❌ Server column removal

---

# ✨ v0.1 - 2025-10-01

### 🎉 Addition

**Base Features**
- 👥 Complete character management
- ➕ Create, edit, delete, duplicate
- 👑 Realm rank system
- 🌍 Multilingual interface (FR/EN/DE)
- 📋 Column configuration
- 🐛 Debug mode with integrated console
- 🔄 Bulk actions
- 🏰 Organization by realm (Albion, Hibernia, Midgard)
- 🌐 Multi-server support
- 📅 Season system
- 🔗 Web data extraction
- 🖥️ PySide6 interface
- 💾 Configuration persistence

### 🧰 Modification

No modifications (initial version).

### 🐛 Fix

No bugs fixed (initial version).

### 🔚 Removal

No features removed (initial version).
