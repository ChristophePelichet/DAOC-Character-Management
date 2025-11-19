# 🚀 Améliorations Futures - DAOC Character Management

Liste des idées d'améliorations et fonctionnalités à développer ultérieurement.

---

## 📋 Vue d'Ensemble

### Système de Thèmes
- [ ] [Éditeur de Thème Intégré](#1-éditeur-de-thème-intégré)
- [ ] [Génération Automatique de Variantes](#2-génération-automatique-de-variantes)
- [ ] [Import/Export de Thèmes](#3-importexport-de-thèmes)

### Système de Gestion des Items Ignorés
- [ ] [Interface de Gestion des Items Ignorés](#4-interface-de-gestion-des-items-ignorés)
- [ ] [Bouton Unignore pour Réactiver un Item](#5-bouton-unignore-pour-réactiver-un-item)
- [ ] [Export/Import de la Liste d'Items Ignorés](#6-exportimport-de-la-liste-ditems-ignorés)

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

### Système de Gestion des Items Ignorés

#### 4. Interface de Gestion des Items Ignorés
**Objectif** : Permettre la visualisation et la gestion complète des items marqués comme ignorés

**Fonctionnalités** :
- Fenêtre dédiée listant tous les items avec `ignore_item: true`
- Table avec colonnes : Nom, Royaume, Raison initiale, Date d'ignorage
- Tri et filtrage par royaume/nom
- Recherche rapide dans la liste
- Compteur total d'items ignorés
- Accès via menu "Tools" ou bouton dans Mass Import

**Bénéfices** :
- Transparence sur les items ignorés
- Évite les oublis (items ignorés par erreur)
- Facilite l'audit de la base de données

#### 5. Bouton Unignore pour Réactiver un Item
**Objectif** : Permettre de retirer le flag `ignore_item` d'un ou plusieurs items

**Fonctionnalités** :
- Bouton "Unignore" dans l'interface de gestion (point 4)
- Sélection multiple d'items à réactiver
- Confirmation avant suppression du flag
- Log de l'action dans les logs de debug
- Mise à jour automatique de la DB

**Workflow** :
1. User ouvre l'interface de gestion des items ignorés
2. Sélectionne un ou plusieurs items (ex: item de quête devenu utile)
3. Clique "Unignore" → Confirmation
4. Flag `ignore_item` retiré de la DB
5. Item réapparaîtra dans les futurs imports

**Bénéfices** :
- Flexibilité pour corriger des erreurs
- Adaptation aux changements de contenu du jeu
- Pas besoin d'éditer manuellement le JSON

#### 6. Export/Import de la Liste d'Items Ignorés
**Objectif** : Partager ou sauvegarder la liste d'items ignorés

**Fonctionnalités Export** :
- Bouton "Export Ignored List" dans l'interface de gestion
- Format JSON lisible avec métadonnées :
  ```json
  {
    "version": "1.0",
    "exported_date": "2025-11-19",
    "total_items": 25,
    "items": [
      {
        "name": "Quest Item X",
        "realm": "Albion",
        "id": "12345",
        "reason": "Quest item - not importable"
      }
    ]
  }
  ```
- Export vers fichier `.ignore-list.json`
- Option pour filtrer par royaume avant export

**Fonctionnalités Import** :
- Bouton "Import Ignored List"
- Sélection d'un fichier `.ignore-list.json`
- Aperçu des items avant import
- Options :
  - Merge (ajouter aux items ignorés existants)
  - Replace (remplacer la liste actuelle)
- Validation du format avant import
- Rapport d'import : X items ajoutés, Y déjà présents

**Cas d'Usage** :
- **Partage entre joueurs** : "Voici ma liste d'items de quête à ignorer"
- **Backup** : Sauvegarder avant réinstallation
- **Template** : Créer une liste commune pour une guilde
- **Migration** : Transférer entre serveurs/saisons

**Bénéfices** :
- Gain de temps pour nouveaux utilisateurs
- Standardisation des configurations
- Sécurité (backup avant modifications)

---

## 💡 Idées Complémentaires

### Items Ignorés - Fonctionnalités Avancées
- [ ] **Raison d'ignorage personnalisée** : Champ texte libre pour documenter pourquoi un item est ignoré
- [ ] **Catégories d'ignorage** : Tags (Quest, Duplicate, Obsolete, Low Priority)
- [ ] **Ignorage temporaire** : Date d'expiration du flag (utile pour events limités)
- [ ] **Statistiques** : Graphique des raisons d'ignorage, top items ignorés par catégorie
- [ ] **Suggestions automatiques** : IA détectant les patterns (items de quête récurrents)
- [ ] **Historique d'ignorage** : Journal avec date/heure/user de chaque modification

---

*(Cette section sera complétée au fur et à mesure du développement)*



---
## 💡 Idées en Vrac

*(Brainstorming d'idées à affiner plus tard)*

---

**Note** : Ce fichier sert de backlog informel. Les éléments prioritaires seront transformés en issues/branches de développement au moment opportun.
