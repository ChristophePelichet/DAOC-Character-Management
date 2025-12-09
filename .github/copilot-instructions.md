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

## ✅ Standard Workflow

**When user requests a feature/fix:**

1. **Implementation ONLY**: Write the requested code
2. **STOP**: Wait for user instructions
3. **Ask user** if they want: commit, translations, documentation, etc.

## 📝 Code Rules

### Language Requirements
- **ALL code comments MUST be in English** - No exceptions, no French in code
- **ALL docstrings MUST be in English** - Function/class/module documentation in English only
- **ALL technical documentation MUST be in English** - Documentation files, README, technical specs
- **Variable names in English**
- **Function/class names in English**
- **Only UI strings use lang.get() for translations** - User-facing text only

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

### Translation & UI Rules
- **NEVER hardcode user-facing text in code** - Always use Language/*.json files with lang.get()
- **Always implement retranslate_ui() for dialogs/windows** - UI must refresh when language changes
- **Always think about refreshing UI items when language changes** - Update labels, buttons, menus, etc.

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


**Otherwise: Code only, then STOP and wait**
