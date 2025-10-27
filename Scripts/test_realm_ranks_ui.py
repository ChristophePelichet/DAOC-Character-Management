"""
Script de test pour vérifier l'intégration des Realm Ranks
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Functions.data_manager import DataManager
from Functions.character_manager import get_all_characters

def test_realm_ranks_integration():
    """Teste l'intégration des Realm Ranks avec les personnages"""
    
    print("=" * 70)
    print("Test d'intégration des Realm Ranks")
    print("=" * 70)
    
    # Initialiser le DataManager
    dm = DataManager()
    
    # Charger tous les personnages
    characters = get_all_characters()
    
    if not characters:
        print("\n⚠️  Aucun personnage trouvé. Créez d'abord des personnages.")
        return
    
    print(f"\n✅ {len(characters)} personnage(s) trouvé(s)\n")
    
    # Afficher les informations de rang pour chaque personnage
    for char in characters:
        name = char.get('name', 'Inconnu')
        realm = char.get('realm', 'Inconnu')
        realm_points = char.get('realm_points', 0)
        
        print(f"{'='*70}")
        print(f"Personnage : {name}")
        print(f"Royaume : {realm}")
        print(f"Realm Points : {realm_points:,}")
        print(f"{'-'*70}")
        
        # Obtenir les infos de rang
        rank_info = dm.get_realm_rank_info(realm, realm_points)
        
        if rank_info:
            print(f"✓ Rang actuel :")
            print(f"  • Rank {rank_info['rank']} - {rank_info['title']}")
            print(f"  • Niveau : {rank_info['level']}")
            print(f"  • Bonus compétences : +{rank_info['skill_bonus']}")
            print(f"  • Points d'aptitudes : {rank_info['realm_ability_points']}")
            
            # Prochain rang
            next_rank = dm.get_next_realm_rank(realm, realm_points)
            if next_rank:
                rp_needed = next_rank['realm_points'] - realm_points
                percentage = (realm_points / next_rank['realm_points']) * 100
                
                print(f"\n→ Prochain rang :")
                print(f"  • {next_rank['level']} - {next_rank['title']}")
                print(f"  • RP nécessaires : {next_rank['realm_points']:,}")
                print(f"  • RP manquants : {rp_needed:,}")
                print(f"  • Progression : {percentage:.1f}%")
                
                # Barre de progression
                bar_length = 40
                filled = int(bar_length * percentage / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"  • [{bar}] {percentage:.1f}%")
            else:
                print(f"\n🎖️  Rang maximum atteint !")
        else:
            print(f"❌ Impossible de trouver les informations de rang")
        
        print()
    
    print("=" * 70)
    print("✅ Test terminé avec succès !")
    print("=" * 70)

if __name__ == "__main__":
    test_realm_ranks_integration()
