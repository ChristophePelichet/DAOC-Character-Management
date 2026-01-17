"""
Script to move all 'legs' subcategory from 'other' to 'armor' category
in the models_metadata.json file.
"""

import json
from pathlib import Path

def move_legs_from_other_to_armor():
    """Move legs subcategory from other to armor in models metadata."""
    
    metadata_path = Path(__file__).parent.parent / "Data" / "models_metadata.json"
    
    # Load the JSON file
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Access the items structure
    items = data.get("items", {})
    other = items.get("other", {})
    armor = items.get("armor", {})
    
    # Check if legs exists in other
    if "legs" not in other:
        print("❌ 'legs' not found in 'other' category")
        return False
    
    # Get the legs items from other
    other_legs = other["legs"]
    count_other_legs = len(other_legs)
    
    print(f"📋 Found {count_other_legs} items in other.legs")
    
    # Check if legs exists in armor
    if "legs" in armor:
        # Merge with existing armor.legs
        count_armor_legs = len(armor["legs"])
        armor["legs"].update(other_legs)
        count_merged = len(armor["legs"])
        print(f"✅ Merged into existing armor.legs: {count_armor_legs} + {count_other_legs} = {count_merged} items")
    else:
        # Create legs in armor
        armor["legs"] = other_legs
        print(f"✅ Created armor.legs with {count_other_legs} items")
    
    # Remove legs from other
    del other["legs"]
    print("✅ Removed 'legs' from 'other' category")
    
    # Save the modified JSON
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {metadata_path}")
    
    # Verify
    remaining_categories = list(other.keys())
    armor_categories = list(armor.keys())
    
    print("\n📊 Verification:")
    print(f"   Other categories: {remaining_categories}")
    print(f"   Armor categories: {armor_categories}")
    print(f"   Total armor.legs: {len(armor['legs'])} items")
    
    return True

if __name__ == "__main__":
    success = move_legs_from_other_to_armor()
    if success:
        print("\n✨ Migration complete!")
    else:
        print("\n⚠️ Migration failed!")
