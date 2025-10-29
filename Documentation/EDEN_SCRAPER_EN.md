# Eden Scraper - Documentation

## Overview

The Eden Scraper module extracts data from the Eden-DAOC Herald. It uses Selenium to manage authenticated sessions and BeautifulSoup to parse HTML.

## File

- **Functions/eden_scraper.py**: `EdenScraper` class for scraping

## Features

### 1. Individual Character Scraping
Extracts all data from a character's Herald page:
- Base statistics
- Equipment
- Realm Ranks and Abilities
- Structured data tables

### 2. Character Search
Performs Herald searches:
- By player name
- By guild
- Filtering by realm (Albion, Midgard, Hibernia)

### 3. Session Management
- Uses CookieManager cookies
- Maintains active Selenium session
- Automatic closing via context manager

## Usage

### Scrape a Character

```python
from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper

# Initialize cookie manager
cookie_manager = CookieManager()

# Use context manager for scraper
with EdenScraper(cookie_manager) as scraper:
    data = scraper.scrape_character("Ewolinette")
    
    if data:
        print(f"Character: {data['character_name']}")
        print(f"Data tables: {len(data['tables'])}")
```

### Search Characters

```python
from Functions.eden_scraper import EdenScraper

with EdenScraper(cookie_manager) as scraper:
    results = scraper.scrape_search_results("Ewoli", realm="hib")
    
    for char in results:
        print(f"- {char['name']}: {char['url']}")
```

### Utility Functions

```python
from Functions.eden_scraper import scrape_character_by_name, search_characters

# Quickly scrape a character
data = scrape_character_by_name("Ewolinette", cookie_manager)

# Search
characters = search_characters("Ewoli", realm="hib", cookie_manager=cookie_manager)
```

## EdenScraper Class API

### Constructor
```python
scraper = EdenScraper(cookie_manager)
```
- **cookie_manager**: CookieManager instance for authentication

### Main Methods

#### initialize_driver(headless=True)
Initializes Selenium Chrome driver.
- **headless**: If True, launches in headless mode
- **Returns**: bool - True if successful

#### load_cookies()
Loads authentication cookies into driver.
- **Returns**: bool - True if cookies were loaded

#### scrape_character(character_name)
Scrapes character data.
- **character_name**: Character name
- **Returns**: dict - Character data or None

Returned data structure:
```python
{
    'character_name': 'Ewolinette',
    'scraped_at': '2025-10-29T18:30:00',
    'title': 'Eden Herald - Ewolinette',
    'h1': ['Level 1 title'],
    'h2': ['Level 2 title'],
    'h3': ['Level 3 title'],
    'tables': [
        [
            ['Header1', 'Header2'],
            ['Data1', 'Data2']
        ]
    ]
}
```

#### scrape_search_results(search_query, realm=None)
Searches characters on Herald.
- **search_query**: Search term
- **realm**: Optional - 'alb', 'mid' or 'hib'
- **Returns**: list - List of found characters

Result structure:
```python
[
    {
        'name': 'Ewolinette',
        'url': 'https://eden-daoc.net/herald?n=player&k=Ewolinette',
        'raw_data': ['Ewolinette', 'Mentalist', 'Lurikeen', ...]
    }
]
```

#### close()
Cleanly closes Selenium driver.

### Context Manager
The scraper supports context manager for automatic resource management:

```python
with EdenScraper(cookie_manager) as scraper:
    # Driver is automatically closed on exit
    data = scraper.scrape_character("Test")
```

## Data Extraction

### _extract_character_data(soup)
Private method that extracts structured data from BeautifulSoup:
- Page title
- All H1, H2, H3 headings
- All HTML tables converted to lists

### _extract_search_results(soup)
Private method that extracts character list from search results.

## Error Handling

### Driver Not Initialized
- Automatic initialization attempt on first scrape
- Error log if initialization fails

### Invalid Cookies
```python
if not scraper.load_cookies():
    logging.error("Unable to load cookies")
    return None
```

### Scraping Error
- Exception caught and logged
- Returns None instead of crashing

## Dependencies

- **selenium**: Browser automation
- **webdriver-manager**: ChromeDriver management
- **beautifulsoup4**: HTML parsing
- **lxml**: Fast HTML parser (optional but recommended)

## Performance

### Headless Mode
Headless mode (no interface) is enabled by default to:
- Reduce resource consumption
- Speed up scraping
- Allow background execution

### Delays
A 2-second delay is applied after each page load to:
- Allow JavaScript to execute
- Avoid overloading Eden server
- Ensure complete content loading

## Security and Best Practices

### Server Respect
- Delays between requests
- No abusive parallel requests
- Clean session closing

### Cookie Management
- Always uses CookieManager
- Never stores cookies hardcoded
- Checks validity before each session

### Logs
All events are logged:
```python
logging.info("Scraping character: Ewolinette")
logging.error("Scraping error: [details]")
```

## Limitations

- **JavaScript**: Some dynamic elements may not be captured
- **HTML Structure**: Scraper depends on current Herald structure
- **Rate Limiting**: No client-side limitation implemented
- **Caching**: No result caching (to implement in Phase 2)

## Future Enhancements

### Phase 2 - Full Integration
- Automatic character import into application
- Bidirectional data synchronization
- Scraped data caching
- Change detection (equipment, stats)
- Integrated search interface

### Optimizations
- Driver pool for parallel scraping
- Smart caching
- HTML change detection (alerts if structure changes)
- More precise stat extraction (advanced parsing)

## Advanced Usage Examples

### Scrape All Guild Members

```python
with EdenScraper(cookie_manager) as scraper:
    # Search guild
    members = scraper.scrape_search_results("GuildName", realm="hib")
    
    # Scrape each member
    all_data = []
    for member in members:
        char_name = member['name'].split()[0]
        data = scraper.scrape_character(char_name)
        if data:
            all_data.append(data)
    
    print(f"{len(all_data)} characters scraped")
```

### Export to JSON

```python
import json

data = scrape_character_by_name("Ewolinette", cookie_manager)
if data:
    with open('character_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```
