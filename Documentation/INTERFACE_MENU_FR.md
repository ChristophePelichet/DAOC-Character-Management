# Interface Menu Windows

## 📋 Vue d'ensemble

L'application DAOC Character Manager utilise une interface Windows traditionnelle avec une barre de menu en lieu et place d'une barre d'outils. Cette approche offre une expérience utilisateur plus familière et professionnelle.

## 🎯 Structure des Menus

### Menu Fichier

Le menu **Fichier** contient les actions principales de l'application :

- **Nouveau Personnage** : Crée un nouveau personnage avec nom, royaume, saison et serveur
- **Paramètres** : Ouvre la fenêtre de configuration de l'application

### Menu Affichage

Le menu **Affichage** permet de personnaliser l'interface :

- **Colonnes** : Configure les colonnes visibles dans la liste des personnages

### Menu Aide

Le menu **Aide** fournit des informations sur l'application :

- **À propos** : Affiche les informations de l'application, version et créateur

## 🚀 Utilisation

### Créer un Nouveau Personnage

1. Cliquez sur **Fichier > Nouveau Personnage**
2. Remplissez le formulaire :
   - **Nom** : Nom du personnage
   - **Royaume** : Albion, Hibernia ou Midgard
   - **Saison** : S1, S2, S3, etc.
   - **Serveur** : Eden, Blackthorn, etc.
3. Cliquez sur "OK" pour créer le personnage

### Configurer l'Application

1. Cliquez sur **Fichier > Paramètres**
2. Ajustez les réglages selon vos préférences :
   - Répertoires de stockage
   - Langue de l'interface
   - Thème (clair/sombre)
   - Serveur et saison par défaut
   - Mode debug
3. Cliquez sur "Enregistrer" pour sauvegarder

### Personnaliser l'Affichage

1. Cliquez sur **Affichage > Colonnes**
2. Cochez/décochez les colonnes à afficher :
   - Sélection (pour actions en masse)
   - Royaume (icône)
   - Saison, Serveur, Nom, Niveau
   - Rang et Titre de royaume
3. Cliquez sur "OK" pour appliquer les changements

## 🌍 Support Multilingue

L'interface menu est entièrement traduite en :
- 🇫🇷 **Français** : Fichier, Affichage, Aide
- 🇬🇧 **English** : File, View, Help  
- 🇩🇪 **Deutsch** : Datei, Ansicht, Hilfe

Le changement de langue se fait via **Fichier > Paramètres > Langue**.

## ✨ Avantages de l'Interface Menu

### Par rapport à une barre d'outils :

- ✅ **Plus professionnel** : Interface standard Windows
- ✅ **Économie d'espace** : Plus de place pour les données
- ✅ **Organisation logique** : Actions groupées par catégorie
- ✅ **Accessibilité** : Navigation au clavier avec Alt+touche
- ✅ **Évolutivité** : Facilite l'ajout de nouvelles fonctionnalités

### Raccourcis clavier (futurs) :
- `Ctrl+N` : Nouveau personnage
- `Ctrl+,` : Paramètres
- `F1` : À propos

## 🔧 Configuration Technique

L'interface menu utilise les composants PySide6 suivants :
- `QMenuBar` : Barre de menu principale
- `QMenu` : Menus individuels (Fichier, Affichage, Aide)
- `QAction` : Actions dans les menus
- Système de traduction via `language_manager.py`

La recréation des menus lors du changement de langue assure une traduction instantanée de l'interface.

---

**Version** : 0.101  
**Date** : 27 Octobre 2025  
**Auteur** : DAOC Character Manager Team