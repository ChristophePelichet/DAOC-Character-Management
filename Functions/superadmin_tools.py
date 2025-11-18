"""
SuperAdmin Tools for Database Management
Version: v0.108
Author: Christophe Pelichet
Description: Administrative tools for building and managing the source items database

SECURITY: Only accessible via --admin flag in Python mode (not in compiled .exe)

Features:
- Build source database from multiple .txt template files
- Merge with existing database (add without duplicates)
- Clean duplicates (same name + realm)
- Get database statistics
- Backup management
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

from Functions.path_manager import PathManager
from Functions.items_parser import parse_template_file, search_item_for_database
from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
from Functions.items_scraper import ItemsScraper


class SuperAdminTools:
    """Administrative tools for source database management"""
    
    def __init__(self, path_manager: PathManager):
        """
        Initialize SuperAdmin tools
        
        Args:
            path_manager: PathManager instance for resolving paths
        """
        self.path_manager = path_manager
        self.source_db_path = self.path_manager.get_app_root() / "Data" / "items_database_src.json"
        
        logging.info("SuperAdminTools initialized", extra={"action": "SUPERADMIN_INIT"})
    
    def get_database_stats(self) -> Dict:
        """
        Get statistics about the source database
        
        Returns:
            Dict with stats: total_items, by_realm counts, file_size, last_updated
        """
        try:
            if not self.source_db_path.exists():
                return {
                    "total_items": 0,
                    "albion": 0,
                    "hibernia": 0,
                    "midgard": 0,
                    "all_realms": 0,
                    "file_size": 0,
                    "last_updated": "Never"
                }
            
            with open(self.source_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            items = data.get("items", {})
            stats = {
                "total_items": len(items),
                "albion": 0,
                "hibernia": 0,
                "midgard": 0,
                "all_realms": 0,
                "file_size": self.source_db_path.stat().st_size,
                "last_updated": data.get("last_updated", "Unknown")
            }
            
            # Count by realm
            for item_data in items.values():
                realm = item_data.get("realm", "").lower()
                if realm == "albion":
                    stats["albion"] += 1
                elif realm == "hibernia":
                    stats["hibernia"] += 1
                elif realm == "midgard":
                    stats["midgard"] += 1
                elif realm == "all":
                    stats["all_realms"] += 1
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting database stats: {e}", extra={"action": "SUPERADMIN_STATS_ERROR"})
            return {
                "total_items": 0,
                "albion": 0,
                "hibernia": 0,
                "midgard": 0,
                "all_realms": 0,
                "file_size": 0,
                "last_updated": "Error"
            }
    
    def backup_source_database(self) -> Tuple[bool, str]:
        """
        Create a backup of the source database
        
        Returns:
            Tuple[bool, str]: (Success, Backup path or error message)
        """
        try:
            if not self.source_db_path.exists():
                return False, "Source database does not exist"
            
            # Create backup folder if needed
            backup_folder = self.path_manager.get_app_root() / "Data" / "Backups"
            backup_folder.mkdir(parents=True, exist_ok=True)
            
            # Backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_folder / f"items_database_src_backup_{timestamp}.json"
            
            # Copy file
            shutil.copy2(self.source_db_path, backup_path)
            
            logging.info(f"Source database backed up to {backup_path}", extra={"action": "SUPERADMIN_BACKUP"})
            return True, str(backup_path)
            
        except Exception as e:
            logging.error(f"Error backing up source database: {e}", extra={"action": "SUPERADMIN_BACKUP_ERROR"})
            return False, str(e)
    
    def parse_template_files(self, file_paths: List[str], realm: str = "All") -> Tuple[Dict, List[str]]:
        """
        Parse multiple .txt template files
        
        Args:
            file_paths: List of paths to .txt template files
            realm: Default realm if not auto-detected ("Albion", "Hibernia", "Midgard", "All")
        
        Returns:
            Tuple[Dict, List[str]]: (Parsed items dict, List of error messages)
        """
        parsed_items = {}
        errors = []
        
        for file_path in file_paths:
            try:
                file_path_obj = Path(file_path)
                
                # Auto-detect realm from filename
                detected_realm = realm
                filename_lower = file_path_obj.stem.lower()
                if "albion" in filename_lower:
                    detected_realm = "Albion"
                elif "hibernia" in filename_lower or "hib" in filename_lower:
                    detected_realm = "Hibernia"
                elif "midgard" in filename_lower or "mid" in filename_lower:
                    detected_realm = "Midgard"
                
                # Use existing parser to get item names
                item_names = parse_template_file(file_path)
                
                # If no items found with Loot filter, try parsing all Name: entries
                if not item_names:
                    # Fallback: parse all lines with "Name:" regardless of Source Type
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    import re
                    item_names = []
                    item_blocks = re.split(r'\n\n+', content)
                    
                    for block in item_blocks:
                        if 'Name:' in block:
                            name_match = re.search(r'^Name:\s*(.+?)$', block, re.MULTILINE)
                            if name_match:
                                item_name = name_match.group(1).strip()
                                if item_name and item_name not in item_names:
                                    item_names.append(item_name)
                
                if item_names:
                    # Create item data for each name
                    for item_name in item_names:
                        item_data = {
                            "name": item_name,
                            "realm": detected_realm,
                            "source": "internal"
                        }
                        
                        # Use lowercase name as key for consistency
                        key = item_name.lower()
                        
                        # Avoid duplicates
                        if key not in parsed_items:
                            parsed_items[key] = item_data
                    
                    logging.info(f"Parsed {len(item_names)} items from {file_path_obj.name}", 
                                extra={"action": "SUPERADMIN_PARSE"})
                else:
                    errors.append(f"No items found in {file_path_obj.name}")
                    
            except Exception as e:
                file_name = Path(file_path).name if file_path else "unknown"
                errors.append(f"Error parsing {file_name}: {str(e)}")
                logging.error(f"Error parsing {file_path}: {e}", extra={"action": "SUPERADMIN_PARSE_ERROR"})
        
        return parsed_items, errors
    
    def build_database_from_files(self, file_paths: List[str], realm: str = "All", 
                                   merge: bool = True, remove_duplicates: bool = True,
                                   auto_backup: bool = True) -> Tuple[bool, str, Dict]:
        """
        Build source database from multiple template files
        
        Args:
            file_paths: List of .txt template file paths
            realm: Default realm for items
            merge: If True, merge with existing DB; if False, replace completely
            remove_duplicates: Remove items with same name + realm
            auto_backup: Automatically backup old DB before saving
        
        Returns:
            Tuple[bool, str, Dict]: (Success, Message, Statistics dict)
        """
        try:
            # Parse all template files to get item names
            new_items_names, parse_errors = self.parse_template_files(file_paths, realm)
            
            if not new_items_names:
                return False, "No items parsed from template files", {}
            
            # Initialize Eden scraper for fetching item details
            logging.info("Initializing Eden scraper for item details...")
            cookie_manager = CookieManager()
            eden_scraper = EdenScraper(cookie_manager)
            
            # Initialize driver (NOT headless for database building)
            if not eden_scraper.initialize_driver(headless=False, minimize=True):
                return False, "Failed to initialize Eden scraper", {}
            
            # Load cookies
            if not eden_scraper.load_cookies():
                eden_scraper.close()
                return False, "Failed to load cookies. Please generate cookies first.", {}
            
            items_scraper = ItemsScraper(eden_scraper)
            logging.info("Eden scraper initialized successfully")
            
            # Load existing database if merging
            existing_items = {}
            if merge and self.source_db_path.exists():
                with open(self.source_db_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_items = existing_data.get("items", {})
            
            # Backup if requested
            if auto_backup and self.source_db_path.exists():
                success, backup_path = self.backup_source_database()
                if not success:
                    logging.warning(f"Backup failed: {backup_path}")
            
            # Fetch details for each item from Eden
            merged_items = existing_items.copy() if merge else {}
            duplicates_count = 0
            added_count = 0
            failed_count = 0
            
            try:
                total_items = len(new_items_names)
                for idx, (key, item_basic) in enumerate(new_items_names.items(), 1):
                    item_name = item_basic["name"]
                    item_realm = item_basic["realm"]
                    
                    logging.info(f"[{idx}/{total_items}] Searching: {item_name}")
                    
                    # Check for duplicates before scraping
                    if remove_duplicates and key in merged_items:
                        existing_realm = merged_items[key].get("realm", "")
                        if existing_realm.lower() == item_realm.lower():
                            duplicates_count += 1
                            logging.info(f"  Skipped (duplicate): {item_name}")
                            continue
                    
                    # Search item details on Eden
                    item_data = search_item_for_database(item_name, items_scraper, item_realm)
                    
                    if item_data:
                        # Check if item has merchant information (mandatory for price calculations)
                        if "merchant_zone" in item_data and "merchant_price" in item_data:
                            # Add source field
                            item_data["source"] = "internal"
                            merged_items[key] = item_data
                            added_count += 1
                            logging.info(f"  ✅ Added: {item_name}")
                        else:
                            failed_count += 1
                            logging.warning(f"  ❌ Skipped (no merchant info): {item_name}")
                    else:
                        failed_count += 1
                        logging.warning(f"  ❌ Failed to fetch: {item_name}")
                        
            finally:
                # Always close scraper
                eden_scraper.close()
                logging.info("Eden scraper closed")
            
            # Build final database structure
            database = {
                "version": "1.0",
                "description": "DAOC Items Source Database - Internal Read-Only",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "item_count": len(merged_items),
                "items": merged_items
            }
            
            # Save to file
            self.source_db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.source_db_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            # Build statistics
            stats = {
                "files_processed": len(file_paths),
                "items_parsed": len(new_items_names),
                "items_added": added_count,
                "items_failed": failed_count,
                "duplicates_skipped": duplicates_count,
                "parse_errors": len(parse_errors),
                "total_items": len(merged_items),
                "errors": parse_errors
            }
            
            message = f"Database built successfully!\n\n"
            message += f"Files processed: {stats['files_processed']}\n"
            message += f"Items parsed: {stats['items_parsed']}\n"
            message += f"Items added: {stats['items_added']}\n"
            message += f"Items failed: {stats['items_failed']}\n"
            message += f"Duplicates skipped: {stats['duplicates_skipped']}\n"
            message += f"Total items in DB: {stats['total_items']}"
            
            if parse_errors:
                message += f"\n\nWarning: {len(parse_errors)} parse errors"
            
            logging.info(f"Source database built: {stats}", extra={"action": "SUPERADMIN_BUILD"})
            return True, message, stats
            
        except Exception as e:
            logging.error(f"Error building database: {e}", extra={"action": "SUPERADMIN_BUILD_ERROR"})
            return False, f"Error building database: {str(e)}", {}
    
    def clean_duplicates(self) -> Tuple[bool, str, int]:
        """
        Remove duplicate items from source database (same name + realm)
        
        Returns:
            Tuple[bool, str, int]: (Success, Message, Count of removed duplicates)
        """
        try:
            if not self.source_db_path.exists():
                return False, "Source database does not exist", 0
            
            # Load database
            with open(self.source_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            items = data.get("items", {})
            original_count = len(items)
            
            # Backup before modification
            self.backup_source_database()
            
            # Track duplicates: key = (name_lower, realm_lower), value = list of keys
            seen = {}
            duplicates_to_remove = []
            
            for key, item_data in items.items():
                name = item_data.get("name", "").lower()
                realm = item_data.get("realm", "").lower()
                dup_key = (name, realm)
                
                if dup_key in seen:
                    # Duplicate found, mark for removal
                    duplicates_to_remove.append(key)
                else:
                    seen[dup_key] = key
            
            # Remove duplicates
            for key in duplicates_to_remove:
                del items[key]
            
            # Update database
            data["items"] = items
            data["item_count"] = len(items)
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save
            with open(self.source_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            removed_count = len(duplicates_to_remove)
            message = f"Removed {removed_count} duplicate items\n"
            message += f"Original: {original_count} items\n"
            message += f"After cleanup: {len(items)} items"
            
            logging.info(f"Cleaned {removed_count} duplicates from source database", 
                        extra={"action": "SUPERADMIN_CLEAN"})
            return True, message, removed_count
            
        except Exception as e:
            logging.error(f"Error cleaning duplicates: {e}", extra={"action": "SUPERADMIN_CLEAN_ERROR"})
            return False, f"Error: {str(e)}", 0
