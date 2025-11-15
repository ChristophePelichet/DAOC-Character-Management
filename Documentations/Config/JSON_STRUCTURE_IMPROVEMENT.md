# 📋 Amélioration de la Structure config.json

**Version :** v0.108 (planifié)  
**Objectif :** Restructurer config.json pour meilleure lisibilité et maintenabilité  
**Statut :** 🟡 En Planning

---

## 📊 État Actuel vs Cible

### Structure Actuelle (v0.108)

```json
{
  "language": "fr",
  "theme": "dark",
  "character_folder": "Characters/",
  "log_folder": "Logs/",
  "armor_folder": "Data/",
  "cookie_folder": "Configuration/",
  "backup_frequency": "daily",
  "backup_retention": 5,
  "backup_location": "Backup/Characters/",
  "column_widths": {...},
  "visible_columns": {...}
}
```

**Problèmes :**
- ❌ Structure plate (toutes clés au même niveau)
- ❌ Pas de regroupement logique
- ❌ Difficile à naviguer avec 15+ clés
- ❌ Nouvelle clé → ajoutée en fin de fichier

### Structure Cible (v0.108)

```json
{
  "ui": {
    "language": "fr",
    "theme": "dark",
    "column_widths": {
      "Name": 150,
      "Realm": 100,
      "Class": 120
    },
    "visible_columns": {
      "Name": true,
      "Realm": true,
      "Class": true
    }
  },
  "folders": {
    "characters": "Characters/",
    "logs": "Logs/",
    "armor": "Data/",
    "cookies": "Configuration/"
  },
  "backup": {
    "frequency": "daily",
    "retention": 5,
    "location": "Backup/Characters/"
  }
}
```

**Avantages :**
- ✅ Sections logiques claires
- ✅ Navigation facile (ui, folders, backup)
- ✅ Extensible (nouvelles sections)
- ✅ Validation par section possible
- ✅ Documentation par section

---

## 🎯 Objectifs du Refactoring

### 1. Structure Hiérarchique

**Grouper les paramètres par domaine fonctionnel :**

- **`ui`** : Tout ce qui concerne l'interface utilisateur
- **`folders`** : Emplacements des dossiers de données
- **`backup`** : Configuration du système de sauvegarde
- **`advanced`** (futur) : Paramètres avancés/debug

### 2. Rétrocompatibilité

**Migration automatique des anciens config.json :**

```python
def migrate_config_to_v2(old_config):
    """Migre config.json v1 (plat) vers v2 (structuré)"""
    new_config = {
        "ui": {
            "language": old_config.get("language", "fr"),
            "theme": old_config.get("theme", "dark"),
            "column_widths": old_config.get("column_widths", {}),
            "visible_columns": old_config.get("visible_columns", {})
        },
        "folders": {
            "characters": old_config.get("character_folder", "Characters/"),
            "logs": old_config.get("log_folder", "Logs/"),
            "armor": old_config.get("armor_folder", "Data/"),
            "cookies": old_config.get("cookie_folder", "Configuration/")
        },
        "backup": {
            "frequency": old_config.get("backup_frequency", "daily"),
            "retention": old_config.get("backup_retention", 5),
            "location": old_config.get("backup_location", "Backup/Characters/")
        }
    }
    return new_config
```

### 3. API de Configuration Améliorée

**Support de la notation pointée :**

```python
# Ancienne API (toujours supportée)
config.get("language")
config.set("language", "en")

# Nouvelle API (recommandée)
config.get("ui.language")
config.set("ui.language", "en")

# Accès direct aux sections
ui_config = config.get_section("ui")
# → {"language": "fr", "theme": "dark", ...}
```

### 4. Validation par Section

```python
SCHEMA = {
    "ui": {
        "language": ["fr", "en", "de"],  # Valeurs autorisées
        "theme": ["dark", "light", "purple"],
        "column_widths": dict,
        "visible_columns": dict
    },
    "folders": {
        "characters": str,
        "logs": str,
        "armor": str,
        "cookies": str
    },
    "backup": {
        "frequency": ["never", "daily", "weekly", "monthly"],
        "retention": (1, 99),  # Range
        "location": str
    }
}
```

---

## 📝 Liste des Tâches

### Phase 1 : Préparation (1h)

- [ ] **1.1** Créer backup de `Functions/config_manager.py` actuel
- [ ] **1.2** Documenter toutes les clés actuelles et leur usage
- [ ] **1.3** Créer schéma de validation JSON
- [ ] **1.4** Créer template `config_v2.json` avec structure cible
- [ ] **1.5** Créer fichier de tests unitaires `test_config_migration.py`

### Phase 2 : Migration Auto (2h)

- [ ] **2.1** Implémenter `migrate_config_to_v2()` dans `config_manager.py`
- [ ] **2.2** Détecter version config au chargement
  ```python
  if "ui" not in config:
      # Ancien format v1
      config = migrate_config_to_v2(config)
      save_config()
  ```
- [ ] **2.3** Créer backup automatique avant migration (`.json.backup`)
- [ ] **2.4** Logger la migration (`Migration config v1 → v2 effectuée`)
- [ ] **2.5** Tester migration avec plusieurs config.json réels

### Phase 3 : API Améliorée (2h)

- [ ] **3.1** Implémenter notation pointée dans `get()`
  ```python
  def get(self, key, default=None):
      if "." in key:
          section, subkey = key.split(".", 1)
          return self.config.get(section, {}).get(subkey, default)
      return self.config.get(key, default)
  ```
- [ ] **3.2** Implémenter notation pointée dans `set()`
  ```python
  def set(self, key, value):
      if "." in key:
          section, subkey = key.split(".", 1)
          if section not in self.config:
              self.config[section] = {}
          self.config[section][subkey] = value
      else:
          self.config[key] = value
  ```
- [ ] **3.3** Ajouter méthode `get_section(section_name)`
- [ ] **3.4** Ajouter méthode `set_section(section_name, section_dict)`
- [ ] **3.5** Maintenir compatibilité avec ancienne API (get/set simples)

### Phase 4 : Refactoring Code Base (3h)

- [ ] **4.1** Identifier tous les appels `config.get()` dans le projet
  ```bash
  grep -r "config\.get(" --include="*.py"
  ```
- [ ] **4.2** Remplacer par notation pointée (UI)
  - [ ] `config.get("language")` → `config.get("ui.language")`
  - [ ] `config.get("theme")` → `config.get("ui.theme")`
  - [ ] `config.get("column_widths")` → `config.get("ui.column_widths")`
  - [ ] `config.get("visible_columns")` → `config.get("ui.visible_columns")`
- [ ] **4.3** Remplacer par notation pointée (Folders)
  - [ ] `config.get("character_folder")` → `config.get("folders.characters")`
  - [ ] `config.get("log_folder")` → `config.get("folders.logs")`
  - [ ] `config.get("armor_folder")` → `config.get("folders.armor")`
  - [ ] `config.get("cookie_folder")` → `config.get("folders.cookies")`
- [ ] **4.4** Remplacer par notation pointée (Backup)
  - [ ] `config.get("backup_frequency")` → `config.get("backup.frequency")`
  - [ ] `config.get("backup_retention")` → `config.get("backup.retention")`
  - [ ] `config.get("backup_location")` → `config.get("backup.location")`
- [ ] **4.5** Vérifier tous les `config.set()` et adapter

### Phase 5 : Validation (1h)

- [ ] **5.1** Implémenter validation par schéma
  ```python
  def validate_section(section, schema):
      """Valide une section contre son schéma"""
  ```
- [ ] **5.2** Valider au chargement du config
- [ ] **5.3** Valider avant sauvegarde
- [ ] **5.4** Logger les erreurs de validation
- [ ] **5.5** Valeurs par défaut si validation échoue

### Phase 6 : Documentation (1h)

- [ ] **6.1** Mettre à jour `CONFIG_DOCUMENTATION.md`
- [ ] **6.2** Ajouter exemples de structure v2
- [ ] **6.3** Documenter API de migration
- [ ] **6.4** Mettre à jour Wiki FR-Settings.md
- [ ] **6.5** Créer changelog détaillé

### Phase 7 : Tests (2h)

- [ ] **7.1** Exécuter tous les tests unitaires
- [ ] **7.2** Tests manuels complets (voir section Tests)
- [ ] **7.3** Tester avec config.json vierge
- [ ] **7.4** Tester avec config.json v1 existant
- [ ] **7.5** Tester modification via Settings
- [ ] **7.6** Vérifier ordre préservé dans JSON

---

## 🧪 Plan de Tests

### Tests Unitaires (`test_config_migration.py`)

```python
import unittest
from Functions.config_manager import ConfigManager, migrate_config_to_v2

class TestConfigMigration(unittest.TestCase):
    
    def test_migrate_v1_to_v2_all_keys(self):
        """Test migration complète v1 → v2"""
        old_config = {
            "language": "fr",
            "theme": "dark",
            "character_folder": "Characters/",
            "backup_frequency": "daily"
        }
        
        new_config = migrate_config_to_v2(old_config)
        
        self.assertEqual(new_config["ui"]["language"], "fr")
        self.assertEqual(new_config["ui"]["theme"], "dark")
        self.assertEqual(new_config["folders"]["characters"], "Characters/")
        self.assertEqual(new_config["backup"]["frequency"], "daily")
    
    def test_migrate_partial_config(self):
        """Test migration avec clés manquantes → valeurs par défaut"""
        old_config = {"language": "en"}
        
        new_config = migrate_config_to_v2(old_config)
        
        self.assertEqual(new_config["ui"]["language"], "en")
        self.assertEqual(new_config["ui"]["theme"], "dark")  # Défaut
    
    def test_dotted_notation_get(self):
        """Test notation pointée pour get()"""
        config = ConfigManager()
        config.config = {
            "ui": {"language": "fr", "theme": "dark"},
            "folders": {"characters": "Characters/"}
        }
        
        self.assertEqual(config.get("ui.language"), "fr")
        self.assertEqual(config.get("folders.characters"), "Characters/")
        self.assertEqual(config.get("ui.missing", "default"), "default")
    
    def test_dotted_notation_set(self):
        """Test notation pointée pour set()"""
        config = ConfigManager()
        config.config = {"ui": {}}
        
        config.set("ui.language", "en")
        
        self.assertEqual(config.config["ui"]["language"], "en")
    
    def test_get_section(self):
        """Test récupération section complète"""
        config = ConfigManager()
        config.config = {
            "ui": {"language": "fr", "theme": "dark"}
        }
        
        ui_section = config.get_section("ui")
        
        self.assertEqual(ui_section["language"], "fr")
        self.assertEqual(ui_section["theme"], "dark")
    
    def test_validation_invalid_language(self):
        """Test validation valeur invalide"""
        config = ConfigManager()
        
        result = config.validate_value("ui.language", "invalid")
        
        self.assertFalse(result)
    
    def test_validation_valid_theme(self):
        """Test validation valeur valide"""
        config = ConfigManager()
        
        result = config.validate_value("ui.theme", "purple")
        
        self.assertTrue(result)
    
    def test_json_structure_preserved(self):
        """Test que l'ordre JSON est préservé après save"""
        config = ConfigManager()
        config.config = {
            "ui": {"language": "fr"},
            "folders": {"characters": "Characters/"},
            "backup": {"frequency": "daily"}
        }
        
        config.save_config()
        config.load_config()
        
        keys = list(config.config.keys())
        self.assertEqual(keys, ["ui", "folders", "backup"])
```

### Tests Manuels (Checklist)

#### Test 1 : Migration Automatique

**Objectif :** Vérifier migration d'un ancien config.json

**Étapes :**
1. [ ] Créer `Configuration/config.json` avec structure v1 (plate)
2. [ ] Lancer l'application
3. [ ] **Vérifier :** Message log "Migration config v1 → v2 effectuée"
4. [ ] **Vérifier :** Fichier `Configuration/config.json.backup` créé
5. [ ] Ouvrir `Configuration/config.json`
6. [ ] **Vérifier :** Structure v2 (sections ui/folders/backup)
7. [ ] **Vérifier :** Toutes les valeurs préservées
8. [ ] **Vérifier :** Ordre logique des sections

**Résultat attendu :** ✅ Migration réussie, données intactes

---

#### Test 2 : Modification via Settings (Langue)

**Objectif :** Vérifier que modification préserve structure

**Étapes :**
1. [ ] Ouvrir Settings (`Ctrl+P`)
2. [ ] Onglet Général
3. [ ] Changer langue : FR → EN
4. [ ] Cliquer sur "Sauvegarder"
5. [ ] Fermer Settings
6. [ ] Ouvrir `Configuration/config.json`
7. [ ] **Vérifier :** `"ui": { "language": "en" }`
8. [ ] **Vérifier :** Structure v2 intacte
9. [ ] **Vérifier :** Ordre des sections préservé
10. [ ] **Vérifier :** Indentation propre (4 espaces)

**Résultat attendu :** ✅ Langue modifiée, structure intacte

---

#### Test 3 : Modification via Settings (Dossier)

**Objectif :** Vérifier changement de chemin

**Étapes :**
1. [ ] Ouvrir Settings
2. [ ] Onglet Dossiers
3. [ ] Modifier "Dossier Personnages" : `Characters/` → `D:/Temp/Chars/`
4. [ ] Cliquer sur "Sauvegarder"
5. [ ] Fermer Settings
6. [ ] Ouvrir `Configuration/config.json`
7. [ ] **Vérifier :** `"folders": { "characters": "D:/Temp/Chars/" }`
8. [ ] **Vérifier :** Autres sections intactes

**Résultat attendu :** ✅ Chemin modifié, structure OK

---

#### Test 4 : Modification via Settings (Backup)

**Objectif :** Vérifier paramètres de sauvegarde

**Étapes :**
1. [ ] Ouvrir Settings
2. [ ] Onglet Sauvegarde
3. [ ] Modifier Fréquence : `Quotidienne` → `Hebdomadaire`
4. [ ] Modifier Rétention : `5` → `10`
5. [ ] Cliquer sur "Sauvegarder"
6. [ ] Ouvrir `Configuration/config.json`
7. [ ] **Vérifier :** `"backup": { "frequency": "weekly", "retention": 10 }`

**Résultat attendu :** ✅ Paramètres backup modifiés

---

#### Test 5 : Config Vierge (Première Installation)

**Objectif :** Vérifier création config v2 par défaut

**Étapes :**
1. [ ] Supprimer `Configuration/config.json`
2. [ ] Lancer l'application
3. [ ] **Vérifier :** Config créé automatiquement
4. [ ] Ouvrir `Configuration/config.json`
5. [ ] **Vérifier :** Structure v2 (sections)
6. [ ] **Vérifier :** Valeurs par défaut correctes
7. [ ] **Vérifier :** Ordre : ui → folders → backup

**Résultat attendu :** ✅ Config v2 créé avec valeurs par défaut

---

#### Test 6 : Validation Valeur Invalide

**Objectif :** Vérifier rejet valeur hors schéma

**Étapes :**
1. [ ] Éditer manuellement `Configuration/config.json`
2. [ ] Modifier : `"language": "invalid_lang"`
3. [ ] Sauvegarder
4. [ ] Lancer l'application
5. [ ] **Vérifier :** Message warning dans logs
6. [ ] **Vérifier :** Valeur par défaut appliquée (`"fr"`)
7. [ ] Ouvrir Settings
8. [ ] **Vérifier :** Langue affichée = FR (défaut)

**Résultat attendu :** ✅ Valeur invalide corrigée automatiquement

---

#### Test 7 : Ordre Préservé après Multiples Modifications

**Objectif :** Vérifier stabilité de l'ordre

**Étapes :**
1. [ ] Modifier langue (Settings)
2. [ ] Sauvegarder
3. [ ] Modifier thème (Settings)
4. [ ] Sauvegarder
5. [ ] Modifier dossier Characters (Settings)
6. [ ] Sauvegarder
7. [ ] Modifier fréquence backup (Settings)
8. [ ] Sauvegarder
9. [ ] Ouvrir `Configuration/config.json`
10. [ ] **Vérifier :** Ordre toujours `ui` → `folders` → `backup`
11. [ ] **Vérifier :** Sous-clés dans ordre logique

**Résultat attendu :** ✅ Ordre parfaitement préservé

---

#### Test 8 : Compatibilité Ancienne API

**Objectif :** Vérifier que anciens appels fonctionnent

**Étapes :**
1. [ ] Ouvrir console Python Debug
2. [ ] Exécuter : `config.get("language")`
3. [ ] **Vérifier :** Retourne valeur (compatibilité rétro)
4. [ ] Exécuter : `config.set("language", "de")`
5. [ ] **Vérifier :** Valeur modifiée
6. [ ] Ouvrir `Configuration/config.json`
7. [ ] **Vérifier :** Modification appliquée dans section `ui`

**Résultat attendu :** ✅ Ancienne API toujours fonctionnelle

---

#### Test 9 : Nouvelle API Notation Pointée

**Objectif :** Vérifier nouvelle API

**Étapes :**
1. [ ] Console Python : `config.get("ui.language")`
2. [ ] **Vérifier :** Retourne valeur correcte
3. [ ] Exécuter : `config.set("ui.theme", "purple")`
4. [ ] **Vérifier :** Thème changé dans l'UI
5. [ ] Exécuter : `config.get_section("backup")`
6. [ ] **Vérifier :** Retourne dict complet de backup

**Résultat attendu :** ✅ Nouvelle API fonctionnelle

---

#### Test 10 : Sauvegarde Manuelle (Intégration)

**Objectif :** Vérifier compatibilité avec BackupManager

**Étapes :**
1. [ ] Ouvrir Settings → Sauvegarde
2. [ ] Cliquer "Sauvegarder les Personnages"
3. [ ] **Vérifier :** Sauvegarde créée
4. [ ] Vérifier que config.json utilise `backup.location`
5. [ ] **Vérifier :** Fichier ZIP dans bon dossier

**Résultat attendu :** ✅ Backup fonctionne avec nouvelle structure

---

## 📐 Schéma de Validation

```python
CONFIG_SCHEMA = {
    "ui": {
        "language": {
            "type": str,
            "allowed": ["fr", "en", "de"],
            "default": "fr"
        },
        "theme": {
            "type": str,
            "allowed": ["dark", "light", "purple"],
            "default": "dark"
        },
        "column_widths": {
            "type": dict,
            "default": {}
        },
        "visible_columns": {
            "type": dict,
            "default": {
                "Name": True,
                "Realm": True,
                "Class": True,
                "Race": True,
                "Level": True
            }
        }
    },
    "folders": {
        "characters": {
            "type": str,
            "default": "Characters/"
        },
        "logs": {
            "type": str,
            "default": "Logs/"
        },
        "armor": {
            "type": str,
            "default": "Data/"
        },
        "cookies": {
            "type": str,
            "default": "Configuration/"
        }
    },
    "backup": {
        "frequency": {
            "type": str,
            "allowed": ["never", "daily", "weekly", "monthly"],
            "default": "daily"
        },
        "retention": {
            "type": int,
            "range": (1, 99),
            "default": 5
        },
        "location": {
            "type": str,
            "default": "Backup/Characters/"
        }
    }
}
```

---

## 🔄 Exemple de Migration

### Avant (v1 - Actuel)

```json
{
  "language": "fr",
  "theme": "dark",
  "character_folder": "Characters/",
  "log_folder": "Logs/",
  "armor_folder": "Data/",
  "cookie_folder": "Configuration/",
  "backup_frequency": "daily",
  "backup_retention": 5,
  "backup_location": "Backup/Characters/",
  "column_widths": {
    "Name": 150,
    "Realm": 100
  },
  "visible_columns": {
    "Name": true,
    "Realm": true
  }
}
```

### Après (v2 - Cible)

```json
{
  "ui": {
    "language": "fr",
    "theme": "dark",
    "column_widths": {
      "Name": 150,
      "Realm": 100
    },
    "visible_columns": {
      "Name": true,
      "Realm": true
    }
  },
  "folders": {
    "characters": "Characters/",
    "logs": "Logs/",
    "armor": "Data/",
    "cookies": "Configuration/"
  },
  "backup": {
    "frequency": "daily",
    "retention": 5,
    "location": "Backup/Characters/"
  }
}
```

---

## 📊 Métriques de Succès

### Code

- [ ] **0 régressions** : Tous les tests passent
- [ ] **100% compatibilité** : Ancienne API fonctionne
- [ ] **Migration auto** : Fonctionne pour tous les cas
- [ ] **Validation** : Rejette valeurs invalides

### Fichier JSON

- [ ] **Ordre préservé** : Sections toujours dans le même ordre
- [ ] **Indentation** : 4 espaces, formatage cohérent
- [ ] **Lisibilité** : Structure claire et logique
- [ ] **Taille** : Pas d'augmentation significative

### Performance

- [ ] **Chargement** : < 50ms (identique à avant)
- [ ] **Sauvegarde** : < 20ms (identique à avant)
- [ ] **Migration** : < 100ms (une seule fois)

---

## ⏱️ Estimation Totale

| Phase | Durée | Complexité |
|-------|-------|------------|
| Préparation | 1h | 🟢 Facile |
| Migration Auto | 2h | 🟡 Moyenne |
| API Améliorée | 2h | 🟡 Moyenne |
| Refactoring | 3h | 🟠 Difficile |
| Validation | 1h | 🟡 Moyenne |
| Documentation | 1h | 🟢 Facile |
| Tests | 2h | 🟡 Moyenne |
| **TOTAL** | **12h** | 🟡 **Moyenne** |

---

## 🚀 Bénéfices Attendus

### Utilisateur

- ✅ Config plus lisible et compréhensible
- ✅ Sections logiques facilitent navigation
- ✅ Validation automatique évite erreurs
- ✅ Migration transparente (aucune action requise)

### Développeur

- ✅ Code plus maintenable (sections claires)
- ✅ Extensibilité (nouvelles sections faciles)
- ✅ Validation centralisée (moins de bugs)
- ✅ API moderne (notation pointée)

### Projet

- ✅ Base solide pour futures évolutions
- ✅ Standard professionnel
- ✅ Documentation améliorée
- ✅ Qualité code augmentée

---

## 📅 Planning Recommandé

**Version :** v0.108  
**Branche :** `108_Config_Json_Structure`

**Semaine 1 :**
- Jour 1-2 : Phases 1-2 (Préparation + Migration)
- Jour 3 : Phase 3 (API)
- Jour 4-5 : Phase 4 (Refactoring)

**Semaine 2 :**
- Jour 1 : Phase 5 (Validation)
- Jour 2 : Phase 6 (Documentation)
- Jour 3-4 : Phase 7 (Tests complets)
- Jour 5 : Corrections, polish, release

---

## 📝 Notes

- Migration 100% automatique, utilisateur ne voit rien
- Backup automatique de l'ancien config
- Logs détaillés pour debug
- Tests exhaustifs avant merge sur main
- Documentation Wiki à mettre à jour après release

---

**Statut :** 🟡 Planifié pour v0.108  
**Priorité :** ⭐⭐⭐⭐☆ (Haute - amélioration qualité code)  
**Risque :** 🟢 Faible (migration auto + tests complets)
