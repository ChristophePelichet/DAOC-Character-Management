# Folder Move System - Technical Documentation

**Version**: 2.1  
**Last Updated**: 2025-11-15  
**Status**: ✅ Production Ready

---

## Overview

The **Folder Move System** allows users to physically relocate application data folders (Characters, Armor, Logs, Cookies, Backups) or create them if they don't exist yet. It provides a unified interface for folder management with **fixed folder names** and safety features.

**Location**: `UI/settings_dialog.py`  
**Method**: `_move_folder(line_edit, config_key, folder_label)`  
**Lines**: ~95 lines of code (optimized)

---

## Key Features (v2.1)

✅ **Fixed Folder Names** - No user input for folder names (predefined by application)  
✅ **Backup Special Handling** - Automatic `/Backups/` intermediate folder for backup paths  
✅ **Merge Support** - Ability to merge files when destination folder already exists  
✅ **Auto-Cleanup** - Automatic deletion of empty source folders after merge  
✅ **Parent Folder Cleanup** - Removes empty Backup parent folder when last subfolder deleted  
✅ **Immediate Reload** - Character list, logging system, and paths updated without restart  
✅ **Open Folder Buttons** - Quick access to all folders via 📂 button  
✅ **Consistent UI** - Same design pattern for all folder configurations  
✅ **Multi-language** - FR/EN/DE support with standardized translations

---

## Supported Folders

| Folder | Configurable | Move Button | Open Button | Browse Button | Fixed Name |
|--------|--------------|-------------|-------------|---------------|------------|
| **Characters** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | `Characters` |
| **Configuration** | ❌ No | ❌ No | ❌ No | ❌ No | N/A |
| **Armor** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | `Armor` |
| **Logs** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | `Logs` |
| **Cookies** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | `Cookies` |
| **Backups (Characters)** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | `Backups/Characters` |
| **Backups (Cookies)** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | `Backups/Cookies` |

**Note**: Configuration folder is NOT configurable to avoid circular dependency (config.json needs to know where it is stored).

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                 User clicks "📦 Déplacer"                    │
---

## Workflow Diagram (v2.0)

```
┌─────────────────────────────────────────────────────────────┐
│                 User clicks "📦 Déplacer"                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │  Does source exist?   │
      └───────┬───────────────┘
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
  YES: MOVE       NO: CREATE
      │               │
      │               │
      ▼               ▼
┌──────────┐    ┌──────────┐
│ Source:  │    │ Use      │
│ existing │    │ FIXED    │
│ folder   │    │ name     │
└────┬─────┘    └────┬─────┘
     │               │
     └───────┬───────┘
             │
             ▼
    ┌────────────────────┐
    │ Get FIXED name     │
    │ from config_key:   │
    │ - character_folder │
    │   → "Characters"   │
    │ - armor_folder     │
    │   → "Armor"        │
    │ - backup_path      │
    │   → "Backups"      │
    │   → /Characters    │
    └────┬───────────────┘
         │
         ▼
    ┌────────────────┐
    │ Select parent  │
    │ destination    │
    │ folder         │
    └────┬───────────┘
         │
         ▼
    ┌────────────────┐
    │ Build path:    │
    │ parent + name  │
    │ (NO user input)│
    └────┬───────────┘
         │
         ▼
    ┌────────────────┐
    │ Check if dest  │
    │ already exists │
    └────┬───────────┘
         │
     ┌───┴───┐
     │       │
EXISTS│       │AVAILABLE
     ▼       ▼
 ┌─────────┐  ┌──────────────┐
 │ Ask to  │  │Confirm action│
 │ use     │  │(Move/Create) │
 │ existing│  └──────┬───────┘
 └────┬────┘         │
      │              │
      ▼              ▼
   Update       ┌───────────────┐
   Config       │ Progress      │
                │ Dialog        │
                └───┬───────────┘
                    │
             ┌──────┴──────┐
             │             │
          MOVE│            │CREATE
             ▼             ▼
       ┌──────────┐  ┌──────────┐
       │Copy with │  │ mkdir()  │
       │shutil.   │  │ (with    │
       │copytree()│  │ parents) │
       └────┬─────┘  └────┬─────┘
            │             │
            └──────┬──────┘
                   │
                   ▼
           ┌────────────────┐
           │ Update line    │
           │ edit with new  │
           │ path           │
           └────┬───────────┘
                │
                ▼
           ┌────────────────┐
           │ Ask to delete  │◄─────(MOVE only)
           │ old folder?    │
           └────┬───────────┘
                │
            ┌───┴───┐
            │       │
           YES      NO
            │       │
            ▼       ▼
       ┌─────────┐ ┌──────────┐
       │ Delete  │ │ Keep old │
       │ with    │ │ folder   │
       │rmtree() │ │          │
       └────┬────┘ └────┬─────┘
            │           │
            └─────┬─────┘
                  │
                  ▼
           ┌─────────────┐
           │  Success    │
           │  Message    │
           └─────────────┘
```

---

## Method Signature

```python
def _move_folder(self, line_edit, config_key, folder_label):
    """
    Move or create a folder at a new location
    
    Args:
        line_edit (QLineEdit): The line edit displaying current path
        config_key (str): Configuration key for this folder
        folder_label (str): Human-readable folder label for messages
        
    Returns:
        None (updates line_edit and shows dialogs)
    """
```

---

## Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `line_edit` | `QLineEdit` | UI field displaying the folder path | `self.char_path_edit` |
| `config_key` | `str` | Configuration key for this folder | `"character_folder"` |
| `folder_label` | `str` | Human-readable label (unused in current implementation) | `"Characters"` |

---

## Operation Modes

### **Mode 1: MOVE with MERGE Support (Source Exists)**

**Trigger**: Source folder exists on disk  
**Flow**:

```
1. Get current path from line_edit
2. Verify source exists → YES: MOVE MODE
3. Select destination parent folder
4. Build destination path with FIXED folder name
5. Check if destination exists
   ├─ YES + Source exists: MERGE MODE
   │   ├─ Ask: "Do you want to merge files?"
   │   ├─ User says NO: Show "Operation cancelled", abort
   │   └─ User says YES: Continue to merge
   ├─ YES + Source missing: USE EXISTING MODE
   │   └─ Update config to use existing destination
   └─ NO: Continue with normal move
6. Confirm move with source/dest display
   ├─ User cancels: abort
   └─ User confirms: continue
7. Show progress dialog (indeterminate)
8. Copy folder: shutil.copytree(source, dest, dirs_exist_ok=True)
   - dirs_exist_ok=True allows merging into existing destination
   - Existing files are overwritten
   - New files are added
9. Update line_edit.setText(dest)
10. Save config immediately: config.set(config_key, dest)
11. Reinitialize BackupManager with new paths
12. Reload affected systems:
    ├─ character_folder changed: refresh_character_list()
    └─ log_folder changed: setup_logging()
13. Check if source folder is empty after copy
    ├─ Empty: Auto-delete source + cleanup parent Backup folder
    └─ Not empty: Ask user to delete
14. If user deletes old folder:
    ├─ shutil.rmtree(source)
    ├─ Check parent folder (if named "Backup")
    │   └─ If no remaining subfolders: shutil.rmtree(parent)
    └─ Show "Moved successfully"
15. If user keeps old folder:
    └─ Show "Copied successfully, old folder kept"
```

**Merge Example**:
```
Source:      D:\DAOC\Backup\Characters\ 
             ├─ backup_20251114.zip
             └─ backup_20251113.zip

Destination: E:\Backups\Characters\ (already exists)
             ├─ backup_20251115.zip
             └─ backup_20251112.zip

After Merge: E:\Backups\Characters\
             ├─ backup_20251115.zip (kept from destination)
             ├─ backup_20251114.zip (added from source)
             ├─ backup_20251113.zip (added from source)
             └─ backup_20251112.zip (kept from destination)

Source After: D:\DAOC\Backup\Characters\ (now empty)
              → Auto-deleted

Parent Check: D:\DAOC\Backup\ (check if empty)
              ├─ No other subfolders found
              → Auto-deleted for cleanliness
```

**Auto-Cleanup Logic**:
```python
# After copytree with merge
if os.path.exists(current_path):
    remaining_files = os.listdir(current_path)
    source_is_empty = len(remaining_files) == 0
    
    if source_is_empty:
        # Delete empty source
        shutil.rmtree(current_path)
        
        # Check parent Backup folder
        parent_backup = os.path.dirname(current_path)
        if os.path.basename(parent_backup).lower() == "backup":
            remaining_items = [item for item in os.listdir(parent_backup) 
                             if os.path.isdir(os.path.join(parent_backup, item))]
            if not remaining_items:
                # Parent Backup folder is empty, delete it
                shutil.rmtree(parent_backup)
```

---

### **Mode 2: CREATE (Source Missing)**

**Trigger**: Source folder doesn't exist  
**Flow**:

```
1. Get current path from line_edit (may be empty)
2. Verify source exists → NO: CREATE MODE
3. Suggest default folder name based on config_key
   ├─ character_folder → "Characters"
   ├─ armor_folder → "Armures"
   ├─ logs_folder → "Logs"
   └─ cookies_folder → "Cookies"
4. Select destination parent folder
5. Ask for folder name (pre-filled with suggestion)
6. Build destination path = parent + name
7. Check if destination exists
   ├─ YES: Show error, abort
   └─ NO: Continue
8. Confirm creation with dest display
   ├─ User cancels: abort
   └─ User confirms: continue
9. Show progress dialog
10. Create folder: os.makedirs(dest, exist_ok=True)
11. Update line_edit.setText(dest)
12. Show "Created successfully"
```

**Example**:
```
Source: (empty or non-existent)
Suggested: "Characters"
Parent: E:\MyDAOC
Result: E:\MyDAOC\Characters created
        Config updated: character_folder = E:\MyDAOC\Characters
        Character list reloaded immediately (if Characters folder)
```

---

## Immediate System Reload

**Critical Feature**: Path changes are applied **immediately** without requiring application restart.

### **Reload Triggers by Folder Type**

```python
# After successful move/create/browse operation:

if config_key == "character_folder":
    # Save to config
    config.set("character_folder", new_path)
    config.save_config()
    
    # Reinitialize backup manager
    self.backup_manager = BackupManager(config)
    
    # Reload character list from new location
    if self.parent():
        self.parent().refresh_character_list()

elif config_key == "log_folder":
    # Save to config
    config.set("log_folder", new_path)
    config.save_config()
    
    # Reinitialize logging system
    from Functions.logging_manager import setup_logging
    setup_logging()
    # New logs will now be written to new location

elif config_key == "armor_folder":
    # Save to config
    config.set("armor_folder", new_path)
    config.save_config()
    # Armor data loaded on-demand, no reload needed

elif config_key in ["backup_path", "cookies_backup_path", "armor_backup_path"]:
    # Save to config
    config.set(config_key, new_path)
    config.save_config()
    
    # Reinitialize backup manager to use new paths
    self.backup_manager = BackupManager(config)
```

### **Browse Immediate Reload**

Browse buttons also trigger immediate reload:

```python
def _browse_character_folder(self):
    old_path = self.char_path_edit.text()
    self._browse_folder(self.char_path_edit, "select_folder_dialog_title")
    new_path = self.char_path_edit.text()
    
    if old_path != new_path:
        config.set("character_folder", new_path)
        config.save_config()
        if self.parent():
            self.parent().refresh_character_list()

def _browse_log_folder(self):
    old_path = self.log_path_edit.text()
    self._browse_folder(self.log_path_edit, "select_log_folder_dialog_title")
    new_path = self.log_path_edit.text()
    
    if old_path != new_path:
        config.set("log_folder", new_path)
        config.save_config()
        from Functions.logging_manager import setup_logging
        setup_logging()

def _browse_armor_folder(self):
    old_path = self.armor_path_edit.text()
    self._browse_folder(self.armor_path_edit, "select_folder_dialog_title")
    new_path = self.armor_path_edit.text()
    
    if old_path != new_path:
        config.set("armor_folder", new_path)
        config.save_config()
```

**Result**: User sees changes instantly in the UI without closing Settings dialog.

---

## Default Folder Names

```python
default_name = {
    "character_folder": "Characters",
    "configuration_directory": "Configuration",
    "armor_folder": "Armures",
    "logs_directory": "Logs",
    "cookies_folder": "Cookies"
}.get(config_key, "Nouveau_Dossier")
```

**Purpose**: Provide intelligent defaults based on folder type

---

## Path Normalization

### **Windows Backslash Format**

All paths are normalized to Windows backslashes (`\\`) for consistency:

```python
# After folder selection
parent_dir = parent_dir.replace('/', '\\')

# Destination already normalized via os.path.join()
destination = os.path.join(parent_dir, folder_name)  # Uses \\
```

**Rationale**:
- ✅ Consistent format in config.json
- ✅ Avoids comparison issues (D:/path vs D:\\path)
- ✅ Windows-native format
- ✅ Compatible with all file operations

---

## Confirmation Dialogs

### **Move Confirmation**

```python
QMessageBox.question(
    self,
    lang.get("move_folder_confirm_title", default="Confirmer le déplacement"),
    f"{lang.get('move_folder_confirm_message', default='Voulez-vous déplacer le dossier ?')}\n\n"
    f"De : {current_path}\n"
    f"Vers : {destination}",
    QMessageBox.Yes | QMessageBox.No,
    QMessageBox.No  # Default: No
)
```

**Display**:
```
┌────────────────────────────────────┐
│   Confirmer le déplacement         │
├────────────────────────────────────┤
│ Voulez-vous déplacer le dossier    │
│ et son contenu ?                   │
│                                    │
│ De : D:\DAOC\Characters            │
│ Vers : E:\Backup\Characters        │
│                                    │
│         [Yes]        [No]          │
└────────────────────────────────────┘
```

### **Create Confirmation**

```python
QMessageBox.question(
    self,
    lang.get("create_folder_confirm_title", default="Créer le dossier"),
    f"{lang.get('create_folder_confirm_message', default='Créer le dossier ?')}\n\n"
    f"{destination}",
    QMessageBox.Yes | QMessageBox.No,
    QMessageBox.No
)
```

### **Delete Old Folder Confirmation**

```python
QMessageBox.question(
    self,
    lang.get("move_folder_delete_title", default="Supprimer l'ancien dossier ?"),
    f"{lang.get('move_folder_delete_message', default='Le dossier a été copié. Supprimer l\'ancien ?')}\n\n"
    f"{current_path}",
    QMessageBox.Yes | QMessageBox.No,
    QMessageBox.No  # Default: No (safe)
)
```

---

## Progress Feedback

```python
progress = QProgressDialog(
    lang.get("move_folder_in_progress", default="Opération en cours..."),
    lang.get("cancel", default="Annuler"),
    0, 0,  # Indeterminate progress (0 to 0)
    self
)
progress.setWindowModality(Qt.WindowModal)
progress.setWindowTitle(lang.get("move_folder_title", default="Déplacement"))
progress.show()

try:
    # Long operation (copy or create)
    shutil.copytree(source, dest)
finally:
    progress.close()
```

**Visual**:
```
┌────────────────────────────────┐
│        Déplacement             │
├────────────────────────────────┤
│ Opération en cours...          │
│ [████████████████████]         │
│           [Annuler]            │
└────────────────────────────────┘
```

---

## Error Handling

### **Destination Already Exists**

```python
if os.path.exists(destination):
    QMessageBox.warning(
        self,
        lang.get("warning_title", default="Attention"),
        lang.get("move_folder_destination_exists", 
                default=f"Le dossier '{folder_name}' existe déjà.")
    )
    return  # Abort operation
```

### **Exception During Copy**

```python
try:
    shutil.copytree(current_path, destination)
    # ...
except Exception as e:
    progress.close()
    QMessageBox.critical(
        self,
        lang.get("error_title", default="Erreur"),
        lang.get("move_folder_error", 
                default=f"Erreur lors du déplacement :\n{str(e)}")
    )
    logging.error(f"Error moving folder: {e}")
```

---

## Safety Features

### **1. Copy Before Delete**

**Pattern**: Copy-first, then optionally delete

```
✅ SAFE: Copy → Verify → Ask → Delete
❌ UNSAFE: Move (atomic, no backup)
```

**Advantage**: User can keep both old and new if desired

### **2. Confirmation at Every Step**

- ✅ Confirm move/create operation
- ✅ Confirm old folder deletion (separate step)
- ✅ Default answer is always "No" (safe choice)

### **3. Duplicate Detection**

```python
if os.path.exists(destination):
    # Abort before any file operation
```

**Prevents**: Accidental overwrite of existing folders

### **4. Path Validation**

```python
source_exists = current_path and os.path.exists(current_path)
```

**Handles**: Empty paths, non-existent paths, None values

---

## Success Messages

### **Move + Delete**

```
Titre: Succès
Message: Dossier déplacé avec succès vers :
         E:\Backup\Characters
```

### **Move + Keep**

```
Titre: Succès
Message: Dossier copié avec succès vers :
         E:\Backup\Characters

         L'ancien dossier a été conservé.
```

### **Create**

```
Titre: Succès
Message: Dossier créé avec succès :
         E:\MyDAOC\Characters
```

---

## Translation Keys

### **UI Labels**

```json
{
    "move_folder_button": "Déplacer",
    "move_folder_tooltip": "Déplacer ou créer ce dossier à un nouvel emplacement"
}
```

### **Dialogs**

```json
{
    "move_folder_select_destination": "Sélectionnez le dossier parent de destination",
    "move_folder_name_title": "Nom du dossier",
    "move_folder_name_message": "Entrez le nom du dossier :",
    "move_folder_confirm_title": "Confirmer le déplacement",
    "move_folder_confirm_message": "Voulez-vous déplacer le dossier et son contenu ?",
    "create_folder_confirm_title": "Créer le dossier",
    "create_folder_confirm_message": "Créer le dossier à cet emplacement ?",
    "move_folder_in_progress": "Opération en cours...",
    "move_folder_title": "Déplacement",
    "move_folder_destination_exists": "Le dossier existe déjà à la destination.",
    "move_folder_delete_title": "Supprimer l'ancien dossier ?",
    "move_folder_delete_message": "Le dossier a été copié avec succès. Voulez-vous supprimer l'ancien dossier ?",
    "move_folder_success": "Dossier déplacé avec succès.",
    "move_folder_copy_success": "Dossier copié avec succès. L'ancien dossier a été conservé.",
    "create_folder_success": "Dossier créé avec succès"
}
```

---

## Usage Examples

### **Example 1: Move Characters to External Drive**

```
Initial state:
  character_folder = D:\DAOC\Characters
  Folder exists with 50 character files

User action:
  1. Settings > General > Characters > Click "📦 Déplacer"
  2. Select parent: E:\GameBackups
  3. Enter name: "DAOC_Characters" (change from default)
  4. Confirm move
  5. Wait for copy (progress bar)
  6. Choose YES to delete old folder

Result:
  character_folder = E:\GameBackups\DAOC_Characters
  Old folder deleted
  All 50 files moved
  Character list refreshed automatically
```

### **Example 2: Create New Logs Folder**

```
Initial state:
  log_folder = (not set or missing)

User action:
  1. Settings > Debug > Logs > Click "📦 Déplacer"
  2. Select parent: C:\MyLogs
  3. Keep suggested name: "Logs"
  4. Confirm creation

Result:
  log_folder = C:\MyLogs\Logs
  Empty folder created
  Future logs will go there
```

### **Example 3: Reorganize All Folders**

```
Goal: Move all data to E:\DAOC-Manager

Steps:
  1. Move Characters: E:\DAOC-Manager\Characters
  2. Move Armor: E:\DAOC-Manager\Armures
  3. Move Logs: E:\DAOC-Manager\Logs
  4. Move Cookies: E:\DAOC-Manager\Cookies

Result:
  Centralized data structure:
    E:\DAOC-Manager\
      ├─ Characters\
      ├─ Armures\
      ├─ Logs\
      └─ Cookies\
  
  Config.json updated with all new paths
```

---

## Integration with Settings Save

```python
# main.py - save_configuration()

# Character folder change detection
old_char_folder = (config.get("character_folder") or "").replace('/', '\\')
new_char_folder = (dialog.char_path_edit.text() or "").replace('/', '\\')
char_folder_changed = (old_char_folder != new_char_folder)

if char_folder_changed:
    # Check migration if needed
    self._check_migration_on_path_change()
    # Reload characters from new location
    self.refresh_character_list()
```

**Effect**: Automatic character list refresh when folder changes

---

## Related Functions

### **Browse Folder** (Simpler Alternative)

```python
def _browse_folder(self, line_edit, title_key):
    directory = QFileDialog.getExistingDirectory(self, lang.get(title_key))
    if directory:
        normalized = directory.replace('/', '\\')
        line_edit.setText(normalized)
```

**Difference**:
- ❌ Doesn't copy files
- ❌ Doesn't create folder
- ✅ Only changes config path
- ✅ User must manually move files

---

## Performance Considerations

### **Large Folders**

For folders with many files:
- ✅ `shutil.copytree()` is efficient (C-level operations)
- ✅ Progress dialog provides visual feedback
- ✅ Operation is not cancellable (indeterminate progress)

**Recommendation**: For very large folders (>1GB), inform user to wait

### **Network Drives**

Moving to/from network drives:
- ⚠️ Slower performance
- ⚠️ Potential timeouts
- ✅ Progress dialog still functional

---

## Limitations

| Limitation | Workaround |
|------------|------------|
| Cannot cancel during copy | Don't provide cancel button (indeterminate progress) |
| No progress percentage | Use indeterminate progress bar |
| Locked files fail operation | Close application before moving |
| Network path timeouts | Use local paths when possible |
| No undo capability | "Keep old folder" provides manual undo |

---

## Future Enhancements

**Potential Improvements**:
- [x] **Merge support** - Implemented in v3.0
- [x] **Auto-cleanup empty folders** - Implemented in v3.0
- [x] **Immediate reload** - Implemented in v3.0
- [ ] Show folder size before move
- [ ] Disk space validation
- [ ] Move with progress percentage (for large folders)
- [ ] Undo/rollback capability
- [ ] Batch move (multiple folders at once)
- [ ] Compression during move
- [ ] Network path optimization

---

## Version History

| Version | Changes |
|---------|---------||
| **0.108** | v2.1 Enhanced Update |
| | - Merge support when destination exists |
| | - Auto-delete empty source folders |
| | - Auto-cleanup parent Backup folder |
| | - Immediate system reload (Characters, Logs, Armor) |
| | - Browse buttons trigger immediate save |
| | - Fixed folder names |
| | - Move + Create modes |
| | - Path normalization |
| | - Safety confirmations |
| | - Progress feedback |

---

## Related Documentation

- [Settings Architecture](SETTINGS_ARCHITECTURE_EN.md)
- [Configuration Manager](../Core/CONFIG_MANAGER_EN.md)
- [Path Manager](../Core/PATH_MANAGER_EN.md)
