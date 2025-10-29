#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script pour analyser et sauvegarder les cookies de session"""

import pickle
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json

def save_cookies_after_auth():
    """Authentifier et sauvegarder les cookies"""
    print("Ouverture du navigateur pour authentification...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Aller à la page de login OAuth
        discord_login_url = "https://eden-daoc.net/ucp.php?mode=login&redirect=forum.php%2Fforum&login=external&oauth_service=studio_discord"
        driver.get(discord_login_url)
        
        print("\nVeuillez vous connecter avec Discord dans le navigateur...")
        input("Appuyez sur Entrée une fois connecté...")
        
        # Récupérer tous les cookies
        cookies = driver.get_cookies()
        
        print(f"\n=== {len(cookies)} cookies trouvés ===\n")
        
        # Analyser chaque cookie
        cookie_info = []
        for cookie in cookies:
            info = {
                'name': cookie.get('name'),
                'domain': cookie.get('domain'),
                'path': cookie.get('path'),
                'secure': cookie.get('secure'),
                'httpOnly': cookie.get('httpOnly'),
                'expiry': cookie.get('expiry'),
                'value_length': len(cookie.get('value', ''))
            }
            
            # Calculer la durée de validité
            if cookie.get('expiry'):
                expiry_date = datetime.fromtimestamp(cookie['expiry'])
                now = datetime.now()
                duration = expiry_date - now
                info['expires_in'] = str(duration)
                info['expires_at'] = expiry_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                info['expires_in'] = 'Session (jusqu\'à fermeture du navigateur)'
                info['expires_at'] = 'N/A'
            
            cookie_info.append(info)
            
            print(f"Cookie: {info['name']}")
            print(f"  Domain: {info['domain']}")
            print(f"  Expire: {info['expires_at']}")
            print(f"  Durée: {info['expires_in']}")
            print(f"  Secure: {info['secure']}, HttpOnly: {info['httpOnly']}")
            print()
        
        # Sauvegarder les cookies avec pickle (format complet)
        with open('session_cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        print("✓ Cookies sauvegardés dans session_cookies.pkl")
        
        # Sauvegarder aussi en JSON pour analyse
        with open('cookies_info.json', 'w', encoding='utf-8') as f:
            json.dump(cookie_info, f, ensure_ascii=False, indent=2)
        print("✓ Informations des cookies sauvegardées dans cookies_info.json")
        
        driver.quit()
        return cookies
        
    except Exception as e:
        print(f"Erreur: {e}")
        driver.quit()
        return None

def test_cookies_validity():
    """Tester si les cookies sauvegardés sont encore valides"""
    try:
        with open('session_cookies.pkl', 'rb') as f:
            cookies = pickle.load(f)
        
        print(f"\n=== Test de validité des cookies ===")
        print(f"Cookies chargés: {len(cookies)}")
        
        # Vérifier l'expiration
        now = datetime.now()
        valid_cookies = 0
        expired_cookies = 0
        
        for cookie in cookies:
            if cookie.get('expiry'):
                expiry_date = datetime.fromtimestamp(cookie['expiry'])
                if expiry_date > now:
                    valid_cookies += 1
                else:
                    expired_cookies += 1
                    print(f"  ⚠ Cookie '{cookie['name']}' a expiré")
            else:
                print(f"  ℹ Cookie '{cookie['name']}' est un cookie de session")
        
        print(f"\nRésultat: {valid_cookies} valides, {expired_cookies} expirés")
        return valid_cookies > 0
        
    except FileNotFoundError:
        print("Aucun cookie sauvegardé. Exécutez d'abord save_cookies_after_auth()")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_cookies_validity()
    else:
        save_cookies_after_auth()
