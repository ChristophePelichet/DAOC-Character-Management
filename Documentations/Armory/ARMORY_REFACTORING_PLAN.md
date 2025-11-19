# Plan d'Implémentation - Refonte du Système d'Armurerie

**Date:** 2025-11-19  
**Version:** 1.0  
**Objectif:** Refonte complète du système d'import de templates pour une meilleure organisation et utilisation contextuelle

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Spécifications fonctionnelles](#spécifications-fonctionnelles)
3. [Améliorations proposées](#améliorations-proposées)
4. [Architecture technique](#architecture-technique)
5. [Plan de migration](#plan-de-migration)
6. [Plan d'implémentation détaillé](#plan-dimplémentation-détaillé)
7. [Impact utilisateur](#impact-utilisateur)

---

## 1. Vue d'ensemble

### 1.1 Problème actuel

- Import de templates depuis les paramètres (déconnecté du contexte)
- Pas de filtrage par classe
- Pas d'organisation par saison
- Nommage manuel sans convention
- Difficulté à retrouver les templates pertinents

### 1.2 Vision cible

**Principe fondamental:** Les templates sont importés **depuis la fiche du personnage** pour un contexte automatique et une organisation intelligente.

**Bénéfices:**
- ✅ Import contextuel (classe automatiquement détectée)
- ✅ Organisation par classe et saison
- ✅ Nommage standardisé et parlant
- ✅ Filtrage automatique par classe dans l'inventaire
- ✅ Gestion des versions/saisons
- ✅ Métadonnées riches (tags, description, date)

---

## 2. Spécifications fonctionnelles

### 2.1 Import de template

**Point d'entrée:** Fiche du personnage uniquement

**Workflow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      WORKFLOW D'IMPORT                          │
└─────────────────────────────────────────────────────────────────┘

1. Utilisateur clique sur "Importer un template" dans la fiche perso
   │
   ├──> Système détecte automatiquement:
   │    - Classe du personnage (ex: "Bard")
   │    - Realm du personnage (ex: "Hibernia")
   │    - Saison actuelle du logiciel (ex: "S3")
   │
2. Dialogue d'import s'ouvre
   │
   ├──> Champs pré-remplis:
   │    - Classe: "Bard" (lecture seule, grisé)
   │    - Realm: "Hibernia" (lecture seule, grisé)
   │    - Saison: "S3" (modifiable via dropdown)
   │
   ├──> Champs à remplir par l'utilisateur:
   │    - Fichier source: "Eden - Hibernia - Bard_Summary.txt"
   │    - Description: "low cost sans ml10" (texte libre)
   │    - Tags optionnels: ["low-cost", "pve", "débutant"]
   │
3. Système génère le nom du fichier template
   │
   └──> Format: {Classe}_{Saison}_{Description_normalisée}.txt
        Exemple: "Bard_S3_Low_Cost_Sans_ML10.txt"
   
4. Template enregistré dans Armory/
   │
   └──> Métadonnées stockées dans un fichier JSON associé

5. Template visible uniquement pour les personnages de classe "Bard"
```

### 2.2 Nommage des templates

**Convention de nommage:**

```
Format: {Classe}_{Saison}_{Description}.txt

Composants:
  - Classe: Nom de la classe en anglais (ex: Bard, Cleric, Warrior)
  - Saison: Version du jeu (S1, S2, S3, S4, etc.)
  - Description: Texte libre normalisé (espaces → underscores, accents retirés)

Exemples:
  ✅ Bard_S3_Low_Cost_Sans_ML10.txt
  ✅ Cleric_S2_Full_RvR_ML10.txt
  ✅ Warrior_S3_Budget_PvE.txt
  ✅ Sorcerer_S1_Template_Eden_Officiel.txt
```

**Normalisation de la description:**
- Espaces → `_`
- Accents retirés (é → e, à → a, etc.)
- Caractères spéciaux retirés (sauf `-` et `_`)
- Majuscules préservées pour lisibilité
- Limite de 50 caractères

### 2.3 Métadonnées des templates

**Fichier métadonnées:** `{nom_template}.json`

**Structure:**

```json
{
  "version": "1.0",
  "template_name": "Bard_S3_Low_Cost_Sans_ML10.txt",
  "metadata": {
    "class": "Bard",
    "class_fr": "Barde",
    "class_de": "Barde",
    "realm": "Hibernia",
    "season": "S3",
    "description": "low cost sans ml10",
    "tags": ["low-cost", "pve", "débutant"],
    "source_file": "Eden - Hibernia - Bard_Summary.txt",
    "import_date": "2025-11-19T14:30:00",
    "imported_by_character": "Mon Barde",
    "item_count": 45,
    "auto_generated": true
  },
  "notes": "Template importé depuis Eden pour un équipement économique PvE"
}
```

**Champs métadonnées:**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `class` | string | ✅ | Nom classe (EN) |
| `class_fr` | string | ✅ | Nom classe (FR) |
| `class_de` | string | ✅ | Nom classe (DE) |
| `realm` | string | ✅ | Albion/Hibernia/Midgard |
| `season` | string | ✅ | Saison (S1, S2, S3, etc.) |
| `description` | string | ✅ | Description courte |
| `tags` | array | ❌ | Tags libres |
| `source_file` | string | ✅ | Fichier source original |
| `import_date` | ISO 8601 | ✅ | Date d'import |
| `imported_by_character` | string | ✅ | Nom du personnage |
| `item_count` | int | ✅ | Nombre d'items |
| `auto_generated` | bool | ✅ | Généré automatiquement |

### 2.4 Filtrage des templates

**Règle de filtrage:**

Dans la fiche d'un personnage, seuls les templates **de la même classe** sont visibles.

**Exemple:**

```python
# Personnage: "Mon Barde" (classe: Bard)

Templates visibles:
  ✅ Bard_S3_Low_Cost_Sans_ML10.txt
  ✅ Bard_S2_Full_RvR_ML10.txt
  ✅ Bard_S3_Budget_PvE.txt

Templates cachés:
  ❌ Cleric_S3_Heal_Spec.txt (classe différente)
  ❌ Warrior_S2_Tank_Build.txt (classe différente)
  ❌ Sorcerer_S1_Nuke.txt (classe différente)
```

**Implémentation:**

```python
def get_available_templates_for_character(character_class):
    """Retourne les templates disponibles pour une classe"""
    armory_path = Path("Armory")
    all_templates = list(armory_path.glob("*.txt"))
    
    filtered_templates = []
    for template_file in all_templates:
        # Lire les métadonnées
        metadata_file = template_file.with_suffix('.json')
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if metadata['metadata']['class'] == character_class:
                    filtered_templates.append({
                        'file': template_file,
                        'metadata': metadata
                    })
    
    return filtered_templates
```

### 2.5 Gestion des saisons

**Saisons supportées:**

Les saisons sont configurées dans `Configuration/config.json` (section `game`):

```json
{
  "game": {
    "servers": ["Eden"],
    "default_server": "Eden",
    "seasons": ["S1", "S2", "S3"],
    "default_season": "S3",
    "default_realm": "Albion"
  }
}
```

**Interface de sélection:**

Dans le dialogue d'import, dropdown avec:
- Saison actuelle pré-sélectionnée (depuis `default_season`)
- Toutes les saisons disponibles (depuis `seasons`)
- Option "Personnalisé" pour saisie libre (ajout dynamique à la liste)

---

## 3. Améliorations proposées

### 3.1 Système de tags

**Objectif:** Catégoriser les templates pour faciliter la recherche

**Tags suggérés:**

| Catégorie | Tags |
|-----------|------|
| **Budget** | `low-cost`, `budget`, `premium`, `high-end` |
| **Contenu** | `pve`, `pvp`, `rvr`, `solo`, `groupe` |
| **Niveau** | `débutant`, `intermédiaire`, `avancé` |
| **ML** | `ml1`, `ml5`, `ml10`, `sans-ml` |
| **Source** | `eden`, `officiel`, `communauté`, `personnel` |
| **Spécialisation** | `heal`, `dps`, `tank`, `support`, `cc` |

**Interface de sélection:**

- Champ texte avec auto-complétion
- Tags prédéfinis cliquables
- Possibilité de créer des tags personnalisés
- Maximum 5 tags par template

### 3.2 Recherche et filtrage avancés

**Dans la fiche personnage:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Templates Bard disponibles                     [🔍 Recherche]  │
├─────────────────────────────────────────────────────────────────┤
│  Filtres: [Saison ▼] [Tags ▼] [Trier par ▼]                    │
├─────────────────────────────────────────────────────────────────┤
│  📄 Bard_S3_Low_Cost_Sans_ML10                          45 items│
│     Saison 3 • low-cost, pve, débutant                          │
│     Importé le 19/11/2025                                       │
│     [👁️ Aperçu] [📥 Charger] [🗑️ Supprimer]                     │
├─────────────────────────────────────────────────────────────────┤
│  📄 Bard_S3_Budget_PvE                                  52 items│
│     Saison 3 • budget, pve, groupe                              │
│     Importé le 15/11/2025                                       │
│     [👁️ Aperçu] [📥 Charger] [🗑️ Supprimer]                     │
└─────────────────────────────────────────────────────────────────┘
```

**Options de tri:**
- Par date (plus récent d'abord)
- Par nom (alphabétique)
- Par nombre d'items
- Par saison

**Options de filtrage:**
- Par saison (S1, S2, S3, etc.)
- Par tags
- Par recherche textuelle (nom + description)

### 3.3 Aperçu du template

**Fenêtre d'aperçu (lecture seule):**

- Liste des items du template
- Statistiques (nombre d'items, slots couverts)
- Métadonnées complètes
- Boutons: [Charger] [Fermer]

---

## 4. Architecture technique

### 4.1 Nouvelle structure de fichiers

```
Armory/
├── templates/                          # Templates organisés
│   ├── Bard_S3_Low_Cost_Sans_ML10.txt
│   ├── Bard_S3_Low_Cost_Sans_ML10.json     # Métadonnées
│   ├── Cleric_S2_Full_RvR_ML10.txt
│   ├── Cleric_S2_Full_RvR_ML10.json
│   └── ...
│
├── .template_index.json                # Index des templates (cache)
└── items_database.json                 # Base personnelle (existant)

Configuration/
└── config.json                         # Configuration globale (section game.seasons)
```

**Index des templates (.template_index.json):**

```json
{
  "version": "1.0",
  "last_updated": "2025-11-19T14:30:00",
  "templates": [
    {
      "file": "Bard_S3_Low_Cost_Sans_ML10.txt",
      "class": "Bard",
      "realm": "Hibernia",
      "season": "S3",
      "tags": ["low-cost", "pve", "débutant"],
      "item_count": 45,
      "import_date": "2025-11-19T14:30:00"
    },
    {
      "file": "Cleric_S2_Full_RvR_ML10.txt",
      "class": "Cleric",
      "realm": "Albion",
      "season": "S2",
      "tags": ["premium", "rvr", "ml10"],
      "item_count": 52,
      "import_date": "2025-11-15T10:20:00"
    }
  ]
}
```

**Avantages de l'index:**
- Chargement rapide (pas besoin de lire tous les fichiers JSON)
- Recherche et filtrage performants
- Mise à jour automatique lors d'import/suppression

### 4.2 Nouveaux composants

#### 4.2.1 TemplateManager

**Responsabilités:**
- Import de templates
- Génération de noms
- Création de métadonnées
- Filtrage par classe
- Gestion de l'index

**Méthodes principales:**

```python
class TemplateManager:
    def import_template(self, source_file, character_class, realm, season, description, tags):
        """Importe un nouveau template"""
        
    def get_templates_for_class(self, character_class):
        """Retourne les templates filtrés par classe"""
        
    def generate_template_name(self, character_class, season, description):
        """Génère le nom du template selon la convention"""
        
    def create_metadata(self, template_name, metadata_dict):
        """Crée le fichier JSON de métadonnées"""
        
    def delete_template(self, template_name):
        """Supprime un template et ses métadonnées"""
        
    def update_index(self):
        """Met à jour l'index des templates"""
        
    def search_templates(self, query, filters):
        """Recherche des templates avec filtres"""
```

#### 4.2.2 TemplateImportDialog (refonte)

**Changements:**

**AVANT:**
- Ouvert depuis Settings (onglet Armory)
- Pas de contexte de personnage

**APRÈS:**
- Ouvert depuis la fiche du personnage
- Contexte automatique (classe, realm)
- Champs pré-remplis intelligents

**Nouvelle interface:**

```python
class TemplateImportDialog(QDialog):
    def __init__(self, parent, character):
        """
        parent: Fenêtre parente
        character: Objet Character (pour extraire classe et realm)
        """
        self.character = character
        self.template_manager = TemplateManager()
        
    def _setup_ui(self):
        """Configure l'interface avec champs contextuels"""
        # Champs lecture seule
        self.class_label = QLabel(self.character.character_class)  # Grisé
        self.realm_label = QLabel(self.character.realm)            # Grisé
        
        # Champs modifiables
        self.season_combo = QComboBox()  # Dropdown avec saisons
        self.description_edit = QLineEdit()  # Texte libre
        self.tags_widget = TagSelector()  # Widget de sélection de tags
        
        # Aperçu du nom généré
        self.preview_label = QLabel()  # Mise à jour en temps réel
```

#### 4.2.3 TemplateListWidget

**Nouveau widget pour afficher les templates dans la fiche personnage**

**Fonctionnalités:**
- Liste filtrée par classe
- Recherche et filtrage
- Actions: Aperçu, Charger, Supprimer
- Tri personnalisable

```python
class TemplateListWidget(QWidget):
    template_selected = Signal(str)  # Nom du template sélectionné
    
    def __init__(self, parent, character_class):
        self.character_class = character_class
        self.template_manager = TemplateManager()
        
    def load_templates(self):
        """Charge les templates pour la classe"""
        templates = self.template_manager.get_templates_for_class(
            self.character_class
        )
        self._populate_list(templates)
        
    def filter_templates(self, season=None, tags=None, search_text=None):
        """Applique des filtres"""
```

### 4.3 Modifications existantes

#### 4.3.1 CharacterSheetWindow

**Ajout d'un onglet "Templates" ou section dans l'onglet Équipement:**

```python
class CharacterSheetWindow(QDialog):
    def _create_equipment_tab(self):
        # ... code existant pour l'affichage de l'équipement ...
        
        # NOUVEAU: Section templates
        template_group = QGroupBox("Templates disponibles")
        template_layout = QVBoxLayout()
        
        # Bouton d'import
        import_btn = QPushButton("📥 Importer un template")
        import_btn.clicked.connect(self._open_template_import)
        
        # Liste des templates
        self.template_list = TemplateListWidget(self, self.character.character_class)
        self.template_list.template_selected.connect(self._load_template)
        
        template_layout.addWidget(import_btn)
        template_layout.addWidget(self.template_list)
        template_group.setLayout(template_layout)
        
        # Ajouter au layout principal
        layout.addWidget(template_group)
    
    def _open_template_import(self):
        """Ouvre le dialogue d'import avec contexte du personnage"""
        dialog = TemplateImportDialog(self, self.character)
        if dialog.exec_() == QDialog.Accepted:
            self.template_list.load_templates()  # Rafraîchir la liste
    
    def _load_template(self, template_name):
        """Charge un template dans l'équipement du personnage"""
        # ... logique de chargement ...
```

#### 4.3.2 Settings Dialog

**Suppression de l'onglet Armory Import (déplacé dans les fiches perso)**

**Conservation:**
- Configuration du dossier Armory
- Mode base de données (interne vs personnelle)
- Statistiques

**Suppression:**
- Bouton "Importer des items" (déplacé dans fiche perso)

---

## 5. Plan de migration

### 5.1 Migration des templates existants

**Problème:** Templates existants sans métadonnées

**Solution:** Script de migration automatique

```python
def migrate_existing_templates():
    """Migre les anciens templates vers le nouveau format"""
    armory_path = Path("Armory")
    old_templates = list(armory_path.glob("*.txt"))
    
    for template_file in old_templates:
        # Vérifier si métadonnées existent déjà
        metadata_file = template_file.with_suffix('.json')
        if metadata_file.exists():
            continue  # Déjà migré
        
        # Dialogue pour saisir les métadonnées
        metadata = prompt_metadata_for_template(template_file)
        
        # Renommer le fichier selon la convention
        new_name = generate_template_name(
            metadata['class'],
            metadata['season'],
            metadata['description']
        )
        
        # Déplacer et créer métadonnées
        new_path = armory_path / new_name
        template_file.rename(new_path)
        
        create_template_metadata(new_path, metadata)
```

**Interface de migration:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Migration des templates                                        │
├─────────────────────────────────────────────────────────────────┤
│  Ancien fichier: Eden - Hibernia - Bard_Summary.txt             │
│                                                                  │
│  Classe:       [Bard ▼]                                         │
│  Realm:        [Hibernia ▼]                                     │
│  Saison:       [S3 ▼]                                           │
│  Description:  [Eden officiel________]                          │
│  Tags:         [officiel] [pve]                                 │
│                                                                  │
│  Nouveau nom:  Bard_S3_Eden_Officiel.txt                        │
│                                                                  │
│                [Ignorer] [Migrer] [Migrer tout]                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Compatibilité descendante

**Stratégie:**

1. **Phase 1 (1-2 semaines):** Support des deux formats
   - Anciens templates continuent de fonctionner
   - Nouveaux imports utilisent le nouveau format
   - Bannière "Migrer vos templates" dans l'interface

2. **Phase 2 (après migration):** Migration forcée
   - Dialogue de migration au démarrage si anciens templates détectés
   - Bouton "Plus tard" pour reporter

3. **Phase 3 (version suivante):** Nouveau format uniquement
   - Anciens templates ignorés
   - Message d'avertissement clair

---

## 6. Plan d'implémentation détaillé

### Phase 1: Fondations (2-3 jours)

**Objectif:** Structures de données et configuration

**Tâches:**

1. **Mise à jour config.json**
   - [ ] Vérifier section game.seasons (déjà existante)
   - [ ] Fonction get_current_season() depuis ConfigManager
   - [ ] Tests unitaires

2. **Créer TemplateManager**
   - [ ] Classe de base
   - [ ] generate_template_name()
   - [ ] create_metadata()
   - [ ] Tests unitaires

3. **Créer structure métadonnées**
   - [ ] Définir schéma JSON
   - [ ] Validation des champs
   - [ ] Tests unitaires

4. **Traductions**
   - [ ] Ajouter clés FR/EN/DE dans Language/*.json
   - [ ] Templates d'interface

**Fichiers créés:**
- `Functions/template_manager.py`
- `Functions/template_metadata.py`

**Fichiers modifiés:**
- `Functions/config_manager.py` (ajout get_current_season(), get_available_seasons())

**Livrable:** Fondations prêtes pour l'intégration UI

---

### Phase 2: Interface d'import (3-4 jours)

**Objectif:** Dialogue d'import contextuel

**Tâches:**

1. **Refonte TemplateImportDialog**
   - [ ] Passage du personnage en paramètre
   - [ ] Champs contextuels (classe, realm)
   - [ ] Dropdown saison
   - [ ] Champ description avec normalisation
   - [ ] Widget de sélection de tags
   - [ ] Aperçu du nom généré en temps réel

2. **Widget de tags (TagSelector)**
   - [ ] Auto-complétion
   - [ ] Tags prédéfinis cliquables
   - [ ] Limite de 5 tags
   - [ ] Affichage visuel (badges)

3. **Validation et import**
   - [ ] Validation des champs
   - [ ] Vérification des doublons
   - [ ] Création du template
   - [ ] Création des métadonnées
   - [ ] Mise à jour de l'index

4. **Tests**
   - [ ] Tests UI
   - [ ] Tests d'import
   - [ ] Tests de validation

**Fichiers modifiés:**
- `UI/armory_import_dialog.py`

**Fichiers créés:**
- `UI/widgets/tag_selector.py`

**Livrable:** Dialogue d'import fonctionnel avec contexte

---

### Phase 3: Liste des templates (2-3 jours)

**Objectif:** Affichage et filtrage dans la fiche personnage

**Tâches:**

1. **Créer TemplateListWidget**
   - [ ] Liste avec métadonnées
   - [ ] Filtrage par saison
   - [ ] Filtrage par tags
   - [ ] Recherche textuelle
   - [ ] Tri (date, nom, items)

2. **Actions sur templates**
   - [ ] Bouton "Aperçu"
   - [ ] Bouton "Charger"
   - [ ] Bouton "Supprimer"
   - [ ] Confirmations

3. **Fenêtre d'aperçu**
   - [ ] Affichage métadonnées
   - [ ] Liste des items
   - [ ] Statistiques
   - [ ] Bouton charger

4. **Intégration dans CharacterSheetWindow**
   - [ ] Ajouter TemplateListWidget
   - [ ] Connecter signaux
   - [ ] Tests d'intégration

**Fichiers créés:**
- `UI/widgets/template_list_widget.py`
- `UI/dialogs/template_preview_dialog.py`

**Fichiers modifiés:**
- `UI/dialogs.py` (CharacterSheetWindow)

**Livrable:** Interface complète de gestion des templates

---

### Phase 4: Fonctionnalités avancées (2-3 jours)

**Objectif:** Index, recherche, optimisations

**Tâches:**

1. **Système d'index**
   - [ ] Création de .template_index.json
   - [ ] Mise à jour automatique
   - [ ] Chargement au démarrage
   - [ ] Invalidation et rebuild

2. **Recherche avancée**
   - [ ] Recherche full-text
   - [ ] Filtres combinés
   - [ ] Suggestions
   - [ ] Highlighting

3. **TemplateManager complet**
   - [ ] get_templates_for_class()
   - [ ] search_templates()
   - [ ] delete_template()
   - [ ] update_index()

4. **Optimisations**
   - [ ] Cache en mémoire
   - [ ] Chargement lazy
   - [ ] Tests de performance

**Fichiers modifiés:**
- `Functions/template_manager.py`

**Livrable:** Système complet et performant

---

### Phase 5: Migration et tests (2-3 jours)

**Objectif:** Migration des anciens templates et tests complets

**Tâches:**

1. **Script de migration**
   - [ ] Détection des anciens templates
   - [ ] Dialogue de saisie métadonnées
   - [ ] Renommage automatique
   - [ ] Création métadonnées
   - [ ] Rapport de migration

2. **Interface de migration**
   - [ ] Dialogue au démarrage
   - [ ] Progression
   - [ ] Gestion des erreurs
   - [ ] Option "Plus tard"

3. **Tests complets**
   - [ ] Tests d'import
   - [ ] Tests de filtrage
   - [ ] Tests de migration
   - [ ] Tests de compatibilité

4. **Documentation**
   - [ ] Guide utilisateur
   - [ ] Documentation technique
   - [ ] Changelog

**Fichiers créés:**
- `Scripts/migrate_templates.py`
- `Documentations/Armory/TEMPLATE_SYSTEM_USER_GUIDE.md`

**Livrable:** Système prêt pour production

---

### Phase 6: Nettoyage et polish (1-2 jours)

**Objectif:** Finitions et optimisations

**Tâches:**

1. **Suppression ancien code**
   - [ ] Retirer import depuis Settings
   - [ ] Nettoyer code inutilisé
   - [ ] Mise à jour des imports

2. **Polish UI**
   - [ ] Icônes
   - [ ] Tooltips
   - [ ] Messages d'aide
   - [ ] Accessibilité

3. **Tests utilisateur**
   - [ ] Scénarios complets
   - [ ] Feedback
   - [ ] Corrections

4. **Documentation finale**
   - [ ] README mis à jour
   - [ ] Changelog détaillé
   - [ ] Guide de migration

**Livrable:** Version finale polished

---

## 7. Impact utilisateur

### 7.1 Workflow avant/après

**AVANT:**

```
1. Ouvrir Settings
2. Aller dans onglet Armory
3. Cliquer "Importer des items"
4. Sélectionner le fichier
5. Attendre le scraping
6. Aucune organisation
7. Difficile de retrouver les templates
8. Aucun filtrage par classe
```

**APRÈS:**

```
1. Ouvrir la fiche du personnage
2. Cliquer "Importer un template"
3. Sélectionner le fichier
4. Remplir la description
5. Template nommé automatiquement selon la classe
6. Visible uniquement pour la classe du personnage
7. Recherche et filtrage faciles
8. Organisation par saison
```

### 7.2 Avantages

**Pour l'utilisateur:**
- ✅ Contexte automatique (plus d'erreurs de classe)
- ✅ Organisation claire par classe et saison
- ✅ Recherche rapide
- ✅ Moins de clics
- ✅ Nommage cohérent

**Pour le développement:**
- ✅ Code mieux organisé
- ✅ Métadonnées riches pour futures fonctionnalités
- ✅ Facilite l'ajout de fonctionnalités (export, partage, etc.)
- ✅ Tests plus faciles

### 7.3 Migration utilisateur

**Message au démarrage (si anciens templates détectés):**

```
┌─────────────────────────────────────────────────────────────────┐
│  Nouveau système de templates ! 🎉                              │
├─────────────────────────────────────────────────────────────────┤
│  Nous avons amélioré l'organisation de vos templates :          │
│                                                                  │
│  ✨ Import depuis la fiche du personnage                        │
│  ✨ Organisation par classe et saison                           │
│  ✨ Recherche et filtrage avancés                               │
│                                                                  │
│  Nous avons détecté 5 anciens templates.                        │
│  Voulez-vous les migrer maintenant ?                            │
│                                                                  │
│  [Plus tard] [Migrer maintenant]                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Estimation globale

**Temps total estimé:** 12-18 jours de développement

**Répartition:**
- Phase 1 (Fondations): 2-3 jours
- Phase 2 (Interface import): 3-4 jours
- Phase 3 (Liste templates): 2-3 jours
- Phase 4 (Fonctionnalités avancées): 2-3 jours
- Phase 5 (Migration et tests): 2-3 jours
- Phase 6 (Polish): 1-2 jours

**Complexité:** Moyenne
**Risques:** Faibles (ajout de fonctionnalités, peu de refactoring majeur)

---

## 9. Checklist de validation

### Tests fonctionnels

- [ ] Import d'un template depuis fiche perso
- [ ] Détection automatique classe et realm
- [ ] Génération correcte du nom
- [ ] Création des métadonnées
- [ ] Filtrage par classe
- [ ] Recherche et filtres
- [ ] Aperçu d'un template
- [ ] Chargement d'un template
- [ ] Suppression d'un template
- [ ] Migration des anciens templates

### Tests techniques

- [ ] Validation des champs
- [ ] Gestion des erreurs
- [ ] Performance (index)
- [ ] Compatibilité ascendante
- [ ] Tests unitaires
- [ ] Tests d'intégration

### Documentation

- [ ] Guide utilisateur
- [ ] Documentation technique
- [ ] Changelog
- [ ] Traductions FR/EN/DE

---

**FIN DU PLAN D'IMPLÉMENTATION**

Ce plan est évolutif et sera ajusté selon les retours et découvertes lors de l'implémentation.
