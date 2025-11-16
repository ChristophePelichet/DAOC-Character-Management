import json
import os
import logging
from .config_manager import config
from .path_manager import get_resource_path

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
        lang_dir = get_resource_path('Language')
        lang_file = os.path.join(lang_dir, f'{lang_code}.json')

        logger.debug(f"Attempting to load language file from: {lang_file}")

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
    """
    Scans the 'Language' folder and returns a dictionary mapping language codes to full names.
    Sorts languages with a specific order: 'fr', 'en', then alphabetically.
    """
    lang_dir = get_resource_path('Language')
    if not os.path.exists(lang_dir):
        return {}
    
    languages = {}
    for filename in os.listdir(lang_dir):
        if filename.endswith('.json'):
            code = os.path.splitext(filename)[0]
            try:
                with open(os.path.join(lang_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    languages[code] = data.get("language_name", code)
            except (json.JSONDecodeError, IOError):
                continue
    
    # Custom sort order: 'fr', then 'en', then alphabetically
    all_codes = list(languages.keys())
    final_sorted_codes = []

    if 'fr' in all_codes:
        final_sorted_codes.append('fr')
        all_codes.remove('fr')
    
    if 'en' in all_codes:
        final_sorted_codes.append('en')
        all_codes.remove('en')
        
    final_sorted_codes.extend(sorted(all_codes))
    return {code: languages[code] for code in final_sorted_codes}

# Global instance to be easily accessible throughout the application
lang = LanguageManager(config.get("ui.language", "fr"))