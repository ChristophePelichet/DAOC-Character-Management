# 🛡️ Patterns de Sécurité Thread - Guide de Référence Rapide

**Date de création** : 14 novembre 2025  
**Contexte** : Architecture fenêtres de progression avec QThread  
**Framework** : PySide6 (Python 3.13.9)

---

## 📚 Table des Matières

1. [Pattern 1 : Protection RuntimeError](#pattern-1--protection-runtimeerror)
2. [Pattern 2 : Cleanup Ressources Externes](#pattern-2--cleanup-ressources-externes)
3. [Pattern 3 : Interruption Gracieuse](#pattern-3--interruption-gracieuse)
4. [Pattern 4 : Signal Dialog Rejected](#pattern-4--signal-dialog-rejected)
5. [Pattern 5 : Cleanup Asynchrone pour Fermeture Rapide](#pattern-5--cleanup-asynchrone-pour-fermeture-rapide)
6. [Checklist de Validation](#checklist-de-validation)
7. [Exemple Complet](#exemple-complet)

---

## Pattern 1 : Protection RuntimeError

### 🚨 Problème
```python
# ❌ DANGEREUX : Connection directe
self.worker_thread.step_started.connect(self.progress_dialog.start_step)

# Si dialog détruit → RuntimeError: wrapped C/C++ object has been deleted
```

### ✅ Solution : Wrappers Thread-Safe
```python
# Dans la classe dialog :
def start_operation(self):
    # Connecter via wrappers
    self.worker_thread.step_started.connect(self._on_step_started)
    self.worker_thread.step_completed.connect(self._on_step_completed)
    self.worker_thread.step_error.connect(self._on_step_error)

def _on_step_started(self, step_index):
    """Wrapper thread-safe"""
    if hasattr(self, 'progress_dialog') and self.progress_dialog:
        try:
            self.progress_dialog.start_step(step_index)
        except RuntimeError:
            pass  # Dialog détruit, pas d'erreur

def _on_step_completed(self, step_index):
    """Wrapper thread-safe"""
    if hasattr(self, 'progress_dialog') and self.progress_dialog:
        try:
            self.progress_dialog.complete_step(step_index)
        except RuntimeError:
            pass

def _on_step_error(self, step_index, error_message):
    """Wrapper thread-safe"""
    if hasattr(self, 'progress_dialog') and self.progress_dialog:
        try:
            self.progress_dialog.error_step(step_index, error_message)
        except RuntimeError:
            pass
```

### 📝 Règles
- ✅ **TOUJOURS** utiliser des wrappers pour les signaux thread → dialog
- ✅ **TOUJOURS** vérifier `hasattr()` ET `self.progress_dialog` (pas juste truthy)
- ✅ **TOUJOURS** wrapper dans `try/except RuntimeError`
- ❌ **JAMAIS** de connexion directe `thread.signal.connect(dialog.method)`

---

## Pattern 2 : Cleanup Ressources Externes

### 🚨 Problème
```python
# Dans QThread.run() :
try:
    driver = webdriver.Chrome()  # Ressource externe
    driver.get("https://example.com")
finally:
    driver.quit()  # ❌ NE S'EXÉCUTE PAS si thread.terminate()
```

**Quand `thread.terminate()` est appelé, le `finally` ne s'exécute JAMAIS** → ressources restent ouvertes (browser Selenium, fichiers, connexions DB)

### ✅ Solution : Cleanup AVANT terminate()
```python
class WorkerThread(QThread):
    def __init__(self):
        super().__init__()
        self._stop_requested = False
        self._external_resource = None  # ✅ Référence pour cleanup externe
    
    def request_stop(self):
        """Demande arrêt gracieux"""
        self._stop_requested = True
    
    def cleanup_external_resources(self):
        """
        ✅ APPELÉ DEPUIS THREAD PRINCIPAL avant terminate()
        Permet cleanup même si finally ne s'exécute pas
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if self._external_resource:
            try:
                logger.info("Cleanup forcé de la ressource externe")
                
                # Adapter selon le type de ressource :
                # - Selenium : self._external_resource.quit()
                # - Fichier : self._external_resource.close()
                # - Connexion DB : self._external_resource.close()
                self._external_resource.quit()
                
                logger.info("Ressource fermée avec succès")
            except Exception as e:
                logger.warning(f"Erreur cleanup: {e}")
            finally:
                self._external_resource = None
    
    def run(self):
        import logging
        logger = logging.getLogger(__name__)
        resource = None
        
        try:
            # Créer ressource
            resource = create_external_resource()
            self._external_resource = resource  # ✅ Stocker pour cleanup externe
            
            # Utiliser ressource
            resource.do_work()
            
            # Checks réguliers
            if self._stop_requested:
                return  # Sortie → finally s'exécute
        
        finally:
            # Cleanup normal (s'exécute si pas terminate())
            if resource:
                try:
                    resource.cleanup()
                except Exception as e:
                    logger.warning(f"Erreur cleanup finally: {e}")

# Dans la classe dialog :
def _stop_worker_thread(self):
    if hasattr(self, 'worker_thread') and self.worker_thread:
        if self.worker_thread.isRunning():
            # 1. Demander arrêt gracieux
            self.worker_thread.request_stop()
            
            # 2. Déconnecter signaux
            try:
                self.worker_thread.step_started.disconnect()
                self.worker_thread.step_completed.disconnect()
                self.worker_thread.step_error.disconnect()
            except:
                pass
            
            # 3. Attendre 3s
            self.worker_thread.wait(3000)
            
            # 4. ✅ CRITIQUE : Cleanup AVANT terminate()
            if self.worker_thread.isRunning():
                logging.warning("Thread non terminé - Cleanup forcé")
                self.worker_thread.cleanup_external_resources()
                self.worker_thread.terminate()
                self.worker_thread.wait()
        
        self.worker_thread = None
```

### 📝 Règles
- ✅ **TOUJOURS** ajouter `self._external_resource = None` dans `__init__()`
- ✅ **TOUJOURS** stocker : `self._external_resource = resource` après création
- ✅ **TOUJOURS** créer méthode `cleanup_external_resources()` (appelable depuis autre thread)
- ✅ **TOUJOURS** appeler cleanup AVANT `terminate()` dans `_stop_worker_thread()`
- ✅ **TOUJOURS** garder le `finally` pour cleanup normal

---

## Pattern 3 : Interruption Gracieuse

### 🚨 Problème
```python
# ❌ BLOQUANT : Thread ne répond pas au request_stop()
time.sleep(5)  # Bloque pendant 5s, pas d'interruption possible
driver.get(url)  # Peut bloquer longtemps sur réseau lent
```

### ✅ Solution : Checks réguliers et Sleep Interruptible
```python
class WorkerThread(QThread):
    def run(self):
        # Opération 1
        self.step_started.emit(0)
        do_work_step_1()
        self.step_completed.emit(0)
        
        # ✅ Check après opération critique
        if self._stop_requested:
            logging.info("Arrêt demandé après step 1")
            return  # Sortie immédiate
        
        # Opération 2
        self.step_started.emit(1)
        do_work_step_2()
        self.step_completed.emit(1)
        
        if self._stop_requested:
            return
        
        # ❌ MAUVAIS : Sleep bloquant
        # time.sleep(5)
        
        # ✅ BON : Sleep interruptible
        for i in range(10):  # 10 x 0.5s = 5s total
            if self._stop_requested:
                logging.info("Arrêt demandé pendant sleep")
                return
            time.sleep(0.5)
        
        # Opération longue (réseau)
        self.step_started.emit(2)
        driver.get(long_url)  # Peut bloquer
        
        # ✅ Check immédiatement après
        if self._stop_requested:
            return
        
        # Continue...
```

### 📝 Règles
- ✅ **TOUJOURS** vérifier `if self._stop_requested: return` après CHAQUE opération critique
- ✅ **TOUJOURS** remplacer `time.sleep(N)` par boucle interruptible :
  ```python
  for _ in range(N * 2):  # N secondes
      if self._stop_requested:
          return
      time.sleep(0.5)
  ```
- ✅ **TOUJOURS** vérifier après opérations réseau (get, post, query)
- ✅ **TOUJOURS** vérifier après opérations I/O (read, write)
- 💡 **Granularité** : Plus de checks = meilleure réactivité (viser 1 check par seconde max)

---

## Pattern 4 : Signal Dialog Rejected

### 🚨 Problème
```python
# Dialog fermé par utilisateur (X ou Escape)
# → Aucun cleanup automatique → thread continue → ressources ouvertes
```

### ✅ Solution : Connecter `rejected` Signal
```python
class MainDialog(QDialog):
    def start_operation(self):
        # Créer progress dialog
        self.progress_dialog = ProgressStepsDialog(...)
        
        # ✅ Connecter rejected AVANT show()
        self.progress_dialog.rejected.connect(self._on_progress_dialog_closed)
        
        # Créer et démarrer thread
        self.worker_thread = WorkerThread(...)
        self.worker_thread.step_started.connect(self._on_step_started)
        self.worker_thread.start()
        
        # Afficher dialog
        self.progress_dialog.show()
    
    def _on_progress_dialog_closed(self):
        """
        ✅ Appelé quand utilisateur ferme dialog (X, Escape, close())
        Déclenche cleanup complet
        """
        logging.info("Dialog fermé par utilisateur - Arrêt opération")
        
        # Arrêter thread (avec cleanup)
        self._stop_worker_thread()
        
        # Réactiver contrôles UI
        self.start_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.combo_box.setEnabled(True)
```

### 📝 Règles
- ✅ **TOUJOURS** connecter `progress_dialog.rejected` → `_on_progress_dialog_closed()`
- ✅ **TOUJOURS** connecter AVANT `show()` ou `exec()`
- ✅ **TOUJOURS** appeler `_stop_worker_thread()` dans le handler
- ✅ **TOUJOURS** réactiver les contrôles UI dans le handler
- 💡 Tester en fermant dialog avec X, Escape, et close()

---

## Checklist de Validation

### ✅ Avant de commencer la migration
- [ ] Lire ce document
- [ ] Identifier les ressources externes (Selenium, fichiers, DB, réseau)
- [ ] Identifier les opérations longues (sleep, réseau, I/O)

### ✅ Dans la classe WorkerThread
- [ ] Attribut `self._stop_requested = False` dans `__init__()`
- [ ] Méthode `request_stop(self)` pour setter le flag
- [ ] Si ressources externes :
  - [ ] Attribut `self._external_resource = None` dans `__init__()`
  - [ ] Stockage : `self._external_resource = resource` après création
  - [ ] Méthode `cleanup_external_resources(self)` complète
- [ ] Checks `if self._stop_requested: return` après opérations critiques
- [ ] Sleeps remplacés par boucles interruptibles
- [ ] `finally` block conservé pour cleanup normal

### ✅ Dans la classe Dialog
- [ ] Wrappers thread-safe pour TOUS les signaux :
  - [ ] `_on_step_started(self, step_index)`
  - [ ] `_on_step_completed(self, step_index)`
  - [ ] `_on_step_error(self, step_index, error_message)`
- [ ] Chaque wrapper vérifie `hasattr() and self.progress_dialog`
- [ ] Chaque wrapper a `try/except RuntimeError`
- [ ] Méthode `_stop_worker_thread(self)` avec ordre correct :
  1. `request_stop()`
  2. Disconnect signaux
  3. `wait(3000)`
  4. Si still running : `cleanup_external_resources()` puis `terminate()`
- [ ] Signal `rejected` connecté à `_on_progress_dialog_closed()`
- [ ] Handler de fermeture appelle `_stop_worker_thread()` + réactive UI

### ✅ Tests de validation
- [ ] Test normal (opération complète)
- [ ] Test fermeture précoce (X après 2s)
- [ ] Test fermeture avec Escape
- [ ] Test fermeture rapide (X après 0.5s)
- [ ] Vérifier aucun processus reste ouvert (Task Manager)
- [ ] Vérifier aucun fichier reste ouvert (lsof ou Handle)
- [ ] Vérifier logs : cleanup appelé correctement

---

## Exemple Complet

```python
# ============================================================================
# WorkerThread avec TOUS les patterns de sécurité
# ============================================================================
from PySide6.QtCore import QThread, Signal
import logging
import time

class SafeWorkerThread(QThread):
    """Thread sécurisé avec cleanup complet"""
    
    # Signaux
    step_started = Signal(int)
    step_completed = Signal(int)
    step_error = Signal(int, str)
    operation_finished = Signal(bool, str)
    
    def __init__(self, parameter):
        super().__init__()
        self.parameter = parameter
        
        # ✅ Pattern 3 : Flag d'interruption
        self._stop_requested = False
        
        # ✅ Pattern 2 : Référence ressource externe
        self._driver = None
    
    def request_stop(self):
        """✅ Pattern 3 : Demande arrêt gracieux"""
        self._stop_requested = True
    
    def cleanup_external_resources(self):
        """✅ Pattern 2 : Cleanup forcé (appelé depuis thread principal)"""
        logger = logging.getLogger(__name__)
        
        if self._driver:
            try:
                logger.info("Cleanup forcé : Fermeture Selenium")
                self._driver.quit()
                logger.info("Driver fermé avec succès")
            except Exception as e:
                logger.warning(f"Erreur cleanup driver: {e}")
            finally:
                self._driver = None
    
    def run(self):
        """Exécution avec patterns de sécurité"""
        from selenium import webdriver
        logger = logging.getLogger(__name__)
        driver = None
        
        try:
            # Step 0 : Init
            self.step_started.emit(0)
            driver = webdriver.Chrome()
            self._driver = driver  # ✅ Pattern 2 : Stocker pour cleanup
            self.step_completed.emit(0)
            
            # ✅ Pattern 3 : Check après opération critique
            if self._stop_requested:
                logger.info("Arrêt demandé après init")
                return
            
            # Step 1 : Navigation
            self.step_started.emit(1)
            driver.get("https://example.com")
            self.step_completed.emit(1)
            
            if self._stop_requested:
                return
            
            # Step 2 : Wait (interruptible)
            self.step_started.emit(2)
            
            # ✅ Pattern 3 : Sleep interruptible
            for i in range(10):  # 5 secondes
                if self._stop_requested:
                    logger.info("Arrêt demandé pendant sleep")
                    return
                time.sleep(0.5)
            
            self.step_completed.emit(2)
            
            if self._stop_requested:
                return
            
            # Step 3 : Extract data
            self.step_started.emit(3)
            data = driver.find_element("id", "data").text
            self.step_completed.emit(3)
            
            # Success
            self.operation_finished.emit(True, f"Data: {data}")
        
        except Exception as e:
            logger.error(f"Erreur: {e}")
            self.step_error.emit(0, str(e))
            self.operation_finished.emit(False, str(e))
        
        finally:
            # ✅ Pattern 2 : Cleanup normal (s'exécute si pas terminate())
            if driver:
                try:
                    logger.info("Cleanup normal : Fermeture driver")
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Erreur cleanup finally: {e}")


# ============================================================================
# Dialog avec TOUS les patterns de sécurité
# ============================================================================
from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout
from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration

class SafeDialog(QDialog):
    """Dialog sécurisé avec gestion complète du thread"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        self.start_button = QPushButton("Start Operation")
        self.start_button.clicked.connect(self.start_operation)
        layout.addWidget(self.start_button)
        self.setLayout(layout)
    
    def start_operation(self):
        """Démarre opération avec progress dialog"""
        # Désactiver contrôles
        self.start_button.setEnabled(False)
        
        # Créer steps
        steps = StepConfiguration.build_steps(
            StepConfiguration.HERALD_CONNECTION,
            StepConfiguration.CLEANUP
        )
        
        # Créer progress dialog
        self.progress_dialog = ProgressStepsDialog(
            parent=self,
            title="Operation in Progress",
            steps=steps,
            show_progress_bar=True,
            allow_cancel=False
        )
        
        # ✅ Pattern 4 : Connecter rejected AVANT show()
        self.progress_dialog.rejected.connect(self._on_progress_dialog_closed)
        
        # Créer thread
        self.worker_thread = SafeWorkerThread(parameter="test")
        
        # ✅ Pattern 1 : Connexions via wrappers thread-safe
        self.worker_thread.step_started.connect(self._on_step_started)
        self.worker_thread.step_completed.connect(self._on_step_completed)
        self.worker_thread.step_error.connect(self._on_step_error)
        self.worker_thread.operation_finished.connect(self.on_operation_finished)
        
        # Démarrer
        self.worker_thread.start()
        self.progress_dialog.show()
    
    # ✅ Pattern 1 : Wrappers thread-safe
    def _on_step_started(self, step_index):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.start_step(step_index)
            except RuntimeError:
                pass
    
    def _on_step_completed(self, step_index):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.complete_step(step_index)
            except RuntimeError:
                pass
    
    def _on_step_error(self, step_index, error_message):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            try:
                self.progress_dialog.error_step(step_index, error_message)
            except RuntimeError:
                pass
    
    # ✅ Pattern 4 : Handler de fermeture
    def _on_progress_dialog_closed(self):
        """Appelé quand utilisateur ferme dialog"""
        logging.info("Dialog fermé par utilisateur - Arrêt opération")
        
        # Arrêter thread
        self._stop_worker_thread()
        
        # Réactiver UI
        self.start_button.setEnabled(True)
    
    def on_operation_finished(self, success, message):
        """Appelé quand opération terminée"""
        if hasattr(self, 'progress_dialog'):
            if success:
                self.progress_dialog.complete_all(f"✅ {message}")
            else:
                self.progress_dialog.set_status_message(f"❌ {message}", "#F44336")
        
        self.start_button.setEnabled(True)
    
    # ✅ Pattern 2 + 3 : Arrêt sécurisé du thread
    def _stop_worker_thread(self):
        """Arrête le thread avec cleanup complet"""
        if hasattr(self, 'worker_thread') and self.worker_thread:
            if self.worker_thread.isRunning():
                # 1. Demander arrêt gracieux
                self.worker_thread.request_stop()
                
                # 2. Déconnecter signaux
                try:
                    self.worker_thread.step_started.disconnect()
                    self.worker_thread.step_completed.disconnect()
                    self.worker_thread.step_error.disconnect()
                    self.worker_thread.operation_finished.disconnect()
                except:
                    pass
                
                # 3. Attendre 3s
                self.worker_thread.wait(3000)
                
                # 4. ✅ CRITIQUE : Cleanup AVANT terminate()
                if self.worker_thread.isRunning():
                    logging.warning("Thread non terminé - Cleanup forcé")
                    self.worker_thread.cleanup_external_resources()
                    self.worker_thread.terminate()
                    self.worker_thread.wait()
                
                logging.info("Thread arrêté proprement")
            
            self.worker_thread = None
        
        # Fermer dialog
        if hasattr(self, 'progress_dialog'):
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except:
                pass
            delattr(self, 'progress_dialog')
```

---

## Pattern 5 : Cleanup Asynchrone pour Fermeture Rapide

### 🚨 Problème
```python
# ❌ BLOQUANT : Fermeture de fenêtre lente (2-3 clics nécessaires)
def closeEvent(self, event):
    self._stop_search_thread()  # wait(3000) → bloque 3 secondes !
    self._cleanup_temp_files()  # I/O peut être lent
    super().closeEvent(event)
```

**Symptômes** :
- L'utilisateur clique sur la croix mais la fenêtre ne se ferme pas immédiatement
- Nécessite 2-3 clics avant que la fenêtre réponde
- UI freeze pendant plusieurs secondes après l'import de personnages

**Causes** :
1. `thread.wait(timeout)` bloque l'event loop Qt pendant le timeout
2. Operations I/O synchrones (cleanup fichiers, refresh UI, backup)
3. `closeEvent()` attend la fin des opérations avant d'appeler `super().closeEvent()`

### ✅ Solution : Cleanup via QTimer (Non-Bloquant)

#### 1️⃣ Fermeture Immédiate avec Cleanup Asynchrone

```python
from PySide6.QtCore import QTimer

def closeEvent(self, event):
    """Appelé à la fermeture - ACCEPTE IMMÉDIATEMENT"""
    # Cleanup asynchrone sans bloquer la fermeture
    QTimer.singleShot(0, self._async_full_cleanup)
    
    # Appeler super() IMMÉDIATEMENT pour fermer la fenêtre
    super().closeEvent(event)

def _async_full_cleanup(self):
    """Cleanup complet en arrière-plan"""
    try:
        self._stop_search_thread_async()
        self._cleanup_temp_files()
    except Exception as e:
        logging.warning(f"Erreur pendant cleanup async: {e}")
```

#### 2️⃣ Stop Thread Asynchrone (Capture de Référence)

```python
def _stop_search_thread_async(self):
    """Version non-bloquante de stop thread"""
    if hasattr(self, 'search_thread') and self.search_thread is not None:
        # ✅ Capturer la référence AVANT de passer à l'async
        thread_ref = self.search_thread
        
        if thread_ref.isRunning():
            # Demander arrêt gracieux
            thread_ref.request_stop()
            
            # Déconnecter signaux
            try:
                thread_ref.search_finished.disconnect()
                thread_ref.step_started.disconnect()
                thread_ref.step_completed.disconnect()
                thread_ref.step_error.disconnect()
            except:
                pass
            
            # Cleanup asynchrone du thread
            def _async_thread_cleanup():
                try:
                    if thread_ref and thread_ref.isRunning():
                        # Wait court (100ms au lieu de 3000ms)
                        thread_ref.wait(100)
                        
                        if thread_ref.isRunning():
                            logging.warning("Thread actif - Cleanup forcé")
                            try:
                                thread_ref.cleanup_driver()
                                thread_ref.terminate()
                                thread_ref.wait()
                            except:
                                pass
                        
                        logging.info("Thread arrêté (async)")
                except Exception as e:
                    logging.warning(f"Erreur cleanup async thread: {e}")
            
            # Exécuter après 50ms (non-bloquant)
            QTimer.singleShot(50, _async_thread_cleanup)
        
        # Nettoyer référence immédiatement
        self.search_thread = None
    
    # Cleanup progress dialog
    if hasattr(self, 'progress_dialog'):
        try:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
        except:
            pass
        
        try:
            delattr(self, 'progress_dialog')
        except:
            pass
```

#### 3️⃣ Operations Lourdes en Asynchrone (Refresh + Backup)

```python
def _import_characters(self, characters):
    """Importe personnages depuis Herald"""
    # ... code d'import ...
    
    # Afficher résultat immédiatement
    QMessageBox.information(self, "Import terminé", message)
    
    # ✅ Refresh UI de manière asynchrone (ne bloque pas)
    if hasattr(self.parent(), 'tree_manager'):
        QTimer.singleShot(100, self.parent().tree_manager.refresh_character_list)
    
    # ✅ Backup asynchrone (ne bloque pas)
    parent_app = self.parent()
    if hasattr(parent_app, 'backup_manager'):
        def _async_backup():
            try:
                logging.info("[BACKUP] Démarrage backup asynchrone")
                parent_app.backup_manager.backup_characters_force(
                    reason="Update", 
                    character_name="multi"
                )
            except Exception as e:
                logging.warning(f"[BACKUP] Erreur backup async: {e}")
        
        QTimer.singleShot(200, _async_backup)
```

### 📝 Règles du Pattern 5

#### ✅ À FAIRE
- Toujours appeler `super().closeEvent(event)` **IMMÉDIATEMENT**
- Utiliser `QTimer.singleShot(0, ...)` pour cleanup en arrière-plan
- **Capturer les références** (thread, dialog) avant lambda/fonction interne
- Réduire les timeouts (100ms au lieu de 3000ms)
- Wrapper toutes les opérations I/O dans try/except

#### ❌ À ÉVITER
- `thread.wait(3000)` dans closeEvent (bloque 3 secondes!)
- `event.accept()` sans appeler `super().closeEvent()`
- Utiliser `self.thread` dans lambda (peut être None/détruit)
- Opérations synchrones lourdes (refresh UI, backup) après MessageBox
- Oublier la déconnexion des signaux avant cleanup async

### 🎯 Résultats Attendus
- ✅ Fermeture instantanée au 1er clic (< 100ms)
- ✅ Pas de freeze après import de personnages
- ✅ Cleanup complet en arrière-plan sans bloquer l'utilisateur
- ✅ Pas d'erreurs RuntimeError ou de ressources orphelines

### 📊 Exemple Complet : HeraldSearchDialog

```python
class HeraldSearchDialog(QDialog):
    """Fenêtre de recherche Herald avec fermeture rapide"""
    
    def closeEvent(self, event):
        """Fermeture immédiate + cleanup async"""
        QTimer.singleShot(0, self._async_full_cleanup)
        super().closeEvent(event)
    
    def accept(self):
        """Fermeture via bouton Fermer"""
        self._stop_search_thread_async()
        self._cleanup_temp_files()
        super().accept()
    
    def _async_full_cleanup(self):
        """Cleanup complet non-bloquant"""
        try:
            self._stop_search_thread_async()
            self._cleanup_temp_files()
        except Exception as e:
            logging.warning(f"Erreur cleanup async: {e}")
    
    def _stop_search_thread_async(self):
        """Stop thread sans bloquer (voir code complet ci-dessus)"""
        # ... code du pattern 5 ...
    
    def _import_characters(self, characters):
        """Import avec refresh/backup asynchrones"""
        # ... import sync ...
        
        QMessageBox.information(self, "Import terminé", message)
        
        # Refresh + Backup en arrière-plan
        QTimer.singleShot(100, self.parent().tree_manager.refresh_character_list)
        QTimer.singleShot(200, lambda: self._async_backup(success_count))
```

### 🔍 Debugging
Si la fermeture est toujours lente, ajoutez des logs :
```python
def closeEvent(self, event):
    logging.info("[CLOSE] Début closeEvent")
    QTimer.singleShot(0, self._async_full_cleanup)
    logging.info("[CLOSE] Avant super().closeEvent()")
    super().closeEvent(event)
    logging.info("[CLOSE] Après super().closeEvent()")
```

Chronométrez chaque opération pour identifier les blocages.

---

## 📚 Ressources Complémentaires

- **Planning complet** : `Documentations/PROGRESS_DIALOGS_PLANNING.md`
- **Code source base** : `UI/progress_dialog_base.py`
- **Tests interactifs** : `Tests/test_progress_dialog_base.py`
- **Migration Herald** : `UI/dialogs.py` (SearchThread + HeraldSearchDialog)

---

## ⚠️ Anti-Patterns à Éviter

### ❌ Connexion directe sans wrapper
```python
# DANGEREUX
self.thread.step_started.connect(self.dialog.start_step)
```

### ❌ Terminate sans cleanup
```python
# DANGEREUX
if self.thread.isRunning():
    self.thread.terminate()  # Ressources restent ouvertes !
```

### ❌ Sleep bloquant
```python
# DANGEREUX
time.sleep(10)  # Thread ne répond pas pendant 10s
```

### ❌ Pas de signal rejected
```python
# DANGEREUX
dialog.show()  # Si user ferme → pas de cleanup
```

### ❌ Wait bloquant dans closeEvent
```python
# DANGEREUX - Freeze de 3 secondes !
def closeEvent(self, event):
    if self.thread.isRunning():
        self.thread.wait(3000)  # ⚠️ BLOQUE l'UI !
    super().closeEvent(event)
```

### ❌ Operations lourdes synchrones après MessageBox
```python
# DANGEREUX - UI freeze après la MessageBox
QMessageBox.information(self, "Terminé", "Import OK")
self.refresh_character_list()  # ⚠️ Peut prendre 2-3 secondes !
self.backup_all_characters()   # ⚠️ BLOQUE l'UI !
```

---

## Checklist de Validation

### ✅ Pattern 1 (RuntimeError)
- [ ] Tous les signaux thread → dialog passent par des wrappers
- [ ] Chaque wrapper vérifie `hasattr()` ET `self.progress_dialog`
- [ ] Chaque wrapper enveloppe dans `try/except RuntimeError`

### ✅ Pattern 2 (Cleanup Ressources)
- [ ] Thread a une méthode `cleanup_external_resources()` publique
- [ ] Cleanup appelé AVANT `terminate()` depuis le thread principal
- [ ] Attribut `_external_resource` pour stocker la référence

### ✅ Pattern 3 (Interruption)
- [ ] Thread a un flag `_stop_requested = False`
- [ ] Méthode `request_stop()` pour demander l'arrêt
- [ ] Boucles longues vérifient `if self._stop_requested: return`
- [ ] Sleep remplacés par boucles de 0.5s avec vérification

### ✅ Pattern 4 (Dialog Rejected)
- [ ] Signal `rejected` connecté AVANT `show()` ou `exec()`
- [ ] Handler appelle `_stop_thread()` puis réactive les contrôles
- [ ] Pas de fuite de ressources si dialog fermé prématurément

### ✅ Pattern 5 (Cleanup Asynchrone)
- [ ] `closeEvent()` appelle `super().closeEvent(event)` IMMÉDIATEMENT
- [ ] Cleanup via `QTimer.singleShot(0, self._async_full_cleanup)`
- [ ] Références thread/dialog capturées avant lambda/fonction interne
- [ ] Timeouts réduits (100ms au lieu de 3000ms)
- [ ] Operations I/O lourdes (refresh, backup) via QTimer après MessageBox

---

**Version** : 2.0  
**Dernière mise à jour** : 14 novembre 2025  
**Validé sur** : HeraldSearchDialog (Pattern 1-5 complets)
