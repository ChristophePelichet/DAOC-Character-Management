# 📋 Simple Changelog - DAOC Character Management

---

# ✨ v0.108

### 🚀 Performance
- ⚡ **Eden Connection Test**: 50%+ improvement (7-8s → 3-4s or <0.1s cached)
  - 🎯 10-second caching for repeated tests (instant)
  - ⏲️ Reduced wait times: 7s → 3.3s
  - 📈 Optional performance logs (Settings > Eden, disabled by default)
  - 📁 Dedicated log file: Logs/eden_performance_YYYY-MM-DD.log

### 🎉 New Features
- 🐛 **Herald Debug HTML Options**: Control debug file generation in Settings > Debug (disabled by default)
- 🌐 **Dedicated Chrome Profile**: Isolated Selenium browser in AppData with automatic cookie migration
- 🗑️ **"Clean Eden" Button**: New button in Settings > Herald to delete cookies and Chrome profile
- 📂 **Auto-Create Backup Folders**: "Open folder" buttons now automatically create missing folders
- 💾 **Automatic Character Migration**: Intelligent folder restructuring without user intervention
  - 🔄 Automatic detection and migration: Characters/Realm/ → Characters/Season/Realm/
  - 💾 Automatic ZIP backup before migration with complete validation
  - ✅ Verification and normalization of each character file
  - ⚙️ Silent execution on startup (no popup, no confirmation)
  - 🛡️ Automatic rollback on error (data preserved)
  - 📊 Tracking in config.json to prevent multiple migrations
  - 🗑️ Removed old popup system (63 obsolete translations deleted)

### 🔧 Improvements
- 💾 **Cookies Backup Optimization**: Backup only cookies file (~10 KB instead of 50+ MB), 99% reduction
- ⚙️ **Simplified Settings Interface**: Removed obsolete cookies fields (path managed automatically)

### Bug Fixes
- 🎨 **Purple Theme**: Text now visible (transparent background, readable placeholder)
- 🐛 Fixed Settings crash with missing cookies_path_edit
- 🐛 Fixed cookies backup disappearing immediately after creation
- 🌍 Fixed "Clean Eden" button translations (FR/EN/DE)
- 🌍 Fixed character "Update" window now translated (FR/EN/DE)
- 🌍 **Dynamic Translations**: Version section updates without restart when changing language
- 🌍 **Herald Import**: "Import Complete" title displays correctly (instead of key name)
- 🌍 **RvR Statistics**: Translated labels (Tours/Forteresses/Reliques Capturées in FR, Towers/Keeps/Relics Captured in EN, etc.)
- 🌍 **PvP/PvE Statistics**: All labels translated (Kills en Solo, Coups Fatals, Dragons Tués, etc.)
- 🗑️ **Cleanup**: Removed obsolete qdarkstyle key (custom JSON theme system used now)
- 🌐 Fixed Chrome browser freeze on first launch (cookies not loaded)
- 🔒 Protection against Chrome profile conflicts during Herald validation at startup
- 🎨 Fixed text display with Purple theme (white square + invisible placeholder)
- 📚 Complete theme system documentation (700+ lines)

### 🎉 New Features
- ⌨️ **Keyboard Shortcuts**: Ctrl+N to create character, Ctrl+F to search on Herald
- 🎨 **Purple Theme (Dracula)**: New purple/pink theme with official Dracula palette
- 📝 **FUTURE_IMPROVEMENTS.md File**: List of planned enhancements with checkboxes

### 🐛 Bug Fixes
- 🛡️ **Migration File**: No more automatic creation of .migration_done file
- ⚡ **Herald Search**: Instant window closure (no more latency)

### 🧹 Cleanup
- 🗑️ Removed test files and temporary documentation
- 📚 Final documentation: CONFIG_V2_TECHNICAL_DOC.md

### 🧰 Improvements
- 🔄 **Configuration v2**: Hierarchical structure with automatic migration and backup
  - 5 organized sections (ui, folders, backup, system, game)
  - 100% backward compatibility guaranteed (39 legacy keys)
  - Default theme: Purple | Default language: English
  - Complete technical documentation included
- 🎨 **Theme Switching**: Complete instant application without restart
- 📋 **Columns**: Automatic width save in manual mode

### 🧰 Improvements (Continued)
- ⚙️ **Reorganized Settings**: New Backup page with real-time stats and direct actions
- 💾 **Integrated Backups**: Characters + Cookies backups accessible from Settings (no more Tools menu)
- 📁 **Simplified Configuration**: Config folder always next to executable (security)
- 🔄 **Auto Refresh**: Character list automatically updated after folder change
- 📚 **Technical Documentation**: 3 new detailed guides (1800+ lines)

### 🐛 Bug Fixes
- ✅ Menus and central display adapt correctly on Dark→Light switch
- ✅ Menu bar correctly reset to system colors in Light theme
- ✅ Column widths remembered between sessions in manual mode

### ✨ Added (Previous Features)

**GitHub Wiki Help System**
- 📚 Migrated from in-app help to GitHub Wiki for better accessibility
- 🌐 F1 shortcut opens Wiki documentation in browser
- 🌍 Multilingual support (FR/EN/DE pages)
- 📝 Complete French documentation (Home, Create, Edit, Delete)
- 🔗 Language-aware links (opens correct language based on app settings)
- 📖 Technical documentation (WIKI_HELP_SYSTEM.md, 400+ lines)

### 🧰 Modified

**Help System Architecture**
- 🔄 Replaced in-app HelpDialog with browser-based Wiki
- 🌐 Single "Documentation" menu item (F1) instead of 3 separate entries
- ✅ Git submodule for Wiki repository integration

### 🗑️ Removed

**In-App Help Components**
- 🗑️ Help/ folder (help_database.json, Markdown files)
- 🗑️ Functions/help_system.py (507 lines)
- 🗑️ Functions/tooltip_manager.py (70 lines)
- 🗑️ Scripts/create_complete_help_database.py
- 🧹 Total: -982 lines removed, +433 lines added (net -549 lines)

### 📚 Documentation

**Technical Eden Scraping**
- 📝 3 detailed English documentations (2000+ lines)
- 📊 ASCII flow diagrams
- 💡 Practical examples and troubleshooting guides
- 🎯 Unified documented architecture

---

# ✨ v0.108 - 11/14/2025

### ✨ Added

**Multilingual Support for Progress Dialogs**
- 🌍 58 new FR/EN/DE translations for all progress dialogs and import messages
- 📚 Complete technical documentation with diagrams (PROGRESS_DIALOG_SYSTEM_EN.md, 1900+ lines)
- 🎯 Full support for 3 languages in user interface

### 🧰 Modified

**Migration to Translation System**
- 🔄 All dialog texts now automatically translated
- 🌐 4 migrated dialogs: Stats update, Character update (×2), Cookie generation
- ✅ Fully multilingual interface (FR/EN/DE)

### 🐛 Fixed

**Column Widths Not Remembered**
- 🛡️ Manually resized columns lost on application restart
- 🔧 Automatic width saving in config.json
- 🎯 Persistent column configuration between sessions

**Message Formatting Error**
- 🛡️ Fixed "Index out of range" crash when displaying messages
- 🔧 Migrated to named parameters ({char_name}, {count}, {error})
- 🎯 Translated messages displayed correctly with dynamic values

**Herald Search Window Freeze**
- 🛡️ Fixed slow window close (2-3 clicks required) + freeze after import
- 🔧 Async cleanup of threads and resources (QTimer.singleShot)
- 🎯 Instant close (<100ms), no freeze, background refresh/backup

**Untranslated Import Messages**
- 🛡️ "Import terminé" messages hardcoded in French
- 🔧 6 new FR/EN/DE translation keys
- 🎯 Herald interface 100% multilingual

### 🔚 Removed

**Documentation Cleanup**
- 🗑️ Removed 20+ obsolete files (~4000 lines)
- 🧹 Clean and consolidated final documentation

---

# ✨ v0.107 - 11/11/2025

### 🧰 Modified

**Copilot Configuration + Technical Documentation**
- ⚙️ VS Code Copilot configuration for automatic workflow (translations, changelogs, commit, merge)
- 📝 2 Copilot instruction files (`.github/copilot-instructions.md` and `.copilot-instructions.md`)
- 📐 Progress window architecture reflection document (ARCHI_WINDOWS.md, 1200+ lines)
- 📊 Complete CharacterProfileScraper + WealthManager documentation (CHARACTER_STATS_SCRAPER_EN.md, 2000+ lines)
- 🔧 Refactored wealth_manager.py to centralized `_connect_to_eden_herald()` function

---

# ✨ v0.108

### 📚 Documentation

**Eden Scraping Technical Documentation**
- 📝 3 detailed English documentations (2000+ lines)
- 📊 ASCII graphical diagrams of execution flows
- 💡 Practical examples and troubleshooting guides
- 🎯 Unified architecture documented

### 🐛 Fixed

**Missing URL on Import**
- 🛡️ Fixed bug where Herald URL was not saved when importing characters
- 🔧 Added URL fallback forgotten during SearchThread refactoring
- 🎯 Imported characters now contain their URL for automatic updates

**Herald Close Crash**
- 🛡️ Fixed crash when closing search window
- 🔧 Complete protection: thread stopping, signal disconnection, exception handling
- 🎯 Safe closing at any time without crashes

### 🧰 Modified

**Enhanced Herald Search**
- 🎨 New progress window with 9 detailed steps
- ✅ Visual status system: Waiting (⏺️), In Progress (⏳), Completed (✅)
- 📋 All steps remain visible with status indication
- 🔄 Automatic step updates as progress advances
- 🎯 Complete visual feedback for user

---

# ✨ v0.107

### 🎉 Added

**Configurable Theme System**
-  Two available themes: Light (default) and Dark
- ⚙️ Theme selector in configuration menu
- 🔄 Instant theme switching without restart

**Font Scaling System**
- � Text size dropdown menu with 5 levels: 100%, 125%, 150%, 175%, 200%
- � Instant application without restart
- 🎯 Base font scaling (9pt Segoe UI on Windows)
- � Automatic CSS stylesheet scaling for themes
- 🖋️ Scaling of all inline Python styles (18 labels modified)

**Responsive Interface**
- 📜 Scrollable area in configuration window
- 📐 Increased minimum size: 600×500 pixels (instead of 500×400)
- 🖥️ Comfortable initial size: 700×700 pixels
- ↕️ Automatic scrolling if window too small

**Version Check System**
- 🔄 Automatic check on application startup
- � Display of current version
- 🌐 Display of latest available version (from GitHub)
- � Manual "🔄 Check" button to relaunch verification
- ✅ Visual indicators: ✓ green (up to date) or ✗ red (outdated)
- � Clickable download link to GitHub Releases (if update available)

**Class Banner System**
- �️ Visual banners for 44 DAOC classes (Albion, Hibernia, Midgard) [©️Eden Daoc](https://eden-daoc.net/)
- � Responsive design adapting to window height
- 🔄 Automatic update when class/realm changes

**Complete Herald Statistics**
- ⚔️ RvR Section: Tower Captures, Keep Captures, Relic Captures
- �️ PvP Section: Solo Kills, Deathblows, Kills (with realm detail Alb/Hib/Mid)
- � PvE Section: Dragons, Legions, Mini Dragons, Epic Encounters, Epic Dungeons, Sobekite
- � Wealth Section: Currency in "18p 128g 45s 12c" format
- 🏆 Achievements Section: 16 achievements displayed

**"Information" Button**
- ℹ️ Button next to "Refresh Stats" button
- 📝 Explanatory message about cumulative nature of statistics

### 🧰 Modified

**"Refresh Stats" Button**
- 🎯 Smart state management (grayed during Herald validation at startup)
- ⏸️ Automatic disable during Herald scraping
- 🔒 Guaranteed reactivation with `try/finally` pattern
- 📢 Detailed error messages for RvR/PvP/PvE/Wealth

**Currency Display**
- � Font size reduced from 11pt to 9pt (better visual harmony)
- � Bold style preserved

### 🐛 Fixed

**Error Messages**
- � Fix incomplete error messages (added missing PvE and Wealth)
- 📢 Display ALL errors (RvR/PvP/PvE/Wealth)

**Currency Formatting**
- � Fix TypeError with `f"{money:,}"` on string
- � Use `str(money)` for direct display

**Herald Connection Test**
- � Fix crash on connection errors
- 🔐 Add `finally` block to properly close driver

**Statistics Display**
- 📱 Fix RvR/PvP/PvE/Wealth/Achievements sections truncated on small screens
- 📏 Fix full height of statistics sections (removed QScrollArea)
- � Add `setWordWrap(False)` on PvP labels to prevent line wrapping

**Debug Files**
- 🗑️ Remove automatically created HTML files
- � Add to .gitignore

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.106 - 2025-11-07

# ✨ v0.106 - 2025-11-07

### 🎉 Added

**Logging System**
- � Unified format: `LOGGER - LEVEL - ACTION - MESSAGE`
- 🏷️ BACKUP Logger: all backup module logs tagged
- 🏷️ EDEN Logger: all Eden scraper logs tagged
- 🎯 Standardized actions for each module
- 🔍 Improved debug window with logger filter

**Eden Cookies Backup**
- � Automatic daily cookie backup at startup
- 📂 Dedicated "Eden Cookies" section in backup window
- ⚙️ Same options as Characters: compression, storage limit
- � "Save Now" button for immediate force backup
- 📁 "Open Folder" button for direct access
- 🔄 Automatic refresh after save
- 📊 Display number of backups and last backup date

**Interface**
- 🖥️ Redesign main window layout with Currency section
- 📏 Herald status bar optimizations (750px × 35px buttons)
- 📋 Redesign character sheet (renamed Statistics, removed Resistances)
- � Moved "Manage Armor" button

### 🧰 Modified

**Backup Module**
- 🏷️ Character name included in backup files
- 📝 Format: `backup_characters_20251107_143025_Update_Merlin.zip`
- 📝 Multiple: `backup_characters_20251107_143025_Update_multi.zip`
- 🔍 Immediate character identification
- 📊 Improved logs: INFO instead of ERROR on first startup
- ✅ Clear error message: "No characters to backup"
- �️ 46+ logs tagged with clear actions

**Herald Performance**
- ⚡ Herald timeout reduction of 17.4% (-4.6 seconds per search)
- 🎯 Character search: 26.5s → 21.9s (-4.6 seconds)
- ✅ 25/25 tests successful (100% stable, 0 crash)

**Interface**
- 📏 Herald URL column width optimized (120px minimum)
- � Herald buttons uniform size in sheet
- 🖥️ Backup window enlarged (1400x800)
- � Side-by-side layout: Characters and Eden Cookies

**Configuration**
- 🎯 Default season: S3 instead of S1
- ⚙️ Manual columns: Manual management enabled by default
- � Conditional logs: Created ONLY if debug_mode enabled

### 🐛 Fixed

**Eden Herald**
- 💥 Fix brutal crash on Herald search errors
- 🔐 Proper WebDriver closure in all error paths
- � Full stacktrace logging for diagnosis
- ✅ Stability test: 25/25 searches successful (100% stable)
- 🛠️ Automated test script for continuous validation
- � Cookie path correction (PyInstaller fix)
- 🔄 Auto-update during character import
- 📂 Configurable Herald cookies folder
- � Herald connection test protection
- 📦 Selenium import error handling
- 🔒 Driver cleanup protection

**Interface**
- 🔧 Column configuration correction (12 columns)
- 🏷️ Label unification ("Directory")
- 📊 Display path beginnings
- 🔍 Robust diagnostic system for unexpected stops
- ↕️ Functional realm sorting (added RealmSortProxyModel)
- 🗺️ Proxy model mapping for sorted operations
- ✅ Save button no longer closes sheet

**Code Quality**
- 🧹 Code cleanup: 74 excessive blank lines removed
- 📦 Reduced exe size: Estimated -1 to 2 MB (-2 to 4%)
- 📋 Fixed version: "About" window now displays v0.106
- 🔧 Migration fix: No more "migration_done" error
- 💻 67 production files modified for optimal quality
- 🔒 sys.stderr/stdout None handling
- 🧵 Thread exception capture
- 📝 Full traceback logging
- ✅ Backup logging errors corrected

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.105 - 2025-11-01

### 🎉 Added

**Eden Scraper**
- 🌐 Complete Eden Scraper module
- 🍪 Cookie manager with GUI interface
- � Bulk character import
- 🌐 Multi-browser support (Chrome, Edge, Firefox)
- 🔧 3-tier ChromeDriver system
- ⚙️ Browser configuration in settings
- � Herald status bar
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
- 🔍 Manual structure verification (Help menu)

### 🧰 Modified

No major modifications in this version.

### � Fixed

**Eden Scraper**
- 🔧 Fixed changing class during rank modification
- 📝 Herald data normalization
- 💾 Fixed Herald modification save
- � Optimized browser detection

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.104 - 2025-10-25

### 🎉 Added

**Complete Refactoring**
- 🔧 Complete refactoring into 3 managers
- ⚡ Performance optimization (-22% loading)
- 📉 Code reduction (-61% main.py)
- 🗂️ New Season/Realm structure

**Automatic Migration**
- 🔄 Automatic migration with ZIP backup
- 💬 Trilingual confirmation popup
- � Compressed backups (70-90% savings)
- ✅ Automatic integrity verification
- ↩️ Automatic rollback on error
- 📝 Complete JSON validation

**Interface**
- � Class and Race columns
- 👑 Realm Rank with dropdown menus
- � Automatic rank save
- � Traditional Windows menu

**Documentation**
- 🧹 Project cleanup script
- � MIGRATION_SECURITY documentation
- 🧪 Migration test scripts
- 📖 Complete documentation reorganization

### 🧰 Modified

No major modifications in this version.

### � Fixed

No bugs fixed in this version.

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.103 - 2025-10-20

### 🎉 Added

**Races and Classes**
- 🧬 Race and class selection
- � Dynamic race/class filtering
- ✅ Automatic race/class validation
- 🌍 Specialization translations (FR/EN/DE)
- 📊 Complete data system (44 classes, 18 races)
- � 188 translated specializations
- 🎮 Eden support (adapted classes)

**Interface**
- 📏 Column width management
- 🤖 Automatic/manual mode for columns

### 🧰 Modified

No major modifications in this version.

### 🐛 Fixed

No bugs fixed in this version.

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.102 - 2025-10-15

### 🎉 Added

**Multi-Server**
- 🌐 Server column restoration (Eden/Blackthorn)
- ⚙️ Default server configuration
- 📋 Server dropdown in character sheet
- 👁️ Server column hidden by default

**Renaming**
- ✏️ Simplified renaming
- ⚡ Quick rename (Enter key)

### 🧰 Modified

No major modifications in this version.

### � Fixed

- 💬 Simplified error messages
- 🔧 RealmTitleDelegate correction

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.101 - 2025-10-10

### 🎉 Added

**Windows Menu Interface**
- 📂 File menu (New character, Settings)
- �️ View menu (Columns)
- ❓ Help menu (About)
- 🌍 Menu translations (FR/EN/DE)

**Editing**
- ✏️ Realm, level, season, page, guild editing
- � Automatic move on realm change
- 🖱️ Rename via context menu

**Optimization**
- ⚡ Icon loading optimization
- 🎨 Interface simplification

### 🧰 Modified

- 🌐 Server automatically set to "Eden"

### � Fixed

No bugs fixed in this version.

### 🔚 Removed

- ❌ Server column removal

---

# ✨ v0.1 - 2025-10-01

### 🎉 Added

**Core Features**
- � Complete character management
- ➕ Create, modify, delete, duplicate
- 👑 Realm rank system
- 🌍 Multilingual interface (FR/EN/DE)
- 📋 Column configuration
- 🐛 Debug mode with integrated console
- � Bulk actions
- 🏰 Realm organization (Albion, Hibernia, Midgard)
- 🌐 Multi-server support
- � Season system
- 🔗 Web data extraction
- 🖥️ PySide6 interface
- 💾 Configuration persistence

### 🧰 Modified

No modifications (initial version).

### � Fixed

No bugs fixed (initial version).

### 🔚 Removed

No features removed (initial version).

### 🎉 Added

**Logging System**
- 📋 Unified format: `LOGGER - LEVEL - ACTION - MESSAGE`
- 🏷️ BACKUP Logger: all backup module logs tagged
- 🏷️ EDEN Logger: all Eden scraper logs tagged
- 🎯 Standardized actions for each module
- 🔍 Improved debug window with logger filter

**Eden Cookies Backup**
- 📅 Automatic daily cookie backup at startup
- 📂 Dedicated "Eden Cookies" section in backup window
- ⚙️ Same options as Characters: compression, storage limit
- 💾 "Save Now" button for immediate force backup
- 📁 "Open Folder" button for direct access
- 🔄 Automatic refresh after save
- 📊 Display number of backups and last backup date

**Interface**
- 🖥️ Redesign main window layout with Currency section
- 📏 Herald status bar optimizations (750px × 35px buttons)
- 📋 Redesign character sheet (renamed Statistics, removed Resistances)
- 🔧 Moved "Manage Armor" button

### 🧰 Modified

**Backup Module**
- 🏷️ Character name included in backup files
- 📝 Format: `backup_characters_20251107_143025_Update_Merlin.zip`
- 📝 Multiple: `backup_characters_20251107_143025_Update_multi.zip`
- 🔍 Immediate character identification
- 📊 Improved logs: INFO instead of ERROR on first startup
- ✅ Clear error message: "No characters to backup"
- 🏷️ 46+ logs tagged with clear actions

**Herald Performance**
- ⚡ Herald timeout reduction of 17.4% (-4.6 seconds per search)
- 🎯 Character search: 26.5s → 21.9s (-4.6 seconds)
- ✅ 25/25 tests successful (100% stable, 0 crash)

**Interface**
- 📏 Herald URL column width optimized (120px minimum)
- 🔘 Herald buttons uniform size in sheet
- 🖥️ Backup window enlarged (1400x800)
- 📂 Side-by-side layout: Characters and Eden Cookies

**Configuration**
- 🎯 Default season: S3 instead of S1
- ⚙️ Manual columns: Manual management enabled by default
- 📁 Conditional logs: Created ONLY if debug_mode enabled

### 🐛 Fixed

**Eden Herald**
- 💥 Fix brutal crash on Herald search errors
- 🔐 Proper WebDriver closure in all error paths
- 📝 Full stacktrace logging for diagnosis
- ✅ Stability test: 25/25 searches successful (100% stable)
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
- 📊 Display path beginnings
- 🔍 Robust diagnostic system for unexpected stops
- ↕️ Functional realm sorting (added RealmSortProxyModel)
- 🗺️ Proxy model mapping for sorted operations
- ✅ Save button no longer closes sheet

**Code Quality**
- 🧹 Code cleanup: 74 excessive blank lines removed
- 📦 Reduced exe size: Estimated -1 to 2 MB (-2 to 4%)
- 📋 Fixed version: "About" window now displays v0.106
- 🔧 Migration fix: No more "migration_done" error
- 💻 67 production files modified for optimal quality
- 🔒 sys.stderr/stdout None handling
- 🧵 Thread exception capture
- 📝 Full traceback logging
- ✅ Backup logging errors corrected

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.105 - 2025-11-01

### 🎉 Added

**Eden Scraper**
- 🌐 Complete Eden Scraper module
- 🍪 Cookie manager with GUI interface
- 📥 Bulk character import
- 🌐 Multi-browser support (Chrome, Edge, Firefox)
- 🔧 3-tier ChromeDriver system
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
- 🔍 Manual structure verification (Help menu)

### 🧰 Modified

No major modifications in this version.

### 🐛 Fixed

**Eden Scraper**
- 🔧 Fixed changing class during rank modification
- 📝 Herald data normalization
- 💾 Fixed Herald modification save
- 🔍 Optimized browser detection

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.104 - 2025-10-25

### 🎉 Added

**Complete Refactoring**
- 🔧 Complete refactoring into 3 managers
- ⚡ Performance optimization (-22% loading)
- 📉 Code reduction (-61% main.py)
- 🗂️ New Season/Realm structure

**Automatic Migration**
- 🔄 Automatic migration with ZIP backup
- 💬 Trilingual confirmation popup
- 📦 Compressed backups (70-90% savings)
- ✅ Automatic integrity verification
- ↩️ Automatic rollback on error
- 📝 Complete JSON validation

**Interface**
- 📋 Class and Race columns
- 👑 Realm Rank with dropdown menus
- 💾 Automatic rank save
- 📂 Traditional Windows menu

**Documentation**
- 🧹 Project cleanup script
- 📚 MIGRATION_SECURITY documentation
- 🧪 Migration test scripts
- 📖 Complete documentation reorganization

### 🧰 Modified

No major modifications in this version.

### 🐛 Fixed

No bugs fixed in this version.

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.103 - 2025-10-20

### 🎉 Added

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

### 🧰 Modified

No major modifications in this version.

### 🐛 Fixed

No bugs fixed in this version.

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.102 - 2025-10-15

### 🎉 Added

**Multi-Server**
- 🌐 Server column restoration (Eden/Blackthorn)
- ⚙️ Default server configuration
- 📋 Server dropdown in character sheet
- 👁️ Server column hidden by default

**Renaming**
- ✏️ Simplified renaming
- ⚡ Quick rename (Enter key)

### 🧰 Modified

No major modifications in this version.

### 🐛 Fixed

- 💬 Simplified error messages
- 🔧 RealmTitleDelegate correction

### 🔚 Removed

No features removed in this version.

---

# ✨ v0.101 - 2025-10-10

### 🎉 Added

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

### 🧰 Modified

- 🌐 Server automatically set to "Eden"

### 🐛 Fixed

No bugs fixed in this version.

### 🔚 Removed

- ❌ Server column removal

---

# ✨ v0.1 - 2025-10-01

### 🎉 Added

**Core Features**
- 👥 Complete character management
- ➕ Create, modify, delete, duplicate
- 👑 Realm rank system
- 🌍 Multilingual interface (FR/EN/DE)
- 📋 Column configuration
- 🐛 Debug mode with integrated console
- 🔄 Bulk actions
- 🏰 Realm organization (Albion, Hibernia, Midgard)
- 🌐 Multi-server support
- 📅 Season system
- 🔗 Web data extraction
- 🖥️ PySide6 interface
- 💾 Configuration persistence

### 🧰 Modified

No modifications (initial version).

### 🐛 Fixed

No bugs fixed (initial version).

### 🔚 Removed

No features removed (initial version).
