# DAOC - Gestionnaire de Personnages v0.104

Application de gestion de personnages pour Dark Age of Camelot (DAOC), développée en Python avec PySide6.

**🌍 Disponible en :** **Français** | [English](Documentation/README_EN.md) | [Deutsch](Documentation/README_DE.md)

## 📦 Téléchargement

**Version actuelle : v0.105** 🎉

[![Télécharger l'exécutable](https://img.shields.io/badge/T%C3%A9l%C3%A9charger-EXE-blue?style=for-the-badge&logo=windows)](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

➡️ [Télécharger DAOC-Character-Manager.exe](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

*Aucune installation requise - exécutable portable Windows*

## 📝 Notes de Version

Consultez le [journal des modifications](CHANGELOG.md) pour l'historique complet.  


## 🎮 Fonctionnalités

### Gestion des Personnages
- ✅ **Créer** manuellement de nouveaux personnages avec race et classe
- ✅ **Importer** directement depuis l'Herald de Eden de nouveaux personnages avec race et classe
- ✅ **Sélection dynamique** des classes selon la race
- ✅ **Validation automatique** des combinaisons race/classe
- ✅ **Renommer** des personnages existants
- ✅ **Dupliquer** des personnages
- ✅ **Supprimer** des personnages (individuellement ou en masse)
- ✅ **Afficher** les détails complets de chaque personnage
- ✅ **Système** de sauvegarde avec séléction de la limitation de la taille

### Races & Classes
- 🎭 **44 classes** disponibles réparties sur 3 royaumes
- 👤 **18 races** jouables (6 par royaume)
- 📚 **188 spécialisations** traduites en FR/EN/DE
- ✅ **Filtrage intelligent** : seules les classes compatibles avec la race sélectionnée sont affichées
- 🌍 **Traductions complètes** : races, classes et spécialisations en 3 langues

### Realm Ranks (Rangs de Royaume)
- 🏆 **Affichage** du rang et du titre de royaume
- 📈 **Ajustement par menus déroulants** du rang (Rank 1-14, Levels 0-9/10)
- 💾 **Sauvegarde automatique** des changements de rang/niveau
- 🎨 **Titres colorés** selon le royaume (rouge pour Albion, vert pour Hibernia, bleu pour Midgard)
- 📊 **Calcul automatique** basé sur les Realm Points

### Armure & Résistances
- 📊 **47 classes** avec leurs résistances par type d'armure
- ⚔️ **9 types de résistances** : Thrust, Crush, Slash, Cold, Energy, Heat, Matter, Spirit, Body
- 🌍 **Données traduites** en EN/FR/DE pour toutes les classes et résistances
- 🏰 **Organisation par royaume** :
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

## ⚙️ Configuration

La configuration est accessible via le menu **Fichier > Paramètres**.

### Options disponibles :
- 📁 **Répertoires** : Personnages, Configuration, Logs
- 🌍 **Langue** : Français, English, Deutsch
- 🎨 **Thème** : Clair / Sombre
- 🖥️ **Serveur par défaut** : Eden, Blackthorn
- 📅 **Saison par défaut** : S1, S2, S3, etc.
- 🐛 **Mode Debug** : Activer/désactiver les logs détaillés

## 🔄 Migration de Structure

**Important** : À partir de la version 0.104, la structure des dossiers a changé pour mieux organiser les personnages par saison.

### Structure actuelle (v0.104+)
```
Characters/
└── Season/              # S1, S2, S3, etc.
    └── Realm/           # Albion, Hibernia, Midgard
        └── Character.json
```

### Migration automatique avec sauvegarde
- **Popup de confirmation** : Au premier démarrage, un dialogue explique la migration
  - Comparaison visuelle : Ancienne structure → Nouvelle structure
  - Information sur la sauvegarde automatique
  - Bouton "OK" : Lance la sauvegarde puis la migration
  - Bouton "Annuler" : Ferme l'application sans modifications
- **Sauvegarde automatique** : Avant toute migration, une sauvegarde complète est créée
  - Format : Archive ZIP compressée (`Characters_backup_AAAAMMJJ_HHMMSS.zip`)
  - Emplacement : `Backup/Characters/`
  - Protège vos données en cas de problème
- **Migration sécurisée** : Vos personnages existants sont préservés et déplacés vers la nouvelle structure
- Un fichier marqueur `.migration_done` est créé pour éviter les migrations multiples

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

## 🛠️ Outils de Développement

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

## 🐛 Débogage

Pour activer le mode debug :
1. Ouvrez la configuration via **Fichier > Paramètres**
2. Cochez "Activer le mode débogage"
3. Redémarrez l'application
4. Consultez les logs dans `Logs/debug.log`




## 📄 Licence

Ce projet est un outil personnel de gestion de personnages DAOC.

