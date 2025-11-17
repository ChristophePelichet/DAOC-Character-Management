#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour rechercher et ajouter des items à la base de données
"""

from test_find_item_id import find_item_id
from test_item_details import get_item_details

def search_and_add_item(item_name, realm=None):
    """
    Recherche un item et affiche ses détails pour l'ajouter à la base
    
    Args:
        item_name: Nom de l'item
        realm: Royaume (None = recherche dans tous les royaumes)
    """
    # Si pas de royaume spécifié, rechercher dans "All"
    search_realm = realm if realm else "All"
    
    print("=" * 80)
    print(f"RECHERCHE: {item_name} (Royaume: {search_realm})")
    print("=" * 80)
    
    # Find ID
    item_id = find_item_id(item_name, search_realm)
    
    if item_id:
        print(f"\n{'=' * 80}")
        print(f"DÉTAILS: {item_name} (ID: {item_id})")
        print("=" * 80)
        
        # Get details
        details = get_item_details(item_id, search_realm)
        
        if details:
            print(f"\n{'=' * 80}")
            print("RÉSUMÉ POUR BASE DE DONNÉES")
            print("=" * 80)
            print(f'"{item_name.lower()}": {{')
            print(f'    "id": "{item_id}",')
            print(f'    "name": "{details.get("name") or item_name}",')
            print(f'    "slot": "{details.get("slot") or "Unknown"}",')
            print(f'    "realm": "{details.get("realm") or search_realm}",')
            
            # Merchant info
            merchants = details.get('merchants', [])
            if merchants:
                merchant = merchants[0]
                price_parsed = merchant.get("price_parsed")
                price_value = str(price_parsed.get("amount")) if price_parsed else "Unknown"
                print(f'    "merchant_zone": "{merchant.get("zone") or "Unknown"}",')
                print(f'    "merchant_price": "{price_value}"')
            else:
                print(f'    "merchant_zone": "Unknown",')
                print(f'    "merchant_price": "Unknown"')
            
            print('},')
            
            return details
    
    return None

if __name__ == "__main__":
    # Pas de royaume spécifié = recherche dans "All"
    search_and_add_item("Rigid Razorback Jerkin")
