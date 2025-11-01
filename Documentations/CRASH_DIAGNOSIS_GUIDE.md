# Guide de Diagnostic des Arrêts Inattendus

## 📋 Contexte
L'application s'arrête parfois sans message d'erreur visible. Nous avons implémenté un système de diagnostic robuste pour capturer les causes.

## 🔧 Modifications Apportées (v0.106)

### 1. **Gestionnaires d'Exceptions Renforcés** (`main.py`)
```python
- global_exception_handler() : Capture les exceptions non gérées
- signal_handler()          : Capture les signaux système (SIGTERM, SIGINT, etc.)
- on_app_exit()             : Enregistre la fermeture de l'application
- atexit.register()         : Garantit que on_app_exit() est appelé
```

### 2. **Logging Amélioré** (`Functions/logging_manager.py`)
- **Avant** : Les erreurs n'étaient loggées que si debug_mode = true
- **Maintenant** : Les erreurs CRITICAL et ERROR sont **toujours** loggées, même avec debug_mode = false

### 3. **Traçage du Démarrage** (`main.py`)
- Enregistrement précis de l'heure de démarrage (ISO 8601)
- Affichage de la version Python
- Énumération de tous les threads actifs au démarrage
- Affichage du code de sortie de la boucle d'événements

## 📍 Où Chercher les Erreurs

### **Fichier log principal**
```
Configuration/debug.log
```

### **Ce que vous verrez maintenant**
```
[2025-11-01T14:23:45,123] - root - INFO - Application started at 2025-11-01T14:23:45.123456
[2025-11-01T14:23:45,124] - root - INFO - Python version: 3.13.9
[2025-11-01T14:23:45,125] - root - DEBUG - Active threads at startup: 1
[2025-11-01T14:23:45,126] - root - DEBUG -   - MainThread (daemon: False)
...
[2025-11-01T14:25:00,000] - root - CRITICAL - UNHANDLED EXCEPTION:
Traceback (most recent call last):
  File "...", line XXX, in some_method
    ...
TypeError: ...
```

## 🔍 Scénarios de Diagnostic

### **Scénario 1 : Application s'arrête sans erreur visible**
**À faire :**
1. Activez le mode debug : Paramètres → "Activer le mode débogage"
2. Reproduisez le problème
3. Vérifiez `Configuration/debug.log` à la fin pour les messages CRITICAL/ERROR

### **Scénario 2 : Application s'arrête lors d'une action spécifique**
**À faire :**
1. Notez l'action exacte qui provoque l'arrêt
2. Cherchez dans le log les messages autour du timestamp
3. Cherchez les patterns : "UNHANDLED EXCEPTION", "signal_handler", "Fatal error"

### **Scénario 3 : Arrêt complètement silencieux (pas d'erreur dans les logs)**
**Causes possibles :**
- Appel à `sys.exit()` quelque part sans logging
- Thread non-daemon qui se termine et termine l'app
- Forcer la fermeture de l'application (Ctrl+C, Task Manager)
- Limitation de ressources système

**À faire :**
1. Cherchez "Application exit at" dans le log pour confirmer que on_app_exit() a été appelé
2. Cherchez les threads dans "Active threads" → Si un thread daemon = False se termine, l'app s'arrête
3. Vérifiez la console système pour les messages stderr

### **Scénario 4 : Détecter un signal système**
**Si vous voyez dans le log :**
```
[2025-11-01T14:25:00,000] - root - CRITICAL - Application interrupted by signal: SIGTERM
```

Cela signifie que le système d'exploitation a forcé l'arrêt de l'application.

## 📊 Types d'Erreurs à Chercher

### ❌ **TypeError**
```
TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'
```
→ Une valeur None a été utilisée où une string était attendue

### ❌ **AttributeError**
```
AttributeError: 'QWidget' object has no attribute 'some_method'
```
→ Tentative d'accès à une méthode/propriété inexistante

### ❌ **IndexError**
```
IndexError: list index out of range
```
→ Accès à un index invalide dans une liste

### ❌ **KeyError**
```
KeyError: 'some_key'
```
→ Clé manquante dans un dictionnaire

### ❌ **RuntimeError (PySide6)**
```
RuntimeError: wrapped C++ object has been deleted
```
→ Tentative d'utilisation d'un widget Qt qui a été supprimé

## 🛠️ Débogage Avancé

### **Afficher la fenêtre de debug au démarrage**
1. Paramètres → "Afficher la fenêtre de debug" ✓
2. Relancez l'application
3. La fenêtre de debug affichera tous les logs en temps réel

### **Console stderr**
Si vous lancez l'app depuis un terminal/PowerShell :
```powershell
& 'path\to\python.exe' main.py
```
Les messages stderr (erreurs critiques) apparaîtront aussi dans le terminal.

### **Vérifier les threads non-daemon**
Cherchez dans le log au démarrage :
```
Active threads at startup: 2
  - MainThread (daemon: False)
  - Worker (daemon: False)  ← ⚠️ Si ce thread se termine, l'app s'arrête
```

## 📋 Checklist de Diagnostic

- [ ] Vérifier `Configuration/debug.log` après l'arrêt
- [ ] Chercher "CRITICAL", "ERROR", "UNHANDLED EXCEPTION"
- [ ] Noter l'heure exacte de l'arrêt (Application exit at)
- [ ] Chercher "signal_handler" → Arrêt forcé du système
- [ ] Chercher les threads non-daemon → Vérifier si l'un d'eux s'arrête
- [ ] Activer le mode debug si ce n'est pas fait
- [ ] Lancer depuis le terminal pour voir stderr

## 🔗 Fichiers Modifiés
- `main.py` : Gestionnaires d'exceptions et signaux renforcés
- `Functions/logging_manager.py` : Logging ERROR/CRITICAL toujours actif

## 💡 Prochaines Étapes
1. Rassemblez les logs après l'arrêt suivant
2. Partagez la section "UNHANDLED EXCEPTION" du log
3. On pourra identifier précisément la cause et implémenter un correctif
