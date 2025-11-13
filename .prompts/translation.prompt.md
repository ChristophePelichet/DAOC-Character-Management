# Instructions de Traduction Multi-Langues

Instructions pour la gestion automatique des traductions dans le projet.

**Contexte :**
* Ce projet doit être **multilingue** avec support complet de 3 langues : **Français (FR)**, **Anglais (EN)**, **Allemand (DE)**
* Tous les textes visibles par l'utilisateur doivent être traduits dans ces 3 langues
* Les fichiers de traduction sont situés dans : `Language/fr.json`, `Language/en.json`, `Language/de.json`

**Règles Automatiques :**

### 1. Création de Nouveaux Textes
Lorsque vous ajoutez un nouveau texte visible par l'utilisateur :
- ✅ Créer automatiquement la clé dans les 3 fichiers JSON
- ✅ Fournir les traductions FR, EN, DE
- ✅ Utiliser des clés descriptives en snake_case (ex: `new_character_button`)
- ✅ Ne PAS demander si l'utilisateur veut les traductions, faites-le systématiquement

### 2. Modification de Textes Existants
Lorsque vous modifiez un texte :
- ✅ Mettre à jour les 3 langues simultanément
- ✅ Maintenir la cohérence entre les traductions
- ✅ Vérifier que la clé existe dans tous les fichiers

### 3. Format des Fichiers JSON
```json
{
  "key_name": "Texte traduit dans la langue du fichier"
}
```

### 4. Exemples de Traductions

**Boutons et Actions :**
- FR : "Nouveau Personnage" / EN : "New Character" / DE : "Neuer Charakter"
- FR : "Sauvegarder" / EN : "Save" / DE : "Speichern"
- FR : "Annuler" / EN : "Cancel" / DE : "Abbrechen"
- FR : "Supprimer" / EN : "Delete" / DE : "Löschen"

**Messages :**
- FR : "Opération réussie" / EN : "Operation successful" / DE : "Vorgang erfolgreich"
- FR : "Erreur lors de la connexion" / EN : "Connection error" / DE : "Verbindungsfehler"

**Labels :**
- FR : "Nom" / EN : "Name" / DE : "Name"
- FR : "Niveau" / EN : "Level" / DE : "Stufe"
- FR : "Royaume" / EN : "Realm" / DE : "Reich"

### 5. Priorités
- 🔴 **Haute** : Messages d'erreur, boutons principaux, labels de formulaires
- 🟡 **Moyenne** : Tooltips, messages informatifs, titres de sections
- 🟢 **Basse** : Messages de debug (peuvent rester en anglais)

### 6. Qualité des Traductions
- ✅ Utiliser un vocabulaire adapté au contexte (gaming DAOC)
- ✅ Maintenir la même longueur approximative (important pour l'UI)
- ✅ Respecter les conventions de chaque langue (majuscules, ponctuation)
- ✅ Pour l'allemand : utiliser les majuscules pour les noms (ex: "Neuer Charakter")

### 7. Cas Spéciaux
- **Noms propres** : Ne pas traduire (Albion, Hibernia, Midgard, Herald, Eden)
- **Termes techniques DAOC** : Garder en anglais si pas d'équivalent (RvR, PvP, PvE)
- **Unités** : Adapter selon la langue (pt/points, MB/Mo)

**Workflow Standard :**
1. Identifier tous les textes visibles dans la demande
2. Créer/modifier les clés dans les 3 fichiers JSON
3. Vérifier la cohérence des traductions
4. Confirmer à l'utilisateur les modifications apportées

**Important :** Ne demandez JAMAIS "voulez-vous que je traduise ?", faites-le automatiquement pour tout texte visible par l'utilisateur.
