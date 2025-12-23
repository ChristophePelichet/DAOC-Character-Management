"""
Armory All Templates Manager - Manages template data and operations
Handles loading, filtering, and managing all templates across realms and classes
"""

import json
import logging
from pathlib import Path

from Functions.path_manager import get_resource_path

logger = logging.getLogger(__name__)


class ArmoryAllTemplatesManager:
    """Manages all templates data loading, filtering, and operations"""

    def __init__(self):
        """Initialize the armory templates manager"""
        self.all_templates = []

    def load_templates(self):
        """Load all templates from disk"""
        self.all_templates = []
        realms = ["Albion", "Hibernia", "Midgard"]
        armory_base = Path(get_resource_path("Armory"))
        logger.info(f"Starting template load from: {armory_base}")
        logger.info(f"Armory base exists: {armory_base.exists()}")

        for realm in realms:
            realm_path = armory_base / realm / "Templates"
            logger.info(f"Loading templates from {realm_path}")
            logger.info(f"Realm path exists: {realm_path.exists()}")
            if realm_path.exists():
                template_files = list(realm_path.glob("*.txt"))
                logger.info(f"Found {len(template_files)} template files in {realm}")
                for template_file in template_files:
                    if template_file.name.startswith("_"):
                        continue

                    metadata = self._load_template_metadata(realm, template_file.name)
                    self.all_templates.append({
                        "realm": realm,
                        "name": template_file.stem,
                        "class": metadata.get("class", "Unknown"),
                        "season": metadata.get("season", "Unknown"),
                        "file": template_file.name,
                        "path": template_file
                    })
            else:
                logger.warning(f"Realm path does not exist: {realm_path}")

        logger.info(f"Total templates loaded: {len(self.all_templates)}")

    def get_all_classes(self):
        """Get sorted list of all available classes"""
        classes = sorted(
            set(t["class"] for t in self.all_templates if t["class"] != "Unknown")
        )
        return classes

    def filter_templates(self, realm_filter="", class_filter="", search_text=""):
        """Filter templates by realm, class, and search text

        Args:
            realm_filter: Realm name filter (empty for all)
            class_filter: Class filter (empty for all)
            search_text: Search text to match in template name

        Returns:
            List of filtered templates
        """
        search_lower = search_text.lower()
        filtered = [
            t for t in self.all_templates
            if (not realm_filter or t["realm"] == realm_filter)
            and (not class_filter or t["class"] == class_filter)
            and (not search_lower or search_lower in t["name"].lower())
        ]
        return filtered

    def _load_template_metadata(self, realm, filename):
        """Load metadata from JSON file if it exists

        Args:
            realm: Realm name
            filename: Template filename

        Returns:
            Dictionary with class and season metadata
        """
        json_path = (
            Path(get_resource_path("Armory")) / realm / "Json" / f"{filename}.json"
        )

        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("metadata", {})
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load metadata from {json_path}: {e}")

        # Parse from filename: Class_Season_Description.txt
        parts = filename.replace(".txt", "").split("_", 2)
        return {
            "class": parts[0] if len(parts) > 0 else "Unknown",
            "season": parts[1] if len(parts) > 1 else "Unknown"
        }

    def get_template_content(self, template):
        """Get template file content

        Args:
            template: Template dictionary

        Returns:
            Template file content as string

        Raises:
            Exception: If template cannot be read
        """
        with open(template["path"], 'r', encoding='utf-8') as f:
            return f.read()

    def delete_template(self, template):
        """Delete a template and its metadata

        Args:
            template: Template dictionary to delete

        Raises:
            Exception: If template cannot be deleted
        """
        # Delete template file
        if template["path"].exists():
            template["path"].unlink()
            logger.info(f"Deleted template file: {template['path']}")
        else:
            logger.warning(f"Template file not found: {template['path']}")

        # Also delete JSON metadata if exists
        # Path structure: Armory/[Realm]/Templates/file.txt -> Armory/[Realm]/Json/file.txt.json
        realm_path = template["path"].parent.parent  # Go up from Templates to Realm folder
        json_path = realm_path / "Json" / f"{template['file']}.json"
        
        if json_path.exists():
            json_path.unlink()
            logger.info(f"Deleted template metadata: {json_path}")
        else:
            logger.warning(f"Template metadata not found: {json_path}")
