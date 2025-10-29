#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Scraper amélioré avec gestion de session persistante"""

import pickle
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json

class PersistentScraper:
    def __init__(self, cookie_file='session_cookies.pkl'):
        self.cookie_file = cookie_file
        self.driver = None
    
    def cookies_are_valid(self):
        """Vérifier si les cookies sauvegardés sont encore valides"""
        if not os.path.exists(self.cookie_file):
            return False
        
        try:
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            now = datetime.now()
            for cookie in cookies:
                if cookie.get('expiry'):
                    expiry_date = datetime.fromtimestamp(cookie['expiry'])
                    if expiry_date <= now:
                        print(f"⚠ Cookie '{cookie['name']}' a expiré")
                        return False
            
            print("✓ Cookies valides trouvés")
            return True
        except Exception as e:
            print(f"Erreur lors de la vérification des cookies: {e}")
            return False
    
    def authenticate_and_save_cookies(self):
        """Authentifier et sauvegarder les cookies"""
        print("🔐 Authentification requise...")
        print("Ouverture du navigateur...")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        try:
            discord_login_url = "https://eden-daoc.net/ucp.php?mode=login&redirect=forum.php%2Fforum&login=external&oauth_service=studio_discord"
            self.driver.get(discord_login_url)
            
            print("\nVeuillez vous connecter avec Discord dans le navigateur...")
            input("Appuyez sur Entrée une fois connecté...")
            
            # Sauvegarder les cookies
            cookies = self.driver.get_cookies()
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            print(f"✓ {len(cookies)} cookies sauvegardés pour réutilisation future")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'authentification: {e}")
            return False
    
    def load_cookies(self):
        """Charger les cookies dans le navigateur"""
        if not os.path.exists(self.cookie_file):
            return False
        
        try:
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            # Aller d'abord sur le domaine pour pouvoir ajouter les cookies
            self.driver.get("https://eden-daoc.net/")
            
            # Ajouter chaque cookie
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Impossible d'ajouter le cookie {cookie.get('name')}: {e}")
            
            print(f"✓ {len(cookies)} cookies chargés")
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement des cookies: {e}")
            return False
    
    def scrape_with_session(self, url):
        """Scraper une URL en utilisant la session persistante"""
        
        # Vérifier si on a des cookies valides
        if not self.cookies_are_valid():
            print("❌ Pas de cookies valides")
            if not self.authenticate_and_save_cookies():
                return None
        else:
            print("♻️ Réutilisation des cookies existants")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            self.load_cookies()
        
        try:
            # Aller à l'URL cible
            print(f"📡 Accès à {url}")
            self.driver.get(url)
            
            # Attendre un peu que la page se charge
            import time
            time.sleep(2)
            
            # Récupérer le HTML
            html_content = self.driver.page_source
            
            # Parser avec BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraire les données
            data = self.extract_data(soup)
            
            return data
            
        except Exception as e:
            print(f"Erreur lors du scraping: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def extract_data(self, soup):
        """Extraire les données de la page"""
        data = {
            'title': soup.find('title').get_text(strip=True) if soup.find('title') else None,
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
            'tables': []
        }
        
        # Récupérer les tableaux
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_data.append(cells)
            if table_data:
                data['tables'].append(table_data)
        
        print(f"✓ Données extraites: {len(data['tables'])} tableaux")
        return data

def main():
    """Exemple d'utilisation"""
    scraper = PersistentScraper()
    
    # Scraper un personnage
    url = "https://eden-daoc.net/herald?n=player&k=Ewolinette"
    data = scraper.scrape_with_session(url)
    
    if data:
        # Sauvegarder
        with open('scraped_with_session.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✓ Données sauvegardées dans scraped_with_session.json")

if __name__ == "__main__":
    main()
