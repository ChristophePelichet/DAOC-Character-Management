"""
Script pour ajouter les traductions FR et DE au fichier armor_resists.json
"""

import json
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Dictionnaires de traduction
ARMOR_TYPES_TRANSLATIONS = {
    "Plate": {"fr": "Plaques", "de": "Platte"},
    "Chain": {"fr": "Mailles", "de": "Kette"},
    "Studded": {"fr": "Cloutée", "de": "Beschlagen"},
    "Leather": {"fr": "Cuir", "de": "Leder"},
    "Cloth": {"fr": "Tissu", "de": "Stoff"},
    "Scale": {"fr": "Écailles", "de": "Schuppen"},
    "Reinforced": {"fr": "Renforcée", "de": "Verstärkt"},
}

RESIST_TRANSLATIONS = {
    "Resistant": {"fr": "Résistant", "de": "Resistent"},
    "Vulnerable": {"fr": "Vulnérable", "de": "Verletzlich"},
    "Neutral": {"fr": "Neutre", "de": "Neutral"},
}

RESIST_TYPES_TRANSLATIONS = {
    "Armor Type": {"fr": "Type d'armure", "de": "Rüstungstyp"},
    "Thrust": {"fr": "Perforation", "de": "Stoß"},
    "Crush": {"fr": "Contondant", "de": "Wucht"},
    "Slash": {"fr": "Tranchant", "de": "Hieb"},
    "Cold": {"fr": "Froid", "de": "Kälte"},
    "Energy": {"fr": "Énergie", "de": "Energie"},
    "Heat": {"fr": "Chaleur", "de": "Hitze"},
    "Matter": {"fr": "Matière", "de": "Materie"},
    "Spirit": {"fr": "Esprit", "de": "Geist"},
    "Body": {"fr": "Corps", "de": "Körper"},
}

# Chargement des traductions de classes depuis classes_races.json
def load_class_translations():
    """Charge les traductions de classes depuis classes_races.json"""
    classes_file = Path("Data/classes_races.json")
    translations = {}
    
    if classes_file.exists():
        with open(classes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for realm, realm_data in data.items():
            if isinstance(realm_data, dict) and 'classes' in realm_data:
                for class_info in realm_data['classes']:
                    if isinstance(class_info, dict):
                        name = class_info.get('name')
                        if name:
                            translations[name] = {
                                'fr': class_info.get('name_fr', name),
                                'de': class_info.get('name_de', name)
                            }
    
    return translations


def add_translations_to_armor_resists():
    """Ajoute les traductions FR et DE au fichier armor_resists.json"""
    
    armor_file = Path("Data/armor_resists.json")
    
    if not armor_file.exists():
        print(f"❌ Fichier {armor_file} introuvable")
        return
    
    # Charger le fichier
    with open(armor_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("📚 Chargement des traductions de classes...")
    class_translations = load_class_translations()
    print(f"   {len(class_translations)} classes trouvées\n")
    
    print("🔄 Ajout des traductions...")
    
    # Ajouter les traductions aux resist_types
    if 'resist_types' in data:
        new_resist_types = []
        for resist_type in data['resist_types']:
            if resist_type in RESIST_TYPES_TRANSLATIONS:
                new_resist_types.append({
                    'name': resist_type,
                    'name_fr': RESIST_TYPES_TRANSLATIONS[resist_type]['fr'],
                    'name_de': RESIST_TYPES_TRANSLATIONS[resist_type]['de']
                })
            else:
                new_resist_types.append({'name': resist_type, 'name_fr': resist_type, 'name_de': resist_type})
        data['resist_types'] = new_resist_types
    
    # Traiter chaque table
    if 'tables' in data:
        for table_key, table_data in data['tables'].items():
            print(f"   Table: {table_key}")
            
            # Mettre à jour les headers avec traductions
            if 'headers' in table_data:
                new_headers = []
                for header in table_data['headers']:
                    if header in RESIST_TYPES_TRANSLATIONS:
                        new_headers.append({
                            'name': header,
                            'name_fr': RESIST_TYPES_TRANSLATIONS[header]['fr'],
                            'name_de': RESIST_TYPES_TRANSLATIONS[header]['de']
                        })
                    elif header == "Class":
                        new_headers.append({
                            'name': 'Class',
                            'name_fr': 'Classe',
                            'name_de': 'Klasse'
                        })
                    else:
                        new_headers.append({'name': header, 'name_fr': header, 'name_de': header})
                table_data['headers'] = new_headers
            
            # Mettre à jour chaque ligne de données
            if 'data' in table_data:
                for row in table_data['data']:
                    # Classe
                    if 'Class' in row:
                        class_name = row['Class']
                        if class_name in class_translations:
                            row['Class_fr'] = class_translations[class_name]['fr']
                            row['Class_de'] = class_translations[class_name]['de']
                        else:
                            row['Class_fr'] = class_name
                            row['Class_de'] = class_name
                    
                    # Type d'armure
                    if 'Armor Type' in row:
                        armor_type = row['Armor Type']
                        if armor_type in ARMOR_TYPES_TRANSLATIONS:
                            row['Armor Type_fr'] = ARMOR_TYPES_TRANSLATIONS[armor_type]['fr']
                            row['Armor Type_de'] = ARMOR_TYPES_TRANSLATIONS[armor_type]['de']
                        else:
                            row['Armor Type_fr'] = armor_type
                            row['Armor Type_de'] = armor_type
                    
                    # Résistances
                    for resist_key in ['Thrust', 'Crush', 'Slash', 'Cold', 'Energy', 'Heat', 'Matter', 'Spirit', 'Body']:
                        if resist_key in row:
                            resist_value = row[resist_key]
                            if resist_value in RESIST_TRANSLATIONS:
                                row[f'{resist_key}_fr'] = RESIST_TRANSLATIONS[resist_value]['fr']
                                row[f'{resist_key}_de'] = RESIST_TRANSLATIONS[resist_value]['de']
                            else:
                                row[f'{resist_key}_fr'] = resist_value
                                row[f'{resist_key}_de'] = resist_value
                
                print(f"      {len(table_data['data'])} lignes traitées")
    
    # Sauvegarder le fichier
    print("\n💾 Sauvegarde du fichier...")
    with open(armor_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fichier {armor_file} mis à jour avec succès!")
    print("\n📊 Résumé:")
    print(f"   - Resist types: {len(data.get('resist_types', []))} entrées")
    print(f"   - Tables: {len(data.get('tables', {}))} tables")
    for table_key, table_data in data.get('tables', {}).items():
        print(f"      - {table_key}: {len(table_data.get('data', []))} classes")


if __name__ == "__main__":
    try:
        add_translations_to_armor_resists()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
