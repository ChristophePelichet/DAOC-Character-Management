"""
Worker Thread for Mass Import
Allows scraping execution in a separate thread to keep UI responsive
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QThread, Signal

from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper
from Functions.items_scraper import ItemsScraper


class ImportWorker(QThread):
    """Worker thread for mass import - keeps UI responsive"""
    
    # Signals to communicate with UI
    progress_updated = Signal(dict)  # Stats: processed, variants, added, failed, duplicates, current_item
    log_message = Signal(str, str)  # message, level
    import_finished = Signal(bool, str, dict)  # success, message, stats
    
    def __init__(self, file_paths, realm, merge, remove_duplicates, auto_backup, 
                 source_db_path, path_manager, skip_filters_mode=False):
        super().__init__()
        self.file_paths = file_paths
        self.realm = realm
        self.merge = merge
        self.remove_duplicates = remove_duplicates
        self.auto_backup = auto_backup
        self.source_db_path = source_db_path
        self.path_manager = path_manager
        self.skip_filters_mode = skip_filters_mode  # NEW: Bypass level/utility filters
        self._eden_scraper = None  # Reference for external cleanup
    
    def cleanup_external_resources(self):
        """Forced scraper cleanup (called from main thread if needed)"""
        if self._eden_scraper:
            try:
                logging.info("Forced cleanup: Closing mass import scraper")
                self._eden_scraper.close()
                logging.info("Scraper fermé avec succès")
            except Exception as e:
                logging.warning(f"Erreur cleanup scraper: {e}")
            finally:
                self._eden_scraper = None
        
    def run(self):
        """Execute import in separate thread"""
        eden_scraper = None  # Protection for guaranteed cleanup
        
        try:
            from Functions.items_parser import parse_template_file
            
            # Parse files
            self.log_message.emit("Parsing template files...", "info")
            
            new_items_names = {}
            parse_errors = []
            
            for file_path in self.file_paths:
                try:
                    file_path_obj = Path(file_path)
                    
                    # Parse items (realm will be detected during scraping)
                    item_names = parse_template_file(file_path)
                    
                    # DEBUG: Log parsing result
                    self.log_message.emit(f"📄 {file_path_obj.name}: {len(item_names) if item_names else 0} item(s) trouvé(s)", "info")
                    
                    if item_names:
                        for item_name in item_names:
                            if not item_name or not item_name.strip():
                                continue
                            
                            item_name = item_name.strip()
                            item_data = {
                                "name": item_name,
                                "realm": self.realm if self.realm != "All" else "All",
                                "source_file": file_path_obj.name
                            }
                            
                            key = item_name.lower()
                            if key not in new_items_names:
                                new_items_names[key] = item_data
                
                except Exception as e:
                    parse_errors.append(f"Error parsing {Path(file_path).name}: {str(e)}")
            
            if not new_items_names:
                self.log_message.emit("❌ Aucun item parsé depuis les fichiers template", "error")
                
                # Show parsing errors if any
                if parse_errors:
                    self.log_message.emit(f"⚠️ {len(parse_errors)} erreur(s) de parsing:", "warning")
                    for error in parse_errors:
                        self.log_message.emit(f"  • {error}", "warning")
                else:
                    self.log_message.emit("ℹ️ Les fichiers ne contiennent peut-être pas d'items avec 'Source Type: Loot'", "info")
                    self.log_message.emit("ℹ️ Format attendu: Name: <nom> + Source Type: Loot", "info")
                
                self.import_finished.emit(False, "No items parsed from template files", {})
                return
            
            self.log_message.emit(f"Fichiers parsés: {len(self.file_paths)}", "info")
            if parse_errors:
                for error in parse_errors:
                    self.log_message.emit(error, "warning")
            
            # Initialize scraper
            self.log_message.emit("Initializing Eden scraper...", "info")
            
            cookie_manager = CookieManager()
            eden_scraper = EdenScraper(cookie_manager)
            self._eden_scraper = eden_scraper  # Store for external cleanup
            
            if not eden_scraper.initialize_driver(headless=False, minimize=True):
                self.log_message.emit("Failed to initialize Eden driver", "error")
                self.import_finished.emit(False, "Failed to initialize Eden scraper", {})
                # eden_scraper will be closed in finally
                return
            
            if not eden_scraper.load_cookies():
                self.log_message.emit("Failed to load cookies", "error")
                self.import_finished.emit(False, "Failed to load cookies", {})
                # eden_scraper will be closed in finally
                return
            
            items_scraper = ItemsScraper(eden_scraper)
            self.log_message.emit("Eden scraper initialized successfully", "success")
            
            # Load existing database
            existing_items = {}
            if self.merge and self.source_db_path.exists():
                with open(self.source_db_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_items = existing_data.get("items", {})
            
            # Backup
            if self.auto_backup and self.source_db_path.exists():
                self.log_message.emit("Creating backup...", "info")
                if self.path_manager:  # Check if path_manager exists
                    from Functions.superadmin_tools import SuperAdminTools
                    superadmin = SuperAdminTools(self.path_manager)
                    success, backup_path = superadmin.backup_source_database()
                    if success:
                        self.log_message.emit(f"Backup created: {backup_path}", "success")
                    else:
                        self.log_message.emit(f"Warning: backup failed - {backup_path}", "warning")
                else:
                    self.log_message.emit("Backup skipped (no path_manager)", "info")
            
            # Process items
            merged_items = existing_items.copy() if self.merge else {}
            duplicates_count = 0
            added_count = 0
            failed_count = 0
            variants_found = 0
            all_filtered_items = []  # Store all filtered items for review
            
            try:
                # Extract unique items
                unique_items = {}
                for key, item_basic in new_items_names.items():
                    item_name = item_basic["name"]
                    if item_name not in unique_items:
                        unique_items[item_name] = item_basic
                
                total_items = len(unique_items)
                
                # Update monitor with correct total
                self.progress_updated.emit({
                    'processed': 0,
                    'total': total_items,
                    'added': 0,
                    'variants': 0,
                    'failed': 0,
                    'duplicates': 0
                })
                
                self.log_message.emit("", "separator")
                self.log_message.emit(f"🔍 {total_items} item(s) unique(s) à traiter", "info")
                self.log_message.emit("", "separator")
                
                for idx, (item_name, item_basic) in enumerate(unique_items.items(), 1):
                    # Update progress
                    self.progress_updated.emit({
                        'processed': idx,
                        'current_item': item_name,
                        'added': added_count,
                        'variants': variants_found,
                        'failed': failed_count,
                        'duplicates': duplicates_count
                    })
                    
                    self.log_message.emit("", "separator")
                    self.log_message.emit(f"[{idx}/{total_items}] Processing: {item_name}", "search")
                    
                    try:
                        # Check if item already exists in DB with bypass_filters flag
                        item_key_base = item_name.lower()
                        should_bypass = self.skip_filters_mode  # Default from worker mode
                        should_ignore = False
                        
                        # Check existing items for bypass_filters tag or ignore_item flag
                        for key, existing_item in merged_items.items():
                            if key.startswith(item_key_base + ":"):
                                # Check if item is marked as ignored
                                if existing_item.get("ignore_item", False):
                                    should_ignore = True
                                    self.log_message.emit(f"   🚫 Item is ignored - skipping", "info")
                                    break
                                # Check if item has bypass_filters tag
                                if existing_item.get("bypass_filters", False):
                                    should_bypass = True
                                    self.log_message.emit(f"   🔓 Item has bypass_filters tag - ignoring level/utility restrictions", "info")
                                    break
                        
                        # Skip if item is marked as ignored
                        if should_ignore:
                            continue
                        
                        # Find variants (with filtered items tracking)
                        # Use skip_filters if in retry mode OR if item has bypass tag in DB
                        variants, filtered = items_scraper.find_all_item_variants(
                            item_name, 
                            return_filtered=True,
                            skip_filters=should_bypass
                        )
                        
                        # Store filtered items for potential retry
                        if filtered:
                            for fitem in filtered:
                                fitem['original_search'] = item_name  # Track original search name
                                all_filtered_items.append(fitem)
                            # Log filtering details
                            self.log_message.emit(f"   {len(filtered)} item(s) filtré(s)", "warning")
                            for fitem in filtered:
                                self.log_message.emit(f"      • {fitem.get('name', 'Unknown')} - Raison: {fitem['reason']}", "warning")
                        
                        if not variants:
                            # Check if item already exists in DB
                            item_key_base = item_name.lower()
                            exists_in_db = any(k.startswith(item_key_base + ":") for k in merged_items.keys())
                            
                            if exists_in_db:
                                self.log_message.emit(f"Item déjà dans la DB: {item_name}", "duplicate")
                                duplicates_count += 1
                            else:
                                failed_count += 1
                                self.log_message.emit(f"Aucune variante trouvée: {item_name}", "error")
                                if filtered:
                                    reasons = ", ".join(set(f['reason'] for f in filtered))
                                    self.log_message.emit(f"   Raison(s): {reasons}", "warning")
                            continue
                        
                        variants_found += len(variants)
                        
                        variant_info = ", ".join([f"{v.get('realm', 'Unknown')} (ID: {v.get('id', '?')})" for v in variants])
                        self.log_message.emit(f"{len(variants)} variant(s) found: {variant_info}", "variant")
                        
                        # Process each variant
                        for variant in variants:
                            item_id = variant['id']
                            variant_realm = variant.get('realm') or 'All'
                            
                            if not variant_realm or not variant_realm.strip():
                                variant_realm = 'All'
                            
                            self.log_message.emit(f"  → Scraping variant {variant_realm} (ID: {item_id})...", "search")
                            
                            # Composite key
                            realm_lower = variant_realm.lower() if variant_realm != "All" else "all"
                            composite_key = f"{item_name.lower()}:{realm_lower}"
                            
                            # Check duplicates
                            if self.remove_duplicates and composite_key in merged_items:
                                duplicates_count += 1
                                self.log_message.emit(f"    Duplicate skipped: {composite_key}", "duplicate")
                                self.progress_updated.emit({'duplicates': duplicates_count})
                                continue
                            
                            # Get details
                            item_details = items_scraper.get_item_details(item_id, variant_realm, item_name)
                            
                            if not item_details:
                                self.log_message.emit(f"    ⚠️ Failed to get details for {variant_realm}", "warning")
                                continue
                            
                            # Format data
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
                                "source": "internal",
                                "bypass_filters": self.skip_filters_mode  # Tag if added via retry (bypass filters)
                            }
                            
                            # Add merchant info
                            merchants = item_details.get('merchants', [])
                            if merchants:
                                merchant = merchants[0]
                                price_parsed = merchant.get("price_parsed")
                                
                                # Check if currency is supported (not BP, Bounty Points, etc.)
                                currency = price_parsed.get("currency") if price_parsed else None
                                unsupported_currencies = ['BP', 'Bounty Points', 'Bounty', 'BPs', 'Merit Points']
                                
                                if currency and any(unsup.lower() in currency.lower() for unsup in unsupported_currencies):
                                    # Track as filtered item with specific reason
                                    filtered_item = {
                                        'name': item_name,
                                        'id': item_id,
                                        'realm': variant_realm,
                                        'reason': 'currency_not_supported',
                                        'currency': currency,
                                        'original_search': item_name
                                    }
                                    all_filtered_items.append(filtered_item)
                                    
                                    failed_count += 1
                                    self.log_message.emit(f"    ❌ Skipped (currency not supported): {currency}", "error")
                                    self.progress_updated.emit({'failed': failed_count})
                                    continue
                                
                                item_data["merchant_zone"] = merchant.get("zone") or "Unknown"
                                item_data["merchant_price"] = str(price_parsed.get("amount")) if price_parsed else "Unknown"
                                item_data["merchant_currency"] = currency
                                
                                merged_items[composite_key] = item_data
                                added_count += 1
                                
                                merchant_info = f"{item_data.get('merchant_zone', '?')} - {item_data.get('merchant_price', '?')} {item_data.get('merchant_currency', '')}"
                                slot_info = item_data.get('slot', 'Unknown')
                                type_info = item_data.get('type', 'Unknown')
                                
                                self.log_message.emit(f"    ✅ Added: {composite_key}", "success")
                                self.log_message.emit(f"       📍 Slot: {slot_info}, Type: {type_info}, Merchant: {merchant_info}", "info")
                                self.progress_updated.emit({'added': added_count})
                            else:
                                # Track as filtered item - no merchant found
                                filtered_item = {
                                    'name': item_name,
                                    'id': item_id,
                                    'realm': variant_realm,
                                    'reason': 'no_merchant',
                                    'level': None,
                                    'utility': None,
                                    'original_search': item_name
                                }
                                all_filtered_items.append(filtered_item)
                                
                                failed_count += 1
                                self.log_message.emit(f"    ❌ Skipped (no merchant info)", "error")
                                self.progress_updated.emit({'failed': failed_count})
                    
                    except Exception as e:
                        failed_count += 1
                        self.log_message.emit(f"Error processing {item_name}: {e}", "error")
                        self.progress_updated.emit({'failed': failed_count})
                        continue
            
            finally:
                # Guaranteed cleanup even in case of error in loop
                if eden_scraper:
                    try:
                        eden_scraper.close()
                        self.log_message.emit("", "separator")
                        self.log_message.emit("Eden scraper closed", "info")
                        logging.info("Eden scraper closed cleanly in worker thread")
                    except Exception as e:
                        logging.warning(f"Error closing Eden scraper in worker: {e}")
            
            # Save database
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
            
            self.source_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.log_message.emit("", "separator")
            self.log_message.emit(f"Saving database ({len(merged_items)} items)...", "info")
            
            with open(self.source_db_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            self.log_message.emit(f"Database saved: {self.source_db_path}", "success")
            
            # Build stats
            stats = {
                "files_processed": len(self.file_paths),
                "unique_items_processed": len(unique_items),
                "variants_found": variants_found,
                "items_added": added_count,
                "items_failed": failed_count,
                "duplicates_skipped": duplicates_count,
                "parse_errors": len(parse_errors),
                "total_items": len(merged_items),
                "errors": parse_errors,
                "filtered_items": all_filtered_items  # For retry functionality
            }
            
            # Log filtered items summary
            if all_filtered_items:
                self.log_message.emit("", "separator")
                self.log_message.emit(f"🔍 {len(all_filtered_items)} item(s) filtré(s) disponibles pour réessai", "warning")
            
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
            
            self.import_finished.emit(True, message, stats)
            
        except Exception as e:
            logging.error(f"Error in ImportWorker: {e}", exc_info=True)
            self.log_message.emit(f"CRITICAL ERROR: {e}", "error")
            self.import_finished.emit(False, f"Error building database: {str(e)}", {})
        
        finally:
            # Final guaranteed cleanup - close scraper even in case of critical exception
            if eden_scraper:
                try:
                    eden_scraper.close()
                    logging.info("Final cleanup: Eden scraper closed in ImportWorker")
                except Exception as e:
                    logging.warning(f"Final cleanup error in ImportWorker: {e}")
