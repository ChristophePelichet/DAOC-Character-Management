"""
Database Key Format Fix Script
Converts wrong-format keys (CamelCase_Realm) to correct format (lowercase:realm)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

DB_PATH = project_root / "Data" / "items_database_src.json"

def fix_database_keys():
    """Fix all database keys to use correct format: {name}:{realm} (lowercase)"""
    
    print("=" * 80)
    print("DATABASE KEY FORMAT FIX SCRIPT")
    print("=" * 80)
    print()
    
    # Load database
    print(f"Loading database from: {DB_PATH}")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"Database version: {db.get('version', 'unknown')}")
    print(f"Item count: {db.get('item_count', 0)}")
    print()
    
    # Find and fix wrong-format keys
    items = db.get("items", {})
    wrong_keys = []
    fixed_items = {}
    
    print("Scanning for wrong-format keys...")
    for key, item_data in items.items():
        # Check if key uses wrong format (contains underscore)
        if "_" in key:
            wrong_keys.append(key)
            
            # Generate correct key
            item_name = item_data.get("name", "")
            realm = item_data.get("realm", "")
            
            # Convert to correct format: lowercase with colon
            correct_key = f"{item_name.lower()}:{realm.lower()}"
            
            print(f"  ❌ Wrong: '{key}'")
            print(f"  ✅ Fixed: '{correct_key}'")
            print()
            
            # Use corrected key
            fixed_items[correct_key] = item_data
        else:
            # Key is already correct, keep as-is
            fixed_items[key] = item_data
    
    print()
    print(f"Found {len(wrong_keys)} items with wrong-format keys")
    
    if not wrong_keys:
        print("✅ All keys are already in correct format!")
        return
    
    # Update database
    db["items"] = fixed_items
    db["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create backup
    backup_path = DB_PATH.with_suffix('.json.backup')
    print(f"\nCreating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    # Save fixed database
    print(f"Saving fixed database: {DB_PATH}")
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 80)
    print("✅ DATABASE FIXED SUCCESSFULLY")
    print("=" * 80)
    print()
    print(f"Total items processed: {len(items)}")
    print(f"Items fixed: {len(wrong_keys)}")
    print(f"Items unchanged: {len(items) - len(wrong_keys)}")
    print()
    print("Wrong-format keys fixed:")
    for key in wrong_keys:
        print(f"  • {key}")
    print()

if __name__ == "__main__":
    fix_database_keys()
