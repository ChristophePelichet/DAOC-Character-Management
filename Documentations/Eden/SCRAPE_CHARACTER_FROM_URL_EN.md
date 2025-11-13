# scrape_character_from_url() - Technical Documentation

## Function Overview

**Name**: `scrape_character_from_url(character_url, cookie_manager)`  
**Location**: `Functions/eden_scraper.py` (line ~677)  
**Purpose**: Update character data from Herald URL by performing targeted search and data normalization  
**Category**: Public API function for character update operations

---

## Function Signature

```python
def scrape_character_from_url(character_url, cookie_manager):
    """
    Retrieves character data from Herald URL
    Uses Herald search because direct page access is blocked (bot check)
    
    Args:
        character_url: Character Herald URL (contains name in &k= parameter)
        cookie_manager: CookieManager instance
        
    Returns:
        tuple: (success, data_dict, error_message)
    """
```

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `character_url` | `str` | ✅ Yes | Full Herald URL (e.g., `https://eden-daoc.net/herald?n=player&k=PlayerName`) |
| `cookie_manager` | `CookieManager` | ✅ Yes | CookieManager instance for authentication |

**URL Format Requirements**:
- Must contain `&k=` or `?k=` parameter with character name
- Example: `https://eden-daoc.net/herald?n=player&k=PlayerName`
- Name extraction via URL parsing (not direct page scraping)

---

## Return Value

**Type**: `tuple(bool, dict | None, str)`

### Success Case
```python
(True, {
    'name': 'PlayerName (Stormur Vakten)',
    'clean_name': 'PlayerName',
    'level': 50,
    'class': 'Armsman',
    'race': 'Briton',
    'realm': 'Albion',
    'guild': 'GuildName',
    'realm_points': 1234567,
    'realm_rank': '5L2',
    'realm_title': 'Stormur Vakten',
    'server': 'Eden',
    'url': 'https://eden-daoc.net/herald?n=player&k=PlayerName',
    'rank': '1234'
}, "")
```

| Index | Type | Description |
|-------|------|-------------|
| `[0]` | `bool` | `True` - Operation succeeded |
| `[1]` | `dict` | Normalized character data dictionary |
| `[2]` | `str` | Empty string (no error) |

### Failure Case
```python
(False, None, "Impossible d'extraire le nom du personnage de l'URL")
```

| Index | Type | Description |
|-------|------|-------------|
| `[0]` | `bool` | `False` - Operation failed |
| `[1]` | `None` | No data (null) |
| `[2]` | `str` | Error message describing the failure |

---

## Key Design Decision: Why Search Instead of Direct Access?

**Problem**: Direct access to character pages triggers bot check:
```
https://eden-daoc.net/herald?n=player&k=PlayerName
→ Bot check page (blocked)
```

**Solution**: Extract name from URL, search via Herald search page:
```
URL: https://eden-daoc.net/herald?n=player&k=PlayerName
Extract: "PlayerName"
Search: https://eden-daoc.net/herald?n=search&s=PlayerName
→ Works! (search page not blocked)
```

**Trade-off**:
- ✅ Avoids bot check
- ✅ Reuses existing search infrastructure
- ✅ Consistent with `search_herald_character()`
- ⚠️ Slightly slower (search instead of direct access)
- ⚠️ May return multiple matches (must filter)

---

## Execution Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                  scrape_character_from_url()                     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: URL PARSING (<1ms)                                       │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Input: https://eden-daoc.net/herald?n=player&k=PlayerName   │ │
│ │                                                               │ │
│ │ from urllib.parse import urlparse, parse_qs                  │ │
│ │ parsed_url = urlparse(character_url)                         │ │
│ │ query_params = parse_qs(parsed_url.query)                    │ │
│ │ character_name = query_params.get('k', [''])[0]              │ │
│ │                                                               │ │
│ │ Output: "PlayerName"                                         │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Name extracted?   │
                    └─────────┬─────────┘
                         Yes  │  No
                              │  └──────> Return (False, None, error)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEPS 2-7: CONNECTION (5-8s)                                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ scraper, error_message = _connect_to_eden_herald(           │ │
│ │     cookie_manager=cookie_manager,                           │ │
│ │     headless=False                                           │ │
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
                              │  └──────> Return (False, None, error)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 8: SEARCH URL CONSTRUCTION (<1ms)                          │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ search_url = f"https://eden-daoc.net/herald?n=search&       │ │
│ │                s={character_name}"                           │ │
│ │                                                               │ │
│ │ Example: https://eden-daoc.net/herald?n=search&s=PlayerName │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 9: NAVIGATE TO SEARCH PAGE (<1s)                           │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ scraper.driver.get(search_url)                               │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 10: WAIT FOR PAGE LOAD (5s)                                │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ time.sleep(5)  ← Wait for search results to load             │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 11: EXTRACT HTML (<1s)                                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ page_source = scraper.driver.page_source                     │ │
│ │ soup = BeautifulSoup(page_source, 'html.parser')            │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 12: PARSE SEARCH RESULTS (<1s)                             │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ IDENTICAL TO search_herald_character():                      │ │
│ │                                                               │ │
│ │ FOR each table:                                              │ │
│ │   FOR each row (skip header):                                │ │
│ │     Extract: rank, name, class, race, guild, level, RP, RR  │ │
│ │     Extract URL from links                                   │ │
│ │     Build character dict                                     │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 13: FORMAT CHARACTERS (<1s)                                │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Same parsing as search_herald_character()                    │ │
│ │                                                               │ │
│ │ Result: characters = [                                       │ │
│ │   {'rank': '1234', 'name': 'PlayerName', ...},              │ │
│ │   {'rank': '5678', 'name': 'PlayerName2', ...},             │ │
│ │   ...                                                         │ │
│ │ ]                                                             │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Characters found? │
                    └─────────┬─────────┘
                         Yes  │  No
                              │  └──────> Return (False, None, error)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 14: FIND TARGET CHARACTER (<1ms)                           │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Strategy 1: Exact match (case-insensitive)                   │ │
│ │   FOR each char in characters:                               │ │
│ │     IF char['clean_name'].lower() == character_name.lower(): │ │
│ │       target_char = char                                     │ │
│ │       BREAK                                                   │ │
│ │                                                               │ │
│ │ Strategy 2: Fallback to first result                         │ │
│ │   IF not target_char AND characters:                         │ │
│ │     target_char = characters[0]                              │ │
│ │     LOG WARNING: "No exact match, using first result"        │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Target found?     │
                    └─────────┬─────────┘
                         Yes  │  No
                              │  └──────> Return (False, None, error)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 15: NORMALIZE DATA (<1ms)                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ normalized_data = _normalize_herald_data(target_char)        │ │
│ │                                                               │ │
│ │ Performs:                                                     │ │
│ │   ├─ Determine realm from class name                         │ │
│ │   ├─ Clean realm_points (remove spaces, commas)              │ │
│ │   ├─ Convert level to int                                    │ │
│ │   ├─ SWAP realm_rank ↔ realm_title (Herald inconsistency)   │ │
│ │   └─ Add server='Eden'                                       │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 16: CLEANUP & RETURN (<1s)                                 │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ FINALLY block (always executed):                             │ │
│ │   IF scraper:                                                 │ │
│ │     scraper.close()  ← Close browser                         │ │
│ │                                                               │ │
│ │ Return:                                                       │ │
│ │   (True, normalized_data, "")                                │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        [ END ]

TOTAL TIME: ~11-14 seconds
  - URL parsing: <1ms
  - Connection: 5-8s
  - Navigation: 5s
  - Processing: 1-2s
  - Cleanup: <1s
```

---

## Comparison: search_herald_character() vs scrape_character_from_url()

| Aspect | `search_herald_character()` | `scrape_character_from_url()` |
|--------|----------------------------|-------------------------------|
| **Input** | Character name (string) | Herald URL (string) |
| **Output** | JSON file path | Normalized dict |
| **Connection** | ✅ Uses `_connect_to_eden_herald()` | ✅ Uses `_connect_to_eden_herald()` |
| **Search** | Direct search | Extract name from URL, then search |
| **Realm filter** | ✅ Supported | ❌ Not supported |
| **Result count** | All matches | First exact match (or first result) |
| **File output** | ✅ 2 JSON files | ❌ No files |
| **Data format** | Raw + formatted lists | Single normalized dict |
| **Use case** | User search, list multiple results | Update existing character |

**Shared Code** (Steps 8-13):
- Both use `_connect_to_eden_herald()` for connection
- Both navigate to search page (not direct character page)
- Both parse HTML tables identically
- Both extract same character fields

**Key Difference** (Step 14-15):
- `search_herald_character()`: Returns ALL characters + saves to JSON
- `scrape_character_from_url()`: Filters to ONE character + normalizes data

---

## Data Normalization Details

### _normalize_herald_data() Function

**Purpose**: Convert raw search data to application-friendly format

**Input** (raw search result):
```python
{
    'rank': '1234',
    'name': 'PlayerName (Stormur Vakten)',
    'clean_name': 'PlayerName',
    'class': 'Armsman',
    'race': 'Briton',
    'guild': 'GuildName',
    'level': '50',
    'realm_points': '1 234 567',
    'realm_rank': 'Stormur Vakten',  # Herald: Title text
    'realm_level': '5L2',            # Herald: Code
    'url': 'https://eden-daoc.net/herald?n=player&k=PlayerName'
}
```

**Transformations**:

1. **Realm Determination** (from class):
```python
class_to_realm = {
    'Armsman': 'Albion', 'Cabalist': 'Albion', ...,
    'Berserker': 'Midgard', 'Bonedancer': 'Midgard', ...,
    'Animist': 'Hibernia', 'Bard': 'Hibernia', ...
}
realm = class_to_realm.get(char_class, 'Unknown')
```

2. **Realm Points Cleaning**:
```python
realm_points = '1 234 567'
realm_points = realm_points.replace(' ', '').replace(',', '')  # Remove separators
realm_points = int(realm_points)  # Convert to integer
# Result: 1234567
```

3. **Level Conversion**:
```python
level = '50'
level = int(level)  # Convert to integer
# Result: 50
```

4. **Realm Rank Field Swap** (CRITICAL):
```python
# PROBLEM: Herald's naming is backwards!
# Herald JSON:
#   realm_rank = "Stormur Vakten" (title text)
#   realm_level = "5L2" (code)
#
# Our application expects:
#   realm_rank = "5L2" (code)
#   realm_title = "Stormur Vakten" (title text)
#
# SOLUTION: Swap the fields!

normalized = {
    'realm_rank': char_data.get('realm_level', '1L1'),  # Code (XLY) - SWAPPED
    'realm_title': char_data.get('realm_rank', ''),     # Title text - SWAPPED
    ...
}
```

**Output** (normalized):
```python
{
    'name': 'PlayerName (Stormur Vakten)',
    'clean_name': 'PlayerName',
    'level': 50,                          # int
    'class': 'Armsman',
    'race': 'Briton',
    'realm': 'Albion',                    # ADDED
    'guild': 'GuildName',
    'realm_points': 1234567,              # int
    'realm_rank': '5L2',                  # SWAPPED
    'realm_title': 'Stormur Vakten',      # SWAPPED
    'server': 'Eden',                     # ADDED
    'url': 'https://eden-daoc.net/herald?n=player&k=PlayerName',
    'rank': '1234'
}
```

---

## Usage Examples

### Example 1: Basic Update

```python
from Functions.eden_scraper import scrape_character_from_url
from Functions.cookie_manager import CookieManager

# Initialize cookie manager
cookie_manager = CookieManager()

# Character URL from Herald
url = "https://eden-daoc.net/herald?n=player&k=PlayerName"

# Update character data
success, data, error = scrape_character_from_url(url, cookie_manager)

if success:
    print(f"✅ Character updated: {data['name']}")
    print(f"   Level: {data['level']}")
    print(f"   Class: {data['class']}")
    print(f"   Realm Points: {data['realm_points']:,}")
    print(f"   Realm Rank: {data['realm_rank']} ({data['realm_title']})")
else:
    print(f"❌ Update failed: {error}")
```

**Output**:
```
✅ Character updated: PlayerName (Stormur Vakten)
   Level: 50
   Class: Armsman
   Realm Points: 1,234,567
   Realm Rank: 5L2 (Stormur Vakten)
```

---

### Example 2: Integration with Character Manager

```python
def update_character_from_herald(self, character_id):
    """Update character data from Herald in character management system"""
    
    # Get character from database
    character = self.character_manager.get_character(character_id)
    
    if not character or not character.get('url'):
        QMessageBox.warning(self, "Error", "Character has no Herald URL")
        return
    
    # Update from Herald
    from Functions.eden_scraper import scrape_character_from_url
    from Functions.cookie_manager import CookieManager
    
    cookie_manager = CookieManager()
    success, data, error = scrape_character_from_url(character['url'], cookie_manager)
    
    if success:
        # Update character fields
        character['level'] = data['level']
        character['realm_points'] = data['realm_points']
        character['realm_rank'] = data['realm_rank']
        character['realm_title'] = data['realm_title']
        character['guild'] = data['guild']
        character['last_updated'] = datetime.now().isoformat()
        
        # Save to database
        self.character_manager.update_character(character_id, character)
        
        QMessageBox.information(self, "Success", f"Character {data['name']} updated!")
    else:
        QMessageBox.critical(self, "Update Failed", error)
```

---

### Example 3: Batch Update

```python
def batch_update_characters(character_urls):
    """Update multiple characters from Herald URLs"""
    from Functions.eden_scraper import _connect_to_eden_herald
    from Functions.cookie_manager import CookieManager
    import time
    
    cookie_manager = CookieManager()
    results = []
    
    # Connect once for all updates
    scraper, error = _connect_to_eden_herald(cookie_manager=cookie_manager, headless=False)
    
    if not scraper:
        return [(False, None, error) for _ in character_urls]
    
    try:
        for url in character_urls:
            # Extract character name
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            character_name = params.get('k', [''])[0]
            
            if not character_name:
                results.append((False, None, "Invalid URL"))
                continue
            
            # Search for character (reuse connection)
            search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
            scraper.driver.get(search_url)
            time.sleep(5)
            
            # Extract and process data
            # ... (same as scrape_character_from_url steps 11-15)
            
            results.append((True, normalized_data, ""))
    
    finally:
        scraper.close()
    
    return results
```

---

## Performance Characteristics

### Timing Breakdown

| Phase | Duration | Description |
|-------|----------|-------------|
| URL Parsing | <1ms | Extract character name from URL |
| Connection | 5-8s | `_connect_to_eden_herald()` |
| Search Navigation | 5s | Navigate + wait for search results |
| HTML Extraction | <1s | Get page source + parse with BeautifulSoup |
| Character Matching | <1ms | Find target character in results |
| Data Normalization | <1ms | Format and clean data |
| Cleanup | <1s | Close browser |
| **TOTAL** | **11-14s** | **Complete update operation** |

**Comparison to search_herald_character()**:
- Same timing (both use identical search process)
- Difference: This returns single character, search returns all + saves JSON

---

## Error Handling

### Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `"Impossible d'extraire le nom du personnage de l'URL"` | URL missing `&k=` parameter | Verify URL format |
| `"Aucun cookie trouvé"` | No cookies exist | Generate cookies via Cookie Manager |
| `"Les cookies ont expiré"` | Cookies too old | Regenerate cookies |
| `"Aucun personnage trouvé pour '{name}'"` | Search returned no results | Check character exists on Eden |
| `"Personnage non trouvé dans les résultats"` | Character name mismatch | Verify character name in URL |

### Exception Safety

**Guarantees**:
- ✅ Browser always closed via `finally` block
- ✅ Always returns tuple (never raises to caller)
- ✅ Detailed error logging

```python
try:
    # All update steps
    return True, normalized_data, ""
except Exception as e:
    module_logger.error(f"❌ Error: {e}")
    module_logger.error(f"Stacktrace: {traceback.format_exc()}")
    return False, None, f"Erreur: {str(e)}"
finally:
    # Cleanup ALWAYS happens
    if scraper:
        scraper.close()
```

---

## Logging

### Log File
**Location**: `Logs/eden.log`

### Example Log Sequence

```log
2025-11-13 15:45:12 [INFO] [UPDATE] Mise à jour du personnage: PlayerName depuis URL: https://eden-daoc.net/herald?n=player&k=PlayerName
2025-11-13 15:45:12 [INFO] [CONNECT] Cookies valides - 12 cookies chargés
2025-11-13 15:45:15 [INFO] [CONNECT] ✅ Connexion au Herald Eden établie avec succès
2025-11-13 15:45:15 [INFO] [UPDATE] Connexion établie - Début de la mise à jour
2025-11-13 15:45:15 [INFO] [UPDATE] Recherche Herald: https://eden-daoc.net/herald?n=search&s=PlayerName
2025-11-13 15:45:15 [INFO] [UPDATE] Attente du chargement de la page (5 secondes)...
2025-11-13 15:45:20 [INFO] [UPDATE] Page chargée - Taille: 45678 caractères
2025-11-13 15:45:20 [INFO] [UPDATE] Données récupérées pour: PlayerName (Stormur Vakten)
2025-11-13 15:45:20 [DEBUG] [CLEANUP] Scraper fermé proprement
```

---

## Dependencies

### Required Modules
```python
import time                          # Page load delays
from urllib.parse import urlparse, parse_qs  # URL parsing
from bs4 import BeautifulSoup        # HTML parsing

from Functions.logging_manager import get_logger
from Functions.eden_scraper import _connect_to_eden_herald, _normalize_herald_data
```

---

## Related Functions

1. **`_connect_to_eden_herald()`** - Establishes connection
2. **`search_herald_character()`** - Searches for characters
3. **`_normalize_herald_data()`** - Normalizes character data
4. **`CharacterProfileScraper.connect()`** - Profile scraping

---

## Troubleshooting

### Issue: "Pas de correspondance exacte, utilisation du premier résultat"

**Cause**: Character name in URL doesn't exactly match search result  
**Examples**:
- URL: `&k=PlayerName` → Search finds `PlayerName (Title)`
- Case mismatch: `&k=playername` → `PlayerName`

**Behavior**: Function uses first search result as fallback  
**Risk**: Low (usually correct character)

**Prevention**: Use exact character names in URLs

---

### Issue: Multiple characters with same name

**Scenario**: Two characters named "PlayerName" on different realms

**Current Behavior**:
1. Search returns both characters
2. Function picks first exact match (case-insensitive)
3. If no exact match, picks first result

**Limitation**: No realm filtering in this function

**Workaround**: Use `search_herald_character()` with `realm_filter` parameter

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-13 | Refactored to use `_connect_to_eden_herald()` instead of delegating to `search_herald_character()` |

---

## Related Documentation

- **Connection**: [CONNECT_TO_EDEN_HERALD_EN.md](CONNECT_TO_EDEN_HERALD_EN.md)
- **Search**: [SEARCH_HERALD_CHARACTER_EN.md](SEARCH_HERALD_CHARACTER_EN.md)
- **Profile Scraper**: [CHARACTER_PROFILE_SCRAPER_EN.md](CHARACTER_PROFILE_SCRAPER_EN.md)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-13  
**Author**: Automated Documentation  
**Status**: ✅ Production Ready
