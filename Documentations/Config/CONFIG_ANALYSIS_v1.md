# 📊 Analyse du Code Actuel - config.json

**Date :** 15 novembre 2024  
**Version :** v0.108  
**Phase :** 1 - Préparation

---

## 🔍 Analyse de config_manager.py

### Structure Actuelle

**Fichier :** `Functions/config_manager.py`  
**Lignes :** ~85 lignes  
**Complexité :** 🟢 Simple (dict plat)

### Méthodes Principales

```python
class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Charge depuis config.json ou crée avec valeurs par défaut"""
    
    def save_config(self):
        """Sauvegarde dans config.json avec indent=4"""
        # ✅ Utilise json.dump() sans sort_keys → Ordre préservé
    
    def get(self, key, default=None):
        """Récupère une valeur"""
        # ⚠️ Accès simple : self.config.get(key)
    
    def set(self, key, value):
        """Définit et sauvegarde immédiatement"""
        # ⚠️ Save automatique à chaque set()
```

### Singleton Pattern

```python
class SingletonConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

# Instance globale
config = SingletonConfig()
```

**✅ Bon point :** Pattern singleton bien implémenté

---

## 📋 Inventaire Complet des Clés

### 1. Interface Utilisateur (UI)

| Clé Actuelle | Type | Défaut | Usage | Fichiers |
|--------------|------|--------|-------|----------|
| `language` | str | `"fr"` | Langue interface | main.py (8×), UI/*.py |
| `theme` | str | `"default"` | Thème visuel | main.py (3×) |
| `font_scale` | float | `1.0` | Échelle police | main.py (3×) |
| `column_widths` | dict | `{}` | Largeurs colonnes | tree_manager.py |
| `column_visibility` | dict | `{}` | Colonnes visibles | main.py (2×) |
| `tree_view_header_state` | str | `None` | État header | tree_manager.py |
| `manual_column_resize` | bool | `True` | Mode resize | main.py (2×) |

**Total :** 7 clés UI

### 2. Dossiers (Folders)

| Clé Actuelle | Type | Défaut | Usage | Fichiers |
|--------------|------|--------|-------|----------|
| `character_folder` | str | `None` | Dossier personnages | main.py (4×), settings_dialog.py (4×) |
| `log_folder` | str | `None` | Dossier logs | main.py (2×), settings_dialog.py (3×) |
| `armor_folder` | str | `None` | Dossier armures | main.py (2×), settings_dialog.py (3×) |
| `cookies_folder` | str | `None` | Dossier cookies | main.py (2×), settings_dialog.py (1×) |

**Total :** 4 clés Folders

### 3. Sauvegarde (Backup)

| Clé Actuelle | Type | Défaut | Usage | Fichiers |
|--------------|------|--------|-------|----------|
| `backup_enabled` | bool | `True` | Activer backup | main.py (2×) |
| `backup_path` | str | `None` | Chemin backup | main.py (2×), settings_dialog.py (4×) |
| `backup_compress` | bool | `True` | Compression ZIP | main.py (2×) |
| `backup_size_limit_mb` | int | `20` | Limite taille | main.py (2×) |
| `backup_auto_delete_old` | bool | `False` | Auto-suppression | main.py (2×) |
| `backup_last_date` | str | `None` | Dernière sauvegarde | backup_manager.py |
| `cookies_backup_enabled` | bool | `True` | Backup cookies | main.py (2×) |
| `cookies_backup_path` | str | `None` | Chemin cookies | main.py (2×), settings_dialog.py (3×) |
| `cookies_backup_compress` | bool | `True` | Compression cookies | main.py (2×) |
| `cookies_backup_size_limit_mb` | int | `5` | Limite cookies | main.py (2×) |
| `cookies_backup_auto_delete_old` | bool | `False` | Auto-suppr cookies | main.py (2×) |
| `armor_backup_enabled` | bool | `True` | Backup armures | main.py (2×) |
| `armor_backup_path` | str | `None` | Chemin armures | main.py (2×), settings_dialog.py (3×) |
| `armor_backup_compress` | bool | `True` | Compression armures | main.py (2×) |
| `armor_backup_size_limit_mb` | int | `5` | Limite armures | main.py (2×) |
| `armor_backup_auto_delete_old` | bool | `False` | Auto-suppr armures | main.py (2×) |

**Total :** 16 clés Backup

### 4. Système (System)

| Clé Actuelle | Type | Défaut | Usage | Fichiers |
|--------------|------|--------|-------|----------|
| `debug_mode` | bool | `False` | Mode debug | main.py (2×) |
| `show_debug_window` | bool | `False` | Fenêtre debug | main.py (2×) |
| `disable_disclaimer` | bool | `False` | Désactiver disclaimer | main.py (2×) |
| `preferred_browser` | str | `"Chrome"` | Navigateur préféré | main.py (2×) |
| `allow_browser_download` | bool | `False` | Autoriser téléchargement | main.py (2×) |

**Total :** 5 clés System

### 5. Jeu (Game)

| Clé Actuelle | Type | Défaut | Usage | Fichiers |
|--------------|------|--------|-------|----------|
| `servers` | list | `["Eden"]` | Serveurs disponibles | main.py (3×) |
| `default_server` | str | `"Eden"` | Serveur par défaut | main.py (2×) |
| `seasons` | list | `["S3"]` | Saisons disponibles | main.py (3×) |
| `default_season` | str | `"S3"` | Saison par défaut | main.py (2×) |
| `default_realm` | str | `None` | Royaume par défaut | main.py (2×) |

**Total :** 5 clés Game

---

## 📈 Statistiques Globales

**Total clés config :** 37 clés  
**Fichiers utilisant config :**
- `main.py` : 94 appels `config.set()`, 50+ appels `config.get()`
- `UI/settings_dialog.py` : 12 appels `config.set()`, 20+ appels `config.get()`
- `Functions/tree_manager.py` : 2 appels `config.set()`
- `Functions/backup_manager.py` : Plusieurs appels `config.get()`

**Répartition des clés :**
- 🎨 UI : 7 clés (19%)
- 📁 Folders : 4 clés (11%)
- 💾 Backup : 16 clés (43%)
- ⚙️ System : 5 clés (14%)
- 🎮 Game : 5 clés (13%)

---

## 🎯 Mapping v1 → v2

### Nouvelle Structure Proposée

```json
{
  "ui": {
    "language": "fr",
    "theme": "default",
    "font_scale": 1.0,
    "column_widths": {},
    "column_visibility": {},
    "tree_view_header_state": null,
    "manual_column_resize": true
  },
  "folders": {
    "characters": null,
    "logs": null,
    "armor": null,
    "cookies": null
  },
  "backup": {
    "characters": {
      "enabled": true,
      "path": null,
      "compress": true,
      "size_limit_mb": 20,
      "auto_delete_old": false,
      "last_date": null
    },
    "cookies": {
      "enabled": true,
      "path": null,
      "compress": true,
      "size_limit_mb": 5,
      "auto_delete_old": false
    },
    "armor": {
      "enabled": true,
      "path": null,
      "compress": true,
      "size_limit_mb": 5,
      "auto_delete_old": false
    }
  },
  "system": {
    "debug_mode": false,
    "show_debug_window": false,
    "disable_disclaimer": false,
    "preferred_browser": "Chrome",
    "allow_browser_download": false
  },
  "game": {
    "servers": ["Eden"],
    "default_server": "Eden",
    "seasons": ["S3"],
    "default_season": "S3",
    "default_realm": null
  }
}
```

### Table de Conversion

| Ancienne Clé v1 | Nouvelle Clé v2 | Section |
|----------------|----------------|---------|
| `language` | `ui.language` | UI |
| `theme` | `ui.theme` | UI |
| `font_scale` | `ui.font_scale` | UI |
| `column_widths` | `ui.column_widths` | UI |
| `column_visibility` | `ui.column_visibility` | UI |
| `tree_view_header_state` | `ui.tree_view_header_state` | UI |
| `manual_column_resize` | `ui.manual_column_resize` | UI |
| `character_folder` | `folders.characters` | Folders |
| `log_folder` | `folders.logs` | Folders |
| `armor_folder` | `folders.armor` | Folders |
| `cookies_folder` | `folders.cookies` | Folders |
| `backup_enabled` | `backup.characters.enabled` | Backup |
| `backup_path` | `backup.characters.path` | Backup |
| `backup_compress` | `backup.characters.compress` | Backup |
| `backup_size_limit_mb` | `backup.characters.size_limit_mb` | Backup |
| `backup_auto_delete_old` | `backup.characters.auto_delete_old` | Backup |
| `backup_last_date` | `backup.characters.last_date` | Backup |
| `cookies_backup_enabled` | `backup.cookies.enabled` | Backup |
| `cookies_backup_path` | `backup.cookies.path` | Backup |
| `cookies_backup_compress` | `backup.cookies.compress` | Backup |
| `cookies_backup_size_limit_mb` | `backup.cookies.size_limit_mb` | Backup |
| `cookies_backup_auto_delete_old` | `backup.cookies.auto_delete_old` | Backup |
| `armor_backup_enabled` | `backup.armor.enabled` | Backup |
| `armor_backup_path` | `backup.armor.path` | Backup |
| `armor_backup_compress` | `backup.armor.compress` | Backup |
| `armor_backup_size_limit_mb` | `backup.armor.size_limit_mb` | Backup |
| `armor_backup_auto_delete_old` | `backup.armor.auto_delete_old` | Backup |
| `debug_mode` | `system.debug_mode` | System |
| `show_debug_window` | `system.show_debug_window` | System |
| `disable_disclaimer` | `system.disable_disclaimer` | System |
| `preferred_browser` | `system.preferred_browser` | System |
| `allow_browser_download` | `system.allow_browser_download` | System |
| `servers` | `game.servers` | Game |
| `default_server` | `game.default_server` | Game |
| `seasons` | `game.seasons` | Game |
| `default_season` | `game.default_season` | Game |
| `default_realm` | `game.default_realm` | Game |

---

## 🔧 Points Critiques Identifiés

### 1. ⚠️ Sauvegarde Automatique dans `set()`

```python
def set(self, key, value):
    """Sets a value in the configuration and saves the file."""
    self.config[key] = value
    self.save_config()  # ← Sauvegarde à CHAQUE modification
```

**Impact :**
- ✅ Bon : Aucune donnée perdue
- ⚠️ Problème : Performance (I/O disque à chaque set)
- ⚠️ Problème : Modifications multiples = multiples écritures

**Recommandation v2 :**
```python
def set(self, key, value, save=True):
    """Sets a value, optionally saves"""
    # Support notation pointée
    if "." in key:
        section, subkey = key.split(".", 1)
        if section not in self.config:
            self.config[section] = {}
        self.config[section][subkey] = value
    else:
        self.config[key] = value
    
    if save:
        self.save_config()
```

### 2. ⚠️ Valeurs par Défaut Hardcodées

```python
self.config = {
    "character_folder": None,
    "debug_mode": False,
    # ... 15+ clés hardcodées
}
```

**Problème :**
- Maintenabilité difficile
- Duplication avec schéma de validation
- Pas de documentation des valeurs

**Recommandation v2 :**
```python
from .config_schema import DEFAULT_CONFIG

self.config = DEFAULT_CONFIG.copy()
```

### 3. ✅ Ordre Préservé

```python
json.dump(self.config, f, indent=4)
# ✅ Pas de sort_keys=True → Ordre préservé
```

**Bon point :** Déjà compatible avec structure v2

### 4. ⚠️ Pas de Validation

Aucune validation des valeurs :
- Langue invalide acceptée
- Thème inexistant accepté
- Chemins invalides acceptés

**Recommandation v2 :**
```python
from .config_schema import validate_value

def set(self, key, value, save=True):
    if not validate_value(key, value):
        raise ValueError(f"Invalid value for {key}: {value}")
    # ...
```

---

## 📦 Dépendances Identifiées

### Imports Actuels

```python
import json  # ✅ Natif Python
import os    # ✅ Natif Python
import sys   # ✅ Natif Python
```

**✅ Aucune dépendance externe** - Parfait !

### Imports Nécessaires v2

```python
import json
import os
import sys
from typing import Any, Dict, Optional  # Type hints
```

**Aucune nouvelle dépendance** nécessaire

---

## 🎯 Fichiers à Modifier (Phase 4)

### Priorité 1 - Core

1. **`Functions/config_manager.py`** (⭐⭐⭐⭐⭐)
   - Ajouter support notation pointée
   - Implémenter migration v1→v2
   - Ajouter validation
   - Lignes à modifier : ~50

2. **`main.py`** (⭐⭐⭐⭐⭐)
   - 94 `config.set()` à adapter
   - 50+ `config.get()` à adapter
   - Lignes à modifier : ~150

3. **`UI/settings_dialog.py`** (⭐⭐⭐⭐⭐)
   - 12 `config.set()` à adapter
   - 20+ `config.get()` à adapter
   - Lignes à modifier : ~40

### Priorité 2 - Modules

4. **`Functions/tree_manager.py`** (⭐⭐⭐☆☆)
   - 2 `config.set()` pour colonnes
   - Lignes à modifier : ~5

5. **`Functions/backup_manager.py`** (⭐⭐⭐☆☆)
   - Plusieurs `config.get()` pour backup
   - Lignes à modifier : ~10

### Priorité 3 - Nouveaux Fichiers

6. **`Functions/config_schema.py`** (⭐⭐⭐⭐☆) - NOUVEAU
   - Définir schéma de validation
   - Valeurs par défaut
   - ~150 lignes

7. **`Tests/test_config_migration.py`** (⭐⭐⭐⭐☆) - NOUVEAU
   - Tests unitaires migration
   - Tests validation
   - ~200 lignes

---

## 📊 Estimation Détaillée

### Temps par Fichier

| Fichier | Lignes à Modifier | Complexité | Temps Estimé |
|---------|------------------|------------|--------------|
| config_manager.py | ~50 | 🟡 Moyenne | 2h |
| config_schema.py | ~150 (nouveau) | 🟢 Facile | 1h |
| main.py | ~150 | 🟠 Difficile | 3h |
| settings_dialog.py | ~40 | 🟡 Moyenne | 1h |
| tree_manager.py | ~5 | 🟢 Facile | 15min |
| backup_manager.py | ~10 | 🟢 Facile | 30min |
| test_config_migration.py | ~200 (nouveau) | 🟡 Moyenne | 2h |
| Documentation | - | 🟢 Facile | 1h |

**Total Développement :** 10h 45min  
**Buffer (tests, debug) :** +2h  
**TOTAL :** ~12-13h

---

## ✅ Checklist Phase 1 (Analyse)

- [x] **1.1** Analyser `config_manager.py` actuel
- [x] **1.2** Documenter toutes les clés actuelles (37 clés)
- [x] **1.3** Identifier tous les fichiers utilisant config
- [x] **1.4** Compter les occurrences `config.get()` et `config.set()`
- [x] **1.5** Créer table de conversion v1 → v2
- [x] **1.6** Identifier points critiques (4 identifiés)
- [x] **1.7** Estimer temps de développement (12-13h)

---

## 🚀 Prochaines Étapes

### Phase 2 : Migration Auto

**Fichiers à créer :**

1. **`Functions/config_schema.py`**
   - Définir `DEFAULT_CONFIG` v2
   - Définir `VALIDATION_SCHEMA`
   - Fonctions de validation

2. **`Functions/config_migration.py`**
   - Fonction `migrate_v1_to_v2()`
   - Fonction `detect_version()`
   - Backup automatique

3. **Modifier `Functions/config_manager.py`**
   - Intégrer migration au `load_config()`
   - Support notation pointée dans `get()`/`set()`

**Temps estimé Phase 2 :** 3h

---

## 📝 Notes

- Structure v2 proposée : 5 sections (ui, folders, backup, system, game)
- Backup subdivisé par type (characters, cookies, armor)
- Rétrocompatibilité totale via migration auto
- Aucune action utilisateur requise
- Tests exhaustifs nécessaires avant merge

---

**Analyse complétée le :** 15 novembre 2024  
**Prochaine phase :** Phase 2 - Migration Auto  
**Statut :** ✅ Phase 1 Terminée
