"""
Test rapide de ChromeDriver
"""

import sys
import os

# Ajouter le chemin Functions au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_chromedriver():
    """Teste si ChromeDriver fonctionne avec les 3 méthodes"""
    
    print("=" * 60)
    print("   Test de ChromeDriver")
    print("=" * 60 + "\n")
    
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Mode invisible
    
    driver = None
    method_used = None
    
    # Méthode 1: webdriver-manager
    print("🔍 Méthode 1: webdriver-manager...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        method_used = "webdriver-manager"
        print("✅ Méthode 1 réussie\n")
    except Exception as e:
        print(f"❌ Méthode 1 échouée: {e}\n")
        
        # Méthode 2: PATH système
        print("🔍 Méthode 2: ChromeDriver système...")
        try:
            driver = webdriver.Chrome(options=chrome_options)
            method_used = "système (PATH)"
            print("✅ Méthode 2 réussie\n")
        except Exception as e:
            print(f"❌ Méthode 2 échouée: {e}\n")
            
            # Méthode 3: Fichier local
            print("🔍 Méthode 3: ChromeDriver local...")
            try:
                local_path = os.path.join(os.path.dirname(__file__), '..', 'chromedriver.exe')
                driver = webdriver.Chrome(service=Service(local_path), options=chrome_options)
                method_used = "local (chromedriver.exe)"
                print("✅ Méthode 3 réussie\n")
            except Exception as e:
                print(f"❌ Méthode 3 échouée: {e}\n")
    
    if driver:
        print("=" * 60)
        print(f"✅ SUCCESS - ChromeDriver fonctionne via: {method_used}")
        print("=" * 60)
        
        # Tester une navigation rapide
        try:
            driver.get("https://www.google.com")
            print(f"✅ Navigation réussie")
            print(f"   Titre de la page: {driver.title}")
        except Exception as e:
            print(f"⚠️  Navigation échouée: {e}")
        finally:
            driver.quit()
            print("✅ Driver fermé proprement")
        
        return True
    else:
        print("=" * 60)
        print("❌ ÉCHEC - Aucune méthode n'a fonctionné")
        print("=" * 60)
        print("\nSOLUTIONS:")
        print("1. Exécutez: python .\\Tools\\download_chromedriver_simple.py")
        print("2. Ou téléchargez manuellement ChromeDriver")
        print("3. Vérifiez que Chrome est installé")
        return False

if __name__ == "__main__":
    try:
        success = test_chromedriver()
        print("\n" + "=" * 60)
        if success:
            print("🎉 Test terminé avec succès!")
        else:
            print("❌ Test échoué")
        print("=" * 60)
        
        input("\n⏸️  Appuyez sur Entrée pour fermer...")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        input("\n⏸️  Appuyez sur Entrée pour fermer...")
