"""
Sound manager for controlling audio feedback in the application.

This module provides functionality to manage sound settings and suppress
system sounds when audio feedback is disabled by the user.
"""

import winsound
from Functions.config_manager import config


class SoundManager:
    """Manages application sound settings and audio suppression."""

    @staticmethod
    def should_play_sounds() -> bool:
        """
        Check if sounds should be played based on user configuration.

        Returns:
            bool: True if sounds are enabled, False otherwise.
        """
        return config.get("ui.enable_sounds", True)

    @staticmethod
    def suppress_pending_sounds() -> None:
        """
        Suppress any pending system sounds.

        This clears the sound queue to prevent Windows system beeps
        when message boxes are displayed while sounds are disabled.
        """
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            # Silently ignore any errors in sound suppression
            pass

    @staticmethod
    def get_sound_setting() -> bool:
        """
        Retrieve the current sound setting value.

        Returns:
            bool: Current value of ui.enable_sounds setting.
        """
        return config.get("ui.enable_sounds", True)
