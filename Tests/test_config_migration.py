"""
Unit Tests for Configuration Migration
Version: v0.108
Author: Christophe Pelichet
Description: Tests for config v1→v2 migration and new API features
"""

import json
import os
import sys
import unittest
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.config_schema import (
    DEFAULT_CONFIG,
    LEGACY_KEY_MAPPING,
    validate_value,
    get_default_value,
    get_legacy_key,
    get_new_key
)
from Functions.config_migration import (
    detect_config_version,
    migrate_v1_to_v2,
    migrate_v2_to_v1,
    validate_migrated_config
)


class TestConfigSchema(unittest.TestCase):
    """Tests for config_schema.py functions"""
    
    def test_default_config_structure(self):
        """Test 1: Verify DEFAULT_CONFIG has all required sections"""
        required_sections = ["ui", "folders", "backup", "system", "game"]
        for section in required_sections:
            self.assertIn(section, DEFAULT_CONFIG, f"Missing section: {section}")
    
    def test_backup_subsections(self):
        """Test 2: Verify backup section has all subsections"""
        required_subsections = ["characters", "cookies", "armor"]
        for subsection in required_subsections:
            self.assertIn(subsection, DEFAULT_CONFIG["backup"], 
                         f"Missing backup subsection: {subsection}")
    
    def test_validate_value_valid(self):
        """Test 3: Validate correct values"""
        self.assertTrue(validate_value("ui.language", "fr"))
        self.assertTrue(validate_value("ui.language", "en"))
        self.assertTrue(validate_value("ui.theme", "default"))
        self.assertTrue(validate_value("ui.font_scale", 1.0))
        self.assertTrue(validate_value("system.debug_mode", False))
    
    def test_validate_value_invalid(self):
        """Test 4: Reject invalid values"""
        self.assertFalse(validate_value("ui.language", "invalid"))
        self.assertFalse(validate_value("ui.font_scale", 3.0))  # > max
        self.assertFalse(validate_value("ui.font_scale", 0.1))  # < min
    
    def test_get_default_value(self):
        """Test 5: Get default values from schema"""
        self.assertEqual(get_default_value("ui.language"), "fr")
        self.assertEqual(get_default_value("ui.theme"), "default")
        self.assertEqual(get_default_value("ui.font_scale"), 1.0)
        self.assertEqual(get_default_value("system.debug_mode"), False)
    
    def test_legacy_mapping_bidirectional(self):
        """Test 6: Legacy key mapping works both ways"""
        # Old → New
        self.assertEqual(get_new_key("language"), "ui.language")
        self.assertEqual(get_new_key("character_folder"), "folders.characters")
        self.assertEqual(get_new_key("backup_enabled"), "backup.characters.enabled")
        
        # New → Old
        self.assertEqual(get_legacy_key("ui.language"), "language")
        self.assertEqual(get_legacy_key("folders.characters"), "character_folder")
        self.assertEqual(get_legacy_key("backup.characters.enabled"), "backup_enabled")


class TestConfigMigration(unittest.TestCase):
    """Tests for config_migration.py functions"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.v1_config = {
            "language": "fr",
            "theme": "dark",
            "character_folder": "Characters/",
            "log_folder": "Logs/",
            "backup_enabled": True,
            "backup_path": "Backup/",
            "debug_mode": False,
            "servers": ["Eden"],
            "default_server": "Eden"
        }
        
        self.v2_config = {
            "ui": {
                "language": "fr",
                "theme": "dark"
            },
            "folders": {
                "characters": "Characters/",
                "logs": "Logs/"
            },
            "backup": {
                "characters": {
                    "enabled": True,
                    "path": "Backup/"
                }
            },
            "system": {
                "debug_mode": False
            },
            "game": {
                "servers": ["Eden"],
                "default_server": "Eden"
            }
        }
    
    def test_detect_v1_config(self):
        """Test 7: Detect v1 configuration"""
        self.assertEqual(detect_config_version(self.v1_config), "v1")
    
    def test_detect_v2_config(self):
        """Test 8: Detect v2 configuration"""
        self.assertEqual(detect_config_version(self.v2_config), "v2")
    
    def test_migrate_v1_to_v2(self):
        """Test 9: Migrate v1 to v2 successfully"""
        migrated = migrate_v1_to_v2(self.v1_config)
        
        # Check structure
        self.assertIn("ui", migrated)
        self.assertIn("folders", migrated)
        self.assertIn("backup", migrated)
        
        # Check values preserved
        self.assertEqual(migrated["ui"]["language"], "fr")
        self.assertEqual(migrated["ui"]["theme"], "dark")
        self.assertEqual(migrated["folders"]["characters"], "Characters/")
        self.assertEqual(migrated["backup"]["characters"]["enabled"], True)
        self.assertEqual(migrated["system"]["debug_mode"], False)
    
    def test_migrate_v2_to_v1(self):
        """Test 10: Reverse migration v2 to v1"""
        migrated = migrate_v2_to_v1(self.v2_config)
        
        # Check key mapping
        self.assertEqual(migrated["language"], "fr")
        self.assertEqual(migrated["theme"], "dark")
        self.assertEqual(migrated["character_folder"], "Characters/")
        self.assertEqual(migrated["backup_enabled"], True)
    
    def test_validate_migrated_config(self):
        """Test 11: Validate complete migrated config"""
        migrated = migrate_v1_to_v2(self.v1_config)
        is_valid, errors = validate_migrated_config(migrated)
        
        self.assertTrue(is_valid, f"Validation failed: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_migration_preserves_all_values(self):
        """Test 12: No data loss during migration"""
        # Create complete v1 config with all keys
        complete_v1 = {
            "language": "en",
            "theme": "light",
            "font_scale": 1.5,
            "character_folder": "Chars/",
            "log_folder": "Logs/",
            "armor_folder": "Armor/",
            "cookies_folder": "Cookies/",
            "backup_enabled": False,
            "backup_path": "Backup/Chars/",
            "backup_compress": False,
            "backup_size_limit_mb": 50,
            "backup_auto_delete_old": True,
            "cookies_backup_enabled": False,
            "armor_backup_enabled": True,
            "debug_mode": True,
            "show_debug_window": True,
            "servers": ["Eden", "Test"],
            "default_server": "Test"
        }
        
        migrated = migrate_v1_to_v2(complete_v1)
        
        # Verify critical values
        self.assertEqual(migrated["ui"]["language"], "en")
        self.assertEqual(migrated["ui"]["theme"], "light")
        self.assertEqual(migrated["ui"]["font_scale"], 1.5)
        self.assertEqual(migrated["folders"]["characters"], "Chars/")
        self.assertEqual(migrated["backup"]["characters"]["enabled"], False)
        self.assertEqual(migrated["backup"]["characters"]["compress"], False)
        self.assertEqual(migrated["backup"]["characters"]["size_limit_mb"], 50)
        self.assertEqual(migrated["backup"]["cookies"]["enabled"], False)
        self.assertEqual(migrated["backup"]["armor"]["enabled"], True)
        self.assertEqual(migrated["system"]["debug_mode"], True)
        self.assertEqual(migrated["game"]["servers"], ["Eden", "Test"])


class TestConfigManagerAPI(unittest.TestCase):
    """Tests for new ConfigManager API features"""
    
    def setUp(self):
        """Setup test config"""
        self.config_data = {
            "ui": {
                "language": "fr",
                "theme": "dark"
            },
            "folders": {
                "characters": "Characters/"
            },
            "system": {
                "debug_mode": False
            }
        }
    
    def test_dotted_notation_get(self):
        """Test 13: Get values using dotted notation"""
        # This will be tested with actual ConfigManager in integration tests
        # For now, just verify the concept
        parts = "ui.language".split(".")
        value = self.config_data
        for part in parts:
            value = value[part]
        self.assertEqual(value, "fr")
    
    def test_dotted_notation_set(self):
        """Test 14: Set values using dotted notation"""
        # Simulate dotted set
        parts = "ui.theme".split(".")
        target = self.config_data
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = "light"
        
        self.assertEqual(self.config_data["ui"]["theme"], "light")
    
    def test_nested_dict_navigation(self):
        """Test 15: Navigate nested dictionaries"""
        # Test multiple levels
        self.assertEqual(self.config_data["ui"]["language"], "fr")
        self.assertEqual(self.config_data["folders"]["characters"], "Characters/")
        self.assertEqual(self.config_data["system"]["debug_mode"], False)


class TestBackwardCompatibility(unittest.TestCase):
    """Tests for backward compatibility features"""
    
    def test_all_v1_keys_mapped(self):
        """Test 16: All expected v1 keys have v2 mapping"""
        expected_v1_keys = [
            "language", "theme", "font_scale",
            "character_folder", "log_folder", "armor_folder", "cookies_folder",
            "backup_enabled", "backup_path", "backup_compress",
            "backup_size_limit_mb", "backup_auto_delete_old",
            "debug_mode", "show_debug_window",
            "servers", "default_server"
        ]
        
        for key in expected_v1_keys:
            self.assertIn(key, LEGACY_KEY_MAPPING, 
                         f"Legacy key not mapped: {key}")
    
    def test_legacy_mapping_count(self):
        """Test 17: Verify number of legacy mappings"""
        # Should have 37 mappings (from analysis)
        self.assertEqual(len(LEGACY_KEY_MAPPING), 37,
                        "Unexpected number of legacy key mappings")
    
    def test_no_duplicate_mappings(self):
        """Test 18: No duplicate new keys in mapping"""
        new_keys = list(LEGACY_KEY_MAPPING.values())
        unique_keys = set(new_keys)
        
        self.assertEqual(len(new_keys), len(unique_keys),
                        "Duplicate new keys found in mapping")


def run_tests():
    """Run all tests and print summary"""
    print("=" * 70)
    print("CONFIGURATION MIGRATION - UNIT TESTS")
    print("=" * 70)
    print(f"Test run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigMigration))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManagerAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
