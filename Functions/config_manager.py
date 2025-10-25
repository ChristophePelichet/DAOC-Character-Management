import json
import os
import sys

def get_config_dir():
    """
    Gets the configuration directory. It checks the config itself for a custom path,
    otherwise defaults to a 'Configuration' folder at the application base.
    This function is defined outside the class to be accessible from the UI.
    """
    from .path_manager import get_base_path
    # config.get() is safe here because it's a global instance
    return config.get("config_folder") or os.path.join(get_base_path(), 'Configuration')

class ConfigManager:
    """Manages loading and saving application settings from a JSON file."""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """Loads the configuration from config.json. Creates it with defaults if it doesn't exist."""
        # To find the config file, we must first determine its directory.
        # This is a bit of a chicken-and-egg problem. We assume it's in the default location first.
        from .path_manager import get_base_path
        default_config_dir = os.path.join(get_base_path(), 'Configuration')
        CONFIG_FILE = os.path.join(default_config_dir, 'config.json')

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                # If a custom path is defined, re-check from that path. This handles moved configs.
                custom_config_dir = self.config.get("config_folder")
                if custom_config_dir and custom_config_dir != default_config_dir:
                    CONFIG_FILE = os.path.join(custom_config_dir, 'config.json')
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                "config_folder": default_config_dir, # Store its own path
                "character_folder": None,
                "debug_mode": False,
                "log_folder": None,
                "language": "fr",
                "servers": ["Eden", "Blackthorn"],
                "default_server": "Eden",
                "seasons": ["S1", "S2", "S3"],
                "default_season": "S1",
                "tree_view_header_state": None
            }
            self.save_config()

    def save_config(self):
        """Saves the current configuration to config.json."""
        try:
            config_dir = self.get("config_folder") or get_config_dir()
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