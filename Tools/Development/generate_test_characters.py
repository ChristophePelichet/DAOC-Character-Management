#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de génération de personnages de test pour DAOC Character Manager
Génère des fichiers JSON de test dans les dossiers Albion/Hibernia/Midgard
"""

import json
import os
import random

def generate_test_characters():
    # Configuration
    base_path = "Characters"
    realms = ["Albion", "Hibernia", "Midgard"]
    
    # Classes par royaume
    classes_by_realm = {
        "Albion": ["Armsman", "Cabalist", "Cleric", "Friar", "Infiltrator", "Mercenary", "Minstrel", "Paladin", "Scout", "Sorcerer", "Theurgist", "Wizard"],
        "Hibernia": ["Animist", "Bard", "Blademaster", "Champion", "Druid", "Eldritch", "Enchanter", "Hero", "Mentalist", "Nightshade", "Ranger", "Warden"],
        "Midgard": ["Berserker", "Bonedancer", "Healer", "Hunter", "Runemaster", "Savage", "Shadowblade", "Shaman", "Skald", "Spiritmaster", "Thane", "Warrior"]
    }
    
    # Races par royaume
    races_by_realm = {
        "Albion": ["Avalonian", "Briton", "Half Ogre", "Highlander", "Inconnu", "Saracen"],
        "Hibernia": ["Celt", "Elf", "Firbolg", "Lurikeen", "Shar"],
        "Midgard": ["Dwarf", "Frostalf", "Kobold", "Norseman", "Troll", "Valkyn"]
    }
    
    # Rangs de royaume
    realm_ranks = {
        "Albion": ["Herald", "Guardian", "Champion", "Knight"],
        "Hibernia": ["Savant", "Cosantoir", "Brehon", "Grove Protector"],
        "Midgard": ["Heidgelt", "Skyttur", "Hersar", "Hersir"]
    }
    
    # Guildes
    guilds = ["Les Gardiens", "Warriors of Light", "Dark Brotherhood", "Phoenix Rising", "Storm Riders", ""]
    
    # Générer 3 personnages par royaume
    for realm in realms:
        realm_path = os.path.join(base_path, realm)
        os.makedirs(realm_path, exist_ok=True)
        
        for i in range(1, 4):
            # Structure ANCIENNE VERSION (avant v0.105) pour tester la migration
            character = {
                "id": f"{realm}_Test_{i}",
                "name": f"Test{realm}{i}",
                "realm": realm,
                "class": random.choice(classes_by_realm[realm]),
                "race": random.choice(races_by_realm[realm]),
                "level": random.randint(1, 50),
                "season": "S3",
                "server": "Eden",
                "page": random.randint(1, 5),
                "guild": random.choice(guilds),
                "realm_rank": random.choice(realm_ranks[realm]),
                "realm_points": f"{random.randint(0, 100000):,}".replace(",", " ")  # Ancien format avec espaces
            }
            
            # Sauvegarder le fichier JSON
            filename = f"{realm}_Test_{i}.json"
            filepath = os.path.join(realm_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character, f, indent=4, ensure_ascii=False)
            
            print(f" Créé: {filepath}")

if __name__ == "__main__":
    print(" Génération de personnages de test...")
    generate_test_characters()
    print(" Terminé!")
