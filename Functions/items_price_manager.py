"""
Items Price Manager Module

Handles price synchronization and lookup operations for DAOC items.
Manages template price metadata and finds missing merchant prices.

This module extracts business logic from UI dialogs to provide reusable,
testable price management functions independent of UI concerns.

Naming Convention: All functions use 'items_price_*' prefix for easy discovery
and grouping with autocomplete.

Functions:
  - items_price_sync_template()    Sync template prices with database
  - items_price_find_missing()     Find items without prices in template
"""

import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def items_price_sync_template(
    metadata_path: str,
    metadata: Dict[str, Any],
    db_manager=None,
    realm: str = ""
) -> int:
    """
    Synchronize template prices with database.

    Check if items with prices in JSON now exist in database with merchant prices.
    If yes: remove from JSON (database version will be used instead).
    If no: keep in JSON.

    This prevents duplicate price storage and ensures database remains the single
    source of truth when available.

    Args:
        metadata_path: Path to the metadata JSON file
        metadata: Loaded metadata dict
        db_manager: DatabaseManager instance for item lookup
        realm: Character realm for realm-specific search

    Returns:
        int: Number of items removed from template JSON (synced to database)

    Example:
        >>> count = items_price_sync_template(
        ...     metadata_path="Armory/Hibernia/Json/template.txt.json",
        ...     metadata={"prices": {"Sword": "100 Scales"}},
        ...     db_manager=db_manager,
        ...     realm="Hibernia"
        ... )
        >>> print(f"Synced {count} items")
        Synced 1 items
    """
    if not metadata or 'prices' not in metadata:
        return 0

    prices_dict = metadata.get('prices', {})
    if not prices_dict:
        return 0

    items_to_remove = []
    realm_lower = realm.lower()

    try:
        for item_name in prices_dict.keys():
            # Check if item now exists in database
            item_name_lower = item_name.lower()

            # Try realm-specific search
            search_key_realm = f"{item_name_lower}:{realm_lower}"
            item_data = db_manager.search_item(search_key_realm)

            # Try ":all" suffix
            if not item_data:
                search_key_all = f"{item_name_lower}:all"
                item_data = db_manager.search_item(search_key_all)

            # Try without suffix
            if not item_data:
                item_data = db_manager.search_item(item_name)

            # If item found in DB with a price, mark for removal from JSON
            if item_data and 'merchant_price' in item_data:
                items_to_remove.append(item_name)
                logger.info(
                    f"Item '{item_name}' now found in DB, removing from template JSON"
                )

        # Remove items from JSON if any found in DB
        if items_to_remove:
            for item_name in items_to_remove:
                del metadata['prices'][item_name]

            # Save updated metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Synced {len(items_to_remove)} items from template JSON to DB")
            return len(items_to_remove)

    except Exception as e:
        logger.error(f"Failed to sync template prices: {e}")
        return 0

    return 0


def items_price_find_missing(
    items_list: List[Dict[str, Any]],
    realm: str,
    db_manager=None,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Find items without merchant prices in template.

    Searches for items without prices in both database and template metadata.
    Returns list of items that need price lookup.

    Args:
        items_list: List of item dicts with 'name' and 'slot' keys
        realm: Character realm for realm-specific search
        db_manager: DatabaseManager instance for price lookup
        metadata: Template metadata dict with optional prices

    Returns:
        List[Dict]: Items without prices with structure:
            {
                "name": "Item Name",
                "slot": "Slot",
                "has_price_in_metadata": bool,
                "has_price_in_db": bool
            }

    Example:
        >>> items = [
        ...     {"name": "Sword", "slot": "Right Hand"},
        ...     {"name": "Helm", "slot": "Head"}
        ... ]
        >>> missing = items_price_find_missing(
        ...     items_list=items,
        ...     realm="Hibernia",
        ...     db_manager=db_manager,
        ...     metadata={"prices": {"Sword": "100 Scales"}}
        ... )
        >>> for item in missing:
        ...     print(f"{item['name']}: db={item['has_price_in_db']}, "
        ...           f"metadata={item['has_price_in_metadata']}")
        Helm: db=False, metadata=False
    """
    items_without_price = []
    metadata_prices = metadata.get('prices', {}) if metadata else {}

    for item in items_list:
        item_name = item.get('name', '')
        if not item_name:
            continue

        # Check if price exists in metadata
        has_price_in_metadata = item_name in metadata_prices

        # Check if price exists in database
        has_price_in_db = False
        if db_manager:
            try:
                item_name_lower = item_name.lower()
                realm_lower = realm.lower()

                # Try realm-specific search
                search_key_realm = f"{item_name_lower}:{realm_lower}"
                item_data = db_manager.search_item(search_key_realm)

                # Try ":all" suffix
                if not item_data:
                    search_key_all = f"{item_name_lower}:all"
                    item_data = db_manager.search_item(search_key_all)

                # Try without suffix
                if not item_data:
                    item_data = db_manager.search_item(item_name)

                has_price_in_db = (
                    item_data and 'merchant_price' in item_data
                )
            except Exception as e:
                logger.debug(f"Error looking up price for '{item_name}': {e}")

        # Add to missing list if no price found anywhere
        if not has_price_in_metadata and not has_price_in_db:
            items_without_price.append({
                'name': item_name,
                'slot': item.get('slot', ''),
                'has_price_in_metadata': False,
                'has_price_in_db': False
            })

    return items_without_price
