"""
Test script to verify migration messages are correctly translated
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.language_manager import LanguageManager

def test_migration_messages():
    """Test migration messages in all languages"""
    
    print("=" * 70)
    print("TEST: Migration Messages Translation")
    print("=" * 70)
    print()
    
    languages = {
        'fr': 'Français',
        'en': 'English',
        'de': 'Deutsch'
    }
    
    keys_to_test = [
        'migration_success_message',
        'migration_no_characters',
        'migration_backup_location',
        'migration_in_progress',
        'migration_success',
        'migration_error'
    ]
    
    for lang_code, lang_name in languages.items():
        print(f"\n{'='*70}")
        print(f"🌍 {lang_name} ({lang_code})")
        print('='*70)
        
        lang = LanguageManager(lang_code)
        
        for key in keys_to_test:
            if key == 'migration_success_message':
                # Test with count parameter
                value = lang.get(key, count=5)
                print(f"✅ {value}")
            elif key == 'migration_backup_location':
                # Test with icon
                value = lang.get(key)
                print(f"💾 {value}")
                print(f"   C:\\Path\\To\\Backup\\backup_20251029_120000.zip")
            else:
                value = lang.get(key)
                print(f"  {key}: {value}")
        
        print()
    
    print("=" * 70)
    print("✅ Test completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_migration_messages()
