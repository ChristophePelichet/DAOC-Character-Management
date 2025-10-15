import logging
import os
from logging.handlers import RotatingFileHandler
from .config_manager import config

# Define the log file path at the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_log_dir():
    """
    Gets the log directory from the config.
    If not set, defaults to a 'Logs' folder in the project root.
    """
    path = config.get("log_folder")
    if path and os.path.isdir(path):
        return path
    return os.path.join(PROJECT_ROOT, "Logs")

def setup_logging():
    """
    Configures the application's logger based on settings in config.json.
    If debug mode is off, all logging is disabled.
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear existing handlers to avoid duplicate logs on re-configuration
    logger.handlers.clear()

    # Determine logging level from config
    is_debug_mode = config.get("debug_mode", False)

    if not is_debug_mode:
        # If debug mode is off, disable logging completely by adding a NullHandler
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1) # Set level higher than any possible log
        return

    # If debug mode is ON, configure file and console handlers
    logger.setLevel(logging.DEBUG)
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