# Menu Action - Documentation

## Vue d'ensemble

Le menu **Action** a été ajouté entre les menus **Fichier** et **Affichage** pour fournir un accès rapide aux fonctionnalités principales de l'application.

## Emplacement

```
┌─────────────────────────────────────┐
│ Fichier │ Action │ Affichage │ Aide │
└─────────────────────────────────────┘
```

## Fonctionnalités

### 📊 Résistances

**Description** : Ouvre le tableau complet des résistances d'armure pour toutes les classes.

**Fonctionnement** :
- Lance l'éditeur de données (`Tools/data_editor.py`) dans un processus séparé
- Affiche automatiquement l'onglet des résistances d'armure
- Permet de consulter les résistances pour les 47 classes des 3 royaumes
- Support multilingue (EN/FR/DE)

**Accès** :
- Menu : `Action > Résistances`
- Raccourci : Aucun (peut être ajouté ultérieurement)

**Cas d'usage** :
- Consulter les résistances d'une classe spécifique
- Comparer les résistances entre plusieurs classes
- Vérifier les valeurs officielles pour optimiser son build

**Traductions** :
- 🇫🇷 Français : "📊 Résistances"
- 🇬🇧 English : "📊 Resistances"
- 🇩🇪 Deutsch : "📊 Widerstände"

---

### 📁 Gestion des armures

**Description** : Ouvre la fenêtre de gestion des armures pour le personnage sélectionné.

**Fonctionnement** :
- Vérifie qu'un personnage est sélectionné dans la liste
- Récupère l'ID du personnage
- Ouvre le dialog `ArmorManagementDialog`
- Permet d'uploader, visualiser et supprimer des fichiers d'armure

**Accès** :
- Menu : `Action > Gestion des armures`
- Alternative : Ouvrir la fiche du personnage → Section Armure → "📁 Gérer les armures"

**Prérequis** :
- Un personnage **doit être sélectionné** dans la liste principale
- Si aucun personnage n'est sélectionné, un message d'information s'affiche :
  ```
  Veuillez sélectionner un personnage dans la liste pour accéder 
  à la gestion de ses armures.
  
  Vous pouvez aussi ouvrir la fiche du personnage et cliquer sur 
  '📁 Gérer les armures'.
  ```

**Cas d'usage** :
- Accès rapide à la gestion des armures depuis n'importe où
- Upload de configurations d'armure
- Consultation rapide des fichiers d'armure existants

**Traductions** :
- 🇫🇷 Français : "📁 Gestion des armures"
- 🇬🇧 English : "📁 Armor Management"
- 🇩🇪 Deutsch : "📁 Rüstungsverwaltung"

---

## Implémentation technique

### Fichiers modifiés

#### `main.py`

**Imports ajoutés** :
```python
from Functions.path_manager import get_base_path
```

**Menu créé** (ligne ~185) :
```python
# Action Menu
action_menu = menubar.addMenu(lang.get("menu_action", default="Action"))

# Action -> Resistances
resistances_action = QAction(lang.get("menu_action_resistances", default="📊 Résistances"), self)
resistances_action.triggered.connect(self.open_resistances_table)
action_menu.addAction(resistances_action)

# Action -> Armor Management
armor_management_action = QAction(lang.get("menu_action_armor_management", default="📁 Gestion des armures"), self)
armor_management_action.triggered.connect(self.open_armor_management_global)
action_menu.addAction(armor_management_action)
```

**Méthode `open_resistances_table()`** :
- Lance `data_editor.py` dans un processus séparé
- Utilise `subprocess.Popen` avec `CREATE_NO_WINDOW` sur Windows
- Gère les erreurs si le fichier est introuvable

**Méthode `open_armor_management_global()`** :
- Vérifie qu'un personnage est sélectionné
- Récupère les données du personnage
- Extrait l'ID du personnage
- Ouvre `ArmorManagementDialog`
- Gère les erreurs (pas de sélection, ID manquant, etc.)

#### Fichiers de langue

**`Language/fr.json`** :
```json
"menu_action": "Action",
"menu_action_resistances": "📊 Résistances",
"menu_action_armor_management": "📁 Gestion des armures",
```

**`Language/en.json`** :
```json
"menu_action": "Action",
"menu_action_resistances": "📊 Resistances",
"menu_action_armor_management": "📁 Armor Management",
```

**`Language/de.json`** :
```json
"menu_action": "Aktion",
"menu_action_resistances": "📊 Widerstände",
"menu_action_armor_management": "📁 Rüstungsverwaltung",
```

---

## Gestion des erreurs

### Résistances

**Erreur** : Fichier `data_editor.py` introuvable
```
Message : Le fichier data_editor.py est introuvable à l'emplacement :
          C:\...\Tools\data_editor.py
Type    : QMessageBox.warning
```

**Erreur** : Échec du lancement
```
Message : Impossible de lancer l'éditeur de données :
          [détails de l'exception]
Type    : QMessageBox.critical
```

### Gestion des armures

**Info** : Aucun personnage sélectionné
```
Message : Veuillez sélectionner un personnage dans la liste pour 
          accéder à la gestion de ses armures.
Type    : QMessageBox.information
```

**Erreur** : Données du personnage introuvables
```
Message : Impossible de trouver les données du personnage '[nom]'.
Type    : QMessageBox.warning
```

**Erreur** : ID du personnage manquant
```
Message : Impossible de déterminer l'ID du personnage.
Type    : QMessageBox.warning
```

---

## Logging

Toutes les actions sont loggées :

```python
# Ouverture du tableau des résistances
logging.info("Opening armor resistances table from menu.")
logging.info("Data editor launched successfully.")

# Ouverture de la gestion des armures
logging.info("Armor management requested from menu.")
```

---

## Tests recommandés

### Test 1 : Menu Action visible
1. Lancer l'application
2. Vérifier que le menu "Action" apparaît entre "Fichier" et "Affichage"
3. Cliquer sur "Action" → vérifier les 2 options

### Test 2 : Résistances
1. Menu > Action > Résistances
2. Vérifier que `data_editor.py` se lance
3. Vérifier que l'onglet "Armor Resistances" est visible

### Test 3 : Gestion des armures (sans sélection)
1. S'assurer qu'aucun personnage n'est sélectionné
2. Menu > Action > Gestion des armures
3. Vérifier le message d'information

### Test 4 : Gestion des armures (avec sélection)
1. Sélectionner un personnage
2. Menu > Action > Gestion des armures
3. Vérifier que le dialog s'ouvre avec l'ID correct

### Test 5 : Multilingue
1. Changer la langue (FR, EN, DE)
2. Vérifier que les textes du menu sont traduits
3. Vérifier les messages d'erreur

---

## Évolutions futures possibles

- [ ] **Raccourcis clavier** : Ajouter Ctrl+R pour Résistances, Ctrl+M pour Armures
- [ ] **Icônes personnalisées** : Remplacer les émojis par des icônes SVG
- [ ] **Menu contextuel** : Ajouter "Gestion des armures" dans le clic droit sur un personnage
- [ ] **Barre d'outils** : Ajouter des boutons rapides pour ces actions
- [ ] **Récents** : Liste des derniers fichiers d'armure consultés

---

**Version** : 0.105  
**Date** : Octobre 2025  
**Auteur** : DAOC Character Manager Team
