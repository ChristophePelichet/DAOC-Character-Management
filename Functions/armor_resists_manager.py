"""
Armor Resistances Manager - Handles loading and formatting armor resistance data.
"""

import json
from pathlib import Path
from Functions.path_manager import get_resource_path
from Functions.debug_logging_manager import get_logger, LOGGER_CHARACTER

logger = get_logger(LOGGER_CHARACTER)


def armor_resists_load_data():
    """
    Load armor resistance data from JSON file.
    
    Returns:
        dict: Armor resistance data with tables and metadata, or empty dict on error.
    """
    try:
        data_path = Path(get_resource_path("Data/armor_resists.json"))
        
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
        
        # Map table keys to realm names (corrected mapping)
        table_mapping = {
            "table_1": "albion",
            "table_2": "hibernia",
            "table_3": "midgard"
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
    
    return str(value).strip()


def armor_resists_get_cell_color(value):
    """
    Determine the color for a cell based on its value.
    
    Args:
        value (str): The raw value from the table (e.g., "10%", "-5%", "0%").
    
    Returns:
        tuple: (r, g, b) color tuple or None for default color.
    """
    if not value:
        return None
    
    value_str = str(value).strip()
    
    # Parse percentage value
    try:
        # Extract numeric part
        numeric_str = value_str.rstrip('%')
        numeric_val = int(numeric_str)
        
        # Green for positive (Resistant)
        if numeric_val > 0:
            return (76, 175, 80)  # Green
        # Red for negative (Vulnerable)
        elif numeric_val < 0:
            return (244, 67, 54)  # Red
        # Orange for zero (Neutral)
        else:
            return (255, 152, 0)  # Orange
    except (ValueError, AttributeError):
        return None

def armor_resists_filter_armor_types_only(realm_data):
    """
    Filter realm data to show only armor types without class duplicates.
    
    Args:
        realm_data (dict): The realm data dictionary with headers and data.
    
    Returns:
        dict: Filtered realm data with Class column removed and one row per armor type.
    """
    if not realm_data:
        return {}
    
    headers = realm_data.get("headers", [])
    rows = realm_data.get("data", [])
    
    # Create new headers without Class column
    filtered_headers = [h for h in headers if h.get("name") != "Class"]
    
    # Track seen armor types to keep only first occurrence
    seen_armor_types = set()
    filtered_rows = []
    
    for row in rows:
        armor_type = row.get("Armor Type", "")
        
        # Skip if we've already seen this armor type
        if armor_type in seen_armor_types:
            continue
        
        seen_armor_types.add(armor_type)
        
        # Create new row without Class data
        filtered_row = {}
        for header in filtered_headers:
            header_name = header.get("name", "")
            filtered_row[header_name] = row.get(header_name, "")
        
        # Keep localized versions of Armor Type if present
        for key in ["Armor Type_fr", "Armor Type_de"]:
            if key in row:
                filtered_row[key] = row[key]
        
        filtered_rows.append(filtered_row)
    
    return {
        "title": realm_data.get("title", ""),
        "headers": filtered_headers,
        "data": filtered_rows
    }