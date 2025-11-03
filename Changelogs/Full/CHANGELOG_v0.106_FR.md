# CHANGELOG v0.106 - Système de Logging, Sauvegarde Cookies & Améliorations

**Date** : 2025-11-01  
**Version** : 0.106

---

## 🔧 Nouveau Système de Logging

### Format unifié avec ACTION

- **Avant** : Format inconsistant, difficile à filtrer et analyser les logs
- **Maintenant** : Format standardisé `LOGGER - LEVEL - ACTION - MESSAGE`
- **Exemple** : `2025-11-01 14:30:00 - BACKUP - INFO - INIT - BackupManager initialized`

**Avantages** :
- Filtrage facile par logger (BACKUP, EDEN, UI, CHARACTER, ROOT)
- Actions claires pour chaque opération
- Traçabilité complète du flux d'exécution
- Compatible avec outils d'analyse de logs

**Implémentation** :
- Nouveau formatter `ContextualFormatter` dans `logging_manager.py`
- Gestion de l'action : Utilise `extra={"action": "VALUE"}` dans les logs
- Fallback : Affiche "-" si aucune action n'est fournie
- Fonction helper : `log_with_action(logger, level, message, action="XXX")`

### Logger BACKUP - Module de sauvegarde

- **Fichiers modifiés** : `backup_manager.py`, `migration_manager.py`
- **46+ logs tagués** avec actions claires

**Actions standardisées** :
- `INIT` - Initialisation du BackupManager
- `DIRECTORY` - Création/vérification du répertoire de backup
- `CHECK` - Vérification si un backup est nécessaire aujourd'hui
- `STARTUP` - Backup automatique au démarrage
- `TRIGGER` - Déclenchement automatique de backup
- `AUTO_TRIGGER` - Démarrage auto-backup
- `AUTO_PROCEED` - Poursuite du backup auto
- `AUTO_BLOCKED` - Backup auto bloqué (déjà fait)
- `MANUAL_TRIGGER` - Backup manuel déclenché
- `ZIP` - Compression ZIP en cours
- `RETENTION` - Gestion de la rétention (suppression anciens backups)
- `SCAN` - Scan des backups existants
- `DELETE` - Suppression d'un backup
- `INFO` - Information sur les backups
- `RESTORE` - Restauration d'un backup
- `ERROR` - Erreurs générales

**Niveaux** : DEBUG (détails), INFO (progression), WARNING (alertes), ERROR (erreurs)

**Traçabilité** : Logs détaillés pour chaque étape du processus de backup

### Logger EDEN - Scraper Herald

- **Fichier** : `eden_scraper.py`
- **Actions** : INIT, COOKIES, SCRAPE, SEARCH, PARSE, TEST, CLOSE, CLEANUP, ERROR
- **Tous les logs** utilisent maintenant `extra={"action": "XXX"}`

---

## 🛠️ Log Source Editor - Nouvel Outil de Développement

### Vue d'ensemble

- **Fichier** : `Tools/log_source_editor.py` (975 lignes)
- **Purpose** : Éditer les logs directement dans le code source AVANT compilation
- **Framework** : PySide6 (Qt6) avec interface graphique complète

### Scanner de code source

- **Technologie** : QThread asynchrone pour ne pas bloquer l'UI
- **Pattern 1** : Détecte `logger.info()`, `self.logger.debug()`, `module_logger.warning()`
- **Pattern 2** : Détecte `log_with_action(logger, "info", "message", action="TEST")`

**Détection intelligente** :
- Extraction du logger name depuis le nom de fichier
- Parsing de `get_logger(LOGGER_XXX)`
- Parsing de `setup_logger("LOGGER_NAME")`

**Parsing** :
- Extraction de l'action depuis `action="XXX"` ou `extra={"action": "XXX"}`
- Extraction du message (supporte f-strings, strings normales, concaténations)
- Récupération du niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Interface utilisateur

**Layout principal** :
- **Gauche** : Table des logs trouvés (read-only)
  - Colonnes : File, Line, Logger, Level, Action, Message, Modified
  - Protection : `setEditTriggers(QTableWidget.NoEditTriggers)`
- **Droite** : Panneau d'édition
  - File/Line/Logger/Level (affichage)
  - Action : ComboBox éditable avec historique
  - Message : QTextEdit multi-ligne
  - Code original : QTextEdit read-only
  - Boutons : Appliquer, Réinitialiser

**Toolbar** :
- 🔍 Scanner le projet
- Filtres : Logger (dropdown), Level (dropdown), Modifiés uniquement, Recherche texte
- Statistiques : `📊 X/Y logs | ✏️ Z modifiés`

### Fonctionnalités clés

**1. ComboBox d'actions avec historique**
- Pré-remplie avec toutes les actions trouvées dans le scan
- Éditable : permet de taper de nouvelles actions
- Auto-complétion : suggestions basées sur l'historique
- Ajout dynamique : nouvelles actions ajoutées automatiquement à la liste
- Politique : `NoInsert` pour contrôler manuellement l'ajout

**2. Raccourcis clavier**
- `Enter` dans le champ Action → Applique les modifications
- `Ctrl+Enter` dans le champ Message → Applique les modifications
- Navigation avec flèches dans la table

**3. Système de filtrage**
- **Par logger** : BACKUP, EDEN, UI, CHARACTER, ROOT, Tous
- **Par level** : DEBUG, INFO, WARNING, ERROR, CRITICAL, Tous
- **Par statut** : Tous, Modifiés uniquement
- **Par texte** : Recherche dans les messages
- Statistiques mises à jour en temps réel

**4. Sauvegarde dans les fichiers**
- Modification directe des fichiers source Python
- Préservation de l'indentation originale
- Support des f-strings et formats complexes
- Gestion de `self.logger` et `module_logger`
- Remplacement sûr ligne par ligne

**5. Mémorisation du dernier projet**
- Configuration JSON : `Tools/log_editor_config.json`
- Chargement automatique au démarrage (délai 100ms)
- Sélection par défaut dans le dialogue
- Titre de fenêtre : `🔧 Log Source Editor - NomProjet (X logs)`

**6. Protections et validations**
- Flag `_updating` : empêche les boucles de mise à jour récursives
- `blockSignals(True)` : pendant les mises à jour de table
- Comparaison `__eq__` et `__hash__` : évite recharger le même log
- Vérification avant sauvegarde : détecte les fichiers non modifiés

### Workflow utilisateur

1. **Lancement** : `.venv\Scripts\python.exe Tools\log_source_editor.py`
2. **Scan automatique** : Le dernier projet se charge automatiquement
3. **Filtrage** : Sélectionner "Logger: BACKUP" pour voir les logs du module backup
4. **Sélection** : Cliquer sur un log dans la table
5. **Édition** :
   - Choisir une action dans le dropdown ou taper une nouvelle
   - Modifier le message si nécessaire
6. **Application** : Appuyer sur Enter ou cliquer "Appliquer"
7. **Répétition** : Naviguer avec ↓ pour le log suivant
8. **Sauvegarde** : Cliquer "💾 Sauvegarder" pour écrire dans les fichiers source

### Statistiques affichées (Après scan)

```
✅ Scan terminé : 144 logs trouvés

📊 Par Logger :
   BACKUP: 46
   EDEN: 52
   ROOT: 30
   UI: 16

📊 Par Level :
   INFO: 80
   DEBUG: 40
   WARNING: 15
   ERROR: 9

📊 Actions :
   • Actions trouvées: CHECK, DELETE, DIRECTORY, ERROR, INIT, PARSE, RETENTION, RESTORE, SCAN, SCRAPE, TRIGGER, ZIP
   • Avec action: 120
   • Sans action: 24
```

---

## 🐛 Corrections

### Chemin de sauvegarde des cookies Eden (PyInstaller fix)

- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut
- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller
- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale
- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`
- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale
- **Fichier modifié** : `Functions/cookie_manager.py`

### Configuration des colonnes corrigée

- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)
- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration
- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente

**Solution** :
- `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement
- Ordre du menu de configuration aligné avec le TreeView (Class avant Level)
- Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL

**Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité

**Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`

### 🧬 Authentification Herald - Détection Simplifiée & Fiable

- **Problème** : Détection d'authentification avec multiple critères peu fiables
- **Cause** : Cookies invalides ou technique de détection inconsistante
- **Solution** : Détection basée sur un seul critère définitif

**Logique de détection** :
- Message d'erreur `'The requested page "herald" is not available.'` = NOT CONNECTED
- Absence du message d'erreur = CONNECTED (peut scraper les données)

**Cohérence** :
- Logique identique entre `test_eden_connection()` (cookie_manager.py) et `load_cookies()` (eden_scraper.py)
- Cookies invalidés correctement détectés et signalés
- Tests validés avec environ 58 résultats de recherche Herald

**Fichiers modifiés** : `Functions/cookie_manager.py`, `Functions/eden_scraper.py`

---

## ✨ Améliorations

### Auto-update lors de l'import de personnages

- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"
- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄

**Données conservées** : name, realm, season, server, données personnalisées

**Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes

**Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs

**Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald

**Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)

### Dossier des cookies Herald configurable

- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"
- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden
- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier
- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)
- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`
- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`
- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)

**Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

### Debug Window améliorée

- **Nouveau filtre** : Dropdown pour filtrer par logger
- **Options** : Tous, BACKUP, EDEN, UI, CHARACTER, ROOT

**Fichier modifié** : `UI/debug_window.py`

### Unification des labels des répertoires

- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")
- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"

**Labels** :
- Répertoire des personnages
- Répertoire de configuration
- Répertoire des logs
- Répertoire des armures
- Répertoire des cookies Herald

**Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)

**Localization** : Traductions complètes en FR, EN, DE

**Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Affichage du début des chemins

- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)
- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins
- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")

**Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()`

### Système de diagnostic robuste pour arrêts inattendus

- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées
- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation
- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées
- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs
- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête
- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt

**Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`

### 🎛️ Contrôle des Boutons Herald

- **Boutons** : "Actualiser" et "Recherche Herald" automatiquement désactivés
- **Condition de désactivation** :
  - Quand aucun cookie n'est détecté
  - Quand les cookies sont expirés
- **Synchronisation** : État du bouton synchronisé avec le statut de connexion
- **Message utilisateur** : Clair - "Aucun cookie détecté"

**Logique** : Si `cookie_exists()` retourne False ou cookies invalides → boutons désactivés

**Fichier modifié** : `UI/ui_manager.py` - Fonction `update_eden_status()`

### Système de sauvegarde automatique lors des mises à jour de personnages

- **Problème** : Lors de la modification d'un personnage existant (rang, infos, armure, compétences) ou lors d'une mise à jour Herald, aucune sauvegarde n'était déclenchée
- **Solution** : Intégration de backups automatiques avec raison descriptive à tous les points de modification

**Points couverts** :
- Mise à jour Herald après confirmation (main.py)
- Modification de rang automatique (auto_apply_rank)
- Modification de rang manuelle (apply_rank_manual)
- Modification d'infos de base (save_basic_info)
- Modification d'armure/compétences (CharacterSheetWindow)
- Import/mise à jour massive (import dialog)

**Type de sauvegarde** : `backup_characters_force(reason="Update")` → MANUEL (bypass du daily limit)

**Filename** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`

**Logs générés** : Chaque modification génère des logs visibles avec tag `[BACKUP_TRIGGER]` :

```
[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip
```

**Résultat** : Chaque modification de personnage crée automatiquement une sauvegarde avec raison descriptive et logs visibles

**Fichiers modifiés** : `main.py`, `UI/dialogs.py`

**Documentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` mise à jour avec nouveaux scénarios

---

## 🎨 Améliorations Interface

### Configuration des colonnes

- Toutes les 12 colonnes (0-11) correctement configurables
- Redimensionnement et visibilité fonctionnels
- Menu de configuration aligné avec le TreeView

### Labels uniformisés

- Tous les chemins de dossiers commencent par "Répertoire"
- Suppression des deux-points inutiles à la fin
- Interface cohérente et professionnelle

### Affichage optimisé des chemins

- Début des chemins visibles (pas "...")
- Curseur au début des champs
- Meilleure lisibilité pour l'utilisateur

### Tri par royaume

**Problème** : La colonne Realm (royaume) ne permettait pas le tri en cliquant sur l'en-tête

**Solution** :
- Ajout d'un `RealmSortProxyModel` personnalisé
- Implémentation de `lessThan()` pour la colonne 1 (Realm)
- Utilisation de `Qt.UserRole + 2` pour stocker les données de tri
- Le proxy intercepte le tri et utilise le nom du royaume

**Fichiers modifiés** :
- `Functions/tree_manager.py` : Ajout de la classe `RealmSortProxyModel`
- Import de `QSortFilterProxyModel` depuis `PySide6.QtCore`
- Configuration du proxy dans `__init__()` : `self.proxy_model.setSourceModel(self.model)`

**Résultat** :
- ✅ Tri alphabétique fonctionnel (Albion → Hibernia → Midgard)
- ✅ Icônes du royaume toujours affichées (sans texte)
- ✅ Delegate existant préservé (`CenterIconDelegate`)

### Largeur colonne URL Herald

**Problème** : Le bouton Herald était écrasé dans la colonne URL trop étroite

**Solution** :
- Largeur minimale de 120px définie pour la colonne 11 (URL)
- Appliquée dans `apply_column_resize_mode()` après `ResizeToContents`

**Code** :
```python
# Définir une largeur minimale pour la colonne URL (11)
self.tree_view.setColumnWidth(11, 120)
```

**Résultat** :
- ✅ Bouton Herald parfaitement visible
- ✅ Espace confortable pour l'interaction
- ✅ Pas d'impact sur les autres colonnes

### Mappage des indices du proxy model pour les opérations sur personnages

**Problème** : Après un tri par royaume (ou toute colonne), les opérations sur les personnages affectaient le mauvais personnage
- Suppression affichait le nom d'un autre personnage
- Ouverture d'une fiche ouvrait le mauvais personnage
- Mise à jour Herald ciblait le mauvais personnage

**Cause racine** : Avec `QSortFilterProxyModel`, les indices de la TreeView (vue triée) ne correspondent pas aux indices du modèle source (stockage). Les opérations utilisaient les indices du proxy directement sur le modèle source.

**Solution** : Utiliser `mapToSource()` pour traduire les indices du proxy vers les indices du modèle source avant d'accéder aux données du modèle

**Méthodes modifiées** :
- `get_selected_character()` dans `tree_manager.py` - Utilisée par supprimer, renommer, dupliquer
- `open_character_sheet()` dans `character_actions_manager.py` - Double-clic pour ouvrir la fiche
- `update_character_from_herald()` dans `main.py` - Menu clic-droit pour mettre à jour depuis Herald

**Exemple de code** :
```python
# Avant (incorrect avec proxy model) :
row = indexes[0].row()
name_item = self.model.item(row, 2)

# Après (correct avec proxy model) :
proxy_index = indexes[0]
source_index = self.proxy_model.mapToSource(proxy_index)
row = source_index.row()
name_item = self.model.item(row, 2)
```

**Résultat** :
- ✅ Suppression confirme le bon personnage
- ✅ Fiche ouvre le bon personnage
- ✅ Mise à jour Herald cible le bon personnage
- ✅ Toutes les opérations fonctionnent correctement avec n'importe quel tri

### Comportement du bouton Enregistrer de la fiche personnage

**Amélioration** : Le bouton Enregistrer ne ferme plus la fenêtre de la fiche automatiquement

**Avant** : Cliquer sur Enregistrer sauvegardait les infos et fermait immédiatement la fenêtre

**Maintenant** : Cliquer sur Enregistrer sauvegarde les infos et garde la fenêtre ouverte, permettant de continuer à éditer d'autres champs

**Cas d'usage** : Les utilisateurs peuvent maintenant modifier plusieurs champs et les enregistrer séquentiellement sans rouvrir la fiche à chaque fois

**Résultat** :
- ✅ Flux de travail plus efficace pour plusieurs modifications
- ✅ Les utilisateurs ferment explicitement la fenêtre avec le bouton Fermer
- ✅ Meilleur contrôle utilisateur sur la session d'édition

### Design uniforme des boutons Herald

**Amélioration** : Les deux boutons Herald (Ouvrir dans le navigateur et Mettre à jour depuis Herald) ont maintenant une taille et un layout uniformes

**Modifications** :
- Distribution égale de la largeur utilisant `setStretch(1, 1)` pour les deux boutons
- Hauteur minimale cohérente de 30px pour les deux boutons
- Apparence plus équilibrée et professionnelle

**Résultat** :
- ✅ Dimensionnement cohérent des boutons dans la section Herald
- ✅ Meilleur design visuel et symétrie
- ✅ Cohérence améliorée de l'interface utilisateur

### Améliorations du layout de la fenêtre principale - Sections Herald et Monnaie

**Amélioration** : Redesign de la section de statut inférieure de la fenêtre principale pour une meilleure ergonomie

**Modifications** :
- Division de la section inférieure en deux colonnes égales :
  - **Colonne gauche** : Section "Statut Eden Herald" (réduite à 50% de la largeur)
  - **Colonne droite** : Nouvelle section "Monnaie" avec placeholder "🔜 Feature à venir"
- Réorganisation des boutons Herald :
  - Changement du layout vertical au horizontal
  - Réduits au format emoji + texte (🔄 Actualiser, 🔍 Recherche, ⚙️ Gérer)
  - Les trois boutons de même taille (750px largeur × 35px hauteur)
  - Compact avec police réduite et espacement minimal
- Dimensions optimisées :
  - Hauteur : 35px (plus compact qu'avant)
  - Largeur : 750px par bouton (format large pour meilleure visibilité)
  - Tous les éléments alignés horizontalement pour cohérence

**Résultat** :
- ✅ Meilleure ergonomie et layout de la fenêtre principale
- ✅ Utilisation optimisée de l'espace
- ✅ Tous les boutons Herald de même taille et visuellement équilibrés
- ✅ Préparation pour la future fonctionnalité Monnaie
- ✅ Interface plus compacte et efficace

---

## 🧹 Nettoyage du Répertoire

- **Suppression de 13 scripts debug temporaires**
- **Suppression de 3 fichiers HTML de débogage**
- **Repository clean et maintainable**
- **Optimisation des performances**

**Fichiers supprimés** :
- analyze_search_structure.py
- debug_comparison.py
- debug_herald_content.py
- debug_search_html.py
- debug_test_connection.py
- save_search_html.py
- show_cookies.py
- test_direct_search.py
- test_full_flow.py
- test_herald_detection.py
- test_identical_flow.py
- test_load_cookies_msg.py
- test_simple.py
- debug_herald_page.html
- debug_test_connection.html
- search_result.html

---

## 📚 Documentation

### Nettoyage et réorganisation du système CHANGELOGs

- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)
- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage

**Structure créée** :
- `Changelogs/Full/` : CHANGELOGs détaillés (~200+ lignes) pour v0.106, v0.104 et versions antérieures
- `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les versions (v0.1 à v0.106)
- Support tri-lingual : FR, EN, DE pour chaque fichier

**Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions

**Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/`

**Fichiers créés** : 27+ fichiers au total (6 Full + 21 Simple)

**Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue

---

## 📊 Statistiques

- **Lignes de code ajoutées** : ~1000+ (log_source_editor.py: 975 lignes)
- **Fichiers modifiés** : 12 fichiers
- **Fichiers créés** : 2 fichiers (log_source_editor.py, log_editor_config.json)
- **Logs tagués** : 46+ dans backup_manager.py, 52+ dans eden_scraper.py
- **Actions standardisées** : 20+ actions différentes
- **Tests effectués** : Scanner, filtrage, édition, sauvegarde validés

---

## 🔗 Fichiers Modifiés

- `main.py`
- `UI/dialogs.py`
- `UI/ui_manager.py`
- `UI/debug_window.py`
- `Functions/cookie_manager.py`
- `Functions/eden_scraper.py`
- `Functions/tree_manager.py`
- `Functions/logging_manager.py`
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`
- `Documentations/BACKUP_DEBUG_GUIDE.md`

---

## 📊 Impact Général

✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant

✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement

✅ **Gestion propre des erreurs avec rapport détaillé** - Nombre de créations, mises à jour et erreurs

✅ **Flexibilité accrue pour la gestion des cookies** - Chemins personnalisables pour le scraping

✅ **Portabilité complète de l'application** - Configuration centralisée sans dépendances __file__

✅ **Capacité à diagnostiquer les arrêts inattendus** - Logs détaillés de tous les événements critiques

✅ **Interface cohérente et consistante** - Labels uniformisés et affichage optimal des chemins

✅ **Sauvegarde automatique lors des modifications** - Chaque modification de personnage crée une sauvegarde avec logs visibles

---

## 🔄 Migration

**Aucune migration requise** - Cette version est 100% rétrocompatible avec v0.105

---

## 🐛 Bugs connus

Aucun bug connu à ce jour.

---

## 📝 Notes de développement

- Le Log Source Editor est un outil de développement, pas inclus dans l'application principale
- L'outil facilite grandement la maintenance et l'amélioration du système de logging
- Le format de logging unifié permet une meilleure analyse et debugging
- Les actions standardisées facilitent le filtrage et la recherche dans les logs
