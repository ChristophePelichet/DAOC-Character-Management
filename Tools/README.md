# Tools Directory

Utility scripts for DAOC Character Management development and maintenance.

## 📁 Directory Structure

```
Tools/
├── DataScraping/          # Scripts for web scraping DAOC official data
├── DatabaseMaintenance/   # Database repair and maintenance utilities
└── Development/           # Development and debugging tools
```

---

## 🌐 DataScraping/

Scripts for extracting game data from official DAOC website and GitHub repositories.

### scrape_all_daoc_data.py ⭐ **UNIFIED SCRAPER**
Complete unified scraper for all DAOC data sources (replaces multiple individual scripts).
- **Purpose**: One-stop solution for all data scraping needs
- **Features**:
  - **Armor Resists**: Extract resistance tables from official website
  - **Realm Ranks**: Scrape RR data for all 3 realms (Albion, Hibernia, Midgard)
  - **Item Models**: Download all item model images from GitHub (3444 files, IDs 1-5000)
- **Output**: 
  - `Data/armor_resists.json`
  - `Data/realm_ranks_*.json` (per realm)
  - `Img/Models/items/*.webp` (WebP images, 80% quality, 63% size reduction)
- **Sources**: 
  - https://www.darkageofcamelot.com/armor-resist-tables/
  - https://www.darkageofcamelot.com/realm-ranks/
  - https://github.com/Eve-of-Darkness/DolModels
- **Usage**:
  ```bash
  # Run all scrapers (default)
  python DataScraping/scrape_all_daoc_data.py --all
  
  # Run specific scrapers
  python DataScraping/scrape_all_daoc_data.py --armor-resists
  python DataScraping/scrape_all_daoc_data.py --realm-ranks
  python DataScraping/scrape_all_daoc_data.py --item-models
  
  # Combine multiple
  python DataScraping/scrape_all_daoc_data.py --armor-resists --realm-ranks
  
  # Advanced options for item models
  python DataScraping/scrape_all_daoc_data.py --item-models --max-id 10000 --workers 30
  ```
- **Features**: SSL handling for corporate proxies, parallel downloads (20 workers), progress tracking, complete statistics

### download_all_models.py
Download model images for all types (items, mobs, icons) from GitHub.
- **Purpose**: Batch download and convert model images to WebP format
- **Types**: Items (3444), Mobs (1000), Icons (370)
- **Output**: `Img/Models/{type}/*.webp`
- **Source**: https://github.com/Eve-of-Darkness/DolModels
- **Usage**: 
  ```bash
  # Download all types
  python DataScraping/download_all_models.py
  
  # Download specific types
  python DataScraping/download_all_models.py --types items mobs
  ```

### scrape_models_metadata.py
Professional scraper for model metadata from Los Ojos website.
- **Purpose**: Extract model names and categories (838 models)
- **Output**: `Data/models_metadata.json`
- **Source**: https://daoc.ndlp.info/losojos-001-site1.btempurl.com/ModelViewer/
- **Features**: Cache system, pagination support, automatic categorization
- **Usage**: 
  ```bash
  # Basic scrape
  python DataScraping/scrape_models_metadata.py
  
  # With cache (faster)
  python DataScraping/scrape_models_metadata.py --cache
  ```

**Note**: Requires internet connection. SSL verification disabled for corporate proxies.

---

## 🗄️ DatabaseMaintenance/

Utilities for database repair, migration, and consistency checks.

### fix_currency_mapping.py
Repairs currency mapping inconsistencies in the items database.
- **Purpose**: Normalize currency names (e.g., "Grimoire Pages" → "Grimoires")
- **Features**: 
  - Validates zone/currency consistency using ZONE_CURRENCY mapping
  - Creates timestamped backup before modifications
  - Detailed statistics reporting (succeeded/failed/total)
- **Output**: Updates `Data/items_database_src.json`
- **Backup**: `Data/items_database_src_backup_YYYYMMDD_HHMMSS.json`
- **Usage**: `python DatabaseMaintenance/fix_currency_mapping.py`

---

## 🛠️ Development/

Development and debugging tools for active development.

### watch_logs.py
Real-time log file monitoring for development debugging.
- **Purpose**: Live tail of application log file
- **Usage**: Run in separate terminal while testing the app
- **Target**: `Logs/debug.log`
- **Controls**: Ctrl+C to stop
- **Usage**: `python Development/watch_logs.py`

### generate_test_characters.py
Generates test character data for development.
- **Purpose**: Create sample characters for testing UI and features
- **Output**: Test character JSON files in `Characters/`
- **Usage**: `python Development/generate_test_characters.py`

### generate_test_characters_old.py
Legacy version of test character generator (deprecated).
- **Status**: Kept for reference, use `generate_test_characters.py` instead

### log_source_editor.py
Log analysis and editing tool with GUI.
- **Purpose**: Browse and edit application logs with syntax highlighting
- **Features**: Search, filtering, line numbers
- **Config**: `Development/log_editor_config.json`
- **Usage**: `python Development/log_source_editor.py`

### log_editor_config.json
Configuration file for log_source_editor.py.
- **Contains**: Color schemes, font settings, file patterns

---

## 💡 Quick Start

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

## 💡 Quick Start

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Update ALL DAOC data (armor, ranks, models) - RECOMMENDED
python Tools/DataScraping/scrape_all_daoc_data.py --all

# Update only armor resistance data
python Tools/DataScraping/scrape_all_daoc_data.py --armor-resists

# Update only realm ranks
python Tools/DataScraping/scrape_all_daoc_data.py --realm-ranks

# Download missing item models
python Tools/DataScraping/scrape_all_daoc_data.py --item-models

# Fix currency mappings in database
python Tools/DatabaseMaintenance/fix_currency_mapping.py

# Watch logs during development
python Tools/Development/watch_logs.py
```

---

**Last Updated**: December 1, 2025
