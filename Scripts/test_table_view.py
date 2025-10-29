#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de l'affichage en tableau des résultats de recherche
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget
import json

# Charger le dernier fichier de résultats
search_dir = Path(__file__).parent.parent / "Configuration" / "SearchResults"
json_files = sorted(search_dir.glob("characters_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

if not json_files:
    print("❌ Aucun fichier de résultats trouvé")
    sys.exit(1)

latest_file = json_files[0]
print(f"📄 Fichier: {latest_file.name}")

with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

characters = data.get('characters', [])
print(f"📊 {len(characters)} personnage(s) trouvé(s)")

# Créer l'application Qt
app = QApplication(sys.argv)

# Créer la fenêtre
window = QWidget()
window.setWindowTitle(f"🔍 Résultats: {data['search_query']}")
window.resize(1000, 400)

layout = QVBoxLayout(window)

# Créer le tableau
table = QTableWidget()
table.setAlternatingRowColors(True)
table.setSelectionBehavior(QTableWidget.SelectRows)
table.setSelectionMode(QTableWidget.SingleSelection)
table.setEditTriggers(QTableWidget.NoEditTriggers)

# Configurer les colonnes
columns = ["#", "Nom", "Classe", "Race", "Guilde", "Niveau", "RP", "Realm Rank", "URL"]
table.setColumnCount(len(columns))
table.setHorizontalHeaderLabels(columns)

# Remplir le tableau
table.setRowCount(len(characters))

for row, char in enumerate(characters):
    table.setItem(row, 0, QTableWidgetItem(char.get('rank', '')))
    table.setItem(row, 1, QTableWidgetItem(char.get('name', '')))
    table.setItem(row, 2, QTableWidgetItem(char.get('class', '')))
    table.setItem(row, 3, QTableWidgetItem(char.get('race', '')))
    table.setItem(row, 4, QTableWidgetItem(char.get('guild', '')))
    table.setItem(row, 5, QTableWidgetItem(char.get('level', '')))
    table.setItem(row, 6, QTableWidgetItem(char.get('realm_points', '')))
    realm_rank = f"{char.get('realm_rank', '')} ({char.get('realm_level', '')})"
    table.setItem(row, 7, QTableWidgetItem(realm_rank))
    table.setItem(row, 8, QTableWidgetItem(char.get('url', '')))

# Ajuster les colonnes
header = table.horizontalHeader()
header.setStretchLastSection(True)
for i in range(len(columns) - 1):
    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

layout.addWidget(table)

window.show()

print("\n✅ Tableau affiché")
print("💡 Chaque personnage est sur une ligne")

sys.exit(app.exec())
