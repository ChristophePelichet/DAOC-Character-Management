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

# Import new logging system
from .logging_manager import get_logger, LOGGER_EDEN

# Logger dédié pour Eden
eden_logger = get_logger(LOGGER_EDEN)

class CookieManager:
    """Gestionnaire de cookies pour l'authentification Eden"""
    
    def __init__(self, config_dir=None):
        """
        Initialise le gestionnaire de cookies
        
        Args:
            config_dir: Dossier de configuration (par défaut: Configuration/)
        """
        if config_dir is None:
            # Utiliser le dossier des cookies depuis la configuration
            from Functions.config_manager import config, get_config_dir
            # Vérifier si un dossier de cookies a été configuré
            config_dir = config.get("cookies_folder")
            if not config_dir:
                # Fallback sur le dossier de configuration par défaut
                config_dir = get_config_dir()
        
        config_dir = Path(config_dir)
        self.config_dir = config_dir
        self.cookie_file = self.config_dir / "eden_cookies.pkl"
        
        # Créer le dossier si nécessaire
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        eden_logger.info(f"CookieManager initialisé - Fichier: {self.cookie_file}")
    
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
            eden_logger.error(f"Erreur lors de la lecture des cookies: {e}")
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
        
        eden_logger.info(f"Tentative d'import du fichier: {source_file}")
        eden_logger.info(f"Chemin absolu: {source_path.absolute()}")
        eden_logger.info(f"Le fichier existe: {source_path.exists()}")
        
        if not source_path.exists():
            eden_logger.error(f"Fichier source introuvable: {source_file}")
            eden_logger.error(f"Chemin absolu testé: {source_path.absolute()}")
            return False
        
        try:
            # Vérifier que c'est un fichier pickle valide
            eden_logger.info(f"Lecture du fichier pickle...")
            with open(source_path, 'rb') as f:
                cookies = pickle.load(f)
            
            eden_logger.info(f"Fichier chargé, type: {type(cookies)}")
            
            if not isinstance(cookies, list):
                eden_logger.error("Format de fichier invalide: doit contenir une liste de cookies")
                return False
            
            eden_logger.info(f"Nombre de cookies dans le fichier: {len(cookies)}")
            # Sauvegarder l'ancien fichier si existant
            if self.cookie_file.exists():
                backup_file = self.cookie_file.with_suffix('.pkl.backup')
                shutil.copy2(self.cookie_file, backup_file)
                eden_logger.info(f"Ancien fichier sauvegardé: {backup_file}")
            
            # Copier le nouveau fichier
            shutil.copy2(source_path, self.cookie_file)
            eden_logger.info(f"Cookies importés: {len(cookies)} cookies")
            
            return True
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de l'importation: {e}")
            return False
    
    def delete_cookies(self):
        """
        Supprime le fichier de cookies
        
        Returns:
            bool: True si la suppression a réussi
        """
        if not self.cookie_file.exists():
            eden_logger.warning("Aucun fichier de cookies à supprimer")
            return True
        
        try:
            # Créer une sauvegarde avant suppression
            backup_file = self.cookie_file.with_suffix('.pkl.deleted')
            shutil.copy2(self.cookie_file, backup_file)
            
            # Supprimer le fichier
            self.cookie_file.unlink()
            eden_logger.info("Fichier de cookies supprimé")
            
            return True
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de la suppression: {e}")
            return False
    
    def detect_available_browsers(self):
        """
        Détecte les navigateurs installés sur le système (sans les ouvrir)
        Vérifie juste la présence des exécutables
        
        Returns:
            list: Liste des navigateurs disponibles ['Chrome', 'Edge', 'Firefox']
        """
        import os
        import shutil
        import platform
        
        available = []
        
        # Vérifier Chrome
        chrome_paths = []
        if platform.system() == "Windows":
            chrome_paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
        elif platform.system() == "Darwin":  # macOS
            chrome_paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        else:  # Linux
            chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]
        
        # Vérifier si chromedriver local existe
        local_chromedriver = os.path.join(os.getcwd(), "chromedriver.exe")
        if os.path.exists(local_chromedriver):
            available.append('Chrome')
        else:
            # Vérifier si Chrome est installé
            for path in chrome_paths:
                if os.path.exists(path):
                    available.append('Chrome')
                    break
        
        # Vérifier Edge (préinstallé sur Windows 10/11)
        if platform.system() == "Windows":
            edge_paths = [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            ]
            for path in edge_paths:
                if os.path.exists(path):
                    available.append('Edge')
                    break
        
        # Vérifier Firefox
        firefox_paths = []
        if platform.system() == "Windows":
            firefox_paths = [
                os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
            ]
        elif platform.system() == "Darwin":  # macOS
            firefox_paths = ["/Applications/Firefox.app/Contents/MacOS/firefox"]
        else:  # Linux
            firefox_paths = ["/usr/bin/firefox"]
        
        for path in firefox_paths:
            if os.path.exists(path):
                available.append('Firefox')
                break
        
        return available
    
    def _initialize_browser_driver(self, headless=False, preferred_browser=None, allow_download=True):
        """
        Initialise un driver Selenium avec support du navigateur préféré
        
        Args:
            headless: Si True, lance le navigateur en mode invisible
            preferred_browser: 'Chrome', 'Edge' ou 'Firefox' (None = auto)
            allow_download: Si False, ne télécharge pas de driver automatiquement
            
        Returns:
            tuple: (driver, browser_name) ou (None, None) si échec
        """
        from selenium import webdriver
        import os
        
        # Log pour debug
        eden_logger.info(f"🔍 _initialize_browser_driver appelé avec: preferred_browser={preferred_browser}, headless={headless}, allow_download={allow_download}")
        
        # Définir l'ordre de priorité
        if preferred_browser:
            browser_order = [preferred_browser]
            # Ajouter les autres comme fallback
            all_browsers = ['Chrome', 'Edge', 'Firefox']
            for browser in all_browsers:
                if browser != preferred_browser:
                    browser_order.append(browser)
            eden_logger.info(f"📋 Ordre de priorité (avec préféré): {browser_order}")
        else:
            # Ordre par défaut
            browser_order = ['Chrome', 'Edge', 'Firefox']
            eden_logger.info(f"📋 Ordre de priorité (par défaut): {browser_order}")
        
        errors = []
        
        for browser_name in browser_order:
            if browser_name == 'Chrome':
                driver = self._try_chrome(headless, allow_download, errors)
                if driver:
                    return driver, 'Chrome'
            
            elif browser_name == 'Edge':
                driver = self._try_edge(headless, errors)
                if driver:
                    return driver, 'Edge'
            
            elif browser_name == 'Firefox':
                driver = self._try_firefox(headless, errors)
                if driver:
                    return driver, 'Firefox'
        
        # ===== ÉCHEC TOTAL =====
        error_summary = "\n".join(errors)
        eden_logger.error(f"❌ Impossible d'initialiser un navigateur:\n{error_summary}")
        return None, None
    
    def _try_chrome(self, headless, allow_download, errors):
        """Tente d'initialiser Chrome"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service as ChromeService
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            import os
            
            chrome_options = ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--log-level=3')
            
            # Chrome local
            try:
                local_chromedriver = os.path.join(os.getcwd(), "chromedriver.exe")
                if os.path.exists(local_chromedriver):
                    driver = webdriver.Chrome(service=ChromeService(local_chromedriver), options=chrome_options)
                    eden_logger.info("✅ Chrome (driver local)")
                    return driver
            except Exception as e:
                eden_logger.debug(f"ChromeDriver local: {e}")
            
            # Chrome système (Selenium Manager)
            try:
                driver = webdriver.Chrome(options=chrome_options)
                eden_logger.info("✅ Chrome (Selenium Manager)")
                return driver
            except Exception as e:
                eden_logger.debug(f"Chrome système: {e}")
            
            # Chrome téléchargement (seulement si autorisé)
            if allow_download:
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    eden_logger.info("🌐 Téléchargement ChromeDriver...")
                    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                    eden_logger.info("✅ Chrome (téléchargé)")
                    return driver
                except Exception as e:
                    errors.append(f"Chrome téléchargement: {e}")
                    eden_logger.debug(f"Chrome téléchargement: {e}")
            else:
                eden_logger.debug("Chrome: Téléchargement non autorisé")
        
        except Exception as e:
            errors.append(f"Chrome: {e}")
            eden_logger.debug(f"Chrome non disponible: {e}")
        
        return None
    
    def _try_edge(self, headless, errors):
        """Tente d'initialiser Edge"""
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options as EdgeOptions
            
            edge_options = EdgeOptions()
            if headless:
                edge_options.add_argument('--headless=new')
                edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--log-level=3')
            
            driver = webdriver.Edge(options=edge_options)
            eden_logger.info("✅ Edge (Selenium Manager)")
            return driver
        
        except Exception as e:
            errors.append(f"Edge: {e}")
            eden_logger.debug(f"Edge: {e}")
        
        return None
    
    def _try_firefox(self, headless, errors):
        """Tente d'initialiser Firefox"""
        try:
            from selenium import webdriver
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            
            firefox_options = FirefoxOptions()
            if headless:
                firefox_options.add_argument('--headless')
            
            driver = webdriver.Firefox(options=firefox_options)
            eden_logger.info("✅ Firefox (Selenium Manager)")
            return driver
        
        except Exception as e:
            errors.append(f"Firefox: {e}")
            eden_logger.debug(f"Firefox: {e}")
        
        return None
        return None, None
    
    def generate_cookies_with_browser(self, preferred_browser=None, allow_download=False):
        """
        Ouvre un navigateur pour authentification et génère les cookies
        Supporte Chrome, Edge et Firefox avec fallback automatique
        
        Args:
            preferred_browser: 'Chrome', 'Edge' ou 'Firefox' (None = auto)
            allow_download: Si True, autorise le téléchargement de drivers
        
        Returns:
            tuple: (success: bool, message: str, driver ou None)
        """
        try:
            eden_logger.info("🌐 Ouverture du navigateur pour authentification Eden")
            
            # Initialiser le driver avec fallback multi-navigateurs
            driver, browser_name = self._initialize_browser_driver(
                headless=False,
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if driver is None:
                error_msg = (
                    "Impossible d'initialiser un navigateur.\n\n"
                    "Navigateurs testés: Chrome, Edge, Firefox\n\n"
                    "Solutions possibles:\n"
                    "1. Installez Chrome, Edge ou Firefox\n"
                    "2. Sur Windows, Edge devrait être préinstallé\n"
                    "3. Vérifiez les logs pour plus de détails"
                )
                if not allow_download:
                    error_msg += "\n\nNote: Le téléchargement automatique de drivers est désactivé."
                eden_logger.error(error_msg)
                return (False, error_msg, None)
            
            eden_logger.info(f"✅ Navigateur initialisé: {browser_name}")
            
            # Stocker le navigateur utilisé pour affichage
            self.last_browser_used = browser_name
            
            try:
                # URL de connexion Discord OAuth pour Eden
                discord_login_url = "https://eden-daoc.net/ucp.php?mode=login&redirect=forum.php%2Fforum&login=external&oauth_service=studio_discord"
                driver.get(discord_login_url)
                
                eden_logger.info("Navigateur ouvert - En attente de l'authentification")
                
                # Retourner le driver pour que l'interface puisse attendre
                return (True, "browser_opened", driver)
                
            except Exception as e:
                driver.quit()
                error_msg = f"Erreur lors de l'ouverture du navigateur: {e}"
                eden_logger.error(error_msg)
                return (False, error_msg, None)
                
        except ImportError as e:
            error_msg = "Selenium n'est pas installé. Installez-le avec: pip install selenium webdriver-manager"
            eden_logger.error(error_msg)
            return (False, error_msg, None)
        except Exception as e:
            error_msg = f"Erreur lors de l'initialisation: {e}"
            eden_logger.error(error_msg)
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
                eden_logger.info(f"Ancien fichier sauvegardé: {backup_file}")
            
            # Sauvegarder les nouveaux cookies
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            eden_logger.info(f"{len(cookies)} cookies sauvegardés dans {self.cookie_file}")
            
            return (True, f"{len(cookies)} cookies sauvegardés avec succès", len(cookies))
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde des cookies: {e}"
            eden_logger.error(error_msg)
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
            eden_logger.error(f"Erreur lors de la lecture des cookies: {e}")
            return None
    
    def test_eden_connection(self):
        """
        Teste la connexion au site Eden avec les cookies actuels
        Note: Utilise Selenium car les cookies ne fonctionnent pas avec requests
        Utilise le navigateur configuré dans les paramètres
        
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
            
            # Lire la configuration pour le navigateur préféré
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            allow_download = config.get('allow_browser_download', False)
            
            eden_logger.info(f"🔧 test_eden_connection - Configuration lue: preferred_browser='{preferred_browser}', allow_download={allow_download}")
            
            # Créer le driver avec fallback multi-navigateurs (mode headless)
            driver, browser_name = self._initialize_browser_driver(
                headless=True,
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if not driver:
                return {
                    'success': False,
                    'status_code': None,
                    'message': 'Impossible d\'initialiser un navigateur pour le test',
                    'accessible': False
                }
            
            # Stocker le navigateur utilisé pour affichage
            self.last_browser_used = browser_name
            eden_logger.debug(f"✅ Test avec {browser_name} (headless)")
            
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
                eden_logger.info(f"Test de connexion à {test_url}")
                
                driver.get(test_url)
                
                # Attendre que la page se charge
                time.sleep(2)
                
                current_url = driver.current_url
                
                eden_logger.info(f"URL finale: {current_url}")
                
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
                
                eden_logger.info(f"Analyse de la page - mode=login: {has_login_form}, formulaire connexion: {has_connexion_text}, contenu herald: {has_herald_content}")
                
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
            eden_logger.error(f"Erreur lors du test de connexion: {e}")
            return {
                'success': False,
                'status_code': None,
                'message': f'Erreur: {str(e)[:50]}',
                'accessible': False
            }

