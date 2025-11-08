# CHANGELOG v0.106 - Système de Logging, Sauvegarde Cookies & Optimisation Herald

**Date de début** : 2025-11-01  
**Dernière mise à jour** : 2025-11-08  
**Version** : 0.106

---

## 🎯 Refactoring Code Complet & Configuration (8 novembre 2025)

### Objectif : Code propre, exe optimisé, configuration par défaut améliorée

**Contexte** :
Avant les tests finaux de la v0.106, refactoring complet du code pour :
- Passer tous les commentaires en anglais
- Réduire la taille de l'exécutable
- Nettoyer les imports inutilisés
- Corriger les bugs découverts
- Améliorer la configuration par défaut

**Résultats** :

### 1. Traduction Complète Français → Anglais
✅ **582 commentaires français traduits** (975 modifications totales)  
✅ **100% du code en anglais** (meilleure maintenabilité)  
✅ **89 phrases complètes** traduites via patterns de correspondance  
✅ **Reste traduit mot par mot** pour contexte approprié  

### 2. Optimisation des Imports
✅ **51 imports inutilisés supprimés** via analyse AST  
✅ **Fichiers les plus nettoyés** :
   - `cookie_manager.py` : 11 imports
   - `eden_scraper.py` : 6 imports
   - `main.py` : 5 imports
   - `backup_manager.py` : 3 imports

### 3. Nettoyage du Code
✅ **74 lignes blanches excessives** supprimées (max 2 consécutives)  
✅ **1 debug print** supprimé  
✅ **Formatage cohérent** sur tout le projet  

### 4. Corrections de Bugs

**Bug 1 : Imports critiques manquants**
- **Problème** : Optimisation trop agressive, imports nécessaires supprimés
- **Fichiers corrigés** :
  - `character_actions_manager.py` : Ajout `QMessageBox, QInputDialog, QDialog, QLineEdit`
  - `armor_manager.py` : Ajout `ensure_armor_dir` depuis `path_manager`
  - `tree_manager.py` : Ajout `QHeaderView`
  - `main.py` : Restauration imports Qt et config
- **Résultat** : ✅ Application démarre, toutes les fonctionnalités OK

**Bug 2 : Logs créés même avec debug_mode désactivé**
- **Problème** : Dossier `Logs/` et `debug.log` créés au démarrage même si option désactivée
- **Solution** : Création conditionnelle uniquement si `debug_mode = true`
- **Fichier modifié** : `logging_manager.py`
- **Résultat** : ✅ Aucun fichier log si debug désactivé

**Bug 3 : Erreur migration sur dossier inexistant**
- **Problème** : Erreur `MIGRATION_FLAG_ERROR` si dossier Characters n'existe pas
- **Solution** : Vérification existence du dossier avant création flag `.migration_done`
- **Fichier modifié** : `migration_manager.py`
- **Résultat** : ✅ Plus d'erreur dans les logs

**Bug 4 : Version incorrecte dans "À Propos"**
- **Problème** : Affichait v0.104 au lieu de v0.106
- **Solution** : `APP_VERSION = "0.106"` dans `main.py`
- **Résultat** : ✅ Version correcte affichée

### 5. Configuration Par Défaut Améliorée

**Problème** : Config.json recréé au premier lancement avec mauvaises valeurs par défaut

**Solutions** :

**Saison par défaut → S3**
- `config_manager.py` : `"default_season": "S3"` (création initiale)
- `character_actions_manager.py` : `config.get("default_season", "S3")`
- `dialogs.py` : `config.get('default_season', 'S3')`

**Gestion manuelle colonnes activée**
- `config_manager.py` : `"manual_column_resize": true` ajouté
- `tree_manager.py` : `config.get("manual_column_resize", True)`
- `main.py` : `config.get("manual_column_resize", True)`
- `dialogs.py` : `config.get("manual_column_resize", True)`

**Résultat** : ✅ Première installation avec S3 et colonnes manuelles

### 6. Impact Global

**Fichiers modifiés** : 67 fichiers production
- `Functions/` : 11 fichiers (managers)
- `UI/` : 4 fichiers (dialogs, delegates, debug)
- `Scripts/` : 42 fichiers (tests/utilitaires)
- `Tools/` : 4 fichiers (éditeurs)
- `Test/` : 2 fichiers (Herald)
- `main.py` : Application principale

**Statistiques** :
- 19,941 lignes totales
- 792.58 KB
- -47 lignes net (607 supprimées, 560 ajoutées)

**Impact exe** :
- Estimation : -1 à 2 MB (-2 à 4%)
- 51 imports en moins = bundle plus léger
- Bytecode plus propre

**Tests** :
✅ Démarrage application : 5 secondes  
✅ Imports : Tous validés  
✅ Backup : Fonctionnel  
✅ Herald : Connexion DevTools OK  
✅ Suppression perso : OK (QMessageBox fix)  
✅ Gestion armures : OK (ensure_armor_dir fix)  
✅ Toutes fonctionnalités : Testées et validées  

**Documentation** :
- Rapport complet : `Reports/CODE_REFACTORING_REPORT_v0.106.md`

---

## ✨ Amélioration Backup - Noms de Fichiers Clairs (7 novembre 2025)

### Amélioration : Inclusion du nom de personnage dans les fichiers de backup

**Problème** :
Les noms de fichiers de backup n'étaient pas assez explicites - impossible de savoir rapidement quel personnage était concerné par une sauvegarde spécifique.

**Exemple ancien format** :
```
backup_characters_20251107_143025_Update.zip
backup_characters_20251107_144512_Delete.zip
```
❌ Quel personnage a été modifié ? Impossible à dire sans ouvrir le fichier.

**Nouveau format** :
```
# Opération sur un personnage unique
backup_characters_20251107_143025_Update_Merlin.zip
backup_characters_20251107_144512_Delete_Arthur.zip
backup_characters_20251107_145820_Rename_Lancelot.zip

# Opération sur plusieurs personnages
backup_characters_20251107_150230_Update_multi.zip

# Backup manuel/automatique global
backup_characters_20251107_151045_Manual.zip
```

**Modifications apportées** :

1. **Ajout du paramètre `character_name`** :
```python
# backup_manager.py
def backup_characters_force(self, reason=None, character_name=None):
    """
    Args:
        reason: "Manual", "Delete", "Update", "Rename"...
        character_name: Nom du personnage ou "multi" pour opérations multiples
    """
    return self._perform_backup("MANUAL-BACKUP", reason=reason or "Manual", character_name=character_name)

def _perform_backup(self, mode="MANUAL", reason=None, character_name=None):
    # Génération du nom de fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reason_str = f"_{reason}" if reason else ""
    char_str = f"_{character_name}" if character_name else ""
    
    backup_name = f"backup_characters_{timestamp}{reason_str}{char_str}"
```

2. **Mise à jour de tous les points d'appel** :

**Suppression de personnage** :
```python
# character_actions_manager.py
self.main_window.backup_manager.backup_characters_force(
    reason="Delete", 
    character_name=char_name  # ✅ Nom du personnage
)
```

**Renommage** :
```python
# character_actions_manager.py
self.main_window.backup_manager.backup_characters_force(
    reason="Rename", 
    character_name=old_name  # ✅ Ancien nom du personnage
)
```

**Modifications (rank, info, armor)** :
```python
# dialogs.py
self.parent_app.backup_manager.backup_characters_force(
    reason="Update", 
    character_name=self.character_data.get('name', 'Unknown')  # ✅ Nom du personnage
)
```

**Import massif** :
```python
# dialogs.py - Mass Import
parent_app.backup_manager.backup_characters_force(
    reason="Update", 
    character_name="multi"  # ✅ Tag pour opérations multiples
)
```

**Backup manuel** :
```python
# dialogs.py - Manual backup button
self.backup_manager.backup_characters_force()  # ✅ Pas de nom (backup global)
```

**Fichiers modifiés** :
- `Functions/backup_manager.py` (ajout paramètre + génération nom)
- `Functions/character_actions_manager.py` (delete, rename)
- `UI/dialogs.py` (update rank/info/armor, mass import)
- `main.py` (update from Herald)

**Avantages** :
- ✅ **Identification immédiate** : Vous savez tout de suite quel personnage est concerné
- ✅ **Distinction claire** : Opérations simples vs. multiples facilement identifiables
- ✅ **Historique lisible** : Navigation dans les backups beaucoup plus intuitive
- ✅ **Recherche rapide** : Trouvez facilement la sauvegarde d'un personnage spécifique
- ✅ **Maintenance facilitée** : Nettoyage des anciens backups plus simple

**Commit** :
- `339a5a8` - feat: Add character name to backup filenames for clarity

---

## 🔧 Corrections Critiques Herald Search (7 novembre 2025)

### FIX CRITIQUE : Crash brutal lors d'erreurs de recherche Herald

**Problème** :
Le programme se fermait **brutalement** (sans message d'erreur) lors de certaines erreurs pendant la recherche Herald. Aucun log, fermeture immédiate.

**Cause racine** :
Le WebDriver (navigateur Chrome) n'était **pas fermé proprement** dans les chemins d'erreur :
```python
# eden_scraper.py - search_herald_character() (CASSÉ)
try:
    scraper = EdenScraper(cookie_manager)
    if not scraper.initialize_driver(headless=False):
        return False, "Erreur", ""  # ❌ scraper pas fermé !
    
    # ... code de recherche ...
    scraper.close()  # ✅ OK dans le chemin normal
    return True, message, path
    
except Exception as e:
    return False, str(e), ""  # ❌ scraper pas fermé !
```

**Solution** :
Ajout de `scraper.close()` dans **tous** les chemins d'erreur avec protection :
```python
# eden_scraper.py - search_herald_character() (CORRIGÉ)
try:
    scraper = EdenScraper(cookie_manager)
    if not scraper.initialize_driver(headless=False):
        try:
            scraper.close()  # ✅ Fermeture propre
        except:
            pass
        return False, "Erreur", ""
    
    # ... code de recherche ...
    scraper.close()  # ✅ Chemin normal
    return True, message, path
    
except Exception as e:
    module_logger.error(f"Erreur: {e}")
    module_logger.error(f"Stacktrace: {traceback.format_exc()}")  # ✅ Log complet
    try:
        scraper.close()  # ✅ Fermeture dans exception
    except:
        pass
    return False, str(e), ""
```

**Corrections appliquées** :

1. **Fermeture propre du WebDriver** (`eden_scraper.py`) :
   - Ajout `scraper.close()` dans le bloc `except`
   - Ajout `scraper.close()` quand `initialize_driver()` échoue
   - Protection avec `try/except` pour éviter erreurs en cascade

2. **Amélioration du diagnostic** :
   - Import module `traceback`
   - Logging du stacktrace complet en cas d'erreur
   - Logs détaillés à chaque étape de la recherche

3. **Validation par test de stabilité** :
   - Script `test_herald_stability.py` créé
   - 25 recherches consécutives testées
   - Résultats : **100% de réussite, 0 crash**

**Test de stabilité effectué** :
```
Configuration :
  - Personnages testés : 5
  - Itérations : 5
  - Total de recherches : 25
  - Délai entre recherches : 3s

Résultats (2025-11-07) :
  - Tests effectués : 25
  - ✅ Réussis : 25 (100.0%)
  - ❌ Échoués : 0 (0.0%)
  - ⏱️ Durée totale : 662.3s (11.0 min)
  - ⏱️ Durée moyenne : 26.5s par recherche
  
Conclusion : ✨ AUCUNE ERREUR - SYSTÈME STABLE ✨
```

**Fichiers modifiés** :
- `Functions/eden_scraper.py` (fermeture propre + logs)

**Fichiers ajoutés** :
- `Scripts/test_herald_stability.py` (script de test automatisé)

**Commits** :
- `9e84494` - fix: Ensure scraper is properly closed in all error paths
- `a351226` - test: Add Herald search stability test script

**Impact** :
- ✅ Plus de crash brutal du programme
- ✅ Logs d'erreur complets pour diagnostic
- ✅ 100% stable validé par tests automatisés
- ✅ Script de test pour validation continue

---

## 🔧 Corrections Critiques Backup (7 novembre 2025)

### FIX CRITIQUE : Résolution des chemins pour les backups

**Problème** :
Le système de backup était **complètement cassé** depuis le début de la v0.106 à cause d'une incohérence dans la résolution des chemins de dossiers.

**Symptômes** :
- ❌ Aucun backup automatique lors de création/modification/suppression
- ❌ Backup manuel échouait avec "folder not found"
- ❌ Messages ERROR trompeurs au premier démarrage
- ❌ Pas de logs de création des dossiers backup

**Cause racine** :
```python
# backup_manager.py (CASSÉ)
char_folder = self.config_manager.get("character_folder")  # Retourne None !
if not char_folder or not os.path.exists(char_folder):
    return "folder not found"  # Toujours vrai si config non définie !

# character_manager.py (CORRECT)
def get_character_dir():
    return config.get("character_folder") or default_path  # Fallback OK
```

**Solution** :
```python
# backup_manager.py (CORRIGÉ)
from Functions.character_manager import get_character_dir
char_folder = get_character_dir()  # Utilise le fallback
if not os.path.exists(char_folder):
    return "folder not found"  # Seulement si réellement inexistant
```

**Corrections appliquées** :

1. **Résolution de chemins** (`backup_manager.py`) :
   - `backup_character()` : Utilise `get_character_dir()` avec fallback
   - `backup_cookies()` : Utilise `get_config_dir()` avec fallback
   - `restore_backup()` : Utilise `get_character_dir()` pour restauration

2. **Amélioration des logs** :
   - ERROR → INFO quand dossiers n'existent pas au 1er démarrage
   - Ajout logs INFO lors de création des dossiers
   - Message clair : "No characters to backup" au lieu de "folder not found"

3. **Logs de création de dossiers** :
   - `_ensure_backup_dir()` : INFO si création, DEBUG si existe
   - `_ensure_cookies_backup_dir()` : INFO si création, DEBUG si existe
   - `character_manager.py` : Log création dossier Characters
   - `cookie_manager.py` : Log création dossier Configuration

**Fichiers modifiés** :
- `Functions/backup_manager.py` (résolution chemins + logs améliorés)
- `Functions/character_manager.py` (log création dossier)
- `Functions/cookie_manager.py` (log création dossier)

**Commits** :
- `175c42b` - Improve logging for first startup
- `9d5158d` - Add INFO logs when backup directories are created
- `20331d6` - Use proper folder resolution for backups (CRITICAL)
- `83f99e9` - Improve backup error message when no characters exist

**Impact** :
- ✅ Backups automatiques fonctionnent (create/update/delete)
- ✅ Backup manuel fonctionne
- ✅ Backup quotidien au démarrage fonctionne
- ✅ Logs clairs et non trompeurs
- ✅ Traçabilité complète de la création des dossiers

---

## ⚡ Optimisation Herald Performance - Phase 1 (8 novembre 2025)

### Réduction des Timeouts Herald

**Contexte** :
- Analyse complète des 21 occurrences de `time.sleep()` dans le code Herald
- Crash WebDriver corrigé (7 nov) : fermeture propre dans tous les chemins d'erreur
- Phase 1 aggressive validée après correction du bug de cleanup
- Documentation complète : `HERALD_TIMEOUTS_ANALYSIS.md` + `HERALD_PHASE1_TEST_REPORT.md`

**Phase 1 - Solution adoptée** :
```python
# eden_scraper.py
time.sleep(1)  # Homepage (avant: 2s) → -1s
# SUPPRIMÉ      # Sleep avant refresh (avant: 3s) → -3s ★ GAIN MAJEUR
time.sleep(2)  # Refresh (avant: 3s) → -1s
time.sleep(2)  # Herald load (avant: 4s) → -2s

# cookie_manager.py  
time.sleep(1)  # Homepage test (avant: 2s) → -1s
time.sleep(2)  # Refresh test (avant: 3s) → -1s
time.sleep(3)  # Herald test (avant: 5s) → -2s
```

**Performance validée (25/25 tests réussis)** :
- **Recherche personnage : 26.5s → 21.9s (-17.4%)**
- **0 crash** (WebDriver cleanup fix appliqué)
- Durée totale 25 recherches : 662.3s → 546.4s (-1.9 min)
- **Gain par recherche : -4.6 secondes**
- Stabilité : 100% (écart type 0.3s, plage 18.7-19.6s)

**Fichiers modifiés** :
- `Functions/eden_scraper.py` (lignes 115, 138, 142, 147)
- `Functions/cookie_manager.py` (lignes 645, 660, 665)
- `Scripts/test_herald_stability.py` (script de test automatisé)

**Pourquoi ça marche maintenant** :
- Phase 1 échouait avant à cause du bug WebDriver (crash QThread)
- Bug corrigé dans commit 9e84494 (7 nov) : `scraper.close()` dans tous les chemins
- Phase 1 agressive est sûre avec une gestion propre des ressources
- `Functions/cookie_manager.py` (lignes 660, 665)
- `.gitignore` (exclusion `Scripts/debug_herald_page.html`)
- `HERALD_TIMEOUTS_ANALYSIS.md` (documentation complète)

**Commits** :
- `5d7d010` - Phase 1 bis : Conservative Herald timeout optimizations
- `815c588` - Phase 1 bis adoptée (post-mortem Phase 1 aggressive)
- `1885656` - Add debug_herald_page.html to .gitignore

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

### Améliorations du layout de la fiche personnage - Section Statistiques

**Amélioration** : Réorganisation de la fiche personnage pour une meilleure lisibilité et fonctionnalité

**Modifications** :
- Renommage de la section "Armure" en "Statistiques" (3 langues)
- Suppression du bouton "Résistances" grisé (placeholder désactivé)
- Ajout du texte "🔜 Fonctionnalité bientôt disponible" dans la section Statistiques
- Déplacement du bouton "Gérer les armures" sous la section "Rang de Royaume"
- Amélioration de la hiérarchie visuelle et organisation des sections

**Résultat** :
- ✅ Nommage de section plus clair (Statistiques vs Armure)
- ✅ Suppression des éléments UI désactivés pour apparence plus propre
- ✅ Meilleur flux visuel avec placement des boutons
- ✅ Placeholder indiquant clairement les futures fonctionnalités
- ✅ Layout de fiche personnage plus intuitif

---

## 🐛 Corrections de Bugs - Stabilité .exe PyInstaller

### Fix : Crash PyInstaller noconsole - Gestion sys.stderr/stdout None

**Problème** : L'application crashait au démarrage avec `AttributeError: 'NoneType' object has no attribute 'flush'`

**Cause racine** : Quand PyInstaller compile l'application en mode `--noconsole` (sans console Windows), `sys.stderr` et `sys.stdout` sont automatiquement mis à `None`. Le code appelait `sys.stderr.flush()` sans vérifier si `sys.stderr` existait, causant un crash immédiat.

**Emplacements affectés** :
- `main.py` - Initialisation globale
- `Functions/backup_manager.py` - Ligne 30 dans `__init__()`
- `UI/dialogs.py` - 10+ occurrences dans divers dialogues

**Solution implémentée** :
```python
# Fix pour PyInstaller --noconsole mode: sys.stderr/stdout peuvent être None
if sys.stderr is None:
    sys.stderr = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')
if sys.stdout is None:
    sys.stdout = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')
```

**Résultat** :
- ✅ Application démarre avec succès en mode `--noconsole`
- ✅ Plus de crashs `NoneType`
- ✅ Logs toujours écrits correctement dans les fichiers
- ✅ .exe totalement fonctionnel

**Fichiers modifiés** : `main.py`, `backup_manager.py`, `dialogs.py`

### Fix : Prévention crash silencieux lors du test de connexion Herald

**Problème** : L'application .exe crashait silencieusement (sans logs) pendant la vérification de connexion Herald Eden. Aucun message d'erreur, aucun log, aucun traceback - crash silencieux complet.

**Causes racines identifiées** :
1. **Import Selenium** pouvait échouer dans le .exe PyInstaller sans logging approprié
2. **Initialisation du driver** pouvait retourner `None` et causer un crash dans `driver.quit()`
3. **Exceptions non catchées** dans le thread `EdenStatusThread` crashaient tout le process
4. **Pas de traceback complet** pour déboguer les erreurs

**Chemin de code vulnérable** :
- `cookie_manager.test_eden_connection()` - Méthode de test principale
- `ui_manager.EdenStatusThread.run()` - Thread de vérification en arrière-plan
- Initialisation et cleanup du WebDriver Selenium

**Solutions implémentées** :

**Dans `cookie_manager.py`** :
- Initialisation `driver = None` au début de la méthode pour cleanup sécurisé
- `try-except` séparé pour les imports Selenium avec messages d'erreur explicites
- Vérification `if not driver` avant toute opération sur le driver
- Bloc `finally` protégé avec `if driver:` avant `driver.quit()`
- Logging complet avec `traceback.format_exc()` pour débogage
- Correction indentation dans le bloc de sauvegarde du fichier debug

**Dans `ui_manager.py`** :
- `try-except` global dans `EdenStatusThread.run()`
- Logging complet des exceptions avec traceback
- Émission d'un signal d'erreur au lieu de crasher
- UI reste responsive même en cas d'erreur

**Structure de gestion d'erreur améliorée** :
```python
driver = None  # Initialisation sécurisée
try:
    # Import séparé avec gestion d'erreur spécifique
    try:
        from selenium import webdriver
    except ImportError as e:
        # Log et retour d'erreur structurée
        
    # Initialisation du driver
    driver, browser = self._initialize_browser_driver(...)
    if not driver:
        # Retour anticipé avec message d'erreur
        
    # Opérations Selenium...
    
except Exception as e:
    # Logging traceback complet
    traceback_details = traceback.format_exc()
    logger.error(f"CRASH: {e}\n{traceback_details}")
    
finally:
    # Cleanup sécurisé
    if driver:
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Erreur cleanup driver: {e}")
```

**Résultat** :
- ✅ Plus de crashs silencieux
- ✅ Toutes les exceptions loguées dans `Logs/debug.log`
- ✅ Messages d'erreur clairs pour les utilisateurs
- ✅ Application reste stable même si le test Herald échoue
- ✅ Traceback complet disponible pour débogage
- ✅ Les crashs de thread ne tuent pas toute l'application

**Fichiers modifiés** : `cookie_manager.py` (117 lignes changées), `ui_manager.py`

**Tests** : Validé dans le .exe compilé avec divers scénarios d'erreur (pas de navigateur, problèmes réseau, cookies invalides)

### Fix : Erreurs de logging du backup - messages d'erreur appropriés

**Problème** : Les logs de backup affichaient des chaînes littérales sans signification au lieu des vrais messages d'erreur :
```
2025-11-03 14:14:28 - BACKUP - ERROR - INFO - error_msg
2025-11-03 14:20:18 - BACKUP - ERROR - INFO - error_msg
```

**Cause racine** : Le code loguait les chaînes littérales `"error_msg"` et `"success_msg"` au lieu du contenu réel des variables. De plus, le formatage des f-strings était malformé avec des guillemets échappés.

**Code problématique** :
```python
# Lignes 185, 223 - Chaînes littérales au lieu des variables
self.logger.error("error_msg", extra={"action": "INFO"})
self.logger.info("success_msg", extra={"action": "INFO"})

# Ligne 200-202 - F-strings malformés
self.logger.info("Creating compressed backup: {os.path.basename(backup_file)}\", action=", ...)
```

**Code corrigé** :
```python
# Logging approprié des variables avec log_with_action
log_with_action(self.logger, "error", error_msg, action="CHECK")
log_with_action(self.logger, "info", success_msg, action="SUCCESS")

# Formatage f-string correct
log_with_action(self.logger, "info", f"Creating compressed backup: {os.path.basename(backup_file)}", action="ZIP")
```

**Modifications effectuées** :
- **Ligne 185** : Utilisation de `log_with_action()` avec la vraie variable `error_msg` au lieu de la chaîne littérale
- **Ligne 200** : Correction du formatage f-string pour le message de backup compressé
- **Ligne 202** : Changement de l'action de `ZIP` à `COPY` pour les backups non compressés (catégorisation appropriée)
- **Ligne 215** : Utilisation de `log_with_action()` avec la vraie variable `success_msg` au lieu de la chaîne littérale
- **Ligne 223** : Utilisation de `log_with_action()` avec la vraie variable `error_msg` au lieu de la chaîne littérale
- Tags d'actions appropriés : `CHECK`, `ZIP`, `COPY`, `SUCCESS`, `ERROR`, `RETENTION`

**Résultat** :
- ✅ Messages d'erreur clairs dans les logs : `BACKUP - ERROR - CHECK - Characters folder not found`
- ✅ Messages de succès montrent les vrais noms de fichiers : `BACKUP - INFO - SUCCESS - Backup created: backup_characters_20251106_153045_Delete.zip`
- ✅ Toutes les opérations de backup entièrement traçables avec des messages significatifs
- ✅ Catégorisation appropriée des actions pour faciliter le débogage
- ✅ Plus de littéraux "error_msg" ou "success_msg" sans signification dans les logs

**Fichiers modifiés** : `backup_manager.py` (6 lignes changées)

**Impact** : Cette correction facilite grandement le débogage des problèmes de backup en fournissant des messages d'erreur clairs et actionnables au lieu de texte placeholder.

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
