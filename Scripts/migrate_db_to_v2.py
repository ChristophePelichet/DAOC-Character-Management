#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration Script: items_database_src.json v1.0 → v2.0
- Adds composite keys (name:realm)
- Adds model, dps, speed, damage_type fields (null if not available)
- Removes level, quality, stats, resistances, bonuses
- Preserves all existing data
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def migrate_database():
    """Migrate database from v1.0 to v2.0"""
    
    # Paths
    project_root = Path(__file__).parent.parent
    db_path = project_root / "Data" / "items_database_src.json"
    backup_folder = project_root / "Data" / "Backups"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Create backup
    backup_folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_folder / f"items_database_v1_backup_{timestamp}.json"
    
    print(f"📦 Loading database: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        old_db = json.load(f)
    
    # Save backup
    print(f"💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(old_db, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Backup saved: {backup_path}")
    
    # Migrate items with composite keys
    print("\n🔄 Migrating items to v2.0...")
    new_items = {}
    migration_stats = {
        "total": 0,
        "migrated": 0,
        "skipped": 0,
        "fields_removed": 0,
        "fields_added": 0
    }
    
    for old_key, item in old_db.get("items", {}).items():
        migration_stats["total"] += 1
        
        # Get realm from item
        realm = item.get("realm", "All")
        
        # Generate new composite key
        new_key = f"{old_key}:{realm.lower()}"
        
        # Build new item structure (v2.0 minimal)
        new_item = {
            "id": item.get("id"),
            "name": item.get("name"),
            "realm": realm,
            "slot": item.get("slot"),
            "type": item.get("type"),
            "model": item.get("model"),  # Will be null if not in v1.0
            "dps": item.get("dps"),  # Will be null if not in v1.0
            "speed": item.get("speed"),  # Will be null if not in v1.0
            "damage_type": item.get("damage_type"),  # Will be null if not in v1.0
            "merchant_zone": item.get("merchant_zone"),
            "merchant_price": item.get("merchant_price"),
            "source": item.get("source", "internal")
        }
        
        # Count removed fields
        removed_fields = ["level", "quality", "stats", "resistances", "bonuses"]
        for field in removed_fields:
            if field in item:
                migration_stats["fields_removed"] += 1
        
        # Count added fields
        added_fields = ["model", "dps", "speed", "damage_type"]
        for field in added_fields:
            if field not in item:
                migration_stats["fields_added"] += 1
        
        new_items[new_key] = new_item
        migration_stats["migrated"] += 1
        
        print(f"  ✓ {old_key} → {new_key}")
    
    # Build new database structure
    new_db = {
        "version": "2.0",
        "description": "DAOC Items Database - Multi-Realm Support (Minimal Data)",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_count": len(new_items),
        "notes": [
            "Composite keys format: 'item_name:realm' (lowercase)",
            "Only essential data: ID, name, realm, slot, type, model, damage info, merchant",
            "No stats, resistances, bonuses, level, or quality",
            f"Migrated from v{old_db.get('version', '1.0')} on {datetime.now().strftime('%Y-%m-%d')}"
        ],
        "items": new_items
    }
    
    # Save new database
    print(f"\n💾 Saving v2.0 database: {db_path}")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(new_db, f, indent=2, ensure_ascii=False)
    
    # Print migration summary
    print(f"\n{'='*80}")
    print(f"✅ MIGRATION SUCCESSFUL")
    print(f"{'='*80}")
    print(f"Version:       v{old_db.get('version', '1.0')} → v2.0")
    print(f"Total items:   {migration_stats['total']}")
    print(f"Migrated:      {migration_stats['migrated']}")
    print(f"Skipped:       {migration_stats['skipped']}")
    print(f"Fields removed: {migration_stats['fields_removed']} (level, quality, stats, resistances, bonuses)")
    print(f"Fields added:  {migration_stats['fields_added']} (model, dps, speed, damage_type)")
    print(f"\n📁 Backup:     {backup_path}")
    print(f"📁 Database:   {db_path}")
    print(f"{'='*80}\n")
    
    return True

if __name__ == "__main__":
    print("\n" + "="*80)
    print("DATABASE MIGRATION: v1.0 → v2.0")
    print("="*80 + "\n")
    
    success = migrate_database()
    
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
