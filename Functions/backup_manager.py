import os
import json
import shutil
import zipfile
import sys
import logging
from datetime import datetime
from pathlib import Path

class BackupManager:
    """Manages character backups with compression, retention policies, and size limits."""

    def __init__(self, config_manager):
        """
        Initialize the BackupManager.
        
        Args:
            config_manager: ConfigManager instance for accessing app configuration
        """
        self.config_manager = config_manager
        self.backup_dir = self._get_backup_dir()
        self.last_backup_date = None
        self._ensure_backup_dir()
        init_msg = f"[BACKUP] BackupManager initialized - Backup directory: {self.backup_dir}"
        print(init_msg)
        print(init_msg, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        logging.info(init_msg)

    def _get_backup_dir(self):
        """Get backup directory from config or use default."""
        backup_path = self.config_manager.get("backup_path")
        if backup_path:
            return backup_path
        
        # Default: Backup/Characters relative to base path
        from .path_manager import get_base_path
        return os.path.join(get_base_path(), "Backup", "Characters")

    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating backup directory: {e}")

    def should_backup_today(self):
        """
        Check if a backup should be performed today.
        Returns True if last backup was on a different day or no backup exists yet.
        """
        backup_enabled = self.config_manager.get("backup_enabled", True)
        if not backup_enabled:
            return False
        
        last_backup_str = self.config_manager.get("backup_last_date")
        if not last_backup_str:
            return True
        
        try:
            last_backup = datetime.fromisoformat(last_backup_str).date()
            today = datetime.now().date()
            return last_backup != today
        except (ValueError, TypeError):
            return True
    
    def startup_backup(self):
        """
        Perform a daily backup on application startup (once per day).
        This is called when the app starts and no backup was done today.
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        if not self.should_backup_today():
            log_msg = "[BACKUP] Startup: Daily backup already done today"
            print(log_msg)
            print(log_msg, file=sys.stderr)
            sys.stdout.flush()
            sys.stderr.flush()
            logging.info(log_msg)
            return {
                "success": False,
                "message": "Daily backup already done today",
                "file": None
            }
        
        log_msg = "[BACKUP] Startup: Performing daily backup on application start..."
        print(log_msg)
        print(log_msg, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        logging.info(log_msg)
        return self._perform_backup("AUTO-DAILY", reason="Startup Daily")
    
    def trigger_backup_if_needed(self):
        """
        Trigger a backup if conditions are met (once per day, enabled).
        Can be called after actions without checking dates again.
        Returns True if backup was triggered, False otherwise.
        """
        if not self.should_backup_today():
            return False
        
        result = self.backup_characters()
        if result["success"]:
            print(f"[Backup] {result['message']}")
            return True
        else:
            print(f"[Backup Error] {result['message']}")
            return False

    def backup_characters(self):
        """
        Create a backup of the Characters folder.
        Respects retention policy and storage size limits.
        Called by auto-trigger system (once per day).
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        log_msg = "[BACKUP] AUTO-BACKUP triggered - Checking daily limit..."
        print(log_msg)
        print(log_msg, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        
        if not self.should_backup_today():
            msg = "Backup already done today - skipped"
            log_msg = f"[BACKUP] AUTO-BACKUP blocked - {msg}"
            print(log_msg)
            print(log_msg, file=sys.stderr)
            sys.stdout.flush()
            sys.stderr.flush()
            logging.info(log_msg)
            return {
                "success": False,
                "message": msg,
                "file": None
            }

        log_msg = "[BACKUP] AUTO-BACKUP - Daily limit OK, proceeding with backup..."
        print(log_msg)
        print(log_msg, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        return self._perform_backup("AUTO-BACKUP", reason="Action")

    def _perform_backup(self, mode="MANUAL", reason=None):
        """
        Internal method that performs the actual backup.
        
        Args:
            mode: String describing the backup mode (e.g., "AUTO-BACKUP", "MANUAL-BACKUP")
            reason: Optional string describing why the backup was triggered (e.g., "Create", "Delete", "Update")
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        try:
            # Ensure backup directory exists
            self._ensure_backup_dir()

            # Get configuration
            should_compress = self.config_manager.get("backup_compress", True)
            
            # Get characters folder
            char_folder = self.config_manager.get("character_folder")
            if not char_folder or not os.path.exists(char_folder):
                error_msg = "Characters folder not found"
                print(f"[BACKUP] {mode} - ERROR: {error_msg}", file=sys.stderr)
                sys.stderr.flush()
                logging.error(f"[BACKUP] {mode} - {error_msg}")
                return {
                    "success": False,
                    "message": error_msg,
                    "file": None
                }

            # Create backup filename with timestamp and reason
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reason_str = f"_{reason}" if reason else ""
            backup_name = f"backup_characters_{timestamp}{reason_str}"
            
            if should_compress:
                backup_file = os.path.join(self.backup_dir, f"{backup_name}.zip")
                log_msg = f"[BACKUP] {mode} - Creating compressed backup: {os.path.basename(backup_file)}"
                print(log_msg)
                print(log_msg, file=sys.stderr)
                sys.stdout.flush()
                sys.stderr.flush()
                logging.info(log_msg)
                self._create_zip_backup(char_folder, backup_file)
            else:
                backup_file = os.path.join(self.backup_dir, backup_name)
                log_msg = f"[BACKUP] {mode} - Creating uncompressed backup: {os.path.basename(backup_file)}"
                print(log_msg)
                print(log_msg, file=sys.stderr)
                sys.stdout.flush()
                sys.stderr.flush()
                logging.info(log_msg)
                shutil.copytree(char_folder, backup_file, dirs_exist_ok=True)

            # Update last backup date
            self.config_manager.set("backup_last_date", datetime.now().isoformat())
            
            # Apply retention policies
            log_msg = f"[BACKUP] {mode} - Applying retention policies..."
            print(log_msg)
            print(log_msg, file=sys.stderr)
            sys.stdout.flush()
            sys.stderr.flush()
            logging.info(log_msg)
            self._apply_retention_policies()

            success_msg = f"Backup created: {os.path.basename(backup_file)}"
            log_msg = f"[BACKUP] {mode} - SUCCESS: {success_msg}"
            print(log_msg)
            print(log_msg, file=sys.stderr)
            sys.stdout.flush()
            sys.stderr.flush()
            logging.info(log_msg)
            return {
                "success": True,
                "message": success_msg,
                "file": backup_file
            }

        except Exception as e:
            error_msg = f"Backup failed: {str(e)}"
            log_msg = f"[BACKUP] {mode} - ERROR: {error_msg}"
            print(log_msg)
            print(log_msg, file=sys.stderr)
            sys.stdout.flush()
            sys.stderr.flush()
            logging.error(log_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "file": None
            }

    def backup_characters_force(self, reason=None):
        """
        Create a backup of the Characters folder immediately, ignoring daily limit.
        Used when manually triggered from UI or during critical operations.
        Respects retention policy and storage size limits.
        
        Args:
            reason: Optional string describing why the backup was triggered (e.g., "Manual", "Delete", "Update")
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        log_msg = "[BACKUP] MANUAL-BACKUP triggered by user - Bypassing daily limit..."
        print(log_msg)
        print(log_msg, file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        logging.info(log_msg)
        return self._perform_backup("MANUAL-BACKUP", reason=reason or "Manual")

    def _create_zip_backup(self, source_dir, zip_file):
        """Create a compressed ZIP backup of the source directory."""
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

    def _apply_retention_policies(self):
        """Apply retention policy based on storage size limit only."""
        backups = self._get_sorted_backups()
        
        # Apply size retention (size limit only, no count limit)
        size_limit_mb = self.config_manager.get("backup_size_limit_mb", 20)
        if size_limit_mb > 0:
            total_size = sum(self._get_file_size(b) for b in backups)
            size_limit_bytes = size_limit_mb * 1024 * 1024
            
            while total_size > size_limit_bytes and backups:
                oldest = backups.pop()  # Remove oldest
                log_msg = f"[BACKUP] Deleting oldest backup due to size limit: {os.path.basename(oldest)}"
                print(log_msg)
                print(log_msg, file=sys.stderr)
                sys.stdout.flush()
                sys.stderr.flush()
                logging.info(log_msg)
                self._delete_backup(oldest)
                total_size -= self._get_file_size(oldest)

    def _get_sorted_backups(self):
        """Get list of backups sorted by modification time (newest first)."""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                backups.append(item_path)
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return backups

    def _delete_backup(self, backup_path):
        """Delete a backup file or directory."""
        try:
            if os.path.isfile(backup_path):
                os.remove(backup_path)
            elif os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
        except Exception as e:
            print(f"Error deleting backup {backup_path}: {e}")

    def _get_file_size(self, path):
        """Get total size of a file or directory in bytes."""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
            return total
        return 0

    def get_backup_info(self):
        """
        Get information about current backup configuration and usage.
        
        Returns:
            dict: Contains path, compress, size_limit, current_usage, backups list
        """
        backups = self._get_sorted_backups()
        total_size = sum(self._get_file_size(b) for b in backups)
        size_limit_mb = self.config_manager.get("backup_size_limit_mb", 20)

        backup_list = []
        for backup_path in backups[:10]:  # Show last 10
            size = self._get_file_size(backup_path)
            mtime = os.path.getmtime(backup_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            backup_list.append({
                "name": os.path.basename(backup_path),
                "size_mb": round(size / (1024 * 1024), 2),
                "date": mtime_str
            })

        return {
            "path": self.backup_dir,
            "compress": self.config_manager.get("backup_compress", True),
            "size_limit_mb": size_limit_mb,
            "current_usage_mb": round(total_size / (1024 * 1024), 2),
            "backups": backup_list
        }

    def restore_backup(self, backup_path, restore_to=None):
        """
        Restore a backup to the characters folder.
        
        Args:
            backup_path: Path to the backup file or directory
            restore_to: Target directory (default: current characters folder)
            
        Returns:
            dict: Status with 'success' (bool) and 'message' (str)
        """
        try:
            if restore_to is None:
                restore_to = self.config_manager.get("character_folder")
            
            if not restore_to:
                return {
                    "success": False,
                    "message": "Target directory not specified"
                }

            # Create backup of current state before restoring
            backup_current = os.path.join(self.backup_dir, f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copytree(restore_to, backup_current, dirs_exist_ok=True)

            # Clear current directory
            shutil.rmtree(restore_to)
            os.makedirs(restore_to, exist_ok=True)

            # Restore from backup
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(restore_to)
            else:
                shutil.copytree(backup_path, restore_to, dirs_exist_ok=True)

            return {
                "success": True,
                "message": f"Backup restored successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Restore failed: {str(e)}"
            }


# Global backup manager instance
backup_manager = None

def get_backup_manager(config_manager=None):
    """Get or create the global BackupManager instance."""
    global backup_manager
    if backup_manager is None and config_manager is not None:
        backup_manager = BackupManager(config_manager)
    return backup_manager
