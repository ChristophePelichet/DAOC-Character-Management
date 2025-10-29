#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de validité des cookies Eden
"""

import pickle
import os
from datetime import datetime
from pathlib import Path

def test_cookie_validity():
    """Tester si les cookies Eden sont encore valides"""
    
    cookie_file = Path(__file__).parent.parent / 'eden_scraper' / 'session_cookies.pkl'
    
    print("=" * 60)
    print("TEST DE VALIDITÉ DES COOKIES EDEN")
    print("=" * 60)
    
    if not cookie_file.exists():
        print("❌ Aucun fichier de cookies trouvé")
        print(f"   Chemin recherché: {cookie_file}")
        return False
    
    print(f"✓ Fichier de cookies trouvé: {cookie_file}")
    print()
    
    try:
        with open(cookie_file, 'rb') as f:
            cookies = pickle.load(f)
        
        print(f"📦 Nombre de cookies chargés: {len(cookies)}")
        print()
        
        now = datetime.now()
        valid_cookies = []
        expired_cookies = []
        session_cookies = []
        
        for cookie in cookies:
            cookie_name = cookie.get('name', 'Unknown')
            cookie_domain = cookie.get('domain', 'Unknown')
            
            if cookie.get('expiry'):
                expiry_timestamp = cookie['expiry']
                expiry_date = datetime.fromtimestamp(expiry_timestamp)
                
                if expiry_date > now:
                    # Cookie valide
                    duration = expiry_date - now
                    days = duration.days
                    hours = duration.seconds // 3600
                    
                    valid_cookies.append({
                        'name': cookie_name,
                        'domain': cookie_domain,
                        'expires_at': expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'days_remaining': days,
                        'hours_remaining': hours
                    })
                else:
                    # Cookie expiré
                    expired_cookies.append({
                        'name': cookie_name,
                        'domain': cookie_domain,
                        'expired_at': expiry_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
            else:
                # Cookie de session (pas d'expiration)
                session_cookies.append({
                    'name': cookie_name,
                    'domain': cookie_domain
                })
        
        # Affichage des résultats
        print("=" * 60)
        print("RÉSULTATS")
        print("=" * 60)
        
        if valid_cookies:
            print(f"\n✅ COOKIES VALIDES ({len(valid_cookies)}):")
            print("-" * 60)
            for cookie in valid_cookies:
                print(f"  • {cookie['name']}")
                print(f"    Domain: {cookie['domain']}")
                print(f"    Expire le: {cookie['expires_at']}")
                print(f"    Validité restante: {cookie['days_remaining']} jours, {cookie['hours_remaining']} heures")
                print()
        
        if expired_cookies:
            print(f"\n❌ COOKIES EXPIRÉS ({len(expired_cookies)}):")
            print("-" * 60)
            for cookie in expired_cookies:
                print(f"  • {cookie['name']}")
                print(f"    Domain: {cookie['domain']}")
                print(f"    Expiré le: {cookie['expired_at']}")
                print()
        
        if session_cookies:
            print(f"\n🔄 COOKIES DE SESSION ({len(session_cookies)}):")
            print("-" * 60)
            for cookie in session_cookies:
                print(f"  • {cookie['name']} ({cookie['domain']})")
            print("    (Valides jusqu'à la fermeture du navigateur)")
            print()
        
        # Conclusion
        print("=" * 60)
        print("CONCLUSION")
        print("=" * 60)
        
        if expired_cookies:
            print("❌ Des cookies ont expiré - Réauthentification nécessaire")
            return False
        elif valid_cookies:
            print("✅ Tous les cookies sont valides - Scraping possible")
            # Trouver le cookie avec la date d'expiration la plus proche
            min_cookie = min(valid_cookies, key=lambda x: x['days_remaining'])
            print(f"\n⏰ Prochaine expiration dans {min_cookie['days_remaining']} jours")
            print(f"   Cookie: {min_cookie['name']}")
            print(f"   Date: {min_cookie['expires_at']}")
            return True
        else:
            print("⚠️ Seulement des cookies de session - Réauthentification recommandée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des cookies: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_cookie_validity()
    print("\n" + "=" * 60)
    if result:
        print("✅ TEST RÉUSSI - Les cookies sont fonctionnels")
    else:
        print("❌ TEST ÉCHOUÉ - Réauthentification nécessaire")
    print("=" * 60)
