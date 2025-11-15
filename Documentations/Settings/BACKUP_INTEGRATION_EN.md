# Backup Integration in Settings - Technical Documentation

## Overview

The **Backup Integration** in Settings provides a unified interface for managing all backup operations directly from the Settings dialog. It replaced the previous Tools > Backups menu system, offering real-time backup execution, configuration, and monitoring.

**Location**: `UI/settings_dialog.py` - Page 5  
**Section**: `_create_backup_page()` (lines 497-700)  
**Integration**: `main.py` - `save_configuration()` (backup settings save)

---

## Architecture

```
Settings Dialog
    ↓
Page 5: Sauvegardes 💾
    ├── Characters Backup Section
    │   ├── Enable/Disable
    │   ├── Path Configuration
    │   ├── Compression Option
    │   ├── Size Limit
    │   ├── Statistics (Count, Last Date)
    │   └── Actions (Backup Now, Open Folder)
    │
    └── Cookies Backup Section
        ├── Enable/Disable
        ├── Path Configuration
        ├── Statistics (Count, Last Date)
        └── Actions (Backup Now, Open Folder)
```

---

## Backup Manager Integration

### **Initialization**

```python
def _create_backup_page(self):
    from Functions.backup_manager import get_backup_manager, BackupManager
    
    # Initialize backup manager
    self.backup_manager = get_backup_manager(config)
    if self.backup_manager is None:
        self.backup_manager = BackupManager(config)
    
    # Get backup info for statistics
    backup_info = self.backup_manager.get_backup_info()
    cookies_info = self.backup_manager.get_cookies_backup_info()
```

**Pattern**: Lazy initialization when page is created

---

## Characters Backup Section

### **UI Layout**

```
┌─────────────────────────────────────────────────────┐
│ 📁 Sauvegardes des personnages                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ☑ Activer les sauvegardes                          │
│                                                     │
│ Dossier de sauvegarde:                              │
│ ┌─────────────────────────────────┬──────────┐     │
│ │ D:\...\Backup\Characters        │[Parcourir]│     │
│ └─────────────────────────────────┴──────────┘     │
│                                                     │
│ ☑ Compresser les sauvegardes (ZIP)                 │
│                                                     │
│ Limite de taille: [20] MB  (Limite totale)         │
│                                                     │
│ Nombre de sauvegardes:    15                        │
│ Dernière sauvegarde:      2025-11-15 14:30:00      │
│                                                     │
│ [Sauvegarder maintenant] [📂 Ouvrir le dossier]    │
└─────────────────────────────────────────────────────┘
```

### **Configuration Fields**

| Field | Widget | Config Key | Default |
|-------|--------|------------|---------|
| Enable | `QCheckBox` | `backup_enabled` | `True` |
| Path | `QLineEdit` (read-only) | `backup_path` | `<base>/Backup/Characters` |
| Compress | `QCheckBox` | `backup_compress` | `True` |
| Size Limit | `QLineEdit` | `backup_size_limit_mb` | `20` |

### **Statistics Display**

```python
# Total backups count
total_backups = len(backup_info["backups"])
self.backup_total_label = QLabel(f"{total_backups}")
self.backup_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")

# Last backup date
last_backup_date = config.get("backup_last_date")
if last_backup_date:
    dt = datetime.fromisoformat(last_backup_date)
    last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
else:
    last_backup_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
```

**Styling**:
- Bold font weight
- Blue color (#0078D4 - Microsoft Blue)
- Real-time updates after backup

---

## Cookies Backup Section

### **UI Layout**

```
┌─────────────────────────────────────────────────────┐
│ 🍪 Sauvegardes des cookies Eden                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ☑ Activer les sauvegardes                          │
│                                                     │
│ Dossier de sauvegarde:                              │
│ ┌─────────────────────────────────┬──────────┐     │
│ │ D:\...\Backup\Cookies           │[Parcourir]│     │
│ └─────────────────────────────────┴──────────┘     │
│                                                     │
│ Nombre de sauvegardes:    8                         │
│ Dernière sauvegarde:      2025-11-15 07:45:00      │
│                                                     │
│ [Sauvegarder maintenant] [📂 Ouvrir le dossier]    │
└─────────────────────────────────────────────────────┘
```

### **Configuration Fields**

| Field | Widget | Config Key | Default |
|-------|--------|------------|---------|
| Enable | `QCheckBox` | `cookies_backup_enabled` | `True` |
| Path | `QLineEdit` (read-only) | `cookies_backup_path` | `<base>/Backup/Cookies` |

**Note**: Cookies backups don't have compression/size limit options (simpler)

---

## Action Buttons

### **Backup Now Button (Characters)**

```python
backup_now_button = QPushButton(lang.get("backup_now_button", default="Sauvegarder maintenant"))
backup_now_button.setStyleSheet("""
    QPushButton {
        padding: 6px 12px;
        font-weight: bold;
        background-color: #0078D4;
        color: white;
        border-radius: 4px;
    }
""")
backup_now_button.clicked.connect(self._backup_now)
```

**Style**: Microsoft Blue (#0078D4), Bold, White text

### **Open Folder Button**

```python
open_folder_button = QPushButton("📂 " + lang.get("backup_open_folder", default="Ouvrir le dossier"))
open_folder_button.setStyleSheet("""
    QPushButton {
        padding: 6px 12px;
        font-weight: bold;
        background-color: #107C10;
        color: white;
        border-radius: 4px;
    }
""")
open_folder_button.clicked.connect(self._open_backup_folder)
```

**Style**: Green (#107C10), Bold, White text

---

## Backup Execution Workflow

### **Characters Backup**

```
User clicks "Sauvegarder maintenant"
    ↓
_backup_now() method
    ↓
try:
    ├─ backup_manager.create_backup()
    ├─ if result:
    │   ├─ Update last_backup_label (now timestamp)
    │   ├─ Update total_label (re-query backup_info)
    │   └─ Show success message
    └─ else:
        └─ Show warning (backup failed)
catch Exception:
    └─ Show error dialog with exception details
```

### **Implementation**

```python
def _backup_now(self):
    """Execute characters backup now"""
    from PySide6.QtWidgets import QMessageBox
    try:
        result = self.backup_manager.create_backup()
        if result:
            # Update last backup date display
            from datetime import datetime
            last_backup_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.backup_last_label.setText(last_backup_str)
            self.backup_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
            
            # Update total count
            backup_info = self.backup_manager.get_backup_info()
            self.backup_total_label.setText(str(len(backup_info["backups"])))
            
            QMessageBox.information(self, lang.get("success_title"), 
                                   lang.get("backup_success"))
        else:
            QMessageBox.warning(self, lang.get("warning_title"),
                               lang.get("backup_failed"))
    except Exception as e:
        QMessageBox.critical(self, lang.get("error_title"),
                            f"{lang.get('backup_error')} : {str(e)}")
```

---

## Cookies Backup Workflow

### **Flow**

```
User clicks "Sauvegarder maintenant" (Cookies section)
    ↓
_backup_cookies_now() method
    ↓
try:
    ├─ backup_manager.backup_cookies()
    ├─ if result:
    │   ├─ Update cookies_last_label (now timestamp)
    │   ├─ Update cookies_total_label (re-query cookies_info)
    │   └─ Show success message
    └─ else:
        └─ Show warning (backup failed)
catch Exception:
    └─ Show error dialog
```

### **Implementation**

```python
def _backup_cookies_now(self):
    """Execute cookies backup now"""
    try:
        result = self.backup_manager.backup_cookies()
        if result:
            from datetime import datetime
            last_backup_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cookies_last_label.setText(last_backup_str)
            
            cookies_info = self.backup_manager.get_cookies_backup_info()
            self.cookies_total_label.setText(str(len(cookies_info["backups"])))
            
            QMessageBox.information(self, lang.get("success_title"),
                                   lang.get("backup_success"))
        else:
            QMessageBox.warning(self, lang.get("warning_title"),
                               lang.get("backup_failed"))
    except Exception as e:
        QMessageBox.critical(self, lang.get("error_title"),
                            f"{lang.get('backup_error')} : {str(e)}")
```

---

## Folder Browser

### **Characters Backup Path**

```python
def _browse_backup_path(self):
    """Browse for backup folder"""
    directory = QFileDialog.getExistingDirectory(
        self, 
        lang.get("backup_select_folder", default="Sélectionner le dossier de sauvegarde")
    )
    if directory:
        normalized_directory = directory.replace('/', '\\')
        self.backup_path_edit.setText(normalized_directory)
```

### **Cookies Backup Path**

```python
def _browse_cookies_backup_path(self):
    """Browse for cookies backup folder"""
    directory = QFileDialog.getExistingDirectory(
        self, 
        lang.get("backup_select_folder")
    )
    if directory:
        normalized_directory = directory.replace('/', '\\')
        self.cookies_backup_path_edit.setText(normalized_directory)
```

**Path Normalization**: Always convert to Windows backslashes

---

## Open Folder Actions

### **Characters Backup Folder**

```python
def _open_backup_folder(self):
    """Open characters backup folder"""
    import subprocess
    backup_path = self.backup_path_edit.text()
    if os.path.exists(backup_path):
        subprocess.Popen(f'explorer "{backup_path}"')
```

### **Cookies Backup Folder**

```python
def _open_cookies_backup_folder(self):
    """Open cookies backup folder"""
    import subprocess
    cookies_backup_path = self.cookies_backup_path_edit.text()
    if os.path.exists(cookies_backup_path):
        subprocess.Popen(f'explorer "{cookies_backup_path}"')
```

**Effect**: Opens Windows Explorer at backup folder location

---

## Settings Persistence

### **Save Operation**

```python
# main.py - save_configuration()

# Backup settings
if hasattr(dialog, 'backup_enabled_check'):
    config.set("backup_enabled", dialog.backup_enabled_check.isChecked())
    config.set("backup_path", dialog.backup_path_edit.text())
    config.set("backup_compress", dialog.backup_compress_check.isChecked())
    
    try:
        size_limit = int(dialog.backup_size_limit_edit.text())
        config.set("backup_size_limit_mb", size_limit)
    except ValueError:
        pass  # Keep existing value if invalid
    
    config.set("cookies_backup_enabled", dialog.cookies_backup_enabled_check.isChecked())
    config.set("cookies_backup_path", dialog.cookies_backup_path_edit.text())
```

**Validation**:
- Size limit must be valid integer
- If invalid, keep existing value (silent fail)
- All other fields saved directly

---

## Statistics Display

### **Backup Count**

```python
backup_info = self.backup_manager.get_backup_info()
total_backups = len(backup_info["backups"])

self.backup_total_label = QLabel(f"{total_backups}")
self.backup_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
```

**Data Source**: `backup_manager.get_backup_info()["backups"]`  
**Format**: Integer count

### **Last Backup Date**

```python
last_backup_date = config.get("backup_last_date")
if last_backup_date:
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(last_backup_date)
        last_backup_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        last_backup_str = "N/A"
else:
    last_backup_str = lang.get("backup_no_backup", default="Aucune sauvegarde")
```

**Data Source**: `config.get("backup_last_date")` (ISO 8601 format)  
**Format**: `YYYY-MM-DD HH:MM:SS`

### **Real-Time Updates**

After successful backup:
```python
# Update timestamp
from datetime import datetime
last_backup_str = datetime.now().strftime("%Y-%m-%d %H:%M:% S")
self.backup_last_label.setText(last_backup_str)

# Update count
backup_info = self.backup_manager.get_backup_info()
self.backup_total_label.setText(str(len(backup_info["backups"])))
```

**Effect**: User sees updated stats immediately without closing dialog

---

## Default Paths

### **Characters Backup**

```python
backup_path = config.get("backup_path")
if not backup_path:
    from Functions.path_manager import get_base_path
    backup_path = os.path.join(get_base_path(), "Backup", "Characters")
```

**Default**: `<executable_dir>/Backup/Characters`

### **Cookies Backup**

```python
cookies_backup_path = config.get("cookies_backup_path")
if not cookies_backup_path:
    from Functions.path_manager import get_base_path
    cookies_backup_path = os.path.join(get_base_path(), "Backup", "Cookies")
```

**Default**: `<executable_dir>/Backup/Cookies`

---

## Translation Keys

### **Section Titles**

```json
{
    "settings_backup_title": "Sauvegardes",
    "settings_backup_subtitle": "Configuration des sauvegardes automatiques",
    "backup_characters_title": "Sauvegardes des personnages",
    "backup_cookies_title": "Sauvegardes des cookies Eden"
}
```

### **Field Labels**

```json
{
    "backup_enabled_label": "Activer les sauvegardes",
    "backup_path_label": "Dossier de sauvegarde",
    "backup_compress_label": "Compresser les sauvegardes (ZIP)",
    "backup_compress_tooltip": "Réduit la taille des sauvegardes",
    "backup_size_limit_label": "Limite de taille",
    "backup_size_limit_tooltip": "Limite totale",
    "backup_total_label": "Nombre de sauvegardes",
    "backup_last_label": "Dernière sauvegarde",
    "backup_no_backup": "Aucune sauvegarde"
}
```

### **Actions**

```json
{
    "backup_now_button": "Sauvegarder maintenant",
    "backup_open_folder": "Ouvrir le dossier",
    "backup_select_folder": "Sélectionner le dossier de sauvegarde"
}
```

### **Messages**

```json
{
    "backup_success": "Sauvegarde créée avec succès",
    "backup_failed": "La sauvegarde a échoué",
    "backup_error": "Erreur lors de la sauvegarde"
}
```

---

## Message Dialogs

### **Success**

```
┌──────────────────────────────┐
│        Succès                │
├──────────────────────────────┤
│ Sauvegarde créée avec succès │
│                              │
│            [OK]              │
└──────────────────────────────┘
```

### **Warning (Failed)**

```
┌──────────────────────────────┐
│        Attention             │
├──────────────────────────────┤
│ La sauvegarde a échoué       │
│                              │
│            [OK]              │
└──────────────────────────────┘
```

### **Error**

```
┌────────────────────────────────────┐
│           Erreur                   │
├────────────────────────────────────┤
│ Erreur lors de la sauvegarde :     │
│ [Errno 13] Permission denied       │
│                                    │
│              [OK]                  │
└────────────────────────────────────┘
```

---

## Comparison: Old vs New System

### **Old System (Tools Menu)**

```
Tools Menu
    ↓
Sauvegardes
    ↓
BackupSettingsDialog (modal)
    ├─ Separate window
    ├─ Blocks main window
    └─ Isolated from other settings
```

**Drawbacks**:
- ❌ Separate menu navigation
- ❌ Modal dialog blocks application
- ❌ Not integrated with other settings
- ❌ Requires separate documentation path

### **New System (Settings Page)**

```
Settings Dialog (non-modal)
    ↓
Page 5: Sauvegardes
    ├─ Integrated with other settings
    ├─ Doesn't block main window
    └─ Consistent UX with other pages
```

**Advantages**:
- ✅ Unified settings location
- ✅ Non-blocking interface
- ✅ Consistent navigation
- ✅ Single save operation for all settings
- ✅ Real-time statistics update

---

## Removed Components

### **Tools Menu**

```python
# Functions/ui_manager.py - DELETED
tools_menu = menubar.addMenu(lang.get("tools_menu"))
backup_action = QAction(lang.get("backup_menu_item"), main_window)
backup_action.triggered.connect(main_window.open_backup_settings)
tools_menu.addAction(backup_action)
```

**Reason**: Consolidation into Settings

### **BackupSettingsDialog**

**Status**: Still exists in `UI/dialogs.py` but no longer used  
**Future**: Can be deleted in cleanup

---

## Error Scenarios

### **Backup Manager Not Initialized**

```python
self.backup_manager = get_backup_manager(config)
if self.backup_manager is None:
    self.backup_manager = BackupManager(config)
```

**Handling**: Create new instance if global instance missing

### **Invalid Size Limit**

```python
try:
    size_limit = int(dialog.backup_size_limit_edit.text())
    config.set("backup_size_limit_mb", size_limit)
except ValueError:
    pass  # Keep existing value
```

**Handling**: Silent fail, preserve previous value

### **Folder Doesn't Exist**

```python
if os.path.exists(backup_path):
    subprocess.Popen(f'explorer "{backup_path}"')
```

**Handling**: Only open if exists (no error shown)

---

## Performance Considerations

### **Backup Info Retrieval**

```python
# Called once during page creation
backup_info = self.backup_manager.get_backup_info()
```

**Cost**: File system scan of backup folder  
**Frequency**: Once per settings dialog open

### **Real-Time Updates**

```python
# After each backup
backup_info = self.backup_manager.get_backup_info()
self.backup_total_label.setText(str(len(backup_info["backups"])))
```

**Cost**: Re-scan backup folder  
**Frequency**: Once per manual backup

---

## Future Enhancements

**Potential Additions**:
- [ ] Automatic backup scheduling (daily/weekly)
- [ ] Backup retention policy (auto-delete old backups)
- [ ] Backup to cloud storage
- [ ] Restore from backup UI
- [ ] Backup comparison/diff
- [ ] Incremental backups
- [ ] Email notifications on backup completion

---

## Version History

| Version | Changes |
|---------|---------|
| **0.108** | Moved from Tools menu to Settings page |
| | - Integrated Characters backup |
| | - Integrated Cookies backup |
| | - Real-time statistics |
| | - Removed modal dialog |

---

## Related Documentation

- [Settings Architecture](SETTINGS_ARCHITECTURE_EN.md)
- [Backup Manager](../Core/BACKUP_MANAGER_EN.md)
- [Configuration Manager](../Core/CONFIG_MANAGER_EN.md)
