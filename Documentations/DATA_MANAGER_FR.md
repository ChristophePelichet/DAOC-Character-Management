# Data Manager - Gestionnaire de Données DAOC

## 📁 Structure des Données

```
Data/
└── realm_ranks.json    # Rangs de royaume pour les 3 royaumes
```

## 🔧 Extraction des Données

### Realm Ranks

Pour mettre à jour les données de Realm Ranks depuis le site officiel DAOC :

```bash
python scrape_realm_ranks.py
```

Ce script :
- ✅ Se connecte à https://www.darkageofcamelot.com/realm-ranks/
- ✅ Extrait les tableaux de rangs pour Albion, Hibernia et Midgard
- ✅ Sauvegarde les données dans `Data/realm_ranks.json`

## 📊 Format des Données

### realm_ranks.json

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

**Champs :**
- `rank` : Numéro du rang (1-14)
- `skill_bonus` : Bonus aux compétences (0-13)
- `title` : Titre du rang (spécifique au royaume)
- `level` : Niveau détaillé (format "XLY", ex: "5L7")
- `realm_points` : Points de royaume requis
- `realm_ability_points` : Points d'aptitudes de royaume disponibles

## 💻 Utilisation dans le Code

### Importer le Data Manager

```python
from Functions.data_manager import DataManager

dm = DataManager()
```

### Exemples d'utilisation

#### 1. Obtenir le rang actuel d'un joueur

```python
rank_info = dm.get_realm_rank_info("Albion", 50000)
print(f"Rang: {rank_info['rank']} - {rank_info['title']}")
print(f"Niveau: {rank_info['level']}")
```

#### 2. Calculer la progression vers le prochain rang

```python
current_rp = 50000
next_rank = dm.get_next_realm_rank("Albion", current_rp)
rp_needed = next_rank['realm_points'] - current_rp
percentage = (current_rp / next_rank['realm_points']) * 100

print(f"Prochain rang: {next_rank['title']}")
print(f"Progression: {percentage:.1f}%")
print(f"RP manquants: {rp_needed:,}")
```

#### 3. Afficher un résumé de tous les rangs

```python
summary = dm.get_all_ranks_summary("Hibernia")
for rank in summary:
    print(f"Rank {rank['rank']}: {rank['title']} "
          f"(+{rank['skill_bonus']} skills, {rank['min_realm_points']:,} RP)")
```

#### 4. Calculer les RP nécessaires pour un rang cible

```python
current_rp = 100000
target_rank = 10
rp_needed = dm.calculate_rp_needed("Midgard", current_rp, target_rank)
print(f"RP à gagner pour Rank {target_rank}: {rp_needed:,}")
```

## 🎮 Intégration avec le Character Manager

Le Data Manager peut être facilement intégré dans votre gestionnaire de personnages :

```python
from Functions.character_manager import CharacterManager
from Functions.data_manager import DataManager

# Charger un personnage
cm = CharacterManager()
character = cm.load_character("Albion", "MonPerso")

# Obtenir ses infos de rang
dm = DataManager()
realm_points = character.get("realm_points", 0)
rank_info = dm.get_realm_rank_info(character["realm"], realm_points)

print(f"{character['name']}: {rank_info['title']} (Rank {rank_info['rank']})")
```

## 🔄 Mise à Jour des Données

Les données sont extraites du site officiel DAOC et peuvent être mises à jour régulièrement :

1. Exécuter `python scrape_realm_ranks.py`
2. Vérifier le fichier `Data/realm_ranks.json`
3. Les modifications seront automatiquement prises en compte

## 📝 Notes

- Les données sont stockées en JSON pour faciliter la lecture et la modification
- Le format est portable et compatible avec tous les systèmes d'exploitation
- Les fichiers JSON peuvent être édités manuellement si nécessaire
- Le Data Manager met en cache les données pour de meilleures performances

## 🚀 Extensions Futures

D'autres types de données peuvent être ajoutés :

- `Data/classes.json` : Classes par royaume
- `Data/races.json` : Races par royaume
- `Data/skills.json` : Compétences et sorts
- `Data/items.json` : Équipements et objets

Utilisez le même pattern pour créer des scripts d'extraction et des méthodes dans le Data Manager.
