#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug détaillé - Affiche ce que test_eden_connection() voit
"""

import sys
sys.path.insert(0, r'D:\Projets\Python\DAOC-Character-Management')

from Functions.cookie_manager import CookieManager

cookie_mgr = CookieManager()

print("Exécution de test_eden_connection()...")
result = cookie_mgr.test_eden_connection()

print(f"\nRésultat:")
print(f"  accessible: {result.get('accessible')}")
print(f"  message: {result.get('message')}")

# Vérifier le HTML sauvegardé par test
print("\nVérification du HTML sauvegardé...")
try:
    with open(r'd:\Projets\Python\DAOC-Character-Management\Scripts\debug_herald_page.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Cherche redirect=app.php
    if 'redirect=app.php' in html:
        print("  - 'redirect=app.php' TROUVÉ dans HTML")
        # Affiche le contexte
        idx = html.find('redirect=app.php')
        print(f"  Contexte: {html[idx-50:idx+100]}")
    else:
        print("  - 'redirect=app.php' PAS trouvé")
    
    # Cherche login
    if 'login' in html.lower():
        print("  - 'login' TROUVÉ (case-insensitive)")
    
    # Cherche herald
    if 'herald' in html.lower():
        print("  - 'herald' TROUVÉ (case-insensitive)")
    
    # Cherche ucp.php
    if 'ucp.php' in html:
        print("  - 'ucp.php' TROUVÉ")
except Exception as e:
    print(f"  Erreur: {e}")
