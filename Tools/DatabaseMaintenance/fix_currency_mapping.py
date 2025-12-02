"""
Script to fix currency mapping in items_database_src.json
Normalizes "Grimoire Pages" to "Grimoires" and validates all currency mappings
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.path_manager import get_base_path

# Expected currency mappings
ZONE_CURRENCY = {
    "DF": "Seals",
    "SH": "Grimoires",
    "ToA": "Glasses",
    "Drake": "Scales",
    "Epic": "Souls/Roots/Ices",
    "Epik": "Souls/Roots/Ices"
}

def fix_currency_mapping():
    """Fix currency mappings in items database"""
    
    base_path = get_base_path()
    db_path = os.path.join(base_path, "Data", "items_database_src.json")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    # Create backup
    backup_path = db_path.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    print("=" * 80)
    print("CURRENCY MAPPING FIX")
    print("=" * 80)
    print(f"\n📂 Database: {db_path}")
    print(f"💾 Backup: {backup_path}\n")
    
    # Load database
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    # Check if we have the new format with version
    if isinstance(db_data, dict) and 'items' in db_data:
        items_db = db_data['items']
        has_metadata = True
    else:
        items_db = db_data
        has_metadata = False
    
    print(f"📊 Total items in database: {len(items_db)}")
    
    # Statistics
    stats = {
        'total_items': len(items_db),
        'items_with_merchant': 0,
        'fixed_grimoire_pages': 0,
        'fixed_dragon_scales': 0,
        'fixed_zone_mismatch': 0,
        'currencies_found': set(),
        'zones_found': set()
    }
    
    # Process each item
    for item_id, item_data in items_db.items():
        merchant_currency = item_data.get('merchant_currency')
        merchant_zone = item_data.get('merchant_zone')
        
        if merchant_currency or merchant_zone:
            stats['items_with_merchant'] += 1
            
            if merchant_currency:
                stats['currencies_found'].add(merchant_currency)
            if merchant_zone:
                stats['zones_found'].add(merchant_zone)
            
            # Fix "Grimoire Pages" → "Grimoires"
            if merchant_currency == "Grimoire Pages":
                item_data['merchant_currency'] = "Grimoires"
                stats['fixed_grimoire_pages'] += 1
                print(f"  🔧 [{item_id}] {item_data.get('name', 'Unknown')}: 'Grimoire Pages' → 'Grimoires'")
            
            # Fix "Dragon Scales" → "Scales"
            if merchant_currency == "Dragon Scales":
                item_data['merchant_currency'] = "Scales"
                stats['fixed_dragon_scales'] += 1
                print(f"  🔧 [{item_id}] {item_data.get('name', 'Unknown')}: 'Dragon Scales' → 'Scales'")
            
            # Validate zone/currency consistency
            if merchant_zone and merchant_currency:
                expected_currency = ZONE_CURRENCY.get(merchant_zone)
                if expected_currency and merchant_currency != expected_currency:
                    # Fix mismatch by trusting the zone
                    old_currency = merchant_currency
                    item_data['merchant_currency'] = expected_currency
                    stats['fixed_zone_mismatch'] += 1
                    print(f"  ⚠️  [{item_id}] {item_data.get('name', 'Unknown')}: Zone '{merchant_zone}' → Currency '{old_currency}' → '{expected_currency}'")
    
    # Display statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total items:                 {stats['total_items']}")
    print(f"Items with merchant info:    {stats['items_with_merchant']}")
    print(f"Fixed 'Grimoire Pages':      {stats['fixed_grimoire_pages']}")
    print(f"Fixed 'Dragon Scales':       {stats['fixed_dragon_scales']}")
    print(f"Fixed zone/currency mismatch: {stats['fixed_zone_mismatch']}")
    
    print(f"\n📊 Currencies found in DB:")
    for currency in sorted(stats['currencies_found']):
        print(f"  - {currency}")
    
    print(f"\n🗺️  Zones found in DB:")
    for zone in sorted(stats['zones_found']):
        expected = ZONE_CURRENCY.get(zone, "UNKNOWN")
        print(f"  - {zone:10} → {expected}")
    
    total_fixes = stats['fixed_grimoire_pages'] + stats['fixed_dragon_scales'] + stats['fixed_zone_mismatch']
    
    if total_fixes > 0:
        # Save backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            if has_metadata:
                db_data['items'] = items_db
                db_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                json.dump(db_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(items_db, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Backup created: {backup_path}")
        
        # Save corrected database
        with open(db_path, 'w', encoding='utf-8') as f:
            if has_metadata:
                db_data['items'] = items_db
                db_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                json.dump(db_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(items_db, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Database updated: {total_fixes} items fixed")
    else:
        print(f"\n✅ No fixes needed - database is clean!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    fix_currency_mapping()
