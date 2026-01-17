"""
Model Gallery Builder - Prepare data for UI display.

This module constructs the data structures needed by the UI layer for
displaying the model gallery. It handles path resolution, pagination,
and thumbnail metadata assembly.

Domain-driven function naming: model_gallery_*
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Global cache for file index to avoid rescanning on every widget open
_FILE_CACHE: Optional[Dict[str, Path]] = None


def model_gallery_warmup_cache():
    """
    Pre-load file cache to avoid slow first gallery open.
    Call this once at application startup.
    """
    global _FILE_CACHE
    if _FILE_CACHE is None:
        logging.info("Warming up file cache...")
        img_base_path = Path(__file__).parent.parent / "Img" / "Models"
        _FILE_CACHE = {}
        extensions = {".jpg", ".jpeg", ".png", ".webp"}
        
        for file in img_base_path.rglob("*"):
            if file.is_file() and file.suffix.lower() in extensions:
                model_id = file.stem
                if model_id not in _FILE_CACHE:
                    _FILE_CACHE[model_id] = file
        
        logging.info(f"File cache warmed up: {len(_FILE_CACHE)} files indexed")


@dataclass
class ModelThumbnail:
    """Represents a single model thumbnail for gallery display."""

    model_id: str
    """Unique model identifier (e.g., '1002')"""

    type_name: str
    """Model type (e.g., 'armor', 'weapons')"""

    subtype_name: str
    """Model subtype (e.g., 'arms', 'feet', or '_' for no subtype)"""

    file_path: str
    """Relative path from Img/ directory (e.g., 'armor/arms/1002.jpg')"""

    full_path: Path
    """Full absolute path to the image file"""

    display_label: str
    """Label for display in UI (usually just the model ID)"""


def model_gallery_build_thumbnail_list(
    metadata: Dict,
    model_ids: List[str],
    img_base_path: Optional[Path] = None,
) -> List[ModelThumbnail]:
    """
    Build list of ModelThumbnail objects for gallery display.

    Each thumbnail includes path information needed for loading and displaying
    the image in the UI.

    Args:
        metadata: Output from model_gallery_load_metadata()
        model_ids: List of model IDs to build thumbnails for
        img_base_path: Base path to Img/Models/ directory. If None, auto-detects.

    Returns:
        List of ModelThumbnail objects ready for UI display

    Example:
        metadata = model_gallery_load_metadata()
        models = model_gallery_apply_filters(metadata, type_filter='armor', subtype_filter='arms')
        thumbnails = model_gallery_build_thumbnail_list(metadata, models)
        # Display thumbnails in gallery widget
    """
    if img_base_path is None:
        img_base_path = Path(__file__).parent.parent / "Img" / "Models"

    # Convert model_ids to set for O(1) lookup
    model_ids_set = set(model_ids)
    
    # Use global cache to avoid rescanning files
    global _FILE_CACHE
    if _FILE_CACHE is None:
        # Build cache only once
        logging.info("Building file cache from Img/Models/...")
        _FILE_CACHE = {}
        extensions = {".jpg", ".jpeg", ".png", ".webp"}
        
        for file in img_base_path.rglob("*"):
            if file.is_file() and file.suffix.lower() in extensions:
                model_id = file.stem
                if model_id not in _FILE_CACHE:  # Keep first occurrence
                    _FILE_CACHE[model_id] = file
        
        logging.info(f"File cache built: {len(_FILE_CACHE)} files indexed")
    else:
        logging.info(f"Using cached file index: {len(_FILE_CACHE)} files")
    
    file_cache = _FILE_CACHE

    thumbnails = []

    for type_name, subtypes in metadata.items():
        for subtype_name, type_models in subtypes.items():
            for model_id in type_models:
                if model_id not in model_ids_set:
                    continue

                # Look up file from cache
                file_path = file_cache.get(model_id)
                
                if file_path:
                    full_path = Path(file_path)
                    try:
                        rel_path = full_path.relative_to(img_base_path)
                        rel_str = str(rel_path).replace("\\", "/")
                    except ValueError:
                        # If relative_to fails, just use the file path as is
                        rel_str = str(file_path)
                    
                    thumbnail = ModelThumbnail(
                        model_id=model_id,
                        type_name=type_name,
                        subtype_name=subtype_name,
                        file_path=rel_str,
                        full_path=full_path,
                        display_label=model_id,
                    )
                    thumbnails.append(thumbnail)

    return thumbnails


def model_gallery_build_filter_options(metadata: Dict) -> Dict[str, List[str]]:
    """
    Build filter option lists for UI dropdowns/combo boxes.

    Returns structured data for populating filter controls.

    Args:
        metadata: Output from model_gallery_load_metadata()

    Returns:
        Dict with keys 'types' and 'subtypes_by_type':
        {
            'types': ['armor', 'weapons', ...],
            'subtypes_by_type': {
                'armor': ['arms', 'feet', 'hands', ...],
                'weapons': [],
                ...
            }
        }

    Example:
        options = model_gallery_build_filter_options(metadata)
        # Use options['types'] to populate type filter dropdown
        # Use options['subtypes_by_type']['armor'] for subtype dropdown
    """
    types = sorted(metadata.keys())

    subtypes_by_type = {}
    for type_name, subtypes in metadata.items():
        subtype_list = [s for s in subtypes.keys() if s != "_"]
        subtypes_by_type[type_name] = sorted(subtype_list)

    return {
        "types": types,
        "subtypes_by_type": subtypes_by_type,
    }


def model_gallery_build_statistics(metadata: Dict) -> Dict[str, object]:
    """
    Build summary statistics about the model gallery.

    Args:
        metadata: Output from model_gallery_load_metadata()

    Returns:
        Dict containing statistics:
        {
            'total_models': int,
            'types_count': int,
            'subtypes_count': int,
            'models_by_type': {'armor': 2500, ...},
            'models_by_subtype': {'armor': {'arms': 253, ...}, ...}
        }

    Example:
        stats = model_gallery_build_statistics(metadata)
        print(f"Total models: {stats['total_models']}")
        print(f"Armor arms: {stats['models_by_subtype']['armor']['arms']}")
    """
    total_models = 0
    models_by_type = {}
    models_by_subtype = {}

    for type_name, subtypes in metadata.items():
        type_total = 0
        models_by_subtype[type_name] = {}

        for subtype_name, models in subtypes.items():
            subtype_count = len(models)
            type_total += subtype_count

            if subtype_name != "_":
                models_by_subtype[type_name][subtype_name] = subtype_count

        models_by_type[type_name] = type_total
        total_models += type_total

    return {
        "total_models": total_models,
        "types_count": len(metadata),
        "subtypes_count": sum(
            len([s for s in subtypes.keys() if s != "_"])
            for subtypes in metadata.values()
        ),
        "models_by_type": models_by_type,
        "models_by_subtype": models_by_subtype,
    }


def _model_gallery_find_image_file(
    directory: Path, model_id: str
) -> Optional[str]:
    """
    Find image file for a model ID in a directory.

    Supports: .jpg, .jpeg, .png, .webp

    Args:
        directory: Directory to search in
        model_id: Model ID to find

    Returns:
        Relative path from Img/Models/ to the file, or None if not found

    Internal function (prefixed with _)
    """
    if not directory.exists():
        return None

    extensions = {".jpg", ".jpeg", ".png", ".webp"}

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            if file.stem == model_id:
                # Return the file path directly - caller will compute relative path
                return str(file).replace("\\", "/")

    return None
