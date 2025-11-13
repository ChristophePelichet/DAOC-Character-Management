# Workflow Complet de Fonctionnalité

Instructions pour le développement complet d'une fonctionnalité avec gestion automatique des traductions et du changelog.

**Contexte :**
* Ce workflow combine la gestion des traductions multilingues ET la documentation dans le changelog
* À utiliser lors de l'ajout ou modification de fonctionnalités complètes
* Toutes les étapes sont appliquées automatiquement

---

## 🌍 PARTIE 1 : TRADUCTIONS MULTILINGUES

### Règles Automatiques de Traduction

**Langues supportées** : Français (FR), Anglais (EN), Allemand (DE)

**Fichiers** : `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Application Automatique
Pour TOUT texte visible par l'utilisateur :
- ✅ Créer/modifier automatiquement dans les 3 fichiers JSON
- ✅ Utiliser des clés descriptives en snake_case
- ✅ Fournir des traductions de qualité adaptées au contexte DAOC
- ✅ Ne JAMAIS demander confirmation pour les traductions

### Exemples de Traductions Courantes

**Boutons :**
- FR : "Nouveau" / EN : "New" / DE : "Neu"
- FR : "Modifier" / EN : "Edit" / DE : "Bearbeiten"
- FR : "Supprimer" / EN : "Delete" / DE : "Löschen"
- FR : "Rechercher" / EN : "Search" / DE : "Suchen"

**Messages :**
- FR : "Succès" / EN : "Success" / DE : "Erfolg"
- FR : "Erreur" / EN : "Error" / DE : "Fehler"
- FR : "Confirmation" / EN : "Confirmation" / DE : "Bestätigung"

**Termes DAOC (ne pas traduire) :**
- Albion, Hibernia, Midgard, Herald, Eden, RvR, PvP, PvE

---

## 📝 PARTIE 2 : DOCUMENTATION CHANGELOG

### Format Standard

Utiliser la structure à 4 sections avec émojis contextuels :

#### 🎉 Ajout
Nouvelles fonctionnalités ajoutées dans cette version

#### 🧰 Modification
Modifications apportées aux fonctionnalités existantes

#### 🐛 Correction
Bugs corrigés dans cette version

#### 🔚 Retrait
Fonctionnalités supprimées dans cette version

### Règles de Documentation

**Pour chaque modification :**
- ✅ Ajouter une ligne avec emoji contextuel approprié
- ✅ Description claire et concise en français
- ✅ Mentionner les fichiers impactés si pertinent
- ✅ Regrouper les changements liés ensemble

**Emojis contextuels à utiliser :**
- 🔄 Vérification / Actualisation
- 📊 Données / Statistiques
- 🌐 Web / Réseau
- 🔘 Boutons / UI
- ✅ Validation / Indicateurs
- 🔗 Liens
- ℹ️ Informations
- 🌍 Traductions
- 📝 Modules / Scripts
- 🎨 Styles / Design
- 📁 Fichiers / Dossiers
- 🐛 Bugs / Corrections
- 🗑️ Suppression
- 🧹 Nettoyage / Optimisation

### Localisation du Changelog

**Versions disponibles :**
- 📝 Simple : `Changelogs/CHANGELOG_SIMPLE_FR.md` et `CHANGELOG_SIMPLE_EN.md`
- 📚 Full : `Changelogs/CHANGELOG_FR.md` et `CHANGELOG_EN.md`

**Fichier principal** : `CHANGELOG.md` (racine du projet)

---

## 🔄 WORKFLOW D'EXÉCUTION

Lors de l'ajout/modification d'une fonctionnalité :

### Étape 1 : Implémentation
- Développer la fonctionnalité demandée
- Appliquer les bonnes pratiques du projet
- Tester la fonctionnalité

### Étape 2 : Traductions Automatiques
- Identifier TOUS les textes visibles par l'utilisateur
- Créer/modifier les clés dans `Language/*.json` (FR/EN/DE)
- Utiliser des clés descriptives en snake_case
- Vérifier la cohérence des traductions
- Ne PAS traduire les termes DAOC (Albion, Herald, RvR, etc.)

### Étape 3 : Documentation Changelog
- Déterminer la section appropriée (Ajout/Modification/Correction/Retrait)
- Mettre à jour `Changelogs/CHANGELOG_FR.md` (version Full)
- Mettre à jour `Changelogs/CHANGELOG_EN.md` (version Full)
- Mettre à jour `Changelogs/CHANGELOG_SIMPLE_FR.md`
- Mettre à jour `Changelogs/CHANGELOG_SIMPLE_EN.md`
- Mettre à jour `CHANGELOG.md` racine avec liens vers la nouvelle version
- Utiliser les emojis contextuels appropriés

### Étape 4 : Git Commit & Push (AUTOMATIQUE)
- **EXÉCUTER IMMÉDIATEMENT** `git add -A` pour ajouter tous les fichiers modifiés
- **EXÉCUTER IMMÉDIATEMENT** le commit structuré en anglais (voir PARTIE 3)
- Utiliser le type conventionnel approprié (feat/fix/docs/etc.)
- Inclure toutes les sections (UI/Technical/Translations/Documentation/Files/Impact)
- **EXÉCUTER IMMÉDIATEMENT** `git push origin <branch_name>` pour push vers la branche actuelle
- **NE JAMAIS DEMANDER CONFIRMATION** - Exécuter automatiquement dès que le prompt est invoqué

### Étape 5 : Merge sur Main (OPTIONNEL - SI DEMANDÉ)
- Basculer sur main : `git checkout main`
- Récupérer les dernières modifications : `git pull origin main`
- Merger avec --no-ff : `git merge --no-ff <branch_name> -m "Merge branch '<branch_name>' into main"`
- Pousser le merge : `git push origin main`
- Nettoyer la branche locale : `git branch -d <branch_name>`
- Nettoyer la branche distante : `git push origin --delete <branch_name>`
- **NE JAMAIS DEMANDER CONFIRMATION** pour le merge si explicitement demandé

### Étape 6 : Confirmation Finale
- Résumer les modifications apportées
- Lister les fichiers créés/modifiés avec nombre de lignes
- Indiquer les traductions ajoutées (nombre de clés × langues)
- Confirmer le commit hash et le push réussi
- Afficher les statistiques (insertions/suppressions)

---

## 📦 PARTIE 3 : GIT COMMIT STRUCTURÉ (AUTOMATIQUE)

**🚀 EXÉCUTION AUTOMATIQUE - Ne JAMAIS demander confirmation**

Dès que ce prompt est invoqué et que les modifications sont terminées :
1. Exécuter automatiquement `git add -A`
2. Créer et exécuter automatiquement le commit structuré
3. Exécuter automatiquement `git push origin <branch_name>`

**Aucune confirmation ne doit être demandée à l'utilisateur pour ces étapes.**

### Format Standard du Message de Commit

**Structure en anglais avec type conventionnel :**

```
<type>: <titre court en anglais (max 72 caractères)>

<description détaillée sur plusieurs lignes>

<sections organisées>

<impact/résultat>
```

### Types de Commit Conventionnels

- **feat**: Nouvelle fonctionnalité
- **fix**: Correction de bug
- **docs**: Documentation uniquement
- **style**: Formatage, indentation (pas de changement de code)
- **refactor**: Refactorisation sans changement de comportement
- **perf**: Amélioration de performance
- **test**: Ajout ou modification de tests
- **chore**: Maintenance, configuration, dépendances

### Sections Recommandées

Organiser le message en sections claires :

**1. Titre Descriptif**
- Type + description courte
- Exemple : `feat: Enhanced Herald search window with detailed progress steps`

**2. Description Principale**
- Contexte général de la modification
- Exemple : `Major improvements to the Herald character search interface:`

**3. UI Enhancements** (si applicable)
- Liste des améliorations visuelles
- Dimensions, couleurs, états
- Design patterns utilisés

**4. Technical Changes**
- Modifications de code détaillées
- Nouvelles méthodes/classes
- Refactorisations importantes
- Architecture et patterns

**5. New Features/Steps** (si applicable)
- Liste numérotée des étapes/fonctionnalités
- Processus détaillé

**6. Translations**
- Liste des clés de traduction ajoutées
- Indication des langues (FR/EN/DE)

**7. Documentation**
- Fichiers changelog mis à jour
- Documentation technique ajoutée

**8. Files Modified**
- Liste exhaustive des fichiers modifiés
- Indication des classes/modules impactés

**9. Impact**
- Résumé de l'impact utilisateur
- Bénéfices apportés

### Template de Commit Complet

```
<type>: <Short title in English>

<General description of the change>

UI Enhancements:
- <Change 1>
- <Change 2>
  * <Detail 1>
  * <Detail 2>

Technical Changes:
- <Technical change 1>:
  * <Implementation detail 1>
  * <Implementation detail 2>
- <Technical change 2>

<Section spécifique si nécessaire>:
1. <Item 1>
2. <Item 2>

Translations:
- Added <X> new translation keys in FR/EN/DE:
  * <key_1>
  * <key_2>

Documentation:
- Updated <file1> with <change>
- Updated <file2> with <change>

Files Modified:
- <file1> (<description>)
- <file2> (<description>)

Impact: <User impact summary>
```

### Exemple Concret

```
feat: Enhanced Herald search window with detailed progress steps and visual status indicators

Major improvements to the Herald character search interface:

UI Enhancements:
- Redesigned progress window (550x350px) with 9 detailed steps
- Added 3-state visual status system:
  * ⏺️ Waiting (gray): Step not started yet
  * ⏳ In Progress (blue): Currently executing with bold text
  * ✅ Completed (green): Successfully finished
- All steps remain visible throughout the search process
- Steps automatically update as progress advances
- Grouped progress area in QGroupBox for better organization
- Consistent design with 'Update from Herald' window

Technical Changes:
- Refactored SearchThread in UI/dialogs.py:
  * Added progress_update signal for real-time updates
  * Integrated all search logic into thread (previously in eden_scraper.py)
  * Emits progress messages at each key step
  * Clean browser closure in finally block
- New _on_search_progress_update() method:
  * Automatic step detection via icon mapping
  * Automatic marking of previous steps as completed
  * Special handling for final success message
  * Font scaling support via _get_scaled_size()
- Added helper method _get_scaled_size() for font scaling

Search Progress Steps (9 total):
1. 🔐 Checking authentication cookies
2. 🌐 Initializing Chrome browser
3. 🍪 Loading cookies into browser
4. 🔍 Searching on Eden Herald
5. ⏳ Loading search page
6. 📊 Extracting search results
7. 💾 Saving results
8. 🎯 Formatting found characters
9. 🔄 Closing browser

Translations:
- Added 13 new translation keys in FR/EN/DE:
  * herald_search_progress_title
  * herald_search_progress_checking_cookies
  * herald_search_progress_init_browser
  * herald_search_progress_loading_cookies
  * herald_search_progress_searching
  * herald_search_progress_loading_page
  * herald_search_progress_extracting
  * herald_search_progress_saving
  * herald_search_progress_formatting
  * herald_search_progress_complete
  * herald_search_progress_closing
  * herald_search_wait_message

Documentation:
- Updated CHANGELOG_FR.md with v0.108 section
- Updated CHANGELOG_EN.md with v0.108 section
- Updated CHANGELOG_SIMPLE_FR.md with v0.108 section
- Updated CHANGELOG_SIMPLE_EN.md with v0.108 section
- Updated CHANGELOG.md root with quick links to v0.108

Files Modified:
- UI/dialogs.py (SearchThread and HeraldSearchDialog classes)
- Language/fr.json, en.json, de.json
- Changelogs/*.md (4 files + root CHANGELOG.md)

Impact: Greatly improved user experience with complete visual feedback during Herald searches. Users now see the status of all steps instead of a simple 'Searching...' message.
```

### Commandes Git Automatiques

```bash
# Étape 1 : Ajouter tous les fichiers modifiés
git add -A

# Étape 2 : Commit avec message structuré
git commit -m "<type>: <titre>" -m "<corps du message>"
# OU utiliser un éditeur pour message multiligne
git commit

# Étape 3 : Push vers la branche actuelle
git push origin $(git branch --show-current)
# OU explicitement
git push origin <branch_name>
```

### Bonnes Pratiques

**À FAIRE :**
- ✅ Utiliser l'anglais pour tout le message de commit
- ✅ Première ligne max 72 caractères
- ✅ Sauter une ligne entre titre et corps
- ✅ Utiliser des listes à puces pour la lisibilité
- ✅ Indenter les sous-détails avec des astérisques
- ✅ Inclure les emojis dans les listes d'étapes (améliore la lecture)
- ✅ Être spécifique sur les fichiers et méthodes modifiés
- ✅ Toujours inclure la section "Impact" en fin de message
- ✅ Mentionner toutes les traductions ajoutées
- ✅ Lister les changelogs mis à jour

**À ÉVITER :**
- ❌ Messages vagues ("fix stuff", "update code")
- ❌ Mélanger français et anglais
- ❌ Oublier de mentionner les traductions
- ❌ Omettre les fichiers de documentation modifiés
- ❌ Ne pas indiquer l'impact utilisateur

---

## 📋 CHECKLIST DE VALIDATION

Avant de finaliser, vérifier :

**Code :**
- [ ] Fonctionnalité implémentée et testée
- [ ] Pas de textes hardcodés dans le code
- [ ] Pas d'erreurs de syntaxe ou d'imports
- [ ] Code suit les conventions du projet

**Traductions :**
- [ ] Tous les textes UI traduits en FR/EN/DE
- [ ] Clés JSON cohérentes dans les 3 fichiers
- [ ] Clés en snake_case descriptives
- [ ] Termes DAOC non traduits (Albion, Herald, etc.)

**Documentation :**
- [ ] CHANGELOG_FR.md mis à jour (version Full)
- [ ] CHANGELOG_EN.md mis à jour (version Full)
- [ ] CHANGELOG_SIMPLE_FR.md mis à jour
- [ ] CHANGELOG_SIMPLE_EN.md mis à jour
- [ ] CHANGELOG.md racine mis à jour avec liens
- [ ] Emojis contextuels appropriés utilisés
- [ ] Section correcte (Ajout/Modification/Correction/Retrait)

**Git Commit (AUTOMATIQUE) :**
- [ ] `git add -A` **EXÉCUTÉ AUTOMATIQUEMENT**
- [ ] Message de commit structuré en anglais **CRÉÉ ET EXÉCUTÉ AUTOMATIQUEMENT**
- [ ] Type conventionnel correct (feat/fix/docs/etc.)
- [ ] Sections organisées (UI/Technical/Translations/etc.)
- [ ] Tous les fichiers modifiés listés
- [ ] Impact utilisateur décrit
- [ ] `git push origin <branch>` **EXÉCUTÉ AUTOMATIQUEMENT**

**Merge (SI DEMANDÉ) :**
- [ ] Checkout sur main exécuté
- [ ] Pull origin main exécuté
- [ ] Merge --no-ff exécuté
- [ ] Push origin main exécuté
- [ ] Branche locale supprimée
- [ ] Branche distante supprimée

---

## 🎯 EXEMPLE COMPLET DE WORKFLOW

**Demande utilisateur** : "Ajoute un bouton pour exporter tous les personnages en CSV"

### Actions Automatiques Exécutées :

#### 1. **Code** - Implémentation
```python
# UI/dialogs.py
export_button = QPushButton(lang.get("export_all_button"))
export_button.clicked.connect(self.export_all_to_csv)

def export_all_to_csv(self):
    # Fonction d'export avec gestion des erreurs
    try:
        # ... code d'export ...
        QMessageBox.information(self, lang.get("success_title"), lang.get("export_success"))
    except Exception as e:
        QMessageBox.critical(self, lang.get("error_title"), f"{lang.get('export_error')}: {str(e)}")
```

#### 2. **Traductions** - 3 langues (FR/EN/DE)
```json
// Language/fr.json
"export_all_button": "📤 Exporter Tout",
"export_success": "Export CSV réussi ! {count} personnages exportés.",
"export_error": "Erreur lors de l'export"

// Language/en.json
"export_all_button": "📤 Export All",
"export_success": "CSV export successful! {count} characters exported.",
"export_error": "Export error"

// Language/de.json
"export_all_button": "📤 Alles Exportieren",
"export_success": "CSV-Export erfolgreich! {count} Charaktere exportiert.",
"export_error": "Exportfehler"
```

#### 3. **Changelog** - 4 fichiers + racine
```markdown
# Changelogs/CHANGELOG_FR.md
## v0.109 - 2025-11-13

### 🎉 Ajout
- 📤 Bouton "Exporter Tout" pour export CSV de tous les personnages
- 💾 Fonction d'export avec gestion des erreurs et confirmation
- 📊 Format CSV avec toutes les colonnes configurables
- 🌍 Traductions complètes FR/EN/DE (3 nouvelles clés)
```

#### 4. **Git Commit** - Message structuré
```
feat: Add CSV export functionality for all characters

Added export button and comprehensive CSV export feature for bulk character data export.

UI Enhancements:
- New "Export All" button in main toolbar
- Export success message with character count
- Error handling with user-friendly messages

Technical Changes:
- New export_all_to_csv() method in CharacterApp class
- CSV writer with configurable column selection
- Error handling for file access and write permissions
- Integration with existing language system

Translations:
- Added 3 new translation keys in FR/EN/DE:
  * export_all_button
  * export_success
  * export_error

Documentation:
- Updated CHANGELOG_FR.md with v0.109 section
- Updated CHANGELOG_EN.md with v0.109 section
- Updated CHANGELOG_SIMPLE_FR.md with v0.109 section
- Updated CHANGELOG_SIMPLE_EN.md with v0.109 section
- Updated CHANGELOG.md root with quick links to v0.109

Files Modified:
- UI/dialogs.py (CharacterApp class - export functionality)
- Language/fr.json, en.json, de.json
- Changelogs/*.md (4 files + root CHANGELOG.md)

Impact: Users can now export all character data to CSV format with a single click, enabling external data analysis and backup capabilities.
```

#### 5. **Commandes Git Exécutées (AUTOMATIQUEMENT)**
```bash
# EXÉCUTÉ AUTOMATIQUEMENT - Pas de confirmation demandée
git add -A
git commit -m "feat: Add CSV export functionality for all characters" -m "<message body>"
git push origin 109_Add_CSV_Export
```

#### 6. **Merge sur Main (SI DEMANDÉ)**
```bash
# EXÉCUTÉ AUTOMATIQUEMENT si l'utilisateur demande le merge
git checkout main
git pull origin main
git merge --no-ff 109_Add_CSV_Export -m "Merge branch '109_Add_CSV_Export' into main"
git push origin main
git branch -d 109_Add_CSV_Export
git push origin --delete 109_Add_CSV_Export
```

#### 7. **Confirmation Finale**
```
✅ Fonctionnalité Implémentée - CSV Export

📦 Fichiers Modifiés (3) :
- UI/dialogs.py (+45 lines)
- Language/fr.json, en.json, de.json (+3 keys × 3 = 9 entries)
- Changelogs/*.md (5 files updated)

🌍 Traductions Ajoutées :
- 3 clés × 3 langues = 9 entrées totales

📊 Statistiques Git :
- Commit: a1b2c3d
- +54 insertions, -0 deletions
- Push: ✅ Réussi vers 109_Add_CSV_Export

🎯 Impact : Les utilisateurs peuvent exporter tous leurs personnages en CSV en un clic
```

---

## 🔀 PARTIE 4 : MERGE SUR MAIN (SI DEMANDÉ)

### Quand Exécuter le Merge

Le merge est exécuté **UNIQUEMENT** si l'utilisateur le demande explicitement avec des termes comme :
- "merge"
- "fusionner sur main"
- "intégrer dans main"
- Référence au fichier merge.prompt.md

### Processus de Merge Automatique

**Aucune confirmation ne doit être demandée - Exécuter automatiquement :**

1. **Basculer sur main** :
   ```bash
   git checkout main
   ```

2. **Récupérer les dernières modifications** :
   ```bash
   git pull origin main
   ```

3. **Merger avec --no-ff** (préserve l'historique de la branche) :
   ```bash
   git merge --no-ff <branch_name> -m "Merge branch '<branch_name>' into main"
   ```

4. **Pousser le merge** :
   ```bash
   git push origin main
   ```

5. **Nettoyer la branche locale** :
   ```bash
   git branch -d <branch_name>
   ```

6. **Nettoyer la branche distante** :
   ```bash
   git push origin --delete <branch_name>
   ```

### Confirmation Post-Merge

Après le merge, afficher :
- ✅ Branche mergée sur main avec commit hash
- ✅ Statistiques du merge (fichiers, insertions, suppressions)
- ✅ Confirmation de la suppression des branches (locale + distante)

---

## ⚡ RÈGLES D'AUTOMATISATION

**IMPORTANT - À respecter systématiquement :**

1. **Ne JAMAIS demander confirmation** pour :
   - Les traductions (toujours FR/EN/DE automatiquement)
   - La mise à jour des changelogs (toujours 4 fichiers + racine)
   - Le format du commit (toujours structuré en anglais)
   - **L'exécution de `git add -A`, `git commit`, `git push`** (AUTOMATIQUE dès invocation du prompt)
   - **Le processus de merge complet** (AUTOMATIQUE si explicitement demandé)

2. **Toujours inclure** :
   - Les 3 langues pour chaque texte UI
   - Les 5 fichiers changelog (4 détaillés + 1 racine)
   - Le commit structuré complet avec toutes les sections
   - Le push automatique vers la branche
   - **L'exécution immédiate de Git add/commit/push**

3. **Toujours vérifier** :
   - Cohérence des clés JSON entre les 3 fichiers
   - Emojis contextuels appropriés dans les changelogs
   - Section correcte (Ajout/Modification/Correction/Retrait)
   - Tous les fichiers modifiés listés dans le commit

4. **Format obligatoire du commit** :
   - Type conventionnel (feat/fix/docs/refactor/etc.)
   - Sections organisées (UI/Technical/Translations/Documentation/Files/Impact)
   - Message en anglais uniquement
   - Détails techniques spécifiques (méthodes, classes, fichiers)

5. **Workflow Git Automatique** :
   - Dès que les modifications sont terminées : **exécuter immédiatement** git add, commit, push
   - Si merge demandé : **exécuter immédiatement** le processus complet de merge
   - Ne **JAMAIS** attendre de confirmation utilisateur pour les commandes Git

---

## 🎯 OPTIONS AVANCÉES

### Option 1 : Commit Uniquement (par défaut)
Lorsque le prompt est invoqué sans mention de merge :
- Exécuter le workflow complet jusqu'à l'étape 4 (commit + push)
- S'arrêter après le push, ne pas merger

### Option 2 : Commit + Merge (si demandé explicitement)
Lorsque l'utilisateur demande explicitement le merge :
- Exécuter le workflow complet jusqu'à l'étape 4 (commit + push)
- **Puis automatiquement** exécuter l'étape 5 (merge sur main)
- Nettoyer les branches obsolètes

### Option 3 : Vérification Pré-Merge (optionnel)
Si des conflits potentiels sont détectés :
- Informer l'utilisateur des conflits
- Proposer de résoudre manuellement avant le merge
- Attendre confirmation uniquement dans ce cas spécifique

---

**Ce workflow doit être appliqué automatiquement et complètement pour chaque fonctionnalité, sans exception ni omission. Les commandes Git doivent être exécutées immédiatement sans demander de confirmation.**
