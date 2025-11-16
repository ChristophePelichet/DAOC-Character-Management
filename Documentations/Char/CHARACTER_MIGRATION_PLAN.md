# Plan de Migration Automatique des Fichiers de Personnages

## 📋 Vue d'ensemble

Créer un système de migration automatique transparent pour les fichiers de personnages `.json`, similaire aux systèmes existants pour `config.json` et `Language/*.json`.

**Objectif** : Migration automatique de la structure ancienne vers nouvelle structure avec saisons, **sans interaction utilisateur**.

---

## 🎯 Principes Clés (Inspirés de config.json / Language.json)

1. ✅ **Transparence totale** - Aucune confirmation demandée à l'utilisateur
2. ✅ **Backup automatique** - Sauvegarde timestampée avant toute migration
3. ✅ **Validation stricte** - Vérification JSON avant/après
4. ✅ **Rollback automatique** - Restauration si erreur détectée
5. ✅ **Flag de migration** - Fichier `.migration_done` pour éviter re-migration
6. ✅ **Logging complet** - Traçabilité de toutes les opérations

---

## 📂 Structures Cibles

### Ancienne Structure (Pre-Migration)
```
Characters/
  ├─ Albion/
  │   ├─ character1.json
  │   └─ character2.json
  ├─ Hibernia/
  │   └─ character3.json
  └─ Midgard/
      └─ character4.json
```

### Nouvelle Structure (Post-Migration)
```
Characters/
  ├─ S1/
  │   ├─ Albion/
  │   ├─ Hibernia/
  │   └─ Midgard/
  ├─ S3/  (saison actuelle)
  │   ├─ Albion/
  │   │   ├─ character1.json
  │   │   └─ character2.json
  │   ├─ Hibernia/
  │   │   └─ character3.json
  │   └─ Midgard/
  │       └─ character4.json
  └─ .migration_done  (flag)
```

---

## 📝 Liste des Tâches

### Phase 1 : Architecture et Schéma

#### Tâche 1.1 : Créer `Functions/character_schema.py`
**Objectif** : Définir la structure attendue des fichiers de personnages

**Contenu** :
- [ ] Fonction `get_character_schema()` - Structure JSON complète avec tous les champs
- [ ] Dictionnaire `REQUIRED_FIELDS` - Champs obligatoires (name, realm, class, race, level, season, server)
- [ ] Dictionnaire `OPTIONAL_FIELDS` - Champs optionnels avec valeurs par défaut
- [ ] Dictionnaire `FIELD_TYPES` - Types attendus pour validation (str, int, dict, list)
- [ ] Fonction `validate_character_data(data)` - Validation de structure JSON
- [ ] Fonction `get_default_season()` - Retourne la saison par défaut ("S3" actuellement)
- [ ] Documentation complète des champs avec exemples

**Champs à gérer** :
```python
REQUIRED_FIELDS = {
    "name": str,
    "realm": str,  # Albion, Hibernia, Midgard
    "class": str,
    "race": str,
    "level": int,
    "season": str,  # S1, S2, S3, etc.
    "server": str   # Eden
}

OPTIONAL_FIELDS = {
    "id": "",
    "page": 1,
    "guild": "",
    "realm_rank": "",
    "realm_title": "",
    "realm_points": 0,
    "url": "",
    "created_date": "",
    "modified_date": "",
    "armor": {},
    "stats": {},
    "achievements": []
}
```

#### Tâche 1.2 : Créer `Functions/character_migration.py`
**Objectif** : Logique de migration automatique des fichiers de personnages

**Fonctions principales** :
- [ ] `detect_old_structure()` - Détecte si ancienne structure existe
- [ ] `backup_characters()` - Crée backup .zip avec timestamp
- [ ] `validate_backup()` - Vérifie intégrité du backup (testzip)
- [ ] `migrate_character_file(old_path, char_data)` - Migre un fichier individuel
- [ ] `migrate_all_characters()` - Migration complète avec rollback
- [ ] `mark_migration_done()` - Crée fichier flag
- [ ] `is_migration_done()` - Vérifie si déjà migré
- [ ] `rollback_migration(migrated_files)` - Restauration en cas d'erreur

**Sécurités** :
- Validation JSON avant migration
- Copie avec vérification de contenu identique
- Tracking de tous les fichiers migrés pour rollback
- Suppression anciens fichiers UNIQUEMENT si 100% succès
- Logging détaillé de chaque opération

#### Tâche 1.3 : Modifier `Functions/character_manager.py`
**Objectif** : Intégrer la migration automatique au démarrage

**Modifications** :
- [ ] Import de `character_migration.py`
- [ ] Fonction `run_migration_at_startup()` appelée au démarrage de CharacterManager
- [ ] Détection automatique si migration nécessaire
- [ ] Exécution silencieuse de la migration (pas de popup)
- [ ] Logging des résultats dans console/fichier log
- [ ] Gestion des erreurs avec message utilisateur minimal

**Workflow** :
```python
def __init__(self):
    # ... existing code ...
    
    # Automatic character migration (silent)
    self._run_character_migration()
    
def _run_character_migration(self):
    """Run character migration automatically if needed"""
    if not is_migration_done():
        if detect_old_structure():
            success, message = migrate_all_characters()
            if success:
                logger.info("Character migration completed successfully")
            else:
                logger.error(f"Character migration failed: {message}")
```

---

### Phase 2 : Backup et Sécurité

#### Tâche 2.1 : Système de Backup Robuste
**Objectif** : Backup automatique avant migration avec vérification

**Implémentation** :
- [ ] Création dossier `Backup/Characters/` si inexistant
- [ ] Nom de fichier : `Characters_migration_backup_YYYYMMDD_HHMMSS.zip`
- [ ] Compression ZIP_DEFLATED pour gain d'espace
- [ ] Inclusion de TOUS les fichiers .json de Characters/
- [ ] Vérification intégrité avec `zipfile.testzip()`
- [ ] Validation du nombre de fichiers (zip vs source)
- [ ] Calcul taille backup et espace disque disponible
- [ ] Logging détaillé de chaque fichier ajouté

**Exemple** :
```python
def backup_characters():
    """Create timestamped ZIP backup of all character files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"Backup/Characters/Characters_migration_backup_{timestamp}.zip"
    
    files_added = 0
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(get_character_dir()):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, get_character_dir())
                    zipf.write(file_path, arcname)
                    files_added += 1
    
    # Verify backup integrity
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        bad_file = zipf.testzip()
        if bad_file:
            os.remove(backup_path)
            raise Exception(f"Backup corrupted: {bad_file}")
    
    return backup_path, files_added
```

#### Tâche 2.2 : Rollback Automatique
**Objectif** : Restauration complète en cas d'erreur

**Implémentation** :
- [ ] Tracking de tous les fichiers migrés : `[(old_path, new_path), ...]`
- [ ] En cas d'erreur : suppression de TOUS les nouveaux fichiers
- [ ] Conservation des anciens fichiers jusqu'à succès total
- [ ] Logging de chaque opération de rollback
- [ ] Message utilisateur clair si rollback effectué

**Exemple** :
```python
def rollback_migration(migrated_files):
    """Remove all migrated files and keep originals"""
    rollback_count = 0
    for old_path, new_path in migrated_files:
        try:
            if os.path.exists(new_path):
                os.remove(new_path)
                rollback_count += 1
                logger.info(f"Rolled back: {new_path}")
        except Exception as e:
            logger.error(f"Rollback failed for {new_path}: {e}")
    
    logger.info(f"Rollback: {rollback_count}/{len(migrated_files)} files removed")
    return rollback_count
```

---

### Phase 3 : Migration Intelligente

#### Tâche 3.1 : Détection de Saison
**Objectif** : Déterminer la saison pour chaque personnage

**Logique** :
- [ ] Si champ `season` existe dans JSON → utiliser cette valeur
- [ ] Si champ `season` manquant → utiliser saison par défaut (S3)
- [ ] Si champ `season` invalide (vide, null) → S3
- [ ] Validation : season doit matcher pattern `S\d+` (S1, S2, S3, etc.)
- [ ] Logging des personnages sans saison détectée

**Exemple** :
```python
def detect_season(char_data):
    """Detect character season with fallback to default"""
    season = char_data.get('season', '').strip()
    
    if not season:
        logger.warning(f"Character {char_data.get('name', 'Unknown')} has no season, defaulting to S3")
        return get_default_season()  # Returns "S3"
    
    if not re.match(r'^S\d+$', season):
        logger.warning(f"Invalid season format '{season}', defaulting to S3")
        return get_default_season()
    
    return season
```

#### Tâche 3.2 : Migration par Fichier
**Objectif** : Migrer chaque fichier individuellement avec validation

**Étapes** :
- [ ] Lecture du fichier JSON source
- [ ] Validation JSON (syntaxe correcte)
- [ ] Validation de structure (champs requis présents)
- [ ] Détection de la saison
- [ ] Création du dossier cible : `Characters/Season/Realm/`
- [ ] Vérification que fichier cible n'existe pas déjà
- [ ] Copie du fichier avec `shutil.copy2` (préserve metadata)
- [ ] Vérification que copie est identique (lecture + comparaison)
- [ ] Ajout à la liste de tracking pour rollback potentiel

**Exemple** :
```python
def migrate_character_file(old_path, char_data):
    """Migrate single character file with validation"""
    # Validate required fields
    for field in REQUIRED_FIELDS:
        if field not in char_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Detect season
    season = detect_season(char_data)
    realm = char_data['realm']
    filename = os.path.basename(old_path)
    
    # Create target directory
    target_dir = os.path.join(get_character_dir(), season, realm)
    os.makedirs(target_dir, exist_ok=True)
    
    # Target file path
    new_path = os.path.join(target_dir, filename)
    
    # Check if already exists
    if os.path.exists(new_path):
        raise FileExistsError(f"Target already exists: {new_path}")
    
    # Copy file
    shutil.copy2(old_path, new_path)
    
    # Verify copy
    with open(new_path, 'r', encoding='utf-8') as f:
        verify_data = json.load(f)
    
    if verify_data != char_data:
        os.remove(new_path)
        raise Exception("Copied file doesn't match original")
    
    logger.info(f"Migrated: {filename} → {season}/{realm}/")
    return new_path
```

#### Tâche 3.3 : Migration Complète
**Objectif** : Orchestrer la migration de tous les personnages

**Processus** :
- [ ] Vérifier si migration déjà effectuée (flag `.migration_done`)
- [ ] Détecter si ancienne structure existe
- [ ] Créer backup automatique
- [ ] Valider backup
- [ ] Pour chaque Realm (Albion, Hibernia, Midgard) :
  - [ ] Lister tous les fichiers .json
  - [ ] Migrer chaque fichier avec tracking
  - [ ] Comptabiliser succès/erreurs
- [ ] Si AUCUNE erreur :
  - [ ] Supprimer les anciens fichiers
  - [ ] Supprimer les anciens dossiers Realm si vides
  - [ ] Créer fichier `.migration_done`
- [ ] Si erreurs détectées :
  - [ ] Rollback complet (supprimer nouveaux fichiers)
  - [ ] Conserver anciens fichiers
  - [ ] Logger les erreurs détaillées
- [ ] Retourner statistiques (total, migrés, erreurs, par saison)

**Exemple** :
```python
def migrate_all_characters():
    """Migrate all character files with automatic rollback on error"""
    # Check if already done
    if is_migration_done():
        return True, "Migration already completed"
    
    # Check if needed
    if not detect_old_structure():
        return True, "No migration needed"
    
    # Create backup
    backup_path, backup_count = backup_characters()
    logger.info(f"Backup created: {backup_path} ({backup_count} files)")
    
    # Track all migrations for rollback
    migrated_files = []
    stats = {"total": 0, "migrated": 0, "errors": 0, "by_season": {}}
    
    try:
        for realm in ["Albion", "Hibernia", "Midgard"]:
            old_realm_dir = os.path.join(get_character_dir(), realm)
            if not os.path.exists(old_realm_dir):
                continue
            
            json_files = [f for f in os.listdir(old_realm_dir) if f.endswith('.json')]
            stats["total"] += len(json_files)
            
            for json_file in json_files:
                old_path = os.path.join(old_realm_dir, json_file)
                try:
                    with open(old_path, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                    
                    new_path = migrate_character_file(old_path, char_data)
                    migrated_files.append((old_path, new_path))
                    
                    season = detect_season(char_data)
                    stats["migrated"] += 1
                    stats["by_season"][season] = stats["by_season"].get(season, 0) + 1
                    
                except Exception as e:
                    logger.error(f"Error migrating {json_file}: {e}")
                    stats["errors"] += 1
        
        # Check if all successful
        if stats["errors"] == 0:
            # Remove old files
            for old_path, new_path in migrated_files:
                os.remove(old_path)
            
            # Remove empty old realm folders
            for realm in ["Albion", "Hibernia", "Midgard"]:
                realm_dir = os.path.join(get_character_dir(), realm)
                if os.path.exists(realm_dir) and not os.listdir(realm_dir):
                    os.rmdir(realm_dir)
            
            # Mark as done
            mark_migration_done()
            
            message = f"Migration successful: {stats['migrated']} character(s) migrated"
            logger.info(message)
            return True, message
        
        else:
            # Rollback
            logger.error(f"Migration failed with {stats['errors']} error(s), performing rollback")
            rollback_migration(migrated_files)
            return False, f"Migration failed: {stats['errors']} error(s). Rollback completed."
    
    except Exception as e:
        logger.error(f"Critical migration error: {e}")
        rollback_migration(migrated_files)
        return False, f"Critical error: {e}. Rollback completed."
```

---

### Phase 4 : Intégration et Tests

#### Tâche 4.1 : Intégration au Démarrage
**Objectif** : Migration automatique transparente au lancement

**Points d'intégration** :
- [ ] `main.py` - Appel de migration avant initialisation UI
- [ ] `Functions/character_manager.py` - Méthode `__init__` ou `initialize()`
- [ ] Logging dans console Python (print + logger)
- [ ] Pas de popup ou confirmation utilisateur
- [ ] Message discret dans log si migration effectuée

**Exemple main.py** :
```python
# Before UI creation
from Functions.character_migration import run_migration_at_startup

# Run character migration silently
migration_needed, success, message = run_migration_at_startup()
if migration_needed:
    if success:
        logger.info(f"✓ Character migration completed: {message}")
    else:
        logger.error(f"✗ Character migration failed: {message}")
```

#### Tâche 4.2 : Tests Unitaires
**Objectif** : Valider toutes les fonctions de migration

**Fichier** : `Scripts/test_character_migration.py`

**Tests à créer** :
- [ ] `test_detect_old_structure()` - Détection ancienne structure
- [ ] `test_backup_creation()` - Création backup ZIP
- [ ] `test_backup_integrity()` - Vérification intégrité
- [ ] `test_detect_season()` - Détection saison avec fallback
- [ ] `test_migrate_single_file()` - Migration fichier individuel
- [ ] `test_migrate_all_success()` - Migration complète succès
- [ ] `test_migrate_with_errors()` - Migration avec erreurs + rollback
- [ ] `test_migration_flag()` - Création et vérification flag
- [ ] `test_validate_character_data()` - Validation structure JSON

**Exemple de test** :
```python
def test_migrate_single_file():
    """Test migration of a single character file"""
    # Create test character
    char_data = {
        "name": "TestChar",
        "realm": "Albion",
        "class": "Paladin",
        "race": "Briton",
        "level": 50,
        "season": "S3",
        "server": "Eden"
    }
    
    # Create old structure
    old_dir = "test_characters/Albion"
    os.makedirs(old_dir, exist_ok=True)
    old_path = os.path.join(old_dir, "TestChar.json")
    
    with open(old_path, 'w') as f:
        json.dump(char_data, f)
    
    # Migrate
    new_path = migrate_character_file(old_path, char_data)
    
    # Verify new location
    assert os.path.exists(new_path)
    assert "S3/Albion/TestChar.json" in new_path
    
    # Verify content identical
    with open(new_path, 'r') as f:
        migrated_data = json.load(f)
    
    assert migrated_data == char_data
    
    # Cleanup
    shutil.rmtree("test_characters")
```

#### Tâche 4.3 : Tests d'Intégration
**Objectif** : Tester le workflow complet

**Scénarios de test** :
- [ ] Scénario 1 : Migration réussie (10 personnages, 0 erreur)
- [ ] Scénario 2 : Migration partielle (10 personnages, 2 erreurs, rollback)
- [ ] Scénario 3 : Fichier JSON corrompu (détection + skip)
- [ ] Scénario 4 : Espace disque insuffisant (détection + arrêt)
- [ ] Scénario 5 : Migration déjà effectuée (skip avec flag)
- [ ] Scénario 6 : Personnages sans champ season (S3 par défaut)
- [ ] Scénario 7 : Personnages multi-saisons (S1, S2, S3 mélangés)

---

### Phase 5 : Documentation

#### Tâche 5.1 : Documentation Technique
**Fichier** : `Documentations/Char/CHARACTER_MIGRATION_TECHNICAL.md`

**Contenu** :
- [ ] Architecture du système de migration
- [ ] Diagramme de flux de migration
- [ ] Description de chaque fonction
- [ ] Structure des fichiers avant/après
- [ ] Schéma JSON des personnages
- [ ] Processus de rollback
- [ ] Logging et traçabilité
- [ ] Exemples de code

#### Tâche 5.2 : Documentation Utilisateur
**Fichier** : `Documentations/Char/CHARACTER_MIGRATION_USER_GUIDE.md`

**Contenu** :
- [ ] Qu'est-ce que la migration ?
- [ ] Quand est-elle déclenchée ?
- [ ] Que se passe-t-il pendant la migration ?
- [ ] Où sont stockés les backups ?
- [ ] Comment restaurer manuellement un backup ?
- [ ] Que faire en cas d'erreur ?
- [ ] FAQ

#### Tâche 5.3 : Mise à Jour Changelog
**Fichiers** : `Changelogs/CHANGELOG_FR.md`, `CHANGELOG_EN.md`, `CHANGELOG_SIMPLE_FR.md`, `CHANGELOG_SIMPLE_EN.md`

**Entrées à ajouter** :
- [ ] Section 🎉 Ajout : "Migration automatique des fichiers de personnages"
- [ ] Description du système de backup/rollback
- [ ] Transparence pour l'utilisateur
- [ ] Saisons automatiques

---

## 🔍 Points de Vérification

### Checklist de Sécurité
- [ ] Backup créé AVANT toute modification
- [ ] Validation JSON stricte (syntaxe + structure)
- [ ] Rollback automatique en cas d'erreur
- [ ] Aucune suppression de fichiers jusqu'à succès total
- [ ] Logging complet de toutes opérations
- [ ] Flag `.migration_done` uniquement si 0 erreur

### Checklist de Transparence
- [ ] Aucune popup ou confirmation demandée
- [ ] Migration silencieuse au démarrage
- [ ] Logging dans console pour debugging
- [ ] Message utilisateur minimal (seulement si erreur critique)
- [ ] Flag empêche re-migration automatique

### Checklist de Compatibilité
- [ ] Supporte personnages avec/sans champ season
- [ ] Gère saisons multiples (S1, S2, S3, etc.)
- [ ] Compatible avec structure actuelle de migration_manager.py
- [ ] Ne casse pas la fonctionnalité existante
- [ ] Rétrocompatible avec anciens fichiers

---

## 📊 Estimation du Temps

| Phase | Tâches | Temps Estimé |
|-------|--------|--------------|
| Phase 1 : Architecture | 3 tâches | 2-3 heures |
| Phase 2 : Backup/Sécurité | 2 tâches | 1-2 heures |
| Phase 3 : Migration | 3 tâches | 2-3 heures |
| Phase 4 : Tests | 3 tâches | 2-3 heures |
| Phase 5 : Documentation | 3 tâches | 1-2 heures |
| **TOTAL** | **14 tâches** | **8-13 heures** |

---

## 🎯 Résultat Attendu

**Expérience Utilisateur** :
- ✅ Lancement de l'application comme d'habitude
- ✅ Migration automatique en arrière-plan (< 1 seconde)
- ✅ Aucune interaction requise
- ✅ Personnages accessibles immédiatement dans nouvelle structure
- ✅ Backup automatique conservé pour sécurité

**Sécurité Garantie** :
- ✅ Backup .zip complet avant migration
- ✅ Validation JSON stricte
- ✅ Rollback automatique si erreur
- ✅ Anciens fichiers conservés jusqu'à succès total
- ✅ Logging complet pour traçabilité

**Compatibilité** :
- ✅ Fonctionne avec/sans champ season dans JSON
- ✅ Saison par défaut (S3) si manquante
- ✅ Multi-saisons supportées (S1, S2, S3, etc.)
- ✅ Structure existante non affectée

---

## 📝 Notes Importantes

1. **Inspiration des Systèmes Existants** :
   - `Functions/config_migration.py` - Modèle pour backup/rollback
   - `Functions/language_migration.py` - Modèle pour migration multi-fichiers
   - `Functions/language_schema.py` - Modèle pour validation de structure

2. **Différences avec Migration Actuelle** :
   - Actuelle : Popup de confirmation + migration manuelle
   - Nouvelle : Automatique + silencieuse + transparente

3. **Rétrocompatibilité** :
   - Le système actuel de migration peut coexister
   - Flag `.migration_done` partagé entre les deux
   - Migration automatique prend le dessus si détectée au démarrage

4. **Testing** :
   - Tester avec 1, 10, 100, 1000 personnages
   - Tester avec fichiers corrompus
   - Tester avec saisons manquantes/invalides
   - Tester rollback sur erreur

---

## ✅ Critères de Succès

- [ ] Migration s'exécute automatiquement au démarrage
- [ ] Aucune interaction utilisateur requise
- [ ] Backup créé avant migration
- [ ] Rollback automatique si erreur
- [ ] Flag `.migration_done` empêche re-migration
- [ ] Logging complet dans fichiers log
- [ ] 100% des personnages migrés avec succès
- [ ] Tests unitaires passent à 100%
- [ ] Documentation complète et claire
- [ ] Changelogs mis à jour

---

**Dernière mise à jour** : 16 novembre 2025  
**Version** : v0.108  
**Statut** : 📋 Planifié
