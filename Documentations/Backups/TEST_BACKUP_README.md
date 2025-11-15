# Test du Système de Backup

## Description

Ce script teste automatiquement toutes les fonctionnalités du système de sauvegarde :

### Tests effectués

1. **Backup quotidien automatique**
   - ✓ Premier backup de la journée détecté
   - ✓ Second backup du même jour ignoré
   - ✓ Backup du jour suivant autorisé

2. **Compression des backups**
   - ✓ Création de backup ZIP compressé
   - ✓ Création de backup dossier non compressé
   - ✓ Vérification de la taille

3. **Suppression automatique (auto-delete)**
   - ✓ Suppression des vieux backups quand activé
   - ✓ Conservation de tous les backups quand désactivé
   - ✓ Respect de la limite de stockage

4. **Limites de stockage**
   - ✓ Limite de 2 MB respectée
   - ✓ Mode illimité (-1) : tous les backups conservés
   - ✓ Tolérance de 10% sur les limites

5. **Backups des cookies**
   - ✓ Création de backup cookies ZIP
   - ✓ Rétention avec limite de stockage
   - ✓ Suppression automatique des anciens

## Utilisation

### Exécution du script

```powershell
# Depuis la racine du projet
python Tools/test_backup_system.py
```

### Environnement de test

Le script crée un environnement de test isolé :
```
Test_Backup_System/
├── Characters/
│   ├── character_0.json (10 KB)
│   ├── character_1.json (10 KB)
│   ├── ...
│   └── character_4.json (10 KB)
├── Cookies/
│   ├── cookies_eden_0.txt (2 KB)
│   ├── cookies_eden_1.txt (2 KB)
│   └── cookies_eden_2.txt (2 KB)
└── Backups/
    ├── Characters/  (backups créés ici)
    └── Cookies/     (backups cookies ici)
```

**Note** : L'environnement de test est automatiquement nettoyé à la fin.

## Résultats

### Format de sortie

Le script affiche des résultats colorés :
- 🟢 **Vert** : Test réussi
- 🔴 **Rouge** : Test échoué
- 🟡 **Jaune** : Information
- 🔵 **Bleu** : En cours

### Exemple de résultat

```
================================================================================
                      RÉSUMÉ DES TESTS
================================================================================

Backup quotidien...................................... ✓ RÉUSSI
Compression........................................... ✓ RÉUSSI
Auto-delete........................................... ✓ RÉUSSI
Limites stockage...................................... ✓ RÉUSSI
Cookies backup........................................ ✓ RÉUSSI

Résultat final: 5/5 tests réussis
✓ TOUS LES TESTS SONT RÉUSSIS !
```

## Détails des tests

### Test 1 : Backup quotidien
- Simule le premier démarrage de la journée
- Vérifie qu'un second backup du même jour est ignoré
- Simule le passage à un nouveau jour

### Test 2 : Compression
- Crée un backup avec compression ZIP
- Crée un backup sans compression (copie dossier)
- Compare les tailles et formats

### Test 3 : Auto-delete
- **Avec auto-delete activé** :
  - Limite : 1 MB
  - Crée 5 backups
  - Vérifie que les plus anciens sont supprimés
  - Vérifie que la limite est respectée

- **Avec auto-delete désactivé** :
  - Limite : 1 MB
  - Crée 5 backups
  - Vérifie que TOUS sont conservés (même si limite dépassée)

### Test 4 : Limites de stockage
- **Limite normale (2 MB)** :
  - Crée 10 backups
  - Vérifie que la taille totale ne dépasse pas 2 MB

- **Mode illimité (-1)** :
  - Crée 15 backups
  - Vérifie que TOUS sont conservés sans suppression

### Test 5 : Cookies backup
- Crée un backup cookies compressé
- Crée plusieurs backups avec limite de 1 MB
- Vérifie la suppression automatique

## Configuration testée

Le script modifie temporairement ces paramètres :
- `backup_enabled` : `True`
- `backup_compress` : `True` / `False`
- `backup_auto_delete_old` : `True` / `False`
- `backup_size_limit_mb` : `1`, `2`, `-1`
- `cookies_backup_enabled` : `True`
- `cookies_backup_compress` : `True`
- `cookies_backup_auto_delete_old` : `True`
- `cookies_backup_size_limit_mb` : `1`

**Important** : La configuration originale est automatiquement restaurée à la fin des tests.

## Codes de sortie

- `0` : Tous les tests réussis
- `1` : Au moins un test échoué

## Dépannage

### Le script ne trouve pas les modules
```powershell
# Assurez-vous d'être dans le bon environnement virtuel
.\.venv\Scripts\Activate.ps1

# Vérifiez que vous êtes à la racine du projet
cd D:\Projets\Python\DAOC-Character-Management
```

### Erreur de permissions
```powershell
# Exécutez en tant qu'administrateur si nécessaire
# ou vérifiez les droits d'accès au dossier Tools/
```

### Tests échouent
1. Vérifiez les logs dans le terminal
2. Vérifiez que le dossier `Test_Backup_System/` peut être créé
3. Vérifiez qu'aucun processus ne bloque les fichiers
4. Relancez le script

## Notes techniques

### Tolérance
- Les tests de limite de stockage ont une tolérance de **10%**
- Exemple : limite de 2 MB → accepte jusqu'à 2.2 MB
- Raison : compression variable selon les données

### Timing
- Délai de 0.2s entre chaque backup pour différencier les timestamps
- Évite les conflits de noms de fichiers

### Isolation
- Le script ne modifie PAS vos backups réels
- Crée un environnement complètement isolé
- Nettoie automatiquement à la fin

## Maintenance

Pour ajouter un nouveau test :

1. Créer une fonction `test_nouvelle_fonctionnalite(config_mgr, backup_mgr, test_paths)`
2. Retourner `True` si réussi, `False` sinon
3. Ajouter à la liste `results` dans `main()`

Exemple :
```python
def test_nouvelle_fonctionnalite(config_mgr, backup_mgr, test_paths):
    print_header("TEST X: NOUVELLE FONCTIONNALITÉ")
    
    print_test("X.1 - Sous-test 1")
    # ... code de test ...
    
    if condition_reussie:
        print_success("Test réussi")
        return True
    else:
        print_error("Test échoué")
        return False
```

## Auteur

Script créé pour tester le système de backup v0.108+
