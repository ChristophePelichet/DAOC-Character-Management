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

# Variable GLOBALE pour garder les drivers Selenium vivants
# Cette liste empêche le garbage collection des navigateurs
_PERSISTENT_DRIVERS = []

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
        
        # Garder une référence aux drivers persistants pour éviter le garbage collection
        self.persistent_drivers = []
        
        eden_logger.info(f"CookieManager initialisé - Fichier: {self.cookie_file}", extra={"action": "COOKIES"})
    
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
            eden_logger.error(f"Erreur lors de la lecture des cookies: {e}", extra={"action": "COOKIES"})
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
        
        eden_logger.info(f"Tentative d", extra={"action": "FILE"})
        eden_logger.info(f"Chemin absolu: {source_path.absolute()}", extra={"action": "FILE"})
        eden_logger.info(f"Le fichier existe: {source_path.exists()}", extra={"action": "FILE"})
        
        if not source_path.exists():
            eden_logger.error(f"Fichier source introuvable: {source_file}", extra={"action": "FILE"})
            eden_logger.error(f"Chemin absolu testé: {source_path.absolute()}", extra={"action": "FILE"})
            return False
        
        try:
            # Vérifier que c'est un fichier pickle valide
            eden_logger.info(f"Lecture du fichier pickle...", extra={"action": "FILE"})
            with open(source_path, 'rb') as f:
                cookies = pickle.load(f)
            
            eden_logger.info(f"Fichier chargé, type: {type(cookies)}", extra={"action": "FILE"})
            
            if not isinstance(cookies, list):
                eden_logger.error("Format de fichier invalide: doit contenir une liste de cookies", extra={"action": "FILE"})
                return False
            
            eden_logger.info(f"Nombre de cookies dans le fichier: {len(cookies)}", extra={"action": "COOKIES"})
            # Sauvegarder l'ancien fichier si existant
            if self.cookie_file.exists():
                backup_file = self.cookie_file.with_suffix('.pkl.backup')
                shutil.copy2(self.cookie_file, backup_file)
                eden_logger.info(f"Ancien fichier sauvegardé: {backup_file}", extra={"action": "FILE"})
            
            # Copier le nouveau fichier
            shutil.copy2(source_path, self.cookie_file)
            eden_logger.info(f"Cookies importés: {len(cookies)} cookies", extra={"action": "COOKIES"})
            
            return True
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de l", extra={"action": "LOAD"})
            return False
    
    def delete_cookies(self):
        """
        Supprime le fichier de cookies
        
        Returns:
            bool: True si la suppression a réussi
        """
        if not self.cookie_file.exists():
            eden_logger.warning("Aucun fichier de cookies à supprimer", extra={"action": "COOKIES"})
            return True
        
        try:
            # Créer une sauvegarde avant suppression
            backup_file = self.cookie_file.with_suffix('.pkl.deleted')
            shutil.copy2(self.cookie_file, backup_file)
            
            # Supprimer le fichier
            self.cookie_file.unlink()
            eden_logger.info("Fichier de cookies supprimé", extra={"action": "COOKIES"})
            
            return True
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de la suppression: {e}", extra={"action": "FILE"})
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
        eden_logger.info(f"🔍 _initialize_browser_driver appelé avec: preferred_browser={preferred_browser},...", extra={"action": "INIT"})
        
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
            eden_logger.info("🌐 Ouverture du navigateur pour authentification Eden", extra={"action": "SCRAPE"})
            
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
                eden_logger.error(error_msg, extra={"action": "ERROR"})
                return (False, error_msg, None)
            
            eden_logger.info("✅ Navigateur initialisé: {browser_name}", extra={"action": "SCRAPE"})
            
            # Stocker le navigateur utilisé pour affichage
            self.last_browser_used = browser_name
            
            try:
                # URL de connexion Discord OAuth pour Eden
                discord_login_url = "https://eden-daoc.net/ucp.php?mode=login&redirect=forum.php%2Fforum&login=external&oauth_service=studio_discord"
                driver.get(discord_login_url)
                
                eden_logger.info("Navigateur ouvert - En attente de l", extra={"action": "SCRAPE"})
                
                # Retourner le driver pour que l'interface puisse attendre
                return (True, "browser_opened", driver)
                
            except Exception as e:
                driver.quit()
                error_msg = f"Erreur lors de l'ouverture du navigateur: {e}"
                eden_logger.error(error_msg, extra={"action": "ERROR"})
                return (False, error_msg, None)
                
        except ImportError as e:
            error_msg = "Selenium n'est pas installé. Installez-le avec: pip install selenium webdriver-manager"
            eden_logger.error(error_msg, extra={"action": "ERROR"})
            return (False, error_msg, None)
        except Exception as e:
            error_msg = f"Erreur lors de l'initialisation: {e}"
            eden_logger.error(error_msg, extra={"action": "ERROR"})
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
                eden_logger.info(f"Ancien fichier sauvegardé: {backup_file}", extra={"action": "BACKUP"})
            
            # Sauvegarder les nouveaux cookies
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            eden_logger.info(f"{len(cookies)} cookies sauvegardés dans {self.cookie_file}", extra={"action": "COOKIES"})
            
            return (True, f"{len(cookies)} cookies sauvegardés avec succès", len(cookies))
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde des cookies: {e}"
            eden_logger.error(error_msg, extra={"action": "ERROR"})
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
            eden_logger.error(f"Erreur lors de la lecture des cookies: {e}", extra={"action": "COOKIES"})
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
            
            eden_logger.info("🔧 test_eden_connection - Configuration lue: preferred_browser=", extra={"action": "TEST"})
            
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
            eden_logger.debug("✅ Test avec {browser_name} (headless)", extra={"action": "TEST"})
            
            try:
                # TEST ALIGNÉ EXACTEMENT AVEC load_cookies()
                import time
                
                # Étape 1: Page d'accueil
                driver.get("https://eden-daoc.net/")
                time.sleep(2)
                
                # Étape 2: Ajouter les cookies
                eden_logger.info(f"Ajout de {len(cookies_list)} cookies", extra={"action": "TEST"})
                for cookie in cookies_list:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                
                time.sleep(1)
                
                # Étape 3: Refresh
                eden_logger.info("Refresh pour activer les cookies", extra={"action": "TEST"})
                driver.refresh()
                time.sleep(3)
                
                # Étape 4: Aller sur le Herald
                eden_logger.info("Navigation vers https://eden-daoc.net/herald", extra={"action": "TEST"})
                driver.get("https://eden-daoc.net/herald")
                time.sleep(5)  # Attendre plus longtemps pour que le contenu se charge
                
                # Récupérer et analyser le HTML
                page_source = driver.page_source
                
                # DEBUG: Sauvegarder pour inspection
                import os
                debug_file = os.path.join(os.path.dirname(__file__), '..', 'Scripts', 'debug_test_connection.html')
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(page_source)
                except:
                    pass
                
                # MÉTHODE DE DÉTECTION SIMPLE ET FIABLE:
                # Si on n'a pas le message d'erreur "not available" → On est connecté
                error_message = 'The requested page "herald" is not available.'
                has_error = error_message in page_source
                
                eden_logger.debug(f"HTML size: {len(page_source)}, error present: {has_error}", extra={"action": "TEST"})
                
                # LOGIQUE SIMPLE: Pas d'erreur = Connecté
                if not has_error:
                    eden_logger.info("CONNECTÉ - Pas de message d'erreur détecté", extra={"action": "TEST"})
                    return {
                        'success': True,
                        'status_code': 200,
                        'message': 'Connecté à Herald',
                        'accessible': True
                    }
                else:
                    eden_logger.warning('NON CONNECTÉ - Message d\'erreur détecté', extra={"action": "TEST"})
                    return {
                        'success': True,
                        'status_code': 200,
                        'message': 'Non connecté à Herald',
                        'accessible': False
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

    def open_url_with_cookies(self, url):
        """
        Ouvre une URL dans le navigateur avec les cookies chargés.
        Utilise Selenium pour charger les cookies puis ouvre le navigateur.
        
        Args:
            url (str): L'URL à ouvrir (ex: https://eden-daoc.net/herald)
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'browser': str
            }
        """
        if not self.cookie_exists():
            return {
                'success': False,
                'message': 'Aucun cookie trouvé',
                'browser': None
            }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            import time
            
            # Charger les cookies
            cookies_list = self.get_cookies_for_scraper()
            if not cookies_list:
                return {
                    'success': False,
                    'message': 'Cookies invalides ou expirés',
                    'browser': None
                }
            
            # Lire la configuration pour le navigateur préféré
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            allow_download = config.get('allow_browser_download', False)
            
            # Créer le driver en mode NON-HEADLESS (pour voir le résultat)
            driver, browser_name = self._initialize_browser_driver(
                headless=False,  # Important: pas de headless pour voir le résultat
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if not driver:
                return {
                    'success': False,
                    'message': 'Impossible d\'initialiser un navigateur',
                    'browser': None
                }
            
            try:
                # Étape 1: Aller à la page d'accueil d'abord
                eden_logger.info(f"Ouverture de {url} avec cookies", extra={"action": "NAVIGATE"})
                driver.get("https://eden-daoc.net/")
                time.sleep(2)
                
                # Étape 2: Ajouter les cookies
                eden_logger.info(f"Chargement de {len(cookies_list)} cookies", extra={"action": "NAVIGATE"})
                for cookie in cookies_list:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as cookie_err:
                        eden_logger.debug(f"Impossible d'ajouter un cookie: {cookie_err}")
                
                time.sleep(1)
                
                # Étape 3: Refresh pour activer les cookies
                eden_logger.info("Refresh pour activer les cookies", extra={"action": "NAVIGATE"})
                driver.refresh()
                time.sleep(2)
                
                # Étape 4: Naviguer vers l'URL demandée
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                eden_logger.info(f"Navigation vers {url}", extra={"action": "NAVIGATE"})
                driver.get(url)
                time.sleep(2)
                
                eden_logger.info(f"✅ Page ouverte avec succès via {browser_name}", extra={"action": "NAVIGATE"})
                
                return {
                    'success': True,
                    'message': f'Page ouverte via {browser_name}',
                    'browser': browser_name
                }
                
            except Exception as e:
                eden_logger.error(f"Erreur lors de la navigation: {e}")
                try:
                    driver.quit()
                except:
                    pass
                return {
                    'success': False,
                    'message': f'Erreur: {str(e)[:50]}',
                    'browser': browser_name
                }
                
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else "inconnu"
            return {
                'success': False,
                'message': f'Module {missing_module} non installé',
                'browser': None
            }
        except Exception as e:
            eden_logger.error(f"Erreur lors de l'ouverture de l'URL avec cookies: {e}")
            return {
                'success': False,
                'message': f'Erreur: {str(e)[:50]}',
                'browser': None
            }

    def open_url_with_cookies_persistent(self, url):
        """
        Ouvre une URL dans le navigateur avec les cookies chargés et garde le navigateur ouvert.
        Ne ferme PAS le navigateur à la fin (pour que l'utilisateur puisse continuer à naviguer).
        
        Args:
            url (str): L'URL à ouvrir (ex: https://eden-daoc.net/herald)
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'browser': str
            }
        """
        if not self.cookie_exists():
            return {
                'success': False,
                'message': 'Aucun cookie trouvé',
                'browser': None
            }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            import time
            
            # Charger les cookies
            cookies_list = self.get_cookies_for_scraper()
            if not cookies_list:
                return {
                    'success': False,
                    'message': 'Cookies invalides ou expirés',
                    'browser': None
                }
            
            # Lire la configuration pour le navigateur préféré
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            allow_download = config.get('allow_browser_download', False)
            
            # Créer le driver en mode NON-HEADLESS (pour voir le résultat)
            driver, browser_name = self._initialize_browser_driver(
                headless=False,  # Important: pas de headless pour voir le résultat
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if not driver:
                return {
                    'success': False,
                    'message': 'Impossible d\'initialiser un navigateur',
                    'browser': None
                }
            
            # NOTE: On ne met PAS le driver dans un try/finally avec quit()
            # pour laisser le navigateur ouvert
            try:
                # Étape 1: Aller à la page d'accueil d'abord
                eden_logger.info(f"Ouverture de {url} avec cookies (persistent)", extra={"action": "NAVIGATE"})
                driver.get("https://eden-daoc.net/")
                time.sleep(3)  # Augmenté de 2 à 3
                
                # Étape 2: Ajouter les cookies
                eden_logger.info(f"Chargement de {len(cookies_list)} cookies", extra={"action": "NAVIGATE"})
                for cookie in cookies_list:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as cookie_err:
                        eden_logger.debug(f"Impossible d'ajouter un cookie: {cookie_err}")
                
                time.sleep(2)  # Augmenté de 1 à 2
                
                # Étape 3: Refresh pour activer les cookies
                eden_logger.info("Refresh pour activer les cookies", extra={"action": "NAVIGATE"})
                driver.refresh()
                time.sleep(4)  # Augmenté de 2 à 4
                
                # Étape 4: Naviguer vers l'URL demandée
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                eden_logger.info(f"Navigation vers {url}", extra={"action": "NAVIGATE"})
                driver.get(url)
                time.sleep(5)  # Augmenté de 2 à 5 - laisser le temps au contenu de charger
                
                eden_logger.info(f"✅ Page ouverte avec succès via {browser_name} (navigateur restera ouvert)", extra={"action": "NAVIGATE"})
                
                # IMPORTANT: Garder une référence au driver pour éviter le garbage collection
                self.persistent_drivers.append(driver)
                
                # IMPORTANT: Ne pas fermer le driver pour garder le navigateur ouvert
                return {
                    'success': True,
                    'message': f'Page ouverte via {browser_name} (le navigateur reste ouvert)',
                    'browser': browser_name
                }
                
            except Exception as e:
                eden_logger.error(f"Erreur lors de la navigation (persistent): {e}")
                # IMPORTANT: En mode persistent, on ne ferme PAS le driver même en cas d'erreur
                # pour laisser l'utilisateur voir la page actuelle
                return {
                    'success': False,
                    'message': f'Erreur: {str(e)[:50]}',
                    'browser': browser_name
                }
                
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else "inconnu"
            return {
                'success': False,
                'message': f'Module {missing_module} non installé',
                'browser': None
            }
        except Exception as e:
            eden_logger.error(f"Erreur lors de l'ouverture persistente de l'URL avec cookies: {e}")
            return {
                'success': False,
                'message': f'Erreur: {str(e)[:50]}',
                'browser': None
            }

    def open_url_with_cookies_simple(self, url):
        """
        Ouvre une URL dans le navigateur par défaut avec les cookies injectés.
        Utilise un petit serveur local qui injecte les cookies et redirige.
        
        Args:
            url (str): L'URL à ouvrir
            
        Returns:
            dict: {
                'success': bool,
                'message': str
            }
        """
        if not self.cookie_exists():
            return {
                'success': False,
                'message': 'Aucun cookie trouvé'
            }
        
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json
            import threading
            import webbrowser
            import time
            
            cookies_list = self.get_cookies_for_scraper()
            if not cookies_list:
                return {
                    'success': False,
                    'message': 'Cookies invalides ou expirés'
                }
            
            # Préparer l'URL cible
            target_url = url
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url
            
            class CookieInjectorHandler(BaseHTTPRequestHandler):
                """Handler qui injecte les cookies et redirige"""
                
                def do_GET(self):
                    if self.path == '/':
                        # Générer une page HTML qui injecte les cookies et redirige
                        cookies_js = 'document.cookie = "";\n'
                        for cookie in cookies_list:
                            name = cookie.get('name', '')
                            value = cookie.get('value', '')
                            domain = cookie.get('domain', '')
                            path = cookie.get('path', '/')
                            # Injecter le cookie (simple, pas de domaine spécifique)
                            safe_value = value.replace('"', '\\"')
                            cookies_js += f'document.cookie = "{name}={safe_value}; path={path}; max-age=31536000";\n'
                        
                        html = f"""
                        <html>
                        <head><title>Loading...</title></head>
                        <body>
                        <script>
                        {cookies_js}
                        window.location.href = "{target_url}";
                        </script>
                        </body>
                        </html>
                        """
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(html.encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    pass  # Supprimer les logs du serveur
            
            # Démarrer le serveur dans un thread séparé
            server = HTTPServer(('127.0.0.1', 0), CookieInjectorHandler)
            port = server.server_address[1]
            server_thread = threading.Thread(target=server.handle_request, daemon=True)
            server_thread.start()
            
            # Ouvrir le navigateur vers le serveur local
            local_url = f"http://127.0.0.1:{port}/"
            eden_logger.info(f"Ouverture de {target_url} avec cookies via serveur local", extra={"action": "NAVIGATE"})
            webbrowser.open(local_url)
            
            # Attendre que la page soit servie
            time.sleep(3)
            server.server_close()
            
            return {
                'success': True,
                'message': f'Page ouverte via navigateur par défaut avec cookies'
            }
            
        except Exception as e:
            eden_logger.error(f"Erreur lors de l'ouverture simple avec cookies: {e}")
            return {
                'success': False,
                'message': f'Erreur: {str(e)[:50]}'
            }

    def open_url_with_cookies_detached(self, url):
        """
        Ouvre une URL dans un navigateur Selenium DÉTACHÉ avec les cookies.
        Le navigateur continue de fonctionner même après que la fonction se termine.
        
        Args:
            url (str): L'URL à ouvrir
            
        Returns:
            dict: {
                'success': bool,
                'message': str
            }
        """
        if not self.cookie_exists():
            return {
                'success': False,
                'message': 'Aucun cookie trouvé'
            }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            import time
            import subprocess
            import os
            
            cookies_list = self.get_cookies_for_scraper()
            if not cookies_list:
                return {
                    'success': False,
                    'message': 'Cookies invalides ou expirés'
                }
            
            # Lire la configuration pour le navigateur préféré
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            allow_download = config.get('allow_browser_download', False)
            
            # Créer le driver
            driver, browser_name = self._initialize_browser_driver(
                headless=False,
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if not driver:
                return {
                    'success': False,
                    'message': 'Impossible d\'initialiser un navigateur'
                }
            
            try:
                # Préparer l'URL
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                eden_logger.info(f"Ouverture détachée de {url} avec cookies", extra={"action": "NAVIGATE"})
                
                # Étape 1: Page d'accueil
                driver.get("https://eden-daoc.net/")
                time.sleep(1)
                
                # Étape 2: Ajouter les cookies
                for cookie in cookies_list:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                
                time.sleep(1)
                
                # Étape 3: Refresh
                driver.refresh()
                time.sleep(2)
                
                # Étape 4: Navigation vers l'URL
                driver.get(url)
                time.sleep(2)
                
                eden_logger.info(f"✅ Page ouverte avec succès via {browser_name} (détaché)", extra={"action": "NAVIGATE"})
                
                # IMPORTANT: Ne PAS appeler driver.quit()
                # Laisser le driver/navigateur ouvert en arrière-plan
                # Le processus se terminera quand l'utilisateur ferme le navigateur
                
                return {
                    'success': True,
                    'message': f'Page ouverte via {browser_name}'
                }
                
            except Exception as e:
                eden_logger.error(f"Erreur lors de la navigation détachée: {e}")
                try:
                    driver.quit()
                except:
                    pass
                return {
                    'success': False,
                    'message': f'Erreur: {str(e)[:50]}'
                }
        
        except Exception as e:
            eden_logger.error(f"Erreur lors de l'ouverture détachée: {e}")
            return {
                'success': False,
                'message': f'Erreur: {str(e)[:50]}'
            }

    def open_url_with_cookies_subprocess(self, url):
        """
        Ouvre une URL dans un navigateur COMPLÈTEMENT INDÉPENDANT avec les cookies.
        Lance Chrome/Edge comme processus détaché qui ne se ferme pas avec l'appli.
        
        Args:
            url (str): L'URL à ouvrir
            
        Returns:
            dict: {
                'success': bool,
                'message': str
            }
        """
        if not self.cookie_exists():
            return {
                'success': False,
                'message': 'Aucun cookie trouvé'
            }
        
        try:
            import subprocess
            import json
            import tempfile
            import os
            from pathlib import Path
            
            cookies_list = self.get_cookies_for_scraper()
            if not cookies_list:
                return {
                    'success': False,
                    'message': 'Cookies invalides ou expirés'
                }
            
            # Préparer l'URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Lire la configuration pour le navigateur préféré
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            
            # Trouver le chemin du navigateur
            browser_path = None
            if preferred_browser == 'Chrome':
                possible_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                ]
            elif preferred_browser == 'Edge':
                possible_paths = [
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
                ]
            else:
                possible_paths = []
            
            for path in possible_paths:
                if os.path.exists(path):
                    browser_path = path
                    break
            
            if not browser_path:
                # Fallback: essayer de lancer via webbrowser
                import webbrowser
                webbrowser.open(url)
                return {
                    'success': True,
                    'message': f'Ouvert via navigateur par défaut (pas de cookies)'
                }
            
            # Créer un profil temporaire pour les cookies
            profile_dir = tempfile.mkdtemp(prefix="daoc_")
            cookies_file = os.path.join(profile_dir, "cookies.txt")
            
            # Sauvegarder les cookies dans un fichier pour Selenium de charger plus tard
            import pickle
            with open(cookies_file, 'wb') as f:
                pickle.dump(cookies_list, f)
            
            eden_logger.info(f"Lancement de {preferred_browser} avec Selenium et cookies", extra={"action": "NAVIGATE"})
            
            # NE PAS lancer le navigateur directement
            # Seulement utiliser Selenium pour lancer et charger les cookies
            import time
            
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.edge.options import Options as EdgeOptions
                
                if preferred_browser == 'Chrome':
                    chrome_options = Options()
                    chrome_options.add_argument("--no-first-run")
                    chrome_options.add_argument("--no-default-browser-check")
                    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                    
                    from webdriver_manager.chrome import ChromeDriverManager
                    driver = webdriver.Chrome(options=chrome_options)
                else:
                    edge_options = EdgeOptions()
                    edge_options.add_argument("--no-first-run")
                    edge_options.add_argument("--disable-blink-features=AutomationControlled")
                    
                    from selenium.webdriver.edge.service import Service as EdgeService
                    from webdriver_manager.microsoft import EdgeChromiumDriverManager
                    driver = webdriver.Edge(options=edge_options)
                
                try:
                    # Charger la page et ajouter les cookies
                    driver.get("https://eden-daoc.net/")
                    time.sleep(1)
                    
                    for cookie in cookies_list:
                        try:
                            driver.add_cookie(cookie)
                        except:
                            pass
                    
                    time.sleep(1)
                    driver.refresh()
                    time.sleep(2)
                    
                    driver.get(url)
                    time.sleep(3)
                    
                    eden_logger.info(f"✅ Navigateur lancé via Selenium avec cookies chargés", extra={"action": "NAVIGATE"})
                    
                    # IMPORTANT: Garder une référence GLOBALE au driver pour éviter le garbage collection
                    # Utiliser la variable globale, pas self.persistent_drivers
                    global _PERSISTENT_DRIVERS
                    _PERSISTENT_DRIVERS.append(driver)
                    
                    # IMPORTANT: NE PAS appeler quit()
                    # Laisser le driver/navigateur ouvert indéfiniment
                    return {
                        'success': True,
                        'message': f'Navigateur lancé avec succès et cookies chargés'
                    }
                    
                finally:
                    # Ne pas fermer le driver
                    pass
                
            except Exception as e:
                eden_logger.error(f"Erreur Selenium avec cookies: {e}")
            
        except Exception as e:
            eden_logger.error(f"Erreur lors du lancement subprocess: {e}")
            return {
                'success': False,
                'message': f'Erreur: {str(e)[:50]}'
            }

