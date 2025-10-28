# Guide d'utilisation : Races, Classes et Spécialisations

## Vue d'ensemble

Le système de gestion des races et classes de DAOC est centralisé dans le fichier `Data/classes_races.json`. Ce fichier contient toutes les informations sur :
- Les races disponibles par royaume
- Les classes disponibles par royaume
- Les combinaisons race/classe valides
- Les spécialisations de chaque classe

## Structure du fichier JSON

```json
{
  "Albion|Midgard|Hibernia": {
    "races": [
      {
        "name": "Nom anglais",
        "name_fr": "Nom français",
        "name_de": "Nom allemand"
      }
    ],
    "classes": [
      {
        "name": "Nom anglais",
        "name_fr": "Nom français",
        "name_de": "Nom allemand",
        "races": ["Race1", "Race2", ...],
        "specializations": ["Spec1", "Spec2", ...]
      }
    ]
  }
}
```

## Utilisation via DataManager

### Importer le module

```python
from Functions.data_manager import DataManager

# Initialiser le manager
dm = DataManager()
```

### 1. Récupérer toutes les races d'un royaume

```python
# Obtenir toutes les races d'Albion
races = dm.get_races("Albion")

for race in races:
    print(f"{race['name']} - FR: {race['name_fr']}, DE: {race['name_de']}")
```

**Résultat :**
```
Avalonian - FR: Avalonien, DE: Avalonianer
Briton - FR: Briton, DE: Brite
Half Ogre - FR: Demi-Ogre, DE: Halbogre
...
```

### 2. Récupérer toutes les classes d'un royaume

```python
# Obtenir toutes les classes de Midgard
classes = dm.get_classes("Midgard")

for class_info in classes:
    print(f"{class_info['name']} ({class_info['name_fr']})")
```

### 3. Obtenir les détails d'une classe

```python
# Informations sur l'Armsman
class_info = dm.get_class_info("Albion", "Armsman")

print(f"Classe: {class_info['name']}")
print(f"Races disponibles: {', '.join(class_info['races'])}")
print(f"Spécialisations: {', '.join(class_info['specializations'])}")
```

**Résultat :**
```
Classe: Armsman
Races disponibles: Avalonian, Briton, Half Ogre, Highlander, Inconnu, Saracen
Spécialisations: Crossbow, Polearm, Slash, Thrust, Two Handed, Parry, Shield
```

### 4. Classes disponibles pour une race

```python
# Quelles classes peut jouer un Briton ?
available_classes = dm.get_available_classes_for_race("Albion", "Briton")

print(f"Nombre de classes: {len(available_classes)}")
for c in available_classes:
    print(f"  - {c['name']}")
```

**Résultat :**
```
Nombre de classes: 16
  - Armsman
  - Cabalist
  - Cleric
  - Friar
  ...
```

### 5. Races disponibles pour une classe

```python
# Quelles races peuvent jouer Healer ?
races = dm.get_races_for_class("Midgard", "Healer")
print(f"Races: {', '.join(races)}")
```

**Résultat :**
```
Races: Dwarf, Frostalf, Norseman
```

### 6. Vérifier la compatibilité race/classe

```python
# Est-ce qu'un Briton peut être Friar ?
is_valid = dm.is_race_class_compatible("Albion", "Briton", "Friar")
print(f"Briton + Friar: {is_valid}")  # True

# Est-ce qu'un Avalonian peut être Friar ?
is_valid = dm.is_race_class_compatible("Albion", "Avalonian", "Friar")
print(f"Avalonian + Friar: {is_valid}")  # False
```

### 7. Récupérer les spécialisations d'une classe

```python
# Spécialisations du Druid
specs = dm.get_specializations("Hibernia", "Druid")
for spec in specs:
    print(f"  - {spec}")
```

**Résultat :**
```
  - Nature Affinity
  - Nurture
  - Regrowth
```

### 8. Obtenir tous les royaumes

```python
realms = dm.get_all_realms()
print(f"Royaumes: {', '.join(realms)}")
```

**Résultat :**
```
Royaumes: Albion, Midgard, Hibernia
```

## Modification des données

### Ajouter une nouvelle race

Pour ajouter une race, éditez le fichier `Data/classes_races.json` :

```json
{
  "Albion": {
    "races": [
      {
        "name": "Nouvelle Race",
        "name_fr": "Nouvelle Race FR",
        "name_de": "Neue Rasse"
      }
    ]
  }
}
```

### Ajouter une nouvelle classe

```json
{
  "Albion": {
    "classes": [
      {
        "name": "Nouvelle Classe",
        "name_fr": "Nouvelle Classe FR",
        "name_de": "Neue Klasse",
        "races": ["Briton", "Avalonian"],
        "specializations": ["Spec1", "Spec2", "Spec3"]
      }
    ]
  }
}
```

### Modifier les races d'une classe

Pour changer quelles races peuvent jouer une classe, modifiez simplement le tableau `races` :

```json
{
  "name": "Armsman",
  "races": ["Briton", "Avalonian", "Highlander"]  // Retirer ou ajouter des races ici
}
```

### Modifier les spécialisations

Pour changer les spécialisations disponibles :

```json
{
  "name": "Armsman",
  "specializations": [
    "Crossbow",
    "Polearm",
    "Slash",
    "Thrust"  // Retirer ou ajouter des spécialisations ici
  ]
}
```

## Intégration dans l'interface utilisateur

### Exemple : Dropdown dynamique de races

```python
# Dans une fenêtre de création de personnage
realm = "Albion"  # Royaume sélectionné
races = dm.get_races(realm)

# Peupler un QComboBox
race_combo = QComboBox()
for race in races:
    race_combo.addItem(race['name_fr'])  # Utiliser la traduction française
```

### Exemple : Filtrer les classes selon la race

```python
def on_race_changed(race_name):
    """Appelé quand l'utilisateur change de race"""
    realm = "Albion"
    
    # Obtenir les classes disponibles
    available_classes = dm.get_available_classes_for_race(realm, race_name)
    
    # Mettre à jour le dropdown de classes
    class_combo.clear()
    for class_info in available_classes:
        class_combo.addItem(class_info['name_fr'])
```

### Exemple : Afficher les spécialisations

```python
def on_class_changed(class_name):
    """Appelé quand l'utilisateur change de classe"""
    realm = "Albion"
    
    # Obtenir les spécialisations
    specs = dm.get_specializations(realm, class_name)
    
    # Afficher dans une liste
    spec_list.clear()
    for spec in specs:
        spec_list.addItem(spec)
```

## Statistiques

### Albion
- **6 races** : Avalonian, Briton, Half Ogre, Highlander, Inconnu, Saracen
- **16 classes** : Armsman, Cabalist, Cleric, Friar, Heretic, Infiltrator, Mauler, Mercenary, Minstrel, Necromancer, Paladin, Reaver, Scout, Sorcerer, Theurgist, Wizard

### Midgard
- **6 races** : Dwarf, Frostalf, Kobold, Norseman, Troll, Valkyn
- **15 classes** : Berserker, Bonedancer, Healer, Hunter, Mauler, Runemaster, Savage, Shadowblade, Shaman, Skald, Spiritmaster, Thane, Valkyrie, Warlock, Warrior

### Hibernia
- **6 races** : Celt, Elf, Firbolg, Lurikeen, Shar, Sylvan
- **16 classes** : Animist, Bainshee, Bard, Blademaster, Champion, Druid, Eldritch, Enchanter, Hero, Mauler, Mentalist, Nightshade, Ranger, Valewalker, Vampiir, Warden

## Notes importantes

1. **Traductions** : Chaque race et classe contient des traductions en français, anglais et allemand
2. **Spécialisations** : Les noms sont en anglais uniquement (comme dans le jeu officiel)
3. **Compatibilité** : Le système vérifie automatiquement les combinaisons race/classe valides
4. **Facilité de modification** : Toutes les données sont dans un seul fichier JSON facile à éditer
5. **Pas de logique codée en dur** : Toutes les règles de compatibilité sont basées sur les données du JSON

## Fichiers concernés

- **Data/classes_races.json** : Fichier de données principal
- **Functions/data_manager.py** : Module de gestion avec toutes les méthodes
- **DAOC-Character-Manager.spec** : Configuration PyInstaller (inclut automatiquement Data/)

## Ressources

- Source officielle : https://www.darkageofcamelot.com/classes-races/
- Documentation du jeu : https://camelotherald.fandom.com/
