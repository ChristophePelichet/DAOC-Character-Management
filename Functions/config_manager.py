import json
import os
import sys
from typing import Any, Optional
from .config_schema import DEFAULT_CONFIG, LEGACY_KEY_MAPPING, validate_value, get_default_value
from .config_migration import (
    detect_config_version,
    create_backup,
    migrate_v1_to_v2,
    validate_migrated_config,
    get_migration_summary
)

def get_config_dir():
    """
    Gets the configuration directory.
    Always returns 'Configuration' folder at the application base.
    Config folder is NOT configurable to avoid circular dependency issues.
    """
    from .path_manager import get_base_path
    return os.path.join(get_base_path(), 'Configuration')

class ConfigManager:
    """Manages loading and saving application settings from a JSON file."""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """Loads the configuration from config.json. Creates it with defaults if it doesn't exist."""
        from .path_manager import get_base_path
        
        # Config is always in Configuration folder next to executable
        default_config_dir = os.path.join(get_base_path(), 'Configuration')
        CONFIG_FILE = os.path.join(default_config_dir, 'config.json')

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Detect config version
            version = detect_config_version(loaded_config)
            print(f"[CONFIG] Detected config version: {version}")
            
            if version == "v1":
                # Migrate from v1 to v2
                print("[CONFIG] Migrating config from v1 to v2...")
                
                # Create backup before migration
                create_backup(CONFIG_FILE)
                
                # Perform migration
                self.config = migrate_v1_to_v2(loaded_config)
                
                # Validate migrated config
                is_valid, errors = validate_migrated_config(self.config)
                if not is_valid:
                    print(f"[CONFIG] Warning: Migration validation errors: {errors}")
                else:
                    print("[CONFIG] Migration validation: ✅ OK")
                
                # Print summary
                summary = get_migration_summary(loaded_config, self.config)
                print(summary)
                
                # Save migrated config
                self.save_config()
            else:
                # v2 config, use as-is
                self.config = loaded_config
                print("[CONFIG] Loaded v2 config successfully")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[CONFIG] Creating new config file (reason: {e})")
            # Use default v2 config
            self.config = json.loads(json.dumps(DEFAULT_CONFIG))  # Deep copy
            self.save_config()

    def save_config(self):
        """Saves the current configuration to config.json."""
        try:
            config_dir = get_config_dir()
            os.makedirs(config_dir, exist_ok=True)
            CONFIG_FILE = os.path.join(config_dir, 'config.json')
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except (IOError, OSError) as e:
            print(f"Critical Error: Could not save config file: {e}", file=sys.stderr)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a value from the configuration.
        Supports both dotted notation (v2: "ui.language") and legacy keys (v1: "language").
        
        Args:
            key: Configuration key (dotted or legacy)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        # Try dotted notation first (v2)
        if "." in key:
            parts = key.split(".")
            value = self.config
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    # Key not found, return default
                    return default
            
            return value
        
        # Check if it's a legacy key (v1)
        if key in LEGACY_KEY_MAPPING:
            new_key = LEGACY_KEY_MAPPING[key]
            return self.get(new_key, default)
        
        # Direct access (for unknown keys or root-level keys)
        return self.config.get(key, default)

    def set(self, key: str, value: Any, save: bool = True, validate: bool = False):
        """
        Sets a value in the configuration.
        Supports both dotted notation (v2: "ui.language") and legacy keys (v1: "language").
        
        Args:
            key: Configuration key (dotted or legacy)
            value: Value to set
            save: Whether to save config immediately (default: True)
            validate: Whether to validate value against schema (default: False)
        """
        # Validate if requested
        if validate:
            # Convert legacy key to new key for validation
            validate_key = LEGACY_KEY_MAPPING.get(key, key)
            if not validate_value(validate_key, value):
                print(f"[CONFIG] Warning: Invalid value for {validate_key}: {value}")
                return
        
        # Handle dotted notation (v2)
        if "." in key:
            parts = key.split(".")
            target = self.config
            
            # Navigate to parent, creating dicts as needed
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                elif not isinstance(target[part], dict):
                    # Can't navigate further, invalid path
                    print(f"[CONFIG] Error: Cannot set {key}, path conflict at {part}")
                    return
                target = target[part]
            
            # Set the final value
            target[parts[-1]] = value
        
        # Check if it's a legacy key (v1)
        elif key in LEGACY_KEY_MAPPING:
            new_key = LEGACY_KEY_MAPPING[key]
            self.set(new_key, value, save=False, validate=validate)
            # Save will be done below if save=True
        
        # Direct access (for unknown keys or root-level keys)
        else:
            self.config[key] = value
        
        # Save if requested
        if save:
            self.save_config()
    
    def get_section(self, section: str) -> dict:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., "ui", "folders", "backup")
        
        Returns:
            Section dictionary or empty dict if not found
        """
        return self.config.get(section, {})
    
    def get_current_season(self) -> str:
        """
        Get current season from game configuration.
        
        Returns:
            Current season identifier (e.g., "S3")
        """
        return self.get("game.default_season", "S3")
    
    def get_available_seasons(self) -> list:
        """
        Get list of available seasons from game configuration.
        
        Returns:
            List of season identifiers (e.g., ["S1", "S2", "S3"])
        """
        return self.get("game.seasons", ["S3"])
    
    def add_season(self, season: str, save: bool = True):
        """
        Add a new season to the available seasons list.
        
        Args:
            season: Season identifier to add (e.g., "S4")
            save: Whether to save config immediately
        """
        seasons = self.get_available_seasons()
        if season not in seasons:
            seasons.append(season)
            self.set("game.seasons", seasons, save=save)
    
    def set_current_season(self, season: str, save: bool = True):
        """
        Set the current season.
        
        Args:
            season: Season identifier (e.g., "S3")
            save: Whether to save config immediately
        """
        # Add to available seasons if not present
        self.add_season(season, save=False)
        # Set as current
        self.set("game.default_season", season, save=save)

class SingletonConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

# Global instance using the singleton pattern.
# This ensures that only one ConfigManager is ever created.
config = SingletonConfig()
