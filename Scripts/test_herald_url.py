"""
Test de l'URL Herald spécifique avec les cookies
"""
import sys
sys.path.insert(0, '..')

from Functions.cookie_manager import CookieManager

def test_herald():
    """Test simple de connexion au Herald"""
    
    cm = CookieManager()
    
    if not cm.cookie_exists():
        print("❌ Aucun cookie trouvé")
        return
    
    print("🔍 Test de connexion au Herald...")
    result = cm.test_eden_connection()
    
    print(f"\n📊 Résultat:")
    print(f"  Success: {result['success']}")
    print(f"  Status Code: {result['status_code']}")
    print(f"  Message: {result['message']}")
    print(f"  Accessible: {result['accessible']}")
    
    if result['accessible']:
        print("\n✅ Les cookies fonctionnent ! Le Herald est accessible.")
    else:
        print("\n❌ Les cookies ne fonctionnent pas. Régénérez-les.")

if __name__ == "__main__":
    test_herald()