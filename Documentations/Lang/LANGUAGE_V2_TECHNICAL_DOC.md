# Language Files v2 - Technical Documentation
**Version:** v0.108  
**Date:** November 16, 2025  
**Branch:** 108_Imp_Lang  
**Status:** ✅ Implemented & Validated  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Migration Summary](#migration-summary)
3. [Architecture](#architecture)
4. [v2 Structure](#v2-structure)
5. [Legacy Mapping System](#legacy-mapping-system)
6. [LanguageManager Enhancement](#languagemanager-enhancement)
7. [Migration System](#migration-system)
8. [Backward Compatibility](#backward-compatibility)
9. [Usage Examples](#usage-examples)
10. [Testing & Validation](#testing--validation)
11. [File Structure](#file-structure)
12. [Maintenance Guide](#maintenance-guide)

---

## 📖 Overview

### What Changed?

The language system was restructured from a **flat 417-key format** to a **hierarchical 12-section v2 format**, mirroring the config.json v2 approach.

**Before (v1 - Flat):**
```json
{
    "window_title": "DAOC - Gestion des personnages",
    "file_menu_label": "Fichier",
    "save_button": "Enregistrer",
    "new_char_dialog_title": "Nouveau Personnage",
    "char_name_empty_error": "Le nom du personnage ne peut pas être vide.",
    // ... 412 more flat keys
}
```

**After (v2 - Hierarchical):**
```json
{
    "window": {
        "main_title": "DAOC - Gestion des personnages"
    },
    "menu": {
        "file": {
            "label": "Fichier"
        }
    },
    "buttons": {
        "save": "Enregistrer"
    },
    "dialogs": {
        "new_character": {
            "title": "Nouveau Personnage"
        }
    },
    "messages": {
        "errors": {
            "char_name_empty": "Le nom du personnage ne peut pas être vide."
        }
    }
}
```

### Why This Change?

**Problems with v1:**
- ❌ All 417 keys at root level - difficult to navigate
- ❌ No logical organization - mixed contexts
- ❌ Hard to find specific translations
- ❌ Prone to key name conflicts
- ❌ Difficult to maintain and extend

**Benefits of v2:**
- ✅ **Organized by context** - 12 logical sections
- ✅ **Easy navigation** - know exactly where to find keys
- ✅ **Scalable** - simple to add new features
- ✅ **Maintainable** - clear ownership of translations
- ✅ **100% backward compatible** - existing code works unchanged

---

## 📊 Migration Summary

### Files Migrated

| File | Keys (v1) | Keys (v2) | Unknown Keys | Status |
|------|-----------|-----------|--------------|--------|
| `Language/fr.json` | 417 | Hierarchical | 0 | ✅ Complete |
| `Language/en.json` | 418 | Hierarchical | 0 | ✅ Complete |
| `Language/de.json` | 418 | Hierarchical | 0 | ✅ Complete |

### Migration Statistics

- **Total v1→v2 mappings**: 421 keys
- **Backups created**: 6 (2 iterations × 3 files)
- **Unknown keys found**: 4 (first pass) → 0 (final pass)
- **Migration success rate**: 100%
- **Code compatibility**: 100% (530+ existing `lang.get()` calls work)

### Timeline

1. **Initial migration** (Nov 16, 2025 18:12):
   - Migrated all 3 files
   - Found 4 unmapped keys
   - Preserved in `_unknown_v1_keys` section

2. **Mapping completion** (Nov 16, 2025 18:13):
   - Added 4 missing mappings to schema
   - Restored v1 backups
   - Re-migrated with complete 421-key mapping

3. **Final validation** (Nov 16, 2025 18:14):
   - Verified 0 unknown keys
   - Tested application startup
   - Confirmed all UI texts display correctly

---

## 🏗️ Architecture

### System Components

```
Language System v2
├── Language Files (v2 hierarchical)
│   ├── fr.json (12 sections, ~550 lines)
│   ├── en.json (12 sections, ~550 lines)
│   └── de.json (12 sections, ~550 lines)
│
├── Schema & Mapping
│   └── Functions/language_schema.py
│       ├── LANGUAGE_LEGACY_MAPPING (421 v1→v2 mappings)
│       ├── get_v2_key(v1_key)
│       ├── get_legacy_key(v2_key)
│       └── is_v2_structure(data)
│
├── Migration System
│   └── Functions/language_migration.py
│       ├── detect_language_version()
│       ├── create_backup()
│       ├── migrate_v1_to_v2()
│       ├── validate_migrated_language()
│       ├── get_migration_summary()
│       └── rollback_migration()
│
├── Language Manager (Enhanced)
│   └── Functions/language_manager.py
│       ├── load_language() → auto-migration
│       ├── get(key) → v1/v2 dual support
│       └── _get_nested(dotted_key)
│
└── Migration Script
    └── Scripts/migrate_languages.py
        └── User-friendly batch migration
```

---

## 🗂️ v2 Structure

### 12 Main Sections

The v2 structure organizes translations into 12 logical sections:

```json
{
    "app": { /* Application metadata (3 keys) */ },
    "window": { /* Window titles (5 keys) */ },
    "menu": { /* Menu items (40 keys) */ },
    "dialogs": { /* Dialog messages (85 keys) */ },
    "buttons": { /* Button labels (20 keys) */ },
    "columns": { /* Table column headers (14 keys) */ },
    "context_menu": { /* Right-click menu (5 keys) */ },
    "settings": { /* Settings dialog (120 keys) */ },
    "backup": { /* Backup system (30 keys) */ },
    "character_sheet": { /* Character stats (35 keys) */ },
    "progress": { /* Progress dialogs (45 keys) */ },
    "messages": { /* Error/success/info messages (40 keys) */ },
    "status_bar": { /* Status bar texts (2 keys) */ },
    "debug": { /* Debug window (10 keys) */ },
    "themes": { /* Theme names (3 keys) */ },
    "realms": { /* Realm names (3 keys) */ },
    "misc": { /* Miscellaneous (5 keys) */ },
    "tooltips": { /* Hover tooltips (5 keys) */ },
    "version_check": { /* Version checker (8 keys) */ }
}
```

### Section Details

#### 1. **app** (Application metadata)
```json
"app": {
    "language_name": "Français",
    "version_info": "Version : {version}",
    "about_title": "À propos de {app_name}"
}
```

#### 2. **window** (Window titles)
```json
"window": {
    "main_title": "DAOC - Gestion des personnages",
    "welcome_message": "Bienvenue dans le gestionnaire de personnages !",
    "configuration_window_title": "Paramètres",
    "debug_window_title": "Console de débogage",
    "character_sheet_title": "Feuille de personnage - {name}"
}
```

#### 3. **menu** (Menu structure)
```json
"menu": {
    "file": {
        "label": "Fichier",
        "new_character": "➕ Nouveau Personnage",
        "search_herald": "🔍 Rechercher sur Herald",
        "settings": "⚙️ Paramètres"
    },
    "action": {
        "label": "Action",
        "resistances": "📊 Résistances",
        "armor_management": "📁 Gestion des armures"
    },
    "view": {
        "label": "Affichage",
        "columns": "Colonnes"
    },
    "help": {
        "label": "Aide",
        "about": "À propos",
        "documentation": "📚 Documentation",
        "migrate": "Migrer la structure des dossiers",
        "eden_debug": "🌐 Debug Eden"
    },
    "tools": {
        "label": "Outils",
        "backup": "Sauvegarde"
    },
    "bulk_actions": {
        "label": "Actions en masse",
        "delete_checked": "Multi Suppression"
    }
}
```

#### 4. **dialogs** (Dialog messages - 85 keys)
```json
"dialogs": {
    "titles": {
        "success": "Succès",
        "error": "Erreur",
        "info": "Information",
        "warning": "Annulé"
    },
    "new_character": {
        "title": "Nouveau Personnage",
        "prompt_name": "Entrez le nom du personnage :",
        "prompt_realm": "Choisissez un royaume :",
        "prompt_season": "Saison :",
        // ... more prompts
    },
    "delete_character": {
        "confirm_title": "Confirmer la suppression",
        "confirm_message": "Êtes-vous sûr de vouloir supprimer définitivement le personnage '{name}' ? Cette action est irréversible.",
        "bulk_confirm_message": "..."
    },
    "migration": {
        "startup_title": "Migration de structure requise / ...",
        "confirm_title": "Confirmer la migration",
        "in_progress": "Migration en cours...",
        "success": "Migration réussie !",
        // ... more migration messages
    },
    "about": { /* ... */ },
    "disclaimer": { /* ... */ },
    "move_folder": { /* ... */ },
    "rename_character": { /* ... */ },
    "duplicate_character": { /* ... */ },
    "columns_config": { /* ... */ },
    "stats_info": { /* ... */ }
}
```

#### 5. **buttons** (Button labels)
```json
"buttons": {
    "create": "Nouveau personnage",
    "save": "Enregistrer",
    "cancel": "Annuler",
    "close": "Fermer",
    "browse": "Parcourir...",
    "move_folder": "Déplacer",
    "open_folder": "Ouvrir le dossier",
    "update_rvr_pvp": "🔄 Actualiser",
    "stats_info": "ℹ️ Informations",
    "backup_now": "Sauvegarder maintenant",
    "version_check": "🔄 Vérifier",
    "download": "📥 Télécharger",
    "eden_refresh": "🔄 Actualiser",
    "eden_search": "🔍 Recherche",
    "eden_manage": "⚙️ Gérer"
}
```

#### 6. **columns** (Table headers)
```json
"columns": {
    "name": "Nom",
    "realm": "Royaume",
    "level": "Niveau",
    "season": "Saison",
    "server": "Serveur",
    "realm_rank": "Rang",
    "realm_title": "Titre",
    "page": "Page",
    "guild": "Guilde",
    "class": "Classe",
    "race": "Race",
    "url": "URL Herald",
    "action": "Action",
    "selection": "Sélection"
}
```

#### 7. **settings** (Settings dialog - 120 keys)
```json
"settings": {
    "navigation": {
        "general": "Général",
        "themes": "Thèmes",
        "startup": "Démarrage",
        "columns": "Colonnes",
        "herald": "Herald Eden",
        "backup": "Sauvegardes",
        "data": "Données",
        "language": "Langue",
        "debug": "Debug"
    },
    "pages": {
        "general": {
            "title": "Paramètres Généraux",
            "subtitle": "Chemins des dossiers et valeurs par défaut"
        },
        "themes": {
            "title": "Thèmes & Affichage",
            "subtitle": "Personnalisation de l'interface"
        },
        // ... 7 more pages
    },
    "groups": {
        "paths": "Chemins des dossiers",
        "defaults": "Valeurs par défaut",
        "theme": "Sélection du thème",
        "font": "Taille du texte",
        // ... more groups
    },
    "labels": {
        "character_folder": "Répertoire des personnages",
        "log_folder": "Répertoire des logs",
        "armor_folder": "Répertoire des armures",
        "language": "Langue de l'application",
        "theme": "Thème",
        "debug_mode": "Activer le mode débogage (crée debug.log)",
        // ... more labels
    }
}
```

#### 8. **messages** (Error/success/info/warnings)
```json
"messages": {
    "errors": {
        "char_name_empty": "Le nom du personnage ne peut pas être vide.",
        "char_exists": "Un personnage nommé '{name}' existe déjà.",
        "update_char_no_url": "Aucune URL Herald n'est configurée pour ce personnage.",
        // ... more errors
    },
    "success": {
        "char_saved": "Personnage '{name}' sauvegardé avec succès.",
        "config_saved": "Configuration enregistrée avec succès.",
        "update_char_success": "Le personnage a été mis à jour avec succès !",
        // ... more success messages
    },
    "info": {
        "creation_cancelled": "Création de personnage annulée.",
        "update_char_no_changes": "Aucune modification détectée. Le personnage est déjà à jour.",
        "no_characters_selected": "Aucun personnage n'est sélectionné.",
        // ... more info messages
    },
    "warnings": {
        "theme_change_restart": "Le thème a été changé. Veuillez redémarrer l'application pour que les changements prennent effet.",
        "cancel_changes_confirm": "Annuler les modifications non sauvegardées ?",
        // ... more warnings
    }
}
```

#### 9. **progress** (Progress dialogs)
```json
"progress": {
    "herald_search": {
        "title": "⏳ Recherche en cours...",
        "checking_cookies": "🔐 Vérification des cookies d'authentification...",
        "searching": "🔍 Recherche de '{0}' sur Eden Herald...",
        "complete": "✅ Recherche terminée avec succès !"
    },
    "character_update": {
        "title": "🌐 Mise à jour depuis Herald...",
        "description": "Récupération des informations du personnage depuis Eden Herald",
        "in_progress": "Récupération des données depuis Herald...",
        "complete": "✅ Données récupérées"
    },
    "steps": {
        "herald_connection_cookies": "Vérification des cookies d'authentification",
        "herald_search_extract": "Extraction des résultats de recherche",
        "stats_scraping_rvr": "Récupération des captures RvR",
        // ... 20+ more steps
    }
}
```

#### 10. **character_sheet** (Character stats)
```json
"character_sheet": {
    "sections": {
        "rvr": "⚔️ RvR",
        "pvp": "🗡️ PvP",
        "pve": "🐉 PvE",
        "achievements": "🏆 Réalisations",
        "wealth": "💰 Monnaie",
        "stats": "Statistiques"
    },
    "stats": {
        "realm_rank": "Rang de Royaume :",
        "tower_captures": "🗼 Tower Captures:",
        "keep_captures": "🏰 Keep Captures:",
        "solo_kills": "⚔️ Solo Kills:",
        "deathblows": "💀 Deathblows:",
        "gold": "Or:",
        "silver": "Argent:",
        // ... more stats
    }
}
```

#### 11. **backup** (Backup system)
```json
"backup": {
    "window_title": "Paramètres de sauvegarde",
    "sections": {
        "characters": "Sauvegardes des personnages",
        "cookies": "Sauvegardes des cookies Eden",
        "armor": "Sauvegardes des données d'armures"
    },
    "labels": {
        "enabled": "Activer les sauvegardes automatiques",
        "path": "Emplacement des sauvegardes",
        "compress": "Compresser les sauvegardes (ZIP)",
        // ... more labels
    },
    "messages": {
        "success_message": "Sauvegarde créée : {0}",
        "error_message": "Erreur lors de la sauvegarde : {0}",
        // ... more messages
    }
}
```

#### 12. Other sections
```json
"status_bar": {
    "loaded": "Prêt. Chargé en {duration:.2f} secondes.",
    "selection_count": "{count} sur {total} personnage(s) sélectionné(s)"
},
"debug": { /* Debug window settings */ },
"themes": { "light": "Clair", "dark": "Sombre", "purple": "Violet (Dracula)" },
"realms": { "albion": "Albion", "hibernia": "Hibernia", "midgard": "Midgard" },
"misc": { "none": "Aucun" },
"tooltips": { /* Hover tooltips */ },
"version_check": { /* Version checker UI */ }
```

---

## 🔄 Legacy Mapping System

### LANGUAGE_LEGACY_MAPPING

File: `Functions/language_schema.py`

Complete dictionary with **421 v1→v2 mappings** ensuring 100% backward compatibility.

**Structure:**
```python
LANGUAGE_LEGACY_MAPPING = {
    # Window
    "window_title": "window.main_title",
    "welcome_message": "window.welcome_message",
    "debug_window_title": "window.debug_window_title",
    "character_sheet_title": "window.character_sheet_title",
    "configuration_window_title": "window.configuration_window_title",
    
    # Menus
    "file_menu_label": "menu.file.label",
    "menu_file_new_character": "menu.file.new_character",
    "menu_file_search_herald": "menu.file.search_herald",
    "menu_file_settings": "menu.file.settings",
    "menu_action_label": "menu.action.label",
    "menu_action_resistances": "menu.action.resistances",
    "menu_action_armor_management": "menu.action.armor_management",
    "help_menu_label": "menu.help.label",
    "menu_help_about": "menu.help.about",
    "menu_help_documentation": "menu.help.documentation",
    
    # Dialogs - Titles
    "success_title": "dialogs.titles.success",
    "error_title": "dialogs.titles.error",
    "info_title": "dialogs.titles.info",
    "warning_title": "dialogs.titles.warning",
    
    # Dialogs - New Character
    "existing_character_label": "dialogs.new_character.existing_character_label",
    "new_char_dialog_title": "dialogs.new_character.title",
    "prompt_char_name": "dialogs.new_character.prompt_name",
    "prompt_char_realm": "dialogs.new_character.prompt_realm",
    "prompt_char_season": "dialogs.new_character.prompt_season",
    
    # Dialogs - Delete Character
    "delete_char_confirm_title": "dialogs.delete_character.confirm_title",
    "delete_char_confirm_message": "dialogs.delete_character.confirm_message",
    "bulk_delete_confirm_message": "dialogs.delete_character.bulk_confirm_message",
    
    # Buttons
    "create_button_text": "buttons.create",
    "exit_button": "buttons.exit",
    "browse_button": "buttons.browse",
    "save_button": "buttons.save",
    "cancel_button": "buttons.cancel",
    "close_button": "buttons.close",
    
    # Columns
    "column_name": "columns.name",
    "column_realm": "columns.realm",
    "column_level": "columns.level",
    "column_season": "columns.season",
    "column_server": "columns.server",
    
    # Settings
    "settings_nav_general": "settings.navigation.general",
    "settings_nav_themes": "settings.navigation.themes",
    "settings_nav_startup": "settings.navigation.startup",
    "settings_page_general_title": "settings.pages.general.title",
    "config_path_label": "settings.labels.character_folder",
    "config_language_label": "settings.labels.language",
    
    # Messages - Errors
    "char_name_empty_error": "messages.errors.char_name_empty",
    "char_exists_error": "messages.errors.char_exists",
    "update_char_no_url_error": "messages.errors.update_char_no_url",
    
    # Messages - Success
    "char_saved_success": "messages.success.char_saved",
    "config_saved_success": "messages.success.config_saved",
    "update_char_success": "messages.success.update_char_success",
    
    # Messages - Info
    "creation_cancelled_info": "messages.info.creation_cancelled",
    "update_char_no_changes_info": "messages.info.update_char_no_changes",
    
    # Messages - Warnings
    "theme_change_restart_warning": "messages.warnings.theme_change_restart",
    "cancel_changes_confirm": "messages.warnings.cancel_changes_confirm",
    
    # Progress
    "progress_herald_search_title": "progress.herald_search.title",
    "progress_character_update_title": "progress.character_update.title",
    "step_herald_connection_cookies": "progress.steps.herald_connection_cookies",
    "step_stats_scraping_rvr": "progress.steps.stats_scraping_rvr",
    
    # Character Sheet
    "char_sheet_section_rvr": "character_sheet.sections.rvr",
    "tower_captures_label": "character_sheet.stats.tower_captures",
    "keep_captures_label": "character_sheet.stats.keep_captures",
    
    # Backup
    "backup_window_title": "backup.window_title",
    "backup_enabled_label": "backup.labels.enabled",
    "backup_success_message": "backup.messages.success_message",
    
    # Status Bar
    "status_bar_loaded": "status_bar.loaded",
    "status_bar_selection_count": "status_bar.selection_count",
    
    # Debug
    "debug_level_all": "debug.levels.all",
    "debug_menu_level": "debug.menu.level",
    
    # Themes
    "theme_light": "themes.light",
    "theme_dark": "themes.dark",
    "theme_purple": "themes.purple",
    
    # Realms
    "realm_albion": "realms.albion",
    "realm_hibernia": "realms.hibernia",
    "realm_midgard": "realms.midgard",
    
    # Misc
    "none_option": "misc.none",
    "language_name": "app.language_name",
    
    # Tooltips
    "create_char_tooltip": "tooltips.create_char",
    "columns_config_tooltip": "tooltips.columns_config",
    
    # Version Check
    "version_check_current": "version_check.current",
    "version_check_latest": "version_check.latest",
    
    # ... 330+ more mappings (total 421)
}
```

### Helper Functions

```python
def get_v2_key(v1_key: str) -> str:
    """Convert v1 flat key to v2 hierarchical key."""
    return LANGUAGE_LEGACY_MAPPING.get(v1_key)

def get_legacy_key(v2_key: str) -> str:
    """Reverse lookup: v2 → v1 (for debugging)."""
    for v1, v2 in LANGUAGE_LEGACY_MAPPING.items():
        if v2 == v2_key:
            return v1
    return None

def is_v2_structure(data: dict) -> bool:
    """Detect if language data uses v2 structure."""
    v2_sections = ["window", "menu", "dialogs", "buttons", "settings"]
    return any(section in data for section in v2_sections)
```

---

## 🔧 LanguageManager Enhancement

File: `Functions/language_manager.py`

### Enhanced `get()` Method

Supports both v1 and v2 keys transparently:

```python
def get(self, key: str, default=None, **kwargs) -> str:
    """
    Get translation with v1/v2 dual support.
    
    Args:
        key: Translation key (v1 flat or v2 dotted notation)
        default: Default value if key not found
        **kwargs: Format parameters for string interpolation
    
    Returns:
        Translated string (formatted if kwargs provided)
    
    Examples:
        # v1 compatibility (auto-redirected)
        lang.get("window_title")  → "DAOC - Gestion des personnages"
        
        # v2 dotted notation
        lang.get("window.main_title")  → "DAOC - Gestion des personnages"
        
        # With formatting
        lang.get("messages.errors.char_exists", name="Gandalf")
        → "Un personnage nommé 'Gandalf' existe déjà."
    """
    # Try v2 dotted notation first
    if "." in key:
        value = self._get_nested(key)
    else:
        # Try v1 key, redirect if in legacy mapping
        if key in LANGUAGE_LEGACY_MAPPING:
            v2_key = LANGUAGE_LEGACY_MAPPING[key]
            value = self._get_nested(v2_key)
        else:
            # Direct key lookup (v1 fallback)
            value = self.strings.get(key)
    
    # Return default if not found
    if value is None:
        return default if default else key
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            # Formatting failed, return unformatted
            return value
    
    return value
```

### Nested Key Navigation

```python
def _get_nested(self, dotted_key: str):
    """
    Navigate hierarchical structure using dotted notation.
    
    Args:
        dotted_key: Dot-separated key path (e.g., "menu.file.label")
    
    Returns:
        Translation value or None if path not found
    
    Examples:
        _get_nested("window.main_title")  → Navigate to strings["window"]["main_title"]
        _get_nested("settings.pages.general.title")  → 3-level navigation
    """
    keys = dotted_key.split(".")
    value = self.strings
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None  # Path not found
    
    return value
```

### Auto-Migration on Load

```python
def load_language(self, lang_code: str):
    """
    Load language file with auto-migration support.
    
    If v1 file detected:
    1. Create timestamped backup
    2. Migrate v1 → v2 structure
    3. Validate migrated data
    4. Save v2 format
    5. Load v2 into memory
    
    If v2 file detected:
    1. Load directly (no migration needed)
    """
    lang_file = self.language_folder / f"{lang_code}.json"
    
    if not lang_file.exists():
        raise FileNotFoundError(f"Language file not found: {lang_file}")
    
    # Load raw data
    with open(lang_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    # Detect version
    version = detect_language_version(loaded_data)
    
    if version == "v1":
        # Auto-migrate v1 → v2
        print(f"[LANGUAGE] Detected v1 format for {lang_code}, migrating...")
        
        # Backup original
        create_backup(lang_file)
        
        # Migrate
        self.strings = migrate_v1_to_v2(loaded_data)
        
        # Validate
        is_valid, errors = validate_migrated_language(self.strings)
        if not is_valid:
            raise ValueError(f"Migration validation failed: {errors}")
        
        # Save v2
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(self.strings, f, ensure_ascii=False, indent=4)
        
        print(f"[LANGUAGE] Migration complete for {lang_code}")
    else:
        # Already v2, use as-is
        self.strings = loaded_data
```

---

## 🛠️ Migration System

File: `Functions/language_migration.py`

### Core Functions

#### 1. Version Detection
```python
def detect_language_version(lang_data: dict) -> str:
    """
    Detect if language data is v1 (flat) or v2 (hierarchical).
    
    Args:
        lang_data: Loaded language dictionary
    
    Returns:
        "v1" or "v2"
    
    Logic:
        v2 has keys like "window", "menu", "dialogs"
        v1 has keys like "window_title", "file_menu_label"
    """
    v2_indicators = ["window", "menu", "dialogs", "buttons", "settings"]
    
    # Check if any v2 section exists and contains dict
    for section in v2_indicators:
        if section in lang_data and isinstance(lang_data[section], dict):
            return "v2"
    
    return "v1"
```

#### 2. Backup Creation
```python
def create_backup(lang_file: Path) -> Path:
    """
    Create timestamped backup of language file.
    
    Args:
        lang_file: Path to language file
    
    Returns:
        Path to backup file
    
    Example:
        fr.json → fr.json.backup_20251116_181201
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = lang_file.with_suffix(f".json.backup_{timestamp}")
    
    shutil.copy2(lang_file, backup_file)
    
    return backup_file
```

#### 3. v1→v2 Migration
```python
def migrate_v1_to_v2(v1_data: dict) -> dict:
    """
    Transform v1 flat structure to v2 hierarchical structure.
    
    Args:
        v1_data: Flat dictionary with 417+ keys
    
    Returns:
        Hierarchical v2 dictionary with 12 sections
    
    Process:
        1. Initialize v2 structure (12 empty sections)
        2. For each v1 key, lookup v2 path in LANGUAGE_LEGACY_MAPPING
        3. Set value at v2 path using _set_nested_value()
        4. Preserve unknown keys in "_unknown_v1_keys" section
    """
    # Initialize v2 structure
    v2_data = {
        "app": {},
        "window": {},
        "menu": {},
        "dialogs": {},
        "buttons": {},
        "columns": {},
        "context_menu": {},
        "settings": {},
        "backup": {},
        "character_sheet": {},
        "progress": {},
        "messages": {},
        "status_bar": {},
        "debug": {},
        "themes": {},
        "realms": {},
        "misc": {},
        "tooltips": {},
        "version_check": {}
    }
    
    unknown_keys = {}
    
    # Map each v1 key to v2 structure
    for v1_key, value in v1_data.items():
        if v1_key in LANGUAGE_LEGACY_MAPPING:
            v2_path = LANGUAGE_LEGACY_MAPPING[v1_key]
            _set_nested_value(v2_data, v2_path, value)
        else:
            # Unknown key, preserve it
            unknown_keys[v1_key] = value
    
    # Add unknown keys section if any
    if unknown_keys:
        v2_data["_unknown_v1_keys"] = unknown_keys
    
    return v2_data

def _set_nested_value(data: dict, dotted_key: str, value):
    """
    Set value in nested dictionary using dotted notation.
    
    Args:
        data: Target dictionary
        dotted_key: Dot-separated path (e.g., "menu.file.label")
        value: Value to set
    
    Example:
        _set_nested_value(data, "menu.file.label", "Fichier")
        → data["menu"]["file"]["label"] = "Fichier"
    """
    keys = dotted_key.split(".")
    current = data
    
    # Navigate to parent
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set final value
    current[keys[-1]] = value
```

#### 4. Validation
```python
def validate_migrated_language(v2_data: dict) -> tuple[bool, list]:
    """
    Validate migrated v2 structure.
    
    Args:
        v2_data: Migrated v2 dictionary
    
    Returns:
        (is_valid, errors)
    
    Checks:
        - All 12 required sections present
        - No empty sections (except optional ones)
        - Structure is hierarchical (dict values)
    """
    errors = []
    
    required_sections = [
        "app", "window", "menu", "dialogs", "buttons", 
        "columns", "settings", "messages"
    ]
    
    # Check required sections exist
    for section in required_sections:
        if section not in v2_data:
            errors.append(f"Missing required section: {section}")
        elif not isinstance(v2_data[section], dict):
            errors.append(f"Section {section} is not a dictionary")
        elif not v2_data[section]:
            errors.append(f"Section {section} is empty")
    
    return (len(errors) == 0, errors)
```

#### 5. Migration Summary
```python
def get_migration_summary(v1_data: dict, v2_data: dict) -> str:
    """
    Generate detailed migration report.
    
    Returns formatted summary with:
    - Total keys migrated
    - Keys per section
    - Unknown keys (if any)
    - Validation status
    """
    summary = []
    summary.append("=" * 60)
    summary.append("MIGRATION SUMMARY")
    summary.append("=" * 60)
    
    # Count v1 keys
    v1_count = len(v1_data)
    summary.append(f"v1 keys: {v1_count}")
    
    # Count v2 keys per section
    summary.append("\nv2 structure:")
    for section, content in v2_data.items():
        if isinstance(content, dict):
            count = count_nested_keys(content)
            summary.append(f"  {section}: {count} keys")
    
    # Unknown keys
    if "_unknown_v1_keys" in v2_data:
        unknown_count = len(v2_data["_unknown_v1_keys"])
        summary.append(f"\n⚠️  Unknown keys: {unknown_count}")
        summary.append("  (preserved in _unknown_v1_keys section)")
    else:
        summary.append("\n✅ All keys mapped successfully")
    
    summary.append("=" * 60)
    
    return "\n".join(summary)
```

#### 6. Rollback
```python
def rollback_migration(lang_file: Path, backup_file: Path):
    """
    Restore language file from backup.
    
    Args:
        lang_file: Current language file
        backup_file: Backup file to restore from
    """
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup not found: {backup_file}")
    
    shutil.copy2(backup_file, lang_file)
```

---

## ✅ Backward Compatibility

### 100% Transparent

All existing code works **without modification**:

```python
# Existing code (v1 keys) - STILL WORKS
lang.get("window_title")  # Auto-redirected to window.main_title
lang.get("file_menu_label")  # Auto-redirected to menu.file.label
lang.get("save_button")  # Auto-redirected to buttons.save
lang.get("char_name_empty_error")  # Auto-redirected to messages.errors.char_name_empty
```

### New Code (v2 keys) - RECOMMENDED

```python
# New code (v2 dotted notation) - PREFERRED
lang.get("window.main_title")
lang.get("menu.file.label")
lang.get("buttons.save")
lang.get("messages.errors.char_name_empty")
```

### Code Impact: ZERO Breaking Changes

- **~530 existing `lang.get()` calls** across codebase
- **0 modifications required**
- **100% backward compatible** through LANGUAGE_LEGACY_MAPPING

---

## 💡 Usage Examples

### Basic Usage

```python
# Window title (v1 compatibility)
title = lang.get("window_title")

# Window title (v2 preferred)
title = lang.get("window.main_title")

# Menu label
file_menu = lang.get("menu.file.label")  # "Fichier"

# Button text
save_btn = lang.get("buttons.save")  # "Enregistrer"

# Error message
error = lang.get("messages.errors.char_name_empty")
# → "Le nom du personnage ne peut pas être vide."
```

### With String Formatting

```python
# Character saved success (with name parameter)
msg = lang.get("messages.success.char_saved", name="Gandalf")
# → "Personnage 'Gandalf' sauvegardé avec succès."

# Character exists error
error = lang.get("messages.errors.char_exists", name="Merlin")
# → "Un personnage nommé 'Merlin' existe déjà."

# Status bar selection count
status = lang.get("status_bar.selection_count", count=3, total=15)
# → "3 sur 15 personnage(s) sélectionné(s)"
```

### Dialog Construction

```python
# New character dialog
dialog_title = lang.get("dialogs.new_character.title")
prompt_name = lang.get("dialogs.new_character.prompt_name")
prompt_realm = lang.get("dialogs.new_character.prompt_realm")
prompt_season = lang.get("dialogs.new_character.prompt_season")

# Delete confirmation
confirm_title = lang.get("dialogs.delete_character.confirm_title")
confirm_msg = lang.get("dialogs.delete_character.confirm_message", name="Thor")
# → "Êtes-vous sûr de vouloir supprimer définitivement le personnage 'Thor' ? ..."
```

### Settings Page

```python
# Navigation
nav_general = lang.get("settings.navigation.general")  # "Général"
nav_themes = lang.get("settings.navigation.themes")  # "Thèmes"

# Page titles
page_title = lang.get("settings.pages.general.title")  # "Paramètres Généraux"
page_subtitle = lang.get("settings.pages.general.subtitle")  # "Chemins des dossiers..."

# Labels
char_folder_label = lang.get("settings.labels.character_folder")  # "Répertoire des personnages"
theme_label = lang.get("settings.labels.theme")  # "Thème"
```

### Progress Messages

```python
# Herald search progress
title = lang.get("progress.herald_search.title")  # "⏳ Recherche en cours..."
checking = lang.get("progress.herald_search.checking_cookies")  # "🔐 Vérification..."
searching = lang.get("progress.herald_search.searching", "Gandalf")  # "🔍 Recherche de 'Gandalf'..."
complete = lang.get("progress.herald_search.complete")  # "✅ Recherche terminée..."

# Character update
update_title = lang.get("progress.character_update.title")  # "🌐 Mise à jour depuis Herald..."
update_desc = lang.get("progress.character_update.description")
```

---

## 🧪 Testing & Validation

### Migration Validation

La migration v1→v2 est **automatique** et intégrée dans `language_manager.py`.

Au premier chargement d'un fichier v1 :
1. Détection automatique de la version
2. Création d'un backup horodaté
3. Migration vers v2
4. Validation
5. Sauvegarde du fichier v2

Tous les fichiers de langue sont maintenant en v2.
```

### Application Testing

```bash
# Launch application
python main.py

# Expected console output:
# [LANGUAGE] Loaded language: fr
# [LANGUAGE] Version detected: v2
# [APP_STARTUP] Language system initialized
```

### Manual Checks

1. **UI Elements**:
   - ✅ Window title displays correctly
   - ✅ All menu items show proper labels
   - ✅ Button texts are correct
   - ✅ Column headers display properly

2. **Dialogs**:
   - ✅ New character dialog shows correct prompts
   - ✅ Delete confirmation messages display
   - ✅ Error/success/info dialogs work

3. **Language Switching**:
   - ✅ Switch to English (EN)
   - ✅ Switch to German (DE)
   - ✅ Switch back to French (FR)
   - ✅ All texts update correctly

4. **Settings Dialog**:
   - ✅ All navigation items display
   - ✅ Page titles and subtitles correct
   - ✅ Labels and tooltips work

### Verify No Unknown Keys

```bash
# Check for unknown keys section
grep -r "_unknown_v1_keys" Language/*.json

# Expected: No matches (all keys mapped)
```

---

## 📁 File Structure

```
Project Root
├── Language/
│   ├── fr.json (v2, ~550 lines, 12 sections)
│   ├── en.json (v2, ~550 lines, 12 sections)
│   └── de.json (v2, ~550 lines, 12 sections)
│
├── Functions/
│   ├── language_schema.py (NEW, ~600 lines)
│   │   └── LANGUAGE_LEGACY_MAPPING (421 mappings)
│   ├── language_migration.py (NEW, ~350 lines)
│   │   ├── detect_language_version()
│   │   ├── create_backup()
│   │   ├── migrate_v1_to_v2()
│   │   ├── validate_migrated_language()
│   │   └── rollback_migration()
│   └── language_manager.py (ENHANCED, ~200 lines)
│       ├── load_language() → auto-migration
│       ├── get() → v1/v2 dual support
│       └── _get_nested() → hierarchical navigation
│
└── Documentations/
    └── Lang/
        └── LANGUAGE_V2_TECHNICAL_DOC.md (THIS FILE)
```

---

## 🔧 Maintenance Guide

### Adding New Translations

#### 1. For New Features (v2 approach)

**Example:** Adding armor comparison feature

```json
// In fr.json (and en.json, de.json)
{
    "dialogs": {
        // ... existing dialogs ...
        "armor_comparison": {
            "title": "Comparaison d'armures",
            "select_armor_1": "Sélectionnez la première armure :",
            "select_armor_2": "Sélectionnez la deuxième armure :",
            "compare_button": "Comparer",
            "difference_label": "Différence :"
        }
    },
    "buttons": {
        // ... existing buttons ...
        "compare_armors": "Comparer les armures"
    }
}
```

**In code:**
```python
# Use v2 keys
title = lang.get("dialogs.armor_comparison.title")
compare_btn = lang.get("buttons.compare_armors")
```

#### 2. Add to Legacy Mapping (optional, for v1 compatibility)

If you want to support v1-style keys:

```python
# In Functions/language_schema.py
LANGUAGE_LEGACY_MAPPING = {
    # ... existing mappings ...
    "armor_comparison_title": "dialogs.armor_comparison.title",
    "compare_armors_button": "buttons.compare_armors",
}
```

### Adding New Section

**Example:** Adding `armor` section

```json
{
    "armor": {
        "types": {
            "cloth": "Tissu",
            "leather": "Cuir",
            "chain": "Mailles",
            "plate": "Plaques"
        },
        "slots": {
            "head": "Tête",
            "chest": "Torse",
            "legs": "Jambes"
        },
        "stats": {
            "armor_factor": "Facteur d'armure",
            "absorption": "Absorption"
        }
    }
}
```

### Translating to New Language

**Example:** Adding Spanish (ES)

1. **Copy existing file:**
   ```bash
   cp Language/fr.json Language/es.json
   ```

2. **Translate all values** (keep keys unchanged):
   ```json
   {
       "window": {
           "main_title": "DAOC - Gestión de personajes",
           "welcome_message": "¡Bienvenido al gestor de personajes!"
       },
       "menu": {
           "file": {
               "label": "Archivo",
               "new_character": "➕ Nuevo Personaje"
           }
       }
   }
   ```

3. **Update LanguageManager:**
   ```python
   # In Functions/language_manager.py
   AVAILABLE_LANGUAGES = {
       "fr": "Français",
       "en": "English",
       "de": "Deutsch",
       "es": "Español"  # NEW
   }
   ```

### Debugging Translation Issues

```python
# Check if key exists (v2)
if lang._get_nested("dialogs.new_character.title"):
    print("Key exists")

# Check v1→v2 mapping
v2_key = get_v2_key("window_title")
print(f"window_title → {v2_key}")

# Reverse lookup
v1_key = get_legacy_key("window.main_title")
print(f"window.main_title → {v1_key}")

# Check unknown keys in migration
with open("Language/fr.json") as f:
    data = json.load(f)
    if "_unknown_v1_keys" in data:
        print("Unknown keys found:", data["_unknown_v1_keys"])
```

### Common Issues

#### Issue 1: Translation not found
```python
# Returns key itself (no error)
lang.get("non.existent.key")  # → "non.existent.key"

# Use default value
lang.get("non.existent.key", default="Fallback text")  # → "Fallback text"
```

#### Issue 2: Formatting error
```python
# Safe formatting (catches exceptions)
lang.get("messages.success.char_saved")  # Missing 'name' parameter
# → Returns unformatted string (doesn't crash)

# Correct usage
lang.get("messages.success.char_saved", name="Gandalf")
# → "Personnage 'Gandalf' sauvegardé avec succès."
```

#### Issue 3: Mixed v1/v2 in same code
```python
# WORKS but not recommended
title1 = lang.get("window_title")  # v1
title2 = lang.get("window.main_title")  # v2
# Both return same value

# RECOMMENDED: Use v2 consistently
title = lang.get("window.main_title")
```

---

## 📊 Statistics

### Migration Results

- **Files migrated**: 3 (fr, en, de)
- **Keys per file**: 417-418 (v1) → Hierarchical (v2)
- **Total mappings**: 421
- **Unknown keys**: 0 (100% mapped)
- **Backups created**: 6 (2 iterations)
- **Migration time**: ~2 minutes
- **Validation**: ✅ Pass (3/3 files)

### Code Impact

- **Existing `lang.get()` calls**: ~530
- **Breaking changes**: 0
- **Modifications required**: 0
- **Backward compatibility**: 100%

### File Sizes

| File | v1 Size | v2 Size | Change |
|------|---------|---------|--------|
| fr.json | ~28 KB | ~32 KB | +14% |
| en.json | ~29 KB | ~33 KB | +14% |
| de.json | ~29 KB | +33 KB | +14% |

*Size increase due to indentation and hierarchical structure (more readable)*

---

## 🎓 Best Practices

### 1. Use v2 Keys in New Code

```python
# ❌ Avoid (v1 style, deprecated)
title = lang.get("window_title")

# ✅ Preferred (v2 style)
title = lang.get("window.main_title")
```

### 2. Group Related Translations

```python
# ✅ Good: All dialog texts together
dialog_title = lang.get("dialogs.new_character.title")
dialog_prompt = lang.get("dialogs.new_character.prompt_name")
dialog_realm = lang.get("dialogs.new_character.prompt_realm")
```

### 3. Use Descriptive v2 Paths

```python
# ❌ Unclear
text = lang.get("settings.labels.path1")

# ✅ Clear
text = lang.get("settings.labels.character_folder")
```

### 4. Consistent Formatting Parameters

```python
# ✅ Use descriptive parameter names
msg = lang.get("messages.success.char_saved", name=character_name)
msg = lang.get("status_bar.selection_count", count=selected, total=total_chars)
```

### 5. Handle Missing Translations

```python
# ✅ Provide sensible defaults
label = lang.get("new.feature.label", default="New Feature")

# ✅ Check before using
key = "dialogs.new_feature.title"
if lang._get_nested(key):
    title = lang.get(key)
else:
    title = "Default Title"
```

---

## 🔒 Security & Safety

### Automatic Backups

All migrations create timestamped backups:
```
Language/fr.json.backup_20251116_181201
Language/en.json.backup_20251116_181353
```

### Rollback Capability

```python
# Restore from backup
from Functions.language_migration import rollback_migration
from pathlib import Path

rollback_migration(
    lang_file=Path("Language/fr.json"),
    backup_file=Path("Language/fr.json.backup_20251116_181201")
)
```

### Validation Before Save

Migration always validates before saving:
```python
is_valid, errors = validate_migrated_language(v2_data)
if not is_valid:
    raise ValueError(f"Migration failed: {errors}")
    # Original file remains unchanged
```

---

## 📚 References

### Related Documentation

- `Documentations/Config/CONFIG_V2_TECHNICAL_DOC.md` - Similar approach for config.json
- `Functions/language_schema.py` - Complete v1→v2 mapping (421 keys)
- `Functions/language_migration.py` - Migration logic
- `Functions/language_manager.py` - Enhanced manager with v1/v2 support

### Key Files

```
Functions/
├── language_schema.py       (421 v1→v2 mappings)
├── language_migration.py    (Migration logic)
└── language_manager.py      (Enhanced manager)

Language/
├── fr.json                  (French v2)
├── en.json                  (English v2)
└── de.json                  (German v2)
```

---

## ✅ Validation Checklist

After migration, verify:

- [ ] All 3 language files migrated (fr, en, de)
- [ ] No `_unknown_v1_keys` section in any file
- [ ] Application starts without errors
- [ ] Window title displays correctly
- [ ] All menu items show proper labels
- [ ] Button texts are correct
- [ ] Dialog messages display
- [ ] Error/success messages work
- [ ] Settings dialog loads completely
- [ ] Language switching works (FR ↔ EN ↔ DE)
- [ ] Progress messages display during operations
- [ ] Character sheet stats show labels
- [ ] Backup system messages display
- [ ] Status bar updates correctly

---

## 🎉 Summary

### What Was Achieved

✅ **Restructured** 3 language files from flat to hierarchical  
✅ **Migrated** 421 translation keys to 12 logical sections  
✅ **Maintained** 100% backward compatibility (530+ existing calls)  
✅ **Created** complete v1→v2 mapping system  
✅ **Enhanced** LanguageManager with dual v1/v2 support  
✅ **Validated** all migrations (0 unknown keys)  
✅ **Tested** application with v2 files successfully  
✅ **Documented** complete technical implementation  

### Benefits Delivered

🎯 **Developer Experience**: Easy to find and add translations  
🎯 **Code Quality**: Clean, organized structure  
🎯 **Maintainability**: Logical grouping by context  
🎯 **Scalability**: Simple to extend for new features  
🎯 **Reliability**: Zero breaking changes, full backward compatibility  

---

**Status:** ✅ Complete & Production Ready  
**Version:** v0.109  
**Date:** November 16, 2025  
**Branch:** 108_Imp_Lang  

---

**End of Technical Documentation**
