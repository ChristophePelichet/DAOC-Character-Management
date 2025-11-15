# Backup System Documentation

## Overview

The automatic backup system protects your character data and Eden cookies from accidental loss. It offers advanced features including compression, automatic retention, and disk space management.

## 📚 Documentation Index

### User Guides
- **[BACKUP_USER_GUIDE.md](BACKUP_USER_GUIDE.md)** - Complete user guide
- **[BACKUP_SETTINGS.md](BACKUP_SETTINGS.md)** - Detailed settings configuration

### Technical Documentation
- **[BACKUP_ARCHITECTURE.md](BACKUP_ARCHITECTURE.md)** - Architecture and internal operation
- **[BACKUP_RETENTION_POLICY.md](BACKUP_RETENTION_POLICY.md)** - Retention policy and automatic deletion

### Testing & Validation
- **[TEST_BACKUP_README.md](../../Tools/TEST_BACKUP_README.md)** - Automated test script

## 🎯 Key Features

### 1. Daily Automatic Backup
- ✅ One backup per day on first startup
- ✅ No duplicates on the same day
- ✅ Precise timestamp (YYYYMMDD_HHMMSS)

### 2. Smart Compression
- ✅ ZIP to save space (can be enabled/disabled)
- ✅ Folder copy for uncompressed backup
- ✅ Significant size reduction

### 3. Automatic Space Management
- ✅ Configurable storage limit (default: 20 MB)
- ✅ Automatic deletion of oldest backups
- ✅ Unlimited mode available (-1)
- ✅ Protection can be disabled if needed

### 4. Separate Backups
- ✅ **Characters**: All your characters
- ✅ **Cookies**: Eden sessions for automatic import

### 5. User-Friendly Interface
- ✅ Configuration in Settings
- ✅ Real-time statistics
- ✅ Quick access buttons (Move, Open)

## 🚀 Quick Start

### Minimum Configuration

1. **Open Settings**: Configuration Menu → Settings
2. **Backups Tab**: Dedicated section
3. **Check Options**:
   - ☑ Enable backups (checked by default)
   - ☑ Compress backups (ZIP)
   - ☑ Auto-delete old backups (enabled by default)
   - Limit: 20 MB (or adjust according to your needs)

### Normal Usage

The system works **automatically**:
- Backup created on first startup of the day
- No action required from you
- Check Settings to view statistics

## 📊 Backup Structure

```
Backups/
├── Characters/
│   ├── backup_characters_20251115_143022.zip
│   ├── backup_characters_20251114_091505.zip
│   └── backup_characters_20251113_085432.zip
└── Cookies/
    ├── backup_cookies_20251115_143022.zip
    ├── backup_cookies_20251114_091505.zip
    └── backup_cookies_20251113_085432.zip
```

## ⚙️ Advanced Configuration

### Storage Limits

| Value | Behavior |
|-------|----------|
| 20 MB | Default limit - suitable for most users |
| 50 MB | For longer history |
| 100+ MB | For maximum retention |
| -1 | Unlimited - WARNING: risk of disk saturation |

### Auto-Delete

**⚠️ Important**: If you disable automatic deletion:
- Backups accumulate indefinitely
- Risk of disk space saturation
- Future backups may fail
- Manual management required

## 🔍 Backup Verification

### In the Interface

**Settings → Backups** displays:
- **Storage Limit**: Allocated space
- **Number of Backups**: Current total
- **Last Backup**: Date and time

### On Disk

1. Click **📂 Open Folder** in Settings
2. Verify presence of `.zip` files or folders
3. Check dates in filenames

## 🛠️ Maintenance

### Manual Cleanup

If you have disabled auto-delete:

1. **Open backup folder**
2. **Identify old ones** (by date in filename)
3. **Manually delete** the oldest
4. **Keep at least** 3-5 recent backups

### Moving Backups

Use the **📦 Move** button in Settings:
- Select a new parent folder
- System automatically moves all content
- Configuration automatically updated

### Restoration

To restore a backup:

1. **Locate** the desired backup file
2. **If ZIP**: Extract the contents
3. **Copy** files to Characters folder
4. **Restart** the application

## 📈 Monitoring

### Logs

Backup operations are traced in logs:
```
[BACKUP] Creating backup: backup_characters_20251115_143022.zip
[BACKUP] Backup created successfully
[RETENTION] Found 8 existing backups
[RETENTION] Total backup size: 18.5 MB / 20 MB
[RETENTION] No backups need to be deleted
```

### Troubleshooting

If a backup fails:
1. Check logs in Debug tab
2. Verify available disk space
3. Check folder permissions
4. Try manual backup (button in Settings if implemented)

## 🔐 Security

### Best Practices

- ✅ Keep at least **3 recent backups**
- ✅ Regularly check available space
- ✅ Don't store backups on the same disk as data
- ✅ Occasionally test restoration

### Limitations

- ❌ No encryption (files in clear text in ZIP)
- ❌ No automatic external backup (cloud)
- ❌ No advanced versioning

## 🆘 Troubleshooting

### Backup Not Created

**Possible Causes**:
- Backups disabled in Settings
- Backup already performed today
- Insufficient disk space
- Missing permissions

**Solutions**:
1. Check Settings → Backups → ☑ Enable
2. Consult logs for exact message
3. Verify available disk space
4. Check folder access rights

### Too Many Backups Deleted

**Cause**: Storage limit too low

**Solution**:
1. Settings → Backups
2. Increase limit (e.g., 20 MB → 50 MB)
3. Or disable auto-delete (⚠️ warning)

### Backups Too Large

**Solutions**:
- ✅ Enable ZIP compression
- ✅ Clean up unused old characters
- ✅ Increase storage limit

## 📞 Support

For any questions or issues:
1. Consult this documentation
2. Check logs (Settings → Debug)
3. Run test script: `python Tools/test_backup_system.py`
4. Open a GitHub issue with logs

## 📝 Changelog

### Version 0.108 (2025-11-15)
- ✨ Complete automatic backup system
- ✨ Optional ZIP compression
- ✨ Automatic deletion with storage limit
- ✨ User interface in Settings
- ✨ Separate Characters/Cookies backups
- ✨ Unlimited mode (-1)
- ✨ Automated test script

## 🔗 Useful Links

- [User Guide](BACKUP_USER_GUIDE.md)
- [Settings Configuration](BACKUP_SETTINGS.md)
- [Technical Architecture](BACKUP_ARCHITECTURE.md)
- [Retention Policy](BACKUP_RETENTION_POLICY.md)
- [Test Script Documentation](TEST_BACKUP_README.md)
- [Test Script ](test_backup_system.pyS)
