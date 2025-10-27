"""Créer des icônes PNG valides pour tester"""
from PIL import Image, ImageDraw, ImageFont
import os

img_dir = r"d:\Projets\Python\DAOC---Gestion-des-personnages\Img"

# Créer des icônes 32x32 avec des couleurs différentes
icons = {
    "albion_logo.png": ("red", "A"),
    "hibernia_logo.png": ("green", "H"),
    "midgard_logo.png": ("blue", "M")
}

print("Création des icônes de royaume...\n")

for filename, (color, letter) in icons.items():
    # Créer une image 32x32
    img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle de couleur
    if color == "red":
        fill_color = (200, 50, 50, 255)
    elif color == "green":
        fill_color = (50, 200, 50, 255)
    else:  # blue
        fill_color = (50, 50, 200, 255)
    
    draw.ellipse([2, 2, 30, 30], fill=fill_color, outline=(0, 0, 0, 255), width=2)
    
    # Ajouter la lettre au centre
    try:
        # Essayer d'utiliser une police
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        # Utiliser la police par défaut
        font = ImageFont.load_default()
    
    # Centrer le texte
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (32 - text_width) // 2
    y = (32 - text_height) // 2 - 2
    
    draw.text((x, y), letter, fill=(255, 255, 255, 255), font=font)
    
    # Sauvegarder
    filepath = os.path.join(img_dir, filename)
    img.save(filepath, "PNG")
    
    # Vérifier
    size = os.path.getsize(filepath)
    print(f"✓ {filename}: {size} octets")

print("\n✅ Icônes créées avec succès!")
print("\nRelancez l'application pour voir les icônes.")
