"""
Test direct de l'ouverture du navigateur pour la génération de cookies
"""

import sys
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_browser_opening():
    """Test d'ouverture du navigateur comme dans l'interface"""
    
    print("=" * 70)
    print("   TEST D'OUVERTURE DU NAVIGATEUR")
    print("=" * 70 + "\n")
    
    # Import du cookie_manager
    from Functions.cookie_manager import CookieManager
    from pathlib import Path
    
    # Créer le cookie manager (avec le dossier, pas le fichier)
    config_dir = Path("Configuration")
    cookie_manager = CookieManager(config_dir)
    
    print("🔧 Cookie Manager initialisé")
    print(f"📁 Cookie file: {cookie_manager.cookie_file}\n")
    
    # Appeler la fonction de génération
    print("🚀 Appel de generate_cookies_with_browser()...\n")
    success, message, driver = cookie_manager.generate_cookies_with_browser()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ SUCCESS - Le navigateur devrait être ouvert!")
        print("=" * 70)
        print(f"📊 Message: {message}")
        print(f"🌐 Driver: {driver}")
        
        if driver:
            print("\n⏳ Le navigateur est ouvert. Vérifiez votre écran!")
            print("📋 Tapez 'ok' une fois que vous êtes connecté, ou 'quit' pour annuler")
            
            user_input = input("\n>>> ").strip().lower()
            
            if user_input == 'ok':
                print("\n💾 Sauvegarde des cookies...")
                success2, message2, count = cookie_manager.save_cookies_from_driver(driver)
                
                if success2:
                    print(f"✅ {count} cookies sauvegardés!")
                else:
                    print(f"❌ Erreur: {message2}")
            
            # Fermer le navigateur
            print("\n🔒 Fermeture du navigateur...")
            try:
                driver.quit()
                print("✅ Navigateur fermé")
            except Exception as e:
                print(f"⚠️  Erreur lors de la fermeture: {e}")
        
    else:
        print("❌ ÉCHEC - Le navigateur n'a pas pu s'ouvrir")
        print("=" * 70)
        print(f"❌ Message d'erreur:\n{message}")
        print("\n💡 SOLUTIONS:")
        print("1. Vérifiez que Chrome est installé")
        print("2. Exécutez: python .\\Tools\\download_chromedriver_simple.py")
        print("3. Vérifiez les logs ci-dessus pour plus de détails")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        test_browser_opening()
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n⏸️  Appuyez sur Entrée pour fermer...")
