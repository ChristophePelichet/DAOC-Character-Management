"""
Character File Migration System
Handles automatic migration of character files from old structure to new season-based structure.

Old structure: Characters/Realm/CharName.json
New structure: Characters/Season/Realm/CharName.json

Migration process:
1. Detect if old structure exists
2. Create backup ZIP of all character files
3. Migrate each file to new structure based on season field
4. Validate migrated files
5. Mark migration as complete
6. Rollback on any error
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging

# Import schema functions
try:
    from Functions.character_schema import (
        validate_character_data,
        normalize_character_data,
        get_default_season,
        get_default_server,
        get_character_info_summary,
        VALID_REALMS
    )
except ImportError:
    from character_schema import (
        validate_character_data,
        normalize_character_data,
        get_default_season,
        get_default_server,
        get_character_info_summary,
        VALID_REALMS
    )

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

CHARACTERS_DIR = "Characters"
BACKUP_DIR = "Backup/Characters"
MIGRATION_FLAG = os.path.join(CHARACTERS_DIR, ".migration_done")

# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================

def detect_old_structure() -> bool:
    """
    Detects if old character structure exists (Characters/Realm/*.json).
    
    Returns:
        bool: True if old structure detected, False otherwise
    """
    if not os.path.exists(CHARACTERS_DIR):
        logger.debug("Characters directory does not exist")
        return False
    
    # Check for direct realm folders in Characters/
    for realm in VALID_REALMS:
        realm_path = os.path.join(CHARACTERS_DIR, realm)
        if os.path.exists(realm_path) and os.path.isdir(realm_path):
            # Check if there are JSON files in this realm folder
            json_files = [f for f in os.listdir(realm_path) if f.endswith('.json')]
            if json_files:
                logger.info(f"Old structure detected: {realm_path} contains {len(json_files)} character(s)")
                return True
    
    logger.debug("No old structure detected")
    return False

def is_migration_done() -> bool:
    """
    Checks if migration has already been completed.
    
    Returns:
        bool: True if migration flag exists, False otherwise
    """
    exists = os.path.exists(MIGRATION_FLAG)
    if exists:
        logger.debug(f"Migration flag found: {MIGRATION_FLAG}")
    return exists

def mark_migration_done():
    """
    Creates migration completion flag file.
    """
    os.makedirs(CHARACTERS_DIR, exist_ok=True)
    
    with open(MIGRATION_FLAG, 'w', encoding='utf-8') as f:
        f.write(f"Migration completed: {datetime.now().isoformat()}\n")
        f.write(f"Old structure (Characters/Realm/) migrated to new structure (Characters/Season/Realm/)\n")
    
    logger.info(f"Migration flag created: {MIGRATION_FLAG}")

# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================

def backup_characters() -> Tuple[Optional[str], int]:
    """
    Creates ZIP backup of all existing character files.
    
    Returns:
        tuple: (backup_path: str or None, file_count: int)
            - backup_path: Path to created ZIP file, or None if no files to backup
            - file_count: Number of files backed up
    """
    if not os.path.exists(CHARACTERS_DIR):
        logger.warning("Characters directory does not exist, nothing to backup")
        return None, 0
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"Characters_migration_backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Count files and create ZIP
    file_count = 0
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through Characters directory
            for root, dirs, files in os.walk(CHARACTERS_DIR):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        # Store with relative path from Characters/
                        arcname = os.path.relpath(file_path, CHARACTERS_DIR)
                        zipf.write(file_path, arcname=f"Characters/{arcname}")
                        file_count += 1
        
        # Validate ZIP
        if file_count == 0:
            os.remove(backup_path)
            logger.warning("No character files found to backup")
            return None, 0
        
        # Verify ZIP integrity
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if zipf.testzip() is not None:
                    logger.error(f"Backup ZIP is corrupted: {backup_path}")
                    os.remove(backup_path)
                    return None, 0
        except Exception as e:
            logger.error(f"Failed to validate backup ZIP: {e}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return None, 0
        
        logger.info(f"Backup created: {backup_path} ({file_count} files)")
        return backup_path, file_count
        
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        if os.path.exists(backup_path):
            os.remove(backup_path)
        return None, 0

# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def determine_season_from_data(char_data: Dict[str, Any]) -> str:
    """
    Determines season from character data.
    
    Args:
        char_data: Character data dictionary
        
    Returns:
        str: Season identifier (e.g., "S3")
    """
    # Check if season field exists and is valid
    if "season" in char_data and char_data["season"]:
        season = char_data["season"].strip()
        if season and season.startswith('S'):
            return season
    
    # Fallback to default season
    default_season = get_default_season()
    logger.debug(f"Using default season: {default_season}")
    return default_season

def migrate_character_file(old_path: str, char_data: Dict[str, Any]) -> Optional[str]:
    """
    Migrates a single character file to new structure.
    
    Args:
        old_path: Path to old character file
        char_data: Character data dictionary
        
    Returns:
        str: New file path if successful, None otherwise
    """
    try:
        # Normalize data (adds missing fields)
        normalized_data = normalize_character_data(char_data)
        
        # Validate normalized data
        is_valid, errors = validate_character_data(normalized_data)
        if not is_valid:
            logger.error(f"Character data validation failed for {old_path}:")
            for error in errors:
                logger.error(f"  - {error}")
            return None
        
        # Determine season and realm
        season = determine_season_from_data(normalized_data)
        realm = normalized_data.get("realm", "")
        
        if not realm or realm not in VALID_REALMS:
            logger.error(f"Invalid or missing realm for {old_path}: '{realm}'")
            return None
        
        # Build new path
        filename = os.path.basename(old_path)
        new_dir = os.path.join(CHARACTERS_DIR, season, realm)
        new_path = os.path.join(new_dir, filename)
        
        # Create new directory
        os.makedirs(new_dir, exist_ok=True)
        
        # Write normalized data to new location
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2, ensure_ascii=False)
        
        # Verify file was written correctly
        if not os.path.exists(new_path):
            logger.error(f"Failed to create new file: {new_path}")
            return None
        
        # Verify file is readable and valid JSON
        try:
            with open(new_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except Exception as e:
            logger.error(f"New file is not valid JSON: {new_path} - {e}")
            os.remove(new_path)
            return None
        
        logger.debug(f"Migrated: {old_path} → {new_path}")
        return new_path
        
    except Exception as e:
        logger.error(f"Failed to migrate {old_path}: {e}")
        return None

def migrate_all_characters() -> Tuple[bool, str, Dict[str, Any]]:
    """
    Migrates all character files from old structure to new structure.
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
            - success: True if all files migrated successfully
            - message: Status message
            - stats: Dictionary with migration statistics
    """
    stats = {
        "total": 0,
        "migrated": 0,
        "failed": 0,
        "skipped": 0,
        "migrated_files": [],  # Track for rollback
        "old_files": []        # Track for cleanup
    }
    
    try:
        # Find all character files in old structure
        for realm in VALID_REALMS:
            realm_path = os.path.join(CHARACTERS_DIR, realm)
            if not os.path.exists(realm_path) or not os.path.isdir(realm_path):
                continue
            
            # Get all JSON files in this realm
            for filename in os.listdir(realm_path):
                if not filename.endswith('.json'):
                    continue
                
                old_path = os.path.join(realm_path, filename)
                stats["total"] += 1
                stats["old_files"].append(old_path)
                
                # Read character data
                try:
                    with open(old_path, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to read {old_path}: {e}")
                    stats["failed"] += 1
                    continue
                
                # Migrate file
                new_path = migrate_character_file(old_path, char_data)
                
                if new_path:
                    stats["migrated"] += 1
                    stats["migrated_files"].append(new_path)
                    logger.info(f"✓ {get_character_info_summary(char_data)}")
                else:
                    stats["failed"] += 1
                    logger.error(f"✗ Failed to migrate: {old_path}")
        
        # Check if all files migrated successfully
        if stats["total"] == 0:
            return True, "No character files found to migrate", stats
        
        if stats["failed"] > 0:
            # Rollback if any failures
            logger.error(f"Migration failed: {stats['failed']}/{stats['total']} files failed")
            rollback_count = rollback_migration(stats["migrated_files"])
            return False, f"Migration failed: {stats['failed']} errors. Rolled back {rollback_count} files.", stats
        
        # Success - remove old files and empty directories
        cleanup_old_structure(stats["old_files"])
        
        message = f"Migration successful: {stats['migrated']}/{stats['total']} characters migrated"
        logger.info(message)
        return True, message, stats
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        # Rollback on unexpected error
        if stats["migrated_files"]:
            rollback_count = rollback_migration(stats["migrated_files"])
            return False, f"Migration error: {e}. Rolled back {rollback_count} files.", stats
        return False, f"Migration error: {e}", stats

def rollback_migration(migrated_files: List[str]) -> int:
    """
    Rolls back migration by removing newly created files.
    
    Args:
        migrated_files: List of file paths that were migrated
        
    Returns:
        int: Number of files rolled back
    """
    rollback_count = 0
    
    for file_path in migrated_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                rollback_count += 1
                logger.debug(f"Rolled back: {file_path}")
        except Exception as e:
            logger.error(f"Failed to rollback {file_path}: {e}")
    
    logger.info(f"Rollback completed: {rollback_count} files removed")
    return rollback_count

def cleanup_old_structure(old_files: List[str]):
    """
    Removes old character files and empty realm directories.
    
    Args:
        old_files: List of old file paths to remove
    """
    removed_count = 0
    
    # Remove old files
    for file_path in old_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                removed_count += 1
                logger.debug(f"Removed old file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to remove old file {file_path}: {e}")
    
    # Remove empty realm directories
    for realm in VALID_REALMS:
        realm_path = os.path.join(CHARACTERS_DIR, realm)
        if os.path.exists(realm_path) and os.path.isdir(realm_path):
            try:
                # Check if directory is empty
                if not os.listdir(realm_path):
                    os.rmdir(realm_path)
                    logger.debug(f"Removed empty directory: {realm_path}")
            except Exception as e:
                logger.error(f"Failed to remove directory {realm_path}: {e}")
    
    logger.info(f"Cleanup completed: {removed_count} old files removed")

# ============================================================================
# MAIN MIGRATION ORCHESTRATION
# ============================================================================

def run_migration(silent: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Main migration orchestration function.
    
    Args:
        silent: If True, only log to file. If False, print to console.
        
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    logger.info("=" * 60)
    logger.info("Character File Migration Started")
    logger.info("=" * 60)
    
    # Check if migration already done
    if is_migration_done():
        message = "Migration already completed (flag file exists)"
        logger.info(message)
        return True, message, {"status": "already_done"}
    
    # Check if old structure exists
    if not detect_old_structure():
        message = "No old structure detected, nothing to migrate"
        logger.info(message)
        # Mark as done to avoid checking again
        mark_migration_done()
        return True, message, {"status": "nothing_to_migrate"}
    
    # Create backup
    logger.info("Creating backup...")
    backup_path, backup_count = backup_characters()
    
    if backup_path is None:
        message = "Failed to create backup, migration aborted"
        logger.error(message)
        return False, message, {"status": "backup_failed"}
    
    logger.info(f"Backup created: {backup_path} ({backup_count} files)")
    
    # Run migration
    logger.info("Starting file migration...")
    success, message, stats = migrate_all_characters()
    
    if success:
        # Mark migration as complete
        mark_migration_done()
        logger.info("Migration completed successfully")
        logger.info(f"Statistics: {stats['migrated']} migrated, {stats['failed']} failed")
    else:
        logger.error("Migration failed")
        logger.error(message)
    
    logger.info("=" * 60)
    
    return success, message, stats

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
    success, message, stats = run_migration(silent=False)
    
    print(f"\nMigration Result:")
    print(f"  Success: {success}")
    print(f"  Message: {message}")
    print(f"  Stats: {stats}")
