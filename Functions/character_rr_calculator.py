"""
Character Realm Rank (RR) calculation functions.

This module provides functions for character realm rank calculations, including
rank determination from realm points, level filtering based on rank restrictions,
and progression information to the next rank level.

Functions:
- character_rr_get_valid_levels() - Get valid level range for a given rank
- character_rr_calculate_points_info() - Get progression info to next rank
- character_rr_calculate_from_points() - Calculate rank/level from realm points

Realm Rank System:
- 14 ranks (1-14) with multiple levels per rank
- Rank 1: levels 0-10 (11 levels)
- Ranks 2-14: levels 0-9 (10 levels each)
- Uses realm_ranks.json for rank/title/RP lookups
"""

import logging

logger = logging.getLogger(__name__)


def character_rr_get_valid_levels(rank):
    """
    Get valid level range for a given realm rank.

    Rank 1 has levels 0-10, all other ranks have levels 0-9.

    Args:
        rank (int): Realm rank number (1-14)

    Returns:
        list: List of valid level numbers for this rank

    Example:
        >>> levels = character_rr_get_valid_levels(1)
        >>> levels
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        >>> levels = character_rr_get_valid_levels(2)
        >>> levels
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    try:
        # Rank 1 has levels 0-10, others have 0-9
        max_level = 10 if rank == 1 else 9
        return list(range(0, max_level + 1))
    except Exception as e:
        logger.error(f"Failed to get valid levels for rank {rank}: {e}")
        return [0]


def character_rr_calculate_points_info(data_manager, realm, rank, level):
    """
    Get progression information from current rank/level to next level.

    Returns current realm points, next level realm points, and completion percentage.

    Args:
        data_manager: DataManager instance for accessing rank data
        realm (str): Realm name (e.g., 'Albion', 'Midgard', 'Hibernia')
        rank (int): Current realm rank (1-14)
        level (int): Current level within rank (0-10 for rank 1, 0-9 for others)

    Returns:
        dict: {
            'current_points': int,      # RP at current level
            'next_points': int,         # RP at next level
            'percentage': float,        # Completion % (0-100)
            'current_level_str': str   # e.g., "1L5"
        }
        Returns empty dict if data not found

    Example:
        >>> info = character_rr_calculate_points_info(
        ...     data_manager, 'Albion', 1, 5
        ... )
        >>> info
        {
            'current_points': 12345,
            'next_points': 15000,
            'percentage': 23.5,
            'current_level_str': '1L5'
        }
    """
    try:
        level_str = f"{rank}L{level}"

        # Get current rank info
        rank_info = data_manager.get_rank_by_level(realm, level_str)
        if not rank_info:
            logger.warning(f"Rank info not found for {realm} {level_str}")
            return {}

        current_points = rank_info.get('realm_points', 0)

        # Get next level info
        valid_levels = character_rr_get_valid_levels(rank)
        if level < valid_levels[-1]:
            # Next level within same rank
            next_level = level + 1
            next_level_str = f"{rank}L{next_level}"
        else:
            # Next rank (if not at max)
            if rank >= 14:
                return {}
            next_level_str = f"{rank + 1}L0"

        next_rank_info = data_manager.get_rank_by_level(realm, next_level_str)
        if not next_rank_info:
            logger.warning(f"Next rank info not found for {realm} {next_level_str}")
            return {}

        next_points = next_rank_info.get('realm_points', 0)

        # Calculate percentage
        if next_points > current_points:
            percentage = ((current_points - current_points) / (next_points - current_points)) * 100
        else:
            percentage = 100.0

        return {
            'current_points': current_points,
            'next_points': next_points,
            'percentage': percentage,
            'current_level_str': level_str
        }

    except Exception as e:
        logger.error(f"Failed to calculate points info for {realm} {rank}L{level}: {e}")
        return {}


def character_rr_calculate_from_points(data_manager, realm, realm_points):
    """
    Calculate realm rank and level from realm points.

    Looks up the realm rank info based on the provided realm points value.

    Args:
        data_manager: DataManager instance for accessing rank data
        realm (str): Realm name (e.g., 'Albion', 'Midgard', 'Hibernia')
        realm_points (int): Total realm points for character

    Returns:
        dict: {
            'rank': int,           # Rank number (1-14)
            'level': int,          # Level within rank (0-10 or 0-9)
            'title': str,          # Rank title (e.g., "Guardian")
            'level_str': str,      # e.g., "1L5"
            'realm_points': int   # Total realm points
        }
        Returns default Rank 1 if calculation fails

    Example:
        >>> info = character_rr_calculate_from_points(
        ...     data_manager, 'Albion', 1500000
        ... )
        >>> info
        {
            'rank': 5,
            'level': 3,
            'title': 'Hero',
            'level_str': '5L3',
            'realm_points': 1500000
        }
    """
    try:
        # Normalize realm_points (handle string with commas/spaces)
        if isinstance(realm_points, str):
            realm_points = int(realm_points.replace(' ', '').replace('\xa0', '').replace(',', ''))

        if not isinstance(realm_points, int):
            realm_points = 0

        # Get rank info from data_manager
        rank_info = data_manager.get_realm_rank_info(realm, realm_points)

        if rank_info:
            return {
                'rank': rank_info.get('rank', 1),
                'level': rank_info.get('level', 1),
                'title': rank_info.get('title', 'Guardian'),
                'level_str': rank_info.get('level_str', '1L1'),
                'realm_points': realm_points
            }
        else:
            # Fallback to Rank 1 Guardian if lookup fails
            logger.warning(f"Could not determine rank for {realm} {realm_points} RP, defaulting to Rank 1")
            return {
                'rank': 1,
                'level': 1,
                'title': 'Guardian',
                'level_str': '1L1',
                'realm_points': realm_points
            }

    except Exception as e:
        logger.error(f"Failed to calculate rank from points ({realm} {realm_points}): {e}")
        return {
            'rank': 1,
            'level': 1,
            'title': 'Guardian',
            'level_str': '1L1',
            'realm_points': 0
        }
