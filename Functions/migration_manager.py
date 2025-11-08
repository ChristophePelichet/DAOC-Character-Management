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
from Functions.language_manager import lang
from Functions.logging_manager import get_logger, log_with_action, LOGGER_BACKUP

logger = get_logger(LOGGER_BACKUP)

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
    Validates backup integrity after creation.
    
    Returns:
        tuple: (success: bool, backup_path: str, message: str)
    """
    base_char_dir = get_character_dir()
    
    if not os.path.exists(base_char_dir):
        return False, "", "Characters directory does not exist"
    
    backup_path = ""
    
    try:
        # Create backup directory structure
        base_path = get_base_path()
        backup_dir = os.path.join(base_path, "Backup", "Characters")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"Characters_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_name)
        
        log_with_action(logger, "info", f"Creating compressed backup: {backup_path}", action="MIGRATION_ZIP")
        
        # Count files to backup for validation
        files_added = 0
        
        # Create zip file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the Characters directory
            for root, dirs, files in os.walk(base_char_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the archive name (relative path from Characters)
                    arcname = os.path.relpath(file_path, os.path.dirname(base_char_dir))
                    zipf.write(file_path, arcname)
                    files_added += 1
                    log_with_action(logger, "debug", f"Added to backup: {arcname}", action="MIGRATION_ZIP")
        
        log_with_action(logger, "info", f"Compressed backup created with {files_added} file(s): {backup_path}", action="MIGRATION_ZIP")
        
        # CRITICAL: Verify backup integrity
        try:
            log_with_action(logger, "info", "Verifying backup integrity...", action="MIGRATION_VERIFY")
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Test the ZIP file integrity
                bad_file = zipf.testzip()
                if bad_file:
                    error_msg = f"Backup verification failed: corrupted file {bad_file}"
                    log_with_action(logger, "error", error_msg, action="MIGRATION_VERIFY_FAILED")
                    # Delete corrupted backup
                    try:
                        os.remove(backup_path)
                    except:
                        pass
                    return False, "", error_msg
                
                # Verify file count
                zip_files = len(zipf.namelist())
                if zip_files != files_added:
                    error_msg = f"Backup verification failed: expected {files_added} files, found {zip_files}"
                    log_with_action(logger, "error", error_msg, action="MIGRATION_VERIFY_FAILED")
                    try:
                        os.remove(backup_path)
                    except:
                        pass
                    return False, "", error_msg
            
            log_with_action(logger, "info", f"✓ Backup integrity verified: {zip_files} file(s) OK", action="MIGRATION_VERIFY")
            
        except zipfile.BadZipFile as e:
            error_msg = f"Backup verification failed: invalid ZIP file - {str(e)}"
            log_with_action(logger, "error", error_msg, action="MIGRATION_VERIFY_FAILED")
            try:
                os.remove(backup_path)
            except:
                pass
            return False, "", error_msg
        
        log_with_action(logger, "info", f"Compressed backup created successfully: {backup_path}", action="MIGRATION_SUCCESS")
        return True, backup_path, f"Backup created: {backup_name}"
        
    except Exception as e:
        error_msg = f"Backup failed: {str(e)}"
        log_with_action(logger, "error", error_msg, action="MIGRATION_BACKUP_ERROR")
        # Clean up partial backup if it exists
        if backup_path and os.path.exists(backup_path):
            try:
                os.remove(backup_path)
                log_with_action(logger, "info", "Cleaned up partial backup file", action="MIGRATION_CLEANUP")
            except:
                pass
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
        log_with_action(logger, "info", "Character directory does not exist yet. No migration needed.", action="MIGRATION_CHECK")
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
                log_with_action(logger, "info", f"Found old structure: {realm_path} contains {len(json_files)} character(s)", action="MIGRATION_CHECK")
                break
    
    return old_structure_exists

def migrate_character_structure():
    """
    Migrates character files from old structure (Characters/Realm/character.json)
    to new structure (Characters/Season/Realm/character.json).
    
    Characters without season info will be placed in a default season folder.
    If any errors occur, performs automatic rollback to preserve data integrity.
    
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
    
    # Track all migrated files for potential rollback
    migrated_files = []  # List of (old_path, new_path) tuples
    
    log_with_action(logger, "info", "=" * 60, action="MIGRATION_START")
    log_with_action(logger, "info", "Starting character structure migration...", action="MIGRATION_START")
    log_with_action(logger, "info", f"Base directory: {base_char_dir}", action="MIGRATION_START")
    log_with_action(logger, "info", "=" * 60, action="MIGRATION_START")
    
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
            
            log_with_action(logger, "info", f"\nProcessing realm: {realm}", action="MIGRATION_PROCESS")
            log_with_action(logger, "info", f"Found {len(json_files)} character file(s)", action="MIGRATION_PROCESS")
            
            for json_file in json_files:
                stats["total_characters"] += 1
                old_file_path = os.path.join(old_realm_path, json_file)
                
                try:
                    # CRITICAL: Validate JSON before processing
                    with open(old_file_path, 'r', encoding='utf-8') as f:
                        try:
                            char_data = json.load(f)
                        except json.JSONDecodeError as je:
                            error_msg = f"Invalid JSON in {json_file}: {str(je)}"
                            log_with_action(logger, "error", f"  ✗ {error_msg}", action="MIGRATION_JSON_ERROR")
                            stats["errors"] += 1
                            continue  # Skip this file but continue with others
                    
                    # Validate that it's a dictionary
                    if not isinstance(char_data, dict):
                        log_with_action(logger, "error", f"  ✗ Invalid character data in {json_file}: not a dictionary", action="MIGRATION_INVALID_DATA")
                        stats["errors"] += 1
                        continue
                    
                    # Get season from character data, default to "S1" if not present
                    season = char_data.get('season', 'S1')
                    if not season or not isinstance(season, str):
                        season = 'S1'
                        log_with_action(logger, "warning", f"Character {json_file} has invalid/missing season, defaulting to S1", action="MIGRATION_NO_SEASON")
                    
                    # Create new directory structure
                    new_season_path = os.path.join(base_char_dir, season)
                    new_realm_path = os.path.join(new_season_path, realm)
                    os.makedirs(new_realm_path, exist_ok=True)
                    
                    # New file path
                    new_file_path = os.path.join(new_realm_path, json_file)
                    
                    # Check if target file already exists (safety check)
                    if os.path.exists(new_file_path):
                        log_with_action(logger, "warning", f"  ! Target file already exists: {new_file_path}, skipping", action="MIGRATION_FILE_EXISTS")
                        stats["errors"] += 1
                        continue
                    
                    # Copy file to new location (use copy2 to preserve metadata)
                    shutil.copy2(old_file_path, new_file_path)
                    
                    # Verify the copy was successful by reading it
                    try:
                        with open(new_file_path, 'r', encoding='utf-8') as f:
                            verify_data = json.load(f)
                        # Basic verification that data is intact
                        if verify_data != char_data:
                            raise Exception("Copied file data doesn't match original")
                    except Exception as ve:
                        log_with_action(logger, "error", f"  ✗ Copy verification failed for {json_file}: {str(ve)}", action="MIGRATION_VERIFY_FAILED")
                        # Remove the invalid copy
                        try:
                            os.remove(new_file_path)
                        except:
                            pass
                        stats["errors"] += 1
                        continue
                    
                    log_with_action(logger, "info", f"  ✓ Migrated: {json_file} -> {season}/{realm}/", action="MIGRATION_SUCCESS")
                    
                    # Track successful migration for potential rollback
                    migrated_files.append((old_file_path, new_file_path))
                    
                    stats["migrated"] += 1
                    stats["by_season"][season] = stats["by_season"].get(season, 0) + 1
                    
                except Exception as e:
                    log_with_action(logger, "error", f"  ✗ Error migrating {json_file}: {e}", action="MIGRATION_ERROR")
                    stats["errors"] += 1
            
            # CRITICAL: Only remove old files if ALL files in this realm migrated successfully
            realm_files_count = len([f for f in json_files])
            realm_migrated_count = len([mf for mf in migrated_files if realm in mf[0]])
            
            if realm_files_count > 0 and realm_migrated_count == realm_files_count:
                try:
                    # Remove all JSON files from old location
                    for json_file in json_files:
                        old_file = os.path.join(old_realm_path, json_file)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    
                    # Try to remove the old realm folder if empty
                    if os.path.exists(old_realm_path) and not os.listdir(old_realm_path):
                        os.rmdir(old_realm_path)
                        log_with_action(logger, "info", f"  ✓ Removed empty old folder: {realm}/", action="MIGRATION_CLEANUP")
                    else:
                        log_with_action(logger, "warning", f"  ! Old folder {realm}/ not empty, keeping it", action="MIGRATION_CLEANUP")
                except Exception as e:
                    log_with_action(logger, "warning", f"  ! Could not clean up old folder {realm}/: {e}", action="MIGRATION_CLEANUP_ERROR")
            else:
                log_with_action(logger, "warning", f"  ! Not all files migrated for {realm} ({realm_migrated_count}/{realm_files_count}), keeping old folder", action="MIGRATION_INCOMPLETE")
        
        # Summary
        log_with_action(logger, "info", "\n" + "=" * 60, action="MIGRATION_SUMMARY")
        log_with_action(logger, "info", "Migration Summary:", action="MIGRATION_SUMMARY")
        log_with_action(logger, "info", f"  Total characters found: {stats['total_characters']}", action="MIGRATION_SUMMARY")
        log_with_action(logger, "info", f"  Successfully migrated: {stats['migrated']}", action="MIGRATION_SUMMARY")
        log_with_action(logger, "info", f"  Errors: {stats['errors']}", action="MIGRATION_SUMMARY")
        if stats["by_season"]:
            log_with_action(logger, "info", "  Characters by season:", action="MIGRATION_SUMMARY")
            for season, count in sorted(stats["by_season"].items()):
                log_with_action(logger, "info", f"    {season}: {count} character(s)", action="MIGRATION_SUMMARY")
        log_with_action(logger, "info", "=" * 60, action="MIGRATION_SUMMARY")
        
        # CRITICAL: If there were errors, perform rollback
        if stats["errors"] > 0:
            log_with_action(logger, "error", "⚠️  ERRORS DETECTED - Performing rollback to preserve data integrity", action="MIGRATION_ROLLBACK")
            rollback_count = 0
            for old_path, new_path in migrated_files:
                try:
                    if os.path.exists(new_path):
                        os.remove(new_path)
                        rollback_count += 1
                        log_with_action(logger, "info", f"  Rolled back: {os.path.basename(new_path)}", action="MIGRATION_ROLLBACK")
                except Exception as re:
                    log_with_action(logger, "error", f"  ✗ Rollback failed for {new_path}: {re}", action="MIGRATION_ROLLBACK_ERROR")
            
            log_with_action(logger, "info", f"Rollback completed: {rollback_count}/{len(migrated_files)} files removed from new location", action="MIGRATION_ROLLBACK")
            error_message = f"Migration failed with {stats['errors']} error(s). All changes have been rolled back. Your original files are safe."
            return False, error_message, stats
        
        elif stats["migrated"] == 0:
            return True, lang.get("migration_no_characters"), stats
        else:
            return True, lang.get("migration_success_message", count=stats['migrated']), stats
            
    except Exception as e:
        error_msg = f"Migration failed with critical error: {e}"
        log_with_action(logger, "error", error_msg, action="MIGRATION_CRITICAL_ERROR")
        
        # CRITICAL: Perform rollback on critical failure
        if migrated_files:
            log_with_action(logger, "error", "⚠️  CRITICAL FAILURE - Attempting rollback", action="MIGRATION_CRITICAL_ROLLBACK")
            rollback_count = 0
            for old_path, new_path in migrated_files:
                try:
                    if os.path.exists(new_path):
                        os.remove(new_path)
                        rollback_count += 1
                except:
                    pass
            log_with_action(logger, "info", f"Emergency rollback: {rollback_count}/{len(migrated_files)} files removed", action="MIGRATION_CRITICAL_ROLLBACK")
        
        return False, f"{error_msg}\nRollback performed. Your original files are safe.", stats

def mark_migration_done():
    """
    Marks the migration as completed by creating a flag file.
    """
    base_char_dir = get_character_dir()
    flag_file = os.path.join(base_char_dir, ".migration_done")
    
    try:
        with open(flag_file, 'w') as f:
            f.write("Migration to Season/Realm structure completed")
        log_with_action(logger, "info", "Migration flag file created", action="MIGRATION_DONE")
        return True
    except Exception as e:
        log_with_action(logger, "error", f"Could not create migration flag file: {e}", action="MIGRATION_FLAG_ERROR")
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
        log_with_action(logger, "debug", "Migration already completed (flag file exists)", action="MIGRATION_CHECK")
        return False, True, "Migration already completed"
    
    # Check if migration is needed
    if not check_migration_needed():
        log_with_action(logger, "info", "No migration needed - structure is already correct", action="MIGRATION_NOT_NEEDED")
        mark_migration_done()
        return False, True, "No migration needed"
    
    # Migration is needed - return this info so UI can show confirmation dialog
    log_with_action(logger, "info", "Migration needed - waiting for user confirmation...", action="MIGRATION_NEEDS_CONFIRM")
    return True, False, "Migration needed - awaiting user confirmation"

def run_migration_with_backup():
    """
    Runs migration with automatic backup.
    Only marks migration as done if completely successful (no errors).
    
    Returns:
        tuple: (success: bool, message: str, backup_path: str)
    """
    log_with_action(logger, "info", "=" * 60, action="MIGRATION_START_BACKUP")
    log_with_action(logger, "info", "Starting migration with backup...", action="MIGRATION_START_BACKUP")
    log_with_action(logger, "info", "=" * 60, action="MIGRATION_START_BACKUP")
    
    # Create backup first
    backup_success, backup_path, backup_msg = backup_characters()
    
    if not backup_success:
        error_msg = f"Backup failed: {backup_msg}\nMigration cancelled for safety."
        log_with_action(logger, "error", error_msg, action="MIGRATION_BACKUP_FAILED")
        return False, error_msg, ""
    
    log_with_action(logger, "info", f"✓ Backup successful: {backup_path}", action="MIGRATION_BACKUP_SUCCESS")
    log_with_action(logger, "info", f"✓ Backup verified and ready for recovery if needed", action="MIGRATION_BACKUP_READY")
    
    # Run migration
    log_with_action(logger, "info", "Starting character structure migration...", action="MIGRATION_START")
    success, message, stats = migrate_character_structure()
    
    if success:
        # CRITICAL: Only mark as done if truly successful (no errors)
        if stats.get("errors", 0) == 0:
            mark_migration_done()
            log_with_action(logger, "info", "✓ Migration marked as completed", action="MIGRATION_DONE")
        else:
            log_with_action(logger, "warning", "⚠️  Migration had errors, not marking as done", action="MIGRATION_HAS_ERRORS")
        
        # Return only the migration message, let the UI handle backup path display
        return True, message, backup_path
    else:
        # On failure, rollback was already performed, don't mark as done
        log_with_action(logger, "error", "✗ Migration failed, rollback performed, not marking as done", action="MIGRATION_FAILED_ROLLBACK")
        # Include backup path in message for safety info
        full_message = f"{message}\n\n✓ Your original files are safe in:\n{backup_path}"
        return False, full_message, backup_path


# ============================================================================
# JSON STRUCTURE VALIDATION AND UPGRADE
# ============================================================================

def get_expected_json_structure():
    """
    Returns the expected structure for character JSON files with default values.
    This serves as the reference for validation and migration.
    
    Returns:
        dict: Dictionary with field names and their default values
    """
    return {
        # Basic character info
        "id": "",
        "name": "",
        "realm": "Albion",
        "class": "",
        "race": "",
        "level": 1,
        
        # Organization
        "season": "S1",
        "server": "Eden",
        "page": 1,
        "guild": "",
        
        # Realm rank (RvR)
        "realm_rank": "",          # Code format: "1L0", "5L3", etc.
        "realm_title": "",         # Text format: "Guardian", "Warlord", etc.
        "realm_points": 0,         # Numeric points
        
        # Eden Herald integration
        "url": "",                 # Herald URL for the character
        
        # Metadata
        "created_at": "",
        "updated_at": ""
    }


def validate_and_upgrade_json_structure(file_path):
    """
    Validates a character JSON file and upgrades its structure if needed.
    Adds missing fields with default values while preserving existing data.
    
    Args:
        file_path (str): Path to the JSON file to validate/upgrade
        
    Returns:
        tuple: (needs_update: bool, updated_data: dict, changes: list)
    """
    try:
        # Read existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            char_data = json.load(f)
        
        if not isinstance(char_data, dict):
            logging.error(f"Invalid JSON structure in {file_path}: not a dictionary")
            return False, None, []
        
        expected_structure = get_expected_json_structure()
        changes = []
        needs_update = False
        
        # Check for missing fields and add them
        for field, default_value in expected_structure.items():
            if field not in char_data:
                char_data[field] = default_value
                changes.append(f"Added missing field: {field} = {default_value}")
                needs_update = True
                logging.debug(f"  + Added field '{field}' with default value")
        
        # Validate/fix realm_rank format (should be like "1L0", "5L3")
        if 'realm_rank' in char_data:
            realm_rank = char_data.get('realm_rank', '')
            # If realm_rank looks like a title (text) instead of code, clear it
            if realm_rank and not any(c.isdigit() for c in str(realm_rank)):
                logging.warning(f"  ! realm_rank '{realm_rank}' looks like a title, clearing it")
                char_data['realm_rank'] = ""
                changes.append("Fixed realm_rank: cleared invalid format")
                needs_update = True
        
        # Ensure realm_points is numeric
        if 'realm_points' in char_data:
            try:
                rp = char_data['realm_points']
                if isinstance(rp, str):
                    # Remove spaces and convert to int
                    rp_clean = int(rp.replace(' ', '').replace('\xa0', '').replace(',', ''))
                    if rp_clean != rp:
                        char_data['realm_points'] = rp_clean
                        changes.append(f"Normalized realm_points: {rp} -> {rp_clean}")
                        needs_update = True
                elif not isinstance(rp, int):
                    char_data['realm_points'] = 0
                    changes.append("Fixed realm_points: set to 0 (was invalid type)")
                    needs_update = True
            except:
                char_data['realm_points'] = 0
                changes.append("Fixed realm_points: set to 0 (conversion failed)")
                needs_update = True
        
        # Ensure level is numeric and within valid range (1-50)
        if 'level' in char_data:
            try:
                level = int(char_data['level'])
                if level < 1 or level > 50:
                    old_level = level
                    level = max(1, min(50, level))
                    char_data['level'] = level
                    changes.append(f"Fixed level: {old_level} -> {level} (clamped to 1-50)")
                    needs_update = True
            except:
                char_data['level'] = 1
                changes.append("Fixed level: set to 1 (was invalid)")
                needs_update = True
        
        # Ensure page is numeric and within valid range (1-5)
        if 'page' in char_data:
            try:
                page = int(char_data['page'])
                if page < 1 or page > 5:
                    old_page = page
                    page = max(1, min(5, page))
                    char_data['page'] = page
                    changes.append(f"Fixed page: {old_page} -> {page} (clamped to 1-5)")
                    needs_update = True
            except:
                char_data['page'] = 1
                changes.append("Fixed page: set to 1 (was invalid)")
                needs_update = True
        
        return needs_update, char_data, changes
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {file_path}: {e}")
        return False, None, [f"ERROR: Invalid JSON - {str(e)}"]
    except Exception as e:
        logging.error(f"Error validating {file_path}: {e}")
        return False, None, [f"ERROR: {str(e)}"]


def upgrade_all_character_files():
    """
    Scans all character JSON files and upgrades their structure if needed.
    Creates a backup before making any changes.
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    base_char_dir = get_character_dir()
    
    if not os.path.exists(base_char_dir):
        return False, "Characters directory does not exist", {}
    
    stats = {
        "total_files": 0,
        "checked": 0,
        "upgraded": 0,
        "errors": 0,
        "skipped": 0
    }
    
    changes_by_file = {}
    
    logging.info("=" * 60)
    logging.info("Starting JSON structure validation and upgrade...")
    logging.info(f"Base directory: {base_char_dir}")
    logging.info("=" * 60)
    
    try:
        # Walk through all directories to find JSON files
        for root, dirs, files in os.walk(base_char_dir):
            for file in files:
                if not file.endswith('.json'):
                    continue
                
                if file.startswith('.'):  # Skip hidden files like .migration_done
                    continue
                
                stats["total_files"] += 1
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_char_dir)
                
                logging.info(f"\nChecking: {rel_path}")
                
                needs_update, updated_data, changes = validate_and_upgrade_json_structure(file_path)
                stats["checked"] += 1
                
                if updated_data is None:
                    # Error occurred
                    logging.error(f"  ✗ Error: {changes[0] if changes else 'Unknown error'}")
                    stats["errors"] += 1
                    continue
                
                if not needs_update:
                    logging.info(f"  ✓ Structure OK, no changes needed")
                    continue
                
                # File needs updating
                logging.info(f"  → Upgrading structure...")
                for change in changes:
                    logging.info(f"    • {change}")
                
                try:
                    # Create backup of original file
                    backup_path = file_path + '.backup'
                    shutil.copy2(file_path, backup_path)
                    
                    # Write updated data
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(updated_data, f, indent=2, ensure_ascii=False)
                    
                    # Verify the write was successful
                    with open(file_path, 'r', encoding='utf-8') as f:
                        verify_data = json.load(f)
                    
                    # Remove backup if verification successful
                    os.remove(backup_path)
                    
                    logging.info(f"  ✓ Successfully upgraded")
                    stats["upgraded"] += 1
                    changes_by_file[rel_path] = changes
                    
                except Exception as e:
                    logging.error(f"  ✗ Failed to upgrade: {e}")
                    stats["errors"] += 1
                    
                    # Restore from backup if it exists
                    if os.path.exists(backup_path):
                        try:
                            shutil.copy2(backup_path, file_path)
                            os.remove(backup_path)
                            logging.info(f"  ✓ Restored from backup")
                        except:
                            logging.error(f"  ✗ Could not restore from backup!")
        
        # Summary
        logging.info("\n" + "=" * 60)
        logging.info("JSON Structure Upgrade Summary:")
        logging.info(f"  Total JSON files found: {stats['total_files']}")
        logging.info(f"  Files checked: {stats['checked']}")
        logging.info(f"  Files upgraded: {stats['upgraded']}")
        logging.info(f"  Errors: {stats['errors']}")
        logging.info(f"  Skipped: {stats['skipped']}")
        
        if changes_by_file:
            logging.info("\nDetailed changes:")
            for file_path, changes in changes_by_file.items():
                logging.info(f"  {file_path}:")
                for change in changes:
                    logging.info(f"    • {change}")
        
        logging.info("=" * 60)
        
        if stats["errors"] > 0:
            message = f"Structure upgrade completed with {stats['errors']} error(s). {stats['upgraded']} file(s) upgraded successfully."
            return True, message, stats
        elif stats["upgraded"] == 0:
            message = f"All {stats['total_files']} character files already have the correct structure."
            return True, message, stats
        else:
            message = f"Successfully upgraded {stats['upgraded']} character file(s) to the latest structure."
            return True, message, stats
            
    except Exception as e:
        error_msg = f"JSON structure upgrade failed: {e}"
        logging.error(error_msg)
        return False, error_msg, stats


def check_and_upgrade_json_structures_if_needed():
    """
    Checks if any character JSON files need structure upgrades and performs them.
    This should be called after folder structure migration.
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    logging.info("Checking for JSON structure upgrades...")
    
    # Run the upgrade process
    success, message, stats = upgrade_all_character_files()
    
    return success, message, stats