# Architecture des Fenêtres de Progression - Réflexion

**Date**: 14 novembre 2025  
**Statut**: 🔄 Réflexion en cours - Non implémenté  
**Objectif**: Uniformiser le design des fenêtres de progression dans l'application

---

## 📋 Contexte

L'application possède actuellement une fenêtre de recherche Herald (`HeraldSearchDialog`) avec un design de progression très élégant et professionnel. L'objectif est d'étendre ce design à toutes les opérations longues de l'application.

### Fenêtre de Référence : `HeraldSearchDialog`

**Points forts du design actuel** :
- ✅ Fenêtre de progression modale avec étapes visuelles
- ✅ Icônes d'état : ⏺️ (en attente) → ⏳ (en cours) → ✅ (terminé)
- ✅ Messages descriptifs pour chaque étape
- ✅ Barre de progression indéterminée (animation continue)
- ✅ Scroll automatique pour les longues listes d'étapes
- ✅ Thread séparé pour éviter le gel de l'interface
- ✅ Signaux `progress_update` pour mise à jour temps réel

**Étapes actuelles de la recherche** (9 étapes) :
1. 🔐 Vérification des cookies d'authentification
2. 🌐 Initialisation du navigateur Chrome
3. 🍪 Chargement des cookies dans le navigateur
4. 🔍 Recherche sur Eden Herald
5. ⏳ Chargement de la page de recherche
6. 📊 Extraction des résultats de recherche
7. 💾 Sauvegarde des résultats
8. 🎯 Formatage des personnages trouvés
9. 🔄 Fermeture du navigateur

---

## 🎯 Cas d'Usage Identifiés

### 1. **Recherche de Personnage** (Existant)
- **Fichier**: `UI/dialogs.py` - `HeraldSearchDialog`
- **Opérations**: Connexion Herald + Recherche + Sauvegarde
- **Particularité**: Design de référence actuel

### 2. **Mise à Jour des Statistiques**
- **Fichier**: `UI/dialogs.py` - `update_rvr_stats()`
- **Opérations**: Connexion Herald + 5 scrapes différents (RvR, PvP, PvE, Wealth, Achievements)
- **Étapes identifiées** :
  1. 🔐 Vérification des cookies
  2. 🌐 Initialisation du navigateur
  3. 🍪 Chargement des cookies
  4. 🏰 Récupération des captures RvR
  5. ⚔️ Récupération des stats PvP
  6. 🐉 Récupération des stats PvE
  7. 💰 Récupération de la richesse
  8. 🏆 Récupération des achievements
  9. 🔄 Fermeture du navigateur
- **Différence**: Même connexion (étapes 1-3), mais scraping multiple au lieu d'une recherche

### 3. **Mise à Jour de Personnage depuis URL**
- **Fonction**: `scrape_character_from_url()`
- **Opérations**: Connexion Herald + Scraping + Comparaison + Sauvegarde
- **Étapes identifiées** :
  1. 🔐 Vérification des cookies
  2. 🌐 Initialisation du navigateur
  3. 🍪 Chargement des cookies
  4. 🔍 Scraping de la page personnage
  5. 📊 Comparaison des données (ancien vs nouveau)
  6. 💾 Application des modifications
  7. 🔄 Fermeture du navigateur
- **Différence**: Connexion Herald + scraping + dialogue de confirmation intermédiaire

### 4. **Génération de Cookies** (Cas Particulier)
- **Fonction**: Cookie Manager
- **Opérations**: Configuration navigateur + Interaction utilisateur + Sauvegarde
- **Étapes identifiées** :
  1. ⚙️ Configuration du navigateur
  2. 🌐 Ouverture de la page de connexion Eden
  3. 👤 **En attente de la connexion utilisateur...** (étape interactive)
  4. 🍪 Extraction des cookies
  5. 💾 Sauvegarde des cookies
  6. ✅ Validation et vérification
- **Différence**: **PAS de connexion Herald** (on génère les cookies), processus **interactif** avec attente utilisateur

### 5. **Récupération Richesse Multi-Royaumes** (Futur)
- **Fonction**: `WealthManager.get_realm_money()`
- **Opérations**: Connexion Herald + Scraping pour 3 royaumes
- **Étapes identifiées** :
  1. 🔐 Vérification des cookies
  2. 🌐 Initialisation du navigateur
  3. 🍪 Chargement des cookies
  4. 🔍 Recherche des personnages par royaume
  5. 🔴 Scraping Albion (si personnage trouvé)
  6. 🔵 Scraping Midgard (si personnage trouvé)
  7. 🟢 Scraping Hibernia (si personnage trouvé)
  8. 💰 Calcul du total
  9. 🔄 Fermeture du navigateur
- **Différence**: Connexion Herald + scraping conditionnel (certains royaumes peuvent être sautés)

---

## 🏗️ Architecture Proposée

### **Composant de Base : `ProgressStepsDialog`**

Création d'un composant réutilisable avec configuration dynamique des étapes.

```python
class ProgressStepsDialog(QDialog):
    """
    Dialogue de progression avec système d'étapes configurables.
    
    Caractéristiques:
    - Liste d'étapes personnalisable
    - Icônes et textes configurables
    - Support des étapes conditionnelles (peuvent être sautées)
    - Mise à jour temps réel via signaux
    - Mode déterminé (pourcentage) ou indéterminé (animation)
    - Gestion des états: pending, running, completed, skipped, error
    """
```

### **Hiérarchie des Classes**

```
┌──────────────────────────────────────────────────────────────┐
│         ProgressStepsDialog (Classe de Base)                 │
│                                                              │
│  Responsabilités:                                            │
│  - Configuration dynamique des étapes                        │
│  - Gestion des icônes d'état (⏺️, ⏳, ✅, ⏭️, ❌)           │
│  - Animation de progression                                  │
│  - Support thread worker                                     │
│  - Émission de signaux (step_updated, all_completed)        │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ Hérite & Configure
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ HeraldSearch   │  │ StatsUpdate    │  │ CookieGen      │
│ ProgressDialog │  │ ProgressDialog │  │ ProgressDialog │
│                │  │                │  │                │
│ 9 étapes       │  │ 9 étapes       │  │ 6 étapes       │
│ Herald search  │  │ Stats scraping │  │ Cookie process │
│ + Thread       │  │ + Thread       │  │ + Interactif   │
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## 💡 Conception Détaillée

### **1. Classe `ProgressStep`**

Représente une étape individuelle dans le processus.

```python
class ProgressStep:
    """
    Représente une étape individuelle.
    
    Attributes:
        icon (str): Emoji représentant l'étape (ex: "🔐", "🌐")
        text (str): Description textuelle
        conditional (bool): Si True, peut être sautée selon le contexte
        category (str): Catégorie ("connection", "scraping", "processing", etc.)
        state (str): État actuel ("pending", "running", "completed", "skipped", "error")
    """
    
    def __init__(self, icon, text, conditional=False, category="general"):
        self.icon = icon
        self.text = text
        self.conditional = conditional
        self.category = category
        self.state = "pending"
```

**États possibles** :
- **pending** (⏺️): En attente, pas encore démarré
- **running** (⏳): En cours d'exécution (texte en gras, bleu)
- **completed** (✅): Terminé avec succès (vert)
- **skipped** (⏭️): Sauté (pour étapes conditionnelles, orange)
- **error** (❌): Échec (rouge)

---

### **2. Classe `StepConfiguration`**

Configurations prédéfinies pour réutiliser des ensembles d'étapes standards.

```python
class StepConfiguration:
    """
    Configurations prédéfinies d'étapes réutilisables.
    """
    
    # Étapes de connexion Herald (communes à beaucoup d'opérations)
    HERALD_CONNECTION = [
        ProgressStep("🔐", "Vérification des cookies d'authentification", category="connection"),
        ProgressStep("🌐", "Initialisation du navigateur Chrome", category="connection"),
        ProgressStep("🍪", "Chargement des cookies dans le navigateur", category="connection"),
    ]
    
    # Étapes de recherche Herald
    HERALD_SEARCH = [
        ProgressStep("🔍", "Recherche sur Eden Herald", category="scraping"),
        ProgressStep("⏳", "Chargement de la page de recherche", category="scraping"),
        ProgressStep("📊", "Extraction des résultats de recherche", category="scraping"),
        ProgressStep("💾", "Sauvegarde des résultats", category="processing"),
        ProgressStep("🎯", "Formatage des personnages trouvés", category="processing"),
    ]
    
    # Étapes de mise à jour stats
    STATS_SCRAPING = [
        ProgressStep("🏰", "Récupération des captures RvR", category="scraping"),
        ProgressStep("⚔️", "Récupération des stats PvP", category="scraping"),
        ProgressStep("🐉", "Récupération des stats PvE", category="scraping"),
        ProgressStep("💰", "Récupération de la richesse", category="scraping"),
        ProgressStep("🏆", "Récupération des achievements", conditional=True, category="scraping"),
    ]
    
    # Étapes de mise à jour personnage
    CHARACTER_UPDATE = [
        ProgressStep("🔍", "Scraping de la page personnage", category="scraping"),
        ProgressStep("📊", "Comparaison des données", category="processing"),
        ProgressStep("💾", "Application des modifications", category="processing"),
    ]
    
    # Étapes de génération de cookies (PAS de connexion Herald)
    COOKIE_GENERATION = [
        ProgressStep("⚙️", "Configuration du navigateur", category="setup"),
        ProgressStep("🌐", "Ouverture de la page de connexion", category="setup"),
        ProgressStep("👤", "En attente de la connexion utilisateur...", category="interactive"),
        ProgressStep("🍪", "Extraction des cookies", category="processing"),
        ProgressStep("💾", "Sauvegarde des cookies", category="processing"),
        ProgressStep("✅", "Validation et vérification", category="processing"),
    ]
    
    # Étape de fermeture (commune)
    CLEANUP = [
        ProgressStep("🔄", "Fermeture du navigateur", category="cleanup"),
    ]
    
    @classmethod
    def build_steps(cls, *step_groups):
        """
        Construit une liste d'étapes en combinant plusieurs groupes.
        
        Example:
            steps = StepConfiguration.build_steps(
                StepConfiguration.HERALD_CONNECTION,
                StepConfiguration.HERALD_SEARCH,
                StepConfiguration.CLEANUP
            )
        """
        combined = []
        for group in step_groups:
            combined.extend(group)
        return combined
```

---

### **3. Classe `ProgressStepsDialog` (Composant de Base)**

```python
class ProgressStepsDialog(QDialog):
    """
    Dialogue de progression avec système d'étapes visuelles configurables.
    
    Signals:
        step_updated: Émis quand une étape change d'état (step_index, new_state)
        all_completed: Émis quand toutes les étapes sont terminées
        canceled: Émis si l'utilisateur annule
    """
    
    step_updated = pyqtSignal(int, str)  # (step_index, new_state)
    all_completed = pyqtSignal()
    canceled = pyqtSignal()
    
    def __init__(self, parent, title, steps, description=None, 
                 show_progress_bar=True, determinate_progress=False, 
                 allow_cancel=False):
        """
        Args:
            parent: Widget parent
            title (str): Titre de la fenêtre (ex: "🔍 Recherche en cours...")
            steps (list[ProgressStep]): Liste des étapes à afficher
            description (str, optional): Description supplémentaire
            show_progress_bar (bool): Afficher la barre de progression
            determinate_progress (bool): Mode déterminé (avec %) ou indéterminé (animation)
            allow_cancel (bool): Permettre l'annulation
        """
```

**Méthodes principales** :

```python
def update_step(self, step_index, state, custom_message=None):
    """
    Met à jour l'état d'une étape.
    
    Args:
        step_index (int): Index de l'étape (0-based)
        state (str): Nouvel état ("pending", "running", "completed", "skipped", "error")
        custom_message (str, optional): Message personnalisé pour le status_label
    """

def start_step(self, step_index):
    """Démarre une étape (marque comme "running")."""

def complete_step(self, step_index):
    """Termine une étape avec succès."""

def skip_step(self, step_index, reason=None):
    """Saute une étape conditionnelle."""

def error_step(self, step_index, error_message=None):
    """Marque une étape comme échouée."""

def complete_all(self, success_message="✅ Opération terminée avec succès !"):
    """Marque toutes les étapes comme terminées."""

def set_status_message(self, message, color=None):
    """Change le message de statut."""
```

---

## 📊 Exemples d'Utilisation

### **Exemple 1 : Recherche Herald**

```python
from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration

# Construire les étapes
steps = StepConfiguration.build_steps(
    StepConfiguration.HERALD_CONNECTION,
    StepConfiguration.HERALD_SEARCH,
    StepConfiguration.CLEANUP
)

# Créer le dialogue
progress_dialog = ProgressStepsDialog(
    parent=self,
    title="🔍 Recherche en cours...",
    steps=steps,
    description=f"Recherche de '{character_name}' sur Eden Herald...",
    show_progress_bar=True,
    determinate_progress=False,  # Animation continue
    allow_cancel=False
)

# Afficher le dialogue
progress_dialog.show()

# Dans le thread worker, émettre des signaux pour mettre à jour
# Via signal progress_update qui appelle:
progress_dialog.start_step(0)  # Démarre "Vérification cookies"
progress_dialog.complete_step(0)  # Termine "Vérification cookies"
progress_dialog.start_step(1)  # Démarre "Initialisation navigateur"
# ... etc
```

### **Exemple 2 : Mise à Jour Stats**

```python
# Construire les étapes
steps = StepConfiguration.build_steps(
    StepConfiguration.HERALD_CONNECTION,
    StepConfiguration.STATS_SCRAPING,
    StepConfiguration.CLEANUP
)

progress_dialog = ProgressStepsDialog(
    parent=self,
    title="📊 Mise à jour des statistiques...",
    steps=steps,
    show_progress_bar=True,
    determinate_progress=True,  # Affiche le pourcentage
    allow_cancel=False
)

# Si achievements échoue (conditionnel), on peut le sauter:
if not achievements_result['success']:
    progress_dialog.skip_step(7, reason="Achievements non disponibles")
```

### **Exemple 3 : Génération Cookies**

```python
# Construire les étapes (PAS de connexion Herald)
steps = StepConfiguration.COOKIE_GENERATION.copy()

progress_dialog = ProgressStepsDialog(
    parent=self,
    title="🍪 Génération des cookies...",
    steps=steps,
    description="Veuillez vous connecter manuellement dans le navigateur qui va s'ouvrir.",
    show_progress_bar=True,
    determinate_progress=False,
    allow_cancel=True  # Annulation possible
)

# L'étape 2 (👤 Attente utilisateur) reste en "running" pendant que l'utilisateur se connecte
progress_dialog.start_step(2)
progress_dialog.set_status_message(
    "⏳ En attente de votre connexion dans le navigateur...",
    color="#FF9800"
)
```

### **Exemple 4 : Richesse Multi-Royaumes**

```python
# Construire les étapes
connection_steps = StepConfiguration.HERALD_CONNECTION
realm_steps = [
    ProgressStep("🔴", "Scraping Albion", conditional=True, category="scraping"),
    ProgressStep("🔵", "Scraping Midgard", conditional=True, category="scraping"),
    ProgressStep("🟢", "Scraping Hibernia", conditional=True, category="scraping"),
    ProgressStep("💰", "Calcul du total", category="processing"),
]
cleanup_steps = StepConfiguration.CLEANUP

steps = connection_steps + realm_steps + cleanup_steps

progress_dialog = ProgressStepsDialog(
    parent=self,
    title="💰 Récupération de la richesse...",
    steps=steps,
    show_progress_bar=True,
    determinate_progress=True
)

# Si aucun personnage Hibernia trouvé:
if not hibernia_character:
    progress_dialog.skip_step(5, reason="Aucun personnage Hibernia trouvé")
```

---

## 🎨 Codes Couleurs et Icônes

### **États des Étapes**

| État | Icône | Couleur | Style | Signification |
|------|-------|---------|-------|---------------|
| **pending** | ⏺️ | `#888` (gris) | Normal | En attente, pas encore démarré |
| **running** | ⏳ | `#2196F3` (bleu) | **Gras** | En cours d'exécution |
| **completed** | ✅ | `#4CAF50` (vert) | Normal | Terminé avec succès |
| **skipped** | ⏭️ | `#FF9800` (orange) | Italique | Sauté (conditionnel) |
| **error** | ❌ | `#F44336` (rouge) | Normal | Échec |

### **Icônes par Catégorie**

| Catégorie | Icônes Suggérées |
|-----------|------------------|
| **Connection** | 🔐 (cookies), 🌐 (navigateur), 🍪 (chargement cookies) |
| **Scraping** | 🔍 (recherche), 📊 (extraction), 🏰 (RvR), ⚔️ (PvP), 🐉 (PvE) |
| **Processing** | 💾 (sauvegarde), 🎯 (formatage), 📊 (comparaison), 💰 (calcul) |
| **Setup** | ⚙️ (configuration), 🌐 (ouverture page) |
| **Interactive** | 👤 (attente utilisateur), ⌨️ (saisie manuelle) |
| **Cleanup** | 🔄 (fermeture), 🧹 (nettoyage) |
| **Realm** | 🔴 (Albion), 🔵 (Midgard), 🟢 (Hibernia) |

---

## 🔄 Workflow de Mise à Jour

### **Séquence Typique**

1. **Création du dialogue**
   ```python
   progress_dialog = ProgressStepsDialog(parent, title, steps)
   progress_dialog.show()
   ```

2. **Démarrage du thread worker**
   ```python
   worker_thread = WorkerThread(...)
   worker_thread.progress_update.connect(on_progress_update)
   worker_thread.start()
   ```

3. **Mise à jour depuis le thread**
   ```python
   def on_progress_update(self, message):
       # Parser le message pour déterminer l'étape
       if message.startswith("🔐"):
           self.progress_dialog.start_step(0)
       elif message.startswith("🌐"):
           self.progress_dialog.complete_step(0)
           self.progress_dialog.start_step(1)
       # ... etc
   ```

4. **Complétion**
   ```python
   def on_operation_finished(self, success, message):
       if success:
           self.progress_dialog.complete_all("✅ Opération terminée !")
       else:
           self.progress_dialog.error_step(current_step, message)
       
       # Fermer après 1 seconde
       QTimer.singleShot(1000, self.progress_dialog.accept)
   ```

---

## 📝 Avantages de cette Architecture

### **1. Réutilisabilité**
- ✅ Un seul composant pour toutes les opérations longues
- ✅ Configurations prédéfinies réutilisables
- ✅ Facile d'ajouter de nouvelles opérations

### **2. Cohérence Visuelle**
- ✅ Design uniforme dans toute l'application
- ✅ Codes couleurs standardisés
- ✅ Comportement prévisible pour l'utilisateur

### **3. Maintenabilité**
- ✅ Code centralisé, facile à modifier
- ✅ Ajout d'étapes simple (juste ajouter à la config)
- ✅ Debug facilité (logs centralisés)

### **4. Flexibilité**
- ✅ Support des étapes conditionnelles
- ✅ Mode déterminé ou indéterminé
- ✅ Annulation possible ou non
- ✅ Messages personnalisables

### **5. Extensibilité**
- ✅ Facile d'ajouter de nouveaux états
- ✅ Support de catégories personnalisées
- ✅ Signaux pour intégration avec threads

---

## 🚧 Migration Progressive

### **Phase 1 : Création du Composant**
1. Créer `UI/progress_dialog_base.py` avec les classes de base
2. Tester avec un cas simple (ex: génération cookies)

### **Phase 2 : Migration HeraldSearchDialog**
1. Adapter `HeraldSearchDialog` pour utiliser `ProgressStepsDialog`
2. Conserver l'ancien code en commentaire pendant les tests
3. Valider que tout fonctionne identiquement

### **Phase 3 : Extension aux Autres Dialogues**
1. Migrer `update_rvr_stats()` → `StatsUpdateProgressDialog`
2. Migrer Cookie Manager → `CookieGenProgressDialog`
3. Migrer `scrape_character_from_url()` → `CharacterUpdateProgressDialog`

### **Phase 4 : Nouvelles Fonctionnalités**
1. Ajouter `WealthManagerProgressDialog` pour richesse multi-royaumes
2. Utiliser pour toute nouvelle opération longue

---

## 📂 Structure de Fichiers Proposée

```
UI/
├── progress_dialog_base.py          # ✨ NOUVEAU - Classes de base
│   ├── ProgressStep                 # Classe étape
│   ├── StepConfiguration            # Configurations prédéfinies
│   └── ProgressStepsDialog          # Dialogue de base
│
├── progress_dialogs.py              # ✨ NOUVEAU - Dialogues spécialisés
│   ├── HeraldSearchProgressDialog   # Spécialisé pour recherche Herald
│   ├── StatsUpdateProgressDialog    # Spécialisé pour mise à jour stats
│   ├── CookieGenProgressDialog      # Spécialisé pour génération cookies
│   ├── CharacterUpdateProgressDialog # Spécialisé pour mise à jour personnage
│   └── WealthManagerProgressDialog  # Spécialisé pour richesse multi-royaumes
│
└── dialogs.py                       # Dialogues existants (à migrer progressivement)
```

---

## 🎯 TODO List pour Implémentation Future

- [ ] **Phase 1 : Base**
  - [ ] Créer `UI/progress_dialog_base.py` (✅ Déjà créé en brouillon)
  - [ ] Implémenter `ProgressStep` class
  - [ ] Implémenter `StepConfiguration` class
  - [ ] Implémenter `ProgressStepsDialog` base class
  - [ ] Tests unitaires des classes de base

- [ ] **Phase 2 : Premier Cas d'Usage**
  - [ ] Choisir le cas le plus simple (probablement Cookie Generation)
  - [ ] Créer le dialogue spécialisé
  - [ ] Intégrer avec le code existant
  - [ ] Tests utilisateur

- [ ] **Phase 3 : Migration HeraldSearch**
  - [ ] Créer `HeraldSearchProgressDialog` en utilisant la base
  - [ ] Adapter le thread de recherche pour émettre les bons signaux
  - [ ] Remplacer l'ancien code
  - [ ] Validation complète

- [ ] **Phase 4 : Stats Update**
  - [ ] Créer `StatsUpdateProgressDialog`
  - [ ] Refactoriser `update_rvr_stats()` pour utiliser le nouveau dialogue
  - [ ] Gérer les étapes conditionnelles (achievements)
  - [ ] Tests

- [ ] **Phase 5 : Autres Dialogues**
  - [ ] `CharacterUpdateProgressDialog`
  - [ ] `WealthManagerProgressDialog`
  - [ ] Autres futurs besoins

- [ ] **Phase 6 : Documentation**
  - [ ] Guide développeur pour créer un nouveau dialogue de progression
  - [ ] Exemples de code
  - [ ] Best practices

---

## 📚 Références

### **Fichiers Concernés (à modifier lors de l'implémentation)**

- `UI/dialogs.py` - Ligne 3310 : `HeraldSearchDialog` (référence actuelle)
- `UI/dialogs.py` - Ligne 1267 : `update_rvr_stats()` (à migrer)
- `Functions/character_profile_scraper.py` - Scraping stats (worker thread)
- `Functions/cookie_manager.py` - Génération cookies (worker thread)
- `Functions/wealth_manager.py` - Richesse multi-royaumes (futur)

### **Inspirations Design**

- Material Design Progress Indicators
- macOS Activity Dialog
- Windows Task Progress Dialog
- VS Code Extension Installation Progress

---

## ⚠️ Points d'Attention

### **1. Thread Safety**
- ⚠️ Tous les appels à `update_step()` doivent être thread-safe
- ⚠️ Utiliser `QMetaObject.invokeMethod()` si appelé depuis un thread
- ⚠️ Ou émettre des signaux et les connecter aux slots du dialogue

### **2. Performance**
- ⚠️ Éviter trop d'appels `QApplication.processEvents()` (peut ralentir)
- ⚠️ Limiter la fréquence de mise à jour (max 10-20 Hz)
- ⚠️ Grouper les mises à jour si possible

### **3. UX**
- ⚠️ Ne pas afficher trop d'étapes (max 10-12, sinon scroll)
- ⚠️ Messages clairs et concis (max 60 caractères)
- ⚠️ Toujours fermer le dialogue automatiquement après complétion

### **4. Gestion d'Erreurs**
- ⚠️ Bien gérer les étapes qui échouent
- ⚠️ Permettre de voir les logs détaillés en cas d'erreur
- ⚠️ Offrir des options de retry si pertinent

---

## 🔮 Évolutions Futures Possibles

### **V2 : Features Avancées**
- 📊 Graphique de progression circulaire
- 🎨 Thèmes personnalisables (dark mode, light mode)
- 📝 Export des logs de progression
- 🔊 Notifications sonores à la fin
- ⏱️ Estimation du temps restant

### **V3 : Intelligence**
- 🤖 Détection automatique des étapes à partir des logs
- 📈 Statistiques de performance (temps moyen par étape)
- 🔄 Retry automatique en cas d'erreur réseau
- 💡 Suggestions d'optimisation

---

**Document de Réflexion - Non Implémenté**  
**À réviser avant implémentation**  
**Version 1.0 - 14 novembre 2025**
