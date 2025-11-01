# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update



**Date** : 2025-11-01  

**Version** : 0.106

**Date** : 2025-11-01  **Date** : 2025-11-01  

## 🐛 Corrections

**Version** : 0.106**Version** : 0.106

### Chemin de sauvegarde des cookies Eden (PyInstaller fix)

- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut

- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller

- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale## 🐛 Corrections## 🐛 Corrections

- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`

- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale

- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)

### Chemin de sauvegarde des cookies Eden (PyInstaller fix)### Chemin de sauvegarde des cookies Eden (PyInstaller fix)

### Configuration des colonnes corrigée

- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut

- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration

- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller

- **Solution** : 

  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale

  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)

  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`

- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité

- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale



## ✨ Améliorations- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)



### Auto-update lors de l'import de personnages

- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"

- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄### Configuration des colonnes corrigée### Configuration des colonnes corrigée

- **Données conservées** : name, realm, season, server, données personnalisées

- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)

- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs

- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration

- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)

- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente

### Dossier des cookies Herald configurable

- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"- **Solution** : - **Solution** : 

- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden

- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement

- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)

- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)

- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`

- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL

- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité

### Unification des labels des répertoires

- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`

- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"

- **Labels** : 

  * Répertoire des personnages

  * Répertoire de configuration## ✨ Améliorations## ✨ Améliorations

  * Répertoire des logs

  * Répertoire des armures

  * Répertoire des cookies Herald

- **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)### Auto-update lors de l'import de personnages### Auto-update lors de l'import de personnages

- **Localization** : Traductions complètes en FR, EN, DE

- **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"



### Affichage du début des chemins- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄

- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)

- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins- **Données conservées** : name, realm, season, server, données personnalisées- **Données conservées** : name, realm, season, server, données personnalisées

- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")

- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes



### Système de diagnostic robuste pour arrêts inattendus- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs

- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées

- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald

- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées

- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)

- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête

- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt

- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`

### Dossier des cookies Herald configurable### Dossier des cookies Herald configurable

### Nettoyage et réorganisation du système CHANGELOGs

- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"

- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage

- **Structure créée** :- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden

  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures

  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier

  - Support tri-lingual : FR, EN, DE pour chaque fichier

- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)

- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)

- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`

- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue

- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`

### Système de sauvegarde automatique lors des mises à jour de personnages

- **Problème** : Lors de la modification d'un personnage existant (rang, infos, armure, compétences) ou lors d'une mise à jour Herald, aucune sauvegarde n'était déclenchée- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)

- **Solution** : Intégration de backups automatiques avec raison descriptive à tous les points de modification

- **Points couverts** :- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

  * Mise à jour Herald après confirmation (main.py)

  * Modification de rang automatique (auto_apply_rank)

  * Modification de rang manuelle (apply_rank_manual)

  * Modification d'infos de base (save_basic_info)### Unification des labels des répertoires### Unification des labels des répertoires

  * Modification d'armure/compétences (CharacterSheetWindow)

  * Import/mise à jour massive (import dialog)- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")

- **Type de sauvegarde** : `backup_characters_force(reason="Update")` → MANUEL (bypass du daily limit)

- **Filename** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"

- **Logs générés** : Chaque modification génère des logs visibles avec tag `[BACKUP_TRIGGER]` :

  ```- **Labels** : - **Labels** : 

  [BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update

  [BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip  * Répertoire des personnages  * Répertoire des personnages

  ```

- **Résultat** : Chaque modification de personnage crée automatiquement une sauvegarde avec raison descriptive et logs visibles  * Répertoire de configuration  * Répertoire de configuration

- **Fichiers modifiés** : `main.py`, `UI/dialogs.py`

- **Documentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` mise à jour avec nouveaux scénarios  * Répertoire des logs  * Répertoire des logs



## 📊 Impact Général  * Répertoire des armures  * Répertoire des armures



✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant    * Répertoire des cookies Herald  * Répertoire des cookies Herald

✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement  

✅ **Gestion propre des erreurs avec rapport détaillé** - Nombre de créations, mises à jour et erreurs  - **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)- **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)

✅ **Flexibilité accrue pour la gestion des cookies** - Chemins personnalisables pour le scraping  

✅ **Portabilité complète de l'application** - Configuration centralisée sans dépendances __file__  - **Localization** : Traductions complètes en FR, EN, DE- **Localization** : Traductions complètes en FR, EN, DE

✅ **Capacité à diagnostiquer les arrêts inattendus** - Logs détaillés de tous les événements critiques  

✅ **Interface cohérente et consistante** - Labels uniformisés et affichage optimal des chemins  - **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`- **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

✅ **Sauvegarde automatique lors des modifications** - Chaque modification de personnage crée une sauvegarde avec logs visibles  



## 🔗 Fichiers Modifiés

### Affichage du début des chemins### Affichage du début des chemins

- `main.py`

- `UI/dialogs.py`- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)

- `Functions/cookie_manager.py`

- `Functions/tree_manager.py`- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins

- `Functions/logging_manager.py`

- `Language/fr.json`- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")

- `Language/en.json`

- `Language/de.json`- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)

- `Documentations/BACKUP_DEBUG_GUIDE.md`



### Système de diagnostic robuste pour arrêts inattendus### Système de diagnostic robuste pour arrêts inattendus

- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées

- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation

- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées

- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs

- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête

- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt

- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`



### Nettoyage et réorganisation du système CHANGELOGs### Nettoyage et réorganisation du système CHANGELOGs

- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)

- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage

- **Structure créée** :- **Structure créée** :

  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures

  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)

  - Support tri-lingual : FR, EN, DE pour chaque fichier  - Support tri-lingual : FR, EN, DE pour chaque fichier

- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions

- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)

- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)

- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue



### Système de sauvegarde automatique lors des mises à jour de personnages## 📊 Impact Général

- **Problème** : Lors de la modification d'un personnage existant (rang, infos, armure, compétences) ou lors d'une mise à jour Herald, aucune sauvegarde n'était déclenchée

- **Solution** : Intégration de backups automatiques avec raison descriptive à tous les points de modification✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant  

- **Points couverts** :✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement  

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
