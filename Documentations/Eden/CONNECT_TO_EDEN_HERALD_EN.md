# Eden Herald Connection Function - Technical Documentation

## Function: `_connect_to_eden_herald()`

### Overview
`_connect_to_eden_herald()` is a **core internal function** that establishes an authenticated connection to the Eden-DAOC Herald website. It centralizes all connection logic to ensure consistency across all scraping operations (search, update, character data retrieval).

**Location**: `Functions/eden_scraper.py` (line ~417)  
**Visibility**: Internal (prefix `_` indicates private function)  
**Purpose**: Single point of connection management for all Herald scraping operations

---

## Function Signature

```python
def _connect_to_eden_herald(cookie_manager=None, headless=False):
    """
    Fonction interne: Établit la connexion au Herald Eden
    Centralise les étapes 1-6 communes à toutes les fonctions de scraping
    
    Args:
        cookie_manager: Instance of CookieManager (created automatically if None)
        headless: Browser display mode (False for visible)
        
    Returns:
        tuple: (scraper: EdenScraper|None, error_message: str)
               If success: (scraper_instance, "")
               If failure: (None, "error message")
    """
```

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cookie_manager` | `CookieManager` or `None` | `None` | Instance of CookieManager for authentication. If `None`, a new instance is created automatically. |
| `headless` | `bool` | `False` | Browser display mode. `False` = visible browser (required for bot check avoidance), `True` = hidden browser. |

---

## Return Value

**Type**: `tuple(EdenScraper | None, str)`

**Success Case**:
```python
(scraper_instance, "")
# scraper_instance: Authenticated EdenScraper object with active browser session
# error_message: Empty string
```

**Failure Case**:
```python
(None, "Error description")
# scraper: None
# error_message: Descriptive error message explaining the failure
```

---

## Connection Workflow - 6 Steps

### **STEP 1: Cookie Manager Initialization**
```python
if cookie_manager is None:
    cookie_manager = CookieManager()
```
- Creates a new `CookieManager` instance if not provided
- Allows flexibility: caller can provide their own or let function create one

**Error Handling**: None (CookieManager creation always succeeds)

---

### **STEP 2: Cookie Existence Verification**
```python
if not cookie_manager.cookie_exists():
    return None, "No cookies found. Please generate or import cookies first."
```
- Checks if authentication cookies exist on disk
- **Critical**: Without cookies, Herald connection is impossible

**Failure Point**: Missing cookie file  
**User Action Required**: Generate or import cookies using Cookie Manager

---

### **STEP 3: Cookie Validity Verification**
```python
info = cookie_manager.get_cookie_info()
if not info or not info.get('is_valid'):
    return None, "Cookies have expired. Please regenerate them."
```
- Verifies cookies are not expired
- Checks cookie metadata (expiration date, count, etc.)

**Failure Point**: Expired cookies  
**User Action Required**: Regenerate cookies

---

### **STEP 4: Scraper Initialization**
```python
scraper = EdenScraper(cookie_manager)
```
- Creates an `EdenScraper` instance
- Links scraper to cookie manager for authentication
- **No browser launched yet** (just object creation)

**Error Handling**: Exception caught by outer try-except

---

### **STEP 5: Browser Driver Initialization**
```python
if not scraper.initialize_driver(headless=headless):
    return None, "Unable to initialize browser."
```
- Launches Selenium WebDriver (Chrome/Edge/Firefox)
- Creates browser instance for web navigation
- **Multi-browser fallback**: Tries Chrome → Edge → Firefox automatically
- **Visible mode required** (`headless=False`) to avoid bot check detection

**Timeouts**: None at this stage  
**Failure Point**: No compatible browser found  
**User Action Required**: Install Chrome, Edge, or Firefox

---

### **STEP 6: Cookie Loading into Browser**
```python
if not scraper.load_cookies():
    scraper.close()  # Clean up browser
    return None, "Unable to load cookies."
```
- Loads authentication cookies into the browser session
- Establishes authenticated session with Eden Herald
- **Includes 3 internal timeouts** (see details below)

**Critical Step**: This is where actual authentication happens

#### Internal Steps in `load_cookies()`:

**6a. Navigate to Root Domain**
```python
self.driver.get("https://eden-daoc.net/")
time.sleep(1)  # TIMEOUT #1
```
- Navigate to main Eden website
- **Wait**: 1 second for page load
- **Purpose**: Establish domain context for cookies

**6b. Add Cookies**
```python
for cookie in cookies_list:
    self.driver.add_cookie(cookie)
```
- Inject all stored cookies into browser
- **No timeout** (instant operation)

**6c. Refresh Page**
```python
self.driver.refresh()
time.sleep(2)  # TIMEOUT #2
```
- Refresh page to activate session
- **Wait**: 2 seconds for session activation
- **Purpose**: Apply cookies to active session

**6d. Navigate to Herald**
```python
self.driver.get("https://eden-daoc.net/herald")
time.sleep(2)  # TIMEOUT #3
```
- Navigate to Herald page (connection test)
- **Wait**: 2 seconds for Herald page load
- **Purpose**: Verify authentication worked

**6e. Verify Connection**
```python
html_content = self.driver.page_source
error_message = 'The requested page "herald" is not available.'
if error_message in html_content:
    return False  # Not connected
else:
    return True   # Connected successfully
```
- Check for error message in page content
- **Reliable indicator**: Absence of error = authenticated

---

## Total Connection Time

| Phase | Duration | Description |
|-------|----------|-------------|
| Step 1-4 | ~0s | Object creation (instant) |
| Step 5 | ~1-3s | Browser launch (varies by system) |
| Step 6a | 1s | Navigate to eden-daoc.net |
| Step 6b | ~0s | Add cookies (instant) |
| Step 6c | 2s | Refresh page |
| Step 6d | 2s | Navigate to Herald |
| **TOTAL** | **~6-8s** | **Full connection time** |

**Note**: Timeouts are hardcoded but could be externalized to config file in future versions.

---

## Error Handling

### Exception Management
```python
try:
    # All connection steps
    return scraper, ""
except Exception as e:
    module_logger.error(f"❌ Erreur lors de la connexion au Herald: {e}")
    return None, f"Erreur de connexion: {str(e)}"
```

**Strategy**: Catch-all exception handler  
**Return**: Always returns a tuple (never raises exceptions)  
**Logging**: All errors logged to `eden.log` with action tag "CONNECT"

### Failure Recovery
When `load_cookies()` fails, the browser is closed to prevent resource leaks:
```python
if not scraper.load_cookies():
    scraper.close()  # Clean up
    return None, "Unable to load cookies."
```

---

## Usage Examples

### Basic Usage (Automatic Cookie Manager)
```python
scraper, error = _connect_to_eden_herald(headless=False)

if scraper:
    # Connection successful - use scraper
    scraper.driver.get("https://eden-daoc.net/herald?n=search&s=PlayerName")
    # ... perform scraping ...
    scraper.close()
else:
    # Connection failed - show error
    print(f"Connection error: {error}")
```

### Advanced Usage (Custom Cookie Manager)
```python
from Functions.cookie_manager import CookieManager

cookie_manager = CookieManager()
scraper, error = _connect_to_eden_herald(
    cookie_manager=cookie_manager,
    headless=False
)

if scraper:
    # Perform operations
    scraper.close()
```

---

## Integration Points

### Functions Using `_connect_to_eden_herald()`

1. **`search_herald_character(character_name, realm_filter="")`**
   - **Location**: `Functions/eden_scraper.py`
   - **Purpose**: Searches for characters on Herald
   - **Usage**: `_connect_to_eden_herald(headless=False)`
   - **After connection**: Navigates to search page + 5s wait + data extraction
   - **Returns**: (success, message, json_path)

2. **`scrape_character_from_url(character_url, cookie_manager)`**
   - **Location**: `Functions/eden_scraper.py`
   - **Purpose**: Updates character from Herald URL
   - **Usage**: `_connect_to_eden_herald(cookie_manager=cookie_manager, headless=False)`
   - **After connection**: Navigates to search page + 5s wait + data extraction
   - **Returns**: (success, data_dict, error_message)

3. **`CharacterProfileScraper.connect(headless=False)`**
   - **Location**: `Functions/character_profile_scraper.py`
   - **Purpose**: Establishes connection for profile scraping (RvR/PvP/PvE/Wealth/Achievements stats)
   - **Usage**: Wraps `_connect_to_eden_herald()` in a class method
   - **Implementation**:
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
   - **After connection**: Navigates to specific tabs (PvP, PvE, Wealth, Achievements) + scrapes data
   - **Returns**: (success: bool, error_message: str)
   - **Used by**:
     - `scrape_rvr_captures()` - Tower/Keep/Relic captures
     - `scrape_pvp_stats()` - Solo Kills, Deathblows, Kills (with realm breakdown)
     - `scrape_pve_stats()` - Dragon Kills, Legion Kills, Epic Encounters, etc.
     - `scrape_wealth_money()` - Character money/wealth
     - `scrape_achievements()` - Achievement progress

**Pattern**: All functions delegate connection logic to `_connect_to_eden_herald()`, ensuring consistency across all scraping operations.

---

## Logging Structure

All connection steps are logged with structured information:

```python
module_logger.info("Message", extra={"action": "CONNECT"})
```

**Log Levels Used**:
- `INFO`: Successful steps (cookies valid, browser initialized, connection established)
- `ERROR`: Critical failures (no cookies, expired cookies, browser initialization failure)
- `DEBUG`: Internal details (cookie count, URL verification)

**Log File**: `Logs/eden.log`  
**Action Tag**: `CONNECT`

### Example Log Output
```
2025-11-13 10:30:01 [INFO] [CONNECT] Cookies valides - 12 cookies chargés
2025-11-13 10:30:02 [INFO] [CONNECT] Navigateur initialisé avec succès
2025-11-13 10:30:05 [INFO] [CONNECT] ✅ Connexion au Herald Eden établie avec succès
```

---

## Dependencies

### Required Modules
```python
from Functions.cookie_manager import CookieManager
```

### Required Classes
- `CookieManager`: Manages authentication cookies
- `EdenScraper`: Selenium-based scraper for Herald

### External Dependencies
- **Selenium**: WebDriver automation
- **Browser**: Chrome, Edge, or Firefox
- **Cookies**: Valid, non-expired authentication cookies

---

## Design Considerations

### Why This Function Exists
**Before refactoring**: Connection code was duplicated in `search_herald_character()` and `scrape_character_from_url()`.

**After refactoring**: Single source of truth for connection logic.

**Benefits**:
- ✅ **Maintainability**: Change connection logic in one place
- ✅ **Consistency**: All scraping operations use identical connection
- ✅ **Debugging**: Single point to investigate connection issues
- ✅ **Extensibility**: Easy to add new scraping functions

### Design Principles
1. **Single Responsibility**: Only handles connection, not scraping
2. **Error Tolerance**: Never raises exceptions, always returns tuple
3. **Resource Management**: Cleans up browser on failure
4. **Flexibility**: Accepts external cookie manager or creates one

---

## Bot Check Avoidance Strategy

### Why Visible Browser?
```python
scraper, error = _connect_to_eden_herald(headless=False)
```

**Eden Herald implements bot detection** that blocks headless browsers.

**Countermeasures**:
- ✅ Visible browser window (appears as normal user)
- ✅ Minimized automatically (doesn't interrupt user)
- ✅ Realistic timeouts (1s, 2s, 2s) simulate human behavior
- ✅ Multi-step navigation (eden-daoc.net → refresh → herald)

**Critical**: Changing `headless=True` will trigger bot check and fail authentication.

---

## Future Improvements

### Potential Enhancements
1. **Configurable Timeouts**: Move hardcoded timeouts (1s, 2s, 2s) to `config.json`
2. **Connection Retry**: Automatic retry with exponential backoff
3. **Connection Pooling**: Reuse existing connections for multiple operations
4. **Browser Selection**: Allow user to force specific browser (Chrome/Edge/Firefox)
5. **Proxy Support**: Add proxy configuration for connection

### Breaking Changes to Avoid
- ❌ Don't change return type (always tuple)
- ❌ Don't remove `headless` parameter (API compatibility)
- ❌ Don't raise exceptions (breaks error handling contract)

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| `"No cookies found"` | Cookie file doesn't exist | Generate or import cookies using Cookie Manager |
| `"Cookies have expired"` | Cookies too old | Regenerate cookies |
| `"Unable to initialize browser"` | No browser installed | Install Chrome, Edge, or Firefox |
| `"Unable to load cookies"` | Bot check detected | Verify `headless=False`, check timeouts |
| Connection timeout | Slow internet | Increase hardcoded timeouts in `load_cookies()` |

### Debug Steps
1. Check `Logs/eden.log` for detailed error messages
2. Verify cookie existence: `Configuration/cookies.json`
3. Test cookie validity in Cookie Manager UI
4. Try manual browser navigation to Herald (test authentication)
5. Check internet connection stability

---

## Testing Recommendations

### Unit Test Structure
```python
def test_connect_to_eden_herald_success():
    """Test successful connection with valid cookies"""
    scraper, error = _connect_to_eden_herald(headless=False)
    assert scraper is not None
    assert error == ""
    scraper.close()

def test_connect_to_eden_herald_no_cookies():
    """Test failure when no cookies exist"""
    # Remove cookies temporarily
    scraper, error = _connect_to_eden_herald()
    assert scraper is None
    assert "No cookies found" in error

def test_connect_to_eden_herald_expired_cookies():
    """Test failure with expired cookies"""
    # Use expired test cookies
    scraper, error = _connect_to_eden_herald()
    assert scraper is None
    assert "expired" in error.lower()
```

### Integration Test
```python
def test_full_connection_workflow():
    """End-to-end test of connection → search → close"""
    scraper, error = _connect_to_eden_herald(headless=False)
    
    if not scraper:
        pytest.skip(f"Connection failed: {error}")
    
    # Navigate to search page
    scraper.driver.get("https://eden-daoc.net/herald?n=search&s=Test")
    time.sleep(5)
    
    # Verify page loaded
    html = scraper.driver.page_source
    assert "search" in html.lower()
    
    # Clean up
    scraper.close()
```

---

## Security Considerations

### Cookie Security
- Cookies stored in plain text in `Configuration/cookies.json`
- Contains session tokens with limited validity (typically 24-48 hours)
- **Not encrypted**: Consider encryption in future versions for shared systems

### Browser Session
- Browser session remains open until `scraper.close()` is called
- **Resource leak risk**: Always close scraper in `finally` block:
  ```python
  scraper = None
  try:
      scraper, error = _connect_to_eden_herald()
      # ... operations ...
  finally:
      if scraper:
          scraper.close()
  ```

### Bot Detection
- Eden Herald monitors for automated access patterns
- **Mitigation**: Realistic timeouts, visible browser, human-like navigation
- **Risk**: Excessive requests may trigger temporary IP ban

---

## Performance Metrics

### Typical Performance
- **Connection Time**: 6-8 seconds (including all timeouts)
- **Browser Memory**: ~150-300 MB (Chrome)
- **CPU Usage**: Low (idle between operations)

### Optimization Opportunities
- ⚡ **Connection reuse**: Keep scraper alive for multiple operations
- ⚡ **Parallel scraping**: Use multiple scrapers with rate limiting
- ⚡ **Timeout tuning**: Reduce timeouts for fast connections (future config option)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-13 | Initial refactoring - Extracted from search_herald_character() |

---

## Related Documentation

- **Character Search**: [CHARACTER_SEARCH_SCRAPER_EN.md](CHARACTER_SEARCH_SCRAPER_EN.md) - `search_herald_character()` function
- **Character Update**: [CHARACTER_PROFILE_SCRAPER_EN.md](CHARACTER_PROFILE_SCRAPER_EN.md) - `scrape_character_from_url()` function
- **Stats & Wealth**: [CHARACTER_STATS_SCRAPER_EN.md](CHARACTER_STATS_SCRAPER_EN.md) - `CharacterProfileScraper` class and `WealthManager` module

---

## Contact & Support

For issues related to `_connect_to_eden_herald()`:
1. Check logs: `Logs/eden.log`
2. Review cookie status in Cookie Manager UI
3. Verify browser installation (Chrome/Edge/Firefox)
4. Test manual Herald access in browser

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-13  
**Author**: Automated Documentation  
**Status**: ✅ Production Ready
