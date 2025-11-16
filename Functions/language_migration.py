"""
Language Migration Module - v1 (flat) to v2 (hierarchical)

Handles automatic migration of language files from flat structure to hierarchical structure.
Similar to config_migration.py but adapted for language files.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Tuple, List
import logging

from .language_schema import LANGUAGE_LEGACY_MAPPING, is_v2_structure

logger = logging.getLogger(__name__)


def detect_language_version(lang_data: Dict[str, Any]) -> str:
    """
    Detect if language file is v1 (flat) or v2 (hierarchical).
    
    Args:
        lang_data: Dictionary containing language strings
    
    Returns:
        "v1" or "v2"
    """
    if is_v2_structure(lang_data):
        return "v2"
    return "v1"


def create_backup(lang_file: str) -> bool:
    """
    Create timestamped backup of language file before migration.
    
    Args:
        lang_file: Path to language file
    
    Returns:
        True if backup successful, False otherwise
    """
    if not os.path.exists(lang_file):
        logger.warning(f"Language file does not exist: {lang_file}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{lang_file}.backup_{timestamp}"
    
    try:
        shutil.copy2(lang_file, backup_file)
        logger.info(f"[LANGUAGE MIGRATION] Backup created: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"[LANGUAGE MIGRATION] Failed to create backup: {e}")
        return False


def migrate_v1_to_v2(v1_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate language data from v1 (flat) to v2 (hierarchical) structure.
    
    Args:
        v1_data: v1 language dictionary (flat structure)
    
    Returns:
        v2 language dictionary (hierarchical structure)
    """
    logger.info("[LANGUAGE MIGRATION] Starting migration from v1 to v2...")
    
    # Initialize empty v2 structure
    v2_data = {}
    
    # Track unknown keys (not in mapping)
    unknown_keys = []
    migrated_count = 0
    
    # Migrate each key using the mapping
    for v1_key, value in v1_data.items():
        if v1_key in LANGUAGE_LEGACY_MAPPING:
            v2_key = LANGUAGE_LEGACY_MAPPING[v1_key]
            _set_nested_value(v2_data, v2_key, value)
            logger.debug(f"[LANGUAGE MIGRATION] Migrated: {v1_key} → {v2_key}")
            migrated_count += 1
        else:
            unknown_keys.append(v1_key)
            logger.warning(f"[LANGUAGE MIGRATION] Unknown key: {v1_key}")
    
    # Preserve unknown keys in a special section for safety
    if unknown_keys:
        v2_data["_unknown_v1_keys"] = {}
        for key in unknown_keys:
            v2_data["_unknown_v1_keys"][key] = v1_data[key]
        logger.warning(f"[LANGUAGE MIGRATION] {len(unknown_keys)} unknown keys preserved in _unknown_v1_keys")
    
    logger.info(f"[LANGUAGE MIGRATION] Migration complete: {migrated_count} keys migrated")
    
    return v2_data


def _set_nested_value(data: Dict[str, Any], dotted_key: str, value: Any):
    """
    Set value in nested dictionary using dotted notation.
    
    Args:
        data: Dictionary to modify
        dotted_key: Key in dotted notation (e.g., "window.main_title")
        value: Value to set
    """
    keys = dotted_key.split(".")
    current = data
    
    # Navigate/create nested structure
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            # Key exists but is not a dict - create backup
            logger.warning(f"[LANGUAGE MIGRATION] Key conflict at '{key}' - creating nested structure")
            current[key] = {}
        current = current[key]
    
    # Set final value
    final_key = keys[-1]
    current[final_key] = value


def validate_migrated_language(lang_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate migrated language structure.
    
    Args:
        lang_data: Migrated v2 language dictionary
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check for required top-level sections
    required_sections = ["app", "window", "menu", "dialogs", "buttons", "columns"]
    
    for section in required_sections:
        if section not in lang_data:
            errors.append(f"Missing required section: {section}")
    
    # Check app section
    if "app" in lang_data:
        if not isinstance(lang_data["app"], dict):
            errors.append("'app' section must be a dictionary")
        elif "language_name" not in lang_data["app"]:
            errors.append("Missing 'app.language_name'")
    
    # Check window section
    if "window" in lang_data:
        if not isinstance(lang_data["window"], dict):
            errors.append("'window' section must be a dictionary")
        elif "main_title" not in lang_data["window"]:
            errors.append("Missing 'window.main_title'")
    
    # Check menu section
    if "menu" in lang_data:
        if not isinstance(lang_data["menu"], dict):
            errors.append("'menu' section must be a dictionary")
        else:
            required_menus = ["file", "help"]
            for menu in required_menus:
                if menu not in lang_data["menu"]:
                    errors.append(f"Missing 'menu.{menu}' section")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info("[LANGUAGE MIGRATION] Validation: ✅ OK")
    else:
        logger.warning(f"[LANGUAGE MIGRATION] Validation: ❌ {len(errors)} errors found")
        for error in errors:
            logger.warning(f"  - {error}")
    
    return is_valid, errors


def get_migration_summary(v1_data: Dict[str, Any], v2_data: Dict[str, Any]) -> str:
    """
    Generate detailed migration summary report.
    
    Args:
        v1_data: Original v1 language dictionary
        v2_data: Migrated v2 language dictionary
    
    Returns:
        Formatted summary string
    """
    v1_count = len(v1_data)
    
    # Count v2 keys (excluding _unknown_v1_keys)
    def count_keys(d, exclude_key="_unknown_v1_keys"):
        count = 0
        for k, v in d.items():
            if k == exclude_key:
                continue
            if isinstance(v, dict):
                count += count_keys(v)
            else:
                count += 1
        return count
    
    v2_count = count_keys(v2_data)
    unknown_count = len(v2_data.get("_unknown_v1_keys", {}))
    
    summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              LANGUAGE MIGRATION SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistics:
   • v1 keys (flat):        {v1_count}
   • v2 keys (hierarchical): {v2_count}
   • Unknown keys preserved: {unknown_count}

📁 Structure:
   • v1: Flat dictionary (all keys at root)
   • v2: Hierarchical (12 main sections)

✅ Migration Status: {'SUCCESS' if unknown_count == 0 else 'SUCCESS (with warnings)'}

"""
    
    if unknown_count > 0:
        summary += f"⚠️  Warning: {unknown_count} unknown keys preserved in '_unknown_v1_keys'\n"
        summary += "   Please review and map these keys manually.\n"
    
    return summary


def migrate_language_file(lang_file: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Migrate a single language file from v1 to v2.
    
    Args:
        lang_file: Path to language file (.json)
        dry_run: If True, don't save changes (testing only)
    
    Returns:
        Tuple of (success, message)
    """
    if not os.path.exists(lang_file):
        return False, f"File not found: {lang_file}"
    
    try:
        # Load current data
        with open(lang_file, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
        
        # Check version
        version = detect_language_version(lang_data)
        logger.info(f"[LANGUAGE MIGRATION] File: {os.path.basename(lang_file)} - Detected version: {version}")
        
        if version == "v2":
            return True, "Already v2 format - no migration needed"
        
        # Create backup
        if not dry_run:
            if not create_backup(lang_file):
                return False, "Failed to create backup"
        
        # Migrate
        v2_data = migrate_v1_to_v2(lang_data)
        
        # Validate
        is_valid, errors = validate_migrated_language(v2_data)
        
        if not is_valid:
            error_msg = "Validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(f"[LANGUAGE MIGRATION] {error_msg}")
            return False, error_msg
        
        # Save migrated data
        if not dry_run:
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(v2_data, f, ensure_ascii=False, indent=4)
            logger.info(f"[LANGUAGE MIGRATION] Saved v2 format to: {lang_file}")
        
        # Generate summary
        summary = get_migration_summary(lang_data, v2_data)
        logger.info(summary)
        
        return True, "Migration successful"
    
    except Exception as e:
        error_msg = f"Migration failed: {str(e)}"
        logger.error(f"[LANGUAGE MIGRATION] {error_msg}")
        return False, error_msg


def migrate_all_language_files(lang_dir: str, dry_run: bool = False) -> Dict[str, Tuple[bool, str]]:
    """
    Migrate all language files in a directory.
    
    Args:
        lang_dir: Path to Language directory
        dry_run: If True, don't save changes (testing only)
    
    Returns:
        Dictionary mapping filename to (success, message)
    """
    results = {}
    
    if not os.path.exists(lang_dir):
        logger.error(f"[LANGUAGE MIGRATION] Language directory not found: {lang_dir}")
        return results
    
    for filename in os.listdir(lang_dir):
        if filename.endswith('.json') and not filename.endswith('.backup'):
            lang_file = os.path.join(lang_dir, filename)
            logger.info(f"\n[LANGUAGE MIGRATION] Processing: {filename}")
            success, message = migrate_language_file(lang_file, dry_run)
            results[filename] = (success, message)
            
            if success:
                logger.info(f"[LANGUAGE MIGRATION] ✅ {filename}: {message}")
            else:
                logger.error(f"[LANGUAGE MIGRATION] ❌ {filename}: {message}")
    
    return results


def rollback_migration(lang_file: str, backup_file: str = None) -> Tuple[bool, str]:
    """
    Rollback migration by restoring from backup.
    
    Args:
        lang_file: Path to language file
        backup_file: Path to specific backup file (if None, finds latest)
    
    Returns:
        Tuple of (success, message)
    """
    if backup_file is None:
        # Find latest backup
        backup_pattern = f"{lang_file}.backup_"
        backups = [f for f in os.listdir(os.path.dirname(lang_file)) 
                   if f.startswith(os.path.basename(backup_pattern))]
        
        if not backups:
            return False, "No backup file found"
        
        backups.sort(reverse=True)  # Latest first
        backup_file = os.path.join(os.path.dirname(lang_file), backups[0])
    
    try:
        shutil.copy2(backup_file, lang_file)
        logger.info(f"[LANGUAGE MIGRATION] Rollback successful: {lang_file} restored from {backup_file}")
        return True, f"Restored from {os.path.basename(backup_file)}"
    except Exception as e:
        error_msg = f"Rollback failed: {str(e)}"
        logger.error(f"[LANGUAGE MIGRATION] {error_msg}")
        return False, error_msg
