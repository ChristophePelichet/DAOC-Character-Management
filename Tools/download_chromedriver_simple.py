"""
Script simple pour télécharger ChromeDriver (sans dépendances externes)
"""

import os
import urllib.request
import zipfile
import subprocess
from pathlib import Path

def get_chrome_version():
    """Récupère la version de Chrome installée"""
    try:
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
            print(f"✓ Version Chrome détectée: {version}")
            return version
        else:
            print("❌ Chrome non trouvé")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def download_chromedriver():
    """Télécharge ChromeDriver"""
    try:
        print("\n" + "=" * 60)
        print("   Téléchargement de ChromeDriver")
        print("=" * 60 + "\n")
        
        chrome_version = get_chrome_version()
        
        if not chrome_version:
            print("\n⚠️  Impossible de détecter Chrome")
            print("Téléchargement de la dernière version stable...")
        
        # URL de téléchargement direct (dernière version stable)
        print("\n📥 Récupération des informations...")
        
        # On va chercher la dernière version stable
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        
        try:
            with urllib.request.urlopen(api_url, timeout=10) as response:
                import json
                data = json.loads(response.read().decode())
                
                stable = data['channels']['Stable']
                version = stable['version']
                
                # Trouver l'URL Windows 64
                downloads = stable['downloads']['chromedriver']
                win64_url = None
                
                for download in downloads:
                    if download['platform'] == 'win64':
                        win64_url = download['url']
                        break
                
                if not win64_url:
                    raise Exception("URL Windows non trouvée")
                
                print(f"✓ Version stable: {version}")
                print(f"📥 URL: {win64_url}\n")
                
        except Exception as e:
            print(f"⚠️  Impossible d'accéder à l'API: {e}")
            print("❌ ÉCHEC: Impossible de télécharger automatiquement\n")
            print("=" * 60)
            print("SOLUTION MANUELLE:")
            print("=" * 60)
            print("1. Allez sur: https://googlechromelabs.github.io/chrome-for-testing/")
            print("2. Téléchargez 'chromedriver' pour 'win64' (Stable)")
            print("3. Extrayez le ZIP")
            print("4. Copiez 'chromedriver.exe' à la racine du projet")
            print(f"   (ici: {Path.cwd()})")
            print("=" * 60)
            return False
        
        # Télécharger
        zip_path = Path("chromedriver-win64.zip")
        print(f"⏬ Téléchargement en cours...")
        
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                print(f"\r  Progression: {percent:.1f}% ({downloaded // 1024} Ko / {total_size // 1024} Ko)", end='', flush=True)
        
        urllib.request.urlretrieve(win64_url, zip_path, report_progress)
        print(f"\n✓ Téléchargement terminé: {zip_path}\n")
        
        # Extraire
        print("📦 Extraction...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("✓ Extraction terminée")
        
        # Déplacer
        extracted_path = Path("chromedriver-win64/chromedriver.exe")
        target_path = Path("chromedriver.exe")
        
        if extracted_path.exists():
            if target_path.exists():
                print(f"\n⚠️  {target_path} existe déjà")
                response = input("Écraser? (o/n): ").strip().lower()
                if response != 'o':
                    print("❌ Annulé")
                    return False
                target_path.unlink()
            
            import shutil
            shutil.copy2(extracted_path, target_path)
            print(f"✓ Copié vers: {target_path.absolute()}")
            
            # Nettoyer
            shutil.rmtree("chromedriver-win64", ignore_errors=True)
            zip_path.unlink(missing_ok=True)
            print("✓ Nettoyage terminé")
            
            print("\n" + "=" * 60)
            print("   ✅ Installation réussie!")
            print("=" * 60)
            print(f"📍 ChromeDriver installé: {target_path.absolute()}")
            print("\n💡 Vous pouvez maintenant utiliser la génération de cookies")
            print("=" * 60)
            return True
        else:
            print(f"❌ Fichier non trouvé: {extracted_path}")
            return False
            
    except urllib.error.URLError as e:
        print(f"\n❌ Erreur réseau: {e}")
        print("\n" + "=" * 60)
        print("SOLUTIONS POSSIBLES:")
        print("=" * 60)
        print("1. Vérifiez votre connexion Internet")
        print("2. Vérifiez firewall/proxy")
        print("3. Téléchargement manuel:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        print("   → Téléchargez 'chromedriver' win64")
        print("   → Extrayez et copiez chromedriver.exe ici")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = download_chromedriver()
        if not success:
            input("\n⏸️  Appuyez sur Entrée pour fermer...")
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
        input("⏸️  Appuyez sur Entrée pour fermer...")
