"""
Model Gallery Filter - Apply filtering logic to model gallery data.

This module handles all filtering operations for the model gallery view.
It filters models based on type, subtype, and search criteria.

Domain-driven function naming: model_gallery_*
"""

from typing import Dict, List, Optional
from Functions.model_database_manager import (
    model_gallery_get_models_by_type_subtype,
)


def model_gallery_apply_filters(
    metadata: Dict,
    type_filter: Optional[str] = None,
    subtype_filter: Optional[str] = None,
    search_query: Optional[str] = None,
) -> List[str]:
    """
    Apply filters to model metadata and return matching model IDs.

    Supports filtering by:
    - Type (e.g., 'items')
    - Subtype (e.g., 'bow', 'helm' for items)
    - Search query (by model ID, partial match)

    Args:
        metadata: Output from model_gallery_load_metadata()
        type_filter: Type to filter by (e.g., 'items'). None = all types
        subtype_filter: Subtype to filter by (e.g., 'bow'). Ignored if type_filter is None
        search_query: Search string to match against model IDs. None = no search filtering

    Returns:
        Sorted list of model IDs matching all applied filters

    Example:
        # Get all weapon bow models
        models = model_gallery_apply_filters(metadata, type_filter='items', subtype_filter='bow')

        # Search for model ID containing '100'
        models = model_gallery_apply_filters(metadata, search_query='100')

        # Combine filters
        models = model_gallery_apply_filters(
            metadata,
            type_filter='items',
            subtype_filter='bow',
            search_query='50'
        )
    """
    # Start with all models or filtered by type/subtype
    if type_filter:
        candidate_models = model_gallery_get_models_by_type_subtype(
            metadata, type_filter, subtype_filter
        )
    else:
        # Get all models from all types - handle hierarchical structure
        candidate_models = []
        for type_name, type_data in metadata.items():
            if isinstance(type_data, dict):
                for subtype_data in type_data.values():
                    if isinstance(subtype_data, dict):
                        # For hierarchical types like 'items'
                        for models in subtype_data.values():
                            if isinstance(models, list):
                                candidate_models.extend(models)
                    elif isinstance(subtype_data, list):
                        # For flat types
                        candidate_models.extend(subtype_data)

    # Apply search filter if provided
    if search_query:
        search_query = search_query.lower().strip()
        candidate_models = [
            model_id
            for model_id in candidate_models
            if search_query in model_id.lower()
        ]

    return sorted(candidate_models, key=lambda x: (int(x) if x.isdigit() else float('inf')))


def model_gallery_get_available_subtypes_for_type(
    metadata: Dict, type_name: str
) -> List[str]:
    """
    Get list of available subtypes for a specific type.

    Useful for populating filter UI dropdowns.

    Args:
        metadata: Output from model_gallery_load_metadata()
        type_name: Type to query (e.g., 'armor')

    Returns:
        Sorted list of subtype names. Returns [] if type doesn't exist.

    Example:
        subtypes = model_gallery_get_available_subtypes_for_type(metadata, 'armor')
        # ['arms', 'cloaks', 'feet', 'hands', 'legs', 'shields', 'torso']
    """
    if type_name not in metadata:
        return []

    subtypes = list(metadata[type_name].keys())
    
    # Filter out "_" (placeholder for single-level types) if present
    subtypes = [s for s in subtypes if s != "_"]

    return sorted(subtypes)


def model_gallery_validate_filters(
    metadata: Dict, type_name: Optional[str], subtype_name: Optional[str]
) -> bool:
    """
    Validate if the given type/subtype combination exists in metadata.

    Args:
        metadata: Output from model_gallery_load_metadata()
        type_name: Type to validate
        subtype_name: Subtype to validate

    Returns:
        True if combination exists, False otherwise

    Example:
        is_valid = model_gallery_validate_filters(metadata, 'armor', 'arms')
        # True

        is_valid = model_gallery_validate_filters(metadata, 'armor', 'nonexistent')
        # False
    """
    if not type_name:
        return True  # No filter = valid

    if type_name not in metadata:
        return False

    if not subtype_name:
        return True  # Type exists = valid

    return subtype_name in metadata[type_name]
