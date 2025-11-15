# Backup System - Retention Policy

## Overview

This document provides detailed information about how the backup system manages storage space through automatic retention policies.

## Core Concepts

### Retention Policy

**Definition**: The automatic deletion of old backups when storage limits are reached.

**Purpose**:
- Prevent unlimited disk space consumption
- Maintain configurable number of recent backups
- Balance between backup history and storage cost

**Trigger**: Runs after each backup creation

---

## Retention Algorithm

### High-Level Flow

```
1. Create new backup
2. Update last backup timestamp
3. Check if auto-delete enabled
   ├─ NO → End (keep all backups)
   └─ YES → Continue
4. Check if storage limit set
   ├─ -1 (unlimited) → End (keep all backups)
   └─ > 0 → Continue
5. Get list of all backups, sorted oldest first
6. Calculate total size of all backups
7. While total size > limit:
   ├─ Delete oldest backup
   ├─ Remove from list
   └─ Recalculate total size
8. End (total size ≤ limit)
```

---

## Detailed Implementation

### Step 1: Check Auto-Delete Enabled

**Code**:
```python
def _apply_retention_policies(self):
    auto_delete = self.config_manager.get("backup_auto_delete_old", True)
    if not auto_delete:
        log_with_action(self.logger, "debug", 
            "Auto-delete disabled - skipping retention policy",
            action="RETENTION")
        return
```

**Logic**:
- If `backup_auto_delete_old` = `False` → **SKIP ALL RETENTION**
- User explicitly disabled auto-delete → honor their choice
- All backups kept regardless of size

**Log Example**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Auto-delete disabled - skipping retention policy
```

---

### Step 2: Check Storage Limit

**Code**:
```python
size_limit_mb = self.config_manager.get("backup_size_limit_mb", 20)
if size_limit_mb <= 0:
    log_with_action(self.logger, "debug",
        "Unlimited storage mode (-1) - skipping retention",
        action="RETENTION")
    return
```

**Logic**:
| Limit Value | Behavior |
|-------------|----------|
| `-1` | Unlimited - skip retention |
| `0` | Unlimited - skip retention |
| `1-999` | Apply retention with limit |

**Log Example**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Unlimited storage mode (-1) - skipping retention
```

---

### Step 3: Get Sorted Backups

**Code**:
```python
def _get_sorted_backups(self):
    """Get backups sorted by modification time (oldest first)."""
    backups = []
    backup_dir = self._get_backup_dir()
    
    for item in backup_dir.iterdir():
        if item.name.startswith("backup_characters_"):
            backups.append(item)
    
    # Sort by modification time (oldest first)
    return sorted(backups, key=lambda x: x.stat().st_mtime)
```

**Sorting Criteria**:
- Uses file modification time (`st_mtime`)
- **Oldest first** (important for deletion order)
- Includes both ZIP files and folders

**Example**:
```python
[
    backup_characters_20251101_083022.zip,  # Oldest
    backup_characters_20251102_084511.zip,
    backup_characters_20251103_085044.zip,
    backup_characters_20251104_090233.zip,
    backup_characters_20251105_091122.zip   # Newest
]
```

---

### Step 4: Calculate Total Size

**Code**:
```python
def _get_backup_size(self, backup_path):
    """Calculate backup size in MB."""
    if backup_path.is_file():
        # ZIP file
        return backup_path.stat().st_size / (1024 * 1024)
    elif backup_path.is_dir():
        # Folder
        total = sum(
            f.stat().st_size 
            for f in backup_path.rglob('*') 
            if f.is_file()
        )
        return total / (1024 * 1024)
    return 0

total_size_mb = sum(self._get_backup_size(b) for b in backups)
```

**Size Calculation**:
- **ZIP files**: Single file size (fast)
- **Folders**: Recursive sum of all files (slower)
- **Unit**: Megabytes (MB) with decimal precision

**Example**:
```
backup_characters_20251101_083022.zip → 1.24 MB
backup_characters_20251102_084511.zip → 1.31 MB
backup_characters_20251103_085044.zip → 1.28 MB
backup_characters_20251104_090233.zip → 1.33 MB
backup_characters_20251105_091122.zip → 1.29 MB
──────────────────────────────────────────────────
Total: 6.45 MB
```

**Log Example**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Found 5 existing backups
2025-11-15 08:00:14 | DEBUG | RETENTION | Total size: 6.45 MB
```

---

### Step 5: Delete Oldest Until Under Limit

**Code**:
```python
while total_size_mb > size_limit_mb and backups:
    oldest_backup = backups.pop(0)  # Remove first (oldest)
    
    backup_size_mb = self._get_backup_size(oldest_backup)
    
    # Delete backup
    if oldest_backup.is_file():
        oldest_backup.unlink()  # Delete file
    elif oldest_backup.is_dir():
        shutil.rmtree(oldest_backup)  # Delete folder
    
    log_with_action(self.logger, "info",
        f"Deleted old backup: {oldest_backup.name} ({backup_size_mb:.2f} MB)",
        action="RETENTION")
    
    # Recalculate total
    total_size_mb = sum(self._get_backup_size(b) for b in backups)
```

**Deletion Logic**:
1. Check if total > limit
2. If yes, remove oldest from list (index 0)
3. Delete from filesystem
4. Recalculate total size
5. Repeat until total ≤ limit

**Example Scenario**:
```
Initial state:
- Limit: 5 MB
- Total: 6.45 MB
- Backups: 5

Iteration 1:
- Delete: backup_characters_20251101_083022.zip (1.24 MB)
- New total: 5.21 MB
- Still > 5 MB, continue

Iteration 2:
- Delete: backup_characters_20251102_084511.zip (1.31 MB)
- New total: 3.90 MB
- Now ≤ 5 MB, stop

Final state:
- Total: 3.90 MB
- Backups: 3 (kept newest 3)
```

**Log Example**:
```
2025-11-15 08:00:14 | INFO | RETENTION | Deleted old backup: backup_characters_20251101_083022.zip (1.24 MB)
2025-11-15 08:00:14 | INFO | RETENTION | Deleted old backup: backup_characters_20251102_084511.zip (1.31 MB)
2025-11-15 08:00:15 | INFO | RETENTION | Total size now: 3.90 MB (under limit: 5.00 MB)
```

---

## Edge Cases

### No Backups Exist

**Scenario**: First backup creation, no previous backups

**Behavior**:
```python
backups = self._get_sorted_backups()  # Returns []
total_size_mb = sum(...)  # 0 MB
while 0 > size_limit_mb:  # False, never enters loop
    # No deletion
```

**Result**: No retention applied (nothing to delete)

---

### All Backups Under Limit

**Scenario**: Total size already under limit

**Example**:
```
Limit: 20 MB
Total: 6.45 MB (5 backups × ~1.3 MB)
```

**Behavior**:
```python
while 6.45 > 20:  # False
    # Never enters loop
```

**Result**: All backups kept

---

### Single Large Backup Exceeds Limit

**Scenario**: New backup alone exceeds limit

**Example**:
```
Limit: 5 MB
New backup: 6 MB
Old backups: 3 × 1 MB = 3 MB
Total: 9 MB
```

**Behavior**:
```python
while 9 > 5:
    delete oldest (1 MB)
    total = 8 MB
while 8 > 5:
    delete oldest (1 MB)
    total = 7 MB
while 7 > 5:
    delete oldest (1 MB)
    total = 6 MB
while 6 > 5:
    delete oldest (6 MB new backup)  # ERROR!
    # Can't delete newest backup
```

**Protection**: Loop only deletes from `backups` list sorted by age. Newest backup not in list yet during retention, so safe.

**Result**: Keeps newest 6 MB backup, deletes all old backups

---

### Unlimited Storage (-1)

**Scenario**: User set limit to -1

**Behavior**:
```python
size_limit_mb = -1
if size_limit_mb <= 0:
    return  # Exit early
```

**Result**: No retention, unlimited backups

**Disk Space**: User responsible for managing space

---

### Auto-Delete Disabled

**Scenario**: User unchecked "Auto-delete old backups"

**Behavior**:
```python
auto_delete = False
if not auto_delete:
    return  # Exit early
```

**Result**: No retention, unlimited backups

**Warning**: User already warned when unchecking:
```
⚠️ WARNING: Disabling automatic deletion may cause:
• Disk space saturation
• Future backups failure
• Need to manually manage old backups
```

---

## Retention Policy Modes

### Mode 1: Full Protection (Default)

**Settings**:
```json
{
  "backup_auto_delete_old": true,
  "backup_size_limit_mb": 20
}
```

**Behavior**:
- Automatic deletion enabled
- Size limit: 20 MB
- Deletes oldest when limit exceeded

**Best For**:
- Normal users
- Limited disk space
- Automatic management

---

### Mode 2: Unlimited Backups

**Settings**:
```json
{
  "backup_auto_delete_old": false,
  "backup_size_limit_mb": 20
}
```

**Behavior**:
- Auto-delete disabled (takes priority)
- Size limit ignored
- Keeps all backups forever

**Best For**:
- Archive purposes
- Testing/development
- Ample disk space

**Risks**:
- Disk saturation
- Backup failures (no space)
- Manual cleanup required

---

### Mode 3: High Limit

**Settings**:
```json
{
  "backup_auto_delete_old": true,
  "backup_size_limit_mb": 100
}
```

**Behavior**:
- Automatic deletion enabled
- Size limit: 100 MB
- Allows more backup history

**Best For**:
- Users with many characters
- Long backup history needed
- Good disk space available

---

### Mode 4: Aggressive Cleanup

**Settings**:
```json
{
  "backup_auto_delete_old": true,
  "backup_size_limit_mb": 5
}
```

**Behavior**:
- Automatic deletion enabled
- Size limit: 5 MB
- Keeps only recent backups

**Best For**:
- Very limited disk space
- Only need last 2-3 backups
- Frequent external backups

---

## Calculation Examples

### Example 1: Standard Use Case

**Configuration**:
```json
{
  "backup_compress": true,
  "backup_auto_delete_old": true,
  "backup_size_limit_mb": 20
}
```

**Backups** (compressed, ~1.5 MB each):
```
backup_characters_20251101_083022.zip → 1.52 MB
backup_characters_20251102_084511.zip → 1.48 MB
backup_characters_20251103_085044.zip → 1.51 MB
...
backup_characters_20251115_091122.zip → 1.49 MB (NEW)
```

**Math**:
```
Number of backups that fit in 20 MB:
20 MB ÷ 1.5 MB = ~13 backups

If 14th backup created:
Total = 14 × 1.5 = 21 MB > 20 MB limit
Delete oldest (1.52 MB)
New total = 19.48 MB < 20 MB ✓
```

**Result**: Maintains ~13 recent backups (about 2 weeks of daily backups)

---

### Example 2: Uncompressed Backups

**Configuration**:
```json
{
  "backup_compress": false,
  "backup_auto_delete_old": true,
  "backup_size_limit_mb": 20
}
```

**Backups** (folders, ~4 MB each):
```
backup_characters_20251111_083022/ → 4.12 MB
backup_characters_20251112_084511/ → 4.08 MB
backup_characters_20251113_085044/ → 4.15 MB
backup_characters_20251114_090233/ → 4.11 MB
backup_characters_20251115_091122/ → 4.09 MB (NEW)
```

**Math**:
```
Number of backups that fit in 20 MB:
20 MB ÷ 4 MB = 5 backups

Total = 5 × 4 = 20.55 MB > 20 MB limit
Delete oldest (4.12 MB)
New total = 16.43 MB < 20 MB ✓
```

**Result**: Maintains only 4 recent backups (less history than compressed)

---

### Example 3: Cookies Backup

**Configuration**:
```json
{
  "cookies_backup_compress": true,
  "cookies_backup_auto_delete_old": true,
  "cookies_backup_size_limit_mb": 20
}
```

**Backups** (compressed, ~0.5 MB each):
```
backup_cookies_20251101_083022.zip → 0.49 MB
backup_cookies_20251102_084511.zip → 0.51 MB
...
backup_cookies_20251140_091122.zip → 0.50 MB (NEW)
```

**Math**:
```
Number of backups that fit in 20 MB:
20 MB ÷ 0.5 MB = 40 backups

40 backups × 0.5 MB = 20 MB
```

**Result**: Maintains ~40 backups (over a month of daily backups)

---

## Performance Impact

### Retention Execution Time

**Factors**:
- Number of existing backups
- Backup format (ZIP vs folder)
- Number of deletions needed

**Typical Times**:
| Backups | Deletions | Time |
|---------|-----------|------|
| 5 | 0 | <0.1s |
| 10 | 1 | 0.2s |
| 20 | 5 | 0.5s |
| 50 | 10 | 1.5s |

**Optimization**: ZIP backups faster to process (single file vs recursive folder scan)

---

### Disk I/O

**Read Operations**:
- Read backup list from filesystem
- Read file sizes (stat calls)

**Write Operations**:
- Delete old backup files
- Update filesystem metadata

**Peak Load**: After backup creation (retention runs immediately)

---

## Monitoring Retention

### Log Messages

**Retention Skipped (Auto-Delete Disabled)**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Auto-delete disabled - skipping retention policy
```

**Retention Skipped (Unlimited)**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Unlimited storage mode (-1) - skipping retention
```

**Backups Found**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Found 8 existing backups
```

**Total Size Calculated**:
```
2025-11-15 08:00:14 | DEBUG | RETENTION | Total size: 22.4 MB
```

**Deletion Occurred**:
```
2025-11-15 08:00:14 | INFO | RETENTION | Deleted old backup: backup_characters_20251101_083022.zip (1.24 MB)
2025-11-15 08:00:14 | INFO | RETENTION | Total size now: 21.16 MB
```

**Under Limit**:
```
2025-11-15 08:00:14 | INFO | RETENTION | Total size 19.8 MB under limit 20.0 MB - no deletion needed
```

---

### Statistics in UI

**Settings Dialog Display**:
```
Number of backups: 8
Last backup: 2025-11-15 08:00:12
```

**Interpretation**:
- **Number decreasing** → Retention deleting old backups
- **Number stable** → Under limit, no deletions
- **Number increasing** → No retention (auto-delete off or unlimited)

---

## Troubleshooting

### Too Many Backups Deleted

**Symptoms**:
- Only 1-2 backups remain
- Expected more backup history

**Causes**:
1. Storage limit too low
2. Backup size increased (more characters)
3. Compression disabled (larger backups)

**Solutions**:
1. Increase storage limit (Settings → Backups → Limit)
2. Enable compression (Settings → Backups → Compress)
3. Use unlimited mode if disk space allows

**Example**:
```
Current: 10 MB limit, uncompressed (4 MB each) = 2 backups
Solution: 50 MB limit, compressed (1.5 MB each) = 33 backups
```

---

### No Deletions Occurring

**Symptoms**:
- Backups accumulating beyond limit
- Disk space growing

**Causes**:
1. Auto-delete disabled
2. Unlimited mode (-1)
3. Retention logic error

**Diagnosis**:
```powershell
# Check logs
Get-Content "Logs\daoc_manager_YYYYMMDD.log" | Select-String "RETENTION"
```

**Solutions**:
1. Enable auto-delete (Settings → Backups → Auto-delete)
2. Set finite limit (not -1)
3. Check logs for errors

---

### Backups Deleted Too Aggressively

**Symptoms**:
- All old backups deleted after single new backup
- Backup history lost

**Causes**:
1. Limit set too low
2. Large new backup created

**Solutions**:
1. Increase limit to accommodate desired backup count
2. Formula: `Desired Count × Average Size = Required Limit`

**Example**:
```
Want: 14 days of backups
Backup size: 1.5 MB compressed
Required limit: 14 × 1.5 = 21 MB
Set limit to: 25 MB (buffer)
```

---

## Best Practices

### Recommended Limits

| Scenario | Compression | Limit |
|----------|-------------|-------|
| Few characters (1-5) | Enabled | 20 MB |
| Medium (5-10) | Enabled | 30-50 MB |
| Many (10-20) | Enabled | 50-100 MB |
| Archive | Enabled | -1 (unlimited) |
| Limited disk space | Enabled | 10 MB |

### Monitoring

1. **Check logs weekly**: Look for retention patterns
2. **Verify backup count**: Settings dialog statistics
3. **Monitor disk space**: Backup folder size vs limit

### Maintenance

1. **Review limit quarterly**: Adjust as character count grows
2. **Enable compression**: Saves 60-70% space
3. **External backups**: Copy to external drive monthly

---

## Related Documentation

- [User Guide](BACKUP_USER_GUIDE.md) - How to use backups
- [Settings Reference](BACKUP_SETTINGS.md) - All settings explained
- [Technical Architecture](BACKUP_ARCHITECTURE.md) - Implementation details
- [README](README.md) - Main documentation index
