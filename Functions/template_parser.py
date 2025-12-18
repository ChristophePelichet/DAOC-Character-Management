"""
Template Parser Module

Handles parsing and processing of DAOC character armor templates.
Supports multiple template formats (Loki, Zenkcraft) with price lookup
and formatting capabilities.

This module extracts business logic from UI dialogs to provide reusable
template parsing functions for armor management and analysis.

Naming Convention: All functions use 'template_*' prefix for easy discovery
and grouping with autocomplete.

Functions:
  - template_parse()              Main entry point for template parsing
  - template_detect_format()      Detect template format type
  - template_parse_loki()         Parse Loki format templates
  - template_parse_zenkcraft()    Parse Zenkcraft format templates
  - template_get_item_price()     Lookup item price from DB/metadata
  - template_format_item_with_price()   Format item with price/category
  - template_merge_columns()      Merge two columns side-by-side
  - template_strip_color_markers()     Remove color markers for width calc
"""

import re
import json
import logging
from pathlib import Path
from collections import defaultdict
from typing import Tuple, Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Model viewer slots - items that have visual models available
MODEL_SLOTS = {
    # Zenkcraft format slot names
    'Torso', 'Arms', 'Legs', 'Hands', 'Feet', 'Helmet',  # Armor pieces
    'Cloak',                                              # Cape
    'Two Handed', 'Right Hand', 'Left Hand',             # Weapons
    # Loki format slot names (additional)
    'Chest', 'Head'                                       # Loki armor equivalents
}


def template_detect_format(content: str) -> str:
    """
    Detect template format type.

    Checks for Loki format patterns first, falls back to Zenkcraft.

    Args:
        content: Raw template content

    Returns:
        str: "loki" or "zenkcraft"
    """
    loki_pattern = (
        r"^(Chest|Arms|Head|Legs|Hands|Feet|Right Hand|Left Hand|Neck|Cloak|"
        r"Jewel|Belt|Left Ring|Right Ring|Left Wrist|Right Wrist|Mythirian) "
        r"\((.+?)\):$"
    )

    if re.search(loki_pattern, content, re.MULTILINE):
        return "loki"

    return "zenkcraft"


def template_strip_color_markers(text: str) -> str:
    """
    Remove color markers from text for width calculation.

    Args:
        text: Text with color markers

    Returns:
        str: Text without color markers
    """
    text = text.replace("%%COLOR_START:#4CAF50%%", "")
    text = text.replace("%%COLOR_START:#FF9800%%", "")
    text = text.replace("%%COLOR_START:#F44336%%", "")
    text = text.replace("%%COLOR_END%%", "")
    return text


def template_merge_columns(
    left_lines: List[str],
    right_lines: List[str]
) -> List[str]:
    """
    Merge two columns with proper alignment.

    Handles color markers and title lines specially. Uses emoji detection
    to identify title lines (📊, 📚, 🛡️, ✨) which are merged without
    separators.

    Args:
        left_lines: Lines for left column
        right_lines: Lines for right column

    Returns:
        List[str]: Merged lines with proper spacing and separators
    """
    result = []

    max_left_width = 0
    for line in left_lines:
        if line.strip() and not any(emoji in line for emoji in ["📊", "📚", "🛡️", "✨", "🎯", "⭐"]):
            clean_line = template_strip_color_markers(line)
            max_left_width = max(max_left_width, len(clean_line))

    max_left_width = max(max_left_width, 30)

    max_lines = max(len(left_lines), len(right_lines))

    for i in range(max_lines):
        left_line = left_lines[i] if i < len(left_lines) else ""
        right_line = right_lines[i] if i < len(right_lines) else ""

        is_title_line = any(emoji in left_line for emoji in ["📊", "📚", "🛡️", "✨", "🎯", "⭐"]) or \
                        any(emoji in right_line for emoji in ["📊", "📚", "🛡️", "✨", "🎯", "⭐"])

        if right_line and left_line.strip() and not is_title_line:
            clean_left = template_strip_color_markers(left_line)
            padding = max_left_width - len(clean_left)
            result.append(f"{left_line}{' ' * padding}  │  {right_line}")
        elif left_line and right_line and is_title_line:
            clean_left = template_strip_color_markers(left_line)
            padding = max_left_width - len(clean_left)
            result.append(f"{left_line}{' ' * padding}     {right_line}")
        elif left_line:
            result.append(left_line)
        elif right_line:
            result.append(" " * (max_left_width + 2) + "│  " + right_line)

    return result


def template_get_item_price(
    item_name: str,
    realm: str = "",
    db_manager=None,
    metadata: Dict = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Lookup item price from database or metadata.

    Search priority:
    1. Template metadata JSON (manually added prices)
    2. Database with realm-aware search (realm-specific, then :all, then generic)

    Args:
        item_name: Name of the item
        realm: Character realm
        db_manager: DatabaseManager instance
        metadata: Metadata dictionary with prices

    Returns:
        tuple: (price_str, source, category)
            - price_str: Formatted price string or None
            - source: "json", "db", or None
            - category: Item category or None
    """
    try:
        if metadata and 'prices' in metadata:
            if item_name in metadata['prices']:
                return (metadata['prices'][item_name], 'json', None)

        if not db_manager:
            return (None, None, None)

        item_name_lower = item_name.lower()
        realm_lower = realm.lower()

        search_key_realm = f"{item_name_lower}:{realm_lower}"
        item_data = db_manager.search_item(search_key_realm)

        if not item_data:
            search_key_all = f"{item_name_lower}:all"
            item_data = db_manager.search_item(search_key_all)

        if not item_data:
            item_data = db_manager.search_item(item_name)

        item_category = item_data.get('item_category') if item_data else None

        if item_data and 'merchant_price' in item_data:
            price = item_data['merchant_price']
            currency = item_data.get('merchant_currency', '')

            if not currency:
                merchant_zone = item_data.get('merchant_zone', '')
                currency_map = {
                    "DF": "Seals",
                    "SH": "Grimoires",
                    "ToA": "Glasses",
                    "Drake": "Scales",
                    "Epic": "Souls/Roots/Ices",
                    "Epik": "Souls/Roots/Ices"
                }
                currency = currency_map.get(merchant_zone, '')

            if currency:
                return (f"{price} {currency}", 'db', item_category)
            return (str(price), 'db', item_category)

        if item_category:
            return (None, None, item_category)

    except Exception as e:
        logger.debug(f"Failed to lookup price for '{item_name}': {e}")

    return (None, None, None)


def template_format_item_with_price(
    item_name: str,
    price_str: Optional[str] = None,
    price_source: Optional[str] = None,
    item_category: Optional[str] = None,
    items_database_manager=None,
    lang_manager=None
) -> str:
    """
    Format item display with price or category.

    Args:
        item_name: Name of the item
        price_str: Price string if available
        price_source: Source of price (json, db, or None)
        item_category: Item category
        items_database_manager: ItemsDatabaseManager for icon/label lookup
        lang_manager: Language manager for translations

    Returns:
        str: Formatted HTML display string with fixed width
    """
    if price_str:
        icon = "📝" if price_source == 'json' else "💰"
        result = f"{icon} {price_str}"
    elif item_category and item_category != "unknown":
        if items_database_manager:
            icon = items_database_manager.get_category_icon(item_category)
            current_lang = 'en'
            if lang_manager and hasattr(lang_manager, 'current_language'):
                current_lang = lang_manager.current_language
            label = items_database_manager.get_category_label(item_category, current_lang)
            result = f"{icon} {label}"
        else:
            result = "❓"
    else:
        result = "❓"

    return result


def template_parse(
    content: str,
    realm: str = "",
    template_manager=None,
    db_manager=None,
    metadata_path: Path = None,
) -> str:
    """
    Main template parser - detects format and delegates to specific parser.

    Supports:
    - Zenkcraft format (default)
    - Loki format (Slot (Item):)

    Args:
        content: Raw template content as string
        realm: Character realm (Albion, Hibernia, Midgard)
        template_manager: TemplateManager instance for metadata lookups
        db_manager: DatabaseManager instance for item price lookups
        metadata_path: Path to metadata.json file

    Returns:
        str: Formatted template display with stats, equipment, prices
    """
    format_type = template_detect_format(content)

    if format_type == "loki":
        return template_parse_loki(
            content, realm, template_manager, db_manager, metadata_path
        )
    else:
        return template_parse_zenkcraft(
            content, realm, template_manager, db_manager, metadata_path
        )


def template_parse_loki(
    content: str,
    realm: str = "",
    template_manager=None,
    db_manager=None,
    metadata_path: Path = None,
) -> str:
    """
    Parse Loki format templates.

    Loki format structure:
    - Equipment: Slot (Item Name):
    - Stats: Statistic section with "Stat: current/cap"
    - Resists: Resistance section with "Resist: current/cap"
    - Skills: Skill section with "Skill: level/cap"
    - Bonuses: TOA Bonus section with "Bonus: value"

    Args:
        content: Raw template content
        realm: Character realm
        template_manager: TemplateManager instance
        db_manager: DatabaseManager instance
        metadata_path: Path to metadata.json

    Returns:
        str: Formatted Loki template display
    """
    from Functions.language_manager import lang
    from Functions.items_database_manager import ItemsDatabaseManager

    logger.debug("Parsing Loki format template")

    metadata = {}
    try:
        if metadata_path and Path(metadata_path).exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
    except Exception as e:
        logger.debug(f"Could not load metadata for price lookup: {e}")

    lines = content.split('\n')
    output = []

    loki_pattern = (
        r'^(Chest|Arms|Head|Legs|Hands|Feet|Right Hand|Left Hand|Neck|'
        r'Cloak|Jewel|Belt|Left Ring|Right Ring|Left Wrist|Right Wrist|Mythirian) '
        r'\((.+?)\):$'
    )

    stats = {}
    bonuses = {}
    resists = {}
    skills = {}
    equipment = []

    current_section = None
    for line in lines:
        line_stripped = line.strip()

        if line_stripped in ["Statistic"]:
            current_section = "stats"
            continue
        elif line_stripped in ["TOA Bonus"]:
            current_section = "bonuses"
            continue
        elif line_stripped == "Resistance":
            current_section = "resists"
            continue
        elif line_stripped == "Skill":
            current_section = "skills"
            continue
        elif line_stripped in ["", "Equipment"]:
            if line_stripped == "Equipment":
                current_section = "equipment"
            else:
                current_section = None
            continue

        if current_section == "stats" and "/" in line_stripped:
            match = re.match(r'([^:]+):\s*(\d+)/(\d+)(?:\+\d+)?', line_stripped)
            if match:
                stat_name = match.group(1).strip()
                current = int(match.group(2))
                cap = int(match.group(3))
                if current > 0:
                    stats[stat_name] = (current, cap)

        elif current_section == "bonuses" and ":" in line_stripped:
            parts = line_stripped.split(":", 1)
            if len(parts) == 2:
                bonus_name = parts[0].strip()
                bonus_value = parts[1].strip()
                bonuses[bonus_name] = bonus_value

        elif current_section == "resists" and ":" in line_stripped:
            match = re.match(r'([^:]+):\s*(\d+)/(\d+)(?:\+\d+)?', line_stripped)
            if match:
                resist_name = match.group(1).strip()
                resist_value = match.group(2)
                resists[resist_name] = resist_value

        elif current_section == "skills" and ":" in line_stripped:
            match = re.match(r'([^:]+):\s*(\d+)/(\d+)', line_stripped)
            if match:
                skill_name = match.group(1).strip()
                skill_level = int(match.group(2))
                if skill_level > 0:
                    skills[skill_name] = skill_level

        elif current_section == "equipment" or re.match(loki_pattern, line_stripped):
            match = re.match(loki_pattern, line_stripped)
            if match:
                slot = match.group(1)
                item_name = match.group(2).strip()
                if item_name and len(item_name) > 2:
                    item_section_start = content.find(f"{slot} ({item_name}):")
                    if item_section_start != -1:
                        item_section = content[item_section_start:item_section_start + 200]
                        if "Quality:" not in item_section:
                            equipment.append({
                                'slot': slot,
                                'name': item_name,
                                'source_type': 'Loot'
                            })

    output.append(f"📋 {lang.get('armoury_dialog.preview.title')} - {lang.get('armoury_dialog.preview.format_loki')}")
    output.append("")

    stats_lines = []
    resist_lines = []

    if stats:
        stats_lines.append(f"📊  {lang.get('armoury_dialog.preview.stats_title')}")
        for stat_name, (current, cap) in stats.items():
            if current < cap:
                color = "#F44336"
            elif current == cap:
                color = "#FF9800"
            else:
                color = "#4CAF50"

            stat_line = f"%%COLOR_START:{color}%%{stat_name:15} {current:3}/{cap:<3}%%COLOR_END%%"
            stats_lines.append(f"  {stat_line}")

    if resists:
        resist_lines.append(f"🛡️  {lang.get('armoury_dialog.preview.resists_title')}")
        resist_list = list(resists.items())
        for i in range(0, len(resist_list), 2):
            resist1_name, resist1_value = resist_list[i]
            resist1_val = int(resist1_value)

            if resist1_val < 25:
                color1 = "#F44336"
            elif resist1_val == 25:
                color1 = "#FF9800"
            else:
                color1 = "#4CAF50"

            resist1 = f"%%COLOR_START:{color1}%%{resist1_name:8} {resist1_value:>2}%%%COLOR_END%%"

            if i + 1 < len(resist_list):
                resist2_name, resist2_value = resist_list[i + 1]
                resist2_val = int(resist2_value)

                if resist2_val < 25:
                    color2 = "#F44336"
                elif resist2_val == 25:
                    color2 = "#FF9800"
                else:
                    color2 = "#4CAF50"

                resist2 = f"%%COLOR_START:{color2}%%{resist2_name:8} {resist2_value:>2}%%%COLOR_END%%"
            else:
                resist2 = ""

            resist_lines.append(f"  {resist1}  /  {resist2}")

    if stats_lines or resist_lines:
        block1_output = template_merge_columns(stats_lines, resist_lines)
        output.extend(block1_output)
        output.append("")

    # Skills and Bonuses
    skills_lines = []
    bonuses_lines = []

    if skills:
        skills_lines.append("🎯  SKILLS")
        for skill_name, skill_level in skills.items():
            skills_lines.append(f"  {skill_name.ljust(20)} {skill_level}")

    if bonuses:
        bonuses_lines.append("⭐  BONUSES")
        bonus_items = list(bonuses.items())
        for i in range(0, len(bonus_items), 2):
            left_name, left_value = bonus_items[i]
            left = f"{left_name:25} {left_value:>8}"

            if i + 1 < len(bonus_items):
                right_name, right_value = bonus_items[i + 1]
                right = f"{right_name:25} {right_value:>8}"
            else:
                right = ""

            if right:
                bonuses_lines.append(f"  {left}  │  {right}")
            else:
                bonuses_lines.append(f"  {left}")

    # Merge BLOCK 2: SKILLS │ BONUSES
    if skills_lines or bonuses_lines:
        block2_output = template_merge_columns(skills_lines, bonuses_lines)
        output.extend(block2_output)
        output.append("")

    output.append("═" * 94)
    output.append("")

    equipment_count = len(equipment)
    equipment_text = lang.get('armoury_dialog.preview.equipment_title')
    count_text = lang.get('armoury_dialog.preview.equipment_count').format(count=equipment_count)
    output.append(f"⚔️  {equipment_text} ({count_text})")
    output.append("")

    if equipment:
        armor_slots = ['Chest', 'Arms', 'Head', 'Legs', 'Hands', 'Feet']
        jewelry_slots = [
            'Left Ring', 'Right Ring', 'Left Wrist', 'Right Wrist',
            'Jewel', 'Belt', 'Neck', 'Cloak', 'Mythirian'
        ]
        weapon_slots = ['Left Hand', 'Right Hand']

        armor_items = [item for item in equipment if item['slot'] in armor_slots]
        jewelry_items = [item for item in equipment if item['slot'] in jewelry_slots]
        weapon_items = [item for item in equipment if item['slot'] in weapon_slots]

        all_loot = armor_items + jewelry_items + weapon_items
        max_len = (
            max(len(f"{item['name']} ({item['slot']})") for item in all_loot)
            if all_loot
            else 0
        )
        max_len = max(max_len, 35)

        items_without_price = []
        currency_totals_temp = defaultdict(int)

        if armor_items:
            output.append(f"    🛡️  {lang.get('armoury_dialog.preview.equipment_categories.armor_pieces')} :")
            for item in armor_items:
                clean_item_text = f"{item['name']} ({item['slot']})"

                price_str, price_source, item_category = template_get_item_price(
                    item['name'], realm, db_manager, metadata
                )

                # Add clickable model icon ONLY if item exists in DB and has visual model
                if item['slot'] in MODEL_SLOTS and (price_str or (item_category and item_category != "unknown")):
                    model_icon = f'<a href="model:{item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
                    item_text = f"{model_icon}{clean_item_text}"
                else:
                    item_text = clean_item_text

                padding = max_len - len(clean_item_text)
                item_with_padding = f"• {item_text}{' ' * padding}"

                display = template_format_item_with_price(
                    item['name'], price_str, price_source, item_category,
                    ItemsDatabaseManager, lang
                )
                output.append(f"      {item_with_padding}  {display}")

                if price_str:
                    try:
                        parts = str(price_str).split()
                        if len(parts) >= 2:
                            price = int(parts[0])
                            currency = ' '.join(parts[1:])
                            currency_totals_temp[currency] += price
                    except:
                        pass
                elif not item_category or item_category == "unknown":
                    items_without_price.append(item['name'])

        if jewelry_items:
            output.append("")
            output.append(f"    💍 {lang.get('armoury_dialog.preview.equipment_categories.jewelry')} :")

            jewelry_dict = {item['slot']: item for item in jewelry_items}

            pairs = [
                ('Mythirian', None),
                ('Neck', 'Cloak'),
                ('Jewel', 'Belt'),
                ('Left Ring', 'Right Ring'),
                ('Left Wrist', 'Right Wrist')
            ]

            # Pre-calculate max item name width (without price) for jewelry alignment
            max_item_name_width = 0
            for left_slot, right_slot in pairs:
                if left_slot in jewelry_dict:
                    left_text = f"{jewelry_dict[left_slot]['name']} ({jewelry_dict[left_slot]['slot']})"
                    max_item_name_width = max(max_item_name_width, len(left_text))
                if right_slot and right_slot in jewelry_dict:
                    right_text = f"{jewelry_dict[right_slot]['name']} ({jewelry_dict[right_slot]['slot']})"
                    max_item_name_width = max(max_item_name_width, len(right_text))

            max_item_name_width = max(max_item_name_width, 35)  # Minimum width

            # Pre-calculate max total width including prices for left column alignment
            max_left_total_width = 0
            for left_slot, right_slot in pairs:
                if left_slot in jewelry_dict:
                    left_item = jewelry_dict[left_slot]
                    left_text = f"{left_item['name']} ({left_item['slot']})"
                    left_price_str, left_price_source, left_item_category = template_get_item_price(
                        left_item['name'], realm, db_manager, metadata
                    )
                    left_name_padded = left_text.ljust(max_item_name_width)
                    left_display = template_format_item_with_price(
                        left_item['name'], left_price_str, left_price_source, left_item_category,
                        ItemsDatabaseManager, lang
                    )
                    full_line = f"• {left_name_padded}  {left_display}"
                    max_left_total_width = max(max_left_total_width, len(full_line))

            max_left_total_width = max(max_left_total_width, 50)  # Minimum total width

            for left_slot, right_slot in pairs:
                if left_slot in jewelry_dict:
                    left_item = jewelry_dict[left_slot]
                    right_item = jewelry_dict.get(right_slot) if right_slot else None

                    # Build left column
                    if left_item:
                        clean_left_text = f"{left_item['name']} ({left_item['slot']})"

                        left_price_str, left_price_source, left_item_category = template_get_item_price(
                            left_item['name'], realm, db_manager, metadata
                        )

                        # Add clickable model icon ONLY if item exists in DB and has visual model
                        if left_item['slot'] in MODEL_SLOTS and (left_price_str or (left_item_category and left_item_category != "unknown")):
                            model_icon = f'<a href="model:{left_item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
                            left_text = f"{model_icon}{clean_left_text}"
                        else:
                            left_text = clean_left_text

                        # Add padding to HTML version
                        padding_needed = max_item_name_width - len(clean_left_text)
                        left_text_padded = left_text + (' ' * padding_needed)
                        left_display = template_format_item_with_price(
                            left_item['name'], left_price_str, left_price_source, left_item_category,
                            ItemsDatabaseManager, lang
                        )
                        left_output = f"• {left_text_padded}  {left_display}"

                        # Accumulate currency totals
                        if left_price_str:
                            try:
                                parts = str(left_price_str).split()
                                if len(parts) >= 2:
                                    price = int(parts[0])
                                    currency = ' '.join(parts[1:])
                                    currency_totals_temp[currency] += price
                            except:
                                pass
                        elif not left_item_category or left_item_category == "unknown":
                            items_without_price.append(left_item['name'])

                        # Pad entire left line to max width
                        left_output = left_output.ljust(max_left_total_width)
                    else:
                        left_output = " " * max_left_total_width

                    # Build right column
                    if right_item:
                        clean_right_text = f"{right_item['name']} ({right_item['slot']})"

                        right_price_str, right_price_source, right_item_category = template_get_item_price(
                            right_item['name'], realm, db_manager, metadata
                        )

                        # Add clickable model icon ONLY if item exists in DB and has visual model
                        if right_item['slot'] in MODEL_SLOTS and (right_price_str or (right_item_category and right_item_category != "unknown")):
                            model_icon = f'<a href="model:{right_item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
                            right_text = f"{model_icon}{clean_right_text}"
                        else:
                            right_text = clean_right_text

                        # Add padding to HTML version
                        padding_needed = max_item_name_width - len(clean_right_text)
                        right_text_padded = right_text + (' ' * padding_needed)
                        right_display = template_format_item_with_price(
                            right_item['name'], right_price_str, right_price_source, right_item_category,
                            ItemsDatabaseManager, lang
                        )
                        right_output = f"• {right_text_padded}  {right_display}"

                        # Accumulate currency totals
                        if right_price_str:
                            try:
                                parts = str(right_price_str).split()
                                if len(parts) >= 2:
                                    price = int(parts[0])
                                    currency = ' '.join(parts[1:])
                                    currency_totals_temp[currency] += price
                            except:
                                pass
                        elif not right_item_category or right_item_category == "unknown":
                            items_without_price.append(right_item['name'])
                    else:
                        right_output = ""

                    # Merge columns with separator
                    if right_output:
                        output.append(f"      {left_output}  │  {right_output}")
                    elif left_item:
                        output.append(f"      {left_output}")

        if weapon_items:
            output.append("")
            output.append(f"    ⚔️  {lang.get('armoury_dialog.preview.equipment_categories.weapons')} :")
            for item in weapon_items:
                clean_item_text = f"{item['name']} ({item['slot']})"

                price_str, price_source, item_category = template_get_item_price(
                    item['name'], realm, db_manager, metadata
                )

                # Add clickable model icon ONLY if item exists in DB and has visual model
                if item['slot'] in MODEL_SLOTS and (price_str or (item_category and item_category != "unknown")):
                    model_icon = f'<a href="model:{item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
                    item_text = f"{model_icon}{clean_item_text}"
                else:
                    item_text = clean_item_text

                padding = max_len - len(clean_item_text)
                item_with_padding = f"• {item_text}{' ' * padding}"

                display = template_format_item_with_price(
                    item['name'], price_str, price_source, item_category,
                    ItemsDatabaseManager, lang
                )
                output.append(f"      {item_with_padding}  {display}")

                if price_str:
                    try:
                        parts = str(price_str).split()
                        if len(parts) >= 2:
                            price = int(parts[0])
                            currency = ' '.join(parts[1:])
                            currency_totals_temp[currency] += price
                    except:
                        pass
                elif not item_category or item_category == "unknown":
                    items_without_price.append(item['name'])

        output.append("")

        if currency_totals_temp:
            output.append("═" * 94)
            output.append("")

            missing_text = ""
            if items_without_price:
                missing_count = lang.get('armoury_dialog.preview.currency_summary_missing').format(count=len(items_without_price))
                missing_text = f" ({missing_count})"
            currency_title = lang.get('armoury_dialog.preview.currency_summary_title')
            output.append(f"💰 {currency_title}{missing_text}")
            output.append("")
            for currency, total in sorted(currency_totals_temp.items()):
                currency_str = currency[:25].ljust(25)
                total_str = str(total).rjust(6)
                output.append(f"  {currency_str} {total_str}")
            output.append("")

    return "\n".join(output)


def template_parse_zenkcraft(
    content: str,
    realm: str = "",
    template_manager=None,
    db_manager=None,
    metadata_path: Path = None,
) -> str:
    """
    Parse Zenkcraft format templates.

    Zenkcraft format structure:
    - Character Summary section
    - Stats section with "current / cap  StatName"
    - Bonuses section
    - Resists section with "25% Resist"
    - Skills section with "level SkillName"
    - Items section with organized slots

    Args:
        content: Raw template content
        realm: Character realm
        template_manager: TemplateManager instance
        db_manager: DatabaseManager instance
        metadata_path: Path to metadata.json

    Returns:
        str: Formatted Zenkcraft template display
    """
    from Functions.language_manager import lang
    from Functions.items_database_manager import ItemsDatabaseManager

    logger.debug("Parsing Zenkcraft format template")

    metadata = {}
    try:
        if metadata_path and Path(metadata_path).exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
    except Exception as e:
        logger.debug(f"Could not load metadata for price lookup: {e}")

    lines = content.split('\n')

    stats = {}
    bonuses = {}
    resists = {}
    skills = {}
    equipment = []

    current_section = None
    for line in lines:
        line = line.strip()

        if line == "Stats":
            current_section = "stats"
            continue
        elif line == "Bonuses":
            current_section = "bonuses"
            continue
        elif line.startswith("Resists"):
            current_section = "resists"
            continue
        elif line == "Skills":
            current_section = "skills"
            continue
        elif line == "Items":
            current_section = "items"
            continue
        elif line in ["Item Procs and Charges", ""]:
            current_section = None
            continue

        if current_section == "stats" and "/" in line:
            match = re.match(r'(\d+)\s*/\s*(\d+)\s+(.+)', line)
            if match:
                current = int(match.group(1))
                cap = int(match.group(2))
                stat_name = match.group(3).strip()
                if current > 0:
                    stats[stat_name] = (current, cap)

        elif current_section == "bonuses" and ":" in line:
            parts = line.split(":")
            if len(parts) == 2:
                bonus_name = parts[0].strip()
                bonus_value = parts[1].strip()
                if bonus_name not in ["Level", "Utility", "Source Type", "Name"]:
                    bonuses[bonus_name] = bonus_value

        elif current_section == "resists" and "%" in line:
            match = re.match(r'(\d+)%\s+(.+)', line)
            if match:
                resist_value = match.group(1)
                resist_name = match.group(2).strip()
                resists[resist_name] = resist_value

        elif current_section == "skills":
            match = re.match(r'(\d+)\s+(.+)', line)
            if match:
                skill_level = int(match.group(1))
                skill_name = match.group(2).strip()
                if skill_level > 0:
                    skills[skill_name] = skill_level

    # Parse equipment items (extract Slot, Name, Source Type)
    # Valid Zenkcraft slots
    valid_slots = [
        "Helmet", "Hands", "Torso", "Arms", "Feet", "Legs",
        "Right Hand", "Left Hand", "Two Handed", "Ranged",
        "Neck", "Cloak", "Jewelry", "Waist", "L Ring", "R Ring",
        "L Wrist", "R Wrist", "Mythical"
    ]

    equipment = []  # List of {slot, name, source_type}
    current_slot = None
    current_item = {}

    for line in lines:
        stripped = line.strip()

        # Detect item slot
        if stripped in valid_slots:
            # Save previous item if exists
            if current_slot and current_item.get('name'):
                equipment.append({
                    'slot': current_slot,
                    'name': current_item['name'],
                    'source_type': current_item.get('source_type', 'Unknown')
                })

            # Start new item
            current_slot = stripped
            current_item = {}
            continue

        # Parse item properties
        if current_slot:
            if stripped.startswith("Name:"):
                name_value = stripped.split("Name:", 1)[1].strip()
                if name_value:
                    current_item['name'] = name_value
            elif stripped.startswith("Source Type:"):
                source_value = stripped.split("Source Type:", 1)[1].strip()
                current_item['source_type'] = source_value
            elif stripped == "" or stripped == "Bonuses" or stripped in ["Item Procs and Charges"]:
                # End of item section
                if current_slot and current_item.get('name'):
                    equipment.append({
                        'slot': current_slot,
                        'name': current_item['name'],
                        'source_type': current_item.get('source_type', 'Unknown')
                    })
                    current_slot = None
                    current_item = {}

    # Save last item if exists
    if current_slot and current_item.get('name'):
        equipment.append({
            'slot': current_slot,
            'name': current_item['name'],
            'source_type': current_item.get('source_type', 'Unknown')
        })

    equipment_count = len(equipment)

    # Helper function to get item price from template JSON or database
    def get_item_price(item_name):
        """
        Lookup item price with priority chain:
        1. Template metadata JSON (manually added prices via search)
        2. Database (internal or personal) with realm-aware search

        Returns tuple: (formatted_price_string, source, item_category)
        - source can be: 'json' (from template) or 'db' (from database)
        - item_category: Category key (quest_reward, event_reward, unknown) or None
        """
        try:
            # Step 1: Check template metadata JSON for stored price
            if metadata and 'prices' in metadata:
                if item_name in metadata['prices']:
                    return (metadata['prices'][item_name], 'json', None)

            # Step 2: Try database with realm-aware search (only if db_manager provided)
            if not db_manager:
                return (None, None, None)

            item_name_lower = item_name.lower()
            realm_lower = realm.lower() if realm else "all"

            # Priority 1: Try with specific realm suffix
            search_key_realm = f"{item_name_lower}:{realm_lower}"
            item_data = db_manager.search_item(search_key_realm)

            # Priority 2: Try with ":all" suffix
            if not item_data:
                search_key_all = f"{item_name_lower}:all"
                item_data = db_manager.search_item(search_key_all)

            # Priority 3: Try without realm suffix (legacy)
            if not item_data:
                item_data = db_manager.search_item(item_name)

            # Check if item is categorized
            item_category = item_data.get('item_category') if item_data else None

            # Format price if found in database
            if item_data and 'merchant_price' in item_data:
                price = item_data['merchant_price']
                currency = item_data.get('merchant_currency', '')

                if currency:
                    return (f"{price} {currency}", 'db', item_category)
                return (price, 'db', item_category)

            # Return category even if no price found
            if item_category:
                return (None, None, item_category)

        except Exception as e:
            logger.debug(f"Failed to lookup price for '{item_name}': {e}")

        return (None, None, None)

    output = []

    stats_lines = []
    resist_lines = []

    if stats:
        stats_lines.append("📊  STATS")
        for stat_name, (current, cap) in stats.items():
            if current == cap:
                color = "#4CAF50"
            elif current > cap:
                color = "#FF9800"
            else:
                color = "#F44336"

            stat_label = stat_name.ljust(15)
            current_str = str(current).rjust(3)
            cap_str = str(cap).rjust(3)
            stats_lines.append(f"  {stat_label} %%COLOR_START:{color}%%{current_str} / {cap_str}%%COLOR_END%%")

    if resists:
        resist_lines.append(f"🛡️  {lang.get('armoury_dialog.preview.resists_title')}")
        resist_list = list(resists.items())
        for i in range(0, len(resist_list), 2):
            resist1_name, resist1_value = resist_list[i]
            resist1_val = int(resist1_value)

            if resist1_val < 25:
                color1 = "#F44336"
            elif resist1_val == 25:
                color1 = "#FF9800"
            else:
                color1 = "#4CAF50"

            resist1 = f"%%COLOR_START:{color1}%%{resist1_name:8} {resist1_value:>2}%%%COLOR_END%%"

            if i + 1 < len(resist_list):
                resist2_name, resist2_value = resist_list[i + 1]
                resist2_val = int(resist2_value)

                if resist2_val < 25:
                    color2 = "#F44336"
                elif resist2_val == 25:
                    color2 = "#FF9800"
                else:
                    color2 = "#4CAF50"

                resist2 = f"%%COLOR_START:{color2}%%{resist2_name:8} {resist2_value:>2}%%%COLOR_END%%"
            else:
                resist2 = ""

            resist_lines.append(f"  {resist1}  /  {resist2}")

    skills_lines = []
    bonuses_lines = []

    if skills:
        skills_lines.append(f"📚  {lang.get('armoury_dialog.preview.skills_title')}")
        for skill_name, skill_level in skills.items():
            skills_lines.append(f"  {skill_name.ljust(20)} {skill_level}")

    if bonuses:
        bonuses_lines.append(f"✨  {lang.get('armoury_dialog.preview.bonuses_title')}")
        bonus_items = list(bonuses.items())
        for i in range(0, len(bonus_items), 2):
            left_name, left_value = bonus_items[i]
            left = f"{left_name:20} {left_value:>5}"

            if i+1 < len(bonus_items):
                right_name, right_value = bonus_items[i+1]
                right = f"{right_name:20} {right_value:>5}"
            else:
                right = " " * 26

            bonuses_lines.append(f"  {left}  /  {right}")

    if stats_lines or resist_lines:
        block1_output = template_merge_columns(stats_lines, resist_lines)
        output.extend(block1_output)
        output.append("")

    if skills_lines or bonuses_lines:
        block2_output = template_merge_columns(skills_lines, bonuses_lines)
        output.extend(block2_output)

    output.append("")

    max_line_width = 80
    for line in output:
        clean_line = template_strip_color_markers(line)
        max_line_width = max(max_line_width, len(clean_line))

    output.append("═" * max_line_width)

    # Helper function to format item display (price or category icon)
    def format_item_display(item_name, price_str, price_source, item_category):
        """Format item display with price or category icon."""
        if price_str:
            # Has price: show icon + price
            icon = "📋" if price_source == 'json' else "💰"
            return f"{icon} {price_str}"
        elif item_category and item_category != "unknown":
            # No price but has category: show category
            icon = ItemsDatabaseManager.get_category_icon(item_category)
            current_lang = lang.current_language if hasattr(lang, 'current_language') else 'en'
            label = ItemsDatabaseManager.get_category_label(item_category, current_lang)
            return f"{icon} {label}"
        else:
            # No price, no category: unknown
            return "❓"

    # Separate Spellcraft and Loot items
    spellcraft_items = [item for item in equipment if item.get('source_type', '').lower() == 'spellcraft']
    loot_items = [item for item in equipment if item.get('source_type', '').lower() == 'loot']

    # Build equipment header with counts
    equipment_header = "⚔️  EQUIPMENT ("
    if spellcraft_items and loot_items:
        equipment_header += f"✨ Spellcraft: {len(spellcraft_items)} / 🏆 Loot: {len(loot_items)}"
    elif spellcraft_items:
        equipment_header += f"✨ Spellcraft: {len(spellcraft_items)}"
    elif loot_items:
        equipment_header += f"🏆 Loot: {len(loot_items)}"
    else:
        equipment_header += f"{equipment_count}/18 slots"
    equipment_header += ")"

    output.append("")
    output.append(equipment_header)
    output.append("")

    # Track items without price and currency totals
    items_without_price = []
    from collections import defaultdict
    currency_totals_temp = defaultdict(int)

    # Process loot items (separated by category)
    if loot_items:
        armor_slots = ['Helmet', 'Hands', 'Torso', 'Arms', 'Feet', 'Legs']
        jewelry_slots = ['L Ring', 'R Ring', 'L Wrist', 'R Wrist', 'Jewelry', 'Waist', 'Neck', 'Cloak', 'Mythical']
        weapon_slots = ['Left Hand', 'Right Hand', 'Two Handed', 'Ranged']

        armor_items = [item for item in loot_items if item['slot'] in armor_slots]
        jewelry_items = [item for item in loot_items if item['slot'] in jewelry_slots]
        weapon_items = [item for item in loot_items if item['slot'] in weapon_slots]

        # Calculate max length for alignment
        all_items = armor_items + jewelry_items + weapon_items
        max_len = max(len(f"{item['name']} ({item['slot']})") for item in all_items) if all_items else 35
        max_len = max(max_len, 35)

        # Display Armor pieces
        if armor_items:
            output.append("    🛡️  Armor Pieces:")
            for item in armor_items:
                item_name = item['name']
                item_text = f"{item_name} ({item['slot']})"

                # Try to get model ID from database
                model_id = None
                if db_manager:
                    try:
                        item_name_lower = item_name.lower()
                        realm_lower = realm.lower() if realm else "all"

                        # Search for item in DB
                        search_key = f"{item_name_lower}:{realm_lower}"
                        item_data = db_manager.search_item(search_key)
                        if not item_data:
                            search_key = f"{item_name_lower}:all"
                            item_data = db_manager.search_item(search_key)
                        if not item_data:
                            item_data = db_manager.search_item(item_name)

                        if item_data:
                            model_id = item_data.get('model') or item_data.get('model_id')
                    except:
                        pass

                # Add model icon if model exists
                if model_id:
                    item_text = f'<a href="model:{item_name}" style="text-decoration:none; color:#4CAF50;">🔍</a> {item_text}'

                price_str, price_source, item_category = get_item_price(item_name)
                padding = max_len - len(f"{item_name} ({item['slot']})")
                display = format_item_display(item_name, price_str, price_source, item_category)
                output.append(f"      • {item_text}{' ' * padding}  {display}")

                # Accumulate currency totals
                if price_str:
                    try:
                        parts = str(price_str).split()
                        if len(parts) >= 2:
                            price = int(parts[0])
                            currency = ' '.join(parts[1:])
                            currency_totals_temp[currency] += price
                    except:
                        pass
                elif not item_category or item_category == "unknown":
                    items_without_price.append(item_name)

        # Display Jewelry items (2 columns layout)
        if jewelry_items:
            output.append("")
            output.append("    ✨  Jewelry:")

            jewelry_dict = {item['slot']: item for item in jewelry_items}

            # Define pairs: (left_slot, right_slot)
            pairs = [
                ('Mythical', None),
                ('Neck', 'Cloak'),
                ('Jewelry', 'Waist'),
                ('L Ring', 'R Ring'),
                ('L Wrist', 'R Wrist')
            ]

            # Calculate max widths for alignment
            max_item_name_width = 0
            for left_slot, right_slot in pairs:
                if left_slot in jewelry_dict:
                    left_text = f"{jewelry_dict[left_slot]['name']} ({jewelry_dict[left_slot]['slot']})"
                    max_item_name_width = max(max_item_name_width, len(left_text))
                if right_slot and right_slot in jewelry_dict:
                    right_text = f"{jewelry_dict[right_slot]['name']} ({jewelry_dict[right_slot]['slot']})"
                    max_item_name_width = max(max_item_name_width, len(right_text))
            max_item_name_width = max(max_item_name_width, 35)

            # Calculate max left column total width
            max_left_total_width = 0
            for left_slot, right_slot in pairs:
                if left_slot in jewelry_dict:
                    left_item = jewelry_dict[left_slot]
                    left_text = f"{left_item['name']} ({left_item['slot']})"
                    left_price_str, left_price_source, left_item_category = get_item_price(left_item['name'])
                    left_name_padded = left_text.ljust(max_item_name_width)
                    left_display = format_item_display(left_item['name'], left_price_str, left_price_source, left_item_category)
                    full_line = f"• {left_name_padded}  {left_display}"
                    max_left_total_width = max(max_left_total_width, len(full_line))
            max_left_total_width = max(max_left_total_width, 50)

            # Display paired jewelry items
            for left_slot, right_slot in pairs:
                left_item = jewelry_dict.get(left_slot)
                right_item = jewelry_dict.get(right_slot) if right_slot else None

                # Build left column
                if left_item:
                    clean_left_text = f"{left_item['name']} ({left_item['slot']})"

                    left_price_str, left_price_source, left_item_category = template_get_item_price(
                        left_item['name'], realm, db_manager, metadata
                    )

                    # Add clickable model icon ONLY if item is Cloak and exists in DB
                    if left_item['slot'] in MODEL_SLOTS and (left_price_str or (left_item_category and left_item_category != "unknown")):
                        model_icon = f'<a href="model:{left_item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
                        left_text = f"{model_icon}{clean_left_text}"
                    else:
                        left_text = clean_left_text

                    # Calculate padding based on clean text, apply to padded text
                    padding_needed = max_item_name_width - len(clean_left_text)
                    left_text_padded = left_text + (' ' * padding_needed)
                    left_display = format_item_display(left_item['name'], left_price_str, left_price_source, left_item_category)
                    left_output = f"• {left_text_padded}  {left_display}"

                    if left_price_str:
                        try:
                            parts = str(left_price_str).split()
                            if len(parts) >= 2:
                                price = int(parts[0])
                                currency = ' '.join(parts[1:])
                                currency_totals_temp[currency] += price
                        except:
                            pass
                    elif not left_item_category or left_item_category == "unknown":
                        items_without_price.append(left_item['name'])
                    left_output = left_output.ljust(max_left_total_width)
                else:
                    left_output = " " * max_left_total_width

                # Build right column
                if right_item:
                    clean_right_text = f"{right_item['name']} ({right_item['slot']})"

                    right_price_str, right_price_source, right_item_category = template_get_item_price(
                        right_item['name'], realm, db_manager, metadata
                    )

                    # Add clickable model icon ONLY if item is Cloak and exists in DB
                    if right_item['slot'] in MODEL_SLOTS and (right_price_str or (right_item_category and right_item_category != "unknown")):
                        model_icon = f'<a href="model:{right_item["name"]}" style="text-decoration:none; color:#4CAF50;">🔍</a> '
                        right_text = f"{model_icon}{clean_right_text}"
                    else:
                        right_text = clean_right_text

                    # Calculate padding based on clean text, apply to padded text
                    padding_needed = max_item_name_width - len(clean_right_text)
                    right_text_padded = right_text + (' ' * padding_needed)
                    right_display = format_item_display(right_item['name'], right_price_str, right_price_source, right_item_category)
                    right_output = f"• {right_text_padded}  {right_display}"

                    if right_price_str:
                        try:
                            parts = str(right_price_str).split()
                            if len(parts) >= 2:
                                price = int(parts[0])
                                currency = ' '.join(parts[1:])
                                currency_totals_temp[currency] += price
                        except:
                            pass
                    elif not right_item_category or right_item_category == "unknown":
                        items_without_price.append(right_item['name'])
                else:
                    right_output = ""

                # Merge columns
                if right_output:
                    output.append(f"      {left_output}  │  {right_output}")
                elif left_item:
                    output.append(f"      {left_output}")

        # Display Weapons
        if weapon_items:
            output.append("")
            output.append("    ⚔️  Weapons:")
            for item in weapon_items:
                item_name = item['name']
                item_text = f"{item_name} ({item['slot']})"

                # Try to get model ID from database
                model_id = None
                if db_manager:
                    try:
                        item_name_lower = item_name.lower()
                        realm_lower = realm.lower() if realm else "all"
                        search_key = f"{item_name_lower}:{realm_lower}"
                        item_data = db_manager.search_item(search_key)
                        if not item_data:
                            search_key = f"{item_name_lower}:all"
                            item_data = db_manager.search_item(search_key)
                        if not item_data:
                            item_data = db_manager.search_item(item_name)
                        if item_data:
                            model_id = item_data.get('model') or item_data.get('model_id')
                    except:
                        pass

                # Add model icon if model exists
                if model_id:
                    item_text = f'<a href="model:{item_name}" style="text-decoration:none; color:#4CAF50;">🔍</a> {item_text}'

                price_str, price_source, item_category = get_item_price(item_name)
                padding = max_len - len(f"{item_name} ({item['slot']})")
                display = format_item_display(item_name, price_str, price_source, item_category)
                output.append(f"      • {item_text}{' ' * padding}  {display}")

                # Accumulate currency totals
                if price_str:
                    try:
                        parts = str(price_str).split()
                        if len(parts) >= 2:
                            price = int(parts[0])
                            currency = ' '.join(parts[1:])
                            currency_totals_temp[currency] += price
                    except:
                        pass
                elif not item_category or item_category == "unknown":
                    items_without_price.append(item['name'])

        # Add price indicators legend
        if items_without_price:
            output.append("")
            output.append("  Price indicators:")
            output.append("      💰 = Database   📋 = Template   ❓ = Missing")
            output.append("      🏆 = Quest Reward   🎉 = Event Reward")

        # Add currency summary if prices found
        if currency_totals_temp:
            output.append("")
            output.append("═" * 80)
            output.append("")
            missing_count = f" ({len(items_without_price)} item(s) without price)" if items_without_price else ""
            output.append(f"💰 CURRENCY SUMMARY{missing_count}")
            output.append("")
            for currency, total in sorted(currency_totals_temp.items()):
                currency_str = currency[:25].ljust(25)
                total_str = str(total).rjust(6)
                output.append(f"  {currency_str} {total_str}")
            output.append("")

    return "\n".join(output)
