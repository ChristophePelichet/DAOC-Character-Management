"""
Migration Manager - Handles structural migrations for the character folder
"""
import os
import json
import shutil
import logging
import zipfile
from datetime import datetime
from Functions.config_manager import config
from Functions.path_manager import get_base_path

def get_character_dir():
    """Returns the configured character directory."""
    default_path = os.path.join(get_base_path(), "Characters")
    return config.get("character_folder") or default_path

def get_backup_path():
    """
    Returns the planned backup path without creating it.
    
    Returns:
        str: The full path where the backup will be created (as .zip)
    """
    base_path = get_base_path()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"Characters_backup_{timestamp}.zip"
    backup_dir = os.path.join(base_path, "Backup", "Characters")
    backup_path = os.path.join(backup_dir, backup_name)
    return backup_path

def backup_characters():
    """
    Creates a compressed backup (.zip) of the entire Characters folder before migration.
    Backup is stored in Backup/Characters/ folder.
    
    Returns:
        tuple: (success: bool, backup_path: str, message: str)
    """
    base_char_dir = get_character_dir()
    
    if not os.path.exists(base_char_dir):
        return False, "", "Characters directory does not exist"
    
    try:
        # Create backup directory structure
        base_path = get_base_path()
        backup_dir = os.path.join(base_path, "Backup", "Characters")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"Characters_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_name)
        
        logging.info(f"Creating compressed backup: {backup_path}")
        
        # Create zip file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the Characters directory
            for root, dirs, files in os.walk(base_char_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the archive name (relative path from Characters)
                    arcname = os.path.relpath(file_path, os.path.dirname(base_char_dir))
                    zipf.write(file_path, arcname)
                    logging.debug(f"Added to backup: {arcname}")
        
        logging.info(f"Compressed backup created successfully: {backup_path}")
        return True, backup_path, f"Backup created: {backup_name}"
        
    except Exception as e:
        error_msg = f"Backup failed: {str(e)}"
        logging.error(error_msg)
        return False, "", error_msg

def check_migration_needed():
    """
    Checks if migration from old structure (Characters/Realm) to new structure 
    (Characters/Season/Realm) is needed.
    
    Returns:
        bool: True if migration is needed, False otherwise
    """
    base_char_dir = get_character_dir()
    
    if not os.path.exists(base_char_dir):
        logging.info("Character directory does not exist yet. No migration needed.")
        return False
    
    # Check if old structure exists (Realm folders directly under Characters)
    old_structure_exists = False
    realms = ["Albion", "Hibernia", "Midgard"]
    
    for realm in realms:
        realm_path = os.path.join(base_char_dir, realm)
        if os.path.exists(realm_path) and os.path.isdir(realm_path):
            # Check if there are JSON files in this realm folder
            json_files = [f for f in os.listdir(realm_path) if f.endswith('.json')]
            if json_files:
                old_structure_exists = True
                logging.info(f"Found old structure: {realm_path} contains {len(json_files)} character(s)")
                break
    
    return old_structure_exists

def migrate_character_structure():
    """
    Migrates character files from old structure (Characters/Realm/character.json)
    to new structure (Characters/Season/Realm/character.json).
    
    Characters without season info will be placed in a default season folder.
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    base_char_dir = get_character_dir()
    realms = ["Albion", "Hibernia", "Midgard"]
    
    stats = {
        "total_characters": 0,
        "migrated": 0,
        "errors": 0,
        "by_season": {}
    }
    
    logging.info("=" * 60)
    logging.info("Starting character structure migration...")
    logging.info(f"Base directory: {base_char_dir}")
    logging.info("=" * 60)
    
    try:
        # Process each realm
        for realm in realms:
            old_realm_path = os.path.join(base_char_dir, realm)
            
            if not os.path.exists(old_realm_path):
                continue
            
            if not os.path.isdir(old_realm_path):
                continue
            
            # Get all JSON files in the old realm folder
            json_files = [f for f in os.listdir(old_realm_path) if f.endswith('.json')]
            
            logging.info(f"\nProcessing realm: {realm}")
            logging.info(f"Found {len(json_files)} character file(s)")
            
            for json_file in json_files:
                stats["total_characters"] += 1
                old_file_path = os.path.join(old_realm_path, json_file)
                
                try:
                    # Read character data to get season
                    with open(old_file_path, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                    
                    # Get season from character data, default to "S1" if not present
                    season = char_data.get('season', 'S1')
                    if not season:
                        season = 'S1'
                        logging.warning(f"Character {json_file} has no season, defaulting to S1")
                    
                    # Create new directory structure
                    new_season_path = os.path.join(base_char_dir, season)
                    new_realm_path = os.path.join(new_season_path, realm)
                    os.makedirs(new_realm_path, exist_ok=True)
                    
                    # New file path
                    new_file_path = os.path.join(new_realm_path, json_file)
                    
                    # Copy file to new location
                    shutil.copy2(old_file_path, new_file_path)
                    logging.info(f"  ✓ Migrated: {json_file} -> {season}/{realm}/")
                    
                    stats["migrated"] += 1
                    stats["by_season"][season] = stats["by_season"].get(season, 0) + 1
                    
                except Exception as e:
                    logging.error(f"  ✗ Error migrating {json_file}: {e}")
                    stats["errors"] += 1
            
            # After successful migration of all files in this realm, remove the old folder
            if json_files and stats["errors"] == 0:
                try:
                    # Remove all JSON files from old location
                    for json_file in json_files:
                        os.remove(os.path.join(old_realm_path, json_file))
                    
                    # Try to remove the old realm folder if empty
                    if not os.listdir(old_realm_path):
                        os.rmdir(old_realm_path)
                        logging.info(f"  ✓ Removed empty old folder: {realm}/")
                    else:
                        logging.warning(f"  ! Old folder {realm}/ not empty, keeping it")
                except Exception as e:
                    logging.warning(f"  ! Could not clean up old folder {realm}/: {e}")
        
        # Summary
        logging.info("\n" + "=" * 60)
        logging.info("Migration Summary:")
        logging.info(f"  Total characters found: {stats['total_characters']}")
        logging.info(f"  Successfully migrated: {stats['migrated']}")
        logging.info(f"  Errors: {stats['errors']}")
        if stats["by_season"]:
            logging.info("  Characters by season:")
            for season, count in sorted(stats["by_season"].items()):
                logging.info(f"    {season}: {count} character(s)")
        logging.info("=" * 60)
        
        if stats["errors"] > 0:
            return False, f"Migration completed with {stats['errors']} error(s)", stats
        elif stats["migrated"] == 0:
            return True, "No characters to migrate", stats
        else:
            return True, f"Successfully migrated {stats['migrated']} character(s)", stats
            
    except Exception as e:
        error_msg = f"Migration failed: {e}"
        logging.error(error_msg)
        return False, error_msg, stats

def mark_migration_done():
    """
    Marks the migration as completed by creating a flag file.
    """
    base_char_dir = get_character_dir()
    flag_file = os.path.join(base_char_dir, ".migration_done")
    
    try:
        with open(flag_file, 'w') as f:
            f.write("Migration to Season/Realm structure completed")
        logging.info("Migration flag file created")
        return True
    except Exception as e:
        logging.error(f"Could not create migration flag file: {e}")
        return False

def is_migration_done():
    """
    Checks if migration has already been completed.
    
    Returns:
        bool: True if migration was already done, False otherwise
    """
    base_char_dir = get_character_dir()
    flag_file = os.path.join(base_char_dir, ".migration_done")
    return os.path.exists(flag_file)

def run_migration_if_needed():
    """
    Runs migration automatically if needed and not already done.
    This should be called once at application startup.
    
    Returns:
        tuple: (was_needed: bool, success: bool, message: str)
    """
    # Check if migration was already done
    if is_migration_done():
        logging.debug("Migration already completed (flag file exists)")
        return False, True, "Migration already completed"
    
    # Check if migration is needed
    if not check_migration_needed():
        logging.info("No migration needed - structure is already correct")
        mark_migration_done()
        return False, True, "No migration needed"
    
    # Migration is needed - return this info so UI can show confirmation dialog
    logging.info("Migration needed - waiting for user confirmation...")
    return True, False, "Migration needed - awaiting user confirmation"

def run_migration_with_backup():
    """
    Runs migration with automatic backup.
    
    Returns:
        tuple: (success: bool, message: str, backup_path: str)
    """
    logging.info("=" * 60)
    logging.info("Starting migration with backup...")
    logging.info("=" * 60)
    
    # Create backup first
    backup_success, backup_path, backup_msg = backup_characters()
    
    if not backup_success:
        error_msg = f"Backup failed: {backup_msg}\nMigration cancelled for safety."
        logging.error(error_msg)
        return False, error_msg, ""
    
    logging.info(f"Backup successful: {backup_path}")
    
    # Run migration
    logging.info("Starting character structure migration...")
    success, message, stats = migrate_character_structure()
    
    if success:
        mark_migration_done()
        full_message = f"{message}\n\nBackup location: {backup_path}"
        return True, full_message, backup_path
    else:
        full_message = f"{message}\n\nYour original files are safe in: {backup_path}"
        return False, full_message, backup_path
