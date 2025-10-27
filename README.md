# DAOC - Gestionnaire de Personnages

Application de gestion de personnages pour Dark Age of Camelot (DAOC), développée en Python avec PySide6.

## 🎮 Fonctionnalités

### Gestion des Personnages
- ✅ **Créer** de nouveaux personnages
- ✅ **Renommer** des personnages existants
- ✅ **Dupliquer** des personnages
- ✅ **Supprimer** des personnages (individuellement ou en masse)
- ✅ **Afficher** les détails complets de chaque personnage

### Organisation
- 📁 Organisation par **Royaume** (Albion, Hibernia, Midgard)
- 🏷️ Filtrage par **Saison** (S1, S2, S3, etc.)
- 🖥️ Gestion multi-**Serveur** (Eden, Blackthorn, etc.)
- 📊 Tableau avec tri par colonnes

### Realm Ranks (Rangs de Royaume)
- 🏆 **Affichage** du rang et du titre de royaume
- 📈 **Ajustement manuel** du rang (Rank 1-14, Levels 1-9/10)
- 🎨 **Titres colorés** selon le royaume
- 📊 **Calcul automatique** basé sur les Realm Points

### Configuration Avancée
- 🌍 **Multi-langue** : Français, English, Deutsch
- 🔧 **Personnalisation** des chemins (personnages, logs, config)
- 📋 **Colonnes configurables** : Masquer/afficher les colonnes souhaitées
- 🐛 **Mode Debug** avec console intégrée

## 📋 Colonnes Configurables

Vous pouvez personnaliser l'affichage des colonnes via le bouton **Colonnes** dans la barre d'outils.

Colonnes disponibles :
- **Sélection** : Case à cocher pour les actions en masse
- **Royaume** : Icône du royaume
- **Saison** : Saison du personnage
- **Serveur** : Serveur du personnage
- **Nom** : Nom du personnage
- **Niveau** : Niveau du personnage
- **Rang** : Rang de royaume (ex: 5L7)
- **Titre** : Titre du rang (ex: Challenger)

Voir [Documentation/COLUMN_CONFIGURATION_FR.md](Documentation/CONFIGURATION_COLONNES_FR.md) (FR) ou [Documentation/COLUMN_CONFIGURATION_EN.md](Documentation/COLUMN_CONFIGURATION_EN.md) (EN) pour plus de détails.

## 🚀 Installation

### Prérequis
- Python 3.13 ou supérieur (⚠️ PySide6 n'est pas compatible avec Python 3.14+)
- Windows, macOS ou Linux

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement de l'application

```bash
python main.py
```

## 📦 Dépendances

- **PySide6** : Interface graphique Qt6
- **requests** : Requêtes HTTP pour le web scraping
- **beautifulsoup4** : Parsing HTML
- **lxml** : Parser XML/HTML
- **urllib3** : Gestion des requêtes HTTP

## 📊 Données Realm Ranks

Pour mettre à jour les données de Realm Ranks depuis le site officiel DAOC :

```bash
python scrape_realm_ranks.py
```

Voir [Documentation/DATA_MANAGER_FR.md](Documentation/DATA_MANAGER_FR.md) (FR) ou [Documentation/DATA_MANAGER_EN.md](Documentation/DATA_MANAGER_EN.md) (EN) pour plus d'informations sur la gestion des données.

## 📚 Documentation

Documentation complète disponible dans le dossier `Documentation/` :

### Français 🇫🇷
- [Configuration des Colonnes](Documentation/CONFIGURATION_COLONNES_FR.md)
- [Système Realm Ranks](Documentation/REALM_RANKS_FR.md)
- [Gestionnaire de Données](Documentation/DATA_MANAGER_FR.md)
- [Dossier Data](Documentation/DATA_FOLDER_FR.md)

### English 🇬🇧
- [Column Configuration](Documentation/COLUMN_CONFIGURATION_EN.md)
- [Realm Ranks System](Documentation/REALM_RANKS_EN.md)
- [Data Manager](Documentation/DATA_MANAGER_EN.md)
- [Data Folder](Documentation/DATA_FOLDER_EN.md)

## �🗂️ Structure du Projet

```
DAOC---Gestion-des-personnages/
├── main.py                      # Application principale
├── requirements.txt             # Dépendances Python
├── scrape_realm_ranks.py        # Script d'extraction des rangs
├── Characters/                  # Données des personnages
│   ├── Albion/
│   ├── Hibernia/
│   └── Midgard/
├── Configuration/               # Fichiers de configuration
│   └── config.json
├── Data/                        # Données de jeu
│   └── realm_ranks.json
├── Documentation/               # Documentation complète (FR/EN)
│   ├── INDEX.md
│   ├── CONFIGURATION_COLONNES_FR.md
│   ├── COLUMN_CONFIGURATION_EN.md
│   ├── REALM_RANKS_FR.md
│   ├── REALM_RANKS_EN.md
│   ├── DATA_MANAGER_FR.md
│   ├── DATA_MANAGER_EN.md
│   ├── DATA_FOLDER_FR.md
│   └── DATA_FOLDER_EN.md
├── Functions/                   # Modules Python
│   ├── character_manager.py
│   ├── config_manager.py
│   ├── data_manager.py
│   ├── language_manager.py
│   ├── logging_manager.py
│   └── path_manager.py
├── Img/                         # Images et icônes
├── Language/                    # Fichiers de traduction
│   ├── fr.json
│   ├── en.json
│   └── de.json
└── Logs/                        # Fichiers de logs
```

## ⚙️ Configuration

La configuration est accessible via le bouton ⚙️ dans la barre d'outils.

### Options disponibles :
- 📁 **Répertoires** : Personnages, Configuration, Logs
- 🌍 **Langue** : Français, English, Deutsch
- 🎨 **Thème** : Clair / Sombre
- 🖥️ **Serveur par défaut** : Eden, Blackthorn, etc.
- 📅 **Saison par défaut** : S1, S2, S3, etc.
- 🐛 **Mode Debug** : Activer/désactiver les logs détaillés

## 🎯 Utilisation

### Créer un Personnage
1. Cliquez sur le bouton **+** (Nouveau personnage)
2. Entrez le nom, choisissez le royaume, la saison et le serveur
3. Cliquez sur "OK"

### Ajuster le Rang de Royaume
1. Double-cliquez sur un personnage pour ouvrir sa feuille
2. Utilisez les sliders pour ajuster le rang (1-14) et le niveau (1-9/10)
3. Cliquez sur "Appliquer ce rang" pour sauvegarder

### Configurer les Colonnes Visibles
1. Cliquez sur le bouton **Colonnes** (icône de liste)
2. Cochez/décochez les colonnes à afficher
3. Cliquez sur "OK" pour sauvegarder

### Actions en Masse
1. Cochez les personnages dans la colonne "Sélection"
2. Utilisez le menu déroulant "Actions en masse"
3. Sélectionnez "Supprimer la sélection" et cliquez sur "Exécuter"

## 🐛 Débogage

Pour activer le mode debug :
1. Ouvrez la configuration (⚙️)
2. Cochez "Activer le mode débogage"
3. Redémarrez l'application
4. Consultez les logs dans `Logs/debug.log`

## 📝 Notes de Version

### Version 0.1 (Octobre 2025)
- ✅ Gestion complète des personnages (CRUD)
- ✅ Système de Realm Ranks avec web scraping
- ✅ Interface multilingue (FR/EN/DE)
- ✅ Configuration des colonnes visibles
- ✅ Mode debug avec console intégrée
- ✅ Thèmes clair/sombre
- ✅ Actions en masse

## 🔮 Fonctionnalités Futures

- 🎨 Icônes personnalisées pour chaque action
- 📊 Statistiques et graphiques de progression
- 🔄 Import/Export de personnages
- 🌐 Synchronisation cloud
- 🎯 Gestion des builds et équipements
- 📱 Version mobile

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Ajouter des traductions

## 📄 Licence

Ce projet est un outil personnel de gestion de personnages DAOC.

---

**Auteur** : Christophe Pelichet  
**Repository** : DAOC---Gestion-des-personnages  
**Branch** : Main_Windows
