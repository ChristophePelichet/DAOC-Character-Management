# Visible Columns Configuration

## 📋 Overview

This feature allows you to customize which columns are displayed in the main character list. You can hide columns you don't need to get a cleaner view.

## 🎯 Accessing Configuration

### Via the Menu

1. Go to **View > Columns** menu
2. A configuration window opens

### Configuration Interface

The configuration window displays:
- ✅ List of all available columns with checkboxes
- 🔘 "Select all" button to show all columns
- 🔘 "Deselect all" button to hide all columns
- ✔️ "OK" button to save changes
- ✖️ "Cancel" button to close without saving

## 📊 Available Columns

| Column | Key | Description | Default |
|--------|-----|-------------|---------|
| **Selection** | `selection` | Checkbox for bulk actions | ✅ Visible |
| **Realm** | `realm` | Realm icon (Albion/Hibernia/Midgard) | ✅ Visible |
| **Season** | `season` | Character's season (S1, S2, S3, etc.) | ✅ Visible |
| **Server** | `server` | Character's server (Eden, Blackthorn, etc.) | ❌ Hidden |
| **Name** | `name` | Character name | ✅ Visible |
| **Level** | `level` | Character level | ✅ Visible |
| **Rank** | `realm_rank` | Realm rank (e.g., 5L7) | ✅ Visible |
| **Title** | `realm_title` | Rank title (e.g., Challenger) | ✅ Visible |
| **Guild** | `guild` | Character's guild name | ✅ Visible |
| **Page** | `page` | Character's page number (1-5) | ✅ Visible |
| **Class** | `class` | Character class | ✅ Visible |
| **Race** | `race` | Character race | ❌ Hidden |

## 💾 Save and Persistence

- Configuration is **automatically saved** in `Configuration/config.json`
- Settings are **preserved between sessions**
- Visibility is applied at application startup
- A confirmation message appears after saving

## 🔧 Technical Configuration

### Configuration File

```json
{
  "column_visibility": {
    "selection": true,
    "realm": true,
    "season": true,
    "server": false,
    "name": true,
    "level": true,
    "realm_rank": true,
    "realm_title": true,
    "guild": true,
    "page": true,
    "class": true,
    "race": false
  }
}
```

### Translations

The feature is available in all languages:
- 🇫🇷 **Français** : "Colonnes" / "Configuration des colonnes"
- 🇬🇧 **English** : "Columns" / "Column Configuration"
- 🇩🇪 **Deutsch** : "Spalten" / "Spaltenkonfiguration"

## 🎨 Icon

The icon used is `Img/colonnes.png`.

## 📝 Recommended Usage

### Use Case Examples

1. **Simplified View**: Hide "Season" and "Server" if you play on a single server
2. **Rank Focus**: Display only Name, Level, Rank, and Title
3. **Complete View**: Show everything for a global overview

### Tips

- ✅ Always keep the "Name" column visible
- ✅ The "Selection" column is useful for bulk deletions
- ⚠️ If you hide all columns, nothing will be displayed!

## 🐛 Troubleshooting

### Columns won't hide

1. Make sure you clicked "OK" (not "Cancel")
2. Restart the application if necessary
3. Check the `Configuration/config.json` file

### Lost configuration

If configuration doesn't persist:
- Check write permissions on the `Configuration/` folder
- Consult logs in `Logs/debug.log` (if debug mode is enabled)

## 🔄 Future Updates

This feature could be extended to:
- Reorganize column order by drag and drop
- Save multiple view "profiles"
- Adjust column widths
- Add new columns (class, race, guild, etc.)

---

**Version**: 0.101  
**Date**: October 2025  
**Author**: DAOC Character Manager Team
