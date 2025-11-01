# Documentation DAOC Character Manager - Index

## Documentation Générale

### Français 🇫🇷
- [README Principal](../README.md)
- [Guide de Configuration](CONFIGURATION_COLONNES_FR.md)
- [Dossier Data](DATA_FOLDER_FR.md)
- [Gestionnaire de Données](DATA_MANAGER_FR.md)
- [Menus d'Interface](INTERFACE_MENU_FR.md)
- [Gestion des Armures - Guide Utilisateur](ARMOR_MANAGEMENT_USER_GUIDE_FR.md)
- [Gestion des Armures - Technique](ARMOR_MANAGEMENT_FR.md)
- [Realm Ranks](REALM_RANKS_FR.md)

### English 🇬🇧
- [Main README](README_EN.md)
- [Column Configuration](COLUMN_CONFIGURATION_EN.md)
- [Data Folder](DATA_FOLDER_EN.md)
- [Data Manager](DATA_MANAGER_EN.md)
- [Interface Menus](INTERFACE_MENU_EN.md)
- [Realm Ranks](REALM_RANKS_EN.md)

### Deutsch 🇩🇪
- [Haupt-README](README_DE.md)
- [Änderungsprotokoll](CHANGELOG_DE.md)

---

## Eden Herald Integration 🌐

### Phase 1 : Gestion des Cookies (Complète ✅)

#### Français 🇫🇷
- **[Gestionnaire de Cookies](COOKIE_MANAGER_FR.md)** - Guide complet
  - Génération de cookies OAuth Discord
  - Validation et test de connexion
  - Import/Export de cookies
  - Interface utilisateur détaillée
  
- **[Eden Scraper](EDEN_SCRAPER_FR.md)** - API de scraping
  - Classe EdenScraper
  - Scraping de personnages
  - Recherche dans le Herald
  - Exemples d'utilisation
  
- **[Phase 1 Terminée](PHASE1_COMPLETE_FR.md)** - Résumé complet
  - Objectifs atteints
  - Fichiers créés/modifiés
  - Tests effectués
  - Problèmes résolus

#### English 🇬🇧
- **[Cookie Manager](COOKIE_MANAGER_EN.md)** - Complete guide
- **[Eden Scraper](EDEN_SCRAPER_EN.md)** - Scraping API
- **[Phase 1 Complete](PHASE1_COMPLETE_EN.md)** - Full summary

#### Deutsch 🇩🇪
- **[Cookie-Manager](COOKIE_MANAGER_DE.md)** - Vollständiger Leitfaden
- **[Eden Scraper](EDEN_SCRAPER_DE.md)** - Scraping-API
- **[Phase 1 Abgeschlossen](PHASE1_COMPLETE_DE.md)** - Vollständige Zusammenfassung

---

## Historique et Développement

### Changelogs
- [CHANGELOG Français](../CHANGELOG.md)
- [CHANGELOG English](CHANGELOG_EN.md)
- [CHANGELOG Deutsch](CHANGELOG_DE.md)

### Rapports de Développement
- [Résumé de la Migration v0.104](MIGRATION_MULTILANG_UPDATE.md)
- [Refactoring Complet v0.104](REFACTORING_FINAL_REPORT_v0.104.md)
- [Rapport de Vérification](VERIFICATION_RAPPORT.md)
- [Mise à Jour du 29 Octobre 2025](UPDATE_SUMMARY_29OCT2025.md)

### Documentation Technique
- [Implémentation Classes/Races](CLASSES_RACES_IMPLEMENTATION.md)
- [Utilisation Classes/Races](CLASSES_RACES_USAGE.md)
- [Sécurité de la Migration](MIGRATION_SECURITY.md)
- [Confirmation de Migration](MIGRATION_CONFIRMATION_UPDATE.md)

### Guides d'Implémentation
- [Menu Action](ACTION_MENU_IMPLEMENTATION_SUMMARY.md)
- [Résumé Gestion Armures v0.105](IMPLEMENTATION_SUMMARY_ARMOR_v0.105.md)
- [Intégration Eden Scraper Phase 1](EDEN_SCRAPER_INTEGRATION_PHASE1.md)

### Corrections et Mises à Jour
- [Correction Format HTML](HTML_FORMAT_FIX.md)
- [Mise à Jour Génération Cookies](COOKIE_GENERATION_UPDATE.md)
- [Mise à Jour UX Cookie Manager](COOKIE_MANAGER_UX_UPDATE.md)
- [Correction Import Cookies](IMPORT_COOKIES_FIX.md)
- [Mise à Jour Backup ZIP](BACKUP_ZIP_UPDATE.md)
- [Correction Icônes](../Scripts/CORRECTIONS_ICONES.md)

---

## Outils et Scripts

### Scripts de Test
- `Scripts/test_eden_cookies.py` - Validation des cookies Eden
- `Scripts/test_cookie_manager.py` - Test du gestionnaire de cookies
- `Scripts/test_eden_connection.py` - Test de connexion multi-URLs
- `Scripts/test_herald_url.py` - Test de l'URL Herald spécifique
- `Scripts/debug_selenium_cookies.py` - Debug visuel Selenium

### Utilitaires
- `Scripts/example_usage_scraper_eden.py` - Exemple d'utilisation du scraper
- `Scripts/fix_icon.py` - Correction d'encodage UTF-8 des icônes
- `Scripts/check_png.py` - Vérification des fichiers PNG

---

## Structure du Projet

### Dossiers Principaux
```
DAOC-Character-Management/
├── Configuration/          # Fichiers de config et cookies
│   ├── config.json
│   └── eden_cookies.pkl   # Cookies d'authentification Eden
├── Data/                   # Données de référence du jeu
│   ├── armor_resists.json
│   ├── classes_races.json
│   ├── classes_races_stats.json
│   └── realm_ranks_*.json
├── Documentation/          # Ce dossier
├── Functions/              # Logique métier
│   ├── cookie_manager.py  # Gestion cookies Eden
│   └── eden_scraper.py    # Scraping Herald
├── UI/                     # Interface utilisateur
│   └── dialogs.py         # Fenêtres de dialogue
├── Scripts/                # Utilitaires et tests
└── Language/               # Fichiers de traduction
    ├── fr.json
    ├── en.json
    └── de.json
```

### Modules Clés
- **Functions/** : Managers pour la logique métier
- **UI/** : Composants d'interface PySide6
- **Data/** : Données de référence DAOC
- **Configuration/** : Paramètres utilisateur et cookies
- **Language/** : Traductions multilingues

---

## Guide de Contribution

### Ajouter une nouvelle fonctionnalité
1. Créer le code dans `Functions/` ou `UI/`
2. Ajouter les tests dans `Scripts/test_*.py`
3. Documenter en 3 langues (FR/EN/DE)
4. Mettre à jour l'INDEX.md

### Standards de documentation
- **Français** : Documentation principale complète
- **English** : Version traduite complète
- **Deutsch** : Version traduite complète
- Format Markdown avec titres hiérarchisés
- Exemples de code avec syntaxe Python
- Captures d'écran pour l'UI si pertinent

---

## Prochaines Étapes

### Phase 2 : Import de Personnages (À venir)
- Import depuis le Herald Eden
- Mapping des données Herald ↔ Application
- Synchronisation des personnages
- Interface de recherche
- Cache des données scrapées

### Améliorations Planifiées
- Optimisations de performance
- Tests automatisés complets
- Intégration CI/CD
- Documentation API complète

---

## Support et Contact

Pour toute question ou problème :
1. Consulter la documentation appropriée ci-dessus
2. Vérifier les logs dans `Logs/`
3. Tester avec les scripts de `Scripts/test_*.py`
4. Consulter le CHANGELOG pour les modifications récentes

---

**Dernière mise à jour** : 29 octobre 2025  
**Version** : 0.105 (Phase 1 Eden Integration complète)
