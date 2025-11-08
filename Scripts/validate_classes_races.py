"""
Validation Script for classes_races.json
Vérifie l'intégrité et la cohérence des données de races/classes/spécialisations
"""
import json
import sys
from pathlib import Path

def validate_classes_races():
    """Valide le fichier classes_races.json"""
    
    print("=" * 70)
    print("VALIDATION DES DONNÉES : classes_races.json")
    print("=" * 70)
    
    # Charger le fichier
    data_file = Path("Data/classes_races.json")
    if not data_file.exists():
        print("❌ ERREUR : Fichier Data/classes_races.json introuvable")
        return False
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERREUR JSON : {e}")
        return False
    
    print("✅ Fichier JSON chargé avec succès\n")
    
    # Check the structure
    required_realms = ["Albion", "Midgard", "Hibernia"]
    errors = []
    warnings = []
    
    print("📋 VÉRIFICATION DE LA STRUCTURE")
    print("-" * 70)
    
    # Check the royaumes
    for realm in required_realms:
        if realm not in data:
            errors.append(f"Royaume manquant : {realm}")
            continue
        
        realm_data = data[realm]
        
        # Check races
        if 'races' not in realm_data:
            errors.append(f"{realm} : Clé 'races' manquante")
        else:
            races = realm_data['races']
            print(f"  {realm} : {len(races)} races")
            
            for i, race in enumerate(races):
                if 'name' not in race:
                    errors.append(f"{realm} race #{i+1} : 'name' manquant")
                if 'name_fr' not in race:
                    warnings.append(f"{realm} race {race.get('name', f'#{i+1}')} : 'name_fr' manquant")
                if 'name_de' not in race:
                    warnings.append(f"{realm} race {race.get('name', f'#{i+1}')} : 'name_de' manquant")
        
        # Check classes
        if 'classes' not in realm_data:
            errors.append(f"{realm} : Clé 'classes' manquante")
        else:
            classes = realm_data['classes']
            print(f"  {realm} : {len(classes)} classes")
            
            for i, class_info in enumerate(classes):
                class_name = class_info.get('name', f"#{i+1}")
                
                if 'name' not in class_info:
                    errors.append(f"{realm} classe #{i+1} : 'name' manquant")
                if 'name_fr' not in class_info:
                    warnings.append(f"{realm} {class_name} : 'name_fr' manquant")
                if 'name_de' not in class_info:
                    warnings.append(f"{realm} {class_name} : 'name_de' manquant")
                if 'races' not in class_info:
                    errors.append(f"{realm} {class_name} : 'races' manquant")
                elif not class_info['races']:
                    warnings.append(f"{realm} {class_name} : Aucune race assignée")
                if 'specializations' not in class_info:
                    errors.append(f"{realm} {class_name} : 'specializations' manquant")
                elif not class_info['specializations']:
                    warnings.append(f"{realm} {class_name} : Aucune spécialisation")
    
    print()
    
    # Check the cohérence des références
    print("🔗 VÉRIFICATION DES RÉFÉRENCES")
    print("-" * 70)
    
    for realm in required_realms:
        if realm not in data:
            continue
        
        realm_data = data[realm]
        available_races = {race['name'] for race in realm_data.get('races', [])}
        
        for class_info in realm_data.get('classes', []):
            class_name = class_info.get('name', 'Unknown')
            class_races = class_info.get('races', [])
            
            for race in class_races:
                if race not in available_races:
                    errors.append(f"{realm} {class_name} : Race inconnue '{race}'")
        
        print(f"  {realm} : Références validées ({len(available_races)} races)")
    
    print()
    
    # Statistiques
    print("📊 STATISTIQUES")
    print("-" * 70)
    
    total_races = sum(len(data[realm]['races']) for realm in required_realms if realm in data)
    total_classes = sum(len(data[realm]['classes']) for realm in required_realms if realm in data)
    total_specs = sum(
        len(class_info.get('specializations', []))
        for realm in required_realms if realm in data
        for class_info in data[realm].get('classes', [])
    )
    
    print(f"  Total races : {total_races}")
    print(f"  Total classes : {total_classes}")
    print(f"  Total spécialisations : {total_specs}")
    
    # Classes les plus polyvalentes (jouables par toutes les races)
    print("\n  Classes les plus polyvalentes :")
    for realm in required_realms:
        if realm not in data:
            continue
        realm_data = data[realm]
        max_races = len(realm_data['races'])
        
        for class_info in realm_data['classes']:
            if len(class_info.get('races', [])) == max_races:
                print(f"    - {realm} : {class_info['name']} (toutes les races)")
    
    # Classes the plus spécialisées (peu of races)
    print("\n  Classes les plus exclusives :")
    for realm in required_realms:
        if realm not in data:
            continue
        realm_data = data[realm]
        
        exclusive_classes = [
            (class_info['name'], len(class_info.get('races', [])))
            for class_info in realm_data['classes']
            if len(class_info.get('races', [])) <= 2
        ]
        
        for class_name, race_count in sorted(exclusive_classes, key=lambda x: x[1]):
            print(f"    - {realm} : {class_name} ({race_count} race{'s' if race_count > 1 else ''})")
    
    print()
    
    # Results
    print("=" * 70)
    print("RÉSULTATS")
    print("=" * 70)
    
    if errors:
        print(f"\n❌ {len(errors)} ERREUR(S) CRITIQUE(S) :")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} AVERTISSEMENT(S) :")
        for warning in warnings[:10]:  # Limiter à 10 warnings
            print(f"  - {warning}")
        if len(warnings) > 10:
            print(f"  ... et {len(warnings) - 10} autres")
    
    if not errors and not warnings:
        print("\n✅ VALIDATION RÉUSSIE : Aucune erreur ni avertissement")
        print("   Toutes les données sont valides et cohérentes !")
    elif not errors:
        print("\n✅ VALIDATION RÉUSSIE (avec avertissements)")
        print("   Les données sont valides mais quelques traductions manquent")
    else:
        print("\n❌ VALIDATION ÉCHOUÉE")
        print("   Veuillez corriger les erreurs avant de continuer")
    
    print("=" * 70)
    
    return len(errors) == 0


if __name__ == "__main__":
    success = validate_classes_races()
    sys.exit(0 if success else 1)