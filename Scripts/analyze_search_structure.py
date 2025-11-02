#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse la structure HTML de la page de recherche
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from bs4 import BeautifulSoup

# Lit le HTML sauvegardé d'une recherche (on l'a créé plus tôt)
with open(r'd:\Projets\Python\DAOC-Character-Management\Scripts\search_result.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("ANALYSE DE LA PAGE DE RECHERCHE")
print("="*80)

# Cherche les tableaux
tables = soup.find_all('table')
print(f"\nNombre de tableaux: {len(tables)}")

for i, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f"\nTableau {i+1}:")
    print(f"  Nombre de lignes: {len(rows)}")
    
    if rows:
        # En-tetes
        first_row = rows[0]
        headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
        print(f"  Headers: {headers}")
        
        # Vérifier si c'est un tableau de résultats
        if 'Name' in headers or 'Nom' in headers:
            print("  --> C'EST UN TABLEAU DE RESULTATS!")
            print(f"  Nombre de personnages (lignes - 1): {len(rows) - 1}")
        else:
            print(f"  --> Pas un tableau de résultats (headers ne contient pas 'Name')")

# Cherche le message d'erreur
msg = 'The requested page "herald" is not available.'
if msg in html:
    print(f"\n>>> MESSAGE D'ERREUR DETECTE: '{msg}'")
else:
    print(f"\n>>> Message d'erreur NON detecte")

# Cherche des éléments de connexion
if "Login" in html:
    print(">>> Mot 'Login' trouvé - Probablement pas connecté")
if "discord" in html.lower():
    print(">>> Discord trouvé (page standard)")
