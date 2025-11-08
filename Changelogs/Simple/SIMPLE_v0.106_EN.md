# v0.106 - Logging System, Cookie Backup & Herald Optimization + Various Fixes# v0.106 - Logging System, Cookies Backup & Herald Optimization



## ✨ Backup Improvement - Clear Filenames (NEW - Nov 7, 2025)

## Eden Herald Fixes & Improvements✅ **Character name** included in backup filenames  

### 🔧 Critical Herald Search Fixes (Nov 7, 2025)✅ Single operations: `backup_characters_20251107_143025_Update_Merlin.zip`  

✅ **CRITICAL FIX**: Brutal crash during Herald search errors resolved  ✅ Mass operations: `backup_characters_20251107_143025_Update_multi.zip`  

✅ Clean WebDriver shutdown in all error paths  ✅ Immediate identification of affected character  

✅ Full stacktrace logging for diagnostics  ✅ Easier backup history navigation  

✅ Stability test: 25/25 successful searches (100% stable)  

✅ Automated test script for continuous validation  ## 🔧 Critical Herald Search Fixes (Nov 7, 2025)

✅ **CRITICAL FIX**: Brutal crash during Herald search errors resolved  

### ⚡ Herald Performance Optimization - Phase 1 (Nov 8, 2025)✅ Proper WebDriver closure in all error paths  

✅ Herald timeout reduction by 17.4% (-4.6 seconds per search)  ✅ Complete stacktrace logging for diagnostics  

✅ 25/25 tests passed (100% stable, 0 crashes)  ✅ Stability test: 25/25 searches successful (100% stable)  

✅ Character search: 26.5s → 21.9s (-4.6 seconds, -17.4%)  ✅ Automated test script for continuous validation  

✅ Search optimizations applied  

✅ Full validation after WebDriver crash fix  ## 🔧 Critical Backup Fixes (Nov 7, 2025)

✅ **CRITICAL FIX**: Path resolution for backups (completely broken)  

### 🍪 Eden Cookies Backup✅ Automatic backups on create/update/delete now work  

✅ Automatic daily cookie backup on startup  ✅ Manual backup works correctly  

✅ Dedicated "Eden Cookies" section in backup window  ✅ Improved logs: INFO instead of ERROR on first startup  

✅ Same options as Characters: compression, storage limit  ✅ Backup directory creation logs now visible  

✅ "Backup Now" button for immediate forced backup  ✅ Clear error message: "No characters to backup" instead of "folder not found"  

✅ "Open Folder" button for direct folder access  

✅ Automatic refresh after backup  ## ⚡ Herald Performance Optimization - Phase 1 (Nov 8, 2025)

✅ Display of backup count and last backup date  ✅ **Herald timeout reduction by 17.4%** (-4.6 seconds per search)  

✅ **25/25 tests successful** (100% stable, 0 crashes)  

### 🔍 Eden Scraping Fixes✅ **Character search: 26.5s → 21.9s** (-4.6 seconds, -17.4%)  

✅ Cookie path fix (PyInstaller fix)  ✅ **7 timeout optimizations applied**:  

✅ Auto-update during character import     • Homepage: 2s → 1s  

✅ Configurable Herald cookies folder     • **Sleep before refresh REMOVED** (major gain)  

✅ Herald connection test protection - Silent crash prevention with full logging     • Refresh: 3s → 2s  

✅ Selenium import error handling - Explicit error messages for missing modules     • Herald load: 4s → 2s  

✅ Driver cleanup protection - Safe driver.quit() with None checks     • Test homepage: 2s → 1s  

   • Test refresh: 3s → 2s  

## Backup Module   • Test Herald: 5s → 3s  

### ✨ Backup Improvements✅ **Total time saved: 1.9 minutes on 25 searches**  

✅ Character name included in backup files  ✅ Full validation after WebDriver crash fix  

✅ Single operations: `backup_characters_20251107_143025_Update_Merlin.zip`  ✅ Documentation: HERALD_PHASE1_TEST_REPORT.md  

✅ Multiple operations: `backup_characters_20251107_143025_Update_multi.zip`  ✅ Automated test script: Scripts/test_herald_stability.py  

✅ Immediate character identification  

✅ Easier backup history navigation  ## 🍪 Eden Cookies Backup

✅ Automatic backups for create/modify/delete now working  ✅ Automatic daily cookies backup on startup  

✅ Manual backup working correctly  ✅ Dedicated "Cookies Eden" section in backup window  

✅ Improved logs: INFO instead of ERROR on first startup  ✅ Same options as Characters: compression, storage limit  

✅ Backup folder creation logs visible  ✅ "Backup Now" button for immediate forced backup  

✅ Clear error message: "No characters to backup" instead of "folder not found"  ✅ "Open Folder" button for direct folder access  

✅ Debug logs for full traceability  ✅ Automatic refresh after backup  

✅ 46+ logs tagged with clear actions  ✅ Display backup count and last backup date  

✅ Action logging added: INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  

✅ Full cookie backup support with retention policies  ## 🔧 New Logging System

✅ Unified format: `LOGGER - LEVEL - ACTION - MESSAGE`  

## 🔧 New Logging System✅ BACKUP logger: all backup module logs tagged  

✅ Unified format: `LOGGER - LEVEL - ACTION - MESSAGE`  ✅ EDEN logger: all Eden scraper logs tagged  

✅ BACKUP logger: all backup module logs tagged  ✅ Standardized actions for each module  

✅ EDEN logger: all Eden scraper logs tagged  ✅ Enhanced debug window with logger filter  

✅ Standardized actions for each module  

✅ Improved debug window with logger filter  ## 🛠️ Log Source Editor (New Tool)

✅ Source code scanner to find all logs  

## 🎨 Interface✅ Interactive editor (table + edit panel)  

### General✅ Detects `logger.xxx()` and `log_with_action()`  

✅ Column configuration fix (12 columns)  ✅ Action ComboBox with history and auto-complete  

✅ Label unification ("Directory")  ✅ Keyboard shortcuts (Enter, Ctrl+Enter)  

✅ Path beginning display  ✅ Filters by logger, level, modified logs  

✅ Robust diagnostic system for unexpected shutdowns  ✅ Direct save to source files  

✅ Functional realm sorting (RealmSortProxyModel added)  ✅ Remembers last edited project  

✅ Herald URL column width optimized (120px minimum)  ✅ Real-time statistics  

✅ Proxy model mapping for sorted operations  

✅ Save button on character sheet no longer closes window  ## 🔍 Eden Scraping Fixes

✅ Uniform Herald button size on character sheet  ✅ Fixed Eden cookies save path (PyInstaller fix)  

✅ Main window layout redesign with Currency section  ✅ Auto-update on character import  

✅ Herald status bar optimizations (buttons 750px × 35px)  ✅ Configurable Herald cookies folder  

✅ Character sheet redesign (Stats renamed, Resists removed, Manage Armor moved)  

## 🧬 Herald Authentication - Simplified & Reliable Detection

### Backup Window✅ Authentication detection based on single definitive criterion  

✅ Side-by-side layout: Characters and Eden Cookies  ✅ Error message 'The requested page "herald" is not available.' = NOT CONNECTED  

✅ Window enlarged to accommodate both sections (1400x800)  ✅ Absence of error message = CONNECTED (can scrape data)  

✅ Smart info refresh after backup  ✅ Coherent logic between `test_eden_connection()` and `load_cookies()`  

✅ "Open Folder" buttons for direct access (Windows/Mac/Linux)  ✅ Invalid cookies correctly detected and reported  

✅ Tests validated with approximately 58 Herald search results  

## 🎯 Various Improvements & Fixes

✅ **Code cleanup**: 74 excessive blank lines removed  ## 🎛️ Herald Button Controls

✅ **Reduced exe size**: Estimated -1 to 2 MB (-2 to 4%)  ✅ "Refresh" and "Herald Search" buttons automatically disabled  

✅ **Version corrected**: About window now shows v0.106  ✅ Disabled when no cookie is detected  

✅ **Default season**: S3 instead of S1  ✅ Disabled when cookies are expired  

✅ **Manual columns**: Manual management enabled by default  ✅ Button state synchronized with connection status  

✅ **Conditional logs**: Logs folder and debug.log created ONLY if debug_mode enabled  ✅ Clear user message: "No cookie detected"  

✅ **Migration fix**: No more "migration_done" error if Characters folder doesn't exist  

✅ **67 production files** modified for optimal code quality  ## 📝 Backup Module

✅ **sys.stderr/stdout None handling** - Fixed noconsole crash (AttributeError on flush)  ✅ 46+ logs tagged with clear actions  

✅ **Thread exception capture** - EdenStatusThread errors no longer crash application  ✅ Actions: INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  

✅ **Full traceback logging** - All errors logged in debug.log for troubleshooting  ✅ Debug logs for complete traceability  

✅ **Backup logging errors fixed** - Proper error messages instead of literal "error_msg" placeholders  ✅ Full support for cookies backup with retention policies  



## 📚 Documentation## 🎨 Interface - Backup Window

✅ CHANGELOG system cleanup and reorganization✅ Side-by-side layout: Characters and Cookies Eden  

✅ Enlarged window to accommodate both sections (1400x800)  
✅ Smart refresh of info after backup  
✅ "Open Folder" buttons for direct access (Windows/Mac/Linux)  

## 🎨 Interface - General
✅ Fixed column configuration (12 columns)  
✅ Unified folder labels ("Directory")  
✅ Improved path display  
✅ Robust diagnostic system for unexpected crashes  
✅ **Functional realm sorting** (added RealmSortProxyModel)  
✅ **Optimized Herald URL column width** (120px minimum)  
✅ **Proxy model index mapping** for sorted operations  
✅ **Character sheet Save button** no longer closes window  
✅ **Herald buttons uniform sizing** in character sheet  
✅ **Main window layout redesign** with Currency section placeholder  
✅ **Herald status bar optimizations** (750px buttons × 35px height)  
✅ **Character sheet redesign** (Statistics section rename, Resistances button removed, Armor manager relocated)  

## 🐛 Bug Fixes - PyInstaller .exe Stability
✅ **sys.stderr/stdout None handling** - Fixed noconsole crash (AttributeError on flush)  
✅ **Herald connection test protection** - Prevented silent crashes with complete error logging  
✅ **Selenium import error handling** - Explicit error messages for missing modules  
✅ **Driver cleanup protection** - Safe driver.quit() with None checks  
✅ **Thread exception catching** - EdenStatusThread errors no longer crash application  
✅ **Complete traceback logging** - All errors logged to debug.log for troubleshooting  
✅ **Backup logging errors fixed** - Proper error messages instead of literal "error_msg" placeholders  

## 🧹 Repository Cleanup
✅ Deletion of 13 temporary debug scripts  
✅ Deletion of 3 debugging HTML files  
✅ Clean and maintainable repository  
✅ Performance optimization  

## 📚 Documentation
✅ CHANGELOGs system cleanup and reorganization