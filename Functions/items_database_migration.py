"""
Items Database Migration System
Handles automatic migration of personal items database when embedded database structure changes.

Migration strategy:
1. Embedded DB (items_database_src.json) has version metadata
2. Personal DB (Armory/items_database.json) has version metadata
3. On load, compare versions
4. If personal DB version < embedded DB version, apply migrations
5. Preserve user-added custom items
6. Update standard items with new fields/structure
7. Create backup before migration

Version history:
- v1: Initial structure (legacy, pre-metadata)
- v2: Added _metadata section with version tracking
- v3+: Future migrations as needed
"""

import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

EMBEDDED_DB_PATH = "Data/items_database_src.json"
PERSONAL_DB_PATH = "Armory/items_database.json"
BACKUP_DIR = "Backup/Database"

# Current database version (increment when structure changes)
CURRENT_DB_VERSION = 2

# ============================================================================
# METADATA FUNCTIONS
# ============================================================================

def get_db_version(db_data: Dict[str, Any]) -> int:
    """
    Get database version from metadata.
    
    Args:
        db_data: Database dictionary
        
    Returns:
        int: Version number (1 if no metadata found)
    """
    # Check for _metadata section (v2+)
    if "_metadata" in db_data:
        return db_data["_metadata"].get("version", 1)
    
    # Legacy structure detection (v1)
    # v1 has "version" as string at root level
    if "version" in db_data and isinstance(db_data.get("version"), str):
        return 1
    
    # Default to v1 if no version info
    return 1


def create_metadata(version: int, item_count: int) -> Dict[str, Any]:
    """
    Create metadata section for database.
    
    Args:
        version: Database version number
        item_count: Number of items in database
        
    Returns:
        dict: Metadata dictionary
    """
    return {
        "version": version,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_count": item_count,
        "migration_history": []
    }


def add_migration_record(metadata: Dict[str, Any], from_version: int, to_version: int):
    """
    Add migration record to metadata history.
    
    Args:
        metadata: Metadata dictionary to update
        from_version: Source version
        to_version: Target version
    """
    if "migration_history" not in metadata:
        metadata["migration_history"] = []
    
    metadata["migration_history"].append({
        "from_version": from_version,
        "to_version": to_version,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================

def create_backup(db_path: str) -> Tuple[Optional[str], bool]:
    """
    Create ZIP backup of items database.
    
    Args:
        db_path: Path to database file
        
    Returns:
        tuple: (backup_path: str or None, success: bool)
    """
    if not os.path.exists(db_path):
        logger.warning(f"Database file does not exist: {db_path}")
        return None, False
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = Path(db_path).stem  # items_database or items_database_src
    backup_filename = f"{db_name}_migration_backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(db_path, arcname=os.path.basename(db_path))
        
        # Verify ZIP integrity
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            if zipf.testzip() is not None:
                logger.error(f"Backup ZIP is corrupted: {backup_path}")
                os.remove(backup_path)
                return None, False
        
        logger.info(f"[ITEMS DB MIGRATION] Backup created: {backup_path}")
        return backup_path, True
        
    except Exception as e:
        logger.error(f"[ITEMS DB MIGRATION] Failed to create backup: {e}")
        if os.path.exists(backup_path):
            os.remove(backup_path)
        return None, False


# ============================================================================
# ITEM COMPARISON & MERGING
# ============================================================================

def get_item_key(item: Dict[str, Any]) -> str:
    """
    Generate unique key for an item (composite key: name:realm).
    
    Args:
        item: Item dictionary
        
    Returns:
        str: Unique item key (lowercase)
    """
    name = item.get("name", "").lower()
    realm = item.get("realm", "").lower()
    return f"{name}:{realm}"


def is_custom_item(item_key: str, embedded_items: Dict[str, Any]) -> bool:
    """
    Check if item is custom (user-added, not in embedded DB).
    
    Args:
        item_key: Item composite key
        embedded_items: Embedded database items dictionary
        
    Returns:
        bool: True if custom item
    """
    return item_key not in embedded_items


def merge_item_data(embedded_item: Dict[str, Any], personal_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge embedded item data with personal item, preserving user customizations.
    
    Strategy:
    - Use embedded data as base (ensures new fields are added)
    - Preserve personal customizations for specific fields if they differ
    - Mark customized fields with _custom_fields metadata
    
    Args:
        embedded_item: Item from embedded database (source of truth)
        personal_item: Item from personal database (may have customizations)
        
    Returns:
        dict: Merged item data
    """
    merged = embedded_item.copy()
    
    # Fields that users might customize (preserve if different from embedded)
    customizable_fields = [
        "usable_by",  # User might restrict classes
        "bypass_filters",  # User might change filter behavior
        "notes"  # User might add notes
    ]
    
    custom_fields = []
    
    for field in customizable_fields:
        # If field exists in personal but not in embedded, preserve it
        if field in personal_item and field not in embedded_item:
            merged[field] = personal_item[field]
            custom_fields.append(field)
        # If field exists in both and values differ, preserve personal value
        elif field in personal_item and field in embedded_item:
            if personal_item[field] != embedded_item[field]:
                merged[field] = personal_item[field]
                custom_fields.append(field)
    
    # Add metadata about customizations
    if custom_fields:
        merged["_custom_fields"] = custom_fields
    
    return merged


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def migrate_v1_to_v2(v1_data: Dict[str, Any], embedded_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate database from v1 to v2 structure.
    
    Changes in v2:
    - Add _metadata section
    - Preserve user custom items
    - Update standard items with latest embedded data
    - Track migration history
    
    Args:
        v1_data: v1 database dictionary
        embedded_data: Current embedded database (for reference)
        
    Returns:
        dict: v2 database dictionary
    """
    logger.info("[ITEMS DB MIGRATION] Migrating v1 → v2...")
    
    v1_items = v1_data.get("items", {})
    embedded_items = embedded_data.get("items", {})
    
    # Initialize v2 structure
    v2_data = {
        "_metadata": create_metadata(version=2, item_count=0),
        "items": {}
    }
    
    # Add migration record
    add_migration_record(v2_data["_metadata"], from_version=1, to_version=2)
    
    # Process each item in personal DB
    custom_items = []
    updated_items = []
    
    for item_key, personal_item in v1_items.items():
        if is_custom_item(item_key, embedded_items):
            # Custom item - preserve as-is
            v2_data["items"][item_key] = personal_item
            custom_items.append(item_key)
            logger.debug(f"[ITEMS DB MIGRATION] Preserved custom item: {item_key}")
        else:
            # Standard item - merge with embedded data
            embedded_item = embedded_items[item_key]
            merged_item = merge_item_data(embedded_item, personal_item)
            v2_data["items"][item_key] = merged_item
            updated_items.append(item_key)
            logger.debug(f"[ITEMS DB MIGRATION] Updated standard item: {item_key}")
    
    # Add new items from embedded DB that don't exist in personal DB
    new_items = []
    for item_key, embedded_item in embedded_items.items():
        if item_key not in v2_data["items"]:
            v2_data["items"][item_key] = embedded_item.copy()
            new_items.append(item_key)
            logger.debug(f"[ITEMS DB MIGRATION] Added new item from embedded: {item_key}")
    
    # Update metadata
    v2_data["_metadata"]["item_count"] = len(v2_data["items"])
    v2_data["_metadata"]["custom_items_count"] = len(custom_items)
    v2_data["_metadata"]["updated_items_count"] = len(updated_items)
    v2_data["_metadata"]["new_items_count"] = len(new_items)
    
    logger.info(f"[ITEMS DB MIGRATION] v1 → v2 complete:")
    logger.info(f"  - Total items: {len(v2_data['items'])}")
    logger.info(f"  - Custom items preserved: {len(custom_items)}")
    logger.info(f"  - Standard items updated: {len(updated_items)}")
    logger.info(f"  - New items added: {len(new_items)}")
    
    return v2_data


def apply_migrations(personal_data: Dict[str, Any], embedded_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    Apply all necessary migrations to bring personal DB up to current version.
    
    Args:
        personal_data: Personal database data
        embedded_data: Embedded database data (reference)
        
    Returns:
        tuple: (migrated_data: dict, success: bool)
    """
    current_version = get_db_version(personal_data)
    target_version = CURRENT_DB_VERSION
    
    if current_version >= target_version:
        logger.info(f"[ITEMS DB MIGRATION] Database already at version {current_version}, no migration needed")
        return personal_data, True
    
    logger.info(f"[ITEMS DB MIGRATION] Starting migration: v{current_version} → v{target_version}")
    
    migrated_data = personal_data
    
    try:
        # Apply migrations sequentially
        if current_version < 2:
            migrated_data = migrate_v1_to_v2(migrated_data, embedded_data)
            current_version = 2
        
        # Future migrations would go here:
        # if current_version < 3:
        #     migrated_data = migrate_v2_to_v3(migrated_data, embedded_data)
        #     current_version = 3
        
        logger.info(f"[ITEMS DB MIGRATION] Migration successful: v{get_db_version(personal_data)} → v{current_version}")
        return migrated_data, True
        
    except Exception as e:
        logger.error(f"[ITEMS DB MIGRATION] Migration failed: {e}")
        return personal_data, False


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_migrated_database(db_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate migrated database structure.
    
    Args:
        db_data: Migrated database dictionary
        
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    # Check for _metadata section
    if "_metadata" not in db_data:
        errors.append("Missing '_metadata' section")
    else:
        metadata = db_data["_metadata"]
        
        # Check required metadata fields
        required_fields = ["version", "last_update", "item_count"]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
        
        # Validate version
        if "version" in metadata:
            if not isinstance(metadata["version"], int):
                errors.append("Metadata 'version' must be an integer")
            elif metadata["version"] < 1:
                errors.append("Metadata 'version' must be >= 1")
    
    # Check for items section
    if "items" not in db_data:
        errors.append("Missing 'items' section")
    elif not isinstance(db_data["items"], dict):
        errors.append("'items' section must be a dictionary")
    
    # Validate item count
    if "_metadata" in db_data and "items" in db_data:
        expected_count = db_data["_metadata"].get("item_count", 0)
        actual_count = len(db_data["items"])
        if expected_count != actual_count:
            errors.append(f"Item count mismatch: metadata={expected_count}, actual={actual_count}")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info("[ITEMS DB MIGRATION] Validation: ✅ OK")
    else:
        logger.warning(f"[ITEMS DB MIGRATION] Validation: ❌ {len(errors)} errors")
        for error in errors:
            logger.warning(f"  - {error}")
    
    return is_valid, errors


# ============================================================================
# MAIN MIGRATION ORCHESTRATION
# ============================================================================

def needs_migration(personal_db_path: str, embedded_db_path: str) -> Tuple[bool, int, int]:
    """
    Check if personal database needs migration.
    
    Args:
        personal_db_path: Path to personal database
        embedded_db_path: Path to embedded database
        
    Returns:
        tuple: (needs_migration: bool, personal_version: int, embedded_version: int)
    """
    # Check if personal DB exists
    if not os.path.exists(personal_db_path):
        logger.debug("[ITEMS DB MIGRATION] Personal DB does not exist, no migration needed")
        return False, 0, CURRENT_DB_VERSION
    
    try:
        # Load personal DB
        with open(personal_db_path, 'r', encoding='utf-8') as f:
            personal_data = json.load(f)
        
        personal_version = get_db_version(personal_data)
        
        # Load embedded DB to get latest version
        with open(embedded_db_path, 'r', encoding='utf-8') as f:
            embedded_data = json.load(f)
        
        embedded_version = get_db_version(embedded_data)
        
        needs = personal_version < embedded_version
        
        if needs:
            logger.info(f"[ITEMS DB MIGRATION] Migration needed: personal v{personal_version} < embedded v{embedded_version}")
        else:
            logger.debug(f"[ITEMS DB MIGRATION] No migration needed: personal v{personal_version} >= embedded v{embedded_version}")
        
        return needs, personal_version, embedded_version
        
    except Exception as e:
        logger.error(f"[ITEMS DB MIGRATION] Error checking migration status: {e}")
        return False, 0, CURRENT_DB_VERSION


def migrate_personal_database(
    personal_db_path: str = PERSONAL_DB_PATH,
    embedded_db_path: str = EMBEDDED_DB_PATH,
    dry_run: bool = False
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Main migration orchestration for personal items database.
    
    Args:
        personal_db_path: Path to personal database
        embedded_db_path: Path to embedded database
        dry_run: If True, don't save changes (testing only)
        
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    logger.info("=" * 70)
    logger.info("ITEMS DATABASE MIGRATION STARTED")
    logger.info("=" * 70)
    
    stats = {
        "personal_version": 0,
        "embedded_version": CURRENT_DB_VERSION,
        "migration_applied": False,
        "backup_created": False,
        "custom_items_preserved": 0,
        "standard_items_updated": 0,
        "new_items_added": 0
    }
    
    try:
        # Check if migration needed
        needs, personal_version, embedded_version = needs_migration(personal_db_path, embedded_db_path)
        stats["personal_version"] = personal_version
        stats["embedded_version"] = embedded_version
        
        if not needs:
            message = f"No migration needed (personal DB is v{personal_version})"
            logger.info(f"[ITEMS DB MIGRATION] {message}")
            logger.info("=" * 70)
            return True, message, stats
        
        # Load databases
        with open(personal_db_path, 'r', encoding='utf-8') as f:
            personal_data = json.load(f)
        
        with open(embedded_db_path, 'r', encoding='utf-8') as f:
            embedded_data = json.load(f)
        
        # Create backup
        if not dry_run:
            logger.info("[ITEMS DB MIGRATION] Creating backup...")
            backup_path, backup_success = create_backup(personal_db_path)
            stats["backup_created"] = backup_success
            
            if not backup_success:
                message = "Failed to create backup, migration aborted"
                logger.error(f"[ITEMS DB MIGRATION] {message}")
                logger.info("=" * 70)
                return False, message, stats
            
            logger.info(f"[ITEMS DB MIGRATION] Backup: {backup_path}")
        
        # Apply migrations
        logger.info("[ITEMS DB MIGRATION] Applying migrations...")
        migrated_data, migration_success = apply_migrations(personal_data, embedded_data)
        
        if not migration_success:
            message = "Migration failed"
            logger.error(f"[ITEMS DB MIGRATION] {message}")
            logger.info("=" * 70)
            return False, message, stats
        
        stats["migration_applied"] = True
        
        # Validate migrated data
        is_valid, errors = validate_migrated_database(migrated_data)
        
        if not is_valid:
            message = f"Validation failed: {', '.join(errors)}"
            logger.error(f"[ITEMS DB MIGRATION] {message}")
            logger.info("=" * 70)
            return False, message, stats
        
        # Extract stats from metadata
        if "_metadata" in migrated_data:
            metadata = migrated_data["_metadata"]
            stats["custom_items_preserved"] = metadata.get("custom_items_count", 0)
            stats["standard_items_updated"] = metadata.get("updated_items_count", 0)
            stats["new_items_added"] = metadata.get("new_items_count", 0)
        
        # Save migrated data
        if not dry_run:
            with open(personal_db_path, 'w', encoding='utf-8') as f:
                json.dump(migrated_data, f, indent=2, ensure_ascii=False)
            logger.info(f"[ITEMS DB MIGRATION] Saved migrated database to: {personal_db_path}")
        
        message = f"Migration successful: v{personal_version} → v{embedded_version}"
        logger.info(f"[ITEMS DB MIGRATION] {message}")
        logger.info(f"[ITEMS DB MIGRATION] Custom items preserved: {stats['custom_items_preserved']}")
        logger.info(f"[ITEMS DB MIGRATION] Standard items updated: {stats['standard_items_updated']}")
        logger.info(f"[ITEMS DB MIGRATION] New items added: {stats['new_items_added']}")
        logger.info("=" * 70)
        
        return True, message, stats
        
    except Exception as e:
        message = f"Migration error: {e}"
        logger.error(f"[ITEMS DB MIGRATION] {message}")
        logger.info("=" * 70)
        return False, message, stats


def rollback_migration(backup_path: str, target_path: str) -> Tuple[bool, str]:
    """
    Rollback migration by restoring from backup.
    
    Args:
        backup_path: Path to backup ZIP file
        target_path: Path where to restore database
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not os.path.exists(backup_path):
        return False, f"Backup file not found: {backup_path}"
    
    try:
        # Extract backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Get the database filename from ZIP
            filenames = zipf.namelist()
            if not filenames:
                return False, "Backup ZIP is empty"
            
            db_filename = filenames[0]
            
            # Extract to target location
            extracted_path = zipf.extract(db_filename, path=os.path.dirname(target_path))
            
            # Move to target location if names differ
            if extracted_path != target_path:
                shutil.move(extracted_path, target_path)
        
        logger.info(f"[ITEMS DB MIGRATION] Rollback successful: restored from {backup_path}")
        return True, f"Restored from {os.path.basename(backup_path)}"
        
    except Exception as e:
        error_msg = f"Rollback failed: {str(e)}"
        logger.error(f"[ITEMS DB MIGRATION] {error_msg}")
        return False, error_msg


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Setup console logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migration
    success, message, stats = migrate_personal_database(dry_run=False)
    
    print(f"\nMigration Result:")
    print(f"  Success: {success}")
    print(f"  Message: {message}")
    print(f"  Stats: {stats}")
