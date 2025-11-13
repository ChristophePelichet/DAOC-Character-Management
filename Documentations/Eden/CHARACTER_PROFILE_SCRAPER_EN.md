# CharacterProfileScraper - Technical Documentation

## Class Overview

**Name**: `CharacterProfileScraper`  
**Location**: `Functions/character_profile_scraper.py` (line ~29)  
**Purpose**: Specialized scraper for extracting detailed statistics from character profile pages  
**Category**: Profile scraping class for RvR, PvP, PvE, Wealth, and Achievement data

---

## Table of Contents

1. [Class Architecture](#class-architecture)
2. [Initialization](#initialization)
3. [Connection Management](#connection-management)
4. [Scraping Methods](#scraping-methods)
   - [scrape_wealth_money()](#scrape_wealth_money)
   - [scrape_rvr_captures()](#scrape_rvr_captures)
   - [scrape_pvp_stats()](#scrape_pvp_stats)
   - [scrape_pve_stats()](#scrape_pve_stats)
   - [scrape_achievements()](#scrape_achievements)
5. [Error Handling](#error-handling)
6. [Usage Examples](#usage-examples)
7. [Performance Characteristics](#performance-characteristics)

---

## Class Architecture

### Design Philosophy

**Purpose**: Extract detailed character statistics from Eden Herald profile pages  
**Separation of Concerns**: Does NOT modify existing `eden_scraper.py` functionality  
**Connection Strategy**: Reuses `_connect_to_eden_herald()` for consistency

```
┌─────────────────────────────────────────────────────────┐
│         CharacterProfileScraper                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Attributes:                                            │
│    ├─ cookie_manager: CookieManager                    │
│    ├─ driver: WebDriver                                │
│    └─ _eden_scraper: EdenScraper                       │
│                                                         │
│  Connection:                                            │
│    └─ connect() → Uses _connect_to_eden_herald()       │
│                                                         │
│  Scraping Methods:                                      │
│    ├─ scrape_wealth_money()      [Money value]         │
│    ├─ scrape_rvr_captures()      [Tower/Keep/Relic]    │
│    ├─ scrape_pvp_stats()         [Solo/Deathblows/Kills]│
│    ├─ scrape_pve_stats()         [Dragon/Legion/Epic]  │
│    └─ scrape_achievements()      [Achievement progress]│
│                                                         │
│  Cleanup:                                               │
│    └─ close() → Closes EdenScraper & driver            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Initialization

### `__init__(cookie_manager=None)`

**Purpose**: Initialize the profile scraper instance

```python
def __init__(self, cookie_manager=None):
    """
    Initialize the character profile scraper
    
    Args:
        cookie_manager: CookieManager instance for authentication 
                       (optional, created if None)
    """
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cookie_manager` | `CookieManager` | ❌ No | `None` | Cookie manager for Herald authentication |

**Behavior**:
- If `cookie_manager` is `None`: Creates new `CookieManager()` instance
- If provided: Uses existing cookie manager

**Attributes Initialized**:

| Attribute | Initial Value | Description |
|-----------|---------------|-------------|
| `self.cookie_manager` | `cookie_manager` or new | Cookie authentication manager |
| `self.driver` | `None` | WebDriver instance (set by `connect()`) |
| `self._eden_scraper` | `None` | EdenScraper instance (set by `connect()`) |

**Example**:

```python
from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager

# Option 1: Let scraper create cookie manager
scraper = CharacterProfileScraper()

# Option 2: Provide existing cookie manager
cookie_mgr = CookieManager()
scraper = CharacterProfileScraper(cookie_manager=cookie_mgr)
```

---

## Connection Management

### `connect(headless=False)`

**Purpose**: Establish connection to Eden Herald using centralized connection function

**Replaces**: Old `initialize_driver()` + `load_cookies()` pattern (eliminated ~300 lines of duplication)

```python
def connect(self, headless=False):
    """
    Establish connection to Eden Herald using centralized connection function.
    
    Args:
        headless: Whether to run browser in headless mode 
                 (False recommended for bot check avoidance)
        
    Returns:
        tuple: (success: bool, error_message: str)
               If success: (True, "")
               If failure: (False, "error description")
    """
```

**Execution Flow**:

```
┌──────────────────────────────────────────────────────────────────┐
│                    connect(headless=False)                       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Import Centralized Function                             │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ from Functions.eden_scraper import _connect_to_eden_herald  │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Call Centralized Connection (5-8s)                      │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ scraper, error_message = _connect_to_eden_herald(           │ │
│ │     cookie_manager=self.cookie_manager,                      │ │
│ │     headless=headless                                        │ │
│ │ )                                                             │ │
│ │                                                               │ │
│ │ Performs:                                                     │ │
│ │   ├─ Cookie verification                                     │ │
│ │   ├─ Browser initialization                                  │ │
│ │   ├─ Cookie loading (1s + 2s + 2s)                           │ │
│ │   └─ Herald authentication test                              │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Connected?      │
                    └─────────┬─────────┘
                         Yes  │  No
                              │  └──────> Return (False, error_message)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Store Scraper & Driver                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ self._eden_scraper = scraper                                 │ │
│ │ self.driver = scraper.driver                                 │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Return Success                                          │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Return (True, "")                                            │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

TOTAL TIME: 5-8 seconds (delegated to _connect_to_eden_herald())
```

**Returns**:

| Index | Type | Description |
|-------|------|-------------|
| `[0]` | `bool` | `True` = Connected, `False` = Failed |
| `[1]` | `str` | Error message (empty string if success) |

**Example**:

```python
scraper = CharacterProfileScraper()
success, error = scraper.connect(headless=False)

if success:
    print("✅ Connected to Herald")
    # Proceed with scraping
else:
    print(f"❌ Connection failed: {error}")
```

---

### `close()`

**Purpose**: Clean up resources by closing browser and scraper

**Behavior**:
- Prefers closing `_eden_scraper` (if available) for consistency
- Fallback: Closes `driver` directly if `_eden_scraper` not set
- Always sets attributes to `None` after cleanup

```python
def close(self):
    """Close the WebDriver cleanly"""
    if self._eden_scraper:
        try:
            self._eden_scraper.close()
            log_with_action(profile_logger, "info", "EdenScraper closed", action="CLEANUP")
        except Exception as e:
            log_with_action(profile_logger, "warning", f"Error closing scraper: {e}", action="CLEANUP")
        finally:
            self._eden_scraper = None
            self.driver = None
    elif self.driver:
        # Fallback: close driver directly if not using EdenScraper
        try:
            self.driver.quit()
            log_with_action(profile_logger, "info", "Driver closed directly", action="CLEANUP")
        except Exception as e:
            log_with_action(profile_logger, "warning", f"Error closing driver: {e}", action="CLEANUP")
        finally:
            self.driver = None
```

**Example**:

```python
scraper = CharacterProfileScraper()
try:
    success, error = scraper.connect()
    # ... scraping operations ...
finally:
    scraper.close()  # Always cleanup
```

---

## Scraping Methods

### Common Pattern: All Scraping Methods

**Shared Characteristics**:
1. ✅ Check if `driver` is initialized
2. ✅ Navigate to specific tab (via `&t=` URL parameter)
3. ✅ Wait 5 seconds for page load
4. ✅ Parse HTML with BeautifulSoup
5. ✅ Check for "Herald not available" error
6. ✅ Extract data from tables/divs
7. ✅ Return structured dict with `success`, data fields, and `error`

---

### scrape_wealth_money()

**Purpose**: Extract money value from Wealth tab

**Tab**: Wealth (`&t=wealth`)

```python
def scrape_wealth_money(self, character_url):
    """
    Scrape the Money value from the Wealth tab of a character profile
    
    Args:
        character_url: Full URL to character profile 
                      (e.g., https://eden-daoc.net/herald?n=player&k=CharName)
        
    Returns:
        dict: {
            'success': bool,
            'money': str or None,  # Money value (e.g., "1234g 56s 78c")
            'error': str or None
        }
    """
```

**Execution Flow**:

```
1. Add &t=wealth parameter to URL
2. Navigate to wealth page
3. Wait 5 seconds
4. Parse HTML → Find div#player_content
5. Search for "Money" label in table cells
6. Extract value from adjacent cell or same cell (after colon)
7. Validate value contains 'g', 's', 'c' or is numeric
8. Return {success, money, error}
```

**Example**:

```python
scraper = CharacterProfileScraper()
scraper.connect()

url = "https://eden-daoc.net/herald?n=player&k=PlayerName"
result = scraper.scrape_wealth_money(url)

if result['success']:
    print(f"Money: {result['money']}")
    # Output: Money: 1234g 56s 78c
else:
    print(f"Error: {result['error']}")
```

**Possible Money Formats**:
- `"1234g 56s 78c"` - Full format
- `"123g 45s"` - No copper
- `"56g"` - Only gold
- `"123456"` - Raw copper value

---

### scrape_rvr_captures()

**Purpose**: Extract RvR capture statistics from default Characters tab

**Tab**: Characters (default, no `&t=` parameter)

```python
def scrape_rvr_captures(self, character_url):
    """
    Scrape RvR capture statistics from the Characters tab (default view)
    
    Returns:
        dict: {
            'success': bool,
            'tower_captures': int or None,
            'keep_captures': int or None,
            'relic_captures': int or None,
            'error': str or None
        }
    """
```

**Execution Flow**:

```
1. Remove any &t= parameter (use default Characters tab)
2. Navigate to character page
3. Wait 5 seconds
4. Parse HTML → Find div#player_content
5. Find all <td> cells
6. Look for labels: "Tower Captures", "Keep Captures", "Relic Captures"
7. Extract value from next cell (i+1)
8. Clean numbers (remove spaces, commas, \xa0)
9. Convert to int
10. Return {success, tower_captures, keep_captures, relic_captures, error}
```

**HTML Structure**:

```html
<div id="player_content">
  <table>
    <tr>
      <td>Tower Captures</td>
      <td>123</td>
    </tr>
    <tr>
      <td>Keep Captures</td>
      <td>45</td>
    </tr>
    <tr>
      <td>Relic Captures</td>
      <td>6</td>
    </tr>
  </table>
</div>
```

**Example**:

```python
result = scraper.scrape_rvr_captures(character_url)

if result['success']:
    print(f"Towers: {result['tower_captures']}")
    print(f"Keeps: {result['keep_captures']}")
    print(f"Relics: {result['relic_captures']}")
    # Output:
    # Towers: 123
    # Keeps: 45
    # Relics: 6
```

---

### scrape_pvp_stats()

**Purpose**: Extract PvP statistics with realm breakdown from PvP tab

**Tab**: PvP (`&t=pvp`)

```python
def scrape_pvp_stats(self, character_url):
    """
    Scrape PvP statistics from the PvP tab
    
    Returns:
        dict: {
            'success': bool,
            'solo_kills': int or None,
            'solo_kills_alb': int or None,
            'solo_kills_hib': int or None,
            'solo_kills_mid': int or None,
            'deathblows': int or None,
            'deathblows_alb': int or None,
            'deathblows_hib': int or None,
            'deathblows_mid': int or None,
            'kills': int or None,
            'kills_alb': int or None,
            'kills_hib': int or None,
            'kills_mid': int or None,
            'error': str or None
        }
    """
```

**Execution Flow**:

```
1. Add &t=pvp parameter to URL
2. Navigate to PvP page
3. Wait 5 seconds
4. Parse HTML → Find div#player_content
5. Find all <td> cells with class="allbg2 med bold" (labels)
6. For each label ("Solo Kills", "Deathblows", "Kills"):
   - Extract Albion value (cell i+2)
   - Extract Hibernia value (cell i+3)
   - Extract Midgard value (cell i+4)
   - Extract Total value (cell i+5)
7. Clean numbers and convert to int
8. Return structured dict with all values
```

**HTML Structure**:

```html
<div id="player_content">
  <table>
    <tr>
      <td class="allbg2 med bold">Solo Kills</td>
      <td></td> <!-- Empty cell -->
      <td>123</td> <!-- Albion -->
      <td>456</td> <!-- Hibernia -->
      <td>789</td> <!-- Midgard -->
      <td>1368</td> <!-- Total -->
    </tr>
    <tr>
      <td class="allbg2 med bold">Deathblows</td>
      <td></td>
      <td>234</td>
      <td>567</td>
      <td>890</td>
      <td>1691</td>
    </tr>
    <tr>
      <td class="allbg2 med bold">Kills</td>
      <td></td>
      <td>345</td>
      <td>678</td>
      <td>901</td>
      <td>1924</td>
    </tr>
  </table>
</div>
```

**Example**:

```python
result = scraper.scrape_pvp_stats(character_url)

if result['success']:
    print(f"Solo Kills: {result['solo_kills']} (Alb: {result['solo_kills_alb']}, Hib: {result['solo_kills_hib']}, Mid: {result['solo_kills_mid']})")
    print(f"Deathblows: {result['deathblows']} (Alb: {result['deathblows_alb']}, Hib: {result['deathblows_hib']}, Mid: {result['deathblows_mid']})")
    print(f"Kills: {result['kills']} (Alb: {result['kills_alb']}, Hib: {result['kills_hib']}, Mid: {result['kills_mid']})")
    # Output:
    # Solo Kills: 1368 (Alb: 123, Hib: 456, Mid: 789)
    # Deathblows: 1691 (Alb: 234, Hib: 567, Mid: 890)
    # Kills: 1924 (Alb: 345, Hib: 678, Mid: 901)
```

**Realm Breakdown**:
- **Solo Kills**: Player killed enemy alone (no group)
- **Deathblows**: Player dealt killing blow (group may have assisted)
- **Kills**: Player participated in kill (any contribution)

---

### scrape_pve_stats()

**Purpose**: Extract PvE statistics from PvE tab

**Tab**: PvE (`&t=pve`)

```python
def scrape_pve_stats(self, character_url):
    """
    Scrape PvE statistics from character profile
    
    Returns:
        dict: {
            'success': bool,
            'dragon_kills': int or None,
            'legion_kills': int or None,
            'mini_dragon_kills': int or None,
            'epic_encounters': int or None,
            'epic_dungeons': int or None,
            'sobekite': int or None,
            'error': str or None
        }
    """
```

**Execution Flow**:

```
1. Add &t=pve parameter to URL
2. Navigate to PvE page
3. Wait 5 seconds
4. Parse HTML → Find div#player_content
5. Find table with class="pvestats"
6. Find all <td> cells with class="bold" (labels)
7. For each label:
   - "Dragon Kills" → Extract value from next cell
   - "Legion Kills" → Extract value from next cell
   - "Mini Dragon Kills" → Extract value from next cell
   - "Epic Encounters" → Extract value from next cell
   - "Epic Dungeons" → Extract value from next cell
   - "Sobekite" → Extract value from next cell
8. Clean numbers and convert to int
9. Return structured dict
```

**HTML Structure**:

```html
<div id="player_content">
  <table class="pvestats">
    <tr>
      <td class="bold">Dragon Kills</td>
      <td>12</td>
    </tr>
    <tr>
      <td class="bold">Legion Kills</td>
      <td>34</td>
    </tr>
    <tr>
      <td class="bold">Mini Dragon Kills</td>
      <td>56</td>
    </tr>
    <tr>
      <td class="bold">Epic Encounters</td>
      <td>78</td>
    </tr>
    <tr>
      <td class="bold">Epic Dungeons</td>
      <td>90</td>
    </tr>
    <tr>
      <td class="bold">Sobekite</td>
      <td>123</td>
    </tr>
  </table>
</div>
```

**Example**:

```python
result = scraper.scrape_pve_stats(character_url)

if result['success']:
    print(f"Dragon Kills: {result['dragon_kills']}")
    print(f"Legion Kills: {result['legion_kills']}")
    print(f"Mini Dragon Kills: {result['mini_dragon_kills']}")
    print(f"Epic Encounters: {result['epic_encounters']}")
    print(f"Epic Dungeons: {result['epic_dungeons']}")
    print(f"Sobekite: {result['sobekite']}")
    # Output:
    # Dragon Kills: 12
    # Legion Kills: 34
    # Mini Dragon Kills: 56
    # Epic Encounters: 78
    # Epic Dungeons: 90
    # Sobekite: 123
```

**PvE Statistics Explained**:
- **Dragon Kills**: Full dragon raid boss kills
- **Legion Kills**: Legion encounter completions
- **Mini Dragon Kills**: Smaller dragon kills
- **Epic Encounters**: Epic mob defeats
- **Epic Dungeons**: Epic dungeon completions
- **Sobekite**: Sobekite mob kills (specific to Eden)

---

### scrape_achievements()

**Purpose**: Extract achievement progress from Achievements tab

**Tab**: Achievements (`&t=achievements`)

```python
def scrape_achievements(self, character_url):
    """
    Scrape achievements from character Herald page.
    
    Returns:
        dict: {
            'success': bool,
            'achievements': list of dict with:
                - 'title': str (achievement name)
                - 'progress': str (e.g., "19/50")
                - 'current': str or None (current tier name)
            'error': str or None
        }
    """
```

**Execution Flow**:

```
1. Add &t=achievements parameter to URL
2. Navigate to Achievements page
3. Wait 2 seconds (shorter wait, simpler page)
4. Parse HTML → Find div#player_content
5. Find all <tr> rows with class="titlerow"
6. For each row:
   - If title is "Current:": Store tier name with previous achievement
   - Else: Extract title and progress, add to list
7. Return list of achievements
```

**HTML Structure**:

```html
<div id="player_content">
  <table>
    <tr class="titlerow">
      <td>Bled Dry</td>
      <td>19/50</td>
    </tr>
    <tr class="titlerow">
      <td>Current:</td>
      <td>Bloodletter</td>
    </tr>
    <tr class="titlerow">
      <td>Dragon Slayer</td>
      <td>5/10</td>
    </tr>
    <tr class="titlerow">
      <td>Current:</td>
      <td>Dragon Hunter</td>
    </tr>
  </table>
</div>
```

**Example**:

```python
result = scraper.scrape_achievements(character_url)

if result['success']:
    for achievement in result['achievements']:
        current_info = f" (Current: {achievement['current']})" if achievement['current'] else ""
        print(f"{achievement['title']}: {achievement['progress']}{current_info}")
    
    # Output:
    # Bled Dry: 19/50 (Current: Bloodletter)
    # Dragon Slayer: 5/10 (Current: Dragon Hunter)
```

**Achievement Structure**:
- **title**: Achievement category name
- **progress**: Current progress (e.g., "19/50" = 19 out of 50 completed)
- **current**: Current tier/title within that achievement (if available)

---

## Error Handling

### Common Error Patterns

All scraping methods follow consistent error handling:

```python
try:
    # 1. Driver check
    if not self.driver:
        return {'success': False, 'error': 'Driver not initialized', ...}
    
    # 2. Navigation & parsing
    # ...
    
    # 3. Connection check
    if 'The requested page "herald" is not available.' in page_source:
        return {'success': False, 'error': 'Not connected to Herald - please regenerate cookies', ...}
    
    # 4. Content check
    if not player_content:
        return {'success': False, 'error': 'Player content not loaded', ...}
    
    # 5. Data extraction with validation
    # ...
    
    # 6. Success/partial success return
    if all_data_found:
        return {'success': True, 'error': None, ...}
    else:
        return {'success': False, 'error': 'Some data not found', ...}

except Exception as e:
    error_msg = f"Error scraping ...: {str(e)}"
    log_with_action(profile_logger, "error", error_msg, action="SCRAPE_...")
    return {'success': False, 'error': error_msg, ...}
```

### Debug Features

**HTML Dump for Troubleshooting**:

When data extraction fails, some methods save HTML to debug file:

```python
# Debug: Save HTML for analysis if stats are missing
try:
    debug_file = Path(__file__).parent.parent / "debug_pvp_missing.html"
    debug_file.write_text(page_source, encoding='utf-8')
    log_with_action(profile_logger, "info", 
                  f"Saved debug HTML to {debug_file}", 
                  action="SCRAPE_PVP")
except Exception as debug_error:
    log_with_action(profile_logger, "warning", 
                  f"Could not save debug HTML: {debug_error}", 
                  action="SCRAPE_PVP")
```

**Debug Files**:
- `debug_pvp_missing.html` - PvP stats missing
- `debug_pve_missing.html` - PvE stats missing

---

## Usage Examples

### Example 1: Complete Profile Scraping

```python
from Functions.character_profile_scraper import CharacterProfileScraper

def scrape_full_profile(character_url):
    """Scrape all available data from character profile"""
    
    # Initialize scraper
    scraper = CharacterProfileScraper()
    
    try:
        # Connect to Herald
        success, error = scraper.connect(headless=False)
        if not success:
            print(f"❌ Connection failed: {error}")
            return None
        
        print("✅ Connected to Herald")
        
        # Scrape all tabs
        results = {}
        
        # 1. Wealth
        print("\n📊 Scraping Wealth...")
        results['wealth'] = scraper.scrape_wealth_money(character_url)
        if results['wealth']['success']:
            print(f"   Money: {results['wealth']['money']}")
        
        # 2. RvR Captures
        print("\n🏰 Scraping RvR Captures...")
        results['rvr'] = scraper.scrape_rvr_captures(character_url)
        if results['rvr']['success']:
            print(f"   Towers: {results['rvr']['tower_captures']}")
            print(f"   Keeps: {results['rvr']['keep_captures']}")
            print(f"   Relics: {results['rvr']['relic_captures']}")
        
        # 3. PvP Stats
        print("\n⚔️ Scraping PvP Stats...")
        results['pvp'] = scraper.scrape_pvp_stats(character_url)
        if results['pvp']['success']:
            print(f"   Solo Kills: {results['pvp']['solo_kills']}")
            print(f"   Deathblows: {results['pvp']['deathblows']}")
            print(f"   Kills: {results['pvp']['kills']}")
        
        # 4. PvE Stats
        print("\n🐉 Scraping PvE Stats...")
        results['pve'] = scraper.scrape_pve_stats(character_url)
        if results['pve']['success']:
            print(f"   Dragon Kills: {results['pve']['dragon_kills']}")
            print(f"   Legion Kills: {results['pve']['legion_kills']}")
        
        # 5. Achievements
        print("\n🏆 Scraping Achievements...")
        results['achievements'] = scraper.scrape_achievements(character_url)
        if results['achievements']['success']:
            print(f"   Found {len(results['achievements']['achievements'])} achievements")
        
        return results
    
    finally:
        # Always cleanup
        scraper.close()
        print("\n🧹 Cleaned up resources")

# Usage
character_url = "https://eden-daoc.net/herald?n=player&k=PlayerName"
profile_data = scrape_full_profile(character_url)
```

**Output**:
```
✅ Connected to Herald

📊 Scraping Wealth...
   Money: 1234g 56s 78c

🏰 Scraping RvR Captures...
   Towers: 123
   Keeps: 45
   Relics: 6

⚔️ Scraping PvP Stats...
   Solo Kills: 1368
   Deathblows: 1691
   Kills: 1924

🐉 Scraping PvE Stats...
   Dragon Kills: 12
   Legion Kills: 34

🏆 Scraping Achievements...
   Found 15 achievements

🧹 Cleaned up resources
```

---

### Example 2: Context Manager Pattern

```python
def quick_wealth_check(character_url):
    """Quick wealth check using context manager"""
    
    with CharacterProfileScraper() as scraper:
        # Connection
        success, error = scraper.connect()
        if not success:
            return None, error
        
        # Scrape wealth
        result = scraper.scrape_wealth_money(character_url)
        
        if result['success']:
            return result['money'], None
        else:
            return None, result['error']
    
    # Cleanup happens automatically via __exit__

# Usage
money, error = quick_wealth_check(character_url)
if money:
    print(f"Character has {money}")
else:
    print(f"Error: {error}")
```

---

### Example 3: Batch Character Analysis

```python
def analyze_guild_characters(character_urls):
    """Analyze multiple characters in one connection session"""
    
    scraper = CharacterProfileScraper()
    
    try:
        # Single connection for all characters
        success, error = scraper.connect()
        if not success:
            return [], error
        
        results = []
        
        for url in character_urls:
            char_data = {
                'url': url,
                'wealth': scraper.scrape_wealth_money(url),
                'rvr': scraper.scrape_rvr_captures(url),
                'pvp': scraper.scrape_pvp_stats(url)
            }
            results.append(char_data)
            
            # Brief pause between characters
            import time
            time.sleep(1)
        
        return results, None
    
    finally:
        scraper.close()

# Usage
guild_urls = [
    "https://eden-daoc.net/herald?n=player&k=Player1",
    "https://eden-daoc.net/herald?n=player&k=Player2",
    "https://eden-daoc.net/herald?n=player&k=Player3"
]

guild_data, error = analyze_guild_characters(guild_urls)

if guild_data:
    for char in guild_data:
        print(f"Character: {char['url']}")
        if char['pvp']['success']:
            print(f"  Solo Kills: {char['pvp']['solo_kills']}")
```

---

### Example 4: UI Integration (from dialogs.py)

```python
def update_rvr_stats(self):
    """Update RvR/PvP/PvE/Wealth/Achievements from Herald UI button"""
    
    from Functions.character_profile_scraper import CharacterProfileScraper
    
    # Get character URL
    character_url = self.character_data.get('url')
    if not character_url:
        QMessageBox.warning(self, "No Herald URL", "Character has no Herald URL")
        return
    
    # Initialize scraper
    scraper = CharacterProfileScraper()
    
    try:
        # Connect
        success, error = scraper.connect()
        if not success:
            QMessageBox.critical(self, "Connection Failed", error)
            return
        
        # Scrape all statistics
        rvr_result = scraper.scrape_rvr_captures(character_url)
        pvp_result = scraper.scrape_pvp_stats(character_url)
        pve_result = scraper.scrape_pve_stats(character_url)
        wealth_result = scraper.scrape_wealth_money(character_url)
        achievements_result = scraper.scrape_achievements(character_url)
        
        # Update character data
        if rvr_result['success']:
            self.character_data['tower_captures'] = rvr_result['tower_captures']
            self.character_data['keep_captures'] = rvr_result['keep_captures']
            self.character_data['relic_captures'] = rvr_result['relic_captures']
        
        # ... update other fields ...
        
        # Save changes
        self.save_character()
        
        QMessageBox.information(self, "Success", "Statistics updated from Herald!")
    
    finally:
        scraper.close()
```

---

## Performance Characteristics

### Timing Analysis

| Operation | Duration | Description |
|-----------|----------|-------------|
| **Initialization** | <1ms | Create scraper instance |
| **Connection** | 5-8s | Via `_connect_to_eden_herald()` |
| **Per Tab Scrape** | 5-6s | Navigate + wait + parse |
| **Cleanup** | <1s | Close browser |
| **TOTAL (Full Profile)** | **30-35s** | Connection + 5 tabs |

### Per-Method Timing

| Method | Tab | Navigation | Wait | Parse | Total |
|--------|-----|------------|------|-------|-------|
| `scrape_wealth_money()` | Wealth | <1s | 5s | <1s | ~6s |
| `scrape_rvr_captures()` | Characters | <1s | 5s | <1s | ~6s |
| `scrape_pvp_stats()` | PvP | <1s | 5s | <1s | ~6s |
| `scrape_pve_stats()` | PvE | <1s | 5s | <1s | ~6s |
| `scrape_achievements()` | Achievements | <1s | 2s | <1s | ~3s |

**Optimization**: Single connection reused across all scraping operations

---

### Memory Usage

| Phase | Memory Impact |
|-------|---------------|
| Scraper instance | ~1MB (Python objects) |
| WebDriver | ~100-150MB (Chrome process) |
| HTML parsing | ~5-10MB per page |
| **Peak Memory** | **~200MB** |

---

## Related Functions

1. **`_connect_to_eden_herald()`** - Centralized connection (see CONNECT_TO_EDEN_HERALD_EN.md)
2. **`search_herald_character()`** - Character search (see SEARCH_HERALD_CHARACTER_EN.md)
3. **`scrape_character_from_url()`** - Character update (see SCRAPE_CHARACTER_FROM_URL_EN.md)

---

## Logging

### Log File
**Location**: `Logs/eden.log`

### Log Actions

| Action | Methods | Description |
|--------|---------|-------------|
| `INIT` | `__init__()` | Scraper initialization |
| `CONNECT` | `connect()` | Connection establishment |
| `SCRAPE_WEALTH` | `scrape_wealth_money()` | Wealth scraping |
| `SCRAPE_RVR` | `scrape_rvr_captures()` | RvR scraping |
| `SCRAPE_PVP` | `scrape_pvp_stats()` | PvP scraping |
| `SCRAPE_PVE` | `scrape_pve_stats()` | PvE scraping |
| `SCRAPE_ACHIEVEMENTS` | `scrape_achievements()` | Achievement scraping |
| `CLEANUP` | `close()` | Resource cleanup |

### Example Log Sequence

```log
2025-11-13 16:00:00 [INFO] [INIT] CharacterProfileScraper initialized
2025-11-13 16:00:00 [INFO] [CONNECT] Connecting to Eden Herald using centralized function
2025-11-13 16:00:05 [INFO] [CONNECT] ✅ Successfully connected to Eden Herald
2025-11-13 16:00:05 [INFO] [SCRAPE_WEALTH] Navigating to: https://eden-daoc.net/herald?n=player&k=PlayerName&t=wealth
2025-11-13 16:00:05 [INFO] [SCRAPE_WEALTH] Waiting for page to fully load (5 seconds)...
2025-11-13 16:00:10 [INFO] [SCRAPE_WEALTH] Page loaded - Size: 45678 chars
2025-11-13 16:00:10 [INFO] [SCRAPE_WEALTH] Money found: 1234g 56s 78c
2025-11-13 16:00:10 [INFO] [SCRAPE_RVR] Navigating to: https://eden-daoc.net/herald?n=player&k=PlayerName
2025-11-13 16:00:15 [INFO] [SCRAPE_RVR] Found Tower Captures: 123
2025-11-13 16:00:15 [INFO] [SCRAPE_RVR] Found Keep Captures: 45
2025-11-13 16:00:15 [INFO] [SCRAPE_RVR] Found Relic Captures: 6
2025-11-13 16:00:15 [INFO] [CLEANUP] EdenScraper closed
```

---

## Troubleshooting

### Issue: "Driver not initialized"

**Cause**: Called scraping method before `connect()`

**Solution**:
```python
scraper = CharacterProfileScraper()
scraper.connect()  # ← MUST call before scraping
result = scraper.scrape_wealth_money(url)
```

---

### Issue: "Not connected to Herald - please regenerate cookies"

**Cause**: Cookies expired or invalid

**Solution**:
1. Open Cookie Manager UI
2. Click "Générer les cookies"
3. Complete manual login
4. Try scraping again

---

### Issue: Missing statistics

**Symptoms**:
- `success: False`
- `error: "Some statistics not found"`
- Debug HTML file created

**Investigation**:
1. Check debug HTML file (e.g., `debug_pvp_missing.html`)
2. Verify Herald page structure hasn't changed
3. Check log file for parsing errors

**Common Causes**:
- Herald HTML structure changed
- Character has no data for that stat
- Page load timeout (increase wait time)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.107 | 2025-11-13 | Refactored to use `_connect_to_eden_herald()` - Eliminated ~300 lines of duplicated connection code |
| 0.106 | Earlier | Previous implementation with separate `initialize_driver()` + `load_cookies()` |

---

## Related Documentation

- **Connection**: [CONNECT_TO_EDEN_HERALD_EN.md](CONNECT_TO_EDEN_HERALD_EN.md)
- **Search**: [SEARCH_HERALD_CHARACTER_EN.md](SEARCH_HERALD_CHARACTER_EN.md)
- **Update**: [SCRAPE_CHARACTER_FROM_URL_EN.md](SCRAPE_CHARACTER_FROM_URL_EN.md)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-13  
**Author**: Automated Documentation  
**Status**: ✅ Production Ready
