"""
Model Gallery Builder Widget - Prepares and manages gallery data for display.

This widget acts as a bridge between filter operations and the gallery display.
It handles filtering operations and prepares thumbnail data for UI rendering.

Paired with: Functions/model_gallery_builder.py
"""

import logging
from typing import List, Optional
from PySide6.QtCore import QObject, Signal

from Functions.model_database_manager import model_gallery_load_metadata
from Functions.model_gallery_filter import model_gallery_apply_filters
from Functions.model_gallery_builder import (
    model_gallery_build_thumbnail_list,
    ModelThumbnail,
)


class ModelsGalleryBuilderWidget(QObject):
    """
    Manages gallery data preparation and filtering.

    Handles the logic of applying filters and building thumbnail data
    for display in the gallery view. Emits signals when data changes.
    """

    # Signal: thumbnails ready for display: List[ModelThumbnail]
    thumbnails_ready = Signal(list)

    # Signal: stats updated: dict with statistics
    stats_updated = Signal(dict)

    # Signal: error occurred: str (error message)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        """
        Initialize gallery builder.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.metadata = {}
        self.current_thumbnails: List[ModelThumbnail] = []

    def set_metadata(self, metadata: dict):
        """
        Set metadata without automatically loading gallery.

        Args:
            metadata: Model metadata dictionary
        """
        logging.info(f"Builder: set_metadata called with {len(metadata)} types")
        self.metadata = metadata
        logging.info("Builder: metadata set (NOT calling apply_filters - wait for user filter action)")

    def apply_filters(
        self, type_filter: str = "", subtype_filter: str = "", search_query: str = ""
    ) -> List[ModelThumbnail]:
        """
        Apply filters and build thumbnails.

        Args:
            type_filter: Type filter (e.g., 'armor'). Empty = no filter
            subtype_filter: Subtype filter (e.g., 'arms'). Ignored if no type_filter
            search_query: Search query by model ID

        Returns:
            List of ModelThumbnail objects matching filters
        """
        logging.info(f"Builder: apply_filters called - type={type_filter}, subtype={subtype_filter}, search={search_query}")
        
        if not self.metadata:
            logging.error("Builder: no metadata available")
            return []

        try:
            # Apply filters to get matching model IDs
            logging.info(f"Builder: applying filters to metadata with {len(self.metadata)} types")
            model_ids = model_gallery_apply_filters(
                self.metadata,
                type_filter if type_filter else None,
                subtype_filter if subtype_filter else None,
                search_query if search_query else None,
            )

            logging.info(f"Builder: filters returned {len(model_ids)} model IDs")

            # Build thumbnail objects
            self.current_thumbnails = model_gallery_build_thumbnail_list(
                self.metadata, model_ids
            )

            logging.info(f"Builder: emitting thumbnails_ready with {len(self.current_thumbnails)} thumbnails")
            # Emit success signal
            self.thumbnails_ready.emit(self.current_thumbnails)

            return self.current_thumbnails

        except Exception as e:
            from Functions.language_manager import lang
            logging.error(f"Builder: filter error: {e}")
            error_msg = lang.get(
                "models_overview.filter_error",
                default="Filter error: {error}"
            ).format(error=str(e))
            self.error_occurred.emit(error_msg)
            return []

    def get_current_thumbnails(self) -> List[ModelThumbnail]:
        """
        Get currently loaded thumbnails.

        Returns:
            List of ModelThumbnail objects
        """
        return self.current_thumbnails

    def get_thumbnail_count(self) -> int:
        """
        Get count of currently loaded thumbnails.

        Returns:
            Number of thumbnails
        """
        return len(self.current_thumbnails)

    def get_thumbnail_by_id(self, model_id: str) -> Optional[ModelThumbnail]:
        """
        Find a specific thumbnail by model ID.

        Args:
            model_id: Model ID to find

        Returns:
            ModelThumbnail object or None if not found
        """
        for thumbnail in self.current_thumbnails:
            if thumbnail.model_id == model_id:
                return thumbnail
        return None
