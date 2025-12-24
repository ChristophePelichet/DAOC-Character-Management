"""
Data Manager - Gestionnaire pour les données statiques du jeu DAOC
Charge et fournit un accès facile aux Realm Ranks et autres données du jeu
"""
import json
import os
from typing import Dict, List, Optional
from .path_manager import get_resource_path

class DataManager:
    """Gestionnaire des données statiques du jeu DAOC"""
    
    def __init__(self, data_folder: str = None):
        """
        Initialise le Data Manager
        
        Args:
            data_folder: Chemin vers le dossier contenant les fichiers de données
                        Si None, utilise le dossier Data bundlé avec l'application
        """
        if data_folder is None:
            # Use bundled Data folder (works in both dev and frozen mode)
            self.data_folder = get_resource_path("Data")
        else:
            self.data_folder = data_folder
        self.realm_ranks = None
        self.classes_races = None
        self._realms_cache = None
        
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
    
    def get_realm_rank_info(self, realm: str, realm_points) -> Optional[Dict]:
        """
        Récupère les informations du Realm Rank en fonction des points de royaume
        
        Args:
            realm: Nom du royaume ("Albion", "Hibernia", "Midgard")
            realm_points: Nombre de points de royaume du joueur (int ou str)
            
        Returns:
            Dictionnaire avec les infos du rang (rank, title, level, etc.) ou None
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return None
        
        # Convertir realm_points en entier (gérer the strings with espaces)
        try:
            if isinstance(realm_points, str):
                # Supprimer les espaces et convertir en int
                realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
            else:
                realm_points = int(realm_points)
        except (ValueError, AttributeError):
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
    
    def get_next_realm_rank(self, realm: str, current_realm_points) -> Optional[Dict]:
        """
        Récupère les informations du prochain Realm Rank à atteindre
        
        Args:
            realm: Nom du royaume
            current_realm_points: Points de royaume actuels (int ou str)
            
        Returns:
            Dictionnaire avec les infos du prochain rang ou None si max rank
        """
        ranks = self.load_realm_ranks()
        
        if realm not in ranks:
            return None
        
        # Convertir current_realm_points en entier (gérer the strings with espaces)
        try:
            if isinstance(current_realm_points, str):
                # Supprimer les espaces et convertir en int
                current_realm_points = int(current_realm_points.replace(' ', '').replace('\xa0', ''))
            else:
                current_realm_points = int(current_realm_points)
        except (ValueError, AttributeError):
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


    # ========================================================================
    # CLASSES & RACES MANAGEMENT
    # ========================================================================
    
    def get_realms(self) -> List[str]:
        """
        Récupère la liste des royaumes depuis les données JSON
        
        Returns:
            Liste des noms de royaumes (ex: ["Albion", "Hibernia", "Midgard"])
        """
        if self._realms_cache is None:
            data = self.load_classes_races()
            self._realms_cache = list(data.keys())
        return self._realms_cache
    
    def load_classes_races(self) -> Dict[str, Dict]:
        """
        Charge les données des races et classes depuis le fichier JSON
        
        Returns:
            Dictionnaire avec les races et classes par royaume (Albion, Hibernia, Midgard)
        """
        if self.classes_races is None:
            file_path = os.path.join(self.data_folder, "classes_races.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self.classes_races = json.load(f)
        return self.classes_races
    
    def get_races(self, realm: str) -> List[Dict]:
        """
        Récupère toutes les races disponibles pour un royaume
        
        Args:
            realm: Nom du royaume ("Albion", "Hibernia", "Midgard")
            
        Returns:
            Liste des races avec leurs noms traduits
        """
        data = self.load_classes_races()
        if realm not in data:
            return []
        return data[realm].get('races', [])
    
    def get_classes(self, realm: str) -> List[Dict]:
        """
        Récupère toutes les classes disponibles pour un royaume
        
        Args:
            realm: Nom du royaume ("Albion", "Hibernia", "Midgard")
            
        Returns:
            Liste des classes avec leurs informations complètes
        """
        data = self.load_classes_races()
        if realm not in data:
            return []
        return data[realm].get('classes', [])
    
    def get_class_info(self, realm: str, class_name: str) -> Optional[Dict]:
        """
        Récupère les informations détaillées d'une classe
        
        Args:
            realm: Nom du royaume
            class_name: Nom de la classe (ex: "Armsman", "Healer", "Druid")
            
        Returns:
            Dictionnaire avec les infos de la classe ou None
        """
        classes = self.get_classes(realm)
        for class_info in classes:
            if class_info['name'] == class_name:
                return class_info
        return None
    
    def get_available_classes_for_race(self, realm: str, race_name: str) -> List[Dict]:
        """
        Récupère toutes les classes jouables pour une race donnée
        
        Args:
            realm: Nom du royaume
            race_name: Nom de la race (ex: "Briton", "Norseman", "Celt")
            
        Returns:
            Liste des classes disponibles pour cette race
        """
        classes = self.get_classes(realm)
        available = []
        
        for class_info in classes:
            if race_name in class_info.get('races', []):
                available.append(class_info)
        
        return available
    
    def get_races_for_class(self, realm: str, class_name: str) -> List[str]:
        """
        Récupère toutes les races pouvant jouer une classe donnée
        
        Args:
            realm: Nom du royaume
            class_name: Nom de la classe
            
        Returns:
            Liste des noms de races
        """
        class_info = self.get_class_info(realm, class_name)
        if class_info:
            return class_info.get('races', [])
        return []
    
    def get_available_races_for_class(self, realm: str, class_name: str) -> List[Dict]:
        """
        Récupère toutes les races (avec leurs infos complètes) pouvant jouer une classe donnée
        
        Args:
            realm: Nom du royaume
            class_name: Nom de la classe
            
        Returns:
            Liste des races disponibles pour cette classe (avec traductions)
        """
        race_names = self.get_races_for_class(realm, class_name)
        all_races = self.get_races(realm)
        
        available = []
        for race in all_races:
            if race['name'] in race_names:
                available.append(race)
        
        return available
    
    def get_specializations(self, realm: str, class_name: str, language: str = "en") -> List[Dict]:
        """
        Récupère toutes les spécialisations disponibles pour une classe
        
        Args:
            realm: Nom du royaume
            class_name: Nom de la classe
            language: Code de langue ("en", "fr", "de") - défaut "en"
            
        Returns:
            Liste des spécialisations avec traductions
            Format: [{"name": "EN", "name_fr": "FR", "name_de": "DE"}, ...]
        """
        class_info = self.get_class_info(realm, class_name)
        if class_info:
            return class_info.get('specializations', [])
        return []
    
    def get_specialization_names(self, realm: str, class_name: str, language: str = "en") -> List[str]:
        """
        Récupère les noms des spécialisations dans une langue spécifique
        
        Args:
            realm: Nom du royaume
            class_name: Nom de la classe
            language: Code de langue ("en", "fr", "de") - défaut "en"
            
        Returns:
            Liste des noms de spécialisations dans la langue demandée
        """
        specs = self.get_specializations(realm, class_name)
        
        # Déterminer the clé of langue
        lang_key = "name"
        if language == "fr":
            lang_key = "name_fr"
        elif language == "de":
            lang_key = "name_de"
        
        # if the specs sont déjà des dicts with traductions
        if specs and isinstance(specs[0], dict):
            return [spec.get(lang_key, spec.get("name", "")) for spec in specs]
        
        # Sinon retourner tel quel (anciennes Data)
        return specs
    
    def is_race_class_compatible(self, realm: str, race_name: str, class_name: str) -> bool:
        """
        Vérifie si une combinaison race/classe est valide
        
        Args:
            realm: Nom du royaume
            race_name: Nom de la race
            class_name: Nom de la classe
            
        Returns:
            True si la combinaison est valide, False sinon
        """
        races = self.get_races_for_class(realm, class_name)
        return race_name in races
    
    def get_all_realms(self) -> List[str]:
        """
        Récupère la liste de tous les royaumes disponibles
        
        Returns:
            Liste des noms de royaumes
        """
        data = self.load_classes_races()
        return list(data.keys())


# Exemple d'utilisation
if __name__ == "__main__":
    dm = DataManager()
    
    print("=" * 70)
    print("EXEMPLE D'UTILISATION DU DATA MANAGER")
    print("=" * 70)
    
    # ========================================================================
    # REALM RANKS
    # ========================================================================
    print("\n" + "=" * 70)
    print("REALM RANKS")
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
    
    # Test 3: Résumé of all the rangs
    print("\n3. Résumé des rangs Hibernia:")
    summary = dm.get_all_ranks_summary("Hibernia")
    for rank in summary[:5]:  # Afficher les 5 premiers
        print(f"   Rank {rank['rank']}: {rank['title']} "
              f"(+{rank['skill_bonus']} skills, {rank['min_realm_points']:,} RP)")
    
    # Test 4: Calculer the RP nécessaires
    print("\n4. RP nécessaires pour atteindre Rank 10 depuis 100,000 RP:")
    rp_needed = dm.calculate_rp_needed("Midgard", 100000, 10)
    print(f"   RP à gagner: {rp_needed:,}")
    
    # ========================================================================
    # RACES & CLASSES
    # ========================================================================
    print("\n" + "=" * 70)
    print("RACES & CLASSES")
    print("=" * 70)
    
    # Test 5: Lister les races d'un royaume
    print("\n5. Races disponibles en Albion:")
    albion_races = dm.get_races("Albion")
    for race in albion_races:
        print(f"   - {race['name']} (FR: {race['name_fr']}, DE: {race['name_de']})")
    
    # Test 6: Lister les classes d'un royaume
    print("\n6. Classes disponibles en Midgard:")
    midgard_classes = dm.get_classes("Midgard")
    for class_info in midgard_classes[:5]:  # Afficher the 5 premières
        print(f"   - {class_info['name']} (FR: {class_info['name_fr']})")
        print(f"     Races: {', '.join(class_info['races'][:3])}...")
    
    # Test 7: Obtenir les infos d'une classe
    print("\n7. Informations sur la classe Armsman (Albion):")
    armsman = dm.get_class_info("Albion", "Armsman")
    if armsman:
        print(f"   Nom: {armsman['name']} (FR: {armsman['name_fr']})")
        print(f"   Races disponibles: {', '.join(armsman['races'])}")
        print(f"   Spécialisations: {', '.join(armsman['specializations'])}")
    
    # Test 8: Classes disponibles pour une race
    print("\n8. Classes jouables pour un Briton:")
    briton_classes = dm.get_available_classes_for_race("Albion", "Briton")
    print(f"   Nombre de classes: {len(briton_classes)}")
    print(f"   Exemples: {', '.join([c['name'] for c in briton_classes[:5]])}...")
    
    # Test 9: Check compatibilité race/classe
    print("\n9. Vérification de compatibilité race/classe:")
    print(f"   Briton + Armsman: {dm.is_race_class_compatible('Albion', 'Briton', 'Armsman')}")
    print(f"   Briton + Friar: {dm.is_race_class_compatible('Albion', 'Briton', 'Friar')}")
    print(f"   Avalonian + Friar: {dm.is_race_class_compatible('Albion', 'Avalonian', 'Friar')}")
    
    # Test 10: Spécialisations d'une classe
    print("\n10. Spécialisations du Healer (Midgard):")
    healer_specs = dm.get_specializations("Midgard", "Healer")
    for spec in healer_specs:
        print(f"   - {spec}")
    
    # Test 11: Races pour une classe
    print("\n11. Races pouvant jouer Druid (Hibernia):")
    druid_races = dm.get_races_for_class("Hibernia", "Druid")
    print(f"   Races: {', '.join(druid_races)}")
    
    print("\n" + "=" * 70)
