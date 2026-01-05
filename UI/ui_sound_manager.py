"""
UI wrapper for silent message boxes.

This module provides a SilentMessageBox class that respects the application's
sound settings, replacing standard QMessageBox with custom dialogs when
sounds are disabled to prevent system beeps.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, QSize
from Functions.sound_manager import SoundManager
from Functions.language_manager import lang


class SilentMessageBox:
    """
    A message box wrapper that respects the sound settings.

    When sounds are disabled, uses a custom QDialog instead of QMessageBox
    to prevent system beeps from Windows.
    """

    @staticmethod
    def information(parent, title: str, text: str) -> int:
        """
        Show an information message box.

        Args:
            parent: Parent widget
            title: Dialog title
            text: Message text

        Returns:
            int: Button result code (StandardButton.Ok)
        """
        if SoundManager.should_play_sounds():
            from PySide6.QtWidgets import QMessageBox
            return QMessageBox.information(parent, title, text)
        else:
            SoundManager.suppress_pending_sounds()
            # Additional sound suppression for robustness
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
            return SilentMessageBox._create_custom_dialog(
                parent, title, text, "information"
            )

    @staticmethod
    def warning(parent, title: str, text: str) -> int:
        """
        Show a warning message box.

        Args:
            parent: Parent widget
            title: Dialog title
            text: Message text

        Returns:
            int: Button result code (StandardButton.Ok)
        """
        if SoundManager.should_play_sounds():
            from PySide6.QtWidgets import QMessageBox
            return QMessageBox.warning(parent, title, text)
        else:
            SoundManager.suppress_pending_sounds()
            # Additional sound suppression for robustness
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
            return SilentMessageBox._create_custom_dialog(
                parent, title, text, "warning"
            )

    @staticmethod
    def critical(parent, title: str, text: str) -> int:
        """
        Show a critical error message box.

        Args:
            parent: Parent widget
            title: Dialog title
            text: Message text

        Returns:
            int: Button result code (StandardButton.Ok)
        """
        if SoundManager.should_play_sounds():
            from PySide6.QtWidgets import QMessageBox
            return QMessageBox.critical(parent, title, text)
        else:
            SoundManager.suppress_pending_sounds()
            # Additional sound suppression for robustness
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
            return SilentMessageBox._create_custom_dialog(
                parent, title, text, "critical"
            )

    @staticmethod
    def question(parent, title: str, text: str, buttons=None, defaultButton=None) -> int:
        """
        Show a question message box with Yes/No buttons.

        Args:
            parent: Parent widget
            title: Dialog title
            text: Message text
            buttons: Qt button flags (optional, for compatibility)
            defaultButton: Default button (optional, for compatibility)

        Returns:
            int: Button result code (StandardButton.Yes or StandardButton.No)
        """
        if SoundManager.should_play_sounds():
            from PySide6.QtWidgets import QMessageBox
            if buttons is not None and defaultButton is not None:
                return QMessageBox.question(parent, title, text, buttons, defaultButton)
            elif buttons is not None:
                return QMessageBox.question(parent, title, text, buttons)
            else:
                return QMessageBox.question(parent, title, text)
        else:
            SoundManager.suppress_pending_sounds()
            # Additional sound suppression for robustness
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
            return SilentMessageBox._create_custom_dialog(
                parent, title, text, "question"
            )

    @staticmethod
    def _create_custom_dialog(
        parent, title: str, text: str, dialog_type: str
    ) -> int:
        """
        Create a custom silent dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            text: Message text
            dialog_type: Type of dialog (information, warning, critical, question)

        Returns:
            int: Button result code (StandardButton.Ok/Yes or StandardButton.No)
        """
        from PySide6.QtWidgets import QMessageBox

        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(400)
        dialog.setModal(True)

        layout = QVBoxLayout()

        # Add message text
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if dialog_type == "question":
            yes_button = QPushButton(lang.get("dialog_yes", "Yes"))
            no_button = QPushButton(lang.get("dialog_no", "No"))

            yes_button.clicked.connect(
                lambda: dialog.done(QMessageBox.StandardButton.Yes)
            )
            no_button.clicked.connect(
                lambda: dialog.done(QMessageBox.StandardButton.No)
            )

            button_layout.addWidget(yes_button)
            button_layout.addWidget(no_button)
        else:
            ok_button = QPushButton(lang.get("dialog_ok", "OK"))
            ok_button.clicked.connect(
                lambda: dialog.done(QMessageBox.StandardButton.Ok)
            )
            button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        result = dialog.exec()
        return result if result > 0 else QMessageBox.StandardButton.Ok
