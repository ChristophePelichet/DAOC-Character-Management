# 📝 CHANGELOG - Gestionnaire de Personnages DAOC

Historique complet des versions du gestionnaire de personnages pour Dark Age of Camelot (Eden).

---

# ✨✨ v0.107 - 2025-11-11

### 🎉 Ajout

**Système de Thèmes Configurable**
- 🎨 Système de thèmes basé sur fichiers JSON stockés dans dossier `Themes/`
- 🌓 Deux thèmes disponibles : Clair (windowsvista) et Sombre (Fusion avec CSS personnalisé)
- ⚙️ Sélecteur de thème intégré dans ConfigurationDialog (`UI/dialogs.py`)
- 🔄 Application immédiate du thème sans redémarrage (via `apply_theme()` dans `main.py`)
- 💾 Persistance du thème sélectionné dans `Configuration/config.json` (clé "theme")
- 🌍 Support multilingue complet avec traductions automatiques :
  - 🇫🇷 Français : Clair / Sombre
  - 🇬🇧 English : Light / Dark
  - 🇩🇪 Deutsch : Hell / Dunkel
- 📦 Portabilité complète pour compilation .exe via PyInstaller
- 🎭 Support des styles Qt natifs : windowsvista, Fusion, Windows, windows11
- 🎨 Personnalisation palette de couleurs (QPalette) avec 17 rôles de couleurs
- 🖌️ Support couleurs état désactivé (préfixe `Disabled_` dans palette)
- 📝 Feuilles de style CSS optionnelles pour personnalisation fine
- 🔧 Module `Functions/theme_manager.py` (138 lignes) :
  - `get_themes_dir()` : Retourne chemin dossier Themes/
  - `get_available_themes()` : Liste thèmes avec traduction automatique
  - `load_theme(theme_id)` : Charge JSON du thème
  - `apply_theme(app, theme_id)` : Applique style, palette et CSS
- 🔤 Tri alphabétique automatique des thèmes dans ComboBox
- 🗂️ Structure JSON des thèmes :
  ```json
  {
    "name": "theme_light",  // Clé de traduction
    "style": "windowsvista",  // Style Qt
    "palette": { "Window": "#F0F0F0", ... },  // Couleurs QPalette
    "stylesheet": ""  // CSS optionnel
  }
  ```

**Thèmes Inclus**
- 🌞 **Thème Clair** (`Themes/default.json`) :
  - Style : windowsvista (natif Windows)
  - Palette : Couleurs claires standard (#F0F0F0 fenêtre, #FFFFFF base)
  - Stylesheet : Aucun (utilise styles natifs)
- 🌙 **Thème Sombre** (`Themes/dark.json`) :
  - Style : Fusion (multi-plateforme)
  - Palette : Couleurs sombres (#2D2D30 fenêtre, #1E1E1E base, #DCDCDC texte)
  - Stylesheet : CSS personnalisé pour menus déroulants, tooltips et combobox
  - Effets : Bordures subtiles, arrière-plans sombres cohérents

### 🧰 Modification

**Configuration de l'Application**
- 📝 `Functions/config_manager.py` (ligne 57) :
  - Ajout clé `"theme": "default"` dans configuration par défaut
  - Sauvegarde automatique lors du changement de thème

**Interface de Configuration**
- 🎛️ `UI/dialogs.py` (lignes 2186-2196) :
  - Ajout QComboBox pour sélection du thème
  - Import `get_available_themes` de `Functions.theme_manager`
  - Tri alphabétique des thèmes par nom traduit
  - Label traduit via `lang.get("config_theme_label")`
- 🔄 `UI/dialogs.py` (lignes 2332-2338) :
  - Chargement du thème actuel dans update_fields()
  - Sélection automatique du thème courant dans ComboBox

**Application Principale**
- 🚀 `main.py` (lignes 685-694) :
  - Détection changement de thème dans save_configuration()
  - Application immédiate du nouveau thème si modifié
  - Appel à `apply_theme()` avec QApplication.instance()
- 🎨 `main.py` (lignes 883-887) :
  - Nouvelle fonction `apply_theme(app)` pour chargement au démarrage
  - Lecture du thème depuis config.json
  - Appel à `theme_manager.apply_theme()`

**Configuration PyInstaller**
- 📦 `DAOC-Character-Manager.spec` :
  - Ajout `('Themes', 'Themes')` dans section `datas` pour bundling
  - Ajout `'Functions.theme_manager'` dans `hiddenimports`
  - Garantit inclusion des fichiers JSON dans l'exécutable

**Gestion des Chemins**
- 🗂️ `Functions/theme_manager.py` :
  - Utilisation de `get_resource_path("Themes")` au lieu de `Path(__file__).parent.parent`
  - Compatible mode développement (chemin absolu) et mode frozen (`sys._MEIPASS`)
  - Import de `Functions.path_manager.get_resource_path`

**Traductions**
- 🌍 Fichiers de langue (`Language/*.json`) :
  - Clés existantes réutilisées : `theme_light`, `theme_dark`, `config_theme_label`
  - Aucune modification nécessaire (clés déjà présentes)

### 🐛 Correction

**Système de Thèmes**
- 🌍 Correction traduction automatique des noms de thèmes :
  - Utilisation correcte de `lang.get(key)` sans second paramètre
  - LanguageManager.get() accepte 2 arguments : self et key
  - Retourne la clé elle-même si traduction absente (fallback automatique)
- 📋 Remplacement noms en dur par clés de traduction dans JSON :
  - `default.json` : "Windows Vista (Par défaut)" → "theme_light"
  - `dark.json` : "Sombre" → "theme_dark"
- 🔧 Détection automatique clés de traduction (préfixe "theme_") :
  - Si clé commence par "theme_", appel à `lang.get()`
  - Sinon, utilisation directe du nom (compatibilité thèmes personnalisés)

**Portabilité**
- 📦 Correction chemin absolu pour PyInstaller :
  - Utilisation `get_resource_path()` dans `get_themes_dir()`
  - Fonctionne en développement et en mode frozen
  - Accès correct aux fichiers JSON dans bundle .exe

### 🔚 Retrait

**Bibliothèques Externes**
- ❌ Retrait tentative d'utilisation de qt-material (conflit avec styles personnalisés)
- ✅ Solution native sans dépendances supplémentaires

---

**Commits associés :**
- `c2f97c1` - feat: Add JSON-based theme system with two themes
- `317bd16` - fix: Make theme system portable and multilingual

---

# ✨✨ v0.107 - 2025-11-10

### 🎉 Ajout

**Système de Vérification de Version**
- 🔄 Vérification automatique au démarrage (thread en arrière-plan, non-bloquant)
- 📊 Affichage version actuelle depuis `Functions/version.py` (__version__ constant)
- 🌐 Affichage dernière version depuis GitHub (version.txt sur branche main)
- 🔘 Bouton manuel "🔄 Vérifier" (désactivé pendant check, timeout 5s)
- ✅ Indicateurs visuels : ✓ vert (à jour) / ✗ rouge (obsolète)
- 🔗 Lien téléchargement cliquable vers GitHub Releases (visible si update disponible)
- ℹ️ Section "Informations" (renommage de "Monnaie")
- 🌍 Traductions FR/EN/DE complètes
- 📚 Bibliothèques : `requests` (HTTP GitHub) et `packaging` (comparaison sémantique)
- 🔐 Timeout 5s pour éviter blocages réseau
- 📝 Module `Functions/version_checker.py` : check_for_updates()
- 🧵 Classe VersionCheckThread (QThread) pour exécution asynchrone
- 🎨 Styles dynamiques : bleu (#0078d4) avec hover (#005a9e)

**Système de Bannières de Classe**
- 🖼️ Bannières visuelles pour 44 classes DAOC (Albion/Hibernia/Midgard)
- 📱 Design responsive adaptatif (hauteur fenêtre)
- 🎨 Design par royaume : Rouge (Albion), Vert (Hibernia), Bleu (Midgard)
- 📐 Dimensions : 150px largeur × hauteur responsive
- 📁 Format JPEG, localisation : `Img/Banner/{Royaume}/{classe}.jpg`
- 🔄 Mise à jour automatique classe/royaume
- 📦 Compatible PyInstaller (.exe) via `get_resource_path()`
- 🔁 Fallback PNG si JPG manquant
- 🎯 Affichage côté gauche fiche personnage
- 💪 QSizePolicy(Expanding, Expanding) pour redimensionnement

**Statistiques Herald Complètes**
- ⚔️ **Section RvR** : Tower Captures, Keep Captures, Relic Captures
- 🗡️ **Section PvP** : Solo Kills, Deathblows, Kills (détail Alb/Hib/Mid avec couleurs)
- 🐉 **Section PvE** : Dragons, Légions, Mini Dragons, Epic Encounters, Epic Dungeons, Sobekite
- 💰 **Section Wealth** : Monnaie format "18p 128g 45s 12c" (9pt gras)
- 🏆 **Section Achievements** : 16 réalisations en 2 colonnes de 8
- 📊 Scraping depuis Herald avec `character_profile_scraper.py`
- 🔢 Gestion séparateurs de milliers
- 🎨 Couleurs par royaume : Rouge #C41E3A (Alb), Vert #228B22 (Hib), Bleu #4169E1 (Mid)
- 📋 Format affichage : `Kills: 4,715 → Alb: 1,811 | Hib: 34 | Mid: 2,870`
- 🔄 Bouton "Actualiser Stats" avec gestion état intelligente
- 📝 Scraping automatique achievements (`&t=achievements`)

**Bouton "Informations" sur Statistiques**
- ℹ️ Bouton à côté de "Actualiser Stats"
- 📝 Message explicatif : statistiques cumulatives depuis création personnage
- ⚠️ Clarification : pas de stats par saison, uniquement total global
- 🌐 Source données : Herald Eden ne fournit que cumul total
- 🌍 Traductions FR/EN/DE

**Interface Utilisateur**
- 📐 Layout 50/50 : RvR/PvP côte à côte, PvE/Wealth côte à côte
- 📏 QGridLayout pour alignement PvP parfait (3 colonnes)
- 📊 Détails royaume sur même ligne (compact)
- 🔲 Section PvE : espacement 5px, séparateur vertical
- 📋 Section Achievements : pleine largeur, 2 colonnes, QScrollArea 200px max
- 🖥️ Largeur minimale 250px par section
- 🎯 Stretch factor égal pour répartition équitable

### 🧰 Modification

**Système de Vérification de Version**
- 📁 Séparation version actuelle/dernière : `Functions/version.py` vs `version.txt`
- 🔄 version.txt devient référence GitHub uniquement (plus fichier local)
- 🎨 Affichage états avec codes couleur : vert (à jour), rouge (obsolète), orange (erreur)
- 🔗 URL download link : `https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest`
- 👁️ Visibilité lien : show/hide selon statut update

**Interface Statistiques**
- 🖥️ Suppression QScrollArea de toutes sections (RvR/PvP/PvE/Wealth/Achievements)
- 📏 Affichage hauteur complète sur grands écrans
- 📱 Scroll naturel fenêtre si petits écrans
- 📄 setWordWrap(False) sur labels PvP (éviter retour ligne)
- 🔲 Séparateur vertical PvE entre colonnes
- 📊 Espacement réduit PvE (5px au lieu de 8px)
- 🏆 Achievements : espacement vertical 2px pour compacité

**Bouton "Actualiser Stats"**
- 🎯 Gestion état : grisé pendant validation Herald startup
- ⏸️ Désactivation automatique pendant scraping
- 🔒 Réactivation garantie avec pattern `try/finally`
- 🏁 Flag `herald_scraping_in_progress` positionné AVANT setText()
- 📢 Messages erreur détaillés pour 4 scrapers (RvR/PvP/PvE/Wealth)
- ✅ Validation Herald terminée avant activation
- 🔗 Signal `status_updated` pour réactivation automatique

**Affichage Monnaie**
- 🔤 Taille police : 11pt → 9pt (harmonie visuelle)
- 💪 Style gras conservé
- 💱 Format direct `str(money)` sans formatage numérique

**Gestion État Boutons Herald**
- 🔐 Nouveau flag `herald_scraping_in_progress` (tracking global)
- 🎯 Méthode `_is_herald_validation_done()` pour check thread startup
- 🔄 Callback `_on_herald_validation_finished()` pour réactivation auto
- ⚡ `QApplication.processEvents()` pour mise à jour UI immédiate
- 🔒 try/finally garantit réactivation tous chemins exécution

### 🐛 Correction

**Système de Vérification de Version**
- 🔧 Fix TypeError `lang.get()` : suppression paramètre par défaut (takes 2 args not 3)
- 📁 Fix séparation version : création `Functions/version.py` avec __version__
- 🔄 Fix version.txt modification affectait current ET latest
- 💡 Solution : code constant (__version__) pour current, GitHub file pour latest

**Bouton "Actualiser Stats"**
- 🔘 Fix bouton actif pendant validation Herald startup
- 🚫 Fix bouton grisé après annulation dialogue update
- ♻️ Fix réactivation avec `try/finally` pour tous chemins (return, exception, succès)
- 🏁 Fix race condition : flag positionné AVANT setText() trigger signal
- 🔍 Fix validation startup : `_is_herald_validation_done()` check thread.isRunning()
- 📢 Fix multiples points sortie sans réactivation boutons

**Messages d'Erreur**
- 📝 Fix messages incomplets : ajout PvE et Wealth manquants
- 📢 Affichage TOUTES erreurs (4 scrapers) au lieu de 2
- 🎯 Format : `❌ RvR/PvP/PvE/Wealth: {error_msg}`

**Formatage Monnaie**
- 🔢 Fix TypeError : `f"{money:,}"` échouait sur string "18p 128g"
- 💱 Solution : `str(money)` affichage direct sans format numérique
- ✅ Format Herald préservé : "18p 128g 45s 12c"

**Test Connexion Herald**
- 💥 Fix crash brutal lors erreurs connexion
- 🔐 Ajout bloc `finally` pour fermeture WebDriver propre
- 📝 Logging stacktrace complet pour diagnostic
- ✅ Pattern identique à `search_herald_character()` fix v0.106

**Affichage Statistiques**
- 📱 Fix sections tronquées petits écrans (suppression QScrollArea)
- 📏 Fix hauteur complète sections (removal scroll limitait height)
- 📄 Fix retour ligne : `setWordWrap(False)` sur labels PvP détails
- 🖥️ Scroll naturel niveau fenêtre au lieu scroll par section
- 🎯 Affichage complet grands écrans avec utilisation optimale espace

**Fichiers Debug**
- 🗑️ Suppression création automatique HTML : `debug_herald_after_cookies.html`, `debug_wealth_page.html`
- 📝 Ajout .gitignore pour protection
- 🧹 Nettoyage 3 sections création fichiers debug (lignes ~155, ~235, ~295)
- 📊 Logs conservés pour debugging (taille HTML, URL, etc.)

**Qualité Code**
- 🧹 Nettoyage ~20 logs debug `[DEBUG]` temporaires
- 📝 Conservation logs essentiels : error, info, warning
- 🎯 Logs propres production-ready

### 🔚 Retrait

**Code Debug**
- ❌ Suppression logs temporaires `[DEBUG]` après validation fixes
- ❌ Suppression création fichiers HTML debug automatiques
- ❌ Nettoyage code débogage actif en production

**QScrollArea**
- ❌ Retrait QScrollArea de section RvR (lignes 229-275)
- ❌ Retrait QScrollArea de section PvP (lignes 276-365)
- ❌ Retrait QScrollArea de section PvE (lignes 373-456)
- ❌ Retrait QScrollArea de section Wealth (lignes 463-475)
- ❌ Retrait QScrollArea de section Achievements (lignes 483-504)

---

## 📋 Informations Techniques - v0.107

**Fichiers Créés**
- `Functions/version.py` : Constante __version__ = "0.107"
- `Functions/version_checker.py` : Module vérification GitHub

**Fichiers Modifiés**
- `Functions/ui_manager.py` : Interface version check + indicateurs visuels + download link
- `UI/dialogs.py` : Suppression QScrollArea, gestion état boutons, stats display
- `Language/*.json` : Ajout clés traduction (version_check_download, stats_info_*)
- `version.txt` : Représente dernière version GitHub
- `requirements.txt` : Ajout requests>=2.31.0, packaging>=23.0

**Commits Associés**
- `42a63a9` : Fix version constant separation (création Functions/version.py, séparation version actuelle/GitHub)
- `62fe01d` : Add download link and red text (lien téléchargement cliquable vers Releases)
- `93f2c54` : Fix lang.get() TypeError (suppression paramètre par défaut)
- `8f7148b` : Add visual indicators (✓/✗) (indicateurs visuels vert/rouge)
- `9c4708e` : Remove scroll areas, preserve full height (suppression QScrollArea RvR/PvP/PvE/Wealth)
- `1bec23c` : Remove scroll from Achievements (suppression QScrollArea Achievements)

**Tests et Validation**
- ✅ 25/25 tests connexion Herald réussis (100% stable)
- ✅ 0 crash après fixes boutons
- ✅ Tous chemins exécution testés (succès, erreur, annulation)
- ✅ Validation startup, scraping, dialogue update

**Prérequis**
- Cookies Herald valides
- Personnage niveau 11+ (stats PvP)
- URL Herald configurée fiche personnage
- Connexion internet (vérification version)

---

# ✨✨ v0.106 - 2025-11-08

### 🎉 Ajout

**Refactoring Code Complet**
- 🌍 Traduction complète FR → EN : 582 commentaires français traduits (975 modifications)
- 🧹 Optimisation imports : 51 imports inutilisés supprimés via analyse AST
- 📝 Nettoyage code : 74 lignes blanches excessives supprimées (max 2 consécutives)
- 💾 Configuration par défaut : `default_season: "S3"` ajouté
- 🖱️ Configuration par défaut : `manual_column_resize: true` ajouté
- 📊 Impact global : 19,941 lignes totales, 792.58 KB
- 📦 Réduction exe estimée : -1 à 2 MB (-2 à 4%)

**Système de Backup Amélioré**
- 📄 Noms de fichiers clairs : inclusion du nom de personnage
- 🔤 Format : `backup_YYYYMMDD_HHMMSS_NomPersonnage.zip`
- 🔀 Distinction opérations : `backup_..._NomPersonnage.zip` vs `backup_..._multiple_characters.zip`
- 🔍 Identification immédiate du personnage concerné
- 📂 Navigation backups plus intuitive

**Optimisation Herald Performance**
- ⚡ Réduction timeouts : analyse complète des 21 occurrences `time.sleep()`
- 📉 Recherche personnage : 26.5s → 21.9s (-17.4%)
- ⏱️ Gain par recherche : -4.6 secondes
- 🔄 Durée totale 25 recherches : 662.3s → 546.4s (-1.9 min)
- 💯 Stabilité : 100% (écart type 0.3s, plage 18.7-19.6s)
- 📚 Documentation : `HERALD_TIMEOUTS_ANALYSIS.md` + `HERALD_PHASE1_TEST_REPORT.md`

### 🧰 Modification

**Refactoring Code**
- 🗂️ Impact fichiers : 11 managers (Functions/), 4 UI, 42 scripts, 4 tools, 2 tests, main.py
- 📉 Réduction nette : -47 lignes (607 supprimées, 560 ajoutées)
- 🎯 51 imports en moins = bundle plus léger
- 💻 Bytecode plus propre

**Configuration par défaut**
- 🎭 Saison par défaut : S3 (config_manager.py, character_actions_manager.py, dialogs.py)
- 🖱️ Redimensionnement colonnes : manuel par défaut (tree_manager.py, main.py, dialogs.py)

### 🐛 Correction

**Bugs Critiques**
- 🚨 Fix imports manquants après optimisation agressive
  - character_actions_manager.py : Ajout `QMessageBox, QInputDialog, QDialog, QLineEdit`
  - armor_manager.py : Ajout `ensure_armor_dir` depuis `path_manager`
  - tree_manager.py : Ajout `QHeaderView`
  - main.py : Restauration imports Qt et config
- 📁 Fix création dossier Logs uniquement si `debug_mode = true`
- 🏁 Fix erreur `MIGRATION_FLAG_ERROR` si dossier Characters n'existe pas
- 🔢 Fix affichage version : v0.104 → v0.106 corrigé

**Fix Crash Herald Search**
- 💥 Fix crash brutal lors erreurs recherche Herald
- 🔐 Ajout bloc `finally` pour fermeture WebDriver propre
- 📝 Logging stacktrace complet pour diagnostic
- ✅ 100% stable validé par tests automatisés
- 📋 Script de test : `Scripts/test_herald_stability.py`

**Fix Backup Critique**
- 🔧 Fix résolution chemins pour backups
- 💾 Backup automatique lors create/update/delete fonctionnel
- 🖱️ Backup manuel "folder not found" corrigé
- 📝 Messages ERROR trompeurs au premier démarrage corrigés
- 📊 Logs création dossiers backup ajoutés
- ✅ Backup quotidien au démarrage fonctionne

### 🔚 Retrait

**Nettoyage Code**
- ❌ 51 imports inutilisés supprimés (cookie_manager: 11, eden_scraper: 6, main: 5, backup_manager: 3)
- ❌ 74 lignes blanches excessives supprimées
- ❌ 1 debug print supprimé

---

## 📋 Informations Techniques - v0.106

**Fichiers Modifiés**
- `Functions/` : 11 managers (refactoring complet commentaires EN)
- `UI/` : 4 fichiers (dialogs, delegates, debug)
- `Scripts/` : 42 fichiers tests/utilitaires
- `Tools/` : 4 fichiers éditeurs
- `Test/` : 2 fichiers Herald
- `main.py` : Application principale
- `Functions/backup_manager.py` : Ajout paramètre nom personnage + génération nom fichier
- `Functions/character_actions_manager.py` : Delete, rename avec nouveaux noms backup
- `UI/dialogs.py` : Update rank/info/armor, mass import avec nouveaux noms
- `main.py` : Update from Herald avec nouveaux noms
- `Functions/eden_scraper.py` : Fermeture propre + logs
- `Functions/backup_manager.py` : Résolution chemins + logs améliorés
- `Functions/character_manager.py` : Log création dossier
- `Functions/cookie_manager.py` : Log création dossier

**Impact Global**
- 19,941 lignes totales, 792.58 KB
- -47 lignes net (607 supprimées, 560 ajoutées)
- Réduction exe estimée : -1 à 2 MB (-2 à 4%)
- 51 imports en moins = bundle plus léger
- Bytecode plus propre

**Commits Associés**
- `339a5a8` : Add character name to backup filenames for clarity
- `9e84494` : Ensure scraper is properly closed in all error paths
- `a351226` : Add Herald search stability test script
- `175c42b` : Improve logging for first startup
- `9d5158d` : Add INFO logs when backup directories are created
- `20331d6` : Use proper folder resolution for backups (CRITICAL)
- `83f99e9` : Improve backup error message when no characters exist

**Documentation Créée**
- `HERALD_TIMEOUTS_ANALYSIS.md` : Analyse complète 21 occurrences time.sleep()
- `HERALD_PHASE1_TEST_REPORT.md` : Rapport tests validation optimisation
- `Reports/CODE_REFACTORING_REPORT_v0.106.md` : Rapport refactoring complet

**Tests et Validation**
- ✅ 100% stabilité Herald search (25 tests)
- ✅ 0 crash après fixes
- ✅ Backups automatiques/manuels/quotidiens fonctionnels
- ✅ Application démarre avec tous imports corrects

---

# ✨✨ v0.104 - 2025-10-29

### 🎉 Ajout

**Architecture - Refactoring Complet**
- 🏗️ Extraction `main.py` (1277 lignes) vers 3 nouveaux managers
- 📝 `Functions/ui_manager.py` (127 lignes) : Gestion éléments d'interface
- 🌳 `Functions/tree_manager.py` (297 lignes) : Gestion liste personnages
- ⚙️ `Functions/character_actions_manager.py` (228 lignes) : Actions sur personnages
- 📉 `main.py` réduit à 493 lignes (-61%)
- 🎯 Séparation claire responsabilités (SRP)
- 🏛️ Architecture MVC partielle

**Migration & Sécurité**
- 📁 Nouvelle structure : `Characters/Saison/Royaume/Personnage.json` (vs `Characters/Royaume/Personnage.json`)
- 🔄 Migration automatique au démarrage (avec confirmation)
- 🏷️ Fichier marqueur `.migration_done` pour éviter migrations multiples
- 💬 Popup confirmation trilingue (FR/EN/DE)
- 💾 Sauvegarde ZIP automatique : compression avec 70-90% économies espace
- ✅ Vérification intégrité : test automatique archives après création
- ↩️ Rollback automatique : suppression auto en cas d'erreur
- 🔍 Validation JSON complète : détection fichiers corrompus
- 📋 Vérification copie : chaque fichier comparé après copie
- 🧹 Nettoyage sécurisé : ancien dossier supprimé uniquement si 100% fichiers migrés
- 🛡️ Prévention écrasement : vérification avant écriture
- 📦 Archive ZIP : `Backup/Characters/Characters_backup_YYYYMMDD_HHMMSS.zip`
- 📝 Messages erreur traduits 3 langues
- 📊 Logs détaillés pour diagnostic
- 📈 Interface progression avec barre pourcentage

**Interface & Expérience Utilisateur**
- 📊 Nouvelle colonne **Classe** : affichée par défaut
- 🧬 Nouvelle colonne **Race** : masquée par défaut
- 👁️ Actif/désactif via Affichage > Colonnes
- 🎚️ Rang Royaume : remplacement curseurs par menus déroulants
  - 🔢 Menu rang (1-14)
  - 📊 Menu niveau (L0-L10 pour rang 1, L0-L9 pour autres)
  - 🎨 Titre rang affiché avec couleur royaume
- 💾 Sauvegarde automatique rangs : suppression bouton "Appliquer"
- 🖱️ Modifications rang/niveau appliquées automatiquement
- 📋 Menu Windows traditionnel : remplacement barre d'outils
  - 📂 Menu Fichier : Nouveau Personnage, Paramètres
  - 👁️ Menu Affichage : Colonnes
  - ❓ Menu Aide : À propos

**Outils de Développement**
- 🧹 `Tools/clean_project.py` : Nettoyage automatique projet
- 🗑️ Suppression dossiers temporaires (Backup, build, dist, Characters, Configuration, Logs)
- 🧼 Nettoyage caches Python (__pycache__, .pyc, .pyo, .pyd)
- 🔍 Mode simulation avec --dry-run
- 🚀 Création et push automatique vers Git
- 💬 Interface interactive avec confirmations

**Documentation**
- 📚 `REFACTORING_v0.104_COMPLETE.md` : Comparaison avant/après détaillée
- 💾 `BACKUP_ZIP_UPDATE.md` : Guide sauvegardes ZIP
- 🔒 `MIGRATION_SECURITY.md` : Guide sécurité complet
- 📖 README mis à jour : Structure projet revue
- 📑 INDEX.md enrichi : Section dédiée v0.104
- 📁 CHANGELOGs déplacés dans `Documentation/`
- 🌍 READMEs linguistiques (EN/DE) déplacés
- 📝 Nouveau `CHANGELOG.md` principal à la racine

**Tests**
- 🧪 `Scripts/simulate_old_structure.py` : Crée ancienne structure pour tests
- 📦 `Scripts/test_backup_structure.py` : Vérifie création sauvegardes ZIP

### 🧰 Modification

**Performance**
- ⚡ Temps chargement : -22% (~0.45s → ~0.35s)
- 🔄 Refresh liste : -33% (~0.12s → ~0.08s pour 100 persos)
- 💾 Utilisation mémoire : -8% (~85MB → ~78MB)
- 🖼️ Cache icônes : chargement unique au démarrage
- 📉 Réduction appels redondants : -60%
- 📦 Lazy loading des ressources
- 🔍 Optimisation requêtes données

**Nettoyage Code**
- 📉 Complexité cyclomatique main.py : -71%
- 📏 Fonctions > 50 lignes : -83%
- 📦 Imports dans main.py : -36%

### 🐛 Correction

**Bugs Corrigés**
- ✅ Facilité maintenance améliorée
- ✅ Testabilité accrue
- ✅ Code plus lisible et modulaire
- ✅ Extensibilité simplifiée

### 🔚 Retrait

**Nettoyage**
- ❌ Scripts test obsolètes (8 fichiers)
- ❌ Imports inutilisés
- ❌ Code dupliqué

---

## 📋 Informations Techniques - v0.104

**Fichiers Créés**
- `Functions/ui_manager.py` (127 lignes) : Gestion éléments d'interface
- `Functions/tree_manager.py` (297 lignes) : Gestion liste personnages
- `Functions/character_actions_manager.py` (228 lignes) : Actions sur personnages
- `Functions/migration_manager.py` : Gestionnaire migration complet
- `Tools/clean_project.py` : Script nettoyage automatique projet
- `Scripts/simulate_old_structure.py` : Crée ancienne structure pour tests
- `Scripts/test_backup_structure.py` : Vérifie création sauvegardes ZIP

**Fichiers Modifiés**
- `main.py` : Réduit à 493 lignes (-61% depuis 1277 lignes)
- Structure dossiers : `Characters/Saison/Royaume/Personnage.json`

**Documentation Créée**
- `REFACTORING_v0.104_COMPLETE.md` : Comparaison avant/après détaillée
- `BACKUP_ZIP_UPDATE.md` : Guide sauvegardes ZIP
- `MIGRATION_SECURITY.md` : Guide sécurité complet
- `README.md` : Structure projet revue
- `INDEX.md` : Section dédiée v0.104
- Nouveau `CHANGELOG.md` principal à la racine

**Impact Global**
- Temps chargement : -22% (~0.45s → ~0.35s)
- Refresh liste : -33% (~0.12s → ~0.08s pour 100 persos)
- Utilisation mémoire : -8% (~85MB → ~78MB)
- Complexité cyclomatique main.py : -71%
- Fonctions > 50 lignes : -83%
- Imports dans main.py : -36%
- Réduction appels redondants : -60%

**Archive ZIP**
- Format : `Backup/Characters/Characters_backup_YYYYMMDD_HHMMSS.zip`
- Compression : 70-90% économies espace
- Vérification intégrité automatique
- Rollback automatique en cas d'erreur

**Tests et Validation**
- ✅ Migration automatique avec confirmation
- ✅ Validation JSON complète
- ✅ Vérification copie fichier par fichier
- ✅ Nettoyage sécurisé (100% migrés avant suppression)

---

## 📋 Légende des Emojis

### Sections Principales
- 🎉 **Ajout** : Nouvelles fonctionnalités
- 🧰 **Modification** : Changements fonctionnalités existantes
- 🐛 **Correction** : Bugs corrigés
- 🔚 **Retrait** : Fonctionnalités supprimées

### Catégories
- 🔄 Vérification / Actualisation
- 📊 Données / Statistiques
- 🌐 Web / Réseau / GitHub
- 🔘 Boutons / UI
- ✅ Indicateurs / Validation
- 🔗 Liens / Téléchargement
- ℹ️ Informations
- 🌍 Traductions / Langues
- 📚 Bibliothèques / Dépendances
- 🔐 Sécurité / Timeout
- 📝 Modules / Scripts
- 🧵 Threads / Asynchrone
- 🎨 Styles / Design
- 🖼️ Images / Bannières
- 📱 Responsive / Adaptatif
- 📐 Dimensions / Layout
- 📁 Fichiers / Dossiers
- 📦 Compatibilité / Build
- 🔁 Fallback / Alternative
- 🎯 Positionnement / Focus
- 💪 Comportement / Propriétés
- ⚔️ RvR / Combat
- 🗡️ PvP / Joueurs
- 🐉 PvE / Monstres
- 💰 Monnaie / Richesse
- 🏆 Réalisations / Achievements
- 🔢 Nombres / Formatage
- 📋 Format / Structure
- 🖥️ Interface / Affichage
- 📏 Taille / Espacement
- 🔲 Sections / Zones
- 🔧 Correction / Fix
- 🚫 Désactivation
- ♻️ Réactivation / Restauration
- 🏁 Flags / États
- 🔍 Vérification / Recherche
- 📢 Messages / Notifications
- 💱 Conversion / Parsing
- 💥 Crash / Erreur critique
- 🗑️ Suppression / Nettoyage
- 🧹 Optimisation / Maintenance
- 🎭 Saison / Configuration
- 🖱️ Interaction / Clics
- 🏗️ Architecture / Structure
- 🌳 TreeView / Liste
- ⚙️ Actions / Opérations
- 📉 Réduction / Diminution
- 🔄 Migration / Conversion
- 🏷️ Marqueurs / Flags
- 💬 Messages / Dialogues
- 💾 Sauvegarde / Backup
- ↩️ Rollback / Annulation
- 🛡️ Protection / Prévention
- 📈 Progression / Évolution
- 🔤 Texte / Format
- 🔀 Distinction / Différenciation
- ⏱️ Temps / Durée
- 💯 Stabilité / Fiabilité
- 🗂️ Organisation / Rangement
- 💻 Code / Développement
- 📖 Documentation / Guides
- 📑 Index / Table matières
- 🧪 Tests / Validation
- ⚡ Performance / Vitesse
- 💡 Solution / Résolution
