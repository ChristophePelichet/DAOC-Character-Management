#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test du gestionnaire de cookies
"""

from Functions.cookie_manager import CookieManager

def test_cookie_manager():
    """Test du CookieManager"""
    
    print("=" * 60)
    print("TEST DU COOKIE MANAGER")
    print("=" * 60)
    
    # Create the Manager
    manager = CookieManager()
    
    print(f"\n✓ CookieManager initialisé")
    print(f"  Fichier: {manager.cookie_file}")
    print(f"  Existe: {manager.cookie_exists()}")
    
    # Retrieve the infos
    info = manager.get_cookie_info()
    
    if info is None:
        print("\n❌ Aucun cookie trouvé")
        return False
    
    print("\n" + "=" * 60)
    print("INFORMATIONS SUR LES COOKIES")
    print("=" * 60)
    
    print(f"\nTotal cookies: {info['total_cookies']}")
    print(f"Cookies valides: {info['valid_cookies']}")
    print(f"Cookies expirés: {info['expired_cookies']}")
    print(f"Cookies de session: {info['session_cookies']}")
    print(f"État: {'✅ Valide' if info['is_valid'] else '❌ Invalide'}")
    
    if info.get('expiry_date'):
        print(f"\n📅 Date d'expiration: {info['expiry_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        from datetime import datetime
        now = datetime.now()
        duration = info['expiry_date'] - now
        print(f"⏰ Validité restante: {duration.days} jours")
    
    # Détails des cookies valides
    if info['details']['valid']:
        print("\n" + "-" * 60)
        print("COOKIES VALIDES:")
        print("-" * 60)
        for cookie in info['details']['valid']:
            print(f"  • {cookie['name']}")
            print(f"    Domain: {cookie['domain']}")
            print(f"    Expire: {cookie['expires_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Reste: {cookie['days_remaining']} jours, {cookie['hours_remaining']} heures")
            print()
    
    return info['is_valid']

if __name__ == "__main__":
    result = test_cookie_manager()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ TEST RÉUSSI - Gestionnaire opérationnel")
    else:
        print("❌ TEST ÉCHOUÉ")
    print("=" * 60)