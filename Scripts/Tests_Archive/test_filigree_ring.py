#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test pour trouver l'ID et les détails de Filigree Antalya Ring
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from test_find_item_id import find_item_id
from test_item_details import get_item_details

if __name__ == "__main__":
    print("=" * 80)
    print("RECHERCHE: Filigree Antalya Ring (Hibernia)")
    print("=" * 80)
    
    # Step 1: Find item ID
    item_id = find_item_id("Filigree Antalya Ring", "Hibernia")
    
    if item_id:
        print(f"\n{'=' * 80}")
        print(f"DÉTAILS DE L'ITEM ID: {item_id}")
        print("=" * 80)
        
        # Step 2: Get item details
        item_details = get_item_details(item_id, "Hibernia")
        
        if item_details:
            print(f"\n{'=' * 80}")
            print("RÉSUMÉ COMPLET")
            print("=" * 80)
            print(f"Nom: {item_details['name']}")
            print(f"ID: {item_details['id']}")
            print(f"Type: {item_details['type']}")
            print(f"Slot: {item_details['slot']}")
            print(f"Royaume: {item_details['realm']}")
    else:
        print("\n❌ Impossible de trouver l'item")
