import json
import os
import sys

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
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                "character_folder": None,
                "debug_mode": False,
                "log_folder": None,
                "language": "fr",
                "servers": ["Eden"],
                "default_server": "Eden",
                "seasons": ["S3"],
                "default_season": "S3",
                "tree_view_header_state": None,
                "manual_column_resize": True,
                "backup_enabled": True,
                "backup_path": None,
                "backup_size_limit_mb": 20,
                "backup_compress": True,
                "backup_last_date": None,
                "theme": "default",
                "font_scale": 1.0
            }
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

    def get(self, key, default=None):
        """Gets a value from the configuration."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a value in the configuration and saves the file."""
        self.config[key] = value
        self.save_config()

class SingletonConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

# Global instance using the singleton pattern.
# This ensures that only one ConfigManager is ever created.
config = SingletonConfig()