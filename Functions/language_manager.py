import json
import os
import logging

logger = logging.getLogger(__name__)

class LanguageManager:
    """
    Manages loading and accessing text strings for internationalization.
    """
    def __init__(self, lang_code='fr'):
        self.strings = {}
        self.load_language(lang_code)
    
    def set_language(self, lang_code):
        """Changes the active language and reloads the text strings."""
        self.load_language(lang_code)

    def load_language(self, lang_code):
        """Loads a JSON language file."""
        # Build the path to the 'Language' folder at the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        lang_file = os.path.join(project_root, 'Language', f'{lang_code}.json')

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load language file '{lang_file}'. {e}")
            # In case of an error, use an empty dictionary to avoid crashing
            self.strings = {}

    def get(self, key, **kwargs):
        """Retrieves a text string by its key and formats it if necessary."""
        return self.strings.get(key, key).format(**kwargs)

def get_available_languages():
    """Scans the 'Language' folder and returns a list of available language codes."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    lang_dir = os.path.join(project_root, 'Language')
    if not os.path.exists(lang_dir):
        return []
    
    languages = []
    for filename in os.listdir(lang_dir):
        if filename.endswith('.json'):
            languages.append(os.path.splitext(filename)[0])
    return sorted(languages)

# Global instance to be easily accessible throughout the application
lang = LanguageManager()