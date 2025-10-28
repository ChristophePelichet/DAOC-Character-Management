# 🎮 DAOC Data Editor

Application d'édition visuelle des fichiers de données JSON pour DAOC Character Manager.

## 📋 Fonctionnalités

### 🎭 Éditeur Classes & Races
- ✅ **Visualiser** toutes les classes par royaume
- ✅ **Ajouter/Supprimer** des classes
- ✅ **Éditer** les noms en 3 langues (EN/FR/DE)
- ✅ **Sélectionner** les races disponibles pour chaque classe
- ✅ **Éditer** les spécialisations avec traductions

### 🏆 Éditeur Realm Ranks
- ✅ **Visualiser** tous les rangs de royaume
- ✅ **Ajouter/Supprimer** des rangs
- ✅ **Éditer** Rank, Level, Realm Points, Title
- ✅ **Gérer** les 3 royaumes séparément

## 🚀 Lancement

### Depuis Python
```bash
python data_editor.py
```

### Avec l'environnement virtuel
```bash
.venv\Scripts\python.exe data_editor.py
```

## 📖 Guide d'utilisation

### Éditer une classe

1. **Sélectionner le royaume** dans le menu déroulant
2. **Cliquer sur une classe** dans la liste
3. **Modifier les informations** :
   - Nom en anglais (EN)
   - Nom en français (FR)
   - Nom en allemand (DE)
4. **Cocher les races** disponibles pour cette classe
5. **Éditer les spécialisations** au format JSON :
   ```json
   [
     {
       "name": "Sword",
       "name_fr": "Épée",
       "name_de": "Schwert"
     },
     {
       "name": "Shield",
       "name_fr": "Bouclier",
       "name_de": "Schild"
     }
   ]
   ```
6. **Cliquer sur "💾 Sauvegarder tout"**

### Ajouter une nouvelle classe

1. **Sélectionner le royaume**
2. **Cliquer sur "➕ Ajouter"**
3. Une nouvelle classe "NewClass" est créée
4. **Modifier les informations** de la classe
5. **Sauvegarder**

### Supprimer une classe

1. **Sélectionner la classe** dans la liste
2. **Cliquer sur "➖ Supprimer"**
3. **Confirmer** la suppression
4. **Sauvegarder**

### Éditer les Realm Ranks

1. **Aller dans l'onglet "🏆 Realm Ranks"**
2. **Sélectionner le royaume**
3. **Modifier directement** dans le tableau :
   - **Rank** : Numéro du rang (1-14)
   - **Level** : Format "XLY" (ex: 5L7)
   - **Realm Points** : Points requis
   - **Title** : Titre du rang
4. **Sauvegarder**

### Ajouter/Supprimer un rang

- **Ajouter** : Cliquer sur "➕ Ajouter rang"
- **Supprimer** : Sélectionner une ligne et cliquer sur "➖ Supprimer rang"

## 📁 Fichiers édités

L'éditeur modifie directement les fichiers suivants :

- `Data/classes_races.json` - Classes, races et spécialisations
- `Data/realm_ranks_albion.json` - Rangs de royaume Albion
- `Data/realm_ranks_hibernia.json` - Rangs de royaume Hibernia
- `Data/realm_ranks_midgard.json` - Rangs de royaume Midgard

## ⚠️ Avertissements

- ⚠️ **Sauvegardez vos fichiers** avant d'utiliser l'éditeur
- ⚠️ **Validez le JSON** des spécialisations avant de sauvegarder
- ⚠️ L'application affiche un avertissement si vous fermez sans sauvegarder
- ⚠️ Les modifications sont appliquées immédiatement lors de la sauvegarde

## 🔧 Format JSON des spécialisations

Les spécialisations doivent être au format JSON valide :

```json
[
  {
    "name": "English Name",
    "name_fr": "Nom Français",
    "name_de": "Deutscher Name"
  }
]
```

**Règles** :
- Chaque spécialisation est un objet `{}`
- Trois clés obligatoires : `name`, `name_fr`, `name_de`
- Les noms sont des chaînes entre guillemets
- Séparer les objets par des virgules
- Le tout est dans un tableau `[]`

## 🎨 Interface

- **Onglet Classes & Races** : Éditeur visuel avec liste et formulaire
- **Onglet Realm Ranks** : Tableau éditable
- **Boutons principaux** :
  - 💾 **Sauvegarder tout** : Sauvegarde toutes les modifications
  - 🔄 **Recharger** : Recharge les données depuis les fichiers
  - ❌ **Fermer** : Ferme l'application (avec avertissement si modifié)

## 💡 Astuces

1. **Changement de royaume** : Les modifications sont automatiquement sauvegardées lors du changement
2. **Validation JSON** : Utilisez un validateur JSON en ligne si vous avez un doute
3. **Copier-coller** : Vous pouvez copier-coller des blocs de spécialisations
4. **Format cohérent** : Gardez la même structure pour toutes les spécialisations

## 🐛 Dépannage

### Erreur "Fichier manquant"
- Vérifiez que les fichiers JSON existent dans le dossier `Data/`

### Erreur JSON
- Vérifiez la syntaxe JSON (guillemets, virgules, crochets)
- Utilisez un validateur JSON en ligne

### Modifications non sauvegardées
- L'icône ⚠️ apparaît dans la barre de statut
- Cliquez sur "💾 Sauvegarder tout" avant de fermer

## 📞 Support

Pour toute question ou problème, consultez la documentation principale du DAOC Character Manager.

---

**Version** : 1.0  
**Auteur** : GitHub Copilot  
**Licence** : Même licence que DAOC Character Manager
