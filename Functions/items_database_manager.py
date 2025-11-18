"""
Items Database Manager
Version: v0.108
Author: Christophe Pelichet
Description: Manages dual-mode items database (internal read-only vs personal user database)

This module handles:
- Database path resolution (internal Data/ or personal Armory/)
- Item search in active database
- Personal database creation (copy from internal)
- Adding scraped items with deduplication
- Statistics (internal/personal/user-added counts)
- Database reset (restore from internal copy)
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from Functions.config_manager import ConfigManager
from Functions.path_manager import PathManager
import logging


class ItemsDatabaseManager:
    """Manages access to items databases with dual-mode support"""

    def __init__(self, config_manager: ConfigManager, path_manager: PathManager):
        """
        Initialize the database manager
        
        Args:
            config_manager: ConfigManager instance for reading/writing config
            path_manager: PathManager instance for resolving paths
        """
        self.config_manager = config_manager
        self.path_manager = path_manager
        
        # Internal database path (embedded in Data/ folder, compiled in .exe)
        self.internal_db_path = self.path_manager.get_app_root() / "Data" / "items_database_src.json"
        
        logging.info("ItemsDatabaseManager initialized", extra={"action": "ITEMDB_INIT"})

    def get_active_database_path(self) -> Path:
        """
        Get path to the active database based on config
        
        Returns:
            Path: Path to internal or personal database
        """
        use_personal = self.config_manager.config.get("armory", {}).get("use_personal_database", False)
        
        if use_personal:
            # Personal database in Armory folder
            armor_path = self.config_manager.config.get("folders", {}).get("armor")
            if armor_path:
                personal_db_path = Path(armor_path) / "items_database.json"
                if personal_db_path.exists():
                    logging.info(f"Using personal database: {personal_db_path}", extra={"action": "ITEMDB_PATH"})
                    return personal_db_path
                else:
                    logging.info(f"Personal database not found at {personal_db_path}, falling back to internal", 
                        extra={"action": "ITEMDB_PATH"})
        
        # Default: internal database (read-only)
        logging.info(f"Using internal database: {self.internal_db_path}", extra={"action": "ITEMDB_PATH"})
        return self.internal_db_path

    def _load_database(self, db_path: Path) -> Dict:
        """
        Load database from JSON file
        
        Args:
            db_path: Path to database file
            
        Returns:
            Dict: Database content (version, items, etc.)
        """
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logging.info(f"Loaded database from {db_path} ({len(data.get('items', {}))} items)", 
                extra={"action": "ITEMDB_LOAD"})
            return data
        except Exception as e:
            logging.error(f"Error loading database from {db_path}: {e}", extra={"action": "ITEMDB_LOAD_ERROR"})
            return {"version": "1.0", "items": {}, "description": "", "last_updated": ""}

    def _save_database(self, db_path: Path, data: Dict) -> bool:
        """
        Save database to JSON file
        
        Args:
            db_path: Path to database file
            data: Database content to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update last_updated timestamp
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Saved database to {db_path} ({len(data.get('items', {}))} items)", 
                extra={"action": "ITEMDB_SAVE"})
            return True
        except Exception as e:
            logging.error(f"Error saving database to {db_path}: {e}", extra={"action": "ITEMDB_SAVE_ERROR"})
            return False

    def search_item(self, item_name: str) -> Optional[Dict]:
        """
        Search for an item in the active database
        
        Args:
            item_name: Name of the item to search (case-insensitive)
            
        Returns:
            Optional[Dict]: Item data if found, None otherwise
        """
        db_path = self.get_active_database_path()
        database = self._load_database(db_path)
        
        # Search by lowercase key
        search_key = item_name.lower()
        item_data = database.get("items", {}).get(search_key)
        
        if item_data:
            logging.info(f"Found item '{item_name}' in database", extra={"action": "ITEMDB_SEARCH"})
        else:
            logging.info(f"Item '{item_name}' not found in database", extra={"action": "ITEMDB_SEARCH"})
        
        return item_data

    def create_personal_database(self) -> Tuple[bool, str]:
        """
        Create personal database by copying internal database to Armory folder
        
        Returns:
            Tuple[bool, str]: (Success, Path or error message)
        """
        try:
            # Get armor path from config, use default if not set
            armor_path = self.config_manager.config.get("folders", {}).get("armor")
            if not armor_path:
                # Use default Armory folder at application root
                armor_path = self.path_manager.get_app_root() / "Armory"
                # Save to config
                self.config_manager.config.setdefault("folders", {})
                self.config_manager.config["folders"]["armor"] = str(armor_path)
                self.config_manager.save_config()
            
            armor_path = Path(armor_path)
            armor_path.mkdir(parents=True, exist_ok=True)
            
            personal_db_path = armor_path / "items_database.json"
            
            # Check if internal database exists
            if not self.internal_db_path.exists():
                return False, f"Internal database not found at {self.internal_db_path}"
            
            # Copy internal database to personal location
            shutil.copy2(self.internal_db_path, personal_db_path)
            
            # Update config
            self.config_manager.config.setdefault("armory", {})
            self.config_manager.config["armory"]["personal_db_created"] = True
            self.config_manager.config["armory"]["personal_db_path"] = str(personal_db_path)
            self.config_manager.config["armory"]["use_personal_database"] = True
            
            # Get internal database version
            internal_db = self._load_database(self.internal_db_path)
            self.config_manager.config["armory"]["last_internal_db_version"] = internal_db.get("version", "1.0")
            
            self.config_manager.save_config()
            
            logging.info(f"Created personal database at {personal_db_path}", extra={"action": "ITEMDB_CREATE"})
            return True, str(personal_db_path)
            
        except Exception as e:
            logging.error(f"Error creating personal database: {e}", extra={"action": "ITEMDB_CREATE_ERROR"})
            return False, str(e)

    def add_scraped_item(self, item_data: Dict, realm: str) -> Tuple[bool, str]:
        """
        Add a scraped item to personal database with deduplication
        
        Args:
            item_data: Item data dictionary (name, id, type, slot, zone, etc.)
            realm: Realm name (Albion, Hibernia, Midgard)
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        try:
            # Only allow adding to personal database
            use_personal = self.config_manager.config.get("armory", {}).get("use_personal_database", False)
            if not use_personal:
                return False, "Personal database not enabled"
            
            db_path = self.get_active_database_path()
            
            # Check if path is actually personal (not internal)
            if db_path == self.internal_db_path:
                return False, "Cannot modify internal database"
            
            database = self._load_database(db_path)
            
            # Get item name and create lowercase key
            item_name = item_data.get("name", "")
            if not item_name:
                return False, "Item name is required"
            
            search_key = item_name.lower()
            items = database.setdefault("items", {})
            
            # Check if item already exists
            if search_key in items:
                existing_item = items[search_key]
                
                # Update realm ID if different realm
                if "realms" in existing_item:
                    # Multi-realm item
                    if realm not in existing_item["realms"]:
                        existing_item["realms"][realm] = item_data.get("id")
                        logging.info(f"Added realm {realm} to existing item '{item_name}'", 
                            extra={"action": "ITEMDB_ADD"})
                    else:
                        # Item already exists for this realm
                        return False, f"Item '{item_name}' already exists for realm {realm}"
                else:
                    # Single-realm item, convert to multi-realm
                    old_realm = existing_item.get("realm", realm)
                    existing_item["realms"] = {
                        old_realm: existing_item.get("id"),
                        realm: item_data.get("id")
                    }
                    if "realm" in existing_item:
                        del existing_item["realm"]
                    if "id" in existing_item:
                        del existing_item["id"]
                    logging.info(f"Converted item '{item_name}' to multi-realm", extra={"action": "ITEMDB_ADD"})
            else:
                # New item - structure depends on whether it has multi-realm data
                new_item = {
                    "name": item_name,
                    "type": item_data.get("type", ""),
                    "slot": item_data.get("slot", ""),
                    "zone": item_data.get("zone", ""),
                    "price": item_data.get("price", ""),
                    "currency": item_data.get("currency", ""),
                    "merchants": item_data.get("merchants", [])
                }
                
                # Add realm ID
                if "realms" in item_data:
                    new_item["realms"] = item_data["realms"]
                else:
                    new_item["realms"] = {realm: item_data.get("id", "")}
                
                # Mark as user-added
                new_item["user_added"] = True
                new_item["added_date"] = datetime.now().strftime("%Y-%m-%d")
                
                items[search_key] = new_item
                logging.info(f"Added new item '{item_name}' to database", extra={"action": "ITEMDB_ADD"})
            
            # Save database
            if self._save_database(db_path, database):
                return True, f"Item '{item_name}' added successfully"
            else:
                return False, "Failed to save database"
                
        except Exception as e:
            logging.error(f"Error adding scraped item: {e}", extra={"action": "ITEMDB_ADD_ERROR"})
            return False, str(e)

    def get_statistics(self) -> Dict[str, int]:
        """
        Get database statistics
        
        Returns:
            Dict: Statistics with keys:
                - internal_count: Number of items in internal database
                - personal_count: Number of items in personal database (or -1 if not exists)
                - user_added_count: Number of user-added items (or -1 if not exists)
        """
        stats = {
            "internal_count": 0,
            "personal_count": -1,
            "user_added_count": -1
        }
        
        try:
            # Internal database count
            if self.internal_db_path.exists():
                internal_db = self._load_database(self.internal_db_path)
                stats["internal_count"] = len(internal_db.get("items", {}))
            
            # Personal database count
            armor_path = self.config_manager.config.get("folders", {}).get("armor")
            if armor_path:
                personal_db_path = Path(armor_path) / "items_database.json"
                if personal_db_path.exists():
                    personal_db = self._load_database(personal_db_path)
                    items = personal_db.get("items", {})
                    stats["personal_count"] = len(items)
                    
                    # Count user-added items
                    user_added = sum(1 for item in items.values() if item.get("user_added", False))
                    stats["user_added_count"] = user_added
            
            logging.info(f"Database statistics: {stats}", extra={"action": "ITEMDB_STATS"})
            
        except Exception as e:
            logging.error(f"Error getting statistics: {e}", extra={"action": "ITEMDB_STATS_ERROR"})
        
        return stats

    def reset_personal_database(self) -> Tuple[bool, str]:
        """
        Reset personal database by replacing it with a fresh copy of internal database
        
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        try:
            # Get personal database path
            armor_path = self.config_manager.config.get("folders", {}).get("armor")
            if not armor_path:
                return False, "Armory path not configured"
            
            personal_db_path = Path(armor_path) / "items_database.json"
            
            # Check if internal database exists
            if not self.internal_db_path.exists():
                return False, f"Internal database not found at {self.internal_db_path}"
            
            # Delete old personal database if exists
            if personal_db_path.exists():
                personal_db_path.unlink()
                logging.info(f"Deleted old personal database at {personal_db_path}", extra={"action": "ITEMDB_RESET"})
            
            # Copy internal database to personal location
            shutil.copy2(self.internal_db_path, personal_db_path)
            
            # Update config
            internal_db = self._load_database(self.internal_db_path)
            self.config_manager.config.setdefault("armory", {})
            self.config_manager.config["armory"]["last_internal_db_version"] = internal_db.get("version", "1.0")
            self.config_manager.save_config()
            
            logging.info(f"Reset personal database from internal copy", extra={"action": "ITEMDB_RESET"})
            return True, "Personal database reset successfully"
            
        except Exception as e:
            logging.error(f"Error resetting personal database: {e}", extra={"action": "ITEMDB_RESET_ERROR"})
            return False, str(e)
