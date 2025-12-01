# DAOC - Character Manager

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white) ![PySide6](https://img.shields.io/badge/PySide6-6.10.0-green?logo=qt&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Version](https://img.shields.io/badge/Version-0.108-orange) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows&logoColor=white)

Character management application for Dark Age of Camelot (DAOC), developed in Python with PySide6.

**📥 [Download version v0.108](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/tag/v0.108)**

**📋 [View Changelog](CHANGELOG.md)**

---

## 🎮 Features

### Character Management
- ✅ **Create** manually new characters with race and class
- ✅ **Import** directly from Eden Herald new characters with race and class
- ✅ **Dynamic selection** of classes according to race
- ✅ **Automatic validation** of race/class combinations
- ✅ **Rename** existing characters
- ✅ **Duplicate** characters
- ✅ **Delete** characters (individually or in bulk)
- ✅ **Display** complete details of each character
- ✅ **Backup system** with size limit selection

### Races & Classes
- 🎭 **44 classes** available across 3 realms
- 👤 **18 playable races** (6 per realm)
- 📚 **188 specializations** translated in FR/EN/DE
- ✅ **Intelligent filtering**: only classes compatible with selected race are displayed
- 🌍 **Complete translations**: races, classes and specializations in 3 languages

### Realm Ranks
- 🏆 **Display** realm rank and title
- 📈 **Adjustment via dropdowns** of rank (Rank 1-14, Levels 0-9/10)
- 💾 **Automatic saving** of rank/level changes
- 🎨 **Colored titles** by realm (red for Albion, green for Hibernia, blue for Midgard)
- 📊 **Automatic calculation** based on Realm Points

### Armor Management
- 📁 **Upload armor files** Zenkcraft format only for the moment
- 🗂️ **Automatic organization** by character ID in subfolders
- 📋 **Armor list** with metadata (name, size, modification date)
- 🔍 **Quick opening** of files with default application
- 🗑️ **File deletion** with confirmation
- 🔄 **Automatic duplicate handling** (suffixes _1, _2, etc.)
- 🖼️ **Item model visualization**: Visual preview of equipment with 3444 item images
- 💰 **Automatic merchant prices**: Missing price lookup via Eden scraping
- 🏷️ **Item categorization**: Category assignment (Quest/Event) for items without prices
- 💽 **Item database**: Embedded or personal

### Backup System
- 💾 **Characters**: Character backup (Modification, Deletion)
- 💾 **Cookies**: Cookie backup
- 📊 **Retention**: Size-based retention system
- 🔧 **Compression**: Option to compress backups

### Advanced Configuration
- 🌍 **Multi-language**: Français, English, Deutsch
- 🎨 **Configurable Themes**: 3 available themes: Light (default), Dark and Purple
- 🔧 **Path customization** (characters, logs, config, armors)
- 📋 **Configurable columns**: Hide/show desired columns

---

## 🙏 Credits and Thanks

- **[DAOC Official Website](https://www.darkageofcamelot.com/)**
- **[Eden DAOC](https://www.eden-daoc.net/)**
- **[Eve-of-Darkness/DolModels](https://github.com/Eve-of-Darkness/DolModels)**

## 🙏 Special Thanks

**Testers and friends who made this project possible**:

- Morfuin / Leifur 
- Laelly

For complete credits and licensing information, see **[CREDITS.md](CREDITS.md)**.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.