#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cookie Manager - Gestionnaire de cookies Eden pour le scraping
Gère l'importation, la validation et la sauvegarde des cookies
"""

import pickle
import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

class CookieManager:
    """Gestionnaire de cookies pour l'authentification Eden"""
    
    def __init__(self, config_dir=None):
        """
        Initialise le gestionnaire de cookies
        
        Args:
            config_dir: Dossier de configuration (par défaut: Configuration/)
        """
        if config_dir is None:
            # Utiliser le dossier Configuration du projet
            base_dir = Path(__file__).parent.parent
            config_dir = base_dir / "Configuration"
        else:
            config_dir = Path(config_dir)
        
        self.config_dir = config_dir
        self.cookie_file = self.config_dir / "eden_cookies.pkl"
        
        # Créer le dossier si nécessaire
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"CookieManager initialisé - Fichier: {self.cookie_file}")
    
    def cookie_exists(self):
        """Vérifie si un fichier de cookies existe"""
        return self.cookie_file.exists()
    
    def get_cookie_info(self):
        """
        Récupère les informations sur les cookies sauvegardés
        
        Returns:
            dict: Informations sur les cookies ou None si inexistant
        """
        if not self.cookie_exists():
            return None
        
        try:
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
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
                        valid_cookies.append({
                            'name': cookie_name,
                            'domain': cookie_domain,
                            'expires_at': expiry_date,
                            'days_remaining': duration.days,
                            'hours_remaining': duration.seconds // 3600
                        })
                    else:
                        # Cookie expiré
                        expired_cookies.append({
                            'name': cookie_name,
                            'domain': cookie_domain,
                            'expired_at': expiry_date
                        })
                else:
                    # Cookie de session
                    session_cookies.append({
                        'name': cookie_name,
                        'domain': cookie_domain
                    })
            
            # Calculer la date d'expiration la plus proche
            expiry_date = None
            if valid_cookies:
                min_cookie = min(valid_cookies, key=lambda x: x['days_remaining'])
                expiry_date = min_cookie['expires_at']
            
            return {
                'exists': True,
                'file_path': str(self.cookie_file),
                'total_cookies': len(cookies),
                'valid_cookies': len(valid_cookies),
                'expired_cookies': len(expired_cookies),
                'session_cookies': len(session_cookies),
                'is_valid': len(expired_cookies) == 0 and len(valid_cookies) > 0,
                'expiry_date': expiry_date,
                'details': {
                    'valid': valid_cookies,
                    'expired': expired_cookies,
                    'session': session_cookies
                }
            }
            
        except Exception as e:
            logging.error(f"Erreur lors de la lecture des cookies: {e}")
            return {
                'exists': True,
                'error': str(e),
                'is_valid': False
            }
    
    def import_cookie_file(self, source_file):
        """
        Importe un fichier de cookies depuis un emplacement externe
        
        Args:
            source_file: Chemin du fichier de cookies à importer
        
        Returns:
            bool: True si l'importation a réussi
        """
        source_path = Path(source_file)
        
        logging.info(f"Tentative d'import du fichier: {source_file}")
        logging.info(f"Chemin absolu: {source_path.absolute()}")
        logging.info(f"Le fichier existe: {source_path.exists()}")
        
        if not source_path.exists():
            logging.error(f"Fichier source introuvable: {source_file}")
            logging.error(f"Chemin absolu testé: {source_path.absolute()}")
            return False
        
        try:
            # Vérifier que c'est un fichier pickle valide
            logging.info(f"Lecture du fichier pickle...")
            with open(source_path, 'rb') as f:
                cookies = pickle.load(f)
            
            logging.info(f"Fichier chargé, type: {type(cookies)}")
            
            if not isinstance(cookies, list):
                logging.error("Format de fichier invalide: doit contenir une liste de cookies")
                return False
            
            logging.info(f"Nombre de cookies dans le fichier: {len(cookies)}")
            # Sauvegarder l'ancien fichier si existant
            if self.cookie_file.exists():
                backup_file = self.cookie_file.with_suffix('.pkl.backup')
                shutil.copy2(self.cookie_file, backup_file)
                logging.info(f"Ancien fichier sauvegardé: {backup_file}")
            
            # Copier le nouveau fichier
            shutil.copy2(source_path, self.cookie_file)
            logging.info(f"Cookies importés: {len(cookies)} cookies")
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de l'importation: {e}")
            return False
    
    def delete_cookies(self):
        """
        Supprime le fichier de cookies
        
        Returns:
            bool: True si la suppression a réussi
        """
        if not self.cookie_file.exists():
            logging.warning("Aucun fichier de cookies à supprimer")
            return True
        
        try:
            # Créer une sauvegarde avant suppression
            backup_file = self.cookie_file.with_suffix('.pkl.deleted')
            shutil.copy2(self.cookie_file, backup_file)
            
            # Supprimer le fichier
            self.cookie_file.unlink()
            logging.info("Fichier de cookies supprimé")
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de la suppression: {e}")
            return False
    
    def generate_cookies_with_browser(self):
        """
        Ouvre un navigateur pour authentification et génère les cookies
        
        Returns:
            tuple: (success: bool, message: str, cookies: list ou None)
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            logging.info("Ouverture du navigateur pour authentification Eden")
            
            # Créer le driver Chrome
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
            try:
                # URL de connexion Discord OAuth pour Eden
                discord_login_url = "https://eden-daoc.net/ucp.php?mode=login&redirect=forum.php%2Fforum&login=external&oauth_service=studio_discord"
                driver.get(discord_login_url)
                
                logging.info("Navigateur ouvert - En attente de l'authentification")
                
                # Retourner le driver pour que l'interface puisse attendre
                return (True, "browser_opened", driver)
                
            except Exception as e:
                driver.quit()
                error_msg = f"Erreur lors de l'ouverture du navigateur: {e}"
                logging.error(error_msg)
                return (False, error_msg, None)
                
        except ImportError as e:
            error_msg = "Selenium n'est pas installé. Installez-le avec: pip install selenium webdriver-manager"
            logging.error(error_msg)
            return (False, error_msg, None)
        except Exception as e:
            error_msg = f"Erreur lors de l'initialisation: {e}"
            logging.error(error_msg)
            return (False, error_msg, None)
    
    def save_cookies_from_driver(self, driver):
        """
        Récupère et sauvegarde les cookies depuis un driver Selenium
        
        Args:
            driver: Instance du WebDriver Selenium
            
        Returns:
            tuple: (success: bool, message: str, cookie_count: int)
        """
        try:
            # Récupérer tous les cookies
            cookies = driver.get_cookies()
            
            if not cookies:
                return (False, "Aucun cookie récupéré", 0)
            
            # Sauvegarder l'ancien fichier si existant
            if self.cookie_file.exists():
                backup_file = self.cookie_file.with_suffix('.pkl.backup')
                shutil.copy2(self.cookie_file, backup_file)
                logging.info(f"Ancien fichier sauvegardé: {backup_file}")
            
            # Sauvegarder les nouveaux cookies
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            logging.info(f"{len(cookies)} cookies sauvegardés dans {self.cookie_file}")
            
            return (True, f"{len(cookies)} cookies sauvegardés avec succès", len(cookies))
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde des cookies: {e}"
            logging.error(error_msg)
            return (False, error_msg, 0)
    
    def get_cookies_for_scraper(self):
        """
        Récupère les cookies pour utilisation avec le scraper
        
        Returns:
            list: Liste des cookies ou None si inexistant/invalide
        """
        if not self.cookie_exists():
            return None
        
        info = self.get_cookie_info()
        if not info or not info.get('is_valid'):
            return None
        
        try:
            with open(self.cookie_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logging.error(f"Erreur lors de la lecture des cookies: {e}")
            return None
    
    def test_eden_connection(self):
        """
        Teste la connexion au site Eden avec les cookies actuels
        Note: Utilise Selenium car les cookies ne fonctionnent pas avec requests
        
        Returns:
            dict: {
                'success': bool,
                'status_code': int ou None,
                'message': str,
                'accessible': bool
            }
        """
        if not self.cookie_exists():
            return {
                'success': False,
                'status_code': None,
                'message': 'Aucun cookie trouvé',
                'accessible': False
            }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Charger les cookies
            cookies_list = self.get_cookies_for_scraper()
            if not cookies_list:
                return {
                    'success': False,
                    'status_code': None,
                    'message': 'Cookies invalides ou expirés',
                    'accessible': False
                }
            
            # Configurer Chrome en mode headless (sans interface)
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--log-level=3')  # Réduire les logs
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Aller sur la page d'accueil pour pouvoir ajouter les cookies
                driver.get("https://eden-daoc.net/")
                
                # Ajouter les cookies
                for cookie in cookies_list:
                    driver.add_cookie(cookie)
                
                # Attendre un peu pour que les cookies soient pris en compte
                import time
                time.sleep(2)
                
                # Tester l'accès au Herald avec une page spécifique
                test_url = 'https://eden-daoc.net/herald?n=top_players&r=hib'
                logging.info(f"Test de connexion à {test_url}")
                
                driver.get(test_url)
                
                # Attendre que la page se charge
                time.sleep(2)
                
                current_url = driver.current_url
                
                logging.info(f"URL finale: {current_url}")
                
                # Vérifier si on est redirigé vers la page de login
                if 'login' in current_url.lower() or 'ucp.php?mode=login' in current_url:
                    return {
                        'success': True,
                        'status_code': 200,
                        'message': 'Redirigé vers la page de connexion',
                        'accessible': False
                    }
                
                # Vérifier le contenu de la page
                page_source = driver.page_source.lower()
                
                # Log pour debug
                has_login_form = 'mode=login' in page_source
                has_connexion_text = 'connexion' in page_source and 'mot de passe' in page_source
                has_herald_content = 'herald' in page_source or 'top players' in page_source or 'player' in page_source
                
                logging.info(f"Analyse de la page - mode=login: {has_login_form}, formulaire connexion: {has_connexion_text}, contenu herald: {has_herald_content}")
                
                # Si on détecte un formulaire de connexion ET pas de contenu Herald, c'est qu'on n'est pas connecté
                if (has_login_form or has_connexion_text) and not has_herald_content:
                    return {
                        'success': True,
                        'status_code': 200,
                        'message': 'Page de connexion détectée',
                        'accessible': False
                    }
                
                # Si on arrive ici, on est probablement connecté
                return {
                    'success': True,
                    'status_code': 200,
                    'message': 'Accès autorisé',
                    'accessible': True
                }
                    
            finally:
                driver.quit()
                
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else "inconnu"
            return {
                'success': False,
                'status_code': None,
                'message': f'Module {missing_module} non installé',
                'accessible': False
            }
        except Exception as e:
            logging.error(f"Erreur lors du test de connexion: {e}")
            return {
                'success': False,
                'status_code': None,
                'message': f'Erreur: {str(e)[:50]}',
                'accessible': False
            }
