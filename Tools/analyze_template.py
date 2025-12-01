#!/usr/bin/env python3
"""
Analyze external template and match items with database
"""
import json
from pathlib import Path

# Load items database
db_path = Path(__file__).parent.parent / 'Data' / 'items_database_src.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

items_db = db['items']

# Items from the template (Valkyrie = Midgard)
template_items = {
    'Chest': 'Hauberk of Frigid Valor',
    'Arms': 'Mail Sleeves of Eternal Retribution',
    'Head': 'Dragonsworn Scribed',
    'Legs': 'Astral Leggings of Fortification',
    'Hands': 'Dragonsworn Scribed',
    'Feet': 'Sabatons of the Shard',
    'Right Hand': 'Fine Steel Long Sword',
    'Left Hand': 'Basalt Shield of Bedlam',
    'Neck': 'Luminescent Diamond Necklace',
    'Cloak': 'Sulphurous Fiend Cloak',
    'Jewel': 'Sphere of the Damned',
    'Belt': 'Soulbinder\'s Belt',
    'Left Ring': 'Leviathan Ring of the Deep',
    'Right Ring': 'Director\'s Ring of Chaos',
    'Left Wrist': 'Gatekeeper Bracer of Bedlam',
    'Right Wrist': 'Bracer of Embodiment',
    'Mythirian': 'Doppelganger Adept Mythirian'
}

print('=' * 90)
print('ANALYSE DU TEMPLATE - RECHERCHE DANS LA BASE DE DONNÉES')
print('=' * 90)
print(f'Character: Valkyrie (Midgard)')
print(f'Total items in database: {len(items_db)}')
print()

found = 0
not_found = 0
results = []

for slot, item_name in template_items.items():
    # Search in database (case insensitive)
    item_name_lower = item_name.lower()
    
    # Try to find with Midgard realm first
    key_mid = f'{item_name_lower}:midgard'
    
    # Search without caring about realm
    found_item = None
    found_realm = None
    found_key = None
    
    if key_mid in items_db:
        found_item = items_db[key_mid]
        found_realm = 'Midgard'
        found_key = key_mid
    else:
        # Search in all realms
        for key, item in items_db.items():
            if item['name'].lower() == item_name_lower:
                found_item = item
                found_realm = item['realm']
                found_key = key
                break
    
    if found_item:
        found += 1
        model = found_item.get('model', 'N/A')
        item_id = found_item.get('id', 'N/A')
        slot_type = found_item.get('slot', 'N/A')
        item_type = found_item.get('type', 'N/A')
        
        print(f'✅ {slot:15} | {item_name:45}')
        print(f'   └─ ID: {item_id:6} | Realm: {found_realm:8} | Slot: {slot_type:10} | Type: {item_type:10} | Model: {model}')
        
        results.append({
            'slot': slot,
            'name': item_name,
            'found': True,
            'id': item_id,
            'realm': found_realm,
            'model': model,
            'key': found_key
        })
    else:
        not_found += 1
        print(f'❌ {slot:15} | {item_name:45} | NON TROUVÉ DANS LA BASE')
        
        results.append({
            'slot': slot,
            'name': item_name,
            'found': False
        })

print()
print('=' * 90)
print(f'RÉSUMÉ: {found}/{len(template_items)} items trouvés ({not_found} manquants)')
print('=' * 90)

# List missing items
if not_found > 0:
    print()
    print('ITEMS MANQUANTS À AJOUTER DANS LA BASE:')
    print('-' * 90)
    for result in results:
        if not result['found']:
            print(f'  • {result["name"]} (Slot: {result["slot"]})')
    print()
    print('💡 Utilisez "Single Item Refresh" dans SuperAdmin pour les ajouter')
