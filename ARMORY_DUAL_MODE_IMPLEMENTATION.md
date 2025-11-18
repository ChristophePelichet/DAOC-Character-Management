# 🛡️ Armory Dual Mode Database - Implementation Plan

**Feature**: Dual Mode Items Database (Internal Read-Only vs Personal User Database)  
**Branch**: `108_Imp_Armo`  
**Date**: November 18, 2025  
**Status**: 🔨 In Progress

---

## 📋 Overview

Implement a dual-mode system for items database:
- **Mode 1 (Read-Only)**: Use embedded database, scrape Eden on-demand, no persistence
- **Mode 2 (Personal DB)**: Copy embedded DB to user folder, allow imports, save scraped items

---

## 🎯 Implementation Phases

### ✅ **Phase 0: Preparation** (BEFORE IMPLEMENTATION)

- [x] Analyze requirements
- [x] Create implementation plan
- [ ] **Save this plan to tracking file** ⬅️ YOU ARE HERE
- [ ] Review with user before starting
- [ ] **NO CHANGELOG UPDATES** until user approval
- [ ] **NO GIT PUSH** until user approval

---

### **Phase 1: Configuration & Data Structure** (2-3h)

#### 1.1 Config Schema (`Functions/config_schema.py`)
- [ ] Add `armory` section to schema
- [ ] Default values:
  ```python
  "armory": {
      "use_personal_database": False,
      "personal_db_created": False,
      "personal_db_path": None,  # Auto-set to {armor_path}/items_database.json
      "auto_add_scraped_items": True,
      "last_internal_db_version": "1.0"
  }
  ```

#### 1.2 Config Migration
- [ ] Update `Configuration/config.json` with default armory section
- [ ] Ensure backward compatibility

#### 1.3 Database Structure Validation
- [ ] Verify `Data/items_database.json` exists (embedded, read-only)
- [ ] Ensure PyInstaller includes it in `--onefile` build
- [ ] Test `get_app_root() / "Data" / "items_database.json"` access

#### 1.4 Personal Database Structure
- [ ] Define schema for `{armor_path}/items_database.json`
- [ ] Add metadata:
  ```json
  {
    "version": "1.0",
    "created": "ISO datetime",
    "updated": "ISO datetime",
    "item_count": 327,
    "source": {
      "internal_copy": 250,
      "imported": 50,
      "scraped": 27
    },
    "items": {...}
  }
  ```

**Files to modify**:
- `Functions/config_schema.py`
- `Configuration/config.json`

---

### **Phase 2: Translations** (1h)

#### 2.1 French Translations (`Language/fr.json`)
- [ ] Add `armory_settings` section with keys:
  - `enable_personal_db`
  - `enable_personal_db_tooltip`
  - `create_db_title`
  - `create_db_message`
  - `create_db_success`
  - `create_db_error`
  - `db_location_label`
  - `stats_title`
  - `stats_internal`
  - `stats_personal`
  - `stats_added_by_user`
  - `actions_title`
  - `import_template_button`
  - `reset_db_button`
  - `export_json_button`
  - `clean_duplicates_button`
  - `reset_db_title`
  - `reset_db_message`
  - `add_scraped_item_title`
  - `add_scraped_item_message`
  - `add_scraped_item_always`
  - `mode_readonly_tooltip`
  - `mode_personal_tooltip`

#### 2.2 English Translations (`Language/en.json`)
- [ ] Translate all FR keys to EN

#### 2.3 German Translations (`Language/de.json`)
- [ ] Translate all FR keys to DE

**Files to modify**:
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`

---

### **Phase 3: Backend - Database Manager** (2-3h)

#### 3.1 Create `Functions/items_database_manager.py`
- [ ] Create new file
- [ ] Implement `ItemsDatabaseManager` class
- [ ] Methods to implement:
  - `__init__()` - Initialize paths
  - `_update_personal_db_path()` - Get path from config
  - `get_active_database_path()` - Return internal or personal path
  - `load_database(db_path)` - Load JSON database
  - `search_item(item_name)` - Search in active database
  - `create_personal_database()` - Copy internal → personal
  - `add_scraped_item(item_data)` - Add to personal DB with deduplication
  - `get_statistics()` - Return internal/personal/user_added counts
  - `reset_personal_database()` - Reset from internal
  - `clean_duplicates()` - Remove duplicate items (Phase 6)
  - `export_database(file_path)` - Export to JSON (Phase 6)

#### 3.2 Code Comments
- [ ] All comments in **ENGLISH**
- [ ] Add docstrings for all methods
- [ ] Include usage examples in docstrings

**Files to create**:
- `Functions/items_database_manager.py`

---

### **Phase 4: UI - Settings Armory Tab** (2-3h)

#### 4.1 Modify `UI/settings_dialog.py`
- [ ] Update `_setup_armory_page()` method
- [ ] Add components:
  - `enable_personal_db_checkbox` - QCheckBox with tooltip
  - `personal_db_group` - QGroupBox (hidden by default)
  - `db_path_label` - Show personal DB path
  - Stats labels (internal/personal/user_added)
  - Action buttons (import/reset/export/clean)

#### 4.2 Implement Signal Handlers
- [ ] `_on_personal_db_toggled(state)` - Handle checkbox toggle
- [ ] `_create_personal_database_confirmation()` - Show popup before creating
- [ ] `_update_statistics()` - Refresh stats from database manager
- [ ] `_update_db_path_label()` - Update path display
- [ ] `_reset_personal_database()` - Reset with confirmation
- [ ] `_open_armory_import()` - Open import dialog (existing)
- [ ] `_export_database()` - Export to JSON (Phase 6)
- [ ] `_clean_duplicates()` - Clean duplicates (Phase 6)

#### 4.3 UI Flow
- [ ] Checkbox unchecked by default → No options visible
- [ ] Check checkbox → Popup confirmation
- [ ] Confirm → Create personal DB → Show options
- [ ] Cancel → Uncheck checkbox
- [ ] Options visible only when personal DB enabled

#### 4.4 Code Comments
- [ ] All comments in **ENGLISH**
- [ ] Document signal connections
- [ ] Explain popup logic

**Files to modify**:
- `UI/settings_dialog.py`

---

### **Phase 5: Integration - Scraping Auto-Add** (1-2h)

#### 5.1 Modify `UI/armory_import_dialog.py`
- [ ] Update `_on_item_found(item_data)` method
- [ ] Add logic after table population:
  - Check if personal DB enabled
  - If `auto_add_scraped_items` = true → Add directly
  - If false → Show popup "Add to your database?"

#### 5.2 Implement Methods
- [ ] `_add_to_personal_db(item_data)` - Add item using database manager
- [ ] `_ask_add_to_personal_db(item_data)` - Show confirmation popup
- [ ] Handle "Always add automatically" checkbox in popup
- [ ] Update config if user checks "Always add"

#### 5.3 Code Comments
- [ ] All comments in **ENGLISH**
- [ ] Explain auto-add logic
- [ ] Document popup flow

**Files to modify**:
- `UI/armory_import_dialog.py`

---

### **Phase 6: Advanced Features** (Optional, 2h)

#### 6.1 Export JSON
- [ ] Implement `_export_database()` in settings dialog
- [ ] Use QFileDialog to select export path
- [ ] Copy personal DB to selected location

#### 6.2 Clean Duplicates
- [ ] Implement `clean_duplicates()` in database manager
- [ ] Find items with same name (case-insensitive)
- [ ] Keep most recent, remove others
- [ ] Return count of removed items

#### 6.3 Merge New Internal DB (Future)
- [ ] Detect version change in internal DB
- [ ] Popup: "New internal DB available, merge?"
- [ ] Merge logic: Add new items, keep user-added

**Files to modify**:
- `Functions/items_database_manager.py`
- `UI/settings_dialog.py`

---

### **Phase 7: Portability & Build** (1-2h)

#### 7.1 PyInstaller Configuration
- [ ] Verify `DAOC-Character-Manager.spec` includes:
  ```python
  datas=[
      ('Data/items_database.json', 'Data'),
      ('Data/*.json', 'Data'),
      ('Language/*.json', 'Language'),
      # ... existing
  ]
  ```
- [ ] Ensure `onefile=True` is set

#### 7.2 Path Manager Validation
- [ ] Verify `Functions/path_manager.py` `get_app_root()` works:
  - In dev mode (script)
  - In compiled .exe (sys._MEIPASS)

#### 7.3 Build & Test
- [ ] Build .exe: `pyinstaller DAOC-Character-Manager.spec`
- [ ] Test in .exe:
  - Internal DB accessible
  - Personal DB creation works
  - No runtime errors

**Files to verify**:
- `DAOC-Character-Manager.spec`
- `Functions/path_manager.py`

---

### **Phase 8: Testing & Validation** (1-2h)

#### 8.1 Manual Tests - Mode 1 (Read-Only)
- [ ] Checkbox unchecked by default
- [ ] No options visible
- [ ] Tooltip shows "Read-only mode"
- [ ] Search item in internal DB → Found
- [ ] Search unknown item → Scrape Eden → No save
- [ ] No personal DB file created

#### 8.2 Manual Tests - Mode 2 (Personal DB)
- [ ] Check checkbox → Popup confirmation shows
- [ ] Popup shows correct path and size
- [ ] Click "Create" → Personal DB created
- [ ] Personal DB file exists in armor path
- [ ] Options group becomes visible
- [ ] Stats show correct counts (internal/personal/user_added)
- [ ] Import template → Items added to personal DB
- [ ] Scrape unknown item:
  - If auto_add = true → Added directly
  - If auto_add = false → Popup "Add to database?"
- [ ] Check "Always add" → Config updated
- [ ] Reset DB → Confirmation popup → DB recreated from internal
- [ ] Stats update after operations

#### 8.3 Tests - Portability
- [ ] Build .exe successfully
- [ ] Launch .exe → No crash
- [ ] Internal DB accessible from .exe
- [ ] Personal DB creation works in .exe
- [ ] All features work in compiled version

#### 8.4 Tests - Translations
- [ ] Switch to French → All labels in FR
- [ ] Switch to English → All labels in EN
- [ ] Switch to German → All labels in DE
- [ ] Popups use translated text

**Testing Checklist**:
- [ ] All Mode 1 tests pass
- [ ] All Mode 2 tests pass
- [ ] All portability tests pass
- [ ] All translation tests pass

---

### **Phase 9: Documentation** (2-3h)

#### 9.1 Create Technical Documentation (English)

**New Files to Create**:
- [ ] `Documentations/Armory/DUAL_MODE_DATABASE_EN.md`
  - Architecture overview
  - Mode 1 vs Mode 2 comparison
  - Configuration schema
  - Database structures
  - Flow diagrams

- [ ] `Documentations/Armory/DATABASE_MANAGER_TECHNICAL_EN.md`
  - ItemsDatabaseManager class documentation
  - Method reference
  - Usage examples
  - Error handling

#### 9.2 Update Existing Documentation

**Files to Update**:
- [ ] `Documentations/Armory/ARMORY_IMPORT_SYSTEM_EN.md`
  - Add section on dual-mode integration
  - Update workflow diagrams
  - Add auto-add to personal DB flow

- [ ] `Documentations/Settings/SETTINGS_ARCHITECTURE_EN.md`
  - Add Armory tab detailed structure
  - Document checkbox + options group
  - Add screenshots/mockups

- [ ] `Documentations/README.md`
  - Update Armory section
  - Add links to new documentation

#### 9.3 User Guide (French)

**Optional**:
- [ ] `Documentations/Armory/ARMORY_USER_GUIDE_FR.md`
  - Update with dual-mode explanation
  - Add step-by-step guide for Mode 2 activation
  - Explain auto-add vs manual add

**Documentation Checklist**:
- [ ] All new technical docs created (EN)
- [ ] All existing docs updated
- [ ] User guide updated (FR)
- [ ] README.md index updated

---

## 📂 Files Summary

### **Files to Create** (3 total)
1. `Functions/items_database_manager.py` - New database manager class
2. `Documentations/Armory/DUAL_MODE_DATABASE_EN.md` - Technical doc
3. `Documentations/Armory/DATABASE_MANAGER_TECHNICAL_EN.md` - API doc

### **Files to Modify** (10+ total)
1. `Functions/config_schema.py` - Add armory section
2. `Configuration/config.json` - Default armory config
3. `Language/fr.json` - FR translations (~20 keys)
4. `Language/en.json` - EN translations (~20 keys)
5. `Language/de.json` - DE translations (~20 keys)
6. `UI/settings_dialog.py` - Armory page UI
7. `UI/armory_import_dialog.py` - Auto-add integration
8. `Documentations/Armory/ARMORY_IMPORT_SYSTEM_EN.md` - Update
9. `Documentations/Settings/SETTINGS_ARCHITECTURE_EN.md` - Update
10. `Documentations/README.md` - Update index

### **Files to Verify** (2 total)
1. `DAOC-Character-Manager.spec` - PyInstaller config
2. `Functions/path_manager.py` - Path resolution

---

## 🎯 Completion Checklist

### **Sprint 1: Backend** (2-3h)
- [ ] Phase 1 completed (Config & Data Structure)
- [ ] Phase 3 completed (Database Manager)
- [ ] CLI tests pass

### **Sprint 2: Translations** (1h)
- [ ] Phase 2 completed (FR/EN/DE)
- [ ] All keys added and translated

### **Sprint 3: UI** (2-3h)
- [ ] Phase 4 completed (Settings Armory Tab)
- [ ] All signals connected
- [ ] UI flow tested manually

### **Sprint 4: Integration** (1-2h)
- [ ] Phase 5 completed (Scraping Auto-Add)
- [ ] Auto-add logic works
- [ ] Popups display correctly

### **Sprint 5: Build & Test** (1-2h)
- [ ] Phase 7 completed (Portability)
- [ ] Phase 8 completed (Testing)
- [ ] .exe build successful
- [ ] All tests pass

### **Sprint 6: Documentation** (2-3h)
- [ ] Phase 9 completed (Documentation)
- [ ] All technical docs created/updated
- [ ] User guide updated

### **Sprint 7: Advanced Features** (Optional, 2h)
- [ ] Phase 6 completed (Export, Clean Duplicates)

---

## ⚠️ Important Constraints

### **Code Quality**
- ✅ All code comments in **ENGLISH**
- ✅ All docstrings in **ENGLISH**
- ✅ Follow existing code patterns
- ✅ Use type hints where applicable

### **Git Workflow**
- ⛔ **NO CHANGELOG UPDATES** until user approval
- ⛔ **NO GIT COMMIT** until user approval
- ⛔ **NO GIT PUSH** until user approval
- ✅ Work on branch `108_Imp_Armo`
- ✅ Test thoroughly before any commit

### **Translations**
- ✅ Full FR/EN/DE support
- ✅ Use translation keys for all UI text
- ✅ Test all 3 languages

### **Portability**
- ✅ Must work in .exe `--onefile` build
- ✅ Internal DB embedded in .exe
- ✅ Personal DB in user folder (not embedded)
- ✅ Use `get_app_root()` for path resolution

---

## 📊 Estimated Timeline

| Phase | Description | Time | Status |
|-------|-------------|------|--------|
| 0 | Preparation | - | ✅ Done |
| 1 | Config & Data | 2-3h | ⏳ Pending |
| 2 | Translations | 1h | ⏳ Pending |
| 3 | Backend | 2-3h | ⏳ Pending |
| 4 | UI Settings | 2-3h | ⏳ Pending |
| 5 | Integration | 1-2h | ⏳ Pending |
| 6 | Advanced | 2h | 🔵 Optional |
| 7 | Build | 1-2h | ⏳ Pending |
| 8 | Testing | 1-2h | ⏳ Pending |
| 9 | Documentation | 2-3h | ⏳ Pending |
| **TOTAL** | **All phases** | **14-21h** | **0% Complete** |

---

## 🚀 Next Steps

1. ✅ Review this implementation plan
2. ⏳ Get user approval before starting
3. ⏳ Start with Sprint 1 (Backend)
4. ⏳ Test each phase before moving to next
5. ⏳ Update this tracking file as progress is made
6. ⏳ **DO NOT** update changelog until final approval
7. ⏳ **DO NOT** commit/push until final approval

---

## 📝 Notes

- This is a **major feature** requiring careful implementation
- Each phase should be tested before moving to next
- Keep this tracking file updated with progress
- User approval required before any git operations
- All code must be production-ready before commit

---

**Last Updated**: November 18, 2025  
**Next Review**: After Phase 1 completion  
**Status**: 📋 Planning Complete - Awaiting User Approval to Start Implementation
