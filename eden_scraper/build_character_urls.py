#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script pour construire les URLs des personnages depuis search_result.json"""

import json
from rich.console import Console
from rich.table import Table

# Lire les données de recherche
with open('search_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

console = Console()

# Trouver le tableau avec les personnages (devrait être le tableau 21 d'après l'affichage)
# On cherche le tableau qui a des colonnes: Name, Class, Race, Guild, etc.

characters = []

for idx, table_rows in enumerate(data.get('tables', []), 1):
    if len(table_rows) > 1:
        # Vérifier si c'est le bon tableau (contient Name, Class, Race)
        headers = table_rows[0]
        if 'Name' in headers and 'Class' in headers and 'Race' in headers:
            console.print(f'[green]✓ Tableau {idx} trouvé avec les personnages[/green]\n')
            
            # Trouver l'index de la colonne Name
            name_idx = headers.index('Name')
            class_idx = headers.index('Class')
            race_idx = headers.index('Race')
            guild_idx = headers.index('Guild') if 'Guild' in headers else -1
            
            # Extraire les personnages (sauter la ligne d'en-tête)
            for row in table_rows[1:]:
                if len(row) > name_idx:
                    name = row[name_idx].strip()
                    if name and 'Ewoli' in name:
                        # Construire l'URL
                        # Format: https://eden-daoc.net/herald?n=player&k=NomPersonnage
                        # Retirer les espaces et caractères spéciaux du nom
                        clean_name = name.split()[0]  # Prendre juste le premier mot
                        url = f'https://eden-daoc.net/herald?n=player&k={clean_name}'
                        
                        char_info = {
                            'name': name,
                            'clean_name': clean_name,
                            'url': url,
                            'class': row[class_idx] if len(row) > class_idx else 'N/A',
                            'race': row[race_idx] if len(row) > race_idx else 'N/A',
                            'guild': row[guild_idx] if guild_idx >= 0 and len(row) > guild_idx else 'N/A'
                        }
                        characters.append(char_info)

# Afficher les résultats
if characters:
    table = Table(title="Personnages Ewoli avec URLs", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim")
    table.add_column("Nom", style="cyan")
    table.add_column("Classe", style="green")
    table.add_column("URL", style="blue")
    
    for idx, char in enumerate(characters, 1):
        table.add_row(
            str(idx),
            char['name'],
            char['class'],
            char['url']
        )
    
    console.print(table)
    
    # Sauvegarder dans un fichier JSON
    with open('characters_urls.json', 'w', encoding='utf-8') as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)
    
    console.print(f'\n[green]✓ {len(characters)} personnages sauvegardés dans characters_urls.json[/green]')
else:
    console.print('[red]✗ Aucun personnage trouvé[/red]')
