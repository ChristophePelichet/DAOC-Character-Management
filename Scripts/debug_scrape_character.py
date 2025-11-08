#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de débogage pour scraper un personnage depuis Herald
Affiche en détail toutes les données extraites de la page
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path pour importer les modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
from bs4 import BeautifulSoup
import time
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def debug_scrape_character(character_url, output_file=None):
    """
    Scrape un personnage et affiche toutes les données extraites
    
    Args:
        character_url: URL du personnage sur Herald
        output_file: Fichier de sortie optionnel (sinon sauvegardé dans Logs/)
    """
    # Create the File of sortie
    if not output_file:
        debug_dir = project_root / "Logs"
        debug_dir.mkdir(exist_ok=True)
        output_file = debug_dir / "debug_scrape_output.txt"
    
    # Ouvrir the File for écriture
    with open(output_file, 'w', encoding='utf-8') as f:
        def log(message):
            """Affiche et écrit dans le fichier"""
            print(message)
            f.write(message + "\n")
        
        log("=" * 80)
        log(f"DÉBOGAGE DU SCRAPING")
        log(f"URL: {character_url}")
        log("=" * 80)
        
        try:
            # Initialiser le cookie manager
            cookie_manager = CookieManager()
            
            if not cookie_manager.cookie_exists():
                log("❌ ERREUR: Aucun cookie trouvé")
                return
            
            log("\n✅ Cookies trouvés")
            
            # Initialiser le scraper
            scraper = EdenScraper(cookie_manager)
            
            if not scraper.initialize_driver(headless=False):
                log("❌ ERREUR: Impossible d'initialiser le navigateur")
                return
            
            log("✅ Navigateur initialisé")
            
            if not scraper.load_cookies():
                scraper.close()
                log("❌ ERREUR: Impossible de charger les cookies")
                return
            
            
            log("✅ Cookies chargés dans le navigateur")
            
            # Naviguer vers l'URL
            log(f"\n🌐 Navigation vers: {character_url}")
            scraper.driver.get(character_url)
            
            # Attendre que la page se charge
            log("⏳ Attente du chargement de la page (5 secondes)...")
            time.sleep(5)
            
            # Retrieve HTML
            page_source = scraper.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            log("\n" + "=" * 80)
            log("CONTENU DE LA PAGE")
            log("=" * 80)
            
            # Afficher le titre
            title = soup.title.string if soup.title else "Pas de titre"
            log(f"\n📄 Titre de la page: {title}")
            
            # Afficher the en-têtes
            log("\n📋 En-têtes H1:")
            h1_tags = soup.find_all('h1')
            if h1_tags:
                for i, h1 in enumerate(h1_tags, 1):
                    log(f"  {i}. {h1.get_text(strip=True)}")
            else:
                log("  Aucun H1 trouvé")
            
            log("\n📋 En-têtes H2:")
            h2_tags = soup.find_all('h2')
            if h2_tags:
                for i, h2 in enumerate(h2_tags, 1):
                    log(f"  {i}. {h2.get_text(strip=True)}")
            else:
                log("  Aucun H2 trouvé")
            
            log("\n📋 En-têtes H3:")
            h3_tags = soup.find_all('h3')
            if h3_tags:
                for i, h3 in enumerate(h3_tags, 1):
                    log(f"  {i}. {h3.get_text(strip=True)}")
            else:
                log("  Aucun H3 trouvé")
            
            # Afficher tous les tableaux
            log("\n" + "=" * 80)
            log("TABLEAUX TROUVÉS")
            log("=" * 80)
            
            tables = soup.find_all('table')
            log(f"\n📊 Nombre de tableaux: {len(tables)}")
            
            for table_idx, table in enumerate(tables, 1):
                log(f"\n{'─' * 80}")
                log(f"TABLEAU {table_idx}")
                log(f"{'─' * 80}")
                
                rows = table.find_all('tr')
                log(f"Nombre de lignes: {len(rows)}\n")
                
                # Collecter toutes the Data of the tableau
                table_data = []
                max_cols = 0
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = []
                        for cell in cells:
                            cell_text = cell.get_text(strip=True)
                            tag_type = cell.name
                            row_data.append((tag_type, cell_text))
                        table_data.append(row_data)
                        max_cols = max(max_cols, len(row_data))
                
                # Calculer les largeurs de colonnes
                col_widths = [0] * max_cols
                for row_data in table_data:
                    for i, (tag, text) in enumerate(row_data):
                        col_widths[i] = max(col_widths[i], len(text) + 4)  # +4 pour [tag]
                
                # Afficher the tableau formaté
                for row_idx, row_data in enumerate(table_data, 1):
                    # Ligne of séparation
                    if row_idx == 1:
                        sep = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
                    else:
                        sep = "├" + "┼".join("─" * w for w in col_widths) + "┤"
                    log(sep)
                    
                    # Contenu de la ligne
                    cells_formatted = []
                    for i in range(max_cols):
                        if i < len(row_data):
                            tag, text = row_data[i]
                            tag_str = f"[{tag}]"
                            cell_str = f"{tag_str} {text}"
                            cells_formatted.append(cell_str.ljust(col_widths[i]))
                        else:
                            cells_formatted.append(" " * col_widths[i])
                    
                    log("│" + "│".join(cells_formatted) + "│")
                
                # Ligne de fin
                if table_data:
                    sep = "└" + "┴".join("─" * w for w in col_widths) + "┘"
                    log(sep)
            
            # Extraction des Data with the logique actuelle
            log("\n" + "=" * 80)
            log("DONNÉES EXTRAITES (avec la logique actuelle)")
            log("=" * 80)
            
            character_data = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'url': character_url
            }
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        log(f"\n🔍 Analyse: '{key}' = '{value}'")
                        
                        # Mapper les champs
                        if 'name' in key or 'nom' in key:
                            character_data['name'] = value
                            character_data['clean_name'] = value.split()[0]
                            log(f"  ✅ Trouvé: name = {value}")
                        elif 'level' in key or 'niveau' in key:
                            character_data['level'] = value
                            log(f"  ✅ Trouvé: level = {value}")
                        elif 'class' in key or 'classe' in key:
                            character_data['class'] = value
                            log(f"  ✅ Trouvé: class = {value}")
                        elif 'race' in key:
                            character_data['race'] = value
                            log(f"  ✅ Trouvé: race = {value}")
                        elif 'realm' in key or 'royaume' in key:
                            character_data['realm'] = value
                            log(f"  ✅ Trouvé: realm = {value}")
                        elif 'guild' in key or 'guilde' in key:
                            character_data['guild'] = value
                            log(f"  ✅ Trouvé: guild = {value}")
                        elif 'realm point' in key or 'points de royaume' in key:
                            character_data['realm_points'] = value
                            log(f"  ✅ Trouvé: realm_points = {value}")
                        elif 'realm rank' in key or 'rang de royaume' in key:
                            character_data['realm_rank'] = value
                            log(f"  ✅ Trouvé: realm_rank = {value}")
                        elif 'realm level' in key or 'niveau de royaume' in key:
                            character_data['realm_level'] = value
                            log(f"  ✅ Trouvé: realm_level = {value}")
                        elif 'server' in key or 'serveur' in key:
                            character_data['server'] = value
                            log(f"  ✅ Trouvé: server = {value}")
            
            log("\n" + "=" * 80)
            log("RÉSULTAT FINAL")
            log("=" * 80)
            
            log("\n📦 Données extraites:")
            for key, value in character_data.items():
                log(f"  {key}: {value}")
            
            # Check if on a the Data minimales
            if 'name' in character_data or 'class' in character_data:
                log("\n✅ SUCCÈS: Données minimales extraites")
            else:
                log("\n❌ ÉCHEC: Impossible d'extraire les données minimales (name ou class)")
            
            # Sauvegarder le HTML brut pour inspection
            debug_dir = project_root / "Logs"
            debug_dir.mkdir(exist_ok=True)
            html_file = debug_dir / "debug_herald_page.html"
            
            with open(html_file, 'w', encoding='utf-8') as hf:
                hf.write(page_source)
            
            log(f"\n💾 HTML brut sauvegardé dans: {html_file}")
            
            scraper.close()
            
        except Exception as e:
            log(f"\n❌ EXCEPTION: {e}")
            import traceback
            log(traceback.format_exc())


if __name__ == "__main__":
    # URL par défaut - can be modifiée
    default_url = "https://eden-daoc.net/herald?n=player&k=Ewo"
    
    if len(sys.argv) > 1:
        character_url = sys.argv[1]
    else:
        character_url = default_url
        print(f"Utilisation de l'URL par défaut: {character_url}")
        print("Pour utiliser une autre URL: python debug_scrape_character.py <URL>\n")
    
    debug_scrape_character(character_url)
    
    # Afficher où the File a été sauvegardé
    output_file = project_root / "Logs" / "debug_scrape_output.txt"
    print("\n" + "=" * 80)
    print("DÉBOGAGE TERMINÉ")
    print(f"📄 Résultats sauvegardés dans: {output_file}")
    print("=" * 80)