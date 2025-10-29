# DAOC - Character Manager

Character management application for Dark Age of Camelot (DAOC), developed in Python with PySide6.

**🌍 Available in:** [Français](README.md) | **English** | [Deutsch](README_DE.md)

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

See [Documentation/COLUMN_CONFIGURATION_EN.md](Documentation/COLUMN_CONFIGURATION_EN.md) for more details.

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

See [Documentation/DATA_MANAGER_EN.md](Documentation/DATA_MANAGER_EN.md) for more information on data management.

## 📚 Documentation

Complete documentation available in the `Documentation/` folder:

### Français 🇫🇷
- [Configuration des Colonnes](Documentation/CONFIGURATION_COLONNES_FR.md)
- [Système Realm Ranks](Documentation/REALM_RANKS_FR.md)
- [Gestionnaire de Données](Documentation/DATA_MANAGER_FR.md)
- [Dossier Data](Documentation/DATA_FOLDER_FR.md)
- [Menu Interface](Documentation/INTERFACE_MENU_FR.md)

### English 🇬🇧
- [Column Configuration](Documentation/COLUMN_CONFIGURATION_EN.md)
- [Realm Ranks System](Documentation/REALM_RANKS_EN.md)
- [Data Manager](Documentation/DATA_MANAGER_EN.md)
- [Data Folder](Documentation/DATA_FOLDER_EN.md)
- [Menu Interface](Documentation/INTERFACE_MENU_EN.md)

## 🗂️ Project Structure

```
DAOC-Character-Management/
├── main.py                      # Main application
├── requirements.txt             # Python dependencies
├── scrape_realm_ranks.py        # Rank extraction script
├── Characters/                  # Character data
│   ├── Albion/
│   ├── Hibernia/
│   └── Midgard/
├── Configuration/               # Configuration files
│   └── config.json
├── Data/                        # Game data
│   └── realm_ranks.json
├── Documentation/               # Complete documentation (FR/EN)
│   ├── INDEX.md
│   ├── CONFIGURATION_COLONNES_FR.md
│   ├── COLUMN_CONFIGURATION_EN.md
│   ├── REALM_RANKS_FR.md
│   ├── REALM_RANKS_EN.md
│   ├── DATA_MANAGER_FR.md
│   ├── DATA_MANAGER_EN.md
│   ├── DATA_FOLDER_FR.md
│   ├── DATA_FOLDER_EN.md
│   ├── INTERFACE_MENU_FR.md
│   └── INTERFACE_MENU_EN.md
├── Functions/                   # Python modules
│   ├── character_manager.py
│   ├── config_manager.py
│   ├── data_manager.py
│   ├── language_manager.py
│   ├── logging_manager.py
│   └── path_manager.py
├── Img/                         # Images and icons
├── Language/                    # Translation files
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

See the [changelog](CHANGELOG_EN.md) for complete history.  
**🌍 Available in:** [Français](CHANGELOG_FR.md) | [English](CHANGELOG_EN.md) | [Deutsch](CHANGELOG_DE.md)

### Version 0.104 (October 29, 2025)
- ✅ **Improved Realm Rank Interface**: Replaced sliders with dropdown menus
- ✅ **Auto-save**: No need to click "Apply this rank" anymore
- ✅ **Visual Organization**: Rank title displayed at top in realm color
- ✅ **Armor Section**: New section next to "General Information"
- ✅ **Resistances Button**: Preparation for resistance management feature (coming soon)

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
**Version:** 0.102  
**Last Update:** October 27, 2025
