import os

img_dir = r"d:\Projets\Python\DAOC---Gestion-des-personnages\Img"
files = ['reglage.png']

print("Vérification des fichiers PNG:\n")

png_signature = b'\x89PNG\r\n\x1a\n'

for filename in files:
    filepath = os.path.join(img_dir, filename)
    with open(filepath, 'rb') as f:
        header = f.read(8)
        size = os.path.getsize(filepath)
        is_png = header == png_signature
        
        print(f"{filename}:")
        print(f"  Taille: {size} octets")
        print(f"  Signature: {header.hex()}")
        print(f"  Est un PNG valide: {is_png}")
        
        if not is_png:
            print(f"  ❌ FICHIER INVALIDE!")
            # Lire tout le contenu pour voir ce que c'est
            f.seek(0)
            content = f.read()
            print(f"  Contenu: {content[:100]}")
        else:
            print(f"  ✓ Fichier PNG valide")
        print()
