# DAOC - Character Manager v0.104

> 📁 **This file has been moved**: Previously at root, now in `Documentation/` (v0.104)

Character management application for Dark Age of Camelot (DAOC), developed in Python with PySide6.

**🌍 Available in:** [Français](../README.md) | **English** | [Deutsch](README_DE.md)

## 📦 Download

**Current Version: v0.104**

[![Download Executable](https://img.shields.io/badge/Download-EXE-blue?style=for-the-badge&logo=windows)](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

➡️ [Download DAOC-Character-Manager.exe](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

*No installation required - portable Windows executable*

## 🎮 Features

### Character Management
- ✅ **Create** new characters with race and class
- ✅ **Dynamic selection** of classes based on race
- ✅ **Automatic validation** of race/class combinations
- ✅ **Edit** race and class in character sheet
- ✅ **Rename** existing characters
- ✅ **Duplicate** characters
- ✅ **Delete** characters (individually or in bulk)
- ✅ **Display** complete details of each character

### Races & Classes
- 🎭 **44 classes** available across 3 realms
- 👤 **18 playable races** (6 per realm)
- 📚 **188 specializations** translated in EN/FR/DE
- ✅ **Smart filtering**: only classes compatible with the selected race are shown
- 🌍 **Complete translations**: races, classes and specializations in 3 languages

### Organization
- 📁 Organization by **Realm** (Albion, Hibernia, Midgard)
- 🏷️ Filter by **Season** (S1, S2, S3, etc.)
- 🖥️ Multi-**Server** management (Eden, Blackthorn, etc.)
- 📊 Table with sortable columns

### Realm Ranks
- 🏆 **Display** realm rank and title
- 📈 **Dropdown adjustment** of rank (Rank 1-14, Levels 0-9/10)
- 💾 **Auto-save** rank/level changes
- 🎨 **Colored titles** by realm (red for Albion, green for Hibernia, blue for Midgard)
- 📊 **Automatic calculation** based on Realm Points

### Armor & Resistances *(Coming Soon)*
- 🛡️ **Armor Section** for equipment management
- ⚔️ **Resistances**: feature in preparation

### Advanced Configuration
- 🌍 **Multi-language**: Français, English, Deutsch
- 🔧 **Customization** of paths (characters, logs, config)
- 📋 **Configurable columns**: Show/hide desired columns
- 🐛 **Debug Mode** with integrated console

## 📋 Configurable Columns

You can customize column display via **View > Columns** menu.

Available columns:
- **Selection**: Checkbox for bulk actions
- **Realm**: Realm icon
- **Season**: Character season
- **Server**: Character server (hidden by default)
- **Name**: Character name
- **Level**: Character level
- **Rank**: Realm rank (ex: 5L7)
- **Title**: Rank title (ex: Challenger)
- **Guild**: Guild name
- **Page**: Character page (1-5)
- **Class**: Character class (displayed by default)
- **Race**: Character race (hidden by default)

See [COLUMN_CONFIGURATION_EN.md](COLUMN_CONFIGURATION_EN.md) for more details.

## 🚀 Installation

### Prerequisites
- Python 3.13 or higher (⚠️ PySide6 is not compatible with Python 3.14+)
- Windows, macOS or Linux

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Launching the Application

```bash
python main.py
```

## 📦 Dependencies

- **PySide6**: Qt6 graphical interface
- **requests**: HTTP requests for web scraping
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser
- **urllib3**: HTTP request management

## 📊 Realm Ranks Data

To update Realm Ranks data from the official DAOC website:

```bash
python scrape_realm_ranks.py
```

See [DATA_MANAGER_EN.md](DATA_MANAGER_EN.md) for more information on data management.

## 📚 Documentation

Complete documentation available in the `Documentation/` folder:

### Français 🇫🇷
- [Configuration des Colonnes](CONFIGURATION_COLONNES_FR.md)
- [Système Realm Ranks](REALM_RANKS_FR.md)
- [Gestionnaire de Données](DATA_MANAGER_FR.md)
- [Dossier Data](DATA_FOLDER_FR.md)
- [Menu Interface](INTERFACE_MENU_FR.md)

### English 🇬🇧
- [Column Configuration](COLUMN_CONFIGURATION_EN.md)
- [Realm Ranks System](REALM_RANKS_EN.md)
- [Data Manager](DATA_MANAGER_EN.md)
- [Data Folder](DATA_FOLDER_EN.md)
- [Menu Interface](INTERFACE_MENU_EN.md)

## 🗂️ Project Structure

```
DAOC---Gestion-des-personnages/
├── 📄 Root files
│   ├── main.py                          # Main application (493 lines - v0.104)
│   ├── requirements.txt                 # Python project dependencies
│   ├── CHANGELOG.md                     # Changelog
│   ├── README.md                        # Main README (French)
│   ├── .gitignore                       # Git excluded files
│   └── .gitattributes                   # Git configuration
│
├── 📁 Characters/                       # ⭐ Character data (Season/Realm structure v0.104)
│   ├── S1/                              # Season 1
│   │   ├── Albion/                      # Albion S1 characters
│   │   │   └── *.json                   # Character files
│   │   ├── Hibernia/                    # Hibernia S1 characters
│   │   └── Midgard/                     # Midgard S1 characters
│   ├── S2/                              # Season 2
│   │   ├── Albion/
│   │   ├── Hibernia/
│   │   └── Midgard/
│   ├── S3/                              # Season 3
│   │   ├── Albion/
│   │   ├── Hibernia/
│   │   └── Midgard/
│   └── .migration_done                  # Migration completed marker
│
├── 📁 Backup/                           # Automatic backups
│   └── Characters/                      # ZIP backups before migration
│       └── Characters_backup_*.zip      # Format: YYYYMMDD_HHMMSS.zip
│
├── 📁 Configuration/                    # Application settings
│   └── config.json                      # User configuration
│
├── 📁 Data/                             # Game data (reference)
│   ├── realm_ranks.json                 # Consolidated ranks (3 realms)
│   ├── realm_ranks_albion.json          # Albion specific ranks
│   ├── realm_ranks_hibernia.json        # Hibernia specific ranks
│   ├── realm_ranks_midgard.json         # Midgard specific ranks
│   ├── classes_races.json               # 44 classes, 18 races, 188 specializations
│   ├── classes_races_stats.json         # Classes/races statistics
│   ├── armor_resists.json               # Resistances by armor type
│   └── README.md                        # Data folder documentation
│
├── 📁 Documentation/                    # Complete documentation (FR/EN/DE)
│   ├── 📋 Main files
│   │   ├── INDEX.md                     # Documentation index
│   │   ├── README_EN.md                 # English README
│   │   └── README_DE.md                 # German README
│   ├── 📝 Changelogs
│   │   ├── CHANGELOG_FR.md              # French changelog
│   │   ├── CHANGELOG_EN.md              # English changelog
│   │   └── CHANGELOG_DE.md              # German changelog
│   ├── 🎮 User guides
│   │   ├── CONFIGURATION_COLONNES_FR.md # Column configuration (FR)
│   │   ├── COLUMN_CONFIGURATION_EN.md   # Column configuration (EN)
│   │   ├── REALM_RANKS_FR.md            # Realm Ranks system (FR)
│   │   ├── REALM_RANKS_EN.md            # Realm Ranks system (EN)
│   │   ├── INTERFACE_MENU_FR.md         # Interface menu (FR)
│   │   ├── INTERFACE_MENU_EN.md         # Interface menu (EN)
│   │   ├── ACTION_MENU_FR.md            # Action menu (FR)
│   │   ├── ARMOR_MANAGEMENT_FR.md       # Armor management (FR)
│   │   └── ARMOR_MANAGEMENT_USER_GUIDE_FR.md  # Armor user guide (FR)
│   ├── 🔧 Technical guides
│   │   ├── DATA_MANAGER_FR.md           # Data manager (FR)
│   │   ├── DATA_MANAGER_EN.md           # Data manager (EN)
│   │   ├── DATA_FOLDER_FR.md            # Data folder (FR)
│   │   ├── DATA_FOLDER_EN.md            # Data folder (EN)
│   │   ├── CLASSES_RACES_IMPLEMENTATION.md    # Classes/races implementation
│   │   ├── CLASSES_RACES_USAGE.md       # Classes/races usage
│   │   └── DATA_EDITOR_README.md        # Data Editor guide
│   └── 📊 v0.104 Documentation
│       ├── REFACTORING_v0.104_COMPLETE.md     # Complete refactoring guide
│       ├── REFACTORING_SUMMARY_v0.104.md      # Refactoring summary
│       ├── REFACTORING_FINAL_REPORT_v0.104.md # Final report with metrics
│       ├── REFACTORING_SUMMARY.md       # General summary
│       ├── IMPLEMENTATION_COMPLETE.md   # Complete implementation
│       ├── IMPLEMENTATION_SUMMARY_ARMOR_v0.105.md  # Armor summary v0.105
│       ├── ACTION_MENU_IMPLEMENTATION_SUMMARY.md   # Action menu summary
│       ├── BACKUP_ZIP_UPDATE.md         # ZIP backup update
│       ├── MIGRATION_CONFIRMATION_UPDATE.md    # Migration confirmation update
│       ├── MIGRATION_MULTILANG_UPDATE.md       # Multilingual migration update
│       ├── MIGRATION_SECURITY.md        # Migration security
│       ├── UPDATE_SUMMARY_29OCT2025.md  # Update summary Oct 29, 2025
│       └── VERIFICATION_RAPPORT.md      # Verification report
│
├── 📁 Functions/                        # ⭐ Python modules (Modular Architecture v0.104)
│   ├── __init__.py                      # Python package marker
│   ├── 🎨 Interface managers (v0.104)
│   │   ├── ui_manager.py                # Menus, dialogs, status bar (127 lines)
│   │   ├── tree_manager.py              # Character list, QTreeView (297 lines)
│   │   └── character_actions_manager.py # Character CRUD actions (228 lines)
│   └── 🔧 Functional managers
│       ├── character_manager.py         # Character file management
│       ├── config_manager.py            # JSON configuration management
│       ├── data_manager.py              # Game data loading
│       ├── language_manager.py          # Multilingual translations
│       ├── logging_manager.py           # Logging system
│       ├── migration_manager.py         # Season/Realm migration with backup
│       ├── path_manager.py              # Path management
│       └── armor_manager.py             # Armor management
│
├── 📁 UI/                               # User interface components
│   ├── __init__.py                      # Python package marker
│   ├── dialogs.py                       # Custom dialogs (creation, editing)
│   ├── delegates.py                     # QTreeView delegates (column rendering)
│   └── debug_window.py                  # Integrated debug console
│
├── 📁 Img/                              # Graphic resources
│   ├── albion.png                       # Albion realm icon
│   ├── hibernia.png                     # Hibernia realm icon
│   └── midgard.png                      # Midgard realm icon
│
├── 📁 Language/                         # Multilingual translations
│   ├── fr.json                          # French translations (default language)
│   ├── en.json                          # English translations
│   └── de.json                          # German translations
│
├── 📁 Logs/                             # Application logging
│   └── debug.log                        # Debug logs (created automatically)
│
├── 📁 Scripts/                          # Utility and maintenance scripts
│   ├── 🌐 Web Scraping
│   │   ├── scrape_realm_ranks.py        # Extract ranks from DAOC site
│   │   ├── scrape_armor_resists.py      # Extract armor resistances
│   │   └── add_armor_translations.py    # Add FR/DE translations
│   ├── 📊 Data management
│   │   ├── update_classes_races.py      # Update classes/races
│   │   └── validate_classes_races.py    # Validate classes/races data
│   ├── 🎨 Graphics
│   │   ├── create_icons.py              # Icon creation
│   │   ├── create_simple_icons.py       # Simplified icons
│   │   └── check_png.py                 # PNG integrity check
│   ├── 🧪 Tests
│   │   ├── test_armor_manager.py        # Armor management tests
│   │   ├── test_column_configuration.py # Column configuration tests
│   │   ├── test_dynamic_data.py         # Dynamic data tests
│   │   ├── test_realm_ranks_ui.py       # Realm ranks UI tests
│   │   └── test_run.py                  # General test suite
│   ├── 📝 Examples
│   │   ├── example_classes_usage.py     # Classes usage examples
│   │   └── example_integration.py       # Integration examples
│   └── 🔧 Utilities
│       ├── watch_logs.py                # Real-time log monitoring
│       ├── analyse_gestion_erreurs.md   # Error analysis
│       └── CORRECTIONS_ICONES.md        # Icon corrections documentation
│
└── 📁 Tools/                            # ⭐ Development tools (v0.104)
    ├── clean_project.py                 # Project cleanup + Git branch creation
    ├── generate_test_characters.py      # Generate 20 test characters (Season/Realm)
    ├── generate_test_characters_old.py  # Legacy version (Realm only)
    ├── data_editor.py                   # Visual JSON data editor
    ├── DAOC-Character-Manager.spec      # PyInstaller configuration for EXE creation
    └── requirements.txt                 # Dependencies for EXE compilation
```

**Legend:**
- ⭐ = New features or major changes v0.104
- 📁 = Folder
- 📄 = Important file
- 🎨/🔧/🌐/📊/🧪/📝 = Functional categories
│   ├── fr.json
│   ├── en.json
│   └── de.json
└── Logs/                        # Log files
```

## ⚙️ Configuration

Configuration is accessible via **File > Settings** menu.

### Available Options:
- 📁 **Directories**: Characters, Configuration, Logs
- 🌍 **Language**: Français, English, Deutsch
- 🎨 **Theme**: Light / Dark
- 🖥️ **Default Server**: Eden, Blackthorn, etc.
- 📅 **Default Season**: S1, S2, S3, etc.
- 🐛 **Debug Mode**: Enable/disable detailed logs

## 🔄 Structure Migration

**Important**: Starting from version 0.104, the folder structure has changed to better organize characters by season.

### Current structure (v0.104+)
```
Characters/
└── Season/              # S1, S2, S3, etc.
    └── Realm/           # Albion, Hibernia, Midgard
        └── Character.json
```

### Automatic migration with backup
- **Confirmation popup**: On first startup, a dialog explains the migration
  - Visual comparison: Old structure → New structure
  - Information about automatic backup
  - "OK" button: Launches backup then migration
  - "Cancel" button: Closes application without changes
- **Automatic backup**: Before any migration, a complete backup is created
  - Format: Compressed ZIP archive (`Characters_backup_YYYYMMDD_HHMMSS.zip`)
  - Location: `Backup/Characters/`
  - Protects your data in case of issues
- **Secure migration**: Your existing characters are preserved and moved to the new structure
- A `.migration_done` marker file is created to prevent multiple migrations

## 🎯 Usage

### Create a Character
1. Go to **File > New Character** menu
2. Enter name, choose realm, season and server
3. Click "OK"

### Rename a Character
1. Double-click on a character to open its sheet
2. Modify the name in the "Name" field
3. Press **Enter** to rename
4. Confirm the renaming in the dialog box

### Adjust Realm Rank
1. Double-click on a character to open its sheet
2. Use sliders to adjust rank (1-14) and level (1-9/10)
3. Click "Apply this rank" to save

### Configure Visible Columns
1. Go to **View > Columns** menu
2. Check/uncheck columns to display (including Server column)
3. Click "OK" to save

### Manage Column Width
To choose between automatic and manual mode:
1. Open configuration via **File > Settings**
2. In "General Settings", check/uncheck "Manual column resize mode"
3. Automatic mode (default): Columns automatically adjust to content
4. Manual mode: You can freely resize each column by dragging separators
5. Click "Save" and restart the application

### Bulk Actions
1. Check characters in the "Selection" column
2. Use the "Bulk Actions" dropdown menu
3. Select "Delete selection" and click "Execute"

## 🐛 Debugging

To enable debug mode:
1. Open configuration via **File > Settings**
2. Check "Enable debug mode"
3. Restart the application
4. Check logs in `Logs/debug.log`

## 📝 Release Notes

See the [changelog](../CHANGELOG.md) for complete history.  
**🌍 Available in:** [Français](CHANGELOG_FR.md) | [English](CHANGELOG_EN.md) | [Deutsch](CHANGELOG_DE.md)

### Version 0.104 (October 29, 2025) - Complete Refactoring & Migration ✨
- ⚡ **Performance**: -22% loading time, -33% refresh time
- 🏗️ **Modular architecture**: Code extracted to dedicated managers
  - `Functions/ui_manager.py`: UI elements management (menus, status bar)
  - `Functions/tree_manager.py`: Character list management
  - `Functions/character_actions_manager.py`: Character actions
- 🧹 **Code cleanup**: main.py reduced from 1277 to 493 lines (-61%)
- 📦 **Optimizations**: Icon caching, reduced redundant calls
- 🗑️ **Cleanup**: Removed obsolete test scripts
- 📚 **Documentation**: New complete refactoring guide
- ✅ **Compatibility**: All features preserved
- 🎯 **Testability**: Modular code easier to test
- 🔄 **Secure migration with automatic backup**
  - Trilingual confirmation popup (FR/EN/DE) before migration
  - Automatic ZIP backup in `Backup/Characters/`
  - Format: `Characters_backup_YYYYMMDD_HHMMSS.zip`
  - Optimal compression to save disk space
  - Complete data protection before any modification
- 📁 **New folder structure**: Organization by season
  - Old: `Characters/Realm/` → New: `Characters/Season/Realm/`
  - Automatic migration on first startup
  - Marker file `.migration_done` to prevent multiple migrations
- 📋 **Class and Race Columns**: New columns in main view
  - "Class" column displayed by default
  - "Race" column hidden by default
  - Configuration via View > Columns menu
- 🏆 **Improved Realm Rank Interface**: Replaced sliders with dropdown menus
- 💾 **Auto-save for ranks**: No need to click "Apply this rank" anymore
- 🎨 **Visual Organization**: Rank title displayed at top in realm color
- 🐛 **Fixes**: Resolved "Migration in progress" popup staying open

See [REFACTORING_v0.104_COMPLETE.md](REFACTORING_v0.104_COMPLETE.md) for all refactoring details.

### Version 0.103 (October 28, 2025)
- ✅ **Race Selection**: Added race field in character creation
- ✅ **Class Selection**: Added class field in character creation
- ✅ **Dynamic Filtering**: Available classes filtered by selected race (and vice versa)
- ✅ **Race/Class Validation**: Automatic verification of race/class compatibility
- ✅ **Specialization Translations**: All specializations translated in FR/EN/DE
- ✅ **Complete Data System**: 44 classes, 18 races and 188 specializations
- ✅ **Optimized Order**: Class selected BEFORE race for more logical workflow
- ✅ **Eden Support**: Data adjusted for Eden server (without Mauler)
- ✅ **Column Width Management**: Automatic or manual mode for column resizing

### Version 0.102 (October 27, 2025)
- ✅ **Server Column**: Restored server column (Eden/Blackthorn)
- ✅ **Server Configuration**: Default server set to "Eden"
- ✅ **Character Sheet**: Added dropdown to select server
- ✅ **Visibility**: Server column hidden by default (can be shown via View > Columns)
- ✅ **Column Reorganization**: New order: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server
- ✅ **Multi-server Support**: Ability to manage characters on Eden and Blackthorn
- ✅ **Columns Menu**: Fixed column list in menu (added server, removed season)
- ✅ **Quick Rename**: Press Enter in "Name" field to rename directly
- ✅ **Cleaner Interface**: Removed "Rename" button and unnecessary popups
- ✅ **Bug Fix**: Resolved critical error in colored titles display

### Version 0.101 (October 27, 2025)
- ✅ **Windows Interface**: Replaced toolbar with traditional menu bar
- ✅ **File Menu**: New Character, Settings
- ✅ **View Menu**: Column configuration
- ✅ **Help Menu**: About with complete information
- ✅ **Translations**: Full menu support in 3 languages
- ✅ **Documentation**: Complete update with menu interface guides
- ✅ **Creator**: Updated to "Ewoline"

### Version 0.1 (October 2025)
- ✅ Complete character management (CRUD)
- ✅ Realm Ranks system with web scraping
- ✅ Multilingual interface (FR/EN/DE)
- ✅ Configurable visible columns
- ✅ Debug mode with integrated console
- ✅ Bulk actions

## 🤝 Contribution

Contributions are welcome! Feel free to:
- Report bugs
- Propose new features
- Improve documentation
- Add translations

## 📄 License

This project is a personal DAOC character management tool.

---

**Created by:** Ewoline  
**Version:** 0.104  
**Last Update:** October 29, 2025
