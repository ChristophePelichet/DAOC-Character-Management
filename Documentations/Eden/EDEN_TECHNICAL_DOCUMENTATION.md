# Eden Herald System - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Connection Management](#connection-management)
   - [Core Connection Function](#core-connection-function)
   - [Chrome Profile Management](#chrome-profile-management)
   - [Connection Performance](#connection-performance)
4. [Character Scraping Operations](#character-scraping-operations)
   - [Character Search](#character-search)
   - [Character Update](#character-update)
   - [Character Statistics](#character-statistics)
5. [Wealth Management](#wealth-management)
6. [UI Integration](#ui-integration)
   - [Button State Management](#button-state-management)
   - [Herald Validation](#herald-validation)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)
9. [Testing & Troubleshooting](#testing--troubleshooting)
10. [Version History](#version-history)

---

## Overview

### Purpose

The Eden Herald System provides comprehensive integration with the Eden-DAOC Herald website for character data retrieval, authentication, and profile scraping. It centralizes all Herald-related operations into a consistent, maintainable architecture.

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Connection Manager** | Establishes authenticated Herald connections | `Functions/eden_scraper.py` |
| **Character Search** | Searches for characters on Herald | `Functions/eden_scraper.py` |
| **Character Update** | Updates character from Herald URL | `Functions/eden_scraper.py` |
| **Profile Scraper** | Scrapes detailed statistics (RvR/PvP/PvE) | `Functions/character_profile_scraper.py` |
| **Wealth Manager** | Retrieves realm-wide money totals | `Functions/wealth_manager.py` |
| **Chrome Profile Manager** | Manages dedicated Chrome profile | `Functions/path_manager.py` |
| **UI State Manager** | Controls Herald button availability | `Functions/ui_manager.py` |

### Key Features

- ✅ **Single Point of Connection** - Centralized `_connect_to_eden_herald()` function
- ✅ **Cookie-Based Authentication** - Persistent session management
- ✅ **Multi-Browser Support** - Chrome/Edge/Firefox fallback
- ✅ **Chrome Profile Isolation** - Dedicated profile in AppData
- ✅ **Performance Caching** - 10-second result caching
- ✅ **Bot Check Avoidance** - Visible browser + realistic timeouts
- ✅ **Thread-Safe UI** - Button state management prevents conflicts
- ✅ **Multi-Language Support** - FR/EN/DE translations

---

## System Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERFACE                            │
├─────────────────────────────────────────────────────────────────┤
│  Main Window          │  Character Sheet  │  Settings Dialog    │
│  - Search Button      │  - Update Herald  │  - Cookie Manager   │
│  - Context Menu       │  - Update Stats   │  - Clean Eden       │
└──────────┬────────────┴───────────┬────────┴──────────┬─────────┘
           │                        │                    │
           ▼                        ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UI MANAGER (State Control)                   │
│  - Button enable/disable based on validation state              │
│  - Herald validation thread lifecycle management                │
│  - Chrome profile conflict prevention                           │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  COOKIE MANAGER (Authentication)                │
│  - Cookie generation/import/export                              │
│  - Cookie validation (existence + expiration)                   │
│  - Chrome profile management                                    │
│  - Connection testing with performance caching                  │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              EDEN SCRAPER (Core Connection Logic)               │
│  - sanitize_filename() - Safe filename creation (v0.109+)       │
│  - _connect_to_eden_herald() - Single connection function       │
│  - search_herald_character() - Character search                 │
│  - scrape_character_from_url() - Character update               │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ├──────────────────────────────────────────────────────┐
           │                                                      │
           ▼                                                      ▼
┌─────────────────────────────────────┐  ┌─────────────────────────────┐
│   CHARACTER PROFILE SCRAPER         │  │    WEALTH MANAGER           │
│  - scrape_rvr_captures()            │  │  - get_realm_money()        │
│  - scrape_pvp_stats()               │  │  - get_first_char_per_realm()│
│  - scrape_pve_stats()               │  └─────────────────────────────┘
│  - scrape_wealth_money()            │
│  - scrape_achievements()            │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SELENIUM WEBDRIVER                             │
│  - Chrome/Edge/Firefox (multi-browser fallback)                 │
│  - Dedicated Chrome profile in AppData                          │
│  - Cookie injection + session management                        │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  EDEN HERALD WEBSITE                            │
│  https://eden-daoc.net/herald                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Connection Management

### Core Connection Function

#### `_connect_to_eden_herald()` - Centralized Connection

**Location**: `Functions/eden_scraper.py` (line ~417)  
**Visibility**: Internal (prefix `_`)  
**Purpose**: Single source of truth for all Herald connections

**Function Signature**:
```python
def _connect_to_eden_herald(cookie_manager=None, headless=False):
    """
    Internal function: Establishes authenticated connection to Eden Herald
    Centralizes steps 1-6 common to all scraping functions
    
    Args:
        cookie_manager: CookieManager instance (created if None)
        headless: Browser display mode (False = visible, True = hidden)
        
    Returns:
        tuple: (scraper: EdenScraper|None, error_message: str)
    """
```

**Return Values**:

| Success | Return Value | Description |
|---------|-------------|-------------|
| ✅ Yes | `(scraper_instance, "")` | Authenticated scraper + empty error |
| ❌ No | `(None, "error message")` | None + descriptive error message |

#### Connection Workflow (6 Steps)

```
STEP 1: Cookie Manager Initialization
  ↓
STEP 2: Cookie Existence Verification
  ↓
STEP 3: Cookie Validity Verification
  ↓
STEP 4: Scraper Initialization
  ↓
STEP 5: Browser Driver Initialization (Chrome/Edge/Firefox)
  ↓
STEP 6: Cookie Loading (3 internal timeouts)
  ├─ 6a. Navigate to https://eden-daoc.net/ (1s wait)
  ├─ 6b. Add cookies to browser session
  ├─ 6c. Refresh page (2s wait)
  ├─ 6d. Navigate to Herald (2s wait)
  └─ 6e. Verify connection success
```

**Total Time**: ~6-8 seconds (including all timeouts)

#### Usage Examples

**Basic Usage**:
```python
scraper, error = _connect_to_eden_herald(headless=False)

if scraper:
    # Connection successful
    scraper.driver.get("https://eden-daoc.net/herald?n=search&s=PlayerName")
    # ... perform scraping ...
    scraper.close()
else:
    # Connection failed
    print(f"Error: {error}")
```

**Custom Cookie Manager**:
```python
from Functions.cookie_manager import CookieManager

cookie_manager = CookieManager()
scraper, error = _connect_to_eden_herald(
    cookie_manager=cookie_manager,
    headless=False
)
```

#### Integration Points

Functions using `_connect_to_eden_herald()`:

1. **`sanitize_filename()`** - Filename sanitization (v0.109+)
2. **`search_herald_character()`** - Character search operations
3. **`scrape_character_from_url()`** - Character update from URL
4. **`CharacterProfileScraper.connect()`** - Stats scraping connection

---

### Chrome Profile Management

#### Architecture

**Data Storage Strategy**: Dedicated Chrome profile isolated from user's personal browser

**Location**: User AppData directory (PyInstaller --onefile compatible)

```
Windows:  %LOCALAPPDATA%/DAOC_Character_Manager/
          └── Eden/
              ├── eden_cookies.pkl          (Authentication cookies)
              └── ChromeProfile/             (Dedicated Selenium profile)
                  └── Default/
                      ├── Cache/
                      ├── Cookies
                      ├── History
                      └── Preferences

Linux:    ~/.local/share/DAOC_Character_Manager/Eden/...
macOS:    ~/Library/Application Support/DAOC_Character_Manager/Eden/...
```

#### Multi-OS Path Resolution

**Implementation** (`Functions/path_manager.py`):

```python
def get_user_data_dir():
    """Platform-specific user data directory"""
    app_name = "DAOC_Character_Manager"
    
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    
    user_data_path = Path(base) / app_name
    user_data_path.mkdir(parents=True, exist_ok=True)
    return user_data_path

def get_chrome_profile_path():
    """Dedicated Chrome profile for Selenium"""
    profile_path = get_eden_data_dir() / "ChromeProfile"
    profile_path.mkdir(parents=True, exist_ok=True)
    return profile_path
```

#### Cookie Migration

**Trigger**: First initialization of `CookieManager`  
**Source**: `Configuration/eden_cookies.pkl`  
**Destination**: `%LOCALAPPDATA%/DAOC_Character_Manager/Eden/eden_cookies.pkl`

**Migration Logic**:
```python
def _migrate_cookies_from_old_location(self):
    """One-time migration from Configuration/ to Eden/"""
    if self.cookie_file.exists():
        return  # Already migrated
    
    old_cookie_file = Path(get_config_dir()) / "eden_cookies.pkl"
    
    if old_cookie_file.exists():
        # Copy to new location
        shutil.copy2(old_cookie_file, self.cookie_file)
        
        # Create backup
        backup_file = old_cookie_file.with_suffix(".pkl.migrated")
        shutil.copy2(old_cookie_file, backup_file)
```

#### Selenium Integration

**Chrome Options Configuration**:
```python
def _try_chrome(self, headless, allow_download, errors):
    from Functions.path_manager import get_chrome_profile_path
    
    chrome_options = ChromeOptions()
    
    # Dedicated profile in AppData
    profile_path = get_chrome_profile_path()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--profile-directory=Default")
    
    # Bot check avoidance
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    return webdriver.Chrome(options=chrome_options)
```

**Profile Isolation Benefits**:
- ✅ No interference with user's personal Chrome
- ✅ Dedicated cache/history for Eden scraping
- ✅ Persistent session between operations
- ✅ Separate browser fingerprint

#### Eden Folder Cleanup

**Settings Integration**: Settings > Herald Eden > Cookies Path

**UI Elements**:
- 📂 **Open Folder**: Opens Eden directory in Explorer
- 🗑️ **Clean Eden** (red button): Deletes all Eden data

**Clean Eden Action**:
- **Deletes**: `eden_cookies.pkl` + entire `ChromeProfile/` directory
- **Confirmation**: Warning dialog before deletion
- **After Cleanup**: Folder recreated empty, cookies must be regenerated
- **Use Cases**: Chrome profile corruption, troubleshooting, fresh start

---

### Connection Performance

#### Performance Optimizations

**1. Result Caching (10 seconds)**:
```python
_test_cache = {'result': None, 'timestamp': None}
_CACHE_DURATION_SECONDS = 10
```

- First test: Full connection (3-4s)
- Subsequent tests within 10s: Instant cache return (<0.1s)
- **Impact**: 99%+ reduction for repeated tests

**2. Reduced Wait Times**:

| Step | Before | After | Reduction |
|------|--------|-------|-----------|
| Homepage load | 1s | 0.5s | 50% |
| After cookies | 1s | 0.3s | 70% |
| After refresh | 2s | 1s | 50% |
| Herald navigation | 3s | 1.5s | 50% |
| **TOTAL** | **7s** | **3.3s** | **53%** |

#### Performance Breakdown (12 Steps)

| Step | Operation | Time | Optimizable |
|------|-----------|------|-------------|
| 1 | Cache check | <1ms | ✅ |
| 2 | Cookie exists check | <1ms | ✅ |
| 3 | Selenium import | 900-1000ms | ❌ Module load |
| 4 | Load cookies from disk | 1-5ms | ✅ |
| 5 | Read config | <1ms | ✅ |
| 6 | **Init Selenium driver** | **2000-2500ms** | ❌ **Bottleneck** |
| 7 | Navigate homepage + wait | 1500-1800ms | ⚠️ Reduced |
| 8 | Add cookies + wait | 300-350ms | ✅ Reduced |
| 9 | Refresh page + wait | 1000-1200ms | ⚠️ Reduced |
| 10 | Navigate Herald + wait | 1500-1800ms | ⚠️ Reduced |
| 11 | Fetch HTML | 20-30ms | ✅ |
| 12 | Parse HTML | <1ms | ✅ |
| **TOTAL (before)** | | **~8000ms** | |
| **TOTAL (after)** | | **~3500ms** | **56% faster** |

**Critical Bottleneck**: Step 6 (Selenium driver init) accounts for ~25-30% and cannot be optimized (Chrome/Selenium startup overhead).

#### Performance Logging (Optional)

**Enable**: `Configuration/config.json`
```json
{
  "system": {
    "eden": {
      "enable_performance_logs": false  // Set to true
    }
  }
}
```

**Log File**: `Logs/eden_performance_YYYY-MM-DD.log`

**Example Output**:
```
2025-11-17 15:14:09 - EDEN_PERF - INFO - PERF - 🚀 DÉBUT TEST CONNEXION EDEN
2025-11-17 15:14:09 - EDEN_PERF - INFO - PERF - ⏱️  STEP 1: Cache check - 0ms
2025-11-17 15:14:09 - EDEN_PERF - INFO - PERF - ⏱️  STEP 2: Cookie check - 0ms
2025-11-17 15:14:10 - EDEN_PERF - INFO - PERF - ⏱️  STEP 3: Import Selenium - 978ms
2025-11-17 15:14:12 - EDEN_PERF - INFO - PERF - ⏱️  STEP 6: Init Chrome - 2022ms
2025-11-17 15:14:14 - EDEN_PERF - INFO - PERF - ⏱️  STEP 7: Homepage - 1761ms
2025-11-17 15:14:17 - EDEN_PERF - INFO - PERF - ✅ CONNECTÉ - TOTAL: 8051ms
```

**Key Metrics to Monitor**:
- STEP 6 (Driver Init): Should be 2-3s (if >5s: slow system/antivirus)
- STEP 7 (Homepage): Should be 1.5-2s (if >3s: slow internet)
- STEP 10 (Herald): Should be 1.5-2s (if >3s: Eden server slow)
- TOTAL: Should be 3-5s non-cached (if >7s: investigate bottleneck)

---

## Character Scraping Operations

### Character Search

#### `sanitize_filename()` Function

**Location**: `Functions/eden_scraper.py` (line ~24)  
**Purpose**: Sanitize text for safe use as filename (removes Windows/POSIX invalid characters)

**Function Signature**:
```python
def sanitize_filename(text):
    """
    Sanitise un texte pour l'utiliser comme nom de fichier.
    Supprime les caractères invalides Windows et autres systèmes.
    
    Caractères invalides: * ? " < > | : \\ /
    
    Args:
        text (str): Texte à sanitiser
        
    Returns:
        str: Texte sanitisé pour utilisation en nom de fichier
    """
```

**Features**:
- ✅ Removes Windows-invalid characters: `* ? " < > | : \ /`
- ✅ Replaces spaces with underscores
- ✅ Removes leading/trailing underscores
- ✅ Returns fallback "search" if result is empty

**Examples**:
```python
>>> sanitize_filename("ewo*")
"ewo"

>>> sanitize_filename("test?file|name")
"testfilename"

>>> sanitize_filename("test  name")
"test_name"

>>> sanitize_filename("***")
"search"
```

**Used In**:
- `search_herald_character()` - Sanitizes character name before JSON filename creation
- Backend safety net for invalid characters in filenames

---

#### `search_herald_character()` Function

**Location**: `Functions/eden_scraper.py` (line ~490)  
**Purpose**: Search for characters on Eden Herald and save results to JSON

**Function Signature**:
```python
def search_herald_character(character_name, realm_filter=""):
    """
    Searches for character on Eden Herald and saves results to JSON
    
    Args:
        character_name: Character name to search (partial match supported)
        realm_filter: Realm filter ("alb", "mid", "hib", or "" for all)
        
    Returns:
        tuple: (success: bool, message: str, json_path: str)
    """
```

**Character Name Sanitization** (v0.109+):
- Input: `character_name` parameter
- Processing: `sanitize_filename(character_name)` removes invalid characters
- Output: Safe filename for JSON creation
- Benefit: Prevents "Invalid argument" errors on Windows when searching with special characters (* ? " < > | : \ /)

**Return Values**:

| Success | Return Format | Description |
|---------|--------------|-------------|
| ✅ Yes | `(True, "5 personnage(s) trouvé(s)", "/tmp/.../characters_*.json")` | Success message + JSON path |
| ❌ No | `(False, "error message", "")` | Error message + empty path |

#### Execution Flow

```
PHASE 1: Connection (5-8s)
  └─ Call _connect_to_eden_herald()
  
PHASE 2: Search URL Construction (<1ms)
  ├─ With realm: "herald?n=search&r=alb&s=PlayerName"
  └─ Without: "herald?n=search&s=PlayerName"
  
PHASE 3: Page Navigation & Load (5s)
  ├─ Navigate to search URL
  └─ Wait 5 seconds for results
  
PHASE 4: HTML Parsing & Extraction (<1s)
  ├─ Parse tables with BeautifulSoup
  ├─ Extract character data (rank, name, class, race, etc.)
  └─ Build character list
  
PHASE 5: File Management (<1s)
  ├─ Clean old JSON files in temp folder
  ├─ **Sanitize character name** (v0.109+ security feature)
  ├─ Save raw search data with sanitized filename
  └─ Save formatted characters (RETURNED PATH)
  
PHASE 6: Cleanup & Return (<1s)
  └─ Close browser (always executed via finally)
```

**Total Time**: ~11-14 seconds

#### File Output

**Location**: OS temp folder (`/tmp/EdenSearchResult/` or Windows equivalent)

**File 1 - Raw Search Data** (sanitized filename):
```
search_PlayerName_20251113_143052.json
search_ewo_20251113_143052.json        (if input was "ewo*" - sanitized)
```

**File 2 - Formatted Characters** (PRIMARY OUTPUT, sanitized filename):
```
characters_PlayerName_20251113_143052.json
characters_ewo_20251113_143052.json    (if input was "ewo*" - sanitized)
```

**Content Structure**:
```json
{
  "search_query": "PlayerName",
  "search_url": "https://eden-daoc.net/herald?n=search&s=PlayerName",
  "timestamp": "2025-11-13T14:30:52.123456",
  "characters": [
    {
      "rank": "1234",
      "name": "PlayerName (Stormur Vakten)",
      "clean_name": "PlayerName",
      "class": "Armsman",
      "race": "Briton",
      "guild": "GuildName",
      "level": "50",
      "realm_points": "1 234 567",
      "realm_rank": "Stormur Vakten",
      "realm_level": "5L2",
      "url": "https://eden-daoc.net/herald?n=player&k=PlayerName"
    }
  ]
}
```

#### Usage Examples

**Basic Search (All Realms)**:
```python
success, message, json_path = search_herald_character("PlayerName")

if success:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for char in data['characters']:
        print(f"{char['name']} - {char['class']} ({char['realm_points']} RP)")
```

**Realm-Filtered Search**:
```python
# Search only in Albion
success, message, json_path = search_herald_character("Player", realm_filter="alb")

# Search only in Midgard
success, message, json_path = search_herald_character("Player", realm_filter="mid")

# Search only in Hibernia
success, message, json_path = search_herald_character("Player", realm_filter="hib")
```

**Search with Special Characters** (v0.109+ - auto-sanitized):
```python
# Input with special characters
success, message, json_path = search_herald_character("ewo*")
# Filename created: search_ewo_20251113_143052.json (asterisk removed)

# Input with multiple invalid chars
success, message, json_path = search_herald_character("test?name|here")
# Filename created: search_testnamehere_20251113_143052.json (invalid chars removed)
```

---

### Character Update

#### `scrape_character_from_url()` Function

**Location**: `Functions/eden_scraper.py` (line ~677)  
**Purpose**: Update character data from Herald URL via targeted search

**Function Signature**:
```python
def scrape_character_from_url(character_url, cookie_manager):
    """
    Retrieves character data from Herald URL
    Uses Herald search (direct page access is bot-checked)
    
    Args:
        character_url: Herald URL (contains name in &k= parameter)
        cookie_manager: CookieManager instance
        
    Returns:
        tuple: (success: bool, data_dict: dict|None, error_message: str)
    """
```

**Return Values**:

| Success | Return Format | Description |
|---------|--------------|-------------|
| ✅ Yes | `(True, {normalized_data}, "")` | Data dict + empty error |
| ❌ No | `(False, None, "error message")` | None + error message |

#### Why Search Instead of Direct Access?

**Problem**: Direct character page access triggers bot check:
```
https://eden-daoc.net/herald?n=player&k=PlayerName → BOT CHECK (blocked)
```

**Solution**: Extract name from URL, search via Herald search:
```
URL: https://eden-daoc.net/herald?n=player&k=PlayerName
Extract: "PlayerName"
Search: https://eden-daoc.net/herald?n=search&s=PlayerName → WORKS
```

**Trade-offs**:
- ✅ Avoids bot check
- ✅ Reuses existing search infrastructure
- ⚠️ Slightly slower (search instead of direct)
- ⚠️ May return multiple matches (must filter)

#### Execution Flow

```
STEP 1: URL Parsing (<1ms)
  └─ Extract character name from &k= parameter
  
STEPS 2-7: Connection (5-8s)
  └─ Call _connect_to_eden_herald()
  
STEP 8: Search URL Construction (<1ms)
  └─ Build search URL with extracted name
  
STEP 9: Navigate to Search Page (<1s)
  
STEP 10: Wait for Page Load (5s)
  
STEP 11: Extract HTML (<1s)
  
STEP 12: Parse Search Results (<1s)
  └─ Same parsing as search_herald_character()
  
STEP 13: Format Characters (<1s)
  
STEP 14: Find Target Character (<1ms)
  ├─ Strategy 1: Exact match (case-insensitive)
  └─ Strategy 2: Fallback to first result
  
STEP 15: Normalize Data (<1ms)
  └─ Call _normalize_herald_data()
  
STEP 16: Cleanup & Return (<1s)
  └─ Close browser (always via finally)
```

**Total Time**: ~11-14 seconds

#### Data Normalization

**Input** (raw search result):
```python
{
    'rank': '1234',
    'name': 'PlayerName (Stormur Vakten)',
    'clean_name': 'PlayerName',
    'class': 'Armsman',
    'level': '50',
    'realm_points': '1 234 567',
    'realm_rank': 'Stormur Vakten',  # Herald: Title text
    'realm_level': '5L2',            # Herald: Code
}
```

**Transformations**:
1. **Realm Determination** from class name
2. **Realm Points Cleaning**: Remove spaces/commas, convert to int
3. **Level Conversion**: String → int
4. **Realm Rank Field Swap** (CRITICAL):
```python
# Herald's naming is backwards!
normalized = {
    'realm_rank': char_data.get('realm_level', '1L1'),  # Code (XLY) - SWAPPED
    'realm_title': char_data.get('realm_rank', ''),     # Title text - SWAPPED
}
```

**Output** (normalized):
```python
{
    'name': 'PlayerName (Stormur Vakten)',
    'clean_name': 'PlayerName',
    'level': 50,                 # int
    'class': 'Armsman',
    'race': 'Briton',
    'realm': 'Albion',           # ADDED
    'guild': 'GuildName',
    'realm_points': 1234567,     # int
    'realm_rank': '5L2',         # SWAPPED
    'realm_title': 'Stormur Vakten',  # SWAPPED
    'server': 'Eden',            # ADDED
    'url': '...'
}
```

#### Usage Example

```python
url = "https://eden-daoc.net/herald?n=player&k=PlayerName"
success, data, error = scrape_character_from_url(url, cookie_manager)

if success:
    print(f"Character: {data['name']}")
    print(f"Level: {data['level']}")
    print(f"Realm Rank: {data['realm_rank']} ({data['realm_title']})")
else:
    print(f"Error: {error}")
```

---

### Character Statistics

#### CharacterProfileScraper Class

**Location**: `Functions/character_profile_scraper.py` (line ~29)  
**Purpose**: Extract detailed statistics from character profile pages

**Class Architecture**:
```python
class CharacterProfileScraper:
    def __init__(self, cookie_manager=None):
        """Initialize with optional cookie manager"""
        
    def connect(self, headless=False):
        """Establish connection using _connect_to_eden_herald()"""
        
    def scrape_wealth_money(self, character_url):
        """Extract money from Wealth tab"""
        
    def scrape_rvr_captures(self, character_url):
        """Extract Tower/Keep/Relic captures"""
        
    def scrape_pvp_stats(self, character_url):
        """Extract Solo Kills/Deathblows/Kills with realm breakdown"""
        
    def scrape_pve_stats(self, character_url):
        """Extract Dragon/Legion/Epic kills"""
        
    def scrape_achievements(self, character_url):
        """Extract achievement progress"""
        
    def close(self):
        """Close browser and cleanup"""
```

#### Connection Management

**Implementation**:
```python
def connect(self, headless=False):
    from Functions.eden_scraper import _connect_to_eden_herald
    
    scraper, error_message = _connect_to_eden_herald(
        cookie_manager=self.cookie_manager,
        headless=headless
    )
    
    if not scraper:
        return False, error_message
    
    self._eden_scraper = scraper
    self.driver = scraper.driver
    return True, ""
```

**Replaces**: Old `initialize_driver()` + `load_cookies()` pattern (eliminated ~300 lines of duplication)

#### Scraping Methods

**1. Wealth Money**

**Tab**: Wealth (`&t=wealth`)

**Return**:
```python
{
    'success': bool,
    'money': str or None,  # "1234g 56s 78c"
    'error': str or None
}
```

**2. RvR Captures**

**Tab**: Characters (default)

**Return**:
```python
{
    'success': bool,
    'tower_captures': int or None,
    'keep_captures': int or None,
    'relic_captures': int or None,
    'error': str or None
}
```

**3. PvP Statistics**

**Tab**: PvP (`&t=pvp`)

**Return**:
```python
{
    'success': bool,
    'solo_kills': int,
    'solo_kills_alb': int,
    'solo_kills_hib': int,
    'solo_kills_mid': int,
    'deathblows': int,
    'deathblows_alb': int,
    'deathblows_hib': int,
    'deathblows_mid': int,
    'kills': int,
    'kills_alb': int,
    'kills_hib': int,
    'kills_mid': int,
    'error': str or None
}
```

**4. PvE Statistics**

**Tab**: PvE (`&t=pve`)

**Return**:
```python
{
    'success': bool,
    'dragon_kills': int or None,
    'legion_kills': int or None,
    'mini_dragon_kills': int or None,
    'epic_encounters': int or None,
    'epic_dungeons': int or None,
    'sobekite': int or None,
    'error': str or None
}
```

**5. Achievements**

**Tab**: Achievements (`&t=achievements`)

**Return**:
```python
{
    'success': bool,
    'achievements': [
        {
            'title': str,         # Achievement name
            'progress': str,      # "19/50"
            'current': str or None  # Current tier name
        }
    ],
    'error': str or None
}
```

#### Usage Example

```python
from Functions.character_profile_scraper import CharacterProfileScraper

scraper = CharacterProfileScraper()

try:
    # Connect
    success, error = scraper.connect(headless=False)
    if not success:
        print(f"Connection failed: {error}")
        return
    
    # Scrape all stats
    url = "https://eden-daoc.net/herald?n=player&k=PlayerName"
    
    wealth = scraper.scrape_wealth_money(url)
    rvr = scraper.scrape_rvr_captures(url)
    pvp = scraper.scrape_pvp_stats(url)
    pve = scraper.scrape_pve_stats(url)
    achievements = scraper.scrape_achievements(url)
    
    if wealth['success']:
        print(f"Money: {wealth['money']}")
    if rvr['success']:
        print(f"Towers: {rvr['tower_captures']}")
    if pvp['success']:
        print(f"Solo Kills: {pvp['solo_kills']}")
    
finally:
    scraper.close()
```

#### Performance

| Operation | Duration |
|-----------|----------|
| Connection | 5-8s (via `_connect_to_eden_herald()`) |
| Per Tab Scrape | 5-6s (navigate + wait + parse) |
| Full Profile (5 tabs) | 30-35s |
| Cleanup | <1s |

**Optimization**: Single connection reused across all tabs

---

## Wealth Management

### WealthManager Module

**Location**: `Functions/wealth_manager.py`  
**Purpose**: Retrieve total money across all realms

#### `get_realm_money()` Function

**Function Signature**:
```python
def get_realm_money(character_folder, cookie_manager=None, headless=False):
    """
    Get money values for each realm
    
    Returns:
        dict: {
            'Albion': str (money or "0"),
            'Midgard': str (money or "0"),
            'Hibernia': str (money or "0"),
            'success': bool,
            'errors': list
        }
    """
```

**Execution Flow**:
```
STEP 1: Get First Character Per Realm
  └─ Find one character (level 11+) per realm
  
STEP 2: Initialize CharacterProfileScraper
  
STEP 3: Connect to Eden Herald
  └─ Uses _connect_to_eden_herald() internally
  
STEP 4: Scrape Money for Each Realm
  ├─ Albion: scrape_wealth_money(alb_char_url)
  ├─ Midgard: scrape_wealth_money(mid_char_url)
  └─ Hibernia: scrape_wealth_money(hib_char_url)
  
STEP 5: Cleanup and Return
```

**Performance**: ~24 seconds (connection + 3 wealth scrapes)

**Character Selection Logic**:
1. Browse season folders (S3 → S2 → S1) from newest to oldest
2. For each realm: Find first character with level ≥ 11
3. If no character found: Use "0" as money value

**Why Level 11+?**: Characters below level 11 are in tutorial zone and don't have representative wealth.

#### `get_first_character_per_realm()` Function

**Function Signature**:
```python
def get_first_character_per_realm(character_folder):
    """
    Get first available character for each realm
    
    Returns:
        dict: {
            'Albion': {'name': str, 'url': str} or None,
            'Midgard': {'name': str, 'url': str} or None,
            'Hibernia': {'name': str, 'url': str} or None
        }
    """
```

#### Usage Example

```python
from Functions.wealth_manager import get_realm_money

result = get_realm_money('Characters/')

if result['success']:
    print(f"Albion: {result['Albion']}")
    print(f"Midgard: {result['Midgard']}")
    print(f"Hibernia: {result['Hibernia']}")
else:
    print(f"Errors: {result['errors']}")
```

---

## UI Integration

### Button State Management

#### Problem: Chrome Profile Conflicts

**Scenario**: Two Selenium instances accessing same Chrome profile simultaneously:
1. Startup validation thread (automatic Herald check)
2. User-triggered operation (manual update/search)

**Error**: Chrome profile locked, browser freezes, cookies fail to load

**Solution**: Disable Herald buttons during validation to prevent conflicts

#### Architecture

**Design Principles**:
1. **Proactive UI State** - Disable buttons BEFORE user can click
2. **Visual Feedback** - Tooltips explain why disabled
3. **Instant Reactivity** - State updates immediately when validation completes
4. **Thread-Safe** - No race conditions

#### State Management Flow

```
App Startup
  ↓
create_context_menu() → Create menu action
  ↓
check_eden_status() → Start validation thread
  ↓                   eden_validation_in_progress = True
  ↓
_update_herald_buttons_state() → DISABLE all Herald buttons
  ↓                               Set tooltips "⏳ Validation en cours..."
  ↓
[Validation Running - Buttons DISABLED]
  ↓
update_eden_status(result) ← Thread sends result signal
  ↓                          eden_validation_in_progress = False
  ↓
_update_herald_buttons_state() → ENABLE all Herald buttons
  ↓                               Restore normal tooltips
  ↓
[Validation Complete - Buttons ENABLED]
```

#### Flag-Based Validation Tracking

**Why Not `thread.isRunning()`?**

**Problem**: Thread's `finished` signal emitted AFTER `status_updated`, causing 2-3 second delay.

**Solution**: Use internal flag set immediately when result arrives:

```python
# OLD (Slow)
is_validation_running = self.eden_status_thread.isRunning()  # Still True for 2-3s

# NEW (Instant)
is_validation_running = getattr(self, 'eden_validation_in_progress', False)
```

**Timeline Comparison**:

| Event | Old `isRunning()` | New Flag |
|-------|------------------|----------|
| Validation starts | True | True |
| Result received | True ⚠️ | False ✅ |
| Thread cleanup | True ⚠️ | False ✅ |
| **UI Update Delay** | **2-3 seconds** | **Instant** |

#### Implementation

**File**: `Functions/ui_manager.py`

**1. Start Validation**:
```python
def check_eden_status(self):
    # Mark validation as in progress
    self.eden_validation_in_progress = True
    
    # Disable buttons immediately
    self.refresh_button.setEnabled(False)
    self.search_button.setEnabled(False)
    
    # Start validation thread
    self.eden_status_thread = EdenStatusThread(cookie_manager)
    self.eden_status_thread.status_updated.connect(self.update_eden_status)
    self.eden_status_thread.start()
    
    # Update Herald buttons state
    self._update_herald_buttons_state()
```

**2. Receive Validation Result**:
```python
def update_eden_status(self, accessible, message):
    # Mark validation FINISHED immediately
    self.eden_validation_in_progress = False
    
    if accessible:
        self.eden_status_label.setText("✅ Herald accessible")
        self.refresh_button.setEnabled(True)
    else:
        self.eden_status_label.setText(f"❌ {message}")
    
    # Update buttons IMMEDIATELY
    self._update_herald_buttons_state()
```

**3. Update Button States**:
```python
def _update_herald_buttons_state(self):
    from Functions.language_manager import lang
    
    is_validation_running = getattr(self, 'eden_validation_in_progress', False)
    
    # Context menu action
    if hasattr(self, 'update_from_herald_action'):
        self.update_from_herald_action.setEnabled(not is_validation_running)
        if is_validation_running:
            tooltip = lang.get("herald_buttons.validation_in_progress")
            self.update_from_herald_action.setToolTip(tooltip)
    
    # Search button
    if hasattr(self, 'search_button'):
        if is_validation_running:
            self.search_button.setEnabled(False)
            self.search_button.setToolTip(lang.get("herald_buttons.validation_in_progress"))
        else:
            self.search_button.setEnabled(True)
```

#### Protected Operations

All Herald operations protected:

| Entry Point | File | Method | UI Element |
|-------------|------|--------|------------|
| Character Update (Context) | `main.py` | `update_character_from_herald()` | Right-click menu |
| Character Update (Sheet) | `UI/dialogs.py` | `update_from_herald()` | Character Sheet button |
| Herald Search | `main.py` | `open_herald_search()` | Search button |
| Stats Update | `UI/dialogs.py` | `update_rvr_stats()` | Stats button |

**Protection Pattern**:
```python
def update_character_from_herald(self):
    # Silent return if validation running
    if hasattr(self.ui_manager, 'eden_validation_in_progress'):
        if self.ui_manager.eden_validation_in_progress:
            return  # No popup, button disabled with tooltip
    
    # Proceed with update...
```

#### Character Sheet Integration

**File**: `UI/dialogs.py` - `CharacterSheetWindow`

**Initialization**:
```python
def __init__(self, parent, character_data):
    # Connect to validation lifecycle
    if hasattr(parent, 'ui_manager'):
        ui_manager = parent.ui_manager
        if hasattr(ui_manager, 'eden_status_thread'):
            ui_manager.eden_status_thread.finished.connect(
                self._update_herald_buttons_state
            )
        
        # Initial state check
        QTimer.singleShot(0, self._update_herald_buttons_state)
```

**Button State Update**:
```python
def _update_herald_buttons_state(self):
    main_window = self.parent()
    is_validation_running = getattr(
        main_window.ui_manager, 
        'eden_validation_in_progress', 
        False
    )
    
    if hasattr(self, 'update_herald_button'):
        if is_validation_running:
            self.update_herald_button.setEnabled(False)
            self.update_herald_button.setToolTip(
                lang.get("herald_buttons.validation_in_progress")
            )
        else:
            self.update_herald_button.setEnabled(True)
```

#### Internationalization

**Translation Keys** (`Language/{fr,en,de}.json`):
```json
{
  "herald_buttons": {
    "validation_in_progress": "⏳ Validation Eden en cours... Veuillez patienter"
  }
}
```

| Language | Translation |
|----------|-------------|
| 🇫🇷 French | "⏳ Validation Eden en cours... Veuillez patienter" |
| 🇬🇧 English | "⏳ Eden validation in progress... Please wait" |
| 🇩🇪 German | "⏳ Eden-Validierung läuft... Bitte warten" |

---

### Herald Validation

#### Automatic Startup Validation

**Trigger**: Application launch  
**Duration**: 2-4 seconds  
**Purpose**: Verify Herald connectivity before user operations

**Execution**:
```python
def check_eden_status(self):
    self.eden_validation_in_progress = True
    self.eden_status_thread = EdenStatusThread(cookie_manager)
    self.eden_status_thread.status_updated.connect(self.update_eden_status)
    self.eden_status_thread.start()
```

**Thread Implementation** (`EdenStatusThread`):
```python
class EdenStatusThread(QThread):
    status_updated = Signal(bool, str)
    
    def run(self):
        accessible, message = self.cookie_manager.test_eden_connection()
        self.status_updated.emit(accessible, message)
```

**Status Display**:
- ✅ **Success**: "✅ Herald accessible"
- ❌ **No Cookies**: "❌ Aucun cookie configuré"
- ❌ **Expired**: "❌ Les cookies ont expiré"
- ⚠️ **Validating**: "⏳ Vérification en cours..."

#### Performance Impact

**Timing** (with optimizations):

| Scenario | Time |
|----------|------|
| First validation (no cache) | 3-4s |
| Repeated validation (<10s) | <0.1s (cached) |
| Button disable | 5ms |
| Button re-enable | <100ms |

**Old Approach** (waiting for `isRunning() == False`):
- Button re-enable delay: 2-3 seconds AFTER result ❌

**New Approach** (flag-based):
- Button re-enable delay: IMMEDIATE with result ✅

#### Herald URL Validation (Phase 8)

**Module**: `Functions/herald_url_validator.py`

**Purpose**: Handle real-time Herald URL validation and browser interaction

**Functions**:

##### 1. herald_url_on_text_changed()
**Signature**: `herald_url_on_text_changed(parent_window, text: str) -> None`

**Purpose**: Validate Herald URL field and update button states in real-time

**Behavior**:
- Called every time user types in the Herald URL field
- Checks if Herald scraping is active (return if true)
- Enables `update_rvr_button` if URL is valid (non-empty)
- Sets tooltip using `lang.get()` for translations

**Integration Point**:
```python
# In CharacterSheetWindow.__init__
self.herald_url_edit.textChanged.connect(
    lambda text: herald_url_on_text_changed(self, text)
)
```

##### 2. herald_url_open_url()
**Signature**: `herald_url_open_url(parent_window) -> None`

**Purpose**: Open Herald URL in browser with authentication cookies

**Behavior**:
- Validates URL is not empty (shows warning if missing)
- Adds protocol (`https://`) if not present
- Launches browser in separate thread to prevent UI blocking
- Uses `CookieManager` for authenticated session
- Shows error dialog if browser launch fails

**Error Handling**:
- Missing URL: Warning dialog with `lang.get()`
- Launch failure: Critical dialog with error message
- Thread errors: Logged but not raised (thread-safe)

**Integration Point**:
```python
# In CharacterSheetWindow
self.open_herald_button.clicked.connect(lambda: herald_url_open_url(self))
```

##### 3. _herald_url_open_in_thread()
**Signature**: `_herald_url_open_in_thread(url: str) -> None`

**Purpose**: Internal worker function for opening URL in separate thread

**Behavior**:
- Runs in daemon thread (non-blocking)
- Initializes `CookieManager`
- Calls `open_url_with_cookies_subprocess()`
- Logs errors without raising exceptions (thread-safe)

**Error Handling**:
- Browser errors: Logged as warning
- Cookie errors: Logged as error
- Never raises exceptions (safe for background thread)

##### 4. herald_url_update_button_states()
**Signature**: `herald_url_update_button_states(parent_window) -> None`

**Purpose**: Manage button enable/disable states based on validation and scraping

**Behavior**:
- Checks if Eden validation is running
- Disables buttons if validation in progress
- Disables `update_rvr_button` if no URL configured
- Disables buttons if Herald scraping is active
- Sets appropriate tooltips for each state

**State Matrix**:
| Validation | URL | Scraping | Update Herald | Update RvR |
|------------|-----|----------|---------------|-----------|
| Running | - | - | Disabled | Disabled |
| Done | No | - | Enabled | Disabled |
| Done | Yes | No | Enabled | Enabled |
| Done | Yes | Yes | Enabled | Disabled |

**Integration Point**:
```python
# Called from multiple places:
# 1. After Eden validation completes
# 2. When Herald URL changes
# 3. Before/after Herald scraping
# 4. When Herald scraping flag changes
```

**Initialization**: `Functions/herald_url_validator.py` (236 lines)

**Quality Standards**:
- ✅ All strings use `lang.get()` for i18n
- ✅ No hardcoded text in English or French
- ✅ All comments in English
- ✅ Type hints for all parameters
- ✅ Comprehensive docstrings with examples
- ✅ Proper error handling with logging
- ✅ Thread-safe execution

---

## Error Handling

### Exception Safety

**Guarantees**:
- ✅ Browser always closed via `finally` block
- ✅ Functions never raise exceptions (always return tuple/dict)
- ✅ Detailed error logging
- ✅ Descriptive error messages to user

**Pattern**:
```python
try:
    # All operations
    return success_result
except Exception as e:
    logger.error(f"Error: {e}")
    logger.error(f"Stacktrace: {traceback.format_exc()}")
    return error_result
finally:
    # Cleanup ALWAYS happens
    if scraper:
        scraper.close()
```

### Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "No cookies found" | Cookie file doesn't exist | Generate or import cookies |
| "Cookies have expired" | Cookies too old (>24-48h) | Regenerate cookies |
| "Unable to initialize browser" | No Chrome/Edge/Firefox | Install compatible browser |
| "Unable to load cookies" | Bot check detected | Verify `headless=False` |
| "Driver not initialized" | Called scrape before connect | Call `connect()` first |
| "Not connected to Herald" | Invalid/expired cookies | Regenerate cookies |

### Debug Features

**HTML Dump** (Settings > Debug > Debug HTML Herald):
- **`debug_test_connection.html`**: Connection test page source
- **`debug_herald_page.html`**: Herald scraping page source
- **`debug_pvp_missing.html`**: PvP stats when missing
- **`debug_pve_missing.html`**: PvE stats when missing

**Location**: `Logs/` folder

**When to Enable**:
- Investigating connection failures
- Diagnosing scraping/parsing issues
- Verifying HTML structure changes
- Troubleshooting authentication

---

## Performance Optimization

### Optimization Summary

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Connection test | 7-8s | 3-4s | 50% faster |
| Repeated tests | 7-8s | <0.1s | 99%+ faster |
| Button re-enable | 2-3s delay | Instant | 100% faster |

### Cache Strategy

**Result Caching**:
```python
_test_cache = {'result': None, 'timestamp': None}
_CACHE_DURATION_SECONDS = 10
```

**Benefits**:
- Instant response for repeated validation
- Reduces Herald server load
- Improves user experience

**Cache Invalidation**:
- Automatic after 10 seconds
- Manual via cache clear

### Wait Time Reduction

**Homepage Load**: 1s → 0.5s (50% reduction)  
**Cookie Injection**: 1s → 0.3s (70% reduction)  
**Page Refresh**: 2s → 1s (50% reduction)  
**Herald Navigation**: 3s → 1.5s (50% reduction)

**Total Reduction**: 7s → 3.3s (53% reduction)

### Future Optimizations

**Planned**:
1. **Parallel Driver Init** - Launch at startup (background)
2. **Connection Pooling** - Keep driver alive between operations
3. **Smart Wait Reduction** - Use `WebDriverWait` with conditions

**Note**: Initial `WebDriverWait` implementation caused blocking issues and was reverted.

---

## Testing & Troubleshooting

### Testing Checklist

**Unit Tests**:
- [ ] `_connect_to_eden_herald()` success with valid cookies
- [ ] `_connect_to_eden_herald()` failure with no cookies
- [ ] `_connect_to_eden_herald()` failure with expired cookies
- [ ] `search_herald_character()` with realm filter
- [ ] `scrape_character_from_url()` URL parsing
- [ ] `CharacterProfileScraper.connect()` delegation
- [ ] `eden_validation_in_progress` flag lifecycle

**Integration Tests**:
- [ ] Full connection → search → close workflow
- [ ] Startup validation disables buttons
- [ ] Button re-enable on validation complete
- [ ] Character sheet button state during validation
- [ ] Cache effectiveness (repeated tests)

**Manual Testing**:
```
Test 1: Startup Validation
1. Launch application
2. Verify "⏳ Vérification en cours..." appears
3. Hover over Search button → Verify tooltip
4. Wait for validation (2-4s)
5. Verify "✅ Herald accessible" + buttons enabled

Test 2: Context Menu During Validation
1. Launch application
2. Immediately right-click character
3. Verify "Update from Herald" grayed out
4. Wait for validation complete
5. Right-click again → Verify enabled

Test 3: Chrome Profile Isolation
1. Open user's personal Chrome browser
2. Generate cookies via application
3. Verify ChromeProfile/ created in AppData
4. Verify no interference with personal browser

Test 4: Performance Logging
1. Enable: config.json → "enable_performance_logs": true
2. Test connection
3. Verify Logs/eden_performance_*.log created
4. Check timing breakdown
```

### Troubleshooting Guide

#### Issue: "Buttons stay disabled forever"

**Symptoms**: After validation, buttons never re-enable

**Possible Causes**:
1. `eden_validation_in_progress` never set to `False`
2. `_update_herald_buttons_state()` not called
3. Signal connection missing

**Debug**:
```python
def update_eden_status(self, accessible, message):
    print(f"DEBUG: Setting flag to False")  # Should print
    self.eden_validation_in_progress = False
    print(f"DEBUG: Calling _update_herald_buttons_state")  # Should print
    self._update_herald_buttons_state()
```

#### Issue: "Context menu action not grayed out"

**Symptoms**: Right-click menu shows enabled action during validation

**Possible Causes**:
1. `update_from_herald_action` doesn't exist yet
2. `show_context_menu()` not calling `_update_herald_buttons_state()`
3. QAction doesn't refresh visually

**Solution**: Ensure `show_context_menu()` calls update before `exec()`:
```python
def show_context_menu(self, position):
    self._update_herald_buttons_state()  # Update before showing
    self.context_menu.exec(...)
```

#### Issue: "Chrome profile locked"

**Symptoms**: "Profile cannot be opened by multiple processes"

**Cause**: Two Selenium instances accessing same profile

**Solution**: Wait for validation to complete before manual operation (automatic via button state)

#### Issue: "Slow connection test"

**Symptoms**: Connection test takes >7 seconds

**Investigation**:
1. Enable performance logging
2. Check `eden_performance_*.log`
3. Identify bottleneck:
   - STEP 6 >5s: Slow system/antivirus
   - STEP 7/10 >3s: Slow internet
   - STEP 3 >2s: First import (expected)

#### Issue: "Missing statistics"

**Symptoms**: `success: False`, `error: "Some statistics not found"`

**Debug Steps**:
1. Check debug HTML file (e.g., `debug_pvp_missing.html`)
2. Verify Herald page structure hasn't changed
3. Check log file for parsing errors

**Common Causes**:
- Herald HTML structure changed
- Character has no data for that stat
- Page load timeout too short

---

## Version History

### v0.108 (Current)

**Eden Herald System**:
- ✅ Centralized `_connect_to_eden_herald()` function
- ✅ Dedicated Chrome profile in AppData
- ✅ Automatic cookie migration from Configuration/
- ✅ Multi-OS path support (Windows/Linux/macOS)
- ✅ Button state management (prevent Chrome conflicts)
- ✅ Performance caching (10-second cache)
- ✅ Reduced wait times (7s → 3.3s)
- ✅ Character sheet integration
- ✅ WealthManager realm money totals
- ✅ Unified "Clean Eden" button in Settings

**Changed**:
- 🔄 Cookies path: `Configuration/` → `AppData/Eden/`
- 🔄 Chrome profile: None → Dedicated profile
- 🔄 Button states: Reactive popups → Proactive disable
- 🔄 Validation tracking: `isRunning()` → Flag-based (instant)
- 🔄 Wait times: 7s → 3.3s (53% reduction)

**Migration**:
- 🔁 Automatic cookie migration on first startup
- 🔁 Backup created as `.pkl.migrated`
- 🔁 No user action required

### v0.107 (Previous)

**Features**:
- ❌ Separate `initialize_driver()` + `load_cookies()` in each scraper
- ❌ Cookies in `Configuration/` folder
- ❌ No Chrome profile (used default)
- ❌ QMessageBox warnings for conflicts
- ❌ 7-8 second connection times

---

## Related Functions Reference

### Connection Functions
- **`_connect_to_eden_herald()`** - Core connection (internal)
- **`test_eden_connection()`** - Connection testing with cache
- **`CookieManager._try_chrome()`** - Chrome profile setup

### Scraping Functions
- **`search_herald_character()`** - Character search
- **`scrape_character_from_url()`** - Character update
- **`CharacterProfileScraper.connect()`** - Stats scraper connection
- **`CharacterProfileScraper.scrape_wealth_money()`** - Wealth tab
- **`CharacterProfileScraper.scrape_rvr_captures()`** - RvR stats
- **`CharacterProfileScraper.scrape_pvp_stats()`** - PvP stats
- **`CharacterProfileScraper.scrape_pve_stats()`** - PvE stats
- **`CharacterProfileScraper.scrape_achievements()`** - Achievements

### Wealth Functions
- **`get_realm_money()`** - Realm-wide money totals
- **`get_first_character_per_realm()`** - Character selection

### UI Functions
- **`check_eden_status()`** - Startup validation
- **`update_eden_status()`** - Validation result handler
- **`_update_herald_buttons_state()`** - Button state manager
- **`show_context_menu()`** - Context menu display

### Path Functions
- **`get_user_data_dir()`** - AppData path (multi-OS)
- **`get_chrome_profile_path()`** - Chrome profile location
- **`get_eden_cookies_path()`** - Cookie file location
- **`get_eden_data_dir()`** - Eden folder location

---

## Summary

### Key Improvements

**Architecture**:
- ✅ Centralized connection logic (single source of truth)
- ✅ Chrome profile isolation (no user browser interference)
- ✅ Multi-OS compatibility (Windows/Linux/macOS)
- ✅ PyInstaller --onefile ready

**Performance**:
- ⚡ 50% faster connection tests (7-8s → 3-4s)
- ⚡ 99% faster repeated tests (cache)
- ⚡ Instant button re-enable (flag-based)

**User Experience**:
- 🎯 No unexpected error dialogs
- 📖 Clear tooltips explain disabled states
- ⚡ Instant visual feedback
- 🌐 Fully translated (FR/EN/DE)

**Reliability**:
- 🔒 Chrome profile conflict prevention
- 🛡️ Exception safety (always cleanup)
- 📊 Optional performance logging
- 🐛 Debug HTML dumps

**Maintainability**:
- 📝 Single connection function (~300 lines removed)
- 🧪 Testable flag-based states
- 📋 Comprehensive documentation
- 🔍 Clear log messages

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Author**: DAOC Character Manager Team  
**Status**: ✅ Production Ready

---

## Document Consolidation Notes

**Original Files Merged**:
1. `CHARACTER_PROFILE_SCRAPER_EN.md` (686 lines) - Profile scraping + URL update
2. `CHARACTER_SEARCH_SCRAPER_EN.md` (995 lines) - Herald search function
3. `CHARACTER_STATS_SCRAPER_EN.md` (1384 lines) - Stats scraper + WealthManager
4. `CHROME_PROFILE_TECHNICAL_EN.md` (542 lines) - Chrome profile in AppData
5. `CONNECT_TO_EDEN_HERALD_EN.md` (585 lines) - Core connection function
6. `HERALD_BUTTONS_STATE_MANAGEMENT_EN.md` (732 lines) - UI button states
7. `PERFORMANCE_OPTIMIZATION_EN.md` (274 lines) - Connection performance

**Total Lines Consolidated**: ~5,198 lines → Single comprehensive document

**Structure**: Follows ARMORY_TECHNICAL_DOCUMENTATION.md template with logical sections
