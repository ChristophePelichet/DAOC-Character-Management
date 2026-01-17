#!/usr/bin/env python
"""Quick test of gallery functions"""

from Functions.model_database_manager import model_gallery_load_metadata
from Functions.model_gallery_filter import model_gallery_apply_filters
from Functions.model_gallery_builder import model_gallery_build_thumbnail_list

try:
    metadata = model_gallery_load_metadata()
    print(f'Metadata: {len(metadata)} types')
    
    model_ids = model_gallery_apply_filters(metadata)
    print(f'Model IDs: {len(model_ids)}')
    
    thumbnails = model_gallery_build_thumbnail_list(metadata, model_ids)
    print(f'Thumbnails: {len(thumbnails)}')
    
    if thumbnails:
        print(f'First: {thumbnails[0].model_id} in {thumbnails[0].type_name}')
    
except Exception as e:
    import traceback
    traceback.print_exc()
