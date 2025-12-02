import sys
import os
from pathlib import Path

def get_base_path():
    """
    Gets the base path for the application.
    For a frozen executable (PyInstaller), it's the directory where the .exe is.
    For a script, it's the project's root directory.
    """
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the base path is the directory of the executable
        return os.path.dirname(sys.executable)
    else:
        # If run as a script, it's the project root (one level up from this file's directory)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_resource_path(relative_path):
    """
    Gets the absolute path to a resource file.
    Works for both development and PyInstaller frozen mode.
    
    In PyInstaller, bundled resources are extracted to sys._MEIPASS.
    In development, resources are in the project directory.
    
    Args:
        relative_path: Path relative to the project root (e.g., 'Img/icon.png')
    
    Returns:
        Absolute path to the resource file
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # In development, use the project root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    return os.path.join(base_path, relative_path)

def get_armory_base_dir():
    """
    Returns the Armory base directory.
    Located at project root: Armory/
    """
    return os.path.join(get_base_path(), "Armory")

def get_armory_dir(season, realm, character_name):
    """
    Returns the armory directory for a specific character.
    Structure: Armory/Season/Realm/CharacterName/
    
    Args:
        season: Season identifier (e.g., 'S3')
        realm: Realm name (e.g., 'Hibernia', 'Albion', 'Midgard')
        character_name: Name of the character
    
    Returns:
        str: Full path to character's armory directory
    """
    base = get_armory_base_dir()
    return os.path.join(base, season, realm, character_name)

def ensure_armory_dir(season, realm, character_name):
    """
    Ensures the armory directory exists for a character, creating it if necessary.
    
    Args:
        season: Season identifier
        realm: Realm name
        character_name: Character name
        
    Returns:
        str: Path to the character's armory directory
    """
    armory_dir = get_armory_dir(season, realm, character_name)
    os.makedirs(armory_dir, exist_ok=True)
    return armory_dir

# Legacy functions - kept for backward compatibility
def get_armor_dir():
    """
    DEPRECATED: Returns the old armor directory.
    Use get_armory_dir() instead.
    """
    from Functions.config_manager import config
    default_path = os.path.join(get_base_path(), "Armory")
    return config.get("armor_folder") or default_path

def ensure_armor_dir():
    """
    DEPRECATED: Ensures the old armor directory exists.
    Use ensure_armory_dir() instead.
    """
    armor_dir = get_armor_dir()
    os.makedirs(armor_dir, exist_ok=True)
    return armor_dir

def get_user_data_dir():
    """
    Returns the user data directory for the application.
    This is where persistent user data (cookies, profiles, etc.) should be stored.
    
    Platform-specific locations:
    - Windows: %LOCALAPPDATA%/DAOC_Character_Manager/
    - Linux: ~/.local/share/DAOC_Character_Manager/
    - macOS: ~/Library/Application Support/DAOC_Character_Manager/
    
    Returns:
        Path: Absolute path to user data directory
    """
    app_name = "DAOC_Character_Manager"
    
    if sys.platform == "win32":
        # Windows: %LOCALAPPDATA%
        base = os.getenv("LOCALAPPDATA")
        if not base:
            # Fallback if LOCALAPPDATA not set
            base = os.path.expanduser("~\\AppData\\Local")
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support
        base = os.path.expanduser("~/Library/Application Support")
    else:
        # Linux and others: ~/.local/share
        base = os.getenv("XDG_DATA_HOME")
        if not base:
            base = os.path.expanduser("~/.local/share")
    
    user_data_path = Path(base) / app_name
    user_data_path.mkdir(parents=True, exist_ok=True)
    return user_data_path

def get_eden_data_dir():
    """
    Returns the Eden data directory for cookies and Chrome profile.
    Located in user data directory: {user_data}/Eden/
    
    Returns:
        Path: Absolute path to Eden data directory
    """
    eden_dir = get_user_data_dir() / "Eden"
    eden_dir.mkdir(parents=True, exist_ok=True)
    return eden_dir

def get_chrome_profile_path():
    """
    Returns the path to the dedicated Chrome profile for Selenium.
    Located in: {user_data}/Eden/ChromeProfile/
    
    This profile is isolated from the user's personal Chrome browser.
    
    Returns:
        Path: Absolute path to Chrome profile directory
    """
    profile_path = get_eden_data_dir() / "ChromeProfile"
    profile_path.mkdir(parents=True, exist_ok=True)
    return profile_path

def get_eden_cookies_path():
    """
    Returns the path to the Eden cookies file.
    Located in: {user_data}/Eden/eden_cookies.pkl
    
    Returns:
        Path: Absolute path to cookies file (may not exist yet)
    """
    return get_eden_data_dir() / "eden_cookies.pkl"


class PathManager:
    """Centralized path management for the application"""
    
    def get_app_root(self):
        """Get application root directory (where Data/ folder is located)"""
        return Path(get_base_path())
    
    def get_resource_path(self, relative_path):
        """Get absolute path to a resource file"""
        return Path(get_resource_path(relative_path))


# Global instance for easy access
path_manager = PathManager()
