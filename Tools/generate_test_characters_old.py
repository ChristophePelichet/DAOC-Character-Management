"""
Script de génération de personnages de test pour DAOC Character Manager
Crée 20 personnages avec des attributs aléatoires pour tester l'application
"""

import os
import sys
import json
import random
import uuid

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Functions.data_manager import DataManager
from Functions.config_manager import config
from Functions.path_manager import get_base_path


# Prénoms aléatoires for générer des noms of personnages
FIRST_NAMES = [
    "Aragorn", "Legolas", "Gimli", "Gandalf", "Frodo", "Sam", "Merry", "Pippin",
    "Boromir", "Faramir", "Eowyn", "Eomer", "Theoden", "Arwen", "Elrond", "Galadriel",
    "Thorin", "Bilbo", "Bard", "Thranduil", "Tauriel", "Kili", "Fili", "Balin",
    "Dwalin", "Oin", "Gloin", "Bifur", "Bofur", "Bombur", "Nori", "Dori", "Ori",
    "Radagast", "Saruman", "Grima", "Celeborn", "Haldir", "Rumil", "Orophin"
]

SUFFIXES = [
    "le Brave", "le Sage", "le Rapide", "le Fort", "l'Ancien", "le Jeune",
    "Coeur-de-Lion", "Main-d'Acier", "Oeil-de-Faucon", "Pied-Léger", "Bouclier-de-Fer",
    "Lame-Tranchante", "Arc-Vif", "Marteau-Tonnant", "Ombre-Furtive", "Lumière-Brillante"
]


def get_random_name():
    """Génère un nom de personnage aléatoire"""
    first = random.choice(FIRST_NAMES)
    if random.random() > 0.5:
        return f"{first}-{random.choice(SUFFIXES)}"
    else:
        return f"{first}{random.randint(1, 999)}"


def get_random_realm_points():
    """Génère des realm points aléatoires"""
    # Distribution réaliste des RP
    roll = random.random()
    if roll < 0.3:  # 30% have peu of RP (1L0 à 3L9)
        return random.randint(0, 100000)
    elif roll < 0.6:  # 30% have des RP moyens (4L0 à 7L9)
        return random.randint(100001, 500000)
    elif roll < 0.85:  # 25% have beaucoup of RP (8L0 à 11L9)
        return random.randint(500001, 2000000)
    else:  # 15% sont des vétérans (12L0+)
        return random.randint(2000001, 5000000)


def generate_character(data_manager, realms, servers, seasons):
    """Génère un personnage avec des attributs aléatoires"""
    
    # Sélection aléatoire of the royaume
    realm = random.choice(realms)
    
    # Obtenir les classes disponibles pour ce royaume
    classes = data_manager.get_classes(realm)
    if not classes:
        print(f"Aucune classe trouvée pour {realm}")
        return None
    
    # Sélection aléatoire of the classe
    class_data = random.choice(classes)
    class_name = class_data.get("name", "Unknown")
    
    # Sélection aléatoire of the race (parmi celles disponibles for this classe)
    available_races = class_data.get("races", [])
    if not available_races:
        print(f"Aucune race disponible pour {class_name}")
        return None
    race = random.choice(available_races)
    
    # Sélection aléatoire of the spécialisation
    specializations = class_data.get("specializations", [])
    spec = ""
    if specializations:
        spec_data = random.choice(specializations)
        spec = spec_data.get("name", "")
    
    # Génération des autres attributs
    name = get_random_name()
    level = random.randint(1, 50)
    season = random.choice(seasons)
    server = random.choice(servers)
    page = random.randint(1, 5)
    realm_points = get_random_realm_points()
    
    # Guilde (50% ont une guilde)
    guilds = ["Les Chevaliers", "Les Guerriers", "Les Mages", "Les Voleurs", 
              "Les Paladins", "Les Dragons", "Les Loups", "Les Aigles"]
    guild = random.choice(guilds) if random.random() > 0.5 else ""
    
    # Calculer the realm rank basé on the RP
    rank_info = data_manager.get_realm_rank_info(realm, realm_points)
    realm_rank = rank_info['level'] if rank_info else "1L1"
    
    # Create the dictionnaire of the personnage
    character = {
        'id': name,
        'uuid': str(uuid.uuid4()),
        'name': name,
        'realm': realm,
        'race': race,
        'class': class_name,
        'specialization': spec,
        'level': level,
        'season': season,
        'server': server,
        'realm_rank': realm_rank,
        'realm_points': realm_points,
        'page': page,
        'guild': guild
    }
    
    return character


def save_character(character, base_path):
    """Sauvegarde un personnage dans le fichier JSON approprié"""
    realm = character['realm']
    name = character['name']
    
    # Create the Folder of the royaume s'il n'existe not
    realm_dir = os.path.join(base_path, "Characters", realm)
    os.makedirs(realm_dir, exist_ok=True)
    
    # Chemin du fichier
    filename = f"{name}.json"
    filepath = os.path.join(realm_dir, filename)
    
    # Check if the File existe déjà
    if os.path.exists(filepath):
        print(f"⚠️  Le personnage '{name}' existe déjà, génération d'un nouveau nom...")
        return False
    
    # Sauvegarder le fichier
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(character, f, indent=4, ensure_ascii=False)
    
    return True


def main():
    """Fonction principale"""
    print("=" * 70)
    print("Générateur de Personnages de Test - DAOC Character Manager")
    print("=" * 70)
    print()
    
    # Initialiser le DataManager
    print("📚 Chargement des données...")
    data_manager = DataManager()
    
    # Retrieve the royaumes, serveurs and saisons
    realms = data_manager.get_realms()
    servers = config.get("servers", ["Eden"])
    seasons = config.get("seasons", ["S3"])
    
    print(f"   Royaumes: {', '.join(realms)}")
    print(f"   Serveurs: {', '.join(servers)}")
    print(f"   Saisons: {', '.join(seasons)}")
    print()
    
    # Obtenir le chemin de base
    base_path = get_base_path()
    
    # Générer 20 personnages
    num_characters = 20
    print(f"🎲 Génération de {num_characters} personnages de test...")
    print()
    
    generated = 0
    attempts = 0
    max_attempts = num_characters * 3  # Limiter les tentatives
    
    stats = {realm: 0 for realm in realms}
    
    while generated < num_characters and attempts < max_attempts:
        attempts += 1
        
        # Générer un personnage
        character = generate_character(data_manager, realms, servers, seasons)
        
        if character is None:
            continue
        
        # Sauvegarder le personnage
        if save_character(character, base_path):
            generated += 1
            stats[character['realm']] += 1
            
            print(f"✅ [{generated:2d}/{num_characters}] {character['name']:25s} | "
                  f"{character['realm']:10s} | {character['class']:15s} | "
                  f"Niv.{character['level']:2d} | {character['realm_rank']:5s} | "
                  f"{character['realm_points']:,} RP")
    
    print()
    print("=" * 70)
    print(f"✨ Génération terminée ! {generated} personnages créés.")
    print()
    print("📊 Répartition par royaume:")
    for realm, count in stats.items():
        print(f"   {realm:10s}: {count} personnages")
    print()
    print(f"💾 Personnages sauvegardés dans: {os.path.join(base_path, 'Characters')}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Génération interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()