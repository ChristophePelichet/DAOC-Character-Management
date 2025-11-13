# search_herald_character() - Technical Documentation

## Function Overview

**Name**: `search_herald_character(character_name, realm_filter="")`  
**Location**: `Functions/eden_scraper.py` (line ~475)  
**Purpose**: Search for characters on Eden Herald and save results to JSON files  
**Category**: Public API function for character search operations

---

## Function Signature

```python
def search_herald_character(character_name, realm_filter=""):
    """
    Searches for a character on Eden Herald and saves results to JSON
    
    Args:
        character_name: Name of the character to search for
        realm_filter: Realm filter ("alb", "mid", "hib", or "" for all)
        
    Returns:
        tuple: (success: bool, message: str, json_path: str)
    """
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `character_name` | `str` | ✅ Yes | N/A | Character name to search for (partial match supported) |
| `realm_filter` | `str` | ❌ No | `""` | Realm filter: `"alb"` (Albion), `"mid"` (Midgard), `"hib"` (Hibernia), or `""` (all realms) |

---

## Return Value

**Type**: `tuple(bool, str, str)`

### Success Case
```python
(True, "5 personnage(s) trouvé(s)", "/tmp/EdenSearchResult/characters_PlayerName_20251113_143052.json")
```

| Index | Type | Description |
|-------|------|-------------|
| `[0]` | `bool` | `True` - Operation succeeded |
| `[1]` | `str` | Success message with character count |
| `[2]` | `str` | Absolute path to JSON file containing formatted character data |

### Failure Case
```python
(False, "Aucun cookie trouvé. Veuillez générer ou importer des cookies d'abord.", "")
```

| Index | Type | Description |
|-------|------|-------------|
| `[0]` | `bool` | `False` - Operation failed |
| `[1]` | `str` | Error message describing the failure |
| `[2]` | `str` | Empty string (no file created) |

---

## Execution Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    search_herald_character()                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: CONNECTION (5-8s)                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Call _connect_to_eden_herald(headless=False)                │ │
│ │   ├─ Verify cookies exist & valid                           │ │
│ │   ├─ Initialize browser (Chrome/Edge/Firefox)               │ │
│ │   ├─ Load cookies (1s + 2s + 2s = 5s)                       │ │
│ │   └─ Verify Herald access                                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Connected?      │
                    └─────────┬─────────┘
                         Yes  │  No
                              │  └──────> Return (False, error, "")
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: SEARCH URL CONSTRUCTION (<1ms)                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ If realm_filter:                                            │ │
│ │   URL = "herald?n=search&r={realm}&s={character_name}"     │ │
│ │ Else:                                                        │ │
│ │   URL = "herald?n=search&s={character_name}"               │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: PAGE NAVIGATION & LOAD (5s)                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ scraper.driver.get(search_url)                              │ │
│ │ time.sleep(5)  ← Wait for page to fully load                │ │
│ │ page_source = scraper.driver.page_source                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: HTML PARSING & EXTRACTION (<1s)                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ soup = BeautifulSoup(page_source, 'html.parser')           │ │
│ │                                                              │ │
│ │ FOR each table in page:                                     │ │
│ │   FOR each row (skip header):                               │ │
│ │     Extract cells:                                          │ │
│ │       - col_0: Rank                                         │ │
│ │       - col_1: Name (with URL link)                         │ │
│ │       - col_3: Class                                        │ │
│ │       - col_5: Race                                         │ │
│ │       - col_7: Guild                                        │ │
│ │       - col_8: Level                                        │ │
│ │       - col_9: Realm Points                                 │ │
│ │       - col_10: Realm Rank (title text)                     │ │
│ │       - col_11: Realm Level (code XLY)                      │ │
│ │     Extract URL from col_1_links                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: FILE MANAGEMENT (<1s)                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ temp_dir = /tmp/EdenSearchResult/ (or OS temp folder)      │ │
│ │                                                              │ │
│ │ Clean old files:                                            │ │
│ │   FOR each *.json in temp_dir:                              │ │
│ │     Delete old search results                               │ │
│ │                                                              │ │
│ │ Save raw search data:                                       │ │
│ │   File: search_{character_name}_{timestamp}.json           │ │
│ │   Content: Raw table data + metadata                        │ │
│ │                                                              │ │
│ │ Save formatted characters:                                  │ │
│ │   File: characters_{character_name}_{timestamp}.json       │ │
│ │   Content: Structured character objects                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: CLEANUP & RETURN (<1s)                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ FINALLY block (always executed):                            │ │
│ │   scraper.close()  ← Close browser cleanly                  │ │
│ │                                                              │ │
│ │ Return:                                                      │ │
│ │   (True, "X personnage(s) trouvé(s)", json_path)           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        [ END ]

TOTAL TIME: ~11-14 seconds
  - Connection: 5-8s
  - Navigation: 5s
  - Processing: 1-2s
```

---

## Detailed Phase Breakdown

### PHASE 1: Connection to Herald (5-8 seconds)

**Purpose**: Establish authenticated session with Eden Herald

**Implementation**:
```python
scraper, error_message = _connect_to_eden_herald(headless=False)

if not scraper:
    return False, error_message, ""
```

**What happens**:
1. Verify cookies exist on disk
2. Validate cookies are not expired
3. Initialize Selenium WebDriver (Chrome/Edge/Firefox)
4. Load cookies into browser (3 timeouts: 1s + 2s + 2s)
5. Navigate to Herald to verify authentication
6. Return authenticated scraper instance

**Failure Points**:
- ❌ No cookies found → `"Aucun cookie trouvé"`
- ❌ Cookies expired → `"Les cookies ont expiré"`
- ❌ Browser initialization failed → `"Impossible d'initialiser le navigateur"`
- ❌ Cookie loading failed → `"Impossible de charger les cookies"`

**See Also**: [CONNECT_TO_EDEN_HERALD_EN.md](CONNECT_TO_EDEN_HERALD_EN.md)

---

### PHASE 2: Search URL Construction (<1ms)

**Purpose**: Build Herald search URL with parameters

**Logic**:
```python
if realm_filter:
    search_url = f"https://eden-daoc.net/herald?n=search&r={realm_filter}&s={character_name}"
else:
    search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
```

**URL Parameters**:
- `n=search` - Page type (search results)
- `r={realm}` - Realm filter (optional): `alb`, `mid`, `hib`
- `s={name}` - Search query (character name, partial match)

**Examples**:
```
All realms: https://eden-daoc.net/herald?n=search&s=PlayerName
Albion only: https://eden-daoc.net/herald?n=search&r=alb&s=PlayerName
Midgard only: https://eden-daoc.net/herald?n=search&r=mid&s=PlayerName
```

---

### PHASE 3: Page Navigation & Load (5 seconds)

**Purpose**: Navigate to search page and wait for full load

**Implementation**:
```python
scraper.driver.get(search_url)  # Navigate to search URL

module_logger.info("Waiting for page to fully load (5 seconds)...")
time.sleep(5)  # CRITICAL TIMEOUT

page_source = scraper.driver.page_source  # Extract HTML
soup = BeautifulSoup(page_source, 'html.parser')  # Parse HTML
```

**Why 5 seconds?**:
- Herald pages include dynamic content
- JavaScript needs time to execute
- Tables need time to render
- Too short = incomplete data
- Too long = wasted time

**Optimization**: This timeout could be made configurable in future versions

**Data Retrieved**:
- Complete HTML page source
- All character tables
- Character URLs (links)
- Metadata (rank, class, race, etc.)

---

### PHASE 4: HTML Parsing & Extraction (<1 second)

**Purpose**: Extract character data from HTML tables

#### 4.1: Raw Table Extraction

```python
search_data = {
    'character_name': character_name,
    'search_url': search_url,
    'timestamp': datetime.now().isoformat(),
    'results': []
}

tables = soup.find_all('table')
for table in tables:
    rows = table.find_all('tr')
    if len(rows) > 1:  # At least header + 1 row
        headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
        
        for row in rows[1:]:  # Skip header row
            cells = row.find_all('td')
            if cells:
                result = {}
                for idx, cell in enumerate(cells):
                    header = headers[idx] if idx < len(headers) else f"col_{idx}"
                    result[header] = cell.get_text(strip=True)
                    
                    # Extract links from cells
                    links = cell.find_all('a')
                    if links:
                        result[f"{header}_links"] = [a.get('href', '') for a in links]
                
                if result:
                    search_data['results'].append(result)
```

**Raw Result Structure**:
```json
{
  "character_name": "PlayerName",
  "search_url": "https://eden-daoc.net/herald?n=search&s=PlayerName",
  "timestamp": "2025-11-13T14:30:52.123456",
  "results": [
    {
      "col_0": "1234",
      "col_1": "PlayerName (Title)",
      "col_1_links": ["?n=player&k=PlayerName"],
      "col_3": "Armsman",
      "col_5": "Briton",
      "col_7": "GuildName",
      "col_8": "50",
      "col_9": "1 234 567",
      "col_10": "Stormur Vakten",
      "col_11": "5L2"
    }
  ]
}
```

#### 4.2: Character Formatting

**Validation Criteria** (must ALL be true):
```python
if (result.get('col_1') and                  # Has name
    result.get('col_3') and                  # Has class
    len(result.get('col_1', '')) > 0 and     # Name not empty
    result.get('col_0') and                  # Has rank
    result.get('col_0', '').isdigit()):      # Rank is numeric
```

**Field Mapping**:
```python
rank = result.get('col_0', '')                # Herald rank
name = result.get('col_1', '').strip()        # Full name with title
char_class = result.get('col_3', '').strip()  # Class name
race = result.get('col_5', '').strip()        # Race name
guild = result.get('col_7', '').strip()       # Guild name
level = result.get('col_8', '').strip()       # Character level
rp = result.get('col_9', '').strip()          # Realm Points
realm_rank = result.get('col_10', '').strip() # Realm rank TITLE (text)
realm_level = result.get('col_11', '').strip()# Realm rank CODE (XLY)
```

**URL Extraction**:
```python
# Priority 1: Extract from HTML link
if 'col_1_links' in result and result['col_1_links']:
    href = result['col_1_links'][0]
    # Build complete URL
    if href.startswith('?'):
        url = f"https://eden-daoc.net/herald{href}"
    elif href.startswith('/'):
        url = f"https://eden-daoc.net{href}"
    elif not href.startswith('http'):
        url = f"https://eden-daoc.net/herald?{href}"
    else:
        url = href
else:
    # Priority 2: Build URL from character name
    clean_name = name.split()[0]  # Remove title
    url = f"https://eden-daoc.net/herald?n=player&k={clean_name}"
```

**Formatted Character Object**:
```json
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
```

---

### PHASE 5: File Management (<1 second)

#### 5.1: Temporary Directory

**Location**:
```python
import tempfile
temp_dir = Path(tempfile.gettempdir()) / "EdenSearchResult"
temp_dir.mkdir(exist_ok=True)
```

**Platform-Specific Paths**:
- **Windows**: `C:\Users\{username}\AppData\Local\Temp\EdenSearchResult\`
- **Linux**: `/tmp/EdenSearchResult/`
- **macOS**: `/var/folders/.../T/EdenSearchResult/`

**Why Temporary Folder?**:
- ✅ Automatic OS cleanup
- ✅ No workspace pollution
- ✅ Platform-independent
- ✅ No permission issues

#### 5.2: Old File Cleanup

**Purpose**: Remove previous search results to avoid confusion

```python
old_files_list = list(temp_dir.glob("*.json"))
if old_files_list:
    for old_file in old_files_list:
        try:
            old_file.unlink()  # Delete file
        except Exception as e:
            # Log warning but continue (non-critical)
            module_logger.warning(f"Cannot delete {old_file.name}: {e}")
```

**Files Removed**:
- All `*.json` files in temp directory
- Both raw search data and formatted character files
- Only from this specific temp folder (isolated)

#### 5.3: File Creation

**File 1: Raw Search Data**
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
json_filename = f"search_{character_name}_{timestamp}.json"
json_path = temp_dir / json_filename

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(search_data, f, indent=2, ensure_ascii=False)
```

**Example Filename**: `search_PlayerName_20251113_143052.json`

**Content Structure**:
```json
{
  "character_name": "PlayerName",
  "search_url": "https://eden-daoc.net/herald?n=search&s=PlayerName",
  "timestamp": "2025-11-13T14:30:52.123456",
  "results": [
    {
      "col_0": "1234",
      "col_1": "PlayerName (Title)",
      "col_1_links": ["?n=player&k=PlayerName"],
      ...
    }
  ]
}
```

**File 2: Formatted Characters** (PRIMARY OUTPUT)
```python
characters_filename = f"characters_{character_name}_{timestamp}.json"
characters_path = temp_dir / characters_filename

with open(characters_path, 'w', encoding='utf-8') as f:
    json.dump({
        'search_query': character_name,
        'search_url': search_url,
        'timestamp': search_data['timestamp'],
        'characters': characters  # Formatted character list
    }, f, indent=2, ensure_ascii=False)
```

**Example Filename**: `characters_PlayerName_20251113_143052.json`

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

**Return Value**: Path to formatted characters file (File 2)

---

### PHASE 6: Cleanup & Return (<1 second)

**Purpose**: Ensure browser is closed properly, even if errors occurred

**Implementation**:
```python
finally:
    # ALWAYS executed, even after return or exception
    if scraper:
        try:
            scraper.close()  # Close browser
            module_logger.debug("Scraper closed cleanly")
        except Exception as e:
            module_logger.warning(f"Error closing scraper: {e}")
```

**Why `finally` block?**:
- ✅ Guarantees browser cleanup
- ✅ Prevents browser zombie processes
- ✅ Releases system resources
- ✅ Executes even if exception thrown
- ✅ Executes even after early return

**Success Return**:
```python
return True, f"{char_count} personnage(s) trouvé(s)", str(characters_path)
```

**Failure Return**:
```python
return False, f"Erreur: {str(e)}", ""
```

---

## Usage Examples

### Example 1: Basic Search (All Realms)

```python
from Functions.eden_scraper import search_herald_character

# Search for character across all realms
success, message, json_path = search_herald_character("PlayerName")

if success:
    print(f"✅ {message}")
    print(f"📁 Results: {json_path}")
    
    # Load and process results
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for character in data['characters']:
        print(f"Found: {character['name']} - {character['class']} ({character['realm_points']} RP)")
else:
    print(f"❌ Search failed: {message}")
```

**Output**:
```
✅ 3 personnage(s) trouvé(s)
📁 Results: /tmp/EdenSearchResult/characters_PlayerName_20251113_143052.json
Found: PlayerName (Stormur Vakten) - Armsman (1 234 567 RP)
Found: PlayerName2 (Title) - Cleric (456 789 RP)
Found: PlayerName3 (Title) - Wizard (123 456 RP)
```

---

### Example 2: Realm-Filtered Search

```python
# Search only in Albion
success, message, json_path = search_herald_character("Player", realm_filter="alb")

# Search only in Midgard
success, message, json_path = search_herald_character("Player", realm_filter="mid")

# Search only in Hibernia
success, message, json_path = search_herald_character("Player", realm_filter="hib")
```

---

### Example 3: Error Handling

```python
success, message, json_path = search_herald_character("PlayerName")

if not success:
    if "cookie" in message.lower():
        print("⚠️ Cookie issue - regenerate cookies via Cookie Manager")
    elif "navigateur" in message.lower() or "browser" in message.lower():
        print("⚠️ Browser issue - install Chrome, Edge, or Firefox")
    else:
        print(f"❌ Unknown error: {message}")
    
    # Do NOT attempt to open json_path (it's empty string)
else:
    # Safe to process results
    process_results(json_path)
```

---

### Example 4: Integration with UI

```python
from PyQt6.QtWidgets import QPushButton, QMessageBox

def on_search_clicked(self):
    """Button click handler in character search dialog"""
    character_name = self.name_input.text().strip()
    realm = self.realm_combo.currentData()  # "alb", "mid", "hib", or ""
    
    if not character_name:
        QMessageBox.warning(self, "Invalid Input", "Please enter a character name")
        return
    
    # Disable button during search
    self.search_button.setEnabled(False)
    self.search_button.setText("⏳ Searching...")
    
    # Execute search
    success, message, json_path = search_herald_character(character_name, realm)
    
    # Re-enable button
    self.search_button.setEnabled(True)
    self.search_button.setText("🔍 Search")
    
    if success:
        # Load results and populate table
        self.load_search_results(json_path)
        QMessageBox.information(self, "Success", message)
    else:
        QMessageBox.critical(self, "Search Failed", message)
```

---

## Performance Characteristics

### Timing Breakdown

| Phase | Duration | Percentage | Can Optimize? |
|-------|----------|------------|---------------|
| Connection | 5-8s | 45-57% | ⚠️ Partially (timeout tuning) |
| URL Construction | <1ms | <0.1% | ✅ Already optimal |
| Navigation | 5s | 36-45% | ⚠️ Partially (timeout tuning) |
| HTML Parsing | 0.5-1s | 4-9% | ✅ Already efficient |
| File Operations | 0.1-0.5s | 1-4% | ✅ Already efficient |
| Cleanup | 0.1s | <1% | ✅ Already efficient |
| **TOTAL** | **11-14s** | **100%** | **⚠️ Timeouts configurable** |

### Scalability

**Single Character Search**:
- Time: 11-14 seconds
- Memory: ~150-300 MB (browser)
- CPU: Low (idle most of time waiting for page load)

**Multiple Searches** (sequential):
- 10 searches: ~2-3 minutes
- Recommendation: Keep browser open between searches (reuse scraper)

**Optimization Strategy**:
```python
from Functions.eden_scraper import _connect_to_eden_herald
import time

# Connect once
scraper, error = _connect_to_eden_herald(headless=False)

if scraper:
    # Perform multiple searches reusing same browser
    for name in ["Player1", "Player2", "Player3"]:
        scraper.driver.get(f"https://eden-daoc.net/herald?n=search&s={name}")
        time.sleep(5)
        # Extract data...
    
    # Close once at end
    scraper.close()
```

---

## Error Handling

### Exception Safety

**Guarantees**:
- ✅ Browser always closed (via `finally` block)
- ✅ No browser zombie processes
- ✅ Always returns tuple (never raises exception to caller)
- ✅ Detailed error logging

**Error Propagation**:
```python
try:
    # All phases of execution
    return True, message, json_path
except Exception as e:
    module_logger.error(f"❌ Error: {e}", extra={"action": "SEARCH"})
    module_logger.error(f"Stacktrace: {traceback.format_exc()}")
    return False, f"Erreur: {str(e)}", ""
finally:
    # Cleanup ALWAYS happens
    if scraper:
        scraper.close()
```

### Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `"Aucun cookie trouvé"` | No cookie file exists | Generate or import cookies via Cookie Manager |
| `"Les cookies ont expiré"` | Cookies too old | Regenerate cookies (24-48h validity) |
| `"Impossible d'initialiser le navigateur"` | No browser installed | Install Chrome, Edge, or Firefox |
| `"Impossible de charger les cookies"` | Bot check detected or network issue | Check internet connection, try again |
| `"Erreur: [exception]"` | Unexpected error | Check logs in `Logs/eden.log` |

---

## Logging

### Log Locations

**File**: `Logs/eden.log`  
**Format**: JSON-structured with action tags

### Log Levels Used

| Level | When | Example |
|-------|------|---------|
| `INFO` | Normal operation milestones | `"Début de la recherche Herald pour: PlayerName"` |
| `DEBUG` | Detailed internal state | `"Personnage extrait: PlayerName - URL: ..."` |
| `WARNING` | Non-critical issues | `"Impossible de supprimer ancien fichier"` |
| `ERROR` | Critical failures | `"❌ Erreur lors de la recherche Herald: ..."` |

### Example Log Sequence

```log
2025-11-13 14:30:45 [INFO] [SEARCH] Début de la recherche Herald pour: PlayerName
2025-11-13 14:30:45 [INFO] [CONNECT] Cookies valides - 12 cookies chargés
2025-11-13 14:30:47 [INFO] [CONNECT] Navigateur initialisé avec succès
2025-11-13 14:30:52 [INFO] [CONNECT] ✅ Connexion au Herald Eden établie avec succès
2025-11-13 14:30:52 [INFO] [SEARCH] Connexion établie - Début de la recherche
2025-11-13 14:30:52 [INFO] [SEARCH] Recherche Herald: https://eden-daoc.net/herald?n=search&s=PlayerName
2025-11-13 14:30:52 [INFO] [SEARCH] Attente du chargement de la page de recherche (5 secondes)...
2025-11-13 14:30:57 [INFO] [SEARCH] Page chargée - Taille: 45678 caractères
2025-11-13 14:30:57 [DEBUG] [PARSE] Personnage extrait: PlayerName - URL: https://eden-daoc.net/herald?n=player&k=PlayerName
2025-11-13 14:30:57 [INFO] [CLEANUP] Dossier temporaire: /tmp/EdenSearchResult
2025-11-13 14:30:57 [INFO] [CLEANUP] Nettoyage de 2 fichier(s) ancien(s)...
2025-11-13 14:30:57 [INFO] [CLEANUP] ✅ Fichier supprimé: search_OldPlayer_20251112_120000.json
2025-11-13 14:30:57 [INFO] [CLEANUP] ✅ Fichier supprimé: characters_OldPlayer_20251112_120000.json
2025-11-13 14:30:57 [INFO] [SEARCH] Recherche terminée: 3 personnages trouvés
2025-11-13 14:30:57 [INFO] [SEARCH] Résultats sauvegardés dans: /tmp/EdenSearchResult/characters_PlayerName_20251113_143052.json
2025-11-13 14:30:57 [DEBUG] [CLEANUP] Scraper fermé proprement
```

---

## Dependencies

### Required Modules

```python
import time                          # Time delays for page loading
import json                          # JSON file reading/writing
import tempfile                      # OS temporary directory
from pathlib import Path             # File path manipulation
from datetime import datetime        # Timestamp generation
from bs4 import BeautifulSoup        # HTML parsing

from Functions.logging_manager import get_logger  # Logging system
from Functions.eden_scraper import _connect_to_eden_herald  # Connection function
```

### External Dependencies

- **Selenium**: WebDriver automation
- **BeautifulSoup4**: HTML parsing
- **Chrome/Edge/Firefox**: One browser must be installed
- **Valid Cookies**: Must exist and not be expired

---

## Related Functions

### 1. `_connect_to_eden_herald()`
- **Purpose**: Establishes authenticated connection
- **Called by**: `search_herald_character()` at start of execution
- **Documentation**: [CONNECT_TO_EDEN_HERALD_EN.md](CONNECT_TO_EDEN_HERALD_EN.md)

### 2. `scrape_character_from_url()`
- **Purpose**: Updates character data from Herald URL
- **Relation**: Uses same connection logic, different scraping target
- **Documentation**: [SCRAPE_CHARACTER_FROM_URL_EN.md](SCRAPE_CHARACTER_FROM_URL_EN.md)

### 3. `CharacterProfileScraper.connect()`
- **Purpose**: Profile scraping for RvR/PvP/PvE stats
- **Relation**: Uses same connection logic via wrapper
- **Documentation**: [CHARACTER_PROFILE_SCRAPER_EN.md](CHARACTER_PROFILE_SCRAPER_EN.md)

---

## Testing Recommendations

### Unit Tests

```python
def test_search_herald_character_success():
    """Test successful character search"""
    success, message, json_path = search_herald_character("TestPlayer")
    
    assert success == True
    assert "personnage(s) trouvé(s)" in message
    assert json_path.endswith(".json")
    assert Path(json_path).exists()
    
    # Verify JSON structure
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert 'search_query' in data
    assert 'characters' in data
    assert isinstance(data['characters'], list)

def test_search_herald_character_realm_filter():
    """Test realm-filtered search"""
    success, message, json_path = search_herald_character("Player", realm_filter="alb")
    
    assert success == True
    assert "?n=search&r=alb&s=" in json_path  # Verify realm filter used

def test_search_herald_character_no_cookies():
    """Test failure when no cookies exist"""
    # Remove cookies temporarily
    success, message, json_path = search_herald_character("Player")
    
    assert success == False
    assert "cookie" in message.lower()
    assert json_path == ""
```

### Integration Tests

```python
def test_full_search_workflow():
    """End-to-end test of search → parse → file creation"""
    character_name = "TestPlayer"
    
    # Execute search
    success, message, json_path = search_herald_character(character_name)
    
    if not success:
        pytest.skip(f"Search failed: {message}")
    
    # Verify file exists
    assert Path(json_path).exists()
    
    # Verify file content structure
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data['search_query'] == character_name
    assert 'characters' in data
    
    if data['characters']:
        char = data['characters'][0]
        assert 'name' in char
        assert 'class' in char
        assert 'level' in char
        assert 'url' in char
```

---

## Troubleshooting

### Issue: "Aucun cookie trouvé"

**Cause**: Cookie file doesn't exist  
**Solution**:
1. Open Cookie Manager in application
2. Either generate new cookies OR import from browser
3. Verify cookie file exists: `Configuration/cookies.json`
4. Retry search

---

### Issue: "Les cookies ont expiré"

**Cause**: Cookies older than 24-48 hours  
**Solution**:
1. Open Cookie Manager
2. Click "Generate Cookies" to create fresh ones
3. Retry search

**Prevention**: Regenerate cookies daily if using application frequently

---

### Issue: Search takes >20 seconds

**Cause**: Slow internet connection or Herald server slow  
**Possible Solutions**:
1. Check internet connection speed
2. Try again later (Herald might be busy)
3. Future: Make timeouts configurable in config.json

---

### Issue: "0 personnage(s) trouvé(s)" but character exists

**Causes**:
1. Character name misspelled
2. Character not on Eden server
3. Character recently deleted
4. Herald page structure changed

**Debug Steps**:
1. Check character name spelling
2. Verify character exists on https://eden-daoc.net/herald manually
3. Check `Logs/eden.log` for parsing errors
4. Inspect raw search results file (`search_*.json`)

---

### Issue: Browser doesn't close after search

**Cause**: Exception before cleanup or zombie process  
**Solution**:
1. Check `Logs/eden.log` for errors
2. Manually close browser process in Task Manager
3. Report bug with log excerpt

**Prevention**: Function uses `finally` block to prevent this, but bugs can occur

---

## Security Considerations

### Cookie Security

- **Storage**: Plain text in `Configuration/cookies.json`
- **Validity**: 24-48 hours typically
- **Risk**: Low (limited session tokens)
- **Recommendation**: Don't share cookie file

### Browser Session

- **Visibility**: Browser window visible (`headless=False`)
- **Reason**: Avoid bot detection
- **Risk**: Low (only Herald access)
- **Cleanup**: Always closed via `finally` block

### File Security

- **Location**: OS temporary folder (public access on multi-user systems)
- **Content**: Character names, stats, URLs (public Herald data)
- **Cleanup**: Old files auto-deleted on next search
- **Risk**: Low (no sensitive data)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-13 | Initial documentation - function refactored to use `_connect_to_eden_herald()` |

---

## Related Documentation

- **Connection Function**: [CONNECT_TO_EDEN_HERALD_EN.md](CONNECT_TO_EDEN_HERALD_EN.md)
- **Update Function**: [SCRAPE_CHARACTER_FROM_URL_EN.md](SCRAPE_CHARACTER_FROM_URL_EN.md)
- **Profile Scraper**: [CHARACTER_PROFILE_SCRAPER_EN.md](CHARACTER_PROFILE_SCRAPER_EN.md)
- **Cookie Manager**: `Documentation/COOKIE_MANAGER_EN.md` (if exists)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-13  
**Author**: Automated Documentation  
**Status**: ✅ Production Ready
