# Changelog - Système de Templates d'Armurerie

## [2025-11-19] Refonte complète du système de templates

### ✨ Nouvelles fonctionnalités

#### Import contextuel depuis fiche personnage
- Import **uniquement depuis la fiche du personnage** (plus dans Settings)
- Détection automatique de la classe et du realm du personnage
- Pré-sélection de la saison actuelle (configurable)
- Champ de description libre pour personnaliser le nom du template

#### Nomenclature standardisée
- Format: `{Classe}_{Saison}_{Description}.txt`
- Normalisation automatique (espaces → underscores, accents retirés)
- Exemples: `Bard_S3_Low_Cost_Sans_ML10.txt`, `Cleric_S2_Full_RvR_ML10.txt`

#### Système de tags
- Tags personnalisables pour catégoriser les templates
- Auto-complétion avec suggestions (budget, content, level, ml, source, spec)
- Limite de 5 tags par template
- Tags affichés sous forme de badges cliquables

#### Métadonnées riches
- Fichier JSON associé à chaque template (.json)
- Stockage: classe (EN/FR/DE), realm, saison, description, tags, source, date, importeur, nombre d'items
- Index global pour recherches rapides (.template_index.json)

#### Filtrage par classe
- Templates visibles **uniquement pour la classe du personnage**
- Exemple: Un Bard ne voit que les templates Bard

#### Recherche et filtrage avancés
- Recherche textuelle (nom + description)
- Filtrage par saison
- Tri par date, nom ou nombre d'items
- Interface en cards avec infos visuelles

#### Aperçu de template
- Dialogue d'aperçu avant chargement
- Affichage complet des métadonnées
- Liste des items (numérotée)
- Statistiques (items, date, source, etc.)

### 🏗️ Architecture

#### Nouveaux composants

**Backend:**
- `Functions/template_metadata.py` - Gestion des métadonnées
- `Functions/template_manager.py` - Manager principal (CRUD, filtrage, index)
- `Functions/config_manager.py` - Méthodes `get_current_season()`, `get_available_seasons()`, `add_season()`, `set_current_season()`

**UI:**
- `UI/template_import_dialog.py` - Dialogue d'import contextuel
- `UI/widgets/tag_selector.py` - Widget de sélection de tags
- `UI/widgets/template_list_widget.py` - Liste des templates avec recherche/filtrage
- `UI/dialogs/template_preview_dialog.py` - Dialogue d'aperçu

**Structure fichiers:**
```
Armory/
├── Bard_S3_Low_Cost_Sans_ML10.txt        # Template
├── Bard_S3_Low_Cost_Sans_ML10.json       # Métadonnées
├── .template_index.json                   # Index (cache)
└── items_database.json                    # Base personnelle (existant)
```

### 🌍 Traductions

Ajout de 3 nouvelles sections dans `Language/{fr,en,de}.json`:
- `template_import` - Interface d'import (17 clés)
- `template_list` - Liste et filtres (14 clés)
- `template_preview` - Dialogue d'aperçu (13 clés)

### 📝 Configuration

Utilisation de la section existante `game` dans `config.json`:
```json
{
  "game": {
    "seasons": ["S3"],
    "default_season": "S3"
  }
}
```

### 🔄 Changements

#### Supprimé
- ❌ Import de templates depuis Settings (sera retiré dans prochaine version)

#### Conservation
- ✅ Affichage actuel de l'armure dans fiche personnage (design préservé)
- ✅ Base de données items (inchangée)
- ✅ Système de scraping (inchangé)

### 📋 Migration

**Migration des anciens templates:**
- Les anciens templates (sans métadonnées) restent fonctionnels
- Script de migration prévu (Phase 5 - à venir)
- Renommage automatique selon nouvelle convention
- Création automatique des métadonnées

### 🚀 Prochaines étapes

**Phase 5 - Migration et tests:**
- [ ] Script de migration des anciens templates
- [ ] Tests complets du système
- [ ] Documentation utilisateur

**Phase 6 - Nettoyage et polish:**
- [ ] Suppression code import depuis Settings
- [ ] Intégration dans CharacterSheetWindow
- [ ] Polish UI (icônes, tooltips)
- [ ] Tests utilisateur

### 📖 Documentation technique

Voir `Documentations/Armory/ARMORY_REFACTORING_PLAN.md` pour:
- Plan d'implémentation complet
- Spécifications fonctionnelles détaillées
- Architecture technique
- Exemples de code

---

**Développeur:** GitHub Copilot  
**Date:** 19 novembre 2025  
**Version:** 1.0  
**Branch:** 108_Imp_Armo
