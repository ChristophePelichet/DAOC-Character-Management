# 🚀 Améliorations Futures - DAOC Character Management

Liste des idées d'améliorations et fonctionnalités à développer ultérieurement.

---

## 📋 Vue d'Ensemble

### Système de Thèmes
- [ ] [Éditeur de Thème Intégré](#1-éditeur-de-thème-intégré)
- [ ] [Génération Automatique de Variantes](#2-génération-automatique-de-variantes)
- [ ] [Import/Export de Thèmes](#3-importexport-de-thèmes)

---

## 🎨 Système de Thèmes

### 1. Éditeur de Thème Intégré
- Interface graphique pour créer/modifier des thèmes directement dans l'application
- Sélecteurs de couleurs pour chaque élément (fenêtre, texte, boutons, etc.)
- Prévisualisation en temps réel des modifications
- Sauvegarde automatique dans un nouveau fichier JSON

### 2. Génération Automatique de Variantes
- À partir d'une couleur de base, générer automatiquement :
  - Couleurs complémentaires (texte, arrière-plan, surbrillance)
  - Variations désactivées (grisées)
  - Palette harmonieuse complète
- Algorithmes de contraste pour assurer la lisibilité
- Génération de variantes claires/sombres d'un même thème

### 3. Import/Export de Thèmes
- Partage de thèmes entre utilisateurs
- Format d'export standardisé (JSON avec métadonnées)
- Bibliothèque de thèmes communautaires
- Validation automatique des thèmes importés

---

## 📋 Fonctionnalités à Ajouter

*(Cette section sera complétée au fur et à mesure du développement)*

---

## 🐛 Corrections à Planifier

### 1. Fenêtre de Progression - Thème Purple
- [ ] Corriger l'affichage du texte en bas de la fenêtre de progression avec le thème Purple
- [ ] Problème : Carré blanc masquant le texte pendant la progression
- [ ] Le texte vert final reste visible dans un carré blanc (manque de contraste/transparence)
- [ ] Impact : Fichier `UI/dialogs.py` ou configuration thème `Themes/purple.json`
- [ ] Solution probable : Ajuster les couleurs de fond du QLabel de statut ou stylesheet du thème

---

## 🔧 Optimisations Techniques

### 1. Profil Chrome Dédié pour Selenium
- [ ] Créer un profil Chrome dédié pour Selenium dans `eden_scraper.py`
- [ ] Configurer ChromeDriver avec un `user-data-dir` séparé et isolé
- [ ] Garantir une isolation totale entre navigation personnelle et requêtes du scraper
- [ ] Éviter tout conflit de cookies à l'avenir
- [ ] Impact : Fichier `Functions/eden_scraper.py` (configuration ChromeDriver)

---

## 💡 Idées en Vrac

*(Brainstorming d'idées à affiner plus tard)*

---

**Note** : Ce fichier sert de backlog informel. Les éléments prioritaires seront transformés en issues/branches de développement au moment opportun.
