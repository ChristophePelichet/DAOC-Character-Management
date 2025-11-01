# Dossier Data - Données de Jeu DAOC

## 📁 Contenu du Dossier

Ce dossier contient toutes les données de jeu extraites et utilisées par l'application :

```
Data/
└── realm_ranks.json    # Rangs de royaume pour les 3 royaumes (390 entrées)
```

## 📊 Description des Fichiers

### realm_ranks.json

**Taille** : 390 entrées (130 par royaume)  
**Royaumes** : Albion, Hibernia, Midgard  
**Source** : https://www.darkageofcamelot.com/realm-ranks/

Ce fichier contient tous les rangs de royaume disponibles dans DAOC, avec pour chaque niveau :
- Numéro du rang (1-14)
- Bonus aux compétences (0-13)
- Titre du rang (spécifique à chaque royaume)
- Niveau détaillé (format "XLY", ex: "5L7")
- Points de royaume requis (0 à 13,040,539 RP)
- Points d'aptitudes de royaume disponibles

**Format** :
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

## 🔄 Mise à Jour des Données

Pour mettre à jour `realm_ranks.json` depuis le site officiel DAOC :

```bash
python scrape_realm_ranks.py
```

Ce script :
1. Se connecte au site officiel DAOC
2. Extrait les tableaux de rangs pour les 3 royaumes
3. Parse et nettoie les données
4. Sauvegarde dans `Data/realm_ranks.json`

**Fréquence recommandée** : Vérifier après chaque patch majeur de DAOC

## 📚 Documentation Complète

Pour plus d'informations sur l'utilisation des données et du Data Manager :

- 🇫🇷 **Français** : [Documentation/DATA_MANAGER_FR.md](../Documentation/DATA_MANAGER_FR.md)
- 🇬🇧 **English** : [Documentation/DATA_MANAGER_EN.md](../Documentation/DATA_MANAGER_EN.md)

Ces documents incluent :
- Guide d'utilisation du Data Manager
- Exemples de code
- API complète
- Intégration avec le gestionnaire de personnages

## 🚀 Extensions Futures

D'autres fichiers de données pourront être ajoutés :

### Données Planifiées

- **`classes.json`** : Classes disponibles par royaume
  - Liste des classes
  - Restrictions par royaume
  - Armures et armes autorisées

- **`races.json`** : Races jouables par royaume
  - Bonus raciaux
  - Restrictions de classe
  - Statistiques de départ

- **`skills.json`** : Compétences et sorts
  - Arbres de compétences
  - Descriptions
  - Niveaux requis

- **`items.json`** : Équipements et objets
  - Statistiques d'items
  - Ensembles (sets)
  - Artefacts

### Exemples d'Utilisation Future

```python
from Functions.data_manager import DataManager

dm = DataManager()

# Classes disponibles pour Hibernia
classes = dm.get_realm_classes("Hibernia")

# Races jouables par un Armsman
races = dm.get_class_races("Armsman")

# Compétences pour niveau 50
skills = dm.get_level_skills(50, "Paladin")
```

## 📝 Notes Importantes

- ✅ **JSON uniquement** : Toutes les données sont en format JSON pour faciliter la lecture et la modification
- ✅ **UTF-8** : Encodage UTF-8 pour supporter tous les caractères
- ✅ **Portable** : Compatible avec tous les systèmes d'exploitation
- ✅ **Éditable** : Les fichiers peuvent être modifiés manuellement si nécessaire
- ⚠️ **Sauvegarde** : Pensez à sauvegarder avant de regénérer les données

## 🔧 Maintenance

### Vérification de l'Intégrité

Pour vérifier que les données sont valides :

```python
import json

# Vérifier realm_ranks.json
with open('Data/realm_ranks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print(f"Albion: {len(data['Albion'])} entrées")
print(f"Hibernia: {len(data['Hibernia'])} entrées")
print(f"Midgard: {len(data['Midgard'])} entrées")
```

### Sauvegarde Manuelle

Avant toute modification importante :

```bash
# Créer une copie de sauvegarde
copy Data\realm_ranks.json Data\realm_ranks.backup.json
```

## 🐛 Dépannage

### Le fichier realm_ranks.json est manquant

Exécutez le script d'extraction :
```bash
python scrape_realm_ranks.py
```

### Erreur de parsing JSON

Le fichier est peut-être corrompu. Restaurez depuis la sauvegarde ou régénérez-le.

### Données obsolètes

Comparez avec le site officiel DAOC et régénérez si nécessaire.

---

**Dernière mise à jour** : Octobre 2025  
**Version des données** : Correspondant au patch DAOC en cours
