#!/usr/bin/env python3
"""
Merge models databases intelligently.

Combines:
- models_metadata.json (595 enriched items with real categories)
- dol_models_database.json (3444 complete items with basic info)

Output: Restructured models_metadata.json with full hierarchy
  items:
    weapon:
      bow:
        132: {name, source_url, ...}
      sword:
        101: {...}
    armor:
      head:
        50: {...}
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "Data"

# Load existing enriched metadata
print("Loading models_metadata.json (595 enriched items)...")
with open(DATA_DIR / "models_metadata.json", 'r', encoding='utf-8') as f:
    enriched = json.load(f)

enriched_items = enriched.get("items", {})
print(f"  Loaded {len(enriched_items)} enriched items")

# Load complete DOL database
print("\nLoading dol_models_database.json (3444 complete items)...")
with open(DATA_DIR / "dol_models_database.json", 'r', encoding='utf-8') as f:
    dol_db = json.load(f)

dol_items = {k: v for k, v in dol_db.items() if isinstance(v, dict)}
print(f"  Loaded {len(dol_items)} DOL items")

# Build hierarchical structure
print("\nBuilding hierarchical structure...")
hierarchy = defaultdict(lambda: defaultdict(dict))

# Category mapping from DOL (translate to lowercase)
dol_category_map = {
    "weapons": "weapon",
    "armor": "armor",
    "deco_and_etc": "other",
    "misc_models": "other"
}

processed = set()
missing_in_dol = []

# Process enriched items first (they have real subcategories)
enriched_ids = set()
for item_id, item_data in enriched_items.items():
    enriched_ids.add(item_id)
    
    main_cat = item_data.get("main_category", "Unknown").lower()
    subcat = item_data.get("subcategory", "Unknown").lower()
    
    hierarchy[main_cat][subcat][item_id] = {
        "name": item_data.get("name", f"Item {item_id}"),
        "source_url": item_data.get("source_url", "")
    }

# Process DOL items not in enriched metadata
duplicates = 0
for item_id, dol_data in dol_items.items():
    if item_id in enriched_ids:
        duplicates += 1
        continue
    
    processed.add(item_id)
    dol_cat = dol_data.get("category", "unknown").lower()
    main_cat = dol_category_map.get(dol_cat, "other")
    subcat = dol_data.get("slot", "Unknown").lower().replace(" ", "_")
    
    hierarchy[main_cat][subcat][item_id] = {
        "name": dol_data.get("name", f"Item {item_id}"),
        "source_url": dol_data.get("source_url", "")
    }

# Statistics
print("\n" + "="*60)
print("MERGE STATISTICS")
print("="*60)

total_items = sum(len(subcat) for cat in hierarchy.values() for subcat in cat.values())
print(f"Total items after merge: {total_items}")
print(f"  Target: 3444")
print(f"  Match: {'✓ YES' if total_items == 3444 else '✗ NO'}")

print(f"\nProcessed: {len(processed)} items")
print(f"  From enriched DB: {len(enriched_items)}")
print(f"  From DOL DB: {len(dol_items) - duplicates}")
print(f"  Duplicates (skipped): {duplicates}")

print(f"\nHierarchy structure:")
for category in sorted(hierarchy.keys()):
    subcats = hierarchy[category]
    print(f"  {category}: {len(subcats)} subcategories")
    for subcat in sorted(subcats.keys()):
        count = len(hierarchy[category][subcat])
        print(f"    - {subcat}: {count} items")

# Convert to standard dict
final_structure = {
    "items": {}
}

for category in hierarchy:
    final_structure["items"][category] = {}
    for subcat in hierarchy[category]:
        final_structure["items"][category][subcat] = hierarchy[category][subcat]

# Save
output_file = DATA_DIR / "models_metadata.json"
print(f"\nSaving to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_structure, f, indent=2, ensure_ascii=False)

print("✓ Done!")
print(f"\nFile size: {output_file.stat().st_size / 1024:.1f} KB")
