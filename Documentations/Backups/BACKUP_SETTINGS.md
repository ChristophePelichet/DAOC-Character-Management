# Backup System - Settings Reference

## Overview

This document provides a complete reference for all backup-related settings available in the application.

## Settings Location

**Path**: Configuration Menu → Settings → Backups Tab

## Characters Backup Settings

### Enable Backups

| Property | Value |
|----------|-------|
| **Control** | Checkbox |
| **Label** | "Enable backups" |
| **Default** | `True` (checked) |
| **Config Key** | `backup_enabled` |

**Description**: Master switch for character backups. When disabled, no automatic backups are created.

**Effect**:
- ✅ **Enabled**: Backup created on first startup each day
- ❌ **Disabled**: No backups created (existing backups preserved)

**Use Cases**:
- Disable temporarily for testing
- Disable if managing backups externally

---

### Compress Backups

| Property | Value |
|----------|-------|
| **Control** | Checkbox |
| **Label** | "Compress backups (ZIP)" |
| **Default** | `True` (checked) |
| **Config Key** | `backup_compress` |
| **Tooltip** | "Reduces backup size" |

**Description**: Determines backup format.

**Effect**:
- ✅ **Enabled**: Creates `.zip` files (compressed)
- ❌ **Disabled**: Creates folder copies (uncompressed)

**Size Comparison**:
| Characters | Compressed | Uncompressed |
|------------|-----------|--------------|
| 5 | ~500 KB | ~1.5 MB |
| 10 | ~1 MB | ~3 MB |
| 20 | ~2 MB | ~6 MB |

**Recommendation**: Keep enabled unless you need direct file access.

---

### Auto-Delete Old Backups

| Property | Value |
|----------|-------|
| **Control** | Checkbox |
| **Label** | "Auto-delete old backups" |
| **Default** | `True` (checked) |
| **Config Key** | `backup_auto_delete_old` |
| **Tooltip** | "Automatically delete oldest backups when limit is reached" |

**Description**: Controls automatic retention policy.

**Effect**:
- ✅ **Enabled**: Oldest backups deleted when storage limit exceeded
- ❌ **Disabled**: All backups kept (manual cleanup required)

**Warning Dialog**: When unchecking, shows warning:
```
⚠️ Warning

WARNING: Disabling automatic deletion may cause:

• Disk space saturation
• Future backups failure
• Need to manually manage old backups

Do you really want to disable this protection?

[Yes] [No]
```

**Behavior with Storage Limit**:
- If limit = 20 MB and auto-delete enabled:
  - System keeps backups until total reaches 20 MB
  - Then removes oldest to make room for new ones
- If limit = 20 MB and auto-delete disabled:
  - Backups accumulate beyond 20 MB
  - No automatic deletion

**Recommendation**: Keep enabled unless you have specific backup retention requirements.

---

### Storage Limit

| Property | Value |
|----------|-------|
| **Control** | Text input field |
| **Label** | "Storage limit:" |
| **Unit** | MB (megabytes) |
| **Default** | `20` |
| **Range** | `-1` or `1-999` |
| **Config Key** | `backup_size_limit_mb` |
| **Tooltip** | "(-1 = unlimited)" |

**Description**: Maximum total size for all backups combined.

**Special Values**:
| Value | Meaning |
|-------|---------|
| `-1` | Unlimited (no size limit) |
| `0` | Invalid (uses default 20) |
| `1-999` | Limit in megabytes |

**Behavior**:
- System calculates total size of all backups
- If total > limit and auto-delete enabled:
  - Removes oldest backups until under limit
- If total > limit and auto-delete disabled:
  - No action (backups kept, warning in logs)

**Automatic Behavior with -1**:
- When user types `-1` in field
- Auto-delete checkbox **automatically unchecks** (without warning)
- Reason: Unlimited storage means no deletion needed

**Recommended Values**:
| Use Case | Suggested Limit |
|----------|----------------|
| 1-5 characters | 20 MB |
| 5-10 characters | 30-50 MB |
| 10-20 characters | 50-100 MB |
| 20+ characters | 100-200 MB |
| Archive/testing | -1 (unlimited) |

---

### Backup Path

| Property | Value |
|----------|-------|
| **Control** | Read-only text field + buttons |
| **Label** | "Backup folder:" |
| **Default** | `<app_folder>/Backups/Characters/` |
| **Config Key** | `backup_path` |

**Description**: Location where character backups are stored.

**Buttons**:
- **Browse**: Select new location (updates path only, doesn't move files)
- **📦 Move**: Relocate entire folder with contents
- **📂 Open**: Open folder in Windows Explorer

**Folder Structure**:
- System automatically creates `/Backups/` intermediate folder
- Example: If you select `D:\MyData\`, actual path becomes `D:\MyData\Backups\Characters\`

**Moving Backups**:
1. Click **📦 Move**
2. Select new parent directory
3. System:
   - Creates `Backups/Characters/` structure
   - Moves all existing backups
   - Updates configuration
   - Shows progress dialog if large

---

### Statistics Display

| Property | Value |
|----------|-------|
| **Control** | Read-only labels |
| **Updates** | On settings dialog open |

**Displayed Information**:

**Number of backups**: `8`
- Total count of backup files in folder
- Updates when settings opened

**Last backup**: `2025-11-15 14:30:22`
- Timestamp of most recent backup
- Format: YYYY-MM-DD HH:MM:SS
- Source: `backup_last_date` config key

**Layout**:
```
[Limit: 20 MB] [(-1 = unlimited)] [☑ Auto-delete] | [Number: 8] | [Last: 2025-11-15 14:30:22]
```

---

## Cookies Backup Settings

All settings mirror Characters backup settings with separate configuration:

### Enable Cookies Backups

| Property | Value |
|----------|-------|
| **Control** | Checkbox |
| **Default** | `True` |
| **Config Key** | `cookies_backup_enabled` |

### Compress Cookies Backups

| Property | Value |
|----------|-------|
| **Control** | Checkbox |
| **Default** | `True` |
| **Config Key** | `cookies_backup_compress` |

### Auto-Delete Old Cookies Backups

| Property | Value |
|----------|-------|
| **Control** | Checkbox |
| **Default** | `True` |
| **Config Key** | `cookies_backup_auto_delete_old` |

### Cookies Storage Limit

| Property | Value |
|----------|-------|
| **Control** | Text input |
| **Default** | `20` MB |
| **Config Key** | `cookies_backup_size_limit_mb` |

**Note**: Cookies backups contain only `eden_cookies.pkl` file (~10-50 KB each), not the entire Eden folder.

### Cookies Backup Path

| Property | Value |
|----------|-------|
| **Default** | `<app_folder>/Backups/Cookies/` |
| **Config Key** | `cookies_backup_path` |

**Backup Content**:
- ✅ **Included**: `eden_cookies.pkl` (cookies file only)
- ❌ **Excluded**: ChromeProfile folder (not backed up)
- **Reason**: Chrome profile can be regenerated, cookies cannot

**File Formats**:
- **Compressed**: `backup_cookies_YYYYMMDD_HHMMSS_Reason.zip` (contains eden_cookies.pkl)
- **Uncompressed**: `backup_cookies_YYYYMMDD_HHMMSS_Reason.pkl` (direct copy)

---

## Configuration File

Settings are stored in `Configuration/config.json`:

```json
{
  "backup_enabled": true,
  "backup_compress": true,
  "backup_auto_delete_old": true,
  "backup_size_limit_mb": 20,
  "backup_path": "D:\\...\\Backups\\Characters",
  "backup_last_date": "2025-11-15T14:30:22",
  
  "cookies_backup_enabled": true,
  "cookies_backup_compress": true,
  "cookies_backup_auto_delete_old": true,
  "cookies_backup_size_limit_mb": 20,
  "cookies_backup_path": "D:\\...\\Backups\\Cookies",
  "cookies_backup_last_date": "2025-11-15T14:30:22"
}
```

## Event Handling

### Auto-Delete Checkbox

**Event**: `stateChanged`  
**Handler**: `_on_backup_auto_delete_changed()` / `_on_cookies_auto_delete_changed()`

**Logic**:
```python
if state == 0:  # Unchecked
    show_warning_dialog()
    if user_clicks_no:
        recheck_checkbox()  # Cancel uncheck
```

### Storage Limit Field

**Event**: `textChanged`  
**Handler**: `_on_backup_limit_changed()` / `_on_cookies_limit_changed()`

**Logic**:
```python
if text == "-1":
    auto_delete_checkbox.setChecked(False)  # No warning
```

## Validation

### On Save

When user clicks **Save** button:

1. **Storage limits** parsed as integers:
   ```python
   try:
       size_limit = int(dialog.backup_size_limit_edit.text())
       config.set("backup_size_limit_mb", size_limit)
   except ValueError:
       # Keep existing value if invalid input
       pass
   ```

2. **All checkboxes** saved:
   ```python
   config.set("backup_enabled", checkbox.isChecked())
   ```

3. **Paths** saved:
   ```python
   config.set("backup_path", line_edit.text())
   ```

### Input Restrictions

**Storage Limit Field**:
- Accepts: Numbers (0-9), minus sign (-)
- No letters or special characters (enforced by input validation)
- Invalid input: Keeps previous value

## UI Behavior

### Initialization

On dialog open:
1. Load values from config
2. Set checkbox states
3. Set text field values
4. Calculate and display statistics

### Real-Time Updates

**Statistics**:
- Calculated when settings dialog opens
- Not updated live during dialog session
- Refresh by closing and reopening dialog

**Warning Dialogs**:
- Modal (blocks settings dialog)
- Must be acknowledged
- Can cancel action

## Troubleshooting Settings

### Setting Not Saved

**Symptoms**:
- Changed setting reverts after restart

**Causes**:
1. Config file read-only
2. Application crash before save
3. Invalid input (for numeric fields)

**Solutions**:
- Check config.json file permissions
- Ensure valid input format
- Check logs for save errors

### Auto-Delete Not Working

**Checklist**:
- ☑ `backup_auto_delete_old` = `true`
- ☑ `backup_size_limit_mb` > 0 (not -1)
- ☑ Total backup size > limit
- ☑ Multiple backups exist

### Path Not Updating

**If using Browse**:
- Updates config immediately
- Doesn't move existing files

**If using Move**:
- Moves files and updates config
- Check logs if move fails

## Related Documentation

- [User Guide](BACKUP_USER_GUIDE.md) - How to use backups
- [Technical Architecture](BACKUP_ARCHITECTURE.md) - Internal implementation
- [Retention Policy](BACKUP_RETENTION_POLICY.md) - Deletion algorithm
