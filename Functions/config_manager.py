import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'Configuration')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

class ConfigManager:
    """Manages loading and saving application settings from a JSON file."""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """Loads the configuration from config.json. Creates it with defaults if it doesn't exist."""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                "character_folder": None,
                "debug_mode": False,
                "log_folder": None,
                "language": "fr"
            }
            self.save_config()

    def save_config(self):
        """Saves the current configuration to config.json."""
        try:
            # Ensure the configuration directory exists
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except (IOError, OSError) as e:
            print(f"Critical Error: Could not save config file at {CONFIG_FILE}: {e}", file=sys.stderr)

    def get(self, key, default=None):
        """Gets a value from the configuration."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a value in the configuration and saves the file."""
        self.config[key] = value
        self.save_config()

# Global instance to be easily accessible throughout the application
config = ConfigManager()