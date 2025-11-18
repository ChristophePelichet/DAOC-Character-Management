# 🔍 Items Scraper - Technical Documentation

**Version**: 1.0  
**Date**: November 2025  
**Component**: `Functions/items_scraper.py`  
**Related**: `Functions/eden_scraper.py`, `UI/armory_import_dialog.py`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Browser Configuration](#browser-configuration)
4. [Core Methods](#core-methods)
5. [HTML Parsing](#html-parsing)
6. [Merchant Parsing](#merchant-parsing)
7. [Zone Overrides](#zone-overrides)
8. [Logging](#logging)
9. [Error Handling](#error-handling)

---

## Overview

`ItemsScraper` is responsible for searching and extracting item information from the Eden items database (`https://eden-daoc.net/items`).

### Key Features

- ✅ **Search by item name** across realms
- ✅ **Extract complete item details** (stats, resistances, bonuses)
- ✅ **Parse merchant information** (zone, price, currency)
- ✅ **Zone override logic** for special currencies
- ✅ **Isolated Chrome profile** for stability
- ✅ **Comprehensive logging** (ITEMDB category)
- ✅ **HTML debug files** saved to Logs/

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     ItemsScraper                         │
├──────────────────────────────────────────────────────────┤
│  __init__(eden_scraper)                                  │
│    - Initialize with EdenScraper instance                │
│                                                           │
│  navigate_to_market()                                    │
│    - Open Eden items database                            │
│    - Save debug HTML                                     │
│                                                           │
│  find_item_id(item_name, realm)                          │
│    - Search item by name                                 │
│    - Extract ID from onclick or result_row               │
│    - Returns: item_id (str) or None                      │
│                                                           │
│  get_item_details(item_id, realm, item_name)             │
│    - Click item row or navigate to ?id=xxx               │
│    - Parse HTML table (item_line_left/right)             │
│    - Extract: name, type, slot, quality, level           │
│    - Parse stats, resistances, bonuses                   │
│    - Parse merchants with zone overrides                 │
│    - Returns: dict with all item data                    │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   EdenScraper                            │
├──────────────────────────────────────────────────────────┤
│  - Chrome WebDriver management                           │
│  - Cookie handling                                       │
│  - Page navigation                                       │
│  - HTML retrieval                                        │
└──────────────────────────────────────────────────────────┘
```

---

## Browser Configuration

### Isolated Chrome Profile

**Path**: `AppData/Eden/ChromeProfile/EdenScraper`

**Purpose**: Separate profile to avoid conflicts with user's main Chrome

**Flags**:
```python
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-position=-32000,-32000")  # Minimize
```

### Headless vs Minimized

- **Headless**: `False` (Eden requires visible browser for some elements)
- **Minimized**: `True` (faster rendering, Eden compatible)

---

## Core Methods

### 1. `navigate_to_market()`

**Purpose**: Navigate to Eden items database

**URL**: `https://eden-daoc.net/items`

**Steps**:
1. Navigate to items page
2. Wait for page load (WebDriverWait)
3. Save debug HTML to `Logs/items_search_debug/market_page.html`

**Returns**: `bool` (success/failure)

```python
def navigate_to_market(self):
    try:
        logging.info("Navigation vers Eden items database", extra={"action": "ITEMDB"})
        self.driver.get("https://eden-daoc.net/items")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Save debug HTML
        self._save_debug_html("market_page.html")
        return True
    except Exception as e:
        logging.error(f"Erreur navigation market: {e}", extra={"action": "ITEMDB"})
        return False
```

---

### 2. `find_item_id(item_name, realm="All")`

**Purpose**: Search item by name and extract its ID

**Parameters**:
- `item_name` (str): Item name to search
- `realm` (str): Realm filter (Albion/Hibernia/Midgard/All)

**Returns**: `str` (item ID) or `None`

**Methods**:

#### Method 1: onclick attributes
```python
# Search for onclick="item_go(ID)"
onclick_elements = soup.find_all(attrs={"onclick": re.compile(r"item_go\((\d+)\)")})
for elem in onclick_elements:
    onclick = elem.get('onclick', '')
    match = re.search(r'item_go\((\d+)\)', onclick)
    if match:
        return match.group(1)
```

#### Method 2: result_row ID
```python
# Search for <tr id="result_row_XXX">
result_rows = soup.find_all('tr', id=re.compile(r'^result_row_\d+$'))
for row in result_rows:
    row_id = row.get('id', '')
    match = re.search(r'result_row_(\d+)', row_id)
    if match:
        return match.group(1)
```

**Example**:
```python
item_id = items_scraper.find_item_id("Rigid Razorback Jerkin", "Hibernia")
# Returns: "153970"
```

---

### 3. `get_item_details(item_id, realm="All", item_name="")`

**Purpose**: Extract complete item information

**Parameters**:
- `item_id` (str): Item ID from find_item_id()
- `realm` (str): Realm filter
- `item_name` (str): Item name (for logging)

**Returns**: `dict` with item data or `None`

**Structure**:
```python
{
    "id": "123456",
    "name": "Item Name",
    "type": "Armor",
    "slot": "Torso",
    "quality": "100%",
    "level": "51",
    "stats": {"Strength": "+16", "Constitution": "+15"},
    "resistances": {"Crush": "3%", "Thrust": "3%"},
    "bonuses": {},
    "merchants": [...]
}
```

---

## HTML Parsing

### Item Details Table

**Structure**:
```html
<table id="table_result">
  <tr class="header">
    <td class="nowrap">Item Name</td>
    <td>Quality: 100%</td>
  </tr>
  <tr>
    <td class="item_line_left">Type:</td>
    <td class="item_line_right">Armor</td>
  </tr>
  <tr>
    <td class="item_line_left">Slot:</td>
    <td class="item_line_right">Torso</td>
  </tr>
  ...
</table>
```

### Name Extraction

**Challenge**: Name is in header row without specific class

**Solution**: Find header row, then nowrap cells without width style

```python
for row in all_rows:
    if row.find('td', class_='header'):
        nowrap_cells = row.find_all('td', class_='nowrap')
        for cell in nowrap_cells:
            # Skip cells with width style
            if not cell.get('style') or 'width' not in cell.get('style', ''):
                text = cell.get_text(strip=True)
                # Skip cells with digits (utility stats)
                if text and not any(char.isdigit() for char in text):
                    item_data['name'] = text
                    break
```

### Detail Rows Parsing

**Pattern**: `item_line_left` (label) + `item_line_right` (value)

```python
left_cells = soup.find_all('td', class_='item_line_left')
right_cells = soup.find_all('td', class_='item_line_right')

for left, right in zip(left_cells, right_cells):
    label = left.get_text(strip=True).replace(':', '').lower()
    value = right.get_text(strip=True)
    
    if label == 'type':
        item_data['type'] = value
    elif label == 'slot':
        item_data['slot'] = value
    elif label == 'quality':
        item_data['quality'] = value
    elif label == 'level':
        item_data['level'] = value
```

---

## Merchant Parsing

### Merchant Table

**Structure**:
```html
<table id="table_merchants">
  <tr>
    <td><div class="item_mob">Merchant Name</div></td>
    <td>Zone Name</td>
    <td>loc=12345,67890</td>
    <td>Lvl: 50</td>
    <td>100 Dragon Scales</td>
  </tr>
</table>
```

### Parsing Logic

```python
merchant_rows = soup.select('#table_merchants tr')

for row in merchant_rows:
    cells = row.find_all('td')
    if len(cells) >= 5:
        merchant_data = {
            'name': cells[0].get_text(strip=True),
            'zone': cells[1].get_text(strip=True),
            'zone_full': cells[1].get_text(strip=True),
            'location': cells[2].get_text(strip=True),
            'level': cells[3].get_text(strip=True).replace('Lvl:', '').strip(),
            'price': cells[4].get_text(strip=True)
        }
        
        # Parse price (amount + currency)
        price_parsed = parse_merchant_price(merchant_data['price'])
        merchant_data['price_parsed'] = price_parsed
```

### Price Parsing

```python
def parse_merchant_price(price_str):
    # Example: "100 Dragon Scales" → {"amount": "100", "currency": "Dragon Scales"}
    parts = price_str.strip().split(maxsplit=1)
    
    if len(parts) == 2:
        amount, currency = parts
        return {
            "amount": amount,
            "currency": currency,
            "display": f"{amount} {currency}"
        }
    else:
        return {
            "amount": price_str,
            "currency": "Unknown",
            "display": price_str
        }
```

---

## Zone Overrides

### Problem

Some currencies require zone correction based on business rules.

### Override Rules

```python
if currency == 'Roots':
    merchant_data['zone'] = 'Epik'

elif currency == 'Dragon Scales':
    # Rename currency
    merchant_data['price_parsed']['currency'] = 'Scales'
    merchant_data['price_parsed']['display'] = f"{amount} Scales"
    merchant_data['zone'] = 'Drake'

elif currency == 'Scales':
    merchant_data['zone'] = 'Drake'

elif currency == 'Atlantean Glass':
    merchant_data['zone'] = 'ToA'

elif currency == 'Seals':
    merchant_data['zone'] = 'DF'
```

### Example

**Before Override**:
```json
{
  "price": "100 Dragon Scales",
  "zone": "Dragon Zone",
  "price_parsed": {
    "amount": "100",
    "currency": "Dragon Scales"
  }
}
```

**After Override**:
```json
{
  "price": "100 Dragon Scales",
  "zone": "Drake",
  "price_parsed": {
    "amount": "100",
    "currency": "Scales",
    "display": "100 Scales"
  }
}
```

---

## Logging

### Log Category

All logs use `extra={"action": "ITEMDB"}`

**Example**:
```python
logging.info("Navigation vers Eden items database", extra={"action": "ITEMDB"})
logging.error(f"Erreur navigation market: {e}", extra={"action": "ITEMDB"})
```

### Log Levels

- **INFO**: Navigation, successful operations
- **WARNING**: Item not found, missing data
- **ERROR**: Scraping failures, exceptions

### Debug HTML Files

**Location**: `Logs/items_search_debug/` and `Logs/items_details_debug/`

**Files**:
- `market_page.html` - Items search page
- `search_results_{item_name}.html` - Search results
- `item_{item_id}_clicked.html` - Item details page

**Usage**: Analyze HTML structure when scraping fails

---

## Error Handling

### 1. Navigation Timeout

```python
try:
    WebDriverWait(self.driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
except TimeoutException:
    logging.error("Timeout navigation market", extra={"action": "ITEMDB"})
    return False
```

### 2. Item Not Found

```python
if not item_id:
    logging.warning(f"Item ID non trouvé: {item_name}", extra={"action": "ITEMDB"})
    return None
```

### 3. Missing Table Elements

```python
table_result = soup.find('table', id='table_result')
if not table_result:
    logging.warning(f"Table result non trouvée: {item_id}", extra={"action": "ITEMDB"})
    return None
```

### 4. Malformed HTML

```python
try:
    soup = BeautifulSoup(html, 'html.parser')
except Exception as e:
    logging.error(f"Erreur parsing HTML: {e}", extra={"action": "ITEMDB"})
    return None
```

---

## Performance Optimization

### Wait Strategies

- **Explicit waits**: `WebDriverWait` for dynamic elements
- **Presence check**: `EC.presence_of_element_located()`
- **Timeout**: 15 seconds (configurable)

### HTML Parsing

- **BeautifulSoup**: Faster than XPath for complex selectors
- **CSS selectors**: `soup.select('#table_merchants tr')`
- **Compiled regex**: `re.compile(r'item_go\((\d+)\)')` for repeated searches

### Browser Reuse

- **Single browser instance**: Reused across multiple items
- **No restart**: Between items (faster)
- **Close on finish**: Only when all items processed

---

## Usage Example

```python
from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
from Functions.items_scraper import ItemsScraper

# Initialize
cookie_manager = CookieManager()
eden_scraper = EdenScraper(cookie_manager)
eden_scraper.initialize_driver(headless=False, minimize=True)
eden_scraper.load_cookies()

items_scraper = ItemsScraper(eden_scraper)

# Search item
item_id = items_scraper.find_item_id("Rigid Razorback Jerkin", "Hibernia")
# Returns: "153970"

# Get details
details = items_scraper.get_item_details(item_id, "Hibernia", "Rigid Razorback Jerkin")
# Returns: {id, name, type, slot, quality, level, stats, resistances, bonuses, merchants}

# Cleanup
eden_scraper.close()
```

---

## Future Improvements

- [ ] Cache parsed HTML to avoid re-scraping
- [ ] Parallel scraping (multiple browsers)
- [ ] Retry logic with exponential backoff
- [ ] Screenshot capture on error
- [ ] Item image download
- [ ] Alternative parsing methods (API if available)

---

**End of Document** - For more details, see:
- [ARMORY_IMPORT_SYSTEM_EN.md](ARMORY_IMPORT_SYSTEM_EN.md)
- [ITEMS_PARSER_EN.md](ITEMS_PARSER_EN.md)
- [Eden/CHROME_PROFILE_TECHNICAL_EN.md](../Eden/CHROME_PROFILE_TECHNICAL_EN.md)
