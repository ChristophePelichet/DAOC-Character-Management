"""
Script pour créer des bannières placeholder pour toutes les classes DAOC
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Structure des classes par royaume
CLASSES = {
    "Alb": [
        "Armsman", "Cabalist", "Cleric", "Friar", "Heretic", "Infiltrator",
        "Mercenary", "Minstrel", "Necromancer", "Paladin", "Reaver",
        "Scout", "Sorcerer", "Theurgist", "Wizard"
    ],
    "Hib": [
        "Animist", "Bainshee", "Bard", "Blademaster", "Champion", "Druid",
        "Eldritch", "Enchanter", "Hero", "Mentalist", "Nightshade",
        "Ranger", "Valewalker", "Vampiir", "Warden"
    ],
    "Mid": [
        "Berserker", "Bonedancer", "Healer", "Hunter", "Runemaster",
        "Savage", "Shadowblade", "Shaman", "Skald", "Spiritmaster",
        "Thane", "Valkyrie", "Warlock", "Warrior"
    ]
}

# Couleurs par royaume
REALM_COLORS = {
    "Alb": (204, 0, 0),      # Rouge
    "Hib": (0, 170, 0),      # Vert
    "Mid": (0, 102, 204)     # Bleu
}

def create_placeholder_banner(realm, class_name, output_path):
    """Crée une bannière placeholder pour une classe"""
    
    # Dimensions
    width = 150
    height = 400
    
    # Couleur du royaume
    bg_color = REALM_COLORS.get(realm, (128, 128, 128))
    
    # Créer l'image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Essayer de charger une font, sinon utiliser la font par défaut
    try:
        # Essayer plusieurs tailles de police
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_class = ImageFont.truetype("arialbd.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_class = ImageFont.load_default()
    
    # Dessiner le fond dégradé (plus sombre en bas)
    for y in range(height):
        darkness = int(100 * (y / height))
        dark_color = tuple(max(0, c - darkness) for c in bg_color)
        draw.line([(0, y), (width, y)], fill=dark_color)
    
    # Texte du royaume en haut
    realm_text = realm.upper()
    try:
        bbox = draw.textbbox((0, 0), realm_text, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width = len(realm_text) * 10
        text_height = 20
    
    x = (width - text_width) // 2
    y = 20
    
    # Ombre du texte
    draw.text((x+2, y+2), realm_text, fill=(0, 0, 0), font=font_title)
    draw.text((x, y), realm_text, fill=(255, 255, 255), font=font_title)
    
    # Nom de la classe au centre
    try:
        bbox = draw.textbbox((0, 0), class_name, font=font_class)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width = len(class_name) * 8
        text_height = 16
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Ombre du texte
    draw.text((x+2, y+2), class_name, fill=(0, 0, 0), font=font_class)
    draw.text((x, y), class_name, fill=(255, 255, 255), font=font_class)
    
    # Bordure dorée
    border_color = (255, 215, 0)
    for i in range(3):
        draw.rectangle([i, i, width-1-i, height-1-i], outline=border_color, width=1)
    
    # Sauvegarder
    img.save(output_path, 'JPEG', quality=95)
    print(f"✅ Created: {output_path}")

def main():
    """Génère toutes les bannières manquantes"""
    
    base_path = os.path.join("Img", "Banner")
    
    # Vérifier que le dossier Banner existe
    if not os.path.exists(base_path):
        print(f"❌ Folder not found: {base_path}")
        return
    
    created_count = 0
    skipped_count = 0
    
    for realm, classes in CLASSES.items():
        realm_path = os.path.join(base_path, realm)
        
        # Créer le dossier du royaume s'il n'existe pas
        os.makedirs(realm_path, exist_ok=True)
        
        for class_name in classes:
            # Nom du fichier en minuscules
            filename = class_name.lower() + ".jpg"
            filepath = os.path.join(realm_path, filename)
            
            # Vérifier si le fichier existe déjà
            if os.path.exists(filepath):
                print(f"⏭️  Skipped (already exists): {filepath}")
                skipped_count += 1
                continue
            
            # Vérifier aussi .png
            png_filepath = os.path.join(realm_path, class_name.lower() + ".png")
            if os.path.exists(png_filepath):
                print(f"⏭️  Skipped (PNG exists): {png_filepath}")
                skipped_count += 1
                continue
            
            # Créer la bannière
            create_placeholder_banner(realm, class_name, filepath)
            created_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   📁 Total: {created_count + skipped_count}")

if __name__ == "__main__":
    print("🎨 DAOC Class Banner Generator")
    print("=" * 50)
    main()
    print("=" * 50)
    print("✨ Done!")
