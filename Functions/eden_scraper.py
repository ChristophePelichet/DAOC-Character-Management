#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eden Scraper Manager - Gestion du scraping des données du Herald Eden-DAOC
Intégré depuis eden_scraper/ pour centraliser la gestion
"""

import logging
import pickle
import os
import traceback
from datetime import datetime
from pathlib import Path

# Import new logging system
from .logging_manager import get_logger, log_with_action, LOGGER_EDEN

# Logger au niveau du module pour les fonctions qui ne sont pas dans la classe
module_logger = get_logger(LOGGER_EDEN)

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
        self.logger = get_logger(LOGGER_EDEN)
        
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
                
                # Minimiser la fenêtre du navigateur si pas en mode headless
                if not headless:
                    try:
                        self.driver.minimize_window()
                        self.logger.info("🔽 Fenêtre du navigateur minimisée", extra={"action": "INIT"})
                    except Exception as e:
                        self.logger.warning(f"Impossible de minimiser la fenêtre: {e}", extra={"action": "INIT"})
                
                self.logger.info(f"✅ Driver Selenium initialisé: {browser_name}", extra={"action": "INIT"})
                return True
            else:
                self.logger.error("❌ Impossible d'initialiser un navigateur", extra={"action": "INIT"})
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l", extra={"action": "INIT"})
            return False
    
    def load_cookies(self):
        """
        Charge les cookies d'authentification dans le driver
        
        Returns:
            bool: True si les cookies ont été chargés et la session est active
        """
        if not self.driver:
            self.logger.error("❌ Driver non initialisé", extra={"action": "INIT"})
            return False
        
        try:
            cookies_list = self.cookie_manager.get_cookies_for_scraper()
            if not cookies_list:
                self.logger.error("❌ Aucun cookie disponible", extra={"action": "COOKIES"})
                return False
            
            # Étape 1: Naviguer vers le domaine racine
            self.logger.info("🌐 Étape 1: Navigation vers https://eden-daoc.net/", extra={"action": "COOKIES"})
            self.driver.get("https://eden-daoc.net/")
            
            # Attendre que la page soit chargée
            import time
            time.sleep(1)  # PHASE 1: Optimisé 2s → 1s
            
            # Étape 2: Ajouter les cookies
            self.logger.info(f"🍪 Étape 2: Ajout de {len(cookies_list)} cookies...", extra={"action": "COOKIES"})
            cookies_added = 0
            for cookie in cookies_list:
                try:
                    # Certains cookies peuvent avoir des attributs qui causent des problèmes
                    # On retire 'expiry' si elle est trop dans le passé
                    if 'expiry' in cookie:
                        import time as time_module
                        if cookie['expiry'] < time_module.time():
                            self.logger.debug(f"Cookie {cookie.get('name')} expiré, tentative d'ajout quand même", extra={"action": "COOKIES"})
                    
                    self.driver.add_cookie(cookie)
                    cookies_added += 1
                except Exception as e:
                    self.logger.warning(f"⚠️ Impossible d'ajouter le cookie {cookie.get('name')}: {e}", extra={"action": "COOKIES"})
            
            self.logger.info(f"✅ {cookies_added}/{len(cookies_list)} cookies chargés dans le driver", extra={"action": "COOKIES"})
            
            # Étape 3: Rafraîchir la page d'accueil (PHASE 1: sleep supprimé)
            self.logger.info("🔄 Rafraîchissement de la page d'accueil pour activer la session...", extra={"action": "COOKIES"})
            self.driver.refresh()
            time.sleep(2)  # PHASE 1: Optimisé 3s → 2s
            
            # Étape 4: Naviguer vers le Herald pour tester la session
            self.logger.info("🔍 Étape 4: Navigation vers le Herald (test de session)...", extra={"action": "COOKIES"})
            self.driver.get("https://eden-daoc.net/herald")
            time.sleep(2)  # PHASE 1: Optimisé 4s → 2s
            
            # Vérifier si on est connecté
            current_url = self.driver.current_url
            html_content = self.driver.page_source
            
            self.logger.debug(f"URL actuelle: {current_url}", extra={"action": "COOKIES"})
            
            # DEBUG: Sauvegarder le HTML pour inspection
            import os
            debug_file = os.path.join(os.path.dirname(__file__), '..', 'Scripts', 'debug_herald_page.html')
            try:
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.debug(f"HTML sauvegardé dans {debug_file}", extra={"action": "COOKIES"})
            except:
                pass
            
            # DÉTECTION SIMPLE ET FIABLE:
            # Si on a le message "not available" → Pas connecté
            # Sinon → Connecté (c'est la seule indication vraiment fiable)
            error_message = 'The requested page "herald" is not available.'
            has_error = error_message in html_content
            
            self.logger.debug(f"Message 'not available' présent: {has_error}", extra={"action": "COOKIES"})
            self.logger.debug(f"Taille HTML: {len(html_content)} caractères", extra={"action": "COOKIES"})
            
            if has_error:
                self.logger.error('❌ NON CONNECTÉ - Message détecté: "The requested page herald is not available."', extra={"action": "COOKIES"})
                self.logger.error("💡 Conseil: Régénérez vos cookies en utilisant le Cookie Manager (générateur ou import)", extra={"action": "COOKIES"})
                return False
            else:
                self.logger.info("✅ Connecté à Herald - Pas de message d'erreur", extra={"action": "COOKIES"})
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement des cookies: {e}", extra={"action": "COOKIES"})
            import traceback
            self.logger.debug(f"Traceback complet: {traceback.format_exc()}", extra={"action": "COOKIES"})
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
            self.logger.error("❌ Impossible de charger les cookies", extra={"action": "COOKIES"})
            return None
        
        try:
            # Construire l'URL du personnage
            url = f"https://eden-daoc.net/herald?n=player&k={character_name}"
            self.logger.info(f"Scraping du personnage: {character_name} ({url})", extra={"action": "SCRAPE"})
            
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
            
            self.logger.info(f"Données du personnage {character_name} extraites avec succès", extra={"action": "SCRAPE"})
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du scraping du personnage {character_name}: {e}", extra={"action": "SCRAPE"})
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
            self.logger.error("❌ Impossible de charger les cookies", extra={"action": "COOKIES"})
            return []
        
        try:
            # Construire l'URL de recherche
            url = f"https://eden-daoc.net/herald?n=search&s={search_query}"
            if realm:
                url += f"&r={realm}"
            
            self.logger.info(f"Recherche: {search_query} (realm: {realm or 'tous'})", extra={"action": "SEARCH"})
            
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
            
            self.logger.info(f"{len(characters)} personnages trouvés", extra={"action": "SEARCH"})
            return characters
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la recherche: {e}", extra={"action": "SEARCH"})
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
                        cells = row.find_all('td')
                        if len(cells) > name_idx:
                            # Extraire le nom et l'URL du lien
                            name_cell = cells[name_idx]
                            char_name = name_cell.get_text(strip=True)
                            
                            # Chercher le lien dans la cellule du nom
                            link = name_cell.find('a')
                            char_url = ""
                            if link and link.get('href'):
                                href = link.get('href')
                                # Construire l'URL complète si c'est un lien relatif
                                if href.startswith('?'):
                                    char_url = f"https://eden-daoc.net/herald{href}"
                                elif href.startswith('/'):
                                    char_url = f"https://eden-daoc.net{href}"
                                elif not href.startswith('http'):
                                    char_url = f"https://eden-daoc.net/herald?{href}"
                                else:
                                    char_url = href
                            
                            if char_name:
                                char_data = {
                                    'name': char_name,
                                    'url': char_url,
                                    'raw_data': [td.get_text(strip=True) for td in cells]
                                }
                                characters.append(char_data)
                                self.logger.debug(f"Personnage trouvé: {char_name} - URL: {char_url}", extra={"action": "PARSE"})
        
        return characters
    
    def close(self):
        """Ferme le driver Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Driver Selenium fermé", extra={"action": "CLOSE"})
            except Exception as e:
                self.logger.warning(f"Erreur lors de la fermeture du driver: {e}", extra={"action": "CLOSE"})
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
        module_logger.info(f"Début de la recherche Herald pour: {character_name}", extra={"action": "SEARCH"})
        
        # Vérifier les cookies
        cookie_manager = CookieManager()
        
        if not cookie_manager.cookie_exists():
            module_logger.error("Aucun cookie trouvé", extra={"action": "SEARCH"})
            return False, "Aucun cookie trouvé. Veuillez générer ou importer des cookies d'abord.", ""
        
        info = cookie_manager.get_cookie_info()
        if not info or not info.get('is_valid'):
            module_logger.error("Cookies expirés", extra={"action": "SEARCH"})
            return False, "Les cookies ont expiré. Veuillez les regénérer.", ""
        
        module_logger.info(f"Cookies valides - {info.get('cookie_count', 0)} cookies chargés", extra={"action": "SEARCH"})
        
        # Initialiser le scraper en mode visible (obligatoire - bot check)
        scraper = EdenScraper(cookie_manager)
        
        if not scraper.initialize_driver(headless=False):
            module_logger.error("Impossible d'initialiser le navigateur", extra={"action": "SEARCH"})
            try:
                scraper.close()
            except:
                pass
            return False, "Impossible d'initialiser le navigateur Chrome.", ""
        
        module_logger.info("Navigateur initialisé avec succès", extra={"action": "SEARCH"})
        
        if not scraper.load_cookies():
            scraper.close()
            module_logger.error("Impossible de charger les cookies dans le navigateur", extra={"action": "SEARCH"})
            return False, "Impossible de charger les cookies.", ""
        
        module_logger.info("Cookies chargés dans le navigateur - Authentification complétée", extra={"action": "SEARCH"})
        
        # Construire l'URL de recherche avec le filtre de royaume
        if realm_filter:
            search_url = f"https://eden-daoc.net/herald?n=search&r={realm_filter}&s={character_name}"
        else:
            search_url = f"https://eden-daoc.net/herald?n=search&s={character_name}"
        module_logger.info(f"Recherche Herald: {search_url}", extra={"action": "SEARCH"})
        
        # Naviguer vers la page de recherche
        scraper.driver.get(search_url)
        
        # Attendre que la page se charge complètement
        module_logger.info("Attente du chargement de la page de recherche (5 secondes)...", extra={"action": "SEARCH"})
        time.sleep(5)
        
        # Extraire le contenu HTML
        page_source = scraper.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        module_logger.info(f"Page chargée - Taille: {len(page_source)} caractères", extra={"action": "SEARCH"})
        
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
        
        module_logger.info(f"Dossier temporaire: {temp_dir}", extra={"action": "CLEANUP"})
        
        # Nettoyer les anciens fichiers avant de créer les nouveaux
        old_files_list = list(temp_dir.glob("*.json"))
        if old_files_list:
            module_logger.info(f"Nettoyage de {len(old_files_list)} fichier(s) ancien(s)...", extra={"action": "CLEANUP"})
            
            for old_file in old_files_list:
                try:
                    module_logger.debug(f"Suppression: {old_file.name}", extra={"action": "CLEANUP"})
                    old_file.unlink()
                    module_logger.info(f"✅ Fichier supprimé: {old_file.name}", extra={"action": "CLEANUP"})
                except Exception as e:
                    module_logger.warning(f"❌ Impossible de supprimer {old_file.name}: {e}", extra={"action": "CLEANUP"})
        else:
            module_logger.info("Aucun ancien fichier à nettoyer", extra={"action": "CLEANUP"})
        
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
                
                # Extraire l'URL depuis les liens (col_1 contient le nom avec le lien)
                url = ""
                if 'col_1_links' in result and result['col_1_links']:
                    href = result['col_1_links'][0]
                    # Construire l'URL complète
                    if href.startswith('?'):
                        url = f"https://eden-daoc.net/herald{href}"
                    elif href.startswith('/'):
                        url = f"https://eden-daoc.net{href}"
                    elif not href.startswith('http'):
                        url = f"https://eden-daoc.net/herald?{href}"
                    else:
                        url = href
                else:
                    # Fallback sur l'URL construite si pas de lien trouvé
                    clean_name = name.split()[0]
                    url = f"https://eden-daoc.net/herald?n=player&k={clean_name}"
                
                if name and char_class:
                    clean_name = name.split()[0]
                    
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
                    module_logger.debug(f"Personnage extrait: {name} - URL: {url}", extra={"action": "PARSE"})
        
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
        
        module_logger.info(f"Recherche terminée: {char_count} personnages trouvés", extra={"action": "SEARCH"})
        module_logger.info(f"Résultats sauvegardés dans: {characters_path}", extra={"action": "SEARCH"})
        module_logger.info(f"Recherche terminée: {char_count} personnages - Fichiers: {json_path}, {characters_path}", extra={"action": "SCRAPE"})
        
        return True, message, str(characters_path)
        
    except Exception as e:
        module_logger.error(f"❌ Erreur lors de la recherche Herald: {e}", extra={"action": "SEARCH"})
        module_logger.error(f"Stacktrace: {traceback.format_exc()}", extra={"action": "SEARCH"})
        try:
            scraper.close()
        except:
            pass
        return False, f"Erreur: {str(e)}", ""


def scrape_character_from_url(character_url, cookie_manager):
    """
    Récupère les données d'un personnage depuis son URL Herald
    Utilise la recherche Herald car l'accès direct à la page est bloqué (bot check)
    
    Args:
        character_url: URL du personnage sur Herald (contient le nom dans &k=)
        cookie_manager: Instance de CookieManager
        
    Returns:
        tuple: (success, data_dict, error_message)
    """
    try:
        # Extraire le nom du personnage depuis l'URL
        # Format: https://eden-daoc.net/herald?n=player&k=NomPersonnage
        from urllib.parse import urlparse, parse_qs
        
        parsed_url = urlparse(character_url)
        query_params = parse_qs(parsed_url.query)
        character_name = query_params.get('k', [''])[0]
        
        if not character_name:
            return False, None, "Impossible d'extraire le nom du personnage de l'URL"
        
        module_logger.info(f"Mise à jour du personnage: {character_name} depuis URL: {character_url}", extra={"action": "UPDATE"})
        
        # Utiliser search_herald_character qui fonctionne (pas de bot check sur la recherche)
        success, message, characters_file = search_herald_character(character_name)
        
        if not success:
            return False, None, message
        
        # Charger les résultats
        if not characters_file or not Path(characters_file).exists():
            return False, None, "Aucun fichier de résultats trouvé"
        
        with open(characters_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        characters = results.get('characters', [])
        
        if not characters:
            return False, None, f"Aucun personnage trouvé pour '{character_name}'"
        
        # Trouver le personnage exact (correspondance exacte du nom)
        target_char = None
        for char in characters:
            if char.get('clean_name', '').lower() == character_name.lower():
                target_char = char
                break
        
        # Si pas de correspondance exacte, prendre le premier
        if not target_char and characters:
            target_char = characters[0]
            module_logger.warning(f"Pas de correspondance exacte, utilisation du premier résultat: {target_char.get('name', 'Unknown')}", extra={"action": "SEARCH"})
        
        if not target_char:
            return False, None, "Personnage non trouvé dans les résultats"
        
        # Normaliser les données pour correspondre au format attendu
        normalized_data = _normalize_herald_data(target_char)
        
        module_logger.info(f"Données récupérées pour: {normalized_data.get('name', 'Unknown')}", extra={"action": "UPDATE"})
        return True, normalized_data, ""
        
    except Exception as e:
        module_logger.error(f"❌ Erreur lors de la récupération: {e}", extra={"action": "UPDATE"})
        return False, None, f"Erreur: {str(e)}"


def _normalize_herald_data(char_data):
    """
    Normalise les données Herald pour correspondre au format attendu par le dialogue
    
    Args:
        char_data: Données brutes depuis search_herald_character
        
    Returns:
        dict: Données normalisées
    """
    # Mapping des classes vers les royaumes
    class_to_realm = {
        # Albion
        'Armsman': 'Albion', 'Cabalist': 'Albion', 'Cleric': 'Albion',
        'Friar': 'Albion', 'Heretic': 'Albion', 'Infiltrator': 'Albion',
        'Mercenary': 'Albion', 'Minstrel': 'Albion', 'Necromancer': 'Albion',
        'Paladin': 'Albion', 'Reaver': 'Albion', 'Scout': 'Albion',
        'Sorcerer': 'Albion', 'Theurgist': 'Albion', 'Wizard': 'Albion',
        'Mauler': 'Albion',
        
        # Hibernia
        'Animist': 'Hibernia', 'Bainshee': 'Hibernia', 'Bard': 'Hibernia',
        'Blademaster': 'Hibernia', 'Champion': 'Hibernia', 'Druid': 'Hibernia',
        'Eldritch': 'Hibernia', 'Enchanter': 'Hibernia', 'Hero': 'Hibernia',
        'Mentalist': 'Hibernia', 'Nightshade': 'Hibernia', 'Ranger': 'Hibernia',
        'Valewalker': 'Hibernia', 'Vampiir': 'Hibernia', 'Warden': 'Hibernia',
        
        # Midgard
        'Berserker': 'Midgard', 'Bonedancer': 'Midgard', 'Healer': 'Midgard',
        'Hunter': 'Midgard', 'Runemaster': 'Midgard', 'Savage': 'Midgard',
        'Shadowblade': 'Midgard', 'Shaman': 'Midgard', 'Skald': 'Midgard',
        'Spiritmaster': 'Midgard', 'Thane': 'Midgard', 'Valkyrie': 'Midgard',
        'Warlock': 'Midgard', 'Warrior': 'Midgard'
    }
    
    # Extraire la classe et déterminer le royaume
    char_class = char_data.get('class', '')
    realm = class_to_realm.get(char_class, 'Unknown')
    
    # Normaliser realm_points (enlever espaces et virgules)
    realm_points = char_data.get('realm_points', '0')
    if isinstance(realm_points, str):
        realm_points = realm_points.replace(' ', '').replace(',', '')
        try:
            realm_points = int(realm_points)
        except:
            realm_points = 0
    
    # Convertir level en int si c'est une string
    level = char_data.get('level', '1')
    if isinstance(level, str):
        try:
            level = int(level)
        except:
            level = 1
    
    # Données normalisées
    # ATTENTION : Dans le JSON Herald :
    #   - realm_rank = titre texte (ex: "Stormur Vakten")  
    #   - realm_level = code (ex: "5L2")
    # Dans notre programme :
    #   - realm_rank = code (ex: "5L2")
    #   - realm_title = titre texte (ex: "Stormur Vakten")
    # Il faut donc INVERSER les champs !
    
    normalized = {
        'name': char_data.get('name', ''),
        'clean_name': char_data.get('clean_name', ''),
        'level': level,
        'class': char_class,
        'race': char_data.get('race', ''),
        'realm': realm,
        'guild': char_data.get('guild', ''),
        'realm_points': realm_points,
        'realm_rank': char_data.get('realm_level', '1L1'),  # Code (XLY) - INVERSÉ!
        'realm_title': char_data.get('realm_rank', ''),  # Titre texte
        'server': 'Eden',  # Toujours Eden pour ce Herald
        'url': char_data.get('url', ''),
        'rank': char_data.get('rank', '')
    }
    
    module_logger.debug(f"Données normalisées: {normalized}", extra={"action": "SCRAPE"})
    return normalized


def _parse_character_herald_data(raw_data):
    """
    Parse les données brutes du Herald pour extraire les informations du personnage
    
    Args:
        raw_data: Données brutes extraites de la page Herald
        
    Returns:
        dict: Données structurées du personnage
    """
    parsed = {}
    
    try:
        # Extraire le nom depuis le titre ou h1
        if 'h1' in raw_data and raw_data['h1']:
            parsed['name'] = raw_data['h1'][0]
        elif 'title' in raw_data:
            # Extraire le nom depuis le titre
            title_parts = raw_data['title'].split('-')
            if title_parts:
                parsed['name'] = title_parts[0].strip()
        
        # Parcourir les tableaux pour extraire les informations
        for table in raw_data.get('tables', []):
            for row in table:
                if len(row) >= 2:
                    key = row[0].lower().strip()
                    value = row[1].strip()
                    
                    # Niveau
                    if 'level' in key or 'niveau' in key:
                        try:
                            parsed['level'] = int(value)
                        except:
                            pass
                    
                    # Classe
                    elif 'class' in key or 'classe' in key:
                        parsed['class'] = value
                    
                    # Race
                    elif 'race' in key:
                        parsed['race'] = value
                    
                    # Royaume
                    elif 'realm' in key or 'royaume' in key:
                        parsed['realm'] = value
                    
                    # Guilde
                    elif 'guild' in key or 'guilde' in key:
                        parsed['guild'] = value
                    
                    # Realm Points
                    elif 'realm point' in key or 'points de royaume' in key:
                        try:
                            # Nettoyer les virgules/espaces
                            clean_value = value.replace(',', '').replace(' ', '')
                            parsed['realm_points'] = int(clean_value)
                        except:
                            pass
                    
                    # Server
                    elif 'server' in key or 'serveur' in key:
                        parsed['server'] = value
        
        return parsed if parsed else None
        
    except Exception as e:
        module_logger.error(f"❌ Erreur lors du parsing des données: {e}", extra={"action": "SCRAPE"})
        return None


