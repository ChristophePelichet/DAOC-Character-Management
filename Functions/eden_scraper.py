#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eden Scraper Manager - Gestion du scraping des données du Herald Eden-DAOC
Intégré depuis eden_scraper/ pour centraliser la gestion
"""

import logging
import pickle
import os
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json


class EdenScraper:
    """
    Gestionnaire de scraping pour le Herald Eden-DAOC
    Utilise Selenium pour gérer les sessions authentifiées
    """
    
    def __init__(self, cookie_manager):
        """
        Initialise le scraper avec un gestionnaire de cookies
        
        Args:
            cookie_manager: Instance de CookieManager pour gérer l'authentification
        """
        self.cookie_manager = cookie_manager
        self.driver = None
        
    def initialize_driver(self, headless=True):
        """
        Initialise le driver Selenium Chrome
        
        Args:
            headless: Si True, lance Chrome en mode sans interface
            
        Returns:
            bool: True si l'initialisation a réussi
        """
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--log-level=3')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logging.info("Driver Selenium initialisé avec succès")
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation du driver: {e}")
            return False
    
    def load_cookies(self):
        """
        Charge les cookies d'authentification dans le driver
        
        Returns:
            bool: True si les cookies ont été chargés
        """
        if not self.driver:
            logging.error("Driver non initialisé")
            return False
        
        try:
            cookies_list = self.cookie_manager.get_cookies_for_scraper()
            if not cookies_list:
                logging.error("Aucun cookie disponible")
                return False
            
            # Aller sur le domaine pour pouvoir ajouter les cookies
            self.driver.get("https://eden-daoc.net/")
            
            # Ajouter chaque cookie
            for cookie in cookies_list:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logging.warning(f"Impossible d'ajouter le cookie {cookie.get('name')}: {e}")
            
            logging.info(f"{len(cookies_list)} cookies chargés dans le driver")
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors du chargement des cookies: {e}")
            return False
    
    def scrape_character(self, character_name):
        """
        Scrape les données d'un personnage depuis le Herald
        
        Args:
            character_name: Nom du personnage à scraper
            
        Returns:
            dict: Données du personnage ou None en cas d'erreur
        """
        if not self.driver:
            if not self.initialize_driver():
                return None
        
        if not self.load_cookies():
            logging.error("Impossible de charger les cookies")
            return None
        
        try:
            # Construire l'URL du personnage
            url = f"https://eden-daoc.net/herald?n=player&k={character_name}"
            logging.info(f"Scraping du personnage: {character_name} ({url})")
            
            # Charger la page
            self.driver.get(url)
            
            # Attendre un peu que la page se charge
            import time
            time.sleep(2)
            
            # Récupérer le HTML
            html_content = self.driver.page_source
            
            # Parser avec BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraire les données
            data = self._extract_character_data(soup)
            data['character_name'] = character_name
            data['scraped_at'] = datetime.now().isoformat()
            
            logging.info(f"Données du personnage {character_name} extraites avec succès")
            return data
            
        except Exception as e:
            logging.error(f"Erreur lors du scraping du personnage {character_name}: {e}")
            return None
    
    def scrape_search_results(self, search_query, realm=None):
        """
        Scrape les résultats de recherche du Herald
        
        Args:
            search_query: Terme de recherche (nom de guilde, joueur, etc.)
            realm: Realm optionnel ('alb', 'mid', 'hib')
            
        Returns:
            list: Liste des personnages trouvés
        """
        if not self.driver:
            if not self.initialize_driver():
                return []
        
        if not self.load_cookies():
            logging.error("Impossible de charger les cookies")
            return []
        
        try:
            # Construire l'URL de recherche
            url = f"https://eden-daoc.net/herald?n=search&s={search_query}"
            if realm:
                url += f"&r={realm}"
            
            logging.info(f"Recherche: {search_query} (realm: {realm or 'tous'})")
            
            # Charger la page
            self.driver.get(url)
            
            # Attendre que la page se charge
            import time
            time.sleep(2)
            
            # Récupérer le HTML
            html_content = self.driver.page_source
            
            # Parser avec BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraire la liste des personnages
            characters = self._extract_search_results(soup)
            
            logging.info(f"{len(characters)} personnages trouvés")
            return characters
            
        except Exception as e:
            logging.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def _extract_character_data(self, soup):
        """
        Extrait les données d'un personnage depuis la page HTML
        
        Args:
            soup: Objet BeautifulSoup de la page
            
        Returns:
            dict: Données structurées du personnage
        """
        data = {
            'title': soup.title.string if soup.title else '',
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
            'tables': []
        }
        
        # Extraire les tableaux
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_data.append(cells)
            if table_data:
                data['tables'].append(table_data)
        
        return data
    
    def _extract_search_results(self, soup):
        """
        Extrait la liste des personnages depuis les résultats de recherche
        
        Args:
            soup: Objet BeautifulSoup de la page
            
        Returns:
            list: Liste de dict avec les infos des personnages
        """
        characters = []
        
        # Trouver le tableau des résultats
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if len(rows) > 1:
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # Vérifier si c'est le bon tableau (contient Name, Class, etc.)
                if 'Name' in headers or 'Nom' in headers:
                    name_idx = headers.index('Name') if 'Name' in headers else headers.index('Nom')
                    
                    for row in rows[1:]:
                        cells = [td.get_text(strip=True) for td in row.find_all('td')]
                        if len(cells) > name_idx:
                            char_name = cells[name_idx]
                            if char_name:
                                characters.append({
                                    'name': char_name,
                                    'url': f"https://eden-daoc.net/herald?n=player&k={char_name.split()[0]}",
                                    'raw_data': cells
                                })
        
        return characters
    
    def close(self):
        """Ferme le driver Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Driver Selenium fermé")
            except Exception as e:
                logging.warning(f"Erreur lors de la fermeture du driver: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Support du context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme automatiquement le driver à la sortie du context"""
        self.close()
        return False


def scrape_character_by_name(character_name, cookie_manager):
    """
    Fonction utilitaire pour scraper un personnage
    
    Args:
        character_name: Nom du personnage
        cookie_manager: Instance de CookieManager
        
    Returns:
        dict: Données du personnage ou None
    """
    with EdenScraper(cookie_manager) as scraper:
        return scraper.scrape_character(character_name)


def search_characters(query, realm=None, cookie_manager=None):
    """
    Fonction utilitaire pour rechercher des personnages
    
    Args:
        query: Terme de recherche
        realm: Realm optionnel ('alb', 'mid', 'hib')
        cookie_manager: Instance de CookieManager
        
    Returns:
        list: Liste des personnages trouvés
    """
    with EdenScraper(cookie_manager) as scraper:
        return scraper.scrape_search_results(query, realm)
