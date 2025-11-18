# Settings System - Technical Architecture

## Overview
The Settings System is a **modern, navigation-based configuration interface** that replaced the monolithic single-page settings dialog. It provides organized access to all application configuration through a sidebar navigation pattern with dedicated pages for each configuration category.

**Location**: `UI/settings_dialog.py` (713 lines)  
**Class**: `SettingsDialog(QDialog)`  
**Pattern**: Sidebar Navigation + Stacked Pages  
**Mode**: Non-Modal (doesn't block main window)

---

## Architecture Overview

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

## Component Hierarchy

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
│   │   ├── Item 4: 🌐 Herald Eden
│   │   ├── Item 5: 💾 Sauvegardes
│   │   └── Item 6: 🐛 Debug
│   │
   └── Pages Stack (QStackedWidget)
       ├── Page 0: General Settings
       ├── Page 1: Themes Settings
       ├── Page 2: Startup Settings
       ├── Page 3: Columns Settings
       ├── Page 4: Herald Settings
       ├── Page 5: Backup Settings
       ├── Page 6: Debug Settings
       └── Page 7: SuperAdmin (conditional - requires --admin flag)
│
└── Button Box (QDialogButtonBox)
    ├── OK Button
    └── Cancel Button
```

---

## Navigation System

### **QListWidget Configuration**

```python
navigation = QListWidget()
navigation.setFixedWidth(200)  # Sidebar fixed at 200px
navigation.setIconSize(QSize(24, 24))
navigation.setSpacing(2)
```

**Navigation Items**:
| Index | Icon | Label | Key |
|-------|------|-------|-----|
| 0 | 📁 | Général | `settings_nav_general` |
| 1 | 🎨 | Thèmes | `settings_nav_themes` |
| 2 | 🚀 | Démarrage | `settings_nav_startup` |
| 3 | 🏛️ | Colonnes | `settings_nav_columns` |
| 4 | 🌐 | Herald Eden | `settings_nav_herald` |
| 5 | 💾 | Sauvegardes | `settings_nav_backup` |
| 6 | 🐛 | Debug | `settings_nav_debug` |
| 7 | 🔧⚡ | SuperAdmin | `settings.navigation.superadmin` (conditional) |

### **Page Switching Mechanism**

```python
navigation.currentRowChanged.connect(pages.setCurrentIndex)
```

- **Event**: User clicks navigation item
- **Signal**: `currentRowChanged(int row)`
- **Action**: `pages.setCurrentIndex(row)` switches to corresponding page
- **Result**: Smooth transition between configuration pages

---

## Window Properties

### **Modality**

```python
self.setModal(False)  # Non-modal dialog
dialog.show()         # Use show() instead of exec()
```

**Advantages**:
- ✅ User can interact with main window while settings are open
- ✅ Can view characters while adjusting settings
- ✅ Can test settings without closing dialog

### **Resizability**

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

## Pages Architecture

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

---

## 8 Configuration Pages

⚠️ **Note**: Page 7 (SuperAdmin) is **conditional** - only created when running `python main.py --admin` in development mode. It is completely hidden in production (.exe builds).

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

### **Page 4: Herald Eden 🌐**

**Content**:
- **Cookies Group**: Cookies folder path (Browse only)
- **Browser Group**: Preferred browser, Auto-download drivers

**Info Box**:
- Links to Cookie Manager
- Explains cookie file location

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

### **Page 7: SuperAdmin 🔧⚡** (Conditional)

**Access Control**:
- **Required**: `python main.py --admin` flag
- **Blocked**: In compiled .exe (frozen check)
- **Condition**: `ADMIN_MODE = '--admin' in sys.argv and not sys.frozen`

**Content**:
- **Armory Section**: 
  * Warning banner about internal database modification
  * Build Database Group:
    - Multi-file .txt template selection
    - Realm dropdown (Albion/Hibernia/Midgard/All Realms)
    - Merge with existing checkbox
    - Remove duplicates checkbox
    - Auto-backup checkbox
    - Execute button (triggers build process)
  * Statistics Group (left 50%):
    - Database name label
    - Total items, Albion, Hibernia, Midgard, All Realms counts
    - File size, Last updated timestamp
    - Refresh button
  * Advanced Operations Group (right 50%):
    - Clean duplicates button

**Special Features**:
- **Triple-layer security**: Flag + frozen check + conditional UI
- **Auto-backup**: Creates timestamped backup before modifications
- **Multi-file import**: Parse multiple .txt files in one operation
- **Duplicate detection**: Removes items with same name+realm
- **Statistics tracking**: Real-time database stats display
- **Side-by-side layout**: Statistics and Advanced at 50/50 width

**Backend Integration**:
- Class: `Functions/superadmin_tools.py::SuperAdminTools`
- Methods: `build_database_from_files()`, `get_database_stats()`, `clean_duplicates()`
- Target: `Data/items_database_src.json` (internal read-only database)
- Backups: `Data/Backups/items_database_src_YYYYMMDD_HHMMSS.json`

**Translations**:
- Namespace: `superadmin.*` (40+ keys)
- Languages: FR/EN/DE
- No emojis in JSON (emojis added in code)

**Documentation**:
- See: `Settings/SUPERADMIN_TOOLS_EN.md` for complete technical documentation

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

---

## Path Management

### **Folder Operations**

**Browse Button**:
```python
def _browse_folder(self, line_edit, title_key):
    directory = QFileDialog.getExistingDirectory(...)
    normalized = directory.replace('/', '\\')  # Windows format
    line_edit.setText(normalized)
```

**Move Button**:
```python
def _move_folder(self, line_edit, config_key, folder_label):
    # 1. Detect if source exists (move) or not (create)
    # 2. Select destination parent folder
    # 3. Ask for folder name (pre-filled if exists)
    # 4. Confirm operation
    # 5. Copy with shutil.copytree() (if exists)
    # 6. Update line_edit with new path
    # 7. Optional: delete old folder
    # 8. Normalize path to backslashes
```

**Move vs Create Logic**:
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

---

## Configuration Persistence

### **Config File Location**

```
ALWAYS: <executable_directory>/Configuration/config.json
```

**Rationale**:
- ❌ Config folder is NOT configurable
- ✅ Avoids circular dependency issues
- ✅ Ensures portability
- ✅ Predictable location for troubleshooting

### **Saved Settings**

| Category | Settings | Config Keys |
|----------|----------|-------------|
| **Paths** | Character, Armor, Logs, Cookies folders | `character_folder`, `armor_folder`, `log_folder`, `cookies_folder` |
| **Defaults** | Server, Season, Realm | `default_server`, `default_season`, `default_realm` |
| **Display** | Theme, Font scale | `theme`, `font_scale` |
| **Columns** | Resize mode, Visibility | `manual_column_resize`, `column_visibility` |
| **Herald** | Browser, Auto-download | `preferred_browser`, `allow_browser_download` |
| **Backup** | Enabled, Paths, Compress, Limit | `backup_enabled`, `backup_path`, `backup_compress`, `backup_size_limit_mb`, `cookies_backup_enabled`, `cookies_backup_path` |
| **Debug** | Debug mode, Show window | `debug_mode`, `show_debug_window` |
| **Startup** | Disclaimer disabled | `disable_disclaimer` |
| **Language** | UI language | `language` |

---

## Special Behaviors

### **Character Folder Change Detection**

```python
# Compare normalized paths
old_char_folder = (config.get("character_folder") or "").replace('/', '\\')
new_char_folder = (dialog.char_path_edit.text() or "").replace('/', '\\')
char_folder_changed = (old_char_folder != new_char_folder)

if char_folder_changed:
    self._check_migration_on_path_change()
    self.refresh_character_list()  # Reload characters
```

**Trigger**: Character folder path changes  
**Action**: Automatically refresh character list without restart

### **Theme Application**

```python
if theme_changed:
    from Functions.theme_manager import apply_theme
    apply_theme(QApplication.instance(), new_theme)
    self.tree_manager.apply_tree_view_style()  # Reapply colors
```

**Effect**: Instant theme switch without restart

### **Language Change**

```python
if language_changed:
    config.set("language", new_lang_code)
    lang.set_language(new_lang_code)
    self.retranslate_ui()  # Refresh all UI text
```

**Effect**: Immediate language switch (no restart needed)

---

## Backup Integration

### **Backup Manager Initialization**

```python
from Functions.backup_manager import get_backup_manager, BackupManager

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

### **Open Folder**

```python
def _open_backup_folder(self):
    backup_path = self.backup_path_edit.text()
    subprocess.Popen(f'explorer "{backup_path}"')
```

---

## Translation System

### **Key Pattern**

```
settings_<page>_<element>
config_<group>_<element>
backup_<element>
```

### **Examples**

```python
lang.get("settings_general_title", default="General Settings")
lang.get("config_paths_group_title", default="Folder Paths")
lang.get("backup_now_button", default="Backup Now")
```

### **Supported Languages**

- 🇫🇷 **French** (Français) - Default
- 🇬🇧 **English**
- 🇩🇪 **German** (Deutsch)

**Total Translation Keys**: ~90+ for Settings System

---

## Window Lifecycle

```
Open Settings
    ↓
SettingsDialog.__init__(parent, languages, seasons, servers, realms)
    ↓
_init_ui()
    ├─ Create navigation (7 items)
    ├─ Create pages (7 pages)
    └─ Setup buttons
    ↓
_load_settings()
    └─ Populate all fields from config
    ↓
dialog.show()  # Non-modal
    ↓
User interacts...
    ↓
User clicks OK
    ↓
accepted.connect(lambda: save_configuration(dialog))
    ↓
save_configuration()
    ├─ Read all dialog values
    ├─ Compare with old values
    ├─ Apply changes
    └─ Show success message
    ↓
Dialog closes
```

---

## Error Handling

### **Path Normalization**

- All paths converted to Windows backslashes (`\\`)
- Prevents inconsistencies in config.json
- Ensures compatibility with file operations

### **Backup Operations**

```python
try:
    result = self.backup_manager.create_backup()
    if result:
        # Update UI + success message
    else:
        # Warning: backup failed
except Exception as e:
    # Critical error dialog with exception details
```

### **Folder Move Operations**

- Source existence validation
- Destination duplicate detection
- Progress dialog during copy
- Optional old folder deletion with confirmation
- Exception handling with error messages

---

## Performance Considerations

### **Lazy Loading**

```python
# Backup manager created only when Backup page is built
def _create_backup_page(self):
    from Functions.backup_manager import get_backup_manager
    self.backup_manager = get_backup_manager(config)
```

### **Efficient Updates**

- Only changed settings trigger updates
- Column visibility: bulk update vs individual
- Theme/Font: direct application vs restart

---

## File Structure

```
UI/
└── settings_dialog.py (713 lines)
    ├── Class SettingsDialog (lines 23-713)
    │   ├── __init__() (lines 30-52)
    │   ├── _init_ui() (lines 54-107)
    │   ├── _create_navigation() (lines 109-139)
    │   ├── _create_general_page() (lines 141-245)
    │   ├── _create_themes_page() (lines 247-299)
    │   ├── _create_startup_page() (lines 301-350)
    │   ├── _create_columns_page() (lines 352-413)
    │   ├── _create_herald_page() (lines 415-495)
    │   ├── _create_backup_page() (lines 497-700)
    │   ├── _create_debug_page() (lines 702-780)
    │   ├── Browse methods (lines 782-806)
    │   ├── Backup methods (lines 808-878)
    │   ├── _move_folder() (lines 880-980)
    │   └── _load_settings() (lines 982-1020)
```

---

## Dependencies

### **Qt Widgets**

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QLineEdit, QComboBox,
    QCheckBox, QDialogButtonBox, QFileDialog,
    QListWidget, QStackedWidget, QWidget, QListWidgetItem
)
```

### **Project Modules**

```python
from Functions.language_manager import lang
from Functions.config_manager import config, get_config_dir
from Functions.character_manager import get_character_dir
from Functions.logging_manager import get_log_dir
from Functions.path_manager import get_armor_dir
from Functions.backup_manager import get_backup_manager, BackupManager
```

---

## Integration Points

### **Main Window**

```python
# main.py
def open_configuration(self):
    from UI.settings_dialog import SettingsDialog
    dialog = SettingsDialog(self, languages, seasons, servers, realms)
    dialog.show()
    dialog.accepted.connect(lambda: self.save_configuration(dialog))
```

### **Menu Item**

```python
# Functions/ui_manager.py
settings_action = QAction(lang.get("menu_file_settings"), main_window)
settings_action.setShortcut("Ctrl+S")
settings_action.triggered.connect(main_window.open_configuration)
```

---

## Future Enhancements

**Potential Additions**:
- [ ] Search/filter in settings
- [ ] Settings profiles (save/load configurations)
- [ ] Import/Export settings
- [ ] Settings history/undo
- [ ] Keyboard navigation (arrow keys)
- [ ] Settings validation with visual feedback
- [ ] Advanced mode toggle (show/hide expert options)

---

## Version History

| Version | Changes |
|---------|---------|------|
| **0.108** | Complete reorganization with sidebar navigation |
| | - Removed monolithic dialog |
| | - Added 7 distinct pages |
| | - Integrated Backup settings |
| | - Added folder move functionality |
| | - Removed Tools menu |
| | - NEW: Page 7 SuperAdmin (conditional, development-only) |
| | - SuperAdmin: Build database from template files |
| | - SuperAdmin: Statistics tracking and duplicate cleaning |
| | - SuperAdmin: Triple-layer security (flag + frozen + UI) |
| | - SuperAdmin: Side-by-side layout (Stats 50% + Advanced 50%) |

---

## Related Documentation

- [SuperAdmin Tools](SUPERADMIN_TOOLS_EN.md) ⭐ NEW
- [Folder Move System](FOLDER_MOVE_SYSTEM_EN.md)
- [Backup Integration](BACKUP_INTEGRATION_EN.md)
- [Dual-Mode Database](../Armory/DUAL_MODE_DATABASE_EN.md)
- [Configuration Manager](../Core/CONFIG_MANAGER_EN.md)
- [Translation System](../Localization/TRANSLATION_SYSTEM_EN.md)
