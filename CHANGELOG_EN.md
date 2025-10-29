# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.104.1] - 2025-10-29

### Added
- **Migration confirmation popup**: Dialog box displayed before any migration
  - Detailed explanation of structure modification
  - Visual comparison: Old structure → New structure
  - Information about automatic backup
  - "OK" button: Launches backup and migration
  - "Cancel" button: Closes application without changes
  - Complete translation in FR/EN/DE
- **Automatic backup before migration**: Data protection
  - Creates complete copy of `Characters` folder
  - Timestamped name: `Characters_backup_YYYYMMDD_HHMMSS`
  - Location next to `Characters` folder
  - Success verification before launching migration
  - Confirmation message with backup location
- **Test script**: `Scripts/simulate_old_structure.py`
  - Simulates old structure to test migration
  - Automatic backup of current structure
  - Creates test characters in all realms

### Changed
- **Automatic migration**: Now requires user confirmation
  - No longer launches automatically without asking
  - Displays confirmation popup at startup
  - Closes application if user cancels
- **Function `run_migration_if_needed()`**: Modified return
  - No longer automatically launches migration
  - Returns "awaiting confirmation" state
  - Lets UI handle popup display

### Technical
- New function `backup_characters()` in `migration_manager.py`
- New function `run_migration_with_backup()` in `migration_manager.py`
- Function `run_automatic_migration()` in `main.py` completely refactored
- Added 3 new translation keys in FR/EN/DE:
  - `migration_startup_title`
  - `migration_startup_message`
  - `migration_backup_info`

## [0.105] - 2024-12-XX

### Added
- **Action Menu**: New menu between "File" and "View"
  - Action "📊 Resistances": Opens armor resistance table (launches data_editor.py)
  - Full multilingual support (FR/EN/DE)
  - Error handling with user messages
  - Logging of all actions
- **Enhanced Context Menu**:
  - Added "📁 Armor Management" to right-click on character
  - Placed between "Duplicate" and "Delete"
- **Armor Management System**: Complete new feature
  - Module `Functions/armor_manager.py` with `ArmorManager` class
  - Upload armor files (all formats: PNG, JPG, PDF, TXT, etc.)
  - Automatic duplicate handling (suffixes _1, _2, etc.)
  - Organization by character ID in subfolders
  - Armor list with metadata (name, size, modification date)
  - Open files with system default application
  - File deletion with confirmation
  - `ArmorManagementDialog` with complete user interface
  - "📁 Manage armors" button in character sheet (Armor section)
  - Armor folder path configuration in Settings
  - Complete documentation: `Documentation/ARMOR_MANAGEMENT_FR.md`
  - Test script: `Scripts/test_armor_manager.py`
- **Path Manager**: New functions for path management
  - `get_armor_dir()`: Returns armor folder path
  - `ensure_armor_dir()`: Creates armor folder automatically

### Changed
- **Configuration**: Added "Armor folder" field in configuration dialog
  - New field with browse button
  - Saved in `config.json` under `armor_folder` key
  - Default value: `<app_dir>/Armures`
- **Architecture**: "Drive-in" approach with configurable paths
  - All paths stored in configuration
  - Automatic creation of necessary directories
  - No hardcoded paths

### Technical
- Support for all file formats
- Metadata preservation during copy (shutil.copy2)
- Detailed logging of all operations
- Complete error handling with user messages
- Windows compatible (tested with os.startfile)

## [0.104] - 2025-10-29

### Added
- **New folder structure**: Migration to hierarchical organization by season
  - Old structure: `Characters/Realm/Character.json`
  - New structure: `Characters/Season/Realm/Character.json`
  - Prepares for future seasons
  - Automatic migration at startup (only once)
  - Marker file `.migration_done` to avoid multiple migrations
- **Help Menu > Migrate folder structure**: Manual migration option
  - Allows manual re-run of migration if needed
  - Asks for confirmation before proceeding
  - Displays detailed migration report (number of characters, distribution by season)
  - Automatically refreshes character list after migration
- **migration_manager.py module**: Complete migration manager
  - `check_migration_needed()`: Detects if migration is needed
  - `migrate_character_structure()`: Performs migration with detailed report
  - `is_migration_done()`: Checks if migration was already completed
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

### Changed
- **All character management functions**: Adapted to new Season/Realm structure
  - `save_character()`: Saves to `Season/Realm/`
  - `get_all_characters()`: Walks through Season/Realm structure with `os.walk()`
  - `rename_character()`: Searches and renames in new structure
  - `delete_character()`: Deletes in new structure
  - `move_character_to_realm()`: Moves between realms within same season
  - Default value "S1" for characters without specified season
- **Action Menu Removed**: The "Action" menu and all its actions have been temporarily removed
  - "Resistances" action removed from menu (data_editor.py preserved)
  - Simplified interface
- **Context Menu**: Icon removed from "Armor Management"
  - Before: "📁 Armor Management"
  - Now: "Armor Management"
  - Text without icon in all 3 languages (FR/EN/DE)
- **Class Column**: Fixed text formatting
  - Text is no longer displayed in bold
  - Normal font for better visual consistency

### Technical
- **Improved architecture**: Season separation at file system level
- **Backward compatibility**: Automatic migration preserves all existing characters
- **Detailed logging**: All migration operations are recorded in logs
- **Robust error handling**: Migration handles error cases without data loss
- **Optimized performance**: Uses `shutil.copy2` to preserve metadata
- Added `font.setBold(False)` for Class column
- Updated `context_menu_armor_management` translations (removed 📁)

### Added (previous version)
- **Armor Resistance System**: Complete new feature
  - File `Data/armor_resists.json` with resistances for all classes (47 classes)
  - Full multilingual support (EN/FR/DE) for all fields
  - 9 resistance types: Thrust, Crush, Slash, Cold, Energy, Heat, Matter, Spirit, Body
  - 3 tables organized by realm (Albion: 16 classes, Hibernia: 16 classes, Midgard: 15 classes)
  - Scraping script `scrape_armor_resists.py` to extract data from darkageofcamelot.com
  - Script `add_armor_translations.py` to automatically add FR/DE translations
- **Test Generation Tool**: Script `generate_test_characters.py`
  - Generates 20 characters with random attributes
  - Realistic Realm Points distribution
  - Automatic validation of class/race combinations
  - Ideal for testing the application with varied data

### Added (continued)
- **Startup Disclaimer**: Trilingual information message (FR/EN/DE)
  - Warns that software is in Alpha version
  - Informs about local data storage
  - Option to disable message in Settings > Miscellaneous
  - Replaces old hard-coded disclaimer system

### Changed
- **Realm Rank Interface**: Replaced sliders with dropdown menus
  - Dropdown menu for rank (1-14)
  - Dropdown menu for level (L0-L10 for rank 1, L0-L9 for others)
  - Rank title now displays at the top of the section in realm color
- **Auto-save**: Removed "Apply this rank" button
  - Rank/level changes are now applied automatically
  - No need to confirm changes
- **Settings**: Added "Miscellaneous" group
  - Checkbox to disable startup disclaimer
  - Persistent save in config.json
- **Visual Organization**: Reorganized "Realm Rank" section
  - Rank title with color (red for Albion, green for Hibernia, blue for Midgard) placed at top
  - Rank/level controls below the title
- **Armor Section**: Positioned next to "General Information"
  - "Resistances" button (temporarily disabled, coming soon)
  - Preparation for resistance system integration

### Fixed
- **LanguageManager Error**: Fixed `lang.get()` calls with incorrect default values
- **AttributeError**: Fixed method names for rank/level callbacks
  - `on_rank_dropdown_changed` → `on_rank_changed`
  - `on_level_dropdown_changed` → `on_level_changed`

### Translations
- Added `armor_group_title` and `resistances_button` keys in FR/EN/DE

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