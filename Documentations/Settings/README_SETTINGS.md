# Settings System - Technical Documentation

Complete technical documentation for the DAOC Character Management Settings system (v0.108+).

---

## 📚 Documentation Index

### **Core Architecture**
- **[Settings Architecture](SETTINGS_ARCHITECTURE_EN.md)** - Complete system overview
  - Component hierarchy and navigation
  - 7 page descriptions with features
  - Data flow and persistence
  - Window lifecycle
  - Translation system
  - Integration points

### **Feature Systems**
- **[Folder Move System](FOLDER_MOVE_SYSTEM_EN.md)** - Folder management functionality
  - Move/Create folder workflows
  - Path normalization
  - Safety features and confirmations
  - Usage examples

- **[Backup Integration](BACKUP_INTEGRATION_EN.md)** - Backup system in Settings
  - Characters and Cookies backup sections
  - Real-time statistics and execution
  - BackupManager integration
  - Comparison with old Tools menu system

---

## 🎯 Quick Reference

### Settings Dialog Pages (7 Total)

| # | Icon | Name | Key Features |
|---|------|------|--------------|
| **0** | 📁 | **Général** | Paths (Characters, Armor), Defaults (Class, Race, Realm), Language selection |
| **1** | 🎨 | **Thèmes** | Theme selection, Font scale adjustment |
| **2** | 🚀 | **Démarrage** | Disclaimer checkbox |
| **3** | 🏛️ | **Colonnes** | Table resize mode, Column visibility (12 columns) |
| **4** | 🌐 | **Herald Eden** | Cookies path, Browser selection (Chrome/Edge/Firefox) |
| **5** | 💾 | **Sauvegardes** | Characters backup, Cookies backup (enable, path, stats, actions) |
| **6** | 🐛 | **Debug** | Logs path, Debug mode, Eden debug window |

---

## 🔧 Configuration Management

### **Configurable Folders** (with Move + Browse buttons)
- ✅ **Characters** - `character_folder` - Default: `<base>/Characters`
- ✅ **Armor** - `armor_folder` - Default: `<base>/Armor`
- ✅ **Logs** - `logs_folder` - Default: `<base>/Logs`
- ✅ **Cookies** - `cookies_folder` - Default: `<base>/Cookies`

### **Non-Configurable Folders**
- ❌ **Configuration** - ALWAYS at `<executable_dir>/Configuration/config.json`
  - Reason: Prevents circular dependency (config can't define its own location)

---

## 💾 Backup System Overview

### **Characters Backup**
- **Enable/Disable**: Checkbox to activate automatic backups
- **Path**: Custom backup folder location
- **Compression**: ZIP compression option
- **Size Limit**: Maximum backup size in MB
- **Statistics**: Real-time backup count and last backup date
- **Actions**: Backup Now (immediate execution), Open Folder (explorer)

### **Cookies Backup**
- **Enable/Disable**: Checkbox to activate cookie backups
- **Path**: Custom backup folder for cookies
- **Statistics**: Backup count and last backup date
- **Actions**: Backup Now, Open Folder

### **Integration**
- Replaced old Tools > Backup menu
- Unified settings interface (non-modal)
- Real-time UI updates after backup execution
- Direct folder access via explorer

---

## 🔄 Folder Move/Create System

### **Two Operation Modes**

**1. MOVE MODE** (source folder exists)
```
Source Exists
    ↓
Copy to Destination
    ↓
Ask: Delete Old Folder?
    ├─ YES: Delete + Update config
    └─ NO: Keep + Update config
```

**2. CREATE MODE** (source folder missing)
```
Source Missing
    ↓
Suggest Default Name
    ↓
User Confirms/Changes
    ↓
Create New Folder
    ↓
Update Config
```

### **Safety Features**
- ✅ Copy-before-delete pattern (never lose data)
- ✅ Confirmations at every step
- ✅ Default answer always "No" (safe choice)
- ✅ Duplicate destination detection
- ✅ Windows path normalization (backslashes)

---

## 🌍 Translation System

### **Languages Supported**
- **FR**: Français (French)
- **EN**: English
- **DE**: Deutsch (German)

### **Translation Files**
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`

### **Key Patterns**
- `settings_*` - Settings dialog UI elements
- `config_*` - Configuration-related strings
- `backup_*` - Backup functionality
- `move_folder_*` - Folder move/create dialogs

### **Total Keys** (Settings-related)
- ~100+ translation keys covering all Settings pages and features

---

## 📊 Data Flow

### **Loading Settings**
```
Dialog Open
    ↓
Load Config via config_manager.get()
    ↓
Populate UI Fields
    ├─ Text Edits (paths)
    ├─ Checkboxes (enable/disable)
    ├─ Comboboxes (selections)
    └─ Spin Boxes (numeric values)
```

### **Saving Settings**
```
User Clicks OK
    ↓
save_configuration() in main.py
    ↓
Detect Changes (compare old vs new)
    ↓
Update Config via config.set()
    ↓
Apply Special Actions:
    ├─ Character folder changed → Refresh list
    ├─ Theme changed → Apply theme
    ├─ Language changed → Reload UI
    └─ Debug mode changed → Toggle logging
```

---

## 🔗 Integration Points

### **Main Window**
- Triggered from: File menu > Settings (`Ctrl+Shift+S`)
- Method: `main.py::save_configuration()` handles all saves
- Effects: May trigger character list refresh, theme change, language reload

### **Backup Manager**
- Singleton instance from `Functions.backup_manager`
- Initialized in `_create_backup_page()`
- Methods: `create_backup()`, `backup_cookies()`, `get_backup_info()`

### **Configuration Manager**
- Path: `Functions.config_manager`
- Fixed config location: `<exe_dir>/Configuration/config.json`
- Methods: `load_config()`, `save_config()`, `get_config_dir()`

### **Path Manager**
- Path: `Functions.path_manager`
- Method: `get_base_path()` - Returns executable directory
- Used for default folder paths

---

## 🐛 Error Handling

### **Folder Operations**
- **Destination exists**: Show error, suggest new name
- **Copy failed**: Critical error dialog with exception details
- **Permission denied**: Error message with folder path

### **Backup Operations**
- **Backup failed**: Warning dialog (backup_failed translation)
- **Exception during backup**: Critical error with exception message
- **Folder doesn't exist**: Silently ignore when opening folder

### **Configuration**
- **Invalid size limit**: Preserve previous value (silent fail)
- **Missing paths**: Use defaults from `get_base_path()`
- **Backup Manager not initialized**: Create new instance

---

## 📏 UI Specifications

### **Settings Dialog**
- **Size**: 950x650 pixels
- **Modality**: Non-modal (doesn't block main window)
- **Resizability**: Enabled (user can resize)
- **Layout**: Horizontal split - Navigation (200px) + Content pages

### **Navigation**
- **Widget**: QListWidget (left panel)
- **Width**: 200px fixed
- **Items**: 7 pages with icons and labels
- **Selection**: Single selection, highlights active page

### **Content Pages**
- **Widget**: QStackedWidget (right panel)
- **Switching**: Based on navigation item selection
- **Layout**: Each page has custom QVBoxLayout with sections

---

## 🚀 Performance Considerations

### **Backup Info Retrieval**
- **When**: Once during page creation
- **Cost**: File system scan of backup folder
- **Optimization**: Cached until next dialog open

### **Real-Time Updates**
- **When**: After manual backup execution
- **Cost**: Re-scan backup folder
- **Impact**: Minimal (only on user action)

### **Path Normalization**
- **When**: Every folder browse/move operation
- **Cost**: String replacement (negligible)
- **Pattern**: `.replace('/', '\\')`

### **Configuration Save**
- **When**: User clicks OK
- **Cost**: JSON serialization + file write
- **Optimization**: Only save if changes detected

---

## 🔮 Future Enhancements

**Potential Additions**:
- [ ] Automatic backup scheduling (daily/weekly/monthly)
- [ ] Backup retention policy (auto-delete old backups beyond X count)
- [ ] Cloud storage integration (Dropbox, Google Drive)
- [ ] Restore from backup UI
- [ ] Backup comparison/diff viewer
- [ ] Incremental backups (only changed files)
- [ ] Email/notification on backup completion
- [ ] Settings import/export (share configurations)
- [ ] Settings profiles (multiple configurations)
- [ ] Advanced column configuration (reordering, custom widths)

---

## 📜 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v0.108** | 2025-11 | Complete Settings dialog reorganization |
| | | - Moved backup from Tools menu to Settings page |
| | | - Integrated Characters + Cookies backup |
| | | - Real-time statistics display |
| | | - Removed modal BackupSettingsDialog |
| | | - Made config folder non-configurable |
| | | - Simplified config_manager (removed .config_path) |
| | | - Path normalization throughout |
| | | - Created comprehensive technical documentation |

---

## 📖 Related Documentation

### **Core Systems**
- [Backup Manager](../Core/BACKUP_MANAGER_EN.md) *(if exists)*
- [Configuration Manager](../Core/CONFIG_MANAGER_EN.md) *(if exists)*
- [Path Manager](../Core/PATH_MANAGER_EN.md) *(if exists)*

### **Eden Integration**
- [Eden Scraper Documentation](../Eden/EDEN_SCRAPER_DOCUMENTATION_EN.md)
- [Cookie Manager](../COOKIE_MANAGER_EN.md)

### **User Guides**
- [Column Configuration Guide](../COLUMN_CONFIGURATION_EN.md)
- [Data Folder Guide](../DATA_FOLDER_EN.md)

### **Changelog**
- [Full Changelog FR](../../Changelogs/CHANGELOG_FR.md)
- [Full Changelog EN](../../Changelogs/CHANGELOG_EN.md)
- [Simple Changelog FR](../../Changelogs/CHANGELOG_SIMPLE_FR.md)
- [Simple Changelog EN](../../Changelogs/CHANGELOG_SIMPLE_EN.md)

---

## 📧 Support

For technical questions or issues:
1. Check this documentation first
2. Review related documentation files
3. Check changelog for recent changes
4. Open an issue on the project repository

---

**Last Updated**: November 2025 (v0.108)  
**Documentation Status**: ✅ Complete - All major systems documented
