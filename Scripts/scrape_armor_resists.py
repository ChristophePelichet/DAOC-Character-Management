"""
Script pour extraire les données de résistances d'armure depuis le site officiel DAOC
Les données incluent les types d'armure et leurs valeurs de résistance
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib3

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_armor_resists():
    """Récupère les tableaux de résistances d'armure"""
    url = "https://www.darkageofcamelot.com/armor-resist-tables/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Connexion à {url}...")
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Structure de données
    armor_data = {
        "armor_types": [],
        "resist_types": [],
        "tables": {}
    }
    
    # Trouver tous les tableaux
    tables = soup.find_all('table')
    if not tables:
        raise Exception("Aucun tableau trouvé sur la page")
    
    print(f"{len(tables)} tableau(x) trouvé(s), parsing des données...")
    
    for table_idx, table in enumerate(tables):
        print(f"\n=== Traitement du tableau {table_idx + 1} ===")
        
        # Extraire le titre du tableau (s'il existe)
        table_title = "Unknown"
        prev_element = table.find_previous(['h2', 'h3', 'h4', 'p'])
        if prev_element:
            table_title = prev_element.get_text(strip=True)
        
        print(f"Titre: {table_title}")
        
        rows = table.find_all('tr')
        if len(rows) < 2:
            print("Tableau vide ou incomplet, ignoré")
            continue
        
        # Première ligne = en-têtes
        headers = []
        header_row = rows[0]
        for cell in header_row.find_all(['th', 'td']):
            headers.append(cell.get_text(strip=True))
        
        print(f"En-têtes: {headers}")
        
        # Extraire les données
        table_data = []
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            row_data = {}
            for idx, cell in enumerate(cells):
                if idx < len(headers):
                    cell_text = cell.get_text(strip=True)
                    # Nettoyer les données (enlever % si présent)
                    cell_text = cell_text.replace('%', '').strip()
                    row_data[headers[idx]] = cell_text
            
            if row_data:
                table_data.append(row_data)
        
        print(f"Lignes de données: {len(table_data)}")
        
        # Stocker les données du tableau
        armor_data["tables"][f"table_{table_idx + 1}"] = {
            "title": table_title,
            "headers": headers,
            "data": table_data
        }
        
        # Collecter les types d'armure uniques (première colonne généralement)
        if headers and table_data:
            first_header = headers[0]
            for row in table_data:
                armor_type = row.get(first_header, "")
                if armor_type and armor_type not in armor_data["armor_types"]:
                    armor_data["armor_types"].append(armor_type)
        
        # Collecter les types de résistance (autres colonnes)
        for header in headers[1:]:
            if header and header not in armor_data["resist_types"]:
                armor_data["resist_types"].append(header)
    
    print(f"\n=== Résumé de l'extraction ===")
    print(f"Types d'armure trouvés: {len(armor_data['armor_types'])}")
    print(f"  {armor_data['armor_types']}")
    print(f"Types de résistance trouvés: {len(armor_data['resist_types'])}")
    print(f"  {armor_data['resist_types']}")
    print(f"Tableaux extraits: {len(armor_data['tables'])}")
    
    return armor_data

def save_to_json(data, filename):
    """Sauvegarde les données dans un fichier JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Données sauvegardées dans: {filename}")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Extraction des Résistances d'Armure de DAOC")
        print("=" * 60)
        
        armor_resists = scrape_armor_resists()
        
        # Sauvegarder
        output_file = "Data/armor_resists.json"
        save_to_json(armor_resists, output_file)
        
        print("\n" + "=" * 60)
        print("✅ Extraction terminée avec succès!")
        print("=" * 60)
        print(f"\nVous pouvez maintenant utiliser le fichier '{output_file}'")
        print("dans votre gestionnaire de personnages DAOC.")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
