# DAOC - Gestionnaire de Personnages v0.107

Application de gestion de personnages pour Dark Age of Camelot (DAOC), développée en Python avec PySide6.

**🌍 Disponible en :** **Français** | [English](Documentation/README_EN.md) | [Deutsch](Documentation/README_DE.md)

## 📦 Téléchargement

**Version actuelle : v0.107** 🎉

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