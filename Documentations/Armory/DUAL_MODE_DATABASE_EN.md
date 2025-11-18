# Dual-Mode Database System - Technical Documentation

## Overview

The Armory system implements a **dual-mode database architecture** that allows users to choose between two operation modes:

- **Mode 1 (Internal Database)**: Read-only mode using the embedded `Data/items_database_src.json`
- **Mode 2 (Personal Database)**: User-managed mode with a copy in `Armory/items_database.json`

This architecture provides flexibility for different use cases while maintaining data integrity.

---

## Architecture

### Database Files

#### Internal Database (Mode 1)
- **Location**: `Data/items_database_src.json`
- **Type**: Read-only, embedded in application
- **Purpose**: Default database shipped with the application
- **Updates**: Only through application updates
- **Persistence**: No user modifications allowed

#### Personal Database (Mode 2)
- **Location**: `Armory/items_database.json`
- **Type**: User-managed, editable
- **Purpose**: Allows user customization and additions
- **Updates**: User can import, add, modify items
- **Persistence**: All changes saved permanently

### Mode Selection

The active mode is controlled by the configuration key:
```json
{
  "armory": {
    "use_personal_database": false,  // Mode 1 (default)
    "use_personal_database": true    // Mode 2
  }
}
```

---

## Features by Mode

### Mode 1: Internal Database (Read-Only)

**Capabilities**:
- ✅ Search items by name, realm, type
- ✅ View item statistics (armor, resists, bonuses)
- ✅ Scrape items from Eden/Zenkraft (temporary storage)
- ✅ Export scraped items to files

**Limitations**:
- ❌ Cannot save scraped items permanently
- ❌ Cannot modify existing items
- ❌ Cannot add custom items
- ❌ No import functionality

**Use Cases**:
- Casual users who don't need data persistence
- Temporary item lookups during gameplay
- Testing/validation without data modification
- Portable installations without write access

### Mode 2: Personal Database (User-Managed)

**Capabilities**:
- ✅ All Mode 1 capabilities
- ✅ **Persistent storage** of scraped items
- ✅ **Auto-add scraped items** (configurable)
- ✅ **Import items** from template files
- ✅ Add custom items manually
- ✅ Modify existing items
- ✅ Reset to internal database copy

**Additional Features**:
- Statistics tracking (internal vs. personal vs. user-added)
- Database version management
- Automatic backups on reset

**Use Cases**:
- Power users building personal item databases
- Guild leaders maintaining shared item lists
- Theorycrafters with custom item data
- Long-term data collection and analysis

---

## Database Manager (ItemsDatabaseManager)

### Core Methods

#### 1. `get_active_database_path() -> Path`
Returns the path to the currently active database based on mode.

**Returns**:
- Mode 1: `Data/items_database_src.json`
- Mode 2: `Armory/items_database.json`

**Usage**:
```python
db_path = db_manager.get_active_database_path()
```

#### 2. `search_item(item_name: str, realm: str = None) -> dict`
Search for an item in the active database.

**Parameters**:
- `item_name`: Item name to search (case-insensitive)
- `realm`: Optional realm filter ("Albion", "Hibernia", "Midgard")

**Returns**:
- Dictionary with item data if found
- `None` if not found

**Usage**:
```python
item = db_manager.search_item("Dragon Slayer Sword", realm="Albion")
```

#### 3. `create_personal_database() -> tuple[bool, str]`
Creates a personal database by copying the internal database.

**Process**:
1. Checks if `Armory` folder exists, creates if needed
2. Copies `Data/items_database_src.json` → `Armory/items_database.json`
3. Updates config: `use_personal_database = True`, `personal_db_created = True`
4. Saves database path and version to config

**Returns**:
- `(True, path)` on success
- `(False, error_message)` on failure

**Usage**:
```python
success, result = db_manager.create_personal_database()
if success:
    print(f"Database created at: {result}")
```

#### 4. `add_scraped_item(item_data: dict) -> bool`
Adds a scraped item to the personal database.

**Requirements**:
- Mode 2 must be active (`use_personal_database = True`)
- Personal database file must exist

**Features**:
- **Realm deduplication**: Only adds if item doesn't exist for same realm
- **User tracking**: Sets `user_added = True` in metadata
- **Automatic save**: Writes to file immediately

**Parameters**:
- `item_data`: Dictionary with item properties (name, realm, type, stats, etc.)

**Returns**:
- `True` if item added successfully
- `False` if item already exists or mode is wrong

**Usage**:
```python
item_data = {
    "name": "Custom Sword",
    "realm": "Albion",
    "type": "Weapon",
    "bonus_stats": {"Strength": 10}
}
success = db_manager.add_scraped_item(item_data)
```

#### 5. `get_statistics() -> dict`
Returns statistics about the databases.

**Returns**:
```python
{
    "internal_count": 1500,        # Items in internal DB
    "personal_count": 1580,        # Items in personal DB (if Mode 2)
    "user_added_count": 80,        # Items added by user (user_added=True)
    "mode": "personal"             # "internal" or "personal"
}
```

**Usage**:
```python
stats = db_manager.get_statistics()
print(f"You have {stats['user_added_count']} custom items")
```

#### 6. `reset_personal_database() -> bool`
Resets the personal database to a fresh copy of the internal database.

**Process**:
1. **WARNING**: Deletes all user-added items
2. Backs up current personal database (optional)
3. Copies internal database → personal database
4. Updates version tracking in config

**Returns**:
- `True` on success
- `False` on failure

**Usage**:
```python
success = db_manager.reset_personal_database()
```

---

## Configuration Schema

### Armory Section
```json
{
  "armory": {
    "use_personal_database": false,
    "personal_db_created": false,
    "personal_db_path": "",
    "auto_add_scraped_items": true,
    "last_internal_db_version": ""
  }
}
```

### Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_personal_database` | bool | `false` | Enable Mode 2 (personal DB) |
| `personal_db_created` | bool | `false` | Flag: personal DB created at least once |
| `personal_db_path` | str | `""` | Full path to personal database file |
| `auto_add_scraped_items` | bool | `true` | Auto-add scraped items without prompt |
| `last_internal_db_version` | str | `""` | Version tracking for updates |

---

## UI Integration

### Settings Dialog - Armory Page

#### Folder Configuration (Always Visible)
- **Armory folder path**: Browse, Move, Open buttons
- Changes immediately saved to config

#### Database Mode Section
- **Checkbox**: "Activate personal database"
  - Unchecked = Mode 1 (internal)
  - Checked = Mode 2 (personal)

#### Statistics Group (Visible in Mode 2)
- Items in internal database
- Items in personal database
- Items added by user

#### Actions Group (Visible in Mode 2)
- **Reset Database** button: Restore to internal copy

#### Import Section (Visible in Mode 2)
- **Import Items** button: Open import dialog
- Help text explaining import functionality

### Activation Flow

**First-time activation**:
1. User checks "Activate personal database"
2. System detects no personal DB exists
3. Popup: "Create personal database? (X items will be copied)"
4. User clicks Yes → database created
5. UI shows statistics, actions, import sections

**Subsequent activations**:
1. User checks "Activate personal database"
2. System detects existing personal DB
3. Mode switches immediately
4. UI shows statistics, actions, import sections

**Deactivation**:
1. User unchecks checkbox
2. System switches to Mode 1 (internal DB)
3. Statistics, actions, import sections hidden
4. Personal database file remains intact (can reactivate later)

---

## Auto-Add Integration

### Armory Import Dialog

When scraping completes and Mode 2 is active:

**If `auto_add_scraped_items = True`**:
- Items automatically added to personal database
- No user interaction required
- Success message shows count

**If `auto_add_scraped_items = False`**:
- Popup: "Add X items to your database?"
- Checkbox: "Always add automatically"
- User can:
  - Yes → Add items + optionally enable auto-add
  - No → Items discarded (not saved)

---

## Data Structure

### Item Format
```json
{
  "name": "Dragon Slayer Sword",
  "realm": "Albion",
  "type": "Two-Handed Weapon",
  "slot": "Two Hand",
  "quality": "Unique",
  "armor_factor": 0,
  "abs": 0,
  "damage": "16.5 DPS",
  "speed": "4.0",
  "bonus_hits": 40,
  "bonus_stats": {
    "Strength": 15,
    "Constitution": 10
  },
  "resists": {
    "Crush": 3,
    "Slash": 3,
    "Thrust": 3
  },
  "skill_bonuses": {
    "Two-Handed": 4
  },
  "focus": null,
  "user_added": false
}
```

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_added` | bool | `True` if item added by user (not from internal DB) |
| `source` | str | Optional: "scraped", "imported", "manual" |
| `date_added` | str | Optional: ISO timestamp |
| `notes` | str | Optional: User notes |

---

## Migration & Updates

### Application Updates

When a new version includes an updated internal database:

1. **Mode 1 users**: Automatically use new internal DB
2. **Mode 2 users**: Keep personal DB unchanged
   - Option to reset and copy new internal DB
   - Version tracking in `last_internal_db_version`

### Version Detection
```python
current_version = config.get("armory.last_internal_db_version")
internal_version = db_manager.get_internal_db_version()

if current_version != internal_version:
    # Notify user of update available
    # Offer to reset personal DB to get new items
```

---

## Error Handling

### Database Creation Failures
- **Folder permissions**: Check write access to Armory folder
- **Disk space**: Verify sufficient space for copy
- **File locks**: Ensure no other process using database

### Import/Add Failures
- **Invalid JSON**: Validate item structure before adding
- **Duplicate detection**: Check realm + name combination
- **Schema validation**: Ensure required fields present

### Recovery
- Personal database can always be reset to internal copy
- Config corruption: Falls back to Mode 1 (internal)
- File corruption: Recreate personal database

---

## Best Practices

### For Users

**Casual Use**:
- Stick with Mode 1 (internal database)
- No setup required, no maintenance

**Power Use**:
- Enable Mode 2 for persistent storage
- Enable auto-add for convenience
- Periodically review statistics
- Backup personal database manually (copy file)

### For Developers

**Database Updates**:
- Increment version number in internal database metadata
- Document changes in changelog
- Test migration from previous versions

**Feature Development**:
- Always check mode before write operations
- Use `get_active_database_path()` for consistency
- Log all database modifications
- Provide user feedback on mode switches

---

## Troubleshooting

### Issue: Checkbox won't stay checked
**Cause**: Personal database file doesn't exist
**Solution**: Delete and recreate personal database

### Issue: Items not saving
**Cause**: Mode 1 active (read-only)
**Solution**: Activate Mode 2 (personal database)

### Issue: Statistics not updating
**Cause**: Config not reloaded after changes
**Solution**: Close and reopen settings dialog

### Issue: Database corrupted
**Cause**: Manual editing introduced JSON errors
**Solution**: Reset personal database to internal copy

---

## Performance Considerations

### Database Size
- Internal DB: ~1-5 MB (1000-5000 items)
- Personal DB: Grows with user additions
- Search performance: O(n) linear search (acceptable for <10k items)

### Optimization
- Use realm filtering to reduce search space
- Cache frequently accessed items
- Consider indexing for large databases (>10k items)

---

## Security & Privacy

### Data Storage
- All databases stored locally (no cloud sync)
- Plain JSON format (no encryption)
- User responsible for backups

### Portable Mode
- Config and databases in application folder
- No registry/AppData dependencies
- Copy entire folder to backup/transfer

---

## Future Enhancements

### Planned Features
- [ ] Database merge tool (combine multiple personal DBs)
- [ ] Import/export personal DB as ZIP
- [ ] Item comparison tool (internal vs. personal)
- [ ] Database optimization (remove duplicates)
- [ ] Advanced search (filters, sorting)
- [ ] Database statistics dashboard

### Under Consideration
- [ ] Cloud sync (optional, encrypted)
- [ ] Collaborative databases (guild sharing)
- [ ] Automatic backups before reset
- [ ] Database compression (SQLite migration)

---

## Related Documentation

- `ARMORY_IMPORT_SYSTEM_EN.md` - Import functionality
- `DATA_MANAGER_EN.md` - Data management architecture
- `CONFIGURATION_EN.md` - Config schema reference
- `DATABASE_MANAGER_TECHNICAL_EN.md` - API reference

---

**Version**: 1.0  
**Last Updated**: November 18, 2025  
**Author**: DAOC Character Manager Development Team
