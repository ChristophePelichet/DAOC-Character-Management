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

# Logger dédié pour Eden
eden_logger = logging.getLogger('eden')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
        Initialise le driver Selenium avec fallback multi-navigateurs
        Supporte Chrome, Edge et Firefox
        Utilise le navigateur configuré dans les paramètres
        
        Args:
            headless: Si True, lance le navigateur en mode sans interface
            
        Returns:
            bool: True si l'initialisation a réussi
        """
        try:
            # Lire la configuration pour le navigateur préféré
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            allow_download = config.get('allow_browser_download', False)
            
            # Utiliser la fonction helper du cookie_manager
            # (qui gère le fallback Chrome → Edge → Firefox)
            driver, browser_name = self.cookie_manager._initialize_browser_driver(
                headless=headless,
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if driver:
                self.driver = driver
                eden_logger.info(f"✅ Driver Selenium initialisé: {browser_name}")
                return True
            else:
                eden_logger.error("❌ Impossible d'initialiser un navigateur")
                return False
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de l'initialisation du driver: {e}")
            return False
    
    def load_cookies(self):
        """
        Charge les cookies d'authentification dans le driver
        
        Returns:
            bool: True si les cookies ont été chargés
        """
        if not self.driver:
            eden_logger.error("Driver non initialisé")
            return False
        
        try:
            cookies_list = self.cookie_manager.get_cookies_for_scraper()
            if not cookies_list:
                eden_logger.error("Aucun cookie disponible")
                return False
            
            # Aller sur le domaine pour pouvoir ajouter les cookies
            self.driver.get("https://eden-daoc.net/")
            
            # Attendre que la page soit chargée
            import time
            time.sleep(2)
            
            # Ajouter chaque cookie
            for cookie in cookies_list:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    eden_logger.warning(f"Impossible d'ajouter le cookie {cookie.get('name')}: {e}")
            
            eden_logger.info(f"{len(cookies_list)} cookies chargés dans le driver")
            
            # Attendre un peu après avoir ajouté les cookies
            time.sleep(1)
            return True
            
        except Exception as e:
            eden_logger.error(f"Erreur lors du chargement des cookies: {e}")
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
            eden_logger.error("Impossible de charger les cookies")
            return None
        
        try:
            # Construire l'URL du personnage
            url = f"https://eden-daoc.net/herald?n=player&k={character_name}"
            eden_logger.info(f"Scraping du personnage: {character_name} ({url})")
            
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
            
            eden_logger.info(f"Données du personnage {character_name} extraites avec succès")
            return data
            
        except Exception as e:
            eden_logger.error(f"Erreur lors du scraping du personnage {character_name}: {e}")
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
            eden_logger.error("Impossible de charger les cookies")
            return []
        
        try:
            # Construire l'URL de recherche
            url = f"https://eden-daoc.net/herald?n=search&s={search_query}"
            if realm:
                url += f"&r={realm}"
            
            eden_logger.info(f"Recherche: {search_query} (realm: {realm or 'tous'})")
            
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
            
            eden_logger.info(f"{len(characters)} personnages trouvés")
            return characters
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de la recherche: {e}")
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
                eden_logger.info("Driver Selenium fermé")
            except Exception as e:
                eden_logger.warning(f"Erreur lors de la fermeture du driver: {e}")
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


def search_herald_character(character_name, realm_filter=""):
    """
    Recherche un personnage sur le Herald Eden et sauvegarde les résultats en JSON
    
    Args:
        character_name: Nom du personnage à rechercher
        realm_filter: Filtre de royaume ("alb", "mid", "hib", ou "" pour tous)
        
    Returns:
        tuple: (success: bool, message: str, json_path: str)
    """
    from Functions.cookie_manager import CookieManager
    from Functions.config_manager import get_config_dir
    import time
    
    try:
        # Vérifier les cookies
        cookie_manager = CookieManager()
        
        if not cookie_manager.cookie_exists():
            return False, "Aucun cookie trouvé. Veuillez générer ou importer des cookies d'abord.", ""
        
        info = cookie_manager.get_cookie_info()
        if not info or not info.get('is_valid'):
            return False, "Les cookies ont expiré. Veuillez les regénérer.", ""
        
        # Initialiser le scraper en mode visible (obligatoire - bot check)
        scraper = EdenScraper(cookie_manager)
        
        if not scraper.initialize_driver(headless=False):
            return False, "Impossible d'initialiser le navigateur Chrome.", ""
        
        if not scraper.load_cookies():
            scraper.close()
            return False, "Impossible de charger les cookies.", ""
        
        # Construire l'URL de recherche avec le filtre de royaume
        if realm_filter:
            search_url = f"https://eden-daoc.net/herald?n=search&r={realm_filter}&s={character_name}"
        else:
            search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
        eden_logger.info(f"Recherche Herald: {search_url}")
        
        # Naviguer vers la page de recherche
        scraper.driver.get(search_url)
        
        # Attendre que la page se charge complètement
        time.sleep(5)
        
        # Extraire le contenu HTML
        page_source = scraper.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extraire les données de recherche
        search_data = {
            'character_name': character_name,
            'search_url': search_url,
            'timestamp': datetime.now().isoformat(),
            'results': []
        }
        
        # Chercher les résultats dans les tableaux
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:  # Au moins un header et une ligne
                headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
                
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if cells:
                        result = {}
                        for idx, cell in enumerate(cells):
                            header = headers[idx] if idx < len(headers) else f"col_{idx}"
                            result[header] = cell.get_text(strip=True)
                            
                            # Extraire les liens
                            links = cell.find_all('a')
                            if links:
                                result[f"{header}_links"] = [a.get('href', '') for a in links]
                        
                        if result:
                            search_data['results'].append(result)
        
        # Utiliser le dossier temporaire de l'OS
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "EdenSearchResult"
        temp_dir.mkdir(exist_ok=True)
        
        # Nettoyer les anciens fichiers avant de créer les nouveaux
        for old_file in temp_dir.glob("*.json"):
            try:
                old_file.unlink()
            except Exception as e:
                eden_logger.warning(f"Impossible de supprimer l'ancien fichier {old_file}: {e}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"search_{character_name}_{timestamp}.json"
        json_path = temp_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, indent=2, ensure_ascii=False)
        
        # Extraire les personnages formatés
        characters = []
        for result in search_data['results']:
            # Vérifier si c'est une ligne de personnage
            if (result.get('col_1') and 
                result.get('col_3') and 
                len(result.get('col_1', '')) > 0 and
                result.get('col_0') and
                result.get('col_0', '').isdigit()):
                
                rank = result.get('col_0', '')
                name = result.get('col_1', '').strip()
                char_class = result.get('col_3', '').strip()
                race = result.get('col_5', '').strip()
                guild = result.get('col_7', '').strip()
                level = result.get('col_8', '').strip()
                rp = result.get('col_9', '').strip()
                realm_rank = result.get('col_10', '').strip()
                realm_level = result.get('col_11', '').strip()
                
                if name and char_class:
                    clean_name = name.split()[0]
                    url = f"https://eden-daoc.net/herald?n=player&k={clean_name}"
                    
                    characters.append({
                        'rank': rank,
                        'name': name,
                        'clean_name': clean_name,
                        'class': char_class,
                        'race': race,
                        'guild': guild,
                        'level': level,
                        'realm_points': rp,
                        'realm_rank': realm_rank,
                        'realm_level': realm_level,
                        'url': url
                    })
        
        # Sauvegarder les personnages formatés dans le même dossier temp
        characters_filename = f"characters_{character_name}_{timestamp}.json"
        characters_path = temp_dir / characters_filename
        
        with open(characters_path, 'w', encoding='utf-8') as f:
            json.dump({
                'search_query': character_name,
                'search_url': search_url,
                'timestamp': search_data['timestamp'],
                'characters': characters
            }, f, indent=2, ensure_ascii=False)
        
        scraper.close()
        
        char_count = len(characters)
        message = f"{char_count} personnage(s) trouvé(s)"
        
        eden_logger.info(f"Recherche terminée: {char_count} personnages - Fichiers: {json_path}, {characters_path}")
        
        return True, message, str(characters_path)
        
    except Exception as e:
        eden_logger.error(f"Erreur lors de la recherche Herald: {e}", exc_info=True)
        return False, f"Erreur: {str(e)}", ""

