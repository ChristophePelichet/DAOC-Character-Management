#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de visualisation des résultats de recherche Herald
Affiche de manière formatée les fichiers JSON générés par la recherche
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def list_search_files():
    """Liste tous les fichiers de recherche disponibles"""
    # Trouver le dossier SearchResults
    script_dir = Path(__file__).parent
    config_dir = script_dir.parent / "Configuration"
    search_dir = config_dir / "SearchResults"
    
    if not search_dir.exists():
        print("❌ Aucun dossier SearchResults trouvé.")
        print(f"📁 Chemin attendu: {search_dir}")
        return []
    
    # Lister les fichiers JSON
    json_files = sorted(search_dir.glob("search_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not json_files:
        print("❌ Aucun fichier de recherche trouvé.")
        return []
    
    print(f"\n📁 Dossier des recherches: {search_dir}")
    print(f"📊 {len(json_files)} fichier(s) trouvé(s)\n")
    print("=" * 80)
    
    for idx, file in enumerate(json_files, 1):
        stat = file.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"{idx}. {file.name}")
        print(f"   📅 Date: {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   💾 Taille: {size:,} octets")
        print()
    
    return json_files


def display_search_result(file_path):
    """Affiche le contenu formaté d'un fichier de recherche"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n" + "=" * 80)
        print(f"🔍 RÉSULTATS DE RECHERCHE")
        print("=" * 80)
        
        # Informations générales
        print(f"\n📝 Personnage recherché: {data.get('character_name', 'N/A')}")
        print(f"🔗 URL: {data.get('search_url', 'N/A')}")
        print(f"📅 Date: {data.get('timestamp', 'N/A')}")
        print(f"📊 Résultats: {len(data.get('results', []))} trouvé(s)")
        
        # Afficher les résultats
        results = data.get('results', [])
        
        if not results:
            print("\n⚠️  Aucun résultat trouvé.")
            return
        
        print("\n" + "-" * 80)
        print("DÉTAILS DES RÉSULTATS")
        print("-" * 80)
        
        for idx, result in enumerate(results, 1):
            print(f"\n🎯 Résultat #{idx}")
            print("-" * 40)
            
            # Afficher tous les champs
            for key, value in result.items():
                if not key.endswith('_links'):  # Ne pas afficher les liens séparément
                    print(f"  {key}: {value}")
                else:
                    # Afficher les liens
                    print(f"  {key}:")
                    for link in value:
                        print(f"    → {link}")
        
        print("\n" + "=" * 80)
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {file_path}")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de lecture JSON: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def display_json_raw(file_path):
    """Affiche le JSON brut formaté"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n" + "=" * 80)
        print("📄 JSON BRUT")
        print("=" * 80)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


def interactive_menu():
    """Menu interactif pour choisir un fichier"""
    files = list_search_files()
    
    if not files:
        return
    
    print("=" * 80)
    print("\n🎯 Que voulez-vous faire?")
    print("\n  1-{}: Afficher le résultat formaté".format(len(files)))
    print("  R: Afficher le JSON brut")
    print("  Q: Quitter")
    
    while True:
        try:
            choice = input("\n👉 Votre choix: ").strip().upper()
            
            if choice == 'Q':
                print("\n👋 Au revoir!")
                break
            
            if choice == 'R':
                file_num = input("📄 Numéro du fichier: ").strip()
                try:
                    idx = int(file_num) - 1
                    if 0 <= idx < len(files):
                        display_json_raw(files[idx])
                    else:
                        print(f"❌ Numéro invalide (1-{len(files)})")
                except ValueError:
                    print("❌ Veuillez entrer un numéro valide")
                continue
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    display_search_result(files[idx])
                else:
                    print(f"❌ Numéro invalide (1-{len(files)})")
            except ValueError:
                print("❌ Veuillez entrer un numéro valide ou 'Q' pour quitter")
                
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break


def main():
    """Point d'entrée principal"""
    print("\n" + "=" * 80)
    print("🔍 VISUALISEUR DE RÉSULTATS DE RECHERCHE HERALD")
    print("=" * 80)
    
    # Si un fichier est spécifié en argument
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if file_path.exists():
            display_search_result(file_path)
        else:
            print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    # Sinon, menu interactif
    interactive_menu()


if __name__ == "__main__":
    main()
