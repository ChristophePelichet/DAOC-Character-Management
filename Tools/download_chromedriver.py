"""
Script pour télécharger ChromeDriver manuellement
Utile si webdriver-manager ne peut pas accéder à googlechromelabs.github.io
"""

import os
import sys
import requests
import zipfile
import subprocess
from pathlib import Path

def get_chrome_version():
    """Récupère la version de Chrome installée"""
    try:
        # Windows
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
        if os.path.exists(chrome_path):
            result = subprocess.run(
                [chrome_path, "--version"],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip().split()[-1]
            major_version = version.split('.')[0]
            return major_version
        else:
            print("❌ Chrome non trouvé dans les emplacements standards")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la version Chrome: {e}")
        return None

def download_chromedriver(chrome_version=None):
    """Télécharge ChromeDriver compatible avec la version de Chrome"""
    try:
        if chrome_version is None:
            chrome_version = get_chrome_version()
            if chrome_version is None:
                print("\n⚠️  Impossible de détecter la version de Chrome")
                chrome_version = input("Entrez la version majeure de Chrome (ex: 119): ").strip()
        
        print(f"\n📥 Téléchargement de ChromeDriver pour Chrome {chrome_version}...")
        
        # URL de l'API pour trouver la bonne version
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        
        print(f"🔍 Recherche de la version compatible...")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Trouver la version stable
        channels = data.get('channels', {})
        stable = channels.get('Stable', {})
        version = stable.get('version', '')
        
        if not version:
            raise Exception("Version stable non trouvée dans l'API")
        
        print(f"✓ Version trouvée: {version}")
        
        # Trouver le lien de téléchargement pour Windows
        downloads = stable.get('downloads', {}).get('chromedriver', [])
        win64_url = None
        
        for download in downloads:
            if download.get('platform') == 'win64':
                win64_url = download.get('url')
                break
        
        if not win64_url:
            raise Exception("URL de téléchargement Windows non trouvée")
        
        print(f"📥 Téléchargement depuis: {win64_url}")
        
        # Télécharger le fichier
        zip_path = Path("chromedriver-win64.zip")
        response = requests.get(win64_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rTéléchargement: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✓ Téléchargement terminé: {zip_path}")
        
        # Extraire le fichier
        print("📦 Extraction...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Déplacer chromedriver.exe à la racine
        extracted_path = Path("chromedriver-win64/chromedriver.exe")
        target_path = Path("../chromedriver.exe")  # Dossier parent (racine du projet)
        
        if extracted_path.exists():
            if target_path.exists():
                print(f"⚠️  {target_path} existe déjà")
                overwrite = input("Écraser? (o/n): ").strip().lower()
                if overwrite != 'o':
                    print("❌ Opération annulée")
                    return False
            
            # Copier le fichier
            import shutil
            shutil.copy2(extracted_path, target_path)
            print(f"✓ ChromeDriver copié vers: {target_path.absolute()}")
            
            # Nettoyer
            shutil.rmtree("chromedriver-win64", ignore_errors=True)
            zip_path.unlink(missing_ok=True)
            print("✓ Fichiers temporaires nettoyés")
            
            print("\n✅ ChromeDriver installé avec succès!")
            print(f"📍 Emplacement: {target_path.absolute()}")
            print("\n💡 Vous pouvez maintenant utiliser la génération de cookies")
            return True
        else:
            print(f"❌ Fichier extrait non trouvé: {extracted_path}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erreur réseau: {e}")
        print("\n💡 Solutions:")
        print("  1. Vérifiez votre connexion Internet")
        print("  2. Vérifiez les paramètres firewall/proxy")
        print("  3. Téléchargez manuellement depuis:")
        print("     https://googlechromelabs.github.io/chrome-for-testing/")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   Téléchargement de ChromeDriver")
    print("=" * 60)
    
    success = download_chromedriver()
    
    if success:
        print("\n" + "=" * 60)
        print("   Installation terminée avec succès!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("   Échec de l'installation")
        print("=" * 60)
        sys.exit(1)
