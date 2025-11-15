# Backup System - User Guide

**Version**: 2.1  
**Last Updated**: 2025-11-15

## Introduction

This guide helps you understand and use the automatic backup system to protect your character data and Eden cookies with **smart folder creation** that only creates backup folders when actually needed.

## What is Backed Up?

### Characters Backup
- **All character files** in your Characters folder
- **Configuration files** associated with characters
- **Timestamps** preserved for restoration

### Cookies Backup
- **Eden session cookies** for automatic login
- **Browser credentials** for Herald import
- **Separate backup** from characters

### Armor Backup (v2.1)
- **Armor resistance data** (armor_resists.json)
- **Custom armor configurations**
- **Separate backup** from characters

## How It Works

### Automatic Daily Backup

The system creates backups **automatically** on the first application startup of each day:

1. **Application starts**
2. **System checks** last backup date
3. **If new day** → Creates backup automatically
4. **If same day** → Skips (already backed up)

**Example**:
```
Monday 08:00   → Backup created ✓
Monday 14:30   → Skipped (already done today)
Monday 20:00   → Skipped (already done today)
Tuesday 09:15  → New backup created ✓
```

### Smart Folder Creation (v2.1)

**NEW BEHAVIOR**: Backup folders are **NOT created on startup** anymore.

**Old Behavior** (v0.108 and earlier):
```
Application Launch
    ↓
Backup/Characters/ folder created (even if empty)
Backup/Cookies/ folder created (even if empty)
Backup/Armor/ folder created (even if empty)
    ↓
Result: Empty folders cluttering your directory
```

**New Behavior** (v2.1+):
```
Application Launch
    ↓
NO folders created
    ↓
First Backup Execution
    ↓
Check if source exists (Characters/, eden_cookies.pkl, armor_resists.json)
    ├─ Source exists: Create backup folder + perform backup
    └─ Source missing: Skip (no folder created)
```

**Benefits**:
- ✅ No empty folders on first launch
- ✅ Cleaner directory structure
- ✅ Folders appear only when actually used
- ✅ Automatic cleanup when moving backups

**Example Timeline**:
```
Day 1, 08:00 - Fresh Install
    → No backup folders exist yet

Day 1, 10:00 - Add first character
    → Characters/ folder created with character data
    
Day 2, 08:00 - Application startup
    → Characters/ exists → Backup/Characters/ created
    → Backup performed: backup_characters_20251102_080000.zip
    
Day 2, 09:00 - Configure cookies
    → eden_cookies.pkl created
    
Day 3, 08:00 - Application startup
    → Characters/ exists → Backup/Characters/ already exists
    → eden_cookies.pkl exists → Backup/Cookies/ created
    → Two backups performed
```

### Backup Naming

Backups use a standardized naming format:
```
backup_characters_YYYYMMDD_HHMMSS.zip
backup_cookies_YYYYMMDD_HHMMSS.zip
backup_armor_YYYYMMDD_HHMMSS.zip
```

**Example**:
- `backup_characters_20251115_143022.zip`
  - Date: 2025-11-15
  - Time: 14:30:22

## Configuration

### Accessing Settings

1. Click **Configuration** menu
2. Select **Settings**
3. Go to **Backups** tab

### Basic Settings

#### Enable Backups
- **Checkbox**: ☑ Enable backups
- **Default**: Enabled
- **Effect**: Turns automatic backup on/off

#### Compress Backups
- **Checkbox**: ☑ Compress backups (ZIP)
- **Default**: Enabled
- **Effect**: 
  - ✅ Enabled → Creates ZIP files (smaller)
  - ❌ Disabled → Creates folder copies (larger)

**Recommendation**: Keep compression enabled to save disk space.

#### Auto-Delete Old Backups
- **Checkbox**: ☑ Auto-delete old backups
- **Default**: Enabled
- **Effect**:
  - ✅ Enabled → Automatically removes oldest backups when limit reached
  - ❌ Disabled → Keeps all backups (manual cleanup required)

**⚠️ Warning**: Disabling auto-delete can cause:
- Disk space saturation
- Backup failures
- Need for manual cleanup

#### Storage Limit
- **Field**: Limit (MB)
- **Default**: 20 MB
- **Range**: 1-999 MB or -1 (unlimited)
- **Effect**: Maximum total size for all backups

**Common values**:
| Value | Suitable For |
|-------|-------------|
| 20 MB | 1-5 characters, moderate usage |
| 50 MB | 5-15 characters, regular usage |
| 100 MB | 15+ characters, heavy usage |
| -1 | Unlimited (⚠️ use with caution) |

### Advanced Settings

#### Backup Folder Location

**Default locations**:
- Characters: `<app_folder>/Backups/Characters/`
- Cookies: `<app_folder>/Backups/Cookies/`

**Changing location**:
1. Click **📦 Move** button
2. Select new parent folder
3. System moves all existing backups
4. Configuration updated automatically

**Opening folder**:
- Click **📂 Open Folder** to view backups in Explorer

## Using Backups

### Viewing Statistics

In Settings → Backups, you can see:

**Storage Limit**: 20 MB (-1 = unlimited)  
**☑ Auto-delete old backups**  
**|** Number of backups: **8** **|** Last backup: **2025-11-15 14:30:22**

### Manual Verification

1. Click **📂 Open Folder**
2. Check backup files:
   ```
   backup_characters_20251115_143022.zip (512 KB)
   backup_characters_20251114_091505.zip (498 KB)
   backup_characters_20251113_085432.zip (503 KB)
   ```
3. Verify dates match your expectations

### Restoring a Backup

#### Full Restoration

1. **Locate backup file** (click 📂 Open Folder)
2. **Close application**
3. **Extract ZIP** to temporary folder (if compressed)
4. **Replace** entire Characters folder with backup content
5. **Restart application**

#### Selective Restoration

1. **Open backup** (extract if ZIP)
2. **Find specific character** file (e.g., `MyChar_Albion.json`)
3. **Copy** to Characters folder
4. **Restart application**

**⚠️ Important**: Always close the application before modifying character files.

## Best Practices

### Recommended Settings

For most users:
```
☑ Enable backups
☑ Compress backups (ZIP)
☑ Auto-delete old backups
Storage limit: 20-50 MB
```

### Backup Frequency

- **Daily backups** are sufficient for normal use
- System prevents multiple backups per day
- No manual intervention needed

### Storage Management

**If using auto-delete**:
- System manages space automatically
- Oldest backups removed when limit reached
- No manual cleanup needed

**If NOT using auto-delete**:
- Monitor disk space regularly
- Manually delete old backups monthly
- Keep at least 3-5 recent backups

### External Backups

**Recommended**:
1. Periodically copy backup folder to:
   - External USB drive
   - Network storage (NAS)
   - Cloud storage (Dropbox, OneDrive, etc.)
2. Keep off-site backup for disaster recovery

## Troubleshooting

### Backup Not Creating

**Symptoms**:
- No new backup file today
- Last backup date is old

**Solutions**:
1. Check Settings → Backups → ☑ Enable backups
2. Verify disk space available (needs 2x character folder size)
3. Check logs (Settings → Debug) for error messages
4. Ensure application has write permissions

### Backups Too Large

**Symptoms**:
- Backup files are very large
- Storage limit reached quickly

**Solutions**:
- ✅ Enable ZIP compression
- Clean up unused characters
- Increase storage limit
- Check for large log files in character folders

### Cannot Restore Backup

**Symptoms**:
- Extracted files don't work
- Characters not appearing

**Solutions**:
1. Ensure application is **closed** during restore
2. Verify backup file is **not corrupted** (can be extracted)
3. Check file permissions after extraction
4. Restore to correct location (Characters folder)

### Too Many Backups Deleted

**Symptoms**:
- Only 1-2 backups remaining
- Wanted to keep more history

**Solutions**:
1. Increase storage limit (20 MB → 50 MB or more)
2. Enable ZIP compression (reduces backup size)
3. Temporarily disable auto-delete while building history

## FAQ

### Q: Can I disable backups completely?
**A**: Yes, uncheck "Enable backups" in Settings. Not recommended.

### Q: How much space do backups use?
**A**: Depends on character count and compression:
- 5 characters, ZIP: ~500 KB per backup
- 10 characters, ZIP: ~1 MB per backup
- Without ZIP: 2-3x larger

### Q: What happens if I delete a backup file?
**A**: Nothing immediately. You just lose that restore point. Application continues normally.

### Q: Can I have multiple backup locations?
**A**: No, only one active location. But you can manually copy backups elsewhere.

### Q: Does backup slow down startup?
**A**: Minimal impact. Backup runs in background, usually completes in 1-2 seconds.

### Q: Are backups encrypted?
**A**: No, files are stored in plain text/ZIP. Use disk encryption if security is a concern.

### Q: What if backup folder is deleted?
**A**: System recreates it automatically on next backup. No data loss for future backups.

### Q: Can I force a backup manually?
**A**: Currently no manual trigger button. Backups are automatic daily only.

## Support

If you encounter issues:

1. **Check logs**: Settings → Debug tab
2. **Verify settings**: Settings → Backups tab
3. **Test script**: Run `python Tools/test_backup_system.py`
4. **Report issue**: GitHub with logs and description

## Related Documentation

- [Settings Configuration](BACKUP_SETTINGS.md) - Detailed settings reference
- [Technical Architecture](BACKUP_ARCHITECTURE.md) - How it works internally
- [Retention Policy](BACKUP_RETENTION_POLICY.md) - Automatic deletion details
- [Test Script](../../Tools/TEST_BACKUP_README.md) - Automated testing
