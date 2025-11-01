# v0.106 - Système de Logging & Outils de Développement

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

## 📝 Backup Module
✅ 46+ logs tagués avec actions claires  
✅ Actions : INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  
✅ Logs de debug pour traçabilité complète  

## 🎨 Interface
✅ Correction de la configuration des colonnes (12 colonnes)  
✅ Unification des labels ("Répertoire")  
✅ Affichage du début des chemins  
✅ Système de diagnostic robuste pour les arrêts inattendus  

## 📚 Documentation
✅ Nettoyage et réorganisation du système CHANGELOGs