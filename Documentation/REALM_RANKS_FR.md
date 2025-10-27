# Intégration des Realm Ranks - Documentation Complète

## 📋 Vue d'ensemble

Le système de Realm Ranks permet de gérer et d'afficher les rangs de royaume (RR) de vos personnages DAOC dans le gestionnaire de personnages. Cette fonctionnalité inclut :

- 🏆 Affichage automatique du rang et du titre basé sur les Realm Points (RP)
- 📊 Deux nouvelles colonnes : "Rang" et "Titre"
- 🎨 Titres colorés selon le royaume (rouge pour Albion, vert pour Hibernia, bleu pour Midgard)
- ⚙️ Ajustement manuel du rang via des sliders dans la feuille de personnage
- 📈 Calcul automatique des RP nécessaires pour chaque niveau

## 🎯 Fonctionnalités

### Affichage dans la Liste Principale

**Colonne "Rang"** (Index 6)
- Affiche le niveau détaillé (ex: "5L7" pour Rank 5 Level 7)
- Centré et aligné
- Calculé automatiquement depuis les Realm Points

**Colonne "Titre"** (Index 7)
- Affiche le titre correspondant au rang (ex: "Challenger")
- **Texte en gras**
- **Coloré selon le royaume** :
  - Albion : Rouge (#CC0000)
  - Hibernia : Vert (#00AA00)
  - Midgard : Bleu (#0066CC)
- Texte blanc lorsque la ligne est sélectionnée

### Feuille de Personnage

Double-cliquez sur un personnage pour ouvrir sa feuille et voir :

**Section "Rang de Royaume"**
- 🏆 Affichage du rang et titre actuel en gros caractères colorés
- 📊 Points de royaume actuels (RP)

**Section "Ajustement du Rang"**
- 🎚️ Slider pour le rang (1-14)
- 🎚️ Slider pour le niveau (1-9 pour Rank 1, 1-10 pour les autres)
- 📝 Affichage des RP nécessaires pour le rang/niveau sélectionné
- 💾 Bouton "Appliquer ce rang" pour sauvegarder

### Règles de Progression

- **Rank 1** : 9 niveaux (1L1 à 1L9)
- **Ranks 2-14** : 10 niveaux chacun (ex: 5L1 à 5L10)
- Total : **139 niveaux** à travers les 14 rangs

## 🔧 Composants Techniques

### 1. Data Manager (`Functions/data_manager.py`)

Gère l'accès aux données de realm ranks :

```python
from Functions.data_manager import DataManager

dm = DataManager()

# Obtenir le rang pour un nombre de RP
rank_info = dm.get_realm_rank_info("Albion", 50000)
print(f"{rank_info['rank']} - {rank_info['title']} ({rank_info['level']})")

# Obtenir les infos pour un niveau spécifique
level_info = dm.get_rank_by_level("Hibernia", "5L7")
print(f"RP requis : {level_info['realm_points']:,}")
```

**Méthodes disponibles** :
- `get_realm_rank_info(realm, realm_points)` - Rang actuel
- `get_next_realm_rank(realm, realm_points)` - Prochain niveau
- `get_rank_by_level(realm, level_str)` - Infos pour un niveau précis
- `get_all_ranks_summary(realm)` - Résumé de tous les rangs
- `calculate_rp_needed(realm, current_rp, target_rank)` - RP à gagner

### 2. RealmTitleDelegate (`main.py`)

Delegate personnalisé pour afficher les titres en couleur :

```python
class RealmTitleDelegate(QStyledItemDelegate):
    REALM_COLORS = {
        "Albion": "#CC0000",
        "Hibernia": "#00AA00",
        "Midgard": "#0066CC"
    }
```

**Caractéristiques** :
- Texte en gras
- Couleur selon le royaume
- Gestion de la sélection (texte blanc)
- Centré dans la cellule

### 3. CharacterSheetWindow

Fenêtre de détails avec contrôles de rang :

**Composants** :
- `rank_slider` : QSlider (1-14)
- `level_slider` : QSlider (1-9/10)
- `rank_title_label` : Affichage du titre actuel
- `rp_info_label` : Infos sur le rang sélectionné

**Méthodes** :
- `on_rank_changed()` - Mise à jour du max du slider de niveau
- `on_level_changed()` - Mise à jour de l'affichage des RP
- `update_rp_info()` - Affiche les RP pour le rang/niveau
- `apply_rank()` - Sauvegarde le nouveau rang

## 📊 Données

### Structure de `Data/realm_ranks.json`

```json
{
  "Albion": [
    {
      "rank": 1,
      "skill_bonus": 0,
      "title": "Guardian",
      "level": "1L1",
      "realm_points": 0,
      "realm_ability_points": 1
    },
    ...
  ],
  "Hibernia": [...],
  "Midgard": [...]
}
```

- **390 entrées totales** (130 par royaume)
- **14 rangs** avec titres uniques par royaume
- **Progression RP** : 0 à 13,040,539 RP (max)

### Mise à Jour des Données

Pour actualiser les données depuis le site officiel :

```bash
python scrape_realm_ranks.py
```

## 🎨 Couleurs des Royaumes

| Royaume | Couleur Hex | Aperçu |
|---------|-------------|--------|
| Albion | `#CC0000` | 🔴 Rouge |
| Hibernia | `#00AA00` | 🟢 Vert |
| Midgard | `#0066CC` | 🔵 Bleu |

## 💾 Format de Sauvegarde

Les données de personnage incluent maintenant :

```json
{
  "id": "Nom_Du_Perso",
  "name": "Nom Du Perso",
  "realm": "Albion",
  "level": 50,
  "season": "S3",
  "server": "Eden",
  "realm_points": 50000,
  "realm_rank": "5L7"
}
```

- `realm_points` : Nombre de RP (calculé ou ajusté manuellement)
- `realm_rank` : Niveau actuel (format "XLY")

## 🔄 Flux de Travail

### Ajustement Manuel

1. Double-cliquer sur un personnage
2. Utiliser les sliders pour choisir Rang et Niveau
3. Vérifier les RP affichés
4. Cliquer sur "Appliquer ce rang"
5. Confirmer dans la boîte de dialogue
6. Les données sont sauvegardées et la liste rafraîchie

### Affichage Automatique

1. L'application charge les personnages au démarrage
2. Pour chaque personnage :
   - Lit `realm_points` depuis le JSON
   - Interroge le DataManager pour obtenir rang/titre
   - Affiche dans les colonnes "Rang" et "Titre"

## 📝 Notes Importantes

- ⚠️ Les valeurs de RP doivent être exactes (pas d'approximation)
- ✅ Le DataManager met en cache les données pour de meilleures performances
- 🔄 Les modifications sont immédiatement visibles après sauvegarde
- 💾 La sauvegarde utilise `allow_overwrite=True` pour les mises à jour

## 🐛 Dépannage

### Les titres ne sont pas colorés

- Vérifiez que le `RealmTitleDelegate` est bien assigné à la colonne 7
- Assurez-vous que le royaume est stocké dans `UserRole` de l'item

### Les sliders ne fonctionnent pas

- Vérifiez que `DataManager` est initialisé dans `CharacterApp`
- Assurez-vous que `realm_ranks.json` existe dans `Data/`

### Erreur "char_exists_error"

- Utilisez `allow_overwrite=True` lors de la sauvegarde d'un personnage existant
- Voir la fonction `save_character()` dans `character_manager.py`

---

**Version** : 0.101  
**Date** : Octobre 2025  
**Auteur** : DAOC Character Manager Team
