# v0.106 - Système de Logging, Sauvegarde Cookies & Améliorations

## 🍪 Sauvegarde des Cookies Eden (NOUVEAU)
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

## 🧹 Nettoyage du Répertoire
✅ Suppression de 13 scripts debug temporaires  
✅ Suppression de 3 fichiers HTML de débogage  
✅ Repository clean et maintainable  
✅ Optimisation des performances  

## 📚 Documentation
✅ Nettoyage et réorganisation du système CHANGELOGs
✅ Système de diagnostic robuste pour les arrêts inattendus  

## 📚 Documentation
✅ Nettoyage et réorganisation du système CHANGELOGs