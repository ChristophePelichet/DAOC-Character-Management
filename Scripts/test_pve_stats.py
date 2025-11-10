"""
Script de test pour analyser le contenu de l'onglet PvE du Herald
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

def test_pve_content():
    """Teste le scraping de l'onglet PvE"""
    driver = None
    try:
        # Configuration
        driver = webdriver.Chrome()
        driver.minimize_window()
        
        url = 'https://eden-daoc.net/herald/character?realm=albion&server=1&name=Whispyr'
        driver.get(url)
        
        # Charger les cookies
        cookies_folder = "D:\\Projets\\Python\\DAOC-Character-Management\\Configuration"
        cookies_file = os.path.join(cookies_folder, "herald_cookies.json")
        
        if os.path.exists(cookies_file):
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    if 'sameSite' in cookie:
                        cookie['sameSite'] = 'Lax'
                    driver.add_cookie(cookie)
            
            driver.refresh()
            time.sleep(2)
        
        # Cliquer sur l'onglet PvE
        print("Recherche de l'onglet PvE...")
        pve_tab = driver.find_element(By.XPATH, "//a[@href='#tabs-pve']")
        pve_tab.click()
        time.sleep(1)
        
        # Récupérer le contenu
        pve_content = driver.find_element(By.ID, 'tabs-pve')
        
        print("\n=== CONTENU TEXTE DE L'ONGLET PVE ===\n")
        print(pve_content.text)
        
        print("\n\n=== STRUCTURE HTML ===\n")
        html = pve_content.get_attribute('outerHTML')
        
        # Sauvegarder pour analyse
        with open('pve_content.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("HTML sauvegardé dans pve_content.html")
        
        # Analyser les tableaux
        tables = pve_content.find_elements(By.TAG_NAME, 'table')
        print(f"\n=== NOMBRE DE TABLEAUX: {len(tables)} ===\n")
        
        for i, table in enumerate(tables):
            print(f"\n--- TABLEAU {i+1} ---")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if cells:
                    print(" | ".join(cell.text for cell in cells))
        
        print("\n\n=== NAVIGATEUR RESTE OUVERT POUR INSPECTION ===")
        print("Appuyez sur Entrée pour fermer le navigateur...")
        input()
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        print("\nNavigateur reste ouvert pour inspection. Appuyez sur Entrée pour fermer...")
        input()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_pve_content()
