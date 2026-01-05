"""
Armor Resistances Manager - Handles loading and formatting armor resistance data.
"""

import json
from pathlib import Path
from Functions.path_manager import get_base_path
from Functions.debug_logging_manager import get_logger, LOGGER_CHARACTER

logger = get_logger(LOGGER_CHARACTER)


def armor_resists_load_data():
    """
    Load armor resistance data from JSON file.
    
    Returns:
        dict: Armor resistance data with tables and metadata, or empty dict on error.
    """
    try:
        data_path = Path(get_base_path()) / "Data" / "armor_resists.json"
        
        if not data_path.exists():
            logger.error(f"Armor resists data file not found: {data_path}")
            return {}
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug("Armor resists data loaded successfully")
        return data
    
    except Exception as e:
        logger.error(f"Error loading armor resists data: {e}")
        return {}


def armor_resists_get_realms_data(data):
    """
    Extract realm tables from loaded armor resistance data.
    
    Args:
        data (dict): Loaded armor resistance data.
    
    Returns:
        dict: Dictionary with realm names as keys and table data as values.
    """
    try:
        tables = data.get("tables", {})
        realms = {}
        
        # Map table keys to realm names
        table_mapping = {
            "table_1": "albion",
            "table_2": "midgard",
            "table_3": "hibernia"
        }
        
        for table_key, realm_name in table_mapping.items():
            if table_key in tables:
                realms[realm_name] = tables[table_key]
        
        return realms
    
    except Exception as e:
        logger.error(f"Error extracting realms data: {e}")
        return {}


def armor_resists_format_cell_value(value):
    """
    Format a cell value from the armor resistance table.
    
    Args:
        value (str): The raw value from the table (e.g., "Resistant", "Vulnerable", "Neutral").
    
    Returns:
        str: Formatted value ready for display.
    """
    if not value:
        return "—"
    
    value = str(value).strip()
    
    # Map display names
    if value == "Resistant":
        return "✓"
    elif value == "Vulnerable":
        return "✗"
    elif value == "Neutral":
        return "◯"
    else:
        return value


def armor_resists_get_cell_color(value):
    """
    Determine the color for a cell based on its value.
    
    Args:
        value (str): The raw value from the table.
    
    Returns:
        tuple: (r, g, b) color tuple or None for default color.
    """
    if not value:
        return None
    
    value = str(value).strip()
    
    # Green for Resistant
    if value == "Resistant":
        return (76, 175, 80)  # Green
    # Red for Vulnerable
    elif value == "Vulnerable":
        return (244, 67, 54)  # Red
    # Orange for Neutral
    elif value == "Neutral":
        return (255, 152, 0)  # Orange
    
    return None
