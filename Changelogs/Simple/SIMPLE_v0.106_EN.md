# v0.106 - Logging System, Cookies Backup & Improvements

## 🍪 Eden Cookies Backup (NEW)
✅ Automatic daily cookies backup on startup  
✅ Dedicated "Cookies Eden" section in backup window  
✅ Same options as Characters: compression, storage limit  
✅ "Backup Now" button for immediate forced backup  
✅ "Open Folder" button for direct folder access  
✅ Automatic refresh after backup  
✅ Display backup count and last backup date  

## 🔧 New Logging System
✅ Unified format: `LOGGER - LEVEL - ACTION - MESSAGE`  
✅ BACKUP logger: all backup module logs tagged  
✅ EDEN logger: all Eden scraper logs tagged  
✅ Standardized actions for each module  
✅ Enhanced debug window with logger filter  

## 🛠️ Log Source Editor (New Tool)
✅ Source code scanner to find all logs  
✅ Interactive editor (table + edit panel)  
✅ Detects `logger.xxx()` and `log_with_action()`  
✅ Action ComboBox with history and auto-complete  
✅ Keyboard shortcuts (Enter, Ctrl+Enter)  
✅ Filters by logger, level, modified logs  
✅ Direct save to source files  
✅ Remembers last edited project  
✅ Real-time statistics  

## 🔍 Eden Scraping Fixes
✅ Fixed Eden cookies save path (PyInstaller fix)  
✅ Auto-update on character import  
✅ Configurable Herald cookies folder  

## 🧬 Herald Authentication - Simplified & Reliable Detection
✅ Authentication detection based on single definitive criterion  
✅ Error message 'The requested page "herald" is not available.' = NOT CONNECTED  
✅ Absence of error message = CONNECTED (can scrape data)  
✅ Coherent logic between `test_eden_connection()` and `load_cookies()`  
✅ Invalid cookies correctly detected and reported  
✅ Tests validated with approximately 58 Herald search results  

## 🎛️ Herald Button Controls
✅ "Refresh" and "Herald Search" buttons automatically disabled  
✅ Disabled when no cookie is detected  
✅ Disabled when cookies are expired  
✅ Button state synchronized with connection status  
✅ Clear user message: "No cookie detected"  

## 📝 Backup Module
✅ 46+ logs tagged with clear actions  
✅ Actions: INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  
✅ Debug logs for complete traceability  
✅ Full support for cookies backup with retention policies  

## 🎨 Interface - Backup Window
✅ Side-by-side layout: Characters and Cookies Eden  
✅ Enlarged window to accommodate both sections (1400x800)  
✅ Smart refresh of info after backup  
✅ "Open Folder" buttons for direct access (Windows/Mac/Linux)  

## 🎨 Interface - General
✅ Fixed column configuration (12 columns)  
✅ Unified folder labels ("Directory")  
✅ Improved path display  
✅ Robust diagnostic system for unexpected crashes  

## 🧹 Repository Cleanup
✅ Deletion of 13 temporary debug scripts  
✅ Deletion of 3 debugging HTML files  
✅ Clean and maintainable repository  
✅ Performance optimization  

## 📚 Documentation
✅ CHANGELOGs system cleanup and reorganization