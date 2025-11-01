# 🔧 Correction de la configuration des colonnes

**Version :** 0.107  
**Date :** 31 octobre 2024  
**Type :** Bug fix

---

## 🔍 Problèmes identifiés

### 1. Colonne URL Herald manquante dans le redimensionnement
**Fichier :** `Functions/tree_manager.py` - ligne 305

**Problème :**
- Le TreeView possède **12 colonnes** (indices 0 à 11)
- La méthode `apply_column_resize_mode()` ne traitait que **11 colonnes** (range(11))
- La colonne 11 (URL Herald) n'était pas soumise à la configuration de redimensionnement

**Impact :**
- En mode automatique, la colonne URL restait avec un mode de resize non défini
- En mode manuel, elle était affectée par le `setSectionResizeMode` global mais pas explicitement

**Solution :**
```python
for i in range(12):  # Changé de range(11) à range(12)
```

---

### 2. Ordre des colonnes incorrect dans le menu de configuration
**Fichier :** `UI/dialogs.py` - ligne 846

**Problème :**
L'ordre des colonnes dans `ColumnsConfigDialog.COLUMNS_CONFIG` ne correspondait pas à l'ordre réel du TreeView :

**Ancien ordre du menu :**
```
0. selection
1. realm
2. name
3. level      ← INVERSÉ
4. realm_rank
5. realm_title
6. guild
7. page
8. server
9. class      ← INVERSÉ
10. race
11. url
```

**Ordre réel du TreeView :**
```
0. Selection
1. Realm
2. Name
3. Class      ← Position correcte
4. Level      ← Position correcte
5. Rank
6. Title
7. Guild
8. Page
9. Server
10. Race
11. URL
```

**Impact :**
- Les utilisateurs ne voyaient pas les colonnes dans le même ordre que dans le TreeView
- Confusion lors de la configuration de visibilité

**Solution :**
Réorganisation de `COLUMNS_CONFIG` pour correspondre à l'ordre du TreeView

---

### 3. Mapping incorrect dans apply_column_visibility
**Fichier :** `Functions/tree_manager.py` - ligne 278

**Problème :**
Le `column_map` utilisait l'ancien mapping avec Class et Level inversés, et la colonne URL manquait :

**Ancien mapping :**
```python
column_map = {
    "selection": 0, "realm": 1, "name": 2, "level": 3,  # level à l'index 3 ❌
    "realm_rank": 4, "realm_title": 5, "guild": 6, "page": 7,
    "server": 8, "class": 9, "race": 10  # class à l'index 9 ❌
    # URL manquant ❌
}
```

**Nouveau mapping (correct) :**
```python
column_map = {
    "selection": 0, "realm": 1, "name": 2, "class": 3, "level": 4,  # ✅
    "realm_rank": 5, "realm_title": 6, "guild": 7, "page": 8,
    "server": 9, "race": 10, "url": 11  # ✅
}
```

**Impact :**
- Affichage/masquage incorrect des colonnes Class et Level
- Colonne URL non configurable (toujours visible)

---

## ✅ Modifications apportées

### 1. `Functions/tree_manager.py`

#### Ligne 305 - `apply_column_resize_mode()`
```python
# AVANT
for i in range(11):
    if i == 2:  # Colonne Name
        header.setSectionResizeMode(i, QHeaderView.Stretch)
    else:
        header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

# APRÈS
for i in range(12):  # 12 colonnes : Selection(0), Realm(1), Name(2), Class(3), Level(4), Rank(5), Title(6), Guild(7), Page(8), Server(9), Race(10), URL(11)
    if i == 2:  # Colonne Name
        header.setSectionResizeMode(i, QHeaderView.Stretch)
    else:
        header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
```

#### Lignes 271-284 - `apply_column_visibility()`
```python
# AVANT
default_visibility = {
    "selection": True, "realm": True, "name": True, "level": True,
    "page": True, "guild": True, "realm_rank": True, "realm_title": True,
    "server": False, "class": True, "race": False
}

column_map = {
    "selection": 0, "realm": 1, "name": 2, "level": 3,
    "realm_rank": 4, "realm_title": 5, "guild": 6, "page": 7,
    "server": 8, "class": 9, "race": 10
}

# APRÈS
default_visibility = {
    "selection": True, "realm": True, "name": True, "class": True, "level": True,
    "realm_rank": True, "realm_title": True, "guild": True, "page": True,
    "server": False, "race": False, "url": False
}

column_map = {
    "selection": 0, "realm": 1, "name": 2, "class": 3, "level": 4,
    "realm_rank": 5, "realm_title": 6, "guild": 7, "page": 8,
    "server": 9, "race": 10, "url": 11
}
```

### 2. `UI/dialogs.py`

#### Lignes 846-858 - `ColumnsConfigDialog.COLUMNS_CONFIG`
```python
# AVANT
COLUMNS_CONFIG = [
    {"key": "selection", "name_key": "column_selection", "default": True},
    {"key": "realm", "name_key": "column_realm", "default": True},
    {"key": "name", "name_key": "column_name", "default": True},
    {"key": "level", "name_key": "column_level", "default": True},        # ❌ Position 3
    {"key": "realm_rank", "name_key": "column_realm_rank", "default": True},
    {"key": "realm_title", "name_key": "column_realm_title", "default": True},
    {"key": "guild", "name_key": "column_guild", "default": True},
    {"key": "page", "name_key": "column_page", "default": True},
    {"key": "server", "name_key": "column_server", "default": False},
    {"key": "class", "name_key": "column_class", "default": True},        # ❌ Position 9
    {"key": "race", "name_key": "column_race", "default": False},
    {"key": "url", "name_key": "column_url", "default": False},
]

# APRÈS
COLUMNS_CONFIG = [
    {"key": "selection", "name_key": "column_selection", "default": True},
    {"key": "realm", "name_key": "column_realm", "default": True},
    {"key": "name", "name_key": "column_name", "default": True},
    {"key": "class", "name_key": "column_class", "default": True},        # ✅ Position 3
    {"key": "level", "name_key": "column_level", "default": True},        # ✅ Position 4
    {"key": "realm_rank", "name_key": "column_realm_rank", "default": True},
    {"key": "realm_title", "name_key": "column_realm_title", "default": True},
    {"key": "guild", "name_key": "column_guild", "default": True},
    {"key": "page", "name_key": "column_page", "default": True},
    {"key": "server", "name_key": "column_server", "default": False},
    {"key": "race", "name_key": "column_race", "default": False},
    {"key": "url", "name_key": "column_url", "default": False},
]
```

---

## 🎯 Résultat

### ✅ Toutes les colonnes sont maintenant correctement configurées

1. **Redimensionnement manuel/automatique** : Les 12 colonnes respectent le paramètre `manual_column_resize`
2. **Menu de configuration** : Les 12 colonnes apparaissent dans le bon ordre
3. **Visibilité** : Le mapping column_map est correct pour les 12 colonnes
4. **Cohérence** : L'ordre est identique partout :
   - Headers du TreeView
   - Ajout de lignes (`_add_character_row`)
   - Menu de configuration
   - Mapping de visibilité
   - Redimensionnement

### 📋 Ordre final des colonnes (indices 0-11)

| Index | Clé          | Nom affiché    | Visible par défaut | Redimensionnable |
|-------|--------------|----------------|--------------------|------------------|
| 0     | selection    | ☑             | ✅                 | ✅               |
| 1     | realm        | Royaume        | ✅                 | ✅               |
| 2     | name         | Nom            | ✅                 | Stretch          |
| 3     | class        | Classe         | ✅                 | ✅               |
| 4     | level        | Niveau         | ✅                 | ✅               |
| 5     | realm_rank   | Rang           | ✅                 | ✅               |
| 6     | realm_title  | Titre          | ✅                 | ✅               |
| 7     | guild        | Guilde         | ✅                 | ✅               |
| 8     | page         | Page           | ✅                 | ✅               |
| 9     | server       | Serveur        | ❌                 | ✅               |
| 10    | race         | Race           | ❌                 | ✅               |
| 11    | url          | URL Herald     | ❌                 | ✅               |

---

## 🧪 Tests recommandés

1. **Test de redimensionnement manuel** :
   - Activer "Redimensionnement manuel des colonnes" dans les paramètres
   - Vérifier que TOUTES les colonnes (0-11) sont redimensionnables à la souris
   - Vérifier que la colonne URL (11) se redimensionne correctement

2. **Test de redimensionnement automatique** :
   - Désactiver "Redimensionnement manuel des colonnes"
   - Vérifier que la colonne Name (2) s'étire
   - Vérifier que les autres colonnes (dont URL) s'adaptent au contenu

3. **Test du menu de configuration** :
   - Ouvrir Affichage → Colonnes
   - Vérifier que l'ordre correspond au TreeView
   - Masquer/afficher Class et Level → vérifier que ce sont les bonnes colonnes
   - Masquer/afficher URL → vérifier que la colonne 11 se cache/affiche

4. **Test de persistance** :
   - Configurer les colonnes
   - Redémarrer l'application
   - Vérifier que la configuration est conservée

---

## 📝 Notes techniques

### Structure des colonnes dans le code

```python
# Ordre constant dans tout le code :
# 0  = Selection (case à cocher)
# 1  = Realm (icône)
# 2  = Name (texte, Stretch)
# 3  = Class (texte)
# 4  = Level (nombre)
# 5  = Realm Rank (texte)
# 6  = Realm Title (texte)
# 7  = Guild (texte)
# 8  = Page (nombre)
# 9  = Server (texte)
# 10 = Race (texte)
# 11 = URL (texte)
```

### Modes de redimensionnement QHeaderView

- **Interactive** : L'utilisateur peut redimensionner manuellement
- **ResizeToContents** : Adapte automatiquement au contenu
- **Stretch** : S'étire pour remplir l'espace disponible

---

## 🔄 Impact sur les utilisateurs existants

### Aucun impact négatif attendu

- Les configurations existantes de visibilité restent valides
- Les nouveaux champs (url) seront simplement masqués par défaut
- Le mapping corrigé Class/Level ne nécessite pas de migration (les clés restent identiques)
- Les états d'en-tête sauvegardés (ordre/taille) restent compatibles

### Amélioration immédiate

- Les utilisateurs pourront désormais cacher/afficher la colonne URL Herald
- Le redimensionnement automatique/manuel s'applique maintenant correctement à toutes les colonnes
- L'ordre du menu correspond enfin à celui du TreeView

---

## ✅ Validation

- ✅ Aucune erreur de syntaxe
- ✅ Les 12 colonnes sont définies dans les headers
- ✅ Les 12 colonnes sont ajoutées dans `_add_character_row`
- ✅ Les 12 colonnes sont redimensionnées dans `apply_column_resize_mode`
- ✅ Les 12 colonnes sont mappées dans `apply_column_visibility`
- ✅ Les 12 colonnes apparaissent dans `ColumnsConfigDialog`
- ✅ L'ordre est cohérent partout
