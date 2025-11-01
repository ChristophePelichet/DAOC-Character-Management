# Data Manager - DAOC Data Manager

## 📁 Data Structure

```
Data/
└── realm_ranks.json    # Realm ranks for all 3 realms
```

## 🔧 Data Extraction

### Realm Ranks

To update Realm Ranks data from the official DAOC website:

```bash
python scrape_realm_ranks.py
```

This script:
- ✅ Connects to https://www.darkageofcamelot.com/realm-ranks/
- ✅ Extracts rank tables for Albion, Hibernia, and Midgard
- ✅ Saves data to `Data/realm_ranks.json`

## 📊 Data Format

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

**Fields:**
- `rank`: Rank number (1-14)
- `skill_bonus`: Skill bonus (0-13)
- `title`: Rank title (realm-specific)
- `level`: Detailed level (format "XLY", e.g., "5L7")
- `realm_points`: Required realm points
- `realm_ability_points`: Available realm ability points

## 💻 Code Usage

### Import Data Manager

```python
from Functions.data_manager import DataManager

dm = DataManager()
```

### Usage Examples

#### 1. Get a player's current rank

```python
rank_info = dm.get_realm_rank_info("Albion", 50000)
print(f"Rank: {rank_info['rank']} - {rank_info['title']}")
print(f"Level: {rank_info['level']}")
```

#### 2. Calculate progression to next rank

```python
current_rp = 50000
next_rank = dm.get_next_realm_rank("Albion", current_rp)
rp_needed = next_rank['realm_points'] - current_rp
percentage = (current_rp / next_rank['realm_points']) * 100

print(f"Next rank: {next_rank['title']}")
print(f"Progress: {percentage:.1f}%")
print(f"RP needed: {rp_needed:,}")
```

#### 3. Display summary of all ranks

```python
summary = dm.get_all_ranks_summary("Hibernia")
for rank in summary:
    print(f"Rank {rank['rank']}: {rank['title']} "
          f"(+{rank['skill_bonus']} skills, {rank['min_realm_points']:,} RP)")
```

#### 4. Calculate RP needed for target rank

```python
current_rp = 100000
target_rank = 10
rp_needed = dm.calculate_rp_needed("Midgard", current_rp, target_rank)
print(f"RP to gain for Rank {target_rank}: {rp_needed:,}")
```

## 🎮 Character Manager Integration

The Data Manager can be easily integrated into your character manager:

```python
from Functions.character_manager import CharacterManager
from Functions.data_manager import DataManager

# Load a character
cm = CharacterManager()
character = cm.load_character("Albion", "MyChar")

# Get rank info
dm = DataManager()
realm_points = character.get("realm_points", 0)
rank_info = dm.get_realm_rank_info(character["realm"], realm_points)

print(f"{character['name']}: {rank_info['title']} (Rank {rank_info['rank']})")
```

## 🔄 Data Updates

Data is extracted from the official DAOC website and can be updated regularly:

1. Run `python scrape_realm_ranks.py`
2. Check the `Data/realm_ranks.json` file
3. Changes will be automatically applied

## 📝 Notes

- Data is stored in JSON for easy reading and modification
- The format is portable and compatible with all operating systems
- JSON files can be manually edited if needed
- Data Manager caches data for better performance

## 🚀 Future Extensions

Other data types can be added:

- `Data/classes.json`: Classes by realm
- `Data/races.json`: Races by realm
- `Data/skills.json`: Skills and spells
- `Data/items.json`: Equipment and items

Use the same pattern to create extraction scripts and Data Manager methods.
