#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test de stabilité pour la recherche Herald
Simule plusieurs recherches consécutives pour détecter les crashs
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Functions.eden_scraper import search_herald_character
from Functions.logging_manager import get_logger, LOGGER_EDEN

logger = get_logger(LOGGER_EDEN)

# Configuration du test
TEST_CHARACTERS = [
    ("Testchar", ""),       # Tous royaumes
    ("Merlin", "alb"),      # Albion
    ("Arthur", "alb"),      # Albion
    ("Lancelot", ""),       # Tous royaumes
    ("Galahad", "mid"),     # Midgard
]

ITERATIONS = 5  # Nombre of fois qu'on répète all the tests
DELAY_BETWEEN_SEARCHES = 3  # Secondes entre chaque recherche


def test_search_stability():
    """
    Test de stabilité des recherches Herald
    """
    print("\n" + "="*80)
    print("🔍 TEST DE STABILITÉ - RECHERCHE HERALD")
    print("="*80)
    print(f"Configuration:")
    print(f"  - Personnages à tester: {len(TEST_CHARACTERS)}")
    print(f"  - Itérations: {ITERATIONS}")
    print(f"  - Délai entre recherches: {DELAY_BETWEEN_SEARCHES}s")
    print(f"  - Total de recherches: {len(TEST_CHARACTERS) * ITERATIONS}")
    print("="*80 + "\n")
    
    total_tests = len(TEST_CHARACTERS) * ITERATIONS
    current_test = 0
    successes = 0
    failures = 0
    errors = []
    
    start_time = time.time()
    
    for iteration in range(1, ITERATIONS + 1):
        print(f"\n{'─'*80}")
        print(f"📋 ITÉRATION {iteration}/{ITERATIONS}")
        print(f"{'─'*80}\n")
        
        for char_name, realm in TEST_CHARACTERS:
            current_test += 1
            realm_str = f" ({realm.upper()})" if realm else " (TOUS)"
            
            print(f"[{current_test}/{total_tests}] 🔎 Recherche: {char_name}{realm_str}...", end=" ", flush=True)
            
            try:
                # Lancer la recherche
                test_start = time.time()
                success, message, json_path = search_herald_character(char_name, realm)
                test_duration = time.time() - test_start
                
                if success:
                    print(f"✅ OK ({test_duration:.1f}s) - {message}")
                    successes += 1
                    logger.info(f"Test {current_test}/{total_tests} réussi: {char_name} - {message}")
                else:
                    print(f"❌ ÉCHEC ({test_duration:.1f}s) - {message}")
                    failures += 1
                    error_msg = f"Test {current_test}: {char_name}{realm_str} - {message}"
                    errors.append(error_msg)
                    logger.error(f"Test {current_test}/{total_tests} échoué: {char_name} - {message}")
                
            except Exception as e:
                test_duration = time.time() - test_start if 'test_start' in locals() else 0
                print(f"💥 CRASH ({test_duration:.1f}s) - {str(e)}")
                failures += 1
                error_msg = f"Test {current_test}: {char_name}{realm_str} - EXCEPTION: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Test {current_test}/{total_tests} crashé: {char_name} - {str(e)}")
            
            # Wait entre the recherches (sauf for the dernière)
            if current_test < total_tests:
                print(f"   ⏱️  Attente {DELAY_BETWEEN_SEARCHES}s...\n")
                time.sleep(DELAY_BETWEEN_SEARCHES)
    
    # Results finaux
    total_duration = time.time() - start_time
    
    print("\n" + "="*80)
    print("📊 RÉSULTATS FINAUX")
    print("="*80)
    print(f"Tests effectués:  {total_tests}")
    print(f"✅ Réussis:       {successes} ({successes/total_tests*100:.1f}%)")
    print(f"❌ Échoués:       {failures} ({failures/total_tests*100:.1f}%)")
    print(f"⏱️  Durée totale:  {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"⏱️  Durée moyenne: {total_duration/total_tests:.1f}s par recherche")
    print("="*80)
    
    if errors:
        print(f"\n⚠️  ERREURS DÉTECTÉES ({len(errors)}):")
        print("─"*80)
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
        print("="*80)
    else:
        print("\n✨ AUCUNE ERREUR - SYSTÈME STABLE ✨")
        print("="*80)
    
    # Sauvegarde du rapport
    report_path = project_root / "Logs" / f"stability_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("RAPPORT DE TEST DE STABILITÉ - RECHERCHE HERALD\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration:\n")
        f.write(f"  - Personnages testés: {len(TEST_CHARACTERS)}\n")
        f.write(f"  - Itérations: {ITERATIONS}\n")
        f.write(f"  - Total de recherches: {total_tests}\n")
        f.write(f"  - Délai entre recherches: {DELAY_BETWEEN_SEARCHES}s\n\n")
        f.write("="*80 + "\n\n")
        f.write("RÉSULTATS:\n")
        f.write(f"  - Tests effectués: {total_tests}\n")
        f.write(f"  - Réussis: {successes} ({successes/total_tests*100:.1f}%)\n")
        f.write(f"  - Échoués: {failures} ({failures/total_tests*100:.1f}%)\n")
        f.write(f"  - Durée totale: {total_duration:.1f}s ({total_duration/60:.1f} min)\n")
        f.write(f"  - Durée moyenne: {total_duration/total_tests:.1f}s\n\n")
        
        if errors:
            f.write("="*80 + "\n\n")
            f.write(f"ERREURS DÉTECTÉES ({len(errors)}):\n")
            f.write("─"*80 + "\n")
            for i, error in enumerate(errors, 1):
                f.write(f"{i}. {error}\n")
    
    print(f"\n📄 Rapport sauvegardé: {report_path}\n")
    
    # Code de sortie
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = test_search_stability()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)