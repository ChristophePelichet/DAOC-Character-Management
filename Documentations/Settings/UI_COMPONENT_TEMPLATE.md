# Settings UI Component Template

**Version**: 1.0  
**Date**: 2025-11-15  
**Purpose**: Standard template for creating consistent UI components in Settings dialog

---

## 📋 Overview

This template provides the standard pattern for creating folder path configurations in the Settings dialog. All folder settings should follow this consistent design to ensure a uniform user experience.

---

## 🎨 Standard Folder Path Component

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ 📁 Group Title                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Label:  [________________Path________________] [Browse] [📦] [📂] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components

1. **QGroupBox** - Container with emoji + title
2. **QLineEdit** - Read-only path display
3. **Browse Button** - Standard "Parcourir..." button (max 100px width)
4. **Move Button** - 📦 emoji + "Déplacer" text
5. **Open Folder Button** - 📂 emoji + "Ouvrir le dossier" text

---

## 💻 Code Template

### Complete Implementation

```python
# === FOLDER NAME ===
folder_group = QGroupBox("📁 " + lang.get("folder_group_title", 
                                         default="Folder Name"))
folder_layout = QFormLayout()

# Path edit (read-only)
self.folder_path_edit = QLineEdit()
self.folder_path_edit.setText(config.get("folder_config_key") or get_default_path())
self.folder_path_edit.setReadOnly(True)
self.folder_path_edit.setCursorPosition(0)

# Browse button
browse_folder_button = QPushButton(lang.get("browse_button", default="Parcourir..."))
browse_folder_button.clicked.connect(self._browse_folder_path)
browse_folder_button.setMaximumWidth(100)

# Move button
move_folder_button = QPushButton("📦 " + lang.get("move_folder_button", default="Déplacer"))
move_folder_button.clicked.connect(lambda: self._move_folder(
    self.folder_path_edit, 
    "folder_config_key", 
    lang.get("folder_label")
))
move_folder_button.setToolTip(lang.get("move_folder_tooltip", 
                                      default="Déplacer le dossier et son contenu vers un nouvel emplacement"))

# Open folder button
open_folder_button = QPushButton("📂 " + lang.get("open_folder_button", default="Ouvrir le dossier"))
open_folder_button.clicked.connect(self._open_folder_path)

# Layout assembly
folder_path_layout = QHBoxLayout()
folder_path_layout.addWidget(self.folder_path_edit)
folder_path_layout.addWidget(browse_folder_button)
folder_path_layout.addWidget(move_folder_button)
folder_path_layout.addWidget(open_folder_button)

folder_layout.addRow(lang.get("folder_path_label", default="Dossier") + " :", folder_path_layout)

folder_group.setLayout(folder_layout)
layout.addWidget(folder_group)
```

### Required Helper Methods

```python
def _browse_folder_path(self):
    """Browse for folder path"""
    from PySide6.QtWidgets import QFileDialog
    folder = QFileDialog.getExistingDirectory(
        self,
        lang.get("select_folder_dialog_title", default="Sélectionner le dossier")
    )
    if folder:
        self.folder_path_edit.setText(folder)
        self.folder_path_edit.setCursorPosition(0)

def _open_folder_path(self):
    """Open folder in file explorer"""
    import subprocess
    folder_path = self.folder_path_edit.text()
    if os.path.exists(folder_path):
        subprocess.Popen(f'explorer "{folder_path}"')
```

---

## 🎯 Naming Conventions

### Widget Names

| Component | Pattern | Example |
|-----------|---------|---------|
| QLineEdit | `self.{type}_path_edit` | `self.character_path_edit` |
| Browse Button | `browse_{type}_button` | `browse_character_button` |
| Move Button | `move_{type}_button` | `move_character_button` |
| Open Button | `open_{type}_folder_button` | `open_character_folder_button` |

### Method Names

| Method | Pattern | Example |
|--------|---------|---------|
| Browse | `_browse_{type}_folder` | `_browse_character_folder` |
| Open | `_open_{type}_folder` | `_open_character_folder` |

### Config Keys

| Type | Pattern | Example |
|------|---------|---------|
| Standard | `{type}_folder` | `character_folder` |
| Backup | `backup_path` or `{type}_backup_path` | `cookies_backup_path` |

---

## 🔧 Fixed Folder Names

When using `_move_folder()`, folder names are **predefined** and **not user-editable**:

```python
folder_names = {
    "character_folder": "Characters",
    "armor_folder": "Armor",
    "log_folder": "Logs",
    "cookies_folder": "Cookies",
    "backup_path": "Backups",          # Special: /Backups/Characters/
    "cookies_backup_path": "Backups"   # Special: /Backups/Cookies/
}
```

### Backup Folder Special Handling

Backup folders maintain a specific structure:

```
Standard folders:
  <parent>/Characters/
  <parent>/Armor/

Backup folders:
  <parent>/Backups/Characters/  ← Intermediate /Backups/ folder
  <parent>/Backups/Cookies/     ← Intermediate /Backups/ folder
```

---

## 🌍 Required Translations

### Language Keys

Add to `Language/*.json`:

```json
{
    "folder_group_title": "Folder Title",
    "folder_path_label": "Folder path",
    "browse_button": "Browse...",
    "move_folder_button": "Move",
    "open_folder_button": "Open folder",
    "move_folder_tooltip": "Move or create this folder to a new location",
    "select_folder_dialog_title": "Select folder"
}
```

### Standard Translations

**French** (fr.json):
- `"browse_button": "Parcourir..."`
- `"move_folder_button": "Déplacer"`
- `"open_folder_button": "Ouvrir le dossier"`

**English** (en.json):
- `"browse_button": "Browse..."`
- `"move_folder_button": "Move"`
- `"open_folder_button": "Open folder"`

**German** (de.json):
- `"browse_button": "Durchsuchen..."`
- `"move_folder_button": "Verschieben"`
- `"open_folder_button": "Ordner öffnen"`

---

## 📐 Layout Guidelines

### Spacing

- **Group spacing**: `layout.addSpacing(20)` between major sections
- **Form spacing**: `layout.addSpacing(10)` within groups
- **Button spacing**: Natural spacing in QHBoxLayout (no manual spacing needed)

### Widget Properties

```python
# Path edit
self.folder_path_edit.setReadOnly(True)        # Always read-only
self.folder_path_edit.setCursorPosition(0)     # Show start of path

# Browse button
browse_button.setMaximumWidth(100)             # Consistent width

# Tooltips
move_button.setToolTip(lang.get("move_folder_tooltip"))
```

---

## ✅ Checklist for New Folder Component

- [ ] QGroupBox with emoji + translated title
- [ ] QLineEdit (read-only, cursor at position 0)
- [ ] Browse button (max 100px, connected to browse method)
- [ ] Move button (📦 emoji, connected to `_move_folder()`)
- [ ] Open button (📂 emoji, connected to open method)
- [ ] All buttons in QHBoxLayout
- [ ] Browse method implemented
- [ ] Open method implemented
- [ ] Config key defined in `folder_names` dict (if using move)
- [ ] All translation keys added to 3 language files
- [ ] Tooltip added to Move button

---

## 🔍 Example Implementations

### Example 1: Character Folder

```python
# === CHARACTERS FOLDER ===
char_group = QGroupBox("📁 " + lang.get("config_path_label", 
                                       default="Répertoire des personnages"))
char_layout = QFormLayout()

self.char_path_edit = QLineEdit()
self.char_path_edit.setText(config.get("character_folder") or get_character_dir())
self.char_path_edit.setReadOnly(True)
self.char_path_edit.setCursorPosition(0)

browse_char_button = QPushButton(lang.get("browse_button"))
browse_char_button.clicked.connect(self._browse_character_folder)
browse_char_button.setMaximumWidth(100)

move_char_button = QPushButton("📦 " + lang.get("move_folder_button"))
move_char_button.clicked.connect(lambda: self._move_folder(
    self.char_path_edit, "character_folder", lang.get("config_path_label")
))
move_char_button.setToolTip(lang.get("move_folder_tooltip"))

open_char_folder_button = QPushButton("📂 " + lang.get("open_folder_button"))
open_char_folder_button.clicked.connect(self._open_character_folder)

char_path_layout = QHBoxLayout()
char_path_layout.addWidget(self.char_path_edit)
char_path_layout.addWidget(browse_char_button)
char_path_layout.addWidget(move_char_button)
char_path_layout.addWidget(open_char_folder_button)

char_layout.addRow(lang.get("config_path_label") + " :", char_path_layout)
char_group.setLayout(char_layout)
layout.addWidget(char_group)
```

### Example 2: Backup Folder (Special)

```python
# === CHARACTERS BACKUP ===
backup_group = QGroupBox("💾 " + lang.get("backup_characters_title", 
                                         default="Sauvegardes des personnages"))
backup_layout = QVBoxLayout()

# Enable + Compress checkboxes (side by side)
enable_compress_layout = QHBoxLayout()
self.backup_enabled_check = QCheckBox(lang.get("backup_enabled_label"))
enable_compress_layout.addWidget(self.backup_enabled_check)
enable_compress_layout.addSpacing(30)
self.backup_compress_check = QCheckBox(lang.get("backup_compress_label"))
enable_compress_layout.addWidget(self.backup_compress_check)
enable_compress_layout.addStretch()
backup_layout.addLayout(enable_compress_layout)
backup_layout.addSpacing(10)

# Path with buttons
path_form = QFormLayout()
self.backup_path_edit = QLineEdit()
backup_path = config.get("backup_path")
if not backup_path:
    backup_path = os.path.join(get_base_path(), "Backups", "Characters")
self.backup_path_edit.setText(backup_path)
self.backup_path_edit.setReadOnly(True)
self.backup_path_edit.setCursorPosition(0)

browse_backup_button = QPushButton(lang.get("browse_button"))
browse_backup_button.clicked.connect(self._browse_backup_path)
browse_backup_button.setMaximumWidth(100)

move_backup_button = QPushButton("📦 " + lang.get("move_folder_button"))
move_backup_button.clicked.connect(lambda: self._move_folder(
    self.backup_path_edit, "backup_path", lang.get("backup_path_label")
))

open_backup_folder_button = QPushButton("📂 " + lang.get("open_folder_button"))
open_backup_folder_button.clicked.connect(self._open_backup_folder)

backup_path_layout = QHBoxLayout()
backup_path_layout.addWidget(self.backup_path_edit)
backup_path_layout.addWidget(browse_backup_button)
backup_path_layout.addWidget(move_backup_button)
backup_path_layout.addWidget(open_backup_folder_button)

path_form.addRow(lang.get("backup_path_label") + " :", backup_path_layout)
backup_layout.addLayout(path_form)

# Statistics (side by side)
info_layout = QHBoxLayout()
total_label = QLabel(lang.get("backup_total_label") + " :")
self.backup_total_label = QLabel("0")
self.backup_total_label.setStyleSheet("font-weight: bold; color: #0078D4;")
info_layout.addWidget(total_label)
info_layout.addWidget(self.backup_total_label)
info_layout.addSpacing(30)
last_label = QLabel(lang.get("backup_last_label") + " :")
self.backup_last_label = QLabel("N/A")
self.backup_last_label.setStyleSheet("font-weight: bold; color: #0078D4;")
info_layout.addWidget(last_label)
info_layout.addWidget(self.backup_last_label)
info_layout.addStretch()
backup_layout.addLayout(info_layout)

backup_group.setLayout(backup_layout)
layout.addWidget(backup_group)
```

---

## 🚫 Anti-Patterns

### ❌ Don't Do This

```python
# Don't: Hard-coded text
button = QPushButton("Parcourir...")

# Don't: Missing read-only
self.path_edit = QLineEdit()

# Don't: No cursor position reset
self.path_edit.setText(path)

# Don't: Different button order
layout.addWidget(open_button)
layout.addWidget(move_button)
layout.addWidget(browse_button)

# Don't: User-editable folder names
folder_name, ok = QInputDialog.getText(...)

# Don't: Missing emoji
group = QGroupBox(lang.get("title"))

# Don't: Inconsistent styling
button.setStyleSheet("background-color: red;")
```

### ✅ Do This Instead

```python
# Do: Translation keys with defaults
button = QPushButton(lang.get("browse_button", default="Parcourir..."))

# Do: Read-only with cursor reset
self.path_edit = QLineEdit()
self.path_edit.setReadOnly(True)
self.path_edit.setText(path)
self.path_edit.setCursorPosition(0)

# Do: Consistent button order
layout.addWidget(browse_button)
layout.addWidget(move_button)
layout.addWidget(open_button)

# Do: Fixed folder names
folder_name = folder_names.get(config_key, "Data")

# Do: Emoji + translated title
group = QGroupBox("📁 " + lang.get("title", default="Folder"))

# Do: No custom styling (use default theme)
button = QPushButton(text)
```

---

## 📝 Notes

1. **No Custom Styles**: Buttons use default theme colors (except special action buttons like "Backup Now")
2. **Consistent Order**: Always Browse → Move → Open
3. **Read-Only Paths**: Path QLineEdit is always read-only
4. **Emoji Usage**: Use appropriate emojis for visual consistency
5. **Translation Defaults**: Always provide English defaults in `lang.get()`
6. **Fixed Names**: Folder names are predefined in `_move_folder()` - no user input
7. **Backup Special Case**: Backup folders always use `/Backups/` intermediate folder

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-15 | Initial template with current standards |

---

## 📚 Related Documentation

- `FOLDER_MOVE_SYSTEM_EN.md` - Detailed folder move system documentation
- `BACKUP_INTEGRATION_EN.md` - Backup system integration guide
- `SETTINGS_ARCHITECTURE_EN.md` - Overall settings architecture

---

**Template Author**: Development Team  
**Last Updated**: 2025-11-15  
**Status**: ✅ Active Standard
