# Data Folder - DAOC Game Data

## 📁 Folder Contents

This folder contains all extracted game data used by the application:

```
Data/
└── realm_ranks.json    # Realm ranks for all 3 realms (390 entries)
```

## 📊 File Descriptions

### realm_ranks.json

**Size**: 390 entries (130 per realm)  
**Realms**: Albion, Hibernia, Midgard  
**Source**: https://www.darkageofcamelot.com/realm-ranks/

This file contains all available realm ranks in DAOC, with the following information for each level:
- Rank number (1-14)
- Skill bonus (0-13)
- Rank title (realm-specific)
- Detailed level (format "XLY", e.g., "5L7")
- Required realm points (0 to 13,040,539 RP)
- Available realm ability points

**Format**:
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

## 🔄 Data Update

To update `realm_ranks.json` from the official DAOC website:

```bash
python scrape_realm_ranks.py
```

This script:
1. Connects to the official DAOC website
2. Extracts rank tables for all 3 realms
3. Parses and cleans the data
4. Saves to `Data/realm_ranks.json`

**Recommended frequency**: Check after each major DAOC patch

## 📚 Complete Documentation

For more information on data usage and Data Manager:

- 🇫🇷 **Français**: [Documentation/DATA_MANAGER_FR.md](../Documentation/DATA_MANAGER_FR.md)
- 🇬🇧 **English**: [Documentation/DATA_MANAGER_EN.md](../Documentation/DATA_MANAGER_EN.md)

These documents include:
- Data Manager usage guide
- Code examples
- Complete API
- Character manager integration

## 🚀 Future Extensions

Additional data files may be added:

### Planned Data

- **`classes.json`**: Available classes by realm
  - Class list
  - Realm restrictions
  - Allowed armor and weapons

- **`races.json`**: Playable races by realm
  - Racial bonuses
  - Class restrictions
  - Starting statistics

- **`skills.json`**: Skills and spells
  - Skill trees
  - Descriptions
  - Required levels

- **`items.json`**: Equipment and items
  - Item statistics
  - Sets
  - Artifacts

### Future Usage Examples

```python
from Functions.data_manager import DataManager

dm = DataManager()

# Available classes for Hibernia
classes = dm.get_realm_classes("Hibernia")

# Playable races for Armsman
races = dm.get_class_races("Armsman")

# Skills for level 50
skills = dm.get_level_skills(50, "Paladin")
```

## 📝 Important Notes

- ✅ **JSON only**: All data is in JSON format for easy reading and modification
- ✅ **UTF-8**: UTF-8 encoding to support all characters
- ✅ **Portable**: Compatible with all operating systems
- ✅ **Editable**: Files can be manually edited if needed
- ⚠️ **Backup**: Remember to backup before regenerating data

## 🔧 Maintenance

### Integrity Check

To verify data validity:

```python
import json

# Check realm_ranks.json
with open('Data/realm_ranks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print(f"Albion: {len(data['Albion'])} entries")
print(f"Hibernia: {len(data['Hibernia'])} entries")
print(f"Midgard: {len(data['Midgard'])} entries")
```

### Manual Backup

Before any major modification:

```bash
# Create backup copy
copy Data\realm_ranks.json Data\realm_ranks.backup.json
```

## 🐛 Troubleshooting

### realm_ranks.json file is missing

Run the extraction script:
```bash
python scrape_realm_ranks.py
```

### JSON parsing error

The file may be corrupted. Restore from backup or regenerate.

### Outdated data

Compare with official DAOC website and regenerate if necessary.

---

**Last update**: October 2025  
**Data version**: Corresponding to current DAOC patch
