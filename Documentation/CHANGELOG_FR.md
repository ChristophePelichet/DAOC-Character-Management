# JOURNAL DES MODIFICATIONS

> 📁 **Ce fichier a été déplacé** : Anciennement à la racine, maintenant dans `Documentation/` (v0.104)

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

## [0.104] - 2025-10-29

### Ajouté
- **Popup de confirmation de migration** : Affichage trilingue (FR/EN/DE) avant toute migration
  - Explication détaillée de la modification de structure
  - Comparaison visuelle : Ancienne structure → Nouvelle structure
  - Information sur la sauvegarde automatique avec chemin d'accès
  - Bouton "OK" : Lance la sauvegarde ZIP puis la migration
  - Bouton "Annuler" : Ferme l'application sans modification
  - Message d'annulation personnalisé si l'utilisateur annule
- **Sauvegarde automatique ZIP avant migration** : Protection optimisée des données
  - Création d'une archive ZIP compressée du dossier `Characters`
  - Nom avec horodatage : `Characters_backup_YYYYMMDD_HHMMSS.zip`
  - Emplacement organisé : `Backup/Characters/`
  - Compression ZIP_DEFLATED pour économiser 70-90% d'espace disque
  - Vérification de succès avant de lancer la migration
  - Message de confirmation avec emplacement de la sauvegarde
- **Nouvelle structure de dossiers** : Migration vers une organisation hiérarchique par saison
  - Ancienne structure : `Characters/Royaume/Personnage.json`
  - Nouvelle structure : `Characters/Saison/Royaume/Personnage.json`
  - Prépare le terrain pour de futures saisons
  - Migration automatique au démarrage (avec confirmation)
  - Fichier marqueur `.migration_done` pour éviter les migrations multiples
- **Menu Aide > Migrer la structure des dossiers** : Option manuelle de migration
  - Permet de relancer la migration manuellement si nécessaire
  - Demande confirmation avant de procéder
  - Crée automatiquement une sauvegarde ZIP
  - Affiche un rapport détaillé de la migration (nombre de personnages, répartition par saison)
  - Actualise automatiquement la liste des personnages après migration
- **Module migration_manager.py** : Gestionnaire de migration complet
  - `get_backup_path()` : Génère le chemin de sauvegarde dans `Backup/Characters/`
  - `backup_characters()` : Crée une archive ZIP compressée
  - `check_migration_needed()` : Détecte si la migration est nécessaire
  - `migrate_character_structure()` : Effectue la migration avec rapport détaillé
  - `is_migration_done()` : Vérifie si la migration a déjà été effectuée
  - `run_migration_with_backup()` : Orchestre sauvegarde puis migration
  - `run_migration_if_needed()` : Lance la migration automatique au démarrage
  - Gestion complète des erreurs avec logs détaillés
  - Préservation des métadonnées des fichiers (dates, attributs)
  - Nettoyage automatique des anciens dossiers vides
- **Colonnes Classe et Race** : Nouvelles colonnes dans la vue principale
  - Colonne "Classe" affichée par défaut
  - Colonne "Race" masquée par défaut
  - Cases à cocher dans le menu Affichage > Colonnes pour activer/désactiver les colonnes
  - Support multilingue complet (FR/EN/DE)
  - Données extraites automatiquement depuis les fichiers JSON de personnages
- **Scripts de test** : Outils pour tester la migration
  - `Scripts/simulate_old_structure.py` : Crée l'ancienne structure pour tests
  - `Scripts/test_backup_structure.py` : Vérifie la création des sauvegardes ZIP
- **Réorganisation de la documentation** : Amélioration de la structure des fichiers
  - CHANGELOGs déplacés dans `Documentation/`
  - Nouveau `CHANGELOG.md` principal à la racine renvoyant vers les versions linguistiques
  - READMEs linguistiques (EN/DE) déplacés dans `Documentation/`
  - README.md principal à la racine avec liens vers les versions linguistiques
  - Meilleure organisation des fichiers de documentation
  - Tous les liens internes mis à jour

### Modifié
- **Toutes les fonctions de gestion des personnages** : Adaptation à la nouvelle structure Season/Realm
  - `save_character()` : Sauvegarde dans `Season/Realm/`
  - `get_all_characters()` : Parcourt la structure Season/Realm avec `os.walk()`
  - `rename_character()` : Recherche et renomme dans la nouvelle structure
  - `delete_character()` : Supprime dans la nouvelle structure
  - `move_character_to_realm()` : Déplace entre royaumes au sein de la même saison
  - Valeur par défaut "S1" pour les personnages sans saison spécifiée
- **Migration automatique** : Nécessite maintenant confirmation utilisateur
  - Ne se lance plus automatiquement sans demander
  - Affiche le popup de confirmation au démarrage
  - Ferme l'application si l'utilisateur annule
- **Fonction `run_automatic_migration()` dans main.py** : Refactorisation complète
  - Affiche le popup de confirmation avec QMessageBox
  - Utilise try/finally pour garantir la fermeture du popup de progression
  - Appelle `progress.deleteLater()` pour nettoyer la mémoire Qt
  - Gère les cas d'annulation avec message trilingue
- **Système de sauvegarde** : Migration de copie de dossier vers archive ZIP
  - Ancienne méthode : `shutil.copytree()` créait une copie lourde
  - Nouvelle méthode : `zipfile.ZipFile()` avec compression ZIP_DEFLATED
  - Économie d'espace disque de 70-90% pour les fichiers JSON
  - Organisation dans un dossier dédié `Backup/`
- **Interface Rang de Royaume** : Remplacement des curseurs par des menus déroulants
  - Menu déroulant pour le rang (1-14)
  - Menu déroulant pour le niveau (L0-L10 pour rang 1, L0-L9 pour les autres)
  - Le titre du rang s'affiche maintenant en haut de la section avec la couleur du royaume
- **Sauvegarde automatique des rangs** : Suppression du bouton "Appliquer ce rang"
  - Les modifications de rang/niveau sont maintenant appliquées automatiquement
  - Plus besoin de confirmer les changements
- **.gitignore** : Ajout du dossier `Backup/` aux exclusions Git

### Corrigé
- **Popup "Migration en cours" restant ouvert** : Correction critique
  - Ajout de `try/finally` pour garantir la fermeture du popup
  - Appel explicite de `progress.close()` et `progress.deleteLater()`
  - Le popup se ferme maintenant correctement après la migration
- **Erreur LanguageManager** : Correction des appels `lang.get()` avec valeurs par défaut incorrectes
- **Erreur AttributeError** : Correction des noms de méthodes pour les callbacks de rang/niveau

### Technique
- **Architecture améliorée** : Séparation des saisons au niveau du système de fichiers
- **Compatibilité ascendante** : Migration automatique préserve tous les personnages existants
- **Logging détaillé** : Toutes les opérations de migration sont enregistrées dans les logs
- **Gestion d'erreurs robuste** : La migration gère les cas d'erreur sans perte de données
- **Performance optimisée** : Utilisation de `zipfile` avec compression pour les sauvegardes
- **Nettoyage mémoire Qt** : Utilisation correcte de `deleteLater()` pour les widgets temporaires
- Ajout de 9 nouvelles clés de traduction dans FR/EN/DE pour le système de migration
- Documentation complète créée : `BACKUP_ZIP_UPDATE.md`

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