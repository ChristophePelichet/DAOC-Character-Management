# CHANGELOG v0.106 - Système de Logging & Outils de Développement# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update



**Date** : 2025-11-01  

**Version** : 0.106

**Date** : 2025-11-01  

---

**Version** : 0.106

## 🔧 Nouveau Système de Logging

**Date** : 2025-11-01  **Date** : 2025-11-01  

### Format unifié avec ACTION

## 🐛 Corrections

- **Avant** : Format inconsistant, difficile à filtrer et analyser les logs

- **Maintenant** : Format standardisé `LOGGER - LEVEL - ACTION - MESSAGE`**Version** : 0.106**Version** : 0.106

- **Exemple** : `2025-11-01 14:30:00 - BACKUP - INFO - INIT - BackupManager initialized`

- **Avantages** :### Chemin de sauvegarde des cookies Eden (PyInstaller fix)

  * Filtrage facile par logger (BACKUP, EDEN, UI, CHARACTER, ROOT)

  * Actions claires pour chaque opération- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut

  * Traçabilité complète du flux d'exécution

  * Compatible avec outils d'analyse de logs- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller



### ContextualFormatter- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale## 🐛 Corrections## 🐛 Corrections



- **Implémentation** : Nouveau formatter dans `logging_manager.py`- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`

- **Gestion de l'action** : Utilise `extra={"action": "VALUE"}` dans les logs

- **Fallback** : Affiche "-" si aucune action n'est fournie- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale

- **Fonction helper** : `log_with_action(logger, level, message, action="XXX")`

- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)

### Logger BACKUP - Module de sauvegarde

### Chemin de sauvegarde des cookies Eden (PyInstaller fix)### Chemin de sauvegarde des cookies Eden (PyInstaller fix)

- **Fichiers modifiés** : `backup_manager.py`, `migration_manager.py`

- **46+ logs tagués** avec actions claires### Configuration des colonnes corrigée

- **Actions standardisées** :

  * `INIT` - Initialisation du BackupManager- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut

  * `DIRECTORY` - Création/vérification du répertoire de backup

  * `CHECK` - Vérification si un backup est nécessaire aujourd'hui- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration

  * `STARTUP` - Backup automatique au démarrage

  * `TRIGGER` - Déclenchement automatique de backup- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller

  * `AUTO_TRIGGER` - Démarrage auto-backup

  * `AUTO_PROCEED` - Poursuite du backup auto- **Solution** : 

  * `AUTO_BLOCKED` - Backup auto bloqué (déjà fait)

  * `MANUAL_TRIGGER` - Backup manuel déclenché  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale

  * `ZIP` - Compression ZIP en cours

  * `RETENTION` - Gestion de la rétention (suppression anciens backups)  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)

  * `SCAN` - Scan des backups existants

  * `DELETE` - Suppression d'un backup  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`

  * `INFO` - Information sur les backups

  * `RESTORE` - Restauration d'un backup- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité

  * `ERROR` - Erreurs générales

- **Niveaux** : DEBUG (détails), INFO (progression), WARNING (alertes), ERROR (erreurs)- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale

- **Traçabilité** : Logs détaillés pour chaque étape du processus de backup



### Logger EDEN - Scraper Herald

## ✨ Améliorations- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)

- **Fichier** : `eden_scraper.py`

- **Actions** : INIT, COOKIES, SCRAPE, SEARCH, PARSE, TEST, CLOSE, CLEANUP, ERROR

- **Tous les logs** utilisent maintenant `extra={"action": "XXX"}`

### Auto-update lors de l'import de personnages

### Debug Window améliorée

- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"

- **Nouveau filtre** : Dropdown pour filtrer par logger

- **Options** : Tous, BACKUP, EDEN, UI, CHARACTER, ROOT- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄### Configuration des colonnes corrigée### Configuration des colonnes corrigée

- **Fichier modifié** : `UI/debug_window.py`

- **Données conservées** : name, realm, season, server, données personnalisées

---

- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)

## 🛠️ Log Source Editor - Nouvel Outil de Développement

- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs

### Vue d'ensemble

- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration

- **Fichier** : `Tools/log_source_editor.py` (975 lignes)

- **Purpose** : Éditer les logs directement dans le code source AVANT compilation- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)

- **Framework** : PySide6 (Qt6) avec interface graphique complète

- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente

### Scanner de code source

### Dossier des cookies Herald configurable

- **Technologie** : QThread asynchrone pour ne pas bloquer l'UI

- **Pattern 1** : Détecte `logger.info()`, `self.logger.debug()`, `module_logger.warning()`- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"- **Solution** : - **Solution** : 

- **Pattern 2** : Détecte `log_with_action(logger, "info", "message", action="TEST")`

- **Détection intelligente** :- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden

  * Extraction du logger name depuis le nom de fichier

  * Parsing de `get_logger(LOGGER_XXX)`- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement

  * Parsing de `setup_logger("LOGGER_NAME")`

- **Parsing** :- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)

  * Extraction de l'action depuis `action="XXX"` ou `extra={"action": "XXX"}`

  * Extraction du message (supporte f-strings, strings normales, concaténations)- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)

  * Récupération du niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)

- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`

### Interface utilisateur

- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL

**Layout principal** :

- **Gauche** : Table des logs trouvés (read-only)- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

  * Colonnes : File, Line, Logger, Level, Action, Message, Modified

  * Protection : `setEditTriggers(QTableWidget.NoEditTriggers)`- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité

- **Droite** : Panneau d'édition

  * File/Line/Logger/Level (affichage)### Unification des labels des répertoires

  * Action : ComboBox éditable avec historique

  * Message : QTextEdit multi-ligne- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`

  * Code original : QTextEdit read-only

  * Boutons : Appliquer, Réinitialiser- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"



**Toolbar** :- **Labels** : 

- 🔍 Scanner le projet

- Filtres : Logger (dropdown), Level (dropdown), Modifiés uniquement, Recherche texte  * Répertoire des personnages

- Statistiques : `📊 X/Y logs | ✏️ Z modifiés`

  * Répertoire de configuration## ✨ Améliorations## ✨ Améliorations

### Fonctionnalités clés

  * Répertoire des logs

**1. ComboBox d'actions avec historique**

- Pré-remplie avec toutes les actions trouvées dans le scan  * Répertoire des armures

- Éditable : permet de taper de nouvelles actions

- Auto-complétion : suggestions basées sur l'historique  * Répertoire des cookies Herald

- Ajout dynamique : nouvelles actions ajoutées automatiquement à la liste

- Politique : `NoInsert` pour contrôler manuellement l'ajout- **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)### Auto-update lors de l'import de personnages### Auto-update lors de l'import de personnages



**2. Raccourcis clavier**- **Localization** : Traductions complètes en FR, EN, DE

- `Enter` dans le champ Action → Applique les modifications

- `Ctrl+Enter` dans le champ Message → Applique les modifications- **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"

- Navigation avec flèches dans la table



**3. Système de filtrage**

- **Par logger** : BACKUP, EDEN, UI, CHARACTER, ROOT, Tous### Affichage du début des chemins- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄

- **Par level** : DEBUG, INFO, WARNING, ERROR, CRITICAL, Tous

- **Par statut** : Tous, Modifiés uniquement- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)

- **Par texte** : Recherche dans les messages

- Statistiques mises à jour en temps réel- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins- **Données conservées** : name, realm, season, server, données personnalisées- **Données conservées** : name, realm, season, server, données personnalisées



**4. Sauvegarde dans les fichiers**- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")

- Modification directe des fichiers source Python

- Préservation de l'indentation originale- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes

- Support des f-strings et formats complexes

- Gestion de `self.logger` et `module_logger`

- Remplacement sûr ligne par ligne

### Système de diagnostic robuste pour arrêts inattendus- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs

**5. Mémorisation du dernier projet**

- Configuration JSON : `Tools/log_editor_config.json`- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées

- Chargement automatique au démarrage (délai 100ms)

- Sélection par défaut dans le dialogue- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald

- Titre de fenêtre : `🔧 Log Source Editor - NomProjet (X logs)`

- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées

**6. Protections et validations**

- Flag `_updating` : empêche les boucles de mise à jour récursives- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)

- `blockSignals(True)` : pendant les mises à jour de table

- Comparaison `__eq__` et `__hash__` : évite recharger le même log- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête

- Vérification avant sauvegarde : détecte les fichiers non modifiés

- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt

### Workflow utilisateur

- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`

1. **Lancement** : `.venv\Scripts\python.exe Tools\log_source_editor.py`

2. **Scan automatique** : Le dernier projet se charge automatiquement### Dossier des cookies Herald configurable### Dossier des cookies Herald configurable

3. **Filtrage** : Sélectionner "Logger: BACKUP" pour voir les logs du module backup

4. **Sélection** : Cliquer sur un log dans la table### Nettoyage et réorganisation du système CHANGELOGs

5. **Édition** :

   - Choisir une action dans le dropdown ou taper une nouvelle- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"

   - Modifier le message si nécessaire

6. **Application** : Appuyer sur Enter ou cliquer "Appliquer"- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage

7. **Répétition** : Naviguer avec ↓ pour le log suivant

8. **Sauvegarde** : Cliquer "💾 Sauvegarder" pour écrire dans les fichiers source- **Structure créée** :- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden



### Statistiques affichées  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures



**Après scan** :  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier

```

✅ Scan terminé : 144 logs trouvés  - Support tri-lingual : FR, EN, DE pour chaque fichier



📊 Par Logger :- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)

   BACKUP: 46

   EDEN: 52- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)

   ROOT: 30

   UI: 16- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`



📊 Par Level :- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue

   INFO: 80

   DEBUG: 40- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`

   WARNING: 15

   ERROR: 9### Système de sauvegarde automatique lors des mises à jour de personnages



📊 Actions :- **Problème** : Lors de la modification d'un personnage existant (rang, infos, armure, compétences) ou lors d'une mise à jour Herald, aucune sauvegarde n'était déclenchée- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)

   • Actions trouvées: CHECK, DELETE, DIRECTORY, ERROR, INIT, PARSE, RETENTION, RESTORE, SCAN, SCRAPE, TRIGGER, ZIP

   • Avec action: 120- **Solution** : Intégration de backups automatiques avec raison descriptive à tous les points de modification

   • Sans action: 24

```- **Points couverts** :- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`



---  * Mise à jour Herald après confirmation (main.py)



## 🔍 Corrections Eden Scraping  * Modification de rang automatique (auto_apply_rank)



### Chemin de sauvegarde des cookies Eden (PyInstaller fix)  * Modification de rang manuelle (apply_rank_manual)



- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut  * Modification d'infos de base (save_basic_info)### Unification des labels des répertoires### Unification des labels des répertoires

- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller

- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale  * Modification d'armure/compétences (CharacterSheetWindow)

- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`

- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale  * Import/mise à jour massive (import dialog)- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")

- **Fichier modifié** : `Functions/cookie_manager.py`

- **Type de sauvegarde** : `backup_characters_force(reason="Update")` → MANUEL (bypass du daily limit)

### Auto-update lors de l'import de personnages

- **Filename** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"

- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"

- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄- **Logs générés** : Chaque modification génère des logs visibles avec tag `[BACKUP_TRIGGER]` :

- **Données conservées** : name, realm, season, server, données personnalisées

- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes  ```- **Labels** : - **Labels** : 

- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs

- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald  [BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update

- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()`

  [BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip  * Répertoire des personnages  * Répertoire des personnages

### Dossier des cookies Herald configurable

  ```

- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"

- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden- **Résultat** : Chaque modification de personnage crée automatiquement une sauvegarde avec raison descriptive et logs visibles  * Répertoire de configuration  * Répertoire de configuration

- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier

- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)- **Fichiers modifiés** : `main.py`, `UI/dialogs.py`

- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`

- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`- **Documentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` mise à jour avec nouveaux scénarios  * Répertoire des logs  * Répertoire des logs

- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)

- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`



---## 📊 Impact Général  * Répertoire des armures  * Répertoire des armures



## 🎨 Améliorations Interface



### Configuration des colonnes corrigée✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant    * Répertoire des cookies Herald  * Répertoire des cookies Herald



- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement  

- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration

- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente✅ **Gestion propre des erreurs avec rapport détaillé** - Nombre de créations, mises à jour et erreurs  - **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)- **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)

- **Solution** :

  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement✅ **Flexibilité accrue pour la gestion des cookies** - Chemins personnalisables pour le scraping  

  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)

  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL✅ **Portabilité complète de l'application** - Configuration centralisée sans dépendances __file__  - **Localization** : Traductions complètes en FR, EN, DE- **Localization** : Traductions complètes en FR, EN, DE

- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité

- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`✅ **Capacité à diagnostiquer les arrêts inattendus** - Logs détaillés de tous les événements critiques  



### Unification des labels des répertoires✅ **Interface cohérente et consistante** - Labels uniformisés et affichage optimal des chemins  - **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`- **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`



- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")✅ **Sauvegarde automatique lors des modifications** - Chaque modification de personnage crée une sauvegarde avec logs visibles  

- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"

- **Labels** :

  * Répertoire des personnages

  * Répertoire de configuration## 🔗 Fichiers Modifiés

  * Répertoire des logs

  * Répertoire des armures### Affichage du début des chemins### Affichage du début des chemins

  * Répertoire des cookies Herald

- **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)- `main.py`

- **Localization** : Traductions complètes en FR, EN, DE

- **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`- `UI/dialogs.py`- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)



### Affichage du début des chemins- `Functions/cookie_manager.py`



- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)- `Functions/tree_manager.py`- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins

- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins

- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")- `Functions/logging_manager.py`

- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()`

- `Language/fr.json`- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")

### Système de diagnostic robuste pour arrêts inattendus

- `Language/en.json`

- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées

- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation- `Language/de.json`- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)

- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées

- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs- `Documentations/BACKUP_DEBUG_GUIDE.md`

- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête

- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt

- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`

### Système de diagnostic robuste pour arrêts inattendus### Système de diagnostic robuste pour arrêts inattendus

---

- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées

## 📚 Documentation

- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation

### Nettoyage et réorganisation du système CHANGELOGs

- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées

- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)

- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs

- **Structure créée** :

  - `Changelogs/Full/` : CHANGELOGs détaillés (~200+ lignes) pour v0.106, v0.104 et versions antérieures- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête

  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les versions (v0.1 à v0.106)

  - Support tri-lingual : FR, EN, DE pour chaque fichier- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt

- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions

- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/`- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`

- **Fichiers créés** : 27+ fichiers au total (6 Full + 21 Simple)

- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue



---### Nettoyage et réorganisation du système CHANGELOGs### Nettoyage et réorganisation du système CHANGELOGs



## 📊 Statistiques- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)



- **Lignes de code ajoutées** : ~1000+ (log_source_editor.py: 975 lignes)- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage

- **Fichiers modifiés** : 12 fichiers

- **Fichiers créés** : 2 fichiers (log_source_editor.py, log_editor_config.json)- **Structure créée** :- **Structure créée** :

- **Logs tagués** : 46+ dans backup_manager.py, 52+ dans eden_scraper.py

- **Actions standardisées** : 20+ actions différentes  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures

- **Tests effectués** : Scanner, filtrage, édition, sauvegarde validés

  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)

---

  - Support tri-lingual : FR, EN, DE pour chaque fichier  - Support tri-lingual : FR, EN, DE pour chaque fichier

## 🔄 Migration

- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions

**Aucune migration requise** - Cette version est 100% rétrocompatible avec v0.105

- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)

---

- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)

## 🐛 Bugs connus

- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue

Aucun bug connu à ce jour.



---

### Système de sauvegarde automatique lors des mises à jour de personnages## 📊 Impact Général

## 📝 Notes de développement

- **Problème** : Lors de la modification d'un personnage existant (rang, infos, armure, compétences) ou lors d'une mise à jour Herald, aucune sauvegarde n'était déclenchée

- Le Log Source Editor est un outil de développement, pas inclus dans l'application principale

- L'outil facilite grandement la maintenance et l'amélioration du système de logging- **Solution** : Intégration de backups automatiques avec raison descriptive à tous les points de modification✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant  

- Le format de logging unifié permet une meilleure analyse et debugging

- Les actions standardisées facilitent le filtrage et la recherche dans les logs- **Points couverts** :✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement  


  * Mise à jour Herald après confirmation (main.py)✅ **Gestion propre des erreurs avec rapport détaillé** - Nombre de créations, mises à jour et erreurs  

  * Modification de rang automatique (auto_apply_rank)✅ **Flexibilité accrue pour la gestion des cookies** - Chemins personnalisables pour le scraping  

  * Modification de rang manuelle (apply_rank_manual)✅ **Portabilité complète de l'application** - Configuration centralisée sans dépendances __file__  

  * Modification d'infos de base (save_basic_info)✅ **Capacité à diagnostiquer les arrêts inattendus** - Logs détaillés de tous les événements critiques  

  * Modification d'armure/compétences (CharacterSheetWindow)✅ **Interface cohérente et consistante** - Labels uniformisés et affichage optimal des chemins  

  * Import/mise à jour massive (import dialog)

- **Type de sauvegarde** : `backup_characters_force(reason="Update")` → MANUEL (bypass du daily limit)### Système de sauvegarde automatique lors des mises à jour de personnages

- **Filename** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`- **Problème** : Lors de la modification d'un personnage existant (rang, infos, armure, compétences) ou lors d'une mise à jour Herald, aucune sauvegarde n'était déclenchée

- **Logs générés** : Chaque modification génère des logs visibles avec tag `[BACKUP_TRIGGER]` :- **Solution** : Intégration de backups automatiques avec raison descriptive à tous les points de modification

  ```- **Points couverts** :

  [BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update  * Mise à jour Herald après confirmation (main.py)

  [BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip  * Modification de rang automatique (auto_apply_rank)

  ```  * Modification de rang manuelle (apply_rank_manual)

- **Résultat** : Chaque modification de personnage crée automatiquement une sauvegarde avec raison descriptive et logs visibles  * Modification d'infos de base (save_basic_info)

- **Fichiers modifiés** : `main.py`, `UI/dialogs.py`  * Modification d'armure/compétences (CharacterSheetWindow)

- **Documentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` mise à jour avec nouveaux scénarios  * Import/mise à jour massive (import dialog)

- **Type de sauvegarde** : `backup_characters_force(reason="Update")` → MANUEL (bypass du daily limit)

## 📊 Impact Général- **Filename** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`

- **Logs générés** : Chaque modification génère des logs visibles avec tag `[BACKUP_TRIGGER]` :

✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant    ```

✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement    [BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update

✅ **Gestion propre des erreurs avec rapport détaillé** - Nombre de créations, mises à jour et erreurs    [BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip

✅ **Flexibilité accrue pour la gestion des cookies** - Chemins personnalisables pour le scraping    ```

✅ **Portabilité complète de l'application** - Configuration centralisée sans dépendances __file__  - **Résultat** : Chaque modification de personnage crée automatiquement une sauvegarde avec raison descriptive et logs visibles

✅ **Capacité à diagnostiquer les arrêts inattendus** - Logs détaillés de tous les événements critiques  - **Fichiers modifiés** : `main.py`, `UI/dialogs.py`

✅ **Interface cohérente et consistante** - Labels uniformisés et affichage optimal des chemins  - **Documentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` mise à jour avec nouveaux scénarios

✅ **Sauvegarde automatique lors des modifications** - Chaque modification de personnage crée une sauvegarde avec logs visibles  

## 📊 Impact Général

## 🔗 Fichiers Modifiés

- `main.py`

- `main.py`- `UI/dialogs.py`

- `UI/dialogs.py`- `Functions/cookie_manager.py`

- `Functions/cookie_manager.py`- `Functions/tree_manager.py`

- `Functions/tree_manager.py`- `Functions/logging_manager.py`

- `Functions/logging_manager.py`- `Language/fr.json`

- `Language/fr.json`- `Language/en.json`

- `Language/en.json`- `Language/de.json`

- `Language/de.json`
- `Documentations/BACKUP_DEBUG_GUIDE.md`
