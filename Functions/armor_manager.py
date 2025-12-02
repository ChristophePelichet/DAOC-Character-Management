"""
Armor Manager - Gestion des templates d'armurerie
"""
import os
import shutil
import logging
from Functions.path_manager import ensure_armory_dir

logger = logging.getLogger(__name__)


class ArmorManager:
    """Gestionnaire des templates d'armurerie pour un personnage"""
    
    def __init__(self, season, realm, character_name):
        """
        Initialize the armor manager for a specific character
        
        Args:
            season: Season identifier (e.g., 'S3')
            realm: Realm name (e.g., 'Hibernia', 'Albion', 'Midgard')
            character_name: Name of the character
        """
        self.season = season
        self.realm = realm
        self.character_name = character_name
        self.armory_dir = ensure_armory_dir(season, realm, character_name)
    
    def upload_armor(self, source_file_path, custom_filename=None):
        """
        Upload an armor template file to the character's armory directory
        
        Args:
            source_file_path: Path to the source file to upload
            custom_filename: Optional custom filename (if None, uses original filename)
            
        Returns:
            str: Path to the uploaded file, or None if failed
        """
        try:
            if not os.path.exists(source_file_path):
                logger.error(f"Source file does not exist: {source_file_path}", extra={"action": "FILE"})
                return None
            
            # Use custom filename if provided, otherwise use original
            if custom_filename and custom_filename.strip():
                filename = custom_filename.strip()
                # Ensure the extension is preserved if not included in custom name
                original_ext = os.path.splitext(source_file_path)[1]
                if not os.path.splitext(filename)[1] and original_ext:
                    filename += original_ext
            else:
                filename = os.path.basename(source_file_path)
            
            destination = os.path.join(self.armory_dir, filename)
            
            # Check if file already exists
            if os.path.exists(destination):
                # Create a unique filename
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(destination):
                    filename = f"{base}_{counter}{ext}"
                    destination = os.path.join(self.armory_dir, filename)
                    counter += 1
            
            # Copy the file
            shutil.copy2(source_file_path, destination)
            logger.info(f"Armor template uploaded: {destination}", extra={"action": "FILE"})
            return destination
            
        except Exception as e:
            logger.error(f"Error uploading armor template: {e}", extra={"action": "FILE"})
            return None
    
    def list_armors(self):
        """
        List all armor template files for this character
        
        Returns:
            list: List of dictionaries with file info (filename, path, size, modified)
        """
        armors = []
        try:
            if not os.path.exists(self.armory_dir):
                return armors
            
            for filename in os.listdir(self.armory_dir):
                filepath = os.path.join(self.armory_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    armors.append({
                        'filename': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
            
            # Sort by filename
            armors.sort(key=lambda x: x['filename'])
            return armors
            
        except Exception as e:
            logger.error(f"Error listing armor templates: {e}", extra={"action": "FILE"})
            return []
    
    def delete_armor(self, filename):
        """
        Delete an armor template file
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            filepath = os.path.join(self.armory_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Armor template deleted: {filepath}", extra={"action": "DELETE"})
                return True
            else:
                logger.warning(f"Armor template not found: {filepath}", extra={"action": "FILE"})
                return False
        except Exception as e:
            logger.error(f"Error deleting armor template: {e}", extra={"action": "FILE"})
            return False
    
    def open_armor(self, filename):
        """
        Open an armor template file with the default system application
        
        Args:
            filename: Name of the file to open
            
        Returns:
            bool: True if opened successfully, False otherwise
        """
        try:
            filepath = os.path.join(self.armory_dir, filename)
            if os.path.exists(filepath):
                os.startfile(filepath)  # Windows
                logger.info(f"Opened armor template: {filepath}", extra={"action": "FILE"})
                return True
            else:
                logger.warning(f"Armor template not found: {filepath}", extra={"action": "FILE"})
                return False
        except Exception as e:
            logger.error(f"Error opening armor template: {e}", extra={"action": "FILE"})
            return False
    
    def get_armor_count(self):
        """
        Get the number of armor template files for this character
        
        Returns:
            int: Number of armor template files
        """
        return len(self.list_armors())