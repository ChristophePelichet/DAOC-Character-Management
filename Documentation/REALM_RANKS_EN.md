# Realm Ranks Integration - Complete Documentation

## 📋 Overview

The Realm Ranks system allows you to manage and display the realm ranks (RR) of your DAOC characters in the character manager. This feature includes:

- 🏆 Automatic display of rank and title based on Realm Points (RP)
- 📊 Two new columns: "Rank" and "Title"
- 🎨 Colored titles by realm (red for Albion, green for Hibernia, blue for Midgard)
- ⚙️ Manual rank adjustment via sliders in character sheet
- 📈 Automatic calculation of RP needed for each level

## 🎯 Features

### Main List Display

**"Rank" Column** (Index 6)
- Displays detailed level (e.g., "5L7" for Rank 5 Level 7)
- Centered and aligned
- Automatically calculated from Realm Points

**"Title" Column** (Index 7)
- Displays the title corresponding to the rank (e.g., "Challenger")
- **Bold text**
- **Colored by realm**:
  - Albion: Red (#CC0000)
  - Hibernia: Green (#00AA00)
  - Midgard: Blue (#0066CC)
- White text when row is selected

### Character Sheet

Double-click on a character to open their sheet and see:

**"Realm Rank" Section**
- 🏆 Display of current rank and title in large colored characters
- 📊 Current realm points (RP)

**"Rank Adjustment" Section**
- 🎚️ Slider for rank (1-14)
- 🎚️ Slider for level (1-9 for Rank 1, 1-10 for others)
- 📝 Display of RP needed for selected rank/level
- 💾 "Apply this rank" button to save

### Progression Rules

- **Rank 1**: 9 levels (1L1 to 1L9)
- **Ranks 2-14**: 10 levels each (e.g., 5L1 to 5L10)
- Total: **139 levels** across 14 ranks

## 🔧 Technical Components

### 1. Data Manager (`Functions/data_manager.py`)

Manages access to realm ranks data:

```python
from Functions.data_manager import DataManager

dm = DataManager()

# Get rank for RP amount
rank_info = dm.get_realm_rank_info("Albion", 50000)
print(f"{rank_info['rank']} - {rank_info['title']} ({rank_info['level']})")

# Get info for specific level
level_info = dm.get_rank_by_level("Hibernia", "5L7")
print(f"RP required: {level_info['realm_points']:,}")
```

**Available methods**:
- `get_realm_rank_info(realm, realm_points)` - Current rank
- `get_next_realm_rank(realm, realm_points)` - Next level
- `get_rank_by_level(realm, level_str)` - Info for specific level
- `get_all_ranks_summary(realm)` - Summary of all ranks
- `calculate_rp_needed(realm, current_rp, target_rank)` - RP to gain

### 2. RealmTitleDelegate (`main.py`)

Custom delegate to display colored titles:

```python
class RealmTitleDelegate(QStyledItemDelegate):
    REALM_COLORS = {
        "Albion": "#CC0000",
        "Hibernia": "#00AA00",
        "Midgard": "#0066CC"
    }
```

**Features**:
- Bold text
- Color by realm
- Selection handling (white text)
- Centered in cell

### 3. CharacterSheetWindow

Detail window with rank controls:

**Components**:
- `rank_slider`: QSlider (1-14)
- `level_slider`: QSlider (1-9/10)
- `rank_title_label`: Current title display
- `rp_info_label`: Info on selected rank

**Methods**:
- `on_rank_changed()` - Update level slider max
- `on_level_changed()` - Update RP display
- `update_rp_info()` - Display RP for rank/level
- `apply_rank()` - Save new rank

## 📊 Data

### Structure of `Data/realm_ranks.json`

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

- **390 total entries** (130 per realm)
- **14 ranks** with unique titles per realm
- **RP progression**: 0 to 13,040,539 RP (max)

### Data Update

To refresh data from official website:

```bash
python scrape_realm_ranks.py
```

## 🎨 Realm Colors

| Realm | Hex Color | Preview |
|-------|-----------|---------|
| Albion | `#CC0000` | 🔴 Red |
| Hibernia | `#00AA00` | 🟢 Green |
| Midgard | `#0066CC` | 🔵 Blue |

## 💾 Save Format

Character data now includes:

```json
{
  "id": "Char_Name",
  "name": "Char Name",
  "realm": "Albion",
  "level": 50,
  "season": "S3",
  "server": "Eden",
  "realm_points": 50000,
  "realm_rank": "5L7"
}
```

- `realm_points`: Number of RP (calculated or manually adjusted)
- `realm_rank`: Current level (format "XLY")

## 🔄 Workflow

### Manual Adjustment

1. Double-click on a character
2. Use sliders to choose Rank and Level
3. Check displayed RP
4. Click "Apply this rank"
5. Confirm in dialog box
6. Data is saved and list refreshed

### Automatic Display

1. Application loads characters at startup
2. For each character:
   - Reads `realm_points` from JSON
   - Queries DataManager for rank/title
   - Displays in "Rank" and "Title" columns

## 📝 Important Notes

- ⚠️ RP values must be exact (no approximation)
- ✅ DataManager caches data for better performance
- 🔄 Changes are immediately visible after save
- 💾 Save uses `allow_overwrite=True` for updates

## 🐛 Troubleshooting

### Titles are not colored

- Check that `RealmTitleDelegate` is assigned to column 7
- Ensure realm is stored in item's `UserRole`

### Sliders don't work

- Verify `DataManager` is initialized in `CharacterApp`
- Ensure `realm_ranks.json` exists in `Data/`

### "char_exists_error" error

- Use `allow_overwrite=True` when saving existing character
- See `save_character()` function in `character_manager.py`

---

**Version**: 0.1  
**Date**: October 2025  
**Author**: DAOC Character Manager Team
