import logging
import os
from logging.handlers import RotatingFileHandler
from .config_manager import config
from .path_manager import get_base_path, get_resource_path

def get_log_dir():
    """
    Gets the log directory from the config.
    If not set, defaults to a 'Logs' folder next to the executable.
    """
    path = config.get("log_folder")
    if path and os.path.isdir(path):
        return path
    return os.path.join(get_base_path(), "Logs")

def get_img_dir():
    """
    Gets the image directory.
    For bundled resources in PyInstaller, uses sys._MEIPASS.
    For development, uses the project's Img folder.
    """
    # Check if user has configured a custom img folder
    path = config.get("img_folder")
    if path and os.path.isdir(path):
        return path
    # Use resource path which handles both dev and frozen modes
    return get_resource_path("Img")

def setup_logging(extra_handlers=None):
    """
    Configures the application's logger based on settings in config.json.
    Always logs CRITICAL and ERROR messages to file, even if debug mode is off.
    An optional list of extra_handlers (like for a GUI window) can be provided.
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear existing handlers to avoid duplicate logs on re-configuration
    logger.handlers.clear()

    # If special handlers (like for the debug window) are provided, add them first.
    if extra_handlers:
        for handler in extra_handlers:
            logger.addHandler(handler)

    # Determine logging level from config
    is_debug_mode = config.get("debug_mode", True)

    # Set the root logger's level to the lowest possible level.
    # This allows individual handlers to control what they display.
    logger.setLevel(logging.DEBUG)

    # Create log directory if it doesn't exist
    log_dir = get_log_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_path = os.path.join(log_dir, "debug.log")

    # Always create a file handler for CRITICAL and ERROR messages (even if debug is OFF)
    fh_errors = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
    fh_errors.setLevel(logging.ERROR)  # Only ERROR and CRITICAL
    fh_errors.setFormatter(formatter)
    logger.addHandler(fh_errors)

    # If debug mode is ON, configure full debug logging
    if is_debug_mode:
        # Full debug file handler
        fh_debug = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
        fh_debug.setLevel(logging.DEBUG)
        fh_debug.setFormatter(formatter)
        logger.addHandler(fh_debug)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)