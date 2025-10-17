import logging
import os
from logging.handlers import RotatingFileHandler
from .config_manager import config
from .path_manager import get_base_path

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
    Gets the image directory from the config.
    If not set, defaults to an 'Img' folder next to the executable.
    """
    path = config.get("img_folder")
    if path and os.path.isdir(path):
        return path
    return os.path.join(get_base_path(), "Img")

def setup_logging(extra_handler=None):
    """
    Configures the application's logger based on settings in config.json.
    If debug mode is off, all logging is disabled.
    An optional extra_handler (like for a GUI window) can be provided.
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear existing handlers to avoid duplicate logs on re-configuration
    logger.handlers.clear()

    # If a special handler (like for the debug window) is provided, add it first.
    if extra_handler:
        logger.addHandler(extra_handler)

    # Determine logging level from config
    is_debug_mode = config.get("debug_mode", True)

    # Set the root logger's level to the lowest possible level.
    # This allows individual handlers to control what they display.
    logger.setLevel(logging.DEBUG)

    # If debug mode is ON, configure file and console handlers
    if is_debug_mode:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        log_dir = get_log_dir()
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file_path = os.path.join(log_dir, "debug.log")

        # Rotates logs: 5 files of 1MB each
        fh = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)