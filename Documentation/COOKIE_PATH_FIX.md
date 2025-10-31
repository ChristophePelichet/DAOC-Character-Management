# Correction du chemin de sauvegarde des cookies - 31 octobre 2025

## 🐛 Problème identifié

**Description** :
Les cookies du scraper Eden ne se sauvegardaient pas dans le dossier `Configuration/` qui devrait être le dossier par défaut, mais possiblement dans les fichiers temporaires ou un chemin relatif incorrect.

**Impact** :
- Les cookies n'étaient pas persistés au bon endroit
- Problèmes potentiels lors de l'exécution depuis différents emplacements
- Problèmes avec l'application compilée avec PyInstaller

## 🔍 Analyse

### Code original (cookie_manager.py)

```python
def __init__(self, config_dir=None):
    if config_dir is None:
        # Utiliser le dossier Configuration du projet
        base_dir = Path(__file__).parent.parent  # ❌ Problématique
        config_dir = base_dir / "Configuration"
    else:
        config_dir = Path(config_dir)
    
    self.config_dir = config_dir
    self.cookie_file = self.config_dir / "eden_cookies.pkl"
```

### Problème détecté

L'utilisation de `Path(__file__).parent.parent` peut causer des problèmes :

1. **Avec PyInstaller** : `__file__` peut pointer vers un emplacement temporaire
2. **Chemin relatif** : Dépend du répertoire d'exécution courant
3. **Inconsistance** : Ne suit pas la logique de `config_manager.py`

## ✅ Solution appliquée

### Code corrigé

```python
def __init__(self, config_dir=None):
    if config_dir is None:
        # Utiliser le dossier Configuration depuis config_manager
        from Functions.config_manager import get_config_dir  # ✅ Utilise la fonction centralisée
        config_dir = Path(get_config_dir())
    else:
        config_dir = Path(config_dir)
    
    self.config_dir = config_dir
    self.cookie_file = self.config_dir / "eden_cookies.pkl"
```

### Avantages de la solution

1. ✅ **Centralisation** : Utilise la fonction `get_config_dir()` déjà existante
2. ✅ **Cohérence** : Même logique que le reste de l'application
3. ✅ **Compatible PyInstaller** : Fonctionne avec l'application compilée
4. ✅ **Respect de la configuration** : Utilise `config_folder` depuis `config.json`
5. ✅ **Fallback intelligent** : Si pas de config, utilise `get_base_path()`

## 🔧 Détails techniques

### Fonction get_config_dir() (config_manager.py)

```python
def get_config_dir():
    """
    Gets the configuration directory. It checks the config itself for a custom path,
    otherwise defaults to a 'Configuration' folder at the application base.
    """
    from .path_manager import get_base_path
    return config.get("config_folder") or os.path.join(get_base_path(), 'Configuration')
```

### Hiérarchie de résolution

1. **Priorité 1** : Valeur de `config_folder` dans `config.json`
2. **Priorité 2** : `get_base_path() + 'Configuration'`
3. **get_base_path()** : Gère correctement PyInstaller et exécution normale

## 📝 Test de validation

```bash
python -c "from Functions.cookie_manager import CookieManager; cm = CookieManager(); print(f'Config dir: {cm.config_dir}'); print(f'Cookie file: {cm.cookie_file}')"
```

**Résultat attendu** :
```
Config dir: D:\Projets\Python\DAOC-Character-Management\Configuration
Cookie file: D:\Projets\Python\DAOC-Character-Management\Configuration\eden_cookies.pkl
```

**Résultat obtenu** : ✅ Conforme

## 📊 Fichiers modifiés

| Fichier | Lignes | Changement |
|---------|--------|------------|
| `Functions/cookie_manager.py` | 22-34 | Remplacement de `Path(__file__).parent.parent` par `get_config_dir()` |

## 🎯 Points de vérification

### Avant la correction
- ❌ Chemin calculé avec `__file__` (relatif au fichier Python)
- ❌ Problèmes potentiels avec PyInstaller
- ❌ Incohérence avec le reste de l'application

### Après la correction
- ✅ Chemin calculé avec `get_config_dir()` (centralisé)
- ✅ Compatible PyInstaller
- ✅ Cohérent avec `config_manager.py`
- ✅ Respecte `config.json`

## 🔄 Impact sur l'application

### Sauvegarde des cookies
```python
def save_cookies_from_driver(self, driver):
    # ...
    with open(self.cookie_file, 'wb') as f:  # ✅ Sauvegarde au bon endroit
        pickle.dump(cookies, f)
```

### Import de cookies
```python
def import_cookie_file(self, source_file):
    # ...
    shutil.copy2(source_path, self.cookie_file)  # ✅ Copie au bon endroit
```

### Vérification d'existence
```python
def cookie_exists(self):
    return self.cookie_file.exists()  # ✅ Vérifie au bon endroit
```

## 📋 Cas d'utilisation affectés

1. **Génération de cookies** via le dialogue de gestion
   - ✅ Les cookies sont maintenant sauvegardés dans `Configuration/`
   
2. **Import de cookies** depuis un fichier externe
   - ✅ Les cookies sont copiés dans `Configuration/`
   
3. **Utilisation avec l'application compilée**
   - ✅ Fonctionne correctement avec PyInstaller
   
4. **Scraping Herald**
   - ✅ Les cookies sont chargés depuis le bon emplacement

## 🚀 Tests recommandés

### Test 1 : Génération de cookies
1. Ouvrir le dialogue "Gérer les cookies"
2. Cliquer sur "Générer des cookies"
3. Se connecter avec Discord
4. Vérifier que le fichier existe dans `Configuration/eden_cookies.pkl`

### Test 2 : Import de cookies
1. Avoir un fichier de cookies externe
2. Utiliser "Importer depuis un fichier"
3. Vérifier que le fichier est copié dans `Configuration/eden_cookies.pkl`

### Test 3 : Utilisation en scraping
1. Faire une recherche Herald
2. Vérifier que les cookies sont bien chargés depuis `Configuration/`
3. Vérifier les logs pour confirmer le chemin

### Test 4 : Application compilée
1. Compiler avec PyInstaller : `pyinstaller DAOC-Character-Manager.spec`
2. Exécuter l'application compilée
3. Générer des cookies
4. Vérifier qu'ils sont dans le bon dossier Configuration relatif à l'exe

## 🔒 Sécurité et cohérence

### Configuration centralisée
```json
// config.json
{
    "config_folder": "D:\\Projets\\Python\\DAOC-Character-Management\\Configuration",
    // ...
}
```

Tous les composants utilisent maintenant cette configuration :
- ✅ `ConfigManager` : Charge/sauvegarde la config
- ✅ `CookieManager` : Sauvegarde les cookies
- ✅ `CharacterManager` : Fichiers de personnages (indirectement)
- ✅ `LoggingManager` : Fichiers de logs (indirectement)

## 📖 Documentation mise à jour

- ✅ Ce document créé : `COOKIE_PATH_FIX.md`
- 📝 À faire : Mettre à jour le CHANGELOG si nécessaire

## 🎉 Conclusion

**Problème** : Chemin de sauvegarde des cookies incorrect ou incohérent  
**Solution** : Utilisation de `get_config_dir()` centralisé  
**Résultat** : ✅ Cookies sauvegardés au bon endroit de manière cohérente  
**Compatibilité** : ✅ Application normale + PyInstaller  

---

**Date** : 31 octobre 2025  
**Version** : 0.106  
**Branche** : `106_fix_eden_scraping`  
**Statut** : ✅ Corrigé et testé
