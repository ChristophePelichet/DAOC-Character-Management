"""
Script de débogage pour comprendre pourquoi les cookies ne fonctionnent pas
"""
import sys
sys.path.insert(0, '..')

from Functions.cookie_manager import CookieManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def debug_cookies():
    """Debug détaillé du comportement des cookies"""
    
    cm = CookieManager()
    
    if not cm.cookie_exists():
        print("❌ Aucun cookie trouvé")
        return
    
    cookies_list = cm.get_cookies_for_scraper()
    print(f"✅ {len(cookies_list)} cookies chargés:")
    for cookie in cookies_list:
        print(f"  - {cookie['name']}: domain={cookie.get('domain')}, path={cookie.get('path', '/')}")
    
    # Tester avec navigateur visible
    print("\n🌐 Ouverture du navigateur (VISIBLE pour debug)...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Step 1: Aller on the page d'accueil
        print("\n📍 Étape 1: Chargement de la page d'accueil...")
        driver.get("https://eden-daoc.net/")
        print(f"   URL: {driver.current_url}")
        input("   ⏸️  Vérifiez la page d'accueil, puis appuyez sur Entrée...")
        
        # Step 2: Add cookies
        print("\n🍪 Étape 2: Ajout des cookies...")
        for cookie in cookies_list:
            try:
                driver.add_cookie(cookie)
                print(f"   ✅ Cookie ajouté: {cookie['name']}")
            except Exception as e:
                print(f"   ❌ Erreur pour {cookie['name']}: {e}")
        
        # Check cookies actuels dans le navigateur
        print("\n🔍 Cookies dans le navigateur:")
        current_cookies = driver.get_cookies()
        for cookie in current_cookies:
            print(f"   - {cookie['name']}: {cookie['value'][:30]}...")
        
        input("   ⏸️  Vérifiez les cookies, puis appuyez sur Entrée...")
        
        # Step 3: Recharger the page d'accueil
        print("\n🔄 Étape 3: Rechargement de la page d'accueil avec les cookies...")
        driver.get("https://eden-daoc.net/")
        print(f"   URL: {driver.current_url}")
        
        # Check if on voit un indicateur of connexion
        page_source = driver.page_source
        if 'se connecter' in page_source.lower() or 'connexion' in page_source.lower():
            print("   ⚠️  Texte 'connexion' trouvé dans la page")
        if 'logout' in page_source.lower() or 'déconnexion' in page_source.lower():
            print("   ✅ Texte 'déconnexion' trouvé - On semble connecté!")
        
        input("   ⏸️  La page d'accueil affiche-t-elle que vous êtes connecté? Appuyez sur Entrée...")
        
        # Step 4: Aller on the forum
        print("\n📝 Étape 4: Navigation vers le forum...")
        driver.get("https://eden-daoc.net/forum.php")
        print(f"   URL finale: {driver.current_url}")
        
        page_source = driver.page_source.lower()
        if 'mode=login' in page_source:
            print("   ❌ 'mode=login' trouvé dans le code source")
        if 'connexion' in page_source and 'mot de passe' in page_source:
            print("   ❌ Formulaire de connexion détecté")
        if 'logout' in page_source or 'déconnexion' in page_source:
            print("   ✅ On semble être connecté sur le forum!")
        
        input("   ⏸️  Êtes-vous connecté sur le forum? Appuyez sur Entrée...")
        
        print("\n✅ Test terminé - analysez les résultats ci-dessus")
        
    finally:
        print("\n🔒 Fermeture du navigateur...")
        driver.quit()

if __name__ == "__main__":
    debug_cookies()