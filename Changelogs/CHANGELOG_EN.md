# 📝 CHANGELOG - DAOC Character Manager

Complete version history of the character manager for Dark Age of Camelot (Eden).

---

# ✨✨ v0.108

### 🎉 Added
- 🌐 **Dedicated Chrome Profile for Selenium**: Complete browser scraping isolation
  - 📁 Chrome profile stored in AppData: `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/ChromeProfile/`
  - 🔄 Automatic cookie migration: `Configuration/eden_cookies.pkl` → `Eden/eden_cookies.pkl`
  - 💾 Multi-OS support (Windows/Linux/macOS) with appropriate paths
  - 📊 Chrome profile size display in cookie manager
  - 🗑️ "Clean Eden" button in Settings > Herald (deletes cookies + Chrome profile)
  - 🔧 path_manager functions: `get_eden_data_dir()`, `get_chrome_profile_path()`, `get_eden_cookies_path()`
  - 📚 Complete technical documentation (CHROME_PROFILE_TECHNICAL_EN.md, 500+ lines)
  - Files: Functions/cookie_manager.py, path_manager.py, UI/settings_dialog.py, dialogs.py

### 🎉 Added
- 💾 **Automatic Character Migration System**: Intelligent folder structure reorganization
  - 📝 3 new modules: character_schema.py (390 lines), character_migration.py (481 lines), config_schema.py (migrations section)
  - 🔄 Automatic old structure detection: Characters/Realm/ → Characters/Season/Realm/
  - 💾 Timestamped ZIP backup with testzip() validation before migration
  - ✅ Complete schema validation (7 required fields, 12 optional) for each character
  - 🔄 Data normalization with intelligent default values
  - ⚙️ Silent execution on character_manager.py load (no user interaction)
  - 🛡️ Automatic rollback on error (removes new files, preserves old ones)
  - 📊 Tracking in config.json (migrations.character_structure_done + ISO timestamp)
  - 📄 Complete technical documentation (CHARACTER_MIGRATION_TECHNICAL_DOC.md, 870 lines)
  - Files: Functions/character_schema.py, character_migration.py, character_manager.py, config_schema.py

### 🔚 Removed
- 🗑️ **Old Popup Migration System**: Complete removal in favor of new automatic system
  - 📝 Removed _run_automatic_migration() method in main.py (105 lines)
  - 🌍 Removed "migration" section in Language/*.json (21 keys × 3 languages = 63 deletions)
  - ⚙️ Removed 22 migration_* mappings in language_schema.py
  - 📚 Updated LANGUAGE_V2_TECHNICAL_DOC.md (421→399 keys)
  - 🎯 Impact: Fully automatic and silent migration, no user interaction
  - Files: main.py, Language/*.json, Functions/language_schema.py, Documentations/Lang/LANGUAGE_V2_TECHNICAL_DOC.md

### 🐛 Bug Fix
- 🌍 **Version Section Translations**: Dynamic language update without restart
  - 🔧 Converted version labels to instance attributes (status_group, info_group, version labels)
  - 🎯 Enhanced retranslate_ui() method with 7 dynamic label updates
  - Added status_bar.status_group_title key (FR/EN/DE)
  - Language change applied immediately to version titles and labels
  - Files: Functions/ui_manager.py, Language/*.json
- 🌍 **herald_import_complete_title Key**: Fixed translation hierarchical path
  - 🔧 Using full path messages.info.herald_import_complete_title
  - 🎯 Import dialog title now displays "Import Complete" instead of key name
  - Fixed in both dialogs (information and warning)
  - File: UI/dialogs.py
- 🌍 **RvR Statistics Labels**: Translated captures in character sheet
  - 🔧 Tours Capturées, Forteresses Capturées, Reliques Capturées (FR)
  - Towers Captured, Keeps Captured, Relics Captured (EN)
  - Türme Erobert, Festungen Erobert, Reliquien Erobert (DE)
  - Note: Scraper continues to search for English terms in Eden Herald HTML
  - Files: Language/*.json
- 🌍 **PvP/PvE Statistics Labels**: Complete translation of combat statistics
  - 🔧 PvP: Kills en Solo, Coups Fatals, Kills (FR) | Solo Kills, Deathblows, Kills (EN) | Solo-Kills, Todesstöße, Kills (DE)
  - PvE: Dragons Tués, Légions Tuées, Mini Dragons Tués, Rencontres Épiques, Donjons Épiques (FR)
  - PvE: Dragons Killed, Legions Killed, Mini Dragons Killed, Epic Encounters, Epic Dungeons (EN)
  - PvE: Drachen Getötet, Legionen Getötet, Mini-Drachen Getötet, Epische Begegnungen, Epische Dungeons (DE)
  - Files: Language/*.json, LANGUAGE_V2_TECHNICAL_DOC.md

### 🔚 Removed
- 🗑️ **Obsolete qdarkstyle_not_found_tooltip Key**: Removed reference to unused library
  - 🔧 Application now uses custom JSON-based theme system (Themes/*.json)
  - No longer depends on external qdarkstyle library
  - Misc section reduced to 1 key (none) instead of 5
  - Files: Language/*.json, Functions/language_schema.py, LANGUAGE_V2_TECHNICAL_DOC.md

### 🎉 Added
- 📚 **Wiki Help Pages**: Complete documentation for Settings and Backup
  - FR-Settings.md page: Complete settings guide (5 detailed tabs)
  - FR-Backup.md page: Comprehensive backup system documentation
  - Navigation between pages with GitHub Wiki links
  - Table of contents, practical examples, FAQ, troubleshooting
  - Compatible with integrated help system (F1 key)
  - FR versions ready, EN/DE translations coming soon
- ⌨️ **Keyboard Shortcuts for Main Actions**: Quick access to common features
  - **Ctrl+N**: Create new character manually (shortcut displayed in File menu)
  - **Ctrl+F**: Search character on Eden Herald with smart validation
  - Automatic Eden connection validation management before opening search
  - Waiting window with 500ms checks (15 seconds timeout)
  - Contextual error messages if Herald connection unavailable
  - 🌍 Complete FR/EN/DE translations (7 new keys)

### 🐛 Bug Fix
- 🌍 **Character Update Window Not Translated**: Added complete FR/EN/DE translations
  - 🛡️ Problem: `CharacterUpdateDialog` window displayed all texts in hardcoded French
  - 🔍 Cause: Hardcoded texts in UI/dialogs.py without using language system
  - ✅ Solution: Added 16 keys in `dialogs.character_update` (title, column headers, buttons, field names)
  - 🎯 Impact: Update window fully translated according to selected language
  - Files: UI/dialogs.py, Language/fr.json, Language/en.json, Language/de.json
  - 📚 Documentation: Updated LANGUAGE_V2_TECHNICAL_DOC.md with character_update section
- 🛡️ **.migration_done File Not Recreated**: Prevention of automatic flag file creation
  - 🔧 Removed `mark_migration_done()` call during startup check
  - 🎯 File only created when migration is actually performed successfully
  - Prevents file recreation when changing Characters folder or manual deletion
  - File: `Functions/migration_manager.py`
- ⚡ **Herald Search Close Button Latency**: Instant window closure
  - 🔧 Modified `accept()` to use asynchronous cleanup via QTimer
  - 🎯 Removed 100ms+ UI blocking caused by `thread.wait(100)`
  - Thread and temporary files cleanup after window closure
  - Consistent with pattern already used in `closeEvent()`
  - File: `UI/dialogs.py` (HeraldSearchDialog class)

### 🧰 Modifications
- 🔄 **Configuration v2 Restructuring**: Hierarchical architecture with automatic migration
  - 📊 Organized structure in 5 sections (ui, folders, backup, system, game)
  - 🔀 Automatic v1→v2 migration with timestamped backup
  - ✅ Automatic validation with type schema and allowed values
  - 🔙 100% backward compatibility guaranteed (39 legacy keys supported)
  - 📝 Dotted notation (e.g., `config.get("ui.language")` instead of `config.get("language")`)
  - 🎯 Complete refactoring: 11 files, 100+ occurrences updated
  - 📚 Complete technical documentation: `CONFIG_V2_TECHNICAL_DOC.md`
  - Files: `Functions/config_schema.py`, `Functions/config_migration.py`, `Functions/config_manager.py`
- 🏷️ **Backup Keys Renaming**: More explicit nomenclature
  - `enabled` → `auto_daily_backup` (clarification of automatic behavior)
  - Added `last_date` for cookies and armor (consistency with characters)
  - Complete legacy mapping maintained for compatibility
- 🎨 **Default Theme**: Changed from "default" to "purple"
  - Purple theme automatically applied to new installations
  - Validated themes list: default, dark, light, purple
  - File: `Functions/config_schema.py`
- 🌍 **Default Language**: Changed from "fr" to "en"
  - English interface by default for better internationalization
  - File: `Functions/config_schema.py`
- ⚙️ **Backup Default Values**: Parameter optimization
  - `auto_delete_old`: `false` → `true` (automatic management of old backups)
  - `size_limit_mb`: 5 → 10 MB for cookies and armor (more space)
  - File: `Functions/config_schema.py`

### 🔚 Removed
- 🗑️ **Test Files**: Removed development scripts
  - Migration unit tests (test_config_migration.py, test_migration_real.py)
  - Automatic refactoring script (refactor_config_keys.py)
- 🗑️ **Working Documentation**: Cleaned up temporary documents
  - CONFIG_ANALYSIS_v1.md, JSON_STRUCTURE_IMPROVEMENT.md, PHASE2_COMPLETE.md
  - Kept only CONFIG_V2_TECHNICAL_DOC.md (final documentation)

### 🧹 Cleanup
- 🗑️ **Removed Obsolete References**: Complete cleanup of code and documentation
  - Removed references to S1 and S2 seasons (ended seasons on Eden)
  - Removed references to Blackthorn server (not compatible with the program)
  - Updated all default values: S3 (current season) and Eden (single server)
  - Simplified configuration: seasons = ["S3"], servers = ["Eden"]
  - Code and documentation aligned with current game state

### 🎉 Added
- 🎨 **New Purple Theme (Dracula)**: Dracula-inspired theme with purple/pink palette
  - Background colors: #282A36 (dark purple-gray background)
  - Accents: #BD93F9 (signature purple), #FF79C6 (pink)
  - Text: #F8F8F2 (off-white)
  - Fusion style with complete 16-color palette
  - FR/EN/DE translations ("Violet", "Purple", "Lila")
- 📝 **FUTURE_IMPROVEMENTS.md File**: Structured list of future enhancements
  - Overview section with checkboxes and anchor links
  - Sections: Theme System, Features, Fixes, Optimizations, Ideas
  - 3 planned theme improvements (Integrated Editor, Variant Generation, Import/Export)

### 🧰 Modified
- 🎨 **Dynamic Style System**: Complete tree_view refactoring
  - New `apply_tree_view_style()` method based on QPalette
  - Automatic theme detection (light/dark) via lightness (>128)
  - Adaptive grid colors: #d6d6d6 (light) / #404040 (dark)
  - Real-time application on theme change
- 📋 **Column Width Persistence**: Automatic save in manual mode
  - New `column_widths` parameter in config.json (dictionary)
  - Automatic restoration on startup in manual mode
  - Save on close and before mode change
- ⚙️ **Complete Settings Reorganization**: Major refactoring of configuration system
  - Migrated backups from Tools menu to Settings > Backup page
  - New dedicated page with two sections: Characters Backup + Cookies Backup
  - Real-time statistics (count, last date) with immediate update after backup
  - Direct actions: Backup Now, Open Folder (explorer)
  - Configuration folder now non-configurable (always `<exe_dir>/Configuration`)
  - Removed `.config_path` system (simplified architecture)
  - Normalized all Windows paths (backslashes `\\`)
  - Automatic character list refresh after Characters folder change
  - Complete Tools menu removal (features consolidated in Settings)
  - Removed Browse UI for Configuration folder (security)
  - Files modified: `UI/settings_dialog.py` (+273 lines), `main.py` (+13 lines), `Functions/ui_manager.py` (-7 lines), `Functions/config_manager.py` (-40 lines)
  - 🌍 Complete FR/EN/DE translations (10 new backup_* keys)
  - 📚 Complete technical documentation (3 files, 1800+ lines): Settings Architecture, Folder Move System, Backup Integration

### 🐛 Fix

**Incomplete Theme Application on Switch**
- 🛡️ **Problem**: When switching from Dark to Light theme, menu bar stayed black and central character display stayed black, requiring application restart to see complete changes
- 🔧 **Root Cause**: 
  - Tree_view had hardcoded colors in `_configure_tree_view()` (`grid_color = "#d6d6d6"`, `text_color = "#000000"`)
  - `default.json` (Light theme) had empty stylesheet, allowing Dark theme styles to persist
  - No call to reapply tree_view styles after theme change
- 🔧 **Solution Implemented**:
  - Created `apply_tree_view_style()`: dynamic method using QPalette to calculate colors based on active theme
  - Automatic theme detection: `base_color.lightness() > 128` → light theme, otherwise dark
  - Adaptive grid colors: `#d6d6d6` (light) / `#404040` (dark)
  - Added `apply_tree_view_style()` call in main.py after theme change
  - Added complete stylesheet in `default.json` with dynamic `palette(window)` references for menu bar
- 📝 Files modified: `Functions/tree_manager.py` (new method), `main.py` (call after switch), `Themes/default.json` and `dark.json` (stylesheets)
- 🎯 Impact: Theme switching now applies instantly and completely to all components (menus, tree view, dialogs) without requiring restart

**Column Widths Not Saved in Manual Resize Mode**
- 🛡️ **Problem**: In manual resize mode (unlocked columns), custom column widths were not saved, forcing users to resize all columns after each application restart
- 🔧 **Root Cause**: The system only saved `tree_view_header_state` (order and general state), but not individual widths. In manual mode, `apply_column_resize_mode()` reset everything to `Interactive` mode without restoring previous widths
- 🔧 **Solution Implemented**:
  - New `column_widths` parameter in `config.json`: dictionary `{"0": 60, "1": 80, ...}` storing each column's width
  - Modified `save_header_state()`: automatic saving of widths for all 12 visible columns
  - Modified `apply_column_resize_mode()` in manual mode: restores saved widths via `setColumnWidth()`, applies default widths if none saved
  - Automatic save before mode change in settings (preserves current configuration)
  - Automatic save on application close (`closeEvent`)
- 📝 Files modified: `Functions/tree_manager.py` (save_header_state, apply_column_resize_mode), `main.py` (save before mode change)
- 🎯 Impact: Custom column widths are now remembered between sessions. Users only need to configure columns once

**Window Freeze After Herald Update**
- 🛡️ **Problem**: Character sheet window (CharacterSheetWindow) froze after closing "No update" dialog, preventing any interaction for several seconds
- 🔧 **Root Cause**: Herald update thread (`char_update_thread`) continued running in background after displaying dialogs (error/success/no changes), blocking the interface
- 🔧 **Solution Implemented**:
  - Automatic thread cleanup (`_stop_char_update_thread()`) BEFORE displaying any dialog in `_on_herald_scraping_finished()`
  - Added `closeEvent()` in CharacterSheetWindow to properly stop thread on window close
  - Protection in `finally` block to guarantee cleanup even on error
- 📝 Modified files: `UI/dialogs.py` (CharacterSheetWindow)
- 🎯 Impact: Instant dialog and window closure, immediately responsive interface

**Inconsistent "No Update" Behavior Between Character Sheet and Context Menu**
- 🛡️ **Problem**: Context menu (right-click on character) showed empty comparison window when no changes detected, while character sheet displayed an informative message
- 🔧 **Root Cause**: `has_changes()` check implemented only in `CharacterSheetWindow.update_from_herald()`, but missing in context menu handler in `main.py._process_herald_update_result()`
- 🔧 **Solution Implemented**:
  - Added pre-display check `if not dialog.has_changes()` in `_process_herald_update_result()`
  - Display "Character already up to date" message instead of empty window
  - Thread cleanup before message display to prevent freeze
- 📝 Modified files: `main.py` (MainWindow)
- 🎯 Impact: Uniform behavior for both update paths, improved user experience

### 🗑️ Removal

**Removed "Check File Structure" Feature**
- 🛡️ **Reason**: Migration feature became obsolete in alpha/beta version, data correct by default in production
- 🔧 **Changes**:
  - Removed "🔧 Check file structure" menu from Help menu
  - Removed `check_json_structures()` method from MainWindow
  - Migration code kept in `Functions/migration_manager.py` for future use if needed
- 📝 Modified files: `Functions/ui_manager.py`, `main.py`
- 🎯 Impact: Simplified interface, manual migration option removed

**Incorrect Realm Rank Display in Update Comparison**
- 🛡️ **Problem**: When updating a character from Herald (via character sheet or context menu), the comparison window displayed the realm rank title (e.g., "Raven Ardent") instead of the XLY code (e.g., "5L9") in the "Current value" column, causing false change detection even when the rank was identical
- 🔧 **Root Cause**: Local JSON file may contain either XLY code (correct format) or text title (old format or incorrect save). The `CharacterUpdateDialog._detect_changes()` method compared values directly without validating realm rank format
- 🔧 **Solution Implemented**:
  - Added XLY format regex validation (`^\d+L\d+$`) to detect if `realm_rank` contains a title instead of a code
  - If title detected: automatic recalculation of XLY code from `realm_points` via `data_manager.get_realm_rank_info(realm, realm_points)`
  - Consistent comparison between XLY codes only (recalculated current vs new from Herald)
  - Import `re` module for regex validation
  - Error handling with logging if recalculation fails
- 🎯 **Impact**: Comparison now always displays rank code (5L9) in both columns, eliminating false positive change detection. Users no longer see proposed updates for realm rank when only the format differs

**Empty Comparison Window During Update**
- 🛡️ **Problem**: Comparison window opened systematically even when no changes were detected between local and Herald data, displaying an empty table with only green checkmarks, forcing the user to close manually
- 🔧 **Root Cause**: `CharacterUpdateDialog` was created and displayed via `exec()` without prior verification of actual changes existence
- 🔧 **Solution Implemented**:
  - New `has_changes()` method in `CharacterUpdateDialog`: traverses table and detects presence of at least one checkbox (= change)
  - Pre-display verification: dialog creation, `has_changes()` call, conditional display
  - If no changes: `QMessageBox.information()` with message "Character already up to date"
  - Dialog not displayed, immediate return
- 🎯 **Impact**: Improved user experience - clear message "Character already up to date" instead of empty window. Time savings and clarity for users

### ✨ Addition

**Multilingual Translations for Update Messages**
- 🌍 Added 2 new FR/EN/DE translation keys (Language/*.json):
  - `update_char_no_changes_title`: Message title "No Update" / "Aucune mise à jour" / "Keine Aktualisierung"
  - `update_char_already_uptodate`: Detailed message "The character is already up to date..." / "Le personnage est déjà à jour..." / "Der Charakter ist bereits aktuell..."
- 🎯 **Impact**: 100% multilingual interface for all Herald update scenarios

---

# ✨✨ v0.108 - 11/14/2025

### ✨ Addition

**Multilingual Translation System for Progress Dialogs**
- 🌐 Added 52 new FR/EN/DE translation keys (Language/*.json):
  - **Progress steps** (35 keys):
    - `step_herald_connection_*`: Checking cookies, initializing browser, loading
    - `step_scraper_init`: Initializing Herald scraper
    - `step_herald_search_*`: Searching, loading, extracting, saving, formatting
    - `step_stats_scraping_*`: RvR, PvP, PvE, wealth, achievements
    - `step_character_update_*`: 8 steps from extraction → browser closure
    - `step_cookie_gen_*`: Configuration, opening, user wait, extraction, saving, validation
    - `step_cleanup`: Common browser closure
  - **Dialog titles and descriptions** (8 keys):
    - `progress_stats_update_title/desc`: Stats update
    - `progress_character_update_title/desc`: Update from Herald
    - `progress_character_update_main_desc`: Description with character name (context menu)
    - `progress_cookie_gen_title/desc`: Discord cookie generation
  - **Status messages** (5 keys):
    - `progress_stats_complete`: ✅ Statistics retrieved
    - `progress_character_complete`: ✅ Data retrieved
    - `progress_cookie_success`: ✅ {count} cookies generated!
    - `progress_error`: ❌ {error} (generic error message)
  - **Herald import messages** (6 keys):
    - `herald_import_complete_title`: Import dialog title
    - `herald_import_success`: ✅ {count} character(s) imported
    - `herald_import_updated`: 🔄 {count} character(s) updated
    - `herald_import_errors`: ⚠️ {count} error(s)
    - `herald_import_more_errors`: ... and {count} more error(s)
    - `herald_import_no_success`: ❌ No import succeeded

**Complete Technical Documentation**
- 📚 New documentation: Documentations/Dialog/PROGRESS_DIALOG_SYSTEM_EN.md (1900+ lines):
  - Complete system architecture with ASCII diagrams
  - Detailed documentation of 3 classes (ProgressStep, StepConfiguration, ProgressStepsDialog)
  - 9 predefined configurations explained (HERALD_CONNECTION, SCRAPER_INIT, etc.)
  - Worker Thread Pattern with 4 security patterns
  - 3 implemented dialogs documented (Stats Update, Character Update, Cookie Generation)
  - Practical usage examples (simple, custom, error handling)
  - Multilingual support and performance characteristics
  - Migration summary (Before/After) with statistics
- 📚 New documentation: Documentations/Dialog/THREAD_SAFETY_PATTERNS.md:
  - Security patterns for Qt threads
  - Dialog lifecycle management
  - RuntimeError protection best practices

### 🧰 Modification

**Migration from Hardcoded Texts to Translation System**
- 🔄 Refactoring UI/progress_dialog_base.py (StepConfiguration):
  - Migrated 45+ hardcoded FR strings → translation keys
  - Classes HERALD_CONNECTION, SCRAPER_INIT, HERALD_SEARCH, STATS_SCRAPING, CHARACTER_UPDATE, COOKIE_GENERATION, CLEANUP
  - Texts now dynamically translated via lang.get()
- 🎨 ProgressStepsDialog improvements:
  - Added automatic translation in `__init__()` (label creation)
  - Added automatic translation in `_update_step_ui()` (state updates)
  - Import `lang` from Functions.language_manager
- 🌐 Updated UI/dialogs.py (4 dialogs):
  - **CharacterSheetDialog.update_rvr_stats()**: Translated title/description/messages
  - **CharacterSheetDialog.update_from_herald()**: Translated title/description/messages
  - **CookieManagerDialog.generate_cookies()**: Translated title/description/messages with count parameter
- 🔧 Updated main.py (CharacterApp.update_character_from_herald()):
  - Translated title/description with dynamic character name
  - Translated success/error messages
  - Import lang from Functions.language_manager

### 🐛 Fix

**Fixed Double Formatting of Translated Messages**
- 🛡️ **Problem**: IndexError "Replacement index 0 out of range" when using progress dialogs
  - Cause: Double .format() call - lang.get() already formats strings, then .format() was called again
  - Error example: `lang.get("key", default="text {0}").format(value)` → lang.get() returns text without {0}, .format() fails
- 🔧 **Solution**: Using named parameters in lang.get() kwargs
  - Changed placeholders: {0} → {char_name}, {count}, {error}
  - Removed .format() after lang.get()
  - Pass values directly via kwargs: `lang.get(key, char_name=name, count=nb)`
- 🎯 **Impact**: 5 fixes applied (main.py × 2, UI/dialogs.py × 3)
  - No more IndexError when displaying messages
  - Translated messages displayed correctly with dynamic values
  - System compatible with all progress dialogs

### 🐛 Fix

**UI Freeze When Closing Herald Search Window**
- 🛡️ **Problem**: Herald search window required 2-3 clicks to close + UI froze for several seconds after character import
- 🔧 **Root cause**:
  - `closeEvent()` called `thread.wait(3000)` synchronously (blocked UI for 3 seconds)
  - `refresh_character_list()` and `backup_characters_force()` executed synchronously after MessageBox
  - `super().closeEvent()` not called → Qt didn't actually close the window
- 🔧 **Solution implemented**:
  - Created `_stop_search_thread_async()`: thread cleanup via QTimer.singleShot() (non-blocking)
  - Created `_async_full_cleanup()`: complete cleanup in background
  - `closeEvent()` calls `super().closeEvent()` IMMEDIATELY then async cleanup
  - Thread reference captured before lambda (avoids access to destroyed object)
  - Timeout reduced from 3000ms to 100ms for thread cleanup
  - UI refresh and backup via QTimer.singleShot(100/200ms) after MessageBox
- 🎯 **Impact**: Instant close on 1st click (< 100ms), no freeze after import, background cleanup
- 📝 **Files modified**:
  - `UI/dialogs.py` (HeraldSearchDialog._stop_search_thread_async, _async_full_cleanup, closeEvent)
  - `UI/dialogs.py` (_import_characters: async refresh/backup)
- 📚 **Documentation**: Pattern 5 added in THREAD_SAFETY_PATTERNS.md (async cleanup for fast closure)

**Untranslated Herald Import Messages**
- 🛡️ **Problem**: "Import terminé" messages, success/error texts hardcoded in French in HeraldSearchDialog
- 🔧 **Solution**: Added 6 new FR/EN/DE translation keys + used lang.get() in code
- 🎯 **Impact**: Herald interface 100% multilingual (FR/EN/DE)

### 🔚 Removal

**Cleanup of Temporary Development Documentation**
- 🗑️ Removed 20+ obsolete documentation files (~4000 lines):
  - Temporary development documentation (PROGRESS_DIALOGS_PLANNING.md, SESSION1_COMPLETE.md, etc.)
  - Obsolete Cookie Manager guides (COOKIE_MANAGER_*.md, COOKIE_PATH_FIX.md, etc.)
  - Obsolete Herald tests (test_herald_search.py, HERALD_PHASE1_TEST_REPORT.md, etc.)
  - Consolidated migration docs (MIGRATION_SECURITY.md, MIGRATION_CONFIRMATION_UPDATE.md, etc.)
- 📚 Consolidation: All information integrated into PROGRESS_DIALOG_SYSTEM_EN.md and THREAD_SAFETY_PATTERNS.md
- 🧹 Result: Clean and complete final documentation (1900+ lines with diagrams)

### 📊 Statistics

- **Files modified**: 42 files (6 JSON translations + 3 Python + 1 main.py + 5 changelogs + 1 doc + 25 deletions)
- **Documentation created**: 2 (PROGRESS_DIALOG_SYSTEM_EN.md 1900+ lines, THREAD_SAFETY_PATTERNS.md)
- **Documentation updated**: 1 (THREAD_SAFETY_PATTERNS.md - Pattern 5 async cleanup)
- **Documentation removed**: 20+ obsolete files (~4000 lines)
- **Total lines**: +5100 insertions, -6471 deletions (net: -1371 lines)
- **Translations**: 58 keys × 3 languages = 174 entries (FR/EN/DE 100% coverage)
- **Dialogs translated**: 4 (StatsUpdate, CharacterUpdate×2, CookieGen)
- **Bugs fixed**: 2 (IndexError double .format() 5 locations, Herald window freeze)
- **Performance**: Herald window closes < 100ms (vs 3000ms+), no post-import freeze
- **Architecture**: UI/progress_dialog_base.py (600+ lines, reusable class)

---

# ✨✨ v0.107 - 2025-11-11

### 🎉 Added

**Configurable Theme System**
- 🎨 JSON-based theme system stored in `Themes/` folder
- 🌓 Two available themes: Light (windowsvista) and Dark (Fusion with custom CSS)
- ⚙️ Theme selector integrated in ConfigurationDialog (`UI/dialogs.py`)
- 🔄 Instant theme application without restart (via `apply_theme()` in `main.py`)
- 💾 Theme persistence in `Configuration/config.json` ("theme" key)
- 🌍 Complete multilingual support with automatic translations:
  - 🇫🇷 French: Clair / Sombre
  - 🇬🇧 English: Light / Dark
  - 🇩🇪 German: Hell / Dunkel
- 📦 Full portability for .exe compilation via PyInstaller
- 🎭 Native Qt styles support: windowsvista, Fusion, Windows, windows11
- 🎨 Color palette customization (QPalette) with 17 color roles
- 🖌️ Disabled state colors support (`Disabled_` prefix in palette)
- 📝 Optional CSS stylesheets for fine customization
- 🔧 `Functions/theme_manager.py` module (138 lines):
  - `get_themes_dir()`: Returns Themes/ folder path
  - `get_available_themes()`: Lists themes with automatic translation
  - `load_theme(theme_id)`: Loads theme JSON
  - `apply_theme(app, theme_id)`: Applies style, palette and CSS
- 🔤 Automatic alphabetical sorting of themes in ComboBox
- 🗂️ Theme JSON structure:
  ```json
  {
    "name": "theme_light",  // Translation key
    "style": "windowsvista",  // Qt style
    "palette": { "Window": "#F0F0F0", ... },  // QPalette colors
    "stylesheet": ""  // Optional CSS
  }
  ```

**Included Themes**
- 🌞 **Light Theme** (`Themes/default.json`):
  - Style: windowsvista (native Windows)
  - Palette: Standard light colors (#F0F0F0 window, #FFFFFF base)
  - Stylesheet: None (uses native styles)
- 🌙 **Dark Theme** (`Themes/dark.json`):
  - Style: Fusion (cross-platform)
  - Palette: Dark colors (#2D2D30 window, #1E1E1E base, #DCDCDC text)
  - Stylesheet: Custom CSS for dropdowns, tooltips and comboboxes
  - Effects: Subtle borders, consistent dark backgrounds

**Complete Font Scaling System**
- 🔤 Comprehensive font scaling system with user control
- 📊 QComboBox selector with 5 scale levels: 100%, 125%, 150%, 175%, 200%
- 💾 Persistent configuration in config.json (font_scale key, default 1.0)
- ⚡ Instant application without restart
- 🎯 Positioning: Configuration window, "General" section, below theme selector
- 🌍 Multilingual labels:
  - 🇫🇷 French: "Taille du texte"
  - 🇬🇧 English: "Text size"
  - 🇩🇪 German: "Textgröße"

**Two-Tier Scaling Architecture**
- 🔤 **Tier 1 - Base Font Scaling**:
  - Uses `QApplication.setFont()` to scale global base font
  - Base: 9pt Segoe UI × scale factor
  - Examples: 9pt → 11.2pt@125%, 13.5pt@150%, 18.0pt@200%
  - Affects all widgets without explicit stylesheets
  
- 🎨 **Tier 2 - CSS Stylesheet Scaling**:
  - Regex parsing of CSS stylesheets (theme JSON + inline Python styles)
  - Two patterns: `r'(\d+(?:\.\d+)?)pt\b'` for pt units, `r'font-size:\s*(\d+(?:\.\d+)?)px\b'` for px units
  - Applied in `apply_theme()` and `apply_font_scale()`
  - Affects themed widgets and custom-styled elements

**Scaling Functions Added** (`Functions/theme_manager.py`, 253 lines total, +115 lines):
- ⚙️ `scale_stylesheet_fonts(stylesheet, scale)` (33 lines, 179-211):
  - Internal regex engine for CSS font scaling
  - Parameters: stylesheet (string), scale (float)
  - Returns: Modified stylesheet (string)
  - Two separate callback functions to avoid IndexError:
    - `scale_pt(match)`: Scales pt values → `f"{size * scale:.1f}pt"`
    - `scale_px(match)`: Scales px values → `f"font-size: {size * scale:.1f}px"`
  - Two regex.sub() calls for pt and px patterns
  - Example: "9pt" → "13.5pt" @ 150% scaling ✓
  - Preserves CSS formatting with 1 decimal precision

- 🔧 `apply_font_scale(app, scale=1.0)` (23 lines, 154-176):
  - Applies scaling to base font and all stylesheets
  - Parameters: app (QApplication), scale (float, default 1.0)
  - Scale validation: if scale <= 0, defaults to 1.0
  - Base font calculation: 9pt × scale → setPointSizeF()
  - CSS scaling: app.styleSheet() → scale_stylesheet_fonts() → setStyleSheet()
  - Called at startup (main.py line 917) and on config change
  
- 📏 `get_scaled_size(base_size_pt)` (13 lines, 214-226):
  - Helper for inline Python stylesheets
  - Parameters: base_size_pt (int/float)
  - Returns: Scaled size (float)
  - Reads font_scale from config (default 1.0)
  - Usage: `f"font-size: {get_scaled_size(9):.1f}pt"`
  - Error handling: returns base_size_pt if config unavailable
  
- 📊 `get_scaled_stylesheet(stylesheet)` (12 lines, 229-240):
  - Helper to scale complete stylesheets
  - Parameters: stylesheet (string)
  - Returns: Scaled stylesheet (string)
  - Reads font_scale from config, applies scale_stylesheet_fonts()
  - Error handling: returns original stylesheet if config unavailable
  - Usage: `get_scaled_stylesheet("font-size: 10pt")` → "font-size: 15.0pt" @ scale=1.5

**Interface Modifications for Scaling**
- 📝 **Herald Progress Dialog** (`main.py`, 3 labels modified):
  - Title label: 12pt → `get_scaled_size(12)` (14.4pt@125%, 18.0pt@150%, 24.0pt@200%)
  - Detail label: 10pt → `get_scaled_size(10)` (12.0pt@125%, 15.0pt@150%, 20.0pt@200%)
  - Wait label: 9pt → `get_scaled_size(9)` (10.8pt@125%, 13.5pt@150%, 18.0pt@200%)
  
- 📊 **RvR Statistics** (`UI/dialogs.py`, 3 detail labels):
  - Solo Kills detail: 9pt → `get_scaled_size(9)`
  - Deathblows detail: 9pt → `get_scaled_size(9)`
  - Kills detail: 9pt → `get_scaled_size(9)`
  
- 💰 **Other Labels** (`UI/dialogs.py`, 12 labels modified):
  - Money label: 9pt bold → `get_scaled_size(9)`
  - Banner placeholder: 9pt italic → `get_scaled_size(9)`
  - Rank title: 16pt bold → `get_scaled_size(16)` (19.2pt@125%, 24.0pt@150%, 32.0pt@200%)
  
- 🏆 **Achievements Panel** (`UI/dialogs.py`, 12 labels modified):
  - Titles (6 labels): 9pt → `get_scaled_size(9)`
  - Progression (6 labels): 9pt bold → `get_scaled_size(9)`
  - Current tier (6 labels): 8pt italic → `get_scaled_size(8)` (9.6pt@125%, 12.0pt@150%, 16.0pt@200%)

**Responsive Configuration Interface**
- 📜 Added QScrollArea for scrollable content area
- 📐 Minimum size increased: 500×400 → 600×500 pixels
- 🖥️ Comfortable initial size: 700×700 pixels (instead of minimal)
- ↕️ Automatic scrolling if window resized (prevents compression)
- 🔲 Optimized margins:
  - Main layout: 0px (no margin around scroll)
  - Content widget: 10px (spacing around content)
- 🏗️ Hierarchical architecture:
  ```
  QDialog
  └── QVBoxLayout (main_layout)
      ├── QScrollArea (widgetResizable=True)
      │   └── QWidget (content_widget)
      │       └── QVBoxLayout (content_layout)
      │           ├── QGroupBox (Paths)
      │           ├── QGroupBox (General) ← Font Scale ComboBox here
      │           ├── QGroupBox (Server)
      │           ├── QGroupBox (Debug)
      │           └── QGroupBox (Misc)
      └── QDialogButtonBox (Save/Cancel)
  ```

**Integration in main.py**
- 🔧 `apply_font_scale(app)` function (lines 881-888):
  - Wrapper to apply scaling at startup
  - Retrieves font_scale from config (default 1.0)
  - Calls `apply_font_scale_manager()` from theme_manager
  - Called after `apply_theme()` in `main()`
  
- 💾 Configuration save (lines 697-703):
  - Change detection: Compares old_font_scale vs new_font_scale
  - Value retrieval: `dialog.font_scale_combo.currentData()`
  - Save: `config.set("font_scale", new_font_scale)`
  - Immediate application: `apply_font_scale(QApplication.instance(), new_font_scale)`

**Compatibility Management**
- 📦 Compatibility with existing config.json:
  - Default value: 1.0 (100%)
  - Automatic migration: Old configs without font_scale use 1.0
  - Intermediate values (e.g. 1.1): Rounded to nearest value (1.0 or 1.25)
- 🔄 Loading in UI:
  - `findData()` to find exact value in ComboBox
  - If not found: Nearest neighbor search algorithm
  - Minimum distance calculation: `abs(scale_value - current_font_scale)`

### 🧰 Modified

**Font Scaling System**
- 🔄 **Slider Replacement with ComboBox** (`UI/dialogs.py`, lines 2212-2217):
  - ❌ **Old system (QSlider)**: 4 positions, range 100-150, step 10
  - ❌ Possible values: [100%, 110%, 125%, 150%]
  - ❌ Complex retrieval: `slider.value() / 100`
  - ✅ **New system (QComboBox)**: 5 items with associated data
  - ✅ Possible values: [100%, 125%, 150%, 175%, 200%]
  - ✅ Direct retrieval: `currentData()` returns float (1.0, 1.25, etc.)
  - 📊 More intuitive interface and extended range (100% → 200% instead of 100% → 150%)

- 🎨 **UI/dialogs.py Modification - ComboBox Structure**:
  - Removed old slider code (lines ~2212-2241, previous version)
  - Added QComboBox with values:
    ```python
    self.font_scale_combo = QComboBox()
    self.font_scale_values = [1.0, 1.25, 1.5, 1.75, 2.0]
    for scale in self.font_scale_values:
        self.font_scale_combo.addItem(f"{int(scale * 100)}%", scale)
    ```
  - Position: In "General" QGroupBox, below theme selector
  - Translated label: `lang.get("config_font_scale_label")`

- 🔄 **update_fields() Modification - Loading Logic** (`UI/dialogs.py`, lines 2363-2378):
  - Read current config: `current_font_scale = config.get("font_scale", 1.0)`
  - Exact value search: `scale_index = self.font_scale_combo.findData(current_font_scale)`
  - If found (`scale_index != -1`): `setCurrentIndex(scale_index)`
  - **If not found** (compatibility with old values):
    - Nearest neighbor search algorithm
    - Minimum distance calculation: `min_diff = abs(self.font_scale_values[0] - current_font_scale)`
    - Iterate through all values to find closest
    - Select index with minimum distance
  - Examples: 1.1 → 1.0, 1.3 → 1.25, 1.6 → 1.5, 1.9 → 2.0

- 💾 **save_configuration() Modification - Save** (`main.py`, line 698):
  - ❌ **Old**: `new_font_scale = dialog.font_scale_slider.value() / 100`
  - ✅ **New**: `new_font_scale = dialog.font_scale_combo.currentData()`
  - Change detection: `if old_font_scale != new_font_scale`
  - Immediate save: `config.set("font_scale", new_font_scale)`
  - Immediate application: `apply_font_scale(QApplication.instance(), new_font_scale)`

**Responsive Configuration Window**
- 📜 **QScrollArea for Scrollable Content** (`UI/dialogs.py`, lines 2126-2146):
  - Added QScrollArea with `widgetResizable=True`
  - Frameless border: `setFrameShape(QFrame.NoFrame)`
  - All QGroupBox moved into scrollable content_widget
  - Buttons (Save/Cancel) stay at bottom (non-scrollable)

- 📐 **Optimized Window Sizes**:
  - ❌ **Old minimum size**: 500×400 pixels (too small with scaling)
  - ✅ **New minimum size**: 600×500 pixels
  - ✅ **Initial size**: 700×700 pixels (comfortable instead of minimal)
  - Automatic scrolling if window resized (prevents content overlap)

- 🔲 **Optimized Margins**:
  - Main layout (QVBoxLayout): `setContentsMargins(0, 0, 0, 0)`
  - Content widget (QWidget): `setContentsMargins(10, 10, 10, 10)`
  - No margin around scroll → Optimized content

- 🏗️ **Hierarchical Architecture**:
  ```
  ConfigurationDialog (QDialog)
  └── main_layout (QVBoxLayout, margins 0px)
      ├── scroll_area (QScrollArea, widgetResizable, NoFrame)
      │   └── content_widget (QWidget, margins 10px)
      │       └── content_layout (QVBoxLayout)
      │           ├── paths_group (QGroupBox "Paths")
      │           ├── general_group (QGroupBox "General")
      │           │   ├── theme_combo (QComboBox)
      │           │   └── font_scale_combo (QComboBox) ← New
      │           ├── server_group (QGroupBox "Server")
      │           ├── debug_group (QGroupBox "Debug")
      │           └── misc_group (QGroupBox "Misc")
      └── buttons (QDialogButtonBox) ← Bottom, fixed
  ```

**Scaled Elements - Preserved Visual Hierarchy**
- 📊 **Herald Progress Dialog** (`main.py`, lines 368, 375, 387):
  - 3 labels modified with `get_scaled_size()`
  - Import added: `from Functions.theme_manager import get_scaled_size`
  - Title (12pt): Larger than detail
  - Detail (10pt): Normal size
  - Wait (9pt): Smaller but readable

- 📈 **RvR Statistics** (`UI/dialogs.py`, lines 288, 300, 312):
  - 3 detail labels modified: Solo Kills, Deathblows, Kills
  - All 9pt × scale → Uniform text for visual consistency

- 💰 **Money Label** (`UI/dialogs.py`, line 469):
  - 9pt bold → `get_scaled_size(9)`
  - Style preserved: "font-weight: bold"

- 🏴 **Banner Label** (`UI/dialogs.py`, line 687):
  - 9pt italic → `get_scaled_size(9)`
  - Style preserved: "font-style: italic"

- 👑 **Rank Title** (`UI/dialogs.py`, line 997):
  - 16pt bold → `get_scaled_size(16)`
  - Largest: 19.2pt@125%, 24.0pt@150%, 32.0pt@200%
  - Maximum visual emphasis

- 🏆 **Achievements Panel** (`UI/dialogs.py`, lines 1162-1213):
  - **12 labels modified** organized in visual hierarchy:
    - 📊 **Titles** (6 labels, lines 1162, 1167, 1173, 1202, 1207, 1213):
      - 9pt × scale → `get_scaled_size(9)`
      - First column: Master Level, Champion Level, Realm Rank
      - Second column: Bounty Points, Kills, Deathblows
    - 📈 **Progression** (6 labels, adjacent positions):
      - 9pt bold × scale → `get_scaled_size(9)`
      - Style: "font-weight: bold"
      - Highlights current values
    - 🎯 **Current tier** (6 labels, adjacent positions):
      - 8pt italic × scale → `get_scaled_size(8)`
      - Style: "font-style: italic; color: #666"
      - Smallest but remains readable: 9.6pt@125%, 12.0pt@150%, 16.0pt@200%

- 📄 **Progress Dialog** (`UI/dialogs.py`, lines 1650, 1657, 1669):
  - 3 labels with hierarchy: Title (12pt) > Text (10pt) > Detail (9pt)
  - Proportional scaling preserves visual ratio

**Application Configuration**
- 📝 `Functions/config_manager.py` (line 57):
  - Added `"theme": "default"` key to default configuration
  - Automatic save on theme change

**Configuration Interface**
- 🎛️ `UI/dialogs.py` (lines 2186-2196):
  - Added QComboBox for theme selection
  - Import `get_available_themes` from `Functions.theme_manager`
  - Alphabetical sorting of themes by translated name
  - Translated label via `lang.get("config_theme_label")`
- 🔄 `UI/dialogs.py` (lines 2332-2338):
  - Loading current theme in update_fields()
  - Automatic selection of current theme in ComboBox

**Main Application**
- 🚀 `main.py` (lines 685-694):
  - Theme change detection in save_configuration()
  - Immediate application of new theme if modified
  - Call to `apply_theme()` with QApplication.instance()
- 🎨 `main.py` (lines 883-887):
  - New `apply_theme(app)` function for startup loading
  - Theme reading from config.json
  - Call to `theme_manager.apply_theme()`

**PyInstaller Configuration**
- 📦 `DAOC-Character-Manager.spec`:
  - Added `('Themes', 'Themes')` in `datas` section for bundling
  - Added `'Functions.theme_manager'` to `hiddenimports`
  - Ensures JSON files inclusion in executable

**Path Management**
- 🗂️ `Functions/theme_manager.py`:
  - Using `get_resource_path("Themes")` instead of `Path(__file__).parent.parent`
  - Compatible with development (absolute path) and frozen modes (`sys._MEIPASS`)
  - Import from `Functions.path_manager.get_resource_path`

**Translations**
- 🌍 Language files (`Language/*.json`):
  - Existing keys reused: `theme_light`, `theme_dark`, `config_theme_label`
  - No modifications needed (keys already present)

### 🐛 Fixed

**Font Scaling System**
- 🔧 **CSS Scaling Regex Fix** (`Functions/theme_manager.py`, lines 179-211):
  - ❌ **Initial problem**: IndexError during CSS parsing
  - 🐞 **Cause**: Regex `r'(\d+(?:\.\d+)?)pt\b'` has only one capture group (size)
  - 🐞 **Error**: Attempted access `match.group(2)` in single `scale_font_size()` function
  - ✅ **Solution**: Separated into two distinct functions with dedicated callbacks
    - `scale_pt(match)`: Handles only `pt` sizes
    - `scale_px(match)`: Handles only `px` sizes (font-size property)
  - ✅ **Regex patterns**:
    - Points: `r'(\d+(?:\.\d+)?)pt\b'` → Captures "9.5" in "9.5pt"
    - Pixels: `r'font-size:\s*(\d+(?:\.\d+)?)px\b'` → Captures "10" in "font-size: 10px"
  - ✅ **Stylesheet application**:
    ```python
    stylesheet = re.sub(r'(\d+(?:\.\d+)?)pt\b', scale_pt, stylesheet)
    stylesheet = re.sub(r'font-size:\s*(\d+(?:\.\d+)?)px\b', scale_px, stylesheet)
    ```
  - ✅ **Validated test**: "9pt" → "13.5pt" @ 150% scaling ✓

- 📐 **Configuration Window Overlap Fix** (`UI/dialogs.py`, lines 2126-2146):
  - ❌ **Problem**: "the bigger you make it, the more the information overlaps"
  - 🐞 **Cause**: QFormLayout compresses content instead of scrolling
  - 🐞 **Symptoms**:
    - Minimum size 500×400 too small with high font scaling
    - No scrolling → Overlapping labels
    - Unreadable content at 150%+ on small screens
  - ✅ **Solution 1 - QScrollArea**:
    - Added QScrollArea with `widgetResizable=True`
    - All QGroupBox in scrollable content_widget
    - Save/Cancel buttons stay at bottom (fixed)
  - ✅ **Solution 2 - Optimized Sizes**:
    - Minimum: 500×400 → 600×500 pixels (+100×100)
    - Initial: 500×400 → 700×700 pixels (comfortable)
  - ✅ **Solution 3 - Margins**:
    - main_layout: 0px (no margin around scroll)
    - content_layout: 10px (content spacing)
  - ✅ **Result**: No overlap even at 200% scaling on small screens

- 📝 **get_scaled_size Import Fix** (`UI/dialogs.py`, line 28):
  - ❌ **Problem**: NameError when using get_scaled_size() in labels
  - 🐞 **Cause**: Function not imported at file beginning
  - ✅ **Solution**: Added global import:
    ```python
    from Functions.theme_manager import get_scaled_size
    ```
  - ✅ **Impact**: 15 labels in UI/dialogs.py can now use the function
  - ✅ **Location**: Line 28 after other Functions.* imports

- 🔄 **Startup Scaling Application Fix** (`main.py`, lines 881-888):
  - ❌ **Problem**: Font scale not applied at application launch
  - 🐞 **Cause**: No call to apply_font_scale() in main()
  - ✅ **Solution**: Added wrapper function and call after apply_theme()
    ```python
    def apply_font_scale(app):
        from Functions.theme_manager import apply_font_scale as apply_font_scale_manager
        font_scale = config.get("font_scale", 1.0)
        apply_font_scale_manager(app, font_scale)
    ```
  - ✅ **Call**: Line 917 in main() after apply_theme(app)
  - ✅ **Execution order**:
    1. apply_theme(app) → Applies theme + scales theme CSS
    2. apply_font_scale(app) → Applies base scaling + rescales global CSS
  - ✅ **Result**: Scaling active from application opening

- 🎨 **Inline Stylesheet Scaling Fix** (18 labels modified):
  - ❌ **Problem**: Labels with inline Python stylesheets not scaled
  - 🐞 **Cause**: Stylesheets built with hardcoded sizes (e.g. "font-size: 9pt")
  - ✅ **Solution**: Replaced with f-strings using get_scaled_size()
    - **Before**: `label.setStyleSheet("font-size: 9pt; font-weight: bold;")`
    - **After**: `label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt; font-weight: bold;")`
  - ✅ **Modified files**:
    - `main.py`: 3 labels (Herald progress dialog)
    - `UI/dialogs.py`: 15 labels (RvR stats, money, banner, rank, achievements, progress)
  - ✅ **Format**: `.1f` for 1 decimal (consistent with regex scaling)

**Theme System**
- 🌍 Fixed automatic translation of theme names:
  - Correct usage of `lang.get(key)` without second parameter
  - LanguageManager.get() accepts 2 arguments: self and key
  - Returns key itself if translation missing (automatic fallback)
- 📋 Replaced hardcoded names with translation keys in JSON:
  - `default.json`: "Windows Vista (Par défaut)" → "theme_light"
  - `dark.json`: "Sombre" → "theme_dark"
- 🔧 Automatic detection of translation keys ("theme_" prefix):
  - If key starts with "theme_", calls `lang.get()`
  - Otherwise, direct name usage (custom themes compatibility)

**Portability**
- 📦 Fixed absolute path for PyInstaller:
  - Using `get_resource_path()` in `get_themes_dir()`
  - Works in development and frozen modes
  - Correct access to JSON files in .exe bundle

### � Technical Information - Font Scaling System

**Associated Commits for Font Scaling:**
- `a6fdec0` - feat: Add comprehensive font scaling system with ComboBox selector
- `3f059cf` - Merge branch '107_Imp_Text_Size' into main (--no-ff)

**Modified Files (7 files, +198/-27 lines):**
1. **Functions/theme_manager.py** (+115 lines):
   - 138 → 253 total lines
   - 4 new functions (apply_font_scale, scale_stylesheet_fonts, get_scaled_size, get_scaled_stylesheet)
   - 2 regex patterns for CSS parsing (pt and px)
   - Separate callbacks to avoid IndexError

2. **UI/dialogs.py** (+42 lines, -15 lines):
   - 4494 total lines
   - QComboBox replaces QSlider (lines 2212-2217)
   - QScrollArea responsive architecture (lines 2126-2146)
   - update_fields() with findData() (lines 2363-2378)
   - 15 labels modified with get_scaled_size()
   - Import get_scaled_size (line 28)

3. **main.py** (+18 lines, -3 lines):
   - 958 total lines
   - apply_font_scale() wrapper (lines 881-888)
   - save_configuration() with currentData() (line 698)
   - 3 Herald dialog labels modified (lines 368, 375, 387)
   - apply_font_scale(app) call at startup (line 917)

4. **Configuration/config.json** (+1 line):
   - Added "font_scale": 1.0 key

5. **Language/fr.json** (+1 line):
   - "config_font_scale_label": "Taille du texte"

6. **Language/en.json** (+1 line):
   - "config_font_scale_label": "Text size"

7. **Language/de.json** (+1 line):
   - "config_font_scale_label": "Textgröße"

**Scaling Statistics:**
- **Scaled UI elements**: 18 labels total
  - Herald dialog: 3 labels (main.py)
  - RvR stats: 3 labels (UI/dialogs.py)
  - Miscellaneous: 12 labels (money, banner, rank, achievements, progress)
- **Scale values**: 5 options (1.0, 1.25, 1.5, 1.75, 2.0)
- **Scaling range**: 100% → 200% (doubling possible)
- **Regex patterns**: 2 patterns (pt units and px units)
- **Helper functions**: 2 functions (get_scaled_size, get_scaled_stylesheet)
- **Core functions**: 2 functions (apply_font_scale, scale_stylesheet_fonts)

**Technical Architecture:**
- **Two-Tier Scaling**:
  - Tier 1 (Base): QApplication.setFont() for global base font
  - Tier 2 (CSS): Regex parsing for CSS stylesheets (themes + inline)
- **Compatibility**:
  - Config without font_scale → Default 1.0 (100%)
  - Intermediate values → Nearest neighbor algorithm
  - Old configs → Transparent automatic migration
- **Responsive UI**:
  - QScrollArea for high scaling
  - Adaptive sizes (600×500 min, 700×700 initial)
  - No overlap up to 200%

### �🔚 Removed

**External Libraries**
- ❌ Removed qt-material usage attempt (conflicts with custom styles)
- ✅ Native solution without additional dependencies

---

**Associated commits:**
- `c2f97c1` - feat: Add JSON-based theme system with two themes
- `317bd16` - fix: Make theme system portable and multilingual

---

# ✨✨ v0.107 - 2025-11-10

### 🎉 Added

**Version Check System**
- 🔄 Automatic check on startup (background thread, non-blocking)
- 📊 Current version display from `Functions/version.py` (__version__ constant)
- 🌐 Latest version display from GitHub (version.txt on main branch)
- 🔘 Manual "🔄 Check" button (disabled during check, 5s timeout)
- ✅ Visual indicators: ✓ green (up to date) / ✗ red (outdated)
- 🔗 Clickable download link to GitHub Releases (visible if update available)
- ℹ️ "Information" section (renamed from "Currency")
- 🌍 Complete FR/EN/DE translations
- 📚 Libraries: `requests` (GitHub HTTP) and `packaging` (semantic comparison)
- 🔐 5s timeout to avoid network blocking
- 📝 Module `Functions/version_checker.py`: check_for_updates()
- 🧵 VersionCheckThread class (QThread) for async execution
- 🎨 Dynamic styles: blue (#0078d4) with hover (#005a9e)

**Class Banner System**
- 🖼️ Visual banners for 44 DAOC classes (Albion/Hibernia/Midgard)
- 📱 Adaptive responsive design (window height)
- 🎨 Realm-based design: Red (Albion), Green (Hibernia), Blue (Midgard)
- 📐 Dimensions: 150px width × responsive height
- 📁 JPEG format, location: `Img/Banner/{Realm}/{class}.jpg`
- 🔄 Automatic class/realm update
- 📦 PyInstaller (.exe) compatible via `get_resource_path()`
- 🔁 PNG fallback if JPG missing
- 🎯 Display on left side of character sheet
- 💪 QSizePolicy(Expanding, Expanding) for resizing

**Complete Herald Statistics**
- ⚔️ **RvR Section**: Tower Captures, Keep Captures, Relic Captures
- 🗡️ **PvP Section**: Solo Kills, Deathblows, Kills (Alb/Hib/Mid details with colors)
- 🐉 **PvE Section**: Dragons, Legions, Mini Dragons, Epic Encounters, Epic Dungeons, Sobekite
- 💰 **Wealth Section**: Currency format "18p 128g 45s 12c" (9pt bold)
- 🏆 **Achievements Section**: 16 achievements in 2 columns of 8
- 📊 Scraping from Herald with `character_profile_scraper.py`
- 🔢 Thousand separator handling
- 🎨 Realm colors: Red #C41E3A (Alb), Green #228B22 (Hib), Blue #4169E1 (Mid)
- 📋 Display format: `Kills: 4,715 → Alb: 1,811 | Hib: 34 | Mid: 2,870`
- 🔄 "Refresh Stats" button with intelligent state management
- 📝 Automatic achievements scraping (`&t=achievements`)

**"Information" Button on Statistics**
- ℹ️ Button next to "Refresh Stats"
- 📝 Explanatory message: cumulative statistics since character creation
- ⚠️ Clarification: no seasonal stats, only global total
- 🌐 Data source: Herald Eden only provides cumulative total
- 🌍 FR/EN/DE translations

**User Interface**
- 📐 50/50 Layout: RvR/PvP side by side, PvE/Wealth side by side
- 📏 QGridLayout for perfect PvP alignment (3 columns)
- 📊 Realm details on same line (compact)
- 🔲 PvE section: 5px spacing, vertical separator
- 📋 Achievements section: full width, 2 columns, QScrollArea 200px max
- 🖥️ Minimum width 250px per section
- 🎯 Equal stretch factor for fair distribution

### 🧰 Modified

**Version Check System**
- 📁 Current/latest version separation: `Functions/version.py` vs `version.txt`
- 🔄 version.txt becomes GitHub reference only (no longer local file)
- 🎨 State display with color codes: green (up to date), red (outdated), orange (error)
- 🔗 Download link URL: `https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest`
- 👁️ Link visibility: show/hide based on update status

**Statistics Interface**
- 🖥️ QScrollArea removal from all sections (RvR/PvP/PvE/Wealth/Achievements)
- 📏 Full height display on large screens
- 📱 Natural window scroll on small screens
- 📄 setWordWrap(False) on PvP labels (avoid line breaks)
- 🔲 PvE vertical separator between columns
- 📊 Reduced PvE spacing (5px instead of 8px)
- 🏆 Achievements: 2px vertical spacing for compactness

**"Refresh Stats" Button**
- 🎯 State management: grayed during Herald startup validation
- ⏸️ Automatic disable during scraping
- 🔒 Guaranteed reactivation with `try/finally` pattern
- 🏁 Flag `herald_scraping_in_progress` set BEFORE setText()
- 📢 Detailed error messages for 4 scrapers (RvR/PvP/PvE/Wealth)
- ✅ Herald validation completed before activation
- 🔗 Signal `status_updated` for automatic reactivation

**Currency Display**
- 🔤 Font size: 11pt → 9pt (visual harmony)
- 💪 Bold style preserved
- 💱 Direct format `str(money)` without numeric formatting

**Herald Button State Management**
- 🔐 New flag `herald_scraping_in_progress` (global tracking)
- 🎯 Method `_is_herald_validation_done()` to check startup thread
- 🔄 Callback `_on_herald_validation_finished()` for auto reactivation
- ⚡ `QApplication.processEvents()` for immediate UI update
- 🔒 try/finally guarantees reactivation on all execution paths

### 🐛 Fixed

**Version Check System**
- 🔧 Fix TypeError `lang.get()`: removed default parameter (takes 2 args not 3)
- 📁 Fix version separation: created `Functions/version.py` with __version__
- 🔄 Fix version.txt modification affected both current AND latest
- 💡 Solution: code constant (__version__) for current, GitHub file for latest

**"Refresh Stats" Button**
- 🔘 Fix button active during Herald startup validation
- 🚫 Fix button grayed after update dialog cancellation
- ♻️ Fix reactivation with `try/finally` for all paths (return, exception, success)
- 🏁 Fix race condition: flag set BEFORE setText() triggers signal
- 🔍 Fix startup validation: `_is_herald_validation_done()` checks thread.isRunning()
- 📢 Fix multiple exit points without button reactivation

**Error Messages**
- 📝 Fix incomplete messages: added missing PvE and Wealth
- 📢 Display ALL errors (4 scrapers) instead of 2
- 🎯 Format: `❌ RvR/PvP/PvE/Wealth: {error_msg}`

**Currency Formatting**
- 🔢 Fix TypeError: `f"{money:,}"` failed on string "18p 128g"
- 💱 Solution: `str(money)` direct display without numeric format
- ✅ Herald format preserved: "18p 128g 45s 12c"

**Herald Connection Test**
- 💥 Fix brutal crash on connection errors
- 🔐 Added `finally` block for clean WebDriver closure
- 📝 Complete stacktrace logging for diagnosis
- ✅ Identical pattern to `search_herald_character()` fix v0.106

**Statistics Display**
- 📱 Fix truncated sections on small screens (QScrollArea removal)
- 📏 Fix full section height (scroll removal limited height)
- 📄 Fix line breaks: `setWordWrap(False)` on PvP detail labels
- 🖥️ Natural scroll at window level instead of per-section scroll
- 🎯 Complete display on large screens with optimal space usage

**Debug Files**
- 🗑️ Removal of automatic HTML creation: `debug_herald_after_cookies.html`, `debug_wealth_page.html`
- 📝 Added .gitignore for protection
- 🧹 Cleanup of 3 debug file creation sections (lines ~155, ~235, ~295)
- 📊 Logs preserved for debugging (HTML size, URL, etc.)

**Code Quality**
- 🧹 Cleanup of ~20 temporary `[DEBUG]` logs
- 📝 Preserved essential logs: error, info, warning
- 🎯 Production-ready clean logs

### 🔚 Removed

**Debug Code**
- ❌ Removed temporary `[DEBUG]` logs after fix validation
- ❌ Removed automatic debug HTML file creation
- ❌ Cleanup of active debug code in production

**QScrollArea**
- ❌ QScrollArea removal from RvR section (lines 229-275)
- ❌ QScrollArea removal from PvP section (lines 276-365)
- ❌ QScrollArea removal from PvE section (lines 373-456)
- ❌ QScrollArea removal from Wealth section (lines 463-475)
- ❌ QScrollArea removal from Achievements section (lines 483-504)

---

## 📋 Technical Information - v0.107

**Created Files**
- `Functions/version.py`: Constant __version__ = "0.107"
- `Functions/version_checker.py`: GitHub verification module

**Modified Files**
- `Functions/ui_manager.py`: Version check interface + visual indicators + download link
- `UI/dialogs.py`: QScrollArea removal, button state management, stats display
- `Language/*.json`: Added translation keys (version_check_download, stats_info_*)
- `version.txt`: Represents latest GitHub version
- `requirements.txt`: Added requests>=2.31.0, packaging>=23.0

**Associated Commits**
- `42a63a9`: Fix version constant separation (created Functions/version.py, separated current/GitHub version)
- `62fe01d`: Add download link and red text (clickable download link to Releases)
- `93f2c54`: Fix lang.get() TypeError (removed default parameter)
- `8f7148b`: Add visual indicators (✓/✗) (green/red visual indicators)
- `9c4708e`: Remove scroll areas, preserve full height (QScrollArea removal RvR/PvP/PvE/Wealth)
- `1bec23c`: Remove scroll from Achievements (QScrollArea removal Achievements)

**Testing and Validation**
- ✅ 25/25 Herald connection tests successful (100% stable)
- ✅ 0 crash after button fixes
- ✅ All execution paths tested (success, error, cancellation)
- ✅ Startup, scraping, update dialog validation

**Prerequisites**
- Valid Herald cookies
- Character level 11+ (PvP stats)
- Herald URL configured for character sheet
- Internet connection (version check)

---

# ✨✨ v0.106 - 2025-11-08

### 🎉 Added

**Complete Code Refactoring**
- 🌍 Complete FR → EN translation: 582 French comments translated (975 modifications)
- 🧹 Import optimization: 51 unused imports removed via AST analysis
- 📝 Code cleanup: 74 excessive blank lines removed (max 2 consecutive)
- 💾 Default configuration: `default_season: "S3"` added
- 🖱️ Default configuration: `manual_column_resize: true` added
- 📊 Global impact: 19,941 total lines, 792.58 KB
- 📦 Estimated exe reduction: -1 to 2 MB (-2 to 4%)

**Improved Backup System**
- 📄 Clear filenames: character name inclusion
- 🔤 Format: `backup_YYYYMMDD_HHMMSS_CharacterName.zip`
- 🔀 Operation distinction: `backup_..._CharacterName.zip` vs `backup_..._multiple_characters.zip`
- 🔍 Immediate character identification
- 📂 More intuitive backup navigation

**Herald Performance Optimization**
- ⚡ Timeout reduction: complete analysis of 21 `time.sleep()` occurrences
- 📉 Character search: 26.5s → 21.9s (-17.4%)
- ⏱️ Gain per search: -4.6 seconds
- 🔄 Total duration 25 searches: 662.3s → 546.4s (-1.9 min)
- 💯 Stability: 100% (std dev 0.3s, range 18.7-19.6s)
- 📚 Documentation: `HERALD_TIMEOUTS_ANALYSIS.md` + `HERALD_PHASE1_TEST_REPORT.md`

### 🧰 Modified

**Code Refactoring**
- 🗂️ File impact: 11 managers (Functions/), 4 UI, 42 scripts, 4 tools, 2 tests, main.py
- 📉 Net reduction: -47 lines (607 deleted, 560 added)
- 🎯 51 fewer imports = lighter bundle
- 💻 Cleaner bytecode

**Default Configuration**
- 🎭 Default season: S3 (config_manager.py, character_actions_manager.py, dialogs.py)
- 🖱️ Column resizing: manual by default (tree_manager.py, main.py, dialogs.py)

### 🐛 Fixed

**Critical Bugs**
- 🚨 Fix missing imports after aggressive optimization
  - character_actions_manager.py: Added `QMessageBox, QInputDialog, QDialog, QLineEdit`
  - armor_manager.py: Added `ensure_armor_dir` from `path_manager`
  - tree_manager.py: Added `QHeaderView`
  - main.py: Restored Qt and config imports
- 📁 Fix Logs folder creation only if `debug_mode = true`
- 🏁 Fix `MIGRATION_FLAG_ERROR` if Characters folder doesn't exist
- 🔢 Fix version display: v0.104 → v0.106 corrected

**Fix Herald Search Crash**
- 💥 Fix brutal crash on Herald search errors
- 🔐 Added `finally` block for clean WebDriver closure
- 📝 Complete stacktrace logging for diagnosis
- ✅ 100% stable validated by automated tests
- 📋 Test script: `Scripts/test_herald_stability.py`

**Fix Critical Backup**
- 🔧 Fix path resolution for backups
- 💾 Automatic backup on create/update/delete functional
- 🖱️ Manual backup "folder not found" fixed
- 📝 Misleading ERROR messages on first startup fixed
- 📊 Backup folder creation logs added
- ✅ Daily startup backup works

### 🔚 Removed

**Code Cleanup**
- ❌ 51 unused imports removed (cookie_manager: 11, eden_scraper: 6, main: 5, backup_manager: 3)
- ❌ 74 excessive blank lines removed
- ❌ 1 debug print removed

---

## 📋 Technical Information - v0.106

**Modified Files**
- `Functions/`: 11 managers (complete EN comments refactoring)
- `UI/`: 4 files (dialogs, delegates, debug)
- `Scripts/`: 42 test/utility files
- `Tools/`: 4 editor files
- `Test/`: 2 Herald files
- `main.py`: Main application
- `Functions/backup_manager.py`: Added character name parameter + filename generation
- `Functions/character_actions_manager.py`: Delete, rename with new backup names
- `UI/dialogs.py`: Update rank/info/armor, mass import with new names
- `main.py`: Update from Herald with new names
- `Functions/eden_scraper.py`: Clean closure + logs
- `Functions/backup_manager.py`: Path resolution + improved logs
- `Functions/character_manager.py`: Folder creation log
- `Functions/cookie_manager.py`: Folder creation log

**Global Impact**
- 19,941 total lines, 792.58 KB
- -47 net lines (607 deleted, 560 added)
- Estimated exe reduction: -1 to 2 MB (-2 to 4%)
- 51 fewer imports = lighter bundle
- Cleaner bytecode

**Associated Commits**
- `339a5a8`: Add character name to backup filenames for clarity
- `9e84494`: Ensure scraper is properly closed in all error paths
- `a351226`: Add Herald search stability test script
- `175c42b`: Improve logging for first startup
- `9d5158d`: Add INFO logs when backup directories are created
- `20331d6`: Use proper folder resolution for backups (CRITICAL)
- `83f99e9`: Improve backup error message when no characters exist

**Created Documentation**
- `HERALD_TIMEOUTS_ANALYSIS.md`: Complete analysis of 21 time.sleep() occurrences
- `HERALD_PHASE1_TEST_REPORT.md`: Optimization validation test report
- `Reports/CODE_REFACTORING_REPORT_v0.106.md`: Complete refactoring report

**Testing and Validation**
- ✅ 100% Herald search stability (25 tests)
- ✅ 0 crash after fixes
- ✅ Automatic/manual/daily backups functional
- ✅ Application starts with all correct imports

---

# ✨✨ v0.104 - 2025-10-29

### 🎉 Added

**Architecture - Complete Refactoring**
- 🏗️ Extracted `main.py` (1277 lines) to 3 new managers
- 📝 `Functions/ui_manager.py` (127 lines): Interface element management
- 🌳 `Functions/tree_manager.py` (297 lines): Character list management
- ⚙️ `Functions/character_actions_manager.py` (228 lines): Character actions
- 📉 `main.py` reduced to 493 lines (-61%)
- 🎯 Clear separation of responsibilities (SRP)
- 🏛️ Partial MVC architecture

**Migration & Security**
- 📁 New structure: `Characters/Season/Realm/Character.json` (vs `Characters/Realm/Character.json`)
- 🔄 Automatic migration on startup (with confirmation)
- 🏷️ Marker file `.migration_done` to avoid multiple migrations
- 💬 Trilingual confirmation popup (FR/EN/DE)
- 💾 Automatic ZIP backup: compression with 70-90% space savings
- ✅ Integrity verification: automatic archive testing after creation
- ↩️ Automatic rollback: auto deletion on error
- 🔍 Complete JSON validation: corrupted file detection
- 📋 Copy verification: each file compared after copy
- 🧹 Secure cleanup: old folder deleted only if 100% files migrated
- 🛡️ Overwrite prevention: verification before writing
- 📦 ZIP archive: `Backup/Characters/Characters_backup_YYYYMMDD_HHMMSS.zip`
- 📝 Error messages translated in 3 languages
- 📊 Detailed logs for diagnosis
- 📈 Progress interface with percentage bar

**Interface & User Experience**
- 📊 New **Class** column: displayed by default
- 🧬 New **Race** column: hidden by default
- 👁️ Enable/disable via Display > Columns
- 🎚️ Realm Rank: replaced sliders with dropdowns
  - 🔢 Rank menu (1-14)
  - 📊 Level menu (L0-L10 for rank 1, L0-L9 for others)
  - 🎨 Rank title displayed with realm color
- 💾 Automatic rank saving: "Apply" button removed
- 🖱️ Rank/level modifications applied automatically
- 📋 Traditional Windows menu: replaced toolbar
  - 📂 File menu: New Character, Settings
  - 👁️ Display menu: Columns
  - ❓ Help menu: About

**Development Tools**
- 🧹 `Tools/clean_project.py`: Automatic project cleanup
- 🗑️ Temporary folder deletion (Backup, build, dist, Characters, Configuration, Logs)
- 🧼 Python cache cleanup (__pycache__, .pyc, .pyo, .pyd)
- 🔍 Simulation mode with --dry-run
- 🚀 Automatic Git creation and push
- 💬 Interactive interface with confirmations

**Documentation**
- 📚 `REFACTORING_v0.104_COMPLETE.md`: Detailed before/after comparison
- 💾 `BACKUP_ZIP_UPDATE.md`: ZIP backup guide
- 🔒 `MIGRATION_SECURITY.md`: Complete security guide
- 📖 Updated README: Revised project structure
- 📑 Enriched INDEX.md: Section dedicated to v0.104
- 📁 CHANGELOGs moved to `Documentation/`
- 🌍 Linguistic READMEs (EN/DE) moved
- 📝 New main `CHANGELOG.md` at root

**Tests**
- 🧪 `Scripts/simulate_old_structure.py`: Creates old structure for tests
- 📦 `Scripts/test_backup_structure.py`: Verifies ZIP backup creation

### 🧰 Modified

**Performance**
- ⚡ Load time: -22% (~0.45s → ~0.35s)
- 🔄 List refresh: -33% (~0.12s → ~0.08s for 100 chars)
- 💾 Memory usage: -8% (~85MB → ~78MB)
- 🖼️ Icon cache: single load on startup
- 📉 Redundant calls reduction: -60%
- 📦 Lazy loading of resources
- 🔍 Data query optimization

**Code Cleanup**
- 📉 Cyclomatic complexity main.py: -71%
- 📏 Functions > 50 lines: -83%
- 📦 Imports in main.py: -36%

### 🐛 Fixed

**Fixed Bugs**
- ✅ Improved maintainability
- ✅ Increased testability
- ✅ More readable and modular code
- ✅ Simplified extensibility

### 🔚 Removed

**Cleanup**
- ❌ Obsolete test scripts (8 files)
- ❌ Unused imports
- ❌ Duplicated code

---

## 📋 Technical Information - v0.104

**Created Files**
- `Functions/ui_manager.py` (127 lines): Interface element management
- `Functions/tree_manager.py` (297 lines): Character list management
- `Functions/character_actions_manager.py` (228 lines): Character actions
- `Functions/migration_manager.py`: Complete migration manager
- `Tools/clean_project.py`: Automatic project cleanup script
- `Scripts/simulate_old_structure.py`: Creates old structure for tests
- `Scripts/test_backup_structure.py`: Verifies ZIP backup creation

**Modified Files**
- `main.py`: Reduced to 493 lines (-61% from 1277 lines)
- Folder structure: `Characters/Season/Realm/Character.json`

**Created Documentation**
- `REFACTORING_v0.104_COMPLETE.md`: Detailed before/after comparison
- `BACKUP_ZIP_UPDATE.md`: ZIP backup guide
- `MIGRATION_SECURITY.md`: Complete security guide
- `README.md`: Revised project structure
- `INDEX.md`: Section dedicated to v0.104
- New main `CHANGELOG.md` at root

**Global Impact**
- Load time: -22% (~0.45s → ~0.35s)
- List refresh: -33% (~0.12s → ~0.08s for 100 chars)
- Memory usage: -8% (~85MB → ~78MB)
- Cyclomatic complexity main.py: -71%
- Functions > 50 lines: -83%
- Imports in main.py: -36%
- Redundant calls reduction: -60%

**ZIP Archive**
- Format: `Backup/Characters/Characters_backup_YYYYMMDD_HHMMSS.zip`
- Compression: 70-90% space savings
- Automatic integrity verification
- Automatic rollback on error

**Testing and Validation**
- ✅ Automatic migration with confirmation
- ✅ Complete JSON validation
- ✅ File-by-file copy verification
- ✅ Secure cleanup (100% migrated before deletion)

---

## 📋 Emoji Legend

### Main Sections
- 🎉 **Added**: New features
- 🧰 **Modified**: Changes to existing features
- 🐛 **Fixed**: Fixed bugs
- 🔚 **Removed**: Removed features

### Categories
- 🔄 Verification / Refresh
- 📊 Data / Statistics
- 🌐 Web / Network / GitHub
- 🔘 Buttons / UI
- ✅ Indicators / Validation
- 🔗 Links / Download
- ℹ️ Information
- 🌍 Translations / Languages
- 📚 Libraries / Dependencies
- 🔐 Security / Timeout
- 📝 Modules / Scripts
- 🧵 Threads / Async
- 🎨 Styles / Design
- 🖼️ Images / Banners
- 📱 Responsive / Adaptive
- 📐 Dimensions / Layout
- 📁 Files / Folders
- 📦 Compatibility / Build
- 🔁 Fallback / Alternative
- 🎯 Positioning / Focus
- 💪 Behavior / Properties
- ⚔️ RvR / Combat
- 🗡️ PvP / Players
- 🐉 PvE / Monsters
- 💰 Currency / Wealth
- 🏆 Achievements
- 🔢 Numbers / Formatting
- 📋 Format / Structure
- 🖥️ Interface / Display
- 📏 Size / Spacing
- 🔲 Sections / Areas
- 🔧 Correction / Fix
- 🚫 Disable
- ♻️ Reactivation / Restore
- 🏁 Flags / States
- 🔍 Verification / Search
- 📢 Messages / Notifications
- 💱 Conversion / Parsing
- 💥 Crash / Critical Error
- 🗑️ Deletion / Cleanup
- 🧹 Optimization / Maintenance
- 🎭 Season / Configuration
- 🖱️ Interaction / Clicks
- 🏗️ Architecture / Structure
- 🌳 TreeView / List
- ⚙️ Actions / Operations
- 📉 Reduction / Decrease
- 🔄 Migration / Conversion
- 🏷️ Markers / Flags
- 💬 Messages / Dialogs
- 💾 Save / Backup
- ↩️ Rollback / Cancel
- 🛡️ Protection / Prevention
- 📈 Progress / Evolution
- 🔤 Text / Format
- 🔀 Distinction / Differentiation
- ⏱️ Time / Duration
- 💯 Stability / Reliability
- 🗂️ Organization / Arrangement
- 💻 Code / Development
- 📖 Documentation / Guides
- 📑 Index / Table of Contents
- 🧪 Tests / Validation
- ⚡ Performance / Speed
- 💡 Solution / Resolution
