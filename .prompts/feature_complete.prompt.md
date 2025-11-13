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

### Étape 2 : Traductions Automatiques
- Identifier TOUS les textes visibles par l'utilisateur
- Créer/modifier les clés dans `Language/*.json` (FR/EN/DE)
- Vérifier la cohérence des traductions

### Étape 3 : Documentation Changelog
- Déterminer la section appropriée (Ajout/Modification/Correction/Retrait)
- Ajouter la ligne avec emoji contextuel
- Mettre à jour les versions Simple ET Full si nécessaire

### Étape 4 : Confirmation
- Résumer les modifications apportées
- Lister les fichiers créés/modifiés
- Indiquer les traductions ajoutées

---

## 📋 CHECKLIST DE VALIDATION

Avant de finaliser, vérifier :

- [ ] Tous les textes UI traduits en FR/EN/DE
- [ ] Clés JSON cohérentes dans les 3 fichiers
- [ ] Changelog mis à jour avec section appropriée
- [ ] Emojis contextuels utilisés
- [ ] Fichiers de code modifiés documentés
- [ ] Pas de textes hardcodés dans le code

---

## 🎯 EXEMPLE COMPLET

**Demande** : "Ajoute un bouton pour exporter tous les personnages en CSV"

**Actions automatiques :**

1. **Code** : Implémentation du bouton et fonction export
2. **Traductions** :
   ```json
   // fr.json
   "export_all_button": "Exporter Tout"
   "export_success": "Export réussi"
   
   // en.json
   "export_all_button": "Export All"
   "export_success": "Export successful"
   
   // de.json
   "export_all_button": "Alles Exportieren"
   "export_success": "Export erfolgreich"
   ```
3. **Changelog** :
   ```markdown
   ### 🎉 Ajout
   - 📤 Bouton "Exporter Tout" pour export CSV de tous les personnages
   - 💾 Fonction d'export avec gestion des erreurs
   - 🌍 Traductions FR/EN/DE complètes
   ```

---

**Important** : Ne demandez JAMAIS de confirmation pour les traductions ou la documentation. Appliquez automatiquement toutes les règles de ce workflow.
