#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier l'affichage des emojis dans Qt
"""

import sys
from pathlib import Path

# Ajouter the répertoire parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from PySide6.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtGui import QFont

class EmojiTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test d'affichage des Emojis")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Test 1 : QLabel simple
        label1 = QLabel("Test QLabel simple:")
        layout.addWidget(label1)
        
        label2 = QLabel("👤 📋 🎯 📝 ⚡ ⚠️ 💡 🔗 📞 🛡️ 🍀 ⚔️ 📚 ✅")
        font = QFont()
        font.setFamilies(["Segoe UI Emoji", "Segoe UI", "Arial"])
        font.setPointSize(12)
        label2.setFont(font)
        layout.addWidget(label2)
        
        # Test 2 : QPushButton
        button = QPushButton("👤 Créer un personnage")
        button.setFont(font)
        layout.addWidget(button)
        
        # Test 3 : QTextBrowser avec HTML simple
        text_browser1 = QTextBrowser()
        text_browser1.setFont(font)
        text_browser1.setMaximumHeight(150)
        text_browser1.setHtml("""
            <h2>Test HTML simple</h2>
            <p>👤 📋 🎯 📝 ⚡ ⚠️ 💡 🔗 📞</p>
            <p>🛡️ Albion | 🍀 Hibernia | ⚔️ Midgard</p>
        """)
        layout.addWidget(text_browser1)
        
        # Test 4 : QTextBrowser avec HTML complet (comme help_manager)
        text_browser2 = QTextBrowser()
        text_browser2.setFont(font)
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <style>
                body {
                    font-family: 'Segoe UI Emoji', 'Segoe UI', 'Apple Color Emoji', 'Noto Color Emoji', Arial, sans-serif;
                    padding: 10px;
                }
                h1, h2, h3 {
                    font-family: 'Segoe UI Emoji', 'Segoe UI', 'Apple Color Emoji', 'Noto Color Emoji', Arial, sans-serif;
                }
            </style>
        </head>
        <body>
            <h1>👤 Créer un Nouveau Personnage</h1>
            <h2>📋 Résumé</h2>
            <p>Apprenez à créer manuellement un nouveau personnage.</p>
            <h2>🎯 Objectif</h2>
            <ul>
                <li>✅ Ouvrir le dialogue</li>
                <li>✅ Remplir les champs</li>
                <li>✅ Sauvegarder</li>
            </ul>
            <h2>📝 Étapes Détaillées</h2>
            <h3>⚡ Raccourcis</h3>
            <p><strong>Ctrl+N</strong> - Créer un nouveau personnage</p>
            <h3>⚠️ Attention</h3>
            <p>Le nom doit être unique</p>
            <h3>💡 Astuces</h3>
            <p>Utilisez des conventions de nommage</p>
            <h2>Royaumes</h2>
            <ul>
                <li>🛡️ <strong>Albion</strong> - Royaume britannique</li>
                <li>🍀 <strong>Hibernia</strong> - Royaume celtique</li>
                <li>⚔️ <strong>Midgard</strong> - Royaume nordique</li>
            </ul>
            <h2>🔗 Voir Aussi</h2>
            <p>📞 Besoin d'aide ? 📚 Documentation</p>
        </body>
        </html>
        """
        text_browser2.setHtml(html_content)
        layout.addWidget(text_browser2)
        
        # Test 5 : Encodage système
        label3 = QLabel(f"Encodage système : {sys.getdefaultencoding()}")
        layout.addWidget(label3)


def main():
    app = QApplication(sys.argv)
    
    # Forcer l'encodage UTF-8
    if sys.platform == 'win32':
        import locale
        print(f"Locale système : {locale.getpreferredencoding()}")
    
    window = EmojiTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()