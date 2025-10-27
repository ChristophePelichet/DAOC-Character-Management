"""Créer des icônes PNG minimales valides (16x16)"""
import struct
import zlib
import os

def create_simple_png(filename, color_rgb):
    """Crée un PNG 16x16 uni-couleur"""
    width, height = 16, 16
    
    # Données de l'image (RGB, pas de transparence)
    img_data = b""
    for y in range(height):
        img_data += b'\x00'  # Pas de filtre pour cette ligne
        for x in range(width):
            img_data += bytes(color_rgb)  # RGB
    
    # Compression des données
    compressed = zlib.compress(img_data)
    
    # En-tête PNG
    png = b'\x89PNG\r\n\x1a\n'
    
    # Chunk IHDR (dimensions et format)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    png += struct.pack('>I', len(ihdr_data))
    png += b'IHDR' + ihdr_data
    png += struct.pack('>I', ihdr_crc)
    
    # Chunk IDAT (données compressées)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    png += struct.pack('>I', len(compressed))
    png += b'IDAT' + compressed
    png += struct.pack('>I', idat_crc)
    
    # Chunk IEND (fin)
    png += struct.pack('>I', 0)
    png += b'IEND'
    png += struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
    
    # Écrire le fichier
    with open(filename, 'wb') as f:
        f.write(png)

# Répertoire des images
img_dir = r"d:\Projets\Python\DAOC---Gestion-des-personnages\Img"

# Créer les icônes avec des couleurs différentes
icons = {
    "albion_logo.png": (200, 50, 50),    # Rouge (Albion)
    "hibernia_logo.png": (50, 200, 50),  # Vert (Hibernia)
    "midgard_logo.png": (50, 50, 200),   # Bleu (Midgard)
}

print("Création des icônes de royaume 16x16...\n")

for filename, color in icons.items():
    filepath = os.path.join(img_dir, filename)
    create_simple_png(filepath, color)
    size = os.path.getsize(filepath)
    
    # Vérifier que c'est un PNG valide
    with open(filepath, 'rb') as f:
        header = f.read(8)
        is_valid = header == b'\x89PNG\r\n\x1a\n'
    
    if is_valid:
        print(f"✓ {filename}: {size} octets (PNG valide)")
    else:
        print(f"✗ {filename}: ERREUR")

print("\n✅ Icônes créées avec succès!")
print("\nCouleurs:")
print("  • Albion (rouge)")
print("  • Hibernia (vert)")
print("  • Midgard (bleu)")
print("\nRelancez l'application pour voir les icônes.")
