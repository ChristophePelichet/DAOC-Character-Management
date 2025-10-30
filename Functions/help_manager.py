#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Help Manager - Gestionnaire du système d'aide intégré
Gère l'affichage des aides Markdown dans l'application
"""

from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont
import markdown
import logging

logger = logging.getLogger(__name__)


class HelpWindow(QDialog):
    """Fenêtre d'affichage d'une aide au format Markdown"""
    
    def __init__(self, parent=None, title="Aide", markdown_file=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 700)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Zone de texte pour afficher l'aide
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        
        # Utiliser une police qui supporte les emojis
        font = QFont()
        font.setFamilies(["Segoe UI Emoji", "Segoe UI", "Arial"])
        font.setPointSize(10)
        self.text_browser.setFont(font)
        
        layout.addWidget(self.text_browser)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Charger le contenu si un fichier est fourni
        if markdown_file:
            self.load_markdown_file(markdown_file)
    
    def load_markdown_file(self, file_path):
        """Charge et affiche un fichier Markdown"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"Fichier d'aide introuvable: {file_path}")
                self.text_browser.setHtml(f"<h1>❌ Erreur</h1><p>Le fichier d'aide n'a pas été trouvé :<br><code>{file_path}</code></p>")
                return
            
            # Lire le fichier Markdown
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convertir Markdown en HTML
            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'fenced_code', 'codehilite', 'toc']
            )
            
            # Ajouter du CSS pour un meilleur rendu
            styled_html = self._add_css_styling(html_content)
            
            # Afficher
            self.text_browser.setHtml(styled_html)
            
            logger.info(f"Aide chargée: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'aide: {e}")
            self.text_browser.setHtml(f"<h1>❌ Erreur</h1><p>Impossible de charger l'aide :<br>{e}</p>")
    
    def _add_css_styling(self, html_content):
        """Ajoute du CSS pour améliorer le rendu HTML"""
        css = """
        <style>
            body {
                font-family: 'Segoe UI Emoji', 'Segoe UI', 'Apple Color Emoji', 'Noto Color Emoji', Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 850px;
                margin: 0 auto;
                background-color: #ffffff;
                color: #333;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Segoe UI Emoji', 'Segoe UI', 'Apple Color Emoji', 'Noto Color Emoji', Arial, sans-serif;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
            }
            h2 {
                color: #34495e;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 8px;
                margin-top: 25px;
            }
            h3 {
                color: #34495e;
                margin-top: 20px;
            }
            h4 {
                color: #7f8c8d;
                margin-top: 15px;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', 'Courier New', monospace;
                color: #e74c3c;
            }
            pre {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            pre code {
                background-color: transparent;
                color: #ecf0f1;
                padding: 0;
            }
            blockquote {
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin-left: 0;
                background-color: #ecf7fd;
                padding: 10px 15px;
                border-radius: 3px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            table th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
            }
            table td {
                border: 1px solid #ddd;
                padding: 10px;
            }
            table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            ul, ol {
                margin-left: 20px;
            }
            li {
                margin: 8px 0;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            hr {
                border: none;
                border-top: 2px solid #ecf0f1;
                margin: 30px 0;
            }
            .emoji {
                font-size: 1.2em;
            }
        </style>
        """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            {css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """


class HelpManager:
    """Gestionnaire du système d'aide"""
    
    def __init__(self, language='fr'):
        """
        Initialise le gestionnaire d'aide
        
        Args:
            language: Code langue (fr, en, de)
        """
        self.language = language
        self.help_dir = Path(__file__).parent.parent / "Help"
        
        logger.info(f"HelpManager initialisé - Langue: {language}, Dossier: {self.help_dir}")
    
    def show_help(self, help_id, parent=None, title=None):
        """
        Affiche une aide spécifique
        
        Args:
            help_id: Identifiant de l'aide (nom du fichier sans extension)
            parent: Widget parent pour la fenêtre
            title: Titre de la fenêtre (optionnel)
        
        Returns:
            HelpWindow: La fenêtre d'aide créée
        """
        # Construire le chemin du fichier
        help_file = self.help_dir / self.language / f"{help_id}.md"
        
        # Si le fichier n'existe pas dans la langue actuelle, essayer en anglais
        if not help_file.exists():
            logger.warning(f"Aide non trouvée en {self.language}: {help_id}, tentative en anglais")
            help_file = self.help_dir / "en" / f"{help_id}.md"
        
        # Si toujours pas trouvé, essayer en français
        if not help_file.exists():
            logger.warning(f"Aide non trouvée en anglais: {help_id}, tentative en français")
            help_file = self.help_dir / "fr" / f"{help_id}.md"
        
        # Si toujours pas trouvé, afficher une erreur
        if not help_file.exists():
            logger.error(f"Aide introuvable: {help_id}")
            help_file = None
        
        # Titre par défaut
        if title is None:
            title = self._get_default_title(help_id)
        
        # Créer et afficher la fenêtre
        help_window = HelpWindow(parent=parent, title=title, markdown_file=help_file)
        help_window.exec()
        
        return help_window
    
    def _get_default_title(self, help_id):
        """Retourne le titre par défaut selon l'ID de l'aide"""
        titles = {
            'character_create': {
                'fr': 'Aide - Créer un Personnage',
                'en': 'Help - Create a Character',
                'de': 'Hilfe - Charakter erstellen'
            },
            'character_edit': {
                'fr': 'Aide - Modifier un Personnage',
                'en': 'Help - Edit a Character',
                'de': 'Hilfe - Charakter bearbeiten'
            },
            'character_delete': {
                'fr': 'Aide - Supprimer un Personnage',
                'en': 'Help - Delete a Character',
                'de': 'Hilfe - Charakter löschen'
            },
            'character_import': {
                'fr': 'Aide - Importer depuis Eden',
                'en': 'Help - Import from Eden',
                'de': 'Hilfe - Von Eden importieren'
            },
            'cookies_management': {
                'fr': 'Aide - Gérer les Cookies',
                'en': 'Help - Manage Cookies',
                'de': 'Hilfe - Cookies verwalten'
            },
            'settings': {
                'fr': 'Aide - Configuration',
                'en': 'Help - Settings',
                'de': 'Hilfe - Einstellungen'
            }
        }
        
        return titles.get(help_id, {}).get(self.language, 'Aide')
    
    def set_language(self, language):
        """Change la langue du système d'aide"""
        self.language = language
        logger.info(f"Langue d'aide changée: {language}")
    
    def help_exists(self, help_id):
        """Vérifie si une aide existe"""
        help_file = self.help_dir / self.language / f"{help_id}.md"
        return help_file.exists()
    
    def get_available_helps(self):
        """Retourne la liste des aides disponibles dans la langue actuelle"""
        help_lang_dir = self.help_dir / self.language
        
        if not help_lang_dir.exists():
            logger.warning(f"Dossier d'aide introuvable: {help_lang_dir}")
            return []
        
        helps = []
        for file in help_lang_dir.glob("*.md"):
            helps.append(file.stem)
        
        return sorted(helps)
