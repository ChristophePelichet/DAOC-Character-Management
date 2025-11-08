"""
Script pour extraire les données de Realm Ranks depuis le site officiel DAOC
Les données sont organisées par royaume: Albion (rouge), Hibernia (vert), Midgard (bleu)
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib3

# Désactiver the avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_realm_ranks():
    """Récupère les tableaux de Realm Ranks pour les 3 royaumes"""
    url = "https://www.darkageofcamelot.com/realm-ranks/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Connexion à {url}...")
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Structure of Data
    realm_data = {
        "Albion": [],
        "Hibernia": [],
        "Midgard": []
    }
    
    # Trouver le tableau principal
    table = soup.find('table')
    if not table:
        raise Exception("Aucun tableau trouvé sur la page")
    
    print(f"Tableau trouvé, parsing des données...")
    
    rows = table.find_all('tr')
    print(f"Nombre total de lignes: {len(rows)}")
    
    # Parser chaque ligne of Data (skip header row 0)
    for row_idx, row in enumerate(rows[1:], 1):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 5:
            continue
        
        # Cellule 0: Rank et skill bonus
        rank_cell = cells[0]
        rank_text = rank_cell.get_text()
        rank_match = re.search(r'Rank (\d+)', rank_text)
        rank = int(rank_match.group(1)) if rank_match else row_idx
        
        skill_bonus_match = re.search(r'\+(\d+) to skills', rank_text)
        skill_bonus = int(skill_bonus_match.group(1)) if skill_bonus_match else 0
        
        # Cellule 1: Titres (séparés par <br>, colorés par royaume)
        title_cell = cells[1]
        # Les titres sont dans l'ordre: Albion (rouge), Hibernia (vert), Midgard (bleu)
        title_lines = [line.strip() for line in title_cell.stripped_strings]
        
        albion_title = title_lines[0] if len(title_lines) > 0 else ""
        hibernia_title = title_lines[1] if len(title_lines) > 1 else ""
        midgard_title = title_lines[2] if len(title_lines) > 2 else ""
        
        # Cellule 2: Niveaux (séparés par <br>)
        level_cell = cells[2]
        levels = [line.strip() for line in level_cell.stripped_strings if line.strip()]
        
        # Cellule 3: Realm Points (séparés par <br>)
        rp_cell = cells[3]
        realm_points = [line.strip().replace(',', '') for line in rp_cell.stripped_strings if line.strip()]
        
        # Cellule 4: Realm Ability Points (séparés par <br>)
        rap_cell = cells[4]
        realm_ability_points = [line.strip() for line in rap_cell.stripped_strings if line.strip()]
        
        # Create une entrée for chaque niveau
        num_levels = len(levels)
        print(f"Rank {rank}: {num_levels} niveaux")
        
        for i in range(num_levels):
            level = levels[i] if i < len(levels) else f"{rank}L{i+1}"
            rp = int(realm_points[i]) if i < len(realm_points) else 0
            rap = int(realm_ability_points[i]) if i < len(realm_ability_points) else 0
            
            # Create the entrées for chaque royaume
            realm_data["Albion"].append({
                "rank": rank,
                "skill_bonus": skill_bonus,
                "title": albion_title,
                "level": level,
                "realm_points": rp,
                "realm_ability_points": rap
            })
            
            realm_data["Hibernia"].append({
                "rank": rank,
                "skill_bonus": skill_bonus,
                "title": hibernia_title,
                "level": level,
                "realm_points": rp,
                "realm_ability_points": rap
            })
            
            realm_data["Midgard"].append({
                "rank": rank,
                "skill_bonus": skill_bonus,
                "title": midgard_title,
                "level": level,
                "realm_points": rp,
                "realm_ability_points": rap
            })
    
    print(f"\n=== Résumé de l'extraction ===")
    for realm in ["Albion", "Hibernia", "Midgard"]:
        count = len(realm_data[realm])
        print(f"{realm}: {count} entrées")
        if count > 0:
            print(f"  Premier: Rank {realm_data[realm][0]['rank']}, {realm_data[realm][0]['title']}")
            print(f"  Dernier: Rank {realm_data[realm][-1]['rank']}, {realm_data[realm][-1]['title']}")
    
    return realm_data

def save_to_json(data, filename):
    """Sauvegarde les données dans un fichier JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Données sauvegardées dans: {filename}")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Extraction des Realm Ranks de DAOC")
        print("=" * 60)
        
        realm_ranks = scrape_realm_ranks()
        
        # Sauvegarder
        output_file = "Data/realm_ranks.json"
        save_to_json(realm_ranks, output_file)
        
        print("\n" + "=" * 60)
        print("✅ Extraction terminée avec succès!")
        print("=" * 60)
        print(f"\nVous pouvez maintenant utiliser le fichier '{output_file}'")
        print("dans votre gestionnaire de personnages DAOC.")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()