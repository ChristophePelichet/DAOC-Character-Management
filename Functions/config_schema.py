"""
Configuration Schema and Default Values
Version: v0.108
Author: Christophe Pelichet
Description: Defines the configuration structure, default values, and validation rules
"""

from typing import Any, Dict, List, Optional, Union

# Default configuration v2 (hierarchical structure)
DEFAULT_CONFIG = {
    "ui": {
        "language": "en",
        "theme": "purple",
        "font_scale": 1.0,
        "column_widths": {},
        "column_visibility": {},
        "tree_view_header_state": None,
        "manual_column_resize": True
    },
    "folders": {
        "characters": None,
        "logs": None,
        "armor": None,
        "cookies": None
    },
    "backup": {
        "characters": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        },
        "cookies": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        },
        "armor": {
            "auto_daily_backup": True,
            "path": None,
            "compress": True,
            "size_limit_mb": 10,
            "auto_delete_old": True,
            "last_date": None
        }
    },
    "system": {
        "debug_mode": False,
        "show_debug_window": False,
        "disable_disclaimer": False,
        "preferred_browser": "Chrome",
        "allow_browser_download": False,
        "debug": {
            "save_herald_html": False,
            "save_test_connection_html": False
        }
    },
    "game": {
        "servers": ["Eden"],
        "default_server": "Eden",
        "seasons": ["S3"],
        "default_season": "S3",
        "default_realm": None
    },
    "migrations": {
        "character_structure_done": False,
        "character_structure_date": None
    },
    "armory": {
        "use_personal_database": False,
        "personal_db_created": False,
        "personal_db_path": None,
        "auto_add_scraped_items": True,
        "last_internal_db_version": "1.0"
    }
}

# Validation schema
VALIDATION_SCHEMA = {
    "ui": {
        "language": {
            "type": str,
            "allowed": ["fr", "en", "de"],
            "default": "en"
        },
        "theme": {
            "type": str,
            "allowed": ["default", "dark", "light", "purple"],
            "default": "dark"
        },
        "font_scale": {
            "type": (int, float),
            "min": 0.5,
            "max": 2.0,
            "default": 1.0
        },
        "column_widths": {
            "type": dict,
            "default": {}
        },
        "column_visibility": {
            "type": dict,
            "default": {}
        },
        "tree_view_header_state": {
            "type": (str, type(None)),
            "default": None
        },
        "manual_column_resize": {
            "type": bool,
            "default": True
        }
    },
    "folders": {
        "characters": {
            "type": (str, type(None)),
            "default": None
        },
        "logs": {
            "type": (str, type(None)),
            "default": None
        },
        "armor": {
            "type": (str, type(None)),
            "default": None
        },
        "cookies": {
            "type": (str, type(None)),
            "default": None
        }
    },
    "backup": {
        "characters": {
            "auto_daily_backup": {"type": bool, "default": True},
            "path": {"type": (str, type(None)), "default": None},
            "compress": {"type": bool, "default": True},
            "size_limit_mb": {"type": int, "min": 1, "max": 1000, "default": 20},
            "auto_delete_old": {"type": bool, "default": True},
            "last_date": {"type": (str, type(None)), "default": None}
        },
        "cookies": {
            "auto_daily_backup": {"type": bool, "default": True},
            "path": {"type": (str, type(None)), "default": None},
            "compress": {"type": bool, "default": True},
            "size_limit_mb": {"type": int, "min": 1, "max": 1000, "default": 10},
            "auto_delete_old": {"type": bool, "default": True},
            "last_date": {"type": (str, type(None)), "default": None}
        },
        "armor": {
            "auto_daily_backup": {"type": bool, "default": True},
            "path": {"type": (str, type(None)), "default": None},
            "compress": {"type": bool, "default": True},
            "size_limit_mb": {"type": int, "min": 1, "max": 1000, "default": 10},
            "auto_delete_old": {"type": bool, "default": True},
            "last_date": {"type": (str, type(None)), "default": None}
        }
    },
    "system": {
        "debug_mode": {
            "type": bool,
            "default": False
        },
        "show_debug_window": {
            "type": bool,
            "default": False
        },
        "disable_disclaimer": {
            "type": bool,
            "default": False
        },
        "preferred_browser": {
            "type": (str, type(None)),
            "allowed": ["Chrome", "Firefox", "Edge", None],
            "default": "Chrome"
        },
        "allow_browser_download": {
            "type": bool,
            "default": False
        }
    },
    "game": {
        "servers": {
            "type": list,
            "default": ["Eden"]
        },
        "default_server": {
            "type": str,
            "default": "Eden"
        },
        "seasons": {
            "type": list,
            "default": ["S3"]
        },
        "default_season": {
            "type": str,
            "default": "S3"
        },
        "default_realm": {
            "type": (str, type(None)),
            "allowed": ["Albion", "Midgard", "Hibernia", None],
            "default": None
        }
    }
}

# Legacy key mapping (v1 → v2)
LEGACY_KEY_MAPPING = {
    # UI keys
    "language": "ui.language",
    "theme": "ui.theme",
    "font_scale": "ui.font_scale",
    "column_widths": "ui.column_widths",
    "column_visibility": "ui.column_visibility",
    "tree_view_header_state": "ui.tree_view_header_state",
    "manual_column_resize": "ui.manual_column_resize",
    
    # Folders keys
    "character_folder": "folders.characters",
    "log_folder": "folders.logs",
    "armor_folder": "folders.armor",
    "cookies_folder": "folders.cookies",
    
    # Backup - Characters
    "backup_enabled": "backup.characters.auto_daily_backup",
    "backup_path": "backup.characters.path",
    "backup_compress": "backup.characters.compress",
    "backup_size_limit_mb": "backup.characters.size_limit_mb",
    "backup_auto_delete_old": "backup.characters.auto_delete_old",
    "backup_last_date": "backup.characters.last_date",
    
    # Backup - Cookies
    "cookies_backup_enabled": "backup.cookies.auto_daily_backup",
    "cookies_backup_path": "backup.cookies.path",
    "cookies_backup_compress": "backup.cookies.compress",
    "cookies_backup_size_limit_mb": "backup.cookies.size_limit_mb",
    "cookies_backup_auto_delete_old": "backup.cookies.auto_delete_old",
    "cookies_backup_last_date": "backup.cookies.last_date",
    
    # Backup - Armor
    "armor_backup_enabled": "backup.armor.auto_daily_backup",
    "armor_backup_path": "backup.armor.path",
    "armor_backup_compress": "backup.armor.compress",
    "armor_backup_size_limit_mb": "backup.armor.size_limit_mb",
    "armor_backup_auto_delete_old": "backup.armor.auto_delete_old",
    "armor_backup_last_date": "backup.armor.last_date",
    
    # System keys
    "debug_mode": "system.debug_mode",
    "show_debug_window": "system.show_debug_window",
    "disable_disclaimer": "system.disable_disclaimer",
    "preferred_browser": "system.preferred_browser",
    "allow_browser_download": "system.allow_browser_download",
    
    # Game keys
    "servers": "game.servers",
    "default_server": "game.default_server",
    "seasons": "game.seasons",
    "default_season": "game.default_season",
    "default_realm": "game.default_realm"
}


def validate_value(key_path: str, value: Any) -> bool:
    """
    Validate a configuration value against the schema.
    
    Args:
        key_path: Dotted path to the key (e.g., "ui.language")
        value: Value to validate
    
    Returns:
        True if valid, False otherwise
    """
    parts = key_path.split(".")
    schema = VALIDATION_SCHEMA
    
    # Navigate to the schema entry
    for part in parts[:-1]:
        if part not in schema:
            return False
        schema = schema[part]
    
    # Get the final key schema
    key = parts[-1]
    if key not in schema:
        return False
    
    key_schema = schema[key]
    
    # Type validation
    expected_type = key_schema.get("type")
    if expected_type:
        if not isinstance(value, expected_type):
            return False
    
    # Allowed values validation
    allowed = key_schema.get("allowed")
    if allowed is not None and value not in allowed:
        return False
    
    # Min/max validation for numbers
    if "min" in key_schema and value < key_schema["min"]:
        return False
    if "max" in key_schema and value > key_schema["max"]:
        return False
    
    return True


def get_default_value(key_path: str) -> Any:
    """
    Get the default value for a configuration key.
    
    Args:
        key_path: Dotted path to the key (e.g., "ui.language")
    
    Returns:
        Default value or None if not found
    """
    parts = key_path.split(".")
    config = DEFAULT_CONFIG
    
    for part in parts:
        if isinstance(config, dict) and part in config:
            config = config[part]
        else:
            return None
    
    return config


def get_legacy_key(new_key: str) -> Optional[str]:
    """
    Get the legacy (v1) key name from a new (v2) key path.
    
    Args:
        new_key: New dotted key path (e.g., "ui.language")
    
    Returns:
        Legacy key name or None if not found
    """
    for legacy, new in LEGACY_KEY_MAPPING.items():
        if new == new_key:
            return legacy
    return None


def get_new_key(legacy_key: str) -> Optional[str]:
    """
    Get the new (v2) key path from a legacy (v1) key name.
    
    Args:
        legacy_key: Legacy key name (e.g., "language")
    
    Returns:
        New dotted key path or None if not found
    """
    return LEGACY_KEY_MAPPING.get(legacy_key)
