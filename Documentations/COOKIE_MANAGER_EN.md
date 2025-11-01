# Eden Cookie Manager - Documentation

## Overview

The Eden cookie manager handles authentication to access the Eden-DAOC Herald. It stores Discord OAuth authentication cookies and verifies their validity.

## Related Files

- **Functions/cookie_manager.py**: `CookieManager` class for cookie management
- **UI/dialogs.py**: `CookieManagerDialog` - Graphical management interface
- **Functions/ui_manager.py**: Eden status bar in the main interface

## Features

### 1. Cookie Generation
- Opens Chrome browser for Discord OAuth authentication
- Automatically retrieves cookies after login
- Saves to `Configuration/eden_cookies.pkl`

### 2. Cookie Validation
- Checks expiration date (364 days)
- Tests actual Herald access (`https://eden-daoc.net/herald?n=top_players&r=hib`)
- Detects invalid or expired cookies

### 3. Import/Export
- Import existing .pkl cookie files
- Automatic backup before deletion
- Format validation during import

### 4. User Interface

#### Main Status Bar
Displayed in the main window between menu and actions:
- **Status**: ✅ Herald accessible / ❌ Error message / ⏳ Checking
- **Refresh Button**: Re-tests connection
- **Manage Button**: Opens detailed manager

#### Management Window
Accessible via "⚙️ Manage" button:
- **Cookie Status**: Valid / Expired / None
- **Expiration Date**: Display with countdown
- **Connection Test**: Real-time verification (background thread)
- **Actions**:
  - 🔐 Generate Cookies: Launches OAuth process
  - 🔄 Refresh: Updates display
  - 🗑️ Delete: Removes cookies (with backup)
- **Import**: Text field + Browse button to import file

## Usage

### Generate Cookies for the First Time
1. Click "⚙️ Manage" in Eden status bar
2. Click "🔐 Generate Cookies"
3. Log in with Discord in the opening browser
4. Press Enter after login
5. Cookies are automatically saved

### Check Status
The main status bar displays Herald connection status in real-time. Test runs automatically at startup in background.

### Import Existing Cookies
1. Open manager ("⚙️ Manage")
2. Enter .pkl file path OR click "📁 Browse"
3. Press Enter or click Import
4. Status updates automatically

## Technical Architecture

### Main Classes

#### CookieManager (Functions/cookie_manager.py)
- `cookie_exists()`: Checks for cookie file presence
- `get_cookie_info()`: Returns detailed information (validity, expiration, counters)
- `generate_cookies_with_browser()`: Launches authentication process
- `save_cookies_from_driver()`: Retrieves cookies from Selenium
- `import_cookie_file()`: Imports external cookie file
- `delete_cookies()`: Deletes with automatic backup
- `test_eden_connection()`: Tests Herald access with Selenium

#### ConnectionTestThread (UI/dialogs.py)
QThread thread to run connection test in background without blocking interface.

#### EdenStatusThread (Functions/ui_manager.py)
QThread thread for main status bar, updates connection indicator.

### Cookie Format
Pickle file containing a list of dictionaries with:
```python
{
    'name': 'eden_daoc_sid',
    'value': '...',
    'domain': '.eden-daoc.net',
    'path': '/',
    'expiry': 1761753600  # Unix timestamp
}
```

### Connection Test
1. Initializes headless Chrome driver
2. Loads Eden homepage
3. Injects cookies
4. Navigates to `https://eden-daoc.net/herald?n=top_players&r=hib`
5. Analyzes content to detect:
   - Redirect to login → invalid cookies
   - Login form → not authenticated
   - Herald content present → connection OK

## Dependencies

- **selenium**: Browser automation
- **webdriver-manager**: Automatic ChromeDriver management
- **PySide6**: Graphical interface (QThread, QDialog)

## Error Handling

### Cookies Not Found
- Display: "❌ No cookies found"
- Action: Generate new cookies

### Expired Cookies
- Display: "⚠️ Expired cookies"
- Action: Regenerate cookies

### Connection Error
- Display: "❌ [Error message]"
- Possible causes:
  - No Internet connection
  - Eden server unreachable
  - ChromeDriver not installed
  - Missing module (selenium, requests)

### Import Failed
- File path validation
- Pickle format verification
- Detailed error messages with logging

## Security

- **Local Storage**: Cookies stored locally in `Configuration/`
- **Automatic Backup**: Backup before deletion
- **No Transmission**: Cookies never sent anywhere except Eden-DAOC
- **Lifetime**: 364 days, then renewal required

## Logs

All events are logged via `logging` module:
- INFO: Successful operations (generation, import, test)
- WARNING: Non-blocking issues (specific cookie not added)
- ERROR: Blocking errors (import failed, driver not initialized)
- CRITICAL: Severe errors (unhandled exception)

## Future Enhancements (Phase 2)

- Full scraper integration to import characters from Herald
- Automatic character data synchronization
- Multiple Discord account management
- Scraped data caching
- Character/guild search interface
