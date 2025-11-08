#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour extraire et formatter les résultats de recherche Herald
Construit les URLs des personnages trouvés
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_search_results(json_path):
    """Analyse le fichier JSON de recherche et extrait les personnages"""
    
    print("\n" + "=" * 80)
    print("📊 ANALYSE DES RÉSULTATS DE RECHERCHE")
    print("=" * 80)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n🔍 Recherche: {data['character_name']}")
    print(f"🔗 URL: {data['search_url']}")
    print(f"📅 Date: {data['timestamp']}")
    print(f"📊 Entrées brutes: {len(data['results'])}")
    
    # Trouver le tableau des personnages
    # Les personnages ont: col_1=Nom, col_3=Classe, col_5=Race, col_7=Guilde
    characters = []
    
    for result in data['results']:
        # Check if it's a character row
        # Critères: col_1 non vide and col_3 ressemble à une classe
        if (result.get('col_1') and 
            result.get('col_3') and 
            len(result.get('col_1', '')) > 0 and
            result.get('col_0') and  # A un rang
            result.get('col_0', '').isdigit()):  # Le rang est un nombre
            
            rank = result.get('col_0', '')
            name = result.get('col_1', '').strip()
            char_class = result.get('col_3', '').strip()
            race = result.get('col_5', '').strip()
            guild = result.get('col_7', '').strip()
            level = result.get('col_8', '').strip()
            rp = result.get('col_9', '').strip()
            realm_rank = result.get('col_10', '').strip()
            realm_level = result.get('col_11', '').strip()
            
            # Ne garder que si on a au moins un nom et une classe
            if name and char_class:
                # Construire l'URL
                # Prendre seulement le premier mot du nom (cas des noms avec espaces)
                clean_name = name.split()[0]
                url = f"https://eden-daoc.net/herald?n=player&k={clean_name}"
                
                character = {
                    'rank': rank,
                    'name': name,
                    'clean_name': clean_name,
                    'class': char_class,
                    'race': race,
                    'guild': guild,
                    'level': level,
                    'realm_points': rp,
                    'realm_rank': realm_rank,
                    'realm_level': realm_level,
                    'url': url
                }
                
                characters.append(character)
    
    # Afficher the Results
    print(f"\n✅ {len(characters)} personnage(s) trouvé(s)")
    print("\n" + "=" * 80)
    print("PERSONNAGES TROUVÉS")
    print("=" * 80)
    
    for idx, char in enumerate(characters, 1):
        print(f"\n#{char['rank']} - {char['name']}")
        print(f"   Classe: {char['class']}")
        print(f"   Race: {char['race']}")
        print(f"   Guilde: {char['guild']}")
        print(f"   Niveau: {char['level']}")
        print(f"   RP: {char['realm_points']}")
        print(f"   Realm Rank: {char['realm_rank']} ({char['realm_level']})")
        print(f"   🔗 URL: {char['url']}")
    
    # Save in un File JSON dedicated
    output_file = Path(json_path).parent / f"characters_{data['character_name']}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'search_query': data['character_name'],
            'search_url': data['search_url'],
            'timestamp': data['timestamp'],
            'characters': characters
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés: {output_file}")
    print("=" * 80)
    
    return characters


def main():
    """Point d'entrée principal"""
    
    # Trouver le dernier fichier de recherche
    search_dir = Path(__file__).parent.parent / "Configuration" / "SearchResults"
    
    if not search_dir.exists():
        print("❌ Dossier SearchResults introuvable")
        return
    
    json_files = sorted(search_dir.glob("search_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not json_files:
        print("❌ Aucun fichier de recherche trouvé")
        return
    
    # Si un argument est fourni, l'utiliser
    if len(sys.argv) > 1:
        target_file = Path(sys.argv[1])
        if target_file.exists():
            analyze_search_results(target_file)
        else:
            print(f"❌ Fichier non trouvé: {target_file}")
    else:
        # Sinon, prendre the plus récent
        latest_file = json_files[0]
        print(f"\n📄 Fichier le plus récent: {latest_file.name}")
        analyze_search_results(latest_file)


if __name__ == "__main__":
    main()