"""
Data Manager - Gestionnaire pour les données statiques du jeu DAOC
Charge et fournit un accès facile aux Realm Ranks et autres données du jeu
"""
import json
import os
from typing import Dict, List, Optional

class DataManager:
    """Gestionnaire des données statiques du jeu DAOC"""
    
    def __init__(self, data_folder: str = "Data"):
        """
        Initialise le Data Manager
        
        Args:
            data_folder: Chemin vers le dossier contenant les fichiers de données
        """
        self.data_folder = data_folder
        self.realm_ranks = None
        
    def load_realm_ranks(self) -> Dict[str, List[Dict]]:
        """
        Charge les données de Realm Ranks depuis le fichier JSON
        
        Returns:
            Dictionnaire avec les rangs par royaume (Albion, Hibernia, Midgard)
        """
        if self.realm_ranks is None:
            file_path = os.path.join(self.data_folder, "realm_ranks.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self.realm_ranks = json.load(f)
        return self.realm_ranks
    
    def get_realm_rank_info(self, realm: str, realm_points: int) -> Optional[Dict]:
        """
        Récupère les informations du Realm Rank en fonction des points de royaume
        
        Args:
            realm: Nom du royaume ("Albion", "Hibernia", "Midgard")
            realm_points: Nombre de points de royaume du joueur
            
        Returns:
            Dictionnaire avec les infos du rang (rank, title, level, etc.) ou None
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return None
        
        realm_data = ranks[realm]
        
        # Trouver le rang correspondant aux points (le plus haut rank atteint)
        current_rank = None
        for rank_info in realm_data:
            if realm_points >= rank_info['realm_points']:
                current_rank = rank_info
            else:
                break
        
        return current_rank
    
    def get_next_realm_rank(self, realm: str, current_realm_points: int) -> Optional[Dict]:
        """
        Récupère les informations du prochain Realm Rank à atteindre
        
        Args:
            realm: Nom du royaume
            current_realm_points: Points de royaume actuels
            
        Returns:
            Dictionnaire avec les infos du prochain rang ou None si max rank
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return None
        
        realm_data = ranks[realm]
        
        # Trouver le prochain rang
        for rank_info in realm_data:
            if rank_info['realm_points'] > current_realm_points:
                return rank_info
        
        return None  # Max rank atteint
    
    def get_rank_by_level(self, realm: str, level: str) -> Optional[Dict]:
        """
        Récupère les informations d'un Realm Rank par son niveau (ex: "5L7")
        
        Args:
            realm: Nom du royaume
            level: Niveau du rang (format "XLY", ex: "5L7")
            
        Returns:
            Dictionnaire avec les infos du rang ou None
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return None
        
        for rank_info in ranks[realm]:
            if rank_info['level'] == level:
                return rank_info
        
        return None
    
    def calculate_rp_needed(self, realm: str, current_rp: int, target_rank: int) -> int:
        """
        Calcule le nombre de points de royaume nécessaires pour atteindre un rang cible
        
        Args:
            realm: Nom du royaume
            current_rp: Points de royaume actuels
            target_rank: Rang cible (1-14)
            
        Returns:
            Nombre de points nécessaires (0 si déjà atteint)
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return 0
        
        # Trouver le premier niveau du rang cible
        for rank_info in ranks[realm]:
            if rank_info['rank'] == target_rank:
                rp_needed = rank_info['realm_points'] - current_rp
                return max(0, rp_needed)
        
        return 0
    
    def get_all_ranks_summary(self, realm: str) -> List[Dict]:
        """
        Récupère un résumé de tous les rangs (premier niveau de chaque rang uniquement)
        
        Args:
            realm: Nom du royaume
            
        Returns:
            Liste des rangs avec leurs informations de base
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return []
        
        summary = []
        seen_ranks = set()
        
        for rank_info in ranks[realm]:
            rank_num = rank_info['rank']
            if rank_num not in seen_ranks:
                summary.append({
                    'rank': rank_num,
                    'title': rank_info['title'],
                    'skill_bonus': rank_info['skill_bonus'],
                    'min_realm_points': rank_info['realm_points']
                })
                seen_ranks.add(rank_num)
        
        return summary


# Exemple d'utilisation
if __name__ == "__main__":
    dm = DataManager()
    
    print("=" * 70)
    print("Exemple d'utilisation du Data Manager")
    print("=" * 70)
    
    # Test 1: Obtenir le rang actuel d'un joueur
    print("\n1. Joueur Albion avec 50,000 Realm Points:")
    rank_info = dm.get_realm_rank_info("Albion", 50000)
    if rank_info:
        print(f"   Rang: {rank_info['rank']} ({rank_info['title']})")
        print(f"   Niveau: {rank_info['level']}")
        print(f"   Bonus compétences: +{rank_info['skill_bonus']}")
        print(f"   Points d'aptitudes: {rank_info['realm_ability_points']}")
    
    # Test 2: Obtenir le prochain rang
    print("\n2. Prochain rang à atteindre:")
    next_rank = dm.get_next_realm_rank("Albion", 50000)
    if next_rank:
        print(f"   Prochain: {next_rank['level']} - {next_rank['title']}")
        print(f"   RP nécessaires: {next_rank['realm_points']}")
        print(f"   Manquants: {next_rank['realm_points'] - 50000}")
    
    # Test 3: Résumé de tous les rangs
    print("\n3. Résumé des rangs Hibernia:")
    summary = dm.get_all_ranks_summary("Hibernia")
    for rank in summary[:5]:  # Afficher les 5 premiers
        print(f"   Rank {rank['rank']}: {rank['title']} "
              f"(+{rank['skill_bonus']} skills, {rank['min_realm_points']:,} RP)")
    
    # Test 4: Calculer les RP nécessaires
    print("\n4. RP nécessaires pour atteindre Rank 10 depuis 100,000 RP:")
    rp_needed = dm.calculate_rp_needed("Midgard", 100000, 10)
    print(f"   RP à gagner: {rp_needed:,}")
    
    print("\n" + "=" * 70)
