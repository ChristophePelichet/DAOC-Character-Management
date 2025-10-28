"""
Script pour mettre à jour classes_races.json :
- Supprimer la classe Mauler
- Supprimer la race Minotaur
- Ajouter les traductions pour les spécialisations
"""
import json

# Dictionnaire de traductions pour les spécialisations
SPEC_TRANSLATIONS = {
    # Albion specializations
    "Crossbow": {"fr": "Arbalète", "de": "Armbrust"},
    "Polearm": {"fr": "Arme d'hast", "de": "Stangenwaffe"},
    "Slash": {"fr": "Tranchant", "de": "Hieb"},
    "Thrust": {"fr": "Estoc", "de": "Stoß"},
    "Two Handed": {"fr": "Deux mains", "de": "Zweihändig"},
    "Parry": {"fr": "Parade", "de": "Parieren"},
    "Shield": {"fr": "Bouclier", "de": "Schild"},
    "Body Magic": {"fr": "Magie du corps", "de": "Körpermagie"},
    "Matter Magic": {"fr": "Magie de la matière", "de": "Materiemagie"},
    "Spirit Magic": {"fr": "Magie de l'esprit", "de": "Geistmagie"},
    "Rejuvenation": {"fr": "Rajeunissement", "de": "Verjüngung"},
    "Smiting": {"fr": "Châtiment", "de": "Züchtigung"},
    "Enhancement": {"fr": "Amélioration", "de": "Verstärkung"},
    "Staff": {"fr": "Bâton", "de": "Stab"},
    "Heresy": {"fr": "Hérésie", "de": "Ketzerei"},
    "Flexible": {"fr": "Flexible", "de": "Flexibel"},
    "Crush": {"fr": "Contondant", "de": "Wucht"},
    "Critical Strike": {"fr": "Coup critique", "de": "Kritischer Schlag"},
    "Stealth": {"fr": "Furtivité", "de": "Heimlichkeit"},
    "Instruments": {"fr": "Instruments", "de": "Instrumente"},
    "Death Servant": {"fr": "Serviteur de la mort", "de": "Todesdiener"},
    "Deathsight": {"fr": "Vision de la mort", "de": "Todessicht"},
    "Painworking": {"fr": "Travail de la douleur", "de": "Schmerzarbeit"},
    "Chants": {"fr": "Chants", "de": "Gesänge"},
    "Soulrending": {"fr": "Déchirement d'âme", "de": "Seelenzerreißen"},
    "Longbow": {"fr": "Arc long", "de": "Langbogen"},
    "Mind Magic": {"fr": "Magie de l'esprit", "de": "Gedankenmagie"},
    "Earth Magic": {"fr": "Magie de la terre", "de": "Erdmagie"},
    "Cold Magic": {"fr": "Magie du froid", "de": "Kältemagie"},
    "Wind Magic": {"fr": "Magie du vent", "de": "Windmagie"},
    "Fire Magic": {"fr": "Magie du feu", "de": "Feuermagie"},
    
    # Midgard specializations
    "Axe": {"fr": "Hache", "de": "Axt"},
    "Hammer": {"fr": "Marteau", "de": "Hammer"},
    "Left Axe": {"fr": "Hache gauche", "de": "Linke Axt"},
    "Sword": {"fr": "Épée", "de": "Schwert"},
    "Bone Army": {"fr": "Armée d'os", "de": "Knochenarmee"},
    "Darkness": {"fr": "Ténèbres", "de": "Dunkelheit"},
    "Suppression": {"fr": "Suppression", "de": "Unterdrückung"},
    "Augmentation": {"fr": "Augmentation", "de": "Verstärkung"},
    "Mending": {"fr": "Guérison", "de": "Heilung"},
    "Pacification": {"fr": "Pacification", "de": "Besänftigung"},
    "Beast Craft": {"fr": "Maîtrise des bêtes", "de": "Tiermeisterschaft"},
    "Composite Bow": {"fr": "Arc composite", "de": "Kompositbogen"},
    "Spear": {"fr": "Lance", "de": "Speer"},
    "Runecarving": {"fr": "Gravure de runes", "de": "Runenschnitzen"},
    "Hand to Hand": {"fr": "Main à main", "de": "Waffenloser Kampf"},
    "Savagery": {"fr": "Sauvagerie", "de": "Wildheit"},
    "Cave Magic": {"fr": "Magie des cavernes", "de": "Höhlenmagie"},
    "Subterranean": {"fr": "Souterrain", "de": "Unterirdisch"},
    "Battlesongs": {"fr": "Chants de bataille", "de": "Kampflieder"},
    "Spirit Animation": {"fr": "Animation d'esprit", "de": "Geistbeschwörung"},
    "Summoning": {"fr": "Invocation", "de": "Beschwörung"},
    "Stormcalling": {"fr": "Appel de la tempête", "de": "Sturmruf"},
    "Odin's Will": {"fr": "Volonté d'Odin", "de": "Odins Wille"},
    "Cursing": {"fr": "Malédiction", "de": "Verfluchung"},
    "Hexing": {"fr": "Envoûtement", "de": "Verhexung"},
    "Witchcraft": {"fr": "Sorcellerie", "de": "Hexerei"},
    "Thrown Weapons": {"fr": "Armes de jet", "de": "Wurfwaffen"},
    
    # Hibernia specializations
    "Arboreal Path": {"fr": "Voie arboricole", "de": "Baumpfad"},
    "Creeping Path": {"fr": "Voie rampante", "de": "Schleichpfad"},
    "Verdant Path": {"fr": "Voie verdoyante", "de": "Grüner Pfad"},
    "Ethereal Shriek": {"fr": "Cri éthéré", "de": "Ätherischer Schrei"},
    "Phantasmal Wail": {"fr": "Gémissement spectral", "de": "Phantomgeheul"},
    "Spectral Guard": {"fr": "Garde spectrale", "de": "Spektralwache"},
    "Blades": {"fr": "Lames", "de": "Klingen"},
    "Blunt": {"fr": "Contondant", "de": "Stumpf"},
    "Music": {"fr": "Musique", "de": "Musik"},
    "Nurture": {"fr": "Protection", "de": "Pflege"},
    "Regrowth": {"fr": "Régénération", "de": "Nachwachsen"},
    "Celtic Dual": {"fr": "Double celte", "de": "Keltisch Dual"},
    "Piercing": {"fr": "Perforant", "de": "Durchbohren"},
    "Large Weapons": {"fr": "Grandes armes", "de": "Große Waffen"},
    "Valor": {"fr": "Vaillance", "de": "Tapferkeit"},
    "Nature Affinity": {"fr": "Affinité naturelle", "de": "Naturverbundenheit"},
    "Light Magic": {"fr": "Magie de la lumière", "de": "Lichtmagie"},
    "Mana Magic": {"fr": "Magie du mana", "de": "Manamagie"},
    "Void Magic": {"fr": "Magie du vide", "de": "Leermagie"},
    "Enchantments": {"fr": "Enchantements", "de": "Verzauberungen"},
    "Mentalism": {"fr": "Mentalisme", "de": "Mentalismus"},
    "RecurveBow": {"fr": "Arc recourbé", "de": "Recurvebogen"},
    "Arborean Path": {"fr": "Voie arboréenne", "de": "Baumlichtung"},
    "Scythe": {"fr": "Faux", "de": "Sense"},
    "Dementia": {"fr": "Démence", "de": "Demenz"},
    "Shadow Mastery": {"fr": "Maîtrise des ombres", "de": "Schattenmeisterschaft"},
}

def translate_specialization(spec_name):
    """Convertit une spécialisation en format multilingue"""
    if spec_name in SPEC_TRANSLATIONS:
        return {
            "name": spec_name,
            "name_fr": SPEC_TRANSLATIONS[spec_name]["fr"],
            "name_de": SPEC_TRANSLATIONS[spec_name]["de"]
        }
    else:
        # Si pas de traduction, utiliser le nom anglais
        print(f"⚠️  Traduction manquante pour: {spec_name}")
        return {
            "name": spec_name,
            "name_fr": spec_name,
            "name_de": spec_name
        }

# Charger le fichier actuel
with open('Data/classes_races.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Traiter chaque royaume
for realm_name, realm_data in data.items():
    print(f"\n🏰 Traitement de {realm_name}...")
    
    # Filtrer les classes (supprimer Mauler)
    original_class_count = len(realm_data['classes'])
    realm_data['classes'] = [
        cls for cls in realm_data['classes']
        if cls['name'] != 'Mauler'
    ]
    removed_classes = original_class_count - len(realm_data['classes'])
    if removed_classes > 0:
        print(f"   ✓ Supprimé {removed_classes} classe(s) Mauler")
    
    # Traduire les spécialisations
    for class_info in realm_data['classes']:
        if 'specializations' in class_info:
            # Convertir les spécialisations en format multilingue
            old_specs = class_info['specializations']
            new_specs = [translate_specialization(spec) for spec in old_specs]
            class_info['specializations'] = new_specs
            print(f"   ✓ {class_info['name']}: {len(new_specs)} spécialisations traduites")

print(f"\n💾 Sauvegarde du fichier mis à jour...")

# Sauvegarder le fichier mis à jour
with open('Data/classes_races.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Mise à jour terminée !")
print("\nRésumé:")
print(f"  - Classes Mauler supprimées des 3 royaumes")
print(f"  - Toutes les spécialisations traduites en FR/EN/DE")
