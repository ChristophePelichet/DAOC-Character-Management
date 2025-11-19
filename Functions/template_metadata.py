"""
Template Metadata Management
Handles creation, validation and management of template metadata files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class TemplateMetadata:
    """Represents metadata for an armory template"""
    
    VERSION = "1.0"
    
    def __init__(
        self,
        template_name: str,
        character_class: str,
        class_fr: str,
        class_de: str,
        realm: str,
        season: str,
        description: str,
        source_file: str,
        imported_by_character: str,
        item_count: int,
        tags: Optional[List[str]] = None,
        notes: str = ""
    ):
        """
        Initialize template metadata.
        
        Args:
            template_name: Name of the template file
            character_class: Class name (English)
            class_fr: Class name (French)
            class_de: Class name (German)
            realm: Realm (Albion/Hibernia/Midgard)
            season: Season identifier (S1, S2, S3, etc.)
            description: Template description
            source_file: Original source file name
            imported_by_character: Character name who imported
            item_count: Number of items in template
            tags: Optional list of tags
            notes: Optional notes
        """
        self.template_name = template_name
        self.character_class = character_class
        self.class_fr = class_fr
        self.class_de = class_de
        self.realm = realm
        self.season = season
        self.description = description
        self.source_file = source_file
        self.imported_by_character = imported_by_character
        self.item_count = item_count
        self.tags = tags or []
        self.notes = notes
        self.import_date = datetime.now().isoformat()
        self.auto_generated = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format"""
        return {
            "version": self.VERSION,
            "template_name": self.template_name,
            "metadata": {
                "class": self.character_class,
                "class_fr": self.class_fr,
                "class_de": self.class_de,
                "realm": self.realm,
                "season": self.season,
                "description": self.description,
                "tags": self.tags,
                "source_file": self.source_file,
                "import_date": self.import_date,
                "imported_by_character": self.imported_by_character,
                "item_count": self.item_count,
                "auto_generated": self.auto_generated
            },
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """Create TemplateMetadata from dictionary"""
        metadata = data.get("metadata", {})
        
        instance = cls(
            template_name=data.get("template_name", ""),
            character_class=metadata.get("class", ""),
            class_fr=metadata.get("class_fr", ""),
            class_de=metadata.get("class_de", ""),
            realm=metadata.get("realm", ""),
            season=metadata.get("season", ""),
            description=metadata.get("description", ""),
            source_file=metadata.get("source_file", ""),
            imported_by_character=metadata.get("imported_by_character", ""),
            item_count=metadata.get("item_count", 0),
            tags=metadata.get("tags", []),
            notes=data.get("notes", "")
        )
        
        # Restore import_date if available
        if "import_date" in metadata:
            instance.import_date = metadata["import_date"]
        
        return instance
    
    def save(self, armory_path: Path) -> bool:
        """
        Save metadata to JSON file.
        
        Args:
            armory_path: Path to Armory folder
        
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata_file = armory_path / f"{self.template_name}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[TEMPLATE_METADATA] Error saving metadata: {e}")
            return False
    
    def save_to_path(self, metadata_path: Path) -> bool:
        """
        Save metadata to specific path.
        
        Args:
            metadata_path: Full path to metadata JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[TEMPLATE_METADATA] Error saving metadata: {e}")
            return False
    
    @classmethod
    def load(cls, metadata_file: Path) -> Optional['TemplateMetadata']:
        """
        Load metadata from JSON file.
        
        Args:
            metadata_file: Path to metadata JSON file
        
        Returns:
            TemplateMetadata instance or None if error
        """
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"[TEMPLATE_METADATA] Error loading metadata: {e}")
            return None


def validate_metadata(metadata: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate metadata structure and required fields.
    
    Args:
        metadata: Metadata dictionary to validate
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required top-level keys
    required_keys = ["version", "template_name", "metadata"]
    for key in required_keys:
        if key not in metadata:
            errors.append(f"Missing required key: {key}")
    
    # Check required metadata fields
    if "metadata" in metadata:
        required_metadata = [
            "class", "class_fr", "class_de", "realm", "season",
            "description", "source_file", "import_date",
            "imported_by_character", "item_count", "auto_generated"
        ]
        for key in required_metadata:
            if key not in metadata["metadata"]:
                errors.append(f"Missing required metadata field: {key}")
    
    # Validate types
    if "metadata" in metadata:
        meta = metadata["metadata"]
        
        if "item_count" in meta and not isinstance(meta["item_count"], int):
            errors.append("item_count must be an integer")
        
        if "tags" in meta and not isinstance(meta["tags"], list):
            errors.append("tags must be a list")
        
        if "auto_generated" in meta and not isinstance(meta["auto_generated"], bool):
            errors.append("auto_generated must be a boolean")
    
    return (len(errors) == 0, errors)


def normalize_description(description: str, max_length: int = 50) -> str:
    """
    Normalize description for use in filename.
    Everything in lowercase.
    
    Args:
        description: Original description text
        max_length: Maximum length (default 50)
    
    Returns:
        Normalized description (all lowercase)
    
    Example:
        "low cost sans ml10" -> "low_cost_sans_ml10"
        "HIGH END BUILD" -> "high_end_build"
    """
    import unicodedata
    import re
    
    # Remove accents
    normalized = unicodedata.normalize('NFD', description)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Replace spaces with underscores
    normalized = normalized.replace(' ', '_')
    
    # Remove special characters except - and _
    normalized = re.sub(r'[^a-z0-9_-]', '', normalized)
    
    # Remove multiple consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)
    
    # Trim to max length
    if len(normalized) > max_length:
        normalized = normalized[:max_length]
    
    # Remove trailing underscore
    normalized = normalized.rstrip('_')
    
    return normalized
