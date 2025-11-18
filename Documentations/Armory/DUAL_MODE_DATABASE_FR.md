# Système de Base de Données Double Mode - Documentation Technique

## Vue d'ensemble

Le système Armory implémente une **architecture de base de données double mode** qui permet aux utilisateurs de choisir entre deux modes d'opération :

- **Mode 1 (Base Interne)** : Mode lecture seule utilisant `Data/items_database.json` embarqué
- **Mode 2 (Base Personnelle)** : Mode géré par l'utilisateur avec une copie dans `Armory/items_database.json`

Cette architecture offre de la flexibilité pour différents cas d'usage tout en maintenant l'intégrité des données.

---

## Architecture

### Fichiers de Base de Données

#### Base Interne (Mode 1)
- **Emplacement** : `Data/items_database.json`
- **Type** : Lecture seule, embarqué dans l'application
- **Objectif** : Base de données par défaut livrée avec l'application
- **Mises à jour** : Uniquement via les mises à jour de l'application
- **Persistance** : Aucune modification utilisateur autorisée

#### Base Personnelle (Mode 2)
- **Emplacement** : `Armory/items_database.json`
- **Type** : Géré par l'utilisateur, éditable
- **Objectif** : Permet la personnalisation et les ajouts utilisateur
- **Mises à jour** : L'utilisateur peut importer, ajouter, modifier des items
- **Persistance** : Tous les changements sauvegardés en permanence

### Sélection du Mode

Le mode actif est contrôlé par la clé de configuration :
```json
{
  "armory": {
    "use_personal_database": false,  // Mode 1 (défaut)
    "use_personal_database": true    // Mode 2
  }
}
```

---

## Fonctionnalités par Mode

### Mode 1 : Base Interne (Lecture Seule)

**Capacités** :
- ✅ Rechercher des items par nom, royaume, type
- ✅ Voir les statistiques d'items (armure, résistances, bonus)
- ✅ Scraper des items depuis Eden/Zenkraft (stockage temporaire)
- ✅ Exporter les items scrapés vers des fichiers

**Limitations** :
- ❌ Impossible de sauvegarder les items scrapés en permanence
- ❌ Impossible de modifier les items existants
- ❌ Impossible d'ajouter des items personnalisés
- ❌ Pas de fonctionnalité d'import

**Cas d'usage** :
- Utilisateurs occasionnels n'ayant pas besoin de persistance
- Recherches d'items temporaires pendant le jeu
- Tests/validation sans modification de données
- Installations portables sans accès en écriture

### Mode 2 : Base Personnelle (Gérée par l'Utilisateur)

**Capacités** :
- ✅ Toutes les capacités du Mode 1
- ✅ **Stockage persistant** des items scrapés
- ✅ **Ajout automatique** des items scrapés (configurable)
- ✅ **Import d'items** depuis des fichiers template
- ✅ Ajout d'items personnalisés manuellement
- ✅ Modification des items existants
- ✅ Réinitialisation vers la copie de la base interne

**Fonctionnalités Supplémentaires** :
- Suivi des statistiques (interne vs. personnel vs. ajouté par l'utilisateur)
- Gestion des versions de base de données
- Sauvegardes automatiques lors de la réinitialisation

**Cas d'usage** :
- Utilisateurs avancés construisant des bases d'items personnelles
- Leaders de guilde maintenant des listes d'items partagées
- Théorycrafters avec des données d'items personnalisées
- Collection et analyse de données à long terme

---

## Gestionnaire de Base de Données (ItemsDatabaseManager)

### Méthodes Principales

#### 1. `get_active_database_path() -> Path`
Retourne le chemin vers la base de données actuellement active selon le mode.

**Retourne** :
- Mode 1 : `Data/items_database.json`
- Mode 2 : `Armory/items_database.json`

**Utilisation** :
```python
db_path = db_manager.get_active_database_path()
```

#### 2. `search_item(item_name: str, realm: str = None) -> dict`
Recherche un item dans la base de données active.

**Paramètres** :
- `item_name` : Nom de l'item à rechercher (insensible à la casse)
- `realm` : Filtre de royaume optionnel ("Albion", "Hibernia", "Midgard")

**Retourne** :
- Dictionnaire avec les données de l'item si trouvé
- `None` si non trouvé

**Utilisation** :
```python
item = db_manager.search_item("Dragon Slayer Sword", realm="Albion")
```

#### 3. `create_personal_database() -> tuple[bool, str]`
Crée une base de données personnelle en copiant la base interne.

**Processus** :
1. Vérifie si le dossier `Armory` existe, le crée si nécessaire
2. Copie `Data/items_database.json` → `Armory/items_database.json`
3. Met à jour la config : `use_personal_database = True`, `personal_db_created = True`
4. Sauvegarde le chemin et la version de la base dans la config

**Retourne** :
- `(True, path)` en cas de succès
- `(False, error_message)` en cas d'échec

**Utilisation** :
```python
success, result = db_manager.create_personal_database()
if success:
    print(f"Base créée à : {result}")
```

#### 4. `add_scraped_item(item_data: dict) -> bool`
Ajoute un item scrapé à la base de données personnelle.

**Prérequis** :
- Le Mode 2 doit être actif (`use_personal_database = True`)
- Le fichier de base de données personnelle doit exister

**Fonctionnalités** :
- **Déduplication par royaume** : Ajoute uniquement si l'item n'existe pas pour le même royaume
- **Suivi utilisateur** : Définit `user_added = True` dans les métadonnées
- **Sauvegarde automatique** : Écrit dans le fichier immédiatement

**Paramètres** :
- `item_data` : Dictionnaire avec les propriétés de l'item (nom, royaume, type, stats, etc.)

**Retourne** :
- `True` si l'item est ajouté avec succès
- `False` si l'item existe déjà ou si le mode est incorrect

**Utilisation** :
```python
item_data = {
    "name": "Custom Sword",
    "realm": "Albion",
    "type": "Weapon",
    "bonus_stats": {"Strength": 10}
}
success = db_manager.add_scraped_item(item_data)
```

#### 5. `get_statistics() -> dict`
Retourne les statistiques sur les bases de données.

**Retourne** :
```python
{
    "internal_count": 1500,        # Items dans la BDD interne
    "personal_count": 1580,        # Items dans la BDD personnelle (si Mode 2)
    "user_added_count": 80,        # Items ajoutés par l'utilisateur (user_added=True)
    "mode": "personal"             # "internal" ou "personal"
}
```

**Utilisation** :
```python
stats = db_manager.get_statistics()
print(f"Vous avez {stats['user_added_count']} items personnalisés")
```

#### 6. `reset_personal_database() -> bool`
Réinitialise la base de données personnelle vers une copie fraîche de la base interne.

**Processus** :
1. **ATTENTION** : Supprime tous les items ajoutés par l'utilisateur
2. Sauvegarde la base personnelle actuelle (optionnel)
3. Copie base interne → base personnelle
4. Met à jour le suivi de version dans la config

**Retourne** :
- `True` en cas de succès
- `False` en cas d'échec

**Utilisation** :
```python
success = db_manager.reset_personal_database()
```

---

## Schéma de Configuration

### Section Armory
```json
{
  "armory": {
    "use_personal_database": false,
    "personal_db_created": false,
    "personal_db_path": "",
    "auto_add_scraped_items": true,
    "last_internal_db_version": ""
  }
}
```

### Clés de Configuration

| Clé | Type | Défaut | Description |
|-----|------|---------|-------------|
| `use_personal_database` | bool | `false` | Activer le Mode 2 (BDD personnelle) |
| `personal_db_created` | bool | `false` | Flag : BDD personnelle créée au moins une fois |
| `personal_db_path` | str | `""` | Chemin complet vers le fichier de BDD personnelle |
| `auto_add_scraped_items` | bool | `true` | Ajout auto des items scrapés sans prompt |
| `last_internal_db_version` | str | `""` | Suivi de version pour les mises à jour |

---

## Intégration UI

### Dialogue Paramètres - Page Armurerie

#### Configuration Dossier (Toujours Visible)
- **Chemin dossier Armory** : Boutons Parcourir, Déplacer, Ouvrir
- Changements sauvegardés immédiatement dans la config

#### Section Mode Base de Données
- **Case à cocher** : "Activer la base de données personnelle"
  - Décochée = Mode 1 (interne)
  - Cochée = Mode 2 (personnelle)

#### Groupe Statistiques (Visible en Mode 2)
- Items dans la base de données interne
- Items dans la base de données personnelle
- Items ajoutés par l'utilisateur

#### Groupe Actions (Visible en Mode 2)
- Bouton **Réinitialiser la Base** : Restaurer vers la copie interne

#### Section Import (Visible en Mode 2)
- Bouton **Importer des Items** : Ouvrir le dialogue d'import
- Texte d'aide expliquant la fonctionnalité d'import

### Flux d'Activation

**Première activation** :
1. L'utilisateur coche "Activer la base de données personnelle"
2. Le système détecte qu'aucune BDD personnelle n'existe
3. Popup : "Créer la base de données personnelle ? (X items seront copiés)"
4. L'utilisateur clique Oui → base créée
5. L'UI affiche les sections statistiques, actions, import

**Activations suivantes** :
1. L'utilisateur coche "Activer la base de données personnelle"
2. Le système détecte une BDD personnelle existante
3. Le mode change immédiatement
4. L'UI affiche les sections statistiques, actions, import

**Désactivation** :
1. L'utilisateur décoche la case
2. Le système bascule en Mode 1 (BDD interne)
3. Les sections statistiques, actions, import sont masquées
4. Le fichier de BDD personnelle reste intact (peut être réactivé plus tard)

---

## Intégration Auto-Add

### Dialogue Import Armurerie

Quand le scraping se termine et que le Mode 2 est actif :

**Si `auto_add_scraped_items = True`** :
- Items automatiquement ajoutés à la base personnelle
- Aucune interaction utilisateur requise
- Message de succès affiche le nombre

**Si `auto_add_scraped_items = False`** :
- Popup : "Ajouter X items à votre base de données ?"
- Case à cocher : "Toujours ajouter automatiquement"
- L'utilisateur peut :
  - Oui → Ajouter les items + optionnellement activer l'ajout auto
  - Non → Items rejetés (non sauvegardés)

---

## Structure des Données

### Format Item
```json
{
  "name": "Dragon Slayer Sword",
  "realm": "Albion",
  "type": "Two-Handed Weapon",
  "slot": "Two Hand",
  "quality": "Unique",
  "armor_factor": 0,
  "abs": 0,
  "damage": "16.5 DPS",
  "speed": "4.0",
  "bonus_hits": 40,
  "bonus_stats": {
    "Strength": 15,
    "Constitution": 10
  },
  "resists": {
    "Crush": 3,
    "Slash": 3,
    "Thrust": 3
  },
  "skill_bonuses": {
    "Two-Handed": 4
  },
  "focus": null,
  "user_added": false
}
```

### Champs de Métadonnées

| Champ | Type | Description |
|-------|------|-------------|
| `user_added` | bool | `True` si l'item a été ajouté par l'utilisateur (pas depuis la BDD interne) |
| `source` | str | Optionnel : "scraped", "imported", "manual" |
| `date_added` | str | Optionnel : Timestamp ISO |
| `notes` | str | Optionnel : Notes utilisateur |

---

## Migration & Mises à Jour

### Mises à Jour de l'Application

Quand une nouvelle version inclut une base de données interne mise à jour :

1. **Utilisateurs Mode 1** : Utilisent automatiquement la nouvelle BDD interne
2. **Utilisateurs Mode 2** : Gardent leur BDD personnelle inchangée
   - Option de réinitialiser et copier la nouvelle BDD interne
   - Suivi de version dans `last_internal_db_version`

### Détection de Version
```python
current_version = config.get("armory.last_internal_db_version")
internal_version = db_manager.get_internal_db_version()

if current_version != internal_version:
    # Notifier l'utilisateur qu'une mise à jour est disponible
    # Proposer de réinitialiser la BDD personnelle pour obtenir les nouveaux items
```

---

## Gestion des Erreurs

### Échecs de Création de Base
- **Permissions dossier** : Vérifier l'accès en écriture au dossier Armory
- **Espace disque** : Vérifier l'espace suffisant pour la copie
- **Verrous fichiers** : S'assurer qu'aucun autre processus n'utilise la base

### Échecs Import/Ajout
- **JSON invalide** : Valider la structure de l'item avant ajout
- **Détection de doublons** : Vérifier la combinaison royaume + nom
- **Validation schéma** : S'assurer que les champs requis sont présents

### Récupération
- La base personnelle peut toujours être réinitialisée vers la copie interne
- Corruption config : Retour au Mode 1 (interne)
- Corruption fichier : Recréer la base personnelle

---

## Meilleures Pratiques

### Pour les Utilisateurs

**Usage Occasionnel** :
- Rester avec le Mode 1 (base interne)
- Aucune configuration requise, aucune maintenance

**Usage Avancé** :
- Activer le Mode 2 pour le stockage persistant
- Activer l'ajout auto pour la commodité
- Revoir périodiquement les statistiques
- Sauvegarder manuellement la base personnelle (copier le fichier)

### Pour les Développeurs

**Mises à Jour de Base** :
- Incrémenter le numéro de version dans les métadonnées de la base interne
- Documenter les changements dans le changelog
- Tester la migration depuis les versions précédentes

**Développement de Fonctionnalités** :
- Toujours vérifier le mode avant les opérations d'écriture
- Utiliser `get_active_database_path()` pour la cohérence
- Logger toutes les modifications de base
- Fournir un retour utilisateur sur les changements de mode

---

## Dépannage

### Problème : La case à cocher ne reste pas cochée
**Cause** : Le fichier de base personnelle n'existe pas
**Solution** : Supprimer et recréer la base personnelle

### Problème : Les items ne se sauvegardent pas
**Cause** : Mode 1 actif (lecture seule)
**Solution** : Activer le Mode 2 (base personnelle)

### Problème : Les statistiques ne se mettent pas à jour
**Cause** : Config non rechargée après les changements
**Solution** : Fermer et rouvrir le dialogue paramètres

### Problème : Base de données corrompue
**Cause** : L'édition manuelle a introduit des erreurs JSON
**Solution** : Réinitialiser la base personnelle vers la copie interne

---

## Considérations de Performance

### Taille de Base
- BDD Interne : ~1-5 MB (1000-5000 items)
- BDD Personnelle : Croît avec les ajouts utilisateur
- Performance recherche : Recherche linéaire O(n) (acceptable pour <10k items)

### Optimisation
- Utiliser le filtrage par royaume pour réduire l'espace de recherche
- Mettre en cache les items fréquemment consultés
- Envisager l'indexation pour les grandes bases (>10k items)

---

## Sécurité & Confidentialité

### Stockage des Données
- Toutes les bases stockées localement (pas de sync cloud)
- Format JSON brut (pas de chiffrement)
- L'utilisateur est responsable des sauvegardes

### Mode Portable
- Config et bases dans le dossier de l'application
- Aucune dépendance registre/AppData
- Copier le dossier entier pour sauvegarder/transférer

---

## Améliorations Futures

### Fonctionnalités Prévues
- [ ] Outil de fusion de bases (combiner plusieurs BDD personnelles)
- [ ] Import/export de BDD personnelle en ZIP
- [ ] Outil de comparaison d'items (interne vs. personnel)
- [ ] Optimisation de base (supprimer les doublons)
- [ ] Recherche avancée (filtres, tri)
- [ ] Tableau de bord statistiques de base

### En Considération
- [ ] Sync cloud (optionnel, chiffré)
- [ ] Bases collaboratives (partage de guilde)
- [ ] Sauvegardes automatiques avant réinitialisation
- [ ] Compression de base (migration SQLite)

---

## Documentation Associée

- `ARMORY_IMPORT_SYSTEM_FR.md` - Fonctionnalité d'import
- `DATA_MANAGER_FR.md` - Architecture de gestion des données
- `CONFIGURATION_FR.md` - Référence schéma config
- `DATABASE_MANAGER_TECHNICAL_FR.md` - Référence API

---

**Version** : 1.0  
**Dernière Mise à Jour** : 18 novembre 2025  
**Auteur** : Équipe de Développement DAOC Character Manager
