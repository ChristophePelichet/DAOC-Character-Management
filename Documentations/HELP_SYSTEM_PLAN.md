# Plan du Système d'Aide - Bibliothèque d'Assistance

## 📋 Vue d'ensemble

Ce document planifie l'implémentation complète d'un système d'aide contextuel pour guider les utilisateurs dans toutes les fonctionnalités de l'application.

---

## 🎯 Objectifs

1. **Aide contextuelle** : Fenêtres d'aide dédiées pour chaque action majeure
2. **Tutoriels pas-à-pas** : Guides interactifs avec captures d'écran
3. **Documentation intégrée** : Accessible directement depuis l'application
4. **Support multilingue** : FR/EN/DE pour toutes les aides
5. **Recherche d'aide** : Système de recherche dans la documentation

---

## 📚 Liste des Aides à Créer

### 🎨 1. Gestion des Personnages

#### 1.1 Création de Personnage
- ✅ **Aide - Créer un nouveau personnage** (PRIORITÉ 1 - À implémenter en premier)
  - Tutoriel pas-à-pas pour la création manuelle
  - Explication de chaque champ (nom, royaume, saison, serveur, niveau, etc.)
  - Conseils sur les conventions de nommage
  - Captures d'écran annotées
  - Raccourcis clavier

#### 1.2 Édition de Personnage
- **Aide - Éditer un personnage**
  - Modifier les informations de base (nom, niveau, guilde, page)
  - Changer de royaume (avec déplacement automatique de fichier)
  - Modifier classe et race
  - Gestion des rangs de royaume

#### 1.3 Import/Export
- **Aide - Importer depuis Eden Herald**
  - Configuration des cookies Discord
  - Recherche de personnages
  - Sélection multiple et import en masse
  - Gestion des doublons
- **Aide - Exporter les données**
  - Export JSON simple
  - Backup complet
  - Migration vers autre machine

#### 1.4 Suppression
- **Aide - Supprimer des personnages**
  - Suppression simple
  - Suppression multiple
  - Récupération après suppression (backup)

#### 1.5 Duplication
- **Aide - Dupliquer un personnage**
  - Cas d'usage (créer un build alternatif)
  - Gestion des noms (suffixes automatiques)

---

### 🏰 2. Système de Royaume et Rang

#### 2.1 Rangs de Royaume
- **Aide - Comprendre les rangs de royaume**
  - Explication du système (rang 1-14, niveau L0-L10)
  - Titres associés à chaque rang
  - Couleurs par royaume
  - Comment mettre à jour les rangs

#### 2.2 Titres
- **Aide - Personnaliser les titres**
  - Sélection du titre affiché
  - Titres par défaut selon le rang
  - Création de titres personnalisés

---

### 🛡️ 3. Gestion des Armures

#### 3.1 Sets d'Armures
- **Aide - Gérer les sets d'armures**
  - Créer un set d'armure
  - Pièces d'armure (tête, torse, jambes, etc.)
  - Résistances par pièce
  - Calcul des résistances totales

#### 3.2 Résistances
- **Aide - Calculateur de résistances**
  - Types de résistances (Crush, Slash, Thrust, Body, etc.)
  - Caps de résistances
  - Optimisation des résistances

---

### 🌐 4. Eden Herald Integration

#### 4.1 Configuration
- **Aide - Configurer Eden Herald**
  - Obtenir les cookies Discord
  - Configurer le navigateur préféré
  - Autoriser/refuser téléchargement drivers
  - Tester la connexion

#### 4.2 Gestion des Cookies
- **Aide - Gérer les cookies Eden**
  - Génération via navigateur
  - Import depuis fichier
  - Test de validité
  - Rafraîchir les cookies expirés
  - Troubleshooting (erreurs courantes)

#### 4.3 Scraping
- **Aide - Rechercher des personnages**
  - Critères de recherche (nom, royaume, niveau)
  - Filtres avancés
  - Prévisualisation des résultats
  - Import sélectif

---

### ⚙️ 5. Configuration

#### 5.1 Paramètres Généraux
- **Aide - Configurer l'application**
  - Dossiers de stockage (Characters, Configuration, Logs)
  - Saison par défaut
  - Serveur par défaut
  - Royaume par défaut

#### 5.2 Paramètres d'Affichage
- **Aide - Personnaliser l'affichage**
  - Colonnes visibles/cachées
  - Largeur des colonnes (auto/manuel)
  - Tri et filtrage
  - Thème (clair/sombre - si implémenté)

#### 5.3 Paramètres de Langue
- **Aide - Changer la langue**
  - Langues disponibles (FR/EN/DE)
  - Impact sur l'interface
  - Traduction des données de jeu

#### 5.4 Paramètres de Debug
- **Aide - Mode débogage**
  - Activer les logs de debug
  - Fenêtre de debug principale
  - Fenêtre de debug Eden
  - Export des logs

---

### 🔧 6. Outils Avancés

#### 6.1 Migration
- **Aide - Migration de structure**
  - Pourquoi migrer (nouvelle structure par saison)
  - Sauvegarde automatique
  - Processus de migration
  - Rollback en cas d'erreur

#### 6.2 Backup/Restore
- **Aide - Sauvegarder et restaurer**
  - Créer un backup manuel
  - Sauvegardes automatiques
  - Restaurer depuis un backup
  - Emplacement des backups

---

### 📊 7. Interface et Navigation

#### 7.1 Navigation de Base
- **Aide - Navigation dans l'interface**
  - Menu Fichier
  - Menu Affichage
  - Menu Aide
  - Raccourcis clavier globaux

#### 7.2 Liste des Personnages
- **Aide - Gérer la liste**
  - Colonnes disponibles
  - Tri par colonne
  - Sélection multiple (Ctrl, Shift)
  - Menu contextuel (clic droit)
  - Glisser-déposer (si implémenté)

#### 7.3 Fiche Personnage
- **Aide - Fiche détaillée**
  - Navigation dans les onglets
  - Sauvegarde automatique
  - Validation des champs
  - Annulation des modifications

---

### 🔍 8. Recherche et Filtrage

#### 8.1 Recherche Locale
- **Aide - Rechercher dans vos personnages**
  - Recherche par nom
  - Filtrer par royaume
  - Filtrer par niveau
  - Filtrer par classe/race
  - Recherche avancée (expressions régulières)

---

### 🐛 9. Dépannage

#### 9.1 Problèmes Courants
- **Aide - Résoudre les problèmes courants**
  - Application ne démarre pas
  - Personnages ne s'affichent pas
  - Erreur lors de la sauvegarde
  - Cookies Eden expirés
  - Navigateur ne s'ouvre pas

#### 9.2 Logs et Debug
- **Aide - Utiliser les logs**
  - Où trouver les logs
  - Lire les logs de debug
  - Exporter les logs pour support
  - Niveaux de log (DEBUG, INFO, WARNING, ERROR)

---

## 🎨 Architecture Technique

### Structure des Fichiers

```
Help/
├── fr/
│   ├── character_create.md
│   ├── character_edit.md
│   ├── character_import.md
│   ├── realm_ranks.md
│   ├── armor_management.md
│   ├── eden_config.md
│   ├── cookies_management.md
│   ├── settings.md
│   ├── troubleshooting.md
│   └── ...
├── en/
│   └── [same files in English]
├── de/
│   └── [same files in German]
└── images/
    ├── character_create_01.png
    ├── character_create_02.png
    └── ...
```

### Format des Fichiers d'Aide

Chaque fichier d'aide suit cette structure Markdown :

```markdown
# [Titre de l'Aide]

## 📋 Résumé
[Description courte de 1-2 lignes]

## 🎯 Objectif
[Ce que l'utilisateur va apprendre]

## 📝 Étapes

### Étape 1 : [Titre]
[Description détaillée]
![Capture d'écran](../images/xxx.png)

### Étape 2 : [Titre]
[Description détaillée]

## ⚡ Raccourcis
- **Ctrl+N** : Nouveau personnage
- **F2** : Renommer

## ⚠️ Points d'Attention
[Erreurs courantes et comment les éviter]

## 💡 Astuces
[Conseils avancés]

## 🔗 Voir Aussi
- [Autre aide connexe]
```

---

## 🚀 Plan d'Implémentation

### Phase 1 : Infrastructure (PRIORITÉ IMMÉDIATE)
✅ Créer le dossier `Help/` avec sous-dossiers `fr/`, `en/`, `de/`, `images/`
✅ Créer la classe `HelpManager` pour gérer l'affichage des aides
✅ Créer la fenêtre `HelpWindow` avec lecteur Markdown
✅ Ajouter l'option "Aide - Créer un personnage" dans le menu Aide

### Phase 2 : Contenu Initial (1-2 semaines)
- ✅ Aide "Créer un nouveau personnage" (FR/EN/DE) + captures d'écran
- ⬜ Aide "Importer depuis Eden Herald"
- ⬜ Aide "Gérer les cookies Eden"
- ⬜ Aide "Configurer l'application"

### Phase 3 : Expansion (2-4 semaines)
- ⬜ Aides pour édition/suppression/duplication
- ⬜ Aides pour rangs de royaume
- ⬜ Aides pour gestion des armures
- ⬜ Aides pour navigation et interface

### Phase 4 : Avancé (4-8 semaines)
- ⬜ Système de recherche dans les aides
- ⬜ Index des aides avec catégories
- ⬜ Aide contextuelle (F1 sur un élément = aide ciblée)
- ⬜ Tutoriels interactifs avec highlight des éléments UI
- ⬜ Vidéos tutoriels intégrées (liens YouTube)

---

## 🎨 Fonctionnalités UI

### Menu Aide
```
Aide
├── 📖 Bibliothèque d'Aide          <- Nouvelle option : Index de toutes les aides
├── ──────────────────
├── 👤 Créer un personnage          <- Aide spécifique
├── 📥 Importer depuis Eden         <- Aide spécifique
├── 🍪 Gérer les cookies            <- Aide spécifique
├── ⚙️ Configurer l'application     <- Aide spécifique
├── ──────────────────
├── À propos
├── Migrer la structure des dossiers
└── 🌐 Debug Eden
```

### Fenêtre d'Aide

**Caractéristiques** :
- Fenêtre modale ou non-modale (configurable)
- Taille : 800x600 pixels
- Lecteur Markdown avec support :
  - Titres (H1-H6)
  - Listes (à puces, numérotées)
  - Code blocks
  - Images
  - Liens (internes et externes)
  - Emojis
  - Tables
- Barre de navigation :
  - Bouton "Précédent" (historique)
  - Bouton "Suivant" (historique)
  - Bouton "Index" (retour à la liste)
  - Champ de recherche
- Sidebar avec table des matières
- Boutons :
  - "Imprimer" (export PDF)
  - "Copier le lien"
  - "Signaler un problème"

---

## 📊 Métriques de Succès

1. **Couverture** : 100% des fonctionnalités majeures ont une aide
2. **Accessibilité** : Aide accessible en moins de 2 clics
3. **Clarté** : 90%+ des utilisateurs trouvent l'aide utile (sondage)
4. **Utilisation** : Tracking des aides les plus consultées
5. **Support** : Réduction de 50% des questions support répétitives

---

## 🔄 Maintenance

### Mise à Jour des Aides
- **Nouvelles fonctionnalités** : Aide créée en même temps
- **Modifications** : Aide mise à jour lors des changements
- **Bugs corrigés** : Aide mise à jour si le workflow change
- **Feedback utilisateurs** : Amélioration continue basée sur retours

### Traductions
- **Priorité FR** : Toujours en premier (langue principale)
- **EN et DE** : Traduction dans les 1-2 semaines suivantes
- **Vérification** : Relecture par natifs si possible

---

## 💡 Idées Avancées (Future)

1. **Aide Contextuelle (F1)** : Appuyer sur F1 sur n'importe quel élément ouvre l'aide correspondante
2. **Tooltips Riches** : Tooltips avec mini-aperçu de l'aide (hover + Ctrl)
3. **Assistant de Configuration** : Wizard lors du premier lancement
4. **Tutoriels Interactifs** : Highlight des éléments UI avec instructions overlay
5. **Vidéos Tutoriels** : Intégration de vidéos courtes (YouTube)
6. **Changelog Intégré** : "Quoi de neuf ?" avec les nouveautés de chaque version
7. **Tips du Jour** : Astuce aléatoire au démarrage (désactivable)
8. **Aide par IA** : Chatbot simple pour recherche d'aide
9. **Mode Débutant** : Interface simplifiée avec aide inline
10. **Badges/Achievements** : Gamification de l'apprentissage

---

## 📝 Notes

- **Markdown** : Format choisi pour facilité d'édition et portabilité
- **Images** : PNG avec compression optimale, max 800px largeur
- **Captures d'écran** : Annotations avec flèches et numéros
- **Cohérence** : Même template pour toutes les aides
- **Accessibilité** : Texte alternatif pour toutes les images
- **SEO Interne** : Mots-clés dans titres pour recherche efficace

---

## 🎯 Prochaines Actions

1. ✅ Créer ce document de planification
2. ✅ Créer l'infrastructure de base (HelpManager, HelpWindow)
3. ✅ Implémenter la première aide "Créer un personnage"
4. ⬜ Ajouter les captures d'écran
5. ⬜ Tester avec utilisateurs
6. ⬜ Itérer et améliorer
7. ⬜ Créer les 5 aides prioritaires suivantes
8. ⬜ Déployer en v0.106

---

**Date de création** : 30 octobre 2025  
**Version** : 1.0  
**Statut** : 📋 Planification  
**Prochaine révision** : À la fin de la Phase 1
