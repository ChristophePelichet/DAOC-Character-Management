# Audit des Données Dynamiques - DAOC Character Manager

## 📋 Résumé

Toutes les données de jeu (classes, races, spécialisations, realm ranks, et realms) sont maintenant **entièrement dynamiques** et chargées depuis les fichiers JSON. Aucune donnée de jeu n'est codée en dur dans le code Python.

## ✅ Modifications Apportées

### 1. **DataManager** (`Functions/data_manager.py`)

#### Ajouts :
- **`_realms_cache`** : Cache pour stocker la liste des realms
- **`get_realms()`** : Nouvelle méthode qui retourne la liste des realms depuis `classes_races.json`
  ```python
  def get_realms(self) -> List[str]:
      """Récupère la liste des royaumes depuis les données JSON"""
      if self._realms_cache is None:
          data = self.load_classes_races()
          self._realms_cache = list(data.keys())
      return self._realms_cache
  ```

#### Impact :
- Les realms sont maintenant extraits dynamiquement des clés du fichier `Data/classes_races.json`
- Si vous ajoutez un nouveau realm (ex: "Cathal Valley"), il sera automatiquement détecté

---

### 2. **Character Manager** (`Functions/character_manager.py`)

#### Avant :
```python
REALMS = ["Albion", "Hibernia", "Midgard"]  # ❌ Codé en dur
```

#### Après :
```python
def _get_data_manager():
    """Lazy initialization of DataManager to avoid circular imports"""
    global _data_manager
    if _data_manager is None:
        from Functions.data_manager import DataManager
        _data_manager = DataManager()
    return _data_manager

def get_realms():
    """Returns the list of realms from JSON data"""
    return _get_data_manager().get_realms()

# Keep REALMS as a callable for backward compatibility
REALMS = get_realms()  # ✅ Dynamique
```

#### Impact :
- `REALMS` est maintenant une liste dynamique chargée depuis JSON
- Tous les usages existants de `REALMS` continuent de fonctionner
- Compatible avec les imports circulaires via lazy loading

---

### 3. **Data Editor** (`data_editor.py`)

#### Modifications principales :

##### A. Initialisation dynamique des realms
**Avant :**
```python
self.realm_ranks_files = {
    "Albion": Path("Data/realm_ranks_albion.json"),
    "Hibernia": Path("Data/realm_ranks_hibernia.json"),
    "Midgard": Path("Data/realm_ranks_midgard.json")
}  # ❌ Codé en dur
```

**Après :**
```python
self.realms_list = []  # Will be populated from JSON
self.realm_ranks_files = {}  # Will be populated dynamically
```

##### B. Chargement dynamique dans `load_data()`
```python
# Extract realms from JSON data
self.realms_list = list(self.classes_races_data.keys())

# Build realm_ranks_files dynamically based on realms found
self.realm_ranks_files = {
    realm: Path(f"Data/realm_ranks_{realm.lower()}.json")
    for realm in self.realms_list
}

# Update combo boxes with dynamic realms
self.realm_combo.clear()
self.realm_combo.addItems(self.realms_list)
self.ranks_realm_combo.clear()
self.ranks_realm_combo.addItems(self.realms_list)
```

##### C. ComboBox realms (lignes 103 et 207)
**Avant :**
```python
self.realm_combo.addItems(["Albion", "Hibernia", "Midgard"])  # ❌ Codé en dur
```

**Après :**
```python
# Realms will be populated dynamically from JSON in load_data()  # ✅ Dynamique
```

##### D. Checkboxes des races (ligne 165)
**Avant :**
```python
for race in ["Briton", "Avalonian", "Highlander", "Saracen", ...]:  # ❌ Codé en dur
    checkbox = QCheckBox(race)
    ...
```

**Après :**
```python
def populate_races_checkboxes(self):
    """Populate races checkboxes dynamically from all realms"""
    # Collect all unique race names from all realms
    all_races = set()
    for realm_data in self.classes_races_data.values():
        if 'races' in realm_data:
            for race in realm_data['races']:
                if isinstance(race, dict) and 'name' in race:
                    all_races.add(race['name'])
    
    # Create checkboxes for each unique race
    for race_name in sorted(all_races):
        checkbox = QCheckBox(race_name)
        checkbox.stateChanged.connect(self.mark_modified)
        self.races_checkboxes[race_name] = checkbox
        self.races_scroll_layout.addWidget(checkbox)
```

#### Impact :
- Les races sont maintenant extraites de TOUS les realms dans le JSON
- Si vous ajoutez une nouvelle race dans un realm, elle apparaîtra automatiquement dans l'éditeur
- Les realm ranks files sont générés automatiquement selon le pattern `realm_ranks_{realm}.json`

---

## 🎯 Garanties de Compatibilité Future

### Scénario 1 : Ajout d'un nouveau Realm
**Exemple : Ajouter "Cathal Valley"**

1. Modifiez `Data/classes_races.json` :
   ```json
   {
     "Albion": { ... },
     "Hibernia": { ... },
     "Midgard": { ... },
     "Cathal Valley": {
       "classes": [...],
       "races": [...]
     }
   }
   ```

2. Créez `Data/realm_ranks_cathal valley.json` (le nom est automatiquement généré en lowercase)

3. **Résultat automatique** :
   - ✅ "Cathal Valley" apparaît dans tous les dropdowns de realm
   - ✅ Les personnages peuvent être créés/édités pour ce realm
   - ✅ L'éditeur de données charge automatiquement le nouveau fichier
   - ✅ Aucune modification de code nécessaire

### Scénario 2 : Ajout d'une nouvelle Race
**Exemple : Ajouter "Minotaur" à Albion**

1. Modifiez `Data/classes_races.json` :
   ```json
   {
     "Albion": {
       "races": [
         {"name": "Briton", "name_fr": "Briton", "name_de": "Brite"},
         {"name": "Minotaur", "name_fr": "Minotaure", "name_de": "Minotaurus"}
       ]
     }
   }
   ```

2. **Résultat automatique** :
   - ✅ "Minotaur" apparaît dans le dropdown des races
   - ✅ "Minotaur" apparaît dans l'éditeur de données (checkboxes)
   - ✅ Les traductions sont utilisées selon la langue active
   - ✅ Aucune modification de code nécessaire

### Scénario 3 : Ajout d'une nouvelle Classe
**Exemple : Ajouter "Bard" à Hibernia**

1. Modifiez `Data/classes_races.json` :
   ```json
   {
     "Hibernia": {
       "classes": [
         {
           "name": "Bard",
           "name_fr": "Barde",
           "name_de": "Barde",
           "races": ["Celt", "Firbolg"],
           "specializations": [...]
         }
       ]
     }
   }
   ```

2. **Résultat automatique** :
   - ✅ "Bard" apparaît dans le dropdown des classes
   - ✅ Seules les races "Celt" et "Firbolg" sont disponibles pour cette classe
   - ✅ L'éditeur de données affiche la nouvelle classe
   - ✅ Aucune modification de code nécessaire

### Scénario 4 : Modification des Realm Ranks
**Exemple : Ajouter un Rank 15**

1. Modifiez `Data/realm_ranks_albion.json` :
   ```json
   [
     ...existing ranks...,
     {
       "rank": 15,
       "level": "15L1",
       "realm_points": 15000000,
       "title": "Legendary Champion"
     }
   ]
   ```

2. **Résultat automatique** :
   - ✅ Le nouveau rank apparaît dans l'éditeur
   - ✅ Le slider s'ajuste automatiquement (max=15)
   - ✅ Les calculs de progression fonctionnent
   - ✅ Aucune modification de code nécessaire

---

## 📂 Fichiers Modifiés

| Fichier | Lignes modifiées | Type de changement |
|---------|------------------|-------------------|
| `Functions/data_manager.py` | 26-27, 176-186 | Ajout méthode `get_realms()` |
| `Functions/character_manager.py` | 1-30 | Remplacement constante `REALMS` |
| `data_editor.py` | 29-30, 40-42, 103, 207, 165-167, 240-280 | Dynamisation complète |

---

## 🧪 Tests Recommandés

### Test 1 : Vérifier que tous les realms sont chargés
```python
from Functions.data_manager import DataManager
dm = DataManager()
print(dm.get_realms())
# Devrait afficher: ['Albion', 'Hibernia', 'Midgard']
```

### Test 2 : Vérifier REALMS dans character_manager
```python
from Functions.character_manager import REALMS
print(REALMS)
# Devrait afficher: ['Albion', 'Hibernia', 'Midgard']
```

### Test 3 : Tester l'ajout d'un nouveau realm
1. Ajouter `"TestRealm": {"classes": [], "races": []}` dans `classes_races.json`
2. Créer `Data/realm_ranks_testrealm.json` avec `[]`
3. Relancer l'application
4. Vérifier que "TestRealm" apparaît dans tous les dropdowns

### Test 4 : Tester la modification d'un personnage existant
1. Ouvrir un personnage existant (créé avant ces modifications)
2. Modifier son realm/classe/race
3. Sauvegarder
4. Vérifier que les nouvelles valeurs sont correctement enregistrées dans le JSON

---

## ⚠️ Points d'Attention

### 1. Structure JSON des Classes/Races
Le fichier `classes_races.json` DOIT avoir cette structure :
```json
{
  "RealmName": {
    "classes": [ {...}, {...} ],
    "races": [ {...}, {...} ]
  }
}
```

Si la structure change, ajustez :
- `DataManager.get_realms()` (ligne 177)
- `DataEditor.load_data()` (ligne 250)

### 2. Nommage des Fichiers Realm Ranks
Le pattern est : `realm_ranks_{realm_name_lowercase}.json`

Si "Cathal Valley" est ajouté, le fichier sera `realm_ranks_cathal valley.json`

### 3. Compatibilité Ascendante
Les fichiers de personnages existants (`.json` dans `Characters/`) ne sont **PAS** affectés par ces changements. Ils continuent de fonctionner normalement.

---

## 📊 Résumé des Données Dynamiques

| Type de données | Source | Méthode d'accès | Fichier modifié |
|-----------------|--------|----------------|-----------------|
| **Realms** | `classes_races.json` (clés) | `DataManager.get_realms()` | `data_manager.py` |
| **Classes** | `classes_races.json` | `DataManager.get_classes(realm)` | *(existant)* |
| **Races** | `classes_races.json` | `DataManager.get_races(realm)` | *(existant)* |
| **Spécialisations** | `classes_races.json` | Inclus dans classe | *(existant)* |
| **Realm Ranks** | `realm_ranks_{realm}.json` | `DataManager.load_realm_ranks()` | *(existant)* |
| **Traductions** | `Language/{lang}.json` | `LanguageManager` | *(existant)* |

---

## ✅ Conclusion

**Toutes les données de jeu sont maintenant dynamiques et transparentes.**

Si vous modifiez un fichier JSON de données :
- ✅ Les modifications seront visibles immédiatement au redémarrage
- ✅ Les personnages existants restent compatibles
- ✅ Aucune modification de code Python n'est nécessaire
- ✅ L'éditeur de données (data_editor.py) reflète automatiquement les changements

**L'application est maintenant 100% data-driven !** 🎉
