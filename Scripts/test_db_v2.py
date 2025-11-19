#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Script for Database v2.0
Tests composite keys, fallback logic, and new data fields
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Functions.items_scraper import ItemsScraper
from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
import json

def test_database_structure():
    """Test v2.0 database structure"""
    print("\n" + "="*80)
    print("TEST 1: Database Structure v2.0")
    print("="*80)
    
    db_path = project_root / "Data" / "items_database_src.json"
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # Check version
    assert db["version"] == "2.0", f"❌ Version should be 2.0, got {db['version']}"
    print(f"✅ Version: {db['version']}")
    
    # Check structure
    assert "notes" in db, "❌ Missing 'notes' field"
    print(f"✅ Notes field present")
    
    # Check composite keys
    sample_keys = list(db["items"].keys())[:5]
    for key in sample_keys:
        assert ":" in key, f"❌ Key '{key}' is not composite (missing ':')"
        name, realm = key.rsplit(":", 1)
        assert realm in ["albion", "hibernia", "midgard", "all"], f"❌ Invalid realm '{realm}' in key '{key}'"
    
    print(f"✅ Composite keys format validated")
    print(f"   Sample keys: {sample_keys[:3]}")
    
    # Check item structure
    first_item = list(db["items"].values())[0]
    required_fields = ["id", "name", "realm", "slot", "type", "model", "dps", "speed", "damage_type", "merchant_zone", "merchant_price", "source"]
    
    for field in required_fields:
        assert field in first_item, f"❌ Missing required field '{field}'"
    
    print(f"✅ Item structure validated (12 fields)")
    
    # Check removed fields
    removed_fields = ["level", "quality", "stats", "resistances", "bonuses"]
    for field in removed_fields:
        assert field not in first_item, f"❌ Old field '{field}' still present"
    
    print(f"✅ Old fields removed (level, quality, stats, resistances, bonuses)")
    
    print(f"\n✅ TEST 1 PASSED\n")

def test_composite_key_generation():
    """Test composite key generation"""
    print("\n" + "="*80)
    print("TEST 2: Composite Key Generation")
    print("="*80)
    
    # Mock scraper for testing
    from pathlib import Path
    cookie_manager = CookieManager()
    eden_scraper = EdenScraper(cookie_manager)
    scraper = ItemsScraper(eden_scraper)
    
    # Test key generation
    test_cases = [
        ("Cudgel of the Undead", "Albion", "cudgel of the undead:albion"),
        ("Cudgel of the Undead", "Hibernia", "cudgel of the undead:hibernia"),
        ("Dragonseye Strand", "All", "dragonseye strand:all"),
        ("SOME ITEM", "Midgard", "some item:midgard"),
        ("Item Name", None, "item name:all"),
    ]
    
    for item_name, realm, expected_key in test_cases:
        generated_key = scraper._get_cache_key(item_name, realm)
        assert generated_key == expected_key, f"❌ Expected '{expected_key}', got '{generated_key}'"
        print(f"✅ {item_name} ({realm}) → {generated_key}")
    
    print(f"\n✅ TEST 2 PASSED\n")

def test_database_lookup():
    """Test database lookup with fallback"""
    print("\n" + "="*80)
    print("TEST 3: Database Lookup with Fallback")
    print("="*80)
    
    cookie_manager = CookieManager()
    eden_scraper = EdenScraper(cookie_manager)
    scraper = ItemsScraper(eden_scraper)
    
    # Test 1: Realm-specific item (Albion)
    item_id = scraper._get_item_from_databases("Cudgel of the Undead", "Albion")
    assert item_id == "139625", f"❌ Expected ID 139625, got {item_id}"
    print(f"✅ Cudgel of the Undead (Albion) → ID {item_id}")
    
    # Test 2: Common item (All realms) - search with specific realm, fallback to "all"
    item_id = scraper._get_item_from_databases("Dragonseye Strand", "Albion")
    assert item_id == "149092", f"❌ Expected ID 149092, got {item_id}"
    print(f"✅ Dragonseye Strand (Albion → All fallback) → ID {item_id}")
    
    # Test 3: Common item (All realms) - direct search
    item_id = scraper._get_item_from_databases("Dragonseye Strand", "All")
    assert item_id == "149092", f"❌ Expected ID 149092, got {item_id}"
    print(f"✅ Dragonseye Strand (All) → ID {item_id}")
    
    # Test 4: Item not in database
    item_id = scraper._get_item_from_databases("Non-Existent Item", "Albion")
    assert item_id is None, f"❌ Should return None for non-existent item"
    print(f"✅ Non-Existent Item → None (as expected)")
    
    print(f"\n✅ TEST 3 PASSED\n")

def test_data_completeness():
    """Test that all items have required fields"""
    print("\n" + "="*80)
    print("TEST 4: Data Completeness")
    print("="*80)
    
    db_path = project_root / "Data" / "items_database_src.json"
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    required_fields = ["id", "name", "realm", "slot", "source"]
    optional_fields = ["type", "model", "dps", "speed", "damage_type", "merchant_zone", "merchant_price"]
    
    items_with_damage = 0
    items_with_model = 0
    
    for key, item in db["items"].items():
        # Check required fields
        for field in required_fields:
            assert field in item and item[field], f"❌ Item '{key}' missing required field '{field}'"
        
        # Check optional fields (can be null)
        for field in optional_fields:
            assert field in item, f"❌ Item '{key}' missing optional field '{field}'"
        
        # Count populated optional fields
        if item.get("dps"):
            items_with_damage += 1
        if item.get("model"):
            items_with_model += 1
    
    total_items = len(db["items"])
    print(f"✅ All {total_items} items have required fields")
    print(f"✅ Items with damage info: {items_with_damage}/{total_items}")
    print(f"✅ Items with model ID: {items_with_model}/{total_items}")
    
    print(f"\n✅ TEST 4 PASSED\n")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("DATABASE v2.0 - TEST SUITE")
    print("="*80)
    
    try:
        test_database_structure()
        test_composite_key_generation()
        test_database_lookup()
        test_data_completeness()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
