#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la détection de connexion au Herald Eden
Test basé sur le message d'erreur "The requested page "herald" is not available."
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Functions.cookie_manager import CookieManager
import time

def test_herald_detection():
    """Test de la détection de connexion au Herald"""
    print("=" * 60)
    print("TEST DE DÉTECTION DE CONNEXION AU HERALD EDEN")
    print("=" * 60)
    
    # Créer le cookie manager
    cookie_mgr = CookieManager()
    
    # Vérifier si on a des cookies
    if not cookie_mgr.cookie_exists():
        print("\n❌ Pas de cookies disponibles")
        print("💡 Générez d'abord des cookies via le Cookie Manager")
        return
    
    print("\n✅ Cookies trouvés - Début du test...")
    
    # Initialiser un driver
    print("\n📌 Initialisation du navigateur...")
    driver, browser_name = cookie_mgr._initialize_browser_driver(
        headless=False,  # Mode visible pour que tu puisses voir
        preferred_browser='Chrome',
        allow_download=False
    )
    
    if not driver:
        print("❌ Impossible d'initialiser le driver")
        return
    
    print(f"✅ Navigateur initialisé: {browser_name}")
    
    try:
        # Aller sur eden-daoc.net
        print("\n📌 Étape 1: Navigation vers https://eden-daoc.net/")
        driver.get("https://eden-daoc.net/")
        time.sleep(2)
        
        # Charger les cookies
        print("\n📌 Étape 2: Chargement des cookies...")
        cookies_list = cookie_mgr.get_cookies_for_scraper()
        cookies_added = 0
        for cookie in cookies_list:
            try:
                driver.add_cookie(cookie)
                cookies_added += 1
            except Exception as e:
                print(f"⚠️  Cookie {cookie.get('name')} non ajouté: {e}")
        
        print(f"✅ {cookies_added}/{len(cookies_list)} cookies chargés")
        
        # Rafraîchir
        print("\n📌 Étape 3: Rafraîchissement de la page...")
        driver.refresh()
        time.sleep(2)
        
        # Aller sur le Herald
        print("\n📌 Étape 4: Navigation vers https://eden-daoc.net/herald")
        driver.get("https://eden-daoc.net/herald")
        time.sleep(3)
        
        # Analyser le contenu
        print("\n📌 Étape 5: Analyse du contenu de la page...")
        page_source = driver.page_source
        
        # TEST PRINCIPAL: Message d'erreur spécifique
        error_message = 'The requested page "herald" is not available.'
        has_error_message = error_message in page_source
        
        # TESTS SECONDAIRES
        has_not_available = 'is not available' in page_source.lower()
        has_herald_menu = 'herald' in page_source.lower() and 'menu' in page_source.lower()
        has_top_players = 'top_players' in page_source.lower() or 'top players' in page_source.lower()
        has_player_search = 'player' in page_source.lower() and 'search' in page_source.lower()
        
        # Afficher les résultats
        print("\n" + "=" * 60)
        print("RÉSULTATS DE L'ANALYSE")
        print("=" * 60)
        print(f"\n🔍 Message exact d'erreur trouvé: {has_error_message}")
        print(f"   → '{error_message}'")
        print(f"\n🔍 'is not available' trouvé: {has_not_available}")
        print(f"🔍 Menu Herald trouvé: {has_herald_menu}")
        print(f"🔍 Top Players trouvé: {has_top_players}")
        print(f"🔍 Recherche joueur trouvée: {has_player_search}")
        
        # CONCLUSION
        print("\n" + "=" * 60)
        print("CONCLUSION")
        print("=" * 60)
        
        if has_error_message:
            print("\n❌ NON CONNECTÉ")
            print("   Raison: Message d'erreur détecté")
            print("   → Le Herald n'est pas accessible sans authentification")
        elif has_top_players or has_player_search:
            print("\n✅ CONNECTÉ")
            print("   Raison: Contenu du Herald détecté")
            print("   → Le Herald est accessible avec vos cookies")
        else:
            print("\n⚠️  ÉTAT INCERTAIN")
            print("   Raison: Ni message d'erreur, ni contenu Herald détecté")
        
        # Afficher un extrait de la page
        print("\n" + "=" * 60)
        print("EXTRAIT DE LA PAGE (500 premiers caractères)")
        print("=" * 60)
        print(page_source[:500])
        
        print("\n" + "=" * 60)
        print("Appuyez sur Entrée pour fermer le navigateur...")
        input()
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        print("\n📌 Fermeture du navigateur...")
        driver.quit()
        print("✅ Test terminé")

if __name__ == "__main__":
    test_herald_detection()
