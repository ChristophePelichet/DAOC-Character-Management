# Copilot Instructions - Base Rules

## 🚫 NEVER DO AUTOMATICALLY

**ONLY on explicit user request:**
- ❌ Git commit
- ❌ Git push
- ❌ Git merge
- ❌ Documentation modifications (README, CHANGELOG, etc.)
- ❌ Translations (Language/*.json)
- ❌ Generate documentation, comments, JSDoc blocks, or README files
- ❌ Modify existing documentation, changelogs, or readme files
- ❌ Change version numbers in documentation

## 🔄 Git Rules

**When performing Git operations (only on explicit user request):**
- **ALL commit messages MUST be in English** - No exceptions, detailed and descriptive
- **Commit message format**: Use conventional commits style (feat:, fix:, docs:, refactor:, etc.)
- **Commit message details**: Be as detailed as possible, explain what, why, and how
- **Merge operations**: ALWAYS use `--no-ff` flag to preserve branch history
  - Example: `git merge feature-branch --no-ff`
  - This creates a merge commit even for fast-forward merges

### Git Branch Naming Convention
- **Format**: `{prefix}/v{version}-{description}`
- **Prefix**: Use `feature/`, `fix/`, `refactor/`, `docs/`, `chore/`, `hotfix/`, or `test/`
- **Version**: Prepend the target version number (e.g., v0.108, v1.5.0)
- **Description**: Use kebab-case (lowercase with hyphens), be descriptive
- **Examples**:
  - `feature/v0.108-dialogs-refactoring-preparation`
  - `feature/v0.108-template-parser-extraction`
  - `fix/v0.108-character-validation-bug`
  - `refactor/v0.108-extract-business-logic`
  - `docs/v0.108-update-refactoring-guide`
  - `chore/v0.108-update-dependencies`
- **Rules**:
  - ✅ All lowercase
  - ✅ Use hyphens to separate words
  - ✅ Keep under 60 characters if possible
  - ✅ Be descriptive about what the branch does

## ✅ Standard Workflow

**When user requests a feature/fix:**

1. **Implementation ONLY**: Write the requested code
2. **STOP**: Wait for user instructions
3. **Ask user** if they want: commit, translations, documentation, etc.

## 📝 Code Rules

### Language Requirements
- **ALL code comments MUST be in English** - No exceptions, no French or German in code
- **ALL docstrings MUST be in English** - Function/class/module documentation in English only
- **ALL technical documentation MUST be in English** - Documentation files, README, technical specs
- **Variable names in English**
- **Function/class names in English**
- **Only UI strings use lang.get() for translations** - User-facing text only (English fallback)

### Python Code Standards (PEP 8)
- **Follow PEP 8 style guide strictly**
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Group in order (standard library, third-party, local) with blank line between groups
- **Naming conventions**:
  - `snake_case` for functions, variables, methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- **Whitespace**: Follow PEP 8 rules (spaces around operators, after commas, etc.)
- **Docstrings**: Use triple double-quotes `"""` for all public modules, functions, classes, methods

### Function Naming Convention (Domain-Driven Prefixes)
- **Pattern**: `{domain}_{action}_{object}` - Use domain prefix for related functions
- **Purpose**: Group functions by functionality for better discoverability and maintainability
- **Examples by domain**:
  - **Template parsing**: `template_parse()`, `template_detect_format()`, `template_parse_loki()`, `template_strip_color_markers()`
  - **Item prices**: `price_sync_template()`, `price_find_missing_items()`, `price_calculate_total()`
  - **Character validation**: `character_get_classes_for_realm()`, `character_validate_race()`, `character_handle_class_change()`
  - **Realm ranks**: `realm_rank_calculate_from_points()`, `realm_rank_get_valid_levels()`, `realm_rank_format_display()`
  - **Herald integration**: `herald_update_character()`, `herald_scrape_stats()`, `herald_apply_scraped_data()`
  - **Armor handling**: `armor_upload_to_s3()`, `armor_validate_structure()`, `armor_build_payload()`
  - **Image processing**: `image_capture_sheet()`, `image_save_to_armory()`, `image_resize_for_upload()`
  - **Model gallery**: `model_gallery_load_metadata()`, `model_gallery_apply_filters()`, `model_gallery_build_thumbnail_list()`
- **Benefits**:
  - ✅ Autocomplete groups related functions (type `template_` to see all template functions)
  - ✅ Immediate clarity on function domain (`realm_rank_` = realm rank functions)
  - ✅ Easy maintenance and searching (`grep "^def herald_"`)
  - ✅ Logical grouping in imports and documentation

### File Naming Convention for UI/Functions Coupling
- **Pattern**: When a UI component is tightly coupled to specific business logic, name them consistently
- **Rule**: If `Functions/{domain}_{feature}.py` exists → Create `UI/ui_{domain}_{feature}.py`
- **Examples**:
  - `Functions/model_gallery_filter.py` → `UI/ui_model_gallery_filter.py`
  - `Functions/herald_url_validator.py` → `UI/ui_herald_url_validator.py` (if UI needed)
  - `Functions/character_actions_manager.py` → `UI/ui_character_actions_manager.py` (if UI needed)
- **Benefits**:
  - ✅ Immediate visual pairing in IDE (ui_* prefix makes relationship clear)
  - ✅ Easy to find related business logic
  - ✅ Clear separation: Functions = logic, UI = presentation
  - ✅ Scalability: Adding new features maintains predictable structure

### Translation & UI Rules

**Supported Languages (Software UI only):**
- 🇬🇧 English (en.json)
- 🇫🇷 French (fr.json)
- 🇩🇪 German (de.json)

**Translation Guidelines:**
- **NEVER hardcode user-facing text in code** - Always use Language/*.json files with lang.get()
- **Always implement retranslate_ui() for dialogs/windows** - UI must refresh when language changes
- **Always think about refreshing UI items when language changes** - Update labels, buttons, menus, etc.
- **Update ALL language files** - When adding new UI text, add translations to en.json, fr.json, AND de.json
- **Note**: These 3 languages apply ONLY to the software UI. All documentation, comments, docstrings, and technical specs MUST remain in English only

## 📁 Folder Structure Rules

- **Technical documentation**: Must be created in `Documentations/` folder (not "Documentation")
- **Changelogs**: Must be created in `Changelogs/` folder
- **Utility scripts**: Must be created in `Tools/` folder with appropriate subdirectory:
  - `Tools/DataScraping/` - Web scraping scripts (Eden, official DAOC website)
  - `Tools/DatabaseMaintenance/` - Database repair, migration, consistency checks
  - `Tools/Development/` - Development and debugging utilities
- **Debug scripts cleanup**: When debug scripts are no longer needed, delete them. If keeping a debug script, update `Tools/README.md` to document it.

## 📚 Documentation Standards

**When creating technical documentation:**

### File Naming Convention
- **Format**: `FEATURE_TECHNICAL_DOCUMENTATION.md`
- **Location**: `Documentations/FeatureName/`
- **Examples**: `BACKUP_TECHNICAL_DOCUMENTATION.md`, `ARMORY_TECHNICAL_DOCUMENTATION.md`

### Document Structure
- **Header**: Title with emoji + "Technical Documentation"
- **Metadata Section**:
  - Version number
  - Date (Month Year format)
  - Last Updated date
  - Component (main file path)
  - Related (related files/modules)
- **Table of Contents**: Numbered sections with anchor links
- **Required Sections**:
  1. Overview - Brief description of the feature
  2. System Architecture - Components and their relationships
  3. Workflow/Process - Step-by-step flow diagrams
  4. Configuration Settings - All related settings
  5. User Guide - How to use the feature
  6. Error Handling - Error cases and recovery
  7. Performance Considerations - Optimization notes
  8. Security Considerations - Security aspects
  9. Version History - Changes log
  10. FAQ - Common questions
- **Code Examples**: Always use proper markdown code blocks with language tags
- **Visual Aids**: Use emojis (✅, ❌, ⚠️) and markdown tables for clarity

## 🔬 Testing Rules

- **Always run main.py from the virtual environment** - Use `python .\main.py` after activating `.venv`
- **Never run tests outside .venv** - Dependencies are installed in virtual environment only
- **Always reuse the existing terminal for running commands** - Do not create new terminal instances if one is already open
- **Ensure all Python commands are run within the activated virtual environment** - Activate `.venv` before executing Python code


**Otherwise: Code only, then STOP and wait**
