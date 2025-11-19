#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de parsing des fichiers template d'items
Parse les fichiers .txt template et extrait les noms d'items pour les chercher sur Eden
"""

import os
import json
import re
from pathlib import Path
from .items_scraper import ItemsScraper
from .eden_scraper import EdenScraper
from .cookie_manager import CookieManager

def parse_template_file(file_path):
    """
    Parse un fichier .txt template et extrait tous les noms d'items de type Loot
    
    Args:
        file_path: Chemin vers le fichier .txt (str ou Path)
        
    Returns:
        list: Liste des noms d'items trouvés (uniquement Source Type: Loot)
    """
    items = []
    
    try:
        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into item blocks (separated by double newlines)
        # Each block contains: Name, Level, Utility, Source Type, etc.
        item_blocks = re.split(r'\n\n+', content)
        
        for block in item_blocks:
            # Check if this block has both "Name:" and "Source Type: Loot"
            if 'Name:' in block and 'Source Type: Loot' in block:
                # Extract item name
                name_match = re.search(r'^Name:\s*(.+?)$', block, re.MULTILINE)
                if name_match:
                    item_name = name_match.group(1).strip()
                    # Skip empty names (length > 2 to avoid single char errors) or duplicates
                    if item_name and len(item_name) > 2 and item_name not in items:
                        items.append(item_name)
        
        print(f"  ✅ {file_path.name}: {len(items)} items Loot trouvés")
        
    except Exception as e:
        print(f"  ❌ Erreur lecture {file_path.name if hasattr(file_path, 'name') else file_path}: {e}")
    
    return items

def search_item_for_database(item_name, items_scraper, realm="All", force_scrape=False):
    """
    Recherche un item et retourne les données formatées pour la base v2.0
    Inclut: id, name, realm, slot, type, model, dps, speed, damage_type, merchant
    
    Args:
        item_name: Nom de l'item
        items_scraper: Instance de ItemsScraper
        realm: Royaume (défaut: All)
        force_scrape: Si True, force le scraping web (pour refresh DB)
        
    Returns:
        dict: Données de l'item ou None si non trouvé
    """
    print(f"    🔍 Recherche: {item_name} ({realm}) [force_scrape={force_scrape}]")
    
    # Find ID (force web scraping if requested)
    item_id = items_scraper.find_item_id(item_name, realm, force_scrape=force_scrape)
    
    if not item_id:
        print(f"      ❌ ID non trouvé")
        return None
    
    print(f"      ✅ ID trouvé: {item_id}")
    
    # Get details
    details = items_scraper.get_item_details(item_id, realm, item_name)
    
    if not details:
        print(f"      ❌ Détails non disponibles")
        return None
    
    # Format for database v2.0 (minimal data)
    item_data = {
        "id": item_id,
        "name": details.get("name") or item_name,
        "realm": details.get("realm") or realm,
        "slot": details.get("slot") or "Unknown",
        "type": details.get("type"),
        "model": details.get("model"),
        "dps": details.get("dps"),
        "speed": details.get("speed"),
        "damage_type": details.get("damage_type")
    }
    
    # Add merchant info if available
    merchants = details.get('merchants', [])
    if merchants:
        merchant = merchants[0]
        price_parsed = merchant.get("price_parsed")
        
        item_data["merchant_zone"] = merchant.get("zone") or "Unknown"
        item_data["merchant_price"] = str(price_parsed.get("amount")) if price_parsed else "Unknown"
        
        print(f"      ✅ Merchant: {item_data['merchant_zone']} - {item_data['merchant_price']}")
        
        # Log damage info if available
        if item_data.get("dps"):
            print(f"      ⚔️  Damage: DPS {item_data['dps']}, Speed {item_data['speed']}, Type {item_data['damage_type']}")
        if item_data.get("model"):
            print(f"      🎨 Model: {item_data['model']}")
    else:
        print(f"      ⚠️  Pas d'info merchant")
    
    return item_data

def build_database_from_folder(folder_path, output_file=None, realm="All"):
    """
    Parse tous les fichiers .txt d'un dossier et construit la base de données
    
    Args:
        folder_path: Chemin vers le dossier contenant les .txt
        output_file: Chemin du fichier de sortie (défaut: Data/items_database_src.json)
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
        items = parse_template_file(txt_file)
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
        output_file = Path("Data/items_database_src.json")
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
        print("  python build_items_database.py Templates/Armures All Data/items_database_src.json")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    realm = sys.argv[2] if len(sys.argv) > 2 else "All"
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    build_database_from_folder(folder_path, output_file, realm)
