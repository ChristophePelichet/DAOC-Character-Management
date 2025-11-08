"""
Test de connexion avec Selenium au lieu de requests
"""
import sys
sys.path.insert(0, '..')

from Functions.cookie_manager import CookieManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_with_selenium():
    """Teste la connexion avec Selenium comme le fait le scraper"""
    
    cm = CookieManager()
    
    if not cm.cookie_exists():
        print("❌ Aucun cookie trouvé")
        return
    
    cookies_list = cm.get_cookies_for_scraper()
    if not cookies_list:
        print("❌ Cookies invalides")
        return
    
    print(f"✅ {len(cookies_list)} cookies chargés")
    
    # Create un driver Selenium
    print("\n🌐 Ouverture du navigateur...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Aller sur le site
        driver.get("https://eden-daoc.net/")
        print("✅ Page d'accueil chargée")
        
        # Ajouter les cookies
        for cookie in cookies_list:
            driver.add_cookie(cookie)
        print("✅ Cookies ajoutés")
        
        # Tester plusieurs URLs
        test_urls = [
            'https://eden-daoc.net/herald?n=player&k=Ewolinette',
            'https://eden-daoc.net/forum.php',
        ]
        
        for url in test_urls:
            print(f"\n🔍 Test de {url}")
            driver.get(url)
            
            current_url = driver.current_url
            page_source = driver.page_source[:500]
            
            print(f"  URL finale: {current_url}")
            
            if 'login' in current_url.lower() or 'ucp.php?mode=login' in current_url:
                print(f"  ❌ Redirigé vers la page de login")
            elif '404' in page_source or 'not found' in page_source.lower():
                print(f"  ❌ Page 404")
            else:
                print(f"  ✅ Page chargée correctement")
            
            input(f"\n⏸️  Vérifiez la page dans le navigateur, puis appuyez sur Entrée...")
        
    finally:
        driver.quit()
        print("\n✅ Navigateur fermé")

if __name__ == "__main__":
    test_with_selenium()