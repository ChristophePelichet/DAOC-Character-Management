# Complete Eden Herald Scraper Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Detailed Operation Flow](#detailed-operation-flow)
4. [Main Components](#main-components)
5. [Cookie Management](#cookie-management)
6. [User Interface](#user-interface)
7. [Data Processing](#data-processing)
8. [Error Handling](#error-handling)

---

## 🎯 Overview

The Eden Herald scraper allows automatic search and import of characters from the Eden DAOC Herald website. It uses Selenium to navigate the website and BeautifulSoup to parse HTML results.

### Main Features

- ✅ **Character search** by name with optional realm filter
- ✅ **Automatic verification** of Herald accessibility
- ✅ **Cookie management** to bypass bot check
- ✅ **Simple or mass import** of found characters
- ✅ **Automatic detection** of realm based on class
- ✅ **Automatic calculation** of Realm Rank
- ✅ **Smart filtering** of search results
- ✅ **Multilingual interface** (FR, EN, DE)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN APPLICATION                              │
│                         (main.py)                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├─── UI Manager (Functions/ui_manager.py)
                 │    └─── Eden Herald Status Bar
                 │         ├─── Status Label
                 │         ├─── Refresh Button
                 │         ├─── Herald Search Button
                 │         └─── Manage Button (cookies)
                 │
                 ├─── Cookie Manager (Functions/cookie_manager.py)
                 │    ├─── Secure cookie storage
                 │    ├─── Data encryption
                 │    ├─── Import/Export
                 │    └─── Validation
                 │
                 ├─── Eden Scraper (Functions/eden_scraper.py)
                 │    ├─── Selenium configuration
                 │    ├─── Herald navigation
                 │    ├─── Data extraction
                 │    └─── Bot check handling
                 │
                 └─── Herald Search Dialog (UI/dialogs.py)
                      ├─── Search interface
                      ├─── Results display
                      ├─── Character selection
                      └─── Import to database
```

---

## 🔄 Detailed Operation Flow

### 1. Initial Herald Verification

```
┌──────────────┐
│  Application │
│    Startup   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.create_eden_status_bar()      │
│ - Creates status interface              │
│ - Disables Refresh/Search buttons       │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.check_eden_status()           │
│ - Creates EdenStatusThread              │
│ - Launches background verification      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ EdenStatusThread.run()                  │
│ - Loads cookies from CookieManager      │
│ - Attempts access to eden-daoc.net      │
│ - Checks Herald presence                │
└──────┬──────────────────────────────────┘
       │
       ├─── ✅ Success
       │    └──▶ Signal: status_updated(True, "")
       │
       └─── ❌ Failure
            └──▶ Signal: status_updated(False, "message")
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.update_eden_status()          │
│ - Updates label (✅/❌)                 │
│ - Re-enables Refresh/Search buttons     │
└─────────────────────────────────────────┘
```

### 2. Character Search

```
┌──────────────────┐
│ User clicks      │
│ "🔍 Herald       │
│    Search"       │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ CharacterApp.open_herald_search()          │
│ - Opens HeraldSearchDialog                 │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.__init__()              │
│ - Creates search interface                 │
│ - Character name text field                │
│ - Realm filter dropdown (with logos)       │
│ - Results table with checkboxes            │
│ - Import selected/all buttons              │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ User enters name (min 3 characters)        │
│ + selects optional realm                   │
│ + clicks "Search"                          │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.start_search()          │
│ - Validates length >= 3 characters         │
│ - Gets realm_filter from dropdown          │
│ - Disables interface during search         │
│ - Creates SearchThread                     │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ SearchThread.run()                         │
│ - Calls eden_scraper.search_herald_...()   │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ eden_scraper.search_herald_character()     │
│ 1. Configures Chrome (off-screen)         │
│ 2. Loads cookies                           │
│ 3. Builds URL with parameters              │
│    - name={character_name}                 │
│    - &r={realm} (if filter active)         │
│ 4. Navigates to Herald                     │
│ 5. Extracts data from 28 HTML tables       │
│ 6. Cleans temporary folder                 │
│ 7. Saves JSON in temp folder               │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Signal: search_finished(success, message,  │
│                         json_path)         │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.on_search_finished()    │
│ - Loads JSON from temporary file           │
│ - Filters: keeps only names starting       │
│   with query (startswith)                  │
│ - Fills table with results                 │
│ - Colors rows by realm                     │
│ - Re-enables interface                     │
└────────────────────────────────────────────┘
```

### 3. Character Import

```
┌──────────────────┐
│ User checks      │
│ characters and   │
│ clicks "Import"  │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.import_selected_...()   │
│ - Gets checked rows                        │
│ - Asks for confirmation                    │
│ - Calls _import_characters()               │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog._import_characters()    │
│ For each character:                        │
│   1. Gets data (name, class, etc.)         │
│   2. Detects realm via CLASS_TO_REALM      │
│   3. Checks if already exists (duplicate)  │
│   4. Creates character_data dict           │
│   5. Calls save_character()                │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ character_manager.save_character()         │
│ - Saves to JSON file                       │
│   Characters/{realm}/{name}.json           │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Automatic refresh                          │
│ - parent().tree_manager.refresh_...()      │
│ - Displays new characters in list          │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Displays result                            │
│ - ✅ X character(s) imported               │
│ - ⚠️ Y error(s) (duplicates, etc.)        │
└────────────────────────────────────────────┘
```

---

## 🧩 Main Components

### 1. UIManager (`Functions/ui_manager.py`)

**Role**: Manages Eden status interface in main window

#### Key Methods

```python
create_eden_status_bar(parent_layout)
```
- Creates "Eden Herald Status" group
- Initializes buttons and status label
- Launches initial verification

```python
check_eden_status()
```
- Disables buttons during verification
- Creates verification thread (EdenStatusThread)
- Launches background verification

```python
update_eden_status(accessible, message)
```
- Updates status display
- Re-enables buttons after verification
- Shows ✅ or ❌ based on result

#### EdenStatusThread Class

Thread that verifies Herald accessibility without blocking the interface.

**Signal**: `status_updated(bool accessible, str message)`

---

### 2. CookieManager (`Functions/cookie_manager.py`)

**Role**: Manages secure storage of Eden cookies

#### Storage Structure

```json
{
  "cookies": [
    {
      "name": "cookie_name",
      "value": "encrypted_value",
      "domain": ".eden-daoc.net",
      "path": "/",
      "secure": true,
      "httpOnly": false,
      "sameSite": "Lax"
    }
  ],
  "created_at": "2025-01-29T10:30:00",
  "last_used": "2025-01-29T14:45:00"
}
```

#### Key Methods

```python
load_cookies_for_selenium(driver)
```
- Loads cookies from encrypted file
- Injects them into Selenium browser
- Returns True if successful, False otherwise

```python
import_cookies_from_file(file_path)
```
- Imports cookies from external JSON file
- Validates format
- Encrypts and saves

```python
export_cookies_to_file(file_path)
```
- Exports current cookies to file
- Decrypts values for export

---

### 3. Eden Scraper (`Functions/eden_scraper.py`)

**Role**: Main scraper that extracts Herald data

#### Selenium Configuration

```python
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--window-position=-2400,-2400")  # Off-screen
```

**Important**: Browser is positioned off-screen (`-2400,-2400`) to remain invisible while being technically "visible" (bypasses bot check).

#### Main Function

```python
search_herald_character(character_name, realm_filter="")
```

**Parameters**:
- `character_name`: Character name to search
- `realm_filter`: "albion", "midgard", "hibernia" or "" (all)

**Return**: `(success: bool, message: str, json_path: str)`

**Process**:

1. **Cleanup**: Removes old temporary files
2. **Configuration**: Configures Chrome with specific options
3. **Cookies**: Loads cookies via CookieManager
4. **Navigation**: Accesses `https://eden-daoc.net/herald/character/search`
5. **Query**: Sends search parameters
6. **Extraction**: Parses 28 HTML tables with BeautifulSoup
7. **Save**: Creates JSON in `tempfile.gettempdir()/EdenSearchResult/`
8. **Cleanup**: Closes browser

#### Extracted HTML Table Structure

The Herald returns data in 28 distinct HTML tables:
- Tables 0-27 each contain character information

**Table format**:
```html
<table>
  <tr><td>Rank</td><td>Name</td><td>Class</td><td>Race</td>...</tr>
  <tr><td>1</td><td>Ewoline</td><td>Cleric</td><td>Briton</td>...</tr>
</table>
```

#### Extracted Columns

1. **rank**: Position in ranking
2. **name**: Full character name
3. **clean_name**: Cleaned name (no HTML tags)
4. **class**: Character class
5. **race**: Character race
6. **guild**: Guild (or "Unguilded")
7. **level**: Level (1-50)
8. **realm_points**: Realm points (format "331 862")
9. **realm_rank**: Realm rank (e.g., "12L3")
10. **realm_level**: Rank level (e.g., "12")
11. **url**: Link to character page

#### Generated Temporary Files

```
%TEMP%/EdenSearchResult/
├── search_20250129_143045.json      # Raw data
└── characters_20250129_143045.json  # Formatted data
```

**Cleanup**: Files are deleted when search dialog closes.

---

### 4. Herald Search Dialog (`UI/dialogs.py`)

**Role**: Search and import interface

#### HeraldSearchDialog Class

##### Interface

```
┌────────────────────────────────────────────────────┐
│  Character Search - Eden Herald                   │
├────────────────────────────────────────────────────┤
│  Character name: [___________]                     │
│  Realm: [All realms ▼]                            │
│  [Search]                                          │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │
│  │ ☑ │ 🏰 │ Name   │ Class  │ Race │ Guild   │ │ │
│  ├───┼────┼────────┼────────┼──────┼─────────┤ │ │
│  │ ☑ │ 🔴 │ Ewoline│ Cleric │Briton│MyGuild  │ │ │
│  │ ☐ │ 🔵 │ Olaf   │Warrior │Norseman│      │ │ │
│  │ ☑ │ 🟢 │ Fionn  │ Druid  │ Celt │OtherG   │ │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  [⬇️ Import selection] [⬇️⬇️ Import all]           │
└────────────────────────────────────────────────────┘
```

##### Key Methods

```python
_load_realm_icons_for_combo()
```
- Loads realm logos (Img/)
- Creates QComboBox with 20x20 icons
- Options: All, Albion, Midgard, Hibernia

```python
start_search()
```
- Validates minimum length (3 characters)
- Gets realm filter
- Launches SearchThread

```python
on_search_finished(success, message, json_path)
```
- Loads results JSON
- **Important filter**: `name.lower().startswith(query.lower())`
  - Avoids partial results ("oli" doesn't find "Ewoline")
- Fills table with colored columns
- Applies background color by realm (alpha 50)

```python
import_selected_characters()
```
- Gets checked rows
- Asks for confirmation
- Calls `_import_characters()`

```python
import_all_characters()
```
- Imports all results without selection confirmation
- Asks for global confirmation
- Calls `_import_characters()`

```python
_import_characters(characters)
```
For each character:
1. Extracts `clean_name` or `name`
2. Determines realm via `CLASS_TO_REALM[class]`
3. **Checks duplicates**:
   ```python
   existing_chars = get_all_characters()
   if any(c.get('name', '').lower() == name.lower() for c in existing_chars):
       # Error: character already exists
   ```
4. Creates complete `character_data` dict
5. Calls `save_character(character_data)`
6. Counts successes/errors
7. Refreshes main interface
8. Displays result in QMessageBox

##### Class → Realm Mapping

```python
CLASS_TO_REALM = {
    # Albion
    "Armsman": "Albion", "Cabalist": "Albion", "Cleric": "Albion",
    "Friar": "Albion", "Heretic": "Albion", "Infiltrator": "Albion",
    "Mauler": "Albion", "Mercenary": "Albion", "Minstrel": "Albion",
    "Necromancer": "Albion", "Paladin": "Albion", "Reaver": "Albion",
    "Scout": "Albion", "Sorcerer": "Albion", "Theurgist": "Albion",
    "Wizard": "Albion",
    
    # Midgard
    "Berserker": "Midgard", "Bonedancer": "Midgard", "Healer": "Midgard",
    "Hunter": "Midgard", "Runemaster": "Midgard", "Savage": "Midgard",
    "Shadowblade": "Midgard", "Shaman": "Midgard", "Skald": "Midgard",
    "Spiritmaster": "Midgard", "Thane": "Midgard", "Valkyrie": "Midgard",
    "Warlock": "Midgard", "Warrior": "Midgard",
    
    # Hibernia
    "Animist": "Hibernia", "Bainshee": "Hibernia", "Bard": "Hibernia",
    "Blademaster": "Hibernia", "Champion": "Hibernia", "Druid": "Hibernia",
    "Eldritch": "Hibernia", "Enchanter": "Hibernia", "Hero": "Hibernia",
    "Mentalist": "Hibernia", "Nightshade": "Hibernia", "Ranger": "Hibernia",
    "Valewalker": "Hibernia", "Vampiir": "Hibernia", "Warden": "Hibernia"
}
```

##### Realm Colors (table)

```python
REALM_COLORS = {
    "Albion": QColor(204, 0, 0, 50),      # Red alpha 50
    "Midgard": QColor(0, 102, 204, 50),   # Blue alpha 50
    "Hibernia": QColor(0, 170, 0, 50)     # Green alpha 50
}
```

---

## 🍪 Cookie Management

### Why Cookies?

The Eden Herald website uses an anti-bot system that requires initial validation. Cookies allow bypassing this verification by reusing an authenticated session.

### Cookie Retrieval Process

#### Method 1: Import from Browser

1. Open Firefox/Chrome
2. Log in to https://eden-daoc.net
3. Open DevTools (F12)
4. Go to "Storage" / "Application" tab
5. Copy cookies from `.eden-daoc.net` domain
6. Create JSON file:

```json
[
  {
    "name": "__cf_bm",
    "value": "your_value_here",
    "domain": ".eden-daoc.net",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "sameSite": "Lax"
  }
]
```

7. In application: **Actions Menu → Manage Eden Cookies → Import**

#### Method 2: Automatic Generation (TODO)

Feature planned to automate retrieval.

### Cookie File Structure

**Location**: `%APPDATA%/DAOCCharacterManager/eden_cookies.json`

**Format**:
```json
{
  "cookies": [
    {
      "name": "__cf_bm",
      "value": "BASE64_ENCRYPTED_VALUE",
      "domain": ".eden-daoc.net",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax"
    }
  ],
  "created_at": "2025-01-29T10:00:00",
  "last_used": "2025-01-29T14:30:00"
}
```

### Security

- ✅ Values encrypted with cryptography (Fernet)
- ✅ Unique encryption key per installation
- ✅ Restrictive file permissions
- ✅ Format validation before use

---

## 🎨 User Interface

### Main Window

#### Eden Herald Status Bar

```
┌──────────────────────────────────────────────────────┐
│ Eden Herald Status                                   │
├──────────────────────────────────────────────────────┤
│ ⏳ Checking...                                       │
│ [🔄 Refresh] [🔍 Herald Search] [⚙️ Manage]         │
└──────────────────────────────────────────────────────┘
```

**Possible States**:
- `⏳ Checking...` (gray) → Buttons disabled
- `✅ Herald accessible` (green bold) → Buttons enabled
- `❌ Herald unreachable: <reason>` (red) → Buttons enabled

#### Character List (coloring)

Rows are colored by realm with subtle background (alpha 25):
- 🔴 **Albion**: Light red background
- 🔵 **Midgard**: Light blue background
- 🟢 **Hibernia**: Light green background

**Implementation**: Custom delegates in `UI/delegates.py`
- `NormalTextDelegate`: Normal text + colored background
- `CenterIconDelegate`: Centered icon + colored background
- `CenterCheckboxDelegate`: Centered checkbox + colored background

### Herald Search Dialog

#### Components

1. **Search field**: QLineEdit with 3+ character validation
2. **Realm filter**: QComboBox with logos (20x20px)
3. **Search button**: Launches search
4. **Results table**: QTableWidget with 9 columns
5. **Import buttons**: Import selection / Import all

#### Table Columns

| Column | Type | Description |
|---------|------|-------------|
| ☑ | Checkbox | Selection for import |
| Realm | Icon | Realm logo |
| Name | Text | Character name |
| Class | Text | Class |
| Race | Text | Race |
| Guild | Text | Guild name |
| Level | Number | Level (1-50) |
| RP | Number | Formatted Realm Points |
| Realm Rank | Text | Rank (e.g., 12L3) |

#### Search Validation

```python
def start_search(self):
    query = self.search_input.text().strip()
    
    # Minimum length validation
    if len(query) < 3:
        QMessageBox.warning(
            self,
            "Invalid search",
            "Please enter at least 3 characters."
        )
        return
    
    # Get realm filter
    realm_filter = ""
    realm_index = self.realm_combo.currentIndex()
    if realm_index > 0:  # 0 = "All"
        realm_filter = ["albion", "midgard", "hibernia"][realm_index - 1]
    
    # Launch search
    self.search_thread = SearchThread(query, realm_filter)
    # ...
```

#### Results Filtering

After retrieval from Herald, local filtering for precision:

```python
def on_search_finished(self, success, message, json_path):
    # ...
    search_query = self.search_input.text().strip().lower()
    
    # Filter: only names starting with query
    filtered_characters = [
        char for char in all_characters
        if char.get('clean_name', '').lower().startswith(search_query)
        or char.get('name', '').lower().startswith(search_query)
    ]
    
    # Display in table
    self._populate_results_table(filtered_characters)
```

**Example**:
- Search: `"Ewo"`
- Herald returns: `["Ewoline", "Ewolinette", "NewoB", "Aewo"]`
- Local filter keeps: `["Ewoline", "Ewolinette"]`
- Eliminates: `["NewoB", "Aewo"]` (don't start with "Ewo")

---

## 📊 Data Processing

### Character Data Structure

#### Raw Herald Data

```json
{
  "rank": "1",
  "name": "Ewoline",
  "clean_name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_points": "331 862",
  "realm_rank": "12L3",
  "realm_level": "12",
  "url": "/herald/character/view/Ewoline"
}
```

#### Data After Import (character_data)

```json
{
  "name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "realm": "Albion",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_rank": "12L3",
  "realm_points": 331862,
  "realm_level": "12",
  "server": "Eden",
  "mlevel": "0",
  "clevel": "0",
  "notes": "Imported from Herald on 2025-01-29 14:30"
}
```

#### Applied Transformations

1. **Realm Detection**:
   ```python
   realm = CLASS_TO_REALM.get(class_name, "Unknown")
   ```

2. **realm_points Conversion**:
   ```python
   # Herald format: "331 862" (string with spaces)
   # Final format: 331862 (integer)
   if isinstance(realm_points, str):
       realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
   ```

3. **Automatic Realm Rank Calculation**:
   ```python
   rank_info = data_manager.get_realm_rank_info(realm, realm_points)
   # Returns: {rank, title, level, realm_points}
   ```

### Realm Rank Calculation

The system uses `Data/realm_ranks_*.json` files to determine rank.

**Albion Example** (`Data/realm_ranks_albion.json`):
```json
{
  "1": {
    "1": {"title": "Guardian", "rp": 0},
    "2": {"title": "Guardian", "rp": 125},
    ...
  },
  "12": {
    "1": {"title": "General", "rp": 309000},
    "2": {"title": "General", "rp": 318000},
    "3": {"title": "General", "rp": 327000}
  }
}
```

**Algorithm** (`data_manager.py::get_realm_rank_info()`):
```python
def get_realm_rank_info(realm, realm_points):
    # Convert if string
    if isinstance(realm_points, str):
        realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
    
    # Traverse ranks from high to low
    for rank in range(max_rank, 0, -1):
        for level in range(max_level, 0, -1):
            required_rp = rank_data[rank][level]['rp']
            if realm_points >= required_rp:
                return {
                    'rank': rank,
                    'level': f"{rank}L{level}",
                    'title': rank_data[rank][level]['title'],
                    'realm_points': required_rp
                }
    
    # Default: 1L1
    return {'rank': 1, 'level': '1L1', 'title': 'Guardian', 'realm_points': 0}
```

### Character Save

**File Structure**:
```
Characters/
├── Albion/
│   ├── Ewoline.json
│   └── Paladin42.json
├── Midgard/
│   ├── Olaf.json
│   └── Berserker99.json
└── Hibernia/
    ├── Fionn.json
    └── Druidess.json
```

**File Format** (`Ewoline.json`):
```json
{
  "id": "unique-uuid",
  "name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "realm": "Albion",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_rank": "12L3",
  "realm_points": 331862,
  "realm_level": "12",
  "server": "Eden",
  "mlevel": "0",
  "clevel": "0",
  "notes": "Imported from Herald on 2025-01-29 14:30",
  "page": "1",
  "armor": {
    "head": {"name": "", "type": "", "af": 0, "abs": 0, ...},
    "hands": {...},
    "arms": {...},
    "torso": {...},
    "legs": {...},
    "feet": {...}
  },
  "resists": {
    "crush": 0, "slash": 0, "thrust": 0, "heat": 0, "cold": 0, "matter": 0,
    "body": 0, "spirit": 0, "energy": 0
  }
}
```

---

## ⚠️ Error Handling

### Common Errors and Solutions

#### 1. "❌ Herald unreachable: Missing or invalid cookies"

**Cause**: No configured cookies or expired cookies

**Solution**:
1. Click "⚙️ Manage"
2. Import valid cookies from browser
3. Click "🔄 Refresh" to re-check

---

#### 2. "No results found for 'xxx'"

**Possible Causes**:
- Character doesn't exist on Eden server
- Incorrect realm filter
- Name misspelled

**Solution**:
- Check spelling
- Try without realm filter
- Verify character exists on Eden

---

#### 3. "Please enter at least 3 characters"

**Cause**: Minimum length validation

**Solution**: Enter at least 3 characters in search field

---

#### 4. "X: character already exists"

**Cause**: Attempting to import duplicate

**Behavior**:
- Existing character is not overwritten
- Counted as error in import report
- Other characters continue to be imported

**Solution**: If you want to update, first delete the old character

---

#### 5. "Scraping error"

**Possible Causes**:
- Modified Herald page (HTML structure changed)
- Network timeout
- Bot check activated despite cookies

**Solution**:
1. Check Internet connection
2. Re-generate/import recent cookies
3. Wait a few minutes before retrying
4. Check logs: `Logs/app.log`

---

### Logs and Debugging

#### Log Location

```
%APPDATA%/DAOCCharacterManager/Logs/
└── app.log
```

#### Log Levels

```python
logging.DEBUG    # Technical details (scraping, parsing)
logging.INFO     # General information (import successful)
logging.WARNING  # Warnings (duplicate detected)
logging.ERROR    # Errors (scraping failed)
logging.CRITICAL # Critical errors (application crash)
```

#### Example Logs During Search

```
2025-01-29 14:30:15 [INFO] Herald search: name='Ewoline', realm='albion'
2025-01-29 14:30:16 [DEBUG] Chrome configuration with off-screen options
2025-01-29 14:30:17 [DEBUG] Loading 3 cookies from CookieManager
2025-01-29 14:30:18 [INFO] Navigating to Herald: https://eden-daoc.net/herald/character/search?name=Ewoline&r=albion
2025-01-29 14:30:20 [DEBUG] Extracting 28 HTML tables
2025-01-29 14:30:21 [INFO] Found 2 characters: ['Ewoline', 'Ewolinette']
2025-01-29 14:30:21 [DEBUG] Filtering: keeping only names starting with 'ewoline'
2025-01-29 14:30:21 [INFO] Filtered results: 2 characters
2025-01-29 14:30:22 [INFO] Temporary save: C:\Users\...\Temp\EdenSearchResult\characters_20250129_143022.json
2025-01-29 14:30:22 [INFO] Search completed successfully
```

#### Example Logs During Import

```
2025-01-29 14:32:10 [INFO] Importing 2 selected characters
2025-01-29 14:32:10 [DEBUG] Import 'Ewoline': class=Cleric, realm=Albion
2025-01-29 14:32:10 [DEBUG] Checking duplicates: 45 existing characters
2025-01-29 14:32:10 [WARNING] Duplicate detected: 'Ewoline' already exists
2025-01-29 14:32:10 [DEBUG] Import 'Ewolinette': class=Cleric, realm=Albion
2025-01-29 14:32:10 [INFO] Save: Characters/Albion/Ewolinette.json
2025-01-29 14:32:10 [INFO] Import completed: 1 success, 1 error
2025-01-29 14:32:10 [INFO] Refreshing main interface
```

---

## 🔧 Technical Configuration

### System Requirements

- **Python**: 3.9+
- **Selenium**: 4.15.2+
- **BeautifulSoup4**: 4.12.2+
- **Chrome/Chromium**: Recent version
- **ChromeDriver**: Compatible with Chrome version

### Python Dependencies

```
selenium>=4.15.2
beautifulsoup4>=4.12.2
PySide6>=6.6.0
cryptography>=41.0.0
requests>=2.31.0
```

### Environment Variables (optional)

```bash
# Force specific ChromeDriver
CHROMEDRIVER_PATH=/path/to/chromedriver

# Custom timeout (seconds)
HERALD_TIMEOUT=30

# Log level
LOG_LEVEL=DEBUG
```

---

## 📈 Performance and Limitations

### Average Response Times

| Operation | Average Duration | Notes |
|-----------|------------------|-------|
| Status check | 2-4 seconds | Depends on network latency |
| Search 1 character | 5-8 seconds | Loads 28 HTML tables |
| Import 1 character | < 1 second | Local operation |
| Import 10 characters | < 2 seconds | Duplicate checking included |

### Known Limitations

1. **Partial search**: Herald doesn't support wildcards
   - `"Ewo*"` doesn't work
   - Solution: Enter exact name beginning

2. **Result count**: Maximum ~100 characters per search
   - Herald limits displayed results
   - Solution: Use more specific names

3. **Expired cookies**: Limited lifespan (hours/days)
   - Solution: Re-import regularly

4. **Bot check**: Can randomly reactivate
   - Solution: Wait 5-10 minutes, re-import cookies

---

## 🔐 Security and Privacy

### Sensitive Data

- ✅ **Encrypted cookies**: Using Fernet (AES-128)
- ✅ **Unique key**: Generated at installation
- ✅ **Local storage**: No data sent to third parties
- ✅ **Temporary files**: Automatically deleted

### Best Practices

1. **Don't share** the `eden_cookies.json` file
2. **Don't commit** cookies to Git (`.gitignore` configured)
3. **Export regularly** your characters (backup)
4. **Update** cookies if access problems occur

---

## 🆘 Support and Troubleshooting

### Diagnostic Checklist

If search doesn't work:

- [ ] Check Internet connection
- [ ] Test manual access to https://eden-daoc.net
- [ ] Verify Chrome/Chromium is installed
- [ ] Re-import recent cookies
- [ ] Click "🔄 Refresh" to re-check
- [ ] Check `Logs/app.log` for errors
- [ ] Try with a known character name

### Complete Reset

If nothing works:

1. Close application
2. Delete `%APPDATA%/DAOCCharacterManager/eden_cookies.json`
3. Restart application
4. Re-import fresh cookies
5. Test search

---

## 📝 Version History

### Current Version: 0.105

**Features**:
- ✅ Herald search with realm filter
- ✅ Simple and mass import
- ✅ Automatic realm detection
- ✅ Automatic Realm Rank calculation
- ✅ Realm-colored interface
- ✅ Duplicate validation
- ✅ Automatic refresh
- ✅ Secure cookie management
- ✅ Precise result filtering (startswith)
- ✅ Grayed buttons during verification

**Recent Fixes**:
- 🐛 Fix realm_points string/int conversion
- 🐛 Fix bold text in main view
- 🐛 Fix colored Title column (now normal)
- 🐛 Fix coloring of empty cells
- 🐛 Fix centering of Name and Guild columns

---

## 🎓 Glossary

**Bot check**: Anti-automation system on Eden site

**Cookie**: Small session file to identify browser

**Delegate**: Qt component to customize cell rendering

**Herald**: Official website displaying DAOC statistics

**Realm**: Kingdom (Albion, Midgard, Hibernia)

**Realm Points (RP)**: Points accumulated in RvR (realm vs realm combat)

**Realm Rank (RR)**: Realm rank (e.g., 12L3 = Rank 12, Level 3)

**Scraper**: Program that extracts data from website

**Selenium**: Web browser automation tool

**Thread**: Parallel process to avoid blocking interface

---

## 📚 Resources

### Technical Documentation

- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [PySide6 Docs](https://doc.qt.io/qtforpython/)

### Eden DAOC Links

- [Main Site](https://eden-daoc.net)
- [Herald](https://eden-daoc.net/herald)
- [Discord](https://discord.gg/eden-daoc)

---

## 👥 Credits

**Development**: ChristophePelichet  
**Version**: 0.105  
**Date**: January 2025  
**License**: MIT

---

*This documentation is kept up to date with each application version.*
