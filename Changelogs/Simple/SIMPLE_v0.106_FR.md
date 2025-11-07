# v0.106 - Système de Logging, Sauvegarde Cookies & Optimisation Herald

## ✨ Amélioration Backup - Noms de Fichiers Clairs (NOUVEAU - 7 nov 2025)
✅ **Nom du personnage** inclus dans les fichiers de backup  
✅ Opérations simples : `backup_characters_20251107_143025_Update_Merlin.zip`  
✅ Opérations multiples : `backup_characters_20251107_143025_Update_multi.zip`  
✅ Identification immédiate du personnage concerné  
✅ Navigation dans l'historique des backups facilitée  

## 🔧 Corrections Critiques Herald Search (7 nov 2025)
✅ **FIX CRITIQUE** : Crash brutal lors d'erreurs de recherche Herald résolu  
✅ Fermeture propre du WebDriver dans tous les chemins d'erreur  
✅ Logging du stacktrace complet pour diagnostic  
✅ Test de stabilité : 25/25 recherches réussies (100% stable)  
✅ Script de test automatisé pour validation continue  

## 🔧 Corrections Critiques Backup (7 nov 2025)
✅ **FIX CRITIQUE** : Résolution des chemins pour les backups (totalement cassés)  
✅ Backups automatiques création/modification/suppression fonctionnent maintenant  
✅ Backup manuel fonctionne correctement  
✅ Logs améliorés : INFO au lieu de ERROR au premier démarrage  
✅ Logs de création des dossiers backup visibles  
✅ Message d'erreur clair : "No characters to backup" au lieu de "folder not found"  

## ⚡ Optimisation Herald Performance (7 nov 2025)
✅ Réduction des timeouts Herald de 18% (-4 secondes par opération)  
✅ Test connexion : 11s → 9s (-2 secondes)  
✅ Recherche personnage : 12s → 10s (-2 secondes)  
✅ 100% stable - Approche conservatrice validée  
✅ Documentation complète du diagnostic (HERALD_TIMEOUTS_ANALYSIS.md)  
✅ Exclusion fichier debug Herald du versioning (.gitignore)  

## 🍪 Sauvegarde des Cookies Eden
✅ Sauvegarde quotidienne automatique des cookies au démarrage  
✅ Section dédiée "Cookies Eden" dans la fenêtre de sauvegarde  
✅ Options identiques aux Characters : compression, limite de stockage  
✅ Bouton "Sauvegarder Maintenant" pour force backup immédiat  
✅ Bouton "Ouvrir le dossier" pour accéder directement au dossier  
✅ Rafraîchissement automatique après sauvegarde  
✅ Affichage du nombre de sauvegardes et date du dernier backup  

## 🔧 Nouveau Système de Logging
✅ Format unifié : `LOGGER - LEVEL - ACTION - MESSAGE`  
✅ Logger BACKUP : tous les logs du module backup tagués  
✅ Logger EDEN : tous les logs du scraper Eden tagués  
✅ Actions standardisées pour chaque module  
✅ Fenêtre de debug améliorée avec filtre par logger  

## 🛠️ Log Source Editor (Nouvel Outil)
✅ Scanner de code source pour trouver tous les logs  
✅ Éditeur interactif (table + panneau d'édition)  
✅ Détection de `logger.xxx()` et `log_with_action()`  
✅ ComboBox d'actions avec historique et auto-complétion  
✅ Raccourcis clavier (Enter, Ctrl+Enter)  
✅ Filtres par logger, level, logs modifiés  
✅ Sauvegarde directe dans les fichiers source  
✅ Mémorisation du dernier projet édité  
✅ Statistiques en temps réel  

## 🔍 Corrections Eden Scraping
✅ Correction du chemin des cookies (PyInstaller fix)  
✅ Auto-update lors de l'import de personnages  
✅ Dossier des cookies Herald configurable  

## 🧬 Authentification Herald - Détection Simplifiée & Fiable
✅ Détection d'authentification basée sur un seul critère définitif  
✅ Message d'erreur 'The requested page "herald" is not available.' = NOT CONNECTED  
✅ Absence du message d'erreur = CONNECTED (peut scraper les données)  
✅ Logique cohérente entre `test_eden_connection()` et `load_cookies()`  
✅ Cookies invalidés correctement détectés et signalés  
✅ Tests validés avec environ 58 résultats de recherche Herald  

## 🎛️ Contrôle des Boutons Herald
✅ Boutons "Actualiser" et "Recherche Herald" automatiquement désactivés  
✅ Désactivation quand aucun cookie n'est détecté  
✅ Désactivation quand les cookies sont expirés  
✅ État du bouton synchronisé avec le statut de connexion  
✅ Message utilisateur clair : "Aucun cookie détecté"  

## 📝 Backup Module
✅ 46+ logs tagués avec actions claires  
✅ Actions : INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  
✅ Logs de debug pour traçabilité complète  
✅ Support complet pour cookies backup avec policies de rétention  

## 🎨 Interface - Fenêtre Sauvegarde
✅ Layout côte à côte : Characters et Cookies Eden  
✅ Fenêtre agrandie pour accommoder les deux sections (1400x800)  
✅ Rafraîchissement intelligent des infos après sauvegarde  
✅ Boutons "Ouvrir le dossier" pour accès direct (Windows/Mac/Linux)  

## 🎨 Interface - Général
✅ Correction de la configuration des colonnes (12 colonnes)  
✅ Unification des labels ("Répertoire")  
✅ Affichage du début des chemins  
✅ Système de diagnostic robuste pour les arrêts inattendus  
✅ **Tri par royaume fonctionnel** (ajout RealmSortProxyModel)  
✅ **Largeur colonne URL Herald optimisée** (120px minimum)  
✅ **Mappage proxy model** pour opérations triées  
✅ **Bouton Enregistrer fiche** ne ferme plus la fenêtre  
✅ **Boutons Herald taille uniforme** dans la fiche  
✅ **Redesign layout fenêtre principale** avec section Monnaie  
✅ **Optimisations barre status Herald** (boutons 750px × 35px)  
✅ **Redesign fiche personnage** (renommage Statistiques, suppression Résistances, déplacement Gérer Armor)  

## 🐛 Corrections de Bugs - Stabilité .exe PyInstaller
✅ **Gestion sys.stderr/stdout None** - Correction crash noconsole (AttributeError sur flush)  
✅ **Protection test connexion Herald** - Prévention crashs silencieux avec logging complet  
✅ **Gestion erreur import Selenium** - Messages d'erreur explicites pour modules manquants  
✅ **Protection cleanup driver** - driver.quit() sécurisé avec vérifications None  
✅ **Capture exceptions thread** - Erreurs EdenStatusThread ne crashent plus l'application  
✅ **Logging traceback complet** - Toutes erreurs loguées dans debug.log pour dépannage  
✅ **Erreurs logging backup corrigées** - Messages d'erreur appropriés au lieu de placeholders "error_msg" littéraux  

## 🧹 Nettoyage du Répertoire
✅ Suppression de 13 scripts debug temporaires  
✅ Suppression de 3 fichiers HTML de débogage  
✅ Repository clean et maintainable  
✅ Optimisation des performances  

## 📚 Documentation
✅ Nettoyage et réorganisation du système CHANGELOGs