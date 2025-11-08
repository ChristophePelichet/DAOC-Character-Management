# -*- coding: utf-8 -*-
"""Script pour corriger l'icône dans dialogs.py"""

with open('UI/dialogs.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger l'icône
content = content.replace('QPushButton("� Générer des Cookies")', 'QPushButton("🔐 Générer des Cookies")')

with open('UI/dialogs.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Icône corrigée")