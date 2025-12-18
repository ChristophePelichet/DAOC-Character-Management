"""
Character validation and data population functions.

This module provides functions for character class/race validation and dropdown
population based on realm and class selection. All functions support multi-language
display using the language manager.

Functions:
- character_get_classes_for_realm() - Get available classes for a realm
- character_get_races_for_class() - Get available races for a class/realm
- character_handle_realm_change() - Handle realm change with cascade updates
- character_handle_class_change() - Handle class change with race filtering
- character_handle_race_change() - Handle race change (placeholder)

Language Support:
- Supports English, French, and German display names
- Uses config.get("ui.language") to determine display language
- Falls back to English if translation unavailable
"""

import logging
from Functions.config_manager import config

logger = logging.getLogger(__name__)


def character_get_classes_for_realm(data_manager, realm):
    """
    Get available classes for the specified realm.

    Args:
        data_manager: DataManager instance for accessing class/realm data
        realm (str): Realm name (e.g., 'Albion', 'Midgard', 'Hibernia')

    Returns:
        list: List of class dictionaries with name and translated display names

    Example:
        >>> classes = character_get_classes_for_realm(data_manager, 'Albion')
        >>> for cls in classes:
        ...     print(cls['name'])  # Actual name
        ...     print(cls.get('name_fr'))  # French name if available
    """
    try:
        classes = data_manager.get_classes(realm)
        return classes
    except Exception as e:
        logger.error(f"Failed to get classes for realm '{realm}': {e}")
        return []


def character_get_races_for_class(data_manager, realm, class_name=None):
    """
    Get available races for the specified realm and optionally filtered by class.

    Args:
        data_manager: DataManager instance for accessing race/class data
        realm (str): Realm name (e.g., 'Albion', 'Midgard', 'Hibernia')
        class_name (str, optional): Class name to filter races. If None or empty,
                                     returns all races for the realm.

    Returns:
        list: List of race dictionaries with name and translated display names

    Example:
        >>> # Get all races in Albion
        >>> races = character_get_races_for_class(data_manager, 'Albion')
        >>> # Get races available for Paladin in Albion
        >>> races = character_get_races_for_class(data_manager, 'Albion', 'Paladin')
    """
    try:
        if not class_name:
            # No class specified, return all races for realm
            races = data_manager.get_races(realm)
        else:
            # Filter races that can be this class
            races = data_manager.get_available_races_for_class(realm, class_name)

        return races
    except Exception as e:
        logger.error(f"Failed to get races for realm '{realm}', class '{class_name}': {e}")
        return []


def character_populate_classes_combo(combo_widget, data_manager, realm):
    """
    Populate class dropdown with translated class names.

    This is a helper function that updates a QComboBox with classes for a realm.
    It stores the actual class name as item data while displaying translated names.

    Args:
        combo_widget: QComboBox widget to populate
        data_manager: DataManager instance for accessing class data
        realm (str): Realm name

    Returns:
        None (modifies combo_widget in place)

    Example:
        >>> character_populate_classes_combo(self.class_combo, self.data_manager, 'Albion')
    """
    try:
        combo_widget.clear()

        classes = character_get_classes_for_realm(data_manager, realm)
        current_language = config.get("ui.language", "en")

        for cls in classes:
            # Get translated name based on current language
            if current_language == "fr" and "name_fr" in cls:
                display_name = cls["name_fr"]
            elif current_language == "de" and "name_de" in cls:
                display_name = cls["name_de"]
            else:
                display_name = cls["name"]

            # Store actual name as item data for programmatic access
            combo_widget.addItem(display_name, cls["name"])

    except Exception as e:
        logger.error(f"Failed to populate classes combo for realm '{realm}': {e}")


def character_populate_races_combo(combo_widget, data_manager, realm, class_name=None):
    """
    Populate race dropdown with translated race names.

    This is a helper function that updates a QComboBox with races. If class_name
    is provided, shows only races available for that class.

    Args:
        combo_widget: QComboBox widget to populate
        data_manager: DataManager instance for accessing race data
        realm (str): Realm name
        class_name (str, optional): Class name to filter races

    Returns:
        None (modifies combo_widget in place)

    Example:
        >>> character_populate_races_combo(self.race_combo, self.data_manager, 'Albion', 'Paladin')
    """
    try:
        combo_widget.clear()

        races = character_get_races_for_class(data_manager, realm, class_name)
        current_language = config.get("ui.language", "en")

        for race in races:
            # Get translated name based on current language
            if current_language == "fr" and "name_fr" in race:
                display_name = race["name_fr"]
            elif current_language == "de" and "name_de" in race:
                display_name = race["name_de"]
            else:
                display_name = race["name"]

            # Store actual name as item data for programmatic access
            combo_widget.addItem(display_name, race["name"])

    except Exception as e:
        logger.error(f"Failed to populate races combo for realm '{realm}': {e}")


def character_handle_realm_change(combo_realm, combo_class, combo_race, data_manager, character_data):
    """
    Handle realm change with cascade update of class and race dropdowns.

    Called when user changes the realm dropdown. Updates both class and race
    dropdowns to show valid options for the new realm, and updates character_data.

    Args:
        combo_realm: QComboBox widget for realm selection
        combo_class: QComboBox widget for class selection
        combo_race: QComboBox widget for race selection
        data_manager: DataManager instance
        character_data (dict): Character data dictionary to update

    Returns:
        str: New realm name selected

    Example:
        >>> new_realm = character_handle_realm_change(
        ...     self.realm_combo, self.class_combo, self.race_combo,
        ...     self.data_manager, self.character_data
        ... )
    """
    try:
        new_realm = combo_realm.currentText()

        # Update character_data
        character_data['realm'] = new_realm

        # Cascade update: populate classes for new realm
        character_populate_classes_combo(combo_class, data_manager, new_realm)

        # Cascade update: populate races (no class selected yet, so show all)
        character_populate_races_combo(combo_race, data_manager, new_realm)

        logger.debug(f"Realm changed to: {new_realm}")
        return new_realm

    except Exception as e:
        logger.error(f"Failed to handle realm change: {e}")
        return combo_realm.currentText()


def character_handle_class_change(combo_class, combo_race, data_manager, realm, character_data):
    """
    Handle class change with race dropdown filtering.

    Called when user changes the class dropdown. Updates the race dropdown to show
    only races available for the selected class, and updates character_data.

    Args:
        combo_class: QComboBox widget for class selection
        combo_race: QComboBox widget for race selection (to be updated)
        data_manager: DataManager instance
        realm (str): Current realm name
        character_data (dict): Character data dictionary to update

    Returns:
        str: New class name selected

    Example:
        >>> new_class = character_handle_class_change(
        ...     self.class_combo, self.race_combo,
        ...     self.data_manager, self.realm, self.character_data
        ... )
    """
    try:
        class_index = combo_class.currentIndex()

        # Get actual class name (stored as item data)
        if class_index >= 0:
            class_name = combo_class.itemData(class_index)
        else:
            class_name = None

        # Update character_data
        if class_name:
            character_data['class'] = class_name

        # Update race dropdown filtered by new class
        character_populate_races_combo(combo_race, data_manager, realm, class_name)

        logger.debug(f"Class changed to: {class_name}")
        return class_name or ""

    except Exception as e:
        logger.error(f"Failed to handle class change: {e}")
        return combo_class.currentText()


def character_handle_race_change(combo_race, character_data):
    """
    Handle race change in character data.

    Called when user changes the race dropdown. Updates character_data with the
    new race selection.

    Args:
        combo_race: QComboBox widget for race selection
        character_data (dict): Character data dictionary to update

    Returns:
        str: New race name selected

    Note:
        Currently a placeholder - just updates character_data. In the future,
        could trigger banner updates or other race-specific logic.

    Example:
        >>> new_race = character_handle_race_change(
        ...     self.race_combo, self.character_data
        ... )
    """
    try:
        race_index = combo_race.currentIndex()

        # Get actual race name (stored as item data)
        if race_index >= 0:
            race_name = combo_race.itemData(race_index)
        else:
            race_name = None

        # Update character_data
        if race_name:
            character_data['race'] = race_name

        logger.debug(f"Race changed to: {race_name}")
        return race_name or ""

    except Exception as e:
        logger.error(f"Failed to handle race change: {e}")
        return combo_race.currentText()
