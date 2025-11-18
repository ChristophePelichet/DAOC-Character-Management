# 📚 Documentation - DAOC Character Management

Complete index of technical and user documentation for the character manager.

---

## 📁 Documentation Structure

### 💾 [Backups/](Backups/) - Backup System
- **README.md** - Backup system overview
- **BACKUP_ARCHITECTURE.md** - Technical architecture of backup system
- **BACKUP_RETENTION_POLICY.md** - Backup retention policy
- **BACKUP_SETTINGS.md** - Backup settings configuration
- **BACKUP_USER_GUIDE.md** - User guide for backups
- **TEST_BACKUP_README.md** - Backup testing documentation

### 👤 [Char/](Char/) - Character Management
- **CHARACTER_MIGRATION_TECHNICAL_DOC.md** - Complete technical documentation of automatic character migration system (870 lines)
  - Migration system architecture
  - Data validation schema
  - Backup and rollback process
  - Tracking in config.json

### ⚙️ [Config/](Config/) - Configuration
- **CONFIG_V2_TECHNICAL_DOC.md** - Configuration v2 technical documentation
  - Hierarchical structure (5 sections)
  - Automatic v1→v2 migration
  - Backward compatibility (39 legacy keys)
  - Backup and validation system

### 💬 [Dialog/](Dialog/) - Dialogs and Interface
- **PROGRESS_DIALOG_SYSTEM_EN.md** - Progress window system (1900+ lines)
  - Progress dialog architecture
  - Complete multilingual integration
  - Real-time update patterns
- **THREAD_SAFETY_PATTERNS.md** - Thread safety patterns for dialogs
  - External resource management in threads
  - Cleanup before terminate()
  - Qt thread safety best practices

### 🛡️ [Armory/](Armory/) - Armory System
- **ARMORY_IMPORT_SYSTEM_EN.md** - Complete armory import system documentation
- **ITEMS_SCRAPER_TECHNICAL_EN.md** - Items scraper technical documentation
- **DUAL_MODE_DATABASE_EN.md** ⭐ NEW - Dual-mode database system (English)
  - Mode 1: Internal read-only database (`Data/items_database.json`)
  - Mode 2: Personal user-managed database (`Armory/items_database.json`)
  - Database manager API reference
  - Configuration and UI integration
  - Auto-add scraped items feature
- **DUAL_MODE_DATABASE_FR.md** ⭐ NEW - Système de base de données double mode (Français)
  - Mode 1 : Base interne lecture seule
  - Mode 2 : Base personnelle gérée par l'utilisateur
  - Référence API du gestionnaire de base
  - Configuration et intégration UI
  - Fonctionnalité d'ajout automatique

### 🌐 [Eden/](Eden/) - Eden Herald Scraping
- **CONNECT_TO_EDEN_HERALD_EN.md** - Eden Herald connection guide
- **CHARACTER_PROFILE_SCRAPER_EN.md** - Character profile scraper
- **CHARACTER_SEARCH_SCRAPER_EN.md** - Character search scraper
- **CHARACTER_STATS_SCRAPER_EN.md** - Character statistics scraper

### ❓ [Help/](Help/) - Help System
- **WIKI_HELP_SYSTEM.md** - Integrated help system documentation
  - GitHub Wiki page navigation
  - F1 key for quick access
  - FR/EN/DE pages (FR complete)

### 🌍 [Lang/](Lang/) - Language System
- **LANGUAGE_V2_TECHNICAL_DOC.md** - Multilingual system v2 technical documentation (1793 lines)
  - Hierarchical structure (12 sections)
  - Automatic v1→v2 migration
  - 399 keys translated FR/EN/DE
  - Complete backward compatibility

### ⚙️ [Settings/](Settings/) - Settings and UI Configuration
- **README_SETTINGS.md** - Settings overview
- **SETTINGS_ARCHITECTURE_EN.md** - Settings system architecture
- **BACKUP_INTEGRATION_EN.md** - Backup integration in Settings
- **FOLDER_MOVE_SYSTEM_EN.md** - Folder move system
- **UI_COMPONENT_TEMPLATE.md** - UI component template

### 🎨 [Themes/](Themes/) - Theme System
*(Documentation coming soon)*

---

## 🔍 Documentation by Feature

### Automatic Migration
- [Char/CHARACTER_MIGRATION_TECHNICAL_DOC.md](Char/CHARACTER_MIGRATION_TECHNICAL_DOC.md) - Character migration
- [Config/CONFIG_V2_TECHNICAL_DOC.md](Config/CONFIG_V2_TECHNICAL_DOC.md) - Configuration migration
- [Lang/LANGUAGE_V2_TECHNICAL_DOC.md](Lang/LANGUAGE_V2_TECHNICAL_DOC.md) - Language migration

### Backup and Security
- [Backups/BACKUP_ARCHITECTURE.md](Backups/BACKUP_ARCHITECTURE.md) - Backup architecture
- [Backups/BACKUP_USER_GUIDE.md](Backups/BACKUP_USER_GUIDE.md) - User guide
- [Settings/BACKUP_INTEGRATION_EN.md](Settings/BACKUP_INTEGRATION_EN.md) - UI integration

### Armory Database System ⭐ NEW
- [Armory/DUAL_MODE_DATABASE_EN.md](Armory/DUAL_MODE_DATABASE_EN.md) - Technical guide (English)
- [Armory/DUAL_MODE_DATABASE_FR.md](Armory/DUAL_MODE_DATABASE_FR.md) - Guide technique (Français)
- [Armory/ARMORY_IMPORT_SYSTEM_EN.md](Armory/ARMORY_IMPORT_SYSTEM_EN.md) - Import system
- [Armory/ITEMS_SCRAPER_TECHNICAL_EN.md](Armory/ITEMS_SCRAPER_TECHNICAL_EN.md) - Scraper technical docs

### Eden Herald Scraping
- [Eden/CONNECT_TO_EDEN_HERALD_EN.md](Eden/CONNECT_TO_EDEN_HERALD_EN.md) - Connection
- [Eden/CHARACTER_SEARCH_SCRAPER_EN.md](Eden/CHARACTER_SEARCH_SCRAPER_EN.md) - Search
- [Eden/CHARACTER_PROFILE_SCRAPER_EN.md](Eden/CHARACTER_PROFILE_SCRAPER_EN.md) - Profile
- [Eden/CHARACTER_STATS_SCRAPER_EN.md](Eden/CHARACTER_STATS_SCRAPER_EN.md) - Statistics

### User Interface
- [Dialog/PROGRESS_DIALOG_SYSTEM_EN.md](Dialog/PROGRESS_DIALOG_SYSTEM_EN.md) - Progress windows
- [Dialog/THREAD_SAFETY_PATTERNS.md](Dialog/THREAD_SAFETY_PATTERNS.md) - Thread safety
- [Settings/UI_COMPONENT_TEMPLATE.md](Settings/UI_COMPONENT_TEMPLATE.md) - Component templates

### Multilingual System
- [Lang/LANGUAGE_V2_TECHNICAL_DOC.md](Lang/LANGUAGE_V2_TECHNICAL_DOC.md) - Complete documentation
- [Help/WIKI_HELP_SYSTEM.md](Help/WIKI_HELP_SYSTEM.md) - Contextual help

---

## 📊 Documentation Statistics

- **Total files**: 27+ technical documents
- **Total lines**: 14,000+ lines of documentation
- **Languages**: FR/EN (DE partial)
- **Sections**: 10 functional categories
- **Major technical documentation**:
  - DUAL_MODE_DATABASE_EN.md: 650+ lines (NEW)
  - DUAL_MODE_DATABASE_FR.md: 650+ lines (NEW)
  - LANGUAGE_V2_TECHNICAL_DOC.md: 1793 lines
  - PROGRESS_DIALOG_SYSTEM_EN.md: 1900+ lines
  - CHARACTER_MIGRATION_TECHNICAL_DOC.md: 870 lines
  - CONFIG_V2_TECHNICAL_DOC.md: Complete with examples

---

## 🆕 Recent Updates

### November 18, 2025 - v0.108
**Armory Dual-Mode Database System**
- Added complete documentation for dual-mode database architecture
- NEW: `Armory/DUAL_MODE_DATABASE_EN.md` (English)
- NEW: `Armory/DUAL_MODE_DATABASE_FR.md` (Français)
- Features: Mode switching, auto-add integration, statistics tracking
- Complete API reference for ItemsDatabaseManager

---

## 🔗 Useful Links

- **Repository**: [GitHub - DAOC-Character-Management](https://github.com/ChristophePelichet/DAOC-Character-Management)
- **GitHub Wiki**: Help pages FR-Settings.md, FR-Backup.md
- **Changelogs**: `Changelogs/` (Full and Simple versions FR/EN)

---

**Note**: This documentation is maintained up to date with each version. For obsolete or work-in-progress documentation, see the `1.ToClean/` folder.
