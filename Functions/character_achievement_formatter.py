"""Character Achievement Formatter Module - Handle achievements display functionality.

This module provides functions for formatting and displaying character achievements.
Extracted from UI/dialogs.py CharacterSheetWindow class (Phase 11 refactoring).

Functions:
    - character_update_achievements_display: Format and display achievements list with 2-column layout

Naming Convention: character_{action}_{object}

Language: English (code and comments)
"""

from PySide6.QtWidgets import (
    QHBoxLayout, QGridLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

from Functions.theme_manager import get_scaled_size
from Functions.logging_manager import get_logger, LOGGER_UI

# Get logger instance
logger = get_logger(LOGGER_UI)


def character_update_achievements_display(parent_window, achievements_list) -> None:
    """Update achievements display with the provided list.

    Displays achievements in a 2-column layout with vertical separator.
    Each column shows up to 8 achievements with title, progress, and current tier.
    Clears previous widgets and rebuilds layout from scratch.

    Process:
        1. Clear existing widgets from achievements_container_layout
        2. If no achievements, show placeholder
        3. Split achievements into 2 groups of 8 (first 8, rest)
        4. Create first grid layout (left column) with styling
        5. Add vertical separator line if second column exists
        6. Create second grid layout (right column) with styling
        7. Add columns to main layout with stretch factors
        8. Add final stretch to push content up

    Parameters:
        parent_window: CharacterSheetWindow instance with:
            - achievements_container_layout: QVBoxLayout for container
        achievements_list: List of dicts with keys:
            - 'title': Achievement name (str)
            - 'progress': Progress indicator like "5/10" (str)
            - 'current': Current tier or rank, or "None" (str)

    Returns:
        None (updates parent_window.achievements_container_layout in-place)

    Layout Structure:
        ┌─────────────────────────────────────────────────────┐
        │  Title 1        5/10  (Tier)  │  Title 9        2/10  (Tier) │
        │  Title 2        3/10  (Tier)  │  Title 10       0/10         │
        │  Title 3        8/10  (Tier)  │  Title 11       1/10  (Tier) │
        │  ...                         │  ...                         │
        └─────────────────────────────────────────────────────┘

    Example:
        >>> achievements = [
        ...     {'title': 'First Victory', 'progress': '1/1', 'current': 'Gold'},
        ...     {'title': 'Realm Rank 5', 'progress': '5/5', 'current': None},
        ... ]
        >>> character_update_achievements_display(window, achievements)
        >>> # Layout is updated with achievements in 2 columns

    Styling Details:
        - Title font: 9pt, left aligned
        - Progress: Bold, 9pt, right aligned
        - Current tier: 8pt, gray, italic, left aligned
        - Separator: Vertical line with light gray color (#cccccc)
        - Empty state: Gray italic dash (—)

    Error Handling:
        - Missing keys handled with .get() and defaults
        - "None" string tier ignored (treated as empty)
        - Empty list shows placeholder
        - Grid layouts maintain consistent spacing
    """
    try:
        # Clear existing widgets
        while parent_window.achievements_container_layout.count():
            item = parent_window.achievements_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layouts
                while item.layout().count():
                    nested_item = item.layout().takeAt(0)
                    if nested_item.widget():
                        nested_item.widget().deleteLater()

        if not achievements_list or len(achievements_list) == 0:
            # Show placeholder
            placeholder = QLabel("—")
            placeholder.setStyleSheet("color: gray; font-style: italic;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            parent_window.achievements_container_layout.addWidget(placeholder)
            parent_window.achievements_container_layout.addStretch()
            return

        # Create horizontal layout for 2 columns
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(15)

        # Split achievements into 2 groups of 8 (or less)
        mid_point = 8
        first_column = achievements_list[:mid_point]
        second_column = achievements_list[mid_point:]

        # === First column (left) ===
        first_grid = QGridLayout()
        first_grid.setHorizontalSpacing(10)
        first_grid.setVerticalSpacing(2)
        first_grid.setColumnStretch(0, 3)  # Title column
        first_grid.setColumnStretch(1, 0)  # Progress column (fixed)
        first_grid.setColumnStretch(2, 2)  # Current tier column

        for row, achievement in enumerate(first_column):
            title = achievement.get('title', 'Unknown')
            progress = achievement.get('progress', '0/0')
            current_tier = achievement.get('current', None)

            # Title
            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"font-size: {get_scaled_size(9):.1f}pt;"
            )
            first_grid.addWidget(
                title_label, row, 0, Qt.AlignmentFlag.AlignLeft
            )

            # Progress
            progress_label = QLabel(progress)
            progress_label.setStyleSheet(
                f"font-weight: bold; font-size: {get_scaled_size(9):.1f}pt;"
            )
            first_grid.addWidget(
                progress_label, row, 1, Qt.AlignmentFlag.AlignRight
            )

            # Current tier
            if current_tier and current_tier != "None":
                current_label = QLabel(f"({current_tier})")
                current_label.setStyleSheet(
                    f"font-size: {get_scaled_size(8):.1f}pt; "
                    f"color: #6c757d; font-style: italic;"
                )
                first_grid.addWidget(
                    current_label, row, 2, Qt.AlignmentFlag.AlignLeft
                )

        columns_layout.addLayout(first_grid, 1)  # Stretch factor 1

        # === Vertical separator ===
        if second_column:  # Only add separator if there's a second column
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.VLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("color: #cccccc;")
            columns_layout.addWidget(separator)

        # === Second column (right) ===
        if second_column:
            second_grid = QGridLayout()
            second_grid.setHorizontalSpacing(10)
            second_grid.setVerticalSpacing(2)
            second_grid.setColumnStretch(0, 3)  # Title column
            second_grid.setColumnStretch(1, 0)  # Progress column (fixed)
            second_grid.setColumnStretch(2, 2)  # Current tier column

            for row, achievement in enumerate(second_column):
                title = achievement.get('title', 'Unknown')
                progress = achievement.get('progress', '0/0')
                current_tier = achievement.get('current', None)

                # Title
                title_label = QLabel(title)
                title_label.setStyleSheet(
                    f"font-size: {get_scaled_size(9):.1f}pt;"
                )
                second_grid.addWidget(
                    title_label, row, 0, Qt.AlignmentFlag.AlignLeft
                )

                # Progress
                progress_label = QLabel(progress)
                progress_label.setStyleSheet(
                    f"font-weight: bold; font-size: {get_scaled_size(9):.1f}pt;"
                )
                second_grid.addWidget(
                    progress_label, row, 1, Qt.AlignmentFlag.AlignRight
                )

                # Current tier
                if current_tier and current_tier != "None":
                    current_label = QLabel(f"({current_tier})")
                    current_label.setStyleSheet(
                        f"font-size: {get_scaled_size(8):.1f}pt; "
                        f"color: #6c757d; font-style: italic;"
                    )
                    second_grid.addWidget(
                        current_label, row, 2, Qt.AlignmentFlag.AlignLeft
                    )

            columns_layout.addLayout(second_grid, 1)  # Stretch factor 1

        # Add columns layout to container
        parent_window.achievements_container_layout.addLayout(columns_layout)

        # Add stretch at the end
        parent_window.achievements_container_layout.addStretch()

    except Exception as e:
        logger.error(f"Error updating achievements display: {e}")
        # Show placeholder on error
        placeholder = QLabel("—")
        placeholder.setStyleSheet("color: gray; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_window.achievements_container_layout.addWidget(placeholder)
        parent_window.achievements_container_layout.addStretch()
