#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de construction de la base de données items depuis des fichiers .txt d'armures Zenkcraft
Parse tous les fichiers .txt d'un dossier et extrait les noms d'items pour les chercher sur Eden
"""

import os
import json
import re
from pathlib import Path
from Functions.items_scraper import ItemsScraper
from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager

def parse_zenkcraft_file(file_path):
    """
    Parse un fichier .txt Zenkcraft et extrait tous les noms d'items
    
    Args:
        file_path: Chemin vers le fichier .txt
        
    Returns:
        list: Liste des noms d'items trouvés
    """
    items = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex pour extraire les items depuis "Name: item_name" (format Zenkcraft)
        # Ignore les lignes "Name: " vides et les items spellcraft sans nom
        item_pattern = r'^Name:\s*(.+?)$'
        matches = re.findall(item_pattern, content, re.MULTILINE)
        
        for item_name in matches:
            item_name = item_name.strip()
            # Ignore les noms vides ou très courts (probablement des erreurs)
            if item_name and len(item_name) > 2 and item_name not in items:
                items.append(item_name)
        
        print(f"  ✅ {file_path.name}: {len(items)} items trouvés")
        
    except Exception as e:
        print(f"  ❌ Erreur lecture {file_path.name}: {e}")
    
    return items

def search_item_for_database(item_name, items_scraper, realm="All"):
    """
    Recherche un item et retourne les données formatées pour la base
    
    Args:
        item_name: Nom de l'item
        items_scraper: Instance de ItemsScraper
        realm: Royaume (défaut: All)
        
    Returns:
        dict: Données de l'item ou None si non trouvé
    """
    print(f"    🔍 Recherche: {item_name}")
    
    # Find ID
    item_id = items_scraper.find_item_id(item_name, realm)
    
    if not item_id:
        print(f"      ❌ ID non trouvé")
        return None
    
    print(f"      ✅ ID trouvé: {item_id}")
    
    # Get details
    details = items_scraper.get_item_details(item_id, realm)
    
    if not details:
        print(f"      ❌ Détails non disponibles")
        return None
    
    # Format for database
    item_data = {
        "id": item_id,
        "name": details.get("name") or item_name,
        "slot": details.get("slot") or "Unknown",
        "realm": details.get("realm") or realm
    }
    
    # Add merchant info if available
    merchants = details.get('merchants', [])
    if merchants:
        merchant = merchants[0]
        price_parsed = merchant.get("price_parsed")
        
        item_data["merchant_zone"] = merchant.get("zone") or "Unknown"
        item_data["merchant_price"] = str(price_parsed.get("amount")) if price_parsed else "Unknown"
        
        print(f"      ✅ Merchant: {item_data['merchant_zone']} - {item_data['merchant_price']}")
    else:
        print(f"      ⚠️  Pas d'info merchant")
    
    return item_data

def build_database_from_folder(folder_path, output_file=None, realm="All"):
    """
    Parse tous les fichiers .txt d'un dossier et construit la base de données
    
    Args:
        folder_path: Chemin vers le dossier contenant les .txt
        output_file: Chemin du fichier de sortie (défaut: Data/items_database.json)
        realm: Royaume pour la recherche (défaut: All)
    """
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print(f"❌ Dossier introuvable: {folder_path}")
        return
    
    # Find all .txt files
    txt_files = list(folder.glob("*.txt"))
    
    if not txt_files:
        print(f"❌ Aucun fichier .txt trouvé dans {folder_path}")
        return
    
    print(f"\n{'='*80}")
    print(f"📁 Dossier: {folder_path}")
    print(f"📄 {len(txt_files)} fichiers .txt trouvés")
    print(f"{'='*80}\n")
    
    # Parse all files and collect unique items
    all_items = []
    for txt_file in txt_files:
        items = parse_zenkcraft_file(txt_file)
        all_items.extend(items)
    
    # Remove duplicates (case insensitive)
    unique_items = {}
    for item in all_items:
        key = item.lower()
        if key not in unique_items:
            unique_items[key] = item
    
    print(f"\n{'='*80}")
    print(f"📦 Total: {len(all_items)} items trouvés")
    print(f"🔹 Uniques: {len(unique_items)} items")
    print(f"{'='*80}\n")
    
    # Initialize scraper
    print("🔧 Initialisation du scraper...")
    cookie_manager = CookieManager()
    eden_scraper = EdenScraper(cookie_manager)
    
    # Initialize driver (NOT headless for items database)
    if not eden_scraper.initialize_driver(headless=False, minimize=True):
        print("❌ Erreur initialisation driver")
        return
    
    # Load cookies
    if not eden_scraper.load_cookies():
        print("❌ Erreur chargement cookies")
        eden_scraper.close()
        return
    
    items_scraper = ItemsScraper(eden_scraper)
    print("✅ Scraper initialisé\n")
    
    # Search each item
    database_items = {}
    success_count = 0
    fail_count = 0
    
    try:
        for idx, (key, item_name) in enumerate(unique_items.items(), 1):
            print(f"\n[{idx}/{len(unique_items)}] {item_name}")
            
            item_data = search_item_for_database(item_name, items_scraper, realm)
            
            if item_data:
                database_items[key] = item_data
                success_count += 1
            else:
                fail_count += 1
    finally:
        # Close scraper
        eden_scraper.close()
        print("\n🔒 Scraper fermé")
    
    # Build final database structure
    database = {
        "version": "1.0",
        "description": "DAOC items database - IDs and basic information",
        "last_updated": "2025-11-17",
        "items": database_items,
        "notes": [
            "This file is the application's embedded database",
            "It contains the most common items",
            "Keys are lowercase names for searching",
            "On first startup, this file is copied to Armory/items_cache.json",
            "Users can customize their cache without modifying the database"
        ]
    }
    
    # Save database
    if output_file is None:
        output_file = Path("Data/items_database.json")
    else:
        output_file = Path(output_file)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"RÉSUMÉ")
    print(f"{'='*80}")
    print(f"✅ Succès: {success_count} items")
    print(f"❌ Échecs: {fail_count} items")
    print(f"💾 Base sauvegardée: {output_file}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build_items_database.py <folder_path> [realm] [output_file]")
        print("\nExemples:")
        print("  python build_items_database.py Templates/Armures")
        print("  python build_items_database.py Templates/Armures Hibernia")
        print("  python build_items_database.py Templates/Armures All Data/items_database.json")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    realm = sys.argv[2] if len(sys.argv) > 2 else "All"
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    build_database_from_folder(folder_path, output_file, realm)
