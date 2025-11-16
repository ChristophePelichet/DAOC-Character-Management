# Guide - Changements de Logger en Temps Réel ⚡

## 🎯 Objectif
Permettre de **modifier les configurations des loggers en temps réel** sans redémarrer l'application, en utilisant l'outil **Logger Configuration Editor**.

## 📊 Système de Logging Complet

### Architecture
```
┌─────────────────────────────────────┐
│   Application (main.py)              │
└──────────┬──────────────────────────┘
           │
           ├─ BACKUP Logger ────┐
           ├─ EDEN Logger       ├── get_logger(LOGGER_NAME)
           ├─ UI Logger         │
           ├─ CHARACTER Logger  │
           └─ ROOT Logger ──────┘
                    │
                    ↓
           ┌─────────────────────┐
           │ ContextualFormatter │ ← Formatte les logs
           └─────────────────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │  Console + Files    │ ← Affiche/Sauvegarde
           └─────────────────────┘
           
           │ (en temps réel)
           ↓
┌──────────────────────────────────────┐
│ Logger Configuration Editor (Tool)   │
│ - View: Voir les configs actuelles   │
│ - Edit: Modifier les niveaux         │
│ - Apply: Appliquer en TEMPS RÉEL     │
└──────────────────────────────────────┘
```

### Les 5 Loggers Disponibles

| Logger | Constante | Utilisation | Couleur |
|--------|-----------|-------------|---------|
| **BACKUP** | `LOGGER_BACKUP` | Opérations de sauvegarde | 🟦 Bleu |
| **EDEN** | `LOGGER_EDEN` | Web scraper / API Eden | 🟪 Violet |
| **UI** | `LOGGER_UI` | Interface graphique | 🟨 Orange |
| **CHARACTER** | `LOGGER_CHARACTER` | Gestion des personnages | 🟩 Vert |
| **ROOT** | `LOGGER_ROOT` | Application générale | ⚫ Noir |

## 🚀 Utilisation

### Démarrage

#### Méthode 1 : Via le Menu Principal
1. Lancez `python main.py`
2. Accédez au menu Tools
3. Cliquez sur "Logger Configuration Editor"

#### Méthode 2 : Via le Script de Test
```powershell
cd d:\Projets\Python\DAOC-Character-Management
python Tools/test_logger_editor.py
```

### Interface Principale

L'outil est divisé en 3 sections :

```
┌─────────────────────────────────────────────────────────┐
│  Logger Configuration Editor                            │
├──────────────────┬──────────────────────────────────────┤
│  LEFT PANE       │       RIGHT PANE                     │
│  ┌────────────┐  │  ┌──────────────────────────────┐   │
│  │ Logger     │  │  │ Logger Information Panel     │   │
│  │ List       │  │  │ - Name: BACKUP              │   │
│  │            │  │  │ - Description: ...          │   │
│  │ 🟢 BACKUP  │  │  │ - Level: INFO               │   │
│  │ 🟢 EDEN    │  │  │ - Status: Enabled           │   │
│  │ 🔴 UI      │  │  │ - Handlers: Console, File   │   │
│  │ 🟢 CHAR.   │  │  │                             │   │
│  │ 🟢 ROOT    │  │  ├──────────────────────────────┤   │
│  │            │  │  │ Configuration Form          │   │
│  │            │  │  │ - Name: [BACKUP]            │   │
│  │            │  │  │ - Description: [...]        │   │
│  │            │  │  │ - Level: [INFO ▼]           │   │
│  │            │  │  │ - Enabled: [X] Enabled      │   │
│  │            │  │  │ - Handlers: [Console, File] │   │
│  │            │  │  │ - Notes: [...]              │   │
│  │            │  │  │                             │   │
│  │            │  │  ├──────────────────────────────┤   │
│  │            │  │  │ Changes to Apply            │   │
│  │            │  │  │ ✨ Level: INFO → WARNING    │   │
│  │            │  │  │ ✨ Status: Enabled → Disabled
│  │            │  │  │                             │   │
│  └────────────┘  │  └──────────────────────────────┘   │
├──────────────────┴──────────────────────────────────────┤
│ Buttons:                                                 │
│ [📤 Export] [📥 Import] [🧪 Test Logger] [✅ Apply]     │
└─────────────────────────────────────────────────────────┘
```

### Modifier un Logger (Pas à Pas)

#### Étape 1️⃣ : Sélectionner le Logger
- Cliquez sur le logger dans la liste de gauche
- Exemple: Cliquez sur "BACKUP"
- La section droite affiche sa configuration

#### Étape 2️⃣ : Éditer la Configuration
Dans le formulaire Configuration Form :

**Changer le niveau de log** (plus courant)
- Cliquez sur le dropdown "Level"
- Sélectionnez un nouveau niveau:
  - **DEBUG** : Tous les messages (très verbeux)
  - **INFO** : Messages informatifs (défaut)
  - **WARNING** : Avertissements et erreurs seulement
  - **ERROR** : Erreurs critiques uniquement
  - **CRITICAL** : Problèmes graves uniquement

**Autres modifications possibles**
- Description : Texte libre
- Enabled : Cochez/Décochez pour activer/désactiver
- Notes : Commentaires personnels
- Handlers : Configuration avancée

#### Étape 3️⃣ : Vérifier les Changements
- Section "Changes to Apply" affiche les modifications
- Exemple d'affichage:
  ```
  Changes to Apply:
  ✨ Level: INFO → WARNING
  ✨ Description: [ancienne] → [nouvelle]
  ```

#### Étape 4️⃣ : Appliquer les Changements
- Cliquez sur le bouton **"✅ Apply Changes (Real-Time)"**
- ⚡ **Les changements s'appliquent IMMÉDIATEMENT**
- Une boîte de confirmation apparaît

### ✅ Confirmation

Après clic sur "Apply Changes", vous verrez:

```
┌────────────────────────────────────┐
│ Success                            │
├────────────────────────────────────┤
│ Logger 'BACKUP' updated!           │
│                                    │
│ ✓ Level: WARNING                   │
│ ✓ Status: Enabled                  │
│ ✓ Changes applied in real-time     │
│                                    │
│           [  OK  ]                 │
└────────────────────────────────────┘
```

## 🧪 Script de Test - Démonstration

Le script `Tools/test_logger_editor.py` démontre les changements en temps réel:

### Lancer le Script
```powershell
python Tools/test_logger_editor.py
```

### Ce qu'il fait
1. **Démarre une boucle de logging** (message toutes les 2 secondes)
2. **Affiche des messages** à différents niveaux:
   - DEBUG messages
   - INFO messages  
   - WARNING messages
3. **Permet de tester** en changeant les niveaux dans l'éditeur

### Exemple de Sortie
```
============================================================
🎯 LOGGER CONFIGURATION EDITOR - DEMO
============================================================

📝 Instructions:
1. Open the Logger Configuration Editor window
2. Select a logger (e.g., BACKUP)
3. Change the 'Log Level' (e.g., to WARNING)
4. Click 'Apply Changes' button
5. You'll see logs below change in real-time!

============================================================

📢 DEMO: Logging messages every 2 seconds...
   Try changing logger levels in the editor window!

2025-11-01 11:19:39 - BACKUP - DEBUG - demo_logging - [DEMO 1] BACKUP DEBUG: Detailed backup information
2025-11-01 11:19:39 - BACKUP - INFO - demo_logging - [DEMO 1] BACKUP INFO: Backup operation in progress
2025-11-01 11:19:39 - BACKUP - WARNING - demo_logging - [DEMO 1] BACKUP WARNING: Backup nearly complete
...
```

### Tester les Changements en Temps Réel
1. **Script de test en cours d'exécution** → les logs s'affichent
2. **Ouvrir Logger Configuration Editor**
3. **Sélectionner BACKUP logger**
4. **Changer le niveau** : INFO → WARNING
5. **Cliquer "Apply Changes"**
6. **Résultat** : Les messages DEBUG et INFO disparaissent immédiatement ! ✨

## 🔍 Exemple Complet

### Scénario : Réduire le Bruit des Logs EDEN

**Problème** : Eden scraper produit trop de messages DEBUG

**Solution** :

```
1. Ouvrir Logger Configuration Editor
   ↓
2. Cliquer sur "EDEN" dans la liste
   ↓
3. Dans le formulaire, changer "Level: DEBUG" → "Level: WARNING"
   ↓
4. Section "Changes to Apply" affiche:
   ✨ Level: DEBUG → WARNING
   ↓
5. Cliquer "✅ Apply Changes (Real-Time)"
   ↓
6. ✅ IMMÉDIATE: Plus de DEBUG du scraper, seulement WARNING+
```

**Résultat**:
- Avant : Console inondée de messages DEBUG
- Après : Console plus claire, only important messages

## 📋 Niveaux de Log Expliqués

### DEBUG (Niveau 10)
```
✅ Affiche: DEBUG, INFO, WARNING, ERROR, CRITICAL
❌ Masque: (rien)
📝 Usage: Debugging intensif, développement
```

### INFO (Niveau 20) ⭐ Par Défaut
```
✅ Affiche: INFO, WARNING, ERROR, CRITICAL
❌ Masque: DEBUG
📝 Usage: Opérations normales, informations utiles
```

### WARNING (Niveau 30)
```
✅ Affiche: WARNING, ERROR, CRITICAL
❌ Masque: DEBUG, INFO
📝 Usage: Production, alertes importantes
```

### ERROR (Niveau 40)
```
✅ Affiche: ERROR, CRITICAL
❌ Masque: DEBUG, INFO, WARNING
📝 Usage: Erreurs graves uniquement
```

### CRITICAL (Niveau 50)
```
✅ Affiche: CRITICAL
❌ Masque: DEBUG, INFO, WARNING, ERROR
📝 Usage: Situations extrêmes
```

## 🎨 Codage Couleur

### Liste des Loggers

| État | Couleur | Signification |
|------|---------|---------------|
| 🟢 | Vert clair | Logger **ACTIVÉ** et fonctionnel |
| 🔴 | Rouge clair | Logger **DÉSACTIVÉ** |
| ⚫ | Noir | ROOT logger (spécial) |

### Icônes d'Interface

| Icône | Signification |
|------|---------------|
| ✨ | Champ modifié, à appliquer |
| ✅ | Changement appliqué avec succès |
| 🧪 | Test du logger |
| 📤 | Exporter configuration |
| 📥 | Importer configuration |

## ⚠️ Cas d'Usage Courants

### 1. Application Trop Bavarde
```
Niveau actuel: DEBUG
Bruit: Beaucoup de messages DEBUG
Solution: Changer à INFO ou WARNING
```

### 2. Pas Assez d'Informations
```
Niveau actuel: WARNING
Bruit: Pas d'informations de progression
Solution: Changer à DEBUG ou INFO
```

### 3. Désactiver un Logger
```
Logger en cours: BACKUP
Solution: Décocher "Enabled" et appliquer
Effet: Cet logger n'émettra plus de messages
```

### 4. Re-activer un Logger
```
Logger désactivé: UI
Solution: Cocher "Enabled" et appliquer
Effet: Le logger reprend ses logs
```

## 🔧 Configuration Avancée

### Exporter la Configuration
```
1. Cliquer "📤 Export"
2. Choisir un fichier .json
3. Toutes les configurations sont sauvegardées
```

### Importer une Configuration
```
1. Cliquer "📥 Import"
2. Sélectionner un fichier .json
3. Les configurations sont restaurées
```

### Tester un Logger Spécifique
```
1. Sélectionner le logger
2. Cliquer "🧪 Test Logger"
3. Fenêtre de test affiche exemple de sortie
```

## 💾 Synchronisation avec le Code

Quand vous appliquez un changement :

```
┌─────────────────────────────────────────┐
│ Logger Configuration Editor             │
│ Change: BACKUP Level INFO → WARNING     │
└────────────────┬────────────────────────┘
                 │
                 ↓ logging.getLogger('backup')
          
┌─────────────────────────────────────────┐
│ Système de Logging (Python)             │
│ logger.setLevel(logging.WARNING)         │
└────────────────┬────────────────────────┘
                 │
                 ↓ Tous les loggers qui utilisent get_logger(LOGGER_BACKUP)
                   
┌─────────────────────────────────────────┐
│ Logs dans backup_manager.py, etc.       │
│ logger.debug(...) ← ❌ Masqué            │
│ logger.info(...) ← ❌ Masqué             │
│ logger.warning(...) ← ✅ Affiché        │
└─────────────────────────────────────────┘
```

## ✨ Points Clés à Retenir

✅ **Les changements s'appliquent immédiatement** - Pas besoin de redémarrer
✅ **Affichage en temps réel** - Voir l'effet sur les logs dans la console
✅ **Noms de loggers en MAJUSCULES** - BACKUP, EDEN, UI, CHARACTER, ROOT
✅ **Format de log uniforme** - Date - Heure - Logger - Level - Fonction - Action - Texte
✅ **Aperçu des changements** - Section "Changes to Apply" avant d'appliquer
✅ **Confirmation immédiate** - Boîte de dialogue confirmant l'application

## 📞 Aide Rapide

### Q: Les changements persistent-ils après redémarrage ?
A: Non, les changements en temps réel ne persistent que pendant la session. Pour les conserver, utilisez Export/Import.

### Q: Puis-je modifier les loggers système (ROOT, etc.) ?
A: Oui, mais avec prudence. Ils contrôlent l'ensemble du système de logging.

### Q: Qu'est-ce que "Handlers" ?
A: Les destinations des logs (console pour affichage, files pour sauvegarde).

### Q: Comment annuler un changement ?
A: Changez le niveau de nouveau et appliquez, ou relancez l'application.

## 🎯 Résumé

Vous avez maintenant un **outil professionnel de gestion de logs** qui vous permet:

1. 👁️ **Voir** les configurations actuelles en temps réel
2. ✏️ **Éditer** les niveaux et paramètres
3. 📊 **Prévisualiser** les changements avant application
4. ⚡ **Appliquer** immédiatement sans redémarrer
5. 💾 **Importer/Exporter** les configurations

**Utilisez-le pour déboguer et optimiser votre application !** 🚀
