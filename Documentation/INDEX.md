# Documentation DAOC Character Manager

Bienvenue dans la documentation complète du gestionnaire de personnages DAOC.

## 📚 Table des Matières

### 🇫🇷 Documentation Française

1. **[Interface Menu Windows](INTERFACE_MENU_FR.md)**
   - Structure des menus (Fichier, Action, Affichage, Aide)
   - Utilisation de l'interface
   - Support multilingue
   - Avantages par rapport à une toolbar

2. **[Menu Action](ACTION_MENU_FR.md)**
   - Accès rapide aux résistances d'armure
   - Gestion des armures depuis le menu
   - Raccourcis et fonctionnalités

3. **[Configuration des Colonnes](CONFIGURATION_COLONNES_FR.md)**
   - Personnalisation de l'affichage des colonnes
   - Masquer/afficher les colonnes souhaitées
   - Gestion de la persistance

4. **[Système Realm Ranks](REALM_RANKS_FR.md)**
   - Affichage des rangs et titres de royaume
   - Ajustement manuel via sliders
   - Calcul automatique basé sur les RP
   - Titres colorés par royaume

4. **[Gestionnaire de Données](DATA_MANAGER_FR.md)**
   - Structure des données
   - Extraction depuis le site officiel DAOC
   - API du Data Manager
   - Exemples d'utilisation

6. **[Dossier Data](DATA_FOLDER_FR.md)**
   - Description du contenu du dossier Data
   - Format des fichiers JSON
   - Maintenance et mise à jour
   - Extensions futures

7. **[Gestion des Armures](ARMOR_MANAGEMENT_FR.md)**
   - Architecture du système de gestion des armures
   - API ArmorManager
   - Configuration et chemins
   - Tests et développement

8. **[Guide Utilisateur - Gestion des Armures](ARMOR_MANAGEMENT_USER_GUIDE_FR.md)**
   - Comment uploader des fichiers d'armure
   - Visualisation et suppression
   - Configuration du dossier
   - Astuces et bonnes pratiques

### 🇬🇧 English Documentation

1. **[Windows Menu Interface](INTERFACE_MENU_EN.md)**
   - Menu structure (File, View, Help)
   - Interface usage
   - Multilingual support
   - Advantages over toolbar

2. **[Column Configuration](COLUMN_CONFIGURATION_EN.md)**
   - Customize column display
   - Show/hide desired columns
   - Persistence management

3. **[Realm Ranks System](REALM_RANKS_EN.md)**
   - Display realm ranks and titles
   - Manual adjustment via sliders
   - Automatic calculation based on RP
   - Colored titles by realm

4. **[Data Manager](DATA_MANAGER_EN.md)**
   - Data structure
   - Extraction from official DAOC website
   - Data Manager API
   - Usage examples

5. **[Data Folder](DATA_FOLDER_EN.md)**
   - Data folder content description
   - JSON file format
   - Maintenance and updates
   - Future extensions

## 🚀 Démarrage Rapide / Quick Start

### Installation

```bash
# Installer les dépendances / Install dependencies
pip install -r requirements.txt

# Lancer l'application / Run application
python main.py
```

### Mise à jour des données / Data Update

```bash
# Mettre à jour les Realm Ranks / Update Realm Ranks
python scrape_realm_ranks.py
```

## 🎯 Fonctionnalités Principales / Main Features

- ✅ **Gestion complète des personnages** / Complete character management
- 🏆 **Système Realm Ranks** avec affichage coloré / Realm Ranks system with colored display
- 📋 **Colonnes configurables** / Configurable columns
- 📁 **Gestion des armures** avec upload et organisation automatique / Armor management with upload and auto-organization
- 🌍 **Multi-langue** : FR, EN, DE / Multi-language
- 🎨 **Thèmes** : Clair/Sombre / Light/Dark themes
- 🔧 **Configuration avancée** / Advanced configuration

## 📖 Structure de la Documentation

```
Documentation/
├── INDEX.md                                 # Ce fichier / This file
├── CONFIGURATION_COLONNES_FR.md             # Config colonnes (FR)
├── COLUMN_CONFIGURATION_EN.md               # Column config (EN)
├── REALM_RANKS_FR.md                        # Realm Ranks (FR)
├── REALM_RANKS_EN.md                        # Realm Ranks (EN)
├── DATA_MANAGER_FR.md                       # Data Manager (FR)
├── DATA_MANAGER_EN.md                       # Data Manager (EN)
├── DATA_FOLDER_FR.md                        # Dossier Data (FR)
├── DATA_FOLDER_EN.md                        # Data Folder (EN)
├── ARMOR_MANAGEMENT_FR.md                   # Gestion des Armures (FR)
└── ARMOR_MANAGEMENT_USER_GUIDE_FR.md        # Guide Utilisateur Armures (FR)
```

## 🔗 Liens Utiles / Useful Links

- [README Principal / Main README](../README.md)
- [Site Officiel DAOC](https://www.darkageofcamelot.com)
- [Realm Ranks Officiels](https://www.darkageofcamelot.com/realm-ranks)

## 💡 Aide / Help

Si vous rencontrez des problèmes, consultez :
- Les sections "Dépannage" de chaque document
- Les logs dans `Logs/debug.log` (si mode debug activé)

If you encounter issues, check:
- "Troubleshooting" sections in each document
- Logs in `Logs/debug.log` (if debug mode enabled)

---

**Version** : 0.105  
**Date** : Décembre 2024 / December 2024  
**Auteur / Author** : DAOC Character Manager Team
