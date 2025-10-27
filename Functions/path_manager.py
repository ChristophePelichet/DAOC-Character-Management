import sys
import os

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