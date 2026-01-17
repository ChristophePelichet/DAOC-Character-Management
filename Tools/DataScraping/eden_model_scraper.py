"""
Eden Model Gallery Scraper

Scrapes https://justamodelfilterpage.com/model_gallery.json to extract all model-to-item mappings.
Creates a complete database linking item numbers to their categories and model files.

This prevents issues with model file relocations and provides a single source of truth
for the models gallery and item database.
"""

import json
import logging
from pathlib import Path
from typing import Dict
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Category to slot name mapping
CATEGORY_TO_SLOT = {
    'armor/arms': 'Arms',
    'armor/cloaks': 'Cloaks',
    'armor/feet': 'Feet',
    'armor/hands': 'Hands',
    'armor/head': 'Head',
    'armor/legs': 'Legs',
    'armor/quiver': 'Quiver',
    'armor/shields': 'Shields',
    'armor/torso': 'Torso',
    'boats': 'Boats',
    'deco and etc': 'Deco',
    'misc models': 'Misc',
    'siege': 'Siege',
    'tents': 'Tents',
    'weapons': 'Weapons',
}


def scrape_eden_models() -> Dict[str, dict]:
    """
    Scrape the Eden model gallery JSON and extract item-to-model mappings.
    
    The JSON structure is:
    [
        {
            "category": "armor/arms",
            "models": ["1002.jpg", "1189.jpg", ...]
        },
        ...
    ]
    
    We extract the item ID from each filename (e.g., "1756.jpg" → item 1756).
    
    Returns:
        Dictionary mapping item_id to {category, slot, models: [model_files]}
    """
    url = "https://justamodelfilterpage.com/model_gallery.json"
    logger.info(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        raise
    
    gallery_data = response.json()
    models_data = {}
    
    # Process each category
    for category_info in gallery_data:
        category = category_info.get('category')
        models = category_info.get('models', [])
        slot_name = CATEGORY_TO_SLOT.get(category, category)
        
        logger.info(f"Processing category: {category} ({len(models)} models)")
        
        # Extract item ID from each model filename
        for model_file in models:
            # Extract number from filename (e.g., "1756.jpg" → 1756)
            try:
                item_id = int(model_file.split('.')[0])
                
                if item_id not in models_data:
                    models_data[item_id] = {
                        'category': category,
                        'slot': slot_name,
                        'models': [],
                    }
                
                models_data[item_id]['models'].append(model_file)
            except (ValueError, IndexError):
                logger.warning(f"Could not extract item ID from {model_file}")
                continue
        
        # Sort models for each item
        for item_id in models_data:
            models_data[item_id]['models'].sort()
    
    return models_data


def save_models_database(data: Dict, output_path: Path):
    """Save models database to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Sort by item ID for readability
    sorted_data = {str(k): v for k, v in sorted(data.items())}
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(data)} items to {output_path}")
    
    # Print statistics
    categories = {}
    total_models = 0
    for item_data in data.values():
        cat = item_data['category']
        categories[cat] = categories.get(cat, 0) + 1
        total_models += len(item_data['models'])
    
    logger.info(f"Total models: {total_models}")
    logger.info("Items by category:")
    for cat, count in sorted(categories.items()):
        logger.info(f"  {cat}: {count} items")


def main():
    """Main entry point."""
    try:
        logger.info("Starting Eden model gallery scraper...")
        models_data = scrape_eden_models()
        
        output_path = Path(__file__).parent.parent.parent / 'Data' / 'dol_models_database.json'
        save_models_database(models_data, output_path)
        
        logger.info("✓ Scraping completed successfully")
        return 0
    except Exception as e:
        logger.error(f"✗ Scraping failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
