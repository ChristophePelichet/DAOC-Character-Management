# Folder Move System - Technical Documentation

## Overview

The **Folder Move System** allows users to physically relocate application data folders (Characters, Armor, Logs, Cookies) or create them if they don't exist yet. It provides a unified interface for folder management with safety features and user confirmations.

**Location**: `UI/settings_dialog.py`  
**Method**: `_move_folder(line_edit, config_key, folder_label)`  
**Lines**: ~115 lines of code

---

## Supported Folders

| Folder | Configurable | Move Button | Browse Button |
|--------|--------------|-------------|---------------|
| **Characters** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Configuration** | ❌ No | ❌ No | ❌ No |
| **Armor** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Logs** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cookies** | ✅ Yes | ✅ Yes | ✅ Yes |

**Note**: Configuration folder is NOT configurable to avoid circular dependency (config.json needs to know where it is stored).

---

## Workflow Diagram

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
│ Source:  │    │ Suggest  │
│ existing │    │ default  │
│ folder   │    │ name     │
└────┬─────┘    └────┬─────┘
     │               │
     └───────┬───────┘
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
    │ Enter folder   │
    │ name (or keep  │
    │ suggested)     │
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
 ┌─────┐  ┌──────────────┐
 │ERROR│  │Confirm action│
 │ Stop│  │(Move/Create) │
 └─────┘  └──────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Progress      │
         │ Dialog        │
         └───┬───────────┘
             │
      ┌──────┴──────┐
      │             │
   MOVE│            │CREATE
      ▼             ▼
┌──────────┐  ┌──────────┐
│Copy with │  │ mkdir()  │
│shutil.   │  │          │
│copytree()│  │          │
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

### **Mode 1: MOVE (Source Exists)**

**Trigger**: Source folder exists on disk  
**Flow**:

```
1. Get current path from line_edit
2. Verify source exists → YES: MOVE MODE
3. Select destination parent folder
4. Ask for folder name (pre-filled with current name)
5. Build destination path = parent + name
6. Check if destination exists
   ├─ YES: Show error, abort
   └─ NO: Continue
7. Confirm move with source/dest display
   ├─ User cancels: abort
   └─ User confirms: continue
8. Show progress dialog
9. Copy folder: shutil.copytree(source, dest)
10. Update line_edit.setText(dest)
11. Ask: Delete old folder?
    ├─ YES: shutil.rmtree(source)
    │       Show "Moved successfully"
    └─ NO:  Show "Copied successfully, old folder kept"
```

**Example**:
```
Source: D:\DAOC\Characters
Dest:   E:\Backups\DAOC\Characters

Result: Folder copied to E:\Backups\DAOC\Characters
        User chooses to delete D:\DAOC\Characters
        Config updated: character_folder = E:\Backups\DAOC\Characters
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
```

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
|---------|---------|
| **0.108** | Initial implementation |
| | - Move + Create modes |
| | - Path normalization |
| | - Safety confirmations |
| | - Progress feedback |

---

## Related Documentation

- [Settings Architecture](SETTINGS_ARCHITECTURE_EN.md)
- [Configuration Manager](../Core/CONFIG_MANAGER_EN.md)
- [Path Manager](../Core/PATH_MANAGER_EN.md)
