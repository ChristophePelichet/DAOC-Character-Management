"""
Test script for Wealth Manager
Tests the get_realm_money function to retrieve Money values for all realms

Usage:
    python Scripts/test_wealth_manager.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Functions.wealth_manager import get_realm_money, get_first_character_per_realm
from Functions.config_manager import config


def test_realm_money():
    """Test getting Money for all realms"""
    
    print("=" * 80)
    print("Wealth Manager - Realm Money Test")
    print("=" * 80)
    
    # Get character folder from config
    character_folder = config.get('character_folder')
    
    if not character_folder:
        print("\n❌ ERROR: No character folder configured!")
        print("Please configure the character folder in settings.")
        return False
    
    print(f"\nCharacter folder: {character_folder}")
    
    if not os.path.exists(character_folder):
        print(f"\n❌ ERROR: Character folder does not exist: {character_folder}")
        return False
    
    # First, show which characters will be used
    print("\n" + "-" * 80)
    print("Characters selected (level 11+ required):")
    print("-" * 80)
    
    characters = get_first_character_per_realm(character_folder)
    for realm, char_info in characters.items():
        if char_info:
            print(f"  {realm:12} → {char_info['name']}")
        else:
            print(f"  {realm:12} → No character found")
    
    print("\n" + "-" * 80)
    print("Retrieving Money values for all realms...")
    print("(This will open a browser window, please wait...)")
    print("-" * 80)
    
    # Get Money for all realms
    result = get_realm_money(character_folder)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if result['success']:
        print("\n✅ SUCCESS!")
        print("\nMoney by Realm:")
        print(f"  Albion:    {result['Albion']}")
        print(f"  Midgard:   {result['Midgard']}")
        print(f"  Hibernia:  {result['Hibernia']}")
        
        if result['errors']:
            print("\n⚠️  Warnings/Errors:")
            for error in result['errors']:
                print(f"  - {error}")
    else:
        print("\n❌ FAILED!")
        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")
    
    print("=" * 80)
    
    return result['success']


if __name__ == "__main__":
    print("\n🪙 Wealth Manager Test\n")
    
    success = test_realm_money()
    
    print()
    sys.exit(0 if success else 1)
