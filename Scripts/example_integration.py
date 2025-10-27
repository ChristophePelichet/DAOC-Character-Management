"""
Exemple d'intégration du Data Manager avec le Character Manager
Démontre comment afficher les informations de Realm Rank d'un personnage
"""

import os
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.character_manager import get_all_characters
from Functions.data_manager import DataManager

def display_character_realm_info(character_data):
    """
    Affiche les informations de Realm Rank pour un personnage
    
    Args:
        character_data: Dictionnaire contenant les données du personnage
    """
    character_name = character_data.get('name', 'Inconnu')
    realm = character_data.get('realm', 'Inconnu')
    print("=" * 70)
    print(f"Informations de Realm Rank - {character_name} ({realm})")
    print("=" * 70)
    
    # Récupérer les Realm Points (si disponibles)
    realm_points = character_data.get('realm_points', 0)
    current_rank_level = character_data.get('realm_rank', '1L1')
    
    print(f"\n📊 Statut actuel:")
    print(f"   Niveau: {character_data.get('level', 1)}")
    print(f"   Realm Points: {realm_points:,}")
    print(f"   Realm Rank: {current_rank_level}")
    
    # Initialiser le Data Manager
    dm = DataManager()
    
    # Obtenir les informations du rang actuel
    current_rank_info = dm.get_realm_rank_info(realm, realm_points)
    if current_rank_info:
        print(f"\n🏆 Rang actuel:")
        print(f"   Rank {current_rank_info['rank']}: {current_rank_info['title']}")
        print(f"   Niveau: {current_rank_info['level']}")
        print(f"   Bonus compétences: +{current_rank_info['skill_bonus']}")
        print(f"   Points d'aptitudes: {current_rank_info['realm_ability_points']}")
    
    # Obtenir le prochain rang
    next_rank = dm.get_next_realm_rank(realm, realm_points)
    if next_rank:
        rp_needed = next_rank['realm_points'] - realm_points
        percentage = (realm_points / next_rank['realm_points']) * 100 if next_rank['realm_points'] > 0 else 100
        
        print(f"\n⬆️  Prochain rang:")
        print(f"   Niveau: {next_rank['level']}")
        print(f"   Titre: {next_rank['title']}")
        print(f"   RP nécessaires: {next_rank['realm_points']:,}")
        print(f"   RP manquants: {rp_needed:,}")
        print(f"   Progression: {percentage:.1f}%")
        
        # Barre de progression visuelle
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"   [{bar}] {percentage:.1f}%")
    else:
        print(f"\n🎖️  Rang maximum atteint!")
    
    print("\n" + "=" * 70)

def display_all_characters_ranks():
    """Affiche un résumé des rangs de tous les personnages"""
    print("=" * 70)
    print("Résumé des Realm Ranks de tous les personnages")
    print("=" * 70)
    
    characters = get_all_characters()
    if not characters:
        print("\n❌ Aucun personnage trouvé")
        return
    
    dm = DataManager()
    
    print(f"\n{len(characters)} personnage(s) trouvé(s):\n")
    
    for char in characters:
        name = char.get('name', 'Inconnu')
        realm = char.get('realm', 'Inconnu')
        level = char.get('level', 1)
        rp = char.get('realm_points', 0)
        
        # Obtenir le rang
        rank_info = dm.get_realm_rank_info(realm, rp)
        if rank_info:
            rank_display = f"Rank {rank_info['rank']} - {rank_info['title']}"
        else:
            rank_display = "Non défini"
        
        print(f"  • {name:20} | {realm:10} | Lvl {level:2} | {rp:>10,} RP | {rank_display}")
    
    print("\n" + "=" * 70)

def display_rank_summary(realm):
    """Affiche un résumé de tous les rangs d'un royaume"""
    print("=" * 70)
    print(f"Résumé des Realm Ranks - {realm}")
    print("=" * 70)
    
    dm = DataManager()
    summary = dm.get_all_ranks_summary(realm)
    
    if not summary:
        print(f"❌ Aucune donnée trouvée pour {realm}")
        return
    
    print(f"\n{len(summary)} rangs disponibles:\n")
    print(f"{'Rank':<6} {'Titre':<30} {'Bonus':<10} {'RP Min':<15}")
    print("-" * 70)
    
    for rank in summary:
        print(f"{rank['rank']:<6} {rank['title']:<30} "
              f"+{rank['skill_bonus']:<9} {rank['min_realm_points']:>14,}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n🎮 Exemples d'intégration Data Manager + Character Manager\n")
    
    # Exemple 1: Afficher les infos d'un personnage spécifique
    print("\n" + "=" * 70)
    print("EXEMPLE 1: Informations détaillées d'un personnage")
    print("=" * 70)
    characters = get_all_characters()
    if characters:
        first_char = characters[0]
        display_character_realm_info(first_char)
    else:
        print("\n⚠️  Aucun personnage disponible. Créez d'abord des personnages.")
    
    # Exemple 2: Résumé de tous les personnages
    print("\n")
    display_all_characters_ranks()
    
    # Exemple 3: Afficher le résumé des rangs d'un royaume
    print("\n")
    display_rank_summary("Albion")
    
    print("\n\n💡 Vous pouvez utiliser ces fonctions dans votre interface utilisateur!")
