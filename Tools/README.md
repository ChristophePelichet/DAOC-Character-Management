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

Scripts for extracting game data from official DAOC website.

### scrape_armor_resists.py
Scrapes armor resistance tables from the official DAOC website.
- **Purpose**: Extract armor type resistance values
- **Output**: `Data/armor_resists.json`
- **Source**: https://www.darkageofcamelot.com/armor-resist-tables/
- **Usage**: `python DataScraping/scrape_armor_resists.py`

### scrape_realm_ranks.py
Scrapes realm rank data for all three realms from the official DAOC website.
- **Purpose**: Extract RR abilities and stats per realm (Albion, Hibernia, Midgard)
- **Output**: `Data/realm_ranks_*.json` (one file per realm)
- **Source**: https://www.darkageofcamelot.com/realm-ranks/
- **Usage**: `python DataScraping/scrape_realm_ranks.py`

**Note**: Requires internet connection. May need updates if website structure changes.

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

# Update armor resistance data
python Tools/DataScraping/scrape_armor_resists.py

# Fix currency mappings in database
python Tools/DatabaseMaintenance/fix_currency_mapping.py

# Watch logs during development
python Tools/Development/watch_logs.py
```

---

**Last Updated**: November 21, 2025
