# Configuration v2 - Documentation Technique
**Version:** v0.108  
**Date:** 16 novembre 2025  
**Auteur:** Christophe Pelichet

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Structure de la configuration](#structure-de-la-configuration)
4. [Système de migration](#système-de-migration)
5. [API du ConfigManager](#api-du-configmanager)
6. [Rétrocompatibilité](#rétrocompatibilité)
7. [Validation](#validation)
8. [Guide d'utilisation](#guide-dutilisation)
9. [Maintenance](#maintenance)

---

## Vue d'ensemble

### Objectifs

La configuration v2 introduit une **structure hiérarchique** pour améliorer :

- ✅ **Organisation** : Regroupement logique par catégories (ui, folders, backup, system, game)
- ✅ **Lisibilité** : Structure JSON claire et auto-documentée
- ✅ **Maintenabilité** : Facilite l'ajout de nouvelles options
- ✅ **Extensibilité** : Support natif des sous-sections (ex: backup.characters, backup.cookies)
- ✅ **Sécurité** : Migration automatique avec backup et validation

### Changements majeurs

| Aspect | v1 (Ancienne) | v2 (Nouvelle) |
|--------|---------------|---------------|
| **Structure** | Plate (37 clés au root) | Hiérarchique (5 sections) |
| **Accès** | `config.get("language")` | `config.get("ui.language")` |
| **Organisation** | Aucune | Logique par domaine |
| **Validation** | Manuelle | Automatique avec schéma |
| **Migration** | Manuelle | Automatique avec backup |
| **Backup settings** | 1 section unique | 3 sous-sections (characters/cookies/armor) |
| **Compatibilité** | N/A | 100% rétrocompatible avec v1 |

---

## Architecture

### Composants

```
Functions/
├── config_schema.py       # Définition de la structure v2
├── config_migration.py    # Logique de migration v1→v2
└── config_manager.py      # Gestionnaire principal (modifié)

Configuration/
└── config.json            # Fichier de configuration
```

### Flux de données

```
┌─────────────────────────────────────────────────────────────┐
│                    Application démarre                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│            ConfigManager.load_config()                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│         detect_config_version(config_data)                   │
│         • v1 détecté si pas de sections "ui", "folders"      │
│         • v2 détecté si sections présentes                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
         ┌────────────────┐    ┌────────────────┐
         │   Version v1   │    │   Version v2   │
         └────────┬───────┘    └────────┬───────┘
                  │                     │
                  ▼                     │
    ┌─────────────────────────┐        │
    │ create_backup()          │        │
    │ → config.json.backup_... │        │
    └────────┬────────────────┘        │
             │                          │
             ▼                          │
    ┌─────────────────────────┐        │
    │ migrate_v1_to_v2()       │        │
    │ • Transform structure    │        │
    │ • Map 39 legacy keys     │        │
    └────────┬────────────────┘        │
             │                          │
             ▼                          │
    ┌─────────────────────────┐        │
    │ validate_migrated_config()│       │
    │ • Check sections         │        │
    │ • Verify keys            │        │
    └────────┬────────────────┘        │
             │                          │
             ▼                          │
    ┌─────────────────────────┐        │
    │ save_config()            │        │
    │ → Write v2 to disk       │        │
    └────────┬────────────────┘        │
             │                          │
             └──────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Config v2 chargée en RAM   │
         │   Application peut démarrer  │
         └──────────────────────────────┘
```

---

## Structure de la configuration

### config_schema.py

#### DEFAULT_CONFIG

Structure complète de la configuration v2 :

```python
DEFAULT_CONFIG = {
    "ui": {
        "language": "en",                    # Langue de l'interface
        "theme": "purple",                   # Thème visuel
        "font_scale": 1.0,                   # Échelle de police
        "column_widths": {},                 # Largeurs des colonnes
        "column_visibility": {},             # Visibilité des colonnes
        "tree_view_header_state": None,      # État de l'en-tête TreeView
        "manual_column_resize": True         # Redimensionnement manuel
    },
    "folders": {
        "characters": None,                  # Dossier des personnages
        "logs": None,                        # Dossier des logs
        "armor": None,                       # Dossier des armures
        "cookies": None                      # Dossier des cookies
    },
    "backup": {
        "characters": {
            "auto_daily_backup": True,       # Backup auto quotidien
            "path": None,                    # Chemin de sauvegarde
            "compress": True,                # Compression ZIP
            "size_limit_mb": 10,             # Limite de taille (MB)
            "auto_delete_old": True,         # Suppr. anciennes backups
            "last_date": None                # Date dernière backup
        },
        "cookies": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        },
        "armor": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        }
    },
    "system": {
        "debug_mode": False,                 # Mode debug
        "show_debug_window": False,          # Fenêtre debug
        "disable_disclaimer": False,         # Désactiver avertissement
        "preferred_browser": "Chrome",       # Navigateur préféré
        "allow_browser_download": False      # Autoriser téléchargement
    },
    "game": {
        "servers": ["Eden"],                 # Serveurs de jeu
        "default_server": "Eden",            # Serveur par défaut
        "seasons": ["S3"],                   # Saisons disponibles
        "default_season": "S3",              # Saison par défaut
        "default_realm": None                # Royaume par défaut
    }
}
```

#### VALIDATION_SCHEMA

Règles de validation pour chaque clé :

```python
VALIDATION_SCHEMA = {
    "ui": {
        "language": {
            "type": str,
            "allowed": ["fr", "en", "de"],
            "default": "en"
        },
        "theme": {
            "type": str,
            "allowed": ["default", "dark", "light", "purple"],
            "default": "purple"
        },
        "font_scale": {
            "type": (int, float),
            "min": 0.5,
            "max": 2.0,
            "default": 1.0
        },
        # ... autres règles UI
    },
    # ... autres sections
}
```

**Types de validation supportés :**

- `type` : Type(s) attendu(s) - ex: `str`, `bool`, `int`, `(str, type(None))`
- `allowed` : Liste de valeurs autorisées
- `min` / `max` : Valeurs min/max pour les nombres
- `default` : Valeur par défaut

#### LEGACY_KEY_MAPPING

Mapping complet v1 → v2 (39 clés) :

```python
LEGACY_KEY_MAPPING = {
    # UI keys
    "language": "ui.language",
    "theme": "ui.theme",
    "font_scale": "ui.font_scale",
    "column_widths": "ui.column_widths",
    "column_visibility": "ui.column_visibility",
    "tree_view_header_state": "ui.tree_view_header_state",
    "manual_column_resize": "ui.manual_column_resize",
    
    # Folders keys
    "character_folder": "folders.characters",
    "log_folder": "folders.logs",
    "armor_folder": "folders.armor",
    "cookies_folder": "folders.cookies",
    
    # Backup - Characters
    "backup_enabled": "backup.characters.auto_daily_backup",
    "backup_path": "backup.characters.path",
    "backup_compress": "backup.characters.compress",
    "backup_size_limit_mb": "backup.characters.size_limit_mb",
    "backup_auto_delete_old": "backup.characters.auto_delete_old",
    "backup_last_date": "backup.characters.last_date",
    
    # Backup - Cookies
    "cookies_backup_enabled": "backup.cookies.auto_daily_backup",
    "cookies_backup_path": "backup.cookies.path",
    "cookies_backup_compress": "backup.cookies.compress",
    "cookies_backup_size_limit_mb": "backup.cookies.size_limit_mb",
    "cookies_backup_auto_delete_old": "backup.cookies.auto_delete_old",
    "cookies_backup_last_date": "backup.cookies.last_date",
    
    # Backup - Armor
    "armor_backup_enabled": "backup.armor.auto_daily_backup",
    "armor_backup_path": "backup.armor.path",
    "armor_backup_compress": "backup.armor.compress",
    "armor_backup_size_limit_mb": "backup.armor.size_limit_mb",
    "armor_backup_auto_delete_old": "backup.armor.auto_delete_old",
    "armor_backup_last_date": "backup.armor.last_date",
    
    # System keys
    "debug_mode": "system.debug_mode",
    "show_debug_window": "system.show_debug_window",
    "disable_disclaimer": "system.disable_disclaimer",
    "preferred_browser": "system.preferred_browser",
    "allow_browser_download": "system.allow_browser_download",
    
    # Game keys
    "servers": "game.servers",
    "default_server": "game.default_server",
    "seasons": "game.seasons",
    "default_season": "game.default_season",
    "default_realm": "game.default_realm"
}
```

---

## Système de migration

### config_migration.py

#### Détection de version

```python
def detect_config_version(config: Dict[str, Any]) -> str:
    """
    Détecte la version de configuration (v1 ou v2).
    
    Logique:
    - v2 détectée si sections "ui", "folders", "backup" présentes
    - v1 détectée sinon (structure plate)
    
    Returns:
        "v1" ou "v2"
    """
```

#### Migration v1 → v2

```python
def migrate_v1_to_v2(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migre une configuration v1 vers v2.
    
    Processus:
    1. Créer structure v2 vide (copie de DEFAULT_CONFIG)
    2. Pour chaque clé v1 dans old_config:
       a. Chercher mapping dans LEGACY_KEY_MAPPING
       b. Si trouvé: copier la valeur dans la structure v2
       c. Si non trouvé: logger warning + conserver dans section "unknown"
    3. Retourner nouvelle structure
    
    Sécurité:
    - Aucune donnée perdue (clés inconnues conservées)
    - Valeurs par défaut appliquées si manquantes
    - Logging détaillé de chaque migration
    """
```

#### Création de backup

```python
def create_backup(config_file: str) -> bool:
    """
    Crée un backup avant migration.
    
    Format: config.json.backup_YYYYMMDD_HHMMSS
    Exemple: config.json.backup_20251116_143052
    
    Returns:
        True si succès, False sinon
    """
```

#### Validation post-migration

```python
def validate_migrated_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valide la structure migrée.
    
    Vérifications:
    - Toutes les sections requises présentes (ui, folders, backup, system, game)
    - Sous-sections backup présentes (characters, cookies, armor)
    - Clés critiques présentes dans chaque section
    
    Returns:
        (is_valid: bool, errors: List[str])
    """
```

#### Résumé de migration

```python
def get_migration_summary(old_config, new_config) -> str:
    """
    Génère un rapport détaillé de migration.
    
    Contient:
    - Nombre de clés migrées
    - Liste des transformations
    - Clés inconnues (si présentes)
    - Structure finale
    
    Utilisé pour logging et debugging
    """
```

---

## API du ConfigManager

### Méthodes principales

#### load_config()

```python
def load_config(self):
    """
    Charge la configuration avec migration automatique.
    
    Workflow:
    1. Charger config.json
    2. Détecter version (v1/v2)
    3. Si v1:
       a. Créer backup
       b. Migrer vers v2
       c. Valider
       d. Sauvegarder
       e. Logger résumé
    4. Si v2:
       a. Charger directement
    5. Retourner config
    """
```

#### get() - Notation pointée

```python
def get(self, key: str, default=None) -> Any:
    """
    Récupère une valeur avec support notation pointée.
    
    Exemples:
        config.get("ui.language")              # v2 (recommandé)
        config.get("language")                 # v1 (legacy, redirigé)
        config.get("backup.characters.enabled")
        config.get("nonexistent", "fallback")
    
    Logique:
    1. Si "." dans key → navigation hiérarchique
    2. Sinon, si key dans LEGACY_KEY_MAPPING → rediriger vers clé v2
    3. Sinon → chercher au root (backward compat)
    4. Si non trouvé → retourner default
    """
```

#### set() - Notation pointée avec validation

```python
def set(self, key: str, value: Any, save=True, validate=False):
    """
    Définit une valeur avec support notation pointée.
    
    Paramètres:
        key: Clé v2 ou v1 (ex: "ui.theme" ou "theme")
        value: Nouvelle valeur
        save: Sauvegarder immédiatement sur disque
        validate: Valider la valeur avant de la définir
    
    Exemples:
        config.set("ui.theme", "purple")
        config.set("theme", "dark")  # Legacy, redirigé vers ui.theme
        config.set("ui.font_scale", 1.5, validate=True)
    
    Validation (si validate=True):
    - Type vérifié contre VALIDATION_SCHEMA
    - Valeurs allowed vérifiées
    - Min/max vérifiés pour les nombres
    - Rejeté si invalide
    """
```

#### get_section()

```python
def get_section(self, section: str) -> Dict[str, Any]:
    """
    Récupère une section complète.
    
    Exemples:
        config.get_section("ui")       # Tout ui.*
        config.get_section("backup")   # Tout backup.*
    
    Retourne un dictionnaire avec toutes les clés de la section.
    """
```

---

## Rétrocompatibilité

### Garantie 100%

**Toutes les anciennes clés v1 continuent de fonctionner** grâce au LEGACY_KEY_MAPPING.

### Exemples de compatibilité

```python
# ✅ AVANT (v1) - Fonctionne toujours
language = config.get("language")
config.set("backup_enabled", True)
theme = config.get("theme", "default")

# ✅ APRÈS (v2) - Nouvelles méthodes recommandées
language = config.get("ui.language")
config.set("backup.characters.auto_daily_backup", True)
theme = config.get("ui.theme", "purple")

# ✅ Les deux fonctionnent simultanément !
```

### Redirection automatique

Quand du code utilise une clé v1 :

1. ConfigManager détecte la clé legacy
2. Cherche dans LEGACY_KEY_MAPPING
3. Redirige automatiquement vers la clé v2
4. Retourne la valeur

**Transparence totale** : le code legacy n'a pas besoin d'être modifié immédiatement.

### Code refactorisé

Bien que la rétrocompatibilité soit garantie, **tout le code a été refactorisé** pour utiliser la notation v2 :

| Fichier | Occurrences refactorées |
|---------|------------------------|
| main.py | 53 |
| UI/settings_dialog.py | 46 |
| UI/dialogs.py | 18 |
| Functions/backup_manager.py | 6 |
| Functions/tree_manager.py | Multiple |
| Functions/ui_manager.py | Multiple |
| Functions/logging_manager.py | Multiple |
| Functions/migration_manager.py | Multiple |
| Functions/language_manager.py | Multiple |
| Functions/eden_scraper.py | Multiple |
| Functions/cookie_manager.py | Multiple |

---

## Validation

### Fonction validate_value()

```python
def validate_value(key_path: str, value: Any) -> bool:
    """
    Valide une valeur contre le schéma.
    
    Vérifications:
    1. Type (str, int, bool, tuple de types, etc.)
    2. Valeurs autorisées (si liste "allowed" définie)
    3. Min/Max (pour nombres)
    
    Exemples:
        validate_value("ui.language", "fr")    # True
        validate_value("ui.language", "es")    # False (non dans allowed)
        validate_value("ui.font_scale", 1.5)   # True
        validate_value("ui.font_scale", 3.0)   # False (max=2.0)
    """
```

### Utilisation dans le code

```python
# Validation explicite
if config.validate_value("ui.theme", new_theme):
    config.set("ui.theme", new_theme)
else:
    print("Thème invalide!")

# Validation automatique avec set()
config.set("ui.theme", new_theme, validate=True)  # Rejeté si invalide
```

---

## Guide d'utilisation

### Pour les développeurs

#### Lecture de configuration

```python
from Functions.config_manager import ConfigManager

config = ConfigManager()

# Lire une valeur simple
language = config.get("ui.language", "en")

# Lire une section complète
ui_settings = config.get_section("ui")

# Lire avec navigation profonde
backup_path = config.get("backup.characters.path")
```

#### Écriture de configuration

```python
# Écrire une valeur (sauvegarde auto)
config.set("ui.theme", "purple")

# Écrire sans sauvegarder immédiatement
config.set("ui.font_scale", 1.2, save=False)
# ... autres modifications ...
config.save_config()  # Sauvegarde groupée

# Écrire avec validation
config.set("ui.theme", "invalid", validate=True)  # Rejeté
```

#### Ajout de nouvelles options

1. **Ajouter dans DEFAULT_CONFIG** (config_schema.py) :
```python
"system": {
    # ... existant ...
    "new_option": "default_value",
}
```

2. **Ajouter validation dans VALIDATION_SCHEMA** :
```python
"system": {
    # ... existant ...
    "new_option": {
        "type": str,
        "allowed": ["value1", "value2"],
        "default": "value1"
    }
}
```

3. **Si besoin de rétrocompatibilité, ajouter dans LEGACY_KEY_MAPPING** :
```python
"old_option_name": "system.new_option"
```

4. **Utiliser dans le code** :
```python
value = config.get("system.new_option")
```

### Pour les utilisateurs

#### Migration automatique

Lors de la première utilisation de v0.108 :

1. **Backup automatique** : `config.json.backup_20251116_143052`
2. **Migration** : Structure v1 → v2
3. **Validation** : Vérification d'intégrité
4. **Sauvegarde** : Nouvelle structure écrite
5. **Log détaillé** : Rapport de migration dans la console

**Aucune action requise** - tout est automatique !

#### Structure du fichier config.json

Avant (v1) :
```json
{
    "language": "fr",
    "theme": "dark",
    "character_folder": "D:/Characters",
    "backup_enabled": true,
    "debug_mode": false
}
```

Après (v2) :
```json
{
    "ui": {
        "language": "en",
        "theme": "purple"
    },
    "folders": {
        "characters": "D:/Characters"
    },
    "backup": {
        "characters": {
            "auto_daily_backup": true
        }
    },
    "system": {
        "debug_mode": false
    }
}
```

---

## Maintenance

### Logs de migration

Lors d'une migration, les informations suivantes sont loggées :

```
[CONFIG MIGRATION] Starting migration from v1 to v2...
[CONFIG MIGRATION] Migrated: language → ui.language = fr
[CONFIG MIGRATION] Migrated: theme → ui.theme = dark
[CONFIG MIGRATION] Migrated: character_folder → folders.characters = D:/Characters
[CONFIG MIGRATION] Migrated: backup_enabled → backup.characters.auto_daily_backup = True
...
[CONFIG MIGRATION] Migration complete: 37 keys migrated
```

### Fichiers de backup

Format : `config.json.backup_YYYYMMDD_HHMMSS`

**Conservation recommandée** : Garder au moins 1 backup en cas de problème.

**Restauration manuelle** :
```powershell
# Sauvegarder la version actuelle
Copy-Item config.json config.json.current

# Restaurer depuis backup
Copy-Item config.json.backup_20251116_143052 config.json
```

### Débogage

#### Vérifier la version

```python
from Functions.config_migration import detect_config_version
import json

with open("Configuration/config.json") as f:
    data = json.load(f)
    version = detect_config_version(data)
    print(f"Version: {version}")
```

#### Valider la configuration

```python
from Functions.config_migration import validate_migrated_config
import json

with open("Configuration/config.json") as f:
    data = json.load(f)
    is_valid, errors = validate_migrated_config(data)
    
    if is_valid:
        print("✅ Configuration valide")
    else:
        print("❌ Erreurs détectées:")
        for error in errors:
            print(f"  - {error}")
```

#### Forcer une migration

```python
from Functions.config_manager import ConfigManager
from Functions.config_migration import migrate_v1_to_v2, create_backup
import json

# Charger config actuelle
with open("Configuration/config.json") as f:
    old_config = json.load(f)

# Créer backup
create_backup("Configuration/config.json")

# Migrer
new_config = migrate_v1_to_v2(old_config)

# Sauvegarder
config = ConfigManager()
config.config = new_config
config.save_config()

print("Migration forcée terminée")
```

### Problèmes courants

#### 1. Config reste en v1

**Symptôme** : La migration ne se déclenche pas.

**Solution** :
- Vérifier que `detect_config_version()` retourne bien "v1"
- Vérifier les permissions d'écriture sur config.json
- Consulter les logs pour erreurs

#### 2. Valeurs perdues après migration

**Symptôme** : Certaines valeurs sont None après migration.

**Solution** :
- Vérifier le fichier backup (`config.json.backup_*`)
- Comparer avec LEGACY_KEY_MAPPING (clé peut être manquante)
- Ajouter le mapping si nécessaire et re-migrer

#### 3. Thème ne s'applique pas

**Symptôme** : Le thème par défaut ne fonctionne pas.

**Cause** : Fichier de thème inexistant (ex: "dracula.json" n'existe pas).

**Solution** :
- Vérifier les thèmes disponibles dans `Themes/`
- Utiliser un thème existant : "default", "dark", "light", "purple"
- Mettre à jour DEFAULT_CONFIG avec un thème valide

---

## Résumé des changements v0.108

### Nomenclature

| Changement | Avant | Après | Raison |
|------------|-------|-------|--------|
| **backup enabled** | `enabled` | `auto_daily_backup` | Plus explicite |
| **backup last_date** | Uniquement characters | characters, cookies, armor | Cohérence |
| **Thème par défaut** | "default" | "purple" | Choix utilisateur |
| **Langue par défaut** | "fr" | "en" | Internationalisation |
| **auto_delete_old** | `False` | `True` | Gestion automatique |
| **size_limit_mb** | 5 MB (cookies/armor) | 10 MB | Plus d'espace |

### Fichiers modifiés

**Nouveaux fichiers :**
- `Functions/config_schema.py` (318 lignes)
- `Functions/config_migration.py` (186 lignes)

**Fichiers modifiés :**
- `Functions/config_manager.py` (migration integration)
- `main.py` (53 occurrences refactorées)
- `UI/settings_dialog.py` (46 occurrences)
- `UI/dialogs.py` (18 occurrences)
- `Functions/backup_manager.py` (6 occurrences)
- 8 autres fichiers Functions/ (multiple occurrences chacun)

**Total :** ~2800 lignes ajoutées, 11 fichiers modifiés, 100% rétrocompatible

---

## Annexes

### Mapping complet v1 → v2

| # | Clé v1 | Clé v2 | Catégorie |
|---|--------|--------|-----------|
| 1 | `language` | `ui.language` | UI |
| 2 | `theme` | `ui.theme` | UI |
| 3 | `font_scale` | `ui.font_scale` | UI |
| 4 | `column_widths` | `ui.column_widths` | UI |
| 5 | `column_visibility` | `ui.column_visibility` | UI |
| 6 | `tree_view_header_state` | `ui.tree_view_header_state` | UI |
| 7 | `manual_column_resize` | `ui.manual_column_resize` | UI |
| 8 | `character_folder` | `folders.characters` | Folders |
| 9 | `log_folder` | `folders.logs` | Folders |
| 10 | `armor_folder` | `folders.armor` | Folders |
| 11 | `cookies_folder` | `folders.cookies` | Folders |
| 12 | `backup_enabled` | `backup.characters.auto_daily_backup` | Backup |
| 13 | `backup_path` | `backup.characters.path` | Backup |
| 14 | `backup_compress` | `backup.characters.compress` | Backup |
| 15 | `backup_size_limit_mb` | `backup.characters.size_limit_mb` | Backup |
| 16 | `backup_auto_delete_old` | `backup.characters.auto_delete_old` | Backup |
| 17 | `backup_last_date` | `backup.characters.last_date` | Backup |
| 18 | `cookies_backup_enabled` | `backup.cookies.auto_daily_backup` | Backup |
| 19 | `cookies_backup_path` | `backup.cookies.path` | Backup |
| 20 | `cookies_backup_compress` | `backup.cookies.compress` | Backup |
| 21 | `cookies_backup_size_limit_mb` | `backup.cookies.size_limit_mb` | Backup |
| 22 | `cookies_backup_auto_delete_old` | `backup.cookies.auto_delete_old` | Backup |
| 23 | `cookies_backup_last_date` | `backup.cookies.last_date` | Backup |
| 24 | `armor_backup_enabled` | `backup.armor.auto_daily_backup` | Backup |
| 25 | `armor_backup_path` | `backup.armor.path` | Backup |
| 26 | `armor_backup_compress` | `backup.armor.compress` | Backup |
| 27 | `armor_backup_size_limit_mb` | `backup.armor.size_limit_mb` | Backup |
| 28 | `armor_backup_auto_delete_old` | `backup.armor.auto_delete_old` | Backup |
| 29 | `armor_backup_last_date` | `backup.armor.last_date` | Backup |
| 30 | `debug_mode` | `system.debug_mode` | System |
| 31 | `show_debug_window` | `system.show_debug_window` | System |
| 32 | `disable_disclaimer` | `system.disable_disclaimer` | System |
| 33 | `preferred_browser` | `system.preferred_browser` | System |
| 34 | `allow_browser_download` | `system.allow_browser_download` | System |
| 35 | `servers` | `game.servers` | Game |
| 36 | `default_server` | `game.default_server` | Game |
| 37 | `seasons` | `game.seasons` | Game |
| 38 | `default_season` | `game.default_season` | Game |
| 39 | `default_realm` | `game.default_realm` | Game |

### Thèmes disponibles

| ID | Nom | Fichier | Description |
|----|-----|---------|-------------|
| `default` | Light | `default.json` | Thème clair système |
| `dark` | Dark | `dark.json` | Thème sombre |
| `light` | Light | `default.json` | Alias de default |
| `purple` | Purple | `purple.json` | **Thème violet (défaut v0.108)** |

---

**Fin de la documentation technique**
