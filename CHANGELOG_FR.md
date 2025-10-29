# JOURNAL DES MODIFICATIONS

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

## [Non publié]

## [0.105] - 2024-12-XX

### Ajouté
- **Menu Action** : Nouveau menu entre "Fichier" et "Affichage"
  - Action "📊 Résistances" : Ouvre le tableau des résistances d'armure (lance data_editor.py)
  - Support multilingue complet (FR/EN/DE)
  - Gestion des erreurs avec messages utilisateur
  - Logging de toutes les actions
- **Menu contextuel amélioré** : 
  - Ajout de "📁 Gestion des armures" au clic droit sur un personnage
  - Placé entre "Dupliquer" et "Supprimer"
- **Système de Gestion des Armures** : Nouvelle fonctionnalité complète
  - Module `Functions/armor_manager.py` avec la classe `ArmorManager`
  - Upload de fichiers d'armure (tous formats : PNG, JPG, PDF, TXT, etc.)
  - Gestion automatique des doublons (suffixes _1, _2, etc.)
  - Organisation par ID de personnage dans des sous-dossiers
  - Liste des armures avec métadonnées (nom, taille, date de modification)
  - Ouverture des fichiers avec l'application par défaut du système
  - Suppression de fichiers avec confirmation
  - Dialog `ArmorManagementDialog` avec interface utilisateur complète
  - Bouton "📁 Gérer les armures" dans la fiche de personnage (section Armure)
  - Configuration du chemin du dossier d'armures dans Paramètres
  - Documentation complète : `Documentation/ARMOR_MANAGEMENT_FR.md`
  - Script de test : `Scripts/test_armor_manager.py`
- **Path Manager** : Nouvelles fonctions pour la gestion des chemins
  - `get_armor_dir()` : Retourne le chemin du dossier d'armures
  - `ensure_armor_dir()` : Crée le dossier d'armures automatiquement

### Modifié
- **Configuration** : Ajout du champ "Dossier des armures" dans le dialogue de configuration
  - Nouveau champ avec bouton de navigation
  - Sauvegarde dans `config.json` sous la clé `armor_folder`
  - Valeur par défaut : `<app_dir>/Armures`
- **Architecture** : Approche "drive-in" avec chemins configurables
  - Tous les chemins stockés dans la configuration
  - Création automatique des répertoires nécessaires
  - Aucun chemin codé en dur

### Technique
- Support de tous les formats de fichiers
- Préservation des métadonnées lors de la copie (shutil.copy2)
- Logging détaillé de toutes les opérations
- Gestion complète des erreurs avec messages utilisateur
- Compatible Windows (testé avec os.startfile)

## [0.104] - 2025-10-29

### Ajouté
- **Colonnes Classe et Race** : Nouvelles colonnes dans la vue principale
  - Colonne "Classe" affichée par défaut
  - Colonne "Race" masquée par défaut
  - Cases à cocher dans le menu Affichage > Colonnes pour activer/désactiver les colonnes
  - Support multilingue complet (FR/EN/DE)
  - Données extraites automatiquement depuis les fichiers JSON de personnages

### Modifié
- **Menu Action supprimé** : Le menu "Action" et toutes ses actions ont été retirés temporairement
  - Action "Résistances" retirée du menu (data_editor.py conservé)
  - Interface simplifiée
- **Menu contextuel** : Icône retirée de "Gestion des armures"
  - Avant : "📁 Gestion des armures"
  - Maintenant : "Gestion des armures"
  - Texte sans icône dans les 3 langues (FR/EN/DE)
- **Colonne Classe** : Correction du formatage du texte
  - Le texte n'est plus affiché en gras
  - Police normale pour une meilleure cohérence visuelle

### Technique
- Ajout de `font.setBold(False)` pour la colonne Classe
- Mise à jour des traductions `context_menu_armor_management` (retrait de 📁)

### Ajouté (version précédente)
- **Système de Résistances d'Armure** : Nouvelle fonctionnalité complète
  - Fichier `Data/armor_resists.json` avec les résistances de toutes les classes (47 classes)
  - Support multilingue complet (EN/FR/DE) pour tous les champs
  - 9 types de résistances : Thrust, Crush, Slash, Cold, Energy, Heat, Matter, Spirit, Body
  - 3 tableaux organisés par royaume (Albion: 16 classes, Hibernia: 16 classes, Midgard: 15 classes)
  - Script de scraping `scrape_armor_resists.py` pour extraire les données depuis darkageofcamelot.com
  - Script `add_armor_translations.py` pour ajouter les traductions FR/DE automatiquement
- **Outil de génération de test** : Script `generate_test_characters.py`
  - Génère 20 personnages avec attributs aléatoires
  - Distribution réaliste des Realm Points
  - Validation automatique des combinaisons classe/race
  - Idéal pour tester l'application avec des données variées

### Ajouté (suite)
- **Disclaimer au démarrage** : Message d'information trilingue (FR/EN/DE)
  - Avertit que le logiciel est en version Alpha
  - Informe sur le stockage local des données
  - Option pour désactiver le message dans Paramètres > Divers
  - Remplace l'ancien système de disclaimer codé en dur

### Modifié
- **Interface Rang de Royaume** : Remplacement des curseurs par des menus déroulants
  - Menu déroulant pour le rang (1-14)
  - Menu déroulant pour le niveau (L0-L10 pour rang 1, L0-L9 pour les autres)
  - Le titre du rang s'affiche maintenant en haut de la section avec la couleur du royaume
- **Sauvegarde automatique** : Suppression du bouton "Appliquer ce rang"
  - Les modifications de rang/niveau sont maintenant appliquées automatiquement
  - Plus besoin de confirmer les changements
- **Paramètres** : Ajout du groupe "Divers"
  - Case à cocher pour désactiver le disclaimer au démarrage
  - Sauvegarde persistante dans config.json
- **Organisation visuelle** : Réorganisation de la section "Rang de Royaume"
  - Titre du rang avec couleur (rouge pour Albion, vert pour Hibernia, bleu pour Midgard) placé en haut
  - Contrôles de rang/niveau en dessous du titre
- **Section Armure** : Positionnée à côté de "Informations générales"
  - Bouton "Résistances" (désactivé temporairement, fonctionnalité à venir)
  - Préparation pour l'intégration du système de résistances

### Corrigé
- **Erreur LanguageManager** : Correction des appels `lang.get()` avec valeurs par défaut incorrectes
- **Erreur AttributeError** : Correction des noms de méthodes pour les callbacks de rang/niveau
  - `on_rank_dropdown_changed` → `on_rank_changed`
  - `on_level_dropdown_changed` → `on_level_changed`

### Traductions
- Ajout des clés `armor_group_title` et `resistances_button` en FR/EN/DE

## [0.103] - 2025-10-28

### Ajouté
- **Sélection de race** : Ajout d'un champ race dans la création de personnage
- **Sélection de classe** : Ajout d'un champ classe dans la création de personnage
- **Filtrage dynamique** : Les classes disponibles sont filtrées selon la race sélectionnée
- **Validation race/classe** : Vérification automatique de la compatibilité race/classe
- **Traductions des spécialisations** : Toutes les spécialisations sont maintenant traduites en FR/EN/DE
- **Système de données complet** : Ajout de `Data/classes_races.json` avec 44 classes, 18 races et 188 spécialisations
- **Documentation complète** : Ajout de guides d'utilisation et de documentation technique
- **Gestion de la largeur des colonnes** : Option pour basculer entre mode automatique et manuel
  - Mode automatique : Ajustement automatique au contenu avec colonne Nom extensible
  - Mode manuel : Redimensionnement libre de toutes les colonnes par l'utilisateur

### Modifié
- **Ordre classe/race inversé** : La classe est maintenant sélectionnée AVANT la race
- **Filtrage race par classe** : Les races disponibles sont filtrées selon la classe sélectionnée
- **Suppression de Mauler** : Classe Mauler supprimée (non implémentée sur serveur Eden)
- **Support Eden** : Données ajustées pour correspondre aux classes disponibles sur Eden
- **Structure des spécialisations** : Format multilingue `{"name": "EN", "name_fr": "FR", "name_de": "DE"}`
- **DataManager enrichi** : Ajout de 11 nouvelles fonctions pour gérer races/classes/spécialisations et de `get_available_races_for_class()` pour le filtrage inversé

### Amélioré
- **Expérience utilisateur** : Ordre plus logique (classe → race)
- **Cohérence** : Ordre identique dans création et édition de personnage

### Fichiers ajoutés
- `Data/classes_races.json` : Données complètes des races, classes et spécialisations
- `Data/classes_races_stats.json` : Statistiques détaillées
- `Documentation/CLASSES_RACES_USAGE.md` : Guide d'utilisation complet
- `Documentation/CLASSES_RACES_IMPLEMENTATION.md` : Documentation technique
- `validate_classes_races.py` : Script de validation des données
- `example_classes_usage.py` : Exemples d'utilisation pratique

### Statistiques
- **44 classes** réparties sur 3 royaumes (Albion: 15, Midgard: 14, Hibernia: 15)
- **18 races** au total (6 par royaume)
- **188 spécialisations** traduites en 3 langues

## [0.102] - 2025-10-27

### Modifié
- **Colonne Serveur** : Restauration de la colonne serveur (Eden/Blackthorn)
- **Configuration serveur** : Serveur par défaut configuré sur "Eden"
- **Fiche personnage** : Ajout d'un dropdown pour sélectionner le serveur
- **Visibilité** : Colonne serveur cachée par défaut (peut être affichée via Affichage > Colonnes)
- **Réorganisation colonnes** : Nouvel ordre : Sélection, Royaume, Nom, Niveau, Rang, Titre, Guilde, Page, Serveur
- **Menu Colonnes** : Correction de la liste des colonnes dans le menu (ajout serveur, suppression season)
- **Renommage simplifié** : Le bouton "Renommer" a été supprimé de la fiche personnage
- **Messages simplifiés** : Suppression du message "Cela mettra à jour le fichier JSON" et de la popup de succès

### Ajouté
- **Support multi-serveur** : Possibilité de gérer des personnages sur Eden et Blackthorn
- **Édition serveur** : Modification du serveur depuis la fiche personnage
- **Renommage rapide** : Appuyez sur Entrée dans le champ "Nom" pour renommer directement le personnage

### Amélioré
- **Interface utilisateur** : Interface plus épurée dans la fiche personnage
- **Ergonomie** : Renommage plus rapide avec la touche Entrée
- **Expérience utilisateur** : Processus de renommage plus fluide sans popups inutiles

### Corrigé
- **RealmTitleDelegate** : Correction d'une erreur critique lors du dessin des titres colorés

## [0.101] - 2025-10-27

### Modifié
- **Interface utilisateur** : Remplacement de la barre d'outils par une barre de menu Windows traditionnelle
- **Menu Fichier** : Ajout du menu avec "Nouveau Personnage" et "Paramètres"
- **Menu Affichage** : Ajout du menu avec "Colonnes"
- **Menu Aide** : Ajout du menu avec "À propos"
- **Boîte de dialogue À propos** : Amélioration avec informations complètes (nom, version, créateur)
- **Traductions** : Ajout des traductions pour les menus dans les 3 langues (FR/EN/DE)
- **Documentation** : Mise à jour de toute la documentation pour refléter la nouvelle interface
- **Créateur** : Mise à jour du nom du créateur vers "Ewoline"
- **Fiche personnage** : Ajout de la possibilité d'éditer le royaume, niveau (1-50), saison, page (1-5) et guilde
- **Changement de royaume** : Déplacement automatique du fichier vers le bon répertoire lors du changement
- **Couleurs dynamiques** : Mise à jour automatique des couleurs selon le nouveau royaume
- **Renommage** : Possibilité de renommer un personnage depuis le menu contextuel (clic droit) ou la fiche personnage
- **Gestion fichiers** : Renommage automatique du fichier JSON lors du renommage du personnage
- **Suppression colonne serveur** : Suppression définitive de la colonne serveur et toutes ses fonctionnalités
- **Simplification interface** : Serveur fixé automatiquement à "Eden" sans sélection possible
- **Réorganisation colonnes** : Réindexation de toutes les colonnes après suppression du serveur
- **Sauvegarde** : Ajout d'un bouton "Sauvegarder" dans la fiche personnage pour enregistrer les modifications
- **Configuration** : Application des valeurs par défaut pour les colonnes même sans configuration existante

### Supprimé
- **Barre d'outils** : Suppression de la barre d'outils avec icônes
- **Code obsolète** : Nettoyage du code lié aux icônes de barre d'outils non utilisées

### Technique
- Optimisation du chargement des icônes (conservation uniquement des icônes de royaume)
- Simplification du système d'actions
- Amélioration de la gestion de la retraduction lors du changement de langue

## [0.1] - 2025-10-XX

### Ajouté
- **Gestion complète des personnages** : Création, modification, suppression, duplication
- **Système de Rangs de Royaume** : Affichage des rangs et titres avec extraction web
- **Interface multilingue** : Support complet pour Français, English, Deutsch
- **Configuration des colonnes** : Personnalisation des colonnes visibles
- **Mode debug** : Console intégrée avec gestion des logs
- **Actions en masse** : Sélection multiple et suppression en lot
- **Organisation par royaume** : Albion, Hibernia, Midgard avec icônes
- **Gestion multi-serveur** : Support pour différents serveurs DAOC
- **Système de saisons** : Organisation par saisons (S1, S2, S3, etc.)
- **Thèmes** : Support thème clair/sombre
- **Persistance** : Sauvegarde automatique des configurations

### Fonctionnalités principales
- **Interface PySide6** : Interface graphique moderne et responsive
- **Gestionnaire de données** : Système complet de gestion des données de jeu
- **Extraction web** : Extraction automatique des données Rangs de Royaume depuis le site officiel
- **Configuration avancée** : Personnalisation complète des chemins et paramètres
- **Documentation complète** : Guides détaillés en français et anglais

---

## Types de changements

- `Ajouté` pour les nouvelles fonctionnalités
- `Modifié` pour les changements dans les fonctionnalités existantes
- `Déprécié` pour les fonctionnalités qui seront supprimées dans les versions futures
- `Supprimé` pour les fonctionnalités supprimées dans cette version
- `Corrigé` pour les corrections de bugs
- `Sécurité` pour les vulnérabilités corrigées

## Liens de versions

- [0.101] - Version actuelle avec interface menu Windows
- [0.1] - Version initiale avec barre d'outils

## Autres langues

- 🇫🇷 [Français](CHANGELOG_FR.md) (ce fichier)
- 🇬🇧 [English](CHANGELOG_EN.md)
- 🇩🇪 [Deutsch](CHANGELOG_DE.md)