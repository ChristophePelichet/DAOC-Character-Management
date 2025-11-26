# GitHub Wiki Help System - Implementation Documentation

**Date**: November 15, 2025  
**Version**: 0.108  
**Feature**: Wiki-based documentation system

---

## 📋 Overview

The DAOC Character Manager uses **GitHub Wiki** as its primary documentation and help system. This approach provides several advantages over an in-app help system:

- 🌐 **Accessible anywhere** - No need to open the application
- 📝 **Easy to edit** - Direct editing on GitHub with Markdown
- 🔍 **Built-in search** - GitHub's search engine
- 📱 **Responsive** - Works on mobile/tablet
- 🔗 **Shareable links** - Easy to share with other users
- 🌍 **Multilingual** - Separate pages for FR/EN/DE
- ✏️ **Community contributions** - Users can suggest improvements
- 📖 **Version control** - Full history of changes

---

## 🏗️ Architecture

### Repository Structure

The Wiki is configured as a **Git submodule** within the main project:

```
DAOC-Character-Management/
├── Wiki/                           # Git submodule
│   ├── .git/                      # Wiki repository
│   ├── Home.md                    # Multilingual homepage
│   ├── FR-Home.md                 # French documentation index
│   ├── FR-Create-Character.md     # Create character guide (FR)
│   ├── FR-Edit-Character.md       # Edit character guide (FR)
│   ├── FR-Delete-Character.md     # Delete character guide (FR)
│   ├── EN-Home.md                 # English documentation index (future)
│   └── DE-Home.md                 # German documentation index (future)
├── .gitmodules                    # Submodule configuration
└── main.py                        # Application entry point
```

### Submodule Setup

The Wiki is added as a Git submodule pointing to:
```
https://github.com/ChristophePelichet/DAOC-Character-Management.wiki.git
```

This allows:
1. **Dual tracking**: Wiki pages are tracked in both repos
2. **Easy updates**: Edit files locally in `Wiki/` and push to the Wiki repo
3. **Synchronized versions**: Main project references specific Wiki commit

---

## 🔗 Application Integration

### Menu System

The Help menu provides direct access to the Wiki:

**Location**: `Functions/ui_manager.py`

```python
# Help menu with F1 shortcut
wiki_doc_action = QAction(lang.get("menu_help_documentation"), self.main_window)
wiki_doc_action.setShortcut("F1")
wiki_doc_action.triggered.connect(self._open_wiki_documentation)
help_menu.addAction(wiki_doc_action)
```

### Link Generation

Wiki links are language-aware:

**Location**: `Functions/ui_manager.py`, `main.py`

```python
def _open_wiki_documentation(self):
    """Opens GitHub Wiki in browser"""
    import webbrowser
    from Functions.config_manager import config
    
    # Determine language for Wiki link
    current_lang = config.get("language", "fr").upper()
    wiki_url = f"https://github.com/ChristophePelichet/DAOC-Character-Management/wiki/{current_lang}-Home"
    webbrowser.open(wiki_url)
```

### Keyboard Shortcuts

- **F1**: Opens Wiki homepage (language-specific)
- **Menu → Help → Documentation**: Same as F1

---

## 📄 Wiki Page Structure

### Naming Convention

Pages follow a strict naming pattern:

```
{LANG}-{Page-Title}.md
```

Examples:
- `FR-Home.md` → https://github.com/.../wiki/FR-Home
- `EN-Create-Character.md` → https://github.com/.../wiki/EN-Create-Character
- `DE-Edit-Character.md` → https://github.com/.../wiki/DE-Edit-Character

**Important**:
- ✅ Case-sensitive: `FR-Home` ≠ `fr-home`
- ✅ Hyphens for spaces: `Create-Character` not `Create Character`
- ✅ No `.md` in URLs: Link to `FR-Home` not `FR-Home.md`

### Content Organization

Each documentation page includes:

1. **Title with emoji** - Visual identification
2. **Summary** - Quick overview
3. **Objectives** - What users will learn
4. **Detailed steps** - Step-by-step instructions with screenshots
5. **Keyboard shortcuts** - Quick reference table
6. **Common errors** - Troubleshooting section
7. **Tips & advice** - Best practices
8. **Related topics** - Cross-links to other pages

---

## 🌍 Multilingual Support

### Current Status (v0.108)

- ✅ **French (FR)**: Complete documentation (5 pages)
  - FR-Home.md
  - FR-Create-Character.md
  - FR-Edit-Character.md
  - FR-Delete-Character.md
  
- 🔲 **English (EN)**: Planned
- 🔲 **German (DE)**: Planned

### Adding New Languages

To add a new language:

1. **Create pages** in `Wiki/`:
   ```
   EN-Home.md
   EN-Create-Character.md
   EN-Edit-Character.md
   EN-Delete-Character.md
   ```

2. **Translate content** from French pages

3. **Commit and push** to Wiki repo:
   ```powershell
   cd Wiki
   git add EN-*.md
   git commit -m "docs: Add English documentation"
   git push origin master
   ```

4. **Update main project** reference:
   ```powershell
   cd ..
   git add Wiki
   git commit -m "docs: Update Wiki submodule (EN pages)"
   git push
   ```

---

## 🔄 Workflow for Wiki Updates

### Method 1: Direct GitHub Edit (Recommended for small changes)

1. Navigate to Wiki page on GitHub
2. Click "Edit" button
3. Make changes in Markdown editor
4. Click "Save Page"
5. Changes are immediately live

### Method 2: Local Edit via Submodule (Recommended for bulk changes)

1. **Edit locally**:
   ```powershell
   cd Wiki
   # Edit files in your IDE
   ```

2. **Commit to Wiki repo**:
   ```powershell
   git add .
   git commit -m "docs: Update character creation guide"
   git push origin master
   ```

3. **Update main project reference**:
   ```powershell
   cd ..
   git add Wiki
   git commit -m "docs: Update Wiki submodule"
   git push
   ```

---

## 🗑️ Removed Components

The following components were **removed** during the Wiki migration:

### Deleted Files
- ✅ `Help/` folder (entire directory)
  - `Help/help_database.json` - JSON help content
  - `Help/fr/character_create.md` - Migrated to Wiki
  - `Help/fr/character_edit.md` - Migrated to Wiki
  - `Help/fr/character_delete.md` - Migrated to Wiki
- ✅ `Functions/help_system.py` - In-app help dialog system
- ✅ `Functions/tooltip_manager.py` - Tooltip automation from JSON
- ✅ `Scripts/create_complete_help_database.py` - JSON generator

### Modified Files
- ✅ `main.py`:
  - Removed `show_help_create_character()` in-app dialog
  - Replaced with `webbrowser.open()` to Wiki
  
- ✅ `Functions/ui_manager.py`:
  - Removed Help submenu with 3 entries
  - Replaced with single "Documentation" entry (F1)
  
- ✅ `UI/dialogs.py`:
  - Removed `_apply_tooltips()` method
  - Removed `TooltipManager` import

---

## 📊 Benefits vs. In-App Help

| Feature | In-App Help | GitHub Wiki |
|---------|-------------|-------------|
| **Accessibility** | App must be open | Accessible anywhere |
| **Editing** | Requires code changes | Direct GitHub edit |
| **Search** | Limited local search | Full GitHub search |
| **Mobile** | Desktop only | Responsive/mobile |
| **Sharing** | Screenshots only | Direct links |
| **Contributions** | Pull requests | Wiki edit suggestions |
| **Versioning** | Coupled with app | Independent history |
| **App size** | Larger (embedded help) | Smaller (external) |
| **Maintenance** | Code + JSON updates | Markdown only |

---

## 🔧 Technical Details

### Dependencies

**Removed**:
- ❌ `markdown` (requirements.txt) - No longer needed for in-app rendering

**Added**:
- ✅ Git submodule configuration (`.gitmodules`)

### URL Format

Wiki URLs follow this pattern:
```
https://github.com/{OWNER}/{REPO}/wiki/{PAGE-TITLE}
```

Example:
```
https://github.com/ChristophePelichet/DAOC-Character-Management/wiki/FR-Create-Character
```

### Language Detection

The application detects the user's language preference and opens the corresponding Wiki page:

```python
current_lang = config.get("language", "fr")  # Get from config
wiki_url = f"https://github.com/.../wiki/{current_lang.upper()}-Home"
```

Supported languages:
- `fr` → `FR-Home`
- `en` → `EN-Home`
- `de` → `DE-Home`

---

## 📝 Future Enhancements

### Planned Features

1. **Complete EN/DE translations**
   - Translate all 4 pages to English and German
   - Maintain consistency across languages

2. **Additional topics**
   - Import from Eden Herald
   - Realm ranks system
   - Armor management
   - Settings and configuration
   - Troubleshooting guide

3. **Search functionality**
   - Leverage GitHub Wiki search
   - Add custom search page if needed

4. **Tips of the Day**
   - Could link to specific Wiki sections
   - Display on app startup (optional)

5. **Video tutorials**
   - Embed YouTube videos in Wiki pages
   - Screenshot galleries with annotations

---

## 🐛 Troubleshooting

### Wiki not opening from app

**Symptom**: Clicking F1 or Help → Documentation does nothing

**Solutions**:
1. Check internet connection
2. Verify Wiki is published on GitHub
3. Check `config.json` for valid language setting
4. Test URL manually in browser

### Links broken between Wiki pages

**Symptom**: Clicking "See Also" links shows 404

**Solutions**:
1. Verify exact page title (case-sensitive)
2. Use hyphens not spaces: `FR-Create-Character`
3. Don't include `.md` extension in links
4. Check page exists on GitHub Wiki

### Submodule not updating

**Symptom**: Local Wiki folder shows old content

**Solutions**:
```powershell
# Pull latest Wiki changes
cd Wiki
git pull origin master

# Update main project reference
cd ..
git add Wiki
git commit -m "docs: Update Wiki submodule"
```

---

## 📚 References

- **GitHub Wiki Documentation**: https://docs.github.com/en/communities/documenting-your-project-with-wikis
- **Git Submodules**: https://git-scm.com/book/en/v2/Git-Tools-Submodules
- **Markdown Guide**: https://www.markdownguide.org/

---

## 📋 Migration Summary

**Migrated from**:
- In-app help system with HelpDialog
- JSON-based help database
- Embedded Markdown rendering

**Migrated to**:
- GitHub Wiki with public access
- Direct Markdown files
- Browser-based rendering

**Result**:
- ✅ Simpler codebase (-700 lines)
- ✅ Better user experience (accessible anywhere)
- ✅ Easier maintenance (no code changes for help updates)
- ✅ Community-friendly (Wiki edit suggestions)

---

**Last Updated**: November 15, 2025  
**Author**: Development Team  
**Status**: ✅ Production Ready
