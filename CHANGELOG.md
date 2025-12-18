# 📋 Changelog - DAOC Character Management

## v0.109

### ♻️ Code Refactoring - dialogs.py Module Extraction

**Overall Scope**: Extract business logic from `UI/dialogs.py` into dedicated domain-specific modules for improved maintainability, testability, and code reuse.

#### Phase 1, 2, 3 & 4: Template, Item Price, Ruff Cleanup & Character Validator

**Extraction Scope**: 4 phases completed, extracting 15+ functions from `UI/dialogs.py` into dedicated domain-specific modules

- **Phase 1**: Template Parser Module (`Functions/template_parser.py` - 1392 lines)
  - Extracted 8 core functions for equipment template parsing
  - Supports Loki and Zenkcraft format detection with automatic fallback
  - Multi-source price lookup with database-metadata-category fallback

- **Phase 2**: Item Price Management Module (`Functions/items_price_manager.py` - 205 lines)
  - Extracted 2 core functions for template price synchronization
  - Template price sync with items database (single source of truth)
  - Missing item price detection across database and metadata

- **Phase 3**: Ruff Compliance Cleanup
  - Fixed 19 E722 errors (bare except → except Exception)
  - Fixed 2 F841 errors (unused variables removal)
  - Fixed 1 F823 error (missing imports)
  - Fixed 4 pre-extraction errors (QSlider import, f-string, unused imports)
  - **Result**: `dialogs.py` now 100% ruff compliant (0 errors)

- **Phase 4**: Character Validator Module (`Functions/character_validator.py` - 280 lines)
  - Extracted 5 core functions for character class/race validation
  - Realm-aware class and race filtering with cascade updates
  - Multi-language display support (EN/FR/DE) for all options
  - Functions: `character_get_classes_for_realm()`, `character_get_races_for_class()`, 
    `character_populate_classes_combo()`, `character_populate_races_combo()`,
    `character_handle_realm_change()`, `character_handle_class_change()`, 
    `character_handle_race_change()`

**Quality Standards Applied to All Extracted Modules**:
  - Domain-driven function naming: `template_*`, `items_price_*`, `character_*` prefixes
  - Complete PEP 8 compliance (ruff validation, <88 char lines, type hints, docstrings)
  - Zero hardcoded strings (all UI text uses `lang.get()` for translations)
  - Zero French comments (English only in code and documentation)
  - ~1600 lines removed from `dialogs.py` and consolidated into reusable modules
  - Comprehensive technical documentation (ARMORY_TECHNICAL_DOCUMENTATION.md, CHARACTER_SYSTEM_TECHNICAL_DOCUMENTATION.md)
  - Robust error handling with graceful degradation
  - Backward compatibility with minimal thin wrapper methods in dialogs.py

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
- 🌐 **Settings/Eden translations**: Fixed hardcoded French text in Eden settings section
  - All buttons, labels and tooltips now follow language selection
  - Implemented retranslate_ui() for live language switching
  - Fixed v2 language keys (buttons.*, settings.herald.*)
- 🔄 **Settings live language update**: Settings dialog now auto-closes and reopens on language change
  - All navigation items, page titles, and widgets instantly translated
  - No need to manually close/reopen Settings window

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
