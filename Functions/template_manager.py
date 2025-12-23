"""
Template Manager
Handles all operations related to armory templates: creation, deletion, filtering, indexing.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from .template_metadata import (
    TemplateMetadata,
    normalize_description,
    validate_metadata
)
from .config_manager import config


class TemplateManager:
    """Manages armory templates and their metadata"""
    
    INDEX_FILE = ".template_index.json"
    
    def __init__(self, armory_path: Optional[Path] = None):
        """
        Initialize TemplateManager.
        
        Args:
            armory_path: Path to Armory folder (defaults to config value)
        """
        if armory_path:
            self.armory_path = Path(armory_path)
        else:
            # Get from config
            armory_folder = config.get("folders.armor")
            if armory_folder:
                self.armory_path = Path(armory_folder)
            else:
                # Fallback to default
                from .path_manager import get_base_path
                self.armory_path = Path(get_base_path()) / "Armory"
        
        # Ensure Armory folder exists
        self.armory_path.mkdir(exist_ok=True)
        
        # Create realm folders structure
        self._ensure_realm_folders()
        
        # Load or create index
        self.index = self._load_index()
    
    def _ensure_realm_folders(self):
        """Create folder structure for all realms"""
        for realm in ['Albion', 'Hibernia', 'Midgard']:
            realm_path = self.armory_path / realm
            templates_path = realm_path / 'Templates'
            json_path = realm_path / 'Json'
            
            templates_path.mkdir(parents=True, exist_ok=True)
            json_path.mkdir(parents=True, exist_ok=True)
    
    def _get_template_path(self, realm: str, template_name: str) -> Path:
        """Get full path for template file"""
        return self.armory_path / realm / 'Templates' / template_name
    
    def _get_metadata_path(self, realm: str, template_name: str) -> Path:
        """Get full path for metadata file"""
        return self.armory_path / realm / 'Json' / f"{template_name}.json"
    
    def _load_index(self) -> Dict[str, Any]:
        """Load template index from file"""
        index_file = self.armory_path / self.INDEX_FILE
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[TEMPLATE_MANAGER] Error loading index: {e}")
        
        # Create new index
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "templates": []
        }
    
    def _save_index(self) -> bool:
        """Save template index to file"""
        index_file = self.armory_path / self.INDEX_FILE
        
        try:
            self.index["last_updated"] = datetime.now().isoformat()
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[TEMPLATE_MANAGER] Error saving index: {e}")
            return False
    
    def generate_template_name(
        self,
        character_class: str,
        season: str,
        description: str,
        include_season: bool = True
    ) -> str:
        """
        Generate template filename according to convention.
        
        Format: {Class}_{Season}_{Description}.txt (if include_season=True)
                {Class}_{Description}.txt (if include_season=False)
        
        Args:
            character_class: Class name (English)
            season: Season identifier (S1, S2, etc.)
            description: Template description
            include_season: Whether to include season in the filename (default: True)
        
        Returns:
            Generated filename
        """
        normalized_desc = normalize_description(description)
        if include_season:
            return f"{character_class}_{season}_{normalized_desc}.txt"
        else:
            return f"{character_class}_{normalized_desc}.txt"
    
    def create_template(
        self,
        source_file: Path,
        character_class: str,
        class_fr: str,
        class_de: str,
        realm: str,
        season: str,
        description: str,
        character_name: str,
        tags: Optional[List[str]] = None,
        notes: str = "",
        include_season: bool = True
    ) -> Optional[str]:
        """
        Create a new template from source file.
        
        Args:
            source_file: Path to source template file
            character_class: Class name (English)
            class_fr: Class name (French)
            class_de: Class name (German)
            realm: Realm
            season: Season
            description: Description
            character_name: Name of character importing
            tags: Optional tags
            notes: Optional notes
            include_season: Whether to include season in filename (default: True)
        
        Returns:
            Template filename if successful, None otherwise
        """
        try:
            # Generate template name with include_season parameter
            template_name = self.generate_template_name(
                character_class,
                season,
                description,
                include_season=include_season
            )
            
            # Check if template already exists
            template_file = self._get_template_path(realm, template_name)
            if template_file.exists():
                print(f"[TEMPLATE_MANAGER] Template already exists: {template_name}")
                return None
            
            # Copy source file to Templates folder
            with open(source_file, 'r', encoding='utf-8') as src:
                content = src.read()
            
            # Count items (lines with content)
            item_count = len([line for line in content.split('\n') if line.strip()])
            
            # Write template file
            with open(template_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            # Create metadata
            metadata = TemplateMetadata(
                template_name=template_name,
                character_class=character_class,
                class_fr=class_fr,
                class_de=class_de,
                realm=realm,
                season=season,
                description=description,
                source_file=source_file.name,
                imported_by_character=character_name,
                item_count=item_count,
                tags=tags or [],
                notes=notes
            )
            
            # Save metadata to Json folder
            metadata_path = self._get_metadata_path(realm, template_name)
            if not metadata.save_to_path(metadata_path):
                # Rollback template file
                template_file.unlink()
                return None
            
            # Update index
            self._add_to_index(metadata)
            
            print(f"[TEMPLATE_MANAGER] Created template: {template_name}")
            return template_name
            
        except Exception as e:
            print(f"[TEMPLATE_MANAGER] Error creating template: {e}")
            return None
    
    def _add_to_index(self, metadata: TemplateMetadata):
        """Add template to index"""
        self.index["templates"].append({
            "file": metadata.template_name,
            "class": metadata.character_class,
            "realm": metadata.realm,
            "season": metadata.season,
            "tags": metadata.tags,
            "item_count": metadata.item_count,
            "import_date": metadata.import_date
        })
        self._save_index()
    
    def _remove_from_index(self, template_name: str):
        """Remove template from index"""
        self.index["templates"] = [
            t for t in self.index["templates"]
            if t["file"] != template_name
        ]
        self._save_index()
    
    def get_templates_for_class(
        self,
        character_class: str
    ) -> List[Dict[str, Any]]:
        """
        Get all templates for a specific class.
        
        Args:
            character_class: Class name (English)
        
        Returns:
            List of template info dictionaries
        """
        templates = []
        
        for template_info in self.index["templates"]:
            if template_info["class"] == character_class:
                # Load full metadata from Realm/Json/ folder
                realm = template_info.get("realm", "Albion")
                metadata_path = self._get_metadata_path(realm, template_info['file'])
                if metadata_path.exists():
                    metadata = TemplateMetadata.load(metadata_path)
                    if metadata:
                        templates.append({
                            "file": template_info["file"],
                            "metadata": metadata
                        })
        
        return templates
    
    def delete_template(self, template_name: str, realm: str) -> bool:
        """
        Delete a template and its metadata.
        
        Args:
            template_name: Name of template file
            realm: Realm name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            template_file = self._get_template_path(realm, template_name)
            metadata_file = self._get_metadata_path(realm, template_name)
            
            # Delete files
            if template_file.exists():
                template_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Remove from index
            self._remove_from_index(template_name)
            
            print(f"[TEMPLATE_MANAGER] Deleted template: {template_name}")
            return True
            
        except Exception as e:
            print(f"[TEMPLATE_MANAGER] Error deleting template: {e}")
            return False
    
    def search_templates(
        self,
        character_class: Optional[str] = None,
        season: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search templates with filters.
        
        Args:
            character_class: Filter by class
            season: Filter by season
            tags: Filter by tags (any match)
            search_text: Search in name/description
        
        Returns:
            List of matching templates
        """
        results = []
        
        for template_info in self.index["templates"]:
            # Filter by class
            if character_class and template_info["class"] != character_class:
                continue
            
            # Filter by season
            if season and template_info["season"] != season:
                continue
            
            # Filter by tags
            if tags:
                template_tags = set(template_info.get("tags", []))
                if not any(tag in template_tags for tag in tags):
                    continue
            
            # Search text
            if search_text:
                search_lower = search_text.lower()
                if search_lower not in template_info["file"].lower():
                    continue
            
            # Load full metadata
            realm = template_info.get("realm", "Albion")
            metadata_path = self._get_metadata_path(realm, template_info['file'])
            if metadata_path.exists():
                metadata = TemplateMetadata.load(metadata_path)
                if metadata:
                    results.append({
                        "file": template_info["file"],
                        "metadata": metadata
                    })
        
        return results
    
    def update_index(self):
        """Rebuild index from existing template files"""
        print("[TEMPLATE_MANAGER] Rebuilding template index...")
        
        # Find all .json metadata files recursively in realm/Json folders
        metadata_files = list(self.armory_path.glob("**/Json/*.json"))
        
        # Exclude index file (though it shouldn't be in Json folders)
        metadata_files = [
            f for f in metadata_files
            if f.name != self.INDEX_FILE
        ]
        
        # Reset index
        self.index = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "templates": []
        }
        
        # Rebuild from metadata files
        for metadata_file in metadata_files:
            metadata = TemplateMetadata.load(metadata_file)
            if metadata:
                self.index["templates"].append({
                    "file": metadata.template_name,
                    "class": metadata.character_class,
                    "realm": metadata.realm,
                    "season": metadata.season,
                    "tags": metadata.tags,
                    "item_count": metadata.item_count,
                    "import_date": metadata.import_date
                })
        
        self._save_index()
        print(f"[TEMPLATE_MANAGER] Index rebuilt: {len(self.index['templates'])} templates")
    
    def get_current_season(self) -> str:
        """Get current season from config"""
        return config.get("game.default_season", "S3")
    
    def get_available_seasons(self) -> List[str]:
        """Get available seasons from config"""
        return config.get("game.seasons", ["S3"])
