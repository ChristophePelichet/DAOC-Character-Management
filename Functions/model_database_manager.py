"""
Model Database Manager - Index and load model data from Img/Models/ directory.

This module handles the discovery and indexing of all model images available
in the Img/Models/ folder structure. It builds a metadata cache for efficient filtering
and gallery display.

Domain-driven function naming: model_gallery_*
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


def model_gallery_load_item_slots() -> Dict[str, List[str]]:
    """
    Load DOL models database and create mapping of model IDs to item slots.
    
    Uses dol_models_database.json which contains all 3444 models scraped from
    the Eden model gallery, organized by category (armor/feet, armor/hands, etc.)
    
    Returns:
        Dict mapping {slot: [model_ids]} for all items
        Example: {'Feet': ['40', '45', ...], 'Hands': ['34', '39', ...]}
    """
    db_file = Path(__file__).parent.parent / "Data" / "dol_models_database.json"
    
    if not db_file.exists():
        logging.warning(f"DOL models database not found: {db_file}")
        return {}
    
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Build mapping of slot -> model IDs
        # Each item_id maps to a slot, and we use item_id as the model_id for the gallery
        slot_mapping: Dict[str, List[str]] = {}
        
        for item_id, item_data in data.items():
            slot = item_data.get("slot")
            
            if slot:
                if slot not in slot_mapping:
                    slot_mapping[slot] = []
                # Use item_id directly as the model_id
                slot_mapping[slot].append(item_id)
        
        # Sort numeric IDs numerically
        result = {}
        for slot, model_ids in slot_mapping.items():
            numeric_ids = sorted([mid for mid in model_ids if mid.isdigit()], key=int)
            result[slot] = numeric_ids
        
        return result
    
    except Exception as e:
        logging.error(f"Error loading DOL models database: {e}")
        return {}


def model_gallery_load_metadata() -> Dict[str, List[str]]:
    """
    Load and index all model images from Img/ directory structure.

    Returns a hierarchical dictionary organized as:
    {
        'type': {
            'subtype': ['model_id1', 'model_id2', ...],
            ...
        },
        ...
    }

    Supported types: armor, weapons, mobs, deco_and_etc, misc_models, etc.

    Returns:
        Dict mapping types -> subtypes -> model IDs list

    Example:
        metadata = model_gallery_load_metadata()
        # {
        #     'armor': {
        #         'arms': ['1002', '1189', '1194', ...],
        #         'feet': ['1001', '1190', ...],
        #         'torso': [...]
        #     },
        #     'weapons': {
        #         '1', '2', '3', ... (no subtype for weapons)
        #     }
    """
    img_dir = Path(__file__).parent.parent / "Img" / "Models"

    logging.info(f"Loading metadata from: {img_dir}")
    if not img_dir.exists():
        logging.error(f"Models directory not found: {img_dir}")
        return {}

    metadata: Dict[str, Dict[str, List[str]]] = {}
    
    # Currently load only 'items' type for performance (3444 items vs 4814+ total)
    types_to_load = ["items"]

    # Iterate through all directories in Img/Models/
    for type_dir in img_dir.iterdir():
        if not type_dir.is_dir():
            continue

        type_name = type_dir.name.lower()
        
        # Skip types not in our whitelist
        if type_name not in types_to_load:
            continue
            
        logging.info(f"Found type directory: {type_name}")

        # Special handling for items: use database slots instead of subdirectories
        if type_name == "items":
            slot_mapping = model_gallery_load_item_slots()
            metadata[type_name] = slot_mapping
            logging.info(f"  Items categorized by slot: {len(slot_mapping)} slots found")
            for slot, model_ids in slot_mapping.items():
                logging.info(f"    {slot}: {len(model_ids)} models")
        else:
            # Check if this type has subdirectories (e.g., armor/arms, armor/feet)
            subdirs = [d for d in type_dir.iterdir() if d.is_dir()]

            if subdirs:
                # Type has subtypes (e.g., armor -> arms, feet, hands, etc.)
                metadata[type_name] = {}

                for subtype_dir in subdirs:
                    subtype_name = subtype_dir.name.lower()
                    model_ids = model_gallery_extract_ids_from_dir(subtype_dir)
                    # Sort numeric IDs, filter out non-numeric names
                    numeric_ids = [mid for mid in model_ids if mid.isdigit()]
                    metadata[type_name][subtype_name] = sorted(numeric_ids, key=int)
                    logging.info(f"  Subtype {subtype_name}: {len(numeric_ids)} models")

            else:
                # Type has no subtypes (e.g., weapons -> just images)
                model_ids = model_gallery_extract_ids_from_dir(type_dir)
                # Sort numeric IDs, filter out non-numeric names
                numeric_ids = [mid for mid in model_ids if mid.isdigit()]
                metadata[type_name] = {"_": sorted(numeric_ids, key=int)}
                logging.info(f"  No subtypes: {len(numeric_ids)} models")

    logging.info(f"Metadata loading complete: {len(metadata)} types found")
    
    return metadata


def model_gallery_apply_visibility_filters(metadata: Dict) -> Dict:
    """
    Apply visibility filters from configuration to metadata.

    Removes slots that are not in the visible_slots list from the configuration.
    This allows users to hide certain model categories from the gallery view.

    Args:
        metadata: Output from model_gallery_load_metadata()

    Returns:
        Filtered metadata containing only visible slots

    Example:
        metadata = model_gallery_load_metadata()
        filtered = model_gallery_apply_visibility_filters(metadata)
        # Now only contains slots that are enabled in settings
    """
    try:
        from Functions.config_manager import config

        visible_slots = config.get(
            "models_gallery.visible_slots",
            [
                "Weapons",
                "Arms",
                "Hands",
                "Feet",
                "Legs",
                "Torso",
                "Head",
                "Shields",
                "Cloaks",
                "Quiver",
                "Misc",
                "Siege",
                "Boats",
                "Tents",
                "Deco",
            ],
        )

        if not metadata or "items" not in metadata:
            return metadata

        # Filter items to only include visible slots
        filtered_items = {
            slot_name: model_ids
            for slot_name, model_ids in metadata["items"].items()
            if slot_name in visible_slots
        }

        filtered_metadata = {"items": filtered_items}

        logging.info(
            f"Applied visibility filters: {len(filtered_items)} visible slots out of {len(metadata['items'])}"
        )

        return filtered_metadata

    except Exception as e:
        logging.error(f"Error applying visibility filters: {e}")
        return metadata


def model_gallery_extract_ids_from_dir(directory: Path) -> List[str]:
    """
    Extract model IDs from image filenames in a directory.

    Supports: *.jpg, *.jpeg, *.png, *.webp

    Args:
        directory: Path to directory containing model images

    Returns:
        List of model IDs (filenames without extension, as strings)
    """
    if not directory.exists():
        return []

    model_ids = []
    extensions = {".jpg", ".jpeg", ".png", ".webp"}

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            # Model ID is the filename without extension
            model_id = file.stem
            model_ids.append(model_id)

    return model_ids


def model_gallery_get_type_count(metadata: Dict) -> Dict[str, int]:
    """
    Get count of models per type.

    Args:
        metadata: Output from model_gallery_load_metadata()

    Returns:
        Dict mapping type names to total model count

    Example:
        counts = model_gallery_get_type_count(metadata)
        # {'armor': 2500, 'weapons': 968, 'mobs': 1000, ...}
    """
    counts = {}

    for type_name, subtypes in metadata.items():
        total = 0
        for subtype_models in subtypes.values():
            total += len(subtype_models)
        counts[type_name] = total

    return counts


def model_gallery_get_subtype_count(
    metadata: Dict, type_name: str
) -> Dict[str, int]:
    """
    Get count of models per subtype within a type.

    Args:
        metadata: Output from model_gallery_load_metadata()
        type_name: Type to query (e.g., 'armor')

    Returns:
        Dict mapping subtype names to model count

    Example:
        counts = model_gallery_get_subtype_count(metadata, 'armor')
        # {'arms': 253, 'feet': 285, 'hands': 256, 'legs': 250, ...}
    """
    if type_name not in metadata:
        return {}

    counts = {}
    for subtype_name, models in metadata[type_name].items():
        counts[subtype_name] = len(models)

    return counts


def model_gallery_get_available_types(metadata: Dict) -> List[str]:
    """
    Get list of all available model types.

    Args:
        metadata: Output from model_gallery_load_metadata()

    Returns:
        Sorted list of type names

    Example:
        types = model_gallery_get_available_types(metadata)
        # ['armor', 'deco_and_etc', 'misc_models', 'mobs', 'weapons']
    """
    return sorted(metadata.keys())


def model_gallery_get_available_subtypes(
    metadata: Dict, type_name: str
) -> List[str]:
    """
    Get list of subtypes for a specific type.

    Args:
        metadata: Output from model_gallery_load_metadata()
        type_name: Type to query (e.g., 'armor')

    Returns:
        Sorted list of subtype names (or ["_"] for single-level types)

    Example:
        subtypes = model_gallery_get_available_subtypes(metadata, 'armor')
        # ['arms', 'cloaks', 'feet', 'hands', 'legs', ...]
    """
    if type_name not in metadata:
        return []

    return sorted(metadata[type_name].keys())


def model_gallery_get_models_by_type_subtype(
    metadata: Dict, type_name: str, subtype_name: Optional[str] = None
) -> List[str]:
    """
    Get list of model IDs for a specific type/subtype combination.

    Args:
        metadata: Output from model_gallery_load_metadata()
        type_name: Type to query (e.g., 'armor')
        subtype_name: Subtype to query (e.g., 'arms'). If None, returns all for type.

    Returns:
        Sorted list of model IDs

    Example:
        models = model_gallery_get_models_by_type_subtype(metadata, 'armor', 'arms')
        # ['1002', '1189', '1194', '1248', ...]
    """
    if type_name not in metadata:
        return []

    if subtype_name is None:
        # Return all models for this type
        all_models = []
        for models in metadata[type_name].values():
            all_models.extend(models)
        return sorted(all_models, key=int)

    if subtype_name not in metadata[type_name]:
        return []

    return metadata[type_name][subtype_name]


def model_gallery_find_model_path(
    metadata: Dict, model_id: str
) -> Optional[Tuple[str, str, str]]:
    """
    Find the path information for a specific model ID.

    Args:
        metadata: Output from model_gallery_load_metadata()
        model_id: Model ID to find (e.g., '1002')

    Returns:
        Tuple of (type, subtype, full_path) or None if not found
        full_path is relative to Img/ directory

    Example:
        result = model_gallery_find_model_path(metadata, '1002')
        # ('armor', 'arms', 'armor/arms/1002.jpg')
    """
    img_dir = Path(__file__).parent.parent / "Img"

    for type_name, subtypes in metadata.items():
        for subtype_name, models in subtypes.items():
            if model_id in models:
                # Find the actual file (could be .jpg, .png, .webp)
                subtype_dir = img_dir / type_name / subtype_name
                if subtype_dir.exists():
                    for file in subtype_dir.iterdir():
                        if file.stem == model_id:
                            relative_path = f"{type_name}/{subtype_name}/{file.name}"
                            return (type_name, subtype_name, relative_path)

    return None
