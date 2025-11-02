# v0.106 - SystÃ¨me de Logging, Sauvegarde Cookies & AmÃ©liorations

## ðŸª Sauvegarde des Cookies Eden (NOUVEAU)
âœ… Sauvegarde quotidienne automatique des cookies au dÃ©marrage  
âœ… Section dÃ©diÃ©e "Cookies Eden" dans la fenÃªtre de sauvegarde  
âœ… Options identiques aux Characters : compression, limite de stockage  
âœ… Bouton "Sauvegarder Maintenant" pour force backup immÃ©diat  
âœ… Bouton "Ouvrir le dossier" pour accÃ©der directement au dossier  
âœ… RafraÃ®chissement automatique aprÃ¨s sauvegarde  
âœ… Affichage du nombre de sauvegardes et date du dernier backup  

## ðŸ”§ Nouveau SystÃ¨me de Logging
âœ… Format unifiÃ© : `LOGGER - LEVEL - ACTION - MESSAGE`  
âœ… Logger BACKUP : tous les logs du module backup taguÃ©s  
âœ… Logger EDEN : tous les logs du scraper Eden taguÃ©s  
âœ… Actions standardisÃ©es pour chaque module  
âœ… FenÃªtre de debug amÃ©liorÃ©e avec filtre par logger  

## ðŸ› ï¸ Log Source Editor (Nouvel Outil)
âœ… Scanner de code source pour trouver tous les logs  
âœ… Ã‰diteur interactif (table + panneau d'Ã©dition)  
âœ… DÃ©tection de `logger.xxx()` et `log_with_action()`  
âœ… ComboBox d'actions avec historique et auto-complÃ©tion  
âœ… Raccourcis clavier (Enter, Ctrl+Enter)  
âœ… Filtres par logger, level, logs modifiÃ©s  
âœ… Sauvegarde directe dans les fichiers source  
âœ… MÃ©morisation du dernier projet Ã©ditÃ©  
âœ… Statistiques en temps rÃ©el  

## ðŸ” Corrections Eden Scraping
âœ… Correction du chemin des cookies (PyInstaller fix)  
âœ… Auto-update lors de l'import de personnages  
âœ… Dossier des cookies Herald configurable  

## ðŸ“ Backup Module
âœ… 46+ logs taguÃ©s avec actions claires  
âœ… Actions : INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  
âœ… Logs de debug pour traÃ§abilitÃ© complÃ¨te  
âœ… Support complet pour cookies backup avec policies de rÃ©tention  

## ðŸŽ¨ Interface - FenÃªtre Sauvegarde
âœ… Layout cÃ´te Ã  cÃ´te : Characters et Cookies Eden  
âœ… FenÃªtre agrandie pour accommoder les deux sections (1400x800)  
âœ… RafraÃ®chissement intelligent des infos aprÃ¨s sauvegarde  
âœ… Boutons "Ouvrir le dossier" pour accÃ¨s direct (Windows/Mac/Linux)  

## ðŸŽ¨ Interface - GÃ©nÃ©ral
âœ… Correction de la configuration des colonnes (12 colonnes)  
âœ… Unification des labels ("RÃ©pertoire")  
âœ… Affichage du dÃ©but des chemins  
âœ… SystÃ¨me de diagnostic robuste pour les arrÃªts inattendus  

## ðŸ“š Documentation
âœ… Nettoyage et rÃ©organisation du systÃ¨me CHANGELOGs
