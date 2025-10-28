"""
Script to test the armor management system.
"""

import sys
import os
import logging

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.config_manager import config
from Functions.path_manager import get_armor_dir, ensure_armor_dir
from Functions.armor_manager import ArmorManager

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_armor_paths():
    """Test armor directory creation and path retrieval."""
    print("\n=== Test 1: Armor Paths ===")
    
    # Test get_armor_dir
    armor_dir = get_armor_dir()
    print(f"Armor directory path: {armor_dir}")
    
    # Test ensure_armor_dir
    ensure_armor_dir()
    print(f"Armor directory exists: {os.path.exists(armor_dir)}")
    
    return armor_dir

def test_armor_manager():
    """Test ArmorManager basic functionality."""
    print("\n=== Test 2: Armor Manager ===")
    
    # Create ArmorManager for a test character
    test_character_id = "test_char_001"
    armor_mgr = ArmorManager(test_character_id)
    
    print(f"Character ID: {test_character_id}")
    print(f"Character armor folder: {armor_mgr.armor_dir}")
    print(f"Folder exists: {os.path.exists(armor_mgr.armor_dir)}")
    
    # List armors
    armors = armor_mgr.list_armors()
    print(f"Number of armor files: {armor_mgr.get_armor_count()}")
    
    if armors:
        print("\nArmor files:")
        for armor in armors:
            print(f"  - {armor['filename']} ({armor['size']} bytes)")
    else:
        print("  No armor files found.")
    
    return armor_mgr

def test_file_operations():
    """Test file upload simulation."""
    print("\n=== Test 3: File Operations ===")
    
    test_character_id = "test_char_002"
    armor_mgr = ArmorManager(test_character_id)
    
    # Create a temporary test file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("Test armor file content\n")
        temp_file.write("This is a test file for armor upload.\n")
        temp_path = temp_file.name
    
    try:
        print(f"Created test file: {temp_path}")
        
        # Upload the file
        print("Uploading file...")
        result_path = armor_mgr.upload_armor(temp_path)
        print(f"File uploaded to: {result_path}")
        
        # List armors
        armors = armor_mgr.list_armors()
        print(f"Armor count after upload: {len(armors)}")
        
        # Test duplicate upload
        print("\nTesting duplicate upload...")
        result_path2 = armor_mgr.upload_armor(temp_path)
        print(f"Duplicate file uploaded to: {result_path2}")
        
        armors = armor_mgr.list_armors()
        print(f"Armor count after duplicate: {len(armors)}")
        
        # Test deletion
        if armors:
            filename_to_delete = armors[0]['filename']
            print(f"\nDeleting file: {filename_to_delete}")
            armor_mgr.delete_armor(filename_to_delete)
            print(f"Armor count after deletion: {armor_mgr.get_armor_count()}")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"\nCleaned up test file: {temp_path}")

def main():
    """Main test function."""
    print("=" * 60)
    print("Armor Manager Test Script")
    print("=" * 60)
    
    try:
        # Test 1: Paths
        armor_dir = test_armor_paths()
        
        # Test 2: Manager
        armor_mgr = test_armor_manager()
        
        # Test 3: File operations
        test_file_operations()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
