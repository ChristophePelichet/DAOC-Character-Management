# Settings System - Technical Documentation

**Version**: 2.0  
**Date**: November 2025  
**Last Updated**: December 2025  
**Component**: `UI/settings_dialog.py`, `Functions/config_manager.py`  
**Related**: `Configuration/config.json`, `Functions/config_schema.py`, `Functions/config_migration.py`, `Functions/theme_manager.py`, `Functions/language_manager.py`, `main.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Navigation System](#navigation-system)
4. [Configuration Pages](#configuration-pages)
5. [Backup Integration](#backup-integration)
6. [Folder Management](#folder-management)
7. [SuperAdmin Tools](#superadmin-tools)
8. [Models Gallery Settings](#models-gallery-settings)
9. [UI Components](#ui-components)
10. [Translation System](#translation-system)
11. [Version History](#version-history)

---

## Overview

The Settings System is a modern, navigation-based configuration interface that provides organized access to all application configuration through a sidebar navigation pattern with dedicated pages for each configuration category.

**Location**: `UI/settings_dialog.py` (713 lines)  
**Class**: `SettingsDialog(QDialog)`  
**Pattern**: Sidebar Navigation + Stacked Pages  
**Mode**: Non-Modal (doesn't block main window)

### **Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    Settings Dialog (QDialog)                 │
│  ┌──────────────┬─────────────────────────────────────────┐ │
│  │              │                                          │ │
│  │  Navigation  │          Content Pages                   │ │
│  │  (QListWidget│         (QStackedWidget)                │ │
│  │   200px)     │                                          │ │
│  │              │                                          │ │
│  │ 📁 Général   │  ┌────────────────────────────────┐    │ │
│  │ 🎨 Thèmes    │  │                                 │    │ │
│  │ 🚀 Démarrage │  │  Active Page Content            │    │ │
│  │ 🏛️ Colonnes  │  │  - Form Layouts                 │    │ │
│  │ 🌐 Herald    │  │  - Group Boxes                  │    │ │
│  │ 💾 Backup    │  │  - Controls                     │    │ │
│  │ 🐛 Debug     │  │                                 │    │ │
│  │              │  └────────────────────────────────┘    │ │
│  └──────────────┴─────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Action Buttons (OK / Cancel)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

### **Component Hierarchy**

```
SettingsDialog (QDialog)
│
├── Main Layout (QHBoxLayout)
│   │
│   ├── Navigation List (QListWidget)
│   │   ├── Item 0: 📁 Général
│   │   ├── Item 1: 🎨 Thèmes
│   │   ├── Item 2: 🚀 Démarrage
│   │   ├── Item 3: 🏛️ Colonnes
│   │   ├── Item 4: 🌐 Eden
│   │   ├── Item 5: 💾 Sauvegardes
│   │   ├── Item 6: 🐛 Debug
│   │   └── Item 7: 🔧⚡ SuperAdmin (conditional)
│   │
│   └── Pages Stack (QStackedWidget)
│       ├── Page 0: General Settings
│       ├── Page 1: Themes Settings
│       ├── Page 2: Startup Settings
│       ├── Page 3: Columns Settings
│       ├── Page 4: Herald Settings
│       ├── Page 5: Backup Settings
│       ├── Page 6: Debug Settings
│       └── Page 7: SuperAdmin (conditional)
│
└── Button Box (QDialogButtonBox)
    ├── OK Button
    └── Cancel Button
```

### **Window Properties**

**Modality**:
```python
self.setModal(False)  # Non-modal dialog
dialog.show()         # Use show() instead of exec()
```

**Advantages**:
- ✅ User can interact with main window while settings are open
- ✅ Can view characters while adjusting settings
- ✅ Can test settings without closing dialog

**Resizability**:
```python
self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
self.setSizeGripEnabled(True)
```

**Features**:
- ✅ Maximize button enabled
- ✅ Resize grip in bottom-right corner
- ✅ Default size: 900x650px
- ✅ Minimum size: 800x600px

---

## Navigation System

### **QListWidget Configuration**

```python
navigation = QListWidget()
navigation.setFixedWidth(200)  # Sidebar fixed at 200px
navigation.setIconSize(QSize(24, 24))
navigation.setSpacing(2)
```

### **Navigation Items**

| Index | Icon | Label | Translation Key |
|-------|------|-------|-----------------|
| 0 | 📁 | Général | `settings_nav_general` |
| 1 | 🎨 | Thèmes | `settings_nav_themes` |
| 2 | 🚀 | Démarrage | `settings_nav_startup` |
| 3 | 🏛️ | Colonnes | `settings_nav_columns` |
| 4 | 🌐 | Eden | `settings_nav_herald` |
| 5 | 💾 | Sauvegardes | `settings_nav_backup` |
| 6 | 🐛 | Debug | `settings_nav_debug` |
| 7 | 🔧⚡ | SuperAdmin | `settings.navigation.superadmin` (conditional) |

### **Page Switching Mechanism**

```python
navigation.currentRowChanged.connect(pages.setCurrentIndex)
```

**Event Flow**:
1. User clicks navigation item
2. Signal: `currentRowChanged(int row)` emitted
3. Action: `pages.setCurrentIndex(row)` switches page
4. Result: Smooth transition to corresponding page

---

## Configuration Pages

### **Page Template**

Each page follows this structure:

```python
def _create_<section>_page(self):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignTop)
    
    # Title (Large, Bold)
    title = QLabel(lang.get("settings_<section>_title"))
    title_font.setPointSize(title_font.pointSize() + 4)
    title_font.setBold(True)
    
    # Subtitle (Gray, Descriptive)
    subtitle = QLabel(lang.get("settings_<section>_subtitle"))
    subtitle.setStyleSheet("color: gray;")
    
    # Group Boxes with specific settings
    # ...
    
    layout.addStretch()  # Push content to top
    self.pages.addWidget(page)
```

### **Page 0: Général 📁**

**Content**:
- **Paths Group**: Character, Armor folders (Browse + Move buttons)
- **Defaults Group**: Default Server, Season, Realm
- **Language Group**: Application language selection

**Special Features**:
- Move buttons create/relocate folders
- Paths normalized to Windows backslashes
- Configuration folder NOT configurable (always next to .exe)

### **Page 1: Thèmes 🎨**

**Content**:
- **Theme Group**: Light, Dark, Purple (Dracula)
- **Font Group**: Text size (Small, Medium, Large, Extra Large, Huge)

**Behavior**:
- Theme changes apply immediately (no restart)
- Font scale affects entire application

### **Page 2: Démarrage 🚀**

**Content**:
- **Startup Options**: Disable disclaimer message checkbox

**Info Box**:
- Explains disclaimer purpose and user control

### **Page 3: Colonnes 🏛️**

**Content**:
- **Resize Mode**: Manual vs Auto column sizing
- **Visibility**: Checkboxes for each column (12 total)

**Columns Available**:
- Selection, Realm, Name, Class, Level, Realm Rank
- Realm Title, Guild, Page, Server, Race, URL

### **Page 4: Eden 🌐**

**Content**:
- **Cookies Path**: Eden AppData folder path with Open/Clean buttons
- **Item Cache Path**: User profile cache folder with Open/Clean buttons
- **Browser Group**: Preferred browser, Auto-download drivers

### **Page 5: Sauvegardes 💾**

**Content**:
- **Characters Backup**: 
  * Enable/disable, Path, Compress, Size limit
  * Backup count, Last backup date
  * "Backup Now" + "Open Folder" buttons
- **Cookies Backup**:
  * Enable/disable, Path
  * Backup count, Last backup date
  * "Backup Now" + "Open Folder" buttons

**Functionality**:
- Real-time backup execution
- Stats update after backup
- Folder browser for custom locations

**Backup System Details**: See [Backup Integration](#backup-integration) section.

### **Page 6: Debug 🐛**

**Content**:
- **Log Folder**: Path to logs directory (Browse + Move)
- **Debug Application**: 
  * Enable debug mode checkbox
  * Show debug window checkbox
- **Debug Eden**:
  * Button to open Eden Debug Window
- **Debug HTML Herald**:
  * Save Herald HTML (debug_herald_page.html) checkbox
  * Save Connection Test HTML (debug_test_connection.html) checkbox
  * Both disabled by default
  * Files saved to Logs/ folder when enabled

**Info Box**:
- Explains debug log location

### **Page 7: Models 🖼️**

**Content**:
- **Model Visibility**: Checkboxes for each model slot (15 total)
  * Arms, Boats, Cloaks, Deco, Feet, Hands, Head
  * Legs, Misc, Quiver, Shields, Siege, Tents, Torso, Weapons
- **Alphabetical Sorting**: Slots displayed in alphabetical order

**Features**:
- Enable/disable model slots to control gallery visibility
- Changes apply immediately to Models Gallery view
- Settings persist in `config.json` under `models_gallery.visible_slots`
- All slots enabled by default

**Related Files**:
- Widget: `UI/ui_models_gallery_settings.py` (150 lines)
- Function: `Functions/model_database_manager.py` - `model_gallery_apply_visibility_filters()`
- Integration: `UI/models_overview_widget.py` applies filters when loading metadata

### **Page 8: SuperAdmin 🔧⚡** (Conditional)

**Access Control**:
- **Required**: `python main.py --admin` flag
- **Blocked**: In compiled .exe (frozen check)
- **Condition**: `ADMIN_MODE = '--admin' in sys.argv and not sys.frozen`

**Content**:
- **Armory Section**: 
  * Warning banner about internal database modification
  * Build Database Group (multi-file import)
  * Statistics Group (database stats)
  * Advanced Operations Group (duplicate cleaning)

**SuperAdmin Details**: See [SuperAdmin Tools](#superadmin-tools) section.

---

## Backup Integration

### **Backup System in Settings v2.1**

**Version**: 2.1  
**Feature**: Immediate path updates without application restart  
**Integration**: Settings Page 5 (Sauvegardes)

### **Architecture**

```
Settings Dialog (Page 5)
    ↓
Backup Manager Initialization
    ├─ get_backup_manager(config)
    └─ BackupManager(config)
    ↓
User Actions
    ├─ Change Path → Reinitialize
    ├─ "Backup Now" → Execute
    └─ "Open Folder" → Explorer
    ↓
Immediate Update (No Restart)
```

### **BackupManager Initialization**

```python
from Functions.backup_manager import get_backup_manager, BackupManager

# Initialize or get existing instance
self.backup_manager = get_backup_manager(config)
if self.backup_manager is None:
    self.backup_manager = BackupManager(config)
```

### **Backup Now Workflow**

```
User clicks "Backup Now"
    ↓
_backup_now() or _backup_cookies_now()
    ↓
backup_manager.create_backup() / backup_cookies()
    ↓
Update UI (last date, count)
    ↓
Show success/error message
```

### **Path Change Workflow**

```
User Changes Backup Path
    ↓
Save Configuration (OK Button)
    ↓
Reinitialize BackupManager
    ├─ New path from config
    └─ Update internal state
    ↓
Ready for Next Backup (No Restart)
```

### **UI Components**

**Characters Backup Section**:
- Enable/disable checkbox
- Path selection (Browse + Move + Open Folder)
- Compress option
- Size limit (MB)
- Statistics (count, last backup)
- "Backup Now" button (immediate execution)

**Cookies Backup Section**:
- Enable/disable checkbox
- Path selection (Browse + Move + Open Folder)
- Statistics (count, last backup)
- "Backup Now" button (immediate execution)

### **Real-Time Statistics**

After backup execution:
```python
# Update count
backup_count = len([f for f in os.listdir(backup_path) if f.endswith('.json')])
self.backup_total_label.setText(str(backup_count))

# Update last backup date
if backup_count > 0:
    files = sorted([...], key=lambda x: os.path.getmtime(...))
    last_file = files[-1]
    last_date = datetime.fromtimestamp(os.path.getmtime(last_file))
    self.backup_last_label.setText(last_date.strftime("%Y-%m-%d %H:%M:%S"))
```

---

## Folder Management

### **Folder Move System v2.1**

**Features**:
- **MOVE with MERGE**: Move existing folder, merge if destination exists
- **MOVE**: Move existing folder to new location
- **CREATE**: Create new empty folder if source doesn't exist
- **Auto-cleanup**: Remove empty source folders
- **Immediate reload**: Apply changes without restart

### **Fixed Folder Names**

Folder names are **predefined** and **not user-editable**:

```python
folder_names = {
    "character_folder": "Characters",
    "armor_folder": "Armor",
    "log_folder": "Logs",
    "cookies_folder": "Cookies",
    "backup_path": "Backups/Characters",
    "cookies_backup_path": "Backups/Cookies"
}
```

### **Backup Folder Structure**

```
Standard folders:
  <parent>/Characters/
  <parent>/Armor/

Backup folders:
  <parent>/Backups/Characters/  ← Intermediate /Backups/ folder
  <parent>/Backups/Cookies/     ← Intermediate /Backups/ folder
```

### **Move vs Create Logic**

```
Source Exists? → MOVE MODE
    ├─ Copy existing folder to new location
    ├─ Ask to delete old folder
    └─ Update configuration

Source Missing? → CREATE MODE
    ├─ Suggest default folder name
    ├─ Create new empty folder
    └─ Update configuration
```

### **Operation Modes**

**MOVE with MERGE**:
- Destination folder exists with files
- User chooses merge or cancel
- Files copied from source to destination
- No duplicates (existing files preserved)
- Source deleted if user confirms

**MOVE**:
- Destination doesn't exist or is empty
- Simple folder copy operation
- Source deleted if user confirms

**CREATE**:
- Source folder doesn't exist
- User selects parent folder
- New empty folder created
- Configuration updated

### **Auto-Cleanup**

After successful move:
```python
# Remove empty source folder
if not os.listdir(source_path):
    os.rmdir(source_path)

# Remove empty parent Backup folder
parent = os.path.dirname(source_path)
if os.path.basename(parent) == "Backups" and not os.listdir(parent):
    os.rmdir(parent)
```

### **Immediate System Reload**

**Character Folder**:
```python
if character_folder_changed:
    self._check_migration_on_path_change()
    self.refresh_character_list()  # No restart
```

**Armor Folder**:
```python
if armor_folder_changed:
    self.armory_manager.reload_source_database()  # No restart
```

**Log Folder**:
```python
if log_folder_changed:
    logging_manager.reinitialize(new_log_path)  # No restart
```

---

## SuperAdmin Tools

### **Security Model - Triple-Layer Protection**

```python
# Layer 1: Command-line flag
ADMIN_MODE = '--admin' in sys.argv and not getattr(sys, 'frozen', False)

# Layer 2: Frozen check (blocks .exe)
not getattr(sys, 'frozen', False)

# Layer 3: Conditional UI
if ADMIN_MODE:
    self._create_superadmin_page()
```

**Protection Mechanisms**:

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| **Flag** | Explicit opt-in required | Must run `python main.py --admin` |
| **Frozen** | Blocked in compiled .exe | `sys.frozen` check returns False in dev |
| **UI** | No menu access without flag | Page 7 created conditionally |

**Result**:
- ✅ Development: `python main.py --admin` → SuperAdmin page visible
- ❌ Development: `python main.py` → No SuperAdmin page
- ❌ Production: `.exe --admin` → No SuperAdmin page (frozen check fails)

### **SuperAdminTools Class**

**Location**: `Functions/superadmin_tools.py` (359 lines)

**Core Methods**:

#### **1. get_database_stats()**

Retrieves comprehensive statistics about the source database.

**Returns**: `dict` or `None`
```python
{
    "total_items": 1542,
    "albion": 487,
    "hibernia": 521,
    "midgard": 498,
    "all_realms": 36,
    "file_size": "245.7 KB",
    "last_updated": "2025-11-18 14:23:45"
}
```

#### **2. backup_source_database()**

Creates timestamped backup before destructive operations.

**Backup Pattern**:
```
Data/Backups/items_database_src_YYYYMMDD_HHMMSS.json
```

**Returns**: `(bool, str)` - success flag and path/error message

#### **3. parse_template_files(file_paths, realm)**

Parses .txt template files to extract item data.

**Template Format**:
```
Ethereal Bond Staff
Venom Etched Blade
Ancient Oak Bow
```

**Returns**: `(list[dict], list[str])` - items and errors

#### **4. build_database_from_files(...)**

Main method for building/updating source database.

**Parameters**:
- `file_paths`: List of .txt template files
- `realm`: Target realm (Albion/Hibernia/Midgard/All Realms)
- `merge`: Merge with existing vs replace (default: True)
- `remove_duplicates`: Clean duplicates (default: True)
- `auto_backup`: Create backup first (default: True)

**Returns**: `(bool, str, dict)` - success, message, stats

**Statistics**:
```python
{
    "total_items": 1650,
    "added_items": 108,
    "existing_items": 1542,
    "removed_duplicates": 12
}
```

#### **5. clean_duplicates()**

Removes duplicate items (same name + realm).

**Returns**: `(bool, str, int)` - success, message, removed count

### **UI Integration**

**Page Layout**:

```
┌─────────────────────────────────────────────────────────┐
│  🔧⚡ SuperAdmin - Outils Administrateur                  │
│  Gestion avancée de la base source de l'armurerie       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🛡️ Armurerie - Base Source                           │
│  ┌───────────────────────────────────────────────────┐ │
│  │ ⚠️ WARNING: These tools modify the internal       │ │
│  │    read-only database. Use with caution!          │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  📋 Construction de la base source                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Fichiers template (.txt):    [Select files...]    │ │
│  │ Royaume:                      [ Hibernia   ▼ ]    │ │
│  │ ☑ Fusionner avec existant                         │ │
│  │ ☑ Supprimer doublons                              │ │
│  │ ☑ Backup automatique                              │ │
│  │                                                    │ │
│  │                [ ⚡ Construire la base ]           │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────┬─────────────────────────┐ │
│  │ 📊 Statistiques         │ ⚙️ Opérations avancées │ │
│  │ ─────────────────────── │ ───────────────────────│ │
│  │ Base de données:        │                         │ │
│  │   items_database_src.   │ [ Nettoyer doublons ]  │ │
│  │                         │                         │ │
│  │ Total items: 1542       │                         │ │
│  │ Albion: 487             │                         │ │
│  │ Hibernia: 521           │                         │ │
│  │ Midgard: 498            │                         │ │
│  │ Tous royaumes: 36       │                         │ │
│  │ Taille: 245.7 KB        │                         │ │
│  │ MAJ: 2025-11-18 14:23   │                         │ │
│  │                         │                         │ │
│  │   [ Actualiser ]        │                         │ │
│  └─────────────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Sections**:

1. **Build Database**: Multi-file .txt import with realm selection
2. **Statistics** (Left 50%): Real-time database stats
3. **Advanced Operations** (Right 50%): Duplicate cleaning

---

## UI Components

### **Standard Folder Path Component Template**

**Visual Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ 📁 Group Title                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Label:  [________________Path________________] [Browse] [📦] [📂] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
1. **QGroupBox** - Container with emoji + title
2. **QLineEdit** - Read-only path display
3. **Browse Button** - "Parcourir..." (max 100px width)
4. **Move Button** - 📦 "Déplacer"
5. **Open Folder Button** - 📂 "Ouvrir le dossier"

**Code Template**:
```python
# === FOLDER NAME ===
folder_group = QGroupBox("📁 " + lang.get("folder_group_title"))
folder_layout = QFormLayout()

# Path edit (read-only)
self.folder_path_edit = QLineEdit()
self.folder_path_edit.setText(config.get("folder_config_key"))
self.folder_path_edit.setReadOnly(True)
self.folder_path_edit.setCursorPosition(0)

# Browse button
browse_button = QPushButton(lang.get("browse_button"))
browse_button.clicked.connect(self._browse_folder_path)
browse_button.setMaximumWidth(100)

# Move button
move_button = QPushButton("📦 " + lang.get("move_folder_button"))
move_button.clicked.connect(lambda: self._move_folder(...))
move_button.setToolTip(lang.get("move_folder_tooltip"))

# Open folder button
open_button = QPushButton("📂 " + lang.get("open_folder_button"))
open_button.clicked.connect(self._open_folder_path)

# Layout assembly
folder_path_layout = QHBoxLayout()
folder_path_layout.addWidget(self.folder_path_edit)
folder_path_layout.addWidget(browse_button)
folder_path_layout.addWidget(move_button)
folder_path_layout.addWidget(open_button)

folder_layout.addRow(lang.get("folder_path_label") + " :", folder_path_layout)
folder_group.setLayout(folder_layout)
layout.addWidget(folder_group)
```

### **Component Guidelines**

**Naming Conventions**:

| Component | Pattern | Example |
|-----------|---------|---------|
| QLineEdit | `self.{type}_path_edit` | `self.character_path_edit` |
| Browse Button | `browse_{type}_button` | `browse_character_button` |
| Move Button | `move_{type}_button` | `move_character_button` |
| Open Button | `open_{type}_folder_button` | `open_character_folder_button` |

**Standard Behaviors**:
- Path QLineEdit always read-only
- Cursor position reset to 0 after setText
- Browse button max width: 100px
- Consistent button order: Browse → Move → Open
- Move button includes tooltip explaining functionality
- No custom styling (use default theme)

---

## Translation System

### **Settings Translation Namespace**

**Key Pattern**: `settings.*`

**Examples**:
```python
lang.get("settings.general_title")
lang.get("settings.nav_themes")
lang.get("settings.pages.backup.title")
```

### **SuperAdmin Translation Namespace**

**Key Pattern**: `superadmin.*` (no `settings.pages.` prefix)

**Examples**:
```python
lang.get("superadmin.title")
lang.get("superadmin.build_group_title")
lang.get("superadmin.stats_total")
```

### **Supported Languages**

- 🇫🇷 **French** (Français) - Default
- 🇬🇧 **English**
- 🇩🇪 **German** (Deutsch)

**Total Translation Keys**: 
- Settings System: ~90+ keys
- SuperAdmin: 40+ keys

### **Language Change Behavior**

```python
if language_changed:
    config.set("language", new_lang_code)
    lang.set_language(new_lang_code)
    self.retranslate_ui()  # Refresh all UI text
```

**Effect**: Immediate language switch (no restart needed)

---

## Data Flow

### **Loading Settings**

```
Application Startup
    ↓
SettingsDialog.__init__()
    ↓
_load_settings()
    ├→ Read from config.get()
    ├→ Populate line edits
    ├→ Set checkbox states
    ├→ Select combo box values
    └→ Load column visibility
```

### **Saving Settings**

```
User clicks OK
    ↓
accepted signal
    ↓
save_configuration(dialog)
    ├→ Compare old vs new values
    ├→ config.set() for each setting
    ├→ Special handling:
    │   ├─ Theme change → apply_theme()
    │   ├─ Font scale → apply_font_scale()
    │   ├─ Language → change_language()
    │   ├─ Column mode → apply_column_resize_mode()
    │   └─ Character folder → refresh_character_list()
    └→ Show success message
```

### **Configuration Persistence**

**Config File Location**:
```
ALWAYS: <executable_directory>/Configuration/config.json
```

**Rationale**:
- ❌ Config folder is NOT configurable
- ✅ Avoids circular dependency issues
- ✅ Ensures portability
- ✅ Predictable location for troubleshooting

**Saved Settings**:

| Category | Settings | Config Keys |
|----------|----------|-------------|
| **Paths** | Character, Armor, Logs, Cookies | `character_folder`, `armor_folder`, `log_folder`, `cookies_folder` |
| **Defaults** | Server, Season, Realm | `default_server`, `default_season`, `default_realm` |
| **Display** | Theme, Font scale | `theme`, `font_scale` |
| **Columns** | Resize mode, Visibility | `manual_column_resize`, `column_visibility` |
| **Herald** | Browser, Auto-download | `preferred_browser`, `allow_browser_download` |
| **Backup** | Enabled, Paths, Compress, Limit | `backup_enabled`, `backup_path`, `backup_compress`, `backup_size_limit_mb` |
| **Debug** | Debug mode, Show window | `debug_mode`, `show_debug_window` |
| **Startup** | Disclaimer disabled | `disable_disclaimer` |
| **Language** | UI language | `language` |
| **Models Gallery** | Visible model slots | `models_gallery.visible_slots` (list of 15 slots) |

---

## Version History

### **v0.110 - Models Gallery Settings**

**New Features**:
- **Page 7: Models Gallery 🖼️**
  * 15 checkboxes for model slot visibility control
  * Alphabetical sorting of slots (Arms, Boats, Cloaks, ...)
  * Enable/disable categories to customize gallery view
  * Settings persist in config under `models_gallery.visible_slots`
- **Configuration Section**: New `models_gallery` section in config.json
  * Default: All 15 slots enabled
  * Schema validation in config_schema.py
- **Filtering Function**: `model_gallery_apply_visibility_filters()` in model_database_manager.py
  * Filters metadata based on visible_slots setting
  * Removes disabled slots from gallery display
- **UI Widget**: New `ModelsGallerySettingsWidget` in UI/ui_models_gallery_settings.py
  * Auto-save on checkbox change
  * Real-time config persistence via `config.save_config()`
- **Gallery Integration**: ModelsOverviewWidget applies filters when loading metadata
  * Gallery automatically reflects visibility settings

**Files Modified**:
- UI/settings_dialog.py: Added `_create_models_gallery_page()` method and navigation item
- Configuration/config.json: Added `models_gallery` section with all 15 slots
- Functions/config_schema.py: Added schema validation for models_gallery
- UI/models_overview_widget.py: Apply visibility filters to loaded metadata
- UI/ui_model_gallery_display.py: Improved thumbnail sizing and label visibility

**Settings Table Update**:
- New entry: Models Gallery with visible_slots configuration

### **v0.108 - Complete Reorganization**

**Major Changes**:
- Complete reorganization with sidebar navigation
- Removed monolithic dialog
- Added 8 distinct pages (+ SuperAdmin conditional)
- Integrated Backup settings
- Added folder move functionality
- Removed Tools menu
- **NEW**: Page 7 SuperAdmin (development-only)
- SuperAdmin: Build database from template files
- SuperAdmin: Statistics tracking and duplicate cleaning
- SuperAdmin: Triple-layer security (flag + frozen + UI)
- SuperAdmin: Side-by-side layout (Stats 50% + Advanced 50%)

**Backup Integration v2.1**:
- Immediate path updates without restart
- Real-time backup execution from Settings
- Statistics display (count, last backup)
- Manual backup triggers

**Folder Move System v2.1**:
- Three operation modes: MOVE with MERGE, MOVE, CREATE
- Fixed folder names (no user input)
- Auto-cleanup of empty folders
- Parent Backup folder cleanup
- Immediate system reload for Characters, Logs, Armor

---

## Models Gallery Settings

**Added in**: v0.110  
**Component**: `UI/ui_models_gallery_settings.py`  
**Integration**: Settings dialog, Page 8 (📋 Models)  
**Related**: `Functions/model_database_manager.py`, `Data/models_metadata.json`

### Overview

The Models Gallery Settings allow users to control which model categories appear in the Models Gallery through an intuitive 3-column hierarchical interface with parent-child checkbox logic. Users can:
- Select entire category groups (Armor, Weapon, Other)
- Fine-tune by selecting/deselecting individual subcategories
- Use parent checkbox to batch-select all subcategories
- Have changes persist immediately to `config.json`

**Default State**:
- ✅ **Armor** (with all 8 subcategories)
- ✅ **Weapon** (flat category)
- ❌ **Other** (with 6 subcategories)

### Architecture

**UI Component** (`UI/ui_models_gallery_settings.py`, 280+ lines):

```python
class ModelsGallerySettingsWidget(QWidget):
    """3-column hierarchical category selector for Models Gallery visibility."""
    
    def __init__(self, parent=None):
        """Initialize with category structure and load saved settings."""
        self.config = config
        self.parent_checkboxes = {}  # {category: QCheckBox}
        self.child_checkboxes = {}   # {category: {subcategory: QCheckBox}}
        self.category_order = ["armor", "weapon", "other"]
        self.category_structure = {
            "armor": ["arms", "cloaks", "feet", "hands", "head", "legs", "shields", "torso"],
            "weapon": [],  # No subcategories - flat category
            "other": ["boats", "deco", "misc", "quiver", "siege", "tents"]
        }
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Create 3-column layout with QFrame borders around each column."""
        # Creates three equal-width columns, one per category
        # Each column contains parent checkbox and subcategory checkboxes
        # Uses signal blocking to prevent infinite loops during updates
    
    def _on_parent_changed(self, category):
        """Parent checkbox clicked - select/deselect all subcategories."""
        # Block signals during update to prevent recursive calls
        # Check parent state and apply to all children
        # Save configuration after update
    
    def _on_child_changed(self, category):
        """Subcategory checkbox clicked - update parent state accordingly."""
        # Evaluate parent state:
        #   - All children checked → Parent = checked
        #   - No children checked → Parent = unchecked  
        #   - Mixed state → Parent = partial/tri-state
        # Save configuration after update
    
    def _load_settings(self):
        """Load visible_slots from config.json and update UI."""
        visible_slots = self.config.get("models_gallery.visible_slots", {})
        # For each category and subcategory, load saved state
        # Apply to corresponding checkboxes
        # Use signal blocking to prevent triggering change handlers
    
    def _save_config(self):
        """Save current checkbox states to models_gallery.visible_slots."""
        visible_slots = {}
        for category in self.category_order:
            visible_slots[category] = {
                "_selected": self.parent_checkboxes[category].isChecked()
            }
            if category != "weapon":
                for subcategory in self.category_structure[category]:
                    visible_slots[category][subcategory] = \
                        self.child_checkboxes[category][subcategory].isChecked()
        
        self.config.set("models_gallery.visible_slots", visible_slots)
        self.config.save_config()
```

### Configuration Structure

**Location**: `Configuration/config.json`, section `models_gallery`

**Default Configuration**:
```json
{
  "models_gallery": {
    "visible_slots": {
      "armor": {
        "_selected": true,
        "arms": true,
        "cloaks": true,
        "feet": true,
        "hands": true,
        "head": true,
        "legs": true,
        "shields": true,
        "torso": true
      },
      "weapon": {
        "_selected": true
      },
      "other": {
        "_selected": false,
        "boats": false,
        "deco": false,
        "misc": false,
        "quiver": false,
        "siege": false,
        "tents": false
      }
    }
  }
}
```

**Schema** (`Functions/config_schema.py`):
```python
"models_gallery": {
    "type": "object",
    "properties": {
        "visible_slots": {
            "type": "object",
            "description": "Visible model categories and subcategories",
            "properties": {
                "armor": {"type": "object", "description": "Armor category and subcategories"},
                "weapon": {"type": "object", "description": "Weapon category"},
                "other": {"type": "object", "description": "Other category and subcategories"}
            }
        }
    },
    "default": { /* as shown above */ }
}
```

### Parent-Child Checkbox Logic

**Key Feature**: Hierarchical synchronization with signal blocking

**Flow Diagram**:
```
User clicks Category Checkbox (Parent)
    ↓
_on_parent_changed() triggered
    ↓
Block child signals (prevent recursion)
    ↓
Set all children to parent state (checked/unchecked)
    ↓
Restore signal connections
    ↓
_save_config() → config.json

User clicks Subcategory Checkbox (Child)
    ↓
_on_child_changed() triggered
    ↓
Evaluate all children state
    ↓
_update_parent_state():
    - All checked? → Parent = checked
    - None checked? → Parent = unchecked
    - Some checked? → Parent = partial
    ↓
_save_config() → config.json
```

**Signal Blocking Mechanism**:
```python
# Prevent infinite loops during cascade updates
child_cb.blockSignals(True)
child_cb.setChecked(is_checked)
child_cb.blockSignals(False)

# Signals remain connected but aren't emitted while blocked
# Avoids: Parent→Child→Parent→Child→... recursion
```

### Integration with Models Gallery

**File**: `Functions/model_database_manager.py`

**Function**: `model_gallery_apply_visibility_filters(items, config)`

```python
def model_gallery_apply_visibility_filters(items, config):
    """Filter items based on visible_slots configuration."""
    visible_slots = config.get("models_gallery.visible_slots", {})
    
    filtered_items = []
    for item in items:
        category = item.get("category", "other")
        subcategory = item.get("subcategory", "misc")
        
        # Check if category is visible
        category_config = visible_slots.get(category, {})
        if not category_config.get("_selected", False):
            continue
        
        # Check if subcategory is visible (if category has subcategories)
        if category != "weapon":
            if not category_config.get(subcategory, True):
                continue
        
        filtered_items.append(item)
    
    return filtered_items
```

**Integration Flow**:
```
ModelsGalleryWidget loads items
    ↓
Calls model_gallery_apply_visibility_filters()
    ↓
Filters based on visible_slots config
    ↓
Displays only visible categories/subcategories
    ↓
User changes settings
    ↓
ModelsGalleryWidget receives config change signal
    ↓
Re-applies filters automatically
    ↓
Gallery UI updates in real-time
```

### UI Layout (v0.110)

**3-Column Design**:
```
┌─────────────────────────────────────────────────────────┐
│     Models Gallery Settings - 3 Equal Columns           │
├────────────────────┬────────────────────┬────────────────┤
│                    │                    │                │
│   ARMOR            │   WEAPON           │   OTHER        │
│   ┌────────────┐   │   ┌────────────┐   │   ┌────────────┐
│   │ ☑ Armor    │   │   │ ☑ Weapon   │   │   │ ☐ Other    │
│   │            │   │   │            │   │   │            │
│   │ ├─☑ Arms   │   │   │ (Flat cat) │   │   │ ├─☐ Boats  │
│   │ ├─☑ Cloaks │   │   │ No subs    │   │   │ ├─☐ Deco   │
│   │ ├─☑ Feet   │   │   │            │   │   │ ├─☐ Misc   │
│   │ ├─☑ Hands  │   │   │            │   │   │ ├─☐ Quiver │
│   │ ├─☑ Head   │   │   │            │   │   │ ├─☐ Siege  │
│   │ ├─☑ Legs   │   │   │            │   │   │ └─☐ Tents  │
│   │ ├─☑ Shields│   │   │            │   │   │            │
│   │ └─☑ Torso  │   │   │            │   │   │            │
│   └────────────┘   │   └────────────┘   │   └────────────┘
│                    │                    │                │
└────────────────────┴────────────────────┴────────────────┘
```

**Features**:
- ✅ Equal-width columns (33% width each)
- ✅ QFrame with borders for visual separation
- ✅ Hierarchical layout (Parent at top, children indented)
- ✅ Real-time signal connection/disconnection
- ✅ Persistent configuration (auto-save on change)
- ✅ Default state: Armor + Weapon selected, Other deselected

### Related Documentation

See [Models Gallery Settings](../../Models/MODELS_VISUAL_SYSTEM_DOCUMENTATION.md#models-gallery-settings) in Models Visual System documentation for comprehensive details on:
- Category hierarchy structure
- Database synchronization
- Image location and format
- Filtering function integration
- Category-based distribution

---


- **SuperAdmin Tools**: `superadmin_tools.py` (Functions/)
- **Folder Move System**: Documented in FOLDER_MOVE_SYSTEM_EN.md
- **Backup Integration**: Documented in BACKUP_INTEGRATION_EN.md
- **Dual-Mode Database**: Armory database management
- **Configuration Manager**: `config_manager.py` (Functions/)
- **Translation System**: `language_manager.py` (Functions/)
- **UI Component Template**: Standard component patterns

---

## File Structure

### **Backend**

```
Functions/
├── superadmin_tools.py (359 lines)
├── backup_manager.py
├── config_manager.py
├── language_manager.py
├── path_manager.py
├── config_schema.py (with models_gallery section)
└── model_database_manager.py (model_gallery_apply_visibility_filters)
```

### **UI**

```
UI/
├── settings_dialog.py (2651+ lines)
│   ├── Conditional Page Creation (lines 88-95)
│   ├── Navigation Items (lines 131-155)
│   ├── _create_general_page() (lines 141-245)
│   ├── _create_themes_page() (lines 247-299)
│   ├── _create_startup_page() (lines 301-350)
│   ├── _create_columns_page() (lines 352-413)
│   ├── _create_herald_page() (lines 415-495)
│   ├── _create_backup_page() (lines 497-700)
│   ├── _create_debug_page() (lines 702-780)
│   ├── _create_models_gallery_page() (NEW - v0.110)
│   └── _create_superadmin_page() (lines 1140-1320)
├── ui_models_gallery_settings.py (NEW - v0.110 - 280+ lines)
│   └── ModelsGallerySettingsWidget(QWidget)
│       ├── 3-column layout (Armor | Weapon | Other)
│       ├── Parent-child checkbox synchronization
│       ├── Signal blocking for infinite loop prevention
│       └── Real-time config persistence
├── models_overview_widget.py (with visibility filtering)
└── ui_model_gallery_display.py (improved thumbnails)
```

### **Data**

```
Data/
├── models_metadata.json (3,444 items - 100% synchronized)
│   ├── All items have source_url field
│   ├── Categories: armor, weapon, other
│   ├── Subcategories documented in Models Visual System docs
│   └── Distribution: armor (~1,200), weapon (~500), other (~1,700)
├── classes_races_stats.json
├── items_database_src.json
└── realm_ranks.json
```

**Deleted in v0.110**:
- ~~`dol_models_database.json`~~ (merged into models_metadata.json)
- ~~`models_metadata.json.backup`~~ (cleanup)
- ~~`models_metadata.json.backup2`~~ (cleanup)  
- ~~`models_metadata.json.backup3`~~ (cleanup)

### **Image Repository**

```
Img/Models/
└── Items/  (Unified directory, v0.110+)
    ├── 1.webp
    ├── 2.webp
    ├── 3.webp
    └── ... 3,444 total WebP files
    
Total Size: ~10.48 MB
Format: WebP (optimized)
```

**Note**: Prior to v0.110, images were organized by category (`armor/`, `weapon/`, `other/`). As of v0.110, all images are in the unified `Items/` directory for simplified access and consistent filtering.

### **Translations**

```
Language/
├── fr.json (settings.* + superadmin.* keys, updated for Models)
├── en.json (settings.* + superadmin.* keys, updated for Models)
└── de.json (settings.* + superadmin.* keys, updated for Models)
```

**New Keys (v0.110)**:
- `settings_models_gallery` - Page title
- `settings_models_gallery_subtitle` - Page subtitle
- `models_gallery_armor` - Category label
- `models_gallery_weapon` - Category label
- `models_gallery_other` - Category label
- And subcategory labels for each language

### **Tools (Removed in v0.110)**

```
Deleted:
├── Tools/merge_models_databases.py (never called - merged functionality)
├── Tools/move_legs_to_armor.py (never called - data already correct)
├── Tools/analyze_template.py (debug script - no longer needed)
```

---

**Current Version**: v0.110  
**Status**: ✅ Active Standard  
**Last Updated**: 2025-01-17

---

## Version History - v0.110 Changes

### **Major Updates**

1. **Models Gallery Settings Redesign**:
   - ✅ New 3-column hierarchical UI with parent-child checkbox logic
   - ✅ Categories: Armor, Weapon, Other with proper subcategories
   - ✅ Default state: Armor + Weapon enabled, Other disabled
   - ✅ Real-time filtering with configuration persistence
   - ✅ Signal blocking prevents infinite loops

2. **Database Optimization**:
   - ✅ Added missing source_url fields to all 2,878 items
   - ✅ Merged dol_models_database.json into models_metadata.json
   - ✅ Removed temporary backup files (backup, backup2, backup3)
   - ✅ 3,444 items now 100% complete with URLs

3. **Image System Improvements**:
   - ✅ Unified image directory: `Img/Models/Items/` (not category-based)
   - ✅ Fixed preview paths in SuperAdmin database editor
   - ✅ All 3,444 WebP files properly indexed

4. **Code Cleanup**:
   - ✅ Removed unused maintenance scripts (never called)
   - ✅ Removed debug analysis script (analyze_template.py)
   - ✅ Clean commit history with 8 focused commits

### **Commits**
- "fix: add missing source_url fields to all 2,878 items in models metadata"
- "feat: redesign models gallery settings with 3-column category layout and parent-child checkbox logic"
- "fix: correct weapon category name and improve parent-child checkbox state synchronization"
- "fix: correct model image preview path from category-based to unified Items directory"
- "chore: remove temporary database backup files" (3 files)
- "chore: remove dol_models_database.json - merged into models_metadata.json"
- "chore: remove unused database maintenance scripts" (2 files)
- "chore: remove analyze_template.py debug script"
