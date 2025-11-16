"""
Configuration Migration Tools
Version: v0.108
Author: Christophe Pelichet
Description: Handles automatic migration from v1 (flat) to v2 (hierarchical) config structure
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Tuple, Optional
from .config_schema import DEFAULT_CONFIG, LEGACY_KEY_MAPPING


def detect_config_version(config: Dict) -> str:
    """
    Detect the configuration version.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        "v1" for flat structure, "v2" for hierarchical structure
    """
    # v2 has top-level sections: ui, folders, backup, system, game
    v2_sections = ["ui", "folders", "backup", "system", "game"]
    
    # Check if all v2 sections exist
    if all(section in config for section in v2_sections):
        return "v2"
    
    # Check if any v1 keys exist
    v1_keys = ["language", "theme", "character_folder", "backup_enabled"]
    if any(key in config for key in v1_keys):
        return "v1"
    
    # Default to v2 for empty config
    return "v2"


def create_backup(config_path: str) -> bool:
    """
    Create a backup of the current config file.
    
    Args:
        config_path: Path to the config.json file
    
    Returns:
        True if backup created successfully, False otherwise
    """
    try:
        if not os.path.exists(config_path):
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{config_path}.backup_{timestamp}"
        
        shutil.copy2(config_path, backup_path)
        print(f"[CONFIG MIGRATION] Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"[CONFIG MIGRATION] Error creating backup: {e}")
        return False


def migrate_v1_to_v2(old_config: Dict) -> Dict:
    """
    Migrate configuration from v1 (flat) to v2 (hierarchical) structure.
    
    Args:
        old_config: Old configuration dictionary (flat structure)
    
    Returns:
        New configuration dictionary (hierarchical structure)
    """
    print("[CONFIG MIGRATION] Starting migration from v1 to v2...")
    
    # Start with default v2 structure
    new_config = json.loads(json.dumps(DEFAULT_CONFIG))  # Deep copy
    
    # Migrate each key using the mapping
    migrated_count = 0
    for old_key, new_key_path in LEGACY_KEY_MAPPING.items():
        if old_key in old_config:
            value = old_config[old_key]
            
            # Navigate to the nested location and set the value
            parts = new_key_path.split(".")
            target = new_config
            
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            
            # Set the final value
            target[parts[-1]] = value
            migrated_count += 1
            print(f"[CONFIG MIGRATION] Migrated: {old_key} → {new_key_path} = {value}")
    
    # Preserve any unknown keys at root level (for future compatibility)
    unknown_keys = set(old_config.keys()) - set(LEGACY_KEY_MAPPING.keys())
    if unknown_keys:
        print(f"[CONFIG MIGRATION] Warning: Unknown keys found (preserved): {unknown_keys}")
        for key in unknown_keys:
            if key not in new_config:
                new_config[key] = old_config[key]
    
    print(f"[CONFIG MIGRATION] Migration complete: {migrated_count} keys migrated")
    return new_config


def migrate_v2_to_v1(new_config: Dict) -> Dict:
    """
    Migrate configuration from v2 (hierarchical) back to v1 (flat) structure.
    This is mainly for testing and backward compatibility.
    
    Args:
        new_config: New configuration dictionary (hierarchical structure)
    
    Returns:
        Old configuration dictionary (flat structure)
    """
    old_config = {}
    
    # Reverse the mapping
    for old_key, new_key_path in LEGACY_KEY_MAPPING.items():
        parts = new_key_path.split(".")
        value = new_config
        
        # Navigate to get the value
        try:
            for part in parts:
                value = value[part]
            old_config[old_key] = value
        except (KeyError, TypeError):
            # Key doesn't exist in new config, use default
            pass
    
    return old_config


def validate_migrated_config(config: Dict) -> Tuple[bool, list]:
    """
    Validate that a migrated configuration has the correct structure.
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for required sections
    required_sections = ["ui", "folders", "backup", "system", "game"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")
    
    # Check backup subsections
    if "backup" in config:
        required_backup_sections = ["characters", "cookies", "armor"]
        for subsection in required_backup_sections:
            if subsection not in config["backup"]:
                errors.append(f"Missing backup subsection: {subsection}")
    
    # Check critical keys
    critical_keys = [
        ("ui", "language"),
        ("ui", "theme"),
        ("folders", "characters"),
        ("system", "debug_mode")
    ]
    
    for section, key in critical_keys:
        if section in config and key not in config[section]:
            errors.append(f"Missing critical key: {section}.{key}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def get_migration_summary(old_config: Dict, new_config: Dict) -> str:
    """
    Generate a summary of the migration process.
    
    Args:
        old_config: Original configuration
        new_config: Migrated configuration
    
    Returns:
        Human-readable summary string
    """
    summary_lines = [
        "=" * 60,
        "CONFIG MIGRATION SUMMARY",
        "=" * 60,
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Old config keys: {len(old_config)}",
        f"New config sections: {len([k for k in new_config.keys() if isinstance(new_config[k], dict)])}",
        "",
        "Migrated sections:",
    ]
    
    # Count keys per section
    if "ui" in new_config:
        summary_lines.append(f"  - UI: {len(new_config['ui'])} keys")
    if "folders" in new_config:
        summary_lines.append(f"  - Folders: {len(new_config['folders'])} keys")
    if "backup" in new_config:
        backup_keys = sum(len(v) if isinstance(v, dict) else 1 for v in new_config['backup'].values())
        summary_lines.append(f"  - Backup: {backup_keys} keys (3 subsections)")
    if "system" in new_config:
        summary_lines.append(f"  - System: {len(new_config['system'])} keys")
    if "game" in new_config:
        summary_lines.append(f"  - Game: {len(new_config['game'])} keys")
    
    summary_lines.append("")
    summary_lines.append("Status: ✅ Migration successful")
    summary_lines.append("=" * 60)
    
    return "\n".join(summary_lines)
