"""
Armor Manager - Gestion des fichiers d'armure uploadés
"""
import os
import shutil
import logging
from pathlib import Path
from Functions.path_manager import get_armor_dir, ensure_armor_dir

logger = logging.getLogger(__name__)


class ArmorManager:
    """Gestionnaire des fichiers d'armure pour un personnage"""
    
    def __init__(self, character_id):
        """
        Initialize the armor manager for a specific character
        
        Args:
            character_id: The unique identifier of the character
        """
        self.character_id = character_id
        self.armor_dir = ensure_armor_dir()
        self.character_armor_dir = os.path.join(self.armor_dir, str(character_id))
        os.makedirs(self.character_armor_dir, exist_ok=True)
    
    def upload_armor(self, source_file_path):
        """
        Upload an armor file to the character's armor directory
        
        Args:
            source_file_path: Path to the source file to upload
            
        Returns:
            str: Path to the uploaded file, or None if failed
        """
        try:
            if not os.path.exists(source_file_path):
                logger.error(f"Source file does not exist: {source_file_path}")
                return None
            
            filename = os.path.basename(source_file_path)
            destination = os.path.join(self.character_armor_dir, filename)
            
            # Check if file already exists
            if os.path.exists(destination):
                # Create a unique filename
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(destination):
                    filename = f"{base}_{counter}{ext}"
                    destination = os.path.join(self.character_armor_dir, filename)
                    counter += 1
            
            # Copy the file
            shutil.copy2(source_file_path, destination)
            logger.info(f"Armor file uploaded: {destination}")
            return destination
            
        except Exception as e:
            logger.error(f"Error uploading armor file: {e}")
            return None
    
    def list_armors(self):
        """
        List all armor files for this character
        
        Returns:
            list: List of tuples (filename, full_path, size_bytes, modified_time)
        """
        armors = []
        try:
            if not os.path.exists(self.character_armor_dir):
                return armors
            
            for filename in os.listdir(self.character_armor_dir):
                filepath = os.path.join(self.character_armor_dir, filename)
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
            logger.error(f"Error listing armor files: {e}")
            return []
    
    def delete_armor(self, filename):
        """
        Delete an armor file
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            filepath = os.path.join(self.character_armor_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Armor file deleted: {filepath}")
                return True
            else:
                logger.warning(f"Armor file not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error deleting armor file: {e}")
            return False
    
    def open_armor(self, filename):
        """
        Open an armor file with the default system application
        
        Args:
            filename: Name of the file to open
            
        Returns:
            bool: True if opened successfully, False otherwise
        """
        try:
            filepath = os.path.join(self.character_armor_dir, filename)
            if os.path.exists(filepath):
                os.startfile(filepath)  # Windows
                logger.info(f"Opened armor file: {filepath}")
                return True
            else:
                logger.warning(f"Armor file not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error opening armor file: {e}")
            return False
    
    def get_armor_count(self):
        """
        Get the number of armor files for this character
        
        Returns:
            int: Number of armor files
        """
        return len(self.list_armors())
