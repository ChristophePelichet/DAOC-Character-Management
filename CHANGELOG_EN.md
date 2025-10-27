# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.102] - 2025-10-27

### Changed
- **Server Column**: Restored server column (Eden/Blackthorn)
- **Server Configuration**: Default server set to "Eden"
- **Character Sheet**: Added dropdown to select server
- **Visibility**: Server column hidden by default (can be shown via View > Columns)
- **Column Reorganization**: New order: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server
- **Columns Menu**: Fixed column list in menu (added server, removed season)
- **Simplified Renaming**: Removed "Rename" button from character sheet
- **Simplified Messages**: Removed "This will update the JSON file" message and success popup

### Added
- **Multi-server Support**: Ability to manage characters on Eden and Blackthorn
- **Server Editing**: Modify server from character sheet
- **Quick Rename**: Press Enter in the "Name" field to rename character directly

### Improved
- **User Interface**: Cleaner interface in character sheet
- **Ergonomics**: Faster renaming with Enter key
- **User Experience**: Smoother renaming process without unnecessary popups

### Fixed
- **RealmTitleDelegate**: Fixed critical error when drawing colored titles

## [0.101] - 2025-10-27

### Changed
- **User Interface**: Replaced toolbar with traditional Windows menu bar
- **File Menu**: Added menu with "New Character" and "Settings"
- **View Menu**: Added menu with "Columns"
- **Help Menu**: Added menu with "About"
- **About Dialog**: Enhanced with complete information (name, version, creator)
- **Translations**: Added menu translations in all 3 languages (FR/EN/DE)
- **Documentation**: Updated all documentation to reflect the new interface
- **Creator**: Updated creator name to "Ewoline"
- **Character Sheet**: Added ability to edit realm, level (1-50), season, page (1-5) and guild name
- **Realm Change**: Automatic file relocation to correct directory when changing realm
- **Dynamic Colors**: Automatic color updates according to new realm
- **Renaming**: Ability to rename character from context menu (right-click) or character sheet
- **File Management**: Automatic JSON file renaming when character is renamed
- **Server Column Removal**: Permanent deletion of server column and all related functionality
- **Interface Simplification**: Server automatically set to "Eden" without user selection
- **Column Reorganization**: Reindexed all columns after server column removal
- **Save**: Added "Save" button in character sheet to save modifications
- **Configuration**: Apply default column values even without existing configuration

### Removed
- **Toolbar**: Removed toolbar with icons
- **Obsolete Code**: Cleaned up code related to unused toolbar icons

### Technical
- Optimized icon loading (keeping only realm icons)
- Simplified action system
- Improved retranslation handling during language changes

## [0.1] - 2025-10-XX

### Added
- **Complete Character Management**: Create, modify, delete, duplicate
- **Realm Ranks System**: Display ranks and titles with web scraping
- **Multilingual Interface**: Full support for Français, English, Deutsch
- **Column Configuration**: Customizable visible columns
- **Debug Mode**: Integrated console with log management
- **Bulk Actions**: Multiple selection and batch deletion
- **Realm Organization**: Albion, Hibernia, Midgard with icons
- **Multi-Server Management**: Support for different DAOC servers
- **Season System**: Organization by seasons (S1, S2, S3, etc.)
- **Themes**: Light/dark theme support
- **Persistence**: Automatic configuration saving

### Main Features
- **PySide6 Interface**: Modern and responsive graphical interface
- **Data Manager**: Complete game data management system
- **Web Scraping**: Automatic Realm Ranks data extraction from official website
- **Advanced Configuration**: Complete customization of paths and parameters
- **Complete Documentation**: Detailed guides in French and English

---

## Types of Changes

- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

## Version Links

- [0.101] - Current version with Windows menu interface
- [0.1] - Initial version with toolbar

## Other Languages

- 🇫🇷 [Français](CHANGELOG_FR.md)
- 🇬🇧 [English](CHANGELOG_EN.md) (this file)
- 🇩🇪 [Deutsch](CHANGELOG_DE.md)