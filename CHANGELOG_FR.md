# JOURNAL DES MODIFICATIONS

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

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