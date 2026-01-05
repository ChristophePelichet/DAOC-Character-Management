# 📚 Documentation - DAOC Character Management

Complete index of technical and user documentation for the character manager.

---

## 📁 Documentation Structure

### 🛡️ [Armory/](Armory/) - Armory System
- **ARMORY_TECHNICAL_DOCUMENTATION.md** - Complete armory system documentation (2636 lines)
  - Template management with metadata and tags
  - Mass import system with batch processing
  - Price search and Eden scraping integration
  - Multi-realm items management
  - Currency normalization system
  - Database persistence (dual-mode architecture)
### 🛡️ [Armor-Resists/](Armor-Resists/) - Armor Resistances Table
- **ARMOR_RESISTS_TECHNICAL_DOCUMENTATION.md** - Armor resistances viewer (v0.2.1)
  - Tab-based realm selection (Albion, Midgard, Hibernia)
  - Numeric percentage display (-5%, 0%, 10%)
  - Color-coded text formatting
  - Configurable display modes (compact/detailed view)
  - Settings integration with persistent configuration
  - Multi-language support (EN/FR/DE)
  - Integration into Tools menu
### � [Debug/](Debug/) - Debug Utilities
- **DEBUG_TECHNICAL_DOCUMENTATION.md** - Debug utilities documentation
  - Freeze Tracker for UI freeze investigation and performance profiling
  - Millisecond-precision timing for operation sequences
  - Visual warning system for slow operations
  - Future expansion for additional debug utilities

### �💾 [Backups/](Backups/) - Backup System
- **BACKUP_TECHNICAL_DOCUMENTATION.md** - Complete backup system documentation
  - Automatic backup system (characters, config, cookies)
  - Manual backup functionality
  - Retention policy and cleanup
  - Centralized backup path configuration
  - Database backup with ZIP compression

### 👤 [Char/](Char/) - Character Management
- **CHARACTER_SYSTEM_TECHNICAL_DOCUMENTATION.md** - Character system documentation (1000+ lines)
  - Character validator module with class/race validation
  - Multi-language support (EN/FR/DE)
  - Automatic character data population
  - Character migration system (automatic migration architecture)
  - Data validation schema
  - Backup and rollback process
  - Migration tracking in config.json

### ⚙️ [Config/](Config/) - Configuration
- **CONFIG_V2_TECHNICAL_DOC.md** - Configuration v2 documentation
  - Hierarchical structure (5 sections)
  - Automatic v1→v2 migration
  - Backward compatibility (39 legacy keys)
  - Backup and validation system

### 💬 [Dialog/](Dialog/) - Dialog System
- **DIALOG_TECHNICAL_DOCUMENTATION.md** - Progress dialog system (1002 lines)
  - ProgressStepsDialog framework
  - Thread-safe worker patterns
  - Multilingual step configuration
  - Resource cleanup patterns

### 🌐 [Eden/](Eden/) - Eden Herald Integration
- **EDEN_TECHNICAL_DOCUMENTATION.md** - Eden Herald system (1589 lines)
  - Connection management with cookie-based auth
  - Character search and update
  - Profile scraping (RvR/PvP/PvE stats)
  - Wealth management
  - Chrome profile isolation
  - UI state management

### 🔊 [Sound/](Sound/) - Sound Control System
- **SOUND_CONTROL_TECHNICAL_DOCUMENTATION.md** - Sound control feature (v1.0)
  - Message box sound suppression system
  - Configuration management (ui.enable_sounds)
  - Custom QDialog fallback for muted audio
  - Windows winsound API integration
  - Settings UI integration
  - Multi-language support (EN/FR/DE)

### ❓ [Help/](Help/) - Help System
- **HELP_TECHNICAL_DOCUMENTATION.md** - GitHub Wiki help system (398 lines)
  - Wiki-based documentation
  - F1 key integration
  - Multilingual support (FR/EN/DE)
  - Community contribution workflow

### 📦 [Items/](Items/) - Items Database
- **ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md** - Items database system (3632 lines)
  - Multi-realm item discovery
  - Automated Eden scraping
  - Dual-mode architecture (internal/personal)
  - Merchant information tracking
  - Auto-add scraped items feature
  - Database persistence and updates

### 🌍 [Lang/](Lang/) - Language System
- **LANGUAGE_TECHNICAL_DOCUMENTATION.md** - Multilingual system (431 lines)
  - Hierarchical key structure
  - Automatic v1→v2 migration
  - 399 keys translated (FR/EN/DE)
  - Backward compatibility layer

### 🖼️ [Models/](Models/) - Visual System
- **MODELS_VISUAL_SYSTEM_DOCUMENTATION.md** - Model image system (842 lines)
  - 1000+ item model images
  - WebP compression (61.8% reduction)
  - Offline-first architecture
  - PyInstaller compatibility
  - Automatic update script

### ⚙️ [Settings/](Settings/) - Settings System
- **SETTINGS_TECHNICAL_DOCUMENTATION.md** - Settings dialog system (935 lines)
  - Sidebar navigation pattern
  - 7 configuration pages
  - Backup integration
  - Folder management
  - SuperAdmin tools (development mode)
  - Translation integration

### 🎨 [Themes/](Themes/) - Theme System
- **THEME_TECHNICAL_DOCUMENTATION.md** - Theme system documentation (1600+ lines)
  - Qt Palette and stylesheet customization
  - Available themes (Light, Dark, Purple)
  - Font scaling system (75%-150%)
  - Theme creation guide
  - API reference and troubleshooting

---

## 🔍 Documentation by Feature

### System Architecture & Debugging
- [Armory/ARMORY_TECHNICAL_DOCUMENTATION.md](Armory/ARMORY_TECHNICAL_DOCUMENTATION.md) - Armory system (2636 lines)
- [Armor-Resists/ARMOR_RESISTS_TECHNICAL_DOCUMENTATION.md](Armor-Resists/ARMOR_RESISTS_TECHNICAL_DOCUMENTATION.md) - Armor resistances table (v0.2.1)
- [Dialog/DIALOG_TECHNICAL_DOCUMENTATION.md](Dialog/DIALOG_TECHNICAL_DOCUMENTATION.md) - Dialog system (1002 lines)
- [Settings/SETTINGS_TECHNICAL_DOCUMENTATION.md](Settings/SETTINGS_TECHNICAL_DOCUMENTATION.md) - Settings system (935 lines)
- [Themes/THEME_TECHNICAL_DOCUMENTATION.md](Themes/THEME_TECHNICAL_DOCUMENTATION.md) - Theme system (1600+ lines)
- [Debug/DEBUG_TECHNICAL_DOCUMENTATION.md](Debug/DEBUG_TECHNICAL_DOCUMENTATION.md) - Debug utilities (Freeze Tracker)

### Data Management
- [Items/ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md](Items/ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md) - Items database (3632 lines)
- [Char/CHARACTER_SYSTEM_TECHNICAL_DOCUMENTATION.md](Char/CHARACTER_SYSTEM_TECHNICAL_DOCUMENTATION.md) - Character system (1000+ lines)
- [Config/CONFIG_V2_TECHNICAL_DOC.md](Config/CONFIG_V2_TECHNICAL_DOC.md) - Configuration system
- [Backups/BACKUP_TECHNICAL_DOCUMENTATION.md](Backups/BACKUP_TECHNICAL_DOCUMENTATION.md) - Backup system

### Eden Integration
- [Eden/EDEN_TECHNICAL_DOCUMENTATION.md](Eden/EDEN_TECHNICAL_DOCUMENTATION.md) - Eden Herald system (1589 lines)

### User Interface
- [Lang/LANGUAGE_TECHNICAL_DOCUMENTATION.md](Lang/LANGUAGE_TECHNICAL_DOCUMENTATION.md) - Multilingual system (431 lines)
- [Help/HELP_TECHNICAL_DOCUMENTATION.md](Help/HELP_TECHNICAL_DOCUMENTATION.md) - Help system (398 lines)
- [Models/MODELS_VISUAL_SYSTEM_DOCUMENTATION.md](Models/MODELS_VISUAL_SYSTEM_DOCUMENTATION.md) - Visual system (842 lines)
- [Sound/SOUND_CONTROL_TECHNICAL_DOCUMENTATION.md](Sound/SOUND_CONTROL_TECHNICAL_DOCUMENTATION.md) - Sound control system (v1.0)

---

## 📊 Documentation Statistics

- **Total files**: 15 major technical documents
- **Total lines**: 18,000+ lines of comprehensive documentation
- **Languages**: FR/EN (DE partial)
- **Categories**: 15 functional areas
- **Documentation by size**:
  - Items Database: 3632 lines
  - Armory System: 2636 lines
  - Theme System: 1600+ lines
  - Eden Integration: 1589 lines
  - Character System: 1000+ lines (includes validator + migration)
  - Dialog System: 1002 lines
  - Settings System: 935 lines
  - Sound Control: v1.0 (message box audio suppression)
  - Armor Resistances: v0.2.1 (multi-realm feature with configurable display)
  - Visual System: 842 lines
  - Language System: 431 lines
  - Help System: 398 lines
  - Debug Utilities: Freeze Tracker utilities
  - Configuration: Complete with examples
  - Backup System: Complete with examples

---

## 🆕 Recent Updates

### January 2025 - v0.109 (Sound Control Feature)
**Message Box Audio Suppression System**
- NEW: `Sound/SOUND_CONTROL_TECHNICAL_DOCUMENTATION.md` (v1.0)
  - Complete sound control feature documentation
  - Custom QDialog fallback for muted sounds
  - Windows winsound API integration (winsound.PlaySound(None, SND_PURGE))
  - Multi-language support (EN/FR/DE)
  - Settings integration (Settings > General > Audio Settings)
  - Comprehensive error handling and fallback patterns
- IMPLEMENTATION: 181 total QMessageBox → SilentMessageBox replacements across 15+ files
- FILES CREATED:
  - `Functions/sound_manager.py` - Business logic for sound settings
  - `UI/ui_sound_manager.py` - Custom message box wrapper class
- FILES MODIFIED: 15 files with dialog updates
  - `UI/settings_dialog.py` (70 replacements)
  - `UI/dialogs.py` (65 replacements)
  - `main.py` (16 replacements)
  - `UI/database_editor_dialog.py` (44 replacements)
  - And 11 other files with targeted replacements
- CONFIGURATION: Added `ui.enable_sounds` (default: true) to config schema
- BRANCH: `feature/v0.109-sound-control` (awaiting user validation before merge)
- STATUS: ✅ Complete - All imports tested and working

### January 5, 2026 - v0.2.1 (Armor Resistances Table)
**Armor Resistances Feature & Settings Integration**
- NEW: `Armor-Resists/ARMOR_RESISTS_TECHNICAL_DOCUMENTATION.md` (v0.2.1)
  - Tab-based realm selection with numeric percentage display
  - Configurable display modes (compact/detailed view)
  - Settings integration (Settings > Armory)
  - Persistent configuration (armory.armor_resists_show_classes)
  - Multi-language support (EN/FR/DE)
  - Color-coded text formatting (Green/Orange/Red)
- FEATURE: Mauler class temporarily hidden (implementation pending)
- BRANCH: `feature/v0.109-armor-resists-table`
- COMMITS: 5+ commits documenting feature development and refinements

### December 18, 2025 - v0.109 (Phase 4 - Character Validator)
**Character System Consolidation & Phase 4 Completion**
- NEW: `Char/CHARACTER_SYSTEM_TECHNICAL_DOCUMENTATION.md` (1000+ lines)
  - Consolidated character migration + new validator module
  - Complete Phase 4 documentation (Character Validator extraction)
  - Multi-language support (EN/FR/DE) for class/race validation
  - Integration examples and error handling patterns
- REMOVED: `Char/CHARACTER_MIGRATION_TECHNICAL_DOC.md` (moved content to consolidated document)
- Updated: `Documentations/README.md` to reflect consolidation
- Phase 4 Extraction Summary:
  - Created `Functions/character_validator.py` (280 lines)
  - Extracted 5 functions from CharacterSheetWindow class
  - 80 lines removed from dialogs.py
  - Full ruff compliance (0 errors)
  - Comprehensive multi-language support

### November 30, 2025 - v0.108
**Documentation Restructuring**
- Complete reorganization: One comprehensive technical document per system
- 12 major technical documentation files covering all systems
- Consolidated structure replacing fragmented multi-file approach
- NEW: `Armory/ARMORY_TECHNICAL_DOCUMENTATION.md` (2636 lines)
- NEW: `Dialog/DIALOG_TECHNICAL_DOCUMENTATION.md` (1002 lines)
- NEW: `Eden/EDEN_TECHNICAL_DOCUMENTATION.md` (1589 lines)
- NEW: `Items/ITEMS_DATABASE_TECHNICAL_DOCUMENTATION.md` (3632 lines)
- NEW: `Lang/LANGUAGE_TECHNICAL_DOCUMENTATION.md` (431 lines)
- NEW: `Models/MODELS_VISUAL_SYSTEM_DOCUMENTATION.md` (842 lines)
- NEW: `Settings/SETTINGS_TECHNICAL_DOCUMENTATION.md` (935 lines)
- NEW: `Themes/THEME_TECHNICAL_DOCUMENTATION.md` (1600+ lines)
- Updated: All documentation follows consistent structure and TOC patterns
- Total: 15,500+ lines of consolidated technical documentation

---

**Note**: This documentation is maintained up to date with each version. For obsolete or work-in-progress documentation, see the `1.ToClean/` folder.
