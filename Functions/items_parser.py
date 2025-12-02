#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de parsing des fichiers template d'items
Parse les fichiers .txt template et extrait les noms d'items pour les chercher sur Eden
"""

import os
import json
import re
import logging
from pathlib import Path
from .items_scraper import ItemsScraper
from .eden_scraper import EdenScraper, _connect_to_eden_herald
from .cookie_manager import CookieManager

def parse_template_file(file_path):
    """
    Parse un fichier .txt template et extrait tous les noms d'items de type Loot
    Supporte 3 formats:
    - Format standard: blocs séparés par double newline
    - Format Zenkcraft: sections d'équipement (Helmet, Hands, etc.)
    - Format externe: "Slot (Item Name):" (templates from non-Zenkcraft software)
    
    Args:
        file_path: Chemin vers le fichier .txt (str ou Path)
        
    Returns:
        list: Liste des noms d'items trouvés (uniquement Source Type: Loot pour formats standard/Zenkcraft)
    """
    items = []
    
    try:
        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect external template format: "Slot (Item Name):"
        external_pattern = r'^(Chest|Arms|Head|Legs|Hands|Feet|Right Hand|Left Hand|Neck|Cloak|Jewel|Belt|Left Ring|Right Ring|Left Wrist|Right Wrist|Mythirian) \((.+?)\):$'
        external_matches = re.findall(external_pattern, content, re.MULTILINE)
        
        if external_matches:
            # External template format detected
            for slot, item_name in external_matches:
                item_name = item_name.strip()
                if item_name and len(item_name) > 2 and item_name not in items:
                    items.append(item_name)
            
            logging.info(f"{file_path.name}: {len(items)} items found (External template format)")
            return items
        
        # Detect Zenkcraft format (has equipment sections like "Helmet", "Hands", etc.)
        is_zenkcraft = bool(re.search(r'^(Helmet|Hands|Torso|Arms|Feet|Legs|Right Hand|Left Hand|Two Handed|Ranged|Neck|Cloak|Jewelry|Waist|L Ring|R Ring|L Wrist|R Wrist|Mythical)\s*$', content, re.MULTILINE))
        
        if is_zenkcraft:
            # Parse Zenkcraft format: split by equipment sections
            # Sections are single words/phrases followed by item details
            equipment_sections = re.split(r'\n(?=(?:Helmet|Hands|Torso|Arms|Feet|Legs|Right Hand|Left Hand|Two Handed|Ranged|Neck|Cloak|Jewelry|Waist|L Ring|R Ring|L Wrist|R Wrist|Mythical)\s*\n)', content)
            
            for section in equipment_sections:
                # Check if section has Name: and Source Type: Loot
                if 'Name:' in section and 'Source Type: Loot' in section:
                    name_match = re.search(r'^Name:\s*(.+?)$', section, re.MULTILINE)
                    if name_match:
                        item_name = name_match.group(1).strip()
                        # Skip empty names or duplicates
                        if item_name and len(item_name) > 2 and item_name not in items:
                            items.append(item_name)
        else:
            # Original format: double newline separated blocks
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
        
        logging.info(f"{file_path.name}: {len(items)} items Loot found {'(Zenkcraft)' if is_zenkcraft else '(Standard format)'}")
        
    except Exception as e:
        logging.error(f"Error reading {file_path.name if hasattr(file_path, 'name') else file_path}: {e}")
    
    return items

def search_item_for_database(item_name, items_scraper, realm="All", force_scrape=False, skip_filters=False):
    """
    Recherche un item et retourne les données formatées pour la base v2.0
    Inclut: id, name, realm, slot, type, model, dps, speed, damage_type, merchant
    
    Args:
        item_name: Nom de l'item
        items_scraper: Instance de ItemsScraper
        realm: Royaume (défaut: All)
        force_scrape: Si True, force le scraping web (pour refresh DB)
        skip_filters: Si True, ignore les filtres level/utility (retry mode)
        
    Returns:
        dict: Données de l'item ou None si non trouvé
    """
    logging.info(f"Searching: {item_name} ({realm}) [force_scrape={force_scrape}, skip_filters={skip_filters}]")
    
    # Find ID (force web scraping if requested, with optional filter bypass)
    item_id = items_scraper.find_item_id(item_name, realm, force_scrape=force_scrape, skip_filters=skip_filters)
    
    if not item_id:
        logging.warning(f"ID not found: {item_name}")
        return None
    
    logging.info(f"ID found: {item_id} ({item_name})")
    
    # Get details
    details = items_scraper.get_item_details(item_id, realm, item_name)
    
    if not details:
        logging.warning(f"Details not available: {item_name}")
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
        item_data["merchant_currency"] = price_parsed.get("currency") if price_parsed else ""
        
        logging.info(f"Merchant: {item_data['merchant_zone']} - {item_data['merchant_price']} {item_data.get('merchant_currency', '')}")
        
        # Log damage info if available
        if item_data.get("dps"):
            logging.info(f"Damage: DPS {item_data['dps']}, Speed {item_data['speed']}, Type {item_data['damage_type']}")
        if item_data.get("model"):
            logging.info(f"Model: {item_data['model']}")
    else:
        logging.warning(f"No merchant info: {item_name}")
    
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
        logging.error(f"Folder not found: {folder_path}")
        return
    
    # Find all .txt files
    txt_files = list(folder.glob("*.txt"))
    
    if not txt_files:
        logging.error(f"No .txt files found in {folder_path}")
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
    
    logging.info(f"Total: {len(all_items)} items found")
    logging.info(f"Unique: {len(unique_items)} items")
    
    # Initialize scraper using centralized connection
    logging.info("Initializing scraper...")
    eden_scraper, error_message = _connect_to_eden_herald(headless=False)
    if not eden_scraper:
        logging.error(f"Eden Herald connection error: {error_message}")
        return
    
    items_scraper = ItemsScraper(eden_scraper)
    logging.info("Scraper initialized")
    
    # Search each item
    database_items = {}
    success_count = 0
    fail_count = 0
    
    try:
        for idx, (key, item_name) in enumerate(unique_items.items(), 1):
            logging.info(f"[{idx}/{len(unique_items)}] {item_name}")
            
            item_data = search_item_for_database(item_name, items_scraper, realm)
            
            if item_data:
                database_items[key] = item_data
                success_count += 1
            else:
                fail_count += 1
    finally:
        # Close scraper
        eden_scraper.close()
        logging.info("Scraper closed")
    
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
    logging.info(f"Success: {success_count} items")
    logging.info(f"Failed: {fail_count} items")
    logging.info(f"Database saved: {output_file}")

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
