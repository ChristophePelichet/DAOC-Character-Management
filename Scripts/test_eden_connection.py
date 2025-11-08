"""
Script de test pour vérifier la connexion au site Eden avec les cookies
"""
import sys
sys.path.insert(0, '..')

from Functions.cookie_manager import CookieManager
import requests

def test_various_urls():
    """Teste plusieurs URLs Eden pour voir lesquelles fonctionnent"""
    
    cm = CookieManager()
    
    if not cm.cookie_exists():
        print("❌ Aucun cookie trouvé")
        return
    
    cookies_list = cm.get_cookies_for_scraper()
    if not cookies_list:
        print("❌ Cookies invalides")
        return
    
    print(f"✅ {len(cookies_list)} cookies chargés:")
    for cookie in cookies_list:
        print(f"  - {cookie['name']}: {cookie['value'][:20]}...")
    
    # Convertir en session requests
    session = requests.Session()
    for cookie in cookies_list:
        session.cookies.set(
            name=cookie.get('name'),
            value=cookie.get('value'),
            domain=cookie.get('domain'),
            path=cookie.get('path', '/')
        )
    
    # Tester plusieurs URLs
    test_urls = [
        'https://eden-daoc.net/',
        'https://eden-daoc.net/herald',
        'https://eden-daoc.net/herald?n=player',
        'https://eden-daoc.net/herald?n=player&k=Test',
        'https://eden-daoc.net/forum.php',
        'https://eden-daoc.net/ucp.php',
    ]
    
    print("\n🔍 Test des URLs:")
    for url in test_urls:
        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            final_url = response.url
            redirect_info = f" → {final_url}" if final_url != url else ""
            
            if 'login' in final_url.lower() or 'ucp.php?mode=login' in final_url:
                print(f"❌ {url} (Code {response.status_code}) → REDIRIGÉ VERS LOGIN")
            else:
                print(f"✅ {url} (Code {response.status_code}){redirect_info}")
                
                # Check the contenu of the page
                if 'login' in response.text.lower() or 'se connecter' in response.text.lower():
                    print(f"   ⚠️  Contenu suggère qu'on n'est pas connecté")
                    
        except Exception as e:
            print(f"❌ {url} - Erreur: {e}")

if __name__ == "__main__":
    test_various_urls()