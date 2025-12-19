# 💬 Dialog System - Technical Documentation

**Version**: 2.2  
**Date**: November 2025  
**Last Updated**: December 19, 2025  
**Component**: `UI/progress_dialog_base.py`, `UI/dialogs.py`, `UI/ui_message_helper.py`, `UI/ui_file_dialogs.py`  
**Related**: `UI/settings_dialog.py`, `UI/armory_import_dialog.py`, `UI/failed_items_review_dialog.py`, `UI/template_import_dialog.py`, `Functions/character_actions_manager.py`  

---

## Table of Contents

1. [Overview](#overview)
2. [Message Helper System](#message-helper-system)
3. [State Management System](#state-management-system)
4. [Validation Helper System](#validation-helper-system)
5. [File Dialog Wrapper System](#file-dialog-wrapper-system)
6. [Progress Dialog System](#progress-dialog-system)
7. [ProgressStep Class](#progressstep-class)
8. [StepConfiguration Class](#stepconfiguration-class)
9. [ProgressStepsDialog Class](#progressstepsdialog-class)
10. [Worker Thread Pattern](#worker-thread-pattern)
11. [Thread Safety Patterns](#thread-safety-patterns)
12. [Implemented Dialogs](#implemented-dialogs)
13. [Multilingual Support](#multilingual-support)
14. [Performance Considerations](#performance-considerations)

---

## Overview

The Dialog System provides a unified, thread-safe, translatable framework for all long-running operations in the DAOC Character Manager. It consists of two main subsystems:

1. **Progress Dialog System** - Visual step tracking for asynchronous operations
2. **Thread Safety Patterns** - Security guidelines for QThread-based operations

### Key Features

- ✅ **Visual consistency** across all operations
- ✅ **Thread safety** by design (5 patterns)
- ✅ **Multilingual support** (FR/EN/DE)
- ✅ **Reusable configurations** for common operations
- ✅ **Guaranteed resource cleanup**
- ✅ **User-friendly progress tracking**

---

## Message Helper System

### Phase 12: UI Message Helper Extraction

**Module**: `UI/ui_message_helper.py` (v0.109 Phase 12)  
**Purpose**: Centralize and standardize all QMessageBox calls across the application  
**Status**: ✅ COMPLETE - 5 helper functions extracted

### Design Philosophy

**Problem**: 40+ repetitive `QMessageBox` calls scattered throughout `dialogs.py` and `character_actions_manager.py`  
**Solution**: Extract common patterns into reusable helpers with automatic translation and logging  
**Benefit**: Single source of truth for message display, consistency, easier maintenance

### Functions Provided

#### 1. `msg_show_success(parent, title_key, message_key, **kwargs)`
Displays a success message with `QMessageBox.information()`

```python
msg_show_success(
    self,
    "titles.success",
    "character_sheet.messages.info_update_success"
)
```

- Automatically translates title and message via `lang.get()`
- Supports dynamic parameters: `msg_show_success(..., level="10", rp=5000)`
- Logs success event

#### 2. `msg_show_error(parent, title_key, message_key, **kwargs)`
Displays an error message with `QMessageBox.critical()`

```python
msg_show_error(
    self,
    "titles.error",
    "character_sheet.messages.save_error",
    error="File not found"
)
```

- Supports plain text errors with "!" prefix: `msg_show_error(..., "!Plain text error")`
- Automatically logs ERROR action
- Uses default: "An error occurred"

#### 3. `msg_show_warning(parent, title_key, message_key, **kwargs)`
Displays a warning message with `QMessageBox.warning()`

```python
msg_show_warning(
    self,
    "titles.warning",
    "messages.errors.char_name_empty"
)
```

- Supports plain text warnings with "!" prefix: `msg_show_warning(..., "!Name cannot be empty")`
- Automatically logs WARNING action
- Uses default: "Warning"

#### 4. `msg_show_confirmation(parent, title, message) -> bool`
Displays a yes/no dialog and returns user's choice

```python
if msg_show_confirmation(self, "Delete Character?", "Are you sure?"):
    # User clicked Yes
    delete_character()
```

- Returns `True` if user clicked Yes, `False` otherwise
- Default button is "No" for safety
- Both parameters are plain text (not translated)

#### 5. `msg_show_info_with_details(parent, title_key, details_text)`
Displays informational message with formatted multi-line text

```python
msg_show_info_with_details(
    self,
    "stats_update_title",
    "Tower Captures: 100\nKeep Captures: 50\nRelic Captures: 25"
)
```

- Useful for displaying complex results with multiple stats
- `details_text` is plain text with newlines
- Supports HTML formatting if needed

### Translation Support

All functions use `lang.get()` for automatic translation:

| Key Pattern | Type | Example |
|---|---|---|
| `titles.success` | System title | ✅ Success |
| `titles.error` | System title | ❌ Error |
| `titles.warning` | System title | ⚠️ Warning |
| `messages.errors.*` | Messages | "Character name cannot be empty" |
| `!Plain text` | Plain text (no translation) | Direct text bypass |

### Plain Text Mode

When you need to pass dynamic or non-translated text, use the "!" prefix:

```python
# Translated key
msg_show_error(self, "titles.error", "messages.errors.char_name_empty")

# Plain text (for dynamic content)
msg_show_error(self, "titles.error", f"!Failed to save: {error_msg}")
```

### Logging Integration

All helpers automatically log their messages:

```python
msg_show_success(...)     # Logs: logger_ui.info(...)
msg_show_error(...)       # Logs: log_with_action(..., "error", ..., action="ERROR")
msg_show_warning(...)     # Logs: log_with_action(..., "warning", ..., action="WARNING")
msg_show_confirmation(...) # No logging (user choice)
msg_show_info_with_details(...) # Logs: logger_ui.info(...)
```

### Usage Examples

#### Example 1: Rename Character Validation
```python
# In character_actions_manager.py
if not new_name:
    msg_show_warning(
        self.main_window,
        "titles.warning",
        "messages.errors.char_name_empty"
    )
    return
```

#### Example 2: Save Error with Context
```python
from Functions.character_manager import save_character
success, msg = save_character(data)

if not success:
    msg_show_error(
        self,
        "titles.error",
        f"!Failed to save character: {msg}"
    )
```

#### Example 3: Destructive Action Confirmation
```python
if msg_show_confirmation(
    self,
    "Delete Armor File?",
    f"Are you sure you want to delete '{filename}'?\nThis cannot be undone."
):
    delete_armor_file(filename)
```

### Quality Standards

✅ **PEP 8 Compliant**
- Proper indentation, spacing, line length
- Type hints on all functions
- Comprehensive docstrings

✅ **No Hardcoded Text**
- All UI strings use `lang.get()`
- Supports dynamic parameters via `**kwargs`
- Plain text mode with "!" prefix for special cases

✅ **100% English Documentation**
- All docstrings in English
- All comments in English
- Module docstring with usage examples

✅ **Complete Error Handling**
- Graceful fallback with defaults
- Logging on all message displays
- Safe defaults (No button by default in confirmations)

### Integration Points

**Files Using Message Helper**:
- `UI/dialogs.py` - CharacterSheetWindow (3 replacements)
- `Functions/character_actions_manager.py` - rename_selected_character() (2 replacements)

**Future Expansions**:
- Phase 13: UI State Manager
- Phase 14: UI Validation Helper
- Phase 15: UI File Dialog Wrapper

---

## State Management System

### Phase 13: UI State Manager Extraction

**Module**: `UI/ui_state_manager.py` (v0.109 Phase 13)  
**Purpose**: Centralize button and UI element state management  
**Status**: ✅ COMPLETE - 5 state management functions extracted

### Design Philosophy

**Problem**: 20+ scattered `.setEnabled()` calls across dialogs.py, making state dependencies unclear

**Solution**: Extract common state patterns into reusable functions with clear intent and dependencies

**Benefit**: Single source of truth for button states, easier to test, reduced complexity

### Functions Provided

#### 1. `ui_state_set_herald_buttons(parent, character_selected, herald_url, scraping_active, validation_active)`
Manages Herald update button states based on character and scraping status.

```python
ui_state_set_herald_buttons(
    self,
    character_selected=True,
    herald_url="https://herald.daocplayers.com/...",
    scraping_active=False,
    validation_active=False
)
```

**Buttons Controlled**:
- `update_herald_button`
- `open_herald_button`
- `update_rvr_button`

**State Logic**:
- Enabled if: character selected AND herald URL provided AND no operations active
- Disabled if: no character OR no URL OR scraping/validation active

#### 2. `ui_state_set_armor_buttons(parent, character_selected, file_selected, items_without_price, db_manager=None)`
Manages armor preview and search button states with database mode validation.

```python
ui_state_set_armor_buttons(
    self,
    character_selected=True,
    file_selected=True,
    items_without_price=True,
    db_manager=self.db_manager
)
```

**Parameters**:
- `parent`: Parent widget containing armor buttons
- `character_selected`: True if character selected
- `file_selected`: True if armor file loaded
- `items_without_price`: True if items missing prices
- `db_manager`: ItemsDatabaseManager instance (optional) - validates database mode

**Buttons Controlled**:
- `preview_download_button`
- `search_prices_button`

**State Logic**:
- preview_download_button: enabled if character selected AND file loaded
- search_prices_button: enabled if file loaded AND items without prices AND personal database active
- If database is embedded (read-only), search button disabled with tooltip: "Enable personal database in Settings/Armory to add/update item prices."

#### 3. `ui_state_set_stats_buttons(parent, character_selected, has_stats, scraping_active)`
Manages character stats update button states.

```python
ui_state_set_stats_buttons(
    self,
    character_selected=True,
    has_stats=True,
    scraping_active=False
)
```

**State Logic**:
- Buttons enabled if: character selected AND has stats AND no scraping active
- Buttons disabled during active scraping operations

#### 4. `ui_state_set_dialog_buttons(parent, button_states)`
Generic button state controller for setting multiple button states at once.

```python
ui_state_set_dialog_buttons(self, {
    "delete_button": has_selection,
    "edit_button": has_selection,
    "save_button": is_valid_input,
    "cancel_button": True
})
```

**Parameters**:
- `button_states`: Dictionary mapping button names to enabled state (bool)

**Usage**: When multiple buttons need state updates in one call

#### 5. `ui_state_on_selection_changed(parent, selection_count, is_valid, enable_delete, enable_edit, enable_export)`
Unified handler for UI state changes when selection changes.

```python
ui_state_on_selection_changed(
    self,
    selection_count=1,
    is_valid=True,
    enable_delete=True,
    enable_edit=True,
    enable_export=False
)
```

**Buttons Controlled** (if present):
- `delete_button`
- `edit_button`
- `export_button`

**State Logic**:
- Delete: enabled if selection_count > 0 AND valid AND enable_delete
- Edit: enabled if selection_count == 1 AND valid AND enable_edit
- Export: enabled if selection_count > 0 AND valid AND enable_export

### State Management Patterns

| Pattern | Function | Use Case |
|---------|----------|----------|
| **Herald Operations** | `ui_state_set_herald_buttons()` | Enable/disable during character updates |
| **File Operations** | `ui_state_set_armor_buttons()` | Manage preview/search buttons |
| **Multi-Button Updates** | `ui_state_set_dialog_buttons()` | Generic state controller |
| **Selection-Based States** | `ui_state_on_selection_changed()` | Handle list/table selection changes |
| **Async Operations** | `ui_state_set_stats_buttons()` | Disable during scraping |

### Integration Examples

#### Example 1: Herald Validation Complete
```python
def _on_herald_validation_finished(self, accessible, message):
    """Called when Herald validation completes"""
    herald_url = self.character_data.get('url', '').strip()
    ui_state_set_herald_buttons(
        self,
        character_selected=True,
        herald_url=herald_url,
        scraping_active=False,
        validation_active=False
    )
```

#### Example 2: File Selected in Armor Dialog
```python
def on_selection_changed(self):
    """Updates buttons when file is selected"""
    if not selected_items:
        ui_state_set_armor_buttons(
            self,
            character_selected=False,
            file_selected=False,
            items_without_price=False
        )
        return
    
    ui_state_set_armor_buttons(
        self,
        character_selected=True,
        file_selected=True,
        items_without_price=has_items_without_price
    )
```

#### Example 3: List Selection Changed
```python
def on_item_selection_changed(self):
    """Handle cookie list selection"""
    has_selection = bool(self.cookie_list.selectedItems())
    ui_state_on_selection_changed(
        self,
        selection_count=1 if has_selection else 0,
        is_valid=has_selection,
        enable_delete=True
    )
```

### Quality Standards

✅ **PEP 8 Compliant**
- Proper naming: `ui_state_{component}_{action}()`
- Type hints on all parameters
- Comprehensive docstrings

✅ **Logging Integration**
- All state changes logged at DEBUG level
- Includes state reason in log message
- Button name validation with warnings

✅ **Safe Attributes**
- Uses `hasattr()` to check for button existence
- Won't crash if button not found in parent
- Gracefully logs missing buttons

✅ **Reusable**
- No hardcoded button names (except patterns)
- Flexible boolean parameters
- Easy to extend for new buttons

### Performance Considerations

**State Updates**: O(n) where n = number of buttons affected (typically 1-4)

**Logging Overhead**: Minimal (DEBUG level, conditional)

**Memory Usage**: Negligible (no state caching, direct attribute access)

**Best Practice**: Call state managers immediately after state change, not pre-emptively

---

## Validation Helper System

### Phase 14: UI Validation Helper Extraction

**Module**: `Functions/ui_validation_helper.py` (v0.109 Phase 14)  
**Purpose**: Centralize input field validation across dialogs  
**File Size**: 480 lines (pure utility module)  
**Functions**: 15 validators covering text, URLs, numbers, files, and domain-specific validations

#### Overview

Centralized validation module to:
- Eliminate 20+ repetitive validation patterns in dialogs.py
- Ensure consistent error messages (all in French)
- Support complex validations (file paths, URLs, DAOC-specific fields)
- Provide type-safe returns with structured dict format

#### Design Pattern: Functional Validation

**Features**:
- All functions are stateless (no side effects)
- All functions return consistent dict format: `{'valid': bool, 'message': str, 'value': Any}`
- No raising exceptions - errors returned in dict
- All messages are French (appropriate for user-facing validation)

**Naming Convention**: `validate_{field_type}_{constraint}`
- `validate_non_empty_text()` - basic text field
- `validate_character_name()` - domain-specific character name
- `validate_url_field()` - specialized Herald URLs
- `validate_filepath_exists()` - file system operations

#### Function Categories

**1. Basic Text Validation** (3 functions)
- `validate_non_empty_text()` - Check field not empty
- `validate_text_field()` - Validate with max_length constraint
- `validate_email_field()` - Validate email format

**2. Domain-Specific (DAOC) Validation** (5 functions)
- `validate_character_name()` - Character names (max 30 chars)
- `validate_guild_name()` - Guild names (optional, max 50 chars)
- `validate_realm_selection()` - Realm selected (Albion/Hibernia/Midgard)
- `validate_class_selection()` - Class selected
- `validate_race_selection()` - Race selected

**3. Specialized Validation** (5 functions)
- `validate_url_field()` - Herald URLs (must contain 'herald', http/https)
- `validate_numeric_field()` - Integer ranges with min/max
- `validate_filepath_exists()` - File path exists
- `validate_directory_exists()` - Directory exists
- `validate_email_field()` - Email format validation

**4. Selection Validation** (2 functions)
- `validate_not_selected()` - Combo box not empty
- `validate_multiple_selections()` - List has minimum items

#### Return Format (Standardized)

All functions return:
```python
{
    'valid': bool,           # True if validation passed
    'message': str,          # Error message (French) if invalid, empty if valid
    'value': Any             # Converted/cleaned value if valid, fallback if invalid
}
```

**Value Types**:
- Text functions: `str` (stripped)
- Numeric functions: `int` (0 if invalid)
- File functions: `str` (absolute path or empty)
- Selection functions: `str` or `bool` or `list`

#### Integration in dialogs.py (3 locations)

1. **`save_basic_info()` (line ~920)**
   - Calls `validate_basic_character_info()` with guild and Herald URL
   - Single validation call replaces separate guild + URL validations
   - Receives `{'valid', 'message', 'guild', 'url'}` dict

2. **`rename_character()` (line ~1650)**
   - Calls `validate_character_rename()` with new character name
   - Simple wrapper around `validate_character_name()`
   - Uses `msg_show_warning()` for error display

3. **`get_data()` in NewCharacterDialog (line ~1890)**
   - Calls `validate_new_character_dialog_data()` with character name and guild
   - Handles both character name (required) and guild (optional) validation
   - Uses `QMessageBox.warning()` for errors
   - Returns validated name and guild directly

**All validation logic is in Functions/ui_validation_helper.py - dialogs.py only calls the validators**

#### Usage Pattern

```python
# Basic pattern
result = validate_character_name(self.name_edit.text())
if not result['valid']:
    QMessageBox.critical(self, "Erreur", result['message'])
    return
name = result['value']  # Safe to use - already validated
```

#### Validation Patterns

**Pattern 1: Required Field**
```python
result = validate_non_empty_text(self.name_edit.text())
if not result['valid']: return show_error(result['message'])
name = result['value']
```

**Pattern 2: Optional Field**
```python
result = validate_guild_name(self.guild_edit.text())  # Empty allowed
guild = result['value']  # May be empty string
```

**Pattern 3: Conditional Validation**
```python
url_text = self.herald_url_edit.text()
if url_text.strip():  # Only validate if provided
    result = validate_url_field(url_text)
    if not result['valid']: return show_error(result['message'])
    url = result['value']
```

#### Performance Notes

**O(n) complexity** where n = input length
- Text field validations: <1ms
- File operations: ~10-100ms (filesystem access)
- Regex validations: <1ms
- **Optimization**: Validate on blur event, not on every keystroke

#### Error Handling

**Defensive Programming**:
- No exceptions raised
- Errors returned in 'message' field
- Always return dict (never None)
- Graceful degradation for edge cases

**File Operations**:
- Catch exceptions (permission errors, invalid paths)
- Log errors with `logging.error()`
- Return user-friendly error messages

#### Testing Results

✅ All 15 functions tested and working
✅ 3 wrapper functions tested and working
✅ Application starts correctly with new module
✅ Validation chain tested:
  - Valid inputs return `valid=True` with proper value
  - Invalid inputs return `valid=False` with error message
  - Error messages are French and appropriate
  - Wrapper functions combine multiple validations correctly

#### Wrapper Functions Reference

**validate_basic_character_info(character_name: str, guild_name: str, herald_url: str) -> dict**

Validates all basic character information fields together.

Parameters:
  character_name: Character name (not used, for future compatibility)
  guild_name: Guild name to validate (optional field)
  herald_url: Herald URL to validate (optional field)

Returns:
  {
    'valid': bool,           # False if any field invalid
    'message': str,          # Error message if invalid
    'guild': str             # Validated guild (empty if invalid)
    'url': str               # Validated URL (empty if invalid)
  }

Behavior:
  - Validates guild first using `validate_guild_name()`
  - If guild invalid: returns early with error message
  - Validates Herald URL if provided
  - Returns both validated values on success

---

**validate_character_rename(new_name: str) -> dict**

Validates character name for rename operation.

Wrapper around `validate_character_name()` for clarity.

Parameters:
  new_name: New character name

Returns:
  {
    'valid': bool,      # False if name invalid
    'message': str,     # Error message if invalid
    'value': str        # Validated name if valid
  }

---

**validate_new_character_creation(character_name: str) -> dict**

Validates character name for new character creation.

Wrapper around `validate_character_name()` for clarity.

Parameters:
  character_name: Character name to validate

Returns:
  {
    'valid': bool,      # False if name invalid
    'message': str,     # Error message if invalid
    'value': str        # Validated name if valid
  }

---

**validate_new_character_dialog_data(character_name: str, guild_name: str) -> dict**

Validates all fields for new character dialog (character name and optional guild).

Parameters:
  character_name: Character name to validate (required)
  guild_name: Guild name to validate (optional)

Returns:
  {
    'valid': bool,      # False if any field invalid
    'message': str,     # Error message if invalid
    'name': str         # Validated character name
    'guild': str        # Validated guild (empty if not provided)
  }

Behavior:
  - Validates character name first using `validate_character_name()`
  - If character name invalid: returns early with error message
  - Then validates guild name using `validate_guild_name()` (optional field)
  - Returns both validated and stripped values on success

Usage in `NewCharacterDialog.get_data()`:
  ```python
  result = validate_new_character_dialog_data(
      self.name_edit.text(),
      self.guild_edit.text()
  )
  if not result['valid']:
      QMessageBox.warning(self, lang.get("error_title"), result['message'])
      return None
  name = result['name']      # Already validated and stripped
  guild = result['guild']    # Already validated and stripped
  ```

#### Migration from Old Code

**Before** (scattered validation):
```python
new_name = self.name_edit.text().strip()
if not new_name:
    msg_show_warning(self, "titles.warning", "char_name_empty")
    return
```

**After** (centralized):
```python
result = validate_character_name(self.name_edit.text())
if not result['valid']:
    msg_show_warning(self, "titles.warning", result['message'])
    return
new_name = result['value']
```

**Benefits**:
- Single place to update validation rules
- Consistent error messages across all dialogs
- Reduced code duplication (~25 lines eliminated)
- Easier to test and maintain

#### Wrapper Functions (Dialog-Specific)

Three wrapper functions encapsulate validation for specific dialog use cases:

**1. `validate_basic_character_info(character_name, guild_name, herald_url)`**
- Purpose: Validate all basic info fields together
- Returns: `{'valid': bool, 'message': str, 'guild': str, 'url': str}`
- Used in: `CharacterSheetWindow.save_basic_info()`
- Example:
  ```python
  result = validate_basic_character_info("", self.guild_edit.text(), self.herald_url_edit.text())
  if not result['valid']:
      QMessageBox.critical(self, "Erreur", result['message'])
      return
  new_guild = result['guild']
  herald_url = result['url']
  ```

**2. `validate_character_rename(new_name)`**
- Purpose: Validate character name for rename operation
- Returns: `{'valid': bool, 'message': str, 'value': str}`
- Used in: `CharacterSheetWindow.rename_character()`
- Wrapper for `validate_character_name()` for clarity

**3. `validate_new_character_creation(character_name)`**
- Purpose: Validate character name for new character dialog
- Returns: `{'valid': bool, 'message': str, 'value': str}`
- Used in: `NewCharacterDialog.get_data()` (legacy, deprecated)
- Wrapper for `validate_character_name()` for clarity

**4. `validate_new_character_dialog_data(character_name, guild_name)`**
- Purpose: Validate both character name and guild for new character dialog
- Returns: `{'valid': bool, 'message': str, 'name': str, 'guild': str}`
- Used in: `NewCharacterDialog.get_data()`
- Combines `validate_character_name()` + `validate_guild_name()`
- Example:
  ```python
  # In NewCharacterDialog.get_data()
  name_text = self.character_name_edit.text()
  guild_text = self.guild_edit.text()
  result = validate_new_character_dialog_data(name_text, guild_text)
  
  if not result['valid']:
      QMessageBox.critical(self, "Erreur", result['message'])
      return
  character_name = result['name']
  guild = result['guild']
  ```

**Architecture**: dialogs.py contains ONLY UI calls to validation functions. All validation logic is in Functions/ui_validation_helper.py.

---

## File Dialog Wrapper System

### Phase 15: UI File Dialog Wrapper Extraction

**Module**: `UI/ui_file_dialogs.py` (v0.109 Phase 15)  
**Purpose**: Centralize QFileDialog usage for consistent file selection behavior  
**Status**: ✅ COMPLETE - 5 file dialog wrapper functions extracted

### Design Philosophy

**Problem**: 5 scattered `QFileDialog` calls in dialogs.py with repeated setup code

**Solution**: Extract common patterns into reusable wrappers with automatic translation

**Benefit**: Single source of truth for file dialogs, consistency, reduced code duplication

### Functions Provided

#### 1. `dialog_open_file(parent, title_key, filter_key="", initial_dir="")`

Opens file selection dialog.

```python
file_path = dialog_open_file(
    self,
    title_key="cookie_manager.browse_dialog_title",
    filter_key="cookie_manager.browse_dialog_filter",
    initial_dir=""
)
```

**Parameters**:
- `parent`: Parent widget
- `title_key`: Translation key for dialog title
- `filter_key`: Translation key for file filter (optional)
- `initial_dir`: Initial directory path (optional)

**Returns**: Selected file path, empty string if cancelled

**Used in**: `CookieManagerDialog.browse_cookie_file()`

---

#### 2. `dialog_save_file(parent, title_key, default_filename="", filter_key="")`

Opens save file dialog.

```python
save_path = dialog_save_file(
    self,
    title_key="armoury_dialog.dialogs.download_file",
    default_filename=filename,
    filter_key="armoury_dialog.dialogs.all_files"
)
```

**Parameters**:
- `parent`: Parent widget
- `title_key`: Translation key for dialog title
- `default_filename`: Default filename (suggestion)
- `filter_key`: Translation key for file filter (optional)

**Returns**: Selected save path, empty string if cancelled

**Used in**: `ArmorManagementDialog.download_file()`

---

#### 3. `dialog_select_directory(parent, title_key, initial_dir="")`

Opens directory selection dialog.

```python
directory = dialog_select_directory(
    self,
    title_key="select_folder_dialog_title",
    initial_dir=""
)
```

**Parameters**:
- `parent`: Parent widget
- `title_key`: Translation key for dialog title
- `initial_dir`: Initial directory path (optional)

**Returns**: Selected directory path, empty string if cancelled

**Used in**: `SettingsDialog.browse_folder()` (generic for character/config folders)

---

#### 4. `dialog_open_armor_file(parent)`

Opens armor file selection dialog (wrapper).

```python
file_path = dialog_open_armor_file(self)
if file_path:
    # Process armor file
```

**Parameters**:
- `parent`: Parent widget

**Returns**: Selected file path, empty string if cancelled

**Used in**: Armor template file selection workflows

---

#### 5. `dialog_select_backup_path(parent, current_path="")`

Opens backup directory selection dialog (wrapper).

```python
backup_path = dialog_select_backup_path(self, current_path)
if backup_path:
    # Use backup path
```

**Parameters**:
- `parent`: Parent widget
- `current_path`: Current path (used as initial directory)

**Returns**: Selected directory path, empty string if cancelled

**Used in**: 
- `BackupSettingsDialog.browse_backup_path()`
- `BackupSettingsDialog.browse_cookies_backup_path()`

### Integration Points (dialogs.py - 5 locations)

| Location | Method | Wrapper Used |
|----------|--------|--------------|
| Line ~2251 | `browse_folder()` | `dialog_select_directory()` |
| Line ~2771 | `download_file()` | `dialog_save_file()` |
| Line ~3238 | `browse_cookie_file()` | `dialog_open_file()` |
| Line ~6059 | `browse_backup_path()` | `dialog_select_backup_path()` |
| Line ~6071 | `browse_cookies_backup_path()` | `dialog_select_backup_path()` |

### Benefits

✅ **Consistency**: All file dialogs follow same pattern  
✅ **Translation**: Automatic via `lang.get()`  
✅ **Maintainability**: Single place to modify dialog behavior  
✅ **Code Reduction**: ~20 lines eliminated from dialogs.py  
✅ **Reusability**: Easy to add new file dialog patterns  

### Quality Standards

✅ **PEP 8 Compliant**
- Proper indentation and spacing
- Type hints on all parameters
- Comprehensive docstrings

✅ **No Hardcoded Text**
- All titles/filters use translation keys
- Automatic `lang.get()` integration

✅ **100% English Documentation**
- All docstrings in English
- All comments in English

---

## Progress Dialog System

### Design Philosophy

**Purpose**: Replace blocking progress dialogs with unified, thread-safe, visual step tracking  
**Consistency**: All long-running operations share same visual language  
**Separation of Concerns**: UI (Dialog) + Business Logic (Worker Thread) + Configuration (StepConfiguration)

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    PROGRESS DIALOG SYSTEM                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐      ┌─────────────────┐                   │
│  │  ProgressStep  │      │ StepConfiguration│                   │
│  ├────────────────┤      ├─────────────────┤                   │
│  │ • icon: str    │◄─────┤ HERALD_CONNECTION│ (3 steps)        │
│  │ • text: str    │      │ SCRAPER_INIT     │ (1 step)         │
│  │ • conditional  │      │ HERALD_SEARCH    │ (5 steps)        │
│  │ • category     │      │ STATS_SCRAPING   │ (5 steps)        │
│  │ • state: enum  │      │ CHARACTER_UPDATE │ (8 steps)        │
│  └────────────────┘      │ COOKIE_GENERATION│ (6 steps)        │
│         │                │ CLEANUP          │ (1 step)         │
│         │                └─────────────────┘                   │
│         ▼                         │                             │
│  ┌──────────────────────────┐    │                             │
│  │  ProgressStepsDialog     │◄───┘                             │
│  ├──────────────────────────┤                                  │
│  │ • Title + Description    │                                  │
│  │ • Scrollable step list   │    ┌──────────────────┐         │
│  │ • Progress bar           │◄───┤  Worker Thread   │         │
│  │ • Status message         │    ├──────────────────┤         │
│  │ • Thread-safe updates    │    │ • step_started   │ Signal  │
│  └──────────────────────────┘    │ • step_completed │ Signal  │
│                                   │ • step_error     │ Signal  │
│                                   │ • finished       │ Signal  │
│                                   │ • _stop_requested│ Flag    │
│                                   │ • cleanup_*()    │ Method  │
│                                   └──────────────────┘         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## ProgressStep Class

### Class Overview

**Name**: `ProgressStep`  
**Location**: `UI/progress_dialog_base.py` (line ~29)  
**Purpose**: Represents a single step in a multi-step operation  
**Category**: Data model with state management

### Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `icon` | `str` | Emoji representing the step | `"🔐"`, `"🌐"`, `"🍪"` |
| `text` | `str` | Translation key or display text | `"step_herald_connection_cookies"` |
| `conditional` | `bool` | Can this step be skipped? | `True` for achievements |
| `category` | `str` | Step category | `"connection"`, `"scraping"`, `"processing"` |
| `state` | `StepState` | Current state (enum) | `PENDING`, `RUNNING`, `COMPLETED`, `SKIPPED`, `ERROR` |

### Step States

```python
class StepState(str, Enum):
    PENDING = "pending"      # ⏺️ Not started yet
    RUNNING = "running"      # ⏳ Currently executing
    COMPLETED = "completed"  # ✅ Successfully finished
    SKIPPED = "skipped"      # ⏭️ Skipped (conditional step)
    ERROR = "error"          # ❌ Failed with error
```

### State Transition Diagram

```
                    ┌─────────────┐
                    │   PENDING   │ ⏺️
                    │  (Initial)  │
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         start_step()          skip_step()
                │                     │
                ▼                     ▼
        ┌──────────────┐      ┌─────────────┐
        │   RUNNING    │ ⏳    │   SKIPPED   │ ⏭️
        └──────┬───────┘      └─────────────┘
               │                    (Final)
       ┌───────┴────────┐
       │                │
  complete_step()  error_step()
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  COMPLETED  │ ✅│    ERROR    │ ❌
└─────────────┘  └─────────────┘
   (Final)           (Final)
```

### Display Methods

#### `get_display_icon() → str`

Returns emoji based on current state:

| State | Icon | Visual |
|-------|------|--------|
| `PENDING` | `"⏺️"` | Grey circle |
| `RUNNING` | `"⏳"` | Hourglass |
| `COMPLETED` | `"✅"` | Green checkmark |
| `SKIPPED` | `"⏭️"` | Fast-forward |
| `ERROR` | `"❌"` | Red X |

#### `get_display_color() → str`

Returns hex color for UI styling:

| State | Color | Hex Code | Usage |
|-------|-------|----------|-------|
| `PENDING` | Grey | `#888888` | Waiting |
| `RUNNING` | Blue | `#2196F3` | Active |
| `COMPLETED` | Green | `#4CAF50` | Success |
| `SKIPPED` | Orange | `#FF9800` | Conditional skip |
| `ERROR` | Red | `#F44336` | Failure |

---

## StepConfiguration Class

### Class Overview

**Name**: `StepConfiguration`  
**Location**: `UI/progress_dialog_base.py` (line ~152)  
**Purpose**: Provides reusable, predefined step groups for common operations  
**Category**: Configuration class (static configurations)

### Predefined Configurations

#### 1. HERALD_CONNECTION (3 steps)

**Purpose**: Standard Herald authentication flow  
**Used by**: All operations requiring authenticated Herald access

```python
HERALD_CONNECTION = [
    ProgressStep("🔐", "step_herald_connection_cookies", category="connection"),
    ProgressStep("🌐", "step_herald_connection_init", category="connection"),
    ProgressStep("🍪", "step_herald_connection_load", category="connection"),
]
```

---

#### 2. SCRAPER_INIT (1 step)

**Purpose**: Simple scraper initialization without full browser setup  
**Used by**: Stats updates (lighter than full connection)

```python
SCRAPER_INIT = [
    ProgressStep("🔌", "step_scraper_init", category="connection"),
]
```

---

#### 3. HERALD_SEARCH (5 steps)

**Purpose**: Character search on Eden Herald  
**Used by**: HeraldSearchDialog (search functionality)

```python
HERALD_SEARCH = [
    ProgressStep("🔍", "step_herald_search_search", category="scraping"),
    ProgressStep("⏳", "step_herald_search_load", category="scraping"),
    ProgressStep("📊", "step_herald_search_extract", category="scraping"),
    ProgressStep("💾", "step_herald_search_save", category="processing"),
    ProgressStep("🎯", "step_herald_search_format", category="processing"),
]
```

---

#### 4. STATS_SCRAPING (5 steps)

**Purpose**: Character statistics extraction  
**Used by**: StatsUpdateThread (RvR/PvP/PvE/Wealth/Achievements)

```python
STATS_SCRAPING = [
    ProgressStep("🏰", "step_stats_scraping_rvr", category="scraping"),
    ProgressStep("⚔️", "step_stats_scraping_pvp", category="scraping"),
    ProgressStep("🐉", "step_stats_scraping_pve", category="scraping"),
    ProgressStep("💰", "step_stats_scraping_wealth", category="scraping"),
    ProgressStep("🏆", "step_stats_scraping_achievements", 
                 conditional=True, category="scraping"),
]
```

**Note**: Step 5 is conditional because achievements may not be available for all characters.

---

#### 5. CHARACTER_UPDATE (8 steps)

**Purpose**: Complete character data update from Herald  
**Used by**: CharacterUpdateThread (2 locations: sheet dialog + context menu)

```python
CHARACTER_UPDATE = [
    ProgressStep("📝", "step_character_update_extract_name", category="connection"),
    ProgressStep("🌐", "step_character_update_init", category="connection"),
    ProgressStep("🍪", "step_character_update_load_cookies", category="connection"),
    ProgressStep("🔍", "step_character_update_navigate", category="scraping"),
    ProgressStep("⏳", "step_character_update_wait", category="scraping"),
    ProgressStep("📊", "step_character_update_extract_data", category="scraping"),
    ProgressStep("🎯", "step_character_update_format", category="processing"),
    ProgressStep("🔄", "step_character_update_close", category="cleanup"),
]
```

---

#### 6. COOKIE_GENERATION (6 steps)

**Purpose**: Generate Eden Herald authentication cookies via Discord login  
**Used by**: CookieGenThread (interactive user authentication)

```python
COOKIE_GENERATION = [
    ProgressStep("⚙️", "step_cookie_gen_config", category="setup"),
    ProgressStep("🌐", "step_cookie_gen_open", category="setup"),
    ProgressStep("👤", "step_cookie_gen_wait_user", category="interactive"),
    ProgressStep("🍪", "step_cookie_gen_extract", category="processing"),
    ProgressStep("💾", "step_cookie_gen_save", category="processing"),
    ProgressStep("✅", "step_cookie_gen_validate", category="processing"),
]
```

**Unique Feature**: Step 3 is interactive - thread waits for user to complete Discord authentication.

---

#### 7. CLEANUP (1 step)

**Purpose**: Standard browser cleanup  
**Used by**: All operations requiring browser closure

```python
CLEANUP = [
    ProgressStep("🔄", "step_cleanup", category="cleanup"),
]
```

---

### Configuration Composition

#### `build_steps(*step_groups) → List[ProgressStep]`

**Purpose**: Combine multiple step groups into a single list

**Example - Stats Update (7 steps)**:

```python
from UI.progress_dialog_base import StepConfiguration

steps = StepConfiguration.build_steps(
    StepConfiguration.SCRAPER_INIT,   # Step 0: Init scraper
    StepConfiguration.STATS_SCRAPING, # Steps 1-5: RvR, PvP, PvE, Wealth, Achievements
    StepConfiguration.CLEANUP         # Step 6: Close browser
)

# Result: 7 total steps (1 + 5 + 1)
```

---

## ProgressStepsDialog Class

### Class Overview

**Name**: `ProgressStepsDialog`  
**Location**: `UI/progress_dialog_base.py` (line ~278)  
**Purpose**: Visual progress dialog with step-by-step tracking  
**Category**: QDialog-based UI component with thread-safe update methods

### Visual Layout

```
┌─────────────────────────────────────────────────────────┐
│  📊 Updating statistics...                       [X]    │
├─────────────────────────────────────────────────────────┤
│  Retrieving RvR, PvP, PvE and Wealth statistics from    │
│  Eden Herald                                            │
├─────────────────────────────────────────────────────────┤
│  ╔═══════════════════════════════════════════════╗     │
│  ║  ✅ 🔌 Initializing Herald scraper            ║     │
│  ║  ⏳ 🏰 Retrieving RvR captures                ║     │
│  ║  ⏺️ ⚔️ Retrieving PvP stats                  ║     │
│  ║  ⏺️ 🐉 Retrieving PvE stats                  ║     │
│  ║  ⏺️ 💰 Retrieving wealth                     ║     │
│  ║  ⏺️ 🏆 Retrieving achievements               ║     │
│  ║  ⏺️ 🔄 Closing browser                       ║     │
│  ╚═══════════════════════════════════════════════╝     │
│                                                         │
│  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░  28%          │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ ⏳ Retrieving RvR captures...                 │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Thread-Safe Methods

#### `start_step(step_index: int)`

**Purpose**: Mark step as started (⏳ RUNNING state)

**Thread Safety**: ✅ Can be called from worker thread  
**Visual Update**: Icon changes to ⏳, color to blue, text to **bold**

---

#### `complete_step(step_index: int)`

**Purpose**: Mark step as completed (✅ COMPLETED state)

**Thread Safety**: ✅ Can be called from worker thread  
**Visual Update**: Icon changes to ✅, color to green, progress bar advances

---

#### `error_step(step_index: int, error_message: str)`

**Purpose**: Mark step as failed (❌ ERROR state)

**Thread Safety**: ✅ Can be called from worker thread  
**Visual Update**: Icon changes to ❌, color to red, status message shows error

---

#### `skip_step(step_index: int)`

**Purpose**: Mark conditional step as skipped (⏭️ SKIPPED state)

**Thread Safety**: ✅ Can be called from worker thread  
**Visual Update**: Icon changes to ⏭️, color to orange, text to *italic*

---

#### `set_status_message(message: str, color: str = "#2196F3")`

**Purpose**: Update status label at bottom of dialog

**Thread Safety**: ✅ Can be called from worker thread

---

## Worker Thread Pattern

### Thread Architecture

All worker threads follow the same architecture with 5 security patterns.

```
┌────────────────────────────────────────────────────────┐
│                  WORKER THREAD PATTERN                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Signals (→ Main Thread):                             │
│    ├─ step_started: Signal(int)                       │
│    ├─ step_completed: Signal(int)                     │
│    ├─ step_error: Signal(int, str)                    │
│    └─ finished: Signal(bool, data, str)               │
│                                                        │
│  Flags:                                                │
│    └─ _stop_requested: bool = False                   │
│                                                        │
│  External Resources:                                   │
│    ├─ _driver: WebDriver = None                       │
│    ├─ _scraper: Scraper = None                        │
│    └─ cleanup_external_resources()                    │
│                                                        │
│  Execution Flow:                                       │
│    1. emit step_started(i)                            │
│    2. Perform operation                               │
│    3. Check _stop_requested                           │
│    4. emit step_completed(i) OR step_error(i, msg)    │
│    5. Repeat for all steps                            │
│    6. FINALLY: cleanup + emit finished                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Thread Safety Patterns

All implemented threads follow 5 critical security patterns to ensure reliable operation and proper resource cleanup.

### Pattern 1: RuntimeError Protection

**Problem**: Accessing deleted QObject from thread causes RuntimeError  
**Solution**: Wrappers with `hasattr()` + `try/except RuntimeError`

```python
# ✅ CORRECT - Thread-safe wrapper
def _on_step_started(self, step_index):
    """Thread-safe wrapper for start_step"""
    if hasattr(self, 'progress_dialog') and self.progress_dialog:
        try:
            self.progress_dialog.start_step(step_index)
        except RuntimeError:
            pass  # Dialog already deleted
```

```python
# ❌ WRONG - Direct call from thread
self.thread.step_started.connect(self.progress_dialog.start_step)
# → RuntimeError if dialog closed early
```

**Rules**:
- ✅ **ALWAYS** use wrappers for thread → dialog signals
- ✅ **ALWAYS** check `hasattr()` AND `self.progress_dialog`
- ✅ **ALWAYS** wrap in `try/except RuntimeError`
- ❌ **NEVER** direct connection `thread.signal.connect(dialog.method)`

---

### Pattern 2: Cleanup External Resources

**Problem**: Browser stays open if thread terminated forcefully  
**Solution**: `_resource = None` + `cleanup_external_resources()` called **BEFORE** `terminate()`

```python
class StatsUpdateThread(QThread):
    def __init__(self, url):
        super().__init__()
        self._scraper = None  # ← External resource
    
    def cleanup_external_resources(self):
        """Called BEFORE terminate()"""
        if self._scraper:
            try:
                self._scraper.close()
            except:
                pass
            self._scraper = None
    
    def run(self):
        try:
            # ... work ...
        finally:
            self.cleanup_external_resources()  # Always cleanup
```

```python
# In dialog - CRITICAL ORDER
def _stop_thread(self):
    if self.thread and self.thread.isRunning():
        self.thread.request_stop()  # 1. Ask nicely
        self.thread.wait(3000)      # 2. Wait 3s
        
        if self.thread.isRunning():
            self.thread.cleanup_external_resources()  # 3. ✅ BEFORE terminate
            self.thread.terminate()                   # 4. Force stop
            self.thread.wait()
```

**Rules**:
- ✅ **ALWAYS** add `self._external_resource = None` in `__init__()`
- ✅ **ALWAYS** store: `self._external_resource = resource` after creation
- ✅ **ALWAYS** create `cleanup_external_resources()` method
- ✅ **ALWAYS** call cleanup BEFORE `terminate()` in `_stop_thread()`

---

### Pattern 3: Graceful Interruption

**Problem**: Long operations can't be stopped (e.g., 5min sleep)  
**Solution**: `_stop_requested` flag + checks + interruptible sleep

```python
class CookieGenThread(QThread):
    def __init__(self):
        super().__init__()
        self._stop_requested = False
    
    def request_stop(self):
        """Signal thread to stop gracefully"""
        self._stop_requested = True
    
    def run(self):
        # Step 2: Wait for user (up to 5 minutes)
        timeout = 300  # 5 minutes
        elapsed = 0
        
        while not self._user_confirmed and elapsed < timeout:
            if self._stop_requested:  # ✅ Check flag
                return  # Exit gracefully
            
            time.sleep(0.5)  # Interruptible sleep
            elapsed += 0.5
```

**Rules**:
- ✅ **ALWAYS** check `if self._stop_requested: return` after critical operations
- ✅ **ALWAYS** replace `time.sleep(N)` with interruptible loop
- ✅ **ALWAYS** check after network/I/O operations

---

### Pattern 4: Dialog Rejected Handling

**Problem**: User closes dialog (X button) but thread keeps running  
**Solution**: Connect `rejected` signal BEFORE `show()` + cleanup

```python
# Create dialog
self.progress_dialog = ProgressStepsDialog(...)

# Create thread
self.worker_thread = WorkerThread(...)

# Connect signals
self.worker_thread.step_started.connect(self._on_step_started)

# ✅ CRITICAL: Connect rejected BEFORE show()
self.progress_dialog.rejected.connect(self._on_dialog_closed)

# Show and start
self.progress_dialog.show()
self.worker_thread.start()
```

```python
def _on_dialog_closed(self):
    """Called when user clicks X"""
    import logging
    logging.info("Dialog closed by user - stopping thread")
    
    self._stop_thread()  # Cleanup BEFORE terminate
    
    # Re-enable UI
    self.button.setEnabled(True)
```

**Rules**:
- ✅ **ALWAYS** connect `progress_dialog.rejected` → handler
- ✅ **ALWAYS** connect BEFORE `show()` or `exec()`
- ✅ **ALWAYS** call `_stop_thread()` in handler
- ✅ **ALWAYS** re-enable UI controls in handler

---

### Pattern 5: Async Cleanup for Fast Window Closing

**Problem**: Window closing is slow (2-3 clicks needed) because `closeEvent()` blocks on thread cleanup  
**Solution**: Accept close immediately, perform cleanup asynchronously with QTimer

#### Fast Close with Async Cleanup

```python
from PySide6.QtCore import QTimer

def closeEvent(self, event):
    """Called on window close - ACCEPT IMMEDIATELY"""
    # Async cleanup without blocking close
    QTimer.singleShot(0, self._async_full_cleanup)
    
    # Call super() IMMEDIATELY to close window
    super().closeEvent(event)

def _async_full_cleanup(self):
    """Complete cleanup in background"""
    try:
        self._stop_search_thread_async()
        self._cleanup_temp_files()
    except Exception as e:
        logging.warning(f"Error during async cleanup: {e}")
```

#### Async Thread Stop (Reference Capture)

```python
def _stop_search_thread_async(self):
    """Non-blocking version of stop thread"""
    if hasattr(self, 'search_thread') and self.search_thread is not None:
        # ✅ Capture reference BEFORE async
        thread_ref = self.search_thread
        
        if thread_ref.isRunning():
            # Request graceful stop
            thread_ref.request_stop()
            
            # Disconnect signals
            try:
                thread_ref.search_finished.disconnect()
                thread_ref.step_started.disconnect()
            except:
                pass
            
            # Async thread cleanup
            def _async_thread_cleanup():
                try:
                    if thread_ref and thread_ref.isRunning():
                        # Short wait (100ms instead of 3000ms)
                        thread_ref.wait(100)
                        
                        if thread_ref.isRunning():
                            logging.warning("Thread active - forced cleanup")
                            try:
                                thread_ref.cleanup_driver()
                                thread_ref.terminate()
                                thread_ref.wait()
                            except:
                                pass
                except Exception as e:
                    logging.warning(f"Error async thread cleanup: {e}")
            
            # Execute after 50ms (non-blocking)
            QTimer.singleShot(50, _async_thread_cleanup)
        
        # Clean reference immediately
        self.search_thread = None
```

#### Heavy Operations as Async (Refresh + Backup)

```python
def _import_characters(self, characters):
    """Import characters from Herald"""
    # ... import code ...
    
    # Show result immediately
    QMessageBox.information(self, "Import complete", message)
    
    # ✅ Async UI refresh (non-blocking)
    if hasattr(self.parent(), 'tree_manager'):
        QTimer.singleShot(100, self.parent().tree_manager.refresh_character_list)
    
    # ✅ Async backup (non-blocking)
    parent_app = self.parent()
    if hasattr(parent_app, 'backup_manager'):
        def _async_backup():
            try:
                logging.info("[BACKUP] Starting async backup")
                parent_app.backup_manager.backup_characters_force(
                    reason="Update", 
                    character_name="multi"
                )
            except Exception as e:
                logging.warning(f"[BACKUP] Error async backup: {e}")
        
        QTimer.singleShot(200, _async_backup)
```

**Pattern 5 Rules**:

#### ✅ TO DO
- Always call `super().closeEvent(event)` **IMMEDIATELY**
- Use `QTimer.singleShot(0, ...)` for background cleanup
- **Capture references** (thread, dialog) before lambda/inner function
- Reduce timeouts (100ms instead of 3000ms)
- Wrap all I/O operations in try/except

#### ❌ TO AVOID
- `thread.wait(3000)` in closeEvent (blocks 3 seconds!)
- `event.accept()` without calling `super().closeEvent()`
- Using `self.thread` in lambda (can be None/destroyed)
- Synchronous heavy operations (UI refresh, backup) after MessageBox
- Forgetting signal disconnection before async cleanup

**Expected Results**:
- ✅ Instant close on 1st click (< 100ms)
- ✅ No freeze after character import
- ✅ Complete background cleanup without blocking user
- ✅ No RuntimeError or orphaned resources

---

## Implemented Dialogs

### Stats Update Dialog

**Location**: `UI/dialogs.py` - `CharacterSheetDialog.update_rvr_stats()`  
**Thread**: `StatsUpdateThread` (7 steps)  
**Configuration**: SCRAPER_INIT + STATS_SCRAPING + CLEANUP

#### Step Breakdown

| # | Icon | Translation Key | Category | Duration |
|---|------|-----------------|----------|----------|
| 0 | 🔌 | `step_scraper_init` | connection | ~1s |
| 1 | 🏰 | `step_stats_scraping_rvr` | scraping | ~4s |
| 2 | ⚔️ | `step_stats_scraping_pvp` | scraping | ~4s |
| 3 | 🐉 | `step_stats_scraping_pve` | scraping | ~4s |
| 4 | 💰 | `step_stats_scraping_wealth` | scraping | ~3s |
| 5 | 🏆 | `step_stats_scraping_achievements` | scraping | ~3s (conditional) |
| 6 | 🔄 | `step_cleanup` | cleanup | ~1s |

**Total Duration**: ~20-24 seconds

---

### Character Update Dialog

**Locations**: 
1. `UI/dialogs.py` - `CharacterSheetDialog.update_from_herald()` (from character sheet)
2. `main.py` - `CharacterApp.update_character_from_herald()` (from context menu)

**Thread**: `CharacterUpdateThread` (8 steps)  
**Configuration**: CHARACTER_UPDATE

#### Step Breakdown

| # | Icon | Translation Key | Category | Duration |
|---|------|-----------------|----------|----------|
| 0 | 📝 | `step_character_update_extract_name` | connection | <1s |
| 1 | 🌐 | `step_character_update_init` | connection | ~2s |
| 2 | 🍪 | `step_character_update_load_cookies` | connection | ~1s |
| 3 | 🔍 | `step_character_update_navigate` | scraping | ~2s |
| 4 | ⏳ | `step_character_update_wait` | scraping | ~3s |
| 5 | 📊 | `step_character_update_extract_data` | scraping | ~2s |
| 6 | 🎯 | `step_character_update_format` | processing | ~1s |
| 7 | 🔄 | `step_character_update_close` | cleanup | ~1s |

**Total Duration**: ~12-15 seconds

---

### Cookie Generation Dialog

**Location**: `UI/dialogs.py` - `CookieManagerDialog.generate_cookies()`  
**Thread**: `CookieGenThread` (6 steps)  
**Configuration**: COOKIE_GENERATION

#### Step Breakdown

| # | Icon | Translation Key | Category | Duration | Interactive |
|---|------|-----------------|----------|----------|-------------|
| 0 | ⚙️ | `step_cookie_gen_config` | setup | ~1s | ❌ No |
| 1 | 🌐 | `step_cookie_gen_open` | setup | ~3s | ❌ No |
| 2 | 👤 | `step_cookie_gen_wait_user` | interactive | 30s-5min | ✅ **YES** |
| 3 | 🍪 | `step_cookie_gen_extract` | processing | ~1s | ❌ No |
| 4 | 💾 | `step_cookie_gen_save` | processing | ~1s | ❌ No |
| 5 | ✅ | `step_cookie_gen_validate` | processing | ~1s | ❌ No |

**Total Duration**: 35 seconds - 5 minutes (depends on user login speed)

**Unique Features**:
- Interactive step (Step 2) - waits for user Discord authentication
- `allow_cancel=True` - only dialog with cancel button
- Interruptible sleep with timeout

---

## Multilingual Support

### Translation System

All step texts use translation keys from `Language/*.json` files.

**Supported Languages**:
- 🇫🇷 French (`fr.json`)
- 🇬🇧 English (`en.json`)
- 🇩🇪 German (`de.json`)

### Translation Keys Structure

#### Step Descriptions (35 keys)

```json
{
  "step_herald_connection_cookies": "Checking authentication cookies",
  "step_herald_connection_init": "Initializing Chrome browser",
  "step_herald_connection_load": "Loading cookies into browser",
  "step_scraper_init": "Initializing Herald scraper",
  "step_herald_search_search": "Searching on Eden Herald",
  "step_stats_scraping_rvr": "Retrieving RvR captures",
  "step_stats_scraping_pvp": "Retrieving PvP stats",
  "step_character_update_extract_name": "Extracting character name",
  "step_cookie_gen_config": "Configuring browser",
  "step_cleanup": "Closing browser"
}
```

#### Dialog Titles & Descriptions (8 keys)

```json
{
  "progress_stats_update_title": "📊 Updating statistics...",
  "progress_stats_update_desc": "Retrieving RvR, PvP, PvE and Wealth statistics from Eden Herald",
  "progress_character_update_title": "🌐 Updating from Herald...",
  "progress_cookie_gen_title": "🍪 Generating cookies..."
}
```

---

## Performance Considerations

### Typical Execution Times

| Dialog | Steps | Avg Duration | Notes |
|--------|-------|--------------|-------|
| Stats Update | 7 | 20-24s | Conditional achievements step |
| Character Update | 8 | 12-15s | Browser initialization overhead |
| Cookie Generation | 6 | 35s-5min | **Depends on user login speed** |

### Performance Factors

**Network Speed**:
- Herald page load: 2-4s
- Data extraction: 1-2s per stat category

**Browser Initialization**:
- Chrome startup: 1-2s
- Cookie loading: 1s

**User Interaction** (Cookie Gen only):
- Discord login: 10s-2min (typical)
- Timeout: 5min (max)

---

## Validation Checklist

### ✅ Pattern 1 (RuntimeError)
- [ ] All thread → dialog signals go through wrappers
- [ ] Each wrapper checks `hasattr()` AND `self.progress_dialog`
- [ ] Each wrapper wrapped in `try/except RuntimeError`

### ✅ Pattern 2 (Cleanup Resources)
- [ ] Thread has `cleanup_external_resources()` public method
- [ ] Cleanup called BEFORE `terminate()` from main thread
- [ ] Attribute `_external_resource` to store reference

### ✅ Pattern 3 (Interruption)
- [ ] Thread has `_stop_requested = False` flag
- [ ] `request_stop()` method to request stop
- [ ] Long loops check `if self._stop_requested: return`
- [ ] Sleep replaced with 0.5s loops with verification

### ✅ Pattern 4 (Dialog Rejected)
- [ ] `rejected` signal connected BEFORE `show()` or `exec()`
- [ ] Handler calls `_stop_thread()` then re-enables controls
- [ ] No resource leaks if dialog closed prematurely

### ✅ Pattern 5 (Async Cleanup)
- [ ] `closeEvent()` calls `super().closeEvent(event)` IMMEDIATELY
- [ ] Cleanup via `QTimer.singleShot(0, self._async_full_cleanup)`
- [ ] Thread/dialog references captured before lambda/inner function
- [ ] Timeouts reduced (100ms instead of 3000ms)
- [ ] Heavy I/O operations (refresh, backup) via QTimer after MessageBox

---

## Migration Summary

### Before Migration

```python
# ❌ BLOCKING - UI freezes
def update_stats(self):
    progress = QProgressDialog("Updating...", None, 0, 0, self)
    progress.show()
    
    # BLOCKS UI for 20+ seconds
    stats = scraper.scrape_all()
    
    progress.close()
    QMessageBox.information(self, "Success", "Stats updated")
```

**Problems**:
- UI frozen during operation
- No detailed progress
- No cancellation
- Browser stays open on crash
- No error recovery
- Not translatable

### After Migration

```python
# ✅ ASYNC - UI responsive
def update_stats(self):
    steps = StepConfiguration.build_steps(
        StepConfiguration.SCRAPER_INIT,
        StepConfiguration.STATS_SCRAPING,
        StepConfiguration.CLEANUP
    )
    
    self.progress_dialog = ProgressStepsDialog(
        parent=self,
        title=lang.get("progress_stats_update_title"),
        steps=steps,
        show_progress_bar=True,
        determinate_progress=True
    )
    
    self.thread = StatsUpdateThread(url)
    self.thread.step_started.connect(self._on_step_started)
    self.thread.step_completed.connect(self._on_step_completed)
    
    self.progress_dialog.rejected.connect(self._on_canceled)
    
    self.progress_dialog.show()
    self.thread.start()
```

**Benefits**:
- ✅ UI responsive (can resize, minimize)
- ✅ Detailed step-by-step progress
- ✅ Cancellation support
- ✅ Guaranteed browser cleanup
- ✅ Error recovery per step
- ✅ Fully translatable (FR/EN/DE)
- ✅ Visual consistency across app
- ✅ Thread-safe by design

---

## Statistics

**Total Components**: 4 classes  
**Total Configurations**: 7 predefined step groups  
**Total Steps Defined**: 29 unique steps  
**Worker Threads**: 4 implementations  
**Dialogs Migrated**: 4 (from blocking to async)  
**Languages Supported**: 3 (FR/EN/DE)  
**Translation Keys**: 52 total (35 steps + 8 dialogs + 5 status + 4 errors)  
**Security Patterns**: 5 applied to all threads  
**Code Reduction**: ~300 lines eliminated (connection duplication)

---

## Related Documentation

- [Armory System](../Armory/ARMORY_TECHNICAL_DOCUMENTATION.md) - Template and mass import
- [Items Database](../Items/ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md) - Database editor
- [Backup System](../Backups/BACKUP_TECHNICAL_DOCUMENTATION.md) - Backup management

---

**End of Documentation**
