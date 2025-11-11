"""
Script pour convertir all_realm_logo.png en app_icon.ico
"""
from PIL import Image
import os

# Chemins
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
img_dir = os.path.join(project_dir, 'Img')

input_png = os.path.join(img_dir, 'all_realm_logo.png')
output_ico = os.path.join(img_dir, 'app_icon.ico')

print(f"Converting: {input_png}")
print(f"Output: {output_ico}")

# Ouvrir l'image PNG
img = Image.open(input_png)

# Convertir en RGBA si nécessaire
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Créer plusieurs tailles pour l'icône (standard Windows)
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
icon_images = []

for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    icon_images.append(resized)

# Sauvegarder en ICO
icon_images[0].save(
    output_ico, 
    format='ICO', 
    sizes=[(img.size[0], img.size[1]) for img in icon_images],
    append_images=icon_images[1:]
)

print(f"✅ Icon created successfully: {output_ico}")
print(f"Sizes included: {sizes}")
