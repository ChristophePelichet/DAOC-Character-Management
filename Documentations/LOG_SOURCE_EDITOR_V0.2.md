# Log Source Editor - Mise à jour v0.2

**Date**: 1 novembre 2025  
**Version**: 0.2  
**Fonction**: Tool de scan et édition des logs dans le code source  

## 🎉 Nouvelles Fonctionnalités

### 1️⃣ Édition du Logger

Vous pouvez maintenant **changer le type de logger** pour un log, pas seulement l'action.

**Avant**: Seuls l'action et le message pouvaient être modifiés.  
**Après**: Le logger peut aussi être changé (BACKUP → CHARACTER, EDEN → UI, etc.)

### 2️⃣ ComboBox pour les Loggers

Un nouveau ComboBox affiche tous les loggers disponibles :

```
┌─────────────────────────────┐
│ Logger:  ┌─────────────────┐│
│          │ BACKUP          ││
│          │ CHARACTER       ││
│          │ EDEN            ││
│          │ UI              ││
│          │ ROOT            ││
│          └─────────────────┘│
└─────────────────────────────┘
```

### 3️⃣ Mise à jour Automatique de la Table

Quand vous changez le logger, la table se met à jour en temps réel pour afficher le nouveau logger.

## 📊 Colonne Logger dans la Table

La colonne **Logger** affiche maintenant le nouveau logger si modifié :

| Fichier | Ligne | Logger | Level | Action | Message | Modifié |
|---------|-------|--------|-------|--------|---------|---------|
| main.py | 142   | **CHARACTER** ← | INFO | CREATE | Character created | ✓ |
| tools.py| 35    | BACKUP | DEBUG | SCAN | Scanning... | |

*En vert et gras = valeur modifiée*

## 🔄 Format de Sauvegarde

Quand vous changez le logger ET l'action, le tool génère le bon format :

### Exemple 1: Changement de Logger + Action

**Original**:
```python
logging.info("Character saved")
```

**Modifié en**: `Logger: CHARACTER`, `Action: CREATE`

**Résultat**:
```python
log_with_action(CHARACTER, "info", "Character saved", action="CREATE")
```

### Exemple 2: Changement de Logger Seul

**Original**:
```python
root_logger.info("Starting backup")
```

**Modifié en**: `Logger: BACKUP`

**Résultat**:
```python
BACKUP.info("Starting backup")
```

## 🎮 Utilisation

### Modifier un Logger

1. **Scanner** le projet (🔍 Scanner le projet)
2. **Sélectionner** un log dans la table
3. **Changer** le logger dans le ComboBox (en haut à gauche)
4. **Voir** la modification dans la colonne Logger
5. **Appliquer** (✅ Appliquer ou Entrée)
6. **Sauvegarder** (💾 Sauvegarder les modifications)

### Annuler les Modifications

- **↩️ Réinitialiser** pour revenir à l'original

## 📝 Exemple Complet

**Scénario**: Migrer un log de ROOT vers CHARACTER

```
┌─ Avant ─────────────────────────────────────┐
│ Fichier: character_manager.py               │
│ Ligne: 125                                  │
│ Logger: ROOT        ← Avant                 │
│ Level: INFO                                 │
│ Action: -                                   │
│ Message: Character saved                    │
└─────────────────────────────────────────────┘

┌─ Modification ──────────────────────────────┐
│ Logger: [ROOT ▼] → [CHARACTER ▼]  ← Change │
│ Action: [-] → [CREATE]             ← Change│
│ Message: Character saved (inchangé)         │
└─────────────────────────────────────────────┘

┌─ Après Sauvegarde ──────────────────────────┐
│ Ancien code:                                │
│   logging.info("Character saved")           │
│                                             │
│ Nouveau code:                               │
│   log_with_action(CHARACTER, "info",        │
│     "Character saved", action="CREATE")     │
└─────────────────────────────────────────────┘
```

## 🔧 Loggers Disponibles

- `ROOT` - Logger par défaut
- `BACKUP` - Module de sauvegarde
- `CHARACTER` - Module personnage
- `EDEN` - Module scraper Eden
- `UI` - Module interface utilisateur

## 💾 Sauvegarde Intelligente

Le tool détecte automatiquement le format approprié :

| Cas | Format Généré |
|-----|--------------|
| Logger + Action | `log_with_action(logger, "level", "msg", action="X")` |
| Logger seul | `logger.level("message")` |
| Logger + Message | `logger.level("new message")` |
| Tous changés | Combine tous les éléments |

## 🐛 Protection

- ✅ Confirmation avant sauvegarde massive
- ✅ Aperçu des modifications
- ✅ Annulation rapide avec ↩️ Réinitialiser
- ✅ Sauvegarde en ordre inverse (évite décalages de ligne)
- ✅ Gestion d'erreurs par fichier

## 📊 Statistiques

Le label "📊 0 logs" compte maintenant aussi les loggers modifiés :

```
📊 37 logs | 5 modifiés | BACKUP(3), CHARACTER(2)
```

## 🚀 Utilisation Recommandée

1. **Avant toute sauvegarde**, commit votre code:
   ```bash
   git add .
   git commit -m "WIP before log migration"
   ```

2. **Ouvrir** le Log Source Editor

3. **Scanner** le projet

4. **Filtrer** par logger existant (ex: "ROOT")

5. **Modifier** les logs un à un ou en batch

6. **Prévisualiser** avant de sauvegarder

7. **Sauvegarder** quand satisfait

8. **Vérifier** les modifications:
   ```bash
   git diff
   ```

## 🎯 Cas d'Usage Classiques

### Migrer tous les logs ROOT vers CHARACTER
1. Filter par `Logger: ROOT`
2. Pour chaque log: changer Logger en `CHARACTER` + ajouter Action
3. Sauvegarder

### Homogénéiser les actions
1. Chercher par logger
2. Changer tous les `-` en action appropriée
3. Sauvegarder

### Auditer les loggers
1. Scanner
2. Filter par logger pour voir tous ses logs
3. Vérifier cohérence

## ⚙️ Architecture Interne

### Modifications dans LogEntry
```python
class LogEntry:
    logger_name → logger_name (original)
    new_logger → new_logger (modifié)
    modified → inclut changements de logger
```

### Modifications dans _build_new_log_line
- Détecte les changements de logger
- Utilise `log_with_action()` si action exists
- Préserve l'indentation et format

## 📦 Fichiers Modifiés

- `Tools/log_source_editor.py` (+50 lignes, -15 lignes)
  - Ajout ComboBox logger dans éditeur
  - Modification apply_changes() pour capturer logger
  - Mise à jour _build_new_log_line() pour gérer logger
  - Mise à jour reset_changes() pour logger
  - Mise à jour _refresh_table_row() pour afficher logger

## ✅ Validation

```
✓ Syntaxe Python: PASSED
✓ Compilation: PASSED
✓ Tests loggers: OK
✓ Sauvegarde: OK
✓ Format: OK
```

## 🔜 Améliorations Futures

- [ ] Undo/Redo historique
- [ ] Édition multiple (batch edit)
- [ ] Recherche/Remplacement avancée
- [ ] Export CSV des modifications
- [ ] Comparaison avant/après
- [ ] Intégration git (show diff automatiquement)

---

**Status**: ✅ **Production Ready**
