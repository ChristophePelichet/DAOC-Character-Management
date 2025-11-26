# Language System - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [V2 Migration](#v2-migration)
4. [Hierarchical Structure](#hierarchical-structure)
5. [Implementation Guide](#implementation-guide)
6. [Translation System](#translation-system)
7. [Testing](#testing)
8. [Version History](#version-history)

---

## Overview

The Language System manages multi-language support throughout the application, providing a hierarchical key-value translation system with automatic migration from legacy flat structures.

**Location**: `Functions/language_manager.py`  
**Current Version**: V2 (Hierarchical)  
**Supported Languages**: French (FR), English (EN), German (DE)  
**Key Structure**: Nested dot-notation (e.g., `menu.file.settings`)

---

## Architecture

### **Language Files**

```
Language/
├── fr.json (French - Default)
├── en.json (English)
└── de.json (German)
```

### **Key Pattern Evolution**

**V1 (Flat Structure - Deprecated)**:
```json
{
    "menu_file_settings": "Paramètres",
    "menu_file_exit": "Quitter",
    "config_path_label": "Répertoire des personnages"
}
```

**V2 (Hierarchical Structure - Current)**:
```json
{
    "menu": {
        "file": {
            "settings": "Paramètres",
            "exit": "Quitter"
        }
    },
    "config": {
        "path_label": "Répertoire des personnages"
    }
}
```

---

## V2 Migration

### **Migration Overview**

**Stats**:
- **V1 Keys**: 417 flat keys
- **V2 Sections**: 13 hierarchical sections
- **Status**: Complete (v0.108)

### **13 Sections**

| Section | Description | Example Keys |
|---------|-------------|--------------|
| `menu` | Menu bar items | `menu.file.settings`, `menu.help.about` |
| `window` | Window titles | `window.title`, `window.settings` |
| `config` | Configuration labels | `config.path_label`, `config.backup_path` |
| `settings` | Settings dialog | `settings.general_title`, `settings.nav_themes` |
| `backup` | Backup system | `backup.enabled_label`, `backup.now_button` |
| `herald` | Eden Herald | `herald.connect_button`, `herald.status_connected` |
| `armory` | Armory system | `armory.import_button`, `armory.stats_total` |
| `character` | Character data | `character.name`, `character.level` |
| `columns` | Table columns | `columns.realm`, `columns.class` |
| `dialogs` | Dialog messages | `dialogs.confirm_delete`, `dialogs.error_title` |
| `buttons` | Generic buttons | `buttons.ok`, `buttons.cancel` |
| `errors` | Error messages | `errors.file_not_found`, `errors.invalid_data` |
| `help` | Help system | `help.getting_started`, `help.faq` |

### **Migration Logic**

```python
from Functions.language_migration import migrate_language_files

# Automatically called on startup
migrate_language_files()
```

**Process**:
1. Detect V1 structure (flat keys)
2. Parse keys by underscore separators
3. Build hierarchical dictionary
4. Write V2 format with proper nesting
5. Keep backup of V1 (`.v1_backup.json`)

**Trigger**: First run after v0.108 update

---

## Hierarchical Structure

### **Dot Notation**

**Access Pattern**:
```python
lang.get("menu.file.settings")
# Returns: "Paramètres" (FR) or "Settings" (EN)

lang.get("settings.pages.general.title")
# Returns: "Général" (FR) or "General" (EN)
```

### **Section Breakdown**

**Menu Section**:
```json
{
    "menu": {
        "file": {
            "new": "Nouveau",
            "open": "Ouvrir",
            "save": "Enregistrer",
            "settings": "Paramètres",
            "exit": "Quitter"
        },
        "edit": {
            "copy": "Copier",
            "paste": "Coller"
        },
        "help": {
            "about": "À propos",
            "documentation": "Documentation"
        }
    }
}
```

**Settings Section**:
```json
{
    "settings": {
        "title": "Paramètres",
        "navigation": {
            "general": "Général",
            "themes": "Thèmes",
            "startup": "Démarrage",
            "columns": "Colonnes",
            "herald": "Eden",
            "backup": "Sauvegardes",
            "debug": "Debug",
            "superadmin": "SuperAdmin"
        },
        "pages": {
            "general": {
                "title": "Paramètres généraux",
                "subtitle": "Configuration des dossiers et paramètres par défaut"
            }
        }
    }
}
```

**Herald Section**:
```json
{
    "herald": {
        "connect_button": "Se connecter à Herald",
        "disconnect_button": "Se déconnecter",
        "status": {
            "connected": "Connecté",
            "disconnected": "Déconnecté",
            "error": "Erreur de connexion"
        },
        "scraping": {
            "start": "Démarrer l'extraction",
            "stop": "Arrêter",
            "progress": "Progression: {0}%"
        }
    }
}
```

---

## Implementation Guide

### **Using Language Manager**

```python
from Functions.language_manager import lang

# Get translated string
text = lang.get("menu.file.settings")

# Get with default fallback
text = lang.get("new.key.path", default="Default Value")

# Get with placeholder replacement
text = lang.get("herald.scraping.progress", 0="75")
# Returns: "Progression: 75%"
```

### **Setting Language**

```python
# Change language (saves to config)
lang.set_language("en")

# Get current language
current = lang.get_current_language()  # Returns: "fr", "en", or "de"
```

### **Adding New Keys**

**1. Choose Section**: Determine logical hierarchy

```python
# Menu item → menu section
"menu.file.new_character"

# Settings option → settings section
"settings.pages.backup.title"

# Error message → errors section
"errors.herald.connection_failed"
```

**2. Add to All 3 Language Files**:

**fr.json**:
```json
{
    "menu": {
        "file": {
            "new_character": "Nouveau personnage"
        }
    }
}
```

**en.json**:
```json
{
    "menu": {
        "file": {
            "new_character": "New Character"
        }
    }
}
```

**de.json**:
```json
{
    "menu": {
        "file": {
            "new_character": "Neuer Charakter"
        }
    }
}
```

**3. Use in Code**:

```python
button = QPushButton(lang.get("menu.file.new_character"))
```

---

## Translation System

### **Language File Structure**

**Metadata** (Top-level):
```json
{
    "__metadata__": {
        "language": "fr",
        "version": "2.0",
        "last_updated": "2025-11-18"
    },
    "menu": { ... },
    "settings": { ... }
}
```

### **Translation Guidelines**

**Key Naming**:
- Use lowercase
- Separate with dots for hierarchy
- Use underscores within words if needed
- Descriptive, not abbreviated

**Examples**:
```
✅ menu.file.save_as
✅ settings.pages.general.title
✅ errors.file_not_found

❌ menuFileSaveAs (camelCase)
❌ menu_file_save_as (flat)
❌ mfs (abbreviation)
```

**Placeholders**:
```python
# In JSON
"message": "Loaded {0} characters from {1}"

# In code
lang.get("message", 0="42", 1="Albion")
# Returns: "Loaded 42 characters from Albion"
```

### **Translation Quality Checklist**

- [ ] All 3 languages (FR, EN, DE) updated
- [ ] Consistent tone and formality
- [ ] Proper grammar and punctuation
- [ ] Context-appropriate terminology
- [ ] Special characters properly encoded (UTF-8)
- [ ] Placeholders match across languages
- [ ] No hard-coded emojis in JSON (add in code)

---

## Testing

### **Manual Testing**

```python
# Test language switching
lang.set_language("fr")
assert lang.get("menu.file.exit") == "Quitter"

lang.set_language("en")
assert lang.get("menu.file.exit") == "Exit"

lang.set_language("de")
assert lang.get("menu.file.exit") == "Beenden"
```

### **Key Existence Check**

```python
# Returns None if key doesn't exist
result = lang.get("nonexistent.key")
assert result is None

# Use default fallback
result = lang.get("nonexistent.key", default="Fallback")
assert result == "Fallback"
```

### **Migration Testing**

```python
# Simulate V1 file
v1_data = {
    "menu_file_exit": "Quitter",
    "menu_file_settings": "Paramètres"
}

# Run migration
migrate_language_files()

# Verify V2 structure
v2_data = lang._load_language("fr")
assert "menu" in v2_data
assert "file" in v2_data["menu"]
assert v2_data["menu"]["file"]["exit"] == "Quitter"
```

---

## Version History

### **V1 (Flat Structure)**
- **Period**: Launch → v0.107
- **Keys**: 417 flat keys
- **Format**: `section_subsection_key`
- **Status**: Deprecated (migrated automatically)

### **V2 (Hierarchical)**
- **Period**: v0.108 → Current
- **Sections**: 13 hierarchical sections
- **Format**: `section.subsection.key`
- **Migration**: Automatic on first run
- **Backup**: `.v1_backup.json` files preserved

**Migration Details**:
```
V1 File: Language/fr.json (417 keys)
   ↓
Migration Script: Functions/language_migration.py
   ↓
V2 File: Language/fr.json (13 sections)
   +
Backup: Language/fr.json.v1_backup.json
```

---

## Related Documentation

- **Language Manager**: `Functions/language_manager.py`
- **Language Migration**: `Functions/language_migration.py`
- **Language Schema**: `Functions/language_schema.py`
- **Settings Dialog**: `UI/settings_dialog.py` (language selection page)

---

**Current Version**: V2 (Hierarchical)  
**Status**: ✅ Active Standard  
**Last Updated**: 2025-11-18
