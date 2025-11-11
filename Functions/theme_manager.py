"""
Gestionnaire de thèmes pour l'application DAOC Character Manager
Les thèmes sont définis dans des fichiers JSON dans le dossier Themes/
"""

import json
import logging
import os
from pathlib import Path
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from Functions.path_manager import get_resource_path


def get_themes_dir():
    """Retourne le chemin vers le dossier des thèmes"""
    return Path(get_resource_path("Themes"))


def get_available_themes():
    """
    Retourne la liste des thèmes disponibles
    Returns: dict {theme_id: theme_name}
    """
    from Functions.language_manager import lang
    
    themes = {}
    themes_dir = get_themes_dir()
    
    if not themes_dir.exists():
        logging.warning(f"Dossier Themes introuvable: {themes_dir}")
        return {"default": lang.get("theme_light")}
    
    for theme_file in themes_dir.glob("*.json"):
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                theme_id = theme_file.stem
                theme_name_key = theme_data.get("name", theme_id)
                # Si c'est une clé de traduction (commence par "theme_"), traduire
                if theme_name_key.startswith("theme_"):
                    theme_name = lang.get(theme_name_key)
                else:
                    theme_name = theme_name_key
                themes[theme_id] = theme_name
        except Exception as e:
            logging.error(f"Erreur lors du chargement du thème {theme_file}: {e}")
    
    return themes if themes else {"default": lang.get("theme_light")}


def load_theme(theme_id):
    """
    Charge un thème depuis son fichier JSON
    Args:
        theme_id: Identifiant du thème (nom du fichier sans .json)
    Returns:
        dict: Données du thème ou None si erreur
    """
    themes_dir = get_themes_dir()
    theme_file = themes_dir / f"{theme_id}.json"
    
    if not theme_file.exists():
        logging.warning(f"Fichier de thème introuvable: {theme_file}")
        return None
    
    try:
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
            logging.info(f"Thème '{theme_data.get('name', theme_id)}' chargé depuis {theme_file.name}")
            return theme_data
    except Exception as e:
        logging.error(f"Erreur lors du chargement du thème {theme_file}: {e}")
        return None


def apply_theme(app, theme_id="default"):
    """
    Applique un thème à l'application
    
    Args:
        app: Instance de QApplication
        theme_id: Identifiant du thème à appliquer
    """
    logging.info(f"Application du thème: {theme_id}")
    
    # Charger le thème
    theme_data = load_theme(theme_id)
    if not theme_data:
        logging.warning(f"Impossible de charger le thème '{theme_id}', utilisation du thème par défaut")
        theme_data = load_theme("default")
        if not theme_data:
            logging.error("Thème par défaut introuvable, utilisation du style système")
            app.setStyle("windowsvista" if "windowsvista" in QStyleFactory.keys() else "Fusion")
            return
    
    # Appliquer le style Qt
    style_name = theme_data.get("style", "windowsvista")
    if style_name in QStyleFactory.keys():
        app.setStyle(style_name)
        logging.debug(f"Style Qt appliqué: {style_name}")
    else:
        logging.warning(f"Style '{style_name}' non disponible, utilisation de Fusion")
        app.setStyle("Fusion")
    
    # Appliquer la palette de couleurs
    palette_data = theme_data.get("palette", {})
    if palette_data:
        palette = QPalette()
        
        # Couleurs normales
        for role_name, color_hex in palette_data.items():
            if role_name.startswith("Disabled_"):
                continue  # Géré après
            
            try:
                role = getattr(QPalette, role_name, None)
                if role is not None:
                    palette.setColor(role, QColor(color_hex))
            except Exception as e:
                logging.warning(f"Erreur lors de l'application de la couleur {role_name}: {e}")
        
        # Couleurs désactivées
        for role_name, color_hex in palette_data.items():
            if role_name.startswith("Disabled_"):
                actual_role_name = role_name.replace("Disabled_", "")
                try:
                    role = getattr(QPalette, actual_role_name, None)
                    if role is not None:
                        palette.setColor(QPalette.Disabled, role, QColor(color_hex))
                except Exception as e:
                    logging.warning(f"Erreur lors de l'application de la couleur désactivée {role_name}: {e}")
        
        app.setPalette(palette)
        logging.debug("Palette de couleurs appliquée")
    
    # Appliquer le stylesheet personnalisé
    stylesheet = theme_data.get("stylesheet", "")
    app.setStyleSheet(stylesheet)
    if stylesheet:
        logging.debug("Stylesheet personnalisé appliqué")
    
    logging.info(f"Thème '{theme_data.get('name', theme_id)}' appliqué avec succès")
