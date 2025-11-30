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
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

from Functions.path_manager import PathManager
from Functions.items_parser import parse_template_file, search_item_for_database
from Functions.eden_scraper import EdenScraper, _connect_to_eden_herald
from Functions.cookie_manager import CookieManager
from Functions.items_scraper import ItemsScraper


class SuperAdminTools:
    """Administrative tools for source database management"""
    
    def __init__(self, path_manager: PathManager, config_manager=None):
        """
        Initialize SuperAdmin tools
        
        Args:
            path_manager: PathManager instance for resolving paths
            config_manager: ConfigManager instance for backup configuration (optional)
        """
        self.path_manager = path_manager
        self.config_manager = config_manager
        self.source_db_path = self.path_manager.get_app_root() / "Data" / "items_database_src.json"
        
        # Initialize backup directory from config or use default
        if config_manager:
            backup_path = config_manager.get("backup_path")
            if backup_path:
                self.backup_dir = Path(backup_path).parent / "Database"
            else:
                # Default: Backup/Database relative to base path
                self.backup_dir = self.path_manager.get_app_root() / "Backup" / "Database"
        else:
            # Fallback if no config_manager provided
            self.backup_dir = self.path_manager.get_app_root() / "Backup" / "Database"
        
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
        Create a backup of the source database using centralized backup system.
        Backups are stored in <backup_path>/Database/ folder as compressed ZIP.
        
        Returns:
            Tuple[bool, str]: (Success, Backup path or error message)
        """
        try:
            if not self.source_db_path.exists():
                return False, "Source database does not exist"
            
            # Use centralized backup directory
            backup_folder = self.backup_dir
            backup_folder.mkdir(parents=True, exist_ok=True)
            
            # Backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_zip_path = backup_folder / f"items_database_src_backup_{timestamp}.zip"
            
            # Create ZIP archive
            import zipfile
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.source_db_path, arcname=self.source_db_path.name)
            
            logging.info(f"Source database backed up to {backup_zip_path}", extra={"action": "SUPERADMIN_BACKUP"})
            return True, str(backup_zip_path)
            
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
                
                # Auto-detect realm from filename (MANDATORY for templates)
                detected_realm = None
                filename_lower = file_path_obj.stem.lower()
                if "albion" in filename_lower:
                    detected_realm = "Albion"
                elif "hibernia" in filename_lower or "hib" in filename_lower:
                    detected_realm = "Hibernia"
                elif "midgard" in filename_lower or "mid" in filename_lower:
                    detected_realm = "Midgard"
                
                # If no realm detected in filename, use parameter
                # BUT NEVER "All" for templates (these are specific characters)
                if not detected_realm:
                    if realm and realm != "All":
                        detected_realm = realm
                    else:
                        # Cannot determine realm - ERROR
                        errors.append(f"Cannot determine realm for {file_path_obj.name}. Filename must contain 'Albion', 'Hibernia', or 'Midgard'")
                        logging.error(f"Realm detection failed for {file_path_obj.name}", extra={"action": "SUPERADMIN_PARSE_ERROR"})
                        continue
                
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
                        # Skip empty or None item names
                        if not item_name or not item_name.strip():
                            continue
                        
                        item_name = item_name.strip()
                        
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
                                   auto_backup: bool = True, monitor=None) -> Tuple[bool, str, Dict]:
        """
        Build source database from multiple template files
        
        NOUVELLE VERSION: Utilise un QThread pour garder l'UI responsive
        
        Args:
            file_paths: List of .txt template file paths
            realm: Default realm for items
            merge: If True, merge with existing DB; if False, replace completely
            remove_duplicates: Remove items with same name + realm
            auto_backup: Automatically backup old DB before saving
            monitor: Optional MassImportMonitor instance for UI feedback
        
        Returns:
            Tuple[bool, str, Dict]: (Success, Message, Statistics dict)
        """
        worker = None  # Protection for cleanup
        
        try:
            # If no monitor, use old method (for compatibility)
            if monitor is None:
                return self._build_database_sync(file_paths, realm, merge, remove_duplicates, auto_backup)
            
            # Utiliser le Worker Thread pour garder l'UI responsive
            from Functions.import_worker import ImportWorker
            from PySide6.QtCore import QEventLoop
            
            # Create worker
            worker = ImportWorker(
                file_paths=file_paths,
                realm=realm,
                merge=merge,
                remove_duplicates=remove_duplicates,
                auto_backup=auto_backup,
                source_db_path=self.source_db_path,
                path_manager=self.path_manager
            )
            
            # Connect signals
            worker.progress_updated.connect(lambda stats: monitor.update_stats(**stats))
            worker.log_message.connect(lambda msg, level: monitor.log_message(msg, level))
            
            # Start import with template files list
            total_items = len(file_paths)  # Approximation, will be updated
            template_file_names = [Path(fp).name for fp in file_paths]
            monitor.start_import(total_items, template_files=template_file_names)
            
            # Variable to store result
            result_data = {'success': False, 'message': '', 'stats': {}}
            
            def on_finished(success, message, stats):
                result_data['success'] = success
                result_data['message'] = message
                result_data['stats'] = stats
                
                logging.info(f"Import finished. Stats keys: {stats.keys() if stats else 'None'}")
                if stats and 'filtered_items' in stats:
                    logging.info(f"Filtered items count: {len(stats['filtered_items'])}")
                
                monitor.finish_import(success)
                
                # Pass filtered items to monitor for review option
                if stats and 'filtered_items' in stats:
                    monitor.set_filtered_items(stats['filtered_items'])
                else:
                    logging.warning("No filtered_items in stats or stats is None")
                
                loop.quit()
            
            worker.import_finished.connect(on_finished)
            
            # Start worker thread
            worker.start()
            
            # Wait for completion (but UI stays responsive)
            loop = QEventLoop()
            loop.exec()
            
            return result_data['success'], result_data['message'], result_data['stats']
            
        except Exception as e:
            logging.error(f"Error building database: {e}", extra={"action": "SUPERADMIN_BUILD_ERROR"})
            
            if monitor:
                from PySide6.QtWidgets import QApplication
                monitor.log_message(f"ERREUR CRITIQUE: {e}", "error")
                monitor.finish_import(success=False)
                QApplication.processEvents()
            
            return False, f"Error building database: {str(e)}", {}
        
        finally:
            # Cleanup garanti du worker thread
            if worker:
                try:
                    if worker.isRunning():
                        logging.warning("Worker thread still running - forcing cleanup")
                        worker.cleanup_external_resources()
                        worker.wait(3000)  # Attendre max 3 secondes
                        if worker.isRunning():
                            worker.terminate()
                            worker.wait()
                    logging.info("Worker thread cleaned up")
                except Exception as e:
                    logging.warning(f"Error cleaning up worker thread: {e}")
    
    def _build_database_sync(self, file_paths: List[str], realm: str = "All",
                             merge: bool = True, remove_duplicates: bool = True,
                             auto_backup: bool = True) -> Tuple[bool, str, Dict]:
        """
        Synchronous version (legacy) - used when no monitor
        Kept for compatibility
        """
        eden_scraper = None  # Protection for guaranteed cleanup
        
        try:
            # Parse all template files to get item names
            new_items_names, parse_errors = self.parse_template_files(file_paths, realm)
            
            if not new_items_names:
                return False, "No items parsed from template files", {}
            
            # Initialize Eden scraper using centralized connection
            logging.info("Initializing Eden scraper for item details...")
            eden_scraper, error_message = _connect_to_eden_herald(headless=False)
            if not eden_scraper:
                return False, f"Failed to connect to Eden Herald: {error_message}", {}
            
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
            variants_found = 0
            
            try:
                # Extract unique item names (without duplication)
                unique_items = {}
                for key, item_basic in new_items_names.items():
                    item_name = item_basic["name"]
                    if item_name not in unique_items:
                        unique_items[item_name] = item_basic
                
                total_items = len(unique_items)
                logging.info(f"Processing {total_items} unique items from templates")
                
                for idx, (item_name, item_basic) in enumerate(unique_items.items(), 1):
                    logging.info(f"[{idx}/{total_items}] Processing: {item_name}")
                    
                    try:
                        # Find ALL item variants (all realms)
                        variants = items_scraper.find_all_item_variants(item_name)
                        
                        if not variants:
                            logging.warning(f"  ❌ No variants found for: {item_name}")
                            failed_count += 1
                            continue
                        
                        logging.info(f"  ✅ Found {len(variants)} variant(s)")
                        variants_found += len(variants)
                        
                        # Scrape details of each variant
                        for variant in variants:
                            item_id = variant['id']
                            variant_realm = variant.get('realm') or 'All'
                            
                            # Validate realm
                            if not variant_realm or not variant_realm.strip():
                                variant_realm = 'All'
                            
                            logging.info(f"    🔍 Scraping variant: {variant_realm} (ID: {item_id})")
                            
                            # Generate composite key
                            realm_lower = variant_realm.lower() if variant_realm != "All" else "all"
                            composite_key = f"{item_name.lower()}:{realm_lower}"
                            
                            # Check for duplicates before scraping
                            if remove_duplicates and composite_key in merged_items:
                                duplicates_count += 1
                                logging.info(f"      ⏭️  Skipped (duplicate): {composite_key}")
                                continue
                            
                            # Get full details
                            item_details = items_scraper.get_item_details(item_id, variant_realm, item_name)
                            
                            if not item_details:
                                logging.warning(f"      ⚠️  Failed to get details")
                                continue
                            
                            # Format for database v2.0
                            item_data = {
                                "id": item_id,
                                "name": item_details.get("name") or item_name,
                                "realm": item_details.get("realm") or variant_realm,
                                "slot": item_details.get("slot") or "Unknown",
                                "type": item_details.get("type"),
                                "model": item_details.get("model"),
                                "dps": item_details.get("dps"),
                                "speed": item_details.get("speed"),
                                "damage_type": item_details.get("damage_type"),
                                "usable_by": item_details.get("usable_by", "ALL"),
                                "source": "internal"
                            }
                            
                            # Add merchant info
                            merchants = item_details.get('merchants', [])
                            if merchants:
                                merchant = merchants[0]
                                price_parsed = merchant.get("price_parsed")
                                
                                item_data["merchant_zone"] = merchant.get("zone") or "Unknown"
                                item_data["merchant_price"] = str(price_parsed.get("amount")) if price_parsed else "Unknown"
                                item_data["merchant_currency"] = price_parsed.get("currency") if price_parsed else None
                                
                                # Save to merged items
                                merged_items[composite_key] = item_data
                                added_count += 1
                                logging.info(f"      ✅ Added: {composite_key}")
                            else:
                                logging.warning(f"      ❌ Skipped (no merchant info)")
                                failed_count += 1
                        
                    except Exception as e:
                        logging.error(f"  ❌ Error processing {item_name}: {e}")
                        import traceback
                        logging.debug(traceback.format_exc())
                        failed_count += 1
                        continue
            
            finally:
                # Guaranteed cleanup even in case of error
                if eden_scraper:
                    try:
                        eden_scraper.close()
                        logging.info("Eden scraper closed")
                    except Exception as e:
                        logging.warning(f"Error closing Eden scraper: {e}")
            
            # Build final database structure (v2.0)
            database = {
                "version": "2.0",
                "description": "DAOC Items Database - Multi-Realm Support (Minimal Data)",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "item_count": len(merged_items),
                "notes": [
                    "Composite keys format: 'item_name:realm' (lowercase)",
                    "Only essential data: ID, name, realm, slot, type, model, damage info, merchant",
                    "No stats, resistances, bonuses, level, or quality"
                ],
                "items": merged_items
            }
            
            # Save to file
            self.source_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.source_db_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            # Build statistics
            stats = {
                "files_processed": len(file_paths),
                "unique_items_processed": len(unique_items),
                "variants_found": variants_found,
                "items_added": added_count,
                "items_failed": failed_count,
                "duplicates_skipped": duplicates_count,
                "parse_errors": len(parse_errors),
                "total_items": len(merged_items),
                "errors": parse_errors
            }
            
            message = f"Database built successfully!\n\n"
            message += f"Files processed: {stats['files_processed']}\n"
            message += f"Unique items: {stats['unique_items_processed']}\n"
            message += f"Variants found: {stats['variants_found']}\n"
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
            return False, f"Error building database: {str(e)}", None
        
        finally:
            # Final guaranteed cleanup even in case of critical exception
            if eden_scraper:
                try:
                    eden_scraper.close()
                    logging.info("Final cleanup: Eden scraper closed in sync build")
                except Exception as e:
                    logging.warning(f"Final cleanup error in sync build: {e}")
    
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
    
    def refresh_all_items(self, progress_callback=None, item_filter: List[str] = None, skip_filters: bool = False) -> Tuple[bool, str, Dict]:
        """
        Refresh all items in the database by re-scraping them from Eden.
        
        NOUVELLE LOGIQUE v2.0:
        - Pour chaque item unique (nom), trouve TOUTES les variantes (tous realms)
        - Crée/met à jour une entrée par realm dans la DB
        - Exemple: "Cudgel of the Undead" → 3 entrées (Albion, Hibernia, Midgard)
        
        Args:
            progress_callback: Optional callback(current, total, item_name) for progress updates
            item_filter: Liste optionnelle de noms d'items à rafraîchir (pour debug)
                        Si None, rafraîchit TOUS les items
                        Exemple: ["Cloth Cap", "Cudgel of the Undead"]
            skip_filters: If True, bypass utility/level filters to get ALL variants
            
        Returns:
            Tuple[bool, str, Dict]: (Success, Message, Stats dict)
        """
        eden_scraper = None
        
        try:
            if not self.source_db_path.exists():
                return False, "Source database does not exist", {}
            
            # Load database
            with open(self.source_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            items = data.get("items", {})
            
            # Extraire les noms d'items uniques (ignorer les doublons de realm)
            unique_items = {}
            for key, item_data in items.items():
                item_name = item_data.get("name", "")
                if item_name and item_name not in unique_items:
                    unique_items[item_name] = item_data
            
            total_items = len(unique_items)
            
            if total_items == 0:
                return False, "Database is empty", {}
            
            # Backup before modification
            logging.info("Creating backup before refresh...")
            self.backup_source_database()
            
            # Initialize scraper with driver using centralized connection
            logging.info("Initializing web scraper...")
            start_init = time.time()
            
            eden_scraper, error_message = _connect_to_eden_herald(headless=False)
            if not eden_scraper:
                return False, f"Failed to connect to Eden Herald: {error_message}", {}
            
            logging.info(f"⏱️  Total initialization: {time.time() - start_init:.2f}s")
            
            items_scraper = ItemsScraper(eden_scraper)
            
            # Statistics
            items_created = 0
            items_updated = 0
            variants_found = 0
            failed_count = 0
            fields_updated = {
                'model': 0,
                'dps': 0,
                'speed': 0,
                'damage_type': 0,
                'type': 0,
                'slot': 0,
                'usable_by': 0
            }
            
            # IMPORTANT: Start from EXISTING database (don't overwrite)
            # We will update/add items, not recreate everything
            new_items = dict(items)  # Copy of current database
            
            # Process each unique item
            for idx, item_name in enumerate(unique_items.keys(), 1):
                # Appliquer le filtre si fourni
                if item_filter is not None and item_name not in item_filter:
                    logging.debug(f"⏭️  SKIP (not in filter): {item_name}")
                    continue
                
                if progress_callback:
                    progress_callback(idx, total_items, item_name)
                
                logging.info(f"Refreshing {idx}/{total_items}: {item_name}")
                item_start = time.time()
                
                try:
                    # Find ALL item variants (all realms) with optional filter bypass
                    logging.debug(f"Searching ALL variants for '{item_name}' (skip_filters={skip_filters})")
                    variants = items_scraper.find_all_item_variants(item_name, skip_filters=skip_filters)
                    
                    if not variants:
                        logging.warning(f"❌ No variants found for: {item_name}")
                        failed_count += 1
                        time.sleep(0.5)
                        continue
                    
                    logging.info(f"✅ Found {len(variants)} variant(s) for '{item_name}'")
                    variants_found += len(variants)
                    
                    # Scrape details of each variant
                    for variant in variants:
                        variant_start = time.time()
                        item_id = variant['id']
                        realm = variant.get('realm') or 'All'
                        
                        # Validate realm
                        if not realm or not realm.strip():
                            realm = 'All'
                        
                        logging.info(f"  Scraping variant: {realm} (ID: {item_id})")
                        
                        # Get full details
                        item_details = items_scraper.get_item_details(item_id, realm, item_name)
                        
                        if not item_details:
                            logging.warning(f"  ⚠️ Failed to get details for {realm} variant")
                            continue
                        
                        # Create DB key (realm is now guaranteed to be valid)
                        db_key = f"{item_name.lower()}:{realm.lower()}"
                        
                        # Check if item already exists
                        is_new = db_key not in items
                        
                        # Prepare full data
                        item_data = {
                            "id": item_id,
                            "name": item_name,
                            "realm": realm,
                            "slot": item_details.get("slot", "Unknown"),
                            "type": item_details.get("type"),
                            "model": item_details.get("model"),
                            "dps": item_details.get("dps"),
                            "speed": item_details.get("speed"),
                            "damage_type": item_details.get("damage_type"),
                            "usable_by": item_details.get("usable_by", "ALL"),
                            "merchant_zone": item_details.get("merchant_zone"),
                            "merchant_price": item_details.get("merchant_price"),
                            "merchant_currency": item_details.get("merchant_currency"),
                            "source": "internal"
                        }
                        
                        # Stocker dans la nouvelle structure
                        new_items[db_key] = item_data
                        
                        if is_new:
                            items_created += 1
                            logging.info(f"  ✨ NEW: {db_key}")
                        else:
                            items_updated += 1
                            # Count updated fields
                            old_item = items.get(db_key, {})
                            for field in ['model', 'dps', 'speed', 'damage_type', 'type', 'slot', 'usable_by']:
                                if item_data.get(field) != old_item.get(field) and item_data.get(field):
                                    fields_updated[field] += 1
                            logging.info(f"  ♻️  UPDATED: {db_key}")
                        
                        logging.info(f"  ⏱️  Variant scraped in {time.time() - variant_start:.2f}s")
                        time.sleep(1)  # Delay between variants
                    
                    logging.info(f"⏱️  Item '{item_name}' completed in {time.time() - item_start:.2f}s")
                    time.sleep(2)  # Delay between items
                    
                except Exception as e:
                    logging.error(f"Error refreshing {item_name}: {e}")
                    import traceback
                    logging.debug(traceback.format_exc())
                    failed_count += 1
                    time.sleep(0.5)
                    continue
            
            # Update metadata
            data["items"] = new_items
            data["item_count"] = len(new_items)
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "notes" not in data:
                data["notes"] = []
            # Note: last_updated suffit, pas besoin de dupliquer dans notes
            
            # Save updated database
            save_start = time.time()
            with open(self.source_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"⏱️  Database saved in {time.time() - save_start:.2f}s")
            
            # Build statistics
            stats = {
                "unique_items_processed": total_items,
                "variants_found": variants_found,
                "items_created": items_created,
                "items_updated": items_updated,
                "failed": failed_count,
                "total_db_entries": len(new_items),
                "fields_updated": fields_updated
            }
            
            message = f"Database refresh completed!\n\n"
            message += f"Unique items processed: {total_items}\n"
            message += f"Total variants found: {variants_found}\n"
            message += f"New DB entries: {items_created}\n"
            message += f"Updated DB entries: {items_updated}\n"
            message += f"Failed: {failed_count}\n"
            message += f"Total DB entries: {len(new_items)}\n\n"
            message += f"Fields updated:\n"
            message += f"• Model: {fields_updated['model']}\n"
            message += f"• DPS: {fields_updated['dps']}\n"
            message += f"• Speed: {fields_updated['speed']}\n"
            message += f"• Damage Type: {fields_updated['damage_type']}\n"
            message += f"• Type: {fields_updated['type']}\n"
            message += f"• Slot: {fields_updated['slot']}\n"
            message += f"• Usable By: {fields_updated['usable_by']}"
            
            logging.info(f"Database refresh completed: {stats}", extra={"action": "SUPERADMIN_REFRESH"})
            return True, message, stats
            
        except Exception as e:
            logging.error(f"Error refreshing database: {e}", extra={"action": "SUPERADMIN_REFRESH_ERROR"})
            import traceback
            logging.debug(traceback.format_exc())
            return False, f"Error refreshing database: {str(e)}", {}
        
        finally:
            # Close browser
            if eden_scraper:
                eden_scraper.close()
