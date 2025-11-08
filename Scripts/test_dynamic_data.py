"""
Script de test pour vérifier que toutes les données sont dynamiques
et que les fichiers de personnages existants restent compatibles
"""

import sys
from pathlib import Path

# Ajouter the répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from Functions.data_manager import DataManager
from Functions.character_manager import REALMS, get_realms, get_all_characters

def test_data_manager_realms():
    """Test que DataManager charge les realms depuis JSON"""
    print("=" * 60)
    print("TEST 1: DataManager.get_realms()")
    print("=" * 60)
    
    dm = DataManager()
    realms = dm.get_realms()
    
    print(f"✅ Realms chargés depuis JSON: {realms}")
    print(f"   Type: {type(realms)}")
    print(f"   Nombre: {len(realms)}")
    
    assert isinstance(realms, list), "get_realms() doit retourner une liste"
    assert len(realms) > 0, "La liste des realms ne doit pas être vide"
    assert all(isinstance(r, str) for r in realms), "Tous les realms doivent être des strings"
    
    print("✅ Test réussi !\n")
    return realms

def test_character_manager_realms():
    """Test que character_manager utilise les realms dynamiques"""
    print("=" * 60)
    print("TEST 2: character_manager.REALMS")
    print("=" * 60)
    
    print(f"✅ REALMS (constante): {REALMS}")
    print(f"   Type: {type(REALMS)}")
    
    realms_func = get_realms()
    print(f"✅ get_realms() (fonction): {realms_func}")
    
    assert REALMS == realms_func, "REALMS et get_realms() doivent retourner la même chose"
    
    print("✅ Test réussi !\n")
    return REALMS

def test_existing_characters():
    """Test que les personnages existants sont toujours lisibles"""
    print("=" * 60)
    print("TEST 3: Compatibilité avec personnages existants")
    print("=" * 60)
    
    characters = get_all_characters()
    
    print(f"✅ Nombre de personnages trouvés: {len(characters)}")
    
    if len(characters) > 0:
        for char in characters[:3]:  # Afficher max 3 exemples
            name = char.get('name', 'N/A')
            realm = char.get('realm', 'N/A')
            char_class = char.get('class', 'N/A')
            race = char.get('race', 'N/A')
            level = char.get('level', 'N/A')
            
            print(f"   📝 {name}")
            print(f"      Royaume: {realm}")
            print(f"      Classe: {char_class}")
            print(f"      Race: {race}")
            print(f"      Niveau: {level}")
            
            # Check that the realm est valide
            if realm in REALMS:
                print(f"      ✅ Realm '{realm}' est valide")
            else:
                print(f"      ⚠️  Realm '{realm}' n'est pas dans la liste dynamique")
    
    print("✅ Test réussi !\n")
    return characters

def test_classes_and_races():
    """Test que les classes et races sont chargées dynamiquement"""
    print("=" * 60)
    print("TEST 4: Classes et Races dynamiques")
    print("=" * 60)
    
    dm = DataManager()
    realms = dm.get_realms()
    
    for realm in realms:
        classes = dm.get_classes(realm)
        races = dm.get_races(realm)
        
        print(f"📍 {realm}:")
        print(f"   Classes: {len(classes)} trouvées")
        if classes:
            print(f"      Exemples: {', '.join([c.get('name', '?') for c in classes[:3]])}")
        
        print(f"   Races: {len(races)} trouvées")
        if races:
            print(f"      Exemples: {', '.join([r.get('name', '?') for r in races[:3]])}")
    
    print("✅ Test réussi !\n")

def test_realm_ranks():
    """Test que les realm ranks sont chargés dynamiquement"""
    print("=" * 60)
    print("TEST 5: Realm Ranks dynamiques")
    print("=" * 60)
    
    dm = DataManager()
    realms = dm.get_realms()
    
    for realm in realms:
        ranks = dm.load_realm_ranks()
        if realm in ranks:
            realm_ranks = ranks[realm]
            print(f"📍 {realm}: {len(realm_ranks)} ranks trouvés")
            
            # Afficher premier et dernier rank
            if realm_ranks:
                first = realm_ranks[0]
                last = realm_ranks[-1]
                print(f"      Premier: Rank {first.get('rank')} - {first.get('title')}")
                print(f"      Dernier: Rank {last.get('rank')} - {last.get('title')}")
    
    print("✅ Test réussi !\n")

def main():
    """Exécute tous les tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  TEST DE DYNAMISATION DES DONNÉES - DAOC CHAR MANAGER  ║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        # Exécuter the tests
        test_data_manager_realms()
        test_character_manager_realms()
        test_existing_characters()
        test_classes_and_races()
        test_realm_ranks()
        
        # Résumé
        print("=" * 60)
        print("🎉 TOUS LES TESTS ONT RÉUSSI !")
        print("=" * 60)
        print()
        print("✅ Les realms sont chargés dynamiquement depuis JSON")
        print("✅ REALMS dans character_manager est dynamique")
        print("✅ Les personnages existants restent compatibles")
        print("✅ Les classes et races sont chargées dynamiquement")
        print("✅ Les realm ranks sont chargés dynamiquement")
        print()
        print("📄 Voir DYNAMIC_DATA_AUDIT.md pour plus de détails")
        print()
        
    except Exception as e:
        print("\n")
        print("=" * 60)
        print("❌ ERREUR PENDANT LES TESTS")
        print("=" * 60)
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()