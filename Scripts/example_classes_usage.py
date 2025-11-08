"""
Exemple d'utilisation pratique du système de races/classes
Démontre comment intégrer les données dans une interface utilisateur
"""

from Functions.data_manager import DataManager

# Initialiser le DataManager
dm = DataManager()

print("=" * 80)
print("EXEMPLE PRATIQUE : Création de personnage avec validation")
print("=" * 80)

# Simulation d'une Creation of personnage
def create_character_workflow():
    """Simule le workflow de création d'un personnage"""
    
    # Step 1 : Sélection of the royaume
    print("\n🏰 ÉTAPE 1 : Sélection du royaume")
    print("-" * 80)
    realms = dm.get_all_realms()
    print(f"Royaumes disponibles : {', '.join(realms)}")
    
    selected_realm = "Albion"  # L'utilisateur sélectionne Albion
    print(f"✓ Royaume sélectionné : {selected_realm}")
    
    # Step 2 : Sélection of the race
    print("\n👤 ÉTAPE 2 : Sélection de la race")
    print("-" * 80)
    races = dm.get_races(selected_realm)
    print(f"Races disponibles en {selected_realm} :")
    for i, race in enumerate(races, 1):
        print(f"  {i}. {race['name']} (FR: {race['name_fr']}, DE: {race['name_de']})")
    
    selected_race = "Briton"  # L'utilisateur sélectionne Briton
    print(f"✓ Race sélectionnée : {selected_race}")
    
    # Step 3 : Filtrer the classes disponibles for this race
    print("\n⚔️  ÉTAPE 3 : Sélection de la classe")
    print("-" * 80)
    available_classes = dm.get_available_classes_for_race(selected_realm, selected_race)
    print(f"Classes disponibles pour un {selected_race} :")
    for i, cls in enumerate(available_classes[:10], 1):  # Afficher the 10 premières
        print(f"  {i}. {cls['name']} (FR: {cls['name_fr']}, DE: {cls['name_de']})")
    if len(available_classes) > 10:
        print(f"  ... et {len(available_classes) - 10} autres")
    
    selected_class = "Armsman"  # L'utilisateur sélectionne Armsman
    print(f"✓ Classe sélectionnée : {selected_class}")
    
    # Step 4 : Validation of the combinaison
    print("\n✅ ÉTAPE 4 : Validation")
    print("-" * 80)
    is_valid = dm.is_race_class_compatible(selected_realm, selected_race, selected_class)
    if is_valid:
        print(f"✓ Combinaison valide : {selected_race} {selected_class}")
    else:
        print(f"✗ ERREUR : {selected_race} ne peut pas être {selected_class}")
        return False
    
    # Step 5 : Afficher the spécialisations disponibles
    print("\n📚 ÉTAPE 5 : Spécialisations disponibles")
    print("-" * 80)
    class_info = dm.get_class_info(selected_realm, selected_class)
    specs = class_info['specializations']
    print(f"Spécialisations du {selected_class} :")
    for spec in specs:
        print(f"  • {spec}")
    
    # Step 6 : Résumé of the personnage
    print("\n📋 RÉSUMÉ DU PERSONNAGE")
    print("=" * 80)
    print(f"Royaume    : {selected_realm}")
    print(f"Race       : {selected_race} (FR: {[r for r in races if r['name'] == selected_race][0]['name_fr']})")
    print(f"Classe     : {selected_class} (FR: {class_info['name_fr']})")
    print(f"Spécs      : {len(specs)} spécialisations disponibles")
    print("=" * 80)
    
    return True

# Exécuter l'exemple
success = create_character_workflow()

# Exemples supplémentaires
if success:
    print("\n" + "=" * 80)
    print("EXEMPLES SUPPLÉMENTAIRES")
    print("=" * 80)
    
    # Exemple 1 : Check une combinaison invalide
    print("\n🚫 Exemple 1 : Tentative de combinaison invalide")
    print("-" * 80)
    result = dm.is_race_class_compatible("Albion", "Avalonian", "Friar")
    print(f"Avalonian + Friar = {result}")
    if not result:
        print("→ Le Friar est exclusif aux Britons")
        races_for_friar = dm.get_races_for_class("Albion", "Friar")
        print(f"   Races autorisées : {', '.join(races_for_friar)}")
    
    # Exemple 2 : Comparer the spécialisations entre classes
    print("\n🔍 Exemple 2 : Comparaison de classes")
    print("-" * 80)
    healer_specs = dm.get_specializations("Midgard", "Healer")
    shaman_specs = dm.get_specializations("Midgard", "Shaman")
    print(f"Healer : {len(healer_specs)} spécialisations - {', '.join(healer_specs)}")
    print(f"Shaman : {len(shaman_specs)} spécialisations - {', '.join(shaman_specs)}")
    
    # Exemple 3 : Find the classes communes à deux races
    print("\n🤝 Exemple 3 : Classes communes entre deux races")
    print("-" * 80)
    briton_classes = set(c['name'] for c in dm.get_available_classes_for_race("Albion", "Briton"))
    saracen_classes = set(c['name'] for c in dm.get_available_classes_for_race("Albion", "Saracen"))
    common = briton_classes & saracen_classes
    print(f"Classes communes Briton/Saracen : {len(common)}")
    print(f"Exemples : {', '.join(list(common)[:5])}...")
    
    # Exemple 4 : Classe la plus polyvalente
    print("\n🌟 Exemple 4 : Classe la plus polyvalente de chaque royaume")
    print("-" * 80)
    for realm in dm.get_all_realms():
        all_classes = dm.get_classes(realm)
        max_races = 0
        most_versatile = None
        
        for cls in all_classes:
            race_count = len(cls['races'])
            if race_count > max_races:
                max_races = race_count
                most_versatile = cls['name']
        
        print(f"{realm:10} : {most_versatile} ({max_races} races)")

print("\n" + "=" * 80)
print("✅ Exemple terminé avec succès !")
print("=" * 80)