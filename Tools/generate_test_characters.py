"""
Script de génération de personnages de test pour DAOC Character Manager
Crée 20 personnages avec des attributs aléatoires pour tester l'application

Version v0.104 - Utilise la nouvelle structure Season/Realm
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


# Prénoms aléatoires pour générer des noms de personnages
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
    if roll < 0.3:  # 30% ont peu de RP (1L0 à 3L9)
        return random.randint(0, 100000)
    elif roll < 0.6:  # 30% ont des RP moyens (4L0 à 7L9)
        return random.randint(100001, 500000)
    elif roll < 0.85:  # 25% ont beaucoup de RP (8L0 à 11L9)
        return random.randint(500001, 2000000)
    else:  # 15% sont des vétérans (12L0+)
        return random.randint(2000001, 5000000)


def generate_character(data_manager, realms, servers, seasons):
    """Génère un personnage avec des attributs aléatoires"""
    
    # Sélection aléatoire du royaume
    realm = random.choice(realms)
    
    # Obtenir les classes disponibles pour ce royaume
    classes = data_manager.get_classes(realm)
    if not classes:
        print(f"Aucune classe trouvée pour {realm}")
        return None
    
    # Sélection aléatoire de la classe
    class_data = random.choice(classes)
    class_name = class_data.get("name", "Unknown")
    
    # Sélection aléatoire de la race (parmi celles disponibles pour cette classe)
    available_races = class_data.get("races", [])
    if not available_races:
        print(f"Aucune race disponible pour {class_name}")
        return None
    race = random.choice(available_races)
    
    # Sélection aléatoire de la spécialisation
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
    
    # Calculer le realm rank basé sur les RP
    rank_info = data_manager.get_realm_rank_info(realm, realm_points)
    realm_rank = rank_info['level'] if rank_info else "1L1"
    
    # Créer le dictionnaire du personnage
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
    """
    Sauvegarde un personnage dans le fichier JSON approprié
    Utilise la nouvelle structure: Characters/Season/Realm/Character.json
    """
    season = character['season']
    realm = character['realm']
    name = character['name']
    
    # Créer la structure Season/Realm si elle n'existe pas
    season_realm_dir = os.path.join(base_path, "Characters", season, realm)
    os.makedirs(season_realm_dir, exist_ok=True)
    
    # Chemin du fichier
    filename = f"{name}.json"
    filepath = os.path.join(season_realm_dir, filename)
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(filepath):
        print(f"⚠️  Le personnage '{name}' existe déjà dans {season}/{realm}, génération d'un nouveau nom...")
        return False
    
    # Sauvegarder le fichier
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(character, f, indent=4, ensure_ascii=False)
    
    return True


def main():
    """Fonction principale"""
    print("=" * 70)
    print("Générateur de Personnages de Test - DAOC Character Manager v0.104")
    print("Structure: Season/Realm")
    print("=" * 70)
    print()
    
    # Initialiser le DataManager
    print("📚 Chargement des données...")
    data_manager = DataManager()
    
    # Récupérer les royaumes, serveurs et saisons
    realms = data_manager.get_realms()
    servers = config.get("servers", ["Eden", "Blackthorn"])
    seasons = config.get("seasons", ["S1", "S2", "S3"])
    
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
    
    stats = {realm: {season: 0 for season in seasons} for realm in realms}
    
    while generated < num_characters and attempts < max_attempts:
        attempts += 1
        
        # Générer un personnage
        character = generate_character(data_manager, realms, servers, seasons)
        
        if character is None:
            continue
        
        # Sauvegarder le personnage
        if save_character(character, base_path):
            generated += 1
            stats[character['realm']][character['season']] += 1
            
            print(f"✅ [{generated:2d}/{num_characters}] {character['name']:25s} | "
                  f"{character['season']:3s} | {character['realm']:10s} | "
                  f"{character['class']:15s} | Niv.{character['level']:2d} | "
                  f"{character['realm_rank']:5s} | {character['realm_points']:,} RP")
    
    print()
    print("=" * 70)
    print(f"✨ Génération terminée ! {generated} personnages créés.")
    print()
    print("📊 Répartition par royaume et saison:")
    for realm in realms:
        total_realm = sum(stats[realm].values())
        if total_realm > 0:
            print(f"   {realm:10s}: {total_realm} personnages")
            for season in seasons:
                count = stats[realm][season]
                if count > 0:
                    print(f"      └─ {season}: {count}")
    print()
    print(f"💾 Personnages sauvegardés dans: {os.path.join(base_path, 'Characters')}")
    print(f"📁 Structure: Characters/Season/Realm/Character.json")
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


# Prénoms aléatoires pour générer des noms de personnages

FIRST_NAMES = [

# Prénoms aléatoires pour générer des noms de personnages    "Aragorn", "Legolas", "Gimli", "Gandalf", "Frodo", "Sam", "Merry", "Pippin",

FIRST_NAMES = [    "Boromir", "Faramir", "Eowyn", "Eomer", "Theoden", "Arwen", "Elrond", "Galadriel",

    "Aragorn", "Legolas", "Gimli", "Gandalf", "Frodo", "Sam", "Merry", "Pippin",    "Thorin", "Bilbo", "Bard", "Thranduil", "Tauriel", "Kili", "Fili", "Balin",

    "Boromir", "Faramir", "Eowyn", "Eomer", "Theoden", "Arwen", "Elrond", "Galadriel",    "Dwalin", "Oin", "Gloin", "Bifur", "Bofur", "Bombur", "Nori", "Dori", "Ori",

    "Thorin", "Bilbo", "Bard", "Thranduil", "Tauriel", "Kili", "Fili", "Balin",    "Radagast", "Saruman", "Grima", "Celeborn", "Haldir", "Rumil", "Orophin"

    "Dwalin", "Oin", "Gloin", "Bifur", "Bofur", "Bombur", "Nori", "Dori", "Ori",]

    "Radagast", "Saruman", "Grima", "Celeborn", "Haldir", "Rumil", "Orophin"

]SUFFIXES = [

    "le Brave", "le Sage", "le Rapide", "le Fort", "l'Ancien", "le Jeune",

SUFFIXES = [    "Coeur-de-Lion", "Main-d'Acier", "Oeil-de-Faucon", "Pied-Léger", "Bouclier-de-Fer",

    "le Brave", "le Sage", "le Rapide", "le Fort", "l'Ancien", "le Jeune",    "Lame-Tranchante", "Arc-Vif", "Marteau-Tonnant", "Ombre-Furtive", "Lumière-Brillante"

    "Coeur-de-Lion", "Main-d'Acier", "Oeil-de-Faucon", "Pied-Léger", "Bouclier-de-Fer",]

    "Lame-Tranchante", "Arc-Vif", "Marteau-Tonnant", "Ombre-Furtive", "Lumière-Brillante"

]

def get_random_name():

    """Génère un nom de personnage aléatoire"""

def get_random_name():    first = random.choice(FIRST_NAMES)

    """Génère un nom de personnage aléatoire"""    if random.random() > 0.5:

    first = random.choice(FIRST_NAMES)        return f"{first}-{random.choice(SUFFIXES)}"

    if random.random() > 0.5:    else:

        return f"{first}-{random.choice(SUFFIXES)}"        return f"{first}{random.randint(1, 999)}"

    else:

        return f"{first}{random.randint(1, 999)}"

def get_random_realm_points():

    """Génère des realm points aléatoires"""

def get_random_realm_points():    # Distribution réaliste des RP

    """Génère des realm points aléatoires"""    roll = random.random()

    # Distribution réaliste des RP    if roll < 0.3:  # 30% ont peu de RP (1L0 à 3L9)

    roll = random.random()        return random.randint(0, 100000)

    if roll < 0.3:  # 30% ont peu de RP (1L0 à 3L9)    elif roll < 0.6:  # 30% ont des RP moyens (4L0 à 7L9)

        return random.randint(0, 100000)        return random.randint(100001, 500000)

    elif roll < 0.6:  # 30% ont des RP moyens (4L0 à 7L9)    elif roll < 0.85:  # 25% ont beaucoup de RP (8L0 à 11L9)

        return random.randint(100001, 500000)        return random.randint(500001, 2000000)

    elif roll < 0.85:  # 25% ont beaucoup de RP (8L0 à 11L9)    else:  # 15% sont des vétérans (12L0+)

        return random.randint(500001, 2000000)        return random.randint(2000001, 5000000)

    else:  # 15% sont des vétérans (12L0+)

        return random.randint(2000001, 5000000)

def generate_character(data_manager, realms, servers, seasons):

    """Génère un personnage avec des attributs aléatoires"""

def generate_character(data_manager, realms, servers, seasons):    

    """Génère un personnage avec des attributs aléatoires"""    # Sélection aléatoire du royaume

        realm = random.choice(realms)

    # Sélection aléatoire du royaume    

    realm = random.choice(realms)    # Obtenir les classes disponibles pour ce royaume

        classes = data_manager.get_classes(realm)

    # Obtenir les classes disponibles pour ce royaume    if not classes:

    classes = data_manager.get_classes(realm)        print(f"Aucune classe trouvée pour {realm}")

    if not classes:        return None

        print(f"Aucune classe trouvée pour {realm}")    

        return None    # Sélection aléatoire de la classe

        class_data = random.choice(classes)

    # Sélection aléatoire de la classe    class_name = class_data.get("name", "Unknown")

    class_data = random.choice(classes)    

    class_name = class_data.get("name", "Unknown")    # Sélection aléatoire de la race (parmi celles disponibles pour cette classe)

        available_races = class_data.get("races", [])

    # Sélection aléatoire de la race (parmi celles disponibles pour cette classe)    if not available_races:

    available_races = class_data.get("races", [])        print(f"Aucune race disponible pour {class_name}")

    if not available_races:        return None

        print(f"Aucune race disponible pour {class_name}")    race = random.choice(available_races)

        return None    

    race = random.choice(available_races)    # Sélection aléatoire de la spécialisation

        specializations = class_data.get("specializations", [])

    # Sélection aléatoire de la spécialisation    spec = ""

    specializations = class_data.get("specializations", [])    if specializations:

    spec = ""        spec_data = random.choice(specializations)

    if specializations:        spec = spec_data.get("name", "")

        spec_data = random.choice(specializations)    

        spec = spec_data.get("name", "")    # Génération des autres attributs

        name = get_random_name()

    # Génération des autres attributs    level = random.randint(1, 50)

    name = get_random_name()    season = random.choice(seasons)

    level = random.randint(1, 50)    server = random.choice(servers)

    season = random.choice(seasons)    page = random.randint(1, 5)

    server = random.choice(servers)    realm_points = get_random_realm_points()

    page = random.randint(1, 5)    

    realm_points = get_random_realm_points()    # Guilde (50% ont une guilde)

        guilds = ["Les Chevaliers", "Les Guerriers", "Les Mages", "Les Voleurs", 

    # Guilde (50% ont une guilde)              "Les Paladins", "Les Dragons", "Les Loups", "Les Aigles"]

    guilds = ["Les Chevaliers", "Les Guerriers", "Les Mages", "Les Voleurs",     guild = random.choice(guilds) if random.random() > 0.5 else ""

              "Les Paladins", "Les Dragons", "Les Loups", "Les Aigles"]    

    guild = random.choice(guilds) if random.random() > 0.5 else ""    # Calculer le realm rank basé sur les RP

        rank_info = data_manager.get_realm_rank_info(realm, realm_points)

    # Calculer le realm rank basé sur les RP    realm_rank = rank_info['level'] if rank_info else "1L1"

    rank_info = data_manager.get_realm_rank_info(realm, realm_points)    

    realm_rank = rank_info['level'] if rank_info else "1L1"    # Créer le dictionnaire du personnage

        character = {

    # Créer le dictionnaire du personnage        'id': name,

    character = {        'uuid': str(uuid.uuid4()),

        'id': name,        'name': name,

        'uuid': str(uuid.uuid4()),        'realm': realm,

        'name': name,        'race': race,

        'realm': realm,        'class': class_name,

        'race': race,        'specialization': spec,

        'class': class_name,        'level': level,

        'specialization': spec,        'season': season,

        'level': level,        'server': server,

        'season': season,        'realm_rank': realm_rank,

        'server': server,        'realm_points': realm_points,

        'realm_rank': realm_rank,        'page': page,

        'realm_points': realm_points,        'guild': guild

        'page': page,    }

        'guild': guild    

    }    return character

    

    return character

def save_character(character, base_path):

    """Sauvegarde un personnage dans le fichier JSON approprié"""

def save_character(character, base_path):    realm = character['realm']

    """    name = character['name']

    Sauvegarde un personnage dans le fichier JSON approprié    

    Utilise la nouvelle structure: Characters/Season/Realm/Character.json    # Créer le dossier du royaume s'il n'existe pas

    """    realm_dir = os.path.join(base_path, "Characters", realm)

    season = character['season']    os.makedirs(realm_dir, exist_ok=True)

    realm = character['realm']    

    name = character['name']    # Chemin du fichier

        filename = f"{name}.json"

    # Créer la structure Season/Realm si elle n'existe pas    filepath = os.path.join(realm_dir, filename)

    season_realm_dir = os.path.join(base_path, "Characters", season, realm)    

    os.makedirs(season_realm_dir, exist_ok=True)    # Vérifier si le fichier existe déjà

        if os.path.exists(filepath):

    # Chemin du fichier        print(f"⚠️  Le personnage '{name}' existe déjà, génération d'un nouveau nom...")

    filename = f"{name}.json"        return False

    filepath = os.path.join(season_realm_dir, filename)    

        # Sauvegarder le fichier

    # Vérifier si le fichier existe déjà    with open(filepath, 'w', encoding='utf-8') as f:

    if os.path.exists(filepath):        json.dump(character, f, indent=4, ensure_ascii=False)

        print(f"⚠️  Le personnage '{name}' existe déjà dans {season}/{realm}, génération d'un nouveau nom...")    

        return False    return True

    

    # Sauvegarder le fichier

    with open(filepath, 'w', encoding='utf-8') as f:def main():

        json.dump(character, f, indent=4, ensure_ascii=False)    """Fonction principale"""

        print("=" * 70)

    return True    print("Générateur de Personnages de Test - DAOC Character Manager")

    print("=" * 70)

    print()

def main():    

    """Fonction principale"""    # Initialiser le DataManager

    print("=" * 70)    print("📚 Chargement des données...")

    print("Générateur de Personnages de Test - DAOC Character Manager v0.104")    data_manager = DataManager()

    print("Structure: Season/Realm")    

    print("=" * 70)    # Récupérer les royaumes, serveurs et saisons

    print()    realms = data_manager.get_realms()

        servers = config.get("servers", ["Eden", "Blackthorn"])

    # Initialiser le DataManager    seasons = config.get("seasons", ["S1", "S2", "S3"])

    print("📚 Chargement des données...")    

    data_manager = DataManager()    print(f"   Royaumes: {', '.join(realms)}")

        print(f"   Serveurs: {', '.join(servers)}")

    # Récupérer les royaumes, serveurs et saisons    print(f"   Saisons: {', '.join(seasons)}")

    realms = data_manager.get_realms()    print()

    servers = config.get("servers", ["Eden", "Blackthorn"])    

    seasons = config.get("seasons", ["S1", "S2", "S3"])    # Obtenir le chemin de base

        base_path = get_base_path()

    print(f"   Royaumes: {', '.join(realms)}")    

    print(f"   Serveurs: {', '.join(servers)}")    # Générer 20 personnages

    print(f"   Saisons: {', '.join(seasons)}")    num_characters = 20

    print()    print(f"🎲 Génération de {num_characters} personnages de test...")

        print()

    # Obtenir le chemin de base    

    base_path = get_base_path()    generated = 0

        attempts = 0

    # Générer 20 personnages    max_attempts = num_characters * 3  # Limiter les tentatives

    num_characters = 20    

    print(f"🎲 Génération de {num_characters} personnages de test...")    stats = {realm: 0 for realm in realms}

    print()    

        while generated < num_characters and attempts < max_attempts:

    generated = 0        attempts += 1

    attempts = 0        

    max_attempts = num_characters * 3  # Limiter les tentatives        # Générer un personnage

            character = generate_character(data_manager, realms, servers, seasons)

    stats = {realm: {season: 0 for season in seasons} for realm in realms}        

            if character is None:

    while generated < num_characters and attempts < max_attempts:            continue

        attempts += 1        

                # Sauvegarder le personnage

        # Générer un personnage        if save_character(character, base_path):

        character = generate_character(data_manager, realms, servers, seasons)            generated += 1

                    stats[character['realm']] += 1

        if character is None:            

            continue            print(f"✅ [{generated:2d}/{num_characters}] {character['name']:25s} | "

                          f"{character['realm']:10s} | {character['class']:15s} | "

        # Sauvegarder le personnage                  f"Niv.{character['level']:2d} | {character['realm_rank']:5s} | "

        if save_character(character, base_path):                  f"{character['realm_points']:,} RP")

            generated += 1    

            stats[character['realm']][character['season']] += 1    print()

                print("=" * 70)

            print(f"✅ [{generated:2d}/{num_characters}] {character['name']:25s} | "    print(f"✨ Génération terminée ! {generated} personnages créés.")

                  f"{character['season']:3s} | {character['realm']:10s} | "    print()

                  f"{character['class']:15s} | Niv.{character['level']:2d} | "    print("📊 Répartition par royaume:")

                  f"{character['realm_rank']:5s} | {character['realm_points']:,} RP")    for realm, count in stats.items():

            print(f"   {realm:10s}: {count} personnages")

    print()    print()

    print("=" * 70)    print(f"💾 Personnages sauvegardés dans: {os.path.join(base_path, 'Characters')}")

    print(f"✨ Génération terminée ! {generated} personnages créés.")    print("=" * 70)

    print()

    print("📊 Répartition par royaume et saison:")

    for realm in realms:if __name__ == "__main__":

        total_realm = sum(stats[realm].values())    try:

        if total_realm > 0:        main()

            print(f"   {realm:10s}: {total_realm} personnages")    except KeyboardInterrupt:

            for season in seasons:        print("\n\n⚠️  Génération interrompue par l'utilisateur.")

                count = stats[realm][season]    except Exception as e:

                if count > 0:        print(f"\n❌ Erreur: {e}")

                    print(f"      └─ {season}: {count}")        import traceback

    print()        traceback.print_exc()

    print(f"💾 Personnages sauvegardés dans: {os.path.join(base_path, 'Characters')}")
    print(f"📁 Structure: Characters/Season/Realm/Character.json")
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
