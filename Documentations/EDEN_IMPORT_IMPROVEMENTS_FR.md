# Améliorations de l'import Eden Herald

**Date**: 31 octobre 2025  
**Version**: 0.106  
**Statut**: ✅ Implémenté

## Vue d'ensemble

Ce document décrit les améliorations apportées au système d'import de personnages depuis le site Eden Herald.

## Modifications apportées

### 1. Assignation automatique de la saison par défaut

#### Description
Lors de l'import d'un personnage depuis le site Eden Herald, celui-ci est désormais automatiquement assigné à la saison définie par défaut dans le fichier de configuration.

#### Implémentation

**Fichier modifié**: `UI/dialogs.py`

**Méthode modifiée**: `_import_characters()`

```python
# Récupérer la saison par défaut depuis la configuration
default_season = config.get('default_season', 'S1')

# Créer le dictionnaire de données du personnage
character_data = {
    'name': name,
    'class': char_class,
    'race': char_data.get('race', ''),
    'realm': realm,
    'guild': char_data.get('guild', ''),
    'level': char_data.get('level', '50'),
    'realm_rank': char_data.get('realm_rank', ''),
    'realm_level': char_data.get('realm_level', ''),
    'realm_points': char_data.get('realm_points', '0'),
    'url': char_data.get('url', ''),
    'server': 'Eden',
    'season': default_season,  # ← Nouveau champ
    'mlevel': '0',
    'clevel': '0',
    'notes': f"Importé depuis le Herald le {datetime.now().strftime('%Y-%m-%d %H:%M')}"
}
```

#### Configuration
La saison par défaut est définie dans `Configuration/config.json` :

```json
{
    "seasons": ["S1", "S2", "S3"],
    "default_season": "S2"
}
```

#### Comportement
- Le personnage importé est automatiquement placé dans le dossier de la saison configurée
- Si `default_season` n'est pas défini, la valeur par défaut est "S1"
- L'utilisateur peut modifier la saison par défaut via l'interface de configuration

---

### 2. Menu contextuel pour import rapide

#### Description
Ajout d'un menu contextuel (clic droit) sur la table de résultats de recherche Herald permettant d'importer directement un personnage spécifique sans passer par les boutons en bas de page.

#### Implémentation

**Fichier modifié**: `UI/dialogs.py`

**Classe modifiée**: `HeraldSearchDialog`

##### Activation du menu contextuel

Dans la méthode `__init__()` :

```python
self.results_table = QTableWidget()
self.results_table.setMinimumHeight(250)
self.results_table.setAlternatingRowColors(True)
self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
self.results_table.setSelectionMode(QTableWidget.SingleSelection)
self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
self.results_table.customContextMenuRequested.connect(self.show_context_menu)
```

##### Nouvelle méthode : `show_context_menu()`

```python
def show_context_menu(self, position):
    """Affiche le menu contextuel sur la table de résultats"""
    if not self.current_characters:
        return
    
    # Récupérer la ligne sélectionnée
    row = self.results_table.rowAt(position.y())
    if row < 0:
        return
    
    # Créer le menu contextuel
    context_menu = QMenu(self)
    
    # Action d'import
    import_action = context_menu.addAction("📥 Importer ce personnage")
    import_action.triggered.connect(lambda: self._import_single_character(row))
    
    # Afficher le menu à la position du curseur
    context_menu.exec_(self.results_table.viewport().mapToGlobal(position))
```

##### Nouvelle méthode : `_import_single_character()`

```python
def _import_single_character(self, row):
    """Importe un personnage spécifique depuis la table"""
    if row < 0 or row >= len(self.current_characters):
        return
    
    char_data = self.current_characters[row]
    
    # Confirmer l'import
    char_name = char_data.get('clean_name', char_data.get('name', ''))
    reply = QMessageBox.question(
        self,
        "Confirmer l'import",
        f"Voulez-vous importer le personnage '{char_name}' ?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        self._import_characters([char_data])
```

##### Import ajouté

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel, 
    QPushButton, QLineEdit, QComboBox, QCheckBox, QSlider, QMessageBox,
    QDialogButtonBox, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget, QTextEdit, QApplication, QProgressBar, QMenu  # ← QMenu ajouté
)
```

#### Utilisation

1. **Rechercher un personnage** sur le Herald via la fenêtre de recherche
2. **Clic droit** sur une ligne de résultat
3. **Sélectionner** "📥 Importer ce personnage" dans le menu contextuel
4. **Confirmer** l'import dans la boîte de dialogue

#### Avantages

- ✅ **Rapidité** : Import direct sans cocher puis cliquer sur "Importer sélection"
- ✅ **Ergonomie** : Interaction naturelle (clic droit = actions contextuelles)
- ✅ **Confirmation** : Dialogue de confirmation pour éviter les imports accidentels
- ✅ **Compatibilité** : Les boutons d'import en bas de page restent fonctionnels

---

## Workflow complet d'import

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECHERCHE SUR HERALD                          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AFFICHAGE DES RÉSULTATS                         │
│                                                                   │
│  Ligne 1: [☑] 🔴 Alaric    Paladin    Avalonian ...              │
│  Ligne 2: [ ] 🔵 Bjorn     Berserker  Norse ...                  │
│  Ligne 3: [ ] 🟢 Cian      Warden     Celt ...                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                 ┌──────────┴───────────┐
                 │                      │
                 ▼                      ▼
        ┌────────────────┐    ┌────────────────┐
        │  CLIC DROIT    │    │  COCHER +      │
        │  sur ligne     │    │  BOUTON        │
        └────────────────┘    └────────────────┘
                 │                      │
                 ▼                      ▼
        ┌────────────────┐    ┌────────────────┐
        │ Menu contextuel│    │ Importer       │
        │ "📥 Importer"  │    │ sélection      │
        └────────────────┘    └────────────────┘
                 │                      │
                 └──────────┬───────────┘
                            ▼
                  ┌─────────────────┐
                  │  Confirmation   │
                  │  utilisateur    │
                  └─────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ _import_        │
                  │ characters()    │
                  └─────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  Récupération default_season  │
            │  depuis config.json           │
            └───────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  Création character_data      │
            │  avec 'season': default_season│
            └───────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  save_character()             │
            │  → Characters/{season}/{name} │
            └───────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  Refresh interface principale │
            └───────────────────────────────┘
                            │
                            ▼
                    ✅ Import terminé
```

## Impact sur l'utilisateur

### Avant
1. Rechercher un personnage
2. Cocher la case du personnage
3. Cliquer sur "Importer sélection"
4. Confirmer
5. ⚠️ Le personnage n'avait pas de saison définie

### Après
1. Rechercher un personnage
2. **Option A** : Clic droit → "Importer ce personnage"
3. **Option B** : Cocher → "Importer sélection"
4. Confirmer
5. ✅ Le personnage est automatiquement placé dans la saison par défaut

## Configuration requise

### Fichier de configuration

Le fichier `Configuration/config.json` doit contenir :

```json
{
    "seasons": ["S1", "S2", "S3"],
    "default_season": "S2"
}
```

### Valeurs par défaut

Si `default_season` n'est pas défini dans la configuration :
- Valeur par défaut : `"S1"`
- Défini dans `Functions/config_manager.py` :

```python
self.config = {
    ...
    "seasons": ["S1", "S2", "S3"],
    "default_season": "S1",
    ...
}
```

## Tests recommandés

### Test 1 : Saison par défaut
1. Définir `default_season: "S2"` dans `config.json`
2. Importer un personnage depuis Herald
3. Vérifier que le fichier est créé dans `Characters/S2/`
4. Vérifier que la colonne "Saison" affiche "S2"

### Test 2 : Menu contextuel
1. Rechercher un personnage sur Herald
2. Clic droit sur une ligne de résultat
3. Vérifier que le menu contextuel s'affiche
4. Cliquer sur "📥 Importer ce personnage"
5. Confirmer l'import
6. Vérifier que le personnage est bien importé

### Test 3 : Import multiple
1. Rechercher un personnage
2. Cocher plusieurs lignes
3. Cliquer sur "Importer sélection"
4. Vérifier que tous les personnages sont importés dans la saison par défaut

### Test 4 : Changement de saison
1. Modifier `default_season` dans `config.json` (ex: "S3")
2. Redémarrer l'application
3. Importer un personnage
4. Vérifier qu'il est bien dans `Characters/S3/`

## Fichiers modifiés

| Fichier | Lignes modifiées | Description |
|---------|------------------|-------------|
| `UI/dialogs.py` | +50 lignes | - Ajout de `QMenu` dans les imports<br>- Activation du menu contextuel sur `results_table`<br>- Méthode `show_context_menu()`<br>- Méthode `_import_single_character()`<br>- Ajout de `season: default_season` dans `character_data` |

## Compatibilité

- ✅ **Version Python** : 3.13.9
- ✅ **PySide6** : 6.6.0+
- ✅ **Rétrocompatibilité** : Maintenue avec les fonctionnalités existantes
- ✅ **Configuration** : Utilise les valeurs par défaut si non définies

## Notes de développement

### Ordre d'exécution de l'import

1. **Validation** : Vérification que le personnage n'existe pas déjà
2. **Récupération** : `default_season = config.get('default_season', 'S1')`
3. **Création** : Construction du dictionnaire `character_data`
4. **Sauvegarde** : `save_character(character_data)` → Crée le fichier JSON dans `Characters/{season}/{name}.json`
5. **Refresh** : `tree_manager.refresh_character_list()` → Met à jour l'affichage

### Gestion des erreurs

- Si `default_season` n'existe pas dans la configuration → Utilise "S1"
- Si le personnage existe déjà → Message d'erreur + pas d'import
- Si l'import échoue → Message d'erreur avec détails

### Performance

- ✅ Pas d'impact sur les performances (lecture simple d'une valeur de config)
- ✅ Menu contextuel léger (créé à la demande)
- ✅ Pas de requête réseau supplémentaire

## Support multilingue

Les nouveaux messages peuvent être traduits dans `Language/*.json` :

### Français (`fr.json`)
```json
{
    "herald_import_single": "Importer ce personnage",
    "herald_confirm_import": "Confirmer l'import",
    "herald_confirm_import_msg": "Voulez-vous importer le personnage '{0}' ?"
}
```

### Anglais (`en.json`)
```json
{
    "herald_import_single": "Import this character",
    "herald_confirm_import": "Confirm import",
    "herald_confirm_import_msg": "Do you want to import the character '{0}'?"
}
```

### Allemand (`de.json`)
```json
{
    "herald_import_single": "Diesen Charakter importieren",
    "herald_confirm_import": "Import bestätigen",
    "herald_confirm_import_msg": "Möchten Sie den Charakter '{0}' importieren?"
}
```

**Note** : Actuellement les messages sont en dur en français. Une future amélioration serait d'utiliser le système de traduction `lang()`.

## Améliorations futures possibles

1. **Internationalisation** : Utiliser `lang()` pour les messages du menu contextuel
2. **Icône de saison** : Afficher l'icône de la saison par défaut dans la notification d'import
3. **Sélection de saison** : Permettre de choisir la saison lors de l'import (combo box dans le dialogue)
4. **Import en masse** : Clic droit multi-ligne pour importer plusieurs personnages d'un coup
5. **Prévisualisation** : Afficher les détails du personnage avant l'import via clic droit

## Historique des versions

| Version | Date | Modifications |
|---------|------|---------------|
| 0.106 | 31/10/2025 | - Ajout de la saison par défaut à l'import<br>- Ajout du menu contextuel pour import rapide |

## Auteur

Développé pour DAOC Character Management  
Branche : `105_eden_scraper`

---

**Statut** : ✅ Implémenté et testé  
**Documentation mise à jour** : Oui  
**Tests unitaires** : À créer (recommandé)
