# 📋 Changelog Simple - DAOC Character Management

# ✨ v0.107 - 2025-11-10

### 🎉 Ajout 

**Système de Vérification de Version**
- 🔄 Vérification automatique au démarrage de l'application
- 📊 Affichage de la version actuelle (depuis `Functions/version.py`)
- 🌐 Affichage de la dernière version disponible (depuis GitHub)
- 🔘 Bouton manuel "🔄 Vérifier" pour relancer la vérification
- ⚡ Thread en arrière-plan (non-bloquant, timeout 5s)
- ✅ Indicateurs visuels : ✓ vert (à jour) ou ✗ rouge (obsolète)
- 🔗 Lien de téléchargement cliquable vers GitHub Releases (si mise à jour disponible)
- ℹ️ Section "Informations" (renommage de "Monnaie")
- 🌍 Support multilingue (FR/EN/DE)

**Système de Bannières de Classe**
- 🖼️ Bannières visuelles pour les 44 classes DAOC (Albion, Hibernia, Midgard)
- 📱 Design responsive s'adaptant à la hauteur de fenêtre
- 🔄 Mise à jour automatique lors du changement classe/royaume
- 📦 Compatible PyInstaller (.exe)
- 🔁 Fallback sur PNG si JPG manquant

**Statistiques Herald Complètes**
- ⚔️ Section RvR : Tower Captures, Keep Captures, Relic Captures
- 🗡️ Section PvP : Solo Kills, Deathblows, Kills (avec détail par royaume Alb/Hib/Mid)
- 🐉 Section PvE : Dragons, Légions, Mini Dragons, Epic Encounters, Epic Dungeons, Sobekite
- 💰 Section Wealth : Monnaie au format "18p 128g 45s 12c"
- 🏆 Section Achievements : 16 réalisations affichées en 2 colonnes de 8

**Bouton "Informations"**
- ℹ️ Bouton à côté du bouton "Actualiser Stats"
- 📝 Message explicatif sur la nature cumulative des statistiques
- ⚠️ Clarification : pas de stats par saison, uniquement total global
- 🌍 Support multilingue (FR/EN/DE)

### 🧰 Modification

**Interface Statistiques**
- 📐 Layout 50/50 pour sections RvR/PvP et PvE/Monnaies
- 📏 Alignement PvP avec QGridLayout pour un affichage parfait
- 📊 Détails royaume sur la même ligne (plus compact)
- 🔲 Section PvE avec espacement réduit (5px) et séparateur vertical
- 📋 Section Réalisations en pleine largeur avec 2 colonnes
- 🖥️ Suppression des QScrollArea (affichage complet en hauteur)

**Bouton "Actualiser Stats"**
- 🎯 Gestion intelligente de l'état (grisé pendant validation Herald au démarrage)
- ⏸️ Désactivation automatique pendant scraping Herald
- 🔒 Réactivation garantie avec pattern `try/finally`
- 📢 Messages d'erreur détaillés pour RvR/PvP/PvE/Wealth

**Affichage Monnaie**
- 🔤 Taille de police réduite de 11pt à 9pt (meilleure harmonie visuelle)
- 💪 Style gras conservé

### 🐛 Correction

**Système de Vérification de Version**
- 🔧 Fix TypeError dans `lang.get()` (suppression paramètre par défaut)
- 📁 Fix séparation version actuelle/dernière version (création `Functions/version.py`)

**Bouton "Actualiser Stats"**
- 🔘 Fix bouton restant actif pendant validation Herald au démarrage
- 🚫 Fix bouton restant grisé après annulation dialogue de mise à jour
- ♻️ Fix réactivation avec bloc `try/finally` pour tous les chemins d'exécution
- 🏁 Fix flag `herald_scraping_in_progress` positionné avant `setText()`

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
