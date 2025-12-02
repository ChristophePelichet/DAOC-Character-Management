import json
import os
import logging
from .config_manager import config
from .path_manager import get_resource_path
from .language_schema import LANGUAGE_LEGACY_MAPPING, is_v2_structure
from .language_migration import (
    detect_language_version,
    create_backup,
    migrate_v1_to_v2,
    validate_migrated_language,
    get_migration_summary
)

logger = logging.getLogger(__name__)


class LanguageManager:
    """
    Manages loading and accessing text strings for internationalization.
    Supports both v1 (flat) and v2 (hierarchical) language file structures.
    Automatically migrates v1 to v2 on first load.
    """
    def __init__(self, lang_code='fr'):
        self.strings = {}
        self.legacy_mapping = LANGUAGE_LEGACY_MAPPING
        self.current_language = lang_code  # Track current language
        self.load_language(lang_code)
    
    def set_language(self, lang_code):
        """Changes the active language and reloads the text strings."""
        self.current_language = lang_code  # Update current language
        self.load_language(lang_code)

    def load_language(self, lang_code):
        """
        Loads a JSON language file with automatic v1→v2 migration.
        
        Workflow:
        1. Load language file
        2. Detect version (v1/v2)
        3. If v1: backup, migrate, validate, save
        4. If v2: load directly
        """
        lang_dir = get_resource_path('Language')
        lang_file = os.path.join(lang_dir, f'{lang_code}.json')

        logger.debug(f"Attempting to load language file from: {lang_file}")

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            # Detect version
            version = detect_language_version(loaded_data)
            logger.info(f"[LANGUAGE] Detected language file version: {version} ({lang_code}.json)")
            
            if version == "v1":
                # Migrate from v1 to v2
                logger.info(f"[LANGUAGE] Migrating {lang_code}.json from v1 to v2...")
                
                # Create backup
                create_backup(lang_file)
                
                # Perform migration
                self.strings = migrate_v1_to_v2(loaded_data)
                
                # Validate
                is_valid, errors = validate_migrated_language(self.strings)
                if not is_valid:
                    logger.warning(f"[LANGUAGE] Migration validation warnings: {errors}")
                else:
                    logger.info("[LANGUAGE] Migration validation: ✅ OK")
                
                # Print summary
                summary = get_migration_summary(loaded_data, self.strings)
                logger.info(summary)
                
                # Save migrated version
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(self.strings, f, ensure_ascii=False, indent=4)
                logger.info(f"[LANGUAGE] Saved v2 format to: {lang_file}")
            else:
                # v2 format, use as-is
                self.strings = loaded_data
                logger.info(f"[LANGUAGE] Loaded v2 language file successfully: {lang_code}.json")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load language file '{lang_file}'. {e}")
            # In case of an error, use an empty dictionary to avoid crashing
            self.strings = {}

    def get(self, key, default=None, **kwargs):
        """
        Retrieves a text string by its key and formats it if necessary.
        Supports both v1 (flat) and v2 (hierarchical) keys with automatic redirection.
        
        Examples:
            lang.get("window.main_title")           # v2 (recommended)
            lang.get("window_title")                # v1 (legacy, auto-redirected)
            lang.get("dialogs.new_character.title") # v2 nested
            lang.get("nonexistent", "fallback")     # with default
            lang.get("char_saved_success", name="John")  # with formatting
        
        Args:
            key: v1 or v2 key to lookup
            default: Default value if key not found (defaults to key itself)
            **kwargs: Formatting arguments for .format()
        
        Returns:
            Translated string, formatted if kwargs provided
        """
        # Try v2 dotted notation first
        if "." in key:
            value = self._get_nested(key)
        else:
            # Try v1 key, redirect if in legacy mapping
            if key in self.legacy_mapping:
                v2_key = self.legacy_mapping[key]
                value = self._get_nested(v2_key)
            else:
                # Fallback to direct key (v1 compatibility or v2 single-level key)
                value = self.strings.get(key)
        
        # If not found, use default
        if value is None:
            value = default if default is not None else key
        
        # Apply formatting if kwargs provided
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, AttributeError, ValueError) as e:
                logger.warning(f"[LANGUAGE] Format error for key '{key}': {e}")
                return value
        
        return value
    
    def _get_nested(self, dotted_key: str):
        """
        Navigate hierarchical structure using dotted notation.
        
        Args:
            dotted_key: Key in dotted notation (e.g., "window.main_title")
        
        Returns:
            Value at nested location or None if not found
        """
        keys = dotted_key.split(".")
        value = self.strings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value

def get_available_languages():
    """
    Scans the 'Language' folder and returns a dictionary mapping language codes to full names.
    Sorts languages with a specific order: 'fr', 'en', then alphabetically.
    Supports both v1 (flat) and v2 (hierarchical) language file structures.
    """
    lang_dir = get_resource_path('Language')
    if not os.path.exists(lang_dir):
        return {}
    
    languages = {}
    for filename in os.listdir(lang_dir):
        if filename.endswith('.json') and not filename.endswith('.backup'):
            code = os.path.splitext(filename)[0]
            try:
                with open(os.path.join(lang_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Try v2 format first (app.language_name)
                    if "app" in data and isinstance(data["app"], dict):
                        lang_name = data["app"].get("language_name", code)
                    else:
                        # Fall back to v1 format (language_name at root)
                        lang_name = data.get("language_name", code)
                    
                    languages[code] = lang_name
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