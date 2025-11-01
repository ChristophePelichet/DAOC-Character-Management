# Guide de Vérification du Système de Sauvegarde v0.106

## Configuration ✅

### Limitation par Nombre Supprimée
- `backup_max_count` a été supprimée
- Seule la limite de **taille en MB** reste active
- Les sauvegardes peuvent être illimitées en nombre

### Sauvegarde Automatique Quotidienne
- Une sauvegarde se fait automatiquement à la **première ouverture du logiciel** si aucune n'a été faite aujourd'hui
- Appelée `startup_backup()` au démarrage
- Nommée avec suffixe `_Startup_Daily`

### Noms Descriptifs des Sauvegardes
- Format: `backup_characters_YYYYMMDD_HHMMSS_REASON.zip`
- Raisons possibles:
  - `Startup_Daily` : Sauvegarde quotidienne au démarrage
  - `Action` : Sauvegarde après création/duplication (auto-backup avec daily limit)
  - `Delete` : Sauvegarde AVANT suppression de personnage (force immédiate, bypass daily limit)
  - `Rename` : Sauvegarde AVANT renommage de personnage (force immédiate, bypass daily limit)
  - `Update` : Sauvegarde après modification de personnage existant (force immédiate, bypass daily limit)
  - `Manual` : Sauvegarde manuelle depuis le dialog (force immédiate, bypass daily limit)

---

## Actions et Logs Attendus

### 0. DÉMARRAGE DE L'APPLICATION
**Action:** Lancer le programme  
**Logs attendus:**
```
[BACKUP] BackupManager initialized - Backup directory: D:\...\Backup\Characters
[APP_STARTUP] Checking for daily backup...
[BACKUP] Startup: Performing daily backup on application start...
[BACKUP] AUTO-DAILY - Creating compressed backup: backup_characters_20251101_143022_Startup_Daily.zip
[BACKUP] AUTO-DAILY - Applying retention policies...
[BACKUP] AUTO-DAILY - SUCCESS: Backup created: backup_characters_20251101_143022_Startup_Daily.zip
[APP_STARTUP] Daily backup completed: Backup created: ...
```

### 1. CRÉATION DE PERSONNAGE
**Action:** Créer un nouveau personnage  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: CREATE character - Attempting backup...
[BACKUP] AUTO-BACKUP triggered - Checking daily limit...
[BACKUP] AUTO-BACKUP blocked - Backup already done today - skipped
```
(ou SUCCESS si première action du jour)

**Nom fichier:** `backup_characters_20251101_143025_Action.zip`

### 2. SUPPRESSION DE PERSONNAGE ⚠️
**Action:** Supprimer un personnage existant  
**IMPORTANT:** Sauvegarde AVANT suppression  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: DELETE character (BEFORE) - Creating backup...
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143030_Delete.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: ...
```

**Nom fichier:** `backup_characters_20251101_143030_Delete.zip`

### 3. RENOMMAGE DE PERSONNAGE ⚠️
**Action:** Renommer un personnage  
**IMPORTANT:** Sauvegarde AVANT renommage  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: RENAME character (BEFORE) - Creating backup...
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143035_Rename.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: ...
```

**Nom fichier:** `backup_characters_20251101_143035_Rename.zip`

### 4. DUPLICATION DE PERSONNAGE
**Action:** Dupliquer un personnage  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: DUPLICATE character - Attempting backup...
[BACKUP] AUTO-BACKUP triggered - Checking daily limit...
[BACKUP] AUTO-BACKUP blocked - Backup already done today - skipped
```
(ou SUCCESS si première action du jour)

### 5. MISE À JOUR HERALD
**Action:** Cliquer sur "Mettre à jour depuis Herald" et confirmer les changements  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: CHARACTER UPDATE - Backup with reason=Update
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143040_Update.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: ...
```

**Nom fichier:** `backup_characters_20251101_143040_Update.zip`

### 6. MODIFICATION DE PERSONNAGE EXISTANT (Rang, Infos, Armure, Compétences)
**Action:** Modifier un personnage existant (ex: changer le rang, les infos générales, l'armure, les compétences)  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank/Basic Info/Skills/Armor) - Backup with reason=Update
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: ...
```

**Nom fichier:** `backup_characters_20251101_143045_Update.zip`

### 7. IMPORT/MISE À JOUR MASSIVE
**Action:** Importer plusieurs personnages (certains nouveaux, d'autres mises à jour)  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: CHARACTER IMPORT/UPDATE (Mass) - X created, Y updated - Backup with reason=Update
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143050_Update.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: ...
```

**Nom fichier:** `backup_characters_20251101_143050_Update.zip`

### 8. SAUVEGARDE MANUELLE (Fenêtre Sauvegarde)
**Action:** Cliquer sur bouton "Sauvegarder maintenant"  
**Logs attendus:**
```
[UI_BACKUP] Manual backup button clicked - Starting backup process...
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143100_Manual.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: backup_characters_20251101_143100_Manual.zip
[UI_BACKUP] SUCCESS - Updating display...
[UI_BACKUP] Display updated successfully
```

**Nom fichier:** `backup_characters_20251101_143100_Manual.zip`

---

## Ordre d'Exécution Critique

### DELETE (Suppression)
```
1. [BACKUP] Créer sauvegarde avec raison "Delete"
2. [DELETE] Supprimer le personnage
3. [REFRESH] Actualiser l'affichage
```

### RENAME (Renommage)
```
1. [BACKUP] Créer sauvegarde avec raison "Rename"
2. [RENAME] Renommer le personnage
3. [REFRESH] Actualiser l'affichage
```

### CREATE/DUPLICATE (Création)
```
1. [CREATE/DUPLICATE] Créer le personnage
2. [REFRESH] Actualiser l'affichage
3. [BACKUP] Créer sauvegarde avec raison "Action"
```

---

## Où Voir les Logs

1. **Console de Débogage VS Code** (Python Debug Console)
   - Lance le programme en mode debug (F5)
   - Les logs s'affichent en temps réel avec timestamps

2. **Fichier de logs** (si configuré)
   - Vérifier dans le dossier Logs/

3. **Terminal** (si lancé depuis terminal)
   - Les logs s'affichent aussi dans le terminal

---

## Points de Vérification

- [ ] Logs [APP_STARTUP] à la première ouverture
- [ ] Sauvegarde `_Startup_Daily` créée
- [ ] Logs apparaissent pour CREATE, DELETE, RENAME
- [ ] DELETE produit sauvegarde AVANT suppression
- [ ] RENAME produit sauvegarde AVANT renommage
- [ ] Noms de fichiers incluent la raison
- [ ] Format: `backup_characters_YYYYMMDD_HHMMSS_REASON.zip`
- [ ] SUCCESS/ERROR clairement indiqué
- [ ] Limite journalière respectée pour AUTO-BACKUP
- [ ] MANUAL-BACKUP contourne la limite journalière

---

## Dépannage

**Les logs ne s'affichent pas?**
- Vérifier que le debug mode est activé
- Vérifier la console Python Debug Console de VS Code
- Les logs vont aussi sur stderr (peut être affiché séparément)

**Pas de sauvegarde au démarrage?**
- Vérifier que `backup_enabled` est à `True` dans config.json
- Vérifier qu'une sauvegarde n'a pas déjà été faite aujourd'hui

**Pas de sauvegarde malgré les logs?**
- Vérifier que le dossier `Backup/Characters/` existe
- Vérifier les permissions en lecture/écriture

**Les sauvegardes continuent à être supprimées?**
- C'est normal si taille totale > limite_en_MB
- Les plus anciennes sauvegardes sont supprimées automatiquement

**Noms sans raison?**
- Vérifier que les actions passent le paramètre `reason` à `backup_characters_force()`
- Format attendu: `backup_characters_YYYYMMDD_HHMMSS_REASON`

### 5. MISE À JOUR HERALD
**Action:** Cliquer sur "Mettre à jour depuis Herald"  
**Logs attendus:**
```
[BACKUP_TRIGGER] Action: HERALD UPDATE - Attempting backup...
[BACKUP] AUTO-BACKUP triggered - Checking daily limit...
[BACKUP] AUTO-BACKUP blocked - Backup already done today - skipped
```
(ou SUCCESS si pas de sauvegarde du jour)

### 6. SAUVEGARDE MANUELLE (Fenêtre Sauvegarde)
**Action:** Cliquer sur bouton "Sauvegarder maintenant"  
**Logs attendus:**
```
[UI_BACKUP] Manual backup button clicked - Starting backup process...
[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit...
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143025.zip
[BACKUP] MANUAL-BACKUP - Applying retention policies...
[BACKUP] MANUAL-BACKUP - SUCCESS: Backup created: backup_characters_20251101_143025.zip
[UI_BACKUP] SUCCESS - Updating display...
[UI_BACKUP] Display updated successfully
```

## Où Voir les Logs

1. **Console de Débogage VS Code** (Python Debug Console)
   - Lance le programme en mode debug
   - Les logs s'affichent en temps réel

2. **Fichier de logs** (si configuré)
   - Vérifier dans le dossier Logs/

## Points de Vérification

- [ ] Logs apparaissent pour chaque action
- [ ] Format cohérent avec [BACKUP], [BACKUP_TRIGGER], [UI_BACKUP]
- [ ] SUCCESS/ERROR clairement indiqué
- [ ] Limite journalière respectée pour AUTO-BACKUP
- [ ] MANUAL-BACKUP contourne la limite journalière
- [ ] Seulement limite de taille activée (pas de limite par nombre)

## Dépannage

**Les logs ne s'affichent pas?**
- Vérifier que le debug mode est activé
- Vérifier la console Python Debug Console de VS Code
- Les logs vont aussi sur stderr (peut être affiché séparément)

**Pas de sauvegarde malgré les logs?**
- Vérifier que `backup_enabled` est à `True` dans config.json
- Vérifier le dossier `Backup/Characters/` existe
- Vérifier les permissions en lecture/écriture

**Les sauvegardes continuent à être supprimées?**
- C'est normal si taille totale > limite_en_MB
- Les plus anciennes sauvegardes sont supprimées automatiquement
