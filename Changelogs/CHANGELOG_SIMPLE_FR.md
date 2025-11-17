# 📋 Changelog Simple - DAOC Character Management

# 📝 CHANGELOG SIMPLIFIÉ

## v0.108

### Nouveautés
- 🌐 **Profil Chrome Dédié** : Navigateur Selenium isolé dans AppData avec migration automatique des cookies
- 🗑️ **Bouton "Nettoyer Eden"** : Nouveau bouton dans Settings > Herald pour supprimer cookies et profil Chrome
- 📂 **Création Auto Dossiers Backup** : Les boutons "Ouvrir le dossier" créent maintenant automatiquement les dossiers manquants

### Améliorations
- 💾 **Optimisation Backup Cookies** : Backup uniquement du fichier cookies (~10 KB au lieu de 50+ MB), réduction de 99%
- ⚙️ **Interface Settings Simplifiée** : Suppression des champs obsolètes pour les cookies (chemin géré automatiquement)

### Corrections
- 🐛 Correction crash Settings avec cookies_path_edit manquant
- 🐛 Correction backup cookies qui disparaissait immédiatement après création
- 🌍 Correction traductions bouton "Nettoyer Eden" (FR/EN/DE)
- 🌍 Correction fenêtre "Mise à jour" personnage maintenant traduite (FR/EN/DE)

## v0.108

### 🎉 Nouveautés
- 💾 **Migration Automatique des Personnages** : Restructuration intelligente des dossiers sans intervention
  - 🔄 Détection et migration automatique : Characters/Royaume/ → Characters/Saison/Royaume/
  - 💾 Sauvegarde ZIP automatique avant migration avec validation complète
  - ✅ Vérification et normalisation de chaque fichier personnage
  - ⚙️ Exécution silencieuse au démarrage (aucune popup, aucune confirmation)
  - 🛡️ Annulation automatique en cas de problème (données préservées)
  - 📊 Suivi dans config.json pour éviter les migrations multiples
  - 🗑️ Suppression de l'ancien système avec popup (63 traductions obsolètes retirées)

### 🐛 Corrections
- 🌍 **Traductions Dynamiques** : Section version se met à jour sans redémarrage lors du changement de langue
- 🌍 **Import Herald** : Titre "Import terminé" s'affiche correctement (au lieu du nom de clé)
- 🌍 **Statistiques RvR** : Labels traduits (Tours/Forteresses/Reliques Capturées en FR, Towers/Keeps/Relics Captured en EN, etc.)
- 🌍 **Statistiques PvP/PvE** : Tous les labels traduits (Kills en Solo, Coups Fatals, Dragons Tués, etc.)
- 🗑️ **Nettoyage** : Suppression de la clé obsolète qdarkstyle (thème custom JSON utilisé maintenant)

### 🎉 Nouveautés
- ⌨️ **Raccourcis Clavier** : Ctrl+N pour créer un personnage, Ctrl+F pour rechercher sur Herald
- 🎨 **Thème Purple (Dracula)** : Nouveau thème violet/rose avec palette Dracula officielle
- 📝 **Fichier FUTURE_IMPROVEMENTS.md** : Liste des améliorations planifiées avec cases à cocher

### 🐛 Corrections
- 🛡️ **Fichier Migration** : Plus de création automatique du fichier .migration_done
- ⚡ **Recherche Herald** : Fermeture instantanée de la fenêtre (plus de latence)

### 🧹 Nettoyage
- 🗑️ Suppression des fichiers de test et documentations temporaires
- 📚 Documentation finale : CONFIG_V2_TECHNICAL_DOC.md

### 🧰 Améliorations
- 🔄 **Configuration v2** : Structure hiérarchique avec migration automatique et backup
  - 5 sections organisées (ui, folders, backup, system, game)
  - Rétrocompatibilité 100% garantie (39 clés legacy)
  - Thème par défaut : Purple | Langue par défaut : English
  - Documentation technique complète incluse
- 🎨 **Changement de Thème** : Application instantanée complète sans redémarrage
- 📋 **Colonnes** : Sauvegarde automatique des largeurs en mode manuel

### 🧰 Améliorations (Suite)
- ⚙️ **Settings Réorganisés** : Nouvelle page Sauvegardes avec statistiques temps réel et actions directes
- 💾 **Sauvegardes Intégrées** : Sauvegardes Personnages + Cookies accessibles depuis Settings (plus de menu Outils)
- 📁 **Configuration Simplifiée** : Dossier config toujours à côté de l'exécutable (sécurité)
- 🔄 **Rafraîchissement Auto** : Liste des personnages mise à jour automatiquement après changement de dossier
- 📚 **Documentation Technique** : 3 nouveaux guides détaillés (1800+ lignes)

### 🐛 Corrections
- ✅ Menus et affichage central s'adaptent correctement lors du changement Dark→Light
- ✅ Barre de menus réinitialisée aux couleurs système en thème Light
- ✅ Largeurs de colonnes mémorisées entre les sessions en mode manuel

### ✨ Ajout (Fonctionnalités Précédentes)

**Support Multilingue des Dialogues de Progression**
- 🌍 58 nouvelles traductions FR/EN/DE pour tous les dialogues de progression et messages d'import
- 📚 Documentation technique complète avec diagrammes (PROGRESS_DIALOG_SYSTEM_EN.md, 1900+ lignes)
- 🎯 Support complet de 3 langues pour l'interface utilisateur
- 🌍 2 nouvelles traductions FR/EN/DE
- 🎯 Interface 100% multilingue

### 📚 Documentation

**Documentation Technique Eden Scraping**
- 📝 3 documentations détaillées en anglais (2000+ lignes)
- 📊 Schémas graphiques ASCII des flux d'exécution
- 💡 Exemples pratiques et guides de dépannage
- 🎯 Architecture unifiée documentée

### 🐛 Correction

**Largeurs de Colonnes Non Mémorisées**
- 🛡️ Colonnes redimensionnées manuellement perdues au redémarrage
- 🔧 Sauvegarde automatique des largeurs dans config.json
- 🎯 Configuration des colonnes persistante entre sessions

**URL Manquante à l'Import**
- 🛡️ Correction bug URL Herald non sauvegardée lors de l'import de personnages
- 🔧 Ajout du fallback URL oublié lors du refactoring SearchThread
- 🎯 Les personnages importés contiennent maintenant leur URL pour les mises à jour auto

**Crash Fermeture Herald**
- 🛡️ Correction crash lors de la fermeture de la fenêtre de recherche
- 🔧 Protection complète : arrêt du thread, déconnexion signaux, gestion exceptions
- 🎯 Fermeture sécurisée à tout moment sans crash

**Erreur Formatage Messages**
- 🛡️ Correction crash "Index out of range" lors affichage messages
- 🔧 Migration vers paramètres nommés ({char_name}, {count}, {error})
- 🎯 Messages traduits affichés correctement avec valeurs dynamiques

**Freeze Fenêtre Recherche Herald**
- 🛡️ Correction fermeture lente (2-3 clics nécessaires) + freeze après import
- 🔧 Cleanup asynchrone des threads et ressources (QTimer.singleShot)
- 🎯 Fermeture instantanée (<100ms), plus de freeze, refresh/backup en arrière-plan

**Messages Import Non Traduits**
- 🛡️ Messages "Import terminé" codés en dur en français
- 🔧 6 nouvelles clés de traduction FR/EN/DE
- 🎯 Interface Herald 100% multilingue

**Comportement Incohérent Menu Contextuel**
- 🛡️ Menu contextuel affichait fenêtre vide, feuille personnage affichait message
- 🔧 Ajout vérification `has_changes()` dans gestionnaire menu contextuel
- 🎯 Comportement uniforme entre feuille personnage et menu contextuel

### 🧰 Modification

**Amélioration Recherche Herald**
- 🎨 Nouvelle fenêtre de progression avec 9 étapes détaillées
- ✅ Système de statuts visuels : En attente (⏺️), En cours (⏳), Terminée (✅)
- 📋 Toutes les étapes restent visibles avec indication de leur statut
- 🔄 Mise à jour automatique des étapes au fur et à mesure de la progression
- 🎯 Feedback visuel complet pour l'utilisateur
- 🔧 Refactoring wealth_manager.py vers fonction centralisée `_connect_to_eden_herald()`
- 📊 Documentation complète CharacterProfileScraper + WealthManager (CHARACTER_STATS_SCRAPER_EN.md, 2000+ lignes)

**Migration vers Système de Traduction**
- 🔄 Tous les textes des dialogues maintenant traduits automatiquement
- 🌐 4 dialogues migrés : Mise à jour stats, Mise à jour personnage (×2), Génération cookies
- ✅ Interface entièrement multilingue (FR/EN/DE)

### 🔚 Retrait

**Nettoyage Documentation**
- 🗑️ Suppression de 20+ fichiers obsolètes (~4000 lignes)
- 🧹 Documentation finale propre et consolidée

**Option "Vérifier la Structure"**
- 🛡️ Fonctionnalité de migration obsolète retirée
- 🎯 Interface simplifiée, option manuelle supprimée

**Rang de Royaume Incorrect dans Comparaison**
- 🛡️ Affichage du titre ("Raven Ardent") au lieu du code (5L9) causant faux changements
- 🔧 Détection automatique et recalcul depuis points de royaume
- 🎯 Comparaison correcte, plus de faux positifs

**Fenêtre Comparaison Vide**
- 🛡️ Fenêtre s'ouvrait même sans changement détecté
- 🔧 Vérification préalable + message "Personnage déjà à jour"
- 🎯 Pas de fenêtre vide, message clair

---

# ✨ v0.107

### 🎉 Ajout 

**Système de Thèmes Configurable**
- 🌓 Deux thèmes disponibles : Clair (par défaut) et Sombre
- ⚙️ Sélecteur de thème dans le menu de configuration
- 🔄 Changement de thème instantané sans redémarrage

**Système de Scaling de Texte**
- 📏 Menu déroulant de taille de texte avec 5 niveaux : 100%, 125%, 150%, 175%, 200%
- 🔄 Application instantanée sans redémarrage de l'application
- 🎯 Scaling de la police de base (9pt Segoe UI sur Windows)
- 📐 Scaling automatique des feuilles de style CSS des thèmes
- 🖋️ Scaling de tous les styles inline Python (18 labels modifiés)

**Interface Responsive**
- 📜 Zone scrollable dans la fenêtre de configuration
- 📐 Taille minimale augmentée : 600×500 pixels (au lieu de 500×400)
- 🖥️ Taille initiale confortable : 700×700 pixels
- ↕️ Scroll automatique si fenêtre trop petite

**Système de Vérification de Version**
- 🔄 Vérification automatique au démarrage de l'application
- 📊 Affichage de la version actuelle
- 🌐 Affichage de la dernière version disponible (depuis GitHub)
- 🔘 Bouton manuel "🔄 Vérifier" pour relancer la vérification
- ✅ Indicateurs visuels : ✓ vert (à jour) ou ✗ rouge (obsolète)
- 🔗 Lien de téléchargement cliquable vers GitHub Releases (si mise à jour disponible)

**Système de Bannières de Classe**
- 🖼️ Bannières visuelles pour les 44 classes DAOC (Albion, Hibernia, Midgard) [©️Eden Daoc](https://eden-daoc.net/)
- 📱 Design responsive s'adaptant à la hauteur de fenêtre
- 🔄 Mise à jour automatique lors du changement classe/royaume

**Statistiques Herald Complètes**
- ⚔️ Section RvR : Tower Captures, Keep Captures, Relic Captures
- 🗡️ Section PvP : Solo Kills, Deathblows, Kills (avec détail par royaume Alb/Hib/Mid)
- 🐉 Section PvE : Dragons, Légions, Mini Dragons, Epic Encounters, Epic Dungeons, Sobekite
- 💰 Section Wealth : Monnaie au format "18p 128g 45s 12c"
- 🏆 Section Achievements : 16 réalisations affichées

**Bouton "Informations"**
- ℹ️ Bouton à côté du bouton "Actualiser Stats"
- 📝 Message explicatif sur la nature cumulative des statistiques

### 🧰 Modification

**Bouton "Actualiser Stats"**
- 🎯 Gestion intelligente de l'état (grisé pendant validation Herald au démarrage)
- ⏸️ Désactivation automatique pendant scraping Herald
- 🔒 Réactivation garantie avec pattern `try/finally`
- 📢 Messages d'erreur détaillés pour RvR/PvP/PvE/Wealth

**Affichage Monnaie**
- 🔤 Taille de police réduite de 11pt à 9pt (meilleure harmonie visuelle)
- 💪 Style gras conservé

### 🐛 Correction

**Messages d'Erreur**
- 📝 Fix messages d'erreur incomplets (ajout PvE et Wealth manquants)
- 📢 Affichage de TOUTES les erreurs (RvR/PvP/PvE/Wealth)

**Formatage Monnaie**
- 🔢 Fix TypeError avec `f"{money:,}"` sur string
- 💱 Utilisation de `str(money)` pour affichage direct

**Test Connexion Herald**
- 💥 Fix crash lors d'erreurs de connexion
- 🔐 Ajout bloc `finally` pour fermer le driver proprement

**Affichage Statistiques**
- 📱 Fix sections RvR/PvP/PvE/Wealth/Achievements tronquées sur petits écrans
- 📏 Fix hauteur complète des sections statistiques (suppression QScrollArea)
- 📄 Ajout `setWordWrap(False)` sur labels PvP pour éviter retour à la ligne

**Fichiers Debug**
- 🗑️ Suppression des fichiers HTML créés automatiquement
- 📝 Ajout au .gitignore

### 🔚 Retrait

Aucune fonctionnalité retirée dans cette version.

---

# ✨ v0.106 - 2025-11-07

### 🎉 Ajout

**Système de Logging**
- 📋 Format unifié : `LOGGER - LEVEL - ACTION - MESSAGE`
- 🏷️ Logger BACKUP : tous les logs du module backup tagués
- 🏷️ Logger EDEN : tous les logs du scraper Eden tagués
- 🎯 Actions standardisées pour chaque module
- 🔍 Fenêtre de debug améliorée avec filtre par logger

**Sauvegarde des Cookies Eden**
- 📅 Sauvegarde quotidienne automatique des cookies au démarrage
- 📂 Section dédiée "Cookies Eden" dans la fenêtre de sauvegarde
- ⚙️ Options identiques aux Characters : compression, limite de stockage
- 💾 Bouton "Sauvegarder Maintenant" pour force backup immédiat
- 📁 Bouton "Ouvrir le dossier" pour accès direct
- 🔄 Rafraîchissement automatique après sauvegarde
- 📊 Affichage du nombre de sauvegardes et date du dernier backup

**Interface**
- 🖥️ Redesign layout fenêtre principale avec section Monnaie
- 📏 Optimisations barre status Herald (boutons 750px × 35px)
- 📋 Redesign fiche personnage (renommage Statistiques, suppression Résistances)
- 🔧 Déplacement bouton "Gérer Armor"

### 🧰 Modification

**Module Backup**
- 🏷️ Nom du personnage inclus dans les fichiers de backup
- 📝 Format : `backup_characters_20251107_143025_Update_Merlin.zip`
- 📝 Multiples : `backup_characters_20251107_143025_Update_multi.zip`
- 🔍 Identification immédiate du personnage concerné
- 📊 Logs améliorés : INFO au lieu de ERROR au premier démarrage
- ✅ Message d'erreur clair : "No characters to backup"
- 🏷️ 46+ logs tagués avec actions claires

**Herald Performance**
- ⚡ Réduction des timeouts Herald de 17.4% (-4.6 secondes par recherche)
- 🎯 Recherche personnage : 26.5s → 21.9s (-4.6 secondes)
- ✅ 25/25 tests réussis (100% stable, 0 crash)

**Interface**
- 📏 Largeur colonne URL Herald optimisée (120px minimum)
- 🔘 Boutons Herald taille uniforme dans la fiche
- 🖥️ Fenêtre Sauvegarde agrandie (1400x800)
- 📂 Layout côte à côte : Characters et Cookies Eden

**Configuration**
- 🎯 Saison par défaut : S3 au lieu de S1
- ⚙️ Colonnes manuelles : Gestion manuelle activée par défaut
- 📁 Logs conditionnels : Créés UNIQUEMENT si debug_mode activé

### 🐛 Correction

**Eden Herald**
- 💥 Fix crash brutal lors d'erreurs de recherche Herald
- 🔐 Fermeture propre du WebDriver dans tous les chemins d'erreur
- 📝 Logging du stacktrace complet pour diagnostic
- ✅ Test de stabilité : 25/25 recherches réussies (100% stable)
- 🛠️ Script de test automatisé pour validation continue
- 📁 Correction du chemin des cookies (PyInstaller fix)
- 🔄 Auto-update lors de l'import de personnages
- 📂 Dossier des cookies Herald configurable
- 🔐 Protection test connexion Herald
- 📦 Gestion erreur import Selenium
- 🔒 Protection cleanup driver

**Interface**
- 🔧 Correction de la configuration des colonnes (12 colonnes)
- 🏷️ Unification des labels ("Répertoire")
- 📊 Affichage du début des chemins
- 🔍 Système de diagnostic robuste pour arrêts inattendus
- ↕️ Tri par royaume fonctionnel (ajout RealmSortProxyModel)
- 🗺️ Mappage proxy model pour opérations triées
- ✅ Bouton Enregistrer fiche ne ferme plus la fenêtre

**Qualité Code**
- 🧹 Nettoyage code : 74 lignes blanches excessives supprimées
- 📦 Taille exe réduite : Estimation -1 à 2 MB (-2 à 4%)
- 📋 Version corrigée : Fenêtre "À Propos" affiche maintenant v0.106
- 🔧 Migration fix : Plus d'erreur "migration_done"
- 💻 67 fichiers production modifiés pour qualité optimale
- 🔒 Gestion sys.stderr/stdout None
- 🧵 Capture exceptions thread
- 📝 Logging traceback complet
- ✅ Erreurs logging backup corrigées

### 🔚 Retrait

Aucune fonctionnalité retirée dans cette version.

---

# ✨ v0.105 - 2025-11-01

### 🎉 Ajout

**Eden Scraper**
- 🌐 Module Eden Scraper complet
- 🍪 Gestionnaire de cookies avec interface GUI
- 📥 Import en masse de personnages
- 🌐 Support multi-navigateurs (Chrome, Edge, Firefox)
- 🔧 ChromeDriver système 3-tiers
- ⚙️ Configuration des navigateurs dans paramètres
- 📊 Barre d'état Herald
- 💬 Dialog d'import Herald
- 🐛 Fenêtre debug Eden
- 🎨 Coloration syntaxique des logs
- 🔄 Mise à jour de personnage depuis Herald
- 📝 Logger Eden dédié

**Interface**
- 🎯 Assignation automatique de la saison par défaut
- 🖱️ Menu contextuel pour import rapide (clic droit)
- ❓ Système d'aide intégré avec Markdown
- ✅ Validation automatique de la structure JSON
- 🔍 Vérification manuelle de la structure (menu Aide)

### 🧰 Modification

Aucune modification majeure dans cette version.

### 🐛 Correction

**Eden Scraper**
- 🔧 Correction classe changeante lors modification rang
- 📝 Normalisation des données Herald
- 💾 Correction sauvegarde des modifications Herald
- 🔍 Détection optimisée des navigateurs

### 🔚 Retrait

Aucune fonctionnalité retirée dans cette version.

---

# ✨ v0.104 - 2025-10-25

### 🎉 Ajout

**Refactoring Complet**
- 🔧 Refactoring complet en 3 managers
- ⚡ Optimisation performance (-22% chargement)
- 📉 Réduction code (-61% main.py)
- 🗂️ Nouvelle structure Season/Realm

**Migration Automatique**
- 🔄 Migration automatique avec backup ZIP
- 💬 Popup confirmation trilingue
- 📦 Sauvegardes compressées (70-90% économie)
- ✅ Vérification d'intégrité automatique
- ↩️ Rollback automatique en cas d'erreur
- 📝 Validation JSON complète

**Interface**
- 📋 Colonnes Classe et Race
- 👑 Rang de Royaume avec menus déroulants
- 💾 Sauvegarde automatique des rangs
- 📂 Menu Windows traditionnel

**Documentation**
- 🧹 Script de nettoyage de projet
- 📚 Documentation MIGRATION_SECURITY
- 🧪 Scripts de test migration
- 📖 Réorganisation documentation complète

### 🧰 Modification

Aucune modification majeure dans cette version.

### 🐛 Correction

Aucun bug corrigé dans cette version.

### 🔚 Retrait

Aucune fonctionnalité retirée dans cette version.

---

# ✨ v0.103 - 2025-10-20

### 🎉 Ajout

**Races et Classes**
- 🧬 Sélection de race et classe
- 🔍 Filtrage dynamique race/classe
- ✅ Validation race/classe automatique
- 🌍 Traductions spécialisations (FR/EN/DE)
- 📊 Système de données complet (44 classes, 18 races)
- 📚 188 spécialisations traduites
- 🎮 Support Eden (classes adaptées)

**Interface**
- 📏 Gestion largeur colonnes
- 🤖 Mode automatique/manuel pour colonnes

### 🧰 Modification

Aucune modification majeure dans cette version.

### 🐛 Correction

Aucun bug corrigé dans cette version.

### 🔚 Retrait

Aucune fonctionnalité retirée dans cette version.

---

# ✨ v0.102 - 2025-10-15

### 🎉 Ajout

**Multi-Serveur**
- 🌐 Restauration colonne serveur (Eden/Blackthorn)
- ⚙️ Configuration serveur par défaut
- 📋 Dropdown serveur dans fiche personnage
- 👁️ Colonne serveur cachée par défaut

**Renommage**
- ✏️ Renommage simplifié
- ⚡ Renommage rapide (touche Entrée)

### 🧰 Modification

Aucune modification majeure dans cette version.

### 🐛 Correction

- 💬 Messages d'erreur simplifiés
- 🔧 Correction RealmTitleDelegate

### 🔚 Retrait

Aucune fonctionnalité retirée dans cette version.

---

# ✨ v0.101 - 2025-10-10

### 🎉 Ajout

**Interface Menu Windows**
- 📂 Menu Fichier (Nouveau personnage, Paramètres)
- 👁️ Menu Affichage (Colonnes)
- ❓ Menu Aide (À propos)
- 🌍 Traductions menus (FR/EN/DE)

**Édition**
- ✏️ Édition du royaume, niveau, saison, page, guilde
- 🔄 Déplacement automatique lors changement royaume
- 🖱️ Renommage via menu contextuel

**Optimisation**
- ⚡ Optimization chargement icônes
- 🎨 Simplification interface

### 🧰 Modification

- 🌐 Serveur fixé automatiquement à "Eden"

### 🐛 Correction

Aucun bug corrigé dans cette version.

### 🔚 Retrait

- ❌ Suppression colonne serveur

---

# ✨ v0.1 - 2025-10-01

### 🎉 Ajout

**Fonctionnalités de Base**
- 👥 Gestion complète des personnages
- ➕ Création, modification, suppression, duplication
- 👑 Système de rangs de royaume
- 🌍 Interface multilingue (FR/EN/DE)
- 📋 Configuration des colonnes
- 🐛 Mode debug avec console intégrée
- 🔄 Actions en masse
- 🏰 Organisation par royaume (Albion, Hibernia, Midgard)
- 🌐 Support multi-serveur
- 📅 Système de saisons
- 🔗 Extraction web données
- 🖥️ Interface PySide6
- 💾 Persistance configuration

### 🧰 Modification

Aucune modification (version initiale).

### 🐛 Correction

Aucun bug corrigé (version initiale).

### 🔚 Retrait

Aucune fonctionnalité retirée (version initiale).
