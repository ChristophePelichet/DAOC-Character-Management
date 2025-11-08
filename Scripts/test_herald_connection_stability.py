"""
Test de stabilité pour la vérification de connexion Herald Eden
Effectue 25 tests consécutifs pour détecter les crashs potentiels

Similaire au test de recherche Herald mais pour test_eden_connection()
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.cookie_manager import CookieManager

def test_connection_stability(num_tests=25):
    """
    Teste la stabilité de la fonction test_eden_connection
    
    Args:
        num_tests: Nombre de tests à effectuer (défaut: 25)
    """
    print("=" * 80)
    print(f"🧪 TEST DE STABILITÉ - Vérification Connexion Herald Eden")
    print(f"📊 Nombre de tests: {num_tests}")
    print(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    results = {
        'success': 0,
        'failed': 0,
        'errors': [],
        'times': []
    }
    
    cookie_manager = CookieManager()
    
    # Vérifier que les cookies existent avant de commencer
    if not cookie_manager.cookie_exists():
        print("❌ ERREUR: Aucun cookie trouvé. Veuillez générer ou importer des cookies d'abord.")
        return
    
    print(f"✅ Cookies trouvés - Début des tests...\n")
    
    for i in range(1, num_tests + 1):
        print(f"[{i:2d}/{num_tests}] Test de connexion Herald en cours...", end=" ", flush=True)
        
        start_time = time.time()
        
        try:
            result = cookie_manager.test_eden_connection()
            elapsed = time.time() - start_time
            results['times'].append(elapsed)
            
            if result.get('success'):
                accessible = result.get('accessible', False)
                if accessible:
                    print(f"✅ CONNECTÉ ({elapsed:.1f}s)")
                    results['success'] += 1
                else:
                    print(f"⚠️  NON CONNECTÉ ({elapsed:.1f}s)")
                    results['success'] += 1  # Test réussi même si pas connecté
            else:
                print(f"❌ ÉCHEC ({elapsed:.1f}s) - {result.get('message', 'Unknown error')}")
                results['failed'] += 1
                results['errors'].append({
                    'test': i,
                    'message': result.get('message'),
                    'time': elapsed
                })
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"💥 CRASH ({elapsed:.1f}s) - {str(e)}")
            results['failed'] += 1
            results['errors'].append({
                'test': i,
                'message': f"EXCEPTION: {str(e)}",
                'time': elapsed
            })
        
        # Petite pause entre les tests pour éviter de surcharger
        if i < num_tests:
            time.sleep(1)
    
    # Statistiques finales
    print()
    print("=" * 80)
    print("📊 RÉSULTATS")
    print("=" * 80)
    print(f"✅ Tests réussis: {results['success']}/{num_tests} ({results['success']/num_tests*100:.1f}%)")
    print(f"❌ Tests échoués: {results['failed']}/{num_tests} ({results['failed']/num_tests*100:.1f}%)")
    
    if results['times']:
        avg_time = sum(results['times']) / len(results['times'])
        min_time = min(results['times'])
        max_time = max(results['times'])
        total_time = sum(results['times'])
        
        print()
        print("⏱️  TEMPS D'EXÉCUTION:")
        print(f"   • Moyen: {avg_time:.1f}s")
        print(f"   • Min: {min_time:.1f}s")
        print(f"   • Max: {max_time:.1f}s")
        print(f"   • Total: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    
    if results['errors']:
        print()
        print("❌ ERREURS DÉTECTÉES:")
        for error in results['errors']:
            print(f"   • Test #{error['test']}: {error['message']} ({error['time']:.1f}s)")
    
    print()
    print("=" * 80)
    print(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Verdict final
    print()
    if results['failed'] == 0:
        print("🎉 SUCCÈS TOTAL: Aucun crash détecté! Le fix fonctionne parfaitement.")
    else:
        print(f"⚠️  {results['failed']} échec(s) détecté(s). Vérifiez les erreurs ci-dessus.")
    
    return results


if __name__ == "__main__":
    # Lancer 25 tests par défaut
    num_tests = 25
    
    # Permettre de spécifier un nombre différent via ligne de commande
    if len(sys.argv) > 1:
        try:
            num_tests = int(sys.argv[1])
        except ValueError:
            print(f"❌ Nombre de tests invalide: {sys.argv[1]}")
            print(f"Usage: python {os.path.basename(__file__)} [nombre_de_tests]")
            sys.exit(1)
    
    test_connection_stability(num_tests)
