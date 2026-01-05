"""
Herald character data scraping and UI update functions.

This module handles scraping character data from Herald and applying the
scraped statistics to the UI and character data structure. It supports
both complete character updates and partial RvR-only updates.
"""

import logging
from Functions.debug_logging_manager import get_logger, LOGGER_CHARACTER


logger = get_logger(LOGGER_CHARACTER)


def character_herald_update(parent_window, url: str) -> None:
    """
    Update character data from Herald - main entry point.

    This function launches the character update workflow:
    1. Validates the Herald URL format
    2. Launches CharacterUpdateThread for scraping
    3. Shows progress dialog with step tracking
    4. Updates UI with scraped data when complete

    Args:
        parent_window: CharacterSheetWindow instance with UI elements
        url: Herald URL to scrape (with or without protocol)

    Returns:
        None (operates via signals on parent_window)

    Process:
        - URL validation (adds https:// if needed)
        - Disables Herald buttons during update
        - Creates CharacterUpdateThread
        - Shows ProgressStepsDialog with CHARACTER_UPDATE steps
        - Receives update_finished signal when complete
    """
    from UI.ui_sound_manager import SilentMessageBox
    from Functions.language_manager import lang
    from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration

    # Validate URL
    if not url:
        SilentMessageBox.warning(
            parent_window,
            lang.get("update_char_error"),
            lang.get("update_char_no_url")
        )
        return

    # Check if Eden validation is running - button should be disabled
    main_window = parent_window.parent()
    if main_window and hasattr(main_window, 'ui_manager'):
        if hasattr(main_window.ui_manager, 'eden_status_thread'):
            if main_window.ui_manager.eden_status_thread:
                if main_window.ui_manager.eden_status_thread.isRunning():
                    return  # Silent return - button is disabled with tooltip

    # Mark that Herald scraping is in progress BEFORE any URL modification
    parent_window.herald_scraping_in_progress = True

    # Check URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        parent_window.herald_url_edit.setText(url)

    # Disable all buttons during update
    parent_window.update_herald_button.setEnabled(False)
    parent_window.open_herald_button.setEnabled(False)
    parent_window.update_rvr_button.setEnabled(False)

    # Import required components
    from UI.dialogs import CharacterUpdateThread

    # Build steps (CHARACTER_UPDATE)
    steps = StepConfiguration.build_steps(
        StepConfiguration.CHARACTER_UPDATE  # 8 steps: Extract name → Init → Load cookies → Navigate → Wait → Extract data → Format → Close
    )

    # Create progress dialog
    parent_window.progress_dialog = ProgressStepsDialog(
        parent=parent_window,
        title=lang.get("progress_character_update_title", default="🌐 Mise à jour depuis Herald..."),
        steps=steps,
        description=lang.get("progress_character_update_desc", default="Récupération des informations du personnage depuis Eden Herald"),
        show_progress_bar=True,
        determinate_progress=True,
        allow_cancel=False
    )

    # Create update thread
    parent_window.char_update_thread = CharacterUpdateThread(url)

    # Connect thread signals (thread-safe via wrappers)
    parent_window.char_update_thread.step_started.connect(parent_window._on_char_update_step_started)
    parent_window.char_update_thread.step_completed.connect(parent_window._on_char_update_step_completed)
    parent_window.char_update_thread.step_error.connect(parent_window._on_char_update_step_error)
    parent_window.char_update_thread.update_finished.connect(parent_window._on_herald_scraping_finished)

    # Connect rejection before show()
    parent_window.progress_dialog.rejected.connect(parent_window._on_char_update_progress_dialog_closed)

    # Show dialog and start worker
    parent_window.progress_dialog.show()
    parent_window.char_update_thread.start()


def character_herald_update_rvr_stats(parent_window, url: str) -> None:
    """
    Update only RvR statistics from Herald.

    This is a faster alternative to full character update when only
    RvR statistics (tower/keep/relic captures) are needed.

    Args:
        parent_window: CharacterSheetWindow instance with UI elements
        url: Herald URL to scrape (with or without protocol)

    Returns:
        None (operates via signals on parent_window)

    Process:
        - URL validation (adds https:// if needed)
        - Disables button during update
        - Creates StatsUpdateThread (lighter than CharacterUpdateThread)
        - Shows ProgressStepsDialog with STATS_SCRAPING steps
        - Receives stats_updated signal when complete
    """
    from PySide6.QtWidgets import QMessageBox
    from Functions.language_manager import lang
    from UI.progress_dialog_base import ProgressStepsDialog, StepConfiguration

    # Validate URL
    if not url:
        SilentMessageBox.warning(
            parent_window,
            "URL manquante",
            "Veuillez entrer une URL Herald valide pour récupérer les statistiques."
        )
        return

    # Check if Eden validation is running - button should be disabled
    main_window = parent_window.parent()
    if main_window and hasattr(main_window, 'ui_manager'):
        if hasattr(main_window.ui_manager, 'eden_status_thread'):
            if main_window.ui_manager.eden_status_thread:
                if main_window.ui_manager.eden_status_thread.isRunning():
                    return  # Silent return - button is disabled with tooltip

    # Check URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        parent_window.herald_url_edit.setText(url)

    # Disable button during update
    parent_window.update_rvr_button.setEnabled(False)

    # Import required components
    from UI.dialogs import StatsUpdateThread

    # Build steps (SCRAPER_INIT + STATS_SCRAPING + CLEANUP)
    steps = StepConfiguration.build_steps(
        StepConfiguration.SCRAPER_INIT,   # Step 0: Init scraper
        StepConfiguration.STATS_SCRAPING, # Steps 1-5: RvR, PvP, PvE, Wealth, Achievements
        StepConfiguration.CLEANUP         # Step 6: Close browser
    )

    # Create progress dialog
    parent_window.progress_dialog = ProgressStepsDialog(
        parent=parent_window,
        title=lang.get("progress_stats_update_title", default="📊 Mise à jour des statistiques..."),
        steps=steps,
        description=lang.get("progress_stats_update_desc", default="Récupération des statistiques RvR, PvP, PvE et Wealth depuis le Herald Eden"),
        show_progress_bar=True,
        determinate_progress=True,  # Mode with percentage
        allow_cancel=False
    )

    # Create update thread
    parent_window.stats_update_thread = StatsUpdateThread(url)

    # Connect thread signals (thread-safe via wrappers)
    parent_window.stats_update_thread.step_started.connect(parent_window._on_stats_step_started)
    parent_window.stats_update_thread.step_completed.connect(parent_window._on_stats_step_completed)
    parent_window.stats_update_thread.step_error.connect(parent_window._on_stats_step_error)
    parent_window.stats_update_thread.stats_updated.connect(parent_window._on_stats_updated)
    parent_window.stats_update_thread.update_failed.connect(parent_window._on_stats_failed)

    # Connect rejection before show()
    parent_window.progress_dialog.rejected.connect(parent_window._on_stats_progress_dialog_closed)

    # Show dialog and start worker
    parent_window.progress_dialog.show()
    parent_window.stats_update_thread.start()


def character_herald_apply_scraped_stats(
    parent_window,
    result_rvr: dict,
    result_pvp: dict,
    result_pve: dict,
    result_wealth: dict,
    result_achievements: dict
) -> None:
    """
    Apply all scraped stats to UI and character data.

    Updates all statistics fields with complete data from Herald scrape:
    RvR captures, PvP kills, PvE encounters, wealth, and achievements.

    Args:
        parent_window: CharacterSheetWindow instance with UI elements
        result_rvr: Dict with tower/keep/relic capture counts
        result_pvp: Dict with solo_kills, deathblows, kills by realm
        result_pve: Dict with dragon/legion/mini-dragon kills, epic encounters/dungeons, sobekite
        result_wealth: Dict with money amount
        result_achievements: Dict with achievements list and success flag

    Returns:
        None (updates UI labels and character_data)

    Updates in character_data:
        - tower_captures, keep_captures, relic_captures (RvR)
        - solo_kills, deathblows, kills (PvP)
        - solo_kills_alb, _hib, _mid (PvP per realm)
        - deathblows_alb, _hib, _mid (PvP per realm)
        - kills_alb, _hib, _mid (PvP per realm)
        - dragon_kills, legion_kills, mini_dragon_kills (PvE)
        - epic_encounters, epic_dungeons (PvE)
        - sobekite (PvE)
        - money (Wealth)
        - achievements (optional)
    """
    # RvR Captures
    tower = result_rvr['tower_captures']
    keep = result_rvr['keep_captures']
    relic = result_rvr['relic_captures']

    parent_window.tower_captures_label.setText(f"{tower:,}")
    parent_window.keep_captures_label.setText(f"{keep:,}")
    parent_window.relic_captures_label.setText(f"{relic:,}")

    # PvP Stats
    solo_kills = result_pvp['solo_kills']
    solo_kills_alb = result_pvp['solo_kills_alb']
    solo_kills_hib = result_pvp['solo_kills_hib']
    solo_kills_mid = result_pvp['solo_kills_mid']

    deathblows = result_pvp['deathblows']
    deathblows_alb = result_pvp['deathblows_alb']
    deathblows_hib = result_pvp['deathblows_hib']
    deathblows_mid = result_pvp['deathblows_mid']

    kills = result_pvp['kills']
    kills_alb = result_pvp['kills_alb']
    kills_hib = result_pvp['kills_hib']
    kills_mid = result_pvp['kills_mid']

    parent_window.solo_kills_label.setText(f"{solo_kills:,}")
    parent_window.deathblows_label.setText(f"{deathblows:,}")
    parent_window.kills_label.setText(f"{kills:,}")

    parent_window.solo_kills_detail_label.setText(
        f'→ <span style="color: #C41E3A;">Alb</span>: {solo_kills_alb:,}  |  '
        f'<span style="color: #228B22;">Hib</span>: {solo_kills_hib:,}  |  '
        f'<span style="color: #4169E1;">Mid</span>: {solo_kills_mid:,}'
    )
    parent_window.deathblows_detail_label.setText(
        f'→ <span style="color: #C41E3A;">Alb</span>: {deathblows_alb:,}  |  '
        f'<span style="color: #228B22;">Hib</span>: {deathblows_hib:,}  |  '
        f'<span style="color: #4169E1;">Mid</span>: {deathblows_mid:,}'
    )
    parent_window.kills_detail_label.setText(
        f'→ <span style="color: #C41E3A;">Alb</span>: {kills_alb:,}  |  '
        f'<span style="color: #228B22;">Hib</span>: {kills_hib:,}  |  '
        f'<span style="color: #4169E1;">Mid</span>: {kills_mid:,}'
    )

    # PvE Stats
    dragon_kills = result_pve['dragon_kills']
    legion_kills = result_pve['legion_kills']
    mini_dragon_kills = result_pve['mini_dragon_kills']
    epic_encounters = result_pve['epic_encounters']
    epic_dungeons = result_pve['epic_dungeons']
    sobekite = result_pve['sobekite']

    parent_window.dragon_kills_value.setText(f"{dragon_kills:,}")
    parent_window.legion_kills_value.setText(f"{legion_kills:,}")
    parent_window.mini_dragon_kills_value.setText(f"{mini_dragon_kills:,}")
    parent_window.epic_encounters_value.setText(f"{epic_encounters:,}")
    parent_window.epic_dungeons_value.setText(f"{epic_dungeons:,}")
    parent_window.sobekite_value.setText(f"{sobekite:,}")

    # Wealth
    money = result_wealth['money']
    parent_window.money_label.setText(str(money))

    # Achievements (optional)
    if result_achievements.get('success'):
        achievements = result_achievements['achievements']
        parent_window._update_achievements_display(achievements)
        parent_window.character_data['achievements'] = achievements

    # Update character_data
    parent_window.character_data['tower_captures'] = tower
    parent_window.character_data['keep_captures'] = keep
    parent_window.character_data['relic_captures'] = relic

    parent_window.character_data['solo_kills'] = solo_kills
    parent_window.character_data['deathblows'] = deathblows
    parent_window.character_data['kills'] = kills
    parent_window.character_data['solo_kills_alb'] = solo_kills_alb
    parent_window.character_data['solo_kills_hib'] = solo_kills_hib
    parent_window.character_data['solo_kills_mid'] = solo_kills_mid
    parent_window.character_data['deathblows_alb'] = deathblows_alb
    parent_window.character_data['deathblows_hib'] = deathblows_hib
    parent_window.character_data['deathblows_mid'] = deathblows_mid
    parent_window.character_data['kills_alb'] = kills_alb
    parent_window.character_data['kills_hib'] = kills_hib
    parent_window.character_data['kills_mid'] = kills_mid

    parent_window.character_data['dragon_kills'] = dragon_kills
    parent_window.character_data['legion_kills'] = legion_kills
    parent_window.character_data['mini_dragon_kills'] = mini_dragon_kills
    parent_window.character_data['epic_encounters'] = epic_encounters
    parent_window.character_data['epic_dungeons'] = epic_dungeons
    parent_window.character_data['sobekite'] = sobekite

    parent_window.character_data['money'] = money


def character_herald_apply_partial_stats(
    parent_window,
    result_rvr: dict,
    result_pvp: dict,
    result_pve: dict,
    result_wealth: dict,
    result_achievements: dict
) -> None:
    """
    Apply only partial stats to UI and character data.

    Updates only specific statistics fields. Used for selective updates
    like RvR-only refreshes. Saves character data when updates are made.

    Args:
        parent_window: CharacterSheetWindow instance with UI elements
        result_rvr: Dict with tower/keep/relic capture counts (optional)
        result_pvp: Dict with PvP stats (optional)
        result_pve: Dict with PvE stats (optional)
        result_wealth: Dict with money amount (optional)
        result_achievements: Dict with achievements (optional)

    Returns:
        None (updates UI labels and character_data, saves when needed)

    Updates behavior:
        - Only updates fields if result_*['success'] is True
        - Saves character data after each successful update
        - Calls save_character() after each stat type update
    """
    from Functions.character_manager import save_character

    # Update RvR captures if successful
    if result_rvr and result_rvr.get('success'):
        tower = result_rvr['tower_captures']
        keep = result_rvr['keep_captures']
        relic = result_rvr['relic_captures']

        parent_window.tower_captures_label.setText(f"{tower:,}")
        parent_window.keep_captures_label.setText(f"{keep:,}")
        parent_window.relic_captures_label.setText(f"{relic:,}")

        parent_window.character_data['tower_captures'] = tower
        parent_window.character_data['keep_captures'] = keep
        parent_window.character_data['relic_captures'] = relic

        save_character(parent_window.character_data, allow_overwrite=True)

    # Update PvP stats if successful
    if result_pvp and result_pvp.get('success'):
        solo_kills = result_pvp['solo_kills']
        solo_kills_alb = result_pvp['solo_kills_alb']
        solo_kills_hib = result_pvp['solo_kills_hib']
        solo_kills_mid = result_pvp['solo_kills_mid']

        deathblows = result_pvp['deathblows']
        deathblows_alb = result_pvp['deathblows_alb']
        deathblows_hib = result_pvp['deathblows_hib']
        deathblows_mid = result_pvp['deathblows_mid']

        kills = result_pvp['kills']
        kills_alb = result_pvp['kills_alb']
        kills_hib = result_pvp['kills_hib']
        kills_mid = result_pvp['kills_mid']

        parent_window.solo_kills_label.setText(f"{solo_kills:,}")
        parent_window.deathblows_label.setText(f"{deathblows:,}")
        parent_window.kills_label.setText(f"{kills:,}")

        parent_window.solo_kills_detail_label.setText(
            f'→ <span style="color: #C41E3A;">Alb</span>: {solo_kills_alb:,}  |  '
            f'<span style="color: #228B22;">Hib</span>: {solo_kills_hib:,}  |  '
            f'<span style="color: #4169E1;">Mid</span>: {solo_kills_mid:,}'
        )
        parent_window.deathblows_detail_label.setText(
            f'→ <span style="color: #C41E3A;">Alb</span>: {deathblows_alb:,}  |  '
            f'<span style="color: #228B22;">Hib</span>: {deathblows_hib:,}  |  '
            f'<span style="color: #4169E1;">Mid</span>: {deathblows_mid:,}'
        )
        parent_window.kills_detail_label.setText(
            f'→ <span style="color: #C41E3A;">Alb</span>: {kills_alb:,}  |  '
            f'<span style="color: #228B22;">Hib</span>: {kills_hib:,}  |  '
            f'<span style="color: #4169E1;">Mid</span>: {kills_mid:,}'
        )

        parent_window.character_data['solo_kills'] = solo_kills
        parent_window.character_data['deathblows'] = deathblows
        parent_window.character_data['kills'] = kills
        parent_window.character_data['solo_kills_alb'] = solo_kills_alb
        parent_window.character_data['solo_kills_hib'] = solo_kills_hib
        parent_window.character_data['solo_kills_mid'] = solo_kills_mid
        parent_window.character_data['deathblows_alb'] = deathblows_alb
        parent_window.character_data['deathblows_hib'] = deathblows_hib
        parent_window.character_data['deathblows_mid'] = deathblows_mid
        parent_window.character_data['kills_alb'] = kills_alb
        parent_window.character_data['kills_hib'] = kills_hib
        parent_window.character_data['kills_mid'] = kills_mid

        save_character(parent_window.character_data, allow_overwrite=True)

    # Update PvE stats if successful
    if result_pve and result_pve.get('success'):
        dragon_kills = result_pve['dragon_kills']
        legion_kills = result_pve['legion_kills']
        mini_dragon_kills = result_pve['mini_dragon_kills']
        epic_encounters = result_pve['epic_encounters']
        epic_dungeons = result_pve['epic_dungeons']
        sobekite = result_pve['sobekite']

        parent_window.dragon_kills_value.setText(f"{dragon_kills:,}")
        parent_window.legion_kills_value.setText(f"{legion_kills:,}")
        parent_window.mini_dragon_kills_value.setText(f"{mini_dragon_kills:,}")
        parent_window.epic_encounters_value.setText(f"{epic_encounters:,}")
        parent_window.epic_dungeons_value.setText(f"{epic_dungeons:,}")
        parent_window.sobekite_value.setText(f"{sobekite:,}")

        parent_window.character_data['dragon_kills'] = dragon_kills
        parent_window.character_data['legion_kills'] = legion_kills
        parent_window.character_data['mini_dragon_kills'] = mini_dragon_kills
        parent_window.character_data['epic_encounters'] = epic_encounters
        parent_window.character_data['epic_dungeons'] = epic_dungeons
        parent_window.character_data['sobekite'] = sobekite

        save_character(parent_window.character_data, allow_overwrite=True)

    # Update wealth if successful
    if result_wealth and result_wealth.get('success'):
        money = result_wealth['money']
        parent_window.money_label.setText(str(money))
        parent_window.character_data['money'] = money

        save_character(parent_window.character_data, allow_overwrite=True)

    # Update achievements if successful
    if result_achievements and result_achievements.get('success'):
        achievements = result_achievements['achievements']
        parent_window._update_achievements_display(achievements)
        parent_window.character_data['achievements'] = achievements

        save_character(parent_window.character_data, allow_overwrite=True)
