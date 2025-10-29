# CHANGELOG

> 📁 **This file has been moved**: Previously at root, now in `Documentation/` (v0.104)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Migration check on path change**: Enhanced security
  - Automatic detection if the new Characters folder requires migration
  - Trilingual warning popup (FR/EN/DE) if old structure is detected
  - Message indicating to restart the application to perform migration
  - Test script: `Scripts/test_migration_path_change.py`
  - New translation keys: `migration_path_change_title` and `migration_path_change_message`

## [0.104] - 2025-10-29

### Added
- **Migration confirmation popup**: Trilingual display (FR/EN/DE) before any migration
  - Detailed explanation of structure modification
  - Visual comparison: Old structure → New structure
  - Information about automatic backup with path location
  - "OK" button: Launches ZIP backup then migration
  - "Cancel" button: Closes application without changes
  - Custom cancellation message if user cancels
- **Automatic ZIP backup before migration**: Optimized data protection
  - Creates compressed ZIP archive of `Characters` folder
  - Timestamped name: `Characters_backup_YYYYMMDD_HHMMSS.zip`
  - Organized location: `Backup/Characters/`
  - ZIP_DEFLATED compression saves 70-90% disk space
  - Success verification before launching migration
  - Confirmation message with backup location
- **New folder structure**: Migration to hierarchical organization by season
  - Old structure: `Characters/Realm/Character.json`
  - New structure: `Characters/Season/Realm/Character.json`
  - Prepares for future seasons
  - Automatic migration at startup (with confirmation)
  - Marker file `.migration_done` to avoid multiple migrations
- **Help Menu > Migrate folder structure**: Manual migration option
  - Allows manual re-run of migration if needed
  - Asks for confirmation before proceeding
  - Automatically creates ZIP backup
  - Displays detailed migration report (number of characters, distribution by season)
  - Automatically refreshes character list after migration
- **migration_manager.py module**: Complete migration manager
  - `get_backup_path()`: Generates backup path in `Backup/Characters/`
  - `backup_characters()`: Creates compressed ZIP archive
  - `check_migration_needed()`: Detects if migration is needed
  - `migrate_character_structure()`: Performs migration with detailed report
  - `is_migration_done()`: Checks if migration was already completed
  - `run_migration_with_backup()`: Orchestrates backup then migration
  - `run_migration_if_needed()`: Runs automatic migration at startup
  - Complete error handling with detailed logs
  - Preserves file metadata (dates, attributes)
  - Automatic cleanup of empty old folders
- **Class and Race Columns**: New columns in main view
  - "Class" column displayed by default
  - "Race" column hidden by default
  - Checkboxes in View > Columns menu to enable/disable columns
  - Full multilingual support (FR/EN/DE)
  - Data automatically extracted from character JSON files
- **Test scripts**: Tools to test migration
  - `Scripts/simulate_old_structure.py`: Creates old structure for testing
  - `Scripts/test_backup_structure.py`: Verifies ZIP backup creation
- **Documentation reorganization**: Improved file structure
  - CHANGELOGs moved to `Documentation/`
  - New main `CHANGELOG.md` at root redirecting to language versions
  - Language READMEs (EN/DE) moved to `Documentation/`
  - Main README.md at root with links to language versions
  - Better organization of documentation files
  - All internal links updated

### Changed
- **All character management functions**: Adapted to new Season/Realm structure
  - `save_character()`: Saves to `Season/Realm/`
  - `get_all_characters()`: Walks through Season/Realm structure with `os.walk()`
  - `rename_character()`: Searches and renames in new structure
  - `delete_character()`: Deletes in new structure
  - `move_character_to_realm()`: Moves between realms within same season
  - Default value "S1" for characters without specified season
- **Automatic migration**: Now requires user confirmation
  - No longer launches automatically without asking
  - Displays confirmation popup at startup
  - Closes application if user cancels
- **Function `run_automatic_migration()` in main.py**: Complete refactoring
  - Displays confirmation popup with QMessageBox
  - Uses try/finally to guarantee progress popup closure
  - Calls `progress.deleteLater()` to clean up Qt memory
  - Handles cancellation cases with trilingual message
- **Backup system**: Migration from folder copy to ZIP archive
  - Old method: `shutil.copytree()` created heavy copy
  - New method: `zipfile.ZipFile()` with ZIP_DEFLATED compression
  - Saves 70-90% disk space for JSON files
  - Organization in dedicated `Backup/` folder
- **Realm Rank Interface**: Replaced sliders with dropdown menus
  - Dropdown menu for rank (1-14)
  - Dropdown menu for level (L0-L10 for rank 1, L0-L9 for others)
  - Rank title now displays at the top of the section in realm color
- **Auto-save for ranks**: Removed "Apply this rank" button
  - Rank/level changes are now applied automatically
  - No need to confirm changes
- **.gitignore**: Added `Backup/` folder to Git exclusions

### Fixed
- **"Migration in progress" popup staying open**: Critical fix
  - Added `try/finally` to guarantee popup closure
  - Explicit call to `progress.close()` and `progress.deleteLater()`
  - Popup now closes correctly after migration
- **LanguageManager Error**: Fixed `lang.get()` calls with incorrect default values
- **AttributeError**: Fixed method names for rank/level callbacks

### Technical
- **Improved architecture**: Season separation at file system level
- **Backward compatibility**: Automatic migration preserves all existing characters
- **Detailed logging**: All migration operations are recorded in logs
- **Robust error handling**: Migration handles error cases without data loss
- **Optimized performance**: Uses `zipfile` with compression for backups
- **Qt memory cleanup**: Correct use of `deleteLater()` for temporary widgets
- Added 9 new translation keys in FR/EN/DE for migration system
- Complete documentation created: `BACKUP_ZIP_UPDATE.md`

## [0.103] - 2025-10-28

### Added
- **Race Selection**: Added race field in character creation
- **Class Selection**: Added class field in character creation
- **Dynamic Filtering**: Available classes are filtered based on selected race
- **Race/Class Validation**: Automatic verification of race/class compatibility
- **Specialization Translations**: All specializations now translated in FR/EN/DE
- **Complete Data System**: Added `Data/classes_races.json` with 44 classes, 18 races and 188 specializations
- **Complete Documentation**: Added usage guides and technical documentation
- **Column Width Management**: Option to switch between automatic and manual resize modes
  - Automatic mode: Content-based resizing with expandable Name column
  - Manual mode: Free resizing of all columns by user

### Changed
- **Mauler Removal**: Mauler class removed (not implemented on Eden server)
- **Eden Support**: Data adjusted to match available classes on Eden
- **Specialization Structure**: Multilingual format `{"name": "EN", "name_fr": "FR", "name_de": "DE"}`
- **Enhanced DataManager**: Added 11 new functions to manage races/classes/specializations

### Added Files
- `Data/classes_races.json`: Complete race, class and specialization data
- `Data/classes_races_stats.json`: Detailed statistics
- `Documentation/CLASSES_RACES_USAGE.md`: Complete usage guide
- `Documentation/CLASSES_RACES_IMPLEMENTATION.md`: Technical documentation
- `validate_classes_races.py`: Data validation script
- `example_classes_usage.py`: Practical usage examples

### Statistics
- **44 classes** across 3 realms (Albion: 15, Midgard: 14, Hibernia: 15)
- **18 races** total (6 per realm)
- **188 specializations** translated in 3 languages

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