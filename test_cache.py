#!/usr/bin/env python
"""Test cache functionality"""
import time
from Functions.model_gallery_builder import model_gallery_warmup_cache, model_gallery_build_thumbnail_list
from Functions.model_database_manager import model_gallery_load_metadata
from Functions.model_gallery_filter import model_gallery_apply_filters

print("=== Test 1: Warmup cache ===")
start = time.time()
model_gallery_warmup_cache()
print(f"Warmup time: {time.time() - start:.2f}s")

print("\n=== Test 2: Load metadata (should use cache) ===")
start = time.time()
metadata = model_gallery_load_metadata()
print(f"Metadata load time: {time.time() - start:.2f}s ({len(metadata)} types)")

print("\n=== Test 3: Apply filters ===")
start = time.time()
model_ids = model_gallery_apply_filters(metadata)
print(f"Filters time: {time.time() - start:.2f}s ({len(model_ids)} models)")

print("\n=== Test 4: Build thumbnails (should use cache) ===")
start = time.time()
thumbnails = model_gallery_build_thumbnail_list(metadata, model_ids)
print(f"Thumbnails time: {time.time() - start:.2f}s ({len(thumbnails)} thumbnails)")

print("\n=== Test 5: Build thumbnails again (should be instant) ===")
start = time.time()
thumbnails = model_gallery_build_thumbnail_list(metadata, model_ids[:100])
print(f"Thumbnails 2nd time: {time.time() - start:.2f}s ({len(thumbnails)} thumbnails)")
