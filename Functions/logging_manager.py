import logging
import os
from logging.handlers import RotatingFileHandler
from .config_manager import config
from .path_manager import get_base_path, get_resource_path

# Logger names constants - for easy filtering and organization
LOGGER_ROOT = "ROOT"
LOGGER_BACKUP = "BACKUP"
LOGGER_EDEN = "EDEN"
LOGGER_EDEN_PERF = "EDEN_PERF"  # Performance logs for Eden connection test
LOGGER_UI = "UI"
LOGGER_CHARACTER = "CHARACTER"

# All available loggers (for future UI filtering)
ALL_LOGGERS = [LOGGER_BACKUP, LOGGER_EDEN, LOGGER_EDEN_PERF, LOGGER_UI, LOGGER_CHARACTER]

class ContextualFormatter(logging.Formatter):
    """
    Enhanced formatter that includes:
    - asctime (date and time)
    - logger name
    - level name
    - action (custom attribute)
    - message
    
    Format: LOGGER - LEVEL - ACTION - MESSAGE
    Example: EDEN - INFO - TEST - Connexion à https://eden-daoc.net/herald?n=top_players&r=hib
    """
    def format(self, record):
        # Add action field (empty by default)
        if not hasattr(record, 'action'):
            record.action = "-"
        else:
            # If action is provided but empty, replace with dash
            if not record.action:
                record.action = "-"
        
        # Convert logger name to uppercase, with special handling for 'root'
        logger_name = record.name.upper() if record.name != 'root' else 'ROOT'
        
        # Build the format string with all parts
        fmt = '%(asctime)s - ' + logger_name + ' - %(levelname)s - %(action)s - %(message)s'
        
        formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

def get_log_dir():
    """
    Gets the log directory from the config.
    If not set, defaults to a 'Logs' folder next to the executable.
    """
    path = config.get("folders.logs")
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

def setup_eden_performance_logger():
    """
    Configure le logger dédié pour les logs de performance Eden.
    Crée un fichier séparé: Logs/eden_performance_YYYY-MM-DD.log
    Activé uniquement si system.eden.enable_performance_logs = true dans config.json
    """
    from datetime import datetime
    
    # Vérifier si les logs de performance sont activés
    perf_logs_enabled = config.get("system.eden.enable_performance_logs", False)
    
    if not perf_logs_enabled:
        return None
    
    # Créer le répertoire de logs si nécessaire
    log_dir = get_log_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nom de fichier avec date du jour
    today = datetime.now().strftime('%Y-%m-%d')
    log_file_path = os.path.join(log_dir, f"eden_performance_{today}.log")
    
    # Créer le logger dédié
    perf_logger = logging.getLogger(LOGGER_EDEN_PERF)
    perf_logger.setLevel(logging.DEBUG)
    
    # Supprimer les handlers existants pour éviter les duplications
    perf_logger.handlers.clear()
    
    # Handler fichier avec rotation quotidienne
    fh = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=10, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(ContextualFormatter())
    perf_logger.addHandler(fh)
    
    # Ne pas propager au logger root (pour éviter duplication dans debug.log)
    perf_logger.propagate = False
    
    return perf_logger

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
    is_debug_mode = config.get("system.debug_mode", False)

    # Set the root logger's level to the lowest possible level.
    # This allows individual handlers to control what they display.
    logger.setLevel(logging.DEBUG)

    # Only create log files if debug mode is enabled
    if is_debug_mode:
        # Create log directory if it doesn't exist
        log_dir = get_log_dir()
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Use the new contextual formatter
        formatter = ContextualFormatter()
        log_file_path = os.path.join(log_dir, "debug.log")
        
        # Full debug file handler
        fh = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        # When debug mode is OFF, only log to console for critical errors
        ch = logging.StreamHandler()
        ch.setLevel(logging.CRITICAL)
        ch.setFormatter(ContextualFormatter())
        logger.addHandler(ch)


def get_logger(name):
    """
    Get a logger with a specific name.
    
    Usage:
        logger = get_logger("backup")
        logger.info("Backup started", extra={"action": "START"})
    """
    return logging.getLogger(name)


def log_with_action(logger, level, message, action=""):
    """
    Log a message with an action field for better filtering.
    
    Usage:
        log_with_action(logger, "info", "Character updated", action="MODIFY")
    """
    extra = {"action": action} if action else {}
    if level.lower() == "debug":
        logger.debug(message, extra=extra)
    elif level.lower() == "info":
        logger.info(message, extra=extra)
    elif level.lower() == "warning":
        logger.warning(message, extra=extra)
    elif level.lower() == "error":
        logger.error(message, extra=extra)
    elif level.lower() == "critical":
        logger.critical(message, extra=extra)


class LoggerFactory:
    """Factory for creating and managing loggers with consistent formatting."""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name):
        """Get or create a logger with the given name."""
        if name not in LoggerFactory._loggers:
            LoggerFactory._loggers[name] = logging.getLogger(name)
        return LoggerFactory._loggers[name]
    
    @staticmethod
    def log(logger, level, message, action=""):
        """Log a message with optional action for context."""
        log_with_action(logger, level, message, action)