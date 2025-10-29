# DAOC - Gestionnaire de Personnages

Application de gestion de personnages pour Dark Age of Camelot (DAOC), développée en Python avec PySide6.

**🌍 Disponible en :** **Français** | [English](README_EN.md) | [Deutsch](README_DE.md)

## 📦 Téléchargement

**Version actuelle : v0.105**

[![Télécharger l'exécutable](https://img.shields.io/badge/T%C3%A9l%C3%A9charger-EXE-blue?style=for-the-badge&logo=windows)](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

➡️ [Télécharger DAOC-Character-Manager.exe](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

*Aucune installation requise - exécutable portable Windows*

## 🎮 Fonctionnalités

### Gestion des Personnages
- ✅ **Créer** de nouveaux personnages avec race et classe
- ✅ **Sélection dynamique** des classes selon la race
- ✅ **Validation automatique** des combinaisons race/classe
- ✅ **Renommer** des personnages existants
- ✅ **Dupliquer** des personnages
- ✅ **Supprimer** des personnages (individuellement ou en masse)
- ✅ **Afficher** les détails complets de chaque personnage

### Races & Classes
- 🎭 **44 classes** disponibles réparties sur 3 royaumes
- 👤 **18 races** jouables (6 par royaume)
- 📚 **188 spécialisations** traduites en FR/EN/DE
- ✅ **Filtrage intelligent** : seules les classes compatibles avec la race sélectionnée sont affichées
- 🌍 **Traductions complètes** : races, classes et spécialisations en 3 langues

### Organisation
- 📁 Organisation par **Royaume** (Albion, Hibernia, Midgard)
- 🏷️ Filtrage par **Saison** (S1, S2, S3, etc.)
- 🖥️ Gestion multi-**Serveur** (Eden, Blackthorn)
- 📊 Tableau avec tri par colonnes

### Realm Ranks (Rangs de Royaume)
- 🏆 **Affichage** du rang et du titre de royaume
- 📈 **Ajustement par menus déroulants** du rang (Rank 1-14, Levels 0-9/10)
- 💾 **Sauvegarde automatique** des changements de rang/niveau
- 🎨 **Titres colorés** selon le royaume (rouge pour Albion, vert pour Hibernia, bleu pour Midgard)
- 📊 **Calcul automatique** basé sur les Realm Points

### Armure & Résistances
- 🛡️ **Système complet de résistances d'armure** avec support multilingue
- 📊 **47 classes** avec leurs résistances par type d'armure
- ⚔️ **9 types de résistances** : Thrust, Crush, Slash, Cold, Energy, Heat, Matter, Spirit, Body
- 🌍 **Données traduites** en EN/FR/DE pour toutes les classes et résistances
- 🏰 **Organisation par royaume** : Albion (16 classes), Hibernia (16 classes), Midgard (15 classes)
- 🔄 **Données scrapées** automatiquement depuis le site officiel DAOC

### Gestion des Armures
- 📁 **Upload de fichiers d'armure** de tous formats (PNG, JPG, PDF, TXT, etc.)
- 🗂️ **Organisation automatique** par ID de personnage dans des sous-dossiers
- 📋 **Liste des armures** avec métadonnées (nom, taille, date de modification)
- 🔍 **Ouverture rapide** des fichiers avec l'application par défaut
- 🗑️ **Suppression** de fichiers avec confirmation
- ⚙️ **Configuration** du chemin du dossier d'armures
- 🔄 **Gestion des doublons** automatique (suffixes _1, _2, etc.)

### Configuration Avancée
- 🌍 **Multi-langue** : Français, English, Deutsch
- 🔧 **Personnalisation** des chemins (personnages, logs, config, armures)
- 📋 **Colonnes configurables** : Masquer/afficher les colonnes souhaitées
- 🐛 **Mode Debug** avec console intégrée
- ℹ️ **Disclaimer configurable** : Message d'avertissement au démarrage (désactivable)

## 📋 Colonnes Configurables

Vous pouvez personnaliser l'affichage des colonnes via le menu **Affichage > Colonnes**.

Colonnes disponibles :
- **Sélection** : Case à cocher pour les actions en masse
- **Royaume** : Icône du royaume
- **Saison** : Saison du personnage
- **Serveur** : Serveur du personnage (cachée par défaut)
- **Nom** : Nom du personnage
- **Niveau** : Niveau du personnage
- **Rang** : Rang de royaume (ex: 5L7)
- **Titre** : Titre du rang (ex: Challenger)
- **Guilde** : Nom de la guilde
- **Page** : Page du personnage (1-5)
- **Classe** : Classe du personnage (affichée par défaut)
- **Race** : Race du personnage (cachée par défaut)

Voir [Documentation/COLUMN_CONFIGURATION_FR.md](Documentation/CONFIGURATION_COLONNES_FR.md) (FR) ou [Documentation/COLUMN_CONFIGURATION_EN.md](Documentation/COLUMN_CONFIGURATION_EN.md) (EN) pour plus de détails.

## � Installation

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
- [Menu Interface](Documentation/INTERFACE_MENU_FR.md)

### English 🇬🇧
- [Column Configuration](Documentation/COLUMN_CONFIGURATION_EN.md)
- [Realm Ranks System](Documentation/REALM_RANKS_EN.md)
- [Data Manager](Documentation/DATA_MANAGER_EN.md)
- [Data Folder](Documentation/DATA_FOLDER_EN.md)
- [Menu Interface](Documentation/INTERFACE_MENU_EN.md)

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

La configuration est accessible via le menu **Fichier > Paramètres**.

### Options disponibles :
- 📁 **Répertoires** : Personnages, Configuration, Logs
- 🌍 **Langue** : Français, English, Deutsch
- 🎨 **Thème** : Clair / Sombre
- 🖥️ **Serveur par défaut** : Eden, Blackthorn
- 📅 **Saison par défaut** : S1, S2, S3, etc.
- 🐛 **Mode Debug** : Activer/désactiver les logs détaillés

## 🎯 Utilisation

### Créer un Personnage
1. Accédez au menu **Fichier > Nouveau Personnage**
2. Entrez le nom, choisissez le royaume, la saison et le serveur
3. Cliquez sur "OK"

### Renommer un Personnage
1. Double-cliquez sur un personnage pour ouvrir sa feuille
2. Modifiez le nom dans le champ "Nom"
3. Appuyez sur **Entrée** pour renommer
4. Confirmez le renommage dans la boîte de dialogue

### Ajuster le Rang de Royaume
1. Double-cliquez sur un personnage pour ouvrir sa feuille
2. Utilisez les sliders pour ajuster le rang (1-14) et le niveau (1-9/10)
3. Cliquez sur "Appliquer ce rang" pour sauvegarder

### Configurer les Colonnes Visibles
1. Accédez au menu **Affichage > Colonnes**
2. Cochez/décochez les colonnes à afficher (y compris la colonne Serveur)
3. Cliquez sur "OK" pour sauvegarder

### Gérer la Largeur des Colonnes
Pour choisir entre le mode automatique et manuel :
1. Ouvrez la configuration via **Fichier > Paramètres**
2. Dans "Paramètres généraux", cochez/décochez "Gestion manuelle de la taille des colonnes"
3. Mode automatique (par défaut) : Les colonnes s'ajustent automatiquement au contenu
4. Mode manuel : Vous pouvez redimensionner librement chaque colonne en glissant les séparateurs
5. Cliquez sur "Enregistrer" et redémarrez l'application

### Actions en Masse
1. Cochez les personnages dans la colonne "Sélection"
2. Utilisez le menu déroulant "Actions en masse"
3. Sélectionnez "Supprimer la sélection" et cliquez sur "Exécuter"

## �️ Outils de Développement

### Générateur de Personnages de Test
Pour tester l'application avec des données variées :
```bash
python Tools/generate_test_characters.py
```
- Génère 20 personnages avec attributs aléatoires
- Distribution réaliste des Realm Points
- Validation automatique des combinaisons classe/race

### Éditeur de Données (Data Editor)
Outil visuel pour éditer les fichiers JSON de données :
```bash
python Tools/data_editor.py
```
- **Onglet Classes & Races** : Éditer les classes, races et spécialisations
- **Onglet Realm Ranks** : Gérer les rangs de royaume
- **Onglet Résistances d'Armure** : Éditer les résistances avec support multilingue (EN/FR/DE)
- Voir [Tools/DATA_EDITOR_README.md](Tools/DATA_EDITOR_README.md) pour plus de détails

### Scripts de Scraping
- `Scripts/scrape_realm_ranks.py` : Extraire les rangs de royaume
- `Scripts/scrape_armor_resists.py` : Extraire les résistances d'armure
- `Scripts/add_armor_translations.py` : Ajouter les traductions FR/DE automatiquement

## �🐛 Débogage

Pour activer le mode debug :
1. Ouvrez la configuration via **Fichier > Paramètres**
2. Cochez "Activer le mode débogage"
3. Redémarrez l'application
4. Consultez les logs dans `Logs/debug.log`

## 📝 Notes de Version

Consultez le [journal des modifications](CHANGELOG_FR.md) pour l'historique complet.  
**🌍 Disponible en :** [Français](CHANGELOG_FR.md) | [English](CHANGELOG_EN.md) | [Deutsch](CHANGELOG_DE.md)

### Version 0.104 (29 Octobre 2025)
- ✅ **Système de Résistances d'Armure** : Nouvelle fonctionnalité complète
  - 47 classes avec leurs résistances par type d'armure
  - 9 types de résistances : Thrust, Crush, Slash, Cold, Energy, Heat, Matter, Spirit, Body
  - Support multilingue complet (EN/FR/DE)
  - Organisation par royaume (Albion, Hibernia, Midgard)
  - Scraping automatique depuis darkageofcamelot.com
- ✅ **Outil de génération de test** : Script `generate_test_characters.py`
  - Génère 20 personnages avec attributs aléatoires pour tester l'application
- ✅ **Interface Rang de Royaume améliorée** : Remplacement des curseurs par des menus déroulants
- ✅ **Sauvegarde automatique** : Plus besoin de cliquer sur "Appliquer ce rang"
- ✅ **Organisation visuelle** : Titre du rang affiché en haut avec couleur du royaume
- ✅ **Section Armure** : Nouvelle section à côté de "Informations générales"
- ✅ **Corrections** : Résolution d'erreurs LanguageManager et AttributeError

### Version 0.103 (28 Octobre 2025)
- ✅ **Sélection de race** : Ajout d'un champ race dans la création de personnage
- ✅ **Sélection de classe** : Ajout d'un champ classe dans la création de personnage
- ✅ **Filtrage dynamique** : Les classes disponibles sont filtrées selon la race sélectionnée (et inversement)
- ✅ **Validation race/classe** : Vérification automatique de la compatibilité race/classe
- ✅ **Traductions des spécialisations** : Toutes les spécialisations traduites en FR/EN/DE
- ✅ **Système de données complet** : 44 classes, 18 races et 188 spécialisations
- ✅ **Ordre optimisé** : Classe sélectionnée AVANT la race pour un workflow plus logique
- ✅ **Support Eden** : Données ajustées pour le serveur Eden (sans Mauler)
- ✅ **Gestion largeur des colonnes** : Mode automatique ou manuel pour le redimensionnement des colonnes

### Version 0.102 (27 Octobre 2025)
- ✅ **Colonne Serveur** : Restauration de la colonne serveur (Eden/Blackthorn)
- ✅ **Configuration serveur** : Serveur par défaut configuré sur "Eden"
- ✅ **Fiche personnage** : Ajout d'un dropdown pour sélectionner le serveur
- ✅ **Visibilité** : Colonne serveur cachée par défaut (affichable via Affichage > Colonnes)
- ✅ **Réorganisation colonnes** : Nouvel ordre : Sélection, Royaume, Nom, Niveau, Rang, Titre, Guilde, Page, Serveur
- ✅ **Support multi-serveur** : Possibilité de gérer des personnages sur Eden et Blackthorn
- ✅ **Menu Colonnes** : Correction de la liste des colonnes (ajout serveur, suppression season)
- ✅ **Renommage rapide** : Appuyez sur Entrée dans le champ "Nom" pour renommer directement
- ✅ **Interface épurée** : Suppression du bouton "Renommer" et des popups inutiles
- ✅ **Correction bug** : Résolution d'une erreur critique dans l'affichage des titres colorés

### Version 0.101 (27 Octobre 2025)
- ✅ **Interface Windows** : Remplacement de la toolbar par une barre de menu traditionnelle
- ✅ **Menu Fichier** : Nouveau Personnage, Paramètres
- ✅ **Menu Affichage** : Configuration des colonnes
- ✅ **Menu Aide** : À propos avec informations complètes
- ✅ **Traductions** : Support complet des menus dans les 3 langues
- ✅ **Documentation** : Mise à jour complète avec guides d'interface menu
- ✅ **Créateur** : Mise à jour vers "Ewoline"

### Version 0.1 (Octobre 2025)
- ✅ Gestion complète des personnages (CRUD)
- ✅ Système de Realm Ranks avec web scraping
- ✅ Interface multilingue (FR/EN/DE)
- ✅ Configuration des colonnes visibles
- ✅ Mode debug avec console intégrée
- ✅ Actions en masse


## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Ajouter des traductions

## 📄 Licence

Ce projet est un outil personnel de gestion de personnages DAOC.

---

**Créé par :** Ewoline  
**Version :** 0.102  
**Dernière mise à jour :** 27 octobre 2025
