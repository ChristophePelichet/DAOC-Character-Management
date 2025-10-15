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