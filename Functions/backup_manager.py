import os
import json
import shutil
import zipfile
import sys
import logging
from datetime import datetime
from pathlib import Path
from .logging_manager import get_logger, log_with_action, LOGGER_BACKUP, LoggerFactory

# Fix for PyInstaller --noconsole mode: sys.stderr can be None
if sys.stderr is None:
    sys.stderr = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')

class BackupManager:
    """Manages character backups with compression, retention policies, and size limits."""

    def __init__(self, config_manager):
        """
        Initialize the BackupManager.
        
        Args:
            config_manager: ConfigManager instance for accessing app configuration
        """
        self.config_manager = config_manager
        self.logger = get_logger(LOGGER_BACKUP)
        self.backup_dir = self._get_backup_dir()
        self.last_backup_date = None
        self._ensure_backup_dir()
        
        init_msg = f"BackupManager initialized - Backup directory: {self.backup_dir}"
        log_with_action(self.logger, "info", init_msg, action="INIT")
        print(f"[{LOGGER_BACKUP.upper()}] {init_msg}", file=sys.stderr)
        sys.stderr.flush()

    def _get_backup_dir(self):
        """Get backup directory from config or use default."""
        backup_path = self.config_manager.get("backup_path")
        if backup_path:
            return backup_path
        
        # Default: Backup/Characters relative to base path
        from .path_manager import get_base_path
        return os.path.join(get_base_path(), "Backup", "Characters")

    def _get_cookies_backup_dir(self):
        """Get cookies backup directory from config or use default."""
        cookies_backup_path = self.config_manager.get("cookies_backup_path")
        if cookies_backup_path:
            return cookies_backup_path
        
        # Default: Backup/Cookies relative to base path
        from .path_manager import get_base_path
        return os.path.join(get_base_path(), "Backup", "Cookies")

    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        try:
            backup_dir_existed = os.path.exists(self.backup_dir)
            os.makedirs(self.backup_dir, exist_ok=True)
            if not backup_dir_existed:
                log_with_action(self.logger, "info", f"Created backup directory: {self.backup_dir}", action="DIRECTORY")
            else:
                log_with_action(self.logger, "debug", f"Backup directory already exists: {self.backup_dir}", action="DIRECTORY")
        except Exception as e:
            error_msg = f"Error creating backup directory: {e}"
            log_with_action(self.logger, "error", error_msg, action="ERROR")
            print(f"[{LOGGER_BACKUP.upper()}] {error_msg}", file=sys.stderr)

    def _ensure_cookies_backup_dir(self):
        """Create cookies backup directory if it doesn't exist."""
        cookies_backup_dir = self._get_cookies_backup_dir()
        try:
            cookies_backup_dir_existed = os.path.exists(cookies_backup_dir)
            os.makedirs(cookies_backup_dir, exist_ok=True)
            if not cookies_backup_dir_existed:
                log_with_action(self.logger, "info", f"Created cookies backup directory: {cookies_backup_dir}", action="DIRECTORY")
            else:
                log_with_action(self.logger, "debug", f"Cookies backup directory already exists: {cookies_backup_dir}", action="DIRECTORY")
        except Exception as e:
            error_msg = f"Error creating cookies backup directory: {e}"
            log_with_action(self.logger, "error", error_msg, action="ERROR")
            print(f"[{LOGGER_BACKUP.upper()}] {error_msg}", file=sys.stderr)

    def should_backup_today(self):
        """
        Check if a backup should be performed today.
        Returns True if last backup was on a different day or no backup exists yet.
        """
        backup_enabled = self.config_manager.get("backup_enabled", True)
        if not backup_enabled:
            log_with_action(self.logger, "debug", "Backup is disabled in configuration", action="CHECK")
            return False
        
        last_backup_str = self.config_manager.get("backup_last_date")
        if not last_backup_str:
            log_with_action(self.logger, "debug", "No previous backup found - backup needed", action="CHECK")
            return True
        
        try:
            last_backup = datetime.fromisoformat(last_backup_str).date()
            today = datetime.now().date()
            should_backup = last_backup != today
            log_with_action(self.logger, "debug", f"Backup check: last={last_backup}, today={today}, needed={should_backup}", action="CHECK")
            return should_backup
        except (ValueError, TypeError) as e:
            log_with_action(self.logger, "warning", f"Invalid backup date format: {e}", action="CHECK")
            return True
    
    def startup_backup(self):
        """
        Perform a daily backup on application startup (once per day).
        This is called when the app starts and no backup was done today.
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        if not self.should_backup_today():
            log_with_action(self.logger, "info", "Daily backup already done today", action="STARTUP")
            return {
                "success": False,
                "message": "Daily backup already done today",
                "file": None
            }
        
        log_with_action(self.logger, "info", "Performing daily backup on application start...", action="STARTUP")
        return self._perform_backup("AUTO-DAILY", reason="Startup Daily")
    
    def trigger_backup_if_needed(self):
        """
        Trigger a backup if conditions are met (once per day, enabled).
        Can be called after actions without checking dates again.
        Returns True if backup was triggered, False otherwise.
        """
        if not self.should_backup_today():
            log_with_action(self.logger, "debug", "Backup not needed or disabled", action="TRIGGER")
            return False
        
        log_with_action(self.logger, "info", "Triggering automatic backup", action="TRIGGER")
        result = self.backup_characters()
        if result["success"]:
            log_with_action(self.logger, "info", result['message'], action="TRIGGER")
            return True
        else:
            log_with_action(self.logger, "error", result['message'], action="TRIGGER")
            return False

    def backup_characters(self):
        """
        Create a backup of the Characters folder.
        Respects retention policy and storage size limits.
        Called by auto-trigger system (once per day).
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        log_with_action(self.logger, "info", "AUTO-BACKUP triggered - Checking daily limit...", action="AUTO_TRIGGER")
        
        if not self.should_backup_today():
            msg = "Backup already done today - skipped"
            log_with_action(self.logger, "info", msg, action="AUTO_BLOCKED")
            return {
                "success": False,
                "message": msg,
                "file": None
            }

        log_with_action(self.logger, "info", "Daily limit OK, proceeding with backup...", action="AUTO_PROCEED")
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
            
            # Get characters folder - use get_character_dir() which has proper fallback
            from Functions.character_manager import get_character_dir
            char_folder = get_character_dir()
            
            if not os.path.exists(char_folder):
                # This is normal on first startup - folder will be created when first character is added
                info_msg = "Characters folder does not exist yet (normal on first startup)"
                log_with_action(self.logger, "info", info_msg, action="CHECK")
                return {
                    "success": False,
                    "message": "Characters folder not found",
                    "file": None
                }

            # Create backup filename with timestamp and reason
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reason_str = f"_{reason}" if reason else ""
            backup_name = f"backup_characters_{timestamp}{reason_str}"
            
            if should_compress:
                backup_file = os.path.join(self.backup_dir, f"{backup_name}.zip")
                log_with_action(self.logger, "info", f"Creating compressed backup: {os.path.basename(backup_file)}", action="ZIP")
                self._create_zip_backup(char_folder, backup_file)
            else:
                backup_file = os.path.join(self.backup_dir, backup_name)
                log_with_action(self.logger, "info", f"Creating uncompressed backup: {os.path.basename(backup_file)}", action="COPY")
                shutil.copytree(char_folder, backup_file, dirs_exist_ok=True)

            # Update last backup date
            self.config_manager.set("backup_last_date", datetime.now().isoformat())
            
            # Apply retention policies
            log_with_action(self.logger, "info", "Applying retention policies...", action="RETENTION")
            self._apply_retention_policies()

            success_msg = f"Backup created: {os.path.basename(backup_file)}"
            log_with_action(self.logger, "info", success_msg, action="SUCCESS")
            return {
                "success": True,
                "message": success_msg,
                "file": backup_file
            }

        except Exception as e:
            error_msg = f"Backup failed: {str(e)}"
            log_with_action(self.logger, "error", error_msg, action="ERROR")
            logging.error(f"Exception during backup: {str(e)}", exc_info=True)
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
        log_with_action(self.logger, "info", "MANUAL-BACKUP triggered - Bypassing daily limit...", action="MANUAL_TRIGGER")
        return self._perform_backup("MANUAL-BACKUP", reason=reason or "Manual")

    def backup_cookies(self):
        """
        Create a backup of the Eden cookies folder.
        Respects retention policy and storage size limits.
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        log_with_action(self.logger, "info", "COOKIES-BACKUP triggered - Checking daily limit...", action="AUTO_TRIGGER_COOKIES")
        
        if not self.should_cookies_backup_today():
            msg = "Cookies backup already done today - skipped"
            log_with_action(self.logger, "info", msg, action="AUTO_BLOCKED_COOKIES")
            return {
                "success": False,
                "message": msg,
                "file": None
            }

        log_with_action(self.logger, "info", "Daily limit OK for cookies, proceeding with backup...", action="AUTO_PROCEED_COOKIES")
        return self._perform_cookies_backup("AUTO-BACKUP", reason="Action")

    def backup_cookies_force(self, reason=None):
        """
        Create a backup of the cookies folder immediately, ignoring daily limit.
        Used when manually triggered from UI or during critical operations.
        Respects retention policy and storage size limits.
        
        Args:
            reason: Optional string describing why the backup was triggered (e.g., "Manual", "Delete", "Update")
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        log_with_action(self.logger, "info", "MANUAL-COOKIES-BACKUP triggered - Bypassing daily limit...", action="MANUAL_TRIGGER_COOKIES")
        return self._perform_cookies_backup("MANUAL-BACKUP", reason=reason or "Manual")

    def should_cookies_backup_today(self):
        """
        Check if a cookies backup should be performed today.
        Returns True if last backup was on a different day or no backup exists yet.
        """
        cookies_backup_enabled = self.config_manager.get("cookies_backup_enabled", True)
        if not cookies_backup_enabled:
            log_with_action(self.logger, "debug", "Cookies backup is disabled in configuration", action="CHECK_COOKIES")
            return False
        
        last_backup_str = self.config_manager.get("cookies_backup_last_date")
        if not last_backup_str:
            log_with_action(self.logger, "debug", "No previous cookies backup found - backup needed", action="CHECK_COOKIES")
            return True
        
        try:
            last_backup = datetime.fromisoformat(last_backup_str).date()
            today = datetime.now().date()
            should_backup = last_backup != today
            log_with_action(self.logger, "debug", f"Cookies backup check: last={last_backup}, today={today}, needed={should_backup}", action="CHECK_COOKIES")
            return should_backup
        except (ValueError, TypeError) as e:
            log_with_action(self.logger, "warning", f"Invalid cookies backup date format: {e}", action="CHECK_COOKIES")
            return True

    def _perform_cookies_backup(self, mode="MANUAL", reason=None):
        """
        Internal method that performs the actual cookies backup.
        
        Args:
            mode: String describing the backup mode (e.g., "AUTO-BACKUP", "MANUAL-BACKUP")
            reason: Optional string describing why the backup was triggered
        
        Returns:
            dict: Status with keys 'success' (bool), 'message' (str), 'file' (str or None)
        """
        try:
            # Ensure backup directory exists
            self._ensure_cookies_backup_dir()

            # Get configuration
            should_compress = self.config_manager.get("cookies_backup_compress", True)
            
            # Get cookies folder - use get_config_dir() which has proper fallback
            from Functions.config_manager import get_config_dir
            cookies_folder = self.config_manager.get("cookies_folder") or get_config_dir()
            
            if not os.path.exists(cookies_folder):
                # This is normal on first startup - folder will be created when first cookies are saved
                info_msg = "Cookies folder does not exist yet (normal on first startup)"
                log_with_action(self.logger, "info", info_msg, action="COOKIES_INFO")
                return {
                    "success": False,
                    "message": "Cookies folder not found",
                    "file": None
                }

            # Create backup filename with timestamp and reason
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reason_str = f"_{reason}" if reason else ""
            backup_name = f"backup_cookies_{timestamp}{reason_str}"
            
            cookies_backup_dir = self._get_cookies_backup_dir()
            if should_compress:
                backup_file = os.path.join(cookies_backup_dir, f"{backup_name}.zip")
                log_with_action(self.logger, "info", f"Creating compressed cookies backup: {os.path.basename(backup_file)}", action="ZIP_COOKIES")
                self._create_zip_backup(cookies_folder, backup_file)
            else:
                backup_file = os.path.join(cookies_backup_dir, backup_name)
                log_with_action(self.logger, "info", f"Creating uncompressed cookies backup: {os.path.basename(backup_file)}", action="ZIP_COOKIES")
                shutil.copytree(cookies_folder, backup_file, dirs_exist_ok=True)

            # Update last cookies backup date
            self.config_manager.set("cookies_backup_last_date", datetime.now().isoformat())
            
            # Apply retention policies for cookies
            log_with_action(self.logger, "info", "Applying retention policies for cookies backup...", action="RETENTION_COOKIES")
            self._apply_cookies_retention_policies()

            success_msg = f"Cookies backup created: {os.path.basename(backup_file)}"
            log_with_action(self.logger, "info", success_msg, action="COOKIES_INFO")
            return {
                "success": True,
                "message": success_msg,
                "file": backup_file
            }

        except Exception as e:
            error_msg = f"Cookies backup failed: {str(e)}"
            log_with_action(self.logger, "error", error_msg, action="COOKIES_INFO")
            logging.error(f"Exception during cookies backup: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "file": None
            }

    def _apply_cookies_retention_policies(self):
        """Apply retention policy for cookies backups based on storage size limit only."""
        cookies_backup_dir = self._get_cookies_backup_dir()
        backups = self._get_sorted_backups_in_dir(cookies_backup_dir)
        
        log_with_action(self.logger, "debug", f"Found {len(backups)} existing cookies backups", action="RETENTION_COOKIES")
        
        # Apply size retention (size limit only, no count limit)
        size_limit_mb = self.config_manager.get("cookies_backup_size_limit_mb", 10)
        if size_limit_mb > 0:
            total_size = sum(self._get_file_size(b) for b in backups)
            size_limit_bytes = size_limit_mb * 1024 * 1024
            
            log_with_action(self.logger, "debug", f"Total cookies backup size: {total_size / (1024*1024):.2f} MB / {size_limit_mb} MB", action="RETENTION_COOKIES")
            
            deleted_count = 0
            while total_size > size_limit_bytes and backups:
                oldest = backups.pop()  # Remove oldest
                old_size = self._get_file_size(oldest)
                log_with_action(self.logger, "info", f"Deleting oldest cookies backup: {os.path.basename(oldest)} ({old_size / (1024*1024):.2f} MB)", action="RETENTION_COOKIES")
                self._delete_backup(oldest)
                total_size -= old_size
                deleted_count += 1
            
            if deleted_count > 0:
                log_with_action(self.logger, "info", f"Cookies retention policy applied: {deleted_count} backup(s) deleted", action="RETENTION_COOKIES")
            else:
                log_with_action(self.logger, "debug", "No cookies backups need to be deleted", action="RETENTION_COOKIES")

    def _get_sorted_backups_in_dir(self, directory):
        """Get list of backups in a specific directory sorted by modification time (newest first)."""
        backups = []
        
        if not os.path.exists(directory):
            log_with_action(self.logger, "debug", f"Backup directory does not exist: {directory}", action="SCAN")
            return backups
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                backups.append(item_path)
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        log_with_action(self.logger, "debug", f"Found {len(backups)} backup(s) in directory: {directory}", action="SCAN")
        return backups

    def _create_zip_backup(self, source_dir, zip_file):
        """Create a compressed ZIP backup of the source directory."""
        log_with_action(self.logger, "debug", f"Starting ZIP compression from {source_dir}", action="ZIP")
        file_count = 0
        try:
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        file_count += 1
            log_with_action(self.logger, "debug", f"ZIP compression complete: {file_count} files", action="ZIP")
        except Exception as e:
            log_with_action(self.logger, "error", f"ZIP compression failed: {e}", action="ZIP")
            raise

    def _apply_retention_policies(self):
        """Apply retention policy based on storage size limit only."""
        backups = self._get_sorted_backups()
        
        log_with_action(self.logger, "debug", f"Found {len(backups)} existing backups", action="RETENTION")
        
        # Apply size retention (size limit only, no count limit)
        size_limit_mb = self.config_manager.get("backup_size_limit_mb", 20)
        if size_limit_mb > 0:
            total_size = sum(self._get_file_size(b) for b in backups)
            size_limit_bytes = size_limit_mb * 1024 * 1024
            
            log_with_action(self.logger, "debug", f"Total backup size: {total_size / (1024*1024):.2f} MB / {size_limit_mb} MB", action="RETENTION")
            
            deleted_count = 0
            while total_size > size_limit_bytes and backups:
                oldest = backups.pop()  # Remove oldest
                old_size = self._get_file_size(oldest)
                log_with_action(self.logger, "info", f"Deleting oldest backup: {os.path.basename(oldest)} ({old_size / (1024*1024):.2f} MB)", action="RETENTION")
                self._delete_backup(oldest)
                total_size -= old_size
                deleted_count += 1
            
            if deleted_count > 0:
                log_with_action(self.logger, "info", f"Retention policy applied: {deleted_count} backup(s) deleted", action="RETENTION")
            else:
                log_with_action(self.logger, "debug", "No backups need to be deleted", action="RETENTION")

    def _get_sorted_backups(self):
        """Get list of backups sorted by modification time (newest first)."""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            log_with_action(self.logger, "debug", "Backup directory does not exist yet", action="SCAN")
            return backups
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                backups.append(item_path)
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        log_with_action(self.logger, "debug", f"Found {len(backups)} backup(s) in directory", action="SCAN")
        return backups

    def _delete_backup(self, backup_path):
        """Delete a backup file or directory."""
        try:
            if os.path.isfile(backup_path):
                os.remove(backup_path)
                log_with_action(self.logger, "debug", f"Deleted backup file: {os.path.basename(backup_path)}", action="DELETE")
            elif os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
                log_with_action(self.logger, "debug", f"Deleted backup directory: {os.path.basename(backup_path)}", action="DELETE")
        except Exception as e:
            error_msg = f"Error deleting backup {backup_path}: {e}"
            log_with_action(self.logger, "error", error_msg, action="DELETE")
            print(f"[{LOGGER_BACKUP.upper()}] {error_msg}", file=sys.stderr)

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
        log_with_action(self.logger, "debug", "Gathering backup information", action="INFO")
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

        log_with_action(self.logger, "debug", f"Backup info: {len(backup_list)} backups, {total_size / (1024*1024):.2f} MB total", action="INFO")
        
        return {
            "path": self.backup_dir,
            "compress": self.config_manager.get("backup_compress", True),
            "size_limit_mb": size_limit_mb,
            "current_usage_mb": round(total_size / (1024 * 1024), 2),
            "backups": backup_list
        }

    def get_cookies_backup_info(self):
        """
        Get information about current cookies backup configuration and usage.
        
        Returns:
            dict: Contains path, compress, size_limit, current_usage, backups list
        """
        log_with_action(self.logger, "debug", "Gathering cookies backup information", action="INFO_COOKIES")
        cookies_backup_dir = self._get_cookies_backup_dir()
        backups = self._get_sorted_backups_in_dir(cookies_backup_dir)
        total_size = sum(self._get_file_size(b) for b in backups)
        size_limit_mb = self.config_manager.get("cookies_backup_size_limit_mb", 10)

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

        log_with_action(self.logger, "debug", f"Cookies backup info: {len(backup_list)} backups, {total_size / (1024*1024):.2f} MB total", action="INFO_COOKIES")
        
        return {
            "path": cookies_backup_dir,
            "compress": self.config_manager.get("cookies_backup_compress", True),
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
            log_with_action(self.logger, "info", f"Starting backup restoration from: {os.path.basename(backup_path)}", action="RESTORE")
            
            if restore_to is None:
                from Functions.character_manager import get_character_dir
                restore_to = get_character_dir()
            
            if not restore_to:
                error_msg = "Target directory not specified"
                log_with_action(self.logger, "error", error_msg, action="RESTORE")
                return {
                    "success": False,
                    "message": error_msg
                }

            # Create backup of current state before restoring
            backup_current = os.path.join(self.backup_dir, f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            log_with_action(self.logger, "info", f"Creating pre-restore backup: {os.path.basename(backup_current)}", action="RESTORE")
            shutil.copytree(restore_to, backup_current, dirs_exist_ok=True)

            # Clear current directory
            log_with_action(self.logger, "debug", f"Clearing target directory: {restore_to}", action="RESTORE")
            shutil.rmtree(restore_to)
            os.makedirs(restore_to, exist_ok=True)

            # Restore from backup
            if backup_path.endswith('.zip'):
                log_with_action(self.logger, "debug", "Extracting ZIP backup", action="RESTORE")
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(restore_to)
            else:
                log_with_action(self.logger, "debug", "Copying uncompressed backup", action="RESTORE")
                shutil.copytree(backup_path, restore_to, dirs_exist_ok=True)

            success_msg = f"Backup restored successfully from {os.path.basename(backup_path)}"
            log_with_action(self.logger, "info", success_msg, action="RESTORE")
            return {
                "success": True,
                "message": success_msg
            }

        except Exception as e:
            error_msg = f"Restore failed: {str(e)}"
            log_with_action(self.logger, "error", error_msg, action="RESTORE")
            return {
                "success": False,
                "message": error_msg
            }


# Global backup manager instance
backup_manager = None

def get_backup_manager(config_manager=None):
    """Get or create the global BackupManager instance."""
    global backup_manager
    if backup_manager is None and config_manager is not None:
        backup_manager = BackupManager(config_manager)
    return backup_manager
