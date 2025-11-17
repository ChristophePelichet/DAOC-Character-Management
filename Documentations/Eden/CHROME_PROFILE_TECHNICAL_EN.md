# Chrome Profile Management - Technical Documentation

## Overview

**Version**: 0.108  
**Purpose**: Dedicated Chrome profile for Selenium scraping, isolated from user's personal browser  
**Location**: User AppData directory (`%LOCALAPPDATA%/DAOC_Character_Manager/Eden/ChromeProfile/`)  
**Compatibility**: PyInstaller --onefile mode  

---

## Architecture

### Data Storage Strategy

**Problem**: PyInstaller --onefile applications cannot write to their installation directory  
**Solution**: Store user data in OS-specific AppData locations

```
Windows:  %LOCALAPPDATA%/DAOC_Character_Manager/
          └── Eden/
              ├── eden_cookies.pkl          (Migrated from Configuration/)
              └── ChromeProfile/             (Dedicated Selenium profile)
                  └── Default/
                      ├── Cache/
                      ├── Cookies
                      ├── History
                      └── Preferences

Linux:    ~/.local/share/DAOC_Character_Manager/Eden/...
macOS:    ~/Library/Application Support/DAOC_Character_Manager/Eden/...
```

### Multi-OS Path Resolution

**Implementation** (`Functions/path_manager.py`):

```python
def get_user_data_dir():
    """Platform-specific user data directory"""
    app_name = "DAOC_Character_Manager"
    
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA")  # Windows
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")  # macOS
    else:
        base = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")  # Linux
    
    user_data_path = Path(base) / app_name
    user_data_path.mkdir(parents=True, exist_ok=True)
    return user_data_path

def get_chrome_profile_path():
    """Dedicated Chrome profile for Selenium"""
    profile_path = get_eden_data_dir() / "ChromeProfile"
    profile_path.mkdir(parents=True, exist_ok=True)
    return profile_path

def get_eden_cookies_path():
    """Eden cookies file location"""
    return get_eden_data_dir() / "eden_cookies.pkl"
```

---

## Eden Folder Cleanup

### Settings Integration

**Location**: Settings > Herald Eden > Cookies Path (Eden AppData)

**UI Elements**:
- 📂 **Open Folder**: Opens `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/` in Explorer
- 🗑️ **Clean Eden** (red button): Deletes all Eden data (cookies + Chrome profile)

**Clean Eden Button**:
- **Action**: Removes entire Eden folder contents
- **Confirmation**: Shows warning dialog before deletion
- **Content Deleted**:
  - `eden_cookies.pkl` - All Eden Herald cookies
  - `ChromeProfile/` - Complete Chrome profile (cache, history, session, preferences)
- **After Cleanup**: Folder recreated empty, user must regenerate cookies

**Why Clean?**:
- Chrome profile corruption
- Clear browsing data
- Reset to fresh state
- Troubleshooting connection issues

**Replacement**: The "Clear Chrome Profile" button in Cookie Manager dialog has been **removed** in favor of this unified cleanup in Settings.

---

## Cookie Manager Integration

### Automatic Migration

**Trigger**: First initialization of `CookieManager`  
**Source**: `Configuration/eden_cookies.pkl`  
**Destination**: `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/eden_cookies.pkl`

**Migration Logic** (`Functions/cookie_manager.py`):

```python
def __init__(self, config_dir=None):
    from Functions.path_manager import get_eden_cookies_path, get_eden_data_dir
    
    self.cookie_file = get_eden_cookies_path()
    self.config_dir = get_eden_data_dir()
    
    # Automatic migration
    self._migrate_cookies_from_old_location()

def _migrate_cookies_from_old_location(self):
    """One-time migration from Configuration/ to Eden/"""
    if self.cookie_file.exists():
        return  # Already migrated
    
    from Functions.config_manager import get_config_dir
    old_cookie_file = Path(get_config_dir()) / "eden_cookies.pkl"
    
    if old_cookie_file.exists():
        # Copy to new location
        shutil.copy2(old_cookie_file, self.cookie_file)
        
        # Create backup of old file
        backup_file = old_cookie_file.with_suffix(".pkl.migrated")
        shutil.copy2(old_cookie_file, backup_file)
        
        eden_logger.info(f"Migration: {old_cookie_file} → {self.cookie_file}")
```

### Chrome Profile Management

**Methods** (`Functions/cookie_manager.py`):

```python
def get_chrome_profile_size():
    """Calculate total size of Chrome profile in bytes"""
    from Functions.path_manager import get_chrome_profile_path
    
    profile_path = get_chrome_profile_path()
    if not profile_path.exists():
        return 0
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(profile_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    
    return total_size

def clear_chrome_profile():
    """Delete and recreate Chrome profile (purge cache/history)"""
    from Functions.path_manager import get_chrome_profile_path
    
    profile_path = get_chrome_profile_path()
    if not profile_path.exists():
        return True
    
    shutil.rmtree(profile_path)  # Delete all
    profile_path.mkdir(parents=True, exist_ok=True)  # Recreate empty
    
    eden_logger.info(f"Chrome profile purged: {profile_path}")
    return True
```

---

## Selenium Integration

### Chrome Options Configuration

**Modified Method** (`Functions/cookie_manager.py -> _try_chrome()`):

```python
def _try_chrome(self, headless, allow_download, errors):
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from Functions.path_manager import get_chrome_profile_path
    
    chrome_options = ChromeOptions()
    
    # Dedicated profile in AppData
    profile_path = get_chrome_profile_path()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--profile-directory=Default")
    
    # Headless mode
    if headless:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
    
    # Standard options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver
```

### Profile Isolation

**Benefits**:
- ✅ No interference with user's personal Chrome browser
- ✅ Dedicated cache/history for Eden scraping
- ✅ Persistent cookies between sessions (optional)
- ✅ Separate browser fingerprint

**Chrome Profile Directory Structure**:
```
ChromeProfile/
└── Default/
    ├── Cache/               (Web resources)
    ├── Code Cache/          (JavaScript compiled code)
    ├── Cookies              (Session cookies, NOT eden_cookies.pkl)
    ├── History              (Visited URLs)
    ├── Local Storage/       (localStorage data)
    ├── Preferences          (Browser settings)
    └── Session Storage/     (sessionStorage data)
```

---

## Backup System Integration

### Modified Backup Logic

**File** (`Functions/backup_manager.py`):

```python
def _perform_cookies_backup(self, mode="MANUAL", reason=None):
    from Functions.path_manager import get_eden_cookies_path, get_eden_data_dir
    
    # New paths (v0.108+)
    cookies_file = get_eden_cookies_path()
    cookies_folder = get_eden_data_dir()
    
    if not cookies_file.exists():
        return {"success": False, "message": "No cookies configured yet"}
    
    # Create backup (includes ChromeProfile/ if exists)
    if should_compress:
        self._create_zip_backup(str(cookies_folder), backup_file)
    else:
        shutil.copytree(str(cookies_folder), backup_file, dirs_exist_ok=True)
```

**What Gets Backed Up**:
- ✅ `eden_cookies.pkl` - Eden authentication cookies
- ✅ `ChromeProfile/` - Entire Chrome profile directory (if exists)

**Backup Size**:
- Cookies only: ~10-50 KB
- Cookies + Profile: 1-10 MB (depending on cache)

---

## User Interface

### Cookie Manager Dialog

**Location**: Tools → Cookie Manager

**New Section** (v0.108):
```
┌─────────────────────────────────────────────┐
│ 🔧 Dedicated Chrome Profile                │
├─────────────────────────────────────────────┤
│ 📊 Profile size: 2.3 MB                     │
│                                             │
│ [🗑️ Clear Chrome Profile]                  │
└─────────────────────────────────────────────┘
```

**Features**:
1. **Profile Size Display** - Real-time calculation of ChromeProfile/ size
2. **Purge Button** - Delete all profile data (cache, history, etc.)
3. **Confirmation Dialog** - Warns about data loss (cookies NOT affected)

**Translations** (FR/EN/DE):
```json
{
  "cookie_manager": {
    "chrome_profile_section": "🔧 Profil Chrome Dédié",
    "chrome_profile_size": "📊 Taille du profil: {size}",
    "chrome_profile_size_empty": "📊 Profil vide (non utilisé)",
    "clear_chrome_profile": "Purger le profil Chrome",
    "clear_chrome_profile_tooltip": "Supprime cache, historique et données...",
    "clear_chrome_confirm_title": "Confirmer la purge",
    "clear_chrome_confirm_message": "... Les cookies Eden ne seront PAS supprimés.",
    "clear_chrome_success_title": "Succès",
    "clear_chrome_success_message": "Le profil Chrome a été purgé avec succès."
  }
}
```

---

## PyInstaller Compatibility

### .spec File Configuration

**File**: `DAOC-Character-Manager.spec`

**Excludes** (Already configured):
```python
excludes=[
    'Configuration',  # User data - not bundled
    'Characters',     # User data - not bundled
    'Logs',           # Runtime logs - not bundled
    # ... other excludes
]
```

**No Changes Required**:
- ✅ User data already excluded from build
- ✅ AppData paths created at runtime
- ✅ --onefile mode fully compatible

### Frozen vs Script Mode

**Detection** (`Functions/path_manager.py`):
```python
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    base_path = os.path.dirname(sys.executable)
else:
    # Running as Python script
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
```

**Behavior**:
- **Script mode**: Data in project's `Configuration/` (development)
- **Frozen mode**: Data in `%LOCALAPPDATA%/...` (production)

---

## Testing Checklist

### Unit Tests

- [ ] `path_manager.get_user_data_dir()` - Correct OS-specific path
- [ ] `path_manager.get_chrome_profile_path()` - Directory creation
- [ ] `path_manager.get_eden_cookies_path()` - File path generation
- [ ] `cookie_manager._migrate_cookies_from_old_location()` - Migration logic
- [ ] `cookie_manager.get_chrome_profile_size()` - Size calculation
- [ ] `cookie_manager.clear_chrome_profile()` - Profile deletion

### Integration Tests

- [ ] **Migration Test**: Copy old cookie file, verify migration on init
- [ ] **Selenium Test**: Initialize driver with profile, verify isolation
- [ ] **Backup Test**: Create backup, verify ChromeProfile/ included
- [ ] **UI Test**: Open Cookie Manager, verify size display and purge button

### Manual Testing (PyInstaller)

```powershell
# Build executable
pyinstaller DAOC-Character-Manager.spec

# Test migration
1. Place eden_cookies.pkl in Configuration/
2. Run dist/DAOC Character Manager.exe
3. Verify file migrated to %LOCALAPPDATA%/DAOC_Character_Manager/Eden/
4. Verify backup created as .pkl.migrated

# Test Chrome profile
1. Generate cookies via Cookie Manager
2. Check ChromeProfile/ created in AppData/Eden/
3. Open Cookie Manager, verify profile size displayed
4. Click "Purge Profile", verify confirmation dialog
5. Verify profile recreated empty

# Test multi-launch
1. Close application
2. Relaunch .exe
3. Verify no duplicate migration (uses existing Eden/ data)
```

---

## Troubleshooting

### Issue: "Cookies not found after migration"

**Cause**: Old path still referenced somewhere  
**Solution**: Search codebase for `Configuration/eden_cookies`, replace with `get_eden_cookies_path()`

### Issue: "ChromeProfile/ not created"

**Cause**: `path_manager` methods not called  
**Solution**: Verify `_try_chrome()` calls `get_chrome_profile_path()`

### Issue: "Multiple Chrome profiles created"

**Cause**: Path not consistent between calls  
**Solution**: Always use `get_chrome_profile_path()`, never hardcode paths

### Issue: "Purge button doesn't update size"

**Cause**: `update_chrome_profile_size()` not called after purge  
**Solution**: Call `self.update_chrome_profile_size()` in `clear_chrome_profile()` success handler

---

## Version History

### v0.108 (Current)

**New Features**:
- ✅ Dedicated Chrome profile in AppData
- ✅ Automatic cookie migration from Configuration/
- ✅ Multi-OS path support (Windows/Linux/macOS)
- ✅ Chrome profile size display in Cookie Manager
- ✅ Unified "Clean Eden" button in Settings (Herald tab)

**Changed**:
- 🔄 Cookies path: `Configuration/eden_cookies.pkl` → `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/eden_cookies.pkl`
- 🔄 Chrome profile: No profile → Dedicated profile in AppData
- 🔄 Backup: Eden folder → Cookies file only (`eden_cookies.pkl`)
- 🔄 UI: Removed "Clear Chrome Profile" from Cookie Manager
- 🔄 UI: Added "Clean Eden" button in Settings > Herald > Cookies section

**Migration**:
- 🔁 Automatic one-time migration on first startup
- 🔁 Backup created as `eden_cookies.pkl.migrated`
- 🔁 No user action required

**Backup Strategy**:
- 💾 Cookies backup: `eden_cookies.pkl` file only (~10 KB)
- ❌ ChromeProfile excluded from backup (can be regenerated)
- ✅ Reduced backup size from 50+ MB to ~10 KB

---

## Backup System

### Cookies Backup Strategy

**What is Backed Up**: `eden_cookies.pkl` file **ONLY**

**Rationale**:
| Component | Backed Up | Reason |
|-----------|-----------|--------|
| `eden_cookies.pkl` | ✅ YES | Critical authentication data, cannot be regenerated |
| `ChromeProfile/` | ❌ NO | Cache/session data, can be regenerated |

**Size Impact**:
- Cookies file: ~10-50 KB
- Chrome profile: ~50-150 MB
- **Savings**: 99%+ reduction in backup size

### Backup Formats

**Compressed** (default):
```
backup_cookies_20251117_143022_Manual.zip
  └─ eden_cookies.pkl
```

**Uncompressed**:
```
backup_cookies_20251117_143022_Manual.pkl (direct copy)
```

### Implementation

**Backup Manager** (`Functions/backup_manager.py`):

```python
def _perform_cookies_backup(self, mode="MANUAL", reason=None):
    from Functions.path_manager import get_eden_cookies_path
    
    cookies_file = get_eden_cookies_path()
    
    if should_compress:
        # ZIP: Contains only eden_cookies.pkl
        import zipfile
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(str(cookies_file), cookies_file.name)
    else:
        # Direct copy: .pkl file
        shutil.copy2(str(cookies_file), backup_file)
```

### Settings UI

**Location**: Settings > Backups > Eden Cookies Backup

**Controls**:
- ✅ **Enable cookies backup** - Master switch
- 🗄️ **Compress backups (ZIP)** - Format selection
- 🗑️ **Auto-delete old backups** - Retention policy
- 💾 **Storage limit** - 20 MB default (configurable)
- 📂 **Open folder** - Opens backup directory
- 🔄 **Backup now** - Manual backup trigger

**Retention Policy**:
- Daily automatic backup (if enabled)
- Size-based retention (oldest deleted when limit exceeded)
- Manual backups bypass daily limit

### Recovery

**From ZIP Backup**:
1. Extract `eden_cookies.pkl` from backup ZIP
2. Copy to `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/`
3. Restart application - cookies restored

**From .pkl Backup**:
1. Rename backup file to `eden_cookies.pkl`
2. Copy to `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/`
3. Restart application

---

## Related Documentation

- [Cookie Manager Implementation](CHROME_PROFILE_IMPLEMENTATION.md) - Task breakdown (French)
- [Backup Architecture](../Backups/BACKUP_ARCHITECTURE.md) - Backup system details
- [Connect to Eden Herald](CONNECT_TO_EDEN_HERALD_EN.md) - Cookie generation guide

---

## Summary

**Key Points**:
1. ✅ Chrome profile stored in **AppData**, not project directory
2. ✅ **Automatic migration** from old Configuration/ location
3. ✅ **Multi-OS compatible** (Windows/Linux/macOS)
4. ✅ **PyInstaller --onefile** ready
5. ✅ **User-facing UI** for profile management
6. ✅ **Backup integration** preserves profile + cookies
7. ✅ **Fully translated** (FR/EN/DE)

**No User Action Required** - Migration happens automatically on first launch after update to v0.108.
