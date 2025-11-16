"""
Language Schema v2 - Hierarchical structure definition and legacy mapping
Similar to config_schema.py but for language files

This module defines:
1. DEFAULT_STRUCTURE_V2: Template hierarchical structure for v2 language files
2. LANGUAGE_LEGACY_MAPPING: Complete v1 (flat) → v2 (hierarchical) key mapping
3. Helper functions for key validation and conversion
"""

# Complete v1 → v2 key mapping (417 keys)
# Format: "old_flat_key": "new.hierarchical.key"
LANGUAGE_LEGACY_MAPPING = {
    # App (3 keys)
    "language_name": "app.language_name",
    "about_message_title": "app.about_title",
    "about_message_content": "app.version_info",
    
    # Window (5 keys)
    "window_title": "window.main_title",
    "welcome_message": "window.welcome_message",
    "character_sheet_title": "window.character_sheet_title",
    "debug_window_title": "window.debug_window_title",
    "configuration_window_title": "window.configuration_window_title",
    
    # Menu - File (6 keys)
    "file_menu_label": "menu.file.label",
    "menu_file": "menu.file.label",
    "menu_file_new_character": "menu.file.new_character",
    "menu_file_search_herald": "menu.file.search_herald",
    "menu_file_settings": "menu.file.settings",
    "configuration_menu_label": "menu.file.settings",
    
    # Menu - Action (4 keys)
    "menu_action": "menu.action.label",
    "menu_action_resistances": "menu.action.resistances",
    "menu_action_armor_management": "menu.action.armor_management",
    "resistances_button": "menu.action.resistances",
    
    # Menu - View (2 keys)
    "view_menu_label": "menu.view.label",
    "menu_view": "menu.view.label",
    "menu_view_columns": "menu.view.columns",
    
    # Menu - Help (7 keys)
    "help_menu_label": "menu.help.label",
    "menu_help": "menu.help.label",
    "menu_help_documentation": "menu.help.documentation",
    "menu_help_create_character": "menu.help.create_character",
    "menu_help_edit_character": "menu.help.edit_character",
    "menu_help_delete_character": "menu.help.delete_character",
    "menu_help_about": "menu.help.about",
    "menu_help_migrate": "menu.help.migrate",
    "menu_help_eden_debug": "menu.help.eden_debug",
    "about_menu_label": "menu.help.about",
    
    # Menu - Tools (2 keys)
    "tools_menu": "menu.tools.label",
    "backup_menu_item": "menu.tools.backup",
    
    # Menu - Bulk Actions (2 keys)
    "bulk_actions_menu_label": "menu.bulk_actions.label",
    "delete_checked_action_label": "menu.bulk_actions.delete_checked",
    
    # Menu - Language (1 key)
    "language_menu_label": "menu.language.label",
    
    # Dialogs - Common titles (4 keys)
    "success_title": "dialogs.titles.success",
    "error_title": "dialogs.titles.error",
    "info_title": "dialogs.titles.info",
    "warning_title": "dialogs.titles.warning",
    
    # Dialogs - New Character (11 keys)
    "new_char_dialog_title": "dialogs.new_character.title",
    "new_char_dialog_prompt": "dialogs.new_character.prompt_name",
    "new_char_realm_prompt": "dialogs.new_character.prompt_realm",
    "new_char_season_prompt": "dialogs.new_character.prompt_season",
    "new_char_server_prompt": "dialogs.new_character.prompt_server",
    "new_char_page_prompt": "dialogs.new_character.prompt_page",
    "new_char_guild_prompt": "dialogs.new_character.prompt_guild",
    "new_char_level_prompt": "dialogs.new_character.prompt_level",
    "new_char_race_prompt": "dialogs.new_character.prompt_race",
    "new_char_class_prompt": "dialogs.new_character.prompt_class",
    "existing_character_label": "dialogs.new_character.existing_character_label",
    
    # Dialogs - Delete Character (2 keys)
    "delete_char_confirm_title": "dialogs.delete_character.confirm_title",
    "delete_char_confirm_message": "dialogs.delete_character.confirm_message",
    "bulk_delete_confirm_message": "dialogs.delete_character.bulk_confirm_message",
    
    # Dialogs - Rename Character (2 keys)
    "rename_char_dialog_title": "dialogs.rename_character.title",
    "rename_char_dialog_prompt": "dialogs.rename_character.prompt",
    
    # Dialogs - Duplicate Character (2 keys)
    "duplicate_char_dialog_title": "dialogs.duplicate_character.title",
    "duplicate_char_dialog_prompt": "dialogs.duplicate_character.prompt",
    
    # Dialogs - About (2 keys)
    "about_dialog_title": "dialogs.about.title",
    "about_dialog_content": "dialogs.about.content",
    
    # Dialogs - Disclaimer (2 keys)
    "disclaimer_title": "dialogs.disclaimer.title",
    "disclaimer_message": "dialogs.disclaimer.message",
    
    # Dialogs - Migration (12 keys)
    "migration_startup_title": "dialogs.migration.startup_title",
    "migration_confirm_title": "dialogs.migration.confirm_title",
    "migration_confirm_message": "dialogs.migration.confirm_message",
    "migration_in_progress": "dialogs.migration.in_progress",
    "migration_success": "dialogs.migration.success",
    "migration_error": "dialogs.migration.error",
    "migration_cancelled_title": "dialogs.migration.cancelled_title",
    "migration_cancelled_message": "dialogs.migration.cancelled_message",
    "migration_dialog_title": "dialogs.migration.confirm_title",
    "migration_startup_message_fr": "dialogs.migration.startup_message_fr",
    "migration_startup_message_en": "dialogs.migration.startup_message_en",
    "migration_startup_message_de": "dialogs.migration.startup_message_de",
    "migration_backup_location": "dialogs.migration.backup_location",
    "migration_warning": "dialogs.migration.warning",
    "migration_question": "dialogs.migration.question",
    "migration_backup_info": "dialogs.migration.backup_info",
    "migration_path_change_title": "dialogs.migration.path_change_title",
    "migration_path_change_message": "dialogs.migration.path_change_message",
    "migration_path_change_question": "dialogs.migration.path_change_question",
    "migration_path_change_later": "dialogs.migration.path_change_later",
    
    # Dialogs - Move Folder (8 keys)
    "move_folder_select_destination": "dialogs.move_folder.select_destination",
    "move_folder_name_title": "dialogs.move_folder.name_title",
    "move_folder_name_message": "dialogs.move_folder.name_message",
    "move_folder_confirm_title": "dialogs.move_folder.confirm_title",
    "move_folder_confirm_message": "dialogs.move_folder.confirm_message",
    "move_folder_success": "dialogs.move_folder.success",
    "move_folder_error": "dialogs.move_folder.error",
    "move_folder_title": "dialogs.move_folder.title",
    "create_folder_confirm_title": "dialogs.move_folder.create_confirm_title",
    "create_folder_confirm_message": "dialogs.move_folder.create_confirm_message",
    
    # Dialogs - Columns Config (4 keys)
    "columns_config_title": "dialogs.columns_config.title",
    "columns_config_desc": "dialogs.columns_config.description",
    "columns_select_all": "dialogs.columns_config.select_all",
    "columns_deselect_all": "dialogs.columns_config.deselect_all",
    
    # Dialogs - Stats Info (2 keys)
    "stats_info_title": "dialogs.stats_info.title",
    "stats_info_message": "dialogs.stats_info.message",
    
    # Buttons (22 keys)
    "create_button_text": "buttons.create",
    "save_button": "buttons.save",
    "cancel_button": "buttons.cancel",
    "close_button": "buttons.close",
    "browse_button": "buttons.browse",
    "move_folder_button": "buttons.move_folder",
    "open_folder_button": "buttons.open_folder",
    "bulk_action_execute_button": "buttons.execute",
    "clear_button_text": "buttons.clear",
    "backup_now_button": "buttons.backup_now",
    "backup_open_folder": "buttons.open_backup_folder",
    "update_rvr_pvp_button": "buttons.update_rvr_pvp",
    "stats_info_button": "buttons.stats_info",
    "version_check_button": "buttons.version_check",
    "version_check_button_checking": "buttons.version_check_checking",
    "version_check_download": "buttons.download",
    "test_debug_button": "buttons.test_debug",
    "exit_button_text": "buttons.exit",
    "action_button_label": "buttons.action",
    "cancel": "buttons.cancel",
    "eden_refresh_button": "buttons.eden_refresh",
    "eden_search_button": "buttons.eden_search",
    "eden_manage_button": "buttons.eden_manage",
    "cookie_generate_button": "buttons.cookie_generate",
    "cookie_delete_button": "buttons.cookie_delete",
    "cookie_browse_button": "buttons.cookie_browse",
    
    # Columns (14 keys)
    "column_name": "columns.name",
    "column_realm": "columns.realm",
    "column_level": "columns.level",
    "column_season": "columns.season",
    "column_server": "columns.server",
    "column_realm_rank": "columns.realm_rank",
    "column_realm_title": "columns.realm_title",
    "column_page": "columns.page",
    "column_guild": "columns.guild",
    "column_class": "columns.class",
    "column_race": "columns.race",
    "column_url": "columns.url",
    "column_action": "columns.action",
    "column_selection": "columns.selection",
    
    # Context Menu (5 keys)
    "context_menu_delete": "context_menu.delete",
    "context_menu_rename": "context_menu.rename",
    "context_menu_duplicate": "context_menu.duplicate",
    "context_menu_armor_management": "context_menu.armor_management",
    "context_menu_update_from_herald": "context_menu.update_from_herald",
    
    # Settings - Navigation (9 keys)
    "settings_nav_general": "settings.navigation.general",
    "settings_nav_themes": "settings.navigation.themes",
    "settings_nav_startup": "settings.navigation.startup",
    "settings_nav_columns": "settings.navigation.columns",
    "settings_nav_herald": "settings.navigation.herald",
    "settings_nav_backup": "settings.navigation.backup",
    "settings_nav_data": "settings.navigation.data",
    "settings_nav_language": "settings.navigation.language",
    "settings_nav_debug": "settings.navigation.debug",
    
    # Settings - Pages - General (2 keys)
    "settings_general_title": "settings.pages.general.title",
    "settings_general_subtitle": "settings.pages.general.subtitle",
    
    # Settings - Pages - Themes (2 keys)
    "settings_themes_title": "settings.pages.themes.title",
    "settings_themes_subtitle": "settings.pages.themes.subtitle",
    
    # Settings - Pages - Startup (3 keys)
    "settings_startup_title": "settings.pages.startup.title",
    "settings_startup_subtitle": "settings.pages.startup.subtitle",
    "settings_startup_info": "settings.pages.startup.info",
    
    # Settings - Pages - Columns (2 keys)
    "settings_columns_title": "settings.pages.columns.title",
    "settings_columns_subtitle": "settings.pages.columns.subtitle",
    
    # Settings - Pages - Herald (3 keys)
    "settings_herald_title": "settings.pages.herald.title",
    "settings_herald_subtitle": "settings.pages.herald.subtitle",
    "settings_herald_info": "settings.pages.herald.info",
    
    # Settings - Pages - Backup (3 keys)
    "settings_backup_title": "settings.pages.backup.title",
    "settings_backup_subtitle": "settings.pages.backup.subtitle",
    "settings_backup_placeholder": "settings.pages.backup.placeholder",
    
    # Settings - Pages - Data (3 keys)
    "settings_data_title": "settings.pages.data.title",
    "settings_data_subtitle": "settings.pages.data.subtitle",
    "settings_data_info": "settings.pages.data.info",
    
    # Settings - Pages - Language (3 keys)
    "settings_language_title": "settings.pages.language.title",
    "settings_language_subtitle": "settings.pages.language.subtitle",
    "settings_language_restart_info": "settings.pages.language.restart_info",
    
    # Settings - Pages - Debug (3 keys)
    "settings_debug_title": "settings.pages.debug.title",
    "settings_debug_subtitle": "settings.pages.debug.subtitle",
    "settings_debug_info": "settings.pages.debug.info",
    
    # Settings - Groups (18 keys)
    "config_paths_group_title": "settings.groups.paths",
    "config_defaults_group_title": "settings.groups.defaults",
    "config_theme_group_title": "settings.groups.theme",
    "config_font_group_title": "settings.groups.font",
    "config_startup_group_title": "settings.groups.startup",
    "config_column_resize_group_title": "settings.groups.column_resize",
    "config_column_visibility_group_title": "settings.groups.column_visibility",
    "config_cookies_group_title": "settings.groups.cookies",
    "config_browser_group_title": "settings.groups.browser",
    "config_armor_group_title": "settings.groups.armor",
    "config_language_group_title": "settings.groups.language",
    "config_debug_app_group_title": "settings.groups.debug_app",
    "config_debug_eden_group_title": "settings.groups.debug_eden",
    "config_season_group_title": "settings.groups.season",
    "config_general_group_title": "settings.groups.general",
    "config_debug_group_title": "settings.groups.debug",
    "config_log_folder_group_title": "settings.groups.log_folder",
    "config_misc_group_title": "settings.groups.misc",
    "config_columns_group_title": "settings.groups.columns",
    "bulk_actions_group_title": "settings.groups.bulk_actions",
    
    # Settings - Labels (18 keys)
    "config_path_label": "settings.labels.character_folder",
    "config_log_path_label": "settings.labels.log_folder",
    "config_armor_path_label": "settings.labels.armor_folder",
    "config_cookies_path_label": "settings.labels.cookies_folder",
    "config_language_label": "settings.labels.language",
    "config_default_server_label": "settings.labels.default_server",
    "config_default_season_label": "settings.labels.default_season",
    "config_default_realm_label": "settings.labels.default_realm",
    "config_theme_label": "settings.labels.theme",
    "config_font_scale_label": "settings.labels.font_scale",
    "config_manual_column_resize_label": "settings.labels.manual_column_resize",
    "config_disable_disclaimer_label": "settings.labels.disable_disclaimer",
    "config_debug_mode_label": "settings.labels.debug_mode",
    "config_show_debug_window_label": "settings.labels.show_debug_window",
    "config_preferred_browser_label": "settings.labels.preferred_browser",
    "config_allow_browser_download_label": "settings.labels.allow_browser_download",
    "config_file_path_label": "settings.labels.config_folder",
    "config_window_content": "settings.labels.window_content",
    
    # Settings - Dialog titles (5 keys)
    "select_folder_dialog_title": "settings.dialog_titles.select_character_folder",
    "select_config_folder_dialog_title": "settings.dialog_titles.select_config_folder",
    "select_log_folder_dialog_title": "settings.dialog_titles.select_log_folder",
    "select_armor_folder_dialog_title": "settings.dialog_titles.select_armor_folder",
    "select_cookies_folder_dialog_title": "settings.dialog_titles.select_cookies_folder",
    
    # Backup (36 keys)
    "backup_settings_title": "backup.window_title",
    "backup_characters_title": "backup.sections.characters",
    "backup_cookies_title": "backup.sections.cookies",
    "backup_armor_title": "backup.sections.armor",
    "backup_enabled_label": "backup.labels.enabled",
    "backup_path_label": "backup.labels.path",
    "backup_compress_label": "backup.labels.compress",
    "backup_retention_label": "backup.labels.retention",
    "backup_max_count_label": "backup.labels.max_count",
    "backup_size_limit_label": "backup.labels.size_limit",
    "backup_auto_delete_label": "backup.labels.auto_delete",
    "backup_usage_label": "backup.labels.usage",
    "backup_recent_label": "backup.labels.recent",
    "backup_total_label": "backup.labels.total",
    "backup_last_label": "backup.labels.last",
    "backup_path_dialog_title": "backup.labels.path_dialog_title",
    "backup_select_folder": "backup.labels.select_folder",
    "backup_success_title": "backup.messages.success_title",
    "backup_success_message": "backup.messages.success_message",
    "backup_error_title": "backup.messages.error_title",
    "backup_error_message": "backup.messages.error_message",
    "backup_no_backup": "backup.messages.no_backup",
    "backup_settings_saved_title": "backup.messages.settings_saved_title",
    "backup_settings_saved_message": "backup.messages.settings_saved_message",
    "backup_settings_error": "backup.messages.settings_error",
    "backup_no_backups_yet": "backup.messages.no_backups_yet",
    "backup_auto_delete_warning_title": "backup.messages.auto_delete_warning_title",
    "backup_auto_delete_warning_message": "backup.messages.auto_delete_warning_message",
    "backup_success": "backup.messages.success",
    "backup_failed": "backup.messages.failed",
    "backup_error": "backup.messages.error",
    "backup_invalid_max_count": "backup.messages.invalid_max_count",
    "backup_invalid_size_limit": "backup.messages.invalid_size_limit",
    "backup_compress_tooltip": "backup.tooltips.compress",
    "backup_max_count_tooltip": "backup.tooltips.max_count",
    "backup_size_limit_tooltip": "backup.tooltips.size_limit",
    "backup_auto_delete_tooltip": "backup.tooltips.auto_delete",
    "backup_now_tooltip": "backup.tooltips.backup_now",
    
    # Character Sheet (38 keys)
    "char_sheet_realm_rank": "character_sheet.stats.realm_rank",
    "armor_group_title": "character_sheet.sections.stats",
    "rvr_section_title": "character_sheet.sections.rvr",
    "pvp_section_title": "character_sheet.sections.pvp",
    "pve_section_title": "character_sheet.sections.pve",
    "achievements_section_title": "character_sheet.sections.achievements",
    "wealth_section_title": "character_sheet.sections.wealth",
    "info_section_title": "character_sheet.sections.info",
    "tower_captures_label": "character_sheet.stats.tower_captures",
    "keep_captures_label": "character_sheet.stats.keep_captures",
    "relic_captures_label": "character_sheet.stats.relic_captures",
    "solo_kills_label": "character_sheet.stats.solo_kills",
    "deathblows_label": "character_sheet.stats.deathblows",
    "kills_label": "character_sheet.stats.kills",
    "dragon_kills_label": "character_sheet.stats.dragon_kills",
    "legion_kills_label": "character_sheet.stats.legion_kills",
    "mini_dragon_kills_label": "character_sheet.stats.mini_dragon_kills",
    "epic_encounters_label": "character_sheet.stats.epic_encounters",
    "epic_dungeons_label": "character_sheet.stats.epic_dungeons",
    "sobekite_label": "character_sheet.stats.sobekite",
    "gold_label": "character_sheet.stats.gold",
    "silver_label": "character_sheet.stats.silver",
    "copper_label": "character_sheet.stats.copper",
    "mithril_label": "character_sheet.stats.mithril",
    "platinum_label": "character_sheet.stats.platinum",
    "total_wealth_label": "character_sheet.stats.total_wealth",
    "pve_coming_soon": "character_sheet.messages.pve_coming_soon",
    "statistics_coming_soon": "character_sheet.messages.statistics_coming_soon",
    
    # Progress - Herald Search (12 keys)
    "herald_search_progress_title": "progress.herald_search.title",
    "herald_search_progress_checking_cookies": "progress.herald_search.checking_cookies",
    "herald_search_progress_init_browser": "progress.herald_search.init_browser",
    "herald_search_progress_loading_cookies": "progress.herald_search.loading_cookies",
    "herald_search_progress_searching": "progress.herald_search.searching",
    "herald_search_progress_loading_page": "progress.herald_search.loading_page",
    "herald_search_progress_extracting": "progress.herald_search.extracting",
    "herald_search_progress_saving": "progress.herald_search.saving",
    "herald_search_progress_formatting": "progress.herald_search.formatting",
    "herald_search_progress_complete": "progress.herald_search.complete",
    "herald_search_progress_closing": "progress.herald_search.closing",
    "herald_search_wait_message": "progress.herald_search.wait_message",
    
    # Progress - Character Update (3 keys)
    "progress_character_update_title": "progress.character_update.title",
    "progress_character_update_desc": "progress.character_update.description",
    "progress_character_update_main_desc": "progress.character_update.main_desc",
    "progress_character_complete": "progress.character_update.complete",
    
    # Progress - Stats Update (3 keys)
    "progress_stats_update_title": "progress.stats_update.title",
    "progress_stats_update_desc": "progress.stats_update.description",
    "progress_stats_complete": "progress.stats_update.complete",
    
    # Progress - Cookie Generation (3 keys)
    "progress_cookie_gen_title": "progress.cookie_generation.title",
    "progress_cookie_gen_desc": "progress.cookie_generation.description",
    "progress_cookie_success": "progress.cookie_generation.success",
    
    # Progress - Steps (32 keys)
    "step_herald_connection_cookies": "progress.steps.herald_connection_cookies",
    "step_herald_connection_init": "progress.steps.herald_connection_init",
    "step_herald_connection_load": "progress.steps.herald_connection_load",
    "step_scraper_init": "progress.steps.scraper_init",
    "step_herald_search_search": "progress.steps.herald_search_search",
    "step_herald_search_load": "progress.steps.herald_search_load",
    "step_herald_search_extract": "progress.steps.herald_search_extract",
    "step_herald_search_save": "progress.steps.herald_search_save",
    "step_herald_search_format": "progress.steps.herald_search_format",
    "step_stats_scraping_rvr": "progress.steps.stats_scraping_rvr",
    "step_stats_scraping_pvp": "progress.steps.stats_scraping_pvp",
    "step_stats_scraping_pve": "progress.steps.stats_scraping_pve",
    "step_stats_scraping_wealth": "progress.steps.stats_scraping_wealth",
    "step_stats_scraping_achievements": "progress.steps.stats_scraping_achievements",
    "step_character_update_extract_name": "progress.steps.character_update_extract_name",
    "step_character_update_init": "progress.steps.character_update_init",
    "step_character_update_load_cookies": "progress.steps.character_update_load_cookies",
    "step_character_update_navigate": "progress.steps.character_update_navigate",
    "step_character_update_wait": "progress.steps.character_update_wait",
    "step_character_update_extract_data": "progress.steps.character_update_extract_data",
    "step_character_update_format": "progress.steps.character_update_format",
    "step_character_update_close": "progress.steps.character_update_close",
    "step_cookie_gen_config": "progress.steps.cookie_gen_config",
    "step_cookie_gen_open": "progress.steps.cookie_gen_open",
    "step_cookie_gen_wait_user": "progress.steps.cookie_gen_wait_user",
    "step_cookie_gen_extract": "progress.steps.cookie_gen_extract",
    "step_cookie_gen_save": "progress.steps.cookie_gen_save",
    "step_cookie_gen_validate": "progress.steps.cookie_gen_validate",
    "step_cleanup": "progress.steps.cleanup",
    
    # Progress - General (1 key)
    "progress_error": "progress.error",
    
    # Additional missing keys (4 keys)
    "config_eden_debug_group_title": "settings.groups.eden_debug",
    "update_char_progress": "progress.character_update.in_progress",
    "migration_rollback_info": "dialogs.migration.rollback_info",
    "migration_data_safe": "dialogs.migration.data_safe",
    
    # Messages - Errors (14 keys)
    "char_name_empty_error": "messages.errors.char_name_empty",
    "char_exists_error": "messages.errors.char_exists",
    "invalid_race_class_combo": "messages.errors.invalid_race_class_combo",
    "update_char_no_url": "messages.errors.update_char_no_url",
    "update_char_error": "messages.errors.update_char_error",
    "move_folder_no_source": "messages.errors.move_folder_no_source",
    "move_folder_destination_exists": "messages.errors.move_folder_destination_exists",
    "herald_validation_timeout_title": "messages.errors.herald_validation_timeout_title",
    "herald_validation_timeout_message": "messages.errors.herald_validation_timeout",
    "herald_validation_failed_title": "messages.errors.herald_validation_failed_title",
    "herald_validation_failed_message": "messages.errors.herald_validation_failed",
    "herald_validation_wait_title": "messages.errors.herald_validation_wait_title",
    "herald_validation_wait_message": "messages.errors.herald_validation_wait_message",
    
    # Messages - Success (11 keys)
    "char_saved_success": "messages.success.char_saved",
    "config_saved_success": "messages.success.config_saved",
    "columns_config_saved": "messages.success.columns_config_saved",
    "move_folder_success": "messages.success.move_folder_success",
    "move_folder_copy_success": "messages.success.move_folder_copy_success",
    "create_folder_success": "messages.success.create_folder_success",
    "move_folder_using_existing": "messages.success.move_folder_using_existing",
    "update_char_success": "messages.success.update_char_success",
    "migration_success_message": "messages.success.migration_success_message",
    
    # Messages - Info (19 keys)
    "creation_cancelled_message": "messages.info.creation_cancelled",
    "update_char_no_changes": "messages.info.update_char_no_changes",
    "update_char_already_uptodate": "messages.info.update_char_already_uptodate",
    "update_char_cancelled": "messages.info.update_char_cancelled",
    "no_characters_selected_warning": "messages.info.no_characters_selected",
    "move_folder_cancelled": "messages.info.move_folder_cancelled",
    "migration_already_done": "messages.info.migration_already_done",
    "migration_not_needed": "messages.info.migration_not_needed",
    "migration_no_characters": "messages.info.migration_no_characters",
    "log_reader_file_not_found": "messages.info.log_reader_file_not_found",
    "herald_import_complete_title": "messages.info.herald_import_complete",
    "herald_import_success": "messages.info.herald_import_success",
    "herald_import_updated": "messages.info.herald_import_updated",
    "herald_import_errors": "messages.info.herald_import_errors",
    "herald_import_more_errors": "messages.info.herald_import_more_errors",
    "herald_import_no_success": "messages.info.herald_import_no_success",
    "update_char_no_changes_title": "messages.info.update_char_no_changes_title",
    "move_folder_in_progress": "messages.info.move_folder_in_progress",
    
    # Messages - Warnings (7 keys)
    "theme_change_restart_message": "messages.warnings.theme_change_restart",
    "cancel_changes_confirm": "messages.warnings.cancel_changes_confirm",
    "move_folder_use_existing": "messages.warnings.move_folder_use_existing",
    "move_folder_merge_question": "messages.warnings.move_folder_merge_question",
    "move_folder_delete_title": "messages.warnings.move_folder_delete_title",
    "move_folder_delete_message": "messages.warnings.move_folder_delete_question",
    
    # Status Bar (2 keys)
    "status_bar_loaded": "status_bar.loaded",
    "status_bar_selection_count": "status_bar.selection_count",
    
    # Debug (13 keys)
    "debug_level_menu": "debug.menu.level",
    "debug_font_size_menu": "debug.menu.font_size",
    "debug_level_all": "debug.levels.all",
    "font_size_small": "debug.font_sizes.small",
    "font_size_medium": "debug.font_sizes.medium",
    "font_size_large": "debug.font_sizes.large",
    "debug_log_pane_title": "debug.panes.logs",
    "debug_errors_pane_title": "debug.panes.errors",
    "debug_details_pane_title": "debug.panes.details",
    "debug_log_reader_pane_title": "debug.panes.log_reader",
    
    # Themes (3 keys)
    "theme_light": "themes.light",
    "theme_dark": "themes.dark",
    "theme_purple": "themes.purple",
    
    # Realms (3 keys)
    "realm_albion": "realms.albion",
    "realm_hibernia": "realms.hibernia",
    "realm_midgard": "realms.midgard",
    
    # Misc (1 key)
    "none_option": "misc.none",
    
    # Tooltips (7 keys)
    "create_char_tooltip": "tooltips.create_char",
    "move_folder_tooltip": "tooltips.move_folder",
    "columns_config_tooltip": "tooltips.columns_config",
    "update_rvr_pvp_tooltip": "tooltips.update_rvr_pvp",
    "stats_info_tooltip": "tooltips.stats_info",
    "columns_config_text": "tooltips.columns_config_text",
    
    # Version Check (8 keys)
    "version_check_current": "version_check.current",
    "version_check_latest": "version_check.latest",
    "version_check_update_available": "version_check.update_available",
    "version_check_up_to_date": "version_check.up_to_date",
    "version_check_error": "version_check.error",
    
    # Additional action labels (2 keys)
    "bulk_action_delete": "menu.bulk_actions.delete",
}


def get_legacy_key(v2_key: str) -> str:
    """
    Get the v1 (flat) key from a v2 (hierarchical) key.
    
    Args:
        v2_key: Hierarchical key (e.g., "window.main_title")
    
    Returns:
        Flat key (e.g., "window_title") or None if not found
    """
    for old_key, new_key in LANGUAGE_LEGACY_MAPPING.items():
        if new_key == v2_key:
            return old_key
    return None


def get_v2_key(v1_key: str) -> str:
    """
    Get the v2 (hierarchical) key from a v1 (flat) key.
    
    Args:
        v1_key: Flat key (e.g., "window_title")
    
    Returns:
        Hierarchical key (e.g., "window.main_title") or None if not found
    """
    return LANGUAGE_LEGACY_MAPPING.get(v1_key)


def is_v2_structure(data: dict) -> bool:
    """
    Check if the language data uses v2 hierarchical structure.
    
    Args:
        data: Language dictionary to check
    
    Returns:
        True if v2 structure, False if v1 (flat)
    """
    # Check for presence of v2 top-level sections
    v2_sections = ["app", "window", "menu", "dialogs", "buttons"]
    return any(section in data for section in v2_sections)
