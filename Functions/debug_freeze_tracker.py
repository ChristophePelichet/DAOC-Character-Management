"""
Debug Freeze Tracker - Minimal Version
Focused on post-dialog freeze investigation
"""

import logging
import time
from datetime import datetime

# Get logger and ensure it's visible
freeze_logger = logging.getLogger("freeze_tracker")
freeze_logger.setLevel(logging.INFO)  # Set to INFO so it shows even in non-debug mode

# Also add a console handler to ensure visibility
if not freeze_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - FREEZE_TRACKER - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    freeze_logger.addHandler(console_handler)


class FreezeTracker:
    """Minimal freeze tracker focused on timing critical operations."""
    
    def __init__(self):
        self.start_time = time.perf_counter()
        self.last_checkpoint_time = self.start_time
        
        freeze_logger.info("=" * 80)
        freeze_logger.info("FREEZE TRACKER START")
        freeze_logger.info(f"Time: {datetime.now().isoformat()}")
        freeze_logger.info("=" * 80)
    
    def checkpoint(self, name: str) -> None:
        """Record a checkpoint with timing."""
        current_time = time.perf_counter()
        elapsed_since_last = (current_time - self.last_checkpoint_time) * 1000
        total_elapsed = (current_time - self.start_time) * 1000
        
        self.last_checkpoint_time = current_time
        
        # Color code based on duration
        warning = ""
        if elapsed_since_last > 3000:
            warning = f" 🔴 CRITICAL {elapsed_since_last:.0f}ms"
        elif elapsed_since_last > 1000:
            warning = f" 🟠 SLOW {elapsed_since_last:.0f}ms"
        elif elapsed_since_last > 500:
            warning = f" 🟡 {elapsed_since_last:.0f}ms"
        
        freeze_logger.info(
            f"[{total_elapsed:7.0f}ms] {name:55s} | Δ {elapsed_since_last:7.0f}ms{warning}"
        )


# Global instance
freeze_tracker = FreezeTracker()
