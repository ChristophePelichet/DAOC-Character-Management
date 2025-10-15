import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.json')

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
                "log_folder": None
            }
            self.save_config()

    def save_config(self):
        """Saves the current configuration to config.json."""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Gets a value from the configuration."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a value in the configuration and saves the file."""
        self.config[key] = value
        self.save_config()

# Global instance to be easily accessible throughout the application
config = ConfigManager()